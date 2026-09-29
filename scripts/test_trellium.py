from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager, redirect_stderr, redirect_stdout
import importlib.util
from io import StringIO
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import cast
import unittest
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).with_name("trellium.py")
SPEC = importlib.util.spec_from_file_location("agent_init", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {SCRIPT_PATH}")
agent_init = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agent_init)


def state_block(payload: dict | None = None, *, text: str | None = None) -> str:
    body = text if text is not None else json.dumps(payload, indent=2)
    return f"<!-- trellium-task-state\n{body}\n-->"


def policy_block(payload: dict | None = None, *, text: str | None = None) -> str:
    body = text if text is not None else json.dumps(payload, indent=2)
    return f"<!-- trellium-policy\n{body}\n-->"


def tracked_policy() -> str:
    return policy_block({"schema_version": 1, "task_storage": "tracked"})


def local_policy() -> str:
    return policy_block({"schema_version": 1, "task_storage": "local"})


def v2_policy(mode: str) -> str:
    return policy_block({"schema_version": 2, "storage_mode": mode})


def private_policy() -> str:
    return v2_policy("private")


def valid_state(task_id: str = "TASK-0001", lifecycle: str = "draft", **overrides) -> dict:
    payload = {
        "schema_version": 1,
        "task_id": task_id,
        "level": "B",
        "authority_level": 2,
        "lifecycle": lifecycle,
    }
    payload.update(overrides)
    for key, value in list(payload.items()):
        if value is None:
            del payload[key]
    return payload


def build_runtime(
    focus: str = "ADOPTION",
    recent: tuple[str, ...] = ("did a thing",),
) -> str:
    lines = [
        "# Runtime Context",
        "",
        "## Focus",
        "",
        f"- {focus}",
        "",
        "## Recent Changes",
        "",
    ]
    lines += [f"- {item}" for item in recent]
    return "\n".join(lines) + "\n"


class TargetTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_agent_init(self, *arguments: str) -> tuple[int, str, str]:
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = agent_init.main(list(arguments))
        return code, out.getvalue(), err.getvalue()

    @staticmethod
    def snapshot(root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

    def adopt(self, target: Path, *extra: str) -> tuple[int, str, str]:
        return self.run_agent_init("adopt", str(target), *extra)

    def read_stamp(self, target: Path) -> dict:
        return json.loads(
            (target / agent_init.STAMP_RELATIVE).read_text(encoding="utf-8")
        )

    @contextmanager
    def patched_templates(self) -> Iterator[Path]:
        templates = self.root / "templates"
        shutil.copytree(agent_init.TEMPLATES_ROOT, templates, dirs_exist_ok=True)
        with patch.object(agent_init, "TEMPLATES_ROOT", templates):
            yield templates


class AgentInitTest(TargetTestCase):
    def test_adopt_creates_expected_files_and_is_idempotent(self) -> None:
        target = self.root / "project"
        target.mkdir()
        (target / "README.md").write_text("# Demo\n\nA demo project.\n", encoding="utf-8")

        code, _, err = self.adopt(target)

        self.assertEqual(code, 0, err)
        expected = {
            "AGENTS.md",
            "README.md",
            "skills/agent-task/SKILL.md",
            "vault/.agent-init.json",
            "vault/collaboration.md",
            "vault/decisions.md",
            "vault/governance.md",
            "vault/handoff.md",
            "vault/index.md",
            "vault/parked.md",
            "vault/project.md",
            "vault/runtime.md",
            "vault/tasks/README.md",
        }
        first_snapshot = self.snapshot(target)
        self.assertEqual(set(first_snapshot), expected)
        self.assertIn("vault/index.md", first_snapshot["AGENTS.md"].decode("utf-8"))

        code, out, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 0, err)
        self.assertEqual(self.snapshot(target), first_snapshot)
        self.assertIn("changed: 0", out)

    def test_adopt_with_go_profile_generates_complete_profile_and_compat_carrier(self) -> None:
        target = self.root / "project"
        target.mkdir()

        code, _, err = self.adopt(target, "--profile", "go-backend=.")

        self.assertEqual(code, 0, err)
        policy_path = target / "docs/engineering/code-comments.md"
        self.assertTrue(policy_path.is_file())
        policy = policy_path.read_text(encoding="utf-8")
        self.assertIn("## 通用原则", policy)
        self.assertIn("## Go", policy)
        self.assertNotIn("## Python", policy)
        self.assertIn("`go-backend`: `.`", policy)
        agents = (target / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("docs/engineering/code-comments.md", agents)
        durable_path = target / "docs/engineering/profiles/go-backend.md"
        self.assertTrue(durable_path.is_file())
        durable = durable_path.read_text(encoding="utf-8")
        for heading in (
            "## 模块和依赖管理",
            "## 推荐结构",
            "## 分层和依赖方向",
            "## 错误处理",
            "## 资源生命周期",
            "## Context 和并发",
            "## HTTP 和服务生命周期",
            "## 测试",
            "## Go 风格",
        ):
            self.assertIn(heading, durable)
        self.assertIn("- Roots: `.`", durable)
        self.assertIn("docs/engineering/profiles/", agents)

        stamp = self.read_stamp(target)
        self.assertEqual(stamp["schema_version"], 2)
        self.assertEqual(
            stamp["profiles"],
            [
                {
                    "id": "go-backend",
                    "project_profile": "docs/engineering/profiles/go-backend.md",
                    "project_rules": "docs/engineering/code-comments.md",
                    "roots": ["."],
                    "source_hash": stamp["profiles"][0]["source_hash"],
                }
            ],
        )
        self.assertRegex(stamp["profiles"][0]["source_hash"], r"^[0-9a-f]{64}$")
        self.assertEqual(stamp["files"]["docs/engineering/code-comments.md"]["role"], "merge")

    def test_adopt_with_existing_agents_routes_complete_profile(self) -> None:
        target = self.root / "project"
        target.mkdir()
        (target / "AGENTS.md").write_text(
            "# My Service\n\nCustom user AGENTS content.\n",
            encoding="utf-8",
        )

        code, _, err = self.adopt(target, "--profile", "go-backend=services/api")

        self.assertEqual(code, 0, err)
        agents = (target / "AGENTS.md").read_text(encoding="utf-8")
        # User prose is preserved and the Trellium entry is appended, not
        # overwritten.
        self.assertIn("Custom user AGENTS content.", agents)
        # Both product classes exist (complete profile + compatibility
        # carrier), matching a fresh adoption.
        self.assertTrue((target / "docs/engineering/profiles/go-backend.md").is_file())
        self.assertTrue((target / "docs/engineering/code-comments.md").is_file())
        # The appended marker must route the complete profile (D-0011), not
        # only the compatibility carrier.
        self.assertIn("docs/engineering/profiles/", agents)
        self.assertIn("docs/engineering/code-comments.md", agents)

    def test_adopt_combines_multiple_profiles_and_roots_in_compat_carrier(self) -> None:
        target = self.root / "project"
        target.mkdir()

        code, _, err = self.adopt(
            target,
            "--profile",
            "go-backend=services/api",
            "--profile",
            "go-backend=cmd/operator",
            "--profile",
            "python-backend=services/model",
        )

        self.assertEqual(code, 0, err)
        policies = list(target.rglob("code-comments.md"))
        self.assertEqual(policies, [target / "docs/engineering/code-comments.md"])
        policy = policies[0].read_text(encoding="utf-8")
        self.assertEqual(policy.count("## Go"), 1)
        self.assertEqual(policy.count("## Python"), 1)
        for root in ("services/api", "cmd/operator", "services/model"):
            self.assertIn(f"`{root}`", policy)
        stamp = self.read_stamp(target)
        self.assertEqual([item["id"] for item in stamp["profiles"]], ["go-backend", "python-backend"])
        self.assertEqual(stamp["profiles"][0]["roots"], ["cmd/operator", "services/api"])
        self.assertEqual(stamp["profiles"][1]["roots"], ["services/model"])
        go_profile = (target / "docs/engineering/profiles/go-backend.md").read_text(encoding="utf-8")
        python_profile = (target / "docs/engineering/profiles/python-backend.md").read_text(encoding="utf-8")
        self.assertIn("`cmd/operator`, `services/api`", go_profile)
        self.assertNotIn("services/model", go_profile)
        self.assertIn("`services/model`", python_profile)
        self.assertNotIn("cmd/operator", python_profile)

    def test_adopt_without_profile_adds_no_engineering_profile_files(self) -> None:
        target = self.root / "project"
        target.mkdir()

        code, _, err = self.adopt(target)

        self.assertEqual(code, 0, err)
        self.assertFalse((target / "docs/engineering").exists())
        self.assertEqual(self.read_stamp(target)["profiles"], [])

    def test_adopt_rejects_invalid_or_duplicate_profile_selection_before_writes(self) -> None:
        invalid = (
            "unknown=.",
            "go-backend=/absolute",
            "go-backend=../escape",
            "go-backend=",
            "go-backend=services/`injected`",
            "go-backend=services/api\n## injected",
        )
        for index, value in enumerate(invalid):
            with self.subTest(value=value):
                target = self.root / f"invalid-{index}"
                target.mkdir()
                code, _, err = self.adopt(target, "--profile", value)
                self.assertEqual(code, 1)
                self.assertIn("profile", err.lower())
                self.assertEqual(self.snapshot(target), {})

        target = self.root / "duplicate"
        target.mkdir()
        code, _, err = self.adopt(
            target,
            "--profile",
            "go-backend=services/api",
            "--profile",
            "go-backend=services/api",
        )
        self.assertEqual(code, 1)
        self.assertIn("duplicate", err.lower())
        self.assertEqual(self.snapshot(target), {})

    def test_adopt_preserves_existing_comment_policy(self) -> None:
        target = self.root / "project"
        policy = target / "docs/engineering/code-comments.md"
        policy.parent.mkdir(parents=True)
        policy.write_text("project-owned policy\n", encoding="utf-8")

        code, _, err = self.adopt(target, "--profile", "go-backend=.")

        self.assertEqual(code, 0, err)
        self.assertEqual(policy.read_text(encoding="utf-8"), "project-owned policy\n")
        stamp = self.read_stamp(target)
        entry = stamp["files"]["docs/engineering/code-comments.md"]
        self.assertTrue(entry["observed"])
        self.assertEqual(entry["baseline"], agent_init.sha256_hex(b"project-owned policy\n"))

    def test_adopt_force_still_preserves_existing_comment_policy(self) -> None:
        target = self.root / "project"
        policy = target / agent_init.PROFILE_RULES_RELATIVE
        policy.parent.mkdir(parents=True)
        policy.write_text("project-owned policy\n", encoding="utf-8")

        code, _, err = self.adopt(
            target,
            "--force",
            "--profile",
            "go-backend=.",
        )

        self.assertEqual(code, 0, err)
        self.assertEqual(policy.read_text(encoding="utf-8"), "project-owned policy\n")
        self.assertTrue(self.read_stamp(target)["files"][agent_init.PROFILE_RULES_RELATIVE]["observed"])

    def test_repeated_adopt_without_profile_keeps_recorded_profiles(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target, "--profile", "go-backend=services/api")
        self.assertEqual(code, 0, err)
        before = self.snapshot(target)

        code, out, err = self.adopt(target)

        self.assertEqual(code, 0, err)
        self.assertEqual(self.snapshot(target), before)
        self.assertIn("changed: 0", out)
        self.assertEqual(self.read_stamp(target)["profiles"][0]["roots"], ["services/api"])

    def test_repeated_adopt_rejects_profile_reconfiguration_before_writes(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target, "--profile", "go-backend=services/api")
        self.assertEqual(code, 0, err)
        before = self.snapshot(target)

        code, _, err = self.adopt(target, "--profile", "python-backend=services/model")

        self.assertEqual(code, 1)
        self.assertIn("profile selections differ", err)
        self.assertEqual(self.snapshot(target), before)

    def test_dry_run_with_create_does_not_write_anything(self) -> None:
        target = self.root / "new-project"

        code, _, err = self.run_agent_init("adopt", str(target), "--create", "--dry-run")

        self.assertEqual(code, 0, err)
        self.assertFalse(target.exists())

    def test_create_builds_missing_target_safely(self) -> None:
        target = self.root / "nested/new-project"

        code, _, err = self.run_agent_init("adopt", str(target), "--create")

        self.assertEqual(code, 0, err)
        self.assertTrue((target / "AGENTS.md").is_file())
        self.assertTrue((target / "vault/runtime.md").is_file())

    def test_rejects_filesystem_root_target(self) -> None:
        filesystem_root = Path(self.root.anchor)

        code, _, err = self.run_agent_init("adopt", str(filesystem_root), "--dry-run")

        self.assertEqual(code, 1)
        self.assertIn("filesystem root", err)

    def test_adopt_uses_portable_fallback_without_dir_fd_support(self) -> None:
        target = self.root / "project"
        target.mkdir()

        with patch.object(agent_init, "ANCHORED_WRITES_SUPPORTED", False):
            code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 0, err)
        self.assertTrue((target / "AGENTS.md").is_file())
        self.assertTrue((target / "vault/runtime.md").is_file())

    @unittest.skipUnless(
        agent_init.ANCHORED_WRITES_SUPPORTED,
        "requires anchored write support",
    )
    def test_write_error_returns_partial_state_warning(self) -> None:
        target = self.root / "project"
        target.mkdir()

        with patch.object(agent_init, "atomic_copy_file_at", side_effect=OSError("disk full")):
            code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 1)
        self.assertIn("partial changes", err)
        self.assertIn("disk full", err)

    def test_adopt_appends_existing_agents_entry_once(self) -> None:
        target = self.root / "project"
        target.mkdir()
        agents_path = target / "AGENTS.md"
        agents_path.write_text("# Existing Rules\n\nKeep this section.\n", encoding="utf-8")

        code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 0, err)
        first_content = agents_path.read_text(encoding="utf-8")
        self.assertIn("Keep this section.", first_content)
        self.assertEqual(first_content.count(agent_init.AGENTS_MARKER_START), 1)

        code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 0, err)
        self.assertEqual(agents_path.read_text(encoding="utf-8"), first_content)

    def test_force_replaces_existing_generated_files(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.run_agent_init("adopt", str(target))
        self.assertEqual(code, 0, err)

        governance = target / "vault/governance.md"
        runtime = target / "vault/runtime.md"
        governance.write_text("custom governance\n", encoding="utf-8")
        runtime.write_text("custom runtime\n", encoding="utf-8")

        code, _, err = self.run_agent_init("adopt", str(target), "--force")

        self.assertEqual(code, 0, err)
        self.assertEqual(
            governance.read_bytes(),
            (agent_init.TEMPLATES_ROOT / "vault/governance.md").read_bytes(),
        )
        self.assertNotEqual(runtime.read_text(encoding="utf-8"), "custom runtime\n")

    def test_force_rejects_symlinked_vault_before_any_write(self) -> None:
        target = self.root / "project"
        outside = self.root / "outside"
        target.mkdir()
        outside.mkdir()
        sentinel = outside / "governance.md"
        sentinel.write_text("do not replace\n", encoding="utf-8")
        (target / "vault").symlink_to(outside, target_is_directory=True)

        code, _, _ = self.run_agent_init("adopt", str(target), "--force")

        self.assertEqual(code, 1)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "do not replace\n")
        self.assertFalse((target / "AGENTS.md").exists())
        self.assertFalse((target / "skills").exists())
        self.assertEqual(self.snapshot(outside), {"governance.md": b"do not replace\n"})

    def test_rejects_symlinked_agents_file_before_any_write(self) -> None:
        target = self.root / "project"
        outside = self.root / "outside"
        target.mkdir()
        outside.mkdir()
        sentinel = outside / "AGENTS.md"
        sentinel.write_text("external rules\n", encoding="utf-8")
        (target / "AGENTS.md").symlink_to(sentinel)

        code, _, _ = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 1)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "external rules\n")
        self.assertFalse((target / "vault").exists())
        self.assertFalse((target / "skills").exists())

    def test_rejects_hard_linked_agents_file_before_any_write(self) -> None:
        target = self.root / "project"
        outside = self.root / "outside"
        target.mkdir()
        outside.mkdir()
        sentinel = outside / "AGENTS.md"
        sentinel.write_text("external rules\n", encoding="utf-8")
        agents_path = target / "AGENTS.md"
        os.link(sentinel, agents_path)
        self.assertEqual(sentinel.stat().st_ino, agents_path.stat().st_ino)

        code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 1)
        self.assertRegex(err.lower(), r"hard link|multiple links|link count")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "external rules\n")
        self.assertFalse((target / "vault").exists())
        self.assertFalse((target / "skills").exists())

    def test_rejects_symlinked_skills_directory_before_any_write(self) -> None:
        target = self.root / "project"
        outside = self.root / "outside"
        target.mkdir()
        outside.mkdir()
        (target / "skills").symlink_to(outside, target_is_directory=True)

        code, _, _ = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 1)
        self.assertFalse((target / "AGENTS.md").exists())
        self.assertFalse((target / "vault").exists())
        self.assertEqual(self.snapshot(outside), {})

    @unittest.skipUnless(
        agent_init.ANCHORED_WRITES_SUPPORTED,
        "requires dir_fd and O_NOFOLLOW support",
    )
    def test_rejects_parent_symlink_added_after_preflight(self) -> None:
        target = self.root / "project"
        outside = self.root / "outside"
        target.mkdir()
        outside.mkdir()
        original_append = agent_init.append_agent_entry

        def append_then_swap(*args: object, **kwargs: object) -> str:
            result = original_append(*args, **kwargs)
            (target / "vault").symlink_to(outside, target_is_directory=True)
            return result

        with patch.object(agent_init, "append_agent_entry", side_effect=append_then_swap):
            code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 1)
        self.assertIn("safe write", err)
        self.assertEqual(self.snapshot(outside), {})

    @unittest.skipUnless(
        agent_init.ANCHORED_WRITES_SUPPORTED,
        "requires dir_fd and O_NOFOLLOW support",
    )
    def test_keeps_original_target_when_ancestor_is_swapped_after_open(self) -> None:
        container = self.root / "container"
        target = container / "project"
        redirected = self.root / "redirected"
        redirected_target = redirected / "project"
        moved_container = self.root / "original-container"
        target.mkdir(parents=True)
        redirected_target.mkdir(parents=True)
        original_validate = agent_init.validate_output_paths
        redirected_once = False

        def validate_then_redirect(*args: object, **kwargs: object) -> None:
            nonlocal redirected_once
            original_validate(*args, **kwargs)
            destinations = cast("list[Path]", args[1])
            if redirected_once or target / "AGENTS.md" not in destinations:
                return
            redirected_once = True
            container.rename(moved_container)
            container.symlink_to(redirected, target_is_directory=True)

        with patch.object(
            agent_init,
            "validate_output_paths",
            side_effect=validate_then_redirect,
        ):
            code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 0, err)
        self.assertTrue((moved_container / "project/AGENTS.md").is_file())
        self.assertFalse((redirected_target / "AGENTS.md").exists())

    def test_does_not_copy_content_from_symlinked_readme(self) -> None:
        target = self.root / "project"
        outside = self.root / "outside.env"
        target.mkdir()
        outside.write_text("TOKEN=outside-secret\n", encoding="utf-8")
        (target / "README.md").symlink_to(outside)

        code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 0, err)
        project = (target / "vault/project.md").read_text(encoding="utf-8")
        self.assertNotIn("outside-secret", project)
        self.assertIn("project project.", project)

    def test_does_not_copy_content_from_hard_linked_readme(self) -> None:
        target = self.root / "project"
        outside = self.root / "outside.env"
        target.mkdir()
        outside.write_text("TOKEN=outside-secret\n", encoding="utf-8")
        os.link(outside, target / "README.md")

        code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 0, err)
        project = (target / "vault/project.md").read_text(encoding="utf-8")
        self.assertNotIn("outside-secret", project)
        self.assertIn("project project.", project)


