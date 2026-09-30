# TASK-0019 - Private storage mode

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0019",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "accepted",
  "current_slice": "accepted-after-phase-6-closure"
}
-->

## Objective

在不削弱既有 durability、安全和 Git 授权边界的前提下，为首次接入增加 `private` 模式：所有 Trellium managed material 只存在于当前 clone，不进入 Git index、HEAD 或远端。

权威实施计划：`docs/superpowers/plans/2026-09-28-private-storage-mode-plan.md`。

## Scope

### In Scope

- 用户层 tracked/local/private 三模式，默认 local。
- policy schema v2 `storage_mode` 与 legacy v1 normalization。
- private 反向 Git privacy Gate、target-scoped canonical `.git/info/exclude` block、Agent-native 契约和 tracked-carrier preflight。
- private TASK lifecycle、adopt completion、diff/upgrade/profile 与双语分发语义。
- 预注册 P0/P1/P2 消融、red-first fixtures、安全回归和独立 review。

### Out of Scope

- CLI `--storage` / `--private` 参数或交互式脚本询问。
- 自动修改 Git index、`git rm --cached`、commit、push、tag、Release 或 history rewrite。
- `skip-worktree`、`assume-unchanged`、Git hook、全局 excludesfile 或修改项目根 `.gitignore`。
- 自动迁移既有 tracked/local 项目，或支持修改已有 tracked `AGENTS.md` 后仍声称严格 private。
- 加密、操作系统访问控制、备份隔离或绝对防泄漏承诺。

## Context Required

- `AGENTS.md`
- `vault/index.md`
- `vault/runtime.md`
- `vault/governance.md`
- `vault/decisions/D-0010-git-durability-gate.md`
- `vault/decisions/D-0012-local-default-task-storage.md`
- `vault/tasks/TASK-0013-adoption-durability.md`
- `vault/tasks/TASK-0017-local-default-adoption.md`
- `docs/superpowers/plans/2026-09-28-private-storage-mode-plan.md`
- `scripts/trellium.py`
- `scripts/test_trellium.py`

## Capability Tags

- agent-governance
- privacy
- git-boundary
- adoption
- upgrade
- security
- testing

## Authority

Allowed:

- Owner 已批准输出最终方案并交 PI 开发。
- 按冻结计划完成 M0-M4 的代码、测试、协议、文档、版本与 snapshot 修改。
- 使用临时本地 Git fixture 做确定性验证；单元测试不得调用真实外部服务。

Requires Approval:

- 改变冻结 policy 结构、private managed scope 或默认 local。
- 自动 Git index 写入、存量迁移、tracked AGENTS 兼容绕行、history rewrite。
- accepted、commit、push、tag 或发布。

Forbidden:

- 通过放松 TASK-0013 durability/managed-path/link/path/fallback 安全 Gate 获得绿色结果。
- 使用 `skip-worktree`、`assume-unchanged`、Git hook或全局 Git 配置。
- 把 private 描述为加密、历史清除或绝对防上传。
- 触碰 owner 排除的 `vault/.agent-init.json` 与 `docs/engineering/`。

## Acceptance Criteria

- [x] M0 契约和 P0/P1 red fixtures 先于产品实现提交，tracked/local golden 冻结。
- [x] schema v1 tracked/local 与 schema v2 三模式严格解析并规范化；既有 v1 不自动改写。
- [x] private clean fixture 达到 check 0/0；全部 managed material untracked/staged-free 且 ignored。
- [x] canonical exclude block 通过 `git rev-parse --git-path info/exclude` 定位，target identity 唯一，patterns anchored 且不越 approved scope。
- [x] tracked/staged/forced-add、缺 ignore、overreach、Git failure 全部 fail-closed。
- [x] tracked AGENTS/private 冲突在任何写入前失败；不使用隐藏 index 状态绕过。
- [x] private 使用 local TASK lifecycle，但文案不声称跨 clone durable。
- [x] adopt/diff/upgrade/profile 与 managed-file allowlist、dirfd/fallback、link/path 安全边界无回归。
- [x] 不新增 CLI storage 参数，不自动修改 index/commit/push/history。
- [x] 双语协议、Skills、MIGRATIONS 与 snapshots 同步；canonical 三模式合同收齐（private 语义与 preflight 接线）。
- [x] README 与 VERSION 同步保留在本任务验收内（owner 选定方案 b）：README 落在收敛计划 Phase 3（TASK-0024 安装契约，已验收），VERSION 落在 Phase 6（2026.09.10 release-prep 已提交、tag 已推送）；两项完成并验收，TASK-0019 进入最终 accepted。
- [x] 全量测试、check、sync、whitespace 和独立 review 通过，无 open P0/P1/P2。（自测全绿；独立 review 三轮完成——round 3 owner APPROVE，无 open P0/P1/P2）
- [x] 任务停在 `ready_for_review`，由 owner 决定 accepted 和发布。

