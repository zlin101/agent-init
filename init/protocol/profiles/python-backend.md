# Profile - Python Backend

## 定位

本 profile 适用于 Python 后端、API 服务、Agent 后端、数据服务或类似项目。

核心协议保持语言无关；本文件只提供 Python 默认值。

## 默认技术栈

| 类别 | 默认值 |
|---|---|
| 语言 | Python |
| 包管理 | uv |
| Web 框架 | 需要 API 时使用 FastAPI |
| 数据模型 | Pydantic |
| 配置管理 | pydantic-settings |
| 测试 | pytest |
| 异步测试 | 需要时使用 pytest-asyncio |
| HTTP 测试 | 需要时使用 httpx + ASGITransport |
| 格式化 | Black |
| import 排序 | isort |
| Lint | flake8 |

项目真实需要前，不要添加运行时框架依赖。

## 包管理

使用 `uv`。

允许命令：

```bash
uv add <package>
uv add --dev <package>
uv sync
uv run <command>
uv lock
```

除非项目明确停止使用 `uv`，不要推荐 `pip install` 作为项目依赖管理方式。

## 推荐结构

```text
app/
  main.py
  api/
  core/
  schemas/
  services/
  repositories/
  clients/
  utils/
tests/
  conftest.py
  test_*.py
```

只创建当前任务真正需要的目录。

## 分层

推荐依赖方向：

```text
API Layer
  -> Service Layer
    -> Domain / Engine Layer
      -> Repository / Client Layer
        -> External Systems
```

约束：

- API 路由不写复杂业务逻辑。
- API 路由不直接访问数据库或外部系统。
- Service 层负责编排流程。
- Repository 层负责数据访问。
- Client 或 Adapter 层负责外部系统。
- Core 层负责配置、日志和基础设施。

## Python 风格

- 函数参数和返回值使用类型注解。
- 优先小函数和清晰职责。
- 运行日志使用集中 logger，不用 `print`。
- 避免全局 Service 单例。
- 避免全局可变请求状态。
- 注释保持克制，只解释不直观的内容。

## 测试

- 测试放在 `tests/`。
- 测试文件命名为 `test_<module>.py`。
- 共享 setup 需要时放入 `conftest.py`。
- mock 外部依赖。
- 单元测试不真实调用 LLM API 或网络服务。

常用命令：

```bash
uv run pytest
uv run pytest --cov=app
uv run black .
uv run isort .
uv run flake8 .
```
