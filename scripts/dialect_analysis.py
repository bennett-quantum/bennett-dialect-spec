"""Dialect analysis: shared definitions extracted without changing checker behavior."""
import re
from dialect_ir import (
    BINOPS, ENV_OP, FBINOPS, FMF, FORBIDDEN_LIE, Fail, HANDLE_OPS, HEAP_FNS, INT_CAND_OPS, INT_FLAGS, Instr, MARKERS, OPCODES, PERMITTED_FN, PERMITTED_PARAM, PERMITTED_RET, REGION_OPS, Reject, attr_name, fnstr, is_marker, parse_call, parse_type, split_top, strip_param_attrs, talign, tsize, tstr
)

class Analysis:
    def __init__(self, mod, materialised=False):
        self.m = mod
        self.materialised = materialised
        self.pw = 64
        self.cands = {}          # (instr id, opidx) -> set or 'TOP'
        self.sources = {}

    # ----------------------------------------------------------- S1
    def s1(self):
        m = self.m
        # rule 1: marker defined
        for kind, name in m.order:
            if kind == "fn" and m.funcs[name].is_def and is_marker(name):
                raise Reject("BD-E-MARKER-DEFINED", name)
        # rule 2: unknown __bennett_ names
        for kind, name in m.order:
            if name.startswith("__bennett_") and not is_marker(name):
                if self.materialised and (name.startswith("__bennett_nz_") or name.startswith("__bennett_sf_")):
                    continue
                raise Reject("BD-E-MARKER-UNKNOWN", name)
        for f in self.funcs():
            for ins in f.instrs():
                for nm in re.findall(r"@(__bennett_[\w.$]+)", ins.text):
                    if not is_marker(nm) and not (self.materialised and re.match(r"__bennett_(nz|sf)_", nm)):
                        raise Reject("BD-E-MARKER-UNKNOWN", nm)
        # rule 3: marker address
        for g in m.globals.values():
            for nm in re.findall(r"@(__bennett_[\w.$]+)", g["text"].split("=", 1)[1]):
                if is_marker(nm):
                    raise Reject("BD-E-MARKER-ADDRESS", g["text"])
        for f in self.funcs():
            for ins in f.instrs():
                refs = re.findall(r"@(__bennett_[\w.$]+)", ins.text)
                if not refs:
                    continue
                callee = None
                if ins.op in ("call", "invoke"):
                    callee = parse_call(ins)["callee"]
                for nm in refs:
                    if is_marker(nm) and ("@" + nm) != callee:
                        raise Reject("BD-E-MARKER-ADDRESS", ins.text)
                    if is_marker(nm) and ins.text.count("@" + nm) > 1:
                        raise Reject("BD-E-MARKER-ADDRESS", ins.text)
        # recognition (3.5)
        for f in self.funcs():
            for ins in f.instrs():
                if ins.op not in ("call", "invoke"):
                    continue
                c = parse_call(ins)
                nm = c["callee"][1:]
                if c["callee"].startswith("@") and is_marker(nm):
                    self.check_signature(ins, c, nm[len("__bennett_"):])
        # attributes (3.6)
        for name, fn in m.funcs.items():
            if is_marker(name) and not fn.is_def:
                self.check_decl_attrs(fn)
        for f in self.funcs():
            for ins in f.instrs():
                if ins.op in ("call", "invoke"):
                    c = parse_call(ins)
                    if c["callee"].startswith("@") and is_marker(c["callee"][1:]):
                        self.check_call_attrs(ins, c)
        # Julia (3.8)
        for name, g in m.globals.items():
            jl = re.match(r"jlplt___bennett_(\w+?)_\d+_got$", name)
            fname = [t for a in g["attrs"] for t in m.groups.get(a, []) if t.startswith('"julia.fname"="__bennett_')]
            if jl or fname:
                raise Reject("BD-E-JULIA-CCALL", name)
        # invoke rewrite (3.7)
        for f in self.funcs():
            changed = False
            for ins in list(f.instrs()):
                if ins.op == "invoke":
                    c = parse_call(ins)
                    if c["callee"].startswith("@") and is_marker(c["callee"][1:]):
                        body = ins.text.split(" = ", 1)[1] if ins.res else ins.text
                        newcall = re.sub(r"^invoke ", "call ", body)
                        newcall = re.sub(r"\s*to label .*$", "", newcall)
                        ins.text = (ins.res + " = " if ins.res else "") + newcall
                        ins.op = "call"
                        normal = c["unwind"][0]
                        blk = [b for b in f.blocks if b[0] == ins.block][0][1]
                        k = blk.index(ins)
                        blk.insert(k + 1, Instr(f"br label {normal}", None, "br", f, ins.block))
                        changed = True
            if changed:
                self.delete_unreachable(f)
        # effect lies (3.8)
        reach = self.reaches_marker()
        for f in self.funcs():
            names = set(attr_name(t) for t in m.fn_attr_names(f.fn_attrs))
            lie = names & FORBIDDEN_LIE
            for t in m.fn_attr_names(f.fn_attrs):
                if t.startswith("memory(") and "write" not in t and "readwrite" not in t:
                    lie.add("memory")
            if lie and f.name in reach:
                raise Reject("BD-E-EFFECT-LIE", f"{f.name}: {sorted(lie)}")

    def funcs(self):
        return [self.m.funcs[n] for k, n in self.m.order if k == "fn" and self.m.funcs[n].is_def]

    def check_signature(self, ins, c, nm):
        mk = MARKERS["__bennett_" + nm]
        decl = self.m.funcs["__bennett_" + nm]
        want = mk.ftype()
        unproto = decl.ret == mk.ret and not decl.params and decl.vararg
        if decl.ftype() != want and not unproto:
            raise Reject("BD-E-MARKER-SIGNATURE", f"declaration {decl.ftype()} != {want}")
        got = fnstr(c["ret"], c["params"], c["vararg"])
        ok = got == want or (unproto and got == fnstr(mk.ret, [p[0] for p in mk.params], True))
        if not ok:
            raise Reject("BD-E-MARKER-SIGNATURE", f"call type {got} != {want}: {ins.text}")
        if len(c["args"]) != len(mk.params):
            raise Reject("BD-E-MARKER-SIGNATURE", f"argument count: {ins.text}")
        if [tstr(a[0]) for a in c["args"]] != [tstr(p[0]) for p in mk.params]:
            raise Reject("BD-E-MARKER-SIGNATURE", f"argument types: {ins.text}")
        if (c["cc"] and c["cc"] != "ccc") or c["bundles"]:
            raise Reject("BD-E-MARKER-SIGNATURE", f"calling convention or bundles: {ins.text}")

    def check_fn_attr_list(self, toks, where):
        for t in self.m.fn_attr_names(toks):
            n = attr_name(t)
            if n == "<string>" or n in PERMITTED_FN:
                continue
            raise Reject("BD-E-MARKER-ATTRIBUTE", f"{where}: {t}")

    def check_decl_attrs(self, fn):
        if fn.linkage == "extern_weak" or (fn.cc and fn.cc != "ccc"):
            raise Reject("BD-E-MARKER-ATTRIBUTE", f"{fn.name}: linkage/cc")
        self.check_fn_attr_list(fn.fn_attrs, fn.name)
        for a in fn.ret_attrs:
            if attr_name(a) not in PERMITTED_RET:
                raise Reject("BD-E-MARKER-ATTRIBUTE", f"{fn.name} return: {a}")
        for p in fn.params:
            for a in p[1]:
                if attr_name(a) not in PERMITTED_PARAM:
                    raise Reject("BD-E-MARKER-ATTRIBUTE", f"{fn.name} param: {a}")

    def check_call_attrs(self, ins, c):
        if c["tail"] == "musttail":
            raise Reject("BD-E-MARKER-ATTRIBUTE", ins.text)
        self.check_fn_attr_list(c["fn_attrs"], ins.text)
        for a in c["ret_attrs"]:
            if attr_name(a) not in PERMITTED_RET:
                raise Reject("BD-E-MARKER-ATTRIBUTE", f"{ins.text}: {a}")
        for ty, attrs, _ in c["args"]:
            for a in attrs:
                if attr_name(a) not in PERMITTED_PARAM:
                    raise Reject("BD-E-MARKER-ATTRIBUTE", f"{ins.text}: {a}")

    def delete_unreachable(self, f):
        succ = {}
        for lab, ins in f.blocks:
            s = []
            for i in ins:
                if i.deleted:
                    continue
                s += re.findall(r"label %([-\w.$]+)", i.text)
            succ[lab] = s
        seen, stack = set(), [f.blocks[0][0]]
        while stack:
            b = stack.pop()
            if b in seen:
                continue
            seen.add(b)
            stack += succ.get(b, [])
        f.blocks = [(l, i) for l, i in f.blocks if l in seen]

    # direct-call graph
    def direct_callees(self, f):
        out = []
        for ins in f.instrs():
            if ins.op in ("call", "invoke"):
                c = parse_call(ins)
                if c["callee"].startswith("@"):
                    n = self.m.resolve_alias(c["callee"][1:])
                    if self.m.defined(n):
                        out.append(n)
        return out

    def marker_calls(self, f):
        for ins in f.instrs():
            if ins.op in ("call", "invoke"):
                c = parse_call(ins)
                if c["callee"].startswith("@") and is_marker(c["callee"][1:]):
                    yield ins, c, c["callee"][len("@__bennett_"):]

    def reaches_marker(self):
        has = {f.name for f in self.funcs() if any(True for _ in self.marker_calls(f))}
        changed = True
        while changed:
            changed = False
            for f in self.funcs():
                if f.name in has:
                    continue
                if any(c in has for c in self.direct_callees(f)) or any(
                        r in has for r in self.region_edges(f)):
                    has.add(f.name)
                    changed = True
        return has

    def region_edges(self, f):
        out = []
        for ins, c, mk in self.marker_calls(f):
            for k in REGION_OPS.get(mk, {}):
                cs = self.cands.get((id(ins), k))
                if isinstance(cs, set):
                    out += list(cs)
        return out

    # ----------------------------------------------------------- values
    def defs(self, f):
        d = {}
        for ins in f.instrs():
            if ins.res:
                d[ins.res] = ins
        return d

    def address_taken(self, fname):
        """Function address used other than as a direct callee or a region-operand source."""
        pat = re.compile(r"@" + re.escape(fname) + r"(?![-\w.$])")
        for g in self.m.globals.values():
            if pat.search(g["text"].split("=", 1)[1]):
                return True
        for a, tgt in self.m.aliases.items():
            if tgt == fname and self.address_taken(a):
                return True
        for f in self.funcs():
            for ins in f.instrs():
                if not pat.search(ins.text):
                    continue
                if ins.op in ("call", "invoke"):
                    c = parse_call(ins)
                    if c["callee"] == "@" + fname:
                        if not any(pat.search(a[2]) for a in c["args"]):
                            continue
                    nm = c["callee"][len("@__bennett_"):] if c["callee"].startswith("@__bennett_") else None
                    if nm in REGION_OPS and all(not pat.search(a[2]) or k in REGION_OPS[nm] for k, a in enumerate(c["args"])):
                        continue
                    return True
                if ins.op in ("select", "phi", "store"):
                    if ins.op == "store":
                        val = split_top(ins.text.split("store ", 1)[1])[0]
                        if pat.search(val):
                            continue  # stored into a slot: tracked by C3
                        return True
                    continue
                return True
        return False

    def nonlocal_linkage(self, fname):
        return self.m.funcs[fname].linkage not in ("internal", "private")

    # ----------------------------------------------------------- bases (5.2)
    def compute_bases(self):
        """base[(fname, value)] -> set of (obj, off) or 'TOP'."""
        self.base = {}
        changed = True
        it = 0
        while changed:
            it += 1
            if it > 50:
                raise Fail("base fixpoint did not converge")
            changed = False
            for f in self.funcs():
                for idx, (ty, attrs, name) in enumerate(f.params):
                    if ty != ("ptr",) or not name:
                        continue
                    b = self.param_base(f, idx)
                    if self.base.get((f.name, name)) != b:
                        self.base[(f.name, name)] = b
                        changed = True
                for ins in f.instrs():
                    if ins.res:
                        b = self.value_base_of_instr(f, ins)
                        if b is not None and self.base.get((f.name, ins.res)) != b:
                            self.base[(f.name, ins.res)] = b
                            changed = True

    def param_base(self, f, idx):
        out = set()
        for g in self.funcs():
            for ins in g.instrs():
                if ins.op in ("call", "invoke"):
                    c = parse_call(ins)
                    if c["callee"].startswith("@") and self.m.resolve_alias(c["callee"][1:]) == f.name:
                        if idx < len(c["args"]):
                            b = self.vbase(g, c["args"][idx][2])
                            if b == "TOP":
                                return "TOP"
                            out |= b
                    nm = c["callee"][len("@__bennett_"):] if c["callee"].startswith("@__bennett_") else None
                    if nm in ENV_OP and idx == 0:
                        for k in REGION_OPS[nm]:
                            cs = self.cands.get((id(ins), k))
                            if isinstance(cs, set) and f.name in cs:
                                b = self.vbase(g, c["args"][ENV_OP[nm]][2])
                                if b == "TOP":
                                    return "TOP"
                                out |= b
        if self.nonlocal_linkage(f.name) or self.address_taken(f.name):
            out.add(("EXT", "*"))
        return frozenset(out)

    def vbase(self, f, v):
        v = v.strip()
        if v.startswith("@"):
            n = v[1:]
            if n in self.m.globals:
                return frozenset({(n, 0)})
            return "TOP"
        if v.startswith("%"):
            return self.base.get((f.name, v), frozenset())
        if v.startswith("getelementptr"):
            return "TOP"
        return "TOP"

    def value_base_of_instr(self, f, ins):
        body = ins.text.split(" = ", 1)[1]
        op = ins.op
        if op == "alloca":
            return frozenset({(f"{f.name}{ins.res}", 0)})
        if op in ("call", "invoke"):
            c = parse_call(ins)
            if c["ret"] != ("ptr",):
                return None
            if c["callee"][1:] in HEAP_FNS:
                return frozenset({(f"{f.name}{ins.res}", 0)})
            return "TOP"
        if op == "getelementptr":
            rest = re.sub(r"^getelementptr\s+((inbounds|nusw|nuw|inrange\(\S+\))\s+)*", "", body)
            parts = split_top(rest)
            srcty = parse_type(parts[0])[0]
            ty, k = parse_type(parts[1])
            b = self.vbase(f, parts[1][k:].strip())
            if b == "TOP":
                return "TOP"
            idxs = []
            for p in parts[2:]:
                ity, kk = parse_type(p)
                val = p[kk:].strip()
                idxs.append(int(val) if re.match(r"^-?\d+$", val) else None)
            if any(i is None for i in idxs):
                return frozenset((o, "*") for (o, _) in b)
            d = gep_offset(srcty, idxs)
            return frozenset((o, "*" if off == "*" else off + d) for (o, off) in b)
        if op in ("phi", "select"):
            ty = self.result_type(ins)
            if ty != ("ptr",):
                return None
            vals = self.value_operands(ins)
            out = set()
            for v in vals:
                b = self.vbase(f, v)
                if b == "TOP":
                    return "TOP"
                out |= b
            return frozenset(out)
        if self.result_type(ins) == ("ptr",):
            return "TOP"
        return None

    def result_type(self, ins):
        body = ins.text.split(" = ", 1)[1]
        op = ins.op
        if op == "phi":
            return parse_type(body[4:])[0]
        if op == "select":
            parts = split_top(body[len("select"):].strip())
            return parse_type(parts[1])[0]
        if op in ("load",):
            rest = re.sub(r"^load\s+(atomic\s+)?(volatile\s+)?", "", body)
            return parse_type(rest)[0]
        if op in ("inttoptr", "getelementptr", "alloca"):
            return ("ptr",)
        if op in ("call", "invoke"):
            return parse_call(ins)["ret"]
        if op in ("ptrtoint", "zext", "sext", "trunc", "bitcast", "fptosi", "fptoui", "sitofp", "uitofp", "fpext", "fptrunc"):
            return parse_type(body.rsplit(" to ", 1)[1])[0]
        if op == "icmp" or op == "fcmp":
            return ("int", 1)
        if op in BINOPS or op in ("freeze", "fneg") or op in FBINOPS:
            rest = strip_flags(body.split(None, 1)[1])
            return parse_type(rest)[0]
        if op == "extractelement":
            return parse_type(body.split(None, 1)[1])[0][2]
        if op in ("insertelement", "shufflevector"):
            return parse_type(body.split(None, 1)[1])[0]
        return None

    def value_operands(self, ins):
        body = ins.text.split(" = ", 1)[1] if ins.res else ins.text
        if ins.op == "phi":
            ty, k = parse_type(body[4:])
            return [split_top(p.strip()[1:-1])[0] for p in split_top(body[4 + k:])]
        if ins.op == "select":
            parts = split_top(body[len("select"):].strip())
            return [typed_val(parts[1]), typed_val(parts[2])]
        raise Fail("value_operands")

    # ----------------------------------------------------------- S2: candidates (6.2)
    def resolve(self, name, seen=None):
        name = self.m.resolve_alias(name)
        seen = seen or set()
        if name in seen:
            raise Reject("BD-E-REGION-THUNK", name)
        seen.add(name)
        f = self.m.funcs.get(name)
        if f and f.is_def:
            ins = list(f.instrs())
            if len(f.blocks) == 1 and len(ins) == 2 and ins[0].op == "call" and ins[1].op == "ret":
                c = parse_call(ins[0])
                pnames = [p[2] for p in f.params]
                if (c["callee"].startswith("@") and [a[2] for a in c["args"]] == pnames and not c["bundles"]
                        and (c["cc"] in (None, "ccc"))):
                    g = self.m.resolve_alias(c["callee"][1:])
                    if g in self.m.funcs and self.m.funcs[g].ftype() == f.ftype():
                        r = ins[1].text.split()
                        if (r == ["ret", "void"] and f.ret == ("void",)) or (len(r) == 3 and r[2] == ins[0].res):
                            return self.resolve(g, seen)
        return name

    def rr(self, f, v, depth=0):
        """Candidate set (set of names) or 'TOP'; also source set."""
        if depth > 40:
            raise Fail("rr depth")
        v = v.strip()
        if v.startswith("@"):
            n = v[1:]
            if n in self.m.funcs or n in self.m.aliases:
                return {n}
            return "TOP"
        if not v.startswith("%"):
            return "TOP"
        # parameter?
        for idx, (ty, at, name) in enumerate(f.params):
            if name == v:
                if self.nonlocal_linkage(f.name) or self.address_taken(f.name):
                    return "TOP"
                out = set()
                for g in self.funcs():
                    for ins in g.instrs():
                        if ins.op in ("call", "invoke"):
                            c = parse_call(ins)
                            if c["callee"].startswith("@") and self.m.resolve_alias(c["callee"][1:]) == f.name:
                                r = self.rr(g, c["args"][idx][2], depth + 1)
                                if r == "TOP":
                                    return "TOP"
                                out |= r
                return out
        d = self.defs(f)
        ins = d.get(v)
        if ins is None:
            return "TOP"
        if ins.op in ("select", "phi"):
            out = set()
            for x in self.value_operands(ins):
                r = self.rr(f, x, depth + 1)
                if r == "TOP":
                    return "TOP"
                out |= r
            return out
        if ins.op == "load":
            body = ins.text.split(" = ", 1)[1]
            rest = re.sub(r"^load\s+(atomic\s+)?(volatile\s+)?", "", body)
            parts = split_top(rest)
            p = typed_val(parts[1])
            b = self.vbase(f, p)
            if b == "TOP":
                return "TOP"
            out = set()
            for (obj, off) in b:
                if obj == "EXT" or obj not in self.m.globals and not self.is_alloca_obj(obj):
                    return "TOP"
                if obj in self.m.globals:
                    g = self.m.globals[obj]
                    out |= set(fn_consts_at(g, off, self.m))
                    if g["constant"]:
                        continue
                if self.obj_escapes(obj):
                    return "TOP"
                for g2 in self.funcs():
                    for st in g2.instrs():
                        if st.op != "store":
                            continue
                        val, ptr = store_parts(st)
                        sb = self.vbase(g2, ptr)
                        if sb == "TOP":
                            continue
                        for (o2, off2) in sb:
                            if o2 == obj and (off2 == off or "*" in (off, off2)):
                                r = self.rr(g2, val, depth + 1)
                                if r == "TOP":
                                    return "TOP"
                                out |= r
            return out
        if ins.op in ("call", "invoke"):
            c = parse_call(ins)
            if c["callee"].startswith("@") and self.m.defined(self.m.resolve_alias(c["callee"][1:])):
                g = self.m.funcs[self.m.resolve_alias(c["callee"][1:])]
                out = set()
                for r_ins in g.instrs():
                    if r_ins.op == "ret":
                        r = self.rr(g, typed_val(r_ins.text[4:]), depth + 1)
                        if r == "TOP":
                            return "TOP"
                        out |= r
                return out
        return "TOP"

    def is_alloca_obj(self, obj):
        return isinstance(obj, str) and "%" in obj

    def obj_escapes(self, obj):
        """C3: address used other than as load/store pointer, gep base, phi/select, direct call arg to a device fn."""
        if obj in self.m.globals:
            pat = re.compile(r"@" + re.escape(obj) + r"(?![-\w.$])")
            for f in self.funcs():
                for ins in f.instrs():
                    if pat.search(ins.text) and ins.op not in ("load", "store", "getelementptr", "phi", "select", "call"):
                        return True
                    if ins.op in ("call", "invoke") and pat.search(ins.text):
                        c = parse_call(ins)
                        if c["callee"].startswith("@llvm.mem"):
                            return True
                    if ins.op == "store" and pat.search(store_parts(ins)[0]):
                        return True
            return False
        fname, res = obj.split("%", 1)
        f = self.m.funcs[fname]
        res = "%" + res
        pat = re.compile(re.escape(res) + r"(?![-\w.$])")
        for ins in f.instrs():
            if ins.res == res:
                continue
            if not pat.search(ins.text):
                continue
            if ins.op in ("load", "getelementptr", "phi", "select"):
                continue
            if ins.op == "store":
                if pat.search(store_parts(ins)[0]):
                    return True
                continue
            if ins.op in ("call", "invoke"):
                c = parse_call(ins)
                if c["callee"].startswith("@llvm.mem"):
                    return True
                if c["callee"].startswith("@") and self.m.defined(self.m.resolve_alias(c["callee"][1:])):
                    continue
                if c["callee"].startswith("@__bennett_"):
                    continue
                return True
            return True
        return False

    def s2(self):
        # joint fixpoint with bases
        self.base = {}
        for _ in range(8):
            self.compute_bases()
            old = dict(self.cands)
            for f in self.funcs():
                for ins, c, mk in self.marker_calls(f):
                    for k in REGION_OPS.get(mk, {}):
                        r = self.rr(f, c["args"][k][2])
                        self.sources[(id(ins), k)] = r
                        self.cands[(id(ins), k)] = r if r == "TOP" else {self.resolve(n) for n in r}
            if old == self.cands:
                break
        for f in self.funcs():
            for ins, c, mk in self.marker_calls(f):
                for k, kind in REGION_OPS.get(mk, {}).items():
                    cs = self.cands[(id(ins), k)]
                    if cs == "TOP":
                        raise Reject("BD-E-REGION-UNBOUNDED", ins.text)
                    for n in sorted(cs):
                        if not self.m.defined(n):
                            raise Reject("BD-E-REGION-EXTERNAL", n)
                        fn = self.m.funcs[n]
                        if not region_type_ok(kind, fn):
                            raise Reject("BD-E-REGION-TYPE", f"{n}: {fn.ftype()}")

    # ----------------------------------------------------------- S3
    def s3(self):
        dev = set()
        for f in self.funcs():
            if any(True for _ in self.marker_calls(f)):
                dev.add(f.name)
        for cs in self.cands.values():
            if isinstance(cs, set):
                dev |= cs
        changed = True
        while changed:
            changed = False
            for f in self.funcs():
                if f.name in dev:
                    for c in self.direct_callees(f):
                        if c not in dev:
                            dev.add(c)
                            changed = True
        self.device = dev
        host = [f for f in self.funcs() if f.name not in dev]
        for h in host:
            for ins in h.instrs():
                for nm in re.findall(r"@([-\w.$]+)", ins.text):
                    n = self.m.resolve_alias(nm)
                    if n in dev and not self.is_entry(n):
                        if ins.op in ("call", "invoke") and parse_call(ins)["callee"] == "@" + nm:
                            continue
                        raise Reject("BD-E-DEVICE-ADDRESS", ins.text)
        for f in self.funcs():
            if f.name not in dev:
                continue
            for ins in f.instrs():
                if ins.op in ("invoke", "landingpad", "resume", "cleanuppad", "catchpad", "catchswitch", "cleanupret", "catchret"):
                    raise Reject("BD-E-EH", f"{f.name}: {ins.text}")

    def is_entry(self, n):
        if self.nonlocal_linkage(n):
            return True
        for f in self.funcs():
            if f.name in self.device:
                continue
            if n in self.direct_callees(f):
                return True
        return False

    # ----------------------------------------------------------- S4 provenance (5.2)
    def s4(self):
        self.prov = {}      # (fname, value) -> {lane: frozenset(roots)} ; scalar lane 0
        self.slots = {}     # (obj, off) -> set(roots)
        devf = [f for f in self.funcs() if f.name in self.device]
        changed = True
        it = 0
        while changed:
            it += 1
            if it > 60:
                raise Fail("provenance fixpoint")
            changed = False
            for f in devf:
                for ins in f.instrs():
                    changed |= self.prov_step(f, ins)
        # rejected uses
        for f in devf:
            for ins in f.instrs():
                self.check_uses(f, ins)
        # rule 7: objects holding handles never escape
        hobjs = {o for (o, off), roots in self.slots.items() if roots}
        for f in devf:
            ptrs = {}
            for (fn, v), b in self.base.items():
                if fn == f.name and b != "TOP" and any(o in hobjs for (o, _) in b):
                    ptrs[v] = b
            for o in hobjs:
                if o in self.m.globals:
                    ptrs["@" + o] = frozenset({(o, 0)})
            for ins in f.instrs():
                self.check_obj_uses(f, ins, ptrs)
        # untracked marker handle operands
        for f in devf:
            for ins, c, mk in self.marker_calls(f):
                for k in HANDLE_OPS[mk]:
                    if not self.vprov_any(f, c["args"][k][2]):
                        raise Reject("BD-E-HANDLE-UNTRACKED", ins.text)

    def vprov(self, f, v):
        v = v.strip()
        if v.startswith("%"):
            return self.prov.get((f.name, v), {})
        return {}

    def vprov_any(self, f, v):
        return any(self.vprov(f, v).values())

    def setprov(self, f, v, lanes):
        key = (f.name, v)
        old = self.prov.get(key, {})
        new = dict(old)
        for k, s in lanes.items():
            if s:
                new[k] = frozenset(new.get(k, frozenset()) | s)
        if new != old:
            self.prov[key] = new
            return True
        return False

    def prov_step(self, f, ins):
        op = ins.op
        body = ins.text.split(" = ", 1)[1] if ins.res else ins.text
        ch = False
        if op in ("call", "invoke"):
            c = parse_call(ins)
            nm = c["callee"][len("@__bennett_"):] if c["callee"].startswith("@__bennett_") else None
            if nm in ("qalloc", "qborrow"):
                return self.setprov(f, ins.res, {0: frozenset({f"{f.name}{ins.res}"})})
            if c["callee"].startswith("@llvm.memcpy") or c["callee"].startswith("@llvm.memmove"):
                dst, src, ln = c["args"][0][2], c["args"][1][2], c["args"][2][2]
                bd, bs = self.vbase(f, dst), self.vbase(f, src)
                if bs == "TOP":
                    return False
                for (o, s0) in bs:
                    for (so, so_off), roots in list(self.slots.items()):
                        if so != o or not roots:
                            continue
                        if bd == "TOP":
                            raise Reject("BD-E-HANDLE-STORE", ins.text)
                        for (do, d0) in bd:
                            if do == "EXT":
                                raise Reject("BD-E-HANDLE-ESCAPE", ins.text)
                            if re.match(r"^\d+$", ln) and s0 != "*" and d0 != "*" and so_off != "*" and \
                                    s0 <= so_off and so_off + self.pw // 8 <= s0 + int(ln):
                                key = (do, d0 + so_off - s0)
                            else:
                                key = (do, "*")
                            before = self.slots.get(key, set())
                            if not roots <= before:
                                self.slots[key] = before | roots
                                ch = True
                return ch
            if c["callee"].startswith("@"):
                g = self.m.resolve_alias(c["callee"][1:])
                if self.m.defined(g) and g in self.device:
                    gf = self.m.funcs[g]
                    for i, a in enumerate(c["args"]):
                        p = self.vprov(f, a[2])
                        if p and gf.params[i][2]:
                            ch |= self.setprov(gf, gf.params[i][2], p)
                    if ins.res:
                        for r in gf.instrs():
                            if r.op == "ret" and r.text != "ret void":
                                p = self.vprov(gf, typed_val(r.text[4:]))
                                if p:
                                    ch |= self.setprov(f, ins.res, p)
            return ch
        if op in ("ptrtoint", "inttoptr"):
            src = typed_val(body[len(op):].rsplit(" to ", 1)[0])
            p = self.vprov(f, src)
            if p:
                return self.setprov(f, ins.res, p)
            return False
        if op in ("phi", "select", "freeze"):
            if op == "freeze":
                vals = [typed_val(body[len("freeze"):])]
            else:
                vals = self.value_operands(ins)
            for v in vals:
                p = self.vprov(f, v)
                if p:
                    ch |= self.setprov(f, ins.res, p)
            return ch
        if op == "insertelement":
            parts = split_top(body[len("insertelement"):].strip())
            vec, sc, idx = typed_val(parts[0]), typed_val(parts[1]), typed_val(parts[2])
            pv = dict(self.vprov(f, vec))
            ps = self.vprov(f, sc)
            if ps:
                if not re.match(r"^\d+$", idx):
                    raise Reject("BD-E-HANDLE-USE", ins.text)
                pv[int(idx)] = pv.get(int(idx), frozenset()) | ps.get(0, frozenset())
            if pv:
                return self.setprov(f, ins.res, pv)
            return False
        if op == "extractelement":
            parts = split_top(body[len("extractelement"):].strip())
            vec, idx = typed_val(parts[0]), typed_val(parts[1])
            pv = self.vprov(f, vec)
            if pv:
                if not re.match(r"^\d+$", idx):
                    raise Reject("BD-E-HANDLE-USE", ins.text)
                if pv.get(int(idx)):
                    return self.setprov(f, ins.res, {0: pv[int(idx)]})
            return False
        if op == "insertvalue":
            parts = split_top(body[len("insertvalue"):].strip())
            agg, sc, idx = typed_val(parts[0]), typed_val(parts[1]), parts[2].strip()
            if len(parts) != 3:
                raise Fail("checker: nested insertvalue paths not implemented")
            pv = dict(self.vprov(f, agg))
            ps = self.vprov(f, sc)
            if ps:
                pv[int(idx)] = pv.get(int(idx), frozenset()) | ps.get(0, frozenset())
            return self.setprov(f, ins.res, pv) if pv else False
        if op == "extractvalue":
            parts = split_top(body[len("extractvalue"):].strip())
            if len(parts) != 2:
                raise Fail("checker: nested extractvalue paths not implemented")
            pv = self.vprov(f, typed_val(parts[0]))
            k = int(parts[1])
            return self.setprov(f, ins.res, {0: pv[k]}) if pv.get(k) else False
        if op == "shufflevector":
            parts = split_top(body[len("shufflevector"):].strip())
            a, b = self.vprov(f, typed_val(parts[0])), self.vprov(f, typed_val(parts[1]))
            if not a and not b:
                return False
            n = parse_type(parts[0])[0][1]
            mask = [typed_val(x) for x in split_top(typed_val(parts[2]).strip("<>"))]
            out = {}
            for k, mv in enumerate(mask):
                if re.match(r"^\d+$", mv):
                    src = int(mv)
                    pv = a.get(src) if src < n else b.get(src - n)
                    if pv:
                        out[k] = pv
            return self.setprov(f, ins.res, out) if out else False
        if op == "store":
            val, ptr = store_parts(ins)
            p = self.vprov(f, val)
            if not any(p.values()):
                return False
            b = self.vbase(f, ptr)
            if b == "TOP":
                raise Reject("BD-E-HANDLE-STORE", ins.text)
            vty = parse_type(re.sub(r"^store\s+(atomic\s+)?(volatile\s+)?", "", ins.text))[0]
            esz = tsize(vty[2]) if vty[0] == "vec" else tsize(vty)
            for (o, off) in b:
                if o == "EXT":
                    raise Reject("BD-E-HANDLE-ESCAPE", ins.text)
                if o in self.m.globals and self.host_references(o):
                    raise Reject("BD-E-HANDLE-ESCAPE", ins.text)
                for lane, roots in p.items():
                    key = (o, "*" if off == "*" else off + lane * esz)
                    before = self.slots.get(key, set())
                    if not roots <= before:
                        self.slots[key] = set(before) | set(roots)
                        ch = True
            return ch
        if op == "load":
            rest = re.sub(r"^load\s+(atomic\s+)?(volatile\s+)?", "", body)
            parts = split_top(rest)
            ty = parse_type(parts[0])[0]
            b = self.vbase(f, typed_val(parts[1]))
            if b == "TOP":
                return False
            lanes = ty[1] if ty[0] == "vec" else 1
            ety = ty[2] if ty[0] == "vec" else ty
            out = {}
            for (o, off) in b:
                for (so, soff), roots in self.slots.items():
                    if so != o or not roots:
                        continue
                    for k in range(lanes):
                        lo = "*" if off == "*" else off + k * tsize(ety)
                        if lo == "*" or soff == "*" or lo == soff:
                            if ety in (("ptr",), ("int", self.pw)):
                                out[k] = out.get(k, frozenset()) | frozenset(roots)
                            elif lo == "*" or soff == "*" or lo < soff + 8 and soff < lo + tsize(ety):
                                raise Reject("BD-E-HANDLE-USE", f"partial load: {ins.text}")
                    if off != "*" and soff != "*" and lanes == 1 and ety not in (("ptr",), ("int", self.pw)):
                        if off < soff + 8 and soff < off + tsize(ety):
                            raise Reject("BD-E-HANDLE-USE", f"partial load: {ins.text}")
            if out:
                return self.setprov(f, ins.res, out)
            return False
        return False

    def check_obj_uses(self, f, ins, ptrs):
        body = ins.text.split(" = ", 1)[1] if ins.res else ins.text
        used = [v for v in ptrs if re.search(re.escape(v) + r"(?![-\w.$])", body)]
        if not used:
            return
        op = ins.op
        if op in ("getelementptr", "phi"):
            return
        if op == "select":
            if typed_val(split_top(body[len("select"):].strip())[0]) in used:
                raise Reject("BD-E-HANDLE-ESCAPE", ins.text)
            return
        if op == "load":
            return
        if op == "store":
            if store_parts(ins)[0] in used:
                raise Reject("BD-E-HANDLE-ESCAPE", f"rule 7: {ins.text}")
            return
        if op in ("call", "invoke"):
            c = parse_call(ins)
            cal = c["callee"]
            if re.match(r"@llvm\.mem(cpy|move|set)", cal):
                return
            if cal.startswith("@") and self.m.defined(self.m.resolve_alias(cal[1:])):
                return
            mk = cal[len("@__bennett_"):] if cal.startswith("@__bennett_") else None
            if mk in ENV_OP and all(a[2] not in used or k == ENV_OP[mk] for k, a in enumerate(c["args"])):
                return
        raise Reject("BD-E-HANDLE-ESCAPE", f"rule 7: {ins.text}")

    def host_references(self, gname):
        pat = re.compile(r"@" + re.escape(gname) + r"(?![-\w.$])")
        for f in self.funcs():
            if f.name in self.device:
                continue
            for ins in f.instrs():
                if pat.search(ins.text):
                    return True
        return False

    def check_uses(self, f, ins):
        body = ins.text.split(" = ", 1)[1] if ins.res else ins.text
        locs = set(re.findall(r"%[-\w.$]+", body))
        hd = [v for v in locs if any(self.vprov(f, v).values())]
        if not hd:
            return
        op = ins.op
        if op in ("ptrtoint", "inttoptr"):
            ty = parse_type(body.rsplit(" to ", 1)[1])[0]
            src_t = parse_type(body[len(op):])[0]
            if (op == "ptrtoint" and ty != ("int", self.pw)) or (op == "inttoptr" and src_t != ("int", self.pw)):
                raise Reject("BD-E-HANDLE-USE", ins.text)
            return
        if op in ("phi", "select", "freeze", "insertelement", "extractelement", "shufflevector", "insertvalue", "extractvalue"):
            if op == "select":
                cond = typed_val(split_top(body[len("select"):].strip())[0])
                if cond in hd:
                    raise Reject("BD-E-HANDLE-USE", ins.text)
            return
        if op == "store":
            val, ptr = store_parts(ins)
            if ptr.strip() in hd:
                raise Reject("BD-E-HANDLE-USE", f"dereference: {ins.text}")
            return
        if op == "load":
            ptr = typed_val(split_top(re.sub(r"^load\s+(atomic\s+)?(volatile\s+)?", "", body))[1])
            if ptr in hd:
                raise Reject("BD-E-HANDLE-USE", f"dereference: {ins.text}")
            return
        if op == "ret":
            if self.nonlocal_linkage(f.name) or self.address_taken(f.name):
                raise Reject("BD-E-HANDLE-ESCAPE", f"{f.name}: {ins.text}")
            return
        if op in ("call", "invoke"):
            c = parse_call(ins)
            cal = c["callee"]
            if cal.startswith("@__bennett_") and is_marker(cal[1:]):
                mk = cal[len("@__bennett_"):]
                for k, a in enumerate(c["args"]):
                    if a[2] in hd and k not in HANDLE_OPS[mk]:
                        raise Reject("BD-E-HANDLE-USE", ins.text)
                return
            if cal.startswith("@llvm.memcpy") or cal.startswith("@llvm.memmove"):
                if c["args"][0][2] in hd or c["args"][1][2] in hd:
                    raise Reject("BD-E-HANDLE-USE", ins.text)
                return
            if cal.startswith("@") and self.m.defined(self.m.resolve_alias(cal[1:])):
                return
            raise Reject("BD-E-HANDLE-USE", ins.text)
        raise Reject("BD-E-HANDLE-USE", ins.text)

    # ----------------------------------------------------------- S5
    def closure(self, name):
        seen, stack = set(), [name]
        while stack:
            n = stack.pop()
            if n in seen or not self.m.defined(n):
                continue
            seen.add(n)
            stack += self.direct_callees(self.m.funcs[n])
        return seen

    def region_members(self, kind):
        out = set()
        for f in self.funcs():
            for ins, c, mk in self.marker_calls(f):
                for k, kd in REGION_OPS.get(mk, {}).items():
                    if kd == kind:
                        out |= self.cands[(id(ins), k)]
        return out

    def s5(self):
        for r in sorted(self.region_members("action")):
            for n in sorted(self.closure(r)):
                for ins, c, mk in self.marker_calls(self.m.funcs[n]):
                    if mk == "measure":
                        raise Reject("BD-E-REGION-MEASURE", f"{n}: {ins.text}")
                    if mk == "reversible":
                        raise Reject("BD-E-REGION-TIER", f"{n}: {ins.text}")
        for r in sorted(self.region_members("reversible")):
            for n in sorted(self.closure(r)):
                for ins, c, mk in self.marker_calls(self.m.funcs[n]):
                    raise Reject("BD-E-REVERSIBLE-MARKER", f"{n}: {ins.text}")

    # ----------------------------------------------------------- S7
    def s7(self, mod):
        for f in [mod.funcs[n] for k, n in mod.order if k == "fn" and mod.funcs[n].is_def]:
            for ins in f.instrs():
                if ins.op not in ("call",):
                    continue
                c = parse_call(ins)
                nm = c["callee"][len("@__bennett_"):] if c["callee"].startswith("@__bennett_") else None
                if nm not in INT_CAND_OPS:
                    continue
                for k, role in INT_CAND_OPS[nm].items():
                    cs = int_candidates(mod, f, c["args"][k][2])
                    if cs == "TOP":
                        raise Reject("BD-E-OPERAND-UNBOUNDED", ins.text)
                    for v in cs:
                        if role in OPCODES and v not in OPCODES[role]:
                            raise Reject("BD-E-OPERAND", f"{ins.text}: {v}")
                        if role == "cls" and v != 0:
                            raise Reject("BD-E-OPERAND", f"{ins.text}: class {v}")
                        if role == "n" and v < 1:
                            raise Reject("BD-E-OPERAND", f"{ins.text}: width {v}")


