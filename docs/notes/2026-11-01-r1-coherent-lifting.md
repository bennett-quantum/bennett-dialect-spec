# R1, coherent lifting under `ctrl`: status at dialect draft 0.3

Plan risk R1 reads "ISA 0.8 permits it; unspecified; draft 0.1 dodged it". That row is stale: §10 has specified TDL-1 to TDL-12 since
0.2. This note separates what is specified, what is executed and what is still owed.

## What 0.3 changes

- All TDL fixtures that ran on ISA 0.8 now run on ISA 0.9 objects, unchanged apart from version tokens and hashes (`tdl` 10/10, plus the
  `state` rows below). No rule needed a rewrite, so K31 (matched pairs), K37 to K41 (cleanup windows) and K65/K80/K81 (cleanup carriers)
  did not invalidate an event list.
- TDL-10's blocked case is gone. A coherent width with an unbounded value set pads to the full unsigned domain (maintainer D15). K1 does
  not help here: `qreg.new` takes classical operands only, so padding stays the construction.
- New witness `tdl-co-width` (§25.4): a width in superposition gives the entangled sum, executed. New example `tdl-co-width-top`.

## Evidence by rule

"Executed" means the reference interpreter ran an action or oracle on an ISA 0.9 object for a checker-built event list. Every event list
is hand-derived from the source in the spec or built by Python (P-3). None comes from a compiler.

| Rule | Executed witnesses | Label |
|---|---|---|
| TDL-1 interface vs body | `tdl-a`, `tdl-b` | executed on minis |
| TDL-2 coherence states | `co-store-release`, `generation-cancel`, `classical-event-application` | native seed plus executed |
| TDL-3 partition | `tdl-a`, `tdl-b`, `tdl-d`, `tdl-f`, `branch-views` | executed; the recogniser checks the partition text, not a compiler's |
| TDL-4 arena | `arena-logical-bounds` | executed |
| TDL-5 store rule | `tdl-overwrite` (reject), `inplace-param-quantum`, `co-loop-adj-overwritten` | executed |
| TDL-6 control and adjoint | `tdl-a`, `co-loop-adjoint` | executed |
| TDL-7, TDL-8 workspace, faults | `fault-output-lifetime`, `nested-cl-view` | executed |
| TDL-9 budget | `generation-budget` | executed |
| TDL-10 Co control | `co-loop-identity`, `co-loop-adjoint`, `tdl-angle` (reject), `tdl-co-width` | executed; the full-domain pad is specified, only a bound of 3 is executed |
| TDL-11 after the region | `co-observe-write-observe`, `partial-observe` | native coherence seed |
| TDL-12 effects | `tdl-effect` | executed on the console mini; the block-overlay and entropy compositions are not (bead `oxs`) |

This map is my reading of the fixtures. The checker's own P-1 coverage only resolves Appendix B's row, which claims "TDL-1 to TDL-12" for
the whole `tdl` family, so a green P-1 row does not establish per-rule coverage.

## What evidence does not allow

- **No producer exists.** `bennett-plugin` has one incidental mention of TDL per source file. Taint-driven outlining from real LLVM has never
  run, so nothing shows the partition is computable at SQLite scale. Bead `bp-xjc`.
- **The analysis is not Co-aware in the checker.** The recogniser's value set does not separate Cl from Co (`tdl-co-width-top`).
- **Scale is unmeasured.** Unrolled padded events (G-14) and shadow state per object have no cost data from a real closure.
- **R4 stays open.** Measurement-based uncomputation under control is unchanged, with unitary uncomputation as the fallback.

No rung's gate depends on R1 today: rungs 4, 7 and 8 use explicit oracles. It is required by the north star's "everything else is inferred"
(§0), so it stays in scope; only its order is the consumer's to choose.

## Recommended next step

Implement TDL-3 and TDL-5 for the rung-2 hashtable under `ctrl` in the plugin, and compare its event list against a hand-derived one. That is
the cheapest experiment that replaces hand-built lists with compiler output.
