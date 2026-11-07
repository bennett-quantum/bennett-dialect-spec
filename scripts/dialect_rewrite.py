"""Dialect rewrite: shared definitions extracted without changing checker behavior."""
import re
from dialect_ir import (
    ABI_WITH_ALIGN, BINOPS, FBINOPS, FMF, Fail, INT_FLAGS, Instr, Module, N4_FN, N4_PARAM, Reject, UNSUPPORTED_FP, attr_name, match_close, parse_call, parse_type, split_top, strip_param_attrs, tsize, tstr
)
from dialect_analysis import (
    typed_val
)

def ren(r):
    return r[1:]


def fault_replace(f, ins, code):
    """F(C) of section 7.1: fault call + unreachable; rest of block deleted; phi entries removed."""
    for lab, blk in f.blocks:
        if ins in blk:
            k = blk.index(ins)
            for later in blk[k:]:
                later.deleted = True
            blk.insert(k, Instr(f"call void @__bennett_nz_fault(i64 {code})", None, "call", f, lab))
            blk.insert(k + 1, Instr("unreachable", None, "unreachable", f, lab))
            for _, b2 in f.blocks:
                for phi in b2:
                    if phi.op == "phi" and not phi.deleted and f"%{lab}" in phi.text:
                        raise Fail("checker: phi entry removal for F(C) not implemented")
            return
    raise Fail("fault_replace: instruction not found")


def replace_uses(f, old, new):
    pat = re.compile(re.escape(old) + r"(?![-\w.$])")
    for ins in f.instrs():
        if ins.res == old:
            continue
        body_l, sep, body_r = ins.text.partition(" = ") if ins.res else ("", "", ins.text)
        nb = pat.sub(new, body_r)
        ins.text = (body_l + sep + nb) if ins.res else nb


