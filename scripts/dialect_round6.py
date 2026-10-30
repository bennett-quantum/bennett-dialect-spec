"""Round-6 recognition and independent execution of the spec's source witnesses."""
import json
import re
import dialect_check as d
from dialect_check_v02 import command, equal, normalise, recognise
from dialect_state import run_native

STATES={'pt2-wrap','pt5-range','pt5-range-load','budget-stage'}


def check_state(runner,block):
    name=block['attrs']['state'];want=json.loads(block['body'])
    if name=='budget-stage':return check_budget_stage(runner,want)
    src=runner.block('example',name)['body']
    verdict,a=recognise(d.with_decls(src))
    equal(name,'reference verdict','accept',verdict)
    if name=='pt2-wrap':
        equal(name,'PT2 wrapped pointer',{('tab',want['pointer_offset'])},a.ptrs(a.m.funcs['top'],'%p'))
        equal(name,'PT6 function atom',{('F','body')},set(a.atoms(a.m.funcs['top'],'%f')))
        equal(name,'candidate set',set(want['candidates']),a.first_candidates())
        driver='''#include <stdlib.h>
static unsigned calls,code;
void __bennett_adj(void(*f)(void*),void*b,void*e){if(!f||b||e)abort();f(e);++calls;}
extern void top(void);int main(void){top();printf("[%u,%u]\\n",calls,code);return 0;}'''
        for major in ('18','23'):
            p=runner.tmp/('pt2-'+major+'.ll');p.write_text(src)
            o0=command([runner.tc[major]/'opt','-S','-passes=default<O0>',p,'-o','-'])
            _,a0=recognise(o0);equal(name,'O0 candidates',{'body'},a0.first_candidates())
            p.write_text(o0)
            folded=command([runner.tc[major]/'opt','-S','-passes=instcombine',p,'-o','-'])
            _,af=recognise(folded);equal(name,'instcombine candidates',{'body'},af.first_candidates())
            if not re.search(r'@__bennett_adj\(ptr (?:nonnull )?@body',folded):raise d.Fail('wrapped GEP did not fold to body')
            # Preserve the custom index semantics before clang installs host DL.
            run_native(runner,name+'-'+major,folded,driver,[[want['calls'],want['trap']]])
    else:
        values=a.ints(a.m.funcs['top'],'%w')
        equal(name,'PT5 materialised width set',want['value_set'],sorted(values))
        materialised=normalise(src,major='23' if name=='pt5-range' else '18')
        if 'range(' in materialised or '!range' in materialised:raise d.Fail('N3/N4 left a range annotation')
        allowed='&&'.join('n!='+str(x) for x in sorted(values))
        entry='extern void top(uint64_t);' if name=='pt5-range' else 'extern void top(const uint64_t*);'
        call='top(n);' if name=='pt5-range' else 'top(&n);'
        driver='''#include <stdlib.h>
static uint64_t width;static unsigned live,code,bits[4];
void *__bennett_qalloc(uint64_t cls,uint64_t n){if((ALLOWED)||cls||n>3||live)abort();width=n;live=1;return (void*)1;}
void __bennett_gate(uint32_t op,void*h,uint64_t i){if(op!=1||h!=(void*)1||!live||i>=width)abort();bits[i]^=1;}
void __bennett_qfree(void*h){if(h!=(void*)1||!live)abort();for(unsigned k=0;k<width;k++)if(bits[k])abort();live=0;}
ENTRY
int main(void){uint64_t n=INPUT;CALL printf("[%llu,%u,%u]\\n",(unsigned long long)width,live,code);return 0;}'''
        driver=driver.replace('ALLOWED',allowed).replace('ENTRY',entry).replace('INPUT',str(want['input'])).replace('CALL',call)
        run_native(runner,name,materialised,driver,[[want['width'],want['live_after'],want['trap']]])


def check_budget_stage(runner,want):
    from dialect_map import Mapper
    from dialect_meta import stage_budget
    src=runner.block('example','budget-stage-runtime')['body']
    canonical=normalise(runner.block('normalise-in','n-budget-stage')['body'])
    equal('budget-stage','N24 pair',runner.block('normalise-out','n-budget-stage')['body'],canonical)
    # The fixed runtime is appended after the canonical materialised function.
    prefix='\n'.join(ln for ln in canonical.splitlines() if not ln.startswith('declare '))+'\n'
    if not src.startswith(prefix):raise d.Fail('budget stage runtime detached from N24 source')
    table=json.loads(runner.block('budget-table','budget-stage')['body'])
    objects={}
    def build(values,capacities):
        link=('null_size=4096 heap_base=8192 heap_limit_max='+str(capacities['heap'])+
              ' stack max '+str(capacities['stack'])+
              ' global @ss_base -> G1 base=4096 size=8 global @ss_size -> G2 base=4104 size=8 global @ss_sp -> G3 base=4112 size=8')
        p=runner.tmp/('budget-'+str(values['sstack'])+'.bisa')
        obj=Mapper(src,'@f','IN(8,zext);tgt=8',link,sstack=values['sstack']).run(runner.isa,p);p.write_text(obj)
        runner.isa.call('check',p)
        identity=runner.isa.call('hash',p)['symbols']['ref']['interface_hash']
        objects[identity]=(p,obj)
        return obj,identity
    final,record=stage_budget(table,'f',build)
    equal('budget-stage','selection_identity',want['selection_identity'],record['selection_identity'])
    equal('budget-stage','semantic identity',want['identity'],record['identity'])
    equal('budget-stage','resolved sstack',want['final_sstack'],record['resolved']['sstack'])
    equal('budget-stage','resolved record',want['resolved'],record['resolved'])
    equal('budget-stage','frozen capacities',want['capacities'],record['capacities'])
    if 'lift.const.i64 '+str(want['final_sstack'])+'\n' not in final.split('lproc ',1)[0]:raise d.Fail('final wrapper has wrong size constant')
    # A launch token binds the final hash and resolved tuple; independently
    # execute that tuple, then the otherwise-identical steps-only token.
    def execute(identity,values):
        budget=','.join(str(values[k]) for k in ('steps','heap','stack','depth'))
        return runner.isa.call('run-oracle',objects[identity][0],'ref','--input','7','--budget',budget)
    selected=execute(record['identity'],record['resolved'])
    equal('budget-stage','final-object token execution',want['run'],selected)
    baseline=dict(record['resolved'],sstack=16)
    baseline_run=execute(record['selection_identity'],baseline)
    equal('budget-stage','baseline frame exhaustion',want['baseline_run'],baseline_run)
    steps_table=dict(table,entries=[{'identity':record['selection_identity'],'steps':'0'}])
    _,steps_record=stage_budget(steps_table,'f',build)
    equal('budget-stage','steps-only object identity',record['selection_identity'],steps_record['identity'])
    steps_run=execute(steps_record['identity'],steps_record['resolved'])
    equal('budget-stage','steps-only token execution',want['steps_only_run'],steps_run)
    if steps_record['resolved']['steps']==record['resolved']['steps']:raise d.Fail('steps-only token did not change')
    (runner.tmp/'budget-stage-resolved.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