## Verification

Required:

- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`
- `python3 scripts/sync-skills.py --check`
- `python3 scripts/trellium.py check . --format json`
- `python3 scripts/trellium.py status . --format json`
- `git diff --check`
- 临时 Git fixtures：policy v1/v2、private clean、forced-add、tracked carrier、missing/overbroad exclude、monorepo、no-HEAD、non-Git、profile、upgrade proposal、安全路径矩阵。

Completed:

- Plan-only：初步方案反思、A0-A3/entry carrier 消融和 R1-R5 strategy red-team 已完成；尚未修改产品代码。
- M0（2026-09-28 至 2026-09-29，PI/Codex）：`scripts/test_trellium.py` 新增 `PrivateStorageModeTest`；三轮整改、第四轮复审后以 6 绿 + 24 红测通过 M0 验收（marker 完整性、反向 privacy Gate、preflight 三合同独立冻结、profile 精确忽略、check/status golden）；Kill Gate 证据落盘 `docs/evals/private-mode-kill-gates-2026-09/`，owner 已授权提交。

## Execution Record

### 2026-09-29 - Agent: Codex — owner-directed pause

- Owner instructed that TASK-0019 be temporarily parked; no further implementation, marker removal, review, or release work is authorized until the owner explicitly resumes it.
- Lifecycle remains `active` because the project schema has no `paused` value and the work is unfinished; `vault/parked.md` is the canonical pause signal, while `current_slice` records the resumable boundary.
- Exact resume point: retain PI's completed M1/M2 work; first remove the 19 stale `expectedFailure` markers in a dedicated TASK-0019 slice, then implement M3-M5. The three M3 preflight expected failures remain intentional.
- No product code or tests were changed as part of parking the task.

### 2026-09-29 - Agent: Codex — M0 accepted

- Owner 第四轮复审通过；M0 无 open P0/P1/P2，获准提交但 TASK-0019 整体仍保持 `active`。
- 独立复核：类内 30 tests（6 green + 24 expected failures）；剥离 marker 后 21 assertion failures + 3 个预期接口缺失 AttributeErrors，0 unexpected successes；全量 207/207 OK。
- `sync-skills --check` 与 `git diff --check` 通过；checker 保持 2 个 owner 排除 error + 1 个提交前 TASK warning；产品 `scripts/trellium.py` 零改动。
- 下一步进入 M1 policy v2 normalization，并在同一实现变更中移除对应三个 expectedFailure marker。

### 2026-09-28 - Agent: PI — M0 review round 1 rework (REQUEST_CHANGES)

Context read:

- Owner 验收结论（两项 P1 阻塞、两项 P2 收口）；`docs/evals/adoption-durability-2026-09/` 证据目录惯例；现有 `PrivateStorageModeTest` 与 checker status 实现。

Changes made:

- P1-1（Kill Gate 1 证据）：重建同规格 fixture 并重跑两个探针，完整留证到 `docs/evals/private-mode-kill-gates-2026-09/`：`protocol.md`（方法与脱敏说明）、`prompts.md`（中性 prompt 逐字）、`results.md`（判定矩阵）、`runs/` 下 Codex（codex-cli 0.158.0，exit 0）、Claude Code（2.1.263，exit 0）原始 stdout/stderr、git fixture 证明（status 空、ls-files 0、check-ignore 命中 `.git/info/exclude`）与 Gate 2 forced-add 探针记录（git 2.43.0）。两 agent 本轮再次 PASS；Claude Code 引用 `AGENTS.md:5/:14` 行号，发现证据更硬。
- P1-2（隐私安全边界红测补全，新增 9 例 expectedFailure）：duplicate/unterminated/crossed marker block → `PRIVATE_STORAGE_UNCONFIGURED`；marker target identity 不匹配 → `UNCONFIGURED`；非 anchored pattern（`vault/`）与 monorepo 越 target pattern（`/packages/other/`）→ `OVERREACH`；tracked AGENTS carrier → `PRIVATE_STORAGE_TRACKED` 且用 worktree/index/HEAD/exclude 四重 fingerprint 断言检测零写入；profile adopt（`--profile go-backend=services/api`）的 stamp 额外 managed paths（`docs/engineering/code-comments.md`、`docs/engineering/profiles/go-backend.md`）必须被 exact pattern 覆盖（缺失 → `UNCONFIGURED`，补齐 → 0/0）且纳入 forced-add 检测（`add -f` → `TRACKED`）。helper 扩展：`private_block_lines`（prefix/raw_patterns）、`stamp_extra_patterns`（从 stamp 派生 exact 覆盖）、`private_repo(*adopt_extra)`、`private_git_fingerprint`。
- P2-1（golden 扩展）：新增 check/status 健康双 golden（status exit 0、findings/tasks/summary 全空桶）与单一异常 golden（accepted 未 tracked → check 恰好 1 个 `TASK_STORAGE_MISMATCH` error；status exit 2、同 finding、closed=1 且不产生 unresolved 桶）。
- P2-2：`runtime.md` Recent Changes 压回 10 条（移除最旧 2026-09-20 条目，TASK-0013/0014/0015 结论已在任务文件与 decisions 冷历史中）；TASK-0019 M0 两轮信息合并为单行，不新增条目。

Checks run:

- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` — 204/204 OK（16→27 类内测试：6 绿 + 21 expected failures 为设计状态）。
- `python3 scripts/sync-skills.py --check` — in sync。
- `python3 scripts/trellium.py check . --format json` — 2 error / 1 warning 与基线一致；runtime measurement `recent_entries: 10`。
- `git diff --check` — passed。
- 产品 `scripts/trellium.py` 零改动（与首轮一致）。

