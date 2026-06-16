---
name: agent-task
description: Use when doing non-trivial project work that requires context reading, scoped edits, verification, task records, or vault memory updates.
---

# Agent Task Workflow

## Steps

1. Read `AGENTS.md`, `vault/index.md`, `vault/runtime.md`, and `vault/governance.md`.
2. Follow `vault/index.md` to read task-specific context.
3. Classify the task as Level A, Level B, or Level C.
4. Determine authority level and whether user confirmation is required.
5. Define objective, scope, out of scope, acceptance criteria, and checks.
6. Create or update a task file for Level B or Level C work.
7. Make the smallest necessary change.
8. Add or update focused tests for behavior changes.
9. Keep long work checkpointable through task files and `vault/handoff.md`.
10. Run required checks.
11. Check acceptance gates; tests passing alone is not completion.
12. Update `vault/runtime.md`.
13. Record durable decisions in `vault/decisions.md`.

## Constraints

- Do not introduce unrelated dependencies or frameworks.
- Do not save secrets.
- Do not rely on real external services in unit tests.
- Do not overwrite user changes silently.
- Escalate when scope affects architecture, public APIs, data models, security, privacy, cost, deployment, dependencies, or Agent governance.

## Review Before Completion

- Confirm acceptance criteria one by one.
- Confirm verification output.
- Confirm vault memory updates.
- Confirm no high-impact change is hidden.
