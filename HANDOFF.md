# Handoff: bennett-dialect-spec
## Snapshot repair — 2026-11-01 12:01:33 UTC

Self-contained sibling reference-interpreter/conformance snapshots implemented in `3679150`,
with target-directory traversal fix `f39634c` and HEAD-move test fixture update `eee2c6a`.
Both targeted snapshot regressions pass. All driver-* checks now pass. ISA 0.8 grading unchanged;
no spec or sibling source edits. Snapshot bead b-dialect-spec-piz closed.

Full headless root gate: **2798/2834 passed, exit 1** (`scripts/.tmp/snapshot-fix.json`).
Completed clean-worktree pre-push on `f39634c32ee3`: **2799/2834 passed, exit 1**;
validator Cargo tests passed. Root-only `step-check/add2` exceeded 180 seconds (b-dialect-spec-088,
open); pre-push passed it. Both gates fail 35 `coverage/0211/*` rows because the external
`bennett-conformance/clauses/ISA-0.9-draft.json` is missing (b-dialect-spec-cbt, open).
Exact failing checks, commands, red→green and logs are in the top block of
`scripts/dialect_check.PROGRESS.md`. No failures skipped or bounds changed. Nothing pushed.

State (2026-10-31 ~12:50Z): draft 0.2.11 (compatible track, ISA 0.8) accepted by the sol and codex seats
(round 10; gate 2834/2834; spec SHA 67157631…82ba); muse advisory for this track. 0.2.10 remains the last
frozen receipt; 0.2.11 is the accepted draft. outline-0.3.md carries the maintainer's rulings D01-D22.
Next: (1) the 33 evidence closures of b-dialect-spec-oxs as a staged job (gate rows per item); (2) the 0.3
capability track (D15-D19) once ISA 0.9 is published (muse vote); (3) consumer re-pins: bennett-plugin is
being re-pinned to 0.2.10 now and moves to 0.2.11 after the oxs evidence lands.
Gate: `scripts/dialect_check_v02.py --json scripts/.tmp/<name>.json` headless (TMPDIR under scripts/.tmp).
Orchestrator state: bennett/HANDOFF.md.
