# D-0014 - Local Historical Evidence Store（2026-09-30）

Status: Active

## Background

TASK-0027 记忆边界复评与定位讨论确认：Operational State、Canonical Knowledge、Historical Evidence 三类职责中，历史证据尚未获得贯穿关闭、保全、查找与恢复的持久性契约。D-0006 曾把 local TASK 定义为私有、可丢弃的工作日志，并以"制造第二事实源"为由否决自动发布/归档。其仓库负担与防越权目标仍然成立，但两条推导不充分：私有与低仓库负担不推出允许丢失历史材料；保留带时间与来源的历史版本也不必然建立第二个当前事实 owner。

## Decision

- 新原则：**Local describes repository visibility, not retention policy。** local TASK/review 在 terminal 后经本机 Historical Store 获得 clone-independent retention；tracked/private 的存储语义不变。
- 项目身份的唯一 canonical owner 是 tracked 单行 `vault/project-id`：首次 local 接入由 bundled 身份 helper 创建，并以 `data` role 登记进版本戳 inventory；clone/rename/workspace relocation/remote URL 变化不改变身份；已有绑定证据而文件缺失时要求恢复，不静默生成替代身份；升级永不重建或覆盖；fork 作为新项目须 owner 显式 re-key。
- Store：标准库 filesystem 模块（默认 root `~/.trellium/history`，位于工作 clone 外），`project-id/artifact-id/sha256` 布局，原子目录发布 + per-artifact flock + SHA-256 不可变版本；metadata 仅五项，不复制 lifecycle、Authority 或当前状态；无 index/manifest/CLI/lifecycle 扩展。已验证域为本机可信 POSIX filesystem 与 cooperative writers。
- Closure：Durable Knowledge Disposition 与 Historical Retention 正交。local terminal 的 TASK 与已开展 review 的 ledger 成组 put/get 验证，整组成功才算 retention 完成；失败保留 source、不回滚 accepted、幂等重试；cleanup 仅 owner 明确授权且 source 未变化时执行。历史不进默认 cold-start、不恢复 Authority、不编译为 current TASK。

## Rationale

Filesystem POC（13 个真实进程失败用例）证明最简方案满足 clone 删除后按身份找回并核验原始 bytes 的目标；SQLite、独立 Git history repo、manifest 均无必要。"第二事实源"风险由约束化解——历史不授予 Authority、不参与默认读取、metadata 不携带当前状态——而不是靠丢弃证据。

## Alternatives

- 维持 D-0006 的 disposable 语义：被否，历史证据无法恢复，且把"仓库可见性"与"保留策略"错误捆绑。
- SQLite/独立 history repo：被否，POC 证明 filesystem 足够，额外基础设施引入新故障域。
- 自动 cleanup：被否，删除 source 永远需要 owner 明确授权。

## Impact

实施于 TASK-0029：`scripts/history_store.py` + `ensure_project_identity` helper + 双语分发（`assets/history_store.py`）。正式验收组合为 macOS / Python 3.9.6 与 Linux / Python 3.12.3；未执行组合不宣称通过。存量项目不自动回填；既有 tracked TASK 原样保留；`vault/tasks/archive/` 保持 repo 内 compaction 职责，与 external Store 正交。D-0006 显式 superseded，其原问题、约束与 reasoning 保留作为历史证据。
