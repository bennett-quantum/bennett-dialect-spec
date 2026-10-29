# Dialect 0.2 pre-flight checker progress

Tracking: `b-dialect-spec-qxd`; seeds `b-dialect-spec-d4k`; asm data
`b-dialect-spec-rq0`; missing rule examples `b-dialect-spec-gvr`.
Implementation sub-agent owns commits under the current user authorization. Never edit the protected spec/header/version files
or `corpus/legality/cases/spec-*`.

## Current milestone: contract inventory

Read CLAUDE.md, HANDOFF.md, Beads skill and `bd prime`, spec §1.5/§1.6,
Appendix B, outline part D, author progress, current checker, toolchains,
interpreter README and the three requested beads. Reading the detailed mechanism
rules and harness continues before implementation of each family.

| Family | Status | Validation / outstanding work |
|---|---|---|
| parse / header | inherited 0.1, incompatible | reproduce crash; 23 markers, implied primitives, all majors |
| recognise / candidates / blockers | implementing | replace 0.1 restrictions with §5–§9 rules |
| normalise / validate | pending | 17 pairs; §12 rules and V1–V16 |
| native / seeds | pending | create seeds and independent clang 18/23 differentials |
| map / check / hash / run-oracle / step-check | pending | snapshot interpreter source, build offline, record commit |
| tdl / run-action | pending | CLI b-isa-spec-xam; poll README |
| cc-run / reverse / run-program | pending | CLI b-isa-spec-xam; poll README |
| trace / events / state | pending | ABI 0.2 runtime b-dialect-spec-566 |
| asm | pending | derive TOML rows from §15 |
| cross-references / coverage | pending | derive rule index; missing examples must fail |
| --list / --family / final table | pending | every tag accounted for; failures isolated |

## Verification

Initial command (reproduced `KeyError: effect_console_write`): `env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS
-u BROWSER python3 scripts/dialect_check.py` (running at initial inventory).
All checker subprocesses will enforce headless execution and repository-local temporary files.

## Next / questions / findings

Implement reporting and regression tests first, then the recogniser and independent
executor adapters. Record ambiguous readings in CHECKER-QUESTIONS.md and Beads.
The spec explicitly lists missing rule coverage in Appendix B; it must remain red
until the editor supplies those examples. No findings filed yet.

## Milestone 1 — executor and reporting foundation

Added `dialect_check_v02.py` runner; reused original parser and marker/header handling.
Headless subprocesses, isolated failures, `--family`, `--list`, JSON report, summary table.
Red regression suite observed failing before implementation (`ModuleNotFoundError`, then
explicit recogniser-unimplemented failures); validator/mask/inventory checks now pass.

Verified: `python3 scripts/dialect_check.py --family parse,header,check,hash,run-oracle
--json scripts/.tmp/initial.json`: **393/393 checks passed** (378 LLVM cells, 6 objects,
6 run blocks, 2 hash blocks, header agreement). Build commit: `89474da58cfc6b0d68b3eced0b43e3fbe16cd129`;
source SHA256: `71ffa095d4f62f32a1ed2b673e4e4764d7bc4bdcf7473187e338efb6ad44e1e9`. Build receipt contains per-file digests.

Next: 0.2 recogniser, normaliser, map and remaining families. All unimplemented tags
currently fail explicitly; do not confuse the passing selected families with the full gate.

## Milestone 2 — 0.2 recogniser

`dialect_flow.py` implements shared pointer/function/handle propagation, extent-aware
array indexing, dynamic lanes, tracked memory, candidate expansion and thunk cycles,
handle containment, unique-candidate region rejections, descriptors, budget blocker
classification, TDL overwrite/angle rules and instance blockers. Inverse pairs use
Rust `run-oracle` over every input, with finite ARG specialisation.

