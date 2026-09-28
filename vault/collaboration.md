# Collaboration Profile

## Purpose

记录稳定协作偏好和观察模式。本文件是软画像，不能覆盖当前用户指令、Agent 入口规则、治理、任务契约、决策、安全、测试、权限、成本、隐私或部署约束。

## Priority

1. 当前用户指令。
2. Agent 入口文件。
3. `vault/governance.md`、任务契约和授权等级。
4. `vault/decisions.md`。
5. 本协作画像。

## Communication Preferences

- 替换为稳定交流偏好。

## Planning Preferences

- 规划 Vault 演进时，以长期深度使用反馈作为主要问题证据；短期小样本用于校准实施顺序，不能未经对照就反证长期结构性摩擦。
- 产品主线是根据 Codex 真实使用反馈做功能升级；自托管取证、第二项目和治理文档是验证手段，不得取代功能交付。
- 优化方案在交付实现前显式反思并做单变量消融，预注册停止条件；能由更小流程解决时不升级为 schema、CLI 或服务。
- 根据任务规模选择交付载体：边界清晰、单会话可完成的小任务给可直接执行的提示词；跨里程碑、多文件、治理/API、消融实验或多轮审查任务产出正式方案文档，再交实施 Agent 执行。
- local TASK 是有意不进入仓库的私有、可丢弃工作日志；只把会约束未来实现的最小结论蒸馏到 canonical Vault 文件，不以跨 clone 保存完整 TASK 流水为目标。
- 对只在特定技术栈或任务类型生效的长规则，优先用 AGENTS 一行机械触发、直接路由到项目工程文档，以可控文件复杂度换取按需 Token；不通过 Vault 二跳，也不把工程规范默认收进 Vault。

## Execution Preferences

- 发布保持低调：Release 标题使用版本号，正文默认留空；除非 owner 明确要求，不生成宣传性描述。

## Review And Verification Preferences

- 替换为稳定审查和验证偏好。

## Observed Patterns

- 替换为重复观察。不要把一次性反馈提升为硬规则。

## Do Not Infer

- 不要推断允许跳过验证。
- 不要推断允许绕过安全或授权规则。
- 不要保存密钥、私有账号或个人服务细节。

## Update Rules

- 重复反馈或用户明确要求后再添加观察。
- 保持本文件短小。
- 影响治理的偏好移到 `vault/decisions.md` 或任务文件。
