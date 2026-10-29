# Legality spike — plan (2026-10-28)

North star §3.2 and §9 item 1: **freezing `bennett-dialect-spec` is gated
on a legality corpus passing.** Marker-bearing bitcode, through every
stock LLVM pass at O3 and through native code generation, must preserve
the *dynamic sequence* of marker calls on every executed path and must
leave no handle use in host code; plus actual emission examples from
clang, rustc and Julia. This document is the brief every spike agent
works from. It is not normative; the spike's job is to produce the
evidence the normative text will cite.

Nothing here concerns the ISA (0.8, settled). The spike marker ABI below
is **provisional**: names and signatures exist only so the corpus can be
written; the spec will fix them, informed by what the spike finds.

## 1. Spike marker ABI v0 (provisional)

C view (`corpus/legality/markers.h`). Handles are an opaque `ptr` in
address space 0. Every marker is a plain external declaration with **no
attributes beyond what the front end adds by default** (positive legality
requirement, north star §3.1).

```c
#include <stdint.h>
#include <stdbool.h>
typedef struct __bennett_q *bq;            /* opaque handle, never dereferenced by host code */
typedef void (*bregion)(void *env);         /* outlined region body */

bq   __bennett_qalloc(uint64_t cls, uint64_t n);          /* clean */
bq   __bennett_qborrow(uint64_t cls, uint64_t n);         /* dirty */
void __bennett_qfree(bq h);
void __bennett_gate(uint32_t op, bq h, uint64_t i);                       /* 1-qubit */
void __bennett_gate2(uint32_t op, bq a, uint64_t i, bq b, uint64_t j);    /* 2-qubit */
void __bennett_rot(uint32_t op, bq h, uint64_t i, double theta);
bool __bennett_measure(bq h, uint64_t i);
void __bennett_qload(bq dst, bq mem, bq addr);
void __bennett_qstore(bq mem, bq addr, bq val);
void __bennett_ctrl(bq q, uint64_t qi, bregion f, uint64_t budget, void *env);
void __bennett_adj(bregion f, void *env);
void __bennett_compute(bregion f, bregion use, void *env);   /* f; use; uncompute f */
void __bennett_reversible(bregion f, uint64_t budget, void *env);
void __bennett_inplace(bregion g, bregion ginv, void *env);
void __bennett_ctrl_v(bq q, uint64_t qi, void *f, uint64_t budget, ...); /* variadic probe: traced, not forwarded */
```

## 2. Layout and ownership (one implementer per directory)

```
corpus/legality/
  markers.h               spike ABI (§1)                               owner: harness agent
  toolchains.toml         bin dir per LLVM major                       owner: orchestrator
  runtime/trace_rt.c      defines every marker; writes the trace (§3)  owner: harness agent
  runtime/driver.c        main(): runs @case_entry per input           owner: harness agent
  harness/run.py          the matrix runner (§4, §5); stdlib only      owner: harness agent
  harness/test_*.py       harness self-tests                           owner: harness agent
  controls/*.ll           negative controls that MUST be detected      owner: harness agent
  cases/*.ll, cases/*.c   adversarial corpus                           owner: corpus agent
  cases/README.md         case → targeted hazard → expected verdict   owner: corpus agent
  results/                raw outputs (gitignored) + summary.json, REPORT.md (committed)
emission/{c,cpp,rust,julia}/   sources, captured IR, NOTES.md         owner: emission agent
```

No agent writes outside its directories, and no agent commits; the
orchestrator reviews and commits.

## 3. Case format, runtime and trace

**Case.** One module, LLVM-18 textual syntax (must also parse in 20 and
23; no debug info), defining `define i64 @case_entry(i64 %x)`. Header
comments the harness reads:

```
; CASE: <id>            one line, kebab-case, equals the file stem
; HAZARD: <passes / transformations this case targets>
; INPUTS: 0..255        inclusive range, or a space-separated list; exhaustive where small
; EXPECT: legal         legal (must pass every check) | probe (a finding either way; report it)
```

`.c` cases carry the same header in `//` comments and are compiled by the
harness with `clang-18 -O0 -Xclang -disable-O0-optnone -emit-llvm -S`, so
the optimiser, not the front end, does the work; for majors 20 and 23 the
same LLVM-18 `.ll` is used (newer readers accept it).

**Runtime** (`trace_rt.c`, compiled separately by the system C compiler,
never seen by the optimiser). Every marker appends one line to the trace;
region markers bracket and *call* their region functions so markers inside
regions are traced: `ctrl`, `adj`, `reversible` call `f(env)` once;
`compute` calls `f`, `use`, `f`; `inplace` calls `g`. Canonicalisation so
traces compare across builds:

- handles print as `H<k>`, k = allocation ordinal within the current input;
  a value not issued by `qalloc`/`qborrow`, or already freed, prints
  `BADHANDLE` (a finding);
- function pointers print as the defining symbol's name via `dladdr`
  (link with `-rdynamic`); unresolved prints `F?` (a finding);
- `double` prints as its hex bit pattern; `env` pointers are not printed;
- `measure` returns a deterministic bit from (input, measure-call ordinal),
  so branches on measurement are exercised and a reordered measure changes
  the trace;
