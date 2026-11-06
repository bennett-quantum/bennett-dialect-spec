from dialect_profile import profile
"""Dialect execution: shared definitions extracted without changing checker behavior."""
from pathlib import Path
import cmath
import hashlib
import json
import math
import re
import shutil
import subprocess
from dialect_ir import (
    ADJ, BINOPS, B_DEFAULT, DECLS_TEXT, Fail, GATE1, GATE2, HEADER, ISA_SPEC, LEG, MAJORS, MARKERS, Module, NORTH_STAR, PERMITTED_PARAM, PERMITTED_RET, Reject, SPEC_PATH, TOOLCHAINS, attr_name, parse_call, parse_type, split_top
)
from dialect_analysis import (
    Analysis, int_candidates, region_type_ok, strip_flags, typed_val
)
from dialect_rewrite import (
    normalise, validate
)

def lift(text):
    m = Module(text)
    defs = [m.funcs[n] for k, n in m.order if k == "fn" and m.funcs[n].is_def]
    if len(defs) != 1:
        raise Fail("lift example must define exactly one function")
    f = defs[0]
    if not region_type_ok("oracle", f):
        raise Reject("BD-E-LIFT-SUBSET", f"type {f.ftype()}")
    N, T = f.params[0][0][1], f.ret[1]
    pname = f.params[0][2]
    blocks = f.blocks
    bidx = {lab: i for i, (lab, _) in enumerate(blocks)}
    vnum, k = {}, 0
    for lab, blk in blocks:
        for ins in blk:
            if ins.res:
                vnum[ins.res] = f"v{k}"
                k += 1
    widths = {}
    regs = []
    cnt = {"c": 0, "t": 0}
    out_blocks = []

    def new(prefix, w):
        n = f"{prefix}{cnt[prefix]}"
        cnt[prefix] += 1
        return n, w

    def define(name, w):
        if name not in widths:
            widths[name] = w
            regs.append(name)

    def opnd(val, ty, rows):
        val = val.strip()
        if val == pname:
            return "p0"
        if val.startswith("%"):
            return vnum[val]
        if ty[0] != "int":
            raise Reject("BD-E-LIFT-SUBSET", f"operand {val}")
        if val in ("true", "false"):
            c = int(val == "true")
        else:
            c = int(val) % (1 << ty[1])
        n, w = new("c", ty[1])
        define(n, w)
        rows.append(f"{n} = lift.const.i{ty[1]} {c}")
        return n

    phis = {}
    for lab, blk in blocks:
        phis[lab] = [i for i in blk if i.op == "phi"]

    def edge_moves(src, dst, rows):
        ps = phis[dst]
        if not ps:
            return
        dsts, srcs = [], []
        for p in ps:
            body = p.text.split(" = ", 1)[1]
            ty, j = parse_type(body[4:])
            inc = {}
            for part in split_top(body[4 + j:]):
                v, b = split_top(part.strip()[1:-1])
                inc[b.strip()[1:]] = v.strip()
            srcs.append(opnd(inc[src], ty, rows))
            dsts.append(vnum[p.res])
        for d, p in zip(dsts, ps):
            define(d, parse_type(p.text.split(" = ", 1)[1][4:])[0][1])
        rows.append(f"({', '.join(dsts)}) = lift.parmov ({', '.join(srcs)})")

    def succ_name(i, lab_to, edge_blocks):
        if phis[lab_to]:
            edge_blocks.add(bidx[lab_to])
            return f"^b{i}.e{bidx[lab_to]}"
        return f"^b{bidx[lab_to]}"

    for i, (lab, blk) in enumerate(blocks):
        rows = []
        chain = []
        edge_blocks = set()
        live = [x for x in blk if not x.deleted]
        j = 0
        while j < len(live):
            ins = live[j]
            op = ins.op
            body = ins.text.split(" = ", 1)[1] if ins.res else ins.text
            if op == "phi":
                j += 1
                continue
            if op in BINOPS:
                rest = body.split(None, 1)[1]
                if strip_flags(rest) != rest:
                    raise Reject("BD-E-LIFT-SUBSET", ins.text)
                ty, k2 = parse_type(rest)
                a, b = split_top(rest[k2:])
                A = opnd(a, ty, rows)
                B = opnd(b, ty, rows)
                define(vnum[ins.res], ty[1])
                rows.append(f"{vnum[ins.res]} = lift.{op} {A} {B}")
            elif op == "icmp":
                pm = re.match(r"icmp (\w+) (.*)$", body)
                pred, rest = pm.group(1), pm.group(2)
                ty, k2 = parse_type(rest)
                if ty[0] != "int":
                    raise Reject("BD-E-LIFT-SUBSET", ins.text)
                a, b = split_top(rest[k2:])
                A = opnd(a, ty, rows)
                B = opnd(b, ty, rows)
                sw = {"ugt": "ult", "uge": "ule", "sgt": "slt", "sge": "sle"}
                if pred in sw:
                    pred, A, B = sw[pred], B, A
                define(vnum[ins.res], 1)
                rows.append(f"{vnum[ins.res]} = lift.icmp.{pred} {A} {B}")
            elif op == "select":
                parts = split_top(body[len("select"):].strip())
                cty, _ = parse_type(parts[0])
                ty, _ = parse_type(parts[1])
                C = opnd(typed_val(parts[0]), cty, rows)
                A = opnd(typed_val(parts[1]), ty, rows)
                B = opnd(typed_val(parts[2]), ty, rows)
                define(vnum[ins.res], ty[1])
                rows.append(f"{vnum[ins.res]} = lift.select {C} {A} {B}")
            elif op in ("zext", "sext", "trunc"):
                src, dst = body[len(op):].rsplit(" to ", 1)
                sty = parse_type(strip_flags(src.strip()))[0]
                dty = parse_type(dst)[0]
                A = opnd(typed_val(src), sty, rows)
                define(vnum[ins.res], dty[1])
                rows.append(f"{vnum[ins.res]} = lift.{op}.i{dty[1]} {A}")
            elif op == "call":
                c = parse_call(ins)
                cal = c["callee"]
                im = re.match(r"@llvm\.(umin|umax|smin|smax|abs)\.i\d+$", cal)
                if cal == "@__bennett_nz_fault":
                    if j + 1 >= len(live) or live[j + 1].op != "unreachable":
                        raise Reject("BD-E-LIFT-SUBSET", ins.text)
                    rows.append(f"fault {int(c['args'][0][2])}")
                    j += 2
                    continue
                if not im:
                    raise Reject("BD-E-LIFT-SUBSET", ins.text)
                kind = im.group(1)
                ty = c["ret"]
                v = vnum[ins.res]
                if kind == "abs":
                    if c["args"][1][2] != "false":
                        raise Reject("BD-E-LIFT-SUBSET", ins.text)
                    A = opnd(c["args"][0][2], ty, rows)
                    z, _ = new("c", ty[1])
                    define(z, ty[1])
                    t1, _ = new("t", 1)
                    define(t1, 1)
                    t2, _ = new("t", ty[1])
                    define(t2, ty[1])
                    define(v, ty[1])
                    rows += [f"{z} = lift.const.i{ty[1]} 0", f"{t1} = lift.icmp.slt {A} {z}", f"{t2} = lift.sub {z} {A}",
                             f"{v} = lift.select {t1} {t2} {A}"]
                else:
                    A = opnd(c["args"][0][2], ty, rows)
                    B = opnd(c["args"][1][2], ty, rows)
                    t, _ = new("t", 1)
                    define(t, 1)
                    pred = "ult" if kind in ("umin", "umax") else "slt"
                    x, y = (A, B) if kind in ("umin", "smin") else (B, A)
                    define(v, ty[1])
                    rows += [f"{t} = lift.icmp.{pred} {x} {y}", f"{v} = lift.select {t} {A} {B}"]
            elif op == "ret":
                rest = body[3:].strip()
                ty, k2 = parse_type(rest)
                A = opnd(rest[k2:], ty, rows)
                rows.append(f"lift.retval {A}")
            elif op == "unreachable":
                rows.append("fault 4")
            elif op == "br":
                lbls = re.findall(r"label %([-\w.$]+)", body)
                if len(lbls) == 1 or lbls[0] == lbls[1]:
                    edge_moves(lab, lbls[0], rows)
                    rows.append(f"qjump ^b{bidx[lbls[0]]}")
                else:
                    cond = re.match(r"br i1 ([^,]+),", body).group(1)
                    C = opnd(cond, ("int", 1), rows)
                    rows.append(f"qbranch {C} {succ_name(i, lbls[0], edge_blocks)} {succ_name(i, lbls[1], edge_blocks)}")
            elif op == "switch":
                sm = re.match(r"switch (\S+) ([^,]+), label %([-\w.$]+) \[(.*)\]$", body)
                ty = parse_type(sm.group(1))[0]
                cond, dflt = sm.group(2), sm.group(3)
                cases = re.findall(r"\S+ (-?\d+), label %([-\w.$]+)", sm.group(4))
                if not cases:
                    edge_moves(lab, dflt, rows)
                    rows.append(f"qjump ^b{bidx[dflt]}")
                else:
                    C = opnd(cond, ty, rows) if not cond.startswith("%") else opnd(cond, ty, rows)
                    cur = rows
                    for jj, (kv, tgt) in enumerate(cases, 1):
                        cn = opnd(kv, ty, cur)
                        t, _ = new("t", 1)
                        define(t, 1)
                        cur.append(f"{t} = lift.icmp.eq {C} {cn}")
                        nxt = f"^b{i}.s{jj}" if jj < len(cases) else succ_name(i, dflt, edge_blocks)
                        cur.append(f"qbranch {t} {succ_name(i, tgt, edge_blocks)} {nxt}")
                        if jj < len(cases):
                            cur = []
                            chain.append((f"b{i}.s{jj}", cur))
            else:
                raise Reject("BD-E-LIFT-SUBSET", ins.text)
            j += 1
        out_blocks.append((f"b{i}", rows))
        out_blocks += chain
        for s in sorted(edge_blocks):
            erows = []
            edge_moves(lab, blocks[s][0], erows)
            erows.append(f"qjump ^b{s}")
            out_blocks.append((f"b{i}.e{s}", erows))
    # regs in order of first appearance as destination in the emitted text
    order = []
    for _, rows in out_blocks:
        for r in rows:
            lhs = r.split(" = ")[0] if " = " in r else ""
            for n in re.findall(r"[A-Za-z_][\w.]*", lhs):
                if n in widths and n not in order:
                    order.append(n)
    text_out = [f"oracle @ref (p0:wire[{N}] in) (tgt:wire[{T}]) (fault:wire[4]) () ()"]
    if order:
        text_out.append("regs { " + ", ".join(f"{n}:reg[{widths[n]}]" for n in order) + " }")
    for name, rows in out_blocks:
        text_out.append(f"^{name}():")
        text_out += rows
    return "\n".join(text_out), N, T


