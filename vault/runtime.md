# Runtime Context

## Current Phase

Self-hosting pilot: the collaboration layer now maintains the Trellium repository itself.

## Focus

- TASK-0004

## Active Tasks

One line per parallel task; keep bodies in `vault/tasks/<task-id>.md`, this
table holds pointers only.

| Task | Objective | Status | Next Action |
| --- | --- | --- | --- |
| TASK-0001 | Run the self-hosting pilot and collect K1-K4 shadow evidence. | active | Next Agent continues pilot work; log transitions in `vault/details/shadow-run-2026-09.md`. |
| TASK-0002 | Publish the existing 2026.09.3 tag as a GitHub Release. | accepted | Closed 2026-09-08: release is live and latest resolves; title/notes demoted to optional by owner decision (D-0003). |
| TASK-0003 | Execute the 2026-09-08 next-cycle plan: calibrate K1-K4 and add the self-hosting CI check. | accepted | Closed 2026-09-08 after review round 2 and a green first CI run (34181086563). |
| TASK-0004 | Post-release validation: cold-start baseline, second-project pilot, Context Go/No-Go. | active | Orion supplied the first real local-project observation; close its local runtime row and tracked durability boundary, rerun check 0/0, then decide M2. |
| TASK-0007 | Local TASK lifecycle close-out and clone-safe projection (2026.09.4). | accepted | Closed 2026-09-09; 2026.09.4 tag and Release published. |
| TASK-0005 | Vault evidence quality: converge coverage counts to a single source and fix cold-start methodology. | accepted | Closed 2026-09-09 after owner review round 2 (final gate closed, six findings fixed). |
| TASK-0006 | Non-Context optimization: ablation experiments and per-candidate Go/No-Go; Evidence Receipt v0 only if M2 experiments pass. | accepted | Closed 2026-09-09 with strictly scoped conclusions: E2 No-Go, E1 Inconclusive, v0 not implemented this cycle (direction not falsified). |
| TASK-0008 | Ship one 2026.09.5 feature from the Codex feedback audit: deterministic read-only status summary. | accepted | Closed 2026-09-09: owner APPROVE after three review rounds; `2026.09.5` tag and Release follow the accepted commit (D-0007). |
| TASK-0009 | Evaluate whether a minimal Review Pack improves review quality/cost before any CLI implementation. | accepted | Closed 2026-09-13: owner accepted with locked conclusions (R1 Inconclusive; R2 not implemented/proposed this cycle; 12 clean / 7 contaminated; No-Go and over-determined phrasing retired). D-0008. |
| TASK-0010 | Fix the three reproduced `status` defects found by the TASK-0009 experiment (short-row unresolved gap, refused-vault unresolved:0, pipe-truncation projection). | accepted | Closed 2026-09-15: three status-layer fixes (check byte-identical), 3 red-first tests (121 total), independent review APPROVE, CI green (34927880245). MIGRATIONS Unreleased section post-09.5-tag. |
| TASK-0011 | Test whether a thin project-scoped `trellium-work` adds value beyond `AGENTS.md + vault`; only an ablation Go authorizes replacing `agent-task` with a project-scoped skill. | accepted | Closed 2026-09-18: verdict No-Go (zero observable gain over AGENTS.md+vault; A1 costs more; Codex project-discovery unverified); leak fix landed; direction closed per owner acceptance. |
| TASK-0012 | Preserve code-comment and API-documentation knowledge through a one-hop, profile-aware project rule without growing Vault. | accepted | Closed 2026-09-16; develop/tag pushed, CI run 35076645891 green, Release 2026.09.7 live with empty body, and releases/latest resolves to it. |
| TASK-0013 | Close the adoption durability and local Git-boundary false-health gap. | accepted | Closed 2026-09-20 after 177/177 tests, security review and owner approval; implementation commit `7582e7c`. |
| TASK-0014 | Persist complete selected language profiles inside adopted projects with one-hop scoped routing. | accepted | Closed 2026-09-20 after tracked implementation commit `7582e7c` and owner approval. |
| TASK-0015 | Unify Claude Code project instructions on AGENTS.md and retire the CLAUDE.md convention. | accepted | Closed 2026-09-20 after focused checks, implementation commit `7582e7c` and owner approval. |
| TASK-0016 | Publish Trellium 2026.09.8 with minimal release metadata. | accepted | Closed 2026-09-28: tag and empty-metadata GitHub Release are live; latest resolves to 2026.09.8. |

