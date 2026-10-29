#!/usr/bin/env python3
"""Static inventory of an oracle's callee closure.

Input: the JSON-lines facts written by the `bennett-inventory` pass
(scripts/plugin/BennettSpike.cpp) over the LTO-linked optimised module.

Closure (sound over-approximation):
  * direct call edges as written in the optimised IR;
  * every indirect call site of LLVM function type T may reach every
    address-taken function (defined or declared) whose LLVM function type is
    exactly T.  Sound for defined C: calling a function through a pointer of
    an incompatible type is undefined behaviour (C17 6.5.2.2p9, 6.3.2.3p8),
    and compatible C types lower to the same LLVM function type under
    opaque pointers (all pointers are `ptr`, signedness is not in the type).
    LLVM never changes the signature of an address-taken function (argument
    promotion and dead-argument elimination require all uses to be direct
    calls), so the optimised IR types are the source types' lowering.
  * "address-taken" is LLVM's Function::hasAddressTaken (any use other than
    as a direct callee), which over-approximates the functions whose address
    can flow into a pointer.

Usage: inventory.py <inventory.jsonl> <root> [<root> ...] --out <dir>
"""
import argparse
import collections
import json
import os
import sys

EFFECTS = {
    # name -> (category, note)
    "malloc": ("heap", "allocator"), "calloc": ("heap", "allocator"),
    "realloc": ("heap", "allocator"), "free": ("heap", "allocator"),
    "malloc_usable_size": ("heap", "allocator"),
    "localtime": ("time", "reads TZ database / environment (file I/O in glibc)"),
    "localtime_r": ("time", "reads TZ database"), "time": ("time", "wall clock"),
    "gettimeofday": ("time", "wall clock"), "clock_gettime": ("time", "clock"),
    "getpid": ("process", "pid"), "getenv": ("environment", "process env"),
    "open": ("file", ""), "read": ("file", ""), "write": ("file", ""), "close": ("file", ""),
    "fopen": ("file", ""), "fprintf": ("file", "stdio"), "printf": ("console", "stdio"),
    "puts": ("console", "stdio"), "exit": ("process", "terminates"),
    "abort": ("process", "terminates"), "__errno_location": ("errno", "thread-local errno"),
    "pthread_mutex_lock": ("mutex", ""), "dlopen": ("dynload", ""),
}
PURE_LIBC = {"memcpy", "memmove", "memset", "memcmp", "bcmp", "memchr", "strlen", "strcmp",
             "strncmp", "strchr", "strrchr", "strcspn", "strspn", "strtoull", "snprintf",
             "strnlen"}


def load(path):
    funcs, globs = {}, {}
    with open(path) as f:
        for line in f:
            o = json.loads(line)
            (funcs if o["kind"] == "function" else globs)[o["name"]] = o
    return funcs, globs


def closure(funcs, roots):
    at_by_type = collections.defaultdict(list)
    for n, f in funcs.items():
        if f["address_taken"] and not f["intrinsic"]:
            at_by_type[f["fty"]].append(n)
    reach, work = set(), list(roots)
    edges = collections.defaultdict(set)      # all edges (direct + indirect candidates)
    dedges = collections.defaultdict(set)     # direct only
    while work:
        n = work.pop()
        if n in reach:
            continue
        reach.add(n)
        f = funcs[n]
        if f["decl"]:
            continue
        for c in f["calls"]:
            edges[n].add(c); dedges[n].add(c)
            if c not in reach:
                work.append(c)
        for t in f["icalls"]:
            for c in at_by_type.get(t, []):
                edges[n].add(c)
                if c not in reach:
                    work.append(c)
    return reach, edges, dedges, at_by_type


