"""Dialect ir: shared definitions extracted without changing checker behavior."""
from dialect_pins import sibling
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent


SPEC = ROOT / "spec" / "Bennett-Dialect-Spec.md"


HEADER = ROOT / "spec" / "bennett_markers.h"


LEG = ROOT / "corpus" / "legality"


TOOLCHAINS = LEG / "toolchains.toml"


ISA_SPEC = sibling("bennett-isa-spec") / "spec" / "Bennett-ISA-Spec.md"


NORTH_STAR = sibling("bennett") / "docs" / "Bennett-NorthStar.md"


MAJORS = ("18", "20", "23")


class Fail(Exception):
    pass


class Reject(Exception):
    """A recogniser verdict: reject with a BD-E code."""
    def __init__(self, code, why):
        super().__init__(f"{code}: {why}")
        self.code, self.why = code, why


def extract_blocks(text):
    out = []
    for m in re.finditer(r"^```([^\n]*)\n(.*?)^```\s*$", text, re.S | re.M):
        info = m.group(1).strip().split()
        lang = info[0] if info else ""
        attrs = {}
        for tok in info[1:]:
            if "=" in tok:
                k, v = tok.split("=", 1)
                attrs[k] = v
            else:
                attrs[tok] = True
        line = text.count("\n", 0, m.start()) + 1
        out.append({"lang": lang, "attrs": attrs, "body": m.group(2), "line": line})
    return out


LINKAGE = {"private", "internal", "available_externally", "linkonce", "weak", "common", "appending",
           "extern_weak", "linkonce_odr", "weak_odr", "external"}


VISIBILITY = {"default", "hidden", "protected", "dso_local", "dso_preemptable", "dllimport", "dllexport"}


CCS = {"ccc", "fastcc", "coldcc", "swiftcc", "tailcc", "webkit_jscc", "anyregcc", "preserve_mostcc",
       "preserve_allcc", "cxx_fast_tlscc", "ghccc", "swifttailcc", "cfguard_checkcc"}


FP_TYPES = {"half", "bfloat", "float", "double", "x86_fp80", "fp128", "ppc_fp128"}


UNSUPPORTED_FP = {"half", "bfloat", "x86_fp80", "fp128", "ppc_fp128"}


def match_close(s, i):
    """Index just past the bracket that closes s[i]."""
    pairs = {"(": ")", "[": "]", "{": "}", "<": ">"}
    stack = [pairs[s[i]]]
    j = i + 1
    while j < len(s):
        c = s[j]
        if c == '"':
            j = s.index('"', j + 1)
        elif c in pairs:
            stack.append(pairs[c])
        elif c == stack[-1]:
            stack.pop()
            if not stack:
                return j + 1
        j += 1
    raise Fail(f"unbalanced bracket in: {s}")


def split_top(s, sep=","):
    parts, depth, cur, i = [], 0, "", 0
    while i < len(s):
        c = s[i]
        if c == '"':
            j = s.index('"', i + 1)
            cur += s[i:j + 1]
            i = j + 1
            continue
        if c in "([{<":
            depth += 1
        elif c in ")]}>":
            depth -= 1
        if c == sep and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += c
        i += 1
    if cur.strip():
        parts.append(cur.strip())
    return parts


