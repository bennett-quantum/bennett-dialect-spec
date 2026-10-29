# Legality corpus: adversarial cases

56 cases (49 `.ll`, 7 `.c`) for the legality spike
(`docs/spikes/2026-10-28-legality-spike.md`). Every case defines
`i64 @case_entry(i64 %x)`, carries the section 3 header and uses the
section 1 ABI. The `.c` cases declare that ABI inline instead of including
`markers.h`.

- **Parse/verify:** every `.ll` file, and every `.c` file after
  `clang-18 -O0 -Xclang -disable-O0-optnone -emit-llvm -S`, passes
  `opt -passes=verify` on 18, 20 and 23.
- **Baseline:** the harness `baseline` subcommand, run on a scratch copy
  (`/tmp/bennett-corpus/lc`, so the live `results/` was not touched),
  reports `agree` for all 56 cases across 18/20/23.
- **Target layout:** every hand-written `.ll` carries the x86-64 datalayout
  and triple. Without them, TTI-dependent transforms do not fire at all:
  switch-to-lookup, the vectorisers and unroll costing.
- **Scratch:** work files, twins and sweep data are in `/tmp/bennett-corpus/`.
  `fire.sh MAJOR CASE PASSES [opt args]` diffs canonical input against opt
  output. `twin.sh MAJOR CASE PASSES` reruns a case with the marker
  declarations given `memory(none) nounwind willreturn`. `sweep.py MAJOR`
  runs every `--print-passes` pass on every case and diffs static facts.

Tool paths used below: `opt18=/usr/lib/llvm-18/bin/opt`,
`opt20=~/.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools/opt`,
`opt23=~/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/opt`.

## Suspected findings

Each finding below was seen in real opt output. Where a run is described as
dynamic, it was confirmed either with a throwaway stub runtime
(`/tmp/bennett-corpus/stubrt2.c`) or with the harness P2 run on the scratch
copy. In the harness run, each FP/`.c` probe gets L1+L5 FAIL in 28 cells:
O1/O2/O3, O3x3, lto and thinlto, on every major.

### F1. LLVM introduces `ptrtoint`/`inttoptr` on handles the source never cast (L3-static; dialect says "rejected fail-loud")

**What happens.** An 8-byte `memcpy` of a handle is lowered by InstCombine
to `load i64`/`store i64`. Store-to-load forwarding then produces a
`ptrtoint` of the `qalloc` result. The source shape is C struct/field copy,
Rust moves or `memcpy` of a handle-table entry.

**Commands.** `$opt18 -passes=instcombine -S val-memcpy-handle-int.ll` gives
the same output on 18, 20 and 23:

```
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  ...
  store ptr %h, ptr %slot, align 8
  %.cast = ptrtoint ptr %h to i64
  store i64 %.cast, ptr %e, align 8            ; %e is the env passed to __bennett_ctrl
```

Under `lto<O3>` on **LLVM 18**, `c-memcpy-handle-int` makes the full round
trip into a marker argument. The command is
`clang-18 -O0 -Xclang -disable-O0-optnone -emit-llvm -S c-memcpy-handle-int.c -o x.ll; $opt18 -passes='lto<O3>' -S x.ll`:

```
  %7 = ptrtoint ptr %4 to i64
  store i64 %7, ptr %2, align 8
  call void @__bennett_ctrl(ptr noundef %4, ..., ptr noundef nonnull %2)
  ...
  %11 = load i64, ptr %2, align 8
  %.cast1 = inttoptr i64 %11 to ptr
  call void @__bennett_qfree(ptr noundef %.cast1)
```

On 20 and 23 only the `ptrtoint` + `store i64` half appears.

**A second source: `load-store-vectorizer`.** On `c-program-mixed`, on 18 and
23, it merges a handle field and an adjacent `i64` field into one
`<2 x i64>` store:

```
  %31 = ptrtoint ptr %26 to i64        ; %26 = __bennett_qborrow result
  %32 = insertelement <2 x i64> %30, i64 %31, i32 1
  store <2 x i64> %32, ptr %29
```

