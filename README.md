# Agent Native Init

Agent Native Init 是一套可迁移的 Agent 协作初始化协议。

它的目标不是生成某个固定技术栈的应用模板，而是给任何项目接入一层稳定的 Agent 协作能力：入口规则、项目记忆、任务治理、验收门、交接机制、可复用工作流和协作画像。

## 这个项目解决什么

长期使用 AI Agent 开发时，常见问题不是“Agent 不会写代码”，而是：

- 新会话不知道项目当前状态；
- Agent 没有清晰授权边界；
- 任务做到一半无法交接；
- 测试通过但验收没有关闭；
- 重要决策散落在聊天记录里；
- 多 Agent 或多工具切换时上下文断裂；
- 每个项目都要重新口头约定一套协作规则。

Agent Native Init 把这些约定收敛为一套项目级初始化协议，让 Agent 进入项目后知道：

- 先读什么上下文；
- 如何判断任务等级和授权等级；
- 哪些文件承载运行态、决策和交接；
- 什么情况下必须创建任务文件；
- 怎样验证任务完成；
- 哪些协作偏好可以沉淀，哪些不能覆盖硬规则。

## 核心产物

本仓库真正可迁移的核心是：

```text
init/
```

`init/` 是协议源目录。把 Agent Native Init 接入其他项目时，应该迁移或引用 `init/`，再由其中的协议指导目标项目生成自己的 Agent 协作层。

仓库根目录中的 `AGENTS.md`、`vault/`、`skills/`、`app/`、`tests/` 等，是当前沙盒根据协议生成出来的验证产物，不是迁移源。

如果只想安装一个自包含 Skill，而不是迁移完整协议源，可以使用：

```text
init/skills/agent-native-init/
init/skills/agent-native-init-zh/
```

这是从 `init/` 协议收敛出的开源 Skill 包，内含主工作流、协议精华 reference 和可复制模板，不依赖本仓库本地路径。`agent-native-init` 是英文版，`agent-native-init-zh` 是中文版。

## 目录结构

```text
init/
  INIT.md                         # 初始化入口清单
  protocol/
    README.md                     # 协议模块说明
    00-overview.md                # 总体定位和分层
    10-vault.md                   # 项目记忆系统
    20-governance.md              # 任务治理、授权和验收
    30-agent-entry.md             # Agent 入口文件规则
    40-skills.md                  # 可复用工作流
    50-engineering-constraints.md # 工程约束
    60-initialization-flow.md     # 新项目初始化流程
    70-adoption-flow.md           # 既有项目接入流程
    80-execution-patterns.md      # Agentic 执行模式
    90-collaboration-profile.md   # 可演化协作画像
    profiles/
      python-backend.md           # Python 后端最小 profile
  skills/
    agent-native-init/             # 自包含开源 Skill 包
    agent-native-init-zh/          # 自包含开源 Skill 包中文版
```

## 使用方式

### 新项目初始化

在目标项目中让 Agent 读取：

```text
init/INIT.md
init/protocol/README.md
init/protocol/60-initialization-flow.md
```

如果项目类型已明确，再读取对应 profile，例如：

```text
init/protocol/profiles/python-backend.md
```

Agent 应根据协议在目标项目中生成自己的：

- Agent 入口文件，例如 `AGENTS.md`；
- `vault/` 项目记忆系统；
- `vault/governance.md` 协作治理规则；
- `vault/tasks/` 任务契约规则；
- `skills/` 可复用工作流；
- 必要时的项目源码、测试和依赖文件。

### 既有项目接入

如果目标项目已经存在，只想接入 Agent 协作层，让 Agent 读取：

```text
init/INIT.md
init/protocol/README.md
init/protocol/70-adoption-flow.md
```

接入模式默认只创建或更新 Agent 协作层：

- Agent 入口文件；
- `vault/`；
- `skills/`；
- 可选的极短 README 协作说明。

除非用户明确授权，否则不要修改业务源码、依赖、测试、构建、部署或 CI 配置。

### 使用开源 Skill 包

如果你的 Agent 环境支持安装 Skills，可以将以下目录作为 Skill 包安装或复制：

```text
init/skills/agent-native-init/
init/skills/agent-native-init-zh/
```

使用该 Skill 时，Agent 会按包内 reference 和 templates 在目标项目中生成或合并：

- Agent 入口文件；
- `vault/` 项目记忆；
- 任务契约治理；
- handoff 和 collaboration profile；
- `skills/agent-task/SKILL.md` starter workflow。

该 Skill 适合跨项目复用；完整 `init/protocol/` 更适合继续设计和维护协议本身。

### 修订协议

如果要改 Agent Native Init 本身，只修改：

```text
init/INIT.md
init/protocol/*
```

当前仓库里的 `vault/`、`skills/` 和测试骨架可以用来验证协议是否合理，但它们不是协议源。

## 协议理念

### 任务契约优先

Agent 不按身份获得信任，而是按任务契约获得授权，并按验收标准关闭任务。

任务契约包含：

- 目标和范围；
- 明确不做什么；
- 必要上下文；
- 授权等级；
- 允许和禁止的修改；
- 验收标准；
- 必要验证；
- 记忆更新和交接要求。

### Vault 作为项目记忆

协议会在目标项目中生成 `vault/`，用于承载：

- 项目定位；
- 当前运行态；
- 治理规则；
- 长期决策；
- 任务记录；
- 交接信息；
- 协作偏好。

这样新 Agent、不同模型或不同工具进入项目时，可以从文件恢复上下文，而不是依赖聊天记录。

### 可迁移，而不是复制沙盒

不要把当前仓库的生成物整体复制到新项目。

正确方式是：

1. 迁移或引用 `init/`；
2. 让 Agent 读取 `init/INIT.md`；
3. 按协议在目标项目中生成属于它自己的协作层；
4. 根据目标项目实际情况更新 `vault/`、`skills/` 和 profile 产物。

## 当前状态

本仓库仍处于协议设计和初始化脚手架迭代阶段。

当前重点是打磨 `init/`，让它成为稳定、轻量、可迁移的 Agent 协作协议源。根目录的其他文件主要用于验证协议生成结果。

## 本地验证

当前沙盒带有最小 Python 骨架，用于验证初始化流程：

```bash
uv run pytest
```

这不代表 Agent Native Init 绑定 Python。Python profile 只是当前已有的一个最小示例。

## 提交边界

如果目标是发布或迁移 Agent Native Init 协议，提交内容应优先限制在：

```text
init/
README.md
```

除非明确需要更新当前沙盒状态，否则不要把 `vault/`、`skills/`、`app/`、`tests/` 等生成物作为协议源提交。
