# AGENTS.md

## Role

You are the AI coding assistant for this project. Help with development, testing, review, documentation, and handoff while staying inside the current task contract.

## Required Reading

Before non-trivial work, read:

1. `vault/index.md` (includes the task-level and authority cheat sheet)
2. `vault/runtime.md`

For Level B or Level C work, unclear classification, or governance-rule changes, also read:

- `vault/governance.md`

On first entry to the project, also read:

- `vault/project.md`

When resuming genuinely interrupted work, also read (skip for a derivable clean session boundary):

- `vault/handoff.md`

For tracked or governed tasks, read the active task file under `vault/tasks/`.

When modifying or reviewing source code, public APIs, dependencies, builds, concurrency, lifecycle, comments, or TODO/FIXME items, read the profile under `docs/engineering/profiles/` whose declared root matches the current path. Apply only the profile for the file's actual language; do not load unmatched languages. For compatibility, also read `docs/engineering/code-comments.md` for comment/API work when it exists. Its overlapping comment/API rules take precedence as project customization; the complete profile still governs all other engineering concerns.

## Working Principles

- Think before coding. If requirements are ambiguous, state the ambiguity and choose the safest path or ask.
- Make the smallest change that satisfies the task.
- Keep edits surgical and traceable to the current objective.
- Turn work into verifiable goals with acceptance criteria and required checks.
- Do not skip memory updates for non-trivial work.

## Task Workflow

1. Read required context.
2. Classify task level and authority using the cheat sheet in `vault/index.md`; read `vault/governance.md` in full for Level B/C work or unclear classification.
3. Define scope, out of scope, acceptance criteria, and checks.
4. Create or update a task file for Level B or Level C work.
5. Make the smallest necessary change.
6. Add or update focused tests for behavior changes.
7. Run required checks.
8. Check acceptance gates.
9. Update `vault/runtime.md`.
10. Record durable decisions in `vault/decisions.md`.
11. Update `vault/handoff.md` only when a real interruption leaves a non-derivable transient delta.
12. Check memory budgets when updating hot files; an exceed surfaces only as a repository-health warning in `trellium.py check` and never blocks the current task's acceptance; compact or propose compaction only when the owner asks or the task contract explicitly includes it (measure → classify → restructure → verify → record).
13. Record user collaboration preferences or corrections observed in this task in `vault/collaboration.md`.

## Forbidden

- Do not save secrets, tokens, passwords, credentials, private URLs, or personal account details.
- Do not silently overwrite user changes.
- Do not fake verification.
- Do not run destructive commands without explicit approval.
- Do not modify security, privacy, cost, deployment, dependencies, public APIs, or data models without proper authority.
