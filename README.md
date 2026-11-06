# bennett-dialect-spec

The LLVM dialect contract of the Bennett ecosystem: the marker-function ABI (names, signatures, positive legality requirement), portable handle convention, outlining / budget / region well-formedness conventions, materialised-normalisation rules, the residual-poison validator, and the legality conformance corpus.

It also carries a reference semantics from marker programs to the ISA formal model, so a competing plugin can be conformance-tested at spec level.

Depends on: `bennett-isa-spec` (its reference semantics targets the ISA formal model).

Layout:

- `spec/`: normative text. [`Bennett-Dialect-Spec.md`](spec/Bennett-Dialect-Spec.md) is the current draft (full version in its title), `bennett_markers.h` the marker ABI header, `errata-0.2.10.md` binding interpretations of accepted 0.2.10. See [`spec/README.md`](spec/README.md) for the change rules.
- `corpus/legality/`: legality corpus.
- The residual-poison validator is the Python `validate()` checker in `scripts/dialect_check_v02.py`. A linkable validator can be added when a consumer needs one.
- `scripts/`: the dialect checker (`dialect_check_v02.py`) and `pre-push`, which gates a clean worktree of the pushed commit (Python unit and slow execution suites plus the spec checker).
- `emission/`, `docs/`: emission notes and audit/brief records.
- `SPEC_VERSIONS.toml`: ISA version this repo is graded against (the gate validates inputs at the commits in `gate.toml`).

Current state and open consumer blockers: [HANDOFF.md](HANDOFF.md).
