# TASK-0017 - 新接入默认使用 local TASK storage

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0017",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "accepted"
}
-->

## Objective

让 Trellium 首次接入明确选择 TASK storage，并把 `local` 设为安全默认值，避免 TASK、review 与 archive 污染业务仓库；协作核心和长期项目真相仍必须进入 Git。

## Scope

### In Scope

- Skill/Agent 工作流在首次接入前询问 owner，推荐 `local`；owner 未指定时按 local 执行。
- Agent 将选择写入 policy；local 模式生成窄范围 `vault/tasks/.gitignore`，只忽略 TASK、review 和 archive。
- 重复接入与存量 upgrade 保持既有 policy，不自动迁移 tracked/local。
- 协议、迁移、README、双语 Skill、版本与测试同步。

### Out of Scope

- 自动 `git add`、commit、push 或修改项目根 `.gitignore`。
- 新增 `--task-storage` CLI 参数、脚本交互或 storage renderer。
- 自动迁移既有项目的 storage、untrack 已跟踪 TASK 或删除历史任务。
- 修改 TASK schema、lifecycle、status/check 语义或 Orion。

## Context Required

- `AGENTS.md`
- `vault/index.md`
- `vault/runtime.md`
- `vault/governance.md`
- `init/protocol/10-vault.md`
- `init/protocol/70-adoption-flow.md`
- `scripts/trellium.py`
- `scripts/test_trellium.py`

## Capability Tags

- agent-governance
- cli
- adoption
- local-storage
- privacy
- testing

## Authority

Allowed:

- Owner 明确决定“默认 local，local 更实际，TASK 文档会污染 repo”。
- 修改 CLI、模板、协议、双语发行包、聚焦测试与项目记忆。

Requires Approval:

- accepted、commit、push、tag、Release 或自动迁移存量项目。

Forbidden:

- 把 `local` 解释为协作核心不入 Git。
- 自动修改目标项目根 `.gitignore` 或执行任何 Git 写操作。
- 触碰 owner 明确排除的 `vault/.agent-init.json` 与 `docs/engineering/code-comments.md`。

## Acceptance Criteria

- [x] Skill 首次接入询问 owner，推荐/默认 local，并准确说明 local/tracked 边界。
- [x] Agent 在 local 模式把 policy 改为 local，并创建只覆盖 TASK/review/archive 的嵌套 ignore；tracked 不添加这些规则。
- [x] 不新增 CLI API，存量 upgrade 不静默改变 storage。
- [x] 双语 Skill、协议、迁移和 README 语义一致。
- [x] 全量测试、sync 与 whitespace 门禁通过，无 open P0/P1/P2。

## Verification

Required:

- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`
- `python3 scripts/sync-skills.py --check`
- `python3 scripts/trellium.py check . --format json`
- `git diff --check`
- 临时 fixture：默认 local、显式 local、显式 tracked、重复 adopt、冲突选择、fresh clone。

Completed:

- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` — 177/177 passed。
- `python3 scripts/sync-skills.py --check` — 双语快照 in sync。
- `git diff --check` — passed。
- `git diff --exit-code -- scripts/trellium.py scripts/test_trellium.py skills/*/assets/trellium.py` — passed；确认没有 CLI/脚本实现改动。
- self-check：2 error（owner 排除的 `vault/.agent-init.json`、`docs/engineering/code-comments.md`），1 warning（当前 tracked TASK 尚未提交）；无本任务新增语义错误。

## Execution Record

### 2026-09-28 - Agent: Codex

Context read:

- 项目必读 Vault、Trellium Skill、协议模型、模板指南、vault/adoption 权威协议与当前 CLI/tests。

Changes made:

- 根据 owner 纠正，将实现从 CLI/renderer 收缩为 Agent-native 工作流；脚本与测试改动已撤回。
- 双语 Skill 负责首次询问与默认 local，并指导 Agent 写 policy 与窄范围嵌套 ignore。
- 同步协议、迁移、README、长期决策与 2026.09.9 版本号；存量项目不自动迁移。

Checks run:

- 收缩前脚本方案的结果不作为最终候选验收；最小方案待复跑全量门禁。

Review and reflection:

- 默认 local 只保护私有工作日志；核心持久性 Gate 不得放松。
- CLI 不做交互，询问由 Skill/Agent 工作流承担，避免 headless 自动化阻塞。
- owner 指出该选择是一句 prompt 可完成的 Agent-native 能力，不应把交互决策固化为 CLI API；已按此降低复杂度。

Risks:

- 大量现有测试隐含默认 tracked，需要区分产品预期变化与测试夹具的显式 tracked 需求。

Next action:

- Owner 于 2026-09-28 验收并授权提交与创建 2026.09.9 tag；按 D-0013 只发布 tag，不创建 GitHub Release。

### 2026-09-28 - Agent: Codex — owner acceptance

- Owner 明确接受 TASK-0017，并授权提交当前 Trellium 变更及创建 `2026.09.9` tag。
- 生命周期 `ready_for_review → accepted`；发布仍须完成提交态 clean-clone、CI/远端与 tag 指向验证，不创建 GitHub Release。

## Memory Updates

- `vault/runtime.md`
- `vault/decisions.md`
- `vault/collaboration.md`
- Durable knowledge disposition: not_applicable（tracked task）

## Handoff Requirement

中断时记录默认值、重复 adopt、conditional ignore 文件和升级兼容四个 Gate 的完成状态；不得修改 Orion 或 owner 排除文件。