- handles are addresses inside a `PROT_NONE` mapping, distinct per handle;
  a SIGSEGV whose address lies in it prints `FAULT handle-deref` and exits
  with a distinct status (host code dereferenced a handle).

The driver prints `IN <x>` before and `RET <value>` after each input, so
classical results are compared too. Per-input state resets.

## 4. Checks

| Id | Property | Method |
|---|---|---|
| L1 | dynamic marker sequence and classical result preserved | trace of transformed build == baseline trace, every input |
| L2 | no pass adds an elimination- or motion-licensing attribute to a marker | static, pre/post diff of every `__bennett_*` declaration and call site. Forbidden: any `memory(...)`, `readnone`, `readonly`, `writeonly`, `argmemonly`, `inaccessiblememonly`, `willreturn`, `speculatable`. Recorded as observations: `nounwind`, `nofree`, `nosync`, `norecurse`, `noreturn`, anything else added |
| L3 | handles stay contained | dynamic: guard-page fault, `BADHANDLE`; static: new `ptrtoint`/`inttoptr` in any function that touches a handle (flag for review, not auto-fail) |
| L4 | region identity | every function pointer passed to a region marker resolves to the same symbol as in the baseline, and that symbol is a `define` (not an alias, thunk-to-other, or declaration) in the transformed module |
| L5 | native codegen | transformed module through `llc -O3` (and `-O0`), linked with runtime + driver: L1 holds; `nm` shows every marker the baseline calls as an undefined external |
| L6 | static resolvability of region operands (observation, added after the Enzyme survey) | classify every region marker's function operand in the transformed module: constant `@f` / `select` of constants / `phi` of constants / load from a constant table / other. clang-18 -O3 already produces `select ptr @g, @f` and `@switch.table.*` + `phi` from per-branch region calls: dynamically legal (L1, L4 hold), but the plugin must resolve the shape statically. Recorded per (case, pass, major); "other" is a finding |

**Baseline** per major: the untransformed case, `llc -O0`. Baselines must
agree across majors (sanity check; a disagreement is a harness or case bug
until shown otherwise).

## 5. Pass matrix, per major in {18, 20, 23}

- **P1 single passes:** every pass `opt --print-passes` lists (module,
  cgscc, function, loop, loop-mssa), wrapped as its level requires,
  parameterised passes at their defaults; run on each case raw **and** on
  each case after `default<O3>` (some transforms fire only after others).
  Outcome per (case, pass): `pass` / `FAIL:<checks>` / `opt-error` (opt
  refused or crashed; recorded, not a legality failure) / `noop` (output
  identical to input).
- **P2 pipelines:** `default<O0|O1|O2|O3|Os|Oz>`, `lto-pre-link<O3>`,
  `lto<O3>`, `thinlto-pre-link<O3>`, `thinlto<O3>`, and `default<O3>`
  three times in a row.
- **P3 random sequences:** N seeded random sequences of 5–40 passes from
  the P1 set that did not `opt-error`; seed and sequence recorded so every
  failure replays.
- **P4 front-end path** (major 18): `.c` cases through `clang -O3 -flto`
  and `ld.lld`/`clang -fuse-ld=lld -flto` to an executable.

Every failure is minimised (`llvm-reduce` with the failing check as the
interestingness test, where practical) and written up with the pass,
major, case, check and diff.

## 6. Negative controls (red before green)

The harness is not trusted until it **fails** these:

- `memory(none) nounwind willreturn` marker in a loop: O3 must CSE/DCE/hoist it → L1 FAIL and L2 notes;
- `readonly` marker under LICM → L1 FAIL;
- host code that loads through a handle → L3 FAIL (`FAULT handle-deref`);
- a region passed to `__bennett_ctrl` with an identical twin, run through `mergefunc` → L4 must notice the symbol change if it happens (probe; if mergefunc does not merge, document why);
- harness unit tests with synthetic pre/post IR pairs for L2 and L3-static.

## 7. Emission examples

For each of C (clang 18), C++ (clang 18, with and without exceptions),
Rust (rustc 1.99 / LLVM 23) and Julia (1.13 / LLVM 20): a small program
over the §1 ABI (allocate, gate, rotate, measure and branch on it, a
`ctrl` region with an environment, a handle table indexed by a classical
value, free), its IR as the front end emits it unoptimised and as LTO
would receive it, and `NOTES.md` recording exactly: the marker
`declare` lines and attribute groups; call-site attributes; whether each
call is a direct call by name (Julia's `ccall` lowering is the suspect);
handle and `bool` representations; how a region function pointer and its
environment are formed; whether the variadic marker is emittable; whether
the declarations meet the positive legality requirement and, if not, what
attribute the front end adds and whether a driver-side strip is needed.

## 8. Deliverable

`corpus/legality/results/REPORT.md`: the matrix per major, every failure
with its minimised reproducer, the list of attributes observed on
markers, and a verdict per north-star claim of §3.1 ("stock passes
preserve the dynamic sequence of marker calls on every executed path";
"no handle use survives into host code"; "region identity survives").
The dialect spec draft cites it.
