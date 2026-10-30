#!/usr/bin/env python3
"""Pre-flight check for spec/Bennett-Dialect-Spec.md (dialect 0.2).

Seed of the reference recogniser, the residual-poison validator and the
lifting map. It extracts every tagged example from the spec (tagging:
spec section 1.5) and checks what the spec states about it:

  - every `llvm` block parses and verifies on LLVM 18, 20 and 23
    (corpus/legality/toolchains.toml), with the implied marker
    declarations of section 1.5;
  - `example=` blocks: the recogniser (sections 3-7, 9) gives the stated
    verdict, and `candidates=` the stated candidate sets (section 6.2);
  - `normalise-in/out` pairs: the normaliser (section 7.2) maps one onto
    the other; the output passes the validator (section 7.5);
  - `lift=` / `reference-body=` / `hash=` / `fb=` / `inplace=`: the
    lifting map (section 9) gives exactly the stated ISA text, the hash
    (section 9.5), and the stated F_B results on an interpreter of the
    ISA lifted rows (ISA section 4.2, 14.1);
  - `semantics=` / `events=` / `state=`: the program equals its corpus
    file, is accepted, and, built with the spike trace runtime, yields
    the stated events (section 8.3, 8.4) and state vector;
  - the marker list (section 3.2) agrees with the C view (section 3.3),
    with spec/bennett_markers.h, and with clang-18's lowering of it;
  - every section cross-reference resolves (this spec, the ISA spec,
    the north star).

Python 3 stdlib only; calls the LLVM tools of toolchains.toml and cc.
Exit 0 only if everything checks. Usage: dialect_check.py [SPEC]
"""
import cmath
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "spec" / "Bennett-Dialect-Spec.md"
HEADER = ROOT / "spec" / "bennett_markers.h"
LEG = ROOT / "corpus" / "legality"
TOOLCHAINS = LEG / "toolchains.toml"
ISA_SPEC = ROOT.parent / "bennett-isa-spec" / "spec" / "Bennett-ISA-Spec.md"
NORTH_STAR = ROOT.parent / "bennett" / "docs" / "Bennett-NorthStar.md"
MAJORS = ("18", "20", "23")


class Fail(Exception):
    pass


class Reject(Exception):
    """A recogniser verdict: reject with a BD-E code."""
    def __init__(self, code, why):
        super().__init__(f"{code}: {why}")
        self.code, self.why = code, why


# ===================================================================== spec

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


# ================================================================== IR parse

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


# ---------------------------------------------------------- call parsing

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


# ================================================================= markers

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


MARKERS = {}           # filled from the spec
DECLS_TEXT = {}

# operand roles (section 3.2 table)
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


# =============================================================== recogniser

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


HEAP_FNS = {"malloc", "calloc", "aligned_alloc", "_Znwm", "_Znam", "__rust_alloc", "__rust_alloc_zeroed"}
BINOPS = {"add", "sub", "mul", "and", "or", "xor", "shl", "lshr", "ashr", "udiv", "sdiv", "urem", "srem"}
FBINOPS = {"fadd", "fsub", "fmul", "fdiv", "frem"}
INT_FLAGS = {"nsw", "nuw", "exact", "inbounds", "nusw", "nneg", "disjoint", "samesign"}
FMF = {"nnan", "ninf", "nsz", "arcp", "contract", "afn", "reassoc", "fast"}


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


# ============================================================ normaliser (7.2)

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


N4_FN = {"memory", "readnone", "readonly", "writeonly", "argmemonly", "inaccessiblememonly",
         "inaccessiblemem_or_argmemonly", "willreturn", "mustprogress", "nosync", "nofree", "norecurse", "speculatable"}
N4_PARAM = {"noundef", "nonnull", "range", "align", "dereferenceable", "dereferenceable_or_null", "nofpclass", "noalias",
            "nocapture", "captures", "readnone", "readonly", "writeonly", "returned", "writable", "dead_on_unwind",
            "initializes", "allocalign", "allocptr"}
ABI_WITH_ALIGN = {"byval", "byref", "sret", "inalloca", "preallocated"}


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


