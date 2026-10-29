# Julia 1.13.3 (LLVM 20.1.8jl) emission notes

Files: `routes.jl` (every route; `case_B` = whole ABI via `ccall(:sym,...)`, `case_D` = whole ABI via `Base.llvmcall`), `emission.jl` (dumps), `ir/<name>.{unopt,opt}.ll` (`code_llvm(...; raw=true, dump_module=true, optimize=false|true, debuginfo=:none)`), `gpucompiler.jl` + `ir_gpucompiler/` (GPUCompiler.jl native target), `staticcompiler.jl` + `ir_staticcompiler/kS.o` (StaticCompiler `generate_obj`), `stub.c`/`libbennett_stub.so` + `run_stub.jl` + `run_stub.out` (test-only stub library: it exists only so `ccall((:sym, LIB))` and execution can be tested; it is not an ABI deliverable; the markers elsewhere are undefined), `nolib.jl`.
All captured `.ll` parse and verify with the LLVM 20 `opt -passes=verify` (checked on `ir/rD_gate.opt.ll`, `ir/case_B.opt.ll`, `ir_gpucompiler/kL.opt.ll`, `ir_gpucompiler/kB.opt.ll`).

"LTO-ready" Julia IR: Julia never emits LTO bitcode; closest are (a) `code_llvm(...; optimize=true)` (Julia's own full pipeline, `ir/*.opt.ll`), (b) GPUCompiler's optimised module for a native target (`ir_gpucompiler/*.opt.ll`), (c) (b) piped through LLVM 20 `opt -passes='lto-pre-link<O2>'` (`ir_gpucompiler/kL.lto-pre-link-O2.ll`, `kB.lto-pre-link-O2.ll`).

## THE KEY QUESTION: is it `call @__bennett_...` by name?

| Route | Source | Result |
|---|---|---|
| A `ccall((:sym, LIB), ...)`, LIB loadable at codegen | `rA_*` | **Indirect call through a PLT-GOT load.** Not by name. |
| A' `ccall((:sym, "nonexistent"), ...)` | `ir/rA_missinglib_gate.unopt.ll` | Indirect through a GOT global, `external`. |
| B `ccall(:sym, ...)` no library | `rB_*` | **Indirect through a lazily bound `jlplt` GOT global.** Not by name. |
| C `@ccall sym(...)::T`, `@ccall LIB.sym(...)` | `rC_*` | Identical to B / A respectively. |
| C-variadic `@ccall sym(a::T; 1::Cint, ...)::Cvoid` | `rH_ctrl_v` | Indirect through a phi of an inline-`dlsym`'d pointer (a `ccall___bennett_ctrl_v` cache global). Not by name. |
| D `Base.llvmcall((modIR, "entry"), ...)` with a `declare` in `modIR` | `rD_*`, `rD2`, `rD3`, `rH5` | **Direct `call @__bennett_...` by name, a real `declare`.** |
| E `ccall(p::Ptr, ...)` | `rE_gate` | Indirect through the `ptr` argument (no symbol at all). |

### Route B (`ccall(:__bennett_qalloc, ...)`, no library), `ir/rB_alloc.unopt.ll`

```
@jlplt___bennett_qalloc_673_got = external global ptr #0
  %__bennett_qalloc = load atomic ptr, ptr @jlplt___bennett_qalloc_673_got unordered, align 8, !dbg !21
  %1 = call ptr %__bennett_qalloc(i64 0, i64 %"n::UInt64"), !dbg !21
attributes #0 = { "julia.fname"="__bennett_qalloc" "julia.libidx"="0" }
```

The SSA name `%__bennett_qalloc` is cosmetic. The callee is a loaded `ptr`; the symbol name survives only (i) in the GOT global's name `jlplt___bennett_qalloc_673_got` (numeric suffix per compilation) and (ii) in the global's attributes `"julia.fname"="__bennett_qalloc"` (`"julia.libidx"="0"` = no library / process). Optimised (`ir/rB_alloc.opt.ll`) is unchanged apart from `external local_unnamed_addr global ptr #0`: `%__bennett_measure = load atomic ptr, ptr @jlplt___bennett_measure_702_got unordered ... ; %2 = call i8 %__bennett_measure(ptr %"h::Ptr", i64 0)`. Julia's optimiser can CSE/hoist the `unordered` GOT loads but not remove the call (`ir/case_B.opt.ll` shows all 13 `call ... %__bennett_*` indirect calls preserved, in source order, each preceded by its own GOT load, e.g. `%__bennett_gate1 = load atomic ptr, ptr @jlplt___bennett_gate_528_got unordered` / `call void %__bennett_gate1(i32 1, ptr %2, i64 2)`).

### Route A (with library), `ir/rA_alloc.unopt.ll`

```
@jlplt___bennett_qalloc_608_got = private unnamed_addr constant ptr @jlplt___bennett_qalloc_608_got.jit #0
@jlplt___bennett_qalloc_608_got.jit = private alias ptr, inttoptr (i64 123916560904464 to ptr)
  %__bennett_qalloc = load atomic ptr, ptr @jlplt___bennett_qalloc_608_got unordered, align 8, !dbg !21
  %1 = call ptr %__bennett_qalloc(i64 0, i64 %"n::UInt64"), !dbg !21
attributes #0 = { "julia.fname"="__bennett_qalloc" "julia.libname"="/home/tobias/.../libbennett_stub.so" }
```

If the library is dlopen-able when Julia compiles, codegen resolves the symbol and bakes the ABSOLUTE ADDRESS into the module (`inttoptr (i64 123916560904464 to ptr)`), so the IR is non-portable and contains no symbol name except in attributes. In the optimised IR the call becomes `%2 = call i8 @jlplt___bennett_measure_642_got.jit(ptr %"h::Ptr", i64 0)` (`ir/rA_measure.opt.ll`), i.e. a syntactically direct call to a *private alias of a constant address*, whose name is `jlplt_<fn>_<n>_got.jit`, not `__bennett_*`. If the library is not loadable at codegen (`ir/rA_missinglib_gate.unopt.ll`): `@jlplt___bennett_gate_133_got = external global ptr #0`, `attributes #0 = { "julia.fname"="__bennett_gate" "julia.libname"="libbennett_does_not_exist" }`.

### Route C (`@ccall`)

`rC_alloc`: same as B (`@jlplt___bennett_qalloc_731_got = external global ptr #0`, `attributes #0 = { "julia.fname"="__bennett_qalloc" "julia.libidx"="0" }`); `rC_alloc_lib` (`@ccall LIB.__bennett_qalloc(...)`): same as A.

### Route D (`Base.llvmcall`), the only route that yields a declaration

```
define swiftcc void @julia_rD_gate_835(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"h::Ptr", i64 zeroext %"i::UInt64") #0 !dbg !7 {
  call void @__bennett_gate(i32 1, ptr %0, i64 %1)
declare void @__bennett_gate(i32, ptr, i64)             ; unopt
declare void @__bennett_gate(i32, ptr, i64) local_unnamed_addr   ; opt
```

(`ir/rD_gate.unopt.ll`, `ir/rD_gate.opt.ll`.) The `declare` carries no attributes at all, not even `nounwind` (Julia adds nothing). The call is inside an internal wrapper function (`define internal void @julia_rD2_gate_785u789(ptr %0, i64 %1)` / `fastcc ... unnamed_addr` after opt) that the Julia function calls. The measure example keeps the user-written `zeroext i1`: `declare zeroext i1 @__bennett_measure(ptr, i64) local_unnamed_addr`; `%r = call zeroext i1 @__bennett_measure(ptr %0, i64 0)`; Julia's own wrapper returns `i8`: `define swiftcc i8 @julia_rD_measure_851(...)`.
Attributes are exactly what the user writes: with `declare void @__bennett_gate(i32, ptr, i64) #0` + `attributes #0 = { nounwind }` (`ir/rD3_gate.unopt.ll`) Julia preserves it: `declare void @__bennett_gate(i32, ptr, i64) #3`, `attributes #3 = { nounwind }`.
Variadic, `rH5_ctrl_v`: `call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr %0, i64 0, ptr null, i64 8, i32 1, double 2.500000e+00, ptr %0)` and `declare void @__bennett_ctrl_v(ptr, i64, ptr, i64, ...) local_unnamed_addr`.

llvmcall forms that FAIL on 1.13 (recorded):
* Legacy `Base.llvmcall(("declare ptr @__bennett_qalloc(i64, i64)", "%r = call ...\nret ptr %r"), ...)` (`routes.jl` `RD0_SRC`): the second string is taken as the *entry-function name*; the emitted method just throws: `ir/rD0_alloc.unopt.ll` contains `c"Module IR does not contain specified entry function\00"` and `call void @ijl_error(...)`.
* Body-only string `Base.llvmcall("%r = call ptr @__bennett_qalloc(i64 0, i64 %0)\nret ptr %r", ...)` (`RD1_SRC`): fails because the callee cannot be declared: `ir/rD1_alloc.unopt.ll`: `Failed to parse LLVM assembly: ... error: use of undefined value '@__bennett_qalloc'`. So the declaration must be in the `(module_ir, "entry")` form.

### Why ccall is indirect, and GPUCompiler

GPUCompiler.jl 2.19.0 / LLVM.jl 10.4.2 installed in `/tmp/bennett-emission-jl` (no errors). `ir_gpucompiler/kB.unopt.ll` shows the full lazy-binding machinery in the module itself:

```
@ccall___bennett_gate_562 = local_unnamed_addr global ptr null
@jlplt___bennett_gate_563_got = local_unnamed_addr global ptr @jlplt___bennett_gate_563 #0
define void @julia_kB_560(ptr %"h::Ptr") local_unnamed_addr #1 {
  %__bennett_gate = load atomic ptr, ptr @jlplt___bennett_gate_563_got unordered, align 8
  call void %__bennett_gate(i32 1, ptr %"h::Ptr", i64 0)
define private void @jlplt___bennett_gate_563(i32 %0, ptr %1, i64 %2) {   ; lazy trampoline
  %__bennett_gate.found = call ptr @ijl_load_and_lookup(ptr null, ptr @_j_str___bennett_gate_1, ptr @jl_RTLD_DEFAULT_handle)
  store atomic ptr %__bennett_gate.found, ptr @ccall___bennett_gate_562 release, align 8
  store atomic ptr %4, ptr @jlplt___bennett_gate_563_got release, align 8
attributes #0 = { "julia.fname"="__bennett_gate" "julia.libidx"="0" }
```

i.e. the GOT is initialised to a *private lazily-binding trampoline* `@jlplt___bennett_gate_563` that calls `ijl_load_and_lookup` (needs the Julia runtime symbols `ijl_load_and_lookup`, `jl_RTLD_DEFAULT_handle`) on first call. With a library: `ijl_load_and_lookup(ptr @_j_str__home_tobias_..._so, ptr @_j_str___bennett_gate_2, ptr @ccalllib_libbennett_stub_so1667)`. `kV` (variadic @ccall) has the inline `dlsym` path with no GOT at all. `kL` (llvmcall) is direct: `call void @__bennett_gate(i32 1, ptr %0, i64 0)`, `declare void @__bennett_gate(i32, ptr, i64) local_unnamed_addr`; after LLVM 20 `lto-pre-link<O2>`: `tail call void @__bennett_gate(i32 1, ptr %"h::Ptr", i64 0)`, still no attributes on the declaration (`ir_gpucompiler/kL.lto-pre-link-O2.ll`).
StaticCompiler.jl installed OK (warning only: `Imported binding Clang_jll.clang was undeclared at import time during import to StaticCompiler`; `StaticTools` was not installed so `using StaticTools` failed in my first draft, see below). `generate_obj` on a function using `ccall(:__bennett_qalloc ...)` produced `ir_staticcompiler/kS.o`; `nm ir_staticcompiler/kS.o` shows NO undefined `__bennett_*` symbol, only `U ijl_load_and_lookup`, `U jl_RTLD_DEFAULT_handle` plus defined `D jlplt___bennett_gate_7222_got` etc., and `objdump -dr` shows `call *(%rax)` through the GOT slots. So even StaticCompiler's output does not yield link-time-visible undefined markers for `ccall`.
Failed route to record: `using StaticCompiler, StaticTools` -> `ArgumentError: Package StaticTools not found in current path.` (first draft; removed the unneeded import). `StaticCompiler.static_llvm` does not exist in the installed version (`UndefVarError: static_llvm not defined in StaticCompiler`).

## 3. Representations (Julia)

* Handle: `Ptr{Cvoid}` is `ptr` in addrspace 0, no param attrs (`ptr %"h::Ptr"`). Julia GC object pointers would be `ptr addrspace(10)` but a `Ptr` is never one. `Vector{Ptr{Cvoid}}` handle table: ordinary array; elements `ptr` loaded from the array data, indexing is bounds-checked (`throw_boundserror` branches in `case_B.opt.ll`), not a marker.
* Marker call args via ccall carry NO attributes: `call void %__bennett_rot(i32 3, ptr %"h::Ptr", i64 1, double %"th::Float64")` (no `noundef`, no `zeroext`).
* `Bool` return: ccall `Bool` is `i8`, with no `zeroext`: `%2 = call i8 %__bennett_measure(ptr %"h::Ptr", i64 0)` (`ir/rB_measure.opt.ll`); the ABI says `zeroext i1`, so a callee mismatch is only benign at the C ABI level because i8 returns are in `al`. The dialect should not rely on `i1` for the ccall routes. llvmcall: `zeroext i1` exactly as the user writes the declare.
* Julia function entry: `define swiftcc ... (ptr nonnull swiftself "gcstack" %pgcstack_arg, i64 zeroext %"n::UInt64")`; marker calls inside use the C calling convention (default cc).
* Region function pointer (`ccall(:__bennett_ctrl, Cvoid, (H, UInt64, Ptr{Cvoid}, UInt64, Ptr{Cvoid}), ...)` with `@cfunction(body, Cvoid, (Ptr{Cvoid},))`):
  * `const BODY = @cfunction(...)` global: the pointer is baked as an integer constant, no symbol: `call void %__bennett_ctrl(ptr %"h::Ptr", i64 0, ptr inttoptr (i64 127079231243584 to ptr), i64 8, ptr %10)` (`ir/rF_ctrl.unopt.ll`; `ptr nonnull inttoptr (...)` in `.opt.ll`).
  * literal `@cfunction` inside the function (`rF2_ctrl`): a named wrapper defined in the module: `call void %__bennett_ctrl(ptr %"h::Ptr", i64 0, ptr @jlcapi_body_896, i64 8, ptr %10)`, with
    ```
    define void @jlcapi_body_896(ptr %0) #6 {
      %6 = call ptr @jl_get_abi_converter(ptr %current_task3, ptr @0)
      call swiftcc void %guard_res(ptr nonnull swiftself "gcstack" %pgcstack, ptr %0)
    ```
    and in the opt module `declare swiftcc void @j_body_914(ptr nonnull swiftself "gcstack", ptr) #7`: the region body (and thus the markers inside it) is NOT in this module; `jlcapi_body_N` only forwards through a runtime-resolved ABI converter pointer (`%guard_res`), after a world-age guard.
  * closure `@cfunction($f, ...)` (`rG_closure`): `%.ptr = load ptr, ptr %2, ...` then `call void %__bennett_ctrl(ptr %"h::Ptr", i64 0, ptr %.ptr, i64 8, ptr null)`; the pointer is loaded at run time (the module also defines `jlcapi_#rG_closure##0_944make`, a constructor for the closure's C-callable thunk), so it is not a static symbol.
* Env: `Ref(Env(h,3,theta))` heap object, passed by `pointer_from_objref(e)` (`call nonnull ptr @julia.pointer_from_objref(ptr addrspace(11) %9)`) or `unsafe_convert`; `%10` above. It is a GC object, so `GC.@preserve` is required (`llvm.julia.gc_preserve_begin/end` tokens bracket the call).

## 4. Variadic marker

Emittable by (i) `ccall(:f, Cvoid, (H, UInt64, Ptr{Cvoid}, UInt64, Cint...), a, b, c, d, Cint(1))` — `rH3_ctrl_v`: `call void (ptr, i64, ptr, i64, ...) %2(ptr %"h::Ptr", i64 0, ptr null, i64 8, i32 1)`; (ii) `@ccall f(a::T, ...; 1::Cint, 2.5::Cdouble, h::H)::Cvoid` — `rH_ctrl_v`: `call void (ptr, i64, ptr, i64, ...) %2(ptr %"h::Ptr", i64 0, ptr null, i64 8, i32 1, double 2.500000e+00, ptr %"h::Ptr")`; (iii) llvmcall: direct `@__bennett_ctrl_v` (above). The plain-`ccall` spelling with `;` in the type tuple is a syntax error: `rH4_ctrl_v.ERROR.txt` = `syntax: more arguments than types for ccall`. Also (i) and (ii) use the lazy `dlsym` path: `%__bennett_ctrl_v.found = call ptr @ijl_load_and_lookup(ptr null, ptr @"_j_str___bennett_ctrl_v#1", ptr @jl_RTLD_DEFAULT_handle)`, i.e. the callee is a phi of two pointers, not a symbol; the call has a proper variadic function type.

## 5. Verdict

* Attributes: no ccall or llvmcall route adds any of `memory(...)`, `readnone`, `readonly`, `writeonly`, `argmemonly`, `inaccessiblememonly`, `willreturn`, `speculatable` to a marker call site or declaration. ccall call sites have NO attributes at all (and no declaration exists); llvmcall `declare`s have none (only `local_unnamed_addr` after optimisation). (The `memory(...)`/`willreturn`/`speculatable` groups in the same Julia modules belong to Julia runtime intrinsics, e.g. `declare nonnull ptr @julia.pointer_from_objref(ptr) local_unnamed_addr #6` with `attributes #6 = { mustprogress nofree norecurse nosync nounwind speculatable willreturn memory(none) }` in `ir/case_D.opt.ll`; no `__bennett` call or declaration references such a group.) Because ccall callees are opaque pointers, LLVM must assume the worst: legality-positive by construction, but the markers are not recognisable by name.
* Does it meet the positive legality requirement? Yes for attributes (all routes); BUT ccall routes (A, B, C, variadic C, E) fail the *recognisability* requirement: there is no `call @__bennett_*` and no `declare`, so a by-name extractor sees nothing. Only `Base.llvmcall` with `(module_ir, "entry")` form (route D) emits the contract shape. Also relevant: (a) Bool is `i8` through ccall; (b) region function pointers from `@cfunction` are either raw integer constants or `jlcapi_*` forwarding wrappers whose body lives in a different module; marker calls inside Julia region bodies are only reachable via an indirect call; (c) `invoke`/exceptions: Julia emits plain `call` for ccall and llvmcall (no landing pads, no `nounwind` either).
