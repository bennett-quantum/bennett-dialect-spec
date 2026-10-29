; CASE: val-sroa-handle-table
; HAZARD: sroa / mem2reg / instcombine / gvn / dse on handle tables in allocas and globals: a [4 x ptr] alloca indexed by constants (fully promotable) and by a classical value (sroa/instcombine may rewrite a 2-element dynamic index into a select of handles), a {ptr, ptr, i64} struct of handles copied as a whole, a dead overwritten store of a handle (DSE), and an internal global [2 x ptr] table indexed by a measurement bit
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
%rec = type { ptr, ptr, i64 }
@gtab = internal global [2 x ptr] zeroinitializer

define i64 @case_entry(i64 %x) {
entry:
  %tab = alloca [4 x ptr]
  %two = alloca [2 x ptr]
  %r1 = alloca %rec
  %r2 = alloca %rec
  %h0 = call ptr @__bennett_qalloc(i64 0, i64 1)
  %h1 = call ptr @__bennett_qalloc(i64 0, i64 1)
  %h2 = call ptr @__bennett_qalloc(i64 0, i64 1)
  %h3 = call ptr @__bennett_qalloc(i64 0, i64 1)
  %p0 = getelementptr inbounds [4 x ptr], ptr %tab, i64 0, i64 0
  %p1 = getelementptr inbounds [4 x ptr], ptr %tab, i64 0, i64 1
  %p2 = getelementptr inbounds [4 x ptr], ptr %tab, i64 0, i64 2
  %p3 = getelementptr inbounds [4 x ptr], ptr %tab, i64 0, i64 3
  store ptr %h1, ptr %p0        ; dead: overwritten below
  store ptr %h0, ptr %p0
  store ptr %h1, ptr %p1
  store ptr %h2, ptr %p2
  store ptr %h3, ptr %p3
  %l2 = load ptr, ptr %p2
  call void @__bennett_gate(i32 1, ptr %l2, i64 0)
  ; dynamic index into a 2-entry table
  %q0 = getelementptr inbounds [2 x ptr], ptr %two, i64 0, i64 0
  %q1 = getelementptr inbounds [2 x ptr], ptr %two, i64 0, i64 1
  store ptr %h3, ptr %q0
  store ptr %h1, ptr %q1
  %b = and i64 %x, 1
  %qd = getelementptr inbounds [2 x ptr], ptr %two, i64 0, i64 %b
  %hd = load ptr, ptr %qd
  call void @__bennett_gate(i32 2, ptr %hd, i64 0)
  ; dynamic index into the 4-entry table
  %s = lshr i64 %x, 1
  %s3 = and i64 %s, 3
  %pd = getelementptr inbounds [4 x ptr], ptr %tab, i64 0, i64 %s3
  %h4 = load ptr, ptr %pd
  call void @__bennett_gate(i32 3, ptr %h4, i64 0)
  ; struct of handles copied whole
  %ra = getelementptr inbounds %rec, ptr %r1, i32 0, i32 0
  %rb = getelementptr inbounds %rec, ptr %r1, i32 0, i32 1
  %rc = getelementptr inbounds %rec, ptr %r1, i32 0, i32 2
  store ptr %h0, ptr %ra
  store ptr %h2, ptr %rb
  store i64 %x, ptr %rc
  %whole = load %rec, ptr %r1
  store %rec %whole, ptr %r2
  %r2b = getelementptr inbounds %rec, ptr %r2, i32 0, i32 1
  %hb = load ptr, ptr %r2b
  call void @__bennett_gate2(i32 3, ptr %h0, i64 0, ptr %hb, i64 0)
  ; global table indexed by a measurement
  store ptr %h0, ptr @gtab
  %g1 = getelementptr inbounds [2 x ptr], ptr @gtab, i64 0, i64 1
  store ptr %h1, ptr %g1
  %m = call zeroext i1 @__bennett_measure(ptr %h2, i64 0)
  %mi = zext i1 %m to i64
  %gp = getelementptr inbounds [2 x ptr], ptr @gtab, i64 0, i64 %mi
  %hg = load ptr, ptr %gp
  call void @__bennett_gate(i32 4, ptr %hg, i64 0)
  call void @__bennett_qfree(ptr %h3)
  call void @__bennett_qfree(ptr %h2)
  call void @__bennett_qfree(ptr %h1)
  call void @__bennett_qfree(ptr %h0)
  %r = add i64 %mi, %s3
  ret i64 %r
}
