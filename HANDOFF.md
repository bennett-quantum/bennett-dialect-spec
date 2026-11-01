# Handoff: bennett-dialect-spec

Updated: 2026-11-01 15:59:39 UTC (real `date -u`).

**Running:** none. Draft **0.2.12**, eight consumer-chosen passes complete, awaiting council;
ISA grading target remains **0.8**. Final pass commit carries this handoff. Spec SHA-256:
`71e929f4d9af45ac539f16dec1c6c9d7e08a9500fa99d320ac2afafdc4b48c0b`.
Superseded accepted 0.2.11 at eaad067 has exact-byte SHA `05101a18e04098cfca5fdfb52edc9d9027723455adf2569da2fa49ef7a47c7c1`;
its separate freeze SHA 67157631…82ba is also retained in the header. Accepted 0.2.10
@023f5a7 is unchanged; eight binding interpretations/new-rule distinctions are in
`spec/errata-0.2.10.md`. SPEC_VERSIONS.toml unchanged. Nothing pushed.

**Next:** orchestrator's one-reviewer council round. Review brief and all eight dispositions:
`docs/briefs/2026-11-01-dialect-0212-consumer-gaps.md`. Required headless gates passed,
in order mkb/jjr/lbq/0na/dfd/1av/z7u/21a: 2840/2840, 2846/2846, 2854/2854, 2868/2868, 2873/2873, 2880/2880, 2888/2888, 2893/2893;
zero failed/blocked rows. Receipts `scripts/.tmp/0212-<bead>.json`; validator Cargo tests
1/1 after every pass; new checker units 4/4. New checks distinguish wording/ABI evidence
from missing runtime numerical conformance. All 497 accepted tagged blocks retained.

**Waiting:** mkb closed as a contract clarification; bp-z9k tracks plugin implementation.
Seven dialect beads remain open as implementation blockers: jjr, lbq, 0na, dfd, 1av, z7u, 21a.
New follow-ups: runtimes brt-agy (alignment), brt-4w7 (process context), brt-2qs (native detection);
arith bennett-arith-4yg (PPC), bennett-arith-wvh (libm), bennett-arith-38c.1 (instances),
bennett-arith-chn.1 (signaling); plugin bp-o0h (arbitrary formats), bp-q6e (comparisons);
driver bennett-driver-i0v (native comparison), bennett-driver-q4d (instances).
All twelve carry dialect-0.2.12/topic labels. Only exported .beads/issues.jsonl was committed
in siblings; no sibling code edits. Existing oxs evidence work and 0.3/ISA0.9 capability
track remain separate; no automatic closure or full runtime/DF claim follows from these gates.
