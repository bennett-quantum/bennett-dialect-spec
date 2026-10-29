# Harness notes — 2026-10-28

Run from the repository root, with Python 3.11+ and the configured LLVM installations:

```sh
python3 -m unittest discover -s corpus/legality/harness -p 'test_*.py'
python3 corpus/legality/harness/run.py controls --majors 18,20,23
python3 corpus/legality/harness/run.py baseline --majors 18,20,23
python3 corpus/legality/harness/run.py matrix --majors 18,20,23 --suites P1,P2,P3 --jobs 12 --p3-seqs 200 --seed 20261028
python3 corpus/legality/harness/run.py report
python3 corpus/legality/harness/run.py replay FAILURE_ID
python3 corpus/legality/harness/run.py minimize FAILURE_ID --seconds 45
```

`--cases` accepts an id, filename, or legality-relative glob and may be repeated.
For example, `--cases 'seed-*'` selects the three harness-owned seed cases;
`--cases 'cases/*'` selects the adversarial corpus. Each command snapshots its
selection and sources. Later files require another run. `--suites P4 --majors 18`
selects the optional C front-end/LTO path; it requires at least one C case.

No commits were made. Only the authorized harness/runtime/control/results paths
were written. The explicit ownership restriction supersedes CLAUDE.md's general
worklog instruction; this file records this session's decisions and surprises.

## Runtime and protocol

The ABI is the plan's provisional ABI, with no added marker attributes. The
runtime and driver are compiled separately by system `cc -O0`; LLVM never sees
their definitions. Native links use system `cc -no-pie -rdynamic ... -ldl`.

Each marker prints its uppercase name followed by its arguments in ABI order.
Handles use zero-based per-input allocation ordinals (`H0`, `H1`, ...). Invalid
or freed handles print `BADHANDLE`. Each allocation receives a distinct 4096-byte
slot in a 256 MiB `PROT_NONE` mapping. A fault anywhere in that mapping prints
`FAULT handle-deref` and exits 86; another SIGSEGV prints `FAULT host-segv` and
exits 87. Exhausting the 65,536 slots is a loud runtime error.

Function-pointer arguments print `F:<dladdr defining symbol>`; an unresolved
pointer prints `F:F?`. `dladdr` must identify the exact start address. Environment
addresses are omitted. Doubles print `0x` and exactly 16 hexadecimal bit digits,
including signed zero and NaN payloads. `MEASURE` also records its ordinal and
returned bit. Its SplitMix64-derived bit depends only on the signed input's bit
pattern and the measure-call ordinal.

Region calls have one opening marker line and an `END <MARKER>` line after the
specified calls: ctrl/adj/reversible call once, compute calls f/use/f, inplace
calls g only. The variadic ctrl probe is traced without forwarding varargs or
calling its function pointer. The driver emits `IN` and `RET`, resetting runtime
state for each input. Stdout is unbuffered for signal-safe fault traces.

Successful inputs are batched into one process. After a non-timeout failure,
remaining inputs are resumed in a fresh process, so an early guard fault does
not silently erase later input coverage. An execution timeout is a failure;
remaining unexecuted inputs are explicitly recorded rather than called passes.

## Checks and execution

L1 compares transformed llc-O0 trace bytes and classical returns against raw
llc-O0. L5 additionally does llc-O3, compares that trace, and checks `nm -u` on
both objects for every marker actually called in the baseline. The runtime's
marker definitions are separate from these objects. Build/link failures are
L5 findings, not optimizer refusals and not passes.

L2 resolves attribute groups from llvm-dis text and checks declarations and
individual call sites separately. Declaration attributes cannot mask an added
call-site attribute. Existing forbidden attributes are reported as such; only
new forbidden attributes fail L2. Post-O3 P1 cells compare against raw baseline
and record the immediate input comparison too, so O3 additions cannot disappear
from the evidence. Site correspondence uses marker, containing function,
argument spelling and occurrence; transformed/duplicated sites with no matching
function fall back to that marker's baseline call sites. This textual matching
is conservative rather than a source-location proof. Parameter/return attributes
are observations too. The forbidden set is exactly the plan's set.

L3 dynamically checks both native traces for BADHANDLE/guard faults. The static
review flags added ptrtoint/inttoptr instructions, without failing a cell solely
for those flags. Handle-touching functions are conservatively connected through
direct calls, function-pointer references, and shared globals. This can overflag
unrelated casts in the same connected component; it is not complete handle-flow
verification. Report generation recalculates those observations from retained IR.

