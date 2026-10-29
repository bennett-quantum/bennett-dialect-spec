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
