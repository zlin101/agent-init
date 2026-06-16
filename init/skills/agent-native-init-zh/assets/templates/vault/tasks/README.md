# Task Files

追踪任务和治理任务使用任务文件。

## Status Flow

```text
Draft -> Active -> Ready for Review -> Accepted
          |
          v
        Blocked
          |
          v
        Active
```

任务被替代时使用 `Superseded`。

## Naming

```text
TASK-0001-short-title.md
```

## Template

```md
# TASK-0001 - Short Title

## Status

Draft | Active | Blocked | Ready for Review | Accepted | Superseded

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

Level:

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
- `vault/handoff.md` if interrupted or handed off
```
