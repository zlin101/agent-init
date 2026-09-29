# TASK-0022 - Risk-first task classification (H4)

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0022",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "accepted",
  "current_slice": "accepted-committed-c631e68",
  "gates": {
    "implementation": "passed",
    "historical_replay": "passed",
    "distribution_sync": "passed",
    "review": "passed"
  }
}
-->

## Objective

把任务分级判定从机械规模阈值改为 risk-first canonical 流程：唯一判断顺序为 Level C 风险域 → Level B 恢复/协作成本 → 默认 Level A。删除"文件数、验收项数量"等单一规模指标到自动升级的链路。不引入 classifier、score、schema、finding 或 checker。

唯一 canonical 判断流程：

```text
命中 Level C 风险域？
→ 是：C

否则，中断恢复或协作成本是否明显较高？
→ 是：B

否则：
→ A
```

核心不变量（最终验收问题）：

```text
新规则是否仍存在任何「单一规模指标 → 自动升级 Level B」的链路？
目标答案：否
```

## Ownership

- PI 按本冻结方案实施 M0-M4，并停在 `ready_for_review`。
- Codex 按"验收重点"独立复核，重点验证 H4 增量与同一 dirty worktree 中 H1-H3/TASK-0019 修改可独立区分。
- Owner 决定最终 accepted；本任务不自行 commit、stage、push 或 tag。

## Scope

### In Scope

- 重写 `init/protocol/20-governance.md` Task Levels：先写三步 canonical flow，再按 C → B → A 顺序定义。
- 修正 `init/protocol/80-execution-patterns.md` 中 Level A 必须写 runtime 的旧表述，保持 H1 的 project-global runtime 语义。
- 手工同步 live surface：`vault/governance.md`、`vault/index.md`、`skills/agent-task/SKILL.md`、双语 `protocol-model.md`、双语 governance/index/agent-task 模板。
- `init/MIGRATIONS.md` 记录迁移（只记录，不复制规则）。
- 运行现有同步机制更新 generated snapshots（`skills/*/references/protocol-source/`）。
- 在现有 `LocalTemplateSemanticsTest` 增加红契约测试（不新建测试 subsystem）。
- Execution Record 内做历史回放简表（B/C control group + 真实 commit-level Level A 样本），不新建 eval/report。

### Out of Scope

- 不新增 classifier、score、schema、finding 或 checker。
- 不做新的 Agent benchmark/eval 报告。
- 不新增 decision 文件：分类规则由 canonical governance 持有，MIGRATIONS 只记录迁移。
- 不因任务后来意外跨 session 而追溯判定最初的 Level A 非法（无追溯重分类）。
- 不修改 `AGENTS.md`、README、`trellium.py`、Profile、Review Ledger、installer、H1/H2/H3 内容、TASK-0019（除非发现实际旧分类描述）。
- 不隐藏或不修改 checker 既有 owner errors / storage warnings。

## Context Required

- `AGENTS.md`
- `vault/index.md`
- `vault/runtime.md`
- `vault/governance.md`
- `init/protocol/20-governance.md`、`init/protocol/80-execution-patterns.md`
- `scripts/test_trellium.py` 的 `LocalTemplateSemanticsTest`

## Capability Tags

- agent-governance
- documentation
- testing

## Authority

Allowed:

- 修改上列 In Scope 文件。
- 在 `LocalTemplateSemanticsTest` 增加测试。
- 运行只读检查与同步脚本。

Requires Approval:

- 本任务整体（Authority 3，治理规则变化）；owner 已在指令中授权实施，最终 accepted 由 owner 决定。

Forbidden:

- stage / commit / push / tag。
- 修改 TASK-0019 的 marker 或继续其 M3-M5。
- 静默覆盖同一 worktree 中 H1-H3/TASK-0019 的既有修改。
- 修改 `vault/.agent-init.json` 与 `docs/engineering/`。

## Acceptance Criteria

1. canonical 顺序冻结为 C → B → A，三步判断流程存在于 `init/protocol/20-governance.md` 且只此一处 canonical 定义。
2. `>2 files`、`>3 acceptance items`、时长阈值等旧充分条件在 live contract 中为零（历史 TASK/MIGRATIONS 中作为历史描述除外）。
3. 规模只保留一句：可提示进一步判断，但不能单独决定等级。
4. 双语模板都包含 risk-first / recovery-cost / default-A 语义。
5. agent-task 只保留三步判断，不形成长 checklist。
6. 一行高风险 contract（dependency/auth/public API）仍为 C；多文件、低风险、易恢复任务可以是 A。
7. 最终验收问题：新规则是否仍存在任何「单一规模指标 → 自动升级 Level B」的链路？目标答案：否。
8. 无评分系统、schema、checker 或新状态；模糊度没有从数字阈值搬成长 checklist。
9. 历史回放简表落在本文件 Execution Record，不修改历史任务或 commit。
10. MIGRATIONS 只记录迁移事实，不复制规则。
11. H4 增量与 H1-H3/TASK-0019 修改可独立区分（基线快照 + SHA-256 供增量 diff）。

## Verification

Required:

