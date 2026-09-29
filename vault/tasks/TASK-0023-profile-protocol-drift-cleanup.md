# TASK-0023 - Profile protocol drift cleanup

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0023",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "accepted",
  "current_slice": "accepted-committed-c631e68",
  "gates": {
    "facts": "passed",
    "canonical_owner": "passed",
    "drift_cleanup": "passed",
    "implementation": "passed",
    "distribution_sync": "passed",
    "review": "passed"
  }
}
-->

## Objective

消除 Profile 协议的 live drift：确立 `init/protocol/70-adoption-flow.md`「Profile 工程规范」为唯一 canonical owner；删除其他 live 面把 `docs/engineering/code-comments.md` 当作唯一 Profile 产物的旧定义；修复 `scripts/trellium.py` `agent_entry_section()` 使既有 `AGENTS.md` 的 marker 按 D-0011 路由完整 Profile + 兼容载体。不修改 Profile 渲染、stamp、upgrade 或文件布局语义。

## Ownership

- PI 按本计划实施 M0-M4，停在 `ready_for_review`。
- Owner 独立复验并决定 accepted/commit。

## Scope

### In Scope

- M0：三个真实 fixture 冻结事实 + 红测。
- M1：`70-adoption-flow.md`「Profile 工程规范」补齐 canonical 内容（显式选择、完整 Profile、兼容载体、重叠优先级、roots/多 Profile/保护/proposal、stamp 两个文件角色）。
- M2：`init/INIT.md`、`init/protocol/README.md`、`init/protocol/60-initialization-flow.md`、双语 README、双语 Trellium Skill、本仓 `AGENTS.md` 的 drift 清理/指针化。
- M3：`agent_entry_section()` 路由 conformance fix + 既有 AGENTS fixture 回归测试；加强既有 Profile 测试名称/断言（不新建 subsystem）。
- M4：`sync-skills.py` 更新嵌入脚本与 snapshots；MIGRATIONS 只加一句 concise `Fixed/Auto`。

### Out of Scope

- 新 Profile schema/metadata、checker/finding/lint、新 source-of-truth 文件。
- 从模板动态解析 AGENTS 路由的重构；Profile 渲染器重写。
- CLI 参数、Profile 路径/输出集合、render 函数、stamp schema、merge/overwrite/proposal 行为、managed-file 权限边界。
- 全仓历史措辞清理；修改 H1-H4、TASK-0019、task-storage、installer、Review Ledger、`docs/engineering/` 实际 owner 文件。
- 重写历史 TASK/evaluation/review 记录。
- `templates-guide.md`、`protocol-model.md`（已检查无「code-comments 唯一产物」旧定义，默认不修改）。

## Context Required

- `AGENTS.md`、`vault/index.md`、`vault/runtime.md`、`vault/governance.md`
- `vault/decisions/D-0011-durable-language-profiles.md`
- `init/protocol/70-adoption-flow.md`、`init/protocol/60-initialization-flow.md`、`init/INIT.md`、`init/protocol/README.md`
- `scripts/trellium.py`（`agent_entry_section`、`FILE_ROLES`）

## Capability Tags

- agent-governance
- implementation
- testing
- documentation

## Authority

Allowed:

- 修改上列 In Scope 文件；运行 adopt fixtures、测试与同步脚本。

Requires Approval:

- 本任务整体（Authority 3）；owner 指令已授权实施，accepted 由 owner 决定。

Forbidden:

- stage / commit / push / tag。
- 修改 `agent_entry_section()` 以外的 `trellium.py` 行为面（CLI、render、stamp、merge/upgrade、权限边界）。
- 静默覆盖 H1-H4/TASK-0019 的既有 worktree 修改。

## Acceptance Criteria

