# Enzyme prior art for stock-LLVM-pass-safe marker calls (2026-10-28)

Purpose: compare the legality spike's empirical findings
(`2026-10-28-legality-spike.md`) with what Enzyme, Enzyme.jl, GPUCompiler.jl
and rustc's `std::autodiff` learned the hard way. Not normative.

Conventions. **[V]** = verified by me against a source I opened (code line,
issue/PR text, or a command I ran today); the URL or command is given.
**[I]** = inference, not directly confirmed. **[NF]** = looked for, not found.

Sources and pinned revisions (all opened/cloned today):

| Short | Repo | Revision |
|---|---|---|
| Enzyme | https://github.com/EnzymeAD/Enzyme | `5f2a1bc096b1801aa941bd7975d8a607d1e9dedb` (main, 2026-10-27) |
| Enzyme.jl | https://github.com/EnzymeAD/Enzyme.jl | `eb6a6df5da57ecb8843698919cb81a2a7a0ae338` |
| GPUCompiler | https://github.com/JuliaGPU/GPUCompiler.jl | `daab6f8c315217aba1ea33e9c42f8a42aadb7a25` |
| rustc | https://github.com/rust-lang/rust | `ab019e71a1a1f4688bcc4d5bf06d2c5a424a31a5` (main) |
| LLVM | https://github.com/llvm/llvm-project | `415cfa278f6cd2367715b2f42779545b71439073` (main) |

Local toolchains used for the "ran today" checks: clang-18 / opt-18,
Julia 1.13.3, rustc 1.99.1. Scratch files are in the session scratchpad
(`.../scratchpad/e/{m.c,s.c,p.c,j2.jl,j3.jl,r.rs}`), not in the repo.

## Summary table

| Hazard | What Enzyme (and its hosts) do | Source |
|---|---|---|
| Marker call (`__enzyme_autodiff`) eliminated, commoned or moved by stock passes | Nothing special. The declaration is an ordinary attribute-free external declaration; the call survives because it is an unknown external call. Enzyme adds no attribute to it. Verified locally: two identical marker calls are not CSE'd at `-O3`; call site carries only `nounwind` (C front end). | Enzyme.cpp L2404 (name match only); clang-18 run, §1.5 [V] |
| Marker recognised by what | Substring match on the callee name (`Fn->getName().contains("__enzyme_autodiff")`), after stripping constant-expression casts; `invoke` of a marker is first rewritten to `call`+`br`. Rust appends a per-site suffix (`__enzyme_autodiff_<outer>`), C++ gets mangled names, so substring is required. | Enzyme.cpp L2011-2060, L2404; rustc builder/autodiff.rs L298-307 [V] |
| Registered functions (custom rules, `enzyme_function_like`, allocation-like) inlined / internalised / dead-arg-eliminated / deleted before Enzyme runs | `PreserveNVVM(Begin=true)` runs at *pipeline start*: adds `noinline`, removes `alwaysinline`, forces `external` linkage, records old state in `prev_*` attributes; `Begin=false` after Enzyme restores it. | PreserveNVVM.cpp L178-195, L1190-1212; PR #948; issues #1994, #791 [V] |
| Region/target function pointer is not a constant `@f` after optimisation | `select` of two functions: Enzyme splits the block and clones the marker call per arm. `phi`, or a load from a lookup table: not handled (hard error `failed to find fn to differentiate`). `-O3` really does produce both forms from `if`/`switch` on marker arguments. | Enzyme.cpp L2471-2496, L413-424, Utils.cpp L3730-3805; clang-18 runs `s.c`, `p.c` [V]; error on phi [I] |
| `@f` internal and dead after inlining | Not a problem for call-operand references: the marker's argument is a use, so `@f` stays defined (clang-18 `-O3` run). Only functions referenced *solely* from registration globals needed linkage pinning (static `myfree` in `customalloc.c`). | clang-18 run `m.c` [V]; PR #948 [V] |
| `mergefunc` merges placeholder/target bodies | rustc turns `merge_functions` off for every pre-differentiation `llvm_optimize` stage. In LLVM `MergeFunctionsPass` is only added when `PTO.MergeFunctions` is set; it is not in the default pipeline otherwise. | rustc write.rs L585-596; LLVM PassBuilderPipelines.cpp L1604-1606 [V] |
| Pre-link LTO runs Enzyme on a one-TU module and fails | Since PR #3211 (2026-10-06) the pre-link `OptimizerEarly` callback does nothing at `FullLTOPreLink`/`ThinLTOPreLink`; differentiation happens in the linker-loaded plugin. Pre-link still runs `PreserveNVVM(Begin)`. Rust requires `-C lto=fat`; ThinLTO unsupported (open). | Enzyme.cpp L3216-3241; PR #3211; rustc intrinsic.rs L1795-1802; rust issue #153687 [V] |
| Sentinel *global variables* used as marker arguments (`enzyme_dup`) lose initialisers / visibility under LTO | Known failure. Open rustc PR proposes anchoring them as `#[no_mangle]` statics in `core`; HIP `-fgpu-rdc` fails similarly. | rust PR #155059 (open), Enzyme #2610 [V] |
| Where Enzyme runs relative to the stock pipeline | Clang/lld plugin: `registerOptimizerEarlyEPCallback` = after the module simplification pipeline (IPSCCP, GlobalOpt, inliner, DAE, GlobalDCE have already run) and before the vectoriser/unroller. rustc: appended after the whole (size-increasing-opts-disabled) default pipeline, then a second full pipeline. | Enzyme.cpp L3274; PassBuilderPipelines.cpp L1005-1230, L1456; rustc pw.cpp L1054-1068, write.rs L581-596 [V] |
| Call-site `noinline`/debug-loc dropped when the marker is replaced | Enzyme builds a fresh call; the call-site attribute and (for some paths) `!dbg` are lost, giving "inlinable function call ... must have a !dbg location". Open since 2024; rustc worked around on its side. | Enzyme issue #2195 [V] |
| Julia lowering of `ccall` | Plain `ccall(:sym, ...)` is **not** a call to a named declaration: it is an indirect call through a `@jlplt_<sym>_N_got` global. `ccall("extern sym", llvmcall, ...)` and `Base.llvmcall` with a `declare` give a direct call to an attribute-free declaration. Enzyme.jl itself does not emit `__enzyme_*` markers for autodiff; GPUCompiler's `deferred_codegen` is the named-marker precedent. | Julia 1.13.3 runs `j.jl`, `j2.jl`, `j3.jl`; GPUCompiler driver.jl L176, L235-248 [V] |
| Rust `extern "C"` declaration/definition attributes | Declaration gets `unnamed_addr` and (call-site and decl) `nounwind`. Definitions get `unnamed_addr` too, which makes address identity insignificant (merge-friendly). | rustc 1.99.1 run `r.rs` [V] |

