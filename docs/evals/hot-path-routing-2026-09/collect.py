#!/usr/bin/env python3
"""Collect TASK-0028 replay evidence per run.

For every row of runs-map.tsv (key, fixture_dir, session_jsonl):
  1. runs/<key>-changes.patch  - full working-tree diff vs the fixture's
     baseline commit (new files staged into a TEMPORARY index).
  2. runs/<key>-changes-full.patch - forced-add snapshot including paths the
     fixture's root .gitignore ignores (pycache/venv excluded).
  3. runs/<key>-reads.txt      - every tool call from the agent session.

Zero-write guarantee: all git index operations run with GIT_INDEX_FILE
pointing at a per-row temp path, so the fixture's real .git/index (and any
pre-existing staged state) is never modified — on success or on failure.
Publish guarantee: a row's evidence files are written only after EVERY step
of that row (diff, forced-add diff, reads parsing) has succeeded; a mid-row
failure publishes nothing for that key (see collect-selftest.txt).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parent
# Overridable so the zero-write self-test (collect-selftest.txt) never touches
# the real runs/ evidence or the real runs-map.tsv.
RUNS = Path(os.environ.get("COLLECT_RUNS") or (EVIDENCE / "runs"))
MAP = Path(os.environ.get("COLLECT_MAP") or (EVIDENCE / "runs-map.tsv"))


def tool_events(session: Path) -> list[str]:
    events: list[str] = []
    for line in session.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        _walk(obj, events)
    return events


def _walk(obj, events: list[str]) -> None:
    if isinstance(obj, dict):
        name = obj.get("name")
        if isinstance(name, str) and name in {
            "read",
            "write",
            "edit",
            "bash",
            "grep",
            "find",
            "ls",
            "glob",
            "ast_grep_search",
            "contact_supervisor",
            "subagent_supervisor",
        }:
            args = obj.get("args") or obj.get("arguments") or {}
            events.append(name + "\t" + json.dumps(args, ensure_ascii=False, sort_keys=True))
        for value in obj.values():
            _walk(value, events)
    elif isinstance(obj, list):
        for item in obj:
            _walk(item, events)


def git(d: Path, *args: str, index_file: Path | None = None) -> subprocess.CompletedProcess:
    """Run git with an optional redirect index.

    When ``index_file`` is set, every index read/write goes to that path
    (GIT_INDEX_FILE) — the fixture's real ``.git/index`` is never touched, so
    existing staged state survives and a failure mid-run cannot leave staging
    debris behind.
    """
    env = dict(os.environ)
    if index_file is not None:
        env["GIT_INDEX_FILE"] = str(index_file)
    return subprocess.run(
        ["git", "-C", str(d), *args],
        check=True,
        capture_output=True,
        env=env,
    )


def staged_paths(d: Path) -> list[str]:
    out = git(d, "diff", "--cached", "--name-only").stdout.decode("utf-8", "replace")
    return [ln for ln in out.splitlines() if ln.strip()]


def main() -> int:
    if not MAP.is_file():
        print(f"collect: missing {MAP}", file=sys.stderr)
        return 2
    rows = [ln.split("\t") for ln in MAP.read_text(encoding="utf-8").splitlines() if ln.strip()]
    header, rows = rows[0], rows[1:]
    if header[:3] != ["key", "fixture_dir", "session_jsonl"]:
        print(f"collect: bad header: {header}", file=sys.stderr)
        return 2
    if not rows:
        print("collect: no rows", file=sys.stderr)
        return 2
    RUNS.mkdir(exist_ok=True)
    failures = 0
    for key, fixture_dir, session in rows:
        tmpdir = Path(tempfile.mkdtemp(prefix="collect-idx-"))
        try:
            d = Path(fixture_dir)
            s = Path(session)
            if not d.is_dir() or not (d / ".git").is_dir():
                raise FileNotFoundError(f"fixture git dir missing: {d}")
            if not s.is_file():
                raise FileNotFoundError(f"session missing: {s}")
            # ---- compute everything for this row first -----------------
            idx = tmpdir / "index"
            git(d, "read-tree", "HEAD", index_file=idx)
            git(d, "add", "-A", index_file=idx)
            diff = git(d, "diff", "--binary", "HEAD", index_file=idx).stdout
            # The fixture clones carry this repo's root .gitignore (`/*` plus
            # selective negations): fixture service files (internal/, cmd/,
            # go.mod, Makefile, RUNLOG.md, ...) are untracked+ignored, so the
            # tracked-only diff above misses them. A forced-add snapshot keeps
            # their full post-state as additions (baseline content stays
            # documented in the builders' heredocs/inputs).
            git(
                d,
                "add",
                "-f",
                "-A",
                "--",
                ".",
                ":(exclude,glob)**/__pycache__/**",
                ":(exclude,glob)**/*.pyc",
                ":(exclude,glob)**/.venv/**",
                index_file=idx,
            )
            full = git(d, "diff", "--binary", "HEAD", index_file=idx).stdout
            events = tool_events(s)
            if os.environ.get("COLLECT_PROBE_FAIL_AFTER_DIFF"):
                raise RuntimeError("probe: injected failure after diffs, before publish")
            # ---- publish only after the whole row succeeded -------------
            (RUNS / f"{key}-changes.patch").write_bytes(diff)
            (RUNS / f"{key}-changes-full.patch").write_bytes(full)
            (RUNS / f"{key}-reads.txt").write_text(
                "\n".join(events) + ("\n" if events else ""),
                encoding="utf-8",
            )
            print(f"{key}: {len(diff)} tracked / {len(full)} full diff bytes, {len(events)} tool events")
        except Exception as exc:  # noqa: BLE001 - aggregate and report
            failures += 1
            print(f"{key}: COLLECT FAIL: {exc}", file=sys.stderr)
        finally:
            # Only our own temp dir is removed; the fixture tree and its real
            # index are never modified.
            shutil.rmtree(tmpdir, ignore_errors=True)
    if failures:
        print(f"collect: {failures} row(s) failed", file=sys.stderr)
        return 1
    print("collect: all rows collected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
