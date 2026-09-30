# TASK-0026 Profile knowledge ablation — before/after fixture 行为回放 protocol

日期：2026-09-30。对应 TASK-0026 M3 与 review round 1 P1 返修：前五个场景此前只有关键词计数，不构成契约要求的"固定 task/repo 输入、前后行为输出"。round 2（同日）修复证据工具链并补做 s5（见文末“round 2 修订”）。

## 变量控制

- 每场景两个工作区 `<scene>-a` / `<scene>-b`（`a`/`b` 为中性代号，执行方不知道其含义）。
- 逐字相同的部分：固定任务文本（`prompts.md`，未随 round 2 变更）、fixture 仓库内容、harness 规则、agent（pi subagent `worker`，fresh context，同模型）。
- 唯一差异：`AGENTS.md` — `a` = 消融前 Profile（`git show $BASE_SHA:init/protocol/profiles/<lang>-backend.md`，`BASE_SHA` 固定为预消融提交 `a01950a1afab092ae4296b29a00c1b9da74fd7ab`，与 M0 基线快照逐字节一致），`b` = 消融后 Profile（当前 worktree，含 round-1/round-2 返修改动）。round 2 起不再使用浮动 `HEAD:`（任务提交后 HEAD 会变成消融后内容）。
- 两侧 Profile 输入的 sha256 固化在本目录 `profiles.sha256`（build 时同时写入 replay 根目录）：

  | 侧 | 语言 | sha256 |
  |---|---|---|
  | before | go | `f44b73315a3c36195a03c567b90e2331c93c206f4c3696593681da5c745b57c5` |
  | after | go | `284539dfa1373ee77894df30e849f33735242f04398faf44cbfe26624bd4dc93` |
  | before | python | `b814bba1c6db61798f73cd37bc7b3583fc7cc2df39c4adac63f2f54f329d8f00` |
  | after | python | `d92c2105eb7f3e79e73e049afdb9bf28c4c645cae3f2b417d5753b96b6490b94` |

- 映射表只在 `build-replay.sh` 与本文件中记录，不进入工作区。

## 执行与证据

- 构建：`sh build-replay.sh [target-dir] [scenario ...]`（确定性；S5 双侧 `uv sync`）。安全语义（round 2）：只创建新目录，目标已存在即拒绝（exit 2），脚本内无任何删除操作；可选场景参数支持定向重建。每个工作区有 2 个 commit（fixture baseline + project profile），`map.tsv` 记录基线 SHA，`profiles.sha256` 记录两侧 Profile 哈希。
- 采集：`sh capture.sh [target-dir]`，输出到 `runs/`（`CAPTURE_RUNS` 可改写目标，供自测避免污染证据）。退出契约（round 2）：0 = 全部解析+全部 VERIFY PASS；1 = 至少一个 VERIFY FAIL；2 = map.tsv 缺失/解析校验失败（key/lang/base 严格校验，分隔符用运行时 `printf '\t'`，不依赖源码里的不可见字面量）。任何子步失败都会计入结果，不会被后续命令或辅助命令的成功状态掩盖。
- 工具自测（故意失败的 fixture 验证非零退出）：`tooling-selftest.txt` —— 构建 exit 0、重复构建拒绝 exit 2、含内置红 fixture 的采集 `s3 VERIFY FAIL` → exit 1、篡改分隔符后解析拒绝 exit 2。
- 每个运行保存到 `runs/<scene><v>-*`：(1) agent 最终输出；(2) 全量变更 `git diff <基线SHA>`（含 RUNLOG.md）；(3) 客观验证命令输出。
- 对照判定（逐场景否决条件）写入 TASK-0026 Execution Record —— 契约规定对照结果写在任务文件内，本目录只存 protocol 与原始证据，不新建报告。

## 场景与否决条件（来自 M3 表；场景 6 为机械回放，由 UpgradeMechanismTest 承载，不进模型回放）

| 场景 | fixture（固定 repo 输入） | 固定 task 输入 | 否决条件 |
|---|---|---|---|
| s1 Go 低风险修改 | stdlib-only 既有仓库（约定 README/Makefile/apierr/writeJSON） | 新增 `GET /healthz`，按仓库约定，跑仓库验证入口 | 后版强推默认栈或额外依赖 |
| s2 Python 新项目 | 只有 README 的空仓库 | 从零启动 `GET /items`，最小实现，说明工具链与验证 | 后版以"repo 可推导"为由丢失 fallback，或超出任务需要初始化 |
| s3 多 module/workspace | go.work + moda(过)/modb(败)，根目录 `go test ./...` 必然报错 | 找出失败测试、修复并说明覆盖范围 | 根目录一次测试被误当全覆盖 |
| s4 并发/取消/资源 | 泄漏 Poller（无停止路径、错误丢弃、测试无清理） | 修正生命周期 + 关闭行为测试 | 任一保留的风险约束被漏掉或改变 |
| s5 Python API/边界 | FastAPI 仓库（pyproject/uv.lock/README 测试入口） | 新增分页 `GET /books` + docstring/注释 | 安全/兼容退化或重复 owner 回归（表达仍归 Policy） |

## 重跑规则与限制

- 仅机械性无效（harness 违例、工具错误、环境失败）可重跑；触发否决条件本身不是重跑理由。任何重跑都会记录。
- 限制：单次 A/B 采样（契约明示无需大型 benchmark）、判定人未盲、模型输出存在随机性；`b` 侧若触发否决，先核对 Profile 文本是否真的缺失该约束（根因），再决定结论。

## round 2 修订（工具链修复 + s5 补证）

1. **P1 构建安全**：`build-replay.sh` 不再 `rm -rf` 传入路径；默认 `mktemp -d` 新目录，显式目标已存在即拒绝。
2. **P1 采集可靠性**：`capture.sh` 修复分隔符（运行时 `printf '\t'` + key/lang/base 严格校验，解析失败 exit 2）、s2 pytest 失败不再被吞（`|| true` 移除且子步状态不被后续命令覆盖）、VERIFY FAIL 汇总为非零退出；自测证据 `tooling-selftest.txt`。
3. **P2 基线固定**：`BASE_SHA` 钉在预消融提交 `a01950a1afab092ae4296b29a00c1b9da74fd7ab`，两侧 Profile sha256 记录于 `profiles.sha256`（上表）。
4. **P2 s5 补 Comment Policy**：fixture v2 在两侧各加入同一份（sha256 `22047dca84060762972e0375677ba2bc2819ba23c6b75a781f68081a2f8aede0`）`docs/engineering/code-comments.md`（由 trellium `render_profile_document` 渲染自 zh 模板，roots=`app, tests`，与目标项目生成物同源）。定向重跑 s5（replay root 2：`/tmp/trellium-0026-replay-r2`，scenario 参数只建 s5）；两侧除 `AGENTS.md` 外逐字节一致（`diff -r` 排除 `.venv` 等环境产物后为空，两侧 Policy `cmp` 相同）。round 1 的 s5 原始输出已归档至 `runs/round1-superseded/`（fixture 不完整时的采集，按机械性无效重跑规则被取代）；s1–s4 沿用 round 1 运行，但 patch/verify 已用修复后的工具原位重新采集（行数与 round 1 逐项一致，10/10 VERIFY PASS，exit 0）。
5. `prompts.md` 未改动：固定任务文本与 harness 规则保持逐字。
