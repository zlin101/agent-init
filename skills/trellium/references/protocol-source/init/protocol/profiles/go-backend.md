# Profile - Go Backend

## 定位

本 profile 适用于 Go 后端、API 服务、命令行服务、Agent 后端、数据服务或类似项目。

核心协议保持语言无关；本文件只提供 Go 项目的默认值，不强制框架或固定目录模板。

工程选择发生冲突时，依次遵循任务契约和项目 Agent 规则、仓库已有构建与 CI 契约、稳定的本地代码模式，最后才使用本 profile 的默认值。

## 默认技术栈

| 类别 | 默认值 |
|---|---|
| 语言 | Go，最低版本以 `go.mod` 的 `go` 指令为准；存在 `toolchain` 指令时同时遵循 |
| 依赖管理 | Go Modules |
| HTTP 服务 | 优先标准库 `net/http`；仅在需求明确时引入框架或路由库 |
| 数据模型 | 普通 struct，按边界定义 JSON、数据库或领域类型 |
| 配置管理 | 优先标准库和环境变量；复杂配置再选择依赖 |
| 日志 | Go 版本支持时优先标准库 `log/slog`，否则沿用项目已有日志方案 |
| 测试 | 标准库 `testing` |
| HTTP 测试 | `net/http/httptest` |
| 格式化 | `gofmt` |
| 静态检查 | `go vet`；项目已有时使用 `staticcheck` 或 `golangci-lint` |

标准库能够清晰解决问题时，不新增第三方依赖。不要为了统一风格替换既有项目已经稳定使用的路由、日志、配置或测试方案。

## 进入项目时先确认

修改前先读取项目的 `AGENTS.md`、README、CI、Makefile 或 Taskfile，再确认 Go 工作区和工具链（module 根、workspace、构建契约；事实来源为仓库 `go.mod`、`go.work`、CI 配置与当前工具链的实际查询，如 `go env GOMOD GOWORK`）。

执行原则：

- `go.mod`、`go.work`、CI 和仓库验证脚本是实际构建契约，本 profile 不能覆盖它们。
- 先识别仓库是单 module、多 module 还是 `go.work` 工作区，再决定命令运行目录。
- 确认 module 根目录后运行 `go list ./...`，了解实际 package 范围；不要在尚未确认的 workspace 根目录机械执行。
- 检查 build tags、`GOOS`、`GOARCH`、CGO、代码生成和私有 module 配置，不假设本机默认环境覆盖全部目标。
- 既有项目优先沿用当前 package 边界和命名；只有任务需要时才调整结构。

## 模块和依赖管理

使用 Go Modules，并将 `go.mod` 纳入版本控制。依赖解析生成 `go.sum` 时也应提交；没有外部依赖的 module 可以不存在 `go.sum`。

约束：

- 新项目只初始化一个主 module，除非多 module 边界有明确发布或所有权需求。
- module path 应使用预期的代码仓库或发布路径；尚未确定时不要编造他人控制的域名。
- 不手工编辑 `go.sum`。
- 添加、升级或移除依赖后运行 `go mod tidy`，并检查 `go.mod` 和 `go.sum` 的变更。
- 不使用无版本依据的依赖升级；升级前检查兼容性和变更范围。
- `replace` 适合本地开发或明确的临时修复，不应无说明地长期指向本机路径或 fork。
- 不随意修改 `go` 或 `toolchain` 指令；它们属于构建和运行时契约。
- 已有 `go.work` 时遵循其 `use` 和 `replace` 边界。只有任务确实跨 module 时才修改工作区，并检查 `go.work`、`go.work.sum` 和各 module 的变化。

## 推荐结构

遵循仓库既有结构；新结构按需创建，不预先搭建空的分层骨架（`cmd/`、`internal/`、`api/`、`migrations/`、`testdata/` 等只在任务需要时建立）。

目录和 package 边界：

