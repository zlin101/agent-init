# Trellium

English | [简体中文](README.md)

Trellium is a portable Agent collaboration protocol: it installs and keeps upgrading the Agent collaboration layer of a project.

Its goal is not to generate a fixed tech-stack application template, but to give any project a stable layer of Agent collaboration capability: entry rules, project memory, task governance, acceptance gates, handoff, reusable workflows, and a collaboration profile.

## What this project solves

When developing with AI Agents over the long term, the common problems are rarely "the Agent can't write code". They are:

- A new session does not know the project's current state;
- The Agent has no clear authorization boundary;
- A task can't be handed off mid-way;
- Tests pass, but acceptance is never closed;
- Important decisions are scattered across chat logs;
- Context breaks when switching between multiple Agents or tools;
- Every project has to re-negotiate a set of collaboration rules from scratch.

Trellium converges these conventions into a single project-level collaboration protocol, so that once an Agent enters a project it knows:

- What context to read first;
- How to judge task level and authorization level;
- Which files carry runtime state, decisions, and handoff;
- When a task file must be created;
- How to verify that a task is complete;
- Which collaboration preferences can be captured, and which must not override hard rules.

## Core artifacts

The truly portable core of this repo falls into two categories:

```text
init/
skills/
```

`init/` is the protocol source directory. It maintains the complete design, initialization, and upgrade flow of Trellium.

`skills/` contains self-contained, directly installable Skill packages. Distilled from the `init/` protocol source, each package bundles the main workflow, a condensed protocol reference, the auto-synced authoritative protocol snapshot, and copy-ready templates. It does not depend on this repo's local path.

The `AGENTS.md`, `vault/`, `app/`, `tests/`, etc. in the repo root are validation artifacts that the current sandbox generates according to the protocol — they are not the migration source.

If you only want to install a self-contained Skill rather than migrate the full protocol source, use:

```text
skills/trellium/
skills/trellium-zh/
```

`trellium` is the English version, `trellium-zh` is the Chinese version.

## Directory structure

```text
init/
  INIT.md                         # initialization entry checklist
  VERSION                         # protocol version (CalVer)
  MIGRATIONS.md                   # upgrade migration playbook (data-protection entries)
  protocol/
    README.md                     # protocol module overview
    00-overview.md                # positioning and layering
    10-vault.md                   # project memory system
    15-vault-compaction.md        # memory compaction and budget lines
    20-governance.md              # task governance, authorization, acceptance
    30-agent-entry.md             # Agent entry file rules
    40-skills.md                  # reusable workflows
    50-engineering-constraints.md # engineering constraints
    60-initialization-flow.md     # new-project initialization flow
    70-adoption-flow.md           # existing-project adoption flow
    80-execution-patterns.md      # agentic execution patterns
    90-collaboration-profile.md   # evolvable collaboration profile
    profiles/
      go-backend.md               # Go backend profile
      python-backend.md           # Python backend minimal profile
skills/
  trellium/               # self-contained open-source Skill package
  trellium-zh/            # self-contained open-source Skill package (Chinese)
scripts/
  trellium.py                      # install/upgrade script (auto-distributed into the Skill packages)
  sync-skills.py                   # mirrors init/ into the Skill distribution packages
.github/workflows/
  skill-sync.yml                   # checks that the protocol source and Skill snapshots agree
```

## Usage

### New project initialization

In the target project, have the Agent read:

```text
init/INIT.md
init/protocol/README.md
init/protocol/60-initialization-flow.md
```

If the project type is already known, also read the matching profile, for example:

```text
init/protocol/profiles/python-backend.md
init/protocol/profiles/go-backend.md
```

The Agent should generate its own, according to the protocol, in the target project:

- Agent entry file, e.g. `AGENTS.md`;
- `vault/` project memory system;
- `vault/governance.md` collaboration governance rules;
- `vault/tasks/` task-contract rules;
- `skills/` reusable workflows;
- project source, tests, and dependency files as needed.

