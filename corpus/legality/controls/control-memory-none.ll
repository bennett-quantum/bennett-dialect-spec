; CASE: control-memory-none
; HAZARD: memory(none) nounwind willreturn measurement CSE in a loop
; INPUTS: 0..7
; EXPECT: probe
declare ptr @__bennett_qalloc(i64, i64)
declare i1 @__bennett_measure(ptr, i64) memory(none) nounwind willreturn
declare void @__bennett_qfree(ptr)
define i64 @case_entry(i64 %x) {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  br label %loop
loop:
  %i = phi i64 [0, %entry], [%j, %loop]
  %acc = phi i64 [0, %entry], [%sum, %loop]
  %m = call i1 @__bennett_measure(ptr %h, i64 0)
  %v = zext i1 %m to i64
  %sum = add i64 %acc, %v
  %j = add i64 %i, 1
  %done = icmp eq i64 %j, 4
  br i1 %done, label %exit, label %loop
exit:
  call void @__bennett_qfree(ptr %h)
  ret i64 %sum
}
