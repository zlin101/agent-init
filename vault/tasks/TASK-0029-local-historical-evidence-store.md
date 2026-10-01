# TASK-0029 - Local Historical Evidence Store 正式实施契约

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0029",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "accepted",
  "current_slice": "owner-accepted",
  "gates": {
    "filesystem_poc": "passed",
    "contract_checks": "passed",
    "implementation": "passed",
    "regression": "passed",
    "distribution_sync": "passed",
    "review": "passed"
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
- 2026-09-30 owner 本轮仅授权修订 review 指出的契约问题；此前“不要开发”仍有效。此次修订不启动实施，implementation/regression/distribution_sync/review gates 保持 pending。

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
- 按 owner 本轮指令修订本任务契约及审查记录，补齐 review 保留顺序、身份绑定流程和正式验收环境；不修改产品代码、canonical 协议、分发模板或 Decision 状态。

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

首次 local 接入的 Agent-native 顺序固定为：owner 选择 local → `adopt` 补齐协作层 → Agent 写入 local policy 和窄范围 TASK ignore → 调用 bundled 可执行身份 helper → 运行 check → owner 控制核心 Git 提交及 fresh-clone 验证。Helper 不注册 CLI，只在明确 local policy 下执行；tracked/private 不触发身份创建或 Store 接入。

- Helper 负责读取/校验或获授权首次创建 `vault/project-id`，并将该路径以 `data` role 登记进现有 stamp `files` inventory。登记使用既有 schema，不新增字段、不复制 UUID；只创建文件但未完成登记不算接入完成。双语 Skill 必须给出实际可执行的 helper 调用路径。
- 有有效文件时复用并补齐 inventory；文件非法、非普通文件或路径不安全时失败，不重写。文件缺失且当前 inventory 或 Git HEAD 已记录该路径时，要求恢复原身份，首次绑定授权也不得绕过此保护。
- 文件缺失且没有上述已绑定证据时，仅允许明确的首次绑定：fresh 接入的计划须说明身份创建，存量 local 首次启用须取得 owner 绑定确认。不能仅凭文件不存在就认定 fresh；证据检查失败或是否曾绑定不确定时保留现场并请求确认。无需增加 fresh/bound 状态字段。
- 身份创建后 inventory 写入失败时保留身份文件，报告接入未完成；重试复用同一 UUID 并补登记，不生成替代值。重复 adopt、baseline、upgrade 必须保留已有 inventory 条目；upgrade 不执行首次绑定，已登记身份缺失时明确要求恢复。

### Historical Store

- V1 默认 root：`~/.trellium/history`，必须位于工作 clone 外。仅承诺经过验证 retention 的证据在该 clone 被删除、移动或重建后仍能从本机 Store 找回；不承诺 disk-/machine-independent persistence。
- 环境边界：已验证的本机可信 POSIX filesystem 与 cooperative writers。Windows/NFS 不在此 POC 证明范围，不伪称全面兼容。
- 正式模块最低解释器为 Python 3.9；必要验收组合为本机 macOS / Python 3.9.6 与 Linux / Python 3.12.3，各自使用可信本地 filesystem。两组均须在正式模块上获得七类 failure cases 和已分发调用路径的证据；这是待验证矩阵，不把原 Linux POC PASS 宣称为 macOS 或正式模块已通过。其他解释器/OS/filesystem 组合不因“POSIX”名称自动取得验证结论。
- 正式测试不得依赖 Linux `/proc/self/fd` 来证明通用 fsync 顺序；用跨两组环境可运行的观测方式核对 file/staging/publication/ancestor sync，记录实际 OS、解释器和 filesystem。保持原 POC 三文件不变，不以修改实验快照消除兼容性失败。
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
- Local review 收敛时可将结论写入 TASK Execution Record，但原 ledger 必须保留在原路径，含已有各轮 findings、处置、理由与证据引用；不执行现行“收敛后不再单独保留”的删除动作。TASK terminal 后将 TASK 与相应 ledger 作为一组分别保全/get 验证；整组成功前任一 source 都不得删除，成功后也只有明确 cleanup 授权才可移除。tracked/private 不因本条触发外部 retention。
- Closure 在写 Store 前确定必要 artifact 集合：TASK 必选，已开展 ledger review 的相应 ledger 必选；若从 TASK 执行记录/稳定引用可知存在必要 ledger 而原文件缺失，报告材料缺口，不按“当前只找到 TASK”宣称整组完成。无 ledger review 的任务允许 TASK 单独成组并说明依据；不新增 manifest 或 TASK 字段。
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

- [x] 身份只有一个 canonical owner；tracked/clone/rename/remote/upgrade 不改变 UUID，非法/缺失值不静默生成替代身份。（修复批次 4 独立重审 F29-002 fixed：lstat 三态分类，查询失败 unknown；真实错误注入下身份文件不存在、stamp bytes 未变，双平台通过）
- [x] 首次 local 接入实际按 policy → 身份 helper → protected inventory → check 执行；首次绑定与身份丢失可区分，登记失败重试复用原 UUID，重复 adopt/baseline/upgrade 不丢失保护条目。（F29-002/F29-003 fixed；双平台 19 identity tests、所有原反例与独立结构分类 fixture PASS）
- [x] 七类 POC failure cases 在正式模块上通过：retry、multi-version、真实中断、同/异内容并发、clone deletion、tamper、unavailable store。（macOS 3.9.6，15/15）
- [x] put/get/list 维持最小 API；所有成功 records 完整且可校验，失败不删除 source，无隐式 current/latest 语义。（修复批次 2 独立重审 F29-001 fixed：bootstrap 失败重试补同步，构造守卫拒绝更深缺失祖先且无写入，双平台 Store 20 tests 与原反例均通过）
- [x] local TASK+review closure 实际可执行；整组 retained/verified 才完成，部分成功重试安全，accepted 与 retention failure 正交，无新 lifecycle/state。（分发副本 E2E + canonical 定义）
- [x] Review 收敛后原 ledger 持续保留至 terminal retention；删 clone 后 TASK 与 ledger 原始 bytes、路径和稳定引用可核验。必要 ledger 缺失不得静默退化为 TASK-only 成功。（helper/流程语义由 canonical 10-vault 定义 + retain E2E 覆盖成组保全）
- [x] none 的 canonical-only 含义准确；历史不参与 default cold-start、不恢复 Authority，不产生 Feature Registry。（10-vault/governance 措辞 + metadata 五项边界）
- [x] 默认不 cleanup；获授权 cleanup 只发生于 verified、未变化的 source，失败可报告并保留数据。（retain_terminal 语义 + 测试）
- [x] private/既有 tracked 存储边界不变，repo archive 与 external Store 正交，不测试写入真实用户 Store。（helper 拒绝非 local；本仓未创建 project-id）
- [x] D-0006 显式 superseded 且原 reasoning 留存；新原则、迁移要求、双语分发一致，无共享文件改动丢失。（D-0014 + MIGRATIONS + 快照 sync）
- [x] 必要回归、仓库健康检查、独立 review 完成；环境/failure-domain 限制与真实新增 LOC/dependency/format 数量报告清楚。（修复批次 4 独立重审 APPROVE，findings 全关闭；双平台 39 聚焦 tests、结构分类和 E2E PASS；macOS 全量 257/258，唯一 FAIL 仍为预存 fixture，保留 residual；最终 LOC/dependency/format 测量见 batch4 evidence）
- [x] 正式模块及分发调用在 macOS / Python 3.9.6 与 Linux / Python 3.12.3 验收组合均通过；测试不依赖 `/proc`，未执行组合保持未验证，不以兼容性 skip 充当 failure gate PASS。（macOS 3.9.6：store 20 + identity 19 聚焦例；Linux 3.12.3：store 20/20 + identity 19/19 + 双语分发副本 E2E（含 bootstrap `.trellium` 布局），环境 Linux 7.0.14-orbstack aarch64 / git 2.39.2 / overlayfs / 非 root 用户，修复批次 4 后复跑，详见台账 Round 7）
- [x] Owner 接受交付；不自动 accepted。（2026-10-01 Owner 明确确认“验收通过是吧，那我这也通过”）

## Verification

Required for implementation:

- 正式 Store 单元/多进程 failure tests；POSIX fixture 内执行 SIGKILL、权限不可写、clone 删除与精确 bytes 验证。
- Identity adopt/upgrade/missing/corrupt/existing/fresh-clone fixture；local closure、review partial success/retry、private/tracked 不触发，以及未授权 cleanup 的反例。
- Identity 接入顺序 fixture：实际 bundled adopt 后写 local policy，再调用身份 helper；覆盖首次绑定、存量确认绑定、inventory/HEAD 已登记但文件丢失、证据查询失败、身份创建后登记失败及重试。确认重复 adopt/baseline/upgrade 不丢 inventory，UUID 不进入 policy/stamp 身份副本。
- Review 全链路 fixture：多轮 ledger 收敛 → 结论并入 TASK 但保留 ledger → TASK terminal → 两份分别 put/get → 删除临时 clone → 按项目/各 artifact logical identity 找回并逐 bytes 核验。补必要 ledger 缺失和第二 artifact 保全失败的反例，验证不报告 closure 成功、不提前 cleanup、accepted 不回滚，重试可完成。
- 在上述两组 OS/解释器验收组合执行正式 failure tests 和分发端到端 fixture；fsync 顺序观测须兼容两组，原始结果注明 OS/解释器/filesystem。环境不可用或 gate 未执行时明确报告缺证据，不自行扩大承诺或降为可选。
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

Completed for implementation（2026-09-30，macOS / Python 3.9.6）：

- 分支 `task-0029-history-evidence-store`（自 develop `756c496`）。全量 `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh scripts.test_history_store`：244 tests，唯一失败为 M0 已确认的预存环境失败 `AgentInitTest.test_keeps_original_target_when_ancestor_is_swapped_after_open`（干净 HEAD 复现的 macOS TOCTOU fixture，与本任务无关，未修改）。
- 正式 Store（`scripts/history_store.py`，221 code SLOC）+ 聚焦测试（`scripts/test_history_store.py`，367 code SLOC）：15/15 PASS。POC 七类 failure cases 全覆盖；fsync 顺序观测改为模块钩子包装（`_write_file`/`_sync_dir`/`os.rename`），无 `/proc` 依赖；新增产品边界测试：artifact/project namespace 隔离、importlib 不注册 sys.modules 的分发加载路径。新第三方依赖 0。
- `ProjectIdentityTest` 11/11 PASS：policy 门（tracked/private/缺失/损坏 index 拒绝）、首次绑定授权门、canonical UUID 严格校验（大写/多行/无换行/非法/symlink fail closed 且不改写）、binding evidence 恢复门（stamp inventory 与 Git HEAD 两路）、Git 查询失败 fail closed、登记失败保留身份文件且重试复用同 UUID、重复 adopt 保留登记、upgrade plan protected 且不提案、baseline 不登记、注册身份进入 core storage Git durability 门。
- 分发 smoke（`test_skill_preflight_command_smoke` 扩展为双 helper）：对两个语言包各执行 packaged-script adopt → 写 local policy → 运行 SKILL 内嵌的 `ensure_project_identity` 真实命令（--create 与复用两种），保留 private_preflight 原 clean/tracked 断言；PASS。
- E2E fixture（真实命令行、分发副本 `skills/trellium-zh/assets/history_store.py`、SKILL 的 importlib 调用方式）：正例——TASK+ledger 成组 retain+verify → 删除 clone → 仅凭 project UUID + artifact id 找回并逐 bytes 核验；反例——第二 artifact 保全失败不报告整组成功且 source 全保留、幂等重试可完成；必要 ledger 文件缺失时报告材料缺口、不退化为 TASK-only 成功。均 PASS。
- `sync-skills.py --check` in sync；`cmp` 确认双语内嵌 `assets/trellium.py` 与 `assets/history_store.py` byte-identical；generated snapshots 由 sync 重新生成。
- `check . --format json`：0 errors / 0 warnings；`status`：Focus TASK-0028 resolved，TASK-0029 ready_for_review；`git diff --check` 与新增文件 whitespace/末尾换行检查通过。
- 环境限制：Linux / Python 3.12.3 组合本机不可用（docker daemon 未运行），未执行、保持未验证，不宣称通过；fsync 顺序观测为模块调用序观测，非硬件 durability 证明（与 POC 限制一致）。
- 实测新增：`history_store.py` 221 + `test_history_store.py` 367 code SLOC；`trellium.py` +216/-7（身份 helper 与管理集集成）；`test_trellium.py` +300/-16（身份测试与 smoke 扩展）；`sync-skills.py` +31/-10。全 diff 32 文件修改 +5 新增，+1171/-91 行（含文档/快照）。schema/lifecycle/dependency 变化 0。

Completed for review fixes (2026-09-30，独立验收 REQUEST_CHANGES 后)：

- macOS / Python 3.9.6：全量 `scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh scripts.test_history_store` 252 tests，唯一失败仍为 M0 预存环境失败（ancestor-swap TOCTOU，干净基线复现）；sync/check(0/0)/status/diff 通过；内嵌副本 byte-identical。
- Linux / Python 3.12.3（F29-004）：Docker `python:3.12.3`（daocloud 镜像拉取），代码拷入容器本地 overlayfs、非 root 用户执行：`test_history_store` 17/17、`ProjectIdentityTest` 16/16、分发副本 importlib 加载 + TASK+ledger 成组 retain→删 clone→找回 E2E，均 PASS。环境：Linux 7.0.14-orbstack aarch64 / git 2.39.2 / overlayfs。初跑 readonly 用例失败为容器 root 绕过权限位所致（非产品缺陷），改非特权用户后通过。
- 修复新增测试：ancestor 三级同步失败重试 + 并发不绕过（store +2）；git 不可用 / rev-parse operational failure / monorepo prefix unknown / 无提交仓库可绑定（identity +4）；严格 policy 解析六反例（identity +1）。
- 本轮未再修改后重新生成快照；`sync-skills.py --check` 确认双语派生副本 in sync。

Completed for review fixes round 2 (2026-10-01，二轮重审 REQUEST_CHANGES 后)：

- F29-001 剩余边界：`_sync_namespace` 重确认链延伸至 `root.parent.parent`（bootstrap 目录如 `~/.trellium` 的 dirent 持久化层），固定结构链、不用 per-put 新建列表；`Store.__init__` 拒绝 bootstrap 之上祖先缺失的 root（无法有界确认的布局显式 `ValueError`，不再静默不健全）。
- F29-002 剩余边界：`_identity_in_head` 删除全部 no-commit stderr 子串；HEAD 不可解析时用 `git rev-list -n 1 --all` 结构探针——仅 Git 确认零修订（rc=0 且空输出）才判可证明 unborn；仓库仍有修订（含 corrupt/unreadable ref）、探针失败、Git 缺失均 unknown 拒绝。非仓库分类保留。
- 测试：store +3（bootstrap 层首次同步失败→重试补同步、bootstrap 已存在时成功路径仍重同步该 link、深缺失祖先构造拒绝）；identity +1（corrupt HEAD ref 反例）并修正一个既有测试前提（rev-parse 操作失败语义需在有修订仓库中验证）；双语分发快照重新生成，`cmp` byte-identical。
- macOS / Python 3.9.6：全量 256 tests，255 PASS / 1 预存 FAIL；store 20 + identity 17 聚焦全 PASS；sync/check(0/0)/diff PASS；ruff 对两分发面产品文件本轮新增行零告警（预存风格项不扩面清扫）。
- Linux / Python 3.12.3 / overlayfs / 非 root：store 20/20、identity 17/17、双语分发 E2E PASS；按 reviewer 复现格式独立复跑两反例均翻转：F29-001 `first put failed, bootstrap visible: True / retry success: True / failed parent fsync retried: True`；F29-002 `Needed a single revision` stderr 下 `replacement created: False` 且无替换文件落盘（git 2.39.2）。
- 未 commit/push；未触碰 reviewer 证据文件（`docs/evals/historical-evidence-store-2026-10-rereview/`）与 owner 未提交改动；停 ready_for_review 待重审。

Completed for review fixes round 3 (2026-10-01，三轮重审后唯一剩余 P1)：

- F29-002 最后分支：corrupt `.git/HEAD` 使 Git 报 `not a git repository`（与从未初始化目录同文本）。非仓库分类改由 `_has_git_metadata(target)` 祖先链结构探测门控：`os.path.lexists` 含 `.git` 目录/指针文件/损坏 symlink → unknown 拒绝；链上无任何 `.git` 条目才可判可证明非仓库；不可读路径 fail closed。stderr 完全退出绑定证明。
- 测试：identity +1（corrupt `.git/HEAD` 反例，先钉住误导性 stderr 文本再断言拒绝且无写入）；真实非仓库正例（完整 adopt fixture）保持 PASS；双语分发快照重新生成，`cmp` byte-identical。
- macOS / Python 3.9.6：全量 257 tests，256 PASS / 1 预存 FAIL；store 20 + identity 18 聚焦全 PASS；sync/check(0/0)/diff PASS。
- Linux / Python 3.12.3 / git 2.39.2 / overlayfs / 非 root：store 20/20、identity 18/18、双语分发 E2E（含 bootstrap `.trellium` 布局）PASS；reviewer 反例独立复跑翻转：stderr 含 `not a git repository` → `replacement created: False`、无替换文件；恢复原 HEAD 后原 UUID 可读回（证明 metadata 在，unknown 是正确处置）。
- 未 commit/push；未触碰 reviewer 证据与 owner 未提交改动；停 ready_for_review 待重审。

Completed for review fixes round 4 (2026-10-01，四轮重审后唯一剩余 P1)：

- F29-002 最后分支：`os.path.lexists` 内部吞 OSError 返回 False，不可读祖先被读作“确认不存在”。改为 `_proven_without_git_metadata` 直接 `os.lstat` 三态分类——条目存在 → False；`FileNotFoundError` → 继续探测；其它 `OSError`/`resolve()` 失败 → None；仅全部祖先确证无条目才判可证明非仓库。调用方仅 True 放行首次绑定，其余一律 unknown 拒绝。
- 测试：identity +1（真实 adopted fixture，非仓库 stderr + `.git` lstat PermissionError 双注入 → 拒绝、无身份文件、stamp bytes 未变）；corrupt-HEAD 与真实非仓库/零修订正例保持 PASS；双语分发快照重新生成，`cmp` byte-identical。
- macOS / Python 3.9.6：全量 258 tests，257 PASS / 1 预存 FAIL；store 20 + identity 19 聚焦全 PASS；sync/check(0/0)/diff PASS；本轮新增行 ruff/lens 零告警。
- Linux / Python 3.12.3 / git 2.39.2 / overlayfs / 非 root：store 20/20、identity 19/19、双语分发 E2E PASS；reviewer 注入格式独立复跑确认翻转。
- 未 commit/push；未触碰 reviewer 证据与 owner 未提交改动；停 ready_for_review 待重审。

## Execution Record

### 2026-09-30 - Codex - Contract Creation

- Owner 授权创建正式 implementation TASK。Filesystem PASS 已冻结，停止 SQLite/Git backend research。
- 新增本契约与原 POC 的固定证据副本；不修改产品协议、正式代码、storage policy、身份或 D-0006 状态。
- Coverage 复核：identity、retention/acceptance、failure domain、七类实验、迁移与唯一 owner 均有明确验收；TASK 与 review 的成组失败采用 source retention + 幂等重试，无额外事务模型。
- Minimality 复核：新增持久格式仅单值 identity 和五项历史 metadata；无 TASK/policy/stamp schema 扩展、无 lifecycle、无依赖/DB/index/manifest/正式 CLI。备份、多设备和通用 provenance 留在 scope 外。
- 已知限制：POC 是可信本机 POSIX cooperative writers 实验；fsync 顺序和 SIGKILL 不等于物理断电/磁盘损坏证明，cleanup 依赖 terminal source 不被并发修改。

### 2026-09-30 - Codex - Contract Review And Revision

- Owner 明确要求先不开发，随后授权 review 并修订本契约；此次只修改任务文档和协作观察，不启动 implementation，不变更现行协议、D-0006、storage policy 或真实身份。
- R29-1（P2，fixed in contract）：补齐 local review 收敛后保留原 ledger、terminal 后整组保全/验证的顺序；必要 ledger 缺失不得报整组成功，并要求全链路与失败 fixture。
- R29-2（P2，fixed in contract）：补齐 adopt 后 local policy → 身份 helper → protected-data inventory → check 的流程；明确首次绑定、已绑定身份丢失、登记失败重试及重复接入/升级保护边界。
- R29-3（P2，fixed in contract）：冻结正式模块 Python 3.9 下限和 macOS 3.9.6 / Linux 3.12.3 验收组合；正式测试移除 `/proc` 依赖，原 POC 快照保留。原 POC 在本机 Python 3.9.6 导入时因 `str | None` 抛 TypeError，未执行任何实验用例；原 Linux 13/13 仅为历史证据。
- 修订前只读核验：POC 三文件 SHA-256 与本契约完全一致；sync/check/status/diff checks 通过，check 为 0 errors / 0 warnings，TASK-0029 仍为 draft。契约问题修订不等于正式实现或独立 implementation review 通过。
- 修订后核验：`sync-skills.py --check`、`check/status --format json`、`git diff --check`、文档 whitespace/末尾换行/本地链接检查通过；check 为 0 errors / 0 warnings。状态块 schema/Authority/lifecycle/gates 与 HEAD 一致，仅更新 slice；POC 三文件与 HEAD byte-identical。本轮无产品行为变化，不重跑代码回归，正式两组环境验收尚未执行。

### 2026-09-30 - PI - Implementation

- Owner 指令“go，新建分支开发”构成本轮 execution authorization；分支 `task-0029-history-evidence-store` 推进 M0–M4，停在 ready_for_review；除 owner 指令的分支创建外无 Git 写操作，未 commit/push。
- M1 Store：从冻结 POC 提炼标准库模块；`from __future__ import annotations` 解除 3.9 导入失败；保留原子发布/per-artifact lock/SHA-256 不可变/fail closed 语义；补齐父目录逐级 sync 与错误传播。
- M2 Identity/Distribution：`ensure_project_identity` helper（无 CLI，private_preflight 同模式）＋ stamp 管理集集成＋ adopt/upgrade 保留登记；sync-skills 新增 `assets/history_store.py` 派生与 drift 检查。E2E 发现并修复真实 3.9 缺陷：`@dataclass` + future annotations 在“importlib 加载且不注册 sys.modules”路径（即 SKILL 调用方式）崩溃——Artifact 改为普通 frozen 类并新增回归测试。
- M3 Closure/Migration：10-vault 新增「Historical Evidence 保留（local）」节与 project-id 职责；20-governance 验收门增 local retention 规则；80 改为“结论归档、原 ledger 保留”；70 增 local 接入身份绑定步骤；MIGRATIONS Unreleased 条目；双语 agent-task 模板新增 retention 步骤并重编号；双语 Skill local 接入补身份 helper 与 retention 可执行路径；D-0014 新 decision、D-0006 显式 superseded（原 reasoning 保留）、索引更新；collaboration 中与“可丢弃”直接冲突的现行表述更新（owner 未提交改动未触碰）。
- M4 验证：结果见上方 Completed for implementation；停在 ready_for_review，owner 决定 accepted/提交；独立 review 未发生，review gate 保持 pending。
- 与契约的必要偏差（均记录在案）：①预存 lint 机械修复——sync-skills.py import 排序与 `write_snapshot` rmtree try/except、trellium.py import 排序与 `suppress(FileExistsError)`、test_trellium.py import 排序（均为既有风格问题，因文件进入本轮修改面而暴露，行为等价）；②分发 smoke 从单命令扩展为双命令（新 helper 示例进入 SKILL 后，原“抽取第一个 python3 -c”的测试契约需覆盖两者）；③D-0006 supersession 以引用块注记置于正文顶部，正文逐字保留。
- 已知遗留：zh agent-task 模板第 9 行与 repo SKILL 第 18 行存在 TASK-0028 遗留的一词 drift（“非可推导 delta” vs “非可推导 transient delta”），属并行任务历史现场，本轮未触碰；Linux / Python 3.12.3 验收组合未执行（缺环境，待有环境补跑）。

### 2026-09-30 - Codex - Independent Acceptance Review

- Owner 提供 Dual Review Loop default-profile PASS 后要求独立验收；本轮按 TASK 冻结契约验收，不把 loop 的 residual 分类替代必要 acceptance gates。当前产品变更仍为原 37 项；仅新增本次 review 台账并回写任务验收结果，未修产品、commit/push 或访问真实 Store。
- 裁决 REQUEST_CHANGES：隔离临时 fixture 新复现 F29-001（P1，父目录 fsync 失败重试漏同步）、F29-002（P1，Git 不可用时替换 HEAD 原身份）、F29-003（P2，helper 接受 checker 拒绝的重复 policy 键）；F29-004（P2）为契约必需的 Linux 3.12.3 正式验收缺证据。findings/repro/验证边界记录在 `vault/tasks/TASK-0029-review.md`，均 open。
- Fresh 验证：四模块全量 245 tests，244 PASS / 1 FAIL（与实施前本机基线相同的 ancestor-swap fixture）；正式 Store 15 tests 包含在本次执行中且全部通过。sync/check/status/diff checks PASS，check 0 errors / 0 warnings；两语言 packaged Store 的 TASK+ledger 部分失败/重试/删临时 clone 后 bytes 与来源路径找回 smoke PASS。新增反例显示既有测试未覆盖全部冻结失败边界，故 implementation/regression 为 partial，review 为 blocked；lifecycle 保持 ready_for_review，不自动 accepted。
- 原报告 F001/F002 的 P3 residual 不作为本轮阻塞；新发现的 correctness 问题和 Linux 缺证据独立阻塞。Linux 未在本轮执行；原 POC Linux PASS 不能替代正式模块与分发调用证据。后续修复批次需新增聚焦测试、sync 并重新验收。

### 2026-09-30 - PI - Review Fix Round

- Owner 独立验收（Codex，台账 TASK-0029-review.md）判 REQUEST_CHANGES：2×P1 + 1×P2 + Linux 验收阻塞。本轮为单一 writer 修复批次，修后停回 ready_for_review 等 owner 重审；未 commit/push。
- F29-001：`Store._sync_namespace` 在 put 成功路径对 artifact/project/root/root.parent 全链重确认；新增三级 ancestor 同步失败重试测试与他人创建 namespace 不绕过同步的测试。
- F29-002：`_identity_in_head` 严格证据分类——Git 不可用/操作失败/monorepo prefix 失败均返回 unknown 并由恢复门拒绝；仅非仓库与无提交仓库（含 `Needed a single revision` 实测 stderr）为可证明无绑定；新增四个边界测试。
- F29-003：policy 解析改用 canonical `extract_comment_blocks` + `parse_block_object` + `validate_policy_object`，恰好一块 + 严格语义；六类反例测试（重复键/非对象/JSON 常量/非法值/多块/未闭合）。
- F29-004：Linux / Python 3.12.3 验收完成（容器内 overlayfs、非 root、daocloud 镜像）；store 17/17、identity 16/16、分发 E2E 通过。环境设置曾耗时过长（官方镜像拉取与容器内 apt 均慢），改用国内镜像后解决；用户纠正已记入流程（优先国内镜像）。
- 台账 F29-001–004 已批量回写 fixed/resolved 及证据；原 F001/F002 保持 P3 residual 未动。

### 2026-10-01 - Codex - Independent Re-review

- 按 owner 修复汇总和“继续”指令增量重审原四项 finding，未修改产品代码。结论仍 REQUEST_CHANGES：F29-001/F29-002 reopened（2×P1），F29-003 fixed、F29-004 resolved；这是原失败边界未补齐，不是新增 strict profile 或扩大 scope。
- F29-001：`.trellium` 自身首次创建后同步 `<home>` 失败，重试在 `root.parent` 停止而漏同步该父目录，却返回成功；F29-002：真实 Git 损坏 HEAD ref 也报 `Needed a single revision`，helper 随后创建并登记与已提交身份不同的 UUID。两项均在自建临时 fixture 的 macOS/Linux 组合复现；具体输入、源码 fingerprints、fixture 和实际输出保存在 [独立重审证据](../../docs/evals/historical-evidence-store-2026-10-rereview/RESULTS.md)，台账保留前轮复现和修复作者历史记录。
- macOS Python 3.9.6：全量 252 tests，251 PASS / 1 预存 ancestor-swap FAIL；33 聚焦 tests PASS。Linux Python 3.12.3：现有 Docker 镜像、禁用网络、非 root、容器本地 overlayfs，33 聚焦 tests PASS；两组双语分发 E2E 均 PASS。F29-004 独立证据已补足，不再是环境 blocker；通过数不替代两个新增反例的观察。
- implementation/regression 回到 partial、review blocked，lifecycle 保持 ready_for_review；未 accepted、commit/push、真实 retention/cleanup 或清理 Docker 镜像。Runtime 移除已过时的 Linux 缺环境描述与 TASK 状态投影，当前 gates/证据仅在任务和台账维护；不改 Focus。

### 2026-10-01 - PI - Review Fix Round 2

- 二轮重审（Codex，台账 TASK-0029-review.md）将 F29-001/F29-002 reopened：两个 P1 各剩一个边界。本轮单一 writer 修复批次，修后停回 ready_for_review 等 owner 重审；未 commit/push。
- F29-001：重确认链从 `root.parent` 延伸至 `root.parent.parent`，覆盖默认布局 `.trellium` 新建时 `<home>` 层 dirent 的持久化；重试与协作 writer 场景均由固定结构链覆盖（无内存新建列表）；新增构造守卫拒绝更深缺失祖先的 root，把“无法有界确认”变成显式错误而非静默成功。
- F29-002：识别出 `Needed a single revision` 同为无提交与 corrupt ref 的输出——放弃 stderr 子串证明，改用 `git rev-list -n 1 --all` 结构探针；只有 Git 自身确认零修订才允许首次绑定，corrupt HEAD + 已有提交 → unknown → 拒绝。reviewer 复现条件（loose ref 写 `corrupt ref\n`）在 Linux 独立复跑确认翻转。
- 修复中发现既有 `test_rev_parse_operational_failure_fails_closed` 前提随新语义漂移（空仓库中注入失败会被结构探针正确判为可绑定）——按其本意改为有修订仓库中验证操作失败拒绝，意图更精确；非同义改写，理由记录在案。
- 台账 F29-001/F29-002 回写第二轮 Fix/Verification 与 Round 3 Fresh Verification；gates 复位 implementation/regression passed、review pending。

### 2026-10-01 - Codex - Independent Re-review of Fix Batch 2

- F29-001 fixed：独立确认原 bootstrap 失败重试补同步，接受构造时更深缺失祖先的显式 ValueError；20 Store tests 双平台 PASS，保留新拒绝路径的披露。F29-002 的原 loose-ref 反例也已拒绝；有提交 fixture 的前提修正符合结构探针目标。
- 唯一 blocker 为 F29-002 reopened（P1）：已提交身份、stamp 未登记、working-tree identity 缺失时，把 `.git/HEAD` 内容改为 `corrupt head\n`，Git 报 `not a git repository`，helper 按非仓库立即创建并登记替代 UUID。恢复原 HEAD 可读回原 UUID。macOS Git 2.54.0 与 Linux Git 2.39.2 均复现，故非仓库字符串尚不是无绑定证明；需补 Git metadata 损坏的 unknown 分类与无写入测试，保留真实非仓库/零修订正例。
- 独立 fresh 验证：macOS Python 3.9.6 全量 256 tests，255 PASS / 1 预存 ancestor-swap FAIL；两平台各 37 聚焦 tests、双语分发 E2E PASS。Linux 为现有 Python 3.12.3 Docker 镜像、禁用网络、non-root、容器本地 overlayfs。源码 fingerprints、实际输入和完整 Linux 输出保存于 [batch 2 独立证据](../../docs/evals/historical-evidence-store-2026-10-rereview/batch2-RESULTS.md)，未改写前轮证据。
- gates 为 implementation/regression partial、review blocked，lifecycle 仍 ready_for_review；未修改产品、accepted、commit/push、真实 Store 或镜像。F29-003/F29-004 保持关闭；任务与台账持有当前验收结果，runtime 无 project-global 新事实，不重复投影。

### 2026-10-01 - PI - Review Fix Round 3

- 三轮重审：F29-001 fixed 被接受；唯一剩余 P1 为 corrupt `.git/HEAD` —— Git 连 `not a git repository` 都会报出，旧非仓库 stderr 分类仍会生成替代 UUID。本轮单一 writer 修复批次，修后停回 ready_for_review；未 commit/push。
- 修复：非仓库判定改结构探测门控（`_has_git_metadata` 祖先链 `.git` 条目检查，`os.path.lexists` 含目录/指针文件/损坏 symlink），stderr 子串完全退出绑定证明；损坏/不可读既有 Git metadata 一律 unknown 拒绝，链上无任何 `.git` 条目的目录才可首次绑定；不可读路径 fail closed。
- 执行期发现：`private_preflight`（L2308）同一 stderr 分类仍在，但其为 pre-adopt 只读探测、写路径仍由 `_identity_in_head` 把守（corrupt metadata 下 policy 门放行后 identity 门拒绝），本轮不扩面修改，留待后续任务评估。
- 验证：identity +1（corrupt `.git/HEAD` 反例，先钉住误导性 stderr 文本再断言拒绝且无写入）；双平台 38 聚焦 tests、双语分发 E2E（含 bootstrap 布局）PASS；reviewer 复现格式独立复跑（Linux/git 2.39.2）：stderr 含 `not a git repository` → `replacement created: False`、无替换文件，恢复原 HEAD 后原 UUID 可读回（metadata 在，unknown 是正确处置）；真实非仓库正例保持可用。macOS 全量 257 tests，唯一 FAIL 仍预存。
- 台账 F29-002 回写第三轮 Fix/Verification 与 Round 5 Fresh Verification；gates 复位 implementation/regression passed、review pending。

### 2026-10-01 - Codex - Independent Re-review of Fix Batch 3

- 损坏 `.git/HEAD` 原反例已正确拒绝，loose-ref/ bootstrap 反例保持修复，真实非仓库/无提交正例通过；private_preflight 未扩面。独立双平台各 38 聚焦 tests、双语 E2E PASS。macOS Python 3.9.6 全量 257 tests，256 PASS / 1 预存 ancestor-swap FAIL。
- 仅 F29-002 reopened（P1）：`os.path.lexists` 会将 lstat 的 OSError 吞掉并返回 False，外层 except 无法实现所声明的不可读路径 unknown。只对临时项目 `.git` lookup 注入 PermissionError，真实 Git 已报非仓库的损坏 HEAD 场景下 detector 返回 False，helper 写入并登记不同 UUID，stamp bytes 改变；恢复 HEAD 原 UUID 可读。Linux Python 3.12.3 / Git 2.39.2 / overlayfs / non-root 与 macOS 均复现。仅明确不存在可继续探测祖先，其他 lookup 错误需 unknown 且无写入。
- 源码 fingerprints、fixture、原始 Linux 输出新增至 [batch 3 独立证据](../../docs/evals/historical-evidence-store-2026-10-rereview/batch3-RESULTS.md)，此前证据保持原内容；台账与 gates 回写 implementation/regression partial、review blocked，lifecycle 仍 ready_for_review。未修改产品、accepted、commit/push、真实 Store 或镜像，无 project-global runtime 新事实。

### 2026-10-01 - PI - Review Fix Round 4

- 四轮重审：corrupt `.git/HEAD` 分支已接受关闭；唯一剩余 P1 为 `os.path.lexists` 内部吞 OSError 返回 False，查询失败与不存在不可区分。本轮单一 writer 修复批次，修后停回 ready_for_review；未 commit/push。
- 修复：`_has_git_metadata` 重构为 `_proven_without_git_metadata`，直接用 `os.lstat` 保留错误类型三态分类——查询成功且条目存在 → False（metadata 在，unknown 拒绝）；`FileNotFoundError` → 本层确证不存在，继续祖先探测；其它 `OSError`（PermissionError/ENOTDIR/ELOOP 等）与 `resolve()` 失败 → None（unknown）。仅全部祖先确证无条目才返回 True；调用方仅 True 读作可证明非仓库，其余一律拒绝。修复批次 3 的“不可读路径 fail closed”意图至此真正实现。
- 测试：identity +1（`test_unqueryable_git_metadata_fails_closed`：真实 adopted fixture，非仓库 stderr 注入 + `.git` lstat PermissionError 注入 → 拒绝、身份文件不落盘、stamp bytes 未变）；corrupt-HEAD（entry 存在语义）与真实非仓库/零修订正例保持 PASS。
- 验证：双平台 39 聚焦 tests、双语分发 E2E PASS；reviewer 注入格式独立复跑（Linux/git 2.39.2）确认翻转；macOS 全量 258 tests，唯一 FAIL 仍预存。台账 Round 7 Fresh Verification 已记录，gates 复位 implementation/regression passed、review pending。修复过程中将新代码的 except 结构改为单 except + isinstance + else 以消除静态分析争议，行为不变。

### 2026-10-01 - Codex - Independent Re-review of Fix Batch 4

- **APPROVE**：F29-002 fixed，其他三个独立验收 findings 保持关闭。直接 lstat 的三态语义与调用方门控符合 required fix；原 PermissionError 注入现在 unknown，拒绝创建，身份文件不存在且 stamp bytes 未变。目录/gitfile/broken symlink/明确不存在/多种 OSError/resolve OSError 的独立分类 fixture PASS；原 corrupt HEAD/loose-ref 与 bootstrap 反例均保持修复。
- Fresh 验证：macOS Python 3.9.6 与 Linux Python 3.12.3 / Git 2.39.2 / overlayfs / non-root 各 39 聚焦 tests PASS，双语分发 E2E PASS；macOS 全量 258 tests，257 PASS / 1 预存 ancestor-swap FAIL。全量命令仍是 FAIL，不作全绿声明；范围内 regression 与 review passed，原 P3/validation residual 保持披露。最终 fixture、原始 Linux 输出、源码 fingerprints 和 LOC/dependency/format 测量新增至 [batch 4 独立证据](../../docs/evals/historical-evidence-store-2026-10-rereview/batch4-RESULTS.md)，以前证据不覆盖。
- 最终 canonical 新文件物理行：Store 292、Store tests 523；相对 HEAD 的脚本 diff：trellium +308/-8、identity 等 tests +496/-16、sync +31/-10。第三方依赖 0；两类持久表示（单行 UUID identity、五字段 metadata），TASK/policy/stamp schema、lifecycle 与正式 CLI 变化 0，derived copies 和 review fixture 不计新增产品实现。
- review gate 回写 passed，current slice 为 review-approved-awaiting-owner-acceptance，lifecycle 保持 ready_for_review；AC 仅 Owner 接受交付未勾选，不自动 accepted、commit/push 或清理镜像。本轮只写验收证据/任务/台账，无 project-global runtime 新事实，不重复状态投影。

### 2026-10-01 - Owner Acceptance

- 独立验收 APPROVE、findings 全关闭且源码 fingerprints 未变化后，Owner 明确确认“验收通过是吧，那我这也通过”，接受当前交付；全部 Acceptance Criteria 勾选，lifecycle 转 accepted，gates 全部 passed。
- 原两个 P3 residual 与预存 macOS ancestor-swap fixture 失败保持已披露的非阻塞风险；该接受不改写历史验证结果。本仓 tracked policy 保持原样，TASK/review ledger 与全部审查证据保留；不触发 external retention、cleanup、归档搬运或 Git 写操作。
- 仅记录本次接受决定，无新的产品原则或长期 decision；不新增 runtime TASK 投影或 handoff。提交、推送及发布仍须 Owner 另行明确指令。

## Memory Updates

- 本契约承载正式实施目标与批准边界；固定实验资料承载过去的验证依据，不替代 canonical 协议。
- 实施时新 decision supersede D-0006 并更新冲突的 current 规则；本次仅创建，不提前改写决策状态。
- Runtime Focus 保留 TASK-0028，本任务不向 runtime 写 inventory/状态投影；全局当前行动变化后再更新。
- Durable knowledge disposition: not_applicable（tracked task）。
- 本轮三项 findings、修订依据与执行边界持久化在本任务；“先 review/修订，尚未开发”的当前协作纠正记入 `vault/collaboration.md`，不推断为所有任务的永久确认要求。
- 2026-10-01 独立重审的两项 reopened findings、处置边界与双环境证据记录在任务/原 review ledger 和 `docs/evals/historical-evidence-store-2026-10-rereview/`；未新增长期决策，未修改产品原则或原 POC 快照。
- 修复批次 2 的独立重审更新同一任务/台账，并新增 batch2 fixture/结果；F29-001 已关闭，仅 F29-002 非仓库分类待修。无新的 canonical 原则或长期 decision，原历史证据不覆盖。
- 修复批次 3 的独立重审新增 batch3 fixture/结果，并更新同一任务/台账；F29-002 剩余 metadata lookup 错误分类持久化，不新增 canonical 原则或长期 decision，不覆盖此前历史证据。
- 修复批次 4 的独立重审新增 batch4 fixture/最终结果；全部 findings 关闭，原始 ledger 与各批次历史证据保持保留。2026-10-01 Owner 已显式接受交付，决定记录在 Execution Record；无新的 canonical 原则/decision。

## Handoff Requirement

本任务、实时工作区和固定 POC 证据足以恢复。无真实中断及不可推导 transient delta，不创建 handoff。
