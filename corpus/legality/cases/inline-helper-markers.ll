; CASE: inline-helper-markers
; HAZARD: cgscc inliner (inline, default<O3>): internal and external helpers containing markers, one with a loop, inlined at several call sites with constant and variable arguments, then unrolled/simplified in the caller
; INPUTS: 0..63
; EXPECT: legal

target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef)
declare void @__bennett_qfree(ptr noundef)
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef)
declare void @__bennett_gate2(i32 noundef, ptr noundef, i64 noundef, ptr noundef, i64 noundef)
declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef)

; do-while over n >= 1 qubits
define internal void @hadamard_all(ptr %h, i64 %n) {
entry:
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %loop ]
  call void @__bennett_gate(i32 1, ptr %h, i64 %i)
  %i.next = add i64 %i, 1
  %done = icmp uge i64 %i.next, %n
  br i1 %done, label %exit, label %loop
exit:
  ret void
}

; external helper: inlined, but its body must stay too
define void @cx_ladder(ptr %h, i64 %k) {
entry:
  %k1 = add i64 %k, 1
  %t = and i64 %k1, 3
  call void @__bennett_gate2(i32 3, ptr %h, i64 %k, ptr %h, i64 %t)
  %odd = and i64 %k, 1
  %isodd = icmp ne i64 %odd, 0
  br i1 %isodd, label %extra, label %out
extra:
  call void @__bennett_gate(i32 2, ptr %h, i64 %k)
  br label %out
out:
  ret void
}

define internal i64 @measure_pair(ptr %h, i64 %a) {
  %m0 = call zeroext i1 @__bennett_measure(ptr %h, i64 %a)
  %m1 = call zeroext i1 @__bennett_measure(ptr %h, i64 0)
  %z0 = zext i1 %m0 to i64
  %z1 = zext i1 %m1 to i64
  %s = shl i64 %z1, 1
  %r = or i64 %s, %z0
  ret i64 %r
}

define i64 @case_entry(i64 %x) {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 4)
  call void @hadamard_all(ptr %h, i64 4)
  %b = and i64 %x, 3
  call void @cx_ladder(ptr %h, i64 %b)
  call void @cx_ladder(ptr %h, i64 1)
  %c = lshr i64 %x, 4
  %n = add i64 %c, 1
  call void @hadamard_all(ptr %h, i64 %n)
  %m = call i64 @measure_pair(ptr %h, i64 %b)
  call void @__bennett_qfree(ptr %h)
  %r = add i64 %m, %x
  ret i64 %r
}
