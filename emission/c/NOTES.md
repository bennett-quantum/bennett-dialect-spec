# C (clang 18.1) emission notes

Source: `bennett_emit.c` (all 15 §1 markers; `case_entry` does alloc, gate, run-time-angle rot, gate2, measure+branch, ctrl region with `struct env`, 4-entry handle table indexed by `x & 3`, variadic `ctrl_v`, adj/compute/reversible/inplace, qload/qstore, free).
Regenerate: see commands at the bottom.

Files: `bennett_emit.O0.ll` (`clang -O0 -Xclang -disable-O0-optnone -S -emit-llvm`), `bennett_emit.O0.fexceptions.ll` (same plus `-fexceptions`), `bennett_emit.O2.ll` (`-O2 -S -emit-llvm`), `bennett_emit.lto.o` / `bennett_emit.lto.ll` (`clang -flto -O2 -c`, then `llvm-dis`; this is the lto-pre-link bitcode the linker plugin receives).

## 1. Declarations, attribute groups, parameter attributes

Unoptimised, quoted from `bennett_emit.O0.ll`:

```
declare ptr @__bennett_qalloc(i64 noundef, i64 noundef) #1
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef) #1
declare void @__bennett_rot(i32 noundef, ptr noundef, i64 noundef, double noundef) #1
declare void @__bennett_gate2(i32 noundef, ptr noundef, i64 noundef, ptr noundef, i64 noundef) #1
declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef) #1
declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ptr noundef) #1
declare void @__bennett_ctrl_v(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ...) #1
declare void @__bennett_adj(ptr noundef, ptr noundef) #1
declare void @__bennett_compute(ptr noundef, ptr noundef, ptr noundef) #1
declare void @__bennett_reversible(ptr noundef, i64 noundef, ptr noundef) #1
declare void @__bennett_inplace(ptr noundef, ptr noundef, ptr noundef) #1
declare ptr @__bennett_qborrow(i64 noundef, i64 noundef) #1
declare void @__bennett_qload(ptr noundef, ptr noundef, ptr noundef) #1
declare void @__bennett_qstore(ptr noundef, ptr noundef, ptr noundef) #1
declare void @__bennett_qfree(ptr noundef) #1
attributes #1 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
```

Group #1 holds only string (target) attributes. No `nounwind`, no memory/`willreturn`/`speculatable` attributes.
Return of `__bennett_qalloc`/`qborrow` is plain `ptr` (no `noundef`, no `noalias`).

LTO-bound IR (`bennett_emit.lto.ll`, after clang `-O2 -flto`):

```
declare ptr @__bennett_qalloc(i64 noundef, i64 noundef) local_unnamed_addr #2
declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef) local_unnamed_addr #2
declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ptr noundef) local_unnamed_addr #2
declare void @__bennett_ctrl_v(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ...) local_unnamed_addr #2
attributes #2 = { "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
```

The only change on declarations is the added `local_unnamed_addr` (address-significance, harmless). Declarations never gain attributes in clang's `-O2` pipeline (all 15 checked with `grep ^declare.*__bennett bennett_emit.lto.ll`).

### Call-site attributes

At O0 (`bennett_emit.O0.ll`) call sites carry none:
`call void @__bennett_gate(i32 noundef 1, ptr noundef %12, i64 noundef 0)`.

In the `-O2 -flto` output every call site has `#3 = { nounwind }`:

```
%4 = tail call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 4) #3
%7 = tail call zeroext i1 @__bennett_measure(ptr noundef %4, i64 noundef 0) #3
call void @__bennett_ctrl(ptr noundef %4, i64 noundef 0, ptr noundef nonnull @body, i64 noundef 8, ptr noundef nonnull %2) #3
call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr noundef %4, i64 noundef 0, ptr noundef nonnull @body, i64 noundef 8, i32 noundef 1, double noundef 2.500000e+00, ptr noundef %4) #3
attributes #3 = { nounwind }
```

