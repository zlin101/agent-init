# Profile - Python Backend

## 定位

本 profile 适用于 Python 后端、API 服务、Agent 后端、数据服务或类似项目。

核心协议保持语言无关；本文件只提供 Python 项目的默认值，不强制固定框架或目录模板。

工程选择发生冲突时，依次遵循任务契约和项目 Agent 规则、仓库已有构建与 CI 契约、稳定的本地代码模式，最后才使用本 profile 的默认值。

## 默认技术栈

| 类别 | 默认值 |
|---|---|
| 语言 | Python，最低版本以项目 `pyproject.toml` 的 `requires-python` 为准 |
| 包管理 | uv |
| Web 框架 | 需要 HTTP API 时使用 FastAPI |
| 数据模型 | Pydantic v2 |
| 配置管理 | pydantic-settings |
| 测试 | pytest |
| 异步测试 | 需要时使用 pytest-asyncio |
| HTTP 测试 | 需要时使用 httpx + ASGITransport |
| 格式化 | Black |
| import 排序 | isort |
| Lint | flake8 |

具体工具版本下限由项目 `pyproject.toml` 决定，本 profile 不锁定版本。项目真实需要前，不要添加运行时框架依赖。

## 进入项目时先确认

修改前先读取项目的 `AGENTS.md`、README、CI、Makefile 或 Taskfile 和 `pyproject.toml`，再确认运行环境（解释器、入口、质量入口；事实来源为仓库 `pyproject.toml`、`uv.lock`、CI 配置与当前解释器、入口的实际查询）。

执行原则：

- `pyproject.toml`、`uv.lock`、CI 和仓库验证脚本是实际构建契约，本 profile 不能覆盖它们。
- 确认项目入口（如 `uv run uvicorn <app>:<asgi>`）和已配置的质量入口（如 `make test`、`make lint`）。
- 既有项目优先沿用当前的目录布局、依赖和工具配置；只有任务需要时才调整。
- 如发现文档与实现不一致，先指出差异，再继续。

## 包管理

使用 `uv`，并将 `pyproject.toml` 和 `uv.lock` 纳入版本控制。

**所有包管理操作通过 `uv`，不使用 `pip` 或 `poetry` 作为项目依赖管理方式。**

约束：

- 生成代码引入新依赖时，明确告知执行 `uv add`；不在代码注释或文档中写 `pip install`。
- 除非项目明确停止使用 `uv`，不推荐 `pip install` 作为项目依赖管理方式。
- 添加、升级或移除依赖后运行 `uv sync`，并审查 `uv.lock` 的变更。
- 不手工编辑 `uv.lock`。

## 推荐结构

遵循仓库既有结构；新结构按需创建，不预先搭建空的分层骨架（`app/`、`tests/` 等只在任务需要时建立）。

## 分层和依赖方向

推荐依赖方向：API 路由 → Service 业务编排 → Schema/领域层 → Repository/Client 数据与外部系统 → 外部系统。

约束：

- API 路由只负责路由注册、参数校验、调用 Service 层和返回响应，不写复杂业务逻辑。
- API 路由不直接访问数据库或外部系统。
- Service 层负责编排业务流程和事务边界。
- Repository 层负责数据访问；Client 或 Adapter 层负责外部系统。
- Core 层负责配置、日志和基础设施。
- 依赖通过构造函数或框架的依赖注入传入，不创建全局单例。

## API 与数据模型规范

以下为框架无关的原则；使用 FastAPI 时以它为实现方式。

RESTful URL：

- 使用复数名词、小写、连字符分隔。
- 版本号放前缀，如 `/api/v1/`。
- 资源动作通过 HTTP 方法和路径表达，不在 URL 里编码动词。

统一响应格式：

- 响应体用 Pydantic 模型定义，让框架自动生成准确的接口文档。
- 公共结构（分页、错误响应等）集中在模型中定义，避免各接口各自造结构。