Status values: draft | active | blocked | ready_for_review | accepted |
superseded. For a task with a task file, the status here is a projection of
its `trellium-task-state` block: update the block first, then this row.
Focus names the current attention, not lifecycle; a status change edits only
the matching row. Demote paused-and-shelved tasks to `vault/parked.md`.

## Current Progress

- TASK-0016: accepted and released 2026-09-28 — release id 398079786 is live with empty name/body; latest resolves to 2026.09.8.
- TASK-0015: accepted 2026-09-20 — Claude Code project instructions use AGENTS.md only; Skill installation support remains unchanged.
- TASK-0014: accepted 2026-09-20 — complete selected profiles, explicit locale, external-link rejection and selected-profile-only authorization shipped in `7582e7c`.
- TASK-0013: accepted 2026-09-20 — HEAD durability, exact managed-file authorization and unified dirfd/fallback fail-closed paths passed 177/177 and owner review.
- TASK-0012: accepted and released 2026-09-16 — develop and lightweight tag `2026.09.7` are pushed at `cf7e06a`; CI run 35076645891 success. Release is non-draft/non-prerelease, titled `Trellium 2026.09.7` with an empty body; `releases/latest` resolves to it.
- TASK-0011: ready_for_review 2026-09-16 — M1 verdict **No-Go** (both arms zero key omissions/violations across three scenarios; A1 costs more; Codex project-discovery unverified). No-Go stop-condition leak fix landed (packages sanitized, adopt/upgrade unchanged); privacy history rewrite executed per owner authorization. Independent review APPROVE. Awaiting owner acceptance.
- TASK-0009: accepted 2026-09-13 — preregistered R0/R1 ablation (19 sessions: 12 valid, 7 contamination-voided, 5 infra aborts archived). Formal verdict **Inconclusive** (plan §10.1 cap: double control_invalidated, both reproduced); decision record: S1 known-P0/P1 recall 25% (blocks any Go), wall-clock +24.4% median. Context-efficiency gains were real (visible bytes −57.6%, vault opens −46.2%). Independent review APPROVE ×4 rounds; owner accepted with conclusions locked (no No-Go/over-determined revival). D-0008.
- TASK-0008: accepted 2026-09-09 — read-only deterministic `trellium.py status` (text/JSON v1, fail-closed unresolved boundaries, closed count-only) shipped as 2026.09.5; three review rounds (independent ×2 + owner ×2 rounds) closed with the reason-code fix and verbatim ablation archive (`vault/details/status-blind-test-2026-09/`); durable decision D-0007.
- TASK-0001: self-hosting pilot continues on real work. Coverage facts live solely in `vault/details/shadow-run-2026-09.md` (append-only event rows; dated derived snapshot — D-0005). Numeric coverage gate is met; remaining work is M2 second project, canonical cross-project evidence, and the five-question review.
- TASK-0002: 2026.09.3 Release published (tag `97d5506`, non-draft, non-prerelease) and `releases/latest` resolves to it. Accepted after the owner demoted the empty title/notes to an optional, non-gating improvement (D-0003).
- TASK-0003: M1 reconciled the K1-K4 contract (append-only, canonical K3/K4 observation tables opened); M2 re-verified the release blocker (latest still 2026.09.2); M3 wired the read-only self-hosting check into CI (write permission confined to the PR self-heal job). Accepted 2026-09-08 after review round 2 and a green first CI run.
- TASK-0004: active — Orion is the second real local project and produced a genuine `TASK_RUNTIME_CLOSED_LOCAL` finding. M2 remains Partial until the closed runtime pointer is removed, the core collaboration layer has an explicit tracked boundary/stamp, and Orion check reaches 0/0. D-0004 remains in force; no Context implementation is authorized.
- TASK-0005: coverage counts single-sourced into the shadow ledger (D-0005); cold-start Protocol v2 isolated under `docs/evals/cold-start-v2/`. Accepted 2026-09-09 after owner review round 2 (final gate closed, six findings fixed).
- TASK-0007: local lifecycle disposition gate + clone-safe projection implemented, ablation-driven (W1 carrier; C0/C1/C2 characterization), 12 focused tests, 2026.09.4 shipped with migrations and bilingual docs. Accepted 2026-09-09; tag and Release published.
- TASK-0006: M0-M2 complete — preregistration frozen before results; E0/E1/E2 ablation run (E0 4/4, E1 4/4, E2 3/4 with the designed false-positive causing the only error). Accepted 2026-09-09 with strictly scoped conclusions: E2 No-Go, E1 Inconclusive, v0 not implemented this cycle (direction not falsified); M3 Blocked, M4 rules draft (no numeric threshold), M5 Blocked + D0-sufficient, M6 deferred.

