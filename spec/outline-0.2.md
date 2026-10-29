# Bennett LLVM Dialect — draft 0.2 — OUTLINE

**Date:** 2026-10-29. **Status:** outline for maintainer review against the demo ladder
(phase 3, step 1 of `bennett/docs/plan/2026-10-29-path-to-north-star.md`). This is not
normative text. It fixes the structure of draft 0.2 and every mechanism decision, so that the
editor writes the full text without re-deciding anything. **Targets ISA 0.8**
(`bennett-isa-spec/spec/Bennett-ISA-Spec.md`, cited "ISA §n"). "NS §n" is
`bennett/docs/Bennett-NorthStar.md` iteration 7. "0.1 §n" is `spec/Bennett-Dialect-Spec.md`
draft 0.1. "Audit" is `docs/audit/2026-10-29-dialect-0.1-narrowing-audit.md`, and its row ids
(D4, B-24, O-01, …) are used unchanged. "SQLite" is `docs/spikes/sqlite/REPORT.md`. bd ids are
the children of epic `b-dialect-spec-8wf` (written `.N` for `b-dialect-spec-8wf.N`) plus the
0.1 dialect items `-566` (C1), `-j88` (C2), `-cjb` (C3), `-25h` (C4), `-ape` (C5), `-u6a` (C6) and
`-kdj` (C7).

**Standing rule (binding on the editor; CLAUDE.md rule 10).** Draft 0.2 narrows no north-star
capability. The text may reject only what the north star itself requires to be rejected, or
what a maintainer decision settles. Every such rejection appears in the diagnostics table (§22)
with the NS clause or decision that requires it. A deferral in §24 postpones mechanics only.
Where ISA 0.8 truly cannot express a promised capability, §25 names a **blocker** and the exact
ISA change. The dialect still specifies the full mechanism, and the plugin reports
`BD-B-<blocker>` (a blocker report, not a dialect rejection) on the executions or programs the
blocker affects. The pre-flight checker never bounds the spec (part D).

Contents:

- **Part A.** Section-by-section outline of draft 0.2.
- **Part B.** Mechanism decisions, with the alternatives rejected.
- **Part C.** Rung-by-rung scope check.
- **Part D.** Pre-flight checking plan.
- **Part E.** Open questions for the maintainer.
- **Part F.** bd closure map.

---

# Part A. Section-by-section outline of draft 0.2

Each section lists:

- **Content:** the normative rules, in bullets.
- **Lowers to:** the ISA 0.8 rows and sections involved.
- **Reuses:** which 0.1 text carries over.
- **Closes:** the bd ids.

Sections keep 0.1's numbering where they correspond. New material is inserted as §8, §10, §11,
§13–§15, §17, §19 and §20.

## §1 Scope and conformance

**Content:**

- **§1.1 What the dialect is.** As 0.1 §1.1, extended to these areas:
  - tiers and polyvariant cloning (§4);
  - the device analysis (§5);
  - the oracle interface (§8);
  - budgets (§9);
  - taint-driven lifting (§10);
  - effects (§11);
  - calls and control transfer (§14);
  - the asm and intrinsic tables (§15);
  - the device classical memory model (§17);
  - driver modes (§19);
  - the platform profile (§20).
- **§1.2 Conformance classes.** The 0.1 classes (Producer, Plugin, Driver, Validator), plus two
  new ones:
  - **Runtime.** `bennett-runtimes` and `bennett-arith` must provide the entry points that
    §11, §13 and §14 name, with the semantics stated there. They are tested by suites DR and
    DF (§21).
  - **Platform.** A platform profile of §20 is a model plus shims, tested by suite DP.
- **§1.3 Relation to the ISA.** As 0.1 §1.3. "Files an open item" becomes the following rule:
  where ISA 0.8 lacks a needed construct, the dialect states the full mechanism, the ISA 0.8
  realisation where one exists, and otherwise a §25 blocker. The dialect never shrinks to fit.
- **§1.4 Departures from the north star.** Only these remain:
  - the three maintainer decisions (region identity by content; handle provenance through
    bitwise copies; region operands dispatched over a bounded candidate set);
  - D8 (handle comparison is supported; legality findings, maintainer, 2026-10-29);
  - normalisation of the whole device closure (1.4-h);
  - the XOR store without a static clean-target rule (1.4-g, D7). These are both supersets of
    the north star.

  Every narrowing row of 0.1 §1.4 (1.4-d, -e, -f) is deleted. Its replacement is §10, §9 and
  §8 respectively.
- **§1.5 Notation and checked examples.** As 0.1 §1.5, with new tags (part D lists all tags):
  - `isa object=ID`: a complete ISA object (layout, data, lprocs) produced by the map;
  - `text run=ID`: run-oracle results with four-component budgets, `--mem` and `--arg`;
  - `text cc-run=ID`: a CC or R run with tape and reversal;
  - `text native=ID`: native differential;
  - `text tdl=ID`: TDL partition and events;
  - `c example=ID`: a C source compiled with clang 18/20/23 `-O2 -flto`;
  - `rust example=ID` and `julia example=ID`: emission examples.
- **§1.6 Diagnostics and verdicts.** As 0.1 §1.6. A verdict is `accept`,
  `reject:<BD-E code>` or `blocked:<BD-B code>`.

**Reuses:** 0.1 §1 almost verbatim apart from §1.4.
**Closes:** `-25h` (C4: amendment A2 is drafted alongside, because §1.4 cites it).

## §2 Terminology

**Content:** the 0.1 terms, plus these:

- **tier** of a function variant: H (host), CC, R or L (lifted: oracle body or lproc);
- **variant** (§4.3);
- **function address** A(F) (§4.4);
- **abstract object**, **slot** and **value set** (§5);
- **binding** and **descriptor** (§8);
- **budget record** (§9);
- **coherence state** Cl/Co and **coherent slice** (§10);
- **effect marker** and **device model** (§11);
- **shim**, **trapped** and **lowered** (§15, as ISA §13 classifications);
- **driver mode** (§19);
- **platform profile** (§20);
- **blocker** (§25).

**Reuses:** 0.1 §2. **Closes:** –.

## §3 The marker ABI (markers 0.2)

**Content:**

- **§3.1 Reserved names.** 0.1 rules 1 to 3. The reserved runtime prefixes become `__bennett_nz_`
  (normaliser), `__bennett_sf_` (arith), `__bennett_rt_` (runtimes) and `__bennett_dev_`
  (device-model entry points of the runtimes). Producers never emit them.
- **§3.2 The marker list.** Every marker is a declared external function with the 0.1 legality
  requirement (0.1 §3.6). The list:
  - **Unchanged from 0.1:** `qalloc`, `qborrow`, `qfree`, `gate`, `gate2`, `gate3`, `rot`,
    `measure`, `qload`, `qstore`.
  - **Changed: every region-entry marker takes a budget record (§9).** One signature change per
    marker:
    - `ctrl(ptr q, i64 qi, ptr f, ptr budget, ptr env)`;
    - `adj(ptr f, ptr budget, ptr env)` and `compute(ptr f, ptr use, ptr budget, ptr env)`.
      They are new operands: coherent slices of adjoint and compute bodies need budgets and a
      fault register too (§10, TDL-8/9). Open question E12;
    - `reversible(ptr f, ptr budget, ptr env)`;
    - `oracle(ptr f, ptr budget, ptr desc)`, where `desc` is the descriptor of §8 and replaces
      0.1's `x, tgt, fault`;
    - `inplace(ptr g, ptr ginv, ptr budget, ptr desc)`, with the same descriptor and the
      in-place register bound as `INOUT`.
  - **New: `void __bennett_observe(ptr p, i64 len)`.** A computational-basis measurement of the
    bytes [p, p+len) of classical memory whose coherence state is Co (§10.6). Afterwards they
    are Cl and hold the outcome. It is the only way that superposed classical memory reaches
    classical code without a handle (NS §4.2, "outputs leave through measurement after exit").
  - **New: the effect markers of §11.2**, one per device-model operation (ISA §7.3):
    - `__bennett_effect_console_write(ptr, i64)`;
    - `__bennett_effect_clock_read(ptr)`;
    - `__bennett_effect_entropy_read(ptr, i64)`;
    - `__bennett_effect_block_read(i64, ptr)`;
    - `__bennett_effect_block_write(i64, ptr)`.

    `bennett-runtimes` calls them from its musl, Julia and platform shims. Ordinary programs
    never call them directly; they may.
  - The operand-role table (0.1 §3.2) is extended. Spike ABI v0 evidence carries over to every
    marker whose signature is unchanged. Each changed or new marker gets corpus cases (§21,
    `-566`).
- **§3.3 C header view.** `spec/bennett_markers.h` is regenerated. New types:
  - `bennett_budget` (§9);
  - `bennett_oracle_desc` and `bennett_bind` (§8);
  - the inline helper `bennett_oracle_desc_init(...)`. It is a header macro only, so that
    producers build descriptors by constant stores.
- **§3.4 Operand encodings.**
  - The 0.1 op-code tables are kept.
  - **Classes:** `cls` = 0 is `any`. `cls` = k ≥ 1 is entry k of the link-time **class-name
    table**. The table is the union by name of the module flags `!"bennett.classes"` (a list
    of strings, merged by the driver in first-appearance order) and the driver option
    `--bennett-class=<name>`. An unknown name at load is an ISA load error (ISA §8.3 `classes`).
  - **Run-time operands:** a non-constant `op` or `cls` is classical data. The plugin
    dispatches over its value set (§5), or over the whole table when the set is unbounded. A
    value outside the table traps at run time (`T-OP`, `T-CLASS`).
  - `n` (width) has a value set from §5 (constants, value-range from `range`/known bits,
    `select`/`phi`). A bounded set is dispatched. An unbounded set is realised on ISA 0.8 only
    by blocker BLK-1 (§25). The verdict is `blocked:BD-B-ISA4` and the diagnostic names the
    value.
  - A **constant** operand outside its table stays `BD-E-OPERAND`. Such a program always
    traps at that marker, so this is L, fail fast.
- **§3.5 Recognition.** 0.1 §3.5 unchanged (including K&R).
- **§3.6 Attributes.** Three lists:
  - **forbidden:** the 0.1 licensing set;
  - **benign, ignored:** the 0.1 permitted list, plus `strictfp`, `cold`, `hot`, `nomerge`,
    `noinline`, `convergent`, `builtin`, `nobuiltin`, `optsize`, `minsize` and `optnone`,
    promoted after a corpus run in which they license nothing (`-566`, `.21`);
  - **unknown:** `BD-E-MARKER-ATTRIBUTE` until corpus evidence. This is L, because an unknown
    attribute may license motion (NS §3.1 positive legality requirement).
- **§3.7 Unwinding of markers.** 0.1 §3.7 first half (invoke of a marker → call + br). The
  second half (`BD-E-EH`) is deleted. Unwinding of everything else is §14.4.
- **§3.8 Front-end emission routes.** As 0.1 §3.8. The Julia `@cfunction` sentence changes:
  Bennett.jl emits `ptr @f` in its own module (audit B-14). A `@cfunction` constant is an
  `inttoptr` of an address. It is dispatched by value against the address-taken functions of
  its type (§7.2), so it resolves whenever the body is in the link.

**Lowers to:**

- classes: ISA §4.3 `qalloc cls n`, §3.3 `qreg.new cls n`;
- dispatch: CC compare-and-branch (ISA §4.1 `icmp`, `br`);
- observe: ISA §3.3 `measure` of the arena slice (§10.4).

**Reuses:** 0.1 §3 (all examples except `operand-class` and `operand-width-host`, which become
`accept` and `blocked` respectively).
**Closes:** `.4`, `.18`, `.21`; `.19` (partly; the rest is BLK-1); `-566`.

## §4 Processing order, device program, tiers, variants, function addresses

**Content:**

- **§4.1 Processing order.** S1 to S9 as in 0.1 §4.1, re-cut:

  | Step | Content |
  |---|---|
  | S1 | names, recognition, attributes, Julia check, marker invokes |
  | S2 | the device analysis (§5): one fixpoint for points-to, value sets, region candidates, indirect-call candidates, handle provenance and descriptor kinds |
  | S3 | tier assignment and variants (§4.2–§4.3) |
  | S4 | handle rules (§6) |
  | S5 | region well-formedness (§7.5) |
  | S6 | TDL partition (§10) |
  | S7 | normalisation (§12) and validator |
  | S8 | lifting (§16) and in-place verification |
  | S9 | lowering |

  The call graph contains direct edges, region-candidate edges and **indirect-call candidate
  edges** (§14.2).
- **§4.2 Tier assignment.** Every defined function reachable from the program's roots gets a
  set of tiers:
  - **H:** reachable from host roots and not forced elsewhere.
  - **CC:** contains a marker call, receives a handle, is reachable from an action region's
    generation, or is promoted by §19.4.
  - **R:** in the closure of a `reversible` operand, or every function under
    `--bennett-tier=reversible` (§19.2).
  - **L:** in the closure of an oracle or in-place operand, or of a coherent slice (§10).

  A function may get several tiers.
- **§4.3 Polyvariant cloning (closes B-16).**
  - Each (function, tier, coherence signature §10.2) pair is a **variant**.
  - H keeps the original. Device variants are clones.
  - Clones share all globals: data is never cloned. There is one classical memory (NS §3.2).
  - 0.1's `BD-E-DEVICE-ADDRESS` is deleted.
- **§4.4 Function addresses.**
  - Every function whose address is used has the **function address** A(F): its address in
    the driver's comparison link (NS §3.2: non-PIE, fixed section addresses, identical-code
    folding and constant merging off; SQLite §5.2(ii)).
  - A(F) is the value of `ptr @F` in every tier:
    - in host code, by linking the production host image with the comparison layout when an
      address may cross the boundary (§19.5);
    - in CC/R code, as a `const` + `inttoptr`;
    - in lifted code, as a `lift.const`;
    - in every data image (global initialisers, vtables, `aBuiltinFunc`, VFS method tables).
  - `ptrtoint`, comparison and storage of function pointers therefore equal native.
  - Each tier maps A(F) to its own variant through the dispatch of §14.2.
