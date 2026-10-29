; CASE: inline-partial
; HAZARD: partial-inliner: a helper with an early-return guard followed by a large marker-bearing body; the guard is inlined into callers and the cold remainder is outlined (helper.N.ir-outlined style function), so markers move into a new function
; INPUTS: 0..63
; EXPECT: legal

target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef)
declare void @__bennett_qfree(ptr noundef)
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef)
declare void @__bennett_gate2(i32 noundef, ptr noundef, i64 noundef, ptr noundef, i64 noundef)
declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef)

define internal i64 @maybe_entangle(ptr %h, i64 %k) {
entry:
  %skip = icmp ult i64 %k, 3
  br i1 %skip, label %ret0, label %body
ret0:
  ret i64 0
body:
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  call void @__bennett_gate2(i32 3, ptr %h, i64 0, ptr %h, i64 1)
  call void @__bennett_gate2(i32 3, ptr %h, i64 1, ptr %h, i64 2)
  call void @__bennett_gate2(i32 3, ptr %h, i64 2, ptr %h, i64 3)
  %a = and i64 %k, 3
  call void @__bennett_gate(i32 7, ptr %h, i64 %a)
  call void @__bennett_gate(i32 8, ptr %h, i64 %a)
  call void @__bennett_gate(i32 9, ptr %h, i64 %a)
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 %a)
  %z = zext i1 %m to i64
  %r = add i64 %z, %k
  ret i64 %r
}

define i64 @case_entry(i64 %x) {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 4)
  %k = and i64 %x, 7
  %r1 = call i64 @maybe_entangle(ptr %h, i64 %k)
  %k2 = lshr i64 %x, 3
  %r2 = call i64 @maybe_entangle(ptr %h, i64 %k2)
  call void @__bennett_qfree(ptr %h)
  %s = shl i64 %r2, 8
  %r = or i64 %s, %r1
  ret i64 %r
}
