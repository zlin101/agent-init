# TASK-0027 - 项目记忆与历史留痕边界复评

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0027",
  "level": "C",
  "authority_level": 1,
  "lifecycle": "ready_for_review",
  "current_slice": "storage-mode-baseline-awaiting-owner-review",
  "gates": {
    "source_verification": "passed",
    "analysis": "passed",
    "documentation_checks": "passed",
    "owner_review": "pending"
  }
}
-->

## Objective

依据最新远端 develop、定位讨论和 owner 提供的三类信息职责，从第一性原理复评项目记忆模型；以旧 Decision 的问题和推理作为证据，产出具体差距及最小调整建议。

2026-10-01 按 owner 的“代码已经合并了，pull一下，根据gpt的文档，梳理一下接下来的计划”追加合并后计划；区分已落地的 TASK-0029 历史保全与仍待验证的功能接续，不启动实现。

## Mode

既有项目协议复评；仅交付讨论文档与必要任务/协作记忆，不进行安装、升级或实现迁移。

## Scope

In scope:

- 核实远端 develop，与本地 HEAD/未提交资料区分。
- 评审 Operational State、Canonical Knowledge、Historical Evidence 的职责及转换边界。
- 对照现有记忆、压缩、治理、review 和 local storage 规则，定位缺口。
- 新增本任务及 `docs/discussions/2026-09-30-memory-boundary-reassessment.md`；必要时记录当前用户的协作纠正信号。
- 2026-10-01 扩展：拉取已合并的 develop，新增 `docs/discussions/2026-10-01-post-history-store-next-steps.md`；按现行 D-0014/TASK-0029 收敛后续顺序，修正 runtime 的过期下一步导航。
- 2026-10-01 后续 steering：分析 owner 提出的 private 默认意向，把默认接入与保全边界纳入计划；仍仅方案分析，不实施模式切换。
- 2026-10-01 最新 steering：先梳理 Private/Local/Tracked 的文件追踪、忽略、边界和管理现状，再由 owner 决定是否及如何优化；新增三模式现状文档，暂停方案选择而非暂停任务 lifecycle。

Out of scope:

- 更改现行 protocol、template、schema、CLI、installer、存储行为或 Decision 状态。
- 实施归档、搬运或删除任何现存资料，选择数据库、服务或备份设施。
- TASK-0026 实施或审查、完整会话采集、跨项目经验检索、commit/push/tag。

## Context Required

- `AGENTS.md`、`vault/index.md`、`vault/runtime.md`、`vault/governance.md`、`vault/collaboration.md`、活跃 TASK-0026 的契约与最新现场。
- 定位讨论、owner 本次目标和建议正文（到第三部分标题）。
- `init/protocol/00-overview.md`、`10-vault.md`、`15-vault-compaction.md`、`20-governance.md`、`80-execution-patterns.md`。
- D-0006、D-0010、D-0012；它们是待检验的历史推理和现状资料。

## Capability Tags

- architecture
- documentation
- agent-governance
- review

## Authority

Allowed:

- 只读核实 GitHub 分支与本地协议，分析并提出建议。
- 2026-10-01 owner 明确授权拉取合并后的代码；允许 fetch、切换到包含当前提交的 develop 并 ff-only pull，保留工作区资料。
- 记录本轮分析文档、任务契约和明确的用户协作偏好；保留已有未提交改动。

Requires approval:

- 把方案变成现行协议、正式治理决策或持久存储/迁移实现；本轮用户只要求复评。

Forbidden:

- 仅凭旧 Decision Active 断定其方案正确，或据此禁止重新推理。
- 将讨论方案伪装成已实施机制、将未跑的场景验证标为通过。
- 自动改写 Decision 状态、对现有资料执行搬运/删除、修改其他任务 ownership、stage/commit/push/tag。

## Acceptance Criteria

- [x] 记录核实的最新 develop SHA，区分未提交的讨论资料。
- [x] 按用户冻结的目标检验三类信息职责，明确文件内部可能同时承载多类内容。
- [x] 用具体协议依据区分已有能力与历史保全契约的缺口。
- [x] 重做 D-0006 关键推理，保留其有价值的问题约束，不更改其状态。
- [x] 给出最小契约、未决边界和待执行的行为验证。
- [x] 文档引用、格式和仓库健康检查已执行并记录。
- [ ] owner 审阅复评建议；不自动 accepted。

## Verification

Required:

- `git ls-remote https://github.com/zlin101/trellium.git refs/heads/develop`
- 文档本地链接核对、`git diff --check`（新文件另做 whitespace 检查）。
- `python3 scripts/trellium.py check . --format json`，记录真实 errors/warnings 与预算测量。

Completed (2026-09-30 historical baseline):