# ============================================================== validator (7.5)

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


# ============================================================== lifting map (9)

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
    sig = {"abi": "0.8", "args": [], "fault": 4, "in": [N], "kind": "oracle", "mem": [], "tgt": T, "tier": "q"}
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


# ============================================================== semantics (8)

GATE1 = {1: [("x",)], 2: [("h",)], 3: [("s",)], 4: [("sdg",)], 5: [("t",)], 6: [("tdg",)], 7: [("s",), ("s",)],
         8: [("sdg",), ("x",), ("s",)]}
GATE2 = {1: "cx", 2: "cz", 3: "swap"}
ADJ = {"x": "x", "h": "h", "s": "sdg", "sdg": "s", "t": "tdg", "tdg": "t", "cx": "cx", "cz": "cz", "swap": "swap",
       "ccx": "ccx", "qalloc": "qfree", "qfree": "qalloc"}


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


# ================================================================== tools

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


# ================================================================== checks

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


B_DEFAULT = 1048576


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


SPEC_PATH = SPEC


def legacy_main():
    global SPEC_PATH, MARKERS, MARKERS_SHORT
    spec = Path(sys.argv[1]) if len(sys.argv) > 1 else SPEC
    SPEC_PATH = spec
    text = spec.read_text()
    errors = []
    tc = toolchains()
    blocks = extract_blocks(text)
    MARKERS.update(marker_list(blocks))
    MARKERS_SHORT |= {n[len("__bennett_"):] for n in MARKERS}
    mk_block = [b for b in blocks if "markers-ir" in b["attrs"]][0]["body"]
    for ln in mk_block.strip().split("\n"):
        n = re.search(r"@(__bennett_\w+)\(", ln).group(1)
        DECLS_TEXT[n] = re.sub(r" %\w+", "", ln)
    counts = {}

    def count(k):
        counts[k] = counts.get(k, 0) + 1

    with tempfile.TemporaryDirectory() as tmp:
        if len(MARKERS) != 16:
            errors.append(f"§3.2 lists {len(MARKERS)} markers, expected 16")
        check_markers(blocks, tc, tmp, errors)
        count("marker-agreement")
        isa_anchor()
        count("isa-hash-anchor")
        lifts, refs, hashes, fbs, inpl = {}, {}, {}, {}, []
        norm_in, norm_out = {}, {}
        sems, events, states = {}, {}, {}
        for b in blocks:
            a, body, lang = b["attrs"], b["body"], b["lang"]
            tag = f"line {b['line']}"
            if lang in ("llvm", "isa") and not a:
                errors.append(f"{tag}: untagged {lang} block")
                continue
            try:
                if lang == "llvm" and "markers-ir" in a:
                    verify_all(body, tc, tmp, "markers")
                    count("verify")
                elif lang == "llvm" and "example" in a:
                    full = with_decls(body)
                    verify_all(full, tc, tmp, a["example"])
                    count("verify")
                    if a.get("mode") == "validate":
                        try:
                            got = validate(full)
                        except Reject as r:
                            got = f"reject:{r.code}"
                        info = None
                    else:
                        got, info = classify(full)
                    if got != a["verdict"]:
                        why = info.why if isinstance(info, Reject) else ""
                        errors.append(f"{tag} example {a['example']}: stated {a['verdict']}, recogniser says {got} {why}")
                    elif "candidates" in a and isinstance(info, Analysis):
                        want = set(a["candidates"].split(","))
                        gotc = set()
                        for cs in info.cands.values():
                            if isinstance(cs, set):
                                gotc |= cs
                        if gotc != want:
                            errors.append(f"{tag} example {a['example']}: stated candidates {sorted(want)}, got {sorted(gotc)}")
                    count("verdict")
                elif lang == "llvm" and "normalise-in" in a:
                    verify_all(body, tc, tmp, "nin-" + a["normalise-in"])
                    norm_in[a["normalise-in"]] = body
                    count("verify")
                elif lang == "llvm" and "normalise-out" in a:
                    verify_all(body, tc, tmp, "nout-" + a["normalise-out"])
                    norm_out[a["normalise-out"]] = body
                    count("verify")
                elif lang == "llvm" and "lift" in a:
                    verify_all(body, tc, tmp, "lift-" + a["lift"])
                    lifts[a["lift"]] = (body, a.get("verdict", "accept"))
                    count("verify")
                elif lang == "llvm" and "semantics" in a:
                    verify_all(body, tc, tmp, "sem-" + a["semantics"])
                    sems[a["semantics"]] = (body, a)
                    count("verify")
                elif lang == "isa" and "reference-body" in a:
                    refs[a["reference-body"]] = body.rstrip("\n")
                elif lang == "text" and "hash" in a:
                    hashes[a["hash"]] = (body.strip(), int(a.get("ptr_width", "64")))
                elif lang == "text" and "fb" in a:
                    fbs[a["fb"]] = body
                elif lang == "text" and "inplace" in a:
                    inpl.append(a)
                elif lang == "text" and "events" in a:
                    events[(a["events"], a["input"])] = body
                elif lang == "text" and "state" in a:
                    states[(a["state"], a["input"], int(a["at"]))] = body
                elif lang in ("llvm", "isa"):
                    errors.append(f"{tag}: unknown tag {a}")
            except Fail as e:
                errors.append(f"{tag}: {e}")
        # normalisation pairs
        for k in sorted(set(norm_in) | set(norm_out)):
            if k not in norm_in or k not in norm_out:
                errors.append(f"normalise pair {k} incomplete")
                continue
            try:
                got = normalise(norm_in[k])
                if collapse(got) != collapse(norm_out[k]):
                    import difflib
                    d = "\n".join(difflib.unified_diff(collapse(norm_out[k]), collapse(got), "stated", "normaliser", lineterm=""))
                    errors.append(f"normalise {k}: output differs\n{d}")
                validate(norm_out[k])
                count("normalise")
            except (Fail, Reject) as e:
                errors.append(f"normalise {k}: {e}")
        # lifting
        computed_hash = {}
        for k, (body, verdict) in lifts.items():
            try:
                isa_text, N, T = lift(body)
                got = "accept"
            except Reject as r:
                got, isa_text = f"reject:{r.code}", None
            except Fail as e:
                errors.append(f"lift {k}: {e}")
                continue
            if got != verdict:
                errors.append(f"lift {k}: stated {verdict}, map says {got}")
                continue
            count("lift-verdict")
            if isa_text is None:
                continue
            lifts[k] = (body, verdict, isa_text, N, T)
            if k in refs:
                if refs[k] != isa_text:
                    import difflib
                    d = "\n".join(difflib.unified_diff(refs[k].split("\n"), isa_text.split("\n"), "stated", "map", lineterm=""))
                    errors.append(f"reference body {k} differs\n{d}")
                else:
                    count("reference-body")
            if k in hashes:
                h = ref_hash(isa_text, N, T, hashes[k][1])
                computed_hash[k] = h
                if hashes[k][0] != h:
                    errors.append(f"hash {k}: stated {hashes[k][0]}, computed {h}")
                else:
                    count("hash")
        for k, body in fbs.items():
            if k not in lifts or len(lifts[k]) < 3:
                errors.append(f"fb {k}: no lifted body")
                continue
            isa_text = lifts[k][2]
            nres = 0
            for ln in body.strip().split("\n"):
                ln = ln.strip()
                ms = re.match(r"^steps=(.*)$", ln)
                if ms:
                    for x in range(256):
                        want = eval(ms.group(1), {}, {"x": x})
                        p, c, s = run_ref(isa_text, x, 10 ** 6)
                        if c == 0 and s != want:
                            errors.append(f"fb {k}: x={x}: steps {s}, stated {want}")
                            break
                        nres += 1
                    continue
                m = re.match(r"^B=(\S+) x=(\d+)\.\.(\d+) -> payload=(.*) code=(\S+)$", ln)
                if not m:
                    errors.append(f"fb {k}: cannot parse {ln!r}")
                    continue
                for x in range(int(m.group(2)), int(m.group(3)) + 1):
                    B = eval(m.group(1), {}, {"x": x})
                    wp = eval(m.group(4), {"min": min}, {"x": x})
                    wc = eval(m.group(5), {}, {"x": x})
                    p, c, s = run_ref(isa_text, x, B)
                    if (p, c) != (wp, wc):
                        errors.append(f"fb {k}: B={B} x={x}: got ({p}, {c}), stated ({wp}, {wc})")
                        break
                    nres += 1
            count("fb-results")
            counts["fb-points"] = counts.get("fb-points", 0) + nres
        for a in inpl:
            g, gi, B = a["g"], a["ginv"], int(a["B"])
            if g not in lifts or gi not in lifts or len(lifts[g]) < 3 or len(lifts[gi]) < 3:
                errors.append(f"inplace {a['inplace']}: missing lifted bodies")
                continue
            N = lifts[g][3]
            verdict = "accept"
            for x in range(1 << N):
                y, c, _ = run_ref(lifts[g][2], x, B)
                if c:
                    verdict = "reject:BD-E-INPLACE-NOT-INVERSE"
                    break
                z, c2, _ = run_ref(lifts[gi][2], y, B)
                if c2 or z != x:
                    verdict = "reject:BD-E-INPLACE-NOT-INVERSE"
                    break
            if verdict != a["verdict"]:
                errors.append(f"inplace {a['inplace']}: stated {a['verdict']}, check says {verdict}")
            else:
                count("inplace")
        # semantics
        for k, (body, a) in sems.items():
            corpus = LEG / "cases" / (a["corpus"] + ".ll")
            if not corpus.exists() or corpus.read_text() != body:
                errors.append(f"semantics {k}: differs from {corpus}")
            got, info = classify(body)
            if got != "accept":
                errors.append(f"semantics {k}: recogniser says {got} {getattr(info, 'why', '')}")
            try:
                traces = build_and_trace(body, k, tc, tmp)
            except Fail as e:
                errors.append(f"semantics {k}: {e}")
                continue
            for (ek, inp), ebody in events.items():
                if ek != k:
                    continue
                try:
                    evs = trace_to_events(traces[int(inp)])
                except Fail as e:
                    errors.append(f"semantics {k}: {e}")
                    continue
                got_s = [event_str(e) for e in evs]
                if got_s != collapse(ebody):
                    errors.append(f"events {k} input {inp}: stated\n{ebody}\ngot\n" + "\n".join(got_s))
                else:
                    count("events")
                try:
                    simulate(evs, len(evs))
                    count("clean-release")
                except Fail as e:
                    errors.append(f"semantics {k}: {e}")
                for (sk, sinp, at), sbody in states.items():
                    if sk != k or sinp != inp:
                        continue
                    wires, st = simulate(evs, at)
                    want = {}
                    for ln in collapse(sbody):
                        mm = re.match(r"^\|([01]+)> (\S+)$", ln)
                        want[tuple(int(c) for c in mm.group(1))] = parse_amp(mm.group(2))
                    keys = set(want) | {kk for kk, v in st.items() if abs(v) > 1e-9}
                    bad = [kk for kk in keys if abs(want.get(kk, 0) - st.get(kk, 0)) > 1e-7]
                    if bad:
                        errors.append(f"state {k} input {inp} at {at}: mismatch on {bad}: got {st}")
                    else:
                        count("state")
        # xrefs
        n = check_xrefs(text, errors)
        counts["xrefs"] = n
    for k in sorted(counts):
        print(f"  {k:18s} {counts[k]}")
    if errors:
        print(f"\nFAIL: {len(errors)} problem(s)")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("\nOK: every example and stated result checks")


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


def main(argv=None):
    # Make the parser module shared when invoked as a script or imported by tests.
    sys.modules.setdefault("dialect_check", sys.modules[__name__])
    from dialect_check_v02 import main as preflight
    return preflight(argv)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fail as e:
        print("FAIL:", e)
        sys.exit(1)
