; CASE: region-iroutliner
; HAZARD: iroutliner extracting a similar marker sequence shared by two region functions and case_entry into one outlined_ir_func; region bodies become (partly) calls to the outlined function, so the marker sequence of a region now lives in a different function than the region symbol
; INPUTS: 0..63
; EXPECT: probe

target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef)
declare void @__bennett_qfree(ptr noundef)
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef)
declare void @__bennett_gate2(i32 noundef, ptr noundef, i64 noundef, ptr noundef, i64 noundef)
declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef)
declare void @__bennett_adj(ptr noundef, ptr noundef)
declare void @__bennett_reversible(ptr noundef, i64 noundef, ptr noundef)

%env = type { ptr, i64 }

define void @qft_step_a(ptr %e) {
  %hp = getelementptr inbounds %env, ptr %e, i32 0, i32 0
  %h = load ptr, ptr %hp
  %kp = getelementptr inbounds %env, ptr %e, i32 0, i32 1
  %k = load i64, ptr %kp
  %k1 = add i64 %k, 1
  %k2 = and i64 %k1, 3
  call void @__bennett_gate(i32 1, ptr %h, i64 %k)
  call void @__bennett_gate2(i32 14, ptr %h, i64 %k, ptr %h, i64 %k2)
  call void @__bennett_gate2(i32 15, ptr %h, i64 %k2, ptr %h, i64 %k)
  call void @__bennett_gate(i32 1, ptr %h, i64 %k2)
  ret void
}

define void @qft_step_b(ptr %e) {
  %hp = getelementptr inbounds %env, ptr %e, i32 0, i32 0
  %h = load ptr, ptr %hp
  %kp = getelementptr inbounds %env, ptr %e, i32 0, i32 1
  %k = load i64, ptr %kp
  %k1 = add i64 %k, 2
  %k2 = and i64 %k1, 3
  call void @__bennett_gate(i32 1, ptr %h, i64 %k)
  call void @__bennett_gate2(i32 14, ptr %h, i64 %k, ptr %h, i64 %k2)
  call void @__bennett_gate2(i32 15, ptr %h, i64 %k2, ptr %h, i64 %k)
  call void @__bennett_gate(i32 1, ptr %h, i64 %k2)
  ret void
}

define i64 @case_entry(i64 %x) {
entry:
  %e = alloca %env
  %h = call ptr @__bennett_qalloc(i64 0, i64 4)
  %hp = getelementptr inbounds %env, ptr %e, i32 0, i32 0
  store ptr %h, ptr %hp
  %k = and i64 %x, 3
  %kp = getelementptr inbounds %env, ptr %e, i32 0, i32 1
  store i64 %k, ptr %kp
  call void @__bennett_adj(ptr @qft_step_a, ptr %e)
  %k3 = lshr i64 %x, 4
  store i64 %k3, ptr %kp
  call void @__bennett_reversible(ptr @qft_step_b, i64 64, ptr %e)
  %k1 = add i64 %k, 3
  %k2 = and i64 %k1, 3
  call void @__bennett_gate(i32 1, ptr %h, i64 %k)
  call void @__bennett_gate2(i32 14, ptr %h, i64 %k, ptr %h, i64 %k2)
  call void @__bennett_gate2(i32 15, ptr %h, i64 %k2, ptr %h, i64 %k)
  call void @__bennett_gate(i32 1, ptr %h, i64 %k2)
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 %k)
  call void @__bennett_qfree(ptr %h)
  %z = zext i1 %m to i64
  ret i64 %z
}
