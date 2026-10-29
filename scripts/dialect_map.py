"""Dialect §16 reference-object map. Emits rows without consulting object= text."""
import collections
import json
import re
from pathlib import Path
import dialect_check as d
from dialect_check_v02 import Analysis02, command, equal


def jcs(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def bits(t):
    if t[0]=='ptr':return 64
    if t[0]=='void':return 1
    if t[0]=='struct':return sum(bits(x) for x in t[1])
    if t[0] in ('arr','vec'):return t[1]*bits(t[2])
    if t[0] in ('half','bfloat','float','double','x86_fp80','fp128','ppc_fp128'):
        return {'half':16,'bfloat':16,'float':32,'double':64,'x86_fp80':80,'fp128':128,'ppc_fp128':128}[t[0]]
    return t[1]


class Mapper:
    def __init__(self,text,region,desc,linkmap,arena=None):
        self.m=d.Module(text);self.entry=region.lstrip('@');self.desc=desc;self.linkmap=linkmap
        self.arena=arena or {};self.arena_functions=set()
        for name,f in self.m.funcs.items():
            if f.is_def and any('@'+g in i.text for i in f.instrs() for g in self.arena):self.arena_functions.add(name)
        for _ in self.m.funcs:
            for name,f in self.m.funcs.items():
                if f.is_def and any(re.search(r'@'+re.escape(g)+r'\(',i.text) for i in f.instrs() for g in self.arena_functions):self.arena_functions.add(name)
        self.globals={};self.addresses={};self.names={};self.bodies={};self.signatures={};self.images={}
        for name,g,base,size in re.findall(r'global @([-\w.$]+) -> (G\d+) base=(\d+) size=(\d+)',linkmap):
            self.globals[name]=(g,int(base),int(size))
        self.addresses={name:int(addr,0) for name,addr in re.findall(r'function @([-\w.$]+) A=(0x[\da-f]+|\d+)',linkmap)}
        def fact(key):
            m=re.search(key+r'=(\d+)',linkmap)
            if not m:raise d.Fail('§16.3 missing linkmap fact '+key)
            return int(m[1])
        self.null_size=fact('null_size');self.heap_base=fact('heap_base');self.heap=fact('heap_limit_max')
        stack=re.search(r'(?:stack max|largest stack) (\d+)',linkmap)
        if not stack:raise d.Fail('§16.3 missing budget stack maximum')
        self.stack=int(stack[1]);self.regions={}
        self.analysis=Analysis02(self.m,materialised=True);self.analysis.analyse()

    def closure(self,name):
        if name in self.names:return
        if not self.m.defined(name):raise d.Fail('§16.1 unmaterialised external function '+name)
        self.names[name]='L'+str(len(self.names)+1)
        f=self.m.funcs[name]
        for ins in f.instrs():
            if ins.op!='call':continue
            c=d.parse_call(ins)
            if c['callee'].startswith('@__bennett_nz_'):continue
            candidates={c['callee'][1:]} if c['callee'].startswith('@') else self.analysis.indirect.get(id(ins),set())
            for target in sorted(candidates,key=lambda n:self.addresses.get(n,0)):self.closure(target)

    def image(self,name):
        g=self.m.globals[name];ty=g['type'];value=g['init'];width=d.tsize(ty)
        if value in ('null','zeroinitializer'):return bytes(width)
        if ty[0]=='arr':
            return b''.join(self.constant_bytes(ty[2],d.typed_val(x)) for x in d.split_top(value[1:-1]))
        return self.constant_bytes(ty,value)

    def constant_bytes(self,ty,value):
        n=d.tsize(ty)
        if value.startswith('blockaddress('):
            fn,lab=re.fullmatch(r'blockaddress\(@([-\w.$]+), %([-\w.$]+)\)',value).groups()
            v=self.block_addresses(fn)[lab]
        elif value.startswith('@'):
            name=value[1:];v=self.addresses.get(name)
            if v is None:v=self.globals[name][1]
        else:v=0 if value in ('null','zeroinitializer') else int(value)
        return (v%(1<<(8*n))).to_bytes(n,'little')

    def block_addresses(self,name):
        taken=set(re.findall(r'blockaddress\(@'+re.escape(name)+r', %([-\w.$]+)\)',self.m.text))
        labels=[lab for lab,_ in self.m.funcs[name].blocks if lab in taken]
        obj='__bennett_rt_blk.'+name
        if obj not in self.globals:raise d.Fail('§14.9 missing comparison block object '+obj)
        base=self.globals[obj][1]
        return {lab:base+k for k,lab in enumerate(labels)}

    def wrapper(self):
        f=self.m.funcs[self.entry];desc=self.desc
        param_part=desc.split(';')[0] if not desc.startswith('dev=') else ''
        bindings=re.findall(r'(IN|ARG|MEM_IN|OUT)\(([^)]+)\)',param_part)
        if len(bindings)!=len(f.params):raise d.Fail('§16.2 binding arity')
        ins=[];mem=[];args=[];rows=[];regs=collections.OrderedDict();actual=[];cn=tn=0
        def dest(name,w,row):regs[name]=w;rows.append(name+' = '+row);return name
        def const(w,value):
            nonlocal cn
            name='c'+str(cn);cn+=1;return dest(name,w,f'lift.const.i{w} {value}')
        def temp(w,row):
            nonlocal tn
            name='t'+str(tn);tn+=1;return dest(name,w,row)
        if self.entry in self.arena_functions:
            mem.append(('coh',max(1,(max(self.arena.values())+1-1).bit_length())))
            dest('d0',64,'lift.addr @coh')
        # §16.2 model order: ENTROPY, BLOCK, CLOCK, CONSOLE.
        dn=0;outputs=[]
        def dvalue(row):
            nonlocal dn
            n='d'+str(dn);dn+=1;return dest(n,64,row)
        def store_global(name,value):
            address=dvalue('lift.addr @'+self.globals[name][0])
            rows.extend(['lift.boundscheck '+address+' 8','lift.store.i64 '+address+' '+value])
        models=dict(re.findall(r'(ENTROPY|BLOCK|CLOCK|CONSOLE)\((\d+)\)',desc.split(';dev=',1)[-1] if ';dev=' in desc else desc if desc.startswith('dev=') else ''))
        for model in ('ENTROPY','BLOCK','CLOCK','CONSOLE'):
            if model not in models:continue
            value=int(models[model])
            if model in ('ENTROPY','BLOCK'):
                region='e0' if model=='ENTROPY' else 'k0';A=value+(9 if model=='BLOCK' else 0)
                mem.append((region,A));base=dvalue('lift.addr @'+region)
                prefix='__bennett_dev_'+model.lower()
                store_global(prefix+'_base',base)
                length=dvalue('lift.const.i64 '+str(1<<value))
                store_global(prefix+('_size' if model=='ENTROPY' else '_nsect'),length)
            elif model=='CLOCK':
                value=dvalue('lift.const.i64 '+str(value));store_global('__bennett_dev_clock_c',value)
            else:
                length=dvalue('lift.const.i64 '+str(value));store_global('__bennett_dev_console_L',length)
                buf=dvalue('lift.alloc '+length);store_global('__bennett_dev_console_buf',buf)
                zero=dvalue('lift.const.i64 0');store_global('__bennett_dev_console_n',zero)
                outputs.append((buf,value))
        for i,((kind,value),(ty,_,_)) in enumerate(zip(bindings,f.params)):
            w=bits(ty);name='w'+str(i)
            if kind=='IN':
                n,mode=value.split(',');n=int(n);x='x'+str(len(ins));ins.append(n)
                actual.append(x if n==w else dest(name,w,f'lift.{"sext" if mode=="sext" else "zext"}.i{w} {x}'))
            elif kind=='ARG':
                a='a'+str(len(args));args.append('i'+str(w));actual.append(a)
            elif kind=='MEM_IN':
                mn='m'+str(sum(n.startswith('m') for n,_ in mem));mem.append((mn,int(value)));actual.append(dest(name,w,'lift.addr @'+mn))
            elif kind=='OUT':
                size=const(64,int(value));buf=dest(name,w,'lift.alloc '+size);actual.append(buf);outputs.insert(i,(buf,int(value)))
        if self.entry in self.arena_functions:actual.append('d0')
        R=bits(f.ret);T=int(re.search(r'tgt=(\d+)',desc)[1]);dest('r',R,'lift.call @L1 ('+', '.join(actual)+')')
        result='r'
        if outputs:
            if len(outputs)!=1 or f.ret[0]!='void':raise d.Fail('§16.2 multiple payloads need an explicit slice selection')
            buf,size=outputs[0]
            if T>8*size or T>128:raise d.Fail('§16.2 payload slice width exceeds buffer/carrier')
            rows.append(f'lift.boundscheck {buf} {(T+7)//8}');result=temp(T,f'lift.load.i{T} {buf}')
        elif T<R:
            c=const(R,T);t=temp(R,'lift.lshr r '+c);z=const(R,0);u=temp(1,'lift.icmp.ne '+t+' '+z);rows.append('lift.faultif '+u+' 4');result=temp(T,f'lift.trunc.i{T} r')
        elif T>R:result=temp(T,f'lift.zext.i{T} r')
        rows.append('lift.retval '+result)
        header='oracle @ref ('+', '.join(f'x{k}:wire[{n}] in' for k,n in enumerate(ins))+f') (tgt:wire[{T}]) (fault:wire[4]) ('+', '.join(f'{n}:region[{A},8] in' for n,A in mem)+') ('+', '.join(f'a{k}:{t}' for k,t in enumerate(args))+')'
        sig={'abi':'0.8','args':args,'fault':4,'in':ins,'kind':'oracle','mem':[{'A':A,'W':8,'role':'in'} for _,A in mem],'tgt':T,'tier':'q'}
        self.signatures['ref']=sig;self.regions={n:1<<A for n,A in mem}
        regline='regs { '+', '.join(f'{n}:reg[{w}]' for n,w in regs.items())+' }'
        return '\n'.join([header,regline,'^entry():',*rows])

    def lproc(self,name):
        f=self.m.funcs[name];label=self.names[name];params={p[2]:'a'+str(i) for i,p in enumerate(f.params)}
        values={i.res:'v'+str(k) for k,i in enumerate(x for x in f.instrs() if x.res)}
        widths={};constants=temps=0;blocks=[];bidx={lab:i for i,(lab,_) in enumerate(f.blocks)}
        phis={lab:[i for i in blk if i.op=='phi'] for lab,blk in f.blocks}
        def assign(n,w,row,rows):widths[n]=w;rows.append(n+' = '+row);return n
        def fresh(prefix,w,row,rows):
            nonlocal constants,temps
            if prefix=='c':n='c'+str(constants);constants+=1
            else:n='t'+str(temps);temps+=1
            return assign(n,w,row,rows)
        def operand(v,ty,rows):
            if v in params:return params[v]
            if v in values:return values[v]
            w=bits(ty)
            if v.startswith('@'):
                n=v[1:]
                if n in self.arena:
                    base=fresh('c',64,'lift.mov a'+str(len(f.params)),rows);offset=self.arena[n]
                    if offset:
                        delta=fresh('c',64,'lift.const.i64 '+str(offset),rows);base=fresh('t',64,'lift.add '+base+' '+delta,rows)
                    return base
                if n in self.globals:return fresh('c',64,'lift.addr @'+self.globals[n][0],rows)
                if n in self.addresses:return fresh('c',64,'lift.const.i64 '+str(self.addresses[n]),rows)
                raise d.Fail('§16.3 missing address '+n)
            if v.startswith('blockaddress('):
                fn,lab=re.fullmatch(r'blockaddress\(@([-\w.$]+), %([-\w.$]+)\)',v).groups()
                return fresh('c',64,'lift.const.i64 '+str(self.block_addresses(fn)[lab]),rows)
            val=0 if v in ('null','false','zeroinitializer') else 1 if v=='true' else int(v)%(1<<w)
            return fresh('c',w,f'lift.const.i{w} {val}',rows)
        def moves(src,dst,rows):
            if not phis[dst]:return
            dests=[];srcs=[]
            for phi in phis[dst]:
                body=phi.text.split(' = ',1)[1][4:];ty,j=d.parse_type(body)
                inc={b.strip()[1:]:v.strip() for v,b in (d.split_top(x[1:-1]) for x in d.split_top(body[j:]))}
                srcs.append(operand(inc[src],ty,rows));dst=values[phi.res];dests.append(dst);widths[dst]=bits(ty)
            rows.append('('+', '.join(dests)+') = lift.parmov ('+', '.join(srcs)+')')
        for i,(lab,blk) in enumerate(f.blocks):
            rows=[];extra=[];edge=set();compare_count=0;call_count=0
            def target(lab):
                if phis[lab]:edge.add(bidx[lab]);return f'^b{i}.e{bidx[lab]}'
                return '^b'+str(bidx[lab])
            def newblock():
                nonlocal compare_count
                compare_count+=1;name=f'b{i}.s{compare_count}';arr=[];extra.append((name,arr));return '^'+name,arr
            def tree(cond,w,keys,default,current):
                if not keys:current.append('qjump '+default);return
                if len(keys)<=3:
                    for j,(key,tgt) in enumerate(keys):
                        c=fresh('c',w,f'lift.const.i{w} {key}',current);t=fresh('t',1,f'lift.icmp.eq {cond} {c}',current)
                        nxt,nrows=newblock() if j<len(keys)-1 else (default,None)
                        current.append(f'qbranch {t} {tgt} {nxt}')
                        if nrows is not None:current=nrows
                else:
                    mid=(len(keys)-1)//2;c=fresh('c',w,f'lift.const.i{w} {keys[mid][0]}',current);t=fresh('t',1,f'lift.icmp.ult {cond} {c}',current)
                    left,lrows=newblock();right,rrows=newblock();current.append(f'qbranch {t} {left} {right}')
                    tree(cond,w,keys[:mid],default,lrows);tree(cond,w,keys[mid:],default,rrows)
            live=list(x for x in blk if not x.deleted);j=0;current=rows
            while j<len(live):
                inst=live[j];op=inst.op;body=inst.text.split(' = ',1)[-1];v=values.get(inst.res)
                rt=self.analysis.result_type(inst) if inst.res else None
                if op in d.BINOPS:
                    rest=body.split(None,1)[1];ty,k=d.parse_type(rest);a,b=d.split_top(rest[k:]);A=operand(a,ty,current);B=operand(b,ty,current);assign(v,bits(ty),'lift.'+op+' '+A+' '+B,current)
                elif op=='icmp':
                    _,pred,rest=body.split(None,2);ty,k=d.parse_type(rest);a,b=d.split_top(rest[k:]);A=operand(a,ty,current);B=operand(b,ty,current)
                    if pred in ('ugt','uge','sgt','sge'):pred={'ugt':'ult','uge':'ule','sgt':'slt','sge':'sle'}[pred];A,B=B,A
                    assign(v,1,f'lift.icmp.{pred} {A} {B}',current)
                elif op=='select':
                    ps=d.split_top(body[6:].strip());parts=[operand(d.typed_val(p),d.parse_type(p)[0],current) for p in ps];assign(v,bits(rt),'lift.select '+' '.join(parts),current)
                elif op in ('zext','sext','trunc','ptrtoint','inttoptr','bitcast','addrspacecast'):
                    src,dst=body[len(op):].rsplit(' to ',1);ty=d.parse_type(src)[0];dt=d.parse_type(dst)[0];A=operand(d.typed_val(src),ty,current)
                    operation=op
                    if op in ('ptrtoint','inttoptr','bitcast','addrspacecast'):operation='mov' if bits(ty)==bits(dt) else 'trunc' if bits(ty)>bits(dt) else 'zext'
                    assign(v,bits(dt),'lift.'+operation+('' if operation=='mov' else '.i'+str(bits(dt)))+' '+A,current)
                elif op=='getelementptr':
                    ps=d.split_top(body[len(op):].strip());ty=d.parse_type(ps[0])[0];P=operand(d.typed_val(ps[1]),('ptr',),current);acc=P;delta=0;dynamic=[];ct=ty
                    for k,p in enumerate(ps[2:]):
                        idx=d.typed_val(p);ity=d.parse_type(p)[0]
                        if k==0:sz=d.tsize(ct)
                        elif ct[0] in ('arr','vec'):ct=ct[2];sz=d.tsize(ct)
                        elif ct[0]=='struct':delta+=d.gep_offset(ct,[0,int(idx)]);ct=ct[1][int(idx)];continue
                        else:raise d.Fail('§16.4 GEP scalar indexing')
                        if re.fullmatch(r'-?\d+',idx):delta+=int(idx)*sz
                        else:dynamic.append((idx,ity,sz))
                    for k,(idx,ity,sz) in enumerate(dynamic):
                        I=operand(idx,ity,current)
                        if bits(ity)!=64:I=fresh('t',64,'lift.'+('sext' if bits(ity)<64 else 'trunc')+'.i64 '+I,current)
                        if sz!=1:
                            c=fresh('c',64,f'lift.const.i64 {sz}',current);I=fresh('t',64,f'lift.mul {I} {c}',current)
                        last=k==len(dynamic)-1 and delta==0
                        acc=assign(v,64,f'lift.add {acc} {I}',current) if last else fresh('t',64,f'lift.add {acc} {I}',current)
                    if delta:
                        C=fresh('c',64,'lift.const.i64 '+str(delta%(1<<64)),current);assign(v,64,f'lift.add {acc} {C}',current)
                    elif not dynamic:assign(v,64,'lift.mov '+P,current)
                elif op=='load':
                    ps=d.split_top(body[5:]);ty=d.parse_type(ps[0])[0];P=operand(d.typed_val(ps[1]),('ptr',),current);w=bits(ty);current.append(f'lift.boundscheck {P} {w//8}');assign(v,w,f'lift.load.i{w} {P}',current)
                elif op=='store':
                    ps=d.split_top(body[6:]);ty=d.parse_type(ps[0])[0];V=operand(d.typed_val(ps[0]),ty,current);P=operand(d.typed_val(ps[1]),('ptr',),current);w=bits(ty);current += [f'lift.boundscheck {P} {w//8}',f'lift.store.i{w} {P} {V}']
                elif op=='call':
                    c=d.parse_call(inst);cal=c['callee'];args=[operand(x[2],x[0],current) for x in c['args']]
                    if cal=='@__bennett_nz_fault':
                        # Fault's C is an immediate, never a materialised operand.
                        if current and current[-1].startswith(args[0]+' = lift.const.'):
                            widths.pop(args[0],None);current.pop();constants-=1
                        current.append('fault '+c['args'][0][2]);j+=2;continue
                    if cal=='@__bennett_nz_alloc':assign(v,64,'lift.alloc '+args[0],current)
                    elif cal=='@__bennett_nz_free':current.append('lift.free '+args[0])
                    elif cal.startswith('@'):
                        dest=v if v is not None else 't'+str(temps)
                        if v is None:temps+=1
                        if cal[1:] in self.arena_functions:args.append('a'+str(len(f.params)))
                        assign(dest,bits(c['ret']),'lift.call @'+self.names[cal[1:]]+' ('+', '.join(args)+')',current)
                    else:
                        call_count+=1;cond=operand(cal,('ptr',),current);cs=sorted(self.analysis.indirect.get(id(inst),set()),key=lambda n:self.addresses[n]);keys=[]
                        for k,n in enumerate(cs):keys.append((self.addresses[n],f'^b{i}.q{call_count}c{k}'))
                        tree(cond,64,keys,f'^b{i}.q{call_count}d',current)
                        for k,n in enumerate(cs):
                            leaf=[];assign(v,bits(c['ret']),'lift.call @'+self.names[n]+' ('+', '.join(args)+')',leaf);leaf.append(f'qjump ^b{i}.q{call_count}r');extra.append((f'b{i}.q{call_count}c{k}',leaf))
                        extra.append((f'b{i}.q{call_count}d',['fault 4']));current=[];extra.append((f'b{i}.q{call_count}r',current))
                elif op=='ret':
                    if body=='ret void':current.append('lift.ret r')
                    else:
                        ty,k=d.parse_type(body[4:]);val=body[4+k:].strip()
                        if ty[0]=='struct':
                            fields=d.split_top(val[1:-1]);scalars=[operand(d.typed_val(x),t,current) for t,x in zip(ty[1],fields)]
                            packed=None;offset=0;w=bits(ty)
                            for t,src in zip(ty[1],scalars):
                                part=src if bits(t)==w else fresh('t',w,f'lift.zext.i{w} {src}',current)
                                if offset:
                                    shift=fresh('c',w,f'lift.const.i{w} {offset}',current)
                                    part=fresh('t',w,f'lift.shl {part} {shift}',current)
                                packed=part if packed is None else fresh('t',w,f'lift.or {packed} {part}',current)
                                offset+=bits(t)
                            A=packed
                        else:A=operand(val,ty,current)
                        current.append('lift.ret '+A)
                elif op=='unreachable':current.append('fault 4')
                elif op=='phi':pass
                elif op=='br':
                    labs=re.findall(r'label %([-\w.$]+)',body)
                    if len(labs)==1 or labs[0]==labs[1]:moves(lab,labs[0],current);current.append('qjump ^b'+str(bidx[labs[0]]))
                    else:
                        cond=re.match(r'br i1 ([^,]+),',body)[1];C=operand(cond,('int',1),current);current.append('qbranch '+C+' '+target(labs[0])+' '+target(labs[1]))
                elif op=='indirectbr':
                    dest,labels=d.split_top(body[len(op):].strip())
                    C=operand(d.typed_val(dest),('ptr',),current);addresses=self.block_addresses(name)
                    keys=sorted((addresses[label],target(label)) for label in re.findall(r'label %([-\w.$]+)',labels))
                    tree(C,64,keys,f'^b{i}.d',current);extra.append((f'b{i}.d',['fault 4']))
                elif op=='switch':
                    m=re.match(r'switch (i\d+) ([^,]+), label %([-\w.$]+) \[(.*)\]',body);ty=d.parse_type(m[1])[0];C=operand(m[2],ty,current)
                    keys=sorted((int(k)%(1<<bits(ty)),target(t)) for k,t in re.findall(r'i\d+ (-?\d+), label %([-\w.$]+)',m[4]));tree(C,bits(ty),keys,target(m[3]),current)
                else:raise d.Fail('checker-unimplemented: §16.4 '+inst.text)
                j+=1
            blocks.append(('b'+str(i),rows));blocks+=extra
            for successor in sorted(edge):
                erows=[];moves(lab,f.blocks[successor][0],erows);erows.append('qjump ^b'+str(successor));blocks.append((f'b{i}.e{successor}',erows))
        # §16.3 numbers constants/temporaries in the final printed block order.
        renames={};counts={'c':0,'t':0}
        for _,rows in blocks:
            for row in rows:
                if ' = ' not in row:continue
                lhs=row.split(' = ',1)[0]
                for n in re.findall(r'\b[ct]\d+\b',lhs):
                    if n not in renames:
                        renames[n]=n[0]+str(counts[n[0]]);counts[n[0]]+=1
        widths={renames.get(n,n):w for n,w in widths.items()}
        for _,rows in blocks:
            rows[:]=[re.sub(r'\b[ct]\d+\b',lambda m:renames.get(m[0],m[0]),row) for row in rows]
        order=[]
        for _,rows in blocks:
            for row in rows:
                if ' = ' not in row:continue
                for n in re.findall(r'[\w.]+',row.split(' = ',1)[0]):
                    if n in widths and n not in order:order.append(n)
        pws=[bits(x[0]) for x in f.params]+([64] if name in self.arena_functions else []);R=bits(f.ret)
        sig={'abi':'0.8','kind':'lproc','params':pws,'result':R,'tier':'q'};self.signatures[label]=sig
        header='lproc @'+label+' ('+', '.join(f'a{k}:reg[{w}]' for k,w in enumerate(pws))+f') (r:reg[{R}]) () () ()'
        lines=[header]
        if order:lines.append('regs { '+', '.join(f'{n}:reg[{widths[n]}]' for n in order)+' }')
        for block,rows in blocks:lines+=['^'+block+'():',*rows]
        return '\n'.join(lines)

    def run(self,isa,path):
        self.closure(self.entry);wrapper=self.wrapper()
        bodies=[wrapper]+[self.lproc(n) for n in self.names]
        used=set(re.findall(r'lift.addr @(G\d+)', '\n'.join(bodies)))
        # Pointer initialisers keep their transitive data dependencies live.
        while True:
            before=set(used)
            for name,(g,_,_) in self.globals.items():
                if g in used:
                    for ref in re.findall(r'@([-\w.$]+)',self.m.globals[name]['init']):
                        if ref in self.globals:used.add(self.globals[ref][0])
            if used==before:break
        globs={g:{'base':base,'image':g,'size':size} for name,(g,base,size) in self.globals.items() if g in used}
        regions={};end=self.heap_base+self.heap
        for name,size in self.regions.items():end=(end+size-1)//size*size;regions[name]={'base':end};end+=size
        end=max([end,self.null_size]+[g['base']+g['size'] for g in globs.values()])
        ceil_log=lambda n:(max(n,1)-1).bit_length()
        layout={'A_tab':ceil_log(len(globs)+len(regions)+self.heap),'H':ceil_log(end),'S_cells':ceil_log(self.stack),'globals':globs,'heap_base':self.heap_base,'heap_limit_max':self.heap,'interface_regions':{'ref':regions},'null_size':self.null_size,'ptr_width':64}
        for key in ('H','A_tab','S_cells'):
            explicit=re.search(r'\b'+key+r'=(\d+)',self.linkmap)
            if explicit:layout[key]=int(explicit[1])
        symbols={str(i):{'interface_hash':'0'*64,'kind':sig['kind'],'name':name,'signature':sig} for i,(name,sig) in enumerate(self.signatures.items())}
        data=[]
        for name,(g,_,size) in self.globals.items():
            if g in globs:
                data.append(g+' '+self.image(name).hex());sig={'abi':'0.8','kind':'data','size':size,'tier':'-'};symbols[str(len(symbols))]={'interface_hash':'0'*64,'kind':'data','name':g,'signature':sig}
        prefix='bennett-object isa=0.8 object=0.8 launch=0.8 sched=0.8 cert=0.8 coverage=0.8 target=0.8 ptr_width=64\n\nsection symbols\n'
        tail='\n\nsection functions\n'+'\n'.join(bodies)+'\n'
        if data:tail+='\nsection data\n'+'\n'.join(data)+'\n'
        tail+='\nsection layout\n'+jcs(layout)+'\n'
        path.write_text(prefix+jcs(symbols)+tail)
        identities=isa.call('hash',path)
        for s in symbols.values():s['interface_hash']=identities['symbols'][s['name']]['interface_hash']
        return prefix+jcs(symbols)+tail


def map_object(runner,block):
    a=block['attrs'];ident=a['lift'];path=runner.tmp/('mapped-'+ident+'.bisa')
    mapper=Mapper(d.with_decls(block['body']),a['region'],a['desc'],runner.block('linkmap',ident)['body'])
    got=mapper.run(runner.isa,path);path.write_text(got)
    expected=runner.block('object',ident)['body']
    if got!=expected:
        import difflib
        diff='\n'.join(difflib.unified_diff(expected.splitlines(),got.splitlines(),'expected','map',lineterm=''))
        raise d.Fail(f'{ident} [§16] expected object text; actual map differs:\n'+diff)
    runner.isa.call('check',path)
    return got


def map_arena(runner):
    # Outline O1 from @copy1's load/add and the Cl old-value argument (TDL-5a).
    source=runner.block('example','tdl')['body'];m=d.Module(source)
    load=next(i for i in m.funcs['copy1'].instrs() if i.op=='load')
    add=next(i for i in m.funcs['copy1'].instrs() if i.op=='add')
    k=int(re.search(r'add i8 %v, (\d+)',add.text)[1])
    body='@cnt = internal global i8 0\n@other = internal global i8 0\ndefine i8 @O1(i8 %old) {\n '+load.text+'\n '+add.text+'\n %mask = xor i8 %old, '+add.res+'\n ret i8 %mask\n}\n'
    mapper=Mapper(body,'@O1','ARG(8);tgt=8','null_size=4096 heap_base=4096 heap_limit_max=0 stack max 32 A_tab=1',arena={'cnt':0,'other':1})
    path=runner.tmp/'mapped-arena-o1.bisa';got=mapper.run(runner.isa,path);path.write_text(got)
    equal('arena-o1','§16.4 hidden arena base map',runner.block('object','arena-o1')['body'],got)
    runner.isa.call('check',path);return got