- 可执行程序入口放在 `cmd/<name>/main.go`，入口只负责组装依赖、启动和优雅退出。
- 不希望被 module 外部导入的代码放在 `internal/`。
- 不默认创建 `pkg/`；它在 Go 工具链中没有特殊语义。确实要向外部 module 提供稳定 API 时，可以使用根 package 或语义明确的公开子 package。
- package 按职责或领域命名，使用简短小写名称，不使用 `util`、`common`、`misc` 等含义模糊的兜底包。
- 避免 import cycle；出现循环通常意味着职责或依赖方向需要调整。

## 分层和依赖方向

以下是逻辑职责和依赖方向，不要求每一层都对应一个 package。依赖方向：Transport（HTTP handler）→ Application / Use Case → Domain Logic；Adapter 实现 Application 拥有的最小接口并对接外部系统。

约束：

- HTTP handler 负责协议转换、输入校验、调用用例和响应映射，不承载复杂业务逻辑。
- Application 或 Use Case 负责流程编排和事务边界。
- 若存在 Repository，它负责持久化访问；Client 或 Adapter 负责外部系统。
- 接口通常由使用方定义并保持最小，Adapter 实现这些接口；不要为每个 struct 机械创建接口。
- 构造函数返回具体类型通常更清晰；只有调用方需要替换实现时才依赖接口。
- 通过显式构造函数完成依赖注入，避免可变全局单例和隐式初始化顺序。

## Go 风格

- 提交前对修改过的 Go 文件运行 `gofmt`；项目已使用 `goimports` 时沿用它。
- 注释、Doc Comment、docstring、TODO/FIXME、directive 与 API 文档表达规范由项目 Comment Policy（`docs/engineering/code-comments.md`）唯一拥有；纯注释/文档工作直接读它，公开 API 或行为与注释同时修改时与本 profile 并读。
- 优先让零值可用。使用指针应有可变性、共享身份、较大复制成本或区分“未设置”的明确理由。
- 明确区分 nil slice、空 slice、nil map 和空 map 在序列化及 API 契约中的行为。
- 不在 `init()` 中执行网络访问、启动 goroutine 或隐藏重要业务初始化。
- 谨慎使用泛型；只有在减少真实重复且不损害可读性时引入类型参数。
- 不使用 `panic` 处理可预期的业务错误。`panic` 只用于不可恢复的程序不变量，或在入口边界被明确恢复和记录。
- 运行日志使用结构化 logger，不使用 `fmt.Println` 代替服务日志。
- 时间、随机数、文件系统和外部调用在需要确定性测试时通过清晰边界注入。

## 错误处理

- 错误必须被处理、返回或有意忽略；有意忽略时应让原因可见。
- 使用 `%w` 包装错误并保留错误链，例如 `fmt.Errorf("load user: %w", err)`。
- 使用 `errors.Is` 和 `errors.As` 判断错误，不依赖错误字符串匹配。
- 在能够补充操作语义的边界包装一次，避免每一层重复堆叠相同上下文。
- 对外部 API 返回稳定的错误码或错误类型，不直接暴露内部错误、SQL、路径或敏感信息。
- 仅为调用方确实需要分支处理的情况定义 sentinel error 或自定义错误类型。

## 资源生命周期

- 谁成功获取资源，谁负责在所有返回路径释放它；获取后尽早安排 `defer`，但循环中的短生命周期资源应及时关闭而不是累积到函数结束。
- 关闭写入器、事务或其他可能在收尾阶段失败的资源时，不能无条件丢弃 `Close`、`Commit` 或 flush 错误。
- HTTP client 在请求未返回 error 且获得 response 后必须关闭 `resp.Body`；需要复用连接时按协议完整读取或妥善处理响应体。
- 数据库查询结果必须关闭，并在迭代结束后检查迭代错误；事务路径必须明确 commit、rollback 和 context 取消行为。
- timer、ticker、subscription 和后台 worker 在不再需要时必须有停止路径，测试也要清理其资源。

## Context 和并发

