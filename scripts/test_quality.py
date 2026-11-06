"""The repository ratchet must detect complexity, wrappers and tracked litter."""
from pathlib import Path
import tempfile
import unittest
from quality import source_metrics, regressions, measure


class Ratchet(unittest.TestCase):
    def test_nested_control_flow_and_forwarding_wrapper(self):
        simple = source_metrics('def f(x):\n    return x + 1\n')
        nested = source_metrics('def f(x):\n    if x:\n        for y in x:\n            if y:\n                return y\n')
        self.assertGreater(nested['complexity'], simple['complexity'])
        wrapper = source_metrics('def f(x):\n    return g(x)\n')
        self.assertEqual(wrapper['wrappers'], 1)
        self.assertEqual(simple['wrappers'], 0)
        self.assertTrue(regressions({'files': {'a.py': simple}, 'litter': [], 'identifiers': []},
                                    {'files': {'a.py': nested}, 'litter': [], 'identifiers': []}))

    def test_new_litter_and_identifier_fail_but_deletion_passes(self):
        baseline = {'files': {}, 'litter': [], 'identifiers': []}
        for key in ('litter', 'identifiers'):
            changed = dict(baseline, **{key: ['bad']})
            self.assertTrue(regressions(baseline, changed))
            self.assertEqual(regressions(changed, baseline), [])

    def test_scan_uses_index_not_untracked_scratch(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            (root / 'scripts').mkdir()
            (root / 'scripts/good.py').write_text('def f(x):\n    return x + 1\n')
            (root / 'scratch.log').write_text('untracked')
            subprocess.run(['git', '-C', str(root), 'add', 'scripts/good.py'], check=True)
            self.assertEqual(measure(root)['litter'], [])
            subprocess.run(['git', '-C', str(root), 'add', 'scratch.log'], check=True)
            self.assertEqual(measure(root)['litter'], ['scratch.log'])
