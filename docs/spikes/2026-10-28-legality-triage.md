# Legality spike — triage of four candidate findings (2026-10-28)

Scope: four candidate findings from the legality matrix (plan:
`2026-10-28-legality-spike.md`; harness: `corpus/legality/harness/NOTES.md`).
For each one the question is whether it is **(A)** an LLVM bug (a miscompile of
well-defined IR), **(B)** a defect in the case, **(C)** a harness artefact, or **(D)**
correct LLVM behaviour that the dialect spec must account for.

Method. Everything was reproduced independently of `run.py`. Cases were copied
to `/tmp/bennett-triage/`. `runtime/trace_rt.c` and `runtime/driver.c` were
compiled there with `cc -std=c11 -O0 -fPIC -c`. Builds used the harness link line
(`llc -O<n> -relocation-model=pic -filetype=obj`, then
`cc -no-pie -rdynamic x.o trace_rt.o driver.o -ldl`). Traces were compared
byte for byte against the untransformed `llc -O0` build. `replay` was not used,
and no repo file other than this one was written. The tools were the
`toolchains.toml` directories:

- LLVM 18.1.3 (system);
- LLVM 20.1.8jl (Julia 1.13.3);
- LLVM 23.1.1 (rustc 1.99.1).

All recorded harness artefacts that I checked agree with my reproductions:

- `transformed.ll` of `c5db1230…` and `d32055cc…` (both `__bennett_adj(@r_a)`, store deleted);
- `9deda4cf…` (both ctrl operands `@oracle_key1`);
- the `trace.diff` of `564a9580…` (`RET 606` → `RET 6`).

Which harness cells fail (P1):

| finding | case | majors | raw | post-O3 |
|---|---|---|---|---|
| 1 | ipo-globalopt-region-bool | 18, 20 (not 23) | `attributor` and `cgscc(attributor-cgscc)`: L1, L4, L5 | same |
| 2 | region-global-state | 20, 23 (no pass in 18) | `function(normalize)`: L1, L4, L5 | L4 only |
| 3 | region-mergefunc-unnamed-addr | 18, 20, 23 | `mergefunc`: L1, L4, L5 | same |
| 4 | cfg-switch-op-table | 18, 20, 23 | `function(structurizecfg)`: L1, L5 | L1, L5 |
| 4 | region-switch-fnptr-table | 18, 20, 23 | `function(structurizecfg)`: L1, L4, L5 | passes |
| 4 | region-recursive-tre | 18, 20, 23 | passes | `function(structurizecfg)`: L1, L4, L5 |

**Pipeline membership.** I ran `opt -passes=<P> -print-pipeline-passes` per
major for `default<O1|O2|O3|Os|Oz>`, `lto<O3>`, `thinlto<O3>`,
`lto-pre-link<O3>` and `thinlto-pre-link<O3>`. No pipeline on any major contains
`attributor`, `attributor-cgscc`, `mergefunc`, `normalize`, `structurizecfg` or
`lower-switch`. Two indirect routes exist:

- `openmp-opt` (in O1+) and `openmp-opt-cgscc` (in O2+) run the Attributor internally. They do so only for modules that use the OpenMP runtime, which marker modules do not.
- `mergefunc` joins the opt pipeline only with `-enable-merge-functions` (verified on 23). Front ends set this through `PipelineTuningOptions::MergeFunctions`.

**rustc 1.99** turns MergeFunctions on at opt-level 2, 3, s and z, in aliases
mode (shown below). **Julia**: `src/pipeline.cpp` on JuliaLang master adds
none of MergeFunctions, Attributor, IRNormalizer, StructurizeCFG, LowerSwitch or
OpenMPOpt. Julia's hand-built pipeline ignores `JULIA_LLVM_ARGS=-print-pipeline-passes`,
so I could not check the 1.13.3 binary directly; this conclusion comes from reading the source.

---

## Finding 1 — attributor on `ipo-globalopt-region-bool`: **(A) LLVM bug, fixed upstream, not in 23**

**Symptom (reproduced).** For x ≥ 10 the trace changes from `ADJ F:r_b` (GATE 21, GATE 22)
to `ADJ F:r_a` (GATE 20). This happens on 18 and 20, raw and post-O3, under both
`attributor` and `cgscc(attributor-cgscc)`. LLVM 23 transforms the case correctly.
The Attributor rewrites `@case_entry` to `call void @__bennett_adj(ptr noundef @r_a, ptr noundef null)`
and deletes `store i64 1, ptr @sel` from `@choose`.

