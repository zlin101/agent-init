#!/bin/sh
# Build TASK-0028 S3 replay fixtures (runtime present-tense ablation):
#   b3-post : B-continuation fixture with POST-cleanup runtime
#             (B control = already-frozen S1 b-post run: same overlays,
#              AGENTS/index, and PRE-cleanup runtime — reused, not rerun)
#   r-pre   : R traceability fixture with PRE-cleanup runtime (M0 snapshot)
#   r-post  : R fixture with POST-cleanup runtime
#
# Safety: creates only NEW directories; refuses existing targets; never removes.
#
# Usage: sh build-s3.sh <target-parent-dir>
set -eu

EVIDENCE=$(cd -- "$(dirname -- "$0")" && pwd)
REPO=$(cd -- "$EVIDENCE/../../.." && pwd)
PIN=77ee0224dc75d18fcdc0f88e67b0faa100e8635a
PRE_RUNTIME=/tmp/trellium-0028-m0/vault/runtime.md
POST_RUNTIME=$REPO/vault/runtime.md
PROFILE_GO=$REPO/init/protocol/profiles/go-backend.md
PROFILE_PY=$REPO/init/protocol/profiles/python-backend.md
POLICY_DOC=$REPO/docs/evals/profile-knowledge-ablation-2026-09/fixtures/s5-catalog-api/docs/engineering/code-comments.md

if [ $# -lt 1 ]; then
    echo "usage: build-s3.sh <target-parent-dir>" >&2
    exit 2
fi
ROOT=$1
if [ -e "$ROOT" ]; then
    echo "build-s3: refusing existing target: $ROOT" >&2
    exit 2
fi
[ -f "$PRE_RUNTIME" ] || {
    echo "build-s3: missing M0 pre-runtime snapshot: $PRE_RUNTIME" >&2
    exit 1
}
mkdir -p "$ROOT"
: >"$ROOT/fixture-manifest.txt"
record() { printf '%s\t%s\t%s\n' "$1" "$2" "$3" >>"$ROOT/fixture-manifest.txt"; }

for spec in "b3-post worktree" "r-pre pre" "r-post worktree"; do
    name=${spec% *}
    runtime_kind=${spec#* }
    dir="$ROOT/$name"
    if [ -e "$dir" ]; then
        echo "build-s3: refusing existing target: $dir" >&2
        exit 2
    fi
    git clone -q --local "$REPO" "$dir"
    git -C "$dir" checkout -q "$PIN"
    [ "$(git -C "$dir" rev-parse HEAD)" = "$PIN" ] || {
        echo "build-s3: pin mismatch" >&2
        exit 1
    }
    mkdir -p "$dir/docs/engineering/profiles"
    cp "$PROFILE_GO" "$dir/docs/engineering/profiles/go-backend.md"
    cp "$PROFILE_PY" "$dir/docs/engineering/profiles/python-backend.md"
    cp "$POLICY_DOC" "$dir/docs/engineering/code-comments.md"
    cp "$REPO/AGENTS.md" "$dir/AGENTS.md"
    cp "$REPO/vault/index.md" "$dir/vault/index.md"
    if [ "$runtime_kind" = pre ]; then
        cp "$PRE_RUNTIME" "$dir/vault/runtime.md"
    else
        cp "$POST_RUNTIME" "$dir/vault/runtime.md"
    fi
    case $name in
        b3-post)
            # Same overlay as the frozen b-case (build-fixtures.sh overlay_b).
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
            ;;
    esac
    git -C "$dir" add -A
    git -C "$dir" -c user.name=replay -c user.email=replay@local \
        -c commit.gpgsign=false commit -qm "fixture overlay: $name"
    record "$name" "head" "$(git -C "$dir" rev-parse HEAD)"
    record "$name" "runtime" "$(sha256sum "$dir/vault/runtime.md" | awk '{print $1}')"
    record "$name" "agents" "$(sha256sum "$dir/AGENTS.md" | awk '{print $1}')"
    record "$name" "index" "$(sha256sum "$dir/vault/index.md" | awk '{print $1}')"
done

echo "built: $ROOT"
cat "$ROOT/fixture-manifest.txt"
