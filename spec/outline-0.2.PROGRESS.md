# Dialect 0.2 outline — progress

Job: write `spec/outline-0.2.md` (structure and mechanism decisions for dialect draft 0.2;
phase 3 step 1 of `bennett/docs/plan/2026-10-29-path-to-north-star.md`). Owned paths: this
file and `spec/outline-0.2.md`. Standing rule: no narrowing of north-star scope.

## Read (2026-10-29)

- [x] `bennett/docs/Bennett-NorthStar.md` (all, iteration 7)
- [x] `bennett/docs/plan/2026-10-29-path-to-north-star.md`
- [x] `docs/spikes/2026-10-28-legality-findings.md` (decisions 1-3, defaults §4)
- [x] `docs/audit/2026-10-29-dialect-0.1-narrowing-audit.md` (all 96 rows, ISA-1..11, G-12..16, TDL-1..10)
- [x] `docs/spikes/sqlite/REPORT.md` (route A, inventory, work items §8)
- [x] `spec/Bennett-Dialect-Spec.md` draft 0.1 (all sections; examples skimmed)
- [x] bd: epic `b-dialect-spec-8wf` children .1-.40 (audit-row mapping), C1-C7 items
- [x] ISA 0.8 §1-§7, §9.1-9.2, §10, §12-§14, §16.2-16.3, §17
- [x] `bennett/docs/council/rubric-isa.md`
- [x] `bennett-isa-spec/reference-interpreter/README.md`, `PROGRESS.md`, `SPEC-QUESTIONS.md`
  (CLI today: check, hash, run-oracle, step-check; library: ClassicalMachine, QuantumRegisters,
  execute_action; CC qreg integration in progress)

## Done

- Part A: section-by-section outline, §1-§25 (commit 89a816c and later)
- Part B: mechanism decisions B1-B17 plus the B-BLK blocker list (387e33f)
- Parts C-F: rung table, precheck plan, open questions E1-E14, bd closure map (1aebb9b)
- Review fixes (c93d7e9 and the final commit):
  - run-time-address arena writes via `qstore`;
  - `observe` via a `qload` copy plus `measure`;
  - the `__bennett_qprep` marker;
  - the snapshot concat tree;
  - effect markers in CC go through `hostcall`;
  - Co-width `qalloc` padding;
  - Rust/Julia bitcode sources.

## Key decisions (summary)

- Lifted subset = all materialised LLVM.
- Oracle interface descriptor in memory (`IN`/`ARG`/`MEM_IN`/`OUT`/`INOUT` plus device
  bindings).
- Function address A(F) = comparison-link address; compare-tree dispatch.
- TDL with the 4-case store rule (d = NS-required error).
- Budget record `{steps, heap, stack, depth, fault}` on every region-entry marker, plus the
  out-of-band table.
- Effects: R → ISA `effect`; L → lifted device state; CC → `hostcall`.
- Shadow stack in a heap block.
- EH, sjlj and fibers by normaliser transforms.
- Polyvariant variants share data.
- Static register files for handles.
- Closed-unit mode with fallback.
- Read-up mixed majors.
- riscv64 platform profile.

Blockers:

- BLK-1 ISA-4: run-time widths and unbounded handle collections;
- BLK-2 ISA-1: device-computed budgets;
- BLK-3 ISA-3: parametrised `qinplace`;
- BLK-4 new ISA-12: `qreg.new`/`qreg.free` in R.

No rung is blocked.

## Next (for the orchestrator / maintainer)

- maintainer review of the outline against the demo ladder; answers to E1-E14
- file the reference-interpreter CLI request (part D3: run-cc, reverse, run-action,
  run-program) with bennett-isa-spec (not done by this job: read-only there)
- after review: write full 0.2 text section by section; checker per part D5
