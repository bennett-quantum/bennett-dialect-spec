"""Regression tests for the v3 harness fixes (2026-10-28, second implementer).

Each class was written before its fix and observed failing.
"""
import pathlib
import tempfile
import unittest

import run
from run import ROOT

INTERNAL_REGION = '''; CASE: {stem}
; HAZARD: harness fixture: internal region function
; INPUTS: 0..3
; EXPECT: legal
declare ptr @__bennett_qalloc(i64, i64)
declare void @__bennett_gate(i32, ptr, i64)
declare void @__bennett_ctrl(ptr, i64, ptr, i64, ptr)
declare void @__bennett_qfree(ptr)
define internal void @hidden_region(ptr %env) {{
  %h = load ptr, ptr %env
  call void @__bennett_gate(i32 4, ptr %h, i64 0)
  ret void
}}
define i64 @case_entry(i64 %x) {{
  %env = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %env
  call void @__bennett_ctrl(ptr %h, i64 0, ptr @hidden_region, i64 3, ptr %env)
  call void @__bennett_qfree(ptr %h)
  ret i64 %x
}}
'''

SWITCH_CASE = '''; CASE: {stem}
; HAZARD: harness fixture: switch before structurizecfg
; INPUTS: 0..7
; EXPECT: legal
declare ptr @__bennett_qalloc(i64, i64)
declare void @__bennett_gate(i32, ptr, i64)
declare void @__bennett_qfree(ptr)
define i64 @case_entry(i64 %x) {{
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %k = and i64 %x, 3
  switch i64 %k, label %d [ i64 0, label %a
                            i64 1, label %b
                            i64 2, label %c ]
a:
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  br label %j
b:
  call void @__bennett_gate(i32 2, ptr %h, i64 0)
  br label %j
c:
  call void @__bennett_gate(i32 3, ptr %h, i64 0)
  br label %j
d:
  call void @__bennett_gate(i32 4, ptr %h, i64 0)
  br label %j
j:
  %r = phi i64 [ 10, %a ], [ 20, %b ], [ 30, %c ], [ 40, %d ]
  call void @__bennett_qfree(ptr %h)
  ret i64 %r
}}
'''


def fixture(text, stem):
    d = tempfile.mkdtemp(dir=ROOT / 'harness', prefix='fixture-')
    path = pathlib.Path(d) / (stem + '.ll')
    path.write_text(text.format(stem=stem))
    return path


class Integration:
    @classmethod
    def setUpClass(cls):
        cls.tcs = run.tools_for([18])
        cls.tc = cls.tcs[18]
        cls.rt = run.runtime_objects()

    def case(self, text, stem):
        path = fixture(text, stem)
        try:
            return run.prepare_case(path, self.tcs, self.rt)
        finally:
            path.unlink()
            path.parent.rmdir()

    def evaluate(self, case, pipeline, **extra):
        return run.evaluate(run.task_for(case, self.tc, self.rt, 'P1', pipeline, **extra))


class SymbolResolutionTests(unittest.TestCase):
    def test_canonicalize_resolves_unresolved_and_alias_sets(self):
        symbols = {0x401000: ['body'], 0x402000: ['a', 'b']}
        raw = 'CTRL H0 0 F@0x401000 2\nADJ F@0x402000\nADJ F@0x403000\n'
        self.assertEqual(run.canonicalize_trace(raw, symbols),
                         'CTRL H0 0 F:body 2\nADJ F:a=b\nADJ F:F?\n')

    def test_canonicalize_rejects_unexpected_raw_spelling(self):
        with self.assertRaises(ValueError):
            run.canonicalize_trace('CTRL H0 0 F:body 2\n', {})

    def test_l4_alias_set_needs_a_definition(self):
        ir = 'define void @a(ptr %e) {\n ret void\n}\n@b = alias void (ptr), ptr @a\n'
        trace = 'ADJ F:a=b\n'
        self.assertEqual(run.check_l4(trace, trace, ir), [])
        self.assertTrue(run.check_l4('ADJ F:b\n', trace, ir))


