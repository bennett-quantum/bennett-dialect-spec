"""CC-level event execution, using independent ISA action calls per event.

Keeping calls separate is required by ISA 0.8 coarse memory windows. Python
only transports/reorders interface bits; every quantum transition runs in Rust.
"""
import collections
import json
import math
import re
import dialect_check as d
from dialect_check_v02 import equal


def dump(x):return json.dumps(x,sort_keys=True,separators=(',',':'))


def object_text(isa,path,functions,signatures,layout=None):
    symbols={str(i):{'interface_hash':'0'*64,'kind':s['kind'],'name':n,'signature':s} for i,(n,s) in enumerate(signatures.items())}
    prefix='bennett-object isa=0.8 object=0.8 launch=0.8 sched=0.8 cert=0.8 coverage=0.8 target=0.8 ptr_width=64\n\nsection symbols\n'
    tail='\n\nsection functions\n'+'\n'.join(functions)+'\n'
    if layout:tail+='\nsection layout\n'+dump(layout)+'\n'
    path.write_text(prefix+dump(symbols)+tail)
    hashes=isa.call('hash',path)
    for s in symbols.values():s['interface_hash']=hashes['symbols'][s['name']]['interface_hash']
    path.write_text(prefix+dump(symbols)+tail);isa.call('check',path)
    return path


class Session:
    def __init__(self,runner,name):
        self.runner=runner;self.name=name;self.widths=collections.OrderedDict();self.state={'': [1,0]};self.serial=0

    def alloc(self,name,width,value=0):
        if name in self.widths:raise d.Fail('TDL duplicate live register '+name)
        self.widths[name]=width
        suffix=''.join(str(value>>i&1) for i in range(width))
        self.state={bits+suffix:amp for bits,amp in self.state.items()}

    def free(self,name):
        start=sum(w for n,w in list(self.widths.items())[:list(self.widths).index(name)]);w=self.widths[name]
        if any('1' in bits[start:start+w] for bits in self.state):raise d.Fail('T-CLEAN: nonzero '+name+' at release')
        self.state={bits[:start]+bits[start+w:]:amp for bits,amp in self.state.items()};del self.widths[name]

    def apply(self,rows,oracle=None,mem=False,token=False,adjoint=False,budget=10000):
        self.serial+=1;names=list(self.widths)
        ordinary=[n for n in names if not mem or n not in ('cnt','other')]
        order=ordinary+(['cnt','other'] if mem else [])
        offsets={};off=0
        for n,w in self.widths.items():offsets[n]=(off,w);off+=w
        def reorder(bits,order):return ''.join(bits[offsets[n][0]:sum(offsets[n])] for n in order)
        state={reorder(bits,order):amp for bits,amp in self.state.items()}
        memsig=[{'A':1,'W':8,'role':'in' if oracle else 'mut'}] if mem else []
        sig={'abi':'0.8','args':['token'] if token else [],'bounds':[],'in':[],'kind':'action','mem':memsig,'mut':[self.widths[n] for n in ordinary],'tier':'q'}
        header='action @event ('+', '.join(f'{n}:wire[{self.widths[n]}] mut' for n in ordinary)+') () ('+('coh:region[1,8] '+memsig[0]['role'] if mem else '')+') ('+('tk:token' if token else '')+') ()'
        functions=[header+'\n^entry():\n'+'\n'.join(rows)];signatures={'event':sig};layout=None
        if oracle:
            function,osig,layout=oracle;functions.append(function);signatures['slice']=osig
        path=self.runner.tmp/f'{self.name}-event-{self.serial}.bisa'
        object_text(self.runner.isa,path,functions,signatures,layout)
        args=[path,'event','--state',';'.join(bits+'='+','.join(map(str,amp)) for bits,amp in state.items())]
        if token:args+=['--arg',f'token:{budget},0,256,8' if layout else f'token:{budget},0,0,0']
        if adjoint:args+=['--adjoint']
        got=self.runner.isa.call('run-action',*args)
        if 'state' not in got:raise d.Fail('run-action expected state; actual '+repr(got))
        newoffsets={};off=0
        for n in order:newoffsets[n]=(off,self.widths[n]);off+=self.widths[n]
        self.state={''.join(bits[newoffsets[n][0]:sum(newoffsets[n])] for n in names):amp for bits,amp in got['state'].items()}
        return got

    def xmask(self,name,value,controls=()):
        rows=[f'x {name}[{k}]' for k in range(self.widths[name]) if value>>k&1]
        self.controlled(rows,controls)

    def controlled(self,rows,controls=(),**kw):
        self.apply([f'qpred {c}' for c in controls]+rows+[f'qunpred {c}' for c in reversed(controls)],**kw)

    def view(self,names):
        offsets={};off=0
        for n,w in self.widths.items():offsets[n]=(off,w);off+=w
        result={}
        for bits,amp in self.state.items():
            key=tuple(int(bits[offsets[n][0]:sum(offsets[n])][::-1],2) for n in names)
            # Never discard entangled workspace while comparing a pure projection.
            rest=''.join(bits[a:a+w] for n,(a,w) in offsets.items() if n not in names)
            result[key,rest]=complex(*amp)
        return result