### Adopting an existing project

If the target project already exists and you only want to add the Agent collaboration layer, have the Agent read:

```text
init/INIT.md
init/protocol/README.md
init/protocol/70-adoption-flow.md
```

Adoption mode creates or updates only the Agent collaboration layer by default:

- Agent entry file;
- `vault/`;
- `skills/`;
- an optional, very short README collaboration note.

Do not modify business source, dependencies, tests, build, deployment, or CI configuration unless the user explicitly authorizes it.

### Using the open-source Skill packages

If your Agent environment supports installing Skills, you can install or copy one of these directories as a Skill package:

```text
skills/trellium/
skills/trellium-zh/
```

When the Skill is used, the Agent generates or merges the following into the target project according to the package's references and templates:

- Agent entry file;
- `vault/` project memory;
- task-contract governance;
- handoff and collaboration profile;
- `skills/agent-task/SKILL.md` starter workflow.

This Skill is suited for cross-project reuse; the full `init/protocol/` is better suited for continuing to design and maintain the protocol itself. Each Skill's `references/protocol-source/` is an authoritative snapshot generated from `init/` — do not edit it directly.

Reinstalling the Skill delivers the new templates, protocol snapshot, and bundled upgrade script. For an already-adopted project, have the Agent follow the upgrade flow in SKILL.md: `diff` (read-only report) → `upgrade --apply` (safe subset + conflict proposals) → agent semantic merge + user confirmation → `upgrade --complete`. Project data (runtime, handoff, decisions, tasks) is read-only to the script and is never replaced by templates.

### One-line install (any agent)

```bash
curl -fsSL https://raw.githubusercontent.com/zlin101/trellium/develop/scripts/install.sh | sh -s -- --version 2026.09.9
```

Installs the English Skill package into the auto-detected agent directory (`$CODEX_HOME`/`~/.codex` → Codex; `~/.claude` → Claude Code). Common options:

```bash
... | sh -s -- --lang zh              # Chinese package (default: en)
... | sh -s -- --agent all            # install for both Codex and Claude Code
                                     # when omitted: auto-detects $CODEX_HOME/~/.codex → codex, ~/.claude → claude
... | sh -s -- --project              # into ./.claude/skills/ of the current project
... | sh -s -- --version <tag>        # required for network installs (e.g. --version 2026.09.9)
... | sh -s -- --dir <path>           # any destination directory
```

Re-running the command upgrades in place (the package directory is replaced). The script requires an explicit `--version` tag for network installs and does exactly two things: download that tagged release tarball from GitHub and copy one directory — audit it first with `curl -fsSL <url> | less` if you prefer. Latest-release resolution is not supported; pick a tag from the repository's tagged releases. Use `--source <dir>` for local checkouts (no version needed).

### Installing the Skill via Codex

The recommended approach is to use Codex's built-in `skill-installer` to install this Skill directly from the GitHub repository. You do not need to clone this repo — you only need Codex installed locally and access to GitHub.

Chinese version:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo zlin101/trellium \
  --path skills/trellium-zh
```

English version:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo zlin101/trellium \
  --path skills/trellium
```

Restart Codex after installing so the new Skill takes effect.

An installed Skill does not auto-upgrade from the GitHub repository. **Protocol-template and updater changes do not require reinstalling the Skill**: add `--fetch` to the adopt/diff/upgrade commands to pull the latest tagged release and run it (cached under `~/.cache/trellium/`; downgrades are refused). Reinstalling is only needed when the Skill workflow (`SKILL.md`) or the script itself changes; the Codex installer refuses to overwrite an existing directory by default. Before reinstalling, confirm the local Skill directory has no custom modifications you want to keep.

If the repository has not been pushed to GitHub yet, first push a commit that includes `skills/trellium-zh/` or `skills/trellium/`, then let Codex install it.

### Using the script to adopt a project

