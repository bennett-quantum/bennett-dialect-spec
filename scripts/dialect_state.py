"""Executable boundary microvectors; expectations never construct observations."""
import json
import re
import dialect_check as d
from dialect_check_v02 import command, equal, normalise, recognise, validate
from dialect_native import PREFIX, SEEDS


NATIVE_STATES={'normalisation-boundaries','fcmp-abi','fp-sign-carrier','inplace-bound','r-fault-code','partial-observe','classical-event-application','sv39-kernel-alias'}


def run_native(runner, name, ir, driver, expected, extra=()):
    directory=runner.tmp/('state-'+name);directory.mkdir(exist_ok=True)
    src=directory/'case.ll';src.write_text(d.with_decls(ir))
    main=directory/'driver.c';main.write_text(PREFIX+driver)
    for major in ('18','23'):
        exe=directory/('case-'+major)
        command([runner.frontends[major]/'clang','-O2',src,main,SEEDS/'runtime.c',SEEDS/'softfloat.c',*extra,'-o',exe])
        got=[json.loads(line) for line in command([exe]).strip().splitlines()]
        equal(name+'/clang'+major,'boundary execution',expected,got)


def budget_admissible(sample, bound, budget, exhaustive=False):
    """§8.7: a sample is a lower bound; admission requires a universal bound."""
    required=sample if exhaustive else bound
    if required is None: return False
    if any(s>b for s,b in zip(sample,required)):
        raise d.Fail('§8.7 declared bound below observed sample')
    return all(b>=r for b,r in zip(budget,required))