def parse_type(s, i=0):
    """Parse one LLVM type at s[i:]; returns (type, index after)."""
    while i < len(s) and s[i] == " ":
        i += 1
    if s.startswith("<{", i):
        j = match_close(s, i)
        return ("struct", tuple(parse_type(x)[0] for x in split_top(s[i + 2:j - 2]))), j
    if s[i] == "{":
        j = match_close(s, i)
        inner = s[i + 1:j - 1].strip()
        return ("struct", tuple(parse_type(x)[0] for x in split_top(inner)) if inner else ()), j
    if s[i] == "<":
        j = match_close(s, i)
        m = re.match(r"\s*(vscale\s+x\s+)?(\d+)\s+x\s+(.*)$", s[i + 1:j - 1])
        return ("vec", int(m.group(2)), parse_type(m.group(3))[0]), j
    if s[i] == "[":
        j = match_close(s, i)
        m = re.match(r"\s*(\d+)\s+x\s+(.*)$", s[i + 1:j - 1])
        return ("arr", int(m.group(1)), parse_type(m.group(2))[0]), j
    m = re.compile(r"(i\d+|ptr(?:\s+addrspace\(\d+\))?|void|half|bfloat|float|double|x86_fp80|fp128|ppc_fp128|label|token|metadata|\.\.\.)").match(s, i)
    if not m:
        raise Fail(f"cannot parse type at: {s[i:]!r}")
    w = m.group(1)
    if w.startswith("i") and w[1:].isdigit():
        return ("int", int(w[1:])), m.end()
    if w.startswith("ptr"):
        return (("ptr", int(re.search(r"addrspace\((\d+)\)", w)[1])) if "addrspace" in w else ("ptr",)), m.end()
    return (w,), m.end()


def tstr(t):
    k = t[0]
    if k == "ptr" and len(t)>1:
        return f"ptr addrspace({t[1]})"
    if k == "int":
        return f"i{t[1]}"
    if k == "vec":
        return f"<{t[1]} x {tstr(t[2])}>"
    if k == "arr":
        return f"[{t[1]} x {tstr(t[2])}]"
    if k == "struct":
        return "{ " + ", ".join(tstr(x) for x in t[1]) + " }"
    return k


def tsize(t, pw=64):
    """Allocation size in bytes under the default (x86-64-like) layout."""
    k = t[0]
    if k == "int":
        n = (t[1] + 7) // 8
        p = 1
        while p < n:
            p *= 2
        return p
    if k == "ptr":
        return pw // 8
    if k in ("double",):
        return 8
    if k in ("float",):
        return 4
    if k == "arr":
        return t[1] * tsize(t[2], pw)
    if k == "vec":
        return t[1] * tsize(t[2], pw)
    if k == "struct":
        off, al = 0, 1
        for e in t[1]:
            a = talign(e, pw)
            off = (off + a - 1) // a * a + tsize(e, pw)
            al = max(al, a)
        return (off + al - 1) // al * al
    raise Fail(f"no size for type {tstr(t)}")


def talign(t, pw=64):
    if t[0] in ("arr", "vec"):
        return talign(t[2], pw) if t[0] == "arr" else tsize(t, pw)
    if t[0] == "struct":
        return max([talign(e, pw) for e in t[1]] or [1])
    return min(tsize(t, pw), 8)


ATTR_TOKEN = re.compile(r'"[^"]*"(?:="[^"]*")?|#\d+|[A-Za-z_][\w.]*(?:\([^()]*(?:\([^()]*\)[^()]*)*\))?|\d+')


def attr_tokens(s):
    return ATTR_TOKEN.findall(s)


def attr_name(tok):
    if tok.startswith('"'):
        return "<string>"
    return re.match(r"[^( ]*", tok).group(0)


PARAM_ATTR_WORDS = {"noundef", "nonnull", "zeroext", "signext", "noext", "inreg", "noalias", "nocapture", "readonly",
                    "readnone", "writeonly", "returned", "writable", "dead_on_unwind", "immarg", "nest", "swiftself",
                    "swifterror", "allocalign", "allocptr", "nofree", "align", "dereferenceable",
                    "dereferenceable_or_null", "range", "nofpclass", "captures", "initializes", "byval", "sret",
                    "byref", "inalloca", "preallocated", "elementtype", "noundef"}


