# AGENTS.md

## Role

你是本项目的 AI 编码助手。你的目标是在当前任务契约内帮助完成开发、测试、审查、文档和交接。

## Required Reading

执行任何非琐碎任务前，读取：

1. `vault/index.md`
2. `vault/runtime.md`
3. `vault/governance.md`

第一次进入项目时，还要读取：

- `vault/project.md`

接手中断任务时，还要读取：

- `vault/handoff.md`

追踪任务或治理任务读取 `vault/tasks/` 下的活跃任务文件。

## Working Principles

- 先思考再编码。需求有歧义时，指出歧义并选择稳妥路径或请求确认。
- 用满足当前任务的最小修改。
- 修改要聚焦，并能追溯到当前目标。
- 将工作转化为可验证目标，明确验收标准和检查。
- 非琐碎任务不要跳过记忆更新。

## Task Workflow

1. 读取必要上下文。
2. 根据 `vault/governance.md` 判断任务等级和授权等级。
3. 明确范围、不做范围、验收标准和检查。
4. Level B 或 Level C 任务创建或更新任务文件。
5. 做最小必要修改。
6. 行为变化时添加或更新聚焦测试。
7. 运行必要检查。
8. 检查验收门。
9. 更新 `vault/runtime.md`。
10. 长期决策写入 `vault/decisions.md`。
11. 中断或交接时更新 `vault/handoff.md`。

## Forbidden

- 不保存密钥、Token、密码、凭据、私有 URL 或个人账号细节。
- 不静默覆盖用户改动。
- 不伪造验证。
- 未经明确授权，不运行破坏性命令。
- 未经适当授权，不修改安全、隐私、成本、部署、依赖、公开 API 或数据模型。
