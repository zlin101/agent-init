# TASK-0027 - 项目记忆与历史留痕边界复评

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0027",
  "level": "C",
  "authority_level": 1,
  "lifecycle": "ready_for_review",
  "current_slice": "proposal-only-awaiting-owner-review",
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

## Mode

既有项目协议复评；仅交付讨论文档与必要任务/协作记忆，不进行安装、升级或实现迁移。

## Scope

In scope:

- 核实远端 develop，与本地 HEAD/未提交资料区分。
- 评审 Operational State、Canonical Knowledge、Historical Evidence 的职责及转换边界。
- 对照现有记忆、压缩、治理、review 和 local storage 规则，定位缺口。
- 新增本任务及 `docs/discussions/2026-09-30-memory-boundary-reassessment.md`；必要时记录当前用户的协作纠正信号。

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

Completed:

- 远端与本地 HEAD 均为 `a01950a1afab092ae4296b29a00c1b9da74fd7ab`。
- 复评文档 8 个本地链接全部可解析；tracked diff 与两个新文件的 whitespace 检查通过。
- `trellium.py check . --format json`：0 errors / 2 warnings，均为 TASK-0026/0027 尚未纳入 Git 的 `TASK_STORAGE_PENDING`；预算测量已执行，当前策略未配置阈值。
- 源码、现行协议和工具实现未修改，无需运行代码回归；行为验证属于后续方案，不属于本轮通过项。

## Execution Record

### 2026-09-30 - Codex

- 默认 sandbox 的 GitHub 查询因本地代理不可达失败；web 访问也未取得正文。经自动审批允许只读 `git ls-remote` 后核实最新 SHA，未改变工作区或远端。
- 保留 TASK-0026 及其相关已有改动；读取技能与当前协议，现行仓库文本作为本次事实依据。
- 两轮反思记录在复评文档：先核对目标覆盖，再核对最小性与持久存储边界。
- 待定：归档恢复覆盖范围、review 历轮保留粒度、具体存储位置与旧资料处置。
- 本轮停在 proposal-only，下一步由 owner 评审后决定是否形成实施任务。

## Memory Updates

- 本任务与复评文档保留分析及未决问题。
- `vault/collaboration.md` 补充 owner 对历史 Decision 与当前方案复评的纠正要求。
- 没有新采纳的治理方案，不写新的 Active Decision，也不改旧决策状态；采纳后再将正式结论落到 canonical 位置。
- project-global runtime 事实未变，Focus 保留 TASK-0026；TASK inventory 由任务文件自身承载。
- Durable knowledge disposition: not_applicable（tracked task）。

## Handoff Requirement

本任务和讨论文档可恢复全部分析；无真实中断和不可推导 transient delta，不更新 handoff。
