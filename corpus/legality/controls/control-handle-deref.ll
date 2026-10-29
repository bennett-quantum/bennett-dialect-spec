; CASE: control-handle-deref
; HAZARD: deliberate host load through opaque handle; guard must fault
; INPUTS: 0
; EXPECT: probe
declare ptr @__bennett_qalloc(i64, i64)
define i64 @case_entry(i64 %x) {
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %v = load volatile i64, ptr %h
  ret i64 %v
}
