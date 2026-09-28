# 10 - Vault 项目记忆系统

## 定位

`vault/` 是项目记忆系统。它的目标不是保存所有文档，而是让 Agent 在正确时机读取正确上下文。

## 索引原则

增长进目录，读取走索引。任何会增长的内容（决策、任务、细节），正文进目录按需读取；索引层保证默认读取路径永远短。

`index.md` 的职责是"路由 + 项目策略"：路由表决定读什么，`trellium-policy` 策略块是项目预算与 TASK storage 的唯一配置来源。它不保存运行态，也不是第二个状态面。新增记忆类型一律按此模式扩展。

## 当前事实 Owner

同一事实只有一个权威位置；其他位置只能是派生投影或带时间戳的历史快照。

| 事实 | 唯一 Owner | 其他位置 |
| --- | --- | --- |
| Level A 当前状态 | `runtime.md` inline 记录 | 无任务文件 |
| Level B/C lifecycle、当前 slice、Gate 结果 | 任务文件顶部 `trellium-task-state` 状态块 | `runtime.md` 行是派生投影 |
| Level B/C 当前契约 | 任务文件 current-contract 段（Objective/Scope/Authority/Acceptance 等） | Execution Record 只存执行历史 |
| 当前 Focus | `runtime.md` | 只表示注意力，不等于 lifecycle |
| 长期事实 | `project.md`、Active 决策或明确权威文档 | 任务文件可记录实施来源 |
| 中断原因与下一动作 | `handoff.md` | 不保存实时 Git 状态为权威 |
| branch、HEAD、脏文件 | 实时 Git | handoff 只可保存带观察时间、明确非权威的历史快照 |
| 项目预算与 TASK storage | `index.md` 的 `trellium-policy` 策略块 | 其他文件只路由，不复制当前值 |

## 记忆分层

| 层 | 文件 | 生命周期 |
| --- | --- | --- |
| 热文件 | `runtime.md`、`handoff.md`、`decisions.md` | 高频更新；有预算线；压缩对象 |
| 治理文件 | `governance.md`、`collaboration.md`、`parked.md` | 事件驱动更新；压缩只出提案 |
| 结构文件 | `index.md`、`project.md`、`tasks/README.md` | 极少更新；压缩不可直接修改 |
| 归档区 | `tasks/<task-id>.md`、`decisions/`、`details/*` | 只增；压缩内容的去向 |

预算线、压缩流程与安全边界见 `15-vault-compaction.md`。

## 必备结构

