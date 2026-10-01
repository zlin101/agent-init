# Runtime Context

## Current Phase

Post-2026.09.9 convergence CLOSED and `2026.09.10` published tag-only; Profile knowledge ablation committed as `77ee022`. Round 3 hot-path routing ablation accepted and closed out: scoped multi-TASK commit + push executed under explicit owner authorization (TASK-0028 plus parallel tracked materials). TASK-0029 is merged into develop; owner accepted Private History delivery and authorized the `2026.10.0` tag-only publication. TASK-0027 planning remains separate.

## Focus

- TASK-0033

Focus is navigation only. It owns no lifecycle, Authority, slice, Gate, or active-task inventory; `trellium status` reads TASK state directly from task files.

## Current Progress

- Round 3 review is closed: routing dedup and runtime trim retained; Level A index-skip remains No-Go, so the default reading set is unchanged. No remaining Round 3 implementation.
- Local/Private 已共享本机 History Store：Private 身份 ignored、显式恢复 UUID，目标 managed material 不进 Git；Local仍为推荐，首次接入明确选择门见D-0017（尚未发布）。本仓仍 tracked，未接入真实 Store；History实现与验证证据见 TASK-0029/0030。

## Constraints

- Preserve owner changes and never include `vault/.agent-init.json` or `docs/engineering/` in TASK-0019.
- Do not operate on Orion or any other repository.
- Publish future Trellium versions by tag only; do not create GitHub Releases or release prose (D-0013).
- Require explicit `install.sh --version`; unversioned installs fail closed before any network access (TASK-0024 removed latest-release resolution).
- Decision-state changes require owner confirmation; this compaction is structural only.
- Private must not weaken TASK-0013 durability/security gates for tracked/local projects or use hidden Git index state.

## Recent Changes

- 2026-10-01: Owner 接受首次项目接入明确选择storage的交付并授权提交/推送任务分支；未答只读、已有选择复用、既有policy保留，Local仍推荐，无全局模式；D-0017与证据见TASK-0033，新版Skill尚未发布。
- 2026-10-01: 2026.10.1 新 tag 已发布；Codex 中文 Skill 已从该 tag 重装，旧09.1外置备份，实际包84项聚焦+3项E2E通过；原10.0保留，证据及发现边界见 TASK-0032。
- 2026-10-01: 项目 starter workflow 名称改为 Trellium Work，已随 develop 推送并纳入2026.10.1 tag；安装包仍 trellium / trellium-zh，旧项目的显式迁移与检查兼容见 TASK-0031 / D-0016。
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

- 2026.10.1 已发布并完成本机中文包重装/实际包兼容验证；交付证据见 TASK-0032，运行态 Skill 发现需下一turn。旧项目迁移规则见 TASK-0031 / D-0016，2026.10.0 保留不改写。
- 后续整体方向见[合并后计划建议](../docs/discussions/2026-10-01-post-history-store-next-steps.md)；默认切换与当前知识恢复分别评估。Owner 已另行授权本次 Private History 的 `2026.10.0` tag-only 发布；TASK-0027 规划审阅单独推进。
