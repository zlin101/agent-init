# TASK-0021 - Budget health decoupling

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0021",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "ready_for_review",
  "current_slice": "M0-M4-done-awaiting-codex-review",
  "gates": {
    "implementation": "passed",
    "warning_exit": "passed",
    "correctness_regression": "passed",
    "distribution_sync": "passed",
    "review": "pending"
  }
}
-->

## Objective

将普通 Vault budget exceed 从业务 TASK 的 acceptance critical path 中移出：`BUDGET_EXCEEDED` 是可见但不阻断的 repository-health warning；不可读、不可解析、结构或 storage contract 损坏仍是 correctness error。保留显式 compaction 能力，不引入第二套 budget 或 maintenance 状态。

核心不变量：

```text
task correctness != repository health
```

## Ownership

- PI 按本计划实施 H3，并停在 `ready_for_review`。
- Codex 独立复核 severity、退出码、CI 调用链、协议消融和 P0/P1/P2 收敛。
- Owner 决定 accepted、commit、push、tag 或发布；本任务不自行执行这些动作。
- TASK-0019 保持 parked，不移除其测试 marker，不继续 M3-M5。

## Scope

### In Scope

- 将 hot-file 与 active-task budget 的现有 `BUDGET_EXCEEDED` severity 从 `error` 改为 `warning`，finding code 与 measurement schema 不变。
- 证明 `check`、`status` 和直接运行 checker 的 CI 在只有 budget warning 时退出 `0`。
- 保持 policy/state/required-file/symlink/non-regular/unreadable/storage 等 correctness findings 为 error。
- 删除 AGENTS、agent-task、Vault routing 与 compaction protocol 中“普通任务收尾发现超预算就立即压缩”的默认耦合。
- 明确 budget warning 只提示独立 maintenance 候选，不扩展当前业务 TASK scope。
- 保留 owner 明确要求、独立 maintenance TASK、当前 TASK acceptance 明确要求或 correctness 已损坏时的显式 compaction 流程。
- 同步必要中英文模板、简明引用、MIGRATIONS 与 generated protocol snapshots。

### Out of Scope

- H4 Level A/B/C 分类。
- Profile protocol drift、Review Ledger、installer latest、task-storage、handoff、runtime projection。
- `trellium.py` 模块拆分、`trellium maintain`、自动 scheduler 或新的 maintenance lifecycle。
- 新 finding、新 threshold 层级、soft/hard/critical budget 分类或新的 policy 字段。
- 修改 compaction 算法、decision/parked 语义判定、现有预算数值或 measurement schema。
- 实际压缩当前 Vault、创建 maintenance commit、push、tag、release 或跨仓库操作。
- 修改 owner 排除的 `vault/.agent-init.json` 与 `docs/engineering/`。
- 修复 TASK-0019 的 expectedFailure markers 或继续 private-mode 实现。

## Context Required

- `AGENTS.md`
- `vault/index.md`
- `vault/runtime.md`
- `vault/governance.md`
- `init/protocol/10-vault.md`
- `init/protocol/15-vault-compaction.md`
- `skills/agent-task/SKILL.md`
- `scripts/trellium.py`
- `scripts/test_trellium.py`
- `.github/workflows/skill-sync.yml`

## Capability Tags

- agent-governance
- checker-severity
- protocol-ablation
- testing

## Authority

Allowed:

- 修改上述 H3 直接相关 checker、测试、协议、模板、简明引用与生成快照。
- 调整现有测试断言并增加最少量聚焦测试。
- 运行本地只读检查和单元测试。

Requires Approval:

- 任何超出 H3 的 schema、finding、CLI、workflow、task level 或 compaction 算法变化。
- commit、push、tag、release 或恢复 TASK-0019。

Forbidden:

- 让 warning-only 结果以非零退出，或把 correctness error 降级为 warning。
- 解析 TASK 自然语言 acceptance 来替代 TASK 自己的验收门。
- 新增 maintenance state、scheduler、命令、文档层或持久化副本。
- 为消除 warning 自动改写 Vault、自动压缩或扩大业务 TASK scope。
- 覆盖当前混合工作树中的 H1/H2/TASK-0019/owner 改动。

