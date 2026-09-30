# Runtime Context

## Current Phase

Post-2026.09.9 convergence CLOSED and `2026.09.10` published tag-only; Profile knowledge ablation is owner-accepted after Codex independent APPROVE. Local commit is authorized for TASK-0026 only; parallel TASK-0027 and discussion files remain separate, with no push or release authorized.

## Focus

- TASK-0026

Focus is navigation only. It owns no lifecycle, Authority, slice, Gate, or active-task inventory; `trellium status` reads TASK state directly from task files.

## Current Progress

- 2026-09-30: TASK-0026 round-1 review = REQUEST_CHANGES (1 P1: first-five “replays” were keyword counts, gate wrongly passed; 3 P2: zh Go lost `Application/Use Case → Domain`, help-docs misused as environment fact source, records drifted) — rework landed; fixed-input fixture replay (5 scenes × before/after, `docs/evals/profile-knowledge-ablation-2026-09/`) executed; evidence retained in TASK and eval fixtures.
- 2026-09-30: TASK-0026 round-2 review = REQUEST_CHANGES (2 P1: build replay had unguarded `rm -rf`, capture parse/exit could not signal failure; 2 P2: floating-HEAD baseline, s5 fixture lacked the Comment Policy file) — rework landed: create-only build + strict parse/failure-propagating capture with self-test (`tooling-selftest.txt`), pinned `BASE_SHA` + profile hashes (`profiles.sha256`), targeted s5 rerun with byte-identical Policy on both sides; all four findings independently closed.
- 2026-09-30: Profile knowledge ablation independently verified (213/213 full, 62/62 focused, s5 6/6 and 9/9); owner accepted TASK-0026 and authorized its scoped local commit. Engineering preferences, routing and machine state remain unchanged; finite single-pair A/B limitations remain documented.
- Convergence Phases 0-5 implemented (`4ddbfe6`/`172fa19`/`5061cd6`/`c5fa637`/`6b6747a`/`1380d6f`/`995e7a0`/`c9939b1`); Phase 6 executed (`051fad6` release-prep, `8765012` acceptances): full suite + clean-clone check 0/0, network installer E2E on tag `2026.09.10`, TASK-0019 deferred item closed and flipped accepted.
- `2026.09.9` and `2026.09.10` are published as tag-only releases (D-0013); the lightweight tag `2026.09.10` was pushed at `051fad6`.
- Owner-local files were removed in Phase 0; `check` is 0/0.

## Constraints

- Preserve owner changes and never include `vault/.agent-init.json` or `docs/engineering/` in TASK-0019.
- Do not operate on Orion or any other repository.
- Publish future Trellium versions by tag only; do not create GitHub Releases or release prose (D-0013).
- Require explicit `install.sh --version`; unversioned installs fail closed before any network access (TASK-0024 removed latest-release resolution).
- Decision-state changes require owner confirmation; this compaction is structural only.
- Private must not weaken TASK-0013 durability/security gates for tracked/local projects or use hidden Git index state.

## Recent Changes

- 2026-09-29: Phase 3 TASK-0024 complete — install.sh requires explicit --version for network installs (latest-release resolver removed, fail-closed before any network), bilingual README install sections updated, README.en H1 runtime-projection drift fixed, --fetch scoped to adopt/diff/upgrade across READMEs and 70-adoption-flow, ReadmeContractTest added; ready_for_review.
- 2026-09-29: TASK-0019 review round 3 closeout accepted (storage_mode migration wording, local-lifecycle close semantics, both-Skill command smoke); owner approved Phase 0-2 and authorized Phase 3; TASK-0019 `active` with README/VERSION deferred to TASK-0024/Phase 6.
- 2026-09-29: TASK-0025 Comment/Profile ownership round 1 complete — Comment Policy solely owns comment/API-documentation expression, profiles keep behavior/fallback with ownership pointers, three-way routing in AGENTS/agent_entry_section; ready_for_review.
- 2026-09-29: convergence Phases 0-1 done: owner-local cleanup (check 0/0); `4ddbfe6` retired 19 satisfied M1/M2 markers.
- 2026-09-29: A1 parity guard landed (`437941b`): appended/en-template routing paragraph parity plus three-copy ownership invariants frozen.
- 2026-09-29: owner accepted TASK-0020..0023; H1–H4 + profile drift cleanup committed as `c631e68` (parked TASK-0019 M1/M2 delta included as-is).
- 2026-09-28: released `2026.09.9` by lightweight tag at `e3bf72c`; clean clone passed 177 tests and check 0/0.
- 2026-09-28: adopted tag-only publishing as D-0013 and superseded D-0003.
- 2026-09-28: accepted TASK-0017; first adoption now asks for TASK storage and recommends/defaults to local without adding a CLI API.
- 2026-09-28: accepted TASK-0001 after its retrospective and superseded TASK-0004 with M2 retained as Partial.

## Known Risks

- Owner-local files were removed in convergence Phase 0 (stamp restored to HEAD, owner-local carrier deleted); the former two `CORE_STORAGE_UNCOMMITTED` errors are gone and check is 0/0.
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

- No remaining TASK-0026 implementation; leave parallel TASK-0027 and discussions separate. Further implementation, push and release require separate owner direction.
