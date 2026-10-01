#!/usr/bin/env python3
"""Adopt Trellium assets into a target project and upgrade them in place."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import secrets
import shutil
import stat
import subprocess
import sys
import tarfile
import urllib.error
import urllib.request
import uuid
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from datetime import date
from pathlib import Path, PurePosixPath

# The script runs from two layouts:
# - repository checkout: scripts/trellium.py, templates under
#   skills/trellium-zh/assets/templates, protocol under init/
# - installed Skill package: assets/trellium.py, templates under
#   assets/templates, protocol under references/protocol-source/init
# Each Skill package uses its own locale templates.
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
SKILL_LAYOUT = (SCRIPT_DIRECTORY / "templates" / "vault" / "index.md").is_file()
if SKILL_LAYOUT:
    TEMPLATES_ROOT = SCRIPT_DIRECTORY / "templates"
    PROTOCOL_INIT_DIRECTORY = SCRIPT_DIRECTORY.parent / "references" / "protocol-source" / "init"
else:
    REPO_ROOT = SCRIPT_DIRECTORY.parent
    TEMPLATES_ROOT = REPO_ROOT / "skills" / "trellium-zh" / "assets" / "templates"
    PROTOCOL_INIT_DIRECTORY = REPO_ROOT / "init"

TEMPLATE_FILES = (
    "vault/index.md",
    "vault/governance.md",
    "vault/decisions.md",
    "vault/handoff.md",
    "vault/parked.md",
    "vault/collaboration.md",
    "vault/tasks/README.md",
    "skills/agent-task/SKILL.md",
)
RENDERED_FILES = ("vault/project.md", "vault/runtime.md")

# TASK-0011 (No-Go stop-condition fix): the agent-task template source must
# not be named SKILL.md anywhere in the distributed packages — Codex globally
# discovered the nested template (reproduced 2026-09-15). The packaged file
# uses a non-discoverable name; adopt/upgrade still render the target
# project's skills/agent-task/SKILL.md unchanged.
TEMPLATE_SOURCE_OVERRIDE = {
    "skills/agent-task/SKILL.md": "skills/agent-task/AGENT_TASK_SKILL.template",
}

PROFILE_RULES_RELATIVE = "docs/engineering/code-comments.md"
PROFILE_RULES_TEMPLATE = "docs/engineering/CODE_COMMENTS.template"
PROFILE_DOCUMENT_DIRECTORY = "docs/engineering/profiles"
PROFILE_DOCUMENT_TEMPLATE_DIRECTORY = "docs/engineering/profiles"
PROFILE_LOCALE_FILE = "PROFILE_LOCALE"
PROFILE_IDS = ("go-backend", "python-backend")
PROFILE_MARKER_PREFIX = "trellium-comment-policy"
PROFILE_SCOPE_PLACEHOLDER = "{{PROFILE_SCOPE}}"


def template_source(relative: str) -> Path:
    """Resolve the packaged template source for a target-relative path."""
    return TEMPLATES_ROOT / TEMPLATE_SOURCE_OVERRIDE.get(relative, relative)


def profile_template_source() -> Path:
    """Return the localized source used to render the project comment policy."""
    return TEMPLATES_ROOT / PROFILE_RULES_TEMPLATE


def profile_document_relative(profile_id: str) -> str:
    """Return the project-relative durable document for one selected profile."""
    if profile_id not in PROFILE_IDS:
        raise AdoptionError(f"unknown profile: {profile_id!r}")
    return f"{PROFILE_DOCUMENT_DIRECTORY}/{profile_id}.md"


def is_profile_document_relative(relative: str) -> bool:
    """Return whether a path is one of the finite supported profile outputs."""
    return relative in {
        profile_document_relative(profile_id) for profile_id in PROFILE_IDS
    }


def profile_document_template_source(profile_id: str) -> Path:
    """Return the localized complete-profile source distributed by this package."""
    return TEMPLATES_ROOT / PROFILE_DOCUMENT_TEMPLATE_DIRECTORY / f"{profile_id}.md"


def profile_for_relative(relative: str, profiles: list[dict]) -> dict | None:
    """Resolve a durable project profile path to its selected profile metadata."""
    for item in profiles:
        if relative == profile_document_relative(item["id"]):
            return item
    return None


def render_durable_profile(profile: dict) -> str:
    """Render one complete localized profile with its project root contract."""
    source = profile_document_template_source(profile["id"])
    try:
        body = source.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise AdoptionError(f"complete profile template does not exist: {source}") from exc
    if not body:
        raise AdoptionError(f"complete profile template is empty: {source}")
    scope = ", ".join(f"`{root}`" for root in profile["roots"])
    try:
        locale = (TEMPLATES_ROOT / PROFILE_LOCALE_FILE).read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise AdoptionError(
            f"profile template locale metadata does not exist: {TEMPLATES_ROOT / PROFILE_LOCALE_FILE}"
        ) from exc
    if locale not in {"en", "zh"}:
        raise AdoptionError(f"unsupported profile template locale: {locale!r}")
    heading = "## 项目适用范围\n\n" if locale == "zh" else "## Project Scope\n\n"
    instruction = (
        "仅当当前文件位于上述任一 root 下时应用本 profile；roots 重叠时按文件实际语言选择规则。"
        if locale == "zh"
        else "Only apply this profile when the current file is under one of these roots. "
        "When roots overlap, select rules by the file's actual language."
    )
    title, separator, remainder = body.partition("\n")
    if not separator:
        raise AdoptionError(f"complete profile template lacks a title/body boundary: {source}")
    return (
        f"<!-- trellium-durable-profile: {profile['id']} -->\n\n"
        f"{title}\n\n{heading}- Profile: `{profile['id']}`\n- Roots: {scope}\n\n"
        f"{instruction}\n{remainder.rstrip()}\n"
    )


def extract_profile_section(text: str, section: str) -> str:
    """Extract one named section from the localized profile-policy template."""
    start_marker = f"<!-- {PROFILE_MARKER_PREFIX}:{section}:start -->"
    end_marker = f"<!-- {PROFILE_MARKER_PREFIX}:{section}:end -->"
    start = text.find(start_marker)
    end = text.find(end_marker, start + len(start_marker))
    if start < 0 or end < 0:
        raise AdoptionError(f"profile template is missing section markers for {section}")
    body = text[start + len(start_marker) : end].strip()
    if not body:
        raise AdoptionError(f"profile template section is empty: {section}")
    return body


def normalize_profile_root(value: str) -> str:
    """Normalize one target-relative profile root without resolving symlinks."""
    if (
        not value
        or value != value.strip()
        or "\\" in value
        or "`" in value
        or not value.isprintable()
    ):
        raise AdoptionError(f"profile root must be a non-empty POSIX relative path: {value!r}")
    root = PurePosixPath(value)
    if root.is_absolute() or ".." in root.parts:
        raise AdoptionError(f"profile root must stay within the project: {value!r}")
    normalized = root.as_posix()
    if normalized in ("", "."):
        return "."
    return normalized.removeprefix("./")


def parse_profile_selections(values: list[str]) -> list[dict]:
    """Parse repeatable `PROFILE[=ROOT]` values into deterministic selections."""
    roots_by_profile: dict[str, list[str]] = {}
    for value in values:
        profile_id, separator, raw_root = value.partition("=")
        if profile_id not in PROFILE_IDS:
            raise AdoptionError(
                f"unknown profile {profile_id!r}; expected one of: {', '.join(PROFILE_IDS)}"
            )
        if separator and not raw_root:
            raise AdoptionError(f"profile root is empty for {profile_id}")
        root = normalize_profile_root(raw_root if separator else ".")
        roots = roots_by_profile.setdefault(profile_id, [])
        if root in roots:
            raise AdoptionError(f"duplicate profile selection: {profile_id}={root}")
        roots.append(root)
    return [
        {"id": profile_id, "roots": sorted(roots_by_profile[profile_id])}
        for profile_id in PROFILE_IDS
        if profile_id in roots_by_profile
    ]


def selections_from_stamp(stamp: dict | None) -> list[dict]:
    """Read known profile selections from a v2 stamp; v1 stamps have none."""
    if not isinstance(stamp, dict):
        return []
    if "profiles" not in stamp:
        return []
    raw_profiles = stamp.get("profiles")
    if not isinstance(raw_profiles, list):
        raise AdoptionError("adoption stamp profiles must be a list")
    values: list[str] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(raw_profiles):
        if not isinstance(item, dict):
            raise AdoptionError(f"adoption stamp profile #{index + 1} must be an object")
        profile_id = item.get("id")
        if profile_id not in PROFILE_IDS:
            raise AdoptionError(f"adoption stamp contains unknown profile: {profile_id!r}")
        if profile_id in seen_ids:
            raise AdoptionError(f"adoption stamp contains duplicate profile: {profile_id}")
        seen_ids.add(profile_id)
        project_rules = item.get("project_rules")
        if project_rules is not None and project_rules != PROFILE_RULES_RELATIVE:
            raise AdoptionError(
                f"adoption stamp profile has an invalid project_rules path: {project_rules!r}"
            )
        project_profile = item.get("project_profile")
        if project_profile is not None:
            validate_managed_relative(project_profile)
            expected_profile = profile_document_relative(profile_id)
            if project_profile != expected_profile:
                raise AdoptionError(
                    "adoption stamp profile has an invalid project_profile path: "
                    f"{project_profile!r}"
                )
        roots = item.get("roots")
        if not isinstance(roots, list) or not roots:
            raise AdoptionError(f"adoption stamp profile roots must be a non-empty list: {profile_id}")
        for root in roots:
            if not isinstance(root, str):
                raise AdoptionError(f"adoption stamp profile root must be a string: {profile_id}")
            values.append(f"{profile_id}={root}")
    return parse_profile_selections(values)


def profile_template_sections() -> dict[str, str]:
    """Load and validate the localized common and language-specific sections."""
    try:
        text = profile_template_source().read_text(encoding="utf-8")
    except OSError as exc:
        raise AdoptionError(f"profile template does not exist: {profile_template_source()}") from exc
    sections = {"common": extract_profile_section(text, "common")}
    for profile_id in PROFILE_IDS:
        sections[profile_id] = extract_profile_section(text, profile_id)
    if PROFILE_SCOPE_PLACEHOLDER not in sections["common"]:
        raise AdoptionError(
            f"profile template common section is missing {PROFILE_SCOPE_PLACEHOLDER}"
        )
    return sections


def profile_source_hash(profile_id: str, sections: dict[str, str] | None = None) -> str:
    """Hash the complete localized engineering profile, independent of roots."""
    del sections
    try:
        material = profile_document_template_source(profile_id).read_bytes()
    except OSError as exc:
        raise AdoptionError(
            f"complete profile template does not exist: {profile_document_template_source(profile_id)}"
        ) from exc
    return sha256_hex(material)


def render_profile_document(profiles: list[dict]) -> str:
    """Render one project-owned policy containing only selected languages."""
    if not profiles:
        raise AdoptionError("cannot render a profile document without selected profiles")
    sections = profile_template_sections()
    scope_lines = [
        f"- `{item['id']}`: " + ", ".join(f"`{root}`" for root in item["roots"])
        for item in profiles
    ]
    common = sections["common"].replace(PROFILE_SCOPE_PLACEHOLDER, "\n".join(scope_lines))
    selected = [sections[item["id"]] for item in profiles]
    return "\n\n".join([common, *selected]).rstrip() + "\n"


def profile_metadata(profiles: list[dict]) -> list[dict]:
    """Build the durable, machine-readable selection metadata for the stamp."""
    return [
        {
            "id": item["id"],
            "roots": list(item["roots"]),
            "source_hash": profile_source_hash(item["id"]),
            "project_rules": PROFILE_RULES_RELATIVE,
            "project_profile": profile_document_relative(item["id"]),
        }
        for item in profiles
    ]

# Upgrade scope. "data" files are project memory: the upgrader never writes
# them. "merge" and "template" files are protocol carriers: they may be
# refreshed while local modifications are preserved. "marker" scopes the
# managed region inside AGENTS.md. Keep this in sync with TEMPLATE_FILES,
# RENDERED_FILES and the AGENTS.md entry.
FILE_ROLES = {
    "AGENTS.md": "marker",
    "vault/index.md": "merge",
    "vault/governance.md": "merge",
    "vault/collaboration.md": "data",
    "vault/decisions.md": "data",
    "vault/handoff.md": "data",
    "vault/parked.md": "data",
    "vault/project.md": "data",
    "vault/runtime.md": "data",
    "vault/tasks/README.md": "template",
    "skills/agent-task/SKILL.md": "template",
}
# Paths removed from future releases stay here as an explicit retirement
# allowlist until every supported stamp version can no longer contain them.
# A stamp is evidence about state, not authority to touch arbitrary files.
RETIRED_FILE_ROLES: dict[str, str] = {}
WRITABLE_ROLES = frozenset({"marker", "merge", "template"})

STAMP_RELATIVE = "vault/.agent-init.json"
# One canonical project-identity owner: a tracked single-line UUID bound by
# the helper-managed local retention onboarding. Never written by adopt or
# upgrade; never copied into policy or install stamps.
PROJECT_IDENTITY_RELATIVE = "vault/project-id"
PROPOSAL_DIRECTORY = "vault/.upgrade"
BACKUP_DIRECTORY = ".agent-init-backup"
VERSION_FILE = PROTOCOL_INIT_DIRECTORY / "VERSION"
MIGRATIONS_FILE = PROTOCOL_INIT_DIRECTORY / "MIGRATIONS.md"

# --fetch pulls the latest tagged release from GitHub and re-executes the
# fetched updater against the fetched tree, so protocol-content updates do
# not require reinstalling the Skill package.
FETCH_REPOSITORY = "zlin101/trellium"
FETCH_TAGS_URL = f"https://api.github.com/repos/{FETCH_REPOSITORY}/tags"
FETCH_TARBALL_TEMPLATE = f"https://codeload.github.com/{FETCH_REPOSITORY}/tar.gz/refs/tags/{{tag}}"
FETCH_CACHE_ROOT = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "trellium"
FETCH_MARKER_NAME = ".trellium-fetched"
FETCH_TIMEOUT_SECONDS = 30

EXIT_ACTIONABLE = 2
EXIT_CONFLICT = 3

ANCHORED_WRITES_SUPPORTED = (
    hasattr(os, "O_DIRECTORY")
    and hasattr(os, "O_NOFOLLOW")
    and hasattr(os, "fchmod")
    and os.open in os.supports_dir_fd
    and os.mkdir in os.supports_dir_fd
    and os.stat in os.supports_dir_fd
    and os.stat in os.supports_follow_symlinks
    and os.unlink in os.supports_dir_fd
    and os.rename in os.supports_dir_fd
)
DIRECTORY_OPEN_FLAGS = (
    os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
)
FILE_CREATE_FLAGS = (
    os.O_WRONLY
    | os.O_CREAT
    | os.O_EXCL
    | getattr(os, "O_NOFOLLOW", 0)
    | getattr(os, "O_BINARY", 0)
)
FILE_READ_FLAGS = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)

AGENTS_MARKER_START = "<!-- agent-native-init:start -->"
AGENTS_MARKER_END = "<!-- agent-native-init:end -->"


class AdoptionError(Exception):
    """Raised when an adoption plan cannot be applied safely."""


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def print_action(dry_run: bool, message: str) -> None:
    prefix = "would " if dry_run else ""
    print(f"{prefix}{message}")


def is_within(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def validate_output_metadata(metadata: os.stat_result, path: Path) -> None:
    if stat.S_ISLNK(metadata.st_mode):
        raise AdoptionError(f"refusing to write through symbolic link: {path}")
    if not stat.S_ISREG(metadata.st_mode):
        raise AdoptionError(f"output path is not a regular file: {path}")
    if metadata.st_nlink > 1:
        raise AdoptionError(f"refusing to replace file with multiple hard links: {path}")


def validate_output_paths(target: Path, destinations: list[Path]) -> None:
    """Reject output paths that could escape the resolved target directory."""
    for destination in destinations:
        if not is_within(destination, target) or destination == target:
            raise AdoptionError(f"output path is outside the adoption target: {destination}")

        relative = destination.relative_to(target)
        current = target
        for index, part in enumerate(relative.parts):
            current = current / part
            try:
                metadata = current.lstat()
            except FileNotFoundError:
                continue

            if stat.S_ISLNK(metadata.st_mode):
                raise AdoptionError(f"refusing to write through symbolic link: {current}")

            is_destination = index == len(relative.parts) - 1
            if is_destination:
                validate_output_metadata(metadata, current)
            elif not stat.S_ISDIR(metadata.st_mode):
                raise AdoptionError(f"output parent is not a directory: {current}")

        resolved = destination.resolve(strict=False)
        if not is_within(resolved, target):
            raise AdoptionError(f"output path resolves outside the adoption target: {destination}")


def validate_template_sources(relative_files: tuple[str, ...]) -> None:
    for relative in relative_files:
        source = template_source(relative)
        if not source.is_file():
            raise AdoptionError(f"template file does not exist: {source}")


def validate_relative_output(relative: Path) -> None:
    if (
        relative.is_absolute()
        or not relative.parts
        or any(part in {"", ".", ".."} for part in relative.parts)
    ):
        raise AdoptionError(f"invalid relative output path: {relative}")


def open_child_directory(parent_descriptor: int, name: str, create: bool) -> int:
    try:
        return os.open(name, DIRECTORY_OPEN_FLAGS, dir_fd=parent_descriptor)
    except FileNotFoundError:
        if not create:
            raise
        with suppress(FileExistsError):
            os.mkdir(name, 0o777, dir_fd=parent_descriptor)
        return os.open(name, DIRECTORY_OPEN_FLAGS, dir_fd=parent_descriptor)
def open_target_directory(target: Path, create: bool) -> int:
    """Open an absolute target from its filesystem root without following links."""
    if not target.is_absolute():
        raise AdoptionError(f"adoption target is not absolute: {target}")

    anchor = Path(target.anchor)
    if target == anchor:
        raise AdoptionError(f"refusing to adopt into filesystem root: {target}")

    descriptor = os.open(anchor, DIRECTORY_OPEN_FLAGS)
    try:
        for part in target.relative_to(anchor).parts:
            child_descriptor = open_child_directory(descriptor, part, create=create)
            os.close(descriptor)
            descriptor = child_descriptor
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


@contextmanager
def open_parent_directory(
    target_descriptor: int,
    relative: Path,
    create: bool,
) -> Iterator[tuple[int, str]]:
    """Open an output parent one component at a time without following links."""
    validate_relative_output(relative)
    descriptor = os.dup(target_descriptor)
    try:
        for part in relative.parts[:-1]:
            child_descriptor = open_child_directory(descriptor, part, create=create)
            os.close(descriptor)
            descriptor = child_descriptor
        yield descriptor, relative.parts[-1]
    finally:
        os.close(descriptor)


def output_metadata_at(parent_descriptor: int, name: str) -> os.stat_result | None:
    try:
        return os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return None


def staging_file_at(parent_descriptor: int, destination_name: str) -> tuple[int, str]:
    for _ in range(100):
        staging_name = f".{destination_name}.{secrets.token_hex(8)}.tmp"
        try:
            descriptor = os.open(
                staging_name,
                FILE_CREATE_FLAGS,
                0o666,
                dir_fd=parent_descriptor,
            )
        except FileExistsError:
            continue
        return descriptor, staging_name
    raise AdoptionError(f"could not allocate a staging file for: {destination_name}")


def unlink_at_if_present(parent_descriptor: int, name: str) -> None:
    with suppress(FileNotFoundError):
        # pi-lens-ignore: unchecked-throwing-call-python
        os.unlink(name, dir_fd=parent_descriptor)


def atomic_copy_file_at(
    source: Path,
    parent_descriptor: int,
    destination_name: str,
) -> None:
    descriptor, staging_name = staging_file_at(parent_descriptor, destination_name)
    staging_pending = True
    try:
        source_mode = stat.S_IMODE(source.stat().st_mode)
        with source.open("rb") as source_handle, os.fdopen(descriptor, "wb") as destination_handle:
            descriptor = -1
            os.fchmod(destination_handle.fileno(), source_mode)
            shutil.copyfileobj(source_handle, destination_handle)
            destination_handle.flush()
            os.fsync(destination_handle.fileno())
        os.replace(
            staging_name,
            destination_name,
            src_dir_fd=parent_descriptor,
            dst_dir_fd=parent_descriptor,
        )
        staging_pending = False
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if staging_pending:
            unlink_at_if_present(parent_descriptor, staging_name)


def atomic_write_text_at(
    parent_descriptor: int,
    destination_name: str,
    content: str,
    mode: int | None,
) -> None:
    descriptor, staging_name = staging_file_at(parent_descriptor, destination_name)
    staging_pending = True
    try:
        if mode is not None:
            os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            descriptor = -1
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(
            staging_name,
            destination_name,
            src_dir_fd=parent_descriptor,
            dst_dir_fd=parent_descriptor,
        )
        staging_pending = False
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if staging_pending:
            unlink_at_if_present(parent_descriptor, staging_name)


def read_text_at(parent_descriptor: int, name: str, display_path: Path) -> str:
    descriptor = os.open(name, FILE_READ_FLAGS, dir_fd=parent_descriptor)
    try:
        validate_output_metadata(os.fstat(descriptor), display_path)
        with os.fdopen(descriptor, "r", encoding="utf-8") as handle:
            descriptor = -1
            return handle.read()
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def staging_file(destination: Path) -> tuple[int, Path]:
    for _ in range(100):
        staging = destination.parent / f".{destination.name}.{secrets.token_hex(8)}.tmp"
        try:
            descriptor = os.open(staging, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
        except FileExistsError:
            continue
        return descriptor, staging
    raise AdoptionError(f"could not allocate a staging file for: {destination}")


def set_staging_mode(descriptor: int, staging: Path, mode: int) -> None:
    fchmod = getattr(os, "fchmod", None)
    if fchmod is not None:
        fchmod(descriptor, mode)
    else:
        os.chmod(staging, mode)


def atomic_copy_file(source: Path, destination: Path) -> None:
    descriptor, staging = staging_file(destination)
    staging_pending = True
    try:
        source_mode = stat.S_IMODE(source.stat().st_mode)
        with source.open("rb") as source_handle, os.fdopen(descriptor, "wb") as destination_handle:
            descriptor = -1
            set_staging_mode(destination_handle.fileno(), staging, source_mode)
            shutil.copyfileobj(source_handle, destination_handle)
            destination_handle.flush()
            os.fsync(destination_handle.fileno())
        os.replace(staging, destination)
        staging_pending = False
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if staging_pending and staging.exists():
            staging.unlink()


def atomic_write_text(destination: Path, content: str) -> None:
    mode: int | None = None
    try:
        metadata = destination.lstat()
    except FileNotFoundError:
        pass
    else:
        if stat.S_ISREG(metadata.st_mode):
            mode = stat.S_IMODE(metadata.st_mode)

    descriptor, staging = staging_file(destination)
    staging_pending = True
    try:
        if mode is not None:
            set_staging_mode(descriptor, staging, mode)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            descriptor = -1
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(staging, destination)
        staging_pending = False
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if staging_pending and staging.exists():
            staging.unlink()


def copy_file(
    source: Path,
    destination: Path,
    target: Path,
    force: bool,
    dry_run: bool,
    target_descriptor: int | None,
) -> str:
    if target_descriptor is not None and not dry_run:
        relative = destination.relative_to(target)
        with open_parent_directory(target_descriptor, relative, create=True) as (
            parent_descriptor,
            destination_name,
        ):
            metadata = output_metadata_at(parent_descriptor, destination_name)
            if metadata is not None:
                validate_output_metadata(metadata, destination)
                if not force:
                    return "skipped"

            action = "replace" if metadata is not None else "create"
            print_action(False, f"{action} {destination}")
            atomic_copy_file_at(source, parent_descriptor, destination_name)
            return action

    if not dry_run:
        validate_output_paths(target, [destination])
    if destination.exists() and not force:
        return "skipped"

    action = "replace" if destination.exists() else "create"
    print_action(dry_run, f"{action} {destination}")
    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        atomic_copy_file(source, destination)
    return action


def write_text_file(
    destination: Path,
    content: str,
    target: Path,
    force: bool,
    dry_run: bool,
    target_descriptor: int | None,
) -> str:
    if target_descriptor is not None and not dry_run:
        relative = destination.relative_to(target)
        with open_parent_directory(target_descriptor, relative, create=True) as (
            parent_descriptor,
            destination_name,
        ):
            metadata = output_metadata_at(parent_descriptor, destination_name)
            if metadata is not None:
                validate_output_metadata(metadata, destination)
                if not force:
                    return "skipped"

            action = "replace" if metadata is not None else "create"
            print_action(False, f"{action} {destination}")
            mode = stat.S_IMODE(metadata.st_mode) if metadata is not None else None
            atomic_write_text_at(parent_descriptor, destination_name, content, mode)
            return action

    if not dry_run:
        validate_output_paths(target, [destination])
    if destination.exists() and not force:
        return "skipped"

    action = "replace" if destination.exists() else "create"
    print_action(dry_run, f"{action} {destination}")
    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(destination, content)
    return action


def append_agent_entry(
    target: Path,
    dry_run: bool,
    target_descriptor: int | None,
) -> str:
    agents_path = target / "AGENTS.md"
    if target_descriptor is not None and not dry_run:
        with open_parent_directory(target_descriptor, Path("AGENTS.md"), create=True) as (
            parent_descriptor,
            destination_name,
        ):
            metadata = output_metadata_at(parent_descriptor, destination_name)
            if metadata is None:
                print_action(False, f"create {agents_path}")
                atomic_copy_file_at(TEMPLATES_ROOT / "AGENTS.md", parent_descriptor, destination_name)
                return "create"

            validate_output_metadata(metadata, agents_path)
            current = read_text_at(parent_descriptor, destination_name, agents_path)
            if AGENTS_MARKER_START in current or "vault/index.md" in current:
                print_action(False, f"keep existing Trellium entry in {agents_path}")
                return "skipped"

            section = agent_entry_section()
            print_action(False, f"append Trellium entry to {agents_path}")
            atomic_write_text_at(
                parent_descriptor,
                destination_name,
                current.rstrip() + section + "\n",
                stat.S_IMODE(metadata.st_mode),
            )
            return "updated"

    if not dry_run:
        validate_output_paths(target, [agents_path])
    if not agents_path.exists():
        return copy_file(
            TEMPLATES_ROOT / "AGENTS.md",
            agents_path,
            target,
            force=False,
            dry_run=dry_run,
            target_descriptor=None,
        )

    current = agents_path.read_text(encoding="utf-8")
    if AGENTS_MARKER_START in current or "vault/index.md" in current:
        print_action(dry_run, f"keep existing Trellium entry in {agents_path}")
        return "skipped"

    section = agent_entry_section()

    print_action(dry_run, f"append Trellium entry to {agents_path}")
    if not dry_run:
        atomic_write_text(agents_path, current.rstrip() + section + "\n")
    return "updated"


def agent_entry_section() -> str:
    return f"""