Review and reflection:

- 红测新增的 marker-integrity 断言只锁 finding code/severity，不锁 message 文案，避免过度约束 M2 实现自由度；profile 覆盖缺失例外地断言 message/path 提及具体路径，因为 owner 要求“精确忽略”必须可诊断。
- `private_git_fingerprint` 刻意排除 `.git/` 内部文件字节比较（git 会机会性刷新 index stat cache），逻辑 index 状态由 `ls-files -s` + `status --porcelain` 覆盖，避免 flaky。
- P0 第二段（部分覆盖 → UNCOMMITTED）与首轮结论一致，未改动。

Risks:

- 21 个红测锁定的 M2 合同面变大；若实现期将 marker-integrity 违规拆分为多个 finding code，需同步改对应红测断言（属预期成本，不放松合同）。
- Kill Gate 1 证据为 2026-09-28 时点行为；agent 版本升级后需按 `protocol.md` 重跑，本目录只保留最近一轮。

Next action:

- Owner 复审 M0（两项 P1 已补齐、两项 P2 已收口）；通过后授权提交，再进入 M1。

### 2026-09-28 - Agent: PI — M0 review round 2 rework (REQUEST_CHANGES)

Context read:

- Owner 第二轮验收结论（一项 P1：preflight 零写入未冻结；两组 P2：Gate 2 表述错误、脱敏/陈旧计数）；现有 preflight/carrier 测试与证据文件。

Changes made:

- P1（preflight 合同）：新增 `test_private_preflight_rejects_tracked_carrier_without_writes`（第 22 例红测）。冻结 M3 Agent-native 接口 `agent_init.private_preflight(target, profiles=())`：快照取自 adopt 之前的前置状态；tracked `AGENTS.md` → `AdoptionError` 明确拒绝；选择 profile 时 tracked `docs/engineering/code-comments.md` 同为 carrier 并拒绝；正控制（untracked carrier）通过且同样零写入；worktree/index/HEAD/exclude 四重 fingerprint 前后相等。探针为只读库调用，不新增 CLI storage 参数。原 checker 侧 carrier 测试保留（两者分别冻结检测阶段与 preflight 阶段的合同）。
- P2（Gate 2 表述）：`protocol.md` 与 `results.md` 改为“探针准备阶段故意执行一次 index 写入（即被测的 `git add -f`）；检测阶段仅只读查询、无额外写入”；PASS 结论不变。
- P2（脱敏与一致性）：Codex 记录 session id 替换为 `<redacted>` 并在 protocol 脱敏说明中登记；`protocol.md` 的 runs 链接 `.txt` 改为实际的 `.md`；`vault/runtime.md` Current Progress 行“12 expectedFailure”更正为当前实数。

Checks run:

- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` — 205/205 OK（类内 28 测试：6 绿 + 22 expected failures 为设计状态）。
- `python3 scripts/sync-skills.py --check` — in sync。
- `python3 scripts/trellium.py check . --format json` — 2 error / 1 warning 与基线一致；`recent_entries: 10`。
- `git diff --check` — passed；无 staged 文件；产品 `scripts/trellium.py` 零改动。

Review and reflection:

- 首版 carrier 测试确实只覆盖了检测阶段；preflight 的零写入必须从 adopt 前状态取证，这正是计划 §6.2“不得产生部分写入”的可测形式。
- `private_preflight` 的接口形状（函数名、profiles kwarg、AdoptionError）是 PI 冻结的建议合同，M3 实现如需调整按同一变更更新测试并记录。

Risks:

- preflight 红测锁定了 profiles 维度；若 M3 将 profile carrier 的判定移入 Skill 文案而非脚本函数，需在同一变更中重构该断言（合同不变，载体变化）。

Next action:

- Owner 第三轮复审 M0；通过后授权提交，再进入 M1。

### 2026-09-28 - Agent: PI — M0 review round 3 rework (REQUEST_CHANGES)

Context read:

- Owner 第三轮验收结论（P1：preflight 三合同同测试致 profile/正控制分支未执行且 profile 无 fingerprint；P2：任务审计正文 Gate 2 残留错误事实、protocol.md“index 为空”表述过强）。

Changes made:

- P1：拆分 preflight 为三个独立红测，各自可独立转绿：`test_private_preflight_rejects_tracked_agents_without_writes`（tracked AGENTS.md 拒绝 + fingerprint）、`test_private_preflight_rejects_tracked_profile_carrier_without_writes`（fixture 仅含 tracked profile carrier，与入口 carrier 隔离，调用前后 worktree/index/HEAD/exclude fingerprint 必须相等）、`test_private_preflight_allows_untracked_carrier_without_writes`（untracked 正控制 + fingerprint）。
- P2：`TASK-0019` Round 1 记录的 Gate 2 行改为“故意执行一次 `git add -f`（本身即 index 写入）；检测阶段无额外 index 写入”；`protocol.md` fixture 描述“index 为空”改为“`AGENTS.md` 不在 index——index 中仅跟踪 README”。
- 本轮自证：剥离全部 expectedFailure 标记后重跑类内测试，结果 run=30、failures=21、errors=3（即三个 preflight 测试各自因接口缺失 AttributeError 独立处于红态）、unexpected_successes=0，与 owner 的验证方法一致。

Checks run:

- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` — 207/207 OK（类内 30 测试：6 绿 + 24 expected failures 为设计状态）。
- `python3 scripts/sync-skills.py --check` — in sync。
- `python3 scripts/trellium.py check . --format json` — 2 error / 1 warning 与基线一致；`recent_entries: 10`。
- `git diff --check` — passed；无 staged 文件；产品 `scripts/trellium.py` 零改动。

Review and reflection:

- 合同拆分后每个 preflight 合同有独立的转绿门：M3 实现可逐合同落地，任一合同回退只影响对应测试。
- 审计正文与证据文件的事实必须同一点核对（`git add -f` 本身是 index 写入）；本轮已把 Round 1 记录、protocol.md、results.md 三处统一为同一表述。

Next action:

- Owner 第四轮复审 M0；通过后授权提交，再进入 M1。

### 2026-09-28 - Agent: PI — M0 contract and red tests

Context read:

- `vault/index.md`、`runtime.md`、`governance.md`、`project.md`、`handoff.md`、本任务契约与冻结计划全文、D-0010、D-0012、TASK-0013/0017、`scripts/trellium.py`（policy/stamp/local-boundary/storage checker）与 `scripts/test_trellium.py` 既有 fixture 模式、`docs/engineering/code-comments.md`（只读）。

Changes made:

- 仅修改 `scripts/test_trellium.py`：新增模块级 `v2_policy`/`private_policy` helper 与 `PrivateStorageModeTest`（+390 行）。产品 `scripts/trellium.py` 零改动，遵守“红测先行，不写最终实现”。
- P0 消融冻结（绿）：local policy + 同 carrier 全量 exclude → 12 个 `CORE_STORAGE_IGNORED` + 2 个 `LOCAL_BOUNDARY_OVERREACH`、0 warning；放松规则后未覆盖核心翻转为 `CORE_STORAGE_UNCOMMITTED`。证实 docs-only private 不可用。
- Golden 冻结（绿）：canonical tracked 与 local adopt+commit fixture 均 0 finding；M1/M2 不得漂移。
- Guard（绿）：v2 畸形变体 5 例拒绝（缺字段/新旧字段并存/未知 mode/string schema/未知字段）；v1 `task_storage: private` 拒绝。
- 红测 12 例（`unittest.expectedFailure`，沿用 TASK-0013 M0 惯例）：M1 三模式 normalization（tracked→TASK_STORAGE_PENDING、local→LOCAL_BOUNDARY 语义、private 识别）；M2 反向 privacy Gate（clean fixture 0/0、`git add -f`、HEAD 已含 managed path、缺 block、overbroad `/docs/`、git failure、非 Git warning、TASK lifecycle local 语义、monorepo 子目录）。M1/M2 实现落地时在同一变更中去掉对应 marker。
- 顺带修复同文件 4 处既有 ruff 阻断（import 排序、`collections.abc.Iterator`、未用 `patcher` 别名、`list()` 改写）；机械、无行为变化。

Checks run:

- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` — 193/193 OK（177 基线 + 16 新增，12 expected failures 为设计状态）。
- `python3 scripts/sync-skills.py --check` — 双语 snapshot in sync。
- `python3 scripts/trellium.py check . --format json` — 2 error / 1 warning，与本任务开始前完全一致（owner 排除文件 ×2 + TASK-0019 未提交预期 warning），无漂移。
- `python3 scripts/trellium.py status . --format json` — exit 2，与基线一致。
- `git diff --check` — passed。

Kill Gates（真实探针，非单元测试）：

- Kill Gate 1（ignored/untracked AGENTS 发现）：PASS。fixture：git 仓库 + `AGENTS.md` 仅存在于 `.git/info/exclude` 规则下（untracked、ignored、HEAD 干净），无历史会话中性提问 Required Reading。Codex CLI（`codex exec`）与 Claude Code（`claude -p`）均自主发现并读取该文件、逐字引用 sentinel `PRIVATE-DISCOVERY-SENTINEL-7QF3`。两 agent 还各自独立指出 fixture 中缺失的 `vault/runtime.md`，进一步佐证真实读取。
- Kill Gate 2（forced-add 确定性检测）：PASS。private fixture 中故意执行一次 `git add -f vault/index.md`（这本身即一次 index 写入，也是被测违规动作）；之后的检测阶段仅用只读查询 `git ls-files --cached` 与 `git status --porcelain`（`A ` 标记）即确定性地暴露 staged 状态，无 hook、无额外 index 写入。同时证实仅 `git check-ignore` 规则查询无法发现 forced-add——反向 Gate 必须同时查 index 与 HEAD tree，且这是充分条件。

M0 合同冻结点（实现 M1-M2 必须遵守）：

- canonical block 位于 `git rev-parse --git-path info/exclude` 解析路径；marker identity 为 Git-root-relative target，repo 根 target 约定为 `.`（计划未显式钉死此字面量，PI 在此冻结，owner 可否决）。
- block 覆盖：`/AGENTS.md`、`/vault/`、`/skills/agent-task/`、`/.agent-init-backup/` + stamp 其他 exact managed paths；monorepo 子目录使用 `/<prefix>/...` anchored 模式（已验证 subdir cwd 下 target-relative 路径可命中）。
- Red fixture 编码上述契约于 `scripts/test_trellium.py` `PrivateStorageModeTest`。

Review and reflection:

- 红测断言只锁 code/severity/path 与退出码，不锁完整 message 文案，降低 M1/M2 实现期无谓 passphrase churn。
- P0 实测补充了一个计划未明说的细节：全量 ignore 时 `CORE_STORAGE_IGNORED` 先于 `CORE_STORAGE_UNCOMMITTED`（ignored 分支 continue），故“ignored/uncommitted 并存”只出现在部分覆盖场景；已在 P0 测试第二段冻结。

Risks:

- 12 个红测锁定的是 M2 目标态；若实现期 contract 微调（如 finding path 约定），需同步改红测断言并移除 marker，属预期成本。
- M0 尚未验证 linked worktree/submodule 下 `--git-path info/exclude` 的写入权限（计划 §11 已列为 checker 保守失败场景，M2 实现 `PRIVATE_STORAGE_UNVERIFIED` 时覆盖）。

Next action:

- Owner 授权后提交 M0（计划、任务文件、红测）；随后进入 M1 policy v2 normalization，逐个移除对应 expectedFailure marker。

### 2026-09-28 - Agent: Codex — final plan and handoff

Context read:

- Trellium Skill/协议模型/模板指南、项目治理和 runtime、TASK-0007/0013/0017、D-0006/0010/0012、checker policy/core/local storage 实现与测试面。

Changes made:

- 将 private 从“第三种 TASK storage”修正为整个协作层的 storage mode。
- 选择 schema v2 `storage_mode`，legacy v1 通过 normalization 保持兼容。
- 冻结 `.git/info/exclude`、tracked-carrier preflight、反向 privacy Gate、存量迁移禁区和完整测试矩阵。
- 写入 PI 可执行的 M0-M5 计划；未改产品代码。

Checks run:

- 计划完成后运行文档 whitespace、Skill snapshot 与当前 Vault checker；当前 owner 排除文件和未提交 tracked TASK 的既有/预期 findings 如实记录。

Review and reflection:

- 严格 private 与已有 tracked AGENTS 存在不可绕过的 Git 语义冲突；第一版必须 fail-closed。
- “不上传”只能承诺配置与检测，不能承诺阻止用户 `git add -f` 或清除历史。
- schema v2 成本低于让 `task_storage=private` 承担隐藏 core 语义。

Risks:

- 受支持 Agent 是否都发现 ignored/untracked AGENTS 仍需 M0 真实 fixture 验证；这是实现 Kill Gate。
- 新模式没有跨 clone 恢复能力，本地目录丢失即丢失协作记忆。

Next action:

- PI 从 M0 characterization/red tests 开始；Kill Gate 通过后再进入 policy/checker 实现。

### 2026-09-29 - Agent: PI — M1/M2 implementation and handoff to Codex

Context read:

- M0 验收（round 4 通过、commit `31bd8c4`）后的授权：不提交、直接连续实现 M1-M5；中途发现与活跃 Codex 会话并发编辑同一工作区。

Changes made (worktree, uncommitted,与 Codex 进行中的 runtime-projection 重构同文件交叠):

- M1 完成：`validate_policy_object` 支持 v1（`task_storage`）/ v2（`storage_mode`，拒绝 v2 内出现 `task_storage`，budgets 语义不变）；新增唯一归一入口 `normalized_storage_mode(policy)`；三个消费点切换（`check_task_storage` local 分支服务 local+private、private 专属 message；`check_local_boundary`；runtime projection `local_mode` 含 private）；移除 2 个 M1 红 marker（v2 tracked / v2 local，验证转绿）。upgrade 不触碰 policy，v1 byte-preservation 由既有套件覆盖。
- M2 实现：`check_private_boundary` + `parse_private_exclude_blocks` + `private_managed_extras` + `PRIVATE_BASE_MANAGED_PATHS`；`collect_vault_state` 按 normalized mode 分派；private 模式跳过正向 durability Gate、保留 stamp 损坏 `CORE_STORAGE_INVALID`；非 Git → `PRIVATE_STORAGE_UNVERIFIED` warning。碰撞前验证：19 个 M2 红测 + v2-private 识别测试全部转绿（unexpected successes），3 个 preflight 红测保持红（M3）。
- lint-gate 维护：修复 8 个预存 Pyright 诊断 + 14 个 ruff 发现（I001/UP035/SIM105/SIM102/PIE810/SIM109 行为保持的机械修复；3 处 S310 加显式 https 守卫后 `# noqa: S310`）。
- 并发冲突（10:35）：活跃 Codex 会话删除 `check_runtime_projection`/`parse_runtime_task_pointers`（进行中的重构）致构建短暂损坏（NameError，122 errors）；按 owner 决定 Codex 接手全部源码/协议/测试编辑直至 M5，PI 退出 `scripts/*`、`init/*`、`skills/*`。完整交接见 `vault/handoff.md` TASK-0019 条目。