**Impact.** The dynamic trace is unaffected, because no host code inspects
the integer. Still, north star section 3.1 rejects "a handle that flows ...
through an inttoptr/ptrtoint round trip" fail-loud. Read literally, that
rule rejects valid source after stock O3. The rule needs to be restated, or
the normaliser must undo integer-typed memory copies of handles, as type
punning in memory and not as a host use. The harness's L3-static review
already flags these cells.

### F2. Region identity is not preserved by `mergefunc` (L4), and local region names do not survive `strip`

- **Thunk.** `$opt18 -passes=mergefunc -S region-mergefunc-twins.ll`, same on
  20 and 23. The twin `@oracle_key2` keeps its symbol but its body becomes
  `tail call void @oracle_key1(ptr %0)`, and its direct caller is redirected
  to `@oracle_key1`. `region-inplace-selfinverse` gives the same result for
  a self-inverse `g`/`ginv` pair (xor by a constant): `@xor_k_inv` becomes a
  thunk to `@xor_k`.
- **RAUW.** `region-mergefunc-unnamed-addr`, with `unnamed_addr` regions (the
  rustc default). mergefunc replaces the *marker operand* itself:
  `call void @__bennett_ctrl(ptr %q, i64 0, ptr @oracle_key1, ...)` on both
  arms.
- **Alias.** Adding `-mergefunc-use-aliases`, as rustc does, makes
  `@oracle_key2 = unnamed_addr alias void (ptr), ptr @oracle_key1`, and
  dladdr can then return either name. This was seen on 18, 20 and 23.
  mergefunc is not in `default<O3>`, but rustc enables it.
- **`strip`.** `$opt18 -passes=strip -S region-internal-strip.ll` renames the
  internal region `@rev_body` to `@1`, and the marker receives `ptr @1`.
  `strip-nondebug` does the same. In the sweep, 20 cases lose local
  function names under these two passes.
- **iroutliner.** `$opt18 -passes=iroutliner -S region-iroutliner.ll` moves
  the marker bodies of two regions and of `case_entry` into
  `@outlined_ir_func_0`. The regions keep their symbols, but their bodies
  are now mostly a call to that outlined function.

### F3. Region operands stop being literal function constants after O3 (probe; the orchestrator's question)

**Shapes observed** (18/20/23 unless noted):

| Case | Pipeline | Region operand shape |
|---|---|---|
| `region-select-two-way` | O3 | `select i1 %c.not, ptr @reg_f, ptr @reg_g` |
| `region-switch-fnptr-table` | O3 | `@switch.table.case_entry = private unnamed_addr constant [6 x ptr]`, then gep + load + `phi ptr [%switch.load, ...], [@oracle3, %entry]` |
| `dbg-region-operands` | O3 | same as `region-switch-fnptr-table` |
| `cfg-switch-op-table` | O3 | 7-way `phi i32` on the op operand |
| `region-fnptr-array-index` | O3 | load from an internal constant table, **load from a stack array** (`alloca [2 x ptr]` survives SROA), load from a mutable global table |
| `ipo-globalopt-region-bool` | O3 | load from a constant table indexed by a shrunk-to-`i1` global |

**Not seen:**

- SimplifyCFG does **not** sink `__bennett_ctrl` when the handle and the region
  both differ (`region-select-two-way` part b), nor `__bennett_compute` when
  both bregions differ. Those stay two direct calls.
- `rel-lookup-table-converter` did not turn the function-pointer switch table
  into `llvm.load.relative` (`c-pie-reltable-region`, even with
  `-relocation-model=pic`).

**Question.** What operand shapes must the plugin resolve: constant,
select-of-constants, phi-of-constants, load-from-constant-table, or other?
"Other" includes a load from mutable stack memory. Enzyme handles only the
`select` shape (see `docs/spikes/enzyme-prior-art.md`).

### F4. Marker argument *values* differ between the -O0 baseline and optimised builds, LLVM-legally (L1 FAIL in the harness)

