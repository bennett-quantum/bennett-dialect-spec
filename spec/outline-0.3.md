# Bennett LLVM Dialect — next draft — OUTLINE 0.3

**Date:** 2026-10-31. **Status:** proposed outline for maintainer rulings; no draft text and no ratification implied. Prepared as the design sub-agent. Accepted baseline: dialect **0.2.10**, ISA **0.8**. Candidate target: ISA **0.9 draft**, accepted by sol/codex seats, muse held, K64/K65 awaiting maintainer ratification. This outline follows the structure and ruling convention of `outline-0.2.md`, while preserving the accepted text's subsequent council repairs (notably Appendix A).

**Scope:** all 40 open children of `b-dialect-spec-8wf`, the three requested dependency beads bz6/cbe/0t9, nonblocking PT12 bead 0y2, and the additionally relevant open ISA-wording bead gwf: **45 item records, 22 decisions**. The epic itself remains the scope ledger. Other open corpus/tooling siblings are not implicitly completed by this design.

**Reading key.** DLT IDs name `../bennett-conformance/clauses/DLT-0.2.10.statements.md`; ISA IDs name `ISA-0.9-draft.statements.md` there. An unsuffixed section or paragraph is a clause dependency; `.S<n>` selects a statement. K/E numbers are ISA §0 change-row mnemonics, not dependency IDs. NS is `../bennett/docs/Bennett-NorthStar.md` iteration7, especially §3, §6.1 and the entire §8 ladder. Audit row IDs retain their original 0.1 meanings. “0.1 capability” below means the north-star capability the 0.1 narrowing removed or omitted, not a claim that restrictive 0.1 already implemented it. Every item distinguishes that history from the actual 0.2.10 state.

## Part A. Draft structure and release boundaries

Proposed section plan: retain §§1–25 and Appendices B/C; add an opening change ledger and dependency declarations; update §§3.4,5,6,8.4,9.5,11.5,17.5–17.6,19.9,23,25 for ISA 0.9; preserve the accepted normalisation/map unless an item explicitly changes it. Appendix A becomes a provenance ledger of departures from ratified outlines, retaining all accepted council repairs. There is no proposed change to marker ABI signatures or descriptor version2 in this outline.

Proposed editorial/process sentences (for the eventual draft, subject to D01):

- The next draft MUST preserve every north-star capability and every existing non-narrowing construction, with deferral limited to mechanics and any real missing ISA operation named precisely as a blocker. [deps: DLT-front-P3, DLT-1.3, DLT-1.6, DLT-24, DLT-25.1]
- Every new or changed normative sentence MUST end with a dependency declaration naming the DLT or ISA statement or clause IDs on which it relies. [deps: DLT-1.5, DLT-23]
- The 0.2.11 compatible track MUST retain the ISA 0.8 target, existing marker signatures, canonical map and externally visible reference behaviour while clarifying inherited rules and supplying their missing closure evidence. [deps: DLT-front-P2, DLT-3.2, DLT-16, DLT-23]
- The 0.3 track MUST declare ISA 0.9 and its complete sub-version tuple, regenerate affected objects, canonical hashes, plugin identity, module flag, schedules and certificates, and preserve the accepted 0.2.10 ISA 0.8 artefacts as historical versioned vectors. [deps: DLT-16.2-P2, DLT-19.9, DLT-23, ISA-front-P2, ISA-9.1, ISA-9.2, ISA-12.3]

The dependency-tag process rule additionally comes directly from repo CLAUDE.md rule12; its dependency marker above names the existing notation/versioning context, not an assertion that 0.2.10 already had rule12. Same principle for the no-narrowing standing rule (repo rule10, NS thesis).

Three groups below describe landing mechanics, never reduced scope:

- **0.2.11:** compatible/editorial confirmations and analysis clarifications already required by 0.2.10; these are mostly open-bead closure/evidence work, not newly invented capabilities.
- **0.3:** actual ISA 0.9 adoption, dynamic-register/token/R lowering and removal of obsolete dependency verdicts.
- **ISA-blocked:** bz6/cbe remain external adoption/implementation blockers in the accepted baseline, destined for 0.3 once the publication and execution gates pass; 0.9 contains their missing sentences already. This is not a claim of an additional ISA design gap.

## Part B. Item index

In the table, `.N` abbreviates `b-dialect-spec-8wf.N`; other suffixes abbreviate `b-dialect-spec-<suffix>`. “Existing construction” means no new ISA capability request. Every record below has history, precise baseline citations, ISA provision, proposed sentences, rejected alternatives, checker consequences and predecessor order.

