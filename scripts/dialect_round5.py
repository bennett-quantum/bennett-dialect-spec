"""Round-5 source-derived witnesses, executed by native LLVM or the ISA CLI."""
import json
import dialect_check as d
from dialect_check_v02 import equal, recognise
from dialect_state import run_native

STATES={'pt6-byte-width','pt6-subrange'}

def check_state(runner,block):
    name=block['attrs']['state'];want=json.loads(block['body'])
    source=runner.block('example',name)['body']
    verdict,a=recognise(d.with_decls(source))
    values=a.ints(a.m.funcs['top'],'%n')
    equal(name,'PT6 whole loaded values',want['value_set'],sorted(values) if values!='TOP' else values)
    driver='''#include <stdlib.h>
static uint64_t width;static unsigned live,code;static unsigned bits[1024];
void *__bennett_qalloc(uint64_t cls,uint64_t n){if(cls||n>1024||live)abort();width=n;live=1;return (void*)1;}
void __bennett_gate(uint32_t op,void*h,uint64_t i){if(op!=1||h!=(void*)1||!live||i>=width)abort();bits[i]^=1;}
void __bennett_qfree(void*h){if(h!=(void*)1||!live)abort();for(unsigned k=0;k<width;k++)if(bits[k])abort();live=0;}
extern void top(void);int main(void){top();printf("[%llu,%u,%u]\\n",(unsigned long long)width,live,code);return 0;}'''
    if values!='TOP':
        allowed='&&'.join('n!='+str(x) for x in sorted(values))
        driver=driver.replace('if(cls||n>1024||live)', 'if(('+allowed+')||cls||n>1024||live)')
    if name=='pt6-byte-width':
        equal(name,'finite dispatch verdict','accept',verdict)
        equal(name,'wire index',want['wire'],int(d.parse_call(next(i for i in a.m.funcs['top'].instrs() if '@__bennett_gate' in i.text))['args'][2][2]))
    else:equal(name,'unbounded dispatch dependency','blocked:BD-B-ISA4',verdict)
    run_native(runner,name,source,driver,[[want['width'],want['live_after'],want['trap']]])
