# Handoff: bennett-dialect-spec

Updated: 2026-11-01 17:15:49 UTC (real `date -u`).

**Running:** none. Draft **0.2.12** accepted by the **sol seat in round 11**
(2026-11-01; 0 blocking; acceptance gate 2893/2893). All four S1 suggestions
completed as specification/checker housekeeping. Final gate **2902/2902**;
zero failed/blocked. ISA grading target remains **0.8**; SPEC_VERSIONS.toml
unchanged. No push by this implementer.

Spec SHA-256: `cfcce70e84ead8a05924c0921f13fc9cb477fdd71f5448c7f6f357ea91349e83`.
Accepted 0.2.11 @eaad067 and 0.2.10 @023f5a7 remain historical pins; this
housekeeping does not change the nonretroactive distinctions in errata-0.2.10.md.

**Completed:** concrete runtime-owned fenv layout; independent numerical host
oracle (70 observations per LLVM 18/23 build, including exact PPC pair sum,
qNaN/sNaN positions, constant predicates, sticky flags, unchanged input bits and
sin(+0)); native allocation fixture plus independent ISA execution/reversal and
actual driver layout-emitter checks; exact C8 replacement in §18.7.
Nearest-away sin(+0) uses the exact-zero identity (no tie); these samples do not
establish production carrier flags, PPC rounding or full-domain libm accuracy.
Allocation probes cover requests 3/13/16, bump 4128, three records, all zero bytes,
requested live sizes, padding/extent/overflow failures and reversal; a diagnostic
zero-size request confirms the final bump. No new allocation primitive.

**Verification:** full headless gates after items 1–5: 2893, 2894, 2897, 2900,
2902, all passed. Final receipt `scripts/.tmp/0212-hk.json`; item 2–5 copies
`scripts/.tmp/0212-hk-N.json`. Validator cargo test 1/1 after every item (0 doc-tests).
Snapshot integration regression failed before repair, then passed; semantic
quiet/signaling and missing-padding mutations were rejected. All 513 tagged
blocks at cc04ecb remain byte-identical. `git diff --check` clean.

**Checker repair:** the first gate exposed an omitted interpreter build input,
`spec/ref-0.9.json`. Immutable source capture now copies/fingerprints it and
rebuilds when it changes; this is build support, not ISA-0.9 adoption.
New dialect bead **b-dialect-spec-pc2** is closed after the green repair gate.

**Waiting:** seven consumer implementation blockers **jjr, lbq, 0na, dfd, 1av,
z7u, 21a** remain open. Full-domain accuracy and exact-flag obligations remain
open regardless of the samples. New runtime child **brt-zct.1** tracks the exact
fenv definition/layout under the existing DR epic, labelled dialect-0.2.12 and
fenv-layout; arith already declares the object. Earlier twelve consumer follow-ups
remain as recorded in the consumer-gap brief. No sibling source was edited;
only the runtime bead export was committed there, as **ec52032**.

**Commits:** item 1 **8e28645**, item 2 **c8647d6**, item 3 **f1b6ad3**,
item 4 **32b56fc**; item 5 carries this handoff. Records are confined to the
PROGRESS top block and this handoff. Next work is consumer implementation and
its independent production conformance evidence, not automatic bead closure.
