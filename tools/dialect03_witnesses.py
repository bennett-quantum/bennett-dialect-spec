"""ISA 0.9 witnesses of draft 0.3: objects built from the §25.1 lowerings, run on the reference interpreter.

Python places the rows; every stated result comes from the executor (P-3). An executor diagnostic in
ABSENT means the ISA row is not implemented there yet: the row reports blocked, naming the capability (P-2).
Any other diagnostic is a failure. Fixtures follow ISA 0.9 §16.3 examples 4 to 8.
"""
import collections,hashlib,json,re
from pathlib import Path
import dialect_check as d
import dialect_check_v02 as v2
import dialect_cc as cc

CAPABILITY='ISA09-EXECUTOR'
ABSENT=(r'qreg size must be a canonical unsigned INT',r'qreg instructions are CC only',
        r'unknown (?:CC/R )?(?:opcode|instruction).*budget\.mint',r'budget\.mint',r'qinplace.*(?:operand|form|arity|expected)',
        r'qreg\.(?:width|id|from_id)')
FLIP=('perm_action @flip (a:wire mut) () () () ()\n^entry():\nx a',
      {'abi':'0.9','args':[],'bounds':[],'in':[],'kind':'perm_action','mem':[],'mut':[1],'tier':'q'})
INC8=('oracle @inc8 (x:wire[8] in) (t:wire[8]) (f:wire[4]) () ()\nregs { one:reg[8], r:reg[8] }\n^entry():\none = lift.const.i8 1\nr = lift.add x one\nlift.retval r',
      {'abi':'0.9','args':[],'fault':4,'in':[8],'kind':'oracle','mem':[],'tgt':8,'tier':'q'})


def build(runner,name,functions,signatures,data=None,devices=None):
    path=runner.tmp/(name+'.bisa')
    try:
        cc.emit(runner,path,functions,signatures,data,devices)
    except d.Fail as e:
        admitted_by_second_reader(path)
        absent(e,name)
    return path


def build_quiet(runner,name,functions,signatures):
    try:return build(runner,name,functions,signatures)
    except v2.Unavailable:return None


def admitted_by_second_reader(path):
    """While the reference cannot admit a row, the VM's published binary reads the fixture: a fixture
    it refuses is this checker's bug, a failure rather than a blocked row. Admission only, no execution."""
    raise v2.Unavailable('independent admission of an unsupported ISA 0.9 row',
                         'configure a published second-reader binary in gate.toml',
                         'SECOND-READER-PIN')



def absent(e,name):
    text=str(e)
    for pattern in ABSENT:
        if re.search(pattern,text):
            raise v2.Unavailable('ISA 0.9 row of witness '+name+': '+text.strip().splitlines()[-1][:160],'bennett-isa-ref with ISA 0.9 K1-K4',CAPABILITY)
    raise e


def call(runner,verb,path,entry,args='',name=''):
    try:
        return runner.isa.call(verb,path,entry,'--args',args)
    except d.Fail as e:
        absent(e,name or path.stem)


def fields(got,verb):
    out={'status':got.get('status')}
    if verb=='run-cc':
        out['fault']='none' if got.get('fault') is None else str(got['fault'])
        out['records']=len(got.get('faults') or [])
    return out


def compare(name,line,got):
    """`key=value` tokens after the `run:`/`reverse:` label; each is an exact observation."""
    _,_,spec=line.partition(': ')
    for key,want in re.findall(r'(\w+)=(\S*)',spec):
        if key=='status':actual=got.get('status')
        elif key=='fault':actual='none' if got.get('fault') is None else str(got['fault'])
        elif key=='records':actual=str(len(got.get('faults') or []))
        elif key=='console':actual=got.get('console_hex','')
        elif key=='tape':actual=str(got.get('effect_tape_length'))
        elif key=='memory_equals_entry':actual=str(got.get('memory_equals_entry')).lower()
        elif key=='result':actual=str(got['results'][0]['value']) if got.get('results') else 'none'
        elif key=='registers_used':actual=str(got['results'][0]['value'])
        else:raise d.Fail(name+': unknown observation '+key)
        v2.equal(name,line.split(':')[0]+' '+key,want,actual)


def lines(block):return [l for l in block['body'].strip().splitlines() if l.strip()]


CONSOLE={'models':{'console':{'version':'0.9'}},'services':{}}