| Case | Baseline (llc -O0) | O3 | Mechanism |
|---|---|---|---|
| `fp-rot-fmuladd-fold` | `rot` θ = `0x0000000000000000` | `0x3C90000000000000` | `llvm.fmuladd` is constant-folded *fused*; llc lowers it to fmul+fadd without FMA |
| `fp-rot-nan-fold` | θ = `0xFFF8000000000000` (SSE "indefinite") | `0x7FF8000000000000` | APFloat default NaN |
| `fp-rot-fastmath-reassoc` | x=1: θ = `0x3fe3333333333334` | `0x3fe3333333333333` | `reassoc` folds `(x*0.1+0.2)+0.3` into `x*0.1+0.5` |
| `c-is-constant-budget` | `qalloc 0 8; reversible budget 1000` | `qalloc 0 3; reversible budget 12` | `llvm.is.constant` |
| `c-objectsize-count` | `qalloc 0 2` | `qalloc 0 5` (x even), `0 4` (x odd) | `llvm.objectsize` |

The north star normalises `is.constant`/`objectsize` and fp *inside
outlined regions after O3*. These values are computed in host code, before
the marker and before any normaliser runs. The spec needs to say whether
marker operands must be optimisation-invariant (and forbid these sources),
or whether the baseline for comparison is the optimised build.

### F5. A source-level effect annotation on a marker-calling helper deletes markers (`c-pure-attr-wrapper`)

`__attribute__((pure))`/`((const))` on helpers that call markers lets O3
common the second `peek_twice` call (two `measure` calls gone) and delete
every `hadamard_ret` call. The stub run shows `measure`/`gate` lines
missing. This is not an LLVM bug; it is a source lie. But Julia
`@assume_effects` and Rust/C attributes can produce it, so the dialect
needs a rule, for example "a marker reachable from a
`memory(none|read)`/`willreturn` function is rejected".

### F6. L2: attributes LLVM adds around markers (none forbidden)

**On declarations:** only `local_unnamed_addr` (globalopt, all 56 cases on
18/20/23).

**On call sites:**

- `nonnull`: instcombine, on region pointers and env allocas.
- `noundef`: attributor.
- `range(i64 0, 2)`: instcombine on 20/23, on small-range integer arguments
  (`eh-invoke-markers`).
- `nounwind`: instcombine marks every marker call inside a `nounwind`
  caller, which is every C function; the inliner does the same for calls
  inlined from a `nounwind` callee.
- `tail`: tailcallelim and O3.

The per-pass sweep (`/tmp/bennett-corpus/sweep/{18,20,23}/sweep.json`) found
no pass that adds `memory`, `readonly`, `readnone`, `willreturn` or
`speculatable` to a marker declaration or call. No pass created an indirect
marker call: GVNSink and SimplifyCFG both refuse to sink calls with
different callees (`cfg-sink-different-callees`).

### Harness-relevant observations (for the harness owner, not legality failures)

1. **Internal/static regions print `F?` in the baseline.** dladdr only sees
   exported symbols. Nine cases are affected (every `static` region in the
   `.c` cases, plus `inline-always-into-region`, `region-global-state`,
   `region-inplace-selfinverse`, `region-internal-strip`), so L4 cannot
   judge them. Resolving through the ELF `.symtab` (or `nm` of the
   executable) would fix it.
2. **`.c` compile flags block inlining.** `-O0 -Xclang -disable-O0-optnone`
   still puts `noinline` on every function, so no inlining hazard fires in
   `.c` cases. `-O1 -Xclang -disable-llvm-passes` gives unoptimised IR
   without `noinline`.
3. **Passes that are not semantics-preserving rewrites of host code** show up
   in every P1 cell:
   - `metarenamer` renames the marker declarations themselves;
   - `dfsan` renames functions (`case_entry` disappears);
   - `hipstdpar-select-accelerator-code` deletes every host function;
   - `strip`/`strip-nondebug` erase local names (F2);
   - `asan`/`msan`/`hwasan`/`memprof`/`tysan` (20) and `instrumentor` (23)
     add `ptrtoint` everywhere.
4. **opt-errors.** These are all opt refusing or crashing, not legality
   failures:
   - LLVM 23 rejects `default<Os>`/`default<Oz>` ("no longer supported");
   - `select-optimize` segfaults standalone in opt-18 (3 cases);
   - `instcombine` aborts with "did not reach a fixpoint after 1 iterations"
     on `dbg-region-operands` on all three majors, also after
     `-strip-debug`, so it is not caused by the debug info.
     `instcombine<no-verify-fixpoint>` avoids it.
5. **`internalize`** needs `-internalize-public-api-list=case_entry`;
   otherwise `case_entry` is internalised and, after globaldce, deleted.
