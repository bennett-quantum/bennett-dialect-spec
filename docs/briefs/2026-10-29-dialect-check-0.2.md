# Job: the dialect 0.2 pre-flight checker (`scripts/dialect_check.py`)

Working directory: the git repository `bennett-dialect-spec`. `spec/Bennett-Dialect-Spec.md` is now draft 0.2
(7,341 lines; the council is grading it concurrently; **never edit `spec/Bennett-Dialect-Spec.md`,
`spec/bennett_markers.h`, `spec/README.md`, `spec/outline-0.2.md` or `SPEC_VERSIONS.toml`**). The existing
`scripts/dialect_check.py` is the 0.1 checker; it crashes on the 0.2 marker set (`KeyError:
'effect_console_write'`). Your job: make `scripts/dialect_check.py` the complete pre-flight for 0.2, so that
`python3 scripts/dialect_check.py` exits 0 only when every tagged example in the spec checks, and reports every
failure with the example id, the rule and the expected versus actual values.

Read first, in full: `CLAUDE.md` (rules 1, 8, 10, 11), `HANDOFF.md`, spec §1.5 "Notation and checked examples"
and §1.6, Appendix B (example index), `spec/Bennett-Dialect-Spec-0.2.PROGRESS.md` (the table of example
families, what each needs and what the previous agent could verify), `spec/outline-0.2.md` part D (the
pre-flight plan the spec was tagged against), the current `scripts/dialect_check.py` (reuse its parsing,
toolchain handling and structure), `corpus/legality/toolchains.toml` and the harness under `corpus/`,
`../bennett-isa-spec/reference-interpreter/README.md` (the interpreter CLI: `check`, `hash`, `run-oracle`,
`step-check` exist; `run-cc`, `reverse`, `run-action`, `run-program` are requested in
`../bennett-isa-spec` bead b-isa-spec-xam and will appear while you work: poll its README), and beads
b-dialect-spec-gvr, -d4k, -rq0 in this repo (`bd show`).

## What the checker must do (every family of §1.5 / Appendix B)

1. Every `llvm` block parses and verifies on LLVM 18, 20 and 23 (headless, rule 11), with the implied marker
   declarations of §1.5 and the 0.2 header.
2. Every `example=` block: the 0.2 recogniser (§3–§7, §9: markers, handles, regions, candidate sets, budgets)
   gives exactly the stated verdict (`accept`, `reject:<rule>`, `blocked:<id>`) and the stated candidate sets.
   Write the recogniser as a faithful executable reading of the spec text, rule by rule, citing the rule id
   in every rejection. Where the spec is ambiguous, do not guess silently: record the question in
   `scripts/CHECKER-QUESTIONS.md` (question, section, the reading you took) and `bd create` it.
3. Every `normalise-in` / `normalise-out` pair: the 0.2 normaliser (§12) maps one onto the other and the
   output passes the residual-poison validator (§12.5). `native=` examples: build with clang (18 and 23)
   and compare the stated native result. Seeds (`spec/seeds/`, b-dialect-spec-d4k): create what the examples
   reference, derived from the spec text; list each seed and the example that needs it.
4. Every `lift=` / `reference-body=` / `hash=` / `fb=` / `inplace=` example: the lifting map (§16) gives
   exactly the stated ISA text; `bennett-isa-ref check`/`hash` gives the stated hash; `run-oracle` and
   `step-check` give the stated results. Build the interpreter from `../bennett-isa-spec/reference-interpreter`
   into a scratch copy under `scripts/.isa-ref/` (ignored by git) so the concurrent interpreter job cannot
   change it under you; record the commit you built.
5. `tdl-*`, `sem2-*` (`run-action`), effect/sjlj/fiber/exit examples (`run-cc`, `reverse`), and
   `run-program` families: implement the checks against the documented CLI contract now; while a command
   does not exist, the checker must **fail loudly** for that family with the exact command it needs and the
   bead id, never skip silently. Re-run when the commands land.
6. `semantics=` / `events=` / `state=`: the program equals its corpus file and, built with the trace runtime,
   yields the stated events and state. The trace runtime is still ABI v0 (b-dialect-spec-566): updating it
   to ABI 0.2 (`corpus/` harness, trace runtime) is in your scope if nothing else blocks; otherwise fail
   loudly with the bead id.
7. The marker list (§3) agrees with the C header, with the spec's `markers-c` block, and with clang-18's
   lowering of it; the asm data files `spec/asm/<arch>.toml` (b-dialect-spec-rq0) exist and agree with §15.
8. Every section cross-reference resolves (this spec, ISA 0.8, the north star). Every rule id in the spec
   has at least one example (b-dialect-spec-gvr lists the ones that lack one): report the list; do not
   invent examples in the spec (the editor adds them).
9. A `--family F` option to run one family, `--list` to print every example with its family and status, and
   a final table: family, examples, passed, failed, blocked-on (command/bead).

## Constraints and process

- Owned paths: `scripts/`, `spec/seeds/`, `spec/asm/`, `corpus/` (harness and trace runtime only; never
  `corpus/legality/cases/spec-*`), `bd` notes and issues. Nothing else.
- Python 3 standard library only, like the 0.1 checker. Red-green where a check is non-trivial: write the
  failing case (a deliberately wrong expectation) first, see it fail, then the real check.
- Headless (rule 11): `DISPLAY`, `WAYLAND_DISPLAY`, `DBUS_SESSION_BUS_ADDRESS`, `BROWSER` unset; `TMPDIR`
  inside the repo (the job runner sets it); never any LLVM `view-*` pass.
- The spec is under council review: if the checker finds the spec wrong (a stated result that does not
  reproduce), that is a finding, not something to paper over: `bd create` it with the example id, expected,
  actual and the command, label `spec-0.2-finding`, and let the check fail.
- Commit owned paths regularly (the runner does it every 20 min too). Never push.
- Progress file `scripts/dialect_check.PROGRESS.md`: family table with status, questions, findings. A fresh
  session resumes from it.

Done means: `python3 scripts/dialect_check.py` runs every family; every family that the available tools can
execute passes or has filed findings; every family that cannot yet execute fails loudly naming its command
and bead; the final table is printed; `--list` and `--family` work.
