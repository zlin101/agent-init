import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
BASE = Path('/private/tmp/trellium-reinstall-20261001')
PACKAGE = Path.home() / '.codex/skills/trellium-zh'
sys.path.insert(0, str(ROOT))
from scripts import test_trellium as tests


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


installed = load('installed_trellium', PACKAGE / 'assets/trellium.py')
history = load('installed_history', PACKAGE / 'assets/history_store.py')
tests.agent_init = installed


class InstalledE2E(tests.VaultCheckMixin):
    def project(self, name, mode):
        if mode == 'private':
            return tests.PrivateHistoryTest.private_project(self, name)
        target = (self.root / name).resolve()
        target.mkdir()
        (target / 'README.md').write_text('# Isolated compatibility fixture\n')
        self.init_git_repo(target)
        self.git(target, 'add', 'README.md')
        self.git(target, 'commit', '-qm', 'init')
        self.assertEqual(self.adopt(target)[0], 0)
        tests.ProjectIdentityTest.write_policy(self, target, tests.v2_policy(mode))
        if mode == 'local':
            (target / 'vault/tasks/.gitignore').write_text('TASK-*.md\narchive/\n')
        self.git(target, 'add', '-A')
        self.git(target, 'commit', '-qm', 'adoption')
        return target

    def test_new_three_modes(self):
        for mode in ('tracked', 'local', 'private'):
            with self.subTest(mode=mode):
                target = self.project(mode, mode)
                self.assertTrue((target / 'skills/trellium-work/SKILL.md').is_file())
                self.assertFalse((target / 'skills/agent-task/SKILL.md').exists())
                task = target / 'vault/tasks/TASK-0001.md'
                task.write_text('# TASK-0001\n' + tests.state_block(tests.valid_state('TASK-0001', 'accepted')))
                tracked = self.git(target, 'check-ignore', str(task)).returncode != 0
                self.assertEqual(tracked, mode == 'tracked')
                if mode == 'tracked':
                    self.git(target, 'add', '-A')
                    self.git(target, 'commit', '-qm', 'closed task')
                self.assertEqual(self.check_json(target)['summary'], {'errors': 0, 'warnings': 0})
                if mode == 'private':
                    self.assertEqual(self.git(target, 'ls-files').stdout, b'README.md\n')
                    self.assertEqual(self.git(target, 'status', '--porcelain').stdout, b'')

    def test_real_091_project_refusal_migration_and_custom_proposal(self):
        target = (self.root / 'actual-old-project').resolve()
        target.mkdir()
        (target / 'README.md').write_text('# Isolated legacy fixture\n')
        self.init_git_repo(target)
        self.git(target, 'add', 'README.md')
        self.git(target, 'commit', '-qm', 'init')
        old = subprocess.run(['python3', '-B', str(BASE / 'old-package/assets/trellium.py'),
                              'adopt', str(target)], capture_output=True, text=True)
        self.assertEqual(old.returncode, 0, old.stderr)
        self.assertEqual(self.read_stamp(target)['protocol_version'], '2026.09.1')
        legacy = target / installed.LEGACY_WORK_SKILL_RELATIVE
        custom = '\n## Project acceptance rule\nKeep the owner custom command.\n'
        legacy.write_text(legacy.read_text() + custom)
        runtime = target / 'vault/runtime.md'
        runtime.write_text(runtime.read_text() + '\nPreserve this project memory sentinel.\n')
        data_before = {relative: (target/relative).read_bytes()
                       for relative, role in installed.FILE_ROLES.items() if role == 'data'}
        self.git(target, 'add', '-A')
        self.git(target, 'commit', '-qm', 'actual old adoption')
        self.assertEqual(self.check_json(target)['summary']['errors'], 0)
        before = {k: v for k, v in self.snapshot(target).items() if not k.startswith('.git/')}
        for command in (('adopt', '--force'), ('upgrade', '--apply'), ('upgrade', '--complete')):
            code, _, err = self.run_agent_init(command[0], str(target), *command[1:])
            self.assertNotEqual(code, 0)
            self.assertIn('explicit work Skill migration required', err)
            self.assertEqual({k: v for k, v in self.snapshot(target).items() if not k.startswith('.git/')}, before)
        original = self.read_stamp(target)
        tests.WorkSkillRenameTest.migrate(self, target)
        migrated = self.read_stamp(target)
        self.assertEqual({k: v for k, v in original.items() if k != 'files'},
                         {k: v for k, v in migrated.items() if k != 'files'})
        remaining = dict(original['files'])
        remaining.pop(installed.LEGACY_WORK_SKILL_RELATIVE)
        self.assertEqual(remaining, {k: v for k, v in migrated['files'].items() if k != installed.WORK_SKILL_RELATIVE})
        current = target / installed.WORK_SKILL_RELATIVE
        self.assertIn(custom, current.read_text())
        self.git(target, 'add', '-A')
        self.git(target, 'commit', '-qm', 'explicit workflow migration')
        local = current.read_bytes()
        code, _, err = self.run_agent_init('upgrade', str(target), '--apply')
        self.assertEqual(code, installed.EXIT_CONFLICT, err)
        self.assertEqual(current.read_bytes(), local)
        self.assertEqual(data_before, {key: (target/key).read_bytes() for key in data_before})
        proposal = target / installed.proposal_relative(installed.read_protocol_version(), installed.WORK_SKILL_RELATIVE)
        self.assertTrue(proposal.is_file())
        self.assertIn('Keep the owner custom command.', proposal.read_text())
        self.assertFalse(legacy.exists())

    def write_stamp(self, target, stamp):
        tests.WorkSkillRenameTest.write_stamp(self, target, stamp)

    def test_installed_history_local_private_group_retry_clone_loss_recovery(self):
        command = next(value for value in re.findall(r'python3 -c "([^"]+)"', (PACKAGE/'SKILL.md').read_text())
                       if 'ensure_project_identity' in value)
        for mode in ('local', 'private'):
            with self.subTest(mode=mode):
                clone = self.project('history-'+mode, mode)
                created = subprocess.run(['python3', '-B', '-c', command, str(clone), '--create'],
                                         cwd=PACKAGE, capture_output=True, text=True)
                self.assertEqual(created.returncode, 0, created.stderr)
                identity = (clone / 'vault/project-id').read_text().strip()
                store = history.Store(self.root / ('external-history-'+mode))
                task = clone / 'vault/tasks/TASK-0002.md'
                ledger = clone / 'vault/tasks/TASK-0002-review.md'
                task.write_text('# TASK-0002\n'+tests.state_block(tests.valid_state('TASK-0002', 'accepted')))
                ledger.write_text('# Review evidence\nF001 fixed; isolated fixture.\n')
                contents = [task.read_bytes(), ledger.read_bytes()]
                first = history.retain_terminal(store, identity, task, clone, 'TASK-0002')
                with patch.object(store, 'put', side_effect=OSError('isolated disk-full injection')):
                    failed = history.retain_terminal(store, identity, ledger, clone, 'TASK-0002-review')
                self.assertTrue(first['retained'])
                self.assertFalse(failed['retained'])
                self.assertEqual([task.read_bytes(), ledger.read_bytes()], contents)
                retried = history.retain_terminal(store, identity, ledger, clone, 'TASK-0002-review')
                self.assertTrue(retried['retained'])
                if mode == 'local':
                    self.git(clone, 'add', '-A')
                    self.git(clone, 'commit', '-qm', 'history identity')
                self.assertEqual(self.check_json(clone)['summary'], {'errors': 0, 'warnings': 0})
                if mode == 'private':
                    self.assertEqual(self.git(clone, 'ls-files').stdout, b'README.md\n')
                    self.assertEqual(self.git(clone, 'status', '--porcelain').stdout, b'')
                shutil.rmtree(clone)  # Exclusively this TemporaryDirectory fixture.
                for artifact_id, result, content in [('TASK-0002', first, contents[0]),
                                                      ('TASK-0002-review', retried, contents[1])]:
                    self.assertEqual(store.get(identity, artifact_id, result['digest'])[result['digest']], content)
                restored = self.project('restored-'+mode, mode)
                with (restored / 'vault/project-id').open('x') as handle:
                    handle.write(identity+'\n')
                registered = subprocess.run(['python3', '-B', '-c', command, str(restored)],
                                            cwd=PACKAGE, capture_output=True, text=True)
                self.assertEqual(registered.returncode, 0, registered.stderr)
                self.assertIn("'created': False", registered.stdout)
                self.assertEqual((restored/'vault/project-id').read_text(), identity+'\n')
                if mode == 'local':
                    self.git(restored, 'add', '-A')
                    self.git(restored, 'commit', '-qm', 'explicit UUID recovery')
                self.assertEqual(self.check_json(restored)['summary'], {'errors': 0, 'warnings': 0})


if __name__ == '__main__':
    unittest.main(verbosity=2)
