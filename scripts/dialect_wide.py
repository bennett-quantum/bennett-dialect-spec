"""N22 re-legalisation of N27/N32 products; limb-slot boundary emitters."""
import re
import dialect_check as d
from dialect_normalise import FP


def extra(nz,f,i,r,w,widths,parts):
    b=i.text.split(' = ',1)[-1];n=len(widths)
    def slot(tag,values=None):
        p=f'%nz.{tag}.{r}';out=[f'{p} = call ptr @__bennett_rt_ss_push(i64 {8*n}, i64 8)']
        nz.decl('__bennett_rt_ss_push','ptr',['i64','i64']);nz.decl('__bennett_rt_ss_pop','void',['ptr'])
        if values is not None:
            for k,(v,lw) in enumerate(zip(values,widths)):
                q=f'%nz.{tag}{k}.{r}';out += [f'{q} = getelementptr i64, ptr {p}, i64 {k}',f'store i{lw} {v}, ptr {q}, align 8']
        return p,out
    def load(p):
        out=[];vals=[]
        for k,lw in enumerate(widths):
            q=f'%nz.rp{k}.{r}';v=f'%nz.rm{k}.{r}';vals.append(v)
            out += [f'{q} = getelementptr i64, ptr {p}, i64 {k}',f'{v} = load i{lw}, ptr {q}, align 8']
        nz.limbs[i.res]=vals;return out
    def pop(p):return f'call void @__bennett_rt_ss_pop(ptr {p})'
    if i.op in ('sitofp','uitofp','fptosi','fptoui'):
        src,dst=b[len(i.op):].rsplit(' to ',1);st,j=d.parse_type(src);value=src[j:].strip();dst=dst.strip()
        if i.op in ('sitofp','uitofp'):
            suffix,bw=FP[dst];p,out=slot('s',parts(value));name=f'__bennett_sf_{i.op}_{suffix}_wide'
            nz.decl(name,f'i{bw}',['ptr','i32'])
            return out+[f'%nz.i.{r} = call i{bw} @{name}(ptr {p}, i32 {w})',pop(p),f'{i.res} = bitcast i{bw} %nz.i.{r} to {dst}']
        suffix,bw=FP[d.tstr(st)];p,out=slot('d');name=f'__bennett_sf_{i.op}_{suffix}_wide'
        nz.decl(name,'void',['ptr',f'i{bw}','i32'])
        return [f'%nz.0.{r} = bitcast {d.tstr(st)} {value} to i{bw}']+out+[f'call void @{name}(ptr {p}, i{bw} %nz.0.{r}, i32 {w})']+load(p)+[pop(p)]
    if i.op=='call':
        c=d.parse_call(i)
        conversion=re.match(r'@llvm\.(fptosi|fptoui)\.sat\.',c['callee'])
        if conversion:
            op=conversion[1];ty=d.tstr(c['args'][0][0]);value=c['args'][0][2]
            synthetic=d.Instr(f'{i.res} = {op} {ty} {value} to i{w}',i.res,op,f,i.block)
            return extra(nz,f,synthetic,r,w,widths,parts)
        m=re.fullmatch(r'@__bennett_rt_(ctpop|ctlz|cttz|bswap|bitreverse|fshl|fshr)_i(\d+)',c['callee'])
        if m:
            op=m[1];p,out=slot('d');slots=[];types=[];args=[]
            for k,(ty,_,val) in enumerate(c['args']):
                if ty[0]=='int' and ty[1]>128:
                    q,lines=slot('s'+str(k),parts(val));out+=lines;slots.append(q);types.append('ptr');args.append('ptr '+q)
                else:types.append(d.tstr(ty));args.append(d.tstr(ty)+' '+val)
            name=f'__bennett_rt_i{w}_{op}';nz.decl(name,'void',['ptr']+types)
            out += [f'call void @{name}(ptr {p}, '+', '.join(args)+')']+load(p)
            return out+[pop(q) for q in reversed([p]+slots)]
    if i.op in ('insertvalue','extractvalue'):
        if not hasattr(nz,'aggregates'):nz.aggregates={}
        ps=d.split_top(b[len(i.op):].strip());base=d.typed_val(ps[0]);key=(f.name,base)
        if i.op=='insertvalue':
            agg=dict(nz.aggregates.get(key,{}));idx=int(ps[2]);ty=d.parse_type(ps[1])[0];v=d.typed_val(ps[1])
            agg[idx]=parts(v) if ty[0]=='int' and ty[1]>128 else v;nz.aggregates[f.name,i.res]=agg;return []
        value=nz.aggregates[key][int(ps[1])]
        if isinstance(value,list):nz.limbs[i.res]=value
        else:nz.replace(f,i.res,value)
        return []
    if i.op in ('and','or','xor'):
        a,z=d.split_top(b.split(None,2)[2]);aa,zz=parts(a),parts(z)
        nz.limbs[i.res]=[f'%nz.m{k}.{r}' for k in range(n)]
        return [f'%nz.m{k}.{r} = {i.op} i{lw} {aa[k]}, {zz[k]}' for k,lw in enumerate(widths)]
    if i.op=='select':
        ps=d.split_top(b[6:].strip());cond=d.typed_val(ps[0]);a,z=parts(d.typed_val(ps[1])),parts(d.typed_val(ps[2]))
        nz.limbs[i.res]=[f'%nz.m{k}.{r}' for k in range(n)]
        return [f'%nz.m{k}.{r} = select i1 {cond}, i{lw} {a[k]}, i{lw} {z[k]}' for k,lw in enumerate(widths)]
    if i.op=='icmp':
        _,pred,rest=b.split(None,2);ty,j=d.parse_type(rest);aa,zz=[parts(x) for x in d.split_top(rest[j:])];out=[]
        previous='true' if pred in ('eq','ule','uge','sle','sge') else 'false'
        for k,lw in enumerate(widths):
            eq=f'%nz.eq{k}.{r}';cmp=f'%nz.cmp{k}.{r}';q=i.res if k==n-1 else f'%nz.c{k}.{r}'
            out.append(f'{eq} = icmp eq i{lw} {aa[k]}, {zz[k]}')
            if pred in ('eq','ne'):out.append(f'{q} = '+('and' if pred=='eq' else 'or')+f' i1 {previous}, '+(eq if pred=='eq' else f'%nz.ne{k}.{r}'))
            else:
                strict=pred[0]+('lt' if pred.endswith(('lt','le')) else 'gt')
                if k<n-1:strict='u'+strict[1:]
                out += [f'{cmp} = icmp {strict} i{lw} {aa[k]}, {zz[k]}',f'{q} = select i1 {eq}, i1 {previous}, i1 {cmp}']
            if pred=='ne':out.insert(-1,f'%nz.ne{k}.{r} = xor i1 {eq}, true')
            previous=q
        return out
    if i.op=='trunc':
        src,dst=b[5:].rsplit(' to ',1);sw=d.parse_type(src)[0][1];dw=int(dst.strip()[1:]);source=parts(d.typed_val(src))
        if dw<=64:
            if dw==64:nz.replace(f,i.res,source[0]);return []
            return [f'{i.res} = trunc i64 {source[0]} to i{dw}']
        raise d.Fail('N22 truncation needs destination limb assembly')
    return None