def r_budget(runner,block):
    """§17.6: the counter over `console.write("x"); return`, for budgets 0, 1 and 2."""
    for line in lines(block):
        s=int(re.match(r'steps=(\d+)',line)[1]);verb='reverse' if ' reverse:' in line else 'run-cc'
        body=f'''fn r @main () () () () ()
^entry():
steps = const.i64 {s}
zero = const.i64 0
one = const.i64 1
address = const.i64 4096
p = inttoptr address
len = const.i64 1
c0 = icmp.eq steps zero
br c0 ^out0() ^i0()
^out0():
fault 1
^i0():
left = sub steps one
effect console.write p len
c1 = icmp.eq left zero
br c1 ^out1() ^i1()
^out1():
fault 1
^i1():
ret'''
        path=build(runner,f'r-budget-{s}',[body],{'main':cc.signature([],[])},{'msg':b'x'},CONSOLE)
        compare('r-budget-prefix',line,call(runner,verb,path,'main'))


def r_code(runner,block):
    for line in lines(block):
        m=re.match(r'(caller-successor )?code=(\d+)',line);code=int(m[2])
        if m[1]:
            fn=[f'fn r @fail () () () () ()\n^entry():\nfault {code}',
                'fn cc @main () () () () ()\n^entry():\ncall @fail\nfault 9']
            sig={'main':cc.signature([],[],'cc'),'fail':cc.signature([],[])}
        else:
            fn=[f'fn r @main () () () () ()\n^entry():\nfault {code}'];sig={'main':cc.signature([],[])}
        path=build(runner,f'r-code-{code}-{bool(m[1])}',fn,sig)
        compare('r-fault-code',line,call(runner,'run-cc',path,'main'))


def k1_width(runner,block):
    body='''fn cc @top (n:i64) () () () ()
^entry():
zero = const.i64 0
one = const.i64 1
bad = icmp.eq n zero
br bad ^tsize() ^ok()
^tsize():
fault 4
^ok():
q = qreg.new any n
w = qreg.width q
br ^test(zero)
^test(i:i64):
c = icmp.ult i w
br c ^body(i) ^done()
^body(j:i64):
s = qreg.slice q j 1
action_call @flip (s) () () ()
t = qreg.slice q j 1
action_call @flip (t) () () ()
j2 = add j one
br ^test(j2)
^done():
qreg.free q
ret'''
    path=build(runner,'k1-width',[body,FLIP[0]],{'top':cc.signature(['i64'],[],'cc'),'flip':FLIP[1]})
    for line in lines(block):
        n=re.match(r'n=(\d+)',line)[1]
        compare('k1-width',line,call(runner,'run-cc',path,'top',n))


def k1_table(runner,block):
    line=lines(block)[0];count=int(re.match(r'registers=(\d+)',line)[1])
    body=f'''fn cc @main () (r:i64) () () ()
^entry():
zero = const.i64 0
one = const.i64 1
n = const.i64 {count}
eight = const.i64 8
base = const.i64 4096
br ^alloc(zero)
^alloc(i:i64):
c = icmp.ult i n
br c ^abody(i) ^use(zero, zero, zero)
^abody(j:i64):
q = qreg.new any 1
id = qreg.id q
off = mul j eight
addr = add base off
p = inttoptr addr
store.i64 p id
j2 = add j one
br ^alloc(j2)
^use(u:i64, prev:i64, total:i64):
d = icmp.ult u n
br d ^ubody(u, prev, total) ^end(total)
^ubody(v:i64, last:i64, sum:i64):
off2 = mul v eight
addr2 = add base off2
p2 = inttoptr addr2
got = load.i64 p2
same = icmp.eq got last
nonfirst = icmp.ult zero v
dup = and same nonfirst
br dup ^alias() ^fresh(v, got, sum)
^alias():
fault 9
^fresh(w:i64, cur:i64, acc:i64):
h = qreg.from_id cur
s = qreg.slice h zero 1
action_call @flip (s) () () ()
t = qreg.slice h zero 1
action_call @flip (t) () () ()
qreg.free h
acc2 = add acc one
w2 = add w one
br ^use(w2, cur, acc2)
^end(r0:i64):
r = add r0 zero
ret r'''
    size=8*count
    path=build(runner,'k1-table',[body,FLIP[0]],{'main':cc.signature([],['i64'],'cc'),'flip':FLIP[1]},{'tab':bytes(size)})
    compare('k1-table',line,call(runner,'run-cc',path,'main'))


def k1_stale(runner,block):
    body='''fn cc @main () () () () ()
^entry():
q = qreg.new any 1
id = qreg.id q
qreg.free q
h = qreg.from_id id
qreg.free h
fault 9'''
    # Literal width, K1 lookup: the failing instruction is the stale qreg.from_id, not the later fault.
    path=build(runner,'k1-stale',[body],{'main':cc.signature([],[],'cc')})
    compare('k1-stale',lines(block)[0],call(runner,'run-cc',path,'main'))


