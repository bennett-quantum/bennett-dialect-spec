"""Auditable CC/R fixtures for §11/§14 checked programs.

The fixtures spell the explicit state propagation of the demonstrated source
programs; constants are read from their source. The run result is never used to
construct the object. Native C runs provide a separate comparison.
"""
import json
import re
from dialect_check_v02 import equal
import dialect_check as d


def emit(runner,path,functions,signatures,data=None,devices=None):
    # ISA CC has pointer conversions and integer add, no gep/addr pseudo-op.
    def gep(m):
        dst,base,off=m.groups()
        return f'{dst}.base = ptrtoint.i64 {base}\n{dst}.address = add {dst}.base {off}\n{dst} = inttoptr {dst}.address'
    functions=[re.sub(r'^(\w+) = gep.i8 (\w+) (\w+)$',gep,f,flags=re.M) for f in functions]
    symbols={str(i):{'interface_hash':'0'*64,'kind':s['kind'],'name':n,'signature':s} for i,(n,s) in enumerate(signatures.items())}
    data=data or {}
    for name,image in data.items():symbols[str(len(symbols))]={'interface_hash':'0'*64,'kind':'data','name':name,'signature':{'abi':'0.8','kind':'data','size':len(image),'tier':'-'}}
    base=4096;globs={}
    for name,image in data.items():globs[name]={'base':base,'image':name,'size':len(image)};base+=len(image)
    heap=(base+4095)//4096*4096
    layout={'A_tab':12,'H':16,'S_cells':0,'globals':globs,'heap_base':heap,'heap_limit_max':4096,'interface_regions':{},'null_size':4096,'ptr_width':64}
    prefix='bennett-object isa=0.8 object=0.8 launch=0.8 sched=0.8 cert=0.8 coverage=0.8 target=0.8 ptr_width=64\n\nsection symbols\n'
    tail='\n\nsection functions\n'+'\n'.join(functions)+'\n'
    if data:tail+='\nsection data\n'+'\n'.join(n+' '+x.hex() for n,x in data.items())+'\n'
    if devices:tail+='\nsection devices\n'+json.dumps(devices,sort_keys=True,separators=(',',':'))+'\n'
    tail+='\nsection layout\n'+json.dumps(layout,sort_keys=True,separators=(',',':'))+'\n'
    dump=lambda:prefix+json.dumps(symbols,sort_keys=True,separators=(',',':'))+tail
    path.write_text(dump());hs=runner.isa.call('hash',path)
    for s in symbols.values():s['interface_hash']=hs['symbols'][s['name']]['interface_hash']
    path.write_text(dump());runner.isa.call('check',path)


def signature(params,results,tier='r'):
    return {'abi':'0.8','kind':tier,'params':params,'results':results,'tier':tier}


