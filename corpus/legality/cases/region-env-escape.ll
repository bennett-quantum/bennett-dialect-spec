; CASE: region-env-escape
; HAZARD: sroa, mem2reg, gvn, dse, memcpyopt, licm and instcombine around an env struct whose address escapes only into region markers: stores before the marker must stay, loads after it must be reloaded (the region writes the env through the runtime's call f(env)); the env is built by memcpy from a template, which memcpyopt/SROA like to forward
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

%env = type { ptr, i64, i64 }   ; handle, in, out

@template = private constant %env { ptr null, i64 5, i64 0 }

; reads in, writes out (classical result of the region), so the caller must reload out
define void @count_region(ptr %e) {
  %hp = getelementptr inbounds %env, ptr %e, i32 0, i32 0
  %h = load ptr, ptr %hp
  %ip = getelementptr inbounds %env, ptr %e, i32 0, i32 1
  %in = load i64, ptr %ip
  %i = and i64 %in, 1
  call void @__bennett_gate(i32 2, ptr %h, i64 %i)
  %op = getelementptr inbounds %env, ptr %e, i32 0, i32 2
  %o = load i64, ptr %op
  %o1 = add i64 %o, %in
  store i64 %o1, ptr %op
  ret void
}

declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg)

define i64 @case_entry(i64 %x) {
entry:
  %e = alloca %env
  %tmp = alloca %env
  call void @llvm.memcpy.p0.p0.i64(ptr %tmp, ptr @template, i64 24, i1 false)
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  %hp = getelementptr inbounds %env, ptr %tmp, i32 0, i32 0
  store ptr %h, ptr %hp
  %ip = getelementptr inbounds %env, ptr %tmp, i32 0, i32 1
  %in0 = load i64, ptr %ip
  %in = add i64 %in0, %x
  store i64 %in, ptr %ip
  call void @llvm.memcpy.p0.p0.i64(ptr %e, ptr %tmp, i64 24, i1 false)
  %op = getelementptr inbounds %env, ptr %e, i32 0, i32 2
  %n = and i64 %x, 3
  br label %loop
loop:
  %k = phi i64 [ 0, %entry ], [ %k.next, %loop ]
  call void @__bennett_adj(ptr @count_region, ptr %e)
  %o = load i64, ptr %op
  %ipe = getelementptr inbounds %env, ptr %e, i32 0, i32 1
  store i64 %o, ptr %ipe
  %k.next = add i64 %k, 1
  %d = icmp ugt i64 %k.next, %n
  br i1 %d, label %out, label %loop
out:
  %fin = load i64, ptr %op
  %stale = load i64, ptr %ip
  call void @__bennett_qfree(ptr %h)
  %r = add i64 %fin, %stale
  ret i64 %r
}
