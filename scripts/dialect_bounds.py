"""§6.5 reference instance bounds: LLVM loop facts plus graph/path obligations."""
import hashlib
import re
import subprocess
from pathlib import Path
import dialect_check as d

_CACHE={}


def loop_facts(text, major=None):
    from dialect_check_v02 import headless_env,SCRATCH
    digest=hashlib.sha256((str(major)+'\n'+text).encode()).hexdigest()
    if digest in _CACHE:return _CACHE[digest]
    path=SCRATCH/('bounds-'+digest[:16]+'.ll');path.write_text(d.with_decls(text))
    facts={}
    tools=d.toolchains()
    if major:tools={major:tools[major]}
    for major,opt_dir in tools.items():
        result={};function=None
        for analysis in ('loops','scalar-evolution'):
            argv=[str(opt_dir/'opt'),f'-passes=print<{analysis}>','-disable-output',str(path)]
            p=subprocess.run(argv,capture_output=True,text=True,env=headless_env(),timeout=30)
            if p.returncode:raise d.Fail(f'§6.5 LLVM {major} loop analysis: expected exit=0; actual={p.returncode}; command={argv}; {p.stderr}')
            (SCRATCH/('bounds-'+digest[:16]+'-'+major+'-'+analysis+'.txt')).write_text(p.stderr+p.stdout)
            for line in (p.stderr+p.stdout).splitlines():
                m=re.match(r"(?:Loop info|Printing analysis .*?) for function '([^']+)':",line)
                if m:function=m[1];result.setdefault(function,{'loops':[],'counts':{}})
                if function is None:continue
                if line.startswith('Loop at depth '):
                    members=set(re.findall(r'%([-\w.$]+)',line));header=re.search(r'%([-\w.$]+)<header>',line)
                    if not header:raise d.Fail('§6.5 could not read LLVM loop header: '+line)
                    result[function]['loops'].append((header[1],members))
                m=re.match(r'Loop %([-\w.$]+): constant max backedge-taken count is (?:i\d+ )?(-?\d+)$',line)
                if m:
                    # getSmallConstantMaxTripCount returns zero for an APInt too wide
                    # for its unsigned result. Negative printed APInts are such cases.
                    backedges=int(m[2]);result[function]['counts'][m[1]]=backedges+1 if 0<=backedges<0xffffffff else None
        facts[major]=result
    _CACHE[digest]=facts
    return facts


def self_disjoint(a,f,site):
    root=f.name+site.res
    allocas={f.name+i.res for i in f.instrs() if i.op=='alloca'}
    objects={o for (o,_,_),ats in a.memory.items() if ('R',root) in ats}
    if objects-allocas:return False
    # The frame object may be passed as marker env, but may not escape F otherwise.
    for ins in f.instrs():
        if ins.op=='store':
            value,_=d.store_parts(ins)
            if any(o in objects for o,_ in a.ptrs(f,value)):return False
        if ins.op=='ret' and ins.text!='ret void':
            if any(o in objects for o,_ in a.ptrs(f,d.typed_val(ins.text[4:]))):return False
        if ins.op=='call' and ' asm ' not in ins.text:
            c=d.parse_call(ins)
            if not d.is_marker(c['callee'][1:]) and any(o in objects for arg in c['args'] for o,_ in a.ptrs(f,arg[2])):return False
    nodes={};successors={};start=None
    labels={lab:(lab,0) for lab,_ in f.blocks}
    for lab,blk in f.blocks:
        for k,ins in enumerate(blk):
            node=(lab,k);nodes[node]=ins
            successors[node]=[(lab,k+1)] if k+1<len(blk) else [labels[x] for x in re.findall(r'label %([-\w.$]+)',ins.text)]
            if ins is site:start=node
    if start is None:raise d.Fail('§6.5 allocation instruction not found')
    stack=list(successors[start]);seen=set()
    while stack:
        node=stack.pop()
        if node in seen:continue
        seen.add(node);ins=nodes[node]
        if ins.op=='call' and ' asm ' not in ins.text:
            c=d.parse_call(ins)
            if c['callee']=='@__bennett_qfree' and a.roots(f,c['args'][0][2])=={root}:continue
            targets={c['callee'][1:]} if c['callee'].startswith('@') else a.indirect.get(id(ins),set())
            if any(f.name in a.closure(n) for n in targets):return False
        if node==start or ins.op=='ret':return False
        stack+=successors[node]
    return True


def instance_rules(a):
    sites=[]
    for f in a.funcs():
        for ins,c,mk in a.marker_calls(f):
            if mk not in ('qalloc','qborrow'):continue
            root=f.name+ins.res
            stored=any(('R',root) in ats for ats in a.memory.values())
            in_r=f.name in a.reversible
            if stored or in_r:sites.append((f,ins,in_r))
    if not sites:return
    a.instance_bounds={}
    nontrivial=[]
    for f,ins,in_r in sites:
        if self_disjoint(a,f,ins):a.instance_bounds[f.name+ins.res]=1
        else:nontrivial.append((f,ins,in_r))
    if not nontrivial:return
    facts=loop_facts(a.m.text,getattr(a,'major',None))
    for f,ins,in_r in nontrivial:
        recursive=any(f.name in a.closure(n) for n in a.direct_callees(f))
        unbounded=recursive;bounds=[]
        for major,info in facts.items():
            entry=info.get(f.name,{'loops':[],'counts':{}});bound=1
            for header,members in entry['loops']:
                if ins.block in members:
                    n=entry['counts'].get(header)
                    if n is None:unbounded=True
                    else:bound*=n
            bounds.append(bound)
        # A bounded callee may still execute without bound through a caller loop.
        # The device-call-site recurrence is solved recursively; a cycle is infinity.
        def executions(name,seen):
            if name in seen:return None
            callers=[]
            for caller in a.funcs():
                if caller.name not in a.device:continue
                for call in caller.instrs():
                    if call.op not in ('call','invoke') or ' asm ' in call.text:continue
                    c=d.parse_call(call);targets={c['callee'][1:]} if c['callee'].startswith('@') else a.indirect.get(id(call),set())
                    if name not in targets:continue
                    count=executions(caller.name,seen|{name})
                    if count is None:return None
                    for major,info in facts.items():
                        loopinfo=info.get(caller.name,{'loops':[],'counts':{}})
                        for header,members in loopinfo['loops']:
                            if call.block in members:
                                n=loopinfo['counts'].get(header)
                                if n is None:return None
                                count*=n
                        # Per-major result is conservative for the finite/infinite decision.
                        break
                    callers.append(count)
            return sum(callers) if callers else 1
        E=executions(f.name,set())
        unbounded|=E is None
        if unbounded:
            a.blockers.append(('BD-B-ISA12' if in_r else 'BD-B-ISA4',('BLK-4 §7.5(b)' if in_r else 'BLK-1 §6.5')+' '+ins.text))
        else:a.instance_bounds[f.name+ins.res]=max(bounds)*E