{AGENTS_MARKER_START}
## Trellium

For non-trivial work, read these files before editing:

1. `vault/index.md` (includes the task-level and authority cheat sheet)
2. `vault/runtime.md`

Read `vault/governance.md` in full for Level B or Level C work, unclear classification, or governance-rule changes.

Use `vault/project.md` on first entry, `vault/handoff.md` when resuming interrupted work, and `vault/tasks/` for tracked or governed tasks.

When modifying or reviewing source code, public APIs, dependencies, builds, concurrency, or lifecycle behavior, read the profile under `docs/engineering/profiles/` whose declared root matches the current path. Apply only the profile for the file's actual language; do not load unmatched languages. Pure documentation work - comments, doc comments, docstrings, TODO/FIXME notes, or directive placement - reads the Comment/API Documentation Policy (`docs/engineering/code-comments.md`) alone, which solely owns that expression guidance. When a public API changes, or behavior and comments change together, read both the profile and the Comment/API Documentation Policy: the Comment Policy wins on expression guidance, while API behavior, security, errors, and compatibility stay governed by the profile.
{AGENTS_MARKER_END}
"""


def safe_project_readme(target: Path, target_descriptor: int | None) -> str | None:
    readme = target / "README.md"
    if target_descriptor is not None:
        try:
            with open_parent_directory(target_descriptor, Path("README.md"), create=False) as (
                parent_descriptor,
                readme_name,
            ):
                metadata = output_metadata_at(parent_descriptor, readme_name)
                if (
                    metadata is None
                    or not stat.S_ISREG(metadata.st_mode)
                    or metadata.st_nlink > 1
                ):
                    return None

                descriptor = os.open(readme_name, FILE_READ_FLAGS, dir_fd=parent_descriptor)
                try:
                    opened_metadata = os.fstat(descriptor)
                    if not stat.S_ISREG(opened_metadata.st_mode) or opened_metadata.st_nlink > 1:
                        return None
                    with os.fdopen(descriptor, "r", encoding="utf-8", errors="ignore") as handle:
                        descriptor = -1
                        return handle.read()
                finally:
                    if descriptor >= 0:
                        os.close(descriptor)
        except OSError:
            return None

    try:
        metadata = readme.lstat()
    except OSError:
        return None
    if (
        not stat.S_ISREG(metadata.st_mode)
        or metadata.st_nlink > 1
        or not is_within(readme.resolve(strict=False), target)
    ):
        return None
    try:
        return readme.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def project_summary(target: Path, target_descriptor: int | None) -> str:
    readme_content = safe_project_readme(target, target_descriptor)
    if readme_content is not None:
        for line in readme_content.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                return stripped
    return f"{target.name} project."


def render_project(target: Path, target_descriptor: int | None) -> str:
    return f"""# Project Context

## Summary

{project_summary(target, target_descriptor)}

## Goals

- Keep project-specific goals here.

## Current Phase

Existing project adoption via Trellium.

## In Scope

- Existing project behavior.
- Agent collaboration layer.

## Out of Scope

- Business source, dependencies, CI, deployment, secrets, and data models unless explicitly approved.

## Technical Direction

- Follow the existing project structure and tooling.

## Boundaries

Future Agents should preserve existing project behavior and request approval before high-impact changes.
"""


def render_runtime(target: Path) -> str:
    today = date.today().isoformat()
    return f"""# Runtime Context

## Current Phase

Trellium adoption recorded on {today}.

## Focus

- (none)

Focus is optional navigation only. It owns no lifecycle, authority, slice,
gate, or active-task inventory; `trellium status` reads TASK state directly
from task files.

Acceptance: `AGENTS.md`, `vault/`, and `skills/agent-task/SKILL.md` exist and route future Agents to project memory.

Required Check: `python3 trellium.py adopt {target} --dry-run` from a Trellium checkout or Skill package, when available.

## Current Progress

- Agent collaboration layer has been initialized or refreshed.

## Constraints

- Move long execution history to `vault/tasks/*`.
- Demote paused tasks to `vault/parked.md` entries.
- Do not save secrets.
- Keep this file short; current line and entry budgets live in the `trellium-policy` block in `vault/index.md`.

## Recent Changes

- Added Trellium project memory files.

## Known Risks

- Replace template text with project facts as the project evolves.

## Required Checks

```bash
find vault -maxdepth 2 -type f | sort
```

## Next Steps