6. **Attribute parser glitch.** The harness `attributes_observed` lists
   `noundef 0`, `noundef 12`, `noundef 3`: the attribute parser is picking
   up the constant argument after `noundef`.
7. **Debug-info variants.** The `-g` variants parse and verify on 18/20/23.
   `default<O3>` with `-verify-each` passes on all three, and the O3 result
   with `-g` equals the O3 result without it (after `-strip-debug`,
   ignoring attribute-group numbering and predecessor order) on 18 and 23.
   The section 3 format says "no debug info"; the two `dbg-*` cases were
   added at the orchestrator's request.

## Probe cases and their questions

22 cases (16 `.ll`, 6 `.c`) are `EXPECT: probe`.

| Case | Question |
|---|---|
| region-mergefunc-twins | Is a thunk-to-twin an L4 failure, or acceptable (the plugin can follow the thunk, since it needs the callee IR anyway)? Must regions with identical bodies stay distinct (per-region budget tables are keyed by symbol)? |
| region-mergefunc-unnamed-addr | Same, when the marker *operand* is rewritten to the twin. rustc runs mergefunc with aliases on `unnamed_addr` functions. |
| region-inplace-selfinverse | A self-inverse `g` with `ginv` emitted separately: `ginv` becomes a thunk to `g`. Fine, or must `inplace` take one function when self-inverse? |
| region-internal-strip | Region identity cannot be a local symbol name (`strip`). What is the identity key? |
| region-iroutliner | Is a region whose body was outlined into `outlined_ir_func_N` still "the same defined symbol"? |
| region-switch-fnptr-table, region-select-two-way, region-fnptr-array-index, ipo-globalopt-region-bool, c-pie-reltable-region, dbg-region-operands | Which operand shapes must the plugin resolve: constant / select-of-constants / phi-of-constants / load-from-constant-table / other (load from a stack array; `llvm.load.relative`)? |
| cfg-sink-different-callees | Can a stock pass turn two direct marker calls into one indirect call? Seen: no (simplifycfg and gvn-sink both refuse a different callee; the same-callee twin sinks). Should the plugin still reject indirect marker calls fail-loud? |
| val-memcpy-handle-int, c-memcpy-handle-int, dbg-memcpy-handle-int | F1: must the dialect accept handles stored as integers in memory (`ptrtoint`+`store i64`, `load i64`+`inttoptr`) when LLVM, not the source, introduced them? |
| fp-rot-fmuladd-fold, fp-rot-nan-fold, fp-rot-fastmath-reassoc | F4: must `rot` angles be bit-identical across optimisation levels, or is the comparison baseline the optimised build? |
| c-is-constant-budget, c-objectsize-count | F4: marker operands computed from optimisation-dependent intrinsics. |
| c-pure-attr-wrapper | F5: must the dialect reject markers reachable from functions carrying `memory(none/read)`/`willreturn` attributes? |
| c-unprototyped-decl | K&R declarations give `declare void @__bennett_gate(...)` and per-call function types `(i32, ptr, i64, ...)`. O3 leaves them alone (seen on 18). Does "recognised by name and signature" accept variadic declarations and mismatched call types? |

## Case table

"Fired" gives the exact pass, and the major(s) on which it was seen to
change the module the intended way. Where the transformation is blocked by
marker opacity, the twin column shows the same pass firing when the
markers are `memory(none) nounwind willreturn`. Twins live in
`/tmp/bennett-corpus/twins/` and are not cases.

### Inlining and IPO (8)

