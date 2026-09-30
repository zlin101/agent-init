# Runtime Context

## Current Phase

Post-2026.09.9 convergence CLOSED and `2026.09.10` published tag-only; Profile knowledge ablation committed as `77ee022`. Round 3 hot-path routing ablation accepted and closed out: scoped multi-TASK commit + push executed under explicit owner authorization (TASK-0028 plus parallel tracked materials). TASK-0027/TASK-0029 committed at their current tracked state as separate lines; releases stay tag-only under owner direction.

## Focus

- TASK-0028

Focus is navigation only. It owns no lifecycle, Authority, slice, Gate, or active-task inventory; `trellium status` reads TASK state directly from task files.

## Current Progress

- Round 3 review is closed: routing dedup and runtime trim retained; Level A index-skip remains No-Go, so the default reading set is unchanged. No remaining Round 3 implementation.

## Constraints

- Preserve owner changes and never include `vault/.agent-init.json` or `docs/engineering/` in TASK-0019.
- Do not operate on Orion or any other repository.
- Publish future Trellium versions by tag only; do not create GitHub Releases or release prose (D-0013).
- Require explicit `install.sh --version`; unversioned installs fail closed before any network access (TASK-0024 removed latest-release resolution).
- Decision-state changes require owner confirmation; this compaction is structural only.
- Private must not weaken TASK-0013 durability/security gates for tracked/local projects or use hidden Git index state.

## Recent Changes

- 2026-09-30: owner accepted Round 3 after independent APPROVE (review baseline `77ee022`); scoped multi-TASK commit + push executed under the same owner authorization.

## Known Risks

- Unversioned `install.sh` now fails closed before any network access (TASK-0024 removed latest-release resolution); existing user scripts that relied on the implicit fallback must add an explicit `--version` tag.
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

- Round 3 is closed (accepted, committed, pushed under owner authorization). TASK-0027/TASK-0029 remain separate owner-reviewed lines; Round 4 only on explicit owner request; releases/tag remain owner-directed.