- 远端与本地 HEAD 均为 `a01950a1afab092ae4296b29a00c1b9da74fd7ab`。
- 复评文档 8 个本地链接全部可解析；tracked diff 与两个新文件的 whitespace 检查通过。
- `trellium.py check . --format json`：0 errors / 2 warnings，均为 TASK-0026/0027 尚未纳入 Git 的 `TASK_STORAGE_PENDING`；预算测量已执行，当前策略未配置阈值。
- 源码、现行协议和工具实现未修改，无需运行代码回归；行为验证属于后续方案，不属于本轮通过项。

Completed (2026-10-01 merged baseline):

- `git rev-parse HEAD origin/develop` 两项均为 `6a875d82227b65ab39978e4d281cbd26244c28ef`；实际执行 fetch / switch / ff-only pull，没有重复旧轮的 ls-remote。
- 拉取后 `sync-skills.py --check` PASS，双语 protocol-source in sync；本轮未改生成源或副本。
- 三个本轮文档的 9 个本地链接全部存在，whitespace 与末尾换行检查 PASS；`git diff --check` PASS（未跟踪的新计划另行纳入检查）。
- 文档落盘后 `trellium.py check . --format json`：0 errors / 0 warnings；预算测量已执行，runtime 为 50 lines，当前 policy 未配置阈值；`status` PASS，TASK-0027 保持 ready_for_review / owner_review pending。
- 本轮为计划与记忆更新，不改产品行为；未重跑全量 unittest，也未执行计划中的 Agent 接续实验。TASK-0029 的历史 macOS suite residual 仍按原始验收记录披露。

## Execution Record

### 2026-09-30 - Codex

- 默认 sandbox 的 GitHub 查询因本地代理不可达失败；web 访问也未取得正文。经自动审批允许只读 `git ls-remote` 后核实最新 SHA，未改变工作区或远端。
- 保留 TASK-0026 及其相关已有改动；读取技能与当前协议，现行仓库文本作为本次事实依据。
- 两轮反思记录在复评文档：先核对目标覆盖，再核对最小性与持久存储边界。
- 待定：归档恢复覆盖范围、review 历轮保留粒度、具体存储位置与旧资料处置。
- 本轮停在 proposal-only，下一步由 owner 评审后决定是否形成实施任务。

### 2026-10-01 - 合并后计划 / Codex

- 拉取前工作区干净；feature 分支 HEAD `93c0c8d` 已包含在远端 develop 中。默认 sandbox 写 `.git/FETCH_HEAD` 被拒后，经审批执行 fetch、switch develop 和 ff-only pull；已保存对应窄范围命令授权。
- 本地与远端 develop 同为 `6a875d82227b65ab39978e4d281cbd26244c28ef`（PR #6 合并提交），拉取后工作区干净。
- 依据两份 9 月 30 日归档讨论与当前 D-0014/TASK-0029 写入[后续计划](../../docs/discussions/2026-10-01-post-history-store-next-steps.md)。已询问“GPT 文档”是否另有所指，暂按两份归档材料推进；未推断缺失的建议正文。
- 主线收敛为当前功能事实与证据导航，以及同一实施任务中的实际接续验收；历史 Store 不重做，预存测试问题与 P3 residual 独立排期。
- 此次仅交付建议，不改产品代码、协议、模板、Decision 或 TASK-0029；owner_review 仍 pending，不将 TASK-0029 的接受投射到本任务。

### 2026-10-01 - Private 默认意向 / Codex

- Owner 表达“我打算将 private 设置为默认模式”；暂按新项目首次接入默认推荐理解，已有 policy 与本仓 tracked 模式不变，不将意向伪装成已实施的默认规则。
- 读取 D-0012/D-0014、已接受的 TASK-0019 与 canonical private 接入规则：private 全部 managed material clone-only，且没有 local 的身份绑定与 Store retention。任务历史保全与当前知识恢复是两个独立缺口。
- 已询问 owner 是否仍需 clone 删除后本机历史可找回；答案影响后续持久性、身份与恢复契约，相关实施不先行。计划新增 private 默认方向，先收敛保全边界，再接续验收。
- 已有 tracked carrier 的 preflight 拒绝、forced-add 检测、存量不自动迁移及升级保持 policy 均应保留；private_preflight 的已知损坏 metadata 分类进入后续评估范围。
- 尚未形成新的 Active Decision，不修改 D-0012/D-0014 或已接受 TASK。当前记录属于意向与分析，不写为稳定协作偏好或全局已生效模式。

### 2026-10-01 - 发布意向与历史功能边界 / Codex

