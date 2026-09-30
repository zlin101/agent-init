# Profile - Python Backend

## Purpose and precedence

Use this profile for Python backends, APIs, agents, and data services. It provides defaults, not a mandatory framework or skeleton. Resolve conflicts through the task contract and Agent rules, repository build/CI contracts, stable local patterns, then this profile.

## Toolchain and entry checks

The Python floor comes from `pyproject.toml`. Prefer the repository's existing tooling; the default stack is uv, FastAPI when HTTP is needed, Pydantic v2, pydantic-settings, pytest/pytest-asyncio, httpx ASGITransport, Black, isort, and flake8. Do not add runtime frameworks before they are needed.

Read AGENTS, README, CI, Makefile/Taskfile, and `pyproject.toml`; inspect `uv sync`, the Python version/interpreter, application entrypoint, and established test/lint commands. Project configuration, lockfile, and CI are the real contract. Report documentation drift before proceeding.

## Packages and dependencies

Manage project dependencies through uv, committing `pyproject.toml` and `uv.lock`. Use `uv add`, `uv add --dev`, `uv sync`, `uv run`, and `uv lock`; do not hand-edit the lockfile or silently switch to pip/Poetry. After add/upgrade/removal, sync and review the lock diff.

Create only needed modules. Keep application/lifecycle assembly at the entrypoint; routes handle registration, validation, service calls, and responses; services own business orchestration and transaction boundaries; repositories own persistence; clients/adapters own external systems; core owns configuration/logging/infrastructure; schemas own boundary models. Routes do not contain complex business logic or directly access databases/external systems. Inject dependencies; do not use mutable global singletons.

## API and models

Use plural lowercase resource URLs with hyphens, version prefixes such as `/api/v1`, and HTTP methods rather than action verbs in URLs. Define response/error/pagination contracts with Pydantic models so generated API documentation is accurate. In Pydantic v2, describe public fields with `Field` and use `model_config`, not the v1 inner `Config` class. Treat field names, optionality, validation, unknown-field behavior, errors, and status codes as public contracts.

## Configuration and security

Centralize configuration through pydantic-settings/environment variables with a project namespace. Do not hardcode ports, URLs, paths, model names, feature flags, or timeouts when they are deployment configuration. Inject API keys, tokens, passwords, and connection strings through environment/secrets systems; never commit or log them.

## Style, async, and documentation

Follow the repository formatter/linter; defaults are Black/isort/flake8 with consistent 120-character configuration. Type all function parameters and returns. Prefer async for network, messaging, and database IO and never call blocking synchronous IO on an async path. Use centralized/structured logging, not `print`.

Comment, docstring, TODO/FIXME, and API-documentation expression guidance is owned solely by the project's Comment Policy (`docs/engineering/code-comments.md`); read it alone for pure documentation work, and together with this profile when a public API changes or behavior and comments change together.

## Async and resource lifecycle

Bind consumers, subscriptions, schedulers, and connections to application startup/shutdown using framework lifecycle hooks such as FastAPI lifespan, not naked globals. The acquirer releases resources on every return path; prefer `with`/`async with`. Every background task needs ownership, cancellation, timeout, stop, error, and cleanup paths. Tests clean up tasks and external connections.

## Errors

Raise specific domain/business exceptions for expected failures. At system boundaries map them to stable HTTP status codes and response models without leaking SQL, paths, secrets, or stacks. Include safe trace context such as request/entity IDs in logs. Never branch on exception-message strings and do not catch broad `Exception` when a narrower recovery boundary exists.

## Quality and tests

Use Black, isort, and flake8 through the project's configured commands; honor existing pre-commit hooks and exclusions for generated/migration/virtual-environment files. Put tests under `tests/` as `test_<module>.py`, share setup through fixtures, and mock/fake databases, queues, LLMs, internet services, and developer infrastructure. Test HTTP APIs through httpx ASGITransport without real listeners. Cover async cancellation, timeouts, cleanup, error mapping, and resource release. Coverage targets belong to the project, not this profile.

Run repository-defined gates first. Otherwise run `uv run black .`, `uv run isort .`, `uv run flake8 .`, and `uv run pytest` (plus the configured coverage command). Review `uv.lock` for dependency changes and synchronize API/config/model/deployment documentation and Vault decisions when those contracts change.
