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
| D02-11 | resolved | 25b52ea |
| D02-12 | resolved | 25b52ea |
| D02-13 | resolved | 25b52ea |
| BD2-5 | resolved | 25b52ea |
| D02-14 | resolved | 25b52ea |
| D02-16 | resolved | 25b52ea |
| D02-17 | resolved | 25b52ea |
| BD2-6 | resolved | 25b52ea |
| BD2-1 | resolved | 5186b42 |
| BD2-2 | resolved | 5186b42 |
| D02-02 | resolved | 5186b42 |
| BD2-4 | resolved | 5186b42 |
| D02-03 | resolved | 5186b42 |
| D02-04 | resolved | 5186b42 |
| D02-05 | resolved | 5186b42 |
| D02-06 | resolved | 5186b42 |
| D02-07 | resolved | 5186b42 |
| D02-08 | resolved | 5186b42 |
| B1 | resolved | 5186b42 |
| BD2-3 | resolved | bf9a5f3 |
| D02-01 | resolved | bf9a5f3 |
| D02-09 | resolved | bf9a5f3 |
| D02-10 | resolved | bf9a5f3 |
| D02-15 | resolved | bf9a5f3 |
| B2 | resolved | bf9a5f3 |
| B3 | resolved | bf9a5f3 |
| B4 | resolved | bf9a5f3 |
| D02-18 | resolved | bf9a5f3 |
| D02-19 | resolved | bf9a5f3 |
| D02-20 | resolved | 40a4962 |
| D02-21 | resolved | 40a4962 |
| D02-22 | resolved | 40a4962 |
| V10 / b-dialect-spec-7u1 | resolved: retain all-format bit operations and carrier transport; full dialect/norm 0.2.2 | this commit |

### Round-1 final verification (2026-10-29)

All 32 source JSON blocker ids have resolved normative-text entries in the response.
No declines or text partials; full freeze gate remains incomplete. Group commits are
listed in the table above. Final consistency fixes also update §9.3/§9.4 generation
budget summaries, fault collection, version labels, retired BLK-3 references, hidden
arena base propagation, Q1 candidates and Q2 punctuation, and all-guest Sv39 wording.

- Offline Rust build succeeds. Nine objects check/run, five hash blocks match; new
  arena O1 payloads 1/6 (10 rows), FP aggregate 1099511627521 (10), entry stack 4112 (42).
- Selected final gate parse/header/check/hash/run-oracle/xrefs: 1702/1702, exit 0.
- Full gate: 1939/2029; 90 fail/blocked, compared with baseline 60. The response has the
  exact family counts. Checker issue b-dialect-spec-ofu, append-only questions Q4–Q8.
- Direct dialect_check_v02.py exits 0 but has no main; only frontend execution counts.
- Independent clang18/23 arithmetic, corrected fcmp input/output and ABI vectors,
  aggregate packing and adopting allocator contract executions pass.
- New ISA dependency b-dialect-spec-bz6: BLK-5/ISA-7 requires R fault C with exact record
  code, no later effects, preserved reversible prefix history; no ISA source edits.
- No push. Only owned files committed; generated Beads export remains uncommitted.

## Freeze-gate coverage follow-up (2026-10-29)

Read CLAUDE.md in full, both task beads, checker PROGRESS/LAST-RUN and questions,
this progress file, README and the round-1 response. Checker 56fe08c is read-only.
Example additions do not change semantics; README requires bumps for semantic
changes, so version remains 0.2.1. ISA 0.9 draft 61550b4 is reference-only.

### Round-1 fixes table additions

| Finding | Change | Verification |
|---|---|---|
| BLK-5 / b-dialect-spec-bz6 | Preserve R-budget state, add materialised code-1 example/blocker and exact ISA-0.9 K5/fault-C result | blocked verdict cannot be routed by frozen checker; source and blocker misclassified as producer inputs |
| V10 / b-dialect-spec-7u1 | Filed literal whitelist vs all-format retained fneg conflict; no normative edit | conflicting rules need full boundary reconciliation, so no semantic bump or narrowing |
| P-1 / b-dialect-spec-1jb: driver/platform | Seven concrete input/state scenarios, eight LLVM modules, index rows | parse 564/564; all new recognition accepts; seven state adapters unavailable and seven coverage rows hard-coded False |
| P-1 / b-dialect-spec-1jb: bindings/transfer/indirectbr | Six hand-derived objects, LLVM/linkmap/run companions and index rows | all six object checks and run blocks pass; replay maps exactly; five maps fail |
| P-1 / b-dialect-spec-1jb: V2–V16/PT12 | 15 clean/residual validator pairs and qalloc ROOT return witness, all indexed | parse 522/522; recognise 112/115; V4/V10/V12 missed rejections |
| P-1 / b-dialect-spec-1jb: N0/N12/N15/N25/N34/N35 | Six hand-derived normalisation pairs and Appendix B rows; no rule narrowed | N12 passes; five missing transforms fail loudly |

