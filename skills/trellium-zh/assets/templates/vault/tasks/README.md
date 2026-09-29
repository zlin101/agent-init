# Task Files

追踪任务和治理任务使用任务文件。

## Lifecycle

```text
draft -> active -> ready_for_review -> accepted
          |
          v
        blocked -> active
```

任务被替代时使用 `superseded`。暂停且暂不推进的工作进入 `vault/parked.md`，不是 lifecycle 值。

local 任务（`task_storage=local`）进入 `accepted` 前必须在 Memory Updates 填写 Durable knowledge disposition：`none — <理由>` 或 `distilled — <canonical 目标文件>`；未填写视为 `pending`，不得进入 `ready_for_review` 或 `accepted`。错误契约走 `superseded` 立即废止，不受该 gate 阻塞，未处置事项显式转交。local 任务关闭后，删除 `vault/handoff.md` 中与其相关的 transient delta（durable 结论先落入 canonical 文件）。tracked 任务默认 `not_applicable`。

## 任务状态块

Level B/C 任务文件在标题之后携带 `trellium-task-state` 状态块。它是 lifecycle、authority_level、当前 slice 与 Gate 结果的唯一 owner（可选字段：`current_slice`、`gates`）。每次状态变化只更新状态块；`runtime.md` 不保存 TASK 投影。未定义字段非法；改变字段含义必须提升 `schema_version`。状态块不授予批准：Allowed、Requires Approval、Forbidden 与验收仍由任务正文与用户指令决定。

没有状态块的任务文件是 legacy：下次接触该任务时补上，不批量迁移历史。`TASK-xxxx-review.md` 台账与 `tasks/archive/` 是冷历史，不带状态块。

## Naming

```text
TASK-0001-short-title.md
```

## Template

```md
# TASK-0001 - Short Title

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0001",
  "level": "B",
  "authority_level": 2,
  "lifecycle": "draft"
}
-->

## Objective

## Scope

### In Scope

### Out of Scope

## Context Required

- `AGENTS.md`
- `vault/index.md`
- `vault/runtime.md`
- `vault/governance.md`

## Capability Tags

- documentation
- testing

## Authority

Allowed:

- ...

Requires Approval:

- ...

Forbidden:

- ...

## Acceptance Criteria

- ...

## Verification

Required:

- ...

Completed:

- ...

## Execution Record

### YYYY-MM-DD - Agent: unknown

Context read:

- ...

Changes made:

- ...

Checks run:

- ...

Review and reflection:

- ...

Risks:

- ...

Next action:

- ...

## Memory Updates

- `vault/runtime.md`
- `vault/decisions.md` if durable decisions were made
- `vault/handoff.md` 仅在真实中断留下非可推导 transient delta 时
- Durable knowledge disposition (required before `accepted` when `task_storage=local`): not_applicable | pending | none — <reason> | distilled — <canonical destinations>
```

## Review Ledger

多轮 review 使用 `TASK-xxxx-review.md` 台账批量收敛，不逐条消息往返。
状态：`open` | `fixed` | `wont-fix`（附理由）| `needs-discussion`。
checklist 优先用任务文件的 Acceptance Criteria；`wont-fix` 与 `needs-discussion` 交还用户判断。
收敛（无 `open` 与 `needs-discussion`）后归档进任务文件 Execution Record。

```md
# TASK-0001 - Review Ledger

## Findings

- R1 · open · 一句话发现
- R2 · fixed · 一句话发现
- R3 · wont-fix · 一句话发现 · 理由

## Round 2026-01-01

- 处理说明与验证结果。
```
