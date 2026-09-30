# Historical Evidence Store disposable POC

## Replay

```bash
python3 -m unittest -v test_history_poc
```

Run from this directory. Observed final result: 13 tests passed, 0 failures, exit 0 (0.663 seconds).
Environment: Linux, Python 3.12.3, local filesystem reported by `stat -f` as ext2/ext3.
The tests own isolated temporary clones and stores; they never write production Trellium material.

## POC design

- Identity: explicit UUID project ID + logical artifact ID + SHA-256 content version.
- Layout: `<root>/<project>/<artifact>/<digest>/{artifact.md,metadata.json}`. One empty `.publish.lock` per logical artifact; hidden `.pending-*` directories hold uncommitted writes.
- Metadata: project_id, artifact_id, digest, archived_at, source_relative_path. No lifecycle, Authority or current-state metadata.
- put: write staging files, flush/fsync both, fsync staging directory, lock publication, atomic directory rename, fsync parent. Same version is verified and re-synced on retry. Different digests coexist.
- get: return digest-to-bytes mapping; optional digest selects an exact version. No implicit latest/effective/current selection.
- list: scan directories and verify records; no independent index or manifest. Corruption raises an error rather than silently disappearing.
- Closure adapter: source must be terminal/immutable and explicitly local by caller contract. It preserves raw bytes; put/get verification precedes optional source removal. I/O failure retains the source. Acceptance and canonical knowledge are not parsed or modified.
- Optional cleanup failure does not negate an already verified historical copy; the transient result reports retained=true, cleaned=false and the cleanup error. Source changes before cleanup are detected.

## Required failure cases

1. PASS — two identical puts yield one version and preserve its original metadata.
2. PASS — same logical ID with different content yields two immutable versions; neither overwrites the other.
3. PASS — real SIGKILL at half-written artifact, before publish while locked, and after rename; partial stages are invisible, published data stays complete, retry succeeds and dead-writer locks are released.
4. PASS — two spawn-based processes synchronize their start; identical and different contents both produce exactly the expected verified versions.
5. PASS — initialize a temporary Git clone, rename/move it and change its remote URL; retain, verify and remove the whole clone. Project ID plus artifact ID retrieves versions and verifies bytes without old path, basename or remote. Explicit re-key keeps project namespaces separate.
6. PASS — truncation, byte modification, missing metadata, malformed metadata and wrong metadata identity are detected by get/list; retry refuses corrupt existing versions rather than repairing/overwriting them.
7. PASS — real non-writable directory permissions and a root path occupied by a regular file fail retention; accepted source bytes remain unchanged even with cleanup requested.

## Supplemental checks

- Cleanup requires verified copy and unchanged terminal source; successful retention does not require deletion.
- active/none/accepted fixture transitions remain independent of store success; canonical content is unchanged.
- Injected fsync failure cannot produce retention-success acknowledgment.
- Failure after atomic publish but before directory durability acknowledgment retains the source; retry verifies and syncs the published record.
- Observed syscall ordering includes both file fsyncs and staging-directory fsync before rename, then parent-directory fsync.
- In-clone store roots and unsafe identity/origin paths are rejected.

## Complexity

- POC implementation: 144 code SLOC / 197 physical lines.
- Tests: 300 code SLOC / 340 physical lines.
- SLOC excludes blank lines, comment-only lines and docstring spans; imports and executable definitions count.
- New third-party dependencies: 0. Implementation uses Python standard library. Clone-fixture tests use the already available Git binary; retrieval itself needs no Git/DB/CLI.
- New Trellium state/schema/lifecycle: 0. The experiment has a five-field JSON metadata format, not a product schema.
- Lock: one POSIX flock at publication per logical artifact; no lock service or persisted lock ownership.
- Index/manifest/database/recovery journal: none.
- Per version: three namespace levels and two data files. Aborted staging can remain as hidden filesystem debris; normal retries need no replay journal or recovery service.

## Findings and limits

- Pairing raw Markdown and metadata needs atomic publication of the directory as a unit; independently publishing the two files would expose incomplete records.
- Directory scans suffice at this test scale; there is no evidence that an independent index is necessary.
- Actual process interruption is tested. Physical power loss, hardware failure and disk-independent survival are not tested or claimed. Observing fsync order is not a hardware durability proof.
- Only local, trusted POSIX filesystem behavior is exercised. Windows and network-filesystem lock/rename behavior are not covered.
- SHA-256 checks payload corruption and version identity; this is not cryptographic authentication against a hostile actor rewriting the whole store. Metadata shape, identity and required presence are checked; arbitrary valid edits to descriptive metadata are not authenticated.
- Cleanup assumes terminal sources are not concurrently edited by cooperating writers. A pre-unlink recheck catches changes before that point; it is not a general adversarial source-locking protocol.
- Structured bytes and their stable references are retained. Git objects, URLs, CI pages and other reference targets are neither fetched nor copied.
- This entire directory is disposable under /tmp, including experiment code and evidence. It is not the selected production retention location and makes no long-term persistence promise for /tmp itself.

## Recommendation

A — Filesystem is simple enough to proceed to formal design within the stated local POSIX scope. Stop here; no SQLite or separate history-Git prototype is justified by the experiment.

Formal design still requires owner decisions about project identity placement, supported environments and the precise durability failure domain. This POC does not authorize implementation of those product contracts.

1. Stable project identity required: yes.
2. New TASK/archive lifecycle required: no.
3. Database required: no.
4. Delete clone then retrieve/verify using project ID plus artifact ID: yes, observed.
