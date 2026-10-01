# Private History 验证

2026-10-01；TASK-0030，develop 基线 6a875d8；本轮未提交或发布。实现已完成至 owner review，本文不是独立 reviewer 的裁决。

## 结果

- Private identity 与 Git 边界、Local 身份回归、Store 聚焦：macOS **55/55 PASS**，Linux 非特权容器 **55/55 PASS**。
- macOS 完整四模块：**274 tests / 273 PASS / 1 预存 FAIL**；修改前基线 **258 tests / 257 PASS / 同一 FAIL**。失败均为 AgentInitTest.test_keeps_original_target_when_ancestor_is_swapped_after_open；完整命令结果仍 FAIL，不能称全量绿。
- 双语包通过 Skill 中的真实 identity 命令完成 Private 初次绑定与显式恢复；加载各包实际 history_store 模块完成 TASK/ledger 成组保全、第二 artifact 失败/重试、删除临时 clone 后 get 校验 bytes、重建 Private 接入并复用原 UUID。目标 index/HEAD 只有 fixture README，身份/任务/ledger ignored。
- 新增 16 tests：PrivateHistoryTest 15 项，加 Local monorepo HEAD 已绑定但 worktree identity 丢失的拒绝测试；原 Store 20 与 Local identity 19 项保持覆盖。
- sync-skills in sync、diff whitespace PASS；新增 Python 代码行宽 ≤120；源码/分发模块和双语 Python 示例 AST syntax PASS，两个语言的 History 示例 byte-identical。
- 仓库 check/status exit 0；0 errors / 1 TASK_STORAGE_PENDING warning，原因是本仓 tracked 而新增 TASK-0030 尚未暂存/提交；没有为消除 warning 擅自操作 Git index。未配置预算阈值，仅执行预算测量。

## 环境与命令

macOS 27.0 arm64 / Python 3.9.6 / Git 2.54.0 (Apple Git-157)。本轮没有新增 filesystem 类型或物理持久性实测；沿用 Store 原有环境边界。

```bash
python3 -B -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh scripts.test_history_store
python3 -B -m unittest scripts.test_trellium.PrivateHistoryTest scripts.test_trellium.ProjectIdentityTest scripts.test_history_store
```

Linux 使用现有 python:3.12.3 镜像，uid/gid 65534、network none、仓库只读挂载；Store/clone 在容器本地临时目录，未访问真实 home Store。默认 sandbox 不能访问 Docker socket，经命令审批后运行，无下载/apt/网络依赖。

```text
docker run --rm --network none --user 65534:65534 \
  --mount type=bind,source=<repo>,target=/work,readonly \
  --workdir /work python:3.12.3 python3 -B -m unittest \
  scripts.test_trellium.PrivateHistoryTest \
  scripts.test_trellium.ProjectIdentityTest scripts.test_history_store
```

Linux 完整四模块未执行，不将 Linux 聚焦结果称为全量 PASS。

## 原始证据

- [修改前 macOS 基线](macos-baseline.txt)
- [macOS 全量](macos-full.txt)
- [macOS 聚焦](macos-focused.txt)
- [Linux 聚焦](linux-focused.txt)
- [最终源码与分发 fingerprints](fingerprints.txt)
- [测试源](../../../scripts/test_trellium.py)中的 PrivateHistoryTest / ProjectIdentityTest

代码行为测试完成后仅调整错误字符串换行与 Store 模块 docstring，再做 AST/sync 检查；fingerprints 对应最终工作区，没有将格式变化冒充新增行为验证。

## 两轮自检与边界

1. 契约覆盖：Private 忽略规则、首次授权、绑定丢失/改变、stamp 登记失败重试、重复 adopt/upgrade、profile extras、forced-add、未知 Git 和损坏 HEAD/ref 均有拒绝/保留证据；预检及 checker 的损坏 metadata 分类已修正，monorepo 使用 Git 根坐标。
2. 最小性：Store 格式/API、policy/stamp schema、默认 Local 不变；无 registry/manifest/服务/CLI/自动同步/cleanup/全 Vault 备份。Private 保留/迁移原 UUID 并按需 get，是显式恢复流程；历史不激活任务/Authority。

原 Store 两项 P3 residual 仍沿用 TASK-0029 的披露；没有扩大通用 artifact id 或 filesystem 保证。未 spawn reviewer、未将自检标为独立审查；owner_review 待定。

## 2026.10.0 发布检查

- Owner 于 2026-10-01 要求“push吧，新打一个tag”，接受本次交付并授权发布；TASK-0030 转 accepted，TASK-0027 保持待审。上文“未提交或发布”描述原实施验证轮，不是此后发布状态。
- init/VERSION 与全部嵌入版本同步为 2026.10.0，四项 Unreleased 迁移条目归入该版本；tag-only，不创建 GitHub Release。
- 最终版本的完整四模块复跑：[原始输出](release-full.txt)，274 tests / 273 PASS / 同一预存 ancestor-swap FAIL；命令仍 FAIL，没有新的失败。同步及 diff 检查 PASS。此前 Linux 聚焦证据适用于未变的功能源码，未在此发布轮重复运行 Linux。
- 最终暂存后 check：0 errors / 0 warnings；status：29 closed / 1 ready_for_review（TASK-0027）；cached diff --check PASS，工作树没有未暂存变更。预算只测量，不执行压缩。
