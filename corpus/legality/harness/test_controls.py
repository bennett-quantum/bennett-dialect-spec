"""Integration red gates: success means the deliberately illegal IR was rejected."""
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ControlsTests(unittest.TestCase):
    def test_controls_fail_intended_checks(self):
        p = subprocess.run([sys.executable, str(ROOT / 'harness/run.py'), 'controls', '--majors', '18'], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        records = json.loads((ROOT / 'results/raw/controls-18.json').read_text())
        by_case = {x['case']: x for x in records}
        self.assertIn('L1', by_case['control-memory-none']['checks'])
        self.assertIn('L1', by_case['control-readonly']['checks'])
        self.assertIn('L3', by_case['control-handle-deref']['checks'])
        for record in records:
            self.assertTrue(record['outcome'].startswith('FAIL'), record['outcome'])
        twin = by_case['control-region-twin']
        self.assertTrue('L4' in twin['checks'] or twin['mergefunc_did_not_merge'])


if __name__ == '__main__':
    unittest.main()
