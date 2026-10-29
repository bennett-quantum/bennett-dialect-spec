; CASE: seed-loop
; HAZARD: loop unrolling and measurement-dependent branch
; INPUTS: 0..7
; EXPECT: legal
declare ptr @__bennett_qalloc(i64, i64)
declare void @__bennett_gate(i32, ptr, i64)
declare i1 @__bennett_measure(ptr, i64)
declare void @__bennett_qfree(ptr)
define i64 @case_entry(i64 %x) {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 8)
  br label %loop
loop:
  %i = phi i64 [0, %entry], [%next, %join]
  call void @__bennett_gate(i32 1, ptr %h, i64 %i)
  %m = call i1 @__bennett_measure(ptr %h, i64 %i)
  br i1 %m, label %yes, label %no
yes:
  call void @__bennett_gate(i32 2, ptr %h, i64 %i)
  br label %join
no:
  call void @__bennett_gate(i32 3, ptr %h, i64 %i)
  br label %join
join:
  %next = add i64 %i, 1
  %done = icmp eq i64 %next, 4
  br i1 %done, label %exit, label %loop
exit:
  call void @__bennett_qfree(ptr %h)
  ret i64 %x
}
