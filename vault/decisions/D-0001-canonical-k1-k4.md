# D-0001 - Canonical K1-K4 实验契约（2026-09-08）

Status: Active

## Background

shadow ledger 初版使用的 K1-K4 标签与 2026-09-04 实施计划第 2 节预注册的假设存在同名异义（初版 K2/K3/K4 与 canonical K2/K3/K4 含义不同），继续混用会使试点结论不可比。

## Decision

以 2026-09-04 计划第 2 节为 canonical K1-K4 唯一定义；初版 K2（runtime 投影）与初版 K4（预算阈值）降为辅助指标 A1/A2，初版 K3（tracked/local）改称 canonical K2；历史观测行不删除、不改写。映射记录见 `vault/details/shadow-run-2026-09.md` 顶部 2026-09-08 reconciliation 块。

## Rationale

跨项目证据要求（两个真实项目、至少 10 次状态变化）挂在 canonical 假设上；不消除同名异义，K3/K4 的证据永远无法积累，kill criterion 无法评估。

## Alternatives

- 保留初版标签并改写计划定义：被否，预注册指标不容事后修改。
- 删除初版表格重建：被否，违反 append-only 与"不改写历史观测"。

## Impact

后续 Agent 记录 shadow 观测时必须按 canonical 定义选表；引用"K1-K4"时须落到具体计划段落，不得只写缩写。
