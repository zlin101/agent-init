# 70 - 既有项目接入流程

## 定位

接入流程用于已经存在的项目。

目标是在不改变既有工程代码、依赖、业务结构和运行逻辑的前提下，引入 Agent-Native 的记忆管理、任务治理和交接机制。

它不是新项目初始化，也不是工程迁移。

一句话定义：

> 接入模式只安装或更新 Agent 协作层，不改业务工程层。

## 适用场景

- 已有项目希望引入 `vault/` 项目记忆系统。
- 已有项目希望引入 `AGENTS.md`、`CLAUDE.md` 等 Agent 入口规则。
- 已有项目希望引入任务契约、授权等级、验收门和 handoff 机制。
- 已有项目希望规范多 Agent 接力，但不调整代码结构。

## 允许修改

默认只允许创建或更新 Agent 协作层文件：

- `AGENTS.md`
- `CLAUDE.md`、`CODEX.md`、`GEMINI.md` 等工具入口文件，按项目需要创建
- `vault/`
- `vault/index.md`
- `vault/project.md`
- `vault/runtime.md`
- `vault/governance.md`
- `vault/decisions.md`
- `vault/handoff.md`
- `vault/tasks/README.md`
- `vault/tasks/.gitkeep`
- `vault/details/*`，仅在已有项目确实需要时创建
- `skills/`
- `skills/agent-task/SKILL.md`

可选修改：

- `README.md` 中添加极短 Agent 协作说明，但必须先说明，并尽量避免打扰原 README 结构。

## 禁止修改

除非用户明确授权，接入模式禁止修改：

- 业务源码目录，例如 `app/`、`src/`、`lib/`、`packages/`
- 测试目录，例如 `tests/`、`spec/`、`__tests__/`
- 依赖文件，例如 `pyproject.toml`、`package.json`、`go.mod`、`Cargo.toml`
- 锁文件，例如 `uv.lock`、`package-lock.json`、`pnpm-lock.yaml`、`Cargo.lock`
- 构建、部署或 CI 配置，例如 `Dockerfile`、`.github/workflows/*`
- 数据库迁移、配置文件或环境文件
- 既有业务文档的大段内容
- 任何真实密钥、Token、密码或凭据

如果接入需要触碰上述文件，必须升级为用户确认事项。

## 接入前扫描

Agent 执行接入前，应只做只读扫描：

1. 查看根目录文件。
2. 查找既有 Agent 入口文件：`AGENTS.md`、`CLAUDE.md`、`CODEX.md`、`GEMINI.md`、`.cursor/rules`。
3. 查找既有项目文档：`README.md`、`docs/`、`CONTRIBUTING.md`。
4. 查找既有记忆或任务目录：`vault/`、`memory/`、`docs/adr/`、`decisions/`。
5. 识别项目类型和技术栈，但不改依赖或代码。
6. 检查工作区是否已有未说明的变更。

扫描后，Agent 应给出接入计划，列出将创建或修改的协作层文件。

## 冲突处理

### 已存在 AGENTS.md

不要直接覆盖。

处理方式：

1. 读取原文件。
2. 保留项目已有规则。
3. 在不削弱原规则的前提下，加入 vault 和 governance 读取规则。
4. 如规则冲突，先指出冲突并请求确认。

### 已存在 CLAUDE.md / CODEX.md / GEMINI.md

保持与 `AGENTS.md` 语义一致。

工具专属说明可以保留，但不得覆盖通用治理规则。

### 已存在 vault/

不要覆盖。

处理方式：

1. 读取现有结构。
2. 缺什么补什么。
3. 已有文件先合并，不直接替换。
4. 对语义冲突的内容请求确认。

### 已存在 docs/adr 或 decisions

不要迁移历史记录。

在 `vault/decisions.md` 中添加指针，说明长期决策还可能存在于原位置。

### 已存在 README.md

默认不修改。

如需要添加 Agent 协作说明，只添加短段落，并避免重写原 README。

## 接入步骤

1. 读取 `init/INIT.md`。
2. 读取 `init/protocol/README.md`。
3. 读取 `init/protocol/10-vault.md`。
4. 读取 `init/protocol/20-governance.md`。
5. 读取 `init/protocol/30-agent-entry.md`。
6. 读取 `init/protocol/40-skills.md`。
7. 执行接入前扫描。
8. 输出接入计划，说明将创建或修改哪些协作层文件。
9. 合并或创建 Agent 入口文件。
10. 合并或创建 `vault/`。
11. 合并或创建 `skills/`。
12. 在 `vault/project.md` 记录“这是既有项目接入，不是新项目初始化”。
13. 在 `vault/runtime.md` 记录接入状态、风险和下一步。
14. 在 `vault/decisions.md` 记录接入决策。
15. 如发生中断或存在未完成事项，更新 `vault/handoff.md`。
16. 运行只读或文档级检查；不要运行会改变工程状态的命令，除非用户授权。

## 接入验收

接入完成必须满足：

- 未修改业务源码。
- 未修改依赖和锁文件。
- 未修改测试、构建、部署或 CI 配置。
- Agent 入口文件会路由到 `vault/index.md`、`vault/runtime.md` 和 `vault/governance.md`。
- `vault/` 必备文件存在。
- `vault/governance.md` 定义任务等级、授权等级、任务契约、验收门和接力规则。
- `skills/agent-task/SKILL.md` 存在。
- `vault/runtime.md` 明确记录接入完成状态。
- `vault/decisions.md` 记录接入模式决策。
- 所有冲突和未完成事项已记录或请求确认。

## 接入模式的授权

接入模式默认属于 Authority 2。

如果需要修改 README 的短说明，仍可视为 Authority 2，但必须提前说明。

如果需要修改源码、依赖、测试、构建、部署或 CI，必须升级为 Authority 3，并取得用户确认。

## 接入输出建议

Agent 完成接入后，应向用户报告：

- 创建或修改了哪些协作层文件；
- 明确没有触碰哪些工程代码或配置；
- 发现了哪些既有规则或冲突；
- 后续 Agent 应从哪些文件开始读取；
- 是否存在需要用户确认的剩余事项。