### Verification table

| Group | Gate | Result |
|---|---|---|
| normalisation omissions | whole direct gate, headless, repository TMPDIR | 2043 pass / 34 fail / 1 blocked (2078); parse 429/429; normalise 19/24 |
| validator/points-to omissions | selected parse,recognise,coverage; headless, repo TMPDIR | 746 pass / 16 fail / 0 blocked (762); 13 remaining coverage rows |
| bindings/transfer/indirectbr | selected parse,map,check,run-oracle,coverage | 697 pass / 12 fail / 0 blocked (709); parse 540/540, check/run 15/15 each, map 9/14, coverage 118/125 |
| driver/platform | selected parse,recognise,state,coverage,xrefs | 2139 pass / 10 fail / 8 blocked (2157); state 28/36, coverage 118/125 |
| BLK-5 | selected parse,recognise,blocker,state,coverage,xrefs | 2142 pass / 12 fail / 8 blocked (2162); parse 567/567, blocker 5/6 |
| final whole gate | direct runner, all families, headless, repository TMPDIR | 2273 pass / 22 fail / 8 blocked (2303), exit 1 |

Normalisation report: `scripts/.tmp/coverage-normalisation.json`. Coverage 96/125
is index discovery only, not successful execution: the six added witnesses remove six
missing-index rows, but five transforms remain red. N0 leaves widenable.condition;
N15 raises “dynamic extract needs select chain”; N25 leaves byval and omits copy;
N34 emits no R marks (rmode attribute ignored); N35 drops volatile without MMIO
routing/poll (platform attribute ignored). These are checker limitations, not
permissions to alter the normative output. N12 passes on all three LLVM majors.


Report: `scripts/.tmp/coverage-validator.json`. All 15 clean validator witnesses
and PT12 ROOT return pass. Negative V4 (ctlz true), V10 (half fneg) and V12
(undefined nonprimitive call in materialised L/R) incorrectly accept; retained
as failing obligations. V8 negative also triggers V13, so this does not claim
an independent pre-N21 V8-pattern implementation. No normative text was fixed.


Report: `scripts/.tmp/coverage-bindings.json`. The six hand-authored objects
were checked/hashed/run independently with Rust before insertion; Python only
serialised symbol/layout facts and inserted the executor's interface hashes.
Hand-derived successes: OUT byte 9 / 10 rows; CLOCK 3 / 16 rows; BLOCK first-byte
42 or 255 / 16 rows; CONSOLE 120 / 27 rows; replay byte 7 / 16 rows; indirectbr
7 or 9 / 9 or 12 rows, no-match code 4 / 10 rows (the failing path never executes
wrapper retval). Clock store rematerialises its global-address operand per map
row conventions; no commoning optimisation is assumed. The replay object maps
byte-exactly, isolating caller-mutated G replay with k=0; general allocation/stack
replay remains covered by the earlier runtime vectors, not claimed here.

Five frozen mapper gaps remain: OUT explicitly raises checker-unimplemented;
BLOCK ignores its interface and model-state prologue; CLOCK ignores counter
initialisation; CONSOLE omits buffer/prologue/output delivery; indirectbr explicitly
raises checker-unimplemented. The binding objects and their expectations remain
unchanged to expose these gaps. Seven hard-coded driver/platform coverage failures
remain regardless of examples (dialect_meta.coverage sets them False).


Report: `scripts/.tmp/coverage-driver.json`. All new source modules parse and
recognise; all 1309 xrefs pass. Each driver operation has a concrete hand-derived
expected state, not merely a section mention. Seven missing state adapters fail
explicitly under P-2 (reported as blocked by this checker). The fallback labels
them “TDL state execution” / b-isa-spec-xam, but all CLI commands exist: missing
capabilities are synthesis, placement promotion, comparison-link layout, snapshot
rewrite, closed-unit fallback, mixed-major link, and the platform UART path.
None can be executed by current families just by adding a tag. In addition,
coverage unconditionally sets all seven section obligations False, irrespective
of Appendix B rows. Recorded on 1jb and Q12; never weakened or removed.


