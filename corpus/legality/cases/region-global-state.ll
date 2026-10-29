; CASE: region-global-state
; HAZARD: ipsccp, globalopt and globals-aa on an internal global written only inside an internal region body that is reachable only through __bennett_compute (callback from an external declaration): passes must not treat the global as constant, never-stored, or unmodified across the marker
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

@acc = internal global i64 0
@hreg = internal global ptr null

define internal void @bump(ptr %e) {
  %h = load ptr, ptr @hreg
  call void @__bennett_gate(i32 2, ptr %h, i64 0)
  %a = load i64, ptr @acc
  %a1 = add i64 %a, 3
  store i64 %a1, ptr @acc
  ret void
}

define internal void @peek(ptr %e) {
  %h = load ptr, ptr @hreg
  %a = load i64, ptr @acc
  %i = and i64 %a, 1
  call void @__bennett_gate(i32 5, ptr %h, i64 %i)
  ret void
}

define i64 @case_entry(i64 %x) {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  store ptr %h, ptr @hreg
  store i64 %x, ptr @acc
  %before = load i64, ptr @acc
  call void @__bennett_compute(ptr @bump, ptr @peek, ptr null)
  %after = load i64, ptr @acc
  call void @__bennett_qfree(ptr %h)
  %d = sub i64 %after, %before
  %r = mul i64 %d, 100
  %r2 = add i64 %r, %after
  ret i64 %r2
}
