# Dialect 0.2 full text — progress

Job: write the normative text of dialect draft 0.2 (`spec/Bennett-Dialect-Spec.md`) from the
ratified outline `spec/outline-0.2.md`. Brief: `docs/briefs/2026-10-29-dialect-0.2-fulltext.md`.
Owned paths: `spec/Bennett-Dialect-Spec.md`, `spec/bennett_markers.h`, `spec/README.md`, this
file, `SPEC_VERSIONS.toml`, `corpus/legality/cases/spec-*`. Standing rule: no narrowing.

## Read (2026-10-29)

- [x] `spec/outline-0.2.md` in full, including the maintainer rulings (E1-E3, E5-E14 as
  recommended; E4 = riscv64; BLK-1..4 named blockers; graded against ISA 0.8)
- [x] `spec/Bennett-Dialect-Spec.md` 0.1 in full
- [x] `docs/spikes/2026-10-28-legality-findings.md` (decisions 1-4)
- [x] `docs/audit/2026-10-29-dialect-0.1-narrowing-audit.md` in full
- [x] `docs/spikes/sqlite/REPORT.md` in full
- [x] `../bennett/docs/Bennett-NorthStar.md` in full
- [x] ISA 0.8 `../bennett-isa-spec/spec/Bennett-ISA-Spec.md` in full
- [x] `../bennett/HANDOFF.md` ("What made the ISA rounds converge")
- [x] `../bennett/docs/council/rubric-isa.md`
- [x] reference interpreter README (CLI: check, hash, run-oracle, step-check)

## Tools used

- Rust ISA reference interpreter: a copy of
  `../bennett-isa-spec/reference-interpreter/target/debug/bennett-isa-ref` (built 2026-10-29
  07:40) in the job scratchpad, so that the concurrent interpreter job cannot change it under
  this job. Every `isa object=` example is checked with `check`, every `text run=` line is the
  output of `run-oracle`, every prefix-reversal claim the output of `step-check`.
- LLVM 18 (`/usr/lib/llvm-18/bin`), 20 (Julia artifact, `corpus/legality/toolchains.toml`),
  23 (`/usr/lib/llvm-23/bin` for clang; rustc llvm-tools for opt): every `llvm` block parsed and
  verified on all three, headless (CLAUDE.md rule 11).

## Sections written

- §1-§3 + header (commit 56a3eb1)
- §4-§8 (commit 85c53ab)
- §9-§12 (commit cd709ee)
- §13-§14 (commit fd30dd5)
- §15-§16 (commit 49a2100)
- §17-§18 + corpus `spec-sem2-*` (commit df9e0a5)
- §19-§25 (commit e0e5142)
- Appendices A (outline changes), B (example index), C (546 generic intrinsics); SPEC_VERSIONS
  0.2/0.8; README change rules (commit d0c4830)
- Hostile re-read under the rubric, two passes of fixes (commits eda7eb3, aa004bf), then a
  consistency pass (section cross-references by script: no dangling internal reference; the
  `markers-c` block equals the header's prototype block byte for byte; version strings `0.2`,
  `dialect-0.2;isa-0.8`, `isa=0.8 … target=0.8` checked).

Size at the end: ~7310 lines, ~59,500 words, 385 kB; 87 verdict examples (82 `llvm`, 5 `c`: 56 accept,
26 reject, 5 blocked), 17 normalisation pairs, 6 executed ISA objects.

## Verification run (final state)

- Every `llvm` block (126) parses and verifies with `opt -passes=verify` on LLVM 18, 20 and 23,
  headless (`env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER
  TMPDIR=$PWD/.tmp`).
- Every `isa object=` block passes `bennett-isa-ref check`; every `hash=` line equals `hash`;
  every `run=` line is the output of `run-oracle`; every `step-check=` claim is the output of
  `step-check` (scratch tool `checkruns.py`: 0 failures).