Report: `scripts/.tmp/coverage-blk5.json`. ISA 0.9 draft commit 61550b4,
section 0.2 K5 and section 4.1 fault row were read: literal C < 2^64, zero
effectively 4, exact nonzero terminal record, FAILED, no successor effects,
reversible prefix retained. The expected under-0.9 budget result is code 1,
empty console/tape, exactly one terminal record with no host request; it still
requires dialect counter instrumentation, not host fuel. Section 25.1 already
had BLK-5 in the same table form as BLK-1/2/4; added witness/draft-reference
paragraph, without changing the ISA-0.8 grading target.

Both materialised code-1 witness and blocker report carry blocked:BD-B-ISA7.
The original state check is retained, with the same verdict and required 0.9
result alongside. Frozen recognition and blocker methods allow materialised
reserved primitives only when id == r-fault-code, so the new r-budget-prefix
example/report wrongly produce BD-E-MARKER-UNKNOWN; state dispatch ignores the
verdict and still probes host fuel. It cannot pass as a blocker-family verdict
without a checker change. This is recorded on bz6, 1jb and Q13, not hidden by
renaming to the special-cased example or removing the original state obligation.

New normative finding b-dialect-spec-7u1 quotes V10's extended-format exception
list and the conflicting section 13.1/16.4 retained-fneg contract. The literal
V10 negative is retained to expose the conflict. The earlier “missed rejection”
classification for V10 is superseded: unlike V4/V12 this is not simply a checker
fix. The intended complete exception boundary also includes retained FP
intrinsics and carrier interfaces, so a complete semantic fix is not uniquely
specified by this coverage task. No normative rule was changed; version 0.2.1
remains appropriate under README.

### Final freeze-gate verification (2026-10-29)

**Not green; round 2 is not ready.** All 35 omissions have concrete added
witnesses and index evidence, but P-2 execution still fails. Do not interpret
118/125 index coverage as implemented capabilities. No checker code changed,
no check removed, no expectation weakened, no push, and no semantic version bump.
This section supersedes the historical open-questions list and earlier counts.

Command (absolute paths; environment headless):

```sh
env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER TMPDIR=/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp python3 /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/dialect_check_v02.py --json /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp/editor-final-freeze.json
```

Spec tested: b7330de, draft 0.2.1; checker remains 56fe08c. Interpreter receipt:
commit 8503d818b7cd96b95682e5970596790b364ea6a6, source fingerprint
4b829170d7c6dcfbb5bc04a713861c01217fd20b55997321bea69e431aceeb96
(the checker snapshots current dependency sources; different group receipts
reflect concurrent dependency work). Full report and stdout are repository-local
`scripts/.tmp/editor-final-freeze.json` and `editor-final-freeze.log`.

| Family | Passed | Failed | Blocked |
|---|---:|---:|---:|
| asm | 1 | 0 | 0 |
| blocker | 5 | 1 | 0 |
| cc-run | 8 | 0 | 0 |
| check | 15 | 0 | 0 |
| coverage | 118 | 7 | 0 |
| driver | 1 | 0 | 0 |
| events | 3 | 0 | 0 |
| frontend | 15 | 0 | 0 |
| hash | 5 | 0 | 0 |
| header | 1 | 0 | 0 |
| map | 9 | 5 | 0 |
| native | 13 | 0 | 0 |
| normalise | 19 | 5 | 0 |
| parse | 567 | 0 | 0 |
| recognise | 120 | 4 | 0 |
| run-oracle | 15 | 0 | 0 |
| run-program | 5 | 0 | 0 |
| seeds | 1 | 0 | 0 |
| state | 28 | 0 | 8 |
| step-check | 6 | 0 | 0 |
| tdl | 9 | 0 | 0 |
| trace | 3 | 0 | 0 |
| xrefs | 1306 | 0 | 0 |
| **Total** | **2273** | **22** | **8** |

Exact remaining red obligations (no other family is red):

| Family | Checks | Why |
|---|---|---|
| coverage (7) | §19.3, §19.4, §19.5, §19.6, §19.7, §19.8, §20 | coverage() hard-codes False despite added source/state/index evidence |
| normalise (5) | n-lower-widenable, n-dynamic-lane, n-byval-copy, n-rstep-return, n-platform-mmio | absent LLVM N0 lowering, dynamic lane chain, byval copy, R marks, platform routing/poll respectively |
| map (5) | binding-out-byte, binding-block-byte, binding-clock-read, binding-console-byte, indirectbr-two-blocks | OUT and indirectbr explicitly unimplemented; BLOCK/CLOCK/CONSOLE model prologues/interface/delivery absent |
| recognise (2) | validator-v4-residue, validator-v12-residue | ctlz(true) and unresolved L/R callee wrongly accept |
| recognise (1) | validator-v10-residue | literal V10 forbids half fneg, but retained-operation rules permit it; normative conflict 7u1 |
| recognise + blocker (2) | r-budget-prefix (one in each family) | materialised recognition only enabled for the hard-coded older r-fault-code id; new primitive use wrongly rejected as producer input |
| state (1 blocked) | r-budget-prefix | verdict ignored; still probes host fuel, which cannot establish typed fault 1 before the first effect |
| state (7 blocked) | driver-oracle-synthesis, driver-pointer-promotion, driver-comparison-layout, driver-snapshot-initializer, driver-closed-unit-fallback, driver-mixed-majors, platform-uart-write | actual driver/platform adapters absent; generic TDL/xam unavailable diagnostic, not missing published ISA commands |