## Constraints

- Move long execution history to `vault/tasks/*`.
- Demote paused tasks to `vault/parked.md` entries.
- Do not save secrets.
- Keep this file short; current line and entry budgets live in the `trellium-policy` block in `vault/index.md`.

## Recent Changes

- TASK-0016 accepted (2026-09-28): GitHub Release 2026.09.8 is live, non-draft/non-prerelease with empty name/body; releases/latest resolves correctly.
- TASK-0016 active → blocked (2026-09-28): `f9df065` passed 177 tests, clean-clone check 0/0 and CI run 36399329700; lightweight tag 2026.09.8 pushed, but no authenticated Release API/CLI is available.
- Opened TASK-0016 (2026-09-28): owner authorized the 2026.09.8 release with minimal metadata and no promotional notes; local Skill test artifacts remain excluded.
- Owner accepted TASK-0013/0014/0015 (2026-09-20): implementation committed as `7582e7c`; develop push authorized, with tag/Release still out of scope.
- TASK-0015 ready_for_review (2026-09-20): retired the CLAUDE.md project-entry convention across canonical and distributed protocol docs; Claude Skill installation remains supported, 11/11 focused tests pass.
- TASK-0013/0014 final technical review (2026-09-20): exact selected-profile managed set and unified fallback guards close the last release blocker; 177/177 tests, snapshots and whitespace pass; both tasks ready_for_review with owner excluded files untouched.
- TASK-0013 owner review fixes implemented (2026-09-18): formal ablation verdict Inconclusive, unauthorized bilingual contract withdrawn, stamp/Git fail-open and adopt-output regressions closed; 157 tests and snapshots pass, self-check truthfully 2 errors on untouched owner state. Lifecycle remains active; no release actions authorized.
- TASK-0013 draft → active (2026-09-18): M0 preregistration frozen at `docs/evals/adoption-durability-2026-09/` and the reproduction replayed as 6 expected-failure red tests plus a committed+dirty control; no `scripts/`, `init/`, or `skills/` product files touched yet.
- Opened TASK-0013 draft (2026-09-18): fix the reproducible adoption false-health state with a preregistered prompt ablation plus deterministic HEAD/ignore-boundary checks; no automatic Git mutations and no Orion changes in scope.
- Resumed TASK-0004 (2026-09-18) with Orion as the second real local project: first observation is Partial, with one actionable closed-local runtime error and an unclosed tracked durability boundary.
- Owner accepted TASK-0011 (2026-09-18): project work skill No-Go confirmed, direction closed; self-hosting protocol upgraded to 2026.09.7 and pushed (7583707). Focus returns to TASK-0001.
- Released `2026.09.7`: exact-SHA CI run 35076645891 succeeded; tag and Release are public, title-only with empty body, and `releases/latest` resolves to 2026.09.7.
- Owner accepted TASK-0012 by explicit self-acceptance instruction (2026-09-16); Focus returned to TASK-0001. Remote ref lookup was unavailable due execution-platform capacity, so the record relies on owner push confirmation plus local post-commit gates and does not invent remote CI evidence.
- TASK-0012 implemented and ready_for_review: direct AGENTS route + one profile-aware project engineering document; no Vault policy growth or language auto-detection. Review closed root-injection and malformed-stamp fail-open risks; version 2026.09.7, 136 tests, check 0/0, snapshots in sync.
- Opened TASK-0012: convert the owner-observed comment-knowledge loss into a routed, cross-language engineering standard; implementation is gated by a frozen carrier ablation and must not add engineering-policy files to Vault.
- Opened TASK-0011: test whether a thin project-scoped `trellium-work` adds value beyond `AGENTS.md + vault`; only an ablation Go authorizes replacing `agent-task`. The control/work split, global-template leakage fix, cross-Agent discovery evidence, and zero-loss upgrade migration are frozen in the contract.
- TASK-0011: accepted 2026-09-18 — No-Go verdict stands (zero observable gain over AGENTS.md+vault; A1 costs more; Codex project-discovery unverified); leak fix landed (control packages sanitized); direction closed. Independent review APPROVE ×5 rounds total across the two tasks.
- TASK-0011 No-Go closed loop (2026-09-16): ablation verdict recorded; privacy history rewrite executed per owner authorization (8 commits collapsed to one clean commit, 12 sensitive files removed from history, 0-hit full scan, force-with-lease push); after remote CI green the task correctly transitioned ready_for_review.
- TASK-0011 M1 verdict **No-Go** (2026-09-15): both arms zero key omissions / zero corrections / zero hard-metric violations across three scenarios; A1 costs more (visible +79%); Codex project-discovery unverified (retracted from overreach per owner review). Prereg and fixtures frozen at docs/evals/project-work-skill-2026-09/.
- Owner accepted TASK-0010 (2026-09-15): three status-layer fixes closed (check byte-identical, 121 tests, CI green). MIGRATIONS Unreleased section stays — TASK-0010 sits after the `2026.09.5` tag; the 09.5 tag itself is untouched.
- TASK-0010 implemented and ready_for_review (2026-09-14): three status-layer fixes with red-first regression tests (short-row unresolved materialisation, refused-vault joint record, oversplit projection suppression); check byte-identical; snapshot regen after the remote gate caught drift; independent review APPROVE; CI green (7d5c589).
- Owner accepted TASK-0009 (2026-09-13, D-0008) and approved plan B. Executed: bundle+verify → filter-repo ×3 (host paths/UUIDs/repo names/cost fields; the two cost regexes were initially malformed — missing `>` separator — caught by post-scan and fixed in pass-3) → hash-reference migration via composed commit-map → multi-tree 0-hit sensitive scan → gates green → pushed. GitHub Actions had a platform incident (no runs for two pushes); after recovery the re-trigger commit's run completed success. Bundle deleted per owner gate; TASK-0010 draft→active, implementation starting.
- TASK-0009 owner review round (2026-09-13, REQUEST_CHANGES → fixes applied): formal verdict corrected to **Inconclusive** per plan §10.1 cap; v1.4 whitelist strictly applied (4 more Skill sessions voided, 12 valid); recall recomputed on the frozen known-P0/P1 denominator (S1 25% FAIL, S2 100%); privacy/history plan for the unpushed eval transcripts drafted for owner authorization. R2 stays unimplemented this cycle.
- Opened TASK-0009 and drafted the Review Pack R0/R1 ablation plan for GLM; R2 public CLI is gated behind a separate owner-approved Level C task.
- Owner accepted TASK-0008 (final review APPROVE, no open P0/P1/P2): status summary is durable decision D-0007; release sequence in motion — push all commits, wait for develop CI, tag `2026.09.5` on the accepted commit, then the GitHub Release (owner-created if gh stays unavailable). Focus returns to TASK-0001.
- Re-audited the Codex deep-use feedback for 2026.09.5; selected deterministic read-only Status Summary as the sole Go-with-experiments candidate and froze TASK-0008's ablation contract before GLM implementation.
- Installed `trellium-zh 2026.09.4` for Codex and Claude Code, removed the old `agent-native-init-zh` package, and upgraded this project's Vault stamp from 2026.09.3 to 2026.09.4; preserved the measurement-only budget policy and owner-approved the sole semantic merge.
- TASK-0007 accepted; `2026.09.4` tag and Release published.

