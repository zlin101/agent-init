import importlib.util
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
import history_store as h
from scripts.test_trellium import ProjectIdentityTest, agent_init

def main():
    print('ENV:', platform.platform(), platform.python_version(), 'uid', os.getuid(), flush=True)
    print('GIT:', subprocess.check_output(['git', '--version'], text=True).strip(), flush=True)
    if sys.platform == 'linux':
        print('FS:', subprocess.check_output(['stat', '-f', '-c', '%T', '.'], text=True).strip(), flush=True)
    suite = unittest.defaultTestLoader.loadTestsFromNames([
        'scripts.test_history_store', 'scripts.test_trellium.ProjectIdentityTest'
    ])
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    assert result.wasSuccessful()

    with tempfile.TemporaryDirectory(prefix='task29-ancestor-') as temporary:
        base = Path(temporary).resolve()
        store = h.Store(base / '.trellium' / 'history')
        artifact = h.Artifact('TASK-0029', b'evidence', 'vault/tasks/TASK-0029.md')
        project = str(uuid.uuid4())
        real_sync = h._sync_dir
        failed = []
        def failing(path):
            if path == base and not failed:
                failed.append(path)
                raise OSError('injected fsync failure persisting .trellium link')
            real_sync(path)
        try:
            with patch.object(h, '_sync_dir', side_effect=failing):
                store.put(project, artifact)
        except OSError:
            pass
        assert failed and (base / '.trellium').is_dir()
        events = []
        def recording(path):
            events.append(path)
            real_sync(path)
        with patch.object(h, '_sync_dir', side_effect=recording):
            digest = store.put(project, artifact)
        assert base in events
        print('F29-001: retry success =', store.get(project, artifact.artifact_id, digest)[digest] == artifact.content,
              '; failed parent fsync retried =', base in events, flush=True)

    fixture = ProjectIdentityTest('test_git_unavailable_fails_closed')
    fixture.setUp()
    try:
        target = fixture.adopt_local()
        original = str(uuid.uuid4())
        path = target / 'vault/project-id'
        path.write_text(original + '\n')
        fixture.init_git_repo(target)
        fixture.git(target, 'add', '-A')
        fixture.git(target, 'commit', '-qm', 'bind identity')
        path.unlink()
        ref = subprocess.check_output(['git', '-C', str(target), 'symbolic-ref', 'HEAD'], text=True).strip()
        (target / '.git' / ref).write_text('corrupt ref\n')
        probe = subprocess.run(['git', '-C', str(target), 'rev-parse', '--verify', 'HEAD'], capture_output=True, text=True)
        print('F29-002: corrupt HEAD stderr =', probe.stderr.strip(), flush=True)
        try:
            replacement = fixture.ensure(target, authorize_create=True)
        except agent_init.AdoptionError:
            print('F29-002 corrupt-ref: replacement created = False ; identity exists =', path.exists(), flush=True)
            assert not path.exists()
        else:
            raise AssertionError('corrupt ref unexpectedly allowed replacement')
    finally:
        fixture.tearDown()

    fixture = ProjectIdentityTest('test_git_unavailable_fails_closed')
    fixture.setUp()
    try:
        target = fixture.adopt_local()
        original = str(uuid.uuid4())
        path = target / 'vault/project-id'
        path.write_text(original + '\n')
        fixture.init_git_repo(target)
        fixture.git(target, 'add', '-A')
        fixture.git(target, 'commit', '-qm', 'bind identity')
        path.unlink()
        head_path = target / '.git/HEAD'
        original_head = head_path.read_bytes()
        head_path.write_text('corrupt head\n')
        probe = subprocess.run(['git', '-C', str(target), 'rev-parse', '--verify', 'HEAD'], capture_output=True, text=True)
        print('F29-002 corrupt-HEAD-file: stderr =', probe.stderr.strip(), flush=True)
        try:
            replacement = fixture.ensure(target, authorize_create=True)
        except agent_init.AdoptionError:
            print('F29-002 corrupt-HEAD-file: replacement created = False ; identity exists =', path.exists(), flush=True)
        else:
            print('F29-002 corrupt-HEAD-file: replacement created =', replacement['created'],
                  '; differs from committed identity =', replacement['identity'] != original,
                  '; registered =', replacement['registered'], flush=True)
        assert not path.exists(), 'normal corrupt HEAD must leave identity absent'
        real_lstat = os.lstat
        lookups = []
        def unreadable_metadata(path_arg, *args, **kwargs):
            if Path(path_arg) == target / '.git':
                lookups.append(str(path_arg))
                raise PermissionError('injected unreadable Git metadata lookup')
            return real_lstat(path_arg, *args, **kwargs)
        stamp_path = target / agent_init.STAMP_RELATIVE
        before = stamp_path.read_bytes()
        with patch.object(os, 'lstat', side_effect=unreadable_metadata):
            detected = agent_init._has_git_metadata(target)
            try:
                replacement = fixture.ensure(target, authorize_create=True)
            except agent_init.AdoptionError:
                print('F29-002 unreadable-metadata: refused ; identity exists =', path.exists(), flush=True)
            else:
                print('F29-002 unreadable-metadata: lookup error observed =', bool(lookups),
                      '; detector =', detected, '; replacement created =', replacement['created'],
                      '; differs from committed identity =', replacement['identity'] != original,
                      '; registered =', replacement['registered'],
                      '; stamp changed =', stamp_path.read_bytes() != before, flush=True)
        head_path.write_bytes(original_head)
        recovered = subprocess.check_output(['git', '-C', str(target), 'show', 'HEAD:vault/project-id'], text=True).strip()
        assert recovered == original
        print('F29-002 corrupt-HEAD-file: committed identity recoverable after restoring HEAD = True', flush=True)
    finally:
        fixture.tearDown()

    for language in ('trellium-zh', 'trellium'):
        module_path = ROOT / 'skills' / language / 'assets/history_store.py'
        name = 'unregistered_' + language.replace('-', '_')
        spec = importlib.util.spec_from_file_location(name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert name not in sys.modules
        with tempfile.TemporaryDirectory(prefix='task29-package-') as temporary:
            base = Path(temporary)
            clone = base / 'clone'
            sources = [clone / 'vault/tasks/TASK-0029.md', clone / 'vault/tasks/TASK-0029-review.md']
            sources[0].parent.mkdir(parents=True)
            payloads = [b'Terminal TASK evidence\n', b'Terminal review ledger evidence\n']
            ids = ['TASK-0029', 'TASK-0029-review']
            for source, payload in zip(sources, payloads):
                source.write_bytes(payload)
            store = module.Store(base / 'external-history')
            project = str(uuid.uuid4())
            store.put(project, module.Artifact(ids[0], payloads[0], sources[0].relative_to(clone).as_posix()))
            with patch.object(module, '_write_file', side_effect=OSError('injected second artifact write failure')):
                failed = module.retain_terminal(store, project, sources[1], clone, ids[1])
            assert not failed['retained'] and all(source.exists() for source in sources)
            retained = [module.retain_terminal(store, project, source, clone, identity)
                        for source, identity in zip(sources, ids)]
            assert all(record['retained'] for record in retained)
            shutil.rmtree(clone)
            for identity, payload, record in zip(ids, payloads, retained):
                assert store.get(project, identity, record['digest'])[record['digest']] == payload
            assert {record['source_relative_path'] for record in store.list(project)} == {
                'vault/tasks/TASK-0029.md', 'vault/tasks/TASK-0029-review.md'
            }
        print('DISTRIBUTED E2E:', language, 'PASS', flush=True)

if __name__ == '__main__':
    main()
