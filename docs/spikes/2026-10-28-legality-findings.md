# Legality spike — findings and decisions (2026-10-28/29)

Deliverable of `2026-10-28-legality-spike.md` §8. Evidence: the harness run
`20261028T215436-2473669` (170,163 cells, LLVM 18.1.3 / 20.1.8 / 23.1.1,
56 corpus cases + 3 seeds + 4 controls; `corpus/legality/results/`), the
corpus rationale (`corpus/legality/cases/README.md`), the triage
(`2026-10-28-legality-triage.md`), the front-end emission examples
(`emission/`), and the Enzyme survey (`enzyme-prior-art.md`). Every
headline below was reproduced by hand by the orchestrator, not only
reported by an agent.

## 1. Verdicts on the north star's §3 claims

| Claim (north star §3.1–3.2) | Verdict | Evidence |
|---|---|---|
| An attribute-free external declaration keeps the **dynamic sequence of marker calls** on every executed path through stock passes | **Holds for every standard pipeline** (`default<O0..O3,Os,Oz>`, `lto(-pre-link)<O3>`, `thinlto(-pre-link)<O3>`, O3×3) on all three majors, for all 50 legal cases. Opacity demonstrably blocks LICM, CSE, DCE of unused results, loop deletion, loop fusion/distribution and the loop vectoriser; each blocked case has a pure-marker twin in which the pass fires. The four negative controls (`memory(none)`, `readonly`, handle deref, region twin) are detected on every major. | P2 table in `results/REPORT.md`; `cases/README.md` "fires" column |
| No pass adds a motion- or elimination-licensing attribute to a marker | **Holds** for every single pass on every major (static sweep of all `--print-passes` × 56 cases × 3 majors). Added: `local_unnamed_addr` (decl); `nonnull`, `noundef`, `range(...)` (20/23), `nounwind` (in nounwind callers), `tail` (call sites). The only forbidden additions seen (`readonly`/`readnone` at call sites) arise in random sequences on `c-pure-attr-wrapper`, i.e. downstream of a source-level `pure` lie (F5). | L2 observations |
| Front ends emit markers as plain direct calls | **Holds for clang (C, C++) and rustc. Julia `ccall` does not** (indirect through `jlplt_*_got`); `ccall("extern __bennett_x", llvmcall, …)` does (direct call, attribute-free declare). | `emission/`, verified by hand |
| No handle use survives into host code; int/ptr round trips are rejected | **The rejection rule is wrong as written.** No pass ever dereferenced a handle, but `instcombine` turns an 8-byte `memcpy` of a handle into `ptrtoint` + `store i64` on all majors, and LLVM 18 `lto<O3>` completes a `ptrtoint → inttoptr` round trip into `__bennett_qfree`. Valid C would be rejected. (F1) | `val-memcpy-handle-int`, `c-memcpy-handle-int` |
| Region entry `__bennett_ctrl(q, @f, …)` names the region | **Not as a constant.** After O1+ the operand is `select` of functions, switch table + `phi`, or `phi` of mixed resolvable values; in source-shaped cases a load from a stack array or mutable table. No pass ever produced an **indirect call to a marker**, and SimplifyCFG/GVNSink never sink a region call whose handle *and* region both differ. (F3) | L6 table |
| Region identity survives | **Not by symbol.** `mergefunc` makes twins into thunks, or under `unnamed_addr` (rustc's default; rustc runs MergeFunctions at O2+) rewrites the marker operand to the twin; `strip` renames internal regions; `iroutliner` and `global-merge-func` (20/23) make regions thunks to outlined bodies. (F2) | triage §3, L4 FAILs |
| Optimisation leaves marker operands alone | **No, legally.** Fused `fmuladd` and NaN canonicalisation change `rot` angles; `__builtin_constant_p` and `__builtin_object_size` change budgets and qalloc widths between O0 and O1+. Exactly the cases north star §3.2's normaliser exists for (soft-float, `fmuladd` split, query intrinsics lowered before both builds). (F4) | `fp-rot-*`, `c-is-constant-budget`, `c-objectsize-count` |

## 2. Findings that are LLVM bugs, not dialect problems

All marker-free reproducers; none of the passes is in any default or LTO
pipeline of the three majors (the Attributor runs in-pipeline only via
openmp-opt on OpenMP modules).

- **Attributor**, constant-table load at a select index folds to element 0
  (18, 20; fixed upstream by llvm-project PR #151359, LLVM 22+); related open
  issue #234748 reproduces on 23. **Attributor loop-counter miscompile**
  (18, 20, 23; triage §5): a loop whose counter lives in memory and is
  incremented by a call (`while (load a < 4) inc(a)`) is folded to an
  infinite loop; `iroutliner` merely created that shape in `c-program-mixed`.
  Marker-free reproducer verified by the orchestrator on 18 and 23; matches
  open llvm-project issue #236104 (candidate fix PR #236114, unconfirmed).
- **IRNormalizer** (`normalize`, 20/23) reorders a load past a store
  (open issue #236128); `normalize<preserve-order>` is correct.
- **structurizecfg** run without its AMDGPU prerequisites
  (lowerswitch, fix-irreducible, unify-loop-exits) miscompiles; with them every
  case passes. Harness outcome `precondition`.

## 3. Decisions (maintainer, 2026-10-29)

1. **Region identity is by content.** A region is the function the marker
   receives at link time, identified by its body (content hash, matching the
   ISA's content-addressed objects). Merged twins are the same region;
   aliases and forwarding thunks resolve to their target; symbol names are
   non-normative.
2. **Handle provenance is tracked through bitwise copies.** It flows through
   `ptrtoint`/`inttoptr`, integer loads and stores, and vector lanes while the
   bits are only copied (no arithmetic, comparison or partial use). Any other
   use of a handle-derived integer is rejected fail-loud. This amends the
   wording of north star §3.1 (handle row); to be filed as north-star
   amendment A2.
3. **Region operands are classical data, dispatched at run time.** The
   device's classical-control tier dispatches on the region pointer; the
   plugin compiles bodies for the bounded candidate set (every function whose
   address can reach a region marker) and fails loud only when that set
   cannot be bounded (pointer from host input, `inttoptr` of a non-handle
   integer, unknown external).

## 4. Defaults the spec will state (not maintainer decisions; open to the council)

- **Unwinding.** Markers never unwind. A marker reached by `invoke` is treated
  as `call` + `br` to the normal destination (Enzyme's practice); the unwind
  edge is dead. Front ends may declare markers `nounwind` (Rust `extern "C"`
  does) or not (C++ `-fexceptions`, Rust `extern "C-unwind"`).
- **Permitted front-end and pass attributes** on marker declarations and call
  sites: `nounwind`, `noundef`, `nonnull`, `range`, `zeroext`/`signext`,
  `local_unnamed_addr`/`unnamed_addr`, `nonlazybind`, `tail`. Forbidden: the
  §4 L2 set; a forbidden attribute on a marker is a fail-loud error.
- **Julia** emits markers with `ccall("extern __bennett_*", llvmcall, …)`;
  plain `ccall` markers are not recognised (the plugin may diagnose
  `jlplt_*_got` globals whose `julia.fname` names a marker).
- **Source attribute lies.** A function declared `pure`/`const`/`memory(read)`
  /`willreturn` that transitively calls a marker is a source error; it is
  covered by the definedness assumption, and the plugin diagnoses any marker
  call it still finds inside a function carrying such attributes. The front
  end's own pre-link optimisation may already have deleted the calls, so this
  cannot be a guarantee. (F5)
- **Reference baseline** for differential testing is the normalised optimised
  module (north star §3.2), never an `-O0` build. The spike's L1 compared
  against `llc -O0` of the raw case and so flags F4 as FAIL; that is by
  design of the spike, not a dialect violation once normalisation runs.
- **Supported-pass envelope.** The plugin's contract is stated for the
  default and LTO pipelines of each supported LLVM major. Passes outside
  them are unsupported unless listed; Attributor (module and CGSCC, on every
  supported major: #234748, #236104), IRNormalizer,
  structurizecfg without prerequisites, and the debugging/instrumentation
  passes the harness classes `non-preserving` are named as unsupported.
- **K&R unprototyped declarations** (`c-unprototyped-decl`) are recognised
  by name; the signature is checked at the call site.

## 5. Open after the spike

- P4 (clang `-flto` end to end) not rerun under harness v3.
- No `llvm-reduce` minimisation of the three P3-only interactions.
- rustc's own pre-link pipeline (MergeFunctions in alias mode) merges region
  twins before the driver sees bitcode: covered by decision 1, but a Rust
  emission case through `-Clinker-plugin-lto` belongs in the corpus.
- North-star amendment A2 (handle provenance wording) to be drafted and
  graded with A1.
