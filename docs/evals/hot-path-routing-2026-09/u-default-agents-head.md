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

修改或评审源码、公开 API、依赖、构建、并发或生命周期行为时，读取 `docs/engineering/profiles/` 下 root 与当前路径匹配的 profile；只应用当前文件实际语言的 profile，不读取未匹配语言。纯注释/文档工作——注释、Doc Comment、docstring、TODO/FIXME、directive 排布——只读 Comment/API Documentation Policy（`docs/engineering/code-comments.md`），它是该表达规范的唯一 owner。公开 API 变化，或行为与注释同时修改时，profile 与 Comment/API Documentation Policy 并读：表达规范以 Comment Policy 为准，API 行为、安全、错误与兼容性仍由完整 profile 约束。