L4 compares all dynamically observed region symbol arguments, including the
inverse/use pointers that the runtime need not execute. Each symbol must be a
function definition in the transformed module. A one-call forwarding definition
to another defined function is rejected as a thunk, as are aliases and declarations.
More complicated wrappers are not proved equivalent or proved non-thunks.

P1 parses IR pass sections, including LoopNest and parameterized sections, but
excludes analyses and machine passes. Parameter defaults use the bare name;
`print<analysis><options>` retains `print<analysis>`. LICM and LNICM use loop-mssa.
P1 executes each advertised pass on raw and post-default-O3 modules. P2 has all
11 specified pipelines. P3 records 200 sequences per case/major, each of length
5–40, sampled from passes not rejected by P1 on the selection. Effective seed
is the requested seed plus the major. A later sequence can still fail due to
interactions; that outcome is recorded.

A 12-worker process pool evaluates cells. Module content hashes use llvm-dis
text with only its path-dependent ModuleID removed. Distinct bitcode encodings
with identical printed IR therefore share a module, native builds and executions.
File locks prevent concurrent duplicates. Native cache keys include major/tool
identity, runtime contents and all input values. Both success and failure results
are cached. Replay explicitly invalidates the transformed module's native cache.

Every completed matrix cell has one JSONL record. An internal Python exception
stops the run loudly; it is never downgraded to opt-error. Reports use the latest
record for a logical cell and exclude the superseded v1 development run. Historic
raw evidence remains on disk. P3 sequence indices identify logical cells across
reruns, even if the eligible population changes.

Raw runs, sources, tool catalogs, command stdout/stderr, bitcode, disassembled IR,
objects and traces are under gitignored `results/raw/`. Every failed check keeps
`transformed.ll`, `trace.diff`, `task.json`, and `result.json`. JSON command records
include argument vectors, shell-display commands, cwd, exit status and timeouts.
REPORT.md indexes every failure; summary.json has counts and compact details.

## Red gates and surprises

* Runtime tests were written and observed failing before implementation. They
  cover guard faults, canonical handles, double bits, region execution, reset,
  invalid/freed handles, and driver input rejection. Synthetic L2/L3/L4/pass-list
  tests likewise failed before `run.py` existed.
* `control-memory-none`: memory(none), nounwind, willreturn on a repeatedly used
  measurement causes O3 to CSE/delete measurements. All majors fail L1 and L5;
  L2 records the preexisting forbidden attributes. The first version used an
  unused void gate: llc-O0 itself removed it, so the control unexpectedly passed.
  This was a defective control, not a reason to weaken L1. Returning and using
  the measurement result makes the llc-O0 baseline retain the calls.
* `control-readonly`: readonly measurement in a loop, with nounwind/willreturn,
  hoists under `function(loop-simplify,lcssa,loop-mssa(licm))`. All majors fail L1
  and L5. Canonical LLVM prints readonly as memory(read); L2 notes it existed
  before the pass.
* `control-handle-deref`: a volatile host load from an allocated handle faults
  with status 86. All majors fail L3 (and L1/L5 for abnormal execution), even for
  no-op-module. Matching faulty traces never count as passes.
* `control-region-twin`: mergefunc retains twin_b's name but replaces its body
  with a forwarding thunk to twin_a. All majors fail L4. Comparing only runtime
  symbol names would incorrectly pass this control. LLVM reduction of the LLVM-18
  control reproduced the same checks after dropping an unneeded free.
* LLVM-23 rejects default<Os> and default<Oz>, explicitly recommending O2 with
  optsize/minsize instead. Those requested pipelines stay opt-error. Likewise,
  required-parameter passes with no accepted bare default remain opt-error.
* Many advertised instrumentation, GPU/target, and internalization passes need
  an environment other than this standalone host ABI. Missing sanitizer/profile
  runtimes or an internalized/deleted case_entry are L5 findings. They prevent an
  unconditional all-pass green result even on tiny legal seeds. They are not
  silently excluded from P1 or P3.
* A cfg-switch-op-table finding under structurizecfg was manually inspected:
  the transformed input contains `br i1 undef` and loses gates/results. On LLVM 18,
  `function(lowerswitch,structurizecfg)` passes the same trace comparison. Thus the
  raw single pass lacks a switch-lowering prerequisite; this is evidence against
  indiscriminately applying every advertised pass, not a quantum-specific bug.
  The spelling `lower-switch` was first tried and rejected on LLVM 18; that major
  calls the pass `lowerswitch` (LLVM 23 uses `lower-switch`).
