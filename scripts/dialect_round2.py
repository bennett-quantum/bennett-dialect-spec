"""Round-2 contract microvectors. C/LLVM and Rust supply observed outcomes."""
import json
import dialect_check as d
from dialect_check_v02 import equal
from dialect_state import run_native
from dialect_tdl import object_text, Session, assert_view, add_constant, oracle
import math

STATES={'handle-setjmp-reentry','entry-allocation-only','arena-logical-bounds','generation-cancel','nested-cl-view','fault-output-lifetime','co-loop-adjoint','deferred-channel-adj','co-store-release'}


def check_state(runner,block):
    name=block['attrs']['state']
    try:v=json.loads(block['body'])
    except ValueError as e:raise d.Fail('round-2 witness must be one JSON object') from e
    if name=='handle-setjmp-reentry':
        from dialect_check_v02 import recognise
        verdict,a=recognise(d.with_decls(runner.block('example',name)['body']))
        equal(name,'reference instance verdict',v['verdict'],verdict)
        src='#include <setjmp.h>\nstatic jmp_buf jb;\nstatic unsigned slots[2],live[64],next;\nstatic unsigned allocate(void){unsigned id=++next;live[id]=1;return id;}\nstatic void g(void){longjmp(jb,1);}\nint main(void){int r=setjmp(jb);unsigned h=allocate();slots[r]=h;if(!r)g();\nunsigned distinct=slots[0]!=slots[1];live[slots[0]]=0;live[slots[1]]=0;unsigned total=0;for(unsigned i=0;i<64;i++)total+=live[i];\nprintf("[%u,%u,%u,%u]\\n",next,distinct,total,0);return 0;}\n'
        run_native(runner,name,'',src,[[v['instances'],int(v['distinct']),v['live_after'],v['trap']]])
    elif name=='entry-allocation-only':
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
    elif name=='generation-cancel':
        ops={'qalloc':0,'gate-x':1,'qfree':2,'ret':3}
        program=','.join(str(ops[x]) for x in v['source'])
        src='#include "'+str(d.ROOT/'scripts/round2_runtime.c')+'"\nint main(void){unsigned ops[]={'+program+'};'
        for c in v['controls']:
            src+=f'{{struct generation g={{.steps={v["steps"]}}};unsigned code=round2_generate(&g,ops,sizeof ops/sizeof *ops);printf("[%u,%u,%u]\\n",{c}?code:0,g.local,code==4);}}'
        src+='return 0;}'
        run_native(runner,name,'',src,v['results'])
        # Failed f skips use; failed use cancels both unapplied recorders.
        src='#include "'+str(d.ROOT/'scripts/round2_runtime.c')+'"\nint main(void){unsigned a[]={0,1,1,2,3};'
        for failed in v['compute_failure']:
            src+=f'{{struct generation f={{.steps={1 if failed=="f" else 9}}},u={{.steps=1}};unsigned foreign={v["foreign_before"]};unsigned c=round2_generate(&f,a,5);if(!c)c=round2_generate(&u,a,5);if(c){{f.events=0;f.local=0;u.events=0;u.local=0;}}printf("[%u,%u,%u]\\n",c,f.local+u.local,foreign);}}'
        src+='return 0;}'
        run_native(runner,name+'-compute','',src,[[1,0,v['foreign_after']]]*len(v['compute_failure']))
    elif name=='nested-cl-view':
        # The native recorder establishes the inherited Cl value. Rust executes
        # the corresponding controlled writes and child quantum event.
        src='#include "'+str(d.ROOT/'scripts/round2_runtime.c')+'"\nint main(void){'+f'struct view parent={{.shadow=0,.written=1,.value={v["parent_store"]}}};struct view child={{.parent=&parent}};printf("%u\\n",round2_read(&child));return 0;}}'
        run_native(runner,name,'',src,[v['child_test']])
        for (c1,c2),want in zip(v['controls'],v['results']):
            q=Session(runner,name+str(c1)+str(c2));q.alloc('c1',1,c1);q.alloc('c2',1,c2);q.alloc('t',8);q.alloc('z',1)
            q.xmask('t',v['parent_store'],('c1[0]',))
            if v['parent_store']==v['child_test']:q.controlled(['x z[0]'],('c1[0]','c2[0]'))
            assert_view(q,['c1','c2','t','z'],{(c1,c2,*want):1})
    elif name=='fault-output-lifetime':
        q=Session(runner,name);q.alloc('c',1);q.alloc('t',8);q.alloc('f',4);q.alloc('Phi',4)
        q.apply(['h c[0]']);q.controlled(['oracle_call @slice tk () t f () ()'],('c[0]',),oracle=oracle('nine'),token=True,budget=0)
        q.apply(['qxor f Phi'])
        equal(name,'null fault field',None,v['budget_fault'])
        if abs(v['branch_probability']-0.5)>1e-7:raise d.Fail('Hadamard branch probability must be 0.5')
        expected={tuple(row[:1]+[0]+row[1:]):1/math.sqrt(2) for row in v['after_invocation']}
        assert_view(q,['c','t','f','Phi'],expected)
        prob=sum(abs(amp)**2 for (key,_),amp in q.view(['c','f','Phi']).items() if key[2]==v['fault'])
        if abs(prob-v['program_end_probability'])>1e-7:raise d.Fail('fault output statistics probability mismatch')
        # Conditional post-measurement correction is checked independently on
        # each supported outcome before clean free, without measuring early.
        for code in (0,v['fault']):
            release=Session(runner,name+'-release'+str(code));release.alloc('f',4,code);release.alloc('Phi',4,code)
            if code:release.xmask('f',code);release.xmask('Phi',code)
            release.free('f');release.free('Phi')
            equal(name,'program end remaining',v['remaining_after_end'],len(release.widths))
        equal(name,'trap',0,v['trap'])
    elif name=='co-loop-adjoint':
        # Source B increments once per active flag; n is a preserved input.
        # Four flag slots implement the stated bounded unroll, without measuring.
        steps=v['steps'];q=Session(runner,name);q.alloc('n',2);q.alloc('cnt',4)
        for k in range(steps):q.alloc('c'+str(k),1)
        q.apply(['h n[1]'])
        flags=['cx n[1] c0[0]','cx n[1] c1[0]']
        q.apply(flags)
        for k in range(steps):q.controlled(add_constant('cnt',4,1),('c'+str(k)+'[0]',))
        # Retained flags are included explicitly in the projected expected state.
        want={(n,c,*([int(i<n) for i in range(steps)])):1/math.sqrt(2) for n,c in zip(v['n_values'],v['use_counts'])}
        assert_view(q,['n','cnt']+['c'+str(k) for k in range(steps)],want)
        for k in reversed(range(steps)):q.controlled(add_constant('cnt',4,1),('c'+str(k)+'[0]',),adjoint=True)
        q.apply(list(reversed(flags)))
        for k in range(steps):q.free('c'+str(k))
        assert_view(q,['n','cnt'],{(n,c):1/math.sqrt(2) for n,c in zip(v['n_values'],v['after_compute'])})
        standalone=Session(runner,name+'-standalone');standalone.alloc('n',2,2);standalone.alloc('cnt',4,v['standalone_start'])
        for k in range(steps):standalone.alloc('c'+str(k),1)
        standalone.apply(flags)
        for k in reversed(range(steps)):standalone.controlled(add_constant('cnt',4,1),('c'+str(k)+'[0]',),adjoint=True)
        standalone.apply(list(reversed(flags)))
        for k in range(steps):standalone.free('c'+str(k))
        assert_view(standalone,['n','cnt'],{(2,v['standalone_result']):1})
        equal(name,'flags clean',True,v['flags_clean'])
    elif name=='deferred-channel-adj':
        for mode in v['modes']:
            if mode not in ('adj','compute'):raise d.Fail('unknown deferred invocation '+mode)
            q=Session(runner,name+'-'+mode);q.alloc('q',1);q.alloc('record',1)
            q.apply(['h q[0]']);q.apply(['cx q[0] record[0]'])
            # Empty use and unused measurement: the channel record survives
            # both adjoint paths; no inverse CX may erase it.
            q.apply(['h q[0]']);probs=[0.,0.]
            for (key,_),amp in q.view(['q','record']).items():probs[key[0]]+=abs(amp)**2
            if any(abs(a-b)>1e-7 for a,b in zip(probs,v['probabilities'])):raise d.Fail('deferred adjoint channel probabilities '+str(probs))
            equal(name,'retained record',v['record_retained'],'record' in q.widths);equal(name,'trap',0,v['trap'])
    elif name=='co-store-release':
        src='#include "'+str(d.ROOT/'scripts/round2_runtime.c')+'"\nint main(void){'
        expected=[]
        for value,want in zip(v['co_values'],v['observe_first_results']):
            src+=f'{{struct object o={{.k=2,.arena={value}}};unsigned c=round2_store(&o,{v["store_value"]});unsigned r=round2_release(&o);printf("[%u,%u,%u]\\n",c,r,o.arena);round2_observe(&o,{value});c=round2_store(&o,{v["store_value"]});printf("[%u,%u]\\n",c,o.shadow);}}'
            expected += [[v['store_code'],v['release_code'],value],[0,want]]
        src+='return 0;}'
        run_native(runner,name,'',src,expected);equal(name,'dirty reuse',False,v['reuse_permitted'])
    else:raise d.Fail('unimplemented round-2 state '+name)
