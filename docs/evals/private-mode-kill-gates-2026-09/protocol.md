# TASK-0019 M0 Kill Gates - 真实探针证据

日期：2026-09-28。对应 `docs/superpowers/plans/2026-09-28-private-storage-mode-plan.md` §11 R1/R2 与 §12 M0。

本目录保存 TASK-0019 两个 Kill Gate 的可复核原始证据。探针只验证"机制是否可行"，不修改产品代码；所有 fixture 都是临时目录，用后即弃，本目录内的文本是唯一留存记录。

## Gate 1：ignored/untracked AGENTS.md 的 Agent 发现（plan §11 R2）

- Kill criterion：新建 ignored `AGENTS.md` 不能被任一受支持 Agent 在无历史会话中发现。
- Fixture：临时 git 仓库（有 HEAD），`AGENTS.md` 仅存在于工作区且被 `.git/info/exclude` 的 canonical private block 忽略（untracked、ignored、`AGENTS.md` 不在 index——index 中仅跟踪 README、HEAD 干净）。见 `runs/2026-09-28-kg1-fixture-proof.txt`。
- Prompt：中性提问 Required Reading，不出现 `AGENTS.md` 字样。见 `prompts.md`。
- 受支持 Agent：Codex CLI（codex-cli 0.158.0）与 Claude Code（2.1.263），各自全新无历史会话。
- 判定：agent 自主发现并读取该文件、逐字引用 sentinel `PRIVATE-DISCOVERY-SENTINEL-7QF3`、正确列出 Required Reading，即 PASS。
- 结果：两个 agent 均 PASS。见 `results.md` 与 `runs/2026-09-28-kg1-{codex,claude-code}.md`。

## Gate 2：forced-add 的确定性检测（plan §11 R1）

- Kill criterion：无法在不安装 hook、不接管 Git 的情况下发现 staged/forced-add 状态。
- Probe：private fixture 中故意执行一次 `git add -f`（这既是被测的违规动作，也是一次有意的 index 写入），随后的检测阶段只用只读查询（`git ls-files --cached`、`git status --porcelain`）验证状态可见；并记录 `git check-ignore` 规则视角对该状态不可见，证明反向 Gate 必须查 index/HEAD。
- 结果：PASS。除被测的 `git add -f` 本身外，检测阶段无 hook、无任何额外 index 写入或检出。见 `runs/2026-09-28-kg2-forced-add-proof.txt`。

## 环境与脱敏说明

- git 2.43.0；Codex CLI 0.158.0（model 字段为会话环境配置，仅作复现参考）；Claude Code 2.1.263（stderr 中的模型告警原样保留，属于环境配置信息，非凭据）。
- 输出中的 `/tmp/trellium-m0-kg1-*` 路径为一次性临时目录，不含个人数据，原样保留以保证可复核；Codex 记录中的 session id 已脱敏（不影响复核）。
- 探针输出中的 sandbox/approval 字段为 CLI 默认头信息；无任何 token、密钥或私有 URL。
- 探针结论与 M0 红测的关系：Kill Gates 是"进入实现"的前提验证，红测（`scripts/test_trellium.py` `PrivateStorageModeTest`）把同样的机制契约固化为可回归断言。
