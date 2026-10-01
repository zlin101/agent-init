"""Real-process failure tests for the formal historical evidence store."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import multiprocessing as mp
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

STORE_PATH = Path(__file__).with_name("history_store.py")
_SPEC = importlib.util.spec_from_file_location("history_store", STORE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"cannot load {STORE_PATH}")
history = importlib.util.module_from_spec(_SPEC)
sys.modules["history_store"] = history
_SPEC.loader.exec_module(history)

Artifact = history.Artifact
IntegrityError = history.IntegrityError
Store = history.Store
retain_terminal = history.retain_terminal


CONTENT = b'''# TASK-0023
<!-- trellium-task-state
{"schema_version":1,"task_id":"TASK-0023","level":"B","authority_level":1,"lifecycle":"accepted"}
-->
## Execution Record
Test command: python3 -m unittest
Git SHA: 0123456789abcdef0123456789abcdef01234567
Reference: https://example.org/issues/1
## Memory Updates
Durable knowledge disposition: none -- no canonical change needed.
'''


def _put_worker(root: str, project: str, content: bytes, barrier, results) -> None:
    try:
        if barrier is not None:
            barrier.wait(timeout=8)
        digest = Store(Path(root)).put(project, Artifact("TASK-0023", content, "vault/tasks/TASK-0023.md"))
        results.put(("ok", digest))
    except Exception as error:
        results.put(("error", repr(error)))


def _crash_worker(root: str, project: str, phase: str, pipe) -> None:
    write_file, rename = history._write_file, history.os.rename

    def stop() -> None:
        pipe.send("ready")
        pipe.recv()

    def partial(path: Path, content: bytes) -> None:
        if path.name == "artifact.md":
            with path.open("xb") as stream:
                stream.write(content[:len(content) // 2])
                stream.flush()
                os.fsync(stream.fileno())
                stop()
        else:
            write_file(path, content)

    def interrupted_rename(source, destination) -> None:
        if phase == "before_publish":
            stop()
        rename(source, destination)
        if phase == "after_publish":
            stop()

    patches = [
        patch.object(history, "_write_file", partial if phase == "partial" else write_file),
        patch.object(history.os, "rename", interrupted_rename),
    ]
    for item in patches:
        item.start()
    try:
        Store(Path(root)).put(project, Artifact("TASK-0023", CONTENT, "vault/tasks/TASK-0023.md"))
    finally:
        for item in reversed(patches):
            item.stop()


class HistoryStoreTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="history-case-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.project = str(uuid.uuid4())
        self.store = Store(self.base / "external-history")
        self.clone = self.base / "clone"
        self.source = self.clone / "vault/tasks/TASK-0023.md"
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(CONTENT)
        self.artifact = Artifact("TASK-0023", CONTENT, "vault/tasks/TASK-0023.md")
        self.context = mp.get_context("spawn")

    def _workers(self, contents: list[bytes], root: Path | None = None) -> list[tuple]:
        results = self.context.Queue()
        barrier = self.context.Barrier(len(contents))
        processes = [self.context.Process(target=_put_worker, args=(
            str(root or self.store.root), self.project, content, barrier, results
        )) for content in contents]
        try:
            for process in processes:
                process.start()
            answers = [results.get(timeout=10) for _ in processes]
            for process in processes:
                process.join(timeout=10)
                self.assertEqual(process.exitcode, 0)
            self.assertTrue(all(answer[0] == "ok" for answer in answers), answers)
            return answers
        finally:
            for process in processes:
                if process.is_alive():
                    process.kill()
                    process.join(timeout=5)
            results.close()
            results.join_thread()

    def test_case_1_idempotent_retry(self) -> None:
        digest = self.store.put(self.project, self.artifact)
        original_metadata = self.store.list(self.project)
        self.assertEqual(self.store.put(self.project, self.artifact), digest)
        self.assertEqual(self.store.list(self.project), original_metadata)
        self.assertEqual(self.store.get(self.project, "TASK-0023"), {digest: CONTENT})
        self.assertEqual(len(list(self.store.root.rglob("artifact.md"))), 1)
        self.assertFalse(list(self.store.root.rglob(".pending-*")))

    def test_case_2_different_terminal_content(self) -> None:
        digest_a = self.store.put(self.project, self.artifact)
        modified = CONTENT + b"\nReview: R1 fixed; R2 wont-fix with owner rationale.\n"
        digest_b = self.store.put(self.project, Artifact("TASK-0023", modified, self.artifact.source_relative_path))
        self.assertNotEqual(digest_a, digest_b)
        self.assertEqual(self.store.get(self.project, "TASK-0023"), {digest_a: CONTENT, digest_b: modified})
        self.assertEqual(len(self.store.list(self.project)), 2)

    def test_case_3_process_death_and_partial_write(self) -> None:
        for phase in ("partial", "before_publish", "after_publish"):
            with self.subTest(phase=phase):
                root = self.base / phase
                receiver, sender = self.context.Pipe()
                process = self.context.Process(target=_crash_worker, args=(str(root), self.project, phase, sender))
                try:
                    process.start()
                    self.assertTrue(receiver.poll(10), "worker did not reach interruption point")
                    self.assertEqual(receiver.recv(), "ready")
                    process.kill()
                    process.join(timeout=5)
                    self.assertEqual(process.exitcode, -signal.SIGKILL)
                finally:
                    if process.is_alive():
                        process.kill()
                        process.join(timeout=5)
                    receiver.close()
                    sender.close()
                store = Store(root)
                if phase == "after_publish":
                    self.assertEqual(len(store.list(self.project)), 1)
                else:
                    self.assertEqual(store.list(self.project), [])
                    with self.assertRaises(FileNotFoundError):
                        store.get(self.project, "TASK-0023")
                    self.assertEqual(len(list(root.rglob(".pending-*"))), 1)
                    if phase == "partial":
                        partial = next(root.rglob(".pending-*/artifact.md"))
                        self.assertEqual(partial.read_bytes(), CONTENT[:len(CONTENT) // 2])
                self._workers([CONTENT], root)
                self.assertEqual(store.get(self.project, "TASK-0023"), {hashlib.sha256(CONTENT).hexdigest(): CONTENT})

    def test_case_4_concurrent_put(self) -> None:
        for contents in ([CONTENT, CONTENT], [CONTENT, CONTENT + b"\nA distinct terminal version.\n"]):
            with self.subTest(different=contents[0] != contents[1]):
                root = self.base / str(uuid.uuid4())
                self._workers(contents, root)
                store = Store(root)
                expected = {hashlib.sha256(content).hexdigest(): content for content in contents}
                self.assertEqual(store.get(self.project, "TASK-0023"), expected)
                self.assertEqual(len(store.list(self.project)), len(expected))
                self.assertFalse(list(root.rglob(".pending-*")))

    def test_case_5_clone_deletion_recovery(self) -> None:
        subprocess.run(["git", "init", "-q", str(self.clone)], check=True)
        subprocess.run(["git", "-C", str(self.clone), "remote", "add", "origin", "https://example.org/old.git"], check=True)
        renamed = self.base / "new-workspace/renamed-repo"
        renamed.parent.mkdir()
        self.clone.rename(renamed)
        subprocess.run(["git", "-C", str(renamed), "remote", "set-url", "origin", "https://example.org/new.git"], check=True)
        source = renamed / self.artifact.source_relative_path
        canonical = renamed / "vault/project.md"
        canonical.write_bytes(b"Current truth stays here.\n")
        result = retain_terminal(self.store, self.project, source, renamed, "TASK-0023")
        self.assertTrue(result["retained"], result)
        self.assertTrue(source.exists())
        self.assertEqual(source.read_bytes(), CONTENT)
        self.assertEqual(canonical.read_bytes(), b"Current truth stays here.\n")
        shutil.rmtree(renamed)
        self.assertFalse(renamed.exists())
        records = self.store.list(self.project)
        self.assertEqual(len(records), 1)
        recovered = self.store.get(self.project, "TASK-0023")
        self.assertEqual(recovered, {result["digest"]: CONTENT})
        self.assertEqual(hashlib.sha256(next(iter(recovered.values()))).hexdigest(), records[0]["digest"])
        self.assertEqual(set(records[0]), {"project_id", "artifact_id", "digest", "archived_at", "source_relative_path"})
        new_project = str(uuid.uuid4())
        self.assertEqual(self.store.list(new_project), [])
        self.store.put(new_project, self.artifact)
        self.assertEqual(len(self.store.list(self.project)), 1)
        self.assertEqual(len(self.store.list(new_project)), 1)

    def test_case_6_tampering_and_truncation(self) -> None:
        for alteration in ("truncate", "modify", "remove_metadata", "bad_metadata", "wrong_identity"):
            with self.subTest(alteration=alteration):
                store = Store(self.base / alteration)
                digest = store.put(self.project, self.artifact)
                version = store.root / self.project / "TASK-0023" / digest
                if alteration == "truncate":
                    (version / "artifact.md").write_bytes(CONTENT[:10])
                elif alteration == "modify":
                    (version / "artifact.md").write_bytes(CONTENT.replace(b"accepted", b"rejected"))
                elif alteration == "remove_metadata":
                    (version / "metadata.json").unlink()
                elif alteration == "bad_metadata":
                    (version / "metadata.json").write_text("{")
                else:
                    metadata = json.loads((version / "metadata.json").read_text())
                    metadata["project_id"] = str(uuid.uuid4())
                    (version / "metadata.json").write_text(json.dumps(metadata))
                with self.assertRaises(IntegrityError):
                    store.get(self.project, "TASK-0023", digest)
                with self.assertRaises(IntegrityError):
                    store.list(self.project)
                with self.assertRaises(IntegrityError):
                    store.put(self.project, self.artifact)

    def test_case_7_store_unavailable(self) -> None:
        blocked = self.base / "not-a-directory"
        blocked.write_text("blocked")
        readonly = self.base / "readonly"
        readonly.mkdir()
        readonly.chmod(0o500)
        try:
            for root in (blocked, readonly):
                with self.subTest(root=root.name):
                    result = retain_terminal(Store(root), self.project, self.source, self.clone, "TASK-0023", cleanup=True)
                    self.assertFalse(result["retained"], result)
                    self.assertTrue(result["error"])
                    self.assertTrue(self.source.exists())
                    self.assertEqual(self.source.read_bytes(), CONTENT)
                    self.assertIn(b'"lifecycle":"accepted"', self.source.read_bytes())
        finally:
            readonly.chmod(0o700)

    def test_cleanup_requires_verified_unchanged_source(self) -> None:
        original_get = self.store.get

        def change_source(*args: object, **kwargs: object):
            result = original_get(*args, **kwargs)  # type: ignore[misc]
            self.source.write_bytes(CONTENT + b"\nUnexpected change.\n")
            return result

        with patch.object(self.store, "get", side_effect=change_source):
            result = retain_terminal(self.store, self.project, self.source, self.clone, "TASK-0023", cleanup=True)
        self.assertTrue(result["retained"])
        self.assertFalse(result["cleaned"])
        self.assertIn("cleanup refused", result["error"])
        self.assertTrue(self.source.exists())
        self.source.write_bytes(CONTENT)
        result = retain_terminal(self.store, self.project, self.source, self.clone, "TASK-0023", cleanup=True)
        self.assertTrue(result["retained"], result)
        self.assertFalse(self.source.exists())
        self.assertEqual(self.store.get(self.project, "TASK-0023"), {result["digest"]: CONTENT})

    def test_fsync_failure_is_not_retention_success(self) -> None:
        with patch("history_store.os.fsync", side_effect=OSError("injected fsync failure")):
            result = retain_terminal(self.store, self.project, self.source, self.clone, "TASK-0023", cleanup=True)
        self.assertFalse(result["retained"])
        self.assertEqual(self.source.read_bytes(), CONTENT)

    def test_post_publish_sync_failure_keeps_source_and_retry_recovers(self) -> None:
        sync_dir = history._sync_dir
        parent = self.store.root / self.project / "TASK-0023"
        version = parent / hashlib.sha256(CONTENT).hexdigest()

        def fail_after_publish(path: Path) -> None:
            if path == parent and version.exists():
                raise OSError("injected directory durability failure")
            sync_dir(path)

        with patch("history_store._sync_dir", side_effect=fail_after_publish):
            result = retain_terminal(self.store, self.project, self.source, self.clone, "TASK-0023", cleanup=True)
        self.assertFalse(result["retained"])
        self.assertEqual(self.source.read_bytes(), CONTENT)
        self.assertEqual(self.store.get(self.project, "TASK-0023"), {version.name: CONTENT})
        retried = retain_terminal(self.store, self.project, self.source, self.clone, "TASK-0023", cleanup=True)
        self.assertTrue(retried["retained"], retried)
        self.assertFalse(self.source.exists())

    def test_sync_order_surrounds_atomic_publish(self) -> None:
        """Portable ordering observation: file/staging syncs precede the rename,
        the publication ancestor is synced after it. Patches the module's own
        durability hooks instead of resolving fds through /proc, so the same
        observation runs on every supported interpreter and OS."""
        events: list[tuple] = []
        real_write, real_sync, real_rename = history._write_file, history._sync_dir, history.os.rename

        def recorded_write(path: Path, content: bytes) -> None:
            real_write(path, content)
            events.append(("fsync_file", str(path)))

        def recorded_sync(path: Path) -> None:
            real_sync(path)
            events.append(("fsync_dir", str(path)))

        def recorded_rename(source, destination) -> None:
            real_rename(source, destination)
            events.append(("rename", str(source), str(destination)))

        with patch.object(history, "_write_file", recorded_write), \
                patch.object(history, "_sync_dir", recorded_sync), \
                patch.object(history.os, "rename", recorded_rename):
            self.store.put(self.project, self.artifact)
        publish_index = next(i for i, event in enumerate(events) if event[0] == "rename")
        staging = events[publish_index][1]
        before, after = events[:publish_index], events[publish_index + 1:]
        self.assertIn(("fsync_file", f"{staging}/artifact.md"), before)
        self.assertIn(("fsync_file", f"{staging}/metadata.json"), before)
        self.assertIn(("fsync_dir", staging), before)
        self.assertIn(("fsync_dir", str(Path(staging).parent)), after)

    def test_closure_acceptance_and_disposition_are_separate(self) -> None:
        canonical = self.clone / "vault/project.md"
        canonical.write_bytes(b"Already sufficient canonical knowledge.\n")
        active = CONTENT.replace(b'"lifecycle":"accepted"', b'"lifecycle":"active"')
        self.source.write_bytes(active)
        self.assertIn(b"disposition: none", active)
        completed = active.replace(b'"lifecycle":"active"', b'"lifecycle":"accepted"')
        self.source.write_bytes(completed)
        blocked = self.base / "unavailable"
        blocked.write_text("not a directory")
        failed = retain_terminal(Store(blocked), self.project, self.source, self.clone, "TASK-0023", cleanup=True)
        self.assertFalse(failed["retained"])
        self.assertEqual(self.source.read_bytes(), completed)
        succeeded = retain_terminal(self.store, self.project, self.source, self.clone, "TASK-0023")
        self.assertTrue(succeeded["retained"], succeeded)
        self.assertTrue(self.source.exists())
        self.assertEqual(canonical.read_bytes(), b"Already sufficient canonical knowledge.\n")
        self.assertEqual(self.store.get(self.project, "TASK-0023"), {succeeded["digest"]: completed})

    def test_store_inside_clone_rejected_and_identity_paths_safe(self) -> None:
        result = retain_terminal(Store(self.clone / "history"), self.project, self.source, self.clone, "TASK-0023", True)
        self.assertFalse(result["retained"])
        self.assertTrue(self.source.exists())
        for identity in ("../escape", "/absolute", ".", ""):
            with self.subTest(identity=identity), self.assertRaises(ValueError):
                self.store.put(self.project, Artifact(identity, CONTENT, "vault/tasks/TASK-0023.md"))
        with self.assertRaises(ValueError):
            self.store.put(self.project, Artifact("TASK-0023", CONTENT, "../escape"))

    def test_distributed_importlib_load_without_sys_modules(self) -> None:
        """The distributed invocation path loads via importlib and never
        registers the module in sys.modules (the SKILL call pattern). The
        module must import and serve put/get on Python 3.9 without the
        dataclass field-type lookup crash observed there."""
        spec = importlib.util.spec_from_file_location("t29-unregistered", STORE_PATH)
        assert spec is not None and spec.loader is not None
        unregistered = importlib.util.module_from_spec(spec)
        assert "t29-unregistered" not in sys.modules
        spec.loader.exec_module(unregistered)
        store = unregistered.Store(self.base / "importlib-root")
        project = str(uuid.uuid4())
        digest = store.put(project, unregistered.Artifact("TASK-0023", CONTENT, "vault/tasks/TASK-0023.md"))
        self.assertEqual(store.get(project, "TASK-0023", digest), {digest: CONTENT})

    def test_retry_reacknowledges_ancestor_links_after_failed_sync(self) -> None:
        """A failed attempt leaves namespace entries visible but unacknowledged;
        the retry must re-fsync the full chain instead of trusting visibility."""
        for level in ("root-parent", "root", "project"):
            with self.subTest(level=level):
                root = self.base / f"flaky-{level}"
                store = Store(root)
                ancestor = {
                    "root-parent": store.root.parent,
                    "root": store.root,
                    "project": store.root / self.project,
                }[level]
                real_sync = history._sync_dir
                state = {"failed": False}

                with patch("history_store._sync_dir", side_effect=self._flaky_sync(ancestor, real_sync, state)):
                    result = retain_terminal(store, self.project, self.source, self.clone, "TASK-0023")
                self.assertFalse(result["retained"], result)
                self.assertTrue(self.source.exists())
                self.assertTrue(ancestor.is_dir())  # visible, but never trusted as durable

                events: list[Path] = []

                with patch("history_store._sync_dir", side_effect=self._recording_sync(events, real_sync)):
                    retried = retain_terminal(store, self.project, self.source, self.clone, "TASK-0023")
                self.assertTrue(retried["retained"], retried)
                self.assertIn(ancestor, events)  # the previously unacknowledged link is re-synced
                self.assertEqual(
                    store.get(self.project, "TASK-0023"), {retried["digest"]: CONTENT}
                )

    def test_existing_namespace_is_reacknowledged_on_success(self) -> None:
        """Namespace links created by an earlier or concurrent writer are still
        re-synced on the success path: visibility never bypasses durability."""
        first = self.store.put(self.project, self.artifact)
        events: list[Path] = []
        real_sync = history._sync_dir

        with patch("history_store._sync_dir", side_effect=self._recording_sync(events, real_sync)):
            digest = self.store.put(
                self.project,
                Artifact("TASK-0023", CONTENT + b"\nsecond terminal version\n", self.artifact.source_relative_path),
            )
        self.assertNotEqual(digest, first)
        for ancestor in (self.store.root.parent.parent, self.store.root.parent, self.store.root, self.store.root / self.project):
            self.assertIn(ancestor, events)

    def test_retry_reacknowledges_bootstrap_parent_after_failed_sync(self) -> None:
        """When the store's bootstrap directory (such as ~/.trellium) is newly
        created, the link above it is also a necessary namespace entry: a
        failed first attempt must not let the retry treat the visible
        bootstrap directory as already durable."""
        bootstrap = self.base / "bootstrap-trellium"
        store = Store(bootstrap / "history")
        ancestor = store.root.parent.parent  # holds the bootstrap directory entry
        real_sync = history._sync_dir
        state = {"failed": False}

        with patch("history_store._sync_dir", side_effect=self._flaky_sync(ancestor, real_sync, state)):
            result = retain_terminal(store, self.project, self.source, self.clone, "TASK-0023")
        self.assertFalse(result["retained"], result)
        self.assertTrue(self.source.exists())
        self.assertTrue(bootstrap.is_dir())  # visible, but never trusted as durable

        events: list[Path] = []
        with patch("history_store._sync_dir", side_effect=self._recording_sync(events, real_sync)):
            retried = retain_terminal(store, self.project, self.source, self.clone, "TASK-0023")
        self.assertTrue(retried["retained"], retried)
        self.assertIn(ancestor, events)  # the previously unacknowledged link is re-synced
        self.assertEqual(store.get(self.project, "TASK-0023"), {retried["digest"]: CONTENT})

    def test_bootstrap_parent_link_is_reacknowledged_on_existing_store(self) -> None:
        """A store whose bootstrap directory already exists still re-syncs the
        link above it on every success: an earlier writer's failed attempt can
        leave that entry unacknowledged, and visibility must not bypass it."""
        bootstrap = self.base / "shared-trellium"
        bootstrap.mkdir()
        store = Store(bootstrap / "history")
        events: list[Path] = []
        real_sync = history._sync_dir

        with patch("history_store._sync_dir", side_effect=self._recording_sync(events, real_sync)):
            digest = store.put(self.project, self.artifact)
        self.assertIn(store.root.parent.parent, events)
        self.assertEqual(store.get(self.project, "TASK-0023"), {digest: CONTENT})

    def test_store_rejects_missing_parent_chain_above_bootstrap(self) -> None:
        """Namespace durability is promised through the bootstrap directory's
        parent only; a root whose higher ancestors are missing is refused
        instead of reporting success with unacknowledgeable links."""
        with self.assertRaises(ValueError):
            Store(self.base / "missing" / "deep" / "root")
        self.assertFalse((self.base / "missing").exists())

    @staticmethod
    def _flaky_sync(ancestor: Path, real_sync, state: dict):
        def flaky(path: Path) -> None:
            if not state["failed"] and path == ancestor:
                state["failed"] = True
                raise OSError("injected ancestor sync failure")
            real_sync(path)

        return flaky

    @staticmethod
    def _recording_sync(events: list, real_sync):
        def recording(path: Path) -> None:
            events.append(path)
            real_sync(path)

        return recording

    def test_artifacts_and_projects_are_isolated_namespaces(self) -> None:
        """Product-boundary check beyond the POC set: distinct logical artifacts
        and project namespaces coexist; no implicit selection spans them."""
        ledger = Artifact("TASK-0023-review", CONTENT + b"\nReview ledger round 1: fixed.\n",
                          "vault/tasks/TASK-0023-review.md")
        task_digest = self.store.put(self.project, self.artifact)
        ledger_digest = self.store.put(self.project, ledger)
        self.assertNotEqual(task_digest, ledger_digest)
        other = str(uuid.uuid4())
        self.store.put(other, self.artifact)
        self.assertEqual(self.store.get(self.project, "TASK-0023"), {task_digest: CONTENT})
        self.assertEqual(self.store.get(self.project, "TASK-0023-review"), {ledger_digest: ledger.content})
        self.assertEqual(
            {(record["artifact_id"], record["digest"]) for record in self.store.list(self.project)},
            {("TASK-0023", task_digest), ("TASK-0023-review", ledger_digest)},
        )
        self.assertEqual({record["project_id"] for record in self.store.list(other)}, {other})
        with self.assertRaises(FileNotFoundError):
            self.store.get(self.project, "TASK-0023", "0" * 64)
        with self.assertRaises(FileNotFoundError):
            self.store.get(self.project, "TASK-4040")
        with self.assertRaises(ValueError):
            self.store.get(self.project, "TASK-0023", "not-a-digest")


if __name__ == "__main__":
    unittest.main(verbosity=2)
