# Templates Guide

## How To Use Templates

Copy files from `assets/templates/` into the target project and adapt them. Keep the target project's real facts, commands, and constraints. Delete guidance text that is not relevant.

Do not copy placeholders as if they were facts.

## Template Map

- `AGENTS.md`: project-level Agent entry rules.
- `vault/index.md`: context routing and memory update rules; carries the `trellium-policy` project policy block (budgets and TASK storage), includes the task/authority cheat sheet.
- `vault/project.md`: stable project purpose and scope.
- `vault/runtime.md`: project-global current state and optional navigation Focus; TASK state and inventory come directly from task-state blocks.
- `vault/governance.md`: task levels, authority levels, task lifecycle, contracts, and acceptance gates.
- `vault/decisions.md`: durable decisions; four lifecycle statuses; index when over budget (bodies move to `vault/decisions/`).
- `vault/handoff.md`: transient delta written only when a real interruption leaves a non-derivable recovery fact; three sections per entry (Why interrupted / Transient context not captured elsewhere / Exact resume point); live Git facts stay out of it.
- `vault/parked.md`: cold index of user-parked items (P-xxxx entries); read only when mentioned; cleanup is proposal-only.
- `vault/collaboration.md`: collaboration preferences and observed patterns.
- `vault/tasks/README.md`: task lifecycle flow, `trellium-task-state` block rules, task template, and review ledger template.
- `skills/agent-task/SKILL.md`: reusable workflow for non-trivial project tasks.

## New Project Initialization

Use most templates directly, then fill project facts:

1. Replace project name and purpose in `vault/project.md`.
2. Set the current stage, optional Focus task, and checks in `vault/runtime.md`; do not copy TASK state into runtime.
3. Leave `vault/parked.md` in template state when nothing is parked; do not pre-fill.
4. Keep `vault/governance.md` conservative.
5. Add project code and tests only when a concrete profile or user request justifies them.

## Existing Project Adoption

Merge carefully:

1. If `AGENTS.md` already exists, preserve existing project rules and add vault/governance routing without weakening them.
2. If the project already has decisions or ADRs, do not migrate history. Add a pointer in `vault/decisions.md`.
3. If the project already has docs, avoid rewriting them. Add only a short collaboration note if useful and approved.
4. Do not touch business engineering files unless the user explicitly expands scope.
5. Do not create `vault/decisions/` or `vault/tasks/archive/` during adoption; first compaction creates them.

## Required Customization

Always customize:

- project name
- project purpose
- current stage
- required verification command
- technology-specific constraints
- existing docs or decision locations
- active task state

Never customize by adding secrets, local absolute paths, private service URLs, personal account details, or default model/provider credentials.
