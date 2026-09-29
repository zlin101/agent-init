# Kill Gates 结果（2026-09-28）

## Gate 1：ignored/untracked AGENTS.md 发现 —— PASS（2/2 Agent）

| Agent | 版本 | 退出码 | 发现 AGENTS.md | 逐字引用 sentinel | 列出 Required Reading | 原始记录 |
| --- | --- | --- | --- | --- | --- | --- |
| Codex CLI | codex-cli 0.158.0 | 0 | 是（无任何提示） | 是 | 是 | `runs/2026-09-28-kg1-codex.md` |
| Claude Code | 2.1.263 | 0 | 是（引用 `AGENTS.md:5`/`:14` 行号） | 是 | 是 | `runs/2026-09-28-kg1-claude-code.md` |

Fixture 证明：`runs/2026-09-28-kg1-fixture-proof.txt` —— `git status --porcelain` 对 `AGENTS.md` 为空（ignored + untracked + HEAD 干净），`git ls-files --cached` 为 0，`git check-ignore -v` 命中 `.git/info/exclude:8:/AGENTS.md`。

Kill criterion（新 ignored AGENTS 不能被任一受支持 Agent 发现）未触发。

## Gate 2：forced-add 确定性检测 —— PASS

原始记录：`runs/2026-09-28-kg2-forced-add-proof.txt`（git 2.43.0）。

- `git add -f vault/index.md`（探针准备阶段故意执行的唯一一次 index 写入，即被测违规动作本身）之后，检测阶段的只读查询稳定暴露状态：`git ls-files --cached` 输出该路径；`git status --porcelain` 输出 `A  vault/index.md`。
- 除被测的 `git add -f` 外，检测阶段无 hook（`.git/hooks/` 仅有 sample）、无任何额外 index 写入或检出；checker 对该状态的检测不需要也不得产生写入。
- 同时证明规则视角不可见：`git check-ignore -v --no-index` 仍只报告 ignore 规则，对 forced-add 状态视而不见。因此 private 反向 Gate 必须组合 index/HEAD 查询，且这已足够。

Kill criterion（无法在不装 hook、不接管 Git 的情况下发现 staged/forced-add）未触发。

## 结论

两个 Kill Gate 均通过，private 模式进入 M1/M2 实现的前提成立。承诺边界不变：这是"配置边界 + 机械检测"，不声称阻止用户强制上传或清除历史（plan §11 R1 收缩承诺）。