```bash
python3 -m unittest scripts.test_trellium.LocalTemplateSemanticsTest
python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh
python3 scripts/sync-skills.py --check
python3 scripts/trellium.py check . --format json
python3 scripts/trellium.py status . --format json
git diff --check
git diff --cached --name-only
```

外加 scoped `rg` 覆盖 canonical、self-hosting、双语模板与 concise references，确认旧充分条件在 live surface 中为零。

Completed:

- M0 基线：worktree 副本 + SHA-256 保存在 `/tmp/trellium-task-0022.AI797J`（`SHA256SUMS.txt`，21 个 H4 重叠文件；`vault/runtime.md` 与本任务文件属 vault memory 更新，不在快照内，增量以 Git diff + 本文件 Execution Record 区分）；`git status --short` 已存档于同目录。`sha256sum -c` 全部 21 项验证通过（review round 1 已删除 checksum 文件对自身的空文件自引用行，修复了不可完整自校验问题）。
- 全量测试基线：189 tests，FAILED（expected failures=3，unexpected successes=19）——TASK-0019 parked 边界的既有红契约，本任务不得改变其数量。
- checker 基线：2 error（`CORE_STORAGE_UNCOMMITTED` ×2，owner-local stamp/engineering doc 已知项）+ 2 warning（`TASK_STORAGE_PENDING` ×2），exit 2（review round 1 更正：先前误记 exit 0；实测有 error 即 exit 2）。
- staged = 0（开工时；验收时仍为 0，未暂存未提交）。
- M4 结果：`LocalTemplateSemanticsTest` 15 tests OK（8 既有 + 7 条 H4 契约红→绿）；全量套件 196 tests，FAILED（expected failures=3，unexpected successes=19）与基线完全一致——TASK-0019 parked 边界的既有红契约数量未变；`sync-skills --check` in sync；`git diff --check` 干净。
- checker：exit 2，2 error（`CORE_STORAGE_UNCOMMITTED` ×2，owner-local stamp/engineering doc 已知项，未隐藏未修改）+ 3 warning（`TASK_STORAGE_PENDING` ×3：基线 2 条 + 本任务新建未提交的 TASK-0022 文件本身，禁止 stage/commit 的直接预期结果，非回归）。
- scoped rg：旧充分条件短语在 live contract（canonical、self-hosting vault、双语模板、concise references、agent-task、AGENTS/README）中为零；唯一命中在 `init/MIGRATIONS.md` 及其 snapshot——作为被删除内容的历史描述引用，属计划允许项。

## Execution Record

### 2026-09-29 - Agent: PI

Context read:

- `AGENTS.md`、`vault/index.md`、`vault/runtime.md`、`vault/governance.md`、`vault/tasks/README.md`
- `init/protocol/20-governance.md`、`init/protocol/80-execution-patterns.md`、`init/MIGRATIONS.md`
- `scripts/test_trellium.py`（`LocalTemplateSemanticsTest`）、`scripts/sync-skills.py`

Changes made:

- M0：冻结现场（见 Verification Completed）。

Checks run:

- `git status --short` 存档；`git diff --cached --name-only` = 0。
- 全量测试与 checker 基线已记录。

Review and reflection:

- H4 与 H1-H3/TASK-0019 同处 dirty worktree；用基线副本 + SHA-256 保证 21 个 H4 重叠文件可区分（review round 1 收敛：不声称 runtime/任务文件已哈希冻结）。

### 2026-09-29 - Agent: PI (review round 1: REQUEST_CHANGES → fixed)

Context read:

- owner 验收结论（2 P1 + 2 P2）；`scripts/trellium.py` FILE_ROLES；TASK-0021 状态块现状；基线目录。

Changes made:

- P1-1：架构风险域显式加入 Level C——canonical 增独立 bullet「架构方向或重大架构决策」（不再仅藏在治理 bullet 内）；`vault/governance.md`、双语 governance 模板、双语 index 速查表、双语 `protocol-model.md` 同步列出架构；4 个测试方法新增「架构/architecture/重大架构决策」冻结 marker。
- P1-2：`init/MIGRATIONS.md` Agent migration 条目改为真实升级语义——`vault/governance.md`/`vault/index.md` 是 merge 角色 protocol 载体：pristine 自动刷新、定制生成 proposal 人工合并、`trellium-policy` 等用户数据保留（原文误称 protected data 升级不改写）。
- P2-3：删除基线 `SHA256SUMS.txt` 对自身的自引用行，`sha256sum -c` 现在 21/21 全部通过；任务文件更正 checker 基线 exit 0 → exit 2（记录错误）；基线覆盖范围如实限定为 21 个 H4 重叠文件，runtime/任务文件不在快照内。
- P2-4：`vault/runtime.md` Current Phase 改为 H1/H2/H3 owner-accepted、H4 待验收；Focus 改为 TASK-0022；TASK-0021 进展行补记 owner 已验收 H3；Next Steps 改为 Codex 复验 H4。TASK-0021 状态块属 owner 维护，未代改。

Checks run:

