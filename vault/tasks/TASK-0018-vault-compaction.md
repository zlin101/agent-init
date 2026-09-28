# TASK-0018 - Vault 热文件结构压缩

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0018",
  "level": "B",
  "authority_level": 2,
  "lifecycle": "accepted"
}
-->

## Objective

把超过预算线的 Vault 热文件恢复为适合冷启动的最小状态，同时保留完整决策正文和可追溯历史。

## Scope

### In Scope

- 测量 `runtime.md`、`decisions.md`、`handoff.md` 与 `parked.md`。
- 将 `decisions.md` 首次索引化，逐字迁移 D-0001 至 D-0011 正文并补齐索引。
- 从当前权威事实重写 `runtime.md`，移除已关闭任务投影、过期进展和过期下一步。
- 验证结构、引用、预算、全量测试和 Vault checker。

### Out of Scope

- 改变任何决策状态、含义或任务结论。
- 归档任务文件、修改产品代码、发布、tag、push 或跨仓库操作。
- 修改 owner 排除的 `vault/.agent-init.json` 与 `docs/engineering/code-comments.md`。

## Context Required

- `AGENTS.md`
- `vault/index.md`
- `vault/runtime.md`
- `vault/governance.md`
- `vault/handoff.md`
- `init/protocol/15-vault-compaction.md`

## Capability Tags

- documentation
- vault-maintenance
- testing

## Authority

Allowed:

- 在 owner 要求执行压缩后，对超预算热文件做非语义结构整理。
- 新建决策正文文件并更新 Vault 当前状态。

Requires Approval:

- 任何决策语义或状态变更。
- commit、push、tag 或发布。

Forbidden:

- 删除历史决策正文或伪造验证。
- 触碰 owner 排除文件或 Orion。

## Acceptance Criteria

- [x] `decisions.md` 是 D-0001 至 D-0013 的纯索引，正文文件一一对应且内容完整。
- [x] `runtime.md` 只保留当前阶段、活跃任务、约束、风险、检查与最多 10 条近期里程碑。
- [x] 不改变任何决策状态或语义，不移动未触发预算线的任务历史。
- [x] 压缩后文件在默认预算内，Vault 状态投影无新增错误。
- [x] 全量测试、Skill 同步与 whitespace 检查通过。

## Verification

Required:

- `wc -l vault/runtime.md vault/decisions.md vault/handoff.md vault/parked.md`
- 决策索引与正文文件 D-ID 一一对应检查。
- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`
- `python3 scripts/sync-skills.py --check`
- `python3 scripts/trellium.py status . --format json`
- `python3 scripts/trellium.py check . --format json`
- `git diff --check`

Completed:

- runtime 67 行、decisions 21 行、handoff 10 行、parked 15 行，均在默认预算内。
- D-0001 至 D-0011 拆分正文与原文件内容等价；D-0001 至 D-0013 索引和正文文件一一对应。
- 177/177 tests passed；Skill snapshots in sync；`git diff --check` passed。
- status/check 无新增结构或投影 error；只保留两个 owner 排除文件的既有 error，以及提交前 TASK storage warning。

## Execution Record

### 2026-09-28 - Agent: Codex

Context read:

- 项目必读 Vault、任务治理规则和 Vault 压缩协议。

Changes made:

- 将 `decisions.md` 收缩为 13 条纯索引，把 D-0001 至 D-0011 正文分别迁入 `vault/decisions/`；D-0012/D-0013 保持原文件。
- 从权威任务状态重写 `runtime.md`，移除 17 个已关闭任务投影、过期进展、风险和 Orion 下一步。
- `handoff.md`、`parked.md` 和任务历史未触发各自阈值，保持不变。

Checks run:

- 压缩前测量：runtime 153 行、decisions 284 行、handoff 10 行、parked 15 行。
- 决策正文重组 diff：通过；仅标题层级适配独立文件。
- 决策索引/正文 ID 集合：13/13，一一对应。
- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`：177/177 passed。
- `python3 scripts/sync-skills.py --check`：in sync。
- `git diff --check`：passed。
- `status` / `check`：无本任务新增错误；既有 2 error 来自 owner 排除文件，提交前 1 warning 来自 tracked TASK-0018 尚未进入 HEAD。

Review and reflection:

- 当前只有 runtime 与 decisions 触发预算线；task 文件数量未触发归档条件。
- owner 排除的 stamp 使工作区 Vault 非 clean，但其变更早于本任务且不会被读取、编辑或纳入本任务 diff。
- 首次自动拆分未落盘，预验证及时发现后修正；随后用原始正文重组 diff 验证无内容丢失。

Risks:

- 当前压缩改动尚未提交，tracked storage checker 会继续报告 TASK-0018 pending；提交权限未由本任务推定。

Next action:

- Owner 于 2026-09-28 接受 TASK-0018 并授权 Vault-only 提交；不纳入 owner 排除文件，不 push。

### 2026-09-28 - Agent: Codex — owner acceptance

- Owner 明确要求完成 TASK-0018 的接受与 Vault-only 提交。
- 生命周期 `ready_for_review → accepted`；提交范围仅限本任务的 runtime、决策索引/正文和任务文件。
- `vault/.agent-init.json` 与 `docs/engineering/` 继续排除；push 未授权。

## Memory Updates

- `vault/runtime.md`
- `vault/decisions.md`
- Durable knowledge disposition: not_applicable（tracked task）

## Handoff Requirement

中断时记录已迁移的决策 ID、剩余 ID、校验结果和未解决差异；不要把 owner 排除文件纳入压缩提交。
