# Draft 0.2.12 consumer-gap review brief — 2026-11-01

ISA grading target: 0.8. Eight consumer-chosen passes; no capability-track adoption.
Accepted 0.2.10 stays in git at 023f5a7; errata are a separate binding interpretation.

| Bead | Reading adopted and why | Clauses touched | Kind | Consumer impact |
|---|---|---|---|---|
| mkb | N0 before resolve; S2 already models normalisation and N0 requires true | §§7.2, 12.2 N0 | clarified | Original source addresses retained; plugin bp-tr5 needs implementation evidence |
| jjr | Aligned C wrapper over exact primitive; unmodified C needs ABI alignment | §§16.9, 17.1 | clarified | Current odd-size thin malloc is an implementation blocker; keep jjr open |
| lbq | A: ordered byte effects, static musl context, ISA R tape; follows tier/entry contracts | §§11.2–11.3, 19.2 (14.7 cross-reference) | clarified | Framing matches; complete process-context evidence remains brt-4w7; keep lbq open; no second tape/ELF startup ABI |
| 0na | A: comparison-only support, explicit resolved layout; native execution needs primitive realisation | §§3.1, 17.7, 19.5 | new ABI + clarified obligations | Layout evidence exists; full detection remains brt-2qs / bennett-driver-i0v; UBSan subset insufficient; keep 0na open |
| dfd | Explicit exactness/CR guarantees outrank APFloat fallback quirks; do not narrow to producer subset | §§13.1, 13.5 | clarified + new pair/flag precision | APFloat-matching fallback is insufficient; bennett-arith-4yg; keep dfd open |
| 1av | B: full-domain one-local-ulp carrier envelope; explicit constrained rounding/flags, not unbounded approximation | §§13.3–13.5 | new accuracy/flag requirement | Measured sweeps do not establish full-domain bound/exact flags; bennett-arith-wvh; keep 1av open |
| z7u | A: finite LLVM-major MDString names, with generated concrete bitcode; metadata names formats, not arbitrary records | §13.1 | clarified names + new instantiation ABI | Generation/consumption: bennett-arith-38c.1, bp-o0h, bennett-driver-q4d; keep z7u open |
| 21a | B: distinct cmps_B_rm; same predicate bits cannot encode distinct qNaN invalid behavior | §§13.1, 13.5 | new ABI + clarified flags | Signaling definitions/lowering: bennett-arith-chn.1 and bp-q6e (existing chn/bp-xms retained); keep 21a open |

Evidence: read-only inspection of runtimes `src/allocator/bump.c`, `src/musl/{syscall,context}.c`,
`src/native/{layout.h,heap,start}.c`, tests and HANDOFF; arith `softfloat/{ppc.h,generate.py}`,
PPC/APFloat and MPFR tests, publication manifests and HANDOFF; plugin `bp-tr5` and
`tests/region_keys.py`. ISA 0.8 §7.1 and 0.9 §7.1 both retain the exact max(n,1) primitive
history; 0.9 is corroboration, not this draft's grading target. LLVM 23's installed
Intrinsics.td/APFloat.h and an actual `isValidArbitraryFPFormat` probe distinguish the eleven
valid names from the five currently mapped by `getArbitraryFPSemantics`.
The [LLVM LangRef conversion contract](https://llvm.org/docs/LangRef.html#llvm-convert-to-arbitrary-fp-intrinsic)
supplies interpretation/rounding/saturation operands; the new carrier/request ABI is this draft's choice.

The extra gate rows check normative wording and retained witnesses; executable additions check
N0 resolution without source mutation, 77 format/base ABI pairs, request canonicalisation and
comparison entry/operand/exception lowering. They do **not** certify full runtime/DF coverage,
PPC correct rounding, full-domain libm bounds or actual signaling-library flags. Those missing
consumer implementations remain blockers. Already determined subquestions (jjr OOM/free/history,
lbq R tape versus L memory) retain §§17.1/17.5 and §§11.1/11.3; no second tape or new ISA
allocation primitive is inferred. Binding interpretations for all eight are in
[`errata-0.2.10.md`](../../spec/errata-0.2.10.md); entries explicitly separate new ABIs/bounds
from interpretations, so the plugin's accepted 0.2.10 pin remains valid.

Review request: one-reviewer council round by the orchestrator; this draft is **not yet accepted**.
Assess the numerical requirements and exact ABI decisions, with consumer completion kept separate.

| Pass | Gate passed/total | Commit |
|---|---:|---|
| mkb | 2840/2840 | 8c4fd7a |
| jjr | 2846/2846 | 7d70813 |
| lbq | 2854/2854 | 0bfc463 |
| 0na | 2868/2868 | c89f4d5 |
| dfd | 2873/2873 | 0eb0dc1 |
| 1av | 2880/2880 | abcef88 |
| z7u | 2888/2888 | a925f3c |
| 21a | 2893/2893 | this final pass commit |

All eight validator runs passed (1 unit each, 0 doc-tests). Receipts:
`scripts/.tmp/0212-<bead>.json`; standalone new checker tests: 4/4.
All 497 accepted tagged blocks are retained byte-for-byte by the existing baseline check.
Closed: mkb (contract clarification only; plugin implementation remains bp-z9k).
Kept open as implementation blockers: jjr, lbq, 0na, dfd, 1av, z7u, 21a.
Twelve follow-ups filed with `dialect-0.2.12` and topic labels; no sibling source edits.

Tracking-only sibling commits (each verified to change only `.beads/issues.jsonl`):
plugin `b5d5834`, `af1e243`, `4f67f6d`;
runtimes `9fa9943`, `96cf15a`, `ebeae63`, `f0e9dc7`;
arith `4ef1b0d`, `966adad`, `8f504c0`, `c48753d`;
driver `752a89e`, `c92bf23`. Nothing pushed. SPEC_VERSIONS.toml remains the accepted-release registry.
