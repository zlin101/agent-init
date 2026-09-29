# Handoff

只用于近期中断或转交工作，最多保留 3 条交接。不要当作永久日志。
每条交接以任务编号命名；无任务编号时用 SESSION。更早的交接在压缩时按任务编号归并进对应任务文件。

分支、HEAD、脏文件在恢复时通过 Git 现场读取；不要把实时 Git 状态当权威记录。可选保留一条带观察时间、明确标注为历史观察的环境快照。累计计数（TASK/转换/handoff 等）不在 handoff 保存：条目中的数字仅为撰写时点快照，权威来源是 `vault/details/shadow-run-2026-09.md` 的 append-only 事件行与 dated 汇总（D-0005）。

## TASK-0019

- Objective: implement strict private storage without weakening tracked/local durability or security.
- Completed: owner direction, ablation/red-team, final M0-M5 plan and Level C contract; M0 reworked through review rounds 1-3 and approved in round 4: `PrivateStorageModeTest` in `scripts/test_trellium.py` now 6 green + 24 expectedFailure red tests (policy v2 normalization, reverse privacy gate, marker integrity/identity, non-anchored/out-of-target patterns, checker-side tracked-carrier, three independent fingerprinted preflight tests — tracked AGENTS.md reject / isolated tracked profile carrier reject / untracked positive control, each with pre-adopt worktree+index+HEAD+exclude fingerprints, profile exact-ignore + forced-add, check/status goldens); marker-stripped self-check: 21 assertion failures + 3 AttributeErrors, 0 unexpected successes; 207/207 suite OK; product `trellium.py` unchanged; no open P0/P1/P2.
- In progress: none; M0 commit authorized, M1 not started.
- Kill Gates: both PASSED with reviewable evidence in `docs/evals/private-mode-kill-gates-2026-09/` (protocol/prompts/results/runs): Gate 1 — fresh Codex CLI 0.158.0 and Claude Code 2.1.263 sessions discovered ignored/untracked AGENTS.md (AGENTS.md not in index; index tracks only README), exit 0, sentinel quoted, Codex session id redacted; Gate 2 — the deliberate `git add -f` is the only index write (it IS the tested violation); the detection phase is read-only (`git ls-files --cached`/`status --porcelain`), `check-ignore` alone provably blind; no hooks.
- Contract frozen in M0: exclude block via `git rev-parse --git-path info/exclude`; identity is Git-root-relative target, `.` for repo-root (PI freeze, owner may veto); base patterns `/AGENTS.md`, `/vault/`, `/skills/agent-task/`, `/.agent-init-backup/` + exact stamp paths (profile docs included); monorepo `/<prefix>/...` anchored; block must be unique/well-formed/uncrossed/identity-matched; checker detection and the pre-adopt preflight (`agent_init.private_preflight(target, profiles=())`, PI-frozen shape) are both write-free, tracked carriers rejected explicitly.
- Next best action: begin M1 policy v2 normalization and remove the three policy-red markers in the same implementation change.
- Files to read first: `vault/tasks/TASK-0019-private-storage-mode.md` (round-3 rework record), `docs/evals/private-mode-kill-gates-2026-09/results.md`, `scripts/test_trellium.py` (`PrivateStorageModeTest`), `docs/superpowers/plans/2026-09-28-private-storage-mode-plan.md`.