def isa_anchor():
    """The hash procedure of section 9.5 must reproduce the ISA's own inc8 test vector (ISA 16.3)."""
    isa = ISA_SPEC.read_text()
    body = re.search(r"\n(oracle @inc8 .*?lift\.retval r)\n", isa, re.S).group(1)
    want = re.search(r"inc8 = ([0-9a-f]{64})", isa).group(1)
    got = ref_hash(body, 8, 8, 32)
    if got != want:
        raise Fail(f"hash procedure does not reproduce ISA inc8: {got} != {want}")


def ref_hash(body, N, T, pw):
    sig = {"abi": profile().isa, "args": [], "fault": 4, "in": [N], "kind": "oracle", "mem": [], "tgt": T, "tier": "q"}
    env = "\n".join(["isa=0.8", f"ptr_width={pw}", json.dumps(sig, sort_keys=True, separators=(",", ":"))] + body.split("\n")) + "\n"
    return hashlib.sha256(env.encode()).hexdigest()


def run_ref(body, x, B):
    """ISA reference interpreter (section 14.1) for the rows the map emits; returns (payload, code, steps)."""
    lines = body.split("\n")
    header = lines[0]
    widths = {"p0": int(re.search(r"p0:wire\[(\d+)\]", header).group(1))}
    T = int(re.search(r"tgt:wire\[(\d+)\]", header).group(1))
    blocks, cur = {}, None
    for ln in lines[1:]:
        if ln.startswith("regs "):
            for n, w in re.findall(r"([\w.]+):reg\[(\d+)\]", ln):
                widths[n] = int(w)
            continue
        if ln.startswith("^"):
            cur = ln[1:-3]
            blocks[cur] = []
            continue
        blocks[cur].append(ln)
    env = {n: 0 for n in widths}
    env["p0"] = x
    pc_b, pc_i, steps = "b0", 0, 0

    def mask(n, v):
        return v & ((1 << widths[n]) - 1)

    def sgn(v, w):
        return v - (1 << w) if v >> (w - 1) else v
    while True:
        if steps >= B:
            return (0, 1, steps)
        row = blocks[pc_b][pc_i]
        steps += 1
        pc_i += 1
        if " = " in row:
            lhs, rhs = row.split(" = ", 1)
        else:
            lhs, rhs = None, row
        t = rhs.split()
        op = t[0]
        if op.startswith("lift.const."):
            env[lhs] = mask(lhs, int(t[1]))
        elif op in ("lift.add", "lift.sub", "lift.mul", "lift.and", "lift.or", "lift.xor", "lift.shl", "lift.lshr", "lift.ashr"):
            a, b = env[t[1]], env[t[2]]
            w = widths[t[1]]
            r = {"lift.add": a + b, "lift.sub": a - b, "lift.mul": a * b, "lift.and": a & b, "lift.or": a | b,
                 "lift.xor": a ^ b, "lift.shl": (a << b) if b < w else 0, "lift.lshr": (a >> b) if b < w else 0,
                 "lift.ashr": (sgn(a, w) >> b) if b < w else 0}[op]
            env[lhs] = mask(lhs, r)
        elif op in ("lift.udiv", "lift.urem", "lift.sdiv", "lift.srem"):
            a, b = env[t[1]], env[t[2]]
            w = widths[t[1]]
            if b == 0:
                return (0, 5, steps)
            if op in ("lift.sdiv", "lift.srem") and a == 1 << (w - 1) and b == (1 << w) - 1:
                return (0, 6, steps)
            if op == "lift.udiv":
                r = a // b
            elif op == "lift.urem":
                r = a % b
            else:
                sa, sb = sgn(a, w), sgn(b, w)
                q = abs(sa) // abs(sb) * (1 if (sa < 0) == (sb < 0) else -1)
                r = q if op == "lift.sdiv" else sa - q * sb
            env[lhs] = mask(lhs, r)
        elif op.startswith("lift.icmp."):
            pred = op.split(".")[2]
            a, b = env[t[1]], env[t[2]]
            w = widths[t[1]]
            r = {"eq": a == b, "ne": a != b, "ult": a < b, "ule": a <= b, "slt": sgn(a, w) < sgn(b, w), "sle": sgn(a, w) <= sgn(b, w)}[pred]
            env[lhs] = int(r)
        elif op == "lift.select":
            env[lhs] = env[t[2]] if env[t[1]] else env[t[3]]
        elif op.startswith(("lift.zext.", "lift.trunc.", "lift.sext.")):
            a = env[t[1]]
            if op.startswith("lift.sext."):
                a = sgn(a, widths[t[1]])
            env[lhs] = mask(lhs, a)
        elif op == "lift.parmov":
            dsts = re.findall(r"[\w.]+", lhs)
            srcs = re.findall(r"[\w.]+", rhs[len("lift.parmov"):])
            vals = [env[s] for s in srcs]
            for d, v in zip(dsts, vals):
                env[d] = mask(d, v)
        elif op == "qjump":
            pc_b, pc_i = t[1][1:], 0
        elif op == "qbranch":
            pc_b, pc_i = (t[2] if env[t[1]] else t[3])[1:], 0
        elif op == "lift.retval":
            return (env[t[1]] & ((1 << T) - 1), 0, steps)
        elif op == "fault":
            return (0, int(t[1]), steps)
        else:
            raise Fail(f"interpreter: row {row}")


