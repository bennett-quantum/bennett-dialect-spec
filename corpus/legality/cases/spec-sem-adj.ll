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
