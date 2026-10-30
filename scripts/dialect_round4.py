"""Round-4 source-derived execution adapters; expectations are spec inputs."""
import json
import dialect_check as d
from dialect_check_v02 import equal
from dialect_map import Mapper

STATES={'n-gep-index','handle-cross-entry','handle-param-cross-entry'}

def check_state(runner,block):
    name=block['attrs']['state'];v=json.loads(block['body'])
    if name=='n-gep-index':
        source=runner.block('normalise-out',name)['body']
        for fn,cases in v.items():
            n=len(d.Module(source).funcs[fn].params)
            mapper=Mapper(source,'@'+fn,','.join(['ARG(64)']*n)+';tgt=64',
                          'null_size=4096 heap_base=4096 heap_limit_max=0 stack max 32')
            path=runner.tmp/(name+'-'+fn+'.bisa');path.write_text(mapper.run(runner.isa,path))
            runner.isa.call('check',path)
            for case in cases:
                argv=[]
                for x in case[:-2]:argv+=['--arg',str(x%(1<<64))]
                got=runner.isa.call('run-oracle',path,'ref','--input','',*argv,'--budget','1000,0,32,8')
                equal(name,fn+' mapped payload/code',case[-2:],[int(got['payload']),int(got['code'])])
    elif name in ('handle-cross-entry','handle-param-cross-entry'):
        from dialect_check_v02 import recognise
        from dialect_state import run_native
        source=runner.block('example',name)['body']
        equal(name,'entry boundary verdict',v['verdict'],recognise(d.with_decls(source))[0])
        driver='''#include <stdlib.h>
static unsigned live[64],value[64],tag[64],next,calls,first,second,code;
void *__bennett_qalloc(uint64_t cls,uint64_t width){
 if(cls||width!=1)abort();unsigned k=0;while(k<64&&live[k])++k;
 if(k==64){code=4;abort();}live[k]=1;tag[k]=++next;
 if(next==1)first=tag[k];if(next==2)second=tag[k];return (void*)(uintptr_t)tag[k];}
static unsigned slot(void*h){unsigned t=(uintptr_t)h;for(unsigned k=0;k<64;k++)if(live[k]&&tag[k]==t)return k;code=4;abort();}
void __bennett_gate(uint32_t op,void*h,uint64_t i){unsigned k=slot(h);if(op!=1||i)abort();value[k]^=1;}
void __bennett_qfree(void*h){unsigned k=slot(h);if(value[k])abort();live[k]=0;}
extern void put(void);extern void use(void);
int main(void){put();++calls;put();++calls;use();unsigned total=0;for(unsigned k=0;k<64;k++)total+=live[k];
printf("[%u,%u,%u,%u,%u]\\n",calls,next,first!=second,total,code);return 0;}'''
        if name=='handle-param-cross-entry':
            driver=driver.replace('extern void put(void);extern void use(void);','extern void stash(void*);extern void useall(void);')
            driver=driver.replace('put();++calls;put();++calls;use();','void *a=__bennett_qalloc(0,1),*b=__bennett_qalloc(0,1);stash(a);++calls;stash(b);++calls;useall();++calls;')
        run_native(runner,name,source,driver,[[v['entry_calls'],v['instances'],int(v['distinct']),v['live_after'],v['trap']]])
    else:raise d.Fail('unknown round-4 state '+name)
