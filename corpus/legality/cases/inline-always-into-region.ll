; CASE: inline-always-into-region
; HAZARD: always-inline of a marker-bearing helper into a region body (internal region referenced only through __bennett_ctrl) and into case_entry; the helper is alwaysinline+internal so it is deleted after inlining
; INPUTS: 0..31
; EXPECT: legal

target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef)
declare void @__bennett_qfree(ptr noundef)
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef)
declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef)
declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ptr noundef)

%env = type { ptr, i64 }

define internal void @phase_kick(ptr %h, i64 %i) alwaysinline {
  call void @__bennett_gate(i32 5, ptr %h, i64 %i)
  call void @__bennett_gate(i32 6, ptr %h, i64 %i)
  ret void
}

define internal void @region_kick(ptr %e) {
  %hp = getelementptr inbounds %env, ptr %e, i32 0, i32 0
  %h = load ptr, ptr %hp
  %ip = getelementptr inbounds %env, ptr %e, i32 0, i32 1
  %i = load i64, ptr %ip
  call void @phase_kick(ptr %h, i64 %i)
  %j = xor i64 %i, 1
  call void @phase_kick(ptr %h, i64 %j)
  ret void
}

define i64 @case_entry(i64 %x) {
entry:
  %e = alloca %env
  %ctl = call ptr @__bennett_qalloc(i64 0, i64 1)
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  %hp = getelementptr inbounds %env, ptr %e, i32 0, i32 0
  store ptr %h, ptr %hp
  %i = and i64 %x, 1
  %ip = getelementptr inbounds %env, ptr %e, i32 0, i32 1
  store i64 %i, ptr %ip
  call void @phase_kick(ptr %ctl, i64 0)
  %budget = add i64 %x, 8
  call void @__bennett_ctrl(ptr %ctl, i64 0, ptr @region_kick, i64 %budget, ptr %e)
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 %i)
  call void @__bennett_qfree(ptr %h)
  call void @__bennett_qfree(ptr %ctl)
  %z = zext i1 %m to i64
  ret i64 %z
}
