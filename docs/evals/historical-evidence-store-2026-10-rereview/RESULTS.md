# TASK-0029 修复批次独立重审 · 2026-10-01

结论 **REQUEST_CHANGES**：F29-001/F29-002 原问题的边界仍未满足；F29-003 fixed，F29-004 resolved。此目录保存审查 fixture 与输出，不修改正式模块或原 2026-09 POC。两个反例只观察失败处理与成功响应，不声称做过物理断电或数据丢失实验。

## 审查对象

HEAD `756c4967d242f78983df8cd3dd81c3b099798ff0` 的未提交修复批次；以下 SHA-256 固定本轮审查源码与测试内容：

```text
23417aa53f4fa7f38e97248f4f7420eb5c043ba1381382224619ff3ccef26ac0 scripts/history_store.py
b68cd30aeec8b0e3458b4e1e8a23073fc1047768bacc56edd7cff602c6b48147 scripts/trellium.py
a10a15ba5b6e4539fa7e64fddbf1a38d0f112646c58c3dc4fd9e3d7514e06887 scripts/test_history_store.py
3cee9de34132622e4055cc586fa13fdb80e5db64aa7f9d9780a36deab77b5076 scripts/test_trellium.py
```

## Fixture 与复核命令

从仓库 root 运行：

```sh
python3 -B docs/evals/historical-evidence-store-2026-10-rereview/replay.py
```

`replay.py` 先运行正式 Store 17 tests + identity 16 tests，再执行两项边界反例与双语分发 E2E。所有项目、Git 损坏注入、Store、clone 删除均在自建 TemporaryDirectory；不访问真实历史 Store。此历史 fixture 的 exit 0 仅表示复核流程运行完成，**不是验收 PASS**；仍然存在的缺陷以实际观察输出判断。

Linux 实际使用现有 `python:3.12.3` 镜像（ID `3966b81808d8`），以 tar stdin 复制 `scripts/`、`init/`、`skills/` 和同一 fixture 到容器 `/tmp/task29`，不使用 host bind mount。运行参数为 `--rm -i --network none --user 65534:65534`；只删除本轮自建临时容器，没有拉取或删除镜像。可复核的等价命令：

```sh
tar -cf - scripts init skills docs/evals/historical-evidence-store-2026-10-rereview/replay.py |
  docker run --rm -i --network none --user 65534:65534 python:3.12.3 sh -c \
    'mkdir /tmp/task29 && cd /tmp/task29 && tar -xf - && python -B docs/evals/historical-evidence-store-2026-10-rereview/replay.py'
```

## 观察与结果

- macOS 27.0 arm64 / Python 3.9.6 / Git 2.54.0 (Apple Git-157)：33 tests PASS（1.599 s）；双语分发 E2E PASS；两项边界反例均复现。此轮未独立取得 macOS filesystem 类型：`diskutil info /` 因 DiskManagement framework 不可用失败，不补造类型。
- Linux 7.0.14-orbstack aarch64 / Python 3.12.3 / Git 2.39.2 / overlayfs / uid 65534：33 tests PASS（2.543 s）；双语分发 E2E PASS；两项边界反例均复现。完整 stdout/stderr 保存在 [linux-output.txt](linux-output.txt)。F29-004 的必需 Linux 正式测试与分发调用证据已独立取得，可关闭。
- F29-001：fixture 使用 `<temp>/.trellium/history`，初始 `.trellium` 不存在；注入第一次同步 `<temp>` 失败后，该目录项已可见。重试 put 成功且 get bytes 正确，但 `<temp>` 未再次 fsync。`_sync_namespace` 在 `root.parent`（`.trellium`）停止，遗漏持久化 `.trellium` 目录项所需的父目录。默认 root 的首次使用即可遇到此边界。
- F29-002：fixture 将 identity 提交至临时 Git HEAD（stamp 未登记），删除 working-tree identity，再将该 HEAD 所指 loose ref 内容改为 `corrupt ref\n`。实际 `rev-parse --verify HEAD` 返回 `fatal: Needed a single revision`；helper 将它判作无提交，获首次绑定授权后创建并登记与已提交身份不同的 UUID。此报错不能单独证明 unborn HEAD。

两组合一致的原始观察摘录：

```text
F29-001: retry success = True ; failed parent fsync retried = False
F29-002: corrupt HEAD stderr = fatal: Needed a single revision
F29-002: replacement created = True ; differs from committed identity = True ; registered = True
DISTRIBUTED E2E: trellium-zh PASS
DISTRIBUTED E2E: trellium PASS
```

macOS 全量 `python3 -B -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh scripts.test_history_store`：252 tests（14.341 s），251 PASS / 1 FAIL；唯一失败仍是此前干净基线已复现的 `AgentInitTest.test_keeps_original_target_when_ancestor_is_swapped_after_open`。全量命令仍为 FAIL，不称“全部验证绿”。sync/check(0 errors / 0 warnings)/status/diff 检查通过。

本轮临时复核入口最初缺少 root import path 和 multiprocessing main 保护，修正入口后重新执行；这些 harness 错误不作为产品 finding。原正式测试未修改。