* Internal region functions cannot be resolved by dladdr even with -rdynamic.
  Some corpus baselines therefore already contain F?, including legal-labeled
  cases with internal outlined bodies. Those L4 failures must be read as baseline
  observability limitations, not automatically as pass-induced symbol changes.
* A synthetic regression found that L3-static originally followed only direct
  callees, missing a region passed as a pointer and a helper reading a saved
  global handle. The red regression was observed, then both paths were connected.
* A manual success spot-check confirmed seed-loop's O3 output has four measure
  call sites instead of one; both native optimization levels still produce
  byte-identical traces across its eight inputs. Replay of the memory-none
  control reproduced FAIL:L1,L5 with the recorded optimizer command.
* No LLVM-18 lld is installed. Optional P4 uses the configured LLVM-20 lld with
  clang-18 bitcode and system cc as the link driver; it records that exact command.
  A real C fixture passes this path and checks saved post-LTO bitcode and nm.

## Limits and reduction policy

The corpus explores finite input sets and seeded pass compositions; it is not a
proof over all LLVM programs, all inputs, or arbitrary pass sequences. Internal
symbols and exotic symbol spellings can limit dladdr-based region observation.
No support for execution of foreign target code is claimed. Debug/GUI passes can
write their own side files; they run in cell directories with displays removed.
Core files are disabled. Tool refusals/crashes/timeouts are retained.

The reducer minimizes pre-pass input and reapplies the actual failing pipeline;
it does not merely delete trace calls from already transformed output. It
requires the same failed checks and a valid, nonfaulting baseline (except the
intentional handle-load control), and preserves L2 marker/attribute signatures.
LLVM-23 has no llvm-reduce installed, so its LLVM-18 source inputs can be reduced
using LLVM-18's reducer with LLVM-23 still running the interestingness check.
Reducer candidates have a shorter execution timeout and remain in the reducer's
process group so bounded cancellation also kills nested tools. Reduction is
bounded, not a claim of global minimality. Native dependency failures and every
random-sequence duplicate are not individually reduced. Reduction status and
verified reproducers are reported explicitly; a timeout is never called a
successful reduction.

# Harness notes — 2026-10-28 (second implementer, `legality-harness-v3`)

Took over the v2 harness mid-run. The v2 record above is kept as written; this
section records what changed and why. `VERSION` is now `legality-harness-v3`;
reports read only v3 records (v2 raw evidence stays on disk). Every change below
has a regression test in `test_fixes_v3.py` (or an updated `test_runtime.py` /
`test_controls.py`) that was observed failing before the fix.

## Changes

1. **Region symbols (was ~15k spurious L4 `F?`).** The runtime no longer calls
   `dladdr`; it prints `F@0x<addr>`. Links are `-no-pie` (the harness now asserts
   `ET_EXEC`), so the harness resolves each address against the executable's full
   symbol table from `llvm-nm -n --defined-only` (local `t` symbols included) and
   writes a canonical trace (`*.canonical.trace`; the raw one is kept). Every name
   starting at the address is printed, sorted and `=`-joined (an alias set);
   `F:F?` now means the address is not the start of any text symbol — a real
   finding, not an observability gap. L4 requires at least one name of the set to
   be a `define` and none of the defined names to be a forwarding thunk.
   After the fix, all 63 baselines on 18/20/23 contain no `F?` and agree.
2. **`nm` on fat objects (the 82 `embed-bitcode` L5 cells).** GNU nm 2.42 loads
   the bfd LLVM plugin; for an object with a `.llvm.lto` section it tries to read
   the embedded IR ("input module has no datalayout") and prints "no symbols".
   Harness artefact, not a finding. Marker imports are now read with the matching
   major's `llvm-nm`, which reads the ELF symbol table.
