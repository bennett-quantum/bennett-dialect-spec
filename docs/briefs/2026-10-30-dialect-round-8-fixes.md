# Brief: dialect 0.2.9 → 0.2.10, council round 8 fixes (spec + checker together)

Repository `/home/tobias/Projects/bennett-workspace/bennett-dialect-spec` (HEAD 1a50835 = 0.2.9 text aa0f72e plus a
HANDOFF-only commit; freeze gate 2732/2732). You are the **sole editor** of the spec **and** the checker for this
round. Council round 8 (`/home/tobias/Projects/bennett-workspace/bennett/docs/council/dialect-2026-10-29/round-8/`,
members sol and codex; muse's seat held; report.md, out-sol.json, out-codex.json) returned: both revise; **every
round-7 blocker and both relay-addendum items confirmed resolved**; no regressions; mean 4.12; two distinct S0 core
blockers. Everything in `docs/briefs/2026-10-30-dialect-round-5-fixes.md` (read-first list, method, exact freeze-gate
command, owned paths, process) still binds; this brief states only the round-8 work. Read both members' full text in
report.md first; each carries a complete witness module and native results on LLVM 18 and 23.

## The blockers

- **SOL-R8-01 ≡ R8-CODEX-02 (core, §5.2 PT3 vs §12.6 N21, §3.4).** PT3 lists `bitcast` under "copies (union)" and
  §5.2 defines copies as "AV(result) ⊇ AV(operand) lane by lane"; that is false for a bitcast that changes lane
  geometry. Witnesses: `bitcast <2 x i8> <1,1> to i16` packs to 257 (sol; two X gates at index 256 on a 257-wire
  allocation) and `<0,1>` packs to 256 (codex); the recogniser keeps lane-0/lane-1 INT(1) entries and VS={1} or
  {0,1}, so §3.4 dispatches only the wrong width while §12.6/N21 materialises the correct packed value. Fix: bitcast
  copies lane by lane only when lane count and per-lane representation width are identical (scalar = one lane);
  otherwise the S2 transfer uses the virtual N21 expansion of §12.6 (pack source lane bit patterns in DataLayout
  order, resegment at destination width, PT4/PT5 transfers over the expansion, finite INT lane sets as their
  Cartesian product with the K cap per resulting lane, unknown bits as non-handle top, ROOT provenance preserved and
  §6.2 unchanged, constant expressions and fixed-vscale forms included), before verdicts, candidate sets and
  dispatch domains freeze. Both members supply replacement text; merge them into one rule (codex's virtual-N21
  phrasing is the more implementable; sol's "never copy a source-lane INT atom as the value of a packed destination
  scalar" sentence must survive). Both witnesses go into DB/DN/DS with verdict accept, AV(bits)={INT(257)} /
  {INT(256)}, VS={257} / {256}, the native marker-harness results (width, gate index, clean free, code 0) on both
  majors, plus the inverse scalar-to-vector / different-geometry companion both members ask for. Never classify a
  finite geometry-changing bitcast as BLK-1 and never reject it (rule 10).
- **R8-CODEX-01 (core, §5.2 initial seeding / PT1 / PT6 vs §§17.1, 17.3, N24).** §17.1/§17.3 make shadow-stack frames
  and heap allocations zero-filled, N24 supplies zero for an uninitialised alloca, but §5.2 seeds only global
  initialisers, so an alloca read on a path with no store has no INT(0) possibility. Witness: `alloca i64`,
  conditional `store i64 1`, `load`, `freeze`, `extractelement <2 x i64> <1, 3>` by the loaded index → widths 1 and 3
  are both executed natively (clang 18/23, O0 and O3), but the recogniser's VS(%width)={3} drops the width-1 case.
  Fix: the initial-seeding paragraph also seeds a zero-byte initial image for every extent of every alloca and
  allocation-site object whose initial contents are zero under §§17.1/17.3 (nonconstant extents symbolically over
  their possible bytes); stores union, never erase; PT6 includes the all-zero value for a possibly valid load wholly
  inside such an extent, unioned with overlapping stores under the interval rules; PT8 propagates the initial bytes
  on memory copies; zero contributes no ROOT; region inputs, replayed caller bytes and other nonzero-initialised
  contents keep their specified sources. Codex supplies the replacement text; adopt it (a virtual initialisation-
  store expansion during S2 is an acceptable implementation note). Witness into DB/DN/DS with AV(%raw)=AV(%idx)=
  {INT(0),INT(1)}, VS(%width)={1,3}, verdict accept, native widths 1/3 with clean free and code 0 on both majors;
  add a heap-allocation (zero-filled) companion. Never move this to a rejection, precondition or ISA blocker.

Hand-verify every member value with the LLVM 18 and 23 tools and the native harness before trusting it; if a value is
wrong, say so with your own derivation. Rule 10: none of these fixes may narrow; every witnessed program stays
admissible.

## Deliverables

As in the round-7 brief: spec edits in place with witnesses; checker cases executing every witness in the same pass
(unit regressions red → green on both majors); freeze gate ≥ 2732 with receipts in both PROGRESS files; version
0.2.10 in `SPEC_VERSIONS.toml` and the spec; response at
`/home/tobias/Projects/bennett-workspace/bennett/docs/council/dialect-2026-10-29/round-8/response.md` in the
round-7 format (one entry per blocker: status, section, hand derivation, what the text now says, witness, checker
case). Commit owned paths by explicit path list (`spec scripts corpus SPEC_VERSIONS.toml` and `.beads/` via `bd` in
the dialect repo; the response file in `bennett`) with `BEADS_HOOK_TIMEOUT=20` and absolute paths; never push;
headless (never LLVM `-view-*`; TMPDIR under `scripts/.tmp`); no `cd` in compound commands. Final message: commit
hashes, per-blocker table, declines/partials, freeze total before → after, any ISA 0.8 gap with the exact ISA change.