def strip_flags(s):
    toks = s.split(" ")
    while toks and (toks[0] in INT_FLAGS or toks[0] in FMF or toks[0].startswith("inrange")):
        toks.pop(0)
    return " ".join(toks)


def typed_val(s):
    s = s.strip()
    ty, k = parse_type(s)
    attrs, rest = strip_param_attrs(s[k:])
    return rest.strip()


def store_parts(ins):
    body = re.sub(r"^store\s+(atomic\s+)?(volatile\s+)?", "", ins.text)
    parts = split_top(body)
    return typed_val(parts[0]), typed_val(parts[1])


def gep_offset(srcty, idxs):
    off = idxs[0] * tsize(srcty)
    t = srcty
    for i in idxs[1:]:
        if t[0] in ("arr", "vec"):
            off += i * tsize(t[2])
            t = t[2]
        elif t[0] == "struct":
            o = 0
            for k, e in enumerate(t[1]):
                a = talign(e)
                o = (o + a - 1) // a * a
                if k == i:
                    break
                o += tsize(e)
            off += o
            t = t[1][i]
        else:
            raise Fail("gep into scalar")
    return off


def fn_consts_at(g, off, mod):
    init = g["init"] or ""
    ty = g["type"]
    if ty[0] == "arr" and init.startswith("["):
        elems = split_top(init[1:-1])
        es = tsize(ty[2])
        out = []
        for k, e in enumerate(elems):
            if off == "*" or off == k * es:
                v = typed_val(e)
                if v.startswith("@"):
                    out.append(v[1:])
        return out
    if ty == ("ptr",) and (off == 0 or off == "*"):
        v = init.strip()
        return [v[1:]] if v.startswith("@") else []
    return []


