# TASK-0029 修复批次 2 独立重审 · 2026-10-01

结论 **REQUEST_CHANGES**：F29-001 fixed；F29-002 的原 loose-ref 反例已修，但损坏 HEAD 文件仍会生成替代身份，故 reopened（P1）。F29-003 fixed、F29-004 resolved。前轮证据文件保持原内容，本轮新增独立 fixture/结果，不修改产品或原 POC。

## 审查对象

HEAD `756c4967d242f78983df8cd3dd81c3b099798ff0` 的未提交修复批次 2；本轮实际源码 SHA-256：

```text
f84e42fc186056c0851ff4db9c6864ffcfdbc769bb67539499e3df6c3db062d2 scripts/history_store.py
9c965c6366e60e699d6583bb74fe4f7272e90dc4d980db8073879646ece72a81 scripts/trellium.py
eb3eb955ba11b28fc8fdba0791e730ad9dcd9d849722e67a75dc3423561a6846 scripts/test_history_store.py
34bc48403861495ff411bb505c273384cd2ab3204ad18dab5378313053fce8de scripts/test_trellium.py
```

## 复核命令与环境

从仓库 root 运行：

```sh
python3 -B docs/evals/historical-evidence-store-2026-10-rereview/batch2-replay.py
```

同一 fixture 实际以 tar stdin 复制到 `python:3.12.3` 现有镜像的 `/tmp/task29`，`--rm -i --network none --user 65534:65534`；容器本地 overlayfs，无 host bind mount、无镜像拉取或删除。可复核等价命令：

```sh
tar -cf - scripts init skills docs/evals/historical-evidence-store-2026-10-rereview/batch2-replay.py |
  docker run --rm -i --network none --user 65534:65534 python:3.12.3 sh -c \
    'mkdir /tmp/task29 && cd /tmp/task29 && tar -xf - && python -B docs/evals/historical-evidence-store-2026-10-rereview/batch2-replay.py'
```

- macOS 27.0 arm64 / Python 3.9.6 / Git 2.54.0 (Apple Git-157)：37 聚焦 tests PASS（1.661 s），双语 E2E PASS。未独立取得 macOS filesystem 类型，沿用前轮披露边界。
- Linux 7.0.14-orbstack aarch64 / Python 3.12.3 / Git 2.39.2 / overlayfs / uid 65534：37 聚焦 tests PASS（2.590 s），双语 E2E PASS；原始 stdout/stderr 为 [batch2-linux-output.txt](batch2-linux-output.txt)。
- macOS 全量四模块 256 tests（14.469 s）：255 PASS / 1 FAIL，唯一失败仍是此前干净基线已复现的 ancestor-swap fixture；全量命令仍为 FAIL。sync/check(0/0)/status/diff 均 PASS；最终 task gates 已回写 implementation/regression partial、review blocked，lifecycle 仍 ready_for_review。

所有损坏、权限、删除操作均在自建 TemporaryDirectory；不访问真实项目身份或 Store。Fixture exit 0 仅表示复核流程完成，不等于 review PASS。临时 fixture 初版将 get 观察放在 TemporaryDirectory 清理后导致 FileNotFoundError，修正该入口生命周期后双平台重跑；不将 harness 错误作为产品 finding。

## 已修复部分

- F29-001：原 bootstrap 父层失败→重试反例的 `failed parent fsync retried` 已翻转为 True；固定同步链覆盖该层，已有 namespace 也重同步。新增守卫对更深缺失祖先在构造时 ValueError 且无写入，20 个 Store tests 覆盖该行为。接受这个有界、显式拒绝的修复选择；不扩大 filesystem 保证。
- F29-002：原 `corrupt ref\n` 的 loose-ref 反例拒绝创建且无身份文件；保留无提交正例，结构探针有有效的额外证据时可判断零修订。因此将 rev-parse 操作错误测试改为有提交 fixture 符合其测试目标。

## F29-002 仍遗漏的非仓库分类

精确输入：adopted local 临时项目，stamp 尚无 identity 登记；原 UUID 写入 `vault/project-id` 并提交 HEAD。删除 working-tree identity；仅将 `.git/HEAD` 原 `ref: refs/heads/<branch>\n` 内容改为 `corrupt head\n`，不删除 refs 或 objects。调用 `ensure_project_identity(..., authorize_create=True)`。

Git 2.54.0 与 2.39.2 实际均返回 `fatal: not a git repository (or any of the parent directories): .git`。`scripts/trellium.py:2425–2426` 立即返回 False，绕过结构探针。helper 创建并登记与已提交身份不同的 UUID。随后恢复原 HEAD 文件，`git show HEAD:vault/project-id` 仍能返回原 UUID，证明是存在且可恢复的仓库损坏，而非已证明没有 Git 绑定证据。

两平台一致的实际观察摘录：

```text
F29-001: retry success = True ; failed parent fsync retried = True
F29-002: corrupt HEAD stderr = fatal: Needed a single revision
F29-002 corrupt-ref: replacement created = False ; identity exists = False
F29-002 corrupt-HEAD-file: stderr = fatal: not a git repository (or any of the parent directories): .git
F29-002 corrupt-HEAD-file: replacement created = True ; differs from committed identity = True ; registered = True
F29-002 corrupt-HEAD-file: committed identity recoverable after restoring HEAD = True
DISTRIBUTED E2E: trellium-zh PASS
DISTRIBUTED E2E: trellium PASS
```

Required fix：非仓库错误文本只能说明 Git 当前无法识别仓库，不能单独证明无绑定。对存在但损坏/不可读的 Git metadata 返回 unknown 并拒绝写入；真实非仓库及 Git 可证明的空仓库保留首次绑定正例。增加上述 HEAD 文件损坏 fixture，核验身份文件和 stamp 都无写入；不新增身份副本、状态 schema 或恢复 CLI。