- Update `vault/project.md` with durable project facts.
- Update `vault/governance.md` only when project-specific governance differs from the default.
"""


# --- Upgrade mechanism -----------------------------------------------------
#
# Project data is never replaced by upgrades. Protocol files follow the
# upstream template when the project has not modified them; diverging copies
# produce a proposal that the agent merges and the user confirms.


PLAN_SECTIONS = (
    ("pending", "?", "pending proposals from a previous upgrade"),
    ("conflict", "!", "local and upstream both changed; a proposal is written for agent merge"),
    ("apply", "~", "local copy is pristine; refresh from the upstream template"),
    ("add", "+", "new protocol file; create from the template"),
    ("add_skip", "+", "new protocol file already exists locally; kept"),
    ("remove", "-", "no longer shipped; local copy is pristine; remove"),
    ("remove_keep", "-", "no longer shipped; local copy was modified; kept"),
    ("keep", "o", "locally customized; upstream unchanged; kept"),
    ("protected", "x", "project data; never touched by upgrades"),
    ("missing", "!", "tracked file is missing"),
    ("in_sync", "=", "already matches upstream"),
)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_path(path: Path) -> str | None:
    try:
        return sha256_hex(path.read_bytes())
    except OSError:
        return None


def validate_managed_relative(relative: object) -> str:
    """Validate one stamp-managed path without normalizing unsafe syntax."""
    if not isinstance(relative, str):
        raise AdoptionError(f"invalid managed path: {relative!r}")
    components = relative.split("/")
    path = PurePosixPath(relative)
    if (
        not relative
        or "\\" in relative
        or "\0" in relative
        or path.is_absolute()
        or any(component in {"", ".", ".."} for component in components)
        or path.as_posix() != relative
    ):
        raise AdoptionError(f"invalid managed path: {relative!r}")
    return relative


def validate_stamp_file_paths(stamp: dict) -> None:
    files = stamp.get("files")
    if not isinstance(files, dict):
        raise AdoptionError("adoption stamp files must be an object")
    profiles = selections_from_stamp(stamp)
    managed_roles = managed_upgrade_file_roles(profiles, include_retired=True)
    for relative, entry in files.items():
        validate_managed_relative(relative)
        if relative in (STAMP_RELATIVE, PROPOSAL_DIRECTORY, BACKUP_DIRECTORY) or relative.startswith(
            (f"{PROPOSAL_DIRECTORY}/", f"{BACKUP_DIRECTORY}/")
        ):
            raise AdoptionError(
                f"managed path uses a reserved internal namespace: {relative!r}"
            )
        if relative == PROFILE_RULES_RELATIVE and not profiles:
            raise AdoptionError(
                f"adoption stamp tracks {PROFILE_RULES_RELATIVE} without profile metadata; "
                "refusing to classify the project-owned policy as removable"
            )
        if relative not in managed_roles:
            raise AdoptionError(
                f"adoption stamp path is outside the explicit managed-file set: {relative!r}"
            )
        if not isinstance(entry, dict):
            raise AdoptionError(f"adoption stamp file entry must be an object: {relative!r}")
        role = entry.get("role")
        allowed_roles = {managed_roles[relative]}
        if relative == "AGENTS.md":
            allowed_roles.add("merge")
        if role is not None and role not in allowed_roles:
            raise AdoptionError(
                f"adoption stamp has an invalid role for {relative!r}: {role!r}"
            )


def managed_upgrade_file_roles(
    profiles: list[dict], *, include_retired: bool = False
) -> dict[str, str]:
    """Return the finite file set this installation may inspect or mutate."""
    roles = dict(RETIRED_FILE_ROLES) if include_retired else {}
    roles.update(FILE_ROLES)
    # Helper-managed identity: stamp registration is allowed (data role), but
    # no template exists and no upgrade path may propose or write it.
    roles[PROJECT_IDENTITY_RELATIVE] = "data"
    if profiles:
        roles[PROFILE_RULES_RELATIVE] = "merge"
        for profile in profiles:
            roles[profile_document_relative(profile["id"])] = "merge"
    return roles


def managed_file_metadata(target: Path, relative: str) -> os.stat_result | None:
    """Validate containment and metadata for an existing managed input."""
    validate_managed_relative(relative)
    path = target / relative
    validate_output_paths(target, [path])
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return None
    validate_output_metadata(metadata, path)
    return metadata


def read_managed_bytes(
    target: Path,
    relative: str,
    target_descriptor: int | None = None,
) -> bytes | None:
    validate_managed_relative(relative)
    path = target / relative
    if target_descriptor is not None:
        try:
            with open_parent_directory(
                target_descriptor, Path(relative), create=False
            ) as (parent_descriptor, name):
                metadata = output_metadata_at(parent_descriptor, name)
                if metadata is None:
                    return None
                validate_output_metadata(metadata, path)
                descriptor = os.open(name, FILE_READ_FLAGS, dir_fd=parent_descriptor)
                try:
                    validate_output_metadata(os.fstat(descriptor), path)
                    with os.fdopen(descriptor, "rb") as handle:
                        descriptor = -1
                        return handle.read()
                finally:
                    if descriptor >= 0:
                        os.close(descriptor)
        except FileNotFoundError:
            return None
    metadata = managed_file_metadata(target, relative)
    if metadata is None:
        return None
    descriptor = os.open(path, FILE_READ_FLAGS)
    try:
        validate_output_metadata(os.fstat(descriptor), path)
        with os.fdopen(descriptor, "rb") as handle:
            descriptor = -1
            return handle.read()
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def read_managed_text(
    target: Path,
    relative: str,
    target_descriptor: int | None = None,
) -> str | None:
    data = read_managed_bytes(target, relative, target_descriptor)
    if data is None:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeError as exc:
        raise AdoptionError(f"managed file is not valid UTF-8: {target / relative}") from exc


def marker_region(text: str) -> str | None:
    start = text.find(AGENTS_MARKER_START)
    if start < 0:
        return None
    end = text.find(AGENTS_MARKER_END, start)
    if end < 0:
        return None
    return text[start : end + len(AGENTS_MARKER_END)]


def strict_marker_region(text: str) -> str | None:
    """Return the marker only when both delimiters are unique and ordered."""
    if text.count(AGENTS_MARKER_START) != 1 or text.count(AGENTS_MARKER_END) != 1:
        return None
    start = text.find(AGENTS_MARKER_START)
    end = text.find(AGENTS_MARKER_END)
    if start < 0 or end < start + len(AGENTS_MARKER_START):
        return None
    return text[start : end + len(AGENTS_MARKER_END)]


def upstream_marker_region() -> str:
    region = marker_region(agent_entry_section())
    if region is None:
        raise AdoptionError("agent entry section is missing its markers")
    return region


def replace_marker_region(text: str, new_region: str) -> str:
    start = text.find(AGENTS_MARKER_START)
    end = text.find(AGENTS_MARKER_END, start)
    if start < 0 or end < 0:
        raise AdoptionError("Trellium marker region not found")
    end += len(AGENTS_MARKER_END)
    return text[:start] + new_region + text[end:]


def read_protocol_version() -> str:
    try:
        version = VERSION_FILE.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise AdoptionError(
            f"protocol version file is missing: {VERSION_FILE}; it must ship with the repository"
        ) from exc
    if not version:
        raise AdoptionError(f"protocol version file is empty: {VERSION_FILE}")
    return version


def parse_version(version: str | None) -> tuple[int, ...] | None:
    if not version:
        return None
    try:
        return tuple(int(part) for part in version.split("."))
    except ValueError:
        return None


def read_migration_sections() -> list[tuple[str, str]]:
    """Return (version, title) pairs for every release section in MIGRATIONS.md."""
    try:
        content = MIGRATIONS_FILE.read_text(encoding="utf-8")
    except OSError:
        return []
    sections: list[tuple[str, str]] = []
    for line in content.splitlines():
        if not line.startswith("## "):
            continue
        header = line[3:].strip()
        parts = header.split(None, 1)
        if not parts or parse_version(parts[0]) is None:
            continue
        title = parts[1].strip() if len(parts) > 1 else ""
        title = title.lstrip("—–- ").strip()
        sections.append((parts[0], title))
    return sections


def migrations_after(version: str | None) -> list[tuple[str, str]]:
    installed = parse_version(version)
    if installed is None:
        return read_migration_sections()
    return [
        section
        for section in read_migration_sections()
        if (parsed := parse_version(section[0])) is not None and parsed > installed
    ]


def stamp_path(target: Path) -> Path:
    return target / STAMP_RELATIVE


def read_stamp(target: Path, target_descriptor: int | None = None) -> dict | None:
    path = stamp_path(target)
    try:
        raw = read_managed_text(target, STAMP_RELATIVE, target_descriptor)
        if raw is None:
            return None
    except FileNotFoundError:
        return None
    except (AdoptionError, OSError, UnicodeError) as exc:
        raise AdoptionError(f"could not read adoption stamp: {path}: {exc}") from exc
    try:
        stamp = json.loads(raw)
    except ValueError as exc:
        raise AdoptionError(f"adoption stamp is not valid JSON: {path}") from exc
    if not isinstance(stamp, dict) or not isinstance(stamp.get("files"), dict):
        raise AdoptionError(f"adoption stamp has an unexpected schema: {path}")
    validate_stamp_file_paths(stamp)
    return stamp


def assert_upgrade_writable(
    target: Path,
    relative: str,
    profiles: list[dict] | None = None,
) -> None:
    """Refuse writes outside the protocol-carrier scope during upgrades."""
    validate_managed_relative(relative)
    role = managed_upgrade_file_roles(
        profiles or [], include_retired=True
    ).get(relative)
    if role is None:
        raise AdoptionError(
            f"refusing to write outside the explicit managed-file set: {relative}"
        )
    if role in WRITABLE_ROLES:
        return
    if role == "data" and not (target / relative).exists():
        # Creating an absent starter template never discards project data.
        return
    raise AdoptionError(
        f"refusing to write outside the protocol upgrade scope: {relative} (role: {role or 'untracked'})"
    )


def local_hash_for_role(
    target: Path,
    relative: str,
    role: str,
    target_descriptor: int | None = None,
) -> str | None:
    data = read_managed_bytes(target, relative, target_descriptor)
    if data is None:
        return None
    if role != "marker":
        return sha256_hex(data)
    text = data.decode("utf-8")
    region = marker_region(text)
    if region is None:
        return None
    return sha256_hex(region.encode("utf-8"))


def upstream_hash_for_role(
    relative: str,
    role: str,
    profiles: list[dict] | None = None,
) -> str | None:
    if relative == PROFILE_RULES_RELATIVE:
        if not profiles:
            return None
        return sha256_hex(render_profile_document(profiles).encode("utf-8"))
    profile = profile_for_relative(relative, profiles or [])
    if profile is not None:
        return sha256_hex(render_durable_profile(profile).encode("utf-8"))
    if role == "marker":
        return sha256_hex(upstream_marker_region().encode("utf-8"))
    return hash_path(template_source(relative))


def open_upgrade_descriptor(target: Path) -> int | None:
    if not ANCHORED_WRITES_SUPPORTED:
        return None
    return open_target_directory(target, create=False)


def resolve_existing_target(value: str) -> Path:
    try:
        target = Path(value).expanduser().resolve()
    except (OSError, RuntimeError) as exc:
        raise AdoptionError(f"could not resolve target: {exc}") from exc
    if target == Path(target.anchor):
        raise AdoptionError(f"refusing to operate on filesystem root: {target}")
    if not target.is_dir():
        raise AdoptionError(f"target is not an existing directory: {target}")
    return target


def write_stamp_file(target: Path, stamp: dict, target_descriptor: int | None) -> None:
    content = json.dumps(stamp, indent=2, sort_keys=True) + "\n"
    if target_descriptor is not None:
        relative = Path(STAMP_RELATIVE)
        with open_parent_directory(target_descriptor, relative, create=True) as (
            parent_descriptor,
            name,
        ):
            metadata = output_metadata_at(parent_descriptor, name)
            mode = stat.S_IMODE(metadata.st_mode) if metadata is not None else None
            if metadata is not None:
                validate_output_metadata(metadata, target / STAMP_RELATIVE)
            atomic_write_text_at(parent_descriptor, name, content, mode)
        return
    destination = target / STAMP_RELATIVE
    validate_output_paths(target, [destination])
    destination.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(destination, content)


def write_adoption_stamp(
    target: Path,
    actions: dict[str, str],
    rendered_files: dict[str, str],
    profiles: list[dict],
    target_descriptor: int | None,
) -> None:
    previous = read_stamp(target, target_descriptor) or {}
    previous_files = previous.get("files", {}) if isinstance(previous, dict) else {}
    files: dict[str, dict] = {}
    for relative, role in FILE_ROLES.items():
        action = actions.get(relative, "skipped")
        if relative == "AGENTS.md":
            # Two flavors: a template file copied wholesale (whole-file "merge"
            # semantics) or a marker section appended to a user file ("marker"
            # semantics). The stamp records which one was installed.
            if action == "create":
                template_hash = hash_path(TEMPLATES_ROOT / "AGENTS.md")
                if template_hash is None:
                    raise AdoptionError(f"template file does not exist: {TEMPLATES_ROOT / 'AGENTS.md'}")
                entry: dict[str, object] = {"role": "merge", "baseline": template_hash}
            elif action == "updated":
                entry = {"role": "marker", "baseline": sha256_hex(upstream_marker_region().encode("utf-8"))}
            else:
                agents_text = read_managed_text(target, relative, target_descriptor)
                if agents_text is None:
                    continue
                region = marker_region(agents_text)
                if region is not None:
                    entry = {"role": "marker", "baseline": sha256_hex(region.encode("utf-8"))}
                else:
                    entry = {"role": "merge", "baseline": sha256_hex(agents_text.encode("utf-8"))}
        elif relative in rendered_files:
            if action != "skipped":
                entry = {"role": role, "baseline": sha256_hex(rendered_files[relative].encode("utf-8"))}
            else:
                baseline = local_hash_for_role(
                    target, relative, role, target_descriptor
                )
                if baseline is None:
                    continue
                entry = {"role": role, "baseline": baseline}
        else:
            template_hash = hash_path(template_source(relative))
            if template_hash is None:
                raise AdoptionError(f"template file does not exist: {template_source(relative)}")
            if action != "skipped":
                entry = {"role": role, "baseline": template_hash}
            else:
                baseline = local_hash_for_role(
                    target, relative, role, target_descriptor
                )
                if baseline is None:
                    entry = {"role": role, "baseline": template_hash}
                else:
                    entry = {"role": role, "baseline": baseline}
        if action == "skipped":
            preserved = previous_files.get(relative)
            if preserved is not None and preserved.get("baseline") == entry["baseline"]:
                entry = dict(preserved)
            else:
                # We did not write these bytes; they are only observed, so later
                # upstream changes must produce proposals instead of auto-replace.
                entry["observed"] = True
        files[relative] = entry

    if profiles:
        relative = PROFILE_RULES_RELATIVE
        action = actions.get(relative, "skipped")
        local_hash = local_hash_for_role(
            target, relative, "merge", target_descriptor
        )
        if local_hash is None:
            raise AdoptionError(f"profile rule file does not exist after adoption: {target / relative}")
        entry = {"role": "merge", "baseline": local_hash}
        if action == "skipped":
            preserved = previous_files.get(relative)
            if preserved is not None and preserved.get("baseline") == local_hash:
                entry = dict(preserved)
            else:
                entry["observed"] = True
        files[relative] = entry
        for profile in profiles:
            relative = profile_document_relative(profile["id"])
            local_hash = local_hash_for_role(
                target, relative, "merge", target_descriptor
            )
            if local_hash is None:
                raise AdoptionError(f"durable profile does not exist after adoption: {target / relative}")
            entry = {"role": "merge", "baseline": local_hash}
            if actions.get(relative, "skipped") == "skipped":
                preserved = previous_files.get(relative)
                if preserved is not None and preserved.get("baseline") == local_hash:
                    entry = dict(preserved)
                else:
                    entry["observed"] = True
            files[relative] = entry
    # Helper-managed project identity: preserve an existing registration
    # verbatim so repeat adopt/upgrade never drops the binding or the Git
    # durability coverage that the stamp inventory provides for it.
    preserved_identity = previous_files.get(PROJECT_IDENTITY_RELATIVE)
    if isinstance(preserved_identity, dict) and preserved_identity.get("role") == "data":
        files[PROJECT_IDENTITY_RELATIVE] = dict(preserved_identity)
    stamp = {
        "schema_version": 2,
        "protocol_version": read_protocol_version(),
        "adopted_at": previous.get("adopted_at") or date.today().isoformat(),
        "last_upgrade": previous.get("last_upgrade"),
        "trust": previous.get("trust", "versioned"),
        "profiles": profile_metadata(profiles),
        "files": files,
    }
    write_stamp_file(target, stamp, target_descriptor)


def build_upgrade_plan(target: Path, stamp: dict) -> dict[str, list[dict]]:
    validate_stamp_file_paths(stamp)
    trust = stamp.get("trust", "versioned")
    entries: dict[str, dict] = stamp["files"]
    profiles = selections_from_stamp(stamp)
    if PROFILE_RULES_RELATIVE in entries and not profiles:
        raise AdoptionError(
            f"adoption stamp tracks {PROFILE_RULES_RELATIVE} without profile metadata; "
            "refusing to classify the project-owned policy as removable"
        )
    desired_roles = managed_upgrade_file_roles(profiles)
    plan: dict[str, list[dict]] = {key: [] for key, _, _ in PLAN_SECTIONS}

    for relative, entry in sorted(entries.items()):
        role = entry.get("role") or desired_roles.get(relative, "template")
        if entry.get("pending"):
            plan["pending"].append(
                {"path": relative, "role": role, "reason": "resolve the proposal, then run upgrade --complete"}
            )
            continue
        if relative not in desired_roles:
            local = local_hash_for_role(target, relative, role)
            if local is None:
                plan["missing"].append({"path": relative, "role": role, "reason": "no longer shipped and missing locally"})
            elif local == entry.get("baseline"):
                plan["remove"].append({"path": relative, "role": role, "reason": "no longer shipped; local copy is pristine"})
            else:
                plan["remove_keep"].append({"path": relative, "role": role, "reason": "no longer shipped; local copy was modified"})
            continue
        if role == "data":
            plan["protected"].append({"path": relative, "role": role, "reason": "project data is never replaced by upgrades"})
            continue
        upstream = upstream_hash_for_role(relative, role, profiles)
        local = local_hash_for_role(target, relative, role)
        baseline = entry.get("baseline")
        observed = bool(entry.get("observed")) or trust == "unversioned"
        if upstream is None:
            plan["missing"].append({"path": relative, "role": role, "reason": "upstream template is missing from this repository"})
        elif local is None:
            if role == "marker":
                plan["add"].append({"path": relative, "role": role, "reason": "marker region absent; append the Trellium entry"})
            else:
                plan["missing"].append({"path": relative, "role": role, "reason": "file is missing locally; re-run adopt or restore it"})
        elif local == upstream:
            plan["in_sync"].append({"path": relative, "role": role})
        elif local == baseline:
            if observed:
                if upstream == entry.get("absorbed_upstream"):
                    plan["in_sync"].append(
                        {"path": relative, "role": role, "reason": "this upstream version is already absorbed"}
                    )
                else:
                    plan["conflict"].append(
                        {"path": relative, "role": role, "reason": "baseline was observed, not written; upstream changed"}
                    )
            else:
                plan["apply"].append({"path": relative, "role": role, "reason": "local copy is pristine; upstream updated"})
        elif upstream == baseline:
            plan["keep"].append({"path": relative, "role": role, "reason": "locally customized; upstream unchanged"})
        else:
            plan["conflict"].append({"path": relative, "role": role, "reason": "local and upstream both changed"})

    for relative, role in sorted(desired_roles.items()):
        if relative == PROJECT_IDENTITY_RELATIVE:
            # Identity is helper-managed: upgrades never propose, create, or
            # auto-add it; first binding is an authorized semantic step.
            continue
        if relative in entries or relative in RENDERED_FILES:
            continue
        metadata = managed_file_metadata(target, relative)
        if role == "marker":
            text = read_managed_text(target, relative) if metadata is not None else ""
            assert text is not None
            if marker_region(text) is not None:
                plan["add_skip"].append({"path": relative, "role": role, "reason": "marker region present but untracked; kept"})
            elif "vault/index.md" in text:
                plan["add_skip"].append({"path": relative, "role": role, "reason": "agent entry already routes to the vault; kept"})
            else:
                plan["add"].append({"path": relative, "role": role, "reason": "append the Trellium entry"})
            continue
        if metadata is not None and profile_for_relative(relative, profiles) is not None:
            plan["conflict"].append(
                {
                    "path": relative,
                    "role": role,
                    "reason": "pre-existing complete profile is untracked; review and adopt it through a proposal",
                }
            )
        elif metadata is not None:
            plan["add_skip"].append(
                {"path": relative, "role": role, "reason": "exists locally but untracked; kept (run baseline to track it)"}
            )
        else:
            plan["add"].append({"path": relative, "role": role, "reason": "new protocol file"})

    return plan


def plan_exit_code(plan: dict[str, list[dict]]) -> int:
    if plan["conflict"] or plan["pending"]:
        return EXIT_CONFLICT
    if plan["apply"] or plan["add"] or plan["remove"]:
        return EXIT_ACTIONABLE
    return 0


def print_plan(plan: dict[str, list[dict]]) -> None:
    for key, symbol, description in PLAN_SECTIONS:
        items = plan.get(key, [])
        if not items:
            continue
        print(f"{key} ({description}):")
        for item in items:
            reason = item.get("reason")
            suffix = f"  # {reason}" if reason else ""
            print(f"  {symbol} {item['path']}{suffix}")
        print()


def print_upgrade_header(target: Path, stamp: dict) -> None:
    installed = stamp.get("protocol_version") or "unknown (unversioned baseline)"
    available = read_protocol_version()
    relationship = "==" if installed == available else "->"
    print(f"upgrade report for {target}")
    print(f"installed protocol: {installed} {relationship} available: {available}")
    print()


def print_playbook(sections: list[tuple[str, str]]) -> None:
    if not sections:
        return
    print("migration playbook (init/MIGRATIONS.md):")
    for version, title in sections:
        print(f"  * {version} - {title}")
    print()


# --- Vault check (read-only) -----------------------------------------------
#
# `check` validates the minimal canonical state layer: the trellium-task-state
# block in Level B/C task files, the trellium-policy block in vault/index.md,
# hot-file budgets, and TASK storage versus Git. It never writes, never
# executes content, and never follows symbolic links into vault inputs.

CHECK_ERROR_EXIT = 2

TASK_STATE_MARKER = "trellium-task-state"
POLICY_MARKER = "trellium-policy"
COMMENT_BLOCK_END = "-->"

TASK_ID_PATTERN = r"TASK-[0-9]{4,}"
TASK_ID_RE = re.compile(rf"^{TASK_ID_PATTERN}$")
TASK_FILE_ID_RE = re.compile(rf"^({TASK_ID_PATTERN})(?:-|\.md$)")
REVIEW_LEDGER_RE = re.compile(rf"^{TASK_ID_PATTERN}-review\.md$")

LIFECYCLE_VALUES = ("draft", "active", "blocked", "ready_for_review", "accepted", "superseded")
GATE_VALUES = ("pending", "in_progress", "passed", "partial", "blocked", "not_authorized", "not_applicable")
STORAGE_MODES = ("tracked", "local", "private")
TASK_STORAGE_VALUES = ("tracked", "local")
POLICY_SCHEMA_VERSIONS = (1, 2)

STATE_REQUIRED_FIELDS = ("schema_version", "task_id", "level", "authority_level", "lifecycle")
STATE_OPTIONAL_FIELDS = ("current_slice", "gates")

BUDGET_FILE_KEYS = {
    "runtime": ("max_lines", "max_recent_entries"),
    "handoff": ("max_lines", "max_entries"),
    "decisions": ("max_lines", "max_records"),
    "parked": ("max_lines", "max_entries"),
    "tasks": ("max_active_tasks",),
}
# Maps a configured policy threshold to the measurement key it constrains.
BUDGET_MEASUREMENT_KEYS = {
    "runtime": {"max_lines": "lines", "max_recent_entries": "recent_entries"},
    "handoff": {"max_lines": "lines", "max_entries": "entries"},
    "decisions": {"max_lines": "lines", "max_records": "records"},
    "parked": {"max_lines": "lines", "max_entries": "entries"},
}

REQUIRED_VAULT_FILES = (
    "vault/index.md",
    "vault/project.md",
    "vault/governance.md",
    "vault/runtime.md",
    "vault/handoff.md",
    "vault/decisions.md",
    "vault/parked.md",
    "vault/tasks/README.md",
)

FINDING_PHASES = (
    "required-files",
    "policy",
    "task-state",
    "budgets",
    "storage",
)


def _reject_json_constant(name: str) -> None:
    raise ValueError(f"non-standard JSON constant: {name}")


def is_strict_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def extract_comment_blocks(text: str, marker: str) -> tuple[list[str], str | None]:
    """Return the payloads of every `<!-- marker ... -->` block in the text."""
    start_token = f"<!-- {marker}"
    payloads: list[str] = []
    index = 0
    while True:
        start = text.find(start_token, index)
        if start < 0:
            return payloads, None
        following = text[start + len(start_token) : start + len(start_token) + 1]
        if following and following not in ("\n", "\r"):
            # A different marker that merely shares the prefix (e.g.
            # trellium-policy-history) is not a block of this marker.
            index = start + len(start_token)
            continue
        end = text.find(COMMENT_BLOCK_END, start)
        if end < 0:
            return [], f"unterminated <!-- {marker} ... --> block"
        payloads.append(text[start + len(start_token) : end].strip())
        index = end + len(COMMENT_BLOCK_END)


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_block_object(payload: str) -> tuple[dict | None, str]:
    try:
        value = json.loads(
            payload,
            parse_constant=_reject_json_constant,
            object_pairs_hook=_reject_duplicate_keys,
        )
    except ValueError as exc:
        return None, f"invalid JSON ({exc})"
    if not isinstance(value, dict):
        return None, "block content is not a JSON object"
    return value, ""


def validate_state_object(state: dict) -> list[str]:
    errors: list[str] = []
    known = set(STATE_REQUIRED_FIELDS) | set(STATE_OPTIONAL_FIELDS)
    unknown = sorted(set(state) - known)
    if unknown:
        errors.append(f"unknown field(s): {', '.join(unknown)}")
    missing = [field for field in STATE_REQUIRED_FIELDS if field not in state]
    if missing:
        errors.append(f"missing field(s): {', '.join(missing)}")

    if "schema_version" in state and (
        not is_strict_int(state["schema_version"]) or state["schema_version"] != 1
    ):
        errors.append("schema_version must be the integer 1")
    if "task_id" in state:
        task_id = state["task_id"]
        if not isinstance(task_id, str) or TASK_ID_RE.match(task_id) is None:
            errors.append(f"task_id must match {TASK_ID_PATTERN}")
    if "level" in state and state["level"] not in ("B", "C"):
        errors.append('level must be "B" or "C"')
    if "authority_level" in state:
        authority = state["authority_level"]
        if not is_strict_int(authority) or not 0 <= authority <= 4:
            errors.append("authority_level must be an integer in 0..4")
    if "lifecycle" in state and state["lifecycle"] not in LIFECYCLE_VALUES:
        errors.append(f"lifecycle must be one of: {', '.join(LIFECYCLE_VALUES)}")
    if "current_slice" in state:
        current_slice = state["current_slice"]
        if not isinstance(current_slice, str) or not current_slice.strip():
            errors.append("current_slice must be a non-empty string")
    if "gates" in state:
        gates = state["gates"]
        if not isinstance(gates, dict):
            errors.append("gates must be an object")
        else:
            for gate_id, gate_value in gates.items():
                if not isinstance(gate_id, str) or not gate_id.strip():
                    errors.append("gate ids must be non-empty strings")
                elif gate_value not in GATE_VALUES:
                    errors.append(
                        f"gate {gate_id!r} must be one of: {', '.join(GATE_VALUES)}"
                    )
    return errors


def validate_policy_object(policy: dict) -> list[str]:
    errors: list[str] = []
    schema_version = policy.get("schema_version")
    schema_v2 = is_strict_int(schema_version) and schema_version == 2
    known = {"schema_version", "storage_mode", "budgets"} if schema_v2 else {"schema_version", "task_storage", "budgets"}
    unknown = sorted(set(policy) - known)
    if unknown:
        errors.append(f"unknown field(s): {', '.join(unknown)}")
    if "schema_version" in policy and (
        not is_strict_int(schema_version) or schema_version not in POLICY_SCHEMA_VERSIONS
    ):
        errors.append("schema_version must be the integer 1 or 2")
    if schema_v2:
        if "task_storage" in policy:
            errors.append("task_storage must not appear in schema 2; use storage_mode")
        if "storage_mode" not in policy:
            errors.append("missing field(s): storage_mode")
        elif policy["storage_mode"] not in STORAGE_MODES:
            errors.append(f"storage_mode must be one of: {', '.join(STORAGE_MODES)}")
    else:
        missing = [field for field in ("schema_version", "task_storage") if field not in policy]
        if missing:
            errors.append(f"missing field(s): {', '.join(missing)}")
        if "task_storage" in policy and policy["task_storage"] not in TASK_STORAGE_VALUES:
            errors.append(f"task_storage must be one of: {', '.join(TASK_STORAGE_VALUES)}")
    if "budgets" in policy:
        budgets = policy["budgets"]
        if not isinstance(budgets, dict):
            errors.append("budgets must be an object")
        else:
            for file_key, thresholds in budgets.items():
                allowed = BUDGET_FILE_KEYS.get(file_key)
                if allowed is None:
                    errors.append(f"unknown budgets key: {file_key}")
                    continue
                if not isinstance(thresholds, dict):
                    errors.append(f"budgets.{file_key} must be an object")
                    continue
                for threshold_key, threshold_value in thresholds.items():
                    if threshold_key not in allowed:
                        errors.append(
                            f"unknown threshold budgets.{file_key}.{threshold_key}"
                        )
                    elif not is_strict_int(threshold_value) or threshold_value <= 0:
                        errors.append(
                            f"budgets.{file_key}.{threshold_key} must be a positive integer"
                        )
    return errors


def normalized_storage_mode(policy: dict | None) -> str | None:
    """Collapse policy schema v1/v2 into the single tracked/local/private mode.

    All storage consumers read this, never the raw fields: v1 keeps its
    legacy task_storage (tracked/local), v2 carries the whole-layer
    storage_mode (tracked/local/private). Callers only receive validated
    policies (check_policy_block returns None otherwise).
    """
    if not isinstance(policy, dict):
        return None
    if is_strict_int(policy.get("schema_version")) and policy["schema_version"] == 2:
        mode = policy.get("storage_mode")
        return mode if isinstance(mode, str) else None
    storage = policy.get("task_storage")
    return storage if isinstance(storage, str) else None


def read_regular_text(path: Path) -> tuple[str | None, str | None]:
    """Read a file without following symlinks; (None, None) means missing."""
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return None, None
    except OSError as exc:
        return None, f"unreadable: {exc}"
    if stat.S_ISLNK(metadata.st_mode):
        return None, "symlink"
    if not stat.S_ISREG(metadata.st_mode):
        return None, "not a regular file"
    try:
        return path.read_text(encoding="utf-8"), None
    except (OSError, UnicodeError) as exc:
        return None, f"unreadable: {exc}"


def markdown_section_lines(text: str, title: str) -> list[str]:
    """Return the body lines of a `## <title>` section, stopping at the next heading."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == f"## {title}":
            body: list[str] = []
            for candidate in lines[index + 1 :]:
                if candidate.startswith("## "):
                    break
                body.append(candidate)
            return body
    return []