def check_native_state(runner, block):
    name=block['attrs']['state'];text=block['body']
    if name=='fcmp-abi':
        calls=re.findall(r'__bennett_sf_cmp_f64\((0x[0-9a-f]+),(0x[0-9a-f]+),(\d+)\)=(\d+)',text)
        if not calls:raise d.Fail('fcmp ABI: no vectors')
        driver='extern uint8_t __bennett_sf_cmp_f64(uint64_t,uint64_t,uint32_t);\nint main(void){'
        for a,b,p,_ in calls:driver+=f'printf("%d\\n",__bennett_sf_cmp_f64({a}ULL,{b}ULL,{p}));'
        run_native(runner,name,'',driver+'return 0;}\n',[int(w) for _,_,_,w in calls])
    elif name=='fp-sign-carrier':
        m=re.search(r'(0x[0-9a-f]+) xor (0x[0-9a-f]+) = (0x[0-9a-f]+)',text)
        if not m:raise d.Fail('fneg vector syntax')
        ir='define i64 @neg(double %x) {\n %n = fneg double %x\n %r = bitcast double %n to i64\n ret i64 %r\n}\n'
        driver=f'extern uint64_t neg(double);\nint main(void){{uint64_t b={m[1]}ULL;double x;memcpy(&x,&b,8);printf("%llu\\n",(unsigned long long)neg(x));return 0;}}'
        run_native(runner,name,ir,driver,[int(m[3],16)])
    elif name=='r-fault-code':
        b=runner.block('example',name)
        got,info=recognise(d.with_decls(b['body']),materialised=True)
        want=re.search(r'status=(blocked:[^;\s]+)',text)[1]
        equal(name,'BLK-5 ISA-7',want,got)
        equal(name,'required typed code',int(re.search(r'required code=(\d+)',text)[1]),int(re.search(r'__bennett_nz_fault\(i64 (\d+)\)',b['body'])[1]))
        if not any('ISA-7' in reason for _,reason in info.blockers):raise d.Fail('ISA-7 reason missing')
    elif name=='inplace-bound':
        sample=int(re.search(r'B_sample=(\d+)',text)[1]);bound=int(re.search(r'B_bound=(\d+)',text)[1]);budget=int(re.search(r'budget=(\d+)',text)[1])
        equal(name,'§8.7 sampled admission',False,budget_admissible((sample,),(bound,),(budget,)))
        equal(name,'§8.7 universal admission',True,budget_admissible((sample,),(bound,),(bound,)))
    elif name in ('partial-observe','classical-event-application'):
        decl='#include "'+str(SEEDS/'coherence.c')+'"\n'
        if name=='partial-observe':
            driver=decl+'''int main(void){struct bennett_seed_object o={.size=2,.k=2};o.arena[0]=1;o.arena[1]=2;unsigned char out[32];unsigned widths[2];
+bennett_seed_observe(&o,0,1,out,widths);printf("[%u,%u,%u,%u]\\n",out[0],o.arena[0],o.arena[1],o.k);
+bennett_seed_observe(&o,1,1,out,widths);printf("[%u,%u,%u,%u,%u]\\n",o.shadow[0],o.shadow[1],o.arena[0],o.arena[1],o.k);
+struct bennett_seed_object p={.size=17,.k=2};size_t chunks=bennett_seed_observe(&p,0,17,out,widths);printf("[%zu,%u,%u]\\n",chunks,widths[0],widths[1]);return 0;}'''.replace('\n+','\n')
            widths=[int(x) for x in re.search(r'chunk widths=\[([^]]+)\]',text)[1].split(',')]
            expected=[[1,1,2,2],[1,2,0,0,0],[len(widths),*widths]]
        else:
            driver=decl+'''int main(void){struct bennett_seed_object o={.size=1};o.shadow[0]=3;bennett_seed_mask(&o,0,3^5,0);
+printf("[%u,%u,%u]\\n",o.shadow[0],o.arena[0],o.k);bennett_seed_materialise(&o);o.arena[0]+=3;o.k=2;
+unsigned char out[1];unsigned widths[1];bennett_seed_observe(&o,0,1,out,widths);printf("[%u,%u,%u,%u]\\n",out[0],o.shadow[0],o.arena[0],o.k);return 0;}'''.replace('\n+','\n')
            expected=[[int(re.search(r'apply -> shadow=([0-9a-f]+)',text)[1],16),0,0],[8,8,0,0]]
        run_native(runner,name,'',driver,expected)
    elif name=='sv39-kernel-alias':
        v=int(re.search(r'V=(0x[0-9a-f]+)',text)[1],16);p=int(re.search(r'P=(0x[0-9a-f]+)',text)[1],16)
        before=int(re.search(r'holds (0x[0-9a-f]+)',text)[1],16);after=int(re.search(r'store (0x[0-9a-f]+)',text)[1],16)
        driver='#include "'+str(SEEDS/'coherence.c')+'"\n'+f'''int main(void){{uint64_t tables[3][512]={{0}},saved[3][512];uint64_t v={v}ULL,p={p}ULL;
+tables[0][(v>>30)&511]=(2ULL<<10)|1;tables[1][(v>>21)&511]=(3ULL<<10)|1;tables[2][(v>>12)&511]=((p>>12)<<10)|199;
+memcpy(saved,tables,sizeof tables);unsigned char ram={before},old=ram;uint64_t a=bennett_seed_sv39(v,(8ULL<<60)|1,tables,1);
+if(a!=p)abort();ram={after};uint64_t b=bennett_seed_sv39(v,(8ULL<<60)|1,tables,0);printf("[%llu,%u,%u]\\n",(unsigned long long)a,ram,b==p?ram:0);
+ram=old;memcpy(tables,saved,sizeof tables);printf("[%u,%u,%d]\\n",ram,bennett_seed_sv39(v,(8ULL<<60)|1,tables,0)==p?ram:0,memcmp(tables,saved,sizeof tables)==0);return 0;}}'''.replace('\n+','\n')
        run_native(runner,name,'',driver,[[p,after,after],[before,before,1]])
    elif name=='normalisation-boundaries':
        # Execute the normaliser's actual generated IR, including one-byte packed
        # access, partial-limb carry/sign extension, GC provenance and frame size.
        ir='''declare i64 @llvm.experimental.gc.get.pointer.offset.p0.i64(ptr)
define i1 @lane(ptr %p) {
 %v = load <8 x i1>, ptr %p, align 1
 %r = extractelement <8 x i1> %v, i64 7
 ret i1 %r
}
define void @carry(ptr %p, ptr %q) {
 %v = load i129, ptr %p, align 1
 %r = add i129 %v, 1
 store i129 %r, ptr %q, align 1
 ret void
}
define void @sign(ptr %p, ptr %q) {
 %v = load i129, ptr %p, align 1
 %r = sext i129 %v to i256
 store i256 %r, ptr %q, align 1
 ret void
}
define i64 @offset(ptr %b) {
 %p = getelementptr i8, ptr %b, i64 8
 %r = call i64 @llvm.experimental.gc.get.pointer.offset.p0.i64(ptr %p)
 ret i64 %r
}
define void @frame() {
 %p = alloca [24 x i8], align 16
 ret void
}
'''
        got=normalise(ir);validate(got)
        expected_frame=int(re.search(r'N24:.*?S=.*?=(\d+);',text)[1])
        equal(name,'N24 rounded frame',expected_frame,int(re.search(r'ss_push\(i64 (\d+)',got)[1]))
        # The textual form has no alignment premise allowing an overread.
        equal(name,'N21 packed access count',1,len(re.findall('load i8,',d.extract_function(d.Module(got),'lane'))))
        expected_lane=int(re.search(r'extract lane 7 -> (\d+)',text)[1])
        limbs=[int(x,16) for x in re.search(r'add i129.*?limbs=\[([^]]+)\]',text)[1].split(',')]
        sign=[int(x,16) for x in re.search(r'sext i129.*?limbs=\[([^]]+)\]',text)[1].split(',')]
        driver='''extern _Bool lane(const void*);extern void carry(const void*,void*),sign(const void*,void*);extern uint64_t offset(void*);
int main(void){unsigned char p[17],r[32]={0};memset(p,255,16);p[16]=0;
unsigned char b=128;printf("%d\\n",lane(&b));carry(p,r);uint64_t a,c;memcpy(&a,r,8);memcpy(&c,r+8,8);printf("[%llu,%llu,%u]\\n",(unsigned long long)a,(unsigned long long)c,r[16]);
p[16]=1;sign(p,r);printf("[");for(int i=0;i<4;i++){memcpy(&a,r+8*i,8);printf("%s%llu",i?",":"",(unsigned long long)a);}puts("]");printf("%llu\\n",(unsigned long long)offset(p));return 0;}
'''
        run_native(runner,name,got,driver,[expected_lane,limbs,sign,8])
        # PT2/PT6: the declared array dimension must not exclude element 1
        # of the underlying allocation, and mutable initialisers seed the fixpoint.
        for body,want in [
            ('@cb = global ptr @f\n',{'f'}),
            ('@tab = global [2 x ptr] [ptr @f, ptr @g]\n',{'g'})]:
            pointer='@cb' if '@cb' in body else '%p'
            addr='' if pointer=='@cb' else ' %p = getelementptr [1 x ptr], ptr @tab, i64 0, i64 1\n'
            source=body+'define void @f(ptr %e) {\n ret void\n}\ndefine void @g(ptr %e) {\n ret void\n}\ndefine void @top(){\n'+addr+' %f = load ptr, ptr '+pointer+'\n call void @__bennett_adj(ptr %f, ptr null, ptr null)\n ret void\n}\n'
            verdict,analysis=recognise(d.with_decls(source));equal(name,'PT2/PT6 verdict','accept',verdict);equal(name,'PT2/PT6 candidates',want,analysis.first_candidates())
    else:raise d.Fail('unimplemented native state adapter '+name)
