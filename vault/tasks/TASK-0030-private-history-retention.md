# TASK-0030 - Private History 保全

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0030",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "accepted",
  "current_slice": "owner-accepted",
  "gates": {
    "implementation": "passed",
    "regression": "passed",
    "distribution_sync": "passed",
    "owner_review": "passed"
  }
}
-->

## Objective

让 Private 的 terminal TASK/review 获得与 Local 相同的本机外部 History 保全，同时保持所有目标项目 managed material 不进入 Git。当前知识仍留在 private Vault，不把历史恢复为当前契约或 Authority。

## Scope

- 按[实施计划](../../docs/superpowers/plans/2026-10-01-private-history-retention-plan.md)扩展 bundled 身份 helper 的 Private 接入，复用 Store、身份文件与现有 stamp schema。
- 补 Private 身份创建/复用/丢失保护、privacy gate、失败重试、双语分发与删临时 clone 找回的测试及文档。
- 更新 canonical protocol、对应中英文模板/Skill、README、MIGRATIONS 与新 Decision；派生副本只由 sync-skills 生成。

Out of scope：默认模式切换、完整 Vault 备份、自动项目发现/绑定/重建、新 CLI/schema/数据库/index/服务、云同步、真实身份创建/历史回填/cleanup、Git index/commit/push/tag；不修改已接受 TASK-0019/0029。

## Context Required

- AGENTS、index/runtime/governance/project/collaboration，TASK-0027 最新分析及授权记录。
- D-0012/D-0014、TASK-0029 的冻结 Store 与身份规则，Private 原实施计划及三模式现状文档。
- canonical root 工程约束、Python profile 和 Comment Policy；scripts/trellium.py、history_store.py、test_trellium.py、sync-skills。

## Capability Tags

- privacy
- persistence
- identity
- agent-governance
- python
- testing

## Authority

Allowed：owner 已明确要求“为private模式增加history的储存方式……跟进”，在上述边界实施、验证与记录。此前 TASK-0027 的 plan-only 不再阻止本任务的新增功能实施，TASK-0027 本身不自动 accepted。

2026-10-01 追加授权：owner 在知悉实现、测试及预存失败后要求“push吧，新打一个tag”；按当前交付接受并授权提交 develop、推送和创建新版本 tag。此授权覆盖本任务及同轮已有分析/记忆材料，不自动接受 TASK-0027，不新增独立 review 结论。

Requires approval：扩大到当前知识备份、自动恢复/迁移/cleanup、切换默认模式、accepted 或 Git 发布。

Forbidden：访问真实 ~/.trellium/history、隐藏 Git index 状态、覆盖本轮已有五项分析/记忆改动、自动生成丢失绑定的替代 UUID、恢复旧 Authority、伪造验证。

## Acceptance Criteria

- [x] Private 显式首次绑定创建 ignored project-id，登记 data role；重复调用/接入/升级保持 UUID。
- [x] 缺 identity 且 stamp/HEAD 存在绑定证据时拒绝；非法身份、policy、privacy 边界或不确定 Git 查询拒绝且无写入；登记失败可保留 UUID 后重试。
- [x] Private TASK 与必要 ledger 成组调用现有 Store；部分失败保留来源、幂等重试；删临时 clone 后能 get 校验原始 bytes。
- [x] 双语分发命令和恢复说明可执行；identity 和 stamp/TASK/ledger 始终 untracked/ignored，强制 add 仍报错。
- [x] Local 与 Tracked 的既有语义无回退；默认仍 Local，Store 格式/API 不变。
- [x] 原始验证证据、sync/check/status/diff 与文档检查已记录。
- [x] owner 接受交付并授权提交、push 和新 tag。

## Verification

- 聚焦 Private history、既有身份及 Store 测试，完整四模块 unittest；预存 ancestor-swap FAIL 独立披露，不冒称全量绿。
- 隔离双语分发 E2E：private adoption → identity → TASK/ledger retain → partial failure/retry → 删除临时 clone → 按已知 UUID/逻辑 id/digest get；模拟重建接入恢复同 UUID，不按路径/remote 猜项目。
- 实际本机环境与可用的 Linux 非特权容器；所有 Store 位于临时目录，不访问真实 home history。
- sync-skills --check、trellium check/status、diff --check、文档 links/whitespace；预算仅测量，不自动压缩。

## Execution Record

- 2026-10-01：核实 develop 基线 6a875d8，保留已有五项分析/记忆改动；按当前用户指令创建独立 Level C 实施任务与计划。
- 完成 helper 的 local/private mode gate、Private 写前 stamp/Git/privacy 校验及 baseline 保护；复用 existing Store，登记失败留下原 UUID。HEAD 缺路径查询由 cat-file stderr 改为 ls-tree --full-tree，覆盖 working-tree-only 文件与 monorepo；Private preflight/checker 拒绝损坏 metadata/未知 HEAD/prefix。
- 完成 canonical 协议、双语模板/Skill 的实际保全代码与恢复步骤、README/MIGRATIONS/D-0015；生成副本经 sync。历史讨论保留原基线并追加实施指针，不修改已接受 TASK-0019/0029。
- [验证证据](../../docs/evals/private-history-2026-10/RESULTS.md)：macOS 与 Linux 非 root 各 55/55 聚焦 PASS；macOS 全量 274 tests、273 PASS/1 预存 ancestor-swap FAIL，与本批前 258 tests 的同一失败一致。regression passed 指范围内回归，不代表全量命令绿。
- 两轮自检分别核对合同覆盖与最小性；没有独立 reviewer，不将自检冒称独立验收。check/status 0 errors / 1 新 tracked TASK 尚未提交的 warning；sync/diff/语法/文档校验 PASS，预算仅测量。停在 ready_for_review；未操作 Git index/commit/push/tag，未访问真实 Store/迁移/cleanup。

### 2026-10-01 - Owner acceptance / tag-only publication

- owner 明确要求 push 并新打 tag，交付转 accepted；已有范围内验证通过、全量预存 ancestor-swap FAIL 继续披露，没有独立复审，不将 owner 接受伪装为独立 review。
- 发布目标为 `2026.10.0`：同步 init/VERSION、迁移条目与双语分发，再执行发布检查、提交 develop、创建并推送版本 tag；按 D-0013 不创建 GitHub Release。真实 Store、默认模式及 TASK-0027 待审状态不变。

- 版本同步后完整四模块复跑 274 tests / 273 PASS / 同一预存 FAIL（19.332s），无新增失败；原始输出见 release-full.txt。sync-skills --check 与 diff --check PASS；接受保留已披露风险。最终暂存后 check 0 errors / 0 warnings、status 与 cached diff --check PASS，TASK-0027 仍 ready_for_review。

## Memory Updates

- 新 Decision 记录 Private Git 可见性与历史保全正交；保留旧 Decision 的历史范围及 reasoning。
- runtime 仅更新项目全局能力/导航，不复制 TASK gates；TASK-0027 记录实施转交。
- Durable knowledge disposition: not_applicable（本仓 tracked task）。

## Handoff Requirement

通过任务、计划、Git 与可重跑测试恢复；无真实中断和不可推导 transient delta 时不写 handoff。
