"""Regression checks for the 0.2 pre-flight. Run: python3 -m unittest discover -s scripts."""
import unittest
import tempfile

import dialect_check as d
import dialect_check_v02 as v


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = d.SPEC.read_text()
        cls.blocks = d.extract_blocks(cls.spec)
        v.initialise(cls.blocks)

    def block(self, tag, name):
        return next(b for b in self.blocks if b['attrs'].get(tag) == name)

    def test_round3_loops(self):
        from dialect_round3 import check_state
        import json
        vectors = {
            'co-loop-identity': {'counts':[1,2], 'p_one':[0,0], 'flags_clean':True, 'trap':0},
            'co-loop-adj-overwritten': {'entry':[2,2], 'compute_restored':[2,2], 'collision':True, 'bijective':False, 'trap':0},
        }
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state'})
            for name, value in vectors.items():
                b={'attrs':{'state':name,'at':'0'},'body':json.dumps(value)}
                check_state(runner,b)
                wrong=dict(value)
                if name=='co-loop-identity':wrong['p_one']=[0.5,0.5]
                else:wrong['bijective']=True
                with self.assertRaises(d.Fail):check_state(runner,dict(b,body=json.dumps(wrong)))

    def test_round3_deferred_placement(self):
        from dialect_round3 import adjoint_records, check_state
        import json
        events=[('record','a','w'),('cx','w','t'),('h','a')]
        self.assertEqual(adjoint_records(events),[('h','a'),('record','a','w'),('cx','w','t')])
        self.assertEqual(adjoint_records([('record','a','w'),('h','a')]),[('h','a'),('record','a','w')])
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state'})
            b={'attrs':{'state':'deferred-channel-adj-place','at':'0'},'body':json.dumps({'zero_then_H':[0.5,0.5],'plus_joint_zero':1,'record_retained':True,'trap':0})}
            check_state(runner,b)
            with self.assertRaises(d.Fail):check_state(runner,dict(b,body=b['body'].replace('[0.5, 0.5]','[1, 0]')))

    def test_round2_r_entry_classification(self):
        for name in ('region-reversible-marker','region-reversible-qalloc-static','effect-console-r'):
            with self.subTest(example=name):self.assertEqual(v.recognise(d.with_decls(self.block('example',name)['body']),rmode=self.block('example',name)['attrs'].get('rmode'))[0],'blocked:BD-B-ISA7')
        direct=self.block('example','region-reversible-in-action')
        self.assertEqual(v.recognise(d.with_decls(direct['body']))[0],'accept')
        self.assertEqual(v.recognise('define i32 @main() {\n ret i32 0\n}\n',rmode='@main')[0],'blocked:BD-B-ISA7')

    def test_round2_setjmp_instances(self):
        from dialect_bounds import setjmp_reentry
        b=self.block('example','handle-setjmp-reentry')
        verdict,a=v.recognise(d.with_decls(b['body']))
        self.assertEqual(verdict,'blocked:BD-B-ISA4')
        f=a.m.funcs['F'];site=next(i for i in f.instrs() if '@__bennett_qalloc' in i.text)
        self.assertTrue(setjmp_reentry(f,site))

    def test_round2_action_lifetimes(self):
        from dialect_round2 import check_state
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state'})
            for name in ('generation-cancel','nested-cl-view','fault-output-lifetime','co-loop-adjoint','deferred-channel-adj','co-store-release'):
                with self.subTest(example=name):
                    b=self.block('state',name);check_state(runner,b)
                    import json
                    wrong=json.loads(b['body'])
                    field={'generation-cancel':'results','nested-cl-view':'results','fault-output-lifetime':'program_end_probability','co-loop-adjoint':'after_compute','deferred-channel-adj':'probabilities','co-store-release':'store_code'}[name]
                    value=wrong[field]
                    if isinstance(value,list):
                        if isinstance(value[0],list):value[0][0]+=1
                        else:value[0]+=1
                    else:wrong[field]+=1
                    with self.assertRaises(d.Fail):check_state(runner,dict(b,body=json.dumps(wrong)))

    def test_round2_memory_contracts(self):
        from dialect_round2 import check_state
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state'})
            for name in ('entry-allocation-only','arena-logical-bounds'):
                b=self.block('state',name)
                check_state(runner,b)
                with self.assertRaises(d.Fail):check_state(runner,dict(b,body=b['body'].replace('4112','4096').replace('513','514')))

    def test_round2_materialisation_boundaries(self):
        for intrinsic in ('abs','ctlz','cttz'):
            ir=f'declare i8 @llvm.{intrinsic}.i8(i8, i1 immarg)\ndefine i8 @f(i8 %x) {{\n %v = call i8 @llvm.{intrinsic}.i8(i8 %x, i1 false)\n ret i8 %v\n}}\n'
            with self.subTest(intrinsic=intrinsic):
                with self.assertRaisesRegex(d.Reject,'V4'):v.validate(ir)
                if intrinsic=='abs':self.assertIn('icmp slt i8 %x, 0',v.normalise(ir))
                else:self.assertIn('@__bennett_rt_'+intrinsic+'_i8',v.normalise(ir))
        ir='define i32 @f() {\n %v = bitcast <2 x i16> <i16 1, i16 2> to i32\n ret i32 %v\n}\n'
        self.assertNotIn('<2 x',v.normalise(ir).split('define')[1])

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
        self.assertEqual(v.recognise(d.with_decls(b['body']),rmode=b['attrs'].get('rmode'))[0], b['attrs']['verdict'])

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

    def test_committed_v10_reconciliation(self):
        # These names come from editor commit 976e4bb, not a checker rewrite.
        for name in ('validator-v10-clean','validator-v10-carriers'):
            with self.subTest(example=name):self.assertEqual(v.validate(self.block('example',name)['body']),'accept')
        with self.assertRaisesRegex(d.Reject,'V9|V10'):
            v.validate(self.block('example','validator-v10-residue')['body'])
        for ty in ('half','bfloat','float','double','x86_fp80','fp128','ppc_fp128'):
            with self.subTest(format=ty):
                ir=f'define {ty} @f({ty} %x) {{\n %n = fneg {ty} %x\n ret {ty} %n\n}}\n'
                self.assertEqual(v.validate(ir),'accept')
        good='define void @f() {\n ret void\n}\n!llvm.module.flags = !{!0}\n!0 = !{i32 1, !"bennett.dialect", !"0.2.3"}\n'
        self.assertEqual(v.recognise(good)[0],'accept')
        self.assertEqual(v.recognise(good.replace('0.2.3','0.2.1'))[0],'reject:BD-E-VERSION')

    def test_v4_v12_residues_and_clean(self):
        for rule in ('v4','v12'):
            with self.subTest(rule=rule):
                self.assertEqual(v.validate(self.block('example','validator-'+rule+'-clean')['body']),'accept')
                with self.assertRaisesRegex(d.Reject,rule.upper()):
                    v.validate(self.block('example','validator-'+rule+'-residue')['body'])
        # Runtime-like spelling alone cannot exempt an undefined callee.
        with self.assertRaisesRegex(d.Reject,'V12'):
            v.validate('declare i8 @__bennett_rt_missing()\ndefine i8 @f() {\n %v = call i8 @__bennett_rt_missing()\n ret i8 %v\n}\n')

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
                got = v.normalise(b['body'],rmode=b['attrs'].get('rmode'),platform=b['attrs'].get('platform'))
                self.assertEqual(d.collapse(want), d.collapse(got))
                self.assertEqual(v.validate(got,linked=v.NORMALISATION_LINK), 'accept')

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

    def test_binding_and_indirectbr_maps(self):
        from dialect_map import map_object
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'map'})
            for name in ('binding-out-byte','binding-block-byte','binding-clock-read','binding-console-byte','indirectbr-two-blocks'):
                with self.subTest(example=name):
                    got=map_object(runner,self.block('lift',name))
                    self.assertEqual(got,self.block('object',name)['body'])
                    bad=dict(self.block('lift',name),body=self.block('lift',name)['body'].replace('i8 9','i8 8').replace('i8 120','i8 121').replace('i64 %c, 1','i64 %c, 2').replace('load i8, ptr %p','load i8, ptr null'))
                    with self.assertRaises(d.Fail):map_object(runner,bad)

    def test_fp_aggregate_map(self):
        from dialect_map import map_object
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'map'})
            got=map_object(runner,self.block('lift','fp-aggregate'))
            self.assertEqual(got,self.block('object','fp-aggregate')['body'])

    def test_packed_partial_and_gc_adapters(self):
        cases=[
            'define i1 @f(ptr %p) {\n %v = load <8 x i1>, ptr %p\n %r = extractelement <8 x i1> %v, i64 7\n ret i1 %r\n}\n',
            'define void @f(ptr %p, ptr %q) {\n %v = load i129, ptr %p\n %r = add i129 %v, 1\n store i129 %r, ptr %q\n ret void\n}\n',
            'define void @f(ptr %p, ptr %q) {\n %v = load i129, ptr %p\n %r = sext i129 %v to i256\n store i256 %r, ptr %q\n ret void\n}\n',
            'declare ptr @llvm.experimental.gc.get.pointer.base.p0.p0(ptr)\ndeclare i64 @llvm.experimental.gc.get.pointer.offset.p0.i64(ptr)\ndefine i64 @f(ptr %b) {\n %p = getelementptr i8, ptr %b, i64 8\n %r = call i64 @llvm.experimental.gc.get.pointer.offset.p0.i64(ptr %p)\n ret i64 %r\n}\n']
        for body in cases:
            with self.subTest(body=body):
                got=v.normalise(body)
                self.assertEqual(v.validate(got,linked=v.NORMALISATION_LINK),'accept')
                self.assertNotIn('load i1,',got)
                self.assertNotIn('call i64 @llvm.experimental.gc.',got)

    def test_boundary_state_execution(self):
        from dialect_state import check_native_state
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state'})
            for name in ('normalisation-boundaries','fcmp-abi','fp-sign-carrier','inplace-bound','r-fault-code'):
                with self.subTest(example=name):
                    b=self.block('state',name)
                    check_native_state(runner,b)
                    if name=='fcmp-abi':
                        bad=dict(b,body=b['body'].replace(',9)=1',',9)=0'))
                        with self.assertRaises(v.Mismatch):check_native_state(runner,bad)

    def test_cc_fixtures_validate(self):
        from dialect_cc import fixture
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'cc-run'})
            for b in self.blocks:
                if 'cc-run' in b['attrs']:
                    with self.subTest(example=b['attrs']['cc-run']):
                        path,_=fixture(runner,b['attrs']['cc-run'])
                        runner.isa.call('check',path)

    def test_tdl_state_prefixes(self):
        from dialect_tdl import ORIGINAL,compare_original
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state'})
            for b in self.blocks:
                if b['attrs'].get('state') in ORIGINAL:
                    with self.subTest(example=b['attrs']):compare_original(runner,b)

    def test_tdl_boundaries_and_wrapper_contracts(self):
        from dialect_tdl import check_boundary, BOUNDARIES, check_wrapper
        from dialect_state import check_native_state
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state'})
            for name in sorted(BOUNDARIES):
                with self.subTest(example=name):check_boundary(runner,self.block('state',name))
            for name in ('wide-delivery','entry-backing','region-two-measure-candidates','clean-predicate','generation-budget'):
                with self.subTest(example=name):check_wrapper(runner,self.block('state',name))
            for name in ('partial-observe','classical-event-application','sv39-kernel-alias'):
                with self.subTest(example=name):check_native_state(runner,self.block('state',name))

    def test_tdl_artifacts_and_mutations(self):
        from dialect_tdl import check_tdl
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'tdl'})
            for b in self.blocks:
                if 'tdl' not in b['attrs']:continue
                with self.subTest(example=b['attrs']):check_tdl(runner,b)
            b=self.block('tdl','tdl-a')
            bad=dict(b,body=b['body'].replace('0x05 ctrl','0x07 ctrl'))
            with self.assertRaises(v.Mismatch):check_tdl(runner,bad)

    def test_arena_hidden_base_map(self):
        from dialect_map import map_arena
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'map'})
            got=map_arena(runner)
            self.assertEqual(got,self.block('object','arena-o1')['body'])

    def test_gep_dimension_is_not_an_index_bound(self):
        source='@tab = global [2 x ptr] [ptr @f, ptr @g]\ndefine void @f(ptr %e) {\n ret void\n}\ndefine void @g(ptr %e) {\n ret void\n}\ndefine void @top(i64 %i){\n %p = getelementptr [1 x ptr], ptr @tab, i64 0, i64 %i\n %f = load ptr, ptr %p\n call void @__bennett_adj(ptr %f, ptr null, ptr null)\n ret void\n}\n'
        verdict,a=v.recognise(d.with_decls(source))
        self.assertEqual(verdict,'accept')
        self.assertEqual(a.first_candidates(),{'f','g'})

    def test_one_shot_program_adapter(self):
        from dialect_cc import check
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'run-program'})
            for b in self.blocks:
                if 'cc-run' in b['attrs']:
                    with self.subTest(example=b['attrs']):check(runner,b,'run-program')

    def test_driver_platform_scenarios(self):
        from dialect_driver import SCENARIOS, check_scenario
        from dialect_meta import coverage
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state','coverage'})
            for name in SCENARIOS.values():
                with self.subTest(example=name):
                    b=self.block('state',name)
                    check_scenario(runner,b)
                    with self.assertRaises((v.Mismatch,d.Fail)):
                        check_scenario(runner,dict(b,body=b['body'].replace('7','6').replace('9','8').replace('78','79')+'\nwrong obligation'))
            self.assertTrue(all(coverage(runner)[0][section] for section in SCENARIOS))
            # An index/source tag alone cannot count as executable evidence.
            runner.scenario_evidence.clear()
            self.assertTrue(all(not coverage(runner)[0][section] for section in SCENARIOS))

    def test_r_budget_blocker_routing_preserves_09_obligation(self):
        from pathlib import Path
        from unittest.mock import patch
        from dialect_cc import r_budget_prefix
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'recognise','blocker','state'})
            runner.recognition(self.block('example','r-budget-prefix'))
            runner.blocker(self.block('blocker','r-budget-prefix'))
            with patch.object(runner.isa,'call',side_effect=AssertionError('ISA 0.8 must not execute ISA 0.9 result')):
                receipt=r_budget_prefix(runner,self.block('state','r-budget-prefix'))
            self.assertEqual(receipt['verdict'],'blocked:BD-B-ISA7')
            self.assertEqual(receipt['bead'],'b-dialect-spec-bz6')
            self.assertFalse(receipt['executed'])
            self.assertEqual(receipt['required_isa09']['fault'],1)
            self.assertEqual(len(receipt['required_isa09']['terminal_records']),1)
            self.assertEqual(receipt['required_isa09']['tape'],[])
            self.assertTrue((Path(tmp)/'r-budget-prefix-isa09-obligation.json').is_file())
            b=self.block('state','r-budget-prefix')
            with self.assertRaises(d.Fail):r_budget_prefix(runner,dict(b,body=b['body'].replace('code=1','code=2')))

    def test_interpreter_rebuilds_when_head_moves(self):
        from pathlib import Path
        from unittest.mock import patch
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            repo=Path(tmp)/'isa';src=repo/'reference-interpreter';(src/'src').mkdir(parents=True)
            (src/'Cargo.toml').write_text('[package]\nname="bennett-isa-ref"\nversion="0.0.0"\nedition="2021"\n')
            (src/'README.md').write_text('Snapshot fixture\n')
            v.command(['git','-C',repo,'init','--quiet'])
            def commit(revision):
                (src/'src'/'main.rs').write_text('fn main() { println!("{{\\"revision\\":'+str(revision)+'}}"); }'.replace('\\"','\\\"'))
                v.command(['git','-C',repo,'add','.'])
                v.command(['git','-C',repo,'-c','user.name=Checker test','-c','user.email=checker@example.invalid','commit','--quiet','-m',str(revision)])
            commit(1)
            with patch.object(v,'ISA_SOURCE',src),patch.object(v,'ISA_DIR',Path(tmp)/'snapshot'):
                interpreter=v.Interpreter()
                self.assertEqual(interpreter.call('hash','unused')['revision'],1)
                first=interpreter.exe
                commit(2)
                self.assertEqual(interpreter.call('hash','unused')['revision'],2)
                self.assertNotEqual(first,interpreter.exe)
                import json
                receipt=json.loads((v.ISA_DIR/'BUILD.json').read_text())
                self.assertEqual(receipt['commit'],v.read_commit(repo))

    def test_view_pass_guard_does_not_reject_filenames(self):
        self.assertEqual(v.command(['/bin/true','compute-view-event-1.bisa']),'')
        for flag in ('-passes=view-cfg','-view-cfg','-passes=function(view-dom)'):
            with self.subTest(flag=flag),self.assertRaisesRegex(d.Fail,'rule 11'):
                v.command(['/bin/true',flag])

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
