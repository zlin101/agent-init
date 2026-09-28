# TASK-0001 - Trellium 自托管试点与 shadow 取证

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0001",
  "level": "B",
  "authority_level": 2,
  "lifecycle": "accepted"
}
-->

## Objective

把 Trellium 仓库自身作为第一个 tracked 模式自托管试点，在真实开发中积累 K1-K4 承重假设的 shadow 证据，并按期产出复盘，决定后续周期是否继续、调整或回退。

## Scope

### In Scope

- `vault/`、`AGENTS.md`、`skills/agent-task/SKILL.md` 的接入与日常维护。
- `vault/details/shadow-run-2026-09.md` 观测记录的持续填写。
- 每次交接与合并前运行 `python3 scripts/trellium.py check . --format json` 并留档结论。
- 试点结束后的简短复盘（五问）。

### Out of Scope

- 协议模板、`scripts/trellium.py`、Skill 包的任何功能改动（需要另立任务，且属 Level C）。
- context compiler、evidence freshness、runtime 自动生成、fact types 等后续能力。
- 对其他项目的接入。

## Context Required

- `AGENTS.md`
- `vault/index.md`
- `vault/runtime.md`
- `vault/governance.md`
- `docs/superpowers/plans/2026-09-04-agent-native-vault-check-plan.md`（K1-K4 假设与重新进入条件）

## Capability Tags

- documentation
- testing
- review

## Authority

Allowed:

- 创建与更新 `vault/` 内文件；
- 以小 diff 方式更新 runtime/handoff 投影；
- 在观测记录中追加事实条目。

Requires Approval:

- 修改 `.gitignore` 的忽略策略（已获用户授权一次：解除 `AGENTS.md` 与 `vault/` 忽略）；
- 任何对协议模板或 checker 的修改；
- 删除或改写历史观测条目。

Forbidden:

- 为凑指标伪造观测数据；
- 把 check 的 warning 静默忽略不记录；
- 批量改写历史 TASK 文件。

## Acceptance Criteria

- [x] 试点累计覆盖 5 个真实 TASK（不含纯演示任务）。——owner 于 2026-09-28 批准闭环；ledger 按 D-0005 口径已覆盖 17 个真实 TASK，远超门槛。
- [x] 试点累计 6 次 lifecycle 转换，全部有对应观测条目。——证据：shadow ledger 初版 K1 表 9 行事件观测（含 TASK-0005 自身 draft→active），每行含修改位置数与人工修正数。
- [x] 试点累计 2 次跨 Agent handoff，每次交接前 `check --format json` 已运行且结论留档。——证据：事件①09-04 adopt 会话→Codex（TASK-0001 handoff 条目 + check 台账「adopt 后基线」0/0）；事件②09-04 Codex→09-08 GLM（TASK-0002 handoff 条目已按压缩规则并入任务文件 + check 台账「TASK-0002 发布前门禁」0/0）。Agent 署名见各任务文件 Execution Record。
- [x] 出现过至少 1 次 blocked → active 转换，阻塞原因与解除条件有记录。——证据：TASK-0002 blocked→active（ledger K1 行；阻塞原因"环境无 gh/无凭据"，解除条件"Release 发布且 latest 解析正确"，见 TASK-0002 执行记录）。
- [x] K1-K4 四个实验按 canonical 契约填写观测：指标定义唯一来源为 `docs/superpowers/plans/2026-09-04-agent-native-vault-check-plan.md` 第 2 节；初版标签到 canonical/辅助指标（A1/A2）的映射以 `vault/details/shadow-run-2026-09.md` 顶部 2026-09-08 `Experiment contract reconciliation` 为准；不追加新指标。——证据：canonical K1（6 行）、canonical K2（初版 K3 表）、canonical K3（2 行）、canonical K4（2 行）均已有观测。
- [x] 上方 coverage gate（5 TASK / 6 转换 / 2 handoff / 1 blocked→active）仅为本仓库 self-hosting 覆盖门槛，不替代 canonical K1-K4 要求的跨项目证据；Orion 提供了第二真实项目的定性样本，未完成部分不外推为已证明结论。
- [x] 复盘五问已于 2026-09-28 完成并形成关闭结论。

## Verification

Required:

