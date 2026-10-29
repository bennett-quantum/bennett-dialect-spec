# Rust (rustc 1.99.1, LLVM 23) emission notes

Sources: `bennett_emit.rs` (markers declared in `extern "C" { ... }`, plus a second `extern "C-unwind"` block redeclaring `__bennett_qfree`/`__bennett_gate` via `#[link_name]`), and `bennett_emit_cunwind.rs` (the whole marker block is `extern "C-unwind"`). Both compile with `rustc --edition 2021` (edition 2015 default fails on `core::`). Regions: `extern "C" fn body(*mut c_void)`, `#[repr(C)] struct Env`, and a closure route (a zero-sized closure `F` turned into `bregion` by a generic `extern "C" fn tramp<F: Fn(&mut Env)>`; Rust cannot coerce a closure directly to `extern "C" fn`). `Guard` has a `Drop` that calls `__bennett_qfree`, and `rt_may_unwind` may panic so the unwind edge exists. Handle table: `[*mut bq_opaque; 4]` indexed by `(x & 3) as usize`.

Files: `bennett_emit.O0.ll` (`rustc --emit=llvm-ir -C opt-level=0`), `bennett_emit.O2.bc/.ll` (`--emit=llvm-bc -C opt-level=2`), `bennett_emit.lto.bc/.ll` (`-C opt-level=2 -C linker-plugin-lto`; this is the pre-link bitcode a linker plugin receives), and the same O0 / lto pair for `bennett_emit_cunwind.rs`. `.ll` produced with the rustup `llvm-dis`. (`bennett_emit.O2.ll` and `.lto.ll` have identical marker declarations/calls.)

## 1. Declarations, attributes (quoted)

`bennett_emit.O0.ll`:

```
declare void @__bennett_gate(i32, ptr, i64) unnamed_addr #0
declare void @__bennett_rot(i32, ptr, i64, double) unnamed_addr #0
declare void @__bennett_qfree(ptr) unnamed_addr #0
declare ptr @__bennett_qalloc(i64, i64) unnamed_addr #0
declare zeroext i1 @__bennett_measure(ptr, i64) unnamed_addr #0
declare void @__bennett_ctrl(ptr, i64, ptr, i64, ptr) unnamed_addr #0
declare void @__bennett_ctrl_v(ptr, i64, ptr, i64, ...) unnamed_addr #0
attributes #0 = { nounwind nonlazybind uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
```

`unnamed_addr` and `nounwind` are on every declaration of an `extern "C"` function. (`nonlazybind uwtable` etc. are copied from the module defaults; `nonlazybind` has no effect on a pure declaration here.) No `noundef` at O0.

Call sites at O0: `call void @__bennett_gate(i32 5, ptr %_3, i64 %_4) #13` with `attributes #13 = { nounwind }` — a call-site `nounwind` (from the `extern "C"` ABI) on every non-unwinding call. Return: `%_9 = call zeroext i1 @__bennett_measure(ptr %h, i64 0) #13`.

LTO/O2 IR (`bennett_emit.lto.ll`) adds parameter/return attributes inferred from the Rust types:

```
declare noundef ptr @__bennett_qalloc(i64 noundef, i64 noundef) unnamed_addr #0
declare noundef zeroext i1 @__bennett_measure(ptr noundef, i64 noundef) unnamed_addr #0
declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef nonnull, i64 noundef, ptr noundef) unnamed_addr #0
declare void @__bennett_adj(ptr noundef nonnull, ptr noundef) unnamed_addr #0
declare void @__bennett_compute(ptr noundef nonnull, ptr noundef nonnull, ptr noundef) unnamed_addr #0
declare void @__bennett_ctrl_v(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ...) unnamed_addr #0
attributes #0 = { nounwind nonlazybind uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
```

New relative to C: `noundef` on the *return* of `qalloc`/`qborrow`/`measure`; `nonnull` on each `bregion` parameter (Rust `extern "C" fn` pointers are non-null; a mere `fn` pointer type implies `nonnull` and the front end puts it on the declaration, not only the call site); `unnamed_addr` on declarations. Note `__bennett_ctrl_v`'s region parameter is `*mut c_void`, so no `nonnull`.
Call sites at O2: `tail call void @__bennett_gate(i32 noundef 5, ptr noundef %_3.i, i64 noundef %_4.i) #6, !noalias !8` with `#6 = { nounwind }`; the variadic one: `call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr noundef %h, i64 noundef 0, ptr noundef nonnull @_RNvCsaOknTnIz6g7_12bennett_emit4body, i64 noundef 8, i32 noundef 1, double noundef 2.500000e+00, ptr noundef %h) #6`. Note the extra metadata `!noalias !N` appears on a few call sites after inlining (scoped-noalias from inlined `&mut` params); it does not appear on the declaration. These call sites are `nounwind`.

None of `memory(...)`, `readnone`, `readonly`, `writeonly`, `argmemonly`, `inaccessiblememonly`, `willreturn`, `speculatable` is present on any marker declaration or call site (`grep` of `^declare.*__bennett` and `__bennett.*#` in all four .ll files).

### `extern "C"` vs `extern "C-unwind"`

