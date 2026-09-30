Implemented `GET /healthz`（200 + JSON `{"status":"ok"}`），按仓库既有 handler 约定实现并通过仓库验证入口。

**(a) 变更摘要（文件级）**
- `internal/httpapi/router.go`：在 `NewRouter` 注册 `mux.HandleFunc("GET /healthz", handleHealthz)`；新增 `handleHealthz`，复用既有 `writeJSON` 写出 200 与 `map[string]string{"status":"ok"}`。
- `internal/httpapi/router_test.go`：新增 `TestHealthz`（httptest，断言 200 + 解码 JSON 校验 `status=="ok"`），并沿用原 `TestVersion` 风格；import 增加 `encoding/json`。
- `RUNLOG.md`（新增）：每条命令一行，含命令与原因。
- 未改动 `go.mod`、`Makefile`、`cmd/server/main.go`、`internal/apierr`；无新目录/新依赖。

**(b) 关键决策**
- **命令运行目录与范围**：所有命令均 `cd /tmp/trellium-0026-replay/s1b` 后执行，仅在该目录内读写；先用 `go env GOMOD GOWORK && go list ./...` 确认这是单 module（`example.com/shopapi`，go 1.22）、无 `go.work`，故验证从该 module 根执行一次即可覆盖全部 3 个 package。
- **依赖/框架选择**：零新增依赖，沿用标准库 `net/http` 的 `http.ServeMux`（Go 1.22 method-pattern 路由，与既有 `GET /version` 同款），JSON 经既有 `writeJSON`，符合 README「不引入第三方依赖」「响应统一经 writeJSON」。
- **创建的目录或层**：无新目录、无新 package；handler 与注册都放在既有 `internal/httpapi`（Transport 层），无业务逻辑，不涉及 `apierr`（成功路径）。
- **依据的 Profile 约束**：标准库优先、不新增第三方依赖；遵循仓库已有构建契约（`Makefile` 的 `verify` 为验证入口）与 README 约定；测试用标准库 `testing` + `net/http/httptest`；修改的 Go 文件经 gofmt 检查；`go.mod`/`go.work` 无变化；未执行任何 git add/commit。

**(c) 验证结果**
- `make verify`（仓库验证入口 = `scripts/check-fmt.sh` + `go vet ./...` + `go test ./...`）：**通过**（gofmt 无输出、vet 无告警、`internal/httpapi` ok）。
- `go test -run 'TestHealthz|TestVersion' -v ./internal/httpapi`：`TestVersion PASS`、`TestHealthz PASS`。
- `git status --short`：仅 `M internal/httpapi/router.go`、`M internal/httpapi/router_test.go`、`?? RUNLOG.md`。

**Open risks/questions**：8080 端口被一个先前遗留的 `server` 进程（pid 1142141，非本次构建）占用，我新构建的二进制 `bind: address already in use`，因此 `curl` 命中的是该遗留进程而非本次构建（其响应同为 200 `{"status":"ok"}`，但不能归因于本次代码）；该进程在目录之外，我未将其终止。真实 HTTP 行为改由 httptest 路由测试确定性覆盖，全部通过。临时二进制已删除，工作区为最终状态。

**Recommended next step**：如需真实进程级端到端复验，先由你决定是否停掉 8080 上的遗留 `server` 进程，再 `go build -o .server-check ./cmd/server && ./.server-check` 并 `curl /healthz`。