def parse_runtime_focus(runtime_text: str) -> list[str]:
    """Return valid TASK ids from runtime's navigation-only Focus section."""
    focus: list[str] = []
    for line in markdown_section_lines(runtime_text, "Focus"):
        stripped = line.strip()
        if stripped.startswith("- "):
            candidate = stripped[2:].strip()
            if TASK_ID_RE.match(candidate):
                focus.append(candidate)
    return focus


def count_recent_entries(runtime_text: str) -> int:
    return sum(
        1
        for line in markdown_section_lines(runtime_text, "Recent Changes")
        if re.match(r"^\s*-\s+", line)
    )


def count_handoff_entries(handoff_text: str) -> int:
    return sum(1 for line in handoff_text.splitlines() if re.match(r"^##\s+(TASK-|SESSION)", line))


def count_decision_records(decisions_text: str) -> int:
    total = 0
    for line in decisions_text.splitlines():
        if re.match(r"^\s*-\s*D-[0-9]", line) or re.match(r"^##\s*[0-9]{4}-[0-9]{2}-[0-9]{2}", line):
            total += 1
    return total


def count_parked_entries(parked_text: str) -> int:
    return sum(1 for line in parked_text.splitlines() if re.match(r"^\s*-\s*P-[0-9]", line))


def git_run(target: Path, arguments: list[str], input_bytes: bytes | None = None) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(
            ["git", *arguments],
            cwd=target,
            input=input_bytes,
            capture_output=True,
            check=False,
        )
    except OSError:
        return None


def git_in_worktree(target: Path) -> bool:
    """True when the target sits inside a usable Git worktree."""
    result = git_run(target, ["rev-parse", "--show-toplevel"])
    return result is not None and result.returncode == 0


def git_tracked_files(target: Path) -> set[str] | None:
    result = git_run(target, ["ls-files", "-z", "--", "."])
    if result is None or result.returncode != 0:
        return None
    return {
        name.decode("utf-8", "surrogateescape")
        for name in result.stdout.split(b"\0")
        if name
    }


def git_ignored_files(target: Path, relatives: list[str]) -> set[str] | None:
    if not relatives:
        return set()
    input_bytes = b"".join(
        relative.encode("utf-8", "surrogateescape") + b"\0" for relative in relatives
    )
    result = git_run(target, ["check-ignore", "-z", "--stdin", "--"], input_bytes=input_bytes)
    if result is None or result.returncode not in (0, 1):
        return None
    return {
        name.decode("utf-8", "surrogateescape")
        for name in result.stdout.split(b"\0")
        if name
    }


def git_ignored_rules(target: Path, relatives: list[str]) -> dict[str, tuple[str, str]] | None:
    """Map each Git-ignored relative path to its (source, pattern); None on failure.

    `--no-index` gives pure rule semantics so the answer does not depend on
    what happens to be staged right now.
    """
    if not relatives:
        return {}
    input_bytes = b"".join(
        relative.encode("utf-8", "surrogateescape") + b"\0" for relative in relatives
    )
    result = git_run(
        target, ["check-ignore", "-z", "-v", "--no-index", "--stdin", "--"], input_bytes=input_bytes
    )
    if result is None or result.returncode not in (0, 1):
        return None
    fields = [name.decode("utf-8", "surrogateescape") for name in result.stdout.split(b"\0")]
    if fields and fields[-1] == "":
        fields.pop()
    rules: dict[str, tuple[str, str]] = {}
    for index in range(0, len(fields) - 3, 4):
        source, _line, pattern, pathname = fields[index : index + 4]
        # With -v git also reports negated matches ("!pattern") for paths the
        # rules explicitly un-ignore; those paths are NOT ignored.
        if pattern.startswith("!"):
            continue
        rules[pathname] = (source, pattern)
    return rules


class AdoptionCoreState:
    def __init__(self, stamp: dict | None, paths: set[str] | None, error: str | None) -> None:
        self.stamp = stamp
        self.paths = paths
        self.error = error


def stamp_core_paths(stamp: dict) -> tuple[set[str] | None, str | None]:
    """Validate the durability-facing stamp schema and derive its core paths."""
    schema_version = stamp.get("schema_version")
    if type(schema_version) is not int or schema_version not in (1, 2):
        return None, "schema_version must be the integer 1 or 2"
    version = stamp.get("protocol_version")
    if not isinstance(version, str) or not version.strip():
        return None, "protocol_version must be a non-empty string"
    files = stamp.get("files")
    if not isinstance(files, dict) or not files:
        return None, "files must be a non-empty object"
    try:
        validate_stamp_file_paths(stamp)
    except AdoptionError as exc:
        return None, str(exc)
    paths: set[str] = {STAMP_RELATIVE}
    for relative, entry in files.items():
        try:
            validate_managed_relative(relative)
        except AdoptionError as exc:
            return None, f"files contains an {exc}"
        if not isinstance(entry, dict):
            return None, f"files[{relative!r}] must be an object"
        paths.add(relative)
    return paths, None


def adoption_core_paths(target: Path) -> AdoptionCoreState:
    """Read the installed stamp without conflating absence with corruption."""
    try:
        stamp = read_stamp(target)
    except (AdoptionError, UnicodeError) as exc:
        return AdoptionCoreState(None, None, str(exc))
    if stamp is None:
        return AdoptionCoreState(None, None, None)
    paths, error = stamp_core_paths(stamp)
    return AdoptionCoreState(stamp, paths, error)


def git_head_files(target: Path) -> tuple[set[str], str | None]:
    """Names committed in HEAD (repo-root relative) plus an operational error."""
    probe = git_run(target, ["rev-parse", "--verify", "HEAD"])
    if probe is None:
        return set(), "git is unavailable"
    if probe.returncode != 0:
        # A repository without any commit: nothing is durable yet.
        return set(), None
    result = git_run(target, ["ls-tree", "-r", "-z", "--name-only", "--full-name", "HEAD"])
    if result is None or result.returncode != 0:
        return set(), "git ls-tree failed"
    return (
        {name.decode("utf-8", "surrogateescape") for name in result.stdout.split(b"\0") if name},
        None,
    )


def git_root_prefix(target: Path) -> str:
    """Target prefix inside its Git root ('' when the target is the root)."""
    result = git_run(target, ["rev-parse", "--show-toplevel"])
    if result is None or result.returncode != 0:
        return ""
    try:
        root = Path(result.stdout.decode("utf-8", "surrogateescape").strip())
        relative = os.path.relpath(target.resolve(), root.resolve())
    except (OSError, ValueError):
        return ""
    if relative == ".":
        return ""
    return Path(relative).as_posix() + "/"


def head_blob_text(target: Path, anchored: str) -> str | None:
    result = git_run(target, ["cat-file", "blob", f"HEAD:{anchored}"])
    if result is None or result.returncode != 0:
        return None
    return result.stdout.decode("utf-8", "surrogateescape")


def check_core_storage(run: VaultCheckRun, state: AdoptionCoreState) -> None:
    """Mechanical durability gate: the adoption core must be present in Git HEAD.

    HEAD facts are the cheap equivalent of fresh-clone visibility; the checker
    stays read-only and never runs git add/commit/clone itself.
    """
    if state.error is not None:
        run.add(
            "storage",
            "CORE_STORAGE_INVALID",
            "error",
            STAMP_RELATIVE,
            f"the adoption stamp exists but is invalid: {state.error}; durability cannot be verified",
        )
        return
    core = state.paths
    if core is None:
        return  # not an adopted installation; nothing to verify
    worktree = git_run(run.target, ["rev-parse", "--show-toplevel"])
    if worktree is None:
        run.add(
            "storage",
            "CORE_STORAGE_UNVERIFIED",
            "error",
            STAMP_RELATIVE,
            "git rev-parse could not be executed; adoption durability was not verified",
        )
        return
    if worktree.returncode != 0:
        run.add(
            "storage",
            "CORE_STORAGE_UNVERIFIED",
            "warning",
            STAMP_RELATIVE,
            "not a Git worktree or Git is unavailable; adoption durability was not verified and generated files are not durable on their own",
        )
        return
    head, error = git_head_files(run.target)
    if error is not None:
        run.add(
            "storage",
            "CORE_STORAGE_UNVERIFIED",
            "error",
            STAMP_RELATIVE,
            f"{error}; adoption durability was not verified",
        )
        return
    prefix = git_root_prefix(run.target)
    rules = git_ignored_rules(run.target, sorted(core))
    if rules is None:
        run.add(
            "storage",
            "CORE_STORAGE_UNVERIFIED",
            "error",
            STAMP_RELATIVE,
            "git check-ignore failed; adoption durability was not verified",
        )
        return
    head_stamp_blob = head_blob_text(run.target, prefix + STAMP_RELATIVE)
    head_stamp = None
    if head_stamp_blob is not None:
        try:
            head_stamp = json.loads(head_stamp_blob)
        except ValueError:
            head_stamp = None
    head_paths = None
    head_error = None
    if isinstance(head_stamp, dict):
        head_paths, head_error = stamp_core_paths(head_stamp)
    head_files = head_stamp.get("files") if isinstance(head_stamp, dict) else None
    head_agents_entry = head_files.get("AGENTS.md", {}) if isinstance(head_files, dict) else {}
    for relative in sorted(core):
        rule = rules.get(relative)
        if rule is not None:
            source, pattern = rule
            run.add(
                "storage",
                "CORE_STORAGE_IGNORED",
                "error",
                relative,
                f"{relative} is excluded by Git ignore rule {pattern} ({source}); a fresh clone would not contain it",
            )
            continue
        anchored = prefix + relative
        if anchored not in head:
            run.add(
                "storage",
                "CORE_STORAGE_UNCOMMITTED",
                "error",
                relative,
                f"{relative} is not committed to Git HEAD; a fresh clone would lose it (commit the collaboration core)",
            )
            continue
        blob = head_blob_text(run.target, anchored)
        if (
            relative == "AGENTS.md"
            and isinstance(head_agents_entry, dict)
            and head_agents_entry.get("role") == "marker"
            and (blob is None or strict_marker_region(blob) is None)
        ):
            run.add(
                "storage",
                "CORE_STORAGE_UNCOMMITTED",
                "error",
                relative,
                "AGENTS.md in Git HEAD lacks one complete, unique, well-formed managed Trellium section; a fresh clone would not receive the routed entry",
            )
        elif relative == STAMP_RELATIVE:
            if not isinstance(head_stamp, dict) or head_error is not None:
                run.add(
                    "storage",
                    "CORE_STORAGE_UNCOMMITTED",
                    "error",
                    relative,
                    "vault/.agent-init.json in Git HEAD is not a readable adoption stamp; a fresh clone would not be recognized as adopted",
                )
            elif (
                state.stamp is not None
                and (
                    head_stamp.get("protocol_version") != state.stamp.get("protocol_version")
                    or head_paths != core
                )
            ):
                run.add(
                    "storage",
                    "CORE_STORAGE_UNCOMMITTED",
                    "error",
                    relative,
                    "vault/.agent-init.json in Git HEAD does not match the installed protocol_version and managed core file set; commit the current complete stamp",
                )


LOCAL_PRIVATE_SENTINELS = (
    "vault/tasks/TASK-0000-sentinel.md",
    "vault/tasks/TASK-0000-sentinel-review.md",
    "vault/tasks/archive/TASK-0000-sentinel.md",
)
LOCAL_DURABLE_SENTINELS = (
    "vault/tasks/README.md",
    "vault/decisions.md",
    "vault/decisions/D-0000-sentinel.md",
    "vault/details/sentinel.md",
)


def check_local_boundary(
    run: VaultCheckRun, policy: dict | None, state: AdoptionCoreState
) -> None:
    """Local storage boundary: future TASKs stay private, durable namespaces public.

    Sentinel paths are queried through `git check-ignore --no-index`; nothing
    is written and no `.gitignore` is ever modified by the checker.
    """
    if policy is None or normalized_storage_mode(policy) != "local":
        return
    if not git_in_worktree(run.target):
        return  # CORE_STORAGE_UNVERIFIED already reports non-Git targets
    core = state.paths
    durable = [
        relative
        for relative in LOCAL_DURABLE_SENTINELS
        if core is None or relative not in core  # stamp-managed paths are judged above
    ]
    rules = git_ignored_rules(run.target, [*LOCAL_PRIVATE_SENTINELS, *durable])
    if rules is None:
        run.add(
            "storage",
            "LOCAL_BOUNDARY_UNVERIFIED",
            "error",
            "vault/tasks",
            "git check-ignore failed; the task_storage=local Git boundary was not verified",
        )
        return
    uncovered = [relative for relative in LOCAL_PRIVATE_SENTINELS if relative not in rules]
    if uncovered:
        run.add(
            "storage",
            "LOCAL_BOUNDARY_UNCONFIGURED",
            "warning",
            "vault/tasks",
            "task_storage=local but future local TASK files are not covered by ignore rules: "
            + ", ".join(uncovered)
            + "; add narrow rules (vault/tasks/TASK-*.md, vault/tasks/*-review.md, vault/tasks/archive/) so private journals never enter Git",
        )
    for relative in durable:
        rule = rules.get(relative)
        if rule is not None:
            source, pattern = rule
            run.add(
                "storage",
                "LOCAL_BOUNDARY_OVERREACH",
                "error",
                relative,
                f"{relative} durable namespace is captured by Git ignore rule {pattern} ({source}); narrow local rules to TASK journals, review ledgers, and vault/tasks/archive/, and keep decisions/details/tasks README tracked",
            )


PRIVATE_BASE_MANAGED_PATHS = ("AGENTS.md", "vault/", "skills/agent-task/", ".agent-init-backup/")


def private_managed_extras(state: AdoptionCoreState) -> list[str]:
    """Stamp-managed paths outside the four base private namespaces."""
    if state.paths is None:
        return []
    return sorted(
        relative
        for relative in state.paths
        if relative != STAMP_RELATIVE
        and relative != "AGENTS.md"
        and not relative.startswith(("vault/", "skills/agent-task/", ".agent-init-backup/"))
    )


PRIVATE_PREFLIGHT_BASE_CANDIDATES = (
    "AGENTS.md",
    "skills/agent-task/SKILL.md",
    "vault/.agent-init.json",
    "vault/collaboration.md",
    "vault/decisions.md",
    "vault/governance.md",
    "vault/handoff.md",
    "vault/index.md",
    "vault/parked.md",
    "vault/project.md",
    "vault/runtime.md",
    "vault/tasks/README.md",
)


def private_preflight_candidates(profiles: tuple[str, ...]) -> list[str]:
    """Candidate managed paths a private adoption would create or require."""
    known = set(PROFILE_IDS)
    candidates: set[str] = set(PRIVATE_PREFLIGHT_BASE_CANDIDATES)
    candidates.add(PROFILE_RULES_RELATIVE)
    for profile_id in profiles:
        if profile_id not in known:
            raise AdoptionError(f"unknown profile id for private preflight: {profile_id}")
        candidates.add(f"{PROFILE_DOCUMENT_DIRECTORY}/{profile_id}.md")
    return sorted(candidates)


def private_preflight(target: Path, profiles: tuple[str, ...] = ()) -> list[str]:
    """Agent-native read-only probe that runs BEFORE adopt in private mode.

    Every candidate managed path must be free of Git index/HEAD collisions;
    any collision raises, and any Git query failure fails closed. The probe
    never mutates the worktree, index, HEAD, or the exclude file.
    """
    target = Path(target)
    candidates = private_preflight_candidates(profiles)
    probe = git_run(target, ["rev-parse", "--show-toplevel"])
    if probe is None:
        raise AdoptionError(
            "private preflight failed closed: git is unavailable; the private boundary cannot be verified"
        )
    if probe.returncode != 0:
        if b"not a git repository" in probe.stderr:
            return []
        raise AdoptionError(
            "private preflight failed closed: git rev-parse failed: "
            + probe.stderr.decode("utf-8", "surrogateescape").strip()
        )
    prefix = git_root_prefix(target)
    namespaces = ("vault/", "skills/agent-task/", ".agent-init-backup/")
    candidate_set = set(candidates) | {"AGENTS.md"}

    def collides(repo_relative: str) -> bool:
        if prefix:
            if not repo_relative.startswith(prefix):
                return False
            repo_relative = repo_relative[len(prefix) :]
        return (
            repo_relative in candidate_set
            or repo_relative.startswith(namespaces)
        )

    tracked = git_tracked_files(target)
    if tracked is None:
        raise AdoptionError(
            "private preflight failed closed: git ls-files failed; the private boundary cannot be verified"
        )
    # git ls-files reports paths relative to the cwd (the target) while
    # ls-tree --full-name reports repo-root-relative paths; normalize both to
    # repo-relative so the namespace/candidate matching sees one coordinate.
    tracked = {prefix + name for name in tracked}
    head, head_error = git_head_files(target)
    if head_error is not None:
        raise AdoptionError(
            f"private preflight failed closed: {head_error}; the private boundary cannot be verified"
        )
    collisions = sorted({r for r in (*tracked, *head) if collides(r)})
    if collisions:
        raise AdoptionError(
            "private adoption rejected: "
            + ", ".join(collisions)
            + " are already tracked in Git; private managed material never enters Git."
            " Choose local storage instead, or remove the paths from the Git index and HEAD"
            " as the project owner decides, then re-run the preflight"
        )
    return []


