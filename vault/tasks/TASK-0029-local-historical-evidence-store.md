# TASK-0029 - Local Historical Evidence Store 正式实施契约

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0029",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "draft",
  "current_slice": "implementation-contract-created",
  "gates": {
    "filesystem_poc": "passed",
    "contract_checks": "passed",
    "implementation": "pending",
    "regression": "pending",
    "distribution_sync": "pending",
    "review": "pending"
  }
}
-->

## Objective

将已验证的 Filesystem POC 收敛为最小正式 Historical Evidence Store：terminal local TASK/review 的结构化证据获得经过校验的 clone-independent retention，同时不产生第二 current truth，不改变 TASK lifecycle，不处理 private。

成功标准是 local 工作 clone 删除后，仅凭稳定 project identity 和 artifact logical identity，可以找回全部 historical versions 并校验原始内容。不是开发日志、Agent runtime、跨设备同步或全量 provenance 系统。

## Ownership / Mode

- Owner 已授权创建正式 implementation TASK；本次交付任务契约及冻结的 POC 证据，不实施产品代码或协议变更。
- 下述实施范围是后续执行契约，创建本文件不自动启动实施、不改变 D-0006 状态、不接受本任务。Owner 指定开始实施后，在此范围推进至 `ready_for_review`。
- 模式：既有协议的限定扩展。当前仓库 TASK storage 为 tracked；本任务自身不改变 storage policy、不自动接入本机正式 Store。
- TASK-0028 的 hot-path routing 是独立工作。共享文件以执行时最新现场为基线，只编辑历史保全相关段落，不覆盖其入口/路由改动。

## Context Required

- 项目 AGENTS、index/runtime/governance/collaboration，本任务与 TASK-0027/0028。
- [定位讨论](../../docs/discussions/2026-09-30-trellium-positioning.md)、[记忆边界复评](../../docs/discussions/2026-09-30-memory-boundary-reassessment.md)，以及本任务下方冻结的正式结论。早期讨论中的未决项以本契约为准。
- [POC 结果](../../docs/evals/historical-evidence-store-2026-09/RESULTS.md)、[POC 实验代码](../../docs/evals/historical-evidence-store-2026-09/history_poc.py)、[POC 测试](../../docs/evals/historical-evidence-store-2026-09/test_history_poc.py)。这是原始实验快照，报告中的 `/tmp` 位置和当时未决项不是正式产品规则。
- canonical `init/protocol/10-vault.md`、`20-governance.md`、`70-adoption-flow.md`、`80-execution-patterns.md`、`init/MIGRATIONS.md`，D-0006/D-0010/D-0012。
- `scripts/trellium.py` 的 adoption/protected-data/check/storage 边界，sync-skills 与双语分发机制，agent-task 工作流。
- 修改源码前读取匹配的 Python engineering profile；涉及 API 表达时并读 Comment/API Documentation Policy。若项目尚未安装对应文件，读取 canonical 协议源中的匹配规范，不擅自安装整个工程规范层。

## Capability Tags

- persistence
- identity
- agent-governance
- python
- testing

## Scope

### In Scope After Execution Authorization

- Store：一个小型标准库 Python 模块及聚焦测试，建议 canonical 路径 `scripts/history_store.py` / `scripts/test_history_store.py`；只提供 put/get/list 和最小 retention 适配，不注册正式 CLI。
- Identity：`vault/project-id` 的首次 local 接入创建、读取/校验、保护与迁移规则；必要且局限的 `scripts/trellium.py` / `scripts/test_trellium.py` 修改。不把身份值复制进 policy 或 install stamp。
- Closure：canonical vault/governance/execution/adoption 段落、项目 agent-task、双语对应模板和必要 Skill 说明，定义 disposition 与 retention 正交的人工/可执行流程。
- 分发：通过现有 sync-skills 管理新 helper 的派生副本及一致性检查，不直接手改 generated snapshots；现有安装方式必须能调用该模块，不增加安装依赖。
- 迁移：`init/MIGRATIONS.md` 最小条目，D-0006 的显式 supersession 与新 decision、decisions 索引，以及与新规则直接冲突的本仓治理/协作说明。保留旧 reasoning 和历史讨论。
- 本任务的实施/验证证据；runtime 仅在 project-global 当前行动确实变化时做必要更新，不写 TASK 状态投影。

### Out of Scope