| Bead | Group | ISA provision / dependency | Decision | Record |
|---|---|---|---|---|
| .1 | 0.2.11 | existing construction; cited below | D08 | [I01](#i01) |
| .2 | 0.3 | K5/K6 | D18 | [I02](#i02) |
| .3 | 0.2.11 | K4 optional; CC expansion retained | D14 | [I03](#i03) |
| .4 | 0.2.11 | existing construction; cited below | D10 | [I04](#i04) |
| .5 | 0.2.11 | existing construction; cited below | D02 | [I05](#i05) |
| .6 | 0.2.11 | existing construction; cited below | D03 | [I06](#i06) |
| .7 | 0.2.11 | existing construction; cited below | D04 | [I07](#i07) |
| .8 | 0.2.11 | existing construction; cited below | D09 | [I08](#i08) |
| .9 | 0.2.11 | existing construction; cited below | D11 | [I09](#i09) |
| .10 | 0.2.11 | existing construction; cited below | D11 | [I10](#i10) |
| .11 | 0.2.11 | existing construction; cited below | D07 | [I11](#i11) |
| .12 | 0.2.11 | existing construction; cited below | D12 | [I12](#i12) |
| .13 | 0.2.11 | §7.3; E13/K10; R faults K5/K6 | D05 | [I13](#i13) |
| .14 | 0.2.11 | K4/K13; sampled CC path retained | D14 | [I14](#i14) |
| .15 | 0.2.11 | existing construction; cited below | D04 | [I15](#i15) |
| .16 | 0.2.11 | existing construction; cited below | D13 | [I16](#i16) |
| .17 | 0.2.11 | existing construction; cited below | D03 | [I17](#i17) |
| .18 | 0.2.11 | existing construction; cited below | D10 | [I18](#i18) |
| .19 | 0.3 | K1; Co padding construction | D15 | [I19](#i19) |
| .20 | 0.3 | K3 | D16 | [I20](#i20) |
| .21 | 0.2.11 | existing construction; cited below | D09 | [I21](#i21) |
| .22 | 0.2.11 | existing construction; cited below | D06 | [I22](#i22) |
| .23 | 0.2.11 | existing construction; cited below | D06 | [I23](#i23) |
| .24 | 0.2.11 | existing construction; cited below | D07 | [I24](#i24) |
| .25 | 0.3 | K1/K2 ledger | D17 | [I25](#i25) |
| .26 | 0.2.11 | existing construction; cited below | D07 | [I26](#i26) |
| .27 | 0.2.11 | existing construction; cited below | D07 | [I27](#i27) |
| .28 | 0.2.11 | existing construction; cited below | D07 | [I28](#i28) |
| .29 | 0.3 | K1 ownership | D17 | [I29](#i29) |
| .30 | 0.2.11 | existing construction; cited below | D06 | [I30](#i30) |
| .31 | 0.2.11 | existing construction; cited below | D08 | [I31](#i31) |
| .32 | 0.3 | K2/K6 | D18 | [I32](#i32) |
| .33 | 0.2.11 | existing construction; cited below | D02 | [I33](#i33) |
| .34 | 0.2.11 | existing construction; cited below | D13 | [I34](#i34) |
| .35 | 0.2.11 | existing construction; cited below | D06 | [I35](#i35) |
| .36 | 0.2.11 | existing construction; cited below | D12 | [I36](#i36) |
| .37 | 0.2.11 | existing construction; cited below | D12 | [I37](#i37) |
| .38 | 0.3 | K5/K6 | D18 | [I38](#i38) |
| .39 | 0.2.11 | existing construction; cited below | D12 | [I39](#i39) |
| .40 | 0.3 | K2 for R; replay retained | D19 | [I40](#i40) |
| bz6 | ISA-blocked | K5/K6; publication + execution | D18 | [I-bz6](#i-bz6) |
| cbe | ISA-blocked | K1/K2; publication + execution | D17 | [I-cbe](#i-cbe) |
| 0t9 | 0.2.11 | none (already corrected) | D20 | [I-0t9](#i-0t9) |
| 0y2 | 0.2.11 | none (N9 transfer) | D21 | [I-0y2](#i-0y2) |
| gwf | 0.2.11 | E11–13/E16.8/K5–6/K13; §12.2 | D22 | [I-gwf](#i-gwf) |

## Part C — 0.2.11 item records

<a id="i01"></a>
### I01 — Taint-driven lifting

**Bead:** `b-dialect-spec-8wf.1`. **Group:** 0.2.11. **Decision:** D08. **Audit:** 1.4-d, D17, B-31, B-50, O-05.

**0.1 capability/history:** 0.1 ran the classical part of ctrl/adj/compute once without controlling its escaping stores; the promised capability is inferred coherent execution of ordinary code.

**0.2.10 delta:** Already restored by DLT-7.1-P7 and DLT-10-P2 through DLT-10-P45: Cl/M/Co state, classical twins, coherent slices, store events and clean control workspace; no surviving generation-only restriction.

**ISA 0.9 provision:** ISA-4.7-P1, ISA-5.2, ISA-5.3 and ISA-6 provide controlled oracle calls, total XOR outcomes and cleanup; no extra ISA sentence is needed.

**Proposed normative resolution:**

> An action body containing classical code MUST retain the Cl/M/Co partition, classical twins, predicated outliving stores and clean-workspace obligations of TDL-1 through TDL-12. [deps: DLT-10, DLT-18.2, ISA-4.7, ISA-5.2, ISA-6]

**Rejected alternatives:** Generation-only execution changes the controlled store result; retaining incidental garbage as undeclared outputs violates the accepted cleanup contract.

**Conformance consequence:** DT/DS: retain tdl-a through tdl-d, co-loop-identity, co-loop-adj-overwritten, co-observe-write-observe and deferred-channel cases; add no subset rejection. Rungs 4/7/8 retain explicit-oracle paths.

**Dependency order:** I07, I17, I22, I33; I31 is the nested reversible-call case.

**Maintainer choice:** D08 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i03"></a>
### I03 — Parametrised inplace

**Bead:** `b-dialect-spec-8wf.3`. **Group:** 0.2.11. **Decision:** D14. **Audit:** 1.4-f / ISA-3.

**0.1 capability/history:** 0.1 inplace accepted only x, omitting preserved quantum inputs, memory and classical parameters.

**0.2.10 delta:** DLT-8.7-P3, DLT-8.7-P4, DLT-8.7-P5 already support all bindings by specialisation, library actions and the CC oracle/swap/inverse expansion; BLK-3 is retired in DLT-25.1-P1.

**ISA 0.9 provision:** K4: ISA-4.5-P5 now provides native qinplace with ins/mem/args and an inverse-pair entry; K62/63 pin adjoints and call-edge identities. This is an optional lowering, not a newly missing capability.

**Proposed normative resolution:**

> Parametrised in-place calls MUST preserve the existing CC expansion for every admitted pair. [deps: DLT-8.7-P5, DLT-8.7-P6, ISA-3.3-P9, ISA-4.7]

Optional 0.3 lowering, after D01:

> Native parametrised qinplace MAY replace that expansion only when its covering ISA inverse-pair entry is verified. [deps: DLT-8.7-P5, DLT-8.7-P6, ISA-4.5-P5, ISA-12.1-P1, ISA-12.3]

**Rejected alternatives:** Reinstating BLK-3 is false; replacing every pair with native qinplace would exclude the sampled path described in I14.

**Conformance consequence:** DO/DM/DS: compare controlled CC expansion and native K4 for exhaustive/library pairs, both orientations, changed preserved input and too-small budget; ISA F checks signature/certificate admission.

**Dependency order:** I06, I17, I14; D01 gates native 0.9 objects and scheduled expansions.

**Maintainer choice:** D14 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i04"></a>
### I04 — Allocation classes

**Bead:** `b-dialect-spec-8wf.4`. **Group:** 0.2.11. **Decision:** D10. **Audit:** D1, B-05.

**0.1 capability/history:** 0.1 rejected cls != 0 despite classed allocations in the north star.

**0.2.10 delta:** DLT-3.4-P18 already defines the link-order class-name table; DLT-3.4-P22 dispatches it.

**ISA 0.9 provision:** ISA-3.3-P8, ISA-4.3 and ISA-8.3 supply classed allocations and target classes; no gap.

**Proposed normative resolution:**

> Allocation class zero MUST denote any, and positive class indices MUST select the existing link-order class-name table. [deps: DLT-3.4-P18, DLT-3.4-P22, ISA-3.3-P8, ISA-8.3]

**Rejected alternatives:** Accepting only class zero or merging classes without names loses the requested resource class.

**Conformance consequence:** DA/DB/DL: retain operand-class and class-table ordering/load-error cases; DS checks actual class allocation.

**Dependency order:** I18; I19 only changes width realisation.

**Maintainer choice:** D10 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i05"></a>
### I05 — Per-region budget tables

**Bead:** `b-dialect-spec-8wf.5`. **Group:** 0.2.11. **Decision:** D02. **Audit:** D2.

**0.1 capability/history:** 0.1 offered only B_default, requiring source annotations or no per-region memory budgets.

**0.2.10 delta:** DLT-9.2-P2 through P8 already define defaults, region-key/glob precedence, one-shot selection_identity overlay, frozen capacities and final-object tokens.

**ISA 0.9 provision:** ISA-5.4-P2, ISA-5.4-P3 and ISA-10 provide the four-component launch tuple; K3 preserves tuple identity at device minting; no table instruction is missing.

**Proposed normative resolution:**

> Per-region budget resolution MUST retain the staged baseline, frozen layout, single selection_identity overlay and final-identity token binding, with explicit non-sentinel marker fields applied after lookup. [deps: DLT-9.1-P7, DLT-9.2-P4, DLT-9.2-P5, DLT-9.2-P6, DLT-9.2-P7, DLT-9.2-P8, ISA-5.4-P3]

**Rejected alternatives:** Iterating the final hash back into lookup creates cycles; steps-only records or source edits would restore the narrowing.

**Conformance consequence:** DD/DM: retain budget-stage including H16/H32 and multiple shapes; check tuple/hash change separately. DX4/7/8 use out-of-band records.

**Dependency order:** I33 before table users; feeds I20, I07, I17 and I40.

**Maintainer choice:** D02 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i06"></a>
### I06 — Classical oracle arguments

**Bead:** `b-dialect-spec-8wf.6`. **Group:** 0.2.11. **Decision:** D03. **Audit:** D3.

**0.1 capability/history:** 0.1 required front ends to specialise constants into a scalar oracle rather than passing fixed-at-entry classical values.

**0.2.10 delta:** DLT-8.2-P3 and DLT-8.4-P1 already pass ARG carrier bits, excluding their values from shape identity; DLT-16.2-P11 maps args.

**ISA 0.9 provision:** ISA-4.7-P1.S5/S6/S7 and ISA-3.7 explicitly forward classical/token parameters, and ISA-12.3-P2 binds exact argument bits; no gap.

**Proposed normative resolution:**

> ARG bindings MUST carry the caller's fixed-at-entry values in parameter order without specialising their values into the shape, and pointer arguments MUST retain entry-state semantics. [deps: DLT-8.2-P3, DLT-8.4-P1, DLT-8.5, ISA-4.7-P1, ISA-12.3-P2]

**Rejected alternatives:** Packing all inputs or constant-specialising every runtime argument imposes source/ABI restrictions the accepted descriptor removed.

**Conformance consequence:** DO/DM: two invocations of one shape with different ARG bits and pointer-rich entry state; mutate params_hash to ensure replay refuses the wrong binding. DX4 uses classical database length.

**Dependency order:** I17, I40; unchanged marker ABI.

**Maintainer choice:** D03 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i07"></a>
### I07 — Full lifted LLVM closure

**Bead:** `b-dialect-spec-8wf.7`. **Group:** 0.2.11. **Decision:** D04. **Audit:** D4, B-39.

**0.1 capability/history:** 0.1 BD-E-LIFT-SUBSET excluded memory, calls, FP and vectors, including ordinary SQLite query paths.

**0.2.10 delta:** DLT-16.1-P1 deletes the diagnostic and admits every materialised function; DLT-12.2-P38/C enumerate 546 generic intrinsics, and DLT-16.4 maps memory/calls/aggregates/carriers.

**ISA 0.9 provision:** ISA-4.2, ISA-3.7 and ISA-7.2 provide memory, allocation, lproc recursion and lifted control; E17.1 has no location-width cap, but the existing canonical dialect limb map remains valid.

**Proposed normative resolution:**

> Every materialised function in an oracle closure MUST remain liftable through the complete normalisation and mapping tables, including memory, recursion, indirect calls, vectors and floating-point carriers. [deps: DLT-12.2, DLT-C, DLT-16.1-P1, DLT-16.4, ISA-3.7, ISA-4.2, ISA-7.2]

**Rejected alternatives:** A scalar-only profile, silently trapping an unsupported generic intrinsic, or limiting the contract to checker seeds narrows scope.

**Conformance consequence:** DN/DM/DV/DR/DF/DX: retain all N0–N35 and V1–V16 rows; memory/recursive/wide/vector/FP/varargs witnesses, native comparison and prefix reversal; SQLite full closure is the rung-4 gate, not a mini substitute.

**Dependency order:** I33, I17, I22/I35, I15, I37, I12, I36; map after normalisation.

**Maintainer choice:** D04 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i08"></a>
### I08 — Requested deferred measurement

**Bead:** `b-dialect-spec-8wf.8`. **Group:** 0.2.11. **Decision:** D09. **Audit:** D5, B-36.

**0.1 capability/history:** 0.1 refused measurement under unitary regions without the front-end opt-in promised by the north star.

**0.2.10 delta:** DLT-7.5 and DLT-18.2 already specify deferred channel records, placement under standalone adjoint/compute and a declared observation boundary; default refusal remains intentional.

**ISA 0.9 provision:** ISA-4.4, ISA-4.6 and ISA-12.1 provide coherent copies, predicates and channel claims; K64/65 matter only when scheduled support/cleanup points are bound.

**Proposed normative resolution:**

> Front-end-requested deferred measurement MUST retain its channel records through the declared observation boundary, including the accepted standalone-adjoint and compute placement rules. [deps: DLT-7.5, DLT-18.2, ISA-4.4, ISA-4.6, ISA-12.1]

**Rejected alternatives:** Measuring immediately changes the controlled instrument; uncopying retained channel records silently turns the channel into a unitary.

**Conformance consequence:** DT/DS: retain deferred-channel-adj-place and compute/loop boundary cases, both control values and superposition; refusal without opt-in remains a negative.

**Dependency order:** I01; I-gwf for certificate record, D01 for scheduled claims.

**Maintainer choice:** D09 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i09"></a>
### I09 — Borrowing outside generations

**Bead:** `b-dialect-spec-8wf.9`. **Group:** 0.2.11. **Decision:** D11. **Audit:** D6, B-49.

**0.1 capability/history:** 0.1 used T-BORROW outside a generation.

**0.2.10 delta:** DLT-18.3 already deletes T-BORROW and uses clean allocation outside statically verified borrow frames.

**ISA 0.9 provision:** ISA-4.3, ISA-5.6 and ISA-9.4 provide dirty borrowing inside actions; direct CC dirty borrowing remains an efficiency primitive absent from 0.9, with the existing clean construction retaining capability.

**Proposed normative resolution:**

> A borrow outside a verified static action frame MUST retain the clean-allocation construction, while static action borrows MUST meet the ISA borrow-frame restoration conditions. [deps: DLT-18.3, DLT-25.3, ISA-4.3, ISA-5.6, ISA-9.4]

**Rejected alternatives:** Reinstating T-BORROW drops capability; treating arbitrary dirty state as clean without restoration is unsound.

**Conformance consequence:** DB/DS: clean fallback outside generation plus entangled dirty-frame restoration in ISA suite G; quantify costs separately, never label clean fallback as dirty savings.

**Dependency order:** I19/I32 for dynamic or R allocation; otherwise independent.

**Maintainer choice:** D11 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i10"></a>
### I10 — Handle equality and null tests

**Bead:** `b-dialect-spec-8wf.10`. **Group:** 0.2.11. **Decision:** D11. **Audit:** D8, B-19.

**0.1 capability/history:** 0.1 rejected ordinary icmp eq/ne on handles (C null checks and Rust Option niches).

**0.2.10 delta:** DLT-6.3-P1 already compares allocation generations, not reusable slots, and removes provenance from the result.

**ISA 0.9 provision:** ISA-3.3-P7, ISA-3.3-P13 and ISA-4.1-P4 give immutable ids and equality; tag-to-id bridging remains necessary at non-64-bit dialect pointer widths.

**Proposed normative resolution:**

> Handle equality and null tests MUST compare allocation identity, preserve stale-versus-new inequality and produce a result without handle provenance. [deps: DLT-6.1-P1, DLT-6.3-P1, ISA-3.3-P7, ISA-4.1-P4]

**Rejected alternatives:** Physical-slot equality or id truncation aliases generations; banning null checks again breaks unmodified language idioms.

**Conformance consequence:** DB/DS: retain handle-stale-generation, null/live equality and slot-reuse witnesses; add lookup-path aliases to the same ledger id and a narrow-pointer bridge case.

**Dependency order:** I17; I-cbe/I25 extend representation without changing equality.

**Maintainer choice:** D11 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i11"></a>
### I11 — General allocation sites

**Bead:** `b-dialect-spec-8wf.11`. **Group:** 0.2.11. **Decision:** D07. **Audit:** D9.

**0.1 capability/history:** 0.1 recognised only seven allocators, sending custom and Julia allocation results to TOP.

**0.2.10 delta:** DLT-5.1-P4, DLT-5.1-P6 admit alloc attributes and language/runtime allocators; DLT-5.2-P10 propagates defined wrappers' parameters/returns, so a wrapper over a fresh site does not require a new named allocator.

**ISA 0.9 provision:** Analysis is dialect-owned; ISA-4.1-P9, ISA-4.2 and ISA-7.1 and ISA-7.2 realise its allocations. No cross-repo analysis helper or new ISA sentence.

**Proposed normative resolution:**

> Abstract-object and return propagation MUST cover attributed allocator calls and defined allocator wrappers through their underlying allocation sites without requiring the wrapper's name in a whitelist. [deps: DLT-5.1-P4, DLT-5.1-P6, DLT-5.2-P10, ISA-7.1, ISA-7.2]

**Rejected alternatives:** A new whitelist of wrapper names or TOP for every non-libc return reinstates the same restriction; inventing freshness for opaque external code is unsound.

**Conformance consequence:** DB: custom wrapper and Julia/C++ attributed sites, return into a collection, separate unknown external negative. DR verifies allocator behaviour independently.

**Dependency order:** I22/I35 call graph; precedes I25/I26/I30.

**Maintainer choice:** D07 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i12"></a>
### I12 — Exceptions and unwinding

**Bead:** `b-dialect-spec-8wf.12`. **Group:** 0.2.11. **Decision:** D12. **Audit:** D10, B-12.

**0.1 capability/history:** 0.1 BD-E-EH excluded invoke/landingpad, Rust panics and C++ throw in device closures.

**0.2.10 delta:** DLT-14.4 and N28 already provide EH state, personality matching, early returns and code 4 only when unwinding escapes a region; Windows funclets are specified, with corpus work still named.

**ISA 0.9 provision:** ISA-4.1-P11, ISA-4.2 and ISA-7.4 provide ordinary calls/memory/history; K5/K6 resolve typed terminal R faults, without adding an LLVM EH opcode.

**Proposed normative resolution:**

> Device exceptions MUST retain explicit propagation and in-region handler execution, with a region-escaping exception reported through that tier's declared fault path. [deps: DLT-14.4, DLT-12.2-P30, ISA-4.1-P11, ISA-4.2, ISA-4.9]

**Rejected alternatives:** Rejecting all unwinding or replacing an in-region catch with fault 4 changes defined program behaviour.

**Conformance consequence:** DV/DN/DS: C++ caught throw, Rust cleanup and escaping panic, funclet corpus as mechanics coverage; execute R failure/reverse after I-bz6.

**Dependency order:** I22/I35 and I07; before sjlj/fiber/platform composition in I39.

**Maintainer choice:** D12 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i13"></a>
### I13 — Device models and libc virtualisation

**Bead:** `b-dialect-spec-8wf.13`. **Group:** 0.2.11. **Decision:** D05. **Audit:** D11, B-17, B-51.

**0.1 capability/history:** 0.1 faulted external calls in oracle/R closures instead of virtualising libc and the four promised devices.

**0.2.10 delta:** DLT-4.5, DLT-11.1-P2 through DLT-11.1-P7, DLT-11.2 and DLT-11.3 already supply shims, R tape, L memory models and inherited action state; blanket F(8) is gone.

**ISA 0.9 provision:** ISA-7.3 and ISA-7.4 provide reversible models, K10 complete block sectors, E13 permits lifted entropy code 10 (ISA-5.4-P4), and K5/K6 fix failure reporting/reversal; no additional device opcode is needed for the four.

**Proposed normative resolution:**

> Modelled libc effects MUST retain the tier-specific host, reversible-tape or lifted-state realisation, and coherent device state MUST be initialised from the descriptor and reversed with the oracle prefix. [deps: DLT-4.5, DLT-11.1, DLT-11.2, DLT-11.3, ISA-7.3, ISA-7.4, ISA-5.4-P4]

**Rejected alternatives:** F(8) for a modelled VFS/entropy call narrows SQLite/Monte Carlo; native host calls from R/L violate effect closure.

**Conformance consequence:** DE/DR/DO: binding-block-byte/clock-read/console-byte plus full overlay write/read/reversal and entropy exhaustion; DX3 tape replay, DX4 image VFS, DX8 superposed entropy. Unmodelled reached effects retain trapped coverage.

**Dependency order:** I17, I07, I37; R fault cases wait on I-bz6, successful model paths do not.

**Maintainer choice:** D05 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i14"></a>
### I14 — In-place evidence above small widths

**Bead:** `b-dialect-spec-8wf.14`. **Group:** 0.2.11. **Decision:** D14. **Audit:** D14, B-41.

**0.1 capability/history:** 0.1 required a library inverse claim above 16 bits and otherwise rejected.

**0.2.10 delta:** DLT-8.7-P6 already has configurable exhaustive width (default 24), sampled evidence, independent sound B_bound and universal inverse assumptions; T-CLEAN alone is not a proof.

**ISA 0.9 provision:** ISA-12.1-P2/K13 preserves sampled evidence, but K4 native qinplace requires ISA-12.1-P1 or P3 exhaustive/library authority. The existing CC expansion is legal under ISA-3.3 cleanliness and ISA-4.7 without a qinplace instruction; no ISA gap.

**Proposed normative resolution:**

> Pairs admitted with sampled evidence and the recorded universal inverse and sound-bound obligations MUST retain the CC expansion, and MUST NOT be labelled a native qinplace inverse-pair proof on the strength of sampling or T-CLEAN. [deps: DLT-8.7-P5, DLT-8.7-P6, ISA-3.3-P9, ISA-4.7, ISA-4.5-P5, ISA-12.1-P1, ISA-12.1-P2]

**Rejected alternatives:** Library-only admission narrows scope; claiming a sampled maximum is B_min or using a sampled claim as K4 authority is unsound.

**Conformance consequence:** DO/DS: above-threshold sampled pair accepted on CC path, insufficient B_bound and bad inverse fail loudly; K4 path has a separate missing-covering-entry negative. Replay binds explicit expected relation and invocation.

**Dependency order:** I03/I17/I33 and I-gwf; optional native path gated by D01.

**Maintainer choice:** D14 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i15"></a>
### I15 — All seven FP formats and vector/libm FP

**Bead:** `b-dialect-spec-8wf.15`. **Group:** 0.2.11. **Decision:** D04. **Audit:** D16, B-45.

**0.1 capability/history:** 0.1 N17 trapped half, bfloat, x86_fp80, fp128, transcendentals and vector FP beyond f32/f64.

**0.2.10 delta:** DLT-13.1 through DLT-13.5 already cover seven formats including ppc_fp128, own-format carrier routines, bit-exact retained forms and constrained environments; DLT-12.1-P1 puts N33 before N32.

**ISA 0.9 provision:** ISA-4.1 and ISA-4.2 integer operations, memory and calls implement soft float; no new FP ISA is required. Libraries remain separately implemented contract consumers.

**Proposed normative resolution:**

> All seven formats MUST retain own-format arithmetic and transcendental semantics, with vector operations scalarised first and identical deterministic carrier implementations in the materialised native and lifted builds. [deps: DLT-13.1, DLT-13.2, DLT-13.3, DLT-13.4, DLT-13.5, DLT-12.1-P1, ISA-4.2]

**Rejected alternatives:** Silent widening through f64/native long double, deleting retained fneg/transport, or faulting uncovered checker formats would narrow the accepted contract.

**Conformance consequence:** DF/DN/DM: seven-format bit/NaN/rounding/carrier and pair-result probes, vector reductions, powi exponent width, fmt_fp and DX8 libm. Keep V10 carrier positives and arithmetic residue negatives.

**Dependency order:** I07 map foundation, N21 before FP rewrite and repeated N22 after wide conversions.

**Maintainer choice:** D04 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i16"></a>
### I16 — Mixed LLVM majors

**Bead:** `b-dialect-spec-8wf.16`. **Group:** 0.2.11. **Decision:** D13. **Audit:** D19, B-53.

**0.1 capability/history:** 0.1 required one LLVM major per link, excluding Julia/runtime combinations in the tested envelope.

**0.2.10 delta:** DLT-19.8 already reads with the newest supported major and preserves a single target triple/DataLayout; DLT-21.1 publishes the envelope.

**ISA 0.9 provision:** This is a driver/LLVM-reader contract, not an ISA capability; ISA-9.1/9.2 encode the produced object independently.

**Proposed normative resolution:**

> Mixed-major bitcode links within the tested envelope MUST use its newest reader and matching plugin and library bitcode, retaining one target triple and DataLayout. [deps: DLT-19.8, DLT-21.1, ISA-9.1, ISA-9.2]

**Rejected alternatives:** One-major-only linkage or promising arbitrary newer bitcode beyond the tested reader both contradict the envelope contract.

**Conformance consequence:** DD/DL: retain driver-mixed-majors actual 18+23 link result 7, incompatible triple/major negatives, and Julia/rustc envelope rows; parsing each module alone is insufficient.

**Dependency order:** I34 driver mode; independent of ISA 0.9 capability work.

**Maintainer choice:** D13 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i17"></a>
### I17 — Multiple inputs, memory and out-parameters

**Bead:** `b-dialect-spec-8wf.17`. **Group:** 0.2.11. **Decision:** D03. **Audit:** D21, B-32.

**0.1 capability/history:** 0.1 oracles had one packed input and scalar iT(iN) signatures, excluding independent register/memory/result bindings.

**0.2.10 delta:** DLT-8.1/8.2 already define the five-kind descriptor, flattening, MEM_IN, OUT, arbitrary result slicing and zero-output execution; DLT-8.6 uses 2k-1 calls rather than the older outline's k+2.

**ISA 0.9 provision:** ISA-4.7-P1, ISA-5.1/5.2, ISA-7.2 and ISA-3.3-P19 express all lists and XOR outputs; wide targets have no type cap in E17.1, but retaining canonical chunking avoids an unneeded budget-semantic change.

**Proposed normative resolution:**

> The descriptor MUST retain independent IN, ARG, MEM_IN, OUT and INOUT bindings, packed field order, preserved inputs, common-delivery validation and exactly one synthetic invocation for zero payload outputs. [deps: DLT-8.1, DLT-8.2, DLT-8.6, DLT-16.2-P17, ISA-4.7, ISA-5.2, ISA-7.2]

**Rejected alternatives:** Source packing wrappers, return-only results, the superseded k+2 scheme or deleting the zero-output call change the admitted interface or fault outcome.

**Conformance consequence:** DO/DM/DS: binding-out-byte, multi-IN, 160-bit OUT, oracle-empty-output/fault/discard-return; arbitrary initial target/fault values and control=0/1. DX4 rowid + image + classical length, DX7 syscall args + snapshot.

**Dependency order:** I33, I22 and I40; prerequisite for I06, I03, I13 and I19 shape dispatch.

**Maintainer choice:** D03 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i18"></a>
### I18 — Runtime operation codes and classes

**Bead:** `b-dialect-spec-8wf.18`. **Group:** 0.2.11. **Decision:** D10. **Audit:** B-06.

**0.1 capability/history:** 0.1 rejected unbounded op/cls value sets despite their finite valid tables.

**0.2.10 delta:** DLT-3.4 already dispatches full valid tables for top op/cls and traps only runtime out-of-table values.

**ISA 0.9 provision:** ISA-4.1-P4, ISA-4.1-P10 and ISA-4.4 provide comparison, branching and the selected operation; no indirect gate opcode is needed.

**Proposed normative resolution:**

> A top operation-code or class value set MUST dispatch the entire valid table and retain the existing out-of-table runtime diagnostic. [deps: DLT-3.4, DLT-5.3, ISA-4.1-P4, ISA-4.1-P10, ISA-4.4]

**Rejected alternatives:** BD-E-OPERAND-UNBOUNDED for a finite-table selector reinstates the narrowing; remapping an invalid code silently is incorrect.

**Conformance consequence:** DA/DS: every code/class entry, unknown runtime selector, constant-invalid negative; DT Co selector uses predication rather than classical inspection.

**Dependency order:** I04; I01 for coherent selectors.

**Maintainer choice:** D10 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i21"></a>
### I21 — Benign marker attributes

**Bead:** `b-dialect-spec-8wf.21`. **Group:** 0.2.11. **Decision:** D09. **Audit:** B-11.

**0.1 capability/history:** 0.1's whitelist refused benign build-flag attributes such as strictfp/cold/noinline/optnone.

**0.2.10 delta:** DLT-3.6 already includes the requested benign list and keeps licensing/unknown attributes fail-loud; DLT-21.2 requires three-major corpus coverage.

**ISA 0.9 provision:** No ISA change: this is LLVM marker preservation, followed by ISA-13 coverage reporting.

**Proposed normative resolution:**

> The benign, forbidden and unknown marker-attribute classification MUST retain the accepted list and be checked against dynamic marker-sequence preservation on every supported LLVM major. [deps: DLT-3.6, DLT-21.1, DLT-21.2, ISA-13]

**Rejected alternatives:** Reverting to the spike-only whitelist narrows build flags; declaring all attributes benign permits elimination/speculation.

**Conformance consequence:** DA/DL L1/L2/L5: attr-strictfp-cold plus the full benign matrix and forbidden negative controls; no changed verdict just to accommodate a parser.

**Dependency order:** Independent; precedes any marker ABI change (none proposed here).

**Maintainer choice:** D09 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i22"></a>
### I22 — Polyvariant function cloning

**Bead:** `b-dialect-spec-8wf.22`. **Group:** 0.2.11. **Decision:** D06. **Audit:** B-16.

**0.1 capability/history:** 0.1 BD-E-DEVICE-ADDRESS prohibited a host address of a device function, breaking shared SQLite use.

**0.2.10 delta:** DLT-4.3-P1 already clones per tier/coherence signature, shares globals and deletes the error; DLT-4.4 fixes one comparison-link A(F).

**ISA 0.9 provision:** ISA-4.1 and ISA-4.2 and ISA-9.1/9.2 realise tier-specific bodies and shared data images; no multi-address function primitive is missing.

**Proposed normative resolution:**

> Host and device variants MUST retain a common comparison-link function address and shared global data, while dispatch selects the variant for the caller's tier and coherence signature. [deps: DLT-4.3-P1, DLT-4.4, DLT-19.5, ISA-4.1, ISA-4.2, ISA-9.1]

**Rejected alternatives:** Duplicating globals changes state; replacing stored addresses by clone addresses breaks comparisons/VFS tables; restoring BD-E-DEVICE-ADDRESS narrows libraries.

**Conformance consequence:** DB/DM/DD: host builds a table and L queries through it; same function used H/CC/R/L, A(F) comparison/hash stable, one mutable global. DX4 includes host-built SQLite database.

**Dependency order:** I35 with I11 analysis fixpoint; before I07 and all callback/region consumers.

**Maintainer choice:** D06 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i23"></a>
### I23 — Handles through callbacks and returned addresses

**Bead:** `b-dialect-spec-8wf.23`. **Group:** 0.2.11. **Decision:** D06. **Audit:** B-22.

**0.1 capability/history:** 0.1 rejected handles passed to indirect callees and returns from address-taken functions.

**0.2.10 delta:** DLT-5.2-P10 and DLT-6.2-P5 and DLT-6.4 already propagate to every candidate parameter and return, retaining true unknown/host escape checks.

**ISA 0.9 provision:** ISA-3.3-P21 explicitly carries qreg aliases through call/ret/br; comparison trees use ISA-4.1 and ISA-4.2. No indirect-call opcode is needed.

**Proposed normative resolution:**

> Handle provenance MUST flow through every indirect-call candidate's parameters and results exactly as through a direct defined call. [deps: DLT-5.2-P10, DLT-6.2-P5, DLT-6.4, ISA-3.3-P21, ISA-4.1-P11]

**Rejected alternatives:** Blanket address-taken/indirect escape rejects visible device code; allowing an opaque host callee to consume handles violates containment.

**Conformance consequence:** DB/DS: callback taking/returning a handle, two candidates with different ROOTs, real host escape negative, identity/liveness preserved across return.

**Dependency order:** I35/I22; I25 for memory-reaching unbounded instances.

**Maintainer choice:** D06 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i24"></a>
### I24 — Dynamically indexed handle vectors

**Bead:** `b-dialect-spec-8wf.24`. **Group:** 0.2.11. **Decision:** D07. **Audit:** B-23.

**0.1 capability/history:** 0.1 rejected non-constant insertelement/extractelement lanes for handles.

**0.2.10 delta:** DLT-5.2-P11 and DLT-6.2-P1 already use N15 total unsigned index semantics, per-lane provenance and zero only for actual out-of-range alternatives.

**ISA 0.9 provision:** ISA-4.1 and ISA-4.2 select/compare and K1 lookup realise classical table selection; no vector-handle ISA required.

**Proposed normative resolution:**

> Dynamically indexed handle vectors MUST use PT10 lane provenance and N15 total index semantics, retaining explicit ROOT atoms and adding zero only for possible out-of-range extraction. [deps: DLT-5.2-P11, DLT-6.2-P1, DLT-12.2-P17, ISA-4.1, ISA-4.2]

**Rejected alternatives:** Constant-lane-only acceptance narrows collections; merging packed scalar integers as lane values or dropping ROOTs is unsound.

**Conformance consequence:** DB/DN/DS: dynamic handle lane, narrow i1 lane and out-of-range extract/insert cases; retain PT3 pack257/pack256/unpack regressions.

**Dependency order:** I11/I27; I25 for dynamic register lookup, without changing the reference AV rule.

**Maintainer choice:** D07 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i26"></a>
### I26 — Linked handle structures

**Bead:** `b-dialect-spec-8wf.26`. **Group:** 0.2.11. **Decision:** D07. **Audit:** B-26.

**0.1 capability/history:** 0.1 disallowed storing/returning an object that contained a handle.

**0.2.10 delta:** DLT-6.4-P1 already admits linked structures and tracked escaping objects; DLT-6.4-P2 excludes actual unknown-reader escape only.

**ISA 0.9 provision:** ISA-7.1 memory and ISA-3.3 K1 ids suffice; finite structures already have the static-file construction. No new pointer graph opcode.

**Proposed normative resolution:**

> A tracked object containing handles MUST remain storable and returnable through other tracked objects, with escape decided by the reachable handle slots rather than object escape alone. [deps: DLT-5.2, DLT-6.4-P1, DLT-6.4-P2, ISA-7.1, ISA-3.3]

**Rejected alternatives:** Object-level escape bans prohibit lists/trees; ignoring an actual unknown reader discards the north-star containment rule.

**Conformance consequence:** DB/DS: two-level list/tree with handle field, returned node and stored header, host-read handle-slot negative; dynamic-size variant in I25.

**Dependency order:** I11/I27; I25 removes only the unbounded naming blocker.

**Maintainer choice:** D07 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i27"></a>
### I27 — Field-sensitive handle provenance

**Bead:** `b-dialect-spec-8wf.27`. **Group:** 0.2.11. **Decision:** D07. **Audit:** B-27.

**0.1 capability/history:** 0.1 variable-index handle arrays tainted adjacent pointer-width integer counters as handle-derived.

**0.2.10 delta:** DLT-5.1-P7, DLT-5.2-P3, DLT-5.2-P7, DLT-5.2-P8 already track offset residues, storage intervals and representation widths; declared array size is not an actual index bound.

**ISA 0.9 provision:** Analysis-only change; ISA-4.1 and ISA-4.2 provide ordinary pointer/integer operations. No ISA sentence needed.

**Proposed normative resolution:**

> Handle-array propagation MUST retain field intervals and finite-width address images so that a disjoint integer counter is not handle-derived, without treating an array type as a proof that indices stay in bounds. [deps: DLT-5.1-P7, DLT-5.2-P3, DLT-5.2-P7, DLT-5.2-P8, ISA-4.1, ISA-4.2]

**Rejected alternatives:** Field-insensitive TOP restores the false rejection; assuming array bounds or using mathematical instead of modular GEP loses reachable slots.

**Conformance consequence:** DB/DN: array-plus-size_t counter, modular GEP/index-width and partial-overlap negatives; retain gep-index-obj and pointer-width probes.

**Dependency order:** I11; before I24/I26/I28.

**Maintainer choice:** D07 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i28"></a>
### I28 — Handle fields in shared globals

**Bead:** `b-dialect-spec-8wf.28`. **Group:** 0.2.11. **Decision:** D07. **Audit:** B-29.

**0.1 capability/history:** 0.1 rejected any handle-bearing global mentioned by any host function.

**0.2.10 delta:** DLT-6.4-P1, DLT-6.4-P2, DLT-6.4-P3 already analyse fields and allow visible host transport of opaque launch ids under handle rules; unknown readers remain escape.

**ISA 0.9 provision:** ISA-10 launch ids and ISA-3.3 ledger state realise transport; no shared-global ban is imposed by ISA.

**Proposed normative resolution:**

> A global handle field MUST be analysed by reachable byte slots, allowing analysed host transport under the handle rules and retaining rejection only for an actual prohibited use or unknown-reader escape. [deps: DLT-5.2, DLT-6.4, DLT-6.6, ISA-3.3, ISA-10]

**Rejected alternatives:** A name-based host-reference ban confuses unrelated fields; letting host native code dereference or perform arithmetic on handles violates provenance.

**Conformance consequence:** DB/DS/DD: host touches only adjacent count, host copies opaque handle back to entry, unknown-reader and dereference negatives.

**Dependency order:** I27/I29; I-cbe for persistent roots.

**Maintainer choice:** D07 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i30"></a>
### I30 — Region operands loaded from heap objects

**Bead:** `b-dialect-spec-8wf.30`. **Group:** 0.2.11. **Decision:** D06. **Audit:** B-33.

**0.1 capability/history:** 0.1 C3 returned TOP/BD-E-REGION-UNBOUNDED for stored callbacks, heap closures and escaping objects.

**0.2.10 delta:** DLT-7.2-P2, DLT-7.2-P3, DLT-7.2-P5 already uses all matching address-taken functions when AV has top and guarantees a program-bounded candidate set; DLT-12.8-P10 expands load.relative.

**ISA 0.9 provision:** ISA-4.1 and ISA-4.2 compares and static calls supply dispatch; ISA-9.2 content identities remain independent of source pointer spelling. No ISA gap.

**Proposed normative resolution:**

> Region operands loaded from tracked memory or relative tables MUST use the reference candidate analysis and its type-compatible address-taken fallback, with no blanket TOP rejection. [deps: DLT-5.2, DLT-7.2, DLT-12.8-P10, ISA-4.1, ISA-4.2, ISA-9.2]

**Rejected alternatives:** Rejecting every imprecise candidate set or any over-approximated ill-formed candidate narrows correct executions; selected invalid/no-match candidates keep the accepted runtime faults.

**Conformance consequence:** DC/DB: heap closure, std::function-like object, relative function table, alias/thunk cycle, selected-invalid and no-match negatives.

**Dependency order:** I11/I22/I35; I-0t9 fixes only example selection evidence.

**Maintainer choice:** D06 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i31"></a>
### I31 — Reversible calls inside actions

**Bead:** `b-dialect-spec-8wf.31`. **Group:** 0.2.11. **Decision:** D08. **Audit:** B-37.

**0.1 capability/history:** 0.1 BD-E-REGION-TIER rejected a reversible call reached during action generation.

**0.2.10 delta:** DLT-7.4 already treats it as a direct body call inheriting the action/TDL context; DLT-11.5-P2.S3 excludes it from the R-entry blocker.

**ISA 0.9 provision:** ISA-4.7/5.3 controlled calls and lifted bodies suffice; R-to-CC is still not an ISA call-tier edge, so the accepted transform is important.

**Proposed normative resolution:**

> A reversible marker reached during action generation MUST retain direct-body generation and inherited TDL/effect semantics rather than creating an R entry. [deps: DLT-7.4, DLT-10, DLT-11.5-P2, ISA-3.1, ISA-4.7, ISA-5.3]

**Rejected alternatives:** Creating an actual R call from a coherent event list would evade predication; reintroducing region-tier rejection loses inferred lifting.

**Conformance consequence:** DC/DT/DS: retain region-reversible-in-action and controlled escaping-store state, with no BLK-5 due solely to that marker.

**Dependency order:** I01/I13; independent of I-bz6 for this direct-call case.

**Maintainer choice:** D08 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i33"></a>
### I33 — Four-component budgets

**Bead:** `b-dialect-spec-8wf.33`. **Group:** 0.2.11. **Decision:** D02. **Audit:** B-42.

**0.1 capability/history:** 0.1 hard-coded (B,0,0,0), making memory/call lifting fault immediately.

**0.2.10 delta:** DLT-9.1-P1 through P7, DLT-9.4-P2 and DLT-17.3 already separate rows, heap bytes, lifted stack cells and depth; sstack bytes are a heap-backed layout input, not a fifth ISA limit.

**ISA 0.9 provision:** ISA-5.4-P2, ISA-5.4-P3 and ISA-3.7 provide the same four counters; neither ISA 0.9 nor runtime budget minting changes their units.

**Proposed normative resolution:**

> Every oracle budget MUST retain explicit steps, heap, stack and depth components and charge wrapper, replay and helper rows under the canonical map, with shadow-stack backing charged to heap. [deps: DLT-9.1, DLT-9.4, DLT-17.3, ISA-5.4-P2, ISA-3.7]

**Rejected alternatives:** Memoryless tuples for a memory-using body, treating stack cells as bytes or omitting replay/helper cost changes the fault set.

**Conformance consequence:** DO/DM/DD: zero/just-below/exact boundary for each component, alloc-zero max(n,1), recursive frame charge and logical shadow-stack liveness; DX2/4/7/8 budget records.

**Dependency order:** Foundation before I05, I07, I17, I20 and I40.

**Maintainer choice:** D02 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i34"></a>
### I34 — Closed-unit fast path

**Bead:** `b-dialect-spec-8wf.34`. **Group:** 0.2.11. **Decision:** D13. **Audit:** B-54.

**0.1 capability/history:** 0.1 banned Bennett processing in every per-TU phase, including programs closed in one unit.

**0.2.10 delta:** DLT-19.7 already provides an explicit closedness check, identical whole-program semantics and fallback on failure; normal pre-link LTO still does no Bennett processing.

**ISA 0.9 provision:** ISA-9.2/9.3 content objects and linking support incremental REPL work; no ISA change.

**Proposed normative resolution:**

> Closed-unit mode MUST retain whole-program semantics after its closedness check and fall back to whole-program processing when that check fails. [deps: DLT-19.1, DLT-19.7, ISA-9.2, ISA-9.3]

**Rejected alternatives:** Rejecting a nonclosed unit rather than falling back narrows the fast path contract; running before final link without closedness can miss context.

**Conformance consequence:** DD/DL: driver-closed-unit-fallback and closed/whole equivalence, external callback input and address escape fallback, incremental reuse of unchanged objects.

**Dependency order:** I22/I35 call graph and I16 reader policy.

**Maintainer choice:** D13 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i35"></a>
### I35 — Indirect calls in device code

**Bead:** `b-dialect-spec-8wf.35`. **Group:** 0.2.11. **Decision:** D06. **Audit:** O-01.

**0.1 capability/history:** 0.1 had direct call edges only and no device indirect-call lowering, excluding SQLite VFS/pcache callbacks.

**0.2.10 delta:** DLT-4.1-P12, DLT-14.2-P1 through P5 and DLT-16.4-P25 already specify closure candidates and sorted compare-tree static calls in CC/R/L.

**ISA 0.9 provision:** ISA-4.1-P4, ISA-4.1-P10, ISA-4.1-P11, ISA-4.2 and ISA-3.7 suffice. Native indirect calls remain optional efficiency, not a missing universal primitive.

**Proposed normative resolution:**

> Every device indirect call MUST retain the reference candidate closure and compare-tree lowering to tier-appropriate static calls, using comparison-link addresses and the accepted no-match fault. [deps: DLT-4.1-P12, DLT-14.2, DLT-16.4-P25, ISA-4.1, ISA-4.2, ISA-3.7]

**Rejected alternatives:** Requiring devirtualisation or rewriting SQLite narrows scope; qjumpr is intra-function and cannot substitute for a call.

**Conformance consequence:** DB/DC/DM/DV: qsort-style callback, VFS table from host, Co function-pointer selection, variadic callback and no-match fault; DX4 full query path includes indirect sites.

**Dependency order:** I22/I11 as one S2 fixpoint; before I23/I30/I37.

**Maintainer choice:** D06 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i36"></a>
### I36 — Inline assembly and target intrinsics

**Bead:** `b-dialect-spec-8wf.36`. **Group:** 0.2.11. **Decision:** D12. **Audit:** O-02.

**0.1 capability/history:** 0.1 omitted syscall asm and host-target intrinsic classification.

**0.2.10 delta:** DLT-15 and N31 already give lowered/shimmed/trapped coverage, syscall/device shims, per-target tables and platform extension patterns.

**ISA 0.9 provision:** ISA-4.1 and ISA-4.2, ISA-7.3 and ISA-13 realise operations, effects and coverage; no universal asm ISA is necessary.

**Proposed normative resolution:**

> Inline assembly and target intrinsics MUST retain the per-target lowered, shimmed or trapped classification with shim identity and a reached unmodelled-effect fault, rather than rejecting an entire device closure for containing asm. [deps: DLT-15, DLT-12.2-P33, ISA-4.1, ISA-7.3, ISA-13]

**Rejected alternatives:** Blanket asm rejection removes musl/kernel paths; treating a syscall as a no-op silently changes effects; patterns do not constitute a completed platform inventory.

**Conformance consequence:** DN/DL/DR/DP: musl __syscall on three ABIs, memory-clobber no-op, clock shim, unknown asm reached/unreached coverage; .S symbol shims inventoried by platform spike.

**Dependency order:** I13/I39 platform profile; prerequisite for DX3/6/7.

**Maintainer choice:** D12 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i37"></a>
### I37 — Varargs

**Bead:** `b-dialect-spec-8wf.37`. **Group:** 0.2.11. **Decision:** D12. **Audit:** O-03.

**0.1 capability/history:** 0.1 omitted variadic definitions/calls, va_start/arg/copy/end and register-save layouts.

**0.2.10 delta:** DLT-14.3 and N23 already define va blocks and memory-path va_list records for x86-64 SysV, AAPCS64 and RISC-V LP64; indirect calls included.

**ISA 0.9 provision:** ISA-4.1-P8, ISA-4.1-P11, ISA-4.2 and ISA-7.1 and ISA-7.2 implement memory and calls; no varargs opcode missing.

**Proposed normative resolution:**

> Variadic calls and definitions MUST retain the N23 argument block and target va_list memory-path transform, including promoted scalar types, va_copy and indirect variadic calls. [deps: DLT-14.3, DLT-12.2-P25, ISA-4.1-P8, ISA-4.1-P11, ISA-4.2]

**Rejected alternatives:** Fixed-arity-only acceptance or relying on host register-save contents excludes printf/sqlite3_mprintf and misreads front-end va_arg expansion.

**Conformance consequence:** DV/DN/DM: sum varargs, integer/FP spills, copied lists and variadic callbacks on each ABI; actual printf/SQLite formatting paths in DX3/4, printk in DP.

**Dependency order:** I35/I15, N23 before N24 shadow-stack placement and lifting I07.

**Maintainer choice:** D12 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i39"></a>
### I39 — Kernel/runtime platform and control transfer

**Bead:** `b-dialect-spec-8wf.39`. **Group:** 0.2.11. **Decision:** D12. **Audit:** O-06.

**0.1 capability/history:** 0.1 omitted MMIO, interrupt delivery, privileged state, context switches, exec and setjmp/longjmp.

**0.2.10 delta:** DLT-14.5/14.6 and DLT-20 already give continuation/fiber transforms, riscv64 board state, MMIO-before-volatile stripping, poll points, Sv39 aliases and guest code dispatch; platform inventory remains mechanics work.

**ISA 0.9 provision:** ISA-4.1 and ISA-4.2, ISA-7.1, ISA-7.2 and ISA-7.3 and ISA-7.4 supply memory, effects and reversal. G-16 native fibers/interrupts remains absent but the rewindable-frame/poll construction keeps the capability.

**Proposed normative resolution:**

> The riscv64 platform MUST retain modelled MMIO, deterministic interrupt polls, rewindable contexts and Sv39 data/code translation in CC, R and L, with guest aliases naming the same backing bytes. [deps: DLT-14.5, DLT-14.6, DLT-20, ISA-4.1, ISA-4.2, ISA-7.3, ISA-7.4]

**Rejected alternatives:** Rejecting setjmp or turning volatile MMIO into an ordinary memfault drops platform scope; restricting translation to user mode breaks supervisor virtual memory.

**Conformance consequence:** DP/DV/DT: platform-uart-write plus poll/trap/return, context ping-pong, live setjmp continuation, Sv39 alias/pagefault and exec dispatch; DX6 QEMU-equivalent boot/unboot/tape, DX7 panic-bit snapshot oracle. Inventory/kernel scale is still work, never deleted.

**Dependency order:** I12/I13/I35/I36/I37/I38; I40 for runtime snapshot; I25 for continuation-surviving handle instances.

**Maintainer choice:** D12 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i-0t9"></a>
### I-0t9 — First-region-operand example metadata

**Bead:** `b-dialect-spec-0t9`. **Group:** 0.2.11. **Decision:** D20. **Audit:** historical example inconsistency.

**0.1 capability/history:** The narrowing-related action/reversible example once named body while the first textual marker operand was classical; this was an example-selector contradiction, not an ISA limitation.

**0.2.10 delta:** DLT-1.5-P9.S2 still defines first-region-operand selection, and accepted 0.2.10 already has region-reversible-in-action candidates=classical (main spec line2773 at the read snapshot). The bead description is stale; no remaining spec edit is justified.

**ISA 0.9 provision:** ISA-4.7 is the lowering context only. No ISA dependency or new sentence is missing.

**Proposed normative resolution:**

> The candidates attribute MUST continue to assert the resolved set of the first region operand in module instruction order, including nested-marker examples. [deps: DLT-1.5-P9, DLT-4.1, DLT-7.2, ISA-4.7]

**Rejected alternatives:** Silently redefining candidates to mean a chosen entry would break existing examples; editing accepted bytes to reapply an already-present fix is unnecessary.

**Conformance consequence:** DC recognise: assert classical for the existing example and a separate top-first reordered module selecting body; only claim closure after the regression runs against the current checker.

**Dependency order:** I31; independent of all ISA 0.9 work.

**Maintainer choice:** D20 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i-0y2"></a>
### I-0y2 — PT12 atomic-update transfers (nonblocking)

**Bead:** `b-dialect-spec-0y2`. **Group:** 0.2.11. **Decision:** D21. **Audit:** PT12 follow-up.

**0.1 capability/history:** 0.1's analysis restriction is not a new program capability here; the capability is correct S2 domains for already-admitted sequential atomic code.

**0.2.10 delta:** DLT-5.2-P13 says load plus store but omits explicit new-value transfer; DLT-5.2-P1.S7 and N9 (DLT-12.2-P11) already require materialised value effects, so this is a compatible clarification of reference analysis and checker repair.

**ISA 0.9 provision:** ISA-4.1 and ISA-4.2 plain operations/load/store realise the N9 expansion under the single-thread assumption; no atomic ISA required.

**Proposed normative resolution:**

> Before domains freeze, PT12 MUST apply PT6 to the old value, the PT5 transfers of the full N9 update, and PT7 to the actual stored value, with cmpxchg returning its old-value and success fields and storing the selected new-or-old value. [deps: DLT-5.2-P1, DLT-5.2-P6, DLT-5.2-P7, DLT-5.2-P8, DLT-5.2-P13, DLT-12.2-P11, ISA-4.1, ISA-4.2]

**Rejected alternatives:** Ignoring the store, storing only the old result, or forcing TOP when the finite expansion is available loses the mandated materialised domain; weakening the single-thread assumption is outside this repair.

**Conformance consequence:** DB/DN/DS: global1 atomicrmw xor2 gives least fixed point {1,3}, runtime width3/free clean/code0; successful/failed cmpxchg old/success aggregate and conditional store, native materialised LLVM18/23. Nonblocking to accepted 0.2.10, required for this clarification's own freeze.

**Dependency order:** I27 and accepted PT3/PT6 byte-image repairs; independent of ISA 0.9.

**Maintainer choice:** D21 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i-gwf"></a>
### I-gwf — ISA wording and certificate migration ledger

**Bead:** `b-dialect-spec-gwf`. **Group:** 0.2.11. **Decision:** D22. **Audit:** DLT §25.2 / extra open ISA-dependency bead.

**0.1 capability/history:** The audit identified ambiguous certificate/launch wording; it did not license dropping fixed-database verification or pointer-rich programs.

**0.2.10 delta:** DLT-25.2 still asks for ISA8 fault return status, args spelling, qreg transport/slicing, entropy code10, certificate metadata fields and fixed-region proof labels.

**ISA 0.9 provision:** E11/E12/E13/E16.8/E17.6 and K5/K6/K13 resolve most requests (ISA-3.3, ISA-4.7, ISA-4.9, ISA-12.3). ISA-12.2-P1.S3 still calls a strict subdomain evidence; dedicated build/table/deferred fields are not assumed. Existing producer.version/definedness metadata and a declared fixed-image domain retain every capability; no real ISA gap.

**Proposed normative resolution:**

> The certificate MUST bind the full invocation and explicit expected relation under ISA 0.9, retain build-record and resolved-table identities and deferred-measurement information in the existing documented metadata channel where no dedicated field exists, and label a fixed-region subdomain as evidence with its covered fraction. [deps: DLT-19.9, DLT-25.2, DLT-18.7, ISA-12.1-P7, ISA-12.2-P1, ISA-12.3-P2, ISA-12.3-P3]

**Rejected alternatives:** Inventing schema fields, returning normally from a faulted R call or labelling a fixed-database subdomain full-D proof misstates ISA 0.9. Evidence still supports the rung's declared-space test; no rung is removed.

**Conformance consequence:** DM/DD/DX: exact args bits/token tuples and budgets, wrong expected relation/invocation negative, fixed DB rows × all target/fault values with coverage label and zero fault; distinguish native-comparable/reference fault/layout-dependent/classifier-undefined outcomes.

**Dependency order:** I05/I06/I08/I14/I-bz6; D01 for schedule-bound claims. Track unresolved wording here, not a new duplicate ISA capability bead.

**Maintainer choice:** D22 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

## Part C — 0.3 item records

<a id="i02"></a>
### I02 — Effective ctrl and R budgets

**Bead:** `b-dialect-spec-8wf.2`. **Group:** 0.3. **Decision:** D18. **Audit:** 1.4-e, D18, B-43.

**0.1 capability/history:** 0.1 made ctrl/reversible budgets inert.

**0.2.10 delta:** DLT-9.3-P2, DLT-9.3-P3, DLT-10-P37 and DLT-17.6 already enforce generation/slice/R budgets; DLT-17.6-P2 and DLT-25.1-P4 still classify every R entry as BLK-5.

**ISA 0.9 provision:** K5/K6: ISA-4.1-P14, ISA-4.9-P13 and ISA-10 provide typed terminal faults and eligible failed-run reversal; they do not supply the dialect instruction counter.

**Proposed normative resolution:**

> R budget exhaustion MUST lower the existing pre-instruction counter check to fault 1, 2 or 3, preserve the preceding history and execute no later source effect. [deps: DLT-17.6-P1, DLT-17.6-P2, DLT-10-P37, ISA-4.1-P14, ISA-4.9-P13, ISA-10]

**Rejected alternatives:** An inert budget, interpreter host fuel, post-effect checks and generic trap substituted for fault C all change observable outcomes.

**Conformance consequence:** DE/DS: r-budget-prefix and n-rstep-return become executed ISA-0.9 success/fault/reverse cases; DT keeps full independent slice budgets and nested generation accounting.

**Dependency order:** I05, I33, I-bz6; I20 for device-computed fields.

**Maintainer choice:** D18 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i19"></a>
### I19 — Runtime register widths

**Bead:** `b-dialect-spec-8wf.19`. **Group:** 0.3. **Decision:** D15. **Audit:** B-07 / ISA-4.

**0.1 capability/history:** 0.1 rejected n not finitely enumerated; the capability is real dynamic allocation and handle widths, not only a build-time SQLite N.

**0.2.10 delta:** DLT-3.4, DLT-6.5-P14 and DLT-25.1-P2 still use BLK-1 for top classical n; DLT-10-P42 also blocks a Co width with top value set.

**ISA 0.9 provision:** K1: ISA-3.3-P7, ISA-3.3-P8, ISA-3.3-P10, ISA-3.3-P12, ISA-3.3-P19 supplies qreg[*], dynamic new/slice/width and fixed-transfer checks. It does not permit a quantum location as a classical allocation operand; Co allocation still needs unconditional padding.

**Proposed normative resolution:**

> Classical runtime widths MUST lower through qreg[*] with the existing n>=1 dialect check and checked transfers, and a coherent width MUST allocate unconditionally to a sound bound derived from materialised instructions or, absent a tighter bound, the full unsigned marker-width domain, with out-of-range wire operations predicated off. [deps: DLT-3.4, DLT-10-P42, DLT-18.3, ISA-3.3-P7, ISA-3.3-P8, ISA-3.3-P19, ISA-3.5]

Additional proposed width/shape sentences, confined to the 0.3 track:

> When an interface width or descriptor extent is not finitely enumerated by AV, the reference dispatch domain MUST include every valid representable shape allowed by the marker's unsigned i64 fields and the existing parameter-binding checks, rather than treating AV top as a runtime interface failure. [deps: DLT-3.2, DLT-8.1, DLT-8.2, DLT-8.4, ISA-3.3-P7, ISA-3.3-P19]

> Each such branch MUST retain the fixed-signature reference-object map and its exact fault and budget semantics, with width selection classical and with no inspection of coherent data to select a shape. [deps: DLT-8.4, DLT-16.2, DLT-9.4, ISA-3.1, ISA-3.3-P19, ISA-5.2]

Design consequence: the valid unsigned-i64 width/extent domain is finite even when the AV representation widens to top, so exhaustive static shape dispatch is a conservative construction, not a claim of efficient compilation. For a Co width, the padding bound is classical and fixed before entry; comparisons against the logical width remain coherent predicates. A more compact lowering is acceptable only with the same semantics; JIT object admission or a parametric region-signature extension is not assumed here. Invalid values and actual resource exhaustion retain the existing named outcomes. This replaces the obsolete top-width blocker case in 0.3; it does not silently transfer it to T-IFACE.

**Rejected alternatives:** Keeping the 4096-atom cap as a capability bound, substituting a user constant, or inspecting a superposed width classically are narrowings/errors. K1 does not by itself justify deleting the Co case without a construction.

**Conformance consequence:** DB/DS: launch- and measurement-derived n, zero/overflow/size mismatch before mutation, widths beyond finite analysis cap, dynamic slice/index; DT a small Co width padded to a known bound plus top-domain construction check. DO extends shape enumeration over valid representable widths/sizes without a catch-all T-IFACE for a valid shape.

**Dependency order:** I17, I33, I25; K1 publication/implementation in D01. The type-domain fallback can be extremely costly; staging is mechanics only.

**Maintainer choice:** D15 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i20"></a>
### I20 — Device-computed budgets

**Bead:** `b-dialect-spec-8wf.20`. **Group:** 0.3. **Decision:** D16. **Audit:** B-08 / ISA-1.

**0.1 capability/history:** 0.1 rejected runtime budgets; the accepted version supports static and launch-supplied fields but not arbitrary device computations.

**0.2.10 delta:** DLT-9.5-P2, DLT-9.5-P3 already mint/select host tokens; DLT-9.5-P4 and DLT-25.1-P3 still issue BLK-2 for device-derived fields.

**ISA 0.9 provision:** K3: ISA-4.1-P17, ISA-5.4-P3 and ISA-7.4-P13 mint validated run-scoped tokens, revoke them on reversal and bind schedule/args to exact tuples.

**Proposed normative resolution:**

> A device-computed classical budget tuple MUST be resolved with the existing field precedence and minted by budget.mint before region entry, without rounding or substituting any component. [deps: DLT-9.1-P7, DLT-9.2-P8, DLT-9.5-P4, DLT-9.5-P5, ISA-4.1-P17, ISA-5.4-P3, ISA-7.4-P13]

**Rejected alternatives:** Finite-token rounding changes F_B; minting inside a coherent region or using another invocation's schedule violates ISA binding.

**Conformance consequence:** DD/DM/DS: measured-64-bit budget witness becomes accept/executed; invalid tuple causes code4 before mutation, revocation/use-after-close negative, schedule B=3 not reused for B=2 and same tuple/different token ids hash equally.

**Dependency order:** I05/I33, I-bz6 for typed mint failures, D01; lproc token forwarding follows Q14 unchanged.

**Maintainer choice:** D16 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i25"></a>
### I25 — Handles stored through loaded/returned pointers

**Bead:** `b-dialect-spec-8wf.25`. **Group:** 0.3. **Decision:** D17. **Audit:** B-24.

**0.1 capability/history:** 0.1 excluded Vec/std::vector buffers whose pointers were loaded from collection headers or returned by functions.

**0.2.10 delta:** DLT-6.4-P1 already admits tracked slots through DLT-5.2; DLT-6.5-P10/25.1-P2 still block memory-reaching sites with infinite reference instance bounds.

**ISA 0.9 provision:** K1 supplies ISA-3.3-P13, ISA-3.3-P14 id/from_id plus width/state checks and ownership through CLOSED; K2 covers their use in R. This removes static-register-file naming as a capability limit.

**Proposed normative resolution:**

> Memory-reaching handles with no finite reference instance bound MUST use a persistent lossless tag-to-ledger-id mapping and qreg.from_id at use, preserving pointer-width tags, identity, liveness, ownership and checked widths. [deps: DLT-6.1-P1, DLT-6.4-P1, DLT-6.5-P10, ISA-3.3-P7, ISA-3.3-P13, ISA-3.3-P14, ISA-3.3-P19, ISA-10]

**Rejected alternatives:** Keeping the 64-slot fallback as a 0.3 limit or narrowing every tag to a truncated 64-bit launch id reintroduces bounds/aliasing; converting ids does not permit arithmetic on source handles.

**Conformance consequence:** DB/DS: grow Vec/list beyond 64 simultaneously live registers, loaded/returned buffer pointers, stale/viewed/foreign-run id negatives and pointer-width bridge; existing bounded/direct cases stay semantically equal.

**Dependency order:** I11/I22/I35, I19, I-cbe; shares one implementation/reference design with I29.

**Maintainer choice:** D17 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i29"></a>
### I29 — Handles across device entries

**Bead:** `b-dialect-spec-8wf.29`. **Group:** 0.3. **Decision:** D17. **Audit:** B-30.

**0.1 capability/history:** 0.1 forced release at each device-entry return, excluding REPL lexical lifetimes.

**0.2.10 delta:** DLT-6.6-P1 already uses QREG parameters/results and program-end leak checking; DLT-6.5-P7 still blocks persistent memory roots without finite bounds.

**ISA 0.9 provision:** K1: ISA-3.3-P14, ISA-3.3-P20, ISA-3.3-P21 and ISA-10 distinguish identity/liveness from exclusive open-run ownership; aliases are not independent registers.

**Proposed normative resolution:**

> QREG parameters and results MUST retain their register identity across entries and may outlive a device-entry return, with persistent lookup subject to the ISA run-ownership and CLOSED rules and leak checking at program end. [deps: DLT-6.5-P7, DLT-6.6-P1, ISA-3.3-P14, ISA-3.3-P20, ISA-3.3-P21, ISA-10]

**Rejected alternatives:** Entry-local release breaks lexical lifetime; simultaneous access by separate open runs or treating aliases as disjoint violates the ledger.

**Conformance consequence:** DB/DD/DS: repeated entries retaining more than 64 roots, parameter-to-global-to-later-entry, QREG return, ownership refusal while original run remains open, and valid reuse after close.

**Dependency order:** I25/I-cbe/I19; no new source marker signature.

**Maintainer choice:** D17 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i32"></a>
### I32 — Quantum markers inside R closures

**Bead:** `b-dialect-spec-8wf.32`. **Group:** 0.3. **Decision:** D18. **Audit:** B-38.

**0.1 capability/history:** 0.1 banned all markers in reversible closures, although only measurement is intrinsically disallowed for reversal.

**0.2.10 delta:** DLT-7.5 already supports gate/region calls on env handles; DLT-25.1-P5 still blocks unbounded R allocation and R entry-state registers (BLK-4).

**ISA 0.9 provision:** K2: ISA-3.3-P7, ISA-3.3-P18 and ISA-4.1-P15 allow qreg operations in R and reverse exact ledger frames; measurement stays CC-only.

**Proposed normative resolution:**

> R allocations, releases, slices and concatenations MUST use the ISA ledger-frame semantics, restoring original ids and alias states on reversal without a static hoisting-instance bound. [deps: DLT-7.5, DLT-25.1-P5, ISA-3.3-P7, ISA-3.3-P18, ISA-4.1-P15, ISA-7.4]

**Rejected alternatives:** A permanent hoisting cap narrows dynamic allocation; replacing reversed free with a fresh unrelated id breaks aliases; allowing R measurement breaks reverse eligibility.

**Conformance consequence:** DB/DE/DS: R allocate/use/free beyond finite bound, uncall/whole-run reverse through concat/slice and retained aliases, unverified-free refusal on non-verifying executor; measurement negative retained.

**Dependency order:** I19/I25 and I-bz6, K2/K6 implementation; unlocks I40 R snapshot.

**Maintainer choice:** D18 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i38"></a>
### I38 — Whole-program reversible mode

**Bead:** `b-dialect-spec-8wf.38`. **Group:** 0.3. **Decision:** D18. **Audit:** O-04.

**0.1 capability/history:** 0.1 had no marker-free entry route for unmodified programs.

**0.2.10 delta:** DLT-19.2 already synthesises a CC launch stub and R entry, argv/envp, exit status, device tape and reversal, but DLT-11.5-P2 applies BLK-5 to every R entry.

**ISA 0.9 provision:** ISA-10, ISA-7.3 and ISA-7.4 and K5/K6 cover whole-run completed/failed reversal with explicit eligibility; faulting R calls do not return a recoverable status to CC.

**Proposed normative resolution:**

> Whole-program R mode MUST retain the unmodified entry route and effect tape, and MUST report terminal faults and reverse eligible completed or failed runs according to ISA 0.9. [deps: DLT-19.2, DLT-14.7, DLT-18.6, ISA-4.9-P1, ISA-7.4, ISA-10]

**Rejected alternatives:** Adding source markers to musl/kernel main narrows unmodified execution; executing a CC successor after R failure contradicts K5.

**Conformance consequence:** DD/DE/DS: argv/env/status, puts tape forward/reverse/replay, failed run and open activation reversal; DX3/5/6 actual programs remain gates beyond the minis.

**Dependency order:** I-bz6, I13/I36/I37, I32 when program allocates registers; D01 implementation gate.

**Maintainer choice:** D18 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i40"></a>
### I40 — Runtime entry-state snapshots

**Bead:** `b-dialect-spec-8wf.40`. **Group:** 0.3. **Decision:** D19. **Audit:** O-07.

**0.1 capability/history:** 0.1 omitted transfer of caller-mutated globals/heap and allocator metadata into an oracle, including a post-boot snapshot.

**0.2.10 delta:** DLT-8.5 and DLT-16.2-P20 already specify replay with sizes/liveness/bump, including allocation-only closures; DLT-8.5-P7 still needs BLK-4 when R prepares the snapshot.

**ISA 0.9 provision:** ISA-7.1 and ISA-7.2 plus qreg concat and calls already realise replay/copy; K2 now permits preparation/release in R. G-12 overlay is absent but not needed for capability.

**Proposed normative resolution:**

> Runtime oracle entry state MUST retain caller bytes and allocator replay in native address order before any wrapper-private allocation, and R callers MUST use reversible register preparation and release for that same snapshot construction. [deps: DLT-8.5, DLT-16.2-P20, ISA-7.1, ISA-7.2, ISA-3.3-P18, ISA-7.4]

**Rejected alternatives:** Link-time images alone omit runtime state; resetting an allocation-only closure's allocator changes addresses; zeroing replayed inputs or silently requiring a small snapshot narrows the kernel path.

**Conformance consequence:** DO/DM/DD/DS: entry-replay-byte, entry-allocation-only and driver-snapshot-initializer; add R snapshot + reverse through metadata changes and stale cache invalidation on alloc/free/stack restore. DX7 compares the same runtime snapshot per basis input.

**Dependency order:** I33/I17/I32/I-bz6; fixed build snapshot remains a compatible path, G-12 is efficiency only.

**Maintainer choice:** D19 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

## Part C — ISA-blocked item records

No genuinely missing ISA 0.9 capability sentence was found for these items. The exact formerly missing sentences are cited below; neither a duplicate proposal bead nor an assertion of implemented semantics follows from draft acceptance. K64/K65 are the separate scheduling ratification gate in D01.

<a id="i-bz6"></a>
### I-bz6 — Typed R faults and reversible prefixes

**Bead:** `b-dialect-spec-bz6`. **Group:** ISA-blocked. **Decision:** D18. **Audit:** ISA-7 / BLK-5.

**0.1 capability/history:** 0.1 generic R traps could not promise an exact cause; every promised named fault and intact prefix is required, including budget boundaries.

**0.2.10 delta:** DLT-11.5-P1, DLT-11.5-P2, DLT-11.5-P3, DLT-17.6-P5 and DLT-25.1-P4 explicitly preserve the missing contract and classify R entries blocked on ISA 0.8.

**ISA 0.9 provision:** Exact required ISA sentence is already present in ISA-4.1-P14.S1: fault C records exact nonzero C (zero becomes4), ends FAILED, runs no successor and retains prefix history; ISA-4.9-P12, ISA-4.9-P13 and ISA-10 complete reporting/reversal. No new ISA proposal.

**Proposed normative resolution:**

> On the ISA 0.9 target, an R entry MUST report the exact effective fault cause through the launch result, preserve its entire logical prefix and stop without returning results or running its CC caller's successor. [deps: DLT-11.5-P3, DLT-17.6-P5, ISA-4.1-P14, ISA-4.9-P1, ISA-4.9-P12, ISA-4.9-P13, ISA-10]

**Rejected alternatives:** Generic trap, CC-only hostcall from R, or an artificial return-status recovery path changes the contract. Draft ISA wording is not executed evidence.

**Conformance consequence:** DE/DS blocker→accept on 0.9: r-fault-code (2), r-budget-prefix (1), implicit causes5/6/7, program-defined code above10, fault0→4, one record, zero later effect, reverse removes record and restores prefix/open activations. Keep old0.8 blocker vectors in their versioned corpus.

**Dependency order:** D01 ISA publication and independent interpreter support; then I02/I32/I38/I40. Status remains open.

**Maintainer choice:** D18 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

<a id="i-cbe"></a>
### I-cbe — Cross-entry root accumulation

**Bead:** `b-dialect-spec-cbe`. **Group:** ISA-blocked. **Decision:** D17. **Audit:** ISA-4 / ISA-12.

**0.1 capability/history:** The original entry-local model omitted an unbounded sequence of live host-retained QREG parameters/results, while the north star requires REPL lifetimes.

**0.2.10 delta:** DLT-6.5-P6, DLT-6.5-P7 and DLT-25.1-P2, DLT-25.1-P5 correctly use infinity and BLK-1/BLK-4 rather than claiming N=1; the bounded 64-slot fallback is not the promised general solution.

**ISA 0.9 provision:** Exact needed sentences already exist: ISA-3.3-P14.S1 gives live id lookup and run ownership; P7/P8 give runtime widths; P18 reverses R ledger operations and resurrects the same id. K1/K2 therefore cover the semantic dependency; no new ISA bead.

**Proposed normative resolution:**

> Persistent parameter and result roots MUST resolve through the program ledger across entry calls without an entry-count or static-file bound, while retaining the ISA's exclusive open-run ownership and same-id reversal rules. [deps: DLT-6.5-P6, DLT-6.5-P7, DLT-6.6, ISA-3.3-P7, ISA-3.3-P14, ISA-3.3-P18, ISA-10]

**Rejected alternatives:** Per-entry trip counts do not bound lifetime; applying a blanket 64-slot limit or reusing stale tags narrows/corrupts the accepted lifetime contract.

**Conformance consequence:** DB/DD/DS blocker→accept on 0.9: handle-cross-entry plus parameter/result/global variants beyond64, active ancestor setjmp, caller-guaranteed free, exact-root free and R reversal. Check held-open ownership error separately from valid sequential closed runs.

**Dependency order:** D01 K1/K2 implementation/publication, I19/I25/I29; I32 supplies R allocation. Status remains open.

**Maintainer choice:** D17 below applies to this item; the recommended resolution is the proposed sentence and retained construction above.

## Part D. Dependency order and conformance gates

The editing dependency graph, expressed as landing waves (items within a wave can share one implementation change; this is a design order, not delegation):

1. **D01 baseline/version ledger:** pin source digests and clause IDs, inventory every retained rule/example, distinguish0.8 and0.9 expectations; complete0.2.11 clarifications independently of ISA adoption.
2. **Analysis and shared identity foundation:** I11/I22/I27/I35 plus PT12 I-0y2; keep S2 as one fixpoint with candidate/provenance/value flows. I-0t9 is independent regression-only bookkeeping.
3. **Budget/interface foundation:** I33 then I05; I17/I06 and existing I40 replay; I07/I15/I37/I12/I36 map the complete closure in the accepted normalisation order.
4. **ISA 0.9 runtime foundation:** I-bz6 (typed terminal cause and reversal), I19 (classical widths and coherent padding), I20 (minting), I25/I29/I-cbe (persistent lookup/ownership), then I32 (R ledger allocations) and I40 (R snapshots). These are linked capabilities, not selectable scope cuts.
5. **Composition:** I01/I31 TDL with I02 budgets, I03/I14 in-place alternatives, I08 channels, I13 models; I38 whole-program R and I39 platform; remaining collection/attribute/driver rows reuse these foundations.
6. **Freeze and bead closure evidence:** full versioned spec/checker/corpus gates, actual rung programs and independent contracts; no automatic closure from outline ratification.

Proposed gate sentences:

- Each new or changed rule MUST have a positive checked example, each retained rejection a negative, and each genuine blocker its version-specific blocked example, with independent execution rather than producer self-comparison. [deps: DLT-1.5, DLT-21.3, DLT-21.4, ISA-15]
- An unimplemented required example MUST fail the gate without being skipped, deleted or reclassified to fit the checker. [deps: DLT-1.5, DLT-21.4]
- An ISA 0.9 capability formerly blocked on 0.8 MUST have executed state, fault and reversal evidence before its bead is closed, and a passing legacy blocked-verdict test MUST NOT stand in for that execution. [deps: DLT-1.6, DLT-18.7, DLT-25.1, ISA-15]
- Scheduled0.9 objects and realised-operation claims MUST use the final ratified support/cleanup ordinal rules and bound reference expansion library before being reported conformant. [deps: ISA-11, ISA-11.1, ISA-12.1, ISA-12.3]

Baseline receipt is **2767/2767**,84 checker units and7 legacy tests at0.2.10 from its PROGRESS. This outline does not re-run or claim a0.9 freeze. The new table adds obligations; it does not lower baseline expectations or imply all listed new cases already exist. DA–DX/DL are the existing suite names in DLT-21.3; row names above identify concrete existing vectors or explicitly described new cases. Changes to checker code, examples, manifests and accepted files belong to the later draft/implementation job after rulings.

## Part E. Demo-ladder scope check

| NS rung | Retained full programme | Critical item records | Acceptance consequence |
|---|---|---|---|
| 1 | C/Rust/Julia scalar functions, including remaining calls and multi-argument functions | I06/I07/I12/I17/I35 | Exhaustive Int8 full declared D; both executors and materialised native comparison, zero fault |
| 2 | Pointer/struct/byte-memory hashtable | I07/I11/I17/I33/I40 | Native result, byte-exact reversal, heap/stack/depth boundaries |
| 3 | Unmodified musl hello-world | I13/I15/I36/I37/I38/I-bz6 | Console equal to native, un-run to reset, deterministic tape replay |
| 4 | **Grover over unmodified SQLite, core deliverable** | I05/I06/I07/I13/I15/I17/I22/I33/I35/I37 | Real SQL rowid query over fixed database in quantum-addressed VFS; all rows/all targets atN<=2^10, zero fault; Grover branch enumerationN<=2^8; estimateN=2^20 with budget/padded cost and named target |
| 5 | Julia push!/Dict on shim runtime | I11/I12/I16/I35/I38/I39 | Allocation-driven behaviour, native agreement and exact reversal; no compiler special cases for containers |
| 6 | xv6 then Linux tinyconfig | I13/I32/I35/I36/I37/I38/I39 | Same-image QEMU output, un-boot to reset vector, byte-identical tape; full platform inventory remains required mechanics |
| 7 | Kernel as oracle on syscall arguments and a post-boot snapshot | I07/I13/I17/I33/I39/I40 | Same snapshot native comparison per basis input; definedness/classifier reporting; amplification and named-target estimate |
| 8 | Plain-C Monte Carlo amplitude estimation | I05/I06/I07/I13/I15/I17/I33 | Entropy as superposed input; deterministic FP/libm; oracle/simulation/estimate gates |

Every rung remains in scope at full programme scale. Minis are diagnostics for mechanisms; the §8 end-to-end programmes remain the conformance repository's consumer gates under NS§6.1. The runtime libraries, VM, specialiser and estimator remain separately replaceable implementations of published contracts; the outline proposes no shared code across a boundary. A huge conservative width construction or slow replay is an efficiency concern, not authority to reject promised programs.

## Part F. Numbered maintainer decisions

The following are proposed questions, not rulings. Each item record names exactly one decision; D01 additionally gates every0.9 adoption. Recommendations retain all capabilities even if mechanics are staged.

**D01. Approve separate compatible 0.2.11/ISA 0.8 and capability 0.3/ISA 0.9 tracks, with publication and execution gates rather than immediate retargeting?**

Recommendation: Yes. Preserve accepted bytes; gate 0.3 on published ISA 0.9, muse disposition, maintainer K64/K65 ratification, published reference-library binding and independent ISA 0.9 execution. K64/K65 define non-row support and whole-cleanup ordinals (ISA-11-P10, ISA-11-P11), relevant to all scheduled/certificate realisations, not new LLVM capability exclusions.

**D02. Retain the staged per-region table and all four budget units, with no new table ABI?**

Recommendation: Yes; I05/I33 retain canonical identity selection, counters and sstack accounting.

**D03. Retain the version2 descriptor with independent ARG/IN/MEM_IN/OUT bindings and existing common-delivery scheme?**

Recommendation: Yes; I06/I17, including zero-output execution and 2k-1 wide delivery.

**D04. Retain the full lifted closure and all seven own-format FP implementations?**

Recommendation: Yes; I07/I15 keep the complete generic-intrinsic inventory, vector/limb order and native-materialised differential contract.

**D05. Retain the four per-tier device models and libc/VFS shims as ordinary bitcode?**

Recommendation: Yes; I13, with R terminal faults updated by D18 and no silent host execution in R/L.

**D06. Retain polyvariant clones, one A(F), shared globals and bounded-program compare-tree dispatch?**

Recommendation: Yes; I22/I35/I23/I30. No new indirect-call ISA opcode is required.

**D07. Retain the exact field/interval-sensitive reference analysis and general allocator/call-return propagation?**

Recommendation: Yes; I11/I24/I26/I27/I28, with no reliance on discarded range metadata or declared array size as an index bound.

**D08. Retain Cl/M/Co TDL and direct-body handling of reversible markers during action generation?**

Recommendation: Yes; I01/I31, including clean control workspace and accepted overwrite/inverse obligations.

**D09. Retain requested deferred measurement and the accepted benign-attribute lists?**

Recommendation: Yes; I08/I21, with channel-boundary and LLVM-legality evidence kept distinct.

**D10. Retain runtime op/class dispatch over the complete valid tables?**

Recommendation: Yes; I04/I18. Out-of-table cases retain their existing precise diagnostics.

**D11. Retain clean fallback for CC-spanning borrowing and allocation-generation handle equality?**

Recommendation: Yes; I09/I10. Direct dirty borrowing outside actions remains optional efficiency, not an extra blocker.

**D12. Retain EH/sjlj/fibers, target asm classification, varargs and the complete riscv64 platform?**

Recommendation: Yes; I12/I36/I37/I39. Continue platform inventory and actual boot/oracle gates; no unsupported-subset shortcut.

**D13. Retain tested mixed-major linkage and closed-unit mode with whole-program fallback?**

Recommendation: Yes; I16/I34. Actual link execution remains required evidence.

**D14. Choose native K4 only for covering exhaustive/library claims, while retaining CC expansion for the existing sampled/assumed inverse path?**

Recommendation: Choose that dual construction; I03/I14. Do not reinterpret sampled evidence or T-CLEAN as a native K4 proof.

**D15. Adopt dynamic classical qreg widths and coherent padding to a sound materialised/type-domain bound?**

Recommendation: Yes; I19. Keep n>=1 and transfer checks. Full unsigned i64-domain padding is the conservative fallback when AV top supplies no smaller bound; cost can be enormous but the analysis cap is not a scope cap.

**D16. Adopt exact device budget.mint with tuple-bound schedules and reversible token validity?**

Recommendation: Yes; I20. Preserve existing host/static paths and forbid tuple rounding.

**D17. Adopt persistent lossless tag-to-ledger-id lookup across entries, with exclusive run ownership?**

Recommendation: Yes; I25/I29/I-cbe. Keep pointer-width tags and an explicit bijection/bridge rather than assuming every pointer can store an ISA64 id; remove static-file bounds only on the0.9 target.

**D18. Adopt K2/K5/K6 R ledger operations, typed terminal faults and eligible failed-run reversal?**

Recommendation: Yes; I02/I32/I38/I-bz6. R faults terminate the whole run, not return status to a continuing CC caller; budget enforcement stays dialect instrumentation.

**D19. Retain runtime entry replay and extend its snapshot preparation/release to R using K2?**

Recommendation: Yes; I40. No overlay primitive or build-time-only restriction; charge replay and preserve allocator identity.

**D20. Treat 0t9 as an already-applied example correction, pending regression evidence rather than another spec change?**

Recommendation: Yes; I-0t9. Keep candidates=classical in the inherited example and test first-operand order.

**D21. Clarify PT12 using the complete virtual N9 value transfer in the compatible track?**

Recommendation: Yes; I-0y2. Execute xor and both cmpxchg paths; preserve its nonblocking status relative to accepted 0.2.10.

**D22. Adopt ISA 0.9 invocation/claim binding while retaining metadata fallbacks and honest fixed-region evidence labels?**

Recommendation: Yes; I-gwf. No schema invention and no claim of full-D proof for a strict fixed-image subdomain; rung4 verification remains complete on its declared fixed-database space.

## ISA proposal disposition

**New ISA beads filed: none.** K1/K2/K3/K5/K6 contain the actual missing0.8 capability sentences. K4 is optional and does not replace the sampled CC construction. G-12/13/14/15/16, direct CC dirty borrowing and native indirect calls retain explicit constructions; they are efficiency work, not newly discovered ISA blockers. Exact sentences formerly needed for bz6/cbe are cited in those records. Fixed-region proof labelling and dedicated certificate metadata fields remain wording/schema questions in the already-open gwf bead, with capability-preserving metadata/evidence defaults. K64/K65 need ratification, not duplicate proposal beads.

## Maintainer rulings

Rulings of 2026-10-31 (maintainer, relayed by the orchestrator; recorded verbatim):

- D01-D13: **yes**, as one block (rule 10: each is a repair of a 0.1 narrowing found by the audit).
- D14: **both paths** (native K4 for covering exhaustive/library claims; the sampled CC-expansion path
  retained for the existing inverse claims).
- D15: **yes, with the caution** that the coherent padding bound uses the conservative finite-domain
  construction named in the outline; an unsound padding bound is the §6.2 class of defect and is not
  acceptable as a default.
- D16-D19: **yes**, in the 0.3 track (ISA 0.9 K1-K6 dependencies; gated on 0.9 publication and execution).
- D20-D22: **yes**. D22 wording must match ISA 0.9 K74 (checker-owned labels; producer label is a checked
  request).

Consequences: draft 0.2.11 (compatible track, ISA 0.8) is to be written from this outline now; draft 0.3
follows once ISA 0.9 is published. Every new or changed normative sentence carries `[deps: ...]`
(CLAUDE.md rule 12).
