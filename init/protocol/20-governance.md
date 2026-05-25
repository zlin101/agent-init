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

### Level A: Simple Task

低风险、可在一次会话中完成的任务。

条件：

- 不改变架构。
- 不改变公开接口。
- 不引入依赖。
- 不影响数据模型。
- 不需要 Agent 接力。
- 通常只影响 1-2 个文件。

记录在 `vault/runtime.md`。

最小字段：

```md
Objective:
Acceptance:
Required Check:
```

### Level B: Tracked Task

需要独立追踪的任务。

满足任一条件即升级：

- 预计超过一次工作会话；
- 涉及 2 个以上文件；
- 验收标准超过 3 条；
- 需要设计、实现、测试和文档同步；
- 可能需要 Agent 交接；
- 存在明显风险或回滚成本；
- 需要保存失败尝试或执行历史；
- 用户要求可审计。

记录在 `vault/tasks/TASK-xxxx-short-title.md`。

### Level C: Governed Task

高影响任务。

满足任一条件即属于治理任务：

- 改变架构；
- 改变公开 API 契约；
- 改变数据模型；
- 引入新框架；
- 引入外部服务；
- 删除公共能力；
- 改变 Agent 治理规则；
- 影响安全、权限、隐私、成本、部署或合规。

记录在：

- `vault/tasks/TASK-xxxx-short-title.md`
- `vault/decisions.md`
- 必要时记录到相关 `vault/details/*`

治理任务通常需要用户确认。

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
- Authority Level
- Allowed Changes
- Forbidden Changes
- Acceptance Criteria
- Required Verification
- Required Memory Updates
- Handoff Requirement

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
6. 未完成事项或风险已记录在任务文件或 `vault/handoff.md`；
7. 没有未说明的高影响变更。

测试通过不等于任务完成。任务完成必须同时满足验收、验证和记忆更新。

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

## 多 Agent 接力

当任务中断、转交或由另一个 Agent 恢复时，必须更新 `vault/handoff.md`。

handoff 至少包含：

- Current Objective
- Completed
- In Progress
- Failed Attempts
- Workspace State
- Known Risks
- Next Best Action
- Files To Read First

如果任务文件已存在，`handoff.md` 应指向任务文件，不重复完整任务记录。
