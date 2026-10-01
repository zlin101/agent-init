#!/usr/bin/env python3
"""Mirror the canonical init protocol and updater script into distributable Skill packages."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "init"
DEFAULT_TARGETS = (
    REPO_ROOT / "skills/trellium-zh/references/protocol-source",
    REPO_ROOT / "skills/trellium/references/protocol-source",
)
EMBEDDED_SCRIPT_SOURCE = REPO_ROOT / "scripts" / "trellium.py"
EMBEDDED_SCRIPT_RELATIVE = "assets/trellium.py"
EMBEDDED_STORE_SOURCE = REPO_ROOT / "scripts" / "history_store.py"
EMBEDDED_STORE_RELATIVE = "assets/history_store.py"
ZH_PACKAGE_ROOT = REPO_ROOT / "skills/trellium-zh"
ZH_PROFILE_TEMPLATE_ROOT = ZH_PACKAGE_ROOT / "assets/templates/docs/engineering/profiles"
MANIFEST_NAME = "manifest.json"


class SyncError(Exception):
    pass


def collect_source_files(source: Path) -> dict[str, bytes]:
    if not source.is_dir():
        raise SyncError(f"source directory does not exist: {source}")

    files: dict[str, bytes] = {}
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise SyncError(f"source symlinks are not supported: {path}")
        if path.is_file():
            relative = path.relative_to(source).as_posix()
            files[relative] = path.read_bytes()

    if not files:
        raise SyncError(f"source directory is empty: {source}")
    return files


def source_digest(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for relative, content in sorted(files.items()):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(content)
        digest.update(b"\0")
    return digest.hexdigest()


def expected_files(source: Path) -> dict[str, bytes]:
    source_files = collect_source_files(source)
    files = {f"{source.name}/{relative}": content for relative, content in source_files.items()}
    manifest = {
        "generated_by": "scripts/sync-skills.py",
        "source": source.name,
        "source_file_count": len(source_files),
        "source_sha256": source_digest(source_files),
    }
    files[MANIFEST_NAME] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return files


def collect_target_files(target: Path) -> dict[str, bytes]:
    if not target.is_dir():
        return {}

    files: dict[str, bytes] = {}
    for path in sorted(target.rglob("*")):
        if path.is_symlink():
            raise SyncError(f"generated snapshot must not contain symlinks: {path}")
        if path.is_file():
            files[path.relative_to(target).as_posix()] = path.read_bytes()
    return files


def describe_drift(expected: dict[str, bytes], actual: dict[str, bytes]) -> list[str]:
    expected_names = set(expected)
    actual_names = set(actual)
    messages = [f"missing {name}" for name in sorted(expected_names - actual_names)]
    messages.extend(f"unexpected {name}" for name in sorted(actual_names - expected_names))
    messages.extend(
        f"changed {name}"
        for name in sorted(expected_names & actual_names)
        if expected[name] != actual[name]
    )
    return messages


def validate_target(source: Path, target: Path) -> None:
    if target.is_symlink():
        raise SyncError(f"target symlinks are not supported: {target}")
    if target.exists() and not target.is_dir():
        raise SyncError(f"target is not a directory: {target}")

    source_resolved = source.resolve()
    target_resolved = target.resolve()
    if target_resolved == source_resolved or source_resolved in target_resolved.parents:
        raise SyncError(f"target must not be inside source: {target}")


def write_snapshot(target: Path, files: dict[str, bytes]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.parent / f".{target.name}.tmp"
    backup = target.parent / f".{target.name}.backup"

    try:
        if staging.exists():
            shutil.rmtree(staging)
        if backup.exists():
            shutil.rmtree(backup)
    except OSError as exc:
        raise SyncError(f"could not clean staging area for {target}: {exc}") from exc

    try:
        for relative, content in files.items():
            destination = staging / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)

        if target.exists():
            target.rename(backup)
        staging.rename(target)
        if backup.exists():
            shutil.rmtree(backup)
    except Exception:
        if target.exists() and backup.exists():
            shutil.rmtree(target)
        if backup.exists():
            backup.rename(target)
        if staging.exists():
            shutil.rmtree(staging)
        raise


def embedded_script_drift(package_root: Path) -> list[str]:
    """Report drift between scripts/trellium.py and its embedded copy."""
    return _embedded_module_drift(package_root, EMBEDDED_SCRIPT_SOURCE, EMBEDDED_SCRIPT_RELATIVE)


def embedded_store_drift(package_root: Path) -> list[str]:
    """Report drift between scripts/history_store.py and its embedded copy."""
    return _embedded_module_drift(package_root, EMBEDDED_STORE_SOURCE, EMBEDDED_STORE_RELATIVE)


def _embedded_module_drift(package_root: Path, source: Path, relative: str) -> list[str]:
    destination = package_root / relative
    try:
        actual = destination.read_bytes()
    except OSError:
        return [f"missing {relative}"]
    expected = source.read_bytes()
    if actual != expected:
        return [f"changed {relative}"]
    return []


def derived_profile_drift(package_root: Path) -> list[str]:
    """Keep Chinese durable-profile templates byte-identical to canonical init profiles."""
    if package_root != ZH_PACKAGE_ROOT:
        return []
    messages: list[str] = []
    source_root = DEFAULT_SOURCE / "protocol/profiles"
    for profile_id in ("go-backend", "python-backend"):
        source = source_root / f"{profile_id}.md"
        destination = ZH_PROFILE_TEMPLATE_ROOT / f"{profile_id}.md"
        try:
            if destination.read_bytes() != source.read_bytes():
                messages.append(f"changed assets/templates/docs/engineering/profiles/{profile_id}.md")
        except OSError:
            messages.append(f"missing assets/templates/docs/engineering/profiles/{profile_id}.md")
    return messages


def write_embedded_script(package_root: Path) -> None:
    destination = package_root / EMBEDDED_SCRIPT_RELATIVE
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(EMBEDDED_SCRIPT_SOURCE.read_bytes())


def write_embedded_store(package_root: Path) -> None:
    destination = package_root / EMBEDDED_STORE_RELATIVE
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(EMBEDDED_STORE_SOURCE.read_bytes())


def write_derived_profiles(package_root: Path) -> None:
    if package_root != ZH_PACKAGE_ROOT:
        return
    ZH_PROFILE_TEMPLATE_ROOT.mkdir(parents=True, exist_ok=True)
    for profile_id in ("go-backend", "python-backend"):
        shutil.copyfile(
            DEFAULT_SOURCE / "protocol/profiles" / f"{profile_id}.md",
            ZH_PROFILE_TEMPLATE_ROOT / f"{profile_id}.md",
        )


def sync(source: Path, targets: list[Path], check: bool) -> int:
    expected = expected_files(source)
    drift_found = False

    for target in targets:
        validate_target(source, target)
        drift = describe_drift(expected, collect_target_files(target))
        package_root = target.parents[1]
        drift.extend(embedded_script_drift(package_root))
        drift.extend(embedded_store_drift(package_root))
        drift.extend(derived_profile_drift(package_root))
        if check:
            if drift:
                drift_found = True
                print(f"out of sync: {target}", file=sys.stderr)
                for message in drift:
                    print(f"  - {message}", file=sys.stderr)
            else:
                print(f"in sync: {target}")
            continue

        write_snapshot(target, expected)
        write_embedded_script(package_root)
        write_embedded_store(package_root)
        write_derived_profiles(package_root)
        print(f"synced {len(expected) - 1} source files and the updater script to {target}")

    if check and drift_found:
        print(
            "Protocol snapshots are out of sync with init/.\n"
            "Fix: run `python3 scripts/sync-skills.py` and commit the regenerated\n"
            "files under skills/*/references/protocol-source/. CI runs the same check.",
            file=sys.stderr,
        )

    return 1 if drift_found else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report drift without writing files")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="canonical protocol directory")
    parser.add_argument(
        "--target",
        action="append",
        type=Path,
        help="snapshot destination; repeat for multiple Skill packages",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    targets = args.target or list(DEFAULT_TARGETS)
    try:
        return sync(args.source.resolve(), [target.resolve() for target in targets], args.check)
    except (OSError, SyncError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
