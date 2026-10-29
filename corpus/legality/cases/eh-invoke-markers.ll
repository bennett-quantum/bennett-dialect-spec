; CASE: eh-invoke-markers
; HAZARD: markers called with invoke (C++ -fexceptions shape) with a cleanup landingpad that also calls markers, and a marker-bearing helper inlined into an invoke site (inliner turns its calls into invokes); simplifycfg/function-attrs/prune-eh-style logic may turn invokes into calls only for nounwind callees, so the markers must stay invokes and the landing pad must survive; personality is __gcc_personality_v0 (libgcc), never actually entered
; INPUTS: 0..31
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
declare i32 @__gcc_personality_v0(...)

define internal void @prep(ptr %h, i64 %i) {
  call void @__bennett_gate(i32 1, ptr %h, i64 %i)
  call void @__bennett_gate(i32 2, ptr %h, i64 %i)
  ret void
}

define i64 @case_entry(i64 %x) personality ptr @__gcc_personality_v0 {
entry:
  %h = invoke ptr @__bennett_qalloc(i64 0, i64 2)
          to label %ok0 unwind label %lp0
ok0:
  %i = and i64 %x, 1
  invoke void @prep(ptr %h, i64 %i)
          to label %ok1 unwind label %lp
ok1:
  invoke void @__bennett_gate(i32 3, ptr %h, i64 1)
          to label %ok2 unwind label %lp
ok2:
  %m = invoke zeroext i1 @__bennett_measure(ptr %h, i64 %i)
          to label %ok3 unwind label %lp
ok3:
  call void @__bennett_qfree(ptr %h)
  %z = zext i1 %m to i64
  ret i64 %z
lp:
  %lpv = landingpad { ptr, i32 }
          cleanup
  call void @__bennett_gate(i32 50, ptr %h, i64 0)
  call void @__bennett_qfree(ptr %h)
  resume { ptr, i32 } %lpv
lp0:
  %lpv0 = landingpad { ptr, i32 }
          cleanup
  resume { ptr, i32 } %lpv0
}
