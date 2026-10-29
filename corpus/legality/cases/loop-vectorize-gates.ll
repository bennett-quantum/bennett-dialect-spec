; CASE: loop-vectorize-gates
; HAZARD: loop-vectorize, slp-vectorizer and loop-interleave on (1) a loop of gate calls over a register with a classical reduction alongside (must not vectorise or interleave the calls), and (2) straight-line code storing four freshly allocated handles into a handle table and reading them back by a classical index, then copying the escaped table element-wise into a second escaped table, which SLP turns into <N x ptr> vector loads/stores of handles
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
@coef = internal constant [16 x i64] [i64 3, i64 1, i64 4, i64 1, i64 5, i64 9, i64 2, i64 6, i64 5, i64 3, i64 5, i64 8, i64 9, i64 7, i64 9, i64 3]

; region over a table of four handles
define void @touch4(ptr %t) {
  %p3 = getelementptr inbounds [4 x ptr], ptr %t, i64 0, i64 3
  %h0 = load ptr, ptr %t
  %h3 = load ptr, ptr %p3
  call void @__bennett_gate2(i32 3, ptr %h0, i64 0, ptr %h3, i64 0)
  ret void
}

define i64 @case_entry(i64 %x) {
entry:
  %tbl = alloca [4 x ptr]
  %tbl2 = alloca [4 x ptr]
  %h = call ptr @__bennett_qalloc(i64 0, i64 16)
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %loop ]
  %s = phi i64 [ 0, %entry ], [ %s.next, %loop ]
  %cp = getelementptr inbounds [16 x i64], ptr @coef, i64 0, i64 %i
  %c = load i64, ptr %cp
  %cx = mul i64 %c, %x
  %s.next = add i64 %s, %cx
  %op = trunc i64 %c to i32
  call void @__bennett_gate(i32 %op, ptr %h, i64 %i)
  %i.next = add nuw nsw i64 %i, 1
  %d = icmp eq i64 %i.next, 16
  br i1 %d, label %slp, label %loop
slp:
  %a0 = call ptr @__bennett_qalloc(i64 0, i64 1)
  %a1 = call ptr @__bennett_qalloc(i64 0, i64 1)
  %a2 = call ptr @__bennett_qalloc(i64 0, i64 1)
  %a3 = call ptr @__bennett_qalloc(i64 0, i64 1)
  %t0 = getelementptr inbounds [4 x ptr], ptr %tbl, i64 0, i64 0
  %t1 = getelementptr inbounds [4 x ptr], ptr %tbl, i64 0, i64 1
  %t2 = getelementptr inbounds [4 x ptr], ptr %tbl, i64 0, i64 2
  %t3 = getelementptr inbounds [4 x ptr], ptr %tbl, i64 0, i64 3
  store ptr %a0, ptr %t0
  store ptr %a1, ptr %t1
  store ptr %a2, ptr %t2
  store ptr %a3, ptr %t3
  %sel = and i64 %x, 3
  %ts = getelementptr inbounds [4 x ptr], ptr %tbl, i64 0, i64 %sel
  %hs = load ptr, ptr %ts
  call void @__bennett_gate2(i32 3, ptr %h, i64 0, ptr %hs, i64 0)
  call void @__bennett_adj(ptr @touch4, ptr %tbl)
  ; element-wise copy of the escaped table into a second escaped table: SLP candidate
  %r0 = load ptr, ptr %t0
  %r1 = load ptr, ptr %t1
  %r2 = load ptr, ptr %t2
  %r3 = load ptr, ptr %t3
  %u0 = getelementptr inbounds [4 x ptr], ptr %tbl2, i64 0, i64 0
  %u1 = getelementptr inbounds [4 x ptr], ptr %tbl2, i64 0, i64 1
  %u2 = getelementptr inbounds [4 x ptr], ptr %tbl2, i64 0, i64 2
  %u3 = getelementptr inbounds [4 x ptr], ptr %tbl2, i64 0, i64 3
  store ptr %r0, ptr %u0
  store ptr %r1, ptr %u1
  store ptr %r2, ptr %u2
  store ptr %r3, ptr %u3
  call void @__bennett_adj(ptr @touch4, ptr %tbl2)
  call void @__bennett_qfree(ptr %r3)
  call void @__bennett_qfree(ptr %r2)
  call void @__bennett_qfree(ptr %r1)
  call void @__bennett_qfree(ptr %r0)
  call void @__bennett_qfree(ptr %h)
  ret i64 %s.next
}
