Implemented the Poller lifecycle fix. 全部工作在 `/tmp/trellium-0026-replay/s4b` 内完成，无 git 操作、无外部系统调用、无新增依赖。

**(a) 变更摘要（文件级）**
- `poller/poller.go`（重写核心逻辑）
  - `Start()` 改为返回 `error`：重复启动、非正 `interval`、`fn == nil` 均返回可检查的错误而非 panic/静默；成功时启动唯一后台 goroutine。
  - 新增 `Stop()`：关闭内部 `stopCh` 并阻塞等待 `doneCh`（goroutine 真正退出、含在途 poll 完成），未启动时为幂等 no-op，server 可无条件 `defer p.Stop()`；`Start` 在 `Stop` 后可再次启动。
  - goroutine 结构改为 `select { <-stopCh / <-ticker.C }` + `defer ticker.Stop()` + `defer close(doneCh)`，停止路径明确，不再保留共享 `ticker` 字段。
  - 错误不再被 `_ =` 丢弃：`fn` 的非 nil 错误经 `%w` 包装一次（`poll: ...`）后交给构造时注入的 `onError`；`onError` 为 nil 时回退到 `log/slog` 结构化日志，保证任何路径都不静默。
  - `New(interval, fn, onError)` 增加第三个参数（错误上报回调）。
- `poller/poller_test.go`（重写测试）
  - `TestPollerRuns`：改用 `atomic.Int64` 计数（消除原测试的数据竞争）、处理 `Start` 错误、`t.Cleanup(p.Stop)`、条件轮询替代固定 sleep。
  - `TestPollerStop`（覆盖关闭行为，任务要求的那个）：Stop 返回后计数冻结、跨 10 个 interval 不再推进、重复 Stop 幂等、运行中二次 Start 报错。
  - `TestPollerStopWaitsForInFlightPoll`：Stop 在 `fn` 在途时不返回，返回即证明 goroutine 已退出（不泄漏）。
  - `TestPollerReportsPollError`：`errors.Is` 验证错误链完整到达 handler。
  - `TestPollerStartRejectsInvalidConfig`：表驱动覆盖启动前置校验。
- `RUNLOG.md`（新建）：每条 shell 命令一行“命令 + 原因 + exit 状态”，共 7 行。

**(b) 关键决策**
- 命令运行目录与范围：先按 Profile 执行 `go env GOMOD GOWORK`，确认 `GOMOD=/tmp/trellium-0026-replay/s4b/go.mod`、`GOWORK` 为空，即单 module、无 workspace；`go list ./...` 确认唯一 package `example.com/worker/poller`，故所有 `gofmt/vet/test/build` 均在 module 根 `s4b/` 下运行一次即可覆盖全部范围。
- 依赖/框架选择：仅标准库（`sync`、`time`、`errors`、`fmt`、`log/slog`、`testing`、`sync/atomic`），未新增第三方依赖，`go.mod`/`go.sum` 无变化（也无需 `go mod tidy`）；沿用标准库 `testing`，未引入 goroutine-leak 类工具包。
- 创建的目录或层：未创建任何新目录/分层；仅在既有 `poller/` package 内修改，并新建日志文件 `RUNLOG.md`。
- 依据的 Profile 约束：① “go.mod/CI 是构建契约、先确认 module 根与 package 范围”（驱动运行目录决策）；② “错误必须被处理/返回，%w 保留错误链、errors.Is 判断”（`onError` 回调 + `%w` 包装 + 测试断言）；③ “每个 goroutine 必须有停止条件和错误路径、不泄漏 goroutine / ticker 必须有停止路径”（`Stop` + `doneCh` 等待 + `ticker.Stop`）；④ “并发变更必须运行 `go test -race`”；⑤ “不使用 panic 处理可预期错误、结构化日志优先 slog”（启动校验返回 error、无 handler 时 slog 兜底）；⑥ “不预建空分层、标准库够用不加依赖”。

**(c) 验证结果**（均在 `s4b/` 根执行，全部 exit 0，已记入 `RUNLOG.md`）
- `go version && go env GOMOD GOWORK` → go1.22.12，`GOMOD=…/s4b/go.mod`，`GOWORK` 空
- `go list ./...` → `example.com/worker/poller`
- `gofmt -l .` → 无输出（格式合规）
- `go vet ./...` → 无输出（通过）
- `go test ./...` → `ok example.com/worker/poller 0.097s`
- `go test -race ./...` → `ok example.com/worker/poller 1.102s`
- `go build ./...` → 无输出（编译通过）

Open risks/questions: 无阻塞项；一处 advisory lint 提示 `RUNLOG.md` 首行非标题（MD041），按规则仅提示、无需处理。若未来 `fn` 可能长时间挂起，`Stop` 会等待其返回（当前 API 有意保持简单，由 server 侧的关闭超时兜底）。README 未描述 API，无需文档同步。

Recommended next step: 由主 agent 复核 `poller/poller.go` 的 `Start/Stop` 契约与测试覆盖，按既有评审流程决定是否合入。