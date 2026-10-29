# Bennett LLVM Dialect — Specification, draft 0.1

**Date:** 2026-10-29. **Status:** founding draft 0.1 of `bennett-dialect-spec`
(`Bennett-NorthStar.md` §3, §6.1), written for the first council round;
not yet graded. Nothing is implemented. It targets the Bennett virtual
ISA **draft 0.8** (`bennett-isa-spec/spec/Bennett-ISA-Spec.md`, council
accepted 2026-10-28), cited here as "ISA §n". MUST, MUST NOT, SHOULD, MAY
are normative; *(non-normative)* explains; every decision an implementer
must take and that this draft does not settle carries a **default** in
§14, which implementers follow until the item is revised.

**Versioning.** Dialect 0.1: markers 0.1, handles 0.1, regions 0.1,
norm 0.1, map 0.1, corpus 0.1; targets ISA 0.8. The **full version
string** (`0.1`) is the compatibility unit (§13): drafts are not
compatible with each other.

**Sources.** North star §3, §4.2, §5.1, §6.1; the legality spike
(`docs/spikes/2026-10-28-legality-spike.md`, `-triage.md`,
`-findings.md`, `enzyme-prior-art.md`, `emission/SUMMARY.md`,
`corpus/legality/`). The maintainer decisions of the spike findings §3
(region identity by content; handle provenance through bitwise copies;
region operands dispatched at run time over a bounded candidate set) are
binding and are applied in §5 and §6.

---

## 1. Scope and conformance

### 1.1 What the dialect is

The dialect is the contract between **front ends** that emit LLVM IR
containing calls to `__bennett_*` marker functions and the **plugin**
that, at the final link of a whole program, recognises those calls,
normalises the code they reach and maps it onto the ISA (ISA §1.1). It
fixes: the marker ABI (§3); the device closure (§4); the handle
convention and its provenance rules (§5); regions, their operands,
identity, well-formedness and budgets (§6); the materialised
normalisation and the residual-poison validator (§7); a reference
semantics from marker programs to the ISA formal model (§8, §9); the
legality corpus as a conformance artefact (§10); the driver's
plugin-invocation interface (§11). It does not fix the plugin's
lowering strategy, its optimisation pipeline after normalisation, or any
format the ISA owns.

### 1.2 Conformance classes

| Class | Who | Obligation |
|---|---|---|
| Producer | front ends (clang, rustc, Bennett.jl, importers) | emit modules that satisfy §3 and §6.6; never emit `__bennett_nz_*` or `__bennett_sf_*` names (§3.1) |
| Plugin | `bennett-plugin` and competitors | the processing order of §4.1; accept exactly the modules the rules accept, with the diagnostics of §12; produce ISA objects whose execution equals the reference semantics (§8.7); suites DA–DS (§10.3) |
| Driver | `bennett-driver` | §11; links `bennett-runtimes` and `bennett-arith` bitcode; builds the native comparison binary (§7.6) |
| Validator | the plugin's validator and `bennett-conformance` | the residual-poison validator (§7.5) and the reference recogniser (§3.5, §5, §6.2), implemented independently; suites DA–DN (§10.3) |

`scripts/dialect_check.py` in this repository is the seed of the
reference recogniser, the residual-poison validator and the lifting map
(§9); it executes every example of this document (§1.5).

### 1.3 Relation to the ISA specification

The ISA is settled; this document never redefines it. Every ISA notion
used here (wires, `qreg` handles, oracles, actions, F_B, budgets, fault
codes, the reference interpreter, interface hashes) has exactly the
meaning ISA §2–§16 give it. Where the dialect needs something ISA 0.8
does not provide, this document states a dialect-side default that stays
inside ISA 0.8 and files an **open item** for a future ISA revision
(§15); it never extends the ISA unilaterally.

### 1.4 Departures from the north star

| North star | Dialect 0.1 | Why |
|---|---|---|
| north star §3.1 handle row: a handle through an `inttoptr`/`ptrtoint` round trip is rejected | Provenance flows through bitwise copies (§5.2) | Spike F1: `instcombine` creates such round trips from plain C; maintainer decision 2 (north-star amendment A2) |
| north star §3.1: regions entered as `__bennett_ctrl(q, @f, …)` with a constant `@f` | Region operands are classical data dispatched over a bounded candidate set (§6.2) | Spike F3; maintainer decision 3 |
| Region named by symbol | Region identity is by content (§6.3) | Spike F2, triage finding 3; maintainer decision 1 |
| north star §3.1: lifted oracles are found by taint analysis inside any region | Coherent (lifted) classical code is entered only through `__bennett_oracle` and `__bennett_inplace` (§6.1); the classical code of `ctrl`/`adj`/`compute` bodies runs classically, once, and only their quantum operations are controlled or inverted (§8.4) | The ISA 0.8 action body has no classical computation (ISA §5.3), so a body whose circuit depends on classical data can only be expressed by classical generation; taint-driven lifting of arbitrary bodies is deferred (§14 D17) |
| north star §3.1: `__bennett_ctrl(q, @f, budget, …)` budget bounds the coherent body | The `ctrl` and `reversible` budget operands have no effect in 0.1 (§6.5) | Follows from the row above (ctrl) and from ISA 0.8 having no R-tier budget (§15 ISA-2) |
| north star §3.1: `__bennett_inplace(@g, @ginv, …)` takes the in-place operand in an environment | `__bennett_inplace(g, ginv, budget, x)` takes the register `x` and no classical arguments | ISA `qinplace` (ISA §4.5) has no classical-argument slot (§15 ISA-3) |
| north star §3.1, §4.2: a `qstore` into a register not known to be clean is a compile-time error | `qstore` is the ISA's XOR store with no static cleanliness rule (§5.5) | A register-granularity rule forbids the uncomputing second store; a cell-granularity rule is undecidable for superposed addresses (§14 D7) |
| north star §3.2: normalisation of "the outlined region" | Normalisation applies to the whole device closure (§4.2, §7.1) | Device classical code is lowered to ISA CC, whose semantics differs from LLVM's poison semantics (ISA §4.1) |

### 1.5 Notation and checked examples

LLVM IR is LLVM's textual form with opaque pointers, as accepted by LLVM
18, 20 and 23. `pw` is the pointer width in bits of address space 0 in
the module's datalayout (64 when the module has no datalayout).

Every fenced block whose info string starts with `llvm` or `isa` is a
**checked example** and carries attributes `key=value`:

| Tag | Meaning; what the checker does |
|---|---|
| `llvm markers-ir` | the marker list of §3.2; compared with the C views (§3.3) |
| `c markers-c` | the C header view; byte-equal to `spec/bennett_markers.h` |
| `llvm example=ID verdict=V` | a module; it must parse and verify on LLVM 18, 20 and 23, and the reference recogniser must classify it as `V` (`accept` or `reject:<code>`, §12). Optional `candidates=f,g` states the resolved candidate set of every region operand (§6.2); optional `mode=validate` applies only the validator (§7.5) |
| `llvm normalise-in=ID` / `llvm normalise-out=ID` | the normaliser (§7.2), treating every defined function of the example as a device function, applied to the first must give the second (lines compared after collapsing runs of blanks); both verify on all three majors; the second passes the validator |
| `llvm lift=ID` | a region function; `verdict` as above (default `accept`) |
| `isa reference-body=ID` | the lifting map (§9) applied to `lift=ID` must give exactly this text |
| `text hash=ID` | the reference-body hash (§9.5) |
| `text fb=ID` | stated F_B results (§9.6), executed on the ISA reference interpreter semantics (ISA §14.1) |
| `text inplace=ID` | an in-place verification verdict (§6.4) |
| `llvm semantics=ID corpus=NAME` | a marker program; byte-equal to `corpus/legality/cases/NAME.ll`; run through the spike trace runtime and the reference semantics (§8) |
| `text events=ID input=X` / `text state=ID input=X at=K` | the stated ISA-level event list (§8.3) and the state vector before event `K` |

A module example that calls a marker without declaring it implicitly
contains the declaration of §3.2. **Section references**: `§n` is a
section of this document, `ISA §n` of the ISA specification, `north
star §n` of `Bennett-NorthStar.md`; a reference that continues a list
(`ISA §4.7, §5.3`, `ISA §2–§16`) names the same document as the reference
before it. Fenced blocks without a tag are
illustrations and are non-normative; an `llvm` or `isa` block without a
tag is an error of this document.

### 1.6 Diagnostics and verdicts

A plugin that rejects a module MUST fail the compilation (nonzero exit,
no output object) and MUST report at least the first diagnostic in the
processing order of §4.1, with its code from §12. A module's **verdict**
is `accept` or `reject:<code of that first diagnostic>`.

## 2. Terminology

- **Marker**: one of the 16 functions of §3.2. **Marker call**: a `call`
  or `invoke` whose callee is a marker (§3.5).
- **Primitive**: a function the normaliser introduces: `__bennett_nz_fault`
  (§7.2) and the soft-float entry points `__bennett_sf_*` (§7.3).
- **Handle**: the `ptr` value a `__bennett_qalloc` or `__bennett_qborrow`
  call returns; it denotes a **register** of n qubits, the ISA's
  `qreg[n]` (ISA §3.3). Qubit `i` of a handle is a **wire**.
- **Root**: a `qalloc` or `qborrow` call instruction. **Handle-derived**:
  a value whose provenance (§5.2) contains a root.
- **Region function**: a function a region-entry marker receives.
  **Region operand**: the marker operand that names it. **Candidate
  set**: the functions a region operand can denote (§6.2).
- **Action region**: a candidate of a `ctrl`, `adj` or `compute`
  operand; a quantum action in the sense of ISA §5.3. **Oracle region**:
  a candidate of an `oracle` or `inplace` operand; a lifted oracle in the
  sense of ISA §5.2. **Reversible region**: a candidate of a
  `reversible` operand; R-tier code (ISA §3.1).
- **Device closure**, **device function**, **host function**, **device
  entry**: §4.2.
- **Materialised module**: the module after normalisation (§7.2).
- **Reference body**: the ISA oracle text the lifting map (§9) produces
  from an oracle region.
- **Generation**: the classical execution of an action region that
  records its quantum operations (§8.4).

## 3. The marker ABI

### 3.1 Reserved names

Every function or global name that starts with `__bennett_` is
reserved. A module given to the plugin:

1. MUST NOT define (`define`) a function with a marker name
   (`BD-E-MARKER-DEFINED`);
2. MUST NOT declare, define or reference a function or global whose
   name starts with `__bennett_` and is not a marker, unless the name
   starts with `__bennett_nz_` or `__bennett_sf_` and the module is a
   materialised module (`BD-E-MARKER-UNKNOWN`); producers never emit
   those two prefixes;
3. MUST NOT use a marker other than as the callee of a call or invoke
   (`BD-E-MARKER-ADDRESS`): no stored, compared, passed or cast marker
   address, so that no marker is ever called indirectly.

`__bennett_ctrl_v`, the variadic probe of the spike ABI v0, is not a
marker; it is rejected by rule 2.

### 3.2 The marker list

The normative IR signatures (return type, name, parameter types; the
parameter names are documentation):

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
declare void @__bennett_ctrl(ptr %q, i64 %qi, ptr %f, i64 %budget, ptr %env)
declare void @__bennett_adj(ptr %f, ptr %env)
declare void @__bennett_compute(ptr %f, ptr %use, ptr %env)
declare void @__bennett_reversible(ptr %f, i64 %budget, ptr %env)
declare void @__bennett_inplace(ptr %g, ptr %ginv, i64 %budget, ptr %x)
declare void @__bennett_oracle(ptr %f, i64 %budget, ptr %x, ptr %tgt, ptr %fault)
```

Operand roles, by marker (positions are 0-based):

| Marker | Handle operands | Region operands | Integer operands with a candidate requirement (§3.4) | Other |
|---|---|---|---|---|
| `qalloc`, `qborrow` | – | – | 0 `cls`, 1 `n` | – |
| `qfree` | 0 | – | – | – |
| `gate` | 1 | – | 0 `op` | 2 index |
| `gate2` | 1, 3 | – | 0 `op` | 2, 4 indices |
| `gate3` | 1, 3, 5 | – | 0 `op` | 2, 4, 6 indices |
| `rot` | 1 | – | 0 `op` | 2 index, 3 angle |
| `measure` | 0 | – | – | 1 index |
| `qload` | 0, 1, 2 | – | – | – |
| `qstore` | 0, 1, 2 | – | – | – |
| `ctrl` | 0 | 2 (action) | – | 1 index, 3 budget (no effect), 4 env |
| `adj` | – | 0 (action) | – | 1 env |
| `compute` | – | 0, 1 (action) | – | 2 env |
| `reversible` | – | 0 (reversible) | – | 1 budget (no effect), 2 env |
| `inplace` | 3 | 0, 1 (oracle, `iN (iN)`) | 2 `budget` | – |
| `oracle` | 2, 3, 4 | 0 (oracle, `iT (iN)`) | 1 `budget` | – |

Spike ABI v0 (`corpus/legality/markers.h`) differs from this list only
in: `gate3` and `oracle` are new; `inplace` changed from `(g, ginv,
env)` to `(g, ginv, budget, x)`; `ctrl_v` is gone. Every other marker
keeps its v0 signature, so the spike evidence applies to it unchanged.

### 3.3 C header view

`spec/bennett_markers.h` is the normative C and C++ header. Its
prototypes (in C++ each carries `noexcept`, which makes clang add
`nounwind`, a permitted attribute, and emit `call` rather than `invoke`):

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
void __bennett_ctrl(bennett_q q, uint64_t qi, bennett_region f, uint64_t budget, void *env) BENNETT_NOEXCEPT;
void __bennett_adj(bennett_region f, void *env) BENNETT_NOEXCEPT;
void __bennett_compute(bennett_region f, bennett_region use, void *env) BENNETT_NOEXCEPT;
void __bennett_reversible(bennett_region f, uint64_t budget, void *env) BENNETT_NOEXCEPT;
void __bennett_inplace(void *g, void *ginv, uint64_t budget, bennett_q x) BENNETT_NOEXCEPT;
void __bennett_oracle(void *f, uint64_t budget, bennett_q x, bennett_q tgt, bennett_q fault) BENNETT_NOEXCEPT;
```

with `typedef struct bennett_q_opaque *bennett_q;` and `typedef void
(*bennett_region)(void *env);`. Clang lowers C `bool` to `zeroext i1`,
which §3.2 admits (`zeroext` is permitted, §3.6). The checker compiles
the header with clang 18 and compares every declaration with §3.2.

### 3.4 Operand encodings

**Operation codes** (`op`; an operand outside its table is
`BD-E-OPERAND`):

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

"Then" is time order. The realisations are exact including global
phase, so Z and Y stay exact under control.

