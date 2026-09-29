# TASK-0020 - Handoff transient delta ablation

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0020",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "ready_for_review",
  "current_slice": "owner-accepted-awaiting-tracked-commit",
  "gates": {
    "implementation": "passed",
    "historical_replay": "passed",
    "distribution_sync": "passed",
    "review": "passed"
  }
}
-->

## Objective

将 `vault/handoff.md` 从任务状态、进展和验证结果的第二份人工副本，收敛为只在真实中断时出现的 transient delta：恢复者先读取 canonical TASK、Git、working tree、tests 与 durable knowledge，再用 handoff 补齐无法低成本推导的中断现场。

本任务的成功标准不是换一套字段，而是减少同一业务任务需要维护的持久化副本、同步动作和漂移面，同时保持真实中断可恢复。

## Ownership

- PI 负责按本计划实施 H2，并停在 review 门前。
- Codex 负责独立验收、历史回放复核和 P0/P1/P2 收敛。
- Owner 决定 accepted、commit、push、tag 或发布；本任务不自行执行这些动作。
- 本计划正常完成且没有不可推导的 transient state，因此创建计划本身不创建 handoff。

## Scope

### In Scope

- 收敛 handoff contract 为三个字段：`Why interrupted`、`Transient context not captured elsewhere`、`Exact resume point`。
- 把 handoff 写入改为“真实 interruption + 存在恢复价值 delta”事件触发；正常执行、等待 acceptance 和普通 review 不触发。
- 明确恢复顺序：canonical TASK / repo state / tests 在先，handoff 只补 transient delta。
- 删除协议、模板和 agent-task Skill 中要求复制 Objective、Completed、In Progress、Failed Attempts、Blockers、普通 Next Action、Files To Read First 或完整 tests 的规则。
- 防止删掉 handoff 字段后把 execution history、Git diff 或测试日志整体搬入 TASK Execution Record。
- 只处理当前活跃 handoff；历史 Git 版本与已归档任务不批量迁移。
- 用三个真实历史案例回放 recoverability 与 drift 消融。
- 更新必要双语模板、简明引用、canonical protocol、MIGRATIONS 和 generated protocol snapshots。

### Out of Scope

- H3 compaction correctness/health 解耦。
- H4 Level A/B/C 分类调整。
- Review Ledger、finding lifecycle 或 review trigger。
- runtime TASK projection（H1 已完成，不在本任务继续调整）。
- TASK-0019 private 模式实现、marker 清理或 M3-M5。
- installer、tag-only UX、profile drift、task storage 或 `trellium.py` 模块拆分。
- 新增 handoff parser、validator、finding、lifecycle、state、schema 或 CLI。
- 批量重写历史 task、handoff、decision 或 Git 历史。
- 新增独立治理报告、评估目录或 handoff 专用 Skill。

## Context Required

- `AGENTS.md`
- `vault/index.md`
- `vault/runtime.md`
- `vault/governance.md`
- `vault/handoff.md`
- `vault/parked.md`
- `vault/tasks/README.md`
- `skills/agent-task/SKILL.md`
- `init/protocol/10-vault.md`
- `init/protocol/15-vault-compaction.md`
- `init/protocol/20-governance.md`
- `init/protocol/30-agent-entry.md`
- `init/protocol/40-skills.md`
- `init/protocol/70-adoption-flow.md`
- `init/protocol/80-execution-patterns.md`
- `init/MIGRATIONS.md`
- 双语 handoff/governance/index/AGENTS/tasks README/agent-task 模板和 concise references
- `scripts/test_trellium.py` 中 `EmbeddedSkillLayoutTest`、`LocalTemplateSemanticsTest` 与 handoff budget fixture

## Capability Tags

- agent-governance
- handoff
- recoverability
- protocol-ablation
- templates
- testing

## Authority

Allowed:

