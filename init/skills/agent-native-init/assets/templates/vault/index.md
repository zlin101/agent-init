# Vault Index

This file routes Agents to the right project context. Do not use it as a long project history.

## Default Reading

For non-trivial work, read:

1. `AGENTS.md`
2. `vault/index.md`
3. `vault/runtime.md`
4. `vault/governance.md`

First project entry:

- `vault/project.md`

Interrupted or resumed work:

- `vault/handoff.md`

Tracked or governed work:

- active file under `vault/tasks/`

## File Responsibilities

- `project.md`: stable project purpose, scope, boundaries, and phase.
- `runtime.md`: current state, active task, checks, risks, and next steps.
- `governance.md`: task levels, authority, task contracts, acceptance gates, escalation, and handoff.
- `decisions.md`: durable architecture, dependency, workflow, scope, and governance decisions.
- `handoff.md`: recent transfer state for interrupted work.
- `collaboration.md`: soft collaboration preferences that cannot override hard rules.
- `tasks/README.md`: task file status flow and template.
- `details/*`: optional long context, created only when repeated reads justify it.

## Detail Routing

- Architecture: `vault/details/architecture.md` and `vault/decisions.md`.
- Development tools, dependencies, tests, or environment: `vault/details/development.md`.
- API contracts: `vault/details/api.md` and `vault/decisions.md`.
- Agent, LLM, prompt, or tool behavior: `vault/details/agent.md` and `vault/decisions.md`.
- Domain knowledge: `vault/details/domain.md`.
- Collaboration preferences: `vault/collaboration.md`.

## Update Rules

- Update `runtime.md` after non-trivial work.
- Update `tasks/*` for Level B or Level C work.
- Update `decisions.md` for durable decisions.
- Update `handoff.md` when interrupted or handing off.
- Move long details out of `runtime.md`.