---

## 1. How the marker calls are declared and recognised

### 1.1 Autodiff entry markers: by name, substring, no attributes

[V] In `lowerEnzymeCalls` the pass walks every `CallInst`, resolves the
callee through constant-expression casts, and matches **by substring on the
name**:

```
Enzyme.cpp L2404:   if (Fn->getName().contains("__enzyme_autodiff")) {
                      enableEnzyme = true;
                      derivativeMode = DerivativeMode::ReverseModeCombined;
```
https://github.com/EnzymeAD/Enzyme/blob/5f2a1bc096b1801aa941bd7975d8a607d1e9dedb/enzyme/Enzyme/Enzyme.cpp#L2404

The same file has a first pass (L2011-2060) that rewrites any `invoke` whose
callee name contains one of ~17 marker substrings (`__enzyme_float`,
`__enzyme_autodiff`, `__enzyme_fwddiff`, `__enzyme_batch`, ...) into a plain
`call` plus unconditional branch to the normal destination, and removes the
PHI entry from the unwind destination:
https://github.com/EnzymeAD/Enzyme/blob/5f2a1bc096b1801aa941bd7975d8a607d1e9dedb/enzyme/Enzyme/Enzyme.cpp#L2011

No signature check: arguments are parsed positionally, with sentinel
*global variables* (`enzyme_dup`, `enzyme_const`, ...) as in-band
annotations (`getMetadataName`, L240-275, resolves a load of / address of a
global to its name). Rust uses exactly the same ABI and declares the
globals itself (`cx.declare_global("enzyme_dup", ...)`):
https://github.com/rust-lang/rust/blob/ab019e71a1a1f4688bcc4d5bf06d2c5a424a31a5/compiler/rustc_codegen_llvm/src/builder/autodiff.rs#L159

Rust emits a *per-site unique* variadic declaration
(`__enzyme_autodiff` + outer function name) with no attributes set by
rustc other than what its declare helper gives:
```
autodiff.rs L300-307: DiffMode::Reverse => "__enzyme_autodiff", ... ad_name.push_str(outer_name);
autodiff.rs L336:     let enzyme_ty = unsafe { llvm::LLVMFunctionType(ret_ty, ptr::null(), 0, TRUE) };
```
https://github.com/rust-lang/rust/blob/ab019e71a1a1f4688bcc4d5bf06d2c5a424a31a5/compiler/rustc_codegen_llvm/src/builder/autodiff.rs#L286

### 1.2 Does Enzyme add/strip attributes to protect the autodiff marker call?

[V] No. I grepped `Clang/EnzymeClang.cpp` and `Clang/EnzymePassLoader.cpp`
for `noinline|NoInline|optnone`: no hits. `PreserveNVVM.cpp` mentions no
`__enzyme_autodiff`/`__enzyme_fwddiff` at all (its `__enzyme_*` strings are
the registration globals: `__enzyme_register_*`, `__enzyme_function_like`,
`__enzyme_allocation_like`, `__enzyme_inactivefn`, `__enzyme_nofree`,
`__enzyme_sparse_accumulate`, `__enzyme_inactive_global`). The marker call
survives stock optimisation solely because it is a call to an unknown
external function.

Counter-observation, also [V]: Enzyme *does* add elimination-licensing
attributes, but only to helper markers and only *inside its own lowering,
after the stock pipeline has run*:
```
Enzyme.cpp L2115-2122: if (Fn->getName().contains("__enzyme_todense") || ...contains("__enzyme_ignore_derivatives")) {
                         CI->setOnlyReadsMemory(); CI->setOnlyWritesMemory();   // LLVM >= 16
```
and for `__enzyme_float` (LLVM < 16) `InaccessibleMemOrArgMemOnly` on the
declaration plus `readonly nocapture` on pointer params (L2124-2137).
Takeaway: the attribute-free requirement is for the *interval before the
plugin runs*; Enzyme itself narrows effects once it owns the call.

### 1.3 Registration markers: global arrays/strings, pinned at pipeline start

[V] Custom derivative/allocation/function-like registrations are
**initialised global variables** whose *name* contains a keyword, e.g.
`void* __enzyme_register_derivative_foo[] = {(void*)foo, (void*)dfoo};`
(example in issue #1994). `PreserveNVVM` (a module pass, registered at
`PipelineStart` and, for full LTO, `FullLinkTimeOptimizationEarly`):

```
Enzyme.cpp L3283-3284:
  PB.registerPipelineStartEPCallback(loadNVVM);
  PB.registerFullLinkTimeOptimizationEarlyEPCallback(loadNVVM);
```
https://github.com/EnzymeAD/Enzyme/blob/5f2a1bc096b1801aa941bd7975d8a607d1e9dedb/enzyme/Enzyme/Enzyme.cpp#L3283

