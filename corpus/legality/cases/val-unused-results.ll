; CASE: val-unused-results
; HAZARD: dce, adce, bdce, instcombine, dse, globaldce and function-attrs on marker calls whose results are unused: a qalloc whose handle is never used (still allocates; later handle ordinals shift if it is dropped), a measure whose bit is discarded, a qborrow never freed, an internal helper whose only effect is a discarded measure; all must still be called
; INPUTS: 0..63
; EXPECT: legal
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef)
declare ptr @__bennett_qborrow(i64 noundef, i64 noundef)
declare void @__bennett_qfree(ptr noundef)
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef)
declare void @__bennett_gate2(i32 noundef, ptr noundef, i64 noundef, ptr noundef, i64 noundef)
declare void @__bennett_rot(i32 noundef, ptr noundef, i64 noundef, double noundef)
declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef)
declare void @__bennett_qload(ptr noundef, ptr noundef, ptr noundef)
declare void @__bennett_qstore(ptr noundef, ptr noundef, ptr noundef)
declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ptr noundef)
declare void @__bennett_adj(ptr noundef, ptr noundef)
declare void @__bennett_compute(ptr noundef, ptr noundef, ptr noundef)
declare void @__bennett_reversible(ptr noundef, i64 noundef, ptr noundef)
declare void @__bennett_inplace(ptr noundef, ptr noundef, ptr noundef)
define internal i1 @peek(ptr %h) noinline {
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 0)
  ret i1 %m
}

define i64 @case_entry(i64 %x) {
entry:
  %unused = call ptr @__bennett_qalloc(i64 0, i64 3)
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %drop = call zeroext i1 @__bennett_measure(ptr %h, i64 0)
  %b = call ptr @__bennett_qborrow(i64 2, i64 1)
  %ign = call i1 @peek(ptr %h)
  %c = and i64 %x, 1
  %t = icmp ne i64 %c, 0
  br i1 %t, label %y, label %n
y:
  %u2 = call ptr @__bennett_qalloc(i64 1, i64 2)
  br label %n
n:
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  call void @__bennett_qfree(ptr %h)
  ret i64 %x
}
