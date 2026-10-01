# TASK-0029 修复批次 4 独立重审 · 2026-10-01

结论 **APPROVE**：F29-002 fixed，F29-001/F29-003 fixed、F29-004 resolved，独立验收 blockers = 0。原 loop 两项 P3 residual 和预存 macOS fixture 失败保持披露，不宣称全量 suite 为绿。TASK 保持 ready_for_review，Owner 接受交付尚未勾选；不自动 accepted/commit/push。

## 审查对象与复核入口

HEAD `756c4967d242f78983df8cd3dd81c3b099798ff0` 的未提交修复批次 4。源码 SHA-256：

```text
f84e42fc186056c0851ff4db9c6864ffcfdbc769bb67539499e3df6c3db062d2 scripts/history_store.py
bce90c10cef382fb15406ecf46ae2a1b3bb170539421bff4a6379d21e22826ad scripts/trellium.py
eb3eb955ba11b28fc8fdba0791e730ad9dcd9d849722e67a75dc3423561a6846 scripts/test_history_store.py
a0e6ca1a19e6b55a99b674e38763480517c20ec36960c9104cba4fac3fad5394 scripts/test_trellium.py
```

从仓库 root 运行：

```sh
python3 -B docs/evals/historical-evidence-store-2026-10-rereview/batch4-replay.py
```

Linux 实际以 tar stdin 复制相同 fixture、scripts/init/skills 到现有 `python:3.12.3` 镜像的 `/tmp/task29`，`--rm -i --network none --user 65534:65534`。容器本地 overlayfs，无 host bind mount、镜像拉取或删除。等价命令：

```sh
tar -cf - scripts init skills docs/evals/historical-evidence-store-2026-10-rereview/batch4-replay.py |
  docker run --rm -i --network none --user 65534:65534 python:3.12.3 sh -c \
    'mkdir /tmp/task29 && cd /tmp/task29 && tar -xf - && python -B docs/evals/historical-evidence-store-2026-10-rereview/batch4-replay.py'
```

所有损坏/错误注入/删除仅在自建 TemporaryDirectory 项目与 Store。Fixture exit 0 仅表示复核完成，结论依赖下方实际观察与源码检查。旧 batch 证据保留原内容，本轮新增文件，不修改产品或原 POC。

## F29-002 关闭证据

- `_proven_without_git_metadata` 直接调用 lstat：条目存在返回 False；FileNotFoundError 继续祖先探测；其它 OSError 返回 None；只有祖先链全部确证无条目才返回 True。调用方 False/None 均拒绝首次绑定，True 才判非仓库。前轮 lexists 吞错误问题已消除。
- 原相同输入：临时 adopted local 项目，原身份已提交 Git HEAD、stamp 未登记，删 working-tree identity，改坏 HEAD。Git 子进程真实报非仓库；只对 `.git` 的 Python lstat 注入 PermissionError，helper 拒绝，身份文件仍不存在、stamp 原始 bytes 逐字节未变。恢复原 HEAD 后原提交 UUID 仍可读取。
- 独立结构分类 fixture 覆盖：全部无条目、目录存在、gitfile 存在、broken symlink 存在、PermissionError/NotADirectoryError/一般 OSError、resolve OSError。实际输出符合三态语义；正式 19 个 identity tests 保留真实非仓库/零修订首次绑定正例。
- 原 loose-ref 损坏和 HEAD 文件损坏均拒绝；bootstrap 同步失败重试仍补同步。20 个 Store tests、双语分发成组保全/第二 artifact 失败与重试/删临时 clone 找回 bytes 和来源路径均通过。

两平台一致的实际观察摘录：

```text
F29-001: retry success = True ; failed parent fsync retried = True
F29-002 corrupt-ref: replacement created = False ; identity exists = False
F29-002 corrupt-HEAD-file: replacement created = False ; identity exists = False
F29-002 unreadable-metadata: lookup error observed = True ; detector = None ; replacement created = False ; identity exists = False ; stamp unchanged = True
F29-002 corrupt-HEAD-file: committed identity recoverable after restoring HEAD = True
STRUCTURAL CLASSIFICATION: absence/presence/gitfile/broken symlink/lookup errors/resolve error PASS
DISTRIBUTED E2E: trellium-zh PASS
DISTRIBUTED E2E: trellium PASS
```

## Fresh Verification 与限制

- macOS 27.0 arm64 / Python 3.9.6 / Git 2.54.0 (Apple Git-157)：39 聚焦 tests PASS（1.765 s），上述反例/结构分类/双语 E2E PASS。未独立取得 macOS filesystem 类型，沿用前轮披露边界，不补造类型或物理 durability 证明。
- Linux 7.0.14-orbstack aarch64 / Python 3.12.3 / Git 2.39.2 / overlayfs / uid 65534：39 聚焦 tests PASS（2.597 s），相同 fixture/E2E PASS。完整 stdout/stderr 为 [batch4-linux-output.txt](batch4-linux-output.txt)。
- macOS 全量四模块 258 tests（15.201 s）：257 PASS / 1 FAIL，唯一失败仍是此前干净基线已复现的 `AgentInitTest.test_keeps_original_target_when_ancestor_is_swapped_after_open`。全量命令仍为 FAIL；不将该预存失败计为本变更新增 blocker。范围内 regression passed，保留该 validation residual。
- sync/check(0 errors / 0 warnings)/status/diff PASS；最终 review gate 已回写 passed，status 确认各 gates passed、lifecycle ready_for_review；AC 唯一未勾选项为 Owner 接受交付。bundled modules byte-identical、源码 fingerprints current，证据 syntax/whitespace/末尾换行/本地链接检查 PASS。

最终 canonical 代码规模按物理行报告，derived copies 与本轮 review fixture 不计为新增产品实现：新 Store 292 lines、新 Store tests 523 lines；相对 HEAD，trellium.py +308/-8、test_trellium.py +496/-16、sync-skills.py +31/-10。第三方依赖新增 0；持久表示为单行 UUID identity 和五字段 historical metadata（共两类，payload 是原始 opaque bytes）；TASK/policy/stamp schema、lifecycle、正式 CLI 变化 0。各 earlier Execution Record 的规模为当时快照，不替代此最终测量。

原 loop F001/F002 维持 P3 residual（非目录条目与大小写不敏感 artifact namespace）；七项 taste 风险未取得原 verdict 正文，不伪造其细节或处置。private_preflight 的相似分类已由实施者记录为后续评估，本次不扩面。Review 台账持续保留，Owner 接受交付与 Git 写操作仍待其决定。
