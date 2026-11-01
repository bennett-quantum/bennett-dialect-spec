# Handoff: bennett-dialect-spec
## Checker follow-ups complete — 2026-11-01 12:24:39 UTC

Both gates are green: required headless root gate **2834/2834, exit 0**;
`bash scripts/pre-push` run once in its clean sibling worktree on `a0b7c47f8d5e`
**2834/2834, exit 0**; validator Cargo tests passed. Hook removed its worktree.
Receipts/logs: `scripts/.tmp/followups.json`, `followups.log`, `followups-pre-push.log`.

`0492c62` uses published `ISA-0.9.json` for exact clarification dependency membership.
Audited current `ISA-0.9.statements.json`: every ledger ISA dependency is a section/clause,
with no statement ID/text pins. Graph regeneration can add/change statements without a
whole-graph hash/count assertion; missing declared dependencies still fail.
`a0b7c47` builds immutable execution snapshots in release and includes profile in the
fingerprint/receipt. Debug add2 reproduced at **175.38 s**; release **24.89 s**, both
**65,536 exhaustive cases**, unchanged `6,0,9,1` budget and 180 s execution timeout.
The original snapshot includes O(1) checkpoints from ISA `7193103`; source hashes verified.
Both targeted snapshot regressions pass. No spec/sibling edits; ISA 0.8 grading unchanged.
Beads **b-dialect-spec-cbt** and **b-dialect-spec-088** closed; JSONL exported. Nothing pushed.
Full evidence and snapshot identities: top block of `scripts/dialect_check.PROGRESS.md`.

State (2026-10-31 ~12:50Z): draft 0.2.11 (compatible track, ISA 0.8) accepted by the sol and codex seats
(round 10; gate 2834/2834; spec SHA 67157631…82ba); muse advisory for this track. 0.2.10 remains the last
frozen receipt; 0.2.11 is the accepted draft. outline-0.3.md carries the maintainer's rulings D01-D22.
Next: (1) the 33 evidence closures of b-dialect-spec-oxs as a staged job (gate rows per item); (2) the 0.3
capability track (D15-D19) once ISA 0.9 is published (muse vote); (3) consumer re-pins: bennett-plugin is
being re-pinned to 0.2.10 now and moves to 0.2.11 after the oxs evidence lands.
Gate: `scripts/dialect_check_v02.py --json scripts/.tmp/<name>.json` headless (TMPDIR under scripts/.tmp).
Orchestrator state: bennett/HANDOFF.md.