**Class** (`cls`): `0` denotes the ISA class `any` (ISA §4.3); every
other value is `BD-E-OPERAND` in 0.1 (§14 D1).

**Width** (`n`): the number of qubits, ≥ 1.

**Budget** (`budget` of `oracle` and `inplace`): the step budget B
(§6.5); the value `0xFFFFFFFFFFFFFFFF` (`BENNETT_BUDGET_DEFAULT`) means
"the driver's default budget".

**Candidate requirement.** After normalisation (§4.1 step S7), every
operand listed with a candidate requirement in §3.2 MUST have a finite
**constant candidate set** CS(v), defined by: a `ConstantInt` c gives
{c}; `select` gives the union over its two value operands; `phi` gives
the union over its incoming values; `zext`/`sext`/`trunc` of v gives the
image of CS(v); a `load` of an integer type whose pointer operand has a
base (§5.2) consisting only of offsets into globals declared `constant`
gives every element of that type in those initialisers (all elements
when the offset is `*`); anything else is unbounded
(`BD-E-OPERAND-UNBOUNDED`). Every member of CS must be valid for the
operand (`BD-E-OPERAND`): `op` in the table above; `cls` = 0; `n` ≥ 1;
any `budget`. *(non-normative)* The device dispatches on the run-time
value, which is always a member of CS.

Qubit **indices** and the rotation **angle** are unconstrained
classical values; their run-time conditions are in §8.3.

The `cfg-switch-op-table` shape (`default<O3>` sinks seven gate calls
into one with a phi of operation codes) is accepted; an invalid code, a
non-zero class and a width from host input are rejected:

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

Operation codes loaded from a constant table (SimplifyCFG's
switch-to-lookup on the `op` operand) resolve through the table:

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

```llvm example=operand-bad-code verdict=reject:BD-E-OPERAND
define void @top() {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  call void @__bennett_gate(i32 99, ptr %h, i64 0)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=operand-class verdict=reject:BD-E-OPERAND
define void @top() {
  %h = call ptr @__bennett_qalloc(i64 1, i64 1)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=operand-width-host verdict=reject:BD-E-OPERAND-UNBOUNDED
define void @top(i64 %n) {
  %h = call ptr @__bennett_qalloc(i64 0, i64 %n)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

### 3.5 Recognition

A call or invoke instruction is a **marker call** iff its callee operand
is the function itself (not a loaded or cast value) and that function's
name is exactly a marker name. Names are compared byte for byte; no
prefix, suffix or demangled match is made. A marker call is accepted iff
all of the following hold; otherwise `BD-E-MARKER-SIGNATURE`:

1. the declaration's function type is exactly the marker's IR signature,
   **or** is the unprototyped form `R (...)` with R the marker's return
   type (a C declaration without a prototype, spike case
   `c-unprototyped-decl`);
2. the call instruction's function type is exactly the marker's IR
   signature, **or**, only when the declaration is unprototyped, the
   marker's parameter list followed by `...`;
3. the call passes exactly as many arguments as the signature has
   parameters;
4. the calling convention is the default C convention and the call has
   no operand bundles.

Attributes and metadata are not part of the comparison; they are
governed by §3.6.

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

The same program passing an `int` index without a cast gives an `i32`
argument and is rejected:

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

### 3.6 The positive legality requirement and attributes

A marker is an external declaration that may read and write any memory,
may unwind and may not return: exactly an unknown external function to
LLVM. Stock passes then preserve the dynamic sequence of marker calls on
every executed path (spike findings §1: every standard pipeline of LLVM
18, 20 and 23, all 50 legal cases; the four negative controls are
detected). No attribute is needed and none may be added that licenses
elimination, commoning, speculation or motion.

The **permitted** attributes are exactly these; every other attribute
on a marker declaration or marker call site is `BD-E-MARKER-ATTRIBUTE`,
except where a row says otherwise:

| Position | Permitted |
|---|---|
| function (declaration or call site) | `nounwind`, `nonlazybind`, `uwtable` (any form), and every string attribute (`"key"` or `"key"="value"`) |
| return value | `noundef`, `nonnull`, `range(...)`, `zeroext`, `signext` |
| parameter | `noundef`, `nonnull`, `range(...)`, `zeroext`, `signext` |
| declaration linkage and keywords | external linkage (no `extern_weak`), `dso_local`, `dso_preemptable`, `unnamed_addr`, `local_unnamed_addr`, any visibility |
| call-site keywords | `tail`, `notail` (not `musttail`) |
| instruction metadata | any |

**Forbidden** (listed for the reader; implied by the permitted list) are
in particular: `memory(...)` in any form, `readnone`, `readonly`,
`writeonly`, `argmemonly`, `inaccessiblememonly`,
`inaccessiblemem_or_argmemonly`, `willreturn`, `speculatable`,
`noreturn`, `returned`, `nocapture`, `captures(...)`,
`dereferenceable(...)`, `dereferenceable_or_null(...)`, `align`,
`nofpclass(...)`, `byval`, `sret`, `writable`, `initializes(...)`,
`dead_on_unwind`, `musttail`, any non-default calling convention.
*(non-normative)* The first eight are the spike's L2 forbidden set;
`noreturn` would delete the code after a marker; `returned` would
replace a marker result by an argument; the parameter-effect attributes
would let LLVM move stores to an environment across a region call;
`dereferenceable` would let it speculate loads through a handle.

The permitted list is exactly the spike's L2 evidence (findings §1 and
§4, emission summary): front ends add `nounwind` (C++ `noexcept`, Rust
`extern "C"`), `nonlazybind`, `uwtable`, `noundef`, `nonnull`,
`zeroext` and string attributes (Rust, clang, Julia `llvmcall`); passes
add `local_unnamed_addr`, `nonnull`, `noundef`, `range` and `tail`; no
front end and no pass of any of the three majors adds anything else to
a marker. Extending the list requires corpus evidence and a version
change (§13). Attribute groups (`#N`) are resolved before the check.

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

### 3.7 Unwinding

Markers never unwind. Before any other analysis (§4.1 step S1) the
plugin rewrites every `invoke` of a marker into a `call` with the same
operands followed by `br label %normal`, removes the invoking block from
the phi nodes of the unwind destination, and then deletes every block
not reachable from the function's entry. *(non-normative)* This is
Enzyme's practice (enzyme survey §1.1); C++ with `-fexceptions` and
Rust `extern "C-unwind"` produce such invokes (emission summary item 3).
Front ends SHOULD declare markers non-unwinding (`noexcept`, Rust
`extern "C"`).

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

Unwinding through any other call in the device closure is not
supported in 0.1: after the rewrite, a device function (§4.2) that
contains `invoke`, `landingpad`, `resume`, `cleanuppad`, `catchpad`,
`catchswitch`, `cleanupret` or `catchret` is `BD-E-EH` (§14 D10).

### 3.8 Front-end emission routes

- **clang (C, C++)** and **rustc** emit markers as direct calls to the
  declaration (emission summary). Rust MUST declare each marker with one
  ABI per crate (`extern "C"`); mixed `"C"`/`"C-unwind"` declarations
  are merged by rustc into one declaration with `invoke` call sites,
  which §3.7 accepts.
- **Julia** MUST emit markers with `ccall("extern __bennett_<name>",
  llvmcall, …)` or with `Base.llvmcall((module_ir, "entry"), …)` whose
  module contains the `declare`. Both give a direct call to an
  attribute-free declaration; `ccall("extern __bennett_measure",
  llvmcall, Bool, …)` gives `declare i1 @__bennett_measure(ptr, i64)`,
  exactly the §3.2 signature (verified with Julia 1.13.3). A plain
  `ccall(:__bennett_x, …)` or `@ccall` is an indirect call through a
  `jlplt` GOT global and is not a marker call. The plugin MUST reject a
  module containing a global variable whose name matches
  `jlplt___bennett_<name>_<digits>_got` or that carries the attribute
  `"julia.fname"="__bennett_<name>"` (`BD-E-JULIA-CCALL`), so that this
  mistake fails at compile time instead of at a lazy binding at run
  time.
- **Region functions** are defined in the linked bitcode and passed as
  `ptr @f` (or any value that resolves under §6.2). A Julia
  `@cfunction` pointer is an `inttoptr` constant or a forwarding wrapper
  whose body lives in another module; it does not resolve (§6.2 rule C6)
  and is rejected.
- **Source effect lies** (spike F5). A device function definition
  carrying any of `memory(none)`, `memory(read)` (any `memory(...)`
  whose effects exclude a write to any location), `readnone`, `readonly`,
  `willreturn` or `speculatable`, from which a marker call is reachable
  through the call graph of §4.1 (the function itself included), is
  `BD-E-EFFECT-LIE`. *(non-normative)* LLVM cannot infer these
  attributes for a function that reaches an unknown external call, so
  they come from the source; the front end's own optimiser may already
  have deleted marker calls on their strength, which is why this is a
  diagnostic and not a guarantee (definedness assumption, north star
  §3.2).

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

## 4. Processing order, call graph and device closure

### 4.1 Processing order

A plugin processes the whole-program module, after the stock pipeline
(§11.1), in this order; the first failing rule gives the verdict (§1.6):

| Step | Rules |
|---|---|
| S1 | §3.1 reserved names; §3.5 recognition; §3.6 attributes; §3.8 Julia check; §3.7 invoke rewrite; §3.8 effect lies |
| S2 | §6.2 region candidate sets; §6.3 identity |
| S3 | §4.2 device closure; §3.7 exceptions |
| S4 | §5 handle provenance and containment |
| S5 | §6.4 static region well-formedness |
| S6 | §7.2 normalisation of the device closure; §7.5 validation |
| S7 | §3.4 integer candidate sets |
| S8 | §9 lifting of every oracle region; §6.4 in-place verification |
| S9 | lowering to ISA objects (plugin-defined, constrained by §8.7) |

Within a step, rules apply in the order listed; within a rule, to
instructions in module text order.

The **call graph** has an edge F → G when F contains a direct `call` or
`invoke` of G (after resolving aliases), and an edge F → R for every
candidate R of every region operand of a marker call in F. Only
functions with a definition are nodes. A function's **closure** is the
set of functions reachable from it by direct-call edges only.

### 4.2 Device closure

The **device closure** is the least set of defined functions that
contains every function containing a marker call, every region
candidate, and every function directly called from a member. Its
members are **device functions**; every other defined function is a
**host function**. A **device entry** is a device function that is
called directly by a host function or that has non-local linkage
(neither `internal` nor `private`). *(non-normative)* Device functions
run on the device's classical-control tier (ISA §3.1) or below it;
host functions are the classical tier, native and untouched; a call
from host code to a device entry is a launch (ISA §10), and memory the
two sides share is bridged by the driver (§14 D25).

A host function that takes the address of a device function other than
a device entry (an instruction operand that is the function and not
the callee of a direct call) is `BD-E-DEVICE-ADDRESS`.

```llvm example=device-address verdict=reject:BD-E-DEVICE-ADDRESS
define internal void @rg(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  ret void
}

define void @top() {
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  call void @__bennett_adj(ptr @rg, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}

define ptr @host() {
  ret ptr @rg
}
```

### 4.3 Calls out of the device closure

A device function may call a function without a definition (an
external function that is not a marker, a primitive, or one of the
memory intrinsics `llvm.memcpy`, `llvm.memmove`, `llvm.memset`). Its
meaning depends on where the call is:

- inside the closure of an oracle region or of a reversible region, the
  normaliser replaces it by a fault (rule N18, fault code 8,
  `FAULT_EFFECT_UNMODELLED`), and the coverage report lists it as
  `trapped`;
- elsewhere, it is a call to host code with native semantics (ISA §10
  `hostcall` is the mechanism; the marshalling is the driver's, §14
  D11), listed as `shimmed`.

## 5. Handles

### 5.1 Representation

A handle is an ordinary `ptr` in address space 0. Its bits are
unspecified, distinct from every other live handle and from every
address of the classical memory model (§7.4), and MUST NOT influence any
result; the rules below make them unobservable. Host code never sees a
handle (§5.4). A handle denotes a register of `n` wires, n the `qalloc`
operand; wire `i` of handle `h` is written `h.i`.

### 5.2 Provenance

Provenance is a flow-insensitive, context-insensitive, whole-module
analysis over device functions, computed as the least fixpoint of the
rules below. Every SSA value v has a provenance `prov(v)`: a set of
roots, kept **per lane** for vector values and **per index path** for
aggregate values. Memory provenance is kept per **slot** `(X, o)`: X an
abstract object, o a byte offset or `*` (unknown offset within X).

**Abstract objects**: each `alloca` instruction; each global variable;
each call of a heap allocation function from the list `malloc`,
`calloc`, `aligned_alloc`, `_Znwm`, `_Znam`, `__rust_alloc`,
`__rust_alloc_zeroed` (§14 D9); and the pseudo-object `EXT` (memory of
unknown callers).

**Bases.** Every `ptr` value p has a base `base(p)`, a set of pairs
`(X, o)` or ⊤:

| Rule | p | base(p) |
|---|---|---|
| B1 | an `alloca`, a global variable, a heap allocation call | `{(p, 0)}` |
| B2 | `getelementptr T, ptr q, idx…` | for each `(X, o)` in base(q): `(X, o + Δ)` when every index is a constant (Δ the constant byte offset under the datalayout, as `GEPOperator::accumulateConstantOffset`), else `(X, *)`; `* + Δ = *` |
| B3 | `phi`, `select` (value operands) | the union |
| B4 | a `ptr` parameter of function F | the union of base(a) over the corresponding argument `a` of every direct call of F, plus base(env) of every region-entry marker call that has F as a candidate (for parameter 0); plus `{(EXT, *)}` if F has non-local linkage or F's address is used other than as a direct callee or as a region-operand source |
| B5 | anything else (loads, call results, `inttoptr`, null, constant expressions other than a global) | ⊤ |

**Propagation** (the permitted uses of a handle-derived value; each
copies bits):