All 567 LLVM parses pass. All 15 object checks and 15 run blocks pass, including
all six new objects. The entry replay object maps exactly. Previously passing
normalise/native/CC/R/TDL/trace families retain their earlier examples.

Group commits: 4e8de56 normalisation; c3977f9 validator/PT12; 2a0358a binding
objects/replay/indirectbr; 02ebe2a driver/platform; b7330de BLK-5 and V10 finding.
Tracking: notes on b-dialect-spec-1jb and b-dialect-spec-bz6; new bug
b-dialect-spec-7u1. All remain open because the freeze gate is not green.
Append-only checker questions Q9–Q13 (plus final Q14) record the required follow-up.
Generated .beads/issues.jsonl stays outside the owned-path commits.

## V10 post-round correction (2026-10-29, b-dialect-spec-7u1)

The coverage-follow-up reports above describe the pre-correction 0.2.1 baseline.
This correction resolves the normative conflict, not the other freeze-gate gaps.

Before editing, re-derived both readings by hand and recorded them in a Beads note:

- Literal V10: load half and bitcast are exceptions, but fneg half is not, so the
  old residue witness rejects. The same reading also excludes the retained
  fabs/copysign calls and extended-format calls, returns and aggregate transport.
  Removing those forms would contradict §13.1's unchanged row, §13.3's all-seven-
  format contract, §16's carrier map and NS §3.2's bit-exact promise. It narrows scope.
- Retained-operation reading: N32/N33 remove arithmetic/comparison/conversion;
  §13.1's bit operations and §16's transport remain. For half carrier bits b,
  fneg is b xor 0x8000, including NaNs. Residual fadd half must still reject:
  its materialised replacement uses __bennett_sf_add_f16 on i16 carriers.

Deciding sentence: **V10 must permit every bit-exact operation retained by §13.1
and every carrier transport admitted by §16, for all seven floating-point formats.**
Rule 10 selects the second reading; there are not two non-narrowing alternatives.

Edited only the V10 exception row, its explanation/witnesses and Appendix B,
plus the version labels required by spec/README.md and §23. The positive now
retains fneg half; the negative retains fadd half instead. New indexed
validator-v10-carriers accepts fabs/copysign plus defined-call/return/aggregate
transport. V4/V9/V12 still apply to calls. §13.1 and §16.4 are unchanged.
Full dialect and norm advance to 0.2.2 because a normative rejection changed;
unchanged sub-artefacts, ISA 0.8, map 0.2.1, reference objects and hashes stay put.

Verification, headless, project TMPDIR, Python -B, LLVM stdin/stdout only:

- Reproduced the pre-edit mismatch: old V10 residue declared reject, checker accepts.
- All 190 tagged LLVM blocks verify on LLVM 18/20/23: 570/570.
- All three V10 verdicts match the read-only checker: accept/reject/accept.
- Seven-format probes cover retained bit operations, load/store/select/phi,
  bitcast, parameters, defined calls, returns and aggregate field transport;
  each accepts, and its fadd variant rejects. All 14 modules verify on all
  three majors (42/42). These are supplemental probes, not new spec examples.
- Independent LLVM instcombine folds agree with b xor 0x8000 on ten half bit
  patterns per major (30/30), including signed zero, infinities and signaling/
  quiet NaNs with nonzero payloads.
- Current 0.2 cross-reference checker: 1310/1310. The legacy 0.1 helper reports
  the same seven failures as e74d70c; it is not the current cross-reference gate.

The full preflight was not run: it writes under checker-owned scripts/.tmp and
may build scripts/.isa-ref, which are read-only for this editor. Manifest/checker
version synchronization to 0.2.2 is tracked as b-dialect-spec-bvy for their owner;
SPEC_VERSIONS.toml and scripts were not edited. The full freeze gate is not
claimed green. Original finding 7u1 is resolved; no push. Beads export remains
outside the commits; the orchestrator owns the session worklog.

