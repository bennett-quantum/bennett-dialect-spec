"""Regression checks for the 0.2 pre-flight. Run: python3 -m unittest discover -s scripts."""
import unittest
import tempfile

import dialect_check as d
import dialect_check_v02 as v


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blocks = d.extract_blocks(d.SPEC.read_text())
        v.initialise(cls.blocks)

    def block(self, tag, name):
        return next(b for b in self.blocks if b['attrs'].get(tag) == name)

    def test_wrong_verdict_is_a_failure(self):
        body = self.block('example', 'operand-bad-code')['body']
        got, _ = v.recognise(d.with_decls(body))
        with self.assertRaises(v.Mismatch):
            v.equal('deliberately-wrong', '§3.4', 'accept', got)
        self.assertEqual(got, 'reject:BD-E-OPERAND')

    def test_unknown_effect_does_not_crash(self):
        b = self.block('example', 'effect-console-write') if any(
            x['attrs'].get('example') == 'effect-console-write' for x in self.blocks
        ) else self.block('example', 'effect-console-r')
        self.assertEqual(v.recognise(d.with_decls(b['body']))[0], 'accept')

    def test_first_region_candidates(self):
        b = self.block('example', 'region-reversible-in-action')
        got, a = v.recognise(d.with_decls(b['body']))
        self.assertEqual(got, 'accept')
        self.assertEqual(a.first_candidates(), {'classical'})
        with self.assertRaises(v.Mismatch):
            v.equal('region-reversible-in-action', '§1.5', {'body'}, a.first_candidates())

    def test_residual_validator_rejects_each_rule(self):
        cases = {
            'V1': '%r = add nsw i32 %x, 1\n  ret i32 %r',
            'V5': 'ret i32 poison',
            'V6': '%r = load volatile i32, ptr null\n  ret i32 %r',
            'V11': '%r = alloca i32\n  ret i32 0',
            'V13': '%r = add <2 x i32> zeroinitializer, zeroinitializer\n  ret i32 0',
            'V14': '%r = add i256 1, 2\n  ret i32 0',
        }
        for rule, body in cases.items():
            with self.subTest(rule=rule), self.assertRaisesRegex(d.Reject, rule):
                v.validate('define i32 @test(i32 %x) {\n  ' + body + '\n}\n')

    def test_blockers_are_distinct_from_rejections(self):
        body = self.block('example', 'operand-width-host')['body']
        self.assertEqual(v.recognise(d.with_decls(body))[0], 'blocked:BD-B-ISA4')

    def test_mask_value_set(self):
        m = d.Module('define void @f(i64 %x) {\n  %m = and i64 %x, 3\n  ret void\n}\n')
        self.assertEqual(v.value_set(m, m.funcs['f'], '%m'), {0, 1, 2, 3})

    def test_every_tag_is_registered(self):
        for b in self.blocks:
            if b['attrs']:
                self.assertTrue(v.families(b), b['attrs'])

    def test_normalisation_pairs(self):
        for b in self.blocks:
            if 'normalise-in' not in b['attrs']:
                continue
            name = b['attrs']['normalise-in']
            with self.subTest(example=name):
                want = self.block('normalise-out', name)['body']
                got = v.normalise(b['body'])
                self.assertEqual(d.collapse(want), d.collapse(got))
                self.assertEqual(v.validate(got), 'accept')

    def test_trace_abi02(self):
        b = self.block('semantics', 'sem2-adj')
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            traces = v.build_trace(b['body'], 'sem2-adj', '18', d.toolchains(), tmp)
        events = [d.event_str(e) for e in d.trace_to_events(traces[0])]
        expected = d.collapse(self.block('events', 'sem2-adj')['body'])
        self.assertEqual(events, expected)
        with self.assertRaises(v.Mismatch):
            v.equal('deliberately-wrong-events', '§18.4', expected + ['x H0.0'], events)

    def test_materialised_isa7_and_parameterised_inplace(self):
        b = self.block('example', 'r-fault-code')
        self.assertEqual(v.recognise(d.with_decls(b['body']), materialised=True)[0], 'blocked:BD-B-ISA7')
        b = self.block('example', 'inplace-param-quantum')
        self.assertEqual(v.recognise(d.with_decls(b['body']))[0], 'accept')

    def test_new_native_drivers(self):
        from dialect_native import cases
        for name in ('n-fcmp', 'fp-aggregate', 'entry-stack'):
            with self.subTest(example=name):
                driver, expected, variants = cases(name, self.block('native', name)['body'])
                self.assertTrue(expected)
                self.assertIn('int main', driver)

    def test_fcmp_seed_predicates(self):
        from pathlib import Path
        from dialect_native import SEEDS
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            src=Path(tmp)/'test.c'; exe=Path(tmp)/'test'
            src.write_text('#include <stdint.h>\nextern uint8_t __bennett_sf_cmp_f64(uint64_t,uint64_t,uint32_t);\nint main(void){return !__bennett_sf_cmp_f64(0x3ff0000000000000ULL,0x3ff0000000000000ULL,9) || __bennett_sf_cmp_f64(0x3ff0000000000000ULL,0x4000000000000000ULL,8);}')
            v.command(['cc', src, SEEDS/'softfloat.c', '-o', exe])
            v.command([exe])

    def test_fp_aggregate_map(self):
        from dialect_map import map_object
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,d.SPEC.read_text(),tmp,{'map'})
            got=map_object(runner,self.block('lift','fp-aggregate'))
            self.assertEqual(got,self.block('object','fp-aggregate')['body'])

    def test_handle_containment_at_external_call(self):
        text = '''declare void @external(ptr)
define void @top() {
  %s = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %s
  call void @external(ptr %s)
  ret void
}
'''
        self.assertEqual(v.recognise(d.with_decls(text))[0], 'reject:BD-E-HANDLE-ESCAPE')

    def test_handle_comparison_is_identity_only(self):
        text = '''define void @top() {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %i = ptrtoint ptr %h to i64
  %eq = icmp eq i64 %i, 16
  call void @__bennett_qfree(ptr %h)
  ret void
}
'''
        self.assertEqual(v.recognise(d.with_decls(text))[0], 'reject:BD-E-HANDLE-USE')


if __name__ == '__main__':
    unittest.main()
