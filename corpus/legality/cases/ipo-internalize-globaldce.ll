; CASE: ipo-internalize-globaldce
; HAZARD: internalize (the LTO step that makes every non-preserved symbol internal) followed by globaldce, globalopt, deadargelim and ipsccp: external region functions and an external marker-calling library function become internal; regions referenced only by marker calls must stay defined; an unused external helper that calls markers may be deleted (never executed). NOTE for the harness: run internalize with -internalize-public-api-list=case_entry, otherwise case_entry itself is internalized and deleted
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
define void @lib_region(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 70, ptr %h, i64 0)
  ret void
}

define void @lib_region_unused_env(ptr %e) {
  ret void
}

define void @lib_never_called(ptr %h) {
  call void @__bennett_gate(i32 71, ptr %h, i64 0)
  ret void
}

define i64 @lib_entangle(ptr %h, i64 %k) {
  call void @__bennett_gate2(i32 3, ptr %h, i64 0, ptr %h, i64 1)
  %r = add i64 %k, 1
  ret i64 %r
}

define i64 @case_entry(i64 %x) {
entry:
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  store ptr %h, ptr %e
  %r = call i64 @lib_entangle(ptr %h, i64 5)
  call void @__bennett_adj(ptr @lib_region, ptr %e)
  call void @__bennett_reversible(ptr @lib_region_unused_env, i64 1, ptr null)
  call void @__bennett_qfree(ptr %h)
  %s = add i64 %r, %x
  ret i64 %s
}
