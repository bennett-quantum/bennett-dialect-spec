# spec/

`Bennett-Dialect-Spec.md` is the normative text: draft 0.1 (2026-10-29),
the founding draft of the dialect contract, **not yet graded** by the
three-model council. It targets ISA 0.8 (`../bennett-isa-spec/spec/`,
settled). `bennett_markers.h` is the normative C/C++ header of the marker
ABI (section 3.3). Council records and the runner live in the `bennett`
meta repo (`docs/council/`, `tools/council.py`); the rubric is
`docs/council/rubric-isa.md`.

Rules for changing it:

- Every semantic change bumps the full version string (header and
  section 13); drafts are not compatible with each other. The
  reference-body hashes of section 9 depend on the ISA version string
  and on the lifting map, so they change with either.
- Run `python3 scripts/dialect_check.py` before anyone grades a draft; it
  must exit 0. It executes every tagged example (section 1.5): LLVM
  18/20/23 verification, recogniser verdicts and candidate sets,
  normalisation pairs, reference bodies, hashes, F_B results, in-place
  verdicts, trace-checked event lists and states, marker-list agreement
  with `bennett_markers.h`, and every section cross-reference.
- Add every new example or stated result as a tagged block, so the
  checker executes it; an untagged `llvm` or `isa` block is an error.
  A `semantics=` example must be byte-equal to its `corpus/legality/cases/
  spec-*.ll` file; run `python3 corpus/legality/harness/run.py baseline
  --majors 18,20,23 --cases 'cases/spec-*'` after changing one.
- Surgical edits only; a rewrite has introduced a mechanical error every
  time it was tried (ISA rounds 1-8).
- Section 14 lists decisions deferred to implementation with their
  defaults; an implementer who must choose something not covered there
  files an issue and the default goes into section 14 first. Anything the
  ISA would need goes to section 15 as an open item, never into a
  dialect-side redefinition of the ISA.
- Revisions go back through the council.
