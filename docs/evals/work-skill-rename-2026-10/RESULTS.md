# Trellium Work 改名验证

2026-10-01；TASK-0031，基线 develop 830f7b0 / 已发布 tag 2026.10.0；本轮未 stage/commit/push/tag。这是实现验证与自检，不是独立 review 裁决。

## 结果

- macOS Python 3.9.6：命名/升级/双语分发聚焦 **52/52 PASS**；完整四模块 **284 tests / 283 PASS / 1 预存 FAIL**，唯一失败仍为 AgentInitTest.test_keeps_original_target_when_ancestor_is_swapped_after_open。完整命令 exit 1，不称全量绿；基线的同一失败记录见 TASK-0030 发布验证。
- Linux Python 3.12.3、非 root uid/gid 65534、network none、仓库只读：改名/Private/实际双语嵌入布局 **55/55 PASS**。未跑 Linux 全量，不将聚焦结果称为全量 PASS。
- 新增 WorkSkillRenameTest 10 项，覆盖旧 Tracked/Private 只读 check、旧文件/绑定/无 stamp/半迁移/冲突的零写入拒绝、定制显式迁移后的 proposal、UUID/stamp 保护、两种 namespace 的 preflight 碰撞与 forced-add 检测。既有双语实际生成测试新增唯一新 name/path 断言；模板继续没有可发现 SKILL.md。
- 隔离临时副本按当前文件建立本地提交，再真实 git clone：check **0 errors / 0 warnings**，status exit 0。副本取样时 TASK-0031 仍 active；这项证据验证协调提交后的 Gate 行为，不替代本仓实际 HEAD，也不宣称当前工作区已提交。
- 本仓 check/status exit 2：**2 CORE_STORAGE_UNCOMMITTED errors / 1 TASK_STORAGE_PENDING warning**，分别为新 Skill 不在 HEAD、HEAD stamp 的 managed paths 未同步、新任务未追踪。它们是未提交改名的真实状态，没有改弱 Gate 或操作本仓 index。提交后必须再次核对真实仓库。
- sync-skills --check、diff --check、Python AST、新增 Python 行宽 ≤120、文档链接/whitespace/末尾换行检查 PASS。预算仅测量，当前 policy 未设置预算阈值，不压缩。
- skill-creator 的 quick_validate 实际尝试因缺少 PyYAML 退出 1；未安装新依赖。另用现有 Ruby Psych safe_load 解析真实 frontmatter，校验 name/description/标题/名称长度及占位符，并确认安装包名称不变和嵌套模板不可发现，PASS。没有把原脚本结果标为成功。
- 本仓 stamp 与 HEAD 的逐字段比较证明：只有旧 workflow entry 被换成新路径、baseline 更新为迁移后内容 hash、observed=true；其他 files 条目、版本、profiles 与其余字段均保持原值。History 模块和 UUID 格式未变。

## 命令与证据

```bash
python3 -B -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh scripts.test_history_store
python3 -B -m unittest scripts.test_trellium.WorkSkillRenameTest scripts.test_trellium.TemplatePackagingTest scripts.test_trellium.UpgradeMechanismTest scripts.test_trellium.EmbeddedSkillLayoutTest
```

Linux：现有 python:3.12.3 镜像、--rm --network none --user 65534:65534、仓库 readonly bind；运行 WorkSkillRenameTest / PrivateStorageModeTest / EmbeddedSkillLayoutTest，经命令授权后执行。无下载/网络服务/真实项目迁移或 History 存储。

- [macOS 全量](macos-full.txt)
- [macOS 聚焦](macos-focused.txt)
- [Linux 聚焦](linux-focused.txt)
- [临时提交 fresh clone 的 check/status 原始结果](committed-clone-check.json)
- [最终源码、工作流与分发 fingerprints](fingerprints.txt)

## 自检与边界

契约覆盖：新路径/名称一致、原安装包保留、旧 stamp allowlist 有限、Private 原 block 可检查、新旧 namespace 均不可 tracked、迁移前不生成第二份 Skill。定制内容经 observed baseline 回到既有 proposal 路径，迁移不抹掉旧 Authority 或改 History 绑定。

最小性：只对现有 starter 改名；旧项目显式 Agent 迁移，不加入新的发现位置、CLI、schema、别名 Skill 或自动删除。D-0009 的独立入口实验不重开，历史任务/实验不改写，版本号仍 2026.10.0 并以 Unreleased 迁移条目记录未来发布内容。用户级已安装包不自动更新，本轮不修改其他项目。

## 接受与 develop 提交

2026-10-01 Owner 明确接受并授权 push，TASK-0031 转 accepted。上文未提交状态与两项 HEAD Gate error 属于实现验证轮，保留其真实历史；提交后重新检查实际仓库，不回写或伪造原始结果。实现 fingerprints 未变化；此次只更新交付记录，沿用当前 macOS/Linux 行为证据。本轮不创建或移动 tag，不变更 init/VERSION，不产生新的 GitHub Release。
