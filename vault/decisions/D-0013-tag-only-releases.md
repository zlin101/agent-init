# D-0013 - Trellium 静默发布仅推送 tag

Status: Active

Date: 2026-09-28

## Background

此前 Trellium 会在 tag 之外创建 GitHub Release，并将标题/正文压缩到最少。Owner 现将当前仓库的发布方式进一步收敛为静默发布。

## Decision

Trellium 后续版本只创建并推送版本 tag，不创建 GitHub Release，不生成 release 标题、正文或 notes。commit、push 与 tag 仍分别需要当前任务的明确授权。

## Rationale

版本 tag 已足以标识可安装版本；额外 Release 对象与文案没有必要，并增加发布步骤和维护成本。

## Impact

D-0003 被本决策取代，既有 Release 作为历史事实保留。`trellium.py --fetch` 已读取 GitHub tags、按版本号选择最新 tag，并保留缓存、tarball 安全解包与降级保护；`install.sh --version <tag>` 也直接下载对应 tag，因此无需新增 fetch 功能。TASK-0024（2026-09-29）已移除该解析：不传 `--version` 的网络安装在任何联网动作前直接失败，tag-only 契约由工具强制执行而非仅文档约定；发布与安装说明要求显式版本。