Checks run:

- 碰撞前全量：`python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` — 207/207 OK（22 expected failures，设计状态）。
- 交接时快照（Codex 重构中途）：套件 175 tests，3 failures 为 Codex 进行中状态；类内 30 测试 = 3 expected failures（preflight 三合同，M3）+ 19 unexpected successes（M2 契约已绿，marker 待 Codex 移除）。
- `sync-skills --check`、`git diff --check` 碰撞前均通过。

Handoff to Codex:

- 立即动作：完成 runtime-projection 重构（保留 normalized mode 两处语义）；移除 19 个已转绿 marker（保留 3 个 preflight marker 给 M3）；M3 `private_preflight` + 条件化 adopt 文案 + 双语协议；M4 分发；M5 全量门禁 + 两轮 review → `ready_for_review`。
- 冻结合同与 gate 惯例（noqa/pi-lens-ignore/disposition）详见 `vault/handoff.md` TASK-0019 条目；可执行合同 = `scripts/test_trellium.py` `PrivateStorageModeTest`。
- M5 目标态：全部测试绿、0 expected failures（22 个 marker 全部移除）+ Required Checks 全过；不自动 accepted/commit/push/tag。

Next action:

- Codex 继续 M2 marker 移除与 M3-M5；PI 待命（可做 review 或验证，不碰源码）。

### 2026-09-29 - Agent: PI — owner resumed；M2 hardening + M3 preflight + distribution complete（ready_for_review）

Context read:

- Owner 收敛计划（Phase 0-2 GO）；TASK-0019 全文与 M1/M2 记录；`scripts/trellium.py` private 实现现状；3 条 preflight 冻结契约；冻结计划 §6.2/6.3/7.2。

Changes made:

