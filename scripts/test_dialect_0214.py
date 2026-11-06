"""Publication regressions for dialect 0.2.14: brt-vbi delivery and the R23 console clarification."""
import copy
import tempfile
import unittest
from run_tests import slow
from pathlib import Path

import dialect_check as d
import dialect_check_v02 as v

TRACKS = ('Bennett-Dialect-Spec.md', 'Bennett-Dialect-Spec-0.3-draft.md')


class Publication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = d.SPEC.read_text()
        v.initialise(d.extract_blocks(cls.spec))

    def test_full_version_guard(self):
        ir = ('define void @f() {\n ret void\n}\n'
              '!llvm.module.flags = !{!0}\n'
              '!0 = !{i32 1, !"bennett.dialect", !"VERSION"}\n')
        self.assertTrue('**full version string** (`0.2.14`)' in self.spec)
        self.assertEqual(v.recognise(ir.replace('VERSION', '0.2.14'))[0], 'accept')
        for version in ('0.2.13', '0.2.12', '0.2.10', '0.3'):
            with self.subTest(version=version):
                self.assertEqual(v.recognise(ir.replace('VERSION', version))[0],
                                 'reject:BD-E-VERSION')

    def test_publication_and_matching_contract(self):
        from dialect_0214 import check_contract
        for name in TRACKS:
            with self.subTest(spec=name):
                result = check_contract((d.ROOT / 'spec' / name).read_text())
                self.assertGreaterEqual(result['items'], 8)

    def test_each_accepted_item_is_load_bearing(self):
        from dialect_0214 import check_contract
        mutations = {
            'MUSE-S1 overflow type': ('{iW, i1} @__bennett_rt_smul_with_overflow_i<W>(iW, iW)',
                                      '{iW, i1} @__bennett_rt_smul_with_overflow_i<W>(ptr, ptr)'),
            'SOL-1 function exports': ('every\nexternally visible function definition',
                                       'every\nexternally visible definition'),
            'MUSE-S2 llvm-dis printing': ("by the requested major's llvm-dis", 'by LLVM'),
            'SOL-3 satisfied instances': ('request only unsatisfied instances', 'request every instance'),
            'SOL-2 build record': ('use an empty instance list when no generated module is linked',
                                   'omit the instance list when no generated module is linked'),
            'N §19.1 selective mode': ('selective-module mode\ncollects the union required by its marked device roots',
                                       'selective-module mode\ncollects the whole program'),
            'R23 native close': ('returns -1 with EBADF', 'succeeds'),
            'ASTRA-C6 canonical rule': ('Duplicate or reordered entries MUST reproduce this canonical request and digest.',
                                        'Duplicate entries are errors.'),
        }
        for label, (old, new) in mutations.items():
            with self.subTest(item=label):
                self.assertEqual(self.spec.count(old), 1, label)
                with self.assertRaises(d.Fail):
                    check_contract(self.spec.replace(old, new))

    def test_errata_carries_r23_sentence(self):
        from dialect_0214 import CONSOLE_SENTENCE
        errata = (d.ROOT / 'spec' / 'errata-0.2.10.md').read_text()
        lbq = errata.split('## lbq', 1)[1].split('\n## ', 1)[0]
        self.assertIn(CONSOLE_SENTENCE, lbq)

    def test_checked_vectors_exist_in_both_tracks(self):
        from dialect_0214 import STATES
        self.assertEqual(set(STATES), {'runtime-instance-request', 'runtime-instance-i257'})
        for name in TRACKS:
            blocks = d.extract_blocks((d.ROOT / 'spec' / name).read_text())
            for ident in STATES:
                with self.subTest(spec=name, witness=ident):
                    self.assertEqual(sum(b['attrs'].get('state') == ident for b in blocks), 1)

    def test_request_canonicalisation_rejects_drift(self):
        import dialect_0214 as m
        blocks = d.extract_blocks(self.spec)
        with tempfile.TemporaryDirectory(prefix='0214-request-') as tmp:
            runner = v.Runner(blocks, self.spec, Path(tmp), set())
            good = runner.block('state', 'runtime-instance-request')
            reordered = copy.deepcopy(good)
            reordered['body'] = reordered['body'].replace(
                '[{"op":"ctpop","width":257},{"op":"mul","width":257}]',
                '[{"op":"mul","width":257},{"op":"ctpop","width":257}]')
            self.assertNotEqual(good['body'], reordered['body'])
            with self.assertRaises(d.Fail):
                m.check_state(runner, reordered)
            boolean = copy.deepcopy(good)
            boolean['body'] = boolean['body'].replace('"llvm_major":18', '"llvm_major":true')
            with self.assertRaises(d.Fail):
                m.check_state(runner, boolean)
            result = copy.deepcopy(runner.block('state', 'runtime-instance-i257'))
            result['body'] = result['body'].replace('"product": [6,', '"product": [7,')
            with self.assertRaises(d.Fail):
                m.check_state(runner, result)

    @slow("native and ISA execution witnesses")
    def test_independent_executors(self):
        from dialect_0214 import STATES
        blocks = d.extract_blocks(self.spec)
        with tempfile.TemporaryDirectory(prefix='0214-witness-') as tmp:
            runner = v.Runner(blocks, self.spec, Path(tmp), set())
            for ident in sorted(STATES):
                with self.subTest(witness=ident):
                    result = v.state_check(runner, runner.block('state', ident))
                    self.assertIn('not a helper implementation', result['claim'])


if __name__ == '__main__':
    unittest.main()
