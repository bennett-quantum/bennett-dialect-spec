"""Draft 0.2.11 checked native witnesses, ISA target remains 0.8."""
import json
import dialect_check as d
from dialect_check_v02 import command, equal, recognise, normalise
from dialect_native import PREFIX, SEEDS

STATES={'pt12-xor','pt12-cmpxchg-success','pt12-cmpxchg-failure'}


def check_state(runner,block):
    name=block['attrs']['state'];want=json.loads(block['body'])
    src=d.with_decls(runner.block('example',name)['body'])
    verdict,a=recognise(src);equal(name,'PT12 admission','accept',verdict)
    for val,values in want['domains'].items():
        equal(name,'PT12 AV '+val,{0:frozenset(('I',x) for x in values)},a.av(a.m.funcs['top'],val))
    driver=PREFIX+'''#include <stdlib.h>
extern uint64_t observed_old,observed_success;
static uint64_t width;static unsigned frees,live,bit;
void *__bennett_qalloc(uint64_t cls,uint64_t n){if(cls||live||!n)abort();width=n;live=1;return (void*)1;}
void __bennett_gate(uint32_t op,void*h,uint64_t i){if(op!=1||h!=(void*)1||!live||i>=width)abort();bit^=1;}
void __bennett_qfree(void*h){if(h!=(void*)1||!live||bit)abort();live=0;++frees;}
extern void top(void);
int main(void){top();printf("[%llu,%llu,%llu,%u,%u,0]\\n",(unsigned long long)observed_old,(unsigned long long)observed_success,(unsigned long long)width,frees,live);return 0;}
'''
    observations={}
    for major in ('18','23'):
        directory=runner.tmp/(name+'-'+major);directory.mkdir(exist_ok=True)
        p=directory/'materialised.ll';p.write_text(normalise(src,major=major))
        command([runner.tc[major]/'opt','-passes=verify',p,'-disable-output'])
        main=directory/'driver.c';main.write_text(driver)
        for level in ('0','3'):
            exe=directory/('O'+level)
            command([runner.frontends[major]/'clang','-O'+level,p,main,SEEDS/'runtime.c','-o',exe])
            observed=json.loads(command([exe]));observations[major+'/O'+level]=observed
            equal(name,major+'/O'+level,want['native'],observed)
    return {'domains':want['domains'],'native':observations}
