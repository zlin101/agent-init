# Parked

Cold index of items the user parked: parked but not forgotten, read only when
mentioned. Never part of the default reading path.

Entry lifecycle: record an item when the user parks a task or decision;
promote it back to `vault/tasks/<task-id>.md` (Draft)
when the user brings it up again. The Agent never deletes entries; cleanup
only produces proposals confirmed by the user.

## Entries

- P-0001 · task · short title · one-line context · resume trigger (what the
  user mentions to pick it up again) · 2026-01-01

Types: task | decision | question. Reference `TASK-xxxx` when a task file
exists; otherwise record 2-4 lines of context.

## Budget

- Trigger a cleanup proposal past 60 lines or 20 entries; with user
  confirmation, stale entries move to `vault/details/parked-archive.md`.
