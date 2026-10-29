; CASE: fp-rot-exact-fold
; HAZARD: instcombine, sccp, loop-unroll + constant folding, licm and reassociate on rot angles computed by IEEE-exact fp arithmetic without fast-math flags (uitofp of the induction variable, fmul/fdiv by constants, fneg, fabs, llvm.sqrt, copysign, fptrunc/fpext round trips): folding must reproduce the run-time bits exactly
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
declare double @llvm.sqrt.f64(double)
declare double @llvm.fabs.f64(double)
declare double @llvm.copysign.f64(double, double)

define i64 @case_entry(i64 %x) {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 4)
  br label %loop
loop:
  %k = phi i64 [ 0, %entry ], [ %k.next, %loop ]
  %kf = uitofp i64 %k to double
  %t1 = fmul double %kf, 0x3FD921FB54442D18      ; pi/4
  %t2 = fdiv double %t1, 3.000000e+00
  %t3 = fneg double %t2
  call void @__bennett_rot(i32 1, ptr %h, i64 %k, double %t3)
  %s = call double @llvm.sqrt.f64(double %t1)
  call void @__bennett_rot(i32 2, ptr %h, i64 %k, double %s)
  %k.next = add nuw nsw i64 %k, 1
  %d = icmp eq i64 %k.next, 4
  br i1 %d, label %rest, label %loop
rest:
  %xf = sitofp i64 %x to double
  %a = fmul double %xf, 1.000000e-01
  %b = fadd double %a, 2.000000e-01
  %c = fadd double %b, 3.000000e-01
  call void @__bennett_rot(i32 3, ptr %h, i64 0, double %c)
  %n = fsub double 0.000000e+00, %c
  %ab = call double @llvm.fabs.f64(double %n)
  %cs = call double @llvm.copysign.f64(double %ab, double -1.000000e+00)
  call void @__bennett_rot(i32 4, ptr %h, i64 1, double %cs)
  %f32 = fptrunc double %a to float
  %f64 = fpext float %f32 to double
  call void @__bennett_rot(i32 5, ptr %h, i64 2, double %f64)
  call void @__bennett_qfree(ptr %h)
  ret i64 %x
}
