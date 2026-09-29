# Task Files

Use task files for tracked or governed work.

## Lifecycle

```text
draft -> active -> ready_for_review -> accepted
          |
          v
        blocked -> active
```

Use `superseded` when replaced by another task. Paused-and-shelved work moves
to `vault/parked.md`, it is not a lifecycle value.

For local tasks (`task_storage=local`), record the Durable knowledge
disposition line in Memory Updates before entering `accepted`: `none —
<reason>` or `distilled — <canonical destinations>`; an unfilled line counts
as `pending`, which blocks `ready_for_review` and `accepted`. Wrong or unsafe
contracts go to `superseded` immediately — the gate never blocks that, and
undisposed facts become an explicit handover. After a local task closes,
delete its related transient deltas from `vault/handoff.md`; durable
conclusions live in canonical files first. Tracked tasks default to
`not_applicable`.

## Task State Block

Level B/C task files carry a `trellium-task-state` block right after the
title. It is the single owner of lifecycle, authority level, the current
slice, and gate results (optional: `current_slice`, `gates`). Update it on
every status change; `runtime.md` persists no TASK projection. Unknown fields
are invalid; changing a field's meaning requires a new
`schema_version`. The block never grants approvals: Allowed, Requires
Approval, Forbidden, and acceptance stay owned by the task body and the user.

Task files without the block are legacy: add the block the next time you
touch the task; do not batch-migrate history. `TASK-xxxx-review.md` ledgers
and `tasks/archive/` are cold history and do not carry a block.

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
- `vault/handoff.md` only if a real interruption leaves a non-derivable transient delta
- Durable knowledge disposition (required before `accepted` when `task_storage=local`): not_applicable | pending | none — <reason> | distilled — <canonical destinations>
```

## Review Ledger

Multi-round review uses a `TASK-xxxx-review.md` ledger and converges in
batch, not through message ping-pong.
Statuses: `open` | `fixed` | `wont-fix` (with reason) | `needs-discussion`.
The checklist prefers the task file's Acceptance Criteria; `wont-fix` and
`needs-discussion` go back to the user.
Archive the ledger into the task file's Execution Record once converged (no
`open` or `needs-discussion` left).

```md
# TASK-0001 - Review Ledger

## Findings

- R1 · open · one-line finding
- R2 · fixed · one-line finding
- R3 · wont-fix · one-line finding · reason

## Round 2026-01-01

- Handling notes and verification results.
```
