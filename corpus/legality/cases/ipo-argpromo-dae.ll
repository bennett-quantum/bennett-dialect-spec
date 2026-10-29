; CASE: ipo-argpromo-dae
; HAZARD: argpromotion (handle and index passed by pointer to an internal helper become by-value), deadargelim (unused argument and unused return value of an internal marker-bearing helper removed), function-attrs on the helper
; INPUTS: 0..63
; EXPECT: legal

target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef)
declare void @__bennett_qfree(ptr noundef)
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef)
declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef)

; handle and index passed by reference; %unused never read; return value ignored by every caller
define internal i64 @apply(ptr %hp, ptr %ip, i64 %unused) noinline {
  %h = load ptr, ptr %hp
  %i = load i64, ptr %ip
  call void @__bennett_gate(i32 4, ptr %h, i64 %i)
  %i2 = xor i64 %i, 1
  call void @__bennett_gate(i32 5, ptr %h, i64 %i2)
  ret i64 %i2
}

define i64 @case_entry(i64 %x) {
entry:
  %hslot = alloca ptr
  %islot = alloca i64
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  store ptr %h, ptr %hslot
  %i = and i64 %x, 1
  store i64 %i, ptr %islot
  %ign1 = call i64 @apply(ptr %hslot, ptr %islot, i64 %x)
  %j = lshr i64 %x, 1
  %j1 = and i64 %j, 1
  store i64 %j1, ptr %islot
  %ign2 = call i64 @apply(ptr %hslot, ptr %islot, i64 7)
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 %j1)
  call void @__bennett_qfree(ptr %h)
  %z = zext i1 %m to i64
  ret i64 %z
}