`trellium.py` is the deterministic installer/upgrader and runs from two locations: `assets/trellium.py` inside a Skill package (the regular path for end users, distributed with the package), or `scripts/trellium.py` in a checkout of this repo (for protocol development and maintenance). `sync-skills.py` keeps the two identical; the commands below use the repo path.

To add the Agent collaboration layer to an existing project:

```bash
python3 scripts/trellium.py adopt /path/to/project
```

When project languages are known, declare their scopes explicitly with repeatable `--profile PROFILE[=ROOT]` arguments. A language may have multiple roots, and each selected language gets its own project document:

```bash
python3 scripts/trellium.py adopt /path/to/project \
  --profile go-backend=services/api \
  --profile python-backend=services/model
```

This creates a complete `docs/engineering/profiles/<profile>.md` for every selected profile, embeds its roots, and adds a one-hop AGENTS route scoped by current path and actual language. Unselected profiles are not generated, and later sessions do not need to rediscover the Trellium Skill. `docs/engineering/code-comments.md` remains as a compatibility carrier for the existing comment/API rules: overlapping comment/API rules follow the carrier as project customization, while the complete profile governs all other engineering concerns. Engineering policy stays outside Vault; the full rules on roots, overwrite protection, and upgrade proposals live in `init/protocol/70-adoption-flow.md` (“Profile 工程规范”).

`adopt` only adds Agent collaboration files that are missing, by default:

- `AGENTS.md`
- `vault/`
- `vault/tasks/README.md`
- `skills/agent-task/SKILL.md`

If the target project already has an `AGENTS.md`, the script appends a marked Trellium section instead of overwriting the file. Existing `vault/*` and `skills/*` files are skipped by default; pass `--force` explicitly to replace them.

Before writing anything, the script preflights every output path. If preflight finds that an output file or any parent path inside the target is a symbolic link, an output file has multiple hard links, or a resolved path escapes the target, adoption fails before any write. File content is replaced atomically through a temporary file in the same directory. On platforms with `dir_fd` and `O_NOFOLLOW`, actual writes also walk from the filesystem root through anchored directory descriptors, preventing a post-preflight link swap from redirecting output. If a filesystem race is detected or an I/O failure occurs while writing, the script stops and explicitly warns that the target may contain partial changes.

After adoption, have the Agent read the following in the target project:

```text
AGENTS.md
vault/index.md
vault/runtime.md
vault/governance.md
```

### Upgrading adopted projects

When the protocol source evolves, adopted projects can follow along safely, without disturbing their own trajectory (Skill users: replace `scripts/trellium.py` with `<skill dir>/assets/trellium.py`; the adopt/diff/upgrade commands accept `--fetch` to pull the latest tagged release without reinstalling the Skill):

```bash
python3 scripts/trellium.py diff /path/to/project              # read-only report
python3 scripts/trellium.py upgrade /path/to/project --apply   # execute the safe subset
python3 scripts/trellium.py upgrade /path/to/project --complete  # finalize resolved proposals
```

The upgrade splits collaboration files into two classes: **project data** (runtime, handoff, decisions, tasks, project, collaboration, and friends) is read-only to the upgrader and is never replaced by templates; **protocol files** (governance, index, tasks/README, skills/agent-task, the managed AGENTS.md region, and the generated engineering policy when profiles were selected) may be refreshed, but local modifications are never silently discarded — when both sides changed, a proposal is written under `vault/.upgrade/<version>/` for the Agent to merge and the user to confirm. Upgrades are per-file opt-in (`--only` / `--skip`) and produce a standalone, revertable commit.

`adopt` records a stamp at `vault/.agent-init.json` (the content hash of each file at install time). Projects adopted before the stamp existed should first run `baseline <target>`. Format migrations for data files are defined entry by entry in `init/MIGRATIONS.md`: content is carried over, never dropped.

### Checking project state (check)

```bash
python3 scripts/trellium.py check /path/to/project                # text report
python3 scripts/trellium.py check /path/to/project --format json  # stable JSON
```

`check` is a fully read-only, deterministic validation command for the minimal state layer introduced in 2026.09.2:

