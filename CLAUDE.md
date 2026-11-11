# bennett-dialect-spec

## What this repo is

The LLVM dialect contract: marker-function ABI, portable handles, outlining/budget/region conventions, materialised-normalisation rules, residual-poison validator and legality corpus. Depends on bennett-isa-spec for its reference semantics.

## Where the spec is

Normative text: `spec/Bennett-Dialect-Spec.md` (draft 0.1, under audit for narrowings: `docs/audit/`; 0.2 in preparation) with its pre-flight `scripts/dialect_check.py`. Source material: `../bennett/docs/Bennett-NorthStar.md` §3; spike evidence: `docs/spikes/`. Versions in `SPEC_VERSIONS.toml`.

## Rules

The one rulebook is bennett/docs/process/COMMON.md; it binds here. Gate: `scripts/pre-push`. Tasks: `bd` (`bd prime` lists its commands).
