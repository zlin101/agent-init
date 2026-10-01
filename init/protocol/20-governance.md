# 20 - 协作治理

## 定位

治理协议定义 Agent 如何获得授权、任务如何追踪、工作如何验收，以及多个 Agent 如何接力。

本协议以任务契约为核心，而不是以固定角色为核心。

## 核心对象

- Context：Agent 必须读取什么。
- Task：Agent 被授权做什么。
- Decision：哪些结论影响未来工作。
- Authority：Agent 可以执行到什么影响等级。
- Acceptance：什么证明任务可以关闭。

## 任务等级

判定只有一条 canonical 流程，按顺序执行：

```text
命中 Level C 风险域？
→ 是：C

否则，中断恢复或协作成本是否明显较高？
→ 是：B

否则：
→ A
```

规模（文件数、diff 行数、验收项数量、预计时长）可提示进一步判断，但不能单独决定等级。后来意外中断 ≠ 最初分类自动错误：升级在事实出现时发生，不追溯改写已完成任务的分级。

### Level C: Governed Task

命中以下任一风险域即属于治理任务，一行修改也不例外：

- 安全 / 隐私 / 权限；
- 公开 API 或外部契约（含删除公共能力、外部服务集成）；
- 持久数据或数据迁移（含数据模型变化）；
- 部署或生产行为；
- 依赖变更（含引入新框架）；
- 实质成本或配额；
- 架构方向或重大架构决策；
- 治理规则或策略（含 Agent 治理规则）。

记录在：

- `vault/tasks/TASK-xxxx-short-title.md`
- `vault/decisions.md`
- 必要时记录到相关 `vault/details/*`

治理任务通常需要用户确认。

### Level B: Tracked Task

未命中 Level C 风险域，但中断恢复或协作成本明显较高时追踪。强信号包括：

- 在已知信息下预计跨 session；
- 需要真实 handoff；
- 多 Agent / 多人 ownership；
- 依赖外部系统状态；
- 存在多阶段 gate；
- acceptance 状态需要持续追踪；
- 存在不可由 diff/tests 低成本恢复的 execution state；
- 在非 C 风险域内仍有明显 migration/rollback 或审计协调成本。

这些是强信号，不是满足即升级的机械清单；结论始终回到：中断恢复或协作成本是否明显较高。

记录在 `vault/tasks/TASK-xxxx-short-title.md`。

### Level A: Simple Task

低风险，恢复和协调成本低：diff、工作区和测试足以低成本重建状态。默认不创建 TASK lifecycle，从实时工作区、Git diff 与测试结果恢复；仅当 project-global runtime 确实变化时更新 `vault/runtime.md`。

最小字段：

```md
Objective:
Acceptance:
Required Check:
```

示例：

```text
4~5 个文件，但低风险、单 session、易恢复 → A
1 个文件，但跨 session 外部调试、多阶段 gate → B
1 行 dependency/auth/public API contract → C
```

## 任务生命周期

追踪与治理任务在 `trellium-task-state` 状态块中使用统一 lifecycle 枚举：

```text
draft | active | blocked | ready_for_review | accepted | superseded
```

- `draft`：任务已建立，尚未开始执行。
- `active`：执行中。
- `blocked`：被阻塞；阻塞原因记录在任务文件（真实外部中断才可能另有 handoff delta）。
- `ready_for_review`：等待用户验收。
- `accepted`：验收通过，任务关闭。
- `superseded`：被其他任务替代。

lifecycle、Authority、当前 slice 与 Gate 结果的唯一 owner 是任务文件顶部的 `trellium-task-state` 状态块（schema 见 `10-vault.md`）；`runtime.md` 不保存 TASK 投影。暂停且暂不推进的工作进入 `parked.md`，不是独立 lifecycle 值。Level A 没有持久化 TASK lifecycle，从实时工作区、Git diff 与测试结果恢复。

## 授权等级

### Authority 0: Read Only

Agent 只能查看、分析、总结和提出建议，不能修改文件。

### Authority 1: Local Edit

Agent 可以完成低风险局部修改。

允许示例：

- 修 typo；
- 添加或调整小测试；
- 修复边界清晰的 bug；
- 更新 `vault/runtime.md`；
- 小范围文档修正。

### Authority 2: Scoped Change

Agent 可以在说明边界和计划后执行中等范围修改。

允许示例：

- 新增局部模块；
- 修改内部实现；
- 添加开发依赖；
- 调整测试结构；
- 更新局部文档。

要求：

- 编辑前说明范围；
- 运行必要检查；
- 更新相关 vault 文件。

### Authority 3: Approval Required

必须先获得用户确认。

示例：

- 引入新框架；
- 改变架构方向；
- 改变公开 API；
- 改变数据模型；
- 删除公共能力；
- 引入外部服务；
- 修改安全、权限、隐私、成本或部署行为。