* All `extern "C"` (default): declarations and call sites `nounwind`, all markers emitted as `call` — never `invoke` — even when the Rust caller has a `Drop` guard whose cleanup would be needed on unwind.
* All `extern "C-unwind"` (`bennett_emit_cunwind.O0.ll`, `.lto.ll`): declarations are NOT `nounwind` and nearly every marker call becomes `invoke`. Because `case_entry` is itself `extern "C"` (cannot unwind), rustc wraps its body so that every unwinding call has an abort edge: `%h = invoke ptr @__bennett_qalloc(i64 0, i64 4)` / `to label %bb1 unwind label %terminate` (O0 line 312-313), which targets `panic_cannot_unwind`. The calls made while `Guard` is live unwind to the real cleanup: `invoke void @__bennett_gate(i32 noundef 6, ptr noundef %_51, i64 noundef 0)  to label %bb26 unwind label %cleanup` (LTO IR line 175). Other examples: `%_9 = invoke zeroext i1 @__bennett_measure(ptr %h, i64 0)`, `invoke void @__bennett_ctrl(ptr %h, i64 0, ptr @_RNvCsbWvCnYHbl8o_20bennett_emit_cunwind4body, i64 8, ptr %e)`; LTO IR: 29 `invoke ... __bennett` vs 2 plain `call ... __bennett` (grep counts), `declare void @__bennett_qfree(ptr noundef) unnamed_addr #1` where `#1` has no `nounwind`, and `invoke void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(...)`.
* Mixed declarations of one symbol in one crate (my first source): rustc warns `clashing_extern_declarations` and emits ONE `declare` (the first, `nounwind`) but both call-site flavours: `invoke void @__bennett_gate(i32 6, ptr %_77, i64 0)` (C-unwind call site) against `declare void @__bennett_gate(i32, ptr, i64) unnamed_addr #0` with `#0 = { nounwind ... }`. A `nounwind` declaration with an `invoke` call site is accepted by LLVM, but the declaration attribute then asserts no unwinding while the IR also has an unwind edge — avoid mixing.

## 2. Direct call by name

Yes. `call void @__bennett_gate(...)`, no PLT/GOT indirection. Function pointers are direct constants `ptr @_RNvCsaOknTnIz6g7_12bennett_emit4body` (v0-mangled `body`, `define internal void @_RNvCsaOknTnIz6g7_12bennett_emit4body(ptr %p) unnamed_addr #0` at O0, `ptr nofree noundef readonly captures(none) %p` at O2 — those are the region's own parameter attributes). Note `internal` linkage for the region even though `extern "C" fn body` has no `#[no_mangle]`; it is only kept alive because of the address-taken reference.

## 3. Representations

* Handle: `ptr` addrspace 0 (`*mut bq_opaque` where `bq_opaque` is a `#[repr(C)] struct { _p: [u8;0] }`); params `ptr noundef` at O2.
* `bool`: `zeroext i1` return, `noundef zeroext i1` at O2 (`declare noundef zeroext i1 @__bennett_measure(ptr noundef, i64 noundef)`). A Rust `bool` param, if any, would be `i1 zeroext` the same way.
* Region: `extern "C" fn(*mut c_void)` value -> `ptr` constant (the symbol). Env: `&mut e as *mut Env as *mut c_void` -> `ptr %e` (`%e = alloca [24 x i8], align 8`).
* Closure route: the closure is not itself passed. `region_of::<F>` returns `tramp::<F>`, an `extern "C" fn` generic over the closure type. At O0 the call site gets the pointer by *calling* `region_of` (`%f = invoke ptr @_RINvCsaOknTnIz6g7_12bennett_emit9region_ofNCNvB2_10case_entry0EB2_()`, then `call void @__bennett_ctrl(ptr %h, i64 1, ptr %f, i64 8, ptr %e) #13`), i.e. a runtime value at O0 and a constant `ptr nonnull @_RINvCsaOknTnIz6g7_12bennett_emit5trampNCNvB2_10case_entry0EB2_` at O2/LTO. The closure body is a separate `{closure#0}` function invoked from `tramp`; the symbol handed to the marker is the trampoline (same identity story as the C++ `__invoke` thunk).

## 4. Variadic

Emittable. Rust *declares* C-variadic externs (`fn __bennett_ctrl_v(q: bq, qi: u64, f: *mut c_void, budget: u64, ...)`) and *calls* them (needs `unsafe`); the call is `call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr %h, i64 0, ptr @..._4body, i64 8, i32 1, double 2.500000e+00, ptr %h) #13`. Rust requires the variadic args to be `i32`/`f64`/pointers-width types (no `f32`/`u8`), as in C promotion.

## 5. Verdict

PASS on the positive requirement for the markers themselves; no forbidden attribute is added. Differences that matter: (a) default `extern "C"` makes every marker declaration AND call site `nounwind`, so unwinding through a marker is UB and no `invoke` appears. A pass or the dialect must not assume `nounwind` is a legality problem (it is on the L2 observation list); (b) `extern "C-unwind"` removes `nounwind` and yields `invoke` everywhere; (c) `nonnull` on `bregion` params of the declaration. The driver need not strip anything for L2, but must handle `nounwind` and (for C-unwind) `invoke`.
