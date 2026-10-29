#!/usr/bin/env python3
"""First-order resource estimates for rung 4 (REPORT.md §7).

Inputs: results/profiles.json (scripts/analyze.py) and results/inventory.json
(scripts/inventory.py).  Every constant below is an assumption, stated here
and in the report; change them and rerun.

Usage: cost.py <results dir>
"""
import json
import math
import sys

# ---------------------------------------------------------------- assumptions
B_MARGIN = 1.10            # budget over the largest observed step count (sampled N)
F_BITS = 4                 # fault register width (ISA §5.4: F >= 4)
INTERP_ROWS_PER_S = [1e5, 1e6, 1e7]   # reversible interpreter speeds (rows/s, one core)
CORES = 32                 # branch enumeration is embarrassingly parallel over basis inputs
PTR = 64
W_CELL = 128               # ISA §3.7 cell width = max(P, Sc, Did, W_max); i128 locations exist
ROW_SLOT_BITS = 700        # widest frame write set: lift.call with 13 args (608 bits) + 3 counters
# Toffoli costs (Bennett.jl v1 BENCHMARKS.md and standard constructions)
T_ADD64 = 128              # 64-bit add/compare, compute + uncompute
T_MOVE64 = 64              # 64-bit controlled copy/exchange (a predicated move)
T_MUL64 = 20000            # 64x64 multiply (v1: i32 x i32 = 5024 Toffoli; x4)
TOFFOLI_TIME = 170         # example-surface-code-d17: ccx time (illustrative units)
TARGET = "bennett-targets/targets/example-surface-code-d17.json (illustrative)"


def grover_iterations(n, m):
    theta = math.asin(math.sqrt(m / n))
    return max(1, round(math.pi / (4 * theta) - 0.5))


def log2c(x):
    return max(1, math.ceil(math.log2(max(2, x))))


def reference_construction(P, inv, n_image, N):
    """ISA §3.6/§5.2 reference step machine, no structure recovery."""
    tot = inv["totals"]
    ratio = P["rows_per_ir_inst"]
    n_rows = int(tot["insts"] * ratio)                     # index space (sound closure)
    pbits = log2c(n_rows + 1)
    B = P["B_estimate"] * B_MARGIN
    globals_bytes = inv["globals"]["bytes"]
    heap = P["heap_bytes"]["max"]
    shadow = P["maxsbytes"]["max"]
    H = log2c(heap + globals_bytes + shadow + 4096)
    A_img = log2c(n_image)
    A_tab = log2c(inv["globals"]["count"] + P["heap_allocs"]["max"] + 1)
    stack_cells = P["monotonic_stack_cells_max"] * B_MARGIN
    mem_static = sum(int(v) for k, v in inv["load_bytes"].items()) + \
        sum(int(v) for k, v in inv["store_bytes"].items())
    other_static = n_rows - 2 * mem_static
    # qubits
    q = {
        "mem (2^H bytes x 8)": 2 ** H * 8,
        "image interface region (2^A x 8)": 2 ** A_img * 8,
        "register file (all locations of the closure)": tot["value_bits"],
        "location stack (monotonic, cells x W_cell)": stack_cells * W_CELL,
        "alloctab (2^A_tab x (2 ptr + 2))": 2 ** A_tab * (2 * PTR + 2),
        "step history (B frames)": B * (2 * pbits + 1 + ROW_SLOT_BITS),
    }
    # Toffoli per step: dispatch + every row under its predicate
    per_mem_row = (2 ** H + 2 ** A_img) * 9 + 2 ** A_tab * 4 * PTR
    t_step = n_rows * pbits * 2 + mem_static * per_mem_row + other_static * T_ADD64
    t_oracle = 2 * B * t_step
    return {"n_rows": n_rows, "P": pbits, "B": B, "H": H, "A_image": A_img, "A_tab": A_tab,
            "stack_cells": stack_cells, "static_mem_rows": mem_static,
            "qubits": q, "qubits_total": sum(q.values()),
            "toffoli_per_step": t_step, "toffoli_per_oracle": t_oracle}


