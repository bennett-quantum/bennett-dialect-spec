"""Materialised normalisation, dialect §12 (expected IR producer)."""
import re
import math
import dialect_check as d

FP={'half':('f16',16),'bfloat':('bf16',16),'float':('f32',32),'double':('f64',64),
    'x86_fp80':('f80',80),'fp128':('f128',128),'ppc_fp128':('ppcf128',128)}


def lower_llvm_intrinsics(text,major):
    from dialect_check_v02 import SCRATCH, command
    import tempfile
    from pathlib import Path
    groups=[(r'coro\.', ['coro-early','cgscc(coro-split)','coro-cleanup']),
            (r'matrix\.', ['lower-matrix-intrinsics']),
            (r'(?:public\.)?type\.|icall\.branch\.funnel', ['lowertypetests']),
            (r'instrprof\.', ['instrprof']), (r'alloc\.token\.id', ['alloc-token']),
            (r'experimental\.guard', ['lower-guard-intrinsic']),
            (r'experimental\.widenable\.condition', ['lower-widenable-condition'])]
    passes=[p for pattern,ps in groups if re.search(r'@llvm\.'+pattern,text) for p in ps]
    if not passes:return text
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        path=Path(tmp)/'n0.ll';path.write_text(d.with_decls(text))
        out=command([d.toolchains()[major]/'opt','-S','-passes='+','.join(passes),path,'-o','-'])
    return out


