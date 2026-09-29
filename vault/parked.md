# Parked

用户挂起事项的冷索引：挂起不遗忘，提及才读取。不进入默认读取路径。

条目生命周期：任务或决定被用户挂起时记入；用户重新提起时升回 `vault/tasks/<task-id>.md`（Draft）或 `vault/runtime.md`。Agent 不得删除条目；清理只出提案，由用户确认。

## Entries

- P-0001 · task · TASK-0019 private storage mode · M0 已验收，M1/M2 已在当前工作区实现，待独立移除 19 个过期 marker 后继续 M3-M5 · 用户明确重新提起 TASK-0019 或 private 模式开发时恢复 · 2026-09-29

类型：task | decision | question。有任务文件的记指针 `TASK-xxxx`，没有的记 2-4 行上下文。

## Budget

- 超过 60 行或 20 条时触发压缩清理提案；过期条目经用户确认后迁入 `vault/details/parked-archive.md`。