- Phase 0（收敛计划，无提交）：owner-local stamp 恢复 HEAD、删除未跟踪 `docs/engineering/code-comments.md`（备份 `/tmp/trellium-phase0-backup/`）；check 0/0、status exit 0。
- Phase 1：移除 19 个已转绿 M1/M2 marker（独立提交 `4ddbfe6`），保留 3 个 preflight 红测。
- M2 hardening（4 红测先行 → 修复）：private policy 缺 stamp → fail-closed `PRIVATE_STORAGE_UNVERIFIED`（分支置于非 Git warning 之后，保住 M0 golden）；canonical block 合格后按实际 `git check-ignore` 判定，后置 negation/高优先级规则 un-ignore → `PRIVATE_STORAGE_UNCONFIGURED`；`git check-ignore` 查询失败 → fail-closed；stamp 声明的唯一副本缺失/非普通文件（含 symlink）→ fail-closed。
- M3 preflight：`private_preflight(target, profiles=())` 只读探针——候选=AGENTS/Vault/agent-task/stamp/Comment Policy/所选完整 Profile；任一候选 tracked/in HEAD → `AdoptionError`（含路径与 local 退路）；Git 查询失败 fail-closed；非 Git 目标通过；指纹不变。真实流程接线：70 号模块 Private 章节 + 双语 Skill 冻结 preflight 先于 adopt 的顺序。
- 生命周期与升级：Private 下 untracked managed 文件不视为 dirty（`git_dirty_paths include_untracked` 按 policy 豁免）；无冲突完成提示改为保持 untracked/ignored + 重跑 check，不提示 commit；adopt checklist 增加 private 步骤并给 tracked 步骤加限定词。
- 2.4 消融：计划文档 R2 Evidence（不重跑真人探针，M0 Kill Gate 证据已落盘）与 R5 Cheapest test（handoff 已被 H2 淘汰）按 owner 清单失效化。
- 2.5 分发：70 号模块新增 Private 存储模式章节；双语 Skill 增 private 接入流程；MIGRATIONS 新增 Unreleased — private storage mode（5 条）；`sync-skills` 刷新镜像与 manifest；AGENTS Profile 路由零改动。
- 移除最后 3 个 preflight marker；恢复 sed 行号过期误删的 3 行测试内容（git diff 核验）。

Checks run:

- PrivateStorageModeTest 34/34 OK；全量 unittest OK exit 0（0 expected / 0 unexpected failure，首次全绿）；sync `--check` in sync；嵌入副本 byte-identical；self check 0 error / 0 warning；`git diff --check` 干净。
- 自查两轮：R1 覆盖面（protocol/Skill/MIGRATIONS private 语义与 preflight 引用齐全）；R2 最小性（变更面 = TASK-0019 授权文件；无 add_argument 增项；AGENTS.md 零漂移）。

Review and reflection:

- M0 golden `test_policy_v2_private_mode_is_recognized` 的 UNVERIFIED severity 期望由 warning 收敛为 error（缺 stamp fail-closed 是 M2 hardening 明确要求）；非 Git warning 路径不变。
- 实施中一次 sed 行号过期误删 3 行测试内容，当轮经 git diff 定位恢复。

Risks:

- preflight 的 Agent-native 调用依赖 Skill 文档的模块加载方式（无 CLI）；请 Codex 确认该接线满足“实际流程使用”标准。

Next action:

- Codex 独立验收 review；owner 决定 accepted。PI 停在 review 门，不进入收敛计划 Phase 3。

### 2026-09-29 - Agent: PI — review round 1 rework（REQUEST_CHANGES：4 P1 + 2 P2）

Context read:

- Codex 验收结论；`private_preflight`/`check_private_boundary`/`complete_upgrade`/`adopt_project` 现状；四处合同漂移面原文。

Changes made:

- P1-1：preflight 碰撞判定改为命名空间感知——tracked/HEAD 下任一文件落在 `vault/`、`skills/agent-task/`、`.agent-init-backup/`（target-scoped）或精确候选（stamp、Comment Policy、所选 Profile docs、AGENTS.md）即拒绝。红测：tracked `vault/custom.md` 曾返回 `[]`，现 `AdoptionError`。
- P1-2：rev-parse 探针区分真实非 Git 目标（放行）与 git 不可用/异常（fail-closed `AdoptionError`）。红测：mock rev-parse → None 曾返回 `[]`。
- P1-3：`complete_upgrade` 补 private 分支——完成提示为保持 untracked/ignored + 重跑 check，不提示 commit。红 e2e：private repo + 本地定制 + patched upstream → `--apply` 冲突 → `--complete` 输出断言。
- P1-4 合同同步：`10-vault.md` policy 节重写为 v2 canonical（schema_version 2 + storage_mode 三模式 + v1 legacy 归一化）；`60-initialization-flow.md` step 5 三模式选择 + step 8 private exclude 语义；双语 vault/index 模板 policy block 迁移到 schema v2（storage_mode，渲染默认值仍 tracked，纯合同同步）并同步说明文字；双语 `protocol-model.md` policy 段重写。TASK-0019:94 AC 按 owner 收敛计划显式拆分（README→Phase 3、VERSION→Phase 6）后勾选。
- P2-1：双语 Skill 补可执行模块加载调用形式；`adopt_project` 对既有 private 项目 re-adopt 时真实调用 `private_preflight`（失败则 adopt 拒绝）。红测：private 项目新增 tracked managed path 后 re-adopt 曾静默通过。
- P2-2：runtime Known Risks 的 CORE_STORAGE 条目替换为 Phase 0 后现实（check 0/0）。
- 测试同步：两个模板合同测试断言更新到 v2 字段名（rendered-policy replace 与 storage_mode=local 断言）——owner 指示模板迁移的直接后果，非行为变更。

