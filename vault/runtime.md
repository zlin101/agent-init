# Runtime Context

## Current Phase

Post-2026.09.9 convergence: H1–H4 + TASK-0023 accepted/committed (`c631e68`); A1 parity guard landed (`437941b`); TASK-0019 resumed from parked — Phase 0-2 of the convergence plan complete, TASK-0019 at `ready_for_review` for Codex.

## Focus

- TASK-0019

Focus is navigation only. It owns no lifecycle, Authority, slice, Gate, or active-task inventory; `trellium status` reads TASK state directly from task files.

## Current Progress

- `2026.09.9` is published as a tag-only release; explicit-version installation was verified and no GitHub Release was created (D-0013).
- TASK-0001 is accepted and TASK-0004 is superseded; the self-hosting and Orion pilot work is closed with Context remaining No-Go (D-0004).
- TASK-0018 is accepted and committed as `bf253f8`; origin/develop was verified at that commit.
- TASK-0019 final plan is frozen after storage-schema and entry-carrier ablation plus strategy red-team.
- TASK-0019 M0 passed owner review after three rework rounds: 24 expectedFailure red tests plus P0/golden/guard freezes in `scripts/test_trellium.py` (marker-stripped self-check: 21 failures + 3 errors, 0 unexpected successes), kill-gate evidence in `docs/evals/private-mode-kill-gates-2026-09/`; checker baseline unchanged and the M0 commit is authorized.
- 2026-09-29: PI implemented M1 (policy v2 normalization) and M2 (reverse privacy Gate; 19 red tests green), then handed the worktree to Codex; the owner has now parked TASK-0019 before marker removal and M3-M5.
- 2026-09-29: TASK-0020 freezes the H2 execution plan: handoff becomes interruption-triggered transient delta; PI implements and Codex independently accepts.
- 2026-09-29: TASK-0020 H2 passed Codex review and owner acceptance; TASK-0021 freezes the H3 plan to downgrade ordinary budget exceed to health warnings and remove automatic task-close compaction without adding maintenance machinery.
- 2026-09-29: PI implemented TASK-0021 H3 (M0-M4) in one pass: both `BUDGET_EXCEEDED` producers are repository-health warnings (warning-only check/status/CI exit 0; correctness errors retain exit 2), task-close compaction coupling deleted across AGENTS/Skill/routing/compaction protocol and bilingual templates with explicit compaction preserved, MIGRATIONS H3 entry added; owner accepted H3 after review.
- 2026-09-29: TASK-0022 (H4) implemented M0-M4: task classification rewritten risk-first (canonical three-step flow: Level C risk domain → recovery/coordination cost → default A); all mechanical scale thresholds deleted from live surfaces; MIGRATIONS entry added; 7 red→green contracts in `LocalTemplateSemanticsTest`; historical replay tables in the task file; owner accepted H4 after review.
- 2026-09-29: TASK-0022 review round 1 (REQUEST_CHANGES) fixed: architecture added as explicit Level C risk domain across canonical + all distribution surfaces; MIGRATIONS upgrade semantics corrected to merge-carrier reality; baseline checksum self-reference removed (21/21 verify) and checker exit corrected to 2; runtime refreshed for H3 acceptance.
- 2026-09-29: TASK-0023 (Profile protocol drift cleanup) implemented M0-M4: `70-adoption-flow.md` made sole canonical owner for profile engineering rules; "唯一 code-comments" drift removed from INIT/protocol README/READMEs/Skills; `agent_entry_section()` fixed to route the complete profile per D-0011 for existing-AGENTS adoptions; regression test red→green; concise MIGRATIONS entry; dual-review loop resolved the stale carrier-only rule in module 50; owner accepted after review.
- 2026-09-29: owner accepted TASK-0020..0023; H1–H4 + profile drift cleanup committed as `c631e68` (parked TASK-0019 M1/M2 delta included as-is; storage warnings cleared, known owner-local storage errors retained by policy).
- 2026-09-29: convergence plan Phases 0-1 done: owner-local stamp restored to HEAD + owner-local carrier deleted (check 0/0); `4ddbfe6` retired 19 satisfied M1/M2 markers.
- 2026-09-29: TASK-0019 Phase 2 complete — M2 hardening (stamp-missing / post-block negation / check-ignore failure / missing sole copy all fail-closed; actual `git check-ignore` outcome verification), M3 read-only `private_preflight` probe wired into protocol + Skills, Private upgrade/adopt completion semantics, plan-doc ablation, MIGRATIONS private entry; last 3 markers removed, full suite fully green; ready_for_review for Codex.

