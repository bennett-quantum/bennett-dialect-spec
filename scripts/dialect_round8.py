"""Round-8 DB/DN/DS witnesses: observed native widths must belong to S2."""
import json
import re
import dialect_check as d
from dialect_check_v02 import command, equal, recognise, normalise
from dialect_native import PREFIX, SEEDS

STATES={'pt3-pack257','pt3-pack256','pt3-unpack'}


def domains(name,ir,want,exact=True):
    verdict,a=recognise(d.with_decls(ir));f=a.m.funcs['top']
    equal(name,'admission','accept',verdict)
    if exact:
        for val,values in want['domains'].items():
            equal(name,'scalar AV '+val,{0:frozenset(('I',x) for x in values)},a.av(f,val))
    call=next(c for i,c,mk in a.marker_calls(f) if mk=='qalloc')
    equal(name,'dispatch domain',set(want['value_set']),a.ints(f,call['args'][1][2]))


def check_state(runner,block):
    name=block['attrs']['state'];want=json.loads(block['body'])
    src=d.with_decls(runner.block('example',name)['body']);domains(name,src,want)
    allowed='&&'.join('n!='+str(x) for x in want['value_set'])
    calls='top();'
    driver=PREFIX+"""#include <stdlib.h>
static uint64_t width,gate_index;static unsigned live,gates,frees,bit;
void *__bennett_qalloc(uint64_t cls,uint64_t n){if(cls||live||(ALLOWED))abort();width=n;live=1;return (void*)1;}
void __bennett_gate(uint32_t op,void*h,uint64_t i){if(op!=1||h!=(void*)1||!live||i>=width)abort();gate_index=i;++gates;bit^=1;}
void __bennett_qfree(void*h){if(h!=(void*)1||!live||bit)abort();live=0;++frees;}
extern void top(void);
int main(void){CALLS printf("[%llu,%u,%llu,%u,%u,%u,0]\\n",(unsigned long long)width,gates,(unsigned long long)gate_index,frees,bit,live);return 0;}
""".replace('ALLOWED',allowed).replace('CALLS',calls)
    expected=[[want['widths'][0],want['gates'],want['index'],want['frees'],want['final_bit'],want['live_after'],want['code']]]
    for major in ('18','23'):
        directory=runner.tmp/(name+'-'+major);directory.mkdir(exist_ok=True)
        p=directory/'source.ll';p.write_text(src)
        o0=command([runner.tc[major]/'opt','-S','-passes=default<O0>',p,'-o','-']);domains(name,o0,want)
        folded=command([runner.tc[major]/'opt','-S','-passes=instcombine',p,'-o','-']);domains(name,folded,want,False)
        materialised=normalise(o0,major=major)
        main=directory/'driver.c';main.write_text(driver)
        for stage,ir in [('source',o0),('instcombine',folded),('materialised',materialised)]:
            p=directory/(stage+'.ll');p.write_text(ir)
            command([runner.tc[major]/'opt','-passes=verify',p,'-disable-output'])
            for level in ('0','3'):
                exe=directory/(stage+'-O'+level)
                command([runner.frontends[major]/'clang','-O'+level,p,main,SEEDS/'runtime.c','-o',exe])
                observed=[json.loads(line) for line in command([exe]).strip().splitlines()]
                equal(name,major+'/'+stage+'/O'+level,expected,observed)
