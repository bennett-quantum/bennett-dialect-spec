# Bennett LLVM Dialect — Specification, draft 0.2

**Date:** 2026-10-29. **Status:** draft 0.2 of `bennett-dialect-spec` (`Bennett-NorthStar.md`
§3, §6.1), written from the ratified outline `spec/outline-0.2.md` (maintainer rulings of
2026-10-29 at its end) for the first council round on 0.2; not yet graded. It replaces draft
0.1, which the narrowing audit (`docs/audit/2026-10-29-dialect-0.1-narrowing-audit.md`) found
to narrow north-star scope in 40 distinct places. Nothing is implemented. It targets the
Bennett virtual ISA **draft 0.8** (`bennett-isa-spec/spec/Bennett-ISA-Spec.md`, council
accepted 2026-10-28), cited "ISA §n", and is graded against ISA 0.8. MUST, MUST NOT, SHOULD and
MAY are normative; *(non-normative)* explains. Mechanics this draft does not settle carry a
**default** in §24; capabilities that ISA 0.8 cannot express in some case are **blockers** in
§25, each with the exact ISA change.

**Versioning.** Dialect 0.2: markers 0.2, handles 0.2, regions 0.2, oracle-abi 0.2, tdl 0.2,
effects 0.2, norm 0.2, map 0.2, asm 0.2, platform 0.2, driver 0.2, corpus 0.2; targets ISA 0.8.
The **full version string** (`0.2`) is the compatibility unit (§23): drafts are not compatible
with each other.

**Standing rule (CLAUDE.md rule 10; council rubric S0).** This document narrows no capability
that the north star promises (its thesis, §3–§5 and every rung of the §8 demo ladder; Grover
over unmodified SQLite is the core). It rejects at compile time only what the north star itself
requires to be rejected or what a maintainer decision settles; every such rejection is a row of
§22.1 citing the clause or decision. A deferral (§24) postpones mechanics only and states the
capability it keeps. Where ISA 0.8 cannot express a promised capability in some case, the
dialect still specifies the whole mechanism, states the ISA 0.8 realisation that exists for the
other cases, and names a blocker (§25) whose verdict is `blocked:`, never `reject:`.

**Sources.** North star §0, §3, §4, §5, §8; the legality spike and its findings
(`docs/spikes/2026-10-28-legality-findings.md`, decisions 1–4); the narrowing audit (row ids
D1–D25, B-01–B-55, O-01–O-08, G-12–G-16, ISA-1–ISA-11 are cited unchanged); the rung-4 spike
(`docs/spikes/sqlite/REPORT.md`, cited "SQLite §n"); the outline (cited "outline", decisions
B1–B17, questions E1–E14).

---

## 1. Scope and conformance

### 1.1 What the dialect is

The dialect is the contract between **front ends** that emit LLVM IR containing calls to
`__bennett_*` marker functions and the **plugin** that, at the final link of a whole program,
recognises those calls, analyses and normalises the code they reach, and maps it onto the ISA
(ISA §1.1). It fixes:

- the marker ABI, operand encodings and C header (§3);
- the processing order, execution tiers, polyvariant variants and function addresses (§4);
- the device analysis: points-to, value sets and every question answered from them (§5);
- the handle convention, provenance, comparison and collections of handles (§6);
- regions: kinds, candidate sets, dispatch, identity, well-formedness (§7);
- the oracle interface: the descriptor, parameter and device bindings, entry state, wide outputs
  and in-place updates (§8);
- budgets (§9);
- taint-driven lifting of classical code under control (§10);
- effects and device models per tier (§11);
- the materialised normalisation and the residual-poison validator (§12), floating point
  (§13), calls and control transfer (§14), inline asm and target intrinsics (§15);
- the lifting map from materialised LLVM to ISA objects (§16);
- the device classical memory model, CC and R lowering rules and fault outcomes (§17);
- a reference semantics from marker programs to the ISA formal model (§18);
- the driver's modes and plugin-invocation interface (§19);
- the platform profile `riscv64-bennett-virt` (§20);
- the legality corpus and conformance suites (§21); diagnostics (§22); versioning (§23);
  deferred mechanics (§24); blockers and ISA items (§25).

It does not fix the plugin's optimisation pipeline after normalisation, the plugin's device
objects beyond the constraints of §18.7, or any format the ISA owns.

### 1.2 Conformance classes

| Class | Who | Obligation |
|---|---|---|
| Producer | front ends (clang, rustc, Bennett.jl, importers) | emit modules that satisfy §3 and the outlining conventions of §7.6; never emit a reserved name of §3.1 other than a marker |
| Plugin | `bennett-plugin` and competitors | the processing order of §4.1; give every module the verdict the rules give it, with the diagnostics of §22; produce ISA objects whose execution equals the reference semantics (§18.7); suites DA–DX (§21.3) |
| Driver | `bennett-driver` | §19; links `bennett-runtimes` and `bennett-arith` bitcode of the link's LLVM major (§19.1); builds the comparison link and the native comparison binary (§17.7); emits blocker reports (§25) |
| Validator | the plugin's validator and `bennett-conformance` | the residual-poison validator (§12.4) and the reference recogniser (§3, §5, §6, §7), implemented independently; suites DA–DN |
| Runtime | `bennett-runtimes` and `bennett-arith` | define every entry point that §11, §13, §14, §17 and §20 name (prefixes `__bennett_rt_`, `__bennett_dev_`, `__bennett_sf_`, §3.1) with the semantics stated there, as ordinary bitcode compiled by the same pipeline; suites DR and DF |
| Platform | a platform profile of §20 | a board model plus shims satisfying §20; suite DP |

`scripts/dialect_check.py` in this repository is the seed of the pre-flight checker (§1.5). It
never bounds this document: an example it cannot yet execute fails the check (rule P-2, §1.5).

### 1.3 Relation to the ISA specification

The ISA is settled; this document never redefines it. Every ISA notion used here (tiers, wires,
`qreg` handles, oracles, actions, permutation actions, lprocs, F_B, budgets, tokens, fault
codes, the reference interpreter, interface and closure hashes, layouts, the launch ABI) has
exactly the meaning ISA §2–§17 give it. Where the dialect needs a construct ISA 0.8 lacks, this
document states (a) the full dialect mechanism, (b) its realisation on ISA 0.8 where one exists,
which may be a longer construction (an **efficiency item**, §25.3), and (c) otherwise a
**blocker** (§25.1) naming the exact ISA change. The dialect never shrinks to fit the ISA and
never extends the ISA unilaterally.

### 1.4 Departures from the north star

Only these remain. Every row of 0.1 §1.4 that narrowed scope (1.4-d, 1.4-e, 1.4-f) is deleted;
its replacement is §10, §9 and §8.7 respectively.

| North star | Dialect 0.2 | Why |
|---|---|---|
| §3.1 handle row: a handle through an `inttoptr`/`ptrtoint` round trip is rejected | Provenance flows through bitwise copies (§6.2) | Spike F1; maintainer decision 2; north-star amendment A2 (drafted with A1, bd `-25h`) |
| §3.1: regions entered as `__bennett_ctrl(q, @f, …)` with a constant `@f` | Region operands are classical data dispatched over a candidate set bounded by the program (§7.2) | Spike F3; maintainer decision 3 |
| Region named by symbol | Region identity is by content (§7.3) | Spike F2; maintainer decision 1 |
| §3.1 handle row is silent on comparison | `icmp eq/ne` of handles is identity (§6.3) | Maintainer decision 4 (2026-10-29; legality findings §3); a superset |
| §3.1, §4.2: a `qstore` into a register not known to be clean is a compile-time error | `qstore` is the ISA's XOR store; the compile-time rule is an optional warning `BD-W-QSTORE-UNCLEAN` (§6.7) | A register-granularity rule forbids the uncomputing second store; a superset of the north star (audit 1.4-g, D7) |
| §3.2: normalisation of "the outlined region" | Normalisation applies to every device variant (§12.1) | Device CC code is lowered to ISA CC, whose semantics differs from LLVM's poison semantics (ISA §4.1); a superset (audit 1.4-h) |

### 1.5 Notation and checked examples

LLVM IR is LLVM's textual form with opaque pointers, as accepted by LLVM 18, 20 and 23. `pw` is
the pointer width in bits of address space 0 in the module's datalayout (64 when the module has
no datalayout). Numbers are decimal unless written `0x…`. A(F) is the function address of §4.4.

**Process rules** (also in `spec/README.md`):

- **P-1.** Every mechanism rule id (the steps S1–S9, rules N1–N35, V1–V16, TDL-1–TDL-12, the
  points-to rules PT1–PT12, the binding kinds of §8.2, the transforms of §14, the map rows of
  §16.4) has at least one checked `accept` example; every compile-time rejection of §22.1 has
  one `reject` example; every blocker of §25.1 has one `blocked` example. Appendix B is the
  index, and the checker derives it from the text: a rule id with no example fails the check.
- **P-2.** An example that the checker cannot yet execute **fails** the check with
  `checker-unimplemented: <capability>`. It is never skipped, and this document never removes
  or weakens an example to make the checker pass. The freeze gate is an all-green check.
- **P-3.** Every executed result comes from an independent executor: LLVM tools, natively built
  binaries, or the Rust ISA reference interpreter `bennett-isa-ref`. Python computes only
  *expected* artefacts (recogniser verdicts, normaliser output, map output, TDL events), and is
  never both producer and judge of one example.

Every fenced block whose info string starts with `llvm`, `isa`, `c`, `rust`, `julia`, `json` or
`text` followed by a tag below is a **checked example**. Its attributes are `key=value` pairs.
The last column names the checker capability (Appendix B) and, where the ISA reference
interpreter is the executor, the `bennett-isa-ref` command (`check`, `hash`, `run-oracle`,
`step-check` exist; `run-cc`, `reverse`, `run-action`, `run-program` are requested,
bd `b-isa-spec-xam`).

| Tag | Meaning; what the checker does | Capability / command |
|---|---|---|
| `llvm markers-ir` | the marker list of §3.2; compared with the C view | `parse`, `header` |
| `c markers-c` | the prototypes of the C header; byte-equal to `spec/bennett_markers.h` between its BEGIN/END PROTOTYPES lines | `header` |
| `llvm example=ID verdict=V` | a module; it parses and verifies on LLVM 18, 20 and 23 and the reference recogniser gives verdict `V` (`accept`, `reject:<code>` or `blocked:<code>`, §1.6). Optional attributes: `candidates=f,g` (the resolved candidate set of the first region operand, §7.2), `callees=f,g` (the candidate set of the first indirect call, §14.2), `shapes=N` (the number of compiled oracle shapes, §8.4), `mode=validate` (validator only, §12.4) | `parse`, `recognise` |
| `llvm normalise-in=ID` / `llvm normalise-out=ID` | the normaliser (§12) applied to the first gives the second, lines compared after collapsing runs of blanks; both verify on the three majors; the second passes the validator | `parse`, `normalise` |
| `text native=ID` | inputs and outputs of the native differential of a normalisation pair or a lifted example: both modules (or the C source and the module) built natively with the seeds of `spec/seeds/` (§21.4), run on the listed inputs, outputs equal to the listed values | `native` |
| `llvm lift=ID` | a materialised module; attribute `region=@f` names the region function and `desc=` the binding shape (§16.1) | `parse`, `map` |
| `isa object=ID` | the reference object (§16.2) that the map produces from `lift=ID`, as complete ISA text; byte-equal to the map output; `bennett-isa-ref check` accepts it | `map`, `check` |
| `text hash=ID` | the interface hashes of the object's symbols (`bennett-isa-ref hash`) | `hash` |
| `text run=ID` | lines `input=… [mem=name:hex] [arg=…] budget=s,h,st,d -> code=C payload=P steps=N`; each line is the output of `bennett-isa-ref run-oracle <object> ref` with those options | `run-oracle` |
| `text step-check=ID` | a prefix-reversal claim; the output of `bennett-isa-ref step-check <object> ref --exhaustive` with the stated options | `step-check` |
| `text inplace=ID` | an in-place verification verdict (§8.7) | `run-oracle` |
| `llvm semantics=ID corpus=NAME` | a marker program; byte-equal to `corpus/legality/cases/NAME.ll`; run through the trace runtime and the reference semantics (§18) | `trace`, `run-action` |
| `text events=ID` / `text state=ID` | the event list (§18.2) of a marker program on an input, and the state vector before event `at` | `trace`, `run-action` |
| `text tdl=ID` | the TDL partition (§10, TDL-3) and generated event list of an action region invocation | `tdl`, `run-action` |
| `text cc-run=ID` | a CC or R run: results, fault records, tape, and the state after `bennett_reverse` | `run-cc`, `reverse` |
| `text blocker=ID` | the blocker report (§25.1) the plugin emits for a `blocked:` example | `recognise` |
| `json budget-table=ID` | a budget table (§9.2); parsed and resolved against the example it names | `driver` |
| `c example=ID`, `rust example=ID`, `julia example=ID` | a source file compiled by the toolchains of `corpus/legality/toolchains.toml` (`clang -O2 -flto` on 18, 20, 23; `rustc --emit=llvm-bc`; Julia `code_llvm`) and then `lto<O3>`; the result is recognised with verdict `verdict=V` | `frontend`, `recognise` |

A module example that calls a marker or a primitive without declaring it implicitly contains
its declaration (§3.2, §3.1). **Section references**: `§n` is a section of this document, `ISA
§n` of the ISA specification, `NS §n` of `Bennett-NorthStar.md`; a reference that continues a
list (`ISA §4.7, §5.3`) names the same document as the reference before it. Fenced blocks
without a tag are illustrations and are non-normative; an `llvm` or `isa` block without a tag is
an error of this document.

### 1.6 Diagnostics and verdicts

A module's **verdict** is one of:

- `accept`: the plugin produces its objects;
- `reject:<code>`: a compile-time rejection of §22.1. The plugin MUST fail the compilation
  (nonzero exit, no output object) and report at least the first diagnostic in the processing
  order of §4.1;
- `blocked:<code>`: the module is accepted by the dialect, but at least one program point needs
  a capability that ISA 0.8 cannot express (§25.1). The plugin MUST produce its objects with
  every such point lowered to a **blocker trap** (§25.1: a run-time fault on exactly the
  executions that reach the point), MUST emit the blocker report of §25.1 and MUST exit with the
  distinct status 3. The code is the first blocker report in processing order.

A module that would be rejected and blocked is rejected. Warnings (`BD-W-*`, §22.3) never change
a verdict.

## 2. Terminology

- **Marker**: one of the 23 functions of §3.2. **Marker call**: a `call` or `invoke` whose
  callee is a marker (§3.5). **Effect marker**: one of the five `__bennett_effect_*` markers.
- **Primitive**: a reserved function with prefix `__bennett_nz_` that the map lowers to an ISA
  instruction directly (§3.1, §16.4): `__bennett_nz_fault`, `__bennett_nz_alloc`,
  `__bennett_nz_free`. **Runtime entry point**: a function with prefix `__bennett_rt_`,
  `__bennett_dev_` or `__bennett_sf_` that `bennett-runtimes` or `bennett-arith` defines in
  bitcode (§3.1).
- **Handle**: the `ptr` value a `__bennett_qalloc` or `__bennett_qborrow` call returns; it
  denotes a **register** of n qubits, the ISA's `qreg[n]` (ISA §3.3). Qubit `i` of a handle is a
  **wire**. **Register id**: the 64-bit value that represents a handle in memory and at the
  host–device boundary (§6.1).
- **Root**: an allocation of a register, identified by its allocation site and dynamic instance
  index (§6.5). **Handle-derived**: a value whose provenance (§6.2) contains a root.
- **Region function**: a function a region-entry marker receives. **Region operand**: the marker
  operand that names it. **Candidate set**: the functions a region operand can denote (§7.2).
- **Action region**: a candidate of a `ctrl`, `adj` or `compute` operand; its interface is a
  quantum action (ISA §5.3). **Oracle region**: a candidate of an `oracle` or `inplace` operand;
  its interface is a lifted oracle (ISA §5.2). **Reversible region**: a candidate of a
  `reversible` operand, or the whole-program entry of §19.2; R-tier code (ISA §3.1).
- **Tier** of a function variant: **H** (host, native), **CC** (device classical control, ISA
  §3.1), **R** (reversible, ISA §3.1), **L** (lifted: an lproc or oracle body, ISA §3.7). A
  **variant** is a (function, tier, coherence signature) triple (§4.3); host code keeps the
  original function, every device tier gets a clone.
- **Device program**: every variant of tier CC, R or L. **Device entry**: a device variant
  called by an H function (a launch, ISA §10).
- **Function address** A(F): the address of F in the driver's comparison link (§4.4).
- **Abstract object**, **slot**, **value set**: §5. ⊤ is the unbounded value set.
- **Descriptor**: the in-memory oracle interface record of §8.1. **Binding**: one parameter or
  device entry of a descriptor. **Shape**: a tuple of binding kinds, modes and widths (§8.4).
- **Budget record**: the in-memory record `bennett_budget` of §9.1. **Budget table**: the driver
  input of §9.2.
- **Coherence state**: Cl (classical) or Co (coherent) of a value or object instance (§10,
  TDL-2). **Coherent slice**: an outlined maximal region of Co instructions (TDL-3).
  **Arena**: the coherent memory of §10 TDL-4. **Generation**: the classical execution of an
  action region that records its events (§18.4).
- **Device model**: one of `console`, `clock`, `entropy`, `block` (ISA §7.3), realised per tier
  by §11.
- **Coverage classes** (ISA §13): **lowered** (the construct has an ISA realisation),
  **shimmed** (it is replaced by a runtime or platform shim with a recorded `shim_hash`),
  **trapped** (it faults with code 8, `FAULT_EFFECT_UNMODELLED`, on the executions that reach it,
  and has a coverage line).
- **Driver mode**: one of the invocation modes of §19.2–§19.7. **Platform profile**: §20.
- **Materialised module**: the module after normalisation (§12). **Reference object**: the ISA
  object the map produces for one oracle shape (§16.2); its oracle `@ref` defines F_B.
- **Blocker**: a capability with no ISA 0.8 realisation in a stated case (§25.1), BLK-1 to
  BLK-4.

## 3. The marker ABI (markers 0.2)

### 3.1 Reserved names

Every function or global name that starts with `__bennett_` is reserved. The reserved names
other than the markers of §3.2 are:

| Prefix | Who defines | Who may reference it |
|---|---|---|
| `__bennett_nz_` | nobody: **primitives**, lowered by the map (§16.4) and the CC/R lowering (§17.4) | the normaliser (§12) and runtimes bitcode |
| `__bennett_sf_` | `bennett-arith` bitcode (§13) | the normaliser and runtimes bitcode |
| `__bennett_rt_` | `bennett-runtimes` bitcode (§11, §14, §17, §20) | the normaliser, the driver's synthesised code (§19) and runtimes bitcode |
| `__bennett_dev_` | `bennett-runtimes` bitcode: device-model entry points and device state (§11.3) | the plugin's L lowering of effect markers and runtimes bitcode |

The primitives are exactly:

```
declare void @__bennett_nz_fault(i64 %code)    ; fault with code C (§12.3)
declare ptr  @__bennett_nz_alloc(i64 %n)       ; ISA alloc / lift.alloc (§17.1)
declare void @__bennett_nz_free(ptr %p)        ; ISA free / lift.free
```

A **producer input** is a bitcode file given to the driver other than `bennett-runtimes` and
`bennett-arith` bitcode. A producer input:

1. MUST NOT define (`define`) a function whose name is a marker or a reserved name
   (`BD-E-MARKER-DEFINED`);
2. MUST NOT declare, define or reference a reserved name that is not a marker
   (`BD-E-MARKER-UNKNOWN`);
3. MUST NOT use a marker other than as the callee of a call or invoke (`BD-E-MARKER-ADDRESS`):
   no stored, compared, passed or cast marker address, so that no marker is ever called
   indirectly.

The driver checks rules 1–3 on every producer input before linking; the plugin checks rules 1
and 3 on the linked module, and, in closed-unit mode (§19.7), all three on its input. Checked
examples are producer inputs. `__bennett_ctrl_v`, the variadic probe of the spike ABI v0, is
not a marker; it is rejected by rule 2. *(non-normative)* The legality corpus's trace runtime
defines markers; it is a test harness, never a production link input (§19.9).

### 3.2 The marker list

The normative IR signatures (return type, name, parameter types; parameter names are
documentation):

```llvm markers-ir
declare ptr @__bennett_qalloc(i64 %cls, i64 %n)
declare ptr @__bennett_qborrow(i64 %cls, i64 %n)
declare void @__bennett_qfree(ptr %h)
declare void @__bennett_gate(i32 %op, ptr %h, i64 %i)
declare void @__bennett_gate2(i32 %op, ptr %a, i64 %i, ptr %b, i64 %j)
declare void @__bennett_gate3(i32 %op, ptr %a, i64 %i, ptr %b, i64 %j, ptr %c, i64 %k)
declare void @__bennett_rot(i32 %op, ptr %h, i64 %i, double %theta)
declare i1 @__bennett_measure(ptr %h, i64 %i)
declare void @__bennett_qload(ptr %dst, ptr %mem, ptr %addr)
declare void @__bennett_qstore(ptr %mem, ptr %addr, ptr %val)
declare void @__bennett_qprep(ptr %h, ptr %src, i64 %nbytes)
declare void @__bennett_observe(ptr %p, i64 %len)
declare void @__bennett_ctrl(ptr %q, i64 %qi, ptr %f, ptr %budget, ptr %env)
declare void @__bennett_adj(ptr %f, ptr %budget, ptr %env)
declare void @__bennett_compute(ptr %f, ptr %use, ptr %budget, ptr %env)
declare void @__bennett_reversible(ptr %f, ptr %budget, ptr %env)
declare void @__bennett_oracle(ptr %f, ptr %budget, ptr %desc)
declare void @__bennett_inplace(ptr %g, ptr %ginv, ptr %budget, ptr %desc)
declare void @__bennett_effect_console_write(ptr %p, i64 %len)
declare void @__bennett_effect_clock_read(ptr %p)
declare void @__bennett_effect_entropy_read(ptr %p, i64 %len)
declare void @__bennett_effect_block_read(i64 %sector, ptr %p)
declare void @__bennett_effect_block_write(i64 %sector, ptr %p)
```

Operand roles, by marker (positions are 0-based). "Dispatched" operands are classical values
whose value set (§5.3) selects among compiled alternatives (§3.4); "memory" operands point into
classical memory.

| Marker | Handle operands | Region operands (kind) | Dispatched operands | Budget | Descriptor | Other |
|---|---|---|---|---|---|---|
| `qalloc`, `qborrow` | – | – | 0 `cls`, 1 `n` | – | – | – |
| `qfree` | 0 | – | – | – | – | – |
| `gate` | 1 | – | 0 `op` | – | – | 2 index |
| `gate2` | 1, 3 | – | 0 `op` | – | – | 2, 4 indices |
| `gate3` | 1, 3, 5 | – | 0 `op` | – | – | 2, 4, 6 indices |
| `rot` | 1 | – | 0 `op` | – | – | 2 index, 3 angle |
| `measure` | 0 | – | – | – | – | 1 index |
| `qload`, `qstore` | 0, 1, 2 | – | – | – | – | – |
| `qprep` | 0 | – | – | – | – | 1 memory (source bytes), 2 byte count |
| `observe` | – | – | – | – | – | 0 memory, 1 byte count |
| `ctrl` | 0 | 2 (action) | – | 3 | – | 1 index, 4 env |
| `adj` | – | 0 (action) | – | 1 | – | 2 env |
| `compute` | – | 0, 1 (action) | – | 2 | – | 3 env |
| `reversible` | – | 0 (reversible) | – | 1 | – | 2 env |
| `oracle` | (in the descriptor) | 0 (oracle) | – | 1 | 2 | – |
| `inplace` | (in the descriptor) | 0, 1 (oracle) | – | 2 | 3 | – |
| `effect_console_write` | – | – | – | – | – | 0 memory, 1 length |
| `effect_clock_read` | – | – | – | – | – | 0 memory (8 bytes) |
| `effect_entropy_read` | – | – | – | – | – | 0 memory, 1 length |
| `effect_block_read`, `effect_block_write` | – | – | – | – | – | 0 sector, 1 memory (512 bytes) |

Changes from 0.1 and from the spike ABI v0 (`corpus/legality/markers.h`): `qalloc`, `qborrow`,
`qfree`, `gate`, `gate2`, `rot`, `measure`, `qload` and `qstore` keep their v0 signatures, so
the spike evidence applies to them unchanged; `gate3` is unchanged from 0.1; every region-entry
marker now takes a budget record (§9.1); `oracle` and `inplace` take a descriptor (§8.1) in
place of 0.1's handle operands; `qprep`, `observe` and the five effect markers are new. The
positive legality requirement (§3.6) is a property of unknown external calls, not of a
signature, but every changed or new marker gets legality corpus cases before this version
freezes (§21.2, bd `-566`).

**Meaning in brief** (the rules are in the sections named):

- `qprep(h, src, n)`: for every k < n and j < 8, wire 8k + j of h ⊕= bit j of byte `src[k]`;
  n ≤ n(h)/8 (else `T-SIZE`). A copy when h is clean; self-inverse. It is how data "fixed
  classically before entry" (NS §4.2, §8 rung 4) reaches a register (§8.5, §17.4); one `gate`
  per set bit would need about 1.3·10^8 marker calls for the rung-4 image.
