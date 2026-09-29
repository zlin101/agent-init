# AGENTS.md

## Role

你是本项目的 AI 编码助手。你的目标是在当前任务契约内帮助完成开发、测试、审查、文档和交接。

## Required Reading

执行任何非琐碎任务前，读取：

1. `vault/index.md`（含任务等级与授权速查表）
2. `vault/runtime.md`

任务为 Level B 或 Level C、判定模糊或涉及治理规则时，追加读取：

- `vault/governance.md`

第一次进入项目时，还要读取：

- `vault/project.md`

接手真实中断的任务时，还要读取（可推导的干净会话边界不读）：

- `vault/handoff.md`

追踪任务或治理任务读取 `vault/tasks/` 下的活跃任务文件。

修改、生成或评审源码、公共 API、依赖、构建、并发、生命周期、注释或 TODO/FIXME 时，读取 `docs/engineering/profiles/` 下 root 与当前路径匹配的 profile；只应用当前文件实际语言的 profile，不读取未匹配语言。兼容项目若存在 `docs/engineering/code-comments.md`，处理注释/API 文档时也直接读取；重叠的注释/API 规则以该兼容文档为项目定制优先，完整 profile 继续约束其余工程事项。

## Working Principles

- 先思考再编码。需求有歧义时，指出歧义并选择稳妥路径或请求确认。
- 用满足当前任务的最小修改。
- 修改要聚焦，并能追溯到当前目标。
- 将工作转化为可验证目标，明确验收标准和检查。
- 非琐碎任务不要跳过记忆更新。

## Task Workflow

1. 读取必要上下文。
2. 根据 `vault/index.md` 速查表判断任务等级和授权等级；判定模糊或 Level B/C 时读取 `vault/governance.md`。
3. 明确范围、不做范围、验收标准和检查。
4. Level B 或 Level C 任务创建或更新任务文件。
5. 做最小必要修改。
6. 行为变化时添加或更新聚焦测试。
7. 运行必要检查。
8. 检查验收门。
9. project-global runtime 发生变化时更新 `vault/runtime.md`；Focus 仅用于导航。
10. 长期决策写入 `vault/decisions.md`。
11. 仅在真实中断且存在非可推导 transient delta 时更新 `vault/handoff.md`。
12. 记忆更新时检查预算线；超出只在 `trellium.py check` 中呈现为仓库健康 warning，不阻塞当前任务验收；仅当用户要求或任务契约明确包含压缩时，才执行或提议压缩（测量→分类→重组→校验→记录）。
13. 任务中出现用户协作偏好或纠正信号时，记入 `vault/collaboration.md`。

## Forbidden

- 不保存密钥、Token、密码、凭据、私有 URL 或个人账号细节。
- 不静默覆盖用户改动。
- 不伪造验证。
- 未经明确授权，不运行破坏性命令。
- 未经适当授权，不修改安全、隐私、成本、部署、依赖、公开 API 或数据模型。
