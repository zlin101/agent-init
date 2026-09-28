# D-0005 - 试点覆盖计数单一事实源（2026-09-08）

Status: Active

## Background

试点覆盖计数（TASK / lifecycle 转换 / blocked→active / handoff）曾同时独立存在于 runtime 进度行、handoff 条目与 shadow ledger，发生过真实漂移：runtime/ledger 写"3 个真实 TASK"而 checker 报 `current_task_files: 4`，checker 对自然语言计数 0 finding，靠人工复核才发现（ledger canonical K3 行有档）。

## Decision

覆盖事件的唯一事实源是 `vault/details/shadow-run-2026-09.md` 的 append-only 事件行；任何数字汇总只是带"截至日期/commit"的派生快照（derived snapshot），不得作为长期 owner；`vault/runtime.md` 不维护可独立修改的详细数字副本，只保留一句话状态、指向 ledger 的路径与未满足的主要 Gate；`vault/handoff.md` 不保存累计计数（条目中的数字仅为撰写时点快照）。不为此扩展 checker、不新增 schema、不做自动生成器。

## Rationale

消除多 owner 漂移的最小手段是减少 owner 数量，而不是增强校验工具。checker 的自然语言盲区已登记（canonical K3 遗漏栏），按 D-0004 的精神不以扩工具响应单次事件。

## Alternatives

- 增强 checker 解析自然语言计数：被否，违反最小 checker 边界，且计数 schema 化属于过度设计。
- 维持多处计数现状：被否，漂移已实际发生一次。

## Impact

后续 Agent 更新覆盖信息时：先写 ledger 事件行，再（可选）刷新 dated 快照；runtime 只写一句话+指针。在其他文件发现独立维护的计数副本时，按本决策收敛并引用 D-0005。
