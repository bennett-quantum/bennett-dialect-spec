## Draft 0.2.11 pre-flight freeze receipt — 2026-10-31

**2834/2834 passed; 0 failed; 0 blocked/unavailable. Baseline 2767 → 2834.**
Draft `0.2.11` (`dialect-0.2.11;isa-0.8`); ISA grading target **0.8**;
status **not yet graded**. This freezes the checked snapshot, **not full closure
of every outline conformance consequence**: 33 original compatible item beads
remain open; continuation **b-dialect-spec-oxs** records the remaining evidence.
All 35 ruled item resolutions are drafted; counts and rejected alternatives
are in the per-item table below. 41 per-item normative sentences/markers,
12 version/process markers; **53 deps markers / 243 resolving references**.

Code/spec/checker snapshot: `5f503e5c6c71c843fa59a495709c7098ce366bcb`.
Spec SHA-256: `67157631837887fabb412b762d571157f71dbb79bb9ff13331ec692ce7ad82ba`.
Checker/harness/source manifest SHA-256:
`79bf42b89773c655be793b2144a85abf95203af1a5cfec09ee67d7b07b687d66` (**115 files**).
The manifest matched before/after final validation, after the code commit and
at receipt writing. All **497 accepted tagged blocks** remain byte-identical
with their original multiplicities; every added gate row is green.

Independent interpreter final snapshot: `ad84e75e10ecbfc582d7fdc50f821ac2a618c1a0`;
immutable source fingerprint `9857b0ed68e1377b3ca4ff4c8c20158df9e4eaca246c7a61d6d26e090838268f`.
The gate also used the already-captured c0df4cc snapshot (fingerprint
`b1e88233b05683eee89dcb3aff35206f1620e729ef1456cf34cd2893cb80714f`).
Both immutable source copies were verified at receipt writing; the final ISA
checkout HEAD/files matched the final captured snapshot. The interpreter's
parallel council-response commit did not alter this draft's grading target.
No ISA source was edited by this job.

Machine receipt: **scripts/dialect_check.LAST-RUN.json**. Complete rows:
**scripts/.tmp/0211-freeze.json**. **92 checker units and 7 legacy runtime tests
pass** headless. No viewer pass, push, header edit, or outside-owned-path source
edit. SPEC_VERSIONS.toml remains the accepted-release registry outside ownership.

Completed original beads: **0t9**, **0y2**. Completed discovered checker repair:
**nzf**. Every other compatible item received a section/evidence/rejected-
alternative comment and remains open for its wider outline evidence; gwf's
ISA0.9 invocation-binding migration remains cross-reference-only. No duplicate
ISA gap was filed; bz6/cbe retain their existing 0.3 adoption gates.

| Family | Passed | Failed | Blocked |
|---|---:|---:|---:|
| asm | 1 | 0 | 0 |
| blocker | 19 | 0 | 0 |
| cc-run | 8 | 0 | 0 |
| check | 22 | 0 | 0 |
| coverage | 161 | 0 | 0 |
| driver | 2 | 0 | 0 |
| events | 3 | 0 | 0 |
| frontend | 21 | 0 | 0 |
| hash | 9 | 0 | 0 |
| header | 1 | 0 | 0 |
| map | 21 | 0 | 0 |
| native | 31 | 0 | 0 |
| normalise | 46 | 0 | 0 |
| parse | 809 | 0 | 0 |
| recognise | 155 | 0 | 0 |
| run-oracle | 22 | 0 | 0 |
| run-program | 5 | 0 | 0 |
| seeds | 1 | 0 | 0 |
| state | 82 | 0 | 0 |
| step-check | 6 | 0 | 0 |
| tdl | 10 | 0 | 0 |
| trace | 3 | 0 | 0 |
| xrefs | 1396 | 0 | 0 |
| **Total** | **2834** | **0** | **0** |

Exact final gate:

```sh
env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER TMPDIR=/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp python3 scripts/dialect_check_v02.py --json scripts/.tmp/0211-freeze.json
```

Green implementation commits: `338c778` (PT12/first operand), `bdd6eb1`
(ruled confirmations/collection/call-return/N21), `5f503e5` (typed atomic parser).
The separate receipt commit follows; nothing was pushed.

## Draft 0.2.11 implementation — 2026-10-31

Owner: implementation sub-agent, sole specification editor; parent owns the session worklog.
Scope: ruled compatible track, ISA grading target 0.8. The outline index contains
32 epic children plus 0t9/0y2/gwf = 35 compatible records (the request's “33 plus
three” count does not match that index). No outline, docs, worklog, HANDOFF,
CLAUDE, sibling or marker-header edits. No push. SPEC_VERSIONS.toml is outside
owned paths and continues to identify accepted 0.2.10; this working draft's
header, full version, plugin identity and module-flag check are 0.2.11.

Accepted baseline reproduced headless: **2767/2767**, 0 failed/unavailable,
`scripts/.tmp/0211-baseline.json`. Accepted spec SHA-256 verified before editing:
`d4f3c1a88391cc147f8c8fa4f80f82852e3ebe6f880610fc16cd5151f33d7206`.
The accepted text is superseded in git, never rewritten as an accepted release.

### Foundation group: I-0y2 and I-0t9

| Bead | Section | Normative sentences added/changed | deps markers | Witness rows | Disposition |
|---|---|---:|---:|---|---|
| b-dialect-spec-0y2 | 5.2 PT12 | 1 | 1 | pt12-xor; pt12-cmpxchg-success; pt12-cmpxchg-failure (parse/recognise/state) | complete; 2782/2782 full gate green; bead closed |
| b-dialect-spec-0t9 | 1.5, 7.7 | 1 | 1 | region-reversible-in-action; region-reversible-in-action-top-first (parse/recognise) | complete; ordering companion and full gate green; bead closed |

PT12 hand derivation: 1 xor 2 = 3, 3 xor 2 = 1, giving least fixed-point
{1,3}; a single run has old=1, width=3. Successful cmpxchg(1,3) has initial
old=1/success=1/width=3 and abstract old/width={1,3}, success={0,1}; failed
cmpxchg(9,3) has old=1/success=0/width=1, with no false store of 3.
All three native materialised witnesses execute on LLVM18/23 at O0/O3 with two
X gates, one clean free, live_after=0 and code0. Python supplies expected domains
and outputs only; clang-built binaries supply the observed execution.

Red→green: the three atomic-domain tests failed 10 subtests before the repair
(`scripts/.tmp/0211-pt12-red.txt`); four tests now pass, including eight integer
update variants, both cmpxchg outcomes and the first-operand ordering test.
The ordering companion is absent from the accepted snapshot and its regression
fails there (`scripts/.tmp/0211-0t9-red.txt`); both orderings pass in this draft,
and a deliberately wrong candidates assertion is rejected by the checker.
Selected development gate: 231/231 recognise/state, 0 failures.
Full foundation gate: **2782/2782**, 0 failed/unavailable,
`scripts/.tmp/0211-foundation.json`; **88 checker units pass**.

Rejected for 0y2: ignored stores, storing only the old result, and forcing TOP
where the finite N9 update is available; the single-thread assumption stays.
Rejected for 0t9: redefining candidates as a chosen entry or applying the already
accepted classical correction a second time. PT12's finite integer products use
K on distinct results; FP uncertainty retains non-handle TOP and ROOT provenance.
The fail-loud fixpoint ceiling now allows K+1 atomic recurrence iterations.

### PT12 spelling hardening — 2026-10-31

A final boundary probe exposed a remaining PT12 parser bug: with explicit
`ptr addrspace(1)` the address string included the type suffix and lost its
tracked object, so neither xor nor cmpxchg added 3 to the memory domain.
Both subtests failed (`scripts/.tmp/0211-atomic-spelling-red.txt`). The shared
N9 grammar parser now separates pointer type/value, strips weak/volatile and
ordering/syncscope syntax, preserves alignment and emits the original typed
pointer in virtual/materialised loads and stores. Pointer-valued atomic
storage widths use P(a). No semantic exclusion or new ISA requirement.

New checked rows `pt12-xor-as1` and `pt12-cmpxchg-as1` exercise the spelling
end to end: LLVM18/23 verify and native materialised O0/O3 give the same
old/success/width/clean-free/code tuples as their unqualified companions.
0y2 was reopened during this hardening and closed again after the final
**2834/2834** green gate (`scripts/.tmp/0211-freeze.json`), 92 checker tests
and 7 legacy runtime tests. The 115-file source manifest stayed unchanged.
No additional normative sentence is introduced: the PT12 clarification applies
to all admitted LLVM atomic spellings already. The full manifest now binds
five PT12 native states, not only the original three.

### Confirmations group validation — 2026-10-31

**2824/2824 gate rows passed**, 0 failed/unavailable;
`scripts/.tmp/0211-final.json` (pre-parser-hardening group).
**91 checker units and 7 legacy runtime tests pass.** All 497 accepted tagged
blocks remain byte-identical, including multiplicity. The tracked source manifest
matched before/after the gate. Spec SHA-256 at this group:
`3e7dcb4f99b8d95292ed5a1a58dabc3ddc54c6cd630e2db737cbaaff5d4436f3`.
The discarded `0211-clarifications.json`/unit run failed on interpreter HEAD
movement; those are development evidence, not freeze receipts. A fresh rerun
passed. No independent ISA source was edited. The found nzf checker defects
are resolved; all 33 remaining outline beads received section/evidence and
rejected-alternative comments, with broader evidence closure left open.

### Ruled confirmations group — draft text and evidence ledger

All 35 compatible item resolutions now appear in their affected sections.
I03 also updates two counterpart/effect table cells; I14 qualifies four
existing native-specialisation sentences so they do not contradict the
sampled CC path. There are 41 per-item normative sentences/markers, plus
12 version/process markers: 53 total, 243 dependency references, all resolving
in the supplied graphs. Unchanged PT/N/TDL/map/diagnostic rows retain
accepted semantics; PT12 is the one changed reference-analysis row. Native K4,
D15–D19 and new 0.9 objects/tokens/R faults are not adopted. I-gwf uses existing
metadata and checker-owned evidence labels; its full-invocation/expected-relation
0.9 migration remains cross-reference-only and the bead stays open.

Red→green for the **document** ledger: 33 missing-sentence subtests failed
before insertion (`scripts/.tmp/0211-clarifications-red.txt`), then all 35
sentence/placement/dependency checks passed. This is textual closure evidence,
not a claim that 33 new runtime mechanisms were implemented. The full gate
adds one coverage row per item requiring the listed retained execution rows to
have passed; a separate S0 row checks every accepted tagged block's hash and
multiplicity. No accepted example was removed or weakened.

The new compatible-allocator-graph is a separate behavioural witness for
I11/I22/I23/I24/I26/I27/I28/I35. It combines a custom attributed site, a defined
allocator wrapper, a returned two-level heap object, a shared global plus
adjacent integer counter, two callback candidates with different ROOTs and a
narrow i1 handle lane. Source/materialised native18/23 O0/O3 give identical
[9,2,4,2,0,0] for both inputs: count, allocations, X gates, clean frees, live,
code. Analysis checks all three ROOT sets and absence of counter/zero taint.
This found b-dialect-spec-nzf: false BLK-1 at a nested visible-callee return,
then invalid `ptr 0` from N21. The red commands failed respectively admission
and LLVM verification before the fixes. Call-return summaries now distinguish
a nested device return from host-entry return; root-killing frees still stop
liveness, including frees in callees. N21 emits typed null/FP/integer zeros.
These repair the checker against accepted rules; no canonical-map or norm
algorithm/version change, new ISA capability, or header change is required.