1. 只有 `70-adoption-flow.md` 保存 Profile 完整定义；其他 live 面仅摘要 + canonical 指针。
2. 无 live 文档把 `code-comments.md` 描述为唯一 Profile 产物（历史 MIGRATIONS/TASK 除外）。
3. 既有 AGENTS fixture：adopt 后保留用户原文、生成两类 Profile 文件、marker 同时路由两类文件（红→绿回归测试冻结）。
4. 未选 Profile 的 fixture 仍不生成任何工程文档（既有测试保持）。
5. Behavior changed 如实记录：yes——仅既有 AGENTS marker 的 Profile 路由；no——CLI、文件布局、Profile 内容、stamp、merge/overwrite、持久状态。
6. 嵌入副本与 snapshots 字节一致；manifest 刷新。
7. MIGRATIONS 保留 2026.09.7 与 TASK-0014 历史记录，仅追加一句 concise Fixed/Auto。

## Verification

Required:

```bash
python3 -m unittest scripts.test_trellium.AgentInitTest
python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh
python3 scripts/sync-skills.py --check
cmp -s scripts/trellium.py skills/trellium/assets/trellium.py
cmp -s scripts/trellium.py skills/trellium-zh/assets/trellium.py
python3 scripts/trellium.py check . --format json
git diff --check
git diff --cached --name-only
```

外加 scoped rg（排除 MIGRATIONS、历史 TASK/eval）确认五条验收主张。

Completed:

- M0 基线：26 个预期重叠文件 + SHA-256 存于 `/tmp/trellium-task-0023.6yy04w`；staged = 0。
- Fixtures（真实运行 `scripts/trellium.py adopt`，`/tmp/trellium-task-0023-fixtures/`）：
  - A 无既有 AGENTS + `--profile go-backend=.`：生成 `code-comments.md` + `profiles/go-backend.md`，模板 AGENTS 路由完整 Profile。
  - B 既有用户 AGENTS + `--profile go-backend=services/api`：用户原文保留、两类文件生成，但追加 marker 只路由 code-comments、不含完整 Profile（**红事实确认**）。
  - C 无 Profile：`docs/engineering/` 不生成。
- 全量测试基线：196 tests，FAILED（expected failures=3，unexpected successes=19）——TASK-0019 parked 边界，不得改变。
- checker 基线：exit 2，2 error（`CORE_STORAGE_UNCOMMITTED` ×2，owner-local 已知项）+ 3 warning（`TASK_STORAGE_PENDING` ×3）。
- M1-M4 结果见 Execution Record；全套验收门已跑（见下）。

## Execution Record

### 2026-09-29 - Agent: PI

Context read:

- `AGENTS.md`、vault 热文件、D-0011、`70-adoption-flow.md`、`60-initialization-flow.md`、`INIT.md`、`protocol/README.md`、双语 README/Skill、`scripts/trellium.py`（`agent_entry_section`/`FILE_ROLES`）、既有 Profile 测试。

Changes made:

- M0：任务文件、基线、三 fixtures、红测（见下）。

Checks run:

- fixtures 实测（见 Verification Completed）。

Review and reflection:

- 漂移根因：2026.09.8 引入完整 Profile 时只更新了模板 AGENTS 与 `60` 号模块；`agent_entry_section()`（既有 AGENTS 追加路径）、`INIT.md`、`protocol/README.md` 仍是 2026.09.7 语义。

Risks:

- 无 handoff（无真实中断、无非可推导 delta）。

Next action:

- 红测入 `AgentInitTest`。

### 2026-09-29 - Agent: PI (M1-M4)

Context read:

- 同 M0；另核 `scripts/trellium.py` `FILE_ROLES`、模板 AGENTS（双语）既有 D-0011 路由文本。

Changes made:

