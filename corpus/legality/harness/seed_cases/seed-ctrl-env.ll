; CASE: seed-ctrl-env
; HAZARD: region identity and environment structure
; INPUTS: 0..3
; EXPECT: legal
%Env = type { ptr, i64 }
declare ptr @__bennett_qalloc(i64, i64)
declare void @__bennett_gate(i32, ptr, i64)
declare void @__bennett_ctrl(ptr, i64, ptr, i64, ptr)
declare void @__bennett_qfree(ptr)
define void @seed_region(ptr %env) {
  %hp = getelementptr %Env, ptr %env, i32 0, i32 0
  %ip = getelementptr %Env, ptr %env, i32 0, i32 1
  %h = load ptr, ptr %hp
  %i = load i64, ptr %ip
  call void @__bennett_gate(i32 4, ptr %h, i64 %i)
  ret void
}
define i64 @case_entry(i64 %x) {
  %env = alloca %Env
  %h = call ptr @__bennett_qalloc(i64 0, i64 4)
  %hp = getelementptr %Env, ptr %env, i32 0, i32 0
  %ip = getelementptr %Env, ptr %env, i32 0, i32 1
  store ptr %h, ptr %hp
  store i64 %x, ptr %ip
  call void @__bennett_ctrl(ptr %h, i64 0, ptr @seed_region, i64 9, ptr %env)
  call void @__bennett_qfree(ptr %h)
  ret i64 %x
}
