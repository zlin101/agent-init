# 90 - Collaboration Profile

## 定位

Collaboration profile 是项目级协作画像，用于沉淀使用者、团队和项目在真实 Agent 协作中形成的稳定偏好。

它不是硬治理规则，也不是多 Agent 编排系统。它回答：

- 使用者倾向怎样下达指令；
- Agent 应该怎样反馈进度；
- 什么情况下应该先问、先计划或直接执行；
- 哪些协作模式已经被验证有效；
- 哪些行为曾被纠正，后续应避免。

默认落库位置：

```text
vault/collaboration.md
```

## 优先级

Collaboration profile 只能补充协议，不能削弱协议。

优先级从高到低：

1. 用户当前明确指令；
2. `AGENTS.md` 和工具专属入口文件；
3. `vault/governance.md`、任务契约和授权等级；
4. `vault/decisions.md` 中的长期决策；
5. `vault/collaboration.md` 中的协作偏好。

当 collaboration profile 与更高优先级规则冲突时，必须忽略 profile 中的对应偏好，并在必要时指出冲突。

## 内容边界

`vault/collaboration.md` 可以记录：

- 交流风格：简短更新、详细分析、先结论后理由等；
- 计划偏好：哪些任务需要先计划，计划应多细；
- 提问偏好：何时先问、何时做稳妥假设；
- 执行偏好：是否偏好小步提交、先审查再改、先跑检查再总结；
- 多 Agent 偏好：接力、并行审查、主从执行或人类最终裁决；
- 反馈模式：用户反复纠正过的行为；
- 已验证工作流：在本项目中证明有效的协作方式。

不应记录：

- 真实密钥、Token、密码或凭据；
- 一次性情绪或偶发偏好；
- 会降低测试、验收、安全、权限、隐私、成本或部署约束的规则；
- 外部账号、个人机器配置或私有服务接入细节；
- 与 `AGENTS.md`、`vault/governance.md` 或任务契约冲突的要求。

## 生成和更新

Collaboration profile 可以在以下时机生成或更新：

- 初始化项目时创建初始模板；
- 完成 Level B 或 Level C 任务后，发现稳定协作偏好；
- 用户明确要求总结协作习惯；
- 多次任务中出现相同反馈、纠正或成功模式；
- 项目阶段变化导致协作节奏变化。

更新时必须遵守：

1. 区分“观察”与“规则”。单次反馈只能作为观察，重复出现或用户确认后才可写成偏好。
2. 记录依据。偏好应尽量说明来源，例如“多次用户要求先结论后细节”。
3. 保持短小。profile 应是可读画像，不是执行日志。
4. 不覆盖硬约束。涉及安全、权限、成本、部署、外部服务或验收规则时，必须升级为治理决策或请求确认。
5. 可撤销。用户纠正后，应更新或删除过时偏好。

## 推荐结构

```md
# Collaboration Profile

## Purpose

## Priority

## Communication Preferences

## Planning Preferences

## Execution Preferences

## Review And Verification Preferences

## Multi-Agent Preferences

## Observed Patterns

## Do Not Infer

## Update Rules
```

## 与其他文件的关系

- `AGENTS.md`：入口硬规则，不能被 profile 覆盖。
- `vault/governance.md`：授权、任务等级、验收门和升级规则，不能被 profile 覆盖。
- `vault/runtime.md`：当前状态和活跃任务，不保存长期协作画像。
- `vault/handoff.md`：最近交接上下文，不保存永久偏好。
- `vault/decisions.md`：长期治理、架构、依赖或工作流决策；profile 中影响治理的内容应升级为 decision。
- `skills/*`：重复稳定的协作流程可以进一步沉淀为 skill。

## 反模式

避免以下做法：

- 把 collaboration profile 当作新的最高优先级规则；
- 把一次对话中的临时要求写成长期偏好；
- 用 profile 规避任务契约、测试、验收或授权等级；
- 在 profile 中保存个人隐私、密钥或外部账号细节；
- 让 profile 变成长执行日志；
- 在没有用户确认的情况下，将高影响偏好升级为默认行为。
