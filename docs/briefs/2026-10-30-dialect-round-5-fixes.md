# Brief: dialect 0.2.5 → 0.2.6, council round 5 fixes (spec + checker together)

Repository `/home/tobias/Projects/bennett-workspace/bennett-dialect-spec` (HEAD a06fcbd, draft 0.2.5, round-4 freeze
gate green). You are the **sole editor** of the spec **and** the checker for this round (the two were split once and
the gate oscillated red across handoffs; never again). Council round 5
(`/home/tobias/Projects/bennett-workspace/bennett/docs/council/dialect-2026-10-29/round-5/`, members sol, codex,
muse) returned no consensus: 8 S0 core blockers (sol 1, codex 2, muse 5) and one wording regression; every round-4
blocker is resolved. Fix each in place or decline with an airtight spec quote; nothing is argued away.

## Read first, in full

1. `CLAUDE.md` (rules 1, 8, 10, 11). Rule 10 is absolute: no fix may narrow a north-star capability
   (`../bennett/docs/Bennett-NorthStar.md`); if a blocker's proposed fix narrows, find the non-narrowing fix.
2. `round-5/report.md`, then the full `problem`/`fix` text of the blockers in `round-5/out-sol.json`,
   `round-5/out-codex.json`, `round-5/out-muse.json` (the JSON is the source). Blocker ids: SOL-R5-01 (pw vs the
   per-address-space pointer representation width, §1.5 vs §16.2–16.4/§17.4/§18.1; raised by sol and codex
   independently), R5-CODEX-01, R5-CODEX-02 (one is the PT6 overlapping-slot loads case), BD3-R5-1 (persistent-memory
   scoping of the BD3-R4-1 fix), BD3-R5-2 (soft-float i128 assumption in §13.1), BD3-R5-3 (N27 vs N22 ordering),
   BD3-R5-4 (N9 missing form), BD3-R5-5 (the §16.4 GEP canonical-row algorithm compressed in 0.2.5; muse's regression:
   restore the text-determined per-index algorithm so row charges/hashes are determined by the text again).
3. `../bennett/docs/council/README.md` (editor loop: surgical edits, never rewrites; accepted text does not move),
   `../bennett/docs/council/rubric-isa.md` (narrowing is S0), `round-4/response.md` (the response format to follow).
4. `spec/Bennett-Dialect-Spec-0.2.PROGRESS.md` and `scripts/dialect_check.PROGRESS.md` (top entries: the round-4
   freeze receipt and the exact gate command), `spec/outline-0.2.md` (ratified outline, rulings E1–E14 at its end).
5. `../bennett-isa-spec/spec/Bennett-ISA-Spec.md` (ISA 0.8; never edit it) as each blocker needs. The dialect is graded
   against 0.8; a gap in 0.8 is a `blocked:` verdict naming the ISA change and a bead, never a shrink.

## Task

For each blocker: re-derive the disputed example by hand from the spec text before editing (the members did: SOL-R5-01
has an LLVM 18/23 witness with datalayout `p270:32:32`; run the same probes headlessly with the installed LLVM 18 and
23 and record the outputs). Where the council is right, apply the fix surgically where the blocker says and add the
witness example in the spec's own format (`tdl=`/`state=`, `normalise-out=`, `native=`, `isa object=`, ...). Where
the council is wrong, decline with the deciding sentence (rare). Where members' fixes conflict, choose, say why, make
rule and example agree.

Every new or changed example must be executed by the checker **in the same pass**: extend `scripts/` (the v02 checker
and its family modules) so each new witness is a checked case, with a unit regression in `scripts/test_dialect_check.py`
that fails before and passes after. Every `isa object=` example must pass the independent interpreter's `check`,
and its stated result must hold (build offline: `cargo build --manifest-path ../bennett-isa-spec/reference-interpreter/Cargo.toml --offline`
with TMPDIR set as below). Bump `SPEC_VERSIONS.toml` and the spec's version string to 0.2.6 as `spec/README.md`
prescribes (if it has no rule, keep the pattern used for 0.2.3→0.2.5 and say so in the response).

Freeze gate, exact command (must end with 0 failed, 0 blocked/unavailable beyond the documented `blocked:` verdicts,
and the total must not go down):

```sh
mkdir -p /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp
env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER \
  TMPDIR=/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp \
  python3 /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/dialect_check_v02.py \
  --json /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp/round5-fixes-freeze.json
```

Then record the freeze receipt (spec SHA-256, checker snapshot, interpreter fingerprint, family table) at the top of
both PROGRESS files as the round-4 receipt did.

Write `/home/tobias/Projects/bennett-workspace/bennett/docs/council/dialect-2026-10-29/round-5/response.md`: one entry
per blocker id, status `resolved` / `declined` (spec quote) / `partial` (what remains and why), section edited, what
the text now says in one or two sentences, the hand derivation, the witness example added and the checker case that
executes it. Written for a hostile reader; members re-grade from scratch with the diff attached.

## Owned paths and process

- Write only `spec/`, `scripts/`, `corpus/` (new cases only), `SPEC_VERSIONS.toml`, `.beads/` (via `bd`) and the
  response file above. Never `worklog/`, `HANDOFF.md`, `CLAUDE.md`, `docs/`, the ISA repo or any sibling.
- Keep `spec/Bennett-Dialect-Spec-0.2.PROGRESS.md` current (a "Round-5 fixes" table: blocker id, status, checker case,
  commit) so a restarted session resumes from it.
- Commit owned paths after every resolved blocker group, never a red gate:
  `BEADS_HOOK_TIMEOUT=20 git -C /home/tobias/Projects/bennett-workspace/bennett-dialect-spec commit -- spec scripts corpus SPEC_VERSIONS.toml`
  and `BEADS_HOOK_TIMEOUT=20 git -C /home/tobias/Projects/bennett-workspace/bennett commit -- docs/council/dialect-2026-10-29/round-5/response.md`
  (retry on `index.lock`). Do not push. Headless (rule 11): never any LLVM `-view-*` pass. No `cd` in compound
  commands; absolute paths everywhere.
- Surprises or ISA 0.8 gaps for the maintainer: `bd create` from the repo root (`BEADS_HOOK_TIMEOUT=20`); never shrink
  the dialect to fit.
- Final message: commit hashes, the per-blocker status table, every decline and partial, the freeze total
  (before → after), and any ISA 0.8 gap with the exact ISA change it needs.
