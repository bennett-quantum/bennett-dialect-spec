"""Round-3 contract witnesses: observations from native code and Rust ISA execution."""
import json
import math
import dialect_check as d
from dialect_check_v02 import equal
from dialect_state import run_native
from dialect_tdl import Session, assert_view, add_constant

STATES = {'co-loop-identity', 'co-loop-adj-overwritten', 'deferred-channel-adj-place', 'co-observe-write-observe'}


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
    else:raise d.Fail('unimplemented round-3 state '+name)
