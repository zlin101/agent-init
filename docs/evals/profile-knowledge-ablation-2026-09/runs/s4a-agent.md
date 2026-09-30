Implemented the Poller lifecycle fix.

**(a) 变更摘要（文件级）**
- `poller/poller.go`：重写生命周期。
  - `New(interval, fn, onError)` 新增错误处理参数；`fn` 返回的错误不再被 `_ =` 丢弃——交给 `onError`，为 `nil` 时回落到标准库 `log/slog` 默认 logger。
  - `Start() error`：可启动、可重复调用（停止后再启动），运行中再次调用返回导出的 sentinel `ErrAlreadyStarted`（`errors.Is` 可判）。
  - `Stop(ctx context.Context) error`：关闭内部 stop channel 并**等待轮询 goroutine 退出**后才返回 nil（nil 即保证不再调用 `fn`）；未启动/已停止时为幂等 no-op；goroutine 被阻塞的 `fn` 卡住时按 ctx 截止返回 `fmt.Errorf("stop poller: %w", ctx.Err())`，且之后可再次 `Stop` 等待。
  - struct 内用 `mu + running + done + stopOnce` 保护运行状态；goroutine 只使用 Start 捕获的局部 `stop/done`，ticker 由 goroutine 自身 `defer ticker.Stop()`，退出路径 `defer close(done)`，无泄漏、无重复 close panic。
- `poller/poller_test.go`：更新并补测。
  - `TestPollerRuns` 改用 `atomic.Int64`（原 `polls++` 在 `-race` 下是数据竞争）+ `t.Cleanup` 停止 poller（原测试从不停止即泄漏 goroutine）。
  - 新增 `TestPollerStopEndsPollingAndGoroutine`（关闭行为：goroutine 已退出、停止后不再轮询、`runtime.NumGoroutine()` 回到基线）、`TestPollerRestartAfterStop`、`TestPollerStartTwice`、`TestPollerReportsErrors`、`TestPollerStopTimesOutWhilePollBlocks`（取消/超时/阻塞路径）。
- `RUNLOG.md`：新建，逐条记录命令与原因。
- 未改动 `go.mod`（零第三方依赖）、无 `go.sum`，未执行任何 git add/commit。

**(b) 关键决策**
- 命令运行目录与范围：bash 默认目录是 `/tmp/trellium-0026-replay`，因此**每条命令都以 `cd /tmp/trellium-0026-replay/s4a && …` 前缀限定在任务目录内**；先用 `go env GOMOD GOWORK GOFLAGS` 确认为单 module、无 `go.work`，故所有 go 命令在 module 根 `s4a/` 运行、覆盖 `./...`。前两次未带 cd 的 `cat` 失败也已如实记入 RUNLOG。
- 依赖/框架选择：标准库即可（`sync`、`sync.OnceFunc`、`context`、`log/slog`、`errors`、`time`、`testing`、`sync/atomic`、`runtime`），未新增任何第三方依赖，未引入框架。
- 创建的目录或层：无新目录，代码仍只在既有 `poller/` package 内；测试与被测代码同目录、同 package（需访问内部 `done` 验证退出）。
- 依据的 Profile 约束：错误必须处理/可见（不静默丢弃、`%w` 保留链、sentinel 仅在调用方需分支时定义）；“每个 goroutine 必须有所有者、停止条件与错误路径”“后台 worker 必须有停止路径”；“进程退出时有截止时间的优雅关闭并等待受管 goroutine 结束”（`Stop(ctx)`）；并发变更跑 `-race`、不用 sleep 掩盖时序（等待用条件轮询 `waitFor`，仅“停止后不再轮询”的否定断言用有界 sleep）；`gofmt`/`go vet`/`log/slog`/标准库 `testing`；命令默认在受影响 module 根执行。

**(c) 验证结果**（均在 `/tmp/trellium-0026-replay/s4a`）
- `gofmt -l poller/` → 无输出（已格式化）。
- `go vet ./...` → 通过，无告警。
- `go build ./...` → 通过。
- `go test ./...` → `ok example.com/worker/poller 0.052s`。
- `go test -race -count=3 ./...` → `ok example.com/worker/poller 1.168s`（3 次重复，含 race detector）。
- `go test -v ./poller/` → 6 个用例全部 PASS：Runs / StopEndsPollingAndGoroutine / RestartAfterStop / StartTwice / ReportsErrors / StopTimesOutWhilePollBlocks。
- `git status --porcelain` → 仅 `M poller/poller.go`、`M poller/poller_test.go`、`?? RUNLOG.md`；未 add、未 commit。

**Open risks/questions**：`fn` 仍保持 `func() error`（未改为 `func(ctx) error`），因此阻塞的 `fn` 只能靠 `Stop` 的 ctx 截止兜底，无法中断 `fn` 本身——这是为最小改动保留的既有签名；若 server 侧需要可取消的轮询任务，可作为后续契约变更单独决定。

**Recommended next step**：把该 `Poller` 接入 server 生命周期（构造后 `Start()`，在 server 优雅关闭流程里以带超时的 ctx 调用 `Stop`），并由父会话确认是否需要把 `fn` 升级为接收 `ctx`。