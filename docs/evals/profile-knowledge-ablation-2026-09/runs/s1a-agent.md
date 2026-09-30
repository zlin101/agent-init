已完成 `GET /healthz` 端点并全量通过仓库验证。

**(a) 变更摘要（文件级）**
- `internal/httpapi/router.go`：在 `NewRouter()` 注册 `mux.HandleFunc("GET /healthz", handleHealthz)`；新增 `handleHealthz`，经既有 `writeJSON` 返回 200 与 `{"status":"ok"}`（Content-Type `application/json; charset=utf-8`）。
- `internal/httpapi/router_test.go`：新增 `TestHealthz`（httptest 断言 200 + JSON `status=="ok"`），并加 `encoding/json` import。
- `RUNLOG.md`：任务要求的命令运行记录（每条命令一行 + 原因）。
- 未改动 `go.mod`/`go.sum`、`Makefile`、`cmd/`，无新建目录。

**(b) 关键决策**
- 运行目录与范围：所有命令均在 `/tmp/trellium-0026-replay/s1a` 下执行。先按 Profile 确认 `go env GOMOD GOWORK GOFLAGS` → 单 module（`example.com/shopapi`）、无 `go.work`、`go 1.22`（本机 go1.22.12），因此以仓库根为命令根运行 `go vet ./...`、`go test ./...`。
- 依赖/框架选择：零新增依赖，沿用标准库 `net/http` 的 `ServeMux` 方法模式路由（与既有 `"GET /version"` 一致）。依据 README 约定「不引入第三方依赖」+ Profile「标准库能解决不新增依赖、仅需求明确才引入框架」。
- 目录/层：无新目录、无新分层；handler 落在既有 `internal/httpapi`（README 约定「handler 都放在 internal/httpapi，响应统一经 writeJSON」），handler 只做协议转换，符合 Profile 的 transport 职责边界。
- 依据的 Profile 约束：优先仓库构建/CI 契约（`make verify` 为实际验证入口）→ 先识别 module 结构再定运行目录 → 提交前 gofmt → HTTP 测试用 `net/http/httptest` → 测试与被测代码同目录同 package → 只创建当前任务真正需要的目录。冲突时（handler 放哪、是否引框架）按 Profile 的优先级服从任务契约与仓库既有约定。

**(c) 验证结果**
- `gofmt -l .` → 无输出（已格式化）。
- `make verify`（仓库规定入口 = fmt-check + `go vet ./...` + `go test ./...`）→ 通过：vet 无报错，`ok example.com/shopapi/internal/httpapi 0.002s`，其余包 no test files。
- 冒烟：`go build ./...` 成功；本地 `go run ./cmd/server` 后 `curl -i /healthz` → `HTTP/1.1 200` + `{"status":"ok"}`；`/version` 仍 200；随后停止进程。
- `git status --short` → 仅 `M internal/httpapi/router.go`、`M internal/httpapi/router_test.go`、`?? RUNLOG.md`，无编译产物残留；未执行任何 git add/commit，未访问包注册表或外部业务系统。

**开放风险/问题**：仅 advisory 的 Markdown 标题告警已通过给 `RUNLOG.md` 加 H1 解决；无其他风险。
**建议下一步**：由主会话按仓库惯例审查 diff 并决定是否纳入提交。