| Rule | Instruction | Effect |
|---|---|---|
| P1 | `%h = call ptr @__bennett_qalloc(...)` or `qborrow` | `prov(%h) ⊇ {%h's call instruction}` |
| P2 | `ptrtoint ptr v to iW` with W = pw | result gets prov(v) |
| P3 | `inttoptr iW v to ptr` with W = pw | result gets prov(v) |
| P4 | `phi`, `select` (as a value operand), `freeze` | result gets the union |
| P5 | `insertelement`, `extractelement`, `shufflevector` with constant lane indices; `insertvalue`, `extractvalue` | provenance moves with the lane or index path |
| P6 | `store v, ptr p` | for every `(X, o)` in base(p) and every lane/field k of v at byte offset d_k: `slot(X, o + d_k) ⊇ prov(v_k)` |
| P7 | `load T, ptr p`, T ∈ {`ptr`, `iW` with W = pw, vectors of these} | lane k gets the union of every `slot(X, o')` with `(X, o)` in base(p) and o' = o + k·(pw/8), where `(X, *)` on either side matches every offset of X |
| P8 | `llvm.memcpy` / `llvm.memmove` (dst, src, len) | for every handle-derived slot `(X, s)` of a src object: if src and dst offsets and len are constants and `[s, s + pw/8)` lies in the copied range, `slot(Y, d + (s − o_src)) ⊇` it; else `slot(Y, *) ⊇` it; for every `(Y, d)` in base(dst) |
| P9 | direct call of a defined device function G | prov(parameter i of G) ⊇ prov(argument i); prov(result) ⊇ prov of every `ret` operand of G |
| P10 | a handle operand of a marker call (§3.2) | the use the analysis exists for |

**Rejected uses** (each `BD-E-HANDLE-USE` unless named otherwise). A
handle-derived value (any lane or field) MUST NOT be:

1. an operand of any instruction or intrinsic not listed in P2–P10:
   in particular arithmetic, bitwise operations, `icmp` (even against
   null, §14 D8), any cast other than P2/P3 (so `trunc`, `zext`, `bitcast`, `ptrtoint` to a width ≠
   pw), `getelementptr` (as base or index), `switch`;
2. the pointer operand of a `load`, `store`, `atomicrmw`, `cmpxchg` or
   memory intrinsic (dereference);
3. an argument of a call to a function without a definition other than
   a marker, or of an indirect call;
4. moved by `insertelement` or `extractelement` with a non-constant
   lane index;
5. stored (P6) or copied (P8) through a pointer whose base is ⊤
   (`BD-E-HANDLE-STORE`) or contains EXT (`BD-E-HANDLE-ESCAPE`);
6. returned by a function with non-local linkage or whose address is
   used other than as a direct callee (`BD-E-HANDLE-ESCAPE`).

In addition (rule 7, `BD-E-HANDLE-ESCAPE`), an abstract object with a
handle-derived slot MUST NOT have its address used other than as the
pointer operand of a load, a store or a memory intrinsic, a
`getelementptr` base, a `phi` or `select` operand, an argument of a
direct call of a defined device function, or the env operand of a
region-entry marker; in particular it is never stored, converted by
`ptrtoint`, returned or passed to a function without a definition. So
every pointer into such an object has a tracked base, and every load
that can read handle bits is a P7 load.

A load (any type) whose byte range overlaps a handle-derived slot
without being exactly one P7 lane is a partial use (rule 1). Every
handle operand of a marker call MUST be handle-derived
(`BD-E-HANDLE-UNTRACKED`).

*(non-normative)* Soundness: a handle can reach a marker only through
the listed copies, and its bits are never interpreted. A load through
a ⊤ base yields an untracked value, which no marker accepts; a value
that is tracked but at run time is not a live handle (a stale copy, a
value from an unknown caller) traps at the marker (§8.3, `T-DEAD`).

The spike F1 shape (8-byte `memcpy` of a handle turned into `ptrtoint`,
`store i64`, `load i64`, `inttoptr`):

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
  call void @__bennett_adj(ptr @rg, ptr %e)
  %l = load i64, ptr %e
  %h2 = inttoptr i64 %l to ptr
  call void @__bennett_qfree(ptr %h2)
  ret void
}
```

The same program before `instcombine`, with the `memcpy` the source
wrote (N13 makes it a `memmove`; P8 copies the slot):

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
  call void @__bennett_adj(ptr @rg, ptr %e)
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

```llvm example=handle-null-check verdict=reject:BD-E-HANDLE-USE
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

```llvm example=handle-to-external verdict=reject:BD-E-HANDLE-USE
declare void @log_handle(ptr)

define void @top() {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  call void @log_handle(ptr %h)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=handle-store-unknown verdict=reject:BD-E-HANDLE-STORE
@slotp = internal global ptr null

define void @top() {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %p = load ptr, ptr @slotp
  store ptr %h, ptr %p
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

A handle that reaches a marker by no tracked path is rejected even
though at run time it might be live:

```llvm example=handle-untracked verdict=reject:BD-E-HANDLE-UNTRACKED
define void @kick(ptr %h) {
  call void @__bennett_gate(i32 2, ptr %h, i64 0)
  ret void
}
```

```llvm example=handle-escape-param verdict=reject:BD-E-HANDLE-ESCAPE
define void @put(ptr %out) {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %out
  ret void
}
```

```llvm example=handle-object-escape verdict=reject:BD-E-HANDLE-ESCAPE
@pp = internal global ptr null

define void @top() {
  %slot = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %slot
  store ptr %slot, ptr @pp
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

Aggregates carry provenance per field (Rust passes pairs this way):

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

```llvm example=handle-escape-return verdict=reject:BD-E-HANDLE-ESCAPE
define ptr @mk() {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  ret ptr %h
}
```

Vector lanes (spike F1, `load-store-vectorizer`): lane 1 carries the
handle, lane 0 an ordinary integer on which arithmetic is legal:

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

### 5.3 Handle tables

A **handle table** is an abstract object with handle-derived slots that
is indexed with a non-constant offset; rule B2 gives such an access the
offset `*`, and rule P7 makes a load from it carry every root stored
into the object. The index is a classical value of the device's
classical-control tier: no oracle region may contain a handle-derived
value (§6.4), so a handle never flows through memory at a superposed
address. *(non-normative)* With `*`, an integer of pointer width stored
in the same object as a variable-indexed handle array becomes
handle-derived when loaded; keep such integers in a separate object.

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

### 5.4 Containment

No handle reaches host code: rules 5, 6 and 7 of §5.2 forbid a handle
in memory or return values that unknown callers can read, and §4.2
makes every function that receives one a device function. In addition,
a store of a handle-derived value into a global variable that any host
function references is `BD-E-HANDLE-ESCAPE`. *(non-normative)*
The spike's L3 (guard-page faults, `BADHANDLE`) is the dynamic
counterpart and stays in the corpus (§10).

### 5.5 Copy, XOR and in-place rules

The dialect has no copy of a handle that copies qubits: copying a
handle copies a reference (§5.2). Quantum data moves only by:

- `qload(dst, mem, addr)`: XOR of cell `addr` of `mem` into `dst`
  (§8.3); a copy when `dst` is clean, the source preserved;
- `qstore(mem, addr, val)`: XOR of `val` into cell `addr` of `mem`
  (ISA `qstore`), whatever `mem` holds. The north star's compile-time
  rule "a store into a register not known to be clean is an error" is
  **not** a dialect rule in 0.1 (§1.4): at register granularity it
  would forbid the second store that uncomputes the first, which is the
  only way to clean a stored cell; front ends that want overwrite
  semantics enforce a clean target themselves (§14 D7);
- `inplace(g, ginv, budget, x)`: x ← g(x), admitted only under §6.4;
- `oracle(f, budget, x, tgt, fault)`: `tgt` ⊕= payload, `fault` ⊕=
  code, `x` preserved (ISA §5.2).

A store followed by the same store is the identity on `mem`, so the
register is released clean:

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

### 5.6 Handle → wire obligations

The plugin converts handles to ISA wires (ISA §3.3 linear values) after
lowering. Its obligations, each a property of every ISA object it emits
(ISA suite F), are: every gate's wires pairwise distinct; no wire used
after its release; every `qalloc`ed bundle released by an explicit
`qfree` (ISA §5.1); every control context disjoint from the operands it
controls (ISA §3.3); the uncomputation-validity discipline of ISA §6
for every value it introduces. Where an obligation depends on run-time
data, the reference semantics checks it dynamically and the plugin MUST
include the same check (§8.3 traps `T-ALIAS`, `T-DEAD`, `T-LEAK`,
`T-CTRL`); `T-CLEAN` is checked as ISA `qreg.free` cleanliness is: by
simulating executors, with hardware following ISA §17 item 14.

## 6. Regions

### 6.1 Region-entry markers and region kinds

| Marker | Region operand(s) | Region kind | Required type of every candidate | ISA counterpart |
|---|---|---|---|---|
| `ctrl(q, qi, f, budget, env)` | `f` | action | `void (ptr)` | `ctl w action_call` (ISA §4.7, §5.3) |
| `adj(f, env)` | `f` | action | `void (ptr)` | `adj action_call` (ISA §5.3) |
| `compute(f, use, env)` | `f`, `use` | action | `void (ptr)` | `action_call`; `action_call`; `adj action_call` |
| `reversible(f, budget, env)` | `f` | reversible | `void (ptr)` | a call of an R-tier function (ISA §3.1, §7.4) |
| `oracle(f, budget, x, tgt, fault)` | `f` | oracle | `iT (iN)`, 1 ≤ N, T ≤ 128 | `oracle_call @ref tk (x) tgt fault () ()` (ISA §4.7, §5.2) |
| `inplace(g, ginv, budget, x)` | `g`, `ginv` | oracle | `iN (iN)`, 1 ≤ N ≤ 128 | `qinplace @g @ginv tk x` (ISA §4.5) |

A candidate whose type differs is `BD-E-REGION-TYPE`. The region kind is
fixed by the marker, never inferred from the body (§1.4). The two
region interfaces of north star §4.2 are kept apart by name: an
**oracle region** is a lifted classical oracle with output target and
fault register (ISA §5.2); an **action region** is a quantum action on
the wires its events name (ISA §5.3), with no fault outcome of its own
(a fault of an oracle it calls lands in that oracle's fault register,
which the action names among its wires).

### 6.2 Candidate sets and dispatch

The candidate set `RR(v)` of a region operand v is a set of defined
functions or ⊤ (unbounded), computed as the least fixpoint of:

| Rule | v | RR(v) |
|---|---|---|
| C1 | a function `@F`, or an alias whose aliasee chain ends at `@F` | `{resolve(F)}` |
| C2 | `select` (value operands), `phi` | the union |
| C3 | `load ptr, ptr p` | for each `(X, o)` in base(p) (§5.2): if X is a global declared `constant`, the functions at offset o of its initialiser (every pointer element when o is `*`); if X is an `alloca` or a global not declared `constant`, the functions at offset o of its initialiser (globals only) together with RR(w) for every `store ptr w, ptr q` whose base contains `(X, o')` with o' = o or either offset `*`; ⊤ if base(p) is ⊤, if X is EXT or a heap object, if X is written by a memory intrinsic, or if X's address is used other than as the pointer operand of a load or store, a `getelementptr` base, a `phi`/`select` operand or an argument of a direct call to a defined device function |
| C4 | a `ptr` parameter of function F | the union of RR(a) over the corresponding argument of every direct call of F; ⊤ if F has non-local linkage or its address is used other than as a direct callee or a region-operand source |
| C5 | the result of a direct call of a defined function G | the union of RR over G's `ret` operands |
| C6 | anything else (`inttoptr`, `null`, a call of a function without a definition, a load through ⊤) | ⊤ |

`resolve(F)` follows **forwarding thunks**: F is a forwarding thunk of
G iff F's body is one block holding exactly a call of G (optionally
`tail`/`musttail`/`notail`, default calling convention, no operand
bundles) whose arguments are F's parameters in order and whose function
type equals F's, followed by `ret void` or `ret` of that call's result;
then `resolve(F) = resolve(G)`. A cycle of thunks is `BD-E-REGION-THUNK`.

Requirements: RR(v) ≠ ⊤ (`BD-E-REGION-UNBOUNDED`); every member is a
function with a definition (`BD-E-REGION-EXTERNAL`); every member has
the type of §6.1 (`BD-E-REGION-TYPE`).

