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

**Verification.** For every compiled pair, every budget in the token's dispatch domain (§9.5)
and every argument tuple: when N ≤ the configured width (driver option
`-bennett-inplace-exhaustive-bits`, default 24, §24), the plugin MUST run the reference
interpreter on both reference bodies and check that for every x ∈ [0, 2^N), F_B^g(x) = (y, 0)
and F_B^ginv(y) = (x, 0); above that width it MUST record a `sampled` evidence claim (ISA §12.1)
of the same check, and the dynamic net applies: a wrong inverse leaves the scratch register of
the `qinplace` expansion non-clean, which `T-CLEAN` catches (NS §3.1). A pair that fails the
check is `BD-E-INPLACE-NOT-INVERSE` (NS §3.1: "an in-place update with no inverse fails loud at
compile time"; "a fallible computation cannot be in-place"). *(non-normative)* On a finite set,
ginv∘g = id makes g injective, hence a bijection, so g∘ginv = id and ginv is fault-free on every
input, as ISA `qinplace` requires. 0.1's `BD-E-INPLACE-UNVERIFIED` is deleted.

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

<!-- APPEND -->