| Item / bead suffix | Section | Sentences | deps markers | Gate witness references | Disposition |
|---|---|---:|---:|---|---|
| I01 / 8wf.1 | 10 | 1 | 1 | state/tdl-a; state/tdl-b; state/tdl-d; state/co-loop-identity; state/co-loop-adj-overwritten; state/co-observe-write-observe | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I03 / 8wf.3 | 7.1, 8.7, 18.3 | 3 | 3 | state/inplace-param-quantum; recognise/inplace-arg-finite | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I04 / 8wf.4 | 3.4 | 1 | 1 | recognise/operand-class; recognise/operand-code-table | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I05 / 8wf.5 | 9.2 | 1 | 1 | state/budget-stage; recognise/budget-stage-runtime | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I06 / 8wf.6 | 8.4 | 1 | 1 | recognise/oracle-two-shapes; run-oracle/entry-replay-byte | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I07 / 8wf.7 | 16.1 | 1 | 1 | native/n-wideint; native/n-vector; native/fp-aggregate; run-oracle/listsum | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I08 / 8wf.8 | 7.5 | 1 | 1 | state/deferred-channel-adj-place; state/deferred-channel-adj; state/deferred-channel; recognise/region-measure-in-ctrl | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I09 / 8wf.9 | 18.3 | 1 | 1 | header/markers-c/markers-ir | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I10 / 8wf.10 | 6.3 | 1 | 1 | state/handle-stale-generation; recognise/handle-null-check; recognise/handle-eq | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I11 / 8wf.11 | 5.1 | 1 | 1 | recognise/handle-object-tracked; recognise/pt12-root-return; recognise/compatible-allocator-graph; state/compatible-allocator-graph | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I12 / 8wf.12 | 14.4 | 1 | 1 | native/n-eh; recognise/validator-v15-residue | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I13 / 8wf.13 | 11.3 | 1 | 1 | run-oracle/binding-block-byte; run-oracle/binding-clock-read; run-oracle/binding-console-byte; run-oracle/rung8-mini | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I14 / 8wf.14 | 8.7 | 5 | 5 | state/inplace-bound; recognise/inplace-wrong-inverse | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I15 / 8wf.15 | 13.5 | 1 | 1 | state/fp-sign-carrier; state/fcmp-abi; state/n-libm-x86-f128; state/n-libm-x86-ppcf128; native/n-vector | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I16 / 8wf.16 | 19.8 | 1 | 1 | state/driver-mixed-majors | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I17 / 8wf.17 | 8.6 | 1 | 1 | state/wide-delivery; state/oracle-empty-output; run-oracle/binding-out-byte; recognise/oracle-two-in | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I18 / 8wf.18 | 3.4 | 1 | 1 | recognise/operand-runtime-op; recognise/operand-class; recognise/operand-bad-code | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I21 / 8wf.21 | 3.6 | 1 | 1 | recognise/attr-strictfp-cold; recognise/attr-memory-none; recognise/attr-callsite-read | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I22 / 8wf.22 | 4.4 | 1 | 1 | state/driver-comparison-layout; recognise/indirect-table; recognise/compatible-allocator-graph; state/compatible-allocator-graph | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I23 / 8wf.23 | 6.4 | 1 | 1 | recognise/handle-indirect; recognise/handle-to-external; recognise/compatible-allocator-graph; state/compatible-allocator-graph | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I24 / 8wf.24 | 6.2 | 1 | 1 | recognise/handle-dynamic-lane; state/pt10-lane-zero; state/pt3-pack257; state/pt3-unpack; recognise/compatible-allocator-graph; state/compatible-allocator-graph | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I26 / 8wf.26 | 6.4 | 1 | 1 | recognise/handle-object-tracked; recognise/handle-store-host; recognise/compatible-allocator-graph; state/compatible-allocator-graph | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I27 / 8wf.27 | 5.2 | 1 | 1 | recognise/pt-variable-index; state/pt2-wrap; state/pt5-range-load; recognise/compatible-allocator-graph; state/compatible-allocator-graph | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I28 / 8wf.28 | 6.4 | 1 | 1 | recognise/handle-object-tracked; recognise/handle-store-host; recognise/compatible-allocator-graph; state/compatible-allocator-graph | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I30 / 8wf.30 | 7.2 | 1 | 1 | recognise/region-stack-slot; recognise/region-switch-table; recognise/region-host-param; recognise/region-mixed-types | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I31 / 8wf.31 | 7.4 | 1 | 1 | recognise/region-reversible-in-action; recognise/region-reversible-in-action-top-first; state/nested-cl-view | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I33 / 8wf.33 | 9.4 | 1 | 1 | state/shadow-stack-liveness; state/entry-allocation-only; run-oracle/listsum; state/budget-stage | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I34 / 8wf.34 | 19.7 | 1 | 1 | state/driver-closed-unit-fallback | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I35 / 8wf.35 | 14.2 | 1 | 1 | recognise/indirect-table; recognise/indirect-host-pointer; recognise/handle-indirect; recognise/compatible-allocator-graph; state/compatible-allocator-graph | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I36 / 8wf.36 | 15.2 | 1 | 1 | normalise/n-asm; recognise/asm-musl-syscall; asm/asm-0.2 | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I37 / 8wf.37 | 14.3 | 1 | 1 | native/n-varargs | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I39 / 8wf.39 | 20.6 | 1 | 1 | state/platform-uart-write; state/sv39-kernel-alias; run-program/fiber-pingpong; run-program/sjlj-two-frames | draft clarification implemented; evidence as listed; full outline closure not inferred |
| I-0t9 / 0t9 | 1.5 | 1 | 1 | recognise/region-reversible-in-action; recognise/region-reversible-in-action-top-first | complete; closed |
| I-0y2 / 0y2 | 5.2 | 1 | 1 | state/pt12-xor; state/pt12-cmpxchg-success; state/pt12-cmpxchg-failure; state/pt12-xor-as1; state/pt12-cmpxchg-as1 | complete; closed |
| I-gwf / gwf | 25.2 | 1 | 1 | state/budget-stage; step-check/rung4-mini | draft clarification implemented; evidence as listed; full outline closure not inferred |

Rejected alternatives by item (from the ruled outline; none adopted):

- **I01**: Generation-only execution changes the controlled store result; retaining incidental garbage as undeclared outputs violates the accepted cleanup contract.
- **I03**: Reinstating BLK-3 is false; replacing every pair with native qinplace would exclude the sampled path described in I14.
- **I04**: Accepting only class zero or merging classes without names loses the requested resource class.
- **I05**: Iterating the final hash back into lookup creates cycles; steps-only records or source edits would restore the narrowing.
- **I06**: Packing all inputs or constant-specialising every runtime argument imposes source/ABI restrictions the accepted descriptor removed.
- **I07**: A scalar-only profile, silently trapping an unsupported generic intrinsic, or limiting the contract to checker seeds narrows scope.
- **I08**: Measuring immediately changes the controlled instrument; uncopying retained channel records silently turns the channel into a unitary.
- **I09**: Reinstating T-BORROW drops capability; treating arbitrary dirty state as clean without restoration is unsound.
- **I10**: Physical-slot equality or id truncation aliases generations; banning null checks again breaks unmodified language idioms.
- **I11**: A new whitelist of wrapper names or TOP for every non-libc return reinstates the same restriction; inventing freshness for opaque external code is unsound.
- **I12**: Rejecting all unwinding or replacing an in-region catch with fault 4 changes defined program behaviour.
- **I13**: F(8) for a modelled VFS/entropy call narrows SQLite/Monte Carlo; native host calls from R/L violate effect closure.
- **I14**: Library-only admission narrows scope; claiming a sampled maximum is B_min or using a sampled claim as K4 authority is unsound.
- **I15**: Silent widening through f64/native long double, deleting retained fneg/transport, or faulting uncovered checker formats would narrow the accepted contract.
- **I16**: One-major-only linkage or promising arbitrary newer bitcode beyond the tested reader both contradict the envelope contract.
- **I17**: Source packing wrappers, return-only results, the superseded k+2 scheme or deleting the zero-output call change the admitted interface or fault outcome.
- **I18**: BD-E-OPERAND-UNBOUNDED for a finite-table selector reinstates the narrowing; remapping an invalid code silently is incorrect.
- **I21**: Reverting to the spike-only whitelist narrows build flags; declaring all attributes benign permits elimination/speculation.
- **I22**: Duplicating globals changes state; replacing stored addresses by clone addresses breaks comparisons/VFS tables; restoring BD-E-DEVICE-ADDRESS narrows libraries.
- **I23**: Blanket address-taken/indirect escape rejects visible device code; allowing an opaque host callee to consume handles violates containment.
- **I24**: Constant-lane-only acceptance narrows collections; merging packed scalar integers as lane values or dropping ROOTs is unsound.
- **I26**: Object-level escape bans prohibit lists/trees; ignoring an actual unknown reader discards the north-star containment rule.
- **I27**: Field-insensitive TOP restores the false rejection; assuming array bounds or using mathematical instead of modular GEP loses reachable slots.
- **I28**: A name-based host-reference ban confuses unrelated fields; letting host native code dereference or perform arithmetic on handles violates provenance.
- **I30**: Rejecting every imprecise candidate set or any over-approximated ill-formed candidate narrows correct executions; selected invalid/no-match candidates keep the accepted runtime faults.
- **I31**: Creating an actual R call from a coherent event list would evade predication; reintroducing region-tier rejection loses inferred lifting.
- **I33**: Memoryless tuples for a memory-using body, treating stack cells as bytes or omitting replay/helper cost changes the fault set.
- **I34**: Rejecting a nonclosed unit rather than falling back narrows the fast path contract; running before final link without closedness can miss context.
- **I35**: Requiring devirtualisation or rewriting SQLite narrows scope; qjumpr is intra-function and cannot substitute for a call.
- **I36**: Blanket asm rejection removes musl/kernel paths; treating a syscall as a no-op silently changes effects; patterns do not constitute a completed platform inventory.
- **I37**: Fixed-arity-only acceptance or relying on host register-save contents excludes printf/sqlite3_mprintf and misreads front-end va_arg expansion.
- **I39**: Rejecting setjmp or turning volatile MMIO into an ordinary memfault drops platform scope; restricting translation to user mode breaks supervisor virtual memory.
- **I-0t9**: Silently redefining candidates to mean a chosen entry would break existing examples; editing accepted bytes to reapply an already-present fix is unnecessary.
- **I-0y2**: Ignoring the store, storing only the old result, or forcing TOP when the finite expansion is available loses the mandated materialised domain; weakening the single-thread assumption is outside this repair.
- **I-gwf**: Inventing schema fields, returning normally from a faulted R call or labelling a fixed-database subdomain full-D proof misstates ISA 0.9. Evidence still supports the rung's declared-space test; no rung is removed.

Continuation bead: **b-dialect-spec-oxs** (open), referencing the 33 original
item beads rather than duplicating their mechanisms.

Additional outline evidence still requires work; these rows remain obligations,
not skipped/deleted/reclassified checked examples. The current retained/new
mini witnesses are not claimed to be the actual §8 end-to-end programs.
In particular: exhaustive class/table loader and runtime selector sweeps;
wrong-invocation/params-hash certificate replay; above-threshold sampled-pair
admission (the current simple-pair recogniser still fails unimplemented there);
entangled dirty-frame evidence; the full benign-attribute dynamic matrix;
Windows funclets; all-ABI va_copy/spills/callback formatting; block-overlay
write/read/reversal and entropy-exhaustion composition; platform poll/trap,
full Sv39/exec inventory, and actual boot/unboot/rung execution. Exact per-item
coverage remains the outline's Conformance consequence paragraphs; the table
above names only evidence actually checked here. Related epic children remain
open with completion comments for the draft portion, rather than being closed
on mini evidence. The two narrow foundation beads are complete and closed.
No new ISA gap found. Existing bz6/cbe and gwf retain their versioned adoption
gates; no duplicate ISA capability issue is justified by compatible drafting.

## Round-8 final freeze — 0.2.10 — 2026-10-30

**2767/2767 passed; 0 failed; 0 blocked/unavailable. Baseline 2732 → 2767.**
Full compatibility `0.2.10` (`dialect-0.2.10;isa-0.8`); ISA grading target 0.8.
Code/spec/checker snapshot: `023f5a771a814270634db3be9cfde88ded69f975`.
Spec SHA-256: `d4f3c1a88391cc147f8c8fa4f80f82852e3ebe6f880610fc16cd5151f33d7206`.
Checker/harness/source manifest SHA-256: `74372f9f2a7077e5eba1063ed687115e4ed0854b9732abb061b236b69efe16ff` (105 files).
Independent interpreter: `697c9a8d64690f0f467a8677a445f4db283a73fc`; immutable source fingerprint
`ddc1a303cd52bd828744e7aa4f85b17127a2869d6ad59da39934f7a6e5bf6c3e`.
The normative/checker/harness/corpus file manifest matched before and after the
final freeze and at receipt writing. Interpreter HEAD and source files matched
the immutable executed snapshot at receipt writing. No ISA source was edited.
Machine receipt: `scripts/dialect_check.LAST-RUN.json`; all executed rows:
`scripts/.tmp/round5-fixes-freeze.json` (inherited exact gate filename).