Verified: `python3 scripts/dialect_check.py --family recognise`: **81/82 passed**.
Remaining failure is finding **b-dialect-spec-0t9**, question Q1 in
CHECKER-QUESTIONS.md. Unit regressions (7 tests) pass. The new 17-pair normaliser
regression was run red (17 missing-implementation errors) before implementation.

Next: implement N-rules and native seeds, complete interpreter map, trace ABI and
command adapters. Strengthen instance-bound calculation to use LLVM ScalarEvolution
instead of the temporary syntactic bound recogniser before calling this family complete.

## Milestone 3 — materialised normalisation

`dialect_normalise.py` implements the transformations exercised by all 17 pairs,
including vector lanes, wide-add limbs, shadow frames, memory/integer intrinsics,
sequential atomics, varargs memory ABI, explicit EH, asm syscall and FP carriers.
`python3 -m unittest discover -s scripts -p test_dialect_check.py`: **8 tests pass**,
including all 17 pairs (observed red first). `python3 scripts/dialect_check.py
--family normalise`: **17/17 pass**, exact output, validator, generated LLVM 18/20/23.

Native differential adapters and independent C seeds are being verified. Trace runtime
has opt-in `BENNETT_MARKERS_ABI=2`; legacy ABI remains the default for old corpus cases.
`python3 -m unittest discover -s corpus/legality/harness -p test_runtime.py`: 4 pass.
Artifacts now persist under scripts/.tmp/run-* so reported commands remain reproducible.

## Milestone 4 — lifting map and native differentials

`dialect_map.py` independently emits wrapper/lprocs, globals, layout, memory bounds,
recursive calls, indirect dispatch, phis and compare trees. It never reads object=
text to produce the map. Rust computes/checks the emitted identities.
`python3 scripts/dialect_check.py --family map`: **6/6 pass**, byte-exact objects.
A red switch-tree numbering mismatch was corrected by numbering constants in final
printed block order, as §16.3 requires.

`dialect_native.py` parses the stated vectors and builds/runs both modules (or C
and materialised IR) on clang 18/23. **10/10 native blocks pass**, including all
rung4 rowids and its fault path. Seeds runtime.c/softfloat.c supply independent
shadow stack, memory, EH catch-all, syscall, integer popcount, binary64 add/mul/cmp.
No host libm is used by the soft-float seeds. More seeds/self-tests and seed index
still needed before closing d4k. Full frontend currently 11/15; remaining cast-flag
parser errors are implementation work, not spec findings. Prefix step-check run is
still active; inspect scripts/.tmp/steps.log and process state before repeating it.

## Milestone 5 — frontend, trace, metadata

All **15/15 C frontend** checks pass on 18/20/23 after post-link lto<O3>.
All **3/3 trace** and **3/3 events** checks pass over LLVM 18/20/23 and inputs 0..3,
using ABI 0.2 opt-in runtime builds; `test_trace_abi02` was observed red before
implementation, now the 9-test checker suite passes. Legacy trace tests also pass.
State checkpoints require run-action; the interpreter README still lacks the new
CLI commands. Fixing the sem2-ctrl generated controlled-action spelling precedes
its command availability check.

Asm TOML published for x86-64/aarch64/riscv64 from §15 + platform patterns §20.2;
`--family asm` passes; rq0 claimed. `--family driver,blocker` passes (1 + 5).
Coverage mechanically reports **35 missing obligations**, consistent with gvr.
Xrefs: 1290/1291 pass. The remaining comma-inherited NS §17.1 reference at line
4654 is filed as a spec-0.2-finding (see Beads; issue id recorded at next update).
Q2/Q3 document reference-list and asm-pattern readings.

Next: complete/validate seeds inventory, CLI fixture adapters for CC/R/TDL, replace
instance-bound heuristic with ScalarEvolution, strengthen recogniser/validator
precision and regression mutation tests. Full gate has not yet been run.

## Resume milestone 6 — draft 0.2.1 core adapters