- `observe(p, len)`: a computational-basis measurement of the classical bytes [p, p + len)
  whose coherence state is Co (§10, TDL-11); afterwards they are Cl and hold the outcome. It is
  the only way superposed classical memory reaches classical code (NS §4.2: "outputs leave
  through measurement after exit"). On Cl bytes it does nothing.
- the effect markers: one per ISA device-model operation (ISA §7.3), realised per tier by §11.
  `bennett-runtimes` calls them from its musl, Julia and platform shims; ordinary programs may
  call them directly.

### 3.3 C header view

`spec/bennett_markers.h` is the normative C and C++ header. Its prototypes (in C++ each carries
`noexcept`, which makes clang add `nounwind`, a permitted attribute, and emit `call` rather than
`invoke`):

```c markers-c
bennett_q __bennett_qalloc(uint64_t cls, uint64_t n) BENNETT_NOEXCEPT;
bennett_q __bennett_qborrow(uint64_t cls, uint64_t n) BENNETT_NOEXCEPT;
void __bennett_qfree(bennett_q h) BENNETT_NOEXCEPT;
void __bennett_gate(uint32_t op, bennett_q h, uint64_t i) BENNETT_NOEXCEPT;
void __bennett_gate2(uint32_t op, bennett_q a, uint64_t i, bennett_q b, uint64_t j) BENNETT_NOEXCEPT;
void __bennett_gate3(uint32_t op, bennett_q a, uint64_t i, bennett_q b, uint64_t j, bennett_q c, uint64_t k) BENNETT_NOEXCEPT;
void __bennett_rot(uint32_t op, bennett_q h, uint64_t i, double theta) BENNETT_NOEXCEPT;
bool __bennett_measure(bennett_q h, uint64_t i) BENNETT_NOEXCEPT;
void __bennett_qload(bennett_q dst, bennett_q mem, bennett_q addr) BENNETT_NOEXCEPT;
void __bennett_qstore(bennett_q mem, bennett_q addr, bennett_q val) BENNETT_NOEXCEPT;
void __bennett_qprep(bennett_q h, const void *src, uint64_t nbytes) BENNETT_NOEXCEPT;
void __bennett_observe(void *p, uint64_t len) BENNETT_NOEXCEPT;
void __bennett_ctrl(bennett_q q, uint64_t qi, bennett_region f, const bennett_budget *budget, void *env) BENNETT_NOEXCEPT;
void __bennett_adj(bennett_region f, const bennett_budget *budget, void *env) BENNETT_NOEXCEPT;
void __bennett_compute(bennett_region f, bennett_region use, const bennett_budget *budget, void *env) BENNETT_NOEXCEPT;
void __bennett_reversible(bennett_region f, const bennett_budget *budget, void *env) BENNETT_NOEXCEPT;
void __bennett_oracle(const void *f, const bennett_budget *budget, const bennett_oracle_desc *desc) BENNETT_NOEXCEPT;
void __bennett_inplace(const void *g, const void *ginv, const bennett_budget *budget, const bennett_oracle_desc *desc) BENNETT_NOEXCEPT;
void __bennett_effect_console_write(const void *p, uint64_t len) BENNETT_NOEXCEPT;
void __bennett_effect_clock_read(void *p) BENNETT_NOEXCEPT;
void __bennett_effect_entropy_read(void *p, uint64_t len) BENNETT_NOEXCEPT;
void __bennett_effect_block_read(uint64_t sector, void *p) BENNETT_NOEXCEPT;
void __bennett_effect_block_write(uint64_t sector, const void *p) BENNETT_NOEXCEPT;
```

The header also defines:

- `typedef struct bennett_q_opaque *bennett_q;` and `typedef void (*bennett_region)(void *env);`;
- `bennett_budget` (§9.1), `bennett_bind`, `bennett_devbind` and `bennett_oracle_desc` (§8.1),
  and the macro `BENNETT_ORACLE_DESC(NP, ND)` that declares a descriptor with NP parameter and
  ND device bindings;
- `bennett_oracle_desc_init(d, np, nd, tgt, fault)`, a macro that sets the header fields by
  plain stores, so that producers build descriptors by constant stores (§8.1);
- the operation codes of §3.4 and the constants of §8 and §9.

Clang lowers C `bool` to `zeroext i1`, which §3.6 admits. The checker compiles the header with
clang 18, 20 and 23 and compares every prototype's IR signature with §3.2.

### 3.4 Operand encodings

**Operation codes** (`op`):

| Marker | Code | Operation | ISA realisation (ISA §4.4) |
|---|---|---|---|
| `gate` | 1 | X | `x` |
| `gate` | 2 | H | `h` |
| `gate` | 3 | S | `s` |
| `gate` | 4 | S† | `sdg` |
| `gate` | 5 | T | `t` |
| `gate` | 6 | T† | `tdg` |
| `gate` | 7 | Z | `s` then `s` (S² = Z exactly) |
| `gate` | 8 | Y | `sdg` then `x` then `s` (S·X·S† = Y exactly) |
| `gate2` | 1 | CX, `a` control, `b` target | `cx` |
| `gate2` | 2 | CZ | `cz` |
| `gate2` | 3 | SWAP | `swap` |
| `gate3` | 1 | CCX, `a`, `b` controls, `c` target | `ccx` |
| `rot` | 1 | RX(θ) | `rx θ` |
| `rot` | 2 | RY(θ) | `ry θ` |
| `rot` | 3 | RZ(θ) | `rz θ` |

"Then" is time order. The realisations are exact including global phase, so Z and Y stay exact
under control.

**Classes** (`cls`). `cls` = 0 denotes the ISA class `any` (ISA §4.3). `cls` = k ≥ 1 denotes
entry k (1-based) of the link's **class-name table**: the names of the module flags
`!"bennett.classes"` (behaviour `AppendUnique`, a list of strings) of every input, in order of
first appearance in the driver's link order, followed by the names given with
`--bennett-class=<name>` (§19.9) that are not already present. The driver writes the table into
the object's class references (ISA §4.3 `qalloc cls n`, §3.3 `qreg.new cls n`); a name the
target does not declare is an ISA load error (ISA §8.3 `classes`), not a dialect error.

**Width** (`n`): the number of qubits, ≥ 1. **Indices**: classical values; an index ≥ n(h)
traps (`T-INDEX`, §18.3). **Angle**: a classical `double` (soft-float bits, §13); a non-finite
angle traps (`T-THETA`).

**Constant and run-time operands.** A dispatched operand (role table, §3.2) is classical data.
Its value set VS(v) is computed by §5.3. The plugin compiles one alternative per member of the
**dispatch domain** and selects among them at run time with the compare tree of §14.2:

- `op`: the dispatch domain is VS(op) when it is finite, else the marker's whole code table.
  A run-time value outside the table traps (`T-OP`).
- `cls`: VS(cls) when finite, else {0} ∪ every index of the class-name table. A value outside
  traps (`T-CLASS`).
- `n`: VS(n) when finite (constants, `range` attributes and metadata, known bits, `select`,
  `phi`, loads from constant tables, §5.3). A value 0 at run time traps (`T-SIZE`). When VS(n)
  is ⊤, ISA 0.8 has no register of run-time width: the verdict is `blocked:BD-B-ISA4` (BLK-1,
  §25.1) and the blocker report names the value.

A **constant** operand outside its table (an `op` code not in the table, a constant `cls`
beyond the class-name table, a constant `n` = 0) is `BD-E-OPERAND`: the program traps at that
marker on every execution that reaches it, so the rejection is fail-fast for an always-failing
call (§22.1). Under coherent control (a Co operand, §10 TDL-10) the same domains apply.

The `cfg-switch-op-table` shape (`default<O3>` sinks seven gate calls into one with a phi of
operation codes) is accepted, as are operation codes loaded from a constant table (SimplifyCFG's
switch-to-lookup on the `op` operand):

```llvm example=operand-phi-codes verdict=accept
define void @top(i1 %c) {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  br i1 %c, label %a, label %b

a:
  br label %j

b:
  br label %j

j:
  %op = phi i32 [ 2, %a ], [ 7, %b ]
  call void @__bennett_gate(i32 %op, ptr %h, i64 0)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=operand-code-table verdict=accept
@switch.table.ops = private unnamed_addr constant [3 x i32] [i32 1, i32 2, i32 5]

define void @top(i64 %i) {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %k = urem i64 %i, 3
  %p = getelementptr [3 x i32], ptr @switch.table.ops, i64 0, i64 %k
  %op = load i32, ptr %p
  call void @__bennett_gate(i32 %op, ptr %h, i64 0)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

A gate-list interpreter that reads its operation codes from host input is accepted: the code
is dispatched over the whole `gate` table, and a code outside it traps (`T-OP`) on that
execution only:

```llvm example=operand-runtime-op verdict=accept
define void @interp(i32 %op) {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  call void @__bennett_gate(i32 %op, ptr %h, i64 0)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=operand-bad-code verdict=reject:BD-E-OPERAND
define void @top() {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  call void @__bennett_gate(i32 99, ptr %h, i64 0)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

A class named by the module flag is entry 2 of this module's class-name table:

```llvm example=operand-class verdict=accept
define void @top() {
  %h = call ptr @__bennett_qalloc(i64 2, i64 3)
  call void @__bennett_qfree(ptr %h)
  ret void
}

!llvm.module.flags = !{!0}
!0 = !{i32 6, !"bennett.classes", !1}
!1 = !{!"fast", !"slow"}
```

A width bounded by a mask has a finite value set: `and` with 7 gives {0, …, 7} and the `add`
gives VS(%n) = {1, …, 8}; the plugin compiles one static register per member and dispatches
(§6.5). A width from host input with no bound is blocked (BLK-1):

```llvm example=operand-width-masked verdict=accept
define void @top(i64 %m) {
  %k = and i64 %m, 7
  %n = add i64 %k, 1
  %h = call ptr @__bennett_qalloc(i64 0, i64 %n)
  call void @__bennett_gate(i32 2, ptr %h, i64 0)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=operand-width-host verdict=blocked:BD-B-ISA4
define void @top(i64 %n) {
  %h = call ptr @__bennett_qalloc(i64 0, i64 %n)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```text blocker=operand-width-host
BD-B-ISA4 @top %h: qalloc operand n has value set TOP (parameter of an externally visible function); ISA 0.8 qreg[n] needs a literal n; BLK-1 (ISA-4) qreg[*]
```

### 3.5 Recognition

A call or invoke instruction is a **marker call** iff its callee operand is the function itself
(not a loaded or cast value) and that function's name is exactly a marker name. Names are
compared byte for byte; no prefix, suffix or demangled match is made. A marker call is accepted
iff all of the following hold; otherwise `BD-E-MARKER-SIGNATURE`:

1. the declaration's function type is exactly the marker's IR signature, **or** is the
   unprototyped form `R (...)` with R the marker's return type (a C declaration without a
   prototype, spike case `c-unprototyped-decl`);
2. the call instruction's function type is exactly the marker's IR signature, **or**, only when
   the declaration is unprototyped, the marker's parameter list followed by `...`;
3. the call passes exactly as many arguments as the signature has parameters;
4. the calling convention is the default C convention and the call has no operand bundles.

Attributes and metadata are not part of the comparison; they are governed by §3.6.

```llvm example=recog-unprototyped verdict=accept
declare ptr @__bennett_qalloc(...)
declare void @__bennett_gate(...)
declare void @__bennett_qfree(...)

define void @kr() {
  %h = call ptr (i64, i64, ...) @__bennett_qalloc(i64 0, i64 1)
  call void (i32, ptr, i64, ...) @__bennett_gate(i32 2, ptr %h, i64 0)
  call void (ptr, ...) @__bennett_qfree(ptr %h)
  ret void
}
```

The same program passing an `int` index without a cast gives an `i32` argument and is
rejected:

```llvm example=recog-unprototyped-wrong-type verdict=reject:BD-E-MARKER-SIGNATURE
declare ptr @__bennett_qalloc(...)
declare void @__bennett_gate(...)
declare void @__bennett_qfree(...)

define void @kr() {
  %h = call ptr (i64, i64, ...) @__bennett_qalloc(i64 0, i64 1)
  call void (i32, ptr, i32, ...) @__bennett_gate(i32 2, ptr %h, i32 0)
  call void (ptr, ...) @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=recog-measure-i8 verdict=reject:BD-E-MARKER-SIGNATURE
declare i8 @__bennett_measure(ptr, i64)

define i8 @m() {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %b = call i8 @__bennett_measure(ptr %h, i64 0)
  call void @__bennett_qfree(ptr %h)
  ret i8 %b
}
```

A 0.1-style `ctrl` with an `i64` budget no longer has the marker's signature:

```llvm example=recog-ctrl-01 verdict=reject:BD-E-MARKER-SIGNATURE
declare void @__bennett_ctrl(ptr, i64, ptr, i64, ptr)

define internal void @body(ptr %e) {
  ret void
}

define void @top(ptr %e) {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  call void @__bennett_ctrl(ptr %h, i64 0, ptr @body, i64 -1, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=recog-ctrl-v verdict=reject:BD-E-MARKER-UNKNOWN
declare void @__bennett_ctrl_v(ptr, i64, ptr, i64, ...)

define void @v(ptr %e) {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr %h, i64 0, ptr null, i64 8, i32 1)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=recog-address-taken verdict=reject:BD-E-MARKER-ADDRESS
@table = global ptr @__bennett_gate
```

```llvm example=recog-defined verdict=reject:BD-E-MARKER-DEFINED
define void @__bennett_qfree(ptr %h) {
  ret void
}
```

A producer input may not reference a runtime entry point:

```llvm example=recog-runtime-name verdict=reject:BD-E-MARKER-UNKNOWN
declare void @__bennett_rt_memmove(ptr, ptr, i64)

define void @f(ptr %d, ptr %s) {
  call void @__bennett_rt_memmove(ptr %d, ptr %s, i64 8)
  ret void
}
```

### 3.6 The positive legality requirement and attributes

A marker is an external declaration that may read and write any memory, may unwind and may not
return: exactly an unknown external function to LLVM. Stock passes then preserve the dynamic
sequence of marker calls on every executed path (spike findings §1: every standard pipeline of
LLVM 18, 20 and 23, all 50 legal cases; the four negative controls are detected). No attribute
is needed and none may be added that licenses elimination, commoning, speculation or motion.

Every attribute, keyword and calling convention on a marker declaration or marker call site is
in exactly one of three lists:

- **Forbidden** (`BD-E-MARKER-ATTRIBUTE`): attributes that license motion or elimination:
  `memory(...)` in any form, `readnone`, `readonly`, `writeonly`, `argmemonly`,
  `inaccessiblememonly`, `inaccessiblemem_or_argmemonly`, `willreturn`, `speculatable`,
  `noreturn`, `returned`, `nocapture`, `captures(...)`, `dereferenceable(...)`,
  `dereferenceable_or_null(...)`, `align`, `nofpclass(...)`, `byval`, `sret`, `writable`,
  `initializes(...)`, `dead_on_unwind`, `nosync`, `nofree`, `norecurse`, `mustprogress`,
  `musttail`, any non-default calling convention, `extern_weak` linkage. *(non-normative)* The
  first eight are the spike's L2 forbidden set; `noreturn` would delete the code after a marker;
  `returned` would replace a marker result by an argument; the parameter-effect attributes would
  let LLVM move stores to an environment across a region call; `dereferenceable` would let it
  speculate loads through a handle.
- **Benign** (ignored): function position `nounwind`, `nonlazybind`, `uwtable` (any form),
  `strictfp`, `cold`, `hot`, `nomerge`, `noinline`, `convergent`, `builtin`, `nobuiltin`,
  `optsize`, `minsize`, `optnone`, and every string attribute; return and parameter position
  `noundef`, `nonnull`, `range(...)`, `zeroext`, `signext`; declaration linkage and keywords
  external linkage, `dso_local`, `dso_preemptable`, `unnamed_addr`, `local_unnamed_addr`, any
  visibility; call-site keywords `tail`, `notail`; instruction metadata of any kind. The first
  group is the spike's L2 evidence (findings §1, §4: front ends add `nounwind`, `nonlazybind`,
  `uwtable`, `noundef`, `nonnull`, `zeroext` and string attributes; passes add
  `local_unnamed_addr`, `nonnull`, `noundef`, `range`, `tail`). `strictfp` through `optnone`
  are added by build flags NS §0 allows (`-ffp-model=strict`, `-Os`, `-O0`) or restrict
  motion; none licenses elimination, commoning, speculation or motion of an unknown call.
  Before this version freezes, a corpus run confirms each of them on the three majors (§21.2,
  bd `.21`).
- **Unknown**: every other attribute is `BD-E-MARKER-ATTRIBUTE` until corpus evidence moves it
  to one of the lists above with a version change. This is required by NS §3.1 (the positive
  legality requirement: an attribute the dialect has not classified may license motion).

Attribute groups (`#N`) are resolved before the check.

```llvm example=attr-rust-style verdict=accept
declare ptr @__bennett_qalloc(i64 noundef, i64 noundef) unnamed_addr #0
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef) unnamed_addr #0
declare void @__bennett_qfree(ptr noundef) unnamed_addr #0

define void @prep() unnamed_addr #1 {
  %h = tail call noundef nonnull ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1) #2
  tail call void @__bennett_gate(i32 noundef 2, ptr noundef nonnull %h, i64 noundef 0) #2
  tail call void @__bennett_qfree(ptr noundef nonnull %h) #2
  ret void
}

attributes #0 = { nounwind nonlazybind uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #1 = { nounwind nonlazybind uwtable }
attributes #2 = { nounwind }
```

Call sites under `-ffp-model=strict` carry `strictfp`; a `cold` declaration is benign too:

```llvm example=attr-strictfp-cold verdict=accept
declare void @__bennett_rot(i32, ptr, i64, double) #0

define void @r(double %t) #1 {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  call void @__bennett_rot(i32 3, ptr %h, i64 0, double %t) #1
  call void @__bennett_qfree(ptr %h)
  ret void
}

attributes #0 = { cold nounwind }
attributes #1 = { strictfp }
```

```llvm example=attr-memory-none verdict=reject:BD-E-MARKER-ATTRIBUTE
declare void @__bennett_gate(i32, ptr, i64) #0

define void @g() {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  call void @__bennett_qfree(ptr %h)
  ret void
}

attributes #0 = { nounwind willreturn memory(none) }
```

```llvm example=attr-callsite-read verdict=reject:BD-E-MARKER-ATTRIBUTE
define void @g() {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  call void @__bennett_gate(i32 1, ptr %h, i64 0) #0
  call void @__bennett_qfree(ptr %h)
  ret void
}

attributes #0 = { memory(read) }
```

### 3.7 Unwinding of markers

Markers never unwind. Before any other analysis (§4.1 step S1) the plugin rewrites every
`invoke` of a marker into a `call` with the same operands followed by `br label %normal`,
removes the invoking block from the phi nodes of the unwind destination, and then deletes every
block not reachable from the function's entry. *(non-normative)* This is Enzyme's practice
(enzyme survey §1.1); C++ with `-fexceptions` and Rust `extern "C-unwind"` produce such invokes
(emission summary item 3). Front ends SHOULD declare markers non-unwinding (`noexcept`, Rust
`extern "C"`). Unwinding through every other call of device code is the explicit-propagation
transform of §14.4; 0.1's `BD-E-EH` is deleted.

```llvm example=unwind-invoke verdict=accept
declare i32 @__gxx_personality_v0(...)

define void @eh() personality ptr @__gxx_personality_v0 {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  invoke void @__bennett_gate(i32 2, ptr %h, i64 0)
          to label %ok unwind label %lp

ok:
  call void @__bennett_qfree(ptr %h)
  ret void

lp:
  %e = landingpad { ptr, i32 } cleanup
  resume { ptr, i32 } %e
}
```

### 3.8 Front-end emission routes

- **clang (C, C++)** and **rustc** emit markers as direct calls to the declaration (emission
  summary). Rust MUST declare each marker with one ABI per crate (`extern "C"`); mixed
  `"C"`/`"C-unwind"` declarations are merged by rustc into one declaration with `invoke` call
  sites, which §3.7 accepts.
- **Julia** MUST emit markers with `ccall("extern __bennett_<name>", llvmcall, …)` or with
  `Base.llvmcall((module_ir, "entry"), …)` whose module contains the `declare`. Both give a
  direct call to an attribute-free declaration; `ccall("extern __bennett_measure", llvmcall,
  Bool, …)` gives `declare i1 @__bennett_measure(ptr, i64)`, exactly the §3.2 signature
  (verified with Julia 1.13.3). A plain `ccall(:__bennett_x, …)` or `@ccall` is an indirect call
  through a `jlplt` GOT global and is not a marker call. The plugin MUST reject a module
  containing a global variable whose name matches `jlplt___bennett_<name>_<digits>_got` or that
  carries the attribute `"julia.fname"="__bennett_<name>"` (`BD-E-JULIA-CCALL`), so that this
  mistake fails at compile time instead of at a lazy binding at run time; the `llvmcall` route
  keeps the full capability (audit B-13, L).
- **Region functions** are passed as `ptr @f` or as any value whose value set §7.2 resolves.
  Bennett.jl emits `ptr @f` in its own module (LLVM.jl), which keeps the full capability (audit
  B-14). A Julia `@cfunction` pointer is an `inttoptr` constant of an address of the Julia
  process; like every region pointer with value set ⊤ it is dispatched by value against the
  address-taken functions of the required type (§7.2), and an execution on which it equals no
  A(F) traps (`T-REGION`).
- **Descriptors and budget records** are built by plain stores into an `alloca` or global
  (C: the header macros; Rust: `#[repr(C)]` structs; Julia: `Ref` of an `isbits` struct), which
  survive `default<O3>` as constant stores that §5.3 reads (corpus cases, §21.2).
- **Source effect lies** (spike F5). A device function definition carrying any of
  `memory(none)`, `memory(read)` (any `memory(...)` whose effects exclude a write to any
  location), `readnone`, `readonly`, `willreturn` or `speculatable`, from which a marker call is
  reachable through the call graph of §4.1 (the function itself included), is
  `BD-E-EFFECT-LIE`. *(non-normative)* LLVM cannot infer these attributes for a function that
  reaches an unknown external call, so they come from the source; the front end's own optimiser
  may already have deleted marker calls on their strength, which is why this is a diagnostic and
  not a guarantee (definedness assumption, NS §3.2).

```llvm example=julia-jlplt verdict=reject:BD-E-JULIA-CCALL
@jlplt___bennett_gate_528_got = external global ptr #0

define void @j(ptr %h) {
  %f = load atomic ptr, ptr @jlplt___bennett_gate_528_got unordered, align 8
  call void %f(i32 1, ptr %h, i64 2)
  ret void
}

attributes #0 = { "julia.fname"="__bennett_gate" "julia.libidx"="0" }
```

```llvm example=effect-lie verdict=reject:BD-E-EFFECT-LIE
define internal void @kick(ptr %h) #0 {
  call void @__bennett_gate(i32 2, ptr %h, i64 0)
  ret void
}

define void @top() {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  call void @kick(ptr %h)
  call void @__bennett_qfree(ptr %h)
  ret void
}

attributes #0 = { willreturn }
```

## 4. Processing order, device program, tiers, variants, function addresses

### 4.1 Processing order

A plugin processes the whole-program module (after the driver's link and post-link pipeline,
§19.1) in this order; the first failing rule gives the verdict (§1.6):

| Step | Rules |
|---|---|
| S1 | §3.1 reserved names; §3.5 recognition; §3.6 attributes; §3.8 Julia check; §3.7 marker invokes; §3.8 effect lies; §19.9 version checks |
| S2 | the device analysis (§5): one fixpoint for points-to, value sets, region candidates (§7.2), indirect-call candidates (§14.2), handle provenance (§6.2) and descriptor kinds (§8.4) |
| S3 | tier assignment and variants (§4.2–§4.4); calls out of the device program (§4.5) |
| S4 | handle rules (§6) |
| S5 | region well-formedness (§7.5) |
| S6 | the TDL partition and the may-Co analysis (§10) |
| S7 | normalisation of every device variant (§12) and the residual-poison validator (§12.4); dispatch domains (§3.4) |
| S8 | lifting (§16) of every oracle shape and coherent slice; in-place verification (§8.7) |
| S9 | lowering to ISA objects (§17; plugin-defined, constrained by §18.7); blocker reports (§25.1) |

Within a step, rules apply in the order listed; within a rule, to instructions in module text
order. Blocker reports are collected during S2–S8 and issued in S9 in that order.

The **call graph** has an edge F → G when F contains a direct `call` or `invoke` of G (after
resolving aliases), an edge F → R for every candidate R of every region operand of a marker
call in F (a **region edge**), and an edge F → C for every candidate C of every indirect call in
F (§14.2). Only functions with a definition are nodes. The **closure** of a function is the set
of functions reachable from it by direct and indirect-candidate edges (region edges start a new
region and are not followed).

### 4.2 Tier assignment

Every defined function reachable from the program's roots gets a set of tiers. The **host
roots** are the functions with non-local linkage and the functions whose address host code
uses; the **device roots** are the region candidates and the whole-program entry of §19.2.

- **CC**: a function that contains a marker call, receives a handle (a parameter or a loaded
  value whose provenance contains a root, §6.2), is a candidate of an action region operand
  (its classical part is the generation, §18.4), is a device entry, is in the CC closure of
  one of these, or is promoted by §19.4.
- **R**: a function in the closure of a `reversible` region operand, or every function under
  `--bennett-tier=reversible` (§19.2).
- **L**: a function in the closure of an oracle or in-place region operand, or of a coherent
  slice (§10, TDL-3).
- **H**: every other function reachable from a host root, and every function reachable from a
  host root through host code only. A function in no device tier stays H only.

A function may get several tiers; it then has one variant per tier (§4.3). *(non-normative)*
SQLite in the rung-4 program is H (the host builds and serialises the database) and L (the
oracle runs the query), so it has two variants and one set of globals (SQLite §5.2(i)).

### 4.3 Polyvariant cloning

A **variant** is a (function, tier, coherence signature) triple, where the coherence signature
is the tuple of coherence states of the function's parameters and of the may-Co objects it
reads (§10, TDL-2) and is empty outside TDL. The H variant is the original function; every
device variant is a clone. **Clones share every global: data is never cloned.** There is one
classical memory (NS §3.2), shared by H, CC, R and the entry state of every L invocation
(§8.5). Calls inside a variant call the variant of the callee with the caller's tier and the
coherence signature at the call. 0.1's `BD-E-DEVICE-ADDRESS` is deleted: a host function may
take the address of any function (audit B-16).

### 4.4 Function addresses

Every function whose address is used has the **function address** A(F): its address in the
driver's **comparison link** (§19.5: non-PIE, fixed section addresses, identical-code folding and
constant merging off; NS §3.2, SQLite §5.2(ii)). A(F) is the value of `ptr @F` in every tier:

- in host code, by linking the production host image with the comparison layout whenever an
  address may cross the host–device boundary (§19.5);
- in CC and R code, as `const` plus `inttoptr` (ISA §4.1);
- in lifted code, as `lift.const` (ISA §4.2);
- in every data image: global initialisers, vtables, function tables (SQLite's `aBuiltinFunc`,
  VFS and pcache method tables).

So `ptrtoint`, comparison, hashing and storage of function pointers equal native execution.
Each tier maps A(F) to its own variant of F by the dispatch of §14.2. Two functions never have
equal A(F) (identical-code folding is off), so the map is well defined. A `blockaddress`
constant is §14.9.

### 4.5 Calls out of the device program

A call in a device variant of a function with no definition resolves, in this order:

1. a marker (§3.2) or a primitive (§3.1);
2. a **runtime shim**: a definition of the symbol in `bennett-runtimes` or `bennett-arith`
   bitcode, which the driver links before S2 (§19.1): libc and libm (musl-derived), libpthread
   with one thread, the Julia shim runtime, Rust's `core::panicking::*` targets and the platform
   shims of §20. The shim is an ordinary device function (coverage class `shimmed`, with its
   `shim_hash`, ISA §13);
3. in a CC variant only, a **host call** through `hostcall` (§11.4);
4. otherwise **trapped**: the call is replaced by F(8) (§12.3) and the coverage report has a
   `trapped` line for it (NS §3.3: "Calls with no bitcode are coverage-report lines (*trapped*),
   never silent").

An R or L variant never makes a host call (ISA §4.1: `hostcall` is CC only; NS §4.2: coherent
regions are closed). *(non-normative)* Item 4 is the only fault the dialect introduces for a
call, and it occurs only on the executions that reach the call; it is the north star's own rule.

## 5. The device analysis (one fixpoint)

The device analysis is a whole-program, flow-insensitive, inclusion-based (Andersen-style),
field-sensitive points-to and value-set analysis over every device variant and every host
function that exchanges data with one (passes it a pointer, or shares a global it accesses). It
is specified exactly: **every verdict, candidate set and dispatch domain of this document is
computed from the reference analysis below.** A plugin MAY use a more precise analysis to shrink
dispatch domains or arena placement in its lowering, never to change a verdict (the run-time
value is always a member of the reference set, so the results are unchanged).

### 5.1 Abstract objects and atoms

The **abstract objects** are:

- each `alloca` instruction;
- each global variable;
- each **allocation site**: a call of a function that carries `allockind("alloc")` or
  `allocsize(...)`, or whose name is one of `malloc`, `calloc`, `realloc`, `aligned_alloc`,
  `posix_memalign` (the object is the one written through its first argument), `memalign`,
  `strdup`, `strndup`, `_Znwm`, `_Znam`, `_ZnwmRKSt9nothrow_t`, `_ZnamRKSt9nothrow_t`,
  `_ZnwmSt11align_val_t`, `_ZnamSt11align_val_t`, `__rust_alloc`, `__rust_alloc_zeroed`,
  `__rust_realloc`, `julia.gc_alloc_obj`, `ijl_gc_alloc_typed`, `jl_gc_alloc`,
  `ijl_gc_small_alloc`, `ijl_gc_big_alloc`, or `__bennett_nz_alloc`;
- the pseudo-object `EXT` (memory of unknown provenance: host memory reached through a pointer
  the analysis did not create).

Heap objects are context-insensitive: one object per allocation-site instruction of the variant
in which it occurs. The list above is the reference list; `bennett-runtimes` declares its
allocator entry points with `allockind("alloc")` so that they are covered by the first rule.

An **offset** is an integer byte offset, a **residue class** (r mod s)[lo, hi) with s ≥ 2 (every
offset o with o ≡ r (mod s) and lo ≤ o < hi), or `*` (any offset). An **atom** is one of:

- `(X, o)`: a pointer into object X at offset o;
- `FN(F)`: the address A(F) of a defined function F;
- `ROOT(r)`: a handle with root r (the allocation site of a `qalloc`/`qborrow` call, §6.5);
- `INT(c)`: the integer constant c (of the value's width).

Every SSA value v (per lane for vectors, per index path for aggregates) has an **abstract
value** AV(v) = (A, t): a finite set A of atoms and a flag t; t = ⊤ means "and any other integer
or address". ⊤ never stands for a `ROOT` atom (handle provenance is always explicit); for a
function-pointer operand it stands for "any function of the operand's type whose address is
used" (§7.2, §14.2). Every slot (X, o) of memory has a content AV(X, o) of the same form. When A
holds more than **K = 4096** `INT` atoms they are dropped and t is set (a normative constant: it
decides dispatch and blocker verdicts, so §24 does not defer it). "AV(v) = ⊤" below means t is
set; unions and inclusions are taken component-wise.

### 5.2 Rules

The analysis is the least fixpoint of the following rules over AV. "Copies" means AV(result) ⊇
AV(operand) lane by lane; ⊤ absorbs.

| Rule | Instruction or source | Effect |
|---|---|---|
| PT1 | `alloca`, global `@G`, allocation-site call | AV ∋ (X, 0) |
| PT2 | `getelementptr T, ptr p, idx…` | for each (X, o) ∈ AV(p), indices in order: a constant index adds its byte offset under the datalayout (to an exact offset, or to r, lo and hi of a class); a non-constant index with element size s into an array type `[N x E]` that starts at byte offset b of the indexed position turns the offset into the class (b mod s)[b, b + N·s), and into (b mod s)[lo′, hi′) with the union of the extents if it is already a class with the same s; a non-constant index of the GEP's first (pointer) operand, or into a class with a different stride s′, gives (o mod gcd(s, s′)) over the whole object; a class with stride 1 is `*`; `*` stays `*` |
| PT3 | `phi`, `select` (value operands), `freeze`, `bitcast`, `addrspacecast` | copies (union) |
| PT4 | `ptrtoint`, `inttoptr`, `zext`/`sext`/`trunc` of a pointer-width integer to pointer width | copies |
| PT5 | `add`/`sub` of a value with pointer atoms and an `INT` set | shifts each pointer atom's offset by each constant (classes and `*` stay); any other integer operation on a pointer atom gives (X, `*`) for each X; on `INT` sets, every LLVM integer operation, cast and `icmp` is evaluated elementwise; `and x, m` with m constant gives the submasks of m intersected with the operand's set when that is ⊤; `urem x, c` with c constant gives {0, …, c−1} when x is ⊤; a `range(lo, hi)` attribute or `!range` metadata (read before N3 removes it) restricts ⊤ to [lo, hi) |
| PT6 | `load T, ptr p` | for each (X, o) ∈ AV(p): the union of AV(X, o′) over the slots o′ that overlap [o, o + size(T)); for a global X declared `constant`, the atoms of its initialiser at those offsets (`FN(F)` for `ptr @F`, `(G, c)` for a pointer into G, `INT(c)` for integers); for X = EXT, ⊤ |
| PT7 | `store v, ptr p` | AV(X, o + d_k) ⊇ AV(v_k) for each (X, o) ∈ AV(p) and each lane or field k at byte offset d_k |
| PT8 | memory copy (`llvm.memcpy`/`memmove`/`memcpy.inline`, `__bennett_rt_memmove`) of (dst, src, len) | for each slot (Y, s) of each (Y, o_s) ∈ AV(src) and (Z, o_d) ∈ AV(dst): when the offsets and len are constants and [s, s + 1) lies in the copied range, AV(Z, o_d + s − o_s) ⊇ AV(Y, s); else AV(Z, `*`) ⊇ AV(Y, s) |
| PT9 | direct call of G, or indirect call with candidate G (§14.2) | AV(parameter i of G) ⊇ AV(argument i); AV(result) ⊇ the union of AV over G's `ret` operands; `byval` arguments copy the pointee's slots into the callee's copy object |
| PT10 | `insertelement`/`extractelement`/`shufflevector`/`insertvalue`/`extractvalue` | atoms move with constant lanes and index paths; a non-constant lane index moves the union of all lanes (a handle-table read, audit B-23) |
| PT11 | a parameter of a function with a host caller, a device entry, or a function whose address host code uses | AV ⊇ {(EXT, `*`)} for `ptr` parameters, ⊤ for integer parameters, plus the atoms of the device-side arguments by PT9 |
| PT12 | `qalloc`/`qborrow` call (§6.5); a call of a function with no definition that resolves to a host call (§4.5) or is trapped; an `atomicrmw`/`cmpxchg` (before N9) | AV ∋ ROOT(site); the result is ⊤ and every pointer argument's reachable slots get ⊤ (host calls are pointer-free, §11.4, so no pointer atoms escape into host code); rmw/cmpxchg are a load plus a store (PT6, PT7) |

An `inttoptr` of a constant gives (EXT, `*`) and, for function-pointer purposes, ⊤: function
addresses are symbolic `FN` atoms during the analysis, and their numeric values A(F) are fixed
only by the comparison link (§19.5), after normalisation (S7) and before lifting (S8).

### 5.3 Value sets

The **value set** VS(v) of an integer or pointer operand is the set of its `INT` and `FN` atoms
(pointer atoms denote addresses that are not compile-time constants and make VS(v) = ⊤ for
dispatch purposes), or ⊤. A value set is a precision tool only:

- an operand with a finite VS is dispatched over it (§3.4, §14.2);
- an operand with VS = ⊤ is dispatched over its type's whole valid domain where that domain is
  finite: operation codes and classes (§3.4), binding kinds (§8.4), the function addresses of a
  type (§7.2, §14.2);
- otherwise it is a blocker case of §25.1: widths (BLK-1), budgets computed on the device
  (BLK-2), parameters of in-place pairs (BLK-3).

### 5.4 Uses

| Result | Read by |
|---|---|
| `FN` atoms of region operands | region candidate sets (§7.2) |
| `FN` atoms of indirect callees | indirect-call candidate sets (§14.2) |
| `ROOT` atoms | handle provenance (§6.2), handle containment (§6.4), static register files (§6.5) |
| `INT` atoms of descriptor and budget fields | descriptor shapes (§8.4), budget pre-minting (§9.5) |
| slots stored under control | the may-Co analysis and arena placement (§10, TDL-2, TDL-4) |
| objects loaded by L code | the oracle read set R and entry-state transfer (§8.5) |
| `INT` atoms of `op`, `cls`, `n` | dispatch domains (§3.4) |

```llvm example=pt-variable-index verdict=accept
%struct.tab = type { [4 x ptr], i64 }

define void @t(i64 %i) {
  %s = alloca %struct.tab
  %h0 = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h0, ptr %s
  %pn = getelementptr %struct.tab, ptr %s, i64 0, i32 1
  store i64 3, ptr %pn
  %k = and i64 %i, 3
  %pk = getelementptr %struct.tab, ptr %s, i64 0, i32 0, i64 %k
  %hk = load ptr, ptr %pk
  call void @__bennett_gate(i32 1, ptr %hk, i64 0)
  %n = load i64, ptr %pn
  %n2 = add i64 %n, 1
  store i64 %n2, ptr %pn
  call void @__bennett_qfree(ptr %h0)
  ret void
}
```

*(non-normative)* In `pt-variable-index`, `%pk` has the offset class (0 mod 8)[0, 32) in `%s`
(the `[4 x ptr]` array), so the load `%hk` reads the slots 0, 8, 16, 24: AV(`%hk`) =
{ROOT(`%h0`)}. The count field is at the exact offset 32, outside the class, so AV(`%n`) holds
INT(3) and, through the store of `%n2`, INT(4), INT(5), … until it exceeds K and becomes ⊤; it
holds no `ROOT` atom, and the arithmetic on it is legal (audit B-27: 0.1 gave the load offset `*`
and rejected this program).

## 6. Handles (handles 0.2)

### 6.1 Representation

A handle is an ordinary `ptr` in address space 0. In memory, in integers and at the host–device
boundary a handle is its **register id**: an opaque value below 2^pw that the device allocates
(the ISA launch representation `bennett_qreg`, ISA §10; on a 32-bit target the device allocates
ids below 2^32). Its bits are distinct from every other live handle, never equal 0, and MUST NOT
influence any result other than through §6.3; the rules below make them unobservable. A handle
denotes a register of n wires, n the `qalloc` operand; wire i of handle h is written h.i.

### 6.2 Provenance (maintainer decision 2)

The **provenance** of a value is the set of `ROOT` atoms of its abstract value (§5). Provenance
flows through **bitwise copies** only: `ptrtoint`/`inttoptr` at width pw, integer loads and
stores of width pw, vector lanes (including dynamic lanes, PT10: a dynamically indexed vector of
handles is a handle table), aggregate fields, memory copies, `phi`, `select`, `freeze`, call
arguments and returns (PT3–PT10). A handle-derived value (any lane or field) MAY be:

1. a handle operand of a marker (§3.2);
2. copied by the rules above, including storage in any slot the analysis tracks (§6.4);
3. an operand of `icmp eq` or `icmp ne` (§6.3);
4. an argument of a direct or indirect call of a defined function, or a return value.

Every other use is `BD-E-HANDLE-USE` (maintainer decision 2: "any other use of a
handle-derived integer is rejected fail-loud"; NS §3.1 "never dereferenced"): in particular
arithmetic, bitwise operations, `icmp` with any other predicate, any cast other than the copies
above (`trunc`, `zext`, `sext`, `bitcast` to a non-pointer-width type, `ptrtoint` to a width ≠
pw), `getelementptr` with a handle as base or index, `switch` on it, use as the pointer operand of
a `load`, `store`, `atomicrmw`, `cmpxchg` or memory intrinsic (dereference), and a load of any
type whose byte range overlaps a handle-derived slot without being exactly one pw-wide lane of
it (a partial read).

A handle operand of a marker whose provenance is empty is `BD-E-HANDLE-UNTRACKED` (it cannot be
a handle of this program). *(non-normative)* A tracked value that at run time is not a live
handle (a stale copy, a freed register) traps at the marker (`T-DEAD`, §18.3).

### 6.3 Comparison (maintainer decision 4)

`icmp eq` and `icmp ne` of a handle with `null`, or with another handle-derived value, compare
**identity**: a live handle is never null, and two handles are equal iff they denote the same
register. The result is not handle-derived. In CC it lowers to `icmp` on register ids. This
covers C `if (!q)` and Rust's `Option<Handle>` niche (audit D8). *(non-normative)* A comparison
is a classical observation of identity, not of the register's content; ids are unique, so it
equals the native comparison of the two handle values.

### 6.4 Collections and containment

Handles may be stored in any slot the analysis tracks: tables, vectors, linked structures,
globals (field-sensitively), heap objects, and objects passed to indirect calls or returned by
address-taken functions (audit B-22, B-24, B-26, B-29). A handle may **escape** only where code
the analysis cannot see could read it:

- `BD-E-HANDLE-ESCAPE`: a `ROOT` atom reaches a slot of `EXT`, an argument or a reachable slot of
  a call that resolves to a host call or is trapped (§4.5), or the return value of a function
  whose callers are not all in the link. NS §3.1: "any handle use that survives into host native
  code is rejected".

H functions in the link that receive register ids through §6.6 are analysed like device code:
they may copy, store, compare and pass them back to device entries (§6.2 items 2–4); any other
use is `BD-E-HANDLE-USE`.

### 6.5 Realisation on ISA 0.8: static register files

ISA 0.8 has no instruction that stores, loads or converts a `qreg` (ISA §3.2, §3.3, §4.1), and
`qreg[n]` types have literal widths. CC code holds `qreg` values in its classical environment
(dynamic SSA instances, block parameters, call arguments and results; ISA §3.2, §7.4). The plugin
realises each allocation site s (a `qalloc` or `qborrow` call) in one of two ways:

- **Direct.** If no `ROOT(s)` atom reaches a memory slot (PT7, PT8), the handle is a CC `qreg`
  value threaded through SSA values, block parameters, call arguments and results ("register-
  environment passing"; §25.2 records that ISA §3.3's transition table should name CC `call`,
  `ret` and `br` operands of `qreg` type). Every execution of s creates a new dynamic instance,
  so loops and recursion need no bound.
- **Static register file.** Otherwise a **root** is a pair (s, instance index k < N(s)). For
  each root the plugin keeps one CC `qreg` variable, threaded like a direct handle through every
  CC variant that may use it; `qalloc` at s picks a free instance index at run time and executes
  `qreg.new cls n` into that variable (one variable per member of the width dispatch domain,
  §3.4); the register id stored in memory is the id of that register. A marker operand whose
  provenance holds several roots is dispatched by comparing its register id with the ids of the
  live candidate roots (compare tree, §14.2).

**Reference instance bound** of a site s in function F with a static register file:

1. s is **self-disjoint** iff the only memory its `ROOT(s)` atom reaches is allocas of F whose
   address does not escape F, and every CFG path of F from s to a `ret`, to s again, or to a call
   whose callee may reach F through the call graph passes through a `qfree` whose operand's
   provenance is exactly {s}. Then N(s) = 1.
2. Otherwise N(s) = E(s), the bound on executions of s per device-entry call: E(s) = TC(s) ×
   Σ_c E(c) over the device call sites c of F (E = 1 for a device entry), where TC(s) is the
   product of the constant maximum trip counts of the loops of F that contain s (LLVM's
   `ScalarEvolution::getSmallConstantMaxTripCount` on the materialised module of the major in
   use), and E(s) = ∞ when a containing loop has no constant maximum trip count or F is in a
   cycle of the call graph.
3. If N(s) = ∞, every execution of s is a **blocker point** of BLK-1 (`blocked:BD-B-ISA4`,
   §25.1): ISA 0.8 cannot name an unbounded number of registers reached through memory. The
   plugin compiles the program with a static file of `--bennett-qreg-instances` instances
   (default 64, §24) and a blocker trap (§25.1) on an execution that needs more.

A width with VS = ⊤ is BLK-1 likewise (§3.4). In R code, which cannot allocate registers on ISA
0.8, §7.5(b) applies.

### 6.6 Host–device boundary

A device entry's parameters and results of handle type bind to launch `QREG` arguments and
results (ISA §10). A `ptr` parameter of a device entry is a **handle parameter** iff its
candidate atom `ROOT(E, i)` (added by PT11 to every pointer parameter of every device entry)
reaches a marker handle operand; otherwise the candidate atom is removed before §6.2 is checked.
A handle parameter binds to `QREG`; host code may copy, store and compare register ids and pass
them back. Leak checking happens at program end and at `bennett_qreg_free`, not at each
device-entry return, which gives the REPL's lexical lifetime (NS §5; audit B-30). *(non-normative)*
A register returned to the host stays live across launches until the host frees it or a
`measure` consumes it (ISA §10: "register ids created by the run remain valid unless measured
or freed").

### 6.7 Copy, XOR and in-place rules

Copying a handle copies a reference. Quantum data moves only by:

- `qload(dst, mem, addr)`: XOR of cell `addr` of `mem` into `dst` (§18.3); a copy when `dst` is
  clean, the source preserved;
- `qstore(mem, addr, val)`: XOR of `val` into cell `addr` of `mem` (ISA `qstore`), whatever `mem`
  holds;
- `qprep(h, src, n)`: XOR of classical bytes into `h` (§3.2);
- `inplace(g, ginv, budget, desc)`: x ← g(x), admitted only under §8.7;
- `oracle(f, budget, desc)`: targets ⊕= outputs, fault ⊕= code, inputs preserved (§8).

The north star's compile-time rule "a store into a register not known to be clean is an error"
(NS §3.1) is the optional warning **`BD-W-QSTORE-UNCLEAN`**: under `-bennett-warn-qstore`, the
plugin warns at every `qstore` whose target is not provably clean (no event since its `qalloc`
other than a `qstore` of the same `addr` and `val`). The warning never changes the verdict, so
the uncomputing second store stays legal (§1.4).

### 6.8 Handle → wire obligations

The plugin converts handles to ISA wires (ISA §3.3 linear values) when it lowers. Its
obligations, each a property of every ISA object it emits (ISA suite F), are: every gate's wires
pairwise distinct; no wire used after its release; every `qalloc`ed bundle released by an
explicit `qfree` (ISA §5.1); every control context disjoint from the operands it controls (ISA
§3.3); the uncomputation-validity discipline of ISA §6 for every value it introduces. Where an
obligation depends on run-time data, the reference semantics checks it dynamically and the plugin
MUST include the same check (§18.3 traps `T-ALIAS`, `T-DEAD`, `T-LEAK`, `T-CTRL`); `T-CLEAN` is
checked as ISA `qreg.free` cleanliness is: by simulating executors, with hardware following ISA
§17 item 14.

### 6.9 Examples

The spike F1 shape (an 8-byte `memcpy` of a handle turned into `ptrtoint`, `store i64`, `load
i64`, `inttoptr`):

```llvm example=handle-int-roundtrip verdict=accept candidates=rg
define internal void @rg(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  ret void
}

define void @top() {
  %e = alloca i64
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %c = ptrtoint ptr %h to i64
  store i64 %c, ptr %e
  call void @__bennett_adj(ptr @rg, ptr null, ptr %e)
  %l = load i64, ptr %e
  %h2 = inttoptr i64 %l to ptr
  call void @__bennett_qfree(ptr %h2)
  ret void
}
```

```llvm example=handle-memcpy verdict=accept candidates=rg
declare void @llvm.memcpy.p0.p0.i64(ptr, ptr, i64, i1 immarg)

define internal void @rg(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  ret void
}

define void @top() {
  %slot = alloca ptr
  %e = alloca { ptr, i64 }
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %slot
  call void @llvm.memcpy.p0.p0.i64(ptr %e, ptr %slot, i64 8, i1 false)
  call void @__bennett_adj(ptr @rg, ptr null, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=handle-arith verdict=reject:BD-E-HANDLE-USE
define void @top() {
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  %c = ptrtoint ptr %h to i64
  %d = add i64 %c, 8
  %h2 = inttoptr i64 %d to ptr
  call void @__bennett_gate(i32 1, ptr %h2, i64 0)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

C `if (!q)` and handle equality are identity (maintainer decision 4):

```llvm example=handle-null-check verdict=accept
define void @top() {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %z = icmp eq ptr %h, null
  br i1 %z, label %out, label %use

use:
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  br label %out

out:
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=handle-eq verdict=accept
define void @swap_if_distinct(ptr %a, ptr %b) {
entry:
  %same = icmp eq ptr %a, %b
  br i1 %same, label %out, label %two

two:
  call void @__bennett_gate2(i32 3, ptr %a, i64 0, ptr %b, i64 0)
  br label %out

out:
  ret void
}
```

*(non-normative)* In `handle-eq`, `@swap_if_distinct` is a device entry whose two `ptr`
parameters reach marker handle operands, so both are handle parameters bound to `QREG` launch
arguments (§6.6).

```llvm example=handle-deref verdict=reject:BD-E-HANDLE-USE
define i64 @top() {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %v = load i64, ptr %h
  call void @__bennett_qfree(ptr %h)
  ret i64 %v
}
```

```llvm example=handle-truncate verdict=reject:BD-E-HANDLE-USE
define i32 @top() {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %c = ptrtoint ptr %h to i32
  call void @__bennett_qfree(ptr %h)
  ret i32 %c
}
```

```llvm example=handle-to-external verdict=reject:BD-E-HANDLE-ESCAPE
declare void @log_handle(ptr)

define void @top() {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  call void @log_handle(ptr %h)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=handle-store-host verdict=reject:BD-E-HANDLE-ESCAPE
define void @put(ptr %out) {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %out
  ret void
}
```

A constant address is no handle of this program:

```llvm example=handle-untracked verdict=reject:BD-E-HANDLE-UNTRACKED
define void @kick() {
  call void @__bennett_gate(i32 2, ptr inttoptr (i64 4096 to ptr), i64 0)
  ret void
}
```

A host-supplied register (REPL), and a register returned to the host:

```llvm example=handle-host-param verdict=accept
define void @kick(ptr %h) {
  call void @__bennett_gate(i32 2, ptr %h, i64 0)
  ret void
}
```

```llvm example=handle-return verdict=accept
define ptr @mk() {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  call void @__bennett_gate(i32 2, ptr %h, i64 0)
  ret ptr %h
}
```

A slot whose address is stored in an internal global is still tracked (audit B-26):

```llvm example=handle-object-tracked verdict=accept
@pp = internal global ptr null

define void @top() {
  %slot = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %slot
  store ptr %slot, ptr @pp
  %s = load ptr, ptr @pp
  %h2 = load ptr, ptr %s
  call void @__bennett_gate(i32 1, ptr %h2, i64 0)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

Aggregates carry provenance per field (Rust passes pairs this way), and vector lanes per lane
(spike F1, `load-store-vectorizer`):

```llvm example=handle-aggregate verdict=accept
define void @top(i64 %i) {
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  %p0 = insertvalue { ptr, i64 } zeroinitializer, ptr %h, 0
  %p1 = insertvalue { ptr, i64 } %p0, i64 %i, 1
  %g = extractvalue { ptr, i64 } %p1, 0
  %j = extractvalue { ptr, i64 } %p1, 1
  %k = and i64 %j, 1
  call void @__bennett_gate(i32 2, ptr %g, i64 %k)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=handle-vector-lane verdict=accept
define i64 @top(i64 %x) {
  %m = alloca <2 x i64>
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %c = ptrtoint ptr %h to i64
  %v0 = insertelement <2 x i64> zeroinitializer, i64 %x, i32 0
  %v1 = insertelement <2 x i64> %v0, i64 %c, i32 1
  store <2 x i64> %v1, ptr %m
  %p = getelementptr i8, ptr %m, i64 8
  %l = load i64, ptr %p
  %h2 = inttoptr i64 %l to ptr
  call void @__bennett_gate(i32 1, ptr %h2, i64 0)
  %l0 = load i64, ptr %m
  %y = add i64 %l0, 1
  call void @__bennett_qfree(ptr %h)
  ret i64 %y
}
```

A handle table indexed by a classical value, and a dynamically indexed vector of handles
(audit B-23):

```llvm example=handle-table verdict=accept
define void @tab(i64 %i) {
  %t = alloca [4 x ptr]
  %h0 = call ptr @__bennett_qalloc(i64 0, i64 1)
  %h1 = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h0, ptr %t
  %p1 = getelementptr [4 x ptr], ptr %t, i64 0, i64 1
  store ptr %h1, ptr %p1
  %k = and i64 %i, 1
  %pk = getelementptr [4 x ptr], ptr %t, i64 0, i64 %k
  %hk = load ptr, ptr %pk
  call void @__bennett_gate(i32 1, ptr %hk, i64 0)
  call void @__bennett_qfree(ptr %h0)
  call void @__bennett_qfree(ptr %h1)
  ret void
}
```

```llvm example=handle-dynamic-lane verdict=accept
define void @lanes(i32 %i) {
  %h0 = call ptr @__bennett_qalloc(i64 0, i64 1)
  %h1 = call ptr @__bennett_qalloc(i64 0, i64 1)
  %v0 = insertelement <2 x ptr> zeroinitializer, ptr %h0, i32 0
  %v1 = insertelement <2 x ptr> %v0, ptr %h1, i32 1
  %k = and i32 %i, 1
  %hk = extractelement <2 x ptr> %v1, i32 %k
  call void @__bennett_gate(i32 1, ptr %hk, i64 0)
  call void @__bennett_qfree(ptr %h0)
  call void @__bennett_qfree(ptr %h1)
  ret void
}
```

A vector of handles filled by a loop with a constant trip count has the instance bound
N(s) = E(s) = 8 (§6.5 rule 2); the same loop with a trip count from host input is blocked
(BLK-1):

```llvm example=handle-vec-bounded verdict=accept
define void @fill() {
entry:
  %v = alloca [8 x ptr]
  br label %loop

loop:
  %i = phi i64 [ 0, %entry ], [ %i2, %loop ]
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %p = getelementptr [8 x ptr], ptr %v, i64 0, i64 %i
  store ptr %h, ptr %p
  %i2 = add i64 %i, 1
  %c = icmp ult i64 %i2, 8
  br i1 %c, label %loop, label %use

use:
  %p3 = getelementptr [8 x ptr], ptr %v, i64 0, i64 3
  %h3 = load ptr, ptr %p3
  call void @__bennett_gate(i32 2, ptr %h3, i64 0)
  br label %free

free:
  %j = phi i64 [ 0, %use ], [ %j2, %free ]
  %q = getelementptr [8 x ptr], ptr %v, i64 0, i64 %j
  %hq = load ptr, ptr %q
  call void @__bennett_qfree(ptr %hq)
  %j2 = add i64 %j, 1
  %d = icmp ult i64 %j2, 8
  br i1 %d, label %free, label %out

out:
  ret void
}
```

```llvm example=handle-vec-unbounded verdict=blocked:BD-B-ISA4
declare ptr @malloc(i64)
declare void @free(ptr)

define void @fill(i64 %n) {
entry:
  %z = icmp eq i64 %n, 0
  br i1 %z, label %out, label %alloc

alloc:
  %bytes = shl i64 %n, 3
  %v = call ptr @malloc(i64 %bytes)
  br label %loop

loop:
  %i = phi i64 [ 0, %alloc ], [ %i2, %loop ]
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %p = getelementptr ptr, ptr %v, i64 %i
  store ptr %h, ptr %p
  %i2 = add i64 %i, 1
  %c = icmp ult i64 %i2, %n
  br i1 %c, label %loop, label %free

free:
  %j = phi i64 [ 0, %loop ], [ %j2, %free ]
  %q = getelementptr ptr, ptr %v, i64 %j
  %hq = load ptr, ptr %q
  call void @__bennett_qfree(ptr %hq)
  %j2 = add i64 %j, 1
  %d = icmp ult i64 %j2, %n
  br i1 %d, label %free, label %done

done:
  call void @free(ptr %v)
  br label %out

out:
  ret void
}
```

```text blocker=handle-vec-unbounded
BD-B-ISA4 @fill %h: qalloc site has no instance bound (stored into a heap object, loop trip count not constant: E = infinity); ISA 0.8 has no qreg in memory; BLK-1 (ISA-4) qreg.id/qreg.from_id; compiled with 64 static instances and a blocker trap beyond them
```

A handle passed to an indirect call reaches every candidate's parameter (audit B-22):

```llvm example=handle-indirect verdict=accept callees=hx,hz
@ops = internal constant [2 x ptr] [ptr @hx, ptr @hz]

define internal void @hx(ptr %q) {
  call void @__bennett_gate(i32 1, ptr %q, i64 0)
  ret void
}

define internal void @hz(ptr %q) {
  call void @__bennett_gate(i32 7, ptr %q, i64 0)
  ret void
}

define void @apply(i64 %k) {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %i = and i64 %k, 1
  %p = getelementptr [2 x ptr], ptr @ops, i64 0, i64 %i
  %f = load ptr, ptr %p
  call void %f(ptr %h)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

`qstore` twice is the identity on `mem`, so every register is released clean:

```llvm example=qstore-twice verdict=accept
define void @top() {
  %mem = call ptr @__bennett_qalloc(i64 0, i64 4)
  %addr = call ptr @__bennett_qalloc(i64 0, i64 1)
  %val = call ptr @__bennett_qalloc(i64 0, i64 2)
  call void @__bennett_qstore(ptr %mem, ptr %addr, ptr %val)
  call void @__bennett_qstore(ptr %mem, ptr %addr, ptr %val)
  call void @__bennett_qfree(ptr %val)
  call void @__bennett_qfree(ptr %addr)
  call void @__bennett_qfree(ptr %mem)
  ret void
}
```

## 7. Regions (regions 0.2)

### 7.1 Region-entry markers and region kinds

| Marker | Region operand(s) | Interface kind | Required type of a candidate | ISA counterpart |
|---|---|---|---|---|
| `ctrl(q, qi, f, budget, env)` | `f` | action | `void (ptr)` | `ctl w action_call` (ISA §4.7, §5.3) |
| `adj(f, budget, env)` | `f` | action | `void (ptr)` | `adj action_call` |
| `compute(f, use, budget, env)` | `f`, `use` | action | `void (ptr)` | `action_call`; `action_call`; `adj action_call` |
| `reversible(f, budget, env)` | `f` | reversible | `void (ptr)` | a call of an R function (ISA §3.1, §7.4) |
| `oracle(f, budget, desc)` | `f` | oracle | any function type (§8) | `oracle_call @ref tk (ins..) tgt fr (mem..) (args..)` (ISA §4.7, §5.2) |
| `inplace(g, ginv, budget, desc)` | `g`, `ginv` | oracle pair | any function type whose INOUT parameter and result have equal widths (§8.7) | `qinplace @g @ginv tk x` (ISA §4.5) |

The marker fixes the region's **interface** (TDL-1, §10). The body is partitioned by content
(§10) and never rejected for containing classical code; the plugin outlines coherent slices of
action bodies (TDL-3). An **oracle region** is a lifted classical oracle with output targets and
a fault register (ISA §5.2); an **action region** is a quantum action on the wires its events
name (ISA §5.3) with no fault outcome of its own: a fault of an oracle it calls lands in a fault
register the action declares (§10, TDL-8).

### 7.2 Candidate sets and dispatch (maintainer decision 3)

The candidate set RR(v) of a region operand v is computed from its abstract value (§5):

- every `FN(F)` atom of AV(v), resolved by `resolve` below;
- if AV(v) has the ⊤ flag: in addition every function of the required type of §7.1 (for
  `oracle`/`inplace`: every function) whose address is used anywhere in the linked program,
  resolved (decision 3 read literally: "every function whose address can reach a region marker";
  audit B-33). The set is therefore always bounded by the program.

`resolve(F)` follows aliases to their aliasee and **forwarding thunks** to their target: F is a
forwarding thunk of G iff F's body is one block holding exactly a call of G (optionally
`tail`/`musttail`/`notail`, default calling convention, no operand bundles) whose arguments are
F's parameters in order and whose function type equals F's, followed by `ret void` or `ret` of
that call's result; then `resolve(F) = resolve(G)`. A cycle of thunks is `BD-E-REGION-THUNK`
(the call never terminates).

**Dispatch.** The region operand is classical data. The plugin compiles a body for every
candidate. At run time the operand's value is compared, by the compare tree of §14.2 over the
sorted keys, with A(S) of every **source** S (every function or alias that resolves into the
candidate set and whose address reaches v, plus every candidate itself); on equality the region
`resolve(S)` is entered. No match is the run-time trap `T-REGION` (fault code 4). A candidate
with no definition (an external declaration, a function without bitcode) is entered as a
trapped call: F(8) with a coverage line (§4.5 item 4).

**Ill-formed candidates.** A candidate that is not well-formed for the marker's kind (a type
other than §7.1's, or a violation of §7.5) is compiled as a **trap body** (`T-REGION-INVALID`,
fault code 4) with a coverage line: it may never be dispatched, so it is not a compile-time
error. It is rejected (`BD-E-REGION-TYPE`, `BD-E-REGION-MEASURE`, `BD-E-REVERSIBLE-MEASURE`)
only when it is the **unique** candidate, because then every execution of the marker fails
(outline E14).

0.1's `BD-E-REGION-UNBOUNDED` and `BD-E-REGION-EXTERNAL` are deleted.

### 7.3 Region identity (maintainer decision 1)

A region is identified by its content, never by its symbol. Candidates that resolve to the same
function are one region. The semantic identity of an **oracle region** in a shape (§8.4) is the
interface hash (ISA §9.2) of `@ref` in its reference object (§16.2): every lproc, data image and
layout leaf of the closure is part of it, and `@ref`, `@L<n>`, `@G<n>` are fixed names, so two
functions with equal materialised bodies have equal identity whatever their source names. Symbol
names, linkage, aliases and thunks are non-normative: diagnostics and coverage entries MAY print
them.

The **region key** of any region is the SHA-256 of the text printed by the LLVM printer of the
major in use for a module that contains the materialised region function and its closure, after
`strip` (local names), with the functions renamed `f0, f1, …` in depth-first preorder from the
region along direct calls in instruction order, and without datalayout, triple and module
metadata. It keys the budget table (§9.2) and is recorded in the certificate and coverage
entries. It depends on the LLVM major, which the certificate records (§24, D13).

### 7.4 Kinds by content

NS §4.2: "the plugin classifies each outlined region by its contents and the verifier checks the
declared interface". After the TDL partition (§10):

- an action region whose generated events are all permutation events (X-family gates, `qload`,
  `qstore`, `qexch`, oracle calls, permutation actions) is emitted as an ISA `perm_action`
  (ISA §5.3), which certificates can verify by T3; otherwise as an `action`;
- an oracle region stays an oracle;
- a `reversible` marker call reached from an action region's generation or from an L closure is
  not an R entry: its operand is treated as a direct call of the region function, partitioned by
  TDL inside actions and lifted inside oracles, with the call's budget record governing its
  slices (§9.3; audit B-37). 0.1's `BD-E-REGION-TIER` and `T-TIER` are deleted.

### 7.5 Static well-formedness

Only the rules the north star requires:

- **(a) Measurement in a unitary region.** A `measure` call in the closure of an action region
  is `BD-E-REGION-MEASURE` (NS §3.1: "user measurement inside it is refused"), unless the module
  requests **deferred measurement** with the module flag `!{i32 1,
  !"bennett.measure_in_unitary", !"defer"}` (NS §3.1: "or, when the front end asks for it,
  deferred by the deferred-measurement principle, which the certificate states"). Then a
  `measure(h, i)` inside a generation becomes a `qcopy` of `h.i` onto a fresh wire w (ISA §4.5),
  the call's `i1` result is a Co value whose wire is w (§10, TDL-2 seed), and the wire is
  released by the uncomputation of the region (it is history, TDL-7). The coverage report has a
  `lowered` entry with source `dialect-0.2:7.5a` for every such call, and the certificate lists
  the id `deferred_measurement` in the region's `definedness_assumptions` (ISA §12.3; §25.2
  records the wording item).
- **(b) Reversible regions.** The closure of a reversible region MAY contain gate and region
  markers on handles received through `env`: they lower to R-tier `action_call`/`oracle_call`
  (ISA §3.1, §4.7), recorded in the R history and reversed by re-application or adjoint (ISA
  §7.4). A `measure` call in the closure is `BD-E-REVERSIBLE-MEASURE` (ISA §10: a run that
  measured is not reversible; ISA §3.3: a `measure` frame is never reversed). A `qalloc`,
  `qborrow` or `qfree` in the closure is **hoisted** (ISA 0.8 has `qreg.new` in CC only): when
  every such site s has a finite reference instance bound N(s) (§6.5 rules 1 and 2, applied to
  every site whether or not it reaches memory, with the reversible entry in place of the device
  entry), the CC caller allocates N(s) clean registers per site before the R call, passes them as
  `qreg` arguments, and frees them after it returns; `qalloc` in R selects a free one, `qfree`
  checks that it is clean (`T-CLEAN`) and returns it to the free set. Otherwise the site is a
  blocker point of BLK-4 (`blocked:BD-B-ISA12`, §25.1).
- **(c) In-place pairs** are verified by §8.7.

### 7.6 Outlining conventions

- Regions are functions on arrival: the front end outlines (a Julia macro, a clang attribute, a
  Rust closure trampoline); the dialect imposes no source syntax. The plugin additionally
  outlines coherent slices (TDL-3), which is not observable beyond §18.
- Action and reversible regions have type `void (ptr env)`. `env` points to classical memory the
  front end owns (an `alloca` or heap object) that is live for the duration of the marker call;
  the region reads and writes it as classical memory (§18.4). Handles reach a region through
  `env` (PT9 binds a region's parameter to the marker's env argument).
- Oracle regions are arbitrary functions bound by a descriptor (§8); no packing wrapper is
  needed (audit D21).
- A region body MUST be referenced by the region operand (directly or through §7.2); a body
  referenced only from a side-table global is not a region (enzyme survey implication 5).
- Region functions SHOULD have internal linkage, so that they are not device entries. C++
  lambdas pass their static `__invoke` thunk and Rust closures an `extern "C"` trampoline; both
  are ordinary region functions whose closure contains the closure body.

### 7.7 Examples

```llvm example=region-select verdict=accept candidates=ra,rb
define internal void @ra(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  ret void
}

define internal void @rb(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 2, ptr %h, i64 0)
  ret void
}

define void @top(i1 %c) {
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  %f = select i1 %c, ptr @ra, ptr @rb
  call void @__bennett_adj(ptr %f, ptr null, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

The SimplifyCFG switch-to-lookup shape (`region-switch-fnptr-table` after `default<O3>`):

```llvm example=region-switch-table verdict=accept candidates=ra,rb,rc,rd
@switch.table.top = private unnamed_addr constant [3 x ptr] [ptr @ra, ptr @rb, ptr @rc]

define internal void @ra(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  ret void
}

define internal void @rb(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 2, ptr %h, i64 0)
  ret void
}

define internal void @rc(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 3, ptr %h, i64 0)
  ret void
}

define internal void @rd(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 4, ptr %h, i64 0)
  ret void
}

define void @top(i64 %i) {
entry:
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  %in = icmp ult i64 %i, 3
  br i1 %in, label %look, label %dflt

look:
  %p = getelementptr [3 x ptr], ptr @switch.table.top, i64 0, i64 %i
  %ft = load ptr, ptr %p
  br label %join

dflt:
  br label %join

join:
  %f = phi ptr [ %ft, %look ], [ @rd, %dflt ]
  call void @__bennett_adj(ptr %f, ptr null, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

The `reg2mem` shape (a region pointer in a stack slot):

```llvm example=region-stack-slot verdict=accept candidates=ra,rb
define internal void @ra(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  ret void
}

define internal void @rb(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 2, ptr %h, i64 0)
  ret void
}

define void @top(i1 %c) {
entry:
  %slot = alloca ptr
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  br i1 %c, label %a, label %b

a:
  store ptr @ra, ptr %slot
  br label %join

b:
  store ptr @rb, ptr %slot
  br label %join

join:
  %f = load ptr, ptr %slot
  call void @__bennett_adj(ptr %f, ptr null, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

Merged twins resolve to one region (spike F2; `mergefunc` makes `@k2` a forwarding thunk,
`-mergefunc-use-aliases` makes an alias):

```llvm example=region-twins verdict=accept candidates=k1
@k3 = internal alias void (ptr), ptr @k1

define internal void @k1(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  ret void
}

define internal void @k2(ptr %0) {
  tail call void @k1(ptr %0)
  ret void
}

define void @top(i1 %c) {
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  %f = select i1 %c, ptr @k2, ptr @k3
  call void @__bennett_adj(ptr %f, ptr null, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

A region pointer from host input (a parameter of an externally visible function) has AV = ⊤,
so its candidates are every address-taken `void (ptr)` function of the program: here `@ra` and
`@rb`, whose addresses `@menu` returns to the host (audit B-33, decision 3):

```llvm example=region-host-param verdict=accept candidates=ra,rb
define internal void @ra(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  ret void
}

define internal void @rb(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 2, ptr %h, i64 0)
  ret void
}

define ptr @menu(i1 %c) {
  %f = select i1 %c, ptr @ra, ptr @rb
  ret ptr %f
}

define void @top(ptr %f) {
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  call void @__bennett_adj(ptr %f, ptr null, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

An `inttoptr` constant is dispatched the same way, and traps (`T-REGION`) on an execution where
it equals neither A(`@ra`) nor A(`@rb`); an external declaration is entered as a trapped call
(F(8)):

```llvm example=region-inttoptr verdict=accept candidates=ra
define internal void @ra(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  ret void
}

@keep = internal global ptr @ra

define void @top() {
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  call void @__bennett_adj(ptr inttoptr (i64 127079231243584 to ptr), ptr null, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=region-external verdict=accept candidates=elsewhere
declare void @elsewhere(ptr)

define void @top() {
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  call void @__bennett_adj(ptr @elsewhere, ptr null, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

A unique ill-formed candidate is rejected; one ill-formed member of a larger set is a trap body:

```llvm example=region-wrong-type verdict=reject:BD-E-REGION-TYPE
define internal i8 @inc(i8 %x) {
  %r = add i8 %x, 1
  ret i8 %r
}

define void @top() {
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  call void @__bennett_adj(ptr @inc, ptr null, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=region-mixed-types verdict=accept candidates=inc,ra
define internal i8 @inc(i8 %x) {
  %r = add i8 %x, 1
  ret i8 %r
}

define internal void @ra(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  ret void
}

define void @top(i1 %c) {
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  %f = select i1 %c, ptr @inc, ptr @ra
  call void @__bennett_adj(ptr %f, ptr null, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

Measurement inside `ctrl` is refused, unless the module asks for deferral:

```llvm example=region-measure-in-ctrl verdict=reject:BD-E-REGION-MEASURE
define internal void @body(ptr %e) {
  %h = load ptr, ptr %e
  %m = call i1 @__bennett_measure(ptr %h, i64 0)
  ret void
}

define void @top() {
  %e = alloca ptr
  %c = call ptr @__bennett_qalloc(i64 0, i64 1)
  %t = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %t, ptr %e
  call void @__bennett_ctrl(ptr %c, i64 0, ptr @body, ptr null, ptr %e)
  call void @__bennett_qfree(ptr %t)
  call void @__bennett_qfree(ptr %c)
  ret void
}
```

```llvm example=region-measure-deferred verdict=accept candidates=body
define internal void @body(ptr %e) {
entry:
  %h = load ptr, ptr %e
  %p = getelementptr i8, ptr %e, i64 8
  %t = load ptr, ptr %p
  %m = call i1 @__bennett_measure(ptr %h, i64 0)
  br i1 %m, label %flip, label %out

flip:
  call void @__bennett_gate(i32 1, ptr %t, i64 0)
  br label %out

out:
  ret void
}

define void @top() {
  %e = alloca [2 x ptr]
  %c = call ptr @__bennett_qalloc(i64 0, i64 1)
  %a = call ptr @__bennett_qalloc(i64 0, i64 1)
  %t = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %a, ptr %e
  %p = getelementptr i8, ptr %e, i64 8
  store ptr %t, ptr %p
  call void @__bennett_ctrl(ptr %c, i64 0, ptr @body, ptr null, ptr %e)
  call void @__bennett_qfree(ptr %t)
  call void @__bennett_qfree(ptr %a)
  call void @__bennett_qfree(ptr %c)
  ret void
}

!llvm.module.flags = !{!0}
!0 = !{i32 1, !"bennett.measure_in_unitary", !"defer"}
```

*(non-normative)* In `region-measure-deferred` the branch on `%m` is a Co branch (TDL-2), so the
gate on `%t` is issued under `qpred` of the copy wire (TDL-10): the action is
`ctl c (qcopy a.0 → w; cx w t.0)` with w released by the region's uncomputation, which is the
deferred-measurement principle.

A `reversible` call inside an action is a direct call of its body (§7.4); gate markers inside a
reversible closure act on handles from `env` (§7.5b); measurement there is refused:

```llvm example=region-reversible-in-action verdict=accept candidates=body
define internal void @classical(ptr %e) {
  %p = getelementptr i8, ptr %e, i64 8
  %v = load i64, ptr %p
  %v2 = add i64 %v, 1
  store i64 %v2, ptr %p
  ret void
}

define internal void @body(ptr %e) {
  call void @__bennett_reversible(ptr @classical, ptr null, ptr %e)
  ret void
}

define void @top() {
  %e = alloca { ptr, i64 }
  call void @__bennett_adj(ptr @body, ptr null, ptr %e)
  ret void
}
```

```llvm example=region-reversible-marker verdict=accept candidates=body
define internal void @body(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  ret void
}

define void @top() {
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  call void @__bennett_reversible(ptr @body, ptr null, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=region-reversible-measure verdict=reject:BD-E-REVERSIBLE-MEASURE
define internal void @body(ptr %e) {
  %h = load ptr, ptr %e
  %m = call i1 @__bennett_measure(ptr %h, i64 0)
  ret void
}

define void @top() {
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  call void @__bennett_reversible(ptr @body, ptr null, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

A register allocated in R and freed before the next allocation is hoisted to the CC caller
(self-disjoint, N = 1); one allocated per activation of a recursion whose depth comes from host
data has no bound and is BLK-4 (the same function in CC is realised directly, §6.5):

```llvm example=region-reversible-qalloc-static verdict=accept candidates=body
define internal void @body(ptr %e) {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  call void @__bennett_qfree(ptr %h)
  ret void
}

define void @top() {
  %e = alloca i64
  call void @__bennett_reversible(ptr @body, ptr null, ptr %e)
  ret void
}
```

```llvm example=region-reversible-qalloc-dynamic verdict=blocked:BD-B-ISA12
define internal void @rec(i64 %d) {
entry:
  %z = icmp eq i64 %d, 0
  br i1 %z, label %out, label %more

more:
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  %d2 = sub i64 %d, 1
  call void @rec(i64 %d2)
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  call void @__bennett_qfree(ptr %h)
  br label %out

out:
  ret void
}

define internal void @body(ptr %e) {
  %d = load i64, ptr %e
  call void @rec(i64 %d)
  ret void
}

define void @top(i64 %n) {
  %e = alloca i64
  store i64 %n, ptr %e
  call void @__bennett_reversible(ptr @body, ptr null, ptr %e)
  ret void
}
```

```text blocker=region-reversible-qalloc-dynamic
BD-B-ISA12 @rec %h: qalloc in a reversible closure with no instance bound (recursive, live across the recursive call: E = infinity); cannot be hoisted to the CC caller; ISA 0.8 qreg.new is CC only; BLK-4 (new ISA-12) qreg.* in R
```

## 8. The oracle interface (oracle-abi 0.2)

`__bennett_oracle(f, budget, desc)` applies the lifted oracle of region function f, under the
budget of §9, to the registers and classical values that the **descriptor** `desc` binds to f's
parameters, result and device models. `__bennett_inplace(g, ginv, budget, desc)` applies an
in-place bijection (§8.7). The descriptor is classical data in the caller's memory, built by
plain stores (§3.8); its kinds are classical values dispatched over their finite domains (§8.4).

### 8.1 Descriptor layout

The descriptor is the LLVM struct `{ H, [nparam x Bind], [ndev x DevBind] }` laid out by the
module's datalayout, where (C view in `bennett_markers.h`, §3.3):

| Type | LLVM | Fields (C names) |
|---|---|---|
| H | `{ i32, i32, i32, i32, ptr, ptr }` | `version` (= 2), `nparam`, `ndev`, `flags` (= 0), `tgt`, `fault` |
| Bind | `{ i32, i32, ptr, i64, i64 }` | `kind`, `mode`, `q`, `value`, `size` |
| DevBind | `{ i32, i32, ptr, i64 }` | `model`, `mode` (= 0), `q`, `value` |

On x86-64, AArch64 and RISC-V64 (pw = 64) H is 32 bytes, Bind 32 bytes (`kind` at 0, `mode` 4,
`q` 8, `value` 16, `size` 24) and DevBind 24 bytes, so `param[i]` is at 32 + 32i and `dev[j]` at
32 + 32·nparam + 24j. The plugin reads the descriptor at the marker call, in the caller's tier,
with ordinary loads. `nparam` MUST equal the number of IR parameters of the dispatched region
function (after ABI lowering: the IR signature). A descriptor whose `version`, `flags`, `nparam`
or any kind, mode or model is not one this section defines, or whose binding does not fit the
parameter's type (below), traps (`T-IFACE`, fault code 4) when the marker is called.

### 8.2 Parameter bindings

Let the dispatched region function have IR parameters p_0 … p_{m−1} and return type R (`void`
or a first-class type of at most 128 bits after N25, §12.2). `param[i]` binds p_i:

| Kind | Code | Parameter type | Register | Meaning | ISA lowering (§16.2) |
|---|---|---|---|---|---|
| `IN` | 1 | `iW` or `ptr` (W = pw) | q with n(q) ≤ W | the parameter's value is the basis value of q, zero-extended (`mode` = ZEXT 0) or sign-extended (`mode` = SEXT 1) to W; a `ptr` parameter may be `IN` (a superposed pointer) | an `ins` bundle `x<k>:wire[n(q)]` (a pseudo-location, ISA §3.7), extended by `lift.zext`/`lift.sext` in the wrapper |
| `ARG` | 2 | `iW` (W ≤ 128) or `ptr` | none (`q` ignored) | a classical value: bits 0–63 from `value`, bits 64–127 from `size`; a `ptr` ARG is an address in the caller's classical memory, which the oracle reads through its entry state (§8.5) | an `args` entry `a<k>:i<W>` (W = pw for `ptr`; ISA §4.7, §5.1) |
| `MEM_IN` | 3 | `ptr` | q with n(q) = 8·2^A, `size` = 2^A | the parameter is the base address of an interface region of 2^A bytes whose cell i is byte i of q (bits [8i, 8i + 8)); its contents may be superposed; role `in` (restored on every basis configuration, ISA §5.1). This is the quantum-addressed memory of NS §8 rung 4 | a `mem` region `m<k>:region[A,8] in`; the argument is `lift.addr @m<k>` |
| `OUT` | 4 | `ptr` | q with n(q) = 8·`size` | the parameter points to a fresh zero-filled buffer of `size` bytes in the oracle's memory; at exit its final bytes are XORed into q, byte k into wires [8k, 8k + 8) (a declared output, NS §4.2) | `lift.alloc size` in the wrapper; the bytes are part of the payload (§8.6) |
| `INOUT` | 5 | `iW` | q with n(q) = W | `inplace` only (§8.7): the in-place register x | `qinplace … x` |

The **result**: a non-null `tgt` register receives the return value: payload bits = the return
value zero-extended to n(tgt) if n(tgt) ≥ R's width; if n(tgt) is narrower, the dropped bits are
checked and an execution on which they are nonzero faults with code 4 (`FAULT_UB_TRAP`); the
retained bits are the low n(tgt). A null `tgt` discards the return value. For `oracle`, the
**fault register** `fault` MUST be a register of exactly 4 wires (ISA §5.4: F = 4) and MUST NOT
be null (`T-IFACE`).
Every register named by the descriptor MUST be live and pairwise distinct (`T-DEAD`, `T-ALIAS`).
A width mismatch in the table above is `T-SIZE`.

### 8.3 Device bindings

`dev[j]` binds a device model for the lifted (coherent) tier (§11.3):

| Model | Code | Register | Meaning |
|---|---|---|---|
| `ENTROPY` | 1 | q with n(q) = 8·2^A | an `in` region `e0:region[A,8]` holding the entropy tape, possibly superposed (NS §8 rung 8: "the entropy device is replaced by a superposed register") |
| `BLOCK` | 2 | q with n(q) = 8·512·2^A′ | an `in` region `k0` holding the disk image of 2^A′ sectors; writes go to a lifted copy-on-write overlay in the oracle's heap |
| `CLOCK` | 3 | none | the clock model's initial value is `value` |
| `CONSOLE` | 4 | q with n(q) = 8·L, or null | the first L bytes the oracle writes to the console are XORed into q as an output (payload, §8.6); with a null q console bytes are discarded with the oracle's other writes |

At most one binding per model. A model without a binding is **unbound**: an effect on it in L
code faults with code 8 on the executions that reach it (§11.3; NS §4.2).

### 8.4 Shapes and dispatch

A **shape** is the tuple (region candidate F; for each parameter its kind, mode, register width
n(q) and `size`; n(tgt) or "none"; for each device binding its model and n(q)). The kind, mode,
model, `size` and `value` fields have value sets (§5.3); register widths come from the register
file (§6.5), whose roots have known widths. The plugin compiles one reference object (§16.2) per
shape that the value sets allow, taking every unbounded kind or mode field over its finite
domain (5 kinds, 2 modes, 4 models), so the number of shapes is always bounded. At run time the
caller's tier reads the descriptor and selects the compiled shape with the compare tree of
§14.2; a descriptor that matches no compiled shape traps (`T-IFACE`), which happens only for a
field outside its table. `value` and `size` of `ARG` bindings are the oracle's classical
arguments and are not part of the shape. *(non-normative)* With constant stores every field has
a singleton value set and there is one shape per candidate.

The marker then issues, in the caller's tier, one **oracle invocation** (§8.6) whose operands are
the static registers the descriptor's handles denote (§6.5), the budget token (§9.5) and the
classical arguments.

### 8.5 Entry state

**Reference semantics.** The region function runs on a **private copy of the caller's whole
classical memory at the call**, with the bound inputs; its writes are discarded except through
`OUT`, `tgt` and the bound device outputs (NS §4.2: "every other write being restored
workspace"). Constant globals, and mutable globals that only the oracle's own L closure writes,
equal their initialisers at every call.

**Realisation on ISA 0.8.** Let R be the abstract objects the oracle closure may load (§5.4),
minus constant globals, minus mutable globals written by no function outside the L closure. If
R is empty, nothing is transferred: the oracle's globals start at their data images (ISA §3.7).
This is rung 4 route A (SQLite §5.2(i)). Otherwise the plugin emits an **entry-state transfer**:

1. **Snapshot.** At the call the caller's tier forms the byte string
   S = k ‖ (size_i ‖ live_i)_{i<k} ‖ G ‖ Hb, where k is the number of heap allocations in the
   caller's allocation table (in allocation order, ISA §7.1), `size_i` and `live_i` are 8-byte
   little-endian fields, G is the bytes of the mutable globals in R in `layout.globals` order,
   and Hb is the bytes of every live heap allocation in allocation order if R contains a heap
   object (else empty). S is zero-padded to 2^A_s bytes, where A_s is the smallest exponent with
   2^A_s ≥ 8 + 16·N_alloc + Σ|G| + `heap_limit_max` (N_alloc the allocation-table capacity of
   the layout, §19.5); A_s is static.
2. **Register.** The CC tier builds a register of 8·2^A_s wires holding S with a **concat
   tree** of A_s − 3 static-width CC functions `B_j` (j = 4, …, A_s): `B_4(p)` executes
   `qreg.new any 128`, loads the 16 bytes at p as two `i64` values and makes the `oracle_call`
   of the runtime oracle `@xor128` (§16.5) that XORs them into the register; `B_j(p)` (j > 4)
   returns `qreg.concat B_{j−1}(p) B_{j−1}(p + 2^{j−1})`. Every type is static and the cost is
   2^(A_s−4) region calls. The register is bound as an extra `in` region `s0:region[A_s,8]`.
3. **Replay.** The wrapper prologue (§16.2) calls the runtimes function
   `__bennett_rt_entry_replay(s0)`, which for i < k executes `__bennett_nz_alloc(size_i)` (ISA
   `lift.alloc`) and, if `live_i` = 0, `__bennett_nz_free` of the result. ISA §4.2 `lift.alloc`
   and ISA §7.1 `alloc` share the rule "bump + max(n, 1) from `heap_base`", so the replay
   reproduces the caller's heap addresses exactly (audit O-07). It then copies G into the
   globals (by the driver-generated table `__bennett_rt_entry_table` of their addresses and
   sizes) and Hb into the replayed live allocations.
4. **Release.** The snapshot register holds the basis state |S⟩ and is unentangled after every
   oracle call (an `in` region is unchanged on every basis configuration, ISA §5.2). The caller
   keeps it for later calls while no store to an object of R has executed since it was built,
   and releases it by `measure` (its outcome is S with probability 1 and is discarded) before
   the next build or at the end of the caller's run. *(non-normative)* A run that measures is not
   reversible (ISA §10); a CC program that calls oracles is not a whole-run reversal candidate.

The replay's rows, allocations and calls are part of the reference body and count against the
budget (§9.4). Entry-state transfer from R-tier code needs registers allocated in R (BLK-4,
§25.1); no rung uses it. **Build-time snapshots** (rung 7, §19.6) rewrite the initialisers of
the mutable globals to snapshot values at link time, so R is empty and nothing is transferred.
Efficiency: G-12 (§25.3).

### 8.6 Oracle invocations and wide outputs

The **outputs** of a shape are, in order: `tgt` (if non-null), each `OUT` parameter in parameter
order, and the `CONSOLE` register (if bound). Each output register is split into **slices** of
at most 128 bits from its low end (ISA §3.3: payloads are `iN` with N ≤ 128); the slices of all
outputs are numbered 0, 1, …, k − 1 in that order. Every slice j has an oracle **variant** W_j:
the same reference body (§16.2) whose `lift.retval` delivers slice j of the payload. All variants
compute the same fault code, so code(F_B) is one function of the inputs.

- **k = 1** (every output fits 128 bits in one register): the invocation is `oracle_call @W_0
  tk (ins..) tgt fault (mem..) (args..)`.
- **k > 1**: the invocation is an `action_call` of the permutation action `@wide` generated per
  shape, with `mut` = the k slice bundles and the fault register, `in` = the `ins` bundles,
  `mem` = the regions and `args` = the classical arguments, whose body is, for j = k − 1, …, 1:

  ```
  t_j = qalloc any w_j ; f_j = qalloc any 4
  oracle_call @W_j tk (ins..) t_j f_j (mem..) (args..)
  qxor t_j slice_j
  oracle_call @W_j tk (ins..) t_j f_j (mem..) (args..)
  qfree f_j ; qfree t_j
  ```

  followed by `oracle_call @W_0 tk (ins..) slice_0 fault (mem..) (args..)`.

  Each copy-out pair computes slice j into fresh wires, XORs it into the target and uncomputes it
  by the identical self-adjoint call, whose inputs no instruction in between modifies, so `t_j`
  and `f_j` are clean (ISA §6.2, §6.4 realisation `reverse`); slice 0 and the fault code are
  delivered by the last call. The action's effect is exactly NS's F_B with a wide payload:
  slice_j ⊕= payload_j(F_B(x)) for every j and fault ⊕= code(F_B(x)). Cost: 2k − 1 oracle
  calls (efficiency item G-15, §25.3).

### 8.7 In-place updates

`inplace(g, ginv, budget, desc)` binds the in-place register x as `INOUT` (exactly one
parameter of each candidate pair is `INOUT`, of type `iN` with N = n(x); the result type is
`iN`). g and ginv are oracles in the sense of §8.2 with a **payload equal to the new value of
x**: their reference objects (§16.2) bind x as an `in` bundle and have an n(x)-bit target. The
descriptor's `tgt` MUST be null and its `fault` is ignored (`T-IFACE` otherwise): an in-place
update has no fault outcome (NS §4.2), and the `qinplace` expansion allocates its own clean
scratch (ISA §4.5).

- **No other bindings**: the call lowers to ISA `qinplace @g @ginv tk x` (ISA §4.5) with @g,
  @ginv the reference oracles of the pair.
- **Classical `ARG`s with finite value sets**: one `qinplace` per tuple of argument values, each
  with the pair specialised to those constants (the arguments become `lift.const` in the
  reference bodies), dispatched by §14.2.
- **Library bijections**: when the pair is a `bennett-arith` library bijection (add or subtract
  a value, xor, rotate, negate, byte swap, modular addition, modular multiplication by a unit,
  each with its stated conditions and its g∘ginv = id certificate, NS §3.1), the call lowers to
  the library's permutation action with `IN`, `MEM_IN` and `ARG` bindings as its `in`, `mem` and
  `args` operands, which ISA 0.8 expresses directly (ISA §4.7 `action_call`). This is also the
  TDL-5(b) mechanism (§10).
- **User pairs with `IN` or `MEM_IN` bindings, or `ARG`s with unbounded value sets**: ISA 0.8's
  `qinplace` has no parameter lists. The verdict is `blocked:BD-B-ISA3` (BLK-3, §25.1): the full
  mechanism is specified here and needs the ISA change of §25.1.

**Verification.** For every compiled pair and every argument tuple, when N ≤ the configured
width (driver option `-bennett-inplace-exhaustive-bits`, default 24, §24), the plugin MUST run
the reference interpreter on both reference bodies with an unbounded budget and check that for
every x ∈ [0, 2^N), F^g(x) = (y, 0) and F^ginv(y) = (x, 0); it records the **minimal budget**
B_min, the componentwise maximum over all those runs of (rows, heap bytes, stack cells, depth).
Above that width it MUST record a `sampled` evidence claim (ISA §12.1) of the same check and
B_min over the sample, and the dynamic net applies: a wrong inverse leaves the scratch register
of the `qinplace` expansion non-clean, which `T-CLEAN` catches (NS §3.1). F_B is monotone in
the budget (a run that completes within B completes identically within every B′ ≥ B), so the
pair is valid for exactly the budgets B ≥ B_min. A pair that fails the check, or whose budget
is static and below B_min in some component, is `BD-E-INPLACE-NOT-INVERSE` (NS §3.1: "an
in-place update with no inverse fails loud at compile time"; "a fallible or budget-limited
computation cannot be in-place"); a run-time budget (§9.5) below B_min traps at the marker
(`T-BUDGET`). *(non-normative)* On a finite set, ginv∘g = id makes g injective, hence a
bijection, so g∘ginv = id and ginv is fault-free on every input, as ISA `qinplace` requires.
0.1's `BD-E-INPLACE-UNVERIFIED` is deleted.

### 8.8 Examples

`inc8` bound by a descriptor with one `IN`, called twice (the oracle is an involution, so every
register is released clean). The descriptor and budget record are built by merged constant
stores, as `default<O3>` emits them; the budget record asks for 5 steps, no heap, 7 stack cells
and depth 1 (§9.1; §16.6 computes these numbers):

```llvm example=oracle-inc8 verdict=accept candidates=inc8 shapes=1
define internal i8 @inc8(i8 %x) {
  %r = add i8 %x, 1
  ret i8 %r
}

define void @top() {
  %d = alloca [64 x i8], align 8
  %b = alloca [40 x i8], align 8
  %x = call ptr @__bennett_qalloc(i64 0, i64 8)
  %t = call ptr @__bennett_qalloc(i64 0, i64 8)
  %f = call ptr @__bennett_qalloc(i64 0, i64 4)
  store <4 x i64> <i64 5, i64 0, i64 7, i64 1>, ptr %b, align 8
  %bf = getelementptr i8, ptr %b, i64 32
  store ptr null, ptr %bf, align 8
  store <4 x i32> <i32 2, i32 1, i32 0, i32 0>, ptr %d, align 8
  %dt = getelementptr i8, ptr %d, i64 16
  store ptr %t, ptr %dt, align 8
  %df = getelementptr i8, ptr %d, i64 24
  store ptr %f, ptr %df, align 8
  %p0 = getelementptr i8, ptr %d, i64 32
  store <2 x i32> <i32 1, i32 0>, ptr %p0, align 8
  %p0q = getelementptr i8, ptr %d, i64 40
  store ptr %x, ptr %p0q, align 8
  %p0v = getelementptr i8, ptr %d, i64 48
  store <2 x i64> zeroinitializer, ptr %p0v, align 8
  call void @__bennett_oracle(ptr @inc8, ptr %b, ptr %d)
  call void @__bennett_oracle(ptr @inc8, ptr %b, ptr %d)
  call void @__bennett_qfree(ptr %f)
  call void @__bennett_qfree(ptr %t)
  call void @__bennett_qfree(ptr %x)
  ret void
}
```

A two-argument function needs no packing wrapper (audit D21): two `IN` bindings, one 9-bit
target (the `zext` to `i9` makes the sum exact):

```llvm example=oracle-two-in verdict=accept candidates=add shapes=1
define internal i9 @add(i8 %a, i8 %b) {
  %a9 = zext i8 %a to i9
  %b9 = zext i8 %b to i9
  %s = add i9 %a9, %b9
  ret i9 %s
}

define void @top() {
  %d = alloca [96 x i8], align 8
  %qa = call ptr @__bennett_qalloc(i64 0, i64 8)
  %qb = call ptr @__bennett_qalloc(i64 0, i64 8)
  %t = call ptr @__bennett_qalloc(i64 0, i64 9)
  %f = call ptr @__bennett_qalloc(i64 0, i64 4)
  store <4 x i32> <i32 2, i32 2, i32 0, i32 0>, ptr %d, align 8
  %dt = getelementptr i8, ptr %d, i64 16
  store ptr %t, ptr %dt, align 8
  %df = getelementptr i8, ptr %d, i64 24
  store ptr %f, ptr %df, align 8
  %p0 = getelementptr i8, ptr %d, i64 32
  store <2 x i32> <i32 1, i32 0>, ptr %p0, align 8
  %p0q = getelementptr i8, ptr %d, i64 40
  store ptr %qa, ptr %p0q, align 8
  %p0v = getelementptr i8, ptr %d, i64 48
  store <2 x i64> zeroinitializer, ptr %p0v, align 8
  %p1 = getelementptr i8, ptr %d, i64 64
  store <2 x i32> <i32 1, i32 0>, ptr %p1, align 8
  %p1q = getelementptr i8, ptr %d, i64 72
  store ptr %qb, ptr %p1q, align 8
  %p1v = getelementptr i8, ptr %d, i64 80
  store <2 x i64> zeroinitializer, ptr %p1v, align 8
  call void @__bennett_oracle(ptr @add, ptr null, ptr %d)
  call void @__bennett_oracle(ptr @add, ptr null, ptr %d)
  call void @__bennett_qfree(ptr %f)
  call void @__bennett_qfree(ptr %t)
  call void @__bennett_qfree(ptr %qb)
  call void @__bennett_qfree(ptr %qa)
  ret void
}
```

A kind chosen at run time gives two shapes, `ARG` and `IN` for the second parameter; a classical
value read by the caller from host input is the `ARG` value:

```llvm example=oracle-two-shapes verdict=accept candidates=add shapes=2
define internal i9 @add(i8 %a, i8 %b) {
  %a9 = zext i8 %a to i9
  %b9 = zext i8 %b to i9
  %s = add i9 %a9, %b9
  ret i9 %s
}

define void @top(i1 %quantum_b, i64 %bval) {
  %d = alloca [96 x i8], align 8
  %qa = call ptr @__bennett_qalloc(i64 0, i64 8)
  %qb = call ptr @__bennett_qalloc(i64 0, i64 8)
  %t = call ptr @__bennett_qalloc(i64 0, i64 9)
  %f = call ptr @__bennett_qalloc(i64 0, i64 4)
  store <4 x i32> <i32 2, i32 2, i32 0, i32 0>, ptr %d, align 8
  %dt = getelementptr i8, ptr %d, i64 16
  store ptr %t, ptr %dt, align 8
  %df = getelementptr i8, ptr %d, i64 24
  store ptr %f, ptr %df, align 8
  %p0 = getelementptr i8, ptr %d, i64 32
  store <2 x i32> <i32 1, i32 0>, ptr %p0, align 8
  %p0q = getelementptr i8, ptr %d, i64 40
  store ptr %qa, ptr %p0q, align 8
  %p0v = getelementptr i8, ptr %d, i64 48
  store <2 x i64> zeroinitializer, ptr %p0v, align 8
  %k1 = select i1 %quantum_b, i32 1, i32 2
  %p1 = getelementptr i8, ptr %d, i64 64
  store i32 %k1, ptr %p1, align 8
  %p1m = getelementptr i8, ptr %d, i64 68
  store i32 0, ptr %p1m, align 4
  %p1q = getelementptr i8, ptr %d, i64 72
  store ptr %qb, ptr %p1q, align 8
  %p1v = getelementptr i8, ptr %d, i64 80
  store i64 %bval, ptr %p1v, align 8
  %p1s = getelementptr i8, ptr %d, i64 88
  store i64 0, ptr %p1s, align 8
  call void @__bennett_oracle(ptr @add, ptr null, ptr %d)
  call void @__bennett_oracle(ptr @add, ptr null, ptr %d)
  call void @__bennett_qfree(ptr %f)
  call void @__bennett_qfree(ptr %t)
  call void @__bennett_qfree(ptr %qb)
  call void @__bennett_qfree(ptr %qa)
  ret void
}
```

A 160-bit output (an `OUT` buffer of 20 bytes) has k = 2 slices, [0, 128) and [128, 160) of the
`OUT` register, so the invocation is the `@wide` action with 2k − 1 = 3 oracle calls (§8.6):

```llvm example=oracle-wide-out verdict=accept candidates=fill20 shapes=1
define internal void @fill20(ptr %out, i8 %x) {
entry:
  br label %loop

loop:
  %i = phi i64 [ 0, %entry ], [ %i2, %loop ]
  %ti = trunc i64 %i to i8
  %v = xor i8 %x, %ti
  %p = getelementptr i8, ptr %out, i64 %i
  store i8 %v, ptr %p
  %i2 = add i64 %i, 1
  %c = icmp ult i64 %i2, 20
  br i1 %c, label %loop, label %done

done:
  ret void
}

define void @top() {
  %d = alloca [96 x i8], align 8
  %qx = call ptr @__bennett_qalloc(i64 0, i64 8)
  %qo = call ptr @__bennett_qalloc(i64 0, i64 160)
  %f = call ptr @__bennett_qalloc(i64 0, i64 4)
  store <4 x i32> <i32 2, i32 2, i32 0, i32 0>, ptr %d, align 8
  %dt = getelementptr i8, ptr %d, i64 16
  store ptr null, ptr %dt, align 8
  %df = getelementptr i8, ptr %d, i64 24
  store ptr %f, ptr %df, align 8
  %p0 = getelementptr i8, ptr %d, i64 32
  store <2 x i32> <i32 4, i32 0>, ptr %p0, align 8
  %p0q = getelementptr i8, ptr %d, i64 40
  store ptr %qo, ptr %p0q, align 8
  %p0v = getelementptr i8, ptr %d, i64 48
  store <2 x i64> <i64 0, i64 20>, ptr %p0v, align 8
  %p1 = getelementptr i8, ptr %d, i64 64
  store <2 x i32> <i32 1, i32 0>, ptr %p1, align 8
  %p1q = getelementptr i8, ptr %d, i64 72
  store ptr %qx, ptr %p1q, align 8
  %p1v = getelementptr i8, ptr %d, i64 80
  store <2 x i64> zeroinitializer, ptr %p1v, align 8
  call void @__bennett_oracle(ptr @fill20, ptr null, ptr %d)
  call void @__bennett_oracle(ptr @fill20, ptr null, ptr %d)
  call void @__bennett_qfree(ptr %f)
  call void @__bennett_qfree(ptr %qo)
  call void @__bennett_qfree(ptr %qx)
  ret void
}
```

In-place pairs (§8.7): a verified pair, a wrong inverse, a classical parameter with a finite
value set (one `qinplace` per value), and a quantum parameter (BLK-3). The descriptor of
`inplace` has `tgt` = null; the INOUT register is `param[0].q`:

```llvm example=inplace-call verdict=accept candidates=add5,sub5
define internal i8 @add5(i8 %x) {
  %r = add i8 %x, 5
  ret i8 %r
}

define internal i8 @sub5(i8 %x) {
  %r = add i8 %x, 251
  ret i8 %r
}

define void @top() {
  %d = alloca [64 x i8], align 8
  %x = call ptr @__bennett_qalloc(i64 0, i64 8)
  %f = call ptr @__bennett_qalloc(i64 0, i64 4)
  store <4 x i32> <i32 2, i32 1, i32 0, i32 0>, ptr %d, align 8
  %dt = getelementptr i8, ptr %d, i64 16
  store ptr null, ptr %dt, align 8
  %df = getelementptr i8, ptr %d, i64 24
  store ptr %f, ptr %df, align 8
  %p0 = getelementptr i8, ptr %d, i64 32
  store <2 x i32> <i32 5, i32 0>, ptr %p0, align 8
  %p0q = getelementptr i8, ptr %d, i64 40
  store ptr %x, ptr %p0q, align 8
  %p0v = getelementptr i8, ptr %d, i64 48
  store <2 x i64> zeroinitializer, ptr %p0v, align 8
  call void @__bennett_inplace(ptr @add5, ptr @sub5, ptr null, ptr %d)
  call void @__bennett_inplace(ptr @sub5, ptr @add5, ptr null, ptr %d)
  call void @__bennett_qfree(ptr %f)
  call void @__bennett_qfree(ptr %x)
  ret void
}
```

```llvm example=inplace-wrong-inverse verdict=reject:BD-E-INPLACE-NOT-INVERSE
define internal i8 @add5(i8 %x) {
  %r = add i8 %x, 5
  ret i8 %r
}

define void @top() {
  %d = alloca [64 x i8], align 8
  %x = call ptr @__bennett_qalloc(i64 0, i64 8)
  %f = call ptr @__bennett_qalloc(i64 0, i64 4)
  store <4 x i32> <i32 2, i32 1, i32 0, i32 0>, ptr %d, align 8
  %dt = getelementptr i8, ptr %d, i64 16
  store ptr null, ptr %dt, align 8
  %df = getelementptr i8, ptr %d, i64 24
  store ptr %f, ptr %df, align 8
  %p0 = getelementptr i8, ptr %d, i64 32
  store <2 x i32> <i32 5, i32 0>, ptr %p0, align 8
  %p0q = getelementptr i8, ptr %d, i64 40
  store ptr %x, ptr %p0q, align 8
  %p0v = getelementptr i8, ptr %d, i64 48
  store <2 x i64> zeroinitializer, ptr %p0v, align 8
  call void @__bennett_inplace(ptr @add5, ptr @add5, ptr null, ptr %d)
  call void @__bennett_qfree(ptr %f)
  call void @__bennett_qfree(ptr %x)
  ret void
}
```

```llvm example=inplace-arg-finite verdict=accept candidates=addk,subk
define internal i8 @addk(i8 %x, i8 %k) {
  %r = add i8 %x, %k
  ret i8 %r
}

define internal i8 @subk(i8 %x, i8 %k) {
  %r = sub i8 %x, %k
  ret i8 %r
}

define void @top(i1 %big) {
  %d = alloca [96 x i8], align 8
  %x = call ptr @__bennett_qalloc(i64 0, i64 8)
  %f = call ptr @__bennett_qalloc(i64 0, i64 4)
  store <4 x i32> <i32 2, i32 2, i32 0, i32 0>, ptr %d, align 8
  %dt = getelementptr i8, ptr %d, i64 16
  store ptr null, ptr %dt, align 8
  %df = getelementptr i8, ptr %d, i64 24
  store ptr %f, ptr %df, align 8
  %p0 = getelementptr i8, ptr %d, i64 32
  store <2 x i32> <i32 5, i32 0>, ptr %p0, align 8
  %p0q = getelementptr i8, ptr %d, i64 40
  store ptr %x, ptr %p0q, align 8
  %p0v = getelementptr i8, ptr %d, i64 48
  store <2 x i64> zeroinitializer, ptr %p0v, align 8
  %k = select i1 %big, i64 7, i64 1
  %p1 = getelementptr i8, ptr %d, i64 64
  store <2 x i32> <i32 2, i32 0>, ptr %p1, align 8
  %p1q = getelementptr i8, ptr %d, i64 72
  store ptr null, ptr %p1q, align 8
  %p1v = getelementptr i8, ptr %d, i64 80
  store i64 %k, ptr %p1v, align 8
  %p1s = getelementptr i8, ptr %d, i64 88
  store i64 0, ptr %p1s, align 8
  call void @__bennett_inplace(ptr @addk, ptr @subk, ptr null, ptr %d)
  call void @__bennett_qfree(ptr %f)
  call void @__bennett_qfree(ptr %x)
  ret void
}
```

```llvm example=inplace-param-quantum verdict=blocked:BD-B-ISA3
define internal i8 @addk(i8 %x, i8 %k) {
  %r = add i8 %x, %k
  ret i8 %r
}

define internal i8 @subk(i8 %x, i8 %k) {
  %r = sub i8 %x, %k
  ret i8 %r
}

define void @top() {
  %d = alloca [96 x i8], align 8
  %x = call ptr @__bennett_qalloc(i64 0, i64 8)
  %y = call ptr @__bennett_qalloc(i64 0, i64 8)
  %f = call ptr @__bennett_qalloc(i64 0, i64 4)
  store <4 x i32> <i32 2, i32 2, i32 0, i32 0>, ptr %d, align 8
  %dt = getelementptr i8, ptr %d, i64 16
  store ptr null, ptr %dt, align 8
  %df = getelementptr i8, ptr %d, i64 24
  store ptr %f, ptr %df, align 8
  %p0 = getelementptr i8, ptr %d, i64 32
  store <2 x i32> <i32 5, i32 0>, ptr %p0, align 8
  %p0q = getelementptr i8, ptr %d, i64 40
  store ptr %x, ptr %p0q, align 8
  %p0v = getelementptr i8, ptr %d, i64 48
  store <2 x i64> zeroinitializer, ptr %p0v, align 8
  %p1 = getelementptr i8, ptr %d, i64 64
  store <2 x i32> <i32 1, i32 0>, ptr %p1, align 8
  %p1q = getelementptr i8, ptr %d, i64 72
  store ptr %y, ptr %p1q, align 8
  %p1v = getelementptr i8, ptr %d, i64 80
  store <2 x i64> zeroinitializer, ptr %p1v, align 8
  call void @__bennett_inplace(ptr @addk, ptr @subk, ptr null, ptr %d)
  call void @__bennett_qfree(ptr %f)
  call void @__bennett_qfree(ptr %y)
  call void @__bennett_qfree(ptr %x)
  ret void
}
```

```text blocker=inplace-param-quantum
BD-B-ISA3 @top call @__bennett_inplace(@addk, @subk): parameter 1 is bound IN (register %y); ISA 0.8 qinplace has no (ins..) (mem..) (args..); BLK-3 (ISA-3) qinplace @g @ginv tk x (ins..) (mem..) (args..)
```

## 9. Budgets

NS §3.1: a region-level classical budget of "dynamic steps, heap bytes and recursion depth,
passed as ordinary integer operands of the region-entry marker or supplied out of band by the
host or driver (a project-wide default, a per-function table) … No per-loop source annotation is
ever required". Budgets are the ISA's four components (ISA §5.4).

### 9.1 The budget record

Every region-entry marker takes a `ptr` to a **budget record** (outline E1, E12), the LLVM struct
`{ i64, i64, i64, i64, ptr }` under the datalayout (C `bennett_budget`, §3.3):

| Field | Meaning |
|---|---|
| `steps` | B: reference-interpreter rows (§9.4) |
| `heap` | `heap_limit`: heap bytes (ISA §5.4) |
| `stack` | `stack_limit`: lifted stack cells (ISA §3.7) |
| `depth` | `depth_limit`: call depth |
| `fault` | action regions only: the caller's fault register (4 wires) that receives the combined fault of the region's coherent slices (§10, TDL-8), or null |

A field equal to `BENNETT_BUDGET_TABLE` (all ones) takes its value from the budget table
(§9.2). A null record means all four budget fields come from the table and `fault` is null. For
`oracle` and `inplace` the `fault` field is ignored: the descriptor names the fault register
(§8.2).

### 9.2 The budget table

The **budget table** is a driver input (`--bennett-budgets=<file>`), one JSON document in RFC
8785 canonical form:

```
{ "version": "0.2",
  "defaults": { "steps": D, "heap": D, "stack": D, "depth": D, "sstack": D },
  "entries": [ { ("identity": HEX64 | "region_key": HEX64 | "symbol": GLOB),
                 "steps"?: D, "heap"?: D, "stack"?: D, "depth"?: D, "sstack"?: D } … ] }
```

with D a decimal string. An entry matches a region by its identity (§7.3, the interface hash of
`@ref` of one shape), its region key (§7.3), or a glob over the source symbol name of the region
function (`*` and `?`). For each component a region takes, in order of precedence, the first
entry matching by identity, then by region key, then by symbol (in array order), that names the
component, else the default. Defaults absent from the table and from
`--bennett-budget-default=<s,h,st,d,ss>` are 1048576 steps, 1048576 heap bytes, 65536 stack
cells, depth 256 and `sstack` 65536 (§24). `sstack` is the shadow-stack size in bytes (§17.3),
part of the heap budget. The driver resolves every symbol entry to identities and records the
resolved table and its SHA-256 in the build record (§19.9).

```json budget-table=rung4-mini
{"defaults":{"depth":"256","heap":"1048576","sstack":"65536","stack":"65536","steps":"1048576"},"entries":[{"depth":"8","heap":"0","stack":"512","steps":"400","symbol":"q"}],"version":"0.2"}
```

*(non-normative)* The entry above is the budget of the reduced rung-4 oracle of §16.7 by symbol;
its `sstack` comes from the default.

### 9.3 What each budget governs

| Region | Budget | Exhaustion |
|---|---|---|
| `oracle`, `inplace` | the token of every oracle invocation (ISA §5.4, §10 `bennett_budget`) | F_B = (0, `FAULT_BUDGET_STEPS` / `_HEAP` / `_DEPTH`) on that input (ISA §5.2) |
| `ctrl`, `adj`, `compute` | the token of **every coherent slice** of the invocation, each with the full record (outline E2) | that slice's fault code, combined into the action's fault register (TDL-8) |
| `reversible`, and the whole-program R mode | an R-tier step, heap and depth counter (§17.6) | the R run ends with a budget fault record (§17.6) |
| device CC code outside regions | none: classical control is "genuinely dynamic" (NS §4.2) | – |

### 9.4 The budget unit

One step is one reference-interpreter row of the reference object (ISA §14.1): the wrapper of
§16.2 (including the entry-state replay of §8.5 and the shadow-stack setup of §17.3) and every
lproc row, so the fault set is a property of the program, the budget, the LLVM version and
pipeline, the normaliser and mapping versions and the runtimes version, never of the plugin's
lowering (NS §4.2). Heap bytes are counted by `lift.alloc` (`heap_used + max(n, 1)`), stack cells
by `lift.call` (R_f cells per call, ISA §3.7, monotonic), depth by `lift.call`/`lift.ret`. The
R-tier unit is §17.6.

### 9.5 Run-time budgets

A budget field of a record is resolved, in this order:

1. **Static**: a constant, `BENNETT_BUDGET_TABLE`, or a finite value set (§5.3). The driver's
   launch stub mints one token per (reference object, budget tuple) with `bennett_budget` (ISA
   §10) at launch and passes them to the CC entry as `TOKEN` arguments; the CC code selects one
   by the compare tree of §14.2.
2. **Launch-supplied**: a field whose abstract value is a bitwise copy of an integer parameter of
   the device entry (its atoms come only from PT11 for that parameter). The launch stub mints the
   token from the host's argument value before `bennett_run`, for every reference object the
   record may reach (a finite set), and passes it as a `TOKEN` argument. A value that
   `bennett_budget` rejects (ISA §5.4 validation) makes the stub fail the launch with that status.
3. **Device-computed**: any other field (arithmetic on inputs, values derived from measurement
   results). ISA 0.8 has no instruction that mints a token from a device value: the verdict is
   `blocked:BD-B-ISA1` (BLK-2, §25.1), naming the field.

Exhaustion is always a fault outcome on the inputs that exhaust it (NS §3.1, §4.2), never a
compile error and never a truncated result. Rounding a run-time budget to a pre-minted value is
not permitted: it would change F_B (outline B5).

```llvm example=budget-launch-arg verdict=accept candidates=inc8 shapes=1
define internal i8 @inc8(i8 %x) {
  %r = add i8 %x, 1
  ret i8 %r
}

define void @run(i64 %steps) {
  %d = alloca [64 x i8], align 8
  %b = alloca [40 x i8], align 8
  %x = call ptr @__bennett_qalloc(i64 0, i64 8)
  %t = call ptr @__bennett_qalloc(i64 0, i64 8)
  %f = call ptr @__bennett_qalloc(i64 0, i64 4)
  store i64 %steps, ptr %b, align 8
  %b1 = getelementptr i8, ptr %b, i64 8
  store <2 x i64> <i64 -1, i64 -1>, ptr %b1, align 8
  %b3 = getelementptr i8, ptr %b, i64 24
  store i64 -1, ptr %b3, align 8
  %bf = getelementptr i8, ptr %b, i64 32
  store ptr null, ptr %bf, align 8
  store <4 x i32> <i32 2, i32 1, i32 0, i32 0>, ptr %d, align 8
  %dt = getelementptr i8, ptr %d, i64 16
  store ptr %t, ptr %dt, align 8
  %df = getelementptr i8, ptr %d, i64 24
  store ptr %f, ptr %df, align 8
  %p0 = getelementptr i8, ptr %d, i64 32
  store <2 x i32> <i32 1, i32 0>, ptr %p0, align 8
  %p0q = getelementptr i8, ptr %d, i64 40
  store ptr %x, ptr %p0q, align 8
  %p0v = getelementptr i8, ptr %d, i64 48
  store <2 x i64> zeroinitializer, ptr %p0v, align 8
  call void @__bennett_oracle(ptr @inc8, ptr %b, ptr %d)
  call void @__bennett_oracle(ptr @inc8, ptr %b, ptr %d)
  call void @__bennett_qfree(ptr %f)
  call void @__bennett_qfree(ptr %t)
  call void @__bennett_qfree(ptr %x)
  ret void
}
```

```llvm example=budget-device-computed verdict=blocked:BD-B-ISA1
define internal i8 @inc8(i8 %x) {
  %r = add i8 %x, 1
  ret i8 %r
}

define void @run(i64 %n) {
  %d = alloca [64 x i8], align 8
  %b = alloca [40 x i8], align 8
  %x = call ptr @__bennett_qalloc(i64 0, i64 8)
  %t = call ptr @__bennett_qalloc(i64 0, i64 8)
  %f = call ptr @__bennett_qalloc(i64 0, i64 4)
  %m = call i1 @__bennett_measure(ptr %x, i64 0)
  %extra = select i1 %m, i64 %n, i64 0
  %steps = add i64 %extra, 5
  store i64 %steps, ptr %b, align 8
  %b1 = getelementptr i8, ptr %b, i64 8
  store <2 x i64> <i64 -1, i64 -1>, ptr %b1, align 8
  %b3 = getelementptr i8, ptr %b, i64 24
  store i64 -1, ptr %b3, align 8
  %bf = getelementptr i8, ptr %b, i64 32
  store ptr null, ptr %bf, align 8
  store <4 x i32> <i32 2, i32 1, i32 0, i32 0>, ptr %d, align 8
  %dt = getelementptr i8, ptr %d, i64 16
  store ptr %t, ptr %dt, align 8
  %df = getelementptr i8, ptr %d, i64 24
  store ptr %f, ptr %df, align 8
  %p0 = getelementptr i8, ptr %d, i64 32
  store <2 x i32> <i32 1, i32 0>, ptr %p0, align 8
  %p0q = getelementptr i8, ptr %d, i64 40
  store ptr %x, ptr %p0q, align 8
  %p0v = getelementptr i8, ptr %d, i64 48
  store <2 x i64> zeroinitializer, ptr %p0v, align 8
  call void @__bennett_oracle(ptr @inc8, ptr %b, ptr %d)
  call void @__bennett_qfree(ptr %f)
  call void @__bennett_qfree(ptr %t)
  call void @__bennett_qfree(ptr %x)
  ret void
}
```

```text blocker=budget-device-computed
BD-B-ISA1 @run call @__bennett_oracle(@inc8): budget field steps = 5 + select(measure, %n, 0) is computed on the device; ISA 0.8 mints tokens only at launch; BLK-2 (ISA-1) CC tk = budget.mint @region s h st d
```

*(non-normative)* In `budget-device-computed` the oracle's budget depends on a measurement
outcome: NS §4.2 "run-time budgets come from the host or from measurement results". The value
set of `%steps` is ⊤ (it contains `%n`), so it is neither static nor a bitwise copy of a launch
argument.

## 10. Taint-driven lifting under control (tdl 0.2)

NS §0: "a way to condition a region on a qubit. Everything else is inferred"; NS §3.1 taint row:
a context-sensitive interprocedural analysis "over data dependence, control dependence and
memory effects, from marker results and region entries … with polyvariant specialisation". This
section replaces 0.1's generation-only semantics, in which classical stores of a `ctrl` body
happened on both branches of the control (audit 1.4-d, R1). Rule ids TDL-1 to TDL-12 are
normative anchors. ISA 0.8 expresses every construct below: actions call oracles (ISA §5.3,
§4.7) and CC issues controlled region calls (ISA §4.7 `ctl w <call>`).

**TDL-1 Interface vs body.** The marker fixes the interface: `ctrl`, `adj` and `compute` give an
action; `oracle` and `inplace` give an oracle. The body of an action region is partitioned by
content (TDL-3) and is never rejected for containing classical code.

**TDL-2 Coherence states.**

- **Object state.** Every instance of an abstract object X has a dynamic state K(X) ∈ {Cl, M,
  Co}, kept by the CC tier (a runtimes table for globals, the coherent allocator's bookkeeping
  for heap objects; §11, §17): Cl (the CC **shadow** holds X's bytes; X's arena cells are |0⟩),
  M (materialised: the arena cells hold the same bytes as a basis state; both are valid), Co
  (the arena is the truth and may be superposed; the shadow is invalid). Every instance starts
  Cl. Transitions: Cl → M by **materialisation** (an uncontrolled XOR of the shadow into the
  arena cells, TDL-4); M → Cl by the same XOR (dematerialisation, before a CC store to X); M or
  Cl → Co when an event is applied (§18.2) that writes X's cells with a non-empty control set or
  with a Co value; Co → Cl by `__bennett_observe` of all of X's bytes (TDL-11) or by its release
  (free, end of lifetime).
- **Value state.** During a generation (§18.4) every executed SSA value instance is Cl or Co:
  Co iff it is a deferred measurement result (§7.5a), a load of a byte whose **view** (below) is
  Co, the result of an instruction with a Co operand, or a `phi` at the join of a Co branch.
- **View.** A generation sees outliving memory through a **view**: a byte of object X has view
  Co if K(X) = Co, or if the generation's recorder (or a recorder of an enclosing generation of
  the same invocation) holds an event that writes it with a non-empty control set or with a Co
  value; otherwise its view is Cl and its value is the shadow updated by the recorder's own
  classical events. *(non-normative)* Inside `ctrl(q, f)` the body's own stores are recorded
  without q (q is added when the generation ends, TDL-6), so f sees its own writes classically,
  as the q = 1 branch must; an inner `ctrl(q2, g)` records g's writes with q2, so f's later reads
  of them are Co.
- **Static may-Co analysis MC** (decides partitions, arena placement and the verdict rules
  below; flow-sensitive, interprocedural over the CC call graph with one summary per (function,
  coherence signature), merge by union, least fixpoint):
  - MC1: the state at a program point is the set of abstract objects that may have K = Co there;
  - MC2: after an action region invocation (`ctrl`, `adj`, `compute`, or a `reversible` call
    reached from a generation, §7.4), add every outliving object (TDL-5) that a store in the
    closure of a candidate may write, if the invocation is `ctrl` or the store may be under an
    inner control, may store a may-Co value, or may be control-dependent on a may-Co branch;
  - MC3: `__bennett_observe(p, len)` removes an object X when AV(p) = {(X, 0)} and len is a
    constant ≥ size(X); otherwise no change;
  - MC4: a value may be Co if an operand may be Co, it is a load whose AV(p) contains a may-Co
    object, or it is control-dependent on a may-Co branch; an object that a may-Co value is
    stored into is may-Co after the store;
  - MC5: calls bind the coherence signature of the callee (which parameters may be Co, and the
    may-Co set at entry); every distinct signature is a variant (§4.3).
- **Interprocedural and context-sensitive** by coherence signature (MC5; NS §3.1).

**TDL-3 Partition.** For each variant of an action region and of its CC callees:

- **G (generation)**: the instructions MC does not mark may-Co. G runs in CC, once per
  invocation (§18.4).
- **Slices**: every maximal single-entry single-exit region of may-Co instructions other than
  stores to outliving objects and marker calls is outlined (LLVM `CodeExtractor`) into a
  **slice function** S_k, with: classical live-ins → `ARG` parameters; Co live-ins → `IN`
  parameters; may-Co objects it loads → the arena, bound as a `MEM_IN` region `coh`; Co
  live-outs → outputs (§8.6). An irreducible may-Co region is outlined as a whole function. S_k
  is normalised (§12) and lifted (§16) like any oracle region; its entry state is the
  generation's view (§8.5: the arena for may-Co objects, the shadow for the rest). Each slice
  also keeps its original instructions as a **classical twin** in G.
- At run time the generation runs the classical twin when every live-in of the slice is Cl and
  every object it may load has view Cl; otherwise it records a **slice invocation**: before it,
  every live instance of a may-Co object the slice may load whose state is Cl is materialised
  (Cl → M); the invocation computes the Co live-outs into fresh registers (`compute` events,
  §18.2).
- **Stores to outliving objects** and **marker calls** are never inside slices: they become
  events (TDL-5, TDL-10). A store or marker call that is control-dependent on a Co branch is
  recorded under the branch's condition wire (TDL-10). A Co branch is if-converted: the
  generation executes both arms (each arm's Cl instructions classically, its events predicated on
  the condition or its negation) and the join's `phi`s become slice-computed selects.

**TDL-4 Coherent arena.**

- The objects in any may-Co set of MC are placed in the **arena**: a static address range
  [A_coh, A_coh + 2^A) of the layout, disjoint from CC globals and heap (ISA §7.1, §7.2; G-13
  would lift the restriction). Globals in the set are relocated into the arena by the layout
  (§19.5) in both builds, so their addresses stay native-equal; heap objects of may-Co allocation
  sites are allocated by the runtimes' **coherent allocator** in the arena range in both builds.
- The arena's contents are a CC-held register of 8·2^A wires, bound to every slice and arena
  action as `region[A,8]` (ISA §3.3 binding); cell i is the byte at address A_coh + i.
- The **shadow** of the arena is the CC global `__bennett_rt_shadow` of 2^A bytes at
  A_coh + Δ_sh (a layout constant); CC loads and stores whose abstract address may lie in the
  arena are rewritten to address + Δ_sh when the object's state is Cl or M, after
  dematerialising an M object for a store; when the state is Co, TDL-11 applies.
- **Writing at a run-time address.** A cell write of a classical mask m at a classical run-time
  address a (an `xmask` event, a materialisation) lowers to an action that calls the runtime
  oracle `@xorargs` (§16.5) to XOR the classical `args` (a, m) into fresh wires a_w, m_w, then
  `qstore coh a_w m_w` (ISA §4.6: XOR into the addressed cell; O(2^A) gates unless the target has
  QRAM, NS §4.3), then `@xorargs` again to uncompute a_w and m_w. Objects at static offsets MAY
  use a static slice (`qreg.slice` with a literal `lo`) and X gates instead.

**TDL-5 Stores to outliving objects (the store rule).** An object **outlives** an invocation if
it is live after it: a global, an object reachable from `env`, or a heap object not freed in the
invocation. A store `store v, ptr p` executed during a generation to an outliving object X is
realised by cases on the view of the bytes it writes:

- **(a) View Cl** (the old bytes c are known to CC).
  - v and p Cl: the event `xmask X+o, c ⊕ v` (o = p − X's base).
  - v or p Co: a slice invocation O computes the address and the mask c ⊕ v into fresh
    registers (c is a classical argument of O); the event `xstore coh a_w m_w` XORs the mask
    into the addressed cells (`qstore`); a second identical invocation of O uncomputes the
    registers. O never loads X's written bytes from the arena (their view is Cl, so O receives
    them as arguments), and no instruction between the two invocations writes anything O reads,
    so the second invocation cleans them exactly (ISA §5.2 involution).
  - Exact; no history.
- **(b) View Co, and the update is a library bijection** in the old value: the materialised IR
  is `x = load X+o; y = op(x, k…); store y, X+o` with no intervening store to X, where op is one
  of: add or sub of k (wrapping at the access width), xor with k, rotate by a constant, negate,
  `bswap`, add of k modulo a constant m (with x < m), multiply by a constant k modulo m with
  gcd(k, m) = 1 (with x < m); or a declared `inplace` pair (§8.7). k may be Cl or Co (an
  `IN` binding of a slice output); k MUST NOT depend on X's written bytes. The event is the
  `bennett-arith` permutation action for op on the arena cells X+o with k as `in` or `args`
  (ISA §4.7), preceded by the slice invocation that computes a Co k and followed by its
  uncomputation. Exact.
- **(c) View Co, inside the `f` part of `compute(f, use, budget, env)`**: history. A slice
  invocation computes the new bytes into a fresh register t; the event `xchg coh a t` exchanges t
  with the cells (`qexchm`); t now holds the displaced bytes and is kept until adjoint(E_f)
  replays the events in reverse (`xchg` again, then the slice invocation again), which cleans it
  (NS §3.1 compute-with-uncompute; Bennett). `use` MUST NOT write bytes that f wrote by case (c)
  (`BD-E-COHERENT-OVERWRITE` otherwise: the replay would not restore them).
- **(d) Otherwise**: `BD-E-COHERENT-OVERWRITE`, decided statically: a store to an outliving
  object that MC says may be Co at the store, and that is neither (b) nor (c). NS §4.2: "writing
  a register not known to be clean is a compile-time error … an in-place update x ← g(x) requires
  a total bijection with a bounded inverse … else it fails loud". The diagnostic names the store
  and the object.

Stores to objects that do not outlive the invocation are workspace: G runs them on the
generation's view; slices run them in their private memory (§8.5); at exit the objects are
released. Allocation in a generation is unconditional, like every allocation in the ISA (ISA
§3.5); the release of an object that outlives the invocation is TDL-12.

**TDL-6 Control and adjoint.** `ctrl(q, qi, …)` adds wire q.qi to every event's control set
(ISA §4.7 `ctl w`). `oracle_call`, `qexch`, `qexchm`, `qstore`, X and `xmask` are self-adjoint
(ISA §5.3 adjoint table); `adj(f)` generates f from the current classical state and applies the
adjoint of the event list; `compute` reuses the recording E_f for its uncompute, so masks and
history match exactly.

**TDL-7 History.** The registers an invocation keeps beyond its own events (displaced bytes of
case (c), the condition flags of a Co loop (TDL-10), Co values whose computing slice cannot be
replayed before the invocation ends because an intervening event wrote something it read, and
the per-slice fault registers of TDL-8) are **declared mutable outputs** of the invocation (NS
§4.2: an action with coherent internal control is its padded unitary on its declared wires).
Inside `compute`'s f they are released by adjoint(E_f). Otherwise the plugin allocates them,
reports them in the certificate's frame descriptor (ISA §9.4 "retained history") and with the
warning `BD-W-COHERENT-HISTORY`, and releases them by `measure` in the CC epilogue of the run.
Every other Co value register is cleaned right after its last use by replaying its computing
slice invocation.

**TDL-8 Faults.** NS §4.2: "a quantum action has no fault outcome of its own: any fallible
computation it needs is a lifted oracle it calls, whose fault register it declares among its
outputs". Every slice invocation k gets a fresh 4-wire fault register f_k; the uncomputing
invocation uses a second fresh register f′_k, which is then cleaned by `qxor f_k f′_k` (both hold
the same code) and freed, so f_k holds the slice's code and is retained (TDL-7). At the end of
the invocation a runtime combine oracle `@firstfault` (§16.5) XORs the first nonzero code of
f_1, …, f_K in invocation order into the action's **declared fault register** Φ: the budget
record's `fault` field (§9.1), or, when that is null, a register the plugin allocates and
retains (TDL-7); the CC epilogue's `measure` of a plugin-allocated Φ records the outcome in the
run's fault statistics, and the certificate reports the rate (`fault_rate`, ISA §12.3). On a
faulting basis input a slice's payload is the canonical 0 (ISA §5.2), so the events it feeds
leave the arena unchanged there. A nonzero rate is a reported quantity (NS §4.2), not an error.

**TDL-9 Budget.** Every slice invocation's token comes from the region-entry marker's budget
record, each field completed from the budget table (§9); each slice gets the full record
(outline E2). Exhaustion is that slice's `FAULT_BUDGET_*` and reaches TDL-8.

**TDL-10 Co control of quantum operations and stores.**

- A marker call or outliving store that is control-dependent on a Co branch, or a marker call
  with a Co index or op code: a slice invocation computes the condition (and the index or code)
  into fresh wires; the event is issued under `qpred` of the condition wire, once per member of
  the index or code dispatch domain under the predicate "value = member" (ISA §3.5, §4.6); then
  the wires are uncomputed.
- A Co rotation angle is predicated per value when its value set is finite. Otherwise it is
  `BD-E-COHERENT-ANGLE`: NS promises predication, not superposed parameters, and ISA §3.1 "angles
  are literals or classical arguments fixed at region entry".
- A loop whose trip count is Co is unrolled in the event list up to N = the `steps` field of the
  budget record: iteration i is predicated on the flag c_i (c_1 = the first continuation
  condition, c_{i+1} = c_i ∧ condition_i, computed by `ccx` into fresh wires); the flags are
  history (TDL-7); if c_{N+1} may be 1 the invocation records `FAULT_BUDGET_STEPS` under c_{N+1}
  into Φ. G-14 (§25.3) is the efficient form.
- A `qalloc`/`qborrow` whose n is Co allocates the maximum of n's value set, padded to its bound
  (NS §4.2: "an allocation whose size depends on a qubit is padded to its bound"); gates on wires
  at or beyond the run-time n are predicated off. An unbounded value set is BLK-1 (§25.1).

**TDL-11 After the region.**

- Code that reads an object whose state is Co, inside the closure of a later region entry, is
  part of that region's slices (TDL-3).
- Code outside every region that may read a may-Co object is compiled in two variants (Cl and
  Co signatures, §4.3), selected by the object's dynamic state. Its Co variant at host or CC
  level traps (`T-TAINT-HOST`, fault code 4), and statically the plugin warns
  (`BD-W-TAINT-HOST`, naming `__bennett_observe`): NS §4.2, classical outputs of coherent memory
  leave only through measurement.
- `__bennett_observe(p, len)` makes bytes Cl by measurement. On ISA 0.8 `measure` consumes a
  whole live non-view register (ISA §3.3), so it lowers to: an action that `qload`-copies the
  addressed cells into a fresh register r of 8·len wires; `measure r`, which collapses the arena
  cells identically (a computational-basis measurement of a CNOT copy equals one of the source);
  the outcome written to the shadow; an `xmask` of the outcome out of the arena cells, returning
  them to |0⟩; K := Cl for every object whose bytes are all observed. Bytes whose state is Cl or M
  are left as they are (an M object is dematerialised).

**TDL-12 Effects in action regions.** An action region is coherent (NS §4.2: "closed and
effect-free"). An effect marker, a host call (§11.4), or the release of an object that outlives
the invocation, reached in the generation of an action region (in G or in a slice), cannot be
recorded as a unitary event. On the executions that reach it the effect does not occur and the
event `fault 8` (`FAULT_EFFECT_UNMODELLED`) is recorded: at application it XORs 8 into a fresh
retained fault register f_k under the event's control set, which TDL-8 combines into Φ like a
slice's (NS §4.2: "an effect the device cannot virtualise is a fault code on the executions
that reach it"). The coverage report has a
`trapped` line for it. Effects inside oracle regions are §11.3.

## 11. Effects and device models per tier (effects 0.2)

### 11.1 Tier table

NS §4.2's effects table, made concrete. The four device models are the ISA's (ISA §7.3):
`console`, `clock`, `entropy`, `block`.

| Tier | Realisation of an effect marker (§3.2) | Other effects |
|---|---|---|
| H | – (host code calls its own libc; markers are never called from H) | real |
| CC | `hostcall bennett.dev.<model>.<op>` (ISA §10): a genuine host effect, since ISA `effect` is R-only (ISA §4.1); the host's reply carries the bytes a read returns | host functions by `hostcall` (§11.4) |
| R | ISA `effect <model>.<op>` on the effect tape, reversed by whole-run reversal (ISA §7.3, §10) | – (R makes no host calls) |
| L | the lifted device model of §11.3 over state bound by the descriptor (§8.3) | – |
| action regions | `fault 8` into the action's fault register (TDL-12) | same |
| unmodelled | F(8) with a `trapped` coverage line (§4.5) | same |

### 11.2 Effect markers in the R tier

`__bennett_effect_<model>_<op>(…)` lowers to ISA `effect <model>.<op> …` with the operands in
ISA §7.3 order: `console.write(ptr, len)`, `clock.read(ptr)`, `entropy.read(ptr, len)`,
`block.read(sector, ptr)`, `block.write(sector, ptr)`. A failing ISA validation (operands out of
range, entropy tape exhausted) is the ISA's fault record (ISA §7.3, code 10 for entropy). The
driver declares the models in `devices.models` (ISA §9.1) and supplies `block_image` from
`--bennett-disk=<file>` (§19.2). `bennett-runtimes`' musl maps system calls onto the markers:

| musl | Effect |
|---|---|
| `write(1, …)`, `write(2, …)`, `writev` on fds 1 and 2 | `console.write` |
| `clock_gettime`, `gettimeofday`, `time` | `clock.read`: the 8-byte counter c; `CLOCK_REALTIME` and `CLOCK_MONOTONIC` both give tv_sec = c / 10^9, tv_nsec = c mod 10^9 |
| `getrandom`, reads of `/dev/urandom` and `/dev/random` | `entropy.read` |
| block-device reads and writes (the platform's virtio-blk, §20.3) | `block.read`, `block.write` |
| files | a runtimes VFS over the block device, or over a data-image file system linked as a global |

Device models beyond the four arrive with an ISA version (ISA §17 item 3, a mechanics
deferral, §24): until then an effect on another device is `FAULT_EFFECT_UNMODELLED`.

### 11.3 Coherent tier: lifted device models

In an L variant, an effect marker call becomes a call of the runtimes function
`__bennett_dev_<model>_<op>` with the same operands. These are ordinary C functions of
`bennett-runtimes`, lifted like any code, over the **device state**: runtimes globals
`__bennett_dev_<model>_*` that the oracle wrapper's prologue (§16.2) initialises from the
descriptor's device bindings (§8.3) before the region function runs. Their contract:

| Model | State set by the prologue | Operation |
|---|---|---|
| `entropy` | base = `lift.addr @e0`, size = 2^A bytes, pos = 0 | `read(p, len)`: if len > size − pos, `__bennett_nz_fault(10)` (`FAULT_ENTROPY_EXHAUSTED`); else copy [base + pos, base + pos + len) to p and pos += len |
| `block` | base = `lift.addr @k0`, nsect = 2^A′; an empty overlay | `read(s, p)`: the overlay's 512 bytes for sector s if present, else sector s of the region if s < nsect, else 512 zero bytes (ISA §7.3: absent sectors read as zero); `write(s, p)`: copy 512 bytes into the overlay entry for s (a heap allocation by `malloc`, lifted to `lift.alloc`) |
| `clock` | c = `value` | `read(p)`: store c (8 bytes, little-endian) at p, then c += 1 |
| `console` | L = n(q)/8 (0 for a null q), a buffer of L bytes in the oracle's heap, n = 0 | `write(p, len)`: copy the first min(len, L − n) bytes to buffer[n…], n += that count; further bytes are discarded with the oracle's other writes |

A model without a binding is unbound: every operation on it is `__bennett_nz_fault(8)` on the
executions that reach it (NS §4.2). The `entropy` fault code 10 in an oracle: ISA §4.2 admits
`fault C` for every C < 2^F; ISA §5.4 labels code 10 "(R only)", which §25.2 records as a wording
item. The bound console buffer's bytes are output slices (§8.6).

### 11.4 Host calls from CC

A CC variant's call of an H function (§4.5 item 3) becomes `hostcall bennett.call/<h>` where
`<h>` is the hex SHA-256 of the callee's symbol name: the argument block holds the scalar
arguments (little-endian, in order) and, for each pointer argument whose pointee the analysis
proves pointer-free (no slot holds a pointer atom, §5), the pointee's byte range as an
(offset, length) pair and the bytes themselves. The host-side stub calls the function on a copy,
writes back the bytes of pointer arguments, and replies with the result and the written bytes.
A pointer argument whose pointee may contain pointers read by device code does not become a host
call: the callee is **promoted** to a CC variant (§19.4; ISA-11 would let it stay native, an
efficiency item). Every service is declared in `devices.services` (ISA §9.1, §10).

### 11.5 Fault codes reported from CC

ISA 0.8 does not say which code a CC trap reports (ISA-7, §25.2). `__bennett_nz_fault(C)` in CC
therefore lowers to `hostcall bennett.fault` with the 8-byte payload C, then `trap`: the driver's
host stub records C as the run's fault code. In R it lowers to `trap`; the R fault record's code
is the ISA's until ISA-7 is settled (§25.2).

### 11.6 Examples

The R-tier console: a whole program in the reversible tier writes three bytes and returns 0;
the tape holds one `console.write`; whole-run reversal restores the entry state:

```llvm example=effect-console-r verdict=accept
@msg = private unnamed_addr constant [3 x i8] c"hi\0A"

define i32 @main() {
  call void @__bennett_effect_console_write(ptr @msg, i64 3)
  ret i32 0
}
```

```text cc-run=effect-console-r
driver: --bennett-tier=reversible --bennett-entry=main
run: status=COMPLETED results=[INT(32):0] faults=[]
tape: console write args=[A(@msg), 3] bytes=68690a
reverse: status=REVERSED console=empty memory=entry
```

The same marker in a CC device function is a host effect:

```llvm example=effect-console-cc verdict=accept
@msg = private unnamed_addr constant [3 x i8] c"ok\0A"

define void @report() {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  call void @__bennett_qfree(ptr %h)
  call void @__bennett_effect_console_write(ptr @msg, i64 3)
  ret void
}
```

```text cc-run=effect-console-cc
run: status=COMPLETED results=[] faults=[]
hostcall: service=bennett.dev.console.write payload=6f6b0a reply=empty
```

The ENTROPY-bound oracle of rung 8 is §16.8.

## 12. Materialised normalisation (norm 0.2)

### 12.1 Scope, order and naming

The normaliser rewrites every device variant (§4.3) and the initialisers of every global a
device variant references; H variants are untouched. It applies the rules of §12.2 in table
order, each to the whole module before the next. The result is the **materialised module**: the
reference semantics (§18), the lifting map (§16) and the native comparison build (§17.7) are all
defined on it (NS §3.2: "the native comparison binary is built from that materialised bitcode").

**Naming.** A rule that introduces a value names it `%nz.<tag>.<r>`, where `<r>` is the name of
the instruction being rewritten without its `%` (a number for an unnamed value). For a rewritten
instruction without a result (a `void` call, a `store`, an `invoke` of a `void` function), `<r>`
is `<f>.<k>`: f the enclosing function's name and k the 0-based count, in instruction order, of
the result-less instructions of f that the same rule rewrites. A value introduced once per
function is `%nz.<tag>.<f>`. A constant global a rule needs is `@nz.<tag>.<f>.<r>`. A
declaration a rule needs is appended at the end of the module, and a global after the module's
globals, in order of first use. Each rule
states its tags.

### 12.2 The rules

**Fault replacement F(C)** (§12.3) and the 35 rules. N13, N17, N18 and N20 are 0.1 ids whose
rules are replaced (outline §12.2); they are kept as anchors.

| Id | Source | Replacement |
|---|---|---|
| N0 | the intrinsic families that LLVM defines by its own lowering passes: `llvm.coro.*`; `llvm.matrix.*`; `llvm.type.test`, `llvm.public.type.test`, `llvm.type.checked.load`, `llvm.type.checked.load.relative`, `llvm.icall.branch.funnel`; `llvm.instrprof.*`; `llvm.alloc.token.id`; `llvm.experimental.guard`, `llvm.experimental.widenable.condition` | the normaliser runs, only when the module contains one of them, the passes of the major in use, in this order: `coro-early`, `cgscc(coro-split)`, `coro-cleanup`; `lower-matrix-intrinsics`; `lowertypetests`; `instrprof`; `alloc-token`; `lower-guard-intrinsic`; `lower-widenable-condition` (which gives `true`). Their output is then normalised by N1–N35 |
| N1 | instruction flags `nsw`, `nuw`, `exact`, `inbounds`, `nusw`, `nneg`, `disjoint`, `samesign`, `inrange` (and `inrange(...)`) | removed: wrapping, inexact, out-of-bounds address arithmetic and the unflagged operation are defined |
| N2 | fast-math flags `nnan`, `ninf`, `nsz`, `arcp`, `contract`, `afn`, `reassoc`, `fast` | removed |
| N3 | instruction metadata other than `!dbg` (`!range`, `!nonnull`, `!noundef`, `!align`, `!dereferenceable`, `!dereferenceable_or_null`, `!tbaa`, `!tbaa.struct`, `!alias.scope`, `!noalias`, `!invariant.load`, `!invariant.group`, `!llvm.loop`, `!nontemporal`, `!prof`, `!alloc_token`, …) | removed (after §5 has read `!range`, PT5) |
| N4 | attributes on device function definitions, their parameters and returns, and on every call site in a device function: `noundef`, `nonnull`, `range(...)`, `align` (except together with `byval`, `byref`, `sret`, `inalloca`, `preallocated`), `dereferenceable(...)`, `dereferenceable_or_null(...)`, `nofpclass(...)`, `noalias`, `nocapture`, `captures(...)`, parameter `readnone`/`readonly`/`writeonly`, `returned`, `writable`, `dead_on_unwind`, `initializes(...)`, `allocalign`, `allocptr`; function attributes `memory(...)`, `readnone`, `readonly`, `writeonly`, `argmemonly`, `inaccessiblememonly`, `inaccessiblemem_or_argmemonly`, `willreturn`, `mustprogress`, `nosync`, `nofree`, `norecurse`, `speculatable`, `personality` (after N28) | removed (attribute groups are rewritten; a group shared with an H function is first duplicated) |
| N5 | calls with no semantic effect: `llvm.assume`, `llvm.sideeffect`, `llvm.donothing`, `llvm.pseudoprobe`, `llvm.fake.use`, `llvm.dbg.*`, `llvm.experimental.noalias.scope.decl`, `llvm.codeview.annotation`, `llvm.var.annotation`, `llvm.reloc.none`, `llvm.prefetch`, `llvm.pcmarker`, `llvm.clear_cache`, `llvm.experimental.convergence.*`, `llvm.seh.*`, `llvm.xray.*`, `llvm.experimental.stackmap`, `llvm.eh.unwind.init`, `llvm.asan.check.memaccess`, `llvm.hwasan.check.memaccess*` | deleted (a token result is never used after deletion of its users) |
| N5 | calls that return an operand: `llvm.expect`, `llvm.expect.with.probability`, `llvm.annotation`, `llvm.ptr.annotation`, `llvm.launder.invariant.group`, `llvm.strip.invariant.group`, `llvm.ssa.copy`, `llvm.arithmetic.fence`, `llvm.threadlocal.address`, `llvm.protected.field.ptr`, `llvm.ptrauth.sign`, `llvm.ptrauth.auth`, `llvm.ptrauth.resign`, `llvm.ptrauth.auth.with.pc.and.resign`, `llvm.ptrauth.strip` | every use replaced by operand 0; deleted. *(non-normative)* Pointer authentication is a target feature with no device counterpart; the identity is one deterministic choice, made identically in both builds |
| N6 | `llvm.lifetime.start`, `llvm.lifetime.end`, `llvm.invariant.start`, `llvm.invariant.end` | deleted (a frame is live for its whole activation, §17.3) |
| N7 | `undef` and `poison` constants: whole operands, vector lanes, aggregate elements, `shufflevector` mask elements, global initialisers | the zero of the type: `0`, `+0.0`, `null`, `zeroinitializer` for a wholly undefined vector or aggregate; mask element `0` |
| N8 | `%x = freeze T v` | deleted; every use of `%x` replaced by v |
| N9 | `atomic` and `volatile` on loads and stores; `fence`; `atomicrmw`; `cmpxchg` | plain load/store; fence deleted; `atomicrmw op ptr p, T v` → `%nz.l.r = load T, ptr p`, `%nz.v.r = <op> T %nz.l.r, v` (for `xchg`: v; `min`/`max`/`umin`/`umax`: `icmp` + `select` named `%nz.k.r`, `%nz.v.r`; FP ops: their N32 form), `store T %nz.v.r, ptr p`, uses of `%r` → `%nz.l.r`; `cmpxchg ptr p, T c, T n` → `%nz.l.r = load`, `%nz.e.r = icmp eq T %nz.l.r, c`, `%nz.s.r = select i1 %nz.e.r, T n, T %nz.l.r`, `store T %nz.s.r, ptr p`, `%nz.a.r = insertvalue { T, i1 } zeroinitializer, T %nz.l.r, 0`, `%r = insertvalue { T, i1 } %nz.a.r, i1 %nz.e.r, 1` (single-thread assumption, recorded in the certificate, §24 D24). Volatile accesses in platform-profile code are first routed by N35 (§20.3) |
| N10 | `llvm.is.constant.*` | `false` |
| N10 | `llvm.objectsize.*(p, min, nullunknown, dynamic)` | `-1` (all ones) if `min` is `false`, else `0` |
| N10 | `llvm.allow.runtime.check`, `llvm.allow.ubsan.check` | `true` (checks stay; a failing check is a fault) |
| N10 | `llvm.allow.sanitize.address`, `.hwaddress`, `.memory`, `.thread` | `false` (no sanitizer runtime exists in either build) |
| N10 | `llvm.get.dynamic.area.offset` | `0` |
| N10 | `llvm.vscale` | the constant V of §12.5 |
| N11 | calls of `llvm.trap`, `llvm.debugtrap`, `llvm.ubsantrap`, `llvm.looptrap` | F(4) |
| N11 | `llvm.cond.loop(c)` | the block is split after the call; `br i1 c, label %nz.spin.<f>.<k>, label <rest>`; the new block `nz.spin.<f>.<k>` is `br label %nz.spin.<f>.<k>` (the infinite loop LangRef defines; budgets bound it, §9) |
| N12 | `llvm.abs.*(x, i1 true)`, `llvm.ctlz.*(x, i1 true)`, `llvm.cttz.*(x, i1 true)` | the flag becomes `i1 false` |
| N13 | (0.1: `memcpy` → `memmove`) | replaced by N26 |
| N14 | `%r = shl/lshr/ashr iW a, b` with b not a constant | `%nz.c.r = icmp uge iW b, W`; `%nz.s.r = <op> iW a, b`; `%r = select i1 %nz.c.r, iW 0, iW %nz.s.r` (every shift by ≥ W gives 0, as the ISA's shifts do, ISA §4.1) |
| N14 | the same with b a constant ≥ W | every use of `%r` replaced by `0`; deleted |
| N15 | `extractelement`/`insertelement` with a non-constant index i on L lanes | `%nz.c.r = icmp uge iK i, L`; `%nz.e.r = <the original instruction>`; `%r = select i1 %nz.c.r, T Z, T %nz.e.r` with Z = the zero element (extract) or the unchanged vector operand (insert) |
| N16 | `%r = call T @llvm.fmuladd.*(a, b, c)` | `%nz.m.r = fmul T a, b`; `%r = fadd T %nz.m.r, c` (no fusion; explicit `llvm.fma` keeps fusion through §13) |
| N17 | (0.1: FP formats and transcendentals → F(8)) | replaced by §13 (N32, N33): no floating-point construct faults |
| N18 | (0.1: external calls in oracle and reversible closures → F(8)) | replaced by §4.5: shims first; trapped only without bitcode |
| N19 | floating-point arithmetic, comparison and conversion of `float` and `double` | the soft-float rewrite of §13.1 (applied by N32) |
| N20 | (0.1: alloca + memset) | replaced by N24 |
| N21 | **vector scalarisation**: every instruction of vector type, every vector intrinsic (`llvm.vector.*`, `llvm.experimental.vector.*`, `llvm.vp.*`, `llvm.experimental.vp.*`, `llvm.masked.*`, `llvm.stepvector`, `llvm.experimental.stepvector`, `llvm.get.active.lane.mask`, `llvm.experimental.get.vector.length`, `llvm.experimental.cttz.elts`, `llvm.vp.cttz.elts`, `llvm.loop.dependence.raw.mask`, `llvm.loop.dependence.war.mask`), vector parameters and results of internal device functions | per-lane scalar instructions in lane order, by the rules of §12.6 |
| N22 | **wide integers and non-byte memory**: an integer type iN with N > 128 in an instruction; a load or store of iN with N not a multiple of 8 or of an aggregate type | iN with N > 128 becomes L = ⌈N/64⌉ i64 limbs (limb 0 the least significant; the top limb is i(N − 64(L−1))) with the expansions of §12.7; a load or store of iN with N mod 8 ≠ 0 becomes a load or store of i(8⌈N/8⌉) with a `trunc` after the load and a `zext` before the store (fixing LangRef's unspecified extra bits as zero); a load or store of an aggregate becomes one access per element in element order at its offset (`%nz.e<k>.<r>`) |
| N23 | **varargs** | §14.3 |
| N24 | **allocas → shadow stack**: every `alloca`; `llvm.stacksave`, `llvm.stackrestore`; `llvm.frameaddress`, `llvm.sponentry`, `llvm.addressofreturnaddress`, `llvm.stackaddress`, `llvm.returnaddress`, `llvm.swift.async.context.addr`, `llvm.localescape`, `llvm.localrecover`, `llvm.localaddress`, `llvm.eh.recoverfp`, `llvm.eh.dwarf.cfa`; `llvm.structured.alloca` | §17.3 |
| N25 | `byval`, `inalloca` and `preallocated` arguments; `llvm.call.preallocated.*`; aggregate returns wider than 128 bits | an explicit caller copy into a shadow-stack slot of the caller's frame (`%nz.bv<j>.<r>` for argument j) passed as a plain `ptr`, and the attribute removed from the callee and the call; a return of a first-class aggregate wider than 128 bits is demoted to a hidden first parameter `ptr %nz.ret` in which the callee stores the value (`sret` semantics) |
| N26 | **memory intrinsics**: `llvm.memcpy.*`, `llvm.memcpy.inline.*`, `llvm.memmove.*`, `llvm.memset.*`, `llvm.memset.inline.*`, `llvm.memcpy/memmove/memset.element.unordered.atomic.*`, `llvm.experimental.memset.pattern.*` | `call void @__bennett_rt_memmove(ptr d, ptr s, i64 n)`, `call void @__bennett_rt_memset(ptr d, i8 v, i64 n)` (the `i1` volatile flag and element-size operand dropped; a constant length becomes an `i64` constant; a narrower non-constant length is first `%nz.n.<r> = zext … to i64`); `memset.pattern(d, v: T, count)` → a loop storing v at d + i·size(T) for i < count (blocks `nz.mp.<r>.*`) |
| N27 | **integer intrinsics** | the fixed expansions of §12.8 |
| N28 | **unwinding: explicit propagation** | §14.4 |
| N29 | **setjmp/longjmp** | §14.5 |
| N30 | **rewindable frames** (fibers) | §14.6, only in the functions §14.6 selects |
| N31 | **inline asm and target intrinsics** | the §15 tables |
| N32 | **floating point** | the soft-float rewrite of §13.1–§13.2 (after N21) |
| N33 | **extended FP formats and libm intrinsics** | §13.3–§13.5 |
| N34 | **R-tier budget instrumentation points** | a call of `__bennett_rt_rstep()` is *not* inserted; N34 marks the R variants' function entries and loop latches with the metadata `!bennett.rstep` (kept by N3) for the R lowering's counters (§17.6) |
| N35 | **platform hooks** | §20.3 (MMIO routing), §20.4 (interrupt poll points), only under a platform profile |

The other generic intrinsics are rows of §12.8 (integer), §13 (floating point), §14 (control
transfer) and §15 (target intrinsics). **Completeness obligation:** Appendix C lists every
generic (target-independent) intrinsic name of LLVM 18, 20 and 23 (546 names) with its rule. No
generic intrinsic is `trapped`.

*(non-normative)* Division by zero and `sdiv`/`srem` of INT_MIN by −1 are not rewritten: they are
faults of the reference semantics (§17.5), the ISA's `lift.div` and CC division fault on them
directly (ISA §4.1, §4.2), and the native comparison build traps (§17.7).

### 12.3 Fault replacement F(C)

F(C): the instruction is replaced by `call void @__bennett_nz_fault(i64 C)` followed by
`unreachable`; the instructions after it in its block are deleted, and the block is removed from
the incoming lists of the phi nodes of its former successors. `__bennett_nz_fault` is a primitive
(§3.1): `bennett-runtimes` defines it for the native comparison build (record C and end the
device entry with fault C); the map gives it the row `fault C` (§16.4); CC and R lower it by
§11.5.

### 12.4 The residual-poison validator

The validator inspects the materialised device variants and rejects (`BD-E-RESIDUAL`) any of:

| Id | Residue |
|---|---|
| V1 | a flag of N1 or N2 |
| V2 | instruction metadata other than `!dbg` and `!bennett.rstep` |
| V3 | an attribute N4 removes, on a device function, its parameters or return, or a call site in a device function |
| V4 | a call of an intrinsic that N0, N5, N6, N10, N11, N16, N21, N24, N26, N27, N32 or N33 removes, or of `llvm.abs`/`ctlz`/`cttz` with a `true` flag |
| V5 | an `undef` or `poison` constant in a device function or in the initialiser of a global a device function references |
| V6 | `freeze`, `fence`, `atomicrmw`, `cmpxchg`, an atomic or volatile load or store |
| V7 | a shift whose amount is not a constant < W, unless the shift's only use is as the false operand of a `select` whose true operand is 0 and whose condition is `icmp uge` of the same amount and the constant W |
| V8 | `extractelement`/`insertelement` with a non-constant index outside the N15 pattern (only before N21; after N21 no vector remains, V13) |
| V9 | a floating-point instruction other than `fneg`, `bitcast`, `load`, `store`, `select` and `phi` of a floating-point value, or a call of a floating-point intrinsic other than `llvm.fabs` and `llvm.copysign` (after N32/N33; 0.1's V9 is inverted) |
| V10 | an operand or result of type `half`, `bfloat`, `x86_fp80`, `fp128` or `ppc_fp128` other than in `bitcast`, `load`, `store`, `select` and `phi` (after N33) |
| V11 | an `alloca` (after N24; replaces 0.1's V11) |
| V12 | in an L or R variant, a call of a function without a definition other than a primitive, a runtime entry point defined in the link, or a trapped call already replaced by F(8) |
| V13 | a value of vector type |
| V14 | a value of type iN with N > 128 |
| V15 | `va_start`, `va_end`, `va_copy`, `va_arg`, `invoke`, `landingpad`, `resume`, `cleanuppad`, `catchpad`, `catchswitch`, `cleanupret`, `catchret`, a call of `setjmp`, `_setjmp`, `sigsetjmp` or `__sigsetjmp` |
| V16 | inline `asm` or a call of a target intrinsic (`llvm.<target>.*`) |

The plugin's validator and `bennett-conformance`'s are implemented independently (NS §3.2); a
disagreement on any input is a conformance failure of one of them.

### 12.5 Scalable vectors

A scalable vector type `<vscale x L x T>` has L·V lanes, where V is the constant `vscale` of the
link: the function attribute `vscale_range(V, V)` when every device function that uses scalable
vectors carries it with equal bounds, else the driver option `--bennett-vscale=<V>` (default: the
minimum of the `vscale_range` bounds, §24). The native comparison build is compiled for the same
V (`-msve-vector-bits=128·V` or `-mrvv-vector-bits`). N10 replaces `llvm.vscale` by V and N21
scalarises the L·V lanes. *(non-normative)* x86-64 has no scalable vectors; the rule exists so
that AArch64 SVE and RISC-V V code is liftable.

### 12.6 Vector scalarisation (N21)

For a value `%v` of type `<L x T>`, lane k is the scalar `%nz.l<k>.v` (k = 0 … L − 1). Rules, in
lane order k = 0, 1, …:

- elementwise instructions (binary, bitwise, `icmp`, `fcmp`, casts, `select` with a vector or
  scalar condition, unary `fneg`, `freeze`, calls of elementwise intrinsics): one scalar
  instruction per lane, `%nz.l<k>.r = <op> T %nz.l<k>.a, %nz.l<k>.b`;
- `load <L x T>, ptr p` → `%nz.p<k>.r = getelementptr T, ptr p, i64 k` and `%nz.l<k>.r = load T,
  ptr %nz.p<k>.r` with alignment min(original, abi-align(T)); `store` likewise in lane order;
- `insertelement`, `extractelement`, `shufflevector` with constant indices: lane renaming; with a
  non-constant index (after N15): a `select` chain over the L lanes in lane order;
- `llvm.vector.reduce.<op>(v)` with op ∈ {add, mul, and, or, xor, smax, smin, umax, umin, fadd,
  fmul, fmax, fmin, fmaximum, fminimum}: a **left fold** in lane order: `%nz.f1.r = <op> lane0,
  lane1`, `%nz.f<k>.r = <op> %nz.f<k−1>.r, lane k`, the last named `%r`; the ordered `fadd`/`fmul`
  forms take the start value as the first operand. Exact for floating point once N2 has removed
  `reassoc`;
- `llvm.vp.*` (vector-predicated) and `llvm.masked.*`: lane k is active iff k < evl and mask[k];
  an active lane executes the scalar operation, an inactive lane yields the passthrough operand
  (masked loads) or 0 (N7: LangRef's poison), and a masked or predicated store, scatter or
  compress-store writes only active lanes, each under a conditional branch (blocks
  `nz.ml<k>.<r>`); gathers and scatters use the lane's pointer;
- `llvm.stepvector` lane k is k; `llvm.get.active.lane.mask(base, n)` lane k is base + k < n
  (unsigned); `llvm.experimental.get.vector.length(cnt, vf, scalable)` is umin(cnt, vf·(V if
  scalable else 1)); `cttz.elts` is the index of the first nonzero lane (L if none, or the
  poison-free 0 of N7 when the flag says zero is poison); `loop.dependence.raw/war.mask(a, b,
  size)` lane k follows LangRef's definition;
- `vector.extract`, `vector.insert`, `vector.reverse`, `vector.splice*`, `vector.interleave<n>`,
  `vector.deinterleave<n>`, `experimental.vector.compress`, `experimental.vector.histogram.*`,
  `experimental.vector.match`, `experimental.vector.extract.last.active`,
  `vector.partial.reduce.*`: lane permutations and folds by their LangRef definitions;
- a vector parameter or result of an internal device function becomes L scalar parameters or an
  aggregate of L scalars in lane order; a vector that crosses an external boundary (a device
  entry's signature, a call of a function without a definition) is rebuilt with `insertelement`
  at that boundary, which only H code and the native build see.

### 12.7 Wide integers (N22)

With limbs a_k, b_k (k = 0 … L − 1, i64, the top limb of width N − 64(L − 1)):

- `add`: `%nz.m0.r = add a_0, b_0`, `%nz.c0.r = icmp ult %nz.m0.r, a_0`; for k ≥ 1:
  `%nz.t<k>.r = add a_k, b_k`, `%nz.z<k>.r = zext i1 %nz.c<k−1>.r to i64`, `%nz.m<k>.r = add
  %nz.t<k>.r, %nz.z<k>.r` and, for k < L − 1, `%nz.u<k>.r = icmp ult %nz.t<k>.r, a_k`,
  `%nz.v<k>.r = icmp ult %nz.m<k>.r, %nz.t<k>.r`, `%nz.c<k>.r = or i1 %nz.u<k>.r, %nz.v<k>.r`;
- `sub`: the same with `sub` and borrows `icmp ult a_k, b_k`;
- `and`, `or`, `xor`: per limb; `icmp`: lexicographic from the top limb (signed on the top
  limb only for signed predicates); `select`, `phi`: per limb; `zext`, `sext`, `trunc`: limb
  copies with the sign limb `ashr a_top, 63` for `sext`;
- `mul`, `udiv`, `sdiv`, `urem`, `srem`, `shl`, `lshr`, `ashr`: calls of the runtimes entry points
  `__bennett_rt_i<N>_<op>(ptr r, ptr a, ptr b)` on shadow-stack slots holding the limbs (division
  by zero calls `__bennett_nz_fault(5)`, signed MIN / −1 `__bennett_nz_fault(6)`, shifts by ≥ N
  give 0 as N14);
- loads and stores: per limb at offsets 8k, little-endian targets (`%nz.p<k>.r` / `%nz.q<k>.r`
  for the addresses);
- a wide parameter or result of an internal device function becomes L limb parameters or an
  aggregate of limbs.

### 12.8 Integer intrinsics (N27)

| Intrinsic | Expansion |
|---|---|
| `smax`, `smin`, `umax`, `umin` (a, b) | `%nz.c.r = icmp sgt/slt/ugt/ult a, b`; `%r = select i1 %nz.c.r, a, b` |
| `abs(a, false)` | `%nz.c.r = icmp slt a, 0`; `%nz.n.r = sub 0, a`; `%r = select i1 %nz.c.r, %nz.n.r, a` |
| `scmp`, `ucmp` (a, b) → iM | `%nz.g.r = icmp sgt/ugt a, b`; `%nz.l.r = icmp slt/ult a, b`; `%nz.z.r = zext i1 %nz.g.r to iM`; `%nz.s.r = sext i1 %nz.l.r to iM`; `%r = or iM %nz.z.r, %nz.s.r` |
| `uadd/usub.with.overflow` (a, b) | `%nz.s.r = add/sub a, b`; `%nz.c.r = icmp ult %nz.s.r, a` (add) or `icmp ult a, b` (sub); `%nz.a.r = insertvalue { T, i1 } zeroinitializer, T %nz.s.r, 0`; `%r = insertvalue { T, i1 } %nz.a.r, i1 %nz.c.r, 1` |
| `sadd/ssub.with.overflow` | `%nz.s.r = add/sub a, b`; `%nz.x.r = xor a, %nz.s.r`; `%nz.y.r = xor b, %nz.s.r` (add) or `xor a, b` (sub); `%nz.w.r = and %nz.x.r, %nz.y.r`; `%nz.c.r = icmp slt %nz.w.r, 0` (overflow iff the result's sign differs from a's while the operands' signs agree (add) or differ (sub)); then the two `insertvalue`s |
| `umul/smul.with.overflow` on iW, W ≤ 64 | the product at width 2W (`zext`/`sext`, `mul`, `trunc`); overflow iff the high half differs from 0 (unsigned) or from the sign extension of the low half (signed); W > 64: `__bennett_rt_<name>_i<W>` |
| `uadd/usub/sadd/ssub.sat` | the `.with.overflow` expansion and a `select` of the saturated bound (unsigned: all ones / 0; signed: MAX if the operand a is non-negative, else MIN) |
| `ptrmask(p, m)` | `%nz.i.r = ptrtoint p to iW`; `%nz.a.r = and iW %nz.i.r, m`; `%r = inttoptr iW %nz.a.r to ptr` |
| `load.relative(p, off)` | `%nz.p.r = getelementptr i8, ptr p, off`; `%nz.o.r = load i32, ptr %nz.p.r`; `%nz.e.r = sext i32 %nz.o.r to i64`; `%r = getelementptr i8, ptr p, i64 %nz.e.r` |
| `bswap`, `bitreverse`, `ctpop`, `ctlz`, `cttz`, `fshl`, `fshr`, `sshl.sat`, `ushl.sat`, `smul.fix`, `umul.fix`, `smul.fix.sat`, `umul.fix.sat`, `sdiv.fix`, `udiv.fix`, `sdiv.fix.sat`, `udiv.fix.sat`, `pdep`, `pext`, `clmul` | `%r = call iW @__bennett_rt_<name>_i<W>(…)` with the same operands (`<name>` with `.` replaced by `_`), defined by `bennett-runtimes` with the LangRef semantics (division by zero in the `.fix` forms: `__bennett_nz_fault(5)`) |
| `read_register`, `read_volatile_register`, `write_register`, `write_volatile_register` (named register) | a load or store of the runtimes global `__bennett_rt_reg_<name>` (the platform register file, §20.1); the name `sp` (and its target spellings) reads the shadow-stack pointer (§17.3) |
| `thread.pointer` | the address of the runtimes global `__bennett_rt_tls` (one thread) |
| `ptrauth.blend(a, d)` | `(a & 0xFFFFFFFFFFFF) | (d << 48)` in i64 |
| `ptrauth.sign.generic(v, d)` | `0` |
| `objc.*` | `llvm.objc.<name>` becomes a call of the Objective-C runtime function `objc_<name>` with the same operands (resolved by §4.5); `objc.clang.arc.use`, `objc.clang.arc.noop.use` and `objc.arc.annotation.*` are deleted |
| `experimental.gc.statepoint(id, n, f, args…)` | a plain call `f(args…)`; `gc.result` → its result; `gc.relocate(token, base, derived)` → the derived pointer of the statepoint's argument list (a non-moving collector); `gc.get.pointer.base(p)` → p; `gc.get.pointer.offset(p)` → 0; `gcroot` deleted; `gcread(o, p)` → `load ptr, ptr p`; `gcwrite(v, o, p)` → `store ptr v, ptr p` |
| `experimental.patchpoint*(id, n, target, nargs, args…)` | an indirect call of target with the first nargs arguments (§14.2); a null target: nothing |
| `experimental.deoptimize(args…)` | a call of the runtimes function `__llvm_deoptimize` with the arguments (resolved by §4.5) and `ret` of its result |
| `init.trampoline`, `adjust.trampoline` | §14.2 (trampolines) |
| `eh.typeid.for`, `eh.exceptionpointer`, `eh.exceptioncode`, `eh.return.*`, `eh.sjlj.*` | §14.4, §14.5 |
| `callbr.landingpad` | §15.2 |

### 12.9 Examples

```llvm normalise-in=n-flags
define internal i32 @f(i32 noundef %a, ptr nonnull align 4 %p) #0 {
  %s = add nsw i32 %a, 1
  %q = getelementptr inbounds i32, ptr %p, i64 1
  %v = load i32, ptr %q, align 4, !range !0, !noundef !1
  %c = icmp sgt i32 %v, 0
  call void @llvm.assume(i1 %c)
  %r = mul nuw nsw i32 %s, %v
  ret i32 %r
}

declare void @llvm.assume(i1 noundef)

attributes #0 = { mustprogress nounwind willreturn memory(argmem: read) }

!0 = !{i32 0, i32 100}
!1 = !{}
```

```llvm normalise-out=n-flags
define internal i32 @f(i32 %a, ptr %p) #0 {
  %s = add i32 %a, 1
  %q = getelementptr i32, ptr %p, i64 1
  %v = load i32, ptr %q, align 4
  %c = icmp sgt i32 %v, 0
  %r = mul i32 %s, %v
  ret i32 %r
}

declare void @llvm.assume(i1 noundef)

attributes #0 = { nounwind }

!0 = !{i32 0, i32 100}
!1 = !{}
```

```llvm normalise-in=n-shift
define internal i32 @sh(i32 %a, i32 %b) {
  %r = shl i32 %a, %b
  %k = lshr i32 %a, 3
  %z = ashr i32 %a, 40
  %t = add i32 %r, %z
  %u = add i32 %t, %k
  ret i32 %u
}
```

```llvm normalise-out=n-shift
define internal i32 @sh(i32 %a, i32 %b) {
  %nz.c.r = icmp uge i32 %b, 32
  %nz.s.r = shl i32 %a, %b
  %r = select i1 %nz.c.r, i32 0, i32 %nz.s.r
  %k = lshr i32 %a, 3
  %t = add i32 %r, 0
  %u = add i32 %t, %k
  ret i32 %u
}
```

```llvm normalise-in=n-undef
define internal i64 @u(i64 %a, i1 %c) {
  %f = freeze i64 undef
  %s = select i1 %c, i64 %a, i64 poison
  %v = insertelement <2 x i64> poison, i64 %a, i32 0
  %w = extractelement <2 x i64> %v, i32 1
  %r = add i64 %f, %s
  %t = add i64 %r, %w
  ret i64 %t
}
```

The vector in `n-undef` is then scalarised by N21: lane 0 is `%a`, lane 1 is the zero of N7, so
`%w` is `0`:

```llvm normalise-out=n-undef
define internal i64 @u(i64 %a, i1 %c) {
  %s = select i1 %c, i64 %a, i64 0
  %r = add i64 0, %s
  %t = add i64 %r, 0
  ret i64 %t
}
```

```llvm normalise-in=n-query
define internal i64 @q(ptr %p, i64 %x) {
  %s = call i64 @llvm.objectsize.i64.p0(ptr %p, i1 false, i1 true, i1 false)
  %k = call i1 @llvm.is.constant.i64(i64 %x)
  %z = zext i1 %k to i64
  %r = add i64 %s, %z
  ret i64 %r
}

declare i64 @llvm.objectsize.i64.p0(ptr, i1 immarg, i1 immarg, i1 immarg)
declare i1 @llvm.is.constant.i64(i64)
```

```llvm normalise-out=n-query
define internal i64 @q(ptr %p, i64 %x) {
  %z = zext i1 false to i64
  %r = add i64 -1, %z
  ret i64 %r
}

declare i64 @llvm.objectsize.i64.p0(ptr, i1 immarg, i1 immarg, i1 immarg)
declare i1 @llvm.is.constant.i64(i64)
```

```llvm normalise-in=n-trap
define internal i32 @t(i32 %a) {
  %c = icmp eq i32 %a, 0
  call void @llvm.trap()
  %r = add i32 %a, 1
  ret i32 %r
}

declare void @llvm.trap()
```

```llvm normalise-out=n-trap
define internal i32 @t(i32 %a) {
  %c = icmp eq i32 %a, 0
  call void @__bennett_nz_fault(i64 4)
  unreachable
}

declare void @llvm.trap()

declare void @__bennett_nz_fault(i64)
```

Vector scalarisation and an ordered reduction (N21):

```llvm normalise-in=n-vector
define internal i32 @v(ptr %pa, ptr %pb) {
  %a = load <4 x i32>, ptr %pa, align 4
  %b = load <4 x i32>, ptr %pb, align 4
  %s = add <4 x i32> %a, %b
  %r = call i32 @llvm.vector.reduce.add.v4i32(<4 x i32> %s)
  ret i32 %r
}

declare i32 @llvm.vector.reduce.add.v4i32(<4 x i32>)
```

```llvm normalise-out=n-vector
define internal i32 @v(ptr %pa, ptr %pb) {
  %nz.p0.a = getelementptr i32, ptr %pa, i64 0
  %nz.l0.a = load i32, ptr %nz.p0.a, align 4
  %nz.p1.a = getelementptr i32, ptr %pa, i64 1
  %nz.l1.a = load i32, ptr %nz.p1.a, align 4
  %nz.p2.a = getelementptr i32, ptr %pa, i64 2
  %nz.l2.a = load i32, ptr %nz.p2.a, align 4
  %nz.p3.a = getelementptr i32, ptr %pa, i64 3
  %nz.l3.a = load i32, ptr %nz.p3.a, align 4
  %nz.p0.b = getelementptr i32, ptr %pb, i64 0
  %nz.l0.b = load i32, ptr %nz.p0.b, align 4
  %nz.p1.b = getelementptr i32, ptr %pb, i64 1
  %nz.l1.b = load i32, ptr %nz.p1.b, align 4
  %nz.p2.b = getelementptr i32, ptr %pb, i64 2
  %nz.l2.b = load i32, ptr %nz.p2.b, align 4
  %nz.p3.b = getelementptr i32, ptr %pb, i64 3
  %nz.l3.b = load i32, ptr %nz.p3.b, align 4
  %nz.l0.s = add i32 %nz.l0.a, %nz.l0.b
  %nz.l1.s = add i32 %nz.l1.a, %nz.l1.b
  %nz.l2.s = add i32 %nz.l2.a, %nz.l2.b
  %nz.l3.s = add i32 %nz.l3.a, %nz.l3.b
  %nz.f1.r = add i32 %nz.l0.s, %nz.l1.s
  %nz.f2.r = add i32 %nz.f1.r, %nz.l2.s
  %r = add i32 %nz.f2.r, %nz.l3.s
  ret i32 %r
}

declare i32 @llvm.vector.reduce.add.v4i32(<4 x i32>)
```

```text native=n-vector
v([1, 2, 3, 2147483647], [10, 20, 30, 1]) = -2147483582
v([-5, 7, 0, 100], [5, -7, 9, 1]) = 110
```

*(non-normative)* 11 + 22 + 33 + (2147483647 + 1 mod 2^32 = −2^31) = 66 − 2147483648 =
−2147483582; 0 + 0 + 9 + 101 = 110.

A 256-bit addition in four limbs (N22):

```llvm normalise-in=n-wideint
define internal void @w(ptr %pa, ptr %pb, ptr %pr) {
  %a = load i256, ptr %pa, align 8
  %b = load i256, ptr %pb, align 8
  %s = add i256 %a, %b
  store i256 %s, ptr %pr, align 8
  ret void
}
```

```llvm normalise-out=n-wideint
define internal void @w(ptr %pa, ptr %pb, ptr %pr) {
  %nz.p0.a = getelementptr i64, ptr %pa, i64 0
  %nz.m0.a = load i64, ptr %nz.p0.a, align 8
  %nz.p1.a = getelementptr i64, ptr %pa, i64 1
  %nz.m1.a = load i64, ptr %nz.p1.a, align 8
  %nz.p2.a = getelementptr i64, ptr %pa, i64 2
  %nz.m2.a = load i64, ptr %nz.p2.a, align 8
  %nz.p3.a = getelementptr i64, ptr %pa, i64 3
  %nz.m3.a = load i64, ptr %nz.p3.a, align 8
  %nz.p0.b = getelementptr i64, ptr %pb, i64 0
  %nz.m0.b = load i64, ptr %nz.p0.b, align 8
  %nz.p1.b = getelementptr i64, ptr %pb, i64 1
  %nz.m1.b = load i64, ptr %nz.p1.b, align 8
  %nz.p2.b = getelementptr i64, ptr %pb, i64 2
  %nz.m2.b = load i64, ptr %nz.p2.b, align 8
  %nz.p3.b = getelementptr i64, ptr %pb, i64 3
  %nz.m3.b = load i64, ptr %nz.p3.b, align 8
  %nz.m0.s = add i64 %nz.m0.a, %nz.m0.b
  %nz.c0.s = icmp ult i64 %nz.m0.s, %nz.m0.a
  %nz.t1.s = add i64 %nz.m1.a, %nz.m1.b
  %nz.z1.s = zext i1 %nz.c0.s to i64
  %nz.m1.s = add i64 %nz.t1.s, %nz.z1.s
  %nz.u1.s = icmp ult i64 %nz.t1.s, %nz.m1.a
  %nz.v1.s = icmp ult i64 %nz.m1.s, %nz.t1.s
  %nz.c1.s = or i1 %nz.u1.s, %nz.v1.s
  %nz.t2.s = add i64 %nz.m2.a, %nz.m2.b
  %nz.z2.s = zext i1 %nz.c1.s to i64
  %nz.m2.s = add i64 %nz.t2.s, %nz.z2.s
  %nz.u2.s = icmp ult i64 %nz.t2.s, %nz.m2.a
  %nz.v2.s = icmp ult i64 %nz.m2.s, %nz.t2.s
  %nz.c2.s = or i1 %nz.u2.s, %nz.v2.s
  %nz.t3.s = add i64 %nz.m3.a, %nz.m3.b
  %nz.z3.s = zext i1 %nz.c2.s to i64
  %nz.m3.s = add i64 %nz.t3.s, %nz.z3.s
  %nz.q0.w.0 = getelementptr i64, ptr %pr, i64 0
  store i64 %nz.m0.s, ptr %nz.q0.w.0, align 8
  %nz.q1.w.0 = getelementptr i64, ptr %pr, i64 1
  store i64 %nz.m1.s, ptr %nz.q1.w.0, align 8
  %nz.q2.w.0 = getelementptr i64, ptr %pr, i64 2
  store i64 %nz.m2.s, ptr %nz.q2.w.0, align 8
  %nz.q3.w.0 = getelementptr i64, ptr %pr, i64 3
  store i64 %nz.m3.s, ptr %nz.q3.w.0, align 8
  ret void
}
```

```text native=n-wideint
w(limbs a = [0xffffffffffffffff, 0xffffffffffffffff, 5, 1], b = [1, 0, 0xffffffffffffffff, 2]) -> r = [0, 0, 5, 4]
w(limbs a = [all ones x 4], b = [1, 0, 0, 0]) -> r = [0, 0, 0, 0]
```

*(non-normative)* Limbs are least significant first. Limb 0: 2^64 − 1 + 1 = 0, carry 1; limb 1:
2^64 − 1 + 0 + 1 = 0, carry 1; limb 2: 5 + 2^64 − 1 + 1 = 5, carry 1; limb 3: 1 + 2 + 1 = 4.

Allocas move to the shadow stack (N24, §17.3); the frame is zero-filled, so the read of
`b[2]`, undefined in the input, is 0:

```llvm normalise-in=n-shadow-stack
define internal i64 @a(i64 %x) {
  %b = alloca [3 x i64], align 8
  %p = getelementptr [3 x i64], ptr %b, i64 0, i64 1
  store i64 %x, ptr %p, align 8
  %q = getelementptr [3 x i64], ptr %b, i64 0, i64 2
  %v = load i64, ptr %q, align 8
  %w = load i64, ptr %p, align 8
  %r = add i64 %v, %w
  ret i64 %r
}
```

```llvm normalise-out=n-shadow-stack
define internal i64 @a(i64 %x) {
  %nz.fp.a = call ptr @__bennett_rt_ss_push(i64 24, i64 8)
  %b = getelementptr i8, ptr %nz.fp.a, i64 0
  %p = getelementptr [3 x i64], ptr %b, i64 0, i64 1
  store i64 %x, ptr %p, align 8
  %q = getelementptr [3 x i64], ptr %b, i64 0, i64 2
  %v = load i64, ptr %q, align 8
  %w = load i64, ptr %p, align 8
  %r = add i64 %v, %w
  call void @__bennett_rt_ss_pop(ptr %nz.fp.a)
  ret i64 %r
}

declare ptr @__bennett_rt_ss_push(i64, i64)

declare void @__bennett_rt_ss_pop(ptr)
```

```text native=n-shadow-stack
a(5) = 5 (output module; the input module's read of b[2] is undefined: the documented choice of N24)
a(-9) = -9 (output module)
```

Memory intrinsics (N26) and integer intrinsics (N27):

```llvm normalise-in=n-memintrinsics
define internal void @cp(ptr %d, ptr %s, i32 %n) {
  call void @llvm.memcpy.p0.p0.i64(ptr %d, ptr %s, i64 16, i1 false)
  call void @llvm.memset.p0.i32(ptr %d, i8 7, i32 %n, i1 false)
  ret void
}

declare void @llvm.memcpy.p0.p0.i64(ptr, ptr, i64, i1 immarg)

declare void @llvm.memset.p0.i32(ptr, i8, i32, i1 immarg)
```

```llvm normalise-out=n-memintrinsics
define internal void @cp(ptr %d, ptr %s, i32 %n) {
  call void @__bennett_rt_memmove(ptr %d, ptr %s, i64 16)
  %nz.n.cp.1 = zext i32 %n to i64
  call void @__bennett_rt_memset(ptr %d, i8 7, i64 %nz.n.cp.1)
  ret void
}

declare void @llvm.memcpy.p0.p0.i64(ptr, ptr, i64, i1 immarg)

declare void @llvm.memset.p0.i32(ptr, i8, i32, i1 immarg)

declare void @__bennett_rt_memmove(ptr, ptr, i64)

declare void @__bennett_rt_memset(ptr, i8, i64)
```

```text native=n-memintrinsics
cp(d, s = [100, 101, …, 115], 3) -> d = [7, 7, 7, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115]
```

```llvm normalise-in=n-intrinsics
define internal i32 @k(i32 %a, i32 %b) {
  %m = call i32 @llvm.smax.i32(i32 %a, i32 %b)
  %o = call { i32, i1 } @llvm.uadd.with.overflow.i32(i32 %a, i32 %b)
  %ov = extractvalue { i32, i1 } %o, 1
  %p = call i32 @llvm.ctpop.i32(i32 %m)
  %z = zext i1 %ov to i32
  %r = add i32 %p, %z
  ret i32 %r
}

declare i32 @llvm.smax.i32(i32, i32)

declare { i32, i1 } @llvm.uadd.with.overflow.i32(i32, i32)

declare i32 @llvm.ctpop.i32(i32)
```

```llvm normalise-out=n-intrinsics
define internal i32 @k(i32 %a, i32 %b) {
  %nz.c.m = icmp sgt i32 %a, %b
  %m = select i1 %nz.c.m, i32 %a, i32 %b
  %nz.s.o = add i32 %a, %b
  %nz.c.o = icmp ult i32 %nz.s.o, %a
  %nz.a.o = insertvalue { i32, i1 } zeroinitializer, i32 %nz.s.o, 0
  %o = insertvalue { i32, i1 } %nz.a.o, i1 %nz.c.o, 1
  %ov = extractvalue { i32, i1 } %o, 1
  %p = call i32 @__bennett_rt_ctpop_i32(i32 %m)
  %z = zext i1 %ov to i32
  %r = add i32 %p, %z
  ret i32 %r
}

declare i32 @llvm.smax.i32(i32, i32)

declare { i32, i1 } @llvm.uadd.with.overflow.i32(i32, i32)

declare i32 @llvm.ctpop.i32(i32)

declare i32 @__bennett_rt_ctpop_i32(i32)
```

```text native=n-intrinsics
k(7, -3) = 4
k(-1, -1) = 33
k(2147483647, 1) = 31
```

*(non-normative)* k(7, −3): smax = 7, ctpop(7) = 3, and 7 + 0xFFFFFFFD overflows 32 bits, so 3 +
1 = 4. k(−1, −1): ctpop(0xFFFFFFFF) = 32, overflow, 33. k(2^31 − 1, 1): ctpop = 31, no unsigned
overflow, 31.

## 13. Floating point (arith contract)

NS §3.2: "Floating point is deterministic soft-float in both builds … Hardware floating point
never executes in either build." Every floating-point construct of every format has a row
here; none faults.

### 13.1 Soft-float rewrite (rules N19, N32)

**Formats and carriers:**

| LLVM type | Suffix | Carrier |
|---|---|---|
| `half` | `f16` | `i16` |
| `bfloat` | `bf16` | `i16` |
| `float` | `f32` | `i32` |
| `double` | `f64` | `i64` |
| `x86_fp80` | `f80` | `i80` |
| `fp128` | `f128` | `i128` |
| `ppc_fp128` | `ppcf128` | `i128` |

The rewrite of an instruction `%r` with floating-point operands or result is: first, for each
floating-point operand k (value or constant, in operand order), `%nz.<k>.r = bitcast <T>
<operand> to <carrier>`; then the call below, named `%nz.i.r`; then, for a floating-point result,
`%r = bitcast <carrier> %nz.i.r to <T>`. The entry points are defined by `bennett-arith` and are
part of its bitcode the driver links. B below is the format's suffix, C its carrier.

| Instruction | Call (carrier operands in order) | Result |
|---|---|---|
| `fadd`, `fsub`, `fmul`, `fdiv`, `frem` | `C @__bennett_sf_{add,sub,mul,div,rem}_B(C, C)` | bitcast |
| `fcmp <p>` | `i1 @__bennett_sf_cmp_B(C, C, i32 P)`, P the LLVM predicate number: `false` 0, `oeq` 1, `ogt` 2, `oge` 3, `olt` 4, `ole` 5, `one` 6, `ord` 7, `ueq` 8, `ugt` 9, `uge` 10, `ult` 11, `ule` 12, `une` 13, `uno` 14, `true` 15 | `%r` is the call itself |
| `fptosi`/`fptoui` to iM, `llvm.fptosi.sat`/`llvm.fptoui.sat` to iM | `i128 @__bennett_sf_{fptosi,fptoui}_B(C, i32 M)` | `%r = trunc i128 %nz.i.r to iM` (the call is `%r` when M = 128) |
| `sitofp`/`uitofp` from iM | `%nz.x.r = sext`/`zext iM a to i128` (omitted when M = 128), `C @__bennett_sf_{sitofp,uitofp}_B(i128)` | bitcast |
| `fpext`, `fptrunc` from format S to format D; `llvm.convert.to.fp16`, `llvm.convert.from.fp16` | `D_carrier @__bennett_sf_{fpext,fptrunc}_S_D(S_carrier)` | bitcast |
| `llvm.fptrunc.round(x, mode)` | `D_carrier @__bennett_sf_fptrunc_S_D_rm(S_carrier, i32 R)`, R from the mode (§13.5) | bitcast |
| `llvm.sqrt`, `llvm.floor`, `llvm.ceil`, `llvm.trunc`, `llvm.round`, `llvm.roundeven`, `llvm.rint`, `llvm.nearbyint`, `llvm.canonicalize` | `C @__bennett_sf_<name>_B(C)` | bitcast |
| `llvm.minnum`, `llvm.maxnum`, `llvm.minimum`, `llvm.maximum`, `llvm.minimumnum`, `llvm.maximumnum` | `C @__bennett_sf_<name>_B(C, C)` | bitcast |
| `llvm.fma` | `C @__bennett_sf_fma_B(C, C, C)` | bitcast |
| `llvm.is.fpclass(x, mask)` | `i1 @__bennett_sf_isfpclass_B(C, i32 mask)` | the call |
| `llvm.ldexp(x, e)`, `llvm.frexp(x)` | `C @__bennett_sf_ldexp_B(C, i32 e)`; `{ C, i32 } @__bennett_sf_frexp_B(C)` | bitcast (for frexp: of field 0) |
| `llvm.lround`, `llvm.llround`, `llvm.lrint`, `llvm.llrint` to iM | `i128 @__bennett_sf_{lround,llround,lrint,llrint}_B(C, i32 M)` | `trunc` to iM |
| `llvm.convert.to.arbitrary.fp`, `llvm.convert.from.arbitrary.fp` (format named by metadata) | `@__bennett_sf_convert_to_<fmt>_B` / `@__bennett_sf_convert_from_<fmt>_B` with LLVM APFloat's semantics of the named format | bitcast |
| `fneg`, `llvm.fabs`, `llvm.copysign`, `bitcast`, `load`, `store`, `select`, `phi` | unchanged: bit-exact operations (LangRef) | – |

**Semantics of the entry points** (the contract with `bennett-arith`): IEEE 754-2019 for
binary16 (`half`), binary32, binary64 and binary128; `bfloat` is the IEEE-style format with 8
exponent and 7 fraction bits; `x86_fp80` is the 80-bit x87 extended format (64-bit significand
with explicit integer bit; encodings with exponent ≠ 0 and integer bit 0, the unnormals, and
pseudo-denormals and pseudo-infinities are treated as NaN inputs, as modern x87 hardware does);
`ppc_fp128` is double-double with the operations of LLVM's APFloat `PPCDoubleDouble` semantics of
the major in use. For all formats: round to nearest ties to even, subnormals supported, no
observable flags or exceptions (except §13.5); **every NaN result is the format's canonical NaN**
(sign 0, quiet bit set, other payload bits 0: `0x7E00` f16, `0x7FC0` bf16, `0x7FC00000` f32,
`0x7FF8000000000000` f64, `0x7FFFC000000000000000` f80, `0x7FFF8000…0` f128, and for ppcf128
the f64 canonical NaN in the high double and +0 in the low); `rem` is C `fmod` (exact, the sign of
the dividend); `cmp` is LLVM's `fcmp` for the predicate; `fptosi`/`fptoui` and the `.sat` forms
truncate toward zero, map NaN to 0 and saturate values outside the range of iM to its bounds,
returned sign-extended (`fptosi`) or zero-extended (`fptoui`) in i128; `sitofp`/`uitofp` round to
nearest even; `minnum`/`maxnum` are IEEE 754-2008 minNum/maxNum (one NaN operand: the other
operand; two: the canonical NaN) with −0 < +0; `minimum`/`maximum` are IEEE 754-2019 (either NaN:
the canonical NaN) with −0 < +0; `minimumnum`/`maximumnum` are IEEE 754-2019 minimumNumber/
maximumNumber; `sqrt`, `fma` and every rounding function are correctly rounded (`round` ties
away from zero, `rint` and `nearbyint` to nearest even); `fpext` is exact; `fptrunc` rounds to
nearest even; `canonicalize` maps every NaN to the canonical NaN and is the identity otherwise;
`is.fpclass` tests LangRef's ten classes on the bit pattern; `ldexp`/`frexp` are exact up to
rounding of a subnormal `ldexp` result; `lround`/`llround` round half away from zero and `lrint`/
`llrint` to nearest even, saturating like `fptosi`. *(non-normative)* `fneg`, `fabs` and
`copysign` stay bit-exact, so a NaN's sign bit set by `fneg` survives, as LangRef requires; an
implementation of `half` and `bfloat` + − × ÷ √ in binary32 followed by one rounding is
correctly rounded, since 24 ≥ 2p + 2 for p = 11 and p = 8 (Figueroa's double-rounding bound), but
the contract is correct rounding, so `fma` needs its own implementation.

### 13.2 Vector floating point

After N21 every vector floating-point operation is scalar: §13.1 applies lane by lane, and
`vector.reduce.fadd`/`fmul` are the ordered left folds of §12.6 (exact once N2 has removed
`reassoc`).

### 13.3 Formats beyond binary32 and binary64

All seven formats of §13.1 are covered by the same table and contract (NS §3.2: "coverage-report
lines until the library covers them"; `bennett-arith` covers them, so they are `lowered`). musl's
`fmt_fp` (`printf("%Lf")`, rung 3) uses `x86_fp80` on x86-64 and `fp128` on AArch64 and RISC-V64.

### 13.4 Transcendentals and libm intrinsics (N33)

`llvm.sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`, `sinh`, `cosh`, `tanh`, `exp`, `exp2`,
`exp10`, `log`, `log2`, `log10`, `pow`, `powi`, `sincos`, `sincospi` and `modf` become calls of
the **runtimes libm**: `@<name>` for `double`, `@<name>f` for `float`, `@<name>l` for the
target's `long double` (`x86_fp80` or `fp128`), and for `half`, `bfloat` and the other
`fp128`/`ppc_fp128` cases the call of the `float`, respectively `long double`, function on the
`fpext`ed value followed by `fptrunc`; `powi(x, n)` becomes `__bennett_rt_powi_B(x, n)` (the
repeated squaring of compiler-rt's `__powidf2`); `sincos(x)` becomes the pair (sin x, cos x),
`sincospi(x)` the pair (sinpi x, cospi x), `modf(x)` the pair (fractional, integral). The runtimes
libm is musl-derived and compiled through this pipeline, so it is soft-float code itself and the
same function runs in both builds; calls of `sin`, `exp`, … in source resolve to it by §4.5. The
certificate records the runtimes version. No correct-rounding claim is required; bit-exact
determinism is (NS §3.2).

### 13.5 Constrained intrinsics, `strictfp` and the floating-point environment

`llvm.experimental.constrained.<op>(…, metadata <rounding>, metadata <except>)` becomes the
soft-float call of §13.1 with the suffix `_rm` and an extra `i32 R` operand: R = 0 for
`round.tonearest`, 1 `round.downward`, 2 `round.upward`, 3 `round.towardzero`, 4
`round.tonearestaway`, and for `round.dynamic` the value loaded from the runtimes global
`__bennett_rt_fenv` (field `round`); when `<except>` is not `fpexcept.ignore`, the entry point
ORs the IEEE flags it raises (invalid 1, divbyzero 2, overflow 4, underflow 8, inexact 16) into
`__bennett_rt_fenv` (field `flags`). `llvm.get.rounding`, `set.rounding`, `get.fpenv`,
`set.fpenv`, `reset.fpenv`, `get.fpmode`, `set.fpmode`, `reset.fpmode` read and write that state;
musl's `<fenv.h>` functions in `bennett-runtimes` do the same. Unconstrained operations use round
to nearest and raise no flags, as LLVM assumes of the default environment. A `strictfp` call-site
attribute on a marker is benign (§3.6).

### 13.6 Examples

```llvm normalise-in=n-fmuladd
define internal double @fm(double %a, double %b, double %c) {
  %r = call double @llvm.fmuladd.f64(double %a, double %b, double %c)
  ret double %r
}

declare double @llvm.fmuladd.f64(double, double, double)
```

```llvm normalise-out=n-fmuladd
define internal double @fm(double %a, double %b, double %c) {
  %nz.0.nz.m.r = bitcast double %a to i64
  %nz.1.nz.m.r = bitcast double %b to i64
  %nz.i.nz.m.r = call i64 @__bennett_sf_mul_f64(i64 %nz.0.nz.m.r, i64 %nz.1.nz.m.r)
  %nz.m.r = bitcast i64 %nz.i.nz.m.r to double
  %nz.0.r = bitcast double %nz.m.r to i64
  %nz.1.r = bitcast double %c to i64
  %nz.i.r = call i64 @__bennett_sf_add_f64(i64 %nz.0.r, i64 %nz.1.r)
  %r = bitcast i64 %nz.i.r to double
  ret double %r
}

declare double @llvm.fmuladd.f64(double, double, double)

declare i64 @__bennett_sf_mul_f64(i64, i64)

declare i64 @__bennett_sf_add_f64(i64, i64)
```

```text native=n-fmuladd
fm(1.5, 2.0, 0.25) = 3.25 (0x400a000000000000), input and output modules
fm(0.1, 10.0, -1.0) = 0.0 (0x0000000000000000), output module on every target; input module: 0.0 for -march=x86-64, 5.551115123125783e-17 (0x3c90000000000000) for -march=haswell
```

*(non-normative)* The double nearest 0.1 is 0x3FB999999999999A = 0.1 + 2^−54/10 exactly, so its
exact product with 10 is 1 + 2^−54. Unfused, the product rounds to 1.0 (2^−54 is below half an
ulp of 1, 2^−53) and adding −1.0 gives 0.0; fused, the exact 1 + 2^−54 − 1 = 2^−54 is returned.
`llvm.fmuladd` lets the code generator choose, so the input module's result depends on the CPU;
N16 fixes the unfused meaning in both builds (spike F4).

Extended precision and libm intrinsics (N33):

```llvm normalise-in=n-fp80
define internal x86_fp80 @l(x86_fp80 %a, double %d) {
  %e = fpext double %d to x86_fp80
  %r = fadd x86_fp80 %a, %e
  ret x86_fp80 %r
}
```

```llvm normalise-out=n-fp80
define internal x86_fp80 @l(x86_fp80 %a, double %d) {
  %nz.0.e = bitcast double %d to i64
  %nz.i.e = call i80 @__bennett_sf_fpext_f64_f80(i64 %nz.0.e)
  %e = bitcast i80 %nz.i.e to x86_fp80
  %nz.0.r = bitcast x86_fp80 %a to i80
  %nz.1.r = bitcast x86_fp80 %e to i80
  %nz.i.r = call i80 @__bennett_sf_add_f80(i80 %nz.0.r, i80 %nz.1.r)
  %r = bitcast i80 %nz.i.r to x86_fp80
  ret x86_fp80 %r
}

declare i80 @__bennett_sf_fpext_f64_f80(i64)

declare i80 @__bennett_sf_add_f80(i80, i80)
```

```llvm normalise-in=n-libm
define internal double @e(double %x, float %y) {
  %a = call double @llvm.exp.f64(double %x)
  %b = call float @llvm.sin.f32(float %y)
  %c = fpext float %b to double
  %r = fadd double %a, %c
  ret double %r
}

declare double @llvm.exp.f64(double)

declare float @llvm.sin.f32(float)
```

```llvm normalise-out=n-libm
define internal double @e(double %x, float %y) {
  %a = call double @exp(double %x)
  %b = call float @sinf(float %y)
  %nz.0.c = bitcast float %b to i32
  %nz.i.c = call i64 @__bennett_sf_fpext_f32_f64(i32 %nz.0.c)
  %c = bitcast i64 %nz.i.c to double
  %nz.0.r = bitcast double %a to i64
  %nz.1.r = bitcast double %c to i64
  %nz.i.r = call i64 @__bennett_sf_add_f64(i64 %nz.0.r, i64 %nz.1.r)
  %r = bitcast i64 %nz.i.r to double
  ret double %r
}

declare double @llvm.exp.f64(double)

declare float @llvm.sin.f32(float)

declare double @exp(double)

declare float @sinf(float)

declare i64 @__bennett_sf_fpext_f32_f64(i32)

declare i64 @__bennett_sf_add_f64(i64, i64)
```

*(non-normative)* The calls of `exp` and `sinf` pass `double` and `float` values, which are
bit-exact moves; they resolve by §4.5 to the runtimes libm, whose own floating-point code has been
normalised by §13.1. The N33 rewrite runs before N32 in the sense that the libm calls it creates
are not floating-point instructions and are left alone by N32.

## 14. Calls and control transfer

### 14.1 Direct calls and recursion

Direct calls lower to CC/R `call` (ISA §4.1) and to lifted `lift.call`/`lift.ret` lprocs (ISA
§3.7), with the depth and stack faults of the budget (§9). Recursion is unrestricted.

### 14.2 Indirect calls

- **Candidate set** of an indirect call with callee value v: every `FN(F)` atom of AV(v) (§5),
  resolved through aliases; if AV(v) has the ⊤ flag, in addition every function whose LLVM
  function type equals the call's and whose address is used anywhere in the linked program
  (sound for defined C, C++ and Rust: a call through an incompatible type is undefined, and
  compatible C types lower to the same LLVM type under opaque pointers; SQLite §3). The device
  closure includes every candidate (§4.1).
- **Dispatch**: the compare tree of §16.4 over the candidates' A(F) values, sorted unsigned, with
  a static call at each leaf: CC/R `icmp eq` + `br` + `call @F_k` (ISA §4.1), lifted `lift.icmp.eq`
  + `qbranch` + `lift.call @L(F_k)` (ISA §4.2). `qjumpr` is intra-function only (ISA §4.2) and is
  not used for calls.
- **No match** (a value that is the address of no function of the program, or of a function
  without bitcode): F(4) `FAULT_UB_TRAP` (outline E13; calling through such a pointer is undefined
  or reaches code without bitcode, which the coverage report names). **Zero candidates**: F(4) at
  the site.
- **Trampolines** (`llvm.init.trampoline(t, f, nval)`, `llvm.adjust.trampoline(t)`): `init`
  stores the tag `0x42454E54` (i32), A(f) and nval in the trampoline memory t (runtimes
  `__bennett_rt_tramp_init`); `adjust` returns t. Before the compare tree, an indirect call whose
  callee value v points to a live allocation holding the tag at offset 0 calls the stored
  function with the stored nest value as its `nest` argument.
- Calls through a variadic function type use §14.3. The same compare-tree construction serves
  region operands (§7.2), handle ids (§6.5), descriptor shapes (§8.4), `switch` (§14.8) and
  `indirectbr` (§14.9).

```llvm example=indirect-table verdict=accept callees=gt,lt
define internal i32 @lt(i32 %a, i32 %b) {
  %c = icmp slt i32 %a, %b
  %r = zext i1 %c to i32
  ret i32 %r
}

define internal i32 @gt(i32 %a, i32 %b) {
  %c = icmp sgt i32 %a, %b
  %r = zext i1 %c to i32
  ret i32 %r
}

@cmps = internal constant [2 x ptr] [ptr @lt, ptr @gt]

define void @pick(i32 %which, i32 %a, i32 %b) {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %k = and i32 %which, 1
  %i = zext i32 %k to i64
  %p = getelementptr [2 x ptr], ptr @cmps, i64 0, i64 %i
  %f = load ptr, ptr %p
  %r = call i32 %f(i32 %a, i32 %b)
  %t = icmp ne i32 %r, 0
  br i1 %t, label %flip, label %out

flip:
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  br label %out

out:
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

A callee from host input dispatches over the address-taken functions of the call's type; here
`@lt` and `@gt` (their addresses are stored in `@cmps`), but not `@neg`, whose type differs:

```llvm example=indirect-host-pointer verdict=accept callees=gt,lt
define internal i32 @lt(i32 %a, i32 %b) {
  %c = icmp slt i32 %a, %b
  %r = zext i1 %c to i32
  ret i32 %r
}

define internal i32 @gt(i32 %a, i32 %b) {
  %c = icmp sgt i32 %a, %b
  %r = zext i1 %c to i32
  ret i32 %r
}

define internal i32 @neg(i32 %a) {
  %r = sub i32 0, %a
  ret i32 %r
}

@cmps = global [2 x ptr] [ptr @lt, ptr @gt]
@unary = global ptr @neg

define void @apply(ptr %f, i32 %a, i32 %b) {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %r = call i32 %f(i32 %a, i32 %b)
  %t = icmp ne i32 %r, 0
  br i1 %t, label %flip, label %out

flip:
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  br label %out

out:
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

### 14.3 Varargs (N23)

- A variadic definition `R @f(P…, ...)` becomes `R @f(P…, ptr %nz.va)`; every call of it, direct
  or through a variadic function type, passes a **va block** in place of the variadic arguments.
- A call site spills its variadic arguments (as the front end promoted them) into a va block
  `%nz.vb.<r>`, an alloca of the caller's entry block (so N24 places it in the caller's shadow
  frame), in argument order: argument j at the next offset aligned to max(8, ABI alignment of its
  type), occupying its size rounded up to 8 bytes (the x86-64 System V, AAPCS64 and RISC-V LP64
  memory-argument layout); argument j ≥ 1 is addressed by `%nz.vb<j>.<r>`.
- `llvm.va_start(ptr ap)` builds the target's `va_list` so that the front end's inline `va_arg`
  takes its memory path:

  | Target | `va_list` | Fields written by `va_start` |
  |---|---|---|
  | x86-64 System V | `{ i32 gp_offset, i32 fp_offset, ptr overflow_arg_area, ptr reg_save_area }` | gp_offset = 48, fp_offset = 176, overflow_arg_area = `%nz.va`, reg_save_area = null (SQLite §5.1): every `va_arg` finds no register slot left |
  | AArch64 AAPCS64 | `{ ptr __stack, ptr __gr_top, ptr __vr_top, i32 __gr_offs, i32 __vr_offs }` | __stack = `%nz.va`, __gr_top = __vr_top = null, __gr_offs = __vr_offs = 0 |
  | RISC-V LP64 | `ptr` | the pointer `%nz.va` |

  The stores are named `%nz.vfo.<r>` (x86-64 `fp_offset` address), `%nz.vov.<r>` (overflow area
  address), `%nz.vrs.<r>` (register save area address); AArch64 and RISC-V use `%nz.vs.<r>`,
  `%nz.vgt.<r>`, `%nz.vvt.<r>`, `%nz.vgo.<r>`, `%nz.vvo.<r>` in field order.
- IR `va_arg` is expanded by the same memory layout; `llvm.va_copy(d, s)` copies the
  `va_list` record (24, 32 or 8 bytes); `llvm.va_end` is deleted.
- A call of an external variadic function without bitcode passes the va block to its host call
  (§11.4) or is trapped (§4.5). One table row per target ABI; adding a target adds a row (§24).

```llvm normalise-in=n-varargs
%struct.__va_list_tag = type { i32, i32, ptr, ptr }

define internal i32 @sum(i32 %n, ...) {
entry:
  %ap = alloca %struct.__va_list_tag, align 16
  call void @llvm.va_start(ptr %ap)
  br label %loop

loop:
  %i = phi i32 [ 0, %entry ], [ %i2, %got ]
  %s = phi i32 [ 0, %entry ], [ %s2, %got ]
  %done = icmp sge i32 %i, %n
  br i1 %done, label %out, label %arg

arg:
  %gp = load i32, ptr %ap, align 16
  %fits = icmp ult i32 %gp, 41
  br i1 %fits, label %inreg, label %inmem

inreg:
  %rsap = getelementptr %struct.__va_list_tag, ptr %ap, i64 0, i32 3
  %rsa = load ptr, ptr %rsap, align 16
  %gp64 = zext i32 %gp to i64
  %ra = getelementptr i8, ptr %rsa, i64 %gp64
  %gp2 = add i32 %gp, 8
  store i32 %gp2, ptr %ap, align 16
  br label %got

inmem:
  %ovp = getelementptr %struct.__va_list_tag, ptr %ap, i64 0, i32 2
  %ov = load ptr, ptr %ovp, align 8
  %ov2 = getelementptr i8, ptr %ov, i64 8
  store ptr %ov2, ptr %ovp, align 8
  br label %got

got:
  %addr = phi ptr [ %ra, %inreg ], [ %ov, %inmem ]
  %v = load i32, ptr %addr, align 4
  %s2 = add i32 %s, %v
  %i2 = add i32 %i, 1
  br label %loop

out:
  call void @llvm.va_end(ptr %ap)
  ret i32 %s
}

define i32 @top(i32 %x) {
  %r = call i32 (i32, ...) @sum(i32 3, i32 %x, i32 20, i32 300)
  ret i32 %r
}

declare void @llvm.va_start(ptr)

declare void @llvm.va_end(ptr)
```

```llvm normalise-out=n-varargs
%struct.__va_list_tag = type { i32, i32, ptr, ptr }

define internal i32 @sum(i32 %n, ptr %nz.va) {
entry:
  %nz.fp.sum = call ptr @__bennett_rt_ss_push(i64 24, i64 16)
  %ap = getelementptr i8, ptr %nz.fp.sum, i64 0
  store i32 48, ptr %ap, align 4
  %nz.vfo.sum.0 = getelementptr i8, ptr %ap, i64 4
  store i32 176, ptr %nz.vfo.sum.0, align 4
  %nz.vov.sum.0 = getelementptr i8, ptr %ap, i64 8
  store ptr %nz.va, ptr %nz.vov.sum.0, align 8
  %nz.vrs.sum.0 = getelementptr i8, ptr %ap, i64 16
  store ptr null, ptr %nz.vrs.sum.0, align 8
  br label %loop

loop:
  %i = phi i32 [ 0, %entry ], [ %i2, %got ]
  %s = phi i32 [ 0, %entry ], [ %s2, %got ]
  %done = icmp sge i32 %i, %n
  br i1 %done, label %out, label %arg

arg:
  %gp = load i32, ptr %ap, align 16
  %fits = icmp ult i32 %gp, 41
  br i1 %fits, label %inreg, label %inmem

inreg:
  %rsap = getelementptr %struct.__va_list_tag, ptr %ap, i64 0, i32 3
  %rsa = load ptr, ptr %rsap, align 16
  %gp64 = zext i32 %gp to i64
  %ra = getelementptr i8, ptr %rsa, i64 %gp64
  %gp2 = add i32 %gp, 8
  store i32 %gp2, ptr %ap, align 16
  br label %got

inmem:
  %ovp = getelementptr %struct.__va_list_tag, ptr %ap, i64 0, i32 2
  %ov = load ptr, ptr %ovp, align 8
  %ov2 = getelementptr i8, ptr %ov, i64 8
  store ptr %ov2, ptr %ovp, align 8
  br label %got

got:
  %addr = phi ptr [ %ra, %inreg ], [ %ov, %inmem ]
  %v = load i32, ptr %addr, align 4
  %s2 = add i32 %s, %v
  %i2 = add i32 %i, 1
  br label %loop

out:
  call void @__bennett_rt_ss_pop(ptr %nz.fp.sum)
  ret i32 %s
}

define i32 @top(i32 %x) {
  %nz.fp.top = call ptr @__bennett_rt_ss_push(i64 24, i64 8)
  %nz.vb.r = getelementptr i8, ptr %nz.fp.top, i64 0
  store i32 %x, ptr %nz.vb.r, align 8
  %nz.vb1.r = getelementptr i8, ptr %nz.vb.r, i64 8
  store i32 20, ptr %nz.vb1.r, align 8
  %nz.vb2.r = getelementptr i8, ptr %nz.vb.r, i64 16
  store i32 300, ptr %nz.vb2.r, align 8
  %r = call i32 @sum(i32 3, ptr %nz.vb.r)
  call void @__bennett_rt_ss_pop(ptr %nz.fp.top)
  ret i32 %r
}

declare ptr @__bennett_rt_ss_push(i64, i64)

declare void @__bennett_rt_ss_pop(ptr)
```

```text native=n-varargs
top(1) = 321
top(-320) = 0
top(2147483000) = 2147483320
```

*(non-normative)* The input is the shape clang's inline x86-64 `va_arg` expansion takes after
`default<O2>` (with the loop bound left as a parameter). With gp_offset = 48 the `fits` test
(gp_offset < 41) is always false, so every argument is read from `overflow_arg_area`, which is the
va block: slots at offsets 0, 8, 16 hold x, 20, 300, and the sum is x + 320.

### 14.4 Unwinding (N28: explicit propagation)

The runtimes keep the **EH state** in the global `__bennett_rt_eh` of type `{ i32 active, i32
selector, ptr object }` (active: 0 none, 1 exception, 2 longjmp, 3 fiber switch, 4 exit; §14.5–
§14.7). Every device variant is rewritten, and the native comparison build uses the same
materialised code, so the behaviour is identical in both builds:

- `invoke F(args) to label %N unwind label %U` → `call F(args)`; `%nz.ehl.<r> = load i32, ptr
  @__bennett_rt_eh`; `%nz.ehc.<r> = icmp ne i32 %nz.ehl.<r>, 0`; `br i1 %nz.ehc.<r>, label %U,
  label %N`.
- A `call` of a function that may unwind (one without `nounwind`, or an indirect call) inside a
  function that may unwind → the same check after the call, branching on a set flag to the
  function's **early-return block** `nz.ehr.<f>`, which pops the shadow frame (§17.3) and returns
  the zero of the return type.
- `%r = landingpad T clauses` → `%r = call { ptr, i32 } @__bennett_rt_eh_match(ptr P, ptr
  @nz.lp.<f>.<r>)`, where P is the function's personality and `@nz.lp.<f>.<r>` is the private
  constant `{ i64 cleanup, i64 n, [n x { i64 kind, ptr info }] }` of the clauses in order (kind 0
  `catch` with its typeinfo, kind 1 `filter` with its array). The runtimes implement the
  personality's matching: for `__gxx_personality_v0`, C++ catch by typeinfo with the C++ ABI's
  derived-class rules and filters; for `rust_eh_personality`, Rust panics; for
  `__gcc_personality_v0`, cleanups only. A matching catch or a cleanup clears `active` and
  returns (object, selector) with selector = `llvm.eh.typeid.for` of the matched typeinfo (0 for
  a cleanup); when nothing matches (or the pseudo-exception is a longjmp, switch or exit, which no
  clause handles) the flag stays set, the selector is −1, and the normaliser's check after the
  call (`%nz.ehm.<r> = extractvalue … 1`, `icmp eq … −1`) branches to the early-return block.
- `resume v` → `call void @__bennett_rt_eh_resume({ ptr, i32 } v)` (sets `active` = 1 and the
  object) and a branch to the early-return block.
- `llvm.eh.typeid.for(ti)` → `call i32 @__bennett_rt_eh_typeid(ptr ti)`; `llvm.eh.exceptionpointer`
  and `llvm.eh.exceptioncode` read the state's object.
- `__cxa_throw`, `_Unwind_RaiseException`, `_Unwind_Resume`, `__rust_start_panic` are runtimes
  functions that set the state and return; the code after their call is the check above, and the
  original `unreachable` after them is kept on the path where the flag is clear (F(4)).
- Windows funclet pads (`catchswitch`, `catchpad`, `cleanuppad`, `catchret`, `cleanupret`) use the
  same transform with the `__CxxFrameHandler3` matching rules (corpus case needed, bd `-kdj`).
- **Unwinding out of a region**: a set flag when an oracle's region function returns is `fault 4`
  in the wrapper (§16.2); in an action's generation it is TDL-12's `fault` event with code 4; at
  an R entry or a CC device entry it ends the run with code 4 (§11.5). NS §3.1: "a fault code
  where it is not [handled in the region]".

```llvm normalise-in=n-eh
declare i32 @__gxx_personality_v0(...)

declare void @may_throw(i32)

define internal i32 @eh(i32 %x) personality ptr @__gxx_personality_v0 {
entry:
  invoke void @may_throw(i32 %x)
          to label %ok unwind label %lp

ok:
  ret i32 0

lp:
  %e = landingpad { ptr, i32 }
          catch ptr null
  ret i32 1
}
```

```llvm normalise-out=n-eh
@__bennett_rt_eh = external global { i32, i32, ptr }
@nz.lp.eh.e = private constant { i64, i64, [1 x { i64, ptr }] } { i64 0, i64 1, [1 x { i64, ptr }] [{ i64, ptr } { i64 0, ptr null }] }

declare i32 @__gxx_personality_v0(...)

declare void @may_throw(i32)

define internal i32 @eh(i32 %x) {
entry:
  call void @may_throw(i32 %x)
  %nz.ehl.eh.0 = load i32, ptr @__bennett_rt_eh, align 4
  %nz.ehc.eh.0 = icmp ne i32 %nz.ehl.eh.0, 0
  br i1 %nz.ehc.eh.0, label %lp, label %ok

ok:
  ret i32 0

lp:
  %e = call { ptr, i32 } @__bennett_rt_eh_match(ptr @__gxx_personality_v0, ptr @nz.lp.eh.e)
  %nz.ehm.e = extractvalue { ptr, i32 } %e, 1
  %nz.ehn.e = icmp eq i32 %nz.ehm.e, -1
  br i1 %nz.ehn.e, label %nz.ehr.eh, label %nz.lpc.e

nz.lpc.e:
  ret i32 1

nz.ehr.eh:
  ret i32 0
}

declare { ptr, i32 } @__bennett_rt_eh_match(ptr, ptr)
```

```text native=n-eh
eh(2) = 0; eh(3) = 1; eh(-5) = 1 (input built with clang++ and a C++ may_throw that throws when x is odd; output built with the runtimes seeds, whose may_throw sets the EH state)
```

### 14.5 setjmp and longjmp (N29)

- A call of `setjmp`, `_setjmp`, `sigsetjmp` or `__sigsetjmp` with buffer b in function f
  becomes a block boundary: `call void @__bennett_rt_setjmp(ptr b, ptr %nz.fp.<f>, i32 k)` stores
  the **frame token** (f's shadow-frame address, §17.3) and the site index k (0-based among f's
  setjmp sites) in b, and the call's result becomes the phi `%r = phi i32 [ 0, <normal> ], [ v,
  %nz.sj<k>.<f> ]` at the continuation.
- `longjmp(b, v)` (and `siglongjmp`, `_longjmp`) is a runtimes function that sets the EH state to
  the longjmp pseudo-exception (`active` = 2, object = b, selector = v, with v = 0 replaced by 1)
  and returns; propagation is §14.4 (landing pads do not handle it).
- In every function containing a setjmp site, the check after each call that may unwind also
  tests `active` = 2 and the frame token and site index stored in b; on a match it clears the
  state and branches to `%nz.sj<k>.<f>`, the continuation of site k with value v. SSA values live
  into the continuation take, on that path, their values at the call after which the longjmp was
  detected (C makes non-volatile locals modified after `setjmp` indeterminate; memory is the
  shadow frame's).
- This covers `longjmp` to an active frame, the only defined case in C, and Julia's `jl_try`
  (`sigsetjmp`, rung 5). A `longjmp` to a frame that has returned reaches the device entry and
  faults (code 4, §14.4).

### 14.6 Fibers and context switches (N30: rewindable frames)

- **Switch primitives**: the runtimes' `swapcontext`, `makecontext`, `setcontext`, Julia's task
  switch (`jl_swap_fiber`, `ctx_switch`), and the platform shims `swtch` and `__switch_to` (§20.5);
  all are implemented by `__bennett_rt_fiber_switch(from, to)` over records that hold a fiber's
  shadow stack (the `makecontext` stack argument) and its saved frame chain.
- Every function on a call-graph path to a switch primitive is **instrumented**, Asyncify-style:
  its SSA values that are live across a call that may switch are spilled to its shadow frame
  before the call and reloaded after it, and it gets a resume index (the call site it was
  suspended at).
- A switch sets the EH state to `active` = 3 and propagates (§14.4): each instrumented frame on
  the way out saves its resume index and returns early, up to the fiber's base; the runtime
  records the chain, then **rewinds** the target fiber: it calls the target's base with the
  rewind state, and each instrumented frame jumps to its saved resume index, reloads its values
  and calls the next frame, until the target's switch call returns.
- This works in CC, R and L on ISA 0.8: it is ordinary code over memory. G-16 (ISA fibers,
  §25.3) is the efficient alternative.

### 14.7 `exit`, `abort`, `_Exit`

- `abort` → F(4).
- musl's `exit` runs the `atexit` handlers and flushes stdio, then calls `_Exit(s)`. `_Exit(s)`
  (the runtimes' `exit_group` system call) sets the EH state to the **exit pseudo-exception**
  (`active` = 4, selector = s) and propagates.
- An R or CC whole-program entry (§19.2) catches it and returns s as the program's status; an
  oracle wrapper in "oracle from program" mode (§19.3) catches it and delivers s as the payload;
  a CC device entry of a host program catches it and makes `hostcall bennett.exit` with s, whose
  host stub calls `_Exit(s)`. Elsewhere (inside an oracle in the plain marker form, inside an
  action) it is unwinding out of the region: code 4.

### 14.8 `switch`

`switch` lowers by the compare tree of §16.4 in L, and by the same tree of `icmp`/`br` in CC and R
(ISA has no switch instruction).

### 14.9 `blockaddress` and `indirectbr`

`blockaddress(@f, %bb)` has the device value A(f) + 4·(1 + i), where i is the index of %bb among
f's address-taken blocks in layout order. `indirectbr ptr v, [labels]` dispatches with the compare
tree over the labels' values to static branches (`qjump` in L, `br` in CC/R); no match is F(4).
*(non-normative)* LangRef permits a `blockaddress` only in `indirectbr` and in comparisons with
null; an execution in which its bits influence a result otherwise (printing, hashing) is
layout-dependent and validated against the reference interpreter (NS §3.2, §17.1).

<!-- APPEND -->