def region_type_ok(kind, fn):
    if kind in ("action", "reversible"):
        return fn.ftype() == "void (ptr)"
    if len(fn.params) != 1 or fn.vararg or fn.params[0][0][0] != "int" or fn.ret[0] != "int":
        return False
    n, t = fn.params[0][0][1], fn.ret[1]
    if not (1 <= n <= 128 and 1 <= t <= 128):
        return False
    return kind == "oracle" or n == t


def int_candidates(mod, f, v, depth=0):
    v = v.strip()
    if re.match(r"^-?\d+$", v):
        return {int(v) % (1 << 64)}
    if v in ("true", "false"):
        return {int(v == "true")}
    if not v.startswith("%") or depth > 30:
        return "TOP"
    d = {i.res: i for i in f.instrs() if i.res}
    ins = d.get(v)
    if ins is None:
        return "TOP"
    a = Analysis(mod)
    if ins.op in ("select", "phi"):
        out = set()
        for x in a.value_operands(ins):
            r = int_candidates(mod, f, x, depth + 1)
            if r == "TOP":
                return "TOP"
            out |= r
        return out
    if ins.op == "load":
        body = ins.text.split(" = ", 1)[1]
        parts = split_top(re.sub(r"^load\s+(atomic\s+)?(volatile\s+)?", "", body))
        lty = parse_type(parts[0])[0]
        g, off = const_global_base(mod, f, typed_val(parts[1]), d)
        if g is None:
            return "TOP"
        gl = mod.globals[g]
        if not gl["constant"] or gl["type"][0] != "arr" or gl["type"][2] != lty:
            return "TOP"
        elems = [int(typed_val(e)) % (1 << 64) for e in split_top(gl["init"][1:-1])]
        es = tsize(lty)
        return set(elems) if off == "*" else {elems[off // es]}
    if ins.op in ("zext", "trunc", "sext"):
        body = ins.text.split(" = ", 1)[1]
        src = body[len(ins.op):].rsplit(" to ", 1)[0]
        sty = parse_type(strip_flags(src.strip()))[0]
        dty = parse_type(body.rsplit(" to ", 1)[1])[0]
        r = int_candidates(mod, f, typed_val(strip_flags(src.strip())), depth + 1)
        if r == "TOP":
            return r
        out = set()
        for x in r:
            x &= (1 << sty[1]) - 1
            if ins.op == "sext" and x >> (sty[1] - 1):
                x -= 1 << sty[1]
            out.add(x % (1 << dty[1]))
        return out
    return "TOP"


def const_global_base(mod, f, v, d):
    """(global, offset or '*') for @g or a getelementptr chain over @g; (None, None) otherwise."""
    v = v.strip()
    if v.startswith("@") and v[1:] in mod.globals:
        return v[1:], 0
    ins = d.get(v)
    if ins is None or ins.op != "getelementptr":
        return None, None
    rest = re.sub(r"^getelementptr\s+((inbounds|nusw|nuw)\s+)*", "", ins.text.split(" = ", 1)[1])
    parts = split_top(rest)
    srcty = parse_type(parts[0])[0]
    g, off = const_global_base(mod, f, typed_val(parts[1]), d)
    if g is None:
        return None, None
    idxs = [typed_val(x) for x in parts[2:]]
    if off == "*" or any(not re.match(r"^-?\d+$", i) for i in idxs):
        return g, "*"
    return g, off + gep_offset(srcty, [int(i) for i in idxs])

