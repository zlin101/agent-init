# Templates Guide

## How To Use Templates

Copy files from `assets/templates/` into the target project and adapt them. Keep the target project's real facts, commands, and constraints. Delete guidance text that is not relevant.

Do not copy placeholders as if they were facts.

## Template Map

- `AGENTS.md`: project-level Agent entry rules.
- `vault/index.md`: context routing and memory update rules.
- `vault/project.md`: stable project purpose and scope.
- `vault/runtime.md`: current state and active task pointer.
- `vault/governance.md`: task levels, authority levels, contracts, and acceptance gates.
- `vault/decisions.md`: durable decisions.
- `vault/handoff.md`: recent transfer state.
- `vault/collaboration.md`: collaboration preferences and observed patterns.
- `vault/tasks/README.md`: task file status flow and template.
- `skills/agent-task/SKILL.md`: reusable workflow for non-trivial project tasks.

## New Project Initialization

Use most templates directly, then fill project facts:

1. Replace project name and purpose in `vault/project.md`.
2. Set the current stage and checks in `vault/runtime.md`.
3. Keep `vault/governance.md` conservative.
4. Add project code and tests only when a concrete profile or user request justifies them.

## Existing Project Adoption

Merge carefully:

1. If `AGENTS.md` already exists, preserve existing project rules and add vault/governance routing without weakening them.
2. If the project already has decisions or ADRs, do not migrate history. Add a pointer in `vault/decisions.md`.
3. If the project already has docs, avoid rewriting them. Add only a short collaboration note if useful and approved.
4. Do not touch business engineering files unless the user explicitly expands scope.

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
