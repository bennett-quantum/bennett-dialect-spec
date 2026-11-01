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
