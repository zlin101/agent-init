#!/bin/sh
# Build TASK-0028 hot-path routing replay fixtures (S1 canary set: a1/b/c × pre/post).
#
# Safety: creates only NEW directories; refuses existing targets; never removes
# anything. Every fixture is a local clone pinned to the frozen baseline commit.
#
# Inputs (frozen in ../protocol.md):
#   PIN          pre-S1 baseline commit
#   side pre     AGENTS/index/runtime as at PIN (clone state, untouched)
#   side post    current worktree AGENTS/index/runtime (post-S1)
#   overlays     per-case minimal materials (shared by both sides)
#
# Usage: sh build-fixtures.sh <target-parent-dir> [case ...]
#   case: a1 b c (default: all)
set -eu

EVIDENCE=$(cd -- "$(dirname -- "$0")" && pwd)
REPO=$(cd -- "$EVIDENCE/../../.." && pwd)
PIN=77ee0224dc75d18fcdc0f88e67b0faa100e8635a
PROFILE_GO=$REPO/init/protocol/profiles/go-backend.md
PROFILE_PY=$REPO/init/protocol/profiles/python-backend.md
POLICY_DOC=$REPO/docs/evals/profile-knowledge-ablation-2026-09/fixtures/s5-catalog-api/docs/engineering/code-comments.md

if [ $# -lt 1 ]; then
    echo "usage: build-fixtures.sh <target-parent-dir> [case ...]" >&2
    exit 2
fi
ROOT=$1
shift
if [ -e "$ROOT" ]; then
    echo "build-fixtures: refusing existing target: $ROOT" >&2
    exit 2
fi
if [ $# -gt 0 ]; then
    CASES=$*
else
    CASES="a1 b c"
fi
for c in $CASES; do
    case $c in
        a1 | b | c) ;;
        *)
            echo "build-fixtures: unknown case: $c (want a1|b|c)" >&2
            exit 2
            ;;
    esac
done

mkdir -p "$ROOT"
: >"$ROOT/fixture-manifest.txt"

record() {
    printf '%s\t%s\t%s\n' "$1" "$2" "$3" >>"$ROOT/fixture-manifest.txt"
}

commit_overlay() {
    dir=$1
    git -C "$dir" add -A
    git -C "$dir" -c user.name=replay -c user.email=replay@local \
        -c commit.gpgsign=false commit -qm "fixture overlay: $2"
    record "$(basename "$dir")" "head" "$(git -C "$dir" rev-parse HEAD)"
}

apply_common() {
    dir=$1
    side=$2
    mkdir -p "$dir/docs/engineering/profiles"
    cp "$PROFILE_GO" "$dir/docs/engineering/profiles/go-backend.md"
    cp "$PROFILE_PY" "$dir/docs/engineering/profiles/python-backend.md"
    cp "$POLICY_DOC" "$dir/docs/engineering/code-comments.md"
    # S1 只变 index：AGENTS 本轮未改（worktree == pin），runtime 两侧都取
    # worktree 起点（Codex round-3 导航先于 S1，不是本轮变量）。
    cp "$REPO/AGENTS.md" "$dir/AGENTS.md"
    cp "$REPO/vault/runtime.md" "$dir/vault/runtime.md"
    if [ "$side" = post ]; then
        cp "$REPO/vault/index.md" "$dir/vault/index.md"
    fi
    record "$(basename "$dir")" "agents" "$(sha256sum "$dir/AGENTS.md" | awk '{print $1}')"
    record "$(basename "$dir")" "index" "$(sha256sum "$dir/vault/index.md" | awk '{print $1}')"
    record "$(basename "$dir")" "runtime" "$(sha256sum "$dir/vault/runtime.md" | awk '{print $1}')"
}

overlay_a1() {
    dir=$1
    sed -i "0,/Trellium/s//Trelium/" "$dir/README.md"
    grep -q "Trelium" "$dir/README.md" || {
        echo "build-fixtures: README typo injection failed" >&2
        exit 1
    }
    mkdir -p "$dir/internal/httpapi"
    cat >"$dir/internal/httpapi/router.go" <<'GOEOF'
package httpapi

import "net/http"

// versionHandler returns the build version string for the /version route.
func versionHandler(version string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/plain; charset=utf-8")
		_, _ = w.Write([]byte("verison " + version))
	}
}
GOEOF
    grep -q "verison" "$dir/internal/httpapi/router.go" || {
        echo "build-fixtures: go typo injection failed" >&2
        exit 1
    }
}

overlay_b() {
    dir=$1
    cat >"$dir/vault/tasks/TASK-0100-install-dry-run.md" <<'TBEOF'
# TASK-0100 - install.sh --dry-run support

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0100",
  "level": "B",
  "authority_level": 2,
  "lifecycle": "active",
  "current_slice": "parser-wired-output-pending",
  "gates": {
    "plan": "passed",
    "implementation": "in_progress",
    "tests": "pending"
  }
}
-->

## Objective

为 `install.sh` 增加 `--dry-run`：解析完成后、任何执行动作之前打印将要执行的动作计划，不触网、不写文件。

## Scope

In scope：`install.sh` 的 dry-run 分支与聚焦测试。

Out of scope：改变默认安装行为、网络协议、`--version` 失败关闭语义。

## Authority

Allowed：修改 `install.sh` 及其聚焦测试。

Requires approval：改变默认安装行为或网络路径。

Forbidden：移除显式 `--version` 失败关闭语义；未经确认改变输出契约。

## Acceptance Criteria

- [ ] 缺 `--version` 时仍 fail-closed，与 dry-run 无关。
- [ ] `--dry-run` 只打印计划，零执行。
- [ ] 聚焦测试覆盖两个分支。
TBEOF
    cat >>"$dir/vault/handoff.md" <<'HBEOF'

## TASK-0100

### Why interrupted

Session ended mid-implementation after discovering that `--dry-run` must reuse the existing flag parser instead of a second pass.

### Transient context not captured elsewhere

`install.sh` rejects unknown flags before any network path is reached; the dry-run plan must be produced after parsing and before execution. The `test_version_required` flake seen earlier was environmental (port reuse) and unrelated.

### Exact resume point

`print_plan()` is defined at the end of `install.sh` but not wired; the `--dry-run` branch still needs to call it after parsing, and the focused test file has not been touched.
HBEOF
    cat >>"$dir/install.sh" <<'SHEOF'

print_plan() {
    printf 'plan: version=%s\n' "${VERSION:-unset}"
}
SHEOF
}

overlay_c() {
    dir=$1
    mkdir -p "$dir/docs"
    cat >"$dir/docs/schema.sql" <<'SQLEOF'
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    total_cents INTEGER NOT NULL
);
SQLEOF
}

for c in $CASES; do
    for side in pre post; do
        dir="$ROOT/$c-$side"
        if [ -e "$dir" ]; then
            echo "build-fixtures: refusing existing target: $dir" >&2
            exit 2
        fi
        git clone -q --local "$REPO" "$dir"
        git -C "$dir" checkout -q "$PIN"
        actual=$(git -C "$dir" rev-parse HEAD)
        if [ "$actual" != "$PIN" ]; then
            echo "build-fixtures: pin mismatch in $dir: $actual" >&2
            exit 1
        fi
        apply_common "$dir" "$side"
        case $c in
            a1) overlay_a1 "$dir" ;;
            b) overlay_b "$dir" ;;
            c) overlay_c "$dir" ;;
        esac
        commit_overlay "$dir" "$c/$side"
    done
done

echo "built: $ROOT"
cat "$ROOT/fixture-manifest.txt"
