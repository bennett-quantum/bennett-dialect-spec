; CASE: fp-rot-fastmath-reassoc
; HAZARD: reassociate, instcombine and loop-unroll on rot angles computed with fast-math flags (reassoc nsz contract arcp, as from -ffast-math or Julia @fastmath): the optimiser may reassociate ((x*0.1)+0.2)+0.3 into x*0.1+0.5, turn /3.0 into *(1/3.0) and fuse an accumulated sum, so the angle bits passed to the marker differ between builds for some inputs; LLVM-legal, but L1 compares angle bits
; INPUTS: 0..63
; EXPECT: probe
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
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %xf = sitofp i64 %x to double
  %a = fmul reassoc nsz arcp contract double %xf, 1.000000e-01
  %b = fadd reassoc nsz arcp contract double %a, 2.000000e-01
  %c = fadd reassoc nsz arcp contract double %b, 3.000000e-01
  call void @__bennett_rot(i32 1, ptr %h, i64 0, double %c)
  %d = fdiv reassoc nsz arcp contract double %xf, 3.000000e+00
  call void @__bennett_rot(i32 2, ptr %h, i64 0, double %d)
  br label %loop
loop:
  %k = phi i64 [ 0, %entry ], [ %k.next, %loop ]
  %acc = phi double [ 0.000000e+00, %entry ], [ %acc.next, %loop ]
  %acc.next = fadd reassoc nsz arcp contract double %acc, 1.000000e-01
  %k.next = add nuw nsw i64 %k, 1
  %done = icmp eq i64 %k.next, 10
  br i1 %done, label %out, label %loop
out:
  %e = fmul reassoc nsz arcp contract double %acc.next, %xf
  call void @__bennett_rot(i32 3, ptr %h, i64 0, double %e)
  call void @__bennett_qfree(ptr %h)
  ret i64 %x
}
