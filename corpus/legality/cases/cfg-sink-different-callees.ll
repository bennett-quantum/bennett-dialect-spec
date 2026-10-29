; CASE: cfg-sink-different-callees
; HAZARD: gvn-sink and simplifycfg sink-common-insts on diamonds whose arms call *different* markers with the same function type (qalloc vs qborrow: ptr(i64,i64); qload vs qstore: void(ptr,ptr,ptr)). simplifycfg refuses to create indirect calls; GVNSink's operand check does not exclude the callee operand, so it may sink the two calls into one indirect call through a phi of @__bennett_qalloc/@__bennett_qborrow. The trace would not change, but the call is no longer a direct call to a marker by name
; INPUTS: 0..63
; EXPECT: probe
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
define i64 @case_entry(i64 %x) {
entry:
  %mem = call ptr @__bennett_qalloc(i64 1, i64 4)
  %addr = call ptr @__bennett_qalloc(i64 0, i64 2)
  %c = and i64 %x, 1
  %clean = icmp eq i64 %c, 0
  %n = lshr i64 %x, 4
  %n1 = add i64 %n, 1
  br i1 %clean, label %a, label %b
a:
  %ha = call ptr @__bennett_qalloc(i64 0, i64 %n1)
  br label %j1
b:
  %hb = call ptr @__bennett_qborrow(i64 0, i64 %n1)
  br label %j1
j1:
  %h = phi ptr [ %ha, %a ], [ %hb, %b ]
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  %d = and i64 %x, 2
  %ld = icmp eq i64 %d, 0
  br i1 %ld, label %l, label %s
l:
  call void @__bennett_qload(ptr %h, ptr %mem, ptr %addr)
  br label %j2
s:
  call void @__bennett_qstore(ptr %mem, ptr %addr, ptr %h)
  br label %j2
j2:
  call void @__bennett_qfree(ptr %h)
  call void @__bennett_qfree(ptr %addr)
  call void @__bennett_qfree(ptr %mem)
  ret i64 %x
}
