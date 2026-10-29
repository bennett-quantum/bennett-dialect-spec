; CASE: ipo-ipsccp-funcspec-region
; HAZARD: ipsccp with function specialization: an internal helper takes a region function pointer and a constant op and forwards them to __bennett_ctrl; called with two different constant regions, so funcspec clones it per region and IPSCCP propagates constant args; region pointers become literal constants inside the clones
; INPUTS: 0..63
; EXPECT: legal

target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef)
declare void @__bennett_qfree(ptr noundef)
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef)
declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef)
declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ptr noundef)

define void @rx(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 11, ptr %h, i64 0)
  ret void
}

define void @rz(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 12, ptr %h, i64 1)
  call void @__bennett_gate(i32 13, ptr %h, i64 0)
  ret void
}

; f is called indirectly on the hot path too, which is what funcspec scores
define internal void @controlled(ptr %q, i64 %qi, ptr %f, i64 %rounds, ptr %e) noinline {
entry:
  br label %loop
loop:
  %k = phi i64 [ 0, %entry ], [ %k.next, %loop ]
  call void @__bennett_ctrl(ptr %q, i64 %qi, ptr %f, i64 16, ptr %e)
  %k.next = add i64 %k, 1
  %d = icmp uge i64 %k.next, %rounds
  br i1 %d, label %out, label %loop
out:
  call void %f(ptr %e)
  ret void
}

define i64 @case_entry(i64 %x) {
entry:
  %e = alloca ptr
  %q = call ptr @__bennett_qalloc(i64 0, i64 1)
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  store ptr %h, ptr %e
  %n = and i64 %x, 3
  %n1 = add i64 %n, 1
  call void @controlled(ptr %q, i64 0, ptr @rx, i64 %n1, ptr %e)
  %n2 = lshr i64 %x, 4
  %n3 = add i64 %n2, 1
  call void @controlled(ptr %q, i64 0, ptr @rz, i64 %n3, ptr %e)
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 0)
  call void @__bennett_qfree(ptr %h)
  call void @__bennett_qfree(ptr %q)
  %z = zext i1 %m to i64
  ret i64 %z
}