**It has nothing to do with callbacks or escaped regions.** The hypotheses in
the brief were wrong: the Attributor does not assume that the function pointer
passed to `__bennett_adj` is never called, and it does not assume that the
unknown call leaves globals untouched. `@sel` is written by `@choose` *before*
the marker call, and the marker plays no part. Removing every marker reproduces
the bug. So does removing `@sel`, `@choose` and every call. Calling back an
escaped function from an unknown external declaration is ordinary IR semantics,
and the case relies on nothing else.

**Minimal reproducer** (`/tmp/bennett-triage/f1-repro4.ll`). The index is in bounds, so there is no UB:

```llvm
@tab = internal constant [2 x i64] [i64 100, i64 200]

define i64 @f(i1 %c) {
  %i = select i1 %c, i64 0, i64 1
  %p = getelementptr inbounds [2 x i64], ptr @tab, i64 0, i64 %i
  %v = load i64, ptr %p
  ret i64 %v
}
```

`opt -passes=attributor` on 18 and 20 produces `define noundef i64 @f(i1 %c) { ret i64 100 }`.
On 23 the function is left unchanged. Executed results:

| build | f(0) | f(1) |
|---|---|---|
| unoptimised | 200 | 100 |
| 18 + attributor | 100 | 100 |
| 20 + attributor | 100 | 100 |
| 23 + attributor | 200 | 100 |

`cgscc(attributor-cgscc)` gives the same results.

**Mechanism.** Release builds have no `-debug-only`, so I used
`-attributor-print-dep`, which works in release builds, plus option bisection.

1. AAPotentialConstantValues of the index reaches `{0, 1}`. In the case, the index is the load of `@sel`: the Attributor sees both the initialiser 0 and the store of 1 in `@choose`. So the index analysis is *correct*.
2. AAPointerInfo of `@tab` therefore records **two bins**, at offsets 0 and 8, each of size 8 (`[AAPointerInfo] … {flt:tab} … PointerInfo #2 bins`).
3. To simplify the load, `AA::getPotentialCopiesOfMemoryValue` calls `forallInterferingAccesses`. That call folds the two ranges into one hull with `RangeTy::operator&=`, giving offset 0, size 16. The hull and the type are then passed to `AA::getInitialValueForObj`.
4. In 18 and 20, `getInitialValueForObj` runs `ConstantFoldLoadFromConst(Initializer, i64, Offset=0)` without checking that the hull size (16) equals the store size of the type (8). It folds to element 0, so AAPotentialValues of `%v` becomes `{100}`.
5. The original load of `@sel` becomes dead. With no remaining reader, the store to the internal `@sel` is also dead and gets deleted. That is why the store disappears from `@choose`.

Option bisection agrees with this. The bug disappears with any of
`-attributor-max-potential-values=0|1`, `-attributor-max-iterations=1..3` or
`-attributor-max-potential-values-iterations=0`, all of which stop the index from reaching `{0,1}`.
It persists with `-attributor-simplify-all-loads=false` and with either setting of
`-attributor-assume-closed-world`.

**Known issue / fix.** Upstream llvm-project PR #151359, "[Attributor] Check range size before constant fold load",
merged 2025-10-25 as commit `09eea22`. It adds the guard
`if (StorageSize != RangePtr->Size) return nullptr;` to `getInitialValueForObj`;
current upstream source has it. Its date puts it in LLVM 22+, which fits 23
being clean. It was not backported to 18 or 20, and Julia's 20.1.8jl does not carry it.

**Related bug still open on 23.** Issue #234748 (open, `miscompilation`, `regression:17`):
"Load through a pointer with two possible offsets is folded to the low half of a wider store".
This is the same hull problem on the *written-value* path in `forallInterferingAccesses`.
Its reproducer (`/tmp/bennett-triage/f1-issue234748.ll`) gives `ret i32 3` instead of 7 on
**18, 20 and 23**. The Attributor is therefore not trustworthy on 23 either.

**Majors affected:** 18, 20 (the case); the sibling bug affects 18, 20 and 23.

**Pipelines:** not in any default pipeline of the three majors, not in rustc's, not in Julia's.

**Case:** no defect. One small wart: `@sel` is never reset between inputs, so the
case depends on input order (ascending inputs and `x > 9` make this harmless).