reads each registration global, copies the relationship onto the *function*
(attribute `enzyme_math`, metadata `enzyme_derivative`, ...), and calls
`preserveLinkage`:
```
PreserveNVVM.cpp L178-195:
bool preserveLinkage(bool Begin, Function &F, bool Inlining = true) {
  if (Begin && !F.hasFnAttribute("prev_fixup")) {
    F.addFnAttr("prev_fixup");
    if (F.hasFnAttribute(Attribute::AlwaysInline)) F.addFnAttr("prev_always_inline");
    if (F.hasFnAttribute(Attribute::NoInline))     F.addFnAttr("prev_no_inline");
    if (Inlining) { F.removeFnAttr(Attribute::AlwaysInline); F.addFnAttr(Attribute::NoInline); copyForwardedCalleeAttrs(F); }
    F.addFnAttr("prev_linkage", std::to_string(F.getLinkage()));
    F.setLinkage(Function::LinkageTypes::ExternalLinkage);
```
https://github.com/EnzymeAD/Enzyme/blob/5f2a1bc096b1801aa941bd7975d8a607d1e9dedb/enzyme/Enzyme/PreserveNVVM.cpp#L178

`Begin=false` (run right after Enzyme at L3257) restores linkage, removes
`noinline`, re-adds `alwaysinline` (L1190-1212). The registration globals
are consumed (erased, removed from `llvm.used`/`llvm.compiler.used`, L988+)
"because left standing they are a definition of the same name in every
translation unit" (PR #3148 text).

The clang plugin generates the registration global for attribute-style
annotations and marks it `used`:
```
Clang/EnzymeClang.cpp L136-141:
  auto &Id = AST.Idents.get((StringRef("__enzyme_") + Kind + "_autoreg_" + VD->getNameAsString()).str());
  auto V = VarDecl::Create(...); V->setStorageClass(SC_PrivateExtern);
  V->addAttr(clang::UsedAttr::CreateImplicit(AST));
```
https://github.com/EnzymeAD/Enzyme/blob/5f2a1bc096b1801aa941bd7975d8a607d1e9dedb/enzyme/Enzyme/Clang/EnzymeClang.cpp#L136

[V] The "keep it alive for the stock pipeline" half of this exists because
the registered function is referenced only by an *initializer* of a
non-`used`-visible global: the stock pipeline sees a plain function it may
inline, internalise and delete. A function that is a *call operand* of an
unknown external call does not have that problem (§4).

### 1.4 `__enzyme_function_like` / allocation-like

