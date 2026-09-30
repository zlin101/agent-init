# 50 - 通用工程约束

## 定位

本模块定义 Agent-Native 项目的语言无关工程约束。

项目类型相关细节放入 `init/protocol/profiles/*`。

## 通用约束

- 修改范围必须收敛到任务契约。
- 不做无关重构。
- 没有任务授权时，不引入框架、服务或依赖。
- 不在仓库中保存密钥。
- 不硬编码环境相关配置。
- 单元测试不真实调用外部服务。
- 外部 SDK 使用必须隔离在清晰模块边界内。
- 加入 Agent 功能时，Prompt 和 LLM 行为必须有清晰边界。
- 重要变更必须同步文档和 vault 记忆。

## 配置

配置必须集中管理。

包括：

- 端口；
- URL；
- 路径；
- 模型名称；
- 功能开关；
- 超时时间；
- API Key；
- Token；
- 密码。

敏感信息必须通过环境变量、密钥管理系统或部署平台注入。

## 测试

测试应确定、隔离、可重复。

- mock 或 fake 外部依赖。
- 不依赖开发者本机状态。
- 覆盖确定性的核心逻辑。
- 行为变化时添加或更新聚焦测试。

## 质量入口与提交规范

优先使用仓库已有的统一任务入口（Makefile、Taskfile 或 scripts），本地与 CI 走同一入口。

- 统一入口提供常见目标，如 `test`、`lint`、`format`、`check`；不绕过项目规定的验证脚本。
- 仓库没有统一入口时，按语言 profile 的默认命令执行质量检查。
- 提交前运行质量入口。

提交信息默认遵循 Conventional Commits 风格；仓库已有 gitlint、commitlint 或自有规范时沿用其约定。

- 类型前缀如 `feat`、`fix`、`refactor`、`docs`、`test`、`optimize` 等；仓库可自定义类型列表。
- 标题简明、可检索；不写无意义占位（如 `wip`、`update`）。
- 具体格式以仓库现有约定为准，本协议只提供默认。

## 文档同步

以下内容变化时更新 vault：

- 项目范围；
- 架构；
- API 契约；
- 数据模型；
- Prompt 或 Agent 行为；
- 测试策略；
- 部署方式；
- 依赖；
- 当前任务状态；
- 重要设计决策。

## 代码注释与 API 文档

注释的目标不是提高“注释率”，而是保存代码本身无法清晰、稳定表达的信息。代码表达 How / What；注释和 API 文档主要补充 Why、调用者可见契约、业务语义、不变量、边界条件，以及安全、并发、资源所有权、生命周期和部署约束。

- 公共 API 文档站在调用者视角，说明行为、重要参数与返回值语义、调用约束、错误或异常、副作用；不机械重复签名、类型或内部算法。
- 实现内部注释解释反直觉选择及其原因，不翻译代码。复杂内部声明只有在职责或约束无法从代码可靠读出时才补充说明。
- 代码难懂时，先改命名、拆分职责、简化控制流和数据结构；注释不能代替代码质量。
- TODO/FIXME 必须写明具体问题和移除条件；使用 Issue 系统时关联对应事项。
- 行为或约束变化时同步更新或删除注释。Git 保存历史，源码注释不保留已失效实现。
- 生成文件的注释从生成源修改；工具 directive、编译指令和其他机器语义注释不得按普通文本翻译或重排。

语言对公共 API 的行为、安全、错误与兼容性约定放在对应 profile；注释、文档语法和 directive 表达规范由 Comment/API Documentation Policy `docs/engineering/code-comments.md` 唯一拥有。显式选择 profile 时生成完整工程规范 `docs/engineering/profiles/<profile>.md`，并保留 Comment/API Documentation Policy `docs/engineering/code-comments.md`；`AGENTS.md` 按 root 与实际语言一跳路由，表达规则重叠处以 Comment Policy 为准。完整规则见 `70-adoption-flow.md`「Profile 工程规范」。

## 记忆目标

- 稳定项目方向：`vault/project.md`。
- 当前状态：`vault/runtime.md`。
- 任务契约和执行记录：`vault/tasks/*`。
- 长期决策：`vault/decisions.md`。
- 交接信息：`vault/handoff.md`。
- 挂起事项：`vault/parked.md`。
- 长上下文：`vault/details/*`。
- 可复用工作流：`skills/*/SKILL.md`。
