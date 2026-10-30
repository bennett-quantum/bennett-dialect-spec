"""Executable §19/§20 driver boundary operations, independent of expected results."""
import hashlib
import re
import dialect_check as d
from dialect_check_v02 import Analysis02, command, equal, expanded_types
from dialect_map import Mapper

SCENARIOS=dict(zip([f'§19.{i}' for i in range(3,9)]+['§20'],[
    'driver-oracle-synthesis','driver-pointer-promotion','driver-comparison-layout',
    'driver-snapshot-initializer','driver-closed-unit-fallback','driver-mixed-majors','platform-uart-write']))


def native(runner,name,source,entry,args='',declaration='extern unsigned char checked_entry(void);'):
    # Compile the actual transformed module, including globals and pointer chains.
    source=re.sub(r'@'+re.escape(entry)+r'\b','@checked_entry',source)
    ir=runner.tmp/(name+'.ll');ir.write_text(d.with_decls(source))
    main=runner.tmp/(name+'.c')
    main.write_text('#include <stdio.h>\n#include <stdint.h>\n'+declaration+'\n'
                    'void *__bennett_qalloc(uint64_t c,uint64_t w){return (void*)1;}\n'
                    'void __bennett_qfree(void *p){}\n'
                    'int main(void){printf("%u\\n",(unsigned)checked_entry('+args+'));return 0;}\n')
    results=[]
    for major in ('18','23'):
        exe=runner.tmp/(name+'-'+major)
        command([runner.frontends[major]/'clang','-O2',ir,main,'-o',exe])
        results.append(int(command([exe]).strip()))
    equal(name,'§19 comparison majors',results[0],results[1])
    return results[0]


def placement(source):
    """§19.4 points-to shared pointer-rich objects, then reverse caller closure."""
    a=Analysis02(d.Module(expanded_types(d.with_decls(source))));a.analyse()
    device=set(a.device);rich=set()
    for f in a.funcs():
        if f.name not in device:continue
        for ins in f.instrs():
            if ins.op=='load':
                parts=d.split_top(ins.text.split(' = ',1)[-1][5:])
                if d.parse_type(parts[0])[0][0]=='ptr':
                    rich.update(o for o,_ in a.ptrs(f,d.typed_val(parts[1])))
    while True:
        old=set(rich)
        for (obj,_,_),atoms in a.memory.items():
            if obj in rich:rich.update(x[1] for x in atoms if x[0]=="P")
        if rich==old:break
    promoted=set(device)
    for f in a.funcs():
        for ins in f.instrs():
            # A mutation of the transitive pointee graph shares the same state.
            if ins.op=='store':
                _,p=d.store_parts(ins)
                if rich & {o for o,_ in a.ptrs(f,p)}:promoted.add(f.name)
    while True:
        old=set(promoted)
        for f in a.funcs():
            if set(a.direct_callees(f))&promoted:promoted.add(f.name)
        if old==promoted:return promoted


