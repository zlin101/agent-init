#!/bin/sh
# Assemble the TASK-0026 profile ablation before/after replay workspaces.
#
# Deterministic inputs:
#   - fixture sources from ./fixtures (this directory)
#   - profile variant "a" (before) =
#       git show $BASE_SHA:init/protocol/profiles/<lang>-backend.md
#   - profile variant "b" (after)  =
#       current worktree init/protocol/profiles/<lang>-backend.md
#   $BASE_SHA is pinned to the pre-ablation commit, NOT floating HEAD: after
#   this task is committed, `HEAD:...` would resolve to the after-profile and
#   silently collapse the ablation. sha256(before/after) per language is
#   recorded in profiles.sha256 (next to protocol.md and in the built root).
#
# Safety: this script only CREATES a new directory. It refuses an existing
# target and never removes anything (no rm -rf anywhere).
#
# Usage: sh build-replay.sh [target-dir] [scenario ...]
#   target-dir  must not exist; default is a fresh mktemp -d directory
#   scenario    one or more of s1 s2 s3 s4 s5; default: all
set -eu

EVIDENCE=$(cd -- "$(dirname -- "$0")" && pwd)
REPO=$(cd -- "$EVIDENCE/../../.." && pwd)

# Pre-ablation baseline commit (HEAD at the time the replay was constructed).
# Pinned deliberately; update only together with protocol.md.
BASE_SHA=a01950a1afab092ae4296b29a00c1b9da74fd7ab

scenario_lang() {
    case $1 in
        s2 | s5) echo python ;;
        *) echo go ;;
    esac
}

scenario_fixture() {
    case $1 in
        s1) echo s1-shop-api ;;
        s2) echo s2-inventory-svc ;;
        s3) echo s3-mono ;;
        s4) echo s4-worker ;;
        s5) echo s5-catalog-api ;;
        *) echo "" ;;
    esac
}

if [ $# -gt 0 ]; then
    ROOT=$1
    shift
    if [ -e "$ROOT" ]; then
        echo "build-replay: refusing existing target: $ROOT" >&2
        echo "build-replay: this script only creates new directories; it never overwrites or deletes" >&2
        exit 2
    fi
else
    ROOT=$(mktemp -d "${TMPDIR:-/tmp}/trellium-0026-replay.XXXXXX")
fi

if [ $# -gt 0 ]; then
    SCENARIOS=$*
else
    SCENARIOS="s1 s2 s3 s4 s5"
fi

for sc in $SCENARIOS; do
    fixture=$(scenario_fixture "$sc")
    if [ -z "$fixture" ]; then
        echo "build-replay: unknown scenario: $sc (want s1..s5)" >&2
        exit 2
    fi
    if [ ! -d "$EVIDENCE/fixtures/$fixture" ]; then
        echo "build-replay: missing fixture for $sc: $EVIDENCE/fixtures/$fixture" >&2
        exit 2
    fi
done

mkdir -p "$ROOT"
: > "$ROOT/map.tsv"

# Record both sides' profile inputs so any rerun can prove which Profile was
# used for "before" and "after".
{
    for lg in go python; do
        printf 'before\t%s\t' "$lg"
        git -C "$REPO" show "$BASE_SHA:init/protocol/profiles/$lg-backend.md" |
            sha256sum | awk '{print $1}'
        printf 'after\t%s\t' "$lg"
        sha256sum "$REPO/init/protocol/profiles/$lg-backend.md" | awk '{print $1}'
    done
} >"$ROOT/profiles.sha256"
cp "$ROOT/profiles.sha256" "$EVIDENCE/profiles.sha256"

for sc in $SCENARIOS; do
    for v in a b; do
        dir="$ROOT/$sc$v"
        mkdir -p "$dir"
        (
            cd "$EVIDENCE/fixtures/$(scenario_fixture "$sc")"
            tar -cf - --exclude=.venv --exclude=__pycache__ --exclude=.pytest_cache .
        ) | (cd "$dir" && tar -xf -)
        git -C "$dir" init -q
        git -C "$dir" add -A
        git -C "$dir" -c user.name=replay -c user.email=replay@local \
            -c commit.gpgsign=false commit -qm "fixture baseline"
        if [ "$v" = a ]; then
            git -C "$REPO" show "$BASE_SHA:init/protocol/profiles/$(scenario_lang "$sc")-backend.md" >"$dir/AGENTS.md"
        else
            cp "$REPO/init/protocol/profiles/$(scenario_lang "$sc")-backend.md" "$dir/AGENTS.md"
        fi
        git -C "$dir" add AGENTS.md
        git -C "$dir" -c user.name=replay -c user.email=replay@local \
            -c commit.gpgsign=false commit -qm "project profile"
        printf '%s\t%s\t%s\n' "$sc$v" "$(scenario_lang "$sc")" "$(git -C "$dir" rev-parse HEAD)" >>"$ROOT/map.tsv"
    done
done

# S5 both sides get a synced environment so the repo's documented test entry runs.
case " $SCENARIOS " in
    *" s5 "*)
        for v in a b; do
            (cd "$ROOT/s5$v" && uv sync -q)
        done
        ;;
esac

echo "built: $ROOT (base $BASE_SHA)"
cat "$ROOT/map.tsv"
cat "$ROOT/profiles.sha256"
