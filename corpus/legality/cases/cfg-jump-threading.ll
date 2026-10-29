; CASE: cfg-jump-threading
; HAZARD: jump-threading (and dfa-jump-threading) on two branches correlated through one measurement result and through a classical flag set in a marker-bearing block: blocks containing marker calls are duplicated onto threaded paths, so static call sites multiply while each path must keep its dynamic sequence
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
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 0)
  %big = icmp ugt i64 %x, 31
  br i1 %m, label %fix, label %mid
fix:
  call void @__bennett_gate(i32 2, ptr %h, i64 1)
  br label %mid
mid:
  %flag = phi i1 [ true, %fix ], [ %big, %entry ]
  call void @__bennett_gate(i32 3, ptr %h, i64 1)
  br i1 %flag, label %t, label %f
t:
  call void @__bennett_gate(i32 4, ptr %h, i64 0)
  br label %join
f:
  call void @__bennett_gate(i32 5, ptr %h, i64 0)
  br label %join
join:
  %r0 = phi i64 [ 1, %t ], [ 2, %f ]
  br i1 %m, label %again, label %done
again:
  call void @__bennett_gate(i32 6, ptr %h, i64 1)
  br label %done
done:
  %r1 = phi i64 [ 10, %again ], [ 20, %join ]
  call void @__bennett_qfree(ptr %h)
  %r = add i64 %r0, %r1
  ret i64 %r
}
