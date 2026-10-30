# Brief: dialect 0.2.7 → 0.2.8, council round 7 fixes (spec + checker together)

Repository `/home/tobias/Projects/bennett-workspace/bennett-dialect-spec` (HEAD 95c3cd3, draft 0.2.7, freeze gate
2651/2651). You are the **sole editor** of the spec **and** the checker for this round. Council round 7
(`/home/tobias/Projects/bennett-workspace/bennett/docs/council/dialect-2026-10-29/round-7/`, members sol and codex;
muse's seat held) returned: both revise; sol 1 core blocker, codex 4 core blockers (the first coincides with sol's);
every round-6 blocker confirmed resolved; no regressions; mean 4.0. Everything in
`docs/briefs/2026-10-30-dialect-round-5-fixes.md` (read-first list, method, exact freeze-gate command, owned paths,
process) still binds; this brief states only the round-7 work.

## The blockers (full text in `round-7/out-sol.json`, `round-7/out-codex.json`)

- **SOL-R7-01 ≡ R7-CODEX-01 (core, §7 PT4/PT5 vs §16.4).** PT5's "shifts each pointer atom's offset by each
  constant" and PT4's "ptrtoint/inttoptr copies" use unbounded offset arithmetic; the integer operation has a finite
  width. Witness: two `add i64 … , -2^63` on a `ptrtoint` of `@tab` cancel modulo 2^64, so `%p == @tab`, and the
  current rule yields a false candidate set. Apply the same modular rule the round-6 GEP fix introduced (I(a)-width
  wrap, then re-association with the object), state the non-handle top alternative propagation through PT6 loads
  that sol names, and add the witness as a recognition case.
- **R7-CODEX-02 (core, PT10 vs N15).** PT10 "a non-constant lane index moves the union of all lanes" while N15
  gives an out-of-range extraction the zero element, which need not be any source lane; the reference domain excludes
  a value of the materialised program. Make PT10 include N15's totalised value (the zero element) in the union.
- **R7-CODEX-03 (core, N15 vs §12.6).** N15 covers only non-constant lane indices; §12.6 says constant indices are
  "lane renaming" while also claiming out-of-range poison is totalised by N15. A constant out-of-range index is valid
  IR with no lane to rename. Extend N15 (or §12.6) to constant out-of-range indices with the same totalisation, and
  add the `extractelement <2 x i8> <5, 9>, i32 2` witness as a normalisation pair with native results on 18 and 23.
- **R7-CODEX-04 (core, §13.4).** The non-native fp128/ppc_fp128 route "fpext to the target's long double then
  fptrunc" is invalid IR where long double is narrower (x86_fp80) or equal-size (ppc_fp128 → fp128). Replace with a
  rule that is valid on every supported platform (direct soft-float library call for the format, or the
  §13.1 bit-exact form), with a witness per affected platform triple and the exact LLVM verifier result.

Rule 10: none of these may narrow; every program the witnesses show stays admissible.

## Deliverables

As in the round-6 brief: spec edits in place with witnesses; checker cases executing every witness in the same pass
(unit regressions red → green); freeze gate ≥ 2651 with receipts in both PROGRESS files; version 0.2.8; response at
`/home/tobias/Projects/bennett-workspace/bennett/docs/council/dialect-2026-10-29/round-7/response.md` in the
round-6 format. Commit owned paths by explicit path list with `BEADS_HOOK_TIMEOUT=20` and absolute paths; never push;
headless; no `cd` in compound commands. Final message: commit hashes, per-blocker table, declines/partials, freeze
total before → after, any ISA 0.8 gap with the exact ISA change.
