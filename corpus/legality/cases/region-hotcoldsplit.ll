; CASE: region-hotcoldsplit
; HAZARD: hotcoldsplit outlining a cold path (marked by a call to a cold function) that contains gate/measure markers and a __bennett_ctrl region-marker call, into case_entry.cold.1; markers and the region operand move into a new function
; INPUTS: 0..63
; EXPECT: legal

target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef)
declare void @__bennett_qfree(ptr noundef)
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef)
declare void @__bennett_gate2(i32 noundef, ptr noundef, i64 noundef, ptr noundef, i64 noundef)
declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef)
declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ptr noundef)

@cold_count = global i64 0

; a defined cold function (so the case links), stands in for an error-reporting path
define void @note_rare_path(i64 %v) cold noinline {
  %c = load i64, ptr @cold_count
  %c1 = add i64 %c, %v
  store i64 %c1, ptr @cold_count
  ret void
}

define void @fixup_region(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 2, ptr %h, i64 1)
  call void @__bennett_gate(i32 6, ptr %h, i64 1)
  ret void
}

define i64 @case_entry(i64 %x) {
entry:
  %e = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  store ptr %h, ptr %e
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 0)
  %r = and i64 %x, 7
  %rare = icmp eq i64 %r, 5
  br i1 %rare, label %cold, label %hot
cold:
  call void @note_rare_path(i64 %x)
  call void @__bennett_gate(i32 9, ptr %h, i64 0)
  call void @__bennett_gate2(i32 3, ptr %h, i64 0, ptr %h, i64 1)
  %m2 = call zeroext i1 @__bennett_measure(ptr %h, i64 1)
  %t = select i1 %m2, i64 40, i64 30
  %q = call ptr @__bennett_qalloc(i64 0, i64 1)
  call void @__bennett_ctrl(ptr %q, i64 0, ptr @fixup_region, i64 %t, ptr %e)
  call void @__bennett_qfree(ptr %q)
  call void @note_rare_path(i64 %t)
  br label %join
hot:
  call void @__bennett_gate(i32 4, ptr %h, i64 1)
  br label %join
join:
  %v = phi i64 [ 1, %cold ], [ 2, %hot ]
  call void @__bennett_qfree(ptr %h)
  %z = zext i1 %m to i64
  %res = add i64 %z, %v
  ret i64 %res
}