def normalise(text):
    """Apply section 7.2 to every defined function (examples: all are device functions)."""
    m = Module(text)
    lines = text.rstrip("\n").split("\n")
    appended = []

    def need_decl(decl):
        name = re.search(r"@([-\w.$]+)\(", decl).group(1)
        if name not in m.funcs and decl not in appended:
            appended.append(decl)

    deffs = [m.funcs[n] for k, n in m.order if k == "fn" and m.funcs[n].is_def]
    used_groups = set()
    for f in deffs:
        used_groups |= set(t for t in f.fn_attrs if t.startswith("#"))
    for f in deffs:
        for ins in f.instrs():
            # N1, N2
            if ins.op in BINOPS or ins.op in ("getelementptr", "zext", "icmp", "trunc", "uitofp") or ins.op in FBINOPS or ins.op == "fcmp":
                toks = ins.text.split(" ")
                ins.text = " ".join(t for t in toks if t not in INT_FLAGS and t not in FMF and not t.startswith("inrange"))
            # N3
            ins.text = re.sub(r",\s*!(?!dbg)[\w.]+\s+![\w.{}]+", "", ins.text)
            ins.text = re.sub(r",\s*!(?!dbg)[\w.]+\s+!\d+", "", ins.text)
            # N4 call sites
            if ins.op in ("call", "invoke"):
                ins.text = strip_n4(ins.text)
        # N4 on the definition header
        f.header = strip_n4_header(f.header)
    for g in used_groups:
        m.groups[g] = [t for t in m.groups.get(g, []) if attr_name(t) not in N4_FN]
    for f in deffs:
        for ins in list(f.instrs()):
            if ins.op == "call":
                c = parse_call(ins)
                if c["callee"].startswith("@llvm.assume") or re.match(r"@llvm\.(lifetime|invariant)\.", c["callee"]):
                    ins.deleted = True          # N5, N6
        # N7
        for ins in f.instrs():
            ins.text = n7(ins.text)
        # N8
        for ins in list(f.instrs()):
            if ins.op == "freeze":
                v = typed_val(ins.text.split(" = ", 1)[1][len("freeze"):])
                ins.deleted = True
                replace_uses(f, ins.res, v)
        # N10, N11, N12, N13
        for ins in list(f.instrs()):
            if ins.op == "call":
                c = parse_call(ins)
                cal = c["callee"]
                if cal.startswith("@llvm.is.constant"):
                    ins.deleted = True
                    replace_uses(f, ins.res, "false")
                elif cal.startswith("@llvm.objectsize"):
                    ins.deleted = True
                    replace_uses(f, ins.res, "-1" if c["args"][1][2] == "false" else "0")
                elif re.match(r"@llvm\.(trap|debugtrap|ubsantrap)", cal):
                    fault_replace(f, ins, 4)
                    need_decl("declare void @__bennett_nz_fault(i64)")
                elif re.match(r"@llvm\.memcpy", cal):
                    newname = re.sub(r"^@llvm\.memcpy(\.inline)?", "@llvm.memmove", cal)
                    ins.text = ins.text.replace(cal + "(", newname + "(", 1)
                    sig = re.search(r"llvm\.memmove\.(\S+)$", newname).group(1)
                    need_decl(f"declare void {newname}(ptr, ptr, {sig.split('.')[-1]}, i1 immarg)")
        # N14 shifts
        for lab, blk in f.blocks:
            k = 0
            while k < len(blk):
                ins = blk[k]
                if not ins.deleted and ins.op in ("shl", "lshr", "ashr"):
                    body = ins.text.split(" = ", 1)[1]
                    ty, j = parse_type(body.split(None, 1)[1])
                    if ty[0] != "int":
                        raise Fail("checker: vector shift not implemented")
                    w = ty[1]
                    a, b = split_top(body.split(None, 1)[1][j:])
                    if re.match(r"^-?\d+$", b):
                        if int(b) >= w:
                            ins.deleted = True
                            replace_uses(f, ins.res, "0")
                        k += 1
                        continue
                    r = ren(ins.res)
                    c1 = Instr(f"%nz.c.{r} = icmp uge i{w} {b}, {w}", f"%nz.c.{r}", "icmp", f, lab)
                    s1 = Instr(f"%nz.s.{r} = {ins.op} i{w} {a}, {b}", f"%nz.s.{r}", ins.op + "!", f, lab)
                    sel = Instr(f"{ins.res} = select i1 %nz.c.{r}, i{w} 0, i{w} %nz.s.{r}", ins.res, "select", f, lab)
                    blk[k:k + 1] = [c1, s1, sel]
                    k += 3
                    continue
                k += 1
        # N16 fmuladd
        for lab, blk in f.blocks:
            k = 0
            while k < len(blk):
                ins = blk[k]
                if not ins.deleted and ins.op == "call" and parse_call(ins)["callee"].startswith("@llvm.fmuladd"):
                    c = parse_call(ins)
                    t = tstr(c["ret"])
                    r = ren(ins.res)
                    a, b, cc = [x[2] for x in c["args"]]
                    blk[k:k + 1] = [Instr(f"%nz.m.{r} = fmul {t} {a}, {b}", f"%nz.m.{r}", "fmul", f, lab),
                                    Instr(f"{ins.res} = fadd {t} %nz.m.{r}, {cc}", ins.res, "fadd", f, lab)]
                    k += 2
                    continue
                k += 1
        # N19 soft-float
        for lab, blk in f.blocks:
            k = 0
            while k < len(blk):
                ins = blk[k]
                if not ins.deleted and ins.op in FBINOPS:
                    body = ins.text.split(" = ", 1)[1]
                    ty, j = parse_type(body.split(None, 1)[1])
                    if ty not in (("double",), ("float",)):
                        raise Fail("checker: soft-float type")
                    bw = 64 if ty == ("double",) else 32
                    sfx = "f64" if bw == 64 else "f32"
                    ops = split_top(body.split(None, 1)[1][j:])
                    r = ren(ins.res)
                    new = []
                    for oi, o in enumerate(ops):
                        new.append(Instr(f"%nz.{oi}.{r} = bitcast {tstr(ty)} {o.strip()} to i{bw}", f"%nz.{oi}.{r}", "bitcast", f, lab))
                    fn = f"__bennett_sf_{ins.op[1:]}_{sfx}"
                    new.append(Instr(f"%nz.i.{r} = call i{bw} @{fn}(i{bw} %nz.0.{r}, i{bw} %nz.1.{r})", f"%nz.i.{r}", "call", f, lab))
                    new.append(Instr(f"{ins.res} = bitcast i{bw} %nz.i.{r} to {tstr(ty)}", ins.res, "bitcast", f, lab))
                    need_decl(f"declare i{bw} @{fn}(i{bw}, i{bw})")
                    blk[k:k + 1] = new
                    k += len(new)
                    continue
                if not ins.deleted and ins.op in ("fcmp", "fptosi", "fptoui", "sitofp", "uitofp", "fpext", "fptrunc"):
                    raise Fail(f"checker: soft-float for {ins.op} not implemented")
                k += 1
        # N20 zero fill
        for lab, blk in f.blocks:
            k = 0
            while k < len(blk):
                ins = blk[k]
                if not ins.deleted and ins.op == "alloca":
                    body = ins.text.split(" = ", 1)[1]
                    parts = split_top(body[len("alloca"):].strip())
                    ty = parse_type(parts[0])[0]
                    cnt = 1
                    for p in parts[1:]:
                        if not p.startswith("align"):
                            v = typed_val(p)
                            if not re.match(r"^\d+$", v):
                                raise Fail("checker: dynamic alloca not implemented")
                            cnt = int(v)
                    size = tsize(ty) * cnt
                    blk.insert(k + 1, Instr(f"call void @llvm.memset.p0.i64(ptr {ins.res}, i8 0, i64 {size}, i1 false)", None, "call", f, lab))
                    need_decl("declare void @llvm.memset.p0.i64(ptr, i8, i64, i1 immarg)")
                    k += 2
                    continue
                k += 1
    return print_module(m, lines, appended)


