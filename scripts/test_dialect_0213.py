"""Publication regressions for the council-accepted allocator and PPC repairs."""
import unittest
import tempfile
from pathlib import Path

import dialect_check as d
import dialect_check_v02 as v


class Publication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = d.SPEC.read_text()
        v.initialise(d.extract_blocks(cls.spec))

    def test_full_version_guard(self):
        ir = ('define void @f() {\n ret void\n}\n'
              '!llvm.module.flags = !{!0}\n'
              '!0 = !{i32 1, !"bennett.dialect", !"VERSION"}\n')
        self.assertEqual(v.recognise(ir.replace('VERSION', '0.2.13'))[0], 'accept')
        for version in ('0.2.12', '0.2.11', '0.2.10', '0.3'):
            with self.subTest(version=version):
                self.assertEqual(v.recognise(ir.replace('VERSION', version))[0],
                                 'reject:BD-E-VERSION')

    def test_publication_and_matching_contract(self):
        from dialect_0213 import check_contract
        for name in ('Bennett-Dialect-Spec.md', 'Bennett-Dialect-Spec-0.3-draft.md'):
            with self.subTest(spec=name):
                check_contract((d.ROOT / 'spec' / name).read_text())

    def test_old_tie_rule_is_detected(self):
        from dialect_0213 import check_contract
        with self.assertRaises(d.Fail):
            check_contract(self.spec.replace('treating a zero significand as even',
                                            'using the high significand for zero'))

    def test_whole_binary_scope_regression_is_detected(self):
        from dialect_0213 import check_contract
        with self.assertRaises(d.Fail):
            check_contract(self.spec.replace('that closure\'s native comparison build',
                                            'the entire native binary'))

    def test_checked_vectors_exist(self):
        from dialect_0213 import STATES
        blocks = d.extract_blocks(self.spec)
        self.assertEqual(set(STATES), {'ppc-zero-low-parity', 'allocator-bookkeeping'})
        for ident in STATES:
            self.assertEqual(sum(b['attrs'].get('state') == ident for b in blocks), 1)

    def test_independent_executors(self):
        from dialect_0213 import STATES
        blocks = d.extract_blocks(self.spec)
        with tempfile.TemporaryDirectory(prefix='0213-witness-') as tmp:
            runner = v.Runner(blocks, self.spec, Path(tmp), set())
            for ident in sorted(STATES):
                with self.subTest(witness=ident):
                    result = v.state_check(runner, runner.block('state', ident))
                    self.assertIn('not production', result['claim'])


if __name__ == '__main__':
    unittest.main()
