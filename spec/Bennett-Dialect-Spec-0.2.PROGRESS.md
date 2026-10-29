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
- §9 budgets (next commit)

## Decisions taken while writing (not in the outline)

- Primitives `__bennett_nz_alloc` / `__bennett_nz_free` (ISA alloc/free, lift.alloc/lift.free)
  added next to `__bennett_nz_fault`: the runtimes allocator needs a way to reach `lift.alloc`.
- Reserved-name rules apply to *producer inputs* (driver checks before link); runtimes/arith
  bitcode may use `__bennett_rt_/dev_/sf_/nz_` names.
- §5: abstract value = (atom set, TOP flag); TOP never stands for a ROOT atom; K = 4096 cap is
  normative (decides verdicts). Residue classes carry an extent [lo, hi) from array types (B-27).
- §5: `inttoptr` constants are TOP for function pointers (A(F) is fixed only after the
  comparison link, which happens after S7); a Julia `@cfunction` constant traps unless it equals
  an A(F) at run time; Bennett.jl's `ptr @f` route keeps the capability.
- §6.5: two realisations: *direct* (handle never stored in memory: CC qreg SSA values, no bound,
  recursion and loops fine) and *static register file* (stored handles; reference instance
  bound: self-disjoint -> 1, else E(s) via constant max trip counts; infinite -> BLK-1).
- §6.6: device-entry pointer parameters get a candidate ROOT(E,i) atom that survives only if it
  reaches a marker handle operand (decides QREG binding).
- §7.5(b): R-tier allocation hoisting uses the reference instance bound; BLK-4 only when it is
  infinite (e.g. allocation per activation of an unbounded recursion).
- §8.1: descriptor layout = LLVM struct {H,[n x Bind],[m x DevBind]} under the datalayout;
  ARG values: bits 0-63 in `value`, 64-127 in `size`.
- §8.5: snapshot byte format fixed; replay by a runtimes function; the snapshot register is
  released by `measure` (it is an unentangled basis state) -- the outline had no cleanup for it.
- §8.7: in-place verification computes B_min; F_B is monotone in the budget, so run-time
  budgets are checked against B_min at the marker (`T-BUDGET`).
- §9.2: budget table JSON schema and precedence (identity > region key > symbol glob > default).

## Departures from the outline

(each also recorded in the spec's Appendix A)

1. **§8.6 wide outputs: copy-out construction (2k−1 calls) instead of the W_c construction
   (k+2 calls).** The outline cleans each slice's fault bundle f_j with `qxor` from a copy c of
   the code computed by a different variant W_c. That cleanup is not "reverse" or "recompute"
   of f_j's own computing sequence (ISA §6.2, §6.4), so the action would be ill-formed under the
   ISA's static discipline. The copy-out pair (compute into fresh t_j, f_j; qxor t_j into the
   target; identical call again) cleans t_j and f_j by `reverse`. Same capability, valid ISA.

## Examples and checker requirements

(the full index is the spec's Appendix B)

## Open questions

(none yet)