# --- Project identity (local historical retention onboarding) ----------------


def project_identity_path(target: Path) -> Path:
    """Target-relative path of the one canonical project-identity owner."""
    return target / PROJECT_IDENTITY_RELATIVE


def read_project_identity(target: Path, target_descriptor: int | None = None) -> str | None:
    """Return the canonical project UUID, or None when no identity file exists.

    Unsafe paths, non-regular files, and content that is not exactly one
    canonical lowercase UUID line followed by a newline fail closed; identity
    is never rewritten or normalized in place.
    """
    metadata = managed_file_metadata(target, PROJECT_IDENTITY_RELATIVE)
    if metadata is None:
        return None
    text = read_managed_text(target, PROJECT_IDENTITY_RELATIVE, target_descriptor)
    if text is None:
        return None
    body = text[:-1] if text.endswith("\n") else None
    if not body or "\n" in body or body != body.strip():
        raise AdoptionError(
            f"{PROJECT_IDENTITY_RELATIVE} must hold exactly one UUID line and a final newline; "
            "refusing to rewrite identity"
        )
    try:
        parsed = uuid.UUID(body)
    except ValueError as exc:
        raise AdoptionError(
            f"{PROJECT_IDENTITY_RELATIVE} is not a valid UUID; refusing to rewrite identity"
        ) from exc
    canonical = str(parsed)
    if canonical != body:
        raise AdoptionError(
            f"{PROJECT_IDENTITY_RELATIVE} must hold the canonical lowercase UUID form ({canonical}); "
            "refusing to rewrite identity"
        )
    return canonical


def _git_root_prefix_strict(target: Path) -> str | None:
    """Repo-root-relative prefix of the target, or None when Git cannot say."""
    result = git_run(target, ["rev-parse", "--show-toplevel"])
    if result is None or result.returncode != 0:
        return None
    try:
        root = Path(result.stdout.decode("utf-8", "surrogateescape").strip())
        relative = os.path.relpath(target.resolve(), root.resolve())
    except (OSError, ValueError):
        return None
    if relative == ".":
        return ""
    return Path(relative).as_posix() + "/"


def _proven_without_git_metadata(target: Path) -> bool | None:
    """True only when target provably has no .git entry on the ancestor chain.

    Git reports "not a git repository" both for a plain directory and for a
    directory whose .git metadata is corrupt, so stderr alone cannot separate
    "never was a repository" from "damaged repository". Only a query that
    definitively succeeds counts as evidence: an existing entry (directory,
    pointer file, or symlink) means damaged existing metadata, and any query
    failure (unreadable ancestor, unresolvable symlink, non-directory
    component) stays unknown instead of reading as absence. Only a confirmed
    FileNotFoundError on every ancestor proves there is no repository.
    """
    try:
        current = target.resolve()
    except OSError:
        return None
    while True:
        try:
            os.lstat(current / ".git")
        except OSError as error:
            if not isinstance(error, FileNotFoundError):
                return None  # the query itself failed; absence is not proven
            # FileNotFoundError: proven absent at this level; keep probing upward.
        else:
            return False  # an existing entry: damaged or not, metadata is there
        if current == current.parent:
            return True
        current = current.parent


def _identity_in_head(target: Path) -> bool | None:
    """Whether Git HEAD records the identity path, or None when Git cannot say.

    Only a plain non-repository target (no .git entry on the ancestor chain)
    and a repository whose zero-revision state Git itself confirms provably
    have no HEAD evidence layer. Git being absent or unexecutable, existing
    but corrupt or unreadable Git metadata (including a damaged .git/HEAD,
    which Git reports as "not a git repository"), an unresolvable HEAD whose
    repository still holds revisions, and any operational query failure
    inside an existing repository (including the monorepo prefix lookup),
    return None: unknown evidence fails closed and must never be read as
    "unbound".
    """
    probe = git_run(target, ["rev-parse", "--verify", "HEAD"])
    if probe is None:
        return None
    if probe.returncode != 0:
        stderr = probe.stderr.decode("utf-8", "surrogateescape")
        if "not a git repository" in stderr:
            # The same error text covers a never-initialized directory, an
            # existing repository with damaged metadata, and unqueryable
            # ancestors; only a structurally proven absence may read as
            # unbound, everything else stays unknown.
            if not _proven_without_git_metadata(target):
                return None
            return False
        # An unresolvable HEAD is ambiguous: an unborn branch, a corrupt ref,
        # and a damaged object database all fail here with overlapping error
        # text. Only Git confirming that no revision exists counts as evidence
        # that no HEAD binding layer can exist; every other outcome stays
        # unknown and fails closed.
        revisions = git_run(target, ["rev-list", "-n", "1", "--all"])
        if revisions is None or revisions.returncode != 0 or revisions.stdout.strip():
            return None
        return False
    prefix = _git_root_prefix_strict(target)
    if prefix is None:
        return None
    result = git_run(target, ["cat-file", "blob", f"HEAD:{prefix}{PROJECT_IDENTITY_RELATIVE}"])
    if result is None:
        return None
    if result.returncode == 0:
        return True
    stderr = result.stderr.decode("utf-8", "surrogateescape")
    if "does not exist" in stderr or "Not a valid object name" in stderr:
        return False
    return None


def identity_binding_evidence(target: Path) -> bool:
    """True when the stamp inventory or Git HEAD already records the identity path."""
    stamp = read_stamp(target)
    files = stamp.get("files") if isinstance(stamp, dict) else None
    if isinstance(files, dict) and PROJECT_IDENTITY_RELATIVE in files:
        return True
    recorded = _identity_in_head(target)
    if recorded is None:
        raise AdoptionError(
            "git could not verify whether a project identity was bound before; "
            "resolve Git verification and retry instead of generating an identity"
        )
    return recorded


def _require_local_policy_for_identity(target: Path) -> dict:
    """Return the policy only under an explicit, valid local storage mode.

    Parsing mirrors the canonical checker exactly (unique block,
    ``parse_block_object`` strictness, ``validate_policy_object``): duplicate
    keys, multiple or unterminated blocks, non-object content, and invalid
    values are all refused — the helper must not accept a policy the checker
    rejects, and an invalid policy never reaches the write path.
    """
    text, error = read_regular_text(target / "vault/index.md")
    if text is None:
        raise AdoptionError(
            f"cannot read the project policy ({error}); identity onboarding requires an explicit local storage policy"
        )
    blocks, extract_error = extract_comment_blocks(text, POLICY_MARKER)
    if extract_error is not None:
        raise AdoptionError(
            f"invalid project policy ({extract_error}); identity onboarding requires an explicit valid local policy"
        )
    if len(blocks) != 1:
        raise AdoptionError(
            f"expected exactly one {POLICY_MARKER} block, found {len(blocks)}; "
            "identity onboarding requires an explicit valid local policy"
        )
    policy, parse_error = parse_block_object(blocks[0])
    if policy is None:
        raise AdoptionError(
            f"invalid project policy ({parse_error}); identity onboarding requires an explicit valid local policy"
        )
    validation_errors = validate_policy_object(policy)
    if validation_errors:
        raise AdoptionError(
            "invalid project policy (" + "; ".join(validation_errors) + "); "
            "identity onboarding requires an explicit valid local policy"
        )
    if normalized_storage_mode(policy) != "local":
        raise AdoptionError(
            "identity onboarding runs only under an explicit local storage policy; "
            "tracked and private projects never bind a historical store"
        )
    return policy


def register_project_identity(
    target: Path, *, created: bool, target_descriptor: int | None = None
) -> bool:
    """Register the identity path in the stamp inventory using the existing schema.

    The entry is a plain ``{"role": "data", "baseline": <sha256>}`` record: no
    new fields, no copy of the UUID value. Existing registrations are kept;
    returns False in that case. A registration after an out-of-band identity
    file is marked observed, so it stays an evidence record, never a claim of
    authorship.
    """
    stamp = read_stamp(target, target_descriptor)
    if stamp is None:
        raise AdoptionError("no adoption stamp found; identity onboarding requires an adopted installation")
    files = stamp["files"]
    entry = files.get(PROJECT_IDENTITY_RELATIVE)
    if isinstance(entry, dict) and entry.get("role") == "data":
        return False
    baseline = local_hash_for_role(target, PROJECT_IDENTITY_RELATIVE, "data", target_descriptor)
    if baseline is None:
        raise AdoptionError(
            "the project identity disappeared before registration; retry to reuse the existing file - never generate a replacement"
        )
    registered: dict[str, str | bool] = {"role": "data", "baseline": baseline}
    if not created:
        registered["observed"] = True
    files[PROJECT_IDENTITY_RELATIVE] = registered
    validate_stamp_file_paths(stamp)
    write_stamp_file(target, stamp, target_descriptor)
    return True


def ensure_project_identity(
    target: Path,
    *,
    authorize_create: bool = False,
    target_descriptor: int | None = None,
) -> dict:
    """Bundled identity helper: read, validate, recover-gate, or create and register.

    Agent-native first local retention onboarding calls this after adopt and
    the local policy/narrow-ignore setup, before check. Under an explicit
    local policy it reuses a valid ``vault/project-id`` and completes its
    stamp registration; a bound-but-missing identity must be restored, never
    regenerated - even an authorized first binding cannot bypass that gate;
    creating one requires ``authorize_create`` and leaves the identity file
    in place if the inventory write fails, so a retry re-registers the same
    UUID. Returns ``{"identity", "created", "registered"}``; every refusal
    raises AdoptionError and leaves the project untouched. Upgrades and
    repeat adopts preserve the registration; tracked and private projects
    never reach identity creation at all.
    """
    target = Path(target).resolve()
    _require_local_policy_for_identity(target)
    identity = read_project_identity(target, target_descriptor)
    created = False
    if identity is None:
        if identity_binding_evidence(target):
            raise AdoptionError(
                f"{PROJECT_IDENTITY_RELATIVE} is missing but a prior binding is recorded "
                "(stamp inventory or Git HEAD); restore the original identity file - do not generate a replacement"
            )
        if not authorize_create:
            raise AdoptionError(
                f"{PROJECT_IDENTITY_RELATIVE} does not exist and no prior binding is recorded; "
                "first binding needs explicit authorization (fresh adoption plan or owner-confirmed enablement)"
            )
        write_text_file(
            project_identity_path(target),
            f"{uuid.uuid4()}\n",
            target,
            force=False,
            dry_run=False,
            target_descriptor=target_descriptor,
        )
        identity = read_project_identity(target, target_descriptor)
        if identity is None:
            raise AdoptionError(
                "the identity file vanished during creation; onboarding is incomplete - retry re-checks binding evidence"
            )
        created = True
    try:
        registered = register_project_identity(target, created=created, target_descriptor=target_descriptor)
    except OSError as exc:
        raise AdoptionError(
            f"the identity file was kept but stamp registration failed ({exc}); "
            "onboarding is incomplete - retry re-registers the same identity"
        ) from exc
    return {"identity": identity, "created": created, "registered": registered}


def parse_private_exclude_blocks(text: str) -> tuple[list[dict], list[str]]:
    """Parse canonical trellium-private blocks; (blocks, structural errors)."""
    blocks: list[dict] = []
    errors: list[str] = []
    current: dict | None = None
    for raw in text.splitlines():
        line = raw.strip()
        match = re.match(r"^# trellium-private:(start|end)\s*(.*)$", line)
        if "trellium-private:" in line and match is None:
            errors.append(f"malformed trellium-private marker: {line}")
            continue
        if match is None:
            if current is not None and line and not line.startswith("#"):
                current["patterns"].append(line)
            continue
        kind, marker_identity = match.group(1), match.group(2).strip()
        if kind == "start":
            if current is not None:
                errors.append(f"unclosed trellium-private block for {current['identity']!r} before a new start marker")
            current = {"identity": marker_identity, "patterns": []}
        elif current is None:
            errors.append(f"trellium-private end marker without a start marker (identity {marker_identity!r})")
        elif current["identity"] != marker_identity:
            errors.append(f"trellium-private end marker identity {marker_identity!r} does not match its start marker {current['identity']!r}")
            current = None
        else:
            blocks.append(current)
            current = None
    if current is not None:
        errors.append(f"unterminated trellium-private block for {current['identity']!r}")
    return blocks, errors


def check_private_boundary(run: VaultCheckRun, policy: dict | None, state: AdoptionCoreState) -> None:
    """Reverse privacy gate for storage_mode=private.

    Replaces the positive HEAD-durability gate: managed material must stay
    out of HEAD and the index, and the canonical .git/info/exclude block
    must carry exactly one well-formed block per target whose anchored
    patterns cover the approved scope and nothing else. Read-only Git
    queries only; any verification failure fails closed.
    """
    if state.error is not None:
        run.add(
            "storage",
            "CORE_STORAGE_INVALID",
            "error",
            STAMP_RELATIVE,
            f"the adoption stamp exists but is invalid: {state.error}; the private boundary cannot be verified",
        )
        return
    if not git_in_worktree(run.target):
        run.add(
            "storage",
            "PRIVATE_STORAGE_UNVERIFIED",
            "warning",
            STAMP_RELATIVE,
            "not a Git worktree or Git is unavailable; there is no Git upload surface, but the private boundary was not verified",
        )
        return
    if state.stamp is None:
        run.add(
            "storage",
            "PRIVATE_STORAGE_UNVERIFIED",
            "error",
            STAMP_RELATIVE,
            "storage_mode=private requires the adoption stamp, but vault/.agent-init.json is missing; the managed-file inventory cannot be read and the private boundary cannot be verified",
        )
        return
    prefix = git_root_prefix(run.target)
    target_identity = prefix.rstrip("/") if prefix else "."
    extras = private_managed_extras(state)
    base = [f"/{prefix}{entry}" for entry in PRIVATE_BASE_MANAGED_PATHS]
    expected = base + [f"/{prefix}{entry}" for entry in extras]
    missing_copies = []
    for relative in extras:
        candidate = run.target / relative
        try:
            metadata = candidate.lstat()
        except OSError:
            missing_copies.append(relative)
            continue
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
            missing_copies.append(relative)
    if missing_copies:
        run.add(
            "storage",
            "PRIVATE_STORAGE_UNVERIFIED",
            "error",
            STAMP_RELATIVE,
            "private managed material has no Git copy to recover; declared managed copies are missing or not regular files: "
            + ", ".join(missing_copies)
            + "; restore them before the private boundary can be verified",
        )
        return

    exclude_result = git_run(run.target, ["rev-parse", "--git-path", "info/exclude"])
    if exclude_result is None or exclude_result.returncode != 0:
        run.add(
            "storage",
            "PRIVATE_STORAGE_UNVERIFIED",
            "error",
            STAMP_RELATIVE,
            "git rev-parse could not locate the Git exclude file; the private boundary was not verified",
        )
        return
    exclude_value = Path(exclude_result.stdout.decode("utf-8", "surrogateescape").strip())
    exclude_path = exclude_value if exclude_value.is_absolute() else (run.target / exclude_value)
    try:
        exclude_text = exclude_path.read_text(encoding="utf-8", errors="surrogateescape")
    except FileNotFoundError:
        exclude_text = ""
    except (OSError, UnicodeError) as exc:
        run.add(
            "storage",
            "PRIVATE_STORAGE_UNVERIFIED",
            "error",
            STAMP_RELATIVE,
            f"could not read the Git exclude file: {exc}; the private boundary was not verified",
        )
        return

    blocks, parse_errors = parse_private_exclude_blocks(exclude_text)
    for parse_error in parse_errors:
        run.add(
            "storage",
            "PRIVATE_STORAGE_UNCONFIGURED",
            "error",
            "vault",
            f"the canonical private exclude block is unusable: {parse_error}; keep exactly one complete block per target in .git/info/exclude",
        )
    own = [block for block in blocks if block["identity"] == target_identity]
    if len(own) > 1:
        run.add(
            "storage",
            "PRIVATE_STORAGE_UNCONFIGURED",
            "error",
            "vault",
            f"{len(own)} canonical private blocks claim target identity {target_identity!r}; keep exactly one complete block per target",
        )
        own = []
    if not own:
        if not parse_errors:
            run.add(
                "storage",
                "PRIVATE_STORAGE_UNCONFIGURED",
                "error",
                "vault",
                f"no canonical trellium-private block for target identity {target_identity!r} in the Git exclude file; write one complete block (start/end markers carrying this identity, one anchored pattern per managed path: {' '.join(expected)})",
            )
    else:
        patterns = own[0]["patterns"]
        non_anchored = [entry for entry in patterns if not entry.startswith("/")]
        overreach = [entry for entry in patterns if entry.startswith("/") and entry not in expected]
        if non_anchored:
            run.add(
                "storage",
                "PRIVATE_STORAGE_OVERREACH",
                "error",
                "vault",
                "private exclude patterns must be anchored (start with '/') so the boundary cannot reach beyond the target: " + ", ".join(non_anchored),
            )
        if overreach:
            run.add(
                "storage",
                "PRIVATE_STORAGE_OVERREACH",
                "error",
                "vault",
                "private exclude block covers paths outside the approved managed scope (expected exactly: " + " ".join(expected) + "): " + ", ".join(overreach),
            )
        missing = [entry for entry in expected if entry not in patterns]
        if missing and not non_anchored and not overreach:
            run.add(
                "storage",
                "PRIVATE_STORAGE_UNCONFIGURED",
                "error",
                "vault",
                "the canonical private block does not cover the required managed scope; missing anchored patterns: " + ", ".join(missing),
            )
        if not parse_errors and not non_anchored and not overreach and not missing:
            check_relatives = (*PRIVATE_BASE_MANAGED_PATHS, *extras)
            ignored = git_ignored_files(run.target, list(check_relatives))
            if ignored is None:
                run.add(
                    "storage",
                    "PRIVATE_STORAGE_UNVERIFIED",
                    "error",
                    STAMP_RELATIVE,
                    "git check-ignore failed; the private boundary was not verified",
                )
            else:
                for relative in check_relatives:
                    if relative not in ignored:
                        run.add(
                            "storage",
                            "PRIVATE_STORAGE_UNCONFIGURED",
                            "error",
                            "vault",
                            f"/{prefix}{relative} is not actually ignored by Git (a later negation or higher-priority rule un-ignored it); fix the ignore rules so every managed path is ignored",
                        )

    index = git_tracked_files(run.target)
    if index is None:
        run.add(
            "storage",
            "PRIVATE_STORAGE_UNVERIFIED",
            "error",
            STAMP_RELATIVE,
            "git ls-files failed; the private boundary was not verified",
        )
        return
    head, head_error = git_head_files(run.target)
    if head_error is not None:
        run.add(
            "storage",
            "PRIVATE_STORAGE_UNVERIFIED",
            "error",
            STAMP_RELATIVE,
            f"{head_error}; the private boundary was not verified",
        )
        return
    extras_set = set(extras)

    def is_managed(relative: str) -> bool:
        return (
            relative == "AGENTS.md"
            or relative.startswith(("vault/", "skills/agent-task/", ".agent-init-backup/"))
            or relative in extras_set
        )

    head_hits: set[str] = set()
    for name in head:
        if prefix and not name.startswith(prefix):
            continue
        relative = name[len(prefix) :] if prefix else name
        if is_managed(relative):
            head_hits.add(relative)
    index_hits = {relative for relative in index if is_managed(relative)}
    for relative in sorted(head_hits | index_hits):
        where = []
        if relative in head_hits:
            where.append("Git HEAD")
        if relative in index_hits:
            where.append("the Git index (tracked or staged)")
        run.add(
            "storage",
            "PRIVATE_STORAGE_TRACKED",
            "error",
            relative,
            f"{relative} is private managed material but is present in {' and '.join(where)}; private material never enters Git; remove it from the index as the project owner decided",
        )


