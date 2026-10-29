; CASE: cfg-unreachable-after-marker
; HAZARD: simplifycfg / instcombine / sccp exploiting UB and unreachable: (1) a marker call followed by unreachable on a path the inputs never take, which LLVM may delete only if the marker is willreturn (it is not, so the call and the branch must stay); (2) the __builtin_assume/__builtin_unreachable idiom after markers on the executed path, which lets LLVM fold the classical check but must not move or drop the markers before it; (3) a noreturn helper reached only on a never-taken path
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
@sink = global i64 0

define void @fatal(i64 %code) noreturn noinline {
  store volatile i64 %code, ptr @sink
  br label %spin
spin:
  br label %spin
}

define i64 @case_entry(i64 %x) {
entry:
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  %inrange = icmp ult i64 %x, 64
  br i1 %inrange, label %ok, label %bad
bad:
  ; executing a marker and then UB: deletable only if the marker were known to return
  call void @__bennett_gate(i32 99, ptr %h, i64 0)
  unreachable
ok:
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  %b = and i64 %x, 1
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 %b)
  ; __builtin_unreachable() idiom: x < 64 here, so x >> 6 == 0
  %hi = lshr i64 %x, 6
  %z = icmp eq i64 %hi, 0
  br i1 %z, label %cont, label %never
never:
  unreachable
cont:
  call void @__bennett_gate(i32 2, ptr %h, i64 1)
  %big = icmp ugt i64 %x, 1000
  br i1 %big, label %die, label %fine
die:
  call void @__bennett_gate(i32 98, ptr %h, i64 1)
  call void @fatal(i64 %x)
  unreachable
fine:
  call void @__bennett_qfree(ptr %h)
  %mz = zext i1 %m to i64
  %r = add i64 %mz, %hi
  ret i64 %r
}
