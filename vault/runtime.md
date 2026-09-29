# Runtime Context

## Current Phase

Post-2026.09.9 development: private storage mode M0 is approved; M1 policy normalization is next.

## Focus

- TASK-0019

## Active Tasks

One line per parallel task; keep bodies in `vault/tasks/<task-id>.md`, this table holds pointers only.

| Task | Objective | Status | Next Action |
| --- | --- | --- | --- |
| TASK-0019 | Add a strict private mode in which all Trellium managed material stays out of Git. | active | M0 approved and commit authorized; begin M1 policy v2 normalization next. |

Status values: draft | active | blocked | ready_for_review | accepted | superseded. Task state blocks are authoritative; this table is a projection.

## Current Progress

- `2026.09.9` is published as a tag-only release; explicit-version installation was verified and no GitHub Release was created (D-0013).
- TASK-0001 is accepted and TASK-0004 is superseded; the self-hosting and Orion pilot work is closed with Context remaining No-Go (D-0004).
- TASK-0018 is accepted and committed as `bf253f8`; origin/develop was verified at that commit.
- TASK-0019 final plan is frozen after storage-schema and entry-carrier ablation plus strategy red-team; product code is unchanged.
- TASK-0019 M0 passed owner review after three rework rounds: 24 expectedFailure red tests plus P0/golden/guard freezes in `scripts/test_trellium.py` (marker-stripped self-check: 21 failures + 3 errors, 0 unexpected successes), kill-gate evidence in `docs/evals/private-mode-kill-gates-2026-09/`; checker baseline unchanged and the M0 commit is authorized.

## Constraints

- Preserve owner changes and never include `vault/.agent-init.json` or `docs/engineering/` in TASK-0019.
- Do not operate on Orion or any other repository.
- Publish future Trellium versions by tag only; do not create GitHub Releases or release prose (D-0013).
- Prefer explicit `install.sh --version`; unversioned install still resolves the last GitHub Release, not the newest tag.
- Decision-state changes require owner confirmation; this compaction is structural only.
- Private must not weaken TASK-0013 durability/security gates for tracked/local projects or use hidden Git index state.

## Recent Changes

- 2026-09-29: TASK-0019 M0 approved after four owner review rounds: kill-gate evidence saved, 24 red contracts independently verified, status goldens frozen, and no P0/P1/P2 remains open.
- 2026-09-28: opened TASK-0019 with the final private-mode plan for PI; no product implementation has started.
- 2026-09-28: accepted and pushed TASK-0018 as `bf253f8`; runtime and decisions returned below budget.
- 2026-09-28: released `2026.09.9` by lightweight tag at `e3bf72c`; clean clone passed 177 tests and check 0/0.
- 2026-09-28: accepted TASK-0017; first adoption now asks for TASK storage and recommends/defaults to local without adding a CLI API.
- 2026-09-28: adopted tag-only publishing as D-0013 and superseded D-0003.
- 2026-09-28: accepted TASK-0001 after its retrospective and superseded TASK-0004 with M2 retained as Partial.
- 2026-09-28: released `2026.09.8`; TASK-0016 accepted.
- 2026-09-18: closed the project-scoped `trellium-work` direction as No-Go (D-0009).
- 2026-09-16: released `2026.09.7` and accepted durable comment routing (TASK-0012).

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

- Begin M1 policy v2 normalization, removing its three expectedFailure markers in the same implementation change.
