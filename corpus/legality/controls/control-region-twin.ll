; CASE: control-region-twin
; HAZARD: mergefunc region identity probe with identical externally visible twins
; INPUTS: 0..3
; EXPECT: probe
declare ptr @__bennett_qalloc(i64, i64)
declare void @__bennett_gate(i32, ptr, i64)
declare void @__bennett_ctrl(ptr, i64, ptr, i64, ptr)
declare void @__bennett_qfree(ptr)
define void @twin_a(ptr %env) {
  %h = load ptr, ptr %env
  call void @__bennett_gate(i32 9, ptr %h, i64 0)
  ret void
}
define void @twin_b(ptr %env) {
  %h = load ptr, ptr %env
  call void @__bennett_gate(i32 9, ptr %h, i64 0)
  ret void
}
define i64 @case_entry(i64 %x) {
  %env = alloca ptr
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  store ptr %h, ptr %env
  call void @__bennett_ctrl(ptr %h, i64 0, ptr @twin_b, i64 2, ptr %env)
  call void @__bennett_qfree(ptr %h)
  ret i64 %x
}
