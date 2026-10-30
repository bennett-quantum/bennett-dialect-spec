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

    def test_canonical_global_numbering(self):
        from dialect_map import Mapper
        b=self.block('lift','atomic-nand')
        link=self.block('linkmap','atomic-nand')['body']
        # The published first global and all interface hashes must follow §16.3.
        self.assertIn('global @cell -> G1 ',link)
        with self.assertRaises(d.Fail):
            Mapper(b['body'],'@f',';tgt=8',link.replace('-> G1 ','-> G0 '))
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'map','hash','run-oracle'})
            from dialect_map import map_object
            map_object(runner,b)
            runner.hashes(self.block('hash','atomic-nand'))
            runner.oracle_run(self.block('run','atomic-nand'))

    def test_round7_pointer_origin(self):
        src='''@slot = internal global ptr null
define void @top() {
 %h = call ptr @__bennett_qalloc(i64 0, i64 1)
 %a = ptrtoint ptr @slot to i64
 %b = add i64 %a, -9223372036854775808
 %c = add i64 %b, -9223372036854775808
 %p = inttoptr i64 %c to ptr
 store ptr %h, ptr %p
 call void @__bennett_qfree(ptr %h)
 ret void
}
'''
        self.assertEqual(v.recognise(d.with_decls(src))[0],'accept')
        self.assertEqual(v.recognise(d.with_decls(src.replace('@slot to i64','%host to i64').replace('@top()','@top(ptr %host)')))[0],'reject:BD-E-HANDLE-ESCAPE')

    def test_round7_fp_formats(self):
        from dialect_normalise import FP
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            for triple in ('x86_64-unknown-linux-gnu','aarch64-unknown-linux-gnu','riscv64-unknown-linux-gnu'):
                D='x86_fp80' if triple.startswith('x86') else 'fp128'
                for ty,(suffix,width) in FP.items():
                    with self.subTest(triple=triple,ty=ty):
                        src=f'target triple = "{triple}"\ndeclare {ty} @llvm.sin.{suffix}({ty})\ndefine {ty} @f({ty} %x) {{\n %r = call {ty} @llvm.sin.{suffix}({ty} %x)\n ret {ty} %r\n}}\n'
                        got=v.normalise(src)
                        if ty in ('float','double',D):
                            name='sinf' if ty=='float' else 'sin' if ty=='double' else 'sinl'
                            self.assertIn(f'call {ty} @{name}({ty} %x)',got)
                        else:self.assertIn(f'call i{width} @__bennett_sf_sin_{suffix}(i{width} %nz.0.r)',got)
                        p=v.Path(tmp)/'fp.ll';p.write_text(got)
                        for major in ('18','23'):v.command([d.toolchains()[major]/'opt','-passes=verify',p,'-disable-output'])
            for op in ('powi','sincos','sincospi','modf'):
                rt='fp128' if op=='powi' else '{ fp128, fp128 }'
                args='fp128, i32' if op=='powi' else 'fp128'
                actual='fp128 %x, i32 3' if op=='powi' else 'fp128 %x'
                src=f'declare {rt} @llvm.{op}.f128({args})\ndefine {rt} @f(fp128 %x) {{\n %r = call {rt} @llvm.{op}.f128({actual})\n ret {rt} %r\n}}\n'
                got=v.normalise(src,major='23')
                self.assertIn('@__bennett_sf_'+op+'_f128',got)
                p=v.Path(tmp)/'fp.ll';p.write_text(got)
                v.command([d.toolchains()['23']/'opt','-passes=verify',p,'-disable-output'])

    def test_round7_fp_execution(self):
        import json
        from dialect_round7 import check_libm
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state'})
            for name in ('n-libm-x86-f128','n-libm-x86-ppcf128','n-libm-arm-ppcf128','n-libm-riscv-ppcf128','libm-invalid-casts'):
                b=self.block('state',name);check_libm(runner,b)
                if name!='libm-invalid-casts':
                    # The fixture link names these definitions. V12 must still
                    # reject the identical call in an actually unlinked module.
                    with self.assertRaises(d.Reject):v.validate(self.block('normalise-out',name)['body'])
                want=json.loads(b['body'])
                if 'vectors' in want:
                    want['vectors'][1][1]='0'*32
                    with self.assertRaises(d.Fail):check_libm(runner,dict(b,body=json.dumps(want)))

    def test_round7_lane_execution(self):
        import json
        from dialect_round7 import check_lanes
        from dialect_native import check
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state','native'})
            b=self.block('state','pt10-lane-zero');want=json.loads(b['body'])
            check_lanes(runner,want)
            with self.assertRaises(d.Fail):check_lanes(runner,dict(want,widths=[2,4,2,1]))
            b=self.block('native','n-constant-lane');check(runner,b)
            with self.assertRaises(d.Fail):check(runner,dict(b,body=b['body'].replace('"f":0','"f":1')))

    def test_round7_lane_domains(self):
        src='''define i64 @top(i32 %index) {
 %v0 = insertelement <2 x i64> zeroinitializer, i64 1, i32 0
 %v1 = insertelement <2 x i64> %v0, i64 3, i32 1
 %lane = extractelement <2 x i64> %v1, i32 %index
 %frozen = freeze i64 %lane
 %width = add i64 %frozen, 1
 ret i64 %width
}
'''
        a=v.Analysis02(d.Module(src));a.analyse();f=a.m.funcs['top']
        self.assertEqual(a.ints(f,'%lane'),{0,1,3})
        self.assertEqual(a.ints(f,'%width'),{1,2,4})
        for index,want in [('0',{1}),('1',{3}),('2',{0}),('-1',{0})]:
            probe=src.replace('i32 %index\n','i32 '+index+'\n')
            a=v.Analysis02(d.Module(probe));a.analyse()
            self.assertEqual(a.ints(a.m.funcs['top'],'%lane'),want)
        # An i1 index cannot select the zero alternative of a two-lane vector.
        a=v.Analysis02(d.Module(src.replace('i32','i1')));a.analyse()
        self.assertEqual(a.ints(a.m.funcs['top'],'%lane'),{1,3})

    def test_round7_constant_lanes(self):
        for idx in ('2','-1'):
            src='define i8 @f() {\n %lane = extractelement <2 x i8> <i8 5, i8 9>, i32 '+idx+'\n %v = freeze i8 %lane\n ret i8 %v\n}\n'
            self.assertIn('ret i8 0',v.normalise(src))
            src='define i8 @g() {\n %v = insertelement <2 x i8> <i8 5, i8 9>, i8 7, i32 '+idx+'\n %f = freeze <2 x i8> %v\n %r = extractelement <2 x i8> %f, i32 0\n ret i8 %r\n}\n'
            self.assertIn('ret i8 5',v.normalise(src))

    def test_round7_pointer_execution(self):
        import json
        from dialect_round7 import check_state, STATES
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state'})
            for name in ('pt5-int-wrap','pt4-wide-wrap','pt6-unknown-address'):
                b=self.block('state',name);check_state(runner,b)
                wrong=json.loads(b['body']);wrong['calls']+=1
                with self.assertRaises(d.Fail):check_state(runner,dict(b,body=json.dumps(wrong)))

    def test_round7_pointer_arithmetic(self):
        src=self.block('example','pt5-int-wrap')['body']
        for wide in (False,True):
            probe=src
            if wide:
                probe=probe.replace('ptr @tab to i64','ptr @tab to i128').replace('%b = add i64 %a, -9223372036854775808','%b = add i128 %a, 18446744073709551616').replace(' %c = add i64 %b, -9223372036854775808\n','').replace('inttoptr i64 %c','inttoptr i128 %b')
            verdict,a=v.recognise(d.with_decls(probe));f=a.m.funcs['top']
            self.assertEqual(verdict,'accept')
            self.assertIn(('tab',0),a.ptrs(f,'%p'))
            self.assertIn('body',a.first_candidates())
        # TOP on an address must survive a load even without an explicit EXT.
        a.values[('top','%p')]={0:frozenset({('P','tab',100),('T',)})}
        load=next(i for i in f.instrs() if i.res=='%f')
        a.values.pop(('top','%f'));a.flow_step(f,load)
        self.assertIn(('T',),a.atoms(f,'%f'))

    def test_round6_atomic_sweep(self):
        # Installed LLVM operation enumerations: all integer forms and all FP
        # min/max variants (23 adds four spellings). No ordinary NAND exists.
        integer='xchg add sub and nand or xor max min umax umin uinc_wrap udec_wrap usub_cond usub_sat'.split()
        floating='fadd fsub fmax fmin fmaximum fminimum fmaximumnum fminimumnum'.split()
        for op in integer+floating:
            with self.subTest(op=op):
                ty='float' if op in floating else 'i32'
                src=f'define {ty} @f(ptr %p, {ty} %v) {{\n %old = atomicrmw {op} ptr %p, {ty} %v seq_cst, align 4\n ret {ty} %old\n}}\n'
                got=v.normalise(src,major='23')
                self.assertNotIn('atomicrmw',got)
                with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
                    p=v.Path(tmp)/'atomic.ll';p.write_text(got)
                    v.command([d.toolchains()['23']/'opt','-passes=verify',p,'-disable-output'])

    def test_round6_execution(self):
        import json
        from dialect_round6 import check_state
        from dialect_native import check
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state','native'})
            for name in ('pt2-wrap','pt5-range','pt5-range-load','budget-stage'):
                b=self.block('state',name);check_state(runner,b)
                wrong=json.loads(b['body'])
                key='calls' if name=='pt2-wrap' else 'width' if name.startswith('pt5') else 'final_sstack'
                wrong[key]+=1
                with self.assertRaises(d.Fail):check_state(runner,dict(b,body=json.dumps(wrong)))
            b=self.block('native','n-atomic-nand');check(runner,b)
            with self.assertRaises(d.Fail):check(runner,dict(b,body=b['body'].replace('f()=63','f()=62')))

    def test_round6_budget_staging(self):
        from dialect_meta import stage_budget
        table={'version':'0.2','defaults':{'sstack':'16'},'entries':[{'identity':'H16','sstack':'32'},{'symbol':'unused','heap':'2000000'}]}
        calls=[]
        def build(values,caps):
            calls.append((values,caps))
            return 'object'+str(values['sstack']),'H'+str(values['sstack'])
        obj,record=stage_budget(table,'f',build)
        self.assertEqual((record['selection_identity'],record['identity'],record['resolved']['sstack']),('H16','H32',32))
        self.assertEqual(obj,'object32')
        self.assertEqual(len(calls),2)
        self.assertEqual(calls[0][1],calls[1][1])
        self.assertEqual(record['capacities']['heap'],2000000)
        # Steps affect token selection but not the object. Region key precedes symbol.
        table['entries']=[{'identity':'H16','steps':'7'},{'region_key':'K','depth':'5'},{'symbol':'f','depth':'6'}]
        _,r=stage_budget(table,'f',build,region_key='K')
        self.assertEqual((r['identity'],r['resolved']['steps'],r['resolved']['depth']),('H16',7,5))

    def test_round6_wrapped_gep(self):
        src=self.block('example','pt2-wrap')['body']
        verdict,a=v.recognise(d.with_decls(src))
        self.assertEqual(verdict,'accept')
        f=a.m.funcs['top']
        self.assertEqual(a.ptrs(f,'%p'),{('tab',0)})
        self.assertEqual(a.atoms(f,'%f'),frozenset({('F','body')}))
        self.assertEqual(set().union(*a.cands.values()),{'body'})
        # Scaling, signed small indices and constant expressions use the same wrap.
        for ty,idx in [('i8','i64 4294967296'),('i16','i64 2147483648'),('i8','i8 -1')]:
            probe=src.replace('i8, ptr @tab, i64 4294967296',ty+', ptr @tab, '+idx)
            _,a=v.recognise(d.with_decls(probe))
            if idx=='i8 -1':self.assertIn(('EXT','*'),a.ptrs(a.m.funcs['top'],'%p'))
            else:self.assertEqual(a.ptrs(a.m.funcs['top'],'%p'),{('tab',0)})

    def test_round6_gep_constant_expression(self):
        src=self.block('example','pt2-wrap')['body']
        src=src.replace(' %p = getelementptr i8, ptr @tab, i64 4294967296\n','').replace('ptr %p,','ptr getelementptr (i8, ptr @tab, i64 4294967296),')
        # Source has a single-space indent; this exact transformation is checked.
        self.assertNotIn('%p =',src)
        verdict,a=v.recognise(d.with_decls(src))
        self.assertEqual((verdict,a.first_candidates()),('accept',{'body'}))
        # Actual host-origin pointer stores retain the existing prohibition.
        host='define void @f(ptr %p) {\n %h = call ptr @__bennett_qalloc(i64 0, i64 1)\n %q = getelementptr i8, ptr %p, i64 8\n store ptr %h, ptr %q\n ret void\n}\n'
        self.assertEqual(v.recognise(d.with_decls(host))[0],'reject:BD-E-HANDLE-ESCAPE')

    def test_round6_gep_residue_offset(self):
        # A struct displacement before an unknown sequential index must survive
        # residue-class formation; dropping it loses the second field's values.
        src='@tab = internal global {i64, [2 x {i64,i64}]} zeroinitializer\ndefine ptr @f(i64 %i) {\n %p = getelementptr {i64, [2 x {i64,i64}]}, ptr @tab, i64 0, i32 1, i64 %i\n ret ptr %p\n}\n'
        a=v.Analysis02(d.Module(src));a.analyse()
        offsets=a.ptrs(a.m.funcs['f'],'%p')
        self.assertIn(('tab',8),offsets)
        self.assertIn(('tab',24),offsets)
        self.assertIn(('EXT','*'),offsets)

    def test_round6_removed_range(self):
        src='define i64 @f(i64 range(i64 1, 2) %n) {\n %m = and i64 %n, 3\n %w = or i64 %m, 1\n ret i64 %w\n}\n'
        a=v.Analysis02(d.Module(src));a.analyse()
        self.assertEqual(a.ints(a.m.funcs['f'],'%w'),{1,3})
        self.assertNotIn('range(',v.normalise(src,major='23'))

    def test_round6_nand(self):
        src='define i8 @f(ptr %p, i8 %v) {\n %old = atomicrmw nand ptr %p, i8 %v seq_cst, align 1\n ret i8 %old\n}\n'
        got=v.normalise(src)
        self.assertIn('%nz.a.old = and i8 %nz.l.old, %v',got)
        self.assertIn('%nz.v.old = xor i8 %nz.a.old, -1',got)
        self.assertIn('ret i8 %nz.l.old',got)

    def test_round5_pointer_width(self):
        from dialect_map import Mapper
        source='target datalayout = "e-p:64:64-p270:32:32"\ndefine i64 @f(i64 %x) {\n %p = inttoptr i64 %x to ptr addrspace(270)\n %r = ptrtoint ptr addrspace(270) %p to i64\n ret i64 %r\n}\n'
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            path=v.Path(tmp)/'p.bisa';isa=v.Interpreter()
            obj=Mapper(source,'@f','ARG(64);tgt=64','null_size=4096 heap_base=4096 heap_limit_max=0 stack max 32').run(isa,path)
            self.assertIn('lift.trunc.i32 a0',obj)
            path.write_text(obj)
            for x,want in ((4294967296,0),(4294967297,1)):
                got=isa.call('run-oracle',path,'ref','--input','','--arg',str(x),'--budget','100,0,32,8')
                self.assertEqual((got['payload'],got['code']),(want,0))

    def test_round5_gep_rows(self):
        from dialect_map import map_object
        row=self.spec.split('### 16.4 Rows',1)[1].split('**Edge moves**',1)[0]
        self.assertIn('For I<P always emit recombination',row)
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'map'})
            for name in ('gep-index-obj','gep-index-const','pointer-as270'):
                map_object(runner,self.block('lift',name))
                runner.hashes(self.block('hash',name))
                runner.oracle_run(self.block('run',name))
            self.assertIn('For I<P always emit recombination',self.spec)
            b=self.block('lift','gep-index-obj')
            with self.assertRaises(d.Fail):map_object(runner,dict(b,body=b['body'].replace('getelementptr i8','getelementptr i16')))

    def test_round5_parameter_liveness(self):
        src=self.block('example','handle-param-cross-entry')['body']
        self.assertEqual(v.recognise(d.with_decls(src))[0],'blocked:BD-B-ISA4')
        freed=src.replace('  store ptr %h, ptr %p','  store ptr %h, ptr %p\n  call void @__bennett_qfree(ptr %h)',1)
        self.assertEqual(v.recognise(d.with_decls(freed))[0],'accept')
        rin=src.replace('define void @stash(ptr %h) {\nentry:', 'define internal void @stash(ptr %env) {\nentry:\n  %h = load ptr, ptr %env')+'\ndefine void @launch(ptr %h) {\n %env = alloca ptr\n store ptr %h, ptr %env\n call void @__bennett_reversible(ptr @stash, ptr null, ptr %env)\n ret void\n}\n'
        _,ra=v.recognise(d.with_decls(rin))
        self.assertTrue(any(code=='BD-B-ISA12' and 'parameter' in reason for code,reason in ra.blockers))
        direct='define void @f(ptr %h) {\n call void @__bennett_gate(i32 1, ptr %h, i64 0)\n ret void\n}\n'
        self.assertEqual(v.recognise(d.with_decls(direct))[0],'accept')
        result='define ptr @make() {\n %s = alloca ptr\n %h = call ptr @__bennett_qalloc(i64 0, i64 1)\n store ptr %h, ptr %s\n %r = load ptr, ptr %s\n ret ptr %r\n}\n'
        self.assertEqual(v.recognise(d.with_decls(result))[0],'blocked:BD-B-ISA4')

    def test_round5_memory_intervals(self):
        for name,want,verdict in (('pt6-byte-width',{257},'accept'),('pt6-subrange','TOP','blocked:BD-B-ISA4')):
            src=self.block('example',name)['body'];got,a=v.recognise(d.with_decls(src))
            self.assertEqual(a.ints(a.m.funcs['top'],'%n'),want)
            self.assertEqual(got,verdict)
        # A partial write/copy must invalidate the exact larger atom.
        src='define i32 @f() {\n %p = alloca i32\n store i32 1, ptr %p\n store i8 2, ptr %p\n %r = load i32, ptr %p\n ret i32 %r\n}\n'
        a=v.Analysis02(d.Module(src));a.analyse()
        self.assertEqual(a.ints(a.m.funcs['f'],'%r'),'TOP')
        copied='declare void @llvm.memcpy.p0.p0.i64(ptr,ptr,i64,i1)\ndefine i32 @f() {\n %p = alloca i32\n %q = alloca i32\n store i32 66049, ptr %p\n store i32 0, ptr %q\n %s = getelementptr i8, ptr %p, i64 1\n call void @llvm.memcpy.p0.p0.i64(ptr %q, ptr %s, i64 2, i1 false)\n %r = load i32, ptr %q\n ret i32 %r\n}\n'
        a=v.Analysis02(d.Module(copied));a.analyse()
        self.assertEqual(a.ints(a.m.funcs['f'],'%r'),'TOP')

    def test_round5_atomic_forms(self):
        for op in ('uinc_wrap','udec_wrap','usub_cond','usub_sat'):
            src='define i32 @f(ptr %p, i32 %v) {\n %old = atomicrmw '+op+' ptr %p, i32 %v seq_cst, align 4\n ret i32 %old\n}\n'
            got=v.normalise(src,major='23')
            self.assertNotIn('atomicrmw',got)
            self.assertIn('select i1',got)

    def test_round5_fp_wide(self):
        for op,ty,result in (('sitofp','i192','double'),('fptosi','double','i192')):
            val='%a' if ty=='double' else '%v'
            src='define void @f(ptr %p, ptr %q, double %a) {\n %v = load i192, ptr %p\n %r = '+op+' '+ty+' '+val+' to '+result+'\n store '+result+' %r, ptr %q\n ret void\n}\n'
            got=v.normalise(src)
            self.assertIn('__bennett_sf_'+op+'_f64_wide',got)
            self.assertNotIn('i192',got)

    def test_round5_wide_intrinsics(self):
        src='declare i192 @llvm.ctpop.i192(i192)\ndefine void @f(ptr %p, ptr %q) {\n %a = load i192, ptr %p\n %r = call i192 @llvm.ctpop.i192(i192 %a)\n store i192 %r, ptr %q\n ret void\n}\n'
        got=v.normalise(src)
        self.assertIn('__bennett_rt_i192_ctpop',got)
        self.assertNotIn('call i192',got)

    def test_round5_execution(self):
        import json
        from dialect_native import check
        from dialect_round5 import check_state
        from dialect_round4 import check_state as check_handle
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'native','state'})
            for name in ('n-fpconv-wide','n-wide-intrinsics','n-atomic-wrap','n-atomic-usub','pointer-as270'):
                b=self.block('native',name);check(runner,b)
                before,after={
                    'n-fpconv-wide':('=5183643171103440896','=5183643171103440897'),
                    'n-wide-intrinsics':('=[0,1,0,0]','=[0,2,0,0]'),
                    'n-atomic-wrap':('[9,10]','[9,11]'),
                    'n-atomic-usub':('[9,9]','[9,8]'),
                    'pointer-as270':('f(4294967296)=0','f(4294967296)=1'),
                }[name]
                wrong=b['body'].replace(before,after)
                # A well-formed wrong expected result must fail execution.

                with self.assertRaises(d.Fail):check(runner,dict(b,body=wrong))
            for name in ('pt6-byte-width','pt6-subrange','handle-param-cross-entry'):
                b=self.block('state',name);fn=check_handle if name.startswith('handle') else check_state
                fn(runner,b);wrong=json.loads(b['body']);wrong['live_after']=1
                with self.assertRaises(d.Fail):fn(runner,dict(b,body=json.dumps(wrong)))

    def test_round5_pointer_storage(self):
        from dialect_map import Mapper
        source='target datalayout = "e-p:64:64-p270:32:32"\ndefine i64 @f(ptr %p, i64 %x) {\n %a = inttoptr i64 %x to ptr addrspace(270)\n store ptr addrspace(270) %a, ptr %p\n %b = load ptr addrspace(270), ptr %p\n %r = ptrtoint ptr addrspace(270) %b to i64\n ret i64 %r\n}\n'
        mapper=Mapper(source,'@f','MEM_IN(3),ARG(64);tgt=64','null_size=4096 heap_base=4096 heap_limit_max=0 stack max 32')
        self.assertEqual(mapper.size(d.parse_type('{ptr addrspace(270), i32}')[0]),8)
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            p=v.Path(tmp)/'storage.bisa';isa=v.Interpreter();obj=mapper.run(isa,p);p.write_text(obj)
            self.assertIn('lift.load.i32',obj);self.assertIn('lift.store.i32',obj)
            got=isa.call('run-oracle',p,'ref','--input','','--arg','4294967297','--mem','m0=00000000aaaaaaaa','--budget','100,0,32,8')
            self.assertEqual((got['payload'],got['code']),(1,0))

    def test_round4_cross_entry(self):
        ir=self.block('example','handle-cross-entry')['body']
        verdict,a=v.recognise(d.with_decls(ir))
        self.assertEqual(verdict,'blocked:BD-B-ISA4')
        self.assertNotIn('put%h',a.instance_bounds)
        self.assertTrue(any('entry' in reason for _,reason in a.blockers))
        # Exact free before return prevents cross-entry accumulation.
        freed=ir.replace('  store ptr %h, ptr %p','  store ptr %h, ptr %p\n  call void @__bennett_qfree(ptr %h)',1)
        self.assertEqual(v.recognise(d.with_decls(freed))[0],'accept')
        r=ir.replace('define void @put()','define internal void @put(ptr %env)')+'\ndefine void @launch() {\n call void @__bennett_reversible(ptr @put, ptr null, ptr null)\n ret void\n}\n'
        _,a=v.recognise(d.with_decls(r))
        self.assertTrue(any(code=='BD-B-ISA12' and 'entry' in reason for code,reason in a.blockers))
        from dialect_round4 import check_state
        import json
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state'})
            b=self.block('state','handle-cross-entry');check_state(runner,b)
            wrong=json.loads(b['body']);wrong['distinct']=False
            with self.assertRaises(d.Fail):check_state(runner,dict(b,body=json.dumps(wrong)))

    def test_round4_narrow_lane(self):
        self.assertEqual(d.collapse(v.normalise(self.block('normalise-in','n-narrow-lane')['body'])),
                         d.collapse(self.block('normalise-out','n-narrow-lane')['body']))

    def test_round4_packed_store(self):
        # Exercise the shared store path at a sub-byte boundary as well as i24.
        source='define void @s(ptr %p) {\n store <8 x i1> <i1 1,i1 0,i1 0,i1 0,i1 0,i1 0,i1 0,i1 1>, ptr %p, align 1\n ret void\n}\n'
        from dialect_state import run_native
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state'})
            driver='extern void s(void*);int main(void){uint8_t p[8]={0,170};s(p);printf("[%u,%u]\\n",p[0],p[1]);return 0;}'
            for name,ir in (('source',source),('materialised',v.normalise(source))):
                run_native(runner,'packed-store-'+name,ir,driver,[[129,170]])

    def test_round4_vector_memory(self):
        self.assertEqual(d.collapse(v.normalise(self.block('normalise-in','n-vector-i24')['body'])),
                         d.collapse(self.block('normalise-out','n-vector-i24')['body']))

    def test_round4_gep_index(self):
        from dialect_round4 import check_state
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state'})
            check_state(runner,self.block('state','n-gep-index'))
            b=self.block('state','n-gep-index')
            with self.assertRaises(d.Fail):check_state(runner,dict(b,body=b['body'].replace('8589934591,1,4294967296','8589934591,1,8589934592')))

    def test_round4_subtraction(self):
        self.assertEqual(d.collapse(v.normalise(self.block('normalise-in','n-wide-sub')['body'])),
                         d.collapse(self.block('normalise-out','n-wide-sub')['body']))

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

    def test_round3_observe_store(self):
        from dialect_round3 import check_state
        import json
        value={'after_first':[2,1], 'after_store':[2,1,9,9], 'after_second':[0,9,2,0,0], 'load':[9,0], 'event_invalidates':True, 'unobserved_store':4}
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state'})
            b={'attrs':{'state':'co-observe-write-observe','at':'0'},'body':json.dumps(value)}
            check_state(runner,b)
            value['load']=[0,4]
            with self.assertRaises(d.Fail):check_state(runner,dict(b,body=json.dumps(value)))

    def test_round3_interprocedural_setjmp(self):
        ir='''@jb = global [256 x i8] zeroinitializer
@slots = global [2 x ptr] zeroinitializer
declare i32 @setjmp(ptr)
declare void @longjmp(ptr, i32)
define internal void @deep(i32 %i) {
entry:
 %first = icmp eq i32 %i, 0
 br i1 %first, label %jump, label %done
jump:
 call void @longjmp(ptr @jb, i32 1)
 unreachable
done:
 ret void
}
define internal void @G(i32 %i) {
entry:
 %h = call ptr @__bennett_qalloc(i64 0, i64 1)
 %p = getelementptr [2 x ptr], ptr @slots, i32 0, i32 %i
 store ptr %h, ptr %p
 call void @deep(i32 %i)
 ret void
}
define void @P() {
entry:
 %r = call i32 @setjmp(ptr @jb)
 call void @G(i32 %r)
 %h0 = load ptr, ptr @slots
 %p1 = getelementptr [2 x ptr], ptr @slots, i32 0, i32 1
 %h1 = load ptr, ptr %p1
 call void @__bennett_qfree(ptr %h0)
 call void @__bennett_qfree(ptr %h1)
 ret void
}
'''
        verdict,a=v.recognise(d.with_decls(ir))
        self.assertEqual(verdict,'blocked:BD-B-ISA4')
        from dialect_bounds import setjmp_reentry
        f=a.m.funcs['G'];site=next(i for i in f.instrs() if '@__bennett_qalloc' in i.text)
        self.assertTrue(setjmp_reentry(f,site,a))
        # No setjmp, no exceptional re-entry: the ordinary finite bound survives.
        self.assertEqual(v.recognise(d.with_decls(ir.replace('%r = call i32 @setjmp(ptr @jb)','%r = add i32 0, 0')))[0],'accept')


    def test_round3_stack_liveness(self):
        from dialect_round3 import check_state
        import json
        value={'live':[7,0], 'popped':[0,7], 'spanning':[0,7], 'padding':[0,7], 'restored':[0,7], 'wrap':[0,7], 'replay':[7,0], 'store_unchanged':True}
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state'})
            b={'attrs':{'state':'shadow-stack-liveness','at':'0'},'body':json.dumps(value)}
            check_state(runner,b)
            value['popped']=[7,0]
            with self.assertRaises(d.Fail):check_state(runner,dict(b,body=json.dumps(value)))

    def test_round3_stale_generation(self):
        from dialect_round3 import check_state
        import json
        value={'physical_slots':1,'equal':False,'stale_code':4,'second_value':0,'live_after':0}
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state'})
            b={'attrs':{'state':'handle-stale-generation','at':'0'},'body':json.dumps(value)}
            check_state(runner,b)
            value['stale_code']=0
            with self.assertRaises(d.Fail):check_state(runner,dict(b,body=json.dumps(value)))

    def test_round3_empty_oracle(self):
        from dialect_map import Mapper
        link='null_size=4096 heap_base=4096 heap_limit_max=0 globals=none budget-table: stack max 32, heap max 0'
        for ret,body in (('void','ret void'),('void','call void @__bennett_nz_fault(i64 4)\n unreachable'),('i8','ret i8 255')):
            mapper=Mapper(d.with_decls('define '+ret+' @f() {\n '+body+'\n}\n'),'@f','tgt=null',link)
            wrapper=mapper.wrapper()
            self.assertIn('p0 = lift.const.i1 0\nlift.retval p0',wrapper)
            self.assertEqual(mapper.signatures['ref']['tgt'],1)
            self.assertEqual(mapper.signatures['ref']['fault'],4)
        from dialect_round3 import check_state
        import json
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            runner=v.Runner(self.blocks,self.spec,tmp,{'state'})
            value={'success':[0,0],'fault':[0,4],'zero_budget':[0,1],'hidden_clean':True,'oracle_calls':1}
            b={'attrs':{'state':'oracle-empty-output','at':'0'},'body':json.dumps(value)}
            check_state(runner,b)
            for field,wrong in (('fault',[0,0]),('zero_budget',[0,0]),('hidden_clean',False),('oracle_calls',2)):
                with self.subTest(field=field),self.assertRaises(d.Fail):
                    check_state(runner,dict(b,body=json.dumps(dict(value,**{field:wrong}))))

    def test_native_fault_probe_disables_core_dump(self):
        from dialect_native import fault_probe
        import signal
        import sys
        from pathlib import Path
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            probe=Path(tmp)/'fault-probe'
            probe.write_text('#!'+sys.executable+'\nimport os, resource, signal\n'
                             'assert resource.getrlimit(resource.RLIMIT_CORE) == (0, 0)\n'
                             'os.kill(os.getpid(), signal.SIGILL)\n')
            probe.chmod(0o700)
            self.assertEqual(fault_probe(probe).returncode,-signal.SIGILL)

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
        good='define void @f() {\n ret void\n}\n!llvm.module.flags = !{!0}\n!0 = !{i32 1, !"bennett.dialect", !"0.2.9"}\n'
        self.assertEqual(v.recognise(good)[0],'accept')
        for stale in ('0.2.8','0.2.7','0.2.6','0.2.5','0.2.4','0.2.3','0.2.1'):
            self.assertEqual(v.recognise(good.replace('0.2.9',stale))[0],'reject:BD-E-VERSION')
        import tomllib
        self.assertEqual(tomllib.loads((d.ROOT/'SPEC_VERSIONS.toml').read_text())['dialect'],'0.2.9')
        self.assertIn('**full version string** (`0.2.9`)',self.spec)

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
