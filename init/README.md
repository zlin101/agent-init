# Agent Native Init

`init/` 是本仓库的可迁移源协议目录。

使用本项目时，优先迁移和维护 `init/`。仓库根目录下的 `AGENTS.md`、`vault/`、`skills/`、`README.md`、源码、测试和依赖文件，是当前沙盒根据协议生成或验证出来的产物，不是迁移到其他项目时必须复制的源内容。

## 核心入口

- `INIT.md`：初始化入口清单，负责把 Agent 路由到协议模块。
- `protocol/`：模块化协议正文，定义项目记忆、治理、入口文件、skills、工程约束、初始化流程、接入流程、执行模式和协作画像。
- `protocol/profiles/`：可选项目类型 profile。当前包含 Python 后端最小 profile。

## 使用方式

### 新项目初始化

让 Agent 读取：

1. `init/INIT.md`
2. `init/protocol/README.md`
3. `init/protocol/60-initialization-flow.md`
4. 需要的 profile，例如 `init/protocol/profiles/python-backend.md`

Agent 应根据协议在目标项目中生成自己的入口文件、`vault/`、`skills/`、README 和必要工程骨架。

### 既有项目接入

让 Agent 读取：

1. `init/INIT.md`
2. `init/protocol/README.md`
3. `init/protocol/70-adoption-flow.md`

接入模式默认只安装或更新 Agent 协作层，不修改业务源码、依赖、测试、构建、部署或 CI 配置。

### 协议修订

修改初始化行为时，只改 `init/INIT.md` 或 `init/protocol/*`。

当前项目里的 `vault/` 和 `skills/` 可以用于验证协议产物是否合理，但不要把它们当成可迁移源协议。

## 协议模块

按顺序读取：

1. `protocol/00-overview.md`
2. `protocol/10-vault.md`
3. `protocol/20-governance.md`
4. `protocol/30-agent-entry.md`
5. `protocol/40-skills.md`
6. `protocol/50-engineering-constraints.md`
7. `protocol/60-initialization-flow.md`
8. `protocol/70-adoption-flow.md`
9. `protocol/80-execution-patterns.md`
10. `protocol/90-collaboration-profile.md`

## 边界

`init/` 负责定义“如何生成或接入 Agent 协作层”。

它不保存：

- 当前项目运行态；
- 当前任务历史；
- 具体业务需求；
- 真实密钥、Token、密码或凭据；
- 目标项目的业务源码；
- 目标项目的私有机器配置或外部账号信息。

## 提交边界

如果目标是发布或迁移 Agent Native Init 协议，只提交 `init/` 下的源协议文件。

不要把当前沙盒的生成物一并作为协议源提交，除非后续明确抽取为 `init/` 内的模板或 profile。
