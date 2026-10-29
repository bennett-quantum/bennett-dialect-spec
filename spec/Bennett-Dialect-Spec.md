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
  Bennett.jl emits `ptr @f` in its own module (LLVM.jl). A Julia `@cfunction` pointer is an
  `inttoptr` constant of an address; it is dispatched by value against the address-taken
  functions of the required type (§7.2), so it resolves whenever the body is in the link
  (audit B-14).
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

<!-- APPEND -->
