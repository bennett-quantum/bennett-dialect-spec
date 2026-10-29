; CASE: meas-repeat-until-success
; HAZARD: bounded repeat-until-success loop: measure, break on 1, otherwise apply a correction gate and retry (max 8 tries); loop-rotate, loop-unroll (full, trip count bounded), simplifycfg and jump-threading on an exit condition that is a measurement result; the number of iterations depends only on the runtime's measurement bits
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
define i64 @case_entry(i64 %x) {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  %a = call ptr @__bennett_qalloc(i64 0, i64 1)
  %q = and i64 %x, 1
  br label %try
try:
  %n = phi i64 [ 0, %entry ], [ %n.next, %retry ]
  call void @__bennett_gate(i32 1, ptr %a, i64 0)
  call void @__bennett_gate2(i32 3, ptr %h, i64 %q, ptr %a, i64 0)
  %ok = call zeroext i1 @__bennett_measure(ptr %a, i64 0)
  br i1 %ok, label %success, label %retry
retry:
  call void @__bennett_gate(i32 8, ptr %h, i64 %q)
  %n.next = add nuw nsw i64 %n, 1
  %more = icmp ult i64 %n.next, 8
  br i1 %more, label %try, label %fail
success:
  call void @__bennett_qfree(ptr %a)
  call void @__bennett_qfree(ptr %h)
  ret i64 %n
fail:
  call void @__bennett_qfree(ptr %a)
  call void @__bennett_qfree(ptr %h)
  ret i64 99
}
