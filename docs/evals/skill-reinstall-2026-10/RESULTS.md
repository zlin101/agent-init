# 2026.10.1 发布与实际 Skill 重装验证

2026-10-01；TASK-0032，发布准备基线 17fa1fd。本文随各阶段追加实际结果；安装/兼容尚待执行，不将发布检查等同于实际 Skill 验收。

## 发布前验证

- init/VERSION、双语嵌入 VERSION 与 MIGRATIONS 的改名条目同步为 2026.10.1；原 2026.10.0 保留不动。
- UI metadata 用 Ruby Psych safe_load 校验：显示 Trellium / Trellium 中文版，default_prompt 调用 $trellium / $trellium-zh，与 SKILL frontmatter 对应，不再调用旧名称。
- 四模块 macOS Python 3.9.6：[原始输出](release-full.txt)，284 tests / 283 PASS / 1 同一预存 ancestor-swap FAIL，完整命令 exit 1，不称全量 PASS。功能代码未改，TASK-0031 的 macOS/Linux 行为验证保持适用。
- sync-skills --check 和 diff --check PASS。当前旧安装包为 2026.09.1，34 文件与对应 tag byte-identical，无本地定制；已备份到 /private/tmp/trellium-reinstall-20261001/old-package，未提前卸载。

## 安装与兼容

待新 tag 发布后，按该不可变 tag 下载到 staging，校验源树、模板不可发现与 CLI 后再替换实际安装。只更新 Codex 中文包，测试目标与 Store 均隔离在临时目录；其他项目和真实 History 不访问。当前 turn 不宣称机器运行态已刷新 Skill 列表，发现情况需下一 turn 确认。