- **§4.5 Calls out of the device program.** Replaces 0.1 §4.3. A call of a function with no
  definition resolves, in order:
  1. markers and primitives;
  2. a **runtime shim** of `bennett-runtimes`/`bennett-arith` defining the symbol (libc, libm,
     libpthread with one thread, the Julia shim runtime, platform shims). The shim is linked as
     bitcode and is an ordinary device function (coverage class `shimmed`, with `shim_hash`,
     ISA §13);
  3. in CC only, a **host call** through `hostcall` (§11.4);
  4. otherwise `trapped`: F(8) at the call, with a coverage line (NS §3.3: "Calls with no
     bitcode are coverage-report lines (*trapped*), never silent"). This is L.

**Lowers to:**

- CC `call`, R `call`, `lift.call` (ISA §4.1, §4.2, §3.7);
- `const`/`inttoptr` (ISA §4.1);
- data images (ISA §9.1 `data`, `layout.globals`);
- `hostcall` (ISA §10).

**Reuses:** 0.1 §4.1–§4.3 (re-cut).
**Closes:** `.22`, `.35` (with §14.2); `.13` (the external-call half).

## §5 The device analysis (one fixpoint)

**Content:**

- **§5.1 Abstract objects.**
  - each `alloca`;
  - each global;
  - each **allocation site**: a call whose callee carries `allockind("alloc")` or `allocsize`;
    the runtimes allocator entry points; `julia.gc_alloc_obj` and its lowered forms; `_Znwm`
    and friends; and any defined function whose return is a fresh object (computed
    interprocedurally);
  - the pseudo-object `EXT`.

  Heap objects are context-insensitive. Optional heap cloning of one level is allowed: it is
  precision only, and the verdict must not depend on it (`.11`).
- **§5.2 Points-to.**
  - Andersen-style, inclusion-based, field-sensitive, whole-program over every device variant
    and every host function that exchanges data with them.
  - Slots (X, o) are byte offsets.
  - A variable GEP over an array of element size s gives the offset class {o + k·s} within
    the array's extent, not `*` (closes B-27).
  - `*` is kept only for offsets the GEP source type cannot bound.
  - Call results flow through `ret`; parameters through every direct call and every indirect
    candidate (§14.2).
  - Memory intrinsics copy slot ranges.
  - Rules replace 0.1 B1–B5 and P1–P9.
- **§5.3 Value sets.** The same fixpoint tracks finite **value sets** for integers and pointers
  stored in slots (constants, function addresses, handle roots, descriptor kinds, budget
  fields), with ⊤ for unbounded. A value set is a precision tool only:
  - an operand with a finite set is dispatched over it;
  - an operand with ⊤ is dispatched over its type's whole valid domain where that domain is
    finite (op codes, classes, binding kinds, function addresses of a type);
  - otherwise it is a §25 blocker case (widths, budgets).
- **§5.4 Uses.** One section states which later rule reads which result:
  - region candidates (§7.2);
  - indirect-call candidates (§14.2);
  - handle provenance (§6);
  - descriptor kinds (§8.2);
  - objects that may become Co (§10.2);
  - objects an oracle may read (entry-state transfer, §8.5).

**Lowers to:** analysis only. **Reuses:** 0.1 §5.2 bases and propagation tables, rewritten as
points-to rules. **Closes:** `.11`, `.25`, `.26`, `.27`, `.30` (with §7.2).

## §6 Handles (handles 0.2)

**Content:**

- **§6.1 Representation.** As 0.1 §5.1. In device memory a handle is stored as its **register
  id**, an opaque 64-bit value, the ISA launch representation (ISA §10 `bennett_qreg`). Its
  bits never influence a result.
- **§6.2 Provenance.** Decision 2. Provenance flows through bitwise copies (`ptrtoint`,
  `inttoptr`, integer loads and stores, vector lanes including **dynamic lanes**: B-23 becomes
  a handle-table read, `.24`) along §5. Any other use of a handle-derived integer is
  `BD-E-HANDLE-USE`. This is L by decision 2.
- **§6.3 Comparison (D8).**
  - `icmp eq/ne` of a handle with `null` or with another handle is **identity**: a live handle
    is never null, and two handles are equal iff they denote the same register.
  - The result is not handle-derived.
  - Lowered in CC as `icmp` on register ids.
  - This covers Rust's `Option<Handle>` niche and C `if (!q)` (`.10`).
- **§6.4 Collections.** Handles may be stored through any pointer the points-to analysis
  tracks: tables, vectors, linked structures, globals (field-sensitive), and objects passed to
  indirect calls or returned by address-taken functions. `BD-E-HANDLE-ESCAPE` remains only for
  slots that **host code may read** (L: NS §3.1, no handle use in host native code). Closes
  B-24, B-26, B-29, B-22: `.23`, `.25`, `.26`, `.28`.
- **§6.5 Realisation on ISA 0.8 (static register files).**
  - The plugin assigns each **root** (allocation site × dynamic-instance index) a static CC
    `qreg` variable.
  - Device CC variants receive the live register file as extra parameters and results (a
    "register-environment passing" transform).
  - A marker operand whose provenance holds several roots is dispatched by comparing register
    ids (compare tree, §14.2) to the static `qreg`.
  - This realises every program in which each allocation site has a **statically bounded**
    number of simultaneously live instances.
  - A root with a run-time-unbounded instance count, or a width with an unbounded value set,
    is BLK-1 (ISA-4).
- **§6.6 Host–device boundary (B-30).**
  - Device-entry parameters and results of handle type bind to launch `QREG` arguments and
    results (ISA §10).
  - Host code may copy, store and compare these ids. Provenance is extended to the host
    functions that receive them, with the rule of §6.2.
  - Leak checking happens at program end and at `bennett_qreg_free`, not at each device-entry
    return. This gives REPL lexical lifetime (NS §5) (`.29`).
- **§6.7 Copy, XOR, in-place.** 0.1 §5.5, with D7 kept: `qstore` is XOR, and an optional
  verifier diagnostic `BD-W-QSTORE-UNCLEAN` serves front ends that want overwrite semantics.
- **§6.8 Handle → wire obligations.** 0.1 §5.6.

**Lowers to:**

- ISA §3.3 `qreg.*`, handle states and binding;
- §4.7 region calls with `qreg` operands;
- §10 `BENNETT_ARG_QREG`;
- CC `icmp`.

**Reuses:** 0.1 §5 (the provenance rules become §5 points-to rules; the examples are kept and
`handle-null-check` flips to accept).
**Closes:** `.10`, `.23`, `.24`, `.25`, `.26`, `.27`, `.28`, `.29`; `.19`/BLK-1 partly.

## §7 Regions (regions 0.2)

**Content:**

- **§7.1 Region-entry markers and kinds.** The 0.1 §6.1 table, with new signatures:
  - `oracle`/`inplace` candidates may have **any LLVM function type** (§8), not `iT (iN)`;
  - action and reversible candidates are `void (ptr env)`.

  "The region kind is fixed by the marker" stays, but only for the *interface* (TDL-1): the
  body is partitioned by content (§10). The sentence "the plugin never outlines source code"
  is deleted. The plugin outlines coherent slices (§10.3).
- **§7.2 Candidate sets and dispatch.** Decision 3 with the type fallback (audit B-33):
  - RR(v) is the §5 value set of the region operand, restricted to functions.
  - Where the analysis gives ⊤, RR(v) = every function of the required type whose address is
    used anywhere in the linked program (decision 3 read literally: the set is bounded by the
    program).
  - Thunk and alias resolution as in 0.1 C1.
  - Dispatch compares A(F) values (§4.4) with a compare tree (§14.2). No match is the run-time
    trap `T-REGION` (code 4).
  - A candidate that is not well-formed for the marker's kind (§7.5) is compiled as a trap
    body (`T-REGION-INVALID`, code 4) with a coverage line. It is not a compile-time rejection,
    because it may never be dispatched. It is rejected (`BD-E-REGION-*`) only when it is the
    unique candidate.
  - `BD-E-REGION-UNBOUNDED` and `BD-E-REGION-EXTERNAL` are deleted. A region pointer that can
    denote a function without bitcode traps on that execution (§4.5 item 4).
- **§7.3 Region identity.** Decision 1, as 0.1 §6.3. The oracle identity is the ISA interface
  hash of the reference oracle produced by §16, layout included (ISA §9.2 oracle closure set).
- **§7.4 Kinds by content.** NS §4.2: a region is classified after TDL:
  - an action whose events are all permutations becomes a `perm_action`;
  - an oracle stays an oracle;
  - a `reversible` operand reached from a coherent context is lifted coherently (closes B-37,
    `.31`).
- **§7.5 Static well-formedness.** Only the NS-required rules remain:
  - **(a)** User `measure` inside a unitary region is refused (L, NS §3.1), unless the module
    requests **deferred measurement**: module flag `!"bennett.measure_in_unitary" = "defer"`.
    Then `measure` inside a generation becomes `qcopy` onto a fresh wire, its result is a Co
    value under §10, and the certificate records `deferred_measurement` (`.8`).
  - **(b)** A `reversible` closure may contain gate and region markers on handles received
    through `env`. They are lowered to R-tier `action_call`/`oracle_call` (ISA §3.1, §4.7) and
    reversed by re-application or adjoint (ISA §7.4). `measure` in R is refused (L:
    irreversible; ISA §10 reverse eligibility). `qalloc`/`qfree` in R are realised by hoisting
    to the CC caller when their count is static, else BLK-4 (`.32`).
  - **(c)** In-place pairs are verified by §8.6.
- **§7.6 Outlining conventions.** As 0.1 §6.6, minus "the plugin never outlines" and minus the
  `iT (iN)` packing rule.

**Lowers to:**

- ISA §4.7 `oracle_call`/`action_call`/`adj`/`ctl`;
- §5.2, §5.3;
- CC compare tree;
- R region calls (§3.1, §7.4 region-call frames).

**Reuses:** 0.1 §6.1–§6.4, §6.6 and examples. `region-host-param`, `region-inttoptr` and
`region-external` flip to accept, with dispatch over the type-compatible set and a run-time
trap.
**Closes:** `.8`, `.30`, `.31`, `.32` (BLK-4 for R allocation).

## §8 The oracle interface: descriptor, bindings, entry state, in-place

**Content:**

- **§8.1 Descriptor layout** (C view; LLVM view via the datalayout):
  `struct bennett_oracle_desc { u32 version /*=2*/; u32 nparam; u32 ndev; u32 flags; bennett_q tgt;
  bennett_q fault; bennett_bind param[nparam]; bennett_devbind dev[ndev]; }`, with
  `struct bennett_bind { u32 kind; u32 mode; bennett_q q; u64 value; u64 size; }` and
  `struct bennett_devbind { u32 model; u32 mode; bennett_q q; u64 value; }`.

  `nparam` equals the number of parameters of the region function after ABI lowering (the IR
  signature).
- **§8.2 Parameter binding kinds:**
  - **`IN`:** the parameter's basis value is register q.
    - n(q) ≤ the parameter width.
    - `mode` = ZEXT or SEXT extends it.
    - A `ptr` parameter may be `IN` (a superposed pointer).
    - Lowered to an ISA `ins` bundle (a pseudo-location).
  - **`ARG`:** a classical value `value` (bits of the parameter). It is an ISA classical
    `args` entry (ISA §4.7, §5.1, §3.7 pseudo-location). A `ptr`-typed ARG denotes an address in
    the caller's classical memory, which the oracle sees through §8.5.
  - **`MEM_IN`:** a `ptr` parameter that receives `lift.addr` of an interface region bound to
    register q, with n(q) = 8·2^A and `size` = 2^A bytes. The region has role `in` (ISA §5.1,
    §7.2, §3.3 binding). Its contents may be superposed; it is the "quantum-addressed memory"
    of NS §8 rung 4.
  - **`OUT`:** a `ptr` parameter that receives a fresh zeroed lifted allocation of `size`
    bytes. Its final bytes are XORed into register q, as a declared output (NS §4.2).
  - **`INOUT`:** in-place only. The register x of `inplace`.
  - The function's return value XORs into `tgt` (a null `tgt` means void).
  - If n(tgt) is narrower than the return type, the plugin appends a check: dropped bits that
    are nonzero → `fault 4`.
  - `fault` is a register of F = 4 wires (ISA §5.4).
- **§8.3 Device bindings (coherent tier, §11.3).** `model` is one of:
  - **ENTROPY:** an `in` region on q, possibly superposed (rung 8);
  - **BLOCK:** an `in` region on q holding the disk image, with a lifted copy-on-write overlay;
  - **CLOCK:** the initial value `value`;
  - **CONSOLE:** an output register q for console bytes; with a null q they are discarded.
- **§8.4 Static shape and dispatch.**
  - Each kind, mode and width field has a §5.3 value set.
  - The plugin builds one ISA oracle signature per element of (region candidate × binding
    shape) that the value sets allow. The kind domain is finite, so this is always bounded.
  - It dispatches at run time in CC.
  - A descriptor whose run-time shape matches no compiled shape traps (`T-IFACE`, code 4):
    this happens only for a value outside the kind table.
- **§8.5 Entry state ("the oracle sees the caller's memory").**
  - **Reference semantics.** The region function runs on a private copy of the caller's whole
    classical memory at the call, with the bound inputs. Its writes are discarded, except
    through `OUT`, `tgt` and device outputs (NS §4.2: "every other write being restored
    workspace").
  - **ISA 0.8 realisation.** Let R be the abstract objects the oracle closure may read (§5),
    minus constant globals.
    - Constant globals are data images: equal by construction.
    - For the mutable globals and live heap objects in R, the plugin emits an
      **entry-state transfer**:
      - at the call, CC prepares a snapshot register;
      - it contains the allocation-table sizes and live bits plus the bytes of R;
      - CC builds it with chunk-wise `oracle_call`s of a runtime oracle that XORs classical
        `args` into slices, 128 bits per call;
      - the register is bound as an extra `in` region;
      - the oracle prologue **replays** the allocation sizes with `lift.alloc`, which
        reproduces the CC addresses exactly, because ISA §4.2 `lift.alloc` and §7.1 `alloc`
        share the rule `max(n,1)` from `heap_base`;
      - it then copies the bytes into globals and heap (audit O-07).
    - When R holds no mutable object, nothing is transferred. This is SQLite route A.
    - Efficiency: G-12 (ISA 0.9 candidate). Closes `.6`, `.40`, D25.
  - **Build-time snapshots** (rung 7 option, §19.6): globals' initialisers are rewritten to
    snapshot values at link time, so the snapshot is in the data images and no transfer runs.
- **§8.6 Wide outputs.** On ISA 0.8 a payload is at most 128 bits (G-15). The rule:
  - Outputs (return value plus `OUT` bytes) wider than 128 bits are split into k slices.
  - The marker lowers to a **permutation action** that calls k + 2 oracle variants:
    - variant `W_c` (payload 0, fault = code(x)) computes a clean fault copy;
    - each `W_j` (j ≥ 1) XORs its slice with a fresh fault bundle, which is then cleaned
      against the copy by `qxor`;
    - `W_0` XORs slice 0 and writes the caller's fault register;
    - `W_c` runs again to clean the copy.
  - All exact. The resulting interface equals NS F_B with a wide payload.
- **§8.7 In-place.**
  - `inplace(g, ginv, budget, desc)` with x bound `INOUT`.
  - Without other bindings, it lowers to ISA `qinplace @g @ginv tk x` (ISA §4.5).
  - With classical `ARG`s whose value sets are finite, it lowers to one `qinplace` per value,
    with each pair specialised.
  - With quantum `IN`, `MEM_IN` or unbounded `ARG`s, it needs BLK-3 (ISA-3: `qinplace` with
    `(ins..) (mem..) (args..)`).
  - **Library bijections** (bennett-arith adders, xor, rotate, modular add and multiply with
    their stated conditions) are permutation actions, not `qinplace`. They take quantum and
    classical parameters on ISA 0.8 directly (§10.5).
  - **Verification:**
    - exhaustive on the reference interpreter for N ≤ the configured width (default 24 bits,
      `-bennett-inplace-exhaustive-bits`);
    - above that, a `sampled` evidence claim (ISA §12.1), plus the dynamic net `T-CLEAN`
      (NS §3.1) (`.14`);
    - a pair that faults or is not inverse is `BD-E-INPLACE-NOT-INVERSE` (L: NS §3.1).

**Lowers to:**

- ISA §4.7 `oracle_call @o tk (ins..) tgt fr (mem..) (args..)`;
- §5.1 signatures;
- §7.2 mapped interface regions;
- §3.3 binding;
- §4.5 `qinplace`;
- §5.5 nesting (the variants of §8.6);
- §12.1 `sampled`.

**Reuses:** 0.1 §6.4 item 4 and §9.6 examples (`inc8` becomes a descriptor with one `IN`).
**Closes:** `.3` (BLK-3 part), `.6`, `.14`, `.17`, `.40`.

## §9 Budgets

**Content:**

- **§9.1 The budget record.** `struct bennett_budget { u64 steps, heap, stack, depth;
  bennett_q fault; }`.
  - The first four fields are ISA §5.4's: steps; heap bytes; lifted stack cells; call depth.
  - A field equal to `BENNETT_BUDGET_TABLE` (all ones) takes its value from §9.2.
  - `fault` is meaningful only for action regions. It names the caller's fault register (F = 4
    wires) that receives the combined fault of the region's coherent slices (TDL-8), or null.
  - A null record means all four budget fields come from the table and `fault` is null.
  - For `oracle`/`inplace`, `fault` is ignored: the descriptor names it.
- **§9.2 Out-of-band budget table** (driver input, `--bennett-budgets=<file>`, JCS JSON):
  - Entries are keyed by region identity (§7.3 hash, or region key) or by a symbol-name
    pattern, which the driver resolves to identities and records.
  - Entries hold (steps, heap, stack, depth, sstack), where `sstack` is the shadow-stack bytes,
    a part of `heap` (§17.3).
  - Project defaults per component come from `--bennett-budget-default=<s,h,st,d>`.
  - The table hash is recorded in the certificate.
- **§9.3 Which budget governs what:**
  - oracle and in-place: the token (ISA §5.4, §10 `bennett_budget`);
  - `ctrl`, `adj`, `compute`: every coherent slice's token (TDL-9);
  - `reversible`: an R-tier step, heap and depth counter (§17.6);
  - device CC code outside regions: unbudgeted (classical control is "genuinely dynamic",
    NS §4.2).
- **§9.4 Unit.** One reference-interpreter row of the reference body (ISA §14.1), heap bytes
  per `lift.alloc`, stack cells per `lift.call` (ISA §3.7 R_f), and depth (NS §4.2). The fault
  set is a property of program plus budget plus recorded versions.
- **§9.5 Run-time budgets.** Budget fields that are:
  - (a) constants, or value sets that are finite: pre-minted at launch and dispatched;
  - (b) bitwise copies of device-entry arguments (provenance §5): minted by the launch stub
    from the host value (ISA §10 `bennett_budget`, `TOKEN`);
  - (c) computed on the device (arithmetic on inputs, measurement results): need BLK-2 (ISA-1).

  Exhaustion is always F_B = (0, `FAULT_BUDGET_*`), never a compile error (NS §3.1).

**Lowers to:** ISA §5.4, §10 `bennett_budget`, `TOKEN` binding, `lift.alloc`/`lift.call` flags.
**Reuses:** 0.1 §6.5 first two bullets. **Closes:** `.2`, `.5`, `.20` (BLK-2 part), `.33`.

## §10 Taint-driven lifting under control (TDL; tdl 0.2)

The rules are fixed here (mechanism paragraph B4). Rule ids TDL-1 to TDL-12 are normative
anchors.

**Content:**

- **TDL-1 Interface vs body.** The marker fixes the interface:
  - `ctrl`, `adj` and `compute` give an action;
  - `oracle` and `inplace` give an oracle.

  The body is partitioned by content and never rejected for containing classical code.
- **TDL-2 Coherence states.**
  - Values: Cl ⊑ Co.
  - Abstract objects: a **static** may-Co set (§5) and a **dynamic** coherence bit per object
    instance, kept by the CC generation in the coherent allocator's bookkeeping.
  - **Seeds:**
    - marker results that are quantum (deferred measurement, §7.5a);
    - loads from objects whose dynamic bit is Co;
    - **application** of an event with a non-empty control set to an object's cells.

    The bit is set when the event is applied, not when it is recorded.
  - **Propagation:** data dependence; control dependence (a Co branch makes its dependent
    region Co); memory (a store of a Co value, or a store under Co control, makes the object
    Co).
  - Interprocedural and context-sensitive, with variants keyed by coherence signature (§4.3).
- **TDL-3 Partition.**
  - **G (generation):** Cl instructions that are not control-dependent on a Co branch. G runs
    once in CC (0.1 §8.4).
  - **Coherent slices:** every maximal SESE region of Co instructions is outlined
    (`CodeExtractor`) into an oracle O_k with this interface:
    - Cl live-ins → `args`;
    - Co live-ins → `ins`;
    - Co objects read → the arena region (`in`);
    - Co live-outs and the new contents of written Co bytes → `tgt` bundles.
  - Irreducible Co code is outlined as a whole function.
  - O_k is lifted by §16 like any oracle.
- **TDL-4 Coherent arena.**
  - Objects in the static may-Co set are placed in the arena: a static address range
    [A_coh, A_coh + 2^A) in the layout, disjoint from CC globals and heap (ISA §7.1/§7.2).
    G-13 would lift that restriction.
  - The arena's contents live in a CC-held `qreg[8·2^A]` bound as `region[A,8]` (ISA §3.3).
  - While an object's bit is Cl, CC reads and writes a **CC shadow** at a fixed offset. Writes
    to the shadow are mirrored by TDL-5 events.
  - Globals in the may-Co set are relocated into the arena by the layout (§19.5). Heap objects
    in the set are allocated by the runtimes' coherent allocator.
- **TDL-5 Stores to outliving objects in action regions (the store rule; B4).** A store
  executed in G or in a slice, to an object that outlives the invocation, is realised by
  cases:
  - **(a) Old contents Cl** (bit Cl at that point; the old bytes c are known to CC).
    - The event is `xmask o, c ⊕ v` for a classical v.
    - For a Co v, the event is a slice oracle that receives c as `args`, XORs v into a fresh
      target, then `qxor` into the arena slice, X-mask c, and re-runs the oracle to uncompute
      the target. The oracle's inputs are unchanged, so the uncompute is valid (ISA §6.2).
    - Exact. No history.
  - **(b) Old contents Co**, and the update is a **library bijection** in the old value with Cl
    or Co parameters (the bennett-arith table: add/sub of a value, xor, rotate, negate, bswap,
    modular add, modular multiply by a unit, with the stated conditions), or a declared
    `inplace` pair. It is realised as compute parameter → permutation action on the arena
    cells → uncompute parameter. Exact.
  - **(c) Old contents Co, inside the `f` part of `compute(f, use, env)`:** history kept. The
    displaced bytes move into history wires and are cleaned by adjoint(E_f) (Bennett;
    NS §3.1 compute-with-uncompute).
  - **(d) Otherwise:** `BD-E-COHERENT-OVERWRITE`. This is L, required by NS §4.2: "writing a
    register not known to be clean is a compile-time error … an in-place update x ← g(x)
    requires a total bijection with a bounded inverse … else it fails loud". The diagnostic
    names the store and the object. Open question E3 asks whether to add an opt-in
    history-output mode.
  - Stores to region-local objects are workspace (G runs them classically). They are released
    or restored at region exit.
- **TDL-6 Control and adjoint.**
  - `ctrl` adds the control wire to every event's control set (ISA §4.7 `ctl w`).
  - `oracle_call`, `qexch`, `qexchm`, X and `xmask` are self-adjoint (ISA §5.3 adjoint table).
  - adj(f) generates f from the current classical state and applies the adjoint event list.
  - compute reuses the recording E_f for its uncompute, so masks and history match exactly.
- **TDL-7 History.**
  - Displaced Co contents (case c), per-slice fault wires and dead Co temporaries live in
    declared mutable wires of the invocation.
  - They are freed by the scheduler (NS §3.1 garbage row) inside the window of ISA §6.2.
- **TDL-8 Faults.** NS §4.2: "a quantum action has no fault outcome of its own: any fallible
  computation it needs is a lifted oracle it calls, whose fault register it declares among its
  outputs". So:
  - A combine oracle XORs the first nonzero per-slice code into the action's declared fault
    register: the `fault` field of the budget record (§9.1).
  - When that field is null and the body has fallible slices, the plugin allocates the
    register itself.
    - It is retained like TDL-7 history.
    - It is released at program end by `measure` in a final CC epilogue, which also records
      the outcome into the run's fault statistics.
    - Its rate is reported in the certificate (`fault_rate`, ISA §12.3).
    - A nonzero rate is a reported quantity (NS §4.2), not an error.
- **TDL-9 Budget.** Each O_k token comes from the region-entry marker's budget record, or from the table entry (§9). Exhaustion is
  that slice's `FAULT_BUDGET_*` and reaches TDL-8. Open question E2 asks whether the budget is
  per slice or a total.
- **TDL-10 Co control of quantum operations.**
  - A marker call that is control-dependent on a Co branch, or has a Co index or op code:
    - a slice oracle computes the condition into a fresh wire;
    - the gate is issued under `qpred` once per candidate index and op code (ISA §3.5, §4.6);
    - the condition is uncomputed.
  - A Co rotation angle is predicated per value when its value set is finite. Otherwise it is
    `BD-E-COHERENT-ANGLE`: L, because NS promises predication, not superposed parameters, and
    ISA §3.1 "angles are literals or classical args".
  - A Co trip count of a gate-issuing loop is padded to the budget and unrolled in the event
    list, with per-iteration flags kept as history. G-14 is the efficient form.
- **TDL-11 After the region.**
  - Code that reads an object whose bit is Co, inside the closure of a later region entry, is
    part of that region's coherent slices.
  - Code outside any region that may read a Co object is compiled in two variants (Cl and Co
    signatures, §4.3), selected by the dynamic bit.
  - Its Co variant at host or CC level is `T-TAINT-HOST` at run time, and statically
    `BD-W-TAINT-HOST` (a warning naming `__bennett_observe`). The reason: NS §4.2, classical
    outputs leave only through measurement.
  - `__bennett_observe` makes bytes Cl by measurement.
- **TDL-12 Effects in Co context.** An effect reached in a Co slice follows §11.3 (coherent
  device models), else F(8) on the executions that reach it.

**Lowers to:**

- ISA §5.3 action body (`oracle_call`, `qexch`, `qexchm`, gates, `qpred`, `qalloc`/`qfree`);
- §4.7 `ctl`;
- §5.2 oracles;
- §3.3 region binding of the arena;
- §6 validity (case a re-run, case c adjoint);
- §4.6 `qexchm` for Co addresses.

**Reuses:** 0.1 §8.4 generation model (classical code runs once, events recorded), now with
store events.
**Closes:** `.1` (all of 1.4-d, D17, B-31, B-50, O-05), `.2` (ctrl part), `.31`.

## §11 Effects and device models per tier (effects 0.2)

**Content:**

- **§11.1 Tier table** (NS §4.2 effects table, made concrete):

  | Tier | Effect realisation |
  |---|---|
  | H | real |
  | CC | `hostcall` to host services (§11.4) |
  | R | ISA `effect` device models, on the tape |
  | L | lifted device-model state bound by §8.3 |
  | unmodelled | F(8) + `trapped` |

- **§11.2 Effect markers → R tier.**
  - `__bennett_effect_<dev>_<op>` lower to ISA `effect dev.op` (ISA §7.3, §4.1) with the
    operands in ISA order.
  - Validation failure is the ISA fault record.
  - `bennett-runtimes` musl maps syscalls onto them:
    - `write(1|2)` → console;
    - `clock_gettime`/`time` → clock;
    - `getrandom` and `/dev/urandom` → entropy;
    - block I/O → block;
    - files → a runtimes VFS over the block device or over a data-image file system.
  - Device models beyond the four: ISA §17 item 3, deferral of mechanics. New models arrive
    with an ISA version.
- **§11.3 Coherent tier (lifted device models).** The same markers, in L variants, lower to
  lifted code over bound state:
  - console: appends to a lifted buffer, discarded by prefix reversal, unless bound CONSOLE;
  - clock: a lifted counter initialised from CLOCK `value`;
  - entropy: reads from the ENTROPY `in` region, with a position counter; reading past its end
    is `fault 10` (`FAULT_ENTROPY_EXHAUSTED`). ISA §4.2 admits any `fault C` with C < 2^F. The
    "(R only)" label of ISA §5.4 is a §25 wording item;
  - block: reads the BLOCK `in` region, and writes go to a lifted overlay map in the heap.

  An unbound device read in L is F(8) (NS: "An effect the device cannot virtualise is a fault
  code on the executions that reach it").
- **§11.4 CC host calls.**
  - A CC variant's call to a host function (H tier only) becomes
    `hostcall bennett.call/<hash>`.
  - The argument block holds scalars and pointer-free byte ranges (§5 proves pointer-free).
  - Pointer-rich arguments trigger promotion (§19.4) instead, with ISA-11 as an efficiency
    item.
  - The service is declared in `devices.services` (ISA §9.1, §10).
- **§11.5 Fault codes reported from CC.** `__bennett_nz_fault(C)` in CC lowers to
  `hostcall bennett.fault` with payload C, then `trap`. This makes the code observable on
  ISA 0.8 despite ISA-7. In R it is `trap` (the code is unspecified until ISA-7; wording item).

**Lowers to:** ISA §7.3, §4.1 `effect`, §10 `hostcall`/tape, §7.2 regions, §5.4.
**Reuses:** none (0.1 had no effects). **Closes:** `.13`.

## §12 Materialised normalisation (norm 0.2)

**Content:**

- **§12.1 Scope and order.** As 0.1 §7.1: device variants, applied in table order. The native
  comparison build and the device both consume the materialised module (NS §3.2).
- **§12.2 Rules.**
  - N1–N16 and N19 as in 0.1.
  - N9 is kept, except that volatile accesses in platform-profile code route to §20.3.
  - **N17 is replaced** by §13: no FP F(8).
  - **N18 is replaced** by §4.5: shims first; trapped only without bitcode.
  - **N20 is replaced** by N24.
  - New rules, in this order after N16:

    | Id | Rule |
    |---|---|
    | N21 | **vector scalarisation**: every vector op becomes per-lane scalar ops in lane order; `vector.reduce.*` becomes a left fold in lane order (exact for FP once reassoc is stripped) |
    | N22 | **wide-integer legalisation**: iN with N > 128 becomes ⌈N/64⌉ i64 limbs with carry-chain expansions; non-byte-width loads and stores are widened to whole bytes with zero-extended stores, fixing LangRef's unspecified extra bits |
    | N23 | **varargs** (§14.3) |
    | N24 | **allocas → shadow stack** (§17.3), zero-filled; replaces N20 |
    | N25 | **byval**, `inalloca` and `preallocated` become explicit caller copies into the shadow stack; aggregate returns wider than 128 bits are demoted to a hidden out-pointer |
    | N26 | **memory intrinsics** become calls of `__bennett_rt_memmove`/`memset`/`memcmp` (runtimes bitcode); replaces N13 |
    | N27 | **integer intrinsics**: `*.with.overflow`, `*.sat`, `bswap`, `ctpop`, `ctlz`, `cttz`, `fshl`, `fshr`, `bitreverse`, `abs`, `min`/`max`, `scmp`/`ucmp` and the remaining generic integer intrinsics become fixed expansions; one table row per LangRef intrinsic |
    | N28 | **unwinding: explicit propagation** (§14.4) |
    | N29 | **setjmp/longjmp** (§14.5) |
    | N30 | **rewindable frames** (fibers, §14.6), only in the functions §14.6 selects |
    | N31 | **inline asm and target intrinsics** via the §15 table |
    | N32 | **FP**: soft-float (§13), after N21 |
    | N33 | **extended FP formats and libm intrinsics** (§13.3–13.4) |
    | N34 | **R-tier budget instrumentation hooks**: point marks only; counters are inserted in the R lowering (§17.6) |
    | N35 | **platform hooks** (§20): MMIO routing, interrupt poll points |

  - **Completeness obligation:** the editor enumerates every generic (target-independent)
    LangRef intrinsic of LLVM 18/20/23 with its row in N5–N35, §13 or §16. No generic
    intrinsic is `trapped`.
- **§12.3 Fault replacement F(C).** As 0.1 §7.1.
- **§12.4 Residual validator.** 0.1 V1–V12, updated:
  - V9/V10 are inverted: after N32/N33 no FP remains;
  - V4 adds the N26/N27 intrinsics;
  - V11 is replaced by the N24 shape;
  - new V13 (no vector type), V14 (no iN > 128), V15 (no `va_*`, `invoke`, `landingpad`,
    `resume`, setjmp calls), V16 (no inline asm).

  Two independent validators, as in 0.1.

**Lowers to:** (normaliser output is LLVM). **Reuses:** 0.1 §7.1–§7.2, §7.5, examples.
**Closes:** `.7` (with §16), `.15` (with §13), `.37` (with §14.3), `.12` (with §14.4).

## §13 Floating point (arith contract)

**Content:**

- **§13.1** The 0.1 §7.3 soft-float rewrite for binary32/binary64, kept verbatim: entry points,
  semantics, canonical NaN, bit-exact moves.
- **§13.2 Vector FP.** After N21 it is scalar FP: covered.
- **§13.3 Formats.**
  - `half` and `bfloat` are computed in binary32 and rounded to nearest-even. This is exact for
    + − × ÷ √ and fma-free paths, since 24 ≥ 2p + 2 for p = 11 and p = 8.
  - Conversions go through `__bennett_sf_{fpext,fptrunc}_*`.
  - `x86_fp80`, `fp128` and `ppc_fp128` use arith entry points `__bennett_sf_<op>_f80/_f128/_ppcf128`
    with the same table as §13.1. `ppc_fp128` is double-double, as LangRef defines it.
  - Each format is a contract row with rounding, NaN and conversion semantics.
- **§13.4 Transcendentals.**
  - `llvm.sin`, `cos`, `tan`, `exp`, `exp2`, `exp10`, `log`, `log2`, `log10`, `pow`, `powi`,
    `ldexp`, `frexp`, `asin`/`acos`/`atan`/`atan2`, `sinh`/`cosh`/`tanh` and the rest become
    calls of the **runtimes libm**: a musl-derived libm compiled through the pipeline with
    soft-float, hence one deterministic implementation in both builds.
  - libm calls in source resolve to the same functions (§4.5).
  - The certificate records the runtimes version.
  - No correct-rounding claim is required. Bit-exact determinism is (NS §3.2).
- **§13.5 Constrained intrinsics and `strictfp`.** `llvm.experimental.constrained.*` become
  soft-float with the dynamic rounding mode read from the runtimes fenv state. Exception flags
  are kept in that state.

**Lowers to:** lifted integer rows (ISA §4.2) and CC integer instructions (ISA §4.1). FP never
reaches the ISA except as `f64` rotation angles (ISA §3.1).
**Reuses:** 0.1 §7.3. **Closes:** `.15`.

## §14 Calls and control transfer

**Content:**

- **§14.1 Direct calls.**
  - CC/R `call` (ISA §4.1); lifted `lift.call`/`lift.ret` lprocs (ISA §3.7), with depth and
    stack faults.
  - Recursion is unrestricted, and budgeted by depth/stack (§9).
- **§14.2 Indirect calls** (R2):
  - **Candidate set:** the §5 value set of the callee, else every address-taken function whose
    LLVM function type equals the call's (sound for defined C/C++/Rust; SQLite §3).
  - The device closure includes every candidate.
  - **Dispatch:** a balanced compare tree over the sorted A(F_k) (construction of §16.4),
    leaves `icmp eq` + static `call @F_k` (CC/R) or `lift.icmp.eq` + `qbranch` + `lift.call`
    (L).
  - No match → F(4) (`FAULT_UB_TRAP`: a call through a pointer that is no function of the
    program is UB, or code without bitcode).
  - Zero candidates → F(4) at the site.
  - Calls through a variadic type use §14.3.
  - The same construction serves region operands (§7.2), handle-id dispatch (§6.5) and
    descriptor-shape dispatch (§8.4).
- **§14.3 Varargs (N23):**
  - A variadic definition `R f(P…, ...)` becomes `R f(P…, ptr %va)`.
  - A call site spills its variadic arguments (after default promotions) into a block on the
    shadow stack, in ABI order and alignment.
  - `llvm.va_start` builds the target's `va_list` so that the front end's inline `va_arg`
    takes the memory path:
    - x86-64 SysV: `gp_offset` = 48, `fp_offset` = 176, `overflow_arg_area` = the block,
      `reg_save_area` = null (SQLite §5.1);
    - AArch64 AAPCS64: `__gr_offs` = 0, `__vr_offs` = 0, `__stack` = the block;
    - RISC-V64: `va_list` = the block pointer.
  - IR `va_arg` is expanded by the same layout. `va_copy` copies the record; `va_end` does
    nothing.
  - A table row per supported target ABI. Adding a target adds a row: mechanics.
- **§14.4 Unwinding (N28, explicit propagation):**
  - The runtimes keep the EH state in a global: `__bennett_rt_eh` = {active flag, exception
    object, selector}.
  - `invoke` → `call`; then load the flag; branch to the landing pad if set.
  - A plain call of a may-unwind function inside a may-unwind function → call; check; return
    early with zero results if set.
  - `landingpad` → a call of `__bennett_rt_eh_match(obj, clause list)` that implements the
    personality's clause matching: catch typeinfo identity, filters, cleanup. The shim
    personalities cover `__gxx_personality_v0`, `rust_eh_personality` and `__gcc_personality_v0`.
  - `resume` → set the flag and return.
  - `__cxa_throw`, `_Unwind_RaiseException`, `__rust_start_panic` → runtimes implementations
    that set the flag.
  - Windows funclet pads (`catchswitch`/`catchpad`/`cleanuppad`) use the same transform (C7:
    corpus case needed, `-kdj`).
  - Unwinding out of an oracle region, an action region or an R entry → F(4) (NS §3.1: "a
    fault code where it is not [handled in the region]").
- **§14.5 setjmp/longjmp (N29, SjLj via propagation):**
  - `setjmp`/`_setjmp`/`sigsetjmp` call sites become block boundaries.
  - `__bennett_rt_setjmp(buf)` returns 0 and stores the frame token (shadow-stack frame
    address) in buf.
  - `longjmp(buf, v)` raises the longjmp pseudo-exception (buf, v, normalised v = 0 → 1).
  - Every function containing a setjmp has an implicit handler after each may-unwind call. On a
    longjmp whose buf token is this frame, it clears the flag and branches to the setjmp
    continuation with v.
  - This covers C longjmp to active frames (the only defined case) and Julia `jl_try`.
- **§14.6 Fibers and context switch (N30, rewindable frames):**
  - Functions on a call path to a switch primitive get Asyncify-style unwind/rewind
    instrumentation: locals spilled to shadow-stack frames, plus a resume index. Switch
    primitives are the runtimes' `swapcontext`/`makecontext`, Julia task switch, and the
    platform `swtch` shim of §20.
  - A switch unwinds the current fiber to its base, saving frames, and rewinds the target.
  - Works in CC, R and L on ISA 0.8. G-16 (ISA fibers) is the efficient alternative.
- **§14.7 `exit`, `abort`, `_Exit`:**
  - `abort` → F(4).
  - `exit(s)` raises the exit pseudo-exception. A region wrapper in "oracle from program" mode
    (§19.3) catches it, with s as payload. An R/CC whole-program entry catches it and returns
    s. Elsewhere it is an unwind out of the region → F(4).
- **§14.8 `switch`.** Lowered by §16.4, using the same tree as dispatch.

**Lowers to:**

- ISA §4.1 `call`/`ret`/`br`;
- §4.2 `lift.call`/`lift.ret`/`lift.icmp`/`qbranch`/`fault`;
- §3.7;
- memory rows for va blocks and frames.

`qjumpr` is intra-function only (ISA §4.2), so it is not used for calls.
**Reuses:** none. **Closes:** `.12`, `.35`, `.37`, `.39` (fibers, sjlj); `-kdj`.

## §15 Inline asm and target intrinsics (asm 0.2)

**Content:**

- **§15.1 Table format.** `spec/asm/<arch>.toml`, normative data, versioned `asm 0.2`. A row
  holds: the asm string normalised (whitespace collapsed, operand placeholders kept),
  constraint string, side-effect and clobber flags, class, replacement.
- **§15.2 Classes** (NS §3.3):
  - **lowered** (an IR replacement):
    - an empty asm with a `memory` clobber → nothing (a compiler barrier, single thread);
    - `pause`, `nop`, `yield`, `fence` → nothing;
    - `rdtsc`, `rdtime` → the clock model;
    - `cpuid` → a constant table of a declared CPU model;
  - **shimmed:**
    - `syscall`/`svc 0`/`ecall` → `__bennett_rt_syscall(nr, a0..a5)` (the runtimes syscall
      layer);
    - privileged forms → platform functions (§20);
  - **trapped:** every other row → F(8) + coverage line (L: NS §3.3 permits trapped asm).
- **§15.3 Module-level asm and assembly objects.** Symbols defined only by `module asm` or by
  non-bitcode `.S` objects resolve like externals (§4.5): runtime or platform shim by symbol
  and content hash, recorded in the certificate, else trapped.
- **§15.4 Target intrinsics** (`llvm.x86.*`, `llvm.aarch64.*`, `llvm.riscv.*`): the same table
  form. Rows required by the rungs are listed (part C).
- **§15.5 Required coverage for 0.2:**
  - the musl `__syscall0..6` asm for x86-64, aarch64 and riscv64 (rung 3);
  - the asm used by xv6-riscv and Linux `tinyconfig` riscv64 (rung 6/7, §20). Its exact row
    list comes from the platform spike (§20.7).

**Lowers to:** IR, then the ordinary rows. Shims are runtime bitcode.
**Reuses:** none. **Closes:** `.36`, `.39` (asm part).

## §16 The lifting map (map 0.2)

**Content:**

- **§16.1 Liftable means after §12, always.** Every materialised function is liftable.
  `BD-E-LIFT-SUBSET` is deleted.
- **§16.2 Objects produced.** One ISA object per device link, containing:
  - an **oracle wrapper** per oracle shape (§8.4), whose prologue:
    - binds IN to pseudo-locations, ARG to args and MEM_IN to `lift.addr @region`;
    - allocates OUT buffers and the shadow stack (§17.3) with `lift.alloc`;
    - runs the entry-state replay (§8.5);
    - then `lift.call @f`, `OUT`/return delivery and the truncation check;
    - `lift.retval`;
  - an **lproc per lifted function variant**;
  - `layout` (§19.5);
  - `data` images for all referenced globals, with function addresses encoded per §4.4.
- **§16.3 Names.** 0.1 §9.2 generalised per function:
  - locations `v<k>`, `c<j>` and `t<j>` per lproc;
  - lproc names `@L<n>` in depth-first preorder from the wrapper;
  - data symbols named by global index `@G<n>`;
  - block names as in 0.1.
- **§16.4 Rows** (0.1 §9.3 table, extended):
  - integer rows as in 0.1;
  - `getelementptr` → `lift.mul`/`lift.add` at pw width (wrap, N1 removed `inbounds`);
  - `ptrtoint`/`inttoptr`/`bitcast` of integers → `lift.mov` or casts;
  - `load T` → `lift.boundscheck p n` then `lift.load.iN` pieces of ≤ 128 bits, little-endian
    order, reassembled by shifts and ors;
  - `store` → `lift.boundscheck` then `lift.store` pieces;
  - aggregates in SSA → one location per field (flattened, in field order);
  - `alloca` is gone (N24);
  - `call` direct → `lift.call` with flattened arguments; results are one location of ≤ 128
    bits (N25 guarantees this);
  - indirect calls → §14.2 tree;
  - `ret` in an lproc → `lift.ret`; in the wrapper → `lift.retval`;
  - **`switch` → balanced compare tree:**
    - cases sorted unsigned;
    - node over the index range [lo, hi]: when hi − lo + 1 ≤ 3, an eq chain in order;
    - otherwise mid = ⌊(lo + hi)/2⌋, `t = lift.icmp.ult C k_mid`,
      `qbranch t ^left ^right`, with left [lo, mid−1] and right [mid, hi];
    - leaves fall through to default;
    - this replaces 0.1's linear chain (open question E6);
  - `unreachable` → `fault 4`;
  - `__bennett_nz_fault(C)` → `fault C`;
  - edge moves via `lift.parmov` as in 0.1.
- **§16.5 Header, hash, F_B.**
  - Reference-oracle signature: `in` = IN widths, `tgt`, F = 4, `mem` = MEM_IN, ENTROPY,
    BLOCK, the snapshot and the arena regions, `args` = ARG types in the §16.2 JCS spelling
    (the ISA-3 editorial item).
  - Hash per ISA §9.2.
  - F_B per ISA §5.2 with the four-component budget.
  - 0.1 §9.4–§9.6 generalised.

**Lowers to:** ISA §4.2 every row, §3.6–§3.7, §7.2, §9.1–§9.2, §16.2 grammar. Recursion is
`lift.call`; `qjumpr` is not used.
**Reuses:** 0.1 §9 (all examples, re-emitted with the wrapper form).
**Closes:** `.7`.

## §17 Device classical code: memory model, lowering, faults

**Content:**

- **§17.1 Memory model.** 0.1 §7.4 (live allocations, zero fill, address-model bounds, single
  thread), with one classical memory shared by H, CC, R and L entry state (§8.5).
- **§17.2 Layout.** The device layout replicates the comparison link (§19.5). CC and R use ISA
  §7.1 memory; L uses ISA §7.2.
- **§17.3 Shadow stack** (N24, NS §3.2 "where possible", which in device variants is always):
  - a runtimes block allocated by the region or entry prologue from the heap, of `sstack`
    bytes (§9.2);
  - frames are pushed and popped by `__bennett_rt_ss_{push,pop}` at function entry and exit,
    and on every early return of §14.4;
  - zero-filled;
  - overflow → F(2) `FAULT_BUDGET_HEAP`.

  Native stack addresses then never reach device results, which shrinks NS's layout-dependent
  class. The residue is host-stack addresses passed in by host code; 0.1 D12 was M and stays M.
- **§17.4 CC lowering.** LLVM to ISA CC (ISA §4.1): instruction table, block parameters for
  phis, `alloc`/`free` from the runtimes allocator, multi-result calls. It is
  plugin-constrained only by §18.7 (reference semantics). It is listed so that the
  CC-specific rules are explicit: handle-register environment (§6.5), dispatch (§14.2), and
  the `hostcall` of §11.4–11.5.
- **§17.5 Fault outcomes.** The 0.1 §7.4 table, plus:
  - indirect no-match (4);
  - shadow-stack overflow (2);
  - unwinding out of a region (4);
  - entropy exhaustion (10);
  - descriptor shape mismatch (4);
  - `T-TAINT-HOST` (4).
- **§17.6 R tier:**
  - The R lowering inserts a step counter: one step per executed materialised LLVM instruction
    other than phi, debug and the N34 marks. Heap bytes come from the allocator shim, depth
    from function entry. These define the R budget unit on the materialised module,
    independent of the plugin.
  - Exhaustion → `trap` (code per ISA-7 wording) and the run ends `FAILED`.
  - R faults end the run (ISA-8 wording item).

**Lowers to:** ISA §4.1, §7.1, §7.4, §10. **Reuses:** 0.1 §7.4, §7.6.
**Closes:** `.2` (R part), `.33`.

## §18 Reference semantics

**Content:**

- **§18.1 State.** Σ = (C, Q, H, G, K, T):
  - C: classical memory and environment;
  - Q: quantum state over live wires, including arena wires;
  - H: the handle table;
  - G: recorders;
  - K: the coherence bits (§10.2);
  - T: device-model state and tape.

  Superposed classical bytes are wires of the arena; C holds the Cl shadow.
- **§18.2 Events.** 0.1 §8.2, plus `xmask`, slice `oracle` events, `qexchm`, `observe` and
  `effect`.
- **§18.3 Marker rules.** The 0.1 §8.3 table, plus:
  - `oracle` with a descriptor (§8);
  - `observe`;
  - effect markers (R/L);
  - the budget record;
  - deferred `measure` (§7.5a).
- **§18.4 Generation.** 0.1 §8.4, plus TDL-3 to TDL-11. The classical part runs once; stores
  to outliving objects are events (TDL-5); slices are oracle events.
- **§18.5 Oracle semantics.** F_B of the reference body (§16) on the bound inputs and the
  entry state (§8.5).
- **§18.6 Reversible semantics.** R history plus tape (ISA §7.4). Whole-run reversal by ISA §10.
- **§18.7 Conformance.** As 0.1 §8.7: probabilities, classical observations, fault codes,
  traps, quantum state at measurement points. Layout-dependent comparison against the
  reference interpreter (NS §5.1). The four-way outcome table of NS §5.1 is stated.
- **§18.8 Worked examples.** The 0.1 ctrl/adj/compute examples, plus new ones:
  - ctrl with a Cl store (TDL-5a);
  - ctrl with a counter increment (TDL-5b);
  - compute with history (TDL-5c);
  - a reject (TDL-5d);
  - observe after ctrl.

**Lowers to:** ISA §14.1, §14.2, §7.4, §10. **Reuses:** 0.1 §8.
**Closes:** `.1` (semantics part).

## §19 The driver (driver 0.2)

**Content:**

- **§19.1 Pipeline position.**
  - 0.1 §11.1: post-link `lto<O3>`, then the plugin.
  - Bennett code never runs in pre-link phases (Enzyme PR 3211), except in the explicit
    closed-unit mode (§19.7).
  - The plugin links `bennett-runtimes` and `bennett-arith` bitcode of the link's major before
    S2.
- **§19.2 Mode `--bennett-tier=reversible --bennett-entry=<sym>`:**
  - The whole program is the device program in tier R.
  - A CC launch stub fetches argv/envp bytes with `hostcall bennett.argv`, then calls the R
    entry.
  - Effects use ISA device models (console, clock, entropy, block with `block_image` from
    `--bennett-disk=<file>`).
  - Un-run is `bennett_reverse` (ISA §10). Tape replay is deterministic from tape plus entropy.
  - This is the mode for rungs 3, 5, 6 (`.38`).
- **§19.3 Mode `--bennett-oracle=<sym>`** ("oracle from program"):
  - Synthesises the separate TU that a quantum programmer would write: a descriptor binding
    the named function's parameters (`--bennett-bind=<param>:<kind>:<width>`), device bindings
    (`--bennett-dev=entropy:in:<bits>`), and a payload (return value, exit status via §14.7,
    or a byte range of console output).
  - It is a convenience. The normative route is a separate TU with marker calls naming the
    unmodified function: rungs 4, 7, 8.
- **§19.4 Placement: host vs device CC.**
  - H functions stay native unless they share pointer-rich memory with device code. A pointer
    argument of a device-entry call whose pointee may contain pointers read by device code is
    pointer-rich.
  - Such host functions are **promoted** to CC variants up to their roots (in the limit
    `main`; then H is the syscall proxy only: `hostcall bennett.syscall`).
  - Results equal by the materialised semantics.
  - ISA-11 would let them stay native (efficiency/placement item, §25).
- **§19.5 Layout.** The comparison link fixes the bases of globals and functions (non-PIE,
  ICF and merging off, low base address so that 2^H covers it). The device `layout` (ISA §9.1)
  replicates it:
  - `heap_base` and `heap_limit_max` from the budget table maxima;
  - the arena (TDL-4) and interface regions placed above;
  - `H`, `A_tab` and `S_cells` derived;
  - the production host image linked with the same layout whenever A(F) may cross the boundary.
- **§19.6 Build-time snapshots** (`--bennett-snapshot=<dump>`): the driver rewrites the
  initialisers of mutable globals, plus the platform RAM global (§20), to the dump's bytes.
  The data images then carry the snapshot (rung 7, route "snapshot as images").
- **§19.7 Closed-unit mode** (`-bennett-closed-unit`, REPL fast path, NS §3.3):
  - The plugin runs on one module plus the runtimes and arith bitcode.
  - The **closedness check**:
    - every device function's callees have definitions in that set, or are trapped as in
      whole-program mode;
    - no device function's address escapes the module;
    - no function pointer enters through an entry parameter.
  - If the check passes, processing is identical to whole-program mode, hence the same
    semantics.
  - If it fails, the driver falls back to whole-program mode. It does not reject.
  - Objects are content-addressed (ISA §9.2) and linked at launch (ISA §9.3), so the REPL is
    incremental (`.34`).
- **§19.8 Mixed LLVM majors:**
  - The driver reads every bitcode input with the newest major M of the envelope (bitcode is
    readable by newer majors), links with M, and runs plugin M.
  - Runtimes and arith ship bitcode for each M.
  - Every input must have one target datalayout and triple (NS §3.2, one datalayout).
  - Inputs newer than M → `BD-E-VERSION` (tool version, L).
  - The tested pairs (front end, major) are published in the envelope. A new corpus case links
    clang 18 bitcode with Julia/rustc bitcode of another major (`.16`).
- **§19.9 Options, identity, outputs, module flag.**
  - 0.1 §11.3–§11.6.
  - New options: budgets, classes, modes, bindings, disk, snapshot, platform.
  - Identity string `dialect-0.2;isa-0.8`.
  - Outputs add the coverage of §4.5, §15 and §13 and the blocker reports (§25).

**Lowers to:**

- ISA §9 (objects, layout, linking);
- §10 (launch, stub, `hostcall`, reverse);
- §12.3 (`producer.materialisation`, bindings);
- §13.

**Reuses:** 0.1 §11. **Closes:** `.16`, `.34`, `.38`, `.5` (table input), `.22` (layout part).

## §20 Platform profile `riscv64-bennett-virt` (platform 0.2; rungs 6–7)

Mechanisms fixed here. Row-level contents follow a platform spike (§20.7). That spike is a
mechanics deferral; the capability is not in question (audit O-06).

**Content:**

- **§20.1 Model.** A virtual board with:
  - RAM as one runtimes global `__bennett_platform_ram` at the board's physical base;
  - a CSR file (privilege mode, `satp`, `stvec`/`mtvec`, `sstatus`, `sie`/`sip`, `scause`,
    `sepc`, `stval`, `mscratch` …) as a runtimes global;
  - devices: UART 16550 (→ console), CLINT and timer (→ clock), PLIC, virtio-blk MMIO (→ block).
- **§20.2 asm rows** (§15): `csrr`/`csrw`/`csrs`/`csrc`, `sfence.vma`, `wfi`, `ecall`, `mret`,
  `sret`, `fence.i`, MMIO-load/store asm forms → platform functions.
- **§20.3 MMIO routing.**
  - N9 plus N35: volatile loads and stores, and the MMIO asm forms, become
    `__bennett_rt_mmio_{load,store}_iN(addr[, v])`.
  - Those dispatch by address range to device-model handlers (C code in runtimes calling the
    effect markers), else to memory.
  - A non-volatile access to an MMIO window is outside every live allocation → F(7), as the
    reference semantics defines.
- **§20.4 Interrupts.**
  - Poll points at loop back edges and function entries (N35) call `__bennett_rt_poll()`.
  - The poll checks the timer model (deterministic, from the clock) and PLIC pending bits.
  - On delivery it sets the CSRs and calls the trap vector `stvec` by A(F) dispatch (§14.2).
- **§20.5 Context switch and traps.** Assembly entry points (`swtch`, `trampoline`, `uservec`,
  `kernelvec`, Linux `__switch_to`, `handle_exception`) are platform shims by symbol (§15.3).
  They are written in C over §14.6 fibers.
- **§20.6 User processes.**
  - User programs are built to bitcode and linked into the device program under the
    comparison layout.
  - Their ELF images on the disk image are the same link, so entry and function addresses are
    A(F).
  - `exec` and `sret` to user mode dispatch the user entry by A(F).
  - User loads and stores go through a soft-MMU: N35 instrumentation of user-compartment
    functions with a Sv39 walk over the modelled `satp`.
- **§20.7 Platform spike (mechanics).** Build xv6-riscv and Linux `tinyconfig` riscv64
  (UP, `CONFIG_SMP=n`) to bitcode with build flags only. Inventory every asm form, `.S`
  symbol, MMIO site and switch path, like SQLite §3. Fix the row lists of §20.2 and §20.5.

**Lowers to:** CC/R (ISA §4.1, §7.3 devices through the effect markers) and lifted code for
rung 7 (§11.3). **Reuses:** none. **Closes:** `.39`.

## §21 Legality corpus and conformance suites (corpus 0.2)

**Content:**

- **§21.1** The 0.1 §10 corpus, harness checks and envelope, with these updates:
  - L4 relaxed to content identity (`-cjb`);
  - P4 clang `-flto` end to end rerun, plus a rustc `-Clinker-plugin-lto` case (`-j88`);
  - harness and trace runtime updated to ABI 0.2 (`-566`);
  - P3-only interactions minimised (`-ape`);
  - `-g` variants (`-u6a`);
  - Windows funclet and non-x86-64 cases (`-kdj`).
- **§21.2 New legality cases:**
  - descriptor construction by constant stores (C, Rust, Julia), surviving O3;
  - the budget record;
  - effect markers;
  - `observe`;
  - a cross-major link;
  - region pointers from host input and `@cfunction`;
  - handle `Vec`/`std::vector`/linked lists;
  - EH, sjlj and varargs through the pipeline.
- **§21.3 Suites:**
  - the 0.1 suites DA, DB, DC, DN, DM, DS, DL;
  - **DT** (TDL partitions and events);
  - **DE** (effects R/L);
  - **DV** (varargs, EH, sjlj, fibers);
  - **DR/DF** (runtimes and arith contract vectors);
  - **DD** (driver modes, closed-unit equivalence, mixed majors);
  - **DP** (platform);
  - **DX** (rung-mini end-to-end programs, part D).

**Closes:** `-566`, `-j88`, `-cjb`, `-ape`, `-u6a`, `-kdj` (as work items the text assigns).

## §22 Diagnostics

**Content:** two tables.

- **Compile-time:** columns code, rule, **NS clause or decision that requires it**. A row with
  no such justification may not exist. The surviving rejections:
  - `BD-E-MARKER-*`, `BD-E-JULIA-CCALL`, `BD-E-EFFECT-LIE`, `BD-E-VERSION`;
  - `BD-E-OPERAND` (constant outside table);
  - `BD-E-HANDLE-USE` (decision 2), `-ESCAPE` (host-readable only), `-UNTRACKED`;
  - `BD-E-REGION-MEASURE` (unless defer), `BD-E-REVERSIBLE-MEASURE`;
  - `BD-E-REGION-*` for a unique ill-formed candidate;
  - `BD-E-RESIDUAL`;
  - `BD-E-INPLACE-NOT-INVERSE`;
  - `BD-E-COHERENT-OVERWRITE`, `BD-E-COHERENT-ANGLE`.

  Deleted: `BD-E-EH`, `-LIFT-SUBSET`, `-DEVICE-ADDRESS`, `-REGION-UNBOUNDED`/`-EXTERNAL`,
  `-REGION-TIER`, `-REVERSIBLE-MARKER` (except measure), `-INPLACE-UNVERIFIED`,
  `-OPERAND-UNBOUNDED`, `-HANDLE-STORE`, `-REGION-TYPE` for oracles.
- **Blocker reports** `BD-B-ISA1`, `-ISA3`, `-ISA4`, `-ISA12`, with the program point and
  value.
- **Run-time traps:** the 0.1 list, plus `T-OP`, `T-CLASS`, `T-IFACE`, `T-REGION-INVALID` and
  `T-TAINT-HOST`. `T-BORROW` is deleted.
- **Warnings:** `BD-W-QSTORE-UNCLEAN`, `BD-W-TAINT-HOST`.

**Closes:** `.9` (`T-BORROW` deleted; qborrow outside generations = clean allocation, ISA-9
efficiency).

## §23 Versioning

**Content:**

- Dialect 0.2 with sub-artefacts `markers`, `handles`, `regions`, `oracle-abi`, `tdl`,
  `effects`, `norm`, `map`, `asm`, `platform`, `driver`, `corpus`, all at 0.2, targeting
  ISA 0.8.
- The certificate records `normaliser_version`, `dialect_mapping_version`, runtimes, arith and
  asm-table hashes, and the budget-table hash.
- `SPEC_VERSIONS.toml` is updated.

**Reuses:** 0.1 §13.

## §24 Deferred mechanics (with defaults)

**Content:** only mechanics may appear. Each row states the capability it keeps. They are:

- the binary layout of descriptors beyond the C view (default: the C view under the datalayout);
- ThinLTO (default: full LTO merge; D23, M);
- the shadow-stack default size (default 64 KiB, from the table);
- the in-place exhaustive width (default 24);
- region-key stability across majors (D13, M);
- the layout base (D15, M);
- concurrency (D24, M; NS §9.11);
- diagnostic text and file names (D22, M);
- extra device models (ISA §17 item 3);
- target ABI rows for va_list and asm beyond x86-64, aarch64 and riscv64 (default: added with
  the target);
- the platform row lists (default: from the §20.7 spike).

**Closes:** none (it is a guard: the editor must not add a capability default here).

## §25 Blockers and ISA items

**Content:** the exact list in part B, paragraph B-BLK. Blockers (capabilities with no ISA 0.8
realisation in the stated case) are BLK-1 to BLK-4. Then wording items (ISA-7, ISA-8, the
ISA-3 JCS spelling, the `qreg.slice` lo operand) and efficiency items (ISA-2 note, ISA-5,
ISA-9, ISA-11, G-12 to G-16, SQLite E1 to E5). Each entry gives: the NS capability, the
programs affected, the ISA 0.8 realisation that does exist, the exact ISA change, and the rungs
affected (none).

**Closes:** `.3`, `.19`, `.20`, `.32` (blocker parts).

---

# Part B. Mechanism decisions

One paragraph per decision. Each says what the outline commits to, the alternatives
considered, and why they were rejected.

**B1. The lifted subset is all of materialised LLVM.**

*Decision.* Nothing is outside the subset. Normalisation (§12) legalises every construct into
integer SSA, memory, calls and branches. The map (§16) gives every such construct an ISA 0.8
row:

| Construct | ISA realisation |
|---|---|
| memory | `lift.boundscheck` plus `lift.load`/`lift.store` in pieces of at most 128 bits |
| globals | data images and `lift.addr` |
| heap | the runtimes allocator over `lift.alloc`/`lift.free`, with heap budget faults (ISA §4.2, §7.2) |
| allocas | the shadow stack (B16) |
| direct calls and recursion | `lift.call`/`lift.ret` lprocs, with depth and stack faults (ISA §3.7) |
| indirect calls | B3 |
| integer intrinsics | fixed expansions (N27) |
| memcpy family | runtime lprocs (N26) |
| FP | soft-float lprocs (§13); `half`/`bfloat` via binary32; `x86_fp80`/`fp128` via arith; transcendentals via the runtimes libm, so the same code runs in both builds |
| vectors | per-lane scalarisation (N21) |
| integers wider than 128 bits | limbs (N22) |
| aggregates | per-field locations |
| varargs | memory blocks with a forced-memory-path `va_list` (N23) |
| `switch` | a balanced compare tree (§16.4) |

The budget unit stays one reference-interpreter row of the reference body.

*Alternatives rejected:*

- **Keep a subset and extend it per rung.** That is what 0.1 D4 did, and it was rejected. It
  makes the checker the scope.
- **Lift through an ISA interpreter of LLVM IR** (one generic "LLVM step" lproc). It gives an
  index space independent of the program, but multiplies B by about 100 and removes the
  structure the specialiser recovers (SQLite §7).
- **Inline-expand memcpy and switch.** Rejected for the reference body. A runtime call keeps
  the reference body and its hash small and deterministic, and executors may inline
  extensionally (ISA §5.7, T6).
- **lift.alloc per stack frame.** Rejected: storage is never reclaimed (ISA §7.1), so
  cumulative heap would grow with every call (SQLite: 3,176 calls per oracle call).

**B2. The oracle interface descriptor.**

*Decision.* The descriptor is an in-memory record built by the front end (constant stores; a C
macro; Rust/Julia structs). It is passed as `__bennett_oracle(f, budget, desc)`. It binds every
IR parameter of an arbitrary region function to one of:

- `IN`: an input register, zero- or sign-extended;
- `ARG`: a classical value;
- `MEM_IN`: a `ptr` parameter that receives `lift.addr` of an `in` interface region bound to a
  register;
- `OUT`: a `ptr` parameter that receives a fresh zeroed buffer, XORed into a register at exit;
- `INOUT`: the in-place register, `inplace` only.

The descriptor also names:

- device-model bindings: ENTROPY, BLOCK, CLOCK, CONSOLE (B6);
- the result target (`tgt`), with a fault-on-dropped-bits check when it is narrower than the
  result;
- the fault register.

Kinds are classical data. Their value sets (§5.3) select compiled signatures, and the finite
kind domain bounds them in every case. Wide outputs use the k + 2 variant construction of §8.6.
The oracle's view of classical memory is the caller's at entry (§8.5): constant globals are
images; mutable reachable objects use entry-state transfer by allocation replay (O-07), or
build-time snapshot images (§19.6).

SQLite route A is then exactly:

| Parameter | Binding |
|---|---|
| `img` | MEM_IN, `region[25,8]` |
| `len` | ARG |
| `rowid` | IN, 20 wires, ZEXT |
| result | `tgt`, 1 wire |

There is no entry state to transfer when the program does not initialise SQLite before the
oracle. When it does, the 12 KB of mutable globals transfer (SQLite C′).

*Alternatives rejected:*

- **Fixed per-kind markers** (`oracle1`, `oracle2`, …). They cannot express arbitrary arity.
- **Variadic marker.** Rejected: fixed signatures are the spike's evidence, the variadic probe
  `ctrl_v` was dropped, and Julia `llvmcall` makes variadic calls awkward.
- **Parameter attributes or annotations.** C cannot attach them to parameters reliably, and
  passes may drop them.
- **A constant-global interface table plus dynamic values passed separately.** It needs a
  second operand list anyway.
- **Packing every input into one register.** That is 0.1 D21, a narrowing.
- **Separate per-oracle globals that do not see host mutations** ("cold globals"). Rejected:
  this changes results relative to native whenever the host mutated state the oracle reads.

**B3. Function addresses and indirect-call dispatch.**

*Decision.* A(F) is F's address in the driver's comparison link (NS §3.2). It is the same in
host, CC, R and lifted code and in every data image. Each tier maps A(F) to its own variant:

- **Candidate sets:** the §5 value set, else exact-LLVM-function-type match over the
  address-taken functions of the linked program. This is sound for defined C, C++ and Rust:
  SQLite gives at most 99 candidates, typically 1 to 38.
- **Dispatch:** a balanced compare tree over the sorted A(F_k), with leaves that make a static
  call:
  - CC/R: `icmp`/`br`/`call @F_k` (ISA §4.1);
  - lifted: `lift.icmp.eq`/`qbranch`/`lift.call @F_k` (ISA §4.2). Cost: about 2⌈log₂k⌉ + 1
    rows.
- **No match:** F(4).
- **Reuse:** the same tree serves region operands (decision 3, B17), `switch`, handle-id
  dispatch and descriptor shapes.

*Alternatives rejected:*

- **A dense canonical function index** (0..k−1) as the encoding. It gives smaller compares,
  but every `ptrtoint`, comparison, hash or store of a function pointer would differ from
  native. Pointer values would then be layout-dependent outcomes everywhere (SQLite hashes and
  compares function pointers).
- **`qjumpr` across functions.** Illegal: ISA §4.2 limits `qjumpr` to the containing function.
- **Linear compare chains.** O(k) rows per call.
- **An ISA indirect-call row.** Efficiency item E3 for ISA 0.9, not needed.

**B4. Taint-driven lifting under `ctrl` (TDL), and the store rule.**

*Decision.* §10 TDL-1 to TDL-12. The audit's TDL-1 to TDL-10 are adopted with four
refinements:

1. **Coherence is per object instance and dynamic.** The CC generation keeps a Cl/Co bit, set
   when a controlled event is *applied*. The static may-Co set only places objects in the
   arena and selects variants.
2. **The store rule (TDL-5) has four cases.** For stores to outliving objects:
   - (a) old contents classical → masked XOR, with any Co value computed by a slice oracle and
     uncomputed by re-running it on unchanged inputs: exact, no history;
   - (b) old contents Co, and the update is a library bijection or declared pair → in place:
     exact;
   - (c) old contents Co, in the `f` part of `compute` → history, cleaned by adjoint(E_f);
   - (d) otherwise `BD-E-COHERENT-OVERWRITE`. This is L, because NS §4.2 states exactly this
     rule for classical code acting on quantum state that outlives a region.
3. **Every action region has a fault output** (TDL-8): the budget record's `fault` field or a
   plugin-allocated register.
4. **After exit** (TDL-11), Co memory reaches classical code only through
   `__bennett_observe`.

This removes the semantic bug the audit found in 0.1, where classical stores of a `ctrl` body
happened on both branches. It needs no ISA change: actions call oracles (ISA §5.3, §4.7).

*Alternatives rejected:*

- **0.1 generation-only semantics.** Wrong results under control.
- **Always keep history (audit TDL-7 as written).** Silently entangles garbage with the
  control, which degrades interference with no diagnostic. NS §4.2 forbids it outside
  compute/uncompute. Open question E3 offers it only as an explicit opt-in.
- **Lift the whole `ctrl` body as one oracle.** Actions are not oracles. Quantum operations
  with classical structure inside the body (indices, op codes, loops) need generation (audit
  §3.1).
- **An implicit measurement when Co memory is read classically.** It would change semantics
  silently.

**B5. Budgets.**

*Decision.* Four components (steps, heap, stack, depth) exactly as ISA §5.4. They come from an
in-source **budget record** (`ptr` operand on every region-entry marker; a null record or
all-ones fields mean "from the table"). The record also carries the action's fault register.
They are completed from an **out-of-band table** keyed by region identity or symbol pattern,
plus per-component project defaults (§9). The `ctrl`, `adj` and `compute` budgets govern every
coherent slice. The `reversible` budget is enforced by an R step counter whose unit is defined
on the materialised module, so it is plugin-independent. Run-time budgets work when they are
finite value sets (pre-minted) or bitwise copies of launch arguments (stub-minted). Budgets
computed on the device need BLK-2.

*Alternatives rejected:*

- **An `i64` steps operand plus table only** (0.1 shape). It cannot carry four components or
  the action fault register in source (open question E1).
- **Budgets per loop.** NS §3.1 says no per-loop annotation is ever required.
- **Round run-time budgets up to pre-minted powers of two.** Changes F_B: inputs between B and
  2^k steps would succeed instead of fault.

**B6. Effects and device models per tier.**

*Decision.*

| Tier | Effects |
|---|---|
| R | effect markers lower to ISA `effect` on console, clock, entropy and block (ISA §7.3), taped and reversed |
| L | the same markers' L variants operate on lifted state bound through the descriptor: console buffer, clock counter, ENTROPY and BLOCK `in` regions with a copy-on-write overlay |
| CC | host functions are reached by `hostcall` with pointer-free argument blocks; pointer-rich sharing promotes code instead (B7) |
| unmodelled | F(8), with a `trapped` coverage line, which NS permits |

The runtimes musl, the Julia shim and the platform map their syscalls onto the effect markers.
Programs are unmodified.

*Alternatives rejected:*

- **Effects as ordinary external calls resolved by name** (`write`, `getrandom`). Markers keep
  the positive legality requirement and recognition by name, and libc names vary.
- **Hostcall from R.** ISA §4.1 limits `hostcall` to CC, and it is not reversible.
- **Coherent effects by fault only.** That narrows rungs 4, 7 and 8 (audit D11).

**B7. Whole-program driver modes and placement.**

*Decision.* The driver has these modes:

- `--bennett-tier=reversible --bennett-entry=<sym>`: the whole program in R, with a CC stub
  that fetches argv by `hostcall`. Un-run is ISA §10 whole-run reversal. Rungs 3, 5, 6.
- `--bennett-oracle=<sym>`: a convenience that synthesises the quantum programmer's TU.
- Placement by **promotion**: host functions that share pointer-rich memory with device code
  become CC variants, down to a syscall proxy in the limit. Correct on ISA 0.8; ISA-11 is
  efficiency only.
- Build-time snapshots.

*Alternatives rejected:*

- **Copy-in/copy-out of pointer-rich host data.** Relocating pointers needs type information
  the IR does not have.
- **Wait for ISA-11.** Not needed for correctness.
- **Run rung 6 kernels inside a device-compiled emulator** (QEMU in R). Rejected as the
  primary route: the thesis is compiling the program, not interpreting it, and the budget
  grows about 100×. It is kept as an optional independent cross-check for rung 6 console
  output.

**B8. Inline asm classification.**

*Decision.* A normative per-architecture data table (`asm 0.2`) keyed by the normalised asm
string and constraints, with classes lowered, shimmed and trapped (NS §3.3). Rows required now:

- musl syscall asm for x86-64, aarch64 and riscv64;
- the riscv64 platform rows (§20, from the platform spike).

Module asm and `.S` symbols resolve as externals, to shims by symbol and hash. Target
intrinsics use the same table.

*Alternatives rejected:*

- **Binary-lift asm to IR** (a remill-style lifter). Large, and per-instruction semantics would
  then be unspecified by the dialect.
- **Trap all asm.** Narrows rungs 3, 6 and 7.
- **Require a source edit.** Forbidden: NS §0 "unmodified".

**B9. Exceptions, setjmp/longjmp, fibers.**

*Decision.* Three normaliser transforms valid in every tier and in the native comparison build:

1. **Explicit propagation** (N28). An EH-state global; `invoke` becomes call, check, branch;
   shim personalities for C++, Rust and C cleanup; unwinding out of a region is F(4), as NS
   §3.1 states.
2. **SjLj as propagation** (N29). longjmp is a pseudo-exception caught by the setjmp frame,
   identified by its shadow-stack frame token. This covers every defined C use and Julia's
   `jl_try`.
3. **Rewindable frames** (N30, Asyncify-style), only for functions on paths to switch
   primitives: swapcontext, Julia tasks, the kernel's `swtch`/`__switch_to` shims. Works on
   ISA 0.8; G-16 is efficiency.

*Alternatives rejected:*

- **Use LLVM's `WinEH`/`SjLjEHPrepare` lowering.** Target-specific and not semantics-defining.
- **A return-value unwind bit.** Overflows 128-bit results.
- **A CPS conversion of the whole program.** Far more invasive than Asyncify for the same
  capability.
- **Wait for G-16.** Not needed for correctness.

**B10. Polyvariant cloning.**

*Decision.* A variant is keyed by (function, tier, coherence signature). Code is cloned; data
never is (one classical memory). A(F) names every variant, and each tier's dispatch picks its
own. This replaces `BD-E-DEVICE-ADDRESS` and makes SQLite usable classically (host builds the
database) and coherently (the oracle) in one program.

*Alternatives rejected:*

- **Clone data per tier.** Divergent state, results that differ from native.
- **Forbid dual use.** That is 0.1 B-16, a narrowing.

**B11. Handle tables in memory, and what needs ISA-4.**

*Decision.*

- The dialect admits handles anywhere the points-to analysis tracks, except host-readable
  slots (L), with register ids as the in-memory representation (§6).
- On ISA 0.8, `qreg` values cannot be stored in memory (ISA §3.2–§3.3, §4.1). The plugin
  therefore lowers to **static register files**: one CC `qreg` variable per (root, instance
  index), threaded through device CC variants by register-environment passing, with
  marker operands dispatched by comparing ids.
- This realises every program whose allocation sites have a statically bounded number of
  live instances, and widths with bounded value sets.
- Run-time-unbounded instance counts (a `Vec` of handles pushed in a data-dependent loop) and
  unbounded widths are **BLK-1 (ISA-4)**: the capability cannot be expressed on 0.8 because
  dynamic SSA instances of a `qreg` name become unnameable and `qreg[n]` types are static.

*Alternatives rejected:*

- **A single pool register with run-time-offset slices.** Two simultaneous slices are illegal
  (ISA-5), whether `lo` may be a run-time value is unclear, and the pool size is static anyway.
- **A recursion spine holding one register per activation.** Unusable control structure.
- **Rejecting** (0.1). A narrowing.

**B12. REPL per-TU fast path.**

*Decision.* An explicit closed-unit mode. The plugin processes one module plus the runtimes
and arith bitcode exactly as a whole program, after a closedness check: callees are resolved,
no device address escapes, and no function pointer enters through an entry. When the check
fails, the driver falls back to whole-program mode instead of rejecting. Incrementality comes
from content-addressed ISA objects and linking (ISA §9.2–§9.3).

*Alternatives rejected:*

- **Run in pre-link phases unconditionally.** Enzyme PR 3211: it breaks LTO semantics.
- **A per-TU mode without the closedness check.** The semantics would then differ from
  whole-program mode, against NS "with the same semantics".

**B13. Mixed LLVM majors in one link.**

*Decision.* Read up: every input is read with the newest major M in the envelope, linked and
processed by plugin M. Runtimes and arith ship per-major bitcode. Datalayout and triple must
agree. Inputs newer than M are a tool-version error. The envelope of tested pairs is
published, with a cross-major corpus case.

*Alternatives rejected:*

- **Per-major partitions linked at the ISA level.** Taint and cloning need one module (NS §3.3).
- **Downgrading bitcode.** Unsupported by LLVM.

**B14. The oracle's entry state.**

*Decision.* The reference semantics is "the region function runs on a private copy of the
caller's classical memory". Its realisation on ISA 0.8:

1. images for constant globals;
2. **entry-state transfer**: the allocation-size replay reproduces CC heap addresses exactly
   (identical `alloc` rules, ISA §4.2/§7.1), then a byte copy from a snapshot `in` region
   filled by CC with 128-bit `args` chunks;
3. **build-time snapshot images** where the snapshot is known at link time (rung 7).

*Alternatives rejected:*

- **Oracles see only static images.** Wrong results whenever the host mutated state (0.1
  implicitly).
- **Wait for G-12.** Efficiency only.

**B15. One device analysis.**

*Decision.* One field-sensitive inclusion-based points-to and value-set fixpoint (§5) answers
every question that 0.1 answered with separate weaker analyses: handle provenance, region
candidates, indirect candidates, descriptor kinds, op-code and width sets, may-Co objects,
oracle read sets. Value sets are only a precision tool. Bounded domains fall back to the full
domain, never to rejection.

*Alternatives rejected:*

- **Per-question analyses** (0.1). Each one's imprecision became a rejection: B-24, B-27, B-33.
- **A context-sensitive (k-CFA) analysis.** Not needed for soundness, and costly at SQLite
  scale (1,218 functions).

**B16. The shadow stack.**

*Decision.* Every alloca of a device variant lives on a runtimes shadow stack, in both builds
(NS §3.2). The stack is one heap block per region or entry of `sstack` bytes, part of the heap
budget. Overflow is F(2).

*Alternatives rejected:*

- **`lift.alloc` per frame.** No reclamation (B1).
- **A dedicated layout global.** It needs a fifth budget component outside ISA §5.4 (open
  question E7).
- **Keep native stack allocas.** Layout-dependent results in device code.

**B17. Region candidates.**

*Decision.* Decision 3 with the type fallback: the candidate set is always bounded by the
program. Ill-formed candidates are compiled as trap bodies (`T-REGION-INVALID`) unless they are
the unique candidate. A region pointer with no matching function traps at run time.

*Alternatives rejected:*

- **Reject on ⊤** (0.1 C3/C4/C6). A narrowing: it covers callbacks, `std::function` and
  host-supplied region pointers.
- **Reject if any candidate is ill-formed.** Type-based sets are over-approximations, so this
  would reject correct programs (open question E14).

**B-BLK. Blockers and ISA items (the §25 list).**

*Capability blockers:* the capability is fully specified in the dialect, but on ISA 0.8 the
stated case has no realisation. No rung depends on any of them (part C).

| Id | NS capability | Affected case | ISA 0.8 realisation that exists | Exact ISA change |
|---|---|---|---|---|
| **BLK-1** = ISA-4 | NS §3.1 handle tables; §4.1/§4.2 dynamic allocation, "real allocation"; Bennett.jl vectors of qubits; adj of generations whose register set is known only at run time | allocation sites with a run-time-unbounded count of live registers; register widths with unbounded value sets | static register files plus dispatch (B11) | (i) dynamic-width type `qreg[*]`; `q = qreg.new cls n` with n an `i64` value yields `qreg[*]`; `w = qreg.width q`. (ii) Binding a `qreg[*]` to `wire[n]`/`region[A,W]` slots checks the width at the call: CC trap / R fault `FAULT_UB_TRAP` on mismatch. (iii) `id = qreg.id q` (non-consuming; the §10 launch id) and `q = qreg.from_id id` (yields `qreg[*]`; trap if the id is not live, is viewed, or is consumed). Frames: `qreg.id` is pure; `qreg.from_id` records the handle reference. |
| **BLK-2** = ISA-1 | NS §4.2 "run-time budgets come from the host or from measurement results" | budgets computed on the device (arithmetic on inputs, measurement-derived) | pre-minted finite sets; stub-minted copies of launch arguments | CC instruction `tk = budget.mint @region s h st d` (`i64` operands) with the ISA §5.4 validation (`bennett_budget`'s checks) as a CC trap; the token is scoped to the run; an impure frame recording the token. |
| **BLK-3** = ISA-3 | NS §3.1/§4.2 parametrised in-place updates `x ← g(x; y, a)` from a user-declared `(g, ginv)` pair with quantum or unbounded classical parameters | `inplace` with `IN`/`MEM_IN` bindings or unbounded `ARG`s | `qinplace` without parameters; per-value specialisation for finite `ARG` sets; library bijections as permutation actions (TDL-5b) | `qinplace @g @ginv tk x (ins..) (mem..) (args..)`. The §4.5 macro passes the lists to both `oracle_call`s. The §6.1 transfer becomes `x: perm with S_x ∪ ins ∪ cells(mem) ∪ Π`. Certificate obligation: g∘ginv = id for every (ins, mem, args) class (exhaustive or library). |
| **BLK-4** = new ISA-12 (audit B-38) | quantum allocation inside reversible-tier code | `qalloc`/`qfree` in an R closure when they cannot be hoisted to the CC caller (run-time count) | hoisting to CC with a static count | Permit `qreg.new`/`qreg.free`/`qreg.slice`/`qreg.concat` in R. The R history records them. Reversal of `qreg.new` is `qreg.free` with the cleanliness obligation (simulator check; hardware per ISA §17 item 14); reversal of `qreg.free` is `qreg.new` (clean). `measure` stays CC-only. |

*Wording items* (no capability lost; two implementations could differ until fixed):

- **ISA-7:** a table from CC/R trap cause to §5.4 code (div0 → 5, MIN/−1 → 6, memory → 7,
  `trap` → 4, alloc failure → 2), plus a CC/R `fault C` instruction. The dialect uses the
  `hostcall bennett.fault` workaround in CC meanwhile (§11.5).
- **ISA-8:** an R call returns a fault status to its CC caller, and runs ending in an R fault
  are reverse-eligible.
- **ISA-3 editorial:** the JCS spelling of `args` types, using the §16.2 type spelling as JSON
  strings.
- **`qreg.slice`:** clarify whether `lo` may be a run-time value.
- **ISA §5.4:** code 10's "(R only)" label versus `fault 10` in oracles (§11.3).

*Efficiency items* (correct on ISA 0.8 by the stated construction; ISA 0.9 candidates on
evidence only):

| Item | Construction on ISA 0.8 |
|---|---|
| ISA-5 | per-wire registers, or a quantum-addressed gate |
| ISA-9 | clean allocation for CC-spanning borrows |
| ISA-11 | promotion (B7) |
| G-12 | entry-state transfer (B14) |
| G-13 | static arena |
| G-14 | unrolled padded events, TDL-10 |
| G-15 | k + 2 variants, §8.6 |
| G-16 | rewindable frames, B9 |
| SQLite E1–E5 | cell width, frame width, indirect-call row, block-copy row, classical-content hint |

ISA-2 is not a gap (R instrumentation, §17.6). ISA-6 is not a gap. ISA-10 is settled by the
vectors.

*LLVM changes needed:* none. The legality findings' LLVM bugs (Attributor, IRNormalizer,
unprepared structurizecfg) are outside the supported envelope (0.1 D20, L).

---

# Part C. Rung-by-rung scope check (NS §8)

Every capability each rung needs, and the 0.2 section or mechanism that provides it.
Blockers: **none for any rung**. BLK-1 to BLK-4 affect no rung, and the efficiency items
affect cost only. Work outside the dialect (runtimes, arith, vm, circuits, estimate) is named
where the rung depends on it. It is not a dialect gap.

| Rung | Capability needed | 0.2 provides it by | ISA 0.8 | Blocker |
|---|---|---|---|---|
| **1** Scalar C, Rust, Julia | markers emitted by clang, rustc and Julia (`llvmcall`) | §3.8 | – | none |
| | multi-argument functions as oracles, no packing wrapper | §8 descriptor: one `IN` per parameter | §4.7 `(ins..)` | |
| | calls left after O3 (helpers, Rust panic paths for `/` `%`, Julia `throw`) | §14.1 lprocs; §4.5 runtime shims for `core::panicking::*` and `jl_throw`; §14.4 unwinding out of the region → F(4) | §3.7, §4.2 | |
| | integer intrinsics (overflow checks, min/max/abs) | N27 | §4.2 | |
| | exhaustive Int8 over D (x, t, e), both executors equal to native | §16 reference body; native comparison build §17/0.1 §7.6; part D | §5.2, §14.1, T3 | |
| **2** Pointers, structs, byte memory (C hashtable) | loads, stores, GEPs, globals | §16.4, data images §16.2 | §4.2 load/store/boundscheck/addr, §7.2 | none |
| | malloc/free, structs by value, memcpy/memset | runtimes allocator over `lift.alloc`/`lift.free`; N25; N26 | §4.2 alloc/free, §7.2 | |
| | allocas | shadow stack (§17.3, B16) | §4.2 | |
| | heap, stack and depth budgets | §9 record and table | §5.4 | |
| | result buffers out of the oracle | `OUT` binding (§8.2) | §5.2 contract | |
| | host-built table queried by the oracle | entry-state transfer (§8.5) | §3.7 initial state, §4.2 alloc | |
| | "reversed byte-exactly, both executors" | oracle prefix reversal, or whole-program R mode with `bennett_reverse` (§19.2) | §5.2 (4), §10 | |
| **3** musl hello world | whole program in the reversible tier | §19.2 mode | §3.1 R, §10 `bennett_run` | none |
| | musl as runtime bitcode; syscalls → device models | §4.5 shims; §11.2 effect markers | §7.3 `console` | |
| | stock musl `__syscall` inline asm | §15 table rows (x86-64, aarch64, riscv64) | – | |
| | `printf` varargs | N23 (§14.3) | memory rows | |
| | `fmt_fp` long double (static closure) | §13.3 `x86_fp80` arith | integer rows | |
| | argv; `exit` | CC stub `hostcall bennett.argv`; §14.7 | §10 `hostcall` | |
| | un-run to reset; tape replay deterministic | whole-run reversal; tape | §7.4, §10, T4 | |
| **4** Grover over unmodified SQLite | the whole closure lifted (1,218 functions, 262k instructions) | B1 / §12 / §16 | §4.2 all rows, §3.6–§3.7 | none |
| | database as a file image in quantum-addressed memory; rowid superposed; classical length | §8.2 `MEM_IN` (`region[25,8]`), `IN` (20 wires, ZEXT), `ARG`; SQLite route A | §5.1, §7.2, §3.3 binding | |
| | 2,229 indirect-call sites (VFS, pcache, SQL functions, walkers) | §14.2 + A(F) in data images (§4.4) | compare + `lift.call` | |
| | 952 variadic call sites | N23 | memory rows | |
| | about 1,000 vector instructions; 32 `vector.reduce` | N21 | integer rows | |
| | FP in 75 functions | §13.1 | integer rows | |
| | 453 relaxed atomics | N9 | plain load/store | |
| | memcpy family | N26 | `lift.call` | |
| | intrinsics: bswap, fshl, ctpop, ctlz, min/max, abs | N27 | | |
| | `switch` with up to 345 cases | §16.4 tree | `qbranch` | |
| | recursion (SCCs of 69, depth 21) | §14.1 | §3.7 depth/stack | |
| | heap 182 KB; budget table | §9 | §5.4 | |
| | SQLite used on the host (build the DB) and in the oracle | §4.3 polyvariant cloning | – | |
| | libc string functions, `localtime`; OS layer VFS with deterministic random and clock | §4.5 runtimes shims | – | |
| | error path → fault | user wrapper `__builtin_trap` → N11 F(4) | §5.4 | |
| | build flags recorded in the certificate | §19.9 / ISA §12.3 `producer` | §12.3 | |
| | (a) exhaustive oracle check at N ≤ 2^10, fault rate zero | part D + `bennett-conformance` | §12.1 `exhaustive` | |
| | (b) Grover with branch enumeration | vm (outside the dialect) | §4.2 executors | |
| | (c) estimate at 2^20 | vm/circuits structure recovery (SQLite work item 9), estimate (outside the dialect); the dialect supplies the reference body and certificate | §5.7, §12 | |
| **5** Julia on a shim runtime | Julia emission | §3.8 `llvmcall` | – | none |
| | Julia's LLVM major mixed with runtimes bitcode | §19.8 read-up | – | |
| | shim runtime as bitcode; `jl_gc_alloc` as allocation sites | §4.5, §5.1 | – | |
| | generic dispatch through function pointers | §14.2 | compare + call | |
| | exceptions via `sigsetjmp` (`jl_try`) | §14.5 | – | |
| | tasks, if reached | §14.6 fibers | – | |
| | `push!`/`Dict` (memmove, hashing, possibly FP) | N26, N27, §13 | – | |
| | forward equal to native Julia; reversal exact | §19.2 R mode; whole-run reversal | §10 | |
| **6** xv6, Linux `tinyconfig` | kernel built to bitcode for a modelled board, build flags only | §20 platform profile (riscv64, open question E4) + §20.7 spike (mechanics) | – | none |
| | privileged asm, `.S` entry and switch code | §15 rows, §15.3 symbol shims, §20.2, §20.5 | – | |
| | MMIO devices (UART, timer, virtio-blk) | §20.3 routing to device models | §7.3 console/clock/block | |
| | interrupts | §20.4 poll points | – | |
| | context switch | §14.6 rewindable frames | – | |
| | user programs, `exec` | §20.6 (A(F) dispatch, soft-MMU) | – | |
| | console output equal to a native QEMU run | §19.2 tape; independent QEMU run (conformance) | §10 tape | |
| | un-boot to the reset vector; tape replay byte-identical | whole-run reversal | §7.4, §10 | |
| | uniprocessor | NS §3.2 single-thread assumption (D24, M) | – | |
| | efficiency | G-16 optional | – | |
| **7** Quantum fuzzing of the kernel | oracle over syscall arguments (superposed, small space) | quantum programmer's TU: §8 descriptor with `IN` bindings on a harness that calls the kernel's syscall entry; or §19.3 | §4.7 | none |
| | kernel snapshot fixed classically after boot | §19.6 build-time snapshot images (no transfer), or §8.5 entry-state transfer | §9.1 data, §7.2 | |
| | devices virtualised in the coherent tier | §11.3 lifted device models | §7.2 regions | |
| | panic flag as the payload | platform `panic` shim raises the exit pseudo-exception (§14.7), caught by the wrapper → payload bit | §5.2 | |
| | the whole kernel lifted (including platform and fiber code) | B1, B9, §20 L variants | §4.2 | |
| | step budget | §9 | §5.4 | |
| | (a) against native execution of the same snapshot | native comparison build with the same images (§17, §19.6) | – | |
| | (b), (c) | vm / estimate | – | |
| | efficiency | G-12 only for run-time snapshots | – | |
| **8** Amplitude estimation on a plain-C Monte Carlo | unmodified program as the oracle | quantum programmer's TU naming the function (§8), or §19.3 | §4.7 | none |
| | entropy device replaced by a superposed register | §8.3 ENTROPY binding, §11.3 lifted entropy reading the `in` region (`rand`/`getrandom` → runtimes → effect marker L variant) | §5.1 `in` region, §5.2 domain D | |
| | double-precision maths and transcendentals | §13.1, §13.4 runtimes libm | integer rows | |
| | vectorised FP loops | N21 | | |
| | `printf` | N23 + console buffer discarded or bound | | |
| | payload from return or exit status | §8.2 `tgt`, §14.7 | | |
| | budget table | §9 | | |
| | (a), (b), (c) | part D, vm, estimate | §12 | |

---

# Part D. Pre-flight checking plan (`scripts/dialect_check.py` for 0.2)

**Principle.** The spec's scope comes from the north star and part B. The checker serves the
spec and never bounds it. Normative process rules, written into the spec's §1.5 and
`spec/README.md`:

- **P-1.** Every mechanism rule id (S-steps, N-rules, TDL-n, map rows, B/P rules, §8 kinds, §14
  transforms, §15 rows) has at least one checked `accept` example. Every L rejection has one
  `reject` example. Every blocker has one `blocked` example. The checker derives this index
  from the spec text: rule ids in bold anchors. A rule with no example fails the check.
- **P-2.** An example that the checker cannot yet execute **fails** (`checker-unimplemented:
  <what>`). It is never skipped, and the spec never removes or weakens an example to make the
  checker pass. The freeze gate is all green.
- **P-3.** Every executed result comes from an independent executor: LLVM tools, clang-built
  native binaries, or the Rust ISA reference interpreter. Python computes only *expected*
  artefacts: recogniser verdicts, normaliser output, map output, TDL events. It is never both
  producer and judge of the same example.

**D1. Layers and executors.**

| Layer | What runs | Executor |
|---|---|---|
| Parse and verify | every `llvm` block on LLVM 18, 20, 23 (`llvm-as` + `opt -passes=verify`), headless (CLAUDE.md rule 11: `env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER TMPDIR=<job dir>`) | LLVM |
| C, Rust, Julia examples | `clang -O2 -flto` (18, 20, 23), `rustc --emit=llvm-bc`, Julia `code_llvm`, then `lto<O3>` | toolchains of `corpus/legality/toolchains.toml` |
| Recogniser and validator verdicts | the Python reference recogniser (seed of the independent `bennett-conformance` one) | Python (expected only) |
| Normalisation | Python normaliser output compared line by line with `normalise-out`; then **native differential**: input and output modules compiled with clang and the spec seeds (D4) and run on the example's input vectors; results must be equal except where the normaliser's documented choices apply (undef → 0, F(C)) | clang native |
| Map | Python map output compared with `isa object=`; the ISA text checked by `bennett-isa-ref check` (well-formedness, hashes, ISA §9.2 identities) | Rust interpreter |
| F_B | `bennett-isa-ref run-oracle <obj> <oracle> --input … --budget s,h,st,d --mem r=hex --arg …` for every `text run=` line: memory, lprocs, recursion, alloc/free, indirect dispatch, varargs, soft-float, EH, sjlj, fibers in lifted code | Rust interpreter (exists today) |
| Prefix reversal | `bennett-isa-ref step-check --exhaustive` over D (≤ 24 bits) for every lifted example small enough | Rust interpreter (exists today) |
| Native vs reference | for every `run=` example, the materialised module compiled natively with seeds; payloads compared input by input: "equals native, or is flagged" (NS §5.1) | clang + Rust interpreter |
| CC/R programs | effect markers, whole-program R mode, reversal, tape: `cc-run=` blocks | Rust interpreter: **needs CLI `run-cc`** (D3) |
| Actions and TDL | event lists from the Python TDL reference, executed as ISA actions | Rust interpreter: **needs CLI `run-action`/`simulate`** (D3); until then the 0.1 Python simulator may compute expected states only, and the result is marked pending → fail (P-2) |
| Rung-mini programs (suite DX) | end to end: C source → driver steps → ISA object → interpreter run → native comparison | all of the above |

**D2. Checked examples 0.2 adds.** At least one per row:

- **lifted memory** (struct sum over an `in` region; a 3-node linked list built with
  `malloc`/`free` in the oracle; heap fault at a small heap budget);
- **recursion** (0.1-style `sum_db` from C, depth fault);
- **indirect calls** (qsort-style comparator from a table; zero-candidate trap; region pointer
  from host input → dispatch);
- **varargs** (`sum(int n, ...)`);
- **vectors** (`<4 x i32>` add and reduce);
- **wide int** (i256 add);
- **soft-float** (`fadd` in an oracle; a libm `exp` via the seed libm);
- **EH** (C++ throw caught inside the oracle; Rust panic → F(4));
- **sjlj** (longjmp across two frames);
- **fiber** (swapcontext ping-pong in R);
- **descriptor shapes** (multi-`IN`, `MEM_IN`, `OUT` with 160-bit output → k + 2 variants);
- **entry-state transfer** (a host-mutated global read by an oracle);
- **budget record and table**;
- **TDL** (cases a–d; a Co-dependent gate; `observe`);
- **effects** (console in R with reversal; ENTROPY-bound oracle);
- **deferred measurement**;
- **handle table** of fixed size; `Vec<Handle>` with a static bound; unbounded → blocked;
- **closed-unit equivalence**;
- **cross-major link**;
- **rung minis:**
  - **R1** (Int8 Rust function, exhaustive);
  - **R2** (a 40-line C hashtable);
  - **R3** (a `puts` through the runtimes seed in R, reversed);
  - **R4** (`sqlite`-shaped: a page image in a `MEM_IN` region, a B-tree-like binary search
    and a function-pointer callback);
  - **R8** (an entropy-driven estimator with `exp`).

**D3. Interface needed from the reference interpreter.** It is a codex job in progress and
read-only to this job. Today it provides `check`, `hash`, `run-oracle` (four-component
budgets, `--mem`, `--arg` including tokens) and `step-check --exhaustive`, which cover every
lifted example. The library already has `ClassicalMachine` (CC/R, tapes, `hostcall`
suspend/reply, segment and whole reversal), `QuantumRegisters` and `execute_action`. The
dialect checker needs CLI exposure of these. They are to be filed as a request to
`bennett-isa-spec` by the orchestrator, not by this job:

| Command | Purpose |
|---|---|
| `run-cc <obj> <entry> --args … --entropy hex --replies file` | results, fault records, tape, a memory digest, measurements with `--draws` |
| `reverse <obj> <entry> …` | run, then whole-run reversal, then entry-state equality |
| `run-action <obj> <action> --mut … --in … --mem … --args …` | basis permutation or state vector out |
| `run-program` | CC runs that issue region calls, with fixed measurement draws |

Until each lands, the examples that need it fail under P-2.

**D4. Seeds.** `spec/seeds/` (C, part of the spec repo, used only by the checker; runtimes
and arith implement independently, CLAUDE.md rule 5):

- a minimal allocator over the layout heap;
- shadow stack;
- memmove/memset/memcmp;
- EH state and personality subset;
- setjmp/longjmp;
- swapcontext;
- binary64 soft-float add/mul/cmp/conversions;
- `exp`/`log` from musl;
- a console/entropy device stub over the effect markers;
- the musl `__syscall` row.

Seed semantics equal the contract rows of §11, §13 and §14. The seeds are tested by their own
vectors (suites DR/DF seeds).

**D5. Order of work.**

1. Port 0.1's recogniser and validator to the §5 analysis.
2. Map with memory and calls, run through `run-oracle`.
3. Normaliser N21–N33 with native differential.
4. Descriptor and wrapper.
5. TDL reference.
6. CC/R examples once D3 lands.
7. Rung minis.

The 0.1 Python `run_ref` is retired as an executor. It may remain as a cross-check of the
Rust interpreter on the scalar subset only.

---

# Part E. Open questions for the maintainer

Each is a genuine design choice inside fixed scope. The outline proceeds with the recommended
option.

| # | Question | Options | Recommendation |
|---|---|---|---|
| E1 | Budget operand form on region-entry markers | (a) `ptr` to `bennett_budget {steps, heap, stack, depth, fault}`, null meaning table; (b) `i64` steps plus table for the rest (0.1 shape) | **(a)**: four components and the action fault register in source; uniform across markers; NS "integer operands" is met by integer fields. Cost: new legality cases for changed signatures. |
| E2 | `ctrl`/`adj`/`compute` budget across coherent slices | (a) every slice gets the full record; (b) the record is a total shared by all slices of one invocation (a counter threaded through the slice tokens) | **(a)**: simple and plugin-independent. (b) makes the fault set depend on the plugin's slice boundaries. |
| E3 | A non-bijective overwrite of a Co cell under `ctrl`/`adj` (TDL-5d) | (a) NS-literal `BD-E-COHERENT-OVERWRITE`; (b) additionally an opt-in module flag `bennett.coherent_overwrite = "history"` making the displaced bytes declared history outputs (garbage, reported in the certificate) | **(a) now**. (b) would extend NS §4.2. If wanted, it is an NS amendment through the council, not a dialect default. |
| E4 | Architecture of the rung 6/7 platform profile | (a) riscv64 (xv6-riscv, Linux `tinyconfig` ARCH=riscv); (b) x86-64 | **(a)**: a small privileged ISA (CSRs, `sret`, `sfence.vma`, `ecall`) and the canonical modern xv6, so fewer asm rows and `.S` shims. x86-64 can follow as a second profile. |
| E5 | Function-address encoding | (a) comparison-link address; (b) dense canonical index | **(a)**: native-equal pointer values (SQLite hashes and compares function pointers). |
| E6 | `switch` and dispatch construction in the reference body | (a) balanced binary compare tree; (b) the 0.1 linear chain | **(a)**: O(log k) rows. Changes 0.1's switch example hashes (a draft-to-draft change, allowed). |
| E7 | Shadow-stack storage | (a) one heap block per region or entry, part of the heap budget; (b) a dedicated layout global with its own size | **(a)**: stays within ISA §5.4's four components. |
| E8 | memcpy/memset in the reference body | (a) always a runtime lproc call; (b) inline expansion below a size threshold | **(a)**: one row shape, smaller hashes. Executors inline extensionally (T6). |
| E9 | Oracle interface representation | (a) in-memory descriptor (§8.1); (b) constant-global interface spec plus a parallel argument block | **(a)**: one operand; Rust/Julia/C build it the same way; kinds bounded by the finite domain. |
| E10 | How a front end requests deferred measurement | (a) module flag; (b) marker variant `__bennett_measure_deferred` | **(a)**: the front end cannot know at the call site whether it is inside a unitary region. |
| E11 | Default placement of host code sharing pointer-rich memory with device code | (a) promotion to device CC (B7); (b) reject until ISA-11 | **(a)**. (b) is a narrowing. |
| E12 | Budget operand on `adj` and `compute` | (a) add `ptr budget` to both (uniform; slices need budget and fault register); (b) keep 0.1 signatures and take both from the table and plugin allocation | **(a)**: the corpus is rerun for the changed `ctrl`/`oracle`/`inplace`/`reversible` signatures anyway. |
| E13 | Fault code for an indirect call matching no function of the program | (a) 4 `FAULT_UB_TRAP`; (b) 8 `FAULT_EFFECT_UNMODELLED` when the pointer may come from code without bitcode | **(a)**: one rule; the coverage report names external pointer sources. |
| E14 | Ill-formed candidates in a region candidate set | (a) compile them as trap bodies, reject only a unique ill-formed candidate; (b) reject if any is reachable | **(a)**: type-based candidate sets over-approximate, so (b) rejects correct programs. |

---

# Part F. bd closure map

Every child of `b-dialect-spec-8wf` and every 0.1 dialect item, with the 0.2 section that
removes it, and the blocker where part of the capability needs one.

| bd | Audit rows | 0.2 section | Blocker part |
|---|---|---|---|
| .1 | 1.4-d, D17, B-31, B-50, O-05 | §10 TDL, §18.4, B4 | – |
| .2 | 1.4-e, D18, B-43 | §9.3, TDL-9, §17.6 | – |
| .3 | 1.4-f | §8.7 | BLK-3 (ISA-3) |
| .4 | D1, B-05 | §3.4 classes | – |
| .5 | D2 | §9.2, §19.9 | – |
| .6 | D3 | §8.2 `ARG`, §8.5 | – |
| .7 | D4, B-39 | B1, §12, §16 | – |
| .8 | D5 | §7.5(a) | – |
| .9 | D6, B-49 | §6, §22 (`T-BORROW` deleted), ISA qborrow in actions | ISA-9 efficiency |
| .10 | D8, B-19 | §6.3 | – |
| .11 | D9 | §5.1 | – |
| .12 | D10, B-12 | §14.4 | – |
| .13 | D11, B-17, B-51 | §11, §4.5 | – |
| .14 | D14, B-41 | §8.7 | – |
| .15 | D16, B-45 | §13 | – |
| .16 | D19, B-53 | §19.8 | – |
| .17 | D21, B-32 | §8 | G-15 efficiency |
| .18 | B-06 | §3.4 | – |
| .19 | B-07 | §3.4, §6.5 | BLK-1 (ISA-4) |
| .20 | B-08 | §9.5 | BLK-2 (ISA-1) |
| .21 | B-11 | §3.6 | – |
| .22 | B-16 | §4.3, §4.4 | – |
| .23 | B-22 | §6.4, §14.2 | – |
| .24 | B-23 | §6.2 | – |
| .25 | B-24 | §5, §6.4 | BLK-1 for unbounded counts |
| .26 | B-26 | §5, §6.4 | – |
| .27 | B-27 | §5.2 | – |
| .28 | B-29 | §6.4 | – |
| .29 | B-30 | §6.6 | – |
| .30 | B-33 | §7.2, B17 | – |
| .31 | B-37 | §7.4, §10 | – |
| .32 | B-38 | §7.5(b) | BLK-4 (new ISA-12) |
| .33 | B-42 | §9, §17 | – |
| .34 | B-54 | §19.7 | – |
| .35 | O-01 | §14.2, §4.4 | – |
| .36 | O-02 | §15 | – |
| .37 | O-03 | §14.3 | – |
| .38 | O-04 | §19.2 | – |
| .39 | O-06 | §14.5, §14.6, §20 | G-16 efficiency |
| .40 | O-07 | §8.5, §19.6 | G-12 efficiency |
| -566 | C1 | §21 | – |
| -j88 | C2 | §21 | – |
| -cjb | C3 | §21 | – |
| -25h | C4 | §1.4 | – |
| -ape | C5 | §21 | – |
| -u6a | C6 | §21 | – |
| -kdj | C7 | §14.4, §21 | – |