- `python3 -m unittest scripts.test_trellium.LocalTemplateSemanticsTest`：15 tests OK（含新增架构 marker）。
- 全套验证复跑（见 Verification）；sync 后 `--check` in sync；`sha256sum -c` 21/21 OK。

Review and reflection:

- P1-1 教训：canonical 内嵌括号不等于分发契约显式列出；分发面必须独立逐一检查，不能假设「语义上包含」就够了。
- P1-2 教训：写 MIGRATIONS 前应核对 `FILE_ROLES` 真实角色，不凭先前任务印象描述升级行为。

Risks:

- 无新增风险；无 handoff。

Next action:

- Codex/owner 复验本轮修复；review gate 保持 pending。

Risks:

- 无 handoff（无真实中断、无非可推导 delta）。

Next action:

- M0 红契约测试（已完成：7 条红契约全部红，随后在 M1-M4 后转绿）。

### 2026-09-29 - Agent: PI (M1-M4)

Context read:

- 同上；另含 `vault/tasks/TASK-0021` 状态块格式、历史 commit 统计。

Changes made:

- M1：`init/protocol/20-governance.md` Task Levels 重写为三步 canonical flow + C → B → A 顺序定义；新增规模不单独决定等级、一行高风险也是 C、后来意外中断 ≠ 追溯改写三句；三条短例。`init/protocol/80-execution-patterns.md` Level A 行改为“仅当 project-global runtime 发生变化时更新”。
- M2：手工同步 `vault/governance.md`、`vault/index.md`、`skills/agent-task/SKILL.md`、双语 `protocol-model.md`、双语 governance/index/agent-task 模板；`init/MIGRATIONS.md` 新增 Unreleased 条目；`python3 scripts/sync-skills.py` 更新 generated snapshots（`--check` in sync）。
- 修复实施中的一处自错误：首次编辑误将旧 Task Levels 段落重复追加（MD024 duplicate headings 报警暴露），已按行范围删除，最终段落唯一且无旧阈值。
- 未修改：`AGENTS.md`、README、`trellium.py`、Profile、Review Ledger、installer、H1-H3 内容、TASK-0019（scoped rg 未发现这些文件中的旧分类描述）。

Checks run:

- `python3 -m unittest scripts.test_trellium.LocalTemplateSemanticsTest`：15 tests OK（8 既有 + 7 条 H4 契约；红→绿）。
- 全量验证与 scoped rg 见 Verification。

Historical replay（只回放判断，不修改历史任务或 commit）：

B/C control group（真实历史 TASK）：

| 场景 | 样本 | 预期 | 判定依据（新规则） |
|---|---|---|---|
| Public API / JSON contract | TASK-0008 | C | 命中公开 API/外部契约风险域，规模无关 |
| Security / durability | TASK-0013 | C | 命中安全/持久数据风险域 |
| Deployment / release | TASK-0002 | C | 命中部署/生产行为风险域 |
| Migration / rollback | TASK-0014 | C | 命中持久数据/迁移风险域；当时也是多文件，但风险域单独已足 |
| Governance | TASK-0020 | C | 命中治理规则风险域 |
| 长期跨 session / 多阶段 | TASK-0001 | B | 非 C 风险域，但跨 session、多阶段、恢复成本明显高 → B |

Level A control changes（真实 commit-level 样本，不是假装存在历史 Level A TASK）：

| Commit | 变化 | 预期 | 判定依据（新规则） |
|---|---|---|---|
| `afd962f` | 单文件 README 语言入口（+2 行） | A | 低风险、易恢复 → A |
| `8df3b7a` | 3 文件安装说明澄清，不改变行为 | A | 旧 `>2 files` 规则的 false positive；低风险、单 session、易恢复 → A |
| `01be4a7` | 大体积英文 README 翻译（+304 行） | A | diff 大小不能单独决定 B；纯文档、易从 diff 恢复 → A |
| `ef039eb` | 单一测试补充（+15 行） | A | 低风险、易恢复 → A |
| `cbb2511` | 单文件历史元数据纠正 | A | 低风险、易恢复 → A |

回放结论：

- `8df3b7a` 证明旧“2 个以上文件”规则产生 false positive。
- `01be4a7` 证明 diff 体量不能单独决定 B。
- TASK-0008/0013/0014 证明“一行或少文件”不能逃逸 C。
- 最终验收问题：新规则是否仍存在任何「单一规模指标 → 自动升级 Level B」的链路？——否（canonical 只剩风险域 → 恢复/协作成本 → 默认 A 三步；规模仅提示）。

Review and reflection:

- 唯一 canonical 定义在 `init/protocol/20-governance.md`；live surface 均为语义同步，未复制完整规则。

Risks:

- 无 handoff（无真实中断、无非可推导 delta）。

Next action:

- Codex 独立验收 review；owner 决定 accepted。

## Memory Updates

- `vault/runtime.md`：任务进入 `ready_for_review` 时更新一行。
- `vault/decisions.md`：accepted 后由 owner 决定记录治理决策（本任务不代行）。
- `vault/handoff.md`：仅真实中断且存在非可推导 transient delta 时写。
- Durable knowledge disposition: not_applicable（tracked task）。