class InternalRegionBaselineTests(Integration, unittest.TestCase):
    def test_internal_region_resolves_in_baseline_and_after_o3(self):
        case = self.case(INTERNAL_REGION, 'fixture-internal-region')
        base = case['majors']['18']
        self.assertEqual(base['issues'], {}, base['issues'])
        trace = pathlib.Path(base['native']['trace']).read_text()
        self.assertIn('F:hidden_region', trace)
        self.assertNotIn('F?', trace)
        self.assertIn('F@0x', pathlib.Path(base['native']['raw_trace']).read_text())
        r = self.evaluate(case, 'default<O3>')
        self.assertEqual(r['checks'], [], r['details'])


class FatObjectNmTests(Integration, unittest.TestCase):
    def test_embed_bitcode_object_still_lists_markers(self):
        case = self.case(INTERNAL_REGION, 'fixture-embed')
        r = self.evaluate(case, 'embed-bitcode')
        self.assertNotIn('L5', r['details'], r['details'])
        self.assertIn(r['outcome'], ('pass', 'noop'))


class EnvironmentTests(unittest.TestCase):
    ir_with_entry = 'define i64 @case_entry(i64 %x) {\n ret i64 %x\n}\n'
    ir_internal_entry = 'define internal i64 @case_entry(i64 %x) {\n ret i64 %x\n}\n'

    def link(self, *symbols):
        return ''.join(f"x.ll:(.text+0x1): undefined reference to `{s}'\n" for s in symbols) + 'collect2: error: ld returned 1 exit status\n'

    def test_runtime_symbols_are_env(self):
        e = run.env_evidence_link(self.link('__asan_init', '__asan_version_mismatch_check_v8'), self.ir_with_entry)
        self.assertEqual(e['rule'], 'missing-instrumentation-runtime')
        self.assertEqual(e['undefined'], ['__asan_init', '__asan_version_mismatch_check_v8'])

    def test_marker_or_unknown_symbol_is_never_env(self):
        self.assertIsNone(run.env_evidence_link(self.link('__asan_init', '__bennett_gate.dfsan'), self.ir_with_entry))
        self.assertIsNone(run.env_evidence_link(self.link('foo'), self.ir_with_entry))
        self.assertIsNone(run.env_evidence_link('ld: some other error\n', self.ir_with_entry))

    def test_entry_only_when_really_gone(self):
        self.assertIsNone(run.env_evidence_link(self.link('case_entry'), self.ir_with_entry))
        self.assertEqual(run.env_evidence_link(self.link('case_entry'), self.ir_internal_entry)['rule'], 'entry-not-external')
        self.assertEqual(run.env_evidence_link(self.link('case_entry'), '')['rule'], 'entry-not-external')

    def test_ld_follow_hidden_and_hwasan_relocation_forms(self):
        follow = self.link('__msan_param_tls') + "/usr/bin/ld: x.o:x.ll:(.text+0x1d5): more undefined references to `__msan_param_tls' follow\n"
        self.assertEqual(run.env_evidence_link(follow, self.ir_with_entry)['undefined'], ['__msan_param_tls'])
        marker_follow = self.link('__msan_param_tls') + "/usr/bin/ld: x.o:x.ll:(.text+0x1): more undefined references to `__bennett_gate.x' follow\n"
        self.assertIsNone(run.env_evidence_link(marker_follow, self.ir_with_entry))
        hidden = "/usr/bin/ld: x.exe: hidden symbol `__llvm_ctx_profile_expected_callee' isn't defined\n/usr/bin/ld: final link failed: bad value\ncollect2: error: ld returned 1 exit status\n"
        self.assertEqual(run.env_evidence_link(hidden, self.ir_with_entry)['undefined'], ['__llvm_ctx_profile_expected_callee'])
        self.assertIsNone(run.env_evidence_link('/usr/bin/ld: final link failed: bad value\n', self.ir_with_entry))
        reloc = self.link('__hwasan_init') + "x.c:32:(.text+0x1b6): relocation truncated to fit: R_X86_64_PC32 against `.data.rel.ro'\n"
        self.assertIsNone(run.env_evidence_link(reloc, self.ir_with_entry))
        hw = self.ir_with_entry + 'declare void @__hwasan_init()\n'
        self.assertEqual(run.env_evidence_link(reloc, hw)['rule'], 'missing-instrumentation-runtime')

    def test_llc_instrprof(self):
        ir = 'define void @f() {\n call void @llvm.instrprof.increment(ptr @x, i64 0, i32 1, i32 0)\n ret void\n}\n'
        self.assertEqual(run.env_evidence_llc('LLVM ERROR: Cannot select: intrinsic %llvm.instrprof.increment\n', ir)['rule'], 'unlowered-instrprof-intrinsic')
        crash = "Stack dump:\n2.\tRunning pass 'X86 DAG->DAG Instruction Selection' on function '@f'\n"
        self.assertEqual(run.env_evidence_llc(crash, ir)['rule'], 'unlowered-instrprof-intrinsic')
        self.assertIsNone(run.env_evidence_llc('LLVM ERROR: something else\n', ir))
        self.assertIsNone(run.env_evidence_llc('LLVM ERROR: Cannot select: intrinsic %llvm.instrprof.increment\n', 'define void @f() {\n ret void\n}\n'))


