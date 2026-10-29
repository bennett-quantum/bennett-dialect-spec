; CASE: meas-select-phi-switch
; HAZARD: measurement results flowing into select, phi, switch and arithmetic: simplifycfg converts diamonds on a measurement into selects (FoldTwoEntryPHINode), combines two measurement bits into a switch index that becomes a lookup table, instcombine rewrites zext/or/shl of i1 results; the measures themselves and the markers on each arm must stay in order
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
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  call void @__bennett_gate(i32 1, ptr %h, i64 1)
  %m0 = call zeroext i1 @__bennett_measure(ptr %h, i64 0)
  br i1 %m0, label %t, label %f
t:
  %vt = add i64 %x, 5
  br label %j
f:
  %vf = shl i64 %x, 2
  br label %j
j:
  %v = phi i64 [ %vt, %t ], [ %vf, %f ]
  %m1 = call zeroext i1 @__bennett_measure(ptr %h, i64 1)
  %z0 = zext i1 %m0 to i64
  %z1 = zext i1 %m1 to i64
  %z1s = shl i64 %z1, 1
  %code = or i64 %z1s, %z0
  switch i64 %code, label %c3 [
    i64 0, label %c0
    i64 1, label %c1
    i64 2, label %c2
  ]
c0:
  br label %k
c1:
  br label %k
c2:
  br label %k
c3:
  call void @__bennett_gate(i32 2, ptr %h, i64 0)
  br label %k
k:
  %w = phi i64 [ 7, %c0 ], [ 11, %c1 ], [ 13, %c2 ], [ 17, %c3 ]
  %sel = select i1 %m1, i64 %w, i64 %v
  %idx = select i1 %m0, i64 1, i64 0
  call void @__bennett_gate(i32 4, ptr %h, i64 %idx)
  call void @__bennett_qfree(ptr %h)
  %r = add i64 %sel, %w
  ret i64 %r
}