- SQLite、独立 Git history repo、manifest/index、recovery journal、数据库 schema、全文/向量/图检索、daemon/server。
- 新 TASK/policy/stamp schema 字段，retention enum，sealed/archived/archive_pending/closure_complete，Feature Registry、feature lifecycle、revision counter。
- 正式 archive/history/project-id CLI、自动 fork detection、lineage graph、自动 re-key、批量搬运或删除旧 TASK、Git 自动 stage/untrack/commit/push/tag。
- private retention/privacy 语义、tracked TASK 存储迁移、Decision → Rationale 改名、AGENTS/Profile/CODE_COMMENTS 路由改造。
- cloud、backup scheduler、replication/authentication、多设备 merge、磁盘损坏保证；完整 repo/CI/日志/聊天/tool trace 采集。
- 将 `vault/tasks/archive/` 改为外部持久存储；修复 tasks README 的旧 runtime projection 文案（独立 drift，不混入本任务）。

## Authority

Allowed now:

- 创建本任务、保存原始 POC 证据并运行不修改产品 contract 的核验。

Allowed after execution authorization:

- 在 Scope 内实施、测试、同步分发和记录决策；所有行为测试使用隔离临时项目与 Store。
- 在测试自建的临时 clone 内模拟删除、篡改、权限失败和进程中断；不对真实用户资料执行这些操作。

Requires approval:

- 开始正式实施；范围/环境保证扩大，既有资料回填、真实 local cleanup、显式 re-key，任务 accepted 和 Git 写操作。

Forbidden:

- 覆盖 owner/并行任务改动；静默修复损坏历史、恢复旧 Authority、以历史替换 current canonical truth。
- 将验收成功等同于 retention 成功；Store 失败时删除 source 或回滚业务 accepted。
- 未核验而删除 source；测试访问真实 `~/.trellium/history` 或写入其他项目；伪造通过项。

## Frozen Design

### Project Identity

- 唯一 canonical owner：独立 tracked `vault/project-id`，单行标准 UUID 加换行。Policy、project knowledge、install stamp 不保存第二份身份值；历史 metadata 中的身份仅绑定该 historical record。
- 首次 local 接入创建一次；已有有效值复用，非法值明确失败。clone/rename/workspace relocation/remote URL 改变都不改变身份。
- Upgrade 永不重建或覆盖身份。旧 local 项目首次启用时由 owner 确认绑定；已拥有身份却缺失时要求恢复，不静默生成新身份。
- Owner 明确将 fork/副本视为新逻辑项目时才 re-key；旧 Store namespace 保留，不自动检测或迁移历史。无新 re-key CLI。
- 沿用现有 protected-data inventory 机制；不增加 stamp schema、不保存 identity 副本、不自动 Git 写操作。现有 Git durability 检查继续保护 tracked identity。

### Historical Store

- V1 默认 root：`~/.trellium/history`，必须位于工作 clone 外。仅承诺经过验证 retention 的证据在该 clone 被删除、移动或重建后仍能从本机 Store 找回；不承诺 disk-/machine-independent persistence。
- 环境边界：已验证的本机可信 POSIX filesystem 与 cooperative writers。Windows/NFS 不在此 POC 证明范围，不伪称全面兼容。
- Layout：`<root>/<project-id>/<artifact-id>/<sha256>/{artifact.md,metadata.json}`；每 logical artifact 一个 `.publish.lock`，隐藏 staging 不作为成功记录。
- Version identity：project UUID + artifact logical id + SHA-256(raw bytes)。同 digest 重试幂等，不同 digest 保留第二 immutable version，不覆盖、不增加 revision counter。
- Metadata 仅为 POC 的五项：project_id、artifact_id、digest、archived_at、source_relative_path；不复制 lifecycle、Authority 或 current project state。路径与 metadata 身份一致性必须校验。
- `put(project_id, artifact)` 原子发布；`get(project_id, artifact_id[, digest])` 读取指定版本或列出该 artifact 的版本；`list(project_id)` 从 filesystem 派生并校验，不另建 index。无隐式 latest/current 选择。
- 写 staging → flush/fsync files → fsync staging directory → cooperative per-artifact lock 下 atomic directory publish → fsync publication parent；成功响应前保证必要的父目录创建持久化。现有同版本必须验证，失败后重试重新核验/同步，不以“路径存在”表示成功。
- put 后通过 get 校验 metadata 与完整 bytes/SHA-256；部分写不可见，异常不确认 retention 成功。损坏记录 fail closed，不静默跳过/修复。SHA-256 证明 payload 完整性，不宣称对恶意整体重写的认证。
- 只保存明确纳入范围的 Trellium structured evidence。TASK 与相应 review ledger 分别保持原始内容、路径和内部稳定引用；正常 closure 所需的全部 artifacts 都验证成功才算完成，不要求跨 artifact 事务。部分成功可幂等重试；不得清理尚未完整保全的一组 source。
- Git SHA/CI URL/issue/test command 仅保存引用，不复制其目标；缺少或多版本内部引用不得猜测成 current truth，不新建关系图。

