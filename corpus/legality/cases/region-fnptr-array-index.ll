; CASE: region-fnptr-array-index
; HAZARD: a region chosen from a function-pointer array indexed by the input, in three storage shapes: an internal constant global table (instcombine/sccp keep a load from a constant table), a stack array filled at run time (sroa/instcombine may turn a small dynamic index into selects of function constants), and an internal mutable global table written once (globalopt may mark it constant). Question: what operand shapes must the plugin resolve: constant / select-of-constants / phi-of-constants / load-from-constant-table / other
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
define void @ora0(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 50, ptr %h, i64 0)
  ret void
}
define void @ora1(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 51, ptr %h, i64 1)
  ret void
}
define void @ora2(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 52, ptr %h, i64 0)
  call void @__bennett_gate(i32 52, ptr %h, i64 1)
  ret void
}
define void @ora3(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 53, ptr %h, i64 1)
  ret void
}

@ctab = internal constant [4 x ptr] [ptr @ora0, ptr @ora1, ptr @ora2, ptr @ora3]
@mtab = internal global [4 x ptr] zeroinitializer

define i64 @case_entry(i64 %x) {
entry:
  %e = alloca ptr
  %stk = alloca [2 x ptr]
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  %q = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  ; (1) constant table
  %i0 = and i64 %x, 3
  %p0 = getelementptr inbounds [4 x ptr], ptr @ctab, i64 0, i64 %i0
  %f0 = load ptr, ptr %p0
  call void @__bennett_adj(ptr %f0, ptr %e)
  ; (2) stack array of two regions, dynamic index
  %s0 = getelementptr inbounds [2 x ptr], ptr %stk, i64 0, i64 0
  %s1 = getelementptr inbounds [2 x ptr], ptr %stk, i64 0, i64 1
  store ptr @ora3, ptr %s0
  store ptr @ora1, ptr %s1
  %i1a = lshr i64 %x, 2
  %i1 = and i64 %i1a, 1
  %ps = getelementptr inbounds [2 x ptr], ptr %stk, i64 0, i64 %i1
  %f1 = load ptr, ptr %ps
  call void @__bennett_ctrl(ptr %q, i64 0, ptr %f1, i64 8, ptr %e)
  ; (3) mutable global table, written once here
  store ptr @ora2, ptr @mtab
  %m1 = getelementptr inbounds [4 x ptr], ptr @mtab, i64 0, i64 1
  store ptr @ora0, ptr %m1
  %m2 = getelementptr inbounds [4 x ptr], ptr @mtab, i64 0, i64 2
  store ptr @ora1, ptr %m2
  %m3 = getelementptr inbounds [4 x ptr], ptr @mtab, i64 0, i64 3
  store ptr @ora3, ptr %m3
  %i2a = lshr i64 %x, 3
  %i2 = and i64 %i2a, 3
  %pm = getelementptr inbounds [4 x ptr], ptr @mtab, i64 0, i64 %i2
  %f2 = load ptr, ptr %pm
  call void @__bennett_reversible(ptr %f2, i64 16, ptr %e)
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 1)
  call void @__bennett_qfree(ptr %q)
  call void @__bennett_qfree(ptr %h)
  %z = zext i1 %m to i64
  ret i64 %z
}
