# D-0002 - Self-hosting vault check 进入 CI 门禁（2026-09-08）

Status: Active

## Decision

`.github/workflows/skill-sync.yml` 在 PR 与 push（`main`、`develop`）上运行只读 `python3 scripts/trellium.py check . --format json`；checker error（exit 2）使 job 失败，warning 保持既有 exit-0 语义。权限按事件最小化：写权限（`contents: write`、`pull-requests: write`）仅存在于 PR 专用 `sync` job（self-heal 所需）；push 专用 `gate` job 无 job 级权限提升，只继承 workflow 级 `contents: read`。CI 不修改 `vault/`。

## Rationale

本仓库以 tracked 模式自托管 Trellium，vault 结构漂移应在合并前机械可见；同时分支 push 不需要任何写 token，单一 job 携带写权限属于不必要的暴露面。

## Alternatives

- 独立新 workflow：被否，最小修改原则，避免第二套触发面。
- 单一 job 承载 PR 与 push：被否（review round 1 R1），`permissions` 只能按 job 声明，单 job 无法让 push 事件摆脱写权限。
- warning 也使 job 失败：被否，擅自加严会改变 checker 既有退出码语义。

## Impact

向 `develop` 或 `main` 推送前先在本地跑同一命令；CI 报 error 时修 vault 结构，而不是放松门禁；后续改 workflow 时保持"push 路径零写权限"不变。
