; CASE: loop-licm-invariant-marker
; HAZARD: licm (hoist and sink, with MemorySSA), sink, gvn-hoist on a loop whose body contains loop-invariant marker calls (same handle, same constant arguments every iteration: a gate, a measure whose result is only used after the loop, and a qalloc/qfree pair); the marker calls must not be hoisted, sunk or promoted; the loop-invariant classical argument computation may be
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
  %n = and i64 %x, 7
  %n1 = add i64 %n, 1
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %loop ]
  %inv = mul i64 %x, 7
  %qi = and i64 %inv, 3
  call void @__bennett_gate(i32 6, ptr %h, i64 %qi)
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 1)
  %t = call ptr @__bennett_qalloc(i64 0, i64 1)
  call void @__bennett_gate2(i32 3, ptr %h, i64 %qi, ptr %t, i64 0)
  call void @__bennett_qfree(ptr %t)
  %i.next = add nuw nsw i64 %i, 1
  %d = icmp eq i64 %i.next, %n1
  br i1 %d, label %exit, label %loop
exit:
  call void @__bennett_qfree(ptr %h)
  %mz = zext i1 %m to i64
  %r = add i64 %mz, %qi
  ret i64 %r
}