| Blocker | Status | Witness / checker | Green implementation commit |
|---|---|---|---|
| SOL-R8-01 ≡ R8-CODEX-02 | resolved | pt3-pack257/pack256/unpack; Flow.bitcast + dialect_round8.check_state | 4fecd06 (arithmetic/K supplement 023f5a7) |
| R8-CODEX-01 | resolved | pt6-zero-stack/heap, pt8-zero-copy; zero_images + dialect_round8.check_state | 023f5a7 |

Hand derivations: little-endian <1,1> → 257; <0,1> → 256;
769 → <1,3> → lane1=3. Exact finite scalar domains/dispatch retain all
three. LLVM18/23 verify O0/instcombine/materialised forms; native clang18/23
O0/O3 widths are 257/256/3, including two X gates at index256, final bit0.
Conditional zero-filled stack/heap store gives raw/idx={0,1}, widths={1,3};
false/true execute1/3 and free cleanly/code0. PT8 copies zero into an initially
nonzero global. Native execution for these uses materialised semantics, never
source LLVM uninitialised-load behaviour. No finite bitcast became BLK-1.

Red→green: six bitcast-domain subtests; six zero-domain subtests; bitcast+1
arithmetic; and five existing descriptor counts. Kind0 stays in AV with the
existing T-IFACE outcome, but is not counted as a valid kind1..5 shape.
No existing expectation was weakened. The development five-failure gate is
archived at scripts/.tmp/round8-development-shape-failures.json and is not a receipt.
**84 checker units and 7 legacy runtime tests pass.** No LLVM viewer pass ran.

Version rules follow spec/README.md: full dialect0.2.10, map0.2.9 and norm0.2.8
retain their unchanged mapping/normalisation algorithms and ISA signatures.
Applied sol's S1 N33/N32 wording clarification without changing rule order.
No S0 declines or partials, no narrowing, no new ISA0.8 gap or requested ISA
change. Existing §25.1 dependencies and their blocked verdicts remain unchanged.
Codex's nonblocking PT12 atomic update suggestion is open as b-dialect-spec-0y2;
not claimed resolved by the two S0 fixes. Main implementation bead jip is closed.
No worklog/HANDOFF/brief/ISA/corpus-program edits; nothing pushed.

| Family | Passed | Failed | Blocked |
|---|---:|---:|---:|
| asm | 1 | 0 | 0 |
| blocker | 19 | 0 | 0 |
| cc-run | 8 | 0 | 0 |
| check | 22 | 0 | 0 |
| coverage | 125 | 0 | 0 |
| driver | 2 | 0 | 0 |
| events | 3 | 0 | 0 |
| frontend | 21 | 0 | 0 |
| hash | 9 | 0 | 0 |
| header | 1 | 0 | 0 |
| map | 21 | 0 | 0 |
| native | 31 | 0 | 0 |
| normalise | 46 | 0 | 0 |
| parse | 788 | 0 | 0 |
| recognise | 148 | 0 | 0 |
| run-oracle | 22 | 0 | 0 |
| run-program | 5 | 0 | 0 |
| seeds | 1 | 0 | 0 |
| state | 76 | 0 | 0 |
| step-check | 6 | 0 | 0 |
| tdl | 10 | 0 | 0 |
| trace | 3 | 0 | 0 |
| xrefs | 1399 | 0 | 0 |
| **Total** | **2767** | **0** | **0** |

Exact inherited freeze command (scripts/.tmp existed):

```sh
env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER TMPDIR=/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp python3 /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/dialect_check_v02.py --json /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp/round5-fixes-freeze.json
```

## Round-8 fixes — in progress — 2026-10-30

Owner: implementation sub-agent; bead b-dialect-spec-jip. Baseline 2732/2732.
Read binding round-5/6/7/8 briefs and full round-8 blocker witnesses.
Hand derivation: <1,1> -> 257, <0,1> -> 256; 769 -> <1,3>.
Conditional stack/heap store: initial 0 union stored 1 -> lane widths {1,3}.
Implementing PT3 first; DB/DN/DS examples pt3-pack257/pack256/unpack added.
PT3 group green: 2749/2749 freeze, 0 failed/blocked; 79 units pass.
Red: test_round8_bitcast_domains failed six subtests (18/23 x three geometries),
then green after Flow.bitcast. Native source/O0/instcombine/materialised O0/O3
checks observe widths 257/256/3, two gates at 256 in sol, clean frees/code 0.
SOL-R8-01 ≡ R8-CODEX-02 resolved; checker dialect_round8.check_state.
Next: R8-CODEX-01 zero initial images; version/final receipts after both groups.
PT3 commit: 4fecd06. R8-CODEX-01 stack/heap/copy examples added; running
red test_round8_zero_domains failed six subtests (missing INT(0)); now green.
Stack/heap/PT8-copy native materialised 18/23 O0/O3 observe 1/3, clean free/code0.
Zero images are byte intervals with symbolic unknown ends, independent of slots;
loads union decoded zero and stores/copies, and copies carry image subranges.
Additional gate-discovered bug: five descriptor-shape counts counted kind0 as
valid after zero seeding. A five-subtest red regression reproduces it; filter
only the valid-shape count to the existing 1..5 table, retaining full AV and
T-IFACE. No expectation was weakened. The development gate with those five
failures is not a freeze receipt. Rerun full gate after the repair.
Full version bumped to 0.2.10; map stays0.2.9 and norm0.2.8 (unchanged algorithms).
Arithmetic through a finite bitcast also now retains PT5 finite values (red→green).
Final gate green: 2767/2767, 0 failed, 0 blocked/unavailable (2732→2767).
84 checker units and 7 legacy runtime tests pass. All 105 normative/checker/
harness/corpus manifest files remained unchanged through final validation.
R8-CODEX-01 resolved; committing zero-image/version group, then writing both
full final receipts bound to that code commit. Optional PT12 atomic suggestion
is tracked separately as open b-dialect-spec-0y2; not an S0 repair claim.
Owned paths only; headless; no push; no source narrowing or ISA change planned.

## Plugin-relay final freeze — 0.2.9 — 2026-10-30

**2732/2732 passed; 0 failed; 0 blocked/unavailable. Baseline 2731 → 2732.**
Draft/full version `0.2.9` (`dialect-0.2.9;isa-0.8`); ISA grading target 0.8.
Code/spec/checker snapshot: `2c718bd6e1931a8ac02eaa8d9e0d82a5842feab9`.
Spec SHA-256: `9cb4cb9e7a2480b5acfb06da1b744a3d7b1379b8adde1f0ae5b00d7739eb45d9`.
Checker/harness/source manifest SHA-256: `79c4f568f3ad0d29c8aa30e18e7680a7e11a8cdf54534b2a95c546bb4636c4d7`.
Independent interpreter: `8d49944066a9c776c28447f8fcd5619ee7238b63`; immutable source fingerprint
`a4f8dd9e8ab8bbcf6723a0899a463b4eae04abcde06d9b365b8cf2080f4708be`.
Final interpreter HEAD and all files in its source manifest matched at receipt writing.
Normative/checker/harness/corpus source manifest stayed unchanged throughout the final gate.
No ISA source edits. Machine receipt: `scripts/dialect_check.LAST-RUN.json`;
complete rows: `scripts/.tmp/round5-fixes-freeze.json` (inherited exact gate filename).

| Finding | Status | Checked witnesses |
|---|---|---|
| b-dialect-spec-uxi | resolved | atomic-nand map/check/hash/run; budget-stage state; test_canonical_global_numbering |
| b-dialect-spec-566 | resolved | unchanged spec-sem2-adj/compute on LLVM 18/23; test_abi02_corpus_regions, budget-record and ABI-selection regressions |

Numbering is G1, G2, … in link order. Atomic NAND: 0xf0 & 0xcc = 0xc0;
8-bit complement = 0x3f = 63. Data name changes its ISA §9.2 data envelope;
the dependent lproc/oracle hashes change transitively. Regenerated by Rust hash/check:

| Vector | New interface hash |
|---|---|
| atomic-nand ref | `21917fb6f3a0cc9bd14651126bb3fecaadcdccbed30b854170c7ba10741adac4` |
| atomic-nand L1 | `4b300c0de9ef64684ae9d5e3e010b6c4888d0e60504c9dd95861d02f753e5e5c` |
| atomic-nand G1 | `e2076ae22078cd264795a96c18f893aff94ffc100ec1480568616b5226a115a7` |
| budget-stage selection_identity | `4162aa7c5cf3b7bed36162dd7c0f123e26e0606a8bc118184d9f7acaab0786ce` |
| budget-stage final identity | `7486a0aa9e6711325475ffce67d6ec1bb3d4d4ec981eb3b755e171ba04819365` |

Atomic NAND still executes code=0/payload=63/steps=16. Budget-stage keeps
baseline code=2/steps=43, final code=0/payload=7/steps=316 and steps-only code=1/steps=0.
Internal driver and staged-budget linkmaps now use G1 as well. The checker rejects
noncanonical fixture numbering and executes all 22 published objects, including 21 maps.

Runtime ABI selection uses module signatures, with separately keyed v0/0.2 objects;
the normative header participates in the runtime cache key. ABI 0.2 budget records
print deterministic values, not addresses. No corpus program changed.

| Case | LLVM | llc O0/O3 exit | P2 L1–L6 |
|---|---:|---|---|
| spec-sem2-adj | 18 | 0 / 0 | 11/11 pass/noop |
| spec-sem2-adj | 23 | 0 / 0 | 9/9 supported pass/noop |
| spec-sem2-compute | 18 | 0 / 0 | 11/11 pass/noop |
| spec-sem2-compute | 23 | 0 / 0 | 9/9 supported pass/noop |

All 69 baselines rerun on both majors. Other 67 cases retain byte-identical O0/O3
canonical traces, exits, baseline issues, marker externals and O3 comparisons.
All 63 stored baselines and 1,386 stored P2 cells match; 1,518 total P2 cells executed.
LLVM 23's existing Os/Oz refusals and intentional negative controls remain unchanged.
Historical P1/P3 spike tables are retained, not claimed rerun.
Corpus receipt: `corpus/legality/results/abi-0.2-relays.json`; linked from its REPORT.md.
76 checker unit tests and 49 harness tests pass. The viewer-pass test was excluded
to obey the brief; no LLVM view pass was run. TMPDIR stays below scripts/.tmp.

| Family | Passed | Failed | Blocked |
|---|---:|---:|---:|
| asm | 1 | 0 | 0 |
| blocker | 19 | 0 | 0 |
| cc-run | 8 | 0 | 0 |
| check | 22 | 0 | 0 |
| coverage | 125 | 0 | 0 |
| driver | 2 | 0 | 0 |
| events | 3 | 0 | 0 |
| frontend | 21 | 0 | 0 |
| hash | 9 | 0 | 0 |
| header | 1 | 0 | 0 |
| map | 21 | 0 | 0 |
| native | 31 | 0 | 0 |
| normalise | 46 | 0 | 0 |
| parse | 770 | 0 | 0 |
| recognise | 142 | 0 | 0 |
| run-oracle | 22 | 0 | 0 |
| run-program | 5 | 0 | 0 |
| seeds | 1 | 0 | 0 |
| state | 70 | 0 | 0 |
| step-check | 6 | 0 | 0 |
| tdl | 10 | 0 | 0 |
| trace | 3 | 0 | 0 |
| xrefs | 1394 | 0 | 0 |
| **Total** | **2732** | **0** | **0** |

No scope narrowing, removed/weakened expectations, corpus-program edits, ISA changes
or push. Existing named ISA blocked-verdict checks remain the documented dependencies.
Unchanged descriptor oracle/inplace trace diagnostics still direct semantic execution
to the ISA executor; this relay repairs the budget-argument mismatch.

Exact freeze command (scripts/.tmp existed):

```sh
env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER TMPDIR=/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp python3 /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/dialect_check_v02.py --json /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp/round5-fixes-freeze.json
```

## Round-7 final freeze — 2026-10-30

