"""Historical evidence store for terminal local/private Trellium artifacts.

Verified, clone-independent retention for structured evidence (terminal TASK
files, review ledgers). One immutable version per SHA-256 content digest; the
store never becomes a second current-truth owner: records restore nothing and
grant no authority.

Environment contract: a trusted local POSIX filesystem with cooperative
writers. Windows, NFS and hostile replacement of the store are out of scope.
SHA-256 proves payload integrity; it is not authentication against an actor
who rewrites the whole store.

Minimum interpreter: Python 3.9, standard library only. This module registers
no CLI; callers import it from its distributed location.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

METADATA_FIELDS = {"project_id", "artifact_id", "digest", "archived_at", "source_relative_path"}
_DIGEST_RE = re.compile(r"[0-9a-f]{64}")
_ARTIFACT_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")


class IntegrityError(ValueError):
    """Stored evidence is incomplete, malformed or inconsistent with its identity."""


class Artifact:
    """One opaque structured artifact snapshot, with a logical ID and relative origin.

    A plain frozen class instead of ``@dataclass``: dataclass field-type
    resolution looks up ``sys.modules`` for string annotations, which breaks
    importlib loads that never register the module (the distributed Skill
    invocation path) on Python 3.9.
    """

    __slots__ = ("artifact_id", "content", "source_relative_path")

    def __init__(self, artifact_id: str, content: bytes, source_relative_path: str) -> None:
        object.__setattr__(self, "artifact_id", artifact_id)
        object.__setattr__(self, "content", content)
        object.__setattr__(self, "source_relative_path", source_relative_path)

    def __repr__(self) -> str:
        return (
            f"Artifact(artifact_id={self.artifact_id!r}, "
            f"content=<bytes:{len(self.content)}>, "
            f"source_relative_path={self.source_relative_path!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Artifact):
            return NotImplemented
        return (self.artifact_id, self.content, self.source_relative_path) == (
            other.artifact_id,
            other.content,
            other.source_relative_path,
        )

    def __hash__(self) -> int:
        return hash((self.artifact_id, self.content, self.source_relative_path))

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("Artifact is immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("Artifact is immutable")


def _sync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _mkdir(path: Path) -> None:
    """Create path and persist every new parent link before returning."""
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
    Hidden staging directories can survive process death but are never records:
    list/get derive everything from the filesystem and fail closed on damage.
    """

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        # Namespace durability is promised through the bootstrap directory's
        # parent (e.g. ~/.trellium/history keeps ~/. in the acknowledged chain).
        # A root whose higher ancestors are missing would be created without a
        # boundable re-acknowledgment chain, so refuse it instead of silently
        # reporting success with unacknowledged links.
        if not self.root.parent.parent.is_dir():
            raise ValueError("store root requires an existing parent above the bootstrap directory")

    def _project(self, project_id: str) -> Path:
        return self.root / str(uuid.UUID(project_id))

    def _artifact(self, project_id: str, artifact_id: str) -> Path:
        if not _ARTIFACT_ID_RE.fullmatch(artifact_id):
            raise ValueError("invalid artifact identity")
        return self._project(project_id) / artifact_id

    def _read(self, project_id: str, artifact_id: str, digest: str) -> tuple[dict, bytes]:
        if not _DIGEST_RE.fullmatch(digest):
            raise ValueError("invalid content digest")
        version = self._artifact(project_id, artifact_id) / digest
        if not version.exists():
            raise FileNotFoundError(version)
        try:
            if version.is_symlink() or any(p.is_symlink() for p in version.iterdir()):
                raise IntegrityError("symlink is not an immutable artifact")
            metadata = json.loads((version / "metadata.json").read_bytes())
            content = (version / "artifact.md").read_bytes()
            if set(metadata) != METADATA_FIELDS:
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

    def _sync_namespace(self, parent: Path) -> None:
        """Persist every namespace link the published record depends on.

        The version entry lives in ``parent``; the artifact directory lives in
        the project directory, the project directory in the store root, the
        store root in its parent, and a newly created bootstrap directory
        (such as ``~/.trellium``) in that parent's parent. A previously failed
        attempt (or a concurrent creator) can leave any of these entries —
        including the bootstrap link above the store root — acknowledged by
        visibility alone, so the success path re-fsyncs the full chain instead
        of trusting earlier or other writers' durability.
        """
        directory = parent
        while True:
            _sync_dir(directory)
            if directory == self.root.parent.parent:
                return
            directory = directory.parent

    def put(self, project_id: str, artifact: Artifact) -> str:
        """Publish a version and return its SHA-256; retries never replace evidence.

        Staging files are written and fsynced, the staging directory is fsynced,
        then an atomic directory rename happens under a cooperative per-artifact
        lock, followed by a parent-directory fsync and a full ancestor-chain
        re-acknowledgment up through the bootstrap directory's parent. An
        existing same-digest version is verified and
        re-synced instead of trusted: "path exists" is
        never success. Corrupt existing versions fail closed. I/O failures leave
        the caller's source untouched; a retry can verify and re-sync an already
        published version.
        """
        if not _relative(artifact.source_relative_path):
            raise ValueError("origin must be a relative path")
        parent = self._artifact(project_id, artifact.artifact_id)
        _mkdir(parent)
        digest = hashlib.sha256(artifact.content).hexdigest()
        version = parent / digest
        staging = Path(tempfile.mkdtemp(prefix=".pending-", dir=parent))
        metadata = {
            "project_id": str(uuid.UUID(project_id)),
            "artifact_id": artifact.artifact_id,
            "digest": digest,
            "archived_at": datetime.now(timezone.utc).isoformat(),
            "source_relative_path": artifact.source_relative_path,
        }
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
                self._sync_namespace(parent)
            return digest
        finally:
            if staging.exists():
                shutil.rmtree(staging)

    def get(self, project_id: str, artifact_id: str, digest: str | None = None) -> dict[str, bytes]:
        """Return verified versions; without a digest return all, never an effective/latest one.

        Missing artifacts raise FileNotFoundError and invalid records raise
        IntegrityError; damage is reported, never silently skipped or repaired.
        """
        parent = self._artifact(project_id, artifact_id)
        if digest is not None:
            return {digest: self._read(project_id, artifact_id, digest)[1]}
        versions = sorted(p.name for p in parent.iterdir() if _DIGEST_RE.fullmatch(p.name))
        if not versions:
            raise FileNotFoundError(artifact_id)
        return {key: self._read(project_id, artifact_id, key)[1] for key in versions}

    def list(self, project_id: str) -> list[dict]:
        """Scan verified historical records; hidden staging/lock files are not records.

        Corruption is reported rather than silently omitted. No persisted index
        is used: the filesystem is the only derivation source.
        """
        project = self._project(project_id)
        if not project.exists():
            return []
        records = []
        for parent in sorted(project.iterdir()):
            if not parent.is_dir() or parent.name.startswith("."):
                continue
            for path in sorted(parent.iterdir()):
                if _DIGEST_RE.fullmatch(path.name):
                    records.append(self._read(project_id, parent.name, path.name)[0])
        return records


def retain_terminal(store: Store, project_id: str, source: Path, clone: Path,
                    artifact_id: str, cleanup: bool = False) -> dict:
    """Minimal closure adapter: retain opaque terminal bytes, verify, optionally unlink.

    The caller supplies a terminal immutable source in local/private mode. This adapter
    does not parse or change lifecycle, canonical knowledge or authority, and it
    never deletes a source that has not been fully retained and verified. The
    store root must live outside the working clone. Failure is a transient
    result, never a new persisted state; the source is retained.
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
