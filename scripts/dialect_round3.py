"""Round-3 contract witnesses: observations from native code and Rust ISA execution."""
import json
import math
import dialect_check as d
from dialect_check_v02 import equal
from dialect_state import run_native
from dialect_tdl import Session, assert_view, add_constant, object_text

STATES = {'co-loop-identity', 'co-loop-adj-overwritten', 'deferred-channel-adj-place', 'co-observe-write-observe', 'handle-setjmp-interproc', 'shadow-stack-liveness', 'handle-stale-generation'}


def stack_probe(runner, name, width):
    """Materialised two-entry logical frame helper; metadata is run-time input.

    Offsets address one physically live pinned block. ISA boundscheck alone
    cannot distinguish any of the logical failures this helper must detect.
    """
    params=['off','size','b0','e0','live0','b1','e1','live1']
    regs=['end:reg[64]','wrap:reg[1]','valid:reg[1]','bad:reg[1]','one:reg[1]']
    rows=['end = lift.add off size','wrap = lift.icmp.ult end off','valid = lift.const.i1 0']
    for k in range(2):
        regs += [f'{s}{k}:reg[1]' for s in ('lo','hi','both','alive','ok')]
        regs += [f'zero{k}:reg[64]']
        rows += [f'lo{k} = lift.icmp.ule b{k} off',f'hi{k} = lift.icmp.ule end e{k}',f'both{k} = lift.and lo{k} hi{k}',f'zero{k} = lift.const.i64 0',f'alive{k} = lift.icmp.ne live{k} zero{k}',f'ok{k} = lift.and both{k} alive{k}',f'valid = lift.or valid ok{k}']
    rows += ['one = lift.const.i1 1','bad = lift.xor valid one','bad = lift.or bad wrap','lift.faultif bad 7','lift.ret valid']
    helper='lproc @validate ('+', '.join(p+':reg[64]' for p in params)+') (r:reg[1]) () () ()\nregs { '+', '.join(regs)+' }\n^entry():\n'+'\n'.join(rows)
    rows=[f'w{k} = lift.mov a{k}' for k in range(8)]
    rows+=['ok = lift.call @validate ('+', '.join('w'+str(k) for k in range(8))+')','base = lift.addr @physical','p = lift.add base w0',f'lift.boundscheck p {width}',f'raw = lift.load.i{width*8} p','r = lift.zext.i16 raw' if width==1 else 'r = lift.mov raw','lift.retval r']
    fn='oracle @ref () (tgt:wire[16]) (fault:wire[4]) (physical:region[4,8] in) ('+', '.join(f'a{k}:i64' for k in range(8))+')\nregs { '+', '.join([f'w{k}:reg[64]' for k in range(8)]+['ok:reg[1]','base:reg[64]','p:reg[64]',f'raw:reg[{width*8}]','r:reg[16]'])+' }\n^entry():\n'+'\n'.join(rows)
    sig={'abi':'0.8','args':['i64']*8,'fault':4,'in':[],'kind':'oracle','mem':[{'A':4,'W':8,'role':'in'}],'tgt':16,'tier':'q'}
    layout={'A_tab':1,'H':13,'S_cells':8,'globals':{},'heap_base':4096,'heap_limit_max':0,'interface_regions':{'ref':{'physical':{'base':4096}}},'null_size':4096,'ptr_width':64}
    return object_text(runner.isa,runner.tmp/(name+str(width)+'.bisa'),[fn,helper],{'ref':sig,'validate':{'abi':'0.8','kind':'lproc','params':[64]*8,'result':1,'tier':'q'}},layout)


def adjoint_records(events):
    """Reverse ordinary events; insert channel records at their latest consumer gap.

    This microvector grammar has self-adjoint ordinary events. Recursive record
    producers are inserted first, source order breaks ties at one gap.
    """
    records={e[2]:e for e in events if e[0]=='record'}
    emitted=set();active=set();out=[]
    def emit(record):
        target=record[2]
        if target in emitted:return
        if target in active:raise d.Fail('cyclic channel-record dependency')
        active.add(target)
        if record[1] in records:emit(records[record[1]])
        active.remove(target);emitted.add(target);out.append(record)
    for event in reversed(events):
        if event[0]=='record':
            emit(event)  # unused records keep their reversed source position
        else:
            needed=set(event[1:])
            for record in records.values():
                if record[2] in needed:emit(record)
            out.append(event)
    return out