def oracle(kind):
    """Runtime slice bodies, independent of the stated state vectors."""
    mem=kind in ('copy','condition');width=1 if kind=='condition' else 8
    osig={'abi':'0.8','args':[],'fault':4,'in':[],'kind':'oracle','mem':[{'A':1,'W':8,'role':'in'}] if mem else [],'tgt':width,'tier':'q'}
    header=f'oracle @slice () (tgt:wire[{width}]) (fault:wire[4]) ('+('coh:region[1,8] in' if mem else '')+') ()'
    if kind=='copy':rows=['p = lift.addr @coh','lift.boundscheck p 1','v = lift.load.i8 p','one = lift.const.i8 1','r = lift.add v one','lift.retval r'];regs='p:reg[64], v:reg[8], one:reg[8], r:reg[8]'
    elif kind=='condition':rows=['p = lift.addr @coh','lift.boundscheck p 1','v = lift.load.i8 p','five = lift.const.i8 5','r = lift.icmp.eq v five','lift.retval r'];regs='p:reg[64], v:reg[8], five:reg[8], r:reg[1]'
    elif kind=='nine':rows=['r = lift.const.i8 9','lift.retval r'];regs='r:reg[8]'
    else:raise d.Fail('TDL unknown slice '+kind)
    layout={'A_tab':1,'H':13,'S_cells':8,'globals':{},'heap_base':4096,'heap_limit_max':0,'interface_regions':{'slice':{'coh':{'base':4096}} if mem else {}},'null_size':4096,'ptr_width':64}
    return header+'\nregs { '+regs+' }\n^entry():\n'+'\n'.join(rows),osig,layout


def add_constant(name,width,value):
    # Ripple increment is a permutation; high bits change before lower controls.
    rows=[]
    for bit in range(width):
        if not value>>bit&1:continue
        for k in range(width-1,bit,-1):
            controls=[f'{name}[{j}]' for j in range(bit,k)]
            rows += [f'qpred {c}' for c in controls]+[f'x {name}[{k}]']+[f'qunpred {c}' for c in reversed(controls)]
        rows.append(f'x {name}[{bit}]')
    return rows