def sccs(nodes, edges):
    """Tarjan, iterative. Returns list of SCCs (lists) that are cyclic."""
    index, low, onst, st, out = {}, {}, set(), [], []
    counter = [0]
    for root in nodes:
        if root in index:
            continue
        stack = [(root, iter(sorted(edges.get(root, ()))))]
        index[root] = low[root] = counter[0]; counter[0] += 1
        st.append(root); onst.add(root)
        while stack:
            v, it = stack[-1]
            advanced = False
            for w in it:
                if w not in nodes:
                    continue
                if w not in index:
                    index[w] = low[w] = counter[0]; counter[0] += 1
                    st.append(w); onst.add(w)
                    stack.append((w, iter(sorted(edges.get(w, ())))))
                    advanced = True
                    break
                elif w in onst:
                    low[v] = min(low[v], index[w])
            if advanced:
                continue
            stack.pop()
            if stack:
                low[stack[-1][0]] = min(low[stack[-1][0]], low[v])
            if low[v] == index[v]:
                comp = []
                while True:
                    w = st.pop(); onst.discard(w); comp.append(w)
                    if w == v:
                        break
                if len(comp) > 1 or v in edges.get(v, ()):
                    out.append(sorted(comp))
    return out


def summarize(funcs, globs, root):
    reach, edges, dedges, at_by_type = closure(funcs, [root])
    dreach, _, _, _ = closure({k: dict(v, icalls={}) for k, v in funcs.items()}, [root])
    defined = sorted(n for n in reach if not funcs[n]["decl"])
    decls = sorted(n for n in reach if funcs[n]["decl"] and not funcs[n]["intrinsic"])
    S = {"root": root, "functions_reachable": len(reach), "defined": len(defined),
         "external_decls": decls, "direct_only_closure_defined":
         len([n for n in dreach if not funcs[n]["decl"]])}
    tot = collections.Counter()
    ops, fp, vec, intr, ext_sites, loadb, storeb = (collections.Counter() for _ in range(7))
    icall_sites = collections.Counter()
    fp_funcs, vec_funcs, vararg_defs, asm_funcs, atomic_funcs = [], [], [], [], []
    vec_examples = []
    big = []
    gref = collections.Counter()
    for n in defined:
        f = funcs[n]
        tot["blocks"] += f["nbb"]; tot["insts"] += f["ninst"]; tot["mprime"] += f["mprime"]
        tot["value_bits"] += f["value_bits"]
        for k in ("max_value_bits", "max_phis_block", "max_phi_bits_block", "max_call_args",
                  "max_call_arg_bits"):
            if f[k] > tot[k]:
                tot[k] = f[k]; tot[k + "_in"] = n
        tot["alloca_static_bytes"] += f["alloca_static_bytes"]
        tot["alloca_dynamic"] += f["alloca_dynamic"]
        tot["va_start"] += f["va_start"]; tot["va_arg"] += f["va_arg"]
        tot["vararg_call_sites"] += f["vararg_calls"]
        tot["inline_asm"] += f["inline_asm"]; tot["atomics"] += f["atomics"]
        tot["volatile"] += f["volatile"]; tot["switches"] += f["switches"]
        tot["indirectbr"] += f["indirectbr"]; tot["unreachable"] += f["unreachable"]
        tot["invoke"] += f["invoke"]
        tot["direct_call_sites"] += sum(f["calls"].values())
        tot["indirect_call_sites"] += sum(f["icalls"].values())
        ops.update(f["ops"]); fp.update(f["fp"]); vec.update(f["vector"])
        intr.update(f["intrinsics"]); loadb.update(f["load_bytes"]); storeb.update(f["store_bytes"])
        for t, k in f["icalls"].items():
            icall_sites[t] += k
        for c, k in f["calls"].items():
            if funcs.get(c, {}).get("decl"):
                ext_sites[c] += k
        if any(not k.startswith("move:") for k in f["fp"]):
            fp_funcs.append((sum(v for k, v in f["fp"].items() if not k.startswith("move:")), n))
        if f["vector"]:
            vec_funcs.append((sum(f["vector"].values()), n))
            vec_examples += f["vector_examples"][:1]
        if f["vararg"]:
            vararg_defs.append(n)
        if f["inline_asm"]:
            asm_funcs.append(n)
        if f["atomics"]:
            atomic_funcs.append(n)
        big.append((f["ninst"], f["nbb"], f["max_switch_cases"], n))
        for g, k in f["globals"].items():
            gref[g] += k
    S["totals"] = {k: v for k, v in tot.items()}
    S["ops"] = dict(ops.most_common())
    S["load_bytes"] = dict(sorted(loadb.items(), key=lambda kv: int(kv[0])))
    S["store_bytes"] = dict(sorted(storeb.items(), key=lambda kv: int(kv[0])))
    S["fp"] = dict(fp.most_common())
    S["fp_functions"] = [n for _, n in sorted(fp_funcs, reverse=True)]
    S["vector"] = dict(vec.most_common())
    S["vector_functions"] = [n for _, n in sorted(vec_funcs, reverse=True)]
    S["vector_examples"] = vec_examples[:6]
    S["intrinsics"] = dict(intr.most_common())
    S["external_call_sites"] = dict(ext_sites.most_common())
    S["external_effects"] = {n: EFFECTS.get(n, ("pure" if n in PURE_LIBC else "unclassified", ""))
                             for n in decls}
    S["vararg_defined"] = vararg_defs
    S["inline_asm_functions"] = asm_funcs
    S["atomic_functions"] = atomic_funcs
    S["setjmp_longjmp"] = [n for n in reach if "setjmp" in n or "longjmp" in n]
    # heap: SQLite's allocation layer and the libc allocator
    heapnames = [n for n in defined if n.startswith(("sqlite3Malloc", "sqlite3DbMalloc",
                 "sqlite3_malloc", "sqlite3Realloc", "sqlite3DbRealloc", "sqlite3_free",
                 "sqlite3DbFree", "sqlite3MemMalloc", "sqlite3MemFree", "sqlite3MemRealloc",
                 "sqlite3DbNNFree", "sqlite3_realloc", "dbMallocRaw", "dbReallocFinish",
                 "sqlite3PageMalloc", "pcache1Alloc", "pcache1Free"))]
    heap_sites = collections.Counter()
    for n in defined:
        for c, k in funcs[n]["calls"].items():
            if c in heapnames or c in ("malloc", "free", "realloc", "calloc"):
                heap_sites[c] += k
    S["heap_call_sites"] = dict(heap_sites.most_common())
    # indirect calls
    rows = []
    for t, k in icall_sites.most_common():
        cands = [c for c in at_by_type.get(t, []) if c in reach]
        rows.append({"type": t, "sites": k, "candidates": len(at_by_type.get(t, [])),
                     "examples": sorted(cands)[:6]})
    S["indirect_calls"] = rows
    S["address_taken_in_closure"] = sum(1 for n in reach if funcs[n]["address_taken"])
    # recursion
    nodes = set(reach)
    S["sccs_direct"] = sccs(nodes, dedges)
    S["sccs_all"] = sccs(nodes, edges)
    big.sort(reverse=True)
    S["largest_functions"] = [{"name": n, "insts": i, "blocks": b, "max_switch_cases": s}
                              for i, b, s, n in big[:12]]
    # globals referenced by the closure (images in the layout)
    gs = {"count": 0, "bytes": 0, "const_bytes": 0, "mutable_bytes": 0, "zeroinit_bytes": 0,
          "largest": []}
    lst = []
    for g in gref:
        if g not in globs:
            continue
        o = globs[g]
        gs["count"] += 1; gs["bytes"] += o["size"]
        gs["const_bytes" if o["constant"] else "mutable_bytes"] += o["size"]
        if o["zeroinit"]:
            gs["zeroinit_bytes"] += o["size"]
        lst.append((o["size"], g, o["constant"]))
    lst.sort(reverse=True)
    gs["largest"] = [{"name": g, "size": s, "constant": c} for s, g, c in lst[:10]]
    S["globals"] = gs
    S["defined_functions"] = defined
    return S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl")
    ap.add_argument("roots", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    funcs, globs = load(a.jsonl)
    os.makedirs(a.out, exist_ok=True)
    allS = {}
    for r in a.roots:
        if r not in funcs:
            sys.exit(f"root {r} not in module")
        allS[r] = summarize(funcs, globs, r)
    with open(os.path.join(a.out, "inventory.json"), "w") as f:
        json.dump(allS, f, indent=1, sort_keys=True)
    for r, S in allS.items():
        t = S["totals"]
        print(f"== {r}: reachable {S['functions_reachable']} (defined {S['defined']}, "
              f"direct-only closure {S['direct_only_closure_defined']}), blocks {t['blocks']}, "
              f"insts {t['insts']}, icall sites {t['indirect_call_sites']}, "
              f"externals {S['external_decls']}")


if __name__ == "__main__":
    main()