def strip_attr_seq(s):
    """Remove N4 parameter attributes from a 'type attrs value' string."""
    ty, k = parse_type(s)
    attrs, rest = strip_param_attrs(s[k:])
    keep_align = any(attr_name(a) in ABI_WITH_ALIGN for a in attrs)
    attrs = [a for a in attrs if attr_name(a) not in N4_PARAM or (attr_name(a) == "align" and keep_align)]
    return " ".join([s[:k].strip()] + attrs + ([rest.strip()] if rest.strip() else []))


def strip_n4(text):
    head, sep, body = text.partition(" = ")
    if not sep:
        head, body = "", text
    m = re.match(r"^((?:tail |musttail |notail )?(?:call|invoke) )(.*)$", body)
    pre, rest = m.group(1), m.group(2)
    cm = re.search(r"[@%][-\w.$]+\(", rest)
    rpre = rest[:cm.start()]
    attrs, ty = strip_param_attrs(rpre)
    attrs = [a for a in attrs if attr_name(a) not in N4_PARAM]
    aend = match_close(rest, cm.end() - 1)
    args = [strip_attr_seq(a) for a in split_top(rest[cm.end():aend - 1])]
    post = rest[aend:]
    post = " ".join(t for t in post.split(" ") if attr_name(t) not in N4_FN) if post.strip() else post
    out = pre + " ".join(attrs + [ty.strip()]) + " " + cm.group(0) + ", ".join(args) + ")" + (" " + post.strip() if post.strip() else "")
    return (head + sep + out) if sep else out


def strip_n4_header(h):
    m = re.search(r"@([-\w.$]+)\(", h)
    pend = match_close(h, m.end() - 1)
    params = [strip_attr_seq(p) for p in split_top(h[m.end():pend - 1])]
    pre = h[:m.start()]
    toks = pre.split()
    keep = []
    for t in toks:
        if attr_name(t) in N4_PARAM:
            continue
        keep.append(t)
    return " ".join(keep) + " " + m.group(0) + ", ".join(params) + ")" + h[pend:]


def n7(t):
    t = re.sub(r"(<\d+ x [^>]+>) (undef|poison)\b", r"\1 zeroinitializer", t)
    t = re.sub(r"\b(ptr) (undef|poison)\b", r"\1 null", t)
    t = re.sub(r"\b(double|float) (undef|poison)\b", r"\1 0.000000e+00", t)
    t = re.sub(r"\b(i\d+) (undef|poison)\b", r"\1 0", t)
    if re.search(r"\b(undef|poison)\b", t):
        raise Fail(f"checker: N7 case not implemented: {t}")
    return t


def print_module(m, orig_lines, appended):
    out = []
    i = 0
    for ln in orig_lines:
        pass
    # rebuild: walk original lines; replace function bodies and attribute groups
    lines = orig_lines
    k = 0
    while k < len(lines):
        st = lines[k].strip()
        if st.startswith("define "):
            name = re.search(r"@([-\w.$]+)\(", st).group(1)
            f = m.funcs[name]
            out.append(f.header)
            for bi, (lab, blk) in enumerate(f.blocks):
                if lab != "<entry>" and (bi > 0 or re.search(r"^\s*" + re.escape(lab) + ":", "\n".join(lines[k + 1:k + 3]), re.M)):
                    if bi > 0:
                        out.append("")
                    out.append(f"{lab}:")
                for ins in blk:
                    if not ins.deleted:
                        out.append("  " + ins.text)
            out.append("}")
            while lines[k].strip() != "}":
                k += 1
            k += 1
            continue
        if st.startswith("attributes #"):
            g = re.match(r"attributes (#\d+)", st).group(1)
            toks = m.groups[g]
            out.append(f"attributes {g} = {{ {' '.join(toks)} }}" if toks else f"attributes {g} = {{ }}")
            k += 1
            continue
        out.append(lines[k])
        k += 1
    for d in appended:
        out.append("")
        out.append(d)
    return "\n".join(out) + "\n"


