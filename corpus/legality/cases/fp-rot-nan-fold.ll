; CASE: fp-rot-nan-fold
; HAZARD: constant folding of an fp operation that produces NaN (0.0/0.0, inf-inf): APFloat folds to the positive default quiet NaN 0x7FF8000000000000, while x86-64 SSE at run time produces the negative "real indefinite" 0xFFF8000000000000; LangRef leaves the NaN sign/payload unspecified, so the rot angle bits differ between the -O0 baseline and an optimised build (globalopt + instcombine make the operands constant)
; INPUTS: 0..3
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
@gz = internal global double 0.000000e+00
@ginf = internal global double 0x7FF0000000000000

define i64 @case_entry(i64 %x) {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %z = load double, ptr @gz
  %n = fdiv double %z, %z
  call void @__bennett_rot(i32 1, ptr %h, i64 0, double %n)
  %i = load double, ptr @ginf
  %n2 = fsub double %i, %i
  call void @__bennett_rot(i32 2, ptr %h, i64 0, double %n2)
  call void @__bennett_qfree(ptr %h)
  ret i64 %x
}
