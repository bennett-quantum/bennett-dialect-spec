; CASE: cfg-callsite-splitting
; HAZARD: callsite-splitting duplicating a marker call into its two predecessors when an argument is a phi of constants or a value constrained by the incoming branch condition; also a helper call whose argument is null-checked (the classic shape); the split call sites are then simplified independently
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
define internal void @apply_or_default(ptr %h, ptr %alt, i64 %i) noinline {
  %isnull = icmp eq ptr %alt, null
  br i1 %isnull, label %one, label %two
one:
  call void @__bennett_gate(i32 7, ptr %h, i64 %i)
  ret void
two:
  call void @__bennett_gate2(i32 3, ptr %h, i64 %i, ptr %alt, i64 0)
  ret void
}

define i64 @case_entry(i64 %x) {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 4)
  %b = and i64 %x, 1
  %c = icmp eq i64 %b, 0
  %y = lshr i64 %x, 1
  br i1 %c, label %p1, label %p2
p1:
  %z0 = icmp eq i64 %y, 5
  br i1 %z0, label %tail, label %other
p2:
  %z = icmp eq i64 %y, 3
  br i1 %z, label %tail, label %other
tail:
  %op = phi i32 [ 11, %p1 ], [ 12, %p2 ]
  call void @__bennett_gate(i32 %op, ptr %h, i64 %y)
  br label %next
other:
  br label %next
next:
  %alt = call ptr @__bennett_qalloc(i64 0, i64 1)
  %t = and i64 %x, 4
  %u = icmp ne i64 %t, 0
  %p = select i1 %u, ptr %alt, ptr null
  %pnull = icmp eq ptr %p, null
  br i1 %pnull, label %cs, label %cs2
cs2:
  br label %cs
cs:
  call void @apply_or_default(ptr %h, ptr %p, i64 2)
  call void @__bennett_qfree(ptr %alt)
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 2)
  call void @__bennett_qfree(ptr %h)
  %mz = zext i1 %m to i64
  ret i64 %mz
}
