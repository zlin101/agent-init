---
name: agent-native-init
description: Use when adding durable Agent collaboration rules, project memory, task governance, handoff, or review gates to a new or existing software project.
---

# Agent Native Init

## Overview

Install an Agent-native collaboration layer into a project: concise Agent entry rules, a vault memory system, task-contract governance, handoff, reusable workflows, and review gates.

This skill is self-contained. It does not require an `init/` directory in the target project.

## Required References

Read these bundled references before editing a target project:

- `references/protocol-model.md` for the concepts and acceptance gates.
- `references/templates-guide.md` for how to use the bundled templates.

Use files under `assets/templates/` as starting points. Adapt names, checks, and project facts to the target project; do not copy placeholders blindly.

## Mode Decision

Choose one mode before editing:

- **New project initialization**: use when the target is empty, disposable, or explicitly asks for a new Agent-ready scaffold.
- **Existing project adoption**: use when the target already has source code, dependencies, tests, build files, deployment files, CI, or project docs.

If uncertain, choose existing project adoption. It is safer because it only adds or merges the Agent collaboration layer by default.

## Task Contract

Before editing, state:

- Objective
- Mode
- In scope and out of scope
- Files expected to change
- Authority level and user confirmations needed
- Acceptance criteria
- Verification commands

If the project already has `vault/tasks/`, create or update a task file. If not, keep the contract in working notes until the vault exists, then write it to `vault/tasks/`.

## New Project Initialization

Create the smallest useful project:

1. Add Agent entry files such as `AGENTS.md`; add tool-specific companions only when useful.
2. Add the required `vault/` files.
3. Add `skills/agent-task/SKILL.md`.
4. Add source, tests, dependencies, and README only if the user requested a concrete project type.
5. Run the smallest meaningful check.
6. Record current state in `vault/runtime.md` and durable choices in `vault/decisions.md`.

Do not add frameworks, services, databases, CI, deployment, LLM SDKs, or credentials until the project genuinely needs them.

## Existing Project Adoption

Preserve the existing project:

1. Read-only scan first: root files, Agent entry files, README/docs, source layout, dependency files, tests, build/deploy/CI files, existing memory or decision records, and dirty worktree state.
2. Present an adoption plan listing only Agent collaboration layer changes.
3. Merge existing Agent entry rules instead of overwriting them.
4. Create or merge `vault/` files and `skills/agent-task/SKILL.md`.
5. Record in `vault/project.md` that this is adoption into an existing project.
6. Record adoption state, risks, and next steps in `vault/runtime.md`.

Without explicit user approval, do not modify business source, tests, dependency files, lock files, build files, deployment files, CI, database migrations, environment files, or large existing docs.

## Review And Reflection

Run at least two rounds before claiming completion.

### Round 1 - Protocol Coverage Review

Check:

- Agent entry file routes non-trivial tasks to `vault/index.md`, `vault/runtime.md`, and `vault/governance.md`.
- Required vault files exist.
- Governance covers task levels, authority levels, task contract fields, acceptance gates, escalation, and handoff.
- `skills/agent-task/SKILL.md` exists and is focused on task execution.
- `vault/runtime.md` is short current state, not a long log.
- `vault/decisions.md` captures durable choices.
- `vault/collaboration.md` exists when collaboration preferences are useful.

Fix gaps before continuing.

### Round 2 - Safety And Minimality Review

Reflect:

- Did any change exceed the selected mode?
- In adoption mode, did any forbidden engineering file change?
- Did the work add dependencies, frameworks, services, secrets, local absolute paths, ports, model names, or credentials?
- Are verification commands concrete and appropriate for the project?
- Are remaining risks and user decisions recorded?

If a round finds issues, fix them and repeat the relevant round.

## Verification

Run the verification named in the task contract or target `vault/runtime.md`.

For documentation-only adoption, use read-only checks such as listing expected files and searching required terms. For code scaffolds, run the smallest project test command. Do not run commands that mutate engineering state in adoption mode unless the user approved them.

## Completion Report

Report:

- Mode used.
- Files created or changed.
- Areas explicitly not touched.
- Verification command and result.
- Review/reflection findings.
- Remaining risks or decisions.