| Case | Hazard | Fired (pass, major) | What changed | Twin evidence | Expect |
|---|---|---|---|---|---|
| inline-helper-markers | cgscc inliner on internal/external marker helpers, loop helper | `inline`, 18 | Three helpers inlined into `case_entry` (loop bodies with `gate` cloned); external `cx_ladder` kept | n/a | legal |
| inline-always-into-region | always-inline into a region body and into `case_entry` | `always-inline`, 18/20/23 (sweep) | `phase_kick` inlined at 3 sites and deleted | n/a | legal |
| inline-partial | partial inliner, guard inlined, body outlined | `partial-inliner -skip-partial-inlining-cost-analysis`, 18; at default cost: **no** (only lifetime decls added) | Guard inlined at 2 sites; markers moved into `@maybe_entangle.1.body` | n/a | legal |
| ipo-argpromo-dae | argpromotion (by-ref handle/index), deadargelim (unused arg and return) | `cgscc(argpromotion),deadargelim`, 18 | `@apply(ptr %hp.0.val, i64 %ip.0.val)` returning void; loads moved to callers | n/a | legal |
| ipo-ipsccp-funcspec-region | IPSCCP function specialisation on a constant region pointer | `ipsccp`, 18 | `@controlled.specialized.1/.2`; `__bennett_ctrl(..., ptr @rz/@rx, ...)` literal; indirect `call %f` becomes direct | n/a | legal |
| ipo-globalopt-region-bool | globalopt shrink-to-bool of a region-selecting index | `globalopt`, 18 | `@sel` becomes `i1`, `idx = zext i1`; region operand is a load from `@regions` (globalopt refuses to shrink a *pointer* global, so the index form is used) | n/a | probe |
| ipo-attributor-function-attrs | attributor, function-attrs on marker helpers next to a pure helper | `attributor`, 18: pure helper deleted, constant return 7 propagated, `noundef` added at marker call sites. `cgscc(function-attrs)`, 18: only `pure_helper` gets `memory(none) willreturn nounwind`; marker helpers get nothing | as described | the pure helper is the twin | legal |
| ipo-internalize-globaldce | internalize + globaldce/globalopt/DAE/ipsccp | `internalize,globaldce,globalopt,deadargelim,ipsccp -internalize-public-api-list=case_entry`, 18 | Regions internalised and kept; `@lib_never_called` deleted; `@lib_entangle` becomes `fastcc` | n/a | legal |

### Region identity and region operands (15)

| Case | Hazard | Fired (pass, major) | What changed | Twin evidence | Expect |
|---|---|---|---|---|---|
| region-mergefunc-twins | mergefunc on identical external regions | `mergefunc`, 18/20/23 | `@oracle_key2` becomes a thunk; direct call redirected (F2) | n/a | probe |
| region-mergefunc-unnamed-addr | mergefunc on `unnamed_addr` regions, with and without aliases | `mergefunc`, 18/20/23; `-mergefunc-use-aliases`, 18 | Marker operand becomes `@oracle_key1`; thunk or alias for key2 | n/a | probe |
| region-inplace-selfinverse | mergefunc on `inplace(g, ginv)`, g self-inverse; `compute` | `mergefunc`, 18 | `@xor_k_inv` becomes a thunk to `@xor_k`. `globalopt` does **not** add `unnamed_addr` to address-escaping regions (so no RAUW) | n/a | probe |
| region-hotcoldsplit | hotcoldsplit of a cold path holding markers and a ctrl call | `hotcoldsplit`, 18 | Cold block moved to `@case_entry.cold.1`, including `__bennett_ctrl(... @fixup_region ...)`; `minsize` added to the cold function | n/a | legal |
| region-iroutliner | iroutliner over two similar regions and `case_entry` | `iroutliner`, 18 | 4-marker sequence moved into `@outlined_ir_func_0`, called from both regions and `case_entry` | n/a | probe |
| region-internal-strip | internal region only referenced by a marker; DAE/globaldce/strip | `strip`, 18: renamed to `@1`. `globalopt,deadargelim,globaldce,function-attrs`, 18: region kept, arg only marked `nocapture readnone` | F2 | n/a | probe |
| region-switch-fnptr-table | sink + switch-to-lookup of the region per case | `default<O3>`, 18/20/23 (needs triple/datalayout); `simplifycfg<switch-to-lookup;sink-common-insts>` alone gives the phi | `@switch.table.case_entry [6 x ptr]` + load + phi (F3) | n/a | probe |
| region-select-two-way | if/else region per arm (adj); ctrl with handle+region differing; compute with both bregions differing | `default<O3>`, 18/20/23 | adj: `select`; ctrl and compute: **not** sunk, stay two direct calls. `gvn-sink`: no change | n/a | probe |
| region-fnptr-array-index | region from a constant table / stack array / mutable global table indexed by the input | `default<O3>`, 18/20/23 | All three remain loads; the stack array is not promoted | n/a | probe |
| region-ctrl-variadic | `__bennett_ctrl_v` with i64/ptr/double varargs, inlined helper, loop | `cgscc(inline)`, 18: helper inlined, variadic call type unchanged. `instcombine`: `nonnull` on varargs ptrs. `expand-variadics`, 23: no change | variadic call keeps `(ptr, i64, ptr, i64, ...)` | n/a | legal |
| region-recursive-tre | tailcallelim of a self-recursive region that also enters itself via ctrl | `tailcallelim`, 18 | Direct self-recursion becomes a loop; `__bennett_ctrl(... @walk ...)` kept, marked `tail`; `function-attrs` adds no `norecurse` | n/a | legal |
| region-env-escape | sroa/memcpyopt/gvn/dse/licm around an env escaping only into markers | `default<O3>`, 18 | `%tmp` and both memcpys removed (forwarded into `%e`); stores to `%e` kept before `__bennett_adj`; `out` reloaded after each call | n/a | legal |
| region-global-state | ipsccp/globalopt/globals-aa on a global written only inside a callback region | `default<O3>`, 18 | `%after = load @acc` kept after `__bennett_compute` | twin: `case_entry` folds to `ret i64 %x` (load forwarded, marker gone) | legal |
| c-pie-reltable-region | PIE module, switch of regions, rel-lookup-table-converter | `default<O3>`, 18/23: `@switch.table` built; reltable conversion: **no** (also with `-relocation-model=pic`) | F3 | n/a | probe |
| dbg-region-operands | `-g` variant: select + switch table + unrolled rot, verifier | `default<O3> -verify-each`, 18/20/23: ok; select and `@switch.table` formed; `-g` does not change the result | F3; also the instcombine fixpoint abort (harness note 4) | n/a | probe |

