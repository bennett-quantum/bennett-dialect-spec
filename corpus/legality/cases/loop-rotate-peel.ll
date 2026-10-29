; CASE: loop-rotate-peel
; HAZARD: loop-rotate duplicating a header that contains a marker call into the preheader guard; loop-peel (loop-unroll with peeling, triggered by an i==0 condition that becomes invariant after peeling the first iteration) cloning the first iteration's markers; trip count from the input may be zero
; INPUTS: 0..31
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
define i64 @case_entry(i64 %x) {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 4)
  %n = and i64 %x, 15
  br label %header
header:
  %i = phi i64 [ 0, %entry ], [ %i.next, %latch ]
  %q = and i64 %i, 3
  call void @__bennett_gate(i32 1, ptr %h, i64 %q)
  %c = icmp ult i64 %i, %n
  br i1 %c, label %body, label %exit
body:
  %first = icmp eq i64 %i, 0
  br i1 %first, label %init, label %latch
init:
  call void @__bennett_gate(i32 9, ptr %h, i64 3)
  br label %latch
latch:
  call void @__bennett_gate2(i32 3, ptr %h, i64 %q, ptr %h, i64 3)
  %i.next = add nuw nsw i64 %i, 1
  br label %header
exit:
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 3)
  call void @__bennett_qfree(ptr %h)
  %mz = zext i1 %m to i64
  %r = add i64 %mz, %i
  ret i64 %r
}
