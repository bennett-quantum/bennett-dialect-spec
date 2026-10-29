; CASE: loop-deletion-marker-only
; HAZARD: loop-deletion, indvars (exit-value rewriting), loop-idiom and instcombine on loops whose only side effect is a marker call and whose classical result is computable in closed form after the loop (indvars replaces the exit value, making the loop otherwise dead); a mustprogress function with a loop that could otherwise be assumed finite and deleted
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
define i64 @case_entry(i64 %x) mustprogress {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %n = and i64 %x, 15
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %loop ]
  %acc = phi i64 [ 0, %entry ], [ %acc.next, %loop ]
  call void @__bennett_gate(i32 2, ptr %h, i64 0)
  %acc.next = add i64 %acc, 3
  %i.next = add nuw nsw i64 %i, 1
  %d = icmp ugt i64 %i.next, %n
  br i1 %d, label %exit, label %loop
exit:
  ; second loop: the marker result is discarded, the classical count is closed-form
  br label %loop2
loop2:
  %j = phi i64 [ 0, %exit ], [ %j.next, %loop2 ]
  %ign = call zeroext i1 @__bennett_measure(ptr %h, i64 0)
  %j.next = add nuw nsw i64 %j, 1
  %d2 = icmp eq i64 %j.next, 3
  br i1 %d2, label %exit2, label %loop2
exit2:
  call void @__bennett_qfree(ptr %h)
  %r = add i64 %acc.next, %j.next
  ret i64 %r
}