class VaultCheckRun:
    """Accumulates findings and measurements for one read-only check run."""

    def __init__(self, target: Path) -> None:
        self.target = target
        self.findings: list[tuple[int, dict, str]] = []
        self.measurements: dict = {}

    def add(self, phase: str, code: str, severity: str, path: str, message: str, task_id: str | None = None) -> None:
        finding = {"code": code, "severity": severity, "path": path, "message": message}
        if task_id is not None:
            finding["task_id"] = task_id
        self.findings.append((FINDING_PHASES.index(phase), finding, path))

    def sorted_findings(self) -> list[dict]:
        ordered = sorted(self.findings, key=lambda item: (item[0], item[2], item[1]["code"], item[1]["message"]))
        return [finding for _phase, finding, _path in ordered]

    def findings_with_phase(self) -> list[tuple[str, dict]]:
        """Findings in report order, paired with their check phase name."""
        ordered = sorted(self.findings, key=lambda item: (item[0], item[2], item[1]["code"], item[1]["message"]))
        return [(FINDING_PHASES[phase], finding) for phase, finding, _path in ordered]

    @property
    def errors(self) -> list[dict]:
        return [finding for finding in self.sorted_findings() if finding["severity"] == "error"]

    @property
    def warnings(self) -> list[dict]:
        return [finding for finding in self.sorted_findings() if finding["severity"] == "warning"]


def check_required_files(run: VaultCheckRun) -> dict[str, str]:
    """Read the fixed vault files; report missing/symlinked inputs."""
    texts: dict[str, str] = {}
    vault = run.target / "vault"
    tasks_dir = vault / "tasks"
    try:
        tasks_metadata = tasks_dir.lstat()
    except FileNotFoundError:
        run.add("required-files", "REQUIRED_FILE_MISSING", "warning", "vault/tasks", "required vault directory is missing: vault/tasks/")
    else:
        if stat.S_ISLNK(tasks_metadata.st_mode):
            run.add("required-files", "SYMLINK_INPUT", "error", "vault/tasks", "vault/tasks/ is a symbolic link; refusing to follow it")
        elif not stat.S_ISDIR(tasks_metadata.st_mode):
            run.add("required-files", "REQUIRED_FILE_MISSING", "warning", "vault/tasks", "vault/tasks/ is not a directory")

    for relative in REQUIRED_VAULT_FILES:
        text, error = read_regular_text(run.target / relative)
        if error == "symlink":
            run.add("required-files", "SYMLINK_INPUT", "error", relative, f"{relative} is a symbolic link; refusing to follow it")
        elif error is not None:
            run.add("required-files", "FILE_UNREADABLE", "error", relative, f"could not read {relative}: {error}")
        elif text is None:
            run.add("required-files", "REQUIRED_FILE_MISSING", "warning", relative, f"required vault file is missing: {relative}")
        else:
            texts[relative] = text
    return texts


def check_policy_block(run: VaultCheckRun, index_text: str | None) -> dict | None:
    if index_text is None:
        run.add("policy", "POLICY_MISSING", "warning", "vault/index.md", "no vault/index.md to hold a trellium-policy block; project budgets and TASK storage are unresolved (legacy)")
        return None
    blocks, error = extract_comment_blocks(index_text, POLICY_MARKER)
    if error is not None:
        run.add("policy", "POLICY_INVALID", "error", "vault/index.md", error)
        return None
    if not blocks:
        run.add("policy", "POLICY_MISSING", "warning", "vault/index.md", "no trellium-policy block in vault/index.md; project budgets and TASK storage are unresolved (legacy)")
        return None
    if len(blocks) > 1:
        run.add("policy", "POLICY_INVALID", "error", "vault/index.md", f"expected at most one {POLICY_MARKER} block, found {len(blocks)}")
        return None
    policy, error = parse_block_object(blocks[0])
    if policy is None:
        run.add("policy", "POLICY_INVALID", "error", "vault/index.md", f"invalid {POLICY_MARKER} block: {error}")
        return None
    validation_errors = validate_policy_object(policy)
    if validation_errors:
        run.add("policy", "POLICY_INVALID", "error", "vault/index.md", f"invalid {POLICY_MARKER} block: " + "; ".join(validation_errors))
        return None
    return policy


def discover_task_files(run: VaultCheckRun) -> tuple[list[dict], list[str], list[str]]:
    """Collect current task entities plus review-ledger and archive paths."""
    tasks_dir = run.target / "vault" / "tasks"
    current: list[dict] = []
    ledgers: list[str] = []
    archive: list[str] = []
    if tasks_dir.is_symlink():
        # Reported by check_required_files; never enumerate through the link.
        return current, ledgers, archive
    try:
        entries = sorted(tasks_dir.iterdir(), key=lambda path: path.name)
    except OSError as exc:
        run.add("task-state", "FILE_UNREADABLE", "error", "vault/tasks", f"could not list vault/tasks/: {exc}")
        return current, ledgers, archive

    for entry in entries:
        relative = entry.relative_to(run.target).as_posix()
        if entry.name.startswith("."):
            continue
        match = TASK_FILE_ID_RE.match(entry.name)
        if entry.is_symlink():
            run.add("task-state", "SYMLINK_INPUT", "error", relative, f"{relative} is a symbolic link; refusing to follow it")
            if REVIEW_LEDGER_RE.match(entry.name):
                ledgers.append(relative)
            elif match and entry.name.endswith(".md"):
                current.append({"path": relative, "task_id": match.group(1), "lifecycle": None, "legacy": False, "valid": False, "state": None})
            continue
        if REVIEW_LEDGER_RE.match(entry.name):
            ledgers.append(relative)
            continue
        if match is None or not entry.name.endswith(".md"):
            continue
        text, error = read_regular_text(entry)
        if error is not None or text is None:
            # (None, None): the entry vanished between listing and reading.
            if error is not None:
                run.add("task-state", "FILE_UNREADABLE", "error", relative, f"could not read {relative}: {error}")
            continue
        state, failures = parse_task_state_block(text)
        if failures is None:
            # (None, None): a legacy task file carries no state block.
            run.add(
                "task-state",
                "TASK_STATE_MISSING",
                "warning",
                relative,
                "legacy task file without a trellium-task-state block; lifecycle is unresolved",
                task_id=match.group(1),
            )
            current.append({"path": relative, "task_id": match.group(1), "lifecycle": None, "legacy": True, "valid": False, "state": None})
            continue
        if failures:
            for code, message in failures:
                run.add("task-state", code, "error", relative, message, task_id=match.group(1))
            current.append({"path": relative, "task_id": match.group(1), "lifecycle": None, "legacy": False, "valid": False, "state": None})
            continue
        if state is None:  # unreachable: (None, None) pairs with failures is None
            continue
        if state["task_id"] != match.group(1):
            run.add(
                "task-state",
                "TASK_ID_MISMATCH",
                "error",
                relative,
                f"trellium-task-state task_id {state['task_id']!r} does not match the file name prefix {match.group(1)}",
                task_id=match.group(1),
            )
            current.append({"path": relative, "task_id": match.group(1), "lifecycle": None, "legacy": False, "valid": False, "state": None})
            continue
        current.append({"path": relative, "task_id": match.group(1), "lifecycle": state["lifecycle"], "legacy": False, "valid": True, "state": state})

    archive_dir = tasks_dir / "archive"
    if archive_dir.is_symlink():
        run.add("task-state", "SYMLINK_INPUT", "error", "vault/tasks/archive", "vault/tasks/archive/ is a symbolic link; refusing to follow it")
    elif archive_dir.is_dir():
        for entry in sorted(archive_dir.iterdir(), key=lambda path: path.name):
            if not (TASK_FILE_ID_RE.match(entry.name) and entry.name.endswith(".md")):
                continue
            relative = entry.relative_to(run.target).as_posix()
            if entry.is_symlink():
                run.add("task-state", "SYMLINK_INPUT", "error", relative, f"{relative} is a symbolic link; refusing to follow it")
            archive.append(relative)

    id_counts: dict[str, int] = {}
    for task in current:
        id_counts[task["task_id"]] = id_counts.get(task["task_id"], 0) + 1
    for task in current:
        if id_counts[task["task_id"]] > 1:
            run.add(
                "task-state",
                "TASK_ID_DUPLICATE",
                "error",
                task["path"],
                f"task_id {task['task_id']} is declared by {id_counts[task['task_id']]} task files; keep exactly one current task per id",
                task_id=task["task_id"],
            )
            task["valid"] = False
    return current, ledgers, archive


def parse_task_state_block(text: str) -> tuple[dict | None, list[tuple[str, str]] | None]:
    """Return (state, []) on success, (None, None) for legacy, or (None, failures)."""
    blocks, error = extract_comment_blocks(text, TASK_STATE_MARKER)
    if error is not None:
        return None, [("TASK_STATE_INVALID", error)]
    if not blocks:
        return None, None
    if len(blocks) > 1:
        return None, [
            ("TASK_STATE_DUPLICATE", f"expected at most one {TASK_STATE_MARKER} block, found {len(blocks)}")
        ]
    state, error = parse_block_object(blocks[0])
    if state is None:
        return None, [("TASK_STATE_INVALID", f"invalid {TASK_STATE_MARKER} block: {error}")]
    validation_errors = validate_state_object(state)
    if validation_errors:
        return None, [
            ("TASK_STATE_INVALID", f"invalid {TASK_STATE_MARKER} block: {message}")
            for message in validation_errors
        ]
    return state, []


def measure_hot_files(run: VaultCheckRun, texts: dict[str, str]) -> None:
    definitions = (
        ("runtime", "vault/runtime.md", "recent_entries", count_recent_entries),
        ("handoff", "vault/handoff.md", "entries", count_handoff_entries),
        ("decisions", "vault/decisions.md", "records", count_decision_records),
        ("parked", "vault/parked.md", "entries", count_parked_entries),
    )
    for key, relative, entry_key, counter in definitions:
        text = texts.get(relative)
        if text is None:
            continue
        lines = text.splitlines()
        encoded = text.encode("utf-8")
        run.measurements[key] = {
            "lines": len(lines),
            "bytes": len(encoded),
            "max_line_bytes": max((len(line.encode("utf-8")) for line in lines), default=0),
            entry_key: counter(text),
        }


def check_budgets(run: VaultCheckRun, policy: dict | None) -> None:
    if policy is None:
        return
    budgets = policy.get("budgets") or {}
    for file_key, measurement in run.measurements.items():
        thresholds = budgets.get(file_key)
        if not isinstance(thresholds, dict):
            continue
        for threshold_key, measured_key in BUDGET_MEASUREMENT_KEYS.get(file_key, {}).items():
            limit = thresholds.get(threshold_key)
            if limit is None:
                continue
            measured = measurement[measured_key]
            if measured > limit:
                run.add(
                    "budgets",
                    "BUDGET_EXCEEDED",
                    "warning",
                    f"vault/{file_key}.md",
                    f"{file_key}.{measured_key} is {measured}, above the configured limit {threshold_key}={limit}",
                )


def check_task_budget(run: VaultCheckRun, policy: dict | None, tasks: list[dict], ledgers: list[str], archive: list[str]) -> None:
    limit = None
    if policy is not None:
        thresholds = (policy.get("budgets") or {}).get("tasks")
        if isinstance(thresholds, dict):
            limit = thresholds.get("max_active_tasks")
    closed = {"accepted", "superseded"}
    unresolved = [task for task in tasks if not task["valid"]]
    active = [task for task in tasks if task["valid"] and task["lifecycle"] not in closed]
    run.measurements["tasks"] = {
        "current_task_files": len(tasks),
        "active_tasks": len(active),
        "closed_tasks": len(tasks) - len(active) - len(unresolved),
        "legacy_tasks": len(unresolved),
        "review_ledgers": len(ledgers),
        "archive_files": len(archive),
    }
    if limit is None:
        return
    if unresolved:
        run.add(
            "budgets",
            "TASK_COUNT_UNRESOLVED",
            "warning",
            "vault/tasks",
            f"cannot verify budgets.tasks.max_active_tasks={limit}: {len(unresolved)} task file(s) have no valid trellium-task-state block",
        )
        return
    if len(active) > limit:
        run.add(
            "budgets",
            "BUDGET_EXCEEDED",
            "warning",
            "vault/tasks",
            f"{len(active)} open task files exceed the configured limit max_active_tasks={limit}",
        )


def check_task_storage(run: VaultCheckRun, policy: dict | None, tasks: list[dict], ledgers: list[str], archive: list[str]) -> None:
    task_paths = [task["path"] for task in tasks] + ledgers + archive
    if policy is None:
        # POLICY_MISSING already reports the unresolved project strategy.
        return
    storage = normalized_storage_mode(policy)
    if not task_paths and storage != "tracked":
        return
    if not git_in_worktree(run.target):
        if task_paths:
            run.add("storage", "GIT_CHECK_SKIPPED", "warning", "vault/tasks", "not a Git worktree or Git is unavailable; TASK storage was not verified")
        return
    tracked = git_tracked_files(run.target)
    if tracked is None:
        run.add("storage", "GIT_CHECK_SKIPPED", "warning", "vault/tasks", "git ls-files failed; TASK storage was not verified")
        return

    if storage == "tracked":
        for relative in sorted(tracked):
            path = Path(relative)
            if (
                path.parent.as_posix() != "vault/tasks"
                or TASK_FILE_ID_RE.match(path.name) is None
                or REVIEW_LEDGER_RE.match(path.name) is not None
                or path.suffix != ".md"
            ):
                continue
            try:
                (run.target / path).lstat()
            except FileNotFoundError:
                run.add(
                    "storage",
                    "TASK_STORAGE_MISMATCH",
                    "error",
                    relative,
                    f"task_storage=tracked but indexed task file {relative} is missing from the working tree",
                    task_id=task_id_of(relative),
                )
            except OSError:
                # Existing task-state discovery reports unreadable filesystem
                # entries; this branch only proves index-known deletion.
                pass

    if not task_paths:
        return

    if storage in ("local", "private"):
        for relative in task_paths:
            if relative in tracked:
                if storage == "local":
                    message = f"task_storage=local but {relative} is tracked or staged in Git; remove it from the index as the project owner decided"
                else:
                    message = f"storage_mode=private but {relative} is tracked or staged in Git; private TASK journals never enter Git; remove it from the index as the project owner decided"
                run.add(
                    "storage",
                    "TASK_STORAGE_MISMATCH",
                    "error",
                    relative,
                    message,
                    task_id=task_id_of(relative),
                )
        return

    ignored = git_ignored_files(run.target, task_paths)
    if ignored is None:
        run.add("storage", "GIT_CHECK_SKIPPED", "warning", "vault/tasks", "git check-ignore failed; TASK storage was not verified")
        return
    for relative in task_paths:
        if relative in ignored:
            run.add(
                "storage",
                "TASK_STORAGE_MISMATCH",
                "error",
                relative,
                f"task_storage=tracked but {relative} is Git-ignored",
                task_id=task_id_of(relative),
            )
    for relative in archive:
        if relative not in tracked:
            run.add(
                "storage",
                "TASK_STORAGE_MISMATCH",
                "error",
                relative,
                f"task_storage=tracked but archived task file {relative} is not tracked",
                task_id=task_id_of(relative),
            )
    closed = {"accepted", "superseded"}
    for task in tasks:
        if task["path"] in tracked:
            continue
        if task["legacy"] or not task["valid"]:
            reason = "legacy" if task["legacy"] else "its state block is invalid"
            run.add(
                "storage",
                "TASK_STORAGE_UNRESOLVED",
                "warning",
                task["path"],
                f"task_storage=tracked but {task['path']} is not tracked and its lifecycle is unresolved ({reason})",
                task_id=task["task_id"],
            )
        elif task["lifecycle"] in closed:
            run.add(
                "storage",
                "TASK_STORAGE_MISMATCH",
                "error",
                task["path"],
                f"task_storage=tracked but closed task ({task['lifecycle']}) {task['path']} is not tracked",
                task_id=task["task_id"],
            )
        else:
            run.add(
                "storage",
                "TASK_STORAGE_PENDING",
                "warning",
                task["path"],
                f"task_storage=tracked but {task['path']} is not tracked yet (allowed until the task is committed)",
                task_id=task["task_id"],
            )


def task_id_of(relative: str) -> str | None:
    match = TASK_FILE_ID_RE.match(Path(relative).name)
    return match.group(1) if match else None


def collect_vault_state(target: Path) -> tuple[VaultCheckRun, dict[str, str], list[dict]]:
    """Run all read-only vault checks and also return inputs and task records."""
    run = VaultCheckRun(target)
    if (target / "vault").is_symlink():
        run.add("required-files", "SYMLINK_INPUT", "error", "vault", "vault/ is a symbolic link; refusing to follow it")
        return run, {}, []
    texts = check_required_files(run)
    policy = check_policy_block(run, texts.get("vault/index.md"))
    tasks, ledgers, archive = discover_task_files(run)
    measure_hot_files(run, texts)
    check_budgets(run, policy)
    check_task_budget(run, policy, tasks, ledgers, archive)
    check_task_storage(run, policy, tasks, ledgers, archive)
    core = adoption_core_paths(run.target)
    if normalized_storage_mode(policy) == "private":
        check_private_boundary(run, policy, core)
    else:
        check_core_storage(run, core)
        check_local_boundary(run, policy, core)
    return run, texts, tasks


def run_vault_checks(target: Path) -> VaultCheckRun:
    return collect_vault_state(target)[0]


def render_check_text(run: VaultCheckRun) -> None:
    print(f"vault check: {run.target}")
    for finding in run.sorted_findings():
        task_suffix = f" [{finding['task_id']}]" if "task_id" in finding else ""
        print(f"  {finding['severity'].upper():<7} {finding['code']} {finding['path']}{task_suffix}: {finding['message']}")
    if run.measurements:
        print("measurements:")
        for key in sorted(run.measurements):
            parts = [f"{name}={value}" for name, value in run.measurements[key].items()]
            print(f"  {key}: {', '.join(parts)}")
    errors, warnings = len(run.errors), len(run.warnings)
    print(f"summary: {errors} error(s), {warnings} warning(s)")
    if errors:
        print("result: failed")
    elif warnings:
        print("result: passed with warnings")
    else:
        print("result: ok")


