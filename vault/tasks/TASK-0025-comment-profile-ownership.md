# TASK-0025 - Comment/Profile ownership round 1

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0025",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "accepted",
  "current_slice": "accepted-ownership-round-1",
  "gates": {
    "implementation": "passed",
    "distribution_sync": "passed",
    "review": "passed"
  }
}
-->

## Objective

确立单一 ownership：`code-comments.md` 是注释、Doc Comment、docstring、TODO/FIXME、directive、API 文档表达的唯一 owner（Comment/API Documentation Policy）；Language Profile 保留 API 行为、安全、错误、兼容性与其他工程 fallback。路由三分支：普通内部实现 → Profile；纯注释/docstring/TODO → Comment Policy；公开 API 或行为+注释 → 两者。只实施 ownership Round 1，完成后停止，不进入 Profile 知识压缩。

## Scope

### In Scope

- 从 Go/Python canonical profile（及双语派生模板）删除重复的注释规范正文；删除前逐条确认 Comment Policy 已覆盖。
- Profile 仅保留短职责指针。
- live protocol 将 `code-comments.md` 描述为正式 Comment/API Documentation Policy；"2026.09.7 compatibility carrier" 只留在 MIGRATIONS/upgrade 历史语境。
- A1 parity 测试同步冻结新路由。

### Out of Scope

- 文件名/路径、`project_rules`/`project_profile`、stamp schema、CLI、输出文件集合、pristine/custom/proposal 行为、Profile 独立选择方式。
- Profile 知识压缩；per-root override；A2/A3。

## Verification

Required:

```bash
python3 -m unittest scripts.test_trellium
python3 scripts/sync-skills.py --check
cmp -s scripts/trellium.py skills/trellium/assets/trellium.py && cmp -s scripts/trellium.py skills/trellium-zh/assets/trellium.py
python3 scripts/trellium.py check . --format json
git diff --check
```

Completed:

- 内容手术（删除前逐条确认 Comment Policy 已覆盖）：Go canonical 4 条注释 bullets、Python canonical 4 条 docstring/注释 bullets 移除（双语镜像 byte-identical）；en 双模板同内容（本地化措辞）移除，`Go style and API documentation` 节更名 `Go style`。
- Profile 仅保留短职责指针（Comment Policy 唯一 owner + 三分支并读规则）。
- 路由三分支重写：AGENTS 双语模板、`agent_entry_section`、self-host AGENTS.md（Comment/API Documentation Policy 唯一 owner；纯文档单读；行为+注释并读；表达规则冲突 Comment Policy 胜；行为/安全/错误/兼容仍由 profile 约束）。
- carrier 措辞所有权化：70×2、60、50、INIT、双语 README、双语 SKILL 共 10 处改为 Comment/API Documentation Policy；MIGRATIONS 历史措辞保留。
- 测试同步：A1 parity 六项不变量换新路由措辞；LocalTemplateSemanticsTest 双语断言与 en expected headings 同步。

Checks run:

- `PrivateStorageModeTest`/`TemplatePackagingTest`/`LocalTemplateSemanticsTest`/`ReadmeContractTest` 全绿；全量 OK exit 0；sync `--check` in sync；嵌入副本 byte-identical；check 0/0；`git diff --check` 干净；live 面 carrier/兼容措辞清零（MIGRATIONS 历史语境保留）。

## Execution Record

### 2026-09-29 - Agent: PI — M1 ownership complete（round 2 rework：P1-1 三分支路由、P1-2 残留清零、P1-3 双语 README 三模式/private；该轮内容最终以 amend 后提交 `08e6fe9` 落库）

- 路由三分支重写 4 副本；30-agent-entry:64、50:88 句首、protocol README:26、zh SKILL:45 carrier 残留清零；README.md zh H1/private 漂移（policy 三模式、TASK storage 三模式+private、反向 privacy Gate、disposition local lifecycle）；README.en TASK storage bullet 补 private 反向 privacy Gate；TASK-0025 契约补全。
- A1 parity 测试冻结三分支语义；全量 OK exit 0；sync/check/嵌入/diff-check 全绿。

### 2026-09-29 - Agent: PI — M1 ownership routing + content surgery complete（ready_for_review）

Context read:

- Owner 收敛计划 Phase 4；两份 canonical profile 全文；CODE_COMMENTS.template 双语结构；carrier 措辞影响面 grep。

Changes made:

- 见 Completed（内容手术、路由三分支重写、carrier 所有权化、测试同步）。

Checks run:

- 见 Completed；另以删除内容逐条对照 Comment Policy 确认无唯一规则丢失。

Review and reflection:

- profile 与 Comment Policy 的重复是 2026.09.7/2026.09.8 两代载体演进的累积；ownership Round 1 只做正文归位，不改生成管线。

Risks:

- self-host 仓库的 Comment Policy 文件已 Phase 0 删除——本仓自身路由目标暂空，待收敛计划后续（Phase 6 或单独 maintenance）重建。
- 无 handoff。

Next action:

- Codex/owner 复验；通过后进入收敛计划 Phase 5/6。

## Context Required

- `AGENTS.md`
- `vault/runtime.md`
- `init/protocol/profiles/go-backend.md`、`python-backend.md`
- `skills/trellium/assets/templates/docs/engineering/CODE_COMMENTS.template` 与双语派生模板
- `skills/trellium/assets/templates/AGENTS.md`、`agent_entry_section()`（scripts/trellium.py）
- `vault/decisions/D-0011-durable-language-profiles.md`

## Capability Tags

- documentation
- testing
- agent-governance

## Authority

Allowed:

- 修改两份 canonical profile、双语派生模板与双语 CODE_COMMENTS/AGENTS 模板中的 ownership 措辞与路由三分支。
- 修改双语 SKILL/README 中 carrier 措辞；同步 generated snapshots。
- 更新 A1 parity guard、LocalTemplateSemanticsTest 与 ReadmeContractTest 断言到新契约。

Requires Approval:

- accepted、push、tag、Release。

Forbidden:

- 修改文件路径、`project_rules`/`project_profile`、stamp schema、CLI、输出文件集合、pristine/custom/proposal 行为或 Profile 独立选择方式。
- 进入 Profile 知识压缩；重引入任何 “compatibility carrier/兼容载体” live 措辞。

## Acceptance Criteria

- [x] Go/Python canonical profile 与双语模板的注释表达 bullets 已移除，且逐条确认 Comment Policy 覆盖（无唯一规则丢失）。
- [x] Profile 仅保留短职责指针（Comment Policy 唯一 owner + 三分支并读规则）。
- [x] 路由三分支（实现→Profile；纯注释→Policy；公开 API/行为+注释→两者）在 AGENTS 双语模板、`agent_entry_section` 与 self-host AGENTS 一致。
- [x] live 面（protocol/Skills/README）“兼容载体/compatibility carrier”措辞清零；MIGRATIONS 历史语境保留。
- [x] A1 parity guard 冻结新路由；全部测试绿。

## Handoff Requirement

仅真实中断且存在非可推导 transient delta 时写三小节 handoff；ownership 状态、措辞位置与测试结果均可从 TASK、Git 与测试恢复，不得进入 handoff。

## Memory Updates

- `vault/runtime.md`
- Durable knowledge disposition: not_applicable（tracked task）