- 2026.09.4 implemented per the local-task-lifecycle plan (TASK-0007): W-group ablation picked the single-line disposition gate; checker gained local-aware projection (`TASK_RUNTIME_LOCAL_UNRESOLVED` warning, `TASK_RUNTIME_CLOSED_LOCAL` error); 12 focused tests; version/migrations/README/snapshots synced; independent review passed with F1-F3 closed. ready_for_review.
- Owner approved the local TASK lifecycle direction (plan passed R1-R6 review); 2026.09.4 implemented under TASK-0007 (see the 2026.09.4 implemented entry above).
- Owner formally accepted TASK-0005 and TASK-0006 (2026-09-09); TASK-0006 conclusions strictly scoped: E2 No-Go, E1 Inconclusive, v0 not implemented this cycle, direction not falsified; D-0004 unchanged, no Evidence Receipt decision added, M3-M6 not reopened. Focus back to TASK-0001.
- Owner review round 2 (REQUEST_CHANGES) on TASK-0005/0006: six findings fixed — TASK-0005 final gate closed; 12 raw first answers archived; M2 conclusions narrowed (E2 No-Go, E1 Inconclusive, v0 not implemented this cycle, direction not falsified); unsafe untracked golden split; 20 KB threshold removed; D-0004 reconsider_when draft rejected (D0 sufficient).

