; CASE: seed-straight
; HAZARD: straight-line marker order and bit-exact double
; INPUTS: 0..3
; EXPECT: legal
declare ptr @__bennett_qalloc(i64, i64)
declare ptr @__bennett_qborrow(i64, i64)
declare void @__bennett_gate(i32, ptr, i64)
declare void @__bennett_gate2(i32, ptr, i64, ptr, i64)
declare void @__bennett_rot(i32, ptr, i64, double)
declare void @__bennett_qload(ptr, ptr, ptr)
declare void @__bennett_qstore(ptr, ptr, ptr)
declare void @__bennett_qfree(ptr)
define i64 @case_entry(i64 %x) {
  %a = call ptr @__bennett_qalloc(i64 0, i64 4)
  %b = call ptr @__bennett_qborrow(i64 1, i64 4)
  call void @__bennett_gate(i32 1, ptr %a, i64 %x)
  call void @__bennett_gate2(i32 2, ptr %a, i64 0, ptr %b, i64 1)
  call void @__bennett_rot(i32 3, ptr %b, i64 2, double 0x8000000000000000)
  call void @__bennett_qload(ptr %a, ptr %b, ptr %a)
  call void @__bennett_qstore(ptr %b, ptr %a, ptr %b)
  call void @__bennett_qfree(ptr %b)
  call void @__bennett_qfree(ptr %a)
  %r = add i64 %x, 7
  ret i64 %r
}
