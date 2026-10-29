#!/usr/bin/env python3
"""Reduce the raw profiles ($WORK/prof/<run>/) to small JSON summaries.

For each run directory (runs.tsv, blocks.tsv, mem.tsv, footprint.json,
table.tsv written by scripts/profile.sh) this computes:

  * IR instructions executed per oracle call (mean/min/max over rowids);
  * an ISA-row estimate per call using the weight model ROW_WEIGHT below
    (stated assumptions; ISA §4.2 rows), and the budget B = max over rowids;
  * the padded structured cost: sum over blocks of (max count over rowids) x
    (rows of the block) -- the cost of a predicated lowering in which every
    block executes as often as its worst rowid (a lower bound for structured
    predication; the general step machine is far above it);
  * divergence: blocks whose count differs across rowids, distinct traces,
    shortest common prefix/suffix with the reference trace;
  * memory sites classified by whether their address sequence / stored
    values / counts differ across rowids;
  * heap (cumulative bytes = the ISA heap budget, since lift.alloc never
    reclaims; peak live), call depth, live locations, stack bytes;
  * bytes touched per call and the union / intersection over all rowids.

Usage: analyze.py <prof dir> <out dir>
"""
import collections
import json
import os
import sys

# ISA rows per IR instruction category (first-order model; REPORT.md §5.1).
ROW_WEIGHT = {
    "load": 2,          # lift.boundscheck + lift.load
    "store": 2,         # lift.boundscheck + lift.store
    "gep": 1,           # lift.binop address arithmetic (constant-folded offsets)
    "phi": 1,           # one lift.parmov slot per phi (upper bound: one row per edge)
    "br": 1,            # qjump / qbranch
    "switch_cases": 0,  # handled per switch block: SWITCH_ROWS
    "call": 1,          # lift.call (the matching lift.ret is the callee's "ret")
    "icall": 9,         # compare-and-branch dispatch over ~16 candidates + lift.call
    "intrinsic": 2,     # min/max/abs/bswap/fshl/ctpop: a few rows each
    "memx": 0,          # counted per byte by the runtime (memx_rows)
    "fp": 150,          # one soft-float lproc call (bennett-arith), first order
    "alloca": 1,        # shadow-stack bump
    "ret": 1,           # lift.ret / lift.retval
    "select": 1, "cmp": 1, "cast": 1, "arith": 1, "muldiv": 1, "other": 1,
    "nop": 0,           # lifetime / assume: removed by the normaliser
}
SWITCH_ROWS = 3         # load label from a constant table + qjumpr


def read_table(path):
    F, B, M, V = {}, {}, {}, {}
    cats = None
    for line in open(path):
        p = line.rstrip("\n").split("\t")
        if p[0] == "#blocks":
            cats = p[4:]
        elif p[0] == "F":
            F[int(p[1])] = {"name": p[2], "mprime": int(p[3]), "alloca": int(p[4])}
        elif p[0] == "B":
            vals = list(map(int, p[4:]))
            c = dict(zip(cats, vals))
            rows = sum(ROW_WEIGHT[k] * v for k, v in c.items())
            if c["switch_cases"]:
                rows += SWITCH_ROWS
            B[int(p[1])] = {"fid": int(p[2]), "ninst": int(p[3]), "cats": c, "rows": rows}
        elif p[0] == "M":
            M[int(p[1])] = {"bid": int(p[2]), "kind": p[3], "size": int(p[4])}
        elif p[0] == "V":
            V[int(p[1])] = {"bid": int(p[2]), "cat": p[3]}
    return F, B, M, V


def tsv(path):
    lines = open(path).read().splitlines()
    head = lines[0].split("\t")
    return [dict(zip(head, l.split("\t"))) for l in lines[1:]]


def stats(xs):
    xs = list(xs)
    return {"mean": sum(xs) / len(xs), "min": min(xs), "max": max(xs)}


