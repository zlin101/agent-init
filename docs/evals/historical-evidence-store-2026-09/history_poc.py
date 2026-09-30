"""Disposable POSIX historical store; opaque evidence never restores current state."""

import fcntl
import hashlib
import json
import os
import re
import shutil
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


class IntegrityError(ValueError):
    """Stored evidence is incomplete, malformed or inconsistent with its identity."""


@dataclass(frozen=True)
class Artifact:
    """One opaque structured artifact snapshot, with a logical ID and relative origin."""

    artifact_id: str
    content: bytes
    source_relative_path: str


def _sync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _mkdir(path: Path) -> None:
    if path.is_dir():
        return
    _mkdir(path.parent)
    path.mkdir(exist_ok=True)
    _sync_dir(path.parent)


def _write_file(path: Path, content: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def _relative(value: str) -> bool:
    path = PurePosixPath(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


class Store:
    """Append-only snapshots on a trusted local POSIX filesystem.

    Writers cooperate through flock. Published records are never overwritten.
    Hidden staging directories can survive process death but are never records.
    Filesystem/device failure and hostile replacement of the store are out of scope.
    """

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def _project(self, project_id: str) -> Path:
        return self.root / str(uuid.UUID(project_id))

    def _artifact(self, project_id: str, artifact_id: str) -> Path:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", artifact_id):
            raise ValueError("invalid artifact identity")
        return self._project(project_id) / artifact_id

    def _read(self, project_id: str, artifact_id: str, digest: str) -> tuple[dict, bytes]:
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("invalid content digest")
        version = self._artifact(project_id, artifact_id) / digest
        if not version.exists():
            raise FileNotFoundError(version)
        try:
            if version.is_symlink() or any(p.is_symlink() for p in version.iterdir()):
                raise IntegrityError("symlink is not an immutable artifact")
            metadata = json.loads((version / "metadata.json").read_bytes())
            content = (version / "artifact.md").read_bytes()
            if set(metadata) != {"project_id", "artifact_id", "digest", "archived_at", "source_relative_path"}:
                raise IntegrityError("metadata fields are incomplete or unexpected")
            if (metadata["project_id"], metadata["artifact_id"], metadata["digest"]) != (
                str(uuid.UUID(project_id)), artifact_id, digest
            ):
                raise IntegrityError("metadata identity mismatch")
            if not _relative(metadata["source_relative_path"]):
                raise IntegrityError("invalid relative origin")
            if datetime.fromisoformat(metadata["archived_at"]).tzinfo is None:
                raise IntegrityError("archive time must include its timezone")
            if hashlib.sha256(content).hexdigest() != digest:
                raise IntegrityError("artifact digest mismatch")
            return metadata, content
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
            raise IntegrityError(f"invalid historical record: {version.name}") from error

    def put(self, project_id: str, artifact: Artifact) -> str:
        """Publish a version and return its SHA-256; retries never replace evidence.

        Corrupt existing versions fail closed. I/O failures leave the caller's source
        untouched; a retry can verify and re-sync an already published version.
        """
        if not _relative(artifact.source_relative_path):
            raise ValueError("origin must be a relative path")
        parent = self._artifact(project_id, artifact.artifact_id)
        _mkdir(parent)
        digest = hashlib.sha256(artifact.content).hexdigest()
        version = parent / digest
        staging = Path(tempfile.mkdtemp(prefix=".pending-", dir=parent))
        metadata = dict(project_id=str(uuid.UUID(project_id)), artifact_id=artifact.artifact_id,
                        digest=digest, archived_at=datetime.now(timezone.utc).isoformat(),
                        source_relative_path=artifact.source_relative_path)
        try:
            _write_file(staging / "artifact.md", artifact.content)
            _write_file(staging / "metadata.json", json.dumps(metadata, sort_keys=True).encode())
            _sync_dir(staging)
            with (parent / ".publish.lock").open("a+b") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                if version.exists():
                    self._read(project_id, artifact.artifact_id, digest)
                    for name in ("artifact.md", "metadata.json"):
                        with (version / name).open("rb") as stream:
                            os.fsync(stream.fileno())
                    _sync_dir(version)
                else:
                    os.rename(staging, version)
                _sync_dir(parent)
            return digest
        finally:
            if staging.exists():
                shutil.rmtree(staging)

    def get(self, project_id: str, artifact_id: str, digest: str | None = None) -> dict[str, bytes]:
        """Return verified versions; without a digest return all, never an effective/latest one.

        Missing artifacts raise FileNotFoundError and invalid records raise IntegrityError.
        """
        parent = self._artifact(project_id, artifact_id)
        if digest is not None:
            return {digest: self._read(project_id, artifact_id, digest)[1]}
        versions = sorted(p.name for p in parent.iterdir() if re.fullmatch(r"[0-9a-f]{64}", p.name))
        if not versions:
            raise FileNotFoundError(artifact_id)
        return {key: self._read(project_id, artifact_id, key)[1] for key in versions}

    def list(self, project_id: str) -> list[dict]:
        """Scan verified historical records; hidden staging/lock files are not records.

        Corruption is reported rather than silently omitted. No persisted index is used.
        """
        project = self._project(project_id)
        if not project.exists():
            return []
        records = []
        for parent in sorted(project.iterdir()):
            if not parent.is_dir() or parent.name.startswith("."):
                continue
            for path in sorted(parent.iterdir()):
                if re.fullmatch(r"[0-9a-f]{64}", path.name):
                    records.append(self._read(project_id, parent.name, path.name)[0])
        return records


def retain_terminal(store: Store, project_id: str, source: Path, clone: Path,
                    artifact_id: str, cleanup: bool = False) -> dict:
    """POC closure adapter: retain opaque terminal bytes, verify, optionally unlink.

    The caller supplies a terminal immutable source and local mode. This adapter
    does not parse/change lifecycle, canonical knowledge or authority. Failure is
    a transient result, never a new persisted state; the source is retained.
    """
    try:
        if store.root.is_relative_to(clone.resolve()):
            raise ValueError("history root must be outside the working clone")
        content = source.read_bytes()
        artifact = Artifact(artifact_id, content, source.relative_to(clone).as_posix())
        digest = store.put(project_id, artifact)
        if store.get(project_id, artifact_id, digest)[digest] != content:
            raise IntegrityError("read-back differs from terminal source")
    except (OSError, ValueError) as error:
        return {"retained": False, "cleaned": False, "digest": None,
                "error": f"{type(error).__name__}: {error}"}
    if cleanup:
        try:
            if source.read_bytes() != content:
                raise IntegrityError("source changed; cleanup refused")
            source.unlink()
        except (OSError, ValueError) as error:
            return {"retained": True, "cleaned": False, "digest": digest,
                    "error": f"cleanup refused: {type(error).__name__}: {error}"}
    return {"retained": True, "cleaned": cleanup, "digest": digest, "error": None}
