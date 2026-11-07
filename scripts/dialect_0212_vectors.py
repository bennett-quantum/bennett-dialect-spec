"""Independent boundary oracles; samples do not certify consumer implementations."""
from dialect_profile import profile
import dialect_check as d
import json
from pathlib import Path
from dialect_check_v02 import command, equal, ROOT


def numerical(runner):
    source=Path(__file__).with_name('0212_numerical.c')
    expected=[['3fff8000000000000008',0,1]]
    for kind in range(2):
        for pos in range(2):
            for sticky in range(2):
                for predicate in range(2):
                    for signaling in range(2):
                        for ignore in range(2):
                            expected.append([predicate,16*sticky | int((kind or signaling) and not ignore),1])
    expected += [[r,1,0] for r in range(5)]
    for major in ('18','23'):
        exe=runner.tmp/('0212-numerical-'+major)
        command([runner.frontends[major]/'clang','-O0','-frounding-math',source,'-lm','-o',exe])
        got=[json.loads(line) for line in command([exe]).splitlines()]
        equal('0212/DF/'+major,'independent host boundary oracle',expected,got)
    return {'claim':'independent host boundary evidence, not production carrier conformance','vectors_per_build':len(expected)}


def allocation(runner):
    source=Path(__file__).with_name('0212_allocation.c')
    expected=[[0,0,4096,4112,4128,3],[4096,3],[4099,13],[4112,16],0,
              [2,1],[2,1],1,[2,1],[2,3,1,1],[2,16,2,1],[4096,1,0,0]]
    for major in ('18','23'):
        exe=runner.tmp/('0212-allocation-'+major)
        command([runner.frontends[major]/'clang','-O2',source,'-o',exe])
        equal('0212/DR/'+major,'native allocation trace',expected,
              [json.loads(line) for line in command([exe]).splitlines()])
    # Execute the identical primitive requests on the independent ISA backend.
    from dialect_tdl import object_text
    for count,address in ((1,4096),(2,4099),(3,4112),(4,4128)):
        regs=['bad:reg[1]'];rows=['bad = lift.const.i1 0']
        for k,n in enumerate((3,13,16,0)[:count]):
            regs += [f'n{k}:reg[64]',f'p{k}:reg[64]']
            rows += [f'n{k} = lift.const.i64 {n}',f'p{k} = lift.alloc n{k}']
            if n:
                regs += [f'z{k}:reg[{8*n}]',f'zero{k}:reg[{8*n}]',f'nz{k}:reg[1]']
                rows += [f'lift.boundscheck p{k} {n}',f'z{k} = lift.load.i{8*n} p{k}',
                         f'zero{k} = lift.const.i{8*n} 0',f'nz{k} = lift.icmp.ne z{k} zero{k}',f'bad = lift.or bad nz{k}']
        regs += ['result:reg[64]','zero:reg[64]','shift:reg[64]']
        rows += ['zero = lift.zext.i64 bad','shift = lift.const.i64 48','zero = lift.shl zero shift',
                 f'result = lift.or p{count-1} zero','lift.retval result']
        body='oracle @ref () (tgt:wire[64]) (fault:wire[4]) () ()\nregs { '+', '.join(regs)+' }\n^entry():\n'+'\n'.join(rows)
        sig={'abi':profile().isa,'args':[],'fault':4,'in':[],'kind':'oracle','mem':[],'tgt':64,'tier':'q'}
        layout={'A_tab':32,'H':13,'S_cells':8,'globals':{},'heap_base':4096,'heap_limit_max':33,'interface_regions':{'ref':{}},'null_size':4096,'ptr_width':64}
        obj=object_text(runner.isa,runner.tmp/f'0212-alloc-{count}.bisa',[body],{'ref':sig},layout)
        for heap,code,payload in ((33 if count==4 else 32,0,address),(sum(max(n,1) for n in (3,13,16,0)[:count])-1,2,0)):
            budget=f'1000,{heap},8,8'
            got=runner.isa.call('run-oracle',obj,'ref','--input','','--budget',budget)
            equal('0212/DR/ISA','primitive address, zero fill or fault',[code,payload],[int(got['code']),int(got['payload'])])
            reverse=runner.isa.call('step-check',obj,'ref','--exhaustive','--budget',budget)
            equal('0212/DR/ISA','forward/reverse allocation and fault state','ok',reverse['status'])
        # Live size is requested n, including n=0, not the charged max(n,1).
        bad=body.replace('result:reg[64]', 'end:reg[64], result:reg[64]').replace(
            'lift.retval result',f'end = lift.add p{count-1} n{count-1}\nlift.boundscheck end 1\nlift.retval result')
        badobj=object_text(runner.isa,runner.tmp/f'0212-alloc-bounds-{count}.bisa',[bad],{'ref':sig},layout)
        budget='1000,33,8,8'
        got=runner.isa.call('run-oracle',badobj,'ref','--input','','--budget',budget)
        equal('0212/DR/ISA','one past requested live size',[7,0],[int(got['code']),int(got['payload'])])
        reverse=runner.isa.call('step-check',badobj,'ref','--exhaustive','--budget',budget)
        equal('0212/DR/ISA','bounds-fault reversal','ok',reverse['status'])
    # Invoke the consumer's emitter with a resolved layout; never copy its code.
    out=runner.tmp/'0212-driver-layout';out.mkdir(exist_ok=True)
    resolved=out/'input-layout.json'
    resolved.write_text(json.dumps({**layout,'heap_limit_max':32}))
    emitter=d.sibling('bennett-driver')/'scripts/native-layout.py'
    command(['python3',emitter,out,out/'unused-device',resolved,'4096',''])
    ll=out/'native-layout.ll'
    equal('0212/DD','driver emits one constant with resolved fields and alignment',
          1,ll.read_text().count('@__bennett_rt_native_layout = constant { i64, i64, i64 } { i64 1, i64 4096, i64 32 }, align 8'))
    driver='''extern const unsigned char __bennett_rt_native_layout[];
int main(void){for(int k=0;k<24;k++)printf("%02x",__bennett_rt_native_layout[k]);puts("");}'''
    main=runner.tmp/'0212-layout.c';main.write_text('#include <stdio.h>\n'+driver)
    for major in ('18','23'):
        exe=runner.tmp/('0212-layout-'+major)
        command([runner.frontends[major]/'clang',ll,main,'-o',exe])
        equal('0212/DD/'+major,'layout bytes at offsets 0/8/16',
              '010000000000000000100000000000002000000000000000',command([exe]).strip())
    return {'claim':'native fixture and independent ISA boundary execution; not production runtime conformance'}
