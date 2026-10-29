; CASE: cfg-switch-op-table
; HAZARD: simplifycfg sink-common-insts + switch-to-lookup on a switch whose arms call the same marker with different constant op codes: the arms collapse into one __bennett_gate call whose op is a 7-way phi (switch-to-lookup turns it into a table only when every arm empties, see region-switch-fnptr-table); one arm has two markers and only its last may be sunk
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
  %h = call ptr @__bennett_qalloc(i64 0, i64 4)
  %s = and i64 %x, 7
  %t = lshr i64 %x, 3
  %qi = and i64 %t, 3
  switch i64 %s, label %dflt [
    i64 0, label %c0
    i64 1, label %c1
    i64 2, label %c2
    i64 3, label %c3
    i64 4, label %c4
    i64 5, label %c5
  ]
c0:
  call void @__bennett_gate(i32 17, ptr %h, i64 %qi)
  br label %join
c1:
  call void @__bennett_gate(i32 4, ptr %h, i64 %qi)
  br label %join
c2:
  call void @__bennett_gate(i32 9, ptr %h, i64 %qi)
  br label %join
c3:
  call void @__bennett_gate(i32 2, ptr %h, i64 %qi)
  br label %join
c4:
  call void @__bennett_gate(i32 40, ptr %h, i64 %qi)
  br label %join
c5:
  call void @__bennett_gate(i32 4, ptr %h, i64 1)
  call void @__bennett_gate(i32 8, ptr %h, i64 %qi)
  br label %join
dflt:
  call void @__bennett_gate(i32 1, ptr %h, i64 %qi)
  br label %join
join:
  %v = phi i64 [ 10, %c0 ], [ 11, %c1 ], [ 12, %c2 ], [ 13, %c3 ], [ 14, %c4 ], [ 15, %c5 ], [ 16, %dflt ]
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 0)
  call void @__bennett_qfree(ptr %h)
  %z = zext i1 %m to i64
  %r = add i64 %v, %z
  ret i64 %r
}
