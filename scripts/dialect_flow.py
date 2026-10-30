"""Finite monotone points-to/provenance analysis, dialect §5 PT1–PT12.

Atoms use P(object,offset), F(symbol), R(root) and T (unknown non-handle data).
Array residue classes are enumerated when small, preserving their extent. Large
classes use (stride,residue,lo,hi); the containment tests retain that extent.
"""
import itertools
import math
import re
import dialect_check as d

TOP = ('T',)


def union(*sets):
    out = set().union(*sets)
    ints = {x for x in out if x[0]=='I'}
    if len(ints)>4096:
        out -= ints
        out.add(TOP)
    return frozenset(out)


def overlap(a, n, b, m):
    if a == '*' or b == '*': return True
    if isinstance(a, tuple):
        stride, residue, lo, hi = a
        return any((x-residue)%stride == 0 for x in range(max(lo,b-n+1),min(hi,b+m)))
    if isinstance(b, tuple): return overlap(b,m,a,n)
    return a < b+m and b < a+n


class Flow:
    def av(self, f, val, ty=None):
        val = val.strip()
        if val.startswith('%'): return self.values.get((f.name,val), {})
        if val.startswith('getelementptr (') and val.endswith(')'):
            return self.gep(f,'getelementptr '+val[len('getelementptr ('):-1])
        if val.startswith('@'):
            name = val[1:]
            if name in self.m.funcs or name in self.m.aliases: return {0:frozenset({('F',name)})}
            if name in self.m.globals: return {0:frozenset({('P',name,0)})}
        if val in ('null','zeroinitializer','undef','poison'): return {k:frozenset({('I',0)}) for k in range(ty[1] if ty and ty[0] in ('arr','vec') else 1)}
        if re.fullmatch(r'-?\d+',val): return {0:frozenset({('I',int(val)%(1<<64))})}
        if val in ('true','false'): return {0:frozenset({('I',int(val=='true'))})}
        if val.startswith(('<','{','[')) and ty and ty[0] in ('vec','arr','struct'):
            return {k:union(*self.av(f,d.typed_val(x)).values()) for k,x in enumerate(d.split_top(val[1:-1]))}
        return {0:frozenset({TOP})}

    def atoms(self,f,v): return union(*self.av(f,v).values())
    def ptrs(self,f,v): return {x[1:] for x in self.atoms(f,v) if x[0]=='P'}
    def roots(self,f,v): return {x[1] for x in self.atoms(f,v) if x[0]=='R'}

    def put(self,f,val,lanes):
        if val is None: return False
        key=(f.name,val); old=self.values.get(key,{})
        new=dict(old)
        for lane,atoms in lanes.items(): new[lane]=union(old.get(lane,()),atoms)
        if new!=old:
            self.values[key]=new
            return True
        return False

    def slot(self,obj,off,size,atoms,width=None):
        key=(obj,off,size); widths=self.memory_widths.setdefault(key,set());new_width=(width or 8*size) not in widths
        widths.add(width or 8*size)
        old=self.memory.get(key,frozenset())
        new=union(old,atoms)
        if new!=old:
            self.memory[key]=new
            return True
        return new_width

    def immutable_image(self,obj):
        g=self.m.globals.get(obj)
        if not g or not re.search(r'\bconstant\b',g['text']):return None
        def encode(t,v):
            n=d.tsize(t,self.pw)
            if v in ('zeroinitializer','null'):return bytes(n)
            if t[0]=='int':return (int(v)%(1<<t[1])).to_bytes(n,self.byteorder)
            if t[0]=='arr':return b''.join(encode(t[2],d.typed_val(x)) for x in d.split_top(v[1:-1]))
            raise ValueError('image contains relocations or unsupported representation')
        try:return encode(g['type'],g['init'])
        except (ValueError,OverflowError):return None

    def getmem(self,ptrs,size,width=None):
        result=frozenset()
        for obj,off in ptrs:
            image=self.immutable_image(obj)
            if image is not None and isinstance(off,int) and 0<=off and off+size<=len(image):
                result=union(result,{('I',int.from_bytes(image[off:off+size],self.byteorder)%(1<<(width or 8*size)))})
                continue
            if obj=='EXT': result=union(result,{TOP})
            for (o,k,n),a in self.memory.items():
                if o!=obj or not overlap(off,size,k,n):continue
                # Provenance survives partial accesses, so handle_rules can reject
                # them. Component integers/functions/pointers are not whole values.
                if all(x[0]=='B' for x in a) and isinstance(off,int) and isinstance(k,int) and k<=off and off+size<=k+n:
                    result=union(result,{('I',int.from_bytes(bytes([x[1]])*size,self.byteorder)) for x in a})
                elif isinstance(off,int) and off==k and size==n and self.memory_widths.get((o,k,n),{8*n})=={width or 8*size}:result=union(result,a)
                else:result=union(result,{x for x in a if x[0] in ('R','C')},{TOP})
        return result

    def type_width(self,t): return self.pw if t[0]=='ptr' else t[1] if t[0]=='int' else 8*d.tsize(t)

    def pointer_widths(self,space=0):
        layout=re.search(r'target datalayout = "([^"]+)"',self.m.text)
        entries={int(m[1] or 0):(int(m[2]),int(m[5] or m[2])) for m in
                 re.finditer(r'(?:^|-)p(\d*):(\d+):(\d+)(?::(\d+))?(?::(\d+))?(?=-|$)',layout[1] if layout else '')}
        return entries.get(space,entries.get(0,(64,64)))

    def gep(self,f,body):
        rest=re.sub(r'^getelementptr\s+(?:(?:inbounds|nusw|nuw)\s+)*','',body)
        parts=d.split_top(rest);t=d.parse_type(parts[0])[0]
        pt=d.parse_type(parts[1])[0];P,I=self.pointer_widths(pt[1] if len(pt)>1 else 0);M=1<<I
        base=self.atoms(f,d.typed_val(parts[1]));deltas={0};stride=0
        for i,part in enumerate(parts[2:]):
            vals=self.ints(f,d.typed_val(part));it=d.parse_type(part)[0]
            if i>0 and t[0]=='struct':
                if vals=='TOP' or len(vals)!=1:raise d.Fail('PT2: variable struct field (LLVM should reject)')
                k=next(iter(vals));ds={d.gep_offset(t,[0,k])%M};t=t[1][k]
            else:
                t=t if i==0 else t[2];sz=d.tsize(t,P)
                if vals=='TOP':ds=None
                else:
                    def index(k):
                        k%=1<<it[1]
                        return k-(1<<it[1]) if k&(1<<(it[1]-1)) else k
                    ds={(index(k)*sz)%M for k in vals}
            if ds is None:
                stride=math.gcd(stride or M,sz,M)
                deltas={a%stride for a in deltas}
            else:
                modulus=stride or M
                if len(deltas)*len(ds)>4096:
                    a0=min(deltas);b0=min(ds)
                    stride=math.gcd(modulus,*(a-a0 for a in deltas),*(b-b0 for b in ds))
                    deltas={(a0+b0)%stride}
                else:deltas={(a+b)%modulus for a in deltas for b in ds}
        # Zero Delta preserves the complete AV, including ROOT provenance.
        if not stride and deltas=={0}:return {0:base}
        out={x for x in base if x[0]=='R'}
        if any(x[0] not in ('P','R') for x in base):out.update({('P','EXT','*'),TOP})
        for atom in base:
            if atom[0]!='P':continue
            _,obj,off=atom;extent=self.object_sizes.get(obj)
            if obj=='EXT' or off=='*' or isinstance(off,tuple):
                out.update({('P',obj,'*'),('P','EXT','*'),TOP});continue
            if stride:
                # Unknown indices range over all bit patterns, never array bounds.
                if extent is not None:
                    for residue in {(off+a)%stride for a in deltas}:
                        if (extent+stride-1)//stride<=4096:out.update(('P',obj,k) for k in range(residue,extent,stride))
                        else:out.add(('P',obj,(stride,residue,0,extent)))
                else:out.add(('P',obj,'*'))
                out.update({('P','EXT','*'),TOP});continue
            # Base low bits are unknown. Both carry alternatives are required;
            # alignment rules out impossible ones. Addition keeps bits above I.
            text=self.m.globals[obj]['text'] if obj in self.m.globals else ''
            align=re.search(r'\balign (\d+)',text);A=min(M,int(align[1])) if align else 1
            low=off%A
            for delta in deltas:
                signed=delta-M if delta>=M//2 else delta
                # A live allocation cannot straddle the full P-bit address
                # space. Interior I=P addresses therefore need no unknown
                # base-bit alternative; low-I subranges may still wrap.
                if I==P and extent is not None and 0<=off+signed<=extent:
                    out.add(('P',obj,off+signed));continue
                offsets=[]
                if low < M-delta:offsets.append(off+delta)
                if low+((M-1-low)//A)*A >= M-delta:offsets.append(off+delta-M)
                for k in offsets:
                    if extent is None or 0<=k<=extent:out.add(('P',obj,k))
                    if extent is None or k<0 or k>=extent:out.update({('P','EXT','*'),TOP})
        return {0:frozenset(out)}

    @staticmethod
    def shift(off,delta):
        if off=='*': return off
        if isinstance(off,tuple):
            s,r,lo,hi=off;return (s,(r+delta)%s,lo+delta,hi+delta)
        return off+delta

    def ints(self,f,v):
        from dialect_check_v02 import value_set
        atoms=self.atoms(f,v)
        ints={x[1] for x in atoms if x[0]=='I'}
        if TOP not in atoms and ints and len(ints)==len(atoms): return ints
        return value_set(self.m,f,v)

    def resolve(self,name,seen=None):
        original=name; visited=set()
        while True:
            if name in visited: return self.m.resolve_alias(original)
            visited.add(name)
            name=self.m.resolve_alias(name)
            f=self.m.funcs.get(name)
            if not f or not f.is_def: return name
            ins=list(f.instrs())
            if len(f.blocks)!=1 or len(ins)!=2 or ins[0].op!='call' or ins[1].op!='ret': return name
            if ' asm ' in ins[0].text:return name
            c=d.parse_call(ins[0]);target=c['callee'][1:]
            if not c['callee'].startswith('@') or target not in self.m.funcs:return name
            if c['bundles'] or c['cc'] not in (None,'ccc') or [a[2] for a in c['args']]!=[p[2] for p in f.params]:return name
            if self.m.funcs[target].ftype()!=f.ftype():return name
            if ins[1].text!='ret void' and d.typed_val(ins[1].text[4:])!=ins[0].res:return name
            name=target

    def address_used(self,name):
        pattern=re.compile('@'+re.escape(name)+r'(?![-\w.$])')
        for g in self.m.globals.values():
            if pattern.search(g['text']):return True
        if name in self.m.aliases.values():return True
        for f in self.funcs():
            for ins in f.instrs():
                if not pattern.search(ins.text):continue
                if ins.op in ('call','invoke') and ' asm ' not in ins.text:
                    c=d.parse_call(ins)
                    if c['callee']=='@'+name and not any(pattern.search(x[2]) for x in c['args']):continue
                return True
        return False

    def candidates(self,f,v,kind=None,ctype=None):
        atoms=self.atoms(f,v); names={a[1] for a in atoms if a[0]=='F'}
        if TOP in atoms or any(a[0]=='P' for a in atoms):
            for name,fn in self.m.funcs.items():
                ok=(kind not in ('action','reversible') or fn.ftype()=='void (ptr)')
                if ctype:ok=fn.ftype()==ctype
                if ok and not d.is_marker(name) and self.address_used(name):names.add(name)
        return {self.resolve(n) for n in names}

    def first_callees(self):
        return next(iter(self.indirect.values()),set())

    def analyse(self):
        layout=re.search(r'target datalayout = "([^"]+)"',self.m.text)
        self.byteorder='big' if layout and layout[1].startswith('E') else 'little'
        self.values={};self.memory={};self.memory_widths={};self.indirect={};self.cands={}; self.blockers=[]
        self.object_sizes={n:d.tsize(g['type']) for n,g in self.m.globals.items()}
        for f in self.funcs():
            for i in f.instrs():
                if i.op=='alloca':
                    ps=d.split_top(i.text.split('alloca ',1)[1]);ty=d.parse_type(ps[0])[0];count=1
                    if len(ps)>1 and ps[1].startswith('i'):
                        c=d.typed_val(ps[1]);count=int(c) if c.isdigit() else None
                    if count is not None:self.object_sizes[f.name+i.res]=d.tsize(ty)*count
        self.pw=int(re.search(r'(?:^|-)p:(\d+)',self.m.text)[1]) if re.search(r'(?:^|-)p:(\d+)',self.m.text) else 64
        for name,g in self.m.globals.items():
            t=g['type']; init=g['init'] or 'undef'
            fake=next(iter(self.funcs()), d.Func());fake.name=fake.name or 'global'
            lanes=self.av(fake,init,t)
            if t[0] in ('arr','vec'):
                if init=='zeroinitializer':lanes={k:{('I',0)} for k in range(t[1])}
                sz=d.tsize(t[2],self.pw)
                for k,atoms in lanes.items():self.slot(name,k*sz,sz,atoms,self.type_width(t[2]))
            else:self.slot(name,0,d.tsize(t,self.pw),union(*lanes.values()),self.type_width(t))
        # PT11 host roots. Handle candidate roots are activated below only at marker operands.
        for f in self.funcs():
            if self.nonlocal_linkage(f.name):
                for idx,(ty,_,v) in enumerate(f.params):
                    if v:self.put(f,v,{0:{('P','EXT','*'),('C',f'ENTRY:{f.name}:{idx}')} if ty[0]=='ptr' else {TOP}})
        for iteration in range(100):
            changed=False
            for f in self.funcs():
                for ins in f.instrs():changed |= self.flow_step(f,ins)
            if not changed:break
        else:raise d.Fail('PT1–PT12: fixpoint did not converge within 100 iterations')
        self.device={f.name for f in self.funcs() if any(self.marker_calls(f))}
        self.device |= set().union(set(),*self.cands.values())
        for _ in range(len(self.m.funcs)):
            before=set(self.device)
            for f in self.funcs():
                if f.name in self.device:
                    self.device.update(self.direct_callees(f))
                    for ins in f.instrs():self.device.update(self.indirect.get(id(ins),set()))
            if self.device==before:break
        # §6.6 candidate ROOT(E,i) atoms survive exactly when a bitwise copy
        # reaches a marker handle operand. Ordinary pointer arithmetic does not
        # manufacture entry-handle provenance.
        active=set()
        for f in self.funcs():
            for ins,c,mk in self.marker_calls(f):
                for k in d.HANDLE_OPS[mk]:
                    active|={x[1] for x in self.atoms(f,c['args'][k][2]) if x[0]=='C'}
        def activate(atoms):
            return frozenset(('R',a[1]) if a[0]=='C' and a[1] in active else a
                             for a in atoms if a[0]!='C' or a[1] in active)
        self.values={k:{lane:activate(ats) for lane,ats in v.items()} for k,v in self.values.items()}
        self.memory={k:activate(ats) for k,ats in self.memory.items()}
        for _ in range(100):
            changed=False
            for f in self.funcs():
                for ins in f.instrs():changed |= self.flow_step(f,ins)
            if not changed:break
        self.base={(fn,v):frozenset(x[1:] for x in union(*lanes.values()) if x[0]=='P') for (fn,v),lanes in self.values.items()}
        self.prov={(fn,v):{k:frozenset(x[1] for x in a if x[0]=='R') for k,a in lanes.items()} for (fn,v),lanes in self.values.items()}

    def flow_step(self,f,ins):
        op=ins.op;body=ins.text.split(' = ',1)[-1];changed=False;lanes={}
        if op=='alloca':lanes={0:{('P',f.name+ins.res,0)}}
        elif op=='getelementptr':lanes=self.gep(f,body)
        elif op in ('phi','select'):
            for v in self.value_operands(ins):
                for k,ats in self.av(f,v).items():lanes[k]=union(lanes.get(k,()),ats)
        elif op in ('ptrtoint','inttoptr','bitcast','addrspacecast','freeze','zext','sext','trunc'):
            src=body[len(op):].rsplit(' to ',1)[0];lanes=self.av(f,d.typed_val(d.strip_flags(src.strip())))
            if op=='inttoptr' and any(a[0]=='I' for a in union(*lanes.values())):lanes={0:union(*lanes.values(),{TOP})}
        elif op in ('insertvalue','insertelement'):
            parts=d.split_top(body[len(op):].strip());lanes=dict(self.av(f,d.typed_val(parts[0])))
            idx=d.typed_val(parts[2]) if op=='insertelement' else parts[2]
            val=union(*self.av(f,d.typed_val(parts[1])).values())
            if re.fullmatch(r'\d+',idx):lanes[int(idx)]=val
            else:
                t=d.parse_type(parts[0])[0]
                for k in range(t[1]):lanes[k]=union(lanes.get(k,()),val)
        elif op in ('extractvalue','extractelement'):
            parts=d.split_top(body[len(op):].strip());src=self.av(f,d.typed_val(parts[0]))
            idx=d.typed_val(parts[1]) if op=='extractelement' else parts[1]
            lanes={0:src.get(int(idx),frozenset()) if re.fullmatch(r'\d+',idx) else union(*src.values())}
        elif op=='shufflevector':
            parts=d.split_top(body[len(op):].strip());a=self.av(f,d.typed_val(parts[0]));b=self.av(f,d.typed_val(parts[1]));n=d.parse_type(parts[0])[0][1]
            for k,p in enumerate(d.split_top(d.typed_val(parts[2])[1:-1])):
                idx=int(d.typed_val(p));lanes[k]=a.get(idx,()) if idx<n else b.get(idx-n,())
        elif op=='store':
            parts=d.split_top(re.sub(r'^store\s+(?:(?:atomic|volatile)\s+)*','',body));ty=d.parse_type(parts[0])[0]
            ptrs=self.ptrs(f,d.typed_val(parts[1]));vals=self.av(f,d.typed_val(parts[0]),ty)
            et=ty[2] if ty[0] in ('vec','arr') else ty;sz=d.tsize(et,self.pw)
            for obj,off in ptrs:
                for k,ats in vals.items():changed|=self.slot(obj,self.shift(off,k*sz),sz,ats,self.type_width(et))
        elif op=='load':
            parts=d.split_top(re.sub(r'^load\s+(?:(?:atomic|volatile)\s+)*','',body));ty=d.parse_type(parts[0])[0]
            ptrs=self.ptrs(f,d.typed_val(parts[1]));n=ty[1] if ty[0] in ('vec','arr') else 1;et=ty[2] if n>1 else ty;sz=d.tsize(et,self.pw)
            for k in range(n):lanes[k]=self.getmem({(o,self.shift(off,k*sz)) for o,off in ptrs},sz,self.type_width(et))
        elif op in ('call','invoke'):
            if ' asm ' in body:return False
            c=d.parse_call(ins);cal=c['callee'];nm=cal[11:] if cal.startswith('@__bennett_') else None
            if nm in ('qalloc','qborrow'):lanes={0:{('R',f.name+ins.res)}}
            elif cal.startswith('@') and cal[1:] in d.HEAP_FNS:lanes={0:{('P',f.name+ins.res,0)}}
            elif cal.startswith('@llvm.memset'):
                dst,byte,length=[x[2] for x in c['args'][:3]]
                n=self.ints(f,length);bs=self.ints(f,byte)
                if n=='TOP':
                    for obj,off in self.ptrs(f,dst):changed|=self.slot(obj,'*',1,{TOP})
                else:
                    for obj,off in self.ptrs(f,dst):
                        for length in n:changed|=self.slot(obj,off,length,{TOP} if bs=='TOP' else {('B',x&255) for x in bs})
            elif cal.startswith(('@llvm.memcpy','@llvm.memmove')):
                dst,src=c['args'][0][2],c['args'][1][2];length=self.ints(f,c['args'][2][2])
                for so,s in self.ptrs(f,src):
                    for (o,k,n),ats in list(self.memory.items()):
                        if o!=so:continue
                        if length!='TOP' and isinstance(s,int) and isinstance(k,int) and not any(overlap(s,ln,k,n) for ln in length):continue
                        exact=length!='TOP' and isinstance(s,int) and isinstance(k,int) and all(s<=k and k+n<=s+ln for ln in length)
                        for do,z in self.ptrs(f,dst):
                            if exact:
                                for rw in self.memory_widths.get((o,k,n),{8*n}):changed|=self.slot(do,z+k-s if all(isinstance(x,int) for x in (z,k,s)) else '*',n,ats,rw)
                            else:changed|=self.slot(do,'*',1,union({x for x in ats if x[0] in ('R','C')},{TOP}))
            elif nm in d.REGION_OPS:
                for k,kind in d.REGION_OPS[nm].items():
                    cs=self.candidates(f,c['args'][k][2],kind);self.cands[id(ins),k]=cs
                    if nm in d.ENV_OP:
                        for name in cs:
                            g=self.m.funcs.get(name)
                            if g and g.is_def and g.params and g.params[0][2]:changed|=self.put(g,g.params[0][2],self.av(f,c['args'][d.ENV_OP[nm]][2]))
            elif not d.is_marker(cal[1:]) and not cal.startswith('@llvm.'):
                if cal.startswith('@'):cs={self.m.resolve_alias(cal[1:])}
                else:
                    cs=self.candidates(f,cal,ctype=d.fnstr(c['ret'],c['params'],c['vararg']));self.indirect[id(ins)]=cs
                for name in cs:
                    g=self.m.funcs.get(name)
                    if not g or not g.is_def:
                        if ins.res:lanes={0:{TOP}}
                        continue
                    for i,arg in enumerate(c['args']):
                        if i<len(g.params) and g.params[i][2]:changed|=self.put(g,g.params[i][2],self.av(f,arg[2],arg[0]))
                    for ret in g.instrs():
                        if ret.op=='ret' and ret.text!='ret void':
                            for k,a in self.av(g,d.typed_val(ret.text[4:])).items():lanes[k]=union(lanes.get(k,()),a)
        elif op in d.BINOPS:
            from dialect_check_v02 import value_set
            vals=value_set(self.m,f,ins.res)
            lanes={0:{TOP} if vals=='TOP' else {('I',x) for x in vals}}
            rest=d.strip_flags(body.split(None,1)[1]);ty,j=d.parse_type(rest);left,right=d.split_top(rest[j:])
            pats={a for a in self.atoms(f,left)|self.atoms(f,right) if a[0]=='P'}
            if pats:
                rhs=self.ints(f,right)
                if op in ('add','sub') and rhs!='TOP' and self.ptrs(f,left):
                    lanes[0]=union(lanes[0],{('P',o,self.shift(off,(-1 if op=='sub' else 1)*v)) for o,off in self.ptrs(f,left) for v in rhs})
                else:lanes[0]=union(lanes[0],{('P',o,'*') for _,o,_ in pats})
        # Integer value sets used by descriptors are read separately using PT5.
        return self.put(f,ins.res,lanes) | changed

    def host_address(self,f,val,seen=None):
        """PT2's wrap/unknown-address alternative is not host provenance.

        Keep the actual base origins for §6.4 instead of treating analysis
        imprecision introduced by modular arithmetic as a host boundary.
        """
        seen=set() if seen is None else set(seen)
        if val in seen:return False
        seen.add(val)
        if val.startswith('getelementptr ('):
            parts=d.split_top(val[len('getelementptr ('):-1])
            return self.host_address(f,d.typed_val(parts[1]),seen)
        ins=next((i for i in f.instrs() if i.res==val),None)
        if ins:
            body=ins.text.split(' = ',1)[-1]
            if ins.op=='getelementptr':
                parts=d.split_top(re.sub(r'^getelementptr\s+(?:(?:inbounds|nusw|nuw)\s+)*','',body))
                return self.host_address(f,d.typed_val(parts[1]),seen)
            if ins.op in ('phi','select'):
                return any(self.host_address(f,v,seen) for v in self.value_operands(ins))
            if ins.op in ('bitcast','addrspacecast','ptrtoint','inttoptr'):
                return self.host_address(f,d.typed_val(body[len(ins.op):].rsplit(' to ',1)[0]),seen)
        return any(o=='EXT' for o,_ in self.ptrs(f,val))

    def handle_rules(self):
        # §6.2–§6.4. Provenance is tracked lane by lane; aliases never erase ROOT.
        for f in self.funcs():
            for ins in f.instrs():
                body=ins.text.split(' = ',1)[-1]
                used={v for v in re.findall(r'%[-\w.$]+',body) if self.roots(f,v)}
                if ins.op=='load':
                    parts=d.split_top(re.sub(r'^load\s+(?:(?:atomic|volatile)\s+)*','',body));ty=d.parse_type(parts[0])[0];sz=d.tsize(ty,self.pw)
                    for obj,off in self.ptrs(f,d.typed_val(parts[1])):
                        for (o,k,n),ats in self.memory.items():
                            if o==obj and any(a[0]=='R' for a in ats) and overlap(off,sz,k,n) and (sz!=self.pw//8 or isinstance(off,int) and isinstance(k,int) and off!=k):
                                raise d.Reject('BD-E-HANDLE-USE','§6.2 partial read: '+ins.text)
                if ins.op in ('call','invoke') and ' asm ' not in body:
                    call=d.parse_call(ins);cal=call['callee']
                    cs={cal[1:]} if cal.startswith('@') else self.indirect.get(id(ins),set())
                    if not d.is_marker(cal[1:]) and not cal.startswith('@llvm.') and cal[1:] not in d.HEAP_FNS|{'free','realloc'} and not (cs and all(self.m.defined(n) for n in cs)):
                        queue=[p for arg in call['args'] for p in self.ptrs(f,arg[2])];seen=set()
                        while queue:
                            obj,off=queue.pop()
                            if obj in seen:continue
                            seen.add(obj)
                            for (o,k,n),ats in self.memory.items():
                                if o!=obj:continue
                                if any(a[0]=='R' for a in ats):raise d.Reject('BD-E-HANDLE-ESCAPE','§6.4 reachable slot '+ins.text)
                                queue.extend(a[1:] for a in ats if a[0]=='P')
                if not used:continue
                op=ins.op
                if op in ('icmp',):
                    parts=d.split_top(body.split(None,2)[2]);other=[d.typed_val(parts[0]),parts[1]]
                    if any(v not in ('null','0') and not self.roots(f,v) for v in other):raise d.Reject('BD-E-HANDLE-USE','§6.3 non-identity comparison '+ins.text)
                    if not re.match(r'icmp (eq|ne)\b',body):raise d.Reject('BD-E-HANDLE-USE','§6.3 '+ins.text)
                    continue
                if op in ('ptrtoint','inttoptr','bitcast','addrspacecast','zext','sext','trunc'):
                    src=d.parse_type(d.strip_flags(body[len(op):].strip()))[0];dst=d.parse_type(body.rsplit(' to ',1)[1])[0]
                    if self.type_width(src)!=self.pw or self.type_width(dst)!=self.pw:raise d.Reject('BD-E-HANDLE-USE','§6.2 '+ins.text)
                    continue
                if op in ('phi','freeze','insertvalue','extractvalue','insertelement','extractelement','shufflevector'):continue
                if op=='select':
                    if d.typed_val(d.split_top(body[6:].strip())[0]) in used:raise d.Reject('BD-E-HANDLE-USE','§6.2 '+ins.text)
                    continue
                if op in ('store','load'):
                    ptr=d.store_parts(ins)[1] if op=='store' else d.typed_val(d.split_top(body[4:].strip())[1])
                    if ptr in used:raise d.Reject('BD-E-HANDLE-USE','§6.2 dereference '+ins.text)
                    if op=='store':
                        if self.host_address(f,ptr) or not self.ptrs(f,ptr):raise d.Reject('BD-E-HANDLE-ESCAPE','§6.4 '+ins.text)
                    continue
                if op=='ret':
                    # §6.6: a device entry returning its allocated register is a QREG result.
                    if self.nonlocal_linkage(f.name) and not any(self.marker_calls(f)):
                        raise d.Reject('BD-E-HANDLE-ESCAPE','§6.4 '+ins.text)
                    continue
                if op in ('call','invoke') and ' asm ' not in body:
                    c=d.parse_call(ins);cal=c['callee'];mk=cal[11:] if cal.startswith('@__bennett_') else None
                    if mk in d.HANDLE_OPS:
                        for k,arg in enumerate(c['args']):
                            if arg[2] in used and k not in d.HANDLE_OPS[mk]:raise d.Reject('BD-E-HANDLE-USE','§6.2 '+ins.text)
                        continue
                    cs={cal[1:]} if cal.startswith('@') else self.indirect.get(id(ins),set())
                    if cs and all(self.m.defined(n) for n in cs):continue
                    raise d.Reject('BD-E-HANDLE-ESCAPE','§6.4 '+ins.text)
                raise d.Reject('BD-E-HANDLE-USE','§6.2 '+ins.text)
        for f in self.funcs():
            for ins,c,mk in self.marker_calls(f):
                for k in d.HANDLE_OPS[mk]:
                    if not self.roots(f,c['args'][k][2]):raise d.Reject('BD-E-HANDLE-UNTRACKED','§6.2 '+ins.text)

    def direct_callees(self,f):
        out=[]
        for ins in f.instrs():
            if ins.op in ('call','invoke') and ' asm ' not in ins.text:
                c=d.parse_call(ins)
                if c['callee'].startswith('@'):
                    n=self.m.resolve_alias(c['callee'][1:])
                    if self.m.defined(n):out.append(n)
        return out

    def marker_calls(self,f):
        for ins in f.instrs():
            if ins.op in ('call','invoke') and ' asm ' not in ins.text:
                c=d.parse_call(ins)
                if c['callee'].startswith('@') and d.is_marker(c['callee'][1:]):yield ins,c,c['callee'][11:]

    def region_rules(self):
        deferred='!"bennett.measure_in_unitary", !"defer"' in self.m.text
        self.reversible=set()
        generating=set()
        for caller in self.funcs():
            for call,_,marker in self.marker_calls(caller):
                if marker in ('ctrl','adj','compute'):
                    for operand in d.REGION_OPS[marker]:
                        for name in self.cands[id(call),operand]:generating |= self.closure(name)
        for f in self.funcs():
            for ins,c,mk in self.marker_calls(f):
                for k,kind in d.REGION_OPS.get(mk,{}).items():
                    if kind=='reversible' and f.name in generating:kind='action'
                    cs=self.cands[id(ins),k]
                    for name in cs:
                        g=self.m.funcs[name]
                        if kind in ('action','reversible') and g.ftype()!='void (ptr)':
                            if len(cs)==1:raise d.Reject('BD-E-REGION-TYPE','§7.1 '+name+': '+g.ftype())
                            continue
                        closure=self.closure(name)
                        if kind=='reversible':
                            self.reversible|=closure
                            for n in closure:
                                for i in self.m.funcs[n].instrs():
                                    if i.op=='call' and '@__bennett_nz_fault(' in i.text:
                                        self.blockers.append(('BD-B-ISA7','BLK-5 (ISA-7) §17.5 typed R fault: '+i.text))
                        for n in closure:
                            for _,_,marker in self.marker_calls(self.m.funcs[n]):
                                if marker=='measure' and (kind=='reversible' or kind=='action' and not deferred) and len(cs)==1:
                                    code='BD-E-REVERSIBLE-MEASURE' if kind=='reversible' else 'BD-E-REGION-MEASURE'
                                    raise d.Reject(code,'§7.5 '+n)

    def closure(self,name):
        seen=set();stack=[name]
        while stack:
            n=stack.pop()
            if n in seen or not self.m.defined(n):continue
            seen.add(n);f=self.m.funcs[n]
            stack+=self.direct_callees(f)
            for ins in f.instrs():stack+=list(self.indirect.get(id(ins),set()))
        return seen

    def operand_rules(self):
        classes=re.findall(r'!"bennett.classes"(.*)',self.m.text)
        nclass=0
        for field in classes:
            refs=re.findall(r'!(\d+)',field)
            for ref in refs:
                row=re.search(r'^!'+ref+r' = !\{(.*)\}',self.m.text,re.M)
                if row:nclass+=len(re.findall(r'!"[^"\n]+"',row[1]))
        for f in self.funcs():
            for ins,c,mk in self.marker_calls(f):
                for k,role in d.INT_CAND_OPS.get(mk,{}).items():
                    vs=self.ints(f,c['args'][k][2])
                    if vs=='TOP':
                        if role=='n':self.blockers.append(('BD-B-ISA4','BLK-1 §3.4 '+ins.text))
                        continue
                    # §3.4 only a constant invalid operand is a rejection.
                    if len(vs)==1:
                        v=next(iter(vs))
                        if role in d.OPCODES and v not in d.OPCODES[role] or role=='n' and v==0 or role=='cls' and v>nclass:
                            raise d.Reject('BD-E-OPERAND','§3.4 '+ins.text+' value='+str(v))

    def field(self,f,p,off,size):
        ptrs={(o,self.shift(k,off)) for o,k in self.ptrs(f,p)}
        return self.getmem(ptrs,size)

    def field_ints(self,f,p,off,size):
        ats=self.field(f,p,off,size)
        vals={a[1] for a in ats if a[0]=='I'}
        return vals if ats and len(vals)==len(ats) else 'TOP'

    def descriptor_rules(self):
        self.shapes=0;self.inplace_pairs=[]
        for f in self.funcs():
            for ins,c,mk in self.marker_calls(f):
                if mk not in ('oracle','inplace','ctrl','adj','compute','reversible'):continue
                bk={'oracle':1,'inplace':2,'ctrl':3,'adj':1,'compute':2,'reversible':1}[mk]
                budget=c['args'][bk][2]
                if budget!='null':
                    for off in (0,8,16,24):
                        ats=self.field(f,budget,off,8)
                        if not ats or TOP in ats:
                            # §9.5 bitwise copies of a launch argument are legal.
                            origins=[]
                            for g in self.funcs():
                                for st in g.instrs():
                                    if st.op=='store':
                                        v,p=d.store_parts(st)
                                        if self.ptrs(g,p)&{(o,self.shift(k,off)) for o,k in self.ptrs(f,budget)}:origins.append((g,v))
                            if origins and all(any(v==pn for _,_,pn in g.params) for g,v in origins):continue
                            self.blockers.append(('BD-B-ISA1','BLK-2 §9.5 '+ins.text+' offset='+str(off)))
                if mk not in ('oracle','inplace'):continue
                desc=c['args'][2 if mk=='oracle' else 3][2]
                version=self.field_ints(f,desc,0,4)
                # §8.1 invalid runtime versions trap T-IFACE; §22.1 has no descriptor rejection.
                nps=self.field_ints(f,desc,4,4)
                if nps=='TOP':
                    raise d.Fail('checker-unimplemented: §8.4 descriptor with unknown parameter count '+ins.text)
                nparam=max(nps);count=1;args=[];quantum=False
                for j in range(nparam):
                    kinds=self.field_ints(f,desc,32+32*j,4)
                    if kinds=='TOP':kinds={1,2,3,4,5}
                    count*=len(kinds)
                    vals=self.field_ints(f,desc,48+32*j,8)
                    args.append(vals)
                    if mk=='inplace' and j>0 and (kinds!={2} or vals=='TOP'):quantum=True
                if not self.shapes:self.shapes=count*len(self.cands[id(ins),0])
                if mk=='inplace':
                    if quantum:self.parameterised_pairs=getattr(self,'parameterised_pairs',[])+[(f,ins,c,args)]
                    else:self.inplace_pairs.append((f,ins,c,args))

    def tdl_rules(self):
        # TDL-2: applications, not event generation, change an object's coherence.
        for f in self.funcs():
            coherent=set()
            for ins,c,mk in self.marker_calls(f):
                if mk=='observe':
                    coherent-={o for o,_ in self.ptrs(f,c['args'][0][2])};continue
                if mk not in ('ctrl','adj','compute'):continue
                for k in d.REGION_OPS[mk]:
                    for name in self.cands[id(ins),k]:
                        if not self.m.defined(name):continue
                        g=self.m.funcs[name];defs=self.defs(g)
                        for st in g.instrs():
                            if st.op in ('call','invoke'):
                                cc=d.parse_call(st)
                                if cc['callee']=='@__bennett_rot':
                                    angle=cc['args'][3][2];ai=defs.get(angle)
                                    if ai and ai.op=='load':
                                        ptr=d.typed_val(d.split_top(ai.text.split(' = ',1)[1][4:].strip())[1])
                                        if {o for o,_ in self.ptrs(g,ptr)}&coherent:raise d.Reject('BD-E-COHERENT-ANGLE','TDL-10 '+st.text)
                            if st.op!='store':continue
                            val,ptr=d.store_parts(st);objs={o for o,_ in self.ptrs(g,ptr) if o in self.m.globals}
                            if objs&coherent and mk!='compute':
                                # TDL-5b admitted local bijections: add/sub/xor by an independent value.
                                vi=defs.get(val);bijection=False
                                if vi and vi.op in ('add','sub','xor'):
                                    vb=vi.text.split(' = ',1)[1].split(None,1)[1];ty,j=d.parse_type(vb)
                                    ops=d.split_top(vb[j:]);li=defs.get(ops[0])
                                    if li and li.op=='load':
                                        lp=d.typed_val(d.split_top(li.text.split(' = ',1)[1][4:].strip())[1]);bijection=self.ptrs(g,lp)==self.ptrs(g,ptr)
                                if not bijection:raise d.Reject('BD-E-COHERENT-OVERWRITE','TDL-5(d) '+st.text)
                            if mk=='ctrl':coherent|=objs

    def instance_rules(self):
        from dialect_bounds import instance_rules
        instance_rules(self)