class EnvironmentIntegrationTests(Integration, unittest.TestCase):
    def test_asan_is_env_error_and_metarenamer_non_preserving(self):
        case = self.case(INTERNAL_REGION, 'fixture-env')
        r = self.evaluate(case, 'asan')
        self.assertEqual(r['outcome'], 'env-error', r['details'])
        self.assertTrue(r['env_evidence'])
        r = self.evaluate(case, 'metarenamer')
        self.assertEqual(r['outcome'], 'non-preserving', r['details'])
        r = self.evaluate(case, 'internalize')
        self.assertEqual(r['outcome'], 'env-error', r['details'])
        r = self.evaluate(case, 'internalize', opt_args=['-internalize-public-api-list=case_entry'])
        self.assertIn(r['outcome'], ('pass', 'noop'), r['details'])


class PreconditionTests(Integration, unittest.TestCase):
    CHAIN = 'function(lowerswitch,fix-irreducible,unify-loop-exits,structurizecfg)'

    def test_structurizecfg_switch_is_precondition(self):
        case = self.case(SWITCH_CASE, 'fixture-switch')
        r = self.evaluate(case, 'function(structurizecfg)')
        self.assertEqual(r['outcome'], 'precondition', r)
        self.assertEqual(r['precondition']['rerun']['pipeline'], self.CHAIN)
        self.assertEqual(r['precondition']['rerun']['outcome'], 'pass')
        self.assertTrue(r['precondition']['raw_checks'])
        self.assertTrue(r['precondition']['violated'])

    def test_no_violation_means_fail(self):
        # Already in the required form: the prerequisite chain changes nothing,
        # so a failure could not be blamed on a precondition.
        case = self.case(INTERNAL_REGION, 'fixture-no-violation')
        self.assertFalse(run.prerequisites_change_input(case, self.tc, run.precondition_for('function(structurizecfg)', 18),
                                                        case['majors']['18']['module']))

    def test_spelling_and_scope(self):
        self.assertEqual(run.precondition_for('function(structurizecfg)', 18)['pipeline'], self.CHAIN)
        self.assertEqual(run.precondition_for('function(structurizecfg)', 23)['pipeline'], self.CHAIN.replace('lowerswitch', 'lower-switch'))
        self.assertIsNone(run.precondition_for('function(gvn)', 18))