class Normaliser:
    def __init__(self,text,*,rmode=None,platform=None,major="18"):
        self.rmode=rmode;self.platform=platform;self.major=major
        lowered=lower_llvm_intrinsics(text,major)
        # Parse named types with the legacy parser without changing the printed type names.
        from dialect_check_v02 import expanded_types
        self.original=text
        expanded=expanded_types(lowered)
        self.m=d.Module(expanded)
        originals={re.search(r'@([-\w.$]+)\(',ln)[1]:ln.strip() for ln in text.splitlines() if ln.lstrip().startswith('define ')}
        for name,f in self.m.funcs.items():
            if f.is_def and name in originals:f.header=originals[name]
        # Instructions may retain named types once their sizes have been resolved.
        self.named=dict(re.findall(r'^(%[-\w.$]+) = type (.+)$',text,re.M))
        for f in self.funcs():
            for ins in f.instrs():
                for name,t in self.named.items():ins.text=ins.text.replace(t,name)
        self.appended=[];self.globals=[]
        self.lanes={};self.limbs={}

    def funcs(self):return [f for f in self.m.funcs.values() if f.is_def]
    def typ(self,s):
        for name,t in self.named.items():s=s.replace(name,t)
        return d.parse_type(s)[0]
    def decl(self,name,ret,args):
        decl=f'declare {ret} @{name}('+', '.join(args)+')'
        if name not in self.m.funcs and decl not in self.appended:self.appended.append(decl)
    def rewrite(self,fn):
        for f in self.funcs():
            for lab,blk in f.blocks:
                out=[];count=0
                for ins in blk:
                    if ins.deleted:continue
                    key=ins.res[1:] if ins.res else f.name+'.'+str(count)
                    lines=fn(f,ins,key)
                    if lines is None:out.append(ins)
                    else:
                        if ins.res is None:count+=1
                        for line in lines:
                            m=re.match(r'(%[-\w.$]+) = (.*)',line)
                            res,body=(m[1],m[2]) if m else (None,line)
                            out.append(d.Instr(line,res,body.split()[0],f,lab))
                blk[:]=out
    def replace(self,f,old,new):d.replace_uses(f,old,new)

    def basic(self):
        # N1–N8 preserve declaration attributes; N4 applies to definitions/calls.
        for f in self.funcs():
            f.header=d.strip_n4_header(f.header)
            f.header=' '.join(t for t in f.header.split(' ') if d.attr_name(t) not in d.N4_FN)
            for ins in f.instrs():
                if ins.op not in ('call','invoke'):
                    ins.text=' '.join(t for t in ins.text.split(' ') if t not in d.INT_FLAGS|d.FMF)
                ins.text=re.sub(r',\s*!(?!dbg\b|bennett\.rstep\b)[\w.]+\s+![\w.{}]+','',ins.text)
                if ins.op in ('call','invoke') and ' asm ' not in ins.text:ins.text=d.strip_n4(ins.text)
                ins.text=d.n7(ins.text)
        for key,toks in self.m.groups.items():self.m.groups[key]=[t for t in toks if d.attr_name(t) not in d.N4_FN]
        def go(f,i,r):
            if i.op=='freeze':self.replace(f,i.res,d.typed_val(i.text.split(' = ',1)[1][7:]));return []
            if i.op=='call' and ' asm ' not in i.text:
                c=d.parse_call(i);cal=c['callee']
                if re.match(r'@llvm\.(assume|lifetime\.|invariant\.|sideeffect|donothing|dbg\.)',cal):return []
                if cal.startswith('@llvm.is.constant'):self.replace(f,i.res,'false');return []
                if cal.startswith('@llvm.objectsize'):self.replace(f,i.res,'-1' if c['args'][1][2]=='false' else '0');return []
        self.rewrite(go)

    def atomics(self):
        def go(f,i,r):
            b=i.text.split(' = ',1)[-1]
            if i.op=='fence':return []
            if i.op in ('load','store'):
                i.text=re.sub(r'\b(atomic|volatile)\s+','',i.text)
                i.text=re.sub(r'\s+(?:unordered|monotonic|acquire|release|acq_rel|seq_cst)\b','',i.text)
                return
            if i.op=='atomicrmw':
                m=re.match(r'atomicrmw (\w+) ptr ([^,]+), (i\d+) ([^ ]+).*?(, align \d+)?$',b)
                op,p,t,v,al=m.groups();al=al or ''
                if op not in ('add','sub','and','or','xor','xchg','uinc_wrap','udec_wrap','usub_cond','usub_sat'):raise d.Fail('N9 atomicrmw '+op)
                out=[f'%nz.l.{r} = load {t}, ptr {p}{al}']
                if op=='xchg':nv=v
                elif op=='uinc_wrap':
                    out += [f'%nz.k.{r} = icmp uge {t} %nz.l.{r}, {v}',f'%nz.i.{r} = add {t} %nz.l.{r}, 1',f'%nz.v.{r} = select i1 %nz.k.{r}, {t} 0, {t} %nz.i.{r}'];nv=f'%nz.v.{r}'
                elif op=='udec_wrap':
                    out += [f'%nz.k.{r} = icmp eq {t} %nz.l.{r}, 0',f'%nz.g.{r} = icmp ugt {t} %nz.l.{r}, {v}',f'%nz.w.{r} = or i1 %nz.k.{r}, %nz.g.{r}',f'%nz.d.{r} = sub {t} %nz.l.{r}, 1',f'%nz.v.{r} = select i1 %nz.w.{r}, {t} {v}, {t} %nz.d.{r}'];nv=f'%nz.v.{r}'
                elif op in ('usub_cond','usub_sat'):
                    otherwise=f'%nz.l.{r}' if op=='usub_cond' else '0'
                    out += [f'%nz.k.{r} = icmp uge {t} %nz.l.{r}, {v}',f'%nz.s.{r} = sub {t} %nz.l.{r}, {v}',f'%nz.v.{r} = select i1 %nz.k.{r}, {t} %nz.s.{r}, {t} {otherwise}'];nv=f'%nz.v.{r}'
                else:out.append(f'%nz.v.{r} = {op} {t} %nz.l.{r}, {v}');nv=f'%nz.v.{r}'
                out.append(f'store {t} {nv}, ptr {p}{al}')
                self.replace(f,i.res,f'%nz.l.{r}');return out
            if i.op=='cmpxchg':
                m=re.match(r'cmpxchg ptr ([^,]+), (i\d+) ([^,]+), i\d+ ([^ ]+).*?(, align \d+)?$',b)
                p,t,c,n,al=m.groups();al=al or ''
                return [f'%nz.l.{r} = load {t}, ptr {p}{al}',f'%nz.e.{r} = icmp eq {t} %nz.l.{r}, {c}',
                    f'%nz.s.{r} = select i1 %nz.e.{r}, {t} {n}, {t} %nz.l.{r}',f'store {t} %nz.s.{r}, ptr {p}{al}',
                    f'%nz.a.{r} = insertvalue {{ {t}, i1 }} zeroinitializer, {t} %nz.l.{r}, 0',
                    f'{i.res} = insertvalue {{ {t}, i1 }} %nz.a.{r}, i1 %nz.e.{r}, 1']
        self.rewrite(go)

    def shifts(self):
        def go(f,i,r):
            if i.op not in ('shl','lshr','ashr'):return
            body=i.text.split(' = ',1)[1].split(None,1)[1];ty,j=d.parse_type(body)
            a,b=d.split_top(body[j:]);w=ty[1]
            if re.fullmatch(r'-?\d+',b):
                if int(b)<0 or int(b)>=w:self.replace(f,i.res,'0');return []
                return
            return [f'%nz.c.{r} = icmp uge i{w} {b}, {w}',f'%nz.s.{r} = {i.op} i{w} {a}, {b}',f'{i.res} = select i1 %nz.c.{r}, i{w} 0, i{w} %nz.s.{r}']
        self.rewrite(go)

    def fmuladd(self):
        def go(f,i,r):
            if i.op!='call' or ' asm ' in i.text:return
            c=d.parse_call(i)
            if not c['callee'].startswith('@llvm.fmuladd'):return
            t=d.tstr(c['ret']);a,b,z=[a[2] for a in c['args']]
            return [f'%nz.m.{r} = fmul {t} {a}, {b}',f'{i.res} = fadd {t} %nz.m.{r}, {z}']
        self.rewrite(go)

    def vector(self):
        def get(v,n,ty):
            if v in ('zeroinitializer','undef','poison'):return ['0']*n
            if v.startswith('<'):return [d.typed_val(x) for x in d.split_top(v[1:-1])]
            if v in self.lanes:return self.lanes[v]
            raise d.Fail('N21 vector source '+v)
        def lane_index(index,L,r):
            t=d.parse_type(index)[0];K=t[1];W=max(K,L.bit_length());idx=d.typed_val(index)
            if W==K:return [],d.tstr(t),idx
            wide=f'%nz.i.{r}'
            return [f'{wide} = zext i{K} {idx} to i{W}'],f'i{W}',wide
        def memory_lane(t,p,k,original):
            e=d.tstr(t);ew=t[1] if t[0]=='int' else d.tsize(t)*8
            # Byte lanes need not share their scalar allocation stride.
            abi=d.talign(t)
            if t[0]=='int':
                alignments={8:1,16:2,32:4,64:8}
                alignments.update({int(w):int(a)//8 for w,a in re.findall(r'(?:^|[-"])i(\d+):(\d+)',self.original)})
                abi=alignments.get(ew,next((alignments[w] for w in sorted(alignments) if w>=ew),alignments[max(alignments)]))
            size=(ew+7)//8;stride=(size+abi-1)//abi*abi
            offset=k*size;align=min(abi,math.gcd(original,offset))
            return (e,k,align) if stride==size else ('i8',offset,align)
        def go(f,i,r):
            b=i.text.split(' = ',1)[-1]
            if i.op=='bitcast' and '<' in b:
                src,dst=b[8:].rsplit(' to ',1);st,j=d.parse_type(src);dt=self.typ(dst);v=src[j:].strip()
                ns,se=(st[1],st[2]) if st[0]=='vec' else (1,st)
                nd,de=(dt[1],dt[2]) if dt[0]=='vec' else (1,dt)
                sw=se[1];dw=de[1];total=ns*sw;out=[];acc=None
                if total!=nd*dw:raise d.Fail('N21 unequal bitcast widths')
                vals=get(v,ns,se) if st[0]=='vec' else [v]
                for k,value in enumerate(vals):
                    cur=value
                    if sw!=total:cur=f'%nz.pack{k}.{r}';out.append(f'{cur} = zext i{sw} {value} to i{total}')
                    if k:
                        shifted=f'%nz.ps{k}.{r}';out.append(f'{shifted} = shl i{total} {cur}, {k*sw}');cur=shifted
                    if acc is not None:
                        joined=f'%nz.or{k}.{r}';out.append(f'{joined} = or i{total} {acc}, {cur}');cur=joined
                    acc=cur
                result=[]
                for k in range(nd):
                    cur=acc
                    if k:cur=f'%nz.bs{k}.{r}';out.append(f'{cur} = lshr i{total} {acc}, {k*dw}')
                    if dw!=total:
                        lane=f'%nz.l{k}.{r}';out.append(f'{lane} = trunc i{total} {cur} to i{dw}');cur=lane
                    result.append(cur)
                if dt[0]=='vec':self.lanes[i.res]=result
                else:self.replace(f,i.res,result[0])
                return out
            if i.op=='call' and re.search(r'@llvm.vp.(merge|select|reduce\.)',b):
                c=d.parse_call(i);args=c['args'];op=c['callee'].split('.')[2];out=[]
                if op in ('merge','select'):
                    ty=args[1][0];n=ty[1];et=d.tstr(ty[2]);cond=get(args[0][2],n,('int',1));a=get(args[1][2],n,ty[2]);z=get(args[2][2],n,ty[2]);vals=[]
                    for k in range(n):
                        active=f'%nz.active{k}.{r}';choice=f'%nz.choice{k}.{r}';lane=f'%nz.l{k}.{r}'
                        out += [f'{active} = icmp ult i32 {k}, {args[3][2]}',f'{choice} = select i1 {cond[k]}, {et} {a[k]}, {et} {z[k]}',f'{lane} = select i1 {active}, {et} {choice}, {et} '+(z[k] if op=='merge' else '0')];vals.append(lane)
                    self.lanes[i.res]=vals;return out
                op=c['callee'].split('.')[3];ty=args[1][0];n=ty[1];et=d.tstr(ty[2]);vals=get(args[1][2],n,ty[2]);masks=get(args[2][2],n,('int',1));acc=args[0][2]
                for k in range(n):
                    active=f'%nz.active{k}.{r}';mask=f'%nz.mask{k}.{r}';fold=f'%nz.fold{k}.{r}';res=i.res if k==n-1 else f'%nz.acc{k}.{r}'
                    out += [f'{active} = icmp ult i32 {k}, {args[3][2]}',f'{mask} = and i1 {active}, {masks[k]}',f'{fold} = {op} {et} {acc}, {vals[k]}',f'{res} = select i1 {mask}, {et} {fold}, {et} {acc}'];acc=res
                return out
            if i.op=='load' and re.search(r'<\d+ x ',b):
                ps=d.split_top(b[5:]);t=d.parse_type(ps[0])[0];n=t[1];e=d.tstr(t[2]);p=d.typed_val(ps[1])
                al=re.search(r', align (\d+)',b);original=int(al[1]) if al else d.talign(t)
                vals=[];out=[]
                if t[2][0]=='int' and t[2][1]%8:
                    ew=t[2][1];mw=((n*ew+7)//8)*8
                    if mw>128:raise d.Fail('N21 packed load exceeds scalar carrier; needs chunk expansion')
                    packed=f'%nz.packed.{r}';out.append(f'{packed} = load i{mw}, ptr {p}, align 1')
                    for k in range(n):
                        src=packed
                        if k:src=f'%nz.shift{k}.{r}';out.append(f'{src} = lshr i{mw} {packed}, {k*ew}')
                        v=f'%nz.l{k}.{r}';out.append(f'{v} = trunc i{mw} {src} to {e}');vals.append(v)
                    self.lanes[i.res]=vals;return out
                for k in range(n):
                    q=f'%nz.p{k}.{r}';v=f'%nz.l{k}.{r}';vals.append(v)
                    gt,off,align=memory_lane(t[2],p,k,original)
                    out += [f'{q} = getelementptr {gt}, ptr {p}, i64 {off}',f'{v} = load {e}, ptr {q}, align {align}']
                self.lanes[i.res]=vals;return out
            if i.op=='store' and re.search(r'<\d+ x ',b):
                ps=d.split_top(b[6:]);t=d.parse_type(ps[0])[0];n=t[1];e=d.tstr(t[2]);p=d.typed_val(ps[1]);vals=get(d.typed_val(ps[0]),n,t[2])
                al=re.search(r', align (\d+)',b);original=int(al[1]) if al else d.talign(t);out=[]
                if t[2][0]=='int' and t[2][1]%8:
                    ew=t[2][1];mw=(n*ew+7)//8*8;acc=None
                    for k,value in enumerate(vals):
                        lane=f'%nz.pack{k}.{r}';out.append(f'{lane} = zext {e} {value} to i{mw}')
                        if k:
                            shift=f'%nz.shift{k}.{r}';out.append(f'{shift} = shl i{mw} {lane}, {k*ew}');lane=shift
                        if acc is not None:
                            joined=f'%nz.or{k}.{r}';out.append(f'{joined} = or i{mw} {acc}, {lane}');lane=joined
                        acc=lane
                    out.append(f'store i{mw} {acc}, ptr {p}, align 1');return out
                for k,value in enumerate(vals):
                    gt,off,align=memory_lane(t[2],p,k,original);q=f'%nz.p{k}.{r}'
                    out += [f'{q} = getelementptr {gt}, ptr {p}, i64 {off}',f'store {e} {value}, ptr {q}, align {align}']
                return out
            if i.op in d.BINOPS and re.search(r'<\d+ x ',b):
                rest=b.split(None,1)[1];t,j=d.parse_type(rest);a,z=d.split_top(rest[j:]);aa=get(a,t[1],t[2]);zz=get(z,t[1],t[2]);vals=[f'%nz.l{k}.{r}' for k in range(t[1])];self.lanes[i.res]=vals
                return [f'{v} = {i.op} {d.tstr(t[2])} {x}, {y}' for v,x,y in zip(vals,aa,zz)]
            if i.op=='insertelement':
                ps=d.split_top(b[len(i.op):].strip());t=d.parse_type(ps[0])[0];lanes=list(get(d.typed_val(ps[0]),t[1],t[2]));idx=d.typed_val(ps[2])
                if not idx.isdigit():
                    out,it,idx=lane_index(ps[2],t[1],r);et=d.tstr(t[2]);value=d.typed_val(ps[1]);vals=[]
                    for k,old in enumerate(lanes):
                        c=f'%nz.k{k}.{r}';v=f'%nz.l{k}.{r}'
                        out += [f'{c} = icmp eq {it} {idx}, {k}',f'{v} = select i1 {c}, {et} {value}, {et} {old}'];vals.append(v)
                    self.lanes[i.res]=vals;return out
                lanes[int(idx)]=d.typed_val(ps[1]);self.lanes[i.res]=lanes;return []
            if i.op=='extractelement':
                ps=d.split_top(b[len(i.op):].strip());t=d.parse_type(ps[0])[0];lanes=get(d.typed_val(ps[0]),t[1],t[2]);idx=d.typed_val(ps[1])
                if not idx.isdigit():
                    L=len(lanes);out,it,idx=lane_index(ps[1],L,r);et=d.tstr(t[2])
                    out.append(f'%nz.c.{r} = icmp uge {it} {idx}, {L}');prev='0'
                    for k,value in enumerate(lanes):
                        c=f'%nz.k{k}.{r}';v=f'%nz.e.{r}' if k==L-1 else f'%nz.l{k}.{r}'
                        out += [f'{c} = icmp eq {it} {idx}, {k}',f'{v} = select i1 {c}, {et} {value}, {et} {prev}'];prev=v
                    return out+[f'{i.res} = select i1 %nz.c.{r}, {et} 0, {et} {prev}']
                self.replace(f,i.res,lanes[int(idx)]);return []
            if i.op=='call' and '@llvm.vector.reduce.' in b:
                c=d.parse_call(i);op=c['callee'].split('.')[3];t=c['args'][0][0];vals=get(c['args'][0][2],t[1],t[2]);out=[];a=vals[0]
                for k,z in enumerate(vals[1:],1):
                    v=i.res if k==len(vals)-1 else f'%nz.f{k}.{r}';out.append(f'{v} = {op} {d.tstr(t[2])} {a}, {z}');a=v
                return out
        self.rewrite(go)

    def wide(self):
        def go(f,i,r):
            b=i.text.split(' = ',1)[-1]
            m=re.search(r'\bi(\d+)\b',b)
            if not m or int(m[1])<=128:return
            w=int(m[1]);n=(w+63)//64
            widths=[64]*(n-1)+[w-64*(n-1)]
            def parts(v):
                if v in self.limbs:return self.limbs[v]
                if re.fullmatch(r'-?\d+',v):
                    return [str((int(v)>>(64*k))% (1<<lw)) for k,lw in enumerate(widths)]
                raise d.Fail('N22 missing limb source '+v)
            from dialect_wide import extra
            expanded=extra(self,f,i,r,w,widths,parts)
            if expanded is not None:return expanded
            if i.op in ('sext','zext'):
                src,dst=b[len(i.op):].rsplit(' to ',1);st,j=d.parse_type(src);sw=st[1];dw=int(dst.strip()[1:]);v=src[j:].strip()
                source=parts(v);out=[];result=list(source);top=sw%64 or 64
                if top<64:
                    q=f'%nz.ext.{r}';out.append(f'{q} = {i.op} i{top} {source[-1]} to i64');result[-1]=q
                fill='0'
                if i.op=='sext':
                    fill=f'%nz.sign.{r}';out.append(f'{fill} = ashr i64 {result[-1]}, 63')
                result += [fill]*((dw+63)//64-len(result));self.limbs[i.res]=result
                return out
            if i.op=='load':
                p=d.typed_val(d.split_top(b[5:])[1]);al=re.search(r', align (\d+)',b);al=', align '+al[1] if al else ''
                vals=[];out=[]
                for k in range(n):
                    q=f'%nz.p{k}.{r}';v=f'%nz.m{k}.{r}';vals.append(v);out.append(f'{q} = getelementptr i64, ptr {p}, i64 {k}')
                    lw=widths[k];mw=(lw+7)//8*8
                    if lw==mw:out.append(f'{v} = load i{lw}, ptr {q}{al}')
                    else:out += [f'%nz.raw{k}.{r} = load i{mw}, ptr {q}{al}',f'{v} = trunc i{mw} %nz.raw{k}.{r} to i{lw}']
                self.limbs[i.res]=vals;return out
            if i.op=='sub':
                a,bv=d.split_top(b.split(None,2)[2]);a=parts(a);z=parts(bv)
                out=[f'%nz.m0.{r} = sub i64 {a[0]}, {z[0]}',f'%nz.c0.{r} = icmp ult i64 {a[0]}, {z[0]}']
                for k in range(1,n):
                    lw=widths[k];borrow=f'%nz.c{k-1}.{r}'
                    out.append(f'%nz.t{k}.{r} = sub i{lw} {a[k]}, {z[k]}')
                    if lw>1:out.append(f'%nz.z{k}.{r} = zext i1 {borrow} to i{lw}');borrow=f'%nz.z{k}.{r}'
                    out.append(f'%nz.m{k}.{r} = sub i{lw} %nz.t{k}.{r}, {borrow}')
                    if k<n-1:out += [f'%nz.u{k}.{r} = icmp ult i{lw} {a[k]}, {z[k]}',f'%nz.v{k}.{r} = icmp ult i{lw} %nz.t{k}.{r}, {borrow}',f'%nz.c{k}.{r} = or i1 %nz.u{k}.{r}, %nz.v{k}.{r}']
                self.limbs[i.res]=[f'%nz.m{k}.{r}' for k in range(n)];return out
            if i.op=='add':
                a,bv=d.split_top(b.split(None,2)[2]);a=parts(a);z=parts(bv);out=[f'%nz.m0.{r} = add i64 {a[0]}, {z[0]}',f'%nz.c0.{r} = icmp ult i64 %nz.m0.{r}, {a[0]}']
                for k in range(1,n):
                    lw=widths[k];carry=f'%nz.c{k-1}.{r}'
                    out.append(f'%nz.t{k}.{r} = add i{lw} {a[k]}, {z[k]}')
                    if lw>1:out.append(f'%nz.z{k}.{r} = zext i1 {carry} to i{lw}');carry=f'%nz.z{k}.{r}'
                    out.append(f'%nz.m{k}.{r} = add i{lw} %nz.t{k}.{r}, {carry}')
                    if k<n-1:out += [f'%nz.u{k}.{r} = icmp ult i64 %nz.t{k}.{r}, {a[k]}',f'%nz.v{k}.{r} = icmp ult i64 %nz.m{k}.{r}, %nz.t{k}.{r}',f'%nz.c{k}.{r} = or i1 %nz.u{k}.{r}, %nz.v{k}.{r}']
                self.limbs[i.res]=[f'%nz.m{k}.{r}' for k in range(n)];return out
            if i.op=='store':
                ps=d.split_top(b[6:]);v=d.typed_val(ps[0]);p=d.typed_val(ps[1]);al=re.search(r', align (\d+)',b);al=', align '+al[1] if al else '';out=[]
                for k,val in enumerate(parts(v)):
                    lw=widths[k];mw=(lw+7)//8*8;q=f'%nz.q{k}.{r}';out.append(f'{q} = getelementptr i64, ptr {p}, i64 {k}')
                    if lw!=mw:out.append(f'%nz.pad{k}.{r} = zext i{lw} {val} to i{mw}');val=f'%nz.pad{k}.{r}'
                    out.append(f'store i{mw} {val}, ptr {q}{al}')
                return out
            raise d.Fail('N22 unsupported wide operation '+i.op)
        self.rewrite(go)

    def shadow(self):
        # §17.3 fixed allocas share one zero-filled frame; dynamic allocas use ss_alloca.
        for f in self.funcs():
            allocas=[i for i in f.instrs() if i.op=='alloca']
            if not allocas:continue
            offset=0;align=1;offsets={}
            for i in allocas:
                ps=d.split_top(i.text.split('alloca ',1)[1]);ty=self.typ(ps[0]);sz=d.tsize(ty);al=next((int(p[6:]) for p in ps[1:] if p.startswith('align ')),d.talign(ty));align=max(align,al)
                offset=(offset+al-1)//al*al;offsets[id(i)]=offset;offset+=sz
            size=(offset+align-1)//align*align
            fp=f'%nz.fp.{f.name}'
            entry=f.blocks[0][1];entry.insert(0,d.Instr(f'{fp} = call ptr @__bennett_rt_ss_push(i64 {size}, i64 {align})',fp,'call',f,f.blocks[0][0]))
            self.decl('__bennett_rt_ss_push','ptr',['i64','i64']);self.decl('__bennett_rt_ss_pop','void',['ptr'])
            for lab,blk in f.blocks:
                out=[]
                for i in blk:
                    if i.op=='alloca':i.text=f'{i.res} = getelementptr i8, ptr {fp}, i64 {offsets[id(i)]}';i.op='getelementptr'
                    if i.op=='ret':out.append(d.Instr(f'call void @__bennett_rt_ss_pop(ptr {fp})',None,'call',f,lab))
                    out.append(i)
                blk[:]=out

    def memory(self):
        def go(f,i,r):
            if i.op!='call' or ' asm ' in i.text:return
            c=d.parse_call(i);m=re.match(r'@llvm\.(memcpy|memmove|memset)',c['callee'])
            if not m:return
            kind='memset' if m[1]=='memset' else 'memmove';dval,sval,n=[a[2] for a in c['args'][:3]];nt=d.tstr(c['args'][2][0]);out=[]
            if nt!='i64' and not n.isdigit():out.append(f'%nz.n.{r} = zext {nt} {n} to i64');n=f'%nz.n.{r}'
            st='i8' if kind=='memset' else 'ptr'
            self.decl('__bennett_rt_'+kind,'void',['ptr',st,'i64'])
            return out+[f'call void @__bennett_rt_{kind}(ptr {dval}, {st} {sval}, i64 {n})']
        self.rewrite(go)

    def intrinsics(self):
        def go(f,i,r):
            if i.op!='call' or ' asm ' in i.text:return
            c=d.parse_call(i);cal=c['callee'];t=d.tstr(c['args'][0][0]) if c['args'] else ''
            if re.match(r'@llvm\.[su](min|max)\.',cal):
                op=cal.split('.')[1];pred=('s' if op[0]=='s' else 'u')+('gt' if op[1:]=='max' else 'lt');a,b=[x[2] for x in c['args']]
                return [f'%nz.c.{r} = icmp {pred} {t} {a}, {b}',f'{i.res} = select i1 %nz.c.{r}, {t} {a}, {t} {b}']
            if cal.startswith('@llvm.uadd.with.overflow.'):
                a,b=[x[2] for x in c['args']];return [f'%nz.s.{r} = add {t} {a}, {b}',f'%nz.c.{r} = icmp ult {t} %nz.s.{r}, {a}',f'%nz.a.{r} = insertvalue {{ {t}, i1 }} zeroinitializer, {t} %nz.s.{r}, 0',f'{i.res} = insertvalue {{ {t}, i1 }} %nz.a.{r}, i1 %nz.c.{r}, 1']
            if cal.startswith('@llvm.ctpop.'):
                name='__bennett_rt_ctpop_'+t;self.decl(name,t,[t]);return [f'{i.res} = call {t} @{name}({t} {c["args"][0][2]})']
            if cal.startswith('@llvm.abs.'):
                a=c['args'][0][2]
                return [f'%nz.c.{r} = icmp slt {t} {a}, 0',f'%nz.n.{r} = sub {t} 0, {a}',f'{i.res} = select i1 %nz.c.{r}, {t} %nz.n.{r}, {t} {a}']
            if re.match(r'@llvm\.(ctlz|cttz)\.',cal):
                name='__bennett_rt_'+cal.split('.')[1]+'_'+t
                self.decl(name,t,[t,'i1'])
                return [f'{i.res} = call {t} @{name}({t} {c["args"][0][2]}, i1 false)']
        self.rewrite(go)

    def gc(self):
        def go(f,i,r):
            if i.op!='call' or '@llvm.experimental.gc.get.pointer.' not in i.text:return
            c=d.parse_call(i);v=c['args'][0][2];defs={x.res:x for x in f.instrs() if x.res};off=0;seen=set()
            while v in defs and defs[v].op=='getelementptr':
                if v in seen:raise d.Fail('N27 cyclic GC provenance')
                seen.add(v);ps=d.split_top(defs[v].text.split('getelementptr ',1)[1]);ty=self.typ(ps[0]);indices=[d.typed_val(x) for x in ps[2:]]
                if not all(re.fullmatch(r'-?\d+',x) for x in indices):raise d.Fail('N27 dynamic GC provenance requires offset expression')
                off+=d.gep_offset(ty,[int(x) for x in indices]);v=d.typed_val(ps[1])
            self.replace(f,i.res,v if '.base.' in c['callee'] else str(off));return []
        self.rewrite(go)

    def asm(self):
        def go(f,i,r):
            if i.op!='call' or ' asm ' not in i.text:return
            c=d.parse_call(i)
            if not c['asm']:return []
            if c['asm'].strip()=='syscall':
                args=[f'{d.tstr(a[0])} {a[2]}' for a in c['args']];args+=['i64 0']*(7-len(args));self.decl('__bennett_rt_syscall','i64',['i64']*7)
                return [f'{i.res} = call i64 @__bennett_rt_syscall('+', '.join(args)+')']
            self.decl('__bennett_nz_fault','void',['i64']);return ['call void @__bennett_nz_fault(i64 8)','unreachable']
        self.rewrite(go)

    def fp(self):
        def go(f,i,r):
            b=i.text.split(' = ',1)[-1];op=i.op
            if op=='call' and ' asm ' not in b:
                c=d.parse_call(i);m=re.match(r'@llvm\.(exp|exp2|log|log2|sin|cos|pow)\.',c['callee'])
                if m:
                    t=d.tstr(c['ret']);name=m[1]+('f' if t=='float' else 'l' if t not in ('float','double') else '')
                    self.decl(name,t,[d.tstr(x[0]) for x in c['args']]);i.text=i.text.replace(c['callee'],'@'+name);return
            if op=='fcmp':
                _,pred,rest=b.split(None,2);t,j=d.parse_type(rest);ts=d.tstr(t);sfx,bw=FP[ts];vals=d.split_top(rest[j:])
                predicates='false oeq ogt oge olt ole one ord uno ueq ugt uge ult ule une true'.split()
                name='__bennett_sf_cmp_'+sfx;self.decl(name,'i1',[f'i{bw}',f'i{bw}','i32'])
                decl=f'declare i1 @{name}(i{bw}, i{bw}, i32)'
                if decl in self.appended:self.appended.remove(decl);self.globals.append(decl)
                return [f'%nz.{k}.{r} = bitcast {ts} {val} to i{bw}' for k,val in enumerate(vals)]+[f'{i.res} = call i1 @{name}(i{bw} %nz.0.{r}, i{bw} %nz.1.{r}, i32 {predicates.index(pred)})']
            if op not in d.FBINOPS|{'fpext','fptrunc'}:return
            if op in d.FBINOPS:
                rest=b.split(None,1)[1];t,j=d.parse_type(rest);ts=d.tstr(t);sfx,bw=FP[ts];vals=d.split_top(rest[j:]);dt=ts;dbw=bw;name=f'__bennett_sf_{op[1:]}_{sfx}'
            else:
                src,dst=b[len(op):].rsplit(' to ',1);t,j=d.parse_type(src);ts=d.tstr(t);sfx,bw=FP[ts];dt=dst.strip();dsfx,dbw=FP[dt];vals=[src[j:].strip()];name=f'__bennett_sf_{op}_{sfx}_{dsfx}'
            out=[f'%nz.{k}.{r} = bitcast {ts} {val} to i{bw}' for k,val in enumerate(vals)]
            self.decl(name,f'i{dbw}',[f'i{bw}']*len(vals))
            out.append(f'%nz.i.{r} = call i{dbw} @{name}('+', '.join(f'i{bw} %nz.{k}.{r}' for k in range(len(vals)))+')')
            out.append(f'{i.res} = bitcast i{dbw} %nz.i.{r} to {dt}')
            return out
        self.rewrite(go)

    def traps(self):
        for f in self.funcs():
            for i in list(f.instrs()):
                if i.op=='call' and re.search(r'@llvm\.(trap|debugtrap|ubsantrap)',i.text):
                    d.fault_replace(f,i,4);self.decl('__bennett_nz_fault','void',['i64'])

    def result(self):
        return ('\n'.join(self.globals)+'\n\n' if self.globals else '')+d.print_module(self.m,self.original.rstrip('\n').split('\n'),self.appended)

    def run(self):
        self.byval();self.basic();self.platform_hooks();self.atomics();self.traps();self.shifts();self.fmuladd();self.vector();self.intrinsics();self.wide()
        self.varargs();self.shadow();self.memory();self.intrinsics();self.gc();self.eh();self.asm();self.fp();self.wide()
        self.rsteps()
        return self.result()

    def byval(self):
        # N25: caller-owned copy, then N24 gives it the common shadow frame.
        attr=r'(?:byval|inalloca|preallocated)\(([^)]+)\)(?: align (\d+))?'
        for f in self.funcs():
            f.header=re.sub(attr,'',f.header)
            f.header=re.sub(r'ptr\s+%','ptr %',f.header)
        def go(f,i,r):
            if i.op!='call' or ' asm ' in i.text:return
            c=d.parse_call(i);out=[];text=i.text
            for j,(ty,attrs,value) in enumerate(c['args']):
                match=next((re.fullmatch(attr,a) for a in attrs if re.fullmatch(attr,a)),None)
                # parse_call can separate the ABI attribute from align.
                if match is None:
                    joined=' '.join(attrs);match=re.search(attr,joined)
                if match is None:continue
                t=self.typ(match[1]);size=d.tsize(t);al=int(match[2] or d.talign(t));slot=f'%nz.bv{j}.{r}'
                out += [f'{slot} = alloca {d.tstr(t)}, align {al}',f'call void @llvm.memcpy.p0.p0.i64(ptr {slot}, ptr {value}, i64 {size}, i1 false)']
                typed='ptr'+(' '+' '.join(attrs) if attrs else '')+' '+value
                text=text.replace(typed,'ptr '+slot,1)
            return out+[text] if out else None
        self.rewrite(go)

    def platform_hooks(self):
        if self.platform is None:return
        if self.platform!='riscv64-bennett-virt':raise d.Fail('N35 unknown platform '+self.platform)
        self.decl('__bennett_rt_poll','void',[])
        for f in self.funcs():
            if f.name.startswith(('__bennett_rt_','__bennett_dev_')):continue
            labels=[lab for lab,_ in f.blocks];pred={lab:set() for lab in labels}
            for lab,blk in f.blocks:
                for target in re.findall(r'label %([-\w.$]+)',blk[-1].text):pred[target].add(lab)
            dom={lab:({lab} if lab==labels[0] else set(labels)) for lab in labels}
            while True:
                old={lab:set(ds) for lab,ds in dom.items()}
                for lab in labels[1:]:dom[lab]={lab}|(set.intersection(*(dom[p] for p in pred[lab])) if pred[lab] else set())
                if old==dom:break
            for lab,blk in f.blocks:
                out=[]
                if lab==labels[0]:out.append(d.Instr('call void @__bennett_rt_poll()',None,'call',f,lab))
                for i in blk:
                    if i is blk[-1] and any(target in dom[lab] for target in re.findall(r'label %([-\w.$]+)',i.text)):
                        out.append(d.Instr('call void @__bennett_rt_poll()',None,'call',f,lab))
                    body=i.text.split(' = ',1)[-1]
                    if i.op in ('load','store') and 'volatile' in body:
                        ps=d.split_top(body.split('volatile ',1)[1]);t=d.parse_type(ps[0])[0];ts=d.tstr(t);p=d.typed_val(ps[1])
                        name='__bennett_rt_mmio_'+i.op+'_'+ts
                        if i.op=='load':
                            self.decl(name,ts,['ptr']);i.text=f'{i.res} = call {ts} @{name}(ptr {p})'
                        else:
                            self.decl(name,'void',['ptr',ts]);i.text=f'call void @{name}(ptr {p}, {ts} {d.typed_val(ps[0])})'
                        i.op='call'
                    out.append(i)
                blk[:]=out

    def rsteps(self):
        if not self.rmode:return
        entry=self.rmode.lstrip('@')
        if not self.m.defined(entry):raise d.Fail('N34 missing R entry '+entry)
        selected={entry}
        while True:
            old=set(selected)
            for name in old:
                for i in self.m.funcs[name].instrs():
                    if i.op=='call' and ' asm ' not in i.text:
                        cal=d.parse_call(i)['callee'].lstrip('@')
                        if self.m.defined(cal):selected.add(cal)
            if old==selected:break
        used={int(x) for x in re.findall(r'!(\d+)',self.original)};n=0
        while n in used:n+=1
        for name in selected:
            for i in self.m.funcs[name].instrs():
                if i.op!='phi' and '@llvm.dbg.' not in i.text and '!bennett.rstep' not in i.text:
                    i.text+=f', !bennett.rstep !{n}'
        self.appended.append(f'!{n} = !{{}}')

    def varargs(self):
        varfuncs={f.name:f for f in self.funcs() if f.vararg}
        if not varfuncs:return
        for f in varfuncs.values():
            f.header=f.header.replace('...', 'ptr %nz.va');f.vararg=False
        def go(f,i,r):
            if i.op!='call':return
            c=d.parse_call(i)
            if c['callee']=='@llvm.va_end':return []
            if c['callee']=='@llvm.va_start':
                p=c['args'][0][2]
                return [f'store i32 48, ptr {p}, align 4',
                    f'%nz.vfo.{r} = getelementptr i8, ptr {p}, i64 4',
                    f'store i32 176, ptr %nz.vfo.{r}, align 4',
                    f'%nz.vov.{r} = getelementptr i8, ptr {p}, i64 8',
                    f'store ptr %nz.va, ptr %nz.vov.{r}, align 8',
                    f'%nz.vrs.{r} = getelementptr i8, ptr {p}, i64 16',
                    f'store ptr null, ptr %nz.vrs.{r}, align 8']
            if c['callee'][1:] not in varfuncs:return
            gf=varfuncs[c['callee'][1:]];fixed=len(gf.params);args=c['args'][fixed:]
            vb=f'%nz.vb.{r}';size=sum((d.tsize(x[0])+7)//8*8 for x in args)
            al=max([8]+[d.talign(x[0]) for x in args]);alloc=d.Instr(f'{vb} = alloca [{size} x i8], align {al}',vb,'alloca',f,f.blocks[0][0])
            # Entry insertion happens after rewriting, so it is not lost by rewrite().
            f._va_allocas=getattr(f,'_va_allocas',[])+[alloc]
            out=[];off=0
            for j,(ty,attrs,val) in enumerate(args):
                p=vb if j==0 else f'%nz.vb{j}.{r}'
                if j:out.append(f'{p} = getelementptr i8, ptr {vb}, i64 {off}')
                out.append(f'store {d.tstr(ty)} {val}, ptr {p}, align 8');off+=(d.tsize(ty)+7)//8*8
            params=[f'{d.tstr(t)} {v}' for t,_,v in c['args'][:fixed]]+['ptr '+vb]
            out.append((i.res+' = ' if i.res else '')+f'call {d.tstr(c["ret"])} {c["callee"]}('+', '.join(params)+')')
            return out
        self.rewrite(go)
        for f in self.funcs():
            f.blocks[0][1][:0]=getattr(f,'_va_allocas',[])
        self.original=re.sub(r'^declare void @llvm.va_(?:start|end)\(ptr\)\n?', '', self.original, flags=re.M)

    def eh(self):
        if not any(i.op=='invoke' for f in self.funcs() for i in f.instrs()):return
        self.globals.insert(0,'@__bennett_rt_eh = external global { i32, i32, ptr }')
        for f in self.funcs():
            personality=re.search(r'personality ptr (@[-\w.$]+)',f.header)
            if not personality:continue
            pers=personality[1];f.header=re.sub(r' personality .*? \{$',' {',f.header)
            extra=[];count=0
            for lab,blk in list(f.blocks):
                out=[];current=out
                for i in blk:
                    r=i.res[1:] if i.res else f.name+'.'+str(count)
                    if i.op=='invoke':
                        c=d.parse_call(i);body=i.text.split(' = ',1)[-1]
                        call=re.sub(r'^invoke ','call ',body);call=re.sub(r'\s+to label .*','',call)
                        current += [d.Instr((i.res+' = ' if i.res else '')+call,i.res,'call',f,lab),
                            d.Instr(f'%nz.ehl.{r} = load i32, ptr @__bennett_rt_eh, align 4',f'%nz.ehl.{r}','load',f,lab),
                            d.Instr(f'%nz.ehc.{r} = icmp ne i32 %nz.ehl.{r}, 0',f'%nz.ehc.{r}','icmp',f,lab),
                            d.Instr(f'br i1 %nz.ehc.{r}, label {c["unwind"][1]}, label {c["unwind"][0]}',None,'br',f,lab)]
                        if not i.res:count+=1
                    elif i.op=='landingpad':
                        clauses=[x for x in blk if x.op=='catch']
                        if any(x.text!='catch ptr null' for x in clauses):raise d.Fail('N28 typeinfo personality matching not implemented')
                        n=len(clauses);items=', '.join('{ i64, ptr } { i64 0, ptr null }' for _ in clauses)
                        glob=f'@nz.lp.{f.name}.{r}'
                        self.globals.append(f'{glob} = private constant {{ i64, i64, [{n} x {{ i64, ptr }}] }} {{ i64 0, i64 {n}, [{n} x {{ i64, ptr }}] [{items}] }}')
                        lines=[f'{i.res} = call {{ ptr, i32 }} @__bennett_rt_eh_match(ptr {pers}, ptr {glob})',
                            f'%nz.ehm.{r} = extractvalue {{ ptr, i32 }} {i.res}, 1',
                            f'%nz.ehn.{r} = icmp eq i32 %nz.ehm.{r}, -1',
                            f'br i1 %nz.ehn.{r}, label %nz.ehr.{f.name}, label %nz.lpc.{r}']
                        for line in lines:
                            m=re.match(r'(%[-\w.$]+) = (.*)',line);res,b=(m[1],m[2]) if m else (None,line);current.append(d.Instr(line,res,b.split()[0],f,lab))
                        current=[];extra.append((f'nz.lpc.{r}',current))
                        self.decl('__bennett_rt_eh_match','{ ptr, i32 }',['ptr','ptr'])
                    elif i.op!='catch':current.append(i)
                blk[:]=out
            f.blocks+=extra
            z='null' if f.ret[0]=='ptr' else '0'
            lab='nz.ehr.'+f.name;line='ret void' if f.ret[0]=='void' else f'ret {d.tstr(f.ret)} {z}'
            f.blocks.append((lab,[d.Instr(line,None,'ret',f,lab)]))


def normalise(text,**context):return Normaliser(text,**context).run()