- Normalisation pairs with `native=` lines: input and output modules compiled with clang 18/23
  and the job's seed implementations, the stated values computed by running them.
- `cc-run=` native statuses (sjlj 77, fiber 98, exit 3) computed by native builds (clang 18 and
  23, -O2); the R-tier `run:`/`reverse:` lines need `run-cc`/`reverse` (b-isa-spec-xam).
- Header: compiles as C and C++ on clang 18/20/23; static asserts on record layouts; IR
  signatures of all 23 prototypes identical across majors and equal to §3.2.
- Corpus: `spec-sem2-ctrl`, `spec-sem2-adj`, `spec-sem2-compute` are byte-equal to §18.8. Baseline
  on a scratch copy of `corpus/legality` with `python3 harness/run.py baseline --majors 18,20,23
  --cases 'cases/spec-sem2-*'` (headless): ctrl agrees on all majors; adj and compute report
  `BASELINE PROBLEM … L1 baseline exit=87` on all majors, because the trace runtime is still at
  ABI v0 (2-argument adj, 3-argument compute); this is bd `-566` (trace runtime at ABI 0.2).

## Decisions taken while writing (not in the outline)

- Primitives `__bennett_nz_alloc` / `__bennett_nz_free` (ISA alloc/free, lift.alloc/lift.free)
  added next to `__bennett_nz_fault`: the runtimes allocator needs a way to reach `lift.alloc`.
- Reserved-name rules apply to *producer inputs* (driver checks before link); runtimes/arith
  bitcode may use `__bennett_rt_/dev_/sf_/nz_` names.
- §5: abstract value = (atom set, TOP flag); TOP never stands for a ROOT atom; K = 4096 cap is
  normative (decides verdicts). Residue classes carry an extent [lo, hi) from array types (B-27).
- §5: `inttoptr` constants are TOP for function pointers (A(F) is fixed only after the
  comparison link); a Julia `@cfunction` constant traps unless it equals an A(F) at run time;
  Bennett.jl's `ptr @f` route keeps the capability.
- §6.5: two realisations: *direct* (handle never stored in memory: CC qreg SSA values, no bound)
  and *static register file* (stored handles; reference instance bound; infinite -> BLK-1).
- §6.6: device-entry pointer parameters get a candidate ROOT(E,i) atom that survives only if it
  reaches a marker handle operand (decides QREG binding).
- §7.5(b): R-tier allocation hoisting uses the reference instance bound; BLK-4 only when infinite.
- §8.1: descriptor layout = LLVM struct {H,[n x Bind],[m x DevBind]} under the datalayout.
- §8.5: snapshot register released by `measure` (unentangled basis state).
- §8.6: wide outputs are the `wide` event: copy-out pairs issued as CC-level region calls
  (`qreg.slice` views, `@xor<w>` action), temporaries freed with the ISA §3.3 dynamic check.
- §8.7: in-place verification computes B_min; run-time budgets checked at the marker (`T-BUDGET`).
- §9.2: budget table JSON schema and precedence (identity > region key > symbol glob > default).
- §9.5 example `budget-device-computed` uses a 64-bit value assembled from 64 measurements, so no
  launch-time token set covers it (a value set like {5, n+5} would be launch-mintable).
- §10: Cl/M/Co object states; slices with classical twins; events applied as CC-level region
  calls (ISA §6 per-region coarse windows make a static action unable to uncompute a slice after
  an arena write); per-slice fault registers retained and combined by `@firstfault`.
- §12.1: N33 runs immediately before N32 (its fpext/fptrunc pairs are FP that N32 rewrites).
- §14.9: blockaddress values are bytes of a driver-added data object `__bennett_rt_blk.<f>`, so
  they never collide with A(F) or other objects.
- §15.2: the default `cpuid` table is read on the build machine and recorded in the build record.
- §16: reference object = wrapper `@ref` + lprocs; layout restricted to closure-reachable
  globals; A_tab chosen so allocation-table overflow never precedes heap exhaustion.