**Dispatch.** The region operand is classical data. At run time its
value is compared with the address of every function or alias whose
address reaches it under C1–C5 (the **source set**); on equality with
source F the region `resolve(F)` is entered. *(non-normative)* Because
every source resolves into the candidate set, the plugin compiles a
body for each candidate and the device's classical-control tier
selects one; this is maintainer decision 3. A value equal to no source
cannot arise from an accepted module; the reference semantics traps
(`T-REGION`) if it does. *(non-normative)* Rule C4 rejects a region
pointer that unknown callers can supply, while rule B4 of §5.2 only
adds `EXT` for handles: a region needs a bounded set at compile time to
be compiled at all, whereas a stale or foreign handle value is caught at
run time (`T-DEAD`).

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
  call void @__bennett_adj(ptr %f, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

The SimplifyCFG switch-to-lookup shape (`region-switch-fnptr-table`
after `default<O3>`):

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
  call void @__bennett_adj(ptr %f, ptr %e)
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
  call void @__bennett_adj(ptr %f, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

Merged twins resolve to one region (spike F2; `mergefunc` makes `@k2`
a forwarding thunk, `-mergefunc-use-aliases` makes an alias):

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
  call void @__bennett_adj(ptr %f, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

A region pointer from host input (a parameter of an externally visible
function), a Julia `@cfunction` constant and an external declaration are
rejected:

```llvm example=region-host-param verdict=reject:BD-E-REGION-UNBOUNDED
define void @top(ptr %f) {
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  call void @__bennett_adj(ptr %f, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=region-inttoptr verdict=reject:BD-E-REGION-UNBOUNDED
define void @top() {
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  call void @__bennett_adj(ptr inttoptr (i64 127079231243584 to ptr), ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=region-external verdict=reject:BD-E-REGION-EXTERNAL
declare void @elsewhere(ptr)

define void @top() {
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  call void @__bennett_adj(ptr @elsewhere, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=region-wrong-type verdict=reject:BD-E-REGION-TYPE
define internal i8 @inc(i8 %x) {
  %r = add i8 %x, 1
  ret i8 %r
}

define void @top() {
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  call void @__bennett_adj(ptr @inc, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

### 6.3 Region identity

A region is identified by its content, never by its symbol (maintainer
decision 1). Candidates that resolve (§6.2) to the same function are one
region. The semantic identity of an **oracle region** is the hash of its
reference body (§9.5), which uses the fixed symbol name `ref`, so two
functions with equal materialised bodies have equal identity whatever
their names. Symbol names, linkage, aliases and thunks are
non-normative: diagnostics and coverage entries MAY print them.

The **region key** of any region (used only in certificates, coverage
entries and diagnostics; no semantics depends on it in 0.1) is the
SHA-256 of the text printed by the LLVM printer of the major in use for
a module that contains the materialised region function and its
closure, after `strip` (local names), with the functions renamed `f0,
f1, …` in depth-first preorder from the region along direct calls in
instruction order, and without datalayout, triple and module metadata
(§14 D13).

### 6.4 Static well-formedness (step S5) and in-place verification (step S8)

1. **Action regions are unitary.** No function in the closure of an
   action region contains a `measure` call (`BD-E-REGION-MEASURE`) or a
   `reversible` call (`BD-E-REGION-TIER`). *(non-normative)* The
   north-star option of deferring measurement inside a unitary region is
   §14 D5 (default: refused). Clean release of the region's own
   allocations is checked dynamically (§8.4, `T-LEAK`, `T-CLEAN`).
2. **Reversible regions are classical.** No function in the closure of
   a reversible region contains a marker call (`BD-E-REVERSIBLE-MARKER`)
   (§14 D11).
3. **Oracle regions are liftable** (step S8): every candidate is in the
   lifted subset of §9.1 (`BD-E-LIFT-SUBSET`); in particular it contains
   no marker call and no handle.
4. **In-place pairs are verified** (step S8). For every `inplace` call,
   every g candidate, every ginv candidate and every member B of the
   budget's candidate set (`0xFFFFFFFFFFFFFFFF` standing for the
   driver's `B_default`, known at compile time), with N the width: when N ≤ 16 the plugin MUST
   run the reference interpreter (ISA §14.1) on the reference bodies and
   check that for every x in [0, 2^N), F_B^g(x) = (y, 0) and
   F_B^ginv(y) = (x, 0) (`BD-E-INPLACE-NOT-INVERSE` otherwise).
   *(non-normative)* On a finite set, ginv∘g = id makes g injective,
   hence a bijection, so g∘ginv = id and ginv is fault-free on every
   input as ISA `qinplace` requires. When N > 16 the plugin MUST hold
   an ISA `inverse_pair_library` claim (ISA §12.1) for the pair's
   reference-body hashes at B, else `BD-E-INPLACE-UNVERIFIED` (§14 D14).
   A fallible computation is therefore never in-place: an input on
   which g faults fails the check.

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
  call void @__bennett_ctrl(ptr %c, i64 0, ptr @body, i64 -1, ptr %e)
  call void @__bennett_qfree(ptr %t)
  call void @__bennett_qfree(ptr %c)
  ret void
}
```

```llvm example=region-reversible-in-action verdict=reject:BD-E-REGION-TIER
define internal void @classical(ptr %e) {
  ret void
}

define internal void @body(ptr %e) {
  call void @__bennett_reversible(ptr @classical, i64 -1, ptr %e)
  ret void
}

define void @top() {
  %e = alloca ptr
  call void @__bennett_adj(ptr @body, ptr %e)
  ret void
}
```

```llvm example=region-reversible-marker verdict=reject:BD-E-REVERSIBLE-MARKER
define internal void @body(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  ret void
}

define void @top() {
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  call void @__bennett_reversible(ptr @body, i64 -1, ptr %e)
  call void @__bennett_qfree(ptr %h)
  ret void
}
```

```llvm example=device-exceptions verdict=reject:BD-E-EH
declare i32 @__gxx_personality_v0(...)
declare void @may_throw()

define void @top() personality ptr @__gxx_personality_v0 {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  invoke void @may_throw()
          to label %ok unwind label %lp

ok:
  call void @__bennett_qfree(ptr %h)
  ret void

lp:
  %e = landingpad { ptr, i32 } cleanup
  call void @__bennett_qfree(ptr %h)
  resume { ptr, i32 } %e
}
```

### 6.5 Budgets

- **Oracle and in-place regions.** The `budget` operand is the step
  budget B. The budget unit is one row of the ISA reference interpreter
  on the reference body (§9.6, ISA §5.2, §14.1), so the fault set is a
  property of the program, B, the LLVM version and pipeline, and the
  normaliser and mapping versions, never of the plugin's lowering. The
  ISA budget is (B, 0, 0, 0): reference bodies are memoryless (ISA §7.2,
  §5.4). The value `0xFFFFFFFFFFFFFFFF` selects the driver's default
  `B_default` (§11.3; default 1048576). B MUST have a finite constant
  candidate set (§3.4): ISA 0.8 has no classical-control instruction
  that builds a budget token from a run-time value, so the driver
  creates one token per (region, B) with `bennett_budget` (ISA §10) at
  launch (§15 ISA-1).
- **Exhaustion.** An oracle input that needs more than B rows yields
  F_B(x) = (0, `FAULT_BUDGET_STEPS`) (ISA §5.2): a fault outcome on that
  input, never a compile error and never a truncated result. An
  in-place pair whose B is insufficient for some input fails §6.4 item 4
  at compile time, since an in-place update has no fault outcome.
- **`ctrl` and `reversible`.** Their `budget` operands have no effect
  in 0.1 (§1.4, §14 D17, D18); producers SHOULD pass
  `0xFFFFFFFFFFFFFFFF`.
- **Out-of-band budgets.** Per-region budget tables are deferred (§14
  D2); the only out-of-band budget in 0.1 is `B_default`.

### 6.6 Outlining conventions

- Regions are functions on arrival: the front end outlines (a Julia
  macro, a clang attribute, a Rust closure trampoline); the dialect
  imposes no source syntax. The plugin never outlines source code; any
  outlining it performs while lowering is not observable.
- Action and reversible regions have type `void (ptr env)`. `env` points
  to classical memory the front end owns (an `alloca` or heap object)
  that is live for the duration of the marker call; the region reads and
  writes it as classical memory (§8.4). Handles reach a region through
  `env` (§5.2 rule B4 binds a region's parameter to the marker's env).
- Oracle regions are classical functions `iT f(iN x)`: x is the basis
  value of the input register (bit i is wire i), the result is the
  payload XORed into the target (bit j into wire j); several logical
  inputs are packed into the one register (§14 D21).
- A region body MUST be referenced by the region operand (directly or
  through §6.2); a body referenced only from a side-table global is not
  a region (enzyme survey implication 5).
- Region functions SHOULD have internal linkage, so that they are not
  device entries. C++ lambdas pass their static `__invoke` thunk and
  Rust closures an `extern "C"` trampoline; both are ordinary region
  functions whose closure contains the closure body.

## 7. Materialised normalisation (norm 0.1)

### 7.1 Scope, order and naming

The normaliser rewrites every device function (§4.2) and the
initialisers of every global a device function references; host
functions are untouched. It applies the rules of §7.2 in table order,
each to the whole module before the next. A rule that introduces a
value names it `%nz.<tag>.<r>`, where `<r>` is the name of the
instruction being rewritten without its `%` (a number for an unnamed
value, giving for example `%nz.c.5`). A rule that needs a declaration
not already in the module appends it at the end of the module, in
order of first use. The result is the **materialised module**: the
reference semantics (§8) and the native comparison build (§7.6) are
both defined on it.

**Fault replacement F(C)**: the instruction is replaced by `call void
@__bennett_nz_fault(i64 C)` followed by `unreachable`; the instructions
after it in its block are deleted, and the block is removed from the
incoming lists of the phi nodes of its former successors.
`__bennett_nz_fault` is declared `declare void @__bennett_nz_fault(i64)`;
`bennett-runtimes` defines it for the native comparison build (record C,
end the device entry with fault C); the reference semantics gives it
fault code C (§7.4).

### 7.2 The rules

Every source of poison, undef and nondeterminism the normaliser removes,
and its stated replacement:

| Id | Source | Replacement |
|---|---|---|
| N1 | instruction flags `nsw`, `nuw`, `exact`, `inbounds`, `nusw`, `nneg`, `disjoint`, `samesign`, `inrange` (and `inrange(...)`) | removed: wrapping, inexact, out-of-bounds address arithmetic and the unflagged operation are defined |
| N2 | fast-math flags `nnan`, `ninf`, `nsz`, `arcp`, `contract`, `afn`, `reassoc`, `fast` | removed |
| N3 | instruction metadata other than `!dbg` (`!range`, `!nonnull`, `!noundef`, `!align`, `!dereferenceable`, `!dereferenceable_or_null`, `!tbaa`, `!tbaa.struct`, `!alias.scope`, `!noalias`, `!invariant.load`, `!invariant.group`, `!llvm.loop` (it carries `llvm.loop.mustprogress`), `!nontemporal`, `!prof`, …) | removed |
| N4 | attributes on device function definitions, their parameters and returns, and on every call site in a device function: `noundef`, `nonnull`, `range(...)`, `align` (except together with `byval`, `byref`, `sret`, `inalloca`, `preallocated`), `dereferenceable(...)`, `dereferenceable_or_null(...)`, `nofpclass(...)`, `noalias`, `nocapture`, `captures(...)`, parameter `readnone`/`readonly`/`writeonly`, `returned`, `writable`, `dead_on_unwind`, `initializes(...)`, `allocalign`, `allocptr`; function attributes `memory(...)`, `readnone`, `readonly`, `writeonly`, `argmemonly`, `inaccessiblememonly`, `inaccessiblemem_or_argmemonly`, `willreturn`, `mustprogress`, `nosync`, `nofree`, `norecurse`, `speculatable` | removed (attribute groups are rewritten; a group shared with a host function is first duplicated) |
| N5 | calls of `llvm.assume` | deleted |
| N6 | calls of `llvm.lifetime.start`, `llvm.lifetime.end`, `llvm.invariant.start`, `llvm.invariant.end` | deleted (an `alloca` is live for its whole function activation, §7.4) |
| N7 | `undef` and `poison` constants: whole operands, vector lanes, aggregate elements, `shufflevector` mask elements, global initialisers | the zero of the type: `0`, `+0.0`, `null`, `zeroinitializer` for a wholly undefined vector or aggregate; mask element `0` |
| N8 | `%x = freeze T v` | deleted; every use of `%x` replaced by v |
| N9 | `atomic` and `volatile` on loads and stores; `fence`; `atomicrmw`; `cmpxchg` | plain load/store; fence deleted; `atomicrmw op ptr p, T v` → `%nz.l.r = load T, ptr p`, `%nz.v.r = <op> T %nz.l.r, v` (for `xchg`: v; `min`/`max`/`umin`/`umax`: `icmp` + `select` named `%nz.k.r`, `%nz.v.r`), `store T %nz.v.r, ptr p`, uses of `%r` → `%nz.l.r`; `cmpxchg ptr p, T c, T n` → `%nz.l.r = load`, `%nz.e.r = icmp eq T %nz.l.r, c`, `%nz.s.r = select i1 %nz.e.r, T n, T %nz.l.r`, `store T %nz.s.r, ptr p`, `%nz.a.r = insertvalue { T, i1 } zeroinitializer, T %nz.l.r, 0`, `%r = insertvalue { T, i1 } %nz.a.r, i1 %nz.e.r, 1` (single-thread assumption, recorded in the certificate, §14 D24) |
| N10 | `llvm.is.constant.*` | `false` |
| N10 | `llvm.objectsize.*(p, min, nullunknown, dynamic)` | `-1` (all ones) if `min` is `false`, else `0`: the "unknown" answer, as LLVM's own lowering gives |
| N11 | calls of `llvm.trap`, `llvm.debugtrap`, `llvm.ubsantrap` | F(4) |
| N12 | `llvm.abs.*(x, i1 true)`, `llvm.ctlz.*(x, i1 true)`, `llvm.cttz.*(x, i1 true)` | the flag becomes `i1 false` (abs of the minimum is the minimum; ctlz/cttz of 0 is the width) |
| N13 | `llvm.memcpy.*`, `llvm.memcpy.inline.*` | `llvm.memmove.*` with the same operands (overlap is defined) |
| N14 | `%r = shl/lshr/ashr iW a, b` with b not a constant | `%nz.c.r = icmp uge iW b, W`; `%nz.s.r = <op> iW a, b`; `%r = select i1 %nz.c.r, iW 0, iW %nz.s.r` (every shift by ≥ W gives 0, as the ISA's shifts do, ISA §4.1); for a vector type `<L x iW>` the same three instructions with the `icmp` constant the vector whose L lanes are all W and the `select` constant `zeroinitializer` |
| N14 | the same with b a constant ≥ W | every use of `%r` replaced by `0`; deleted |
| N15 | `extractelement`/`insertelement` with a non-constant index i on L lanes | `%nz.c.r = icmp uge iK i, L`; `%nz.e.r = <the original instruction>`; `%r = select i1 %nz.c.r, T Z, T %nz.e.r` with Z = the zero element (extract) or the unchanged vector operand (insert) |
| N16 | `%r = call T @llvm.fmuladd.*(a, b, c)` | `%nz.m.r = fmul T a, b`; `%r = fadd T %nz.m.r, c` (no fusion; explicit `llvm.fma` keeps fusion through §7.3) |
| N17 | an instruction with an operand or result of type `half`, `bfloat`, `x86_fp80`, `fp128`, `ppc_fp128` or a vector of them; a call of a floating-point intrinsic absent from §7.3 (e.g. `llvm.sin`, `llvm.exp`, `llvm.pow`); a floating-point operation on a vector type | F(8) (§14 D16) |
| N18 | in the closure of an oracle or reversible region, a call of a function without a definition other than a primitive or a memory intrinsic (§4.3) | F(8) |
| N19 | floating-point arithmetic, comparison and conversion | the soft-float rewrite of §7.3 |
| N20 | `%a = alloca T[, iK n]` | followed immediately by `call void @llvm.memset.p0.i64(ptr %a, i8 0, i64 S, i1 false)` with S = the allocation size of T (`DataLayout::getTypeAllocSize`) times n, when n is a constant (or absent, n = 1); otherwise preceded by `%nz.n.a = zext iK n to i64` (omitted when K = 64) and `%nz.z.a = mul i64 %nz.n.a, <alloc size of T>`, the memset taking `%nz.z.a` |

*(non-normative)* Division by zero and `sdiv`/`srem` of INT_MIN by −1
are not rewritten: they are faults of the reference semantics (§7.4),
the ISA's `lift.div` and CC division fault on them directly (ISA §4.1,
§4.2), and the native comparison build traps (§7.6).

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

```llvm normalise-out=n-undef
define internal i64 @u(i64 %a, i1 %c) {
  %s = select i1 %c, i64 %a, i64 0
  %v = insertelement <2 x i64> zeroinitializer, i64 %a, i32 0
  %w = extractelement <2 x i64> %v, i32 1
  %r = add i64 0, %s
  %t = add i64 %r, %w
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

```llvm normalise-in=n-alloca
define internal i64 @a() {
  %b = alloca [3 x i64], align 8
  %p = getelementptr [3 x i64], ptr %b, i64 0, i64 1
  %v = load i64, ptr %p, align 8
  ret i64 %v
}
```

```llvm normalise-out=n-alloca
define internal i64 @a() {
  %b = alloca [3 x i64], align 8
  call void @llvm.memset.p0.i64(ptr %b, i8 0, i64 24, i1 false)
  %p = getelementptr [3 x i64], ptr %b, i64 0, i64 1
  %v = load i64, ptr %p, align 8
  ret i64 %v
}

declare void @llvm.memset.p0.i64(ptr, i8, i64, i1 immarg)
```

### 7.3 Soft-float rewrite (rule N19)

Floating point never executes in hardware in either build. With B = 64
for `double` (suffix `f64`, carrier `i64`) and B = 32 for `float`
(suffix `f32`, carrier `i32`), the rewrite of an instruction `%r` is:
first, for each floating-point operand k (value or constant, in operand
order), `%nz.<k>.r = bitcast <T> <operand> to iB`; then the call below,
named `%nz.i.r`; then, for a floating-point result, `%r = bitcast iB
%nz.i.r to <T>`. The entry points are defined by `bennett-arith` and
are part of its bitcode the driver links.

| Instruction | Call (carrier operands in order) | Result |
|---|---|---|
| `fadd`, `fsub`, `fmul`, `fdiv`, `frem` | `iB @__bennett_sf_{add,sub,mul,div,rem}_fB(iB, iB)` | bitcast |
| `fcmp <p>` | `i1 @__bennett_sf_cmp_fB(iB, iB, i32 P)`, P the LLVM predicate number: `false` 0, `oeq` 1, `ogt` 2, `oge` 3, `olt` 4, `ole` 5, `one` 6, `ord` 7, `ueq` 8, `ugt` 9, `uge` 10, `ult` 11, `ule` 12, `une` 13, `uno` 14, `true` 15 | `%r` is the call itself |
| `fptosi`/`fptoui` to iM | `i128 @__bennett_sf_{fptosi,fptoui}_fB(iB, i32 M)` | `%r = trunc i128 %nz.i.r to iM` (the call is `%r` when M = 128) |
| `sitofp`/`uitofp` from iM | `%nz.x.r = sext`/`zext iM a to i128` (omitted when M = 128), `iB @__bennett_sf_{sitofp,uitofp}_fB(i128)` | bitcast |
| `fpext float to double` | `i64 @__bennett_sf_fpext_f32_f64(i32)` | bitcast |
| `fptrunc double to float` | `i32 @__bennett_sf_fptrunc_f64_f32(i64)` | bitcast |
| `llvm.sqrt`, `llvm.floor`, `llvm.ceil`, `llvm.trunc`, `llvm.round`, `llvm.roundeven`, `llvm.rint`, `llvm.nearbyint` | `iB @__bennett_sf_<name>_fB(iB)` | bitcast |
| `llvm.minnum`, `llvm.maxnum`, `llvm.minimum`, `llvm.maximum` | `iB @__bennett_sf_<name>_fB(iB, iB)` | bitcast |
| `llvm.fma` | `iB @__bennett_sf_fma_fB(iB, iB, iB)` | bitcast |
| `fneg`, `llvm.fabs`, `llvm.copysign`, `bitcast`, `load`, `store`, `select`, `phi` | unchanged: bit-exact operations (LangRef) | – |

**Semantics of the entry points** (the contract with `bennett-arith`):
IEEE 754-2019 binary64/binary32, round to nearest ties to even,
subnormals supported, no observable flags or exceptions; **every NaN
result is the canonical NaN** (`0x7FF8000000000000`, `0x7FC00000`);
`rem` is C `fmod` (exact, the sign of the dividend); `cmp` is LLVM's
`fcmp` for the predicate; `fptosi`/`fptoui` truncate toward zero, map
NaN to 0 and saturate values outside the range of iM to its bounds,
returned sign-extended (`fptosi`) or zero-extended (`fptoui`) in i128;
`sitofp`/`uitofp` round to nearest even; `minnum`/`maxnum` are IEEE
754-2008 minNum/maxNum (one NaN operand: the other operand; two: the
canonical NaN) with −0 < +0; `minimum`/`maximum` are IEEE 754-2019
(either NaN: the canonical NaN) with −0 < +0; `sqrt`, `fma` and every
rounding function are correctly rounded (`round` ties away from zero,
`rint` and `nearbyint` to nearest even); `fpext` is exact; `fptrunc`
rounds to nearest even. *(non-normative)* `fneg`, `fabs` and `copysign`
stay bit-exact, so a NaN's sign bit set by `fneg` survives, as LangRef
requires.

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

### 7.4 Memory model and fault outcomes of device classical code

- **Live allocations**: an `alloca` from its execution to the return of
  its function; a global, always; a heap allocation of the
  `bennett-runtimes` allocator, from its allocation to its `free`
  (`free` of a null pointer does nothing). The null region is never
  allocated.
- **Zero fill**: allocas (N20); heap allocations (the allocator returns
  zero-filled memory in both builds); globals hold their initialisers.
  Region inputs are not zero-filled: they are the bytes the host
  supplies.
- **Bounds**: a load, store or memory-intrinsic range is valid iff all
  its bytes lie in one live allocation (an address model: the object a
  pointer was derived from is irrelevant).
- **Addresses**: the native comparison build's link map and the
  allocator's fixed base (north star §3.2); executions in which a
  native stack address influences a result are *layout-dependent*
  (§14 D12, D15).
- **Single thread**: atomics and volatile are sequentialised (N9).

The fault outcomes (immediate undefined behaviour the reference machine
encounters, and the dialect's run-time checks):

| Event | Fault code (ISA §5.4) |
|---|---|
| `udiv`, `urem`, `sdiv`, `srem` with divisor 0 | 5 `FAULT_UB_DIV0` |
| `sdiv`, `srem` of the minimum value by −1 | 6 `FAULT_UB_SDIV_OVERFLOW` |
| an access outside every live allocation; `free` of a non-null pointer that is not the base of a live heap allocation | 7 `FAULT_UB_MEMFAULT` |
| `unreachable` reached; N11 | 4 `FAULT_UB_TRAP` |
| `__bennett_nz_fault(C)` | C |
| oracle budget exhausted | 1 `FAULT_BUDGET_STEPS` (§6.5) |
| a run-time check of §8.3 fails | 4 `FAULT_UB_TRAP` |

In an oracle region a fault is the F_B outcome (ISA §5.2). In any other
device code the run ends `FAILED` with that fault record (ISA §10); for
a reversible region the record is an R-tier fault record (ISA §7.4).
(§15 ISA-7, ISA-8.)

### 7.5 The residual-poison validator

The validator inspects the materialised device closure and rejects
(`BD-E-RESIDUAL`) any of:

| Id | Residue |
|---|---|
| V1 | a flag of N1 or N2 |
| V2 | instruction metadata other than `!dbg` |
| V3 | an attribute N4 removes, on a device function, its parameters or return, or a call site in a device function |
| V4 | a call of `llvm.assume`, `llvm.lifetime.*`, `llvm.invariant.*`, `llvm.is.constant.*`, `llvm.objectsize.*`, `llvm.trap`, `llvm.debugtrap`, `llvm.ubsantrap`, `llvm.memcpy.*`, `llvm.fmuladd.*`; `llvm.abs`/`ctlz`/`cttz` with a `true` flag |
| V5 | an `undef` or `poison` constant in a device function or in the initialiser of a global a device function references |
| V6 | `freeze`, `fence`, `atomicrmw`, `cmpxchg`, an atomic or volatile load or store |
| V7 | a shift whose amount is not a constant < W, unless the shift's only use is as the false operand of a `select` whose true operand is 0 and whose condition is `icmp uge` of the same amount and the constant W |
| V8 | `extractelement`/`insertelement` with a non-constant index outside the N15 pattern |
| V9 | `fadd`, `fsub`, `fmul`, `fdiv`, `frem`, `fcmp`, `fptosi`, `fptoui`, `sitofp`, `uitofp`, `fpext`, `fptrunc`, or a call of a floating-point intrinsic other than `llvm.fabs` and `llvm.copysign` |
| V10 | an operand or result of type `half`, `bfloat`, `x86_fp80`, `fp128`, `ppc_fp128` |
| V11 | an `alloca` not followed by its N20 memset |
| V12 | in the closure of an oracle or reversible region, a call of a function without a definition other than a primitive or a memory intrinsic |

The plugin's validator and `bennett-conformance`'s are implemented
independently (north star §3.2); a disagreement on any input is a
conformance failure of one of them.

```llvm example=residual-nsw verdict=reject:BD-E-RESIDUAL mode=validate
define internal i32 @f(i32 %a) {
  %s = add nsw i32 %a, 1
  ret i32 %s
}
```

```llvm example=residual-clean verdict=accept mode=validate
define internal i32 @f(i32 %a) {
  %s = add i32 %a, 1
  ret i32 %s
}
```

### 7.6 Reference baseline and the native comparison build

Differential testing (north star §5.1) compares the artefact with the
**native comparison binary**: the materialised device closure,
code-generated by the same LLVM major and linked with
`bennett-runtimes` and `bennett-arith` (never host libc or libm) under
the comparison link of §7.4. It is never an `-O0` build: optimisation
legally changes marker operands (spike F4: `fmuladd` fusion, NaN
folding, `llvm.is.constant`, `llvm.objectsize`), and the normalised
optimised module is the one program both builds implement. The driver
MUST make division by zero and INT_MIN/−1 trap in the native build: on
targets whose divide instruction does not trap it inserts, after
materialisation and outside the materialised module, a check that
calls `__bennett_nz_fault` with code 5 or 6. *(non-normative)* The
spike's L1 compared against `llc -O0` of the raw case; its F4 cells are
by design and are not dialect violations once normalisation runs.

## 8. Reference semantics

### 8.1 State

The reference semantics runs host functions natively and every call of
a device entry on the materialised module (§7) over a state Σ = (C, Q,
H, G):

- **C**, the classical state: LLVM's semantics of the materialised
  module (LangRef), with every remaining choice fixed by §7 and the
  fault outcomes of §7.4;
- **Q**, the quantum state of the ISA formal model (ISA §14.2): a unit
  vector over the live wires, in allocation order;
- **H**, the handle table: for each handle value, its wires, whether it
  is live, and the generation (below) it was allocated in, if any;
- **G**, a stack of **recorders**, one per active generation (§8.4).

Measurement makes the semantics a tree: every outcome sequence has its
Born probability (ISA §14.2) and its own continuation.

### 8.2 Events

A marker call produces **events**: ISA-level operations, each with a
**control set** (a set of wires, initially empty). The event forms are
`qalloc H n`, `qfree H`, the gates `x h s sdg t tdg cx cz swap ccx`
(ISA §4.4) and `rx θ`, `ry θ`, `rz θ` on wires, `qload D M A`, `qstore
M A V`, `oracle R B X T F` and `inplace G G' B X`. When no recorder is
active, an event is **applied** to Σ at once; otherwise it is appended
to the innermost recorder. Applying an event with control set S applies
it only on the basis states where every wire of S is 1 (ISA `ctl`, ISA
§4.7, §5.3); `qalloc` and `qfree` are unconditional (ISA §3.5).

**Adjoint** of an event list (ISA §5.3 adjoint table): reverse the
list and replace each event: `x h cx cz swap ccx qload qstore oracle`
are self-adjoint; `s` ↔ `sdg`; `t` ↔ `tdg`; `rx θ` ↦ `rx −θ` (and `ry`,
`rz`); `qalloc` ↔ `qfree` of the same wires; `inplace G G' B X` ↦
`inplace G' G B X`. Control sets are unchanged.

### 8.3 Marker rules

Wire `h.i` is wire i of handle h; `n(h)` its width. A wire is
**named** by an event when it is one of the event's operand wires (not
merely a member of its control set). The conditions are checked when
the marker is called, against H, and H is updated then (so a register
allocated during a generation is live for the rest of that generation);
Q changes only when an event is applied. A failed condition is a
run-time trap: the run ends with fault code 4 (§7.4) and the named
diagnostic (§12).

| Marker | Conditions (trap) | Effect |
|---|---|---|
| `qalloc(cls, n)` | – | a new live handle h of n wires; event `qalloc h n`, whose application appends the n wires to Q in state 0; h belongs to the innermost active generation, if any |
| `qborrow(cls, n)` | a recorder is active (`T-BORROW`) | as `qalloc` (§14 D6: borrowing is clean allocation in 0.1) |
| `qfree(h)` | h live (`T-DEAD`); if a recorder is active, h belongs to it (`T-FOREIGN`); when applied, Q is the product of the all-zero state on h's wires and a state of the other wires (`T-CLEAN`) | event `qfree h`; when applied, the wires leave Q and h is dead |
| `gate(op, h, i)` | h live (`T-DEAD`); i < n(h) (`T-INDEX`) | the realisation of §3.4 on `h.i` (Z and Y expand to their gate sequences) |
| `gate2(op, a, i, b, j)` | as above for both; `a.i` ≠ `b.j` (`T-ALIAS`) | `cx a.i b.j`, `cz a.i b.j` or `swap a.i b.j` |
| `gate3(op, a, i, b, j, c, k)` | as above; the three wires distinct (`T-ALIAS`) | `ccx a.i b.j c.k` |
| `rot(op, h, i, θ)` | as `gate`; θ finite (`T-THETA`) | `rx θ`, `ry θ` or `rz θ` on `h.i` |
| `measure(h, i)` | as `gate`; no recorder active (`T-MEASURE`) | projective measurement of `h.i` in the computational basis (ISA §14.2); outcome m with its Born probability; the wire stays live in state m; returns m as `i1` |
| `qload(dst, mem, addr)` | the three handles live and distinct (`T-DEAD`, `T-ALIAS`); n(mem) = 2^n(addr) · n(dst) (`T-SIZE`) | event `qload`: for every cell c in [0, 2^n(addr)), on the basis states where the wires of addr hold c (wire k = bit k), `dst.b ⊕= mem.(c·W + b)` for b < W = n(dst) (ISA §4.6 cell order) |
| `qstore(mem, addr, val)` | as `qload` with W = n(val) | event `qstore`: `mem.(c·W + b) ⊕= val.b` under addr = c |
| `ctrl(q, qi, f, budget, env)` | q live, qi < n(q); after generation, the wire `q.qi` is named by no event of E (`T-CTRL`) | E = gen(f, env) (§8.4); each event of E with `q.qi` added to its control set |
| `adj(f, env)` | – | E = gen(f, env); the adjoint of E |
| `compute(f, use, env)` | – | E_f = gen(f, env), then E_u = gen(use, env); the events E_f, E_u, adjoint(E_f) |
| `reversible(f, budget, env)` | no recorder active (`T-TIER`) | §8.6 |
| `oracle(f, budget, x, tgt, fault)` | handles live and distinct; n(x) = N, n(tgt) = T, n(fault) = 4 for the dispatched region `iT (iN)` (`T-SIZE`) | event `oracle ref B x tgt fault`: on every basis state, tgt ⊕= payload(F_B(x)) and fault ⊕= code(F_B(x)) (ISA §5.2), F_B from the reference body of §9 with budget (B, 0, 0, 0) |
| `inplace(g, ginv, budget, x)` | x live; n(x) = N for the dispatched pair (`T-SIZE`) | event `inplace`: x ← g(x), the permutation that §6.4 verified (ISA `qinplace`) |

A region operand whose value matches no source of its candidate set
traps (`T-REGION`, §6.2). A `budget` equal to `0xFFFFFFFFFFFFFFFF`
denotes `B_default` (§6.5).

### 8.4 Generation of action regions

`gen(R, env)` pushes a recorder, calls `R(env)` under the classical
semantics of §8.1 (its classical code runs once, with ordinary classical
effects; every marker call it makes produces events per §8.3, nested
`ctrl`, `adj` and `compute` producing their events into this recorder),
pops the recorder and returns its event list E. **Leak rule**
(`T-LEAK`): for `ctrl` and `adj`, every register allocated during the
generation is freed during it; for `compute`, every register allocated
during gen(use) is freed during it, while a register allocated during
gen(f) and not freed during it is freed by adjoint(E_f), in which its
`qalloc` event becomes a `qfree` event (the compute–use–uncompute
pattern), so gen(use) MUST NOT free it (`T-FOREIGN`). *(non-normative)*

- The classical part of an action region runs once per invocation,
  whatever the quantum context: it is neither controlled nor inverted.
  A `compute` generates `f` once and uncomputes by the adjoint of that
  recording; the spike trace runtime, which calls `f` twice, is a test
  harness convention, not the semantics.
- E is a finite list of ISA operations; its controlled form is the list
  of controlled events because controlled-(UV) = controlled-U ·
  controlled-V and allocation is unconditional with clean release; a
  plugin may compile E statically when it does not depend on run-time
  data, and otherwise lowers the generation to classical-control code
  that issues the events (§8.7). The ISA counterpart of one invocation
  is the quantum action whose body is E (ISA §5.3).
- North star §4.2 requires "allocations inside released clean or
  borrowed and restored": `T-LEAK` and `T-CLEAN` are those checks.

### 8.5 Device entries

When a device entry returns, every register allocated during that call
and still live is a leak (`T-LEAK`): no handle survives into host code
(§5.4), so such a register is unreachable.

### 8.6 Reversible regions

`reversible(f, budget, env)` runs `f(env)` on the R tier (ISA §3.1):
its classical effects on memory are those of §8.1; the run history
(ISA §7.4) is retained so that the whole run is reversible (ISA §10
reverse eligibility). Its closure has no marker call (§6.4) and no call
without a definition (N18), so it has no external effect in 0.1 (device
models, ISA §7.3, are deferred: §14 D11). A fault ends the run (§7.4).

### 8.7 Conformance

A plugin and an executor (ISA §1.2) together conform iff, for every
module the rules accept, every host input and every sequence of
measurement outcomes: the probability of that sequence, every classical
value the host observes (return values of device entries, memory they
write), every fault code, and every trap, equal those of the reference
semantics; and the quantum state at every measurement and at every
device-entry return equals the reference state, exactly when the program
uses permutation gates only, and otherwise within the error bound its
certificate states (ISA §12.3, operator norm composed along the
sequence). A program that reaches `T-CLEAN` in the reference semantics
is erroneous; an executor that cannot test cleanliness (hardware) need
not reproduce that trap (ISA §17 item 14). Where the reference
semantics is layout-dependent (§7.4) the comparison is with the
reference interpreter, not with native execution (north star §5.1).

### 8.8 Worked examples (trace-checked)

The following programs are also legality cases in the corpus. The
checker builds each with the spike trace runtime
(`corpus/legality/runtime/`), whose `ctrl` and `adj` call the region
once and whose `compute` calls `f`, `use`, `f`; it converts the trace
into events by §8.3–§8.4 (for `compute` it keeps the first `f`
recording and checks that the third equals it) and simulates them. Wire
`Hk.i` is wire i of the k-th allocated handle; basis states list wires
in allocation order, leftmost first; the state is given before event
`at` (0-based).

**Control.** A `ctrl` on a control in superposition entangles; a second
`ctrl` disentangles:

```llvm semantics=sem-ctrl corpus=spec-sem-ctrl
; CASE: spec-sem-ctrl
; HAZARD: dialect 0.1 reference-semantics example (spec section 8.8): ctrl of an action region that flips a target read from an environment, on a control in superposition, twice
; INPUTS: 0..3
; EXPECT: legal
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64, i64)
declare void @__bennett_qfree(ptr)
declare void @__bennett_gate(i32, ptr, i64)
declare void @__bennett_ctrl(ptr, i64, ptr, i64, ptr)

define void @flip(ptr %e) {
  %t = load ptr, ptr %e
  call void @__bennett_gate(i32 1, ptr %t, i64 0)
  ret void
}

define i64 @case_entry(i64 %x) {
  %e = alloca ptr
  %c = call ptr @__bennett_qalloc(i64 0, i64 1)
  %t = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %t, ptr %e
  call void @__bennett_gate(i32 2, ptr %c, i64 0)
  call void @__bennett_ctrl(ptr %c, i64 0, ptr @flip, i64 -1, ptr %e)
  call void @__bennett_ctrl(ptr %c, i64 0, ptr @flip, i64 -1, ptr %e)
  call void @__bennett_gate(i32 2, ptr %c, i64 0)
  call void @__bennett_qfree(ptr %t)
  call void @__bennett_qfree(ptr %c)
  ret i64 %x
}
```

```text events=sem-ctrl input=0
qalloc H0 1
qalloc H1 1
h H0.0
x H1.0 ctrl H0.0
x H1.0 ctrl H0.0
h H0.0
qfree H1
qfree H0
```

```text state=sem-ctrl input=0 at=4
|00> 0.70710678
|11> 0.70710678
```

**Adjoint.** `adj` replays the recording reversed and inverted:

```llvm semantics=sem-adj corpus=spec-sem-adj
; CASE: spec-sem-adj
; HAZARD: dialect 0.1 reference-semantics example (spec section 8.8): a direct call of a region body applies h s t; adj of the same body applies tdg sdg h and returns the register to 0
; INPUTS: 0..3
; EXPECT: legal
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64, i64)
declare void @__bennett_qfree(ptr)
declare void @__bennett_gate(i32, ptr, i64)
declare void @__bennett_adj(ptr, ptr)

define void @phase(ptr %e) {
  %q = load ptr, ptr %e
  call void @__bennett_gate(i32 2, ptr %q, i64 0)
  call void @__bennett_gate(i32 3, ptr %q, i64 0)
  call void @__bennett_gate(i32 5, ptr %q, i64 0)
  ret void
}

define i64 @case_entry(i64 %x) {
  %e = alloca ptr
  %q = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %q, ptr %e
  call void @phase(ptr %e)
  call void @__bennett_adj(ptr @phase, ptr %e)
  call void @__bennett_qfree(ptr %q)
  ret i64 %x
}
```

```text events=sem-adj input=0
qalloc H0 1
h H0.0
s H0.0
t H0.0
tdg H0.0
sdg H0.0
h H0.0
qfree H0
```

```text state=sem-adj input=0 at=4
|0> 0.70710678
|1> -0.5+0.5i
```

**Compute–use–uncompute.** Phase kickback through an ancilla that the
uncompute returns clean:

```llvm semantics=sem-compute corpus=spec-sem-compute
; CASE: spec-sem-compute
; HAZARD: dialect 0.1 reference-semantics example (spec section 8.8): compute(f, use) with f = cx onto an ancilla and use = z on the ancilla; phase kickback leaves the ancilla clean
; INPUTS: 0..3
; EXPECT: legal
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64, i64)
declare void @__bennett_qfree(ptr)
declare void @__bennett_gate(i32, ptr, i64)
declare void @__bennett_gate2(i32, ptr, i64, ptr, i64)
declare void @__bennett_compute(ptr, ptr, ptr)

define void @copy(ptr %e) {
  %a = load ptr, ptr %e
  %pb = getelementptr i8, ptr %e, i64 8
  %b = load ptr, ptr %pb
  call void @__bennett_gate2(i32 1, ptr %a, i64 0, ptr %b, i64 0)
  ret void
}

define void @kick(ptr %e) {
  %pb = getelementptr i8, ptr %e, i64 8
  %b = load ptr, ptr %pb
  call void @__bennett_gate(i32 7, ptr %b, i64 0)
  ret void
}

define i64 @case_entry(i64 %x) {
  %e = alloca [2 x ptr]
  %a = call ptr @__bennett_qalloc(i64 0, i64 1)
  %b = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %a, ptr %e
  %pb = getelementptr i8, ptr %e, i64 8
  store ptr %b, ptr %pb
  call void @__bennett_gate(i32 2, ptr %a, i64 0)
  call void @__bennett_compute(ptr @copy, ptr @kick, ptr %e)
  call void @__bennett_gate(i32 2, ptr %a, i64 0)
  call void @__bennett_gate(i32 1, ptr %a, i64 0)
  call void @__bennett_qfree(ptr %b)
  call void @__bennett_qfree(ptr %a)
  ret i64 %x
}
```

```text events=sem-compute input=0
qalloc H0 1
qalloc H1 1
h H0.0
cx H0.0 H1.0
s H1.0
s H1.0
cx H0.0 H1.0
h H0.0
x H0.0
qfree H1
qfree H0
```

```text state=sem-compute input=0 at=8
|10> 1
```

## 9. The lifting map (map 0.1)

The lifting map turns a materialised oracle region into its reference
body: the ISA oracle whose reference-interpreter run (ISA §14.1)
defines F_B and the budget unit (ISA §4.2 "Reference body and
binding"). It is a function of the materialised function alone, so two
plugins on the same LLVM version and pipeline produce byte-identical
reference bodies. Its version (`map 0.1`) is the certificate's
`dialect_mapping_version` (ISA §12.3).

### 9.1 The lifted subset

A function is **liftable** iff, after normalisation:

1. its type is `iT (iN)` with 1 ≤ N, T ≤ 128 (for `inplace`, T = N);
2. every value has an integer type iK with 1 ≤ K ≤ 128;
3. every instruction is one of `add sub mul and or xor shl lshr ashr
   udiv sdiv urem srem icmp select zext sext trunc phi br switch ret
   unreachable`, a call of `llvm.umin`, `llvm.umax`, `llvm.smin`,
   `llvm.smax` or `llvm.abs` (with flag `false`), or `call void
   @__bennett_nz_fault(i64 C)` immediately followed by `unreachable`.

Otherwise the region is `BD-E-LIFT-SUBSET` (§14 D4: memory, calls,
floating point and vectors in oracle regions are deferred). *(non-
normative)* The subset is demo rung 1 of north star §8 (scalar
functions); after `default<O3>` most scalar functions are already
call-free and memory-free.

### 9.2 Names

| LLVM entity | ISA name |
|---|---|
| the parameter | pseudo-location `p0` (interface input, role `in`) |
| the output target, the fault register | `tgt`, `fault` |
| the k-th instruction that produces a value (0-based, in layout order, phis included) | location `v<k>` |
| the j-th constant materialisation, in emission order | location `c<j>` |
| the j-th mapping temporary, in emission order | location `t<j>` |
| the i-th basic block (0-based, layout order) | block `^b<i>` |
| the j-th compare-chain block of a `switch` in block i | block `^b<i>.s<j>` (j ≥ 1) |
| the edge block from block i to block s | block `^b<i>.e<s>` |

### 9.3 Rows

Rows of an instruction are emitted in instruction order within its
block. Before the rows of an instruction, each of its **constant
operands** that is a value operand (in operand order; not an immediate
flag such as the `i1` of `llvm.abs`) is materialised by `c<j> =
lift.const.iW <value>`, W its width and the value printed as an
unsigned decimal; the operand then reads `c<j>`. A non-constant operand
reads the location of its value (`p0` for the parameter). `A`, `B`, `C`
below are the operands so read; `v` is the instruction's location.

| LLVM | Rows |
|---|---|
| `add sub mul and or xor shl lshr ashr` | `v = lift.<op> A B` |
| `udiv sdiv urem srem` | `v = lift.<op> A B` |
| `icmp eq/ne/ult/ule/slt/sle a, b` | `v = lift.icmp.<pred> A B` |
| `icmp ugt/uge/sgt/sge a, b` | `v = lift.icmp.{ult,ule,slt,sle} B A` (operands swapped) |
| `select c, a, b` | `v = lift.select C A B` |
| `zext/sext/trunc a to iM` | `v = lift.<op>.iM A` |
| `llvm.umin(a, b)` | `t = lift.icmp.ult A B`; `v = lift.select t A B` |
| `llvm.umax(a, b)` | `t = lift.icmp.ult B A`; `v = lift.select t A B` |
| `llvm.smin(a, b)` | `t = lift.icmp.slt A B`; `v = lift.select t A B` |
| `llvm.smax(a, b)` | `t = lift.icmp.slt B A`; `v = lift.select t A B` |
| `llvm.abs(a, false)` | `c = lift.const.iW 0`; `t1 = lift.icmp.slt A c`; `t2 = lift.sub c A`; `v = lift.select t1 t2 A` |
| `phi` | none at its position (edge moves) |
| `ret a` | `lift.retval A` |
| `unreachable` | `fault 4` |
| `call void @__bennett_nz_fault(i64 C)`; `unreachable` | `fault C` (one row for the pair) |
| `br label %S` | edge moves (B → S); `qjump ^S` |
| `br i1 c, label %T, label %F`, T ≠ F | `qbranch C ^T' ^F'` |
| `br i1 c, label %S, label %S` | as `br label %S` |
| `switch` | the compare chain below |

**Edge moves** (B → S), S with phis φ_1 … φ_r in S's order and incoming
values a_1 … a_r for B: the constant materialisations of the a_k that
are constants (in order), then `(v_φ1, …, v_φr) = lift.parmov (A_1, …,
A_r)` (ISA §4.2, parallel). None when S has no phi. For a successor X
of a conditional terminator in block i, X' is `^b<i>.e<x>` when X has a
phi, else `^b<x>`; the **edge block** `^b<i>.e<x>` holds the edge moves
(i → x) and `qjump ^b<x>`.

**Compare chain.** `switch iW c, label %D [iW k_1, label %L_1 … iW
k_m, label %L_m]` in block i: with m = 0, as `br label %D`; otherwise,
for case j = 1 … m: `c = lift.const.iW k_j`; `t = lift.icmp.eq C c`;
`qbranch t ^L_j' ^next_j`, where `next_j` is `^b<i>.s<j>` for j < m
and `^D'` for j = m. The rows of case 1 end block `^b<i>`; the rows of
case j ≥ 2 form block `^b<i>.s<j−1>`. A constant condition is
materialised once, before case 1.

**Block order.** For i = 0, 1, …: block `^b<i>`, then its chain blocks
`^b<i>.s1 …` in order, then its edge blocks in ascending successor
index.

### 9.4 Header and locations

The reference body is the ISA function text (ISA §16.2):

```
oracle @ref (p0:wire[N] in) (tgt:wire[T]) (fault:wire[4]) () ()
regs { <every location, in order of first appearance as a destination, as name:reg[W], separated by ", "> }
^b0():
<rows>
...
```

The `regs` line is omitted when there is no location. Widths: `v<k>`
has its value's width (`i1` gives `reg[1]`); `c<j>` its constant's;
`t<j>` is `reg[1]` for a compare and W for `lift.sub`. Every block line
is `^<name>():`. Text is canonical per ISA §16.1.

### 9.5 Reference-body hash

The reference body's identity is its ISA interface hash as the only
symbol of an object with header `bennett-object isa=0.8 … ptr_width=pw`
and no `layout` section: an acyclic one-member symbol, so the hash is
the SHA-256 of its semantic envelope (ISA §9.2; this is how the ISA
§16.3 test vectors `inc8` and `zero` are computed). Its signature is
`{"abi":"0.8","args":[],"fault":4,"in":[N],"kind":"oracle","mem":[],"tgt":T,"tier":"q"}`.
The hash is the certificate's `reference_program_hash` (ISA §12.3) and
the oracle region's identity (§6.3).

### 9.6 F_B and the budget unit

F_B(x) is ISA §5.2's on the reference body with budget (B, 0, 0, 0):
each executed row is one step; success at `lift.retval` within B
steps gives (f(x), 0); a fault row or a faulting `lift.div` gives (0,
code); otherwise (0, 1). Stated results below are lines `B=<b>
x=<lo>..<hi> -> payload=<expr> code=<expr>` (expressions in x), or
`steps=<expr>` giving the exact number of rows on success.

**Example: `inc8`.** The dialect form of ISA §16.3 example 1:

```llvm lift=inc8
define internal i8 @inc8(i8 %x) {
b0:
  %r = add i8 %x, 1
  ret i8 %r
}
```

```isa reference-body=inc8
oracle @ref (p0:wire[8] in) (tgt:wire[8]) (fault:wire[4]) () ()
regs { c0:reg[8], v0:reg[8] }
^b0():
c0 = lift.const.i8 1
v0 = lift.add p0 c0
lift.retval v0
```

```text hash=inc8 ptr_width=64
d7576a3304e4df500e5ac5a07238401b28a72b1475ec577504e203e50937b035
```

```text fb=inc8
B=3 x=0..255 -> payload=(x+1)%256 code=0
B=2 x=0..255 -> payload=0 code=1
steps=3
```

*(non-normative)* Up to the location names and the symbol name, this
is ISA example `inc8`, with the same F_B at B = 3 and B = 2.

**Example: a loop.** Phis become parallel moves; the step count is
7 + 9x:

```llvm lift=countdown
define internal i8 @countdown(i8 %x) {
b0:
  br label %b1

b1:
  %i = phi i8 [ %x, %b0 ], [ %i2, %b2 ]
  %acc = phi i8 [ 0, %b0 ], [ %acc2, %b2 ]
  %z = icmp eq i8 %i, 0
  br i1 %z, label %b3, label %b2

b2:
  %i2 = sub i8 %i, 1
  %acc2 = add i8 %acc, 3
  br label %b1

b3:
  ret i8 %acc
}
```

```isa reference-body=countdown
oracle @ref (p0:wire[8] in) (tgt:wire[8]) (fault:wire[4]) () ()
regs { c0:reg[8], v0:reg[8], v1:reg[8], c1:reg[8], v2:reg[1], c2:reg[8], v3:reg[8], c3:reg[8], v4:reg[8] }
^b0():
c0 = lift.const.i8 0
(v0, v1) = lift.parmov (p0, c0)
qjump ^b1
^b1():
c1 = lift.const.i8 0
v2 = lift.icmp.eq v0 c1
qbranch v2 ^b3 ^b2
^b2():
c2 = lift.const.i8 1
v3 = lift.sub v0 c2
c3 = lift.const.i8 3
v4 = lift.add v1 c3
(v0, v1) = lift.parmov (v3, v4)
qjump ^b1
^b3():
lift.retval v1
```

```text hash=countdown ptr_width=64
48b12bccedc56557b3364da9b37546afb9e94202fdd0b66ac8659e9ee91a843a
```

```text fb=countdown
B=7+9*x x=0..255 -> payload=(3*x)%256 code=0
B=6+9*x x=0..255 -> payload=0 code=1
steps=7+9*x
```

**Example: a division fault.**

```llvm lift=div
define internal i8 @div(i8 %x) {
b0:
  %q = udiv i8 100, %x
  ret i8 %q
}
```

```isa reference-body=div
oracle @ref (p0:wire[8] in) (tgt:wire[8]) (fault:wire[4]) () ()
regs { c0:reg[8], v0:reg[8] }
^b0():
c0 = lift.const.i8 100
v0 = lift.udiv c0 p0
lift.retval v0
```

```text hash=div ptr_width=64
cd9cad2ac5a43c7c564432e0c4d71674487adb8cdd97beef2c526ddbd753218d
```

```text fb=div
B=3 x=1..255 -> payload=100//x code=0
B=3 x=0..0 -> payload=0 code=5
```

**Example: a switch with a phi successor.**

```llvm lift=switch
define internal i8 @sw(i8 %x) {
b0:
  switch i8 %x, label %b3 [
    i8 1, label %b1
    i8 2, label %b2
  ]

b1:
  br label %b3

b2:
  br label %b3

b3:
  %r = phi i8 [ 7, %b0 ], [ 10, %b1 ], [ 20, %b2 ]
  ret i8 %r
}
```

```isa reference-body=switch
oracle @ref (p0:wire[8] in) (tgt:wire[8]) (fault:wire[4]) () ()
regs { c0:reg[8], t0:reg[1], c1:reg[8], t1:reg[1], c2:reg[8], v0:reg[8], c3:reg[8], c4:reg[8] }
^b0():
c0 = lift.const.i8 1
t0 = lift.icmp.eq p0 c0
qbranch t0 ^b1 ^b0.s1
^b0.s1():
c1 = lift.const.i8 2
t1 = lift.icmp.eq p0 c1
qbranch t1 ^b2 ^b0.e3
^b0.e3():
c2 = lift.const.i8 7
(v0) = lift.parmov (c2)
qjump ^b3
^b1():
c3 = lift.const.i8 10
(v0) = lift.parmov (c3)
qjump ^b3
^b2():
c4 = lift.const.i8 20
(v0) = lift.parmov (c4)
qjump ^b3
^b3():
lift.retval v0
```

```text hash=switch ptr_width=64
89345d4e3b3fc814cc40a167ca17b6e8365f393922a63dd9dbf9f8cb31612013
```

```text fb=switch
B=10 x=0..255 -> payload=10 if x==1 else (20 if x==2 else 7) code=0
B=7 x=1..1 -> payload=10 code=0
B=7 x=2..255 -> payload=0 code=1
B=7 x=0..0 -> payload=0 code=1
steps=7 if x==1 else 10
```

**Example: an intrinsic.**

```llvm lift=umin
define internal i8 @mn(i8 %x) {
b0:
  %r = call i8 @llvm.umin.i8(i8 %x, i8 9)
  ret i8 %r
}

declare i8 @llvm.umin.i8(i8, i8)
```

```isa reference-body=umin
oracle @ref (p0:wire[8] in) (tgt:wire[8]) (fault:wire[4]) () ()
regs { c0:reg[8], t0:reg[1], v0:reg[8] }
^b0():
c0 = lift.const.i8 9
t0 = lift.icmp.ult p0 c0
v0 = lift.select t0 p0 c0
lift.retval v0
```

```text hash=umin ptr_width=64
ab979131e6abf1a384afb65d00b7c53ef6f362dc48c1504a43e462ee179baaa4
```

```text fb=umin
B=4 x=0..255 -> payload=min(x,9) code=0
steps=4
```

**Example: outside the subset.**

```llvm lift=load verdict=reject:BD-E-LIFT-SUBSET
@k = internal constant i8 5

define internal i8 @ld(i8 %x) {
b0:
  %v = load i8, ptr @k
  %r = add i8 %x, %v
  ret i8 %r
}
```

**Example: oracle and in-place calls in a module.** The oracle is
applied twice, which XORs the payload in and out again (an involution,
ISA §5.2), so every register is released clean:

```llvm example=oracle-call verdict=accept candidates=inc8
define internal i8 @inc8(i8 %x) {
  %r = add i8 %x, 1
  ret i8 %r
}

define void @top() {
  %x = call ptr @__bennett_qalloc(i64 0, i64 8)
  %t = call ptr @__bennett_qalloc(i64 0, i64 8)
  %f = call ptr @__bennett_qalloc(i64 0, i64 4)
  call void @__bennett_oracle(ptr @inc8, i64 3, ptr %x, ptr %t, ptr %f)
  call void @__bennett_oracle(ptr @inc8, i64 3, ptr %x, ptr %t, ptr %f)
  call void @__bennett_qfree(ptr %f)
  call void @__bennett_qfree(ptr %t)
  call void @__bennett_qfree(ptr %x)
  ret void
}
```

```llvm example=oracle-budget-host verdict=reject:BD-E-OPERAND-UNBOUNDED
define internal i8 @inc8(i8 %x) {
  %r = add i8 %x, 1
  ret i8 %r
}

define void @top(i64 %b) {
  %x = call ptr @__bennett_qalloc(i64 0, i64 8)
  %t = call ptr @__bennett_qalloc(i64 0, i64 8)
  %f = call ptr @__bennett_qalloc(i64 0, i64 4)
  call void @__bennett_oracle(ptr @inc8, i64 %b, ptr %x, ptr %t, ptr %f)
  call void @__bennett_qfree(ptr %f)
  call void @__bennett_qfree(ptr %t)
  call void @__bennett_qfree(ptr %x)
  ret void
}
```

```llvm example=oracle-not-liftable verdict=reject:BD-E-LIFT-SUBSET
@k = internal constant i8 5

define internal i8 @ld(i8 %x) {
  %v = load i8, ptr @k
  %r = add i8 %x, %v
  ret i8 %r
}

define void @top() {
  %x = call ptr @__bennett_qalloc(i64 0, i64 8)
  %t = call ptr @__bennett_qalloc(i64 0, i64 8)
  %f = call ptr @__bennett_qalloc(i64 0, i64 4)
  call void @__bennett_oracle(ptr @ld, i64 4, ptr %x, ptr %t, ptr %f)
  call void @__bennett_oracle(ptr @ld, i64 4, ptr %x, ptr %t, ptr %f)
  call void @__bennett_qfree(ptr %f)
  call void @__bennett_qfree(ptr %t)
  call void @__bennett_qfree(ptr %x)
  ret void
}
```

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
  %x = call ptr @__bennett_qalloc(i64 0, i64 8)
  call void @__bennett_inplace(ptr @add5, ptr @sub5, i64 3, ptr %x)
  call void @__bennett_inplace(ptr @sub5, ptr @add5, i64 3, ptr %x)
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
  %x = call ptr @__bennett_qalloc(i64 0, i64 8)
  call void @__bennett_inplace(ptr @add5, ptr @add5, i64 3, ptr %x)
  call void @__bennett_qfree(ptr %x)
  ret void
}
```

**Example: in-place verification** (§6.4 item 4). `x ← x + 5` with its
inverse `x ← x + 251` is admitted; `x ← 2x` has no inverse:

```llvm lift=add5
define internal i8 @add5(i8 %x) {
b0:
  %r = add i8 %x, 5
  ret i8 %r
}
```

```llvm lift=sub5
define internal i8 @sub5(i8 %x) {
b0:
  %r = add i8 %x, 251
  ret i8 %r
}
```

```llvm lift=dbl
define internal i8 @dbl(i8 %x) {
b0:
  %r = shl i8 %x, 1
  ret i8 %r
}
```

```llvm lift=half
define internal i8 @half(i8 %x) {
b0:
  %r = lshr i8 %x, 1
  ret i8 %r
}
```

```text inplace=add5 g=add5 ginv=sub5 B=3 verdict=accept
```

```text inplace=dbl g=dbl ginv=half B=3 verdict=reject:BD-E-INPLACE-NOT-INVERSE
```

```text inplace=short g=add5 ginv=sub5 B=2 verdict=reject:BD-E-INPLACE-NOT-INVERSE
```

## 10. The legality corpus and the conformance suites (corpus 0.1)

### 10.1 The corpus

`corpus/legality/` holds the cases (`cases/`, 56 spike cases plus the
`spec-*` cases of this document), four negative controls
(`controls/`), the harness (`harness/run.py`), the trace runtime
(`runtime/`) and the spike's results. Spike cases use the provisional
ABI v0 and arbitrary operation codes: they are **legality** cases (what
LLVM passes do to marker programs), not well-formedness cases; their
`EXPECT: probe` questions are answered by this draft as follows:

| Probe question (cases README) | Answer in 0.1 |
|---|---|
| F1: handles stored as integers by LLVM | accepted (§5.2 P2, P3, P6–P8) |
| F2: thunk-to-twin, alias, `strip`, `iroutliner` | accepted: identity by content (§6.3) |
| F3: operand shapes | every shape §6.2 resolves is legal; `other` that §6.2 maps to ⊤ is rejected |
| F4: optimisation-dependent marker operands | the baseline is the materialised optimised module (§7.6) |
| F5: effect attributes on marker-calling helpers | `BD-E-EFFECT-LIE` (§3.8) |
| `cfg-sink-different-callees`: indirect marker calls | cannot arise (§3.1 rule 3); none observed |
| `c-unprototyped-decl` | accepted (§3.5) |

The harness checks, restated with their 0.1 reading:

| Check | Property | 0.1 reading |
|---|---|---|
| L1 | the dynamic marker sequence and the classical result are preserved | unchanged; for cases whose marker operands are computed from floating point or query intrinsics, the baseline is the materialised module (§7.6) |
| L2 | no pass adds a forbidden attribute | the permitted list of §3.6 |
| L3 | handles stay contained (guard page, `BADHANDLE`; static review of new casts) | dynamic part unchanged; the static review is decided by §5 |
| L4 | region identity | every region operand resolves (§6.2) to candidates content-equal (§6.3) to the baseline's; aliases, forwarding thunks and merged twins pass (the harness still compares symbols: §15 item C3) |
| L5 | native code generation keeps L1 and every marker an undefined external | unchanged |
| L6 | region-operand shapes | a shape is legal iff §6.2 resolves it |

### 10.2 What a conforming toolchain passes

A toolchain (a front end, an LLVM major and a pipeline) conforms for
dialect 0.1 iff, for every `EXPECT: legal` case and every pipeline in
the **supported envelope**, L1, L2, L3 and L5 pass and L4 and L6 pass
in their 0.1 reading, and the four negative controls are detected (red)
by the harness used.

**Supported envelope**: LLVM 18, 20 and 23; `default<O0>` …
`default<O3>`; `default<Os>`, `default<Oz>` on 18 and 20 (LLVM 23's
`opt` rejects them); `lto-pre-link<O3>`, `lto<O3>`,
`thinlto-pre-link<O3>`, `thinlto<O3>`, `default<O3>` three times;
clang `-O0` … `-O3` with `-flto`; rustc `-C opt-level` 0, 1, 2, 3, s, z,
including its MergeFunctions in aliases mode; Julia 1.13's own
pipeline; `strip`, `strip-nondebug` and `mergefunc` alone.
**Unsupported** (outside the contract on every supported major): the
Attributor, module and CGSCC (`attributor`, `attributor-cgscc`;
llvm-project #234748, #236104, and on 18 and 20 the constant-table fold
fixed by PR #151359); `normalize` without `preserve-order` (#236128);
`structurizecfg` without its prerequisites (`lowerswitch` or
`lower-switch`, `fix-irreducible`, `unify-loop-exits`); the passes the
harness classes `non-preserving` (`metarenamer`, `dfsan`,
`hipstdpar-select-accelerator-code`) and the sanitizer and
instrumentation passes (`asan`, `msan`, `hwasan`, `memprof`, `tysan`,
`instrumentor`); any other single pass not run inside an envelope
pipeline (§14 D20). *(non-normative)* The spike measured every P2 cell
of the envelope pipelines on every major: the only FAIL cells are the
F4 and F5 probes, which 0.1 resolves (§7.6, §3.8).

### 10.3 Conformance suites

| Suite | Class | Content |
|---|---|---|
| DA | Plugin, Validator | recognition, reserved names, attributes, Julia check, unwinding: the §3 examples; L2 over the corpus |
| DB | Plugin, Validator | handle provenance and containment: the §5 examples; L3 over the corpus |
| DC | Plugin, Validator | candidate sets, identity, well-formedness, budgets: the §6 examples; L4, L6 over the corpus |
| DN | Plugin, Validator | normalisation pairs and validator verdicts: the §7 examples; two independent validators agree on the corpus after materialisation |
| DM | Plugin | lifting map, reference-body hashes, F_B and in-place verdicts: the §9 examples, executed on the ISA reference interpreter |
| DS | Plugin + executor | marker semantics: the §8.8 programs and their events and states; differential runs against the reference semantics (§8.7) |
| DL | Toolchain | the legality matrix of §10.2 |

The `spec-*` cases (`spec-sem-ctrl`, `spec-sem-adj`,
`spec-sem-compute`) are byte-identical to the §8.8 programs and run
under the harness like every case.

## 11. The driver's plugin-invocation interface

### 11.1 Pipeline position

Front ends emit bitcode with their stock pre-link pipelines; no Bennett
code runs before the final link. The driver links all bitcode of one
LLVM major (§14 D19), runs the post-link pipeline (`lto<O3>` by
default, or any envelope pipeline of §10.2 the user selects), then runs
the plugin on the whole program (north star §3.3). With `opt`:

```
opt -load-pass-plugin=libbennett-plugin-<major>.so -passes='lto<O3>,bennett' -bennett-dialect=0.1 …
```

The plugin runs on one merged module: full LTO (§14 D23). It registers
one module pass, named `bennett`. It MAY also
register a full-LTO last extension point for use from a linker plugin;
it MUST do nothing in any pre-link or per-translation-unit phase
(enzyme survey §2.4: Enzyme PR #3211).

### 11.2 A missing plugin fails loud

No production artefact defines a marker: `bennett-runtimes`,
`bennett-arith` and the driver's link inputs define no `__bennett_*`
marker symbol (test runtimes such as the spike trace runtime do, and
are never linked into production). A link in which the plugin did not
run therefore leaves undefined references to `__bennett_*` and fails at
link time. The driver MUST NOT ignore unresolved symbols or supply weak
marker definitions. *(non-normative)* This is Enzyme's behaviour since
PR #3211 ("Forgetting it is a loud failure").

### 11.3 Options

| Option | Meaning | Default |
|---|---|---|
| `-bennett-dialect=<v>` | MUST equal the plugin's dialect version (`BD-E-VERSION` otherwise) | required |
| `-bennett-isa=<v>` | MUST equal the ISA version the plugin targets (`BD-E-VERSION`) | `0.8` |
| `-bennett-budget-default=<u64>` | `B_default` (§6.5) | `1048576` |
| `-bennett-out=<dir>` | directory receiving the outputs of §11.5 | required |

### 11.4 Identity

`llvmGetPassPluginInfo` returns plugin name `bennett` and version
string `dialect-0.1;isa-0.8`; the driver refuses a plugin whose string
differs from the versions it was built for. One plugin build per LLVM
major (north star §3.2).

### 11.5 Outputs

In `-bennett-out`: the materialised device closure as bitcode (for the
native comparison build, §7.6); the host module with device entries
replaced by launch calls (driver-defined); the ISA objects (ISA §9,
§16); the certificate (ISA §12) with `producer.materialisation =
{llvm_version, pipeline, normaliser_version: "0.1"}` and
`bindings.dialect_mapping_version = "0.1"`; and the coverage report
(ISA §13), whose `source` field is `dialect-0.1:<rule id>` (for example
`dialect-0.1:N18`). File names are plugin-defined (§14 D22).

### 11.6 Module flag

A producer MAY add the module flag `!{i32 1, !"bennett.dialect",
!"0.1"}` (behaviour Error, so an LTO link of modules of two dialect
versions fails); the plugin MUST reject a module whose flag differs from
its version (`BD-E-VERSION`).

## 12. Diagnostics

Compile-time rejections, in processing order (§4.1):

| Code | Rule |
|---|---|
| `BD-E-VERSION` | §11.3, §11.6 |
| `BD-E-MARKER-DEFINED` | §3.1 rule 1 |
| `BD-E-MARKER-UNKNOWN` | §3.1 rule 2 |
| `BD-E-MARKER-ADDRESS` | §3.1 rule 3 |
| `BD-E-MARKER-SIGNATURE` | §3.5 |
| `BD-E-MARKER-ATTRIBUTE` | §3.6 |
| `BD-E-JULIA-CCALL` | §3.8 |
| `BD-E-EFFECT-LIE` | §3.8 |
| `BD-E-REGION-UNBOUNDED`, `BD-E-REGION-EXTERNAL`, `BD-E-REGION-TYPE`, `BD-E-REGION-THUNK` | §6.2 |
| `BD-E-DEVICE-ADDRESS` | §4.2 |
| `BD-E-EH` | §3.7 |
| `BD-E-HANDLE-USE`, `BD-E-HANDLE-STORE`, `BD-E-HANDLE-ESCAPE`, `BD-E-HANDLE-UNTRACKED` | §5.2, §5.4 |
| `BD-E-REGION-MEASURE`, `BD-E-REGION-TIER`, `BD-E-REVERSIBLE-MARKER` | §6.4 |
| `BD-E-RESIDUAL` | §7.5 |
| `BD-E-OPERAND`, `BD-E-OPERAND-UNBOUNDED` | §3.4 |
| `BD-E-LIFT-SUBSET` | §9.1 |
| `BD-E-INPLACE-NOT-INVERSE`, `BD-E-INPLACE-UNVERIFIED` | §6.4 |

Run-time traps (fault code 4, §7.4, §8.3): `T-DEAD`, `T-FOREIGN`,
`T-CLEAN`, `T-INDEX`, `T-ALIAS`, `T-THETA`, `T-MEASURE`, `T-SIZE`,
`T-CTRL`, `T-TIER`, `T-BORROW`, `T-LEAK`, `T-REGION`.

## 13. Versioning

- The **full version string** of this document (`0.1`) is the unit of
  compatibility: a plugin implements exactly one dialect version and
  targets exactly one ISA version (§11.3, §11.4); drafts are not
  compatible with each other.
- Sub-artefacts, versioned with the document and recorded where named:
  `markers` (§3), `handles` (§5), `regions` (§6), `norm` (§7; the
  certificate's `normaliser_version`), `map` (§9; the certificate's
  `dialect_mapping_version`), `corpus` (§10). In draft 0.1 all are
  `0.1`.
- Every semantic change bumps the version; the reference-body hashes of
  §9 depend on the ISA version string and change with it.
- `SPEC_VERSIONS.toml` records `dialect` and the targeted `isa`; the
  change rules are in `spec/README.md`.

## 14. Decisions deferred to implementation, with defaults

Each item is one an implementer may need to decide; two implementations
agree by following the default until the item is revised.

| Id | Decision | Default in 0.1 |
|---|---|---|
| D1 | Qubit classes other than `any` (§3.4) | only `cls` = 0 (`any`); any other value is `BD-E-OPERAND` |
| D2 | Out-of-band per-region budget tables (§6.5) | none; `B_default` only |
| D3 | Classical arguments of oracle regions | none: an oracle region is `iT (iN)`; a front end specialises constants into the function |
| D4 | Lifting of memory, calls, floating point and vectors in oracle regions (§9.1) | `BD-E-LIFT-SUBSET` |
| D5 | Deferred measurement inside unitary regions (north star §3.1) | refused (`BD-E-REGION-MEASURE`) |
| D6 | Dirty borrowing (`qborrow`) | a clean allocation, only inside a generation (`T-BORROW` otherwise) |
| D7 | A static clean-target rule for `qstore` | none; `qstore` is XOR (§5.5) |
| D8 | Comparison of handles (`icmp` on a handle) | rejected (`BD-E-HANDLE-USE`) |
| D9 | Heap allocation functions that create abstract objects (§5.2) | `malloc`, `calloc`, `aligned_alloc`, `_Znwm`, `_Znam`, `__rust_alloc`, `__rust_alloc_zeroed`; any other allocator's result has base ⊤ |
| D10 | Exceptions in the device closure (§3.7) | `BD-E-EH`, except marker invokes |
| D11 | Effects: virtualisation of libc calls as device models (ISA §7.3); marshalling of host calls from device code (§4.3) | in oracle and reversible closures F(8); elsewhere a host call whose marshalling is driver-defined |
| D12 | Shadow stack for allocas (north star §3.2) | none; executions where a native stack address influences a result are layout-dependent |
| D13 | A region key stable across LLVM majors (§6.3) | the key depends on the major, which the certificate records |
| D14 | In-place verification above 16 bits (§6.4) | an `inverse_pair_library` claim, else `BD-E-INPLACE-UNVERIFIED` |
| D15 | The address layout of device classical memory (§7.4) | the native comparison link (non-PIE, fixed addresses, no identical-code folding or constant merging) and the allocator's fixed base |
| D16 | Half, bfloat, x86_fp80, fp128, transcendental intrinsics, vector floating point (N17) | F(8) |
| D17 | Coherent lifting of the classical code of `ctrl` bodies (taint into classical code under control) | none: generation semantics (§8.4); the `ctrl` budget has no effect |
| D18 | An R-tier budget (`reversible`) | no effect (§15 ISA-2) |
| D19 | Links mixing LLVM majors | one major per link |
| D20 | Single passes outside the envelope (§10.2) | unsupported unless listed |
| D21 | Oracles over several input registers | one input register; producers pack inputs into it |
| D22 | Output file names and diagnostic text | plugin-defined; the codes of §12 are normative |
| D23 | ThinLTO with the plugin | full LTO only: the plugin runs on one merged module |
| D24 | Multi-threaded device code | the single-thread assumption (N9), recorded in the certificate |
| D25 | How device code reaches host memory (pointer arguments of device entries, globals shared with host functions) | the reference semantics has one classical memory (§8.1); the driver realises it across the host–device boundary as it chooses (copy-in/copy-out around each device-entry call, or `hostcall`), and conformance is judged by §8.7 |

## 15. Open items

**For a future ISA revision** (the dialect works inside ISA 0.8 with the
default stated in each row):

| Id | Need | Dialect 0.1 default |
|---|---|---|
| ISA-1 | A classical-control instruction that builds a budget token from run-time values (north star §4.2: budgets chosen at run time from classical data) | budgets must have a finite constant candidate set; the driver mints the tokens (§6.5) |
| ISA-2 | A step budget for R-tier calls | the `reversible` budget has no effect |
| ISA-3 | Classical arguments for `qinplace`; the JCS encoding of `args` types in oracle signatures (ISA §9.1 shows only `"args":[]`) | no classical arguments for oracle regions (D3) |
| ISA-4 | `qreg` values of run-time width, and `qreg` values in classical memory or indexed tables (dialect handle tables, §5.3) | the plugin resolves widths and handle tables to static `qreg` values or rejects; widths have constant candidate sets (§3.4) |
| ISA-5 | Two simultaneous slices of one `qreg` (a two-qubit gate on two wires of one register at classical indices) | the plugin keeps each wire a separate `qreg[1]` |
| ISA-6 | A non-consuming measurement of one wire | `measure` plus re-preparation (`qreg.new` and a conditional `x`) |
| ISA-7 | The fault code a classical-control trap reports in launch results (ISA §10) | the dialect's codes of §7.4 |
| ISA-8 | Propagation of an R-tier fault record to the calling classical-control code | the run ends `FAILED` |
| ISA-9 | Borrowed wires outside static Q regions | clean allocation (D6) |
| ISA-10 | ISA §9.2 wording for acyclic one-member symbols (council round-8 suggestion) | the ISA §16.3 test vectors: the hash is the SHA-256 of the envelope (§9.5) |
| ISA-11 | Launch arguments that pass host memory to a device entry by reference (ISA §10 binds only `INT`, `F64`, `QREG`, `TOKEN`) | D25 |

**Dialect items:**

| Id | Item |
|---|---|
| C1 | Update the trace runtime and harness to ABI 0.1 (`gate3`, `oracle`, the new `inplace`); add corpus cases for them (owner: harness) |
| C2 | Rerun P4 (clang `-flto` end to end) under the current harness; add a rustc `-Clinker-plugin-lto` case (spike findings §5) |
| C3 | Relax harness L4 to content identity (§10.1) |
| C4 | Draft and grade north-star amendment A2 (handle provenance, §1.4) with A1 |
| C5 | Minimise the three P3-only interactions with `llvm-reduce` |
| C6 | A `-g` variant of every `.c` case (enzyme survey implication 9): every instruction the plugin creates in place of a marker inherits its debug location |
| C7 | Windows EH funclet bundles and non-x86-64 targets are untested |