def check_project(args: argparse.Namespace) -> int:
    try:
        target = resolve_existing_target(args.target)
    except (AdoptionError, OSError) as exc:
        return fail(str(exc))
    if args.format not in ("text", "json"):
        return fail(f"unknown format: {args.format} (expected text or json)")
    if not (target / "vault").is_dir():
        return fail(f"target has no vault/ directory; run 'adopt' first: {target}")

    run = run_vault_checks(target)
    if args.format == "json":
        payload = {
            "schema_version": 1,
            "target": str(target),
            "summary": {"errors": len(run.errors), "warnings": len(run.warnings)},
            "findings": run.sorted_findings(),
            "measurements": run.measurements,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        render_check_text(run)
    return CHECK_ERROR_EXIT if run.errors else 0



# --- Vault status (read-only) -----------------------------------------------
#
# `status` compiles the same checked state layer as `check` into an owner
# summary: navigation focus, canonical open-task state, closed counts, and
# explicit unresolved entries. It adds no facts and claims no authority:
# lifecycle, authority, slice, and gates come only from validated task state
# blocks. Closed tasks appear as counts only. Like `check`, it never writes,
# never follows symlinks into vault inputs, and never executes content.

STATUS_OPEN_LIFECYCLES = ("draft", "active", "blocked", "ready_for_review")
CLOSED_LIFECYCLES = frozenset({"accepted", "superseded"})

# Unresolved reasons come straight from canonical task-state checks. Storage
# and budget findings never demote or misdescribe lifecycle state.
STATUS_REASON_PHASES = frozenset({"task-state"})


def status_unresolved_reasons(phase_findings: list[tuple[str, dict]]) -> dict[str, list[str]]:
    """Map task ids to ordered unique finding codes from lifecycle phases."""
    reasons: dict[str, list[str]] = {}
    for phase, finding in phase_findings:
        if phase not in STATUS_REASON_PHASES:
            continue
        code = finding["code"]
        task_id = finding.get("task_id")
        if task_id is None:
            # Path-only findings name current task files only: review ledgers
            # and archive/ entries are cold history, never current state.
            path = finding["path"]
            name = Path(path).name
            match = TASK_FILE_ID_RE.match(name)
            if (
                match is None
                or REVIEW_LEDGER_RE.match(name) is not None
                or path.startswith("vault/tasks/archive/")
            ):
                continue
            task_id = match.group(1)
        codes = reasons.setdefault(task_id, [])
        if code not in codes:
            codes.append(code)
    return reasons


def build_status_payload(
    target: Path,
    run: VaultCheckRun,
    texts: dict[str, str],
    tasks: list[dict],
) -> dict:
    phase_findings = run.findings_with_phase()
    findings = [finding for _phase, finding in phase_findings]
    runtime_text = texts.get("vault/runtime.md")
    focus_ids: list[str] = []
    if runtime_text is not None:
        focus_ids = parse_runtime_focus(runtime_text)

    reasons = status_unresolved_reasons(phase_findings)
    open_buckets: dict[str, list[dict]] = {lifecycle: [] for lifecycle in STATUS_OPEN_LIFECYCLES}
    unresolved: list[dict] = []
    unresolved_ids: set[str] = set()
    resolved_ids: set[str] = set()
    closed = 0

    def unresolved_entry(task_id: str, path: str | None) -> dict:
        # Every unresolved task source emits a task-state finding, so the
        # reason below is the actual check diagnosis. "UNVERIFIED" is a
        # neutral last resort, never a fabricated checker code.
        entry: dict = {
            "task_id": task_id,
            "reason": ",".join(reasons.get(task_id) or ["UNVERIFIED"]),
        }
        if path is not None:
            entry["task_path"] = path
        return entry

    for task in tasks:
        task_id = task["task_id"]
        if not task["valid"]:
            if task_id not in unresolved_ids:
                unresolved_ids.add(task_id)
                # A duplicated id spans several files; the findings list keeps
                # every path, so the entry stays pathless instead of picking one.
                ambiguous = "TASK_ID_DUPLICATE" in reasons.get(task_id, [])
                unresolved.append(unresolved_entry(task_id, None if ambiguous else task["path"]))
            continue
        resolved_ids.add(task_id)
        if task["lifecycle"] in CLOSED_LIFECYCLES:
            closed += 1
            continue
        state = task["state"]
        item: dict = {
            "task_id": task_id,
            "lifecycle": task["lifecycle"],
            "authority_level": state["authority_level"],
            "task_path": task["path"],
        }
        if "current_slice" in state:
            item["current_slice"] = state["current_slice"]
        if "gates" in state:
            item["gates"] = state["gates"]
        open_buckets[task["lifecycle"]].append(item)

    # A current task file can also fail before any record exists (unreadable,
    # not a regular file); its id still belongs in unresolved.
    for task_id in sorted(reasons):
        if task_id in resolved_ids or task_id in unresolved_ids:
            continue
        unresolved_ids.add(task_id)
        unresolved.append(unresolved_entry(task_id, None))
    # Enumeration refused (vault or vault/tasks unreadable): say so with an
    # explicit vault-scope record instead of reporting a clean bill of health.
    # The joint shape (scope/path/reason, no task_id) cannot be mistaken for a
    # task, and summary.unresolved stays consistent with the array.
    refused_paths = sorted(
        {
            finding["path"]
            for finding in findings
            if finding["code"] == "SYMLINK_INPUT" and finding.get("path") in {"vault", "vault/tasks"}
        }
    )
    for path in refused_paths:
        unresolved.append({"scope": "vault", "path": path, "reason": "SYMLINK_INPUT"})
    unresolved.sort(key=lambda entry: entry.get("task_id") or f"~{entry.get('path', '')}")

    return {
        "schema_version": 1,
        "target": str(target),
        "focus": [
            {"task_id": task_id, "resolved": task_id in resolved_ids}
            for task_id in focus_ids
        ],
        "summary": {
            "draft": len(open_buckets["draft"]),
            "active": len(open_buckets["active"]),
            "blocked": len(open_buckets["blocked"]),
            "ready_for_review": len(open_buckets["ready_for_review"]),
            "closed": closed,
            "unresolved": len(unresolved),
        },
        "tasks": {
            "ready_for_review": open_buckets["ready_for_review"],
            "blocked": open_buckets["blocked"],
            "active": open_buckets["active"],
            "draft": open_buckets["draft"],
            "unresolved": unresolved,
        },
        "findings": findings,
    }


def render_status_text(payload: dict) -> None:
    print(f"trellium status: {payload['target']}")
    if payload["focus"]:
        focus_cells = [
            f"{item['task_id']} ({'resolved' if item['resolved'] else 'unresolved'})"
            for item in payload["focus"]
        ]
        print(f"focus: {', '.join(focus_cells)}")
    else:
        print("focus: (none)")
    summary = payload["summary"]
    print(
        "summary: {draft} draft, {active} active, {blocked} blocked, "
        "{ready_for_review} ready_for_review, {closed} closed, {unresolved} unresolved".format(**summary)
    )
    for lifecycle in STATUS_OPEN_LIFECYCLES:
        items = payload["tasks"][lifecycle]
        if not items:
            print(f"{lifecycle}: (none)")
            continue
        print(f"{lifecycle} ({len(items)}):")
        for item in items:
            head = f"  {item['task_id']} authority={item['authority_level']}"
            if "current_slice" in item:
                head += f" slice={item['current_slice']}"
            if "gates" in item:
                gates = ", ".join(f"{gate}={value}" for gate, value in sorted(item["gates"].items()))
                head += f" gates: {gates}"
            head += f" path={item['task_path']}"
            print(head)
    unresolved = payload["tasks"]["unresolved"]
    if not unresolved:
        print("unresolved: (none)")
    else:
        print(f"unresolved ({len(unresolved)}):")
        for item in unresolved:
            if "scope" in item:
                line = f"  [{item['scope']}] path={item['path']} reason={item['reason']}"
            else:
                line = f"  {item['task_id']} reason={item['reason']}"
            if "task_path" in item:
                line += f" path={item['task_path']}"
            print(line)
    findings = payload["findings"]
    if not findings:
        print("findings: none")
    else:
        print(f"findings ({len(findings)}):")
        for finding in findings:
            task_suffix = f" [{finding['task_id']}]" if "task_id" in finding else ""
            print(f"  {finding['severity'].upper():<7} {finding['code']} {finding['path']}{task_suffix}: {finding['message']}")
    errors = sum(1 for finding in findings if finding["severity"] == "error")
    warnings = sum(1 for finding in findings if finding["severity"] == "warning")
    print(f"result: {errors} error(s), {warnings} warning(s)")


def status_project(args: argparse.Namespace) -> int:
    try:
        target = resolve_existing_target(args.target)
    except (AdoptionError, OSError) as exc:
        return fail(str(exc))
    if args.format not in ("text", "json"):
        return fail(f"unknown format: {args.format} (expected text or json)")
    if not (target / "vault").is_dir():
        return fail(f"target has no vault/ directory; run 'adopt' first: {target}")

    run, texts, tasks = collect_vault_state(target)
    payload = build_status_payload(target, run, texts, tasks)
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        render_status_text(payload)
    return CHECK_ERROR_EXIT if run.errors else 0



# --- Release fetching (--fetch) --------------------------------------------


def latest_release_tag() -> str:
    """Return the newest CalVer tag of the upstream repository."""
    if not FETCH_TAGS_URL.startswith("https://"):
        raise AdoptionError(f"refusing non-https fetch URL: {FETCH_TAGS_URL}")
    request = urllib.request.Request(
        FETCH_TAGS_URL,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "trellium-fetch"},
    )
    # FETCH_TAGS_URL is a module constant pinned to https; the guard above
    # keeps the scheme allowlist explicit for auditors.
    with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as response:  # noqa: S310
        body = response.read().decode("utf-8")
    try:
        payload = json.loads(body)
    except ValueError as exc:
        raise AdoptionError(f"invalid tag listing from {FETCH_TAGS_URL}: {exc}") from exc
    if not isinstance(payload, list):
        raise AdoptionError(f"unexpected tag listing from {FETCH_TAGS_URL}")
    candidates = []
    for entry in payload:
        if isinstance(entry, dict):
            name = str(entry.get("name", ""))
            if parse_version(name) is not None:
                candidates.append((parse_version(name), name))
    if not candidates:
        raise AdoptionError(f"no version tags found for {FETCH_REPOSITORY}; publish a tag first")
    # GitHub lists recently created tags first, but sort defensively anyway.
    return max(candidates)[1]


def safe_extract_tarball(tarball_path: Path, destination: Path) -> None:
    """Extract a release tarball while refusing anything but plain files and directories."""
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with tarfile.open(tarball_path, "r:gz") as archive:
        for member in archive.getmembers():
            if member.issym() or member.islnk() or member.isdev():
                raise AdoptionError(f"refusing non-regular file in release tarball: {member.name}")
            target = (root / member.name).resolve()
            if not target.is_relative_to(root):
                raise AdoptionError(f"refusing path escape in release tarball: {member.name}")
        # Members were individually validated above; the "data" filter is a
        # second, interpreter-level line of defense (strips setuid/setgid and
        # refuses absolute/traversal targets).
        archive.extractall(destination, filter="data")


def fetch_release_tree(tag: str) -> Path:
    """Return the extracted release tree for a tag, downloading it once."""
    destination = FETCH_CACHE_ROOT / tag
    if (
        (destination / FETCH_MARKER_NAME).is_file()
        and (destination / "scripts" / "trellium.py").is_file()
        and (destination / "init" / "VERSION").is_file()
    ):
        return destination

    FETCH_CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    staging_tarball = FETCH_CACHE_ROOT / f".{tag}.{secrets.token_hex(8)}.tar.gz"
    staging_extract = FETCH_CACHE_ROOT / f".{tag}.extracting.{secrets.token_hex(8)}"
    try:
        tarball_url = FETCH_TARBALL_TEMPLATE.format(tag=tag)
        if not tarball_url.startswith("https://"):
            raise AdoptionError(f"refusing non-https fetch URL: {tarball_url}")
        request = urllib.request.Request(  # noqa: S310
            tarball_url,
            headers={"User-Agent": "trellium-fetch"},
        )
        # tarball_url is https-guarded above.
        with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as response, staging_tarball.open("wb") as handle:  # noqa: S310
            shutil.copyfileobj(response, handle)
        safe_extract_tarball(staging_tarball, staging_extract)
        entries = list(staging_extract.iterdir())
        if len(entries) != 1 or not entries[0].is_dir():
            raise AdoptionError(f"release tarball for {tag} has an unexpected layout")
        if destination.exists():
            shutil.rmtree(destination)
        entries[0].rename(destination)
        (destination / FETCH_MARKER_NAME).write_text(f"{tag}\n", encoding="utf-8")
    finally:
        if staging_tarball.exists():
            staging_tarball.unlink()
        if staging_extract.exists():
            shutil.rmtree(staging_extract)
    return destination


