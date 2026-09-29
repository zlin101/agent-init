# Handoff

Transient delta for real interruptions that leave a recovery fact not cheaply derivable from canonical state. Create or update an entry only when BOTH hold: a real interruption occurred (session boundary before completion, agent ownership switch, owner pause, unavailable environment or external dependency, or a partially completed transient operation), and at least one recovery-relevant fact is not cheaply derivable from canonical state (TASK file, Git, working tree, rerun tests, durable knowledge). Normal completion, waiting for acceptance, a finished review, an open lifecycle alone, an ordinary next step, or a fully recoverable clean session boundary creates no entry.

Each entry is named after its task id, or SESSION when there is none, and contains exactly three sections:

- Why interrupted: why the previous context stopped.
- Transient context not captured elsewhere: the non-reproducible scene.
- Exact resume point: the exact continuation action, only when it adds recovery value beyond the task slice.

Recovery order: read the TASK file, live Git/working tree, and rerun tests first; use a handoff entry only to apply its transient delta, then delete the entry once consumed. Durable conclusions must already live in canonical files.

Branch, HEAD, and dirty files are read live from Git at resume time and are never stored here as authoritative state.

After a local task (`task_storage=local`) closes, delete its related transient deltas here; durable conclusions land in canonical files first.
