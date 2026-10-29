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
