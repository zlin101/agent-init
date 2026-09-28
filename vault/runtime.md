# Runtime Context

## Current Phase

Post-2026.09.9 maintenance: no product or governance task is active.

## Focus

- None

## Active Tasks

One line per parallel task; keep bodies in `vault/tasks/<task-id>.md`, this table holds pointers only.

| Task | Objective | Status | Next Action |
| --- | --- | --- | --- |

Status values: draft | active | blocked | ready_for_review | accepted | superseded. Task state blocks are authoritative; this table is a projection.

## Current Progress

- `2026.09.9` is published as a tag-only release; explicit-version installation was verified and no GitHub Release was created (D-0013).
- TASK-0001 is accepted and TASK-0004 is superseded; the self-hosting and Orion pilot work is closed with Context remaining No-Go (D-0004).
- TASK-0018 is accepted after structural parity checks, 177 tests and Vault budget validation; no task remains open.

## Constraints

- Preserve owner changes and never include `vault/.agent-init.json` or `docs/engineering/code-comments.md` in this task.
- Do not operate on Orion or any other repository.
- Publish future Trellium versions by tag only; do not create GitHub Releases or release prose (D-0013).
- Prefer explicit `install.sh --version`; unversioned install still resolves the last GitHub Release, not the newest tag.
- Decision-state changes require owner confirmation; this compaction is structural only.

## Recent Changes

- 2026-09-28: accepted TASK-0018; runtime fell from 153 to 67 lines and decisions became a 21-line index with 13 linked bodies.
- 2026-09-28: released `2026.09.9` by lightweight tag at `e3bf72c`; clean clone passed 177 tests and check 0/0.
- 2026-09-28: accepted TASK-0017; first adoption now asks for TASK storage and recommends/defaults to local without adding a CLI API.
- 2026-09-28: adopted tag-only publishing as D-0013 and superseded D-0003.
- 2026-09-28: accepted TASK-0001 after its retrospective and superseded TASK-0004 with M2 retained as Partial.
- 2026-09-28: released `2026.09.8`; TASK-0016 accepted.
- 2026-09-20: accepted TASK-0013 through TASK-0015 after 177 tests and security review.
- 2026-09-18: closed the project-scoped `trellium-work` direction as No-Go (D-0009).
- 2026-09-16: released `2026.09.7` and accepted durable comment routing (TASK-0012).
- 2026-09-09: shipped local TASK lifecycle and deterministic read-only status foundations.

## Known Risks

- The owner-local stamp and engineering document intentionally make the current worktree checker report two `CORE_STORAGE_UNCOMMITTED` errors; this task must neither hide nor modify them.
- Unversioned `install.sh` still follows GitHub `releases/latest`, so after tag-only releases it does not discover the newest tag; explicit `--version` is the documented safe path.
- The checker cannot validate arbitrary natural-language summaries; durable counts remain single-sourced in `vault/details/shadow-run-2026-09.md` (D-0005).

## Required Checks

```bash
python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh
python3 scripts/sync-skills.py --check
python3 scripts/trellium.py status . --format json
python3 scripts/trellium.py check . --format json
git diff --check
```

## Next Steps

- Start no new feature until the owner selects the next priority.