class UpgradeMechanismTest(TargetTestCase):
    def make_adopted_target(self) -> Path:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        return target

    def test_file_roles_cover_every_adopted_file(self) -> None:
        self.assertEqual(
            set(agent_init.FILE_ROLES),
            set(agent_init.TEMPLATE_FILES) | set(agent_init.RENDERED_FILES) | {"AGENTS.md"},
        )
        self.assertEqual(agent_init.WRITABLE_ROLES, {"marker", "merge", "template"})
        for relative, role in agent_init.FILE_ROLES.items():
            self.assertIn(role, agent_init.WRITABLE_ROLES | {"data"}, relative)

    def test_adopt_writes_stamp_with_roles_and_hashes(self) -> None:
        target = self.make_adopted_target()

        stamp = self.read_stamp(target)

        self.assertEqual(stamp["protocol_version"], agent_init.read_protocol_version())
        self.assertEqual(stamp["trust"], "versioned")
        self.assertEqual(stamp["schema_version"], 2)
        self.assertEqual(stamp["profiles"], [])
        self.assertEqual(set(stamp["files"]), set(agent_init.FILE_ROLES))
        for relative, entry in stamp["files"].items():
            expected_role = "merge" if relative == "AGENTS.md" else agent_init.FILE_ROLES[relative]
            self.assertEqual(entry["role"], expected_role)
        for relative in agent_init.TEMPLATE_FILES:
            expected = agent_init.sha256_hex((target / relative).read_bytes())
            self.assertEqual(stamp["files"][relative]["baseline"], expected)

    def test_diff_reports_in_sync_after_adopt(self) -> None:
        target = self.make_adopted_target()

        code, out, err = self.run_agent_init("diff", str(target))

        self.assertEqual(code, 0, err)
        self.assertIn("in_sync", out)
        self.assertIn("protected", out)

    def test_diff_reads_legacy_v1_stamp_without_profiles(self) -> None:
        target = self.make_adopted_target()
        stamp_path = target / agent_init.STAMP_RELATIVE
        stamp = self.read_stamp(target)
        stamp["schema_version"] = 1
        stamp.pop("profiles")
        stamp_path.write_text(json.dumps(stamp), encoding="utf-8")

        code, out, err = self.run_agent_init("diff", str(target))

        self.assertEqual(code, 0, err)
        self.assertIn("in_sync", out)

    def test_diff_rejects_inconsistent_profile_stamp_without_removing_policy(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target, "--profile", "go-backend=.")
        self.assertEqual(code, 0, err)
        stamp_path = target / agent_init.STAMP_RELATIVE
        stamp = self.read_stamp(target)
        stamp["profiles"] = []
        stamp_path.write_text(json.dumps(stamp), encoding="utf-8")
        policy = (target / agent_init.PROFILE_RULES_RELATIVE).read_bytes()

        code, out, err = self.run_agent_init("diff", str(target))

        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("without profile metadata", err)
        self.assertEqual((target / agent_init.PROFILE_RULES_RELATIVE).read_bytes(), policy)

    def test_diff_rejects_malformed_profile_metadata(self) -> None:
        target = self.make_adopted_target()
        stamp_path = target / agent_init.STAMP_RELATIVE
        stamp = self.read_stamp(target)
        stamp["profiles"] = {"id": "go-backend", "roots": ["."]}
        stamp_path.write_text(json.dumps(stamp), encoding="utf-8")

        code, _, err = self.run_agent_init("diff", str(target))

        self.assertEqual(code, 1)
        self.assertIn("profiles must be a list", err)

    def test_diff_rejects_malformed_profile_paths_and_file_roles(self) -> None:
        cases = (
            ("project_rules", "/outside.md", "invalid project_rules path"),
            ("project_profile", "../outside.md", "invalid managed path"),
            ("project_profile", "docs/engineering/profiles/python-backend.md", "invalid project_profile path"),
        )
        for index, (field, value, expected) in enumerate(cases):
            with self.subTest(field=field, value=value):
                target = self.root / f"profile-path-{index}"
                target.mkdir()
                code, _, err = self.adopt(target, "--profile", "go-backend=.")
                self.assertEqual(code, 0, err)
                stamp = self.read_stamp(target)
                stamp["profiles"][0][field] = value
                (target / agent_init.STAMP_RELATIVE).write_text(
                    json.dumps(stamp), encoding="utf-8"
                )

                code, _, err = self.run_agent_init("diff", str(target))

                self.assertEqual(code, 1)
                self.assertIn(expected, err)

        target = self.make_adopted_target()
        stamp = self.read_stamp(target)
        stamp["files"]["vault/index.md"]["role"] = "marker"
        (target / agent_init.STAMP_RELATIVE).write_text(
            json.dumps(stamp), encoding="utf-8"
        )

        code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, 1)
        self.assertIn("invalid role", err)

    def test_upgrade_preserves_local_edits_and_data_files(self) -> None:
        target = self.make_adopted_target()
        (target / "vault/runtime.md").write_text("# Evolved runtime\n", encoding="utf-8")
        (target / "vault/decisions.md").write_text("D-0001 keep this decision\n", encoding="utf-8")
        governance = (target / "vault/governance.md").read_text(encoding="utf-8")
        (target / "vault/governance.md").write_text(
            governance + "\n## Project Rules\n\n- Keep this local rule.\n", encoding="utf-8"
        )

        with self.patched_templates() as templates:
            (templates / "vault/index.md").write_text("new index template\n", encoding="utf-8")
            (templates / "vault/governance.md").write_text("new governance template\n", encoding="utf-8")
            code, out, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, agent_init.EXIT_CONFLICT, err)
        self.assertEqual((target / "vault/index.md").read_text(encoding="utf-8"), "new index template\n")
        self.assertIn("Keep this local rule.", (target / "vault/governance.md").read_text(encoding="utf-8"))
        self.assertEqual((target / "vault/runtime.md").read_text(encoding="utf-8"), "# Evolved runtime\n")
        self.assertIn(
            "D-0001 keep this decision", (target / "vault/decisions.md").read_text(encoding="utf-8")
        )

        version = agent_init.read_protocol_version()
        proposals = list((target / "vault/.upgrade" / version).glob("*.proposal.md"))
        self.assertEqual([path.name for path in proposals], ["vault__governance.md.proposal.md"])
        proposal_text = proposals[0].read_text(encoding="utf-8")
        self.assertIn("new governance template", proposal_text)
        self.assertIn("Keep this local rule.", proposal_text)
        backup = target / agent_init.BACKUP_DIRECTORY / version / "vault/index.md"
        self.assertTrue(backup.is_file())
        self.assertNotEqual(backup.read_text(encoding="utf-8"), "new index template\n")

        stamp = self.read_stamp(target)
        self.assertEqual(
            stamp["files"]["vault/index.md"]["baseline"],
            agent_init.sha256_hex(b"new index template\n"),
        )
        self.assertTrue(stamp["files"]["vault/governance.md"]["pending"])

    def test_upgrade_refreshes_pristine_profile_policy(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target, "--profile", "go-backend=.")
        self.assertEqual(code, 0, err)
        policy_path = target / agent_init.PROFILE_RULES_RELATIVE
        before = policy_path.read_text(encoding="utf-8")

        with self.patched_templates() as templates:
            template = templates / agent_init.PROFILE_RULES_TEMPLATE
            template.write_text(
                template.read_text(encoding="utf-8").replace(
                    "禁止为了“看起来有注释”而注释。",
                    "禁止为了“看起来有注释”而注释。\n\n升级测试规则。",
                ),
                encoding="utf-8",
            )
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, 0, err)
        self.assertNotEqual(policy_path.read_text(encoding="utf-8"), before)
        self.assertIn("升级测试规则。", policy_path.read_text(encoding="utf-8"))
        stamp = self.read_stamp(target)
        self.assertEqual(
            stamp["files"][agent_init.PROFILE_RULES_RELATIVE]["baseline"],
            agent_init.sha256_hex(policy_path.read_bytes()),
        )

    def test_upgrade_proposes_profile_policy_when_local_and_upstream_changed(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target, "--profile", "go-backend=.")
        self.assertEqual(code, 0, err)
        policy_path = target / agent_init.PROFILE_RULES_RELATIVE
        policy_path.write_text(
            policy_path.read_text(encoding="utf-8") + "\n## Project Rule\n\nKeep this.\n",
            encoding="utf-8",
        )

        with self.patched_templates() as templates:
            template = templates / agent_init.PROFILE_RULES_TEMPLATE
            template.write_text(
                template.read_text(encoding="utf-8").replace(
                    "禁止为了“看起来有注释”而注释。",
                    "禁止为了“看起来有注释”而注释。\n\n上游新增规则。",
                ),
                encoding="utf-8",
            )
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, agent_init.EXIT_CONFLICT, err)
        self.assertIn("Keep this.", policy_path.read_text(encoding="utf-8"))
        proposal = (
            target
            / agent_init.PROPOSAL_DIRECTORY
            / agent_init.read_protocol_version()
            / "docs__engineering__code-comments.md.proposal.md"
        )
        self.assertTrue(proposal.is_file())
        text = proposal.read_text(encoding="utf-8")
        self.assertIn("上游新增规则。", text)
        self.assertIn("Keep this.", text)

    def test_upgrade_refreshes_pristine_complete_profile(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target, "--profile", "go-backend=services/api")
        self.assertEqual(code, 0, err)
        relative = agent_init.profile_document_relative("go-backend")
        profile_path = target / relative
        before = profile_path.read_text(encoding="utf-8")

        with self.patched_templates() as templates:
            source = templates / agent_init.PROFILE_DOCUMENT_TEMPLATE_DIRECTORY / "go-backend.md"
            source.write_text(source.read_text(encoding="utf-8") + "\nUpstream lifecycle rule.\n", encoding="utf-8")
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, 0, err)
        self.assertNotEqual(profile_path.read_text(encoding="utf-8"), before)
        self.assertIn("Upstream lifecycle rule.", profile_path.read_text(encoding="utf-8"))

    def test_upgrade_proposes_complete_profile_without_overwriting_customization(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target, "--profile", "go-backend=.")
        self.assertEqual(code, 0, err)
        relative = agent_init.profile_document_relative("go-backend")
        profile_path = target / relative
        profile_path.write_text(profile_path.read_text(encoding="utf-8") + "\nProject-owned rule.\n", encoding="utf-8")

        with self.patched_templates() as templates:
            source = templates / agent_init.PROFILE_DOCUMENT_TEMPLATE_DIRECTORY / "go-backend.md"
            source.write_text(source.read_text(encoding="utf-8") + "\nUpstream rule.\n", encoding="utf-8")
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, agent_init.EXIT_CONFLICT, err)
        self.assertIn("Project-owned rule.", profile_path.read_text(encoding="utf-8"))
        proposal = target / agent_init.PROPOSAL_DIRECTORY / agent_init.read_protocol_version() / "docs__engineering__profiles__go-backend.md.proposal.md"
        self.assertTrue(proposal.is_file())
        proposal_text = proposal.read_text(encoding="utf-8")
        self.assertIn("Upstream rule.", proposal_text)
        self.assertIn("Project-owned rule.", proposal_text)

    def test_legacy_v2_profile_stamp_adds_complete_profile_on_upgrade(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target, "--profile", "go-backend=.")
        self.assertEqual(code, 0, err)
        relative = agent_init.profile_document_relative("go-backend")
        (target / relative).unlink()
        stamp = self.read_stamp(target)
        stamp["files"].pop(relative)
        for item in stamp["profiles"]:
            item.pop("project_profile", None)
        (target / agent_init.STAMP_RELATIVE).write_text(json.dumps(stamp), encoding="utf-8")

        code, out, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, 0, err)
        self.assertIn(f"create {relative}", out)
        self.assertTrue((target / relative).is_file())
        self.assertEqual(self.read_stamp(target)["profiles"][0]["project_profile"], relative)

    def test_legacy_v2_preexisting_custom_profile_requires_proposal_then_is_tracked(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target, "--profile", "go-backend=.")
        self.assertEqual(code, 0, err)
        relative = agent_init.profile_document_relative("go-backend")
        profile_path = target / relative
        custom = "# Project-owned Go profile\n\nKeep this local rule.\n"
        profile_path.write_text(custom, encoding="utf-8")
        stamp = self.read_stamp(target)
        stamp["files"].pop(relative)
        for item in stamp["profiles"]:
            item.pop("project_profile", None)
        (target / agent_init.STAMP_RELATIVE).write_text(json.dumps(stamp), encoding="utf-8")

        code, out, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, agent_init.EXIT_CONFLICT, err)
        self.assertIn(f"proposal {agent_init.proposal_relative(agent_init.read_protocol_version(), relative)}", out)
        self.assertEqual(profile_path.read_text(encoding="utf-8"), custom)
        pending_stamp = self.read_stamp(target)
        self.assertTrue(pending_stamp["files"][relative]["pending"])
        proposal = target / agent_init.proposal_relative(agent_init.read_protocol_version(), relative)
        self.assertIn("Keep this local rule.", proposal.read_text(encoding="utf-8"))

        code, _, err = self.run_agent_init("upgrade", str(target), "--complete")

        self.assertEqual(code, 0, err)
        self.assertEqual(profile_path.read_text(encoding="utf-8"), custom)
        completed_stamp = self.read_stamp(target)
        self.assertEqual(completed_stamp["profiles"][0]["project_profile"], relative)
        self.assertFalse(completed_stamp["files"][relative]["pending"])
        self.assertTrue(completed_stamp["files"][relative]["observed"])
        core_paths, core_error = agent_init.stamp_core_paths(completed_stamp)
        self.assertIsNone(core_error)
        self.assertIn(relative, core_paths)

    def test_legacy_v2_preexisting_profile_symlink_is_rejected_without_leaking(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target, "--profile", "go-backend=.")
        self.assertEqual(code, 0, err)
        relative = agent_init.profile_document_relative("go-backend")
        profile_path = target / relative
        profile_path.unlink()
        secret = self.root / "secret.txt"
        secret.write_text("outside-secret-must-not-leak\n", encoding="utf-8")
        profile_path.symlink_to(secret)
        stamp = self.read_stamp(target)
        stamp["files"].pop(relative)
        for item in stamp["profiles"]:
            item.pop("project_profile", None)
        (target / agent_init.STAMP_RELATIVE).write_text(json.dumps(stamp), encoding="utf-8")

        code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, 1)
        self.assertIn("symbolic link", err)
        proposal_root = target / agent_init.PROPOSAL_DIRECTORY
        proposal_text = "".join(
            path.read_text(encoding="utf-8")
            for path in proposal_root.rglob("*")
            if path.is_file()
        ) if proposal_root.exists() else ""
        self.assertNotIn("outside-secret-must-not-leak", proposal_text)

    def test_legacy_v2_preexisting_profile_rejects_special_and_hardlinked_files(self) -> None:
        for kind in ("hardlink", "fifo"):
            with self.subTest(kind=kind):
                target = self.root / f"project-{kind}"
                target.mkdir()
                code, _, err = self.adopt(target, "--profile", "go-backend=.")
                self.assertEqual(code, 0, err)
                relative = agent_init.profile_document_relative("go-backend")
                profile_path = target / relative
                profile_path.unlink()
                secret = self.root / f"secret-{kind}.txt"
                secret.write_text(f"outside-{kind}-secret-must-not-leak\n", encoding="utf-8")
                if kind == "hardlink":
                    os.link(secret, profile_path)
                    expected_error = "multiple hard links"
                else:
                    os.mkfifo(profile_path)
                    expected_error = "not a regular file"
                stamp = self.read_stamp(target)
                stamp["files"].pop(relative)
                for item in stamp["profiles"]:
                    item.pop("project_profile", None)
                (target / agent_init.STAMP_RELATIVE).write_text(
                    json.dumps(stamp), encoding="utf-8"
                )

                code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

                self.assertEqual(code, 1)
                self.assertIn(expected_error, err)
                proposal_root = target / agent_init.PROPOSAL_DIRECTORY
                proposal_text = "".join(
                    path.read_text(encoding="utf-8")
                    for path in proposal_root.rglob("*")
                    if path.is_file()
                ) if proposal_root.exists() else ""
                self.assertNotIn(f"outside-{kind}-secret-must-not-leak", proposal_text)

    def test_upgrade_complete_marks_merged_files_observed(self) -> None:
        target = self.make_adopted_target()
        (target / "vault/governance.md").write_text("locally modified governance\n", encoding="utf-8")
        with self.patched_templates() as templates:
            (templates / "vault/governance.md").write_text("new governance template\n", encoding="utf-8")
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")
        self.assertEqual(code, agent_init.EXIT_CONFLICT, err)

        merged = "new governance template\nmerged with local edits\n"
        (target / "vault/governance.md").write_text(merged, encoding="utf-8")

        code, out, err = self.run_agent_init("upgrade", str(target), "--complete")

        self.assertEqual(code, 0, err)
        version = agent_init.read_protocol_version()
        stamp = self.read_stamp(target)
        entry = stamp["files"]["vault/governance.md"]
        self.assertFalse(entry["pending"])
        self.assertTrue(entry["observed"])
        self.assertEqual(entry["baseline"], agent_init.sha256_hex(merged.encode("utf-8")))
        self.assertEqual(stamp["protocol_version"], version)
        self.assertEqual(stamp["trust"], "versioned")

        # A merged file is user-owned: the next upstream change must propose,
        # never auto-replace.
        with self.patched_templates() as templates:
            (templates / "vault/governance.md").write_text("newer governance template\n", encoding="utf-8")
            code, out, err = self.run_agent_init("diff", str(target))
        self.assertEqual(code, agent_init.EXIT_CONFLICT, err)
        self.assertIn("conflict", out)
        self.assertEqual(
            (target / "vault/governance.md").read_text(encoding="utf-8"), merged
        )

        # The same upstream revision the merge already absorbed stays quiet.
        with self.patched_templates() as templates:
            (templates / "vault/governance.md").write_text("new governance template\n", encoding="utf-8")
            code, out, err = self.run_agent_init("diff", str(target))
        self.assertEqual(code, 0, err)
        self.assertIn("already absorbed", out)

    def test_upgrade_replaces_marker_region_and_keeps_user_content(self) -> None:
        # The marker flavor appears when adopt appends a section to an
        # existing user-owned AGENTS.md.
        target = self.root / "project"
        target.mkdir()
        agents_path = target / "AGENTS.md"
        agents_path.write_text("# Project Rules\n\nOwned by the project.\n", encoding="utf-8")
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        self.assertEqual(agents_path.read_text(encoding="utf-8").count(agent_init.AGENTS_MARKER_START), 1)

        def refreshed_section() -> str:
            return (
                f"{agent_init.AGENTS_MARKER_START}\n## Trellium\n\n"
                f"Refreshed entry text.\n{agent_init.AGENTS_MARKER_END}\n"
            )

        with patch.object(agent_init, "agent_entry_section", refreshed_section):
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, 0, err)
        text = agents_path.read_text(encoding="utf-8")
        self.assertIn("Owned by the project.", text)
        self.assertIn("Refreshed entry text.", text)
        self.assertEqual(text.count(agent_init.AGENTS_MARKER_START), 1)

        # A locally modified marker region is a conflict, not an auto-replace.
        text = agents_path.read_text(encoding="utf-8")
        marker_end = text.find(agent_init.AGENTS_MARKER_END)
        agents_path.write_text(
            text[:marker_end] + "- local note inside the region\n" + text[marker_end:], encoding="utf-8"
        )

        def newer_section() -> str:
            return (
                f"{agent_init.AGENTS_MARKER_START}\n## Trellium\n\n"
                f"Newer entry text.\n{agent_init.AGENTS_MARKER_END}\n"
            )

        with patch.object(agent_init, "agent_entry_section", newer_section):
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, agent_init.EXIT_CONFLICT, err)
        text = agents_path.read_text(encoding="utf-8")
        self.assertIn("- local note inside the region", text)
        self.assertNotIn("Newer entry text.", text)

    def test_upgrade_refuses_dirty_git_state(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("requires git")
        target = self.make_adopted_target()
        subprocess.run(["git", "init", "-q"], cwd=target, check=True)

        with self.patched_templates() as templates:
            (templates / "vault/index.md").write_text("new index template\n", encoding="utf-8")
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")
            self.assertEqual(code, 1)
            self.assertIn("uncommitted changes", err)
            self.assertNotEqual(
                (target / "vault/index.md").read_text(encoding="utf-8"), "new index template\n"
            )

            subprocess.run(["git", "add", "-A"], cwd=target, check=True)
            subprocess.run(
                ["git", "-c", "user.name=test", "-c", "user.email=test@example.com", "commit", "-qm", "adopt"],
                cwd=target,
                check=True,
            )
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, 0, err)
        self.assertEqual((target / "vault/index.md").read_text(encoding="utf-8"), "new index template\n")

    def test_baseline_unversioned_upgrades_conflict_only(self) -> None:
        target = self.make_adopted_target()
        (target / agent_init.STAMP_RELATIVE).unlink()
        (target / "vault/index.md").write_text("legacy local index\n", encoding="utf-8")

        code, _, err = self.run_agent_init("diff", str(target))
        self.assertEqual(code, 1)
        self.assertIn("baseline", err)

        code, _, err = self.run_agent_init("baseline", str(target))
        self.assertEqual(code, 0, err)
        stamp = self.read_stamp(target)
        self.assertEqual(stamp["trust"], "unversioned")
        self.assertIsNone(stamp["protocol_version"])
        self.assertTrue(stamp["files"]["vault/index.md"]["observed"])

        code, _, err = self.run_agent_init("baseline", str(target))
        self.assertEqual(code, 1)
        self.assertIn("already exists", err)

        with self.patched_templates() as templates:
            (templates / "vault/index.md").write_text("new upstream index\n", encoding="utf-8")
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, agent_init.EXIT_CONFLICT, err)
        self.assertEqual((target / "vault/index.md").read_text(encoding="utf-8"), "legacy local index\n")
        self.assertTrue(list((target / "vault/.upgrade").rglob("*.proposal.md")))

    def test_write_scope_guard_rejects_project_data(self) -> None:
        target = self.root / "project"
        (target / "vault").mkdir(parents=True)
        (target / "vault/runtime.md").write_text("# Runtime\n", encoding="utf-8")

        for relative in (
            "vault/runtime.md",  # existing project data
            "vault/tasks/TASK-0001.md",
            "vault/decisions/D-0001-x.md",
            "src/app.py",
            "docs/engineering/profiles/ruby-backend.md",
            "docs/engineering/profiles/../outside.md",
            agent_init.STAMP_RELATIVE,
            "vault/.upgrade/2026.08.0/vault__index.md.proposal.md",
            ".agent-init-backup/2026.08.0/vault/index.md",
        ):
            with self.assertRaises(agent_init.AdoptionError):
                agent_init.assert_upgrade_writable(target, relative)

        for relative in (
            "AGENTS.md",
            "vault/index.md",
            "vault/governance.md",
            "vault/tasks/README.md",
            "skills/agent-task/SKILL.md",
        ):
            agent_init.assert_upgrade_writable(target, relative)

        # Creating an absent data-role starter is allowed.
        with patch.dict(agent_init.FILE_ROLES, {"vault/parked.md": "data"}):
            agent_init.assert_upgrade_writable(target, "vault/parked.md")

    def test_upgrade_rejects_unselected_supported_profile_before_removal(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target, "--profile", "go-backend=.")
        self.assertEqual(code, 0, err)
        relative = agent_init.profile_document_relative("python-backend")
        path = target / relative
        content = "project-owned Python profile\n"
        path.write_text(content, encoding="utf-8")
        stamp = self.read_stamp(target)
        stamp["files"][relative] = {
            "role": "merge",
            "baseline": agent_init.sha256_hex(content.encode("utf-8")),
        }
        (target / agent_init.STAMP_RELATIVE).write_text(
            json.dumps(stamp), encoding="utf-8"
        )

        with patch.object(agent_init, "ANCHORED_WRITES_SUPPORTED", False):
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, 1)
        self.assertIn("outside the explicit managed-file set", err)
        self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_fallback_stamp_write_rejects_symlinked_parent_and_hardlink(self) -> None:
        stamp = {"schema_version": 2, "files": {}}

        symlink_target = self.root / "symlink-project"
        symlink_target.mkdir()
        external_vault = self.root / "external-vault"
        external_vault.mkdir()
        (symlink_target / "vault").symlink_to(external_vault, target_is_directory=True)
        with self.assertRaises(agent_init.AdoptionError):
            agent_init.write_stamp_file(symlink_target, stamp, None)
        self.assertFalse((external_vault / ".agent-init.json").exists())

        hardlink_target = self.root / "hardlink-project"
        (hardlink_target / "vault").mkdir(parents=True)
        external_stamp = self.root / "external-stamp.json"
        external_stamp.write_text("keep\n", encoding="utf-8")
        os.link(external_stamp, hardlink_target / agent_init.STAMP_RELATIVE)
        with self.assertRaises(agent_init.AdoptionError):
            agent_init.write_stamp_file(hardlink_target, stamp, None)
        self.assertEqual(external_stamp.read_text(encoding="utf-8"), "keep\n")

    def test_upgrade_rejects_unmanaged_profile_paths_without_anchored_writes(self) -> None:
        for index, relative in enumerate(
            (
                "docs/engineering/profiles/ruby-backend.md",
                "docs/engineering/profiles/../outside.md",
            )
        ):
            with self.subTest(relative=relative):
                target = self.root / f"project-{index}"
                target.mkdir()
                code, _, err = self.adopt(target)
                self.assertEqual(code, 0, err)
                path = target / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                content = f"project-owned {index}\n"
                path.write_text(content, encoding="utf-8")
                stamp = self.read_stamp(target)
                stamp["files"][relative] = {
                    "role": "merge",
                    "baseline": agent_init.sha256_hex(content.encode("utf-8")),
                }
                (target / agent_init.STAMP_RELATIVE).write_text(
                    json.dumps(stamp), encoding="utf-8"
                )

                with patch.object(agent_init, "ANCHORED_WRITES_SUPPORTED", False):
                    code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

                self.assertEqual(code, 1)
                expected_error = (
                    "invalid managed path"
                    if ".." in relative
                    else "outside the explicit managed-file set"
                )
                self.assertIn(expected_error, err)
                self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_upgrade_rejects_traversal_stamp_key_before_fallback_removal(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        victim = self.root / "victim.txt"
        content = "must survive\n"
        victim.write_text(content, encoding="utf-8")
        stamp = self.read_stamp(target)
        stamp["files"][".agent-init-backup/../../victim.txt"] = {
            "role": "merge",
            "baseline": agent_init.sha256_hex(content.encode("utf-8")),
        }
        (target / agent_init.STAMP_RELATIVE).write_text(json.dumps(stamp), encoding="utf-8")

        with patch.object(agent_init, "ANCHORED_WRITES_SUPPORTED", False):
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, 1)
        self.assertIn("invalid managed path", err)
        self.assertEqual(victim.read_text(encoding="utf-8"), content)

    def test_upgrade_rejects_internal_namespace_entries_before_fallback_removal(self) -> None:
        for index, relative in enumerate(
            (
                ".agent-init-backup/important.txt",
                "vault/.upgrade/manual.md",
            )
        ):
            with self.subTest(relative=relative):
                target = self.root / f"internal-namespace-{index}"
                target.mkdir()
                code, _, err = self.adopt(target)
                self.assertEqual(code, 0, err)
                path = target / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                content = f"project-owned {index}\n"
                path.write_text(content, encoding="utf-8")
                stamp = self.read_stamp(target)
                stamp["files"][relative] = {
                    "role": "merge",
                    "baseline": agent_init.sha256_hex(content.encode("utf-8")),
                }
                (target / agent_init.STAMP_RELATIVE).write_text(
                    json.dumps(stamp), encoding="utf-8"
                )

                with patch.object(agent_init, "ANCHORED_WRITES_SUPPORTED", False):
                    code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

                self.assertEqual(code, 1)
                self.assertIn("reserved internal namespace", err)
                self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_upgrade_rejects_stamp_symlink_before_planning(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        stamp_path = target / agent_init.STAMP_RELATIVE
        external_stamp = self.root / "external-stamp.json"
        stamp_path.replace(external_stamp)
        stamp_path.symlink_to(external_stamp)

        code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, 1)
        self.assertIn("symbolic link", err)
        self.assertTrue(external_stamp.is_file())

    def test_repeated_adopt_and_baseline_reject_symlinked_stamp(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        stamp_path = target / agent_init.STAMP_RELATIVE
        external_stamp = self.root / "external-stamp.json"
        stamp_path.replace(external_stamp)
        stamp_path.symlink_to(external_stamp)

        for command in (("adopt", str(target)), ("baseline", str(target))):
            with self.subTest(command=command[0]):
                code, _, err = self.run_agent_init(*command)
                self.assertEqual(code, 1)
                self.assertIn("symbolic link", err)
                self.assertTrue(stamp_path.is_symlink())
                self.assertTrue(external_stamp.is_file())

    def test_upgrade_skip_leaves_file_untouched(self) -> None:
        target = self.make_adopted_target()

        with self.patched_templates() as templates:
            (templates / "vault/index.md").write_text("new index template\n", encoding="utf-8")
            code, _, err = self.run_agent_init(
                "upgrade", str(target), "--apply", "--skip", "vault/index.md"
            )

        self.assertEqual(code, agent_init.EXIT_ACTIONABLE, err)
        self.assertNotEqual(
            (target / "vault/index.md").read_text(encoding="utf-8"), "new index template\n"
        )
        stamp = self.read_stamp(target)
        self.assertEqual(
            stamp["files"]["vault/index.md"]["baseline"],
            agent_init.sha256_hex((agent_init.TEMPLATES_ROOT / "vault/index.md").read_bytes()),
        )

    def test_diff_lists_pending_migration_playbook(self) -> None:
        target = self.make_adopted_target()
        stamp = self.read_stamp(target)
        stamp["protocol_version"] = "2025.01.0"
        (target / agent_init.STAMP_RELATIVE).write_text(
            json.dumps(stamp, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        code, out, err = self.run_agent_init("diff", str(target))

        self.assertEqual(code, 0, err)
        self.assertIn("migration playbook", out)
        self.assertIn(agent_init.read_protocol_version(), out)

    def test_adopt_fails_without_version_file(self) -> None:
        target = self.root / "project"
        target.mkdir()

        with patch.object(agent_init, "VERSION_FILE", self.root / "missing-VERSION"):
            code, _, err = self.adopt(target)

        self.assertEqual(code, 1)
        self.assertIn("version file", err)

    def test_upgrade_backfills_new_data_file_for_older_adoption(self) -> None:
        # A project adopted at 2026.08.0 has no parked.md and no stamp entry
        # for it; the 2026.09.0 template set backfills it as a data-role add.
        target = self.make_adopted_target()
        (target / "vault/parked.md").unlink()
        stamp = self.read_stamp(target)
        stamp["files"].pop("vault/parked.md", None)
        (target / agent_init.STAMP_RELATIVE).write_text(
            json.dumps(stamp, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        code, out, err = self.run_agent_init("diff", str(target))
        self.assertEqual(code, agent_init.EXIT_ACTIONABLE, err)
        self.assertIn("+ vault/parked.md", out)

        code, _, err = self.run_agent_init("upgrade", str(target), "--apply")
        self.assertEqual(code, 0, err)

        self.assertTrue((target / "vault/parked.md").is_file())
        entry = self.read_stamp(target)["files"]["vault/parked.md"]
        self.assertEqual(entry["role"], "data")
        code, out, err = self.run_agent_init("diff", str(target))
        self.assertEqual(code, 0, err)
        self.assertIn("x vault/parked.md", out)


class EmbeddedSkillLayoutTest(TargetTestCase):
    @staticmethod
    def load_module(script_path: Path, name: str):
        spec = importlib.util.spec_from_file_location(name, script_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load {script_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_repo_layout_detection(self) -> None:
        self.assertFalse(agent_init.SKILL_LAYOUT)
        self.assertEqual(
            agent_init.TEMPLATES_ROOT,
            agent_init.SCRIPT_DIRECTORY.parent / "skills" / "trellium-zh" / "assets" / "templates",
        )

    def test_embedded_packages_install_their_own_locale(self) -> None:
        repo_zh_package = agent_init.TEMPLATES_ROOT.parents[1]
        repo_en_package = repo_zh_package.parent / "trellium"
        for package, _locale_marker, profile_marker, excluded_marker in (
            (repo_zh_package, "替换为", "## 模块和依赖管理", "## Modules, workspaces, and dependencies"),
            (repo_en_package, "replace with", "## Modules, workspaces, and dependencies", "## 模块和依赖管理"),
        ):
            with self.subTest(package=package.name):
                copied = self.root / package.name
                shutil.copytree(package, copied)
                embedded = self.load_module(copied / "assets" / "trellium.py", f"embedded_{package.name}")

                self.assertTrue(embedded.SKILL_LAYOUT)
                self.assertEqual(embedded.TEMPLATES_ROOT, (copied / "assets" / "templates").resolve())
                self.assertTrue(embedded.VERSION_FILE.is_file())
                self.assertTrue(embedded.MIGRATIONS_FILE.is_file())

                target = self.root / f"target-{package.name}"
                target.mkdir()
                code, _, err = self.run_agent_init_module(
                    embedded, "adopt", str(target), "--profile", "go-backend=services/api"
                )
                self.assertEqual(code, 0, err)
                handoff = (target / "vault/handoff.md").read_text(encoding="utf-8")
                self.assertEqual(agent_init.count_handoff_entries(handoff), 0)
                runtime = (target / "vault/runtime.md").read_text(encoding="utf-8")
                self.assertNotIn("## Active Tasks", runtime)
                self.assertIn("Trellium adoption recorded", runtime)
                profile = (target / "docs/engineering/profiles/go-backend.md").read_text(encoding="utf-8")
                self.assertIn(profile_marker, profile)
                self.assertNotIn(excluded_marker, profile)
                self.assertIn("`services/api`", profile)
                if package.name == "trellium":
                    self.assertIn("## Project Scope", profile)
                    self.assertIn("Only apply this profile", profile)
                else:
                    self.assertIn("## 项目适用范围", profile)
                    self.assertIn("仅当当前文件位于上述任一 root 下时应用本 profile", profile)

                stamp = json.loads(
                    (target / embedded.STAMP_RELATIVE).read_text(encoding="utf-8")
                )
                self.assertEqual(stamp["protocol_version"], embedded.read_protocol_version())

    def test_durable_profile_locale_comes_from_package_metadata_not_body_headings(self) -> None:
        with self.patched_templates() as templates:
            locale_file = templates / "PROFILE_LOCALE"
            source = templates / agent_init.PROFILE_DOCUMENT_TEMPLATE_DIRECTORY / "go-backend.md"
            original = source.read_text(encoding="utf-8")
            profile = {"id": "go-backend", "roots": ["services/api"]}

            locale_file.write_text("zh\n", encoding="utf-8")
            source.write_text(original.replace("## 定位", "## 角色"), encoding="utf-8")
            rendered = agent_init.render_durable_profile(profile)
            self.assertIn("## 项目适用范围", rendered)
            self.assertIn("仅当当前文件位于上述任一 root 下时应用本 profile", rendered)

            locale_file.write_text("en\n", encoding="utf-8")
            source.write_text(original + "\n## 定位\n\nHeading text must not select locale.\n", encoding="utf-8")
            rendered = agent_init.render_durable_profile(profile)
            self.assertIn("## Project Scope", rendered)
            self.assertIn("Only apply this profile", rendered)

    def test_embedded_check_passes_on_fresh_adoption(self) -> None:
        # The shipped templates must be check-clean: a fresh adoption in both
        # skill packages validates policy/state/template consistency.
        repo_zh_package = agent_init.TEMPLATES_ROOT.parents[1]
        for package_name in (repo_zh_package.name, "trellium"):
            package_root = repo_zh_package.parent / package_name
            with self.subTest(package=package_name):
                copied = self.root / f"check-{package_name}"
                shutil.copytree(package_root, copied)
                embedded = self.load_module(copied / "assets" / "trellium.py", f"embedded_check_{package_name}")

                target = self.root / f"check-target-{package_name}"
                target.mkdir()
                code, _, err = self.run_agent_init_module(embedded, "adopt", str(target))
                self.assertEqual(code, 0, err)

                out, err2 = StringIO(), StringIO()
                with redirect_stdout(out), redirect_stderr(err2):
                    check_code = embedded.main(["check", str(target), "--format", "json"])
                self.assertEqual(check_code, 0, out.getvalue())
                payload = json.loads(out.getvalue())
                self.assertEqual(payload["summary"]["errors"], 0, payload["findings"])
                self.assertIsNotNone(payload["measurements"].get("runtime"))

    @staticmethod
    def run_agent_init_module(module, *arguments: str) -> tuple[int, str, str]:
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = module.main(list(arguments))
        return code, out.getvalue(), err.getvalue()

    def test_embedded_upgrade_uses_package_version(self) -> None:
        repo_zh_package = agent_init.TEMPLATES_ROOT.parents[1]
        copied = self.root / "trellium-zh"
        shutil.copytree(repo_zh_package, copied)
        embedded = self.load_module(copied / "assets" / "trellium.py", "embedded_upgrade")

        target = self.root / "project"
        target.mkdir()
        code, _, err = self.run_agent_init_module(embedded, "adopt", str(target))
        self.assertEqual(code, 0, err)

        # Upstream drift inside the package's own templates must be detected
        # by the embedded script without any repo paths.
        with patch.object(embedded, "TEMPLATES_ROOT", copied / "assets" / "templates"):
            (copied / "assets" / "templates" / "vault" / "index.md").write_text(
                "package-updated index\n", encoding="utf-8"
            )
            code, out, err = self.run_agent_init_module(embedded, "diff", str(target))
            self.assertEqual(code, embedded.EXIT_ACTIONABLE, err)
            self.assertIn("~ vault/index.md", out)
            code, _, err = self.run_agent_init_module(embedded, "upgrade", str(target), "--apply")
            self.assertEqual(code, 0, err)
        self.assertEqual(
            (target / "vault/index.md").read_text(encoding="utf-8"), "package-updated index\n"
        )


class FetchTest(TargetTestCase):
    def build_release_tree(self, version: str, index_text: str | None = None) -> Path:
        release = self.root / "releases" / version
        (release / "scripts").mkdir(parents=True)
        shutil.copy(SCRIPT_PATH, release / "scripts" / "trellium.py")
        (release / "init").mkdir()
        (release / "init" / "VERSION").write_text(f"{version}\n", encoding="utf-8")
        (release / "init" / "MIGRATIONS.md").write_text(
            f"# Migrations\n\n## {version} — test\n\n- test entry\n", encoding="utf-8"
        )
        templates = release / "skills" / "trellium-zh" / "assets" / "templates"
        shutil.copytree(agent_init.TEMPLATES_ROOT, templates)
        if index_text is not None:
            (templates / "vault" / "index.md").write_text(index_text, encoding="utf-8")
        return release

    def test_fetch_runs_fetched_release_end_to_end(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        release = self.build_release_tree("9999.0.0", index_text="fetched index template\n")

        with patch.object(agent_init, "latest_release_tag", return_value="9999.0.0"), patch.object(
            agent_init, "fetch_release_tree", return_value=release
        ):
            code, out, err = self.run_agent_init("diff", str(target), "--fetch")

        self.assertEqual(code, agent_init.EXIT_ACTIONABLE, err)
        self.assertIn("fetch: using zlin101/trellium tag 9999.0.0", out)
        self.assertIn("available: 9999.0.0", out)
        self.assertIn("~ vault/index.md", out)

        with patch.object(agent_init, "latest_release_tag", return_value="9999.0.0"), patch.object(
            agent_init, "fetch_release_tree", return_value=release
        ):
            code, out, err = self.run_agent_init("upgrade", str(target), "--fetch", "--apply")

        self.assertEqual(code, 0, err)
        self.assertEqual((target / "vault/index.md").read_text(encoding="utf-8"), "fetched index template\n")
        stamp = self.read_stamp(target)
        self.assertEqual(stamp["protocol_version"], "9999.0.0")

    def test_upgrade_applies_version_pointer_on_tooling_release(self) -> None:
        # A release with no file changes must still advance the stamp so the
        # version pointer does not stick behind the latest release.
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        stamp = self.read_stamp(target)
        stamp["protocol_version"] = "2026.09.0"
        (target / agent_init.STAMP_RELATIVE).write_text(
            json.dumps(stamp, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.assertNotEqual(agent_init.read_protocol_version(), "2026.09.0")

        code, out, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, 0, err)
        self.assertIn("recorded protocol version", out)
        updated = self.read_stamp(target)
        self.assertEqual(updated["protocol_version"], agent_init.read_protocol_version())
        self.assertEqual(updated["schema_version"], 2)
        self.assertEqual(updated["profiles"], [])

    def test_fetch_refuses_downgrade(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        release = self.build_release_tree("2025.01.0")

        with patch.object(agent_init, "latest_release_tag", return_value="2025.01.0"), patch.object(
            agent_init, "fetch_release_tree", return_value=release
        ):
            code, _, err = self.run_agent_init("diff", str(target), "--fetch")

        self.assertEqual(code, 1)
        self.assertIn("older than", err)

    def test_templates_flag_overrides_without_fetch(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        release = self.build_release_tree("9999.0.0", index_text="overridden index template\n")

        code, out, err = self.run_agent_init(
            "diff", str(target), "--templates", str(release / "skills" / "trellium-zh" / "assets" / "templates")
        )

        self.assertEqual(code, agent_init.EXIT_ACTIONABLE, err)
        self.assertIn("~ vault/index.md", out)

    def test_safe_extract_rejects_traversal_and_links(self) -> None:
        import io
        import tarfile

        def write_tar(path: Path, member_name: str, symlink: bool = False) -> None:
            with tarfile.open(path, "w:gz") as archive:
                if symlink:
                    info = tarfile.TarInfo(member_name)
                    info.type = tarfile.SYMTYPE
                    info.linkname = "/etc/passwd"
                    archive.addfile(info)
                else:
                    payload = b"evil"
                    info = tarfile.TarInfo(member_name)
                    info.size = len(payload)
                    archive.addfile(info, io.BytesIO(payload))

        tarball = self.root / "evil-traversal.tar.gz"
        write_tar(tarball, "../evil.txt")
        with self.assertRaises(agent_init.AdoptionError):
            agent_init.safe_extract_tarball(tarball, self.root / "extract-a")

        tarball = self.root / "evil-symlink.tar.gz"
        write_tar(tarball, "link", symlink=True)
        with self.assertRaises(agent_init.AdoptionError):
            agent_init.safe_extract_tarball(tarball, self.root / "extract-b")


class RenderedContentTest(unittest.TestCase):
    def test_agent_entry_section_levels_governance_reading(self) -> None:
        section = agent_init.agent_entry_section()
        self.assertIn("cheat sheet", section)
        self.assertIn("Level B or Level C", section)
        self.assertNotIn("3. `vault/governance.md`", section)


class VaultCheckMixin(TargetTestCase):
    def make_project(
        self,
        *,
        index: str | None = None,
        runtime: str | None = None,
        handoff: str | None = None,
        decisions: str | None = None,
        parked: str | None = None,
        files: dict[str, str] | None = None,
        policy: str | None = None,
    ) -> Path:
        count = getattr(self, "_project_count", 0) + 1
        self._project_count = count
        name = "project" if count == 1 else f"project-{count}"
        target = self.root / name
        (target / "vault" / "tasks").mkdir(parents=True, exist_ok=True)
        if index is None:
            index = "# Vault Index\n\n" + (policy if policy is not None else tracked_policy()) + "\n\nRouting text.\n"
        (target / "vault/index.md").write_text(index, encoding="utf-8")
        (target / "vault/runtime.md").write_text(
            runtime if runtime is not None else build_runtime(), encoding="utf-8"
        )
        (target / "vault/handoff.md").write_text(
            handoff if handoff is not None else "# Handoff\n\n## TASK-0001 - 2026-01-01\n\n- Objective: x\n", encoding="utf-8"
        )
        (target / "vault/decisions.md").write_text(
            decisions if decisions is not None else "# Decisions\n\n- D-0001 · title · Active · essence · 2026-01-01\n", encoding="utf-8"
        )
        (target / "vault/parked.md").write_text(
            parked if parked is not None else "# Parked\n\n## Entries\n\n- P-0001 · task · title · context · trigger · 2026-01-01\n", encoding="utf-8"
        )
        (target / "vault/project.md").write_text(
            f"# Project\n\n{target.name} project facts.\n", encoding="utf-8"
        )
        (target / "vault/governance.md").write_text("# Governance\n\nDefault governance.\n", encoding="utf-8")
        (target / "vault/tasks/README.md").write_text("# Task Files\n\nLifecycle and templates.\n", encoding="utf-8")
        for relative, content in (files or {}).items():
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
        return target

    def check(self, target: Path, *extra: str) -> tuple[int, str, str]:
        return self.run_agent_init("check", str(target), *extra)

    def check_json(self, target: Path, *extra: str) -> dict:
        code, out, err = self.check(target, "--format", "json", *extra)
        self.assertIn(code, (0, agent_init.CHECK_ERROR_EXIT), err)
        return json.loads(out)

    def codes(self, payload: dict) -> list[str]:
        return [finding["code"] for finding in payload["findings"]]

    def init_git_repo(self, target: Path) -> None:
        subprocess.run(["git", "init", "-q"], cwd=target, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=target, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=True)

    def git(self, target: Path, *arguments: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *arguments], cwd=target, check=False, capture_output=True)


class VaultCheckTest(VaultCheckMixin, TargetTestCase):
    def test_valid_project_passes_with_zero_findings(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0001-short-title.md": (
                "# TASK-0001 - Short Title\n\n" + state_block(valid_state()) + "\n\n## Objective\n\nWork.\n"
            )},
            runtime=build_runtime(focus="TASK-0001"),
        )

        code, out, err = self.check(target)
        self.assertEqual(code, 0, err)
        self.assertIn("passed with warnings", out)
        self.assertIn("GIT_CHECK_SKIPPED", out)

        payload = self.check_json(target)
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["summary"], {"errors": 0, "warnings": 1})
        self.assertEqual(self.codes(payload), ["GIT_CHECK_SKIPPED"])
        self.assertIn("runtime", payload["measurements"])
        self.assertIn("tasks", payload["measurements"])
        self.assertEqual(payload["measurements"]["tasks"]["current_task_files"], 1)

    def test_field_order_and_whitespace_do_not_matter(self) -> None:
        block = state_block(text='{ "lifecycle":"draft" ,\n"authority_level":2,\n "schema_version":1, "task_id":"TASK-0001", "level":"B" }')
        target = self.make_project(
            files={"vault/tasks/TASK-0001-a.md": f"# TASK-0001 - A\n\n{block}\n"},
            runtime=build_runtime(),
        )

        payload = self.check_json(target)

        self.assertEqual(payload["summary"]["errors"], 0)

    def test_missing_policy_is_legacy_warning_without_hidden_defaults(self) -> None:
        target = self.make_project(
            policy="",
            runtime=build_runtime(recent=tuple(f"item {i}" for i in range(30))),
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 0, err)
        self.assertIn("POLICY_MISSING", out)
        self.assertIn("passed with warnings", out)
        self.assertNotIn("BUDGET_EXCEEDED", out)

        payload = self.check_json(target)
        self.assertEqual(payload["summary"], {"errors": 0, "warnings": 1})
        self.assertEqual(self.codes(payload), ["POLICY_MISSING"])

    def test_policy_schema_violations_are_errors(self) -> None:
        cases = {
            "unknown-field": policy_block({"schema_version": 1, "task_storage": "tracked", "extra": True}),
            "bad-storage": policy_block({"schema_version": 1, "task_storage": "hybrid"}),
            "bad-schema-version": policy_block({"schema_version": 2, "task_storage": "tracked"}),
            "bool-schema-version": policy_block(text='{"schema_version": true, "task_storage": "tracked"}'),
            "trailing-comma": policy_block(text='{"schema_version": 1, "task_storage": "tracked",}'),
            "negative-budget": policy_block({
                "schema_version": 1,
                "task_storage": "tracked",
                "budgets": {"runtime": {"max_lines": -5}},
            }),
            "unknown-budget-key": policy_block({
                "schema_version": 1,
                "task_storage": "tracked",
                "budgets": {"runtime": {"max_bytes": 100}},
            }),
            "unknown-budget-file": policy_block({
                "schema_version": 1,
                "task_storage": "tracked",
                "budgets": {"misc": {"max_lines": 100}},
            }),
        }
        for name, index in cases.items():
            with self.subTest(case=name):
                target = self.make_project(index="# Vault Index\n\n" + index + "\n")
                code, out, err = self.check(target)
                self.assertEqual(code, 2, out)
                self.assertIn("POLICY_INVALID", out)

    def test_duplicate_policy_blocks_are_invalid(self) -> None:
        index = "# Vault Index\n\n" + tracked_policy() + "\n" + tracked_policy() + "\n"
        target = self.make_project(index=index)

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("POLICY_INVALID", out)

    def test_legacy_task_without_state_block_is_unresolved_warning(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0002-legacy.md": "# TASK-0002 - Legacy\n\n## Status\n\nActive\n"},
            runtime=build_runtime(),
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 0, err)
        self.assertIn("TASK_STATE_MISSING", out)

        payload = self.check_json(target)
        self.assertEqual(
            sorted(self.codes(payload)),
            ["GIT_CHECK_SKIPPED", "TASK_STATE_MISSING"],
        )
        self.assertEqual(payload["measurements"]["tasks"]["legacy_tasks"], 1)

    def test_state_block_violations_are_errors(self) -> None:
        base = {"schema_version": 1, "task_id": "TASK-0001", "level": "B", "authority_level": 2, "lifecycle": "draft"}
        cases = {
            "unknown-field": dict(base, surprise=1),
            "bad-lifecycle": dict(base, lifecycle="waiting-review"),
            "bad-level": dict(base, level="A"),
            "authority-out-of-range": dict(base, authority_level=5),
            "authority-bool": None,  # handled with raw text below
            "string-schema-version": None,
            "bad-task-id": dict(base, task_id="TASK-1"),
            "not-an-object": None,
        }
        raw_cases = {
            "authority-bool": '{ "schema_version": 1, "task_id": "TASK-0001", "level": "B", "authority_level": true, "lifecycle": "draft" }',
            "string-schema-version": '{ "schema_version": "1", "task_id": "TASK-0001", "level": "B", "authority_level": 2, "lifecycle": "draft" }',
            "not-an-object": '["TASK-0001"]',
        }
        for name, payload in cases.items():
            if payload is None:
                continue
            with self.subTest(case=name):
                target = self.make_project(
                    files={"vault/tasks/TASK-0001-x.md": "# TASK-0001 - X\n\n" + state_block(payload) + "\n"}
                )
                code, out, err = self.check(target)
                self.assertEqual(code, 2, out)
                self.assertIn("TASK_STATE_INVALID", out)
        for name, text in raw_cases.items():
            with self.subTest(case=name):
                target = self.make_project(
                    files={"vault/tasks/TASK-0001-x.md": "# TASK-0001 - X\n\n" + state_block(text=text) + "\n"}
                )
                code, out, err = self.check(target)
                self.assertEqual(code, 2, out)
                self.assertIn("TASK_STATE_INVALID", out)

    def test_duplicate_state_blocks_are_invalid(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0001-x.md": (
                "# TASK-0001 - X\n\n" + state_block(valid_state()) + "\n" + state_block(valid_state()) + "\n"
            )}
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("TASK_STATE_DUPLICATE", out)

    def test_unterminated_state_block_is_invalid(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0001-x.md": "# TASK-0001 - X\n\n<!-- trellium-task-state\n{ \"broken\": true }\n"},
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("TASK_STATE_INVALID", out)

    def test_task_id_must_match_file_name(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0001-a.md": "# TASK-0001 - A\n\n" + state_block(valid_state(task_id="TASK-0002")) + "\n"}
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("TASK_ID_MISMATCH", out)

    def test_optional_state_fields_are_validated(self) -> None:
        good = valid_state(current_slice="A4", gates={"design": "passed", "live": "not_authorized"})
        target = self.make_project(
            files={"vault/tasks/TASK-0001-x.md": "# TASK-0001 - X\n\n" + state_block(good) + "\n"},
            runtime=build_runtime(),
        )
        payload = self.check_json(target)
        self.assertEqual(payload["summary"], {"errors": 0, "warnings": 1})
        self.assertEqual(self.codes(payload), ["GIT_CHECK_SKIPPED"])

        bad_gate = valid_state(gates={"design": "approved"})
        target = self.make_project(
            files={"vault/tasks/TASK-0001-x.md": "# TASK-0001 - X\n\n" + state_block(bad_gate) + "\n"}
        )
        code, out, err = self.check(target)
        self.assertEqual(code, 2)
        self.assertIn("TASK_STATE_INVALID", out)

    def test_budget_thresholds_require_explicit_policy(self) -> None:
        long_runtime = build_runtime(recent=tuple(f"item {i}" for i in range(30)))
        target = self.make_project(runtime=long_runtime)
        payload = self.check_json(target)
        self.assertEqual(payload["summary"]["errors"], 0)
        self.assertGreaterEqual(payload["measurements"]["runtime"]["lines"], 30)

        strict = policy_block({
            "schema_version": 1,
            "task_storage": "tracked",
            "budgets": {"runtime": {"max_lines": 5, "max_recent_entries": 2}},
        })
        target = self.make_project(index="# Vault Index\n\n" + strict + "\n", runtime=long_runtime)
        code, out, err = self.check(target)
        self.assertEqual(code, 0, err)
        self.assertIn("BUDGET_EXCEEDED", out)
        payload = self.check_json(target)
        self.assertEqual(payload["summary"]["errors"], 0)
        self.assertEqual(payload["summary"]["warnings"], 2)
        status_code, _, status_err = self.run_agent_init("status", str(target))
        self.assertEqual(status_code, 0, status_err)

    def test_budget_exceeds_are_warning_only_health_signals(self) -> None:
        long_runtime = build_runtime(recent=tuple(f"item {i}" for i in range(30)))
        active_task = "# TASK-0001 - A\n\n" + state_block(valid_state(lifecycle="active")) + "\n"
        second_active = "# TASK-0002 - B\n\n" + state_block(valid_state(task_id="TASK-0002", lifecycle="active")) + "\n"
        cases = {
            "runtime": (
                {"runtime": {"max_lines": 5, "max_recent_entries": 2}},
                {"runtime": long_runtime},
                {},
                2,
            ),
            "handoff": (
                {"handoff": {"max_lines": 1}},
                {},
                {},
                1,
            ),
            "decisions": (
                {"decisions": {"max_lines": 1}},
                {},
                {},
                1,
            ),
            "parked": (
                {"parked": {"max_lines": 1}},
                {},
                {},
                1,
            ),
            "active-tasks": (
                {"tasks": {"max_active_tasks": 1}},
                {},
                {
                    "vault/tasks/TASK-0001-a.md": active_task,
                    "vault/tasks/TASK-0002-b.md": second_active,
                },
                1,
            ),
        }
        for name, (budgets, runtime_kwargs, files, expected_warnings) in cases.items():
            with self.subTest(case=name):
                policy = policy_block({"schema_version": 1, "task_storage": "tracked", "budgets": budgets})
                target = self.make_project(
                    index="# Vault Index\n\n" + policy + "\n",
                    files=files,
                    **runtime_kwargs,
                )
                code, out, err = self.check(target)
                self.assertEqual(code, 0, err)
                self.assertIn("BUDGET_EXCEEDED", out)
                payload = self.check_json(target)
                self.assertEqual(payload["summary"]["errors"], 0)
                exceeded = [f for f in payload["findings"] if f["code"] == "BUDGET_EXCEEDED"]
                self.assertEqual(len(exceeded), expected_warnings)
                for finding in exceeded:
                    self.assertEqual(finding["severity"], "warning")
                status_code, _, status_err = self.run_agent_init("status", str(target))
                self.assertEqual(status_code, 0, status_err)

    def test_max_active_tasks_with_legacy_files_is_unresolved(self) -> None:
        policy = policy_block({
            "schema_version": 1,
            "task_storage": "tracked",
            "budgets": {"tasks": {"max_active_tasks": 1}},
        })
        target = self.make_project(
            index="# Vault Index\n\n" + policy + "\n",
            files={
                "vault/tasks/TASK-0001-a.md": "# TASK-0001 - A\n\n" + state_block(valid_state(lifecycle="active")) + "\n",
                "vault/tasks/TASK-0002-legacy.md": "# TASK-0002 - Legacy\n",
            },
            runtime=build_runtime(),
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 0, err)
        self.assertIn("TASK_COUNT_UNRESOLVED", out)

    def test_max_active_tasks_is_enforced_when_resolvable(self) -> None:
        policy = policy_block({
            "schema_version": 1,
            "task_storage": "tracked",
            "budgets": {"tasks": {"max_active_tasks": 1}},
        })
        target = self.make_project(
            index="# Vault Index\n\n" + policy + "\n",
            files={
                "vault/tasks/TASK-0001-a.md": "# TASK-0001 - A\n\n" + state_block(valid_state(lifecycle="active")) + "\n",
                "vault/tasks/TASK-0002-b.md": "# TASK-0002 - B\n\n" + state_block(valid_state(task_id="TASK-0002", lifecycle="accepted")) + "\n",
                "vault/tasks/TASK-0003-c.md": "# TASK-0003 - C\n\n" + state_block(valid_state(task_id="TASK-0003", lifecycle="active")) + "\n",
            },
            runtime=build_runtime(),
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 0, err)
        self.assertIn("BUDGET_EXCEEDED", out)
        payload = self.check_json(target)
        self.assertEqual(payload["summary"]["errors"], 0)

    def test_review_ledgers_and_archive_are_cold_history(self) -> None:
        target = self.make_project(
            files={
                "vault/tasks/TASK-0001-review.md": "# TASK-0001 - Review Ledger\n\n## Findings\n",
                "vault/tasks/archive/TASK-0002-old.md": "# TASK-0002 - Old\n",
            },
        )

        code, out, err = self.check(target)
        self.assertEqual(code, 0, err)
        self.assertNotIn("TASK_STATE_MISSING", out)

        payload = self.check_json(target)
        self.assertEqual(payload["measurements"]["tasks"]["review_ledgers"], 1)
        self.assertEqual(payload["measurements"]["tasks"]["archive_files"], 1)
        self.assertEqual(payload["measurements"]["tasks"]["current_task_files"], 0)

    def test_storage_tracked_mode(self) -> None:
        files = {
            "vault/tasks/TASK-0001-active.md": "# TASK-0001 - Active\n\n" + state_block(valid_state(lifecycle="active")) + "\n",
            "vault/tasks/TASK-0002-done.md": "# TASK-0002 - Done\n\n" + state_block(valid_state(task_id="TASK-0002", lifecycle="accepted")) + "\n",
            "vault/tasks/archive/TASK-0003-old.md": "# TASK-0003 - Old\n",
        }
        target = self.make_project(files=files, runtime=build_runtime())
        self.init_git_repo(target)
        self.git(target, "add", "-A")
        self.git(target, "commit", "-qm", "base")

        code, out, err = self.check(target)
        self.assertEqual(code, 0, err)
        self.assertNotIn("TASK_STORAGE_MISMATCH", out)

        # An uncommitted new active task is a normal window: warning only.
        new_task = target / "vault/tasks/TASK-0004-new.md"
        new_task.write_text("# TASK-0004 - New\n\n" + state_block(valid_state(task_id="TASK-0004")) + "\n", encoding="utf-8")
        code, out, err = self.check(target)
        self.assertEqual(code, 0, err)
        self.assertNotIn("TASK_STORAGE_MISMATCH", out)

        # A closed (accepted) task that is not tracked is an error.
        done_path = target / "vault/tasks/TASK-0005-done.md"
        done_path.write_text("# TASK-0005 - Done\n\n" + state_block(valid_state(task_id="TASK-0005", lifecycle="accepted")) + "\n", encoding="utf-8")
        code, out, err = self.check(target)
        self.assertEqual(code, 2)
        self.assertIn("TASK_STORAGE_MISMATCH", out)
        done_path.unlink()

        # An untracked task file matched by .gitignore is an error: it would
        # silently stay local while the project policy says tracked. (Tracked
        # files are never reported by check-ignore; the index wins.)
        ignored_task = target / "vault/tasks/TASK-0006-ignored.md"
        ignored_task.write_text("# TASK-0006 - Ignored\n\n" + state_block(valid_state(task_id="TASK-0006")) + "\n", encoding="utf-8")
        (target / ".gitignore").write_text("vault/tasks/TASK-0006-ignored.md\n", encoding="utf-8")
        code, out, err = self.check(target)
        self.assertEqual(code, 2)
        self.assertIn("TASK_STORAGE_MISMATCH", out)
        self.assertIn("TASK-0006-ignored.md", out)

    def test_tracked_task_deleted_from_worktree_is_reported_from_index(self) -> None:
        relative = "vault/tasks/TASK-0008-indexed.md"
        target = self.make_project(
            files={relative: (
                "# TASK-0008 - Indexed\n\n"
                + state_block(valid_state(task_id="TASK-0008", lifecycle="active"))
                + "\n"
            )},
        )
        self.init_git_repo(target)
        self.git(target, "add", "-A")
        self.git(target, "commit", "-qm", "base")
        (target / relative).unlink()

        code, payload, err = self.check(target, "--format", "json")

        self.assertEqual(code, agent_init.CHECK_ERROR_EXIT, err)
        findings = [item for item in json.loads(payload)["findings"] if item["code"] == "TASK_STORAGE_MISMATCH"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["path"], relative)
        self.assertEqual(findings[0]["task_id"], "TASK-0008")
        self.assertIn("missing from the working tree", findings[0]["message"])

    def test_storage_local_mode_rejects_tracked_tasks(self) -> None:
        target = self.make_project(
            policy=local_policy(),
            files={"vault/tasks/TASK-0001-quiet.md": "# TASK-0001 - Quiet\n\n" + state_block(valid_state()) + "\n"},
            runtime=build_runtime(),
        )
        self.init_git_repo(target)

        # Not tracked yet: no storage finding.
        code, out, err = self.check(target)
        self.assertEqual(code, 0, err)

        self.git(target, "add", "-A")
        code, out, err = self.check(target)
        self.assertEqual(code, 2)
        self.assertIn("TASK_STORAGE_MISMATCH", out)

    def test_duplicate_task_ids_across_files_exit_2(self) -> None:
        block = state_block(valid_state(task_id="TASK-0001"))
        target = self.make_project(
            files={
                "vault/tasks/TASK-0001-a.md": f"# TASK-0001 - A\n\n{block}\n",
                "vault/tasks/TASK-0001-b.md": f"# TASK-0001 - B\n\n{block}\n",
                "vault/tasks/TASK-0002-c.md": f"# TASK-0002 - C\n\n{state_block(valid_state(task_id='TASK-0002'))}\n",
            },
            runtime=build_runtime(),
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("TASK_ID_DUPLICATE", out)
        payload = self.check_json(target)
        self.assertEqual(len([f for f in payload["findings"] if f["code"] == "TASK_ID_DUPLICATE"]), 2)

    def test_bare_task_file_name_is_discovered(self) -> None:
        # TASK-0001.md (no slug suffix) is a current task entity per the
        # TASK-*.md glob; discovery must not silently skip it.
        target = self.make_project(
            policy=local_policy(),
            files={"vault/tasks/TASK-0009.md": "# TASK-0009 - Bare\n\n" + state_block(valid_state(task_id="TASK-0009")) + "\n"},
            runtime=build_runtime(),
        )
        self.init_git_repo(target)
        self.git(target, "add", "-A")

        code, out, err = self.check(target)
        self.assertEqual(code, 2)
        self.assertIn("TASK_STORAGE_MISMATCH", out)
        self.assertIn("TASK-0009.md", out)

        payload = self.check_json(target)
        self.assertEqual(payload["measurements"]["tasks"]["current_task_files"], 1)

    def test_storage_handles_unicode_and_space_file_names(self) -> None:
        name = "TASK-0007-我的 任务.md"
        target = self.make_project(
            policy=local_policy(),
            files={f"vault/tasks/{name}": f"# TASK-0007 - Unicode\n\n{state_block(valid_state(task_id='TASK-0007'))}\n"},
            runtime=build_runtime(),
        )
        self.init_git_repo(target)
        self.git(target, "add", "-A")

        code, out, err = self.check(target)
        self.assertEqual(code, 2)
        self.assertIn("TASK_STORAGE_MISMATCH", out)
        self.assertIn(name, out)

    def test_storage_check_skipped_without_git(self) -> None:
        # A task file exists, so storage could not be verified: skipped warning.
        target = self.make_project(
            files={"vault/tasks/TASK-0001-a.md": "# TASK-0001 - A\n\n" + state_block(valid_state()) + "\n"},
            runtime=build_runtime(),
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 0, err)
        self.assertIn("GIT_CHECK_SKIPPED", out)
        self.assertNotIn("storage ok", out)

    def test_symlinked_task_input_is_not_followed(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        secret = outside / "TASK-0001-real.md"
        secret.write_text("# TASK-0001 - Real\n\nOUTSIDE-SECRET-CONTENT\n", encoding="utf-8")
        target = self.make_project()
        (target / "vault/tasks/TASK-0001-link.md").symlink_to(secret)

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("SYMLINK_INPUT", out)
        self.assertNotIn("OUTSIDE-SECRET-CONTENT", out)

    def test_symlinked_vault_is_not_followed(self) -> None:
        outside = self.root / "outside-vault"
        outside.mkdir()
        (outside / "index.md").write_text("OUTSIDE-INDEX-CONTENT\n", encoding="utf-8")
        target = self.root / "project"
        target.mkdir()
        (target / "vault").symlink_to(outside, target_is_directory=True)

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("SYMLINK_INPUT", out)
        self.assertNotIn("OUTSIDE-INDEX-CONTENT", out)

    def test_symlinked_tasks_directory_is_not_followed(self) -> None:
        outside = self.root / "outside-tasks"
        outside.mkdir()
        block = state_block(text='{ "schema_version": 1, "task_id": "TASK-0500", "level": "B", "authority_level": 2, "lifecycle": "draft", "zzz_external_marker_field": 1 }')
        (outside / "TASK-0500-secret.md").write_text(f"# TASK-0500 - Secret\n\n{block}\nOUTSIDE-SECRET-CONTENT\n", encoding="utf-8")
        target = self.make_project()
        shutil.rmtree(target / "vault/tasks")
        (target / "vault/tasks").symlink_to(outside, target_is_directory=True)

        code, out, err = self.check(target)
        self.assertEqual(code, 2)
        self.assertIn("SYMLINK_INPUT", out)
        self.assertNotIn("OUTSIDE-SECRET-CONTENT", out)
        self.assertNotIn("zzz_external_marker_field", out)
        self.assertNotIn("TASK-0500-secret.md", out.replace("vault/tasks is a symbolic link", ""))

        payload = self.check_json(target)
        self.assertEqual(payload["measurements"]["tasks"]["current_task_files"], 0)

    def test_symlinked_ledger_and_archive_are_errors(self) -> None:
        outside = self.root / "outside-archive"
        outside.mkdir()
        (outside / "TASK-0600-old.md").write_text("# TASK-0600 - Old\n", encoding="utf-8")
        target = self.make_project(
            files={"vault/tasks/TASK-0001-review.md": "# TASK-0001 - Review Ledger\n"},
        )
        (target / "vault/tasks/TASK-0001-review.md").unlink()
        (target / "vault/tasks/TASK-0001-review.md").symlink_to(outside / "TASK-0600-old.md")
        (target / "vault/tasks/archive").symlink_to(outside, target_is_directory=True)

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("SYMLINK_INPUT", out)

    def test_prefix_marker_lookalike_is_not_a_block(self) -> None:
        index = "# Vault Index\n\n" + tracked_policy() + "\n\n<!-- trellium-policy-history\nsome archived notes\n-->\n"
        target = self.make_project(index=index)

        payload = self.check_json(target)

        self.assertEqual(payload["summary"]["errors"], 0)

    def test_duplicate_json_keys_are_rejected(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0001-x.md": "# TASK-0001 - X\n\n" + state_block(
                text='{ "schema_version": 1, "task_id": "TASK-0001", "level": "B", "authority_level": 2, "lifecycle": "draft", "lifecycle": "accepted" }'
            ) + "\n"}
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("TASK_STATE_INVALID", out)

    def test_check_is_read_only_and_deterministic(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0001-a.md": "# TASK-0001 - A\n\n" + state_block(valid_state()) + "\n"},
            runtime=build_runtime(),
        )
        self.init_git_repo(target)
        self.git(target, "add", "-A")
        before_snapshot = self.snapshot(target)
        before_status = self.git(target, "status", "--porcelain").stdout

        results = []
        for _ in range(3):
            code, out, _err = self.check(target, "--format", "json")
            self.assertEqual(code, 0)
            payload = json.loads(out)
            payload.pop("target")
            results.append(payload)

        self.assertEqual(results[0], results[1])
        self.assertEqual(results[1], results[2])
        self.assertEqual(before_snapshot, self.snapshot(target))
        self.assertEqual(before_status, self.git(target, "status", "--porcelain").stdout)

    def test_json_output_shape_is_stable(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0001-a.md": "# TASK-0001 - A\n\n" + state_block(valid_state()) + "\n"},
            runtime=build_runtime(),
        )

        _, out, _ = self.check(target, "--format", "json")
        payload = json.loads(out)

        self.assertEqual(
            set(payload),
            {"schema_version", "target", "summary", "findings", "measurements"},
        )
        for finding in payload["findings"]:
            self.assertLessEqual(
                {"code", "severity", "path", "message"} - set(finding),
                set(),
            )
            self.assertLessEqual(
                set(finding) - {"code", "severity", "path", "message", "task_id"},
                set(),
            )
        self.assertEqual(
            [(f["code"], f["severity"]) for f in payload["findings"]],
            [("GIT_CHECK_SKIPPED", "warning")],
        )

    def test_check_requires_existing_target_with_vault(self) -> None:
        code, _, err = self.check(self.root / "missing")
        self.assertEqual(code, 1)
        self.assertIn("existing directory", err)

        empty = self.root / "empty"
        empty.mkdir()
        code, _, err = self.check(empty)
        self.assertEqual(code, 1)
        self.assertIn("vault", err)

    def test_check_rejects_unknown_format(self) -> None:
        target = self.make_project()

        code, _, err = self.check(target, "--format", "yaml")

        self.assertEqual(code, 1)
        self.assertIn("format", err)

    def test_missing_required_files_are_reported(self) -> None:
        target = self.make_project()
        (target / "vault/parked.md").unlink()

        code, out, err = self.check(target)

        self.assertEqual(code, 0, err)
        self.assertIn("REQUIRED_FILE_MISSING", out)

    def test_missing_structural_files_are_reported(self) -> None:
        target = self.make_project()
        (target / "vault/project.md").unlink()
        (target / "vault/governance.md").unlink()
        (target / "vault/tasks/README.md").unlink()

        code, out, err = self.check(target)

        self.assertEqual(code, 0, err)
        self.assertIn("vault/project.md", out)
        self.assertIn("vault/governance.md", out)
        self.assertIn("vault/tasks/README.md", out)
        payload = self.check_json(target)
        missing = [f["path"] for f in payload["findings"] if f["code"] == "REQUIRED_FILE_MISSING"]
        self.assertEqual(
            sorted(missing),
            ["vault/governance.md", "vault/project.md", "vault/tasks/README.md"],
        )




class StatusSummaryTest(VaultCheckMixin, TargetTestCase):
    """Frozen 2026.09.5 contract: read-only status summary (TASK-0008)."""

    def status(self, target: Path, *extra: str) -> tuple[int, str, str]:
        return self.run_agent_init("status", str(target), *extra)

    def status_json(self, target: Path) -> tuple[int, dict, str]:
        code, out, err = self.status(target, "--format", "json")
        return code, json.loads(out), err

    def mixed_fixture(self, **kwargs) -> Path:
        files = {
            "vault/tasks/TASK-0010-draft.md": "# TASK-0010 - Draft\n\n" + state_block(valid_state(task_id="TASK-0010", level="B", authority_level=1)) + "\n",
            "vault/tasks/TASK-0011-active.md": "# TASK-0011 - Active\n\n" + state_block(valid_state(
                task_id="TASK-0011", lifecycle="active", authority_level=2,
                current_slice="M2", gates={"design": "passed", "launch": "not_authorized"},
            )) + "\n",
            "vault/tasks/TASK-0012-blocked.md": "# TASK-0012 - Blocked\n\n" + state_block(valid_state(
                task_id="TASK-0012", lifecycle="blocked", gates={"vendor": "blocked"},
            )) + "\n",
            "vault/tasks/TASK-0013-ready.md": "# TASK-0013 - Ready\n\n" + state_block(valid_state(
                task_id="TASK-0013", level="C", lifecycle="ready_for_review", authority_level=3,
            )) + "\n",
            "vault/tasks/TASK-0014-accepted.md": "# TASK-0014 - Accepted\n\n" + state_block(valid_state(
                task_id="TASK-0014", lifecycle="accepted",
            )) + "\n",
            "vault/tasks/TASK-0015-superseded.md": "# TASK-0015 - Superseded\n\n" + state_block(valid_state(
                task_id="TASK-0015", lifecycle="superseded",
            )) + "\n",
        }
        runtime = build_runtime(focus="TASK-0013")
        return self.make_project(files=files, runtime=runtime, **kwargs)

    def test_mixed_fixture_classifies_and_keeps_contract(self) -> None:
        target = self.mixed_fixture()

        code, out, err = self.status(target)
        self.assertEqual(code, 0, err)
        self.assertIn("focus: TASK-0013 (resolved)", out)
        self.assertIn(
            "summary: 1 draft, 1 active, 1 blocked, 1 ready_for_review, 2 closed, 0 unresolved", out
        )
        self.assertIn(
            "  TASK-0011 authority=2 slice=M2 gates: design=passed, launch=not_authorized"
            " path=vault/tasks/TASK-0011-active.md",
            out,
        )
        self.assertNotIn("## Active Tasks", (target / "vault/runtime.md").read_text(encoding="utf-8"))
        # Closed tasks are counts only: they never reach action lists.
        self.assertNotIn("TASK-0014", out)
        self.assertNotIn("TASK-0015", out)

        exit_json, payload, err = self.status_json(target)
        self.assertEqual(exit_json, 0, err)
        self.assertEqual(
            set(payload), {"schema_version", "target", "focus", "summary", "tasks", "findings"}
        )
        self.assertEqual(
            set(payload["tasks"]),
            {"ready_for_review", "blocked", "active", "draft", "unresolved"},
        )
        self.assertEqual(payload["summary"], {
            "draft": 1, "active": 1, "blocked": 1, "ready_for_review": 1, "closed": 2, "unresolved": 0,
        })
        self.assertEqual(payload["focus"], [{"task_id": "TASK-0013", "resolved": True}])
        self.assertEqual(
            [item["task_id"] for item in payload["tasks"]["ready_for_review"]], ["TASK-0013"]
        )
        active = payload["tasks"]["active"][0]
        self.assertEqual(
            set(active),
            {"task_id", "lifecycle", "authority_level", "task_path", "current_slice", "gates"},
        )
        self.assertEqual(active["lifecycle"], "active")
        self.assertEqual(active["authority_level"], 2)
        self.assertEqual(active["gates"], {"design": "passed", "launch": "not_authorized"})
        self.assertNotIn("runtime_projection", json.dumps(payload))
        self.assertEqual(
            [item["task_id"] for bucket in ("draft", "active", "blocked", "ready_for_review") for item in payload["tasks"][bucket]],
            ["TASK-0010", "TASK-0011", "TASK-0012", "TASK-0013"],
        )

    def test_task_state_changes_without_runtime_update(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0001-open.md": (
                "# TASK-0001 - Open\n\n" + state_block(valid_state(lifecycle="draft")) + "\n"
            )},
            runtime=build_runtime(focus="TASK-0001"),
        )
        runtime_before = (target / "vault/runtime.md").read_bytes()

        code, payload, err = self.status_json(target)
        self.assertEqual(code, 0, err)
        self.assertEqual([item["task_id"] for item in payload["tasks"]["draft"]], ["TASK-0001"])

        task = target / "vault/tasks/TASK-0001-open.md"
        task.write_text(
            "# TASK-0001 - Open\n\n" + state_block(valid_state(lifecycle="active")) + "\n",
            encoding="utf-8",
        )
        code, payload, err = self.status_json(target)
        self.assertEqual(code, 0, err)
        self.assertEqual([item["task_id"] for item in payload["tasks"]["active"]], ["TASK-0001"])
        self.assertEqual((target / "vault/runtime.md").read_bytes(), runtime_before)

    def test_missing_local_task_is_only_unresolved_navigation(self) -> None:
        target = self.make_project(
            policy=local_policy(),
            runtime=build_runtime(focus="TASK-0001"),
        )

        code, payload, err = self.status_json(target)

        self.assertEqual(code, 0, err)
        self.assertEqual(payload["tasks"]["unresolved"], [])
        self.assertEqual(payload["summary"]["unresolved"], 0)
        self.assertEqual(payload["findings"], [])
        self.assertEqual(payload["focus"], [{"task_id": "TASK-0001", "resolved": False}])

    def test_fail_closed_inputs_stay_unresolved(self) -> None:
        invalid = self.make_project(
            files={"vault/tasks/TASK-0001-x.md": "# TASK-0001 - X\n\n" + state_block(valid_state(lifecycle="onfire")) + "\n"},
        )
        code, payload, _err = self.status_json(invalid)
        self.assertEqual(code, 2)
        self.assertEqual(payload["tasks"]["unresolved"][0]["reason"], "TASK_STATE_INVALID")
        self.assertEqual(payload["tasks"]["draft"], [])

        block = state_block(valid_state())
        duplicate = self.make_project(
            files={
                "vault/tasks/TASK-0001-a.md": f"# TASK-0001 - A\n\n{block}\n",
                "vault/tasks/TASK-0001-b.md": f"# TASK-0001 - B\n\n{block}\n",
            },
        )
        code, payload, _err = self.status_json(duplicate)
        self.assertEqual(code, 2)
        unresolved = payload["tasks"]["unresolved"]
        self.assertEqual([item["task_id"] for item in unresolved], ["TASK-0001"])
        self.assertEqual(unresolved[0]["reason"], "TASK_ID_DUPLICATE")
        self.assertNotIn("task_path", unresolved[0])

        outside = self.root / "outside-status"
        outside.mkdir()
        (outside / "secret.md").write_text("OUTSIDE-STATUS-SECRET\n", encoding="utf-8")
        symlinked = self.make_project()
        (symlinked / "vault/tasks/TASK-0002-link.md").symlink_to(outside / "secret.md")
        code, payload, _err = self.status_json(symlinked)
        self.assertEqual(code, 2)
        self.assertEqual(payload["tasks"]["unresolved"][0]["reason"], "SYMLINK_INPUT")
        code, out, _err = self.status(symlinked)
        self.assertNotIn("OUTSIDE-STATUS-SECRET", out)

    def test_unreadable_task_file_is_unresolved_without_pointer(self) -> None:
        # A current task file that fails before any record exists (not a
        # regular file here) must still surface as unresolved even though no
        # runtime row or focus pointer references it.
        target = self.make_project()
        (target / "vault/tasks/TASK-0009-dir.md").mkdir()

        code, payload, _err = self.status_json(target)

        self.assertEqual(code, 2)
        unresolved = payload["tasks"]["unresolved"]
        self.assertEqual([item["task_id"] for item in unresolved], ["TASK-0009"])
        self.assertEqual(unresolved[0]["reason"], "FILE_UNREADABLE")
        self.assertNotIn("task_path", unresolved[0])
        self.assertNotIn("lifecycle", unresolved[0])
        self.assertEqual(payload["summary"]["unresolved"], 1)

    def test_cold_history_symlinks_do_not_create_phantom_unresolved(self) -> None:
        outside = self.root / "outside-cold"
        outside.mkdir()
        (outside / "old.md").write_text("OLD\n", encoding="utf-8")
        target = self.make_project(
            files={"vault/tasks/TASK-0001-review.md": "# TASK-0001 - Review Ledger\n"},
        )
        (target / "vault/tasks/TASK-0001-review.md").unlink()
        (target / "vault/tasks/TASK-0001-review.md").symlink_to(outside / "old.md")
        (target / "vault/tasks/archive").mkdir()
        (target / "vault/tasks/archive/TASK-0090-old.md").symlink_to(outside / "old.md")

        code, payload, _err = self.status_json(target)

        self.assertEqual(code, 2)
        self.assertEqual(payload["tasks"]["unresolved"], [])
        self.assertEqual(payload["summary"]["unresolved"], 0)

    def test_storage_findings_never_become_lifecycle_reasons(self) -> None:
        # The reason vocabulary is derived from lifecycle phases, not a code
        # allowlist: storage mismatches keep the task classified and never
        # leak into any reason string.
        target = self.make_project(
            policy=local_policy(),
            files={"vault/tasks/TASK-0001-quiet.md": "# TASK-0001 - Quiet\n\n" + state_block(valid_state()) + "\n"},
            runtime=build_runtime(),
        )
        self.init_git_repo(target)
        self.git(target, "add", "-A")

        code, payload, _err = self.status_json(target)

        self.assertEqual(code, 2)
        self.assertIn("TASK_STORAGE_MISMATCH", self.codes({"findings": payload["findings"]}))
        self.assertEqual([item["task_id"] for item in payload["tasks"]["draft"]], ["TASK-0001"])
        self.assertEqual(payload["tasks"]["unresolved"], [])
        self.assertNotIn("reason", payload["tasks"]["draft"][0])

    def test_status_is_read_only_and_deterministic(self) -> None:
        target = self.mixed_fixture()
        self.init_git_repo(target)
        self.git(target, "add", "-A")
        self.git(target, "commit", "-qm", "base")
        before_snapshot = self.snapshot(target)
        before_status = self.git(target, "status", "--porcelain").stdout

        outputs = []
        for _ in range(3):
            code, out, _err = self.status(target)
            self.assertEqual(code, 0)
            outputs.append(out)

        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(outputs[1], outputs[2])
        self.assertEqual(before_snapshot, self.snapshot(target))
        self.assertEqual(before_status, self.git(target, "status", "--porcelain").stdout)

    def test_status_requires_target_vault_and_known_format(self) -> None:
        code, _, err = self.status(self.root / "missing")
        self.assertEqual(code, 1)
        self.assertIn("existing directory", err)

        empty = self.root / "empty"
        empty.mkdir()
        code, _, err = self.status(empty)
        self.assertEqual(code, 1)
        self.assertIn("vault", err)

        target = self.make_project()
        code, _, err = self.status(target, "--format", "yaml")
        self.assertEqual(code, 1)
        self.assertIn("format", err)


class LocalTemplateSemanticsTest(TargetTestCase):
    """Round-2 R2: the hand-maintained distribution templates must carry the
    local lifecycle semantics; sync-skills does not validate these files."""

    REPO = Path(__file__).resolve().parent.parent

    def read(self, relative: str) -> str:
        return (self.REPO / relative).read_text(encoding="utf-8")

    def test_governance_templates_carry_local_disposition_gate(self) -> None:
        for relative in (
            "skills/trellium-zh/assets/templates/vault/governance.md",
            "skills/trellium/assets/templates/vault/governance.md",
        ):
            text = self.read(relative)
            self.assertIn("Durable Knowledge Disposition", text)
            self.assertIn("task_storage=local", text)
            self.assertIn("superseded", text)

    def test_index_templates_carry_local_storage_contract(self) -> None:
        for relative in (
            "skills/trellium-zh/assets/templates/vault/index.md",
            "skills/trellium/assets/templates/vault/index.md",
        ):
            text = self.read(relative)
            self.assertIn("task_storage=local", text)
            self.assertIn("storage contract", text)

    def test_handoff_templates_carry_local_close_deletion(self) -> None:
        for relative in (
            "skills/trellium-zh/assets/templates/vault/handoff.md",
            "skills/trellium/assets/templates/vault/handoff.md",
        ):
            text = self.read(relative)
            self.assertIn("task_storage=local", text)
            self.assertNotIn("compress", text.lower())
            self.assertNotIn("压缩", text)
            self.assertNotIn("runtime.md", text)

    def test_handoff_templates_use_transient_delta_contract(self) -> None:
        for relative in (
            "skills/trellium-zh/assets/templates/vault/handoff.md",
            "skills/trellium/assets/templates/vault/handoff.md",
        ):
            text = self.read(relative)
            for section in (
                "Why interrupted",
                "Transient context not captured elsewhere",
                "Exact resume point",
            ):
                self.assertIn(section, text)
            for legacy in (
                "Objective:",
                "Completed:",
                "In progress:",
                "Failed attempts:",
                "Blockers:",
                "Next best action:",
                "Files to read first:",
            ):
                self.assertNotIn(legacy, text)
            self.assertNotIn("## TASK-", text)
            self.assertNotIn("## SESSION", text)
            self.assertEqual(agent_init.count_handoff_entries(text), 0)

    def test_adopted_blank_handoff_measures_zero_entries(self) -> None:
        repo_packages = self.REPO / "skills"
        for package_name in ("trellium-zh", "trellium"):
            with self.subTest(package=package_name):
                copied = self.root / package_name
                shutil.copytree(repo_packages / package_name, copied)
                spec = importlib.util.spec_from_file_location(
                    f"adopt_blank_{package_name}", copied / "assets" / "trellium.py"
                )
                assert spec is not None and spec.loader is not None
                embedded = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(embedded)
                target = self.root / f"blank-{package_name}"
                target.mkdir()
                out, err = StringIO(), StringIO()
                with redirect_stdout(out), redirect_stderr(err):
                    code = embedded.main(["adopt", str(target)])
                self.assertEqual(code, 0, err.getvalue())
                handoff = (target / "vault/handoff.md").read_text(encoding="utf-8")
                self.assertIn("Why interrupted", handoff)
                self.assertEqual(agent_init.count_handoff_entries(handoff), 0)

    def test_task_readme_templates_carry_disposition_line(self) -> None:
        for relative in (
            "skills/trellium-zh/assets/templates/vault/tasks/README.md",
            "skills/trellium/assets/templates/vault/tasks/README.md",
        ):
            text = self.read(relative)
            self.assertIn("Durable knowledge disposition", text)
            self.assertIn("distilled", text)

    def test_agent_task_templates_carry_disposition_step(self) -> None:
        for relative in (
            "skills/trellium-zh/assets/templates/skills/agent-task/AGENT_TASK_SKILL.template",
            "skills/trellium/assets/templates/skills/agent-task/AGENT_TASK_SKILL.template",
        ):
            text = self.read(relative)
            self.assertIn("Durable knowledge disposition", text)
            self.assertIn("pending", text)

    def test_runtime_templates_are_navigation_only(self) -> None:
        for relative in (
            "skills/trellium-zh/assets/templates/vault/runtime.md",
            "skills/trellium/assets/templates/vault/runtime.md",
        ):
            text = self.read(relative)
            self.assertNotIn("## Active Tasks", text)
            self.assertTrue("navigation" in text or "导航" in text)

    # TASK-0022: live contract surfaces that must not carry mechanical scale
    # thresholds. Historical TASK files and MIGRATIONS may quote them as
    # history; the contract may not.
    LIVE_CLASSIFICATION_FILES = (
        "init/protocol/20-governance.md",
        "init/protocol/80-execution-patterns.md",
        "vault/governance.md",
        "vault/index.md",
        "skills/agent-task/SKILL.md",
        "skills/trellium/references/protocol-model.md",
        "skills/trellium-zh/references/protocol-model.md",
        "skills/trellium/assets/templates/vault/governance.md",
        "skills/trellium-zh/assets/templates/vault/governance.md",
        "skills/trellium/assets/templates/vault/index.md",
        "skills/trellium-zh/assets/templates/vault/index.md",
        "skills/trellium/assets/templates/skills/agent-task/AGENT_TASK_SKILL.template",
        "skills/trellium-zh/assets/templates/skills/agent-task/AGENT_TASK_SKILL.template",
    )

    SCALE_THRESHOLD_PHRASES = (
        "1-2 files",
        "one or two files",
        "1-2 个文件",
        "一到两个文件",
        "more than two files",
        "两个以上文件",
        "2 个以上文件",
        "more than three acceptance criteria",
        "验收标准超过三条",
        "验收标准超过 3 条",
    )

    def test_canonical_classification_is_risk_first_c_before_b_before_a(self) -> None:
        text = self.read("init/protocol/20-governance.md")
        levels = text.split("## 任务等级", 1)[1].split("## 任务生命周期", 1)[0]
        # Canonical three-step flow, in order: Level C risk domain, then
        # interruption-recovery or collaboration cost, then default A.
        self.assertLess(levels.index("命中 Level C 风险域"), levels.index("中断恢复或协作成本"))
        self.assertLess(levels.index("中断恢复或协作成本"), levels.index("→ A"))
        self.assertLess(levels.index("### Level C"), levels.index("### Level B"))
        self.assertLess(levels.index("### Level B"), levels.index("### Level A"))
        # Scale may prompt further judgment but never decides the level alone.
        self.assertIn("提示进一步判断", levels)
        self.assertIn("不能单独决定", levels)
        # A one-line high-risk change is still C; Level B signals are strong
        # signals, not a mechanical any-match checklist.
        self.assertIn("一行", levels)
        self.assertIn("强信号", levels)
        # Architecture is an explicit Level C risk domain in the canonical
        # list, not merely an implication of governance/policy.
        self.assertIn("重大架构决策", levels)
        # A later unexpected interruption does not retroactively make the
        # original classification wrong.
        self.assertIn("≠", levels)
        # The old mechanical-enrollment phrasing must be gone entirely.
        self.assertNotIn("满足任一条件即升级", text)
        self.assertNotIn("满足任一条件即属于治理任务", text)

    def test_scale_thresholds_are_gone_from_live_contract(self) -> None:
        for relative in self.LIVE_CLASSIFICATION_FILES:
            text = self.read(relative)
            for phrase in self.SCALE_THRESHOLD_PHRASES:
                self.assertNotIn(phrase, text, f"{relative} still carries {phrase!r}")

    def test_canonical_governance_template_carries_risk_first_semantics(self) -> None:
        expectations = {
            "skills/trellium-zh/assets/templates/vault/governance.md": (
                "风险域",
                "恢复",
                "协作成本",
                "默认",
                "一行",
                "架构",
            ),
            "skills/trellium/assets/templates/vault/governance.md": (
                "risk domain",
                "recovery",
                "coordination cost",
                "default",
                "one-line",
                "architecture",
            ),
        }
        for relative, markers in expectations.items():
            text = self.read(relative)
            for marker in markers:
                self.assertIn(marker, text, f"{relative} lacks {marker!r}")

    def test_index_cheat_sheets_carry_risk_first_semantics(self) -> None:
        expectations = {
            "vault/index.md": ("风险域", "恢复", "默认", "架构"),
            "skills/trellium-zh/assets/templates/vault/index.md": ("风险域", "恢复", "默认", "架构"),
            "skills/trellium/assets/templates/vault/index.md": ("risk domain", "recovery", "default", "architecture"),
        }
        for relative, markers in expectations.items():
            text = self.read(relative)
            for marker in markers:
                self.assertIn(marker, text, f"{relative} lacks {marker!r}")

    def test_agent_task_classification_stays_three_steps(self) -> None:
        expectations = {
            "skills/agent-task/SKILL.md": ("三步", "风险域", "协作成本", "→ A"),
            "skills/trellium-zh/assets/templates/skills/agent-task/AGENT_TASK_SKILL.template": (
                "三步",
                "风险域",
                "协作成本",
                "→ A",
            ),
            "skills/trellium/assets/templates/skills/agent-task/AGENT_TASK_SKILL.template": (
                "three-step",
                "risk domain",
                "coordination cost",
                "→ A",
            ),
        }
        for relative, markers in expectations.items():
            text = self.read(relative)
            for marker in markers:
                self.assertIn(marker, text, f"{relative} lacks {marker!r}")
            self.assertNotIn("满足任一条件", text)

    def test_protocol_model_references_carry_risk_first_semantics(self) -> None:
        expectations = {
            "skills/trellium-zh/references/protocol-model.md": ("风险域", "恢复", "协作成本", "默认", "架构"),
            "skills/trellium/references/protocol-model.md": (
                "risk domain",
                "recovery",
                "coordination cost",
                "default",
                "architecture",
            ),
        }
        for relative, markers in expectations.items():
            text = self.read(relative)
            for marker in markers:
                self.assertIn(marker, text, f"{relative} lacks {marker!r}")

    def test_execution_patterns_level_a_defers_to_project_global_runtime(self) -> None:
        text = self.read("init/protocol/80-execution-patterns.md")
        self.assertNotIn("并在 `vault/runtime.md` 记录必要状态", text)
        self.assertIn("仅当 project-global runtime 发生变化时更新 `vault/runtime.md`", text)


class StatusDefectRegressionsTest(VaultCheckMixin, TargetTestCase):
    """TASK-0010: three reproduced status defects (owner adjudicated P1/P1/P2).

    Frozen output design: vault-scope unresolved entries use the explicit
    joint record {scope, path, reason} — never a synthetic task id, never a
    bare summary clamp.
    """

    def status(self, target: Path, *extra: str) -> tuple[int, str, str]:
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = agent_init.main(["status", str(target), *extra])
        return code, out.getvalue(), err.getvalue()

    def status_json(self, target: Path) -> tuple[int, dict, str]:
        code, out, err = self.status(target, "--format", "json")
        return code, json.loads(out), err

    def one_active_project(self, runtime: str) -> Path:
        files = {
            "vault/tasks/TASK-0001-active.md": "# TASK-0001\n\n"
            + state_block(valid_state(task_id="TASK-0001", lifecycle="active"))
            + "\n"
        }
        return self.make_project(files=files, runtime=runtime)

    def test_refused_vault_emits_vault_scope_unresolved_record(self) -> None:
        runtime = build_runtime(focus="TASK-0001")
        target = self.one_active_project(runtime)
        outside = self.root / "outside-enumeration"
        outside.mkdir()
        shutil.rmtree(target / "vault" / "tasks")
        os.symlink(outside, target / "vault" / "tasks")
        (target / "vault" / "runtime.md").unlink()
        os.symlink(Path(outside) / "missing", target / "vault" / "runtime.md")

        code, payload, err = self.status_json(target)
        self.assertEqual(code, 2, err)
        entries = payload["tasks"]["unresolved"]
        scope_entries = [e for e in entries if e.get("scope") == "vault"]
        self.assertEqual(len(scope_entries), 1)
        self.assertEqual(scope_entries[0]["path"], "vault/tasks")
        self.assertEqual(scope_entries[0]["reason"], "SYMLINK_INPUT")
        self.assertNotIn("task_id", scope_entries[0])
        self.assertNotIn("lifecycle", scope_entries[0])
        self.assertNotIn("authority_level", scope_entries[0])
        self.assertEqual(
            payload["summary"]["unresolved"], len(entries), "count must match the array"
        )
        code, out, _ = self.status(target)
        self.assertIn("SYMLINK_INPUT", out)

class TemplatePackagingTest(TargetTestCase):
    """TASK-0011 No-Go stop-condition fix: the control packages must not carry
    a discoverable SKILL.md template (Codex globally discovered the nested
    agent-task template). adopt/upgrade must still render the target project's
    skills/agent-task/SKILL.md via the source-name override."""

    def test_profile_routing_paragraph_parity_across_append_and_templates(self) -> None:
        """TASK-0023 review residual: the routing semantic contract lives in three
        hand-maintained copies (en/zh template AGENTS.md plus the appended
        agent_entry_section). Freeze whole-paragraph parity between the appended
        copy and the en template, and freeze the shared routing invariants in all
        three copies, so wording drift cannot silently reintroduce the
        appended-vs-template divergence TASK-0023 fixed."""
        repo = Path(__file__).resolve().parents[1]

        def normalize(paragraph: str) -> str:
            return " ".join(paragraph.split())

        def routing_paragraph(markdown: str) -> str:
            matches = [
                p.strip()
                for p in markdown.split("\n\n")
                if agent_init.PROFILE_DOCUMENT_DIRECTORY in p
            ]
            self.assertEqual(len(matches), 1)
            return matches[0]

        section = agent_init.agent_entry_section()
        appended_body = section.split(agent_init.AGENTS_MARKER_START, 1)[1].split(
            agent_init.AGENTS_MARKER_END, 1
        )[0]
        appended_paragraphs = [p.strip() for p in appended_body.strip().split("\n\n") if p.strip()]
        appended = normalize(appended_paragraphs[-1])

        en_template = (repo / "skills/trellium/assets/templates/AGENTS.md").read_text(encoding="utf-8")
        zh_template = (repo / "skills/trellium-zh/assets/templates/AGENTS.md").read_text(
            encoding="utf-8"
        )
        en_routing = normalize(routing_paragraph(en_template))
        zh_routing = normalize(routing_paragraph(zh_template))

        # The appended copy and the en template must stay verbatim-equal
        # (whitespace-normalized); this equality is exactly what eroded before.
        self.assertEqual(appended, en_routing)

        # Shared routing invariants, frozen in all three copies.
        surfaces = {
            "appended": appended,
            "en template": en_routing,
            "zh template": zh_routing,
        }
        for surface, paragraph in surfaces.items():
            with self.subTest(surface=surface):
                self.assertIn("docs/engineering/profiles/", paragraph)
                self.assertIn("docs/engineering/code-comments.md", paragraph)
                if surface == "zh template":
                    self.assertIn("root 与当前路径匹配", paragraph)
                    self.assertIn("不读取未匹配语言", paragraph)
                    self.assertIn("以该兼容文档为项目定制优先", paragraph)
                    self.assertIn("完整 profile 继续约束其余工程事项", paragraph)
                else:
                    self.assertIn("declared root matches the current path", paragraph)
                    self.assertIn("do not load unmatched languages", paragraph)
                    self.assertIn("take precedence as project customization", paragraph)
                    self.assertIn("still governs all other engineering concerns", paragraph)

    def test_control_packages_carry_no_discoverable_skill_template(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        for package in ("trellium", "trellium-zh"):
            templates = repo / "skills" / package / "assets" / "templates"
            discoverable = list(templates.rglob("SKILL.md"))
            self.assertEqual(discoverable, [], f"{package} leaks a discoverable template: {discoverable}")
            packaged = templates / "skills" / "agent-task" / "AGENT_TASK_SKILL.template"
            self.assertTrue(packaged.is_file(), f"missing renamed template source: {packaged}")

    def test_adopt_still_renders_agent_task_skill_md(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.run_agent_init("adopt", str(target))
        self.assertEqual(code, 0, err)
        rendered = target / "skills" / "agent-task" / "SKILL.md"
        self.assertTrue(rendered.is_file(), "adopt must still render skills/agent-task/SKILL.md")
        self.assertIn("name: agent-task", rendered.read_text(encoding="utf-8"))

    def test_localized_profile_templates_have_matching_sections_and_routes(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        for package, common_heading in (
            ("trellium", "## Common Principles"),
            ("trellium-zh", "## 通用原则"),
        ):
            templates = repo / "skills" / package / "assets" / "templates"
            policy = (templates / agent_init.PROFILE_RULES_TEMPLATE).read_text(encoding="utf-8")
            agents = (templates / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn(common_heading, policy)
            self.assertEqual(policy.count(agent_init.PROFILE_SCOPE_PLACEHOLDER), 1)
            for section in ("common", *agent_init.PROFILE_IDS):
                self.assertEqual(
                    policy.count(f"<!-- {agent_init.PROFILE_MARKER_PREFIX}:{section}:start -->"),
                    1,
                )
                self.assertEqual(
                    policy.count(f"<!-- {agent_init.PROFILE_MARKER_PREFIX}:{section}:end -->"),
                    1,
                )
            self.assertIn(agent_init.PROFILE_RULES_RELATIVE, agents)
            self.assertIn(agent_init.PROFILE_DOCUMENT_DIRECTORY, agents)
            if package == "trellium":
                self.assertIn("take precedence as project customization", agents)
                self.assertIn("still governs all other engineering concerns", agents)
            else:
                self.assertIn("以该兼容文档为项目定制优先", agents)
                self.assertIn("完整 profile 继续约束其余工程事项", agents)
            for profile_id in agent_init.PROFILE_IDS:
                durable = templates / agent_init.PROFILE_DOCUMENT_TEMPLATE_DIRECTORY / f"{profile_id}.md"
                self.assertTrue(durable.is_file())
                text = durable.read_text(encoding="utf-8")
                if package == "trellium":
                    self.assertNotIn("## 定位", text)
                    self.assertIn("## Purpose", text)
                    expected = {
                        "go-backend": (
                            "Modules, workspaces, and dependencies",
                            "Packages and structure",
                            "Errors",
                            "Resource lifecycle",
                            "Context and concurrency",
                            "HTTP and service lifecycle",
                            "Tests and verification",
                            "API documentation",
                        ),
                        "python-backend": (
                            "Packages and dependencies",
                            "API and models",
                            "Configuration and security",
                            "Async and resource lifecycle",
                            "Errors",
                            "Quality and tests",
                            "documentation",
                        ),
                    }[profile_id]
                    for category in expected:
                        self.assertIn(category, text)
                else:
                    canonical = repo / "init/protocol/profiles" / f"{profile_id}.md"
                    self.assertEqual(durable.read_bytes(), canonical.read_bytes())
            self.assertNotIn("vault/index.md ->", agents)


class AdoptionDurabilityTest(VaultCheckMixin, TargetTestCase):
    """TASK-0013 adoption-durability contract tests (prereg:
    docs/evals/adoption-durability-2026-09/, severity matrix section 9).

    These replay the confirmed 2026.09.7 false-health reproduction (fresh
    `adopt` leaving the collaboration core outside Git HEAD while check
    reported zero findings). The red-first state was committed at M0 with
    expectedFailure markers; the M2/M3 HEAD-persistence and local-boundary
    checks turned them green and removed the markers in the same change.
    """

    def adopted_repo(self, name: str = "project") -> Path:
        target = self.root / name
        target.mkdir()
        (target / "README.md").write_text("# Demo\n", encoding="utf-8")
        self.init_git_repo(target)
        self.git(target, "add", "README.md")
        self.git(target, "commit", "-q", "-m", "init")
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        return target

    def check_payload(self, target: Path) -> tuple[int, dict]:
        code, out, err = self.run_agent_init("check", str(target), "--format", "json")
        return code, json.loads(out)

    @staticmethod
    def findings_with(payload: dict, code: str) -> list[dict]:
        return [finding for finding in payload["findings"] if finding["code"] == code]

    @staticmethod
    def reported_paths(findings: list[dict]) -> str:
        return " ".join(str(finding.get("path", "")) for finding in findings)

    def test_untracked_core_after_adopt_is_reported(self) -> None:
        target = self.adopted_repo()

        check_code, payload = self.check_payload(target)

        uncommitted = self.findings_with(payload, "CORE_STORAGE_UNCOMMITTED")
        self.assertTrue(uncommitted, payload["findings"])
        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        reported = self.reported_paths(uncommitted)
        for core in ("AGENTS.md", "vault/index.md", agent_init.STAMP_RELATIVE, "skills/agent-task/SKILL.md"):
            self.assertIn(core, reported)

    def test_profile_documents_are_core_and_survive_fresh_clone(self) -> None:
        target = self.root / "profile-project"
        target.mkdir()
        (target / "README.md").write_text("# Demo\n", encoding="utf-8")
        self.init_git_repo(target)
        self.git(target, "add", "README.md")
        self.git(target, "commit", "-q", "-m", "init")
        code, _, err = self.adopt(target, "--profile", "go-backend=services/api")
        self.assertEqual(code, 0, err)
        relative = agent_init.profile_document_relative("go-backend")

        check_code, payload = self.check_payload(target)
        uncommitted = self.findings_with(payload, "CORE_STORAGE_UNCOMMITTED")
        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        self.assertIn(relative, self.reported_paths(uncommitted))

        self.git(target, "add", ".")
        self.git(target, "commit", "-q", "-m", "adopt")
        clone = self.root / "fresh-clone"
        subprocess.run(
            ["git", "clone", "-q", str(target), str(clone)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertTrue((clone / relative).is_file())
        clone_code, clone_payload = self.check_payload(clone)
        self.assertEqual(clone_code, 0, clone_payload["findings"])

    def test_staged_only_core_is_still_uncommitted(self) -> None:
        target = self.adopted_repo()
        self.git(target, "add", "-A")

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        self.assertTrue(self.findings_with(payload, "CORE_STORAGE_UNCOMMITTED"), payload["findings"])

    def test_stamp_only_partial_commit_still_reports_missing_core(self) -> None:
        target = self.adopted_repo()
        self.git(target, "add", agent_init.STAMP_RELATIVE)
        self.git(target, "commit", "-q", "-m", "stamp only")

        check_code, payload = self.check_payload(target)

        uncommitted = self.findings_with(payload, "CORE_STORAGE_UNCOMMITTED")
        self.assertTrue(uncommitted, payload["findings"])
        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        reported = self.reported_paths(uncommitted)
        self.assertIn("AGENTS.md", reported)
        self.assertNotIn(agent_init.STAMP_RELATIVE, reported)

    def test_invalid_json_stamp_is_an_error_not_unadopted(self) -> None:
        target = self.adopted_repo()
        (target / agent_init.STAMP_RELATIVE).write_text("{not-json\n", encoding="utf-8")

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        invalid = self.findings_with(payload, "CORE_STORAGE_INVALID")
        self.assertEqual(len(invalid), 1, payload["findings"])
        self.assertIn("not valid JSON", invalid[0]["message"])

    def test_wrong_stamp_schema_is_an_error_not_unadopted(self) -> None:
        target = self.adopted_repo()
        (target / agent_init.STAMP_RELATIVE).write_text(
            json.dumps({"schema_version": 2, "protocol_version": "2026.09.8", "files": []}),
            encoding="utf-8",
        )

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        self.assertEqual(len(self.findings_with(payload, "CORE_STORAGE_INVALID")), 1)

    def test_unsupported_or_non_integer_stamp_schema_version_is_invalid(self) -> None:
        for index, schema_version in enumerate((999, True, "2")):
            with self.subTest(schema_version=schema_version):
                target = self.adopted_repo(name=f"invalid-schema-version-{index}")
                stamp = self.read_stamp(target)
                stamp["schema_version"] = schema_version
                (target / agent_init.STAMP_RELATIVE).write_text(
                    json.dumps(stamp, indent=2, sort_keys=True) + "\n", encoding="utf-8"
                )

                check_code, payload = self.check_payload(target)

                self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
                invalid = self.findings_with(payload, "CORE_STORAGE_INVALID")
                self.assertEqual(len(invalid), 1, payload["findings"])
                self.assertIn("schema_version", invalid[0]["message"])

    def test_stamp_file_keys_reject_absolute_empty_and_noncanonical_paths(self) -> None:
        invalid_paths = (
            "/absolute.md",
            "",
            ".",
            "../outside.md",
            "vault/../outside.md",
            "./vault/index.md",
            "vault/./index.md",
            "vault//index.md",
            "vault/index.md/",
        )
        for index, relative in enumerate(invalid_paths):
            with self.subTest(relative=relative):
                target = self.adopted_repo(name=f"invalid-managed-path-{index}")
                stamp = self.read_stamp(target)
                stamp["files"][relative] = {"role": "merge", "baseline": "0" * 64}
                (target / agent_init.STAMP_RELATIVE).write_text(
                    json.dumps(stamp, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )

                check_code, payload = self.check_payload(target)

                self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
                invalid = self.findings_with(payload, "CORE_STORAGE_INVALID")
                self.assertEqual(len(invalid), 1, payload["findings"])
                self.assertIn("invalid managed path", invalid[0]["message"])

    def test_legacy_v1_stamp_schema_remains_supported(self) -> None:
        target = self.adopted_repo()
        stamp = self.read_stamp(target)
        stamp["schema_version"] = 1
        (target / agent_init.STAMP_RELATIVE).write_text(
            json.dumps(stamp, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.git(target, "add", "-A")
        self.git(target, "commit", "-q", "-m", "adopt trellium with legacy stamp")

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, 0, payload["findings"])
        self.assertEqual(self.findings_with(payload, "CORE_STORAGE_INVALID"), [])

    def test_worktree_stamp_cannot_shrink_head_managed_files(self) -> None:
        target = self.adopted_repo()
        self.git(target, "add", "-A")
        self.git(target, "commit", "-q", "-m", "adopt trellium")
        stamp = self.read_stamp(target)
        stamp["files"].pop("vault/governance.md")
        (target / agent_init.STAMP_RELATIVE).write_text(
            json.dumps(stamp, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        uncommitted = self.findings_with(payload, "CORE_STORAGE_UNCOMMITTED")
        self.assertIn(agent_init.STAMP_RELATIVE, self.reported_paths(uncommitted))
        self.assertIn("managed core file set", " ".join(item["message"] for item in uncommitted))

    def test_worktree_stamp_protocol_must_match_head(self) -> None:
        target = self.adopted_repo()
        self.git(target, "add", "-A")
        self.git(target, "commit", "-q", "-m", "adopt trellium")
        stamp = self.read_stamp(target)
        stamp["protocol_version"] = "9999.99.99"
        (target / agent_init.STAMP_RELATIVE).write_text(
            json.dumps(stamp, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        uncommitted = self.findings_with(payload, "CORE_STORAGE_UNCOMMITTED")
        self.assertIn(agent_init.STAMP_RELATIVE, self.reported_paths(uncommitted))
        self.assertIn("protocol_version", " ".join(item["message"] for item in uncommitted))

    def test_ignored_core_is_reported_with_path(self) -> None:
        target = self.root / "project"
        target.mkdir()
        (target / "README.md").write_text("# Demo\n", encoding="utf-8")
        (target / ".gitignore").write_text("AGENTS.md\nskills/\n", encoding="utf-8")
        self.init_git_repo(target)
        self.git(target, "add", "README.md", ".gitignore")
        self.git(target, "commit", "-q", "-m", "init")
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)

        check_code, payload = self.check_payload(target)

        ignored = self.findings_with(payload, "CORE_STORAGE_IGNORED")
        self.assertTrue(ignored, payload["findings"])
        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        reported = self.reported_paths(ignored)
        self.assertIn("AGENTS.md", reported)
        self.assertIn("skills/agent-task/SKILL.md", reported)

    def test_repository_without_head_reports_uncommitted_core(self) -> None:
        target = self.root / "project"
        target.mkdir()
        self.init_git_repo(target)
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        self.assertTrue(self.findings_with(payload, "CORE_STORAGE_UNCOMMITTED"), payload["findings"])

    def test_committed_core_passes_despite_dirty_worktree(self) -> None:
        # Control (must stay green): normal daily edits after a focused commit
        # are exactly the state the checker must keep accepting (prereg §9 #4).
        target = self.adopted_repo()
        self.git(target, "add", "-A")
        self.git(target, "commit", "-q", "-m", "adopt trellium")
        runtime = target / "vault/runtime.md"
        runtime.write_text(runtime.read_text(encoding="utf-8") + "\n- normal daily edit\n", encoding="utf-8")

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, 0, payload["findings"])
        self.assertEqual(self.findings_with(payload, "CORE_STORAGE_UNCOMMITTED"), [])
        self.assertEqual(self.findings_with(payload, "CORE_STORAGE_IGNORED"), [])

    def test_head_marker_removal_is_reported_even_when_worktree_matches_head(self) -> None:
        target = self.root / "project"
        target.mkdir()
        (target / "AGENTS.md").write_text("# Existing project rules\n", encoding="utf-8")
        self.init_git_repo(target)
        self.git(target, "add", "AGENTS.md")
        self.git(target, "commit", "-q", "-m", "init")
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.read_stamp(target)["files"]["AGENTS.md"]["role"], "marker")
        self.git(target, "add", "-A")
        self.git(target, "commit", "-q", "-m", "adopt trellium")
        agents = target / "AGENTS.md"
        agents.write_text("# Existing project rules\n", encoding="utf-8")
        self.git(target, "add", "AGENTS.md")
        self.git(target, "commit", "-q", "-m", "remove managed marker")
        # Marker requirements come from the committed stamp, not mutable
        # worktree metadata that can be changed to suppress the HEAD check.
        stamp = self.read_stamp(target)
        stamp["files"]["AGENTS.md"]["role"] = "merge"
        (target / agent_init.STAMP_RELATIVE).write_text(
            json.dumps(stamp, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        findings = self.findings_with(payload, "CORE_STORAGE_UNCOMMITTED")
        self.assertIn("AGENTS.md", self.reported_paths(findings))

    def test_head_marker_must_be_unique_and_well_formed(self) -> None:
        malformed_regions = (
            f"{agent_init.AGENTS_MARKER_START}\nmissing end\n",
            (
                f"{agent_init.AGENTS_MARKER_START}\none\n{agent_init.AGENTS_MARKER_END}\n"
                f"{agent_init.AGENTS_MARKER_START}\ntwo\n{agent_init.AGENTS_MARKER_END}\n"
            ),
            f"{agent_init.AGENTS_MARKER_END}\n{agent_init.AGENTS_MARKER_START}\n",
        )
        for index, malformed in enumerate(malformed_regions):
            with self.subTest(index=index):
                target = self.root / f"malformed-marker-{index}"
                target.mkdir()
                (target / "AGENTS.md").write_text("# Existing project rules\n", encoding="utf-8")
                self.init_git_repo(target)
                self.git(target, "add", "AGENTS.md")
                self.git(target, "commit", "-q", "-m", "init")
                code, _, err = self.adopt(target)
                self.assertEqual(code, 0, err)
                self.git(target, "add", "-A")
                self.git(target, "commit", "-q", "-m", "adopt trellium")
                (target / "AGENTS.md").write_text(
                    "# Existing project rules\n\n" + malformed,
                    encoding="utf-8",
                )
                self.git(target, "add", "AGENTS.md")
                self.git(target, "commit", "-q", "-m", "malform managed marker")

                check_code, payload = self.check_payload(target)

                self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
                findings = self.findings_with(payload, "CORE_STORAGE_UNCOMMITTED")
                self.assertIn("AGENTS.md", self.reported_paths(findings))

    def make_local_project(self, gitignore: str | None) -> Path:
        files = {} if gitignore is None else {".gitignore": gitignore}
        target = self.make_project(policy=local_policy(), files=files, runtime=build_runtime(focus="TASK-0000"))
        self.init_git_repo(target)
        self.git(target, "add", "-A")
        return target

    def test_local_boundary_good_rules_pass_clean(self) -> None:
        # Prereg §9 #9 (good): narrow private journal rules leave the durable
        # namespaces tracked and produce zero boundary findings.
        target = self.make_local_project(
            "vault/tasks/TASK-*.md\nvault/tasks/*-review.md\nvault/tasks/archive/\n"
        )

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, 0, payload["findings"])
        self.assertEqual(
            [finding for finding in payload["findings"] if finding["code"].startswith("LOCAL_BOUNDARY")],
            [],
        )

    def test_local_boundary_overreach_reports_rule_and_path(self) -> None:
        # Prereg §9 #9 (bad): broad rules silently capture durable namespaces;
        # the error names the sentinel path and the offending rule.
        target = self.make_local_project("vault/tasks/*\nvault/decisions/\nvault/details/\n")

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        overreach = self.findings_with(payload, "LOCAL_BOUNDARY_OVERREACH")
        reported = self.reported_paths(overreach)
        self.assertIn("vault/tasks/README.md", reported)
        self.assertIn("vault/decisions/D-0000-sentinel.md", reported)
        self.assertIn("vault/details/sentinel.md", reported)
        self.assertIn("vault/tasks/*", " ".join(finding["message"] for finding in overreach))

    def test_local_boundary_missing_rules_warn(self) -> None:
        # local policy without any ignore rules must not stay silent: future
        # private journals would otherwise enter Git unguarded.
        target = self.make_local_project(None)

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, 0, payload["findings"])
        self.assertEqual(len(self.findings_with(payload, "LOCAL_BOUNDARY_UNCONFIGURED")), 1)

    def test_check_ignore_failure_is_error_for_adopted_local_project_without_tasks(self) -> None:
        target = self.adopted_repo()
        index = target / "vault/index.md"
        index.write_text(
            index.read_text(encoding="utf-8").replace(
                '"task_storage": "tracked"', '"task_storage": "local"'
            ),
            encoding="utf-8",
        )
        (target / ".gitignore").write_text(
            "vault/tasks/TASK-*.md\nvault/tasks/*-review.md\nvault/tasks/archive/\n",
            encoding="utf-8",
        )
        self.assertEqual(list((target / "vault/tasks").glob("TASK-*.md")), [])
        self.git(target, "add", "-A")
        self.git(target, "commit", "-q", "-m", "adopt local trellium")
        real_git_run = agent_init.git_run

        def failing_check_ignore(
            cwd: Path, arguments: list[str], input_bytes: bytes | None = None
        ) -> subprocess.CompletedProcess | None:
            if arguments and arguments[0] == "check-ignore":
                return subprocess.CompletedProcess(["git", *arguments], 128, b"", b"failure")
            return real_git_run(cwd, arguments, input_bytes)

        with patch.object(agent_init, "git_run", side_effect=failing_check_ignore):
            check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        core = self.findings_with(payload, "CORE_STORAGE_UNVERIFIED")
        boundary = self.findings_with(payload, "LOCAL_BOUNDARY_UNVERIFIED")
        self.assertEqual([(item["severity"], item["path"]) for item in core], [("error", agent_init.STAMP_RELATIVE)])
        self.assertEqual([(item["severity"], item["path"]) for item in boundary], [("error", "vault/tasks")])

    def test_adopt_output_never_claims_commit_facts(self) -> None:
        # Review finding: the ending block must not assert Git facts ("none
        # of the generated files is committed") that are false for dry-run,
        # idempotent repeats on committed projects, partial changes, or
        # non-Git targets. Durability is decided by HEAD and confirmed by
        # check, never by the adopt run itself.
        committed = self.adopted_repo()
        self.git(committed, "add", "-A")
        self.git(committed, "commit", "-q", "-m", "adopt trellium")
        plain = self.root / "plain"
        plain.mkdir()

        scenarios: dict[str, tuple[Path, tuple[str, ...]]] = {
            "dry-run": (self.adopted_repo(name="dry-run-target"), ("--dry-run",)),
            "idempotent-committed": (committed, ()),
            "non-git": (plain, ()),
        }
        for name, (target, extra) in scenarios.items():
            code, out, err = self.run_agent_init("adopt", str(target), *extra)
            self.assertEqual(code, 0, err)
            with self.subTest(scenario=name):
                self.assertNotIn("none of the generated files is committed", out)
                self.assertNotIn("not durable yet", out)
                self.assertNotIn("to finish adoption", out)
                self.assertIn("generated does not mean durable", out)
                self.assertIn(
                    "adoption durability checklist (apply applicable steps in order):", out
                )

        # Partial change: one core file missing, everything else skipped.
        (committed / "AGENTS.md").unlink()
        code, out, err = self.run_agent_init("adopt", str(committed))
        self.assertEqual(code, 0, err)
        self.assertNotIn("none of the generated files is committed", out)
        self.assertNotIn("not durable yet", out)
        self.assertNotIn("to finish adoption", out)
        self.assertIn("generated does not mean durable", out)
        self.assertIn("adoption durability checklist (apply applicable steps in order):", out)

    def test_whitelist_gitignore_is_not_reported_as_ignored(self) -> None:
        # A `/*` + negated-whitelist .gitignore (this repository's own style)
        # must not read as "core ignored": check-ignore -v reports the
        # negated match too, and a leading "!" means the path stays tracked.
        repo = self.root / "project"
        repo.mkdir()
        (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
        (repo / ".gitignore").write_text(
            "/*\n!README.md\n!AGENTS.md\n!/skills/\n!/skills/**\n!/vault/\n!/vault/**\n",
            encoding="utf-8",
        )
        self.init_git_repo(repo)
        self.git(repo, "add", "-A")
        self.git(repo, "commit", "-q", "-m", "init")
        code, _, err = self.adopt(repo)
        self.assertEqual(code, 0, err)
        self.git(repo, "add", "-A")
        self.git(repo, "commit", "-q", "-m", "adopt trellium")

        check_code, payload = self.check_payload(repo)

        self.assertEqual(check_code, 0, payload["findings"])
        self.assertEqual(self.findings_with(payload, "CORE_STORAGE_IGNORED"), [])

    def test_monorepo_child_uncommitted_core_is_reported_with_target_paths(self) -> None:
        # Prereg §9 #7: paths must resolve against the real Git root so a
        # monorepo child adoption is judged (and reported) without crossing
        # outside its own directory.
        repo = self.root / "monorepo"
        app = repo / "packages" / "app"
        app.mkdir(parents=True)
        (app / "README.md").write_text("# App\n", encoding="utf-8")
        self.init_git_repo(repo)
        self.git(repo, "add", "packages/app/README.md")
        self.git(repo, "commit", "-q", "-m", "init")
        code, _, err = self.adopt(app)
        self.assertEqual(code, 0, err)

        check_code, payload = self.check_payload(app)

        uncommitted = self.findings_with(payload, "CORE_STORAGE_UNCOMMITTED")
        self.assertTrue(uncommitted, payload["findings"])
        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        for finding in uncommitted:
            self.assertFalse(finding["path"].startswith("packages/"), finding["path"])
            self.assertTrue((app / finding["path"]).exists(), finding["path"])
        for core in ("AGENTS.md", "vault/index.md", agent_init.STAMP_RELATIVE):
            self.assertIn(core, self.reported_paths(uncommitted))

    def test_monorepo_child_committed_core_passes(self) -> None:
        # Control (prereg §9 #7): a fully committed monorepo child adoption
        # must produce zero core findings.
        repo = self.root / "monorepo"
        app = repo / "packages" / "app"
        app.mkdir(parents=True)
        (app / "README.md").write_text("# App\n", encoding="utf-8")
        self.init_git_repo(repo)
        self.git(repo, "add", "packages/app/README.md")
        self.git(repo, "commit", "-q", "-m", "init")
        code, _, err = self.adopt(app)
        self.assertEqual(code, 0, err)
        self.git(repo, "add", "-A")
        self.git(repo, "commit", "-q", "-m", "adopt trellium")

        check_code, payload = self.check_payload(app)

        self.assertEqual(check_code, 0, payload["findings"])
        self.assertEqual(self.findings_with(payload, "CORE_STORAGE_UNCOMMITTED"), [])
        self.assertEqual(self.findings_with(payload, "CORE_STORAGE_IGNORED"), [])

    def test_non_git_target_reports_unverified_core(self) -> None:
        # Prereg §9 #8: silence on an adopted non-Git target is the same
        # false-health pattern; check must say durability was not verified,
        # as a warning (exit 0) so non-Git adoption stays usable.
        target = self.root / "plain"
        target.mkdir()
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, 0, payload["findings"])
        unverified = self.findings_with(payload, "CORE_STORAGE_UNVERIFIED")
        self.assertTrue(unverified, payload["findings"])
        self.assertEqual(unverified[0]["severity"], "warning")


class PrivateStorageModeTest(VaultCheckMixin, TargetTestCase):
    """TASK-0019 M0 contract and red tests (prereg:
    docs/superpowers/plans/2026-09-28-private-storage-mode-plan.md sections 9
    and 12-M0).

    P0 freezes the 2026.09.9 verdict on the A0 ablation (local policy plus a
    hand-maintained exclude over the whole core) to prove a docs-only private
    mode is unusable. P1 red tests follow the TASK-0013 M0 convention: the
    frozen v2/privacy contract is committed with expectedFailure markers and
    stays red until M1/M2 turn each test green and remove its marker in the
    same change. The two Kill Gates (ignored-AGENTS discovery in fresh agent
    sessions; forced-add visibility through read-only Git queries) are
    real-agent/runtime probes recorded in the task file, not unit tests.
    """

    PRIVATE_BASE_PATTERNS = (
        "/AGENTS.md",
        "/vault/",
        "/skills/agent-task/",
        "/.agent-init-backup/",
    )

    def adopted_repo(self, name: str = "project", *adopt_extra: str) -> Path:
        target = self.root / name
        target.mkdir()
        (target / "README.md").write_text("# Demo\n", encoding="utf-8")
        self.init_git_repo(target)
        self.git(target, "add", "README.md")
        self.git(target, "commit", "-q", "-m", "init")
        code, _, err = self.adopt(target, *adopt_extra)
        self.assertEqual(code, 0, err)
        return target

    def stamp_extra_patterns(self, target: Path, prefix: str = "") -> tuple[str, ...]:
        """Exact anchored patterns for stamp-managed paths outside the base namespaces."""
        stamp = self.read_stamp(target)
        patterns = []
        for relative in sorted(stamp.get("files", {})):
            if relative == "AGENTS.md" or relative.startswith(("vault/", "skills/agent-task/")):
                continue
            patterns.append(f"/{prefix}{relative}")
        return tuple(patterns)

    def private_repo(self, name: str = "private-project", *adopt_extra: str) -> Path:
        """Adopted repo as the Agent-native private workflow would leave it."""
        target = self.adopted_repo(name, *adopt_extra)
        self.write_index_policy(target, private_policy())
        self.write_private_exclude(target, extra_patterns=self.stamp_extra_patterns(target))
        return target

    def check_payload(self, target: Path) -> tuple[int, dict]:
        code, out, err = self.run_agent_init("check", str(target), "--format", "json")
        return code, json.loads(out)

    def status_payload(self, target: Path) -> tuple[int, dict]:
        code, out, err = self.run_agent_init("status", str(target), "--format", "json")
        return code, json.loads(out)

    def private_git_fingerprint(self, target: Path) -> tuple:
        """Write-proof snapshot: worktree files, index stages, HEAD, exclude bytes.

        `.git/` internals are excluded from the file snapshot because git
        opportunistically refreshes index stat-cache metadata; logical index
        state is covered by `git ls-files -s` and `git status --porcelain`.
        """
        files = {
            relative: content
            for relative, content in self.snapshot(target).items()
            if not relative.startswith(".git/")
        }
        return (
            files,
            self.git(target, "status", "--porcelain").stdout,
            self.git(target, "ls-files", "-s").stdout,
            self.git(target, "rev-parse", "HEAD").stdout,
            self.git_path(target, "info/exclude").read_bytes(),
        )

    @staticmethod
    def findings_with(payload: dict, code: str) -> list[dict]:
        return [finding for finding in payload["findings"] if finding["code"] == code]

    @staticmethod
    def reported_paths(findings: list[dict]) -> str:
        return " ".join(str(finding.get("path", "")) for finding in findings)

    def git_path(self, target: Path, argument: str) -> Path:
        """Resolve `git rev-parse --git-path` without assuming .git is a dir."""
        result = self.git(target, "rev-parse", "--git-path", argument)
        self.assertEqual(result.returncode, 0, result.stderr)
        value = Path(result.stdout.decode("utf-8").strip())
        return value if value.is_absolute() else (target / value)

    def write_index_policy(self, target: Path, policy: str) -> None:
        """Replace the adopted policy block the way the Agent workflow does."""
        index = target / "vault/index.md"
        text = index.read_text(encoding="utf-8")
        updated, count = re.subn(
            r"<!-- trellium-policy\n.*?\n-->", policy, text, count=1, flags=re.S
        )
        self.assertEqual(count, 1, "adopted vault/index.md must hold one policy block")
        index.write_text(updated, encoding="utf-8")

    def private_block_lines(
        self,
        *,
        prefix: str = "",
        extra_patterns: tuple[str, ...] = (),
        raw_patterns: tuple[str, ...] = (),
    ) -> list[str]:
        """Canonical block lines: identity, scoped anchored patterns, raw extras."""
        identity = prefix if prefix else "."
        scoped = [
            f"/{prefix}{pattern}" if prefix else pattern
            for pattern in (*self.PRIVATE_BASE_PATTERNS, *extra_patterns)
        ]
        return [
            f"# trellium-private:start {identity}",
            *scoped,
            *raw_patterns,
            f"# trellium-private:end {identity}",
        ]

    def write_private_exclude(
        self,
        target: Path,
        *,
        prefix: str = "",
        extra_patterns: tuple[str, ...] = (),
        raw_patterns: tuple[str, ...] = (),
    ) -> Path:
        """Append the canonical trellium-private block frozen by M0.

        Identity is the Git-root-relative target ("." for a repo-root
        target); patterns are anchored and Git-root-relative, carrying the
        target prefix for monorepo children. Only the approved managed scope
        is ever written: AGENTS.md, vault/, skills/agent-task/, the backup
        directory, plus exact extra managed paths. `raw_patterns` exists for
        negative fixtures that must exercise out-of-scope lines.
        """
        exclude = self.git_path(target, "info/exclude")
        with exclude.open("a", encoding="utf-8") as handle:
            handle.write(
                "\n".join(
                    self.private_block_lines(
                        prefix=prefix,
                        extra_patterns=extra_patterns,
                        raw_patterns=raw_patterns,
                    )
                )
                + "\n"
            )
        return exclude

    # ------------------------------------------------------------------ M0
    # Preregistered ablations and golden freezes (green against 2026.09.9).

    def test_p0_local_with_core_hand_ignored_stays_unhealthy(self) -> None:
        # P0 (prereg section 9): local policy + the same .git/info/exclude
        # carrier a private mode would use. The current checker must refuse
        # to call this healthy: every ignored core path is CORE_STORAGE_IGNORED
        # and the broad vault/ rule overreaches onto durable namespaces.
        target = self.adopted_repo()
        self.write_index_policy(target, local_policy())
        exclude = self.write_private_exclude(target)

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        self.assertEqual(payload["summary"]["warnings"], 0)
        ignored = self.reported_paths(self.findings_with(payload, "CORE_STORAGE_IGNORED"))
        for core in ("AGENTS.md", "vault/index.md", agent_init.STAMP_RELATIVE, "skills/agent-task/SKILL.md"):
            self.assertIn(core, ignored)
        overreach = self.reported_paths(self.findings_with(payload, "LOCAL_BOUNDARY_OVERREACH"))
        self.assertIn("vault/decisions/D-0000-sentinel.md", overreach)
        self.assertIn("vault/details/sentinel.md", overreach)

        # Weakening the rules does not reach health either: the uncovered
        # remainder flips to CORE_STORAGE_UNCOMMITTED because nothing that is
        # not ignored ever reaches HEAD.
        kept = [
            line
            for line in exclude.read_text(encoding="utf-8").splitlines(keepends=True)
            if "/AGENTS.md" not in line and "/skills/" not in line
        ]
        exclude.write_text("".join(kept), encoding="utf-8")

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        uncommitted = self.reported_paths(self.findings_with(payload, "CORE_STORAGE_UNCOMMITTED"))
        self.assertIn("AGENTS.md", uncommitted)
        self.assertIn("skills/agent-task/SKILL.md", uncommitted)

    def test_tracked_and_local_goldens_stay_clean(self) -> None:
        # M0 golden freeze: canonical tracked and local adoptions are 0/0.
        # M1/M2 must not drift these outputs; only private policies may gain
        # private-mode findings.
        tracked = self.adopted_repo(name="tracked-golden")
        self.git(tracked, "add", "-A")
        self.git(tracked, "commit", "-q", "-m", "adopt trellium")
        check_code, payload = self.check_payload(tracked)
        self.assertEqual(check_code, 0, payload["findings"])
        self.assertEqual(payload["findings"], [])

        local = self.adopted_repo(name="local-golden")
        self.write_index_policy(local, local_policy())
        tasks_gitignore = local / "vault/tasks/.gitignore"
        tasks_gitignore.write_text("TASK-*.md\n*-review.md\narchive/\n", encoding="utf-8")
        self.git(local, "add", "-A")
        self.git(local, "commit", "-q", "-m", "adopt trellium as local")
        check_code, payload = self.check_payload(local)
        self.assertEqual(check_code, 0, payload["findings"])
        self.assertEqual(payload["findings"], [])

    def test_check_and_status_goldens_healthy(self) -> None:
        # M0 golden freeze (review round 1): the healthy tracked adoption
        # freezes `status` alongside `check`; M1/M2 must not drift either.
        tracked = self.adopted_repo(name="tracked-golden")
        self.git(tracked, "add", "-A")
        self.git(tracked, "commit", "-q", "-m", "adopt trellium")

        check_code, payload = self.check_payload(tracked)
        self.assertEqual(check_code, 0, payload["findings"])
        self.assertEqual(payload["findings"], [])

        status_code, status_payload = self.status_payload(tracked)
        self.assertEqual(status_code, 0, status_payload["findings"])
        self.assertEqual(status_payload["findings"], [])
        self.assertEqual(
            status_payload["summary"],
            {
                "active": 0,
                "blocked": 0,
                "closed": 0,
                "draft": 0,
                "ready_for_review": 0,
                "unresolved": 0,
            },
        )
        self.assertEqual(
            status_payload["tasks"],
            {
                "active": [],
                "blocked": [],
                "draft": [],
                "ready_for_review": [],
                "unresolved": [],
            },
        )

    def test_check_and_status_goldens_single_storage_error(self) -> None:
        # One deterministic violation: a closed (accepted) task that never
        # reached Git under tracked policy. check reports exactly one error;
        # status carries the same single finding and must NOT turn the
        # storage failure into an unresolved lifecycle bucket.
        tracked = self.adopted_repo(name="tracked-golden-error")
        self.git(tracked, "add", "-A")
        self.git(tracked, "commit", "-q", "-m", "adopt trellium")
        (tracked / "vault/tasks/TASK-0002-done.md").write_text(
            "# TASK-0002 - Done\n\n"
            + state_block(valid_state(task_id="TASK-0002", lifecycle="accepted"))
            + "\n",
            encoding="utf-8",
        )

        check_code, payload = self.check_payload(tracked)
        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        self.assertEqual([item["code"] for item in payload["findings"]], ["TASK_STORAGE_MISMATCH"])
        self.assertEqual(payload["summary"], {"errors": 1, "warnings": 0})

        status_code, status_payload = self.status_payload(tracked)
        self.assertEqual(status_code, agent_init.CHECK_ERROR_EXIT)
        self.assertEqual([item["code"] for item in status_payload["findings"]], ["TASK_STORAGE_MISMATCH"])
        self.assertEqual(status_payload["tasks"]["unresolved"], [])
        self.assertEqual(status_payload["summary"]["closed"], 1)
        self.assertEqual(status_payload["summary"]["unresolved"], 0)

    def test_policy_v2_malformed_variants_stay_rejected(self) -> None:
        # M1 guard (green today, must stay green): v2 only parses with an
        # exact storage_mode and no legacy/unknown fields.
        cases = {
            "missing-mode": '{"schema_version": 2}',
            "legacy-and-v2-fields": '{"schema_version": 2, "storage_mode": "local", "task_storage": "tracked"}',
            "unknown-mode": '{"schema_version": 2, "storage_mode": "hybrid"}',
            "string-schema": '{"schema_version": "2", "storage_mode": "local"}',
            "unknown-field": '{"schema_version": 2, "storage_mode": "local", "extra": true}',
        }
        for name, payload_text in cases.items():
            with self.subTest(case=name):
                target = self.make_project(policy=policy_block(text=payload_text))
                code, out, err = self.check(target)
                self.assertEqual(code, agent_init.CHECK_ERROR_EXIT, out)
                self.assertIn("POLICY_INVALID", out)

    def test_policy_v1_rejects_private_task_storage(self) -> None:
        # M1 guard: v1 keeps exactly its two legacy values; private never
        # becomes a task_storage value.
        target = self.make_project(
            policy=policy_block({"schema_version": 1, "task_storage": "private"})
        )
        code, out, err = self.check(target)
        self.assertEqual(code, agent_init.CHECK_ERROR_EXIT, out)
        self.assertIn("POLICY_INVALID", out)

    # -------------------------------------------------------------- P1 red
    # Policy v2 normalization contract (turns green in M1).

    def test_policy_v2_tracked_mode_drives_tracked_semantics(self) -> None:
        # Green since M1: schema v2 normalization feeds tracked semantics.
        target = self.adopted_repo(name="v2-tracked")
        (target / "vault/runtime.md").write_text(
            build_runtime(), encoding="utf-8"
        )
        (target / "vault/tasks/TASK-0001-entry.md").write_text(
            "# TASK-0001 - Entry\n\n" + state_block(valid_state(lifecycle="active")) + "\n",
            encoding="utf-8",
        )
        self.write_index_policy(target, v2_policy("tracked"))

        check_code, payload = self.check_payload(target)

        self.assertNotIn("POLICY_INVALID", self.codes(payload))
        pending = self.findings_with(payload, "TASK_STORAGE_PENDING")
        self.assertTrue(pending, payload["findings"])
        self.assertEqual([item["task_id"] for item in pending], ["TASK-0001"])

    def test_policy_v2_local_mode_drives_local_boundary_semantics(self) -> None:
        # Green since M1: schema v2 normalization feeds local boundary semantics.
        target = self.make_project(policy=v2_policy("local"))
        self.init_git_repo(target)

        check_code, payload = self.check_payload(target)

        self.assertNotIn("POLICY_INVALID", self.codes(payload))
        self.assertEqual(
            [item["code"] for item in payload["findings"] if item["code"] == "LOCAL_BOUNDARY_UNCONFIGURED"],
            ["LOCAL_BOUNDARY_UNCONFIGURED"],
        )

    def test_policy_v2_private_mode_is_recognized(self) -> None:
        target = self.make_project(policy=v2_policy("private"))

        check_code, payload = self.check_payload(target)

        self.assertNotIn("POLICY_INVALID", self.codes(payload))
        unverified = self.findings_with(payload, "PRIVATE_STORAGE_UNVERIFIED")
        self.assertTrue(unverified, payload["findings"])
        self.assertTrue(all(item["severity"] == "warning" for item in unverified), payload["findings"])

    # -------------------------------------------------------------- P1 red
    # Private reverse privacy Gate contract (turns green in M2).

    def test_private_clean_fixture_is_healthy(self) -> None:
        # Go Gate (prereg section 9): clean private fixture reaches 0/0 with
        # all managed material untracked, staged-free, and ignored.
        target = self.private_repo()
        tracked = self.git(target, "ls-files", "--cached", "--", "AGENTS.md", "vault", "skills/agent-task")
        self.assertEqual(tracked.stdout, b"")

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, 0, payload["findings"])
        self.assertEqual(payload["summary"], {"errors": 0, "warnings": 0})
        self.assertEqual(payload["findings"], [])

    def test_private_forced_add_is_reported(self) -> None:
        # Kill Gate 2 contract: git add -f of a managed path must fail closed
        # through read-only index queries, with no hooks and no index writes.
        target = self.private_repo()
        self.git(target, "add", "-f", "vault/index.md")

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        tracked_findings = self.findings_with(payload, "PRIVATE_STORAGE_TRACKED")
        self.assertTrue(tracked_findings, payload["findings"])
        self.assertIn("vault/index.md", self.reported_paths(tracked_findings))

    def test_private_committed_head_is_reported(self) -> None:
        # A managed path that reached HEAD stays a privacy error; private
        # never scans history, but the current tree must not pass.
        target = self.private_repo()
        self.git(target, "add", "-f", "AGENTS.md")
        self.git(target, "commit", "-q", "-m", "leak")

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        tracked_findings = self.findings_with(payload, "PRIVATE_STORAGE_TRACKED")
        self.assertTrue(tracked_findings, payload["findings"])
        self.assertIn("AGENTS.md", self.reported_paths(tracked_findings))

    def test_private_missing_exclude_block_is_unconfigured(self) -> None:
        target = self.adopted_repo()
        self.write_index_policy(target, private_policy())

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        unconfigured = self.findings_with(payload, "PRIVATE_STORAGE_UNCONFIGURED")
        self.assertTrue(unconfigured, payload["findings"])
        self.assertTrue(all(item["severity"] == "error" for item in unconfigured))

    def test_private_overbroad_exclude_is_overreach(self) -> None:
        target = self.adopted_repo()
        self.write_index_policy(target, private_policy())
        self.write_private_exclude(target, extra_patterns=("/docs/",))

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        overreach = self.findings_with(payload, "PRIVATE_STORAGE_OVERREACH")
        self.assertTrue(overreach, payload["findings"])
        self.assertIn("/docs/", " ".join(item["message"] for item in overreach))

    def test_private_git_failure_is_unverified(self) -> None:
        target = self.private_repo()
        real_git_run = agent_init.git_run

        def failing_ls_files(cwd: Path, arguments: list[str], input_bytes: bytes | None = None):
            if arguments and arguments[0] == "ls-files":
                return subprocess.CompletedProcess(["git", *arguments], 128, b"", b"failure")
            return real_git_run(cwd, arguments, input_bytes)

        with patch.object(agent_init, "git_run", side_effect=failing_ls_files):
            check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        unverified = self.findings_with(payload, "PRIVATE_STORAGE_UNVERIFIED")
        self.assertTrue(unverified, payload["findings"])
        self.assertTrue(all(item["severity"] == "error" for item in unverified))

    def test_private_non_git_target_warns(self) -> None:
        # Non-Git targets have no Git upload surface but no mechanically
        # verifiable privacy boundary either: warning, never silence.
        target = self.root / "plain-private"
        target.mkdir()
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        self.write_index_policy(target, private_policy())

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, 0, payload["findings"])
        unverified = self.findings_with(payload, "PRIVATE_STORAGE_UNVERIFIED")
        self.assertTrue(unverified, payload["findings"])
        self.assertTrue(all(item["severity"] == "warning" for item in unverified), payload["findings"])

    def test_private_task_lifecycle_follows_local_semantics(self) -> None:
        target = self.private_repo()
        (target / "vault/runtime.md").write_text(
            build_runtime(), encoding="utf-8"
        )
        (target / "vault/tasks/TASK-0001-entry.md").write_text(
            "# TASK-0001 - Entry\n\n" + state_block(valid_state(lifecycle="draft")) + "\n",
            encoding="utf-8",
        )

        check_code, payload = self.check_payload(target)
        self.assertEqual(payload["summary"]["errors"], 0, payload["findings"])
        self.assertEqual(self.findings_with(payload, "TASK_STORAGE_MISMATCH"), [])

        self.git(target, "add", "-f", "vault/tasks/TASK-0001-entry.md")
        check_code, payload = self.check_payload(target)
        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        self.assertTrue(self.findings_with(payload, "TASK_STORAGE_MISMATCH"), payload["findings"])

    def test_private_monorepo_subdir_fixture_is_healthy(self) -> None:
        repo = self.root / "monorepo"
        app = repo / "packages" / "app"
        app.mkdir(parents=True)
        (app / "README.md").write_text("# App\n", encoding="utf-8")
        self.init_git_repo(repo)
        self.git(repo, "add", "packages/app/README.md")
        self.git(repo, "commit", "-q", "-m", "init")
        code, _, err = self.adopt(app)
        self.assertEqual(code, 0, err)
        self.write_index_policy(app, private_policy())
        self.write_private_exclude(app, prefix="packages/app")

        tracked = self.git(repo, "ls-files", "--cached", "--", "packages/app/AGENTS.md", "packages/app/vault")
        self.assertEqual(tracked.stdout, b"")
        check_code, payload = self.check_payload(app)

        self.assertEqual(check_code, 0, payload["findings"])
        self.assertEqual(payload["summary"], {"errors": 0, "warnings": 0})

    # ---------------------------------------------------- P1 red (round 2)
    # Marker-block integrity: the canonical block is only valid when it is
    # unique, well-formed, uncrossed, and named for this exact target.

    def assert_unconfigured(self, payload: dict) -> None:
        unconfigured = self.findings_with(payload, "PRIVATE_STORAGE_UNCONFIGURED")
        self.assertTrue(unconfigured, payload["findings"])
        self.assertTrue(all(item["severity"] == "error" for item in unconfigured))

    def test_private_duplicate_marker_blocks_are_unconfigured(self) -> None:
        target = self.private_repo()
        self.write_private_exclude(target)  # second complete block, same identity

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        self.assert_unconfigured(payload)

    def test_private_unterminated_marker_block_is_unconfigured(self) -> None:
        target = self.adopted_repo()
        self.write_index_policy(target, private_policy())
        exclude = self.git_path(target, "info/exclude")
        with exclude.open("a", encoding="utf-8") as handle:
            handle.write("# trellium-private:start .\n/AGENTS.md\n/vault/\n")

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        self.assert_unconfigured(payload)

    def test_private_crossed_marker_blocks_are_unconfigured(self) -> None:
        target = self.adopted_repo()
        self.write_index_policy(target, private_policy())
        exclude = self.git_path(target, "info/exclude")
        with exclude.open("a", encoding="utf-8") as handle:
            handle.write(
                "# trellium-private:start .\n"
                "/AGENTS.md\n"
                "# trellium-private:start other\n"
                "/vault/\n"
                "# trellium-private:end .\n"
                "/skills/agent-task/\n"
                "# trellium-private:end other\n"
            )

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        self.assert_unconfigured(payload)

    def test_private_marker_identity_mismatch_is_unconfigured(self) -> None:
        target = self.adopted_repo()
        self.write_index_policy(target, private_policy())
        exclude = self.git_path(target, "info/exclude")
        # A complete, well-formed block that names a different target is not
        # this target's boundary.
        exclude.write_text("\n".join(self.private_block_lines(prefix="packages/other")) + "\n", encoding="utf-8")

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        self.assert_unconfigured(payload)

    def test_private_non_anchored_pattern_is_overreach(self) -> None:
        # "vault/" without a leading slash reaches any nested directory of
        # the same name; the frozen contract requires anchored patterns.
        target = self.adopted_repo()
        self.write_index_policy(target, private_policy())
        exclude = self.write_private_exclude(target)
        exclude.write_text(
            exclude.read_text(encoding="utf-8").replace("/vault/", "vault/"),
            encoding="utf-8",
        )

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        self.assertTrue(self.findings_with(payload, "PRIVATE_STORAGE_OVERREACH"), payload["findings"])

    def test_private_out_of_target_pattern_is_overreach(self) -> None:
        # A monorepo child block may never reach into a sibling target's
        # namespace.
        repo = self.root / "monorepo-cross"
        app = repo / "packages" / "app"
        app.mkdir(parents=True)
        (app / "README.md").write_text("# App\n", encoding="utf-8")
        self.init_git_repo(repo)
        self.git(repo, "add", "packages/app/README.md")
        self.git(repo, "commit", "-q", "-m", "init")
        code, _, err = self.adopt(app)
        self.assertEqual(code, 0, err)
        self.write_index_policy(app, private_policy())
        self.write_private_exclude(
            app,
            prefix="packages/app",
            raw_patterns=("/packages/other/",),
        )

        check_code, payload = self.check_payload(app)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        self.assertTrue(self.findings_with(payload, "PRIVATE_STORAGE_OVERREACH"), payload["findings"])

    def test_private_tracked_carrier_fails_closed_without_writes(self) -> None:
        # A tracked AGENTS.md is a hard private conflict: the checker must
        # report it (never silently merge semantics) and detection itself
        # must leave index, HEAD, worktree, and the exclude file untouched.
        target = self.root / "tracked-carrier"
        target.mkdir()
        (target / "README.md").write_text("# Demo\n", encoding="utf-8")
        (target / "AGENTS.md").write_text("# Custom entry\n", encoding="utf-8")
        self.init_git_repo(target)
        self.git(target, "add", "README.md", "AGENTS.md")
        self.git(target, "commit", "-q", "-m", "init")
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        self.write_index_policy(target, private_policy())
        self.write_private_exclude(target)

        before = self.private_git_fingerprint(target)
        check_code, payload = self.check_payload(target)
        after = self.private_git_fingerprint(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        tracked_findings = self.findings_with(payload, "PRIVATE_STORAGE_TRACKED")
        self.assertTrue(tracked_findings, payload["findings"])
        self.assertIn("AGENTS.md", self.reported_paths(tracked_findings))
        self.assertEqual(before, after)

    @unittest.expectedFailure
    def test_private_preflight_rejects_tracked_agents_without_writes(self) -> None:
        # Plan §6.2 (1/3): the Agent-native preflight runs BEFORE adopt; a
        # tracked AGENTS.md must be rejected explicitly and leave the
        # pre-adopt worktree, index, HEAD, and exclude file byte-identical.
        # The probe is a read-only library call; no storage CLI parameter.
        target = self.root / "preflight-agents"
        target.mkdir()
        (target / "README.md").write_text("# Demo\n", encoding="utf-8")
        (target / "AGENTS.md").write_text("# Custom entry\n", encoding="utf-8")
        self.init_git_repo(target)
        self.git(target, "add", "README.md", "AGENTS.md")
        self.git(target, "commit", "-q", "-m", "init")

        before = self.private_git_fingerprint(target)
        with self.assertRaises(agent_init.AdoptionError) as rejected:
            agent_init.private_preflight(target)
        self.assertIn("AGENTS.md", str(rejected.exception))
        self.assertEqual(before, self.private_git_fingerprint(target))

    @unittest.expectedFailure
    def test_private_preflight_rejects_tracked_profile_carrier_without_writes(self) -> None:
        # Plan §6.2 (2/3): with a profile selected, its tracked engineering
        # document is a carrier on its own - isolated here from AGENTS.md so
        # the profile rejection cannot hide behind the entry-carrier case,
        # and fingerprinted so mutation during the rejection fails.
        target = self.root / "preflight-profile"
        target.mkdir()
        (target / "README.md").write_text("# Demo\n", encoding="utf-8")
        carrier = target / "docs/engineering/code-comments.md"
        carrier.parent.mkdir(parents=True, exist_ok=True)
        carrier.write_text("# Rules\n", encoding="utf-8")
        self.init_git_repo(target)
        self.git(target, "add", "README.md", "docs/engineering/code-comments.md")
        self.git(target, "commit", "-q", "-m", "init")

        before = self.private_git_fingerprint(target)
        with self.assertRaises(agent_init.AdoptionError) as rejected:
            agent_init.private_preflight(target, profiles=("go-backend",))
        self.assertIn("docs/engineering/code-comments.md", str(rejected.exception))
        self.assertEqual(before, self.private_git_fingerprint(target))

    @unittest.expectedFailure
    def test_private_preflight_allows_untracked_carrier_without_writes(self) -> None:
        # Plan §6.2 (3/3): untracked carriers are adoptable for private mode;
        # the probe itself must stay read-only there too.
        target = self.root / "preflight-clean"
        target.mkdir()
        (target / "README.md").write_text("# Demo\n", encoding="utf-8")
        (target / "AGENTS.md").write_text("# Custom entry\n", encoding="utf-8")
        self.init_git_repo(target)
        self.git(target, "add", "README.md")
        self.git(target, "commit", "-q", "-m", "init")

        before = self.private_git_fingerprint(target)
        self.assertEqual(agent_init.private_preflight(target), [])
        self.assertEqual(before, self.private_git_fingerprint(target))

    def test_private_profile_managed_paths_require_exact_ignore(self) -> None:
        # Stamp-managed paths outside the base namespaces (profile documents)
        # must be covered exactly before a private adoption counts healthy.
        target = self.adopted_repo("profile-private", "--profile", "go-backend=services/api")
        self.write_index_policy(target, private_policy())
        extra = self.stamp_extra_patterns(target)
        self.assertEqual(
            extra,
            ("/docs/engineering/code-comments.md", "/docs/engineering/profiles/go-backend.md"),
        )
        self.write_private_exclude(target)  # base namespaces only

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        self.assert_unconfigured(payload)
        reported = self.reported_paths(payload["findings"]) + " " + " ".join(
            item["message"] for item in payload["findings"]
        )
        self.assertIn("docs/engineering/code-comments.md", reported)
        self.assertIn("docs/engineering/profiles/go-backend.md", reported)

        # The same fixture with the exact stamp paths covered reaches health.
        exclude = self.git_path(target, "info/exclude")
        exclude.write_text("\n".join(self.private_block_lines(extra_patterns=extra)) + "\n", encoding="utf-8")

        check_code, payload = self.check_payload(target)
        self.assertEqual(check_code, 0, payload["findings"])
        self.assertEqual(payload["summary"], {"errors": 0, "warnings": 0})

    def test_private_profile_forced_add_is_reported(self) -> None:
        # Profile paths are inside the managed scope: forcing one into the
        # index is the same privacy violation as forcing vault/index.md.
        target = self.private_repo("profile-forced", "--profile", "go-backend=services/api")
        self.git(target, "add", "-f", "docs/engineering/code-comments.md")

        check_code, payload = self.check_payload(target)

        self.assertEqual(check_code, agent_init.CHECK_ERROR_EXIT)
        tracked_findings = self.findings_with(payload, "PRIVATE_STORAGE_TRACKED")
        self.assertTrue(tracked_findings, payload["findings"])
        self.assertIn("docs/engineering/code-comments.md", self.reported_paths(tracked_findings))


if __name__ == "__main__":
    unittest.main()