### Authority 4: Forbidden

Agent 禁止：

- 保存真实密钥、Token、密码或凭据；
- 绕过测试或伪造验证结果；
- 静默覆盖用户改动；
- 删除自己未理解的代码；
- 在单元测试中调用真实外部服务；
- 未经明确授权执行破坏性命令。

## 任务契约

追踪任务和治理任务必须包含：

- Objective
- Scope
- Out of Scope
- Context Required
- Capability Tags
- Authority Level（数值由状态块承载，正文不设第二份可编辑副本）
- Allowed Changes
- Forbidden Changes
- Acceptance Criteria
- Required Verification
- Required Memory Updates
- Handoff Requirement

任务文件顶部的 `trellium-task-state` 状态块是 lifecycle、authority_level、当前 slice 与 Gate 结果的唯一 owner；任务正文的 Authority 段只保留 Allowed、Requires Approval、Forbidden（行为边界）。状态块不授予批准。

Capability Tags 只描述工作需要的能力，不授予权限。

常见标签：

- architecture
- implementation
- testing
- review
- documentation
- debugging
- release
- agent-governance

## 验收门

任务只有在满足以下条件后才能关闭：

1. 逐条检查验收标准；
2. 必要验证已运行并记录结果；
3. 代码、测试和文档已同步；
4. `vault/runtime.md` 已更新；
5. 长期有效决策已记录在 `vault/decisions.md`；
6. 未完成事项或风险已记录在任务文件（验收 gate 不把普通 handoff 当风险台账）；
7. 没有未说明的高影响变更。

测试通过不等于任务完成。任务完成必须同时满足验收、验证和记忆更新。

采用 local lifecycle 的任务（`storage_mode=local` 或 `private`）进入 `accepted` 前还必须完成 Durable Knowledge Disposition（定义见 `10-vault.md`）：`pending` 不得进入 `ready_for_review` 或 `accepted`；`none` 需写明理由；`distilled` 只列 canonical 目标文件，不复制正文。契约错误、过期或不安全的任务走 `superseded` 立即废止，不被该 gate 阻塞，未处置事项显式转交。采用 local lifecycle 的任务关闭后，删除 `vault/handoff.md` 中与其相关的 transient delta（消费即删；durable 结论先落入 canonical 文件）。tracked 任务默认 `not_applicable`。

local/private 任务在 terminal 转换后执行 Historical Retention（流程与 Store 契约见 `10-vault.md`）：TASK 与已开展 ledger review 的相应 ledger 作为一组分别写入本机 Store 并逐份 get 验证，整组成功才算 closure retention 完成；失败保留 source、不回滚 accepted、幂等重试。默认不 cleanup，删除 source 需 owner 明确授权。tracked 不触发；Private 身份和来源保持 ignored，外部 Store 不进入项目 Git。

## 升级规则

出现以下情况时，必须升级任务等级或请求确认：

- 需求存在多个合理解释；
- 修改影响公开行为；
- 修改扩大项目范围；
- 需要新依赖或外部服务；
- 需要删除或迁移既有能力；
- 必要检查失败但 Agent 想继续推进；
- 当前任务无法满足验收标准；
- 文档与实现冲突；
- 用户改动与当前计划冲突。

升级事件同时是治理反馈信号：当升级暴露 `governance.md` 的规则空白、边界模糊或必要检查过时时，记录为治理修订候选，并按 Level C 提请用户确认。治理文件不通过日常任务直接修改。

## 多 Agent 接力

handoff 是双重触发的：仅当 (1) 发生真实中断（完成前的会话边界、Agent 所有权切换、owner 暂停、环境/外部依赖不可用、不可重现的半完成瞬态操作），且 (2) 存在无法从 canonical 状态（TASK、Git、工作区、重跑测试、durable knowledge）低成本推导的恢复事实时，才创建或更新 `vault/handoff.md`。正常完成、等待 acceptance、完成 review、单纯的 open lifecycle、普通下一步或完全可推导的干净会话边界，均不创建、不更新 handoff。

每条 handoff（任务编号命名，无任务编号时用 SESSION）只含三个小节：

- `### Why interrupted`：为什么在当前上下文停下
- `### Transient context not captured elsewhere`：无法从 canonical 状态重现的现场
- `### Exact resume point`：精确续作动作（仅在超出任务 slice 导航价值时写）

恢复顺序：先读 TASK 文件、实时 Git/工作区并重跑测试，再读 handoff 补齐瞬态 delta；delta 消费后删除该条目。branch、HEAD、脏文件等实时 Git 事实在恢复时现场读取，handoff 不把它们当权威记录；不保存环境快照充当状态副本。

如果任务文件已存在，`handoff.md` 应指向任务文件，不重复完整任务记录。未完成风险属于任务文件，验收 gate 在任务文件记录它们，不写普通 handoff。
