; CASE: region-internal-strip
; HAZARD: an internal region function referenced only through __bennett_reversible (the shape clang gives a static helper and rustc/clang give closures and lambdas): globaldce, deadargelim (unused env), globalopt and function-attrs must keep it; `strip` / `strip-nondebug` erase the names of local symbols, so the region's symbol name does not survive (region identity cannot be a local symbol name)
; INPUTS: 0..63
; EXPECT: probe

target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef)
declare void @__bennett_qfree(ptr noundef)
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef)
declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef)
declare void @__bennett_reversible(ptr noundef, i64 noundef, ptr noundef)

@hq = internal global ptr null

; env is unused: a candidate for deadargelim if the pass thought it saw every caller
define internal void @rev_body(ptr %env) {
  %h = load ptr, ptr @hq
  call void @__bennett_gate(i32 2, ptr %h, i64 0)
  call void @__bennett_gate(i32 2, ptr %h, i64 1)
  ret void
}

define i64 @case_entry(i64 %x) {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  store ptr %h, ptr @hq
  %b = add i64 %x, 4
  call void @__bennett_reversible(ptr @rev_body, i64 %b, ptr null)
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 1)
  call void @__bennett_qfree(ptr %h)
  %z = zext i1 %m to i64
  ret i64 %z
}