def check_state(runner, block):
    name = block['attrs']['state']
    v = json.loads(block['body'])
    if name == 'co-loop-identity':
        for count, probability in zip(v['counts'], v['p_one']):
            if count not in (1, 2): raise d.Fail('identity count domain')
            q = Session(runner, name+str(count))
            for n,w in [('c',1),('invoke',1),('n',2),('z',1),('c0',1),('c1',1)]:q.alloc(n,w)
            q.xmask('invoke',1)
            q.apply(['h c[0]',f'cx c[0] n[{count-1}]'])
            flags=[f'cx n[{count-1}] c{k}[0]' for k in range(count)]
            q.apply(flags)
            for k in range(count):
                q.controlled(['x z[0]']*(2 if count==1 else 1),('invoke[0]',f'c{k}[0]'))
            q.apply(list(reversed(flags)))
            q.apply([f'cx c[0] n[{count-1}]','h c[0]'])
            assert_view(q,['c','invoke','n','z','c0','c1'],{(0,1,0,0,0,0):1})
            observed=sum(abs(a)**2 for (key,_),a in q.view(['c']).items() if key[0])
            equal(name,'P(c=1)',probability,round(observed,12))
            for n in ('c0','c1'):q.free(n)
        equal(name,'flags clean',True,v['flags_clean']);equal(name,'trap',0,v['trap'])
    elif name == 'co-loop-adj-overwritten':
        # Exhaustively test the finite data-only interface, independently of expectations.
        src='''int main(void){unsigned seen[16]={0},collision=0;
for(unsigned x=0;x<4;x++)for(unsigned z=0;z<4;z++){
 unsigned a=x,b=z;while(a<2){a++;b=(b+1)&3;}
 if(seen[a*4+b]++)collision=1;
}printf("[%u,%u]\\n",collision,!collision);return 0;}'''
        run_native(runner,name,'',src,[[int(v['collision']),int(v['bijective'])]])
        equal(name,'entry',[2,2],v['entry'])
        # Saved flags are valid through use, then cleaned against the restored entry.
        flags=['x x[1]','cx x[1] c0[0]','x x[0]','ccx x[1] x[0] c1[0]','x x[0]','x x[1]']
        for x in (0,1,2):
            q=Session(runner,name+str(x));q.alloc('x',2,x);q.alloc('z',2,x);q.alloc('c0',1);q.alloc('c1',1)
            q.apply(flags)
            rows=add_constant('x',2,1)+add_constant('z',2,1)
            for k in range(2):q.controlled(rows,(f'c{k}[0]',))
            assert_view(q,['x','z','c0','c1'],{(2,2,int(x<2),int(x<1)):1})
            for k in reversed(range(2)):q.controlled(rows,(f'c{k}[0]',),adjoint=True)
            q.apply(flags,adjoint=True);q.free('c0');q.free('c1')
            want=v['compute_restored'] if x==2 else [x,x]
            assert_view(q,['x','z'],{tuple(want):1})
        equal(name,'trap',0,v['trap'])
    elif name == 'deferred-channel-adj-place':
        events=adjoint_records([('record','a','w'),('cx','w','t'),('h','a')])
        for prep in ('zero','plus'):
            q=Session(runner,name+prep)
            for n in ('a','t','w'):q.alloc(n,1)
            if prep=='plus':q.apply(['h a[0]'])
            for op,*args in events:
                if op=='record':q.apply([f'cx {args[0]}[0] {args[1]}[0]'])
                elif op=='h':q.apply([f'h {args[0]}[0]'])
                elif op=='cx':q.apply([f'cx {args[0]}[0] {args[1]}[0]'])
                else:raise d.Fail('unknown adjoint microvector operation '+op)
            if prep=='plus':
                prob=sum(abs(a)**2 for (key,_),a in q.view(['a','t','w']).items() if key==(0,0,0))
                equal(name,'plus input joint zero',v['plus_joint_zero'],round(prob,12))
            else:
                q.apply(['h a[0]']);probs=[0.,0.]
                for (key,_),amp in q.view(['a']).items():probs[key[0]]+=abs(amp)**2
                equal(name,'zero input then H',v['zero_then_H'],[round(x,12) for x in probs])
            equal(name,'channel retained',v['record_retained'],'w' in q.widths)
        equal(name,'trap',0,v['trap'])
    elif name == 'co-observe-write-observe':
        src='#include "'+str(d.ROOT/'spec/seeds/coherence.c')+'"\n'+'''int main(void){
struct bennett_seed_object o={.size=2,.k=2,.arena={1,2}};unsigned char out[2];unsigned widths[1];
unsigned bad=bennett_seed_cc_store(&o,0,9);
bennett_seed_observe(&o,0,1,out,widths);printf("[%u,%u]\\n",o.k,o.covered[0]);
if(bennett_seed_cc_store(&o,0,9))return 9;
printf("[%u,%u,%u,%u]\\n",o.k,o.covered[0],o.arena[0],o.shadow[0]);
bennett_seed_observe(&o,1,1,out,widths);printf("[%u,%u,%u,%u,%u]\\n",o.k,o.shadow[0],o.shadow[1],o.arena[0],o.arena[1]);
printf("[%u,%u]\\n",o.k==0?o.shadow[0]:0,o.k==0?0:4);
o.k=2;bennett_seed_mask(&o,0,1,1);printf("[%u,%u]\\n",!o.covered[0],bad);return 0;}'''
        run_native(runner,name,'',src,[v['after_first'],v['after_store'],v['after_second'],v['load'],[int(v['event_invalidates']),v['unobserved_store']]])
    elif name == 'handle-setjmp-interproc':
        from dialect_check_v02 import recognise
        verdict,_=recognise(d.with_decls(runner.block('example',name)['body']))
        equal(name,'BLK-1 conservative reference bound',v['verdict'],verdict)
        src='''#include <setjmp.h>
#include <stdlib.h>
static jmp_buf jb;static unsigned slots[2],live[64],next,maxlive;
static void deep(unsigned i){if(!i)longjmp(jb,1);}
static void G(unsigned i){unsigned h=++next;if(h>=64)abort();live[h]=1;slots[i]=h;
unsigned total=0;for(unsigned j=0;j<64;j++)total+=live[j];if(total>maxlive)maxlive=total;deep(i);}
int main(void){unsigned r=setjmp(jb);G(r);unsigned distinct=slots[0]!=slots[1];
live[slots[0]]=live[slots[1]]=0;unsigned total=0;for(unsigned j=0;j<64;j++)total+=live[j];
printf("[%u,%u,%u,%u,%u]\\n",next,distinct,total,0,maxlive);return 0;}'''
        run_native(runner,name,'',src,[[v['instances'],int(v['distinct']),v['live_after'],v['trap'],v['max_live']]])
    elif name == 'shadow-stack-liveness':
        src='#include "'+str(d.ROOT/'scripts/round3_runtime.c')+'"\n'+'''static void show(struct stack*s,uint64_t p){unsigned c;unsigned v=ss_load(s,p,&c);printf("[%u,%u]\\n",v,c);}
static uint64_t f(struct stack*s){uint64_t p=ss_push(s,1);if(ss_store(s,p,7))abort();ss_pop(s,p);return p;}
int main(void){struct stack s={0};uint64_t p=ss_push(&s,1);ss_store(&s,p,7);show(&s,p);
struct stack replay=s;ss_pop(&s,p);show(&s,p);unsigned old=s.bytes[0];ss_store(&s,0,9);
printf("%u\\n",s.bytes[0]==old);show(&replay,p);
struct stack t={0};p=f(&t);show(&t,p);
ss_push(&replay,1);printf("[%u,%u]\\n",0,ss_check(&replay,0,2));
printf("[%u,%u]\\n",0,ss_check(&replay,2,1));
ss_restore(&replay,1);show(&replay,1);
printf("[%u,%u]\\n",0,ss_check(&replay,UINT64_MAX,2));return 0;}'''
        run_native(runner,name,'',src,[v['live'],v['popped'],int(v['store_unchanged']),v['replay'],v['popped'],v['spanning'],v['padding'],v['restored'],v['wrap']])
        paths={w:stack_probe(runner,name,w) for w in (1,2)}
        cases=[('live',[0,1,0,1,1,1,2,0]),('popped',[0,1,0,1,0,1,2,0]),('spanning',[0,2,0,1,1,1,2,1]),('padding',[2,1,0,1,1,1,2,0]),('restored',[1,1,0,1,1,1,2,0]),('wrap',[(1<<64)-1,2,0,1,1,1,2,1]),('replay',[0,1,0,1,1,1,2,0])]
        for key,args in cases:
            argv=[]
            for x in args:argv+=['--arg',str(x)]
            got=runner.isa.call('run-oracle',paths[args[1]],'ref','--input','',*argv,'--mem','physical=07'+'00'*15,'--budget','1000,0,256,8')
            equal(name,key+' payload/code',v[key],[int(got['payload']),int(got['code'])])
    elif name == 'handle-stale-generation':
        from dialect_check_v02 import recognise
        ir=runner.block('example',name)['body']
        verdict,analysis=recognise(d.with_decls(ir))
        equal(name,'source remains accepted','accept',verdict)
        equal(name,'reference physical bound',[v['physical_slots']],list(analysis.instance_bounds.values()))
        src='''#include <setjmp.h>
#include <stdlib.h>
static jmp_buf fault;static uintptr_t next,current;static unsigned live,value,code;
void *__bennett_qalloc(uint64_t cls,uint64_t width){(void)cls;if(live||width!=1)abort();
current=++next;live=1;value=0;return (void*)current;}
void __bennett_qfree(void*h){if(!live||(uintptr_t)h!=current)abort();if(value)abort();live=0;}
void __bennett_gate(uint32_t op,void*h,uint64_t bit){if(!live||(uintptr_t)h!=current){code=4;longjmp(fault,1);}
if(op!=1||bit)abort();value^=1;}
extern void stale_generation(void);extern unsigned generation_equal;
int main(void){if(!setjmp(fault))stale_generation();unsigned second=value;
if(live)__bennett_qfree((void*)current);
printf("[%u,%u,%u,%u]\\n",generation_equal,code,second,live);return 0;}'''
        run_native(runner,name,ir,src,[[int(v['equal']),v['stale_code'],v['second_value'],v['live_after']]])
    else:raise d.Fail('unimplemented round-3 state '+name)