## Constraints

- Preserve owner changes and never include `vault/.agent-init.json` or `docs/engineering/` in TASK-0019.
- Do not operate on Orion or any other repository.
- Publish future Trellium versions by tag only; do not create GitHub Releases or release prose (D-0013).
- Prefer explicit `install.sh --version`; unversioned install still resolves the last GitHub Release, not the newest tag.
- Decision-state changes require owner confirmation; this compaction is structural only.
- Private must not weaken TASK-0013 durability/security gates for tracked/local projects or use hidden Git index state.

## Recent Changes

- 2026-09-29: A1（owner 裁定的 Profile 路由 parity guard，Level A test-only）：`TemplatePackagingTest.test_profile_routing_paragraph_parity_across_append_and_templates` 冻结 agent_entry_section 与 en 模板路由段落全段等价（空白归一化）及三副本（append/en/zh）六项语义不变量（完整 Profile 路径、root 匹配当前路径、仅实际语言、carrier 兼容、重叠 carrier 优先、其余完整 Profile 约束）；F002 残留收口。A2/A3 合并为观察项（等真实定制摩擦），self-hosting Profile 补齐待单独授权评估。
- 2026-09-29: accepted TASK-0020 H2 after two review/rework rounds and opened TASK-0021 with the reflected/ablated H3 plan; no H3 product implementation or planning handoff was created.

- 2026-09-29: opened TASK-0020 with the reflected/ablated H2 plan; no H2 implementation or planning handoff was created.
- 2026-09-29: parked TASK-0019 at the post-M2 boundary by owner direction; cleared Focus and retained the exact recovery delta in `vault/handoff.md`.
- 2026-09-29: TASK-0019 M0 approved after four owner review rounds: kill-gate evidence saved, 24 red contracts independently verified, status goldens frozen, and no P0/P1/P2 remains open.
- 2026-09-28: opened TASK-0019 with the final private-mode plan for PI; no product implementation has started.
- 2026-09-28: accepted and pushed TASK-0018 as `bf253f8`; runtime and decisions returned below budget.
- 2026-09-28: released `2026.09.9` by lightweight tag at `e3bf72c`; clean clone passed 177 tests and check 0/0.
- 2026-09-28: accepted TASK-0017; first adoption now asks for TASK storage and recommends/defaults to local without adding a CLI API.
- 2026-09-28: adopted tag-only publishing as D-0013 and superseded D-0003.
- 2026-09-28: accepted TASK-0001 after its retrospective and superseded TASK-0004 with M2 retained as Partial.
- 2026-09-28: released `2026.09.8`; TASK-0016 accepted.

## Known Risks

- The owner-local stamp and engineering document intentionally make the current worktree checker report two `CORE_STORAGE_UNCOMMITTED` errors; this task must neither hide nor modify them.
- Unversioned `install.sh` still follows GitHub `releases/latest`, so after tag-only releases it does not discover the newest tag; explicit `--version` is the documented safe path.
- The checker cannot validate arbitrary natural-language summaries; durable counts remain single-sourced in `vault/details/shadow-run-2026-09.md` (D-0005).
- Private support has two Kill Gates: ignored/untracked AGENTS discovery across supported Agents, and deterministic detection of forced-added managed files.

## Required Checks

```bash
python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh
python3 scripts/sync-skills.py --check
python3 scripts/trellium.py status . --format json
python3 scripts/trellium.py check . --format json
git diff --check
```

## Next Steps

- All four governance tasks (H1–H4) and TASK-0023 are accepted and committed as `c631e68`. TASK-0019 is back in review (Codex验收); 收敛计划 Phase 3-6（TASK-0024 installer、TASK-0025 ownership、vault maintenance、release 2026.09.10）按序等待。