## Round-2 fixes

Tracking b-dialect-spec-1zy; draft/full norm 0.2.3, ISA 0.8.

| Item | Status | Commit group |
|---|---|---|
| SOL-R2-03 | resolved | f868741 |
| SOL-R2-04 | resolved | f868741 |
| R2-CODEX-04 | resolved | f868741 |
| REG-CODEX-N27 | resolved | f868741 |
| SOL-R2-02 | resolved | f868741 |
| R2-CODEX-02 | resolved | f868741 |
| R2-CODEX-01 | resolved | f868741 |
| SOL-R2-01 | resolved | 2fa3460 |
| REG-SOL-TDL9 | resolved | 2fa3460 |
| R2-CODEX-03 | resolved | 2fa3460 |
| BD3-1 | resolved | 2fa3460 |
| BD3-2 | resolved | 2fa3460 |
| BD3-3 | resolved | 2fa3460 |
| REG-MUSE-7.7 | resolved | 2fa3460 |
| BD3-6 | resolved | 2fa3460 |
| BD3-4 | resolved | a9e9563 |
| BD3-5 | resolved | a9e9563 |
| E-MUSE-TERM | resolved | a9e9563 |
| E-MUSE-7.7 | resolved | a9e9563 |

Group receipts: f868741 (vectors/materialisation/memory), 2fa3460 (action lifetimes).
BD3-5 uses the explicitly permitted conservative default, optional finite-bound refinement
b-dialect-spec-egm; external typed R semantics remain b-dialect-spec-bz6. No declines/partials.

## Round-2 final freeze — 2026-10-29

**2401/2401 passed; 0 failed; 0 blocked/unavailable.** Version 0.2.3,
ISA grading target 0.8. Tested spec/checker snapshot 5ba4b27427fefda4bde84218e9dbba0e2a7475f8.
Spec SHA-256 110c07deae4bf44cce7564f2149d9ad742c8135bd2ce8c788c12d4db74c0df0c.
Independent interpreter b7014019b2be1fed73b146823d08d7120baae23b, source fingerprint d2d8bfe19d97410f37b65125942d2db23852c4d7434ed0f84dda8fb88ddaa7c6.

| Family | Passed | Failed | Blocked |
|---|---:|---:|---:|
| asm | 1 | 0 | 0 |
| blocker | 15 | 0 | 0 |
| cc-run | 8 | 0 | 0 |
| check | 15 | 0 | 0 |
| coverage | 125 | 0 | 0 |
| driver | 1 | 0 | 0 |
| events | 3 | 0 | 0 |
| frontend | 21 | 0 | 0 |
| hash | 5 | 0 | 0 |
| header | 1 | 0 | 0 |
| map | 14 | 0 | 0 |
| native | 19 | 0 | 0 |
| normalise | 29 | 0 | 0 |
| parse | 606 | 0 | 0 |
| recognise | 127 | 0 | 0 |
| run-oracle | 15 | 0 | 0 |
| run-program | 5 | 0 | 0 |
| seeds | 1 | 0 | 0 |
| state | 44 | 0 | 0 |
| step-check | 6 | 0 | 0 |
| tdl | 10 | 0 | 0 |
| trace | 3 | 0 | 0 |
| xrefs | 1327 | 0 | 0 |
| **Total** | **2401** | **0** | **0** |


Exact headless freeze command (absolute paths):

```sh
env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER TMPDIR=/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp python3 /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/dialect_check_v02.py --json /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp/round2-fixes-freeze.json
```

36 checker unit tests pass via the repository unittest runner; pytest is not installed.
4 legacy runtime tests pass. No expectation weakened, no ISA source edited, no push.
Program-end fault release executes fresh-copy measurement and conditional correction/free
through Rust run-cc; superposed statistics and loop/deferred-channel checkpoints execute
through run-action. BLK-5 is a passing dependency verdict, not typed-fault execution on 0.8.
BD3-5 uses the explicitly permitted conservative default, not a claimed N=2 proof;
optional finite-bound refinement is b-dialect-spec-egm. No declines or partial resolutions.

## Round-3 council fixes — b-dialect-spec-zax

Theme A resolved SOL-R3-01, R3-CODEX-01, BD3-R3-1 and both regressions.
0.2.4 restores clean control workspace; B2 keeps its compute/out-of-place interface
and cannot invent a standalone inverse. Red-green loop unittest passed; new state
adapters execute Rust run-action and native exhaustive collision validation.
Full freeze pending the remaining themes; no green full-gate claim yet.
