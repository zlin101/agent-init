# D-0007 - 只读 status 摘要命令（2026-09-09）

Status: Active

## Background

owner 在 09.3–09.4 期间反复让 Agent 重读 runtime/TASK 手工汇总进度（A+B 级证据）；2026.09.5 审计将其选为唯一开发候选（TASK-0008），实现前完成 S0/S1 双臂盲测（原始记录存 `vault/details/status-blind-test-2026-09/`），owner 两轮 review 后验收。

## Decision

`trellium.py status <target>`（`--format json` 可选）作为只读 owner 状态摘要：lifecycle/authority 只来自有效的 trellium-task-state 块；closed 只进计数；drift 降级 unresolved、不裁决；unresolved 原因按 finding phase（task-state/runtime-projection）结构化推导，不伪造码；文本与 JSON v1 同源。它是状态摘要，不是 approval inbox。

## Rationale

复用 check 的单一事实源而不新增状态 owner；盲测显示 S1 的正确性优势来自内建 open/closed 分类学与 fail-closed 投影抑制，而非仅 bytes 更小。

## Alternatives

- 持久 inbox/approvals 文件：被否，会形成第二状态 owner。
- 把 owner 视图并入 check：被否，会污染 check 的稳定 schema 与退出码。
- runtime 自动生成器：被否，写放大且制造第二事实源。

## Impact

后续把 status 扩展为 inbox/approval 推断、增加字段或改变 JSON v1 形状，需新决策；unresolved 原因推导按 phase 跟随 checker 演进，无需维护代码清单；引用本命令边界时以本决策与 TASK-0008 契约为准。
