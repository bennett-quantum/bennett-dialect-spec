"""Round-2 contract microvectors. C/LLVM and Rust supply observed outcomes."""
import json
import dialect_check as d
from dialect_check_v02 import equal
from dialect_state import run_native
from dialect_tdl import object_text

STATES={'entry-allocation-only','arena-logical-bounds'}


def check_state(runner,block):
    name=block['attrs']['state']
    try:v=json.loads(block['body'])
    except ValueError as e:raise d.Fail('round-2 witness must be one JSON object') from e
    if name=='entry-allocation-only':
        sizes=v['caller_sizes'];base=v['base'];req=v['request']
        # Runtime replay uses the independent C allocator, with no byte reads.
        src='''#include <stdint.h>
#include <stdio.h>
struct alloc { uint64_t base,bump,limit; };
static uint64_t take(struct alloc *a,uint64_t n,unsigned *code) {
 uint64_t m=n?n:1;
 if(m>a->limit || a->bump>a->limit-m){*code=2;return 0;}
 uint64_t p=a->base+a->bump;a->bump+=m;*code=0;return p;
}
int main(void){'''
        for j,limit in enumerate(v['heap_limits']):
            src+=f'{{struct alloc caller={{{base},0,{limit}}};unsigned code=0;'
            for size in sizes:src+=f'take(&caller,{size},&code);'
            src+=f'struct alloc saved=caller,private=caller;uint64_t p=take(&private,{req},&code);printf("[%llu,%u]\\n",(unsigned long long)p,code);if(caller.bump!=saved.bump)return 9;}}'
        src+=f'{{struct alloc a={{{base},0,4096}};unsigned c;'
        for size in sizes+[v['next_caller_size']]:src+=f'take(&a,{size},&c);'
        src+=f'struct alloc private=a;uint64_t p=take(&private,{req},&c);printf("[%llu,%u]\\n",(unsigned long long)p,c);}}return 0;}}'
        run_native(runner,name,'',src,v['results']+[v['next_result']])
        equal(name,'caller state preserved',True,v['caller_unchanged'])
    elif name=='arena-logical-bounds':
        # Materialise the default OR of live-and-contained metadata predicates.
        sig={'abi':'0.8','args':['i64','i64'],'fault':4,'in':[],'kind':'oracle','mem':[{'A':1,'W':8,'role':'in'}],'tgt':16,'tier':'q'}
        layout={'A_tab':1,'H':13,'S_cells':8,'globals':{},'heap_base':4096,'heap_limit_max':0,'interface_regions':{'ref':{'coh':{'base':4096}}},'null_size':4096,'ptr_width':64}
        for width in (1,2):
            regs=['base:reg[64]','p:reg[64]','end:reg[64]','wrap:reg[1]','valid:reg[1]','bad:reg[1]','one:reg[1]','raw:reg['+str(width*8)+']','r:reg[16]']
            rows=['base = lift.addr @coh','p = lift.add base off','end = lift.add off size','wrap = lift.icmp.ult end off','valid = lift.const.i1 0']
            for k,(b,n,live) in enumerate(v['objects']):
                regs += [f'{x}{k}:reg[{w}]' for x,w in [('b',64),('e',64),('lo',1),('hi',1),('both',1),('live',1),('ok',1)]]
                rows += [f'b{k} = lift.const.i64 {b}',f'e{k} = lift.const.i64 {b+n}',f'lo{k} = lift.icmp.ule b{k} off',f'hi{k} = lift.icmp.ule end e{k}',f'both{k} = lift.and lo{k} hi{k}',f'live{k} = lift.const.i1 {live}',f'ok{k} = lift.and both{k} live{k}',f'valid = lift.or valid ok{k}']
            rows+=['one = lift.const.i1 1','bad = lift.xor valid one','bad = lift.or bad wrap','lift.faultif bad 7',f'lift.boundscheck p {width}',f'raw = lift.load.i{width*8} p','r = lift.zext.i16 raw' if width==1 else 'r = lift.mov raw','lift.retval r']
            fn='oracle @ref () (tgt:wire[16]) (fault:wire[4]) (coh:region[1,8] in) (off:i64, size:i64)\nregs { '+', '.join(regs)+' }\n^entry():\n'+'\n'.join(rows)
            path=object_text(runner.isa,runner.tmp/(name+str(width)+'.bisa'),[fn],{'ref':sig},layout)
            for (off,size),want in zip(v['accesses'],v['results']):
                if size!=width:continue
                got=runner.isa.call('run-oracle',path,'ref','--input','','--arg',str(off),'--arg',str(size),'--mem','coh='+bytes(v['bytes']).hex(),'--budget','1000,0,32,2')
                equal(name,'logical bounds payload/code',want,[int(got['payload']),int(got['code'])])
        equal(name,'physical bytes',v['physical_i16'],int.from_bytes(bytes(v['bytes']),'little'))
        # dead, padding, wrapping and event-store mutation share the runtime predicate.
        src='''static int valid(unsigned long p,unsigned long n,unsigned long b,unsigned long s,int live){return live && p+n>=p && p>=b && p+n<=b+s;}
int main(void){unsigned char x=1;int a=valid(0,1,0,1,0);int b=valid(2,1,0,1,1);if(a)x=9;printf("[%d,%d,%d]\\n",a?0:7,b?0:7,x==1);return 0;}'''
        run_native(runner,name+'-release','',src,[[v['freed_code'],v['padding_code'],int(v['store_unchanged'])]])
    else:raise d.Fail('unimplemented round-2 state '+name)