[V] `__enzyme_function_like` is a global of aggregate type
`{ptr @f, ptr @"name"}`; `handleFunctionLike` strips const-expr casts,
requires a `Function` ("First argument of enzyme_function_like must be a
constant function", L205-209), attaches attribute `enzyme_math`, calls
`preserveLinkage`. A Fortran variant encodes the name in the global's name
after `__enzyme_function_like__` (L847-860). Metadata/attributes are used
only as the *post-extraction* representation; the input form is always a
named global or named external call.

### 1.5 Does a stock pipeline really leave the marker alone? (ran today)

[V] `clang-18 -O3` on a C file with `double __enzyme_autodiff(void*, ...)`,
a `static double sq(double)`, and two identical calls in one function, then
`opt-18 -passes='default<O3>'` on the result:
```
declare double @__enzyme_autodiff(ptr noundef, ...) local_unnamed_addr #1   ; #1 has no function attrs of semantic interest
%2 = tail call double (ptr, ...) @__enzyme_autodiff(ptr noundef nonnull @sq, double noundef %0) #3   ; #3 = { nounwind }
%3 = tail call double (ptr, ...) @__enzyme_autodiff(ptr noundef nonnull @sq, double noundef %0) #3
define internal noundef double @sq(double noundef %0) #2     ; still present, internal, memory(none)
```
Both calls retained, `@sq` retained, the declaration gained only
`local_unnamed_addr`. Call-site attribute `nounwind` is front-end supplied
(C without `-fexceptions`). This matches the spike's L2 "observations"
column.

---

## 2. Passes that have broken markers or function pointers passed to them

I searched `EnzymeAD/Enzyme` and `rust-lang/rust` issues/PRs for:
mergefunc, function specialization, argument promotion, dead argument
elimination, globalopt, internalize, ipsccp, inferattrs, readnone,
`memory(none)`, optnone, noinline, LTO, ThinLTO. Results that are actually
about marker legality are below. **[NF]** for mergefunc, function
specialisation, argument promotion, ipsccp and inferattrs as the cause of
any reported Enzyme bug; the only mergefunc evidence is the rustc comment.

### 2.1 Inlining of the function a rule is attached to

- Enzyme issue #1994, "Compiling with -O{1,2,3} breaks custom rule that
  works with -O0". Reproducer: custom `__enzyme_register_derivative_*` for a
  `static` function; at `-O3` the primal is inlined and the rule never
  fires (`test output: 4.000000` vs `100.000000`). Reporter's fix:
  "These attributes are very important---without them, compiling with any
  -O flag besides -O0 silently breaks this rule ... `void
  __attribute__((noinline,optnone)) isconverged(...)`". [V]
  https://github.com/EnzymeAD/Enzyme/issues/1994
  (State: open; user-side workaround, i.e. the clang-plugin path does not
  fully protect users.)
- Enzyme issue #791, linker plugin and custom gradient: maintainer comment
  "this appears to be very similar to how at O0 the enzyme_like
  functionality we added didn't work until we ensured the code wasn't
  inlined until after Enzyme." [V]
  https://github.com/EnzymeAD/Enzyme/issues/791
- PR #3149: wrapper `CuWrap1DStruct::Call` pinned `noinline` stripped a
  user's `alwaysinline` "before any inliner saw it", breaking a downstream
  pipeline; fix gated by `PreserveCustomRuleLinkage`. Shows the cost of
  pinning by attribute mutation: it is lossy and must be undone. [V]
  https://github.com/EnzymeAD/Enzyme/pull/3149

### 2.2 Dead / internal functions referenced only by registration data

- PR #948 "Preserve deallocation function via linkage": the free function
  of `__enzyme_allocation_like` was not pinned; the diff makes the test's
  `myfree` `static` to cover it, and adds `preserveLinkage` for it. [V]
  https://github.com/EnzymeAD/Enzyme/pull/948
- `PreserveNVVM.cpp` L1149-1154 for libdevice-implemented intrinsics:
  `// As a side effect, enforces arguments cannot be erased.` followed by
  `preserveLinkage`. [V] This is the only explicit evidence I found that
  Enzyme relies on **external linkage to block dead-argument elimination**
  (the stock pipeline runs `DeadArgumentEliminationPass` at
  PassBuilderPipelines.cpp L1219 before Enzyme's `OptimizerEarly`
  extension point). Whether DAE/IPSCCP would have been the specific pass in
  any given bug: [I].

### 2.3 mergefunc

[V] rustc comment, `write.rs` L585-596:
```
// We also must disable merge_functions, since autodiff placeholder/dummy bodies tend to be
// identical. We run opts before AD, so there is a chance that LLVM will merge our dummies.
// In that case, we lack some dummy bodies and can't replace them with the real AD code anymore.
// We then would need to abort compilation. This was especially common in test cases.
```
https://github.com/rust-lang/rust/blob/ab019e71a1a1f4688bcc4d5bf06d2c5a424a31a5/compiler/rustc_codegen_llvm/src/back/write.rs#L585
and it sets `merge_functions = false` for stages other than PostAD. LLVM's
default pipeline adds `MergeFunctionsPass` only under `PTO.MergeFunctions`
(PassBuilderPipelines.cpp L1604-1606, [V]). That comment is about the
*old* design where Rust emitted placeholder function bodies; since PR
#142640 the marker is emitted at the call site, but the `merge_functions =
false` line is still there in the pinned revision [V].

### 2.4 LTO pipelines

- Enzyme registers on `OptimizerEarly` (per TU) *and*
  `FullLinkTimeOptimizationEarly`. With `-flto` both fired; the pre-link
  one saw one TU and died with `failed to find fn to differentiate`.
  PR #3211 (2026-10-06): "Defer differentiation from an LTO pre-link
  pipeline to the post-link run"; "Forgetting it is a loud failure
  (`undefined reference to __enzyme_autodiff...`), not silently wrong
  derivatives." [V]
  https://github.com/EnzymeAD/Enzyme/pull/3211 ; code at Enzyme.cpp
  L3216-3241.
- Issue #1925 "Clarify usage through linking": `ld.lld: error: ... Enzyme:
  failed to find fn to differentiate` when callee bitcode is not present
  (no `-flto` on the library). Maintainer: "you're perhaps not using
  clang/llvm/lto to force the emission of all the LLVM". [V]
  https://github.com/EnzymeAD/Enzyme/issues/1925
- Issue #2610: HIP `-fgpu-rdc` defers optimisation to link time, so a
  compile-time-only plugin never runs; needs the linker plugin too. [V]
- rustc: autodiff requires fat LTO, enforced in the intrinsic codegen:
  `if lto != rustc_session::config::Lto::Fat { emit_err(AutoDiffWithoutLto) }`
  (intrinsic.rs L1795-1802). ThinLTO support: rust issue #153687, open. The
  issue text explains the contract: Enzyme "knows to differentiate foo,
  because we generate declarations with magic names, called
  `__enzyme_autodiff_<hash>` ... When we call those declaration we pass a
  ptr to `foo` as the first argument." and without running Enzyme, link
  fails with `undefined symbol: __enzyme_autodiff_...`. [V]
  https://github.com/rust-lang/rust/issues/153687
- rustc defers Enzyme in non-LTO debug multi-CGU builds: "In the case of
  debug builds with multiple codegen units, we might not have all function
  definitions available during the early compiler invocations. We
  therefore wait for the final lto step to run Enzyme." (pw.cpp L1054-1058,
  `if (EnzymePtr && IsLTO)`). [V]

### 2.5 Sentinel globals under LTO

rust PR #155059 (open): "LLVM's Link-Time Optimization aggressively
stripped their initializers, causing Enzyme to misinterpret them as active
external variables rather than constant structural markers"; error text
`Enzyme: cannot compute with global variable that doesn't have marked
shadow global  @enzyme_dup = external global ptr`. Proposed fix anchors the
globals in `core`. [V] (PR unmerged; I have not verified that the diagnosis
is correct.)
https://github.com/rust-lang/rust/pull/155059

### 2.6 Attributes inferred onto declarations / TargetLibraryInfo

[NF] for Enzyme. Locally [V]: `InferFunctionAttrsPass` is the first pass in
the default pipeline (PassBuilderPipelines.cpp L1051) and only attaches
attributes to names matching `TargetLibraryInfo`; clang-18 `-O3` put none on
a `__enzyme_autodiff` declaration beyond `local_unnamed_addr`. Enzyme's own
special-casing of `log`, `sin`, ... (issue #1925: "The outermost function
Enzyme differentiates presently can't be a standard math function")
is the converse: a *libfunc name* gets inferred `memory(write)`/`willreturn`
from TLI and loses its body. The `__bennett_` prefix is not in TLI. [I]

### 2.7 Pass-created `select`/`phi` of function pointers

Not an Enzyme issue report; I tested it, §4.

### 2.8 Call-site info lost when Enzyme rewrites the call

Enzyme issue #2195 "enzyme pass drops noinline attribute": "The call to
`__enzyme_autodiff` has a callsite debug metadata saying noinline. This get's
dropped by enzyme, so the final call is inlineable. Now we get ...
`inlinable function call in a function with debug info must have a !dbg
location`". Open (reopened by maintainer after a rust-side workaround). [V]
https://github.com/EnzymeAD/Enzyme/issues/2195

---

## 3. How hosts emit the markers

### 3.1 C/C++ (clang)

User source declares `extern double __enzyme_autodiff(void*, ...);` and
calls it. Clang emits an attribute-free declaration (§1.5). In C++ a
templated declaration `template<class R, class... A> R __enzyme_autodiff(A...)`
(issue #2610) yields a mangled name, which is why Enzyme matches by
substring. Plugin positions: `-fplugin=ClangEnzyme-N.so` (compile time),
`-Wl,--load-pass-plugin=LLDEnzyme-N.so` (link time), described in issue
#1925 and PR #3211. [V]

### 3.2 Enzyme.jl: no marker calls for the main API

[V] Enzyme.jl does **not** emit `__enzyme_autodiff` calls. `autodiff` is a
generated function that compiles the callee with GPUCompiler and
`EnzymeInterpreter`, then calls the Enzyme C API directly
(`API.EnzymeCreatePrimalAndGradient`, `EnzymeCreateForwardDiff`;
src/compiler.jl L3571-3716):
https://github.com/EnzymeAD/Enzyme.jl/blob/eb6a6df5da57ecb8843698919cb81a2a7a0ae338/src/compiler.jl#L3628
Markers appear only for in-IR helpers: `__enzyme_ignore_derivatives`
(callconv.jl L574: "emits a call to `__enzyme_ignore_derivatives`, which
only the Enzyme pipeline resolves") and `__enzyme_float/double/integer/
pointer` which Enzyme.jl erases after use (compiler.jl L7336-7345). `grep
-n "__enzyme_" src` found no `__enzyme_autodiff`.

The *named-marker precedent in the Julia ecosystem* is GPUCompiler's
`deferred_codegen`, which Enzyme.jl reuses (compiler.jl L8829):
```
GPUCompiler driver.jl L176:  ccall("extern deferred_codegen", llvmcall, Ptr{Cvoid}, (Int,), $id)
GPUCompiler driver.jl L235:  haskey(ir.functions, "deferred_codegen")
GPUCompiler driver.jl L248:  for use in dyn_marker.uses  ... id = convert(Int, first(call.operands))
```
https://github.com/JuliaGPU/GPUCompiler.jl/blob/daab6f8c315217aba1ea33e9c42f8a42aadb7a25/src/driver.jl#L235
i.e. a named external, recognised by `ir.functions[name]` after Julia's own
optimiser has run, with a constant integer id operand; plus a comment that a
Julia bug "drops the pointer when code-coverage is enabled" on 1.11+
(driver.jl L181-183), the reason it is also registered as a JIT symbol.
[V]

**Why not plain `ccall`**: [V] ran on Julia 1.13.3, `optimize=true`:
```julia
ccall(:__bennett_gate, Cvoid, (UInt32, Ptr{Cvoid}, UInt64), 1, C_NULL, x)
  =>  %__bennett_gate = load atomic ptr, ptr @jlplt___bennett_gate_170_got unordered
      call void %__bennett_gate(i32 1, ptr null, i64 %x)           ; INDIRECT, no named callee
ccall("extern __bennett_gate", llvmcall, Cvoid, (UInt32, Ptr{Cvoid}, UInt64), 1, C_NULL, x)
  =>  call void @__bennett_gate(i32 1, ptr null, i64 %"x::UInt64")   ; direct
      declare void @__bennett_gate(i32, ptr, i64) local_unnamed_addr  ; no attributes
Base.llvmcall(("declare void @__bennett_gate(i32, ptr, i64)\n define void @f(i64 %0) alwaysinline {...}", "f"), ...)
  =>  two direct calls to @__bennett_gate after Julia inlines f
```
(A first attempt with a body-only `llvmcall` string produced
`Module IR does not contain specified entry function` -- the module form
with a defined entry function is required.) Enzyme.jl's own `llvmcall` code
includes a comment that Julia links the `llvmcall` module "as is into every
caller", so any non-internal definition in it is duplicated and aborts the
JIT (compiler.jl L8076-8081). That bears on any `llvmcall` that defines a
helper next to the marker declaration. [V for the comment; the spike's
emission agent should confirm behaviour.]

### 3.3 rustc

[V] Pipeline:
1. `#[autodiff_forward/reverse]` expands to a placeholder function whose body
   calls the `autodiff` intrinsic (builtin_macros/autodiff.rs L181-202).
   `#[inline(never)]` is copied onto the generated function only if the
   source function has it (L423-427).
2. Codegen of the intrinsic (`generate_enzyme_call`, builder/autodiff.rs
   L286-380) declares `__enzyme_{fwddiff,autodiff}<outer>` as a variadic
   external function via `declare_simple_fn(... llvm::UnnamedAddr::No ...)`,
   passes `@fn_to_diff` as first argument, then `enzyme_*` global sentinels,
   and emits `bx.call(...)`. No attributes are added.
3. The old design (before PR #142640, merged as
   `e3a178234d75ee8545b766653643306d0c3f2919`) did add `noinline` to the
   declaration: "Otherwise LLVM might inline our temporary code before the
   enzyme pass has a chance to do it's work." plus a made-up
   `enzyme_marker` string attribute on the outer function to find it after AD
   (diff lines visible via `gh pr diff 142640`). `noinline` on a
   *declaration* is meaningless to the inliner (nothing to inline); I read
   this as a defensive attribute for the placeholder and **[I]** the real
   protection was never the attribute. It was removed in the intrinsic
   rewrite. Issue #138920 documents the follow-up problem: functions pinned
   `noinline` before AD must be un-pinned for the post-AD pipeline.
4. Pipeline position (`llvm_optimize`, write.rs L555-600; lto.rs L596-645;
   PassWrapper.cpp L1054-1068): optimisation with unrolling, vectorisation
   and mergefunc **off** ("PreAD"), then `EnzymePtr(PB,false)` registers the
   pass *names only* and `parsePassPipeline(MPM,"enzyme")` appends the
   Enzyme pass **at the end of that module pipeline**, then a second
   `llvm_optimize` with full options ("PostAD") runs. Fat LTO is required.
   The first-stage comment: "The whole point of compiler based AD is to
   differentiate optimized IR instead of unoptimized source code."
   (write.rs L557-560).

Rust attributes on `extern "C"` declarations/definitions, rustc 1.99.1
`-O --emit=llvm-ir` [V]:
```
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef) unnamed_addr #0   ; #0 = nounwind nonlazybind uwtable ...
tail call void @__bennett_gate(...) #1                                              ; #1 = nounwind
define void @u(...) unnamed_addr #0                                                  ; definitions are unnamed_addr too
```

### 3.4 Papers

[V] NeurIPS 2020 (arXiv 2010.01709): "Static Languages: Using gradients
inside LLVM-based languages simply requires calling an external
`__enzyme_autodiff` function" and "Enzyme requires the IR for all
functions it may need to differentiate to be available when the pass is
run ... enable LTO and run Enzyme on the merged IR for all the sources";
the paper's case for running after optimisation ("O(N) if optimization is
run before AD and O(N^2) if optimization is run after AD"). Local copy
read via `pdftotext`. SC'21 (EnzymeGPU.pdf from c.wsmoses.com): "an
optimization pass is enabled that acts on calls to the `__enzyme_autodiff`
function ... The call to `__enzyme_autodiff` is replaced by a call to the
newly generated derivative function." **Not opened**: SC'22 (DOI
10.1109/SC41404.2022.00065; no accessible PDF). Neither opened paper
discusses attribute protection, mergefunc, or function-pointer
canonicalisation.