- `context.Context` 通常作为需要它的函数或方法的第一个显式参数，命名为 `ctx`；不要把 context 存入 struct。必须匹配既有接口时沿用接口签名。
- 从请求或任务入口向下传播 context，不用 `context.Background()` 绕过已有的取消和截止时间。
- 不把可选业务参数塞进 context；context value 只承载跨边界的请求级元数据。
- 每个 goroutine 都必须有清晰的所有者、停止条件和错误处理路径。
- 启动并发任务时设计取消、超时、结果收集和资源释放；避免 goroutine 或 channel 泄漏。
- channel 只在需要通知接收方“不再有值”时关闭，不要求为了释放资源而关闭。负责完整发送生命周期的一方拥有关闭权；接收方不要关闭它不拥有的 channel，也不要让 send 与 close 无同步地并发发生。
- 共享状态优先通过所有权隔离避免竞争；确需共享时使用合适的同步原语，并说明锁保护的不变量。
- 并发相关变更应在工具链和目标平台支持时运行 `go test -race ./...`。race detector 只能发现实际执行路径上的竞态，不能替代并发设计审查；不要用增加 sleep 掩盖时序问题。

## HTTP 和服务生命周期

- 为 HTTP server 配置适合协议的 header、读取、写入、空闲和请求级超时；流式响应需要单独设计，不能机械套用普通请求超时。
- 对请求体设置大小限制，并在边界完成解码和校验。
- 明确 JSON 字段名、可选性和未知字段策略；公开 API 变更应视为契约变更。
- 传播请求 context 到数据库和外部客户端，并为外部调用设置超时。复用 `http.Client` 或 Transport，不为每个请求新建连接池。
- 在进程退出时停止接收新流量，执行有截止时间的优雅关闭，并等待受管 goroutine 结束。
- 响应和日志不得泄露密钥、Token、连接串或内部堆栈。

## 测试

- 使用标准库 `testing` 组织测试，多输入组合优先表驱动；项目已有测试框架则沿用。
- 需要验证内部实现时使用同 package 测试；需要验证公开契约时使用 `_test` 外部 package。不要机械统一。
- 使用 `t.Helper()` 标记测试辅助函数，使用 `t.Cleanup()` 管理资源。
- 可以安全并行且无共享状态的测试才调用 `t.Parallel()`。
- HTTP handler 使用 `httptest`；外部服务使用 fake、stub 或本地测试 server。
- 单元测试不真实调用 LLM API、互联网服务或开发者本机基础设施。
- 涉及并发、锁、channel 或共享缓存的变更必须覆盖取消、超时、关闭和错误路径，并在支持时运行 race detector。
- fuzz test 适合解析器、编解码器和输入边界，但不能替代确定性的单元测试。

测试、构建与格式化验证默认从受影响 module 的根目录执行。多 module 或 `go.work` 项目应使用仓库已有验证入口，或逐个验证受影响 module；不要假设从仓库根目录运行一次 `go test ./...` 就覆盖所有 module。

按变更范围追加检查：

- 修改依赖：在受影响 module 运行 `go mod tidy`，检查依赖 diff；项目已配置 `govulncheck` 时运行它。
- 修改并发：在环境支持时运行 `go test -race ./...`。
- 修改 build tags、平台代码或 CGO：使用目标 `GOOS`、`GOARCH`、tags 和 CGO 设置执行构建或测试。
- 修改生成代码：使用仓库固定的生成命令，并确认生成器版本和生成 diff。
- 修改公开 package：验证文档、示例、兼容性和下游调用方。

如果仓库已有 Makefile、Taskfile 或 CI 命令，优先使用项目规定的验证入口，并确认相关 Go 检查没有被跳过。

## 完成标准

- 修改过的 Go 文件已格式化，生成文件只通过项目规定的生成流程更新。
- 受影响 package 的测试、静态检查和构建已通过；无法运行的检查已说明原因和剩余风险。
- `go.mod`、`go.sum`、`go.work` 和 `go.work.sum` 的变化均由任务需要产生，并已审查。
- 并发、context、资源释放、错误链和外部边界的失败路径已按变更风险验证。
- 公开 API、配置、部署或架构发生变化时，相关文档、任务记录和 vault 记忆已同步。
