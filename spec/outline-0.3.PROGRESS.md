# Outline0.3 — design progress

## Session log — 2026-10-31 — design sub-agent

Scope: proposed outline only; owned paths spec/outline-0.3.md, this progress file and .beads/. Accepted files, checker, corpus, headers, versions and worklog are untouched. No push. Parent/orchestrator owns the repository session worklog under CLAUDE.md rule0's sub-agent exception.

## Sources read and findings

- Repo CLAUDE.md (especially rules0/9/10/11/12), AGENTS.md, local Beads SKILL.md and bd prime.
- outline-0.2.md structure, mechanisms B1–B17, alternatives, scope/gate/closure maps and its final maintainer rulings; outline-0.2.PROGRESS.md.
- Accepted Bennett-Dialect-Spec.md0.2.10: section/rule structure, current normative statements and mapped dependency views; direct checks of marker legality, PT12, first-region-operand example, event semantics, drivers, blockers and Appendix A. Examples were reviewed selectively, not all executed.
- Bennett-Dialect-Spec-0.2.PROGRESS.md: initial drafting/departures, council repair history, current round8 freeze2767/2767,84 units/7 runtime tests, nonblocking PT12 follow-up. Accepted canonical-file SHA256 d4f3c1a88391cc147f8c8fa4f80f82852e3ebe6f880610fc16cd5151f33d7206.
- North star iteration7: thesis, §3 mechanisms/determinism/compilation model, §4 coherent/control/effect context, §6.1 boundaries and all eight §8 rungs. Grover over unmodified SQLite stays central.
- ISA0.9 draft title/publication status, complete §0 K/E-row table; provisions for register ledger, ownership, R frames, minting, parametrised qinplace, typed faults, history, calls, budgets, claims/domains and scheduling; corresponding ISA statement IDs.
- DLT-0.2.10.statements.md and ISA-0.9-draft.statements.md, as immutable ID vocabulary; clauses used directly where a whole mechanism is a dependency.
- 2026-10-29-dialect-0.1-narrowing-audit.md: 96 rows (57N/12M/27L),40 distinct narrowings, genuine0.8 gaps and construction-based alternatives.
- bd list --status open:57 open issues; bd show on epic8wf and each child. All40 children open. Also read bz6,cbe,0t9,0y2 and extra relevant ISA-wording bead gwf.

## Inventory and design results

45 item records:40 epic children +4 requested follow-ups +gwf. Groups: 35 compatible0.2.11, 8 capability0.3, 2 ISA-blocked external adoption records destined for0.3.22 numbered maintainer decisions; Maintainer rulings left empty. Every item has history/current DLT citations, ISA IDs, a dependency-tagged proposed sentence, alternatives, checker/gate effects and predecessor order.

Key corrections to stale assumptions:

- Most epic items already have the promised capability in accepted0.2.10; an open bead does not establish a surviving spec narrowing.
- 0t9 is already corrected to candidates=classical. Propose regression/closure evidence, not another accepted-file edit.
- BLK-3 was retired by the accepted CC expansion; native K4 is optional. K4's inverse-pair admission does not accept sampled evidence, so the sampled/assumed inverse path remains a CC expansion.
- K1 supports classical dynamic widths, not quantum-dependent classical allocation. Co widths still use unconditional sound-bound padding, with the full finite unsigned marker domain as a conservative capability-preserving construction.
- Pointer-width dialect tags are not automatically ISA64 ids: persistent tag/id bridging preserves narrow-pointer identity and prohibits truncation-based aliasing.
- ISA8 wording about a status returning to CC is superseded by0.9 terminal whole-run faults with no CC successor.
- Fixed-image subdomains remain evidence under ISA12.2. No implicit full-D proof or invented certificate fields.
- No real additional ISA0.9 semantic gap found; no ISA bead filed. K64/K65 publication gates and independent interpreter support remain external dependencies, not new proposals.

## Open maintainer questions

D01–D22 in the outline are the complete proposed ruling slate. Particular choices: release split and K64/K65/library gate (D01), native-vs-CC in-place evidence route (D14), full-domain Co-width fallback/shape realisation (D15), persistent tag/id bridge and run lifetime (D17), typed failed-run reversal (D18), certificate metadata/fixed-domain labels (D22). Ratification remains pending; no implementation readiness is claimed. No blocker is used to shrink a rung.

## Validation and tracking

Source-ID/coverage/diff verification and Beads receipt follow below. No draft/checker implementation or new conformance execution belongs to this session. Legacy freeze numbers above are inherited receipts only.

## Item-to-note map

