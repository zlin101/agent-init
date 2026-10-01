# Runtime Context

## Current Phase

Post-2026.09.9 convergence CLOSED and `2026.09.10` published tag-only; Profile knowledge ablation committed as `77ee022`. Round 3 hot-path routing ablation accepted and closed out: scoped multi-TASK commit + push executed under explicit owner authorization (TASK-0028 plus parallel tracked materials). TASK-0029 is merged into develop; owner accepted Private History delivery and authorized the `2026.10.0` tag-only publication. TASK-0027 planning remains separate.

## Focus

- TASK-0032

Focus is navigation only. It owns no lifecycle, Authority, slice, Gate, or active-task inventory; `trellium status` reads TASK state directly from task files.

## Current Progress

- Round 3 review is closed: routing dedup and runtime trim retained; Level A index-skip remains No-Go, so the default reading set is unchanged. No remaining Round 3 implementation.
- Local/Private 已共享本机 History Store：Private 身份 ignored、显式恢复 UUID，目标 managed material 不进 Git；双语已同步，默认仍 Local。本仓仍 tracked，未接入真实 Store；实现与验证证据见 TASK-0029/0030。

## Constraints

- Preserve owner changes and never include `vault/.agent-init.json` or `docs/engineering/` in TASK-0019.
- Do not operate on Orion or any other repository.
- Publish future Trellium versions by tag only; do not create GitHub Releases or release prose (D-0013).
- Require explicit `install.sh --version`; unversioned installs fail closed before any network access (TASK-0024 removed latest-release resolution).
- Decision-state changes require owner confirmation; this compaction is structural only.
- Private must not weaken TASK-0013 durability/security gates for tracked/local projects or use hidden Git index state.

## Recent Changes

- 2026-10-01: Owner 授权 2026.10.1 新 tag 与 Codex 中文 Skill 重装/兼容验证；旧 09.1 包已备份，原 10.0 tag 保留，范围和执行证据见 TASK-0032。
- 2026-10-01: 项目 starter workflow 名称改为 Trellium Work，owner 已授权随 develop 提交推送（尚未纳入版本 tag）；安装包仍 trellium / trellium-zh，旧项目的显式迁移与检查兼容见 TASK-0031 / D-0016。
- 2026-10-01: Private History 交付与 `2026.10.0` tag-only 发布授权已记录；版本号及双语分发随提交同步，默认仍 Local，未接入真实 Store。
- 2026-10-01: Historical Evidence Store 经 PR #6 合入 develop；D-0014 与 canonical retention/身份规则已进入主开发线，双语分发已同步，当前协议与历史讨论应分开读取。
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

- 改名与旧项目显式迁移见 TASK-0031 / D-0016；新路径与 stamp 协调提交到 develop，真实 HEAD Gate 在提交后核对。已发布 2026.10.0 不改写，Owner 已另行授权 2026.10.1 发布及本机重装，见 TASK-0032。
- 后续整体方向见[合并后计划建议](../docs/discussions/2026-10-01-post-history-store-next-steps.md)；默认切换与当前知识恢复分别评估。Owner 已另行授权本次 Private History 的 `2026.10.0` tag-only 发布；TASK-0027 规划审阅单独推进。