def strip_param_attrs(s):
    """Split 'attrs... rest' where attrs are parameter attributes; returns (attrs, rest)."""
    attrs = []
    s = s.strip()
    while True:
        m = re.match(r'([A-Za-z_]+)(\([^()]*(?:\([^()]*\)[^()]*)*\))?\s*', s)
        if not m or m.group(1) not in PARAM_ATTR_WORDS:
            break
        word = m.group(1)
        tok = m.group(0).strip()
        s = s[m.end():]
        if word == "align":
            m2 = re.match(r"(\d+)\s*", s)
            tok += " " + m2.group(1)
            s = s[m2.end():]
        attrs.append(tok)
    return attrs, s


class Instr:
    def __init__(self, text, res, op, fn, block):
        self.text, self.res, self.op, self.fn, self.block = text, res, op, fn, block
        self.deleted = False

    def __repr__(self):
        return self.text


class Func:
    def __init__(self):
        self.name = None
        self.is_def = False
        self.linkage = "external"
        self.ret = None
        self.ret_attrs = []
        self.params = []        # (type, attrs, name)
        self.vararg = False
        self.fn_attrs = []      # tokens (#N resolved later)
        self.keywords = []
        self.blocks = []        # (label, [Instr])
        self.header = ""
        self.cc = None

    def ftype(self):
        return fnstr(self.ret, [p[0] for p in self.params], self.vararg)

    def instrs(self):
        for _, ins in self.blocks:
            for i in ins:
                if not i.deleted:
                    yield i


def fnstr(ret, params, vararg):
    ps = [tstr(p) for p in params] + (["..."] if vararg else [])
    return f"{tstr(ret)} ({', '.join(ps)})"