---

## 4. Function pointers passed as marker arguments

### 4.1 Required form

[V] `parseFunctionParameter` (Enzyme.cpp L403-425):
```
fn = GetFunctionFromValue(fn);
if (!fn || !isa<Function>(fn)) { EmitFailure("NoFunctionToDifferentiate", ..., "failed to find fn to differentiate", *CI, " - found - ", *ofn); return nullptr; }
if (cast<Function>(fn)->empty()) { EmitFailure("EmptyFunctionToDifferentiate", ...
```
Resolution (`GetFunctionValFromValue`, Utils.cpp L3730-3805) strips: cast
instructions, cast constant-expressions, `BlockAddress` (to its function),
`GlobalAlias` (to aliasee), and `call`/`invoke` of a function with a single
`ret` of a constant or an argument, plus `simplifyLoad` (loads from constant
globals). It has **no `PHINode` case and no variable-index table-load
case**. So a target must resolve to a `Function` *definition*.

The same code also covers a non-markers case: `__enzyme_virtualreverse`
requires `dyn_cast<Constant>` ("Cannot create virtual version of
non-constant value", L2586-2591).

### 4.2 `select` of functions: handled by path splitting

[V] Enzyme.cpp L2471-2496: if the (cast-stripped) first operand is a
`SelectInst`, the block is split, the marker call is **cloned into two
arms**, one with the true value and one with the false value, with a PHI
merging the result, and the scan restarts (`goto retry`).
https://github.com/EnzymeAD/Enzyme/blob/5f2a1bc096b1801aa941bd7975d8a607d1e9dedb/enzyme/Enzyme/Enzyme.cpp#L2471
This is exactly a "tail duplication" that preserves the dynamic marker
sequence. It exists because the optimiser creates this shape (next).

### 4.3 The optimiser does create select and phi+table

[V] clang-18 `-O3`, `if (c) __enzyme_autodiff((void*)f, x); else
__enzyme_autodiff((void*)g, x);`:
```
%4 = select i1 %3, ptr @g, ptr @f
%5 = tail call double (ptr, ...) @__enzyme_autodiff(ptr noundef nonnull %4, double noundef %1) #3
```
(SimplifyCFG sink-common-code merges the two calls; the *dynamic* marker
sequence is preserved but the static call count halves and the operand
is no longer a constant.)

[V] a four-way `switch` with a marker call per case:
```
@switch.table.d = private unnamed_addr constant [3 x ptr] [ptr @f, ptr @g, ptr @h], align 8
%6 = getelementptr inbounds [3 x ptr], ptr @switch.table.d, i64 0, i64 %5
%9 = phi ptr [ %7, %4 ], [ @k, %2 ]
%10 = tail call double (ptr, ...) @__enzyme_autodiff(ptr noundef nonnull %9, double noundef %1) #3
```
(SimplifyCFG switch-to-lookup-table; the table load has a variable index and
the PHI mixes it with a constant.) Enzyme's resolver has no case for this
shape, so I **[I]** infer `NoFunctionToDifferentiate`; I did not build
Enzyme to run it. [NF]: no Enzyme issue report for this shape.

### 4.4 `@f` internal and dead after inlining

[V] Not an issue when `@f` is the call operand (clang-18 run `m.c`: internal
`@sq` kept after `default<O3>`, in `d` the call still names `@sq`). It *is*
an issue for functions referenced only from registration initialisers
(§2.2, PR #948), hence `preserveLinkage`. Inlining `@f` into *its callers*
does not matter for Enzyme because the marker's own use keeps the
definition; Enzyme clones `@f` and never modifies it (rust #153687 text:
"Enzyme will never modify foo, bar, or baz. It creates full copies").

### 4.5 Rust: `unnamed_addr` definitions

[V] rustc 1.99.1 definitions carry `unnamed_addr`. [I] This licenses
`MergeFunctions` (when enabled) and constant merging to unify identical
bodies without preserving address identity; a design that tests "pointer
equals same symbol as before" (spike L4) will see a spurious difference
under Rust. Enzyme avoided this by disabling mergefunc (§2.3).

---

## 5. Other findings directly relevant to "stock passes preserve the dynamic call sequence"

1. **Unknown external call = fixed point of LLVM's effect model.** [V,
   clang-18 run, §1.5] Two identical calls, no attributes, both retained
   after `default<O3>`; the only attribute on the call is front-end
   `nounwind`. Enzyme's 6-year history shows no issue where a stock pass
   deleted, merged or reordered marker calls ([NF] after the searches in
   §2); the reported breakages are all about the **operands** (function
   pointers, sentinel globals) and about **registered functions**, not
   about the call itself. Absence of reports is not proof.
2. **The plugin position matters more than anything about the call.**
   Enzyme runs at `OptimizerEarly` after the simplification pipeline
   (LLVM PassBuilderPipelines.cpp L1676-1679, L1456), then
   `AlwaysInlinerPass`, GVN, SROA, itself, `PreserveNVVM(false)`, more
   cleanup (Enzyme.cpp L3245-3264). In rustc it runs after the entire
   reduced pipeline. Both therefore see **post-inliner IR**: markers were
   never expected to survive *as static call sites*, only as dynamic
   events; same contract as the north star's §3.1 row.
3. **Debug-info interactions** (issue #2195, §2.8): replacing a marker with
   a generated call needs `setDebugLoc` (Enzyme sets it for the main path:
   `diffretc->setDebugLoc(CI->getDebugLoc())`, Enzyme.cpp L1700, but the
   issue shows some paths still lose it). The spike corpus is specified
   "no debug info"; this hazard is invisible to it.
4. **`invoke` form** (Enzyme.cpp L2011-2060): front ends produce `invoke` of
   markers inside C++ cleanup scopes; Enzyme needed a dedicated pre-step.
5. **Enzyme's `-O0` story**: PreserveNVVM exists at all because the
   registration route is data, not calls. maintainers: custom rules
   "didn't work until we ensured the code wasn't inlined until after
   Enzyme" (#791). So for -O0 + `alwaysinline` (what clang does at -O0 for
   `always_inline`) the same applies to any region function a front end
   marks `alwaysinline`: the AlwaysInliner runs at pipeline start
   (PassBuilderPipelines.cpp L1211 `AlwaysInlinerPass` in the simplification
   pipeline; also rustc `inline(always)`). Region functions inlined into
   their caller **cease to be a `define` that a marker can name**, only if
   the marker operand is not itself a use; with the operand as a use,
   `alwaysinline` still inlines other call sites, leaves the definition
   (non-`linkonce`) in place, but for `linkonce_odr`/`available_externally`
   bodies the definition may be dropped if no remaining uses besides the
   address; the address use here keeps it. [I]
6. **Lowering atomicity** (PreserveNVVM `Begin=false`): Enzyme restores
   everything it perturbed after it finishes, so the output stays valid for
   later stock passes.

---

## Implications for the Bennett dialect spec

Each is tied to a finding above. "Spike" = adjust the legality corpus/harness.

1. **Match on a name prefix, not equality; accept `invoke`, cast callees,
   and per-site suffixes (§1.1, §3.3).** Enzyme uses `contains(...)`, strips
   const-expr casts, and special-cases `invoke`. State in the spec that
   recognition is `callee-name starts_with "__bennett_"` after demangling,
   *plus* a signature check (Enzyme has none, a source of silent misparse),
   applied to `call`, `invoke`, and calls through bitcast/const-expr
   callees. Spike: add an `invoke`-based marker case with a landing pad and
   a C++ template-mangled marker.

2. **Keep the positive requirement "no attributes on markers", but classify
   `nounwind`, `unnamed_addr`, `local_unnamed_addr` as expected (§1.5, §3.3,
   §5.1).** Front ends add them themselves (clang: call-site `nounwind`;
   rustc: `nounwind` + `unnamed_addr`; O3: `local_unnamed_addr`). Spike L2
   should not treat them as failures (the doc already records `nounwind`
   as an observation; add the two `*unnamed_addr` forms). Do **not** copy
   Enzyme's later habit of adding `memory(none)`/`readonly` to helper
   markers (§1.2) into any stage that precedes the final plugin run.

3. **Region operands are not always a constant `@f`; the plugin must
   resolve and path-split (§4.2-4.3).** At `-O3`, SimplifyCFG turns "marker
   call per branch" into a single call with a `select ptr @g, ptr @f`, and
   a multiway `switch` into a `phi` over a lookup-table load. Enzyme handles
   `select` by cloning the call per arm and fails on the table/phi shape.
   Bennett's `__bennett_ctrl/adj/compute/reversible/inplace` take function
   pointers, so the spec must define "region operand resolution" as: strip
   casts/aliases (Enzyme's list), then if `select`/`phi`/constant-table
   load over defined functions, **tail-duplicate the marker call per
   incoming function** (legal: preserves the dynamic sequence), else
   fail-loud. Spike L4 as written ("resolves to the same symbol as in the
   baseline") would flag legal select/phi; replace by "operand resolves, via
   select/phi/constant-table, to a set of `define`s each reachable only on
   the path where the baseline passed it". Add corpus cases: two-way
   `if`, 4-way `switch`, region chosen from a `static const bregion tbl[]`
   indexed by input.

4. **Do not rely on symbol identity of region functions (§2.3, §4.5).**
   rustc had to disable mergefunc because identical placeholder bodies were
   merged; Rust definitions are `unnamed_addr`. Define region identity as
   behavioural (the plugin sees through `GlobalAlias` as Enzyme's resolver
   does, L3746, and through a merge thunk if it can prove it forwards
   unchanged), and list `mergefunc` explicitly in the compatibility notes:
   when a pipeline enables it, aliases/thunks are legal, `declaration` is not.
   The spike's `mergefunc` probe stays a probe, but run it with
   `unnamed_addr` on the twin definitions, which is what Rust emits.

5. **Region functions need no linkage pinning when they are call operands
   (§1.3, §4.4); it is data-only registrations that need it.** Enzyme's
   whole `PreserveNVVM` machinery exists because registered functions are
   referenced only by global initialisers. Bennett's design passes
   `@f` as an operand of an external call, which is a use LLVM must respect.
   Record this as a deliberate design decision: **never** introduce a
   side-table global (`__bennett_register_*`, `llvm.global.annotations`) as
   the only reference to a region body, because then the Bennett plugin
   would need Enzyme's pipeline-start pass, which a link-time plugin
   running after pre-link O3 cannot be.

6. **Plugin pass position is part of the contract, and LTO has two
   phases (§2.4, §5.2).** Specify that the plugin runs only at the final
   link, with no compile-time companion, and that the *pre-link* pipeline
   is stock. Enzyme learned (PR #3211) that registering on both
   `OptimizerEarly` and `FullLinkTimeOptimizationEarly` made the compile-time
   instance fire on one-TU modules; if Bennett ships a single plugin
   library (clang plugin and lld plugin are the same `.so` in Enzyme),
   gate on `ThinOrFullLTOPhase` and on the "no definition visible" case, and
   fail loud (undefined reference to `__bennett_*`) when the plugin did not
   run, which is what PR #3211 gives Enzyme and is better than silent
   wrongness. State supported modes: full LTO and ThinLTO post-link;
   rustc requires `-C lto=fat` (rust #153687 open for ThinLTO); HIP-style
   deferred relocatable device code needs the linker plugin as well
   (Enzyme #2610). Spike: run P4 with ThinLTO and with
   `-flto=thin -fno-inline` at compile time.

7. **Julia: specify `ccall("extern __bennett_x", llvmcall, ...)` or
   `Base.llvmcall` with a `declare` as the emission form; plain
   `ccall(:__bennett_x, ...)` is not a legal front end (§3.2).** Verified:
   plain `ccall` becomes an indirect call through `@jlplt_*_got`, with no
   named callee, so name-based recognition cannot see it. Both alternatives
   yield direct calls to an attribute-free declaration
   (`declare void @__bennett_gate(i32, ptr, i64) local_unnamed_addr`).
   GPUCompiler's `deferred_codegen` is the in-ecosystem precedent; follow
   its pattern (constant integer operand, name lookup in the final module)
   and keep the JIT-symbol fallback in mind for code coverage (driver.jl
   L181-183). Because an `llvmcall` module is linked as-is into every caller
   (Enzyme.jl compiler.jl L8076), the marker must be a bare declaration with no
   accompanying definitions.

8. **Avoid sentinel global variables as marker arguments (§2.5).** Enzyme's
   `enzyme_dup`-style activity sentinels broke under LTO (rust #155059) and
   HIP RDC (#2610). Bennett's ABI already passes plain integer opcodes
   (`uint32_t op`); say in the spec that every in-band tag is an integer
   constant, never the address or value of a global.

9. **The replacement of a marker must copy `!dbg` and call-site
   attributes, and the corpus needs a `-g` variant (§2.8, §5.3).** Enzyme
   #2195 shows that substituting a new call for the marker leads to a verifier
   failure under debug info. Bennett's plugin rewrites many marker calls and
   outlines regions, so require "every instruction the plugin creates in
   place of a marker inherits the marker's `DebugLoc`", and add a spike
   dimension: compile every `.c` case with `-g`.

10. **Keep "legality is a property of the unknown external call" but
    qualify it (§5.1).** Enzyme's evidence supports: the *call* is stable;
    the *operands that are pointers* are not (item 3), and any
    *data* that names functions needs pinning (item 5). Update north star
    §3.1 text: "Stock passes preserve the dynamic sequence of marker calls;
    they do not preserve the static call sites, the constancy of function
    pointer operands, or the identity of region functions." (the first
    clause is what the spike tests; the other two are what Enzyme's
    code and the clang-18 runs above show.)

## Not found / not verified

- SC'22 paper not opened. Enzyme docs website (enzyme.mit.edu) not
  accessible as a repo; claims rest on source, issues, PRs and the two
  papers I opened.
- Did not build Enzyme; the "phi/table operand is rejected" claim (§4.3)
  is inferred from reading `GetFunctionValFromValue`, not executed.
- No Enzyme issue found attributing a bug to mergefunc, function
  specialisation, argument promotion, IPSCCP, or `inferattrs` on markers.
  Only rustc's mergefunc comment (and general linkage pinning) point that
  way.
- I did not look at Enzyme.jl's behaviour for `ccall` user code beyond
  the emission points listed; no Julia-specific mergefunc/DAE issue was
  searched for beyond the keyword sweeps in §2.
- Older rustc revisions' exact `noinline` logic (pre-#142640) read only
  through `gh pr diff 142640` and issues #138920, #143994, not as a
  checked-out tree.