```text
vault/
├── index.md
├── project.md
├── runtime.md
├── governance.md
├── decisions.md
├── decisions/            # 首次压缩时创建：决策正文
├── handoff.md
├── parked.md
├── tasks/
│   ├── README.md
│   ├── .gitkeep
│   └── archive/          # 里程碑归档时创建
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
- `vault/parked.md`
- `vault/tasks/README.md`

同一主题的长内容被重复读取或迁移 2 次以上时创建 `vault/details/<topic>.md`。

## 文件职责

### index.md

vault 上下文路由表 + 项目策略载体。

它定义：

- 默认读取路径；
- 何时读取 project、runtime、governance、decisions、handoff、任务文件或 details；
- 各类记忆的更新规则；
- `trellium-policy` 策略块：项目预算与 TASK storage 的唯一配置来源（见"项目策略块"）。

### project.md

稳定项目方向。

读取场景：

- Agent 第一次进入项目；
- 项目方向或范围不清楚；
- 任务可能引入模块、框架、服务或新边界。

不要在这里记录当前任务进展或交接流水。

### runtime.md

当前项目运行态。

任何非琐碎任务前都要读取。保持短小，建议 50-120 行。超过 120 行即触发压缩（见 `15-vault-compaction.md`）。

它应包含：

- 当前阶段；
- 活跃任务指针表：`Focus` 行指向当前主线任务，`Active Tasks` 表每行一个并行任务（任务编号、一句话目标、状态、下一步），支持多任务并行；
- 当前进展（对应 Focus 任务）；
- 没有任务文件时的验收标准；
- 当前约束；
- 最近变化；
- 已知风险；
- 必须运行的检查；
- 下一步建议。

TASK 行的状态使用统一 lifecycle 枚举（定义见 `20-governance.md`）：`draft | active | blocked | ready_for_review | accepted | superseded`。对有任务文件的 TASK，行内状态是 `trellium-task-state` 状态块的派生投影：lifecycle 变化先改状态块，再同步对应行。`Focus` 只表示当前注意力，不等于 lifecycle。暂停且暂不推进的任务降级为 `parked.md` 条目，不是独立状态。没有任务文件的 Level A 行仍以 `runtime.md` 为权威。

长内容迁移到 `tasks/*`、`decisions.md`、`parked.md` 或 `details/*`。

### governance.md

任务授权、追踪、验收、升级和多 Agent 接力规则。

非琐碎任务前必须读取。

### decisions.md

长期有效决策。

当架构、技术栈、API 契约、数据模型、依赖、项目范围或 Agent 协作规则变化时更新。

每条决策标注生命周期状态：`Active`、`Superseded by D-xxxx`、`Merged into D-xxxx` 或 `Expired`。超过 150 行或 8 条完整记录时索引化：`decisions.md` 变纯索引，正文迁入 `vault/decisions/D-xxxx-slug.md`，默认只读索引。

### handoff.md

任务中断、模型切换、工具切换或多 Agent 接力时的最近交接上下文。

只保留最近 1-3 次关键交接，每条以任务编号命名（无任务编号时用 SESSION）。稳定结论迁移到 `decisions.md`；当前状态迁移到 `runtime.md`；执行历史按任务编号归并进对应任务文件。

handoff 只保存持久叙事：目标、进展、失败尝试、阻塞、下一步、行动前先读取的文件。branch、HEAD、脏文件等实时 Git 事实在恢复时现场读取，不作为 handoff 权威记录；只可保存一条带观察时间、明确标注非权威的环境快照。

### parked.md

用户挂起事项的冷索引：挂起不遗忘，提及才读取，不进入默认读取路径。

条目格式：`P-xxxx · 类型(task/decision/question) · 标题 · 一句话上下文 · 重启触发器 · 日期`。有任务文件的记 `TASK-xxxx` 指针，没有的记 2-4 行上下文。

生命周期与 `runtime.md` 双向流动：任务被用户挂起时记入；用户重新提起时升回任务文件（Draft）或 `runtime.md`。Agent 不得删除条目；压缩清理只出提案，由用户确认。

### tasks/

追踪任务和治理任务的任务契约与执行记录。

简单的一次性任务可以留在 `runtime.md`。

Level B/C 任务文件在标题之后、叙事正文之前放置 `trellium-task-state` 状态块，是 lifecycle、authority_level、当前 slice 与 Gate 结果的唯一 owner（schema 见下方"状态块与策略块"）。`TASK-*-review.md` 台账与 `tasks/archive/` 是冷历史，不需要状态块。

TASK storage 由 policy 块的 `task_storage` 决定：`local` 时任务文件、review 台账与 archive 不 tracked、不 staged，Accepted 后的结论必须先蒸馏进 `decisions.md` 等公开位置；`tracked` 时完整任务流水纳入版本控制。Skill/Agent 首次接入前询问 owner 并推荐 `local`，owner 未指定时按 local 执行。Agent 在 local 模式创建 `vault/tasks/.gitignore` 的窄规则，不修改项目根 `.gitignore`；storage 迁移由 owner 决定，工具不自动 untrack。

local 任务的生命周期边界（Durable Knowledge Disposition，人工 gate 而非机器校验）：

- local 任务进入 `accepted` 前，必须在任务文件的 Memory Updates 中显式记录处置结果：`none — <理由>`（没有会约束未来 clone 的新事实）或 `distilled — <canonical 目标文件>`（长期事实的唯一正式正文写在那些文件中，不在此复制第二份）；未记录视为 `pending`，`pending` 的 local 任务不得进入 `ready_for_review` 或 `accepted`。
- 没有长期结论的任务允许明确记录 `none`，关闭后不留下额外项目记忆；不把 TASK 全文、review 流水或执行日志复制进 Vault。
- `superseded` 不被该 gate 阻塞：错误、过期或不安全的任务契约可立即废止；未处置的长期事实作为显式 next action 转交替代任务或 owner。
- local 任务进入 `accepted`/`superseded` 后删除 `runtime.md` 对应行（closed 任务不占热路径），并压缩 `handoff.md` 相关条目；稳定结论必须已落入 canonical 文件。
- fresh clone 中被忽略的 local TASK 文件必然不存在：`runtime.md` 的 open 摘要只是未验证的工作线索，不是任务契约，不授予 Authority；继续工作必须取回原任务文件，或经 owner 批准后重建任务契约。
- tracked 任务默认 `not_applicable`（仍可主动记录 `none`/`distilled`），其 runtime closed 行为不变；该规则只作用于新关闭或重新打开后再关闭的任务，不批量回填历史。

### details/

按路由读取的长上下文：

- `details/architecture.md`：架构、模块、数据流和边界。
- `details/development.md`：工具、命令、依赖、CI/CD 和环境。
- `details/api.md`：API 设计和契约。
- `details/agent.md`：Agent、LLM、Prompt 和工具行为。
- `details/domain.md`：领域术语和规则。

## 状态块与策略块

两个结构化块承载"当前状态事实"，其余内容保持 Markdown：

### trellium-task-state v1（任务状态块）

固定标记 `trellium-task-state`，HTML 注释包裹的严格 JSON（不支持 YAML、注释或尾逗号），放在 Level B/C 任务文件标题之后、正文之前：

```html
<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0060",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "ready_for_review"
}
-->
```

- 必填：`schema_version`（整数 `1`）、`task_id`（`TASK-[0-9]{4,}`，与文件名开头一致）、`level`（`B | C`）、`authority_level`（整数 `0..4`）、`lifecycle`（统一枚举，见 `20-governance.md`）。
- 可选：`current_slice`（非空字符串，存在时 lifecycle 与 Gates 描述当前 slice）；`gates`（Gate ID 为非空字符串，不固定语义，值限 `pending | in_progress | passed | partial | blocked | not_authorized | not_applicable`）。
- 未定义字段非法；改变字段含义必须提升 `schema_version`。
- 每个任务实体恰好零或一个状态块：零个是 legacy（报 warning，不猜状态），多个非法。
- 状态块不授予批准：Allowed、Requires Approval、Forbidden 和验收条件仍由任务正文与用户指令决定。

### trellium-policy v1（项目策略块）

固定标记 `trellium-policy`，放在 `vault/index.md` 开头说明之后：

```html
<!-- trellium-policy
{
  "schema_version": 1,
  "task_storage": "tracked",
  "budgets": {
    "runtime": {"max_lines": 120, "max_recent_entries": 10},
    "handoff": {"max_lines": 100, "max_entries": 3},
    "decisions": {"max_lines": 150, "max_records": 8},
    "parked": {"max_lines": 60, "max_entries": 20},
    "tasks": {"max_active_tasks": 40}
  }
}
-->
```

- 必填：`schema_version`（整数 `1`）、`task_storage`（`tracked | local`）。`budgets` 可选。
- 预算是可选正整数；键或对象缺失表示"不设该上限"。模板中的数字是初始化默认值，不是猜测出的普适阈值。
- 本协议与模板其他位置出现的预算数字都是初始化默认值；项目当前预算以该块为唯一来源。缺失策略块的项目是 legacy：人工判断按初始化默认值，机械校验只测量、不套用默认值。
- 新接入项目由 Agent 先询问 owner并推荐 `local`；owner 未指定时默认 local。`tracked` 用于需要共享完整任务流水的项目。
- 重复接入与升级保持既有选择；tracked/local 迁移由 owner 单独评审，工具不自动 untrack 或改写既有 storage。

`python3 trellium.py check <target>` 对以上结构与投影做只读确定性校验。

## 默认读取路径

非琐碎任务：

```text
AGENTS.md
vault/index.md    # 含任务等级与授权速查表
vault/runtime.md
```

满足任一条件时追加读取完整 `vault/governance.md`：

- 任务为 Level B 或 Level C；
- 任务等级或授权判定模糊；
- 任务涉及治理规则本身。

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

用户提到挂起、搁置或暂停的事项时追加读取：

```text
vault/parked.md
```

## 更新规则

- 热文件更新纪律：固定段落顺序，每条内容占一行；状态或进展变化用单行替换，不重写整段——保证每次更新是小 diff。
- Level B/C 任务状态变化先更新任务文件的状态块，再同步 `runtime.md` 对应行（投影）。
- 非琐碎任务完成后更新 `runtime.md`（Active Tasks 表中对应任务行）。
- 追踪任务或治理任务更新 `tasks/*`。
- 产生长期结论时更新 `decisions.md`。
- 任务中断或转交时更新 `handoff.md`。
- 用户挂起任务或决定时记入 `parked.md`；重新提起时升回。
- `runtime.md` 膨胀时，将细节迁移到对应目标文件。
- 更新热文件时检查预算线；超出时按 `15-vault-compaction.md` 执行压缩。
- 压缩语义判定只提案，由用户确认；未确认的决策保持 `Active`。