- 修改本任务列明的 H2 协议、模板、Skill、自托管 vault、迁移说明、generated snapshots 和聚焦内容测试。
- 只迁移当前 `vault/handoff.md`；历史 handoff 仅通过 `git show` 只读回放。
- 在 `/tmp` 创建回放材料；不把回放全文新增为仓库治理文件。

Requires Approval:

- 改变三个目标字段的语义或恢复顺序。
- 引入任何 machine-readable handoff schema、checker/CLI 行为、TASK lifecycle/state 字段或新治理文件。
- accepted、commit、push、tag 或发布。

Forbidden:

- 修改 H3/H4、Review Ledger、runtime projection、TASK storage、installer 或 TASK-0019 产品实现。
- 触碰 owner 排除的 `vault/.agent-init.json` 与 `docs/engineering/`。
- 删除历史事实，或为追求格式统一批量迁移旧任务与 Git 历史。
- 将 handoff 删除的内容原样搬入 TASK Execution Record、runtime、decision 或另一份新文档。
- 把测试输出、Git diff、changed-files list 或普通 Next Action 作为 durable handoff 内容。

## Frozen Contract

### Information ownership

| Information | Canonical owner | Handoff treatment |
| --- | --- | --- |
| Objective / Scope / Acceptance | TASK | Never copy |
| Lifecycle / Authority / slice / gates | `trellium-task-state` | Never copy |
| Committed changes | Git | Inspect live |
| Uncommitted changes | working tree / diff | Inspect live |
| Test truth | Rerun tests | Do not preserve full result |
| Durable failure conclusion | TASK Execution Record or decision | Link only when needed |
| Why the current context stopped | handoff, only when not already cheaply recoverable | `Why interrupted` |
| Non-reproducible or partially completed transient operation | handoff | `Transient context not captured elsewhere` |
| Exact continuation operation | handoff, only when it adds recovery value beyond task slice | `Exact resume point` |

### Minimal entry

```md
## TASK-xxxx

### Why interrupted

...

### Transient context not captured elsewhere

...

### Exact resume point

...
```

`SESSION` remains allowed when no TASK exists. A taskless interruption may put the minimum non-derivable goal context inside the transient section; it does not reintroduce an Objective field.

If all useful information is cheaply derivable from TASK + Git + working tree + tests + durable knowledge, do not create an empty handoff entry merely because a session ended.

The distributed blank template must contain no active `## TASK-...` or `## SESSION` example heading, because the existing budget counter treats such headings as real entries. It may document the three-section shape without materializing a fake entry; a newly adopted project must measure `handoff.entries == 0`.

### Event trigger

Create or update handoff only when both are true:

1. A real interruption occurred: session boundary before completion, Agent ownership switch, owner pause, unavailable environment/external dependency, or a partially completed transient operation.
2. At least one recovery-relevant fact or exact continuation action is not cheaply derivable from canonical repository state.

Do not create or update handoff for normal completion, waiting for owner acceptance, completed review, an open lifecycle alone, an ordinary next step, or a fully recoverable clean session boundary.

On resume, read TASK and live repo/test state first. Read handoff only for an interrupted task, apply its delta, and delete the entry once its transient value is consumed; durable conclusions must already live in canonical owners.

## Ablation And Red-Team Conclusions

### A1 - Three headings could become a new mandatory report

- Fails if every session writes three sections containing `none` or repeats TASK progress.
- Cheapest test: Case B must produce no handoff at all.
- Kill criterion: any protocol sentence makes incomplete lifecycle, normal completion, ready-for-review, or waiting acceptance sufficient to create handoff.

### A2 - Duplication could move into TASK Execution Record

- Fails if removal of Completed/Tests/Failed Attempts causes equivalent mandatory fields or logs to appear in TASK.
- Cheapest test: diff task templates and execution guidance before/after.
- Kill criterion: H2 adds a new mandatory execution-history field, full test log, changed-files list, or generic progress report to TASK.