- `trellium-task-state` blocks: the strict JSON block at the top of Level B/C task files, the single owner of lifecycle, authority level, current slice, and gate results;
- the `trellium-policy` block: project policy in `vault/index.md`, the single source for budgets and TASK storage (`tracked | local | private`);
- `runtime.md`: project-global current state plus an optional navigation Focus; it owns no TASK lifecycle, authority, or projection, and `status` reads TASK state blocks directly. In `local` or `private` projects an absent task file in a fresh clone follows the storage contract (no recovery copy);
- budget measurements: hot-file lines, UTF-8 bytes, max line size, and entry counts are always reported; only explicitly configured policy thresholds raise `BUDGET_EXCEEDED` warnings (repository-health signals that never block acceptance);
- TASK storage: actual Git state compared against the configured strategy (tracked/local).

Exit codes: `2` when any error finding exists; `0` with warnings only, but the summary always shows them (never an unconditional PASS); `1` for operational failures such as an invalid target. `check` never auto-fixes, never writes to the target, never accesses the network, and never executes commands found in documents.

Legacy projects fail closed: historical task files without a state block produce legacy warnings and their lifecycle is never guessed; a missing policy block is never replaced with hidden defaults. State blocks never grant approvals — Allowed, Requires Approval, Forbidden, and acceptance always stay owned by the task body and user instructions.

For tasks using local lifecycle semantics (`storage_mode=local` or `private`), the Durable knowledge disposition line in Memory Updates must be completed by hand before `accepted` (`none — <reason>` or `distilled — <canonical destinations>`; unfilled counts as `pending` and blocks `accepted`). Wrong contracts go to `superseded` immediately — the gate never blocks that.

### Viewing the owner status summary (status, 2026.09.5)

```bash
python3 scripts/trellium.py status /path/to/project                # text summary
python3 scripts/trellium.py status /path/to/project --format json  # stable JSON v1
```

`status` is a fully read-only, deterministic owner status summary (introduced in 2026.09.5) that removes the repeated cost of having an agent re-read runtime and task files by hand just to report progress. It only compiles the same state layer `check` already validates and adds no new fact source:

- the Focus line marks each pointer resolved/unresolved;
- open tasks are classified as `draft / active / blocked / ready_for_review`, each with its `authority_level`, task file path, and optional `current_slice`/`gates` verbatim;
- `accepted`/`superseded` tasks appear only in the closed count, never in action lists;
- tasks whose state cannot be determined are listed explicitly under `unresolved` with the blocking finding codes (such as `TASK_STATE_INVALID` or `TASK_ID_DUPLICATE`); lifecycle and authority are never inferred;
- exit codes match `check` (`2` for errors, `0` with warnings only, `1` for operational failures).

It is a status summary, not a full owner approval inbox: blocked tasks and pending gates are shown verbatim, never translated into "the owner must approve". Text and JSON render from one result; JSON v1 always carries the `schema_version/target/focus/summary/tasks/findings` keys. `status` never writes to the target, never accesses the network, and never executes commands found in documents.

### Revising the protocol

To change Trellium itself, modify only:

```text
init/INIT.md
init/protocol/*
```

The `vault/`, `app/`, and test scaffolding in the current repo can be used to validate that the protocol is sound, but they are not the protocol source. The root `skills/` are distributable Skill packages distilled from the protocol source; after modifying the protocol you should check that they still align with `init/`.

After modifying `init/`, regenerate the authoritative protocol snapshot inside both the Chinese and English Skill packages:

```bash
python3 scripts/sync-skills.py
```

Check for drift without writing files:

```bash
python3 scripts/sync-skills.py --check
```

This script is only for this repo's release maintenance; it is not an install-time dependency for Skill users. CI runs the same check. `references/protocol-source/` is maintained entirely by the script; `SKILL.md`, the condensed `references/protocol-model.md`, and `assets/templates/` still require manual review and adjustment when protocol behavior changes. The sync script guarantees the protocol source enters the install package, but it does not pretend to automatically complete Chinese↔English semantic translation or template design.