## Current Implementation Facts

- `scripts/trellium.py` 只有两个 `BUDGET_EXCEEDED` 生成点：hot-file thresholds 与 `max_active_tasks`；当前均写死为 `error`。
- `VaultCheckRun.errors` 只按 `severity == "error"` 聚合；`check_project` 与 `status_project` 均仅在 `run.errors` 非空时返回 `CHECK_ERROR_EXIT`。
- CI 的两个 self-hosting steps 直接运行 `python3 scripts/trellium.py check . --format json`，没有“任意 finding 即失败”的 wrapper；因此不应修改 workflow，只需用行为测试验证。
- `TASK_COUNT_UNRESOLVED` 已是 warning，保持不变。
- 当前协议耦合主要位于 `AGENTS.md`、`vault/index.md`、`skills/agent-task/SKILL.md`、双语模板、`init/protocol/10-vault.md`、`init/protocol/15-vault-compaction.md` 与 README 的 task-close 叙述。

## Reflected Ablation / Kill Assumptions

### A1 - Severity-only change is sufficient

- Steelman: existing rendering, JSON summary, `check`、`status` and CI all derive failure from `run.errors`, so changing the two producer severities should propagate without a new abstraction.
- Fails if any caller fails on total finding count, the string `BUDGET_EXCEEDED`, or warning count.
- Cheapest test: run text/JSON `check` and `status` against a fixture whose only findings are budget warnings; assert both exit `0`, errors `0`, warning findings retained. Inspect CI command unchanged.
- Kill criterion: any warning-only path returns nonzero. Fix the existing caller predicate; do not add a compatibility state or second code path.

### A2 - Correctness remains independently enforced

- Steelman: required-file, policy/state parsing, symlink/non-regular/unreadable and storage checks have independent error codes and do not depend on budget severity.
- Fails if an unreadable/malformed canonical source is represented only as a budget warning or returns `0`.
- Cheapest test: retain and explicitly rerun malformed policy/state plus unsafe input/storage tests; add only a focused assertion if current coverage does not prove exit `2`.
- Kill criterion: any structural/canonical corruption becomes warning-only. Revert and isolate the accidental severity change.

### A3 - Protocol deletion does not recreate maintenance machinery elsewhere

- Steelman: a warning plus existing explicit compaction protocol is enough; no scheduler is needed because owner/TASK acceptance already supplies intent.
- Fails if implementation adds a new threshold class, lifecycle, command, queue, auto-created TASK, required follow-up field or mandatory warning-to-maintenance transition.
- Cheapest test: scoped diff/`rg` for new budget codes, schema fields, maintenance states and unconditional “exceed -> compact” routes.
- Kill criterion: added durable machinery exceeds the two severity changes plus deletion/rewording of coupling rules.

### A4 - Explicit maintenance remains recoverable without generic enforcement

- Steelman: owner request or a TASK acceptance criterion already makes compaction part of that task contract; the generic checker need only report health.
- Fails if protocol says an explicit compaction criterion may be ignored because check exits `0`, or if implementation parses Markdown acceptance to enforce it.
- Cheapest test: protocol fixture/review showing explicit maintenance remains governed by its TASK criterion while the checker still emits only the generic warning.
- Kill criterion: either compaction capability disappears, or a natural-language acceptance parser/state is introduced.

### A5 - Mixed-worktree implementation stays attributable

- Steelman: H3 touches a narrow set of known lines even though H1/H2/TASK-0019 are uncommitted in overlapping files.
- Fails if PI restores files from HEAD, rewrites whole generated/manual files, edits owner exclusions, or reports aggregate diff as H3-only evidence.
- Cheapest test: record pre-H3 fingerprints/diffs for every expected overlapping file; review H3 hunks semantically and use sync tooling for generated snapshots.
- Kill criterion: any pre-existing change is lost or H3 provenance cannot be separated. Stop and restore only from the recorded pre-H3 content, never from HEAD wholesale.

