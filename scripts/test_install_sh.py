from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALL_SCRIPT = REPO_ROOT / "scripts" / "install.sh"


class InstallScriptTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_installer(self, *arguments: str, cwd: Path | None = None, home: Path | None = None) -> subprocess.CompletedProcess:
        environment = dict(os.environ)
        environment.pop("CODEX_HOME", None)
        if home is not None:
            environment["HOME"] = str(home)
        return subprocess.run(
            ["sh", str(INSTALL_SCRIPT), "--source", str(REPO_ROOT), *arguments],
            cwd=cwd or self.root,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_dir_install_en_default_and_zh(self) -> None:
        target = self.root / "skills"
        result = self.run_installer("--dir", str(target))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((target / "trellium" / "SKILL.md").is_file())
        self.assertFalse((target / "trellium-zh").exists())

        result = self.run_installer("--dir", str(target), "--lang", "zh")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((target / "trellium-zh" / "SKILL.md").is_file())

    def test_reinstall_replaces_in_place(self) -> None:
        target = self.root / "skills"
        self.run_installer("--dir", str(target))
        marker = target / "trellium" / "stale-file.txt"
        marker.write_text("stale\n", encoding="utf-8")

        result = self.run_installer("--dir", str(target))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists(), "reinstall must replace, not merge")

    def test_project_install_uses_local_claude_skills(self) -> None:
        project = self.root / "project"
        project.mkdir()

        result = self.run_installer("--project", cwd=project)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((project / ".claude" / "skills" / "trellium" / "SKILL.md").is_file())

    def test_agent_all_installs_codex_and_claude(self) -> None:
        home = self.root / "home"
        (home / ".codex").mkdir(parents=True)
        (home / ".claude").mkdir(parents=True)

        result = self.run_installer("--agent", "all", home=home)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((home / ".codex" / "skills" / "trellium" / "SKILL.md").is_file())
        self.assertTrue((home / ".claude" / "skills" / "trellium" / "SKILL.md").is_file())

    def test_invalid_language_is_rejected(self) -> None:
        result = self.run_installer("--dir", str(self.root / "skills"), "--lang", "xx")
        self.assertEqual(result.returncode, 1)
        self.assertIn("must be en or zh", result.stderr)

    def test_unknown_option_is_rejected(self) -> None:
        result = self.run_installer("--bogus")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown option", result.stderr)

    def test_network_install_without_version_fails_closed(self) -> None:
        # TASK-0024: network installs require an explicit --version tag;
        # latest-release resolution was removed, and the failure must happen
        # before any network access.
        result = subprocess.run(
            ["sh", str(INSTALL_SCRIPT)],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("--version", result.stderr)
        self.assertNotIn("http", result.stderr)


if __name__ == "__main__":
    unittest.main()
