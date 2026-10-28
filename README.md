# bennett-dialect-spec

The LLVM dialect contract of the Bennett ecosystem: the marker-function ABI (names, signatures, positive legality requirement), portable handle convention, outlining / budget / region well-formedness conventions, materialised-normalisation rules, the residual-poison validator, and the legality conformance corpus.

It also carries a reference semantics from marker programs to the ISA formal model, so a competing plugin can be conformance-tested at spec level.

Depends on: `bennett-isa-spec` (its reference semantics targets the ISA formal model).

Layout: `spec/` (normative text, not yet drafted), `corpus/` (legality corpus), `validator/` (Rust crate `bennett-dialect-validator`), `SPEC_VERSIONS.toml`.
