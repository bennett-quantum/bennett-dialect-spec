"""Compatible draft regressions, including the PT12 full N9 value effects."""
import unittest
import dialect_check as d
import dialect_check_v02 as v


def analysis(text):
    a=v.Analysis02(d.Module(d.with_decls(text)));a.analyse();return a,a.m.funcs['top']


class AtomicDomains(unittest.TestCase):
    def test_xor_fixed_point(self):
        a,f=analysis('''@cell = internal global i64 1
define void @top() {
 %old = atomicrmw xor ptr @cell, i64 2 seq_cst
 %width = load i64, ptr @cell
 ret void
}
''')
        self.assertEqual(a.ints(f,'%old'),{1,3})
        self.assertEqual(a.ints(f,'%width'),{1,3})

    def test_cmpxchg_fields_and_store(self):
        for compare,success,memory in [(1,{0,1},{1,3}),(9,{0},{1})]:
            with self.subTest(compare=compare):
                a,f=analysis(f'''@cell = internal global i64 1
define void @top() {{
 %pair = cmpxchg ptr @cell, i64 {compare}, i64 3 seq_cst seq_cst
 %old = extractvalue {{i64,i1}} %pair, 0
 %ok = extractvalue {{i64,i1}} %pair, 1
 %width = load i64, ptr @cell
 ret void
}}
''')
                self.assertEqual(a.ints(f,'%old'),memory)
                self.assertEqual(a.ints(f,'%ok'),success)
                self.assertEqual(a.ints(f,'%width'),memory)

    def test_integer_update_variants(self):
        # Exhaustive byte domains avoid a Python execution oracle: these test
        # reference analysis only; checked native witnesses test execution.
        for op,rhs,want in [('xchg',7,{1,7}),('and',2,{0,1}),('nand',255,{1,254}),
                            ('umin',0,{0,1}),('max',255,{1}),('uinc_wrap',2,{0,1,2}),
                            ('udec_wrap',2,{0,1,2}),('usub_sat',2,{0,1})]:
            with self.subTest(op=op):
                a,f=analysis(f'''@cell = internal global i8 1
define void @top() {{
 %old = atomicrmw {op} ptr @cell, i8 {rhs} seq_cst
 %width = load i8, ptr @cell
 ret void
}}
''')
                self.assertEqual(a.ints(f,'%width'),want)

class FirstRegionOperand(unittest.TestCase):
    def test_nested_and_top_first(self):
        import os
        from pathlib import Path
        spec=Path(os.environ.get('DRAFT0211_SPEC',str(d.SPEC))).read_text()
        blocks=d.extract_blocks(spec);v.initialise(blocks)
        for name,want in [('region-reversible-in-action',{'classical'}),
                          ('region-reversible-in-action-top-first',{'body'})]:
            with self.subTest(name=name):
                block=next((b for b in blocks if b['attrs'].get('example')==name),None)
                self.assertIsNotNone(block,'missing checked ordering companion')
                verdict,a=v.recognise(d.with_decls(block['body']))
                self.assertEqual(verdict,'accept');self.assertEqual(a.first_candidates(),want)
                runner=v.Runner(blocks,spec,v.SCRATCH,{'recognise'})
                wrong=dict(block,attrs=dict(block['attrs'],candidates='wrong'))
                with self.assertRaises(d.Fail):runner.recognition(wrong)

if __name__=='__main__':unittest.main()