**2731/2731 passed; 0 failed; 0 blocked/unavailable. Baseline 2651 → 2731.**
Draft/full version `0.2.8` (`dialect-0.2.8;isa-0.8`); ISA grading target 0.8.
75 checker unit tests and 4 legacy runtime tests pass headless.
Final spec/checker code snapshot: `d627fd10b3feae73e25f04b189ddc90d549a6fa5`.
Resolved groups: pointer `8f83291`, lanes `8694e5f`, FP `d627fd1`.
Spec SHA-256: `8f493e36ab5dee9a934d55312767589b81e7961ab22877bc1d0db5cf4ed95cdc`.
Checker/source file-set SHA-256: `b61294a4199b057417f5f23b9c0feeab49bb86aec84a8845f631a4e72390680e`.
Independent interpreter final snapshot: `0b70157c65ddf91184e9ef9e753dd61ab94a7c0b`;
source fingerprint `cebb8019f4e657361ce395b89bab04efb590fdd157bda73281c2ea18b48d8097`.
The gate also used immutable initial snapshot `c37b9698c6208303cb63498626649ec183179171`,
fingerprint `bfc88c5be2029d66bc77e59c15f21cbf9dd6313eaf8069ff2cdd028d1db41290` before the ISA checkout advanced.
The final snapshot matched dependency HEAD and its source-file manifest at
validation end (checked immediately after the gate). The working dependency
source changed again before receipt writing; this is not a claim that the
current checkout is byte-equal to that immutable snapshot. No ISA source was edited. Earlier development runs, including
the snapshot-guard rejection while HEAD moved during a build, are not receipts.
Normative/checker source manifest was unchanged throughout this final freeze.
Machine receipt: `scripts/dialect_check.LAST-RUN.json`; complete executed rows:
`scripts/.tmp/round5-fixes-freeze.json` (inherited historical filename).

| Family | Passed | Failed | Blocked |
|---|---:|---:|---:|
| asm | 1 | 0 | 0 |
| blocker | 19 | 0 | 0 |
| cc-run | 8 | 0 | 0 |
| check | 22 | 0 | 0 |
| coverage | 125 | 0 | 0 |
| driver | 2 | 0 | 0 |
| events | 3 | 0 | 0 |
| frontend | 21 | 0 | 0 |
| hash | 9 | 0 | 0 |
| header | 1 | 0 | 0 |
| map | 21 | 0 | 0 |
| native | 31 | 0 | 0 |
| normalise | 46 | 0 | 0 |
| parse | 770 | 0 | 0 |
| recognise | 142 | 0 | 0 |
| run-oracle | 22 | 0 | 0 |
| run-program | 5 | 0 | 0 |
| seeds | 1 | 0 | 0 |
| state | 70 | 0 | 0 |
| step-check | 6 | 0 | 0 |
| tdl | 10 | 0 | 0 |
| trace | 3 | 0 | 0 |
| xrefs | 1393 | 0 | 0 |
| **Total** | **2731** | **0** | **0** |

All five blocker IDs (four distinct) resolved. No declines, partials, narrowed
capabilities, removed/weakened expectations, ISA edits or push. These fixes need
no ISA 0.8 change. Existing §25.1 ISA-4/ISA-1/ISA-12/ISA-7 blocked-verdict checks
remain named dependencies, not claims that their mechanisms landed in 0.8.
The native FP fixture proves the tagged carrier vectors, not a production
soft-float library or cross-native ARM/RISC-V execution.

Exact final command (scripts/.tmp existed):

```sh
env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER TMPDIR=/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp python3 /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/dialect_check_v02.py --json /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp/round5-fixes-freeze.json
```

## Round-7 fixes — b-dialect-spec-j08 — 2026-10-30

Sole spec/checker editor; baseline 2651. Before edits, LLVM 18/23 probes
verified the original pointer/lane/FP sources at O0. Pointer arithmetic:
2*(-2^63)=0 modulo 2^64; wide +2^64 truncates to zero displacement.
Dynamic lane {1,3} plus totalised zero gives widths {1,2,4}. Constant index
2 (or unsigned -1) on two lanes extracts zero / preserves inserted vector.
fp128 -> x86_fp80 and ppc_fp128 -> fp128 fpext both fail with
`invalid cast opcode` on both LLVM majors. Direct own-format carrier calls
avoid these conversions entirely. Probe logs: scripts/.tmp/round7-probes.

| Blocker | Status | Checker case | Commit |
|---|---|---|---|
| SOL-R7-01 / R7-CODEX-01 | resolved, gate 2667/2667 | pt5-int-wrap, pt4-wide-wrap, pt6-unknown-address | 8f83291 |
| R7-CODEX-02 | resolved, gate 2680/2680 | pt10-lane-zero; test_round7_lane_domains/execution | 8694e5f |
| R7-CODEX-03 | resolved, gate 2680/2680 | n-constant-lane; test_round7_constant_lanes/lane_execution | 8694e5f |
| R7-CODEX-04 | resolved, gate 2731/2731 | n-libm-{x86,arm,riscv}-*; libm-invalid-casts; test_round7_fp_formats/execution | d627fd1 |

## Round-6 final freeze — 2026-10-30

