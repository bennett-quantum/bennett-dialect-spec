; CASE: cfg-hoist-sink-common
; HAZARD: simplifycfg hoist-common-insts / sink-common-insts, gvn-hoist and gvn-sink on identical and near-identical marker calls at the start and end of both arms of a measurement-controlled diamond; then select formation for the classical result; marker calls are hoisted above / sunk below the branch (one dynamic call per path must remain, in order, with the right arguments)
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
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 0)
  br i1 %m, label %one, label %zero
one:
  call void @__bennett_gate(i32 2, ptr %h, i64 1)
  call void @__bennett_gate(i32 3, ptr %h, i64 2)
  %a = add i64 %x, 1
  %ia = and i64 %x, 3
  call void @__bennett_gate(i32 4, ptr %h, i64 %ia)
  br label %join
zero:
  call void @__bennett_gate(i32 2, ptr %h, i64 1)
  call void @__bennett_gate(i32 5, ptr %h, i64 3)
  %b = mul i64 %x, 3
  %ib = lshr i64 %x, 4
  call void @__bennett_gate(i32 4, ptr %h, i64 %ib)
  br label %join
join:
  %r = phi i64 [ %a, %one ], [ %b, %zero ]
  call void @__bennett_qfree(ptr %h)
  ret i64 %r
}