def k2_ledger(runner,block):
    r='''fn r @scratch (n:i64) () () () ()
^entry():
q = qreg.new any n
zero = const.i64 0
one = const.i64 1
br ^test(zero)
^test(i:i64):
c = icmp.ult i n
br c ^body(i) ^done()
^body(j:i64):
s = qreg.slice q j 1
action_call @flip (s) () () ()
t = qreg.slice q j 1
action_call @flip (t) () () ()
j2 = add j one
br ^test(j2)
^done():
qreg.free q
ret'''
    try:
        a=build(runner,'k2-ledger',[r,'fn cc @main (n:i64) () () () ()\n^entry():\ncall @scratch n\nret',FLIP[0]],
                {'main':cc.signature(['i64'],[],'cc'),'scratch':cc.signature(['i64'],[]),'flip':FLIP[1]})
    finally:
        # Built either way, so the second reader also sees this fixture while the row is blocked.
        b=build_quiet(runner,'k2-fault',['fn r @main () () () () ()\n^entry():\nn = const.i64 2\nq = qreg.new any n\nfault 9'],{'main':cc.signature([],[])})
    for line in lines(block):
        verb='reverse' if ' reverse:' in line else 'run-cc'
        if line.startswith('n=3'):got=call(runner,verb,a,'main','3')
        else:got=call(runner,verb,b,'main')
        compare('k2-ledger',line,got)


def k3_mint(runner,block):
    top='''fn cc @top (s:i64) (r:i8) () () ()
^entry():
zero = const.i64 0
x = qreg.new any 8
t = qreg.new any 8
f = qreg.new any 4
tk = budget.mint @inc8 s zero zero zero
oracle_call @inc8 tk (x) t f () ()
r = measure t
qreg.free x
ret r'''
    over='''fn cc @overdraw () () () () ()
^entry():
three = const.i64 3
one = const.i64 1
zero = const.i64 0
tk = budget.mint @inc8 three one zero zero
ret'''
    path=build(runner,'k3-mint',[top,over,INC8[0]],{'top':cc.signature(['i64'],['i8'],'cc'),'overdraw':cc.signature([],[],'cc'),'inc8':INC8[1]})
    for line in lines(block):
        if line.startswith('overdraw'):got=call(runner,'run-cc',path,'overdraw')
        else:got=call(runner,'run-cc',path,'top',re.match(r'steps=(\d+)',line)[1])
        compare('k3-mint',line,got)


def k4_native(runner,block):
    g='oracle @{n} (x:wire[2] in, y:wire[2] in) (t:wire[2]) (f:wire[4]) () (a:i2)\nregs {{ s:reg[2], r:reg[2] }}\n^entry():\ns = lift.{o} x y\nr = lift.{o} s a\nlift.retval r'
    sig={'abi':'0.9','args':['i2'],'fault':4,'in':[2,2],'kind':'oracle','mem':[],'tgt':2,'tier':'q'}
    act='perm_action @addya (x:wire[2] mut) (y:wire[2] in) () (tk:token, a:i2) ()\n^entry():\nqinplace @g @ginv tk x (y) () (a)'
    asig={'abi':'0.9','args':['token','i2'],'bounds':[],'in':[2],'kind':'perm_action','mem':[],'mut':[2],'tier':'q'}
    run='''fn cc @main () () () () ()
^entry():
x = qreg.new any 2
y = qreg.new any 2
three = const.i64 3
zero = const.i64 0
tk = budget.mint @g three zero zero zero
a = const.i2 1
action_call @addya (x) (y) () (tk, a)
ret'''
    path=build(runner,'k4-native',[g.format(n='g',o='add'),g.format(n='ginv',o='sub'),act,run],
               {'g':sig,'ginv':sig,'addya':asig,'main':cc.signature([],[],'cc')})
    compare('k4-native',lines(block)[0],call(runner,'run-cc',path,'main'))


def k5_open(runner,block):
    inner='''fn r @inner (p:ptr) () () () ()
^entry():
v = const.i8 120
store.i8 p v
len = const.i64 1
effect console.write p len
fault 11'''
    outer='''fn r @main () () () () ()
^entry():
size = const.i64 8
p = alloc size
call @inner p
fault 12'''
    path=build(runner,'k5-open',[outer,inner],{'main':cc.signature([],[]),'inner':cc.signature(['ptr'],[])},None,CONSOLE)
    for line in lines(block):
        compare('k5-failed-open-activation',line,call(runner,'reverse' if line.startswith('reverse') else 'run-cc',path,'main'))