3. **`env-error` outcome, decided from tool evidence only** (`env_evidence_link`,
   `env_evidence_llc`). Link: every line of the *full* ld stderr must be an
   undefined reference (`undefined reference to`, `more undefined references to
   … follow`, `hidden symbol … isn't defined`) to an instrumentation-runtime
   symbol (`__asan_ __msan_ __tsan_ __hwasan_ __dfsan_ __memprof_ __nsan_ __rtsan_
   __tysan_ __ubsan_ __sanitizer_ __sancov_ __cfi_ __safestack_ __xray_
   __llvm_profile_ __llvm_ctx_profile_ __llvm_gcov_ llvm_gcda_ llvm_gcov_
   __poison_checker_ __instrumentor_ _Unwind_SjLj_`), or `case_entry` when the
   transformed module has no externally visible `@case_entry`. Two companion
   lines are accepted only with their cause present: `final link failed: bad
   value` after a hidden-symbol line, and `relocation truncated to fit` when the
   module references `@__hwasan_*` (HWASan's tagged globals on x86-64). llc: the
   module still calls `llvm.instrprof.*` and llc fails in instruction selection
   (`Cannot select: intrinsic %llvm.instrprof.*`, or LLVM 23's message-less crash
   in "X86 DAG->DAG Instruction Selection"); those intrinsics need the
   `instrprof` IR lowering pass, which llc does not run. Never env-error: any
   undefined `__bennett_*` symbol, any other undefined symbol, any other ld/llc
   diagnostic, a missing marker import in the object, or any other failed check
   (trace difference, fault, BADHANDLE, forbidden attribute). Each env-error cell
   records `env_evidence` (rule, stage, symbols/intrinsics) in its result.json.
   First implementation classified from a 20 kB stderr excerpt; a truncated last
   line of an `instrumentor` link log then looked like an unknown error. It now
   always reads the complete stderr file.
4. **`non-preserving` outcome (documented list, confirmed per cell).** Only for
   single-pass P1 cells of exactly these passes, and only when the transformed
   module shows the documented behaviour:
   - `metarenamer` — renames every non-intrinsic, non-libcall function, including
     the marker declarations and `@case_entry` (confirmed: marker names gone and
     no external `@case_entry`). It is an anonymising debug pass.
   - `dfsan` — DataFlowSanitizer without an ABI list wraps/renames every function
     with a `.dfsan` suffix, markers included (`__bennett_gate.dfsan` undefined at
     link). Confirmed by `@__bennett_*.dfsan` / `@case_entry.dfsan` in the module.
   - `hipstdpar-select-accelerator-code` — keeps only accelerator kernels and
     deletes all host code (confirmed: no `@case_entry` definition left).
   Sanitizers whose only failure is the missing runtime fall under env-error by
   evidence instead. L3-static flags (sanitizers add ptrtoint everywhere) of
   env-error/non-preserving cells are reported in a separate bucket.
5. **`precondition` outcome.** `structurizecfg` expects no `switch`, a
   reducible CFG and single-exit loops; its in-tree user (AMDGPU) runs
   `lowerswitch`, `fix-irreducible`, `unify-loop-exits` first. Evidence that
   `lowerswitch` alone is not enough: `region-recursive-tre` after `default<O3>`
   (tail recursion turned into multi-exit loops, no switch) loses whole CTRL
   regions under `structurizecfg` and under `lowerswitch,structurizecfg`, but
   passes under `fix-irreducible,unify-loop-exits,structurizecfg`. Rule: a failing
   P1 structurizecfg cell is `precondition` only if (a) running the prerequisite
   chain alone changes its input module (the input violated the expected form)
   and (b) `function(<lowerswitch>,fix-irreducible,unify-loop-exits,structurizecfg)`
   passes every check (`lowerswitch` on 18, `lower-switch` on 20/23). Otherwise
   FAIL. Both runs are recorded (`precondition.raw_checks`, `.violated`, `.rerun`).
   The main matrix ran with the first version (lowerswitch only, switch-based
   violation check); the structurizecfg P1 cells were then re-evaluated with
   `matrix --suites P1 --p1-passes structurizecfg`, which supersedes them.
6. **L6** (`region_operand_shapes`, `check_l6`): every function operand of
   ctrl/adj/compute/reversible/inplace/ctrl_v at each call/invoke site, classified
   `const`, `select-of-consts`, `phi-of-consts`, `load-from-const-table` (load
   through a GEP of / directly from a `constant` global whose elements are all
   function symbols), `select-of-mixed` / `phi-of-mixed` (added: every incoming
   value statically resolvable, not all constants; LLVM produces
   `phi [%switch.load, …], [@f, …]`), or `other`. "Introduced" = a non-const
   (marker, operand, shape) count that grew relative to the cell's *input* module.
   L6 never changes a cell outcome; `other` sites are listed as findings.
7. **C front end.** `.c` cases now compile with `clang-18 -O1 -Xclang
   -disable-llvm-passes` (the corpus agent found that `-O0 -disable-O0-optnone`
   puts `noinline` on every function, so no inlining hazard in a .c case could
   fire). Verified: no `noinline`/`optnone`, unoptimised IR; baselines still agree.
8. **Attribute parser.** `noundef 0` etc.: the token regex attached any trailing
   integer to an attribute, swallowing the next call argument. Only `align N` /
   `alignstack N` take a bare integer now.
9. **P1 variants**, beside the bare cells: `internalize` with
   `-internalize-public-api-list=case_entry` (bare internalize internalises the
   entry → env-error `entry-not-external`) and `function(instcombine<no-verify-fixpoint>)`
   (bare instcombine's fixpoint verification aborts on `dbg-region-operands`).
   Cells carry `opt_args`; logical cell keys include them.
10. **P3 population** excludes passes that were opt-error, env-error,
    non-preserving or precondition on any selected case in P1 (they would only
    repeat that known outcome in most sequences: v2's P3 was ~2/3 FAIL from
    instrumentation passes). Genuine P1 FAIL passes stay eligible. The excluded
    set per major is written to `runs/<id>/p3-excluded-<major>.json`.
11. **Baseline gate.** `baseline` exits 1 on any case error, cross-major
    disagreement, or any baseline issue (F?, missing marker import, fault) except
    the intentional handle-deref control's L1/L3.
12. Native cache key now includes `NATIVE_SCHEMA`; the fail-loud KeyError on a
    stale cache record (missing `diagnostic_path`) showed it was needed.
13. REPORT.md/summary.json restructured: corpus-only matrix first; seeds and
    controls separately (controls as detected yes/no per check); P2 per case;
    distinct FAILs deduplicated by case+pass+check signature with reproducer,
    diagnosis and trace-diff head; L2 observations; L3-static (two buckets); L6
    shape table and `other` findings; env-error rule with grouped evidence.
14. **Inherited failures.** The first v3 run (stopped after ~25k LLVM-18 P1
    cells) showed probe cases whose `default<O3>` output already changes the trace
    (fp-rot-*, c-pure-attr-wrapper, c-objectsize-count, c-is-constant-budget):
    every post-O3 cell then FAILs, ~300 per case per major, regardless of the pass.
    `fp-rot-fastmath-reassoc` additionally FAILs L5 in *every* cell because the
    untouched module under `llc -O3` already differs. These stay FAIL (they are
    findings), but a cell now carries `inherited` when everything the dynamic and
    L4 checks observe (per level: build stage, trace digest, exit, marker imports,
    L4 issues) is identical to that of its own input module and no forbidden
    attribute was added relative to the input. The report groups inherited FAILs
    per case, so each such finding appears once instead of once per pass. Baselines
    now also build `llc -O3` and record `llc_O3.trace_equal` (reported, not a gate).
15. **P3 grouping in the report.** A P3 FAIL whose sequence contains a pass that
    FAILs alone in P1 on the same case/major is grouped per (case, checks) with
    per-pass counts; a sequence with no such pass is listed individually and
    marked **interaction**. (Cells and outcomes are unchanged.)
16. **L6 stale-cache surprise.** The static-analysis cache is keyed by module
    pair only. The smoke run populated it before the quoted-name and
    `*-of-mixed` L6 fixes, and the full run reused those entries for the four
    smoke cases on LLVM 23 (showing `other` only on 23). The cache key now has
    `STATIC_SCHEMA`, and `report` recomputes L6 from the retained IR with the
    current classifier, so the report never shows stale shapes.

## Run record (2026-10-28)

`baseline --majors 18,20,23`: 63 selections (56 corpus = 49 `.ll` + 7 `.c`,
3 seeds, 4 controls) agree across majors, exit 0, zero `F?`. Then
`matrix --majors 18,20,23 --suites P1,P2,P3 --p3-seqs 200 --jobs 12 --seed 20261028`
(run `20261028T215436-2473669`, 170,163 cells, ~30 min) and
`matrix --suites P1 --p1-passes structurizecfg` (run `20261028T222531-3642703`,
378 cells, final precondition rule), then `report`. The stopped first v3 run
(`20261028T214809-2381419`) and the LLVM-23 smoke run (`20261028T214248-2366962`) remain on disk and are superseded
logically. Controls: every control FAILs its intended check on 18/20/23. Seeds:
no FAIL in any suite.

Notable: P3 populations are 279/296/316 passes (18/20/23) after excluding the
P1-ineligible passes. LLVM 23 still rejects `default<Os|Oz>` (kept opt-error).
`c-pure-attr-wrapper` post-O3 sanitizer cells stay FAIL:L5 rather than
env-error, correctly by the rule: O3 already removed the `__bennett_gate`
import (the case's own finding), so "every marker still imported" fails; they
are reported, but they are consequences of that O3 finding, not new findings.

Not done this session: P4 was not rerun under v3; no `llvm-reduce` minimisation
of the new findings; the CLAUDE.md worklog was not written (outside the owned
paths, as for the previous implementer).
