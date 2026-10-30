# Brief: dialect 0.2.6 → 0.2.7, council round 6 fixes (spec + checker together)

Repository `/home/tobias/Projects/bennett-workspace/bennett-dialect-spec` (HEAD ff249d5, draft 0.2.6, freeze gate
2598/2598). You are the **sole editor** of the spec **and** the checker for this round. Council round 6
(`/home/tobias/Projects/bennett-workspace/bennett/docs/council/dialect-2026-10-29/round-6/`, members sol and codex;
muse's seat held) returned: sol core **accept** / overall revise with one contract blocker; codex core revise with three
blockers; every round-5 blocker confirmed resolved; no regressions; mean 4.25. Everything in the previous brief
(`docs/briefs/2026-10-30-dialect-round-5-fixes.md`: read-first list, method, gate command, owned paths, process)
still binds; this brief only states the round-6 work.

## The four blockers (full text in `round-6/out-sol.json`, `round-6/out-codex.json`)

- **SOL-R6-01 (contract, §9.2, §16.2).** A budget-table entry is matched "by its identity (§7.3, the interface hash of
  @ref of one shape)", and that identity includes the shadow-stack size `sstack` that the entry itself selects; the
  selector depends on the value it selects and no staging rule breaks the cycle. Witness: an O0 `alloca [24 x i8]`
  function with an IN(8,zext)/tgt=8 shape. Fix by a normative staging rule (identity computed over the shape without
  the budget-dependent components, then the entry supplies them; or an explicit provisional-identity step), stated so
  two implementations cannot differ, with the witness as a checked example whose hash the checker reproduces.
- **R6-CODEX-01 (core, §7 PT2 vs §16.4).** PT2 adds constant GEP indices as datalayout byte offsets in the original
  object without the modular index computation §16.4 now prescribes, so a `getelementptr i8, ptr @tab, i64 2^32` under
  `p:64:64:64:32` yields a false candidate set. Make PT2 compute exactly what §16.4 computes (index width I(a),
  wrap), and add the witness as a recognition case.
- **R6-CODEX-02 (core, §7 PT5 vs N4, §12.1/§18.1).** PT5 reads `range` attributes/metadata "before N3 removes it",
  but N4 removes range attributes and execution is defined on the materialised module, so the old range is not a
  bound on the program dispatch must handle. Decide one consistent rule (either the materialised module keeps the
  range as a checked assumption that faults when violated, or PT5 may not narrow ⊤ from a removed range) and state
  it; the witness (`range(i64 1, 2) %n`, `and`/`or` to a width the range would exclude) must execute consistently
  under the rule in the checker.
- **R6-CODEX-03 (core, §12 N9).** N9's `atomicrmw` replacement table omits `nand`; LLVM has no ordinary `nand`
  instruction, so the prescribed replacement is invalid IR and retaining `atomicrmw` violates V6. Add the `nand`
  expansion (`xor (and old, v), -1`) with a normalisation pair and native witness on LLVM 18 and 23 (`lli` results
  the member gives), and sweep the table for any other missing `atomicrmw` operation.

Rule 10 as always: none of these fixes may narrow; a `range` rule that rejects is a narrowing unless the north star
permits it (it does not); choose the rule that keeps every program admissible.

## Deliverables

Spec edits in place with witnesses; checker cases executing every witness in the same pass (unit regression that
fails before and passes after); freeze gate green at ≥ 2598 (exact command in the previous brief; write the receipt
to both PROGRESS files); version 0.2.7 in `SPEC_VERSIONS.toml` and the spec; response file
`/home/tobias/Projects/bennett-workspace/bennett/docs/council/dialect-2026-10-29/round-6/response.md` in the
round-5 format (one entry per blocker: status, section, hand derivation, what the text now says, witness, checker
case). Commit owned paths by explicit path list (`spec scripts corpus SPEC_VERSIONS.toml` in the dialect repo; the
response file in `bennett`) with `BEADS_HOOK_TIMEOUT=20` and absolute paths; never push; headless; no `cd` in compound
commands. Final message: commit hashes, per-blocker table, declines/partials, freeze total before → after, any ISA
0.8 gap with the exact ISA change.