Pydantic v2 模型：

- 使用 `Field()` 定义字段；公开 API 的字段必须加 `description`，需要时提供 `examples`。
- 使用 `model_config` 配置模型，不使用 v1 风格的内嵌 `Config` 类。

## 配置管理

配置必须集中管理，使用 `pydantic-settings` 从环境变量读取并提供合理默认值。

- 端口、URL、路径、模型名称、功能开关、超时时间等通过 `Settings` 读取，不硬编码。
- 使用 `env_prefix` 划分配置命名空间，前缀按项目命名。
- 敏感信息（API Key、Token、密码、连接串）通过环境变量或密钥管理系统注入，不写入仓库；这与通用配置约束一致。

## Python 风格

- 行宽上限 120 字符（Black、isort、flake8 一致）。
- 所有函数参数和返回值使用类型注解。
- IO 操作（网络、消息订阅、数据库）优先使用 `async/await`；不在 async 路径中调用同步阻塞 IO。
- 依赖通过框架的依赖注入（如 FastAPI `Depends`）传入，不创建全局单例。
- 不使用全局可变状态存储请求级数据。
- 运行日志使用集中或结构化 logger，不使用 `print` 代替服务日志。
- 注释、Doc Comment、docstring、TODO/FIXME、directive 与 API 文档表达规范由项目 Comment Policy（`docs/engineering/code-comments.md`）唯一拥有；纯注释/文档工作直接读它，公开 API 或行为与注释同时修改时与本 profile 并读。
- import 顺序由 isort 维护：标准库、第三方库、本项目模块。

## 异步与资源生命周期

- 长生命周期的后台任务（消息订阅、消费者、定时任务等）与应用生命周期绑定：在应用启动时建立连接、在关闭时优雅断开。
- 使用框架提供的生命周期钩子（如 FastAPI `lifespan`）管理这些任务，不使用裸全局变量持有连接。
- 获取资源的代码负责在所有返回路径释放它；优先使用 `async with` 等上下文管理器。
- 处理取消和超时：后台任务要有明确的停止条件，避免任务泄漏。
- 测试也要清理后台任务和外部连接。

## 错误处理

- 抛出具体的领域或业务异常，不用宽泛的 `Exception` 表达可预期错误。
- 在边界把领域异常统一映射为稳定的 HTTP 状态码和错误响应，不向响应泄露内部细节、SQL、路径或堆栈。
- 错误日志带上可追溯的上下文（如请求 id、实体 id）。
- 不依赖捕获异常的字符串内容做分支判断。

## 代码质量工具

- Black 格式化，isort 整理 import（`profile=black`，`line_length=120`）。
- flake8 检查：`max-line-length=120`、`max-complexity=10`，排除生成代码、迁移和虚拟环境目录。
- 项目已配置 `pre-commit` 时沿用其钩子（如 isort、flake8、大文件与私钥检测）；没有时不强制引入。

## 测试

- 测试放在 `tests/`，文件命名为 `test_<module>.py`。
- 共享 setup 放入 `conftest.py`，用 fixture 管理公共依赖。
- 外部依赖（数据库、消息系统、LLM API、网络服务）必须 mock 或 fake，单元测试可独立、确定、可重复运行。
- HTTP 接口测试使用 httpx + ASGITransport，不真实监听端口。
- 核心逻辑设定覆盖率目标（如 >80%），具体门槛由项目决定；测试与覆盖率入口优先使用 `pyproject.toml`/Makefile 中已配置的命令。

## 完成标准

- 改动文件已用 Black/isort 格式化，flake8 通过。
- 受影响测试通过，核心逻辑覆盖率未回退。
- 依赖变更（`uv add` / `uv remove`）产生的 `uv.lock` diff 已审查。
- 异步路径、资源释放、错误映射和外部边界的失败路径已按变更风险验证。
- 公开 API、配置、数据模型或部署方式发生变化时，相关文档与 vault 记忆已同步。