- TASK-0006 M2 ablation concluded (E1 Inconclusive — cost unmeasured; E2 No-Go — false-positive misled; 0 fresh-mislabels) — Evidence Receipt v0 not implemented this cycle, zero code changes, direction not falsified; M3-M6 conclusions delivered; task ready_for_review.

- Opened TASK-0006 (Level C) from the non-Context optimization plan; experiment preregistration frozen under `docs/evals/non-context-optimization-2026-09/` before any results were collected.
- Drafted the non-Context Vault optimization and ablation plan for GLM handoff; no candidate feature is authorized or implemented, and D-0004 remains unchanged.
- TASK-0005 (owner-mandated evidence-quality fix) ready for review: coverage counts single-sourced into the shadow ledger (D-0005), runtime no longer keeps numeric copies; cold-start Protocol v2 isolated under `docs/evals/cold-start-v2/`.
- Owner adopted the Context No-Go as D-0004 (M4 unauthorized; reopen only via its three conditions); TASK-0004 active → blocked pending the second real project for M2.
- M1 cold-start baseline complete (S1-S7, 7 independent sessions): 7/7 correct, 0 overreach, 0 stale-evidence misuse; M3 No-Go recommendation delivered to owner.

- Opened the post-release validation phase (TASK-0004, Level B): plan formalized at `docs/superpowers/plans/2026-09-08-post-release-validation-plan.md`, M1 cold-start protocol drafted.
- TASK-0002 accepted: owner demoted Release title/notes to a non-gating optional improvement (D-0003); Codex had already verified the release live and moved it blocked -> active.
- Verified the published 2026.09.3 Release and latest resolution; TASK-0002 moved blocked → active, with title/notes completion still pending.
- Pushed the next-cycle work to `origin/develop`; first GitHub Actions run (34181086563) green: `gate` job executed the self-hosting check on push, `sync` job correctly skipped.
- TASK-0003 accepted after review round 2 (canonical K1-K4 mapping and CI scope approved; round 1 findings R1-R6 fixed).
- Accepted the 2026-09-08 GLM plan via the owner's start instruction; created TASK-0003 (Level C, M1+M3 in scope, M4 stays with TASK-0001).
- Reconciled the K1-K4 experiment contract in the shadow ledger (canonical mapping, history preserved); updated TASK-0001 acceptance criteria.
- Added the read-only self-hosting vault check to CI and extended push triggers to `develop`; recorded durable decisions in `vault/decisions.md` (D-0001/D-0002).
- Drafted `docs/superpowers/plans/2026-09-08-agent-native-next-cycle-glm-plan.md` for owner handoff; no checker, CI, release, or governance implementation was performed.
- Adopted Trellium into its own repository (tracked mode, protocol 2026.09.3).
- Created TASK-0001 (self-hosting pilot) and `vault/details/shadow-run-2026-09.md`.
- Unignored `AGENTS.md` and `vault/` in `.gitignore` (user-approved).
- Started TASK-0002 to publish the existing 2026.09.3 tag; corrected K4 setup to measurement-only.

