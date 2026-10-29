; CASE: meas-speculation
; HAZARD: speculative-execution, simplifycfg speculation (SpeculativelyExecuteBB), instcombine select formation and licm hoisting of classical code next to markers in conditional blocks: cheap arithmetic in an arm that also contains a marker, and arms that contain only a marker; the marker must not be speculated (it is not speculatable) while the pure instructions may be
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
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 0)
  br i1 %m, label %then, label %join
then:
  %a = mul i64 %x, 3
  %b = add i64 %a, 1
  call void @__bennett_gate(i32 7, ptr %h, i64 1)
  br label %join
join:
  %v = phi i64 [ %b, %then ], [ %x, %entry ]
  %c = icmp ugt i64 %x, 40
  br i1 %c, label %then2, label %join2
then2:
  call void @__bennett_gate(i32 8, ptr %h, i64 0)
  br label %join2
join2:
  %d = and i64 %x, 4
  %e = icmp ne i64 %d, 0
  br i1 %e, label %then3, label %join3
then3:
  %s = lshr i64 %v, 1
  br label %join3
join3:
  %w = phi i64 [ %s, %then3 ], [ %v, %join2 ]
  call void @__bennett_qfree(ptr %h)
  ret i64 %w
}