- Owner 指示 TASK-0027 结束后应发布新 tag，按 D-0013 保持 tag-only。当前仍有 owner_review 与 private 保全边界未决项，未提前执行 tag/commit/push；最终版本和发布提交需在实际收尾时核对。
- 回答历史功能完整性：TASK-0029 冻结范围内的 local TASK/review 本机保全已实现、独立验收、owner 接受并合并；private 未接入，当前 canonical knowledge 恢复与跨设备/磁盘故障保证不在其实现范围。两项 P3 与预存 macOS suite 失败仍保留披露。
- 本次查阅最终重审证据与任务接受记录，不把历史报告当本轮测试结果，也不把报告当时的 ready_for_review 覆盖任务后来 accepted 的现行状态。

### 2026-10-01 - 三模式现状梳理 / Codex

- Owner 要求先逐项梳理 Private、Local、Tracet，再决定优化；将 Tracet 按现行 `tracked` 理解，最新任务范围为现状分析，不继续默认模式方案选择。前一轮保全偏好问题可留待本次梳理后讨论。
- 核对 canonical Vault/adoption 协议、分发 Skill、stamp inventory、core/local/private checker、task storage 和 upgrade 实现；项目工程文档尚未安装，读取 canonical root 工程约束与 Python profile，沿用已读 Comment Policy。
- 新增[三模式现状](../../docs/discussions/2026-10-01-storage-modes-baseline.md)：给出文件矩阵、ignore 载体、恢复承诺及 Agent/owner/checker 分工。明确 private extras、整个 namespace、外部 raw evidence 未自动覆盖；private canonical 仍不进 Git。
- 区分要求与机械 Gate：核心校验 HEAD，tracked 任务多用 index，ledger 没有 closed TASK 同等未追踪 error；Local 缺 future ignore 为 warning；disposition/retention 不由 checker 自动执行或证明。
- 当前本仓 tracked，默认仍 local；不更改源码、协议、模板、Decision、Git index 或其他任务。未执行新模式行为测试，未 commit/push/tag。
- 已记录 owner 本轮“现状对照后再决定优化”的协作纠正信号；文档/记忆共五文件的本地链接、whitespace、末尾换行与 diff 检查通过，check 0 errors / 0 warnings、status PASS、双语 sync in sync。没有因纯文档分析重跑产品回归。

### 2026-10-01 - Private 未接入 History 的理由复核 / Codex

- Owner 询问缺席的出发点；读取 Private 原实施计划 §1/4.2/7.3、D-0012/D-0014 和 TASK-0029 冻结范围，补充三模式现状文档 §5。
- 区分有记录的事实与解释：private 原本只承诺当前 clone 的 Git 边界；TASK-0029 明确不处理 private；现有身份绑定依赖 tracked project-id。先覆盖默认 local 的缺口属于依据任务顺序推断的分阶段交付解释，不伪造 private 已经被证明无需保全的结论。
- 当前只提出可复评性：私有 Git 可见性不必然排斥本机外存保全。Private 的保存范围、身份持久化/找回与恢复契约仍需另行定义及验证，本轮不采纳方案或修改实现。
- Owner 随后回复“同意”，确认 Git 可见性与本机持久保全可并存、Private 的 clone-only 值得复评；将该共识记入现状与后续计划。下一方案先收敛 Private 历史保全范围、身份及恢复，再讨论默认切换；不把回复扩大为开发授权、完整 Vault 备份方案或 TASK-0027 accepted。

### 2026-10-01 - Private History 实施转交

- Owner 随后明确要求“为private模式增加history的储存方式……跟进”，已另立 [TASK-0030](TASK-0030-private-history-retention.md) 承载授权、实现与测试，不将源码实现混入本分析契约。
- 当前 Private 相关结论已按 D-0015 在工作区扩展；三模式文档保留 6a875d8 分析基线，新增指向实施记录的后续说明。默认选择仍 Local，当前知识备份与自动身份发现未授权扩面。
- TASK-0027 的 owner_review 保持 pending，Private 实施不自动关闭本任务或触发发布；tag-only 收尾意向保留。

## Memory Updates

- 本任务与复评文档保留分析及未决问题。
- `vault/collaboration.md` 补充 owner 对历史 Decision 与当前方案复评的纠正要求。
- 没有新采纳的治理方案，不写新的 Active Decision，也不改旧决策状态；采纳后再将正式结论落到 canonical 位置。
- project-global runtime 事实未变，Focus 保留 TASK-0026；TASK inventory 由任务文件自身承载。
- Durable knowledge disposition: not_applicable（tracked task）。
- 2026-10-01：新增合并后计划；runtime 仅更新合并的项目全局事实及下一步导航，不复制任务 lifecycle/gates。未产生新长期决策或稳定协作偏好，不改 decisions/collaboration；无真实中断，不改 handoff。

## Handoff Requirement

本任务和讨论文档可恢复全部分析；无真实中断和不可推导 transient delta，不更新 handoff。
