---
name: agent-task
description: 用于执行需要上下文读取、限定范围修改、验证、任务记录或 vault 记忆更新的非琐碎项目任务。
---

# Agent Task Workflow

## Steps

1. 读取 `AGENTS.md`、`vault/index.md`、`vault/runtime.md` 和 `vault/governance.md`。
2. 按 `vault/index.md` 读取任务特定上下文。
3. 将任务归类为 Level A、Level B 或 Level C。
4. 判断授权等级和是否需要用户确认。
5. 明确目标、范围、不做范围、验收标准和检查。
6. Level B 或 Level C 创建或更新任务文件。
7. 做最小必要修改。
8. 行为变化时添加或更新聚焦测试。
9. 通过任务文件和 `vault/handoff.md` 让长任务可恢复。
10. 运行必要检查。
11. 检查验收门；测试通过不等于完成。
12. 更新 `vault/runtime.md`。
13. 长期决策写入 `vault/decisions.md`。

## Constraints

- 不引入无关依赖或框架。
- 不保存密钥。
- 单元测试不依赖真实外部服务。
- 不静默覆盖用户改动。
- 涉及架构、公开 API、数据模型、安全、隐私、成本、部署、依赖或 Agent 治理时升级。

## Review Before Completion

- 逐条确认验收标准。
- 确认验证输出。
- 确认 vault 记忆已更新。
- 确认没有隐藏高影响变更。