Resumed from milestones 1–5, not the previous session. Q4–Q8 read in full.
Added the direct runner entry point (previously a no-op), corrected fcmp enum and
normalisation, rounded shadow frames, FP/aggregate carriers and aggregate return
packing, native n-fcmp/fp-aggregate/entry-stack adapters and allocator adoption,
version recognition 0.2.1, materialised primitive recognition and explicit ISA-7
blocker reporting. Retired BLK-3 classification; parameterised pairs are tracked
for their CC expansion rather than rejected.

Red-green: existing normalisation tests failed for n-fcmp/n-varargs; new seed,
native-driver, materialised/blocker and aggregate map regressions failed before
implementation. Now 15 unit regressions pass. Selected direct gate
normalise/native/recognise/blocker/map/driver: **128/128**. Headless, repo TMPDIR.
Native 13/13, normalise 18/18, map 7/7, recognise 84/84, blocker 5/5.

Baseline reproduced 1940/2030 (the current text has one additional xref/check
relative to the editor's report); 35 coverage obligations remain explicitly
missing in Appendix B. They cannot be removed or made green by weakening P-1.
Next: independent boundary/state adapters; then inspect the published interpreter
command contracts and wire TDL/CC/R. No spec, docs, worklog or ISA edits.

## Resume milestone 7 — executable boundary and CC adapters

Added packed sub-byte vector loads, partial top-limb memory/arithmetic and wide
sign extension, and GC GEP provenance queries. New boundary regression was red
before these changes. Five state witnesses now execute native generated LLVM
and/or recogniser/budget obligations: normalisation-boundaries, fcmp-abi,
fp-sign-carrier, inplace-bound, r-fault-code. clang 18/23 observations are compared
with stated vectors, including a wrong-expectation mutation. 17 regressions pass.

Read dependency README and commit log after core adapters: run-cc and reverse
landed as bc63483/d987500; README Commands lags, while executable --help documents
them. Command discovery now checks both. Rebuilt original interpreter offline as
requested and refreshed the isolated snapshot. CC fixtures were red on invented
addr/gep.i8 pseudo-ops; replaced with ISA pointer conversion/add. **cc-run 8/8**
now passes, including console tape, host transcript, native statuses and reversal.
run-action/run-program remain absent from --help at this milestone. TDL/state
adapters continue; no placeholder result is treated as an execution.

## Resume milestone 8 — TDL and wrapper execution

run-action (9d4c0dc), run-program (623a9bb) and the README Commands contract have
landed. The independent snapshot now includes commit
8503d818b7cd96b95682e5970596790b364ea6a6, fingerprint
c3e15311b38c410de7af163f2825cb53f5b39c7dda9f28d1ee52359d153f2267.
Added dialect_tdl.py: source-derived worked partitions/events, per-event Rust
action execution, coherent arena read calls, retained compute history, clean
slice/fault scratch, parameterised CC in-place expansion, branch views, all-zero
success predicates and deferred-channel probabilities. Boundary adapters execute
wide common projection budgets, caller-backing replay, 128-bit snapshot release,
partial observation, native Cl/M/Co transitions and supervisor Sv39 aliases.
Arena O1 now has an independent byte-exact map with hidden-base threading.
Native seed fixtures are indexed in spec/seeds/README.md.

New TDL/artefact/wrapper/arena/program/extent tests ran red before adapters or
fixes. Fixed a real PT2 bug: a dynamic GEP used the declared array dimension as
an index bound; now it uses the underlying allocation extent. One-shot launch
checks wrap R entries in CC and use run-program. No specification example was
removed. The command view-pass guard no longer mistakes compute-view filenames
for LLVM passes; it still rejects actual view pass options.

An overlapping verification exposed the inherited mutable snapshot race. Stopped
those runs, then replaced snapshot deletion with immutable content-addressed
sources and a build lock; receipts identify the exact source and commit. No ISA
source edits. Direct full gate (before final A_tab link-fact correction) reached
1994/2031: only 35 coverage rows, arena map layout and R-budget prefix red.
The arena layout correction and all five run-program adapters now pass targeted
regressions. The R-budget prefix is a real ISA-7 dependency, not missing CLI:
--budget 0 is host fuel and diagnoses "CC/R has no ISA step budget". A concrete
R fixture and its diagnostic are retained; no generic trap is substituted.
Coverage bug b-dialect-spec-1jb filed (also b-dialect-spec-gvr). Final verification
and exact family table follow below after rerunning the final code.

## Final resume verification — 2026-10-29

Spec snapshot: c61de71, draft 0.2.1. Direct freeze gate:
`env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER
TMPDIR=/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp
python3 /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/dialect_check_v02.py
--json /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp/final-gate.json`.
**Exit 1: 2000 passed / 35 failed / 1 blocked / 2036 total.**
No skip, removed example or rewritten spec expectation. Six extra checks compared
to the resumed runner: independent arena-O1 map plus five one-shot launch checks.
The resumed reproduction was 2030 checks; the editor's earlier report was 2029.

| Family | Passed | Failed | Blocked |
|---|---:|---:|---:|
| asm | 1 | 0 | 0 |
| blocker | 5 | 0 | 0 |
| cc-run | 8 | 0 | 0 |
| check | 9 | 0 | 0 |
| coverage | 90 | 35 | 0 |
| driver | 1 | 0 | 0 |
| events | 3 | 0 | 0 |
| frontend | 15 | 0 | 0 |
| hash | 5 | 0 | 0 |
| header | 1 | 0 | 0 |
| map | 8 | 0 | 0 |
| native | 13 | 0 | 0 |
| normalise | 18 | 0 | 0 |
| parse | 393 | 0 | 0 |
| recognise | 84 | 0 | 0 |
| run-oracle | 9 | 0 | 0 |
| run-program | 5 | 0 | 0 |
| seeds | 1 | 0 | 0 |
| state | 28 | 0 | 1 |
| step-check | 6 | 0 | 0 |
| tdl | 9 | 0 | 0 |
| trace | 3 | 0 | 0 |
| xrefs | 1285 | 0 | 0 |

Every remaining red coverage row fails P-1 because it lacks the required
accepted example/index evidence (Appendix B explicitly preserves these failures;
b-dialect-spec-gvr and newly filed bug **b-dialect-spec-1jb**, label dialect-precheck):

- `N0`: no required checked accept example/index evidence.
- `N12`: no required checked accept example/index evidence.
- `N15`: no required checked accept example/index evidence.
- `N25`: no required checked accept example/index evidence.
- `N34`: no required checked accept example/index evidence.
- `N35`: no required checked accept example/index evidence.
- `PT12`: no required checked accept example/index evidence.
- `V10`: no required checked accept example/index evidence.
- `V11`: no required checked accept example/index evidence.
- `V12`: no required checked accept example/index evidence.
- `V13`: no required checked accept example/index evidence.
- `V14`: no required checked accept example/index evidence.
- `V15`: no required checked accept example/index evidence.
- `V16`: no required checked accept example/index evidence.
- `V2`: no required checked accept example/index evidence.
- `V3`: no required checked accept example/index evidence.
- `V4`: no required checked accept example/index evidence.
- `V5`: no required checked accept example/index evidence.
- `V6`: no required checked accept example/index evidence.
- `V7`: no required checked accept example/index evidence.
- `V8`: no required checked accept example/index evidence.
- `V9`: no required checked accept example/index evidence.
- `binding:OUT`: no required checked accept example/index evidence.
- `device:BLOCK`: no required checked accept example/index evidence.
- `device:CLOCK`: no required checked accept example/index evidence.
- `device:CONSOLE`: no required checked accept example/index evidence.
- `§8.5 entry-state transfer`: no required checked accept example/index evidence.
- `§14.9 indirectbr`: no required checked accept example/index evidence.
- `§19.3`: no required checked accept example/index evidence.
- `§19.4`: no required checked accept example/index evidence.
- `§19.5`: no required checked accept example/index evidence.
- `§19.6`: no required checked accept example/index evidence.
- `§19.7`: no required checked accept example/index evidence.
- `§19.8`: no required checked accept example/index evidence.
- `§20`: no required checked accept example/index evidence.

The only blocked execution is **state/r-budget-prefix**: dialect §17.6 requires
typed code 1 before the first counted instruction and no later console/tape effect.
The concrete `r-budget-prefix.bisa` is parsed, hashed and checked, then run with
`run-cc ... main --budget 0`. The published CLI diagnoses
`§3.4: reference execution fuel exhausted; CC/R has no ISA step budget`.
Host fuel does not implement N34; ISA 0.8 has no R `fault C`. Blocked on
**b-dialect-spec-bz6 / ISA-7** (and the already tracked ISA change), not on a
missing CLI. No generic trap is claimed equivalent. The exact command and stderr
are in final-gate.json/log and the run directory's r-budget-prefix.diagnostic.

All requested commands have landed: run-cc, reverse, run-action, run-program.
There are **no checks waiting on an unlanded CLI command** from b-isa-spec-xam.
The final source snapshot receipt records commit `8503d818b7cd96b95682e5970596790b364ea6a6`, SHA256 `5178cabb4c3c2c6dcbf20a37da9b8679487deb54fe03f73b530c32572b6cc779`.
The immutable snapshot and concrete run files remain under ignored scripts/.isa-ref
and scripts/.tmp. Machine report: scripts/.tmp/final-gate.json; log: final-gate.log.

Validation: 26 checker unit regressions (including deliberately wrong expectations,
new adapters, real ISA-7 probe, exact arena/aggregate maps and headless guard);
4 legacy runtime tests; LLVM 18/20/23 and native clang 18/23 within the full gate.
`--family driver --list` passes; `git diff --check` passes. The freeze gate remains
red and gyl/ofu remain in progress for the editor-owned coverage and ISA-7 work.
No push, protected file edits or ISA source edits. Generated Beads JSONL is outside
the owned paths and is intentionally left uncommitted.

## Freeze repair item 1 — driver/platform scenario execution

Read all requested handoffs, Q1–Q14, editor freeze JSON (2303 rows), and beads
1jb/7u1/bz6. Added seven executable scenario adapters: source-derived oracle
wrapper and ISA runs; points-to placement with caller promotion and native
pointer-chain run; comparison layout/images and ISA/native run; snapshot rewrite
and SHA-256 build record; closed-unit fallback and indirect native call; real
18/23 bitcode read/link and version negatives; UART console effect and whole-state
ISA reversal. Fixed transitive pointer-initialiser data retention in the mapper.
Coverage now requires successful scenario execution plus index evidence.
Regression was red before implementation; seven scenarios and wrong-expectation
mutations now pass. Selected gate coverage 125/125, driver 1/1, all seven new
state adapters pass. R-budget remains the old bz6 probe until item 5.
No spec or ISA source edits. Snapshot rebuilt offline through the existing
immutable build path; the runner records its actual dependency commit.

## Freeze repair item 2 — N0/N15/N25/N34/N35

Normalisation now consumes rmode/platform/LLVM-major context. N0 invokes LLVM's
normative lowering passes; N15 builds scalar dynamic-lane selection with the
out-of-range zero/unchanged-vector semantics; N25 creates caller-owned copies
in the shared shadow frame; N34 preserves and emits pre-instruction metadata
through the R closure; N35 routes volatile memory before N9 and inserts entry
and loop-back-edge polls. All 24 exact pairs ran red before implementation and
now pass, including validator and LLVM 18/20/23 verification. Each major runs
its own N0 lowering. No changed or omitted expected output.