### Closure And Non-authority

```text
active local TASK
→ work / review
→ Durable Knowledge Disposition
→ accepted / superseded
→ Historical Retention
→ Integrity Verification
→ optional local cleanup
```

- Work/Acceptance 的 owner 是 active TASK 的当前 contract 与验收依据；current implementation truth 在 code/tests/API/docs，长期理由在 current canonical knowledge。TASK accepted 只证明当时 Scope/Acceptance 通过。
- Disposition 的 owner 是 TASK Memory Updates，保持 `pending | none | distilled | not_applicable`；none 精确定义为“经检查，本 TASK 没有新增或修订 Canonical Knowledge 的必要，并说明理由”。它不决定历史是否保留。
- Terminal transition 的 owner 仍是 TASK state block。accepted/superseded 足够结束 current contract；terminal 原始 artifact 不再作为 current contract 修改。错误契约可立即 superseded，未完成的 canonical disposition 责任显式交给后续工作。
- Retention 在 terminal 后运行，只覆盖 local；每份 artifact 的 evidence owner 是 immutable Store version。正常 agent-task closure 要求全部必要 copy 经过 get 验证，现实 Store 状态决定是否满足，不持久化新 closure state。
- Retention 失败/不确定：accepted 不回滚、source 保留，明确报告 closure retention 未满足及重试位置；不阻止新业务工作、不静默宣称本次 closure 完成。
- Cleanup 默认不做。仅经明确授权且整组验证完成、source 仍与已保全版本一致时允许删除；cleanup 失败不取消 verified retention。成功 retention 不要求删除 source。
- 极少数 owner 明确豁免作为人工 waiver，与失败区分；不新增字段。历史不进默认 cold-start、不恢复 Authority、不编译为 current TASK、不覆盖 canonical；回溯需要改变当前判断时，走新的工作和 canonical 更新。
- Content role 不按物理文件划分：active TASK 可同时含 Operational contract 和已发生的 Historical execution；review 可同时含 open finding 和 fixed/wont-fix evidence。terminal 后整份 artifact 成为历史，不为角色拆分 duplicate file。

### Migration

- 既有 local active TASK：身份绑定后在下一次 closure 应用新 retention；既有 terminal TASK 只在 owner 授权后回填，不批量删除、不宣称丢失材料可恢复。
- 既有 tracked TASK 原样保留，private 不进入 Store；本仓不为实现测试创建正式 project-id 或更改 storage_mode。
- D-0006 保留原问题、约束和 reasoning 作为历史；实施新 decision 后显式 supersede 其旧解法，不删除正文。
- 继续成立：local 不进 project Git、canonical unique owner、历史不授予 Authority/默认读取、长期知识 semantic distillation。
- 明确废止：not tracked ⇒ disposable；historical retention ⇒ second truth；distilled ⇒ original evidence may disappear。新原则：Local describes repository visibility, not retention policy。
- Fresh local adopt 创建唯一身份；upgrade 保留身份和用户资料，存量首次启用遵循确认绑定。`vault/tasks/archive/` 保持 repo 内 compaction 职责。

## Execution Plan

1. **M0 — Baseline**：重读 TASK-0028 与工作区，冻结本次涉及文件的当前内容；确认 execution authorization，跑现有 baseline，不把历史测试数当当前通过项。
2. **M1 — Store**：从冻结 POC 提炼标准库模块，保留 atomic publish/lock/hash/immutable 语义；先通过七类 failure cases，补齐产品边界的路径、父目录 sync 和错误传播检查。
3. **M2 — Identity / Distribution**：最小接入/保护逻辑与双语 helper 分发；验证 adopt/clone/upgrade/re-key 语义、缺失身份处理以及 Git durability 边界，不改 CLI/schema。
4. **M3 — Closure / Migration**：更新唯一 canonical 定义与必要投放面，接通 local closure 的可执行 retention 路径；校验 TASK+review 全部成功才 closure，partial success 可重试，private/tracked 不被触发。记录新 decision 并保留 D-0006 历史。
5. **M4 — Verification / Review**：回归、sync、check/status、两轮 coverage/minimality 复核；逐项记录结果与限制，停在 `ready_for_review`。Owner 决定 accepted/提交。

## Acceptance Criteria

