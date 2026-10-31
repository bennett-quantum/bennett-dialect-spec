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


def setjmp_reentry(f,site,a=None):
    """Conservative N29 continuation reachability through may-ancestor calls."""
    functions=list(a.funcs()) if a is not None else [f]
    nodes={};succ={};entries={};continuations=[];target=None
    for fun in functions:
        labels={lab:(fun.name,lab,0) for lab,_ in fun.blocks}
        if fun.blocks:entries[fun.name]=labels[fun.blocks[0][0]]
        for lab,blk in fun.blocks:
            for k,ins in enumerate(blk):
                node=(fun.name,lab,k);nodes[node]=(fun,ins)
                succ[node]=[(fun.name,lab,k+1)] if k+1<len(blk) else [labels[x] for x in re.findall(r'label %([-\w.$]+)',ins.text)]
                if ins is site:target=node
                ancestor=(fun.name==f.name or (a is not None and f.name in a.closure(fun.name)))
                if ancestor and ins.op=='call' and re.search(r'@(?:setjmp|_setjmp|sigsetjmp|__sigsetjmp|__bennett_rt_setjmp)\(',ins.text):continuations.extend(succ[node])
    if a is not None:
        for node,(fun,ins) in nodes.items():
            if ins.op not in ('call','invoke') or ' asm ' in ins.text:continue
            c=d.parse_call(ins)
            targets={c['callee'][1:]} if c['callee'].startswith('@') else a.indirect.get(id(ins),set())
            succ[node].extend(entries[n] for n in targets if n in entries)
    stack=continuations;seen=set()
    while stack:
        node=stack.pop()
        if node==target:return True
        if node in seen:continue
        seen.add(node);stack.extend(succ[node])
    return False


def entry_boundary_live(a,f,site,in_r=False,root=None):
    """May-live persistent ROOT and an augmented call/return path avoiding free.

    Return edges conservatively include every possible caller continuation.
    Thus an internal callee return alone is not an entry boundary, and frees
    in its caller can discharge the obligation.
    """
    root=root or f.name+site.res
    objects={o for (o,_,_),ats in a.memory.items() if ('R',root) in ats}
    allocas={fun.name+i.res for fun in a.funcs() for i in fun.instrs() if i.op=='alloca'}
    persistent=set(a.m.globals)|(objects-allocas)
    for fun in a.funcs():
        for ins in fun.instrs():
            if ins.op=='ret' and ins.text!='ret void':
                persistent.update(o for o,_ in a.ptrs(fun,d.typed_val(ins.text[4:])))
    # Memory reachable from persistent objects can itself retain a ROOT.
    while True:
        before=set(persistent)
        for (o,_,_),ats in a.memory.items():
            if o in persistent:persistent.update(x[1] for x in ats if x[0]=='P')
        if persistent==before:break
    returned=any(ins.op=='ret' and ins.text!='ret void' and root in a.roots(fun,d.typed_val(ins.text[4:]))
                 for fun in a.funcs() if a.nonlocal_linkage(fun.name) for ins in fun.instrs())
    if not objects & persistent and not returned:return False
    entries={fun.name for fun in a.funcs() if (fun.name in a.device or fun is f) and not re.search(r'\b(?:internal|private)\b',fun.header)}
    if in_r:
        entries=set()
        for fun in a.funcs():
            for ins,c,mk in a.marker_calls(fun):
                if mk=='reversible':entries.update(a.cands.get((id(ins),0),set()))
        if not entries:entries={f.name} # whole-program R entry
    nodes={};succ={};starts={};returns={};calls=[];target=None
    for fun in a.funcs():
        labels={lab:(fun.name,lab,0) for lab,_ in fun.blocks}
        if not fun.blocks:continue
        starts[fun.name]=labels[fun.blocks[0][0]];returns[fun.name]=[]
        for lab,blk in fun.blocks:
            for k,ins in enumerate(blk):
                node=(fun.name,lab,k);nodes[node]=(fun,ins)
                succ[node]=[(fun.name,lab,k+1)] if k+1<len(blk) else [labels[x] for x in re.findall(r'label %([-\w.$]+)',ins.text)]
                if ins is site:target=node
                if ins.op in ('ret','resume'):returns[fun.name].append(node)
                if ins.op in ('call','invoke') and ' asm ' not in ins.text:
                    c=d.parse_call(ins)
                    if c['callee']=='@__bennett_qfree' and a.roots(fun,c['args'][0][2])=={root}:succ[node]=[]
                    else:
                        targets={c['callee'][1:]} if c['callee'].startswith('@') else a.indirect.get(id(ins),set())
                        calls.append((node,targets,list(succ[node])))
    # A visible external function called by CC is not a host-entry return on
    # that edge. Summarise call/return paths with ROOT alive, then follow only
    # unmatched returns through possible ancestors of the allocation activation.
    call_info={node:(targets,after) for node,targets,after in calls}
    returned_alive=set()
    def after_call(node):
        targets,after=call_info[node]
        defined=targets & starts.keys()
        return after if not defined or targets-starts.keys() or defined & returned_alive else []
    while True:
        before=set(returned_alive)
        for name,entry in starts.items():
            queue=[entry];visited=set()
            while queue:
                node=queue.pop()
                if node in visited:continue
                visited.add(node);_,ins=nodes[node]
                if ins.op in ('ret','resume'):
                    returned_alive.add(name);break
                queue.extend(after_call(node) if node in call_info else succ[node])
        if returned_alive==before:break
    ancestors={name:[] for name in starts}
    for node,targets,after in calls:
        for name in targets & starts.keys():ancestors[name].extend(after)
    # N29 continuation cases are handled first by setjmp_reentry.
    stack=list(succ[target]) if site is not None else [starts[f.name]];seen=set()
    while stack:
        node=stack.pop()
        if node in seen:continue
        seen.add(node);fun,ins=nodes[node]
        if ins.op in ('ret','resume'):
            if fun.name in entries:return True
            stack.extend(ancestors[fun.name])
        else:stack.extend(after_call(node) if node in call_info else succ[node])
    return False


