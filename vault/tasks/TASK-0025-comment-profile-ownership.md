# TASK-0025 - Comment/Profile ownership round 1

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0025",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "ready_for_review",
  "current_slice": "M1-ownership-complete-awaiting-review",
  "gates": {
    "implementation": "passed",
    "distribution_sync": "passed",
    "review": "pending"
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

## Memory Updates

- `vault/runtime.md`
- Durable knowledge disposition: not_applicable（tracked task）
