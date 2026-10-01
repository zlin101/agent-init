import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path.home() / '.codex/skills/trellium-zh'
sys.path.insert(0, str(ROOT))
from scripts import test_trellium

spec = importlib.util.spec_from_file_location('installed_trellium', PACKAGE / 'assets/trellium.py')
installed = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = installed
spec.loader.exec_module(installed)
test_trellium.agent_init = installed
suite = unittest.TestSuite()
loader = unittest.defaultTestLoader
for case in (test_trellium.WorkSkillRenameTest, test_trellium.ProjectIdentityTest,
             test_trellium.PrivateStorageModeTest, test_trellium.PrivateHistoryTest):
    for name in loader.getTestCaseNames(case):
        # The separate E2E covers the actually installed single-language package.
        if name == 'test_packaged_private_history_and_explicit_uuid_recovery':
            continue
        suite.addTest(case(name))
print('Implementation loaded from:', installed.__file__, flush=True)
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(not result.wasSuccessful())
