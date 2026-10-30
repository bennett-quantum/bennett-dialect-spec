"""Round-7 source witnesses: independent LLVM verification and native execution."""
import json
import re
import dialect_check as d
from dialect_check_v02 import command, equal, recognise, normalise
from dialect_state import run_native

STATES={'pt5-int-wrap','pt4-wide-wrap','pt6-unknown-address','pt10-lane-zero'}


def check_state(runner,block):
    name=block['attrs']['state'];want=json.loads(block['body'])
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