Checks run:

- PrivateStorageModeTest 38/38 OK；全量 OK exit 0（0 expected / 0 unexpected）；sync `--check` in sync；嵌入副本 byte-identical；self check 0/0；`git diff --check` 干净。

Review and reflection:

- M0 时代的模板合同测试（task_storage 字段名断言）随 v2 模板迁移同步更新——属合同演进，非放松。
- 私有冲突制造必须用 patched_templates 造 upstream delta（同版本下仅改本地文件不产生 upgrade 冲突）。

Risks:

- 无 handoff。

Next action:

- Codex 复验本轮 rework；通过后按收敛计划进入 Phase 3（TASK-0024）。

### 2026-09-29 - Agent: PI — review round 2 rework（REQUEST_CHANGES：3 P1 + 2 P2）

Context read:

- Codex round 2 结论；`git ls-files`/`ls-tree --full-name` 坐标差异验证；四处 v1-only 残留原文。

Changes made:

- P1-1：`private_preflight` 统一坐标——`git ls-files`（target-relative）归一化为 repo-relative 后与 `ls-tree --full-name` 同坐标系匹配；monorepo staged-only `vault/custom.md` 红测（曾 PASS 漏报，现拒绝）。附带 `private_preflight` 入口 `Path(target)` 强转（修复 Skill 命令的 str AttributeError）。
- P1-2：双语 Skill 的 preflight 示例改为 argv 传参（`Path(sys.argv[1])` + `profiles=tuple(sys.argv[2:])`，避免路径引号注入且携带所选 profile）；新增 Skill 命令 smoke test（从 SKILL.md 提取精确命令，clean fixture 返回 `[]`、tracked carrier 非零退出并报路径）。
- P1-3：live 合同三模式收齐——`10-vault:162`、`70:73`（首次选择三模式）、`70:158`（保持既有 storage_mode/mode 迁移）、`SKILL:45` 首次选择补 private；双语 governance/handoff/tasks-README/agent-task 模板与 live governance/tasks-README 的 disposition/lifecycle 限定从 `task_storage=local` 扩展为“采用 local lifecycle 语义（storage_mode=local 或 private）”；补齐同类的 `20-governance:216`、`30-agent-entry:83`。模板合同测试断言同步到新措辞（storage_mode=local / local lifecycle）。
- P2-1：TASK-0019:94 AC 拆分为两行——已同步部分勾选，README/VERSION 推迟项不勾选（owner 授权拆分）。
- P2-2：current_slice 更新为 review-round-2 rework 状态。

Checks run:

- PrivateStorageModeTest 40/40 OK（38 + 2 新红→绿：monorepo staged、Skill 命令 smoke 双场景）；全量 OK exit 0；sync `--check` in sync；嵌入副本 byte-identical；check 0/0；`git diff --check` 干净；live 合同 v1-only 残留为零（仅剩 legacy 归一化语境与产品内 v1 字段消息）。

Risks:

- 无 handoff。

Next action:

- Codex 复验；通过后进入收敛计划 Phase 3（TASK-0024）。

### 2026-09-29 - Agent: PI — review round 3 closeout（3 P2 + 验收门选项 b）

Changes made:

- P2-1：`10-vault.md:235` 迁移条款改为“`storage_mode` 迁移（含 private）由 owner 单独评审”，消除 private 迁移不在授权门内的歧义。
- P2-2：关闭语义后半句统一——“采用 local lifecycle 的任务关闭后”覆盖 private（`20-governance:216`、live `vault/tasks/README:16`、双语 tasks/README 模板、双语 en tasks/README 模板英文句）。
- P2-3：smoke test 重构——提取并分别执行双语 Skill 的精确命令；tracked fixture 改用 `docs/engineering/profiles/go-backend.md`（不传 profiles 即 PASS，冻结 argv 透传）；子测试覆盖 clean/tracked 双场景。
- 验收门：选定方案 b——README/VERSION 验收项保留在 TASK-0019 内不勾选，README 落 Phase 3（TASK-0024）、VERSION 落 Phase 6（release-prep），两项完成并验收后 TASK-0019 方可 accepted；current_slice 同步。

Checks run:

- PrivateStorageModeTest 40/40 OK；全量 OK exit 0；sync `--check` in sync；check 0/0；`git diff --check` 干净。

Risks:

- 无 handoff。

Next action:

- Codex 复验；通过后进入收敛计划 Phase 3（TASK-0024）。

## Memory Updates

- `vault/runtime.md`
- `vault/handoff.md`
- 验收后才新增 durable decision
- Durable knowledge disposition: not_applicable（tracked task）

## Handoff Requirement

PI 中断时记录当前 milestone、red/green fixture、normalized policy 状态、privacy finding 集合和任何 Kill Gate；禁止把部分 private 支持描述为完成。
