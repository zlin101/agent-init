# shop-api

内部运维小 API。

## 仓库约定

- handler 都放在 `internal/httpapi`，响应统一经 `writeJSON` 写出。
- 业务错误统一用 `internal/apierr` 的 `*apierr.Error`（含 Code/Message）。
- 仓库不引入第三方依赖；没有对应 issue 时不要新增依赖或框架。
- 所有变更通过 `make verify` 验证（gofmt 检查、`go vet`、`go test ./...`）。
