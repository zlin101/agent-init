# TASK-0019 - Private storage mode

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0019",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "active",
  "current_slice": "M0-contract-and-red-tests"
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

- [ ] M0 契约和 P0/P1 red fixtures 先于产品实现提交，tracked/local golden 冻结。
- [ ] schema v1 tracked/local 与 schema v2 三模式严格解析并规范化；既有 v1 不自动改写。
- [ ] private clean fixture 达到 check 0/0；全部 managed material untracked/staged-free 且 ignored。
- [ ] canonical exclude block 通过 `git rev-parse --git-path info/exclude` 定位，target identity 唯一，patterns anchored 且不越 approved scope。
- [ ] tracked/staged/forced-add、缺 ignore、overreach、Git failure 全部 fail-closed。
- [ ] tracked AGENTS/private 冲突在任何写入前失败；不使用隐藏 index 状态绕过。
- [ ] private 使用 local TASK lifecycle，但文案不声称跨 clone durable。
- [ ] adopt/diff/upgrade/profile 与 managed-file allowlist、dirfd/fallback、link/path 安全边界无回归。
- [ ] 不新增 CLI storage 参数，不自动修改 index/commit/push/history。
- [ ] 双语协议、README、MIGRATIONS、VERSION 与 snapshots 同步。
- [ ] 全量测试、check、sync、whitespace 和独立 review 通过，无 open P0/P1/P2。
- [ ] 任务停在 `ready_for_review`，由 owner 决定 accepted 和发布。

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

## Memory Updates

- `vault/runtime.md`
- `vault/handoff.md`
- 验收后才新增 durable decision
- Durable knowledge disposition: not_applicable（tracked task）

## Handoff Requirement

PI 中断时记录当前 milestone、red/green fixture、normalized policy 状态、privacy finding 集合和任何 Kill Gate；禁止把部分 private 支持描述为完成。