def fixture(runner,ident,launch=False):
    source=runner.block('example',ident)['body'];functions=[];sigs={};data={};devices={};entry='main'
    path=runner.tmp/(ident+('-program' if launch else '')+'.bisa')
    if ident.startswith('effect-console-'):
        msg=re.search(r'constant \[(\d+) x i8\] c"([^"]+)"',source)
        image=re.sub(r'\\([0-9A-Fa-f]{2})',lambda m:chr(int(m[1],16)),msg[2]).encode('latin1')
        data['msg']=image;tier='r' if ident.endswith('-r') else 'cc';entry='main' if tier=='r' else 'report'
        sigs[entry]=signature([],['i32'] if tier=='r' else [],tier)
        rows=[f'fn {tier} @{entry} () '+('(r:i32)' if tier=='r' else '()')+' () () ()','^entry():','address = const.i64 4096','p = inttoptr address',f'len = const.i64 {len(image)}']
        if tier=='r':
            rows+=['effect console.write p len','r = const.i32 0','ret r'];devices={'models':{'console':{'version':'0.8'}},'services':{}}
        else:
            rows+=['q = qreg.new any 1','qreg.free q','reply = hostcall bennett.dev.console.write p len','ret'];devices={'models':{},'services':{'bennett.dev.console.write':{'version':'0.8'}}}
        functions=['\n'.join(rows)]
    elif ident=='sjlj-two-frames':
        jump=int(re.search(r'longjmp\(jb, (\d+)\)',source)[1]);m=re.search(r'try_deep\((\d+)\) \+ (\d+) \* try_deep\((\d+)\)',source);n,k,n2=map(int,m.groups())
        functions=[f'''fn r @main () (r:i32) () () ()
^entry():
n = const.i32 {n}
a = call @try_deep n
m = const.i32 {n2}
b = call @try_deep m
k = const.i32 {k}
t = mul k b
r = add a t
ret r''', '''fn r @try_deep (n:i32) (r:i32) () () ()
^entry():
size = const.i64 8
state = alloc size
z = const.i32 0
store.i32 state z
call @deep n state
r = load.i32 state
free state
ret r''',f'''fn r @deep (n:i32, state:ptr) () () () ()
^entry():
z = const.i32 0
c = icmp.eq n z
br c ^raise() ^descend()
^raise():
v = const.i32 {jump}
store.i32 state v
ret
^descend():
one = const.i32 1
next = sub n one
call @deep next state
ret''']
        sigs={'main':signature([],['i32']),'try_deep':signature(['i32'],['i32']),'deep':signature(['i32','ptr'],[])}
    elif ident=='fiber-pingpong':
        loops=[int(n) for n in re.findall(r'i < (\d+)',source)];equal(ident,'N30 matching loop bounds',loops[0],loops[1]);N=loops[0]
        offset=int(re.search(r'trace\[n\+\+\] = (\d+) \+ i',source)[1]);radix=int(re.search(r's = s \* (\d+) \+ trace\[i\] % (\d+)',source)[1]);mod=int(re.search(r'return s % (\d+)',source)[1])
        functions=[f'''fn r @main () (r:i32) () () ()
^entry():
size = const.i64 {8*N+8}
mem = alloc size
four = const.i64 4
eight = const.i64 8
z = const.i32 0
one = const.i32 1
count = const.i32 {N}
store.i32 mem z
trace = gep.i8 mem eight
br ^ping(z)
^ping(i:i32):
a = zext.i64 i
p8 = mul a eight
p = gep.i8 trace p8
store.i32 p i
v = call @fiber_step mem
q = gep.i8 p four
store.i32 q v
i2 = add i one
more = icmp.ult i2 count
br more ^ping(i2) ^sumstart()
^sumstart():
total = const.i32 {2*N}
radix = const.i32 {radix}
modulus = const.i32 {mod}
br ^sum(z, z)
^sum(j:i32, acc:i32):
j64 = zext.i64 j
off = mul j64 four
sp = gep.i8 trace off
value = load.i32 sp
digit = urem value radix
t = mul acc radix
s = add t digit
j2 = add j one
again = icmp.ult j2 total
br again ^sum(j2, s) ^done(s)
^done(answer:i32):
r = urem answer modulus
free mem
ret r''',f'''fn r @fiber_step (frame:ptr) (r:i32) () () ()
^entry():
resume = load.i32 frame
base = const.i32 {offset}
r = add base resume
one = const.i32 1
next = add resume one
store.i32 frame next
ret r''']
        sigs={'main':signature([],['i32']),'fiber_step':signature(['ptr'],['i32'])}
    elif ident=='exit-status':
        status=int(re.search(r'exit\((\d+)\)',source)[1])
        functions=[f'''fn r @main () (r:i32) () () ()
^entry():
size = const.i64 8
state = alloc size
s = const.i32 {status}
call @exit_seed state s
r = load.i32 state
free state
ret r''','''fn r @exit_seed (state:ptr, s:i32) () () () ()
^entry():
store.i32 state s
ret'''];sigs={'main':signature([],['i32']),'exit_seed':signature(['ptr','i32'],[])}
    else:raise d.Fail('checker-unimplemented: CC/R fixture '+ident)
    if launch and sigs[entry]['kind']=='r':
        result=sigs[entry]['results'];params=sigs[entry]['params']
        if params:raise d.Fail('one-shot wrapper needs explicit launch arguments')
        groups=', '.join('v'+str(k)+':'+t for k,t in enumerate(result));names=['v'+str(k) for k in range(len(result))]
        call=((', '.join(names)+' = ') if names else '')+'call @'+entry
        functions.insert(0,'fn cc @launch () ('+groups+') () () ()\n^entry():\n'+call+'\nret'+(' '+ ' '.join(names) if names else ''))
        sigs={'launch':signature([],result,'cc'),**sigs};entry='launch'
    emit(runner,path,functions,sigs,data,devices)
    return path,entry