def execute_original(runner,name,at):
    """Execute the §18.8 event prefixes at their stated checkpoint boundaries."""
    s=Session(runner,name);count={'tdl-a':1,'tdl-b':2,'tdl-d':2,'tdl-f':3,'tdl-effect':2}[name]
    for k in range(count):s.alloc('H'+str(k),1)
    if name=='tdl-effect':
        s.alloc('console',16);s.alloc('length',8);s.alloc('Phi1',4)
        s.apply(['h H0[0]']);s.apply(['cx H0[0] H1[0]']);s.xmask('console',0x0a21,('H0[0]',));s.xmask('length',2,('H0[0]',));return s
    s.alloc('cnt',8);s.alloc('other',8)
    s.apply(['h H0[0]'])
    if name in ('tdl-b','tdl-f'):s.apply(['h H1[0]'])
    # Source constant, rather than a value from state=.
    source=runner.block('example','tdl')['body'];bump=d.extract_function(d.Module(source),'bump')
    value=int(re.search(r'store i8 (\d+)',bump)[1]);s.xmask('cnt',value,('H0[0]',))
    if name=='tdl-b':
        s.alloc('m1',8);s.alloc('f1',4)
        s.controlled(['oracle_call @slice tk () m1 f1 (coh) ()'],('H1[0]',),oracle=oracle('copy'),mem=True,token=True)
        s.apply(['qpred H1[0]']+[f'cx m1[{k}] other[{k}]' for k in range(8)]+['qunpred H1[0]'])
        s.alloc('f1b',4)
        s.controlled(['oracle_call @slice tk () m1 f1b (coh) ()'],('H1[0]',),oracle=oracle('copy'),mem=True,token=True)
        s.apply(['qxor f1 f1b']);s.free('f1b')
        if at>10:
            s.free('m1');s.alloc('Phi1',4);s.apply(['qxor f1 Phi1'])
            add=int(re.search(r'add i8 %v, (\d+)',d.extract_function(d.Module(source),'add3'))[1]);s.controlled(add_constant('cnt',8,add),('H1[0]',))
    elif name=='tdl-d':
        s.alloc('history',8);s.alloc('f9',4)
        s.apply(['oracle_call @slice tk () history f9 () ()'],oracle=oracle('nine'),token=True)
        s.apply(['qexch cnt history']);s.alloc('g9',4);s.apply(['qxor f9 g9'])
        if at>7:
            s.apply(['x H1[0]']);s.apply(['qexch cnt history'])
            s.apply(['oracle_call @slice tk () history f9 () ()'],oracle=oracle('nine'),token=True);s.free('history');s.free('f9')
    elif name=='tdl-f':
        s.alloc('w',1);s.alloc('fz',4)
        s.controlled(['oracle_call @slice tk () w fz (coh) ()'],('H1[0]',),oracle=oracle('condition'),mem=True,token=True)
        s.apply(['ccx H1[0] w[0] H2[0]']);s.alloc('fzb',4)
        s.controlled(['oracle_call @slice tk () w fzb (coh) ()'],('H1[0]',),oracle=oracle('condition'),mem=True,token=True)
        s.apply(['qxor fz fzb']);s.free('fzb');s.free('w');s.alloc('Phi1',4);s.apply(['qxor fz Phi1'])
    return s


def compare_original(runner,block):
    name=block['attrs']['state'];at=int(block['attrs']['at']);s=execute_original(runner,name,at)
    expected={}
    for line in block['body'].strip().splitlines():
        m=re.fullmatch(r'\|([01]+); (.*?)> (\S+)(?: \(h = ([0-9a-f]+)\))?',line)
        if not m:raise d.Fail('TDL state syntax: '+line)
        controls=tuple(int(x) for x in m[1]);values=m[2]
        if name=='tdl-effect':
            a=re.fullmatch(r'console=([0-9a-f]+) length=(\d+), Phi1=(\d+)',values);other=(int.from_bytes(bytes.fromhex(a[1]),'little'),int(a[2]),int(a[3]))
        else:other=tuple(int(x,16) for x in values.split())
        expected[controls+other+( (int(m[4],16),) if m[4] else ())]=d.parse_amp(m[3])
    names=[n for n in s.widths if n.startswith('H')]+(['console','length','Phi1'] if name=='tdl-effect' else ['cnt']+(['other'] if name=='tdl-b' else [])+(['history'] if name=='tdl-d' and at==7 else []))
    observed={}
    for (key,rest),amp in s.view(names).items():
        if '1' in rest:raise d.Fail('TDL checkpoint has unexpected nonzero unprojected register '+rest)
        observed[key]=observed.get(key,0)+amp
    for key in expected.keys()|observed.keys():
        if abs(expected.get(key,0)-observed.get(key,0))>1e-7:raise d.Fail(f'{name} at={at}: expected {expected}; actual {observed}')


ORIGINAL={'tdl-a','tdl-b','tdl-d','tdl-f','tdl-effect'}


def assert_view(s,names,want):
    observed={}
    for (key,rest),amp in s.view(names).items():
        if '1' in rest:raise d.Fail('unexpected nonzero workspace '+rest)
        observed[key]=observed.get(key,0)+amp
    for key in want.keys()|observed.keys():
        if abs(want.get(key,0)-observed.get(key,0))>1e-7:
            raise d.Fail(f'{s.name}: expected {want}; actual {observed}')