def validate(text):
    m = Module(text)
    for f in [m.funcs[n] for k, n in m.order if k == "fn" and m.funcs[n].is_def]:
        for ins in f.instrs():
            toks = set(ins.text.replace(",", " ").split())
            if ins.op not in ("call", "invoke") and (toks & INT_FLAGS or toks & FMF):
                raise Reject("BD-E-RESIDUAL", f"V1: {ins.text}")
            if re.search(r",\s*!(?!dbg)[\w.]+\s+!", ins.text):
                raise Reject("BD-E-RESIDUAL", f"V2: {ins.text}")
            if re.search(r"\b(undef|poison)\b", ins.text):
                raise Reject("BD-E-RESIDUAL", f"V5: {ins.text}")
            if ins.op in ("freeze", "fence", "atomicrmw", "cmpxchg") or " atomic " in ins.text or " volatile " in ins.text:
                raise Reject("BD-E-RESIDUAL", f"V6: {ins.text}")
            if ins.op in FBINOPS or ins.op in ("fcmp", "fptosi", "fptoui", "sitofp", "uitofp", "fpext", "fptrunc"):
                raise Reject("BD-E-RESIDUAL", f"V9: {ins.text}")
            if ins.op in ("call", "invoke"):
                c = parse_call(ins)
                if re.match(r"@llvm\.(assume|lifetime|invariant|is\.constant|objectsize|trap|debugtrap|ubsantrap|memcpy|fmuladd)", c["callee"]):
                    raise Reject("BD-E-RESIDUAL", f"V4: {ins.text}")
                for a in c["ret_attrs"] + [x for arg in c["args"] for x in arg[1]]:
                    if attr_name(a) in N4_PARAM:
                        raise Reject("BD-E-RESIDUAL", f"V3: {ins.text}")
            if any(t in UNSUPPORTED_FP for t in re.findall(r"\b\w+\b", ins.text)):
                raise Reject("BD-E-RESIDUAL", f"V10: {ins.text}")
        for p in f.params:
            for a in p[1]:
                if attr_name(a) in N4_PARAM:
                    raise Reject("BD-E-RESIDUAL", f"V3: {f.name} param {a}")
        for t in m.fn_attr_names(f.fn_attrs):
            if attr_name(t) in N4_FN:
                raise Reject("BD-E-RESIDUAL", f"V3: {f.name} {t}")
        # V7 shifts, V11 allocas
        d = {i.res: i for i in f.instrs() if i.res}
        allins = list(f.instrs())
        for idx, ins in enumerate(allins):
            if ins.op in ("shl", "lshr", "ashr"):
                body = ins.text.split(" = ", 1)[1]
                ty, j = parse_type(body.split(None, 1)[1])
                a, b = split_top(body.split(None, 1)[1][j:])
                if re.match(r"^\d+$", b) and int(b) < ty[1]:
                    continue
                uses = [u for u in allins if u is not ins and re.search(re.escape(ins.res) + r"(?![-\w.$])", u.text)]
                ok = len(uses) == 1 and uses[0].op == "select"
                if ok:
                    sp = split_top(uses[0].text.split(" = ", 1)[1][len("select"):].strip())
                    cond, tv, fv = typed_val(sp[0]), typed_val(sp[1]), typed_val(sp[2])
                    ci = d.get(cond)
                    ok = fv == ins.res and tv == "0" and ci is not None and ci.op == "icmp" and \
                        re.match(r"icmp uge i\d+ " + re.escape(b) + r", " + str(ty[1]) + "$", ci.text.split(" = ", 1)[1]) is not None
                if not ok:
                    raise Reject("BD-E-RESIDUAL", f"V7: {ins.text}")
            if ins.op == "alloca":
                nxt = allins[idx + 1] if idx + 1 < len(allins) else None
                if not (nxt and nxt.op == "call" and parse_call(nxt)["callee"].startswith("@llvm.memset")
                        and parse_call(nxt)["args"][0][2] == ins.res):
                    raise Reject("BD-E-RESIDUAL", f"V11: {ins.text}")
    return "accept"