- M1：`70-adoption-flow.md`「Profile 工程规范」加唯一 canonical owner 声明；补“显式选择不猜测、未选不生成”与 stamp 两个文件角色（`project_profile` + `project_rules`）语义。
- M2：`INIT.md`、`protocol/README.md` 删除“唯一 code-comments.md”旧定义，改两类产物摘要 + canonical 指针；`60-initialization-flow.md` 补指针；双语 README 收敛详细规则（stamp/force/proposal 细节归还 canonical），保留两类产物与重叠优先级摘要；双语 Skill 补兼容载体角色与 canonical 路由；本仓 `AGENTS.md` 路由行改为与 zh 模板一致的 D-0011 语义。`templates-guide`/`protocol-model` 已检查无旧定义，未修改。
- M3：`agent_entry_section()` 路由 conformance fix（与新项目模板 AGENTS 路由文本一致，同时路由完整 Profile + 兼容载体 + 重叠优先）；新增回归 `test_adopt_with_existing_agents_routes_complete_profile`；重命名 `test_adopt_with_go_profile_writes_one_scoped_comment_policy` → `..._generates_complete_profile_and_compat_carrier`、`test_adopt_combines_multiple_profiles_and_roots_into_one_file` → `..._in_compat_carrier`，消除旧表述。
- 门禁机械修复（pi-lens 要求，非行为变化）：`scripts/trellium.py` import 块按 ruff I001 重排（直导入在前）、`try/except/pass` → `contextlib.suppress`（SIM105，行为等价）。【review round 1 已按 owner 裁决（P2-1 越界）全部恢复基线；详见下方 round 1 条目】
- M4：`sync-skills.py` 重同步；MIGRATIONS 新增 concise `Unreleased — Profile 路由 conformance`（Fixed + Auto 各一条）；2026.09.7 与 TASK-0014 历史条目未动。

Checks run:

- fixture 复验（修复后）：既有 AGENTS + `--profile go-backend=services/api` → 用户原文保留、两类文件生成、marker 同时路由两类文件（`/tmp/trellium-task-0023-fixtures/b2`）。
- `AgentInitTest` 25/25 OK；全量 197 tests，FAILED（expected failures=3，unexpected successes=19）与基线一致；sync `--check` in sync；嵌入副本 byte-identical；check exit 2（既有 2 error + 3 warning；review round 1 更正：M4 时点实为 4 warning——第 4 条是本任务自身未提交文件的 TASK_STORAGE_PENDING，不 stage/commit 的直接预期）；`git diff --check` 干净；staged = 0。
- scoped rg：旧“唯一 code-comments”语义在 live 面为零；7 个 live 面均含 canonical 指针（review round 1 更正：F001 修复后实为 8 个，含 50 号模块）；`templates-guide`/`protocol-model`/`docs/engineering/` 本任务零修改（其 worktree 既有修改属 H1-H4，可经 TASK-0022 基线区分）。

Behavior changed:

- yes：仅修复既有 `AGENTS.md` marker 的 Profile 路由（`agent_entry_section` 现按 D-0011 同时路由完整 Profile 与兼容载体）。
- no：CLI、文件布局、Profile 内容、stamp、merge/overwrite 和持久状态均未变化。

Review and reflection:
- 漂移根因是 2026.09.8 只更新了模板载体；追加路径（`agent_entry_section`）与 2026.09.7 文档残留漏更。修 fix 时同轮引入过一次语法损坏（函数间换行误删），当轮发现并修复，最终经 compile + 全量测试验证。

Risks:

- 无 handoff（无真实中断、无非可推导 delta）。

Next action:

- Owner 独立复验；review gate 保持 pending。

### 2026-09-29 - Agent: PI (dual-review-loop，owner 指令)

Context read:

- dual-review-loop skill 五个 contract；pi-subagents spawn 机制。

Changes made:

- Round 1（fresh C+S，冻结基线 26 文件 → current）：C1[P1]+S1[regression] 同根因归并为 F001——`init/protocol/50-engineering-constraints.md:88` 残留旧单载体规则（计划漏检的 live 面，违背本任务验收标准 2 与新增 canonical-owner 不变量）；审计确认后修复：改写为摘要+指针（与 60/protocol README 同形状），重跑 sync-skills 刷新镜像与 manifest。C2[P3]+S2[improvement] 同根因归并为 F002——模板 AGENTS 路由与 `agent_entry_section` 两份手维护副本无 parity guard；默认 profile 下 RESIDUAL，不自动修（post-gate 写入禁止）。
- Round 2（全新 C+S，`runs.all` 真并行，同一冻结基线 → 含修复的 current，范围按 review-scope §5 扩至 30 文件）：两 lens 均不再确认 F001（RESOLVED）；F002 根因被再次确认但仍为 RESIDUAL。Gate blockers = 0，验证当前 → PASS。
- 记录：round 1 的 S spawn 因 harness 单 subagent/回合限制在 C 返回后补发（materialization 冻结未变，S 未接触 C 产出）；round 2 改用 runs.all 消除该偏差。