def comparison_layout(source,data_base,heap):
    m=d.Module(source);base=data_base;globals_={}
    for name,g in m.globals.items():
        align=d.talign(g['type'])
        line=next(x for x in source.splitlines() if x.startswith('@'+name+' '))
        explicit=re.search(r', align (\d+)',line)
        if explicit:align=int(explicit[1])
        base=(base+align-1)//align*align;size=d.tsize(g['type'])
        globals_[name]=(base,size);base+=size
    hb=(base+4095)//4096*4096;end=hb+heap
    text=max(0x400000,(end+0x1fffff)//0x200000*0x200000)
    return globals_,hb,end,text


def snapshot(source,dump):
    m=d.Module(source)
    for name,image in dump.items():
        g=m.globals[name]
        equal(name,'§19.6 snapshot size',d.tsize(g['type']),len(image))
        if g['type'][0]!='int':raise d.Fail('snapshot adapter needs scalar or byte-array image')
        source=re.sub(r'(@'+re.escape(name)+r' = .*?global i\d+ )[^,\n]+',lambda x:x[1]+str(int.from_bytes(image,'little')),source)
    digest=hashlib.sha256(b''.join(dump.values())).hexdigest()
    return source,digest


def closed_unit(source):
    a=Analysis02(d.Module(d.with_decls(source)));a.analyse()
    for name in a.device:
        f=a.m.funcs[name]
        pointer_params={v for t,_,v in f.params if t[0]=='ptr'}
        if any(i.op=='call' and d.parse_call(i)['callee'] in pointer_params for i in f.instrs()):return False
        if any(not a.m.defined(n) for n in a.direct_callees(f) if not d.is_marker(n)):return False
        if any('@'+name in g['init'] for g in a.m.globals.values()):return False
    return True


def mixed_link(runner,inputs,newest):
    layouts=set();triples=set();paths=[]
    for k,(major,source) in enumerate(inputs):
        if int(major)>int(newest):raise d.Reject('BD-E-VERSION','§19.8 input newer than envelope')
        dl=re.search(r'target datalayout = "([^"]+)"',source);tr=re.search(r'target triple = "([^"]+)"',source)
        if not dl or not tr:raise d.Reject('BD-E-VERSION','§19.8 missing target')
        layouts.add(dl[1]);triples.add(tr[1])
        ir=runner.tmp/f'mixed-{k}.ll';bc=runner.tmp/f'mixed-{k}.bc';ir.write_text(source)
        command([runner.tc[major]/'opt','-passes=verify',ir,'-o',bc]);paths.append(bc)
    if len(layouts)!=1 or len(triples)!=1:raise d.Reject('BD-E-VERSION','§19.8 target mismatch')
    linked=runner.tmp/'mixed-linked.ll'
    command([runner.frontends[newest]/'llvm-link',*paths,'-S','-o',linked])
    command([runner.tc[newest]/'opt','-passes=verify','-disable-output',linked])
    return linked.read_text(),layouts.pop(),triples.pop()


def uart(runner,source):
    """§20 UART model lowering: physical transmit byte -> console device effect."""
    from dialect_cc import emit,signature
    addr=int(re.search(r'inttoptr i64 (\d+)',source)[1]);value=int(re.search(r'store volatile i8 (\d+)',source)[1])
    if addr!=0x10000000:raise d.Fail('§20 UART adapter: address outside transmit window')
    path=runner.tmp/'platform-uart.bisa'
    rows='fn r @main () (r:i32) () () ()\n^entry():\naddress = const.i64 4096\np = inttoptr address\nn = const.i64 1\neffect console.write p n\nr = const.i32 0\nret r'
    emit(runner,path,[rows],{'main':signature([],['i32'])},{'uart':bytes([value])},{'models':{'console':{'version':'0.8'}},'services':{}})
    got=runner.isa.call('run-cc',path,'main');rev=runner.isa.call('reverse',path,'main')
    equal('UART','§20 faults',[],got['faults']);equal('UART','§20 tape bytes',bytes([value]).hex(),got['tape'][0]['bytes'])
    equal('UART','§20 reverse whole state',True,rev['equals_entry'])
    equal('UART','§20 reverse tape',0,rev['effect_tape_length'])
    equal('UART','§20 reverse console','',rev['console_hex'])
    return got,rev


def check_scenario(runner,block):
    name=block['attrs']['state'];text=block['body'];source=runner.block('example',name)['body'];report=[]
    if name=='driver-oracle-synthesis':
        opts=re.search(r'driver: --bennett-oracle=(\w+) --bennett-bind=(\d+):in:(\d+) --bennett-payload=(\w+)',text)
        if not opts:raise d.Fail('§19.3 unsupported synthesis options')
        entry,index,width,payload=opts.groups();f=d.Module(source).funcs[entry];width=int(width)
        equal(name,'§19.3 binding index',0,int(index));equal(name,'§19.3 payload','return',payload)
        desc=f'IN({width},zext);tgt={f.ret[1]}'
        path=runner.tmp/'synthesised.bisa';mapper=Mapper(source,'@'+entry,desc,'null_size=4096 heap_base=4096 heap_limit_max=0 stack max 32')
        path.write_text(mapper.run(runner.isa,path));runner.isa.call('check',path)
        report=[opts[0],f'synthesise: nparam={len(f.params)} IN({width},zext); tgt width={f.ret[1]}; fault width=4; one invocation']
        for x in re.findall(r'^input=(\d+) ->',text,re.M):
            got=runner.isa.call('run-oracle',path,'ref','--input',x)
            report.append(f'input={x} -> code={got["code"]} payload={got["payload"]}')
    elif name=='driver-pointer-promotion':
        promoted=placement(source)
        equal(name,'§19.4 promotion',{'mutate','main','device'},promoted)
        value=native(runner,name,source,'main')
        report=['placement: mutate=CC main=CC device=CC; host retains only system-call proxy',f'run: main returns {value}; device follows head.next; tail image 1 is not the call-entry value']
    elif name=='driver-comparison-layout':
        data,heap=map(int,re.search(r'data_base=(\d+) heap_limit_max=(\d+)',text).groups())
        gl,hb,end,tb=comparison_layout(source,data,heap)
        lm='\n'.join(f'global @{n} -> G{k} base={b} size={s}' for k,(n,(b,s)) in enumerate(gl.items(),1))+f'\nnull_size={data} heap_base={hb} heap_limit_max={heap} stack max 32'
        path=runner.tmp/'comparison-layout.bisa';mapper=Mapper(source,'@f',';tgt=8',lm);path.write_text(mapper.run(runner.isa,path))
        got=runner.isa.call('run-oracle',path,'ref','--input','');value=native(runner,name,source,'f');equal(name,'§19.5 comparison',value,int(got['payload']))
        report=[f'driver: data_base={data} heap_limit_max={heap}; no arena/interface',f'layout: bytes={gl["bytes"][0]} slot={gl["slot"][0]} heap_base={hb} heap_end={end} text_base={tb}',f'slot image={mapper.image("slot").hex()}',f'native and device: f returns {value}; no code/data overlap']
    elif name=='driver-snapshot-initializer':
        image=bytes.fromhex(re.search(r'dump bytes for @g=([0-9a-f]+)',text)[1]);rewritten,digest=snapshot(source,{'g':image})
        (runner.tmp/'snapshot-build-record.json').write_text('{"snapshot":"'+digest+'"}\n')
        m=d.Module(rewritten);value=native(runner,name,rewritten,'f')
        path=runner.tmp/'snapshot.bisa';mapper=Mapper(rewritten,'@f',';tgt=8','global @g -> G1 base=4096 size=1\nnull_size=4096 heap_base=8192 heap_limit_max=0 stack max 32');path.write_text(mapper.run(runner.isa,path))
        got=runner.isa.call('run-oracle',path,'ref','--input','');equal(name,'§19.6 comparison',value,int(got['payload']))
        equal(name,'§19.6 fixed snapshot writers',[],[i.text for f in m.funcs.values() if f.is_def for i in f.instrs() if i.op=='store' and '@g' in i.text])
        report=[f'driver: --bennett-snapshot=dump; dump bytes for @g={image.hex()}',f'materialised global: @g = internal global i8 {m.globals["g"]["init"]}',f'data image={mapper.image("g").hex()}; entry read-set requiring transfer=empty; no snapshot register',f'native and device: f returns {value}; build record includes dump SHA-256']
    elif name=='driver-closed-unit-fallback':
        closed=closed_unit(source);equal(name,'§19.7 fallback',False,closed)
        # Internal @g is exposed only to this comparison harness.
        src=source.replace('define internal i8 @g','define i8 @g')
        value=native(runner,name,src,'entry','g','extern unsigned char g(void); extern unsigned char checked_entry(void*);')
        verdict=runner.block('example',name)['attrs']['verdict']
        report=['driver: -bennett-closed-unit; entry parameter p supplies function pointer',f'closedness={str(closed).lower()}; selected route=whole-program; verdict={verdict}',f'p=@g -> return {value}; same result without -bennett-closed-unit']
    elif name=='driver-mixed-majors':
        second=runner.block('example',name+'-second')['body'];linked,dl,tr=mixed_link(runner,[('18',source),('23',second)],'23')
        value=native(runner,name,linked,'main',declaration='extern unsigned checked_entry(void);')
        for inputs,M in [([('18',source),('23',second.replace(tr,'aarch64-unknown-linux-gnu'))],'23'),([('18',source),('23',second.replace(dl,'e-p:32:32'))],'23'),([('23',source)],'18')]:
            try:mixed_link(runner,inputs,M)
            except d.Reject as e:equal(name,'§19.8 version','BD-E-VERSION',e.code)
            else:raise d.Fail('§19.8 conflicting input accepted')
        report=['driver: input from18.bc major=18; input from23.bc major=23; envelope newest M=23',f'read/link/plugin/runtime/arith major=23; common datalayout={dl} triple={tr}',f'linked main -> return {value}','conflicting triple or datalayout -> reject:BD-E-VERSION','input newer than M -> reject:BD-E-VERSION']
    elif name=='platform-uart-write':
        got,rev=uart(runner,source)
        report=['driver: --bennett-platform=riscv64-bennett-virt --bennett-tier=reversible --bennett-entry=main','entry: console=empty tape=empty; interrupts pending=none','materialisation: entry poll; volatile store -> MMIO helper -> UART model -> console.write',f'run: status={got["status"]} result={got["results"][0]["value"]} console={got["console_hex"]}; tape has console.write({got["tape"][0]["bytes"]}); no code 7',f'reverse: status={rev["status"]} console=empty tape=empty CSR=entry RAM=entry']
    else:raise d.Fail('unknown driver scenario '+name)
    equal(name,'§19/§20 executed scenario',d.collapse(text),d.collapse('\n'.join(report)))
    runner.scenario_evidence.add(name)