BOUNDARIES={'compute-view','branch-views','fault-consumers','deferred-channel','inplace-param-quantum'}


def check_boundary(runner,block):
    name=block['attrs']['state'];text=block['body'];s=Session(runner,name)
    if name=='compute-view':
        tdl=runner.block('tdl',name)['body'];value=int(re.search(r'f: store (\d+)',tdl)[1]);test=int(re.search(r'@t==(\d+)',tdl)[1])
        # Retaining f's classical recorder gives use the updated value.
        s.alloc('H1',1);s.alloc('t',8);s.xmask('t',value)
        if value==test:s.apply(['x H1[0]'])
        s.xmask('t',value)
        want=int(re.search(r'\|([01]);',text)[1]);assert_view(s,['H1','t'],{(want,0):1})
    elif name=='branch-views':
        tdl=runner.block('tdl',name)['body'];a,b=map(int,re.search(r'branch w: store (\d+) @x; else: store (\d+)',tdl).groups())
        expected={int(k):int(v,16) for k,v in re.findall(r'w=(\d) -> x=([0-9a-f]+)',text)}
        for w in (0,1):
            s=Session(runner,name+str(w));s.alloc('w',1,w);s.alloc('x',8)
            s.xmask('x',a,('w[0]',));s.apply(['x w[0]']);s.xmask('x',b,('w[0]',));s.apply(['x w[0]'])
            assert_view(s,['w','x'],{(w,expected[w]):1})
        # Forked workspace arms select their own store, rather than seeing the
        # other arm's updated private memory. Execute the lifted select in Rust.
        from dialect_map import Mapper
        source='define i8 @select(i1 %w) {\n %r = select i1 %w, i8 1, i8 2\n ret i8 %r\n}\n'
        path=runner.tmp/'branch-workspace.bisa';mapper=Mapper(source,'@select','IN(1,zext);tgt=8','null_size=4096 heap_base=4096 heap_limit_max=0 stack max 32')
        path.write_text(mapper.run(runner.isa,path))
        for w,v in re.findall(r'w=(\d) -> payload=(\d+)',text):
            got=runner.isa.call('run-oracle',path,'ref','--input',w);equal(name,'workspace select',int(v),int(got['payload']))
    elif name=='fault-consumers':
        s.alloc('X',8,5);s.alloc('t',8);s.alloc('f',4);s.alloc('success',1);s.alloc('Phi',4)
        s.apply(['oracle_call @slice tk () t f () ()'],oracle=oracle('nine'),token=True,budget=0)
        # All-code-zero success, including the negative branch. The same exact
        # reversible computation cleans the flag after its final consumer.
        flag=[f'x f[{k}]' for k in range(4)]+[f'qpred f[{k}]' for k in range(4)]+['x success[0]']+[f'qunpred f[{k}]' for k in range(3,-1,-1)]+[f'x f[{k}]' for k in range(3,-1,-1)]
        s.apply(flag);s.controlled(['qexch X t'],('success[0]',));s.apply(flag);s.apply(['qxor f Phi'])
        code=int(re.search(r'code=(\d+)',text)[1]);assert_view(s,['X','t','f','Phi'],{(5,0,code,code):1})
    elif name=='deferred-channel':
        s.alloc('q',1);s.alloc('record',1);s.apply(['h q[0]']);s.apply(['cx q[0] record[0]']);s.apply(['h q[0]'])
        probabilities=[0.,0.]
        for (key,_),amp in s.view(['q','record']).items():probabilities[key[0]]+=abs(amp)**2
        expected=[float(re.search(r'P\('+str(k)+r'\)=1/(\d+)',text)[1])**-1 for k in (0,1)]
        for want,got in zip(expected,probabilities):
            if abs(want-got)>1e-7:raise d.Fail(f'deferred channel expected {expected}; actual {probabilities}')
    elif name=='inplace-param-quantum':
        source=runner.block('example',name)['body'];module=d.Module(source)
        operations=[]
        for fn in ('addk','subk'):
            operations.append(next(i.op for i in module.funcs[fn].instrs() if i.op in ('add','sub')))
        def pair_oracle(op):
            sig={'abi':'0.8','args':[],'fault':4,'in':[8,8],'kind':'oracle','mem':[],'tgt':8,'tier':'q'}
            function=f'oracle @slice (x:wire[8] in, y:wire[8] in) (tgt:wire[8]) (fault:wire[4]) () ()\nregs {{ r:reg[8] }}\n^entry():\nr = lift.{op} x y\nlift.retval r'
            return function,sig,None
        for superposed in (False,True):
            s=Session(runner,name+str(superposed));s.alloc('x',8,5);s.alloc('y',8,0 if superposed else 7);s.alloc('t',8);s.alloc('f',4)
            if superposed:s.apply(['h y[0]'])
            s.apply(['oracle_call @slice tk (x, y) t f () ()'],oracle=pair_oracle(operations[0]),token=True)
            s.apply(['qexch x t'])
            s.apply(['oracle_call @slice tk (x, y) t f () ()'],oracle=pair_oracle(operations[1]),token=True)
            s.free('t');s.free('f')
            if superposed:want={(5,0):1/math.sqrt(2),(6,1):1/math.sqrt(2)}
            else:
                x,y=map(int,re.search(r'-> x=(\d+),y=(\d+)',text).groups());want={(x,y):1}
            assert_view(s,['x','y'],want)
    else:raise d.Fail('unimplemented TDL boundary '+name)