### A3 - Recoverability could fall for real external/manual interruptions

- Fails if Case A cannot identify the exact external action and stopping reason after duplicate summaries are removed.
- Cheapest test: replay TASK-0002 from commit `05c8a36` using the proposed delta.
- Kill criterion: fresh recovery requires reintroducing the whole task summary instead of one transient fact and one exact action.

### A4 - Current handoff could keep drifting against the working tree

- Fails if Case C still stores milestone completion, test counts, changed files or normal next steps.
- Cheapest test: compare TASK-0019 handoff from `31bd8c4` with the current working tree and targeted tests.
- Kill criterion: recovery trusts handoff progress over live TASK/diff/tests, or requires synchronizing the same progress in both places.

### A5 - Governance simplification could add more machinery than it deletes

- Fails if H2 needs a parser, checker finding, schema, lifecycle, new Skill, scheduler or additional durable document.
- Cheapest test: production diff must be zero and live contract/template LOC must be net negative.
- Kill criterion: any `scripts/trellium.py` behavior change or net-positive live protocol/template source without a demonstrated recovery requirement.

Surviving design: three human-readable sections, dual trigger (interruption + non-derivable delta), TASK/repo-first recovery, no machine enforcement.

## Implementation Plan

### M0 - Freeze baseline and protect concurrent work

1. Read the current dirty worktree and preserve all H1 and parked TASK-0019 changes; do not restore files from HEAD.
2. Record baseline line counts for live handoff contract/template files separately from cold MIGRATIONS and generated snapshots.
3. Record the known suite baseline: 186 tests; normal runner is nonzero only for 19 stale TASK-0019 `expectedFailure` markers, while three M3 preflight expected failures remain intentional.
4. Confirm `trellium.py` has no old handoff-field parser. Existing `count_handoff_entries` only counts `## TASK-` / `## SESSION` headings and remains unchanged.

### M1 - Canonical protocol deletion

Make the smallest semantic edits in:

- `init/protocol/10-vault.md`: replace durable narrative/progress ownership with transient-delta ownership and TASK/repo-first recovery.
- `init/protocol/15-vault-compaction.md`: stop merging generic failures/history into TASK; expired handoff deltas may be deleted after any durable conclusion is already canonical.
- `init/protocol/20-governance.md`: replace the seven old mandatory fields with the three-section contract and dual trigger; acceptance gate records durable unfinished risks in TASK, not ordinary handoff.
- `init/protocol/30-agent-entry.md`: handoff is conditional reading/writing for real interrupted work, never a default progress sink.
- `init/protocol/40-skills.md`: starter workflow requires interruption-triggered delta, not generic handoff updates.
- `init/protocol/70-adoption-flow.md`: remove “mere unfinished work creates handoff”; only actual interruption with non-derivable delta does.
- `init/protocol/80-execution-patterns.md`: recovery order is TASK → Git/working tree/tests → handoff delta.
- `init/MIGRATIONS.md`: one Unreleased H2 entry; historical handoff stays untouched, current active entry is classified/migrated only if it contains a surviving delta.

Do not modify `init/VERSION`, Review Ledger sections, compaction warning/error policy, Level classification or CLI behavior.

### M2 - Entry, Skill, templates and self-hosting contract

Update only H2-relevant text in:

- `AGENTS.md`
- `skills/agent-task/SKILL.md`
- `vault/index.md`
- `vault/governance.md`
- `vault/tasks/README.md`
- bilingual `assets/templates/AGENTS.md`
- bilingual `assets/templates/vault/{index,governance,handoff,tasks/README}.md`
- bilingual `assets/templates/skills/agent-task/AGENT_TASK_SKILL.template`
- bilingual concise `references/{protocol-model,templates-guide}.md`

Do not touch `skills/trellium*/SKILL.md` unless an exact old-field or unconditional-handoff rule is found; overview mentions alone are not a reason to churn them.

