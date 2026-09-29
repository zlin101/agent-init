# Vault Index

This file routes Agents to the right project context and carries the project
policy block. Do not use it as a long project history or a second status
surface.

<!-- trellium-policy
{
  "schema_version": 1,
  "task_storage": "tracked",
  "budgets": {
    "runtime": {"max_lines": 120, "max_recent_entries": 10},
    "handoff": {"max_lines": 100, "max_entries": 3},
    "decisions": {"max_lines": 150, "max_records": 8},
    "parked": {"max_lines": 60, "max_entries": 20},
    "tasks": {"max_active_tasks": 40}
  }
}
-->

The block above is the single source for project budgets and TASK storage.
`task_storage: tracked` keeps task files in version control; `local` keeps
task files, review ledgers, and archive out of Git (Accepted conclusions must
then be distilled into `decisions.md` or other published truth). Budget
numbers elsewhere in the protocol are initialization defaults, not project
policy. A missing policy block means a legacy project: report it, and do not
substitute hidden defaults.

## Task And Authority Cheat Sheet

- Level C, governed: any risk domain makes it governed, a one-line change included (security/privacy, public API/external contracts, persistent data/migrations, deployment, dependencies, cost/quota, architecture, governance rules); record in `tasks/*` and `decisions.md`; needs user confirmation.
- Level B, tracked: outside Level C risk domains but recovery or coordination cost is clearly high (cross-session, real handoff, multi-owner, external state, multi-stage gates); record in `tasks/*`.
- Level A, simple: low risk, low recovery and coordination cost, no persisted TASK lifecycle by default; record in `runtime.md` only when project-global runtime changes.
- Scale (file counts, acceptance-item counts) only prompts judgment and never decides the level alone.
- Authority: 0 read-only / 1 local edit / 2 scoped change / 3 approval required / 4 forbidden.
- Unclear classification or governance-rule work: read full `governance.md`.

## Default Reading

For non-trivial work, read:

1. `AGENTS.md`
2. `vault/index.md` (with the cheat sheet)
3. `vault/runtime.md`

For Level B or Level C work, unclear classification, or governance-rule changes, also read:

- `vault/governance.md`

First project entry:

- `vault/project.md`

Genuinely interrupted work (skip for a derivable clean boundary):

- `vault/handoff.md`

Tracked or governed work:

- active file under `vault/tasks/`

When the user mentions a parked, shelved, or suspended item:

- `vault/parked.md`

## File Responsibilities

- `index.md` (this file): routing + the `trellium-policy` project policy block; no runtime state.
- `project.md`: stable project purpose, scope, boundaries, and phase.
- `runtime.md`: project-global current state, optional navigation Focus, checks, risks, and next steps. It owns no TASK state or inventory.
- `governance.md`: task levels, authority, task contracts, acceptance gates, escalation, and handoff.
- `decisions.md`: durable decision index and, before the split, full records; bodies move to `vault/decisions/D-xxxx-*.md` after indexing.
- `handoff.md`: transient delta for real interruptions; each entry is named after its task id (or SESSION) and holds exactly three sections (Why interrupted / Transient context not captured elsewhere / Exact resume point); recovery reads TASK and live Git/tests first, applies the delta, then deletes the entry.
- `parked.md`: cold index of user-parked items; read only when mentioned, never on the default path.
- `collaboration.md`: soft collaboration preferences that cannot override hard rules.
- `tasks/README.md`: task file lifecycle flow, state block, and template.
- `details/*`: optional long context, created only when repeated reads justify it.

## Detail Routing

- Architecture: `vault/details/architecture.md` and `vault/decisions.md`.
- Development tools, dependencies, tests, or environment: `vault/details/development.md`.
- API contracts: `vault/details/api.md` and `vault/decisions.md`.
- Agent, LLM, prompt, or tool behavior: `vault/details/agent.md` and `vault/decisions.md`.
- Domain knowledge: `vault/details/domain.md`.
- Collaboration preferences: `vault/collaboration.md`.

## Update Rules

- Hot-file update discipline: keep section order fixed, one item per line; replace the single matching line on a status or progress change instead of rewriting whole sections.
- Update `runtime.md` after non-trivial work only when project-global runtime changes; Focus is navigation only.
- Update `tasks/*` for Level B or Level C work: the `trellium-task-state` block is the only lifecycle, authority, slice, and gate owner.
- Update `decisions.md` for durable decisions.
- Update `handoff.md` only when a real interruption leaves a non-derivable transient delta.
- Record parked items in `parked.md` when the user suspends them; promote back to a task file when mentioned again.
- Move long details out of `runtime.md`.
- For local tasks (`task_storage=local`), absence from a fresh clone follows the storage contract; `runtime.md` is not a recovery copy (see governance.md).
- Check hot-file budgets when updating them; current limits live in the `trellium-policy` block above.
- A budget exceed appears only as a repository-health warning in `trellium.py check` and never blocks task acceptance; compaction is triggered by explicit intent (owner request / independent maintenance TASK / task contract): measure → classify → restructure → verify → record. Semantic judgments (Superseded / Merged / Expired) are proposals only; keep Active until the user confirms.