def self_disjoint(a,f,site):
    if setjmp_reentry(f,site,a):return False
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
    # Parameter roots have no allocation site and cannot inherit per-call bounds.
    for f in sorted(a.funcs(),key=lambda f:f.name not in a.reversible):
        for _,_,param in f.params:
            received=set(a.roots(f,param))
            if f.name in a.reversible:
                queue=[o for o,_ in a.ptrs(f,param)];seen=set()
                while queue:
                    obj=queue.pop()
                    if obj in seen:continue
                    seen.add(obj)
                    for (o,_,_),ats in a.memory.items():
                        if o!=obj:continue
                        received.update(x[1] for x in ats if x[0]=='R')
                        queue.extend(x[1] for x in ats if x[0]=='P')
            for root in sorted(r for r in received if r.startswith('ENTRY:')):
                if not entry_boundary_live(a,f,None,f.name in a.reversible,root):continue
                a.blockers.append(('BD-B-ISA12' if f.name in a.reversible else 'BD-B-ISA4',
                    ('BLK-4 ' if f.name in a.reversible else 'BLK-1 ')+'handle parameter may outlive an entry return in persistent memory: @'+f.name+' '+param))
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
        if setjmp_reentry(f,ins,a):
            a.blockers.append(('BD-B-ISA12' if in_r else 'BD-B-ISA4',('BLK-4 §7.5(b)' if in_r else 'BLK-1 §6.5')+' setjmp continuation re-entry: '+ins.text))
        elif entry_boundary_live(a,f,ins,in_r):
            a.blockers.append(('BD-B-ISA12' if in_r else 'BD-B-ISA4',('BLK-4 §7.5(b)' if in_r else 'BLK-1 §6.5')+' instance may outlive an entry return: '+ins.text))
        elif self_disjoint(a,f,ins):a.instance_bounds[f.name+ins.res]=1
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
                    if setjmp_reentry(caller,call,a):return None
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