- `python3 scripts/trellium.py check . --format json`（每次交接与合并前，退出码必须为 0）。
- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`（涉及脚本提交时）。

Completed:

- 2026-09-04: adopt + check 退出 0（0 error / 0 warning）；`.gitignore` 解除忽略后任务文件可被 tracked。

## Execution Record

### 2026-09-04 - Agent: Claude (GLM)

Context read:

- `AGENTS.md`、`vault/index.md`、`vault/runtime.md`、`vault/governance.md`
- 用户试点指令（验收指标与四实验表）

Changes made:

- `.gitignore` 解除 `AGENTS.md` 与 `vault/` 忽略（用户已授权）。
- `trellium.py adopt .` 接入本仓库（tracked 模式）。
- 创建本任务文件与 `vault/details/shadow-run-2026-09.md` 观测记录。

Checks run:

- `trellium.py check . --format json` → 0 error / 0 warning（adopt 后基线）。

Review and reflection:

- 首个生命周期转换：draft → active（接入完成，试点开始执行）。

Risks:

- 单人开发可能长期只有 TASK-0001，5 个真实 TASK 的覆盖需要真实工作自然产生，不预造。

Next action:

- 由下一个会话/Agent 接手：按 runtime 的下一步推进，出现阻塞时记录 blocked → active 样本。

### 2026-09-09 - Agent: Codex

Context read:

- `AGENTS.md`、`vault/index.md`、`vault/runtime.md`、`vault/governance.md`、`vault/handoff.md`、本任务文件。
- 已安装 `trellium-zh` 的升级流程、模板指南与 2026.09.4 migration playbook。

Changes made:

- 使用正式安装器将 `trellium-zh 2026.09.4` 安装到 Codex 与 Claude Code，并删除旧 Codex `agent-native-init-zh` Skill。
- 将本项目 Vault 从 2026.09.3 升级到 2026.09.4；安全刷新 `skills/agent-task/SKILL.md`，并按 owner 逐项确认合并 `vault/index.md`。
- 保留本项目“暂不配置预算阈值”定制；仅将 local 关闭规则精确限定为 `task_storage=local`。tracked 项目无需执行 local TASK 数据迁移。

Checks run:

- `trellium.py diff .` → installed 2026.09.4 == available 2026.09.4；协议文件全部 in sync / absorbed。
- `trellium.py check . --format json` → 0 error / 0 warning。
- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` → 106/106 OK。
- `python3 scripts/sync-skills.py --check` → 中英两套 snapshot in sync；`git diff --check` 通过。

Review and reflection:

- 升级仅触及协作层；未替换 runtime、tasks、decisions、handoff 等项目事实，未修改业务源码、依赖、测试或 CI。
- 2026.09.4 migration 的 local 数据动作对当前 `tracked` 策略不适用，未做批量回填。

### 2026-09-28 - Agent: Codex — 五问复盘与试点关闭

Owner decision:

- 自托管试点不再长期保持 active；补齐五问后关闭，未完成的新问题改由独立任务承载。

Five-question retrospective:

1. **check 真正捕获了什么**：结构化状态块/runtime 漂移、closed local 行残留、tracked/local Git 状态错误、核心未进入 Git HEAD、stamp/policy/state 非法以及 local ignore 越界都产生过可执行结果；其中 Orion 的 `TASK_RUNTIME_CLOSED_LOCAL` 与 TASK-0013 的 fresh-clone 假健康复现是最有价值的真实样本。
2. **哪些字段没人用**：`current_slice` 与细粒度 `gates` 只在少数复杂任务出现，普通任务长期为空；预算阈值在本仓库一直未配置。它们可选是正确的，不应升级为每个任务的强制填写负担。
3. **投影维护成本**：状态块到 runtime 的双写在正常转换中成本低，但长周期内确实出现漏记 lifecycle 事件、自然语言计数过期与 closed-local runtime 残留；checker/status 能捕获结构化漂移，却不能维护 prose 汇总。因此 runtime 应保持短指针，不再承载累计统计。
4. **哪些规则需频繁解释**：local 只包含 TASK/review/archive、协作核心仍 tracked；runtime 只是投影且不授予 Authority；`accepted` 必须由 owner 决定；local 任务关闭前要蒸馏长期结论。这些边界已分别固化到 D-0006、D-0010 与当前 Skill/协议。
5. **哪些预算只是理论值**：runtime/decisions/tasks 的初始化数字未在本仓库 policy 启用，实际文件已经超过模板建议值而 checker 只测量、不报阈值错误。当前真实问题是默认读取成本与历史堆积，应做一次内容压缩，而不是倒推未经验证的硬阈值。

Conclusion:

- 试点证明最小状态层与只读 checker 有实际价值，同时暴露 runtime prose、跨文件累计计数和长期 active 试点的维护成本。canonical K2 的 Orion 样本仍为 Partial，不伪装成完整证明；这不再阻塞试点关闭。后续产品缺陷与压缩分别立独立任务，不继续把 TASK-0001 当作常驻背景任务。

Checks run:

- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` → 177/177 passed。
- `python3 scripts/sync-skills.py --check` → 双语 snapshot in sync；`git diff --check` passed。
- `status` → active 0、ready_for_review 1、unresolved 0；TASK-0001 accepted、TASK-0004 superseded 投影一致。
- self-check → 2 error / 1 warning，均为已知未提交边界：owner 排除的 `docs/engineering/code-comments.md` 与 `vault/.agent-init.json`，以及当前 tracked TASK-0017 未提交；不伪造为 0/0。

## Memory Updates

- `vault/runtime.md`（每次状态变化同步投影行）
- `vault/details/shadow-run-2026-09.md`（观测条目）
- `vault/handoff.md`（每次中断或交接）