### CFG (6)

| Case | Hazard | Fired (pass, major) | What changed | Twin evidence | Expect |
|---|---|---|---|---|---|
| cfg-hoist-sink-common | hoist/sink identical and near-identical markers across a measurement diamond | `simplifycfg<hoist-common-insts;sink-common-insts>`, 18 | `gate(2,h,1)` hoisted above the branch; `gate(4,h,%ib.sink)` sunk with a phi; select formed | n/a | legal |
| cfg-sink-different-callees | qalloc/qborrow, qload/qstore diamonds; could a sink create an indirect marker call? | `gvn-sink` / `simplifycfg<sink-common-insts>`, 18/20/23: **no** (callee operand not phi'd) | none | same-callee twin (`twins/gvnsink.ll`): gvn-sink merges `qalloc(0,n)`/`qalloc(1,n)` into `qalloc(%.sink1, n)` on 18/20/23 | probe |
| cfg-switch-op-table | 7-arm switch of `gate` with constant ops | `default<O3>`, 18 | Arms emptied; one `gate(i32 %.sink, ...)` with a 7-way phi; the second marker of arm c5 stays in c5 | n/a | legal |
| cfg-jump-threading | correlated branches through a measurement and a flag | `jump-threading`, 18 | Static `gate` call sites go from 6 to 8 (`join.thread` clone) | n/a | legal |
| cfg-callsite-splitting | callsite-splitting of marker calls and of a helper | `callsite-splitting`, 18: helper `@apply_or_default` split into `ptr null` / `ptr nonnull %p` calls. Direct marker call sites: **not split** (the pass skips calls to declarations) | as described | n/a | legal |
| cfg-unreachable-after-marker | marker + `unreachable`, `__builtin_unreachable` idiom, noreturn helper | `default<O3>`, 18/23 | `never` and `die` paths deleted (assume, range folding); `bad: gate 99; unreachable` **kept** | twin (`willreturn nounwind` gate): `bad` path and `gate 99` deleted, branch becomes `llvm.assume` | legal |

### Loops (8)

| Case | Hazard | Fired (pass, major) | What changed | Twin evidence | Expect |
|---|---|---|---|---|---|
| loop-unroll-gates | full nest unroll, runtime unroll | `loop-unroll<O3>`, 18: 4x4 nest fully unrolled (16 `gate2`). `loop-unroll<O3;runtime>`, 18: 8x body + `rt.epil` remainder | as described | n/a | legal |
| loop-rotate-peel | rotate with a marker in the header; peel of an `i==0` condition | `loop(loop-rotate)`, 18: header `gate(1)` cloned into the guard. `loop-unroll<peeling>`, 18: `body.peel`, `llvm.loop.peeled.count 1` | as described | n/a | legal |
| loop-unswitch-nontrivial | unswitch on a classical flag and on a measurement | `loop(simple-loop-unswitch<nontrivial>)`, 18 | Loop cloned four ways (`loop.us.us`, ...) with frozen `%m.fr` | n/a | legal |
| loop-licm-invariant-marker | LICM on invariant gate/measure/qalloc | `loop-mssa(licm)`, 18 | Only `mul`/`and` hoisted; markers stay | twin: all markers removed from the loop, `measure` sunk to the exit (`%m.le`) | legal |
| loop-deletion-marker-only | indvars exit values + loop-deletion with a marker as the only effect; `mustprogress` | `loop(indvars,loop-deletion)`, 18 | Exit values rewritten to closed form; both loops **kept** | twin: both loops deleted | legal |
| loop-fuse-distribute | loop-fusion of adjacent marker loops; loop-distribute | `loop-fusion` (alone, or after `loop-simplify,lcssa,loop(loop-rotate)`), 18: **no** (0 changes). `loop-distribute`, 18: **no** | none | twin: all three loops fused into one; distribute splits l3 (`l3.ldist1`) | legal |
| loop-idiom-handle-table | memset/memcpy idioms on handle tables | `loop(loop-idiom)`, 18: `memset(%tab, 0, 64)` and `memcpy(%cpy, %tab, 64)`. O3 18/20/23: memcpy forwarded away, no `ptrtoint` | as described | n/a | legal |
| loop-vectorize-gates | LV/SLP on a gate loop and a handle-table copy | `loop-vectorize`, 18: **no** ("call instruction cannot be vectorized"). `slp-vectorizer`, 18: only with `-slp-threshold=-10` (`<2 x ptr>` load/store of handles; default cost 0 >= 0). O3, 18: full unroll of the 16-gate loop with ops folded from `@coef` | as described | twin with the call replaced by a store: LV vectorises (`<2 x i64>` reduction) | legal |

### Handles and values (6)

| Case | Hazard | Fired (pass, major) | What changed | Twin evidence | Expect |
|---|---|---|---|---|---|
| val-cse-duplicate-markers | early-cse/gvn/newgvn/instcombine on identical marker calls | each pass, 18: only `%i = and x, 0` folded into the gate argument; no marker commoned | as described | twin, `early-cse`: second qalloc, 2 gates, 3 measures deleted | legal |
| val-unused-results | dce/adce/bdce/instcombine on unused qalloc/measure/qborrow | `dce`/`adce`/`bdce`, 18: no change to markers | none | twin, `adce`: unused `qalloc` and `measure` deleted | legal |
| val-sroa-handle-table | SROA/DSE of handle tables, struct copy, global table by measurement | `sroa`, 18: record allocas promoted (struct copy gone). O3: dead overwritten store removed; dynamic-index tables stay allocas (no select form) | as described | n/a | legal |
| val-memcpy-handle-int | 8-byte memcpy of a handle | `instcombine`, 18/20/23 | F1 `ptrtoint` + `store i64` | n/a | probe |
| c-memcpy-handle-int | the same from C, plus a struct copy | O3, 18/20/23: `ptrtoint`. `lto<O3>`, 18: `ptrtoint`...`inttoptr` into `qfree` | F1 | n/a | probe |
| dbg-memcpy-handle-int | `-g` variant of the above | O3, 18: `%.cast = ptrtoint ..., !dbg`; verifies on 18/20/23 | F1 | n/a | probe |

### Measurement (3)

| Case | Hazard | Fired (pass, major) | What changed | Twin evidence | Expect |
|---|---|---|---|---|---|
| meas-repeat-until-success | bounded RUS loop exiting on a measurement | `default<O3>`, 18 | Loop fully unrolled to 8 `measure` call sites (one per try) | n/a | legal |
| meas-select-phi-switch | measurements into select/phi/switch | `simplifycfg<switch-to-lookup>`, 18 | Diamond becomes `select i1 %m0`; switch on `m1<<1|m0` becomes `@switch.table [3 x i64]` | n/a | legal |
| meas-speculation | speculation of pure code next to markers | `speculative-execution`, 18: `mul`/`add`/`lshr` hoisted, gates not. `simplifycfg`, 18: `spec.select` for the pure arm; marker arms keep their branches | as described | the pure arms are the twin | legal |

### Exceptions (1; `cfg-unreachable-after-marker` covers noreturn)

| Case | Hazard | Fired (pass, major) | What changed | Twin evidence | Expect |
|---|---|---|---|---|---|
| eh-invoke-markers | invoke of markers, cleanup pad with markers, helper inlined into an invoke site | `default<O3>`, 18/23 | Helper's 2 gates become `invoke`s; invoke to a trivial cleanup+resume pad becomes `call` (legal); real pad kept; 23 adds `range(i64 0, 2)` at call sites | twin (gate `nounwind`): gate invokes become calls | legal |

### Floating point (4)

| Case | Hazard | Fired (pass, major) | What changed | Twin evidence | Expect |
|---|---|---|---|---|---|
| fp-rot-exact-fold | exact fp folding after unroll | `default<O3>`, 18 | 8 rot angles constant-folded (e.g. `0xBFC0C152382D7365`); no fast-math, so must match | n/a | legal |
| fp-rot-fmuladd-fold | fmuladd fused fold | O3, 18; dynamic via stub and harness | F4 | n/a | probe |
| fp-rot-nan-fold | NaN sign/payload fold | O3, 18; dynamic | F4 | n/a | probe |
| fp-rot-fastmath-reassoc | reassoc/arcp | O3, 18: `fadd %a, 0.5`, `fmul %xf, 0x3FD5555555555555`; dynamic | F4 | n/a | probe |

### Optimisation-dependent arguments and front-end shapes (5)

| Case | Hazard | Fired (pass, major) | What changed | Twin evidence | Expect |
|---|---|---|---|---|---|
| c-is-constant-budget | `__builtin_constant_p` choosing budget and size | O3, 18 (ipsccp into the static helper, then fold); dynamic | F4 | n/a | probe |
| c-objectsize-count | `__builtin_dynamic_object_size` as qalloc width | O3, 18; dynamic | F4 | n/a | probe |
| c-pure-attr-wrapper | `pure`/`const` helpers calling markers | O3, 18; dynamic | F5 | n/a | probe |
| c-unprototyped-decl | K&R marker declarations | O3, 18: no rewrite of call types | variadic decls stay | n/a | probe |
| c-program-mixed | whole-program C | O3 and `clang-18 -O3 -flto`: no int casts. `load-store-vectorizer`, 18/23: F1 `ptrtoint` of the ancilla handle | as described | n/a | legal |

## Cases that would not fire (and why)

- **Blocked by marker opacity, with a firing twin:** `loop-licm-invariant-marker`,
  `loop-deletion-marker-only`, `loop-fuse-distribute` (fusion and
  distribution), `loop-vectorize-gates` (LV), `val-cse-duplicate-markers`,
  `val-unused-results`, `cfg-unreachable-after-marker` (the `bad` path),
  `eh-invoke-markers` (invoke to call), `region-global-state`.
- **Blocked by a pass's own rule:**
  - `cfg-sink-different-callees`: no pass sinks a different callee; the
    same-callee twin sinks.
  - `cfg-callsite-splitting`: marker call sites are skipped because the
    callee is a declaration; the helper call does split.
  - `region-select-two-way` parts b/c: SimplifyCFG does not sink when two
    operands differ.
  - `region-internal-strip`: deadargelim cannot touch an address-taken region.
  - `ipo-globalopt-region-bool`: globalopt does not shrink pointer globals,
    hence the index form.
- **Fires only with a flag:**
  - `inline-partial` (`-skip-partial-inlining-cost-analysis`);
  - `loop-vectorize-gates` SLP part (`-slp-threshold=-10`; the default cost
    is exactly 0);
- **Did not fire at all:**
  - `c-pie-reltable-region`: `rel-lookup-table-converter` on a
    function-pointer table;
  - `region-ctrl-variadic`: `expand-variadics` on 20/23 (x86-64 host,
    external variadic declaration).
