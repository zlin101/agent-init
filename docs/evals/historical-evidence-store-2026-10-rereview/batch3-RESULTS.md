# TASK-0029 修复批次 3 独立重审 · 2026-10-01

结论 **REQUEST_CHANGES**：损坏 `.git/HEAD` 的原反例已修；新 metadata 探测器仍把查询错误当作不存在，F29-002 reopened（P1）。F29-001/F29-003 fixed、F29-004 resolved。此前证据保持原内容，本轮仅新增 fixture、结果和原始 Linux 输出，不修改产品或原 POC。

## 审查对象与复核入口

HEAD `756c4967d242f78983df8cd3dd81c3b099798ff0` 的未提交修复批次 3；实际源文件 SHA-256：

```text
f84e42fc186056c0851ff4db9c6864ffcfdbc769bb67539499e3df6c3db062d2 scripts/history_store.py
1a4663d42bbb1888a44d782997ec245aa7db636b83a908a8b11a3c30c465443b scripts/trellium.py
eb3eb955ba11b28fc8fdba0791e730ad9dcd9d849722e67a75dc3423561a6846 scripts/test_history_store.py
8fd175de32cc174b8164ae745c56d62514637cee3d92cd21306682a6ae7ff403 scripts/test_trellium.py
```

从仓库 root 运行：

```sh
python3 -B docs/evals/historical-evidence-store-2026-10-rereview/batch3-replay.py
```

Linux 实际以 tar stdin 复制同一 fixture、scripts/init/skills 至现有 `python:3.12.3` 镜像的 `/tmp/task29`，运行参数 `--rm -i --network none --user 65534:65534`；容器本地 overlayfs，无 host bind mount、无镜像拉取或删除。等价命令：

```sh
tar -cf - scripts init skills docs/evals/historical-evidence-store-2026-10-rereview/batch3-replay.py |
  docker run --rm -i --network none --user 65534:65534 python:3.12.3 sh -c \
    'mkdir /tmp/task29 && cd /tmp/task29 && tar -xf - && python -B docs/evals/historical-evidence-store-2026-10-rereview/batch3-replay.py'
```

所有反例仅在自建 TemporaryDirectory 项目/Store；不访问真实身份、Store 或其他项目。Fixture exit 0 表示复核完成，不能代替 review PASS。

## 已修复与仍遗漏的边界

- 原 loose-ref 损坏与 `.git/HEAD` 损坏两个反例都拒绝创建身份，无替换文件；bootstrap 同步重试仍补同步；38 正式聚焦 tests（20 Store + 18 identity）均通过，真实非仓库/无提交首次绑定正例保持通过。
- 剩余问题在 `_has_git_metadata` 的 `os.path.lexists(current / '.git')`：Python `lexists` 内部调用 `os.lstat`，将 `OSError`（含 PermissionError）及 ValueError 捕获后返回 False，因而外层 `except OSError: return True` 无法接收该 lookup 错误。函数在不能查询 `.git` 时继续沿祖先链，最终以 False 当作已证明无 metadata。
- 新反例沿用已经提交身份、删除 working-tree identity、损坏 HEAD 的临时 Git 项目。Git 自身真实返回 `not a git repository`；正常读取 metadata 时修复后的 helper 拒绝。只对该项目 `.git` 的 Python `os.lstat` 注入 PermissionError，其余 filesystem 查询与 Git 子进程保持真实执行：detector 返回 False，helper 创建并登记不同 UUID，stamp bytes 也改变。恢复原 HEAD 后原提交 UUID 可读取。注入的是明确的查询错误，不声称实测了一种特定 ACL 或硬件故障。

两平台一致的实际观察摘录：

```text
F29-001: retry success = True ; failed parent fsync retried = True
F29-002 corrupt-ref: replacement created = False ; identity exists = False
F29-002 corrupt-HEAD-file: replacement created = False ; identity exists = False
F29-002 unreadable-metadata: lookup error observed = True ; detector = False ; replacement created = True ; differs from committed identity = True ; registered = True ; stamp changed = True
F29-002 corrupt-HEAD-file: committed identity recoverable after restoring HEAD = True
DISTRIBUTED E2E: trellium-zh PASS
DISTRIBUTED E2E: trellium PASS
```

Required fix：使用能区分不存在与查询失败的 metadata lookup，只有明确不存在才能继续探测祖先；权限/IO 等查询错误返回 unknown 并无写入拒绝。可直接用 lstat 并按错误类型分类，保留 broken symlink/目录/gitfile 的存在语义，不增加 schema/依赖/CLI。聚焦 fixture 需覆盖 lookup PermissionError/OSError 下 identity 和 stamp 均不写，保留正常无 `.git` 正例；无需扩面修 private_preflight。

## Fresh Verification

- macOS 27.0 arm64 / Python 3.9.6 / Git 2.54.0 (Apple Git-157)：38 聚焦 tests PASS（1.781 s），双语 E2E PASS，新错误注入反例成立。未独立取得 macOS filesystem 类型，保留前轮披露边界。
- Linux 7.0.14-orbstack aarch64 / Python 3.12.3 / Git 2.39.2 / overlayfs / uid 65534：38 聚焦 tests PASS（2.651 s），双语 E2E PASS，新错误注入反例成立。完整 stdout/stderr 为 [batch3-linux-output.txt](batch3-linux-output.txt)。
- macOS 全量四模块 257 tests（14.728 s）：256 PASS / 1 FAIL，唯一失败仍是此前干净基线已复现的 ancestor-swap fixture；全量命令仍为 FAIL。
- sync/check(0 errors / 0 warnings)/status/diff 均 PASS；最终任务与台账已据唯一剩余 P1 回写，status 确认 implementation/regression partial、review blocked，lifecycle 仍 ready_for_review。bundled modules byte-identical、源码 fingerprints current，证据 syntax/whitespace/末尾换行/本地链接检查 PASS。未修改产品、accepted、commit/push 或清理镜像。
