; CASE: region-ctrl-variadic
; HAZARD: the variadic probe __bennett_ctrl_v with integer, pointer and double variadic operands, called in a loop and from an inlined helper; checks that no pass (instcombine call canonicalisation, deadargelim, expand-variadics on 20/23, inlining) rewrites the variadic call or its function type
; INPUTS: 0..31
; EXPECT: legal

target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef)
declare void @__bennett_qfree(ptr noundef)
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef)
declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef)
declare void @__bennett_ctrl_v(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ...)

define void @vbody(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 2, ptr %h, i64 0)
  ret void
}

define internal void @helper(ptr %q, i64 %i, ptr %e, double %th) {
  call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr %q, i64 0, ptr @vbody, i64 4, ptr %e, i64 %i, double %th)
  ret void
}

define i64 @case_entry(i64 %x) {
entry:
  %e = alloca ptr
  %q = call ptr @__bennett_qalloc(i64 0, i64 1)
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %e
  %n = and i64 %x, 3
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %loop ]
  %f = uitofp i64 %i to double
  %th = fmul double %f, 2.500000e-01
  call void @helper(ptr %q, i64 %i, ptr %e, double %th)
  %i.next = add i64 %i, 1
  %d = icmp ugt i64 %i.next, %n
  br i1 %d, label %out, label %loop
out:
  call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr %q, i64 0, ptr @vbody, i64 4, ptr %e)
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 0)
  call void @__bennett_qfree(ptr %h)
  call void @__bennett_qfree(ptr %q)
  %z = zext i1 %m to i64
  ret i64 %z
}