**2651/2651 passed; 0 failed; 0 blocked/unavailable. Baseline 2598 → 2651.**
Draft/full version `0.2.7` (`dialect-0.2.7;isa-0.8`); ISA grading target 0.8.
67 checker unit tests and 4 legacy runtime tests pass headless.
Code/spec/checker snapshot: `8c7fb5264384c53e8659b101aa30c4416ef4d4ee`.
Spec SHA-256: `d183190bd4d8f924e617b2de570beda317175cb388b2bead635bcd847275e09c`.
Checker/source file-set SHA-256: `90c2c9374896f2ef8ed3abd796348ad6b2afedaf21179ad29b01d3ab5857e875`.
Independent interpreter: `0bc842653c2cbf860fec90a79ac2115d3d5e11fa`; immutable source fingerprint:
`1d4920cd86333b6902202e1472245b917dd1340a62c7166aaadc35a03784743d`. Final dependency HEAD matched when validation ended.
Normative/checker source manifest was unchanged during the final freeze.
Machine receipt: `scripts/dialect_check.LAST-RUN.json`; full executed rows:
`scripts/.tmp/round5-fixes-freeze.json` (the inherited command's historical filename).

| Family | Passed | Failed | Blocked |
|---|---:|---:|---:|
| asm | 1 | 0 | 0 |
| blocker | 19 | 0 | 0 |
| cc-run | 8 | 0 | 0 |
| check | 22 | 0 | 0 |
| coverage | 125 | 0 | 0 |
| driver | 2 | 0 | 0 |
| events | 3 | 0 | 0 |
| frontend | 21 | 0 | 0 |
| hash | 9 | 0 | 0 |
| header | 1 | 0 | 0 |
| map | 21 | 0 | 0 |
| native | 30 | 0 | 0 |
| normalise | 39 | 0 | 0 |
| parse | 716 | 0 | 0 |
| recognise | 138 | 0 | 0 |
| run-oracle | 22 | 0 | 0 |
| run-program | 5 | 0 | 0 |
| seeds | 1 | 0 | 0 |
| state | 61 | 0 | 0 |
| step-check | 6 | 0 | 0 |
| tdl | 10 | 0 | 0 |
| trace | 3 | 0 | 0 |
| xrefs | 1388 | 0 | 0 |
| **Total** | **2651** | **0** | **0** |

All four round-6 blockers resolved; no declines, partials, weakened expectations,
removed examples, ISA edits or push. Existing §25.1 ISA-4/ISA-1/ISA-12/ISA-7
blocked-verdict checks remain explicit dependency checks, not claims that ISA 0.8
implements those capabilities. No new ISA change is needed for this round.
Development runs and their superseded snapshots are not freeze receipts.

Exact final command (scripts/.tmp existed):

```sh
env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER TMPDIR=/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp python3 /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/dialect_check_v02.py --json /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp/round5-fixes-freeze.json
```

## Round-6 fixes — b-dialect-spec-wfi — 2026-10-30

Draft 0.2.7; spec/checker edited together. Hand derivations preceded edits:
GEP 2^32 mod 2^32 = 0 -> tab[0] -> FN(body); removed ranges give widths
{1,3}, input 2 -> width 3; NAND ~(0xf0 & 0xcc) = 0x3f, returned old 240;
alloca24 + saved-sp8 needs sstack32, so H16-selection must overlay once.
LLVM 18/23 O0 probes retained the alloca/GEP/nand/load-range forms; parameter
range is LLVM 23. Independent native/Rust execution and wrong-result mutations
cover every new witness. No narrowing, removed examples, ISA edit or push.

| Blocker | Status | Checker case | Commit |
|---|---|---|---|
| SOL-R6-01 | resolved (2651/2651 green) | budget-stage; test_round6_budget_staging/execution | 8c7fb52 |
| R6-CODEX-01 | resolved (2651/2651 green) | pt2-wrap; test_round6_wrapped_gep/gep_constant_expression/gep_residue_offset | 8c7fb52 |
| R6-CODEX-02 | resolved (2651/2651 green) | pt5-range/pt5-range-load; test_round6_removed_range/execution | 8c7fb52 |
| R6-CODEX-03 | resolved (2651/2651 green) | n-atomic-nand/atomic-nand; test_round6_nand/atomic_sweep/execution | 8c7fb52 |

Freeze: 2598 → 2651/2651, zero failed or blocked/unavailable; 67 checker and
4 legacy runtime tests pass. Validation used the exact inherited
headless gate command (including its historical round5-fixes-freeze.json filename).
Development runs exposed synthetic unknown-address alternatives mistaken for host
provenance; base-origin checks now preserve existing handle-table/descriptor verdicts.
The independent ISA checkout changed concurrently during development; immutable
snapshots and build-time source/HEAD guards remain in force. No new ISA gap.
Response: ../bennett/docs/council/dialect-2026-10-29/round-6/response.md.

## Round-5 final freeze — 2026-10-30

**2598/2598 passed; 0 failed; 0 blocked/unavailable. Baseline 2514 → 2598.**
Draft/full version `0.2.6` (`dialect-0.2.6;isa-0.8`); ISA grading target 0.8.
59 checker unit tests and 4 legacy runtime tests pass headless.
Code/spec/checker snapshot: `5b01a51ac216fa36a2c7d1cbb5f92aa73b491798`.
Spec SHA-256: `4bbf697dd39e43c5c815864bcb27b502b47a047b18092a67ade466c858a05adc`.
Checker/source file-set SHA-256: `19192e6ba7b92cd3f023091dc103a634739dc692f68315711375645407944fec`.
Independent interpreter: `0b913dace5d69082dda28c85ce5dbb1aefb52cd2`; immutable source fingerprint:
`c65b7590fd21e8de29ea81851ffdbef919a3bc91ba200de5b2ede348ae993c4e`. Dependency HEAD matched when the green gate ended.
Machine receipt: `scripts/dialect_check.LAST-RUN.json`; full executed rows:
`scripts/.tmp/round5-fixes-freeze.json`.

| Family | Passed | Failed | Blocked |
|---|---:|---:|---:|
| asm | 1 | 0 | 0 |
| blocker | 19 | 0 | 0 |
| cc-run | 8 | 0 | 0 |
| check | 21 | 0 | 0 |
| coverage | 125 | 0 | 0 |
| driver | 1 | 0 | 0 |
| events | 3 | 0 | 0 |
| frontend | 21 | 0 | 0 |
| hash | 8 | 0 | 0 |
| header | 1 | 0 | 0 |
| map | 20 | 0 | 0 |
| native | 29 | 0 | 0 |
| normalise | 37 | 0 | 0 |
| parse | 691 | 0 | 0 |
| recognise | 134 | 0 | 0 |
| run-oracle | 21 | 0 | 0 |
| run-program | 5 | 0 | 0 |
| seeds | 1 | 0 | 0 |
| state | 57 | 0 | 0 |
| step-check | 6 | 0 | 0 |
| tdl | 10 | 0 | 0 |
| trace | 3 | 0 | 0 |
| xrefs | 1376 | 0 | 0 |
| **Total** | **2598** | **0** | **0** |

All eight S0 findings and the GEP wording regression are resolved. No declines,
partials, weakened expectations, removed examples, ISA edits or push. The checked
ISA-4/ISA-12 dependency verdicts do not claim those capabilities landed in 0.8;
newly exposed parameter/result accumulation is tracked by **b-dialect-spec-cbe**.

The prior `scripts/.tmp/round5-isa-head-race.json` preserves the 2597/2598 run
whose sole failure was an ISA HEAD-moved snapshot guard. Earlier development
receipts retain the red witness/adapter failures; the green receipt above supersedes
them. The guard was retained. The aborted intervening freeze used superseded
text; final SHA above includes PT2 restored and the canonical GEP algorithm
placed in §16.4. No normative source or checker file changed during the final
successful freeze (source file hashes are in the machine receipt).

Exact final command (scripts/.tmp existed):

```sh
env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER TMPDIR=/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp python3 /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/dialect_check_v02.py --json /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp/round5-fixes-freeze.json
```

## Round-5 fixes — b-dialect-spec-p7u

Hand-derived before edits; red regressions reproduced pointer two-move result,
PT6 {1} rather than {257}, parameter-root accept, unsupported FP/wide call and
atomicrmw forms. Paired normative rules and executable witnesses now implemented;
full freeze 2598/2598 green; 59 checker and 4 legacy unit tests pass. Draft full/norm/handles/
regions/map versions 0.2.6; untouched subversions retain their earlier values.

| Blocker | Status | Checker case | Commit |
|---|---|---|---|
| SOL-R5-01 | resolved | pointer-as270; test_round5_pointer_width | 5b01a51 |
| R5-CODEX-02 | resolved (same pointer defect) | pointer-as270 | 5b01a51 |
| R5-CODEX-01 | resolved | pt6-byte-width; pt6-subrange; test_round5_memory_intervals | 5b01a51 |
| BD3-R5-1 | resolved | handle-param-cross-entry; test_round5_parameter_liveness | 5b01a51 |
| BD3-R5-2 | resolved | n-fpconv-wide; test_round5_fp_wide | 5b01a51 |
| BD3-R5-3 | resolved | n-wide-intrinsics; test_round5_wide_intrinsics | 5b01a51 |
| BD3-R5-4 | resolved | n-atomic-wrap; n-atomic-usub; test_round5_atomic_forms | 5b01a51 |
| BD3-R5-5 | resolved | gep-index-obj/const; test_round5_gep_rows | 5b01a51 |

Baseline 2514/2514. Native/state mutation test_round5_execution passes. Named
ISA-4/ISA-12 gap tracked as b-dialect-spec-cbe; no ISA edits or scope restriction.

# Dialect 0.2 full text — progress

Job: write the normative text of dialect draft 0.2 (`spec/Bennett-Dialect-Spec.md`) from the
ratified outline `spec/outline-0.2.md`. Brief: `docs/briefs/2026-10-29-dialect-0.2-fulltext.md`.
Owned paths: `spec/Bennett-Dialect-Spec.md`, `spec/bennett_markers.h`, `spec/README.md`, this
file, `SPEC_VERSIONS.toml`, `corpus/legality/cases/spec-*`. Standing rule: no narrowing.

## Read (2026-10-29)

- [x] `spec/outline-0.2.md` in full, including the maintainer rulings (E1-E3, E5-E14 as
  recommended; E4 = riscv64; BLK-1..4 named blockers; graded against ISA 0.8)
- [x] `spec/Bennett-Dialect-Spec.md` 0.1 in full
- [x] `docs/spikes/2026-10-28-legality-findings.md` (decisions 1-4)
- [x] `docs/audit/2026-10-29-dialect-0.1-narrowing-audit.md` in full
- [x] `docs/spikes/sqlite/REPORT.md` in full
- [x] `../bennett/docs/Bennett-NorthStar.md` in full
- [x] ISA 0.8 `../bennett-isa-spec/spec/Bennett-ISA-Spec.md` in full
- [x] `../bennett/HANDOFF.md` ("What made the ISA rounds converge")
- [x] `../bennett/docs/council/rubric-isa.md`
- [x] reference interpreter README (CLI: check, hash, run-oracle, step-check)

## Tools used

- Rust ISA reference interpreter: a copy of
  `../bennett-isa-spec/reference-interpreter/target/debug/bennett-isa-ref` (built 2026-10-29
  07:40) in the job scratchpad, so that the concurrent interpreter job cannot change it under
  this job. Every `isa object=` example is checked with `check`, every `text run=` line is the
  output of `run-oracle`, every prefix-reversal claim the output of `step-check`.
- LLVM 18 (`/usr/lib/llvm-18/bin`), 20 (Julia artifact, `corpus/legality/toolchains.toml`),
  23 (`/usr/lib/llvm-23/bin` for clang; rustc llvm-tools for opt): every `llvm` block parsed and
  verified on all three, headless (CLAUDE.md rule 11).

## Sections written

- §1-§3 + header (commit 56a3eb1)
- §4-§8 (commit 85c53ab)
- §9-§12 (commit cd709ee)
- §13-§14 (commit fd30dd5)
- §15-§16 (commit 49a2100)
- §17-§18 + corpus `spec-sem2-*` (commit df9e0a5)
- §19-§25 (commit e0e5142)
- Appendices A (outline changes), B (example index), C (546 generic intrinsics); SPEC_VERSIONS
  0.2/0.8; README change rules (commit d0c4830)
- Hostile re-read under the rubric, two passes of fixes (commits eda7eb3, aa004bf), then a
  consistency pass (section cross-references by script: no dangling internal reference; the
  `markers-c` block equals the header's prototype block byte for byte; version strings `0.2`,
  `dialect-0.2;isa-0.8`, `isa=0.8 … target=0.8` checked).

Size at the end: ~7310 lines, ~59,500 words, 385 kB; 87 verdict examples (82 `llvm`, 5 `c`: 56 accept,
26 reject, 5 blocked), 17 normalisation pairs, 6 executed ISA objects.

## Verification run (final state)

- Every `llvm` block (126) parses and verifies with `opt -passes=verify` on LLVM 18, 20 and 23,
  headless (`env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER
  TMPDIR=$PWD/.tmp`).
- Every `isa object=` block passes `bennett-isa-ref check`; every `hash=` line equals `hash`;
  every `run=` line is the output of `run-oracle`; every `step-check=` claim is the output of
  `step-check` (scratch tool `checkruns.py`: 0 failures).
- Normalisation pairs with `native=` lines: input and output modules compiled with clang 18/23
  and the job's seed implementations, the stated values computed by running them.
- `cc-run=` native statuses (sjlj 77, fiber 98, exit 3) computed by native builds (clang 18 and
  23, -O2); the R-tier `run:`/`reverse:` lines need `run-cc`/`reverse` (b-isa-spec-xam).
- Header: compiles as C and C++ on clang 18/20/23; static asserts on record layouts; IR
  signatures of all 23 prototypes identical across majors and equal to §3.2.
- Corpus: `spec-sem2-ctrl`, `spec-sem2-adj`, `spec-sem2-compute` are byte-equal to §18.8. Baseline
  on a scratch copy of `corpus/legality` with `python3 harness/run.py baseline --majors 18,20,23
  --cases 'cases/spec-sem2-*'` (headless): ctrl agrees on all majors; adj and compute report
  `BASELINE PROBLEM … L1 baseline exit=87` on all majors, because the trace runtime is still at
  ABI v0 (2-argument adj, 3-argument compute); this is bd `-566` (trace runtime at ABI 0.2).

## Decisions taken while writing (not in the outline)

- Primitives `__bennett_nz_alloc` / `__bennett_nz_free` (ISA alloc/free, lift.alloc/lift.free)
  added next to `__bennett_nz_fault`: the runtimes allocator needs a way to reach `lift.alloc`.
- Reserved-name rules apply to *producer inputs* (driver checks before link); runtimes/arith
  bitcode may use `__bennett_rt_/dev_/sf_/nz_` names.
- §5: abstract value = (atom set, TOP flag); TOP never stands for a ROOT atom; K = 4096 cap is
  normative (decides verdicts). Residue classes carry an extent [lo, hi) from array types (B-27).
- §5: `inttoptr` constants are TOP for function pointers (A(F) is fixed only after the
  comparison link); a Julia `@cfunction` constant traps unless it equals an A(F) at run time;
  Bennett.jl's `ptr @f` route keeps the capability.
- §6.5: two realisations: *direct* (handle never stored in memory: CC qreg SSA values, no bound)
  and *static register file* (stored handles; reference instance bound; infinite -> BLK-1).
- §6.6: device-entry pointer parameters get a candidate ROOT(E,i) atom that survives only if it
  reaches a marker handle operand (decides QREG binding).
- §7.5(b): R-tier allocation hoisting uses the reference instance bound; BLK-4 only when infinite.
- §8.1: descriptor layout = LLVM struct {H,[n x Bind],[m x DevBind]} under the datalayout.
- §8.5: snapshot register released by `measure` (unentangled basis state).
- §8.6: wide outputs are the `wide` event: copy-out pairs issued as CC-level region calls
  (`qreg.slice` views, `@xor<w>` action), temporaries freed with the ISA §3.3 dynamic check.
- §8.7: in-place verification computes B_min; run-time budgets checked at the marker (`T-BUDGET`).
- §9.2: budget table JSON schema and precedence (identity > region key > symbol glob > default).
- §9.5 example `budget-device-computed` uses a 64-bit value assembled from 64 measurements, so no
  launch-time token set covers it (a value set like {5, n+5} would be launch-mintable).
- §10: Cl/M/Co object states; slices with classical twins; events applied as CC-level region
  calls (ISA §6 per-region coarse windows make a static action unable to uncompute a slice after
  an arena write); per-slice fault registers retained and combined by `@firstfault`.
- §12.1: N33 runs immediately before N32 (its fpext/fptrunc pairs are FP that N32 rewrites).
- §14.9: blockaddress values are bytes of a driver-added data object `__bennett_rt_blk.<f>`, so
  they never collide with A(F) or other objects.
- §15.2: the default `cpuid` table is read on the build machine and recorded in the build record.
- §16: reference object = wrapper `@ref` + lprocs; layout restricted to closure-reachable
  globals; A_tab chosen so allocation-table overflow never precedes heap exhaustion.
- §18.4: `T-LEAK` outside generations is checked at program end (§6.6's REPL lifetime).
- §19.5: `text_base` rises above the device ranges when they pass 0x400000 (native binary must
  map heap/arena/regions disjointly from its code); §20.1 RAM placed by the profile's linker
  script at 0x80000000 after the other data.

## Departures from the outline

All are in the spec's Appendix A (A1-A23), each with its reason; every one keeps or widens the
outline's capability. Summary: A1 wide outputs by 2k-1 copy-out calls (outline's qxor cleanup is
ill-formed under ISA §6); A2 snapshot release by measure; A3 direct handle realisation without a
bound; A4 exact reference instance bound; A5 Cl/M/Co; A6 slices without stores/markers + classical
twins; A7 one XOR of c ⊕ v; A8 CC-level event application; A9 retained per-slice fault registers;
A10 effects in action regions are fault 8; A11 history as declared outputs measured at the
epilogue; A12 two more primitives; A13 `@cfunction` constants dispatched by value; A14 thunk cycles
resolve to themselves (BD-E-REGION-THUNK deleted); A15 N0 (LLVM's own lowering passes); A16 N34
marks as metadata; A17 wrapper/lproc form and layout rules; A18 compare-tree block names; A19
blockaddress/indirectbr, seven FP formats, exit via hostcall, B_min/T-BUDGET; A20 two more wording
items; A21 `__bennett_rt_platform_ram`; A22 `spec-sem2-*` beside `spec-sem-*`; A23 N33 before N32.

## Examples and checker requirements

The full index is the spec's Appendix B. Capabilities per example family:

| Examples | Checker capability | Executor / CLI |
|---|---|---|
| markers-ir, markers-c | parse, header | LLVM 18/20/23, clang 18/20/23 |
| operand-*, recog-*, attr-*, unwind-invoke, julia-jlplt, effect-lie, pt-variable-index, handle-* (20), qstore-twice, region-* (18), oracle-*, budget-*, indirect-*, asm-musl-syscall, version-flag | parse, recognise | LLVM; Python reference recogniser (to be written in dialect_check.py) |
| inplace-* (4) | parse, recognise, run-oracle | isa-ref `run-oracle` (exists) for the inverse check |
| budget-table=rung4-mini | driver | Python |
| tdl, tdl-overwrite, tdl-effect, tdl-angle (+ tdl=, state=) | parse, recognise, tdl, run-action | Python TDL; isa-ref `run-action` (b-isa-spec-xam, requested) |
| effect-console-r, effect-console-cc; sjlj-two-frames, fiber-pingpong, exit-status (cc-run=) | frontend, run-cc, reverse | isa-ref `run-cc`, `reverse` (requested); native statuses computed |
| 17 normalise-in/out pairs, 10 native= | parse, normalise, native | LLVM; Python normaliser; clang + spec/seeds (not yet created) |
| residual-nsw, residual-clean | validate | Python |
| inc8, add2, rung4-mini, rung8-mini, listsum, switch5 (lift=, linkmap=, object=, hash=, run=, step-check=) | map, check, hash, run-oracle, step-check | isa-ref `check`, `hash`, `run-oracle`, `step-check` (exist; all lines verified) |
| rung4-minidb, rung4-grover-tu (+ native=) | frontend, recognise, native | clang 18/20/23 |
| sem2-ctrl, sem2-adj, sem2-compute (events=, state=) | trace, run-action | trace runtime at ABI 0.2 (bd -566); isa-ref `run-action` (requested) |

Blocked examples (one per BLK): `operand-width-host` and `handle-vec-unbounded` (BD-B-ISA4,
BLK-1), `budget-device-computed` (BD-B-ISA1, BLK-2), `inplace-param-quantum` (BD-B-ISA3, BLK-3),
`region-reversible-qalloc-dynamic` (BD-B-ISA12, BLK-4); each has a `text blocker=` report line.

## Open questions

- Rule ids without an example (P-1 fails on them until added; Appendix B lists them): N0, N12,
  N15, N25, N34, N35; V2-V16; PT12; the OUT binding's object; BLOCK, CLOCK, CONSOLE device
  bindings; entry-state transfer (§8.5); indirectbr; §19.3-§19.8; §20.
- `spec/seeds/` (checker seeds named in §21.4) and `spec/asm/<arch>.toml` (§15.1) are not owned
  paths of this job and do not exist yet.
- ISA wording items raised in §25.2: certificate fields (build record, budget table, deferred
  measurement); ISA §12.2 domains with a fixed classical region (rung 4(a)); `qreg` across CC
  call/ret/br; code 10 "(R only)".
- TDL: event application as CC-level region calls is exact but not one ISA action; an ISA 0.9
  per-cell window rule would allow static actions (efficiency, not capability).

## Issues filed (bd)

- `b-dialect-spec-566`: note added (spec-sem2-adj/compute baseline exit 87; trace runtime to ABI 0.2).
- `b-dialect-spec-d4k`: checker seeds `spec/seeds/` (§21.4) do not exist.
- `b-dialect-spec-gvr`: rule ids without a checked example (P-1 list of Appendix B).
- `b-dialect-spec-rq0`: publish `spec/asm/<arch>.toml` from §15.
- `b-dialect-spec-gwf`: ISA 0.9 wording items raised by §25.2.

`.beads/issues.jsonl` was rewritten by `bd` and is left uncommitted (not an owned path).

## Round-1 fixes

Brief: docs/briefs/2026-10-29-dialect-0.2-council-fixes.md; tracking b-dialect-spec-pz7.
Version 0.2.1 per spec/README.md; ISA 0.8 unchanged. No push.

| Blocker id | Status | Commit |
|---|---|---|
| D02-11 | resolved | 25b52ea |
| D02-12 | resolved | 25b52ea |
| D02-13 | resolved | 25b52ea |
| BD2-5 | resolved | 25b52ea |
| D02-14 | resolved | 25b52ea |
| D02-16 | resolved | 25b52ea |
| D02-17 | resolved | 25b52ea |
| BD2-6 | resolved | 25b52ea |
| BD2-1 | resolved | 5186b42 |
| BD2-2 | resolved | 5186b42 |
| D02-02 | resolved | 5186b42 |
| BD2-4 | resolved | 5186b42 |
| D02-03 | resolved | 5186b42 |
| D02-04 | resolved | 5186b42 |
| D02-05 | resolved | 5186b42 |
| D02-06 | resolved | 5186b42 |
| D02-07 | resolved | 5186b42 |
| D02-08 | resolved | 5186b42 |
| B1 | resolved | 5186b42 |
| BD2-3 | resolved | bf9a5f3 |
| D02-01 | resolved | bf9a5f3 |
| D02-09 | resolved | bf9a5f3 |
| D02-10 | resolved | bf9a5f3 |
| D02-15 | resolved | bf9a5f3 |
| B2 | resolved | bf9a5f3 |
| B3 | resolved | bf9a5f3 |
| B4 | resolved | bf9a5f3 |
| D02-18 | resolved | bf9a5f3 |
| D02-19 | resolved | bf9a5f3 |
| D02-20 | resolved | 40a4962 |
| D02-21 | resolved | 40a4962 |
| D02-22 | resolved | 40a4962 |
| V10 / b-dialect-spec-7u1 | resolved: retain all-format bit operations and carrier transport; full dialect/norm 0.2.2 | this commit |

### Round-1 final verification (2026-10-29)

All 32 source JSON blocker ids have resolved normative-text entries in the response.
No declines or text partials; full freeze gate remains incomplete. Group commits are
listed in the table above. Final consistency fixes also update §9.3/§9.4 generation
budget summaries, fault collection, version labels, retired BLK-3 references, hidden
arena base propagation, Q1 candidates and Q2 punctuation, and all-guest Sv39 wording.

- Offline Rust build succeeds. Nine objects check/run, five hash blocks match; new
  arena O1 payloads 1/6 (10 rows), FP aggregate 1099511627521 (10), entry stack 4112 (42).
- Selected final gate parse/header/check/hash/run-oracle/xrefs: 1702/1702, exit 0.
- Full gate: 1939/2029; 90 fail/blocked, compared with baseline 60. The response has the
  exact family counts. Checker issue b-dialect-spec-ofu, append-only questions Q4–Q8.
- Direct dialect_check_v02.py exits 0 but has no main; only frontend execution counts.
- Independent clang18/23 arithmetic, corrected fcmp input/output and ABI vectors,
  aggregate packing and adopting allocator contract executions pass.
- New ISA dependency b-dialect-spec-bz6: BLK-5/ISA-7 requires R fault C with exact record
  code, no later effects, preserved reversible prefix history; no ISA source edits.
- No push. Only owned files committed; generated Beads export remains uncommitted.

## Freeze-gate coverage follow-up (2026-10-29)

Read CLAUDE.md in full, both task beads, checker PROGRESS/LAST-RUN and questions,
this progress file, README and the round-1 response. Checker 56fe08c is read-only.
Example additions do not change semantics; README requires bumps for semantic
changes, so version remains 0.2.1. ISA 0.9 draft 61550b4 is reference-only.

### Round-1 fixes table additions

| Finding | Change | Verification |
|---|---|---|
| BLK-5 / b-dialect-spec-bz6 | Preserve R-budget state, add materialised code-1 example/blocker and exact ISA-0.9 K5/fault-C result | blocked verdict cannot be routed by frozen checker; source and blocker misclassified as producer inputs |
| V10 / b-dialect-spec-7u1 | Filed literal whitelist vs all-format retained fneg conflict; no normative edit | conflicting rules need full boundary reconciliation, so no semantic bump or narrowing |
| P-1 / b-dialect-spec-1jb: driver/platform | Seven concrete input/state scenarios, eight LLVM modules, index rows | parse 564/564; all new recognition accepts; seven state adapters unavailable and seven coverage rows hard-coded False |
| P-1 / b-dialect-spec-1jb: bindings/transfer/indirectbr | Six hand-derived objects, LLVM/linkmap/run companions and index rows | all six object checks and run blocks pass; replay maps exactly; five maps fail |
| P-1 / b-dialect-spec-1jb: V2–V16/PT12 | 15 clean/residual validator pairs and qalloc ROOT return witness, all indexed | parse 522/522; recognise 112/115; V4/V10/V12 missed rejections |
| P-1 / b-dialect-spec-1jb: N0/N12/N15/N25/N34/N35 | Six hand-derived normalisation pairs and Appendix B rows; no rule narrowed | N12 passes; five missing transforms fail loudly |

### Verification table

| Group | Gate | Result |
|---|---|---|
| normalisation omissions | whole direct gate, headless, repository TMPDIR | 2043 pass / 34 fail / 1 blocked (2078); parse 429/429; normalise 19/24 |
| validator/points-to omissions | selected parse,recognise,coverage; headless, repo TMPDIR | 746 pass / 16 fail / 0 blocked (762); 13 remaining coverage rows |
| bindings/transfer/indirectbr | selected parse,map,check,run-oracle,coverage | 697 pass / 12 fail / 0 blocked (709); parse 540/540, check/run 15/15 each, map 9/14, coverage 118/125 |
| driver/platform | selected parse,recognise,state,coverage,xrefs | 2139 pass / 10 fail / 8 blocked (2157); state 28/36, coverage 118/125 |
| BLK-5 | selected parse,recognise,blocker,state,coverage,xrefs | 2142 pass / 12 fail / 8 blocked (2162); parse 567/567, blocker 5/6 |
| final whole gate | direct runner, all families, headless, repository TMPDIR | 2273 pass / 22 fail / 8 blocked (2303), exit 1 |

Normalisation report: `scripts/.tmp/coverage-normalisation.json`. Coverage 96/125
is index discovery only, not successful execution: the six added witnesses remove six
missing-index rows, but five transforms remain red. N0 leaves widenable.condition;
N15 raises “dynamic extract needs select chain”; N25 leaves byval and omits copy;
N34 emits no R marks (rmode attribute ignored); N35 drops volatile without MMIO
routing/poll (platform attribute ignored). These are checker limitations, not
permissions to alter the normative output. N12 passes on all three LLVM majors.


Report: `scripts/.tmp/coverage-validator.json`. All 15 clean validator witnesses
and PT12 ROOT return pass. Negative V4 (ctlz true), V10 (half fneg) and V12
(undefined nonprimitive call in materialised L/R) incorrectly accept; retained
as failing obligations. V8 negative also triggers V13, so this does not claim
an independent pre-N21 V8-pattern implementation. No normative text was fixed.


Report: `scripts/.tmp/coverage-bindings.json`. The six hand-authored objects
were checked/hashed/run independently with Rust before insertion; Python only
serialised symbol/layout facts and inserted the executor's interface hashes.
Hand-derived successes: OUT byte 9 / 10 rows; CLOCK 3 / 16 rows; BLOCK first-byte
42 or 255 / 16 rows; CONSOLE 120 / 27 rows; replay byte 7 / 16 rows; indirectbr
7 or 9 / 9 or 12 rows, no-match code 4 / 10 rows (the failing path never executes
wrapper retval). Clock store rematerialises its global-address operand per map
row conventions; no commoning optimisation is assumed. The replay object maps
byte-exactly, isolating caller-mutated G replay with k=0; general allocation/stack
replay remains covered by the earlier runtime vectors, not claimed here.

Five frozen mapper gaps remain: OUT explicitly raises checker-unimplemented;
BLOCK ignores its interface and model-state prologue; CLOCK ignores counter
initialisation; CONSOLE omits buffer/prologue/output delivery; indirectbr explicitly
raises checker-unimplemented. The binding objects and their expectations remain
unchanged to expose these gaps. Seven hard-coded driver/platform coverage failures
remain regardless of examples (dialect_meta.coverage sets them False).


Report: `scripts/.tmp/coverage-driver.json`. All new source modules parse and
recognise; all 1309 xrefs pass. Each driver operation has a concrete hand-derived
expected state, not merely a section mention. Seven missing state adapters fail
explicitly under P-2 (reported as blocked by this checker). The fallback labels
them “TDL state execution” / b-isa-spec-xam, but all CLI commands exist: missing
capabilities are synthesis, placement promotion, comparison-link layout, snapshot
rewrite, closed-unit fallback, mixed-major link, and the platform UART path.
None can be executed by current families just by adding a tag. In addition,
coverage unconditionally sets all seven section obligations False, irrespective
of Appendix B rows. Recorded on 1jb and Q12; never weakened or removed.


Report: `scripts/.tmp/coverage-blk5.json`. ISA 0.9 draft commit 61550b4,
section 0.2 K5 and section 4.1 fault row were read: literal C < 2^64, zero
effectively 4, exact nonzero terminal record, FAILED, no successor effects,
reversible prefix retained. The expected under-0.9 budget result is code 1,
empty console/tape, exactly one terminal record with no host request; it still
requires dialect counter instrumentation, not host fuel. Section 25.1 already
had BLK-5 in the same table form as BLK-1/2/4; added witness/draft-reference
paragraph, without changing the ISA-0.8 grading target.

Both materialised code-1 witness and blocker report carry blocked:BD-B-ISA7.
The original state check is retained, with the same verdict and required 0.9
result alongside. Frozen recognition and blocker methods allow materialised
reserved primitives only when id == r-fault-code, so the new r-budget-prefix
example/report wrongly produce BD-E-MARKER-UNKNOWN; state dispatch ignores the
verdict and still probes host fuel. It cannot pass as a blocker-family verdict
without a checker change. This is recorded on bz6, 1jb and Q13, not hidden by
renaming to the special-cased example or removing the original state obligation.

New normative finding b-dialect-spec-7u1 quotes V10's extended-format exception
list and the conflicting section 13.1/16.4 retained-fneg contract. The literal
V10 negative is retained to expose the conflict. The earlier “missed rejection”
classification for V10 is superseded: unlike V4/V12 this is not simply a checker
fix. The intended complete exception boundary also includes retained FP
intrinsics and carrier interfaces, so a complete semantic fix is not uniquely
specified by this coverage task. No normative rule was changed; version 0.2.1
remains appropriate under README.

### Final freeze-gate verification (2026-10-29)

**Not green; round 2 is not ready.** All 35 omissions have concrete added
witnesses and index evidence, but P-2 execution still fails. Do not interpret
118/125 index coverage as implemented capabilities. No checker code changed,
no check removed, no expectation weakened, no push, and no semantic version bump.
This section supersedes the historical open-questions list and earlier counts.

Command (absolute paths; environment headless):

```sh
env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER TMPDIR=/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp python3 /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/dialect_check_v02.py --json /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp/editor-final-freeze.json
```

Spec tested: b7330de, draft 0.2.1; checker remains 56fe08c. Interpreter receipt:
commit 8503d818b7cd96b95682e5970596790b364ea6a6, source fingerprint
4b829170d7c6dcfbb5bc04a713861c01217fd20b55997321bea69e431aceeb96
(the checker snapshots current dependency sources; different group receipts
reflect concurrent dependency work). Full report and stdout are repository-local
`scripts/.tmp/editor-final-freeze.json` and `editor-final-freeze.log`.

| Family | Passed | Failed | Blocked |
|---|---:|---:|---:|
| asm | 1 | 0 | 0 |
| blocker | 5 | 1 | 0 |
| cc-run | 8 | 0 | 0 |
| check | 15 | 0 | 0 |
| coverage | 118 | 7 | 0 |
| driver | 1 | 0 | 0 |
| events | 3 | 0 | 0 |
| frontend | 15 | 0 | 0 |
| hash | 5 | 0 | 0 |
| header | 1 | 0 | 0 |
| map | 9 | 5 | 0 |
| native | 13 | 0 | 0 |
| normalise | 19 | 5 | 0 |
| parse | 567 | 0 | 0 |
| recognise | 120 | 4 | 0 |
| run-oracle | 15 | 0 | 0 |
| run-program | 5 | 0 | 0 |
| seeds | 1 | 0 | 0 |
| state | 28 | 0 | 8 |
| step-check | 6 | 0 | 0 |
| tdl | 9 | 0 | 0 |
| trace | 3 | 0 | 0 |
| xrefs | 1306 | 0 | 0 |
| **Total** | **2273** | **22** | **8** |

Exact remaining red obligations (no other family is red):

| Family | Checks | Why |
|---|---|---|
| coverage (7) | §19.3, §19.4, §19.5, §19.6, §19.7, §19.8, §20 | coverage() hard-codes False despite added source/state/index evidence |
| normalise (5) | n-lower-widenable, n-dynamic-lane, n-byval-copy, n-rstep-return, n-platform-mmio | absent LLVM N0 lowering, dynamic lane chain, byval copy, R marks, platform routing/poll respectively |
| map (5) | binding-out-byte, binding-block-byte, binding-clock-read, binding-console-byte, indirectbr-two-blocks | OUT and indirectbr explicitly unimplemented; BLOCK/CLOCK/CONSOLE model prologues/interface/delivery absent |
| recognise (2) | validator-v4-residue, validator-v12-residue | ctlz(true) and unresolved L/R callee wrongly accept |
| recognise (1) | validator-v10-residue | literal V10 forbids half fneg, but retained-operation rules permit it; normative conflict 7u1 |
| recognise + blocker (2) | r-budget-prefix (one in each family) | materialised recognition only enabled for the hard-coded older r-fault-code id; new primitive use wrongly rejected as producer input |
| state (1 blocked) | r-budget-prefix | verdict ignored; still probes host fuel, which cannot establish typed fault 1 before the first effect |
| state (7 blocked) | driver-oracle-synthesis, driver-pointer-promotion, driver-comparison-layout, driver-snapshot-initializer, driver-closed-unit-fallback, driver-mixed-majors, platform-uart-write | actual driver/platform adapters absent; generic TDL/xam unavailable diagnostic, not missing published ISA commands |

All 567 LLVM parses pass. All 15 object checks and 15 run blocks pass, including
all six new objects. The entry replay object maps exactly. Previously passing
normalise/native/CC/R/TDL/trace families retain their earlier examples.

Group commits: 4e8de56 normalisation; c3977f9 validator/PT12; 2a0358a binding
objects/replay/indirectbr; 02ebe2a driver/platform; b7330de BLK-5 and V10 finding.
Tracking: notes on b-dialect-spec-1jb and b-dialect-spec-bz6; new bug
b-dialect-spec-7u1. All remain open because the freeze gate is not green.
Append-only checker questions Q9–Q13 (plus final Q14) record the required follow-up.
Generated .beads/issues.jsonl stays outside the owned-path commits.

## V10 post-round correction (2026-10-29, b-dialect-spec-7u1)

The coverage-follow-up reports above describe the pre-correction 0.2.1 baseline.
This correction resolves the normative conflict, not the other freeze-gate gaps.

Before editing, re-derived both readings by hand and recorded them in a Beads note:

- Literal V10: load half and bitcast are exceptions, but fneg half is not, so the
  old residue witness rejects. The same reading also excludes the retained
  fabs/copysign calls and extended-format calls, returns and aggregate transport.
  Removing those forms would contradict §13.1's unchanged row, §13.3's all-seven-
  format contract, §16's carrier map and NS §3.2's bit-exact promise. It narrows scope.
- Retained-operation reading: N32/N33 remove arithmetic/comparison/conversion;
  §13.1's bit operations and §16's transport remain. For half carrier bits b,
  fneg is b xor 0x8000, including NaNs. Residual fadd half must still reject:
  its materialised replacement uses __bennett_sf_add_f16 on i16 carriers.

Deciding sentence: **V10 must permit every bit-exact operation retained by §13.1
and every carrier transport admitted by §16, for all seven floating-point formats.**
Rule 10 selects the second reading; there are not two non-narrowing alternatives.

Edited only the V10 exception row, its explanation/witnesses and Appendix B,
plus the version labels required by spec/README.md and §23. The positive now
retains fneg half; the negative retains fadd half instead. New indexed
validator-v10-carriers accepts fabs/copysign plus defined-call/return/aggregate
transport. V4/V9/V12 still apply to calls. §13.1 and §16.4 are unchanged.
Full dialect and norm advance to 0.2.2 because a normative rejection changed;
unchanged sub-artefacts, ISA 0.8, map 0.2.1, reference objects and hashes stay put.

Verification, headless, project TMPDIR, Python -B, LLVM stdin/stdout only:

- Reproduced the pre-edit mismatch: old V10 residue declared reject, checker accepts.
- All 190 tagged LLVM blocks verify on LLVM 18/20/23: 570/570.
- All three V10 verdicts match the read-only checker: accept/reject/accept.
- Seven-format probes cover retained bit operations, load/store/select/phi,
  bitcast, parameters, defined calls, returns and aggregate field transport;
  each accepts, and its fadd variant rejects. All 14 modules verify on all
  three majors (42/42). These are supplemental probes, not new spec examples.
- Independent LLVM instcombine folds agree with b xor 0x8000 on ten half bit
  patterns per major (30/30), including signed zero, infinities and signaling/
  quiet NaNs with nonzero payloads.
- Current 0.2 cross-reference checker: 1310/1310. The legacy 0.1 helper reports
  the same seven failures as e74d70c; it is not the current cross-reference gate.

The full preflight was not run: it writes under checker-owned scripts/.tmp and
may build scripts/.isa-ref, which are read-only for this editor. Manifest/checker
version synchronization to 0.2.2 is tracked as b-dialect-spec-bvy for their owner;
SPEC_VERSIONS.toml and scripts were not edited. The full freeze gate is not
claimed green. Original finding 7u1 is resolved; no push. Beads export remains
outside the commits; the orchestrator owns the session worklog.

## Round-2 fixes

Tracking b-dialect-spec-1zy; draft/full norm 0.2.3, ISA 0.8.

| Item | Status | Commit group |
|---|---|---|
| SOL-R2-03 | resolved | f868741 |
| SOL-R2-04 | resolved | f868741 |
| R2-CODEX-04 | resolved | f868741 |
| REG-CODEX-N27 | resolved | f868741 |
| SOL-R2-02 | resolved | f868741 |
| R2-CODEX-02 | resolved | f868741 |
| R2-CODEX-01 | resolved | f868741 |
| SOL-R2-01 | resolved | 2fa3460 |
| REG-SOL-TDL9 | resolved | 2fa3460 |
| R2-CODEX-03 | resolved | 2fa3460 |
| BD3-1 | resolved | 2fa3460 |
| BD3-2 | resolved | 2fa3460 |
| BD3-3 | resolved | 2fa3460 |
| REG-MUSE-7.7 | resolved | 2fa3460 |
| BD3-6 | resolved | 2fa3460 |
| BD3-4 | resolved | a9e9563 |
| BD3-5 | resolved | a9e9563 |
| E-MUSE-TERM | resolved | a9e9563 |
| E-MUSE-7.7 | resolved | a9e9563 |

Group receipts: f868741 (vectors/materialisation/memory), 2fa3460 (action lifetimes).
BD3-5 uses the explicitly permitted conservative default, optional finite-bound refinement
b-dialect-spec-egm; external typed R semantics remain b-dialect-spec-bz6. No declines/partials.

## Round-2 final freeze — 2026-10-29

**2401/2401 passed; 0 failed; 0 blocked/unavailable.** Version 0.2.3,
ISA grading target 0.8. Tested spec/checker snapshot 5ba4b27427fefda4bde84218e9dbba0e2a7475f8.
Spec SHA-256 110c07deae4bf44cce7564f2149d9ad742c8135bd2ce8c788c12d4db74c0df0c.
Independent interpreter b7014019b2be1fed73b146823d08d7120baae23b, source fingerprint d2d8bfe19d97410f37b65125942d2db23852c4d7434ed0f84dda8fb88ddaa7c6.

| Family | Passed | Failed | Blocked |
|---|---:|---:|---:|
| asm | 1 | 0 | 0 |
| blocker | 15 | 0 | 0 |
| cc-run | 8 | 0 | 0 |
| check | 15 | 0 | 0 |
| coverage | 125 | 0 | 0 |
| driver | 1 | 0 | 0 |
| events | 3 | 0 | 0 |
| frontend | 21 | 0 | 0 |
| hash | 5 | 0 | 0 |
| header | 1 | 0 | 0 |
| map | 14 | 0 | 0 |
| native | 19 | 0 | 0 |
| normalise | 29 | 0 | 0 |
| parse | 606 | 0 | 0 |
| recognise | 127 | 0 | 0 |
| run-oracle | 15 | 0 | 0 |
| run-program | 5 | 0 | 0 |
| seeds | 1 | 0 | 0 |
| state | 44 | 0 | 0 |
| step-check | 6 | 0 | 0 |
| tdl | 10 | 0 | 0 |
| trace | 3 | 0 | 0 |
| xrefs | 1327 | 0 | 0 |
| **Total** | **2401** | **0** | **0** |


Exact headless freeze command (absolute paths):

```sh
env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER TMPDIR=/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp python3 /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/dialect_check_v02.py --json /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp/round2-fixes-freeze.json
```

36 checker unit tests pass via the repository unittest runner; pytest is not installed.
4 legacy runtime tests pass. No expectation weakened, no ISA source edited, no push.
Program-end fault release executes fresh-copy measurement and conditional correction/free
through Rust run-cc; superposed statistics and loop/deferred-channel checkpoints execute
through run-action. BLK-5 is a passing dependency verdict, not typed-fault execution on 0.8.
BD3-5 uses the explicitly permitted conservative default, not a claimed N=2 proof;
optional finite-bound refinement is b-dialect-spec-egm. No declines or partial resolutions.

## Round-3 council fixes — b-dialect-spec-zax

Theme A resolved SOL-R3-01, R3-CODEX-01, BD3-R3-1 and both regressions.
0.2.4 restores clean control workspace; B2 keeps its compute/out-of-place interface
and cannot invent a standalone inverse. Red-green loop unittest passed; new state
adapters execute Rust run-action and native exhaustive collision validation.
Full freeze pending the remaining themes; no green full-gate claim yet.

Theme B resolved R3-CODEX-02 / BD3-R3-2: deterministic latest-before-consumer
channel instrument. Red-green scheduler/state test passes on both council inputs.
Theme A commit 8e56d56; response 2412c4c.

Theme C resolved BD3-R3-3: CC covering stores preserve observation coverage;
applied events invalidate it. Native byte-level witness and mutation test added.
Theme B commit 5e13596; response df75746.

Theme D resolved BD3-R3-4: augmented interprocedural N29 continuation rule,
E(c) defined; actual recogniser red accept -> green BLK-1. Native fallback
witness uses two distinct live slots. Theme C 3303a5b / response c7523ab.

Theme E resolved SOL-R3-02: logical stack frame checks precede physical accesses,
charged materialised helper and replay metadata. Red-green state regression passes
on native push/pop/restore/replay and Rust helper. Theme D 1a511c5 / dd22119.

Theme F resolved SOL-R3-03: physical slots and generation identities separated;
N(s)=1 accepted stale-generation module traps 4 before changing the replacement,
equality false. Native original LLVM witness passes clang 18/23 and mutation test.
Theme E 90fa101 / response 9cc0bff.


Theme G resolved R3-CODEX-03: k=0 has one synthetic W_empty call using
one hidden target bit and the required four-wire fault register. The successful
terminal is charged const-zero/retval; the hidden bit is freed unconditionally.
Source-mapped Rust vectors verify void success (4 steps), budget-3 failure,
explicit fault 4, zero budget 1, and discarded non-void returns. A real CC
caller verifies clean free, exactly one call and controls 0/1. The inherited
null-target regression failed red before mapping support; result, budget,
cleanliness and call-count mutations are rejected. New marker descriptor stays
accepted. Full dialect/manifest/parser remain 0.2.4, ISA target 0.8.

Resumption findings: fixed the stale unittest's 0.2.3 positive flag and an
ambiguous ISA-draft section cross-reference. A native intentional SIGILL probe
could time out in systemd core-dump handling; a red-green child-process test
now verifies core dumps are disabled for deliberate fault probes only, retaining
the exact expected -4/132 statuses. A concurrent ISA HEAD change triggered the
existing fail-fast snapshot guard; verification is rerun on the latest snapshot.
Final freeze receipt follows after the full rerun; no final-green claim yet.


## Round-3 final freeze — 2026-10-30

**2466/2466 passed; 0 failed; 0 blocked/unavailable.** Full version
`0.2.4` (`dialect-0.2.4;isa-0.8`); ISA grading target remains 0.8.
Theme G and resumption fixes: 8d1517a6586a506488c4af7a9c35800c7053b508; A–F commits remain 8e56d56,
5e13596, 3303a5b, 1a511c5, 90fa101 and 111e889.
Spec SHA-256: `2ba040956ac8e22d11ff2bd4655d908b08de9d44564913a8b4f12c8a522fa156`.
Independent Rust interpreter: `92c26af045b816f5ef1e283a7b734aa244d8f320`;
immutable source fingerprint: `2dd454deeb8352a0b0e64ac1e61ddcc346ae5e2bdea59bd60440d35654946050`.
ISA HEAD remained at this revision throughout the successful freeze.
Machine-readable receipt: `scripts/dialect_check.LAST-RUN.json`.

| Family | Passed | Failed | Blocked |
|---|---:|---:|---:|
| asm | 1 | 0 | 0 |
| blocker | 16 | 0 | 0 |
| cc-run | 8 | 0 | 0 |
| check | 18 | 0 | 0 |
| coverage | 125 | 0 | 0 |
| driver | 1 | 0 | 0 |
| events | 3 | 0 | 0 |
| frontend | 21 | 0 | 0 |
| hash | 5 | 0 | 0 |
| header | 1 | 0 | 0 |
| map | 17 | 0 | 0 |
| native | 19 | 0 | 0 |
| normalise | 29 | 0 | 0 |
| parse | 624 | 0 | 0 |
| recognise | 130 | 0 | 0 |
| run-oracle | 18 | 0 | 0 |
| run-program | 5 | 0 | 0 |
| seeds | 1 | 0 | 0 |
| state | 52 | 0 | 0 |
| step-check | 6 | 0 | 0 |
| tdl | 10 | 0 | 0 |
| trace | 3 | 0 | 0 |
| xrefs | 1353 | 0 | 0 |
| **Total** | **2466** | **0** | **0** |


| Theme | Executed state witness | Status |
|---|---|---|
| A | co-loop-identity | passed |
| A | co-loop-adj-overwritten | passed |
| B | deferred-channel-adj-place | passed |
| C | co-observe-write-observe | passed |
| D | handle-setjmp-interproc | passed |
| E | shadow-stack-liveness | passed |
| F | handle-stale-generation | passed |
| G | oracle-empty-output | passed |


The G map/check/run families also execute oracle-empty-fault and
oracle-discard-return; oracle-empty-marker passes parse and recognition.
A–F witnesses are actual passing state rows in this receipt, not index-only
claims. The original co-loop-adjoint, deferred-channel-adj and other round-2
vectors remain executed. Named ISA dependency examples pass their specified
blocker verdicts; zero gate blockers does not claim those capabilities have
been added to ISA 0.8. No expectation was weakened and no ISA source was edited.

Exact freeze command:

```sh
env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER TMPDIR=/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp python3 /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/dialect_check_v02.py --json /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp/round3-fixes-freeze.json
```

44 checker unit tests and 4 legacy runtime unit tests pass headless. Full
version, SPEC_VERSIONS.toml and current/stale module-flag parsing agree on 0.2.4.
The deliberate-fault probe disables core dumps only; expected -4/132 exits
remain checked. The earlier stale-version test, ambiguous cross-reference,
concurrent ISA snapshot race and core-dump timeout were reproduced and fixed
or rerun; none is hidden in this receipt. All ten S0 findings and both regressions
are resolved, with theme A's single clean-workspace/U† reading stated above.
No decline, partial resolution, scope narrowing or push.

## Round-4 fixes — b-dialect-spec-5t7

SOL-R4-01 resolved: explicit two-stage borrow; n-wide-sub exact pair and clang 18/23 native vectors. Red unsupported sub → green exact unit regression. Full version/parser/manifest 0.2.5; final freeze follows after all five blockers.

SOL-R4-02 resolved: index-width GEP rows and CC/R/C agreement; n-gep-index Rust mapping executes truncation, negative offset, low wrap and constant-expression wrap. Native LLVM-fold/clang 18/23 checks the council truncation vector (clang overwrites custom layouts; LLVM18 constant folding does not correctly fold wrap). Red old-map 8589934592 vs 4294967296; green source-mapped interpreter regression with mutation. SOL-R4-01 commit bec39eb / response fc97aa7.

R4-CODEX-01 resolved: n-vector-i24 load/store at offsets 0/3, align 1; exact pair red → green and native clang18/23 both source/output pass; sentinels preserved. SOL-R4-02 commit 68d8f5b / response a285b98.

R4-CODEX-02 resolved: W=max(K,ceil(log2(L+1))), exact lane constants; n-narrow-lane extraction/insertion/four-lane alias probe red → green. Native clang18/23 source/output pass; n-dynamic-lane output 2/-1 both zero. R4-CODEX-01 commit 22d23e9 / response 29c3944.

BD3-R4-1 resolved: entry-boundary persistence forces infinity before per-entry TC/E; BLK-1/BLK-4 with existing fallback. handle-cross-entry recogniser red accept/N=1 → blocked:BD-B-ISA4; native actual LLVM across two entries has two distinct cleanly freed handles, no trap; mutation fails. Guaranteed-free and caller-free positives retained, R variant gets ISA12. R4-CODEX-02 commit 6663d8a / response ac2c64e. Full unit/gate verification follows.

Final review: the new shared vector-store path also needs packed sub-byte stores. A native source/materialised i1 boundary regression failed red (wrong byte range), then passed after packing eight bits into one byte, preserving the following sentinel. This is a supplemental R4-CODEX-01 check; all original witnesses remain. Preserve unchanged oracle-abi/tdl/effects subversions at 0.2.4; changed norm/handles/regions/map and full version are 0.2.5. BD3-R4-1 commit bdfa241 / response ba395b6. Initial whole gate 2514/2514; final rerun follows this review fix.

## Round-4 final freeze — 2026-10-30

**2514/2514 passed; 0 failed; 0 blocked/unavailable.**
Full version `0.2.5` (`dialect-0.2.5;isa-0.8`); ISA grading target 0.8.
50 checker unit tests and 4 legacy runtime tests pass headless.
Code/spec snapshot: `3e4c27e7fcdd21b59f32bde83b3d5f1e9441568f`.
Spec SHA-256: `c19dc84c476fe9a3c6ebb9cb621efd540a04aad05dd675a8ca78f3fd7f452d9a`.
Independent interpreter: `9e4984fc47587aa2dd501038b011dfc137449aae`; immutable source fingerprint:
`320982f83c264f805f06d2dc9730d87ba19e247d3485a40e11e8c4efc8b544cc`. Dependency HEAD matched at final verification.
Machine receipt: `scripts/dialect_check.LAST-RUN.json`; full executed rows:
`scripts/.tmp/round4-fixes-freeze.json`.

| Family | Passed | Failed | Blocked |
|---|---:|---:|---:|
| asm | 1 | 0 | 0 |
| blocker | 17 | 0 | 0 |
| cc-run | 8 | 0 | 0 |
| check | 18 | 0 | 0 |
| coverage | 125 | 0 | 0 |
| driver | 1 | 0 | 0 |
| events | 3 | 0 | 0 |
| frontend | 21 | 0 | 0 |
| hash | 5 | 0 | 0 |
| header | 1 | 0 | 0 |
| map | 17 | 0 | 0 |
| native | 24 | 0 | 0 |
| normalise | 33 | 0 | 0 |
| parse | 651 | 0 | 0 |
| recognise | 131 | 0 | 0 |
| run-oracle | 18 | 0 | 0 |
| run-program | 5 | 0 | 0 |
| seeds | 1 | 0 | 0 |
| state | 54 | 0 | 0 |
| step-check | 6 | 0 | 0 |
| tdl | 10 | 0 | 0 |
| trace | 3 | 0 | 0 |
| xrefs | 1361 | 0 | 0 |
| **Total** | **2514** | **0** | **0** |


| Blocker | Status | Dialect commit | Response commit |
|---|---|---|---|
| SOL-R4-01 | resolved | bec39eb | fc97aa7 |
| SOL-R4-02 | resolved | 68d8f5b | a285b98 |
| R4-CODEX-01 | resolved | 22d23e9 | 29c3944 |
| R4-CODEX-02 | resolved | 6663d8a | ac2c64e |
| BD3-R4-1 | resolved | bdfa241 | ba395b6 |

Supplemental packed-store regression/subversion receipt: 3e4c27e / 399962b.
No declines, partials, removed expectations, ISA edits or pushes. Named ISA
blocker examples pass their specified dependency verdicts; zero unavailable
checks does not claim ISA 0.8 gained dynamic register naming or R allocation.
New witnesses execute: n-wide-sub (normalise/native), n-gep-index
(normalise/native/state with Rust mapping), n-vector-i24 (normalise/native),
n-narrow-lane (normalise/native), handle-cross-entry (recognise/blocker/state).
Existing n-dynamic-lane output also executes natively at 0,1,2,-1.
The intermediate freeze failed one check because dependency HEAD moved during
its build; `scripts/.tmp/round4-freeze-head-race.json` preserves that result.
The full final rerun above supersedes it, with the guard retained unchanged.
External LLVM18 low-bit-wrap folding discrepancy is filed as
**b-dialect-spec-co5** for maintainer/upstream follow-up. The Rust-mapped wrap
and constant-expression witnesses execute the required high-bit-preserving
semantics; native LLVM-fold/clang18/23 probes execute the council truncation
case. This is not an unexecuted dialect witness or partial council resolution.

Exact final command:

```sh
env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER TMPDIR=/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp python3 /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/dialect_check_v02.py --json /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/scripts/.tmp/round4-fixes-freeze.json
```
