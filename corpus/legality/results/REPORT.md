# Bennett legality spike results

ABI 0.2 follow-up (2026-10-30, dialect 0.2.9): [machine receipt](abi-0.2-relays.json).
All 69 cases rerun on LLVM 18/23 at llc O0/O3; only `spec-sem2-adj` and
`spec-sem2-compute` change (exit 87 → 0). The other 67 cases retain byte-identical
canonical traces, exits, baseline issues and O3 comparisons. All 1,386 P2 cells
with stored results match; the full rerun contains 1,518 cells including the six
`spec-*` additions. Each repaired case passes L1–L6 in all 11 LLVM-18 pipelines
and all 9 supported LLVM-23 pipelines (the existing Os/Oz opt refusals remain).
The historical P1/P3 spike tables below retain their original scope and date.

Generated 2026-10-28T22:32:08+0100 by `legality-harness-v3`; 170163 recorded matrix cells over 56 corpus cases (plus 3 harness seeds and 4 negative controls, reported separately).

Outcomes: **FAIL** is the only legality counterexample. `env-error` (native build impossible in this standalone host environment, by the evidence rule in Harness notes), `non-preserving` (documented single passes that by design do not preserve a standalone program, confirmed per cell), and `precondition` (pass run without its documented prerequisite; rerun with the prerequisite passes) are recorded with evidence and never hide a trace difference, a guard fault, BADHANDLE, a forbidden attribute or a missing marker external. `noop` means identical IR after all checks pass.

## 1. Corpus matrix (cases/ only)

| LLVM / suite | pass | FAIL | noop | opt-error | env-error | non-preserving | precondition |
|---|---:|---:|---:|---:|---:|---:|---:|
| 18/P1 | 2900 | 2154 | 27972 | 1248 | 999 | 336 | 7 |
| 18/P2 | 501 | 61 | 54 | 0 | 0 | 0 | 0 |
| 18/P3 | 8579 | 871 | 1748 | 2 | 0 | 0 | 0 |
| 20/P1 | 3087 | 2295 | 29828 | 1240 | 1511 | 336 | 7 |
| 20/P2 | 501 | 61 | 54 | 0 | 0 | 0 | 0 |
| 20/P3 | 8345 | 850 | 2005 | 0 | 0 | 0 | 0 |
| 23/P1 | 3402 | 2403 | 31203 | 2915 | 1622 | 336 | 7 |
| 23/P2 | 401 | 49 | 54 | 112 | 0 | 0 | 0 |
| 23/P3 | 8793 | 736 | 1617 | 54 | 0 | 0 | 0 |

Harness seeds (must be all pass/noop apart from env-error/non-preserving/precondition cells of instrumentation passes):

| LLVM / suite | pass | FAIL | noop | opt-error | env-error | non-preserving | precondition |
|---|---:|---:|---:|---:|---:|---:|---:|
| 18/P1 | 110 | 0 | 1603 | 132 | 51 | 12 | 0 |
| 18/P2 | 30 | 0 | 3 | 0 | 0 | 0 | 0 |
| 18/P3 | 456 | 0 | 144 | 0 | 0 | 0 | 0 |
| 20/P1 | 116 | 0 | 1700 | 144 | 80 | 12 | 0 |
| 20/P2 | 30 | 0 | 3 | 0 | 0 | 0 | 0 |
| 20/P3 | 421 | 0 | 179 | 0 | 0 | 0 | 0 |
| 23/P1 | 128 | 0 | 1808 | 210 | 86 | 12 | 0 |
| 23/P2 | 24 | 0 | 3 | 6 | 0 | 0 | 0 |
| 23/P3 | 458 | 0 | 139 | 3 | 0 | 0 | 0 |

## 2. Negative controls (must be detected)

| Control | intended | pipeline | LLVM 18 | LLVM 20 | LLVM 23 | matrix cells detecting intended check |
|---|---|---|---|---|---|---|
| `control-handle-deref` | L3 | `no-op-module` | detected: **yes** (L1:yes, L2:no, L3:yes, L4:no, L5:yes) | detected: **yes** (L1:yes, L2:no, L3:yes, L4:no, L5:yes) | detected: **yes** (L1:yes, L2:no, L3:yes, L4:no, L5:yes) | 2448/2701 |
| `control-memory-none` | L1 | `default<O3>` | detected: **yes** (L1:yes, L2:no, L3:no, L4:no, L5:yes) | detected: **yes** (L1:yes, L2:no, L3:no, L4:no, L5:yes) | detected: **yes** (L1:yes, L2:no, L3:no, L4:no, L5:yes) | 1069/2701 |
| `control-readonly` | L1 | `function(loop-simplify,lcssa,loop-mssa(licm))` | detected: **yes** (L1:yes, L2:no, L3:no, L4:no, L5:yes) | detected: **yes** (L1:yes, L2:no, L3:no, L4:no, L5:yes) | detected: **yes** (L1:yes, L2:no, L3:no, L4:no, L5:yes) | 1066/2701 |
| `control-region-twin` | L4 | `mergefunc` | detected: **yes** (L1:no, L2:no, L3:no, L4:yes, L5:no) | detected: **yes** (L1:no, L2:no, L3:no, L4:yes, L5:no) | detected: **yes** (L1:no, L2:no, L3:no, L4:yes, L5:no) | 34/2701 |

## 3. P2 standard pipelines, per case

Cell: `ok` = pass/noop on every major run; otherwise outcome per major.

| Case | `default<O0>` | `default<O1>` | `default<O2>` | `default<O3>` | `default<Os>` | `default<Oz>` | `lto-pre-link<O3>` | `lto<O3>` | `thinlto-pre-link<O3>` | `thinlto<O3>` | `default<O3>,default<O3>,default<O3>` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `c-is-constant-budget` | ok | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:opt-error | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:opt-error | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 |
| `c-memcpy-handle-int` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `c-objectsize-count` | ok | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:opt-error | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:opt-error | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 |
| `c-pie-reltable-region` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `c-program-mixed` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `c-pure-attr-wrapper` | ok | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:opt-error | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:opt-error | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 |
| `c-unprototyped-decl` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `cfg-callsite-splitting` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `cfg-hoist-sink-common` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `cfg-jump-threading` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `cfg-sink-different-callees` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `cfg-switch-op-table` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `cfg-unreachable-after-marker` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `dbg-memcpy-handle-int` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `dbg-region-operands` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `eh-invoke-markers` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `fp-rot-exact-fold` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `fp-rot-fastmath-reassoc` | 18:FAIL:L5<br>20:FAIL:L5<br>23:FAIL:L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:opt-error | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:opt-error | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 |
| `fp-rot-fmuladd-fold` | ok | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:opt-error | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:opt-error | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 |
| `fp-rot-nan-fold` | ok | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:opt-error | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:opt-error | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 |
| `inline-always-into-region` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `inline-helper-markers` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `inline-partial` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `ipo-argpromo-dae` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `ipo-attributor-function-attrs` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `ipo-globalopt-region-bool` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `ipo-internalize-globaldce` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `ipo-ipsccp-funcspec-region` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `loop-deletion-marker-only` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `loop-fuse-distribute` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `loop-idiom-handle-table` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `loop-licm-invariant-marker` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `loop-rotate-peel` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `loop-unroll-gates` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `loop-unswitch-nontrivial` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `loop-vectorize-gates` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `meas-repeat-until-success` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `meas-select-phi-switch` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `meas-speculation` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `region-ctrl-variadic` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `region-env-escape` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `region-fnptr-array-index` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `region-global-state` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `region-hotcoldsplit` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `region-inplace-selfinverse` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `region-internal-strip` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `region-iroutliner` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `region-mergefunc-twins` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `region-mergefunc-unnamed-addr` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `region-recursive-tre` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `region-select-two-way` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `region-switch-fnptr-table` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `val-cse-duplicate-markers` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `val-memcpy-handle-int` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `val-sroa-handle-table` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| `val-unused-results` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| seed `seed-ctrl-env` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| seed `seed-loop` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| seed `seed-straight` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |
| control `control-handle-deref` | 18:FAIL:L1,L3,L5<br>20:FAIL:L1,L3,L5<br>23:FAIL:L1,L3,L5 | 18:FAIL:L1,L3,L5<br>20:FAIL:L1,L3,L5<br>23:FAIL:L1,L3,L5 | 18:FAIL:L1,L3,L5<br>20:FAIL:L1,L3,L5<br>23:FAIL:L1,L3,L5 | 18:FAIL:L1,L3,L5<br>20:FAIL:L1,L3,L5<br>23:FAIL:L1,L3,L5 | 18:FAIL:L1,L3,L5<br>20:FAIL:L1,L3,L5<br>23:opt-error | 18:FAIL:L1,L3,L5<br>20:FAIL:L1,L3,L5<br>23:opt-error | 18:FAIL:L1,L3,L5<br>20:FAIL:L1,L3,L5<br>23:FAIL:L1,L3,L5 | 18:FAIL:L1,L3,L5<br>20:FAIL:L1,L3,L5<br>23:FAIL:L1,L3,L5 | 18:FAIL:L1,L3,L5<br>20:FAIL:L1,L3,L5<br>23:FAIL:L1,L3,L5 | 18:FAIL:L1,L3,L5<br>20:FAIL:L1,L3,L5<br>23:FAIL:L1,L3,L5 | 18:FAIL:L1,L3,L5<br>20:FAIL:L1,L3,L5<br>23:FAIL:L1,L3,L5 |
| control `control-memory-none` | ok | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:opt-error | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:opt-error | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 |
| control `control-readonly` | ok | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:opt-error | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:opt-error | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 | 18:FAIL:L1,L5<br>20:FAIL:L1,L5<br>23:FAIL:L1,L5 |
| control `control-region-twin` | ok | ok | ok | ok | 23:opt-error | 23:opt-error | ok | ok | ok | ok | ok |

## 4. Distinct FAILs (280)

Deduplicated by case + pass + failed-check signature (P3: by case + sequence). Corpus first, then seeds, then controls (controls are expected to FAIL).

### corpus

- **`c-is-constant-budget`** (probe) — inherited `(any pass; behaviour identical to its input = default<O3> output; 355 pass/mode cells)` — **L1,L5** — LLVM 18,20,23; modes post-O3; 933 cells
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 374952223c619e48de26`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt -passes=alloc-token /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/39ad417e6cc2a4e612089013ada767de26913d3fb18c79b00101b677785add6d/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/374952223c619e48de26/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P1 `attributor` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 8c05aa9521faa7c1fa75`; opt: `/usr/lib/llvm-18/bin/opt -passes=attributor /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/8c05aa9521faa7c1fa75/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P1 `cgscc(attributor-cgscc)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay b2cee9c4b0cc604ed7e1`; opt: `/usr/lib/llvm-18/bin/opt '-passes=cgscc(attributor-cgscc)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/b2cee9c4b0cc604ed7e1/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P1 `scc-oz-module-inliner` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 538d10bbac58589c1104`; opt: `/usr/lib/llvm-18/bin/opt -passes=scc-oz-module-inliner /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/538d10bbac58589c1104/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P1 `strip` — **L1,L4,L5** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region symbols changed body->__unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): body; first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 2cb4aac3020bdaac5b9a`; opt: `/usr/lib/llvm-18/bin/opt -passes=strip /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/1bdf5d71f94109d30be2fd0590538c8d4d3f2955a06367256067a37d6194a481/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/2cb4aac3020bdaac5b9a/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:__unnamed_1 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P1 `strip-nondebug` — **L1,L4,L5** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region symbols changed body->__unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): body; first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay e99c98387baaac873108`; opt: `/usr/lib/llvm-18/bin/opt -passes=strip-nondebug /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/1bdf5d71f94109d30be2fd0590538c8d4d3f2955a06367256067a37d6194a481/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/e99c98387baaac873108/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:__unnamed_1 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P2 `default<O1>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay ad741199336976a2ea81`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O1>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/ad741199336976a2ea81/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P2 `default<O2>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 2ba53731655bf93b0579`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O2>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/2ba53731655bf93b0579/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P2 `default<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 5e2686aecbdc9b35315f`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/5e2686aecbdc9b35315f/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P2 `default<O3>,default<O3>,default<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay e4d5e0c58448cbdf7707`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O3>,default<O3>,default<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/e4d5e0c58448cbdf7707/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P2 `default<Os>` — **L1,L5** — LLVM 18,20; modes raw; 2 cells
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 6d73c885d6bcca657338`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<Os>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/6d73c885d6bcca657338/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P2 `default<Oz>` — **L1,L5** — LLVM 18,20; modes raw; 2 cells
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay d65e52e305c0225e5938`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<Oz>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/d65e52e305c0225e5938/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P2 `lto-pre-link<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 6fca52eb081944e3fa97`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lto-pre-link<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/6fca52eb081944e3fa97/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P2 `lto<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 37f5a99839bdbb2076d7`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lto<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/37f5a99839bdbb2076d7/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P2 `thinlto-pre-link<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 0e7a8fc97578521c428b`; opt: `/usr/lib/llvm-18/bin/opt '-passes=thinlto-pre-link<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/0e7a8fc97578521c428b/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P2 `thinlto<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay ce55df7b4ae8c104342b`; opt: `/usr/lib/llvm-18/bin/opt '-passes=thinlto<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/ce55df7b4ae8c104342b/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `99 random sequences, each containing a pass that FAILs alone on this case (attributor 46, cgscc(attributor-cgscc) 40, scc-oz-module-inliner 21)` — **L1,L5** — LLVM 18,20,23; modes seq-0002,seq-0003,seq-0006,seq-0010,seq-0012,seq-0014,seq-0015,seq-0016,seq-0018,seq-0020,seq-0025,seq-0026,seq-0027,seq-0031,seq-0032,seq-0035,seq-0036,seq-0038,seq-0041,seq-0044,seq-0048,seq-0050,seq-0054,seq-0056,seq-0061,seq-0065,seq-0066,seq-0069,seq-0072,seq-0074,seq-0075,seq-0079,seq-0081,seq-0082,seq-0083,seq-0086,seq-0089,seq-0093,seq-0096,seq-0097,seq-0099,seq-0100,seq-0102,seq-0103,seq-0107,seq-0109,seq-0112,seq-0117,seq-0118,seq-0119,seq-0120,seq-0122,seq-0123,seq-0124,seq-0125,seq-0126,seq-0128,seq-0130,seq-0134,seq-0138,seq-0139,seq-0140,seq-0141,seq-0142,seq-0143,seq-0144,seq-0145,seq-0147,seq-0148,seq-0149,seq-0150,seq-0152,seq-0160,seq-0161,seq-0165,seq-0167,seq-0174,seq-0176,seq-0180,seq-0181,seq-0183,seq-0185,seq-0186,seq-0187,seq-0188,seq-0194,seq-0195,seq-0198,seq-0199; 99 cells
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 26804aa95928ae1f9b6c`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=attributor,function(print<scalar-evolution>),function(consthoist),function(view-dom),inliner-wrapper-no-mandatory-first,invalidate<all>,function(correlated-propagation),print-callgraph-sccs,function(mergereturn),function(flatten-cfg),function(loop-versioning),hipstdpar-interpose-alloc,function(instsimplify),function(print<stack-lifetime>),function(lower-switch),cgscc(attributor-light-cgscc),function(print<func-properties>),function(load-store-vectorizer),function(lower-switch),function(objc-arc),function(print<stack-lifetime>),embed-bitcode,function(loop(simple-loop-unswitch)),function(ee-instrument),function(instcombine<no-verify-fixpoint>),print-ir-similarity,extract-blocks,cgscc(no-op-cgscc),function(guard-widening),function(objc-arc),function(print<demanded-bits>),print<dxil-metadata>,function(lower-switch),function(dot-cfg),function(hardware-loops),iroutliner,deadargelim,always-inline,function(print<loops>),function(lower-invoke)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/26804aa95928ae1f9b6c/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `73 random sequences, each containing a pass that FAILs alone on this case (strip 44, strip-nondebug 35, cgscc(attributor-cgscc) 8, attributor 3, scc-oz-module-inliner 3)` — **L1,L4,L5** — LLVM 18,20,23; modes seq-0002,seq-0005,seq-0006,seq-0007,seq-0009,seq-0012,seq-0018,seq-0019,seq-0025,seq-0027,seq-0031,seq-0039,seq-0043,seq-0044,seq-0046,seq-0049,seq-0051,seq-0053,seq-0055,seq-0056,seq-0057,seq-0061,seq-0062,seq-0063,seq-0067,seq-0072,seq-0077,seq-0080,seq-0081,seq-0082,seq-0090,seq-0091,seq-0093,seq-0095,seq-0101,seq-0103,seq-0104,seq-0115,seq-0116,seq-0120,seq-0121,seq-0122,seq-0125,seq-0126,seq-0130,seq-0131,seq-0136,seq-0141,seq-0144,seq-0147,seq-0155,seq-0160,seq-0162,seq-0164,seq-0166,seq-0169,seq-0172,seq-0173,seq-0175,seq-0179,seq-0182,seq-0190,seq-0192,seq-0193,seq-0194; 73 cells
  - diagnosis: region symbols changed body->__unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_2; region is not a definition (missing, declaration, or alias): body; first trace difference: -REVERSIBLE F:body 1000 / +REVERSIBLE F:__unnamed_2 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 111b1e6ef9e4ed55a9ee`; opt: `/usr/lib/llvm-18/bin/opt '-passes=canonicalize-aliases,function(tailcallelim),function(print<access-info>),function(print-cfg-sccs),always-inline,function(instsimplify),function(loop(loop-predication)),function(print<branch-prob>),function(assume-simplify),strip-nonlinetable-debuginfo,function(print<memoryssa-walker>),function(view-dom-only),function(verify<scalar-evolution>),function(assume-simplify),function(print<inliner-size-estimator>),strip-nondebug,function(loop-data-prefetch),wholeprogramdevirt,function(dce),function(lower-constant-intrinsics),function(dot-post-dom),hipstdpar-interpose-alloc' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/111b1e6ef9e4ed55a9ee/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,7 +1,7 @@
   IN 0
   QALLOC H0 0 1
   QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +REVERSIBLE F:__unnamed_2 1000
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
  @@ -11,7 +11,7 @@
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0198 (26 passes)` — **L1,L5** — LLVM 23; modes seq-0198; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay e710f8d5d50a44d350a6`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=elim-avail-extern,cgscc(coro-split),function(slsr),print-callgraph,function(early-cse),memprof-context-disambiguation,function(irce),inliner-wrapper-no-mandatory-first,function(sroa),function(load-store-vectorizer),function(pa-eval),hipstdpar-interpose-alloc,function(dce),function(add-discriminators),function(win-eh-prepare),function(print<block-freq>),assign-guid,cgscc(invalidate<all>),cgscc(coro-split),function(loop(print<hash-recognize>)),function(print<stack-lifetime>),function(dfa-jump-threading),print<ctx-prof-analysis>,strip-debug-declare,function(loop(loop-idiom-vectorize)),function(verify<domtree>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/6a7643e588dae9cbab9fb778d5f46f78b65d39c5f8bca6079f59485400aaf088/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/e710f8d5d50a44d350a6/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0169 (40 passes)` — **L1,L5** — LLVM 20; modes seq-0169; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay dcd5aaaefa3e8fea24da`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(adce),function(dot-dom),print-must-be-executed-contexts,cgscc(invalidate<all>),cg-profile,function(sccp),function(newgvn),function(print<branch-prob>),function(lower-widenable-condition),constmerge,function(print<scalar-evolution>),function(print<memoryssa>),strip-debug-declare,function(bdce),function(count-visits),function(count-visits),function(objc-arc-expand),function(print-predicateinfo),function(print<domtree>),function(objc-arc-contract),function(flatten-cfg),function(loop(loop-flatten)),function(early-cse),function(assume-simplify),function(loop(print<loopnest>)),assign-guid,print,function(vector-combine),cgscc(argpromotion),print-lcg,function(sink),function(jump-table-to-switch),openmp-opt,function(transform-warning),function(bdce),function(loop(loop-reduce)),recompute-globalsaa,function(loop(dot-ddg)),inliner-wrapper,function(loop(loop-term-fold))' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/dcd5aaaefa3e8fea24da/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0118 (26 passes)` — **L1,L5** — LLVM 18; modes seq-0118; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 2146570efbe7e0fc2739`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(adce),function(early-cse),function(print<branch-prob>),inliner-wrapper-no-mandatory-first,function(transform-warning),lowertypetests,function(lower-expect),function(print<scalar-evolution>),deadargelim,function(wasm-eh-prepare),function(dot-dom-only),function(mem2reg),function(infer-address-spaces),function(print<scalar-evolution>),function(print<inline-cost>),function(lower-guard-intrinsic),rewrite-statepoints-for-gc,function(verify<domtree>),function(loop-distribute),attributor-light,openmp-opt-postlink,no-op-module,function(tailcallelim),function(objc-arc-expand),function(loop(no-op-loop)),function(coro-elide)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/2146570efbe7e0fc2739/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0137 (31 passes)` — **L1,L5** — LLVM 20; modes seq-0137; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 9737ca264aa9df4bf7bb`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(cfguard),function(sroa),function(loop(no-op-loop)),function(loop(dot-ddg)),function(lower-atomic),function(win-eh-prepare),function(reassociate),function(loop(loop-deletion)),function(gc-lowering),function(libcalls-shrinkwrap),function(view-cfg),ipsccp,function(loop-load-elim),function(print<postdomtree>),function(loop-vectorize),deadargelim,function(loop(print<ddg>)),always-inline,function(irce),iroutliner,function(loop-versioning),function(verify<domtree>),function(helloworld),function(print-alias-sets),function(verify<cycles>),attributor-light,function(objc-arc),function(loop(loop-instsimplify)),function(lower-constant-intrinsics),function(nary-reassociate),dxil-upgrade' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/9737ca264aa9df4bf7bb/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0022 (23 passes)` — **L1,L5** — LLVM 18; modes seq-0022; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 60bde019f0bc2fa95326`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(correlated-propagation),function(assume-builder),function(objc-arc-contract),cgscc(attributor-light-cgscc),function(loop(canon-freeze)),function(callbrprepare),function(hardware-loops),sancov-module,function(loop-data-prefetch),function(place-safepoints),function(loop-distribute),function(view-cfg),deadargelim,ipsccp,function(loop(loop-deletion)),function(instcount),function(print-memderefs),function(gvn),function(loop-simplify),function(place-safepoints),print-profile-summary,function(print<cost-model>),function(no-op-function)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/60bde019f0bc2fa95326/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0170 (18 passes)` — **L1,L5** — LLVM 20; modes seq-0170; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay ca599268f46cdfb60237`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(dce),sancov-module,function(loop(dot-ddg)),function(loop(loop-flatten)),function(print<cycles>),function(print<func-properties>),function(annotation-remarks),function(annotation-remarks),function(make-guards-explicit),cgscc(argpromotion),function(verify<safepoint-ir>),function(print<phi-values>),function(redundant-dbg-inst-elim),function(lower-atomic),function(mem2reg),function(simplifycfg),module-inline,function(win-eh-prepare)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/ca599268f46cdfb60237/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0092 (20 passes)` — **L1,L5** — LLVM 23; modes seq-0092; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 1b4bb0f3c14f501fe7cd`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=function(guard-widening),called-value-propagation,function(memcpyopt),global-merge,function(loop(loop-unroll-and-jam)),function(replace-with-veclib),function(lint),inliner-wrapper-no-mandatory-first,function(sroa),function(guard-widening),function(wasm-eh-prepare),function(instsimplify),function(loop-mssa(lnicm)),function(lower-widenable-condition),hipstdpar-math-fixup,cgscc(no-op-cgscc),function(print<loops>),sancov-module,function(partially-inline-libcalls),openmp-opt-postlink' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/6a7643e588dae9cbab9fb778d5f46f78b65d39c5f8bca6079f59485400aaf088/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/1b4bb0f3c14f501fe7cd/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0119 (35 passes)` — **L1,L5** — LLVM 18; modes seq-0119; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay e5685a06ded9a01c89a0`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(guard-widening),module-inline,function(pgo-memop-opt),function(callbrprepare),deadargelim,function(tailcallelim),function(lint),function(bdce),function(adce),function(print<demanded-bits>),function(make-guards-explicit),function(callbrprepare),cgscc(inline),function(float2int),function(print-memderefs),function(sroa),function(objc-arc),function(tlshoist),function(helloworld),function(print<stack-lifetime>),function(fix-irreducible),called-value-propagation,function(print<inline-cost>),function(annotation-remarks),function(dot-post-dom),function(print<access-info>),view-callgraph,lower-ifunc,function(slsr),function(nary-reassociate),function(print<memoryssa-walker>),view-callgraph,function(loop(loop-reduce)),function(mldst-motion),function(loop-unroll)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/e5685a06ded9a01c89a0/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0117 (32 passes)` — **L1,L5** — LLVM 18; modes seq-0117; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay d2de060c495a496112a0`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(gvn-hoist),cgscc(openmp-opt-cgscc),function(slp-vectorizer),function(pgo-memop-opt),print-callgraph,function(dot-cfg-only),function(print<postdomtree>),function(callsite-splitting),print<inline-advisor>,shadow-stack-gc-lowering,function(verify<loops>),function(dse),function(loop(loop-instsimplify)),function(print-predicateinfo),strip-dead-debug-info,global-merge,function(print<branch-prob>),function(helloworld),function(print<memoryssa>),openmp-opt-postlink,function(instnamer),function(verify<regions>),function(newgvn),function(sccp),function(loop(loop-rotate)),function(print-predicateinfo),inliner-wrapper,function(nary-reassociate),function(view-dom),function(loop(loop-reroll)),function(fix-irreducible),function(helloworld)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/d2de060c495a496112a0/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0111 (34 passes)` — **L1,L5** — LLVM 18; modes seq-0111; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -REVERSIBLE F:body 1000 / +REVERSIBLE F:body 12
  - reproduce: `python3 corpus/legality/harness/run.py replay f98688b80bacbae1e58c`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(instcombine<no-verify-fixpoint>),function(print<inliner-size-estimator>),function(loop(loop-versioning-licm)),strip-debug-declare,function(gvn-sink),print-stack-safety,function(reassociate),module-inline,constmerge,openmp-opt-postlink,function(helloworld),function(lowerinvoke),function(sink),function(print<demanded-bits>),function(loop(print<iv-users>)),globalsplit,function(loop(print<ddg>)),function(print-predicateinfo),function(loop-data-prefetch),function(float2int),function(infer-address-spaces),function(early-cse),function(verify<memoryssa>),function(add-discriminators),lower-emutls,deadargelim,iroutliner,rpo-function-attrs,print-profile-summary,function(alignment-from-assumptions),function(lowerswitch),function(irce),function(move-auto-init),function(no-op-function)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/f98688b80bacbae1e58c/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
   QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  -RET 1000
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0163 (14 passes)` — **L1,L5** — LLVM 20; modes seq-0163; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 4ac81e419f56db55455a`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(libcalls-shrinkwrap),function(correlated-propagation),function(lower-widenable-condition),cgscc(function-attrs),function(bounds-checking),function(loop(loop-interchange)),function(mem2reg),module-inline,function(print<inliner-size-estimator>),cgscc(attributor-light-cgscc),function(print<inline-cost>),function(verify<safepoint-ir>),function(print-predicateinfo),function(helloworld)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/4ac81e419f56db55455a/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0053 (6 passes)` — **L1,L5** — LLVM 18; modes seq-0053; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 196ec188f92becc7551a`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(loop(indvars)),pseudo-probe,function(assume-simplify),cgscc(inline),function(newgvn),function(print<stack-lifetime>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/196ec188f92becc7551a/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0191 (18 passes)` — **L1,L5** — LLVM 23; modes seq-0191; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 8ac437c119673f70eafd`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=function(loop(loop-flatten)),function(print<loops>),print-callgraph,function(mldst-motion),inliner-wrapper-no-mandatory-first,lowertypetests,print-lcg,function(print<postdomtree>),function(loop-distribute),drop-type-tests,lowertypetests,function(reg2mem),function(print<predicate-info>),function(gvn-sink),dot-callgraph,function(vector-combine),function(sroa),function(no-op-function)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/6a7643e588dae9cbab9fb778d5f46f78b65d39c5f8bca6079f59485400aaf088/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/8ac437c119673f70eafd/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0186 (19 passes)` — **L1,L5** — LLVM 18; modes seq-0186; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -REVERSIBLE F:body 1000 / +REVERSIBLE F:body 12
  - reproduce: `python3 corpus/legality/harness/run.py replay 152e912e643f028add1e`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(loop(no-op-loopnest)),strip-debug-declare,function(loop(print<iv-users>)),function(print<stack-lifetime>),cgscc(inline),function(pgo-memop-opt),function(dot-cfg),pgo-icall-prom,function(callsite-splitting),globaldce,function(coro-elide),function(loop(loop-unroll-full)),function(loop(guard-widening)),function(objc-arc-contract),function(place-safepoints),inliner-wrapper-no-mandatory-first,recompute-globalsaa,function(loop-fusion),function(instcombine<no-verify-fixpoint>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/152e912e643f028add1e/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
   QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  -RET 1000
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0192 (31 passes)` — **L1,L5** — LLVM 18,23; modes seq-0192; 2 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 63c992dfc6803b03d87b`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=function(loop-load-elim),sanmd-module,lower-comment-string,function(extra-vector-passes),function(print<phi-values>),print<module-debuginfo>,function(unreachableblockelim),print<module-debuginfo>,strip-dead-prototypes,function(loop-mssa(lnicm)),global-merge,function(verify),static-data-annotator,function(expand-memcmp),function(print<domfrontier>),function(print<memoryssa>),function(assume-simplify),cgscc(inline),function(print<predicate-info>),print<module-debuginfo>,shadow-stack-gc-lowering,function(print<memoryssa>),function(vector-combine),function(print<mem-derefs>),function(mem2reg),function(strip-gc-relocates),function(annotation-remarks),function(loop-mssa(licm)),function(unreachableblockelim),function(loop(loop-flatten)),function(instcount)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/6a7643e588dae9cbab9fb778d5f46f78b65d39c5f8bca6079f59485400aaf088/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/63c992dfc6803b03d87b/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0156 (29 passes)` — **L1,L5** — LLVM 20; modes seq-0156; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 842c4afebc831e2cf2ac`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(loop-unroll),function(loop(loop-deletion)),function(adce),function(alignment-from-assumptions),function(lower-expect),lower-global-dtors,function(cfguard),function(loop(print<iv-users>)),function(loop-versioning),function(load-store-vectorizer),rewrite-symbols,function(newgvn),function(verify<loops>),function(guard-widening),function(instcombine<no-verify-fixpoint>),dxil-upgrade,function(break-crit-edges),function(annotation-remarks),function(print<da>),function(print<inliner-size-estimator>),inliner-wrapper-no-mandatory-first,function(aa-eval),debugify,function(loop-fusion),function(print<func-properties>),print<dxil-metadata>,function(loop(loop-idiom)),function(callbr-prepare),print<inline-advisor>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/842c4afebc831e2cf2ac/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0013 (35 passes)` — **L1,L5** — LLVM 23; modes seq-0013; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 4205950df15efc5c0baa`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=function(lower-invoke),function(print<lazy-value-info>),wholeprogramdevirt,function(extra-vector-passes),function(sroa),function(print<loop-cache-cost>),cg-profile,deadargelim,function(constraint-elimination),module-inline,function(print),function(print<phi-values>),function(dot-dom),function(slp-vectorizer),memprof-remove-attributes,function(cfguard),function(jump-threading),print<ctx-prof-analysis>,function(lower-invoke),function(print<assumptions>),function(slsr),function(separate-const-offset-from-gep),always-inline,noinline-nonprevailing,function(print<domfrontier>),function(separate-const-offset-from-gep),strip-dead-debug-info,function(normalize),rewrite-statepoints-for-gc,debugify,inliner-wrapper,function(sandbox-vectorizer),function(prof-inject),pseudo-probe,function(bounds-checking)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/6a7643e588dae9cbab9fb778d5f46f78b65d39c5f8bca6079f59485400aaf088/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/4205950df15efc5c0baa/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0132 (39 passes)` — **L1,L5** — LLVM 23; modes seq-0132; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay c2c58b3338fa7d9fb87b`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=function(make-guards-explicit),drop-type-tests,rewrite-symbols,sancov-module,function(verify),function(early-cse),function(add-discriminators),function(add-discriminators),function(fix-irreducible),function(print<postdomtree>),ipsccp,strip-dead-cg-profile,function(vector-combine),attributor-light,function(loop(print<loopnest>)),function(load-store-vectorizer),rewrite-symbols,function(objc-arc-expand),function(win-eh-prepare),declare-runtime-libcalls,function(print<scev-division>),function(lower-switch),function(loop(canon-freeze)),function(alignment-from-assumptions),function(instnamer),function(wasm-eh-prepare),function(loop-mssa(lnicm)),function(loop(loop-simplifycfg)),function(add-discriminators),function(loop-unroll),function(infer-alignment),function(print<loops>),function(loop(dot-ddg)),print-profile-summary,attributor-light,pgo-icall-prom,function(newgvn),function(lower-matrix-intrinsics),view-callgraph' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/6a7643e588dae9cbab9fb778d5f46f78b65d39c5f8bca6079f59485400aaf088/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/c2c58b3338fa7d9fb87b/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0158 (13 passes)` — **L1,L5** — LLVM 20; modes seq-0158; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -REVERSIBLE F:body 1000 / +REVERSIBLE F:body 12
  - reproduce: `python3 corpus/legality/harness/run.py replay fc799d4e2b6754a105cd`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(print),rpo-function-attrs,function(scalarize-masked-mem-intrin),function(instcombine<no-verify-fixpoint>),function(loop(no-op-loopnest)),pseudo-probe-update,inliner-wrapper,function(print<inliner-size-estimator>),function(sink),function(print-memderefs),module-inline,function(tailcallelim),function(print<stack-lifetime>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/fc799d4e2b6754a105cd/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
   QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  -RET 1000
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0151 (33 passes)` — **L1,L5** — LLVM 20; modes seq-0151; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay aca9e134726ff8ea6c61`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(print-mustexecute),openmp-opt,globalopt,annotation2metadata,shadow-stack-gc-lowering,function(verify<safepoint-ir>),function(instcount),function(loop-mssa(licm)),function(newgvn),function(ee-instrument),function(normalize),function(guard-widening),cgscc(inline),hipstdpar-interpose-alloc,function(strip-gc-relocates),function(view-dom),rewrite-statepoints-for-gc,function(print<inliner-size-estimator>),iroutliner,function(print-predicateinfo),function(loop(loop-reduce)),function(print<inline-cost>),function(loop(print<loopnest>)),function(infer-address-spaces),function(objc-arc),function(print-mustexecute),function(lower-allow-check),function(pgo-memop-opt),function(lint),function(loop(loop-instsimplify)),function(loop-simplify),function(inject-tli-mappings),function(loop(canon-freeze))' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/aca9e134726ff8ea6c61/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0123 (36 passes)` — **L1,L5** — LLVM 23; modes seq-0123; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -REVERSIBLE F:body 1000 / +REVERSIBLE F:body 12
  - reproduce: `python3 corpus/legality/harness/run.py replay 6aaf624aee6d5be2a8d9`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=function(print<access-info>),function(loop(print<hash-recognize>)),function(print<predicate-info>),function(redundant-dbg-inst-elim),function(instcombine<no-verify-fixpoint>),function(load-store-vectorizer),function(reassociate),global-merge,function(loop-mssa(licm)),function(print<scev-division>),cross-dso-cfi,simplify-type-tests,function(inject-tli-mappings),function(print<func-properties>),cgscc(invalidate<all>),function(loop-vectorize),function(win-eh-prepare),print<structural-hash>,norecurse-lto-inference,function(lower-invoke),function(print<alias-sets>),function(reg2mem),function(sink),function(loop(simple-loop-unswitch)),annotation2metadata,function(early-cse),print-ir-similarity,function(helloworld),function(aa-eval),hipstdpar-math-fixup,function(pa-eval),ipsccp,canonicalize-aliases,shadow-stack-gc-lowering,function(assume-simplify),module-inline' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/6a7643e588dae9cbab9fb778d5f46f78b65d39c5f8bca6079f59485400aaf088/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/6aaf624aee6d5be2a8d9/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
   QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  -RET 1000
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0073 (24 passes)` — **L1,L5** — LLVM 23; modes seq-0073; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -REVERSIBLE F:body 1000 / +REVERSIBLE F:body 12
  - reproduce: `python3 corpus/legality/harness/run.py replay b7f78d8f8b6ecc0c4c38`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=function(print<alias-sets>),function(gvn-sink),function(tailcallelim),check-debugify,cgscc(invalidate<all>),print<reg-usage>,function(instcombine<no-verify-fixpoint>),function(verify),function(print<loops>),function(verify<memoryssa>),function(wasm-eh-prepare),debugify,function(scalarize-masked-mem-intrin),ipsccp,function(loop-sink),forceattrs,function(instsimplify),cgscc(coro-annotation-elide),function(lower-constant-intrinsics),function(print<cost-model>),function(loop-unroll),function(jump-table-to-switch),function(div-rem-pairs),function(annotation-remarks)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/6a7643e588dae9cbab9fb778d5f46f78b65d39c5f8bca6079f59485400aaf088/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/b7f78d8f8b6ecc0c4c38/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
   QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  -RET 1000
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0157 (14 passes)` — **L1,L5** — LLVM 20; modes seq-0157; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 9e603aa1a3ab77bfaab7`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(print<da>),function(loop(loop-term-fold)),no-op-module,function(view-post-dom-only),function(chr),function(loop-distribute),module-inline,function(verify<regions>),function(unify-loop-exits),function(loop(loop-reduce)),function(gvn),function(float2int),cgscc(invalidate<all>),print-lcg' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/9e603aa1a3ab77bfaab7/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0146 (21 passes)` — **L1,L5** — LLVM 18; modes seq-0146; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 32d9ded59e537477ac7e`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(print<memoryssa-walker>),function(transform-warning),cgscc(invalidate<all>),function(place-safepoints),name-anon-globals,strip-dead-prototypes,module-inline,function(newgvn),function(loop(dot-ddg)),function(lint),function(verify<loops>),function(fix-irreducible),mergefunc,function(print-cfg-sccs),pseudo-probe,function(loop-versioning),function(correlated-propagation),print-must-be-executed-contexts,hipstdpar-interpose-alloc,function(print<inliner-size-estimator>),module-inline' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/32d9ded59e537477ac7e/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0007 (26 passes)` — **L1,L5** — LLVM 23; modes seq-0007; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 4d64da6f76932771bfe9`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=function(print<memoryssa-walker>),loop-extract,function(print<uniformity>),invalidate<all>,function(loop(loop-instsimplify)),function(sroa),recompute-globalsaa,function(print<phi-values>),pseudo-probe,function(lower-widenable-condition),pgo-force-function-attrs,function(partially-inline-libcalls),function(loop-vectorize),function(inject-tli-mappings),function(verify<loops>),function(view-post-dom),function(inline-asm-prepare),ctx-prof-flatten,function(expand-reductions),function(print<memoryssa-walker>),shadow-stack-gc-lowering,function(print<cost-model>),function(loop(loop-unroll-full)),function(loop(loop-rotate)),ipsccp,function(pa-eval)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/6a7643e588dae9cbab9fb778d5f46f78b65d39c5f8bca6079f59485400aaf088/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/4d64da6f76932771bfe9/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0085 (22 passes)` — **L1,L5** — LLVM 18; modes seq-0085; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 30ce7f8c99079dcf25c1`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(print<stack-safety-local>),partial-inliner,print,function(print<access-info>),function(callsite-splitting),function(sroa),cgscc(openmp-opt-cgscc),pseudo-probe-update,function(infer-address-spaces),function(infer-address-spaces),function(print<access-info>),function(loop-vectorize),function(objc-arc),function(verify<domtree>),loop-extract,function(loop-vectorize),function(objc-arc),inliner-wrapper-no-mandatory-first,cgscc(openmp-opt-cgscc),function(bounds-checking),cgscc(invalidate<all>),function(declare-to-assign)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/30ce7f8c99079dcf25c1/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0091 (32 passes)` — **L1,L5** — LLVM 18; modes seq-0091; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 5bf4b2f06c585c83aecc`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(slsr),function(break-crit-edges),objc-arc-apelim,function(aggressive-instcombine),recompute-globalsaa,function(view-dom-only),function(annotation-remarks),function(dot-post-dom),function(callbrprepare),function(print<domtree>),function(objc-arc),function(verify<scalar-evolution>),function(gvn-sink),function(mem2reg),inliner-wrapper,function(view-cfg),function(verify),print,function(gvn),function(sroa),inferattrs,function(print<stack-safety-local>),print<structural-hash>,function(loop-unroll),print<module-debuginfo>,function(newgvn),annotation2metadata,instrorderfile,function(objc-arc),function(jump-threading),function(print-predicateinfo),function(bdce)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/5bf4b2f06c585c83aecc/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0008 (38 passes)` — **L1,L5** — LLVM 18; modes seq-0008; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay c44a5e287ed5da8935af`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(verify<domtree>),function(instcount),function(view-dom-only),function(loop(print)),inliner-wrapper-no-mandatory-first,function(loop-sink),synthetic-counts-propagation,function(vector-combine),function(loop-sink),function(irce),function(loop(print<iv-users>)),function(assume-builder),deadargelim,function(add-discriminators),function(dot-cfg-only),print<module-debuginfo>,lower-ifunc,function(alignment-from-assumptions),function(print<domtree>),annotation2metadata,elim-avail-extern,function(lcssa),function(loweratomic),function(no-op-function),function(dfa-jump-threading),lower-global-dtors,function(lower-expect),function(loop(invalidate<all>)),function(kcfi),function(loop(canon-freeze)),function(simplifycfg),function(gvn),function(gvn-hoist),function(infer-address-spaces),function(reassociate),function(instnamer),pseudo-probe,ipsccp' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/c44a5e287ed5da8935af/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0193 (33 passes)` — **L1,L5** — LLVM 20,23; modes seq-0193; 2 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 899f3cb64ffd988c49c5`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(view-post-dom-only),function(verify<loops>),function(loop(simple-loop-unswitch)),extract-blocks,function(callsite-splitting),function(sroa),function(loop(loop-idiom)),module-inline,function(aggressive-instcombine),function(loop(print<iv-users>)),function(loop(loop-predication)),function(speculative-execution),rewrite-statepoints-for-gc,verify,function(loop(loop-versioning-licm)),function(infer-address-spaces),function(loop(loop-predication)),function(loop(print<loop-cache-cost>)),print-lcg-dot,pseudo-probe,function(print<delinearization>),function(loop-versioning),function(partially-inline-libcalls),print<structural-hash>,function(print<inliner-size-estimator>),function(loop(loop-unroll-full)),function(flatten-cfg),function(loop(loop-simplifycfg)),function(lower-widenable-condition),function(print<cost-model>),function(strip-gc-relocates),function(loop(loop-rotate)),annotation2metadata' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/899f3cb64ffd988c49c5/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0075 (35 passes)` — **L1,L5** — LLVM 18; modes seq-0075; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 5e5ae41c4bf5552b2707`; opt: `/usr/lib/llvm-18/bin/opt '-passes=hipstdpar-interpose-alloc,function(infer-address-spaces),wholeprogramdevirt,print-profile-summary,function(loop-versioning),function(tailcallelim),function(loweratomic),pseudo-probe,inliner-wrapper-no-mandatory-first,function(infer-address-spaces),function(count-visits),function(loop(loop-unroll-full)),openmp-opt-postlink,function(adce),function(loop(print<loopnest>)),function(view-cfg),constmerge,function(view-cfg),function(print<loops>),function(verify<regions>),cross-dso-cfi,instrorderfile,function(loop(loop-unroll-full)),function(sroa),function(transform-warning),function(print),function(print<inline-cost>),function(print<scalar-evolution>),lowertypetests,function(newgvn),strip-dead-prototypes,function(lower-expect),no-op-module,recompute-globalsaa,function(load-store-vectorizer)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/5e5ae41c4bf5552b2707/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0009 (26 passes)` — **L1,L5** — LLVM 20; modes seq-0009; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay fd1b38460e59c8e4393c`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=hotcoldsplit,function(correlated-propagation),strip-debug-declare,function(nary-reassociate),function(redundant-dbg-inst-elim),function(loop(loop-idiom-vectorize)),function(separate-const-offset-from-gep),canonicalize-aliases,function(print<delinearization>),function(print<cost-model>),globalsplit,function(gc-lowering),jmc-instrumenter,print-callgraph-sccs,print,function(infer-alignment),function(mem2reg),cgscc(invalidate<all>),function(strip-gc-relocates),function(load-store-vectorizer),module-inline,function(loop-sink),function(flatten-cfg),function(memcpyopt),called-value-propagation,function(slsr)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/fd1b38460e59c8e4393c/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0112 (39 passes)` — **L1,L5** — LLVM 23; modes seq-0112; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 13e54df2e362f891373a`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=inliner-wrapper-no-mandatory-first,wholeprogramdevirt,function(place-safepoints),shadow-stack-gc-lowering,function(loop(loop-predication)),function(make-guards-explicit),function(dot-dom),function(loop(guard-widening)),function(make-guards-explicit),annotation2metadata,rewrite-symbols,function(print<scalar-evolution>),function(mem2reg),function(dfa-jump-threading),rewrite-symbols,function(print<func-properties>),function(view-cfg),function(loop(loop-idiom)),function(place-safepoints),pgo-force-function-attrs,function(print<cost-model>),sanmd-module,coro-early,function(sandbox-vectorizer),function(no-op-function),cgscc(inline),function(guard-widening),function(replace-with-veclib),global-merge,function(slsr),function(print<cycles>),cgscc(attributor-light-cgscc),function(jump-threading),function(separate-const-offset-from-gep),function(view-dom),function(print<loop-cache-cost>),function(extra-vector-passes),deadargelim,function(slp-vectorizer)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/6a7643e588dae9cbab9fb778d5f46f78b65d39c5f8bca6079f59485400aaf088/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/13e54df2e362f891373a/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0108 (19 passes)` — **L1,L5** — LLVM 18; modes seq-0108; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay d5c4bb82a4ae59c86983`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lower-emutls,function(correlated-propagation),function(print<domfrontier>),function(lcssa),no-op-module,function(sroa),function(flattencfg),module-inline,function(print<postdomtree>),function(loop(print<loopnest>)),function(dot-cfg-only),cgscc(coro-split),function(print-cfg-sccs),function(count-visits),function(partially-inline-libcalls),function(loop(loop-unroll-full)),function(gvn),function(loop(loop-versioning-licm)),function(print<regions>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/d5c4bb82a4ae59c86983/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0136 (28 passes)` — **L1,L5** — LLVM 23; modes seq-0136; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay ad0d9d603c18ff9df8d0`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=name-anon-globals,function(mem2reg),cgscc(coro-annotation-elide),function(pa-eval),function(verify<domtree>),function(wasm-eh-prepare),memprof-context-disambiguation,coro-early,function(coro-elide),partial-inliner,called-value-propagation,strip-dead-prototypes,function(loop(no-op-loop)),function(mldst-motion),function(mldst-motion),function(loop(extra-simple-loop-unswitch-passes)),ipsccp,function(loop(loop-unroll-and-jam)),function(print<predicate-info>),assign-guid,openmp-opt,function(no-op-function),function(print<predicate-info>),function(lower-widenable-condition),function(loop(canon-freeze)),function(loop-mssa(licm)),function(slp-vectorizer),function(loop(simple-loop-unswitch))' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/6a7643e588dae9cbab9fb778d5f46f78b65d39c5f8bca6079f59485400aaf088/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/ad0d9d603c18ff9df8d0/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0133 (31 passes)` — **L1,L5** — LLVM 20; modes seq-0133; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 292432a6e36c4343a0f7`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=objc-arc-apelim,invalidate<all>,embed-bitcode,function(view-dom),function(print<cost-model>),function(mem2reg),function(annotation-remarks),function(loop(loop-instsimplify)),coro-early,function(instsimplify),memprof-context-disambiguation,cgscc(coro-annotation-elide),function(print-mustexecute),inliner-wrapper-no-mandatory-first,inliner-wrapper-no-mandatory-first,function(lint),function(lower-guard-intrinsic),function(loop-distribute),function(mergeicmps),function(helloworld),print<ctx-prof-analysis>,shadow-stack-gc-lowering,rpo-function-attrs,function(print<loops>),cg-profile,cgscc(invalidate<all>),print<module-debuginfo>,name-anon-globals,globalopt,shadow-stack-gc-lowering,function(newgvn)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/292432a6e36c4343a0f7/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0153 (34 passes)` — **L1,L5** — LLVM 23; modes seq-0153; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay dad6fff3c979359ca4db`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=print,dot-callgraph,strip-dead-cg-profile,strip-dead-prototypes,ipsccp,function(div-rem-pairs),function(helloworld),recompute-globalsaa,function(mem2reg),function(speculative-execution),function(transform-warning),attributor-light,function(loop(print<loopnest>)),module-inline,alloc-token,function(invalidate<all>),dxil-upgrade,function(verify<cycles>),function(loop(no-op-loopnest)),function(ee-instrument),function(loop(loop-unroll-and-jam)),function(loop-versioning),function(strip-gc-relocates),dot-callgraph,function(loop(guard-widening)),function(print<loops>),function(tailcallelim),function(verify<memoryssa>),function(view-cfg-only),cgscc(attributor-light-cgscc),function(print<inline-cost>),ctx-prof-flatten-prethinlink,constmerge,inferattrs' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/6a7643e588dae9cbab9fb778d5f46f78b65d39c5f8bca6079f59485400aaf088/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/dad6fff3c979359ca4db/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0115 (15 passes)` — **L1,L5** — LLVM 20; modes seq-0115; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 39470a8ec3cd893e10e5`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=print<inline-advisor>,function(print<inline-cost>),function(print<loops>),mergefunc,print<dxil-metadata>,inliner-wrapper-no-mandatory-first,pseudo-probe-update,function(correlated-propagation),function(irce),function(print<delinearization>),print<structural-hash>,function(loop(indvars)),function(lower-matrix-intrinsics),function(gvn),function(sroa)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/18ded834f2ae9f5c6fbc09eb198660d50a59c39472eeb6207d3240e0d9903f2c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/39470a8ec3cd893e10e5/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-is-constant-budget`** (probe) — P3 `seq-0116 (32 passes)` — **L1,L5** — LLVM 23; modes seq-0116; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -QALLOC H1 0 8 / -REVERSIBLE F:body 1000
  - reproduce: `python3 corpus/legality/harness/run.py replay 97b8499e449de8772d60`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=print<reg-usage>,openmp-opt,pseudo-probe-update,function(lower-guard-intrinsic),print<structural-hash>,function(lower-switch),function(adce),hipstdpar-interpose-alloc,function(print<postdomtree>),verify,function(expand-reductions),function(bdce),global-merge-func,function(view-cfg-only),function(dot-dom),sanmd-module,function(objc-arc-expand),function(objc-arc),assign-guid,strip-dead-prototypes,cgscc(argpromotion),lower-comment-string,function(print<demanded-bits>),function(newgvn),function(lcssa),function(strip-gc-relocates),drop-type-tests,function(verify<safepoint-ir>),function(print<phi-values>),function(sink),function(wasm-eh-prepare),inliner-wrapper' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/6a7643e588dae9cbab9fb778d5f46f78b65d39c5f8bca6079f59485400aaf088/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/97b8499e449de8772d60/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,160 +1,160 @@
   IN 0
   QALLOC H0 0 1
  -QALLOC H1 0 8
  -REVERSIBLE F:body 1000
  +QALLOC H1 0 3
  +REVERSIBLE F:body 12
   GATE 1 H0 0
   END REVERSIBLE
   GATE2 3 H0 0 H1 0
   QFREE H1
   QFREE H0
  ...
  ```
  </details>
- **`c-memcpy-handle-int`** (probe) — P1 `strip` — **L1,L4,L5** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region symbols changed rg->__unnamed_1, rpair->__unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_2; region is not a definition (missing, declaration, or alias): rg
  - reproduce: `python3 corpus/legality/harness/run.py replay 89442cc4dfbbde8cef35`; opt: `/usr/lib/llvm-18/bin/opt -passes=strip /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/a0d261e9203dc949619c6f05707631d9077b5e61f654d1fa7140921bbaf60182/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/89442cc4dfbbde8cef35/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,11 +1,11 @@
   IN 0
   QALLOC H0 0 1
   GATE 2 H0 0
  -CTRL H0 0 F:rg 4
  -GATE 1 H0 0
  -END CTRL
  -QALLOC H1 0 1
  -ADJ F:rpair
  +CTRL H0 0 F:__unnamed_1 4
  +GATE 1 H0 0
  +END CTRL
  ...
  ```
  </details>
- **`c-memcpy-handle-int`** (probe) — P1 `strip-nondebug` — **L1,L4,L5** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region symbols changed rg->__unnamed_1, rpair->__unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_2; region is not a definition (missing, declaration, or alias): rg
  - reproduce: `python3 corpus/legality/harness/run.py replay f3773d86c5d8118e3b89`; opt: `/usr/lib/llvm-18/bin/opt -passes=strip-nondebug /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/a0d261e9203dc949619c6f05707631d9077b5e61f654d1fa7140921bbaf60182/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/f3773d86c5d8118e3b89/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,11 +1,11 @@
   IN 0
   QALLOC H0 0 1
   GATE 2 H0 0
  -CTRL H0 0 F:rg 4
  -GATE 1 H0 0
  -END CTRL
  -QALLOC H1 0 1
  -ADJ F:rpair
  +CTRL H0 0 F:__unnamed_1 4
  +GATE 1 H0 0
  +END CTRL
  ...
  ```
  </details>
- **`c-memcpy-handle-int`** (probe) — P3 `73 random sequences, each containing a pass that FAILs alone on this case (strip 44, strip-nondebug 35)` — **L1,L4,L5** — LLVM 18,20,23; modes seq-0002,seq-0005,seq-0006,seq-0007,seq-0009,seq-0012,seq-0018,seq-0019,seq-0025,seq-0027,seq-0031,seq-0039,seq-0043,seq-0044,seq-0046,seq-0049,seq-0051,seq-0053,seq-0055,seq-0056,seq-0057,seq-0061,seq-0062,seq-0063,seq-0067,seq-0072,seq-0077,seq-0080,seq-0081,seq-0082,seq-0090,seq-0091,seq-0093,seq-0095,seq-0101,seq-0103,seq-0104,seq-0115,seq-0116,seq-0120,seq-0121,seq-0122,seq-0125,seq-0126,seq-0130,seq-0131,seq-0136,seq-0141,seq-0144,seq-0147,seq-0155,seq-0160,seq-0162,seq-0164,seq-0166,seq-0169,seq-0172,seq-0173,seq-0175,seq-0179,seq-0182,seq-0190,seq-0192,seq-0193,seq-0194; 73 cells
  - diagnosis: region symbols changed rg->__unnamed_1, rpair->__unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_2; region is not a definition (missing, declaration, or alias): rg
  - reproduce: `python3 corpus/legality/harness/run.py replay 59ae11dfb058d37a222b`; opt: `/usr/lib/llvm-18/bin/opt '-passes=canonicalize-aliases,function(tailcallelim),function(print<access-info>),function(print-cfg-sccs),always-inline,function(instsimplify),function(loop(loop-predication)),function(print<branch-prob>),function(assume-simplify),strip-nonlinetable-debuginfo,function(print<memoryssa-walker>),function(view-dom-only),function(verify<scalar-evolution>),function(assume-simplify),function(print<inliner-size-estimator>),strip-nondebug,function(loop-data-prefetch),wholeprogramdevirt,function(dce),function(lower-constant-intrinsics),function(dot-post-dom),hipstdpar-interpose-alloc' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3657b76dcd431ca103281a453ae2b0f22a856f8cccaae6ea7858dd357332baee/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/59ae11dfb058d37a222b/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,11 +1,11 @@
   IN 0
   QALLOC H0 0 1
   GATE 2 H0 0
  -CTRL H0 0 F:rg 4
  -GATE 1 H0 0
  -END CTRL
  -QALLOC H1 0 1
  -ADJ F:rpair
  +CTRL H0 0 F:__unnamed_1 4
  +GATE 1 H0 0
  +END CTRL
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — inherited `(any pass; behaviour identical to its input = default<O3> output; 356 pass/mode cells)` — **L1,L5** — LLVM 18,20,23; modes post-O3; 938 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay d5935136334c08c22152`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt -passes=alloc-token /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/f52f276d4cc3c77aac4ccb2d9cf28178419ab3069d6d6fc6f4db039016b31fca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/d5935136334c08c22152/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P1 `attributor` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay 6fcfa4e6c0263fbe11ce`; opt: `/usr/lib/llvm-18/bin/opt -passes=attributor /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/6fcfa4e6c0263fbe11ce/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P1 `cgscc(attributor-cgscc)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay 5a2f5577aca6401debd7`; opt: `/usr/lib/llvm-18/bin/opt '-passes=cgscc(attributor-cgscc)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/5a2f5577aca6401debd7/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P1 `function(gvn)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay d4efae6ba9637751d12f`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(gvn)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/d4efae6ba9637751d12f/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P1 `function(instcombine)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay a6acfd4e629e6a72fa4d`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(instcombine)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/a6acfd4e629e6a72fa4d/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P1 `function(instcombine<no-verify-fixpoint>)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay cd20b1cf78797d5713a8`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(instcombine<no-verify-fixpoint>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/cd20b1cf78797d5713a8/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P1 `function(mem2reg)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay 35c2bcee675d9966569f`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(mem2reg)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/35c2bcee675d9966569f/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P1 `function(newgvn)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay 00c4810ee141d3abaec2`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(newgvn)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/00c4810ee141d3abaec2/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P1 `function(sroa)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay 84d43489bf3f0a29be8d`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(sroa)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/84d43489bf3f0a29be8d/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P1 `scc-oz-module-inliner` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay 99cf760c2bf43cba89d7`; opt: `/usr/lib/llvm-18/bin/opt -passes=scc-oz-module-inliner /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/99cf760c2bf43cba89d7/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P2 `default<O1>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay 78703bb39649cebef01a`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O1>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/78703bb39649cebef01a/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P2 `default<O2>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay e61205af873635df4af7`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O2>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/e61205af873635df4af7/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P2 `default<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay c3bb5f007535e9440b40`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/c3bb5f007535e9440b40/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P2 `default<O3>,default<O3>,default<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay 01495356f62e976fc74e`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O3>,default<O3>,default<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/01495356f62e976fc74e/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P2 `default<Os>` — **L1,L5** — LLVM 18,20; modes raw; 2 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay be70c9fb279c5c8ee66a`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<Os>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/be70c9fb279c5c8ee66a/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P2 `default<Oz>` — **L1,L5** — LLVM 18,20; modes raw; 2 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay 355ad593ef16f0f8f481`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<Oz>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/355ad593ef16f0f8f481/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P2 `lto-pre-link<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay 6d2b6f7be42f37c43c1b`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lto-pre-link<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/6d2b6f7be42f37c43c1b/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P2 `lto<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay 03dc282956bf921da701`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lto<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/03dc282956bf921da701/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P2 `thinlto-pre-link<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay e2f0b918c4383ed96001`; opt: `/usr/lib/llvm-18/bin/opt '-passes=thinlto-pre-link<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/e2f0b918c4383ed96001/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P2 `thinlto<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay 2e62901a9813c8d2a37f`; opt: `/usr/lib/llvm-18/bin/opt '-passes=thinlto<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/2e62901a9813c8d2a37f/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-objectsize-count`** (probe) — P3 `238 random sequences, each containing a pass that FAILs alone on this case (function(newgvn) 49, attributor 48, cgscc(attributor-cgscc) 47, function(sroa) 41, function(instcombine<no-verify-fixpoint>) 35, function(gvn) 32, function(mem2reg) 32, scc-oz-module-inliner 28)` — **L1,L5** — LLVM 18,20,23; modes seq-0001,seq-0002,seq-0003,seq-0005,seq-0006,seq-0007,seq-0008,seq-0009,seq-0010,seq-0012,seq-0013,seq-0014,seq-0015,seq-0016,seq-0018,seq-0020,seq-0022,seq-0024,seq-0025,seq-0026,seq-0027,seq-0029,seq-0031,seq-0032,seq-0035,seq-0036,seq-0037,seq-0038,seq-0039,seq-0041,seq-0042,seq-0044,seq-0046,seq-0047,seq-0048,seq-0049,seq-0050,seq-0051,seq-0053,seq-0054,seq-0055,seq-0056,seq-0058,seq-0061,seq-0064,seq-0065,seq-0066,seq-0067,seq-0069,seq-0070,seq-0072,seq-0073,seq-0074,seq-0075,seq-0077,seq-0078,seq-0079,seq-0080,seq-0081,seq-0082,seq-0083,seq-0085,seq-0086,seq-0088,seq-0089,seq-0091,seq-0092,seq-0093,seq-0094,seq-0096,seq-0097,seq-0099,seq-0100,seq-0101,seq-0102,seq-0103,seq-0105,seq-0106,seq-0107,seq-0108,seq-0109,seq-0111,seq-0112,seq-0113,seq-0114,seq-0115,seq-0116,seq-0117,seq-0118,seq-0119,seq-0120,seq-0122,seq-0123,seq-0124,seq-0125,seq-0126,seq-0128,seq-0130,seq-0132,seq-0133,seq-0134,seq-0135,seq-0136,seq-0137,seq-0138,seq-0139,seq-0140,seq-0141,seq-0142,seq-0143,seq-0144,seq-0145,seq-0146,seq-0147,seq-0148,seq-0149,seq-0150,seq-0151,seq-0152,seq-0153,seq-0156,seq-0157,seq-0158,seq-0160,seq-0161,seq-0162,seq-0163,seq-0164,seq-0165,seq-0166,seq-0167,seq-0168,seq-0169,seq-0170,seq-0171,seq-0172,seq-0174,seq-0175,seq-0176,seq-0177,seq-0179,seq-0180,seq-0181,seq-0183,seq-0184,seq-0185,seq-0186,seq-0187,seq-0188,seq-0189,seq-0191,seq-0192,seq-0193,seq-0194,seq-0195,seq-0198,seq-0199; 238 cells
  - diagnosis: first trace difference: -QALLOC H0 0 2 / +QALLOC H0 0 5
  - reproduce: `python3 corpus/legality/harness/run.py replay 14df32df3de950136563`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=attributor,function(print<scalar-evolution>),function(consthoist),function(view-dom),inliner-wrapper-no-mandatory-first,invalidate<all>,function(correlated-propagation),print-callgraph-sccs,function(mergereturn),function(flatten-cfg),function(loop-versioning),hipstdpar-interpose-alloc,function(instsimplify),function(print<stack-lifetime>),function(lower-switch),cgscc(attributor-light-cgscc),function(print<func-properties>),function(load-store-vectorizer),function(lower-switch),function(objc-arc),function(print<stack-lifetime>),embed-bitcode,function(loop(simple-loop-unswitch)),function(ee-instrument),function(instcombine<no-verify-fixpoint>),print-ir-similarity,extract-blocks,cgscc(no-op-cgscc),function(guard-widening),function(objc-arc),function(print<demanded-bits>),print<dxil-metadata>,function(lower-switch),function(dot-cfg),function(hardware-loops),iroutliner,deadargelim,always-inline,function(print<loops>),function(lower-invoke)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/3d7cd549f8369d71b7ed0e60df70d646dcd0ff6ccb2925d3c79914aa88121eb4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/14df32df3de950136563/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,96 +1,96 @@
   IN 0
  -QALLOC H0 0 2
  +QALLOC H0 0 5
   GATE 1 H0 0
   GATE 2 H0 0
   QFREE H0
  -RET 2100
  +RET 5100
   IN 1
  -QALLOC H0 0 2
  +QALLOC H0 0 4
  ...
  ```
  </details>
- **`c-pie-reltable-region`** (probe) — P1 `global-merge-func` — **L4** — LLVM 20,23; modes raw; 2 cells
  - diagnosis: region o0 became a forwarding thunk to o0.Tgm; region o1 became a forwarding thunk to o1.Tgm; region o2 became a forwarding thunk to o2.Tgm; region o3 became a forwarding thunk to o3.Tgm
  - reproduce: `python3 corpus/legality/harness/run.py replay c4df211d5042cd7d32e8`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes=global-merge-func /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/43f8308efb720d4545cf61da18f59942ed44deb0a8fb5a6ed7ab82e617271fb1/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/c4df211d5042cd7d32e8/output.bc`
- **`c-pie-reltable-region`** (probe) — P3 `16 random sequences, each containing a pass that FAILs alone on this case (global-merge-func 16)` — **L4** — LLVM 20,23; modes seq-0043,seq-0048,seq-0059,seq-0089,seq-0090,seq-0101,seq-0105,seq-0116,seq-0139,seq-0152,seq-0154,seq-0162,seq-0169,seq-0178,seq-0186,seq-0188; 16 cells
  - diagnosis: region o0 became a forwarding thunk to o0.Tgm; region o1 became a forwarding thunk to o1.Tgm; region o2 became a forwarding thunk to o2.Tgm; region o3 became a forwarding thunk to o3.Tgm
  - reproduce: `python3 corpus/legality/harness/run.py replay e78002d307b763caf0ae`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=cgscc(inline),pre-isel-intrinsic-lowering,function(instsimplify),function(fix-irreducible),function(transform-warning),function(safe-stack),hotcoldsplit,function(load-store-vectorizer),function(invalidate<all>),cgscc(argpromotion),function(lcssa),cross-dso-cfi,function(dot-cfg-only),function(lower-guard-intrinsic),function(no-op-function),function(print<cost-model>),global-merge-func,function(lint),hotcoldsplit,inliner-wrapper-no-mandatory-first,function(unify-loop-exits),function(lower-expect),inliner-wrapper,function(verify<regions>),function(print<branch-prob>),iroutliner,strip-dead-debug-info' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/43f8308efb720d4545cf61da18f59942ed44deb0a8fb5a6ed7ab82e617271fb1/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/e78002d307b763caf0ae/output.bc`
- **`c-program-mixed`** (legal) — P1 `strip` — **L1,L4,L5** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region symbols changed diffuse->__unnamed_3, oracle->__unnamed_1, phase->__unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_3
  - reproduce: `python3 corpus/legality/harness/run.py replay 325ef739a4de52918335`; opt: `/usr/lib/llvm-18/bin/opt -passes=strip /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3e4bdde0bb7a31d5ba2d0d6f0b9f1926e4f90853d8c277235c3aeb9caacf0e28/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/325ef739a4de52918335/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -6,20 +6,20 @@
   QBORROW H4 1 1
   QALLOC H5 0 1
   GATE 1 H5 0
  -CTRL H5 0 F:oracle 64
  -END CTRL
  -ADJ F:diffuse
  -GATE 1 H0 0
  -GATE 1 H1 0
  -GATE 1 H2 0
  -GATE 1 H3 0
  -GATE 2 H0 0
  ...
  ```
  </details>
- **`c-program-mixed`** (legal) — P1 `strip-nondebug` — **L1,L4,L5** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region symbols changed diffuse->__unnamed_3, oracle->__unnamed_1, phase->__unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_3
  - reproduce: `python3 corpus/legality/harness/run.py replay bef4a9cb4bacb9c6dd01`; opt: `/usr/lib/llvm-18/bin/opt -passes=strip-nondebug /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/3e4bdde0bb7a31d5ba2d0d6f0b9f1926e4f90853d8c277235c3aeb9caacf0e28/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/bef4a9cb4bacb9c6dd01/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -6,20 +6,20 @@
   QBORROW H4 1 1
   QALLOC H5 0 1
   GATE 1 H5 0
  -CTRL H5 0 F:oracle 64
  -END CTRL
  -ADJ F:diffuse
  -GATE 1 H0 0
  -GATE 1 H1 0
  -GATE 1 H2 0
  -GATE 1 H3 0
  -GATE 2 H0 0
  ...
  ```
  </details>
- **`c-program-mixed`** (legal) — P3 `73 random sequences, each containing a pass that FAILs alone on this case (strip 44, strip-nondebug 35)` — **L1,L4,L5** — LLVM 18,20,23; modes seq-0002,seq-0005,seq-0006,seq-0007,seq-0009,seq-0012,seq-0018,seq-0019,seq-0025,seq-0027,seq-0031,seq-0039,seq-0043,seq-0044,seq-0046,seq-0049,seq-0051,seq-0053,seq-0055,seq-0056,seq-0057,seq-0061,seq-0062,seq-0063,seq-0067,seq-0072,seq-0077,seq-0080,seq-0081,seq-0082,seq-0090,seq-0091,seq-0093,seq-0095,seq-0101,seq-0103,seq-0104,seq-0115,seq-0116,seq-0120,seq-0121,seq-0122,seq-0125,seq-0126,seq-0130,seq-0131,seq-0136,seq-0141,seq-0144,seq-0147,seq-0155,seq-0160,seq-0162,seq-0164,seq-0166,seq-0169,seq-0172,seq-0173,seq-0175,seq-0179,seq-0182,seq-0190,seq-0192,seq-0193,seq-0194; 73 cells
  - diagnosis: region symbols changed diffuse->__unnamed_2, oracle->__unnamed_1, phase->__unnamed_4; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_4
  - reproduce: `python3 corpus/legality/harness/run.py replay 93c8ea6cc27fee3c2b80`; opt: `/usr/lib/llvm-18/bin/opt '-passes=canonicalize-aliases,function(tailcallelim),function(print<access-info>),function(print-cfg-sccs),always-inline,function(instsimplify),function(loop(loop-predication)),function(print<branch-prob>),function(assume-simplify),strip-nonlinetable-debuginfo,function(print<memoryssa-walker>),function(view-dom-only),function(verify<scalar-evolution>),function(assume-simplify),function(print<inliner-size-estimator>),strip-nondebug,function(loop-data-prefetch),wholeprogramdevirt,function(dce),function(lower-constant-intrinsics),function(dot-post-dom),hipstdpar-interpose-alloc' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/d90c758a2e944347bcdb2c8c66508d1a1b7503e41cae743c2527b0ba4697242f/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/93c8ea6cc27fee3c2b80/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -6,20 +6,20 @@
   QBORROW H4 1 1
   QALLOC H5 0 1
   GATE 1 H5 0
  -CTRL H5 0 F:oracle 64
  -END CTRL
  -ADJ F:diffuse
  -GATE 1 H0 0
  -GATE 1 H1 0
  -GATE 1 H2 0
  -GATE 1 H3 0
  -GATE 2 H0 0
  ...
  ```
  </details>
- **`c-program-mixed`** (legal) — P3 `seq-0082 (25 passes)` — **L1,L4,L5** — LLVM 23; modes seq-0082; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: region symbols changed (count 448->0); region is not a definition (missing, declaration, or alias): diffuse; region is not a definition (missing, declaration, or alias): oracle; region is not a definition (missing, declaration, or alias): phase
  - reproduce: `python3 corpus/legality/harness/run.py replay f03a9fd29e0412b49f14`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=function(float2int),function(replace-with-veclib),function(coro-elide),function(loop-load-elim),function(loop(loop-versioning-licm)),rewrite-symbols,function(early-cse),function(print<predicate-info>),function(dot-post-dom-only),function(func-properties-stats),iroutliner,attributor,function(print<scev-division>),cgscc(openmp-opt-cgscc),fatlto-cleanup,pgo-force-function-attrs,function(lower-constant-intrinsics),function(chr),partial-inliner,global-merge,function(consthoist),function(slsr),cgscc(openmp-opt-cgscc),memprof-remove-attributes,function(gvn)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/f3774bade90017f5b5010f944db76a6d59050f5eb5296df0dcc212144d586471/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/f03a9fd29e0412b49f14/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -3,4255 +3,4194366 @@
   QALLOC H1 0 1
   QALLOC H2 0 1
   QALLOC H3 0 1
  -QBORROW H4 1 1
  +QALLOC H4 0 1
   QALLOC H5 0 1
  -GATE 1 H5 0
  -CTRL H5 0 F:oracle 64
  -END CTRL
  -ADJ F:diffuse
  -GATE 1 H0 0
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — inherited `(any pass; behaviour identical to its input = default<O3> output; 358 pass/mode cells)` — **L1,L5** — LLVM 18,20,23; modes post-O3; 942 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O3 object lacks marker externals __bennett_gate; first trace difference: -MEASURE H0 0 2 1 / -MEASURE H0 0 3 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 2d7683b24a4359f3af62`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt -passes=alloc-token /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/1fef9ea05ecb70537da8f036deee1817ddf0cd71cba0c561cd6c049db5522672/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/2d7683b24a4359f3af62/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -2,167 +2,95 @@
   QALLOC H0 0 1
   MEASURE H0 0 0 1
   MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P1 `asan` — **L5** — LLVM 18,20,23; modes post-O3; 3 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O0: native build failed at link; O3 object lacks marker externals __bennett_gate; O3: native build failed at link
  - reproduce: `python3 corpus/legality/harness/run.py replay d53ad7b2c7f1771184de`; opt: `/usr/lib/llvm-18/bin/opt -passes=asan /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/e22519ef40dcef0e52ef0210aa7c3518af2319d1b76a621c7a0bccf5e4149bc7/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/d53ad7b2c7f1771184de/output.bc`
- **`c-pure-attr-wrapper`** (probe) — P1 `attributor` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O3 object lacks marker externals __bennett_gate; first trace difference: -GATE 1 H0 0 / -GATE 1 H0 0
  - reproduce: `python3 corpus/legality/harness/run.py replay aa0666fd87c0d95081a9`; opt: `/usr/lib/llvm-18/bin/opt -passes=attributor /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/aa0666fd87c0d95081a9/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -4,7 +4,6 @@
   MEASURE H0 0 1 0
   MEASURE H0 0 2 1
   MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
  @@ -13,8 +12,6 @@
   MEASURE H0 0 1 1
   MEASURE H0 0 2 0
   MEASURE H0 0 3 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P1 `cgscc(attributor-cgscc)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -GATE 1 H0 0 / -GATE 1 H0 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 0099231414e2d0c1d230`; opt: `/usr/lib/llvm-18/bin/opt '-passes=cgscc(attributor-cgscc)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/0099231414e2d0c1d230/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -4,7 +4,6 @@
   MEASURE H0 0 1 0
   MEASURE H0 0 2 1
   MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
  @@ -14,7 +13,6 @@
   MEASURE H0 0 2 0
   MEASURE H0 0 3 1
   GATE 1 H0 0
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P1 `ctx-instr-lower` — **L5** — LLVM 20,23; modes post-O3; 2 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O0: native build failed at link; O3 object lacks marker externals __bennett_gate; O3: native build failed at link
  - reproduce: `python3 corpus/legality/harness/run.py replay 5562524c286db0dd3f61`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes=ctx-instr-lower /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/1fef9ea05ecb70537da8f036deee1817ddf0cd71cba0c561cd6c049db5522672/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/5562524c286db0dd3f61/output.bc`
- **`c-pure-attr-wrapper`** (probe) — P1 `function(gvn)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 2 1 / -MEASURE H0 0 3 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 0f663bfc2a63fafc8404`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(gvn)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/0f663bfc2a63fafc8404/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -2,8 +2,6 @@
   QALLOC H0 0 1
   MEASURE H0 0 0 1
   MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   GATE 1 H0 0
   QFREE H0
   RET 2
  @@ -11,32 +9,20 @@
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P1 `function(instcombine)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -GATE 1 H0 0 / -GATE 1 H0 0
  - reproduce: `python3 corpus/legality/harness/run.py replay df976f3befa036979a67`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(instcombine)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/df976f3befa036979a67/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -4,7 +4,6 @@
   MEASURE H0 0 1 0
   MEASURE H0 0 2 1
   MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
  @@ -14,7 +13,6 @@
   MEASURE H0 0 2 0
   MEASURE H0 0 3 1
   GATE 1 H0 0
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P1 `function(instcombine<no-verify-fixpoint>)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -GATE 1 H0 0 / -GATE 1 H0 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 4bbb9c0c5ce149606570`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(instcombine<no-verify-fixpoint>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/4bbb9c0c5ce149606570/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -4,7 +4,6 @@
   MEASURE H0 0 1 0
   MEASURE H0 0 2 1
   MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
  @@ -14,7 +13,6 @@
   MEASURE H0 0 2 0
   MEASURE H0 0 3 1
   GATE 1 H0 0
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P1 `function(mem2reg)` — **L1** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -GATE 1 H0 0 / -GATE 1 H0 0
  - reproduce: `python3 corpus/legality/harness/run.py replay e26826ea9ef776101f26`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(mem2reg)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/e26826ea9ef776101f26/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -4,7 +4,6 @@
   MEASURE H0 0 1 0
   MEASURE H0 0 2 1
   MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
  @@ -14,7 +13,6 @@
   MEASURE H0 0 2 0
   MEASURE H0 0 3 1
   GATE 1 H0 0
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P1 `function(newgvn)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 2 1 / -MEASURE H0 0 3 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 5d6d89357aa61c005421`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(newgvn)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/5d6d89357aa61c005421/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -2,8 +2,6 @@
   QALLOC H0 0 1
   MEASURE H0 0 0 1
   MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   GATE 1 H0 0
   QFREE H0
   RET 2
  @@ -11,32 +9,20 @@
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P1 `function(sroa)` — **L1** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -GATE 1 H0 0 / -GATE 1 H0 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 77eafa97bc4297221cc4`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(sroa)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/77eafa97bc4297221cc4/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -4,7 +4,6 @@
   MEASURE H0 0 1 0
   MEASURE H0 0 2 1
   MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
  @@ -14,7 +13,6 @@
   MEASURE H0 0 2 0
   MEASURE H0 0 3 1
   GATE 1 H0 0
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P1 `function(tsan)` — **L5** — LLVM 18,20,23; modes post-O3; 3 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O0: native build failed at link; O3 object lacks marker externals __bennett_gate; O3: native build failed at link
  - reproduce: `python3 corpus/legality/harness/run.py replay c02b68d9987034ed8bb5`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(tsan)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/e22519ef40dcef0e52ef0210aa7c3518af2319d1b76a621c7a0bccf5e4149bc7/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/c02b68d9987034ed8bb5/output.bc`
- **`c-pure-attr-wrapper`** (probe) — P1 `hwasan` — **L5** — LLVM 18,20,23; modes post-O3; 3 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O0: native build failed at link; O3 object lacks marker externals __bennett_gate; O3: native build failed at link
  - reproduce: `python3 corpus/legality/harness/run.py replay 2687f5646d263d89565d`; opt: `/usr/lib/llvm-18/bin/opt -passes=hwasan /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/e22519ef40dcef0e52ef0210aa7c3518af2319d1b76a621c7a0bccf5e4149bc7/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/2687f5646d263d89565d/output.bc`
- **`c-pure-attr-wrapper`** (probe) — P1 `instrumentor` — **L5** — LLVM 23; modes post-O3; 1 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O0: native build failed at link; O3 object lacks marker externals __bennett_gate; O3: native build failed at link
  - reproduce: `python3 corpus/legality/harness/run.py replay a028d6c42a06eee1655d`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt -passes=instrumentor /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/1fef9ea05ecb70537da8f036deee1817ddf0cd71cba0c561cd6c049db5522672/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/a028d6c42a06eee1655d/output.bc`
- **`c-pure-attr-wrapper`** (probe) — P1 `internalize` — **L5** — LLVM 18,20,23; modes post-O3; 3 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O0: native build failed at link; O3 object lacks marker externals __bennett_gate; O3: native build failed at link
  - reproduce: `python3 corpus/legality/harness/run.py replay 6507b8fe10a1699fcb53`; opt: `/usr/lib/llvm-18/bin/opt -passes=internalize /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/e22519ef40dcef0e52ef0210aa7c3518af2319d1b76a621c7a0bccf5e4149bc7/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/6507b8fe10a1699fcb53/output.bc`
- **`c-pure-attr-wrapper`** (probe) — P1 `ipsccp` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -GATE 1 H0 0 / -GATE 1 H0 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 4785fd5ce5a1ce6bf615`; opt: `/usr/lib/llvm-18/bin/opt -passes=ipsccp /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/4785fd5ce5a1ce6bf615/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -4,7 +4,6 @@
   MEASURE H0 0 1 0
   MEASURE H0 0 2 1
   MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
  @@ -13,8 +12,6 @@
   MEASURE H0 0 1 1
   MEASURE H0 0 2 0
   MEASURE H0 0 3 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P1 `memprof-module` — **L5** — LLVM 18,20,23; modes post-O3; 3 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O0: native build failed at link; O3 object lacks marker externals __bennett_gate; O3: native build failed at link
  - reproduce: `python3 corpus/legality/harness/run.py replay a3234c831cd0fa900194`; opt: `/usr/lib/llvm-18/bin/opt -passes=memprof-module /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/e22519ef40dcef0e52ef0210aa7c3518af2319d1b76a621c7a0bccf5e4149bc7/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/a3234c831cd0fa900194/output.bc`
- **`c-pure-attr-wrapper`** (probe) — P1 `msan` — **L5** — LLVM 18,20,23; modes post-O3; 3 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O0: native build failed at link; O3 object lacks marker externals __bennett_gate; O3: native build failed at link
  - reproduce: `python3 corpus/legality/harness/run.py replay aa3342f6f39c5de1efc1`; opt: `/usr/lib/llvm-18/bin/opt -passes=msan /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/e22519ef40dcef0e52ef0210aa7c3518af2319d1b76a621c7a0bccf5e4149bc7/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/aa3342f6f39c5de1efc1/output.bc`
- **`c-pure-attr-wrapper`** (probe) — P1 `nsan` — **L5** — LLVM 20,23; modes post-O3; 2 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O0: native build failed at link; O3 object lacks marker externals __bennett_gate; O3: native build failed at link
  - reproduce: `python3 corpus/legality/harness/run.py replay 33774e23d4036854cb37`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes=nsan /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/1fef9ea05ecb70537da8f036deee1817ddf0cd71cba0c561cd6c049db5522672/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/33774e23d4036854cb37/output.bc`
- **`c-pure-attr-wrapper`** (probe) — P1 `rtsan` — **L5** — LLVM 20,23; modes post-O3; 2 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O0: native build failed at link; O3 object lacks marker externals __bennett_gate; O3: native build failed at link
  - reproduce: `python3 corpus/legality/harness/run.py replay e049c01788d683dd7ee3`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes=rtsan /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/1fef9ea05ecb70537da8f036deee1817ddf0cd71cba0c561cd6c049db5522672/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/e049c01788d683dd7ee3/output.bc`
- **`c-pure-attr-wrapper`** (probe) — P1 `scc-oz-module-inliner` — **L1,L5** — LLVM 18,20; modes raw; 2 cells
  - diagnosis: first trace difference: -MEASURE H0 0 2 1 / -MEASURE H0 0 3 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 52b3aaa3b5bde6bf8649`; opt: `/usr/lib/llvm-18/bin/opt -passes=scc-oz-module-inliner /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/52b3aaa3b5bde6bf8649/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -2,39 +2,27 @@
   QALLOC H0 0 1
   MEASURE H0 0 0 1
   MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P1 `tsan-module` — **L5** — LLVM 18,20,23; modes post-O3; 3 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O0: native build failed at link; O3 object lacks marker externals __bennett_gate; O3: native build failed at link
  - reproduce: `python3 corpus/legality/harness/run.py replay 69978136d836125ddd09`; opt: `/usr/lib/llvm-18/bin/opt -passes=tsan-module /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/e22519ef40dcef0e52ef0210aa7c3518af2319d1b76a621c7a0bccf5e4149bc7/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/69978136d836125ddd09/output.bc`
- **`c-pure-attr-wrapper`** (probe) — P1 `tysan` — **L5** — LLVM 20,23; modes post-O3; 2 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O0: native build failed at link; O3 object lacks marker externals __bennett_gate; O3: native build failed at link
  - reproduce: `python3 corpus/legality/harness/run.py replay fd0fe0fe5b7cc1f4cca6`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes=tysan /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/1fef9ea05ecb70537da8f036deee1817ddf0cd71cba0c561cd6c049db5522672/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/fd0fe0fe5b7cc1f4cca6/output.bc`
- **`c-pure-attr-wrapper`** (probe) — P2 `default<O1>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O3 object lacks marker externals __bennett_gate; first trace difference: -MEASURE H0 0 2 1 / -MEASURE H0 0 3 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 341f97c845e93042c492`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O1>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/341f97c845e93042c492/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -2,167 +2,95 @@
   QALLOC H0 0 1
   MEASURE H0 0 0 1
   MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P2 `default<O2>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O3 object lacks marker externals __bennett_gate; first trace difference: -MEASURE H0 0 2 1 / -MEASURE H0 0 3 0
  - reproduce: `python3 corpus/legality/harness/run.py replay bb4d671dc24c3a0a4742`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O2>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/bb4d671dc24c3a0a4742/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -2,167 +2,95 @@
   QALLOC H0 0 1
   MEASURE H0 0 0 1
   MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P2 `default<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O3 object lacks marker externals __bennett_gate; first trace difference: -MEASURE H0 0 2 1 / -MEASURE H0 0 3 0
  - reproduce: `python3 corpus/legality/harness/run.py replay af7002307aee5cf7d299`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/af7002307aee5cf7d299/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -2,167 +2,95 @@
   QALLOC H0 0 1
   MEASURE H0 0 0 1
   MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P2 `default<O3>,default<O3>,default<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O3 object lacks marker externals __bennett_gate; first trace difference: -MEASURE H0 0 2 1 / -MEASURE H0 0 3 0
  - reproduce: `python3 corpus/legality/harness/run.py replay fcb645495c988d923607`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O3>,default<O3>,default<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/fcb645495c988d923607/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -2,167 +2,95 @@
   QALLOC H0 0 1
   MEASURE H0 0 0 1
   MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P2 `default<Os>` — **L1,L5** — LLVM 18,20; modes raw; 2 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O3 object lacks marker externals __bennett_gate; first trace difference: -MEASURE H0 0 2 1 / -MEASURE H0 0 3 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 8e293951b6e573d318ab`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<Os>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/8e293951b6e573d318ab/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -2,167 +2,95 @@
   QALLOC H0 0 1
   MEASURE H0 0 0 1
   MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P2 `default<Oz>` — **L1,L5** — LLVM 18,20; modes raw; 2 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O3 object lacks marker externals __bennett_gate; first trace difference: -MEASURE H0 0 2 1 / -MEASURE H0 0 3 0
  - reproduce: `python3 corpus/legality/harness/run.py replay a3294dbc75d47fc23324`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<Oz>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/a3294dbc75d47fc23324/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -2,167 +2,95 @@
   QALLOC H0 0 1
   MEASURE H0 0 0 1
   MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P2 `lto-pre-link<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O3 object lacks marker externals __bennett_gate; first trace difference: -MEASURE H0 0 2 1 / -MEASURE H0 0 3 0
  - reproduce: `python3 corpus/legality/harness/run.py replay baac21cb6479ed9bb13e`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lto-pre-link<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/baac21cb6479ed9bb13e/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -2,167 +2,95 @@
   QALLOC H0 0 1
   MEASURE H0 0 0 1
   MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P2 `lto<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O3 object lacks marker externals __bennett_gate; first trace difference: -GATE 1 H0 0 / -GATE 1 H0 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 0b7f60a6264ff2009183`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lto<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/0b7f60a6264ff2009183/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -4,7 +4,6 @@
   MEASURE H0 0 1 0
   MEASURE H0 0 2 1
   MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
  @@ -13,8 +12,6 @@
   MEASURE H0 0 1 1
   MEASURE H0 0 2 0
   MEASURE H0 0 3 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P2 `thinlto-pre-link<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O3 object lacks marker externals __bennett_gate; first trace difference: -MEASURE H0 0 2 1 / -MEASURE H0 0 3 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 25d013e533ca9474aff3`; opt: `/usr/lib/llvm-18/bin/opt '-passes=thinlto-pre-link<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/25d013e533ca9474aff3/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -2,167 +2,95 @@
   QALLOC H0 0 1
   MEASURE H0 0 0 1
   MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P2 `thinlto<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O3 object lacks marker externals __bennett_gate; first trace difference: -GATE 1 H0 0 / -GATE 1 H0 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 331f40d15995832b1f3a`; opt: `/usr/lib/llvm-18/bin/opt '-passes=thinlto<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/331f40d15995832b1f3a/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -4,7 +4,6 @@
   MEASURE H0 0 1 0
   MEASURE H0 0 2 1
   MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
  @@ -13,8 +12,6 @@
   MEASURE H0 0 1 1
   MEASURE H0 0 2 0
   MEASURE H0 0 3 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P3 `197 random sequences, each containing a pass that FAILs alone on this case (cgscc(attributor-cgscc) 44, function(newgvn) 44, ipsccp 41, attributor 41, function(instcombine<no-verify-fixpoint>) 34, function(gvn) 25, scc-oz-module-inliner 23, function(sroa) 15, function(mem2reg) 9)` — **L1,L5** — LLVM 18,20,23; modes seq-0002,seq-0006,seq-0007,seq-0009,seq-0010,seq-0012,seq-0013,seq-0014,seq-0015,seq-0016,seq-0017,seq-0018,seq-0019,seq-0020,seq-0022,seq-0024,seq-0025,seq-0026,seq-0027,seq-0029,seq-0032,seq-0033,seq-0034,seq-0035,seq-0038,seq-0041,seq-0042,seq-0046,seq-0047,seq-0048,seq-0050,seq-0051,seq-0054,seq-0055,seq-0056,seq-0058,seq-0060,seq-0061,seq-0062,seq-0064,seq-0065,seq-0066,seq-0069,seq-0071,seq-0072,seq-0073,seq-0074,seq-0075,seq-0076,seq-0077,seq-0078,seq-0079,seq-0080,seq-0081,seq-0082,seq-0083,seq-0084,seq-0086,seq-0088,seq-0094,seq-0095,seq-0096,seq-0097,seq-0099,seq-0100,seq-0101,seq-0102,seq-0103,seq-0105,seq-0107,seq-0108,seq-0109,seq-0111,seq-0112,seq-0113,seq-0114,seq-0116,seq-0117,seq-0118,seq-0119,seq-0122,seq-0123,seq-0124,seq-0125,seq-0126,seq-0128,seq-0131,seq-0132,seq-0133,seq-0134,seq-0135,seq-0136,seq-0137,seq-0138,seq-0139,seq-0140,seq-0141,seq-0142,seq-0143,seq-0144,seq-0145,seq-0146,seq-0147,seq-0148,seq-0149,seq-0151,seq-0152,seq-0155,seq-0156,seq-0158,seq-0159,seq-0160,seq-0161,seq-0162,seq-0163,seq-0164,seq-0165,seq-0166,seq-0167,seq-0168,seq-0169,seq-0171,seq-0172,seq-0174,seq-0176,seq-0177,seq-0179,seq-0180,seq-0181,seq-0182,seq-0183,seq-0184,seq-0185,seq-0186,seq-0187,seq-0188,seq-0189,seq-0191,seq-0192,seq-0194,seq-0198,seq-0199; 197 cells
  - diagnosis: O0 object lacks marker externals __bennett_gate; O3 object lacks marker externals __bennett_gate; first trace difference: -GATE 1 H0 0 / -GATE 1 H0 0
  - reproduce: `python3 corpus/legality/harness/run.py replay e2f6e4d5139a055e01bc`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=annotation2metadata,function(loop(print)),function(print<cfg-sccs>),function(view-dom),cgscc(coro-annotation-elide),strip-dead-prototypes,function(print<phi-values>),function(callsite-splitting),function(ee-instrument),function(print<scev-division>),function(bounds-checking),deadargelim,function(verify<regions>),ipsccp,print<inline-advisor>,dxil-upgrade,function(loop-mssa(lnicm)),function(declare-to-assign),print<module-debuginfo>,function(print<domfrontier>),globalopt,function(lower-invoke),cgscc(function-attrs),ipsccp,function(memcpyopt),print<module-debuginfo>,function(lower-guard-intrinsic),function(loop(loop-unroll-full)),function(print<regions>),function(lower-widenable-condition),strip-dead-prototypes,print,openmp-opt,wholeprogramdevirt,function(loop-unroll),function(print<delinearization>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/061e5d555eff22206cdecfde78e090f2b9b47ae6248ff2d556609b03c08f735a/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/e2f6e4d5139a055e01bc/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -4,7 +4,6 @@
   MEASURE H0 0 1 0
   MEASURE H0 0 2 1
   MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
  @@ -13,8 +12,6 @@
   MEASURE H0 0 1 1
   MEASURE H0 0 2 0
   MEASURE H0 0 3 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P3 `6 random sequences, each containing a pass that FAILs alone on this case (attributor 3, function(instcombine<no-verify-fixpoint>) 2, function(mem2reg) 2, function(gvn) 1, ipsccp 1, cgscc(attributor-cgscc) 1)` — **L1,L2,L5** — LLVM 20,23; modes seq-0005,seq-0044,seq-0061,seq-0117,seq-0153; 6 cells
  - diagnosis: added forbidden readonly on __bennett_measure call; first trace difference: -GATE 1 H0 0 / -GATE 1 H0 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 118c93a20a64378189d7`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=attributor,function(print<scalar-evolution>),function(consthoist),function(view-dom),inliner-wrapper-no-mandatory-first,invalidate<all>,function(correlated-propagation),print-callgraph-sccs,function(mergereturn),function(flatten-cfg),function(loop-versioning),hipstdpar-interpose-alloc,function(instsimplify),function(print<stack-lifetime>),function(lower-switch),cgscc(attributor-light-cgscc),function(print<func-properties>),function(load-store-vectorizer),function(lower-switch),function(objc-arc),function(print<stack-lifetime>),embed-bitcode,function(loop(simple-loop-unswitch)),function(ee-instrument),function(instcombine<no-verify-fixpoint>),print-ir-similarity,extract-blocks,cgscc(no-op-cgscc),function(guard-widening),function(objc-arc),function(print<demanded-bits>),print<dxil-metadata>,function(lower-switch),function(dot-cfg),function(hardware-loops),iroutliner,deadargelim,always-inline,function(print<loops>),function(lower-invoke)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/118c93a20a64378189d7/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -4,7 +4,6 @@
   MEASURE H0 0 1 0
   MEASURE H0 0 2 1
   MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
  @@ -13,8 +12,6 @@
   MEASURE H0 0 1 1
   MEASURE H0 0 2 0
   MEASURE H0 0 3 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P3 `28 random sequences, each containing a pass that FAILs alone on this case (function(sroa) 16, function(mem2reg) 15)` — **L1** — LLVM 18,20,23; modes seq-0001,seq-0005,seq-0006,seq-0012,seq-0016,seq-0018,seq-0029,seq-0034,seq-0037,seq-0039,seq-0049,seq-0053,seq-0065,seq-0067,seq-0083,seq-0091,seq-0098,seq-0099,seq-0106,seq-0132,seq-0145,seq-0153,seq-0156,seq-0172,seq-0174,seq-0186,seq-0189; 28 cells
  - diagnosis: first trace difference: -GATE 1 H0 0 / -GATE 1 H0 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 39545e8a162b9f0309c8`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=cgscc(invalidate<all>),print-ir-similarity,function(unify-loop-exits),function(helloworld),function(mergereturn),function(dot-dom),cgscc(coro-split),cg-profile,function(libcalls-shrinkwrap),function(lower-allow-check),print<reg-usage>,verify,function(lint),function(nary-reassociate),function(print<func-properties>),function(mem2reg),strip-nondebug,lower-emutls,function(print<domtree>),function(invalidate<all>),called-value-propagation,function(verify<loops>),function(safe-stack),function(print<delinearization>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/39545e8a162b9f0309c8/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -4,7 +4,6 @@
   MEASURE H0 0 1 0
   MEASURE H0 0 2 1
   MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
  @@ -14,7 +13,6 @@
   MEASURE H0 0 2 0
   MEASURE H0 0 3 1
   GATE 1 H0 0
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P3 `seq-0105 (34 passes)` — **L1,L5** — LLVM 18; modes seq-0105; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -GATE 1 H0 0 / -GATE 1 H0 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 44d67cbacc56a1905fa0`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(dot-dom),function(objc-arc),function(mergeicmps),memprof-context-disambiguation,function(loop(loop-unroll-full)),function(loop(loop-unroll-and-jam)),function(pa-eval),function(print<func-properties>),function(aggressive-instcombine),function(helloworld),globaldce,function(print<branch-prob>),function(instsimplify),function(pa-eval),openmp-opt-postlink,pseudo-probe-update,function(break-crit-edges),function(objc-arc-contract),function(callbrprepare),deadargelim,print-lcg-dot,function(print-mustexecute),function(dse),iroutliner,inliner-wrapper,function(mergereturn),function(loop(loop-reduce)),function(slp-vectorizer),function(print<debug-ata>),debugify,constmerge,function(no-op-function),function(load-store-vectorizer),print<module-debuginfo>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/44d67cbacc56a1905fa0/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -4,7 +4,6 @@
   MEASURE H0 0 1 0
   MEASURE H0 0 2 1
   MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
  @@ -14,7 +13,6 @@
   MEASURE H0 0 2 0
   MEASURE H0 0 3 1
   GATE 1 H0 0
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P3 `seq-0014 (29 passes)` — **L1,L5** — LLVM 18; modes seq-0014; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -GATE 1 H0 0 / -GATE 1 H0 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 69df7ca080df16bcd61e`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(infer-address-spaces),function(print-mustexecute),function(loop-distribute),lower-global-dtors,function(wasm-eh-prepare),function(callbrprepare),lower-ifunc,function(print<da>),function(slp-vectorizer),function(gvn-sink),function(float2int),function(safe-stack),function(early-cse),shadow-stack-gc-lowering,function(flattencfg),print-must-be-executed-contexts,sanmd-module,function(assume-builder),function(print-memderefs),function(loop(loop-rotate)),function(alignment-from-assumptions),function(no-op-function),openmp-opt-postlink,rewrite-statepoints-for-gc,function(dse),function(print<delinearization>),function(print<branch-prob>),function(irce),function(early-cse)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/69df7ca080df16bcd61e/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -4,7 +4,6 @@
   MEASURE H0 0 1 0
   MEASURE H0 0 2 1
   MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
  @@ -14,7 +13,6 @@
   MEASURE H0 0 2 0
   MEASURE H0 0 3 1
   GATE 1 H0 0
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P3 `seq-0163 (13 passes)` — **L1,L5** — LLVM 23; modes seq-0163; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -GATE 1 H0 0 / -GATE 1 H0 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 894bb308a300a5b31be9`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=function(loop(loop-rotate)),function(wasm-eh-prepare),function(loop-mssa(licm)),function(view-cfg),function(loop(guard-widening)),pre-isel-intrinsic-lowering,function(partially-inline-libcalls),function(pgo-memop-opt),function(verify<scalar-evolution>),function(loop-data-prefetch),function(dot-post-dom-only),function(helloworld),function(bdce)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/061e5d555eff22206cdecfde78e090f2b9b47ae6248ff2d556609b03c08f735a/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/894bb308a300a5b31be9/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -25,7 +25,6 @@
   MEASURE H0 0 3 0
   GATE 1 H0 0
   GATE 1 H0 0
  -GATE 1 H0 0
   QFREE H0
   RET 3
   IN 3
  @@ -34,8 +33,6 @@
   MEASURE H0 0 1 1
   MEASURE H0 0 2 1
   MEASURE H0 0 3 1
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P3 `seq-0198 (7 passes)` — **L1,L5** — LLVM 20; modes seq-0198; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -GATE 1 H0 0 / -GATE 1 H0 0
  - reproduce: `python3 corpus/legality/harness/run.py replay 819e5061789c22544c1f`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(memcpyopt),pseudo-probe-update,function(separate-const-offset-from-gep),function(adce),global-merge,function(dse),function(speculative-execution)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/33f40909d4db449f0478920570ee30ae719cde60382da973d612cc2bea7f33f9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/819e5061789c22544c1f/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -4,7 +4,6 @@
   MEASURE H0 0 1 0
   MEASURE H0 0 2 1
   MEASURE H0 0 3 0
  -GATE 1 H0 0
   QFREE H0
   RET 2
   IN 1
  @@ -14,7 +13,6 @@
   MEASURE H0 0 2 0
   MEASURE H0 0 3 1
   GATE 1 H0 0
  ...
  ```
  </details>
- **`c-pure-attr-wrapper`** (probe) — P3 `seq-0047 (40 passes)` — **L2** — LLVM 23; modes seq-0047; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: added forbidden readonly on __bennett_measure call; added forbidden readnone on __bennett_gate call
  - reproduce: `python3 corpus/legality/harness/run.py replay fe2b0601cec8fde25486`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=lower-ifunc,function(redundant-dbg-inst-elim),function(loop(canon-freeze)),function(print<postdomtree>),function(ee-instrument),hipstdpar-math-fixup,coro-cleanup,function(dse),rpo-function-attrs,cgscc(invalidate<all>),function(assume-builder),function(flatten-cfg),iroutliner,function(simplifycfg),function(gvn-sink),drop-type-tests,function(print<memoryssa-walker>),function(annotation-remarks),function(print<da>),fatlto-cleanup,function(view-cfg),function(jump-threading),function(coro-elide),function(print<scalar-evolution>),pseudo-probe,function(verify<domtree>),function(scalarizer),mergefunc,function(print<assumptions>),function(loop(dot-ddg)),function(loop-fusion),cgscc(attributor-light-cgscc),function(lower-constant-intrinsics),cg-profile,scc-oz-module-inliner,strip-dead-cg-profile,function(gvn-sink),function(instsimplify),function(consthoist),function(print<func-properties>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/061e5d555eff22206cdecfde78e090f2b9b47ae6248ff2d556609b03c08f735a/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/fe2b0601cec8fde25486/output.bc`
- **`dbg-memcpy-handle-int`** (probe) — P1 `strip` — **L1,L4,L5** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region symbols changed rg->__unnamed_1, rpair->__unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_2; region is not a definition (missing, declaration, or alias): rg
  - reproduce: `python3 corpus/legality/harness/run.py replay 0fee8a1c801ba56b0857`; opt: `/usr/lib/llvm-18/bin/opt -passes=strip /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/6e712f533621bab09b4710a510bb5a5af5dd2f1f43cd696d0771d0c4bfd6e155/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/0fee8a1c801ba56b0857/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,11 +1,11 @@
   IN 0
   QALLOC H0 0 1
   GATE 2 H0 0
  -CTRL H0 0 F:rg 4
  -GATE 1 H0 0
  -END CTRL
  -QALLOC H1 0 1
  -ADJ F:rpair
  +CTRL H0 0 F:__unnamed_1 4
  +GATE 1 H0 0
  +END CTRL
  ...
  ```
  </details>
- **`dbg-memcpy-handle-int`** (probe) — P1 `strip-nondebug` — **L1,L4,L5** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region symbols changed rg->__unnamed_1, rpair->__unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_2; region is not a definition (missing, declaration, or alias): rg
  - reproduce: `python3 corpus/legality/harness/run.py replay e00c38a4a618e5ad4b5d`; opt: `/usr/lib/llvm-18/bin/opt -passes=strip-nondebug /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/6e712f533621bab09b4710a510bb5a5af5dd2f1f43cd696d0771d0c4bfd6e155/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/e00c38a4a618e5ad4b5d/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,11 +1,11 @@
   IN 0
   QALLOC H0 0 1
   GATE 2 H0 0
  -CTRL H0 0 F:rg 4
  -GATE 1 H0 0
  -END CTRL
  -QALLOC H1 0 1
  -ADJ F:rpair
  +CTRL H0 0 F:__unnamed_1 4
  +GATE 1 H0 0
  +END CTRL
  ...
  ```
  </details>
- **`dbg-memcpy-handle-int`** (probe) — P3 `73 random sequences, each containing a pass that FAILs alone on this case (strip 44, strip-nondebug 35)` — **L1,L4,L5** — LLVM 18,20,23; modes seq-0002,seq-0005,seq-0006,seq-0007,seq-0009,seq-0012,seq-0018,seq-0019,seq-0025,seq-0027,seq-0031,seq-0039,seq-0043,seq-0044,seq-0046,seq-0049,seq-0051,seq-0053,seq-0055,seq-0056,seq-0057,seq-0061,seq-0062,seq-0063,seq-0067,seq-0072,seq-0077,seq-0080,seq-0081,seq-0082,seq-0090,seq-0091,seq-0093,seq-0095,seq-0101,seq-0103,seq-0104,seq-0115,seq-0116,seq-0120,seq-0121,seq-0122,seq-0125,seq-0126,seq-0130,seq-0131,seq-0136,seq-0141,seq-0144,seq-0147,seq-0155,seq-0160,seq-0162,seq-0164,seq-0166,seq-0169,seq-0172,seq-0173,seq-0175,seq-0179,seq-0182,seq-0190,seq-0192,seq-0193,seq-0194; 73 cells
  - diagnosis: region symbols changed rg->__unnamed_1, rpair->__unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_2; region is not a definition (missing, declaration, or alias): rg
  - reproduce: `python3 corpus/legality/harness/run.py replay 7e821945cee092213776`; opt: `/usr/lib/llvm-18/bin/opt '-passes=canonicalize-aliases,function(tailcallelim),function(print<access-info>),function(print-cfg-sccs),always-inline,function(instsimplify),function(loop(loop-predication)),function(print<branch-prob>),function(assume-simplify),strip-nonlinetable-debuginfo,function(print<memoryssa-walker>),function(view-dom-only),function(verify<scalar-evolution>),function(assume-simplify),function(print<inliner-size-estimator>),strip-nondebug,function(loop-data-prefetch),wholeprogramdevirt,function(dce),function(lower-constant-intrinsics),function(dot-post-dom),hipstdpar-interpose-alloc' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/f57745a8234dcb0d225dedcbf6cdd237d8e5124e518ea93efdd7e6014bfa9840/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/7e821945cee092213776/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,11 +1,11 @@
   IN 0
   QALLOC H0 0 1
   GATE 2 H0 0
  -CTRL H0 0 F:rg 4
  -GATE 1 H0 0
  -END CTRL
  -QALLOC H1 0 1
  -ADJ F:rpair
  +CTRL H0 0 F:__unnamed_1 4
  +GATE 1 H0 0
  +END CTRL
  ...
  ```
  </details>
- **`dbg-region-operands`** (probe) — P1 `global-merge-func` — **L4** — LLVM 20,23; modes raw; 2 cells
  - diagnosis: region ora1 became a forwarding thunk to ora1.Tgm; region ora3 became a forwarding thunk to ora3.Tgm; region reg_f became a forwarding thunk to reg_f.Tgm; region reg_g became a forwarding thunk to reg_g.Tgm
  - reproduce: `python3 corpus/legality/harness/run.py replay 3c2ed73d0128a64af882`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes=global-merge-func /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/9cdb34610b4b8ce1bebf53dc97d9ba5003fa6d3c7e2674112b7747c10d1a65fa/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/3c2ed73d0128a64af882/output.bc`
- **`dbg-region-operands`** (probe) — P3 `19 random sequences, each containing a pass that FAILs alone on this case (global-merge-func 19)` — **L4** — LLVM 20,23; modes seq-0036,seq-0043,seq-0048,seq-0051,seq-0059,seq-0085,seq-0089,seq-0090,seq-0101,seq-0105,seq-0116,seq-0139,seq-0152,seq-0154,seq-0162,seq-0169,seq-0178,seq-0186,seq-0188; 19 cells
  - diagnosis: region ora1 became a forwarding thunk to ora1.Tgm; region ora3 became a forwarding thunk to ora3.Tgm; region reg_f became a forwarding thunk to reg_f.Tgm; region reg_g became a forwarding thunk to reg_g.Tgm
  - reproduce: `python3 corpus/legality/harness/run.py replay a186ffac4c1b966e3b1c`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=cgscc(inline),pre-isel-intrinsic-lowering,function(instsimplify),function(fix-irreducible),function(transform-warning),function(safe-stack),hotcoldsplit,function(load-store-vectorizer),function(invalidate<all>),cgscc(argpromotion),function(lcssa),cross-dso-cfi,function(dot-cfg-only),function(lower-guard-intrinsic),function(no-op-function),function(print<cost-model>),global-merge-func,function(lint),hotcoldsplit,inliner-wrapper-no-mandatory-first,function(unify-loop-exits),function(lower-expect),inliner-wrapper,function(verify<regions>),function(print<branch-prob>),iroutliner,strip-dead-debug-info' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/9cdb34610b4b8ce1bebf53dc97d9ba5003fa6d3c7e2674112b7747c10d1a65fa/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/a186ffac4c1b966e3b1c/output.bc`
- **`fp-rot-fastmath-reassoc`** (probe) — inherited `(any pass; behaviour identical to its input = default<O3> output; 358 pass/mode cells)` — **L1,L5** — LLVM 18,20,23; modes post-O3; 942 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay 1f0594aea9e712bb218c`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt -passes=alloc-token /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/f50db56321dd71a3010e0f5b1033885e657ec7f179756cc973003d631c1875aa/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/1f0594aea9e712bb218c/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — inherited `(any pass; behaviour identical to its input = untransformed input; 791 pass/mode cells)` — **L5** — LLVM 18,20,23; modes raw,seq-0000,seq-0001,seq-0002,seq-0003,seq-0004,seq-0005,seq-0006,seq-0007,seq-0008,seq-0009,seq-0010,seq-0011,seq-0012,seq-0013,seq-0014,seq-0015,seq-0016,seq-0017,seq-0018,seq-0019,seq-0020,seq-0021,seq-0022,seq-0023,seq-0024,seq-0025,seq-0026,seq-0027,seq-0028,seq-0029,seq-0030,seq-0031,seq-0032,seq-0033,seq-0034,seq-0035,seq-0036,seq-0037,seq-0038,seq-0039,seq-0040,seq-0041,seq-0042,seq-0043,seq-0044,seq-0045,seq-0046,seq-0047,seq-0048,seq-0049,seq-0050,seq-0051,seq-0052,seq-0053,seq-0054,seq-0055,seq-0056,seq-0057,seq-0058,seq-0059,seq-0060,seq-0061,seq-0062,seq-0063,seq-0064,seq-0065,seq-0066,seq-0067,seq-0068,seq-0069,seq-0070,seq-0071,seq-0072,seq-0073,seq-0074,seq-0075,seq-0076,seq-0077,seq-0078,seq-0079,seq-0080,seq-0081,seq-0082,seq-0083,seq-0084,seq-0085,seq-0086,seq-0087,seq-0088,seq-0089,seq-0090,seq-0091,seq-0092,seq-0093,seq-0094,seq-0095,seq-0096,seq-0097,seq-0098,seq-0099,seq-0100,seq-0101,seq-0102,seq-0103,seq-0104,seq-0105,seq-0106,seq-0107,seq-0108,seq-0109,seq-0110,seq-0111,seq-0112,seq-0113,seq-0114,seq-0115,seq-0116,seq-0117,seq-0118,seq-0119,seq-0120,seq-0121,seq-0122,seq-0123,seq-0124,seq-0125,seq-0126,seq-0127,seq-0128,seq-0129,seq-0130,seq-0131,seq-0132,seq-0133,seq-0134,seq-0135,seq-0136,seq-0137,seq-0138,seq-0139,seq-0140,seq-0141,seq-0142,seq-0143,seq-0144,seq-0145,seq-0146,seq-0147,seq-0148,seq-0149,seq-0150,seq-0151,seq-0152,seq-0153,seq-0154,seq-0155,seq-0156,seq-0157,seq-0158,seq-0159,seq-0160,seq-0161,seq-0162,seq-0163,seq-0164,seq-0165,seq-0167,seq-0168,seq-0169,seq-0170,seq-0171,seq-0172,seq-0173,seq-0174,seq-0175,seq-0176,seq-0177,seq-0178,seq-0179,seq-0180,seq-0181,seq-0182,seq-0183,seq-0184,seq-0185,seq-0186,seq-0187,seq-0188,seq-0189,seq-0190,seq-0191,seq-0192,seq-0193,seq-0194,seq-0195,seq-0196,seq-0197,seq-0198; 1365 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay 50cff3b796342f14bc35`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt -passes=alloc-token /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/50cff3b796342f14bc35/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O3
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P1 `embed-bitcode` — **L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay 00096a50516e9d49612c`; opt: `/usr/lib/llvm-18/bin/opt -passes=embed-bitcode /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/00096a50516e9d49612c/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O3
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P1 `function(instcombine)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay ebf315b1b131944160cc`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(instcombine)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/ebf315b1b131944160cc/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P1 `function(instcombine<no-verify-fixpoint>)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay 84293d8d97edbbcf7764`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(instcombine<no-verify-fixpoint>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/84293d8d97edbbcf7764/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P1 `function(loop-vectorize)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 3 H0 0 0x3fefffffffffffff / +ROT 3 H0 0 0x3ff0000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay f1d79923e0f555fb853f`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(loop-vectorize)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/f1d79923e0f555fb853f/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -9,440 +9,440 @@
   QALLOC H0 0 1
   ROT 1 H0 0 0x3fe3333333333334
   ROT 2 H0 0 0x3fd5555555555555
  -ROT 3 H0 0 0x3fefffffffffffff
  +ROT 3 H0 0 0x3ff0000000000000
   QFREE H0
   RET 1
   IN 2
   QALLOC H0 0 1
   ROT 1 H0 0 0x3fe6666666666666
   ROT 2 H0 0 0x3fe5555555555555
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P1 `function(reassociate)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay 86a6aaba87cb220b3077`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(reassociate)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/86a6aaba87cb220b3077/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P1 `scc-oz-module-inliner` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay aa5a014786fccb4abdd9`; opt: `/usr/lib/llvm-18/bin/opt -passes=scc-oz-module-inliner /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/aa5a014786fccb4abdd9/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P2 `default<O1>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay 2aaa93a00421e6f4bd75`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O1>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/2aaa93a00421e6f4bd75/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P2 `default<O2>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay ed0076b402e4169b3343`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O2>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/ed0076b402e4169b3343/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P2 `default<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay 70ca1e17508bff7a8ccf`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/70ca1e17508bff7a8ccf/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P2 `default<O3>,default<O3>,default<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay 3fd6a362ea162c17b104`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O3>,default<O3>,default<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/3fd6a362ea162c17b104/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P2 `default<Os>` — **L1,L5** — LLVM 18,20; modes raw; 2 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay 98ef89ccc34cccde2867`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<Os>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/98ef89ccc34cccde2867/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P2 `default<Oz>` — **L1,L5** — LLVM 18,20; modes raw; 2 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay 3bf43c85a688958d1bbf`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<Oz>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/3bf43c85a688958d1bbf/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P2 `lto-pre-link<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay 44a1d5b04fc7fd69646f`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lto-pre-link<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/44a1d5b04fc7fd69646f/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P2 `lto<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay a9868b3f79594ce65ba4`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lto<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/a9868b3f79594ce65ba4/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P2 `thinlto-pre-link<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay 6a9df159cb3383593feb`; opt: `/usr/lib/llvm-18/bin/opt '-passes=thinlto-pre-link<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/6a9df159cb3383593feb/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P2 `thinlto<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay 97e79403a7609180d63c`; opt: `/usr/lib/llvm-18/bin/opt '-passes=thinlto<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/97e79403a7609180d63c/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P3 `30 random sequences, each containing a pass that FAILs alone on this case (embed-bitcode 30)` — **L5** — LLVM 18,20,23; modes seq-0000,seq-0001,seq-0016,seq-0028,seq-0047,seq-0054,seq-0065,seq-0072,seq-0090,seq-0093,seq-0098,seq-0111,seq-0120,seq-0128,seq-0132,seq-0133,seq-0140,seq-0144,seq-0150,seq-0151,seq-0156,seq-0166,seq-0167,seq-0170,seq-0175,seq-0176,seq-0180,seq-0189,seq-0199; 30 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay db7c1fdada45111bb712`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=annotation2metadata,function(view-dom-only),function(break-crit-edges),embed-bitcode,function(instsimplify),function(loop(loop-simplifycfg)),extract-blocks,coro-cleanup,invalidate<all>,function(loop(print<loop-cache-cost>)),function(no-op-function),function(sandbox-vectorizer),hotcoldsplit,check-debugify,function(partially-inline-libcalls),inliner-wrapper,function(print),print<dxil-metadata>,function(early-cse),function(bdce),inferattrs,function(move-auto-init),function(print<access-info>),cgscc(argpromotion),function(adce),cgscc(attributor-light-cgscc),objc-arc-apelim,function(add-discriminators),function(loop(loop-simplifycfg)),function(lcssa),function(print<regions>),function(lower-allow-check),function(inject-tli-mappings),function(print<domtree>),function(print<memoryssa>),function(print<cycles>),function(loop-sink),loop-extract,verify' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/db7c1fdada45111bb712/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O3
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fastmath-reassoc`** (probe) — P3 `130 random sequences, each containing a pass that FAILs alone on this case (function(loop-vectorize) 41, function(reassociate) 40, function(instcombine<no-verify-fixpoint>) 39, scc-oz-module-inliner 31, embed-bitcode 15)` — **L1,L5** — LLVM 18,20,23; modes seq-0002,seq-0003,seq-0005,seq-0006,seq-0007,seq-0008,seq-0009,seq-0010,seq-0011,seq-0013,seq-0014,seq-0015,seq-0020,seq-0021,seq-0027,seq-0029,seq-0030,seq-0031,seq-0032,seq-0033,seq-0036,seq-0037,seq-0038,seq-0041,seq-0042,seq-0043,seq-0044,seq-0046,seq-0047,seq-0048,seq-0054,seq-0055,seq-0056,seq-0058,seq-0061,seq-0062,seq-0064,seq-0066,seq-0067,seq-0068,seq-0072,seq-0073,seq-0075,seq-0077,seq-0080,seq-0081,seq-0082,seq-0084,seq-0085,seq-0086,seq-0088,seq-0091,seq-0093,seq-0094,seq-0096,seq-0097,seq-0098,seq-0101,seq-0102,seq-0103,seq-0105,seq-0109,seq-0110,seq-0111,seq-0114,seq-0117,seq-0118,seq-0119,seq-0122,seq-0123,seq-0127,seq-0130,seq-0133,seq-0134,seq-0135,seq-0137,seq-0138,seq-0140,seq-0142,seq-0143,seq-0146,seq-0147,seq-0148,seq-0149,seq-0152,seq-0153,seq-0155,seq-0156,seq-0158,seq-0160,seq-0162,seq-0164,seq-0165,seq-0166,seq-0171,seq-0177,seq-0178,seq-0179,seq-0181,seq-0183,seq-0186,seq-0188,seq-0189,seq-0193,seq-0195,seq-0198,seq-0199; 130 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x3fe3333333333334 / +ROT 1 H0 0 0x3fe3333333333333
  - reproduce: `python3 corpus/legality/harness/run.py replay 4b0dffb070f05676f501`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=attributor,function(print<scalar-evolution>),function(consthoist),function(view-dom),inliner-wrapper-no-mandatory-first,invalidate<all>,function(correlated-propagation),print-callgraph-sccs,function(mergereturn),function(flatten-cfg),function(loop-versioning),hipstdpar-interpose-alloc,function(instsimplify),function(print<stack-lifetime>),function(lower-switch),cgscc(attributor-light-cgscc),function(print<func-properties>),function(load-store-vectorizer),function(lower-switch),function(objc-arc),function(print<stack-lifetime>),embed-bitcode,function(loop(simple-loop-unswitch)),function(ee-instrument),function(instcombine<no-verify-fixpoint>),print-ir-similarity,extract-blocks,cgscc(no-op-cgscc),function(guard-widening),function(objc-arc),function(print<demanded-bits>),print<dxil-metadata>,function(lower-switch),function(dot-cfg),function(hardware-loops),iroutliner,deadargelim,always-inline,function(print<loops>),function(lower-invoke)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/39e3723d14131c782ba824c5f5b104247316cee5e637fab115831a1f005a53ca/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/4b0dffb070f05676f501/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -7,7 +7,7 @@
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0x3fe3333333333334
  +ROT 1 H0 0 0x3fe3333333333333
   ROT 2 H0 0 0x3fd5555555555555
   ROT 3 H0 0 0x3fefffffffffffff
   QFREE H0
  @@ -28,7 +28,7 @@
   RET 3
   IN 4
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — inherited `(any pass; behaviour identical to its input = default<O3> output; 358 pass/mode cells)` — **L1,L5** — LLVM 18,20,23; modes post-O3; 942 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x0000000000000000 / -ROT 2 H0 0 0x0000000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 62c8a70638cac2f25148`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt -passes=alloc-token /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/d01602b66c7b90b66b192caca7e9bdb212188ce3362a20682677b3c4666bb7fb/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/62c8a70638cac2f25148/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 1 H0 0 0x3c90000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P1 `function(early-cse)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 2 H0 0 0x0000000000000000 / +ROT 2 H0 0 0x3c90000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay c253186285adc65efda8`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(early-cse)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/c253186285adc65efda8/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
   ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
   ROT 1 H0 0 0x0000000000000000
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P1 `function(gvn)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 2 H0 0 0x0000000000000000 / +ROT 2 H0 0 0x3c90000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay b0a72d716cf87ac7addc`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(gvn)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/b0a72d716cf87ac7addc/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
   ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
   ROT 1 H0 0 0x0000000000000000
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P1 `function(instcombine)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 2 H0 0 0x0000000000000000 / +ROT 2 H0 0 0x3c90000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 8913e63ad8f22ce2c2ed`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(instcombine)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/8913e63ad8f22ce2c2ed/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
   ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
   ROT 1 H0 0 0x0000000000000000
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P1 `function(instcombine<no-verify-fixpoint>)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 2 H0 0 0x0000000000000000 / +ROT 2 H0 0 0x3c90000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 24dbf9ff50bfc559bc25`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(instcombine<no-verify-fixpoint>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/24dbf9ff50bfc559bc25/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
   ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
   ROT 1 H0 0 0x0000000000000000
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P1 `function(instsimplify)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 2 H0 0 0x0000000000000000 / +ROT 2 H0 0 0x3c90000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay e8a023d05b7f27497a1b`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(instsimplify)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/e8a023d05b7f27497a1b/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
   ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
   ROT 1 H0 0 0x0000000000000000
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P1 `function(sccp)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 2 H0 0 0x0000000000000000 / +ROT 2 H0 0 0x3c90000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 2b9690258257e6006e24`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(sccp)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/2b9690258257e6006e24/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
   ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
   ROT 1 H0 0 0x0000000000000000
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P1 `ipsccp` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x0000000000000000 / -ROT 2 H0 0 0x0000000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay c667ca9258c4f4a40e2f`; opt: `/usr/lib/llvm-18/bin/opt -passes=ipsccp /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/c667ca9258c4f4a40e2f/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 1 H0 0 0x3c90000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P1 `scc-oz-module-inliner` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 2 H0 0 0x0000000000000000 / +ROT 2 H0 0 0x3c90000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay f4ac81b31a226dafd70e`; opt: `/usr/lib/llvm-18/bin/opt -passes=scc-oz-module-inliner /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/f4ac81b31a226dafd70e/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
   ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
   ROT 1 H0 0 0x0000000000000000
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P2 `default<O1>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x0000000000000000 / -ROT 2 H0 0 0x0000000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay ae08456cb5d418bf9314`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O1>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/ae08456cb5d418bf9314/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 1 H0 0 0x3c90000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P2 `default<O2>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x0000000000000000 / -ROT 2 H0 0 0x0000000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 8ae0eeeaead6cbf0a06f`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O2>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/8ae0eeeaead6cbf0a06f/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 1 H0 0 0x3c90000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P2 `default<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x0000000000000000 / -ROT 2 H0 0 0x0000000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay e7f10f46eb0bd333775d`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/e7f10f46eb0bd333775d/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 1 H0 0 0x3c90000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P2 `default<O3>,default<O3>,default<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x0000000000000000 / -ROT 2 H0 0 0x0000000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 60f712d78b447bdd32bb`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O3>,default<O3>,default<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/60f712d78b447bdd32bb/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 1 H0 0 0x3c90000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P2 `default<Os>` — **L1,L5** — LLVM 18,20; modes raw; 2 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x0000000000000000 / -ROT 2 H0 0 0x0000000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 9e9edd6950c2236e0344`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<Os>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/9e9edd6950c2236e0344/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 1 H0 0 0x3c90000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P2 `default<Oz>` — **L1,L5** — LLVM 18,20; modes raw; 2 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x0000000000000000 / -ROT 2 H0 0 0x0000000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 19c09e3caf58717273c2`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<Oz>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/19c09e3caf58717273c2/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 1 H0 0 0x3c90000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P2 `lto-pre-link<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x0000000000000000 / -ROT 2 H0 0 0x0000000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 41a3f8b72c22c9ebbb89`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lto-pre-link<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/41a3f8b72c22c9ebbb89/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 1 H0 0 0x3c90000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P2 `lto<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x0000000000000000 / -ROT 2 H0 0 0x0000000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 7b3631fbf684e9d72762`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lto<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/7b3631fbf684e9d72762/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 1 H0 0 0x3c90000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P2 `thinlto-pre-link<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x0000000000000000 / -ROT 2 H0 0 0x0000000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 74f13af1a2918d0cbff3`; opt: `/usr/lib/llvm-18/bin/opt '-passes=thinlto-pre-link<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/74f13af1a2918d0cbff3/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 1 H0 0 0x3c90000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P2 `thinlto<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x0000000000000000 / -ROT 2 H0 0 0x0000000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 43d03d590ac81445a34d`; opt: `/usr/lib/llvm-18/bin/opt '-passes=thinlto<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/93b37e16709bd5a86178d76b8161eeb2a41eb1aa641e8e4ce7f6193ba0169dd9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/43d03d590ac81445a34d/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 1 H0 0 0x3c90000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`fp-rot-fmuladd-fold`** (probe) — P3 `220 random sequences, each containing a pass that FAILs alone on this case (ipsccp 48, function(instsimplify) 48, function(sccp) 47, function(early-cse) 42, function(instcombine<no-verify-fixpoint>) 39, function(gvn) 33, scc-oz-module-inliner 31)` — **L1,L5** — LLVM 18,20,23; modes seq-0001,seq-0002,seq-0003,seq-0005,seq-0006,seq-0007,seq-0008,seq-0009,seq-0010,seq-0012,seq-0013,seq-0014,seq-0015,seq-0017,seq-0019,seq-0020,seq-0022,seq-0023,seq-0024,seq-0025,seq-0026,seq-0027,seq-0028,seq-0029,seq-0030,seq-0031,seq-0032,seq-0033,seq-0034,seq-0035,seq-0036,seq-0037,seq-0038,seq-0040,seq-0041,seq-0042,seq-0044,seq-0045,seq-0046,seq-0047,seq-0048,seq-0053,seq-0054,seq-0055,seq-0056,seq-0057,seq-0058,seq-0060,seq-0061,seq-0062,seq-0064,seq-0065,seq-0066,seq-0068,seq-0069,seq-0071,seq-0072,seq-0073,seq-0074,seq-0075,seq-0076,seq-0077,seq-0079,seq-0081,seq-0082,seq-0083,seq-0084,seq-0086,seq-0088,seq-0090,seq-0091,seq-0092,seq-0094,seq-0095,seq-0096,seq-0098,seq-0100,seq-0101,seq-0103,seq-0104,seq-0105,seq-0108,seq-0109,seq-0110,seq-0111,seq-0113,seq-0114,seq-0115,seq-0116,seq-0117,seq-0118,seq-0119,seq-0120,seq-0121,seq-0122,seq-0123,seq-0127,seq-0128,seq-0130,seq-0131,seq-0132,seq-0133,seq-0134,seq-0135,seq-0136,seq-0137,seq-0138,seq-0139,seq-0140,seq-0142,seq-0143,seq-0144,seq-0145,seq-0146,seq-0147,seq-0148,seq-0149,seq-0151,seq-0152,seq-0153,seq-0154,seq-0155,seq-0156,seq-0157,seq-0158,seq-0159,seq-0160,seq-0162,seq-0163,seq-0164,seq-0165,seq-0168,seq-0169,seq-0171,seq-0172,seq-0173,seq-0174,seq-0175,seq-0176,seq-0179,seq-0182,seq-0183,seq-0185,seq-0186,seq-0187,seq-0188,seq-0189,seq-0190,seq-0191,seq-0192,seq-0196,seq-0197,seq-0198,seq-0199; 220 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0x0000000000000000 / -ROT 2 H0 0 0x0000000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay b45e49dbd4702cae7ff8`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=annotation2metadata,function(loop(print)),function(print<cfg-sccs>),function(view-dom),cgscc(coro-annotation-elide),strip-dead-prototypes,function(print<phi-values>),function(callsite-splitting),function(ee-instrument),function(print<scev-division>),function(bounds-checking),deadargelim,function(verify<regions>),ipsccp,print<inline-advisor>,dxil-upgrade,function(loop-mssa(lnicm)),function(declare-to-assign),print<module-debuginfo>,function(print<domfrontier>),globalopt,function(lower-invoke),cgscc(function-attrs),ipsccp,function(memcpyopt),print<module-debuginfo>,function(lower-guard-intrinsic),function(loop(loop-unroll-full)),function(print<regions>),function(lower-widenable-condition),strip-dead-prototypes,print,openmp-opt,wholeprogramdevirt,function(loop-unroll),function(print<delinearization>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/46f257d881186e563236ea1dd4e6daa9151970d51fe39e595b904b8b62b5f9bb/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/b45e49dbd4702cae7ff8/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,28 +1,28 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0x0000000000000000
  -ROT 2 H0 0 0x0000000000000000
  +ROT 1 H0 0 0x3c90000000000000
  +ROT 2 H0 0 0x3c90000000000000
   ROT 3 H0 0 0x0000000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`fp-rot-nan-fold`** (probe) — inherited `(any pass; behaviour identical to its input = default<O3> output; 358 pass/mode cells)` — **L1,L5** — LLVM 18,20,23; modes post-O3; 942 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0xfff8000000000000 / -ROT 2 H0 0 0xfff8000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 65bc6a269451cc531840`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt -passes=alloc-token /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/ba1f939d68cebf44313aa98af3a69c705b812f029f9199a87dd503463445a296/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/65bc6a269451cc531840/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,24 +1,24 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  -ROT 2 H0 0 0xfff8000000000000
  +ROT 1 H0 0 0x7ff8000000000000
  +ROT 2 H0 0 0x7ff8000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  ...
  ```
  </details>
- **`fp-rot-nan-fold`** (probe) — P1 `attributor` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0xfff8000000000000 / -ROT 2 H0 0 0xfff8000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay ec538fffa32a74b6bffc`; opt: `/usr/lib/llvm-18/bin/opt -passes=attributor /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/4821594ec3e20f50f0caff79b9b1b1b1fa655f2250092848ae8b1ab9d45aac50/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/ec538fffa32a74b6bffc/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,24 +1,24 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  -ROT 2 H0 0 0xfff8000000000000
  +ROT 1 H0 0 0x7ff8000000000000
  +ROT 2 H0 0 0x7ff8000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  ...
  ```
  </details>
- **`fp-rot-nan-fold`** (probe) — P1 `cgscc(attributor-cgscc)` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0xfff8000000000000 / -ROT 2 H0 0 0xfff8000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay fccb1f6b4d458211af87`; opt: `/usr/lib/llvm-18/bin/opt '-passes=cgscc(attributor-cgscc)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/4821594ec3e20f50f0caff79b9b1b1b1fa655f2250092848ae8b1ab9d45aac50/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/fccb1f6b4d458211af87/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,24 +1,24 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  -ROT 2 H0 0 0xfff8000000000000
  +ROT 1 H0 0 0x7ff8000000000000
  +ROT 2 H0 0 0x7ff8000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  ...
  ```
  </details>
- **`fp-rot-nan-fold`** (probe) — P1 `globalopt` — **L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0xfff8000000000000 / -ROT 2 H0 0 0xfff8000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay d37a57bef8ad2faad769`; opt: `/usr/lib/llvm-18/bin/opt -passes=globalopt /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/4821594ec3e20f50f0caff79b9b1b1b1fa655f2250092848ae8b1ab9d45aac50/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/d37a57bef8ad2faad769/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O3
  @@ -1,24 +1,24 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  -ROT 2 H0 0 0xfff8000000000000
  +ROT 1 H0 0 0x7ff8000000000000
  +ROT 2 H0 0 0x7ff8000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  ...
  ```
  </details>
- **`fp-rot-nan-fold`** (probe) — P1 `ipsccp` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0xfff8000000000000 / -ROT 2 H0 0 0xfff8000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay dc3ef884dc8c10e14195`; opt: `/usr/lib/llvm-18/bin/opt -passes=ipsccp /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/4821594ec3e20f50f0caff79b9b1b1b1fa655f2250092848ae8b1ab9d45aac50/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/dc3ef884dc8c10e14195/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,24 +1,24 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  -ROT 2 H0 0 0xfff8000000000000
  +ROT 1 H0 0 0x7ff8000000000000
  +ROT 2 H0 0 0x7ff8000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  ...
  ```
  </details>
- **`fp-rot-nan-fold`** (probe) — P2 `default<O1>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0xfff8000000000000 / -ROT 2 H0 0 0xfff8000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 981eaf235590ef4a38e4`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O1>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/4821594ec3e20f50f0caff79b9b1b1b1fa655f2250092848ae8b1ab9d45aac50/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/981eaf235590ef4a38e4/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,24 +1,24 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  -ROT 2 H0 0 0xfff8000000000000
  +ROT 1 H0 0 0x7ff8000000000000
  +ROT 2 H0 0 0x7ff8000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  ...
  ```
  </details>
- **`fp-rot-nan-fold`** (probe) — P2 `default<O2>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0xfff8000000000000 / -ROT 2 H0 0 0xfff8000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay c0d8d5aa4b6114b1fc37`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O2>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/4821594ec3e20f50f0caff79b9b1b1b1fa655f2250092848ae8b1ab9d45aac50/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/c0d8d5aa4b6114b1fc37/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,24 +1,24 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  -ROT 2 H0 0 0xfff8000000000000
  +ROT 1 H0 0 0x7ff8000000000000
  +ROT 2 H0 0 0x7ff8000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  ...
  ```
  </details>
- **`fp-rot-nan-fold`** (probe) — P2 `default<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0xfff8000000000000 / -ROT 2 H0 0 0xfff8000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 361a4f95b993b9b7bde1`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/4821594ec3e20f50f0caff79b9b1b1b1fa655f2250092848ae8b1ab9d45aac50/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/361a4f95b993b9b7bde1/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,24 +1,24 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  -ROT 2 H0 0 0xfff8000000000000
  +ROT 1 H0 0 0x7ff8000000000000
  +ROT 2 H0 0 0x7ff8000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  ...
  ```
  </details>
- **`fp-rot-nan-fold`** (probe) — P2 `default<O3>,default<O3>,default<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0xfff8000000000000 / -ROT 2 H0 0 0xfff8000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay ffc5ed7272dc9abd4dd0`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O3>,default<O3>,default<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/4821594ec3e20f50f0caff79b9b1b1b1fa655f2250092848ae8b1ab9d45aac50/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/ffc5ed7272dc9abd4dd0/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,24 +1,24 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  -ROT 2 H0 0 0xfff8000000000000
  +ROT 1 H0 0 0x7ff8000000000000
  +ROT 2 H0 0 0x7ff8000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  ...
  ```
  </details>
- **`fp-rot-nan-fold`** (probe) — P2 `default<Os>` — **L1,L5** — LLVM 18,20; modes raw; 2 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0xfff8000000000000 / -ROT 2 H0 0 0xfff8000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 69cb98e294e37c9ae5be`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<Os>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/4821594ec3e20f50f0caff79b9b1b1b1fa655f2250092848ae8b1ab9d45aac50/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/69cb98e294e37c9ae5be/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,24 +1,24 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  -ROT 2 H0 0 0xfff8000000000000
  +ROT 1 H0 0 0x7ff8000000000000
  +ROT 2 H0 0 0x7ff8000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  ...
  ```
  </details>
- **`fp-rot-nan-fold`** (probe) — P2 `default<Oz>` — **L1,L5** — LLVM 18,20; modes raw; 2 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0xfff8000000000000 / -ROT 2 H0 0 0xfff8000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 3d7d8e4a2ae217b16e2c`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<Oz>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/4821594ec3e20f50f0caff79b9b1b1b1fa655f2250092848ae8b1ab9d45aac50/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/3d7d8e4a2ae217b16e2c/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,24 +1,24 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  -ROT 2 H0 0 0xfff8000000000000
  +ROT 1 H0 0 0x7ff8000000000000
  +ROT 2 H0 0 0x7ff8000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  ...
  ```
  </details>
- **`fp-rot-nan-fold`** (probe) — P2 `lto-pre-link<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0xfff8000000000000 / -ROT 2 H0 0 0xfff8000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay a8a247ab70e35cf11a17`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lto-pre-link<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/4821594ec3e20f50f0caff79b9b1b1b1fa655f2250092848ae8b1ab9d45aac50/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/a8a247ab70e35cf11a17/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,24 +1,24 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  -ROT 2 H0 0 0xfff8000000000000
  +ROT 1 H0 0 0x7ff8000000000000
  +ROT 2 H0 0 0x7ff8000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  ...
  ```
  </details>
- **`fp-rot-nan-fold`** (probe) — P2 `lto<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0xfff8000000000000 / -ROT 2 H0 0 0xfff8000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay b7f93552d78448279553`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lto<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/4821594ec3e20f50f0caff79b9b1b1b1fa655f2250092848ae8b1ab9d45aac50/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/b7f93552d78448279553/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,24 +1,24 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  -ROT 2 H0 0 0xfff8000000000000
  +ROT 1 H0 0 0x7ff8000000000000
  +ROT 2 H0 0 0x7ff8000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  ...
  ```
  </details>
- **`fp-rot-nan-fold`** (probe) — P2 `thinlto-pre-link<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0xfff8000000000000 / -ROT 2 H0 0 0xfff8000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 8e95c6fd00933da1a0ed`; opt: `/usr/lib/llvm-18/bin/opt '-passes=thinlto-pre-link<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/4821594ec3e20f50f0caff79b9b1b1b1fa655f2250092848ae8b1ab9d45aac50/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/8e95c6fd00933da1a0ed/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,24 +1,24 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  -ROT 2 H0 0 0xfff8000000000000
  +ROT 1 H0 0 0x7ff8000000000000
  +ROT 2 H0 0 0x7ff8000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  ...
  ```
  </details>
- **`fp-rot-nan-fold`** (probe) — P2 `thinlto<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0xfff8000000000000 / -ROT 2 H0 0 0xfff8000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 956e95254f56b0047efd`; opt: `/usr/lib/llvm-18/bin/opt '-passes=thinlto<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/4821594ec3e20f50f0caff79b9b1b1b1fa655f2250092848ae8b1ab9d45aac50/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/956e95254f56b0047efd/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,24 +1,24 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  -ROT 2 H0 0 0xfff8000000000000
  +ROT 1 H0 0 0x7ff8000000000000
  +ROT 2 H0 0 0x7ff8000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  ...
  ```
  </details>
- **`fp-rot-nan-fold`** (probe) — P3 `146 random sequences, each containing a pass that FAILs alone on this case (attributor 52, cgscc(attributor-cgscc) 51, ipsccp 48, globalopt 20)` — **L1,L5** — LLVM 18,20,23; modes seq-0002,seq-0005,seq-0006,seq-0007,seq-0008,seq-0010,seq-0012,seq-0014,seq-0015,seq-0016,seq-0017,seq-0018,seq-0020,seq-0022,seq-0025,seq-0026,seq-0027,seq-0029,seq-0031,seq-0032,seq-0033,seq-0034,seq-0035,seq-0036,seq-0037,seq-0038,seq-0044,seq-0048,seq-0050,seq-0051,seq-0054,seq-0056,seq-0060,seq-0061,seq-0062,seq-0065,seq-0066,seq-0069,seq-0071,seq-0072,seq-0073,seq-0074,seq-0075,seq-0076,seq-0078,seq-0079,seq-0081,seq-0082,seq-0083,seq-0089,seq-0093,seq-0095,seq-0096,seq-0097,seq-0098,seq-0099,seq-0100,seq-0101,seq-0102,seq-0103,seq-0107,seq-0109,seq-0112,seq-0116,seq-0117,seq-0118,seq-0120,seq-0121,seq-0122,seq-0123,seq-0124,seq-0125,seq-0126,seq-0128,seq-0131,seq-0132,seq-0133,seq-0134,seq-0136,seq-0137,seq-0138,seq-0139,seq-0140,seq-0141,seq-0143,seq-0144,seq-0145,seq-0146,seq-0147,seq-0148,seq-0149,seq-0150,seq-0151,seq-0152,seq-0153,seq-0155,seq-0159,seq-0160,seq-0161,seq-0167,seq-0169,seq-0172,seq-0174,seq-0175,seq-0176,seq-0179,seq-0180,seq-0181,seq-0182,seq-0183,seq-0185,seq-0186,seq-0187,seq-0188,seq-0189,seq-0191,seq-0192,seq-0194,seq-0195,seq-0198; 146 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0xfff8000000000000 / -ROT 2 H0 0 0xfff8000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay 4ede0b31c161f8ca07ad`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=annotation2metadata,function(loop(print)),function(print<cfg-sccs>),function(view-dom),cgscc(coro-annotation-elide),strip-dead-prototypes,function(print<phi-values>),function(callsite-splitting),function(ee-instrument),function(print<scev-division>),function(bounds-checking),deadargelim,function(verify<regions>),ipsccp,print<inline-advisor>,dxil-upgrade,function(loop-mssa(lnicm)),function(declare-to-assign),print<module-debuginfo>,function(print<domfrontier>),globalopt,function(lower-invoke),cgscc(function-attrs),ipsccp,function(memcpyopt),print<module-debuginfo>,function(lower-guard-intrinsic),function(loop(loop-unroll-full)),function(print<regions>),function(lower-widenable-condition),strip-dead-prototypes,print,openmp-opt,wholeprogramdevirt,function(loop-unroll),function(print<delinearization>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/00cca38d9f570f2ec515215f7e54d607b3c42bc91e0bff5b5c13cc330cf28f0b/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/4ede0b31c161f8ca07ad/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,24 +1,24 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  -ROT 2 H0 0 0xfff8000000000000
  +ROT 1 H0 0 0x7ff8000000000000
  +ROT 2 H0 0 0x7ff8000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  ...
  ```
  </details>
- **`fp-rot-nan-fold`** (probe) — P3 `24 random sequences, each containing a pass that FAILs alone on this case (globalopt 24)` — **L5** — LLVM 18,20,23; modes seq-0022,seq-0028,seq-0032,seq-0039,seq-0049,seq-0061,seq-0066,seq-0067,seq-0079,seq-0086,seq-0090,seq-0092,seq-0099,seq-0106,seq-0116,seq-0120,seq-0125,seq-0134,seq-0135,seq-0143,seq-0154,seq-0156,seq-0177,seq-0187; 24 cells
  - diagnosis: first trace difference: -ROT 1 H0 0 0xfff8000000000000 / -ROT 2 H0 0 0xfff8000000000000
  - reproduce: `python3 corpus/legality/harness/run.py replay d33f0ad626c916be08da`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=cg-profile,strip-dead-prototypes,function(move-auto-init),inliner-wrapper-no-mandatory-first,function(verify<scalar-evolution>),pseudo-probe-update,name-anon-globals,function(loop(loop-term-fold)),function(callbr-prepare),function(view-cfg),function(loop(loop-predication)),sancov-module,lower-ifunc,annotation2metadata,cgscc(inline),called-value-propagation,function(helloworld),function(print<loops>),function(cfguard),function(print<postdomtree>),function(correlated-propagation),function(print<memoryssa>),function(dot-dom-only),function(print<stack-lifetime>),print<dxil-metadata>,globalopt,function(helloworld),function(loop-mssa(licm)),inferattrs' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/4821594ec3e20f50f0caff79b9b1b1b1fa655f2250092848ae8b1ab9d45aac50/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/d33f0ad626c916be08da/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O3
  @@ -1,24 +1,24 @@
   IN 0
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  -ROT 2 H0 0 0xfff8000000000000
  +ROT 1 H0 0 0x7ff8000000000000
  +ROT 2 H0 0 0x7ff8000000000000
   QFREE H0
   RET 0
   IN 1
   QALLOC H0 0 1
  -ROT 1 H0 0 0xfff8000000000000
  ...
  ```
  </details>
- **`inline-always-into-region`** (legal) — P1 `strip` — **L1,L4,L5** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region symbols changed region_kick->__unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): region_kick; first trace difference: -CTRL H0 0 F:region_kick 8 / +CTRL H0 0 F:__unnamed_1 8
  - reproduce: `python3 corpus/legality/harness/run.py replay 51ec6445c8c8a0ef0c00`; opt: `/usr/lib/llvm-18/bin/opt -passes=strip /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/2b36214a2120604d1ac4007f7d4f81092e4ba2e4fd963f7a3297561634f86cc1/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/51ec6445c8c8a0ef0c00/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -3,7 +3,7 @@
   QALLOC H1 0 2
   GATE 5 H0 0
   GATE 6 H0 0
  -CTRL H0 0 F:region_kick 8
  +CTRL H0 0 F:__unnamed_1 8
   GATE 5 H1 0
   GATE 6 H1 0
   GATE 5 H1 1
  @@ -18,7 +18,7 @@
   QALLOC H1 0 2
   GATE 5 H0 0
  ...
  ```
  </details>
- **`inline-always-into-region`** (legal) — P1 `strip-nondebug` — **L1,L4,L5** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region symbols changed region_kick->__unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): region_kick; first trace difference: -CTRL H0 0 F:region_kick 8 / +CTRL H0 0 F:__unnamed_1 8
  - reproduce: `python3 corpus/legality/harness/run.py replay 46f98836cea212bf16ea`; opt: `/usr/lib/llvm-18/bin/opt -passes=strip-nondebug /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/2b36214a2120604d1ac4007f7d4f81092e4ba2e4fd963f7a3297561634f86cc1/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/46f98836cea212bf16ea/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -3,7 +3,7 @@
   QALLOC H1 0 2
   GATE 5 H0 0
   GATE 6 H0 0
  -CTRL H0 0 F:region_kick 8
  +CTRL H0 0 F:__unnamed_1 8
   GATE 5 H1 0
   GATE 6 H1 0
   GATE 5 H1 1
  @@ -18,7 +18,7 @@
   QALLOC H1 0 2
   GATE 5 H0 0
  ...
  ```
  </details>
- **`inline-always-into-region`** (legal) — P3 `73 random sequences, each containing a pass that FAILs alone on this case (strip 44, strip-nondebug 35)` — **L1,L4,L5** — LLVM 18,20,23; modes seq-0002,seq-0005,seq-0006,seq-0007,seq-0009,seq-0012,seq-0018,seq-0019,seq-0025,seq-0027,seq-0031,seq-0039,seq-0043,seq-0044,seq-0046,seq-0049,seq-0051,seq-0053,seq-0055,seq-0056,seq-0057,seq-0061,seq-0062,seq-0063,seq-0067,seq-0072,seq-0077,seq-0080,seq-0081,seq-0082,seq-0090,seq-0091,seq-0093,seq-0095,seq-0101,seq-0103,seq-0104,seq-0115,seq-0116,seq-0120,seq-0121,seq-0122,seq-0125,seq-0126,seq-0130,seq-0131,seq-0136,seq-0141,seq-0144,seq-0147,seq-0155,seq-0160,seq-0162,seq-0164,seq-0166,seq-0169,seq-0172,seq-0173,seq-0175,seq-0179,seq-0182,seq-0190,seq-0192,seq-0193,seq-0194; 73 cells
  - diagnosis: region symbols changed region_kick->__unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): region_kick; first trace difference: -CTRL H0 0 F:region_kick 8 / +CTRL H0 0 F:__unnamed_1 8
  - reproduce: `python3 corpus/legality/harness/run.py replay ac18a524c41e57f1b823`; opt: `/usr/lib/llvm-18/bin/opt '-passes=canonicalize-aliases,function(tailcallelim),function(print<access-info>),function(print-cfg-sccs),always-inline,function(instsimplify),function(loop(loop-predication)),function(print<branch-prob>),function(assume-simplify),strip-nonlinetable-debuginfo,function(print<memoryssa-walker>),function(view-dom-only),function(verify<scalar-evolution>),function(assume-simplify),function(print<inliner-size-estimator>),strip-nondebug,function(loop-data-prefetch),wholeprogramdevirt,function(dce),function(lower-constant-intrinsics),function(dot-post-dom),hipstdpar-interpose-alloc' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/a24e939e5b7c1348c394d6d03643aa2a6220ab08692ffec9996c2ba4f40b42e2/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/ac18a524c41e57f1b823/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -3,7 +3,7 @@
   QALLOC H1 0 2
   GATE 5 H0 0
   GATE 6 H0 0
  -CTRL H0 0 F:region_kick 8
  +CTRL H0 0 F:__unnamed_1 8
   GATE 5 H1 0
   GATE 6 H1 0
   GATE 5 H1 1
  @@ -18,7 +18,7 @@
   QALLOC H1 0 2
   GATE 5 H0 0
  ...
  ```
  </details>
- **`ipo-globalopt-region-bool`** (probe) — P1 `attributor` — **L1,L4,L5** — LLVM 18,20; modes post-O3,raw; 4 cells
  - diagnosis: region symbols changed r_b->r_a; first trace difference: -ADJ F:r_b / -GATE 21 H0 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 16c0afeb717debd80ea6`; opt: `/usr/lib/llvm-18/bin/opt -passes=attributor /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/274a7d32dc6d2dfce5da8b6a0c87675ab467f57010bacc2409480928293784c5/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/16c0afeb717debd80ea6/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -70,49 +70,43 @@
   RET 9
   IN 10
   QALLOC H0 0 2
  -ADJ F:r_b
  -GATE 21 H0 1
  -GATE 22 H0 0
  +ADJ F:r_a
  +GATE 20 H0 0
   END ADJ
   QFREE H0
   RET 10
  ...
  ```
  </details>
- **`ipo-globalopt-region-bool`** (probe) — P1 `cgscc(attributor-cgscc)` — **L1,L4,L5** — LLVM 18,20; modes post-O3,raw; 4 cells
  - diagnosis: region symbols changed r_b->r_a; first trace difference: -ADJ F:r_b / -GATE 21 H0 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 848826c92b17990f241f`; opt: `/usr/lib/llvm-18/bin/opt '-passes=cgscc(attributor-cgscc)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/274a7d32dc6d2dfce5da8b6a0c87675ab467f57010bacc2409480928293784c5/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/848826c92b17990f241f/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -70,49 +70,43 @@
   RET 9
   IN 10
   QALLOC H0 0 2
  -ADJ F:r_b
  -GATE 21 H0 1
  -GATE 22 H0 0
  +ADJ F:r_a
  +GATE 20 H0 0
   END ADJ
   QFREE H0
   RET 10
  ...
  ```
  </details>
- **`ipo-globalopt-region-bool`** (probe) — P3 `72 random sequences, each containing a pass that FAILs alone on this case (cgscc(attributor-cgscc) 42, attributor 36)` — **L1,L4,L5** — LLVM 18,20; modes seq-0002,seq-0005,seq-0010,seq-0012,seq-0014,seq-0015,seq-0016,seq-0018,seq-0020,seq-0025,seq-0026,seq-0027,seq-0032,seq-0035,seq-0038,seq-0044,seq-0048,seq-0050,seq-0061,seq-0062,seq-0065,seq-0069,seq-0074,seq-0075,seq-0079,seq-0081,seq-0083,seq-0089,seq-0096,seq-0097,seq-0099,seq-0100,seq-0101,seq-0102,seq-0107,seq-0112,seq-0117,seq-0118,seq-0124,seq-0125,seq-0128,seq-0138,seq-0139,seq-0140,seq-0141,seq-0143,seq-0144,seq-0145,seq-0146,seq-0147,seq-0148,seq-0149,seq-0152,seq-0160,seq-0161,seq-0167,seq-0174,seq-0175,seq-0179,seq-0180,seq-0181,seq-0185,seq-0186,seq-0187,seq-0194,seq-0195; 72 cells
  - diagnosis: region symbols changed r_b->r_a; first trace difference: -ADJ F:r_b / -GATE 21 H0 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 3946244de246c8b76dc2`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=attributor,function(print<scalar-evolution>),function(consthoist),function(view-dom),inliner-wrapper-no-mandatory-first,invalidate<all>,function(correlated-propagation),print-callgraph-sccs,function(mergereturn),function(flatten-cfg),function(loop-versioning),hipstdpar-interpose-alloc,function(instsimplify),function(print<stack-lifetime>),function(lower-switch),cgscc(attributor-light-cgscc),function(print<func-properties>),function(load-store-vectorizer),function(lower-switch),function(objc-arc),function(print<stack-lifetime>),embed-bitcode,function(loop(simple-loop-unswitch)),function(ee-instrument),function(instcombine<no-verify-fixpoint>),print-ir-similarity,extract-blocks,cgscc(no-op-cgscc),function(guard-widening),function(objc-arc),function(print<demanded-bits>),print<dxil-metadata>,function(lower-switch),function(dot-cfg),function(hardware-loops),iroutliner,deadargelim,always-inline,function(print<loops>),function(lower-invoke)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/c85b0e5e3e87df7231a0c115b5edb96d353b1be201030b0a5306ec51a4da5247/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/3946244de246c8b76dc2/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -70,49 +70,43 @@
   RET 9
   IN 10
   QALLOC H0 0 2
  -ADJ F:r_b
  -GATE 21 H0 1
  -GATE 22 H0 0
  +ADJ F:r_a
  +GATE 20 H0 0
   END ADJ
   QFREE H0
   RET 10
  ...
  ```
  </details>
- **`ipo-ipsccp-funcspec-region`** (legal) — P1 `iroutliner` — **L4** — LLVM 18; modes post-O3; 1 cells
  - diagnosis: region rz became a forwarding thunk to outlined_ir_func_0
  - reproduce: `python3 corpus/legality/harness/run.py replay 361495c30341ecb3a7ec`; opt: `/usr/lib/llvm-18/bin/opt -passes=iroutliner /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/d710a53a72396efa43fce22ff3121e4753dd9f61c3c3c302fb32cacdc0e38b36/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/361495c30341ecb3a7ec/output.bc`
- **`ipo-ipsccp-funcspec-region`** (legal) — P3 `seq-0117 (40 passes)` — **L4** — LLVM 20; modes seq-0117; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: region rz became a forwarding thunk to outlined_ir_func_0
  - reproduce: `python3 corpus/legality/harness/run.py replay 547ecb2d4ef320eb2b9f`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=attributor,function(print<scalar-evolution>),function(consthoist),function(view-dom),inliner-wrapper-no-mandatory-first,invalidate<all>,function(correlated-propagation),print-callgraph-sccs,function(mergereturn),function(flatten-cfg),function(loop-versioning),hipstdpar-interpose-alloc,function(instsimplify),function(print<stack-lifetime>),function(lower-switch),cgscc(attributor-light-cgscc),function(print<func-properties>),function(load-store-vectorizer),function(lower-switch),function(objc-arc),function(print<stack-lifetime>),embed-bitcode,function(loop(simple-loop-unswitch)),function(ee-instrument),function(instcombine<no-verify-fixpoint>),print-ir-similarity,extract-blocks,cgscc(no-op-cgscc),function(guard-widening),function(objc-arc),function(print<demanded-bits>),print<dxil-metadata>,function(lower-switch),function(dot-cfg),function(hardware-loops),iroutliner,deadargelim,always-inline,function(print<loops>),function(lower-invoke)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/8a16271d01edb20728e371b5334d45775d51dac4b4af1a007e8c9e7455814fe3/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/547ecb2d4ef320eb2b9f/output.bc`
- **`region-global-state`** (legal) — P1 `function(normalize)` — **L1,L5** — LLVM 20,23; modes raw; 2 cells
  - diagnosis: first trace difference: -RET 606 / +RET 6
  - reproduce: `python3 corpus/legality/harness/run.py replay a496f3b79db009551593`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(normalize)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/990a73b04a2a1e767c5f83074cd9003f0e017d25f76a20c939560dd76c4bd888/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/a496f3b79db009551593/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -6,7 +6,7 @@
   GATE 2 H0 0
   END COMPUTE
   QFREE H0
  -RET 606
  +RET 6
   IN 1
   QALLOC H0 0 2
   COMPUTE F:bump F:peek
  @@ -15,7 +15,7 @@
   GATE 2 H0 0
   END COMPUTE
  ...
  ```
  </details>
- **`region-global-state`** (legal) — P1 `strip` — **L1,L4,L5** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region symbols changed bump->__unnamed_1, peek->__unnamed_4; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_4; region is not a definition (missing, declaration, or alias): bump
  - reproduce: `python3 corpus/legality/harness/run.py replay 8e2c95374c2e4d62d3c8`; opt: `/usr/lib/llvm-18/bin/opt -passes=strip /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/328f8c2244bde6447f7dd5ec201fb1654b77ef32f02d26d997c5e1d220684183/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/8e2c95374c2e4d62d3c8/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,6 +1,6 @@
   IN 0
   QALLOC H0 0 2
  -COMPUTE F:bump F:peek
  +COMPUTE F:__unnamed_1 F:__unnamed_4
   GATE 2 H0 0
   GATE 5 H0 1
   GATE 2 H0 0
  @@ -9,7 +9,7 @@
   RET 606
   IN 1
   QALLOC H0 0 2
  ...
  ```
  </details>
- **`region-global-state`** (legal) — P1 `strip-nondebug` — **L1,L4,L5** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region symbols changed bump->__unnamed_1, peek->__unnamed_4; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_4; region is not a definition (missing, declaration, or alias): bump
  - reproduce: `python3 corpus/legality/harness/run.py replay d4e5b4bb10a1723c8f52`; opt: `/usr/lib/llvm-18/bin/opt -passes=strip-nondebug /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/328f8c2244bde6447f7dd5ec201fb1654b77ef32f02d26d997c5e1d220684183/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/d4e5b4bb10a1723c8f52/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,6 +1,6 @@
   IN 0
   QALLOC H0 0 2
  -COMPUTE F:bump F:peek
  +COMPUTE F:__unnamed_1 F:__unnamed_4
   GATE 2 H0 0
   GATE 5 H0 1
   GATE 2 H0 0
  @@ -9,7 +9,7 @@
   RET 606
   IN 1
   QALLOC H0 0 2
  ...
  ```
  </details>
- **`region-global-state`** (legal) — P3 `73 random sequences, each containing a pass that FAILs alone on this case (strip 44, strip-nondebug 35, function(normalize) 3)` — **L1,L4,L5** — LLVM 18,20,23; modes seq-0002,seq-0005,seq-0006,seq-0007,seq-0009,seq-0012,seq-0018,seq-0019,seq-0025,seq-0027,seq-0031,seq-0039,seq-0043,seq-0044,seq-0046,seq-0049,seq-0051,seq-0053,seq-0055,seq-0056,seq-0057,seq-0061,seq-0062,seq-0063,seq-0067,seq-0072,seq-0077,seq-0080,seq-0081,seq-0082,seq-0090,seq-0091,seq-0093,seq-0095,seq-0101,seq-0103,seq-0104,seq-0115,seq-0116,seq-0120,seq-0121,seq-0122,seq-0125,seq-0126,seq-0130,seq-0131,seq-0136,seq-0141,seq-0144,seq-0147,seq-0155,seq-0160,seq-0162,seq-0164,seq-0166,seq-0169,seq-0172,seq-0173,seq-0175,seq-0179,seq-0182,seq-0190,seq-0192,seq-0193,seq-0194; 73 cells
  - diagnosis: region symbols changed bump->__unnamed_1, peek->__unnamed_4; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_4; region is not a definition (missing, declaration, or alias): bump
  - reproduce: `python3 corpus/legality/harness/run.py replay 50c2df33899ad1befff7`; opt: `/usr/lib/llvm-18/bin/opt '-passes=canonicalize-aliases,function(tailcallelim),function(print<access-info>),function(print-cfg-sccs),always-inline,function(instsimplify),function(loop(loop-predication)),function(print<branch-prob>),function(assume-simplify),strip-nonlinetable-debuginfo,function(print<memoryssa-walker>),function(view-dom-only),function(verify<scalar-evolution>),function(assume-simplify),function(print<inliner-size-estimator>),strip-nondebug,function(loop-data-prefetch),wholeprogramdevirt,function(dce),function(lower-constant-intrinsics),function(dot-post-dom),hipstdpar-interpose-alloc' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/990a73b04a2a1e767c5f83074cd9003f0e017d25f76a20c939560dd76c4bd888/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/50c2df33899ad1befff7/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,6 +1,6 @@
   IN 0
   QALLOC H0 0 2
  -COMPUTE F:bump F:peek
  +COMPUTE F:__unnamed_1 F:__unnamed_4
   GATE 2 H0 0
   GATE 5 H0 1
   GATE 2 H0 0
  @@ -9,7 +9,7 @@
   RET 606
   IN 1
   QALLOC H0 0 2
  ...
  ```
  </details>
- **`region-global-state`** (legal) — P3 `16 random sequences, each containing a pass that FAILs alone on this case (function(normalize) 16)` — **L1,L5** — LLVM 20,23; modes seq-0005,seq-0013,seq-0041,seq-0042,seq-0048,seq-0052,seq-0060,seq-0074,seq-0093,seq-0101,seq-0135,seq-0157,seq-0173,seq-0177,seq-0193,seq-0197; 16 cells
  - diagnosis: first trace difference: -RET 606 / +RET 6
  - reproduce: `python3 corpus/legality/harness/run.py replay d5511d781eefc28dabb1`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=cgscc(attributor-light-cgscc),function(irce),function(loop-mssa(licm)),jmc-instrumenter,function(invalidate<all>),function(print<assumptions>),loop-extract,function(normalize),function(declare-to-assign),print,function(scalarizer),coro-early,function(simplifycfg),shadow-stack-gc-lowering,function(lower-invoke),cross-dso-cfi,openmp-opt-postlink,function(dot-cfg-only),function(guard-widening),openmp-opt,function(loop(loop-versioning-licm))' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/990a73b04a2a1e767c5f83074cd9003f0e017d25f76a20c939560dd76c4bd888/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/d5511d781eefc28dabb1/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -6,7 +6,7 @@
   GATE 2 H0 0
   END COMPUTE
   QFREE H0
  -RET 606
  +RET 6
   IN 1
   QALLOC H0 0 2
   COMPUTE F:bump F:peek
  @@ -15,7 +15,7 @@
   GATE 2 H0 0
   END COMPUTE
  ...
  ```
  </details>
- **`region-inplace-selfinverse`** (probe) — P1 `mergefunc` — **L4** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region xor_k_inv became a forwarding thunk to xor_k
  - reproduce: `python3 corpus/legality/harness/run.py replay d15a830cc1f23425bef5`; opt: `/usr/lib/llvm-18/bin/opt -passes=mergefunc /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fbabf6e0810aadcf0a6b3a841f610e86ca2de4affebbba20e9ca5e3d088538ee/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/d15a830cc1f23425bef5/output.bc`
- **`region-inplace-selfinverse`** (probe) — P1 `strip` — **L1,L4,L5** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region symbols changed use_parity->__unnamed_3, xor_k->__unnamed_1, xor_k_inv->__unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_3
  - reproduce: `python3 corpus/legality/harness/run.py replay bd6011c917380cdeec0c`; opt: `/usr/lib/llvm-18/bin/opt -passes=strip /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fbabf6e0810aadcf0a6b3a841f610e86ca2de4affebbba20e9ca5e3d088538ee/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/bd6011c917380cdeec0c/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,8 +1,8 @@
   IN 0
   QALLOC H0 0 4
  -INPLACE F:xor_k F:xor_k_inv
  -END INPLACE
  -COMPUTE F:xor_k F:use_parity
  +INPLACE F:__unnamed_1 F:__unnamed_2
  +END INPLACE
  +COMPUTE F:__unnamed_1 F:__unnamed_3
   GATE2 3 H0 0 H0 3
   END COMPUTE
   MEASURE H0 3 0 1
  ...
  ```
  </details>
- **`region-inplace-selfinverse`** (probe) — P1 `strip-nondebug` — **L1,L4,L5** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region symbols changed use_parity->__unnamed_3, xor_k->__unnamed_1, xor_k_inv->__unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_3
  - reproduce: `python3 corpus/legality/harness/run.py replay a568bf45d532d43547cc`; opt: `/usr/lib/llvm-18/bin/opt -passes=strip-nondebug /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fbabf6e0810aadcf0a6b3a841f610e86ca2de4affebbba20e9ca5e3d088538ee/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/a568bf45d532d43547cc/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,8 +1,8 @@
   IN 0
   QALLOC H0 0 4
  -INPLACE F:xor_k F:xor_k_inv
  -END INPLACE
  -COMPUTE F:xor_k F:use_parity
  +INPLACE F:__unnamed_1 F:__unnamed_2
  +END INPLACE
  +COMPUTE F:__unnamed_1 F:__unnamed_3
   GATE2 3 H0 0 H0 3
   END COMPUTE
   MEASURE H0 3 0 1
  ...
  ```
  </details>
- **`region-inplace-selfinverse`** (probe) — P3 `73 random sequences, each containing a pass that FAILs alone on this case (strip 44, strip-nondebug 35, mergefunc 5)` — **L1,L4,L5** — LLVM 18,20,23; modes seq-0002,seq-0005,seq-0006,seq-0007,seq-0009,seq-0012,seq-0018,seq-0019,seq-0025,seq-0027,seq-0031,seq-0039,seq-0043,seq-0044,seq-0046,seq-0049,seq-0051,seq-0053,seq-0055,seq-0056,seq-0057,seq-0061,seq-0062,seq-0063,seq-0067,seq-0072,seq-0077,seq-0080,seq-0081,seq-0082,seq-0090,seq-0091,seq-0093,seq-0095,seq-0101,seq-0103,seq-0104,seq-0115,seq-0116,seq-0120,seq-0121,seq-0122,seq-0125,seq-0126,seq-0130,seq-0131,seq-0136,seq-0141,seq-0144,seq-0147,seq-0155,seq-0160,seq-0162,seq-0164,seq-0166,seq-0169,seq-0172,seq-0173,seq-0175,seq-0179,seq-0182,seq-0190,seq-0192,seq-0193,seq-0194; 73 cells
  - diagnosis: region symbols changed use_parity->__unnamed_3, xor_k->__unnamed_1, xor_k_inv->__unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_2; region is not a definition (missing, declaration, or alias): __unnamed_3
  - reproduce: `python3 corpus/legality/harness/run.py replay b3a1e9600a70885a0ebc`; opt: `/usr/lib/llvm-18/bin/opt '-passes=canonicalize-aliases,function(tailcallelim),function(print<access-info>),function(print-cfg-sccs),always-inline,function(instsimplify),function(loop(loop-predication)),function(print<branch-prob>),function(assume-simplify),strip-nonlinetable-debuginfo,function(print<memoryssa-walker>),function(view-dom-only),function(verify<scalar-evolution>),function(assume-simplify),function(print<inliner-size-estimator>),strip-nondebug,function(loop-data-prefetch),wholeprogramdevirt,function(dce),function(lower-constant-intrinsics),function(dot-post-dom),hipstdpar-interpose-alloc' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/38b0a8eeb52061e13b350a34f6caf37de07d1efe74237d543bec2f03e3fcf70c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/b3a1e9600a70885a0ebc/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,8 +1,8 @@
   IN 0
   QALLOC H0 0 4
  -INPLACE F:xor_k F:xor_k_inv
  -END INPLACE
  -COMPUTE F:xor_k F:use_parity
  +INPLACE F:__unnamed_1 F:__unnamed_2
  +END INPLACE
  +COMPUTE F:__unnamed_1 F:__unnamed_3
   GATE2 3 H0 0 H0 3
   END COMPUTE
   MEASURE H0 3 0 1
  ...
  ```
  </details>
- **`region-inplace-selfinverse`** (probe) — P3 `23 random sequences, each containing a pass that FAILs alone on this case (mergefunc 23)` — **L4** — LLVM 18,20,23; modes seq-0006,seq-0014,seq-0020,seq-0029,seq-0033,seq-0057,seq-0062,seq-0069,seq-0076,seq-0087,seq-0089,seq-0107,seq-0129,seq-0131,seq-0134,seq-0138,seq-0152,seq-0154,seq-0156,seq-0159,seq-0174,seq-0185,seq-0186; 23 cells
  - diagnosis: region xor_k_inv became a forwarding thunk to xor_k
  - reproduce: `python3 corpus/legality/harness/run.py replay dee5c5f55e5a879921b9`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=dot-callgraph,function(lower-expect),function(annotation-remarks),function(loop(loop-reduce)),loop-extract,function(loop-versioning),function(simplifycfg),function(loop(print)),function(gc-lowering),function(extra-vector-passes),function(print<phi-values>),mergefunc,function(loop(loop-versioning-licm)),strip-nonlinetable-debuginfo,norecurse-lto-inference,function(break-crit-edges),invalidate<all>,function(loop(loop-instsimplify)),function(expand-memcmp)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/38b0a8eeb52061e13b350a34f6caf37de07d1efe74237d543bec2f03e3fcf70c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/dee5c5f55e5a879921b9/output.bc`
- **`region-inplace-selfinverse`** (probe) — P3 `seq-0082 (25 passes)` — **L4** — LLVM 23; modes seq-0082; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: region xor_k became a forwarding thunk to outlined_ir_func_0; region xor_k_inv became a forwarding thunk to outlined_ir_func_0
  - reproduce: `python3 corpus/legality/harness/run.py replay 60d4d7ec78c71ffbbcb6`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=function(float2int),function(replace-with-veclib),function(coro-elide),function(loop-load-elim),function(loop(loop-versioning-licm)),rewrite-symbols,function(early-cse),function(print<predicate-info>),function(dot-post-dom-only),function(func-properties-stats),iroutliner,attributor,function(print<scev-division>),cgscc(openmp-opt-cgscc),fatlto-cleanup,pgo-force-function-attrs,function(lower-constant-intrinsics),function(chr),partial-inliner,global-merge,function(consthoist),function(slsr),cgscc(openmp-opt-cgscc),memprof-remove-attributes,function(gvn)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/38b0a8eeb52061e13b350a34f6caf37de07d1efe74237d543bec2f03e3fcf70c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/60d4d7ec78c71ffbbcb6/output.bc`
- **`region-internal-strip`** (probe) — P1 `strip` — **L1,L4,L5** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region symbols changed rev_body->__unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): rev_body; first trace difference: -REVERSIBLE F:rev_body 4 / +REVERSIBLE F:__unnamed_1 4
  - reproduce: `python3 corpus/legality/harness/run.py replay d9fba76647582fa85cd8`; opt: `/usr/lib/llvm-18/bin/opt -passes=strip /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/4dfd56687fe8aba8a56fc6c4763ecac0496c2fbe6d3f320f6a3cfca1016adea9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/d9fba76647582fa85cd8/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,6 +1,6 @@
   IN 0
   QALLOC H0 0 2
  -REVERSIBLE F:rev_body 4
  +REVERSIBLE F:__unnamed_1 4
   GATE 2 H0 0
   GATE 2 H0 1
   END REVERSIBLE
  @@ -9,7 +9,7 @@
   RET 1
   IN 1
   QALLOC H0 0 2
  ...
  ```
  </details>
- **`region-internal-strip`** (probe) — P1 `strip-nondebug` — **L1,L4,L5** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region symbols changed rev_body->__unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): rev_body; first trace difference: -REVERSIBLE F:rev_body 4 / +REVERSIBLE F:__unnamed_1 4
  - reproduce: `python3 corpus/legality/harness/run.py replay 181758fe99e92f50bf1d`; opt: `/usr/lib/llvm-18/bin/opt -passes=strip-nondebug /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/4dfd56687fe8aba8a56fc6c4763ecac0496c2fbe6d3f320f6a3cfca1016adea9/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/181758fe99e92f50bf1d/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,6 +1,6 @@
   IN 0
   QALLOC H0 0 2
  -REVERSIBLE F:rev_body 4
  +REVERSIBLE F:__unnamed_1 4
   GATE 2 H0 0
   GATE 2 H0 1
   END REVERSIBLE
  @@ -9,7 +9,7 @@
   RET 1
   IN 1
   QALLOC H0 0 2
  ...
  ```
  </details>
- **`region-internal-strip`** (probe) — P3 `73 random sequences, each containing a pass that FAILs alone on this case (strip 44, strip-nondebug 35)` — **L1,L4,L5** — LLVM 18,20,23; modes seq-0002,seq-0005,seq-0006,seq-0007,seq-0009,seq-0012,seq-0018,seq-0019,seq-0025,seq-0027,seq-0031,seq-0039,seq-0043,seq-0044,seq-0046,seq-0049,seq-0051,seq-0053,seq-0055,seq-0056,seq-0057,seq-0061,seq-0062,seq-0063,seq-0067,seq-0072,seq-0077,seq-0080,seq-0081,seq-0082,seq-0090,seq-0091,seq-0093,seq-0095,seq-0101,seq-0103,seq-0104,seq-0115,seq-0116,seq-0120,seq-0121,seq-0122,seq-0125,seq-0126,seq-0130,seq-0131,seq-0136,seq-0141,seq-0144,seq-0147,seq-0155,seq-0160,seq-0162,seq-0164,seq-0166,seq-0169,seq-0172,seq-0173,seq-0175,seq-0179,seq-0182,seq-0190,seq-0192,seq-0193,seq-0194; 73 cells
  - diagnosis: region symbols changed rev_body->__unnamed_1; region is not a definition (missing, declaration, or alias): __unnamed_1; region is not a definition (missing, declaration, or alias): rev_body; first trace difference: -REVERSIBLE F:rev_body 4 / +REVERSIBLE F:__unnamed_1 4
  - reproduce: `python3 corpus/legality/harness/run.py replay 94d0a6f7e641ad201586`; opt: `/usr/lib/llvm-18/bin/opt '-passes=canonicalize-aliases,function(tailcallelim),function(print<access-info>),function(print-cfg-sccs),always-inline,function(instsimplify),function(loop(loop-predication)),function(print<branch-prob>),function(assume-simplify),strip-nonlinetable-debuginfo,function(print<memoryssa-walker>),function(view-dom-only),function(verify<scalar-evolution>),function(assume-simplify),function(print<inliner-size-estimator>),strip-nondebug,function(loop-data-prefetch),wholeprogramdevirt,function(dce),function(lower-constant-intrinsics),function(dot-post-dom),hipstdpar-interpose-alloc' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/c425032125c9f2c23a6e9a432ec29f81c54c8590e15a77e17f1d507942ff782c/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/94d0a6f7e641ad201586/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,6 +1,6 @@
   IN 0
   QALLOC H0 0 2
  -REVERSIBLE F:rev_body 4
  +REVERSIBLE F:__unnamed_1 4
   GATE 2 H0 0
   GATE 2 H0 1
   END REVERSIBLE
  @@ -9,7 +9,7 @@
   RET 1
   IN 1
   QALLOC H0 0 2
  ...
  ```
  </details>
- **`region-iroutliner`** (probe) — P3 `seq-0151 (33 passes)` — **L4** — LLVM 20; modes seq-0151; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: region qft_step_a became a forwarding thunk to outlined_ir_func_0; region qft_step_b became a forwarding thunk to outlined_ir_func_0
  - reproduce: `python3 corpus/legality/harness/run.py replay b815d6bb0f84ac8f6851`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(print-mustexecute),openmp-opt,globalopt,annotation2metadata,shadow-stack-gc-lowering,function(verify<safepoint-ir>),function(instcount),function(loop-mssa(licm)),function(newgvn),function(ee-instrument),function(normalize),function(guard-widening),cgscc(inline),hipstdpar-interpose-alloc,function(strip-gc-relocates),function(view-dom),rewrite-statepoints-for-gc,function(print<inliner-size-estimator>),iroutliner,function(print-predicateinfo),function(loop(loop-reduce)),function(print<inline-cost>),function(loop(print<loopnest>)),function(infer-address-spaces),function(objc-arc),function(print-mustexecute),function(lower-allow-check),function(pgo-memop-opt),function(lint),function(loop(loop-instsimplify)),function(loop-simplify),function(inject-tli-mappings),function(loop(canon-freeze))' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/95eeba59f0077807e0c169f7c7f2f47fbe05f12cf40af3258924787837a05da4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/b815d6bb0f84ac8f6851/output.bc`
- **`region-iroutliner`** (probe) — P3 `seq-0019 (37 passes)` — **L4** — LLVM 20; modes seq-0019; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: region qft_step_a became a forwarding thunk to outlined_ir_func_0; region qft_step_b became a forwarding thunk to outlined_ir_func_0
  - reproduce: `python3 corpus/legality/harness/run.py replay ab8af50c2dba81a606e1`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(print<domtree>),function(print<domfrontier>),function(transform-warning),function(tailcallelim),print-lcg-dot,function(loop(canon-freeze)),function(dse),function(print<phi-values>),annotation2metadata,strip-nonlinetable-debuginfo,cgscc(coro-annotation-elide),function(loop-versioning),canonicalize-aliases,function(loop-versioning),function(load-store-vectorizer),function(float2int),function(print<lazy-value-info>),function(kcfi),inferattrs,function(print<access-info>),function(verify<scalar-evolution>),function(constraint-elimination),annotation2metadata,function(lcssa),function(simplifycfg),rpo-function-attrs,function(loop-versioning),module-inline,function(loop(loop-versioning-licm)),function(dot-post-dom),print<ctx-prof-analysis>,function(sandbox-vectorizer),rewrite-statepoints-for-gc,iroutliner,function(lower-invoke),function(print<domfrontier>),wholeprogramdevirt' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/95eeba59f0077807e0c169f7c7f2f47fbe05f12cf40af3258924787837a05da4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/ab8af50c2dba81a606e1/output.bc`
- **`region-iroutliner`** (probe) — P3 `seq-0097 (14 passes)` — **L4** — LLVM 23; modes seq-0097; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: region qft_step_a became a forwarding thunk to outlined_ir_func_0; region qft_step_b became a forwarding thunk to outlined_ir_func_0
  - reproduce: `python3 corpus/legality/harness/run.py replay eb1936c76df3fa88dc3c`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=function(wasm-eh-prepare),function(strip-convergence-intrinsics),function(assume-simplify),function(aggressive-instcombine),rpo-function-attrs,function(tailcallelim),function(loop(loop-reduce)),function(loop(print<loopnest>)),print-callgraph-sccs,iroutliner,function(instnamer),function(assume-builder),function(print<da>),function(view-dom)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/95eeba59f0077807e0c169f7c7f2f47fbe05f12cf40af3258924787837a05da4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/eb1936c76df3fa88dc3c/output.bc`
- **`region-mergefunc-twins`** (probe) — P1 `iroutliner` — **L4** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region oracle_key1 became a forwarding thunk to outlined_ir_func_0; region oracle_key2 became a forwarding thunk to outlined_ir_func_0
  - reproduce: `python3 corpus/legality/harness/run.py replay 3c6bf261e64a30d51d42`; opt: `/usr/lib/llvm-18/bin/opt -passes=iroutliner /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/cc75a39ca184d88b16f338e5874884aefc09b779648e32c64905029c6f581066/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/3c6bf261e64a30d51d42/output.bc`
- **`region-mergefunc-twins`** (probe) — P1 `mergefunc` — **L4** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region oracle_key2 became a forwarding thunk to oracle_key1
  - reproduce: `python3 corpus/legality/harness/run.py replay 97d2392a48ae05df2a2b`; opt: `/usr/lib/llvm-18/bin/opt -passes=mergefunc /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/cc75a39ca184d88b16f338e5874884aefc09b779648e32c64905029c6f581066/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/97d2392a48ae05df2a2b/output.bc`
- **`region-mergefunc-twins`** (probe) — P3 `57 random sequences, each containing a pass that FAILs alone on this case (iroutliner 30, mergefunc 28)` — **L4** — LLVM 18,20,23; modes seq-0004,seq-0006,seq-0007,seq-0012,seq-0013,seq-0014,seq-0019,seq-0020,seq-0024,seq-0029,seq-0033,seq-0038,seq-0040,seq-0046,seq-0048,seq-0049,seq-0054,seq-0057,seq-0062,seq-0066,seq-0069,seq-0073,seq-0076,seq-0081,seq-0082,seq-0083,seq-0087,seq-0089,seq-0091,seq-0097,seq-0105,seq-0107,seq-0110,seq-0111,seq-0116,seq-0117,seq-0129,seq-0130,seq-0131,seq-0133,seq-0134,seq-0137,seq-0138,seq-0151,seq-0152,seq-0154,seq-0156,seq-0159,seq-0174,seq-0175,seq-0182,seq-0185,seq-0186,seq-0197,seq-0198,seq-0199; 57 cells
  - diagnosis: region oracle_key1 became a forwarding thunk to outlined_ir_func_0; region oracle_key2 became a forwarding thunk to outlined_ir_func_0
  - reproduce: `python3 corpus/legality/harness/run.py replay 98bcea2cd4d2ea8ce685`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=attributor,function(print<scalar-evolution>),function(consthoist),function(view-dom),inliner-wrapper-no-mandatory-first,invalidate<all>,function(correlated-propagation),print-callgraph-sccs,function(mergereturn),function(flatten-cfg),function(loop-versioning),hipstdpar-interpose-alloc,function(instsimplify),function(print<stack-lifetime>),function(lower-switch),cgscc(attributor-light-cgscc),function(print<func-properties>),function(load-store-vectorizer),function(lower-switch),function(objc-arc),function(print<stack-lifetime>),embed-bitcode,function(loop(simple-loop-unswitch)),function(ee-instrument),function(instcombine<no-verify-fixpoint>),print-ir-similarity,extract-blocks,cgscc(no-op-cgscc),function(guard-widening),function(objc-arc),function(print<demanded-bits>),print<dxil-metadata>,function(lower-switch),function(dot-cfg),function(hardware-loops),iroutliner,deadargelim,always-inline,function(print<loops>),function(lower-invoke)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/807e87709ca6fad201eee631ac2598421cdd86ff5a30f8dd3ddc78633f604075/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/98bcea2cd4d2ea8ce685/output.bc`
- **`region-mergefunc-unnamed-addr`** (probe) — P1 `iroutliner` — **L4** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region oracle_key1 became a forwarding thunk to outlined_ir_func_0; region oracle_key2 became a forwarding thunk to outlined_ir_func_0
  - reproduce: `python3 corpus/legality/harness/run.py replay 28b2812f6efc7cb4e9d6`; opt: `/usr/lib/llvm-18/bin/opt -passes=iroutliner /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/9852c12f7e23301ba7988cc25cb6fee61d165fb7229451ff61652e7e41323545/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/28b2812f6efc7cb4e9d6/output.bc`
- **`region-mergefunc-unnamed-addr`** (probe) — P1 `mergefunc` — **L1,L4,L5** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region symbols changed oracle_key2->oracle_key1; region oracle_key2 became a forwarding thunk to oracle_key1; first trace difference: -CTRL H0 0 F:oracle_key2 32 / +CTRL H0 0 F:oracle_key1 32
  - reproduce: `python3 corpus/legality/harness/run.py replay 3dff302424074b80cbb8`; opt: `/usr/lib/llvm-18/bin/opt -passes=mergefunc /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/9852c12f7e23301ba7988cc25cb6fee61d165fb7229451ff61652e7e41323545/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/3dff302424074b80cbb8/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -15,7 +15,7 @@
   IN 1
   QALLOC H0 0 1
   QALLOC H1 0 2
  -CTRL H0 0 F:oracle_key2 32
  +CTRL H0 0 F:oracle_key1 32
   GATE 1 H1 0
   GATE2 3 H1 0 H1 1
   GATE 7 H1 1
  @@ -48,7 +48,7 @@
   IN 3
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`region-mergefunc-unnamed-addr`** (probe) — P3 `29 random sequences, each containing a pass that FAILs alone on this case (iroutliner 29)` — **L4** — LLVM 18,20,23; modes seq-0004,seq-0007,seq-0013,seq-0019,seq-0024,seq-0038,seq-0040,seq-0046,seq-0048,seq-0054,seq-0066,seq-0073,seq-0081,seq-0082,seq-0083,seq-0091,seq-0097,seq-0105,seq-0110,seq-0111,seq-0117,seq-0133,seq-0137,seq-0151,seq-0175,seq-0182,seq-0197,seq-0198,seq-0199; 29 cells
  - diagnosis: region oracle_key1 became a forwarding thunk to outlined_ir_func_0; region oracle_key2 became a forwarding thunk to outlined_ir_func_0
  - reproduce: `python3 corpus/legality/harness/run.py replay d09ff1c89a8061e491fd`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=attributor,function(print<scalar-evolution>),function(consthoist),function(view-dom),inliner-wrapper-no-mandatory-first,invalidate<all>,function(correlated-propagation),print-callgraph-sccs,function(mergereturn),function(flatten-cfg),function(loop-versioning),hipstdpar-interpose-alloc,function(instsimplify),function(print<stack-lifetime>),function(lower-switch),cgscc(attributor-light-cgscc),function(print<func-properties>),function(load-store-vectorizer),function(lower-switch),function(objc-arc),function(print<stack-lifetime>),embed-bitcode,function(loop(simple-loop-unswitch)),function(ee-instrument),function(instcombine<no-verify-fixpoint>),print-ir-similarity,extract-blocks,cgscc(no-op-cgscc),function(guard-widening),function(objc-arc),function(print<demanded-bits>),print<dxil-metadata>,function(lower-switch),function(dot-cfg),function(hardware-loops),iroutliner,deadargelim,always-inline,function(print<loops>),function(lower-invoke)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/855d6b92513c2ddd5f2e0dc52782f6f978058058ce500e8ef7549fdff1c4a78b/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/d09ff1c89a8061e491fd/output.bc`
- **`region-mergefunc-unnamed-addr`** (probe) — P3 `33 random sequences, each containing a pass that FAILs alone on this case (mergefunc 33, iroutliner 1)` — **L1,L4,L5** — LLVM 18,20,23; modes seq-0006,seq-0009,seq-0012,seq-0014,seq-0020,seq-0029,seq-0033,seq-0049,seq-0055,seq-0057,seq-0062,seq-0069,seq-0076,seq-0082,seq-0087,seq-0089,seq-0107,seq-0115,seq-0116,seq-0129,seq-0130,seq-0131,seq-0134,seq-0138,seq-0146,seq-0152,seq-0154,seq-0156,seq-0159,seq-0174,seq-0185,seq-0186,seq-0195; 33 cells
  - diagnosis: region symbols changed oracle_key2->oracle_key1; first trace difference: -CTRL H0 0 F:oracle_key2 32 / +CTRL H0 0 F:oracle_key1 32
  - reproduce: `python3 corpus/legality/harness/run.py replay f2804ac5059e80c3b633`; opt: `/usr/lib/llvm-18/bin/opt '-passes=called-value-propagation,function(print<loops>),function(mergeicmps),mergefunc,function(float2int),hipstdpar-interpose-alloc,cgscc(invalidate<all>),function(tlshoist),function(lower-matrix-intrinsics),function(win-eh-prepare),function(view-post-dom-only),function(memcpyopt),debugify,function(loop-sink),function(print<func-properties>),function(print<assumptions>),function(dot-cfg-only),check-debugify,function(alignment-from-assumptions),inliner-wrapper-no-mandatory-first,function(declare-to-assign),function(print<da>),function(print<demanded-bits>),function(lower-matrix-intrinsics),function(objc-arc-contract),function(alignment-from-assumptions),function(alignment-from-assumptions),function(infer-address-spaces),lower-emutls,rel-lookup-table-converter,print<inline-advisor>,attributor,function(loop-vectorize),function(print<da>),function(verify),function(mergereturn),function(dse)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/855d6b92513c2ddd5f2e0dc52782f6f978058058ce500e8ef7549fdff1c4a78b/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/f2804ac5059e80c3b633/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -15,7 +15,7 @@
   IN 1
   QALLOC H0 0 1
   QALLOC H1 0 2
  -CTRL H0 0 F:oracle_key2 32
  +CTRL H0 0 F:oracle_key1 32
   GATE 1 H1 0
   GATE2 3 H1 0 H1 1
   GATE 7 H1 1
  @@ -48,7 +48,7 @@
   IN 3
   QALLOC H0 0 1
  ...
  ```
  </details>
### control

- **`control-handle-deref`** (probe) — inherited `(any pass; behaviour identical to its input = default<O3> output; 346 pass/mode cells)` — **L1,L3,L5** — LLVM 18,20,23; modes post-O3; 909 cells
  - diagnosis: dynamic L3 ['FAULT handle-deref'] at O0; dynamic L3 ['FAULT handle-deref'] at O3; O0: trace/result differs or execution failed (exit=86, timeout=False)
  - reproduce: `python3 corpus/legality/harness/run.py replay e7bb97ffbe97e7e15c83`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt -passes=alloc-token /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/847f20e364d2b0cd305356e03d0fd0ea4428deb2a26b69eaa5063ac7a84f8b88/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/e7bb97ffbe97e7e15c83/output.bc`
- **`control-handle-deref`** (probe) — inherited `(any pass; behaviour identical to its input = untransformed input; 956 pass/mode cells)` — **L1,L3,L5** — LLVM 18,20,23; modes raw,seq-0000,seq-0001,seq-0002,seq-0003,seq-0004,seq-0005,seq-0006,seq-0007,seq-0008,seq-0009,seq-0010,seq-0011,seq-0012,seq-0013,seq-0014,seq-0015,seq-0016,seq-0017,seq-0018,seq-0019,seq-0020,seq-0021,seq-0022,seq-0023,seq-0024,seq-0025,seq-0026,seq-0027,seq-0028,seq-0029,seq-0030,seq-0031,seq-0032,seq-0033,seq-0034,seq-0035,seq-0036,seq-0037,seq-0038,seq-0039,seq-0040,seq-0041,seq-0042,seq-0043,seq-0044,seq-0045,seq-0046,seq-0047,seq-0048,seq-0049,seq-0050,seq-0051,seq-0052,seq-0053,seq-0054,seq-0055,seq-0056,seq-0057,seq-0058,seq-0059,seq-0060,seq-0061,seq-0062,seq-0063,seq-0064,seq-0065,seq-0066,seq-0067,seq-0068,seq-0069,seq-0070,seq-0071,seq-0072,seq-0073,seq-0074,seq-0075,seq-0076,seq-0077,seq-0078,seq-0079,seq-0080,seq-0081,seq-0082,seq-0083,seq-0084,seq-0085,seq-0086,seq-0087,seq-0088,seq-0089,seq-0090,seq-0091,seq-0092,seq-0093,seq-0094,seq-0095,seq-0096,seq-0097,seq-0098,seq-0099,seq-0100,seq-0101,seq-0102,seq-0103,seq-0104,seq-0105,seq-0106,seq-0107,seq-0108,seq-0109,seq-0110,seq-0111,seq-0112,seq-0113,seq-0114,seq-0115,seq-0116,seq-0117,seq-0118,seq-0119,seq-0120,seq-0121,seq-0122,seq-0123,seq-0124,seq-0125,seq-0126,seq-0127,seq-0128,seq-0129,seq-0130,seq-0131,seq-0132,seq-0133,seq-0134,seq-0135,seq-0136,seq-0137,seq-0138,seq-0139,seq-0140,seq-0141,seq-0142,seq-0143,seq-0144,seq-0145,seq-0146,seq-0147,seq-0148,seq-0149,seq-0150,seq-0151,seq-0152,seq-0153,seq-0154,seq-0155,seq-0156,seq-0157,seq-0158,seq-0159,seq-0160,seq-0161,seq-0162,seq-0163,seq-0164,seq-0165,seq-0166,seq-0167,seq-0168,seq-0169,seq-0170,seq-0171,seq-0172,seq-0173,seq-0174,seq-0175,seq-0176,seq-0177,seq-0178,seq-0179,seq-0180,seq-0181,seq-0182,seq-0183,seq-0184,seq-0185,seq-0186,seq-0187,seq-0188,seq-0189,seq-0190,seq-0191,seq-0192,seq-0193,seq-0194,seq-0195,seq-0196,seq-0197,seq-0198,seq-0199; 1539 cells
  - diagnosis: dynamic L3 ['FAULT handle-deref'] at O0; dynamic L3 ['FAULT handle-deref'] at O3; O0: trace/result differs or execution failed (exit=86, timeout=False)
  - reproduce: `python3 corpus/legality/harness/run.py replay d81adeb65961fd23e4e2`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt -passes=alloc-token /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/61d0b1631edaec75754625e1c59b9e53f5287682c2543a13d07d076745aec693/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/d81adeb65961fd23e4e2/output.bc`
- **`control-memory-none`** (probe) — inherited `(any pass; behaviour identical to its input = default<O3> output; 346 pass/mode cells)` — **L1,L5** — LLVM 18,20,23; modes post-O3; 910 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay de790480720c69551ea1`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt -passes=alloc-token /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/bc5667a9bf9c276e15ac5341673cca7b121c1fd52951bf2422249030658d45b4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/de790480720c69551ea1/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P1 `function(loop-mssa(licm))` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 2b51f5bde110104f9543`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(loop-mssa(licm))' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/2b51f5bde110104f9543/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P1 `function(loop-mssa(lnicm))` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay d2feead5d9160f24a5d2`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(loop-mssa(lnicm))' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/d2feead5d9160f24a5d2/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P1 `function(normalize)` — **L1,L3,L5** — LLVM 20,23; modes post-O3; 2 cells
  - diagnosis: dynamic L3 ['BADHANDLE'] at O0; dynamic L3 ['BADHANDLE'] at O3; first trace difference: -MEASURE H0 0 0 1 / -MEASURE H0 0 1 0
  - reproduce: `python3 corpus/legality/harness/run.py replay f51b64369414d103f47c`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(normalize)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/bc5667a9bf9c276e15ac5341673cca7b121c1fd52951bf2422249030658d45b4/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/f51b64369414d103f47c/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
  -MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +MEASURE BADHANDLE 0 0 1
  +RET 4
   IN 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P1 `scc-oz-module-inliner` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay de7fbc9b3a6a67d634c2`; opt: `/usr/lib/llvm-18/bin/opt -passes=scc-oz-module-inliner /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/de7fbc9b3a6a67d634c2/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P2 `default<O1>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 8d683e8754ecda50b9e0`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O1>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/8d683e8754ecda50b9e0/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P2 `default<O2>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay fc6370fde08749b8fcb0`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O2>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/fc6370fde08749b8fcb0/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P2 `default<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 8972715108acf2eb47bb`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/8972715108acf2eb47bb/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P2 `default<O3>,default<O3>,default<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay a7bf7d1961bb4c097f4c`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O3>,default<O3>,default<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/a7bf7d1961bb4c097f4c/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P2 `default<Os>` — **L1,L5** — LLVM 18,20; modes raw; 2 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay d6ec2de7bbf4534560d7`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<Os>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/d6ec2de7bbf4534560d7/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P2 `default<Oz>` — **L1,L5** — LLVM 18,20; modes raw; 2 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 63f3b2104ca68ea7e7a9`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<Oz>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/63f3b2104ca68ea7e7a9/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P2 `lto-pre-link<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 530890d1c12df3b69cd4`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lto-pre-link<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/530890d1c12df3b69cd4/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P2 `lto<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay aed74674b21c44f75f7a`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lto<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/aed74674b21c44f75f7a/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P2 `thinlto-pre-link<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 3565c7777a4ab942273e`; opt: `/usr/lib/llvm-18/bin/opt '-passes=thinlto-pre-link<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/3565c7777a4ab942273e/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P2 `thinlto<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 7536dfdb751b8452fd84`; opt: `/usr/lib/llvm-18/bin/opt '-passes=thinlto<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/7536dfdb751b8452fd84/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P3 `109 random sequences, each containing a pass that FAILs alone on this case (function(loop-mssa(licm)) 45, function(loop-mssa(lnicm)) 43, scc-oz-module-inliner 31, function(normalize) 6)` — **L1,L5** — LLVM 18,20,23; modes seq-0000,seq-0002,seq-0003,seq-0006,seq-0010,seq-0011,seq-0012,seq-0015,seq-0017,seq-0018,seq-0022,seq-0028,seq-0029,seq-0031,seq-0034,seq-0035,seq-0037,seq-0038,seq-0041,seq-0046,seq-0047,seq-0048,seq-0049,seq-0051,seq-0052,seq-0056,seq-0058,seq-0061,seq-0062,seq-0064,seq-0065,seq-0066,seq-0067,seq-0070,seq-0071,seq-0073,seq-0075,seq-0076,seq-0077,seq-0080,seq-0081,seq-0082,seq-0086,seq-0092,seq-0094,seq-0096,seq-0098,seq-0100,seq-0103,seq-0108,seq-0109,seq-0110,seq-0115,seq-0119,seq-0122,seq-0123,seq-0124,seq-0126,seq-0129,seq-0130,seq-0131,seq-0132,seq-0133,seq-0134,seq-0136,seq-0137,seq-0138,seq-0142,seq-0143,seq-0144,seq-0145,seq-0148,seq-0151,seq-0153,seq-0162,seq-0163,seq-0165,seq-0167,seq-0170,seq-0171,seq-0173,seq-0175,seq-0179,seq-0182,seq-0183,seq-0187,seq-0188,seq-0189,seq-0192,seq-0196,seq-0198,seq-0199; 109 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay ae82fb1b00a64140d42c`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=annotation2metadata,function(loop(print)),function(print<cfg-sccs>),function(view-dom),cgscc(coro-annotation-elide),strip-dead-prototypes,function(print<phi-values>),function(callsite-splitting),function(ee-instrument),function(print<scev-division>),function(bounds-checking),deadargelim,function(verify<regions>),ipsccp,print<inline-advisor>,dxil-upgrade,function(loop-mssa(lnicm)),function(declare-to-assign),print<module-debuginfo>,function(print<domfrontier>),globalopt,function(lower-invoke),cgscc(function-attrs),ipsccp,function(memcpyopt),print<module-debuginfo>,function(lower-guard-intrinsic),function(loop(loop-unroll-full)),function(print<regions>),function(lower-widenable-condition),strip-dead-prototypes,print,openmp-opt,wholeprogramdevirt,function(loop-unroll),function(print<delinearization>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/ae82fb1b00a64140d42c/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P3 `seq-0045 (33 passes)` — **L1,L5** — LLVM 18; modes seq-0045; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay c1d739219cba5b53cf7b`; opt: `/usr/lib/llvm-18/bin/opt '-passes=coro-early,function(loop(print<loop-cache-cost>)),deadargelim,function(callbrprepare),function(loop(dot-ddg)),function(loop-unroll),openmp-opt-postlink,function(guard-widening),function(loop(loop-rotate)),function(safe-stack),function(print<scalar-evolution>),invalidate<all>,strip-debug-declare,function(print<cycles>),function(print<demanded-bits>),function(loop-versioning),function(loop(loop-unroll-full)),function(infer-alignment),function(print<uniformity>),hipstdpar-interpose-alloc,rewrite-symbols,function(declare-to-assign),function(loop-fusion),function(print<stack-safety-local>),function(early-cse),inferattrs,function(loop(loop-flatten)),function(print<domfrontier>),function(print),view-callgraph,function(print<stack-safety-local>),function(separate-const-offset-from-gep),strip-dead-prototypes' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/c1d739219cba5b53cf7b/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P3 `seq-0083 (36 passes)` — **L1,L5** — LLVM 18; modes seq-0083; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 3f1f1989d11157232efd`; opt: `/usr/lib/llvm-18/bin/opt '-passes=dxil-upgrade,function(fix-irreducible),function(loop-fusion),function(instnamer),function(pgo-memop-opt),function(verify<safepoint-ir>),function(helloworld),function(constraint-elimination),function(slp-vectorizer),print-lcg,function(irce),function(sccp),function(print<memoryssa>),loop-extract,sanmd-module,function(loop-unroll),cgscc(attributor-cgscc),partial-inliner,function(loop-distribute),check-debugify,function(loop(loop-interchange)),rel-lookup-table-converter,function(sccp),function(print<debug-ata>),print-lcg,function(print<uniformity>),function(tailcallelim),print-profile-summary,memprof-context-disambiguation,function(simplifycfg),function(loop(loop-unroll-full)),function(objc-arc-expand),strip-nonlinetable-debuginfo,function(newgvn),function(loop(loop-unroll-full)),cgscc(argpromotion)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/3f1f1989d11157232efd/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P3 `seq-0030 (23 passes)` — **L1,L5** — LLVM 23; modes seq-0030; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay ff58e5d08143fc9cd957`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=function(break-crit-edges),mir-strip-debug,function(print<demanded-bits>),deadargelim,function(loop(loop-unroll-full)),function(instcount),lower-emutls,function(print<uniformity>),function(assume-builder),function(reassociate),function(verify),cg-profile,lower-comment-string,cross-dso-cfi,function(mergeicmps),jmc-instrumenter,function(infer-alignment),inliner-wrapper,function(early-cse),function(tailcallelim),function(aggressive-instcombine),function(print<da>),function(verify<loops>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/ff58e5d08143fc9cd957/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P3 `seq-0190 (29 passes)` — **L1,L5** — LLVM 20; modes seq-0190; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 9325d9eb7de61f8ae290`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(lcssa),function(loop-unroll),function(sink),lower-ifunc,function(print<stack-lifetime>),function(dot-dom-only),no-op-module,function(wasm-eh-prepare),jmc-instrumenter,debugify,print-ir-similarity,function(consthoist),function(dot-post-dom),function(verify<memoryssa>),print<dxil-metadata>,strip-nondebug,function(loop(loop-reduce)),sancov-module,function(bdce),function(load-store-vectorizer),function(early-cse),function(pa-eval),function(loop(indvars)),function(infer-alignment),function(print<func-properties>),no-op-module,print<module-debuginfo>,function(dot-cfg-only),function(loop(loop-rotate))' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/9325d9eb7de61f8ae290/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P3 `seq-0156 (29 passes)` — **L1,L5** — LLVM 20; modes seq-0156; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay db15b54dd32f58fd3463`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(loop-unroll),function(loop(loop-deletion)),function(adce),function(alignment-from-assumptions),function(lower-expect),lower-global-dtors,function(cfguard),function(loop(print<iv-users>)),function(loop-versioning),function(load-store-vectorizer),rewrite-symbols,function(newgvn),function(verify<loops>),function(guard-widening),function(instcombine<no-verify-fixpoint>),dxil-upgrade,function(break-crit-edges),function(annotation-remarks),function(print<da>),function(print<inliner-size-estimator>),inliner-wrapper-no-mandatory-first,function(aa-eval),debugify,function(loop-fusion),function(print<func-properties>),print<dxil-metadata>,function(loop(loop-idiom)),function(callbr-prepare),print<inline-advisor>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/db15b54dd32f58fd3463/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P3 `seq-0091 (32 passes)` — **L1,L5** — LLVM 18; modes seq-0091; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay a6c7d96146ba7934d64d`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(slsr),function(break-crit-edges),objc-arc-apelim,function(aggressive-instcombine),recompute-globalsaa,function(view-dom-only),function(annotation-remarks),function(dot-post-dom),function(callbrprepare),function(print<domtree>),function(objc-arc),function(verify<scalar-evolution>),function(gvn-sink),function(mem2reg),inliner-wrapper,function(view-cfg),function(verify),print,function(gvn),function(sroa),inferattrs,function(print<stack-safety-local>),print<structural-hash>,function(loop-unroll),print<module-debuginfo>,function(newgvn),annotation2metadata,instrorderfile,function(objc-arc),function(jump-threading),function(print-predicateinfo),function(bdce)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/a6c7d96146ba7934d64d/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P3 `seq-0075 (35 passes)` — **L1,L5** — LLVM 18; modes seq-0075; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 6624bba880a6c620f623`; opt: `/usr/lib/llvm-18/bin/opt '-passes=hipstdpar-interpose-alloc,function(infer-address-spaces),wholeprogramdevirt,print-profile-summary,function(loop-versioning),function(tailcallelim),function(loweratomic),pseudo-probe,inliner-wrapper-no-mandatory-first,function(infer-address-spaces),function(count-visits),function(loop(loop-unroll-full)),openmp-opt-postlink,function(adce),function(loop(print<loopnest>)),function(view-cfg),constmerge,function(view-cfg),function(print<loops>),function(verify<regions>),cross-dso-cfi,instrorderfile,function(loop(loop-unroll-full)),function(sroa),function(transform-warning),function(print),function(print<inline-cost>),function(print<scalar-evolution>),lowertypetests,function(newgvn),strip-dead-prototypes,function(lower-expect),no-op-module,recompute-globalsaa,function(load-store-vectorizer)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/6624bba880a6c620f623/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P3 `seq-0108 (19 passes)` — **L1,L5** — LLVM 18; modes seq-0108; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay ae309542487c1db7b8e9`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lower-emutls,function(correlated-propagation),function(print<domfrontier>),function(lcssa),no-op-module,function(sroa),function(flattencfg),module-inline,function(print<postdomtree>),function(loop(print<loopnest>)),function(dot-cfg-only),cgscc(coro-split),function(print-cfg-sccs),function(count-visits),function(partially-inline-libcalls),function(loop(loop-unroll-full)),function(gvn),function(loop(loop-versioning-licm)),function(print<regions>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/ae309542487c1db7b8e9/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P3 `seq-0101 (38 passes)` — **L1,L5** — LLVM 18; modes seq-0101; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 61356285cbe43968b91c`; opt: `/usr/lib/llvm-18/bin/opt '-passes=memprof-context-disambiguation,function(unify-loop-exits),cgscc(argpromotion),function(lower-expect),function(add-discriminators),memprof-context-disambiguation,strip-nondebug,function(guard-widening),shadow-stack-gc-lowering,function(count-visits),function(lower-guard-intrinsic),function(reg2mem),function(dot-post-dom-only),attributor,pseudo-probe,objc-arc-apelim,debugify,function(correlated-propagation),function(jump-threading),strip-nonlinetable-debuginfo,function(print<stack-lifetime>),function(ee-instrument),function(verify<domtree>),attributor,function(load-store-vectorizer),print-lcg-dot,canonicalize-aliases,function(gvn-hoist),function(loop-load-elim),function(fix-irreducible),function(lint),pseudo-probe-update,elim-avail-extern,verify,print-callgraph-sccs,function(partially-inline-libcalls),function(loop(loop-rotate)),function(bounds-checking)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/61356285cbe43968b91c/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P3 `seq-0166 (33 passes)` — **L1,L5** — LLVM 18; modes seq-0166; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay a0fa876f78eb11bbaa93`; opt: `/usr/lib/llvm-18/bin/opt '-passes=openmp-opt-postlink,function(lowerinvoke),strip-debug-declare,function(pgo-memop-opt),rel-lookup-table-converter,function(bounds-checking),function(stack-protector),function(loop(invalidate<all>)),function(verify),print-lcg,cgscc(attributor-light-cgscc),cgscc(function-attrs),strip-dead-prototypes,function(loop-unroll),print-stack-safety,coro-cleanup,function(bdce),function(print<domtree>),function(dot-post-dom-only),function(reassociate),print,function(newgvn),print-callgraph,function(kcfi),function(print<block-freq>),openmp-opt,function(loop-unroll),coro-cleanup,function(objc-arc-expand),function(add-discriminators),strip-nondebug,function(loop(loop-reroll)),function(loop(loop-predication))' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/a0fa876f78eb11bbaa93/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-memory-none`** (probe) — P3 `seq-0125 (33 passes)` — **L1,L5** — LLVM 23; modes seq-0125; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 9033619b7685996a23fd`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=pseudo-probe,coro-early,function(lower-guard-intrinsic),function(place-safepoints),attributor-light,function(loop(loop-rotate)),function(print<scev-division>),function(func-properties-stats),cross-dso-cfi,function(loop(invalidate<all>)),hipstdpar-math-fixup,cgscc(coro-annotation-elide),cgscc(function-attrs),coro-cleanup,print-must-be-executed-contexts,function(loop-unroll),function(hardware-loops),function(mergeicmps),fatlto-cleanup,function(ee-instrument),function(dfa-jump-threading),function(newgvn),function(print<scalar-evolution>),function(loop(print<ddg>)),print<ctx-prof-analysis>,extract-blocks,function(print<delinearization>),function(simplifycfg),function(print<block-freq>),function(loop(loop-deletion)),function(print<block-freq>),expand-variadics,rewrite-symbols' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/fd9232c9e3f815b299bb0e729cf6b0f6fbc4fa932ec0c86a75ff16a3286ee948/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/9033619b7685996a23fd/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — inherited `(any pass; behaviour identical to its input = default<O3> output; 346 pass/mode cells)` — **L1,L5** — LLVM 18,20,23; modes post-O3; 910 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay adaba539f4b16895ecde`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt -passes=alloc-token /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/1d0a1b5dc910530ae6967d6118c46c3906df60e31fa1daa1924fb7a400378325/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/adaba539f4b16895ecde/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P1 `asan` — **L2,L5** — LLVM 23; modes post-O3,raw; 2 cells
  - diagnosis: added forbidden memory(readwrite, argmem: read, inaccessiblemem: read, errnomem: read, target_mem: read) on __bennett_measure declaration; O0: native build failed at link; O3: native build failed at link
  - reproduce: `python3 corpus/legality/harness/run.py replay 483f59176b6bdcbabbcd`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt -passes=asan /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/1d0a1b5dc910530ae6967d6118c46c3906df60e31fa1daa1924fb7a400378325/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/483f59176b6bdcbabbcd/output.bc`
- **`control-readonly`** (probe) — P1 `function(loop-mssa(licm))` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 1ae7ac84b64f99486067`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(loop-mssa(licm))' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/1ae7ac84b64f99486067/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P1 `function(loop-mssa(lnicm))` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay b324911fd4bc8eecbdee`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(loop-mssa(lnicm))' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/b324911fd4bc8eecbdee/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P1 `function(normalize)` — **L1,L3,L5** — LLVM 20,23; modes post-O3; 2 cells
  - diagnosis: dynamic L3 ['BADHANDLE'] at O0; dynamic L3 ['BADHANDLE'] at O3; first trace difference: -MEASURE H0 0 0 1 / -MEASURE H0 0 1 0
  - reproduce: `python3 corpus/legality/harness/run.py replay b328393803b7816e4bf4`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(normalize)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/1d0a1b5dc910530ae6967d6118c46c3906df60e31fa1daa1924fb7a400378325/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/b328393803b7816e4bf4/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
  -MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +MEASURE BADHANDLE 0 0 1
  +RET 4
   IN 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P1 `hwasan` — **L2,L5** — LLVM 23; modes post-O3,raw; 2 cells
  - diagnosis: added forbidden memory(readwrite, argmem: read, inaccessiblemem: read, errnomem: read, target_mem: read) on __bennett_measure declaration; O0: native build failed at link; O3: native build failed at link
  - reproduce: `python3 corpus/legality/harness/run.py replay 3a9df1dab30af3f99c6b`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt -passes=hwasan /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/1d0a1b5dc910530ae6967d6118c46c3906df60e31fa1daa1924fb7a400378325/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/3a9df1dab30af3f99c6b/output.bc`
- **`control-readonly`** (probe) — P1 `scc-oz-module-inliner` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay a388769a2cf9008c6371`; opt: `/usr/lib/llvm-18/bin/opt -passes=scc-oz-module-inliner /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/a388769a2cf9008c6371/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P2 `default<O1>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 55431a34c92205a137fb`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O1>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/55431a34c92205a137fb/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P2 `default<O2>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 598ec3576f6e0b3055b1`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O2>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/598ec3576f6e0b3055b1/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P2 `default<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 1d2f991a614d10ce18ae`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/1d2f991a614d10ce18ae/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P2 `default<O3>,default<O3>,default<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 96ba35a564e8d25305fb`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<O3>,default<O3>,default<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/96ba35a564e8d25305fb/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P2 `default<Os>` — **L1,L5** — LLVM 18,20; modes raw; 2 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 8bdf4256db94a03e2ffe`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<Os>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/8bdf4256db94a03e2ffe/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P2 `default<Oz>` — **L1,L5** — LLVM 18,20; modes raw; 2 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 6697f53bdf1a50567a6a`; opt: `/usr/lib/llvm-18/bin/opt '-passes=default<Oz>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/6697f53bdf1a50567a6a/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P2 `lto-pre-link<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 442974e12f3a884cc324`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lto-pre-link<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/442974e12f3a884cc324/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P2 `lto<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay ab19c6b500f3c250517e`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lto<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/ab19c6b500f3c250517e/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P2 `thinlto-pre-link<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 7b48430e2b9add3141ce`; opt: `/usr/lib/llvm-18/bin/opt '-passes=thinlto-pre-link<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/7b48430e2b9add3141ce/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P2 `thinlto<O3>` — **L1,L5** — LLVM 18,20,23; modes raw; 3 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 4f63579bf54679f8a607`; opt: `/usr/lib/llvm-18/bin/opt '-passes=thinlto<O3>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/4f63579bf54679f8a607/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P3 `107 random sequences, each containing a pass that FAILs alone on this case (function(loop-mssa(licm)) 44, function(loop-mssa(lnicm)) 42, scc-oz-module-inliner 31, function(normalize) 6)` — **L1,L5** — LLVM 18,20,23; modes seq-0000,seq-0002,seq-0003,seq-0006,seq-0010,seq-0011,seq-0015,seq-0017,seq-0018,seq-0022,seq-0028,seq-0029,seq-0031,seq-0035,seq-0037,seq-0038,seq-0041,seq-0046,seq-0047,seq-0048,seq-0049,seq-0051,seq-0052,seq-0056,seq-0058,seq-0061,seq-0062,seq-0064,seq-0065,seq-0066,seq-0067,seq-0070,seq-0071,seq-0073,seq-0075,seq-0076,seq-0077,seq-0080,seq-0081,seq-0082,seq-0086,seq-0092,seq-0094,seq-0096,seq-0098,seq-0100,seq-0103,seq-0108,seq-0109,seq-0110,seq-0115,seq-0119,seq-0122,seq-0123,seq-0124,seq-0126,seq-0129,seq-0130,seq-0131,seq-0132,seq-0133,seq-0134,seq-0136,seq-0137,seq-0138,seq-0142,seq-0143,seq-0144,seq-0145,seq-0148,seq-0151,seq-0153,seq-0162,seq-0163,seq-0165,seq-0167,seq-0170,seq-0171,seq-0173,seq-0175,seq-0179,seq-0182,seq-0183,seq-0187,seq-0188,seq-0189,seq-0192,seq-0196,seq-0198,seq-0199; 107 cells
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay e462d0216850a3685385`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=annotation2metadata,function(loop(print)),function(print<cfg-sccs>),function(view-dom),cgscc(coro-annotation-elide),strip-dead-prototypes,function(print<phi-values>),function(callsite-splitting),function(ee-instrument),function(print<scev-division>),function(bounds-checking),deadargelim,function(verify<regions>),ipsccp,print<inline-advisor>,dxil-upgrade,function(loop-mssa(lnicm)),function(declare-to-assign),print<module-debuginfo>,function(print<domfrontier>),globalopt,function(lower-invoke),cgscc(function-attrs),ipsccp,function(memcpyopt),print<module-debuginfo>,function(lower-guard-intrinsic),function(loop(loop-unroll-full)),function(print<regions>),function(lower-widenable-condition),strip-dead-prototypes,print,openmp-opt,wholeprogramdevirt,function(loop-unroll),function(print<delinearization>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/e462d0216850a3685385/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P3 `seq-0045 (33 passes)` — **L1,L5** — LLVM 18; modes seq-0045; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 34ba0bc8eee6f2bfad86`; opt: `/usr/lib/llvm-18/bin/opt '-passes=coro-early,function(loop(print<loop-cache-cost>)),deadargelim,function(callbrprepare),function(loop(dot-ddg)),function(loop-unroll),openmp-opt-postlink,function(guard-widening),function(loop(loop-rotate)),function(safe-stack),function(print<scalar-evolution>),invalidate<all>,strip-debug-declare,function(print<cycles>),function(print<demanded-bits>),function(loop-versioning),function(loop(loop-unroll-full)),function(infer-alignment),function(print<uniformity>),hipstdpar-interpose-alloc,rewrite-symbols,function(declare-to-assign),function(loop-fusion),function(print<stack-safety-local>),function(early-cse),inferattrs,function(loop(loop-flatten)),function(print<domfrontier>),function(print),view-callgraph,function(print<stack-safety-local>),function(separate-const-offset-from-gep),strip-dead-prototypes' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/34ba0bc8eee6f2bfad86/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P3 `seq-0083 (36 passes)` — **L1,L5** — LLVM 18; modes seq-0083; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay fef801301a0fb05c2995`; opt: `/usr/lib/llvm-18/bin/opt '-passes=dxil-upgrade,function(fix-irreducible),function(loop-fusion),function(instnamer),function(pgo-memop-opt),function(verify<safepoint-ir>),function(helloworld),function(constraint-elimination),function(slp-vectorizer),print-lcg,function(irce),function(sccp),function(print<memoryssa>),loop-extract,sanmd-module,function(loop-unroll),cgscc(attributor-cgscc),partial-inliner,function(loop-distribute),check-debugify,function(loop(loop-interchange)),rel-lookup-table-converter,function(sccp),function(print<debug-ata>),print-lcg,function(print<uniformity>),function(tailcallelim),print-profile-summary,memprof-context-disambiguation,function(simplifycfg),function(loop(loop-unroll-full)),function(objc-arc-expand),strip-nonlinetable-debuginfo,function(newgvn),function(loop(loop-unroll-full)),cgscc(argpromotion)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/fef801301a0fb05c2995/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P3 `seq-0030 (23 passes)` — **L1,L5** — LLVM 23; modes seq-0030; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 78a2dbdaec08dfb55848`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=function(break-crit-edges),mir-strip-debug,function(print<demanded-bits>),deadargelim,function(loop(loop-unroll-full)),function(instcount),lower-emutls,function(print<uniformity>),function(assume-builder),function(reassociate),function(verify),cg-profile,lower-comment-string,cross-dso-cfi,function(mergeicmps),jmc-instrumenter,function(infer-alignment),inliner-wrapper,function(early-cse),function(tailcallelim),function(aggressive-instcombine),function(print<da>),function(verify<loops>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/78a2dbdaec08dfb55848/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P3 `seq-0190 (29 passes)` — **L1,L5** — LLVM 20; modes seq-0190; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 2af380345275b9285c8d`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(lcssa),function(loop-unroll),function(sink),lower-ifunc,function(print<stack-lifetime>),function(dot-dom-only),no-op-module,function(wasm-eh-prepare),jmc-instrumenter,debugify,print-ir-similarity,function(consthoist),function(dot-post-dom),function(verify<memoryssa>),print<dxil-metadata>,strip-nondebug,function(loop(loop-reduce)),sancov-module,function(bdce),function(load-store-vectorizer),function(early-cse),function(pa-eval),function(loop(indvars)),function(infer-alignment),function(print<func-properties>),no-op-module,print<module-debuginfo>,function(dot-cfg-only),function(loop(loop-rotate))' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/2af380345275b9285c8d/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P3 `seq-0156 (29 passes)` — **L1,L5** — LLVM 20; modes seq-0156; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 20b115758f46c991d6eb`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=function(loop-unroll),function(loop(loop-deletion)),function(adce),function(alignment-from-assumptions),function(lower-expect),lower-global-dtors,function(cfguard),function(loop(print<iv-users>)),function(loop-versioning),function(load-store-vectorizer),rewrite-symbols,function(newgvn),function(verify<loops>),function(guard-widening),function(instcombine<no-verify-fixpoint>),dxil-upgrade,function(break-crit-edges),function(annotation-remarks),function(print<da>),function(print<inliner-size-estimator>),inliner-wrapper-no-mandatory-first,function(aa-eval),debugify,function(loop-fusion),function(print<func-properties>),print<dxil-metadata>,function(loop(loop-idiom)),function(callbr-prepare),print<inline-advisor>' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/20b115758f46c991d6eb/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P3 `seq-0091 (32 passes)` — **L1,L5** — LLVM 18; modes seq-0091; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 96d88e8dcbf215cee3ea`; opt: `/usr/lib/llvm-18/bin/opt '-passes=function(slsr),function(break-crit-edges),objc-arc-apelim,function(aggressive-instcombine),recompute-globalsaa,function(view-dom-only),function(annotation-remarks),function(dot-post-dom),function(callbrprepare),function(print<domtree>),function(objc-arc),function(verify<scalar-evolution>),function(gvn-sink),function(mem2reg),inliner-wrapper,function(view-cfg),function(verify),print,function(gvn),function(sroa),inferattrs,function(print<stack-safety-local>),print<structural-hash>,function(loop-unroll),print<module-debuginfo>,function(newgvn),annotation2metadata,instrorderfile,function(objc-arc),function(jump-threading),function(print-predicateinfo),function(bdce)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/96d88e8dcbf215cee3ea/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P3 `seq-0075 (35 passes)` — **L1,L5** — LLVM 18; modes seq-0075; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay c6b885cc53d377f48039`; opt: `/usr/lib/llvm-18/bin/opt '-passes=hipstdpar-interpose-alloc,function(infer-address-spaces),wholeprogramdevirt,print-profile-summary,function(loop-versioning),function(tailcallelim),function(loweratomic),pseudo-probe,inliner-wrapper-no-mandatory-first,function(infer-address-spaces),function(count-visits),function(loop(loop-unroll-full)),openmp-opt-postlink,function(adce),function(loop(print<loopnest>)),function(view-cfg),constmerge,function(view-cfg),function(print<loops>),function(verify<regions>),cross-dso-cfi,instrorderfile,function(loop(loop-unroll-full)),function(sroa),function(transform-warning),function(print),function(print<inline-cost>),function(print<scalar-evolution>),lowertypetests,function(newgvn),strip-dead-prototypes,function(lower-expect),no-op-module,recompute-globalsaa,function(load-store-vectorizer)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/c6b885cc53d377f48039/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P3 `seq-0108 (19 passes)` — **L1,L5** — LLVM 18; modes seq-0108; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 0c908caa79226d575de5`; opt: `/usr/lib/llvm-18/bin/opt '-passes=lower-emutls,function(correlated-propagation),function(print<domfrontier>),function(lcssa),no-op-module,function(sroa),function(flattencfg),module-inline,function(print<postdomtree>),function(loop(print<loopnest>)),function(dot-cfg-only),cgscc(coro-split),function(print-cfg-sccs),function(count-visits),function(partially-inline-libcalls),function(loop(loop-unroll-full)),function(gvn),function(loop(loop-versioning-licm)),function(print<regions>)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/0c908caa79226d575de5/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P3 `seq-0166 (33 passes)` — **L1,L5** — LLVM 18; modes seq-0166; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay 59c36c6337ec8233fddb`; opt: `/usr/lib/llvm-18/bin/opt '-passes=openmp-opt-postlink,function(lowerinvoke),strip-debug-declare,function(pgo-memop-opt),rel-lookup-table-converter,function(bounds-checking),function(stack-protector),function(loop(invalidate<all>)),function(verify),print-lcg,cgscc(attributor-light-cgscc),cgscc(function-attrs),strip-dead-prototypes,function(loop-unroll),print-stack-safety,coro-cleanup,function(bdce),function(print<domtree>),function(dot-post-dom-only),function(reassociate),print,function(newgvn),print-callgraph,function(kcfi),function(print<block-freq>),openmp-opt,function(loop-unroll),coro-cleanup,function(objc-arc-expand),function(add-discriminators),strip-nondebug,function(loop(loop-reroll)),function(loop(loop-predication))' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/59c36c6337ec8233fddb/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-readonly`** (probe) — P3 `seq-0125 (33 passes)` — **L1,L5** — LLVM 23; modes seq-0125; 1 cells
  - **interaction**: no pass of this sequence FAILs alone on this case in P1
  - diagnosis: first trace difference: -MEASURE H0 0 1 0 / -MEASURE H0 0 2 1
  - reproduce: `python3 corpus/legality/harness/run.py replay b1cd628b78d71a6bea82`; opt: `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt '-passes=pseudo-probe,coro-early,function(lower-guard-intrinsic),function(place-safepoints),attributor-light,function(loop(loop-rotate)),function(print<scev-division>),function(func-properties-stats),cross-dso-cfi,function(loop(invalidate<all>)),hipstdpar-math-fixup,cgscc(coro-annotation-elide),cgscc(function-attrs),coro-cleanup,print-must-be-executed-contexts,function(loop-unroll),function(hardware-loops),function(mergeicmps),fatlto-cleanup,function(ee-instrument),function(dfa-jump-threading),function(newgvn),function(print<scalar-evolution>),function(loop(print<ddg>)),print<ctx-prof-analysis>,extract-blocks,function(print<delinearization>),function(simplifycfg),function(print<block-freq>),function(loop(loop-deletion)),function(print<block-freq>),expand-variadics,rewrite-symbols' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/802c8843bdeb02d6a77b0f78e29ddd83671197ce3a0c6d1486c058ea9657ce94/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/b1cd628b78d71a6bea82/output.bc`
  <details><summary>trace diff head</summary>

  ```diff
  --- baseline-O0
  +++ transformed-O0
  @@ -1,64 +1,40 @@
   IN 0
   QALLOC H0 0 1
   MEASURE H0 0 0 1
  -MEASURE H0 0 1 0
  -MEASURE H0 0 2 1
  -MEASURE H0 0 3 0
   QFREE H0
  -RET 2
  +RET 4
   IN 1
   QALLOC H0 0 1
  ...
  ```
  </details>
- **`control-region-twin`** (probe) — P1 `mergefunc` — **L4** — LLVM 18,20,23; modes post-O3,raw; 6 cells
  - diagnosis: region twin_b became a forwarding thunk to twin_a
  - reproduce: `python3 corpus/legality/harness/run.py replay b5c1518f2ac7de3e0279`; opt: `/usr/lib/llvm-18/bin/opt -passes=mergefunc /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/18/f85a6dd9b4cec28514ae87c9d5b1d66712ba89228a1bbfb6710ea715e118e2f2/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/b5c1518f2ac7de3e0279/output.bc`
- **`control-region-twin`** (probe) — P3 `28 random sequences, each containing a pass that FAILs alone on this case (mergefunc 28)` — **L4** — LLVM 18,20,23; modes seq-0006,seq-0012,seq-0014,seq-0020,seq-0029,seq-0033,seq-0049,seq-0057,seq-0062,seq-0069,seq-0076,seq-0082,seq-0087,seq-0089,seq-0107,seq-0116,seq-0129,seq-0130,seq-0131,seq-0134,seq-0138,seq-0152,seq-0154,seq-0156,seq-0159,seq-0174,seq-0185,seq-0186; 28 cells
  - diagnosis: region twin_b became a forwarding thunk to twin_a
  - reproduce: `python3 corpus/legality/harness/run.py replay 642f8f48220de309ffad`; opt: `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt '-passes=cross-dso-cfi,function(load-store-vectorizer),memprof-context-disambiguation,pgo-icall-prom,function(print-predicateinfo),shadow-stack-gc-lowering,mergefunc,mergefunc,function(hardware-loops),function(lower-guard-intrinsic),function(instsimplify),check-debugify,function(sroa),function(loop(guard-widening)),coro-cleanup,cgscc(openmp-opt-cgscc),function(print<block-freq>),function(no-op-function),function(jump-table-to-switch),name-anon-globals,global-merge,function(loop(loop-term-fold)),function(print<branch-prob>),print-lcg,function(print-alias-sets),function(objc-arc-contract),function(loop(loop-instsimplify)),function(print<memoryssa>),print-lcg,function(print<func-properties>),strip,function(mem2reg)' /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/20/ea277dce36c52053507fe1b4252db2014669615958674831ba09bedfdead9f4f/module.bc -o /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/cells/642f8f48220de309ffad/output.bc`

## 5. L2 observations (added marker attributes that are not forbidden)

- `"frame-pointer"="all"`: `dfsan` (18,20,23)
- `"no-trapping-math"="true"`: `dfsan` (18,20,23)
- `"op10117(op11958)"`: `function(normalize)` (23)
- `"op10199__bennett_qalloc(0, op38234(op36786(5, op62674(0, vl94238(%a0, 1))), 0, op87549(5, op62674(0, vl94238(%a0, 1)))))"`: `P3 sequences` (23)
- `"op10271__bennett_qalloc(0, op75265(1, vl62332(%a0, 4)))"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op10271__bennett_qborrow(0, op75265(1, vl62332(%a0, 4)))"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op10497(op58227)"`: `P3 sequences` (23)
- `"op10557(op21385)"`: `P3 sequences` (23)
- `"op10581__bennett_measure(vl20713__bennett_qalloc(0, 8), op90751(0, op17645(1, i)))"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op10581__bennett_measure(vl20713__bennett_qalloc(0, 8), op90751(0, op17645(1, i))).1"`: `P3 sequences` (20)
- `"op10581__bennett_measure(vl20713__bennett_qalloc(0, 8), op90751(0, op17645(1, i))).2"`: `P3 sequences` (20)
- `"op10581__bennett_measure(vl20713__bennett_qalloc(0, 8), op90751(0, op17645(1, i))).3"`: `P3 sequences` (20)
- `"op10647(op62674)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op10647(op67649)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op10647(op78175)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op10647(vl17123)"`: `function(normalize)` (23)
- `"op10647(vl63412)"`: `function(normalize)` (23)
- `"op10647(vl72525)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op10647(vl72525).i"`: `P3 sequences` (23)
- `"op10764(vl50347)"`: `P3 sequences` (20)
- `"op10764(vl81200)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op10926(op11847, op64863)"`: `function(normalize)` (20)
- `"op10955(vl12040, vl12040)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op10956(op15580)"`: `P3 sequences` (20)
- `"op10956(op68297)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op10956(op68297)1"`: `function(normalize)` (20)
- `"op10956(op68297)2"`: `function(normalize)` (20)
- `"op10956(op68297)3"`: `function(normalize)` (20)
- `"op10995(op12466)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11073(op16534)"`: `P3 sequences` (20)
- `"op11283(op16197)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op11395(op12113)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op11395(op15298)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op11395(op17645)"`: `function(normalize)` (20)
- `"op11395(vl12700)"`: `function(normalize)` (20)
- `"op11395(vl15055)"`: `function(normalize)` (20)
- `"op11395(vl24903)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op11536(vl13192)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11536(vl34383)"`: `P3 sequences` (23)
- `"op11536(vl34626)"`: `P3 sequences` (23)
- `"op11536(vl57928)"`: `function(normalize)` (23)
- `"op11701(vl81224, vl81224)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11747(op11194)"`: `function(normalize)` (23)
- `"op11777(op14298)"`: `P3 sequences` (23)
- `"op11777(op14298)1"`: `P3 sequences` (23)
- `"op11846(op13802)"`: `P3 sequences` (23)
- `"op11846(op13802)14"`: `P3 sequences` (23)
- `"op11846(op13802)15"`: `P3 sequences` (23)
- `"op11846(op13802)16"`: `P3 sequences` (23)
- `"op11958(op11194)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958(vl31633(0, 2), 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958(vl31633)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958(vl37564(0, 2), 0)"`: `P3 sequences` (23)
- `"op11958__bennett_measure(vl10604__bennett_qalloc(0, 1), 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl12417__bennett_qalloc(0, 1), 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl12417__bennett_qalloc(0, 2), 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl12417__bennett_qalloc(0, 2), 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl24259__bennett_qalloc(0, 1), 0)"`: `P3 sequences` (23)
- `"op11958__bennett_measure(vl26594__bennett_qalloc(0, 1), 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 1), 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 1), 0)1"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 1), 0)10"`: `P3 sequences` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 1), 0)12"`: `P3 sequences` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 1), 0)13"`: `P3 sequences` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 1), 0)14"`: `P3 sequences` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 1), 0)2"`: `function(normalize)` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 1), 0)3"`: `function(normalize)` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 1), 0)32"`: `P3 sequences` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 1), 0)33"`: `P3 sequences` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 1), 0)34"`: `P3 sequences` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 2), 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 2), 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 4), 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 4), 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 4), 2)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 4), 3)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 8), 0)"`: `function(normalize)` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 8), 1)"`: `function(normalize)` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 8), 2)"`: `function(normalize)` (23)
- `"op11958__bennett_measure(vl31633__bennett_qalloc(0, 8), 3)"`: `function(normalize)` (23)
- `"op11958__bennett_measure(vl40545__bennett_qalloc(0, 1), 0)"`: `P3 sequences` (23)
- `"op11958__bennett_measure(vl43888__bennett_qalloc(0, 1), 0)"`: `P3 sequences` (23)
- `"op11958__bennett_measure(vl49268__bennett_qalloc(0, 1), 0)"`: `P3 sequences` (23)
- `"op11958__bennett_measure(vl53563__bennett_qalloc(0, 1), 0)"`: `function(normalize)` (23)
- `"op11958__bennett_measure(vl72598__bennett_qalloc(0, 1), 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl72598__bennett_qalloc(0, 1), 0)10"`: `function(normalize)` (23)
- `"op11958__bennett_measure(vl72598__bennett_qalloc(0, 1), 0)11"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl72598__bennett_qalloc(0, 1), 0)12"`: `function(normalize)` (23)
- `"op11958__bennett_measure(vl72598__bennett_qalloc(0, 1), 0)13"`: `function(normalize)` (23)
- `"op11958__bennett_measure(vl72598__bennett_qalloc(0, 1), 0)2"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl72598__bennett_qalloc(0, 1), 0)7"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl72598__bennett_qalloc(0, 1), 0)8"`: `function(normalize)` (23)
- `"op11958__bennett_measure(vl72598__bennett_qalloc(0, 1), 0)9"`: `function(normalize)` (23)
- `"op11958__bennett_measure(vl72598__bennett_qalloc(0, 2), 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl72598__bennett_qalloc(0, 2), 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op11958__bennett_measure(vl72598__bennett_qalloc(0, 4), 3)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl10117)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl10117)8"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl11054)"`: `P3 sequences` (23)
- `"op12466(vl11111)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl11389)"`: `P3 sequences` (23)
- `"op12466(vl11474)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl11474)2"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl11538)"`: `P3 sequences` (23)
- `"op12466(vl11538)7"`: `P3 sequences` (23)
- `"op12466(vl11980)"`: `P3 sequences` (23)
- `"op12466(vl12102)"`: `P3 sequences` (23)
- `"op12466(vl12822)"`: `P3 sequences` (23)
- `"op12466(vl13419)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl13428)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl13428)19"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl13428)21"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl13428)23"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl13428)25"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl13428)27"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl13428)29"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl13495)"`: `P3 sequences` (23)
- `"op12466(vl13757)"`: `P3 sequences` (23)
- `"op12466(vl13757)2"`: `P3 sequences` (23)
- `"op12466(vl14123)"`: `P3 sequences` (23)
- `"op12466(vl14247)"`: `P3 sequences` (23)
- `"op12466(vl14472)19"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl14637)50"`: `P3 sequences` (23)
- `"op12466(vl15399)"`: `function(normalize)` (23)
- `"op12466(vl15605)"`: `P3 sequences` (23)
- `"op12466(vl15757)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl15989)"`: `P3 sequences` (23)
- `"op12466(vl16379)"`: `function(normalize)` (23)
- `"op12466(vl16396)"`: `P3 sequences` (23)
- `"op12466(vl16826)"`: `function(normalize)` (23)
- `"op12466(vl16849)"`: `function(normalize)` (23)
- `"op12466(vl17102)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl17145)"`: `function(normalize)` (23)
- `"op12466(vl17297)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl17297).i"`: `P3 sequences` (23)
- `"op12466(vl17386)"`: `P3 sequences` (23)
- `"op12466(vl17386)2"`: `P3 sequences` (23)
- `"op12466(vl17738)"`: `P3 sequences` (23)
- `"op12466(vl17738)37"`: `P3 sequences` (23)
- `"op12466(vl17738)56"`: `P3 sequences` (23)
- `"op12466(vl17738)59"`: `P3 sequences` (23)
- `"op12466(vl17821)"`: `P3 sequences` (23)
- `"op12466(vl17934)11"`: `P3 sequences` (23)
- `"op12466(vl18148)"`: `P3 sequences` (23)
- `"op12466(vl18413)"`: `P3 sequences` (23)
- `"op12466(vl18745)"`: `function(normalize)` (23)
- `"op12466(vl25219)"`: `P3 sequences` (23)
- `"op12466(vl25219)45"`: `P3 sequences` (23)
- `"op12466(vl25219)59"`: `P3 sequences` (23)
- `"op12466(vl25219)62"`: `P3 sequences` (23)
- `"op12466(vl28701)"`: `P3 sequences` (23)
- `"op12466(vl28701)6"`: `P3 sequences` (23)
- `"op12466(vl28701)7"`: `P3 sequences` (23)
- `"op12466(vl31166)"`: `P3 sequences` (23)
- `"op12466(vl31268)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl31268)20"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl31268)22"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl31268)24"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl31268)26"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl31268)28"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl31268)30"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl32673)"`: `P3 sequences` (23)
- `"op12466(vl32673)36"`: `P3 sequences` (23)
- `"op12466(vl32673)38"`: `P3 sequences` (23)
- `"op12466(vl32673)40"`: `P3 sequences` (23)
- `"op12466(vl32673)42"`: `P3 sequences` (23)
- `"op12466(vl32673)44"`: `P3 sequences` (23)
- `"op12466(vl32673)46"`: `P3 sequences` (23)
- `"op12466(vl33730)"`: `function(normalize)` (23)
- `"op12466(vl42134)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl45156)"`: `P3 sequences` (23)
- `"op12466(vl45156)9"`: `P3 sequences` (23)
- `"op12466(vl46766)2"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl47949)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl47949)5"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl47949)7"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl47949)8"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl58029)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl58029).i"`: `P3 sequences` (23)
- `"op12466(vl58042)"`: `P3 sequences` (23)
- `"op12466(vl59467)"`: `P3 sequences` (23)
- `"op12466(vl59467)8"`: `P3 sequences` (23)
- `"op12466(vl59728)"`: `P3 sequences` (23)
- `"op12466(vl59728)11"`: `P3 sequences` (23)
- `"op12466(vl64431)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl65922)"`: `P3 sequences` (23)
- `"op12466(vl67739)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl67739)9"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl70601)"`: `P3 sequences` (23)
- `"op12466(vl72690)"`: `function(normalize)` (23)
- `"op12466(vl75695)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl76580)"`: `P3 sequences` (23)
- `"op12466(vl76580)40"`: `P3 sequences` (23)
- `"op12466(vl76580)59"`: `P3 sequences` (23)
- `"op12466(vl76580)62"`: `P3 sequences` (23)
- `"op12466(vl80278)15"`: `P3 sequences` (23)
- `"op12466(vl83663)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl83663)14"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl83663)16"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl84937)"`: `function(normalize)` (23)
- `"op12466(vl84937)5"`: `function(normalize)` (23)
- `"op12466(vl84937)6"`: `function(normalize)` (23)
- `"op12466(vl84937)7"`: `function(normalize)` (23)
- `"op12466(vl84937)8"`: `function(normalize)` (23)
- `"op12466(vl85806)"`: `P3 sequences` (23)
- `"op12466(vl86444)18"`: `P3 sequences` (23)
- `"op12466(vl88508)"`: `P3 sequences` (23)
- `"op12466(vl88508)10"`: `P3 sequences` (23)
- `"op12466(vl88556)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl88556)33"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl88556)47"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl88556)50"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl89934)"`: `function(normalize)` (23)
- `"op12466(vl91786)"`: `P3 sequences` (23)
- `"op12466(vl93131)"`: `P3 sequences` (23)
- `"op12466(vl93131)37"`: `P3 sequences` (23)
- `"op12466(vl93131)39"`: `P3 sequences` (23)
- `"op12466(vl93131)41"`: `P3 sequences` (23)
- `"op12466(vl93131)43"`: `P3 sequences` (23)
- `"op12466(vl93131)45"`: `P3 sequences` (23)
- `"op12466(vl93131)47"`: `P3 sequences` (23)
- `"op12466(vl94475)"`: `P3 sequences` (23)
- `"op12466(vl94579)13"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl97059)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op12466(vl99131)"`: `P3 sequences` (23)
- `"op12698(op29182)"`: `function(normalize)` (20)
- `"op12840__bennett_qalloc(0, op22110(5, vl70728(%a0, 1)))"`: `function(normalize)` (20)
- `"op12921(op32900)"`: `P3 sequences` (20)
- `"op12921(op61660)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op12921(vl16466)"`: `function(normalize)` (20)
- `"op12921(vl44313)1"`: `function(normalize)` (20)
- `"op12921(vl44313)2"`: `function(normalize)` (20)
- `"op12921(vl44664)"`: `P3 sequences` (20)
- `"op12941(op85785)"`: `function(normalize)` (23)
- `"op12947(vl11951)"`: `P3 sequences` (23)
- `"op12947(vl13218)"`: `P3 sequences` (23)
- `"op12960__bennett_measure(op15150(vl12081(1))9, vl11679(%a0, 1))"`: `P3 sequences` (20)
- `"op13287__bennett_measure(%a0, vl14917(%a1, 3))"`: `function(normalize)` (23)
- `"op13287__bennett_measure(%a0, vl34595(%a1, 3))"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13380(op17212)"`: `P3 sequences` (20)
- `"op13380(op18321)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op13536(vl41281)"`: `P3 sequences` (23)
- `"op13536(vl52002)"`: `P3 sequences` (23)
- `"op13536(vl79218)"`: `P3 sequences` (23)
- `"op13536(vl96711)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op11267)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op11267)13"`: `P3 sequences` (23)
- `"op13802(op11267)14"`: `P3 sequences` (23)
- `"op13802(op11267)3"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op11267)5"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op11452)"`: `function(normalize)` (23)
- `"op13802(op11452)11"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op11452)12"`: `P3 sequences` (23)
- `"op13802(op11452)14"`: `P3 sequences` (23)
- `"op13802(op11452)15"`: `function(normalize)` (23)
- `"op13802(op11452)16"`: `P3 sequences` (23)
- `"op13802(op11452)18"`: `function(normalize)` (23)
- `"op13802(op11452)24"`: `P3 sequences` (23)
- `"op13802(op11704)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op11760)"`: `P3 sequences` (23)
- `"op13802(op12584)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op12729)"`: `function(normalize)` (23)
- `"op13802(op14795)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op14795)10"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op14795)11"`: `P3 sequences` (23)
- `"op13802(op14795)12"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op14795)13"`: `P3 sequences` (23)
- `"op13802(op14795)17"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op14795)18"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op14795)20"`: `P3 sequences` (23)
- `"op13802(op14795)21"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op14795)22"`: `P3 sequences` (23)
- `"op13802(op14795)24"`: `P3 sequences` (23)
- `"op13802(op14795)27"`: `P3 sequences` (23)
- `"op13802(op14795)29"`: `P3 sequences` (23)
- `"op13802(op14795)31"`: `P3 sequences` (23)
- `"op13802(op14795)4"`: `function(normalize)` (23)
- `"op13802(op14795)49"`: `P3 sequences` (23)
- `"op13802(op14795)5"`: `P3 sequences` (23)
- `"op13802(op14795)50"`: `P3 sequences` (23)
- `"op13802(op14795)52"`: `P3 sequences` (23)
- `"op13802(op14795)6"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op14795)7"`: `P3 sequences` (23)
- `"op13802(op14795)8"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op14795)9"`: `P3 sequences` (23)
- `"op13802(op18112)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op18112)1"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op18112)2"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op18112)4"`: `P3 sequences` (23)
- `"op13802(op24071)"`: `P3 sequences` (23)
- `"op13802(op24071)22"`: `P3 sequences` (23)
- `"op13802(op24071)27"`: `P3 sequences` (23)
- `"op13802(op38920)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op38920).i"`: `P3 sequences` (23)
- `"op13802(op38920)127"`: `P3 sequences` (23)
- `"op13802(op38920)134"`: `P3 sequences` (23)
- `"op13802(op38920)44"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op38920)53"`: `P3 sequences` (23)
- `"op13802(op38920)54"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op38920)56"`: `P3 sequences` (23)
- `"op13802(op38920)59"`: `P3 sequences` (23)
- `"op13802(op38920)60"`: `P3 sequences` (23)
- `"op13802(op38920)63"`: `P3 sequences` (23)
- `"op13802(op38920)66"`: `P3 sequences` (23)
- `"op13802(op38920)67"`: `P3 sequences` (23)
- `"op13802(op44586)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op80883)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op80883)4"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(op96402)"`: `P3 sequences` (23)
- `"op13802(vl10193)"`: `P3 sequences` (23)
- `"op13802(vl10201)"`: `P3 sequences` (23)
- `"op13802(vl10572)"`: `P3 sequences` (23)
- `"op13802(vl10731)"`: `P3 sequences` (23)
- `"op13802(vl11103)"`: `function(normalize)` (23)
- `"op13802(vl12915)"`: `function(normalize)` (23)
- `"op13802(vl12997)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(vl13033)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(vl13033)1"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(vl13033)2"`: `P3 sequences` (23)
- `"op13802(vl13033)3"`: `P3 sequences` (23)
- `"op13802(vl13033)5"`: `P3 sequences` (23)
- `"op13802(vl13289)"`: `P3 sequences` (23)
- `"op13802(vl13289)1"`: `P3 sequences` (23)
- `"op13802(vl13336)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(vl14006)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(vl14366)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(vl18395)"`: `P3 sequences` (23)
- `"op13802(vl18439)"`: `P3 sequences` (23)
- `"op13802(vl19896)"`: `P3 sequences` (23)
- `"op13802(vl27029)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(vl32383)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(vl33985)"`: `P3 sequences` (23)
- `"op13802(vl38371)"`: `P3 sequences` (23)
- `"op13802(vl38371)1"`: `P3 sequences` (23)
- `"op13802(vl60141)"`: `P3 sequences` (23)
- `"op13802(vl61774)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(vl61774)3"`: `P3 sequences` (23)
- `"op13802(vl65884)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(vl73166)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op13802(vl76060)"`: `function(normalize)` (23)
- `"op13802(vl98197)"`: `P3 sequences` (23)
- `"op13886(vl11026, vl11026, vl11026)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op14049(op73296)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op14049(vl15033)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op14049(vl78063)"`: `P3 sequences` (20)
- `"op14290(vl32589)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op14628(op64863)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op14764(op26584, op37946)"`: `function(normalize)` (23)
- `"op14991(vl11745)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op14991(vl12635)"`: `function(normalize)` (20)
- `"op14991(vl29895)"`: `function(normalize)` (20)
- `"op14991(vl66779)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl10049)11"`: `P3 sequences` (20)
- `"op15150(vl10181)"`: `P3 sequences` (20)
- `"op15150(vl10336)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl10336)22"`: `P3 sequences` (20)
- `"op15150(vl10336)24"`: `P3 sequences` (20)
- `"op15150(vl10336)25"`: `P3 sequences` (20)
- `"op15150(vl10336)5"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl10336)7"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl10336)8"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl10347)"`: `P3 sequences` (20)
- `"op15150(vl10347)23"`: `P3 sequences` (20)
- `"op15150(vl10347)28"`: `P3 sequences` (20)
- `"op15150(vl10396)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl10783)35"`: `P3 sequences` (20)
- `"op15150(vl10819)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl11031)13"`: `P3 sequences` (20)
- `"op15150(vl11031)14"`: `P3 sequences` (20)
- `"op15150(vl11042)27"`: `P3 sequences` (20)
- `"op15150(vl11042)28"`: `P3 sequences` (20)
- `"op15150(vl11148)"`: `P3 sequences` (20)
- `"op15150(vl11148)49"`: `P3 sequences` (20)
- `"op15150(vl11299)"`: `P3 sequences` (20)
- `"op15150(vl11299)47"`: `P3 sequences` (20)
- `"op15150(vl11299)49"`: `P3 sequences` (20)
- `"op15150(vl11299)51"`: `P3 sequences` (20)
- `"op15150(vl11299)53"`: `P3 sequences` (20)
- `"op15150(vl11299)55"`: `P3 sequences` (20)
- `"op15150(vl11299)57"`: `P3 sequences` (20)
- `"op15150(vl11550)"`: `P3 sequences` (20)
- `"op15150(vl11550)15"`: `P3 sequences` (20)
- `"op15150(vl11680)"`: `P3 sequences` (20)
- `"op15150(vl11680)12"`: `P3 sequences` (20)
- `"op15150(vl11680)13"`: `P3 sequences` (20)
- `"op15150(vl11680)14"`: `P3 sequences` (20)
- `"op15150(vl11680)15"`: `P3 sequences` (20)
- `"op15150(vl11680)16"`: `P3 sequences` (20)
- `"op15150(vl11709)"`: `P3 sequences` (20)
- `"op15150(vl11709)44"`: `P3 sequences` (20)
- `"op15150(vl11762)"`: `function(normalize)` (20)
- `"op15150(vl11794)"`: `P3 sequences` (20)
- `"op15150(vl11794)23"`: `P3 sequences` (20)
- `"op15150(vl11794)24"`: `P3 sequences` (20)
- `"op15150(vl11794)27"`: `P3 sequences` (20)
- `"op15150(vl11794)30"`: `P3 sequences` (20)
- `"op15150(vl12050)"`: `P3 sequences` (20)
- `"op15150(vl12050)26"`: `P3 sequences` (20)
- `"op15150(vl12081)"`: `P3 sequences` (20)
- `"op15150(vl12081)13"`: `P3 sequences` (20)
- `"op15150(vl12081)14"`: `P3 sequences` (20)
- `"op15150(vl12081)15"`: `P3 sequences` (20)
- `"op15150(vl12081)16"`: `P3 sequences` (20)
- `"op15150(vl12081)17"`: `P3 sequences` (20)
- `"op15150(vl12278)"`: `P3 sequences` (20)
- `"op15150(vl12278)50"`: `P3 sequences` (20)
- `"op15150(vl12493)"`: `function(normalize)` (20)
- `"op15150(vl12574)"`: `P3 sequences` (20)
- `"op15150(vl12618)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl12618)20"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl12618)22"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl12618)24"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl12618)26"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl12618)28"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl12618)30"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl12739)"`: `P3 sequences` (20)
- `"op15150(vl12739)22"`: `P3 sequences` (20)
- `"op15150(vl12739)24"`: `P3 sequences` (20)
- `"op15150(vl12739)26"`: `P3 sequences` (20)
- `"op15150(vl12739)29"`: `P3 sequences` (20)
- `"op15150(vl12793)"`: `P3 sequences` (20)
- `"op15150(vl13087)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl13160)"`: `P3 sequences` (20)
- `"op15150(vl13823)"`: `P3 sequences` (20)
- `"op15150(vl14011)"`: `P3 sequences` (20)
- `"op15150(vl14011)17"`: `P3 sequences` (20)
- `"op15150(vl14041)"`: `P3 sequences` (20)
- `"op15150(vl14041)12"`: `P3 sequences` (20)
- `"op15150(vl14336)"`: `P3 sequences` (20)
- `"op15150(vl14357)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl14357)19"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl14357)21"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl14357)23"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl14357)25"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl14357)27"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl14357)29"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl14920)"`: `P3 sequences` (20)
- `"op15150(vl14920)35"`: `P3 sequences` (20)
- `"op15150(vl14920)37"`: `P3 sequences` (20)
- `"op15150(vl14920)39"`: `P3 sequences` (20)
- `"op15150(vl14920)41"`: `P3 sequences` (20)
- `"op15150(vl14920)43"`: `P3 sequences` (20)
- `"op15150(vl14920)45"`: `P3 sequences` (20)
- `"op15150(vl15129)"`: `P3 sequences` (20)
- `"op15150(vl15129)23"`: `P3 sequences` (20)
- `"op15150(vl15129)25"`: `P3 sequences` (20)
- `"op15150(vl15129)27"`: `P3 sequences` (20)
- `"op15150(vl15186)"`: `P3 sequences` (20)
- `"op15150(vl15216)"`: `P3 sequences` (20)
- `"op15150(vl15216)14"`: `P3 sequences` (20)
- `"op15150(vl15216)15"`: `P3 sequences` (20)
- `"op15150(vl15216)17"`: `P3 sequences` (20)
- `"op15150(vl15283)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl15283)9"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl15486)"`: `P3 sequences` (20)
- `"op15150(vl15486)10"`: `P3 sequences` (20)
- `"op15150(vl15486)9"`: `P3 sequences` (20)
- `"op15150(vl15493)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl15623)"`: `P3 sequences` (20)
- `"op15150(vl15623)34"`: `P3 sequences` (20)
- `"op15150(vl15623)35"`: `P3 sequences` (20)
- `"op15150(vl15623)41"`: `P3 sequences` (20)
- `"op15150(vl15623)43"`: `P3 sequences` (20)
- `"op15150(vl15623)44"`: `P3 sequences` (20)
- `"op15150(vl15669)"`: `P3 sequences` (20)
- `"op15150(vl15669)36"`: `P3 sequences` (20)
- `"op15150(vl15669)38"`: `P3 sequences` (20)
- `"op15150(vl15669)40"`: `P3 sequences` (20)
- `"op15150(vl15669)42"`: `P3 sequences` (20)
- `"op15150(vl15669)44"`: `P3 sequences` (20)
- `"op15150(vl15669)45"`: `P3 sequences` (20)
- `"op15150(vl15669)47"`: `P3 sequences` (20)
- `"op15150(vl15669)49"`: `P3 sequences` (20)
- `"op15150(vl15669)50"`: `P3 sequences` (20)
- `"op15150(vl15719)"`: `P3 sequences` (20)
- `"op15150(vl15719)35"`: `P3 sequences` (20)
- `"op15150(vl15719)40"`: `P3 sequences` (20)
- `"op15150(vl15719)42"`: `P3 sequences` (20)
- `"op15150(vl15719)45"`: `P3 sequences` (20)
- `"op15150(vl15741)"`: `P3 sequences` (20)
- `"op15150(vl15741)49"`: `P3 sequences` (20)
- `"op15150(vl15741)54"`: `P3 sequences` (20)
- `"op15150(vl15741)56"`: `P3 sequences` (20)
- `"op15150(vl15741)63"`: `P3 sequences` (20)
- `"op15150(vl15771)"`: `P3 sequences` (20)
- `"op15150(vl15771)31"`: `P3 sequences` (20)
- `"op15150(vl15771)36"`: `P3 sequences` (20)
- `"op15150(vl15771)43"`: `P3 sequences` (20)
- `"op15150(vl15796)"`: `P3 sequences` (20)
- `"op15150(vl15796)9"`: `P3 sequences` (20)
- `"op15150(vl15828)"`: `P3 sequences` (20)
- `"op15150(vl15829)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl15829)2"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl15829)9"`: `P3 sequences` (20)
- `"op15150(vl15996)"`: `P3 sequences` (20)
- `"op15150(vl15996)12"`: `P3 sequences` (20)
- `"op15150(vl15996)13"`: `P3 sequences` (20)
- `"op15150(vl15996)15"`: `P3 sequences` (20)
- `"op15150(vl16102)"`: `P3 sequences` (20)
- `"op15150(vl16296)"`: `P3 sequences` (20)
- `"op15150(vl16296)2"`: `P3 sequences` (20)
- `"op15150(vl16457)"`: `function(normalize)` (20)
- `"op15150(vl16545)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl16597)"`: `function(normalize)` (20)
- `"op15150(vl16655)"`: `P3 sequences` (20)
- `"op15150(vl16655)32"`: `P3 sequences` (20)
- `"op15150(vl16794)"`: `P3 sequences` (20)
- `"op15150(vl16875)15"`: `P3 sequences` (20)
- `"op15150(vl16875)16"`: `P3 sequences` (20)
- `"op15150(vl16875)17"`: `P3 sequences` (20)
- `"op15150(vl16875)18"`: `P3 sequences` (20)
- `"op15150(vl16875)19"`: `P3 sequences` (20)
- `"op15150(vl16875)20"`: `P3 sequences` (20)
- `"op15150(vl16875)21"`: `P3 sequences` (20)
- `"op15150(vl17588).i"`: `P3 sequences` (20)
- `"op15150(vl17703)"`: `P3 sequences` (20)
- `"op15150(vl17703)52"`: `P3 sequences` (20)
- `"op15150(vl17703)58"`: `P3 sequences` (20)
- `"op15150(vl17703)60"`: `P3 sequences` (20)
- `"op15150(vl17748)"`: `P3 sequences` (20)
- `"op15150(vl17748)25"`: `P3 sequences` (20)
- `"op15150(vl17748)28"`: `P3 sequences` (20)
- `"op15150(vl17748)31"`: `P3 sequences` (20)
- `"op15150(vl17767)"`: `P3 sequences` (20)
- `"op15150(vl17767)36"`: `P3 sequences` (20)
- `"op15150(vl17767)38"`: `P3 sequences` (20)
- `"op15150(vl17767)40"`: `P3 sequences` (20)
- `"op15150(vl17767)42"`: `P3 sequences` (20)
- `"op15150(vl17767)44"`: `P3 sequences` (20)
- `"op15150(vl17767)46"`: `P3 sequences` (20)
- `"op15150(vl17871)"`: `P3 sequences` (20)
- `"op15150(vl17871)22"`: `P3 sequences` (20)
- `"op15150(vl17871)23"`: `P3 sequences` (20)
- `"op15150(vl17875)12"`: `P3 sequences` (20)
- `"op15150(vl17875)2"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl17885)"`: `function(normalize)` (20)
- `"op15150(vl17912)"`: `P3 sequences` (20)
- `"op15150(vl18096)17"`: `P3 sequences` (20)
- `"op15150(vl18231)"`: `function(normalize)` (20)
- `"op15150(vl18253)28"`: `P3 sequences` (20)
- `"op15150(vl18277)"`: `P3 sequences` (20)
- `"op15150(vl18277)48"`: `P3 sequences` (20)
- `"op15150(vl18277)50"`: `P3 sequences` (20)
- `"op15150(vl18277)52"`: `P3 sequences` (20)
- `"op15150(vl18277)54"`: `P3 sequences` (20)
- `"op15150(vl18277)56"`: `P3 sequences` (20)
- `"op15150(vl18277)58"`: `P3 sequences` (20)
- `"op15150(vl18294)15"`: `P3 sequences` (20)
- `"op15150(vl18294)18"`: `P3 sequences` (20)
- `"op15150(vl18302)"`: `P3 sequences` (20)
- `"op15150(vl18302)36"`: `P3 sequences` (20)
- `"op15150(vl18302)42"`: `P3 sequences` (20)
- `"op15150(vl19830)"`: `P3 sequences` (20)
- `"op15150(vl19830)27"`: `P3 sequences` (20)
- `"op15150(vl19830)28"`: `P3 sequences` (20)
- `"op15150(vl19830)29"`: `P3 sequences` (20)
- `"op15150(vl19830)30"`: `P3 sequences` (20)
- `"op15150(vl19830)31"`: `P3 sequences` (20)
- `"op15150(vl19830)32"`: `P3 sequences` (20)
- `"op15150(vl19830)33"`: `P3 sequences` (20)
- `"op15150(vl19830)34"`: `P3 sequences` (20)
- `"op15150(vl19830)36"`: `P3 sequences` (20)
- `"op15150(vl20703)"`: `P3 sequences` (20)
- `"op15150(vl20703)18"`: `P3 sequences` (20)
- `"op15150(vl20703)19"`: `P3 sequences` (20)
- `"op15150(vl20703)20"`: `P3 sequences` (20)
- `"op15150(vl20703)21"`: `P3 sequences` (20)
- `"op15150(vl20703)22"`: `P3 sequences` (20)
- `"op15150(vl20703)23"`: `P3 sequences` (20)
- `"op15150(vl20703)24"`: `P3 sequences` (20)
- `"op15150(vl20703)25"`: `P3 sequences` (20)
- `"op15150(vl21163)"`: `P3 sequences` (20)
- `"op15150(vl21743)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl23062)"`: `P3 sequences` (20)
- `"op15150(vl23062)42"`: `P3 sequences` (20)
- `"op15150(vl23062)44"`: `P3 sequences` (20)
- `"op15150(vl23308)"`: `P3 sequences` (20)
- `"op15150(vl23308)24"`: `P3 sequences` (20)
- `"op15150(vl23308)27"`: `P3 sequences` (20)
- `"op15150(vl23939)"`: `P3 sequences` (20)
- `"op15150(vl23939)20"`: `P3 sequences` (20)
- `"op15150(vl23939)26"`: `P3 sequences` (20)
- `"op15150(vl28725)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl28725).i"`: `P3 sequences` (20)
- `"op15150(vl31106)"`: `P3 sequences` (20)
- `"op15150(vl31106)20"`: `P3 sequences` (20)
- `"op15150(vl31106)22"`: `P3 sequences` (20)
- `"op15150(vl31106)24"`: `P3 sequences` (20)
- `"op15150(vl31106)26"`: `P3 sequences` (20)
- `"op15150(vl31106)28"`: `P3 sequences` (20)
- `"op15150(vl31106)30"`: `P3 sequences` (20)
- `"op15150(vl31345)"`: `P3 sequences` (20)
- `"op15150(vl34566)"`: `P3 sequences` (20)
- `"op15150(vl34566)9"`: `P3 sequences` (20)
- `"op15150(vl34958)"`: `function(normalize)` (20)
- `"op15150(vl37700)"`: `P3 sequences` (20)
- `"op15150(vl37945)"`: `P3 sequences` (20)
- `"op15150(vl37945)21"`: `P3 sequences` (20)
- `"op15150(vl38488)"`: `P3 sequences` (20)
- `"op15150(vl38488)25"`: `P3 sequences` (20)
- `"op15150(vl38891)"`: `P3 sequences` (20)
- `"op15150(vl38954)17"`: `P3 sequences` (20)
- `"op15150(vl41195)72"`: `P3 sequences` (20)
- `"op15150(vl42500)"`: `P3 sequences` (20)
- `"op15150(vl45282)"`: `P3 sequences` (20)
- `"op15150(vl45282)16"`: `P3 sequences` (20)
- `"op15150(vl45450)"`: `P3 sequences` (20)
- `"op15150(vl45450)22"`: `P3 sequences` (20)
- `"op15150(vl45450)25"`: `P3 sequences` (20)
- `"op15150(vl45450)26"`: `P3 sequences` (20)
- `"op15150(vl45594)13"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl46259)"`: `P3 sequences` (20)
- `"op15150(vl46688)"`: `P3 sequences` (20)
- `"op15150(vl47049)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl47049)8"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl49291)"`: `P3 sequences` (20)
- `"op15150(vl49291)12"`: `P3 sequences` (20)
- `"op15150(vl49291)15"`: `P3 sequences` (20)
- `"op15150(vl49368)"`: `P3 sequences` (20)
- `"op15150(vl50416)"`: `P3 sequences` (20)
- `"op15150(vl50416)23"`: `P3 sequences` (20)
- `"op15150(vl50416)29"`: `P3 sequences` (20)
- `"op15150(vl50416)32"`: `P3 sequences` (20)
- `"op15150(vl51520)"`: `P3 sequences` (20)
- `"op15150(vl54288)"`: `P3 sequences` (20)
- `"op15150(vl54363)"`: `P3 sequences` (20)
- `"op15150(vl54363)33"`: `P3 sequences` (20)
- `"op15150(vl54363)35"`: `P3 sequences` (20)
- `"op15150(vl54363)37"`: `P3 sequences` (20)
- `"op15150(vl55432)"`: `P3 sequences` (20)
- `"op15150(vl55432)23"`: `P3 sequences` (20)
- `"op15150(vl55432)24"`: `P3 sequences` (20)
- `"op15150(vl55432)25"`: `P3 sequences` (20)
- `"op15150(vl55432)26"`: `P3 sequences` (20)
- `"op15150(vl55432)27"`: `P3 sequences` (20)
- `"op15150(vl55432)28"`: `P3 sequences` (20)
- `"op15150(vl55432)29"`: `P3 sequences` (20)
- `"op15150(vl56147)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl56979)"`: `P3 sequences` (20)
- `"op15150(vl56979)19"`: `P3 sequences` (20)
- `"op15150(vl56979)21"`: `P3 sequences` (20)
- `"op15150(vl56979)23"`: `P3 sequences` (20)
- `"op15150(vl56979)25"`: `P3 sequences` (20)
- `"op15150(vl56979)27"`: `P3 sequences` (20)
- `"op15150(vl56979)29"`: `P3 sequences` (20)
- `"op15150(vl58397)"`: `P3 sequences` (20)
- `"op15150(vl58416)"`: `P3 sequences` (20)
- `"op15150(vl58497)"`: `P3 sequences` (20)
- `"op15150(vl59215)"`: `P3 sequences` (20)
- `"op15150(vl59215)8"`: `P3 sequences` (20)
- `"op15150(vl59215)9"`: `P3 sequences` (20)
- `"op15150(vl60320)"`: `P3 sequences` (20)
- `"op15150(vl60320)32"`: `P3 sequences` (20)
- `"op15150(vl60983)"`: `P3 sequences` (20)
- `"op15150(vl60983)152"`: `P3 sequences` (20)
- `"op15150(vl60983)166"`: `P3 sequences` (20)
- `"op15150(vl60983)169"`: `P3 sequences` (20)
- `"op15150(vl61494)"`: `P3 sequences` (20)
- `"op15150(vl61601)"`: `P3 sequences` (20)
- `"op15150(vl61601)31"`: `P3 sequences` (20)
- `"op15150(vl61601)32"`: `P3 sequences` (20)
- `"op15150(vl61601)34"`: `P3 sequences` (20)
- `"op15150(vl61601)36"`: `P3 sequences` (20)
- `"op15150(vl61601)40"`: `P3 sequences` (20)
- `"op15150(vl61976)49"`: `P3 sequences` (20)
- `"op15150(vl64724)"`: `function(normalize)` (20)
- `"op15150(vl65713)"`: `function(normalize)` (20)
- `"op15150(vl65885)"`: `function(normalize)` (20)
- `"op15150(vl66606)"`: `P3 sequences` (20)
- `"op15150(vl66606)46"`: `P3 sequences` (20)
- `"op15150(vl69845)18"`: `P3 sequences` (20)
- `"op15150(vl69983)53"`: `P3 sequences` (20)
- `"op15150(vl70977)"`: `P3 sequences` (20)
- `"op15150(vl70977)2"`: `P3 sequences` (20)
- `"op15150(vl70990)"`: `P3 sequences` (20)
- `"op15150(vl76885)"`: `P3 sequences` (20)
- `"op15150(vl76885)14"`: `P3 sequences` (20)
- `"op15150(vl78433)17"`: `P3 sequences` (20)
- `"op15150(vl80538)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl82060)16"`: `P3 sequences` (20)
- `"op15150(vl82619)24"`: `P3 sequences` (20)
- `"op15150(vl84136)26"`: `P3 sequences` (20)
- `"op15150(vl84136)29"`: `P3 sequences` (20)
- `"op15150(vl84138)"`: `P3 sequences` (20)
- `"op15150(vl84138)56"`: `P3 sequences` (20)
- `"op15150(vl84138)58"`: `P3 sequences` (20)
- `"op15150(vl85646)"`: `P3 sequences` (20)
- `"op15150(vl85646)41"`: `P3 sequences` (20)
- `"op15150(vl85646)58"`: `P3 sequences` (20)
- `"op15150(vl85646)61"`: `P3 sequences` (20)
- `"op15150(vl86732)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl86732)33"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl86732)47"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl86732)50"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl88132)"`: `P3 sequences` (20)
- `"op15150(vl88132)37"`: `P3 sequences` (20)
- `"op15150(vl88132)51"`: `P3 sequences` (20)
- `"op15150(vl88132)53"`: `P3 sequences` (20)
- `"op15150(vl89899)"`: `function(normalize)` (20)
- `"op15150(vl89899)5"`: `function(normalize)` (20)
- `"op15150(vl89899)6"`: `function(normalize)` (20)
- `"op15150(vl89899)7"`: `function(normalize)` (20)
- `"op15150(vl89899)8"`: `function(normalize)` (20)
- `"op15150(vl90107)15"`: `P3 sequences` (20)
- `"op15150(vl90107)16"`: `P3 sequences` (20)
- `"op15150(vl90107)18"`: `P3 sequences` (20)
- `"op15150(vl90107)19"`: `P3 sequences` (20)
- `"op15150(vl90107)20"`: `P3 sequences` (20)
- `"op15150(vl90787)"`: `P3 sequences` (20)
- `"op15150(vl90787)46"`: `P3 sequences` (20)
- `"op15150(vl90787)57"`: `P3 sequences` (20)
- `"op15150(vl90787)61"`: `P3 sequences` (20)
- `"op15150(vl91382)"`: `P3 sequences` (20)
- `"op15150(vl91382)21"`: `P3 sequences` (20)
- `"op15150(vl91382)22"`: `P3 sequences` (20)
- `"op15150(vl91382)23"`: `P3 sequences` (20)
- `"op15150(vl91382)24"`: `P3 sequences` (20)
- `"op15150(vl91382)25"`: `P3 sequences` (20)
- `"op15150(vl91382)26"`: `P3 sequences` (20)
- `"op15150(vl91950)19"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl93394)"`: `P3 sequences` (20)
- `"op15150(vl93394)37"`: `P3 sequences` (20)
- `"op15150(vl93394)39"`: `P3 sequences` (20)
- `"op15150(vl93394)41"`: `P3 sequences` (20)
- `"op15150(vl93394)43"`: `P3 sequences` (20)
- `"op15150(vl93394)46"`: `P3 sequences` (20)
- `"op15150(vl93394)48"`: `P3 sequences` (20)
- `"op15150(vl96531)"`: `P3 sequences` (20)
- `"op15150(vl96539)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl96539)14"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl96539)16"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15150(vl99408)21"`: `P3 sequences` (20)
- `"op15302(op31723)"`: `function(normalize)` (23)
- `"op15487(op10208)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op15489(op10128)"`: `P3 sequences` (23)
- `"op15489(op16632)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op15580(op15150(vl10336(1))20, 0)"`: `P3 sequences` (20)
- `"op15580(op15150(vl10336(1))3, 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15580(op15150)"`: `P3 sequences` (20)
- `"op15580(op15150)21"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl11031(1))9, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl11042(1))18, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl11550(1)), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl11550(1))6, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl11762(1)), 0)"`: `function(normalize)` (20)
- `"op15580__bennett_measure(op15150(vl11794(1))15, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl13264(1))13, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl14041(1)), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl14041(1))4, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl15216(1)), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl15486(1))6, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl15623(1))31, 3)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl15669(1))34, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl15719(1))28, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl15719(1))29, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl15829(1)), 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15580__bennett_measure(op15150(vl15829(1))1, 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15580__bennett_measure(op15150(vl15829(1))8, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl15996(1))7, 1)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl16875(1))12, 1)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl16875(1))9, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl17871(1))18, 2)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl18294(1))11, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl19830(1))24, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl20703(1))10, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl23062(1))28, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl37700(1)), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl55432(1))16, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl59215(1)), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl60983(1))142, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl61601(1)), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl85646(1))32, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl86732(1))23, 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15580__bennett_measure(op15150(vl88132(1))28, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl89899(1))3, 0)"`: `function(normalize)` (20)
- `"op15580__bennett_measure(op15150(vl91382(1))16, 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op15150(vl91382(1))17, 1)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op73296(op10627(vl11114(1), 0, op31077(0, op10912(op17645(1, indvars.iv35), op17645(1, indvars.iv35)8)))), 0)"`: `function(normalize)` (20)
- `"op15580__bennett_measure(op73296(op12888(op15816(vl15935(1), 0, 0)29, 0, op87963(op35843(op17645(, 1)28, op15150(vl21388(1))))30)), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op73296(op12888(op15816(vl16436(1), 0, 0)25, 0, op87963(op35843(op17645(, 1)24, op15150(vl13732(1))))26)), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op73296(op12888(op15816(vl77939(1), 0, 0)18, 0, op15118(op15150(vl14664(1))))), 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15580__bennett_measure(op73296(op12888(op15816(vl80143(1), 0, 0)137, 0, op15118(op15150(vl95635(1))))), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op73296(op12888(vl13681(%a1, 0, 0), 0, op15118(vl10997(%a0)))), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op73296(op15816(vl10311(1), 0, 0)60), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op73296(op15816(vl13124(1), 0, 0)8), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op73296(op15816(vl17203(1), 0, 0)27), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op73296(op15816(vl17900(1), 0, 0)7), 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15580__bennett_measure(op73296(op15816(vl25598(1), 0, 0)), 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15580__bennett_measure(op73296(op15816(vl33802(1), 0, 0)4), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op73296(op15816(vl43512(1), 0, 0)), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op73296(op15816(vl49010(1), 0, 0)), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op73296(op15816(vl71834(1), 0, 0)8), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op73296(op15816(vl72996(1), 0, 0)), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op73296(op30851(vl34994(1), 0, op87963(op90751(op17645(, 1)25, 0)))), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_measure(op73296(op58134(%a2, 0, op87963(op90751(op17645(, 1), %a1))4)), 0)"`: `P3 sequences` (20)
- `"op15580__bennett_qalloc(0, op15150(vl15493(1)))"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15580__bennett_qalloc(0, op15150(vl31345(1)))"`: `P3 sequences` (20)
- `"op15580__bennett_qalloc(0, op15150(vl37945(1)))"`: `P3 sequences` (20)
- `"op15580__bennett_qalloc(0, op15150(vl70990(1)))"`: `P3 sequences` (20)
- `"op15580__bennett_qborrow(0, op15150(vl37945(1))13)"`: `P3 sequences` (20)
- `"op15648(vl18102, vl13789)"`: `function(normalize)` (23)
- `"op15801(op15150)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op15801(op73296)"`: `function(normalize)` (20)
- `"op16068(op34123)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op16197(op12921)"`: `function(normalize)` (20)
- `"op16202(op10557)"`: `P3 sequences` (23)
- `"op16202(op83627)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op16202(op83627)11"`: `function(normalize)` (23)
- `"op16202(op83627)16"`: `function(normalize)` (23)
- `"op16202(op83627)6"`: `function(normalize)` (23)
- `"op16506__bennett_measure(vl31633__bennett_qalloc(0, 8), op83627(0, op78175(1, i)))"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op16506__bennett_measure(vl31633__bennett_qalloc(0, 8), op83627(0, op78175(1, op83627(op78175))))"`: `P3 sequences` (23)
- `"op16632(op13802)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op16801(op10424)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op17194(op15150)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op17272(op15150)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op17272(op15150)15"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op17272(op15150)57"`: `P3 sequences` (20)
- `"op17272(op15150)58"`: `P3 sequences` (20)
- `"op17272(op73296)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op17272(vl89528)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op17277(op26584, op94372)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op17277(op26584, op94372).i"`: `P3 sequences` (23)
- `"op17688(op15150(vl90107(1))10, op15150(vl18096(1))11, %bb10130, %bb12064)"`: `P3 sequences` (20)
- `"op17911(op15645)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op17911(op94372)"`: `P3 sequences` (23)
- `"op17911(vl14260)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op17911(vl20434)"`: `P3 sequences` (23)
- `"op17911(vl43157)1"`: `function(normalize)` (23)
- `"op17911(vl43157)2"`: `function(normalize)` (23)
- `"op18047(op13802)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op18047(vl11184)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op18047(vl16228)"`: `P3 sequences` (23)
- `"op18321(op73296)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op19549(op17272)"`: `function(normalize)` (20)
- `"op19734(op55710, op55710)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op20359(op79688)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op22110(vl70728)"`: `function(normalize)` (20)
- `"op22639(op14505)"`: `P3 sequences` (20)
- `"op23673(vl19754)"`: `function(normalize)` (23)
- `"op23673(vl25533)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op23673(vl78331)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op23673(vl85679)"`: `function(normalize)` (23)
- `"op24395(op10271, op10271)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op24612(vl13896, vl13896)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op26526(op15150, op15150)"`: `P3 sequences` (20)
- `"op26584(op12665)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op26882(op68297)"`: `function(normalize)` (20)
- `"op27944(vl20713__bennett_qalloc(0, 2), vl25668(%a0, 1), %bb15160, %bb12064)"`: `function(normalize)` (20)
- `"op28599(op81127, vl41281)"`: `P3 sequences` (23)
- `"op28599(op81127, vl52002)"`: `P3 sequences` (23)
- `"op28599(op81127, vl79218)"`: `P3 sequences` (23)
- `"op31179__bennett_qalloc(0, op95908(5, vl49095(%a0, 1)))"`: `function(normalize)` (23)
- `"op37102(vl14972(0, 2, %bb456441, %bb92355), vl11213(%a0, 1), %bb15160, %bb12064)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op37102(vl14972(0, 2, %bb456442, %bb92355), vl37227(%a0, 1), %bb15160, %bb12064)"`: `P3 sequences` (20)
- `"op37725(op11073)"`: `P3 sequences` (20)
- `"op37725(op35843)"`: `function(normalize)` (20)
- `"op37725(op90751)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op37725(op90751).peel"`: `P3 sequences` (20)
- `"op37725(op90751)11"`: `function(normalize)` (20)
- `"op37725(op90751)16"`: `function(normalize)` (20)
- `"op37725(op90751)6"`: `function(normalize)` (20)
- `"op38234(op36786, op87549)"`: `P3 sequences` (23)
- `"op38470(op12466(vl47949(1))3, 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op38470__bennett_measure(op12466(vl11474(1)), 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op38470__bennett_measure(op12466(vl11474(1)), 0).i"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op12466(vl11474(1)), 0).i17"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op12466(vl11474(1))1, 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op38470__bennett_measure(op12466(vl11474(1))1, 0).i"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op12466(vl11474(1))1, 0).i19"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op12466(vl11538(1)), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op12466(vl11538(1))2, 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op12466(vl17738(1))27, 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op12466(vl18413(1)), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op12466(vl18745(1)), 0)"`: `function(normalize)` (23)
- `"op38470__bennett_measure(op12466(vl25219(1))35, 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op12466(vl28701(1))3, 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op12466(vl59467(1)), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op12466(vl59467(1))1, 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op12466(vl59728(1)), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op12466(vl59728(1))3, 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op12466(vl76580(1))30, 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op12466(vl84937(1))3, 0)"`: `function(normalize)` (23)
- `"op38470__bennett_measure(op12466(vl88508(1)), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op12466(vl88508(1))4, 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op12466(vl88556(1))23, 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op38470__bennett_measure(op13802(op11452(vl46614(1), op15516(0, op17327(op78175(1, indvars.iv35), op78175(1, indvars.iv35)8)))), 0)"`: `function(normalize)` (23)
- `"op38470__bennett_measure(op13802(op14795(vl10402(1), 0, 0)7), 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op38470__bennett_measure(op13802(op14795(vl10939(1), 0, 0)), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op13802(op14795(vl12077(1), 0, 0)16), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op13802(op14795(vl13977(1), 0, 0)26), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op13802(op14795(vl15829(1), 0, 0)), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op13802(op14795(vl16063(1), 0, 0)), 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op38470__bennett_measure(op13802(op14795(vl16968(1), 0, 0)23), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op13802(op14795(vl77951(1), 0, 0)44), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op13802(op14795(vl84381(1), 0, 0)), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op13802(op24071(vl12132(1), 0, op15157(op12466(vl37637(1))))), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op13802(op38920(op14795(vl10732(1), 0, 0)18, 0, op15157(op12466(vl13401(1))))), 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op38470__bennett_measure(op13802(op38920(op14795(vl16247(1), 0, 0)22, 0, op15157(op12466(vl87050(1))))), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op13802(op38920(op14795(vl32347(1), 0, 0)46, 0, op70975(op83627(0, op78175(.025, 1))))), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op13802(op38920(op14795(vl41731(1), 0, 0)108, 0, op70975(op83627(0, op78175(1, vl13401(1).0))))), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op13802(op38920(op14795(vl46118(1), 0, 0)41, 0, op70975(op83627(0, op78175(.025, 1))))), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op13802(op38920(op14795(vl63127(1), 0, 0)25, 0, op15157(op12466(vl18201(1))))), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_measure(op13802(op38920(op14795(vl87169(1), 0, 0)30, 0, op15157(op12466(vl51280(1))))), 0)"`: `P3 sequences` (23)
- `"op38470__bennett_qalloc(0, op12466(vl13419(1)))"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op38937(vl16149(0, 2, %bb923551, %bb15508), vl35138(%a0, 1), %bb72598, %bb15693)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op38937(vl16149(0, 2, %bb923552, %bb15508), vl18293(%a0, 1), %bb72598, %bb15693)"`: `P3 sequences` (23)
- `"op38937(vl16149(0, 2, %bb923555, %bb15508), vl18293(%a0, 1), %bb72598, %bb15693)"`: `P3 sequences` (23)
- `"op39068(op36786, vl50347)"`: `P3 sequences` (20)
- `"op39512__bennett_qalloc(0, op11073(2, op16534llvm.objectsize.i64.p0(op16218(vl72083(1), vl12992(%a0, 1)), false, true, true)))"`: `P3 sequences` (20)
- `"op39512__bennett_qalloc(0, op15801(op15150(vl14039(1))4, 8))"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op39512__bennett_qalloc(0, op15801(op15150(vl14039(1))4, 8)).i"`: `P3 sequences` (20)
- `"op39512__bennett_qalloc(0, op15801(op15150(vl72489(1))4, 8))"`: `P3 sequences` (20)
- `"op39512__bennett_qalloc(0, vl11649(%a1, 8)).i"`: `P3 sequences` (20)
- `"op40789(op15150)"`: `P3 sequences` (20)
- `"op43445__bennett_measure(vl12417__bennett_qalloc(0, 2), op23673(1, vl25533(%a0, 1)))"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op43445__bennett_measure(vl12417__bennett_qalloc(0, 2), vl10232(%a0, 1))"`: `P3 sequences` (23)
- `"op43445__bennett_measure(vl12417__bennett_qalloc(0, 2), vl15070(%a0, 1))"`: `P3 sequences` (23)
- `"op43445__bennett_measure(vl12417__bennett_qalloc(0, 2), vl15227(%a0, 1))"`: `function(normalize)` (23)
- `"op43445__bennett_measure(vl12417__bennett_qalloc(0, 2), vl70282(%a0, 1))"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op43445__bennett_measure(vl31633__bennett_qalloc(0, 2), op23673(1, vl85679(%a0, 1)))"`: `function(normalize)` (23)
- `"op43445__bennett_measure(vl31633__bennett_qalloc(0, 2), vl46723(%a0, 1))"`: `P3 sequences` (23)
- `"op43445__bennett_measure(vl31633__bennett_qalloc(0, 2), vl91993(%a0, 1))"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op43445__bennett_measure(vl31633__bennett_qalloc(0, 4), vl14702(%a0, 3))"`: `function(normalize)` (23)
- `"op43445__bennett_measure(vl31633__bennett_qalloc(0, 4), vl52107(%a0, 3))"`: `P3 sequences` (23)
- `"op43445__bennett_measure(vl31633__bennett_qalloc(0, 4), vl62806(%a0, 3))"`: `P3 sequences` (23)
- `"op43445__bennett_measure(vl31633__bennett_qalloc(0, 4), vl88532(%a0, 3))"`: `P3 sequences` (23)
- `"op43445__bennett_measure(vl31633__bennett_qalloc(0, 4), vl92053(%a0, 3))"`: `P3 sequences` (23)
- `"op43445__bennett_measure(vl72598__bennett_qalloc(0, 4), vl10383(%a0, 3))"`: `P3 sequences` (23)
- `"op43445__bennett_measure(vl72598__bennett_qalloc(0, 4), vl16038(%a0, 3))"`: `function(normalize)` (23)
- `"op43445__bennett_measure(vl72598__bennett_qalloc(0, 4), vl73209(%a0, 3))"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op43445__bennett_measure(vl72598__bennett_qalloc(0, 4), vl86131(%a0, 3))"`: `P3 sequences` (23)
- `"op47246(op13802)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op49047(op10647)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op51459__bennett_qalloc(0, op10557(2, op21385llvm.objectsize.i64.p0(op11256(op14795(vl17277(1), 0, 0), vl82323(%a0, 1)), false, true, true)))"`: `P3 sequences` (23)
- `"op51459__bennett_qalloc(0, op10557(2, op21385llvm.objectsize.i64.p0(op11256(op14795(vl41917(1), 0, 0), vl82323(%a0, 1)), false, true, true)))"`: `P3 sequences` (23)
- `"op51459__bennett_qalloc(0, op10557(op21385llvm.objectsize.i64.p0(op11256(op14795(vl15153(1), 0, 0), vl42880(%a0, 1)), false, true, true), 2))"`: `P3 sequences` (23)
- `"op51459__bennett_qalloc(0, op54150(op12466(vl10784(1))4, 8))"`: `P3 sequences` (23)
- `"op51459__bennett_qalloc(0, op54150(op12466(vl68533(1))4, 8))"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op51459__bennett_qalloc(0, op54150(op12466(vl68533(1))4, 8)).i"`: `P3 sequences` (23)
- `"op51459__bennett_qalloc(0, vl40606(%a1, 8))"`: `P3 sequences` (23)
- `"op51459__bennett_qalloc(0, vl81127(3, 8))"`: `P3 sequences` (23)
- `"op54150(op12466)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op54150(op12466).i"`: `P3 sequences` (23)
- `"op54150(op13802)"`: `function(normalize)` (23)
- `"op55710__bennett_qalloc(0, op14290(1, vl32589(%a0, 4)))"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op55710__bennett_qborrow(0, op14290(1, vl32589(%a0, 4)))"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op56160(op44129)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op57091__bennett_measure(%a0, 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op57091__bennett_qalloc(0, 3)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op57091__bennett_qalloc(1, 2)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op57091__bennett_qborrow(2, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op58038(op26584)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op58630(op10533)"`: `function(normalize)` (20)
- `"op62161(op90542)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op64863(op12039)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op65501__bennett_measure(op15150(vl12739(1))14, op15150(vl15129(1))15)"`: `P3 sequences` (20)
- `"op67044(op13609)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op67870(op32900, op64863)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op67870(op32900, op64863).i"`: `P3 sequences` (20)
- `"op68297(op10533)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297(vl18195(0, 2), 0)"`: `P3 sequences` (20)
- `"op68297(vl20713(0, 2), 0)"`: `function(normalize)` (20)
- `"op68297(vl20713)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl11202__bennett_qalloc(0, 1), 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl15001__bennett_qalloc(0, 1), 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl15001__bennett_qalloc(0, 2), 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl15001__bennett_qalloc(0, 2), 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl15160__bennett_qalloc(0, 1), 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl15160__bennett_qalloc(0, 1), 0)10"`: `function(normalize)` (20)
- `"op68297__bennett_measure(vl15160__bennett_qalloc(0, 1), 0)11"`: `function(normalize)` (20)
- `"op68297__bennett_measure(vl15160__bennett_qalloc(0, 1), 0)12"`: `function(normalize)` (20)
- `"op68297__bennett_measure(vl15160__bennett_qalloc(0, 1), 0)13"`: `function(normalize)` (20)
- `"op68297__bennett_measure(vl15160__bennett_qalloc(0, 1), 0)2"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl15160__bennett_qalloc(0, 1), 0)7"`: `function(normalize)` (20)
- `"op68297__bennett_measure(vl15160__bennett_qalloc(0, 1), 0)8"`: `function(normalize)` (20)
- `"op68297__bennett_measure(vl15160__bennett_qalloc(0, 1), 0)9"`: `function(normalize)` (20)
- `"op68297__bennett_measure(vl15160__bennett_qalloc(0, 2), 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl15160__bennett_qalloc(0, 2), 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl15160__bennett_qalloc(0, 4), 3)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl20713__bennett_qalloc(0, 1), 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl20713__bennett_qalloc(0, 1), 0).1"`: `P3 sequences` (20)
- `"op68297__bennett_measure(vl20713__bennett_qalloc(0, 1), 0).2"`: `P3 sequences` (20)
- `"op68297__bennett_measure(vl20713__bennett_qalloc(0, 1), 0)1"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl20713__bennett_qalloc(0, 1), 0)2"`: `function(normalize)` (20)
- `"op68297__bennett_measure(vl20713__bennett_qalloc(0, 1), 0)3"`: `function(normalize)` (20)
- `"op68297__bennett_measure(vl20713__bennett_qalloc(0, 2), 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl20713__bennett_qalloc(0, 2), 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl20713__bennett_qalloc(0, 4), 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl20713__bennett_qalloc(0, 4), 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl20713__bennett_qalloc(0, 4), 2)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl20713__bennett_qalloc(0, 4), 3)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op68297__bennett_measure(vl20713__bennett_qalloc(0, 8), 0)"`: `function(normalize)` (20)
- `"op68297__bennett_measure(vl20713__bennett_qalloc(0, 8), 1)"`: `function(normalize)` (20)
- `"op68297__bennett_measure(vl20713__bennett_qalloc(0, 8), 2)"`: `function(normalize)` (20)
- `"op68297__bennett_measure(vl20713__bennett_qalloc(0, 8), 3)"`: `function(normalize)` (20)
- `"op68297__bennett_measure(vl40092__bennett_qalloc(0, 1), 0)"`: `function(normalize)` (20)
- `"op68297__bennett_measure(vl69719__bennett_qalloc(0, 1), 0)"`: `function(normalize)` (20)
- `"op68297__bennett_measure(vl81504__bennett_qalloc(0, 1), 0)"`: `P3 sequences` (20)
- `"op68909(op12080)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op73296(op10627)"`: `function(normalize)` (20)
- `"op73296(op10627)11"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op10627)12"`: `P3 sequences` (20)
- `"op73296(op10627)15"`: `function(normalize)` (20)
- `"op73296(op10627)18"`: `function(normalize)` (20)
- `"op73296(op11308)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op11308)1"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op11308)2"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op12888)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op12888).i"`: `P3 sequences` (20)
- `"op73296(op12888)163"`: `P3 sequences` (20)
- `"op73296(op12888)173"`: `P3 sequences` (20)
- `"op73296(op12888)2"`: `P3 sequences` (20)
- `"op73296(op12888)44"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op12888)48"`: `P3 sequences` (20)
- `"op73296(op12888)54"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op12888)55"`: `P3 sequences` (20)
- `"op73296(op12888)59"`: `P3 sequences` (20)
- `"op73296(op12888)67"`: `P3 sequences` (20)
- `"op73296(op13863)65"`: `P3 sequences` (20)
- `"op73296(op13863)67"`: `P3 sequences` (20)
- `"op73296(op13863)71"`: `P3 sequences` (20)
- `"op73296(op15816)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op15816).1"`: `P3 sequences` (20)
- `"op73296(op15816).2"`: `P3 sequences` (20)
- `"op73296(op15816)10"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op15816)11"`: `P3 sequences` (20)
- `"op73296(op15816)12"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op15816)13"`: `P3 sequences` (20)
- `"op73296(op15816)17"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op15816)18"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op15816)19"`: `P3 sequences` (20)
- `"op73296(op15816)20"`: `P3 sequences` (20)
- `"op73296(op15816)21"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op15816)37"`: `P3 sequences` (20)
- `"op73296(op15816)39"`: `P3 sequences` (20)
- `"op73296(op15816)4"`: `function(normalize)` (20)
- `"op73296(op15816)40"`: `P3 sequences` (20)
- `"op73296(op15816)41"`: `P3 sequences` (20)
- `"op73296(op15816)45"`: `P3 sequences` (20)
- `"op73296(op15816)48"`: `P3 sequences` (20)
- `"op73296(op15816)5"`: `P3 sequences` (20)
- `"op73296(op15816)51"`: `P3 sequences` (20)
- `"op73296(op15816)6"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op15816)7"`: `P3 sequences` (20)
- `"op73296(op15816)71"`: `P3 sequences` (20)
- `"op73296(op15816)74"`: `P3 sequences` (20)
- `"op73296(op15816)8"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op15816)9"`: `P3 sequences` (20)
- `"op73296(op16218)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op16218)3"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op16218)5"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op16369)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op16382)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op30851)"`: `P3 sequences` (20)
- `"op73296(op30851)34"`: `P3 sequences` (20)
- `"op73296(op30851)38"`: `P3 sequences` (20)
- `"op73296(op41554)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op58134)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op58134).i"`: `P3 sequences` (20)
- `"op73296(op58134)5"`: `P3 sequences` (20)
- `"op73296(op60958)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op60958)12"`: `P3 sequences` (20)
- `"op73296(op60958)4"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(op70895)"`: `P3 sequences` (20)
- `"op73296(op73303)"`: `P3 sequences` (20)
- `"op73296(vl11121)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(vl11121)1"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(vl11308)"`: `P3 sequences` (20)
- `"op73296(vl13681)"`: `P3 sequences` (20)
- `"op73296(vl13823)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(vl13897)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(vl14194)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(vl15262)"`: `P3 sequences` (20)
- `"op73296(vl16259)"`: `P3 sequences` (20)
- `"op73296(vl16430)"`: `P3 sequences` (20)
- `"op73296(vl17472)"`: `P3 sequences` (20)
- `"op73296(vl18330)"`: `P3 sequences` (20)
- `"op73296(vl18434)"`: `P3 sequences` (20)
- `"op73296(vl23019)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(vl31401)"`: `function(normalize)` (20)
- `"op73296(vl34898)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(vl37946)"`: `P3 sequences` (20)
- `"op73296(vl37946)1"`: `P3 sequences` (20)
- `"op73296(vl42191)"`: `function(normalize)` (20)
- `"op73296(vl43482)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(vl53266)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(vl67387)"`: `function(normalize)` (20)
- `"op73296(vl75217)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op73296(vl76465)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op75265(vl62332)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op75266(op18103)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op75266(op78373)"`: `P3 sequences` (20)
- `"op75266(op78373)48"`: `P3 sequences` (20)
- `"op76978(vl89528, vl89528)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op78373(op73296)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op78373(op73296)30"`: `P3 sequences` (20)
- `"op79688(op17911)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op82200(vl31633__bennett_qalloc(0, 2), vl46723(%a0, 1), %bb72598, %bb15693)"`: `function(normalize)` (23)
- `"op82780(vl11679, vl16222)"`: `function(normalize)` (20)
- `"op83627(op78175)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op83627(op78175).i"`: `P3 sequences` (23)
- `"op83627(op78175).i5"`: `P3 sequences` (23)
- `"op83627(op78175)1"`: `function(normalize)` (23)
- `"op83627(op78175)10"`: `P3 sequences` (23)
- `"op83627(op78175)11"`: `P3 sequences` (23)
- `"op83627(op78175)12"`: `P3 sequences` (23)
- `"op83627(op78175)13"`: `P3 sequences` (23)
- `"op83627(op78175)14"`: `P3 sequences` (23)
- `"op83627(op78175)17"`: `P3 sequences` (23)
- `"op83627(op78175)3"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op83627(op78175)5"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op83627(op78175)6"`: `P3 sequences` (23)
- `"op83627(op78175)7"`: `P3 sequences` (23)
- `"op83627(op78175)8"`: `P3 sequences` (23)
- `"op85166(op11958)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op85166(op11958)1"`: `function(normalize)` (23)
- `"op85166(op11958)2"`: `function(normalize)` (23)
- `"op85166(op11958)3"`: `function(normalize)` (23)
- `"op85166(vl26594)"`: `P3 sequences` (23)
- `"op85785(op12466)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op85785(op12466)15"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op85785(op13802)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op85785(vl13896)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op86228(op75094, vl81200)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op86564(op11395)"`: `function(normalize)` (20)
- `"op87711__bennett_measure(vl15001__bennett_qalloc(0, 2), op14991(1, vl66779(%a0, 1)))"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op87711__bennett_measure(vl15001__bennett_qalloc(0, 2), vl27043(%a0, 1))"`: `function(normalize)` (20)
- `"op87711__bennett_measure(vl15001__bennett_qalloc(0, 2), vl29927(%a0, 1))"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op87711__bennett_measure(vl15001__bennett_qalloc(0, 2), vl55795(%a0, 1))"`: `P3 sequences` (20)
- `"op87711__bennett_measure(vl15001__bennett_qalloc(0, 2), vl61348(%a0, 1))"`: `P3 sequences` (20)
- `"op87711__bennett_measure(vl15160__bennett_qalloc(0, 4), vl13568(%a0, 3))"`: `P3 sequences` (20)
- `"op87711__bennett_measure(vl15160__bennett_qalloc(0, 4), vl16375(%a0, 3))"`: `P3 sequences` (20)
- `"op87711__bennett_measure(vl15160__bennett_qalloc(0, 4), vl16567(%a0, 3))"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op87711__bennett_measure(vl15160__bennett_qalloc(0, 4), vl55654(%a0, 3))"`: `function(normalize)` (20)
- `"op87711__bennett_measure(vl20713__bennett_qalloc(0, 2), op14991(1, vl29895(%a0, 1)))"`: `function(normalize)` (20)
- `"op87711__bennett_measure(vl20713__bennett_qalloc(0, 2), vl65636(%a0, 1))"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op87711__bennett_measure(vl20713__bennett_qalloc(0, 4), vl48963(%a0, 3))"`: `function(normalize)` (20)
- `"op87711__bennett_measure(vl20713__bennett_qalloc(0, 4), vl98633(%a0, 3))"`: `P3 sequences` (20)
- `"op90329__bennett_measure(%a0, vl20225(%a1, 3))"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op90329__bennett_measure(%a0, vl56951(%a1, 3))"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op90751(op17645)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op90751(op17645)1"`: `function(normalize)` (20)
- `"op90751(op17645)11"`: `P3 sequences` (20)
- `"op90751(op17645)3"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op90751(op17645)5"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op90751(op17645)7"`: `P3 sequences` (20)
- `"op91455__bennett_measure(%a0, 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op91455__bennett_qalloc(0, 3)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op91455__bennett_qalloc(1, 2)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op91455__bennett_qborrow(2, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op91509(vl26482)"`: `P3 sequences` (20)
- `"op91509(vl44847)"`: `function(normalize)` (20)
- `"op91509(vl94308)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"op91799(op15150)"`: `P3 sequences` (20)
- `"op93118(op22442, vl96711)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"op95908(vl49095)"`: `function(normalize)` (23)
- `"op95925(vl88346, vl88346, vl88346)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"stack-protector-buffer-size"="8"`: `dfsan` (18,20,23)
- `"target-cpu"="x86-64"`: `dfsan` (18,20,23)
- `"target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87"`: `dfsan` (18,20,23)
- `"tune-cpu"="generic"`: `dfsan` (18,20,23)
- `"vl10014(1)"`: `P3 sequences` (23)
- `"vl10016(1)"`: `P3 sequences` (23)
- `"vl10131(1)"`: `P3 sequences` (23), `function(normalize)` (20,23)
- `"vl10144(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl10181(1)"`: `P3 sequences` (20)
- `"vl10232(%a0, 1)"`: `P3 sequences` (23)
- `"vl10237(1)"`: `P3 sequences` (20)
- `"vl10249(%a0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl10271__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl10271__bennett_qborrow(1, 1)"`: `P3 sequences` (23)
- `"vl10284(1)"`: `function(normalize)` (20)
- `"vl10311(1)"`: `P3 sequences` (20)
- `"vl10383(%a0, 3)"`: `P3 sequences` (23)
- `"vl10402(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl10530(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl10533__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl10604__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl10604__bennett_qalloc(0, 2)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl10693(1)"`: `P3 sequences` (20)
- `"vl10732(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl10848(1)"`: `P3 sequences` (23)
- `"vl10856__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl10856__bennett_qalloc(0, 4)"`: `P3 sequences` (20)
- `"vl11026(%a0)"`: `P3 sequences` (23)
- `"vl11054(1)"`: `P3 sequences` (23)
- `"vl11060(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl11109(1)"`: `function(normalize)` (23)
- `"vl11114(1)"`: `function(normalize)` (20)
- `"vl11184(%a1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl11194__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl11194__bennett_qalloc(0, 1)14"`: `P3 sequences` (23)
- `"vl11198(1)"`: `function(normalize)` (20)
- `"vl11202__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl11202__bennett_qalloc(0, 2)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl11202__bennett_qalloc(0, 4)"`: `P3 sequences` (20)
- `"vl11203(%a0, 3)"`: `P3 sequences` (20)
- `"vl11210(1)"`: `P3 sequences` (23)
- `"vl11213(%a0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl11245(1)"`: `P3 sequences` (23)
- `"vl11306(1)"`: `function(normalize)` (20)
- `"vl11432(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl11468(@hglob)"`: `P3 sequences` (23)
- `"vl11477(1)"`: `P3 sequences` (23)
- `"vl11483(%a0)"`: `P3 sequences` (23)
- `"vl11555(1)"`: `function(normalize)` (20)
- `"vl11605(%a2)"`: `P3 sequences` (20)
- `"vl11614(1)"`: `P3 sequences` (23)
- `"vl11679(%a0, 1)"`: `P3 sequences` (20)
- `"vl11706__bennett_qborrow(1, 1)"`: `P3 sequences` (23)
- `"vl11713(%a0, 1)"`: `function(normalize)` (20)
- `"vl11855(1)"`: `P3 sequences` (23)
- `"vl11867(1)"`: `P3 sequences` (23)
- `"vl11882__bennett_qalloc(0, 1)"`: `P3 sequences` (20)
- `"vl11980(1)"`: `P3 sequences` (23)
- `"vl12040(%a0)"`: `function(normalize)` (20)
- `"vl12040(%a2)"`: `P3 sequences` (20)
- `"vl12065__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl12077(1)"`: `P3 sequences` (23)
- `"vl12097(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl12132(1)"`: `P3 sequences` (23)
- `"vl12264(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl12310(%a0, 4)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl12364(1)"`: `P3 sequences` (23)
- `"vl12380(1)"`: `P3 sequences` (23)
- `"vl12390(%a0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl12417__bennett_measure(%a0, 0)"`: `P3 sequences` (23)
- `"vl12417__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl12417__bennett_qalloc(0, 16)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl12417__bennett_qalloc(0, 2)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl12417__bennett_qalloc(0, 8)"`: `function(normalize)` (23)
- `"vl12493(1)"`: `function(normalize)` (20)
- `"vl12550(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl12678__bennett_qalloc(0, 1)"`: `P3 sequences` (20)
- `"vl12678__bennett_qborrow(1, 1)"`: `P3 sequences` (20)
- `"vl12793(1)"`: `P3 sequences` (20)
- `"vl12840__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl12840__bennett_qalloc(0, 8)"`: `P3 sequences` (20)
- `"vl12961(%a0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl12961(@hglob)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl12961(@hreg)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl12971(1)"`: `P3 sequences` (20)
- `"vl13087(1).0"`: `P3 sequences` (20)
- `"vl13123(%a0, 8)"`: `P3 sequences` (23)
- `"vl13124(1)"`: `P3 sequences` (20)
- `"vl13125__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl13147(%a0, 8)"`: `P3 sequences` (20)
- `"vl13160(1)"`: `P3 sequences` (20)
- `"vl13174(1)"`: `function(normalize)` (23)
- `"vl13252(1)"`: `P3 sequences` (20)
- `"vl13287__bennett_qborrow(1, 1)"`: `P3 sequences` (23)
- `"vl13310(1)"`: `P3 sequences` (23)
- `"vl13425(1)"`: `P3 sequences` (23)
- `"vl13476(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl13495(1)"`: `P3 sequences` (23)
- `"vl13563__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl13563__bennett_qalloc(0, 2)"`: `P3 sequences` (20)
- `"vl13568(%a0, 3)"`: `P3 sequences` (20)
- `"vl13629(1)"`: `function(normalize)` (23)
- `"vl13644(1)"`: `P3 sequences` (20)
- `"vl13672(1)"`: `P3 sequences` (23)
- `"vl13757(1)"`: `P3 sequences` (23)
- `"vl13896(%a0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl13896(@hreg)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl13975(1)"`: `function(normalize)` (23)
- `"vl13977(1)"`: `P3 sequences` (23)
- `"vl13989(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl14123(1)"`: `P3 sequences` (23)
- `"vl14238(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl14247(1)"`: `P3 sequences` (23)
- `"vl14384(1)"`: `P3 sequences` (20)
- `"vl14516(%a0, 3)"`: `P3 sequences` (20)
- `"vl14592(%a0)"`: `P3 sequences` (20)
- `"vl14592(@hglob)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl14628__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl14662__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl14662__bennett_qalloc(0, 16)"`: `P3 sequences` (20)
- `"vl14662__bennett_qalloc(0, 2)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl14662__bennett_qalloc(1, 4)"`: `P3 sequences` (20)
- `"vl14662llvm.fmuladd.f64(1.000000e+01, 1.000000e-01, -1.000000e+00)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl14702(%a0, 3)"`: `function(normalize)` (23)
- `"vl14860(%a0, 8)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl14917(%a1, 3)"`: `function(normalize)` (23)
- `"vl14969__bennett_qalloc(0, 1)"`: `P3 sequences` (20)
- `"vl14972(0, 2, %bb456441, %bb92355)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl14972(0, 2, %bb456442, %bb92355)"`: `P3 sequences` (20)
- `"vl14986(%a0, 4)"`: `P3 sequences` (20)
- `"vl15001__bennett_measure(%a0, 0).i"`: `P3 sequences` (20)
- `"vl15001__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl15001__bennett_qalloc(0, 16)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl15001__bennett_qalloc(0, 2)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl15001__bennett_qalloc(0, 8)"`: `function(normalize)` (20)
- `"vl15033(%a1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl15035__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl15070(%a0, 1)"`: `P3 sequences` (23)
- `"vl15113(%a0, 1)"`: `function(normalize)` (20)
- `"vl15160__bennett_measure(%a0, 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl15160__bennett_measure(%a0, 0).i"`: `P3 sequences` (20)
- `"vl15160__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl15160__bennett_qalloc(0, 2)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl15160__bennett_qalloc(0, 4)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl15160__bennett_qborrow(1, 4)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl15219(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl15227(%a0, 1)"`: `function(normalize)` (23)
- `"vl15301(%a0, 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl15323__bennett_qborrow(1, 1)"`: `P3 sequences` (20)
- `"vl15381(1)"`: `P3 sequences` (20)
- `"vl15399(1)"`: `function(normalize)` (23)
- `"vl15449(1)"`: `P3 sequences` (23)
- `"vl15486(1)"`: `P3 sequences` (20)
- `"vl15570(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl15580__bennett_qborrow(1, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl15584(%a0)"`: `P3 sequences` (20)
- `"vl15634(1)"`: `P3 sequences` (20)
- `"vl15681(1)"`: `P3 sequences` (23)
- `"vl15801(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl15808__bennett_qalloc(0, 1)"`: `P3 sequences` (20)
- `"vl15828(1)"`: `P3 sequences` (20)
- `"vl15841(1)"`: `P3 sequences` (23)
- `"vl15853(1)"`: `function(normalize)` (23)
- `"vl15929(0, 2, %bb13637, %bb92355)"`: `P3 sequences` (20)
- `"vl15935(1)"`: `P3 sequences` (20)
- `"vl15963__bennett_qalloc(0, 1)"`: `P3 sequences` (20)
- `"vl15976(1)"`: `P3 sequences` (23)
- `"vl15989(1)"`: `P3 sequences` (23)
- `"vl16038(%a0, 3)"`: `function(normalize)` (23)
- `"vl16102(1)"`: `P3 sequences` (20)
- `"vl16149(0, 2, %bb923551, %bb15508)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl16149(0, 2, %bb923552, %bb15508)"`: `P3 sequences` (23)
- `"vl16149(0, 2, %bb923555, %bb15508)"`: `P3 sequences` (23)
- `"vl16228(%a0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl16228(%a1)"`: `P3 sequences` (23)
- `"vl16247(1)"`: `P3 sequences` (23)
- `"vl16296(%a0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl16296(1)"`: `P3 sequences` (20)
- `"vl16352(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl16375(%a0, 3)"`: `P3 sequences` (20)
- `"vl16379(1)"`: `function(normalize)` (23)
- `"vl16391(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl16396(1)"`: `P3 sequences` (23)
- `"vl16428(%a0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl16428(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl16432(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl16436(1)"`: `P3 sequences` (20)
- `"vl16446(%a0, 3)"`: `P3 sequences` (23)
- `"vl16457(1)"`: `function(normalize)` (20)
- `"vl16486(1)"`: `P3 sequences` (23)
- `"vl16488(%a0)"`: `function(normalize)` (20)
- `"vl16498(1)"`: `P3 sequences` (23)
- `"vl16567(%a0, 3)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl16597(1)"`: `function(normalize)` (20)
- `"vl16801__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl16826(1)"`: `function(normalize)` (23)
- `"vl16849(1)"`: `function(normalize)` (23)
- `"vl16879(1)"`: `function(normalize)` (23)
- `"vl16927__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl16968(1)"`: `P3 sequences` (23)
- `"vl17031(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl17048(%a0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl17066(%a0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl17116(1)"`: `P3 sequences` (23)
- `"vl17145(1)"`: `function(normalize)` (23)
- `"vl17203(1)"`: `P3 sequences` (20)
- `"vl17297(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl17297(1).i"`: `P3 sequences` (23)
- `"vl17328(1)"`: `P3 sequences` (23)
- `"vl17386(1)"`: `P3 sequences` (23)
- `"vl17450(%a0)"`: `function(normalize)` (20)
- `"vl17588(1).i"`: `P3 sequences` (20)
- `"vl17681(1)"`: `P3 sequences` (23)
- `"vl17709(1)"`: `function(normalize)` (20)
- `"vl17776(%a0, 8)"`: `P3 sequences` (20)
- `"vl17821(1)"`: `P3 sequences` (23)
- `"vl17885(1)"`: `function(normalize)` (20)
- `"vl17900(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl17902(%a0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl17912(1)"`: `P3 sequences` (20)
- `"vl17966(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl18089(%a0)"`: `P3 sequences` (23)
- `"vl18089(@hglob)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl18195(0, 2)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl18195__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl18195__bennett_qalloc(0, 2)"`: `P3 sequences` (20)
- `"vl18195__bennett_qalloc(0, 4)"`: `P3 sequences` (20)
- `"vl18195__bennett_qalloc(0, 8)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl18231(1)"`: `function(normalize)` (20)
- `"vl18293(%a0, 1)"`: `P3 sequences` (23)
- `"vl18304(%a1, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl18320(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl18425(1)"`: `P3 sequences` (20)
- `"vl18870(1)"`: `P3 sequences` (23)
- `"vl19754(%a0, 1)"`: `P3 sequences` (23)
- `"vl19969(%a3)"`: `P3 sequences` (20)
- `"vl20163(%a0)"`: `P3 sequences` (20)
- `"vl20225(%a1, 3)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl20473(1)"`: `P3 sequences` (23)
- `"vl20713(0, 2)"`: `function(normalize)` (20)
- `"vl20713__bennett_measure(%a0, %a1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl20713__bennett_measure(%a0, %a1).i"`: `P3 sequences` (20)
- `"vl20713__bennett_measure(%a0, 0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl20713__bennett_qalloc(0, %a0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl20713__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl20713__bennett_qalloc(0, 2)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl20713__bennett_qalloc(0, 4)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl20713__bennett_qalloc(0, 8)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl20713__bennett_qalloc(1, 4)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl20713alloc_helper()"`: `function(normalize)` (20)
- `"vl20713alloc_helper(2)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl20828(1)"`: `function(normalize)` (23)
- `"vl21044(1)"`: `P3 sequences` (23)
- `"vl21168__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl21385__bennett_qborrow(1, 1)"`: `P3 sequences` (23)
- `"vl21743(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl24069__bennett_qalloc(0, 1)"`: `P3 sequences` (20)
- `"vl24259__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl24680(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl24844(%a0, 4)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl25024(%a0, 1)"`: `P3 sequences` (20)
- `"vl25651(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl25668(%a0, 1)"`: `function(normalize)` (20)
- `"vl25680(%a0, 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl26259(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl26594__bennett_measure(%a1, 1)"`: `P3 sequences` (23)
- `"vl26594__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl26594__bennett_qalloc(0, 3)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl26594__bennett_qalloc(0, 8)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl26594__bennett_qborrow(1, 1)"`: `function(normalize)` (23)
- `"vl26606(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl27043(%a0, 1)"`: `function(normalize)` (20)
- `"vl28578(%a0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl28578(@hglob)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl28578(@hq)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl28701(1)"`: `P3 sequences` (23)
- `"vl28725(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl28725(1).i"`: `P3 sequences` (20)
- `"vl29782(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl29920(1)"`: `P3 sequences` (23)
- `"vl29927(%a0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl31166(1)"`: `P3 sequences` (23)
- `"vl31179__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl31179__bennett_qalloc(0, 1)13"`: `P3 sequences` (23)
- `"vl31179__bennett_qborrow(1, 1)"`: `P3 sequences` (23)
- `"vl31504__bennett_qalloc(0, 1)"`: `P3 sequences` (20)
- `"vl31633(0, 2)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl31633__bennett_measure(%a0, %a1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl31633__bennett_measure(%a0, %a1).i"`: `P3 sequences` (23)
- `"vl31633__bennett_measure(%a0, 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl31633__bennett_qalloc(0, %a0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl31633__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl31633__bennett_qalloc(0, 2)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl31633__bennett_qalloc(0, 4)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl31633__bennett_qalloc(0, 8)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl31633__bennett_qalloc(1, 4)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl31633alloc_helper()"`: `function(normalize)` (23)
- `"vl31633alloc_helper(2)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl32347(1)"`: `P3 sequences` (23)
- `"vl33236__bennett_qalloc(0, 1)"`: `P3 sequences` (20)
- `"vl33730(1)"`: `function(normalize)` (23)
- `"vl33802(1)"`: `P3 sequences` (20)
- `"vl33989(1)"`: `P3 sequences` (20)
- `"vl34058(%a0, 3)"`: `P3 sequences` (20)
- `"vl34578(1)"`: `P3 sequences` (20)
- `"vl34595(%a1, 3)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl34720__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl34720__bennett_qalloc(0, 2)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl34720llvm.fmuladd.f64(1.000000e+01, 1.000000e-01, -1.000000e+00)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl34958(1)"`: `function(normalize)` (20)
- `"vl34994(1)"`: `P3 sequences` (20)
- `"vl35138(%a0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl35249llvm.fmuladd.f64(1.000000e+01, 1.000000e-01, -1.000000e+00)"`: `P3 sequences` (20)
- `"vl35397(%a0, 4)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl35427(1)"`: `function(normalize)` (20)
- `"vl36180(%a0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl36530(%a1, 1)"`: `function(normalize)` (20)
- `"vl36786(1, 8, 40, 2, 9, 4, 17)"`: `function(normalize)` (20)
- `"vl37227(%a0, 1)"`: `P3 sequences` (20)
- `"vl37564(0, 2)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl37564__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl37564__bennett_qalloc(0, 8)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl37591(1)"`: `function(normalize)` (23)
- `"vl37617(1)"`: `P3 sequences` (20)
- `"vl39573(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl39845(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl40092__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl40092__bennett_qalloc(0, 2)"`: `P3 sequences` (20)
- `"vl40116__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl40545__bennett_qalloc(0, 1)"`: `P3 sequences` (23)
- `"vl40606(%a1, 8)"`: `P3 sequences` (23)
- `"vl40820(1)"`: `function(normalize)` (20)
- `"vl41497(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl41731(1)"`: `P3 sequences` (23)
- `"vl41939(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl42431(1)"`: `P3 sequences` (20)
- `"vl42527(%a0)"`: `function(normalize)` (23)
- `"vl43888__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl45344(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl46118(1)"`: `P3 sequences` (23)
- `"vl46140__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl46541(1)"`: `P3 sequences` (23)
- `"vl46614(1)"`: `function(normalize)` (23)
- `"vl46688(1)"`: `P3 sequences` (20)
- `"vl46723(%a0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl47306__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl48963(%a0, 3)"`: `function(normalize)` (20)
- `"vl49268__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl49382(1)"`: `P3 sequences` (20)
- `"vl49911(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl50010__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl50117(%a0, 1)"`: `P3 sequences` (23)
- `"vl52107(%a0, 3)"`: `P3 sequences` (23)
- `"vl53322__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl53563__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl53563__bennett_qalloc(0, 2)"`: `P3 sequences` (23)
- `"vl53917(1)"`: `P3 sequences` (20)
- `"vl54935__bennett_qborrow(1, 1)"`: `P3 sequences` (20)
- `"vl55087__bennett_measure(%a0, 0)"`: `P3 sequences` (23)
- `"vl55087__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl55087__bennett_qalloc(0, 2)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl55087__bennett_qalloc(0, 8)"`: `function(normalize)` (23)
- `"vl55654(%a0, 3)"`: `function(normalize)` (20)
- `"vl55710__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl55710__bennett_qalloc(0, 8)"`: `P3 sequences` (20)
- `"vl55795(%a0, 1)"`: `P3 sequences` (20)
- `"vl56047__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl56047__bennett_qalloc(0, 1)15"`: `P3 sequences` (23)
- `"vl56047__bennett_qborrow(1, 1)"`: `P3 sequences` (23)
- `"vl56147(1).0.copyload"`: `P3 sequences` (20)
- `"vl56951(%a1, 3)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl58038__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl58134(%a0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl58398(1)"`: `P3 sequences` (20)
- `"vl58446(1)"`: `P3 sequences` (20)
- `"vl59164(1)"`: `P3 sequences` (20)
- `"vl59442(1)"`: `P3 sequences` (20)
- `"vl60318(1)"`: `P3 sequences` (23)
- `"vl60952(%a0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl60952(%a0).i"`: `P3 sequences` (23)
- `"vl61348(%a0, 1)"`: `P3 sequences` (20)
- `"vl61373(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl62156__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl62156__bennett_qalloc(0, 2)"`: `P3 sequences` (20)
- `"vl62643(1)"`: `P3 sequences` (20)
- `"vl62806(%a0, 3)"`: `P3 sequences` (23)
- `"vl63127(1)"`: `P3 sequences` (23)
- `"vl63224(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl64168(%a1, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl64724(1)"`: `function(normalize)` (20)
- `"vl65425(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl65636(%a0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl65636(%a0, 3)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl65713(1)"`: `function(normalize)` (20)
- `"vl65885(1)"`: `function(normalize)` (20)
- `"vl65922(1)"`: `P3 sequences` (23)
- `"vl66008(1)"`: `P3 sequences` (20)
- `"vl66594(1)"`: `function(normalize)` (23)
- `"vl67044__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl68435__bennett_qalloc(0, 4)"`: `P3 sequences` (20)
- `"vl68494(%a0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl68494(@hglob)"`: `function(normalize)` (23)
- `"vl69365(1)"`: `P3 sequences` (20)
- `"vl69719__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl69719__bennett_qalloc(0, 2)"`: `P3 sequences` (20)
- `"vl69719__bennett_qalloc(0, 3)"`: `function(normalize)` (20)
- `"vl69719__bennett_qalloc(0, 4)"`: `P3 sequences` (20)
- `"vl69719__bennett_qalloc(0, 8)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl69719__bennett_qborrow(1, 1)"`: `function(normalize)` (20)
- `"vl69732(%a0)"`: `function(normalize)` (23)
- `"vl69777(%a1, 1)"`: `function(normalize)` (23)
- `"vl70282(%a0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl70341__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl70341__bennett_qborrow(1, 1)"`: `P3 sequences` (20)
- `"vl70385(%a0, 1)"`: `P3 sequences` (23)
- `"vl70601(1)"`: `P3 sequences` (23)
- `"vl70876(1)"`: `P3 sequences` (23)
- `"vl70977(1)"`: `P3 sequences` (20)
- `"vl71200(%a0, 8)"`: `P3 sequences` (23)
- `"vl71834(1)"`: `P3 sequences` (20)
- `"vl71917(1)"`: `function(normalize)` (20)
- `"vl71972(%a0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl72281(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl72598__bennett_measure(%a0, 0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl72598__bennett_measure(%a0, 0).i"`: `P3 sequences` (23)
- `"vl72598__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl72598__bennett_qalloc(0, 2)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl72598__bennett_qalloc(0, 4)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl72598__bennett_qborrow(1, 4)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl72690(1)"`: `function(normalize)` (23)
- `"vl73209(%a0, 3)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl74879()"`: `P3 sequences` (23)
- `"vl75073__bennett_qalloc(0, 1)"`: `P3 sequences` (20)
- `"vl75695(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl75791__bennett_qalloc(0, 1)"`: `P3 sequences` (23)
- `"vl76167(%a0, 4)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl76365(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl76999(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl77672__bennett_measure(%a0, 0).i"`: `P3 sequences` (20)
- `"vl77672__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl77672__bennett_qalloc(0, 2)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl77672__bennett_qalloc(0, 4)"`: `P3 sequences` (20)
- `"vl77672__bennett_qalloc(0, 8)"`: `function(normalize)` (20)
- `"vl77931(1)"`: `P3 sequences` (23)
- `"vl77939(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl77951(1)"`: `P3 sequences` (23)
- `"vl78063(%a1)"`: `P3 sequences` (20)
- `"vl79735(1, 100)"`: `P3 sequences` (23)
- `"vl79763(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl80143(1)"`: `P3 sequences` (20)
- `"vl80538(1).0.copyload"`: `P3 sequences` (20)
- `"vl81127()"`: `P3 sequences` (23)
- `"vl81127(3, 8)"`: `P3 sequences` (23)
- `"vl81504__bennett_qalloc(0, 1)"`: `P3 sequences` (20)
- `"vl81504__bennett_qborrow(1, 1)"`: `P3 sequences` (20)
- `"vl81942(%a0, 8)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl82115(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl82121(11, 12)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl82506(%a0)"`: `P3 sequences` (20)
- `"vl82506(@hglob)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl83627(1, 8, 40, 2, 9, 4, 17)"`: `function(normalize)` (23)
- `"vl83627(11, 12)"`: `P3 sequences` (23)
- `"vl83734(1)"`: `P3 sequences` (23)
- `"vl84937(1)"`: `function(normalize)` (23)
- `"vl85714(1)"`: `P3 sequences` (23)
- `"vl85806(1)"`: `P3 sequences` (23)
- `"vl86131(%a0, 3)"`: `P3 sequences` (23)
- `"vl86133(11, 12)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl87169(1)"`: `P3 sequences` (23)
- `"vl88024(1)"`: `P3 sequences` (20)
- `"vl88044(1)"`: `P3 sequences` (20)
- `"vl88344__bennett_qalloc(0, 1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl88346(%a0)"`: `P3 sequences` (20)
- `"vl88405(%a0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl88405(@hglob)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl88405(@hq)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl88532(%a0, 3)"`: `P3 sequences` (23)
- `"vl88868(%a0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl89235(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl89528(%a0)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl89528(@hreg)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl89713(1)"`: `P3 sequences` (20)
- `"vl89899(1)"`: `function(normalize)` (20)
- `"vl89934(1)"`: `function(normalize)` (23)
- `"vl90139(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl90329__bennett_qalloc(0, 1)"`: `P3 sequences` (20)
- `"vl90896__bennett_qalloc(0, 1)"`: `P3 sequences` (23)
- `"vl91036(%a0, 1)"`: `function(normalize)` (23)
- `"vl91786(1)"`: `P3 sequences` (23)
- `"vl91993(%a0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl91993(%a0, 3)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl92053(%a0, 3)"`: `P3 sequences` (23)
- `"vl92144(1)"`: `P3 sequences` (23)
- `"vl92607__bennett_qborrow(1, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl92756__bennett_qalloc(0, 1)"`: `P3 sequences` (20)
- `"vl94475(1)"`: `P3 sequences` (23)
- `"vl94583__bennett_qalloc(0, 1)"`: `P3 sequences` (20)
- `"vl94921(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl95496__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl96582(1)"`: `P3 sequences` (20), `function(normalize)` (20)
- `"vl96986(1)"`: `P3 sequences` (20)
- `"vl97059(1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl97883(1)"`: `P3 sequences` (20)
- `"vl97944__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl98411__bennett_qalloc(0, 1)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl98411__bennett_qalloc(0, 8)"`: `P3 sequences` (23)
- `"vl98633(%a0, 3)"`: `P3 sequences` (20)
- `"vl98792(%a0)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl98792(@hglob)"`: `P3 sequences` (23), `function(normalize)` (23)
- `"vl98792(@hreg)"`: `P3 sequences` (23), `function(normalize)` (23)
- `align 8`: `P3 sequences` (18,20,23), `attributor` (18,20,23), `cgscc(attributor-cgscc)` (18,20,23)
- `dereferenceable(16)`: `P3 sequences` (18,20,23), `attributor` (18,20,23), `cgscc(attributor-cgscc)` (18,20,23)
- `dereferenceable(24)`: `P3 sequences` (18,20,23), `attributor` (18,20,23), `cgscc(attributor-cgscc)` (18,20,23)
- `dereferenceable(48)`: `P3 sequences` (18,20,23), `attributor` (18,20,23), `cgscc(attributor-cgscc)` (18,20,23)
- `dereferenceable(8)`: `P3 sequences` (18,20,23), `attributor` (18,20,23), `cgscc(attributor-cgscc)` (18,20,23)
- `local_unnamed_addr`: `P3 sequences` (18,20,23), `alloc-token` (23), `always-inline` (18,20,23), `annotation2metadata` (18,20,23), `asan` (18,20,23), `assign-guid` (20,23), `attributor` (18,20,23), `attributor-light` (18,20,23), `called-value-propagation` (18,20,23), `canonicalize-aliases` (18,20,23), `cg-profile` (18,20,23), `cgscc(argpromotion)` (18,20,23), `cgscc(attributor-cgscc)` (18,20,23), `cgscc(attributor-light-cgscc)` (18,20,23), `cgscc(coro-annotation-elide)` (20,23), `cgscc(coro-split)` (18,20,23), `cgscc(function-attrs)` (18,20,23), `cgscc(inline)` (18,20,23), `cgscc(invalidate<all>)` (18,20,23), `cgscc(no-op-cgscc)` (18,20,23), `cgscc(openmp-opt-cgscc)` (18,20,23), `check-debugify` (18,20,23), `constmerge` (18,20,23), `coro-cleanup` (18,20,23), `coro-early` (18,20,23) … 359 more
- `mustprogress`: `P3 sequences` (18,20,23), `alloc-token` (23), `always-inline` (18,20,23), `annotation2metadata` (18,20,23), `asan` (18,20,23), `assign-guid` (20,23), `attributor` (18,20,23), `attributor-light` (18,20,23), `called-value-propagation` (18,20,23), `canonicalize-aliases` (18,20,23), `cg-profile` (18,20,23), `cgscc(argpromotion)` (18,20,23), `cgscc(attributor-cgscc)` (18,20,23), `cgscc(attributor-light-cgscc)` (18,20,23), `cgscc(coro-annotation-elide)` (20,23), `cgscc(coro-split)` (18,20,23), `cgscc(function-attrs)` (18,20,23), `cgscc(inline)` (18,20,23), `cgscc(invalidate<all>)` (18,20,23), `cgscc(no-op-cgscc)` (18,20,23), `cgscc(openmp-opt-cgscc)` (18,20,23), `check-debugify` (18,20,23), `constmerge` (18,20,23), `coro-cleanup` (18,20,23), `coro-early` (18,20,23) … 346 more
- `nobuiltin`: `asan` (23), `hwasan` (23)
- `nofpclass(nan inf nzero nsub nnorm)`: `P3 sequences` (23), `attributor` (23), `attributor-light` (23), `cgscc(attributor-cgscc)` (23), `cgscc(attributor-light-cgscc)` (23)
- `nofpclass(nan ninf nzero nsub nnorm)`: `P3 sequences` (20), `attributor` (20), `attributor-light` (20), `cgscc(attributor-cgscc)` (20), `cgscc(attributor-light-cgscc)` (20)
- `nofree`: `P3 sequences` (18,20,23), `alloc-token` (23), `always-inline` (18,20,23), `annotation2metadata` (18,20,23), `asan` (18,20,23), `assign-guid` (20,23), `attributor` (18,20,23), `attributor-light` (18,20,23), `called-value-propagation` (18,20,23), `canonicalize-aliases` (18,20,23), `cg-profile` (18,20,23), `cgscc(argpromotion)` (18,20,23), `cgscc(attributor-cgscc)` (18,20,23), `cgscc(attributor-light-cgscc)` (18,20,23), `cgscc(coro-annotation-elide)` (20,23), `cgscc(coro-split)` (18,20,23), `cgscc(function-attrs)` (18,20,23), `cgscc(inline)` (18,20,23), `cgscc(invalidate<all>)` (18,20,23), `cgscc(no-op-cgscc)` (18,20,23), `cgscc(openmp-opt-cgscc)` (18,20,23), `check-debugify` (18,20,23), `constmerge` (18,20,23), `coro-cleanup` (18,20,23), `coro-early` (18,20,23) … 346 more
- `nonnull`: `P3 sequences` (18,20,23), `alloc-token` (23), `always-inline` (18,20,23), `annotation2metadata` (18,20,23), `asan` (18,20,23), `assign-guid` (20,23), `attributor` (18,20,23), `attributor-light` (18,20,23), `called-value-propagation` (18,20,23), `canonicalize-aliases` (18,20,23), `cg-profile` (18,20,23), `cgscc(argpromotion)` (18,20,23), `cgscc(attributor-cgscc)` (18,20,23), `cgscc(attributor-light-cgscc)` (18,20,23), `cgscc(coro-annotation-elide)` (20,23), `cgscc(coro-split)` (18,20,23), `cgscc(function-attrs)` (18,20,23), `cgscc(inline)` (18,20,23), `cgscc(invalidate<all>)` (18,20,23), `cgscc(no-op-cgscc)` (18,20,23), `cgscc(openmp-opt-cgscc)` (18,20,23), `check-debugify` (18,20,23), `constmerge` (18,20,23), `coro-cleanup` (18,20,23), `coro-early` (18,20,23) … 359 more
- `nosync`: `P3 sequences` (18,20,23), `alloc-token` (23), `always-inline` (18,20,23), `annotation2metadata` (18,20,23), `asan` (18,20,23), `assign-guid` (20,23), `attributor` (18,20,23), `attributor-light` (18,20,23), `called-value-propagation` (18,20,23), `canonicalize-aliases` (18,20,23), `cg-profile` (18,20,23), `cgscc(argpromotion)` (18,20,23), `cgscc(attributor-cgscc)` (18,20,23), `cgscc(attributor-light-cgscc)` (18,20,23), `cgscc(coro-annotation-elide)` (20,23), `cgscc(coro-split)` (18,20,23), `cgscc(function-attrs)` (18,20,23), `cgscc(inline)` (18,20,23), `cgscc(invalidate<all>)` (18,20,23), `cgscc(no-op-cgscc)` (18,20,23), `cgscc(openmp-opt-cgscc)` (18,20,23), `check-debugify` (18,20,23), `constmerge` (18,20,23), `coro-cleanup` (18,20,23), `coro-early` (18,20,23) … 346 more
- `noundef`: `P3 sequences` (18,20,23), `attributor` (18,20,23), `cgscc(attributor-cgscc)` (18,20,23), `dfsan` (18,20,23)
- `nounwind`: `P3 sequences` (18,20,23), `alloc-token` (23), `always-inline` (18,20,23), `annotation2metadata` (18,20,23), `asan` (18,20,23), `assign-guid` (20,23), `attributor` (18,20,23), `attributor-light` (18,20,23), `called-value-propagation` (18,20,23), `canonicalize-aliases` (18,20,23), `cg-profile` (18,20,23), `cgscc(argpromotion)` (18,20,23), `cgscc(attributor-cgscc)` (18,20,23), `cgscc(attributor-light-cgscc)` (18,20,23), `cgscc(coro-annotation-elide)` (20,23), `cgscc(coro-split)` (18,20,23), `cgscc(function-attrs)` (18,20,23), `cgscc(inline)` (18,20,23), `cgscc(invalidate<all>)` (18,20,23), `cgscc(no-op-cgscc)` (18,20,23), `cgscc(openmp-opt-cgscc)` (18,20,23), `check-debugify` (18,20,23), `constmerge` (18,20,23), `coro-cleanup` (18,20,23), `coro-early` (18,20,23) … 359 more
- `range(i64 0, 2)`: `P3 sequences` (20,23), `alloc-token` (23), `always-inline` (20,23), `annotation2metadata` (20,23), `asan` (20,23), `assign-guid` (20,23), `attributor` (20,23), `attributor-light` (20,23), `called-value-propagation` (20,23), `canonicalize-aliases` (20,23), `cg-profile` (20,23), `cgscc(argpromotion)` (20,23), `cgscc(attributor-cgscc)` (20,23), `cgscc(attributor-light-cgscc)` (20,23), `cgscc(coro-annotation-elide)` (20,23), `cgscc(coro-split)` (20,23), `cgscc(function-attrs)` (20,23), `cgscc(inline)` (20,23), `cgscc(invalidate<all>)` (20,23), `cgscc(no-op-cgscc)` (20,23), `cgscc(openmp-opt-cgscc)` (20,23), `check-debugify` (20,23), `constmerge` (20,23), `coro-cleanup` (20,23), `coro-early` (20,23) … 350 more
- `range(i64 0, 4)`: `P3 sequences` (20,23), `alloc-token` (23), `always-inline` (20,23), `annotation2metadata` (20,23), `asan` (20,23), `assign-guid` (20,23), `attributor` (20,23), `attributor-light` (20,23), `called-value-propagation` (20,23), `canonicalize-aliases` (20,23), `cg-profile` (20,23), `cgscc(argpromotion)` (20,23), `cgscc(attributor-cgscc)` (20,23), `cgscc(attributor-light-cgscc)` (20,23), `cgscc(coro-annotation-elide)` (20,23), `cgscc(coro-split)` (20,23), `cgscc(function-attrs)` (20,23), `cgscc(inline)` (20,23), `cgscc(invalidate<all>)` (20,23), `cgscc(no-op-cgscc)` (20,23), `cgscc(openmp-opt-cgscc)` (20,23), `check-debugify` (20,23), `constmerge` (20,23), `coro-cleanup` (20,23), `coro-early` (20,23) … 350 more
- `zeroext`: `dfsan` (18,20,23)

## 6. L3-static review flags (new ptrtoint/inttoptr in handle-touching functions; never automatic failures)

### legality-relevant: 1611 distinct (case, pass, function, opcode)

- corpus `c-memcpy-handle-int` `alloc-token`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `always-inline`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `annotation2metadata`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `assign-guid`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `attributor`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `attributor-light`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `called-value-propagation`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `canonicalize-aliases`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `cg-profile`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `cgscc(argpromotion)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `cgscc(attributor-cgscc)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `cgscc(attributor-light-cgscc)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `cgscc(coro-annotation-elide)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `cgscc(coro-split)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `cgscc(function-attrs)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `cgscc(inline)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `cgscc(invalidate<all>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `cgscc(no-op-cgscc)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `cgscc(openmp-opt-cgscc)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `check-debugify`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `constmerge`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `coro-cleanup`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `coro-early`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `cross-dso-cfi`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `ctx-prof-flatten`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `ctx-prof-flatten-prethinlink`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `deadargelim`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `debugify`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `declare-runtime-libcalls`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `default<O1>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `default<O2>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `default<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `default<O3>,default<O3>,default<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `default<Os>`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `default<Oz>`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `dot-callgraph`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `drop-type-tests`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `dxil-upgrade`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `elim-avail-extern`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `embed-bitcode`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `expand-variadics`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `extract-blocks`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `fatlto-cleanup`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `forceattrs`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(aa-eval)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(adce)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(add-discriminators)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(aggressive-instcombine)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(alignment-from-assumptions)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(annotation-remarks)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(assume-builder)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(assume-simplify)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(atomic-expand)`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `function(bdce)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(bounds-checking)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(break-crit-edges)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(callbr-prepare)`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `function(callbrprepare)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `function(callsite-splitting)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(cfguard)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(chr)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(complex-deinterleaving)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `function(consthoist)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(constraint-elimination)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(coro-elide)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(correlated-propagation)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(count-visits)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(dce)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(declare-to-assign)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(dfa-jump-threading)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(div-rem-pairs)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(dot-cfg)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(dot-cfg-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(dot-dom)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(dot-dom-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(dot-post-dom)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(dot-post-dom-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(drop-unnecessary-assumes)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `function(dse)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(dwarf-eh-prepare)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `function(early-cse)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(ee-instrument)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(expand-large-div-rem)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `function(expand-large-fp-convert)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `function(expand-memcmp)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(expand-reductions)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `function(extra-vector-passes)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `function(fix-irreducible)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(flatten-cfg)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `function(flattencfg)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `function(float2int)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(func-properties-stats)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `function(gc-lowering)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `function(guard-widening)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(gvn)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(gvn-hoist)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(gvn-sink)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(hardware-loops)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(helloworld)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(indirectbr-expand)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(infer-address-spaces)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(infer-alignment)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(inject-tli-mappings)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(inline-asm-prepare)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `function(instcombine)`: `case_entry` gains `inttoptr` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(instcombine)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(instcombine<no-verify-fixpoint>)`: `case_entry` gains `inttoptr` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(instcombine<no-verify-fixpoint>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(instcount)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(instnamer)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(instsimplify)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(interleaved-access)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(interleaved-load-combine)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(invalidate<all>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(irce)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(jump-table-to-switch)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `function(jump-threading)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(kcfi)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(kernel-info)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `function(lcssa)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(libcalls-shrinkwrap)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(lint)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(load-store-vectorizer)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(load-store-vectorizer)`: `rg` gains `inttoptr` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(load-store-vectorizer)`: `rpair` gains `inttoptr` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(canon-freeze))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(dot-ddg))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(extra-simple-loop-unswitch-passes))`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `function(loop(guard-widening))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(indvars))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(invalidate<all>))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(loop-bound-split))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(loop-deletion))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(loop-flatten))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(loop-idiom))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(loop-idiom-vectorize))`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `function(loop(loop-instsimplify))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(loop-interchange))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(loop-predication))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(loop-reduce))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(loop-reroll))`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `function(loop(loop-rotate))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(loop-simplifycfg))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(loop-term-fold))`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `function(loop(loop-unroll-and-jam))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(loop-unroll-full))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(loop-versioning-licm))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(no-op-loop))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(no-op-loopnest))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(print))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(print<ddg>))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(print<hash-recognize>))`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `function(loop(print<iv-users>))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(print<loop-cache-cost>))`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `function(loop(print<loopnest>))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop(simple-loop-unswitch))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop-data-prefetch)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop-distribute)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop-fusion)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop-load-elim)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop-mssa(licm))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop-mssa(lnicm))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop-simplify)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop-sink)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop-unroll)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop-vectorize)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loop-versioning)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(lower-allow-check)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `function(lower-atomic)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `function(lower-constant-intrinsics)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(lower-expect)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(lower-guard-intrinsic)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(lower-invoke)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `function(lower-matrix-intrinsics)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(lower-switch)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `function(lower-widenable-condition)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(loweratomic)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `function(lowerinvoke)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `function(lowerswitch)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `function(make-guards-explicit)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(mem2reg)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(memcpyopt)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(mergeicmps)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(mergereturn)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `function(mldst-motion)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(move-auto-init)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(nary-reassociate)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(newgvn)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(no-op-function)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(normalize)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `function(objc-arc)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(objc-arc-contract)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(objc-arc-expand)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(pa-eval)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(partially-inline-libcalls)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(pgo-memop-opt)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(place-safepoints)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print-alias-sets)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `function(print-cfg-sccs)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `function(print-memderefs)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `function(print-mustexecute)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `function(print-predicateinfo)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `function(print<access-info>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<alias-sets>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `function(print<assumptions>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<block-freq>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<branch-prob>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<cfg-sccs>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `function(print<cost-model>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<cycles>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<da>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<debug-ata>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<delinearization>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<demanded-bits>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<domfrontier>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<domtree>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<func-properties>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<inline-cost>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<inliner-size-estimator>)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `function(print<lazy-value-info>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<loop-cache-cost>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `function(print<loops>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<mem-derefs>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `function(print<memoryssa-walker>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<memoryssa>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<must-execute>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `function(print<phi-values>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<postdomtree>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<predicate-info>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `function(print<regions>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<scalar-evolution>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<scev-division>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `function(print<stack-lifetime>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<stack-safety-local>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(print<uniformity>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(prof-inject)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `function(reassociate)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(redundant-dbg-inst-elim)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(reg2mem)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(replace-with-veclib)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `function(safe-stack)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(sandbox-vectorizer)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `function(scalarize-masked-mem-intrin)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(scalarizer)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(sccp)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(select-optimize)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `function(separate-const-offset-from-gep)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(simplifycfg)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(sink)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(sjlj-eh-prepare)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(slp-vectorizer)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(slsr)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(speculative-execution)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(sroa)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(stack-protector)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(strip-convergence-intrinsics)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `function(strip-gc-relocates)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(structurizecfg)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(tailcallelim)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(tlshoist)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `function(transform-warning)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(typepromotion)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(unify-loop-exits)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(unreachableblockelim)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `function(vector-combine)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(verify)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(verify<cycles>)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `function(verify<domtree>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(verify<loops>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(verify<memoryssa>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(verify<regions>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(verify<safepoint-ir>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(verify<scalar-evolution>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(view-cfg)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(view-cfg-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(view-dom)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(view-dom-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(view-post-dom)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(view-post-dom-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(wasm-eh-prepare)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `function(win-eh-prepare)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `global-merge`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `global-merge-func`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `globaldce`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `globalopt`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `globalsplit`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `hipstdpar-interpose-alloc`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `hipstdpar-math-fixup`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `hotcoldsplit`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `inferattrs`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `inliner-wrapper`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `inliner-wrapper-no-mandatory-first`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `insert-gcov-profiling`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `instrorderfile`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `instrprof`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `internalize [-internalize-public-api-list=case_entry]`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `invalidate<all>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `ipsccp`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `iroutliner`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `jmc-instrumenter`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `loop-extract`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `lower-comment-string`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `lower-emutls`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `lower-global-dtors`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `lower-ifunc`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `lowertypetests`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `lto-pre-link<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `lto<O3>`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `lto<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `memprof-context-disambiguation`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `memprof-remove-attributes`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `mergefunc`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `mir-check-debugify`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `mir-debugify`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `mir-strip-debug`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `module-inline`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `name-anon-globals`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `no-op-module`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `noinline-nonprevailing`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `norecurse-lto-inference`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `objc-arc-apelim`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `openmp-opt`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `openmp-opt-postlink`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `partial-inliner`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `pgo-force-function-attrs`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `pgo-icall-prom`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `poison-checking`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `pre-isel-intrinsic-lowering`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `print`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `print-callgraph`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `print-callgraph-sccs`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `print-ir-similarity`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `print-lcg`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `print-lcg-dot`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `print-must-be-executed-contexts`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `print-profile-summary`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `print-stack-safety`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `print<ctx-prof-analysis>`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `print<dxil-metadata>`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `print<dxil-resource-binding>`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `print<dxil-resources>`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `print<inline-advisor>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `print<module-debuginfo>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `print<reg-usage>`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `print<structural-hash>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `pseudo-probe`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `pseudo-probe-update`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `recompute-globalsaa`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `rel-lookup-table-converter`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `rewrite-statepoints-for-gc`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `rewrite-symbols`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `rpo-function-attrs`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `sancov-module`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `sanmd-module`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `scc-oz-module-inliner`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `seq-0003`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0005`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0007`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0009`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0009`: `rg` gains `inttoptr` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0009`: `rpair` gains `inttoptr` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0010`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0010`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0012`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0013`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0015`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0015`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0015`: `rg` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0015`: `rpair` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0019`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-memcpy-handle-int` `seq-0019`: `rg` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0019`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0020`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0029`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0031`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0032`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0033`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0034`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0038`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0039`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0041`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0042`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0042`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0043`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0046`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0047`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0048`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0050`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0052`: `case_entry` gains `ptrtoint` (LLVM 18,23)
- corpus `c-memcpy-handle-int` `seq-0052`: `rg` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0052`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0055`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0056`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0058`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0059`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0061`: `case_entry` gains `ptrtoint` (LLVM 18,23)
- corpus `c-memcpy-handle-int` `seq-0062`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0064`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0064`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0066`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0073`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0075`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `seq-0075`: `rg` gains `inttoptr` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `seq-0075`: `rpair` gains `inttoptr` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `seq-0077`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0077`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0080`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0081`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0081`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0082`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0082`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0083`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0083`: `rg` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0083`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0084`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0086`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0088`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0094`: `case_entry` gains `inttoptr` (LLVM 18,23)
- corpus `c-memcpy-handle-int` `seq-0094`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0096`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0101`: `0` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0101`: `1` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0101`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0103`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0105`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0105`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `seq-0105`: `rg` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0105`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0109`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0111`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0111`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0111`: `rg` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0111`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0114`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0116`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `seq-0116`: `rg` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0116`: `rpair` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0117`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0117`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0117`: `rg` gains `inttoptr` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0117`: `rpair` gains `inttoptr` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0119`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0122`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0122`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `seq-0123`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0123`: `case_entry` gains `ptrtoint` (LLVM 18,23)
- corpus `c-memcpy-handle-int` `seq-0123`: `rg` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0123`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0124`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0130`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0132`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0132`: `rg` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0132`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0133`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0133`: `rg` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0133`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0134`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0135`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0141`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0142`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `seq-0143`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0144`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0146`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0148`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0152`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0152`: `rg` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0152`: `rpair` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0153`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0154`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0155`: `0` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0155`: `1` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0155`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0156`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0156`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0158`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0162`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0162`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0163`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0163`: `rg` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0163`: `rpair` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0164`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0165`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0170`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0170`: `rg` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0170`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0171`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0177`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0177`: `rg` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0177`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0179`: `case_entry` gains `inttoptr` (LLVM 18,20)
- corpus `c-memcpy-handle-int` `seq-0183`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0186`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0188`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `c-memcpy-handle-int` `seq-0188`: `case_entry` gains `ptrtoint` (LLVM 18,23)
- corpus `c-memcpy-handle-int` `seq-0188`: `rg` gains `inttoptr` (LLVM 18,23)
- corpus `c-memcpy-handle-int` `seq-0188`: `rpair` gains `inttoptr` (LLVM 18,23)
- corpus `c-memcpy-handle-int` `seq-0190`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-memcpy-handle-int` `seq-0198`: `case_entry` gains `ptrtoint` (LLVM 18,23)
- corpus `c-memcpy-handle-int` `seq-0198`: `rg` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0198`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `c-memcpy-handle-int` `seq-0199`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `shadow-stack-gc-lowering`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `simplify-type-tests`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `static-data-annotator`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `strip`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `strip-dead-cg-profile`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-memcpy-handle-int` `strip-dead-debug-info`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `strip-dead-prototypes`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `strip-debug-declare`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `strip-nondebug`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `strip-nonlinetable-debuginfo`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `synthetic-counts-propagation`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-memcpy-handle-int` `thinlto-pre-link<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `thinlto<O3>`: `case_entry` gains `inttoptr` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `thinlto<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `verify`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `view-callgraph`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-memcpy-handle-int` `wholeprogramdevirt`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-program-mixed` `function(load-store-vectorizer)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-program-mixed` `function(load-store-vectorizer)`: `diffuse` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `function(load-store-vectorizer)`: `oracle` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0009`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-program-mixed` `seq-0012`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-program-mixed` `seq-0015`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-program-mixed` `seq-0019`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `c-program-mixed` `seq-0019`: `diffuse` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0019`: `oracle` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0034`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-program-mixed` `seq-0039`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-program-mixed` `seq-0042`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-program-mixed` `seq-0043`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-program-mixed` `seq-0050`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-program-mixed` `seq-0052`: `case_entry` gains `ptrtoint` (LLVM 18,23)
- corpus `c-program-mixed` `seq-0052`: `diffuse` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0052`: `oracle` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0058`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-program-mixed` `seq-0059`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-program-mixed` `seq-0061`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-program-mixed` `seq-0075`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-program-mixed` `seq-0076`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-program-mixed` `seq-0080`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-program-mixed` `seq-0083`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-program-mixed` `seq-0083`: `diffuse` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0083`: `oracle` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0101`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-program-mixed` `seq-0105`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `c-program-mixed` `seq-0111`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-program-mixed` `seq-0111`: `diffuse` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0111`: `oracle` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0116`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-program-mixed` `seq-0117`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-program-mixed` `seq-0123`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-program-mixed` `seq-0124`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-program-mixed` `seq-0132`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-program-mixed` `seq-0133`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-program-mixed` `seq-0133`: `diffuse` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0133`: `oracle` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0134`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-program-mixed` `seq-0141`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-program-mixed` `seq-0142`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-program-mixed` `seq-0144`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-program-mixed` `seq-0152`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-program-mixed` `seq-0153`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-program-mixed` `seq-0154`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-program-mixed` `seq-0155`: `.extracted` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0155`: `1` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0155`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-program-mixed` `seq-0156`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-program-mixed` `seq-0163`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `c-program-mixed` `seq-0170`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-program-mixed` `seq-0170`: `diffuse` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0170`: `oracle` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0177`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-program-mixed` `seq-0177`: `diffuse` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0177`: `oracle` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0188`: `case_entry` gains `ptrtoint` (LLVM 18,23)
- corpus `c-program-mixed` `seq-0188`: `diffuse` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0188`: `oracle` gains `inttoptr` (LLVM 23)
- corpus `c-program-mixed` `seq-0190`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `c-program-mixed` `seq-0198`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `c-pure-attr-wrapper` `function(load-store-vectorizer)`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-pure-attr-wrapper` `msan`: `case_entry` gains `inttoptr` (LLVM 18,20)
- corpus `c-pure-attr-wrapper` `msan`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `c-pure-attr-wrapper` `seq-0019`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-pure-attr-wrapper` `seq-0052`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-pure-attr-wrapper` `seq-0083`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-pure-attr-wrapper` `seq-0111`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-pure-attr-wrapper` `seq-0132`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-pure-attr-wrapper` `seq-0133`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-pure-attr-wrapper` `seq-0155`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-pure-attr-wrapper` `seq-0170`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `c-pure-attr-wrapper` `seq-0177`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `alloc-token`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `always-inline`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `annotation2metadata`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `assign-guid`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `attributor`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `attributor-light`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `called-value-propagation`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `canonicalize-aliases`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `cg-profile`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `cgscc(argpromotion)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `cgscc(attributor-cgscc)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `cgscc(attributor-light-cgscc)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `cgscc(coro-annotation-elide)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `cgscc(coro-split)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `cgscc(function-attrs)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `cgscc(inline)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `cgscc(invalidate<all>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `cgscc(no-op-cgscc)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `cgscc(openmp-opt-cgscc)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `check-debugify`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `constmerge`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `coro-cleanup`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `coro-early`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `cross-dso-cfi`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `ctx-prof-flatten`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `ctx-prof-flatten-prethinlink`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `deadargelim`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `debugify`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `declare-runtime-libcalls`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `default<O1>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `default<O2>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `default<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `default<O3>,default<O3>,default<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `default<Os>`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `default<Oz>`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `dot-callgraph`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `drop-type-tests`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `dxil-upgrade`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `elim-avail-extern`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `embed-bitcode`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `expand-variadics`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `extract-blocks`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `fatlto-cleanup`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `forceattrs`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(aa-eval)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(adce)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(add-discriminators)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(aggressive-instcombine)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(alignment-from-assumptions)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(annotation-remarks)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(assume-builder)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(assume-simplify)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(atomic-expand)`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `function(bdce)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(bounds-checking)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(break-crit-edges)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(callbr-prepare)`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `function(callbrprepare)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `function(callsite-splitting)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(cfguard)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(chr)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(complex-deinterleaving)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `function(consthoist)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(constraint-elimination)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(coro-elide)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(correlated-propagation)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(count-visits)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(dce)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(declare-to-assign)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(dfa-jump-threading)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(div-rem-pairs)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(dot-cfg)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(dot-cfg-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(dot-dom)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(dot-dom-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(dot-post-dom)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(dot-post-dom-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(drop-unnecessary-assumes)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `function(dse)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(dwarf-eh-prepare)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `function(early-cse)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(ee-instrument)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(expand-large-div-rem)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `function(expand-large-fp-convert)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `function(expand-memcmp)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(expand-reductions)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `function(extra-vector-passes)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `function(fix-irreducible)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(flatten-cfg)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `function(flattencfg)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `function(float2int)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(func-properties-stats)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `function(gc-lowering)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `function(guard-widening)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(gvn)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(gvn-hoist)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(gvn-sink)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(hardware-loops)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(helloworld)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(indirectbr-expand)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(infer-address-spaces)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(infer-alignment)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(inject-tli-mappings)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(inline-asm-prepare)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `function(instcombine)`: `case_entry` gains `inttoptr` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(instcombine)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(instcombine<no-verify-fixpoint>)`: `case_entry` gains `inttoptr` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(instcombine<no-verify-fixpoint>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(instcount)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(instnamer)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(instsimplify)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(interleaved-access)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(interleaved-load-combine)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(invalidate<all>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(irce)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(jump-table-to-switch)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `function(jump-threading)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(kcfi)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(kernel-info)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `function(lcssa)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(libcalls-shrinkwrap)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(lint)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(load-store-vectorizer)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(load-store-vectorizer)`: `rg` gains `inttoptr` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(load-store-vectorizer)`: `rpair` gains `inttoptr` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(canon-freeze))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(dot-ddg))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(extra-simple-loop-unswitch-passes))`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(guard-widening))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(indvars))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(invalidate<all>))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(loop-bound-split))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(loop-deletion))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(loop-flatten))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(loop-idiom))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(loop-idiom-vectorize))`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(loop-instsimplify))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(loop-interchange))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(loop-predication))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(loop-reduce))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(loop-reroll))`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `function(loop(loop-rotate))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(loop-simplifycfg))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(loop-term-fold))`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(loop-unroll-and-jam))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(loop-unroll-full))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(loop-versioning-licm))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(no-op-loop))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(no-op-loopnest))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(print))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(print<ddg>))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(print<hash-recognize>))`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `function(loop(print<iv-users>))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(print<loop-cache-cost>))`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `function(loop(print<loopnest>))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop(simple-loop-unswitch))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop-data-prefetch)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop-distribute)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop-fusion)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop-load-elim)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop-mssa(licm))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop-mssa(lnicm))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop-simplify)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop-sink)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop-unroll)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop-vectorize)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loop-versioning)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(lower-allow-check)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `function(lower-atomic)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `function(lower-constant-intrinsics)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(lower-expect)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(lower-guard-intrinsic)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(lower-invoke)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `function(lower-matrix-intrinsics)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(lower-switch)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `function(lower-widenable-condition)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(loweratomic)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `function(lowerinvoke)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `function(lowerswitch)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `function(make-guards-explicit)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(mem2reg)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(memcpyopt)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(mergeicmps)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(mergereturn)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `function(mldst-motion)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(move-auto-init)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(nary-reassociate)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(newgvn)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(no-op-function)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(normalize)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `function(objc-arc)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(objc-arc-contract)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(objc-arc-expand)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(pa-eval)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(partially-inline-libcalls)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(pgo-memop-opt)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(place-safepoints)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print-alias-sets)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `function(print-cfg-sccs)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `function(print-memderefs)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `function(print-mustexecute)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `function(print-predicateinfo)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `function(print<access-info>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<alias-sets>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `function(print<assumptions>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<block-freq>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<branch-prob>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<cfg-sccs>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `function(print<cost-model>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<cycles>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<da>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<debug-ata>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<delinearization>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<demanded-bits>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<domfrontier>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<domtree>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<func-properties>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<inline-cost>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<inliner-size-estimator>)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `function(print<lazy-value-info>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<loop-cache-cost>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `function(print<loops>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<mem-derefs>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `function(print<memoryssa-walker>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<memoryssa>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<must-execute>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `function(print<phi-values>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<postdomtree>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<predicate-info>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `function(print<regions>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<scalar-evolution>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<scev-division>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `function(print<stack-lifetime>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<stack-safety-local>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(print<uniformity>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(prof-inject)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `function(reassociate)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(redundant-dbg-inst-elim)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(reg2mem)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(replace-with-veclib)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `function(safe-stack)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(sandbox-vectorizer)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `function(scalarize-masked-mem-intrin)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(scalarizer)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(sccp)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(select-optimize)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `function(separate-const-offset-from-gep)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(simplifycfg)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(sink)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(sjlj-eh-prepare)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(slp-vectorizer)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(slsr)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(speculative-execution)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(sroa)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(stack-protector)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(strip-convergence-intrinsics)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `function(strip-gc-relocates)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(structurizecfg)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(tailcallelim)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(tlshoist)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `function(transform-warning)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(typepromotion)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(unify-loop-exits)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(unreachableblockelim)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `function(vector-combine)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(verify)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(verify<cycles>)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `function(verify<domtree>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(verify<loops>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(verify<memoryssa>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(verify<regions>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(verify<safepoint-ir>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(verify<scalar-evolution>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(view-cfg)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(view-cfg-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(view-dom)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(view-dom-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(view-post-dom)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(view-post-dom-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(wasm-eh-prepare)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `function(win-eh-prepare)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `global-merge`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `global-merge-func`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `globaldce`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `globalopt`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `globalsplit`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `hipstdpar-interpose-alloc`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `hipstdpar-math-fixup`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `hotcoldsplit`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `inferattrs`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `inliner-wrapper`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `inliner-wrapper-no-mandatory-first`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `instrorderfile`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `instrprof`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `internalize [-internalize-public-api-list=case_entry]`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `invalidate<all>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `ipsccp`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `iroutliner`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `jmc-instrumenter`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `loop-extract`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `lower-comment-string`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `lower-emutls`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `lower-global-dtors`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `lower-ifunc`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `lowertypetests`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `lto-pre-link<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `lto<O3>`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `lto<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `memprof-context-disambiguation`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `memprof-remove-attributes`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `mergefunc`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `mir-check-debugify`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `mir-debugify`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `mir-strip-debug`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `module-inline`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `name-anon-globals`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `no-op-module`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `noinline-nonprevailing`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `norecurse-lto-inference`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `objc-arc-apelim`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `openmp-opt`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `openmp-opt-postlink`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `partial-inliner`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `pgo-force-function-attrs`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `pgo-icall-prom`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `poison-checking`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `pre-isel-intrinsic-lowering`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `print`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `print-callgraph`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `print-callgraph-sccs`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `print-ir-similarity`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `print-lcg`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `print-lcg-dot`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `print-must-be-executed-contexts`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `print-profile-summary`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `print-stack-safety`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `print<ctx-prof-analysis>`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `print<dxil-metadata>`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `print<dxil-resource-binding>`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `print<dxil-resources>`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `print<inline-advisor>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `print<module-debuginfo>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `print<reg-usage>`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `print<structural-hash>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `pseudo-probe`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `pseudo-probe-update`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `recompute-globalsaa`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `rel-lookup-table-converter`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `rewrite-statepoints-for-gc`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `rewrite-symbols`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `rpo-function-attrs`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `sancov-module`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `sanmd-module`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `scc-oz-module-inliner`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `seq-0003`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0005`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0007`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0009`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0009`: `rg` gains `inttoptr` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0009`: `rpair` gains `inttoptr` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0010`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0010`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0012`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0013`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0015`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0015`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0015`: `rg` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0015`: `rpair` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0019`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-memcpy-handle-int` `seq-0019`: `rg` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0019`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0020`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0029`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0031`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0032`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0033`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0034`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0038`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0039`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0041`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0042`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0042`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0043`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0046`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0047`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0048`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0050`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0052`: `case_entry` gains `ptrtoint` (LLVM 18,23)
- corpus `dbg-memcpy-handle-int` `seq-0052`: `rg` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0052`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0055`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0056`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0058`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0059`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0061`: `case_entry` gains `ptrtoint` (LLVM 18,23)
- corpus `dbg-memcpy-handle-int` `seq-0062`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0064`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0064`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0066`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0073`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0075`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `seq-0075`: `rg` gains `inttoptr` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `seq-0075`: `rpair` gains `inttoptr` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `seq-0077`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0077`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0080`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0081`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0081`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0082`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0082`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0083`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0083`: `rg` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0083`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0084`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0086`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0088`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0094`: `case_entry` gains `inttoptr` (LLVM 18,23)
- corpus `dbg-memcpy-handle-int` `seq-0094`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0096`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0101`: `0` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0101`: `1` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0101`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0103`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0105`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0105`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `seq-0105`: `rg` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0105`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0109`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0111`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0111`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0111`: `rg` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0111`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0114`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0116`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `seq-0116`: `rg` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0116`: `rpair` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0117`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0117`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0117`: `rg` gains `inttoptr` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0117`: `rpair` gains `inttoptr` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0119`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0122`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0122`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `seq-0123`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0123`: `case_entry` gains `ptrtoint` (LLVM 18,23)
- corpus `dbg-memcpy-handle-int` `seq-0123`: `rg` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0123`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0124`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0130`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0132`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0132`: `rg` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0132`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0133`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0133`: `rg` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0133`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0134`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0135`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0141`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0142`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `seq-0143`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0144`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0146`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0148`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0152`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0152`: `rg` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0152`: `rpair` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0153`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0154`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0155`: `0` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0155`: `1` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0155`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0156`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0156`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0158`: `case_entry` gains `inttoptr` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0162`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0162`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0163`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0163`: `rg` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0163`: `rpair` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0164`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0165`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0170`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0170`: `rg` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0170`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0171`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0177`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0177`: `rg` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0177`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0179`: `case_entry` gains `inttoptr` (LLVM 18,20)
- corpus `dbg-memcpy-handle-int` `seq-0183`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0186`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0188`: `case_entry` gains `inttoptr` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `seq-0188`: `case_entry` gains `ptrtoint` (LLVM 18,23)
- corpus `dbg-memcpy-handle-int` `seq-0188`: `rg` gains `inttoptr` (LLVM 18,23)
- corpus `dbg-memcpy-handle-int` `seq-0188`: `rpair` gains `inttoptr` (LLVM 18,23)
- corpus `dbg-memcpy-handle-int` `seq-0190`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-memcpy-handle-int` `seq-0195`: `case_entry` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0198`: `case_entry` gains `ptrtoint` (LLVM 18,23)
- corpus `dbg-memcpy-handle-int` `seq-0198`: `rg` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0198`: `rpair` gains `inttoptr` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `seq-0199`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `shadow-stack-gc-lowering`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `simplify-type-tests`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `static-data-annotator`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `strip`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `strip-dead-cg-profile`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-memcpy-handle-int` `strip-dead-debug-info`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `strip-dead-prototypes`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `strip-debug-declare`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `strip-nondebug`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `strip-nonlinetable-debuginfo`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `synthetic-counts-propagation`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-memcpy-handle-int` `thinlto-pre-link<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `thinlto<O3>`: `case_entry` gains `inttoptr` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `thinlto<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `verify`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `view-callgraph`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-memcpy-handle-int` `wholeprogramdevirt`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-region-operands` `function(load-store-vectorizer)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-region-operands` `function(load-store-vectorizer)`: `ora0` gains `inttoptr` (LLVM 18,20,23)
- corpus `dbg-region-operands` `seq-0009`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-region-operands` `seq-0009`: `ora0` gains `inttoptr` (LLVM 20)
- corpus `dbg-region-operands` `seq-0012`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-region-operands` `seq-0015`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-region-operands` `seq-0015`: `ora0` gains `inttoptr` (LLVM 18)
- corpus `dbg-region-operands` `seq-0019`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `dbg-region-operands` `seq-0019`: `ora0` gains `inttoptr` (LLVM 23)
- corpus `dbg-region-operands` `seq-0034`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-region-operands` `seq-0039`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-region-operands` `seq-0042`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-region-operands` `seq-0043`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-region-operands` `seq-0050`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-region-operands` `seq-0052`: `case_entry` gains `ptrtoint` (LLVM 18,23)
- corpus `dbg-region-operands` `seq-0052`: `ora0` gains `inttoptr` (LLVM 23)
- corpus `dbg-region-operands` `seq-0058`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-region-operands` `seq-0059`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-region-operands` `seq-0061`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-region-operands` `seq-0075`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-region-operands` `seq-0075`: `ora0` gains `inttoptr` (LLVM 18,20)
- corpus `dbg-region-operands` `seq-0076`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-region-operands` `seq-0080`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-region-operands` `seq-0083`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-region-operands` `seq-0083`: `ora0` gains `inttoptr` (LLVM 23)
- corpus `dbg-region-operands` `seq-0101`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-region-operands` `seq-0101`: `ora0` gains `inttoptr` (LLVM 18)
- corpus `dbg-region-operands` `seq-0105`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `dbg-region-operands` `seq-0105`: `ora0` gains `inttoptr` (LLVM 23)
- corpus `dbg-region-operands` `seq-0111`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-region-operands` `seq-0111`: `ora0` gains `inttoptr` (LLVM 23)
- corpus `dbg-region-operands` `seq-0116`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `dbg-region-operands` `seq-0116`: `ora0` gains `inttoptr` (LLVM 18)
- corpus `dbg-region-operands` `seq-0117`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-region-operands` `seq-0117`: `ora0` gains `inttoptr` (LLVM 20)
- corpus `dbg-region-operands` `seq-0123`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-region-operands` `seq-0123`: `ora0` gains `inttoptr` (LLVM 23)
- corpus `dbg-region-operands` `seq-0124`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-region-operands` `seq-0132`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-region-operands` `seq-0132`: `ora0` gains `inttoptr` (LLVM 23)
- corpus `dbg-region-operands` `seq-0133`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-region-operands` `seq-0133`: `ora0` gains `inttoptr` (LLVM 23)
- corpus `dbg-region-operands` `seq-0134`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-region-operands` `seq-0141`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-region-operands` `seq-0142`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-region-operands` `seq-0144`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-region-operands` `seq-0152`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-region-operands` `seq-0152`: `ora0` gains `inttoptr` (LLVM 18)
- corpus `dbg-region-operands` `seq-0153`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-region-operands` `seq-0154`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-region-operands` `seq-0155`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-region-operands` `seq-0155`: `ora0` gains `inttoptr` (LLVM 23)
- corpus `dbg-region-operands` `seq-0156`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-region-operands` `seq-0163`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `dbg-region-operands` `seq-0163`: `ora0` gains `inttoptr` (LLVM 18)
- corpus `dbg-region-operands` `seq-0170`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-region-operands` `seq-0170`: `ora0` gains `inttoptr` (LLVM 23)
- corpus `dbg-region-operands` `seq-0177`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-region-operands` `seq-0177`: `ora0` gains `inttoptr` (LLVM 23)
- corpus `dbg-region-operands` `seq-0188`: `case_entry` gains `ptrtoint` (LLVM 18,23)
- corpus `dbg-region-operands` `seq-0188`: `ora0` gains `inttoptr` (LLVM 18,23)
- corpus `dbg-region-operands` `seq-0190`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `dbg-region-operands` `seq-0198`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `dbg-region-operands` `seq-0198`: `ora0` gains `inttoptr` (LLVM 23)
- corpus `region-fnptr-array-index` `function(load-store-vectorizer)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `region-fnptr-array-index` `seq-0009`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `region-fnptr-array-index` `seq-0015`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `region-fnptr-array-index` `seq-0042`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `region-fnptr-array-index` `seq-0101`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `region-fnptr-array-index` `seq-0117`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `region-fnptr-array-index` `seq-0152`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `region-fnptr-array-index` `seq-0163`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `alloc-token`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `always-inline`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `annotation2metadata`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `assign-guid`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `attributor`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `attributor-light`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `called-value-propagation`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `canonicalize-aliases`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `cg-profile`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `cgscc(argpromotion)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `cgscc(attributor-cgscc)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `cgscc(attributor-light-cgscc)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `cgscc(coro-annotation-elide)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `cgscc(coro-split)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `cgscc(function-attrs)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `cgscc(inline)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `cgscc(invalidate<all>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `cgscc(no-op-cgscc)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `cgscc(openmp-opt-cgscc)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `check-debugify`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `constmerge`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `coro-cleanup`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `coro-early`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `cross-dso-cfi`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `ctx-prof-flatten`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `ctx-prof-flatten-prethinlink`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `deadargelim`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `debugify`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `declare-runtime-libcalls`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `default<O1>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `default<O2>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `default<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `default<O3>,default<O3>,default<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `default<Os>`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `default<Oz>`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `dot-callgraph`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `drop-type-tests`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `dxil-upgrade`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `elim-avail-extern`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `embed-bitcode`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `expand-variadics`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `extract-blocks`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `fatlto-cleanup`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `forceattrs`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(aa-eval)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(adce)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(add-discriminators)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(aggressive-instcombine)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(alignment-from-assumptions)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(annotation-remarks)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(assume-builder)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(assume-simplify)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(atomic-expand)`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `function(bdce)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(bounds-checking)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(break-crit-edges)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(callbr-prepare)`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `function(callbrprepare)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `function(callsite-splitting)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(cfguard)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(chr)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(complex-deinterleaving)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `function(consthoist)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(constraint-elimination)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(coro-elide)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(correlated-propagation)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(count-visits)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(dce)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(declare-to-assign)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(dfa-jump-threading)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(div-rem-pairs)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(dot-cfg)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(dot-cfg-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(dot-dom)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(dot-dom-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(dot-post-dom)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(dot-post-dom-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(drop-unnecessary-assumes)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `function(dse)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(dwarf-eh-prepare)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `function(early-cse)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(ee-instrument)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(expand-large-div-rem)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `function(expand-large-fp-convert)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `function(expand-memcmp)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(expand-reductions)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `function(extra-vector-passes)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `function(fix-irreducible)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(flatten-cfg)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `function(flattencfg)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `function(float2int)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(func-properties-stats)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `function(gc-lowering)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `function(guard-widening)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(gvn)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(gvn-hoist)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(gvn-sink)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(hardware-loops)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(helloworld)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(indirectbr-expand)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(infer-address-spaces)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(infer-alignment)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(inject-tli-mappings)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(inline-asm-prepare)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `function(instcombine)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(instcombine<no-verify-fixpoint>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(instcount)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(instnamer)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(instsimplify)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(interleaved-access)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(interleaved-load-combine)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(invalidate<all>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(irce)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(jump-table-to-switch)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `function(jump-threading)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(kcfi)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(kernel-info)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `function(lcssa)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(libcalls-shrinkwrap)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(lint)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(load-store-vectorizer)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(canon-freeze))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(dot-ddg))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(extra-simple-loop-unswitch-passes))`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `function(loop(guard-widening))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(indvars))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(invalidate<all>))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(loop-bound-split))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(loop-deletion))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(loop-flatten))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(loop-idiom))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(loop-idiom-vectorize))`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `function(loop(loop-instsimplify))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(loop-interchange))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(loop-predication))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(loop-reduce))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(loop-reroll))`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `function(loop(loop-rotate))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(loop-simplifycfg))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(loop-term-fold))`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `function(loop(loop-unroll-and-jam))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(loop-unroll-full))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(loop-versioning-licm))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(no-op-loop))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(no-op-loopnest))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(print))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(print<ddg>))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(print<hash-recognize>))`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `function(loop(print<iv-users>))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(print<loop-cache-cost>))`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `function(loop(print<loopnest>))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop(simple-loop-unswitch))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop-data-prefetch)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop-distribute)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop-fusion)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop-load-elim)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop-mssa(licm))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop-mssa(lnicm))`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop-simplify)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop-sink)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop-unroll)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop-vectorize)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loop-versioning)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(lower-allow-check)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `function(lower-atomic)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `function(lower-constant-intrinsics)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(lower-expect)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(lower-guard-intrinsic)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(lower-invoke)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `function(lower-matrix-intrinsics)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(lower-switch)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `function(lower-widenable-condition)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(loweratomic)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `function(lowerinvoke)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `function(lowerswitch)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `function(make-guards-explicit)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(mem2reg)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(memcpyopt)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(mergeicmps)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(mergereturn)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `function(mldst-motion)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(move-auto-init)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(nary-reassociate)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(newgvn)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(no-op-function)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(normalize)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `function(objc-arc)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(objc-arc-contract)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(objc-arc-expand)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(pa-eval)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(partially-inline-libcalls)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(pgo-memop-opt)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(place-safepoints)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print-alias-sets)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `function(print-cfg-sccs)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `function(print-memderefs)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `function(print-mustexecute)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `function(print-predicateinfo)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `function(print<access-info>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<alias-sets>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `function(print<assumptions>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<block-freq>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<branch-prob>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<cfg-sccs>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `function(print<cost-model>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<cycles>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<da>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<debug-ata>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<delinearization>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<demanded-bits>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<domfrontier>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<domtree>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<func-properties>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<inline-cost>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<inliner-size-estimator>)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `function(print<lazy-value-info>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<loop-cache-cost>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `function(print<loops>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<mem-derefs>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `function(print<memoryssa-walker>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<memoryssa>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<must-execute>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `function(print<phi-values>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<postdomtree>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<predicate-info>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `function(print<regions>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<scalar-evolution>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<scev-division>)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `function(print<stack-lifetime>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<stack-safety-local>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(print<uniformity>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(prof-inject)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `function(reassociate)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(redundant-dbg-inst-elim)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(reg2mem)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(replace-with-veclib)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `function(safe-stack)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(sandbox-vectorizer)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `function(scalarize-masked-mem-intrin)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(scalarizer)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(sccp)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(select-optimize)`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `function(separate-const-offset-from-gep)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(simplifycfg)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(sink)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(sjlj-eh-prepare)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(slp-vectorizer)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(slsr)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(speculative-execution)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(sroa)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(stack-protector)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(strip-convergence-intrinsics)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `function(strip-gc-relocates)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(structurizecfg)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(tailcallelim)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(tlshoist)`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `function(transform-warning)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(typepromotion)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(unify-loop-exits)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(unreachableblockelim)`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `function(vector-combine)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(verify)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(verify<cycles>)`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `function(verify<domtree>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(verify<loops>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(verify<memoryssa>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(verify<regions>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(verify<safepoint-ir>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(verify<scalar-evolution>)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(view-cfg)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(view-cfg-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(view-dom)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(view-dom-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(view-post-dom)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(view-post-dom-only)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(wasm-eh-prepare)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `function(win-eh-prepare)`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `global-merge`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `global-merge-func`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `globaldce`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `globalopt`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `globalsplit`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `hipstdpar-interpose-alloc`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `hipstdpar-math-fixup`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `hotcoldsplit`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `inferattrs`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `inliner-wrapper`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `inliner-wrapper-no-mandatory-first`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `insert-gcov-profiling`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `instrorderfile`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `instrprof`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `internalize [-internalize-public-api-list=case_entry]`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `invalidate<all>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `ipsccp`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `iroutliner`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `jmc-instrumenter`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `loop-extract`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `lower-comment-string`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `lower-emutls`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `lower-global-dtors`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `lower-ifunc`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `lowertypetests`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `lto-pre-link<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `lto<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `memprof-context-disambiguation`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `memprof-remove-attributes`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `mergefunc`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `mir-check-debugify`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `mir-debugify`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `mir-strip-debug`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `module-inline`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `name-anon-globals`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `no-op-module`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `noinline-nonprevailing`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `norecurse-lto-inference`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `objc-arc-apelim`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `openmp-opt`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `openmp-opt-postlink`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `partial-inliner`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `pgo-force-function-attrs`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `pgo-icall-prom`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `poison-checking`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `pre-isel-intrinsic-lowering`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `print`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `print-callgraph`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `print-callgraph-sccs`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `print-ir-similarity`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `print-lcg`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `print-lcg-dot`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `print-must-be-executed-contexts`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `print-profile-summary`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `print-stack-safety`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `print<ctx-prof-analysis>`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `print<dxil-metadata>`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `print<dxil-resource-binding>`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `print<dxil-resources>`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `print<inline-advisor>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `print<module-debuginfo>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `print<reg-usage>`: `case_entry` gains `ptrtoint` (LLVM 20,23)
- corpus `val-memcpy-handle-int` `print<structural-hash>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `pseudo-probe`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `pseudo-probe-update`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `recompute-globalsaa`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `rel-lookup-table-converter`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `rewrite-statepoints-for-gc`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `rewrite-symbols`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `rpo-function-attrs`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `sancov-module`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `sanmd-module`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `scc-oz-module-inliner`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `seq-0003`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0005`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0007`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0010`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `seq-0013`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0015`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `seq-0020`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `seq-0029`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `seq-0031`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `seq-0032`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `seq-0033`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `seq-0038`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0041`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0042`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0046`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0047`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `seq-0048`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `seq-0055`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `seq-0056`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0061`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `seq-0062`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `seq-0064`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0066`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `seq-0073`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `seq-0075`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0077`: `case_entry` gains `ptrtoint` (LLVM 18,23)
- corpus `val-memcpy-handle-int` `seq-0081`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `seq-0082`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `seq-0084`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `seq-0086`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0088`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0094`: `case_entry` gains `ptrtoint` (LLVM 18,23)
- corpus `val-memcpy-handle-int` `seq-0096`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `seq-0103`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0105`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `seq-0109`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0111`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `seq-0114`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `seq-0117`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0119`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0122`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `seq-0123`: `case_entry` gains `ptrtoint` (LLVM 18,23)
- corpus `val-memcpy-handle-int` `seq-0130`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `seq-0135`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `seq-0142`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `seq-0143`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `seq-0146`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0148`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `seq-0156`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0158`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0162`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `seq-0164`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `seq-0165`: `case_entry` gains `ptrtoint` (LLVM 20)
- corpus `val-memcpy-handle-int` `seq-0171`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `seq-0179`: `case_entry` gains `ptrtoint` (LLVM 18,20)
- corpus `val-memcpy-handle-int` `seq-0183`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `seq-0186`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `seq-0188`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `seq-0198`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `seq-0199`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `shadow-stack-gc-lowering`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `simplify-type-tests`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `static-data-annotator`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `strip`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `strip-dead-cg-profile`: `case_entry` gains `ptrtoint` (LLVM 23)
- corpus `val-memcpy-handle-int` `strip-dead-debug-info`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `strip-dead-prototypes`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `strip-debug-declare`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `strip-nondebug`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `strip-nonlinetable-debuginfo`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `synthetic-counts-propagation`: `case_entry` gains `ptrtoint` (LLVM 18)
- corpus `val-memcpy-handle-int` `thinlto-pre-link<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `thinlto<O3>`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `verify`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `view-callgraph`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)
- corpus `val-memcpy-handle-int` `wholeprogramdevirt`: `case_entry` gains `ptrtoint` (LLVM 18,20,23)

### env-error/non-preserving: 1127 distinct (case, pass, function, opcode)

By pass: `dfsan` 272, `msan` 272, `tysan` 206, `instrumentor` 179, `function(memprof)` 162, `pgo-instr-gen` 4, `internalize` 3, `memprof-module` 3, `tsan-module` 3, `asan` 3, `hwasan` 3, `function(tsan)` 3, `ctx-instr-lower` 3, `nsan` 3, `rtsan` 3, `ctx-instr-gen` 3, `insert-gcov-profiling` 1, `function(sjlj-eh-prepare)` 1

## 7. L6 region-operand shapes

Shapes present in baselines: `const`: 23 cases; `load-from-const-table`: 2 cases; `other`: 3 cases

| Shape | passes that introduced it (majors) |
|---|---|
| `select-of-consts` | `P3 sequences` (18,20,23), `default<O1>` (18,20,23), `default<O2>` (18,20,23), `default<O3>` (18,20,23), `default<O3>,default<O3>,default<O3>` (18,20,23), `default<Os>` (18,20), `default<Oz>` (18,20), `lto-pre-link<O3>` (18,20,23), `lto<O3>` (18,20,23), `scc-oz-module-inliner` (18,20,23), `thinlto-pre-link<O3>` (18,20,23), `thinlto<O3>` (18,20,23) |
| `phi-of-consts` | `P3 sequences` (18,20,23), `function(gvn)` (18,20,23), `function(gvn-sink)` (18,20,23), `function(mem2reg)` (18,20,23), `function(sroa)` (18,20,23), `scc-oz-module-inliner` (18,20,23), `thinlto-pre-link<O3>` (18,20,23) |
| `phi-of-mixed` | `P3 sequences` (18,23), `default<O1>` (18,20,23), `default<O2>` (18,20,23), `default<O3>` (18,20,23), `default<O3>,default<O3>,default<O3>` (18,20,23), `default<Os>` (18,20), `default<Oz>` (18,20), `lto-pre-link<O3>` (18,20,23), `lto<O3>` (18,20,23), `thinlto<O3>` (18,20,23) |
| `other` | `P3 sequences` (18,20,23), `function(reg2mem)` (18,20,23), `hwasan` (18,20,23), `instrumentor` (23) |

### L6 `other` operands already present in the untransformed cases

- `c-pie-reltable-region` in `case_entry`: `__bennett_ctrl` operand 2 = `load ptr, ptr %5, align 8, !tbaa !5` (LLVM 18,20,23)
- `ipo-ipsccp-funcspec-region` in `controlled`: `__bennett_ctrl` operand 2 = `%f` (LLVM 18,20,23)
- `region-fnptr-array-index` in `case_entry`: `__bennett_ctrl` operand 2 = `load ptr, ptr %ps, align 8` (LLVM 18,20,23)
- `region-fnptr-array-index` in `case_entry`: `__bennett_reversible` operand 0 = `load ptr, ptr %pm, align 8` (LLVM 18,20,23)

### L6 `other` introduced by a pass (findings: the plugin cannot resolve these statically): 22 distinct

- corpus `c-pie-reltable-region` P1 `hwasan`: `__bennett_ctrl` operand 2 = `%.0` (LLVM 18,20,23)
- corpus `c-pie-reltable-region` P1 `instrumentor`: `__bennett_ctrl` operand 2 = `%.0` (LLVM 23)
- corpus `c-pie-reltable-region` P1 `function(reg2mem)`: `__bennett_ctrl` operand 2 = `%.0.reload` (LLVM 18,20,23)
- corpus `dbg-region-operands` P3 `P3`: `__bennett_ctrl` operand 2 = `%ora1.sink.reload` (LLVM 23)
- corpus `dbg-region-operands` P1 `hwasan`: `__bennett_ctrl` operand 2 = `%ora3.sink.i` (LLVM 18,20,23)
- corpus `dbg-region-operands` P1 `instrumentor`: `__bennett_ctrl` operand 2 = `%ora3.sink.i` (LLVM 23)
- corpus `dbg-region-operands` P1 `function(reg2mem)`: `__bennett_ctrl` operand 2 = `%ora3.sink.i.reload` (LLVM 18,20,23)
- corpus `dbg-region-operands` P3 `P3`: `__bennett_ctrl` operand 2 = `%ora3.sink.i.reload` (LLVM 18)
- corpus `dbg-region-operands` P3 `P3`: `__bennett_ctrl` operand 2 = `%ora3.sink.reload` (LLVM 23)
- corpus `ipo-globalopt-region-bool` P1 `instrumentor`: `__bennett_adj` operand 0 = `%14` (LLVM 23)
- corpus `ipo-globalopt-region-bool` P1 `instrumentor`: `__bennett_adj` operand 0 = `%18` (LLVM 23)
- corpus `ipo-globalopt-region-bool` P1 `hwasan`: `__bennett_adj` operand 0 = `%f` (LLVM 18,20,23)
- corpus `ipo-ipsccp-funcspec-region` P3 `P3`: `__bennett_ctrl` operand 2 = `%1` (LLVM 18)
- corpus `ipo-ipsccp-funcspec-region` P3 `P3`: `__bennett_ctrl` operand 2 = `%2` (LLVM 23)
- corpus `ipo-ipsccp-funcspec-region` P3 `P3`: `__bennett_ctrl` operand 2 = `%a2` (LLVM 20)
- corpus `region-fnptr-array-index` P1 `instrumentor`: `__bennett_adj` operand 0 = `%20` (LLVM 23)
- corpus `region-fnptr-array-index` P1 `hwasan`: `__bennett_adj` operand 0 = `%f0` (LLVM 18,20,23)
- corpus `region-switch-fnptr-table` P3 `P3`: `__bennett_ctrl` operand 2 = `%oracle1.sink.reload` (LLVM 23)
- corpus `region-switch-fnptr-table` P1 `hwasan`: `__bennett_ctrl` operand 2 = `%oracle3.sink` (LLVM 18,20,23)
- corpus `region-switch-fnptr-table` P1 `instrumentor`: `__bennett_ctrl` operand 2 = `%oracle3.sink` (LLVM 23)
- corpus `region-switch-fnptr-table` P1 `function(reg2mem)`: `__bennett_ctrl` operand 2 = `%oracle3.sink.reload` (LLVM 18,20,23)
- corpus `region-switch-fnptr-table` P3 `P3`: `__bennett_ctrl` operand 2 = `%oracle3.sink.reload` (LLVM 18,23)

## 8. Harness notes

### env-error rule and counts

A native build failure is `env-error` only when (link) every line of the full ld stderr is an undefined/hidden reference to a symbol of an instrumentation runtime we do not link (prefixes `__asan_ __msan_ __tsan_ __hwasan_ __dfsan_ __memprof_ __nsan_ __rtsan_ __tysan_ __ubsan_ __sanitizer_ __sancov_ __cfi_ __safestack_ __xray_ __llvm_profile_ __llvm_ctx_profile_ __llvm_gcov_ llvm_gcda_ llvm_gcov_ __poison_checker_ __instrumentor_ _Unwind_SjLj_`), or the only non-runtime undefined symbol is `case_entry` and the transformed module has no externally visible `@case_entry` definition; or (llc) the module still calls `llvm.instrprof.*` intrinsics (they need the `instrprof` IR lowering pass, which llc does not run) and llc fails in instruction selection. In addition the object must still import every marker the baseline calls, every other check must pass, and no undefined `__bennett_*` symbol may appear.

Counts (cells): corpus: entry-not-external 333, missing-instrumentation-runtime 3239, unlowered-instrprof-intrinsic 560; seed: entry-not-external 18, missing-instrumentation-runtime 169, unlowered-instrprof-intrinsic 30; control: entry-not-external 24, missing-instrumentation-runtime 226, unlowered-instrprof-intrinsic 40

| rule | LLVM | pass | stage | symbols / intrinsics | cells |
|---|---:|---|---|---|---:|
| entry-not-external | 18 | `internalize` | link | `case_entry` | 125 |
| entry-not-external | 20 | `internalize` | link | `case_entry` | 125 |
| entry-not-external | 23 | `internalize` | link | `case_entry` | 125 |
| missing-instrumentation-runtime | 18 | `asan` | link | `__asan_init,__asan_register_elf_globals,__asan_unregister_elf_globals,__asan_version_mismatch_check_vN` | 30 |
| missing-instrumentation-runtime | 18 | `asan` | link | `__asan_init,__asan_register_elf_globals,__asan_version_mismatch_check_vN` | 95 |
| missing-instrumentation-runtime | 18 | `function(memprof)` | link | `__memprof_memcpy,__memprof_shadow_memory_dynamic_address` | 7 |
| missing-instrumentation-runtime | 18 | `function(memprof)` | link | `__memprof_memset` | 1 |
| missing-instrumentation-runtime | 18 | `function(memprof)` | link | `__memprof_shadow_memory_dynamic_address` | 59 |
| missing-instrumentation-runtime | 18 | `function(sjlj-eh-prepare)` | link | `_Unwind_SjLj_Register,_Unwind_SjLj_Unregister` | 2 |
| missing-instrumentation-runtime | 18 | `function(tsan)` | link | `__tsan_func_entry,__tsan_func_exit` | 125 |
| missing-instrumentation-runtime | 18 | `hwasan` | link | `__hwasan_init` | 125 |
| missing-instrumentation-runtime | 18 | `insert-gcov-profiling` | link | `llvm_gcda_emit_arcs,llvm_gcda_emit_function,llvm_gcda_end_file,llvm_gcda_start_file,llvm_gcda_summary_info,llvm_gcov_ini` | 4 |
| missing-instrumentation-runtime | 18 | `instrprof` | link | `__llvm_profile_runtime` | 14 |
| missing-instrumentation-runtime | 18 | `memprof-module` | link | `__memprof_init,__memprof_version_mismatch_check_vN` | 125 |
| missing-instrumentation-runtime | 18 | `msan` | link | `__msan_init,__msan_memcpy,__msan_param_tls,__msan_retval_tls` | 7 |
| missing-instrumentation-runtime | 18 | `msan` | link | `__msan_init,__msan_memset,__msan_param_tls,__msan_retval_tls` | 1 |
| missing-instrumentation-runtime | 18 | `msan` | link | `__msan_init,__msan_param_tls,__msan_retval_tls` | 99 |
| missing-instrumentation-runtime | 18 | `msan` | link | `__msan_init,__msan_param_tls,__msan_retval_tls,__msan_va_arg_overflow_size_tls` | 2 |
| missing-instrumentation-runtime | 18 | `msan` | link | `__msan_init,__msan_param_tls,__msan_retval_tls,__msan_va_arg_overflow_size_tls,__msan_va_arg_tls` | 2 |
| missing-instrumentation-runtime | 18 | `poison-checking` | link | `__poison_checker_assert` | 46 |
| missing-instrumentation-runtime | 18 | `tsan-module` | link | `__tsan_init` | 125 |
| missing-instrumentation-runtime | 20 | `asan` | link | `__asan_init,__asan_register_elf_globals,__asan_unregister_elf_globals,__asan_version_mismatch_check_vN` | 29 |
| missing-instrumentation-runtime | 20 | `asan` | link | `__asan_init,__asan_register_elf_globals,__asan_version_mismatch_check_vN` | 96 |
| missing-instrumentation-runtime | 20 | `ctx-instr-lower` | link | `__llvm_ctx_profile_expected_callee` | 125 |
| missing-instrumentation-runtime | 20 | `function(memprof)` | link | `__memprof_memcpy,__memprof_shadow_memory_dynamic_address` | 7 |
| missing-instrumentation-runtime | 20 | `function(memprof)` | link | `__memprof_memset` | 1 |
| missing-instrumentation-runtime | 20 | `function(memprof)` | link | `__memprof_shadow_memory_dynamic_address` | 58 |
| missing-instrumentation-runtime | 20 | `function(sjlj-eh-prepare)` | link | `_Unwind_SjLj_Register,_Unwind_SjLj_Unregister` | 2 |
| missing-instrumentation-runtime | 20 | `function(tsan)` | link | `__tsan_func_entry,__tsan_func_exit` | 125 |
| missing-instrumentation-runtime | 20 | `hwasan` | link | `__hwasan_init` | 125 |
| missing-instrumentation-runtime | 20 | `insert-gcov-profiling` | link | `llvm_gcda_emit_arcs,llvm_gcda_emit_function,llvm_gcda_end_file,llvm_gcda_start_file,llvm_gcda_summary_info,llvm_gcov_ini` | 4 |
| missing-instrumentation-runtime | 20 | `instrprof` | link | `__llvm_profile_runtime` | 14 |
| missing-instrumentation-runtime | 20 | `memprof-module` | link | `__memprof_init,__memprof_version_mismatch_check_vN` | 125 |
| missing-instrumentation-runtime | 20 | `msan` | link | `__msan_init,__msan_memcpy,__msan_param_tls,__msan_retval_tls` | 7 |
| missing-instrumentation-runtime | 20 | `msan` | link | `__msan_init,__msan_memset,__msan_param_tls,__msan_retval_tls` | 1 |
| missing-instrumentation-runtime | 20 | `msan` | link | `__msan_init,__msan_param_tls,__msan_retval_tls` | 99 |
| missing-instrumentation-runtime | 20 | `msan` | link | `__msan_init,__msan_param_tls,__msan_retval_tls,__msan_va_arg_overflow_size_tls` | 2 |
| missing-instrumentation-runtime | 20 | `msan` | link | `__msan_init,__msan_param_tls,__msan_retval_tls,__msan_va_arg_overflow_size_tls,__msan_va_arg_tls` | 2 |
| missing-instrumentation-runtime | 20 | `nsan` | link | `__nsan_init` | 125 |
| missing-instrumentation-runtime | 20 | `rtsan` | link | `__rtsan_ensure_initialized` | 125 |
| missing-instrumentation-runtime | 20 | `tsan-module` | link | `__tsan_init` | 125 |
| missing-instrumentation-runtime | 20 | `tysan` | link | `__tysan_app_memory_mask,__tysan_init,__tysan_shadow_memory_address` | 71 |
| missing-instrumentation-runtime | 20 | `tysan` | link | `__tysan_init` | 54 |
| missing-instrumentation-runtime | 23 | `asan` | link | `__asan_init,__asan_register_elf_globals,__asan_unregister_elf_globals,__asan_version_mismatch_check_vN` | 29 |
| missing-instrumentation-runtime | 23 | `asan` | link | `__asan_init,__asan_register_elf_globals,__asan_version_mismatch_check_vN` | 94 |
| missing-instrumentation-runtime | 23 | `ctx-instr-lower` | link | `__llvm_ctx_profile_expected_callee` | 125 |
| missing-instrumentation-runtime | 23 | `function(memprof)` | link | `__memprof_memcpy,__memprof_shadow_memory_dynamic_address` | 7 |
| missing-instrumentation-runtime | 23 | `function(memprof)` | link | `__memprof_memset` | 1 |
| missing-instrumentation-runtime | 23 | `function(memprof)` | link | `__memprof_shadow_memory_dynamic_address` | 58 |
| missing-instrumentation-runtime | 23 | `function(sjlj-eh-prepare)` | link | `_Unwind_SjLj_Register,_Unwind_SjLj_Unregister` | 2 |
| missing-instrumentation-runtime | 23 | `function(tsan)` | link | `__tsan_func_entry,__tsan_func_exit` | 125 |
| missing-instrumentation-runtime | 23 | `hwasan` | link | `__hwasan_init` | 123 |
| missing-instrumentation-runtime | 23 | `insert-gcov-profiling` | link | `llvm_gcda_emit_arcs,llvm_gcda_emit_function,llvm_gcda_end_file,llvm_gcda_start_file,llvm_gcda_summary_info,llvm_gcov_ini` | 4 |
| missing-instrumentation-runtime | 23 | `instrprof` | link | `__llvm_profile_runtime` | 14 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_alloca,__instrumentor_post_base_pointer_info,__instrumentor_post_cast,__instrumentor_post_compare,__` | 2 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_alloca,__instrumentor_post_base_pointer_info,__instrumentor_post_cast,__instrumentor_post_compare,__` | 4 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_alloca,__instrumentor_post_base_pointer_info,__instrumentor_post_cast,__instrumentor_post_compare,__` | 18 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_alloca,__instrumentor_post_base_pointer_info,__instrumentor_post_cast,__instrumentor_post_function,_` | 1 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_alloca,__instrumentor_post_base_pointer_info,__instrumentor_post_cast,__instrumentor_post_function,_` | 6 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_alloca,__instrumentor_post_base_pointer_info,__instrumentor_post_cast,__instrumentor_post_function,_` | 7 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_alloca,__instrumentor_post_base_pointer_info,__instrumentor_post_compare,__instrumentor_post_functio` | 2 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_alloca,__instrumentor_post_base_pointer_info,__instrumentor_post_compare,__instrumentor_post_functio` | 5 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_alloca,__instrumentor_post_base_pointer_info,__instrumentor_post_function,__instrumentor_post_global` | 3 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_alloca,__instrumentor_post_base_pointer_info,__instrumentor_post_function,__instrumentor_post_load,_` | 6 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_alloca,__instrumentor_post_base_pointer_info,__instrumentor_post_function,__instrumentor_post_load,_` | 4 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_base_pointer_info,__instrumentor_post_cast,__instrumentor_post_compare,__instrumentor_post_function,` | 1 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_base_pointer_info,__instrumentor_post_cast,__instrumentor_post_compare,__instrumentor_post_function,` | 2 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_base_pointer_info,__instrumentor_post_cast,__instrumentor_post_function,__instrumentor_post_global,_` | 2 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_base_pointer_info,__instrumentor_post_cast,__instrumentor_post_function,__instrumentor_post_global,_` | 1 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_base_pointer_info,__instrumentor_post_cast,__instrumentor_post_function,__instrumentor_post_global_i` | 1 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_base_pointer_info,__instrumentor_post_compare,__instrumentor_post_function,__instrumentor_post_globa` | 1 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_base_pointer_info,__instrumentor_post_function,__instrumentor_post_global,__instrumentor_post_load,_` | 2 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_base_pointer_info,__instrumentor_post_function,__instrumentor_post_global,__instrumentor_post_load,_` | 1 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_base_pointer_info,__instrumentor_post_function,__instrumentor_post_load,__instrumentor_post_module,_` | 2 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_cast,__instrumentor_post_compare,__instrumentor_post_function,__instrumentor_post_module,__instrumen` | 16 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_cast,__instrumentor_post_function,__instrumentor_post_module,__instrumentor_post_numeric,__instrumen` | 12 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_cast,__instrumentor_post_function,__instrumentor_post_module,__instrumentor_post_numeric,__instrumen` | 1 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_compare,__instrumentor_post_function,__instrumentor_post_module,__instrumentor_post_numeric,__instru` | 15 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_function,__instrumentor_post_module,__instrumentor_post_numeric,__instrumentor_pre_function,__instru` | 6 |
| missing-instrumentation-runtime | 23 | `instrumentor` | link | `__instrumentor_post_function,__instrumentor_post_module,__instrumentor_pre_function,__instrumentor_pre_module` | 4 |
| missing-instrumentation-runtime | 23 | `memprof-module` | link | `__memprof_init,__memprof_version_mismatch_check_vN` | 125 |
| missing-instrumentation-runtime | 23 | `msan` | link | `__msan_init,__msan_memcpy,__msan_param_tls,__msan_retval_tls` | 7 |
| missing-instrumentation-runtime | 23 | `msan` | link | `__msan_init,__msan_memset,__msan_param_tls,__msan_retval_tls` | 1 |
| missing-instrumentation-runtime | 23 | `msan` | link | `__msan_init,__msan_param_tls,__msan_retval_tls` | 99 |
| missing-instrumentation-runtime | 23 | `msan` | link | `__msan_init,__msan_param_tls,__msan_retval_tls,__msan_va_arg_overflow_size_tls` | 2 |
| missing-instrumentation-runtime | 23 | `msan` | link | `__msan_init,__msan_param_tls,__msan_retval_tls,__msan_va_arg_overflow_size_tls,__msan_va_arg_tls` | 2 |
| missing-instrumentation-runtime | 23 | `nsan` | link | `__nsan_init` | 125 |
| missing-instrumentation-runtime | 23 | `rtsan` | link | `__rtsan_ensure_initialized` | 125 |
| missing-instrumentation-runtime | 23 | `tsan-module` | link | `__tsan_init` | 125 |
| missing-instrumentation-runtime | 23 | `tysan` | link | `__tysan_init` | 54 |
| missing-instrumentation-runtime | 23 | `tysan` | link | `__tysan_init,__tysan_instrument_mem_inst,__tysan_instrument_with_shadow_update` | 58 |
| missing-instrumentation-runtime | 23 | `tysan` | link | `__tysan_init,__tysan_instrument_with_shadow_update` | 13 |
| unlowered-instrprof-intrinsic | 18 | `pgo-instr-gen` | llc | `llvm.instrprof.increment` | 108 |
| unlowered-instrprof-intrinsic | 18 | `pgo-instr-gen` | llc | `llvm.instrprof.increment,llvm.instrprof.increment.step` | 17 |
| unlowered-instrprof-intrinsic | 18 | `pgo-instr-gen` | llc | `llvm.instrprof.increment,llvm.instrprof.value.profile` | 1 |
| unlowered-instrprof-intrinsic | 20 | `ctx-instr-gen` | llc | `llvm.instrprof.callsite,llvm.instrprof.increment` | 109 |
| unlowered-instrprof-intrinsic | 20 | `ctx-instr-gen` | llc | `llvm.instrprof.callsite,llvm.instrprof.increment,llvm.instrprof.increment.step` | 17 |
| unlowered-instrprof-intrinsic | 20 | `pgo-instr-gen` | llc | `llvm.instrprof.increment` | 107 |
| unlowered-instrprof-intrinsic | 20 | `pgo-instr-gen` | llc | `llvm.instrprof.increment,llvm.instrprof.increment.step` | 17 |
| unlowered-instrprof-intrinsic | 20 | `pgo-instr-gen` | llc | `llvm.instrprof.increment,llvm.instrprof.value.profile` | 2 |
| unlowered-instrprof-intrinsic | 23 | `ctx-instr-gen` | llc | `llvm.instrprof.callsite,llvm.instrprof.increment` | 109 |
| unlowered-instrprof-intrinsic | 23 | `ctx-instr-gen` | llc | `llvm.instrprof.callsite,llvm.instrprof.increment,llvm.instrprof.increment.step` | 17 |
| unlowered-instrprof-intrinsic | 23 | `pgo-instr-gen` | llc | `llvm.instrprof.increment` | 107 |
| unlowered-instrprof-intrinsic | 23 | `pgo-instr-gen` | llc | `llvm.instrprof.increment,llvm.instrprof.increment.step` | 17 |
| unlowered-instrprof-intrinsic | 23 | `pgo-instr-gen` | llc | `llvm.instrprof.increment,llvm.instrprof.value.profile` | 2 |

### non-preserving (documented list; rationale in harness/NOTES.md)

- `dfsan` LLVM 18: 112 cells — DataFlowSanitizer without an ABI list renames functions with a .dfsan suffix, including markers
- `dfsan` LLVM 20: 112 cells — DataFlowSanitizer without an ABI list renames functions with a .dfsan suffix, including markers
- `dfsan` LLVM 23: 112 cells — DataFlowSanitizer without an ABI list renames functions with a .dfsan suffix, including markers
- `hipstdpar-select-accelerator-code` LLVM 18: 126 cells — keeps only accelerator kernels; deletes host code including @case_entry
- `hipstdpar-select-accelerator-code` LLVM 20: 126 cells — keeps only accelerator kernels; deletes host code including @case_entry
- `hipstdpar-select-accelerator-code` LLVM 23: 126 cells — keeps only accelerator kernels; deletes host code including @case_entry
- `metarenamer` LLVM 18: 126 cells — renames every non-intrinsic, non-libcall function, including marker declarations and @case_entry
- `metarenamer` LLVM 20: 126 cells — renames every non-intrinsic, non-libcall function, including marker declarations and @case_entry
- `metarenamer` LLVM 23: 126 cells — renames every non-intrinsic, non-libcall function, including marker declarations and @case_entry

### precondition

- `cfg-switch-op-table` LLVM 23 post-O3 `function(structurizecfg)`: raw run L1,L5; rerun `function(lower-switch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `cfg-switch-op-table` LLVM 23 raw `function(structurizecfg)`: raw run L1,L5; rerun `function(lower-switch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `dbg-region-operands` LLVM 23 raw `function(structurizecfg)`: raw run L1,L4,L5; rerun `function(lower-switch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `c-pie-reltable-region` LLVM 18 raw `function(structurizecfg)`: raw run L1,L4,L5; rerun `function(lowerswitch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `cfg-switch-op-table` LLVM 18 post-O3 `function(structurizecfg)`: raw run L1,L5; rerun `function(lowerswitch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `cfg-switch-op-table` LLVM 18 raw `function(structurizecfg)`: raw run L1,L5; rerun `function(lowerswitch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `dbg-region-operands` LLVM 18 raw `function(structurizecfg)`: raw run L1,L4,L5; rerun `function(lowerswitch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `meas-select-phi-switch` LLVM 18 raw `function(structurizecfg)`: raw run L1,L5; rerun `function(lowerswitch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `region-recursive-tre` LLVM 18 post-O3 `function(structurizecfg)`: raw run L1,L4,L5; rerun `function(lowerswitch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `region-switch-fnptr-table` LLVM 18 raw `function(structurizecfg)`: raw run L1,L4,L5; rerun `function(lowerswitch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `c-pie-reltable-region` LLVM 20 raw `function(structurizecfg)`: raw run L1,L4,L5; rerun `function(lower-switch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `cfg-switch-op-table` LLVM 20 post-O3 `function(structurizecfg)`: raw run L1,L5; rerun `function(lower-switch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `cfg-switch-op-table` LLVM 20 raw `function(structurizecfg)`: raw run L1,L5; rerun `function(lower-switch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `dbg-region-operands` LLVM 20 raw `function(structurizecfg)`: raw run L1,L4,L5; rerun `function(lower-switch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `meas-select-phi-switch` LLVM 20 raw `function(structurizecfg)`: raw run L1,L5; rerun `function(lower-switch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `region-recursive-tre` LLVM 20 post-O3 `function(structurizecfg)`: raw run L1,L4,L5; rerun `function(lower-switch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `region-switch-fnptr-table` LLVM 20 raw `function(structurizecfg)`: raw run L1,L4,L5; rerun `function(lower-switch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `c-pie-reltable-region` LLVM 23 raw `function(structurizecfg)`: raw run L1,L4,L5; rerun `function(lower-switch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `meas-select-phi-switch` LLVM 23 raw `function(structurizecfg)`: raw run L1,L5; rerun `function(lower-switch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `region-recursive-tre` LLVM 23 post-O3 `function(structurizecfg)`: raw run L1,L4,L5; rerun `function(lower-switch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass
- `region-switch-fnptr-table` LLVM 23 raw `function(structurizecfg)`: raw run L1,L4,L5; rerun `function(lower-switch,fix-irreducible,unify-loop-exits,structurizecfg)` → pass

### opt-error (optimizer refused or crashed; not legality results)

- LLVM 18 `P3 seq-0110`: 2 cells (dbg-memcpy-handle-int, dbg-region-operands); `case_entry rg rpair 2 candidates of length 2.  Found in:    Function: rg, Basic Block: bb     Start Instruction:   %i2 = load ptr, ptr %i, align 8, !dbg !44       End Instruction:   store ptr %i2, ptr %i1, align 8, !dbg `
- LLVM 18 `dfsan`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `LLVM ERROR: unsupported operating system PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace. Stack dump: 0.	Program arguments: /usr/lib/llvm-18/bin/opt -passes=dfsa`
- LLVM 18 `function(codegenprepare)`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace. Stack dump: 0.	Program arguments: /usr/lib/llvm-18/bin/opt -passes=function(codegenprepare) /home/tobias/Project`
- LLVM 18 `function(dwarf-eh-prepare)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace. Stack dump: 0.	Program arguments: /usr/lib/llvm-18/bin/opt -passes=function(dwarf-eh-prepare) /home/tobias/Proje`
- LLVM 18 `function(expand-large-div-rem)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace. Stack dump: 0.	Program arguments: /usr/lib/llvm-18/bin/opt -passes=function(expand-large-div-rem) /home/tobias/P`
- LLVM 18 `function(expand-large-fp-convert)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace. Stack dump: 0.	Program arguments: /usr/lib/llvm-18/bin/opt -passes=function(expand-large-fp-convert) /home/tobia`
- LLVM 18 `function(expand-memcmp)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace. Stack dump: 0.	Program arguments: /usr/lib/llvm-18/bin/opt -passes=function(expand-memcmp) /home/tobias/Projects`
- LLVM 18 `function(function-simplification)`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `/usr/lib/llvm-18/bin/opt: invalid function-simplification parameter ''  `
- LLVM 18 `function(gc-lowering)`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace. Stack dump: 0.	Program arguments: /usr/lib/llvm-18/bin/opt -passes=function(gc-lowering) /home/tobias/Projects/b`
- LLVM 18 `function(indirectbr-expand)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace. Stack dump: 0.	Program arguments: /usr/lib/llvm-18/bin/opt -passes=function(indirectbr-expand) /home/tobias/Proj`
- LLVM 18 `function(instcombine)`: 2 cells (c-unprototyped-decl, dbg-region-operands); `LLVM ERROR: Instruction Combining did not reach a fixpoint after 1 iterations PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace. Stack dump: 0.	Program arguments: `
- LLVM 18 `function(interleaved-access)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace. Stack dump: 0.	Program arguments: /usr/lib/llvm-18/bin/opt -passes=function(interleaved-access) /home/tobias/Pro`
- LLVM 18 `function(interleaved-load-combine)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace. Stack dump: 0.	Program arguments: /usr/lib/llvm-18/bin/opt -passes=function(interleaved-load-combine) /home/tobi`
- LLVM 18 `function(select-optimize)`: 28 cells (c-program-mixed, cfg-callsite-splitting, control-handle-deref, control-memory-none, control-readonly, control-region-twin, dbg-region-operands, inline-helper-markers…); `PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace. Stack dump: 0.	Program arguments: /usr/lib/llvm-18/bin/opt -passes=function(select-optimize) /home/tobias/Projec`
- LLVM 18 `function(trigger-verifier-error)`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `Terminator found in the middle of a basic block! label %0 Terminator found in the middle of a basic block! label %0 LLVM ERROR: Broken module found, compilation aborted! PLEASE submit a bug report to https://github.com/l`
- LLVM 18 `function(typepromotion)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace. Stack dump: 0.	Program arguments: /usr/lib/llvm-18/bin/opt -passes=function(typepromotion) /home/tobias/Projects`
- LLVM 18 `function-import`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `LLVM ERROR: error: -function-import requires -summary-file  PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace. Stack dump: 0.	Program arguments: /usr/lib/llvm-18/b`
- LLVM 18 `inliner-ml-advisor-release`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `error: Could not setup Inlining Advisor for the requested mode and/or options `
- LLVM 18 `memprof-use`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `error: : No such file or directory `
- LLVM 18 `msan`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `LLVM ERROR: unsupported operating system PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace. Stack dump: 0.	Program arguments: /usr/lib/llvm-18/bin/opt -passes=msan`
- LLVM 18 `pgo-instr-use`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `error: : No such file or directory `
- LLVM 18 `sample-profile`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `error: Could not open profile: No such file or directory `
- LLVM 18 `trigger-crash`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace. Stack dump: 0.	Program arguments: /usr/lib/llvm-18/bin/opt -passes=trigger-crash /home/tobias/Projects/bennett-w`
- LLVM 18 `trigger-verifier-error`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `Aliasee cannot be NULL! ptr @__bad_alias LLVM ERROR: Broken module found, compilation aborted! PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace. Stack dump: 0.	Pr`
- LLVM 20 `dfsan`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `LLVM ERROR: unsupported operating system PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifacts/21334d62ab8fb1788`
- LLVM 20 `function(atomic-expand)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes`
- LLVM 20 `function(codegenprepare)`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes`
- LLVM 20 `function(complex-deinterleaving)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes`
- LLVM 20 `function(dwarf-eh-prepare)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes`
- LLVM 20 `function(expand-large-div-rem)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes`
- LLVM 20 `function(expand-large-fp-convert)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes`
- LLVM 20 `function(expand-memcmp)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes`
- LLVM 20 `function(function-simplification)`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `/home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt: invalid function-simplification parameter ''  `
- LLVM 20 `function(indirectbr-expand)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes`
- LLVM 20 `function(instcombine)`: 2 cells (c-unprototyped-decl, dbg-region-operands); `LLVM ERROR: Instruction Combining on case_entry did not reach a fixpoint after 1 iterations. Use 'instcombine<no-verify-fixpoint>' or function attribute 'instcombine-no-verify-fixpoint' to suppress this error. `
- LLVM 20 `function(interleaved-access)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes`
- LLVM 20 `function(interleaved-load-combine)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes`
- LLVM 20 `function(loop(loop-bound-split))`: 1 cells (c-program-mixed); `PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes`
- LLVM 20 `function(select-optimize)`: 19 cells (c-program-mixed, cfg-callsite-splitting, control-handle-deref, control-memory-none, control-readonly, control-region-twin, meas-select-phi-switch, seed-ctrl-env…); `PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes`
- LLVM 20 `function(trigger-crash-function)`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes`
- LLVM 20 `function(trigger-verifier-error)`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `Terminator found in the middle of a basic block! label %0 Terminator found in the middle of a basic block! label %0 LLVM ERROR: Broken module found, compilation aborted! PLEASE submit a bug report to https://github.com/j`
- LLVM 20 `function(typepromotion)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes`
- LLVM 20 `function-import`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `LLVM ERROR: error: -function-import requires -summary-file  PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifact`
- LLVM 20 `inliner-ml-advisor-release`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `error: Could not setup Inlining Advisor for the requested mode and/or options `
- LLVM 20 `memprof-use`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `error: : No such file or directory `
- LLVM 20 `msan`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `LLVM ERROR: unsupported operating system PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifacts/21334d62ab8fb1788`
- LLVM 20 `pgo-instr-use`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `error: : No such file or directory `
- LLVM 20 `sample-profile`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `error: Could not open profile: No such file or directory `
- LLVM 20 `trigger-crash-module`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program arguments: /home/tobias/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt -passes`
- LLVM 20 `trigger-verifier-error`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `Aliasee cannot be NULL! ptr @__bad_alias LLVM ERROR: Broken module found, compilation aborted! PLEASE submit a bug report to https://github.com/julialang/julia and include the crash backtrace. Stack dump: 0.	Program argu`
- LLVM 23 `P3 seq-0195`: 61 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `Printing the call graph for module: /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/results/raw/modules/23/edbf5d26fd95053f9ecd5b82023fbaa38f6ae9a2bfcd3462120ff77678abd258/module.bc    Edges `
- LLVM 23 `default`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt: invalid optimization level '' `
- LLVM 23 `default<Os>`: 63 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `LLVM ERROR: The optimization level "Os" is no longer supported. Use O2 in conjunction with the optsize attribute instead. `
- LLVM 23 `default<Oz>`: 63 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `LLVM ERROR: The optimization level "Oz" is no longer supported. Use O2 in conjunction with the minsize attribute instead. `
- LLVM 23 `dfsan`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `LLVM ERROR: unsupported operating system PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace and instructions to reproduce the bug. Stack dump: 0.	Program arguments:`
- LLVM 23 `fatlto-pre-link`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt: missing optimization level for fatlto-pre-link pipeline `
- LLVM 23 `function(atomic-expand)`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `error: 'LibcallLoweringModuleAnalysis' analysis required error: 'LibcallLoweringModuleAnalysis' analysis required error: 'LibcallLoweringModuleAnalysis' analysis required error: 'LibcallLoweringModuleAnalysis' analysis r`
- LLVM 23 `function(codegenprepare)`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `LLVM ERROR: this pass requires the profile-summary module analysis to be available `
- LLVM 23 `function(complex-deinterleaving)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt: pass 'complex-deinterleaving' requires TargetMachine `
- LLVM 23 `function(dwarf-eh-prepare)`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `error: 'LibcallLoweringModuleAnalysis' analysis required error: 'LibcallLoweringModuleAnalysis' analysis required error: 'LibcallLoweringModuleAnalysis' analysis required error: 'LibcallLoweringModuleAnalysis' analysis r`
- LLVM 23 `function(expand-ir-insts)`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `error: 'LibcallLoweringModuleAnalysis' analysis required error: 'LibcallLoweringModuleAnalysis' analysis required error: 'LibcallLoweringModuleAnalysis' analysis required error: 'LibcallLoweringModuleAnalysis' analysis r`
- LLVM 23 `function(free-machine-function)`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace and instructions to reproduce the bug. Stack dump: 0.	Program arguments: /home/tobias/.rustup/toolchains/stable-x`
- LLVM 23 `function(function-simplification)`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt: invalid function-simplification parameter '' `
- LLVM 23 `function(indirectbr-expand)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt: pass 'indirectbr-expand' requires TargetMachine `
- LLVM 23 `function(instcombine)`: 2 cells (c-unprototyped-decl, dbg-region-operands); `LLVM ERROR: Instruction Combining on case_entry did not reach a fixpoint after 1 iterations. Use 'instcombine<no-verify-fixpoint>' or function attribute 'instcombine-no-verify-fixpoint' to suppress this error. `
- LLVM 23 `function(interleaved-access)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt: pass 'interleaved-access' requires TargetMachine `
- LLVM 23 `function(interleaved-load-combine)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt: pass 'interleaved-load-combine' requires TargetMachine `
- LLVM 23 `function(loop(loop-bound-split))`: 1 cells (c-program-mixed); `PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace and instructions to reproduce the bug. Stack dump: 0.	Program arguments: /home/tobias/.rustup/toolchains/stable-x`
- LLVM 23 `function(safe-stack)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt: pass 'safe-stack' requires TargetMachine `
- LLVM 23 `function(select-optimize)`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `LLVM ERROR: this pass requires the profile-summary module analysis to be available `
- LLVM 23 `function(stack-protector)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt: pass 'stack-protector' requires TargetMachine `
- LLVM 23 `function(trigger-crash-function)`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace and instructions to reproduce the bug. Stack dump: 0.	Program arguments: /home/tobias/.rustup/toolchains/stable-x`
- LLVM 23 `function(trigger-verifier-error)`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `Terminator found in the middle of a basic block! label %1 Terminator found in the middle of a basic block! label %1 Terminator found in the middle of a basic block! label %1 Terminator found in the middle of a basic bloc`
- LLVM 23 `function(typepromotion)`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt: pass 'typepromotion' requires TargetMachine `
- LLVM 23 `function-import`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `LLVM ERROR: error: -function-import requires -summary-file  PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace and instructions to reproduce the bug. Stack dump: 0.`
- LLVM 23 `inliner-ml-advisor-release`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `error: Could not setup Inlining Advisor for the requested mode and/or options `
- LLVM 23 `lto`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt: invalid optimization level '' `
- LLVM 23 `lto-pre-link`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt: invalid optimization level '' `
- LLVM 23 `memprof-use`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `error: : No such file or directory `
- LLVM 23 `msan`: 14 cells (control-handle-deref, control-memory-none, control-readonly, control-region-twin, seed-ctrl-env, seed-loop, seed-straight…); `LLVM ERROR: unsupported operating system PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace and instructions to reproduce the bug. Stack dump: 0.	Program arguments:`
- LLVM 23 `pgo-instr-use`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `error: : No such file or directory `
- LLVM 23 `print<dxil-metadata>`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace and instructions to reproduce the bug. Stack dump: 0.	Program arguments: /home/tobias/.rustup/toolchains/stable-x`
- LLVM 23 `print<ir2vec-vocab>`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `LLVM ERROR: IR2Vec vocabulary file path not specified; You may need to set it using --ir2vec-vocab-path `
- LLVM 23 `print<ir2vec>`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `LLVM ERROR: IR2Vec vocabulary file path not specified; You may need to set it using --ir2vec-vocab-path `
- LLVM 23 `prof-verify`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `error: Profile verification failed for function 'case_entry': function entry count missing (set to 0 if cold) error: Profile verification failed for function 'oracle': function entry count missing (set to 0 if cold) erro`
- LLVM 23 `sample-profile`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `error: Could not open profile: No such file or directory `
- LLVM 23 `thinlto`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt: invalid optimization level '' `
- LLVM 23 `thinlto-pre-link`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `/home/tobias/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt: invalid optimization level '' `
- LLVM 23 `trigger-crash-module`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace and instructions to reproduce the bug. Stack dump: 0.	Program arguments: /home/tobias/.rustup/toolchains/stable-x`
- LLVM 23 `trigger-verifier-error`: 126 cells (c-is-constant-budget, c-memcpy-handle-int, c-objectsize-count, c-pie-reltable-region, c-program-mixed, c-pure-attr-wrapper, c-unprototyped-decl, cfg-callsite-splitting…); `Aliasee cannot be NULL! ptr @__bad_alias LLVM ERROR: Broken module found, compilation aborted! PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace and instructions t`

### Baselines

63 baselines; cross-major agreement for all: True; problems: none.

Untransformed module under `llc -O3` behaves differently from `llc -O0` (codegen-level finding; every cell of the case inherits it as L5): `fp-rot-fastmath-reassoc` (18,20,23).

### Method

Region pointers are printed by the runtime as raw addresses and resolved against the linked non-PIE executable's full symbol table (llvm-nm, local symbols included); `F:F?` now means the address is not the start of any symbol. Marker imports are checked with the matching major's llvm-nm (GNU nm misreads objects carrying a `.llvm.lto` section). `.c` cases are compiled with `clang-18 -O1 -Xclang -disable-llvm-passes`. P1 adds `internalize [-internalize-public-api-list=case_entry]` and `instcombine<no-verify-fixpoint>` cells beside the bare ones. P3 draws from P1 passes that were never opt-error/env-error/non-preserving/precondition on any selected case. Every cell has an exact record in raw/runs/*/outcomes.jsonl and, for every non-pass outcome, raw/cells/ID/result.json.