class Module:
    def __init__(self, text):
        self.text = text
        self.funcs = {}
        self.order = []
        self.globals = {}       # name -> dict
        self.aliases = {}       # name -> aliasee
        self.groups = {}        # '#N' -> tokens
        self.lines_other = []
        self.parse(text)

    def parse(self, text):
        lines = text.split("\n")
        i = 0
        while i < len(lines):
            ln = lines[i]
            st = ln.strip()
            if not st or st.startswith(";"):
                i += 1
                continue
            if st.startswith("define "):
                f, i = self.parse_function(lines, i)
                self.funcs[f.name] = f
                self.order.append(("fn", f.name))
                continue
            if st.startswith("declare "):
                f = self.parse_header(st, False)
                self.funcs[f.name] = f
                self.order.append(("fn", f.name))
            elif st.startswith("attributes #"):
                m = re.match(r"attributes (#\d+) = \{(.*)\}\s*$", st)
                self.groups[m.group(1)] = attr_tokens(m.group(2))
            elif st.startswith("@"):
                self.parse_global(st)
            i += 1

    def parse_global(self, st):
        m = re.match(r'@([-\w.$]+) = (.*)$', st)
        name, rest = m.group(1), m.group(2)
        toks = rest.split()
        if " alias " in f" {rest} ":
            am = re.search(r"alias [^,]+, ptr @([-\w.$]+)", rest)
            self.aliases[name] = am.group(1)
            self.order.append(("alias", name))
            return
        linkage = "external"
        kws = []
        j = 0
        while toks[j] not in ("global", "constant"):
            if toks[j] in LINKAGE:
                linkage = toks[j]
            kws.append(toks[j])
            j += 1
        kind = toks[j]
        after = " ".join(toks[j + 1:])
        ty, k = parse_type(after, 0)
        init = after[k:].strip()
        init_parts = split_top(init)
        init_val = init_parts[0] if init_parts else ""
        attrs = re.findall(r"#\d+", init)
        is_decl = linkage in ("external", "extern_weak") and (init_val == "" or init_val.startswith("#") or init_val.startswith("align"))
        self.globals[name] = {"linkage": linkage, "constant": kind == "constant", "type": ty, "init": None if is_decl else init_val,
                              "attrs": attrs, "text": st, "kws": kws}
        self.order.append(("global", name))

    def parse_header(self, st, is_def):
        f = Func()
        f.is_def = is_def
        f.header = st
        m = re.search(r"@([-\w.$]+)\(", st)
        f.name = m.group(1)
        pre = st[:m.start()].split(None, 1)[1] if " " in st[:m.start()] else ""
        pend = match_close(st, m.end() - 1)
        params = st[m.end():pend - 1]
        post = st[pend:].strip()
        if post.endswith("{"):
            post = post[:-1].strip()
        toks = pre.split()
        rest = []
        for t in toks:
            if t in LINKAGE:
                f.linkage = t
                f.keywords.append(t)
            elif t in VISIBILITY or t in CCS or t.startswith("cc"):
                f.keywords.append(t)
                if t in CCS:
                    f.cc = t
            else:
                rest.append(t)
        rattrs, rtype = strip_param_attrs(" ".join(rest))
        f.ret_attrs = rattrs
        f.ret = parse_type(rtype)[0]
        for p in split_top(params):
            if p == "...":
                f.vararg = True
                continue
            ty, k = parse_type(p)
            attrs, name = strip_param_attrs(p[k:])
            f.params.append((ty, attrs, name.strip() or None))
        # post: unnamed_addr, attrs, personality ...
        pers = re.search(r"personality .*$", post)
        if pers:
            post = post[:pers.start()]
        for t in attr_tokens(post):
            if t in ("unnamed_addr", "local_unnamed_addr"):
                f.keywords.append(t)
            else:
                f.fn_attrs.append(t)
        return f

    def parse_function(self, lines, i):
        hdr = lines[i].strip()
        f = self.parse_header(hdr, True)
        i += 1
        label = "<entry>"
        cur = []
        f.blocks.append((label, cur))
        pending = ""
        while True:
            st = lines[i].strip()
            i += 1
            if st == "}":
                break
            if not st or st.startswith(";"):
                continue
            if pending:
                st = pending + " " + st
                pending = ""
            if re.match(r"^[-\w.$]+:(\s*;.*)?$", st):
                lab = st.split(":")[0]
                if not cur and f.blocks[-1][0] == "<entry>" and len(f.blocks) == 1:
                    f.blocks[-1] = (lab, cur)
                else:
                    cur = []
                    f.blocks.append((lab, cur))
                continue
            st = re.sub(r"\s*;.*$", "", st) if not st.startswith('"') else st
            if (st.startswith("invoke ") or " = invoke " in st) and " unwind " not in st:
                pending = st
                continue
            if ("switch " in st.split("=")[-1][:12] or st.startswith("switch ")) and not st.rstrip().endswith("]"):
                pending = st
                continue
            m = re.match(r"^(%[-\w.$]+) = (.*)$", st)
            res, body = (m.group(1), m.group(2)) if m else (None, st)
            op = body.split()[0]
            if op in ("tail", "musttail", "notail"):
                op = body.split()[1]
            cur.append(Instr(st, res, op, f, f.blocks[-1][0]))
        return f, i

    # ------------------------------------------------------------- helpers
    def defined(self, name):
        return name in self.funcs and self.funcs[name].is_def

    def resolve_alias(self, name):
        seen = set()
        while name in self.aliases:
            if name in seen:
                raise Fail("alias cycle")
            seen.add(name)
            name = self.aliases[name]
        return name

    def fn_attr_names(self, toks):
        out = []
        for t in toks:
            if t.startswith("#"):
                out += [x for x in self.groups.get(t, [])]
            else:
                out.append(t)
        return out


