#!/bin/sh
# Build TASK-0028 S2 kill-gate U fixture: customized index (project-unique
# constraint) + candidate light-read AGENTS (u-cand) vs default entry (u-ctrl).
#
# Safety: creates only NEW directories; refuses existing targets; never removes.
#
# Usage: sh build-u.sh <target-parent-dir>
set -eu

EVIDENCE=$(cd -- "$(dirname -- "$0")" && pwd)
REPO=$(cd -- "$EVIDENCE/../../.." && pwd)
PIN=77ee0224dc75d18fcdc0f88e67b0faa100e8635a
S1=$REPO/docs/evals/profile-knowledge-ablation-2026-09/fixtures/s1-shop-api
PROFILE_GO=$REPO/init/protocol/profiles/go-backend.md
PROFILE_PY=$REPO/init/protocol/profiles/python-backend.md
POLICY_DOC=$REPO/docs/evals/profile-knowledge-ablation-2026-09/fixtures/s5-catalog-api/docs/engineering/code-comments.md

if [ $# -lt 1 ]; then
    echo "usage: build-u.sh <target-parent-dir>" >&2
    exit 2
fi
ROOT=$1
if [ -e "$ROOT" ]; then
    echo "build-u: refusing existing target: $ROOT" >&2
    exit 2
fi
mkdir -p "$ROOT"
: >"$ROOT/fixture-manifest.txt"

record() { printf '%s\t%s\t%s\n' "$1" "$2" "$3" >>"$ROOT/fixture-manifest.txt"; }

# Splice the Required Reading body of AGENTS.md from a head file, and rewrite
# workflow step 2 for the candidate variant.
splice_agents() {
    src=$1
    head=$2
    step2_new=$3
    out=$4
    python3 - "$src" "$head" "$step2_new" "$out" <<'PYEOF'
import sys
src, head, step2_new, out = sys.argv[1:5]
text = open(src, encoding="utf-8").read()
body = open(head, encoding="utf-8").read().rstrip("\n")
start = text.index("## Required Reading")
end = text.index("## Working Principles", start)
head_block = text[start : text.index("\n", start) + 1]
text = text[: start + len(head_block)] + "\n" + body + "\n\n" + text[end:]
old_step2 = (
    "2. 根据 `vault/index.md` 速查表判断任务等级和授权等级；"
    "判定模糊或 Level B/C 时读取 `vault/governance.md`。"
)
new_step2 = open(step2_new, encoding="utf-8").read().strip()
if old_step2 in text:
    text = text.replace(old_step2, new_step2, 1)
open(out, "w", encoding="utf-8").write(text)
PYEOF
}

for v in ctrl cand; do
    dir="$ROOT/u-$v"
    if [ -e "$dir" ]; then
        echo "build-u: refusing existing target: $dir" >&2
        exit 2
    fi
    git clone -q --local "$REPO" "$dir"
    git -C "$dir" checkout -q "$PIN"
    [ "$(git -C "$dir" rev-parse HEAD)" = "$PIN" ] || {
        echo "build-u: pin mismatch" >&2
        exit 1
    }
    # engineering docs
    mkdir -p "$dir/docs/engineering/profiles"
    cp "$PROFILE_GO" "$dir/docs/engineering/profiles/go-backend.md"
    cp "$PROFILE_PY" "$dir/docs/engineering/profiles/python-backend.md"
    cp "$POLICY_DOC" "$dir/docs/engineering/code-comments.md"
    # s1-shop-api overlay as the project's service code
    cp "$S1/README.md" "$dir/README.md"
    cp "$S1/go.mod" "$dir/go.mod"
    cp "$S1/Makefile" "$dir/Makefile"
    cp "$S1/scripts/check-fmt.sh" "$dir/scripts/check-fmt.sh"
    mkdir -p "$dir/cmd" "$dir/internal"
    cp -r "$S1/cmd/." "$dir/cmd/"
    cp -r "$S1/internal/." "$dir/internal/"
    # side files: runtime from worktree start; index = worktree + custom block
    cp "$REPO/vault/runtime.md" "$dir/vault/runtime.md"
    python3 - "$REPO/vault/index.md" "$dir/vault/index.md" <<'PYEOF'
import sys
text = open(sys.argv[1], encoding="utf-8").read()
block = """## 项目定制约束（本项目独有，升级不得删除）

- 所有新增 HTTP 路由必须挂在 `/api` 前缀下（例如 `GET /api/health`；`/health` 不符合约定）。

"""
anchor = "## 任务与授权速查表"
text = text.replace(anchor, block + anchor, 1)
open(sys.argv[2], "w", encoding="utf-8").write(text)
PYEOF
    grep -q "/api/health" "$dir/vault/index.md" || {
        echo "build-u: constraint injection failed" >&2
        exit 1
    }
    if [ "$v" = ctrl ]; then
        cp "$REPO/AGENTS.md" "$dir/AGENTS.md"
    else
        cat >"$ROOT/candidate-step2.txt" <<'S2EOF'
2. 分级判断：命中任一 Level C 风险域（安全/隐私、公开 API/外部契约、持久数据/迁移、部署/生产、依赖、实质成本/配额、架构方向、治理规则），或恢复/协作成本明显高（跨会话、真实 handoff、多 owner、外部系统状态、多阶段 gate），或判定模糊 → 读完整 `vault/governance.md` 并按 B/C 处理；B/C 续作、真实中断、Vault 写入或 storage/预算判断先读 `vault/index.md`；否则按 A 处理，读 `vault/runtime.md` 与匹配工程规范。
S2EOF
        splice_agents "$REPO/AGENTS.md" "$EVIDENCE/u-candidate-agents-head.md" \
            "$ROOT/candidate-step2.txt" "$dir/AGENTS.md"
        grep -q "普通 Level A 任务前" "$dir/AGENTS.md" || {
            echo "build-u: candidate AGENTS splice failed" >&2
            exit 1
        }
    fi
    git -C "$dir" add -A
    git -C "$dir" -c user.name=replay -c user.email=replay@local \
        -c commit.gpgsign=false commit -qm "fixture overlay: u/$v"
    record "u-$v" "head" "$(git -C "$dir" rev-parse HEAD)"
    record "u-$v" "agents" "$(sha256sum "$dir/AGENTS.md" | awk '{print $1}')"
    record "u-$v" "index" "$(sha256sum "$dir/vault/index.md" | awk '{print $1}')"
    record "u-$v" "runtime" "$(sha256sum "$dir/vault/runtime.md" | awk '{print $1}')"
done

echo "built: $ROOT"
cat "$ROOT/fixture-manifest.txt"