Where it comes from: not the front end. Verified by running single passes on `bennett_emit.O0.ll` with `opt-18`: `-passes='function(instcombine)'` produces `call void @__bennett_qfree(ptr noundef %45) #2` with `attributes #2 = { nounwind }`; `function-attrs`, `inferattrs`, `simplifycfg`, `inline`, `sroa` do not. Mechanism: the caller `case_entry` is `nounwind` (C without `-fexceptions`), and InstCombine marks calls in a `nounwind` caller `nounwind`. Also `tail` is added to call sites, and `nonnull` is added to the `@body` function-pointer argument and to the env pointer (`ptr noundef nonnull @body`, `ptr noundef nonnull %2`), at the call site, not on the declaration.

Also seen (not on markers): `body` becomes `define internal void @body(ptr nocapture noundef readonly %0)`; the `readonly` is on body's own env parameter, not on a marker.

With `-fexceptions` (`bennett_emit.O0.fexceptions.ll`) the declaration is unchanged: `declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef) #1` and `attributes #1 = { "frame-pointer"="all" "no-trapping-math"="true" ... }`.

## 2. Direct call by name?

Yes: `call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 4)` (O0), `tail call ...` (LTO). Each marker is a `declare` and every call names it. Function-pointer arguments (`@body`) are direct references to the defining symbol (internal linkage `define internal void @body(ptr nocapture noundef readonly %0)` in the LTO IR; at O0 `define internal void @body(ptr noundef %0) #0` with `#0 = { noinline nounwind uwtable ... }`).

## 3. Representations

* Handle: `ptr` (address space 0), param attr `noundef`; no `nonnull`/`noalias`. `bq tab[4]` is `alloca [4 x ptr]`.
* `bool` return: `zeroext i1`, i.e. `declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef)`; call: `%21 = call zeroext i1 @__bennett_measure(ptr noundef %20, i64 noundef 0)`; no `noundef` on the return.
* `uint32_t op` -> `i32 noundef`, `uint64_t` -> `i64 noundef`, `double` -> `double noundef`.
* Region: `ptr noundef @body` (a direct constant reference); env: `ptr noundef %6` where `%6 = alloca %struct.env, align 8`.
* An env struct on the stack escapes into the marker call; at -O2 the call is `ptr noundef nonnull %2` and the struct fields are stored before the call (`store ptr %4, ptr %2` ...). Because the marker is an opaque call with no memory attributes, the stores cannot be sunk or removed.

## 4. Variadic marker

Emittable. `void __bennett_ctrl_v(bq, uint64_t, void *, uint64_t, ...)` gives
`declare void @__bennett_ctrl_v(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ...) #1` and
`call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr noundef %47, i64 noundef 0, ptr noundef @body, i64 noundef 8, i32 noundef 1, double noundef 2.500000e+00, ptr noundef %48)`.
The call carries an explicit function type (`void (ptr, i64, ptr, i64, ...)`). Default argument promotion applies (`int` stays `i32`, `float` would become `double`).

## 5. Verdict against the positive legality requirement

PASS. Clang 18 adds none of `memory(...)`, `readnone`, `readonly`, `writeonly`, `argmemonly`, `inaccessiblememonly`, `willreturn`, `speculatable` to any marker declaration or call site (O0, `-O2`, `-flto -O2`). Observations: call-site `nounwind` appears at `-O2` (from InstCombine because the caller is `nounwind`, see above); `local_unnamed_addr` on declarations; `nonnull`/`tail` on call sites. No driver-side strip needed for C; for `nounwind` see the C++ file (relevant once unwinding is possible).
Side note: `llvm.lifetime.start/end` (`memory(argmem: readwrite)`, `willreturn`) appear in the LTO IR for the env alloca; these are intrinsics, not markers.

## Commands
```
C=/usr/lib/llvm-18/bin/clang
$C -O0 -Xclang -disable-O0-optnone -S -emit-llvm bennett_emit.c -o bennett_emit.O0.ll
$C -O0 -Xclang -disable-O0-optnone -S -emit-llvm -fexceptions bennett_emit.c -o bennett_emit.O0.fexceptions.ll
$C -O2 -S -emit-llvm bennett_emit.c -o bennett_emit.O2.ll
$C -flto -O2 -c bennett_emit.c -o bennett_emit.lto.o && /usr/lib/llvm-18/bin/llvm-dis bennett_emit.lto.o -o bennett_emit.lto.ll
```