def trace_to_events(lines):
    """Parse the trace runtime output for one input into the event list of sections 8.3-8.4."""
    pos = 0
    widths = {}

    def parse_seq(stop):
        nonlocal pos
        ev = []
        while pos < len(lines):
            ln = lines[pos]
            pos += 1
            t = ln.split()
            if not t:
                continue
            if t[0] == stop:
                return ev
            if t[0] in ("IN", "RET"):
                continue
            if t[0] == "QALLOC":
                widths[t[1]] = int(t[3])
                ev.append(("qalloc", t[1], (), int(t[3])))
            elif t[0] == "QFREE":
                ev.append(("qfree", t[1], ()))
            elif t[0] == "GATE":
                for g in GATE1[int(t[1])]:
                    ev.append((g[0], f"{t[2]}.{t[3]}", ()))
            elif t[0] == "GATE2":
                ev.append((GATE2[int(t[1])], f"{t[2]}.{t[3]}", f"{t[4]}.{t[5]}", ()))
            elif t[0] == "CTRL":
                body = parse_seq("END")
                w = f"{t[1]}.{t[2]}"
                for e in body:
                    if w in e[1:-1]:
                        raise Fail("T-CTRL in trace")
                ev += [e[:-1] + (tuple(sorted(set(e[-1]) | {w})),) if e[0] not in ("qalloc", "qfree") else e for e in body]
            elif t[0] == "ADJ":
                body = parse_seq("END")
                ev += adjoint(body)
            elif t[0] == "COMPUTE":
                body = parse_seq("END")
                ks = [k for k in range(1, len(body) // 2 + 1) if body[:k] == body[len(body) - k:]]
                if len(ks) != 1:
                    raise Fail(f"compute trace split ambiguous: {ks}")
                k = ks[0]
                ev += body[:len(body) - k] + adjoint(body[:k])
            else:
                raise Fail(f"trace line not handled: {ln}")
        return ev
    return parse_seq(None)


def adjoint(evs):
    out = []
    for e in reversed(evs):
        if e[0] == "qalloc":
            out.append(("qfree", e[1], ()))
        elif e[0] == "qfree":
            raise Fail("adjoint of qfree needs the width")
        else:
            out.append((ADJ[e[0]],) + e[1:])
    return out


def event_str(e):
    if e[0] == "qalloc":
        return f"qalloc {e[1]} {e[3]}"
    if e[0] == "qfree":
        return f"qfree {e[1]}"
    s = " ".join([e[0]] + list(e[1:-1]))
    if e[-1]:
        s += " ctrl " + ",".join(e[-1])
    return s


def simulate(evs, upto):
    wires = []
    state = {(): 1 + 0j}
    widths = {}
    for idx, e in enumerate(evs):
        if idx == upto:
            return wires, state
        if e[0] == "qalloc":
            for i in range(e[3]):
                wires.append(f"{e[1]}.{i}")
            state = {k + (0,) * e[3]: a for k, a in state.items()}
            widths[e[1]] = e[3]
            continue
        if e[0] == "qfree":
            idxs = [wires.index(f"{e[1]}.{i}") for i in range(widths[e[1]])]
            for k, a in state.items():
                if abs(a) > 1e-12 and any(k[i] for i in idxs):
                    raise Fail(f"T-CLEAN at event {idx}")
            state = {tuple(b for j, b in enumerate(k) if j not in idxs): a for k, a in state.items()}
            wires = [w for j, w in enumerate(wires) if j not in idxs]
            continue
        ctrl = [wires.index(w) for w in e[-1]]
        ops = [wires.index(w) for w in e[1:-1]]
        new = {}
        for k, a in state.items():
            if abs(a) < 1e-15:
                continue
            if not all(k[c] for c in ctrl):
                new[k] = new.get(k, 0) + a
                continue
            for k2, a2 in apply_gate(e[0], k, ops):
                new[k2] = new.get(k2, 0) + a * a2
        state = new
    return wires, state


def apply_gate(g, k, ops):
    k = list(k)
    q = ops[0]
    b = k[q]
    if g == "x":
        k[q] ^= 1
        return [(tuple(k), 1)]
    if g == "h":
        k0, k1 = list(k), list(k)
        k0[q], k1[q] = 0, 1
        s = 1 / math.sqrt(2)
        return [(tuple(k0), s), (tuple(k1), -s if b else s)]
    ph = {"s": 1j, "sdg": -1j, "t": cmath.exp(1j * math.pi / 4), "tdg": cmath.exp(-1j * math.pi / 4)}
    if g in ph:
        return [(tuple(k), ph[g] if b else 1)]
    if g == "cx":
        if k[ops[0]]:
            k[ops[1]] ^= 1
        return [(tuple(k), 1)]
    if g == "cz":
        return [(tuple(k), -1 if k[ops[0]] and k[ops[1]] else 1)]
    if g == "swap":
        k[ops[0]], k[ops[1]] = k[ops[1]], k[ops[0]]
        return [(tuple(k), 1)]
    raise Fail(f"gate {g}")


def parse_amp(s):
    s = s.strip()
    if s.endswith("i"):
        m = re.match(r"^([-+]?[\d.]+)([-+][\d.]+)i$", s)
        if m:
            return complex(float(m.group(1)), float(m.group(2)))
        return complex(0, float(s[:-1]))
    return complex(float(s), 0)


def toolchains():
    tc = {}
    cur = None
    for ln in TOOLCHAINS.read_text().split("\n"):
        m = re.match(r"\[llvm(\d+)\]", ln.strip())
        if m:
            cur = m.group(1)
        m = re.match(r'bin\s*=\s*"([^"]+)"', ln.strip())
        if m and cur:
            tc[cur] = Path(m.group(1))
    for k in MAJORS:
        if k not in tc or not (tc[k] / "opt").exists():
            raise Fail(f"toolchain LLVM {k} missing opt (toolchains.toml)")
    return tc


def run(argv, **kw):
    r = subprocess.run(argv, capture_output=True, text=True, **kw)
    return r


def verify_all(text, tc, tmp, label):
    p = Path(tmp) / (re.sub(r"\W", "_", label) + ".ll")
    p.write_text(text)
    for k in MAJORS:
        r = run([str(tc[k] / "opt"), "-passes=verify", "-disable-output", str(p)])
        if r.returncode != 0:
            raise Fail(f"{label}: LLVM {k} verify failed:\n{r.stderr.strip()[:800]}")


def with_decls(text):
    out = text
    used = set(re.findall(r"@(__bennett_\w+)\(", text)) | set(re.findall(r"@(__bennett_\w+)\b", text))
    declared = set(re.findall(r"declare [^@]*@(__bennett_\w+)\(", text)) | set(re.findall(r"define [^@]*@(__bennett_\w+)\(", text))
    extra = [DECLS_TEXT[n] for n in sorted(used - declared) if n in DECLS_TEXT]
    if extra:
        out = text + "\n" + "\n".join(extra) + "\n"
    return out


def collapse(s):
    return [re.sub(r"\s+", " ", l).strip() for l in s.split("\n") if l.strip()]


def headings(path):
    hs = set()
    for ln in Path(path).read_text().split("\n"):
        m = re.match(r"^#{2,4}\s+(\d+(?:\.\d+)*)\.?\s", ln)
        if m:
            hs.add(m.group(1))
    return hs


def check_xrefs(text, errors):
    """Section references. A reference preceded by 'ISA' names the ISA spec, by 'north star' the north
    star; one that continues a list ('§a, §b', '§a and §b', '§a–§b') names the document of the reference
    before it (spec section 1.5); references after 'findings', 'survey', 'triage', 'summary', 'plan' name
    spike documents and are not checked; any other names this spec."""
    own = headings(SPEC_PATH)
    isa = headings(ISA_SPEC)
    ns = headings(NORTH_STAR)
    n = 0
    last_doc, last_end = None, -10
    for m in re.finditer(r"§(\d+(?:\.\d+)*)", text):
        ref = m.group(1)
        between = text[last_end:m.start()]
        before = text[max(0, m.start() - 40):m.start()]
        words = re.findall(r"[A-Za-z]+", before)
        prev = words[-1].lower() if words and re.search(r"[A-Za-z]+\W*$", before.rstrip("( `")) else ""
        if last_doc is not None and re.fullmatch(r"\s*([,;]\s*|[–-]\s*|\s+(and|or|to)\s+)", between or "x"):
            doc = last_doc
        elif prev == "isa":
            doc = "ISA"
        elif prev == "star":
            doc = "north star"
        elif prev in ("findings", "survey", "triage", "summary", "plan"):
            doc = "spike"
        else:
            doc = "spec"
        last_doc, last_end = doc, m.end()
        if doc == "spike":
            continue
        ok = ref in {"ISA": isa, "north star": ns, "spec": own}[doc]
        n += 1
        if not ok:
            line = text.count("\n", 0, m.start()) + 1
            errors.append(f"line {line}: unresolved {doc} §{ref}")
    return n


def check_markers(blocks, tc, tmp, errors):
    hdr = HEADER.read_text()
    protos = hdr.split("/* BEGIN PROTOTYPES */\n", 1)[1].split("/* END PROTOTYPES */", 1)[0]
    cblk = [b for b in blocks if b["lang"] == "c" and "markers-c" in b["attrs"]]
    if len(cblk) != 1:
        errors.append("expected exactly one `c markers-c` block")
        return
    if cblk[0]["body"] != protos:
        errors.append("C header view (§3.3) differs from spec/bennett_markers.h prototypes")
    # names agree
    ir_names = set(MARKERS)
    c_names = set(re.findall(r"(__bennett_\w+)\(", protos))
    if ir_names != c_names:
        errors.append(f"marker names differ: IR-only {ir_names - c_names}, C-only {c_names - ir_names}")
    # clang lowering of the header
    src = Path(tmp) / "hdr.c"
    calls = []
    for name, fn in MARKERS.items():
        args = []
        for (ty, _, _) in fn.params:
            args.append({"ptr": "0", "int": "0", "double": "0.0"}[ty[0]])
        calls.append(f"(void){name}({', '.join(args)});")
    src.write_text('#include "bennett_markers.h"\nvoid use_all(void) {\n' + "\n".join(calls) + "\n}\n")
    out = Path(tmp) / "hdr.ll"
    r = run([str(tc["18"] / "clang"), "-std=c11", "-O0", "-S", "-emit-llvm", "-I", str(HEADER.parent), str(src), "-o", str(out)])
    if r.returncode != 0:
        errors.append(f"clang-18 on header failed: {r.stderr[:500]}")
        return
    got = {}
    for ln in out.read_text().split("\n"):
        if ln.startswith("declare ") and "__bennett_" in ln:
            fn = Module(ln).funcs
            (n, f), = fn.items()
            got[n] = f
    for name, fn in MARKERS.items():
        if name not in got:
            errors.append(f"clang did not declare {name}")
            continue
        if got[name].ftype() != fn.ftype():
            errors.append(f"{name}: header lowers to {got[name].ftype()}, §3.2 says {fn.ftype()}")
        for a in got[name].ret_attrs + [x for p in got[name].params for x in p[1]]:
            if attr_name(a) not in PERMITTED_PARAM | PERMITTED_RET:
                errors.append(f"{name}: clang adds non-permitted attribute {a}")
    # C++ view compiles too
    srcpp = Path(tmp) / "hdr.cpp"
    srcpp.write_text(src.read_text().replace("(void)", "(void)"))
    r = run([str(tc["18"] / "clang"), "-x", "c++", "-std=c++17", "-fsyntax-only", "-I", str(HEADER.parent), str(srcpp)])
    if r.returncode != 0:
        errors.append(f"clang++ on header failed: {r.stderr[:500]}")


def classify(text):
    m = Module(text)
    a = Analysis(m)
    try:
        a.s1()
        a.s2()
        a.s3()
        a.s4()
        a.s5()
        # S6: normalise device closure (examples: whole module) and validate
        dev_only = text
        nm = normalise(dev_only) if a.device else dev_only
        a.materialised = True
        validate_device(nm, a.device)
        a.s7(Module(nm))
        # S8: lift oracle regions (9), then verify in-place pairs (6.4 item 4)
        mm = Module(nm)
        bodies = {}
        for name in sorted(a.region_members("oracle") | a.region_members("inplace")):
            bodies[name] = lift(extract_function(mm, name))
        verify_inplace(mm, bodies, a)
        return "accept", a
    except Reject as r:
        return f"reject:{r.code}", r


def verify_inplace(mm, bodies, a):
    """Candidate sets come from step S2 on the optimised module (section 4.1), keyed by position."""
    pos = {}
    for f in a.funcs():
        for k, (ins, c, mk) in enumerate(a.marker_calls(f)):
            if mk == "inplace":
                pos[(f.name, k)] = (a.cands[(id(ins), 0)], a.cands[(id(ins), 1)])
    am = Analysis(mm, materialised=True)
    for f in am.funcs():
        for k, (ins, c, mk) in enumerate(am.marker_calls(f)):
            if mk != "inplace":
                continue
            budgets = int_candidates(mm, f, c["args"][2][2])
            gs, gis = pos[(f.name, k)]
            for g in sorted(gs):
                for gi in sorted(gis):
                    for B in sorted(budgets):
                        B = B_DEFAULT if B == (1 << 64) - 1 else B
                        bg, N, _ = bodies[g]
                        bgi = bodies[gi][0]
                        if N > 16:
                            raise Reject("BD-E-INPLACE-UNVERIFIED", f"{g}/{gi}: N = {N}")
                        for x in range(1 << N):
                            y, c1, _ = run_ref(bg, x, B)
                            z, c2, _ = run_ref(bgi, y, B) if not c1 else (None, 1, 0)
                            if c1 or c2 or z != x:
                                raise Reject("BD-E-INPLACE-NOT-INVERSE", f"{g}/{gi} at B={B}, x={x}")


def validate_device(text, device):
    m = Module(text)
    keep = [n for k, n in m.order if k == "fn" and m.funcs[n].is_def and n in device]
    if keep:
        validate(text)


def extract_function(m, name):
    f = m.funcs[name]
    lines = [f.header]
    for bi, (lab, blk) in enumerate(f.blocks):
        lines.append(f"{lab if lab != '<entry>' else 'b0'}:")
        lines += ["  " + i.text for i in blk if not i.deleted]
    lines.append("}")
    decls = [fn.header for n, fn in m.funcs.items() if not fn.is_def and n.startswith("llvm.")]
    return "\n".join(lines + decls) + "\n"


def build_and_trace(body, k, tc, tmp):
    d = Path(tmp) / f"sem-{k}"
    d.mkdir(exist_ok=True)
    ll = d / "case.ll"
    ll.write_text(body)
    obj = d / "case.o"
    r = run([str(tc["18"] / "llc"), "-O0", "-relocation-model=pic", "-filetype=obj", str(ll), "-o", str(obj)])
    if r.returncode:
        raise Fail(f"llc: {r.stderr[:400]}")
    cc = shutil.which("cc") or shutil.which("gcc")
    objs = []
    for src in ("trace_rt.c", "driver.c"):
        o = d / (src + ".o")
        r = run([cc, "-std=c11", "-O0", "-fPIC", "-c", str(LEG / "runtime" / src), "-o", str(o)])
        if r.returncode:
            raise Fail(f"cc {src}: {r.stderr[:400]}")
        objs.append(str(o))
    exe = d / "case"
    r = run([cc, "-no-pie", "-rdynamic", str(obj)] + objs + ["-ldl", "-o", str(exe)])
    if r.returncode:
        raise Fail(f"link: {r.stderr[:400]}")
    out = {}
    for x in range(4):
        r = run([str(exe), str(x)])
        if r.returncode:
            raise Fail(f"run x={x}: {r.stdout[-300:]} {r.stderr[-300:]}")
        out[x] = r.stdout.strip().split("\n")
    return out