Current self-host handoff classification:

- Audit every TASK-0019 handoff sentence against the ownership table.
- Preliminary result: pause reason is in `parked.md`/TASK, implementation facts are in TASK/diff, test counts are rerunnable, and resume slice is in TASK state. Therefore the expected H2 result is deletion of the TASK-0019 handoff entry and return of `vault/handoff.md` to empty template state.
- If PI finds a genuinely non-derivable fact, keep only that current entry in the three-section format and record the concrete reason in TASK-0020; do not migrate any historical entry.

TASK Execution Record guidance:

- Keep only durable deviations, kill-gate conclusions and one-line replay outcomes.
- Verification may record command + pass/fail summary, not copied logs.
- Do not add Completed/Changed Files/full Tests/ordinary Next Action as new required fields.

### M3 - Distribution and focused tests

1. Run `python3 scripts/sync-skills.py` after canonical `init/` edits; never edit generated protocol-source snapshots manually.
2. In `scripts/test_trellium.py`, limit edits to template/distribution content tests:
   - adopted English and Chinese handoff templates contain the three localized headings;
   - live templates omit Objective, Completed, In Progress, Failed Attempts, Blockers, Next Best Action and Files To Read First;
   - agent-task templates state the dual trigger and TASK/repo-first recovery;
   - existing local-task close compression semantics remain intact;
   - a newly adopted blank handoff measures zero entries while `count_handoff_entries` remains unchanged.
3. Prefer extending/renaming existing `EmbeddedSkillLayoutTest` and `LocalTemplateSemanticsTest`; target no more than two net-new test methods.
4. Do not edit TASK-0019 expectedFailure markers as part of H2.

### M4 - Historical replay

Do not add a new eval directory. Use `git show` and temporary files, then record only one-line outcomes in this task.

Case A — genuine interruption, TASK-0002 at `05c8a36`:

- Reconstruct from AGENTS/index/runtime/TASK, Git state and available tests first.
- Candidate delta: environment lacked `gh`; the external release operation stopped after the wrong tag's Release existed, with 2026.09.3 still missing; resume by creating the Release for the exact 2026.09.3 tag and verifying `releases/latest`.
- Pass when a fresh reader identifies the exact external operation without Objective/Completed/test-history copies.

Case B — false handoff, TASK-0012 at `7ad4d58`:

- Implementation and review were complete; only owner acceptance remained.
- Pass when TASK state, Git and tests are sufficient and the correct new-contract output is “no handoff entry”.

Case C — handoff behind working tree, TASK-0019:

- Compare `31bd8c4:vault/handoff.md`, current TASK state, current diff and targeted test behavior.
- Pass when recovery trusts TASK/diff/tests, not the old “M1 not started” narrative; the retained handoff is empty or contains only a justified transient delta.

For each replay, use a fresh Agent/session when available. The reviewer receives canonical context and repo evidence before the candidate handoff. Score only: correct interruption reason, exact resume action, prohibited duplicated state, and unsafe reliance on stale handoff.

### M5 - Review and stop point

PI performs two self-review rounds:

1. Protocol coverage: all live routes express the same dual trigger, three fields and recovery order; bilingual templates match.
2. Safety/minimality: no H3/H4/Review Ledger/CLI/task-storage drift; no historical migration; live LOC reduction is real.

Then set this task to `ready_for_review` and stop. Do not commit. Codex performs independent P0/P1/P2 review and replays before asking the owner for acceptance.

## Acceptance Criteria