WRAPPERS={'wide-delivery','entry-backing','region-two-measure-candidates','clean-predicate','generation-budget'}


def check_wrapper(runner,block):
    name=block['attrs']['state'];text=block['body']
    if name=='clean-predicate':
        from dialect_map import Mapper
        source='define i1 @f(i1 %x) {\n %c = icmp ne i1 %x, 0\n %v = xor i1 %x, 1\n %r = select i1 %c, i1 %v, i1 %x\n ret i1 %r\n}\n'
        path=runner.tmp/'clean-predicate.bisa';mapper=Mapper(source,'@f','IN(1,zext);tgt=1','null_size=4096 heap_base=4096 heap_limit_max=0 stack max 32');path.write_text(mapper.run(runner.isa,path))
        images=[]
        for x in (0,1):
            got=runner.isa.call('run-oracle',path,'ref','--input',x);equal(name,'out of place fault',0,int(got['code']));images.append(int(got['payload']))
        expected=json.loads(re.search(r'visible images (\[[^]]+\])',text)[1]);equal(name,'image vector',expected,images)
        verdict='accept' if len(set(images))==len(images) else 'reject:BD-E-COHERENT-OVERWRITE'
        equal(name,'TDL-5 total bijection',re.search(r'verdict=(\S+);',text)[1],verdict)
    elif name=='region-two-measure-candidates':
        from dialect_check_v02 import recognise
        source=runner.block('example',name);verdict,a=recognise(d.with_decls(source['body']))
        equal(name,'candidate-set module verdict','accept',verdict)
        cs=a.first_candidates();equal(name,'dispatch candidates',set(re.search(r'candidates=\{([^}]+)\}',text)[1].split(',')),cs)
        for target in cs:
            function=a.m.funcs[target]
            invalid=any(c['callee']=='@__bennett_measure' for i in function.instrs() if i.op=='call' for c in [d.parse_call(i)])
            if not invalid:raise d.Fail('expected invalid measuring action candidate '+target)
            signature={'abi':'0.8','args':[],'fault':4,'in':[],'kind':'oracle','mem':[],'tgt':1,'tier':'q'}
            path=runner.tmp/(name+'-'+target+'.bisa')
            object_text(runner.isa,path,['oracle @ref () (tgt:wire[1]) (fault:wire[4]) () ()\n^entry():\nfault 4'],{'ref':signature})
            got=runner.isa.call('run-oracle',path,'ref','--input','')
            equal(name+'/'+target,'T-REGION-INVALID',int(re.search(r'code=(\d+)',text)[1]),int(got['code']))
    elif name=='entry-backing':
        # The fixed replay microvector provides the runtime closure; load its
        # replayed backing byte instead of performing the subsequent malloc.
        from dialect_check_v02 import Interpreter
        source=runner.block('object','entry-stack')['body']
        source=source.replace('r = lift.call @L3 ()','r = lift.const.i64 4096\nlift.boundscheck r 1\nr = lift.load.i8 r')
        # The return register needs a separate i8 carrier and explicit extension.
        source=source.replace('r:reg[64] }','r:reg[64], byte:reg[8] }',1).replace('r = lift.load.i8 r','byte = lift.load.i8 r\nr = lift.zext.i64 byte')
        path=runner.tmp/'entry-backing.bisa';path.write_text(source)
        symbols=json.loads(source.split('section symbols\n')[1].splitlines()[0]);hs=runner.isa.call('hash',path)
        for sym in symbols.values():sym['interface_hash']=hs['symbols'][sym['name']]['interface_hash']
        source=source.replace(source.split('section symbols\n')[1].splitlines()[0],dump(symbols));path.write_text(source);runner.isa.call('check',path)
        vector=runner.block('run','entry-stack')['body'];mem=re.search(r'mem=s0:([0-9a-f]+)',vector)[1]
        got=runner.isa.call('run-oracle',path,'ref','--input','','--mem','s0='+mem,'--budget','200,64,64,2')
        equal(name,'replayed caller byte',int(re.search(r'payload=(\d+)',text)[1]),int(got['payload']));equal(name,'replay code',0,int(got['code']))
        # Release a 32-byte basis snapshot by two independent 128-bit slice
        # calls, retaining the classical byte image through both unpreparations.
        size=int(re.search(r'release (\d+) bytes',text)[1]);data=bytes.fromhex(mem)[:size];s=Session(runner,name)
        for k in range(0,size,16):
            n='chunk'+str(k//16);value=int.from_bytes(data[k:k+16],'little');s.alloc(n,128,value);s.xmask(n,value);s.free(n)
        equal(name,'snapshot release cleanliness',{'':[1,0]},s.state)
    elif name=='wide-delivery':
        n,value=map(int,re.search(r'OUT\[(\d+)\]=(\d+)',text).groups());value=int(str(value),16)
        widths=[min(128,8*n-k) for k in range(0,8*n,128)]
        signatures={};functions=[]
        # Every variant computes every projection before selecting its retval.
        # Consequently every budget boundary is identical across variants.
        for selected,w in enumerate(widths):
            namej='W'+str(selected);signatures[namej]={'abi':'0.8','args':[],'fault':4,'in':[],'kind':'oracle','mem':[],'tgt':w,'tier':'q'}
            rows=[]
            for j,pw in enumerate(widths):rows.append(f'p{j} = lift.const.i{pw} '+str(int.from_bytes(bytes([value])*(pw//8),'little')))
            functions.append(f'oracle @{namej} () (tgt:wire[{w}]) (fault:wire[4]) () ()\nregs {{ '+', '.join(f'p{j}:reg[{pw}]' for j,pw in enumerate(widths))+' }\n^entry():\n'+'\n'.join(rows)+f'\nlift.retval p{selected}')
        path=runner.tmp/'wide-delivery.bisa';object_text(runner.isa,path,functions,signatures)
        expected=bytes.fromhex(re.search(r'target=([0-9a-f]+)',text)[1]);observed=bytearray()
        for j,w in enumerate(widths):
            for budget in range(len(widths)+1):
                got=runner.isa.call('run-oracle',path,'W'+str(j),'--input','','--budget',budget)
                equal(name,'common prefix code',1,int(got['code']));equal(name,'common failure payload',0,int(got['payload']))
            got=runner.isa.call('run-oracle',path,'W'+str(j),'--input','','--budget',len(widths)+1)
            equal(name,'delivery success',0,int(got['code']));observed+=int(got['payload']).to_bytes(w//8,'little')
        equal(name,'all projections delivered',expected,bytes(observed))
    elif name=='generation-budget':
        from dialect_state import run_native
        src=runner.block('tdl',name)['body'];steps=int(re.search(r'steps=(\d+)',src)[1])
        # Native bounded G executes the actual branch loop; its emitted fault is
        # applied under the invocation control by an independent quantum action.
        driver=f'int main(void){{unsigned left={steps},executed=0; for(;;){{if(!left){{printf("[%u,1]\\n",executed);break;}} --left;++executed;}} return 0;}}'
        run_native(runner,name,'',driver,[[steps,1]])
        for control in (0,1):
            s=Session(runner,name+str(control));s.alloc('control',1,control);s.alloc('Phi',4)
            s.xmask('Phi',1,('control[0]',));expected=int(re.search('control='+str(control)+r' -> Phi=(\d+)',text)[1]);assert_view(s,['control','Phi'],{(control,expected):1})
    else:raise d.Fail('unimplemented wrapper vector '+name)


def original_artifact(runner,name):
    """TDL-3 lowering for the five worked LLVM generation shapes.

    Templates name the outlined slices; arithmetic constants, allocation/gate
    order and region calls are read from the LLVM source, never from tdl=.
    """
    source=runner.block('example','tdl-effect' if name=='tdl-effect' else 'tdl')['body'];m=d.Module(source)
    entry={'tdl-a':'tdl_a','tdl-b':'tdl_b','tdl-d':'tdl_d','tdl-f':'tdl_f','tdl-effect':'tdl_e'}[name]
    handles={};events=[];record=[];prefix=[]
    def integer(fn,pattern):
        match=re.search(pattern,d.extract_function(m,fn))
        if not match:raise d.Fail('TDL source shape does not match '+fn+': '+pattern)
        return int(match[1])
    for i in m.funcs[entry].instrs():
        if i.op!='call':continue
        c=d.parse_call(i);callee=c['callee'];args=c['args']
        if callee=='@__bennett_qalloc':
            h='H'+str(len(handles));handles[i.res]=h;events.append('qalloc '+h+' '+args[1][2])
        elif callee=='@__bennett_gate':
            events.append({1:'x',2:'h'}[int(args[0][2])]+' '+handles[args[1][2]]+'.'+args[2][2])
        elif callee=='@__bennett_ctrl':
            target=args[2][2][1:];ctrl=handles[args[0][2]]+'.'+args[1][2]
            if target=='bump':
                k=integer(target,r'store i8 (\d+), ptr @cnt');mask=f'0x{k:02x}'
                events.append(f'xmask @cnt+0 {mask} ctrl {ctrl}')
                if name=='tdl-a':prefix=[f'@bump: G = {{ store i8 {k}, ptr @cnt -> xmask @cnt+0 {mask} }}, slices = {{}}']
            elif target=='copy1':
                k=integer(target,r'add i8 %v, (\d+)')
                prefix.append(f'@copy1 (signature: @cnt may-Co, @other Cl): slice O1 = {{ %v = load i8, ptr @cnt; %w = add i8 %v, {k} }} with ARG c (the old byte of @other), MEM_IN coh, output m:8 = c xor %w; store i8 %w, ptr @other -> TDL-5(a) with a Co value')
                events += [f'slice O1 args(0x00) mem(coh) -> m1:8 f1:4 ctrl {ctrl}',f'xstore @other+0 m1 ctrl {ctrl} success(f1)',f'slice O1 args(0x00) mem(coh) -> m1 f1b:4 ctrl {ctrl}','qxor f1 f1b','qfree f1b','qfree m1','firstfault (f1) -> Phi1:4']
            elif target=='add3':
                k=integer(target,r'add i8 %v, (\d+)');prefix.append(f'@add3 (signature: @cnt may-Co): {{ %v = load; %w = add i8 %v, {k}; store i8 %w, ptr @cnt }} -> TDL-5(b) perm add.i8 with k = {k}')
                events.append(f'perm add.i8 @cnt+0 k={k} ctrl {ctrl}')
            elif target=='maybe':
                k=integer(target,r'icmp eq i8 %v, (\d+)')
                prefix.append(f'@maybe (signature: @cnt may-Co): slice Oz = {{ %v = load i8, ptr @cnt; %z = icmp eq i8 %v, {k} }} output w:1; the gate in %yes is control-dependent on %z -> issued under qpred w')
                events += [f'slice Oz mem(coh) -> w:1 fz:4 ctrl {ctrl}',f'x H2.0 ctrl {ctrl} w success(fz)',f'slice Oz mem(coh) -> w fzb:4 ctrl {ctrl}','qxor fz fzb','qfree fzb','qfree w','firstfault (fz) -> Phi1:4']
            elif target=='loud':
                body=d.extract_function(m,target)
                if not re.search(r'__bennett_gate\(i32 1,',body) or '@__bennett_effect_console_write' not in body:raise d.Fail('TDL loud shape changed')
                image=re.search(r'constant \[\d+ x i8\] c"([^"]+)"',source)[1]
                image=re.sub(r'\\([0-9a-fA-F]{2})',lambda m:chr(int(m[1],16)),image).encode().hex()
                prefix.append('@loud: G = { load of %t; gate marker -> x }; bound console -> reversible append (TDL-12)')
                events += [f'x H1.0 ctrl {ctrl}',f'perm console.append bytes={image} ctrl {ctrl}','firstfault () -> Phi1:4']
            else:raise d.Fail('TDL unimplemented region shape '+target)
        elif callee=='@__bennett_compute':
            f,use=args[0][2][1:],args[1][2][1:];k=integer(f,r'store i8 (\d+), ptr @cnt')
            if f!='set9' or use!='flip' or k!=9:raise d.Fail('TDL compute shape changed')
            prefix.append(f'@set9 inside compute f (signature: @cnt may-Co): slice O9 = {{ the constant {k} }} output h:8; store i8 {k}, ptr @cnt -> TDL-5(c) xchg')
            events += ['slice O9 -> h:8 f9:4','xchg @cnt+0 h success(f9)','copy f9 -> g9:4','x H1.0','xchg @cnt+0 h success(f9)','slice O9 -> h f9','qfree h','qfree f9']
        elif callee=='@settle':
            if name=='tdl-a':events+=['observe @cnt+0 1','observe @other+0 1']
            else:break
        elif callee=='@reset':
            if name=='tdl-a':events.append('measure '+handles[args[0][2]]+'.0')
            break
    title='events of @'+entry+(' up to the observes:' if name in ('tdl-b','tdl-d','tdl-f') else ':')
    return '\n'.join(prefix+[title]+events)


def check_tdl(runner,block):
    name=block['attrs']['tdl'];text=block['body']
    if name in ORIGINAL:
        equal(name,'TDL-3 partition and events',d.collapse(text),d.collapse(original_artifact(runner,name)))
    elif name=='compute-view':
        value=int(re.search(r'f: store (\d+) @t',text)[1]);test=int(re.search(r'@t==(\d+)',text)[1])
        generated=[f'xmask @t+0 0x{value:02x}']+(['x H1.0'] if value==test else [])+[f'xmask @t+0 0x{value:02x}']
        equal(name,'retained recorder',d.collapse(text)[1:],generated)
    elif name=='branch-views':
        a,b=map(int,re.search(r'branch w: store (\d+) @x; else: store (\d+)',text).groups())
        equal(name,'forked recorders',d.collapse(text)[1:3],[f'xmask @x+0 0x{a:02x} ctrl w',f'xmask @x+0 0x{b:02x} ctrl not-w'])
        if 'slice select(w,1,2)' not in text:raise d.Fail('TDL private workspace select missing')
    elif name=='inplace-param-quantum':
        source=runner.block('example',name)['body'];m=d.Module(source)
        if not any(i.op=='add' for i in m.funcs['addk'].instrs()) or not any(i.op=='sub' for i in m.funcs['subk'].instrs()):raise d.Fail('§8.7 parameterised pair shape changed')
        if 't=x+y mod 256' not in text or 't=x_old xor (x-y)=0' not in text or 'every region call controlled under ctrl' not in text:raise d.Fail('§8.7 CC expansion artefact mismatch')
    elif name=='generation-budget':
        if not re.search(r'entry: br label loop; loop: br label loop',text):raise d.Fail('G source shape changed')
        steps=int(re.search(r'steps=(\d+)',text)[1]);words={2:'two'}
        if f'execute {words.get(steps,str(steps))} branches' not in text or 'next branch emits fault 1 under invocation control, stop' not in text:raise d.Fail('TDL-9 bounded G artefact mismatch')
    else:raise d.Fail('unimplemented TDL artefact '+name)
    companions=[b for b in runner.blocks if b['attrs'].get('state')==name]
    if not companions:raise d.Fail('TDL artefact has no executable state witness '+name)
    for b in companions:
        if name in ORIGINAL:compare_original(runner,b)
        elif name in BOUNDARIES:check_boundary(runner,b)
        elif name in WRAPPERS:check_wrapper(runner,b)
        else:raise d.Fail('unimplemented TDL state companion '+name)
