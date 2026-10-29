; CASE: region-recursive-tre
; HAZARD: tailcallelim turning a directly self-recursive region body into a loop, while the same region also enters itself recursively through __bennett_ctrl (address escapes from inside its own body); function-attrs must not infer norecurse; inliner must not unroll the recursion into the region
; INPUTS: 0..15
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

%env = type { ptr, ptr, i64 }   ; data handle, control handle, depth

; walk(e): gate(depth); if depth>0 { depth--; if odd: ctrl(q, @walk, e) else walk(e) }   (tail-recursive)
define void @walk(ptr %e) {
entry:
  %hp = getelementptr inbounds %env, ptr %e, i32 0, i32 0
  %h = load ptr, ptr %hp
  %dp = getelementptr inbounds %env, ptr %e, i32 0, i32 2
  %d = load i64, ptr %dp
  %i = and i64 %d, 1
  call void @__bennett_gate(i32 3, ptr %h, i64 %i)
  %z = icmp eq i64 %d, 0
  br i1 %z, label %done, label %more
more:
  %d1 = sub i64 %d, 1
  store i64 %d1, ptr %dp
  %odd = icmp eq i64 %i, 1
  br i1 %odd, label %viactrl, label %direct
viactrl:
  %qp = getelementptr inbounds %env, ptr %e, i32 0, i32 1
  %q = load ptr, ptr %qp
  call void @__bennett_ctrl(ptr %q, i64 0, ptr @walk, i64 64, ptr %e)
  ret void
direct:
  tail call void @walk(ptr %e)
  ret void
done:
  ret void
}

define i64 @case_entry(i64 %x) {
entry:
  %e = alloca %env
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  %q = call ptr @__bennett_qalloc(i64 0, i64 1)
  %hp = getelementptr inbounds %env, ptr %e, i32 0, i32 0
  store ptr %h, ptr %hp
  %qp = getelementptr inbounds %env, ptr %e, i32 0, i32 1
  store ptr %q, ptr %qp
  %dp = getelementptr inbounds %env, ptr %e, i32 0, i32 2
  store i64 %x, ptr %dp
  call void @walk(ptr %e)
  %left = load i64, ptr %dp
  call void @__bennett_qfree(ptr %q)
  call void @__bennett_qfree(ptr %h)
  ret i64 %left
}