- [x] Handoff is defined only as interruption-triggered, non-derivable transient delta.
- [x] Live templates use exactly the three target sections; `SESSION` remains supported without an Objective field.
- [x] A newly adopted blank handoff contains no countable placeholder entry and measures `handoff.entries == 0` without changing the counter.
- [x] Objective/Scope/Acceptance, lifecycle/authority/slice/gates, Git state, full test truth and ordinary next actions retain their canonical owners.
- [x] Normal completion, waiting acceptance, completed review and open lifecycle alone do not create or update handoff.
- [x] Recovery order is TASK/repo/tests first and handoff delta second; handoff is not a default cold-start source.
- [x] TASK Execution Record gains no replacement progress/test/diff log requirements.
- [x] Current TASK-0019 handoff is removed if fully derivable; otherwise only its evidenced delta is migrated. Historical handoff is untouched.
- [x] No new parser, checker finding, lifecycle, state, schema, CLI behavior, Skill or governance file is introduced.
- [x] Cases A/B/C pass and their outcomes fit in three one-line task records.
- [x] English/Chinese templates, concise references and generated protocol snapshots are synchronized.
- [x] Live protocol/template source LOC is net negative; MIGRATIONS and generated mirrors are reported separately.
- [x] H1 behavior, TASK-0019 implementation and owner exclusions remain untouched.
- [x] No open P0/P1/P2 remains before Codex recommends acceptance.

## Verification

Required focused checks:

- `python3 -m unittest scripts.test_trellium.EmbeddedSkillLayoutTest scripts.test_trellium.LocalTemplateSemanticsTest scripts.test_sync_skills`
- `python3 scripts/sync-skills.py --check`
- scoped `rg` proving old handoff fields/unconditional triggers are absent from live protocol, current template, agent-task Skill and self-host governance (exclude MIGRATIONS, historical tasks and generated historical snapshots as appropriate)
- `python3 scripts/trellium.py status . --format json`
- `python3 scripts/trellium.py check . --format json`
- `git diff --check`

Full-suite delta check:

- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`
- Do not fix TASK-0019 markers in H2. Compare against the frozen baseline: no new assertion failure/error is allowed; the only tolerated nonzero cause is the known 19 stale expectedFailure unexpected successes, with the three M3 preflight expected failures unchanged.

Line accounting:

- Report live canonical/hand-maintained protocol-template LOC separately from `init/MIGRATIONS.md`, generated snapshots, self-host data and TASK-0020.
- Production LOC target: `0`.
- Test target: at most `+2` test methods; no behavioral production tests because no CLI behavior changes.

## Expected Changed Files

Canonical/live source:

- `AGENTS.md`
- `init/MIGRATIONS.md`
- `init/protocol/{10-vault,15-vault-compaction,20-governance,30-agent-entry,40-skills,70-adoption-flow,80-execution-patterns}.md`
- `skills/agent-task/SKILL.md`
- `vault/{index,governance,handoff,runtime}.md`
- `vault/tasks/{README.md,TASK-0020-handoff-transient-delta.md}`
- `scripts/test_trellium.py`

Hand-maintained distribution:

- bilingual `assets/templates/AGENTS.md`
- bilingual `assets/templates/vault/{index,governance,handoff,tasks/README}.md`
- bilingual `assets/templates/skills/agent-task/AGENT_TASK_SKILL.template`
- bilingual `references/{protocol-model,templates-guide}.md`

Generated only:

- matching `skills/trellium*/references/protocol-source/**`
- matching manifests from `scripts/sync-skills.py`

Explicitly unchanged:

- `scripts/trellium.py` and embedded copies except byte-identical sync confirmation
- `init/VERSION`
- Review Ledger sections
- `vault/decisions.md`
- `vault/parked.md` and `vault/tasks/TASK-0019-private-storage-mode.md`
- `vault/.agent-init.json`
- `docs/engineering/`

## Review Gate For Codex

Codex rejects H2 if any of the following remains:

- a normal completed/ready-for-review task is instructed to create handoff;
- handoff repeats a full TASK/Git/tests state projection;
- current handoff contains milestone/test-count/changed-files driftable prose without a non-derivability justification;
- deleted handoff material reappears as mandatory TASK Execution Record content;
- production CLI/checker changes appear;
- historical files are migrated for formatting only;
- live contract/template LOC is not reduced without a concrete recoverability proof;
- any H3/H4/Review Ledger/TASK-0019 work enters the patch.

## Memory Updates

- `vault/runtime.md`: H2 plan/implementation/review phase and navigation Focus only.
- `vault/handoff.md`: only if an actual interruption leaves a non-derivable delta; planning handoff is intentionally absent.
- `vault/decisions.md`: no new record expected; the frozen protocol and MIGRATIONS entry are canonical. Add a decision only if implementation discovers a new durable choice outside this approved contract, which requires owner approval.
- Durable knowledge disposition: not_applicable (tracked task).

## Handoff Requirement

Do not create handoff merely because PI begins or finishes this plan. If PI is genuinely interrupted and repo state cannot reconstruct the exact continuation, write only the three-section delta. Otherwise TASK state, diff and tests are sufficient.

### 2026-09-29 - Agent: PI — H2 implemented in one pass (M0-M5), ready for Codex review

- M0 baseline: suite 186 tests (3 preflight expected + 19 TASK-0019 stale markers), `count_handoff_entries` confirmed unchanged (`^##\s+(TASK-|SESSION)` only); live LOC 3067 across 29 contract/template/reference files.
- M1 canonical: 7 protocol files reworded to dual-trigger/three-section/recovery-order (10-vault owner table + handoff section; 15-compaction consume-then-delete; 20-governance Handoff section, gate #6 and `blocked` narrowed to TASK-only; 30-entry conditional read; 40-skills starter workflow; 70-adoption step 15; 80-execution recovery order); MIGRATIONS gains one Unreleased H2 entry (+7 cold LOC, reported separately).
- M2 entry/skill/templates/self-host: AGENTS.md, agent-task Skill, vault/{index,governance,tasks/README}.md, en+zh templates (AGENTS, index, governance, tasks/README, agent-task), en+zh references (protocol-model, templates-guide). Self-host `vault/handoff.md` reset to empty transient-delta contract (TASK-0019 entry deleted: pause reason lives in parked/TASK, implementation facts in TASK/diff, test counts rerunnable, resume slice in task state block — fully derivable, owner pre-judged and confirmed).
- M3 distribution/tests: `sync-skills.py` regenerated protocol-source snapshots (byte-identical embedded trellium.py confirmed via cmp); +2 net-new tests in LocalTemplateSemanticsTest (`test_handoff_templates_use_transient_delta_contract`, `test_adopted_blank_handoff_measures_zero_entries`); existing locale-marker assertion in `test_embedded_packages_install_their_own_locale` replaced by zero-entries assertion (the placeholder-entry convention is exactly what H2 ablates); local-close-compression note re-added to both handoff templates to keep `test_handoff_templates_carry_local_close_compression` green.
- M4 replay (one-line outcomes): Case A TASK-0002 @ 05c8a36 — PASS: exact external op (owner creates Release for tag 2026.09.3, verify `releases/latest`) reconstructed from TASK acceptance criteria + record L105/L176 (`gh` missing already recorded in TASK); old entry's Objective/Completed copies pure duplication. Case B TASK-0012 @ 7ad4d58 — PASS: state block ready_for_review + all-[x] criteria + commit `bbae794` fully capture waiting-for-acceptance; old entry was 100% duplication; correct new-contract output = no handoff. Case C TASK-0019 — PASS: old handoff claimed "M1 not started" while the working tree completed M1/M2 with a Codex handoff; recovery now trusts task state block + diff + tests (19 unexpected successes + 3 preflight reds); retained handoff empty, drift surface gone.
- LOC accounting: live contract/template/reference 3067 → 3035 (**net −32**); MIGRATIONS +7 (cold, separate); production `trellium.py` unchanged (embedded copies byte-identical); test +2 methods.
- Checks: focused suite 18/18 OK; full 188 tests (3 expected + 19 stale markers, zero new failures vs frozen baseline); sync `--check` in-sync; checker baseline exactly 2 owner errors + 1 expected TASK_STORAGE_PENDING on TASK-0020; `handoff.entries == 0`; `git diff --check` clean; scoped rg proves old fields/unconditional triggers/countable headings absent from live surface (residual matches are canonical TASK contract/record fields or the prohibition sentence itself).
- Self-review ×2 done (coverage + safety/minimality). Durable deviations: existing locale-marker test updated as above; no other deviations from frozen plan.

### 2026-09-29 - Agent: PI — review round 1 rework (REQUEST_CHANGES: 2 P1 + 2 P2)

- P1-1 MIGRATIONS migration branch: Agent migration bullet rewritten as explicit three-way classification with wholesale-copy prohibition — (1) fully derivable → delete; (2) unique durable fact (long-term constraint / failure conclusion) → distill one-sentence conclusion into TASK record or decision first, then delete (no narrative/progress/test-history copies); (3) non-derivable transient delta → rewrite to the three sections, delete after consumption.
- P1-2 semantic inversions: fixed inverted condition in 10-vault owner table (now 无法从 canonical 状态低成本推导); 40-skills starter workflow and en/zh protocol-model Checkpointable bullets now carry both trigger conditions (real interruption + non-derivable delta).
- P2-3 local-close semantics: all six live compress sites replaced with delete-on-close (10-vault, 20-governance, self-host tasks/README, en/zh tasks/README templates, en/zh handoff templates); test renamed `test_handoff_templates_carry_local_close_deletion` and now asserts the old compression wording is absent in both locales.
- P2-4: acceptance criteria 1-13 checked with implementation evidence; criterion 14 (no open P0/P1/P2 before acceptance) intentionally left unchecked pending this review round.
- Re-verification after rework: focused 18/18 OK; full suite 188 (3 expected + 19 stale markers, no new failures); sync in-sync; checker 2 owner errors + 1 expected TASK_STORAGE_PENDING; `handoff.entries == 0`; `git diff --check` clean; residual rg sweep clean (no inverted condition, no compress-handoff, no single-trigger route left in live surface).

### 2026-09-29 - Agent: PI — review round 2 rework (REQUEST_CHANGES: 2 P1, original four re-verified pass)

- P1 README.md:355: compaction narrative no longer says handoff "滚动保留" or frames deletion as information loss; handoff clause now states the transient-delta contract (kept only for real interruptions with non-derivable facts, consume-then-delete, deletion is not information loss). The same sentence appears verbatim in the cold 2026-08-21 plan archive (`docs/superpowers/plans/`), which is historical record and left untouched.
- P1 bilingual templates-guide: en/zh `vault/handoff.md` bullets now require both conditions (real interruption + non-derivable recovery fact). Proactive harmonization with the same sweep: protocol-model en/zh file bullets and both blank handoff templates dropped their single-trigger opening phrases ("for real interruptions only" / "仅用于真实中断") in favor of the dual-condition phrasing; repo-wide sweep over live surface (excluding docs archive, historical task files, `.upgrade` proposals, generated snapshots) now returns zero single-trigger or rolling-retention matches.
- Re-verification: focused 18/18 OK; full suite 188 (3 expected + 19 stale, no new failures); sync in-sync; checker 2 owner errors + 1 expected TASK_STORAGE_PENDING; `handoff.entries == 0`; `git diff --check` clean.

### 2026-09-29 - Agent: Codex — review passed and owner accepted

- Round-2 incremental review closed the remaining two P1 findings; focused/full test baselines, sync, checker baseline, zero-entry handoff and whitespace checks matched the frozen contract. The owner then declared H1/H2 accepted and review gate moved to `passed`; because this tracked task file is still untracked and commit is not authorized in this planning turn, lifecycle remains `ready_for_review` until the accepted task and implementation enter Git together.
