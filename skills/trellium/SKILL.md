---
name: trellium
description: Use when adding or upgrading durable Agent collaboration rules, project memory, task governance, handoff, or review gates in a new or existing software project.
---

# Trellium

## Overview

Install and upgrade an Agent-native collaboration layer in a project: concise Agent entry rules, a vault memory system, task-contract governance, handoff, reusable workflows, and review gates.

This skill is self-contained. It does not require an `init/` directory in the target project.

## Required References

Read these bundled references before editing a target project:

- `references/protocol-model.md` for the concepts and acceptance gates.
- `references/templates-guide.md` for how to use the bundled templates.

`references/protocol-source/` is the authoritative generated protocol snapshot and preserves the complete `init/...` path layout. The canonical source is currently authored in Chinese; use the English concise references for the normal flow and consult the source selectively:

- New project initialization: read `references/protocol-source/init/protocol/60-initialization-flow.md`.
- Existing project adoption: read `references/protocol-source/init/protocol/70-adoption-flow.md`.
- Known project type: read the matching profile under `references/protocol-source/init/protocol/profiles/`.
- Work involving a specific governance topic: use `references/protocol-source/init/INIT.md` to locate the relevant module, resolving its `init/...` paths under `references/protocol-source/`.

If a concise reference conflicts with the authoritative protocol, follow `references/protocol-source/init/`. Do not edit this generated directory directly.

Use files under `assets/templates/` as starting points. Adapt names, checks, and project facts to the target project; do not copy placeholders blindly.

## Mode Decision

Choose one mode before editing:

- **New project initialization**: use when the target is empty, disposable, or explicitly asks for a new Agent-ready scaffold.
- **Existing project adoption**: use when the target already has source code, dependencies, tests, build files, deployment files, CI, or project docs.

If uncertain, choose existing project adoption. It is safer because it only adds or merges the Agent collaboration layer by default.

## Install And Upgrade (Bundled Script First)

This package bundles a deterministic installer/upgrader at `assets/trellium.py`; prefer it, and layer Agent-driven semantic migration on top.

- Before first adoption, ask the owner to choose TASK storage. Recommend and default to `local` when the owner does not specify: only `vault/tasks/TASK-*.md`, review ledgers, and archive entries stay local, while the collaboration core remains in Git. Choose `tracked` when the complete task trail should be shared. After running `python3 assets/trellium.py adopt <target>`, the agent records the choice in `vault/index.md`; for local storage it also creates a narrow `vault/tasks/.gitignore` (`TASK-*.md`, `*-review.md`, `archive/`), while tracked storage adds no such ignore rules. The script only adds missing files by default; an existing `AGENTS.md` gets a marked section appended, never overwritten. When languages are known, repeat `--profile go-backend=<root>` / `--profile python-backend=<root>`; each selected profile becomes a complete project-local document under `docs/engineering/profiles/` with a one-hop root-scoped AGENTS route; `docs/engineering/code-comments.md` stays as the compatibility carrier for comment/API rules (overlaps follow the carrier; full rules in `references/protocol-source/init/protocol/70-adoption-flow.md`, “Profile 工程规范”). Languages are never guessed automatically.
- Protocol-content updates do not require reinstalling this Skill: add `--fetch` to any command to fetch the latest tagged release from GitHub and run it with that release's script and templates (cached under `~/.cache/trellium/`; downgrades are refused). Reinstall the Skill only when the SKILL workflow or the script itself changes.
- Upgrading an adopted project:
  1. `python3 assets/trellium.py diff <target>` — read-only report of what would change, what is never touched, and pending migration playbook entries.
  2. `python3 assets/trellium.py upgrade <target> --apply` — executes the safe subset; conflicts produce proposals under the target's `vault/.upgrade/<version>/`.
  3. The agent merges each proposal semantically (preserving every local customization); the user confirms item by item.
  4. `python3 assets/trellium.py upgrade <target> --complete` — finalizes the round.
- Projects without a stamp (missing `vault/.agent-init.json`): run `python3 assets/trellium.py baseline <target>` first.
- Validating a project: `python3 assets/trellium.py check <target>` (add `--format json` for stable JSON) is a fully read-only, deterministic validation of the minimal state layer — canonical `trellium-task-state` blocks in Level B/C task files, the `trellium-policy` block in `vault/index.md`, hot-file budget measurements, and TASK storage versus Git. `status` scans those state blocks directly; runtime Focus is navigation only. Exit codes: `2` on any error finding, `0` with warnings only (warnings are always shown, never an unconditional PASS), `1` for operational failures. It never auto-fixes or writes anything; legacy task files without a state block are reported as unresolved, never guessed. Create new task files from the bundled template (which carries the state block) and add a block when re-activating an old task; do not batch-migrate history. In `local` projects, task absence in a fresh clone follows the storage contract; runtime does not provide a recovery copy.
- Data protection: project data (runtime, handoff, decisions, tasks, and friends) is read-only to the script and is never replaced by templates; format migrations run semantically per `references/protocol-source/init/MIGRATIONS.md`, carrying content over without dropping facts.
- Version check: propose an upgrade when the target's `vault/.agent-init.json` `protocol_version` is older than `references/protocol-source/init/VERSION`.
- When the script cannot run (no python3, restricted sandbox), fall back to the agent-driven flow of this skill: merge templates and run migrations by hand per `references/protocol-source/`, honoring the same data-protection boundary.

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

- Agent entry file routes non-trivial tasks to `vault/index.md` and `vault/runtime.md`, with full `vault/governance.md` for Level B/C work, unclear classification, or governance-rule changes.
- Required vault files exist.
- Governance covers task levels, authority levels, task contract fields, acceptance gates, escalation, and handoff.
- `skills/agent-task/SKILL.md` exists and is focused on task execution.
- `vault/runtime.md` is short current state, not a long log.
- `vault/decisions.md` captures durable choices.
- `vault/collaboration.md` exists when collaboration preferences are useful.
- Hot-file budgets and the compact procedure are routed from vault/index.md (see references/protocol-source/init/protocol/15-vault-compaction.md).

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
