; CASE: loop-unroll-gates
; HAZARD: loop-unroll full (constant trip count 4, nested), partial and runtime unrolling (trip count from the input) of loops whose bodies are marker calls with induction-variable arguments; loop-unroll-and-jam on the nest; unrolled copies must issue exactly the original dynamic sequence, including the remainder loop
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
  br label %outer
outer:
  %i = phi i64 [ 0, %entry ], [ %i.next, %outer.latch ]
  br label %inner
inner:
  %j = phi i64 [ 0, %outer ], [ %j.next, %inner ]
  %op = trunc i64 %j to i32
  %op1 = add i32 %op, 20
  call void @__bennett_gate2(i32 %op1, ptr %h, i64 %i, ptr %h, i64 %j)
  %j.next = add nuw nsw i64 %j, 1
  %jd = icmp eq i64 %j.next, 4
  br i1 %jd, label %outer.latch, label %inner
outer.latch:
  %i.next = add nuw nsw i64 %i, 1
  %id = icmp eq i64 %i.next, 4
  br i1 %id, label %rt.pre, label %outer
rt.pre:
  %n = and i64 %x, 31
  %z = icmp eq i64 %n, 0
  br i1 %z, label %done, label %rt
rt:
  %k = phi i64 [ 0, %rt.pre ], [ %k.next, %rt ]
  %acc = phi i64 [ 0, %rt.pre ], [ %acc.next, %rt ]
  %q = and i64 %k, 3
  call void @__bennett_gate(i32 7, ptr %h, i64 %q)
  %acc.next = add i64 %acc, %k
  %k.next = add nuw nsw i64 %k, 1
  %kd = icmp eq i64 %k.next, %n
  br i1 %kd, label %done, label %rt
done:
  %r = phi i64 [ 0, %rt.pre ], [ %acc.next, %rt ]
  call void @__bennett_qfree(ptr %h)
  ret i64 %r
}