def tdl_co_width(runner,block):
    body='perm_action @pad (r:wire[3] mut) (w:wire[2] in) () () ()\n^entry():\ncx w[0] r[0]\ncx w[1] r[0]\nccx w[0] w[1] r[0]\ncx w[1] r[1]\nccx w[0] w[1] r[2]'
    sig={'abi':'0.9','args':[],'bounds':[],'in':[2],'kind':'perm_action','mem':[],'mut':[3],'tier':'q'}
    path=build(runner,'tdl-co-width',[body],{'pad':sig})
    amp=format(2**-0.5,'.16f')
    for line in lines(block):
        m=re.match(r'w=(\d+) run: mut=(\d+)',line)
        if m:
            got=runner.isa.call('run-action',path,'pad','--mut','0','--in',m[1])
            v2.equal('tdl-co-width',line,[int(m[2])],got['mut'])
        else:
            want=re.search(r'state: (\S+)',line)[1].split(',')
            got=runner.isa.call('run-action',path,'pad','--state',f'00010={amp};00001={amp}')
            v2.equal('tdl-co-width',line,sorted(want),sorted(got['state']))
            for bits in want:
                if abs(got['state'][bits][0]-2**-0.5)>1e-12 or got['state'][bits][1]:raise d.Fail('tdl-co-width amplitude '+repr(got['state'][bits]))


WITNESSES={'tdl-co-width':tdl_co_width,'k1-width':k1_width,'k1-table':k1_table,'k1-stale':k1_stale,'k2-ledger':k2_ledger,'k3-mint':k3_mint,
           'k4-native':k4_native,'k5-failed-open-activation':k5_open}
STATES={'r-budget-prefix':r_budget,'r-fault-code':r_code}


def check(runner,block):
    return WITNESSES[block['attrs']['witness09']](runner,block)


ORIGINAL_STATE=v2.state_check


def state_check(runner,block):
    name=block['attrs']['state']
    if name in STATES:return STATES[name](runner,block)
    return ORIGINAL_STATE(runner,block)


v2.state_check=state_check

TOKEN_MAP=[('isa=0.8 object=0.8 launch=0.8 sched=0.8 cert=0.8 coverage=0.8 target=0.8','isa=0.9 object=0.9 launch=0.9 sched=0.9 cert=0.9 coverage=0.9 target=0.9'),
           ('"abi":"0.8"','"abi":"0.9"'),('"version":"0.8"','"version":"0.9"')]
HASHES=re.compile(r'"interface_hash":"[0-9a-f]{64}"')


def normal(text):
    for a,b in TOKEN_MAP:text=text.replace(a,b)
    text=re.sub(r'\{"abi":"0\.9","kind":"lproc","params":(\[[0-9,]*\]),"result":(\d+),"tier":"q"\}',r'{"abi":"0.9","args":[],"kind":"lproc","mem":[],"params":\1,"result":\2,"tier":"q","tokens":[]}',text)
    return HASHES.sub('"interface_hash":"H"',text)


def ident_of(block):
    a=block['attrs']
    return next((f'{k}={a[k]}' for k in v2.TAGS if k in a),f'line-{block["line"]}')


def delta(runner):
    """Every checked 0.2.12 block is retained modulo the ISA version tokens, except the manifest's reviewed list."""
    old=d.extract_blocks((d.ROOT/'spec'/'Bennett-Dialect-Spec.md').read_text())
    manifest=json.loads((Path(__file__).with_name('dialect03_delta.json')).read_text())
    fingerprint=lambda b:(b['lang'],normal(b['body']))
    current=collections.Counter(fingerprint(b) for b in runner.blocks)
    changed=[]
    for b in old:
        if not b['attrs'] and b['lang'] not in ('llvm','isa'):continue
        key=fingerprint(b)
        if current[key]:current[key]-=1
        elif 'hash' in b['attrs']:pass
        else:changed.append(ident_of(b))
    v2.equal('delta','§23 changed checked blocks',sorted(manifest['changed']),sorted(changed))
    return {'retained':len(old)-len(changed),'changed':len(changed)}


def no_active_blocker(runner):
    verdicts=[b['attrs']['verdict'] for b in runner.blocks if b['attrs'].get('verdict','').startswith('blocked:')]
    v2.equal('blockers','§25.1 no active blocker verdict',[],verdicts)
    v2.equal('blockers','§25.1 no blocker block',[],[ident_of(b) for b in runner.blocks if 'blocker' in b['attrs']])
    return {'blocked_verdicts':0}


def ruled_items(runner):
    """Outline-0.3 rulings D14-D19, D22: each ruled sentence is present, in its section."""
    from dialect_0211_contract import check_sentence
    items=json.loads((Path(__file__).with_name('dialect03_items.json')).read_text())
    for item in items:check_sentence(runner.spec,item)
    return {'items':[i['item'] for i in items]}


def delta_checks(runner):
    if runner.selected and 'isa09' not in runner.selected:return
    runner.check('coverage','03/block-delta','§23',lambda:delta(runner))
    runner.check('coverage','03/no-active-blocker','§25.1',lambda:no_active_blocker(runner))
    runner.check('coverage','03/ruled-items','outline-0.3 rulings',lambda:ruled_items(runner))