- [ ] 身份只有一个 canonical owner；tracked/clone/rename/remote/upgrade 不改变 UUID，非法/缺失值不静默生成替代身份。
- [ ] 七类 POC failure cases 在正式模块上通过：retry、multi-version、真实中断、同/异内容并发、clone deletion、tamper、unavailable store。
- [ ] put/get/list 维持最小 API；所有成功 records 完整且可校验，失败不删除 source，无隐式 current/latest 语义。
- [ ] local TASK+review closure 实际可执行；整组 retained/verified 才完成，部分成功重试安全，accepted 与 retention failure 正交，无新 lifecycle/state。
- [ ] none 的 canonical-only 含义准确；历史不参与 default cold-start、不恢复 Authority，不产生 Feature Registry。
- [ ] 默认不 cleanup；获授权 cleanup 只发生于 verified、未变化的 source，失败可报告并保留数据。
- [ ] private/既有 tracked 存储边界不变，repo archive 与 external Store 正交，不测试写入真实用户 Store。
- [ ] D-0006 显式 superseded 且原 reasoning 留存；新原则、迁移要求、双语分发一致，无共享文件改动丢失。
- [ ] 必要回归、仓库健康检查、独立 review 完成；环境/failure-domain 限制与真实新增 LOC/dependency/format 数量报告清楚。
- [ ] Owner 接受交付；不自动 accepted。

## Verification

Required for implementation:

- 正式 Store 单元/多进程 failure tests；POSIX fixture 内执行 SIGKILL、权限不可写、clone 删除与精确 bytes 验证。
- Identity adopt/upgrade/missing/corrupt/existing/fresh-clone fixture；local closure、review partial success/retry、private/tracked 不触发，以及未授权 cleanup 的反例。
- `python3 -m unittest discover -s scripts -p 'test_*.py'`。
- `python3 scripts/sync-skills.py --check`，核对 helper 与协议派生副本一致。
- `python3 scripts/trellium.py status . --format json` / `check . --format json`，记录真实 findings 与预算测量；新增文件 whitespace/链接检查及 `git diff --check`。
- 端到端 fixture 验证已分发 Skill 的调用路径，不只测试 canonical 模块；不将本文计划或原 POC 通过数替代正式测试证据。

Completed for contract creation:

- 原 disposable POC 13 tests PASS；这是实验结果，不是正式实现 gate。
- 保存原 POC 三文件的 byte-identical 快照；SHA-256 分别为：implementation `712d3e81268662636b1485397ed57c0467ebd83373c0dbd72057522b1f67abd6`，tests `62c1abc272ebd9281343ca4ad30e428a67246f2796eaccc1ae86f6f4a6ab3229`，RESULTS `4b1579b91f3ac5667b15eb853518dfcc6bc085c1716e072306b10c8eff0eec10`。
- 在固定证据目录运行 `python3 -m unittest -v test_history_poc`：13/13 PASS，exit 0，0.702 seconds；确认实验迁入仓库后仍可独立回放。
- `check`：0 errors / 3 warnings，均为 TASK-0027/0028/0029 尚未纳入 Git 的 `TASK_STORAGE_PENDING`；预算测量完成。`status` 正确识别 TASK-0029 为 draft，Focus 仍为 TASK-0028。
- `git diff --check` 与四个新增文件的 whitespace、结尾换行、Markdown 本地链接检查通过。
- 尚未开始实施，生产 LOC 尚未实测。设计预计约 250–400 新增 code SLOC（Store、identity、closure glue），仅为估计，不作为验收阈值。

## Execution Record

### 2026-09-30 - Codex - Contract Creation

- Owner 授权创建正式 implementation TASK。Filesystem PASS 已冻结，停止 SQLite/Git backend research。
- 新增本契约与原 POC 的固定证据副本；不修改产品协议、正式代码、storage policy、身份或 D-0006 状态。
- Coverage 复核：identity、retention/acceptance、failure domain、七类实验、迁移与唯一 owner 均有明确验收；TASK 与 review 的成组失败采用 source retention + 幂等重试，无额外事务模型。
- Minimality 复核：新增持久格式仅单值 identity 和五项历史 metadata；无 TASK/policy/stamp schema 扩展、无 lifecycle、无依赖/DB/index/manifest/正式 CLI。备份、多设备和通用 provenance 留在 scope 外。
- 已知限制：POC 是可信本机 POSIX cooperative writers 实验；fsync 顺序和 SIGKILL 不等于物理断电/磁盘损坏证明，cleanup 依赖 terminal source 不被并发修改。

## Memory Updates

- 本契约承载正式实施目标与批准边界；固定实验资料承载过去的验证依据，不替代 canonical 协议。
- 实施时新 decision supersede D-0006 并更新冲突的 current 规则；本次仅创建，不提前改写决策状态。
- Runtime Focus 保留 TASK-0028，本任务不向 runtime 写 inventory/状态投影；全局当前行动变化后再更新。
- Durable knowledge disposition: not_applicable（tracked task）。

## Handoff Requirement

本任务、实时工作区和固定 POC 证据足以恢复。无真实中断及不可推导 transient delta，不创建 handoff。
