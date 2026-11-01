"""Executable consumer-gap regressions, independent LLVM N0 lowering."""
import unittest
import dialect_check as d
from dialect_check_v02 import Analysis02, headless_env

class N0Resolution(unittest.TestCase):
    def test_widenable_definition_and_original_addresses(self):
        headless_env()
        text='''declare i1 @llvm.experimental.widenable.condition()
@alias = alias i1 (), ptr @f
define i1 @f() {
 %r = call i1 @llvm.experimental.widenable.condition()
 ret i1 %r
}
'''
        for major in d.MAJORS:
            a=Analysis02(d.Module(text));a.major=major
            self.assertEqual(a.resolve('f'),'f')
            self.assertEqual(a.resolve('alias'),'f')
            # Resolution's virtual bodies must not mutate the address-bearing source.
            self.assertIn('llvm.experimental.widenable.condition',a.m.funcs['f'].instrs().__next__().text)


class CarrierABI(unittest.TestCase):
    def verify(self, text, major):
        from dialect_check_v02 import SCRATCH, command
        path=SCRATCH/f'0212-abi-{major}.ll';path.write_text(text)
        command([d.toolchains()[major]/'opt','-passes=verify','-disable-output',path])

    def test_arbitrary_names_and_operands(self):
        from dialect_normalise import normalise
        widths={name:8 for name in ('Float8E5M2','Float8E5M2FNUZ','Float8E4M3','Float8E4M3FN','Float8E4M3FNUZ','Float8E4M3B11FNUZ','Float8E3M4','Float8E8M0FNU')}
        widths.update(Float6E3M2FN=6,Float6E2M3FN=6,Float4E2M1FN=4)
        for fmt,n in widths.items():
            for t,base,bits in (("half","f16",16),("bfloat","bf16",16),("float","f32",32),("double","f64",64),("x86_fp80","f80",80),("fp128","f128",128),("ppc_fp128","ppcf128",128)):
                text=f'''declare i{n} @llvm.convert.to.arbitrary.fp.i{n}.{base}({t}, metadata, metadata, i1)
declare {t} @llvm.convert.from.arbitrary.fp.{base}.i{n}(i{n}, metadata)
define i{n} @to({t} %x) {{
 %r = call i{n} @llvm.convert.to.arbitrary.fp.i{n}.{base}({t} %x, metadata !"{fmt}", metadata !"round.towardzero", i1 true)
 ret i{n} %r
}}
define {t} @from(i{n} %x) {{
 %r = call {t} @llvm.convert.from.arbitrary.fp.{base}.i{n}(i{n} %x, metadata !"{fmt}")
 ret {t} %r
}}
'''
                self.verify(text,'23')
                out=normalise(text,major='23')
                self.assertIn(f'call i{n} @__bennett_sf_convert_to_{fmt}_{base}(i{bits} %nz.0.r, i32 3, i1 true)',out)
                self.assertIn(f'call i{bits} @__bennett_sf_convert_from_{fmt}_{base}(i{n} %x)',out)
                self.verify(out,'23')


    def test_constrained_comparison_operands(self):
        from dialect_normalise import normalise
        for major in d.MAJORS:
            for op in ('fcmp','fcmps'):
                for behavior in ('ignore','maytrap','strict'):
                    for p,pred in enumerate('false oeq ogt oge olt ole one ord uno ueq ugt uge ult ule une true'.split()):
                        text=f'''declare i1 @llvm.experimental.constrained.{op}.f64(double, double, metadata, metadata)
define i1 @f(double %x, double %y) {{
 %r = call i1 @llvm.experimental.constrained.{op}.f64(double %x, double %y, metadata !"{pred}", metadata !"fpexcept.{behavior}")
 ret i1 %r
}}
'''
                        out=normalise(text,major=major)
                        stem='cmps' if op=='fcmps' and behavior!='ignore' else 'cmp'
                        suffix='_rm' if behavior!='ignore' else ''
                        tail=', i32 0' if suffix else ''
                        self.assertIn(f'call i1 @__bennett_sf_{stem}_f64{suffix}(i64 %nz.0.r, i64 %nz.1.r, i32 {p}{tail})',out)
                        self.verify(out,major)

class InstantiationRequest(unittest.TestCase):
    def test_schema_canonicalisation_and_no_width_subset(self):
        import copy,json
        from dialect_arith_request import canonical_request
        entries=[{'op':'powi','base':'f128','exponent_bits':k} for k in (7,8388608,1)]
        entries += [{'op':'convert_to','format':'Float8E3M4','base':'ppcf128'}]
        request=dict(schema='bennett-arith-instantiations-1',llvm_major=23,target_triple='x86_64-unknown-linux-musl',data_layout='e-p:64:64',entries=entries)
        canonical=canonical_request(request)
        shuffled={**request,'entries':list(reversed(entries))+entries}
        self.assertEqual(canonical,canonical_request(shuffled))
        self.assertEqual(4,len(json.loads(canonical)['entries']))
        for bad in (0,8388609,True,'7'):
            value=copy.deepcopy(request);value['entries'][0]['exponent_bits']=bad
            with self.assertRaises(ValueError):canonical_request(value)
        for key,val in (('extra',0),('schema','wrong'),('llvm_major',True)):
            with self.assertRaises(ValueError):canonical_request({**request,key:val})
        wrong=copy.deepcopy(request);wrong['entries'][-1]['format']='custom-p500-e20'
        with self.assertRaises(ValueError):canonical_request(wrong)
        absent=copy.deepcopy(request);absent['llvm_major']=18
        with self.assertRaises(ValueError):canonical_request(absent)

if __name__=='__main__':unittest.main()