Surviving design: two producer severity edits, existing error-based exit path, protocol deletion of automatic coupling, explicit compaction preserved, no new state.

## Implementation Plan

### M0 - Freeze baseline and red tests

1. Capture `git status --short`, no-staged state, relevant file fingerprints/diffs, current full-suite baseline and the two known owner checker errors. Do not clean or restore the worktree.
2. Locate all `BUDGET_EXCEEDED` producers and all direct checker callers; confirm only the two known producers and direct CI command exist.
3. First change/add focused tests so current behavior fails H3 expectations:
   - use table-driven/subtest coverage for runtime, decisions, handoff and parked explicit thresholds; each produces only `BUDGET_EXCEEDED` warnings and `check` exit `0`;
   - active-task count over budget produces the same warning/exit behavior;
   - `status` also exits `0` for warning-only budget findings;
   - malformed policy or TASK state remains error/exit `2`;
   - healthy fixture remains unchanged.
4. Do not use expectedFailure markers for H3; ordinary red/green assertions are sufficient.

### M1 - Minimal checker change

1. Change only the severity argument at the two existing `BUDGET_EXCEEDED` producer sites from `error` to `warning`.
2. Do not rename the finding, alter messages/measurements/policy schema, add helpers, or special-case exit codes.
3. Confirm `check_project` and `status_project` remain untouched unless a red test proves an existing caller is not severity-based.
4. Do not modify `.github/workflows/skill-sync.yml`; its direct checker invocation is the end-to-end CI proof unless inspection discovers a real wrapper.

### M2 - Delete acceptance coupling, preserve capability

Use the smallest wording changes:

- `AGENTS.md` and bilingual AGENTS templates: budget checks may surface health warnings; they do not require current-task compaction or block acceptance unless compaction is in the task contract.
- `skills/agent-task/SKILL.md` and bilingual agent-task templates: replace unconditional step 17 with warning/report behavior plus explicit-maintenance exceptions; retain the five-phase procedure only as a routed capability.
- `vault/index.md` and bilingual index templates: replace “超出即压缩” with “warning visible; do not expand current TASK; explicit maintenance routes to protocol”.
- `init/protocol/10-vault.md`: change “trigger compaction” and update-rule coupling to health-signal language.
- `init/protocol/15-vault-compaction.md`: redefine trigger as explicit owner/maintenance TASK/current acceptance/correctness-recovery intent; remove task-close exceed as an automatic trigger. Keep algorithms and safety invariants unchanged.
- `README.md` and `README.en.md`: change over-budget error to warning and remove task-close automatic compaction wording; preserve existing H1/H2 semantics while editing the paragraph.
- bilingual `references/protocol-model.md`: state that configured exceeds are warnings and explicit compaction is independent maintenance. Do not expand the concise reference into a scheduler policy.
- `init/MIGRATIONS.md`: add one H3 Unreleased entry covering severity/exit behavior and Agent migration of unconditional task-close rules.

Do not touch governance acceptance fields, Review Ledger, level classification or compaction algorithms.

### M3 - Distribution sync and four cases

1. Run `python3 scripts/sync-skills.py`; generated protocol-source snapshots and embedded scripts are outputs, not hand-edited sources.
2. Case A: accepted/ready business TASK plus explicit runtime and decisions thresholds exceeded -> all `BUDGET_EXCEEDED` findings warning, `check` and `status` exit `0`.
3. Case B: malformed policy/TASK state and unsafe canonical input regression -> error retained, exit `2`.
4. Case C: protocol says an explicit compaction acceptance criterion still blocks that TASK until satisfied; checker does not parse or replace that criterion.
5. Case D: healthy project golden remains zero-error with unchanged output schema; `TASK_COUNT_UNRESOLVED` remains warning.
6. Verify both main and embedded bilingual `trellium.py` copies are byte-identical after sync.

### M4 - Self-review and stop

PI performs two reviews:

