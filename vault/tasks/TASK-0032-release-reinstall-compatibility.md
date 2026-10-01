# TASK-0032 - 2026.10.1 发布、重装和兼容验证

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0032",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "ready_for_review",
  "current_slice": "owner-acceptance",
  "gates": {
    "release_checks": "passed",
    "tag_publication": "passed",
    "reinstallation": "passed",
    "compatibility": "passed",
    "owner_review": "pending"
  }
}
-->

## Objective

将已接受的 Trellium Work 改名纳入新 tag 2026.10.1，替换当前 Codex 中文 Skill，并用真实安装包验证接入、升级与数据保护。

## Scope

- init/VERSION 与改名 MIGRATIONS 转为 2026.10.1，双语 snapshot 同步；校正既有 openai.yaml 的 UI 名称和 default_prompt 到实际 Skill 名称，其他配置不变。
- 发布新版本 tag 并推送 develop，保留 2026.10.0；不创建 GitHub Release。
- 仅将当前 ~/.codex/skills/trellium-zh 的旧包卸载并重装同一语言/位置；旧包先备份到发现目录之外，校验新包后替换，失败恢复。
- 使用新安装包及旧 2026.09.1 备份创建临时 fixture：新三模式、实际旧接入与显式工作流迁移、定制 proposal、Private forced-add、History 成组失败/重试/删 clone 找回；不访问真实 History。

Out of scope：Claude/其他 Skill 安装、真实其他项目迁移、全局独立 trellium-work 安装、默认模式切换、新 schema/CLI/发现机制、自动当前 Vault 恢复、扩大 filesystem 持久性保证。

## Context Required

AGENTS、index/runtime/governance/project、已接受 TASK-0031 与 D-0013/D-0016、skill-installer、skill-creator 的 UI metadata 规范、canonical 工程规范/Comment Policy、install.sh 与实际旧/新包。

## Capability Tags

release, installation, skills, migration, testing, privacy

## Authority

Allowed：Owner 明确要求卸载目前 trellium Skill、安装最新版并测试兼容；随后明确要求包含最新版内容的新 10.1 tag。授权当前限定的本机包替换、测试、版本提交/push/tag；相同职责的失配 UI metadata 一并校正。

Requires approval：扩大安装对象/真实项目迁移、新发现机制、其他版本发布、owner 接受。

Forbidden：覆盖本地定制不留副本、改写 2026.10.0 tag、把旧数据恢复为当前 Authority、泄露凭据或私有账号信息、伪造实时 Skill 自动发现验证。

## Acceptance Criteria

- [x] 新 tag 指向包含改名及一致版本号的提交，原 10.0 tag 不变。
- [x] 新包来自发布 tag，与对应源文件 byte-identical；UI 调用名正确，嵌套模板不可发现。
- [x] 原 09.1 包无定制或已妥善保留，替换后目录正常、备份可回滚。
- [x] 用实际安装包验证新三模式、旧项目拒绝/迁移/定制保护、Private forced-add 与 History 找回。
- [x] 如实记录环境、原始证据、仓库与分发检查及运行态发现边界。
- [ ] Owner 接受本轮兼容交付。

## Verification

发布前四模块及 sync/diff/check/status；安装 helper 的固定 tag staging；tree hashes/name/YAML/无 symlink 与嵌套 SKILL 检查；实际包 E2E 与存储/身份/迁移聚焦测试；本机 Codex 所需写权限用工具审批执行。macOS 全量既有 ancestor-swap 失败独立保留，不称全量绿；测试只用临时项目/Store。下一 turn 的 Skill 列表发现不能用磁盘结构检查冒充。

## Execution Record

- 2026-10-01：源基线 develop 17fa1fd（已接受/推送 TASK-0031）；旧包是 2026.09.1，34 文件与对应 tag 全部 byte-identical，无本地定制。已备份到 /private/tmp/trellium-reinstall-20261001/old-package，未先移除可用安装。
- 初按 develop 最新进行准备；owner 随后明确新 10.1 tag，交付改为从不可变新发布版本重装。远端 2026.10.1 不存在，2026.10.0 仍指向 830f7b0。
- 发现两包 UI metadata 仍显示 Agent Native Init 且 default_prompt 指向已不存在的 agent-native-init 名称；按实际 name 校正，保证重装后的 UI 调用入口兼容。

- [发布前证据](../../docs/evals/skill-reinstall-2026-10/RESULTS.md)：全量 284 tests / 283 PASS / 同一预存 FAIL；版本/UI metadata/sync/diff 检查通过，范围内 release_checks passed 不代表全量绿。发布、下载与真实替换仍分阶段记录。
- 发布提交 d1b6af3 已与新 tag 2026.10.1 原子推送，远端已独立核对；10.0 未动。实际 Codex 中文包从新 tag 下载，校验39文件后原位替换，旧包在临时目录外置保留，测试后新包 hashes 未变。
- 实际安装包84项聚焦 +3项 E2E通过；旧09.1真实 fixture、三模式、定制 proposal、Private forced-add、Local/Private History失败重试及删clone找回均覆盖。初始 E2E fixture错误及修正保留在证据中；产品代码未改，真实History与其他项目未操作。下一turn可发现新包，当前turn不冒充运行态发现测试。
- 收尾 sync/check/status/diff 全 PASS，check 0/0、status unresolved 0；证据与任务记忆单独提交到 develop，不移动发布 tag。只有 Owner acceptance 保持 pending。

## Memory Updates

runtime 更新本机安装/发布事实与导航，不维护 TASK 投影；无新的长期架构决定，不改已接受任务。

Durable knowledge disposition: not_applicable（tracked task）。

## Handoff Requirement

当前 Git、任务、已保存备份及验证脚本可推导现场；仅真实中断且有非可推导 delta 才写 handoff。
