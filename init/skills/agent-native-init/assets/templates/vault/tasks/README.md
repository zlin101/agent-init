# Task Files

Use task files for tracked or governed work.

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

Use `Superseded` when replaced by another task.

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
