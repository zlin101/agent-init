# Agent Native Init Protocol Model

## Purpose

Agent Native Init adds a durable collaboration layer to a software project. It is not a business framework, role hierarchy, CI system, or LLM runtime.

The core principle:

> Agents are trusted by task contract, not identity, and work closes only through acceptance gates.

## Layers

- Entry layer: `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `GEMINI.md`, or similar project-level Agent instructions.
- Context layer: `vault/index.md`, `vault/project.md`, `vault/runtime.md`, and optional `vault/details/*`.
- Governance layer: `vault/governance.md` and `vault/tasks/*`.
- Decision layer: `vault/decisions.md`.
- Handoff layer: `vault/handoff.md`.
- Workflow layer: `skills/*/SKILL.md`.
- Profile layer: language or framework defaults only when the project type is known.

## Required Vault Files

Create these files unless merging with an existing equivalent:

```text
vault/
  index.md
  project.md
  runtime.md
  governance.md
  decisions.md
  handoff.md
  collaboration.md
  tasks/
    README.md
    .gitkeep
```

Create `vault/details/*` only when repeated long-context reads justify them.

## File Responsibilities

- `vault/index.md`: routing table for what context to read and when to update memory.
- `vault/project.md`: stable project purpose, scope, boundaries, and current phase.
- `vault/runtime.md`: short current state, active task pointer, checks, risks, and next steps.
- `vault/governance.md`: task levels, authority levels, task contracts, acceptance gates, escalation, and handoff.
- `vault/decisions.md`: durable architecture, dependency, scope, workflow, and governance decisions.
- `vault/handoff.md`: recent transfer context for interrupted or resumed work.
- `vault/collaboration.md`: soft collaboration preferences that cannot override hard governance.
- `vault/tasks/*`: tracked or governed task contracts, execution records, verification, and closure notes.
- `skills/*`: reusable Agent workflows.

## Task Levels

- Level A, simple task: low risk, usually one session, one or two files, no architecture/API/dependency/data-model impact. Record in `vault/runtime.md`.
- Level B, tracked task: multi-file, auditable, needs design plus docs/tests/verification, may need handoff. Record in `vault/tasks/TASK-xxxx-short-title.md`.
- Level C, governed task: changes architecture, public API, data model, framework, external services, security, privacy, cost, deployment, or Agent governance. Record in task file and `vault/decisions.md`; usually requires user confirmation.

## Authority Levels

- Authority 0: read-only analysis.
- Authority 1: low-risk local edit.
- Authority 2: scoped change after stating boundaries and checks.
- Authority 3: approval required for high-impact work.
- Authority 4: forbidden actions, including secrets, fake verification, destructive commands without authorization, and silent overwrite of user changes.

## Task Contract Fields

Tracked and governed tasks should include:

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

Do not close work until:

1. Acceptance criteria are checked one by one.
2. Required verification has run and results are recorded.
3. Code, tests, docs, and vault memory are synchronized when applicable.
4. `vault/runtime.md` is updated.
5. Durable decisions are recorded in `vault/decisions.md`.
6. Unfinished work or risks are recorded in the task file or `vault/handoff.md`.
7. No high-impact change is hidden.

Passing tests alone is not completion.

## Execution Patterns

- Plan first: clarify goal, boundary, acceptance, verification, files, and non-goals before editing.
- Context grounded: read local project context before applying generic advice.
- Checkpointable: keep long tasks recoverable through task files, runtime, and handoff.
- Human signal: return architecture, cost, safety, privacy, deployment, and ambiguous product decisions to the user.
- Workflow compounding: repeated stable workflows become focused skills, not bloated entry files.

## Existing Project Adoption Boundary

Adoption mode adds or merges Agent collaboration files only.

Allowed by default:

- Agent entry files
- `vault/`
- `skills/`
- a very short README collaboration note, only after stating intent

Forbidden without explicit user approval:

- business source
- tests
- dependency and lock files
- build, deployment, or CI files
- database migrations
- environment files
- large existing docs rewrites
- secrets or credentials

## Collaboration Profile

`vault/collaboration.md` records stable collaboration preferences and observed patterns. It is a soft profile, not a hard rule. It cannot override the user’s current instruction, Agent entry files, governance, task contracts, decisions, safety, permissions, testing, cost, or deployment constraints.
