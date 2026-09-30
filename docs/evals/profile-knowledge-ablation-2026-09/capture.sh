#!/bin/sh
# Capture replay outputs: full diff vs baseline commit + objective verification.
#
# Usage: sh capture.sh [target-dir]   (default: /tmp/trellium-0026-replay)
#   CAPTURE_RUNS  override output dir (default: <evidence>/runs; used by the
#                 failure self-test so it cannot clobber real evidence).
#
# Exit status is the reliability contract:
#   0  every map row parsed AND every workspace verified
#   1  at least one workspace printed VERIFY FAIL
#   2  map.tsv missing/unparseable (key/lang/base validation), unknown key
# A VERIFY FAIL is never masked: verification status, not the last helper
# command, decides the exit code.
set -eu

EVIDENCE=$(cd -- "$(dirname -- "$0")" && pwd)
ROOT=${1:-/tmp/trellium-0026-replay}
RUNS=${CAPTURE_RUNS:-$EVIDENCE/runs}
mkdir -p "$RUNS"

if [ ! -f "$ROOT/map.tsv" ]; then
    echo "capture: missing map.tsv in $ROOT" >&2
    exit 2
fi

verify() {
    key=$1
    dir="$ROOT/$key"
    out="$RUNS/$key-verify.txt"
    if {
        case $key in
            s1?)
                (cd "$dir" && make verify) ;;
            s3?)
                (cd "$dir/moda" && go test ./...) &&
                    (cd "$dir/modb" && go test ./...) ;;
            s4?)
                (cd "$dir" && go vet ./... && go test ./...) ;;
            s5?)
                (cd "$dir" && uv run pytest -q) ;;
            s2?)
                # Any sub-step failure must fail the verification: do not let
                # a later command's status mask the pytest status.
                rc=0
                if [ -f "$dir/pyproject.toml" ]; then
                    (cd "$dir" && uv sync -q && uv run python -m pytest -q) || rc=1
                fi
                python3 -c "import ast,pathlib,sys
bad=[]
root=pathlib.Path(sys.argv[1])
for p in root.rglob('*.py'):
    if '.venv' in p.parts or '__pycache__' in p.parts:
        continue
    try:
        ast.parse(p.read_text(encoding='utf-8'))
    except SyntaxError as e:
        bad.append(f'{p}: {e}')
print('syntax ok' if not bad else '\n'.join(bad))
sys.exit(1 if bad else 0)" "$dir" || rc=1
                [ "$rc" -eq 0 ] ;;
            *)
                echo "verify: unknown key: $key"
                false ;;
        esac
    } >"$out" 2>&1; then
        echo "VERIFY PASS" >>"$out"
        printf '%s: VERIFY PASS\n' "$key"
        return 0
    fi
    echo "VERIFY FAIL" >>"$out"
    printf '%s: VERIFY FAIL\n' "$key"
    return 1
}

# Tab IFS is built at runtime (printf), not written as an invisible literal in
# the source, so the delimiter cannot be lost or misread across edits/copies.
TAB=$(printf '\t')
failures=0
IFS=$TAB
while read -r key lang base; do
    [ -n "$key" ] || continue
    # Strict validation: if the split ever breaks (whole line lands in $key),
    # fail loudly instead of writing evidence under a garbage filename.
    case $key in
        s[1-5][ab]) ;;
        *)
            echo "capture: bad key in map.tsv: '$key'" >&2
            exit 2 ;;
    esac
    case $lang in
        go | python) ;;
        *)
            echo "capture: bad lang for $key: '$lang'" >&2
            exit 2 ;;
    esac
    case $base in
        "" | *[!0-9a-f]*)
            echo "capture: bad base for $key: '$base'" >&2
            exit 2 ;;
    esac
    if [ "${#base}" -lt 40 ]; then
        echo "capture: short base for $key: '$base'" >&2
        exit 2
    fi
    dir="$ROOT/$key"
    git -C "$dir" add -A
    git -C "$dir" diff "$base" >"$RUNS/$key-changes.patch"
    printf '%s: %s lines of change\n' "$key" "$(wc -l <"$RUNS/$key-changes.patch")"
    if ! verify "$key"; then
        failures=$((failures + 1))
    fi
done <"$ROOT/map.tsv"

if [ "$failures" -ne 0 ]; then
    echo "capture: $failures workspace(s) failed verification" >&2
    exit 1
fi
echo "capture: all workspaces verified"
