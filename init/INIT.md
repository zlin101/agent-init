# init/INIT.md

## 定位

`init/INIT.md` 是 Agent-Native 项目初始化的入口清单。

它不承载完整协议正文，而是负责把 Agent 路由到各个协议模块。协议模块定义 Agent 协作治理、项目记忆、任务契约、入口文件、技能、工程约束和初始化验收规则。

核心目标是初始化一个项目，使 Agent 能够：

- 用最少但正确的上下文进入项目；
- 理解当前任务状态；
- 通过任务契约获得授权；
- 按验收标准关闭任务；
- 沉淀长期有效决策；
- 在 Agent、模型或工具切换时完成交接。

## 协议模块

初始化或修订协议时，按顺序读取：

1. `init/protocol/00-overview.md`
2. `init/protocol/10-vault.md`
3. `init/protocol/20-governance.md`
4. `init/protocol/30-agent-entry.md`
5. `init/protocol/40-skills.md`
6. `init/protocol/50-engineering-constraints.md`
7. `init/protocol/60-initialization-flow.md`
8. `init/protocol/70-adoption-flow.md`
9. `init/protocol/80-execution-patterns.md`
10. `init/protocol/90-collaboration-profile.md`

如果项目类型已明确，还要读取对应 profile。当前脚手架使用：

- `init/protocol/profiles/python-backend.md`

## 生成目标

新项目初始化应创建或更新：

- Agent 入口文件，例如 `AGENTS.md` 和 `CLAUDE.md`；
- `vault/` 项目记忆系统；
- `vault/governance.md` 协作治理规则；
- `vault/tasks/` 任务契约规则；
- `skills/` 可复用 Agent 工作流；
- Agentic 执行模式；
- 可演化协作画像；
- 仅在所选 profile 需要时创建项目源码、测试和依赖文件；
- `README.md`；
- 记录最终初始化状态的 `vault/runtime.md`。

## 开源 Skill 包

如果目标是发布或安装一个自包含 Skill，而不是携带完整 `init/` 协议源目录，使用：

```text
init/skills/agent-native-init/
init/skills/agent-native-init-zh/
```

该 Skill 包提炼了本协议的核心设计，包括 Agent 入口规则、vault 记忆、任务契约治理、既有项目接入边界、review/reflection 和最小模板。它不要求目标项目存在 `init/`。`agent-native-init` 是英文版，`agent-native-init-zh` 是中文版。

既有项目接入时，只创建或更新 Agent 协作层：

- Agent 入口文件；
- `vault/`；
- `skills/`；
- 可选的极短 README 协作说明。

接入模式默认不修改业务源码、依赖、测试、构建、部署或 CI 配置。

## 规则

- 将本文件视为入口清单，不视为完整协议正文。
- 不要凭记忆执行初始化，必须按引用模块顺序执行。
- 核心治理协议不绑定任何单一语言或框架。
- 技术栈默认值放入 `init/protocol/profiles/*`。
- 不要在协议、vault、README、示例或测试文件中保存密钥、Token、密码或真实凭据。

## 验收标准

初始化只有在满足以下条件时才算完成：

- 生成的 Agent 入口文件会路由到 `vault/index.md`、`vault/runtime.md` 和 `vault/governance.md`；
- 必需的 vault 文件存在；
- governance 定义任务等级、授权等级、任务契约、验收门、升级规则和多 Agent 接力规则；
- 执行模式定义计划先行、上下文扎根、检查点化工作、人工判断信号和 skill 复利；
- collaboration profile 定义协作偏好的生成、更新、优先级和禁止边界；
- `vault/tasks/` 下存在追踪任务和治理任务规则；
- 必要检查已运行并记录结果；
- `vault/runtime.md` 反映当前状态；
- 长期有效决策已记录到 `vault/decisions.md`。
