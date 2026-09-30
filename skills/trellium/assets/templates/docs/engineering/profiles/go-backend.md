# Profile - Go Backend

## Purpose and precedence

Use this profile for Go backends, APIs, services, CLIs, agents, and data services. It supplies defaults, not a mandatory framework or directory skeleton. Resolve conflicts in this order: the task contract and project Agent rules, repository build/CI contracts, stable local patterns, then this profile.

## Default toolchain

- The minimum Go version comes from `go.mod`; honor any `toolchain` directive.
- Use Go Modules and any existing `go.work` workspace.
- Prefer `net/http`, ordinary structs, standard configuration facilities, `log/slog` when supported, `testing`, `httptest`, `gofmt`, and `go vet` unless the repository already has established alternatives.
- Do not add a third-party dependency when the standard library solves the problem clearly.

## Entering a project

Read AGENTS, README, CI, Makefile/Taskfile, then inspect `go version` and `go env GOMOD GOWORK GOFLAGS`. Determine whether the repository is one module, multiple modules, or a workspace before choosing a command directory. Treat `go.mod`, `go.work`, CI, build tags, target GOOS/GOARCH, CGO settings, generators, and private-module configuration as the real build contract. Run `go list ./...` only from a confirmed module context.

## Modules, workspaces, and dependencies

- Commit `go.mod` and generated `go.sum`; never edit `go.sum` manually.
- Create one module unless publication or ownership needs justify more.
- Do not invent a module path under a domain the project does not control.
- After dependency changes, run `go mod tidy` in each affected module and review both module files.
- Do not upgrade dependencies without a version and compatibility rationale.
- Do not casually change `go` or `toolchain` directives.
- Keep `replace` directives documented and free of unexplained machine-local paths or long-lived forks.
- In a workspace, respect `use` and `replace`; change `go.work` only when the task crosses module boundaries and review `go.work.sum` too.

## Packages and structure

Put executable assembly in `cmd/<name>/main.go`, keeping it focused on wiring, startup, and graceful shutdown. Put module-private code under `internal/`. Do not create `pkg/` by default; use public root/subpackages only for deliberately stable cross-module APIs. Name packages by responsibility or domain, not `util`, `common`, or `misc`. Avoid import cycles and create only directories the current task needs.

Logical dependency direction is transport to application/use-case to domain; adapters implement application-owned minimal interfaces and communicate with external systems. Handlers perform protocol conversion, validation, use-case calls, and response mapping—not complex business logic. Application code owns orchestration and transaction boundaries. Repositories own persistence; clients/adapters own external systems. Define interfaces at the consumer, only when substitution is needed. Prefer explicit constructors and concrete return types; avoid mutable global singletons and hidden initialization order.

## Go style

- Format changed Go files with `gofmt` (or the repository's existing `goimports`).
- Comment, doc comment, docstring, TODO/FIXME, directive, and API-documentation expression guidance is owned solely by the project's Comment Policy (`docs/engineering/code-comments.md`); read it alone for pure documentation work, and together with this profile when a public API changes or behavior and comments change together.
- Prefer useful zero values. Use pointers for mutation, identity, material copy cost, or a meaningful unset state.
- Preserve API distinctions among nil/empty slices and maps, especially during serialization.
- Do not hide network calls, goroutines, or material initialization in `init()`.
- Use generics only for real duplication reduction without readability loss.
- Do not use panic for expected business errors. Use structured service logging rather than `fmt.Println`.
- Inject clocks, randomness, filesystems, and external calls when deterministic tests require a boundary.

## Errors

Handle, return, or visibly and intentionally ignore every error. Wrap with `%w` at boundaries that add operation meaning, then use `errors.Is`/`errors.As`; never branch on error strings. Avoid redundant wrapping at every layer. Public APIs expose stable codes or types without SQL, paths, secrets, stacks, or internal implementation details. Define sentinel/custom errors only when callers genuinely need to branch.

## Resource lifecycle

The successful acquirer owns release on every return path. Arrange `defer` promptly, but close short-lived loop resources per iteration. Do not discard meaningful `Close`, `Commit`, or flush errors. Close HTTP response bodies after a successful response and consume/manage them when connection reuse matters. Close database rows, check iteration errors, and make commit/rollback/context-cancel behavior explicit. Timers, tickers, subscriptions, workers, and test resources need a stop/cleanup path.

## Context and concurrency

Pass `context.Context` explicitly as the first parameter named `ctx`; do not store it in structs unless an existing interface forces that shape. Propagate entry contexts instead of replacing them with `context.Background`, and reserve context values for cross-boundary request metadata. Every goroutine needs an owner, stop condition, error path, cancellation/timeout strategy, result collection, and cleanup. The complete sender owns channel closure; receivers do not close channels they do not own, and send/close must be synchronized. Prefer ownership isolation; otherwise document mutex-protected invariants. For concurrency changes, exercise cancel, timeout, close, and error paths and run `go test -race ./...` where supported; never mask timing with sleeps.

## HTTP and service lifecycle

Configure suitable header/read/write/idle/request timeouts, designing streaming separately. Limit request-body size and decode/validate at the boundary. Treat JSON names, optionality, and unknown-field behavior as API contracts. Propagate request context and set external-call timeouts. Reuse `http.Client`/Transport instead of creating connection pools per request. On shutdown, stop new traffic, perform deadline-bound graceful shutdown, and wait for managed goroutines. Responses and logs must not leak secrets, connection strings, internal paths, or stacks.

## Tests and verification

Place `*_test.go` beside code. Use standard `testing`, table tests, `t.Run`, `t.Helper`, and `t.Cleanup`; parallelize only independent tests. Choose same-package tests for internals and external-package tests for public contracts. Use `httptest` and local fakes/stubs/servers; unit tests never call real internet, LLM, or developer infrastructure. Fuzz parsers/codecs/input boundaries, but retain deterministic tests.

Run repository-defined verification first. Otherwise, from each affected module, use `gofmt`, `go test ./...`, `go test -race ./...` when relevant, `go vet ./...`, and `go build ./...`. Do not assume one root command covers every module. Run `go mod tidy` for dependencies, existing `govulncheck` when configured, target builds for platform/tags/CGO changes, pinned generation commands for generated code, and compatibility/docs/examples checks for public packages. Review every `go.mod`, `go.sum`, `go.work`, and `go.work.sum` change.
