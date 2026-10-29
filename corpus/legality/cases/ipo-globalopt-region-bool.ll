; CASE: ipo-globalopt-region-bool
; HAZARD: globalopt shrink-to-boolean of an internal global index (stored only with its initializer or one other value) that selects a region from a constant table; with instcombine the region operand of __bennett_adj becomes `select i1 %sel.b, @r_b, @r_a` (globalopt refuses to shrink a global of pointer type, hence the index); plus an internal global handle slot written once and read later
; INPUTS: 0..15
; EXPECT: probe

target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef)
declare void @__bennett_qfree(ptr noundef)
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef)
declare void @__bennett_adj(ptr noundef, ptr noundef)

@sel = internal global i64 0
@regions = internal constant [2 x ptr] [ptr @r_a, ptr @r_b]
@hglob = internal global ptr null

define void @r_a(ptr %e) {
  %h = load ptr, ptr @hglob
  call void @__bennett_gate(i32 20, ptr %h, i64 0)
  ret void
}

define void @r_b(ptr %e) {
  %h = load ptr, ptr @hglob
  call void @__bennett_gate(i32 21, ptr %h, i64 1)
  call void @__bennett_gate(i32 22, ptr %h, i64 0)
  ret void
}

define internal void @choose(i64 %x) noinline {
  %c = icmp ugt i64 %x, 9
  br i1 %c, label %set, label %out
set:
  store i64 1, ptr @sel
  br label %out
out:
  ret void
}

define i64 @case_entry(i64 %x) {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  store ptr %h, ptr @hglob
  call void @choose(i64 %x)
  %idx = load i64, ptr @sel
  %fp = getelementptr inbounds [2 x ptr], ptr @regions, i64 0, i64 %idx
  %f = load ptr, ptr %fp
  call void @__bennett_adj(ptr %f, ptr null)
  %h2 = load ptr, ptr @hglob
  call void @__bennett_qfree(ptr %h2)
  ret i64 %x
}
