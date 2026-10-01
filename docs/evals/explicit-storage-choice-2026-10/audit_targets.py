"""Independently verify frozen Skill evaluation targets and their Git boundaries."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def git(target, *arguments):
    return subprocess.run(['git', '-C', str(target), *arguments], capture_output=True, text=True)


def files(root):
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob('*') if path.is_file() and '.git' not in path.relative_to(root).parts}


def snapshot(target):
    return {'files': files(target), 'index': git(target, 'ls-files', '-s').stdout,
            'head': git(target, 'rev-parse', 'HEAD').stdout.strip(),
            'exclude': (target / '.git/info/exclude').read_text()}


def mode(target):
    text = (target / 'vault/index.md').read_text()
    block = text.split('<!-- trellium-policy\n', 1)[1].split('\n-->', 1)[0]
    return json.loads(block)['storage_mode']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=Path, default=Path('/private/tmp/trellium-storage-choice-20261001'))
    args = parser.parse_args()
    before = json.loads((args.base / 'before-targets.json').read_text())
    checks = {}
    for name in ('unspecified', 'missing-existing-policy', 'invalid-existing-policy', 'conflicting-existing-policy'):
        checks[name] = {'snapshot_unchanged': snapshot(args.base / 'targets' / name) == before[name]}

    for name, expected in (('explicit-private', 'private'), ('explicit-local', 'local'),
                           ('explicit-tracked', 'tracked'), ('valid-existing-private', 'private')):
        target = args.base / 'targets' / name
        tracked = set(git(target, 'ls-files').stdout.splitlines())
        stamp = json.loads((target / 'vault/.agent-init.json').read_text())
        result = subprocess.run(['python3', '-B', str(args.base / 'packages/trellium-zh/assets/trellium.py'),
                                 'check', str(target), '--format', 'json'], capture_output=True, text=True)
        payload = json.loads(result.stdout)
        checks[name] = {
            'policy_matches': mode(target) == expected,
            'checker_no_errors': result.returncode == 0 and payload['summary']['errors'] == 0,
            'business_readme_unchanged': files(target)['README.md'] == before[name]['files']['README.md'],
        }
        if expected == 'private':
            checks[name]['managed_not_tracked'] = not (set(stamp['files']) & tracked)
            checks[name]['identity_ignored'] = git(target, 'check-ignore', '--no-index', '-q', 'vault/project-id').returncode == 0
            checks[name]['git_index_preserved'] = git(target, 'ls-files', '-s').stdout == before[name]['index']
            checks[name]['head_preserved'] = git(target, 'rev-parse', 'HEAD').stdout.strip() == before[name]['head']
        else:
            checks[name]['managed_core_tracked'] = set(stamp['files']).issubset(tracked)
        if expected == 'local':
            checks[name]['task_namespaces_ignored'] = all(
                git(target, 'check-ignore', '--no-index', '-q', path).returncode == 0
                for path in ('vault/tasks/TASK-9999.md', 'vault/tasks/TASK-9999-review.md', 'vault/tasks/archive/TASK-9999.md'))
            checks[name]['task_not_indexed'] = not any(
                path.startswith('vault/tasks/TASK-') or path.startswith('vault/tasks/archive/') for path in tracked)
            checks[name]['identity_tracked'] = 'vault/project-id' in tracked
        elif expected == 'tracked':
            checks[name]['task_not_ignored'] = git(target, 'check-ignore', '--no-index', '-q', 'vault/tasks/TASK-9999.md').returncode == 1
            checks[name]['no_auto_identity'] = not (target / 'vault/project-id').exists()
        if name == 'valid-existing-private':
            checks[name]['uuid_unchanged'] = files(target)['vault/project-id'] == before[name]['files']['vault/project-id']
            checks[name]['exclude_unchanged'] = (target / '.git/info/exclude').read_text() == before[name]['exclude']
            checks[name]['project_data_unchanged'] = all(
                files(target)[f'vault/{file}.md'] == before[name]['files'][f'vault/{file}.md']
                for file in ('project', 'runtime', 'collaboration', 'decisions', 'handoff', 'parked'))

    source = args.base / 'packages/trellium-zh'
    installed = args.base / 'package-only-destination/trellium-zh'
    checks['package-only'] = {'byte_identical': files(source) == files(installed)}
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    if not all(all(items.values()) for items in checks.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