- §18.4: `T-LEAK` outside generations is checked at program end (§6.6's REPL lifetime).
- §19.5: `text_base` rises above the device ranges when they pass 0x400000 (native binary must
  map heap/arena/regions disjointly from its code); §20.1 RAM placed by the profile's linker
  script at 0x80000000 after the other data.

## Departures from the outline

All are in the spec's Appendix A (A1-A23), each with its reason; every one keeps or widens the
outline's capability. Summary: A1 wide outputs by 2k-1 copy-out calls (outline's qxor cleanup is
ill-formed under ISA §6); A2 snapshot release by measure; A3 direct handle realisation without a
bound; A4 exact reference instance bound; A5 Cl/M/Co; A6 slices without stores/markers + classical
twins; A7 one XOR of c ⊕ v; A8 CC-level event application; A9 retained per-slice fault registers;
A10 effects in action regions are fault 8; A11 history as declared outputs measured at the
epilogue; A12 two more primitives; A13 `@cfunction` constants dispatched by value; A14 thunk cycles
resolve to themselves (BD-E-REGION-THUNK deleted); A15 N0 (LLVM's own lowering passes); A16 N34
marks as metadata; A17 wrapper/lproc form and layout rules; A18 compare-tree block names; A19
blockaddress/indirectbr, seven FP formats, exit via hostcall, B_min/T-BUDGET; A20 two more wording
items; A21 `__bennett_rt_platform_ram`; A22 `spec-sem2-*` beside `spec-sem-*`; A23 N33 before N32.

## Examples and checker requirements

The full index is the spec's Appendix B. Capabilities per example family:

| Examples | Checker capability | Executor / CLI |
|---|---|---|
| markers-ir, markers-c | parse, header | LLVM 18/20/23, clang 18/20/23 |
| operand-*, recog-*, attr-*, unwind-invoke, julia-jlplt, effect-lie, pt-variable-index, handle-* (20), qstore-twice, region-* (18), oracle-*, budget-*, indirect-*, asm-musl-syscall, version-flag | parse, recognise | LLVM; Python reference recogniser (to be written in dialect_check.py) |
| inplace-* (4) | parse, recognise, run-oracle | isa-ref `run-oracle` (exists) for the inverse check |
| budget-table=rung4-mini | driver | Python |
| tdl, tdl-overwrite, tdl-effect, tdl-angle (+ tdl=, state=) | parse, recognise, tdl, run-action | Python TDL; isa-ref `run-action` (b-isa-spec-xam, requested) |
| effect-console-r, effect-console-cc; sjlj-two-frames, fiber-pingpong, exit-status (cc-run=) | frontend, run-cc, reverse | isa-ref `run-cc`, `reverse` (requested); native statuses computed |
| 17 normalise-in/out pairs, 10 native= | parse, normalise, native | LLVM; Python normaliser; clang + spec/seeds (not yet created) |
| residual-nsw, residual-clean | validate | Python |
| inc8, add2, rung4-mini, rung8-mini, listsum, switch5 (lift=, linkmap=, object=, hash=, run=, step-check=) | map, check, hash, run-oracle, step-check | isa-ref `check`, `hash`, `run-oracle`, `step-check` (exist; all lines verified) |
| rung4-minidb, rung4-grover-tu (+ native=) | frontend, recognise, native | clang 18/20/23 |
| sem2-ctrl, sem2-adj, sem2-compute (events=, state=) | trace, run-action | trace runtime at ABI 0.2 (bd -566); isa-ref `run-action` (requested) |

Blocked examples (one per BLK): `operand-width-host` and `handle-vec-unbounded` (BD-B-ISA4,
BLK-1), `budget-device-computed` (BD-B-ISA1, BLK-2), `inplace-param-quantum` (BD-B-ISA3, BLK-3),
`region-reversible-qalloc-dynamic` (BD-B-ISA12, BLK-4); each has a `text blocker=` report line.

## Open questions

- Rule ids without an example (P-1 fails on them until added; Appendix B lists them): N0, N12,
  N15, N25, N34, N35; V2-V16; PT12; the OUT binding's object; BLOCK, CLOCK, CONSOLE device
  bindings; entry-state transfer (§8.5); indirectbr; §19.3-§19.8; §20.
- `spec/seeds/` (checker seeds named in §21.4) and `spec/asm/<arch>.toml` (§15.1) are not owned
  paths of this job and do not exist yet.
- ISA wording items raised in §25.2: certificate fields (build record, budget table, deferred
  measurement); ISA §12.2 domains with a fixed classical region (rung 4(a)); `qreg` across CC
  call/ret/br; code 10 "(R only)".
- TDL: event application as CC-level region calls is exact but not one ISA action; an ISA 0.9
  per-cell window rule would allow static actions (efficiency, not capability).

## Issues filed (bd)

- `b-dialect-spec-566`: note added (spec-sem2-adj/compute baseline exit 87; trace runtime to ABI 0.2).
- `b-dialect-spec-d4k`: checker seeds `spec/seeds/` (§21.4) do not exist.
- `b-dialect-spec-gvr`: rule ids without a checked example (P-1 list of Appendix B).
- `b-dialect-spec-rq0`: publish `spec/asm/<arch>.toml` from §15.
- `b-dialect-spec-gwf`: ISA 0.9 wording items raised by §25.2.

`.beads/issues.jsonl` was rewritten by `bd` and is left uncommitted (not an owned path).

## Round-1 fixes

Brief: docs/briefs/2026-10-29-dialect-0.2-council-fixes.md; tracking b-dialect-spec-pz7.
Version 0.2.1 per spec/README.md; ISA 0.8 unchanged. No push.

| Blocker id | Status | Commit |
|---|---|---|
| D02-11 | resolved | this group commit (see git log) |
| D02-12 | resolved | this group commit (see git log) |
| D02-13 | resolved | this group commit (see git log) |
| BD2-5 | resolved | this group commit (see git log) |
| D02-14 | resolved | this group commit (see git log) |
| D02-16 | resolved | this group commit (see git log) |
| D02-17 | resolved | this group commit (see git log) |
| BD2-6 | resolved | this group commit (see git log) |
| BD2-1 | resolved | this TDL group commit (see git log) |
| BD2-2 | resolved | this TDL group commit (see git log) |
| D02-02 | resolved | this TDL group commit (see git log) |
| BD2-4 | resolved | this TDL group commit (see git log) |
| D02-03 | resolved | this TDL group commit (see git log) |
| D02-04 | resolved | this TDL group commit (see git log) |
| D02-05 | resolved | this TDL group commit (see git log) |
| D02-06 | resolved | this TDL group commit (see git log) |
| D02-07 | resolved | this TDL group commit (see git log) |
| D02-08 | resolved | this TDL group commit (see git log) |
| B1 | resolved | this TDL group commit (see git log) |
| BD2-3 | resolved | this interface group commit (see git log) |
| D02-01 | resolved | this interface group commit (see git log) |
| D02-09 | resolved | this interface group commit (see git log) |
| D02-10 | resolved | this interface group commit (see git log) |
| D02-15 | resolved | this interface group commit (see git log) |
| B2 | resolved | this interface group commit (see git log) |
| B3 | resolved | this interface group commit (see git log) |
| B4 | resolved | this interface group commit (see git log) |
| D02-18 | resolved | this interface group commit (see git log) |
| D02-19 | resolved | this interface group commit (see git log) |
| D02-20 | resolved | this R/platform group commit (see git log) |
| D02-21 | resolved | this R/platform group commit (see git log) |
| D02-22 | resolved | this R/platform group commit (see git log) |
