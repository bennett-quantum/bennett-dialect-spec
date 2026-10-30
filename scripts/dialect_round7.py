"""Round-7 source witnesses: independent LLVM verification and native execution."""
import json
import re
import dialect_check as d
from dialect_check_v02 import command, equal, recognise, normalise
from dialect_state import run_native

STATES={'pt5-int-wrap','pt4-wide-wrap','pt6-unknown-address','pt10-lane-zero','n-libm-x86-f128','n-libm-x86-ppcf128','n-libm-arm-ppcf128','n-libm-riscv-ppcf128','libm-invalid-casts'}


def check_state(runner,block):
    name=block['attrs']['state'];want=json.loads(block['body'])
    if name.startswith('n-libm-') or name=='libm-invalid-casts':return check_libm(runner,block)
    if name=='pt10-lane-zero':return check_lanes(runner,want)
    src=runner.block('example',name)['body']
    verdict,a=recognise(d.with_decls(src))
    equal(name,'verdict','accept',verdict)
    equal(name,'candidates',set(want['candidates']),a.first_candidates())
    if name!='pt6-unknown-address':
        if ('tab',0) not in a.ptrs(a.m.funcs['top'],'%p'):raise d.Fail(name+': lost modular identity')
    if not a.candidates(a.m.funcs['top'],'%f'):raise d.Fail(name+': empty load')
    driver='''#include <stdlib.h>
static unsigned calls;
void __bennett_adj(void(*f)(void*),void*b,void*e){if(!f||b||e)abort();f(e);++calls;}
extern void top(void);int main(void){top();printf("[%u,0]\\n",calls);return 0;}'''
    for major in ('18','23'):
        p=runner.tmp/(name+'-'+major+'.ll');p.write_text(src)
        for stage in ('default<O0>','instcombine'):
            ir=command([runner.tc[major]/'opt','-S','-passes='+stage,p,'-o','-'])
            equal(name,stage+' candidates',set(want['candidates']),recognise(ir)[1].first_candidates())
            if name=='pt5-int-wrap' and stage=='instcombine' and not re.search(r'@__bennett_adj\(ptr (?:nonnull )?@body',ir):raise d.Fail(name+': independent fold lost body')
            # O0 native execution is required too; use the host's complete DL for
            # codegen, with identical 64-bit integral-pointer semantics here.
            run_native(runner,name+'-'+major+'-'+stage.replace('<','').replace('>',''),ir,driver,[[want['calls'],want['trap']]])


def check_lanes(runner,want):
    name='pt10-lane-zero';src=runner.block('example',name)['body']
    verdict,a=recognise(d.with_decls(src));f=a.m.funcs['top']
    equal(name,'verdict','accept',verdict)
    equal(name,'lane set',want['lane_set'],sorted(a.ints(f,'%lane')))
    widths=sorted(a.ints(f,'%width'))
    equal(name,'width dispatch',want['value_set'],widths)
    allowed='&&'.join('n!='+str(x) for x in widths)
    calls=''.join(f'top({i});printf("[%llu,%u,%u]\\n",(unsigned long long)width,live,code);' for i in want['inputs'])
    driver='''#include <stdlib.h>
static uint64_t width;static unsigned live,code;
void *__bennett_qalloc(uint64_t cls,uint64_t n){if((ALLOWED)||cls||live)abort();width=n;live=1;return (void*)1;}
void __bennett_qfree(void*h){if(h!=(void*)1||!live)abort();live=0;}
extern void top(uint32_t);
int main(void){CALLS return 0;}'''.replace('ALLOWED',allowed).replace('CALLS',calls)
    for major in ('18','23'):
        p=runner.tmp/(name+'-'+major+'.ll');p.write_text(d.with_decls(src))
        o0=command([runner.tc[major]/'opt','-S','-passes=default<O0>',p,'-o','-'])
        materialised=normalise(o0,major=major)
        run_native(runner,name+'-'+major,materialised,driver,[[w,want['live_after'],want['trap']] for w in want['widths']])

def check_libm(runner,block):
    name=block['attrs']['state'];want=json.loads(block['body'])
    if name=='libm-invalid-casts':
        for major in ('18','23'):
            for arch,src,dst in [('x86_64','fp128','x86_fp80'),('x86_64','ppc_fp128','x86_fp80'),('aarch64','ppc_fp128','fp128'),('riscv64','ppc_fp128','fp128')]:
                p=runner.tmp/('invalid-'+arch+'-'+src+'-'+major+'.ll')
                p.write_text(f'target triple = "{arch}-unknown-linux-gnu"\ndefine {dst} @f({src} %x) {{\n %r = fpext {src} %x to {dst}\n ret {dst} %r\n}}\n')
                import subprocess
                from dialect_check_v02 import headless_env
                result=subprocess.run([runner.tc[major]/'opt','-passes=verify',p,'-disable-output'],env=headless_env(),text=True,capture_output=True,timeout=10)
                equal(name,'verifier exit '+arch,1,result.returncode)
                if want[major] not in result.stderr:raise d.Fail(name+': diagnostic mismatch: '+result.stderr)
                p.with_suffix('.txt').write_text(result.stderr)
        return
    src=runner.block('normalise-in',name)['body'];expected=runner.block('normalise-out',name)['body']
    ty='ppc_fp128' if name.endswith('ppcf128') else 'fp128'
    for major in ('18','23'):
        got=normalise(src,major=major);equal(name,'exact carrier pair',expected,got)
        p=runner.tmp/(name+'-'+major+'.ll')
        for stage,text in [('source',src),('materialised',got)]:
            p.write_text(text)
            command([runner.tc[major]/'opt','-passes=verify',p,'-disable-output'])
            equal(name,stage+' verifier exit',want['verifier'][major],0)
        # Inline the FP transport at the comparison link; then only integer
        # carriers cross the fixture ABI. Verify at the source triple first.
        ir=got.replace('define '+ty+' @f(', 'define internal '+ty+' @f(')
        ir+=f'\ndefine void @probe(ptr %src, ptr %dst) {{\n %a = load i128, ptr %src, align 8\n %x = bitcast i128 %a to {ty}\n %y = call {ty} @f({ty} %x)\n %z = bitcast {ty} %y to i128\n store i128 %z, ptr %dst, align 8\n ret void\n}}\n'
        p.write_text(ir)
        ir=command([runner.tc[major]/'opt','-S','-passes=cgscc(inline),instcombine,globaldce',p,'-o','-'])
        # Host execution of the same integer carrier body, not cross-native code.
        ir=re.sub(r'^target triple = .*\n','',ir,flags=re.M)
        driver='extern void probe(const void*,void*);\nint main(void){uint64_t a[2],r[2];'
        for x,y in want['vectors']:
            value=int(x,16)
            driver+=f'a[0]={value&((1<<64)-1)}ULL;a[1]={value>>64}ULL;probe(a,r);printf("[\\"%016llx%016llx\\",0]\\n",(unsigned long long)r[1],(unsigned long long)r[0]);'
        driver+='return 0;}'
        run_native(runner,name+'-'+major,ir,driver,[[y,want['code']] for x,y in want['vectors']],extra=(d.ROOT/'scripts'/'round7_libm.c','-lquadmath'))