def fetch_and_run(args: argparse.Namespace, forwarded: list[str]) -> int:
    """Resolve the latest release and re-execute the fetched updater."""
    try:
        tag = latest_release_tag()
        release_dir = fetch_release_tree(tag)
        fetched_version = (release_dir / "init" / "VERSION").read_text(encoding="utf-8").strip()
    except (AdoptionError, OSError, ValueError, tarfile.TarError) as exc:
        return fail(
            f"could not fetch the latest release: {exc}; "
            "rerun without --fetch to use the bundled content"
        )

    target_value = getattr(args, "target", None)
    if target_value:
        try:
            target = Path(target_value).expanduser().resolve()
            stamp = read_stamp(target)
        except (AdoptionError, OSError, RuntimeError):
            stamp = None
        if stamp is not None:
            installed = parse_version(stamp.get("protocol_version"))
            fetched = parse_version(fetched_version)
            if installed is not None and fetched is not None and fetched < installed:
                return fail(
                    f"latest release {tag} ({fetched_version}) is older than the target's "
                    f"installed protocol {stamp.get('protocol_version')}; "
                    "rerun without --fetch to use the bundled content"
                )

    package_name = TEMPLATES_ROOT.parent.parent.name
    fetched_script = release_dir / "scripts" / "trellium.py"
    fetched_templates = release_dir / "skills" / package_name / "assets" / "templates"
    if not fetched_script.is_file() or not (fetched_templates / "AGENTS.md").is_file():
        return fail(f"release {tag} is missing the updater script or the {package_name} templates")

    command = [sys.executable, str(fetched_script), *forwarded, "--templates", str(fetched_templates)]
    print(f"fetch: using {FETCH_REPOSITORY} tag {tag} (protocol {fetched_version})")
    result = subprocess.run(command, check=False, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode


def git_dirty_paths(
    target: Path, relatives: list[str], include_untracked: bool = True
) -> list[str]:
    if not (target / ".git").exists():
        return []
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", *relatives],
            cwd=target,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    dirty = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        if not include_untracked and line.startswith("?? "):
            continue
        dirty.append(line[3:].strip().strip('"'))
    return dirty


def target_storage_mode(target: Path) -> str | None:
    """Best-effort storage mode from the target's own policy block; None if unreadable."""
    try:
        index_text = (target / "vault/index.md").read_text(
            encoding="utf-8", errors="surrogateescape"
        )
    except (OSError, UnicodeError):
        return None
    blocks, error = extract_comment_blocks(index_text, POLICY_MARKER)
    if error is not None or not blocks:
        return None
    policy, error = parse_block_object(blocks[0])
    if policy is None:
        return None
    return normalized_storage_mode(policy)


def selection_filter(args: argparse.Namespace):
    skip = set(args.skip or [])
    only = set(args.only or []) if args.only else None
    known_paths = {
        *FILE_ROLES,
        PROFILE_RULES_RELATIVE,
        *(profile_document_relative(profile_id) for profile_id in PROFILE_IDS),
    }
    unknown = (skip | (only or set())) - known_paths
    if unknown:
        raise AdoptionError(f"unknown paths in --only/--skip: {', '.join(sorted(unknown))}")

    def selected(relative: str) -> bool:
        if relative in skip:
            return False
        return only is None or relative in only

    return selected


def apply_protocol_file(
    target: Path,
    relative: str,
    role: str,
    force: bool,
    target_descriptor: int | None,
    profiles: list[dict] | None = None,
) -> str:
    if role == "marker":
        return update_agent_entry_region(target, target_descriptor)
    if relative == PROFILE_RULES_RELATIVE:
        if not profiles:
            raise AdoptionError("profile rule update has no selected profiles")
        return write_text_file(
            target / relative,
            render_profile_document(profiles),
            target,
            force=force,
            dry_run=False,
            target_descriptor=target_descriptor,
        )
    profile = profile_for_relative(relative, profiles or [])
    if profile is not None:
        return write_text_file(
            target / relative,
            render_durable_profile(profile),
            target,
            force=force,
            dry_run=False,
            target_descriptor=target_descriptor,
        )
    return copy_file(
        template_source(relative),
        target / relative,
        target,
        force=force,
        dry_run=False,
        target_descriptor=target_descriptor,
    )


def update_agent_entry_region(target: Path, target_descriptor: int | None) -> str:
    new_region = upstream_marker_region()
    agents_path = target / "AGENTS.md"
    if target_descriptor is not None:
        with open_parent_directory(target_descriptor, Path("AGENTS.md"), create=True) as (
            parent_descriptor,
            name,
        ):
            metadata = output_metadata_at(parent_descriptor, name)
            if metadata is None:
                raise AdoptionError(f"agent entry file disappeared during upgrade: {agents_path}")
            validate_output_metadata(metadata, agents_path)
            current = read_text_at(parent_descriptor, name, agents_path)
            if marker_region(current) is None:
                raise AdoptionError(f"Trellium marker region missing in {agents_path}")
            atomic_write_text_at(
                parent_descriptor,
                name,
                replace_marker_region(current, new_region),
                stat.S_IMODE(metadata.st_mode),
            )
            return "updated"

    validate_output_paths(target, [agents_path])
    current = agents_path.read_text(encoding="utf-8")
    if marker_region(current) is None:
        raise AdoptionError(f"Trellium marker region missing in {agents_path}")
    atomic_write_text(agents_path, replace_marker_region(current, new_region))
    return "updated"


def remove_tracked_file(target: Path, relative: str, target_descriptor: int | None) -> None:
    validate_managed_relative(relative)
    if target_descriptor is not None:
        with open_parent_directory(target_descriptor, Path(relative), create=False) as (
            parent_descriptor,
            name,
        ):
            metadata = output_metadata_at(parent_descriptor, name)
            if metadata is None:
                return
            validate_output_metadata(metadata, target / relative)
            unlink_at_if_present(parent_descriptor, name)
        return
    metadata = managed_file_metadata(target, relative)
    if metadata is None:
        return
    with suppress(FileNotFoundError):
        (target / relative).unlink()


def backup_upgraded_file(
    target: Path,
    relative: str,
    version: str,
    target_descriptor: int | None,
) -> None:
    if managed_file_metadata(target, relative) is None:
        return
    source = target / relative
    backup = f"{BACKUP_DIRECTORY}/{version}/{relative}"
    validate_managed_relative(backup)
    copy_file(source, target / backup, target, force=True, dry_run=False, target_descriptor=target_descriptor)


def proposal_relative(version: str, relative: str) -> str:
    flattened = relative.replace("/", "__")
    return f"{PROPOSAL_DIRECTORY}/{version}/{flattened}.proposal.md"


def render_proposal(
    target: Path,
    version: str,
    item: dict,
    profiles: list[dict] | None = None,
) -> str:
    relative, role = item["path"], item["role"]
    reason = item.get("reason", "")
    if role == "marker":
        upstream_text = upstream_marker_region()
        text = read_managed_text(target, relative)
        local_text = marker_region(text) if text is not None else ""
        local_text = local_text or ""
    elif relative == PROFILE_RULES_RELATIVE:
        if not profiles:
            raise AdoptionError("profile rule proposal has no selected profiles")
        upstream_text = render_profile_document(profiles)
        local_text = read_managed_text(target, relative) or ""
    elif (profile := profile_for_relative(relative, profiles or [])) is not None:
        upstream_text = render_durable_profile(profile)
        local_text = read_managed_text(target, relative) or ""
    else:
        upstream_text = template_source(relative).read_text(encoding="utf-8")
        local_text = read_managed_text(target, relative) or ""
    diff = "\n".join(
        difflib.unified_diff(
            upstream_text.splitlines(),
            local_text.splitlines(),
            fromfile=f"upstream/{relative}",
            tofile=f"local/{relative}",
            lineterm="",
        )
    )
    return (
        f"# Upgrade Proposal - {version}\n\n"
        f"- File: `{relative}`\n"
        f"- Role: {role}\n"
        f"- Reason: {reason}\n\n"
        "The upstream template and the local file both changed. Merge the upstream\n"
        "version into the local file while preserving every local customization,\n"
        "then propose the result to the user. Project data is never at risk here,\n"
        "and the previous content stays recoverable through git.\n\n"
        f"## Upstream template\n\n````md\n{upstream_text.rstrip()}\n````\n\n"
        f"## Differences (upstream -> local)\n\n````diff\n{diff}\n````\n"
    )


def updated_stamp_after_apply(
    target: Path,
    stamp: dict,
    version: str,
    apply_items: list[dict],
    add_items: list[dict],
    remove_items: list[dict],
    conflict_items: list[dict],
    applied: dict[str, str],
    profiles: list[dict],
) -> dict:
    files = {relative: dict(entry) for relative, entry in stamp["files"].items()}
    for item in (*apply_items, *add_items):
        relative, role = item["path"], item["role"]
        if applied.get(relative) == "skipped":
            continue
        baseline = upstream_hash_for_role(relative, role, profiles)
        if baseline is None:
            continue
        files[relative] = {"role": role, "baseline": baseline}
    for item in remove_items:
        files.pop(item["path"], None)
    for item in conflict_items:
        entry = files.get(item["path"])
        if entry is None:
            entry = {
                "role": item["role"],
                "baseline": local_hash_for_role(target, item["path"], item["role"]) or "",
            }
        # Remember which upstream revision the pending proposal merges in, so
        # a completed merge is recognized as absorbed instead of re-proposed.
        absorbed = upstream_hash_for_role(item["path"], item["role"], profiles)
        if absorbed is not None:
            entry["absorbed_upstream"] = absorbed
        entry["pending"] = True
        files[item["path"]] = entry
    updated = dict(stamp)
    updated["schema_version"] = 2
    updated["files"] = files
    updated["target_version"] = version
    if not conflict_items:
        updated["protocol_version"] = version
        updated["last_upgrade"] = date.today().isoformat()
        updated["trust"] = "versioned"
        updated["profiles"] = profile_metadata(profiles)
    return updated


def baseline_project(args: argparse.Namespace) -> int:
    try:
        target = resolve_existing_target(args.target)
        if not (target / "vault").is_dir():
            raise AdoptionError(
                f"target has no vault/ directory; run 'adopt' for new adoptions: {target}"
            )
        if read_stamp(target) is not None:
            raise AdoptionError(f"adoption stamp already exists: {stamp_path(target)}")
        files: dict[str, dict] = {}
        for relative, role in sorted(FILE_ROLES.items()):
            if relative == "AGENTS.md":
                agents_text = read_managed_text(target, relative)
                if agents_text is None:
                    continue
                region = marker_region(agents_text)
                if region is not None:
                    files[relative] = {
                        "role": "marker",
                        "baseline": sha256_hex(region.encode("utf-8")),
                        "observed": True,
                    }
                else:
                    files[relative] = {
                        "role": "merge",
                        "baseline": sha256_hex(agents_text.encode("utf-8")),
                        "observed": True,
                    }
                continue
            baseline = local_hash_for_role(target, relative, role)
            if baseline is None:
                continue
            files[relative] = {"role": role, "baseline": baseline, "observed": True}
        stamp = {
            "schema_version": 2,
            "protocol_version": None,
            "adopted_at": None,
            "last_upgrade": None,
            "trust": "unversioned",
            "profiles": [],
            "files": files,
        }
        descriptor = open_upgrade_descriptor(target)
        try:
            write_stamp_file(target, stamp, descriptor)
        finally:
            if descriptor is not None:
                os.close(descriptor)
    except (AdoptionError, OSError) as exc:
        return fail(str(exc))

    print(f"baseline recorded: {len(stamp['files'])} tracked file(s) at {target}")
    print("trust: unversioned -- upstream changes only produce proposals until the first upgrade completes")
    return 0


def diff_project(args: argparse.Namespace) -> int:
    try:
        target = resolve_existing_target(args.target)
        stamp = read_stamp(target)
        if stamp is None:
            raise AdoptionError(
                f"no adoption stamp found at {stamp_path(target)}; "
                "run 'adopt' for new adoptions or 'baseline' for an existing vault"
            )
        plan = build_upgrade_plan(target, stamp)
        print_upgrade_header(target, stamp)
        print_plan(plan)
        print_playbook(migrations_after(stamp.get("protocol_version")))
    except (AdoptionError, OSError) as exc:
        return fail(str(exc))
    return plan_exit_code(plan)


def complete_upgrade(target: Path, stamp: dict) -> int:
    entries = stamp["files"]
    pending = sorted(relative for relative, entry in entries.items() if entry.get("pending"))
    if not pending:
        return fail("no pending proposals to complete; run 'diff' to check the current state")
    for relative in pending:
        role = entries[relative].get("role", "merge")
        baseline = local_hash_for_role(target, relative, role)
        if baseline is None:
            return fail(f"pending file is missing: {relative}")
        entries[relative]["baseline"] = baseline
        entries[relative]["observed"] = True
        entries[relative]["pending"] = False
    try:
        version = read_protocol_version()
    except AdoptionError as exc:
        return fail(str(exc))
    stamp["protocol_version"] = version
    stamp["last_upgrade"] = date.today().isoformat()
    stamp["trust"] = "versioned"
    stamp["schema_version"] = 2
    profiles = selections_from_stamp(stamp)
    stamp["profiles"] = profile_metadata(profiles)
    stamp.pop("target_version", None)
    try:
        descriptor = open_upgrade_descriptor(target)
        try:
            write_stamp_file(target, stamp, descriptor)
        finally:
            if descriptor is not None:
                os.close(descriptor)
    except (AdoptionError, OSError) as exc:
        return fail(str(exc))

    print(f"completed upgrade to {version}: {len(pending)} proposal file(s) finalized")
    for relative in pending:
        print(f"  - {relative}")
    print_playbook([section for section in read_migration_sections() if section[0] == version])
    if target_storage_mode(target) == "private":
        print(
            "next: private storage - keep all Trellium material untracked and covered by the"
            " trellium-private block in .git/info/exclude; never commit Trellium material;"
            " re-run check to confirm the boundary"
        )
    else:
        print("next: commit this upgrade as a standalone, revertable change")
    return 0


def upgrade_project(args: argparse.Namespace) -> int:
    try:
        target = resolve_existing_target(args.target)
        stamp = read_stamp(target)
        if stamp is None:
            raise AdoptionError(
                f"no adoption stamp found at {stamp_path(target)}; "
                "run 'adopt' for new adoptions or 'baseline' for an existing vault"
            )
        version = read_protocol_version()
        profiles = selections_from_stamp(stamp)
        plan = build_upgrade_plan(target, stamp)
        selected = selection_filter(args)
    except (AdoptionError, OSError) as exc:
        return fail(str(exc))

    if args.complete:
        return complete_upgrade(target, stamp)

    print_upgrade_header(target, stamp)
    print_plan(plan)
    print_playbook(migrations_after(stamp.get("protocol_version")))

    if not args.apply:
        print("dry run only; rerun with --apply to execute apply/add/remove; conflicts always produce proposals")
        return plan_exit_code(plan)

    apply_items = [item for item in plan["apply"] if selected(item["path"])]
    add_items = [item for item in plan["add"] if selected(item["path"])]
    remove_items = [item for item in plan["remove"] if selected(item["path"])]
    conflict_items = [item for item in plan["conflict"] if selected(item["path"])]

    if not (apply_items or add_items or remove_items or conflict_items):
        # A tooling-only release changes no files; still move the stamp
        # forward so the version pointer does not stick behind forever.
        if args.apply and stamp.get("trust") == "versioned" and stamp.get("protocol_version") != version:
            stamp["protocol_version"] = version
            stamp["last_upgrade"] = date.today().isoformat()
            stamp["schema_version"] = 2
            stamp["profiles"] = profile_metadata(profiles)
            descriptor = open_upgrade_descriptor(target)
            try:
                write_stamp_file(target, stamp, descriptor)
            finally:
                if descriptor is not None:
                    os.close(descriptor)
            print(f"recorded protocol version {version} (no file changes)")
        print("nothing to apply")
        return plan_exit_code(plan)

    touch_paths = [item["path"] for item in (*apply_items, *add_items, *remove_items)]
    storage_mode = target_storage_mode(target)
    dirty = git_dirty_paths(
        target,
        [*touch_paths, STAMP_RELATIVE],
        include_untracked=storage_mode != "private",
    )
    if dirty and not args.allow_dirty:
        return fail(
            "target has uncommitted changes in files the upgrade would touch: "
            + ", ".join(sorted(dirty))
            + "; commit or stash them first, or pass --allow-dirty"
        )

    try:
        for item in (*apply_items, *add_items, *remove_items, *conflict_items):
            assert_upgrade_writable(target, item["path"], profiles)
        destinations = [target / item["path"] for item in (*apply_items, *add_items)]
        proposals = [
            (
                proposal_relative(version, item["path"]),
                render_proposal(target, version, item, profiles),
            )
            for item in conflict_items
        ]
    except (AdoptionError, OSError) as exc:
        return fail(str(exc))

    target_descriptor: int | None = None
    outcomes: list[tuple[str, str, str]] = []
    try:
        if ANCHORED_WRITES_SUPPORTED:
            target_descriptor = open_target_directory(target, create=False)
        if destinations:
            validate_output_paths(target, destinations)
        if not (target / ".git").exists():
            backup_version = stamp.get("protocol_version") or "unknown"
            for item in (*apply_items, *remove_items):
                backup_upgraded_file(target, item["path"], backup_version, target_descriptor)

        for item in (*apply_items, *add_items):
            relative, role = item["path"], item["role"]
            action = apply_protocol_file(
                target,
                relative,
                role,
                force=item in apply_items,
                target_descriptor=target_descriptor,
                profiles=profiles,
            )
            outcomes.append((relative, role, action))

        for item in remove_items:
            remove_tracked_file(target, item["path"], target_descriptor)
            outcomes.append((item["path"], item["role"], "removed"))

        for relative, content in proposals:
            write_text_file(
                target / relative,
                content,
                target,
                force=True,
                dry_run=False,
                target_descriptor=target_descriptor,
            )

        applied = {
            relative: action for relative, role, action in outcomes if action != "skipped"
        }
        stamp = updated_stamp_after_apply(
            target,
            stamp,
            version,
            apply_items,
            add_items,
            remove_items,
            conflict_items,
            applied,
            profiles,
        )
        write_stamp_file(target, stamp, target_descriptor)
    except (AdoptionError, OSError, UnicodeError) as exc:
        return fail(f"upgrade stopped during a safe write; the target may contain partial changes: {exc}")
    finally:
        if target_descriptor is not None:
            os.close(target_descriptor)

    for relative, _role, action in outcomes:
        print(f"{action} {relative}")
    for relative, _content in proposals:
        print(f"proposal {relative}")
    print()
    if conflict_items:
        print(
            f"next: resolve proposals under {target / PROPOSAL_DIRECTORY / version}, "
            "then run 'upgrade <target> --complete'"
        )
    elif storage_mode == "private":
        print(
            "next: private storage - keep all Trellium material untracked and covered by the"
            " trellium-private block in .git/info/exclude; never commit Trellium material;"
            " re-run check to confirm the boundary"
        )
    else:
        print("next: commit this upgrade as a standalone, revertable change")
    return EXIT_CONFLICT if conflict_items else 0


def adopt_project(args: argparse.Namespace) -> int:
    try:
        target = Path(args.target).expanduser().resolve()
        target_exists = target.exists()
        previous_stamp = read_stamp(target) if target_exists else None
        previous_profiles = selections_from_stamp(previous_stamp)
        profiles = parse_profile_selections(args.profile) if args.profile else previous_profiles
        if args.profile and previous_profiles and profiles != previous_profiles:
            raise AdoptionError(
                "profile selections differ from the existing adoption stamp; "
                "adopt will not rewrite project-owned rules -- preserve the recorded selection "
                "or migrate it through an explicit reviewed change"
            )
    except (OSError, RuntimeError) as exc:
        return fail(f"could not resolve adoption target: {exc}")
    except AdoptionError as exc:
        return fail(str(exc))

    if target == Path(target.anchor):
        return fail(f"refusing to adopt into filesystem root: {target}")
    if not target_exists and not args.create:
        return fail(f"target does not exist: {target}")
    if target_exists and target_storage_mode(target) == "private":
        try:
            private_preflight(target, profiles=tuple(item["id"] for item in profiles))
        except AdoptionError as exc:
            return fail(str(exc))
    try:
        if target_exists and not target.is_dir():
            return fail(f"target is not a directory: {target}")
    except OSError as exc:
        return fail(f"could not inspect adoption target: {exc}")

    if not TEMPLATES_ROOT.is_dir():
        return fail(f"template directory does not exist: {TEMPLATES_ROOT}")

    destinations = [target / "AGENTS.md"]
    destinations.extend(target / relative for relative in TEMPLATE_FILES)
    destinations.extend(target / relative for relative in RENDERED_FILES)
    if profiles:
        destinations.append(target / PROFILE_RULES_RELATIVE)
        destinations.extend(
            target / profile_document_relative(profile["id"]) for profile in profiles
        )

    target_descriptor: int | None = None
    if target_exists and not args.dry_run and ANCHORED_WRITES_SUPPORTED:
        try:
            target_descriptor = open_target_directory(target, create=False)
        except (AdoptionError, OSError) as exc:
            return fail(f"could not securely open adoption target: {exc}")

    try:
        validate_template_sources(("AGENTS.md", *TEMPLATE_FILES))
        if profiles:
            profile_template_sections()
            for profile in profiles:
                render_durable_profile(profile)
        validate_output_paths(target, destinations)
    except (AdoptionError, OSError, RuntimeError) as exc:
        if target_descriptor is not None:
            os.close(target_descriptor)
        return fail(str(exc))

    if not target_exists:
        print_action(args.dry_run, f"create directory {target}")
        if not args.dry_run:
            if ANCHORED_WRITES_SUPPORTED:
                try:
                    target_descriptor = open_target_directory(target, create=True)
                except (AdoptionError, OSError) as exc:
                    return fail(f"could not securely create adoption target: {exc}")
            else:
                try:
                    target.mkdir(parents=True)
                except OSError as exc:
                    return fail(f"could not create adoption target: {exc}")

    rendered_files = {
        "vault/project.md": render_project(target, target_descriptor),
        "vault/runtime.md": render_runtime(target),
    }
    if profiles:
        rendered_files[PROFILE_RULES_RELATIVE] = render_profile_document(profiles)
        for profile in profiles:
            rendered_files[profile_document_relative(profile["id"])] = render_durable_profile(profile)

    changed: list[str] = []
    skipped: list[str] = []
    actions: dict[str, str] = {}
    try:
        agent_result = append_agent_entry(target, args.dry_run, target_descriptor)
        (changed if agent_result in {"create", "updated"} else skipped).append("AGENTS.md")
        actions["AGENTS.md"] = agent_result

        for relative in TEMPLATE_FILES:
            result = copy_file(
                template_source(relative),
                target / relative,
                target,
                force=args.force,
                dry_run=args.dry_run,
                target_descriptor=target_descriptor,
            )
            (changed if result != "skipped" else skipped).append(relative)
            actions[relative] = result

        for relative, content in rendered_files.items():
            result = write_text_file(
                target / relative,
                content,
                target,
                # Profile rules are project-owned engineering knowledge. Even
                # `adopt --force` must not silently replace an existing file.
                force=args.force
                and relative != PROFILE_RULES_RELATIVE
                and not is_profile_document_relative(relative),
                dry_run=args.dry_run,
                target_descriptor=target_descriptor,
            )
            (changed if result != "skipped" else skipped).append(relative)
            actions[relative] = result

        if not args.dry_run:
            write_adoption_stamp(target, actions, rendered_files, profiles, target_descriptor)
    except (AdoptionError, OSError, UnicodeError) as exc:
        return fail(f"adoption stopped during a safe write; the target may contain partial changes: {exc}")
    finally:
        if target_descriptor is not None:
            os.close(target_descriptor)

    print()
    print(f"adoption target: {target}")
    print(f"changed: {len(changed)}")
    for item in changed:
        print(f"  - {item}")
    if skipped:
        print(f"skipped existing files: {len(skipped)}")
        for item in skipped:
            print(f"  - {item}")
    print("generated does not mean durable: whether the collaboration core is persisted is a Git HEAD fact, decided by a commit and confirmed by check, not by this run")
    print("adoption durability checklist (apply applicable steps in order):")
    print("  1. review the proposed or existing collaboration files with the user and finish semantic configuration: mode choice, TASK storage decision, merging any existing agent entry")
    print("  2. for tracked storage, ensure the collaboration core is present in Git HEAD (AGENTS.md, vault/, skills/agent-task/SKILL.md, vault/.agent-init.json); adopt never runs git add/commit/push - commits stay under the user's control")
    print("  3. for tracked storage, after the commit, re-run: python3 trellium.py check <target> - adoption is complete only with 0 errors (core paths present in Git HEAD, not ignored)")
    print("  4. for local or production adoptions, verify a fresh clone of the repository passes check too")
    print("  5. for private adoptions (storage_mode=private), never commit Trellium material: keep everything untracked and covered by the trellium-private block in .git/info/exclude, then re-run check; adoption is complete only with 0 errors")
    print("later upgrades: python3 trellium.py diff <target>")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Adopt Trellium into a target project.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    content_options = argparse.ArgumentParser(add_help=False)
    content_options.add_argument(
        "--templates", metavar="DIR", help="override the template directory (VERSION stays with the running script)"
    )
    content_options.add_argument(
        "--fetch",
        action="store_true",
        help="fetch the latest tagged release from GitHub and run it instead of the bundled content",
    )

    adopt = subparsers.add_parser(
        "adopt", help="add Agent collaboration files to a project", parents=[content_options]
    )
    adopt.add_argument("target", nargs="?", default=".", help="target project directory")
    adopt.add_argument("--create", action="store_true", help="create target directory if missing")
    adopt.add_argument("--force", action="store_true", help="replace existing generated files")
    adopt.add_argument("--dry-run", action="store_true", help="print actions without writing")
    adopt.add_argument(
        "--profile",
        action="append",
        default=[],
        metavar="PROFILE[=ROOT]",
        help=(
            "select a language profile and target-relative root; repeat for multiple roots or languages "
            f"({', '.join(PROFILE_IDS)})"
        ),
    )
    adopt.set_defaults(func=adopt_project)

    baseline = subparsers.add_parser(
        "baseline", help="record an adoption stamp for an existing vault adopted before versioning"
    )
    baseline.add_argument("target", nargs="?", default=".", help="target project directory")
    baseline.set_defaults(func=baseline_project)

    report = subparsers.add_parser(
        "diff", help="report drift between an adopted project and the current templates", parents=[content_options]
    )
    report.add_argument("target", nargs="?", default=".", help="target project directory")
    report.set_defaults(func=diff_project)

    upgrade = subparsers.add_parser(
        "upgrade",
        help="refresh protocol files in an adopted project while preserving project data",
        parents=[content_options],
    )
    upgrade.add_argument("target", nargs="?", default=".", help="target project directory")
    upgrade.add_argument(
        "--apply", action="store_true", help="execute the safe subset (apply/add/remove); conflicts produce proposals"
    )
    upgrade.add_argument(
        "--complete", action="store_true", help="finalize proposals resolved by the agent and the user"
    )
    upgrade.add_argument(
        "--skip", action="append", default=[], metavar="PATH", help="exclude a path from this upgrade round"
    )
    upgrade.add_argument(
        "--only", action="append", default=[], metavar="PATH", help="restrict this upgrade round to the given paths"
    )
    upgrade.add_argument(
        "--allow-dirty", action="store_true", help="proceed even when files to touch have uncommitted changes"
    )
    upgrade.set_defaults(func=upgrade_project)

    check = subparsers.add_parser(
        "check",
        help="read-only validation of task state blocks, policy, budgets, and TASK storage",
    )
    check.add_argument("target", nargs="?", default=".", help="target project directory")
    check.add_argument(
        "--format",
        default="text",
        help="output format: text or json (default: text)",
    )
    check.set_defaults(func=check_project)

    status = subparsers.add_parser(
        "status",
        help="read-only owner summary: navigation focus, canonical task state, closed counts, and unresolved tasks",
    )
    status.add_argument("target", nargs="?", default=".", help="target project directory")
    status.add_argument(
        "--format",
        default="text",
        help="output format: text or json (default: text)",
    )
    status.set_defaults(func=status_project)

    return parser


def main(argv: list[str] | None = None) -> int:
    global TEMPLATES_ROOT
    arguments = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(arguments)
    original_templates_root = TEMPLATES_ROOT
    if getattr(args, "templates", None):
        TEMPLATES_ROOT = Path(args.templates).expanduser().resolve()
    try:
        if getattr(args, "fetch", False):
            forwarded = [argument for argument in arguments if argument != "--fetch"]
            return fetch_and_run(args, forwarded)
        return args.func(args)
    finally:
        # Keep repeated in-process invocations (tests) from inheriting the override.
        TEMPLATES_ROOT = original_templates_root


if __name__ == "__main__":
    raise SystemExit(main())
