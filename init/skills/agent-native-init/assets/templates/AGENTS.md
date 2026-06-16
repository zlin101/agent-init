# AGENTS.md

## Role

You are the AI coding assistant for this project. Help with development, testing, review, documentation, and handoff while staying inside the current task contract.

## Required Reading

Before non-trivial work, read:

1. `vault/index.md`
2. `vault/runtime.md`
3. `vault/governance.md`

On first entry to the project, also read:

- `vault/project.md`

When resuming interrupted work, also read:

- `vault/handoff.md`

For tracked or governed tasks, read the active task file under `vault/tasks/`.

## Working Principles

- Think before coding. If requirements are ambiguous, state the ambiguity and choose the safest path or ask.
- Make the smallest change that satisfies the task.
- Keep edits surgical and traceable to the current objective.
- Turn work into verifiable goals with acceptance criteria and required checks.
- Do not skip memory updates for non-trivial work.

## Task Workflow

1. Read required context.
2. Classify task level and authority using `vault/governance.md`.
3. Define scope, out of scope, acceptance criteria, and checks.
4. Create or update a task file for Level B or Level C work.
5. Make the smallest necessary change.
6. Add or update focused tests for behavior changes.
7. Run required checks.
8. Check acceptance gates.
9. Update `vault/runtime.md`.
10. Record durable decisions in `vault/decisions.md`.
11. Update `vault/handoff.md` if interrupted or handing off.

## Forbidden

- Do not save secrets, tokens, passwords, credentials, private URLs, or personal account details.
- Do not silently overwrite user changes.
- Do not fake verification.
- Do not run destructive commands without explicit approval.
- Do not modify security, privacy, cost, deployment, dependencies, public APIs, or data models without proper authority.