def structured(P, n_image, Pbig=None, page=4096):
    """Structure-recovered estimate from differential taint (padded runs).

    P: exhaustive padded run (all rowids; exact address-set sizes D per site).
    Pbig: sampled padded run at the target N (per-site counts and any site that
    only appears there).  D per site = max of the two, except the page read
    from the image (memdbRead), whose D is the number of pages of the image."""
    if Pbig is not None:
        sites = {s["mid"]: dict(s) for s in P["superposed_address_sites"]}
        for s in Pbig["superposed_address_sites"]:
            if s["mid"] in sites:
                t = sites[s["mid"]]
                t["maxcnt"] = max(t["maxcnt"], s["maxcnt"])
                t["diff_inst"] = max(t.get("diff_inst", t["maxcnt"]), s.get("diff_inst", s["maxcnt"]))
                for k in ("distinct_dst", "distinct_src", "memx_max_bytes"):
                    t[k] = max(t[k], s[k])
            else:
                sites[s["mid"]] = dict(s)
        P = dict(P, superposed_address_sites=list(sites.values()))
        for k in ("values_varying_by_category", "value_instances_differing_by_category"):
            if k not in P:
                continue
            merged = dict(P[k])
            for c, n in Pbig[k].items():
                merged[c] = max(merged.get(c, 0), n)
            P[k] = merged
        P["values_varying_total"] = max(P["values_varying_total"], Pbig["values_varying_total"])
        if "value_instances_differing_total" in P:
            P["value_instances_differing_total"] = max(P["value_instances_differing_total"],
                                                       Pbig["value_instances_differing_total"])
        P["rows_varying"] = max(P["rows_varying"], Pbig["rows_varying"])
    vc = P.get("value_instances_differing_by_category", P["values_varying_by_category"])
    t_val = 0
    for cat, n in vc.items():
        if cat == "muldiv":
            t_val += n * T_MUL64
        elif cat in ("load", "phi", "cast", "select", "alloca", "call", "other"):
            t_val += n * T_MOVE64
        else:
            t_val += n * T_ADD64
    t_pred = P["rows_varying"] * T_MOVE64
    t_mem = 0
    qrom_pages = 0
    for s in P["superposed_address_sites"]:
        n = s.get("diff_inst", s["maxcnt"])   # instances whose address differs from the reference
        if s["kind"] in ("memcpy", "memmove"):
            nbytes = s["memx_max_bytes"]
            if s["distinct_src"] > 1:
                if s["fn"] == "memdbRead":     # page read from the image: QROM over pages
                    D = max(s["distinct_src"], n_image // page)
                    qrom_pages = max(qrom_pages, D)
                    t_mem += n * 2 * D
                else:
                    t_mem += n * 2 * s["distinct_src"] * (1 + 8 * nbytes)
            if s["distinct_dst"] > 1:
                t_mem += n * 2 * s["distinct_dst"] * (1 + 8 * nbytes)
        elif s["kind"] == "memset":
            t_mem += n * 2 * s["distinct_dst"] * (1 + 8 * s["memx_max_bytes"])
        else:
            D = s["distinct_dst"]
            t_mem += n * 2 * D * (1 + 8 * s["size"])
    written = sum(P["footprint"]["union_written"])
    q = {"superposed memory (union of written bytes x 8)": written * 8,
         "garbage, no pebbling (differing value instances x 64)":
             P.get("value_instances_differing_total", P["values_varying_total"]) * 64}
    return {"toffoli_values": t_val, "toffoli_predication": t_pred, "toffoli_memory": t_mem,
            "toffoli_per_oracle": 2 * (t_val + t_pred + t_mem), "qrom_pages": qrom_pages,
            "qubits": q, "qubits_total": sum(q.values())}


def main():
    res = sys.argv[1]
    prof = json.load(open(f"{res}/profiles.json"))
    inv = json.load(open(f"{res}/inventory.json"))["oracle_on_image"]
    out = {"assumptions": {k: v for k, v in globals().items() if k.isupper()}}
    # (a) oracle verification at N = 2^10 and (b) Grover at N = 2^8
    for n, key in ((1024, "deser-N1024"), (256, "deser-N256")):
        P = prof[key]
        B = P["B_estimate"] * B_MARGIN
        rows_per_input = 2 * B                       # forward + prefix reversal
        full_D = n * 2 * 2 ** F_BITS                 # every x, t, e
        e = {"B": B, "rows_per_basis_input": rows_per_input,
             "domain_full": full_D, "domain_shared": n}
        for s in INTERP_ROWS_PER_S:
            e[f"wall_s_full_D_at_{s:.0e}_rows_per_s_{CORES}_cores"] = full_D * rows_per_input / s / CORES
            e[f"wall_s_per_x_at_{s:.0e}_rows_per_s_{CORES}_cores"] = n * rows_per_input / s / CORES
        if n == 256:
            m = P["matches"]
            k = grover_iterations(n, m)
            e["marked"] = m
            e["grover_iterations"] = k
            e["oracle_branch_runs"] = k * n        # one run per basis x (t in |->: shared)
            for s in INTERP_ROWS_PER_S:
                e[f"grover_wall_s_at_{s:.0e}_rows_per_s_{CORES}_cores"] = k * n * rows_per_input / s / CORES
        out[f"verify_N{n}"] = e
    # (c) N = 2^20
    P = prof["deser-N1048576-s4099"]
    Pp = prof.get("deser-N1048576-s4099-pad512", P)
    n_image = P["footprint"]["image_bytes"]
    N = 1 << 20
    ref = reference_construction(P, inv, n_image, N)
    st = structured(prof["deser-N1024-pad512"], n_image, prof.get("deser-N1048576-s4099-pad512"))
    m = 11698                                   # matches of the predicate at N = 2^20 (verify run)
    k_m = grover_iterations(N, m)
    k_1 = grover_iterations(N, 1)
    out["N2^20"] = {"reference": ref, "structured": st, "grover_iterations_M=11698": k_m,
                    "grover_iterations_M=1": k_1}
    for name, t in (("reference", ref["toffoli_per_oracle"]), ("structured", st["toffoli_per_oracle"])):
        out["N2^20"][f"{name}_toffoli_total_M=11698"] = t * k_m
        out["N2^20"][f"{name}_toffoli_total_M=1"] = t * k_1
        out["N2^20"][f"{name}_time_units_sequential_M=1"] = t * k_1 * TOFFOLI_TIME
    with open(f"{res}/cost.json", "w") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=float)
    print(json.dumps(out, indent=1, sort_keys=True, default=float))


if __name__ == "__main__":
    main()