1. Correctness/exit review: every budget exceed is warning-only, every structural/canonical/storage error remains blocking, and CI uses the same exit semantics.
2. Ablation/minimality review: no unconditional task-close compaction route remains; explicit compaction still exists; no H4/profile/review/installer/task-storage/handoff/private-mode changes entered the patch.

Then set TASK-0021 to `ready_for_review`, record concise command outcomes, and stop without commit or handoff unless a real interruption leaves a non-derivable delta.

## Acceptance Criteria

- [x] Both existing `BUDGET_EXCEEDED` producers emit `warning`; the finding code, messages, measurements and policy schema remain stable.
- [x] Warning-only budget fixtures make both `check` and `status` exit `0`, including the same direct invocation used by CI.
- [x] runtime, decisions, handoff, parked and active-task-count budget exceed are all repository-health warnings.
- [x] Malformed policy/state, unreadable/non-regular/symlink canonical input, task-state damage and storage-contract damage remain correctness errors with nonzero exit.
- [x] A normal business TASK can be accepted with visible `BUDGET_EXCEEDED` warnings when its own acceptance criteria pass.
- [x] An explicit compaction TASK/criterion remains binding through its own contract, not through generic budget checker enforcement.
- [x] No normal task-close route requires immediate five-phase compaction, Vault rewrite or a separate maintenance commit.
- [x] Owner-requested or independently scoped compaction still routes to the existing five-phase capability and safety rules.
- [x] No new finding, threshold tier, policy field, CLI command, lifecycle/state, scheduler, parser or governance file is introduced.
- [x] H1/H2 behavior and TASK-0019 parked/private work remain untouched; owner exclusions remain untouched.
- [x] English/Chinese templates, concise references, main script and generated snapshots are synchronized.
- [x] Focused tests, full frozen suite, sync check and whitespace check pass with no new failures beyond TASK-0019's known marker baseline.
- [x] Production change is limited to the two severity literals unless a failing exit-path test proves otherwise; protocol/template deletions exceed additions where practical.
- [ ] No open P0/P1/P2 remains before Codex recommends acceptance.

## Verification

Required focused checks:

- targeted `VaultCheckTest` and status tests covering Cases A-D
- `python3 scripts/trellium.py check <warning-only-fixture> --format json` -> exit `0`, errors `0`, `BUDGET_EXCEEDED` warning visible
- `python3 scripts/trellium.py status <warning-only-fixture> --format json` -> exit `0`
- malformed policy/state fixture -> exit `2`
- scoped `rg` for unconditional task-close compaction language and forbidden new maintenance/schema/finding concepts
- `cmp` main and both embedded `trellium.py` copies

Repository gates:

- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`
- `python3 scripts/sync-skills.py --check`
- `python3 scripts/trellium.py status . --format json`
- `python3 scripts/trellium.py check . --format json`
- `git diff --check`
- `git status --short` proving no staged files unless owner separately authorizes staging

Frozen baseline note: TASK-0019 currently causes 19 stale expectedFailure unexpected successes with three preflight expected failures. H3 must add no new failure/error and must not remove those markers.

Line accounting targets:

- production source: net `0` LOC expected (two severity literal replacements; generated embedded copies reported separately);
- tests: small positive delta only for Cases A-D, preferring table-driven extensions over duplicated fixtures;
- live protocol/templates: net negative where practical because automatic-coupling rules are deleted, not replaced by a new subsystem;
- MIGRATIONS, generated snapshots, self-host data and TASK-0021 are reported separately.

## Expected Changed Files

Product and tests:

- `scripts/trellium.py`
- `scripts/test_trellium.py`
- synchronized `skills/trellium*/assets/trellium.py`

Canonical/live protocol:

- `AGENTS.md`
- `README.md`
- `README.en.md`
- `init/MIGRATIONS.md`
- `init/protocol/10-vault.md`
- `init/protocol/15-vault-compaction.md`
- `skills/agent-task/SKILL.md`
- `vault/index.md`
- `vault/runtime.md`
- `vault/tasks/TASK-0021-budget-health-decoupling.md`

Hand-maintained distribution:

- bilingual `assets/templates/AGENTS.md`
- bilingual `assets/templates/vault/index.md`
- bilingual `assets/templates/skills/agent-task/AGENT_TASK_SKILL.template`
- bilingual `references/protocol-model.md`

Generated only:

- matching `skills/trellium*/references/protocol-source/**`
- matching manifests from `scripts/sync-skills.py`

Unexpected edits to `.github/workflows/skill-sync.yml`, governance, task templates/README, handoff, profiles, installer, Review Ledger, decisions, parked, TASK-0019, owner exclusions or unrelated tests require stopping and justification.

## Review Gate For Codex

Codex rejects H3 if any of the following remains:

- any ordinary budget exceed is still error or makes `check`/`status`/CI return nonzero;
- any correctness/storage/safety failure was downgraded;
- ordinary business acceptance still mandates compaction, Vault rewrites or an unrelated commit;
- explicit compaction capability or its safety invariants were deleted;
- a second budget model, maintenance state, scheduler, command or acceptance parser appears;
- protocol claims warning-only behavior without an exit-code test;
- H4 or another excluded concern enters the patch;
- pre-existing mixed-worktree changes are lost or misreported as H3.

## Memory Updates

- `vault/runtime.md`: H3 plan/implementation/review phase and navigation Focus only.
- `vault/decisions.md`: no new record expected; the owner-frozen principle is implemented directly in checker/protocol. Add a decision only if implementation discovers a genuinely new durable choice, which requires approval.
- `vault/handoff.md`: only for a real interruption with non-derivable transient state; planning and normal PI/Codex review create no entry.
- Durable knowledge disposition: not_applicable (tracked task).

## Handoff Requirement

Normal PI implementation and Codex review do not create handoff. If genuinely interrupted, record only the non-derivable transient delta and exact resume point; TASK state, diff and rerunnable tests remain canonical.

## PI Completion Report

At the review stop, report only:

```text
Changed:
- ...

Severity changes:
- ...

Deleted coupling:
- ...

Added complexity:
- ...

Behavior verification:
- warning-only exit code
- correctness error exit code

Tests:
- ...

Net result:
- production LOC ±
- test LOC ±
- protocol/template LOC ±

1. 一个与 Vault maintenance 无关的业务 TASK，是否还可能仅因为普通 budget exceed 而无法 accepted？
2. 是否新增了任何第二套 budget threshold、maintenance state 或 scheduler？
```

Target answers: `1. 否`；`2. 否`。

## Execution Record

### 2026-09-29 - Agent: Codex — plan frozen for PI

- Read current checker, exit paths, CI workflow, budget tests and all live task-close compaction routes. Red-team/ablation left five kill assumptions; all are covered by M0-M4 gates. No H3 product implementation was performed.

### 2026-09-29 - Agent: PI — M0-M4 implemented, stopped at ready_for_review

- M0 baseline: 68 dirty paths, staged 0; suite 188 (3 expected + 19 stale, no new failures); checker exactly 2 owner errors + 2 expected TASK_STORAGE_PENDING (TASK-0020/0021); pre-H3 sha256 fingerprints recorded for all 10 overlap files. Producers confirmed: exactly two `BUDGET_EXCEEDED` sites (trellium.py L2697 hot-files, L2735 task count); CI calls the checker directly at two workflow steps, no wrapper; exit predicates severity-based (`CHECK_ERROR_EXIT if run.errors`). Red tests written first, no expectedFailure markers: new table-driven `test_budget_exceeds_are_warning_only_health_signals` (runtime/handoff/decisions/parked/active-tasks × check+status exit 0) plus two existing assertions flipped red (7 failures confirmed before M1).
- M1 production change: exactly two severity literals `"error"` → `"warning"` at the two producer sites; diff-verified (`- "error"` / `+ "warning"` hunks only); no renames, no helpers, no exit special-casing, workflow untouched.
- M2 coupling deletion: AGENTS.md + en/zh templates (rule 12 → health-warning language), agent-task SKILL + en/zh templates (step 17 → report warning; five phases only on explicit intent: owner request / independent maintenance TASK / task acceptance / correctness recovery), vault/index.md + en/zh templates, 10-vault.md (2 sites), 15-vault-compaction.md trigger section redefined (explicit-intent taxonomy; task-close exceed is a health signal, not a trigger; algorithms and safety invariants untouched), README.md + README.en.md compaction paragraphs, en/zh protocol-model one-sentence warning note, MIGRATIONS H3 Unreleased entry (Breaking/Removed/Auto/Agent migration). Residual rg sweep clean.
- M3: sync applied, `--check` in-sync; main and both embedded trellium.py byte-identical (cmp). Case A warning-only fixture via direct CLI (CI form): check exit 0, summary errors 0 / warnings 3 (`BUDGET_EXCEEDED` ×2 + `GIT_CHECK_SKIPPED` ×1, all severity warning), status exit 0. Case B malformed policy: exit 2 retained; full VaultCheckTest+StatusSummaryTest (44 tests) confirm all correctness/storage findings remain blocking. Case C: `acceptance` occurs zero times in the checker — no parser exists; explicit criteria bind via task contract only. Case D: full suite 189 (188 frozen + 1 new H3 test) with the same 3 expected failures and 19 stale markers and zero new failures.
- M4 self-review: (1) correctness/exit — both producers warning-only, every structural/canonical/storage error still blocking, CI semantics identical by construction; (2) ablation/minimality — production delta is the two literals; no new finding/threshold/state/scheduler/CLI/parser; no H4/profile/review/installer/task-storage/handoff/private-mode changes; ruff 35 findings all pre-date H3 (Codex TASK-0019 layer and older test regions; my two assertion rewrites converted previously-unused `err` bindings to used). LOC: production net 0 (2 literals); H3 tests ≈ +80 net (table test + assertion updates; aggregate file diff includes pre-existing TASK-0019/H2 layers, reported separately); live protocol/templates net ≈ +5 (mostly 15-vault explicit-trigger taxonomy replacing the two-bullet automatic version); MIGRATIONS +22 separate.
- Stop state: `ready_for_review`, gates implementation/warning_exit/correctness_regression/distribution_sync passed, review pending; staged 0, no commit, no handoff (no real interruption).

### 2026-09-29 - Agent: PI — review round 1 rework (REQUEST_CHANGES: 1 P1 + 2 P2)

- P1 severity wording: README.md budget bullet now says `BUDGET_EXCEEDED` warning (repository-health signal, never blocks acceptance) instead of "超限错误"; README.en.md mirror fixed ("over-budget errors" removed); MIGRATIONS Breaking bullet now lists error-retained codes precisely (`POLICY_INVALID`, `TASK_STATE_INVALID`, `FILE_UNREADABLE`, symlink/non-regular canonical input, storage safety `CORE_STORAGE_*` error states) and notes `POLICY_MISSING`/legacy `TASK_STATE_MISSING`/`REQUIRED_FILE_MISSING` were already warnings and are unchanged. All cited code names verified against producer literals.
- P2 severity freeze: table-driven test now asserts each matched `BUDGET_EXCEEDED` finding has `severity == "warning"` (no new test method).
- P2 record corrections: full suite corrected to 189 (188 frozen baseline + 1 new H3 test); Case A fixture composition corrected to `BUDGET_EXCEEDED` ×2 + `GIT_CHECK_SKIPPED` ×1 (the ad-hoc fixture's 30 list items sit outside the Recent Changes section, so `recent_entries` measured 0 and only `max_lines` exceeded); runtime.md Current Phase and Next Steps updated to the implemented/awaiting-review state.
- Re-verification: focused budget tests OK; full suite 189 (3 expected + 19 stale, no new failures); sync re-applied after MIGRATIONS edit and `--check` in-sync; checker 2 owner errors + 2 expected TASK_STORAGE_PENDING; `git diff --check` clean; staged 0.
