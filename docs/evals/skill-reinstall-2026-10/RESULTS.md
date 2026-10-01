# 2026.10.1 发布与实际 Skill 重装验证

2026-10-01；TASK-0032，发布准备基线 17fa1fd。发布、真实包替换和兼容验证均已完成；Owner acceptance 尚待确认。

## 发布前验证

- init/VERSION、双语嵌入 VERSION 与 MIGRATIONS 的改名条目同步为 2026.10.1；原 2026.10.0 保留不动。
- UI metadata 用 Ruby Psych safe_load 校验：显示 Trellium / Trellium 中文版，default_prompt 调用 $trellium / $trellium-zh，与 SKILL frontmatter 对应，不再调用旧名称。
- 四模块 macOS Python 3.9.6：[原始输出](release-full.txt)，284 tests / 283 PASS / 1 同一预存 ancestor-swap FAIL，完整命令 exit 1，不称全量 PASS。功能代码未改，TASK-0031 的 macOS/Linux 行为验证保持适用。
- sync-skills --check 和 diff --check PASS。当前旧安装包为 2026.09.1，34 文件与对应 tag byte-identical，无本地定制；已备份到 /private/tmp/trellium-reinstall-20261001/old-package，未提前卸载。

## 安装与兼容

- `2026.10.1` 已推送，远端 tag 与本地一致：`d1b6af36e4091f48f2369f91989081af22fd2290`；原 `2026.10.0` 仍为 `830f7b0ce691d85674d7bf03d7412334c6281608`。未创建 GitHub Release。
- 使用 skill-installer helper 固定 `--ref 2026.10.1 --path skills/trellium-zh` 下载到 staging；39 文件的路径与 SHA-256 全部等于 `git archive 2026.10.1` 对应包，无 symlink，只有根部 SKILL.md；工作流模板为 TRELLIUM_WORK_SKILL.template。CLI help exit 0，实际 YAML 显示 Trellium 中文版、调用 `$trellium-zh`。
- 原位重装 `~/.codex/skills/trellium-zh` 完成。替换前再次验证旧包/备份未变，将原目录移到发现目录外再装新包；脚本含失败回滚。备份：`/private/tmp/trellium-reinstall-20261001/old-package`；原卸载目录：同级 `uninstalled-original`，均非永久备份，系统清理临时目录后可能消失。替换后及测试后39文件 hashes均等于 tag；其他 Skills 未操作。
- 实际安装路径动态加载脚本与模板，macOS 27.0 arm64 / Python 3.9.6 / Git 2.54.0 (Apple Git-157)：[84 项聚焦测试](installed-tests.txt) 全 PASS（WorkSkillRename 10、ProjectIdentity 20、PrivateStorageMode 40、PrivateHistory 14）；使用[复跑脚本](run_installed_tests.py)，排除需要双语包相邻布局的单项，改由下列真实单包 E2E 覆盖。没有把 multiprocessing 子进程加载仓库 Store 的测试算作实际安装包验证。
- [3 项端到端测试](installed-e2e.txt) 全 PASS，见[脚本](run_e2e.py)：新 tracked/local/private 接入与 Git 边界；真正由旧 2026.09.1 备份接入的项目，旧命名写操作无写入拒绝、显式迁移仅修改 workflow 与指定 stamp 项、定制生成 proposal、不覆盖 data-role 记忆；实际 SKILL 内身份调用与 bundled Store 在 Local/Private 下完成 TASK+review 成组保全、第二项失败保留来源、重试、删除临时 clone 后按 digest 找回原 bytes、显式旧 UUID 恢复后重新登记与 check 0/0。
- [E2E 首跑失败记录](installed-e2e-initial.txt) 保留：临时 fixture 使用 `*` ignore 误忽略必须追踪的 tasks README；旧升级保护断言误把可升级 protocol 文件算入 data。改为窄 TASK/archive ignore，并按 FILE_ROLES=data 断言后通过；没有改产品代码或削弱真实保护边界。
- 所有项目、Git 操作与 Store 均在 TemporaryDirectory 内；真实其他项目与 `~/.trellium/history` 未访问。当前 turn 未实测运行态刷新后的 Skill 列表；按 skill-installer contract 新 Skill 下一 turn 可用。普通项目 `skills/trellium-work/` 的跨 Agent 自动发现仍受 D-0009 边界约束，本轮不作新增能力宣称。
- 收尾检查：`sync-skills.py --check` PASS；`trellium.py check . --format json` 0 errors / 0 warnings；`status` 无 unresolved，TASK-0032 ready_for_review，仅 owner_review pending；`git diff --check` PASS。验证记录另随 develop 提交，不移动已发布 tag。
