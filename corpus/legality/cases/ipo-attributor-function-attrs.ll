; CASE: ipo-attributor-function-attrs
; HAZARD: attributor, attributor-cgscc, function-attrs, rpo-function-attrs, inferattrs and openmp-opt-free IPO on helpers that call markers next to a pure twin helper: the pure helper gets memory(none)/willreturn/nounwind and its dead call is deleted; the marker-calling helpers must get none of those, and no attribute (memory/willreturn/speculatable/nocapture on handles) may be added to marker declarations; the attributor also sees an internal helper with a constant return value and a handle argument that is never captured by host code
; INPUTS: 0..63
; EXPECT: legal
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
define internal i64 @pure_helper(i64 %a) noinline {
  %b = mul i64 %a, 3
  ret i64 %b
}

define internal i64 @gate_helper(ptr %h, i64 %a) noinline {
  %i = and i64 %a, 1
  call void @__bennett_gate(i32 1, ptr %h, i64 %i)
  ret i64 7
}

define internal i1 @measure_helper(ptr %h) noinline {
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 0)
  ret i1 %m
}

define internal ptr @alloc_helper(i64 %n) noinline {
  %h = call ptr @__bennett_qalloc(i64 0, i64 %n)
  ret ptr %h
}

define i64 @case_entry(i64 %x) {
entry:
  %h = call ptr @alloc_helper(i64 2)
  %dead = call i64 @pure_helper(i64 %x)
  %dead2 = call i64 @gate_helper(ptr %h, i64 %x)
  %k = call i64 @gate_helper(ptr %h, i64 1)
  %m1 = call i1 @measure_helper(ptr %h)
  %m2 = call i1 @measure_helper(ptr %h)
  call void @__bennett_qfree(ptr %h)
  %z1 = zext i1 %m1 to i64
  %z2 = zext i1 %m2 to i64
  %s = shl i64 %z2, 1
  %r0 = or i64 %z1, %s
  %r = add i64 %r0, %k
  ret i64 %r
}
