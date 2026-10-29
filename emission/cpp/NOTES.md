# C++ (clang++ 18.1) emission notes

Source: `bennett_emit.cpp`. Markers are `extern "C"`. Uses 10 of the 15 markers (qalloc, qborrow, qfree, gate, gate2, rot, measure, ctrl, ctrl_v, adj); the other five have identical C-ABI declarations to C (see `../c/NOTES.md`). Extra C++ features: a captureless lambda used as the `ctrl` region, and an RAII `struct Scope` whose destructor calls `__bennett_qfree`, with markers and an external `may_throw` (a function that may unwind) inside its scope.

Files (each of `fexceptions`, `fno-exceptions`):
`bennett_emit.<m>.O0.ll` = `clang++ -O0 -Xclang -disable-O0-optnone -S -emit-llvm -<m>`;
`bennett_emit.<m>.lto.o/.lto.ll` = `clang++ -flto -O2 -<m> -c` + `llvm-dis`.

## 1. Declarations / attributes

Identical to C. `bennett_emit.fno-exceptions.O0.ll`:

```
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef) #1
attributes #1 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
```

`bennett_emit.fexceptions.O0.ll` has the same `declare ... #1` for every marker: `extern "C"` functions with no `noexcept`/`throw()` and no `__attribute__((nothrow))` are NOT marked `nounwind` by clang++, with or without `-fexceptions`. Group #1 has no `nounwind` and no memory attributes. Declared return `declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef) #1`, variadic `declare void @__bennett_ctrl_v(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ...) #1`.

LTO IR (`bennett_emit.fexceptions.lto.ll`): `declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef) local_unnamed_addr #2` with `#2` = target strings only. No marker declaration gains any attribute (10 of 10 checked, `grep '^declare.*@__bennett'`).

Call-site attributes:
* `-fexceptions` O0: none. Calls inside the scope with the destructor are `invoke` (below).
* `-fexceptions` LTO IR: calls outside any cleanup scope are plain `call void @__bennett_ctrl(ptr noundef %4, i64 noundef 1, ptr noundef nonnull @"_ZZ10case_entryEN3$_08__invokeEPv", i64 noundef 8, ptr noundef nonnull %2)` (NO call-site `nounwind`, since the caller can unwind); the `invoke`s have none either.
* `-fno-exceptions` LTO IR: `%23 = call ptr @__bennett_qborrow(i64 noundef 0, i64 noundef 1) #4`, `call void @__bennett_qfree(ptr noundef %23) #4`, `attributes #4 = { nounwind }` (the same InstCombine-in-nounwind-caller effect as in C; `case_entry` is `#0 = { mustprogress nounwind uwtable ...}`).

## 2. Direct call by name

Yes for `call` and `invoke` (`invoke void @__bennett_gate(i32 noundef 6, ptr noundef %56, i64 noundef 0)`).

## `invoke` / exceptions (the point of this variant)

With `-fexceptions`, a marker call inside a scope that has a live destructor is emitted as `invoke` with a landing pad (quoted from `bennett_emit.fexceptions.O0.ll`):

```
invoke void @__bennett_gate(i32 noundef 6, ptr noundef %56, i64 noundef 0)
        to label %57 unwind label %76
invoke void @_Z9may_throwm(i64 noundef %58)
invoke void @__bennett_gate(i32 noundef 7, ptr noundef %61, i64 noundef 0)
invoke void @__bennett_ctrl(ptr noundef %63, i64 noundef 0, ptr noundef @_ZL4bodyPv, i64 noundef 8, ptr noundef %6)
%77 = landingpad { ptr, i32 }
```

Also inside the destructor itself, which is `noexcept` by default, so the unwind edge goes to `std::terminate`:

```
define linkonce_odr dso_local void @_ZN5ScopeD2Ev(...) ... personality ptr @__gxx_personality_v0 {
  invoke void @__bennett_qfree(ptr noundef %5)
          to label %6 unwind label %7
7:  %8 = landingpad { ptr, i32 }
          catch ptr null
  call void @__clang_call_terminate(ptr %9) #5
```

The same invokes survive into the LTO IR: `invoke void @__bennett_gate(i32 noundef 6, ptr noundef %23, i64 noundef 0)`, `invoke void @__bennett_ctrl(... nonnull @_ZL4bodyPv ...)`, `invoke void @__bennett_qfree(ptr noundef %23)` (x2). With `-fno-exceptions` there is no `invoke`, no `landingpad`, no personality (the same source has `call` everywhere). Consequence: with `-fexceptions` the dialect extractor must accept `invoke` of a marker (normal edge = marker semantics; the unwind edge exists only because the declaration is not `nounwind`) or the front end must declare markers `noexcept`/`nounwind` (then clang emits `call`). Because markers are not `nounwind`, a marker that really unwinds is representable; the runtime ABI should say markers never unwind, and the driver may add `nounwind` (this is not an eliminating/motion attribute under L2 but is an "observation" attribute).

## 3. Representations

Same as C: handle `ptr` addrspace 0 `noundef`; `bool` is `zeroext i1` return (`%24 = call zeroext i1 @__bennett_measure(ptr noundef %23, i64 noundef 0)`); env `ptr noundef %6` (alloca `%struct.env`).

Region function pointer:
* Plain function (`static void body(void*)`): `ptr noundef @_ZL4bodyPv` — a direct constant, mangled name (`internal` linkage); in LTO IR `ptr noundef nonnull @_ZL4bodyPv`.
* Captureless lambda converted to `bregion`: at O0 it is a runtime value from the conversion operator, not a constant:
  `%33 = call noundef ptr @"_ZZ10case_entryENK3$_0cvPFvPvEEv"(ptr ... %7)` then `call void @__bennett_ctrl(ptr noundef %32, i64 noundef 1, ptr noundef %33, i64 noundef 8, ptr noundef %6)` (`bennett_emit.fno-exceptions.O0.ll` lines 64-65). After `-O2` it folds to a constant naming a *thunk*, not the lambda body:
  `call void @__bennett_ctrl(ptr noundef %4, i64 noundef 1, ptr noundef nonnull @"_ZZ10case_entryEN3$_08__invokeEPv", i64 noundef 8, ptr noundef nonnull %2) #4`, where `@"_ZZ10case_entryEN3$_08__invokeEPv"` is `define internal void ... { call void @"_ZZ10case_entryENK3$_0clEPv"(ptr noundef nonnull align 1 dereferenceable(1) %3, ptr noundef %4) ; ret void }` (the real body is `operator()`, reached through the `__invoke` thunk). Relevant to L4 (region identity): the region symbol is the thunk, and an optimiser that inlines the thunk's body does not change the symbol passed.

## 4. Variadic

Emittable, same as C: `call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr noundef %47, i64 noundef 0, ptr noundef @_ZL4bodyPv, i64 noundef 8, i32 noundef 1, double noundef 2.500000e+00, ptr noundef %48)`. The `(void *)body` cast gives `ptr noundef @_ZL4bodyPv`.

## 5. Verdict

PASS on the positive requirement (no `memory`, `readnone`, `readonly`, `writeonly`, `argmemonly`, `inaccessiblememonly`, `willreturn`, `speculatable` on any marker declaration or call site), for both exception modes. Observations: `nounwind` on call sites appears only in `-fno-exceptions -O2`; with `-fexceptions` markers can appear under `invoke`; `local_unnamed_addr` on declarations. The dialect must handle `invoke` of markers (or mandate a no-exceptions front-end mode / `noexcept` marker declarations).