def parse_call(ins):
    """Return dict for call/invoke: callee, fntype (ret, params, vararg), args, fn_attrs, ret_attrs, cc, bundles."""
    body = ins.text.split(" = ", 1)[1] if ins.res else ins.text
    m = re.match(r"^(?:(tail|musttail|notail)\s+)?(call|invoke)\s+(.*)$", body)
    if not m:
        raise Fail(f"not a call: {ins.text}")
    tailkw, kind, rest = m.group(1), m.group(2), m.group(3)
    if re.search(r'\basm\b', rest):
        # Inline asm is ordinary §15 input, never a marker. Keep arguments for N31.
        am = re.search(r'asm(?: sideeffect)?(?: alignstack)? "([^"\n]*)", "([^"\n]*)"\((.*)\)', rest)
        if not am:
            raise Fail("cannot parse inline asm: " + ins.text)
        ret = parse_type(rest)[0]
        args = []
        for arg in split_top(am.group(3)):
            ty, kk = parse_type(arg)
            attrs, value = strip_param_attrs(arg[kk:])
            args.append((ty, attrs, value))
        return {"callee": "@llvm.inlineasm", "ret": ret, "params": [a[0] for a in args],
                "vararg": False, "args": args, "fn_attrs": [], "ret_attrs": [], "cc": None,
                "bundles": False, "tail": tailkw, "kind": kind, "unwind": None, "fmf": [],
                "explicit": False, "asm": am.group(1), "constraints": am.group(2)}
    # callee: first top-level @name( or %name(
    cm = None
    depth = 0
    for mm in re.finditer(r"[@%][-\w.$]+\(|[()]", rest):
        tok = mm.group(0)
        if tok == "(":
            depth += 1
            continue
        if tok == ")":
            depth -= 1
            continue
        if depth == 0:
            cm = mm
            break
    if cm is None:
        raise Fail(f"cannot find callee: {ins.text}")
    callee = cm.group(0)[:-1]
    pre = rest[:cm.start()].strip()
    aend = match_close(rest, cm.end() - 1)
    args_s = rest[cm.end():aend - 1]
    post = rest[aend:].strip()
    unwind = None
    if kind == "invoke":
        um = re.search(r"to label (%[-\w.$]+) unwind label (%[-\w.$]+)", post)
        unwind = (um.group(1), um.group(2))
        post = post[:um.start()].strip()
    bundles = "[" in post and re.search(r'\[\s*"', post) is not None
    # strip metadata
    post_attrs = re.sub(r",\s*!.*$", "", post)
    fn_attrs = [t for t in attr_tokens(post_attrs)]
    # pre: [fast-math flags] [cc] [ret attrs] type [ (fn params) ]
    cc = None
    toks = pre.split()
    fmf = []
    while toks and toks[0] in {"fast", "nnan", "ninf", "nsz", "arcp", "contract", "afn", "reassoc"}:
        fmf.append(toks.pop(0))
    if toks and (toks[0] in CCS or re.match(r"cc\d+", toks[0])):
        cc = toks.pop(0)
    pre2 = " ".join(toks)
    ret_attrs, tyrest = strip_param_attrs(pre2)
    ret, k = parse_type(tyrest)
    explicit = tyrest[k:].strip()
    args = []
    for a in split_top(args_s):
        ty, kk = parse_type(a)
        attrs, val = strip_param_attrs(a[kk:])
        args.append((ty, attrs, val.strip()))
    if explicit.startswith("("):
        ps = split_top(explicit[1:-1])
        vararg = "..." in ps
        params = [parse_type(p)[0] for p in ps if p != "..."]
    else:
        vararg = False
        params = [a[0] for a in args]
    return {"callee": callee, "ret": ret, "params": params, "vararg": vararg, "args": args, "fn_attrs": fn_attrs,
            "ret_attrs": ret_attrs, "cc": cc, "bundles": bundles, "tail": tailkw, "kind": kind, "unwind": unwind,
            "fmf": fmf, "explicit": bool(explicit)}


def marker_list(spec_blocks):
    blk = [b for b in spec_blocks if b["lang"] == "llvm" and "markers-ir" in b["attrs"]]
    if len(blk) != 1:
        raise Fail("expected exactly one `llvm markers-ir` block")
    out = {}
    for ln in blk[0]["body"].strip().split("\n"):
        f = Module(ln).funcs
        (name, fn), = f.items()
        out[name] = fn
    return out


MARKERS = {}


DECLS_TEXT = {}