- b-dialect-spec-8wf.1: spec/outline-0.3.md#i01, D08, 0.2.11.
- b-dialect-spec-8wf.2: spec/outline-0.3.md#i02, D18, 0.3.
- b-dialect-spec-8wf.3: spec/outline-0.3.md#i03, D14, 0.2.11.
- b-dialect-spec-8wf.4: spec/outline-0.3.md#i04, D10, 0.2.11.
- b-dialect-spec-8wf.5: spec/outline-0.3.md#i05, D02, 0.2.11.
- b-dialect-spec-8wf.6: spec/outline-0.3.md#i06, D03, 0.2.11.
- b-dialect-spec-8wf.7: spec/outline-0.3.md#i07, D04, 0.2.11.
- b-dialect-spec-8wf.8: spec/outline-0.3.md#i08, D09, 0.2.11.
- b-dialect-spec-8wf.9: spec/outline-0.3.md#i09, D11, 0.2.11.
- b-dialect-spec-8wf.10: spec/outline-0.3.md#i10, D11, 0.2.11.
- b-dialect-spec-8wf.11: spec/outline-0.3.md#i11, D07, 0.2.11.
- b-dialect-spec-8wf.12: spec/outline-0.3.md#i12, D12, 0.2.11.
- b-dialect-spec-8wf.13: spec/outline-0.3.md#i13, D05, 0.2.11.
- b-dialect-spec-8wf.14: spec/outline-0.3.md#i14, D14, 0.2.11.
- b-dialect-spec-8wf.15: spec/outline-0.3.md#i15, D04, 0.2.11.
- b-dialect-spec-8wf.16: spec/outline-0.3.md#i16, D13, 0.2.11.
- b-dialect-spec-8wf.17: spec/outline-0.3.md#i17, D03, 0.2.11.
- b-dialect-spec-8wf.18: spec/outline-0.3.md#i18, D10, 0.2.11.
- b-dialect-spec-8wf.19: spec/outline-0.3.md#i19, D15, 0.3.
- b-dialect-spec-8wf.20: spec/outline-0.3.md#i20, D16, 0.3.
- b-dialect-spec-8wf.21: spec/outline-0.3.md#i21, D09, 0.2.11.
- b-dialect-spec-8wf.22: spec/outline-0.3.md#i22, D06, 0.2.11.
- b-dialect-spec-8wf.23: spec/outline-0.3.md#i23, D06, 0.2.11.
- b-dialect-spec-8wf.24: spec/outline-0.3.md#i24, D07, 0.2.11.
- b-dialect-spec-8wf.25: spec/outline-0.3.md#i25, D17, 0.3.
- b-dialect-spec-8wf.26: spec/outline-0.3.md#i26, D07, 0.2.11.
- b-dialect-spec-8wf.27: spec/outline-0.3.md#i27, D07, 0.2.11.
- b-dialect-spec-8wf.28: spec/outline-0.3.md#i28, D07, 0.2.11.
- b-dialect-spec-8wf.29: spec/outline-0.3.md#i29, D17, 0.3.
- b-dialect-spec-8wf.30: spec/outline-0.3.md#i30, D06, 0.2.11.
- b-dialect-spec-8wf.31: spec/outline-0.3.md#i31, D08, 0.2.11.
- b-dialect-spec-8wf.32: spec/outline-0.3.md#i32, D18, 0.3.
- b-dialect-spec-8wf.33: spec/outline-0.3.md#i33, D02, 0.2.11.
- b-dialect-spec-8wf.34: spec/outline-0.3.md#i34, D13, 0.2.11.
- b-dialect-spec-8wf.35: spec/outline-0.3.md#i35, D06, 0.2.11.
- b-dialect-spec-8wf.36: spec/outline-0.3.md#i36, D12, 0.2.11.
- b-dialect-spec-8wf.37: spec/outline-0.3.md#i37, D12, 0.2.11.
- b-dialect-spec-8wf.38: spec/outline-0.3.md#i38, D18, 0.3.
- b-dialect-spec-8wf.39: spec/outline-0.3.md#i39, D12, 0.2.11.
- b-dialect-spec-8wf.40: spec/outline-0.3.md#i40, D19, 0.3.
- b-dialect-spec-bz6: spec/outline-0.3.md#i-bz6, D18, ISA-blocked.
- b-dialect-spec-cbe: spec/outline-0.3.md#i-cbe, D17, ISA-blocked.
- b-dialect-spec-0t9: spec/outline-0.3.md#i-0t9, D20, 0.2.11.
- b-dialect-spec-0y2: spec/outline-0.3.md#i-0y2, D21, 0.2.11.
- b-dialect-spec-gwf: spec/outline-0.3.md#i-gwf, D22, 0.2.11.

## Source snapshots and review corrections

Dialect repo HEAD at reading: da874dfe0cc6a1639f5eafb25930d90c4647dd29.
ISA repo HEAD at reading: 9b8e01eaaabf471d9df99c5434bde8f5752dbcc4.
The supplied ISA statement view has older front-matter status (“not yet graded”); current ISA source supplies the two-seat acceptance/publication status. Semantic dependency IDs use the supplied immutable view, not a regenerated one. K64/K65 clauses are ISA-11-P10/P11, not the selection/validation clauses P6/P7. This was corrected during outline validation.
Native K4's optional lowering is explicitly confined to 0.3, separate from the compatible confirmation that the CC construction remains. I19 specifies the full finite representable shape-dispatch construction when AV widens to top; no JIT, new parametric signature, hidden T-IFACE narrowing or unsupported Co allocation primitive is assumed.

## Final validation receipt — 2026-10-31

- 45 unique item anchors, exact coverage of40/40 epic children plus bz6/cbe/0t9/0y2/gwf;22 decision questions; each item names its decision and dependency order.
- 48 quoted proposed normative sentence blocks plus8 process/gate sentences:56 dependency markers,307 dependency references,188 distinct IDs. All dependency IDs resolve in the supplied DLT/ISA clause graphs and statement views; every MUST/MAY/SHOULD/SHALL line ends with its dependency tag.
- Maintainer rulings section empty; no acceptance/ratification invented.
- 45 item comments and1 epic comment written by bd comment, each pointing to the outline (item comments include section anchor/group/decision); all46 records remain open. Verified all46 notes in the exported .beads/issues.jsonl.
- bd export -o .beads/issues.jsonl completed. Export diff is46 existing issue records updated with comments; no new ISA issues, no closures.
- git diff --check passed; accepted canonical spec SHA256 still d4f3c1a88391cc147f8c8fa4f80f82852e3ebe6f880610fc16cd5151f33d7206. Only the two new outline files and .beads/issues.jsonl are changed.
- No implementation changes, full preflight, native/ISA0.9 execution or new conformance tests claimed. Existing2767/2767 is the baseline's inherited receipt, not a result from this outline session.
- Ready for the explicit-path commit and maintainer handoff; no push or Dolt remote sync.