## Known Risks

- Tool boundary (2026-09-14): a Focus line annotated beyond the pure task id (e.g. `- TASK-0010（ready_for_review…）`) is silently ignored by both checker and status — `TASK_ID_RE` strict-matches the whole line and neither tool warns. Seen when an annotated Focus shipped in an acceptance commit; `status .` reported `focus: (none)` while check stayed 0/0. Keep Focus lines to the bare task id.

- `vault/decisions.md` is past the 150-line indexing threshold (7 full records); the protocol says it should become a pure index with bodies under `vault/decisions/`. Restructuring is queued for the owner's confirmation, not silently executed here.
- The PR-only snapshot self-heal push path has not yet been observed in a real GitHub PR run; develop push event routing and the read-only gate have been verified.
- The checker validates the Active Tasks table and structure but cannot see natural-language counts elsewhere; stale prose numbers need manual reconciliation (observed 2026-09-08: "3 TASKs" vs `current_task_files: 4`).
- The 2026.09.3/2026.09.4 Release titles and bodies remain empty; per D-0003 this is an optional improvement, not a risk to machine paths.
- Single-developer pace may produce fewer than 5 real TASKs quickly; coverage grows only with real work, never manufactured.

## Required Checks

```bash
python3 scripts/trellium.py check . --format json
# 范围级 whitespace 检查（owner 裁定 2026-09-13：逐字证据文件豁免，不清理证据本身）：
git diff --check ee4f223..HEAD -- . ':(exclude)docs/evals/review-pack-2026-09/packs/pack-*.md' ':(exclude)docs/evals/review-pack-2026-09/runs/*/prompt.md' ':(exclude)docs/evals/review-pack-2026-09/runs/*/answer.md'
```

豁免说明：`packs/pack-*.md`、`runs/*/prompt.md`、`runs/*/answer.md` 为逐字保存的实验证据（内嵌原始 patch/首答，含原始尾随空格）；清理它们会破坏"逐字存档"的证据承诺。

## Next Steps

- Upgrade Orion to released 2026.09.8, close its local runtime/tracked-boundary findings, and complete TASK-0004 M2 with original-repo and fresh-clone check 0/0 evidence.
- Continue TASK-0001 only as background shadow evidence; it is not the product-development mainline.
- After 2026.09.8 is released, upgrade Orion, remove the accepted TASK runtime row/Focus, establish the tracked core/stamp boundary, run a fresh-clone check to 0/0, and record the final TASK-0004 M2 observation.
- Context implementation stays closed per D-0004; any reopen requires the owner-approved Level C task first.