**Spec implication.** This is not a marker-semantics issue. The corpus found a
generic constant-table miscompile because markers made the wrong table entry visible.
The spec should list the module/CGSCC Attributor as **outside the supported
pipeline set** for 18 and 20 (and, given #234748, for 23 as well). The corpus should
keep the cell as a known-LLVM-bug entry that cites PR #151359 and #234748, rather
than as a legality failure of the ABI.

---

## Finding 2 — `normalize` (IRNormalizer) on `region-global-state`: **(A) LLVM bug, known and open**

**Symptom (reproduced).** On 20 and 23, raw: `RET 606` → `RET 6` (and 607 → 7, 611 → 11);
the marker sequence is unchanged. LLVM 18 has no `normalize` pass
(`unknown function pass 'normalize'`). IR after the pass:

```llvm
  store i64 %a0, ptr @acc, align 8
  call void @__bennett_compute(ptr @bump, ptr @peek, ptr null)
  call void @__bennett_qfree(ptr %"vl31633__bennett_qalloc(0, 2)")
  %"vl11330(@acc)"  = load i64, ptr @acc, align 8   ; was %before, ABOVE the compute call
  %"vl11330(@acc)1" = load i64, ptr @acc, align 8   ; %after
  %"op11194(vl11330, vl11330)" = sub i64 %"vl11330(@acc)", %"vl11330(@acc)1"
```

The `%before` load has been moved below the call that writes `@acc`, through the
escaped `@bump`.

**Callback-independent.** No unknown call is needed: the pass moves a load below a
store to the *same pointer*. Minimal reproducer (`/tmp/bennett-triage/f2-repro2.ll`):

```llvm
define i64 @f(ptr %p, i64 %x) {
  %a = load i64, ptr %p
  store i64 %x, ptr %p
  ret i64 %a
}
```

`opt -passes='function(normalize)'` on 20 and 23 produces:

```llvm
  store i64 %a1, ptr %a0, align 4
  %"vl…(%a0)" = load i64, ptr %a0, align 4
  ret i64 %"vl…(%a0)"
```

The function now returns the new value instead of the old one.
`/tmp/bennett-triage/f2-repro1.ll` shows the same with `load @g; call @ext(); load @g`.

**Mechanism.** `IRNormalizer::reorderInstructions` builds an order from the
"output" instructions (stores, calls, terminators) and moves each instruction's
operand tree next to its first user. It adds no memory-dependence edges, so loads
are free to sink below stores and calls. With `normalize<preserve-order>` on 23,
or `-norm-preserve-order` on 20, the reproducer and the case are both correct
(`RET 606/607/611`).

**Known issue.** llvm-project issue #236128, "[IRNormalizer] `normalize` moves a load below a store to the same address".
It is open, labelled `confirmed` and `miscompilation`, and has no fix PR yet. Its diagnosis matches the mechanism above.

**Post-O3 cells** fail only L4, and that is a harness artefact **(C)**. `@bump` and
`@peek` are `internal`, so `dladdr` prints `F?` already in the baseline. This
case's L4 fails in 1863 P1 cells with every pass, as NOTES.md already says. L1 passes
post-O3 because O3 has already folded `%before` to `%x`, which leaves nothing to reorder.
Separately from that, the case marks internal regions as `EXPECT: legal`; L4 can
never pass on it until the regions are made external (a small **B**-type wart in the case).

**Majors affected:** 20, 23 (the pass does not exist in 18).

**Pipelines:** none. IRNormalizer is a diffing and canonicalisation aid, not an optimisation.

**Spec implication.** None for the marker ABI. The spec should exclude
`normalize` without `preserve-order` from the supported set (or have the corpus mark it
"known LLVM bug #236128"). If the plugin or tooling ever uses IRNormalizer to compare
Bennett modules, it must pass `preserve-order`.

---

## Finding 3 — `mergefunc` on `region-mergefunc-unnamed-addr`: **(D) correct LLVM behaviour; the spec must account for it**

**Symptom (reproduced, all majors, raw and post-O3).** Both `__bennett_ctrl` operands become
`ptr @oracle_key1`, and the direct `call @oracle_key2` becomes `call @oracle_key1`.
`@oracle_key2` survives as a forwarding thunk (`tail call void @oracle_key1(ptr %0)`).
With `-mergefunc-use-aliases` it becomes `@oracle_key2 = unnamed_addr alias void (ptr), ptr @oracle_key1`.
The trace diff is exactly 16× `CTRL H0 0 F:oracle_key2 32` → `CTRL H0 0 F:oracle_key1 32`.
Every GATE, MEASURE and RET line is identical.

**Mechanism.** The two bodies are identical under FunctionComparator, so MergeFunctions
keeps one and redirects the other.

- **With `unnamed_addr`**, the address carries no meaning, so LLVM may replace *every* use, address-taken uses included (`replaceAllUsesWith`). That is what happens to the pointer passed to `__bennett_ctrl`. This is permitted IR semantics, not a bug.
- **Without `unnamed_addr`** (`/tmp/bennett-triage/f3-named.ll`), on all majors, with or without `-mergefunc-use-aliases`, only direct calls are redirected. The address-taken `ptr @oracle_key2` operand is **kept**, and `@oracle_key2` becomes a thunk; no alias is made, because aliasing would merge addresses. The trace is then identical. L4 still fails, by its own rule "thunk-to-other is rejected". That matches `control-region-twin` and is intentional.

**rustc 1.99 (LLVM 23).** `/tmp/bennett-triage/rust/twin.rs` passes two identical
`#[no_mangle] pub extern "C" fn`s, and two identical private `extern "C" fn`s, to an
extern `__bennett_ctrl`. rustc marks every function `unnamed_addr`, even at O0.

| rustc flags | result |
|---|---|
| `-C opt-level=0` or `1` | no merging |
| `-C opt-level=2`, `3` or `s` | `@oracle_key2 = unnamed_addr alias void (ptr), ptr @oracle_key1`; the private twin is deleted; both ctrl operands are merged (`select i1 %0, ptr @oracle_key1, ptr @oracle_key1`, `select … @…priv1, @…priv1`) |
| `-Z merge-functions=aliases` | same IR as plain O2, so aliases is the x86_64-linux default |
| `-Z merge-functions=trampolines` | ctrl operands still merged (RAUW because of `unnamed_addr`); `@oracle_key2` becomes a thunk |
| `-Z merge-functions=disabled` | operands preserved (`select … @oracle_key1, @oracle_key2`) |

`-C help` has no merge-functions switch. The only control is the unstable
`-Z merge-functions=disabled|trampolines|aliases` (or the target spec's `merge-functions`).
Notice that the redundant `select %c, @k1, @k1` survives: MergeFunctions runs after
the last InstCombine, so L6 still sees a "select of constants".

**Mitigation measured.** I gave the twins *distinct string function attributes*
(`"bennett.region"="key1"` and `"key2"`). That **blocks merging on 18, 20 and 23**, even with
aliases, because FunctionComparator compares attributes. Distinct **function metadata**
(`!bennett.region !{"key1"}`) does **not** block it.

**Majors affected:** 18, 20, 23; and rustc's own O2+ pipeline.

**Pipelines:** not in `default<O*>` or the LTO pipelines for opt. It is in rustc's
default O2/O3/Os/Oz pipeline (aliases mode). It is not in Julia's or clang's defaults.

**Spec implication (normative input).** Two regions with identical bodies have identical
quantum semantics, so the merge is *semantically* harmless for Bennett: the gate sequence
is unchanged. Only symbol identity is lost. The spec must therefore choose between two positions:

- **(a)** Region identity is the *body*, not the symbol. Anything keyed by region symbol (budgets, inverse pairing, oracle labels, diagnostics) must tolerate `@k2` → `@k1`, aliases and forwarding thunks. Consequently L4's "thunk-to-other" and "alias" rules should be relaxed to "resolves to a definition with an equivalent body".
- **(b)** Symbol identity is normative. The front end must then either not mark region functions `unnamed_addr`, which rustc cannot be told to do per function today, or attach a distinct per-region string function attribute, which demonstrably blocks MergeFunctions in all three majors. Function metadata is not sufficient.

Rust users would otherwise need `-Z merge-functions=disabled`, which is nightly-only.

---

## Finding 4 — `structurizecfg` on three cases: **(C) harness artefact (pass run without its preconditions); not a Bennett finding**

StructurizeCFG is a GPU, AMDGPU-oriented lowering pass. Its only in-tree client sets up
the CFG first. `AMDGPUTargetMachine.cpp`, in both the legacy and new PM, runs
`LowerSwitchPass` in `addCodeGenPrepare`. Then, in `addPreISel`, it runs in this order:

1. `AMDGPUUnifyDivergentExitNodes` (commented "StructurizeCFG won't recognize the multi-exit regions formed by them");
2. `FixIrreducible`;
3. `UnifyLoopExits`;
4. `StructurizeCFG`.

The pass's own source states only "single entry/exit region". It handles only `br`
terminators, silently ignoring `switch` (`analyzeLoops`: "TODO: support other terminators other than branches").
Older LLVM made LowerSwitch a required pass in the legacy PM; that dependency has since
moved to the AMDGPU pipeline. Evidence for the raw switch input on 23:

```llvm
  br i1 undef, label %c5, label %Flow
c2:
  call void @__bennett_gate(i32 9, ptr %h, i64 %qi)
  br i1 undef, label %c1, label %Flow4
```

The switch is replaced by `br i1 undef` chains. Results with `/tmp/bennett-triage/check.sh`
(full-input trace comparison; the lower-switch pass is spelled `lowerswitch` on 18 and `lower-switch` on 20 and 23):

| case | mode | structurizecfg alone | lower-switch, structurizecfg | full AMDGPU chain¹ |
|---|---|---|---|---|
| cfg-switch-op-table | raw / post-O3 | FAIL, all majors | PASS, all | PASS, all |
| region-switch-fnptr-table | raw | FAIL, all majors | PASS, all | PASS, all |
| region-switch-fnptr-table | post-O3 | PASS (O3 already made a lookup table, so no switch) | PASS | PASS |
| region-recursive-tre | raw | PASS | PASS | PASS |
| region-recursive-tre | post-O3 | FAIL, all majors | **FAIL, all majors** | PASS, all |

¹ The full chain is `function(lower-switch,mergereturn,fix-irreducible,unify-loop-exits,structurizecfg)`.
LLVM 23 has no `mergereturn`, so it was omitted there.
`function(unify-loop-exits,structurizecfg)` alone also passes the TRE case, as does
`function(loop-simplify,structurizecfg)`.

**The TRE post-O3 failure persists with lower-switch, because there is a second
precondition.** After O3, `@walk` is inlined into `@case_entry` as a rotated loop. That
loop has header `%more.i` and two exits: `%viactrl.i` from the header, and
`%walk.exit.loopexit` from the latch. `%walk.exit.loopexit` is also reached from
`%entry`, so the exit is not dedicated and the function is not in loop-simplify form.
StructurizeCFG emits the backedge as `br i1 true, label %Flow3, label %Flow`. The loop
therefore never iterates: the inner `CTRL F:walk` / `GATE` lines disappear and `RET` becomes an undef value.

Marker-free reproducer (`/tmp/bennett-triage/f4-repro2.ll`):

```llvm
declare void @use(i64)
define i64 @f(i64 %x) {
entry:
  %z0 = icmp eq i64 %x, 0
  br i1 %z0, label %exitA, label %more
latch:
  %z = icmp eq i64 %d1, 0
  br i1 %z, label %exitA, label %more
more:
  %d = phi i64 [ %d1, %latch ], [ %x, %entry ]
  %d1 = add i64 %d, -1
  %lo = and i64 %d, 1
  %even = icmp eq i64 %lo, 0
  br i1 %even, label %latch, label %side
side:
  call void @use(i64 %d1)
  br label %join
exitA:
  call void @use(i64 -1)
  br label %join
join:
  %r = phi i64 [ 0, %exitA ], [ %d1, %side ]
  ret i64 %r
}
```

With `structurizecfg`, alone or after lower-switch, the `use(...)` call disappears for even x ≥ 2, on 18, 20 and 23.
On 18 and 20, `f(4)` also returns 0 instead of 2. With `unify-loop-exits` or `loop-simplify`
first, the output is correct on every major. Strictly speaking, a pass that silently
miscompiles a multi-exit loop that is not in simplify form, with no assertion, is
a robustness bug in LLVM. But it sits outside the contract the pass's only client
establishes, and I found no upstream issue for it. A web search turned up only old
Bugzilla reports, 26925 and 41509, without matching details.

**Majors affected:** 18, 20, 23 (all of them, and only when the preconditions are skipped).

**Pipelines:** none of the host pipelines. It runs only in AMDGPU codegen, after its prerequisite passes.

**Spec implication.** None for the marker ABI. The harness should either run
`structurizecfg` only together with its prerequisite chain, or tag such cells
"precondition-violating pass", alongside the instrumentation and target passes
NOTES.md already lists. The plan's §5 "every advertised pass at its defaults"
needs a precondition carve-out for lowering utilities: structurizecfg, and probably
`unify-loop-exits` itself, which asserts on switches.

---

## 5. iroutliner + attributor, LLVM 23 (`c-program-mixed`, P3 seq-0082): **(A) Attributor bug; IROutliner is innocent; all majors**

**Symptom (reproduced).** Input:
`results/raw/modules/23/f3774bad…/module.bc`, copied to `/tmp/bennett-triage/f5/in.bc`.
Region-marker call sites (ctrl, adj, compute, reversible, inplace) after each pipeline:

| pipeline | region-marker call sites |
|---|---|
| `iroutliner` alone | 3 |
| `attributor` alone | 3 |
| `iroutliner,attributor` | 0 |

The same happens on **18, 20 and 23**. I started instead from the case source compiled
the harness way (`clang-18 -O0 -Xclang -disable-O0-optnone -emit-llvm -S c-program-mixed.c`)
and ran `opt -passes=iroutliner,attributor` with each major's opt; the counts are again
3 / 3 / 0. The baseline trace for x=5 runs `QALLOC H0..H3`, then `QBORROW H4`, then `CTRL …`.
The transformed program never leaves the first loop: it prints `QALLOC H0, H1, H2, …` without end.

**What IROutliner does.** It outlines the `i++` of the handle-table fill loop
(`for (i = 0; i < 4; i++) env.h[i] = __bennett_qalloc(0, 1);`) and of a second loop into

```llvm
define internal void @outlined_ir_func_0(ptr %0) {   ; minsize optsize
  ...
  %2 = load i32, ptr %0
  %3 = add i32 %2, 1
  store i32 %3, ptr %0
  br label %.exitStub, !llvm.loop !26
.exitStub:
  ret void
}
```

The loop body becomes `…; call void @outlined_ir_func_0(ptr %4); br label %13`. That IR is well-defined:

- `opt -passes=verify` accepts it.
- The loop still has its latch in the caller.
- The loop terminates (i < 4) and calls the side-effecting `__bennett_qalloc`, so the `llvm.loop.mustprogress` metadata licenses nothing.
- The misplaced `!llvm.loop` on the outlined function's branch is irrelevant. Stripping it gives the same result: 0 region markers after `attributor`.

**What the Attributor does.** It folds the loop-header test `load i32 %4 < 4` to `true`,
because it sees only `store i32 0`. The loop becomes infinite, the exit edge and
everything after it become `unreachable`, and `case_entry` is marked `noreturn`. The
`outlined_ir_func_0` it calls *is* correctly annotated
`memory(argmem: readwrite)`; the increment is simply not treated as a write that reaches the header load.

**Marker-free reproducer** (`/tmp/bennett-triage/f5/r2.ll`):

```llvm
define internal void @inc(ptr %p) {
  %v = load i32, ptr %p
  %v1 = add i32 %v, 1
  store i32 %v1, ptr %p
  ret void
}

define i32 @f() {
entry:
  %a = alloca i32
  store i32 0, ptr %a
  br label %loop
loop:
  %v = load i32, ptr %a
  %c = icmp ult i32 %v, 4
  br i1 %c, label %body, label %exit
body:
  call void @inc(ptr %a)
  br label %loop
exit:
  ret i32 %v
}
```

Unoptimised, `f()` returns 4. After `opt -passes=attributor`, on **18, 20 and 23**:

```llvm
loop:
  br label %body
body:
  call void @inc(ptr noalias nofree noundef nonnull writeonly align 4 captures(none) dereferenceable(4) %a)
  br label %loop
exit:                                             ; No predecessors!
  unreachable
```

Executed, the result loops forever (stopped by an `alarm`) on all three majors. On 23 the
call-site argument is even marked `writeonly`, although `@inc` reads it. The bug does not
depend on `internal` (an external `@inc` behaves the same). It also needs no
outliner: any loop whose induction variable lives in memory and is updated by a
non-inlined callee triggers it. The same loop with the increment inline (`r5.ll`)
compiles correctly, which is why `attributor` alone on the original module is harmless.

**Mechanism** (`-attributor-print-dep`, LLVM 23). The final state has:

- AAPotentialValues `{i32 0}` for the header load;
- `{i1 true}` for `%c`;
- the header load `assumed-dead`, because `exit` is unreachable.

Liveness of the store in the callee is **not** the cause. In `r6.ll` the callee's
store has a live reader in the loop body (`%x = load %a; call @sink(i32 %x)`), and
`AAIsDead` reports that store `assumed-live`. Even so, both loads fold to 0 and
the program calls `@sink(i32 0)` on every iteration, on all three majors. So
AAPointerInfo is wrongly answering *reachability*: it does not count the callee's store as an
interfering write for the header load, which it reaches by returning to the
call site and taking the back edge.

This matches the diagnosis in llvm-project issue **#236104**, "[Attributor] Incorrect loop-counter simplification".
That issue is open, labelled `confirmed`, `miscompilation` and `regression:18`, with candidate fix PR #236114, also open.
Its diagnosis: `AAIntraFnReachabilityFunction::updateImpl` clears its dead-edge and dead-block
assumptions without returning `CHANGED`. Dependents therefore keep a "not reachable" answer
computed while the loop body was still assumed dead. Its C reproducer
(`compare("abX","abY",2)` should exit 0) exits 1 after `attributor` on 18, 20 and 23 here.
I could not apply PR #236114 (I have no LLVM source build), so "same root cause as #236104" is
**likely but unconfirmed**. It is **not** #234748 (the offset-hull bug of finding 1) and not
the bug fixed by #151359, since 23 is affected.

**Majors affected:** 18, 20, 23.

**Pipelines:** neither `iroutliner` nor `attributor` / `attributor-cgscc` is in
`default<O2|O3|Os|Oz>`, `lto<O3>`, `thinlto<O3>` or `lto-pre-link<O3>` on any major.
Both are opt-in only: `-ir-outliner` adds `iroutliner` to the pipeline (verified on 23), and
`-attributor-enable=module|cgscc|all` does the same for the Attributor. Neither is in rustc's
or Julia's pipelines. The AMDGPU backend's `amdgpu-attributor` is a separate, target-only pass.
So the default pipelines are unaffected. But *any* user who enables the Attributor gets
this miscompile on ordinary loops; it does not need IROutliner or markers.

**Spec implication.** None for the marker ABI. It adds to finding 1: the Attributor
(module and CGSCC) must be listed as unsupported on **all three** majors, not just 18
and 20. The P3 cell should be filed as a known-LLVM-bug entry citing #236104/#236114.

---

## Summary

| # | pass | verdict | one-line reason | majors | in a default pipeline? |
|---|---|---|---|---|---|
| 1 | attributor / attributor-cgscc | **A** | constant-table load at offsets {0,8} folded to offset 0 (`getInitialValueForObj` missing a size check; fixed by PR #151359, LLVM 22+); sibling #234748 still open on 23 | 18, 20 (sibling: all) | no (only via openmp-opt on OpenMP modules) |
| 2 | normalize | **A** (post-O3 L4: **C**) | IRNormalizer reorders loads below stores and calls with no memory dependences; issue #236128 open; `preserve-order` avoids it | 20, 23 | no |
| 3 | mergefunc | **D** | `unnamed_addr` makes the address meaningless, so RAUW of the region pointer is legal; without it LLVM keeps the address and makes a thunk; rustc O2+ runs it in aliases mode and merges the passed pointers | 18, 20, 23 | **yes, rustc O2/O3/Os/Oz**; not opt, clang or Julia |
| 5 | iroutliner + attributor (P3) | **A** | Attributor ignores a loop counter's increment once it lives in a callee (IROutliner merely moves it there), so the loop header folds to `true` and the loop never exits; likely #236104 (open); marker-free reproducer | 18, 20, 23 | no (both opt-in only) |
| 4 | structurizecfg | **C** | run without its AMDGPU-pipeline preconditions (lower-switch, plus unify-loop-exits for multi-exit loops); passes with the chain | 18, 20, 23 | no |

Implications for the dialect spec:

- Findings 1, 2 and 5 are generic LLVM miscompiles. The spec's supported-pipeline statement must exclude them by name and major, rather than treating them as ABI legality failures. Because of finding 5 and #234748, the Attributor is unsupported on all three majors.
- Finding 3 is the one normative item. Decide whether region identity is the body or the symbol. If it is the symbol, require a distinct per-region string function attribute (shown to block MergeFunctions on all three majors) or forbid `unnamed_addr` on regions. If it is the body, relax L4 to accept aliases and thunks.
- Finding 4 is a harness-policy fix: run lowering utilities only with their prerequisites.
