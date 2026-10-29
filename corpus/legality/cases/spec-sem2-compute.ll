; CASE: spec-sem2-compute
; HAZARD: dialect 0.2 reference-semantics example (spec section 18.8): compute(f, use) with f = cx onto an ancilla and use = z on the ancilla; phase kickback leaves the ancilla clean
; INPUTS: 0..3
; EXPECT: legal
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64, i64)
declare void @__bennett_qfree(ptr)
declare void @__bennett_gate(i32, ptr, i64)
declare void @__bennett_gate2(i32, ptr, i64, ptr, i64)
declare void @__bennett_compute(ptr, ptr, ptr, ptr)

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
  call void @__bennett_compute(ptr @copy, ptr @kick, ptr null, ptr %e)
  call void @__bennett_gate(i32 2, ptr %a, i64 0)
  call void @__bennett_gate(i32 1, ptr %a, i64 0)
  call void @__bennett_qfree(ptr %b)
  call void @__bennett_qfree(ptr %a)
  ret i64 %x
}