def check(runner,block,verb):
    ident=block['attrs']['cc-run'];path,entry=fixture(runner,ident,launch=verb=='run-program')
    argv=[path,entry,'--args','']
    if 'hostcall:' in block['body']:
        replies=runner.tmp/(ident+'-replies.json');replies.write_text(json.dumps([{'service':'bennett.dev.console.write','payload':'6f6b0a','reply':''}])+'\n')
        argv+=['--replies',replies]
    got=runner.isa.call(verb,*argv)
    if verb=='run-program':
        equal(ident,'§10 run close','CLOSED',got.get('run_state'))
        equal(ident,'§10 forward launch',False,got.get('reversed'))
    expected_line=next(line for line in block['body'].splitlines() if line.startswith('reverse:' if verb=='reverse' else 'run:'))
    status=re.search(r'status=([A-Z]+)',expected_line)[1];equal(ident,'§18.6 status',status,got.get('status'))
    if verb=='reverse':
        equal(ident,'§18.6 memory restoration',True,got.get('memory_equals_entry'))
        if 'console=empty' in expected_line:equal(ident,'§11.2 console restoration','',got.get('console'))
    else:
        expected=re.findall(r'INT\((\d+)\):(-?\d+)',expected_line)
        # JSON contract is checked strictly; unknown/new schemas fail with values.
        observed=got.get('results');equal(ident,'§18.6 results',[{'type':'i'+w,'value':v} for w,v in expected],observed)
        equal(ident,'§18.6 faults',[],got.get('faults'))
        if 'hostcall:' in block['body']:
            m=re.search(r'hostcall: service=(\S+) payload=([0-9a-f]+) reply=empty',block['body'])
            requests=got.get('host_requests')
            equal(ident,'§11.4 host transcript',[{'service':m[1],'payload':m[2],'reply':''}],
                  [{k:x[k] for k in ('service','payload','reply')} for x in requests])
        if 'tape:' in block['body']:
            tape=got.get('tape');want=re.search(r'bytes=([a-f0-9]+)',block['body'])[1]
            if not tape or tape[0].get('bytes')!=want:raise d.Fail(f'{ident} [§11.2 tape] expected bytes={want}; actual={tape!r}')


def r_budget_prefix(runner,block):
    """Probe the concrete executor boundary, never substitute generic trap 4."""
    from dialect_check_v02 import Unavailable, command
    path=runner.tmp/'r-budget-prefix.bisa'
    emit(runner,path,['fn r @main () () () () ()\n^entry():\naddress = const.i64 4096\np = inttoptr address\nn = const.i64 1\neffect console.write p n\nret'],
         {'main':signature([],[])},{'msg':b'x'},{'models':{'console':{'version':'0.8'}},'services':{}})
    runner.isa.build()
    argv=[runner.isa.exe,'run-cc',path,'main','--budget','0']
    try:
        output=command(argv)
    except d.Fail as error:
        if 'CC/R has no ISA step budget' not in str(error):raise
        # Published ISA CLI contract: --budget is host execution fuel, not an
        # implementation of dialect N34. Preserve the diagnostic as evidence.
        (runner.tmp/'r-budget-prefix.diagnostic').write_text(str(error)+'\n')
        raise Unavailable('N34/ISA-7 typed R fault 1 before first counted instruction; CLI only supplies host fuel',
                          ' '.join(map(str,argv)), 'b-dialect-spec-bz6') from error
    got=json.loads(output)
    equal('r-budget-prefix','§17.6 code',1,got.get('fault'))
    equal('r-budget-prefix','§17.6 no later tape',[],got.get('tape'))
    equal('r-budget-prefix','§17.6 no later console','',got.get('console'))

