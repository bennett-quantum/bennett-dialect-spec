; CASE: val-cse-duplicate-markers
; HAZARD: early-cse (with and without MemorySSA), gvn, newgvn, instcombine and gvn-hoist on byte-identical repeated marker calls: two qalloc(0,1) in a row, two measure(h,0) in a row, gate twice with the same arguments (an involution: X;X), measure-gate-measure with the same arguments; none may be commoned, and the second qalloc must yield a distinct handle
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
  %h1 = call ptr @__bennett_qalloc(i64 0, i64 1)
  %h2 = call ptr @__bennett_qalloc(i64 0, i64 1)
  %i = and i64 %x, 0
  call void @__bennett_gate(i32 2, ptr %h1, i64 %i)
  call void @__bennett_gate(i32 2, ptr %h1, i64 0)
  %m1 = call zeroext i1 @__bennett_measure(ptr %h1, i64 0)
  %m2 = call zeroext i1 @__bennett_measure(ptr %h1, i64 0)
  call void @__bennett_gate(i32 1, ptr %h2, i64 0)
  %m3 = call zeroext i1 @__bennett_measure(ptr %h2, i64 0)
  call void @__bennett_gate(i32 1, ptr %h2, i64 0)
  %m4 = call zeroext i1 @__bennett_measure(ptr %h2, i64 0)
  %eq = icmp eq i1 %m1, %m2
  %eq2 = icmp eq i1 %m3, %m4
  %both = and i1 %eq, %eq2
  call void @__bennett_gate2(i32 3, ptr %h1, i64 0, ptr %h2, i64 0)
  call void @__bennett_qfree(ptr %h2)
  call void @__bennett_qfree(ptr %h1)
  %z1 = zext i1 %m1 to i64
  %z2 = zext i1 %m2 to i64
  %z3 = zext i1 %m3 to i64
  %z4 = zext i1 %m4 to i64
  %zb = zext i1 %both to i64
  %s1 = shl i64 %z2, 1
  %s2 = shl i64 %z3, 2
  %s3 = shl i64 %z4, 3
  %s4 = shl i64 %zb, 4
  %r1 = or i64 %z1, %s1
  %r2 = or i64 %r1, %s2
  %r3 = or i64 %r2, %s3
  %r = or i64 %r3, %s4
  ret i64 %r
}