HANDLE_OPS = {"qalloc": [], "qborrow": [], "qfree": [0], "gate": [1], "gate2": [1, 3], "gate3": [1, 3, 5], "rot": [1],
              "measure": [0], "qload": [0, 1, 2], "qstore": [0, 1, 2], "ctrl": [0], "adj": [], "compute": [],
              "reversible": [], "inplace": [3], "oracle": [2, 3, 4]}


REGION_OPS = {"ctrl": {2: "action"}, "adj": {0: "action"}, "compute": {0: "action", 1: "action"},
              "reversible": {0: "reversible"}, "inplace": {0: "inplace", 1: "inplace"}, "oracle": {0: "oracle"}}


ENV_OP = {"ctrl": 4, "adj": 1, "compute": 2, "reversible": 2}


INT_CAND_OPS = {"qalloc": {0: "cls", 1: "n"}, "qborrow": {0: "cls", 1: "n"}, "gate": {0: "op1"}, "gate2": {0: "op2"},
                "gate3": {0: "op3"}, "rot": {0: "rot"}, "inplace": {2: "budget"}, "oracle": {1: "budget"}}


OPCODES = {"op1": set(range(1, 9)), "op2": {1, 2, 3}, "op3": {1}, "rot": {1, 2, 3}}


PERMITTED_FN = {"nounwind", "nonlazybind", "uwtable"}


PERMITTED_RET = {"noundef", "nonnull", "range", "zeroext", "signext"}


PERMITTED_PARAM = {"noundef", "nonnull", "range", "zeroext", "signext"}


FORBIDDEN_LIE = {"readnone", "readonly", "willreturn", "speculatable"}


def mname(fname):
    return fname[len("__bennett_"):] if fname.startswith("__bennett_") and fname[len("__bennett_"):] in MARKERS_SHORT else None


MARKERS_SHORT = set()


def is_marker(name):
    return name.startswith("__bennett_") and name[len("__bennett_"):] in MARKERS_SHORT


HEAP_FNS = {"malloc", "calloc", "aligned_alloc", "_Znwm", "_Znam", "__rust_alloc", "__rust_alloc_zeroed"}


BINOPS = {"add", "sub", "mul", "and", "or", "xor", "shl", "lshr", "ashr", "udiv", "sdiv", "urem", "srem"}


FBINOPS = {"fadd", "fsub", "fmul", "fdiv", "frem"}


INT_FLAGS = {"nsw", "nuw", "exact", "inbounds", "nusw", "nneg", "disjoint", "samesign"}


FMF = {"nnan", "ninf", "nsz", "arcp", "contract", "afn", "reassoc", "fast"}


N4_FN = {"memory", "readnone", "readonly", "writeonly", "argmemonly", "inaccessiblememonly",
         "inaccessiblemem_or_argmemonly", "willreturn", "mustprogress", "nosync", "nofree", "norecurse", "speculatable"}


N4_PARAM = {"noundef", "nonnull", "range", "align", "dereferenceable", "dereferenceable_or_null", "nofpclass", "noalias",
            "nocapture", "captures", "readnone", "readonly", "writeonly", "returned", "writable", "dead_on_unwind",
            "initializes", "allocalign", "allocptr"}


ABI_WITH_ALIGN = {"byval", "byref", "sret", "inalloca", "preallocated"}


GATE1 = {1: [("x",)], 2: [("h",)], 3: [("s",)], 4: [("sdg",)], 5: [("t",)], 6: [("tdg",)], 7: [("s",), ("s",)],
         8: [("sdg",), ("x",), ("s",)]}


GATE2 = {1: "cx", 2: "cz", 3: "swap"}


ADJ = {"x": "x", "h": "h", "s": "sdg", "sdg": "s", "t": "tdg", "tdg": "t", "cx": "cx", "cz": "cz", "swap": "swap",
       "ccx": "ccx", "qalloc": "qfree", "qfree": "qalloc"}


B_DEFAULT = 1048576


SPEC_PATH = SPEC