class RegionShapeTests(unittest.TestCase):
    head = ('declare void @__bennett_adj(ptr, ptr)\ndeclare void @__bennett_compute(ptr, ptr, ptr)\n'
            'declare void @f(ptr)\ndeclare void @h(ptr)\n')

    def shapes(self, body, extra=''):
        ir = self.head + extra + 'define void @g(i1 %c, i64 %i, ptr %p) {\n' + body + '\n ret void\n}\n'
        return [(s['marker'], s['operand'], s['shape']) for s in run.region_operand_shapes(ir)]

    def test_shapes(self):
        self.assertEqual(self.shapes(' call void @__bennett_adj(ptr nonnull @f, ptr null)'), [('__bennett_adj', 0, 'const')])
        self.assertEqual(self.shapes(' %s = select i1 %c, ptr @f, ptr @h\n call void @__bennett_adj(ptr %s, ptr null)'), [('__bennett_adj', 0, 'select-of-consts')])
        self.assertEqual(self.shapes(' call void @__bennett_compute(ptr @f, ptr %p, ptr null)'),
                         [('__bennett_compute', 0, 'const'), ('__bennett_compute', 1, 'other')])
        table = '@switch.table.g = private unnamed_addr constant [2 x ptr] [ptr @f, ptr @h], align 8\n'
        self.assertEqual(self.shapes(' %q = getelementptr inbounds [2 x ptr], ptr @switch.table.g, i64 0, i64 %i\n %l = load ptr, ptr %q, align 8\n call void @__bennett_adj(ptr %l, ptr null)', table),
                         [('__bennett_adj', 0, 'load-from-const-table')])
        mutable = '@tab = global [2 x ptr] [ptr @f, ptr @h]\n'
        self.assertEqual(self.shapes(' %q = getelementptr inbounds [2 x ptr], ptr @tab, i64 0, i64 %i\n %l = load ptr, ptr %q\n call void @__bennett_adj(ptr %l, ptr null)', mutable)[0][2], 'other')

    def test_phi_shape(self):
        ir = self.head + '''define void @g(i1 %c) {
entry:
  br i1 %c, label %a, label %b
a:
  br label %j
b:
  br label %j
j:
  %f = phi ptr [ @f, %a ], [ @h, %b ]
  call void @__bennett_adj(ptr %f, ptr null)
  ret void
}
'''
        self.assertEqual([s['shape'] for s in run.region_operand_shapes(ir)], ['phi-of-consts'])

    def test_quoted_names_and_mixed_phi(self):
        self.assertEqual(self.shapes(' %"a(b)" = select i1 %c, ptr @f, ptr @h\n call void @__bennett_adj(ptr nonnull %"a(b)", ptr null)'),
                         [('__bennett_adj', 0, 'select-of-consts')])
        table = '@switch.table.g = private unnamed_addr constant [2 x ptr] [ptr @f, ptr @h], align 8\n'
        ir = self.head + table + '''define void @g(i1 %c, i64 %i) {
entry:
  br i1 %c, label %t, label %j
t:
  %q = getelementptr inbounds [2 x ptr], ptr @switch.table.g, i64 0, i64 %i
  %l = load ptr, ptr %q, align 8
  br label %j
j:
  %f = phi ptr [ %l, %t ], [ @f, %entry ]
  call void @__bennett_adj(ptr %f, ptr null)
  %r = alloca ptr
  store ptr %f, ptr %r
  %v = load ptr, ptr %r
  call void @__bennett_adj(ptr %v, ptr null)
  ret void
}
'''
        self.assertEqual([s['shape'] for s in run.region_operand_shapes(ir)], ['phi-of-mixed', 'other'])

    def test_introduced(self):
        pre = self.head + 'define void @g(i1 %c) {\n call void @__bennett_adj(ptr @f, ptr null)\n call void @__bennett_adj(ptr @h, ptr null)\n ret void\n}\n'
        post = self.head + 'define void @g(i1 %c) {\n %s = select i1 %c, ptr @f, ptr @h\n call void @__bennett_adj(ptr %s, ptr null)\n ret void\n}\n'
        r = run.check_l6(pre, post)
        self.assertEqual(r['introduced'], [{'marker': '__bennett_adj', 'operand': 0, 'shape': 'select-of-consts'}])
        self.assertEqual(run.check_l6(pre, pre)['introduced'], [])


