# 10 - Vault 项目记忆系统

## 定位

`vault/` 是项目记忆系统。它的目标不是保存所有文档，而是让 Agent 在正确时机读取正确上下文。

## 必备结构

```text
vault/
├── index.md
├── project.md
├── runtime.md
├── governance.md
├── decisions.md
├── handoff.md
├── tasks/
│   ├── README.md
│   └── .gitkeep
└── details/
    ├── architecture.md
    ├── development.md
    ├── api.md
    ├── agent.md
    └── domain.md
```

必备文件：

- `vault/index.md`
- `vault/project.md`
- `vault/runtime.md`
- `vault/governance.md`
- `vault/decisions.md`
- `vault/handoff.md`
- `vault/tasks/README.md`

`details/*` 只有在存在真实重复读取场景时才创建。

## 文件职责

### index.md

vault 上下文路由表。

它定义：

- 默认读取路径；
- 何时读取 project、runtime、governance、decisions、handoff、任务文件或 details；
- 各类记忆的更新规则。

### project.md

稳定项目方向。

读取场景：

- Agent 第一次进入项目；
- 项目方向或范围不清楚；
- 任务可能引入模块、框架、服务或新边界。

不要在这里记录当前任务进展或交接流水。

### runtime.md

当前项目运行态。

任何非琐碎任务前都要读取。保持短小，建议 50-120 行。

它应包含：

- 当前阶段；
- 活跃任务或任务指针；
- 当前进展；
- 没有任务文件时的验收标准；
- 当前约束；
- 最近变化；
- 已知风险；
- 必须运行的检查；
- 下一步建议。

长内容迁移到 `tasks/*`、`decisions.md` 或 `details/*`。

### governance.md

任务授权、追踪、验收、升级和多 Agent 接力规则。

非琐碎任务前必须读取。

### decisions.md

长期有效决策。

当架构、技术栈、API 契约、数据模型、依赖、项目范围或 Agent 协作规则变化时更新。

### handoff.md

任务中断、模型切换、工具切换或多 Agent 接力时的最近交接上下文。

只保留最近 1-3 次关键交接。稳定结论迁移到 `decisions.md`；当前状态迁移到 `runtime.md`；执行历史迁移到任务文件。

### tasks/

追踪任务和治理任务的任务契约与执行记录。

简单的一次性任务可以留在 `runtime.md`。

### details/

按路由读取的长上下文：

- `details/architecture.md`：架构、模块、数据流和边界。
- `details/development.md`：工具、命令、依赖、CI/CD 和环境。
- `details/api.md`：API 设计和契约。
- `details/agent.md`：Agent、LLM、Prompt 和工具行为。
- `details/domain.md`：领域术语和规则。

## 默认读取路径

非琐碎任务：

```text
AGENTS.md
vault/index.md
vault/runtime.md
vault/governance.md
```

第一次进入项目追加读取：

```text
vault/project.md
```

接手交接任务追加读取：

```text
vault/handoff.md
```

追踪任务或治理任务追加读取：

```text
vault/tasks/<task-id>.md
```

## 更新规则

- 非琐碎任务完成后更新 `runtime.md`。
- 追踪任务或治理任务更新 `tasks/*`。
- 产生长期结论时更新 `decisions.md`。
- 任务中断或转交时更新 `handoff.md`。
- `runtime.md` 膨胀时，将细节迁移到对应目标文件。
