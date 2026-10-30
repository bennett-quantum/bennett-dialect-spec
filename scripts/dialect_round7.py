"""Round-7 source witnesses: independent LLVM verification and native execution."""
import json
import re
import dialect_check as d
from dialect_check_v02 import command, equal, recognise
from dialect_state import run_native

STATES={'pt5-int-wrap','pt4-wide-wrap','pt6-unknown-address'}


def check_state(runner,block):
    name=block['attrs']['state'];want=json.loads(block['body'])
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
