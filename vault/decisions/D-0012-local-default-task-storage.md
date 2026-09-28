# D-0012 - 首次接入默认 local TASK storage

Status: Active

Date: 2026-09-28

## Background

完整 TASK、review 台账与 archive 属于高频工作日志；默认 tracked 会把过程材料带入业务仓库。协作入口、项目事实、治理、决策、handoff、模板、profile 与安装版本戳仍需要跨 clone 持久化。

## Decision

首次使用 Skill 时由 Agent 询问 owner 选择 storage，并推荐 `local`；owner 未指定时按 local 执行。local 仅通过 `vault/tasks/.gitignore` 的窄规则忽略 `TASK-*.md`、`*-review.md` 与 `archive/`，其余协作核心仍 tracked。需要共享完整任务流水时选择 `tracked`。这是一条 Agent-native 工作流，不新增 CLI 参数；重复接入与 upgrade 保持现有 policy，任何 tracked/local 迁移都需 owner 单独评审，工具不自动 untrack。

## Rationale

这将临时过程记录留在本地，同时保留项目长期真相与协作规则的可恢复性。窄范围嵌套 ignore 避免污染项目根规则，也防止误伤 `vault/tasks/README.md` 等 durable 文件。

## Impact

新接入项目的默认行为变化为 local；现有项目不变。local 任务关闭前必须完成 Durable knowledge disposition，长期结论蒸馏到 canonical Vault 文件。
