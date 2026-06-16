# Governance

## Core Rule

Agent 不按身份获得信任，而是按任务契约获得授权。工作只有通过验收门才能关闭。

## Task Levels

### Level A: Simple Task

低风险，通常一次会话完成，一到两个文件，不影响架构、API、依赖或数据模型。记录在 `vault/runtime.md`。

### Level B: Tracked Task

当工作需要追踪、影响两个以上文件、验收标准超过三条、需要设计加验证、可能需要交接或需要审计时使用。记录在 `vault/tasks/TASK-xxxx-short-title.md`。

### Level C: Governed Task

当工作改变架构、公开 API、数据模型、框架、外部服务、安全、隐私、成本、部署或 Agent 治理时使用。记录在任务文件和 `vault/decisions.md`；通常请求用户批准。

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
- Authority level
- Allowed changes
- Requires approval
- Forbidden changes
- Acceptance criteria
- Required verification
- Required memory updates
- Handoff requirement

## Acceptance Gates

关闭工作前：

1. 逐条检查验收标准。
2. 运行并记录必要验证。
3. 适用时同步代码、测试、文档和 vault 记忆。
4. 更新 `vault/runtime.md`。
5. 在 `vault/decisions.md` 记录长期决策。
6. 在任务文件或 `vault/handoff.md` 记录未完成工作或风险。
7. 说明所有高影响变更。

测试通过不等于完成。

## Escalation

需求有歧义、范围扩大、涉及高影响文件、必要检查失败、文档与实现冲突或用户改动与计划冲突时，升级或询问用户。

## Handoff

中断或交接时，更新 `vault/handoff.md`，包含：

- Current objective
- Completed
- In progress
- Failed attempts
- Workspace state
- Known risks
- Next best action
- Files to read first
