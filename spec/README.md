# spec/

`Bennett-Dialect-Spec.md` is the normative text: draft 0.2 (2026-10-29), written from the ratified
outline `outline-0.2.md` (its maintainer rulings at the end), **not yet graded** by the
three-model council. It replaces draft 0.1, which the narrowing audit
(`../docs/audit/2026-10-29-dialect-0.1-narrowing-audit.md`) rejected; git keeps 0.1. It targets
ISA 0.8 (`../bennett-isa-spec/spec/`, settled) and is graded against it. `bennett_markers.h` is the
normative C/C++ header of the marker ABI (section 3.3). `Bennett-Dialect-Spec-0.2.PROGRESS.md` is
the writing job's log. Council records and the runner live in the `bennett` meta repo
(`docs/council/`, `tools/council.py`); the rubric is `docs/council/rubric-isa.md`, under which any
narrowing of north-star scope is S0.

Rules for changing it:

- **No narrowing** (CLAUDE.md rule 10). A compile-time rejection needs a row in section 22.1 citing
  the north-star clause or maintainer decision that requires it. A deferral (section 24) postpones
  mechanics only and states the capability it keeps. A capability ISA 0.8 cannot express is a
  blocker (section 25.1) with the exact ISA change and a `blocked:` verdict, never a rejection.
- Every semantic change bumps the full version string (header and section 23); drafts are not
  compatible with each other. The reference objects and hashes of section 16 depend on the ISA
  version string, the lifting map and the layout, so they change with any of them.
- **Checked examples** (section 1.5, process rules P-1 to P-3):
  - P-1: every rule id has an `accept` example, every rejection a `reject` example, every blocker
    a `blocked` example; Appendix B is the index, and a rule without one fails the check.
  - P-2: an example the checker cannot yet execute fails (`checker-unimplemented: <capability>`);
    no example is removed or weakened to make the checker pass; the freeze gate is all green.
  - P-3: executed results come from independent executors (LLVM tools, native binaries, the Rust
    ISA reference interpreter `bennett-isa-ref`); Python computes expected artefacts only.
- Run `python3 scripts/dialect_check.py` before anyone grades a draft; it must exit 0. (For 0.2 the
  checker is being extended against the Rust interpreter in a separate job; until then the 0.2
  examples were executed by the writing job as its progress file records.)
- Add every new example or stated result as a tagged block, so the checker executes it; an
  untagged `llvm` or `isa` block is an error. A `semantics=` example must be byte-equal to its
  `corpus/legality/cases/spec-*.ll` file; run `python3 corpus/legality/harness/run.py baseline
  --majors 18,20,23 --cases 'cases/spec-*'` (headless, CLAUDE.md rule 11) after changing one.
- Write derivations out before stating numbers; every stated example result must be computed.
- Surgical edits only; a rewrite has introduced a mechanical error every time it was tried (ISA
  rounds 1-8).
- Revisions go back through the council.
