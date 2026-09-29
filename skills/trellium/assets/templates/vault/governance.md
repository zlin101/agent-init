# Governance

## Core Rule

Agents are trusted by task contract, not identity. Work closes only through acceptance gates.

## Task Levels

Classification follows one canonical order: a Level C risk domain → C; otherwise clearly high interruption-recovery or collaboration cost → B; otherwise → A. Scale only prompts further judgment and never decides the level alone; a later unexpected interruption never retroactively rewrites the original classification.

### Level C: Governed Task

Risk domains (a one-line change included): security/privacy, public APIs or external contracts, persistent data/migrations, deployment/production behavior, dependency changes, material cost/quota, architecture (durable architectural decisions), governance rules/policy. Record in a task file and `vault/decisions.md`; usually request user approval.

### Level B: Tracked Task

Outside Level C risk domains but with clearly high recovery or coordination cost: expected to cross sessions, a real handoff, multi-agent or multi-person ownership, external system state, multi-stage gates, acceptance state under continuous tracking, or execution state not cheaply recoverable from diff/tests. Record in `vault/tasks/TASK-xxxx-short-title.md`.

### Level A: Simple Task

Low risk with low recovery and coordination cost: diff, workspace, and tests can rebuild the state cheaply. No persisted TASK lifecycle by default; update `vault/runtime.md` only when project-global runtime actually changes.

## Task Lifecycle

`draft | active | blocked | ready_for_review | accepted | superseded`

Lifecycle, authority, current slice, and gate results are owned only by the task file's `trellium-task-state` block; `runtime.md` persists no TASK projection. Paused-and-shelved work lives in `parked.md`, not in a lifecycle value. Level A has no persisted TASK lifecycle and recovers from the workspace, Git diff, and tests.

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
- Authority level (the number lives in the `trellium-task-state` block; keep no second editable copy)
- Allowed changes
- Requires approval
- Forbidden changes
- Acceptance criteria
- Required verification
- Required memory updates
- Handoff requirement

The task state block never grants approvals; behavior boundaries stay in the task body and user instructions.

## Acceptance Gates

Before closing work:

1. Check every acceptance criterion.
2. Run and record required verification.
3. Sync code, tests, docs, and vault memory where applicable.
4. Update `vault/runtime.md`.
5. Record durable decisions in `vault/decisions.md`.
6. Record unfinished work or risks in the task file (the acceptance gate does not treat ordinary handoff as a risk ledger).
7. Disclose all high-impact changes.

Tests passing alone is not completion.

For tasks using local lifecycle semantics (`storage_mode=local` or `private`), entering `accepted` also requires the
Durable Knowledge Disposition in Memory Updates (`none — <reason>` or
`distilled — <canonical destinations>`; an unfilled line counts as `pending`
and blocks `ready_for_review` and `accepted`). Wrong contracts go to
`superseded` immediately — the gate never blocks that. Tracked tasks default
to `not_applicable`.

## Escalation

Escalate or ask the user when requirements are ambiguous, scope expands, high-impact files are involved, required checks fail, docs conflict with implementation, or user changes conflict with the plan.

## Handoff

Handoff is dual-triggered: create or update `vault/handoff.md` only when (1) a real interruption occurred, and (2) at least one recovery-relevant fact is not cheaply derivable from canonical state (TASK file, Git, working tree, rerun tests, durable knowledge). Normal completion, waiting for acceptance, a finished review, an open lifecycle alone, an ordinary next step, or a derivable clean session boundary never writes handoff.

Each entry (named after its task id, or SESSION) holds exactly three sections:

- Why interrupted
- Transient context not captured elsewhere
- Exact resume point

Recovery order: read the TASK file, live Git/working tree, and rerun tests first; apply the handoff delta second; delete the entry once consumed. Branch, HEAD, and dirty files are read live from Git at resume time; handoff stores no state copies.