Checks run:

- 修复后 gate 级验证（fresh）：全量 unittest（TASK-0019 parked 边界 sanctioned）、AgentInitTest OK、sync `--check` in sync、嵌入副本 byte-identical、check exit 2（既有 owner errors）、`git diff --check` 干净、staged 0、live 旧语义 sweep 仅剩 MIGRATIONS 历史。

Risks:

- F002（residual）：routing 契约存在三份手维护副本（en/zh 模板 + agent_entry_section），parity 仅由片段断言部分覆盖；未来路由措辞编辑需人工同步，或由 owner 决定是否加 parity 断言/运行时派生（test-only 或渲染器小改，属新决策）。

Next action:

- Owner 复验（含本轮 dual-review 修复）；review gate 保持 pending。

### 2026-09-29 - Agent: PI (review round 1: REQUEST_CHANGES → fixed)

Context read:

- Owner 验收结论（3×P2）；TASK-0023 基线快照中 `scripts/trellium.py` 的 import 块与 `open_child_directory` 原文。

Changes made:

- P2-1：按 owner 裁决恢复 `scripts/trellium.py` 的两处门禁机械改动到 TASK-0023 基线（import 块原交stmt顺序；`open_child_directory` 恢复 try/except/pass 与零空行分隔），仅保留 `agent_entry_section()` 路由修改；重跑 sync-skills，嵌入副本重新 byte-identical；`AgentInitTest` 25/25 OK、compile OK。恢复后该文件 vs 基线仅剩 agent_entry_section 一个 hunk。
- P2-2：更正任务记录——checker 为 2 error + 4 warning（第 4 条是本任务自身未提交文件的 TASK_STORAGE_PENDING，属预期）；canonical 指针面为 8 个（含 F001 修复后的 50 号模块）。
- P2-3：`vault/runtime.md` Current Phase 改为 H1–H4 owner-accepted、TASK-0023 待复验；Next Steps 改为 owner 复验 TASK-0023 P2 修复；未动 TASK-0021/0022 canonical 状态文件。

Checks run:

- 恢复后 vs 基线 diff：仅 agent_entry_section 一个 hunk；compile OK；sync `--check` in sync；嵌入副本 byte-identical；AgentInitTest 25/25；fresh check = 2 error + 4 warning（exit 2）。

Review and reflection:

- 门禁冲突如实上报：pi-lens turn-end 门禁对恢复后的基线状态报 2 条存量发现（L4 import 顺序、L452 try/except/pass）——即 P2-1 明示恢复的状态本身。owner 裁决优先，不重新代行修复；每次触碰该文件门禁都会重报。解决路径由 owner 决定：(a) 独立 hygiene TASK 授权仅这两处机械修复；(b) 仓库级 ruff 配置对齐基线风格。
- 教训：门禁要求的顺手修复也属产品代码变更，必须先确认在任务授权面内；越界修复即使行为等价也是范围违规。

Risks:

- 无 handoff（无真实中断、无非可推导 delta）。

Next action:

- Owner 复验本轮 P2 修复；review gate 保持 pending。

## Memory Updates

- `vault/runtime.md`：`ready_for_review` 时更新一行。
- `vault/decisions.md`：无新长期决策（D-0011 已有；本任务是 conformance）。
- `vault/handoff.md`：仅真实中断且非可推导 delta 时写。
- Durable knowledge disposition: not_applicable（tracked task）。
