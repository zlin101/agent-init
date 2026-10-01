# Trellium Protocol Model

## Purpose

Trellium adds a durable collaboration layer to a software project. It is not a business framework, role hierarchy, CI system, or LLM runtime.

The core principle:

> Agents are trusted by task contract, not identity, and work closes only through acceptance gates.

## Layers

- Entry layer: shared `AGENTS.md`, plus tool-specific compatibility files only when a target tool still requires one. Claude Code reads `AGENTS.md` directly.
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
  parked.md
  collaboration.md
  tasks/
    README.md
    .gitkeep
```

## Memory Tiers And Compaction

| Tier | Files | Lifecycle |
| --- | --- | --- |
| Hot files | `runtime.md`, `handoff.md`, `decisions.md` | Frequently updated; budgeted; compaction targets |
| Governance files | `governance.md`, `collaboration.md`, `parked.md` | Event-driven updates; compaction only proposes |
| Structural files | `index.md`, `project.md`, `tasks/README.md` | Rarely updated |
| Archive | `tasks/<task-id>.md`, `decisions/`, `details/*` | Append-only |

Budgets: runtime ≤ 120 lines (Recent Changes ≤ 10 entries); handoff ≤ 3 entries or 100 lines; decisions ≤ 150 lines or 8 full records; parked ≤ 60 lines or 20 entries; tasks ≤ 40 current task files (excluding archive and review ledgers). These are initialization defaults; the project's current budgets and TASK storage live once in the `trellium-policy` block in `vault/index.md`. `trellium.py check <target>` measures hot files and only enforces explicitly configured thresholds; a missing policy block is reported as legacy, never substituted with hidden defaults.

Read-only status summary: `trellium.py status <target>` (2026.09.5) scans canonical task-state blocks into an owner view — navigation focus, open-task classification (draft/active/blocked/ready_for_review with authority/slice/gates verbatim and task path), closed tasks as counts only, and explicit unresolved task-state entries with finding codes. Focus is navigation only; lifecycle and authority are never inferred. It is not an approval inbox, and exit codes match `check` (`2` errors / `0` warnings-only / `1` operational).

Compaction runs five phases: measure → classify → restructure → verify → record. Non-semantic moves (relocating bodies, indexing, marking Active, demoting paused tasks to parked entries) run autonomously; semantic judgments (`Superseded by D-xxxx` / `Merged into D-xxxx` / `Expired`, parked cleanup) are proposal-only, confirmed by the user in batch, and stay `Active` until confirmed. Compaction is a dedicated commit containing only `vault/` changes. Configured budget exceeds are repository-health warnings in `trellium.py check`; compaction itself is independent maintenance triggered by explicit intent, never an automatic task-close step.

Decision indexing: decisions.md becomes a pure index and bodies move to `vault/decisions/D-xxxx-slug.md`. Index principle: growth goes to directories, reading goes through indexes.

The entry-reading contract lives in `30-agent-entry.md` and is implemented by the project entry file (default set and conditional triggers); this reference does not restate the flow.

## State And Policy Blocks

Two small versioned JSON blocks carry current-state facts; everything else stays Markdown.

`trellium-task-state` sits right after a Level B/C task title. Required fields: `schema_version` (integer `1`), `task_id` (`TASK-NNNN`, matching the file name), `level` (`B | C`), `authority_level` (integer 0..4), `lifecycle`. Optional: `current_slice` (non-empty string) and `gates` (open gate ids mapped to `pending | in_progress | passed | partial | blocked | not_authorized | not_applicable`). Unknown fields are invalid. It is the single owner of lifecycle, authority level, current slice, and gate results; it never grants approvals. Task files without a block are legacy (reported, not guessed); review ledgers and `tasks/archive/` carry no block.

`trellium-policy` sits at the top of `vault/index.md`. Required: `schema_version` (`2`) and `storage_mode` (`tracked | local | private`); optional `budgets` per hot file. Legacy schema v1 (`task_storage`: `tracked | local`) remains parseable and is never auto-rewritten. It is the single source for project budgets and storage. First adoption requires an explicit owner choice through the storage gate in `70-adoption-flow.md`; no reply allows only read-only scanning. Local is a recommendation, not default write authorization; reuse an explicit choice and preserve valid existing policy. In Local mode, task files, review ledgers, and archive stay out of Git while the collaboration core remains tracked; Accepted conclusions must then be distilled into published truth. Choose `tracked` when the complete task trail should be shared. Choose `private` to keep every target-project Trellium-managed file out of Git, while terminal TASK/review evidence is retained in the local History Store: untracked, precisely ignored via the canonical trellium-private block in `.git/info/exclude`, verified by the reverse privacy gate, with the read-only `private_preflight` probe run before adopt (see 70-adoption-flow.md, Private 存储模式). Local adoption creates a narrow `vault/tasks/.gitignore` (private does not - the whole vault is covered by the private block); tools never auto-migrate or auto-untrack. Before a local task enters `accepted`, its Memory Updates record a Durable knowledge disposition (`none` with a reason, or `distilled` listing canonical destinations; unfilled counts as `pending` and blocks `ready_for_review`/`accepted`). In a fresh clone an ignored local task file is absent by storage contract; runtime provides no recovery copy.

## Task Lifecycle

`draft | active | blocked | ready_for_review | accepted | superseded`

The `trellium-task-state` block is the only persisted owner of lifecycle, authority, current slice, and gate results; `runtime.md` persists no TASK projection. Paused-and-shelved work lives in `parked.md`, not in a lifecycle value. Level A has no persisted TASK lifecycle and recovers from the workspace, Git diff, and tests.

## File Responsibilities

- `vault/index.md`: routing table plus the `trellium-policy` project policy block; no runtime state.
- `vault/project.md`: stable project purpose, scope, boundaries, and current phase.
- `vault/runtime.md`: short project-global current state, optional navigation Focus, checks, risks, and next steps. Focus owns no task state, authority, or active-task inventory.
- `vault/governance.md`: task levels, authority levels, task lifecycle, task contracts, acceptance gates, escalation, and handoff.
- `vault/decisions.md`: durable decision index and lifecycle records (Active / Superseded / Merged / Expired); bodies move to `vault/decisions/*` after indexing.
- `vault/handoff.md`: transient delta written only when a real interruption leaves a non-derivable recovery fact; each entry (task id, or SESSION) holds exactly three sections — Why interrupted, Transient context not captured elsewhere, Exact resume point; recovery reads TASK/live Git/tests first, applies the delta, then deletes it.
- `vault/parked.md`: cold index of user-parked items; read only when mentioned, never on the default path; promote back to a task file when resumed.
- `vault/collaboration.md`: soft collaboration preferences that cannot override hard governance.
- `vault/tasks/*`: tracked or governed task contracts, execution records, verification, and closure notes.
- `skills/*`: reusable Agent workflows.

## Task Levels

Classification order: a Level C risk domain → C; otherwise clearly high recovery or coordination cost → B; otherwise → A. Scale only prompts judgment and never decides the level alone.

- Level C, governed task: any risk domain makes it governed — a one-line change included (security/privacy, public API or external contracts, persistent data/migrations, deployment/production behavior, dependencies, cost/quota, architecture (durable architectural decisions), governance rules). Record in task file and `vault/decisions.md`; usually requires user confirmation.
- Level B, tracked task: outside Level C risk domains but recovery or coordination cost is clearly high (cross-session, real handoff, multi-owner, external system state, multi-stage gates, execution state not cheaply recoverable from diff/tests). Record in `vault/tasks/TASK-xxxx-short-title.md`.
- Level A, simple task: low risk, low recovery and coordination cost. No persisted TASK lifecycle by default; recover from the workspace, Git diff, and tests.

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
- Authority level (the number lives in the task state block; keep no second editable copy)
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
6. Unfinished work or risks are recorded in the task file (not an ordinary handoff).
7. No high-impact change is hidden.

Passing tests alone is not completion.

## Execution Patterns

- Plan first: clarify goal, boundary, acceptance, verification, files, and non-goals before editing.
- Context grounded: read local project context before applying generic advice.
- Checkpointable: keep long tasks recoverable through task files, runtime, live Git/tests, and — only for real interruptions that leave a non-derivable delta — a transient-delta handoff.
- Human signal: return architecture, cost, safety, privacy, deployment, and ambiguous product decisions to the user.
- Review ledger: converge multi-round review through a `TASK-xxxx-review.md` ledger — one batched write per round instead of message ping-pong; archive into the task file once converged.
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