def analyze(d):
    F, B, M, V = read_table(os.path.join(d, "table.tsv"))
    runs = tsv(os.path.join(d, "runs.tsv"))
    blocks = tsv(os.path.join(d, "blocks.tsv"))
    mem = tsv(os.path.join(d, "mem.tsv"))
    foot = json.load(open(os.path.join(d, "footprint.json")))
    I = lambda r, k: int(r[k])
    S = {"run": os.path.basename(d.rstrip("/")), "rowids": len(runs)}
    S["mismatches"] = sum(1 for r in runs if r["result"] != r["ref"])
    S["matches"] = sum(1 for r in runs if r["result"] == "1")
    S["ir_insts"] = stats(I(r, "insts") for r in runs)
    # rows: ratio from the aggregate, applied per run (block mix is near-identical across rowids)
    sum_inst = sum(int(b["sum"]) * B[int(b["bid"])]["ninst"] for b in blocks)
    sum_rows = sum(int(b["sum"]) * B[int(b["bid"])]["rows"] for b in blocks)
    ratio = sum_rows / sum_inst
    S["rows_per_ir_inst"] = ratio
    per_run_rows = [I(r, "insts") * ratio + I(r, "memx_rows") for r in runs]
    S["isa_rows"] = stats(per_run_rows)
    S["B_estimate"] = max(per_run_rows)
    padded = sum(int(b["max"]) * B[int(b["bid"])]["rows"] for b in blocks)
    S["padded_structured_rows"] = padded + max(I(r, "memx_rows") for r in runs)
    var = [b for b in blocks if b["min"] != b["max"]]
    S["blocks_executed"] = len(blocks)
    S["blocks_varying"] = len(var)
    S["rows_varying"] = sum((int(b["max"]) - int(b["min"])) * B[int(b["bid"])]["rows"] for b in var)
    fns = {B[int(b["bid"])]["fid"] for b in blocks}
    S["functions_executed"] = len(fns)
    S["functions_executed_names"] = sorted(F[f]["name"] for f in fns)
    # ISA §3.7: the location stack is monotonic (records are history), so
    # stack_limit >= sum over every dynamic call of R_f = 3 + m'_f cells.
    entry = {}
    for bid, b in B.items():
        if b["fid"] not in entry or bid < entry[b["fid"]]:
            entry[b["fid"]] = bid
    bmax = {int(b["bid"]): int(b["max"]) for b in blocks}
    bsum = {int(b["bid"]): int(b["sum"]) for b in blocks}
    S["dynamic_calls_mean"] = sum(bsum.get(e, 0) for e in entry.values()) / nrun if (nrun := len(runs)) else 0
    S["monotonic_stack_cells_max"] = sum(bmax.get(e, 0) * (3 + F[f]["mprime"]) for f, e in entry.items())
    S["monotonic_stack_cells_mean"] = sum(bsum.get(e, 0) * (3 + F[f]["mprime"]) for f, e in entry.items()) / nrun
    S["static_rows_of_executed_functions"] = sum(
        v["rows"] for v in B.values() if v["fid"] in fns)
    dyn = collections.Counter()
    for b in blocks:
        for k, v in B[int(b["bid"])]["cats"].items():
            dyn[k] += int(b["sum"]) * v
    S["dynamic_by_category_mean"] = {k: v / nrun for k, v in dyn.most_common()}
    varyfn = collections.Counter()
    for b in var:
        varyfn[F[B[int(b["bid"])]["fid"]]["name"]] += (int(b["max"]) - int(b["min"])) * B[int(b["bid"])]["rows"]
    S["varying_rows_by_function"] = dict(varyfn.most_common(15))
    # memory sites
    cls = collections.Counter(); sites = collections.Counter(); afn = collections.Counter()
    for m in mem:
        key = ("addr" if m["addr_differs"] == "1" else "-") + "/" + \
              ("val" if m["val_differs"] == "1" else "-") + "/" + \
              ("cnt" if m["cnt_differs"] == "1" else "-")
        cls[key] += int(m["maxcnt"]); sites[key] += 1
        if m["addr_differs"] == "1":
            afn[F[B[M[int(m["mid"])]["bid"]]["fid"]]["name"]] += int(m["maxcnt"])
    S["mem_dynamic_ops_by_class"] = dict(cls)
    S["mem_sites_by_class"] = dict(sites)
    S["addr_varying_ops_by_function"] = dict(afn.most_common(15))
    # resources
    for k in ("heap_bytes", "heap_peak_live", "heap_allocs", "heap_frees", "heap_live_at_exit",
              "maxdepth", "maxlocs", "maxsbytes", "native_stack", "dyn_alloca_bytes",
              "touched_any", "touched_r", "touched_w", "touched_heap", "touched_stack",
              "touched_image", "touched_other", "n_ld", "n_st", "b_ld", "b_st", "n_memx",
              "b_memx", "memx_rows", "trace_len"):
        S[k] = stats(I(r, k) for r in runs)
    S["distinct_traces"] = len({r["trace_hash"] for r in runs})
    S["min_common_prefix"] = min(I(r, "prefix") for r in runs)
    S["min_common_suffix"] = min(I(r, "suffix") for r in runs)
    S["footprint"] = foot
    # ---- differential taint: values and addresses that differ across rowids
    vp = os.path.join(d, "val.tsv")
    if os.path.exists(vp):
        vals = tsv(vp)
        qv = collections.Counter(); cv = collections.Counter(); qfn = collections.Counter()
        for v in vals:
            meta = V[int(v["vid"])]
            w = ROW_WEIGHT.get(meta["cat"], 1)
            if meta["cat"] == "switch_cases":
                w = SWITCH_ROWS
            n = int(v["maxcnt"])
            if v["val_differs"] == "1" or v["cnt_differs"] == "1":
                qv[meta["cat"]] += n
                qfn[F[B[meta["bid"]]["fid"]]["name"]] += n
            else:
                cv[meta["cat"]] += n
        S["values_varying_by_category"] = dict(qv.most_common())
        S["values_invariant_by_category"] = dict(cv.most_common())
        S["values_varying_total"] = sum(qv.values())
        S["values_invariant_total"] = sum(cv.values())
        S["values_varying_by_function"] = dict(qfn.most_common(20))
    ap = os.path.join(d, "addrsets.tsv")
    if os.path.exists(ap):
        aset = {int(a["mid"]): a for a in tsv(ap)}
        memd = {int(m["mid"]): m for m in mem}
        rows = []
        for mid, m in memd.items():
            if m["addr_differs"] != "1":
                continue
            a = aset.get(mid, {"distinct_addr": "0", "distinct_src": "0", "memx_max_bytes": "0"})
            meta = M[mid]
            rows.append({"mid": mid, "fn": F[B[meta["bid"]]["fid"]]["name"], "kind": meta["kind"],
                         "size": meta["size"], "maxcnt": int(m["maxcnt"]),
                         "distinct_dst": int(a["distinct_addr"]), "distinct_src": int(a["distinct_src"]),
                         "memx_max_bytes": int(a["memx_max_bytes"]),
                         "val_differs": m["val_differs"] == "1"})
        rows.sort(key=lambda r: -r["maxcnt"] * max(r["distinct_dst"], r["distinct_src"]))
        S["superposed_address_sites"] = rows
    return S


def main():
    prof, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    allS = {}
    for name in sorted(os.listdir(prof)):
        d = os.path.join(prof, name)
        if not os.path.isfile(os.path.join(d, "runs.tsv")):
            continue
        S = analyze(d)
        allS[name] = S
        if S["mismatches"]:
            sys.exit(f"{name}: {S['mismatches']} oracle mismatches")
        print(f"{name:28s} rowids={S['rowids']:5d} ir={S['ir_insts']['mean']:10.0f} "
              f"rows={S['isa_rows']['mean']:10.0f} B={S['B_estimate']:10.0f} "
              f"padded={S['padded_structured_rows']:10.0f} heap={S['heap_bytes']['max']:8d} "
              f"depth={S['maxdepth']['max']:3d} fns={S['functions_executed']:4d} "
              f"varyblk={S['blocks_varying']:5d}/{S['blocks_executed']:5d} traces={S['distinct_traces']}")
    with open(os.path.join(out, "profiles.json"), "w") as f:
        json.dump(allS, f, indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
