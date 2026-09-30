"""Real-process failure experiments for the disposable historical store."""

import hashlib
import json
import multiprocessing as mp
import os
import shutil
import signal
import subprocess
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import history_poc as history
from history_poc import Artifact, IntegrityError, Store, retain_terminal


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

    history._write_file = partial if phase == "partial" else write_file
    history.os.rename = interrupted_rename
    Store(Path(root)).put(project, Artifact("TASK-0023", CONTENT, "vault/tasks/TASK-0023.md"))


class HistoryPOCTest(unittest.TestCase):
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

        def change_source(*args, **kwargs):
            result = original_get(*args, **kwargs)
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
        with patch("history_poc.os.fsync", side_effect=OSError("injected fsync failure")):
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

        with patch("history_poc._sync_dir", side_effect=fail_after_publish):
            result = retain_terminal(self.store, self.project, self.source, self.clone, "TASK-0023", cleanup=True)
        self.assertFalse(result["retained"])
        self.assertEqual(self.source.read_bytes(), CONTENT)
        self.assertEqual(self.store.get(self.project, "TASK-0023"), {version.name: CONTENT})
        retried = retain_terminal(self.store, self.project, self.source, self.clone, "TASK-0023", cleanup=True)
        self.assertTrue(retried["retained"], retried)
        self.assertFalse(self.source.exists())

    def test_sync_order_surrounds_atomic_publish(self) -> None:
        events = []
        fsync, rename = history.os.fsync, history.os.rename

        def synced(fd: int) -> None:
            events.append(("fsync", os.readlink(f"/proc/self/fd/{fd}")))
            fsync(fd)

        def published(source, destination) -> None:
            events.append(("rename", str(source), str(destination)))
            rename(source, destination)

        with patch("history_poc.os.fsync", side_effect=synced), patch("history_poc.os.rename", side_effect=published):
            self.store.put(self.project, self.artifact)
        publish_index = next(i for i, event in enumerate(events) if event[0] == "rename")
        staging = events[publish_index][1]
        before, after = events[:publish_index], events[publish_index + 1:]
        self.assertIn(("fsync", f"{staging}/artifact.md"), before)
        self.assertIn(("fsync", f"{staging}/metadata.json"), before)
        self.assertIn(("fsync", staging), before)
        self.assertIn(("fsync", str(Path(staging).parent)), after)

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
