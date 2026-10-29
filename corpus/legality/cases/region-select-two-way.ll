; CASE: region-select-two-way
; HAZARD: simplifycfg sink-common-insts (+ FoldTwoEntryPHINode / select formation) on two-way ifs whose arms call the same region marker with a different region per arm: (a) __bennett_adj(@f | @g, env), expected to become one call with `select i1 %c, ptr @g, ptr @f`; (b) __bennett_ctrl where the control handle AND the region differ per arm (does the sink phi/select both operands?); (c) __bennett_compute with both bregion operands differing. Question: what operand shapes must the plugin resolve: constant / select-of-constants / phi-of-constants / load-from-constant-table / other
; INPUTS: 0..63
; EXPECT: probe
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef)
declare ptr @__bennett_qborrow(i64 noundef, i64 noundef)
declare void @__bennett_qfree(ptr noundef)
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef)
declare void @__bennett_gate2(i32 noundef, ptr noundef, i64 noundef, ptr noundef, i64 noundef)
declare void @__bennett_rot(i32 noundef, ptr noundef, i64 noundef, double noundef)
declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef)
declare void @__bennett_qload(ptr noundef, ptr noundef, ptr noundef)
declare void @__bennett_qstore(ptr noundef, ptr noundef, ptr noundef)
declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ptr noundef)
declare void @__bennett_adj(ptr noundef, ptr noundef)
declare void @__bennett_compute(ptr noundef, ptr noundef, ptr noundef)
declare void @__bennett_reversible(ptr noundef, i64 noundef, ptr noundef)
declare void @__bennett_inplace(ptr noundef, ptr noundef, ptr noundef)
define void @reg_f(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 40, ptr %h, i64 0)
  ret void
}
define void @reg_g(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 41, ptr %h, i64 1)
  ret void
}
define void @reg_u(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate2(i32 3, ptr %h, i64 0, ptr %h, i64 1)
  ret void
}

define i64 @case_entry(i64 %x) {
entry:
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  %qa = call ptr @__bennett_qalloc(i64 0, i64 1)
  %qb = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  %c0 = and i64 %x, 1
  %c = icmp ne i64 %c0, 0
  br i1 %c, label %a1, label %b1
a1:
  call void @__bennett_adj(ptr @reg_g, ptr %e)
  br label %j1
b1:
  call void @__bennett_adj(ptr @reg_f, ptr %e)
  br label %j1
j1:
  %d0 = and i64 %x, 2
  %d = icmp ne i64 %d0, 0
  br i1 %d, label %a2, label %b2
a2:
  call void @__bennett_ctrl(ptr %qa, i64 0, ptr @reg_f, i64 8, ptr %e)
  br label %j2
b2:
  call void @__bennett_ctrl(ptr %qb, i64 0, ptr @reg_g, i64 8, ptr %e)
  br label %j2
j2:
  %f0 = and i64 %x, 4
  %f = icmp ne i64 %f0, 0
  br i1 %f, label %a3, label %b3
a3:
  call void @__bennett_compute(ptr @reg_f, ptr @reg_u, ptr %e)
  br label %j3
b3:
  call void @__bennett_compute(ptr @reg_g, ptr @reg_f, ptr %e)
  br label %j3
j3:
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 0)
  call void @__bennett_qfree(ptr %qb)
  call void @__bennett_qfree(ptr %qa)
  call void @__bennett_qfree(ptr %h)
  %z = zext i1 %m to i64
  ret i64 %z
}