O3_CHANGES = '''; CASE: {stem}
; HAZARD: harness fixture: O3 legally deletes a memory(none) measurement
; INPUTS: 0..7
; EXPECT: probe
declare ptr @__bennett_qalloc(i64, i64)
declare i1 @__bennett_measure(ptr, i64) memory(none) nounwind willreturn
declare void @__bennett_qfree(ptr)
define i64 @case_entry(i64 %x) {{
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  br label %loop
loop:
  %i = phi i64 [0, %entry], [%j, %loop]
  %acc = phi i64 [0, %entry], [%sum, %loop]
  %m = call i1 @__bennett_measure(ptr %h, i64 0)
  %v = zext i1 %m to i64
  %sum = add i64 %acc, %v
  %j = add i64 %i, 1
  %done = icmp eq i64 %j, 4
  br i1 %done, label %exit, label %loop
exit:
  call void @__bennett_qfree(ptr %h)
  ret i64 %sum
}}
'''


class InheritedAttributionTests(Integration, unittest.TestCase):
    def test_post_o3_failure_inherited_only_when_behaviour_identical(self):
        case = self.case(O3_CHANGES, 'fixture-o3-changes')
        setup = run.evaluate(run.task_for(case, self.tc, self.rt, 'setup', 'default<O3>'))
        self.assertTrue(setup['outcome'].startswith('FAIL'), setup['outcome'])
        self.assertEqual(setup.get('inherited'), None)
        r = self.evaluate(case, 'function(instsimplify)', mode='post-O3', input_module=setup['transformed'])
        self.assertTrue(r['outcome'].startswith('FAIL'))
        self.assertEqual(r['inherited']['from'], 'default<O3> output')
        twin = self.case(INTERNAL_REGION.replace('define internal void @hidden_region', 'define void @hidden_region'), 'fixture-not-inherited')
        r = self.evaluate(twin, 'function(instsimplify)')
        self.assertIsNone(r.get('inherited'))


class AttributeParserTests(unittest.TestCase):
    def test_value_not_swallowed(self):
        pre = 'declare void @__bennett_gate(i32, ptr, i64)\ndefine i64 @case_entry(i64 %x) {\n call void @__bennett_gate(i32 1, ptr null, i64 %x)\n ret i64 %x\n}\n'
        post = pre.replace('i32 1, ptr null', 'i32 noundef 1, ptr align 8 null')
        attrs = {x['attribute'] for x in run.check_l2(pre, post)['observations']}
        self.assertEqual(attrs, {'noundef', 'align 8'})


class FrontendFlagTests(unittest.TestCase):
    def test_c_cases_are_not_noinline(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'harness') as d:
            source = pathlib.Path(d) / 'fixture-cflags.c'
            source.write_text('// CASE: fixture-cflags\n// HAZARD: x\n// INPUTS: 0\n// EXPECT: legal\n#include <stdint.h>\n'
                              'static int64_t helper(int64_t x) { return x + 1; }\nint64_t case_entry(int64_t x) { return helper(x); }\n')
            case = run.prepare_case(source, run.tools_for([18]), run.runtime_objects())
            text = pathlib.Path(case['majors']['18']['module']['ll']).read_text()
            self.assertNotIn('noinline', text)
            self.assertNotIn('optnone', text)
            self.assertIn('define internal i64 @helper', text)


if __name__ == '__main__':
    unittest.main()
