# Governance

## Core Rule

Agents are trusted by task contract, not identity. Work closes only through acceptance gates.

## Task Levels

### Level A: Simple Task

Low risk, normally one session, one or two files, no architecture/API/dependency/data-model impact. Record in `vault/runtime.md`.

### Level B: Tracked Task

Use when work needs tracking, affects more than two files, has more than three acceptance criteria, needs design plus verification, may need handoff, or should be auditable. Record in `vault/tasks/TASK-xxxx-short-title.md`.

### Level C: Governed Task

Use when work changes architecture, public APIs, data models, frameworks, external services, security, privacy, cost, deployment, or Agent governance. Record in a task file and `vault/decisions.md`; usually request user approval.

## Authority Levels

- Authority 0: read-only analysis.
- Authority 1: low-risk local edit.
- Authority 2: scoped change after stating boundaries and checks.
- Authority 3: approval required for high-impact work.
- Authority 4: forbidden.

## Forbidden

- Saving real secrets, tokens, passwords, credentials, private URLs, or personal account details.
- Faking verification.
- Silently overwriting user changes.
- Destructive commands without explicit approval.
- Unit tests that call real external services.

## Task Contract

Tracked and governed tasks must include:

- Objective
- Scope and out of scope
- Context required
- Capability tags
- Authority level
- Allowed changes
- Requires approval
- Forbidden changes
- Acceptance criteria
- Required verification
- Required memory updates
- Handoff requirement

## Acceptance Gates

Before closing work:

1. Check every acceptance criterion.
2. Run and record required verification.
3. Sync code, tests, docs, and vault memory where applicable.
4. Update `vault/runtime.md`.
5. Record durable decisions in `vault/decisions.md`.
6. Record unfinished work or risks in the task file or `vault/handoff.md`.
7. Disclose all high-impact changes.

Tests passing alone is not completion.

## Escalation

Escalate or ask the user when requirements are ambiguous, scope expands, high-impact files are involved, required checks fail, docs conflict with implementation, or user changes conflict with the plan.

## Handoff

When interrupted or transferring work, update `vault/handoff.md` with:

- Current objective
- Completed
- In progress
- Failed attempts
- Workspace state
- Known risks
- Next best action
- Files to read first
