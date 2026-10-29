; CASE: loop-unswitch-nontrivial
; HAZARD: simple-loop-unswitch<nontrivial> (and trivial unswitching) on a loop with a loop-invariant classical condition and a loop-invariant measurement result guarding different marker calls: the loop is cloned per condition value and the markers are duplicated into both versions
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
  %h = call ptr @__bennett_qalloc(i64 0, i64 4)
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 0)
  %mode = and i64 %x, 1
  %useb = icmp ne i64 %mode, 0
  %n0 = lshr i64 %x, 1
  %n = and i64 %n0, 7
  %n1 = add i64 %n, 1
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %latch ]
  %acc = phi i64 [ 0, %entry ], [ %acc.next, %latch ]
  %q = and i64 %i, 3
  br i1 %useb, label %b, label %a
a:
  call void @__bennett_gate(i32 4, ptr %h, i64 %q)
  br label %mid
b:
  call void @__bennett_gate(i32 5, ptr %h, i64 %q)
  call void @__bennett_gate(i32 6, ptr %h, i64 %q)
  br label %mid
mid:
  br i1 %m, label %mone, label %latch
mone:
  call void @__bennett_gate(i32 8, ptr %h, i64 %q)
  br label %latch
latch:
  %acc.next = add i64 %acc, %q
  %i.next = add nuw nsw i64 %i, 1
  %d = icmp eq i64 %i.next, %n1
  br i1 %d, label %exit, label %loop
exit:
  call void @__bennett_qfree(ptr %h)
  ret i64 %acc.next
}
