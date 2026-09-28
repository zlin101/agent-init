# D-0008 - Review Pack 方向结论与 R2 处置（2026-09-13）

Status: Active

## Background

Codex 深度使用反馈指出 reviewer 不应只拿到 diff 而缺少契约/证据边界（TASK-0009 的需求源）。TASK-0009 以 TASK-0007/0008 的真实历史 review 快照完成 R0（reviewer 自行组装）与 R1（手工最小 Review Pack）消融：19 个盲测会话（12 有效 / 7 污染作废 / 5 infra 中断留档），预注册→快照→会话→评分全链路 Git DAG 可证，独立 review 四轮，owner 两轮 review。

## Decision

R1 正式判定为 **Inconclusive**（计划 §10.1 封顶：负对照被两处真实 `status` 缺陷失效，control_invalidated 双登记，均经 scorer 与独立 review 复现）。**R2（确定性 review-pack CLI）本周期不实现、不提案**；重开需 owner 另立 Level C 任务。记录性发现（非正式结论）：S1 known-P0/P1 召回 25%、wall-clock 中位数 +24.4%、上下文组装效率真实改善（visible −57.6%、vault opens −46.2%）。owner 指令：不得恢复早期 No-Go 或 "over-determined" 表述。

## Rationale

负对照被真实缺陷失效后，实验无法输出任何方向的终局结论；"核心数字正确"不能替代全部投影与审计记录同步正确（owner review 两轮共 8 项发现的教训）。

## Alternatives

- 维持 No-Go：被 owner 否决，违反冻结封顶规则。
- 立即实现 R2：被否，消融未证明收益且两处 status 缺陷优先（TASK-0010）。

## Impact

Review Pack 不进入 2026.09.x 路线；重开仅经 owner Level C。三项 `status` 缺陷另立 TASK-0010（P1/P1/P2，owner severity 裁定）。实验原始材料与脱敏方案见 `docs/evals/review-pack-2026-09/`。
