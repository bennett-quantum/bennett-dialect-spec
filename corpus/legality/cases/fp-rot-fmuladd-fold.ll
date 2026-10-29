; CASE: fp-rot-fmuladd-fold
; HAZARD: constant folding of llvm.fmuladd.f64 (what clang emits for a*b+c under the default -ffp-contract=on): instcombine/instsimplify fold it with a single rounding (fused), while llc -O0 on a target without FMA lowers it to fmul+fadd (two roundings); LangRef permits either, so the rot angle bits passed to the marker can differ between the baseline and the optimised build. Operands are loaded from internal globals so that only the optimiser (globalopt + instcombine) sees constants, as in the C source `double a=0.1,b=10.0,c=-1.0; rot(a*b+c)`
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
declare double @llvm.fmuladd.f64(double, double, double)

@ga = internal global double 1.000000e-01
@gb = internal global double 1.000000e+01
@gc = internal global double -1.000000e+00

define i64 @case_entry(i64 %x) {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %a = load double, ptr @ga
  %b = load double, ptr @gb
  %c = load double, ptr @gc
  ; exact: 0.1*10 = 1.0000000000000000555..., unfused rounds to 1.0 -> 0.0; fused -> 5.551115123125783e-17
  %t = call double @llvm.fmuladd.f64(double %a, double %b, double %c)
  call void @__bennett_rot(i32 1, ptr %h, i64 0, double %t)
  ; literal-constant form: instcombine folds at once
  %t2 = call double @llvm.fmuladd.f64(double 1.000000e-01, double 1.000000e+01, double -1.000000e+00)
  call void @__bennett_rot(i32 2, ptr %h, i64 0, double %t2)
  ; input-dependent form: never folded, both builds unfused (control)
  %xf = uitofp i64 %x to double
  %xa = fadd double %xf, 1.000000e-01
  %t3 = call double @llvm.fmuladd.f64(double %xa, double 1.000000e+01, double -1.000000e+00)
  call void @__bennett_rot(i32 3, ptr %h, i64 0, double %t3)
  call void @__bennett_qfree(ptr %h)
  ret i64 %x
}
