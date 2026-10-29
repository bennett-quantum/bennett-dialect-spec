; CASE: region-switch-fnptr-table
; HAZARD: simplifycfg sink-common-insts + switch-to-lookup: a switch whose arms differ only in the region passed to __bennett_ctrl is folded into one ctrl call whose region operand is loaded from a private constant table of function pointers (@switch.table.case_entry); the region operand is no longer a literal function at the call site
; INPUTS: 0..63
; EXPECT: probe

target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef)
declare void @__bennett_qfree(ptr noundef)
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef)
declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef)
declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ptr noundef)

define void @oracle0(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 30, ptr %h, i64 0)
  ret void
}
define void @oracle1(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 31, ptr %h, i64 1)
  ret void
}
define void @oracle2(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 32, ptr %h, i64 0)
  call void @__bennett_gate(i32 32, ptr %h, i64 1)
  ret void
}
define void @oracle3(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 33, ptr %h, i64 1)
  call void @__bennett_gate(i32 33, ptr %h, i64 0)
  ret void
}

define i64 @case_entry(i64 %x) {
entry:
  %e = alloca ptr
  %q = call ptr @__bennett_qalloc(i64 0, i64 1)
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  store ptr %h, ptr %e
  call void @__bennett_gate(i32 1, ptr %q, i64 0)
  %s = and i64 %x, 7
  switch i64 %s, label %other [
    i64 0, label %c0
    i64 1, label %c1
    i64 2, label %c2
    i64 3, label %c3
    i64 4, label %c4
    i64 5, label %c5
  ]
c0:
  call void @__bennett_ctrl(ptr %q, i64 0, ptr @oracle0, i64 8, ptr %e)
  br label %join
c1:
  call void @__bennett_ctrl(ptr %q, i64 0, ptr @oracle1, i64 8, ptr %e)
  br label %join
c2:
  call void @__bennett_ctrl(ptr %q, i64 0, ptr @oracle2, i64 8, ptr %e)
  br label %join
c3:
  call void @__bennett_ctrl(ptr %q, i64 0, ptr @oracle3, i64 8, ptr %e)
  br label %join
c4:
  call void @__bennett_ctrl(ptr %q, i64 0, ptr @oracle2, i64 8, ptr %e)
  br label %join
c5:
  call void @__bennett_ctrl(ptr %q, i64 0, ptr @oracle1, i64 8, ptr %e)
  br label %join
other:
  call void @__bennett_ctrl(ptr %q, i64 0, ptr @oracle3, i64 8, ptr %e)
  br label %join
join:
  %m = call zeroext i1 @__bennett_measure(ptr %q, i64 0)
  call void @__bennett_qfree(ptr %h)
  call void @__bennett_qfree(ptr %q)
  %z = zext i1 %m to i64
  ret i64 %z
}