When a change affects protocol templates shipped to adopted projects, update three things in step: `FILE_ROLES` in `scripts/trellium.py` (when files are added or removed), `init/MIGRATIONS.md` (append a migration entry), and `init/VERSION` (bump as needed). When publishing a version for `--fetch`, tag it: `git tag <version> && git push origin <version>` (matching `init/VERSION`).

## Protocol philosophy

### Task contract first

An Agent earns trust not by identity, but by task contract: it is authorized by the contract and closes the task against acceptance criteria.

A task contract includes:

- Goal and scope;
- Explicit non-goals;
- Necessary context;
- Authorization level;
- Allowed and forbidden changes;
- Acceptance criteria;
- Required verification;
- Memory-update and handoff requirements.

### Vault as project memory

The protocol generates a `vault/` in the target project to carry:

- Project positioning;
- Current runtime state;
- Governance rules;
- Long-term decisions;
- Task records;
- Handoff information;
- Collaboration preferences.

This way, when a new Agent, a different model, or a different tool enters the project, it can recover context from files instead of depending on chat history.

### Memory Compaction

The hot files (runtime, handoff, decisions) have explicit budget lines. A budget exceed appears in `trellium.py check` as a repository-health warning: tasks are accepted as usual, no compaction is triggered automatically, and no extra commit is produced. Compaction is an independent maintenance action, run only when the owner explicitly asks, an independent maintenance TASK exists, or a task contract explicitly includes it, following the five phases (measure → classify → restructure → verify → record): runtime is rewritten rather than trimmed, handoff keeps only real-interruption non-derivable transient deltas (consumed then deleted; deletion is not information loss), and decisions are indexed once past the threshold (bodies move to `vault/decisions/`, leaving a read-only-by-default index). Semantic judgments such as Superseded/Merged/Expired are only ever proposed and confirmed by the user in batch — compaction is always zero-loss restructuring, never deletion. Compaction produces a dedicated commit containing only `vault/` changes, revertible at any time.

Governance files (governance, collaboration) are activated by events: escalation events and compaction reviews produce governance-revision proposals, and collaboration preferences are captured at task close. The default reading path is leveled: `index.md` carries the built-in task-level and authority cheat sheet, and the full `governance.md` is read only for Level B/C work or when classification is unclear.

### Portable, not copying the sandbox

Do not copy the current repo's generated artifacts wholesale into a new project.

When using the full protocol source, the correct flow is:

1. Migrate or reference `init/`;
2. Have the Agent read `init/INIT.md`;
3. Generate the project's own collaboration layer according to the protocol;
4. Update the `vault/`, `skills/`, and profile artifacts based on the target project's reality.

When using a Skill package, the correct flow is:

1. Install or copy `skills/trellium-zh/` or `skills/trellium/`;
2. Invoke the Skill in the target project;
3. Let the Skill generate the target project's own `AGENTS.md`, `vault/`, and `skills/agent-task/` from its built-in templates.

## Current status

This repository is still in the protocol-design and initialization-scaffolding iteration phase.

The current focus is refining `init/` and `skills/`: the former as the protocol source, the latter as the installable Skill distribution package. Other generated artifacts in the root exist mainly to validate that the protocol is sound.

## Local verification

The current sandbox carries a minimal Python scaffold to validate the initialization flow:

```bash
uv run pytest
```

This does not mean Trellium is tied to Python. The Python and Go profiles are just examples of currently available project types.

## Commit boundary

If the goal is to release or migrate the Trellium protocol, commits should preferably be limited to:

```text
init/
skills/
README.md
scripts/
```

Unless there is an explicit need to update the current sandbox state, do not commit artifacts such as `vault/`, `app/`, `tests/`, or a target project's generated `skills/agent-task/` as protocol source. The root `skills/trellium*` packages are distribution artifacts and may be committed alongside protocol changes.
