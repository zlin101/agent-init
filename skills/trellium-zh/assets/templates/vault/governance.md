# Governance

## Core Rule

Agent 不按身份获得信任，而是按任务契约获得授权。工作只有通过验收门才能关闭。

## Task Levels

判定顺序：命中 Level C 风险域 → C；否则中断恢复或协作成本明显较高 → B；否则 → A。规模只提示进一步判断，不能单独决定等级；后来意外中断不追溯改写最初分级。

### Level C: Governed Task

风险域（一行修改也不例外）：安全/隐私、公开 API 或外部契约、持久数据/迁移、部署/生产行为、依赖变更、实质成本/配额、架构方向/重大架构决策、治理规则/策略。记录在任务文件和 `vault/decisions.md`；通常请求用户批准。

### Level B: Tracked Task

非 C 风险域，但中断恢复或协作成本明显较高：预计跨 session、需要真实 handoff、多 Agent/多人 ownership、外部系统状态、多阶段 gate、acceptance 持续追踪、diff/tests 难以低成本恢复的 execution state。记录在 `vault/tasks/TASK-xxxx-short-title.md`。

### Level A: Simple Task

低风险、恢复和协调成本低：diff、工作区和测试足以低成本重建。默认不持久化 TASK lifecycle；仅当 project-global runtime 确实变化时更新 `vault/runtime.md`。

## Task Lifecycle

`draft | active | blocked | ready_for_review | accepted | superseded`

lifecycle、Authority、当前 slice 与 Gate 结果只由任务文件的 `trellium-task-state` 状态块持有；`runtime.md` 不保存 TASK 投影。暂停且暂不推进的工作放 `parked.md`，不是 lifecycle 值。Level A 不持久化 TASK lifecycle，从工作区、Git diff 与测试结果恢复。

## Authority Levels

- Authority 0：只读分析。
- Authority 1：低风险局部修改。
- Authority 2：说明边界和检查后的限定范围修改。
- Authority 3：高影响工作需要批准。
- Authority 4：禁止。

## Forbidden

- 保存真实密钥、Token、密码、凭据、私有 URL 或个人账号细节。
- 伪造验证。
- 静默覆盖用户改动。
- 未经明确批准执行破坏性命令。
- 单元测试真实调用外部服务。

## Task Contract

追踪任务和治理任务必须包含：

- Objective
- Scope and out of scope
- Context required
- Capability tags
- Authority level（数值由 `trellium-task-state` 状态块承载，不设第二份可编辑副本）
- Allowed changes
- Requires approval
- Forbidden changes
- Acceptance criteria
- Required verification
- Required memory updates
- Handoff requirement

状态块不授予批准；行为边界仍由任务正文与用户指令决定。

## Acceptance Gates

关闭工作前：

1. 逐条检查验收标准。
2. 运行并记录必要验证。
3. 适用时同步代码、测试、文档和 vault 记忆。
4. 更新 `vault/runtime.md`。
5. 在 `vault/decisions.md` 记录长期决策。
6. 在任务文件记录未完成工作或风险（验收 gate 不把普通 handoff 当风险台账）。
7. 说明所有高影响变更。

测试通过不等于完成。

采用 local lifecycle 的任务（`storage_mode=local` 或 `private`）进入 `accepted` 前还必须完成 Durable Knowledge Disposition（Memory Updates 中的 `none — <理由>` 或 `distilled — <canonical 目标文件>`；未填写视为 `pending`，不得进入 `ready_for_review` 或 `accepted`）。契约错误走 `superseded` 立即废止，不受该 gate 阻塞。tracked 任务默认 `not_applicable`。

local/private terminal TASK 与必要 review 台账随后按 canonical History 契约成组 put/get 保全；失败保留来源、幂等重试，不回滚 accepted，默认不 cleanup。Private 身份及来源仍 ignored，外部 Store 不进入项目 Git；tracked 不触发。

## Escalation

需求有歧义、范围扩大、涉及高影响文件、必要检查失败、文档与实现冲突或用户改动与计划冲突时，升级或询问用户。

## Handoff

handoff 是双重触发的：仅当 (1) 发生真实中断，且 (2) 存在无法从 canonical 状态（TASK、Git、工作区、重跑测试、durable knowledge）低成本推导的恢复事实时，才创建或更新 `vault/handoff.md`。正常完成、等待 acceptance、完成 review、open lifecycle、普通下一步或可推导的干净会话边界，均不写 handoff。

每条 handoff（任务编号命名，无任务编号时 SESSION）只含三个小节：

- Why interrupted
- Transient context not captured elsewhere
- Exact resume point

恢复顺序：先读 TASK 文件、实时 Git/工作区并重跑测试，再读 handoff 补齐瞬态 delta；delta 消费后删除该条目。分支、HEAD、脏文件在恢复时通过 Git 现场读取，handoff 不保存状态副本。
