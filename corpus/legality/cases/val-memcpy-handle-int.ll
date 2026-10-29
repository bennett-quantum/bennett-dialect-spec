; CASE: val-memcpy-handle-int
; HAZARD: instcombine (memcpy of <= 8 bytes becomes an integer load/store) followed by store-to-load forwarding (instcombine, gvn, early-cse): a handle copied by an 8-byte memcpy from a handle-table slot into a region env becomes `ptrtoint ptr %h to i64` + `store i64`, then flows into the region through memory; the source contains no int/ptr conversion of a handle. Minimal .ll form of c-memcpy-handle-int
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
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg)

@gslot = global [4 x ptr] zeroinitializer

define void @rg(ptr %e) {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  ret void
}

define i64 @case_entry(i64 %x) {
entry:
  %e = alloca { ptr, i64 }
  %h = call ptr @__bennett_qalloc(i64 0, i64 1)
  %s = and i64 %x, 3
  %slot = getelementptr inbounds [4 x ptr], ptr @gslot, i64 0, i64 %s
  store ptr %h, ptr %slot
  call void @llvm.memcpy.p0.p0.i64(ptr %e, ptr %slot, i64 8, i1 false)
  %ip = getelementptr inbounds { ptr, i64 }, ptr %e, i32 0, i32 1
  store i64 %x, ptr %ip
  call void @__bennett_ctrl(ptr %h, i64 0, ptr @rg, i64 4, ptr %e)
  %h2 = load ptr, ptr %e
  call void @__bennett_gate(i32 2, ptr %h2, i64 0)
  call void @__bennett_qfree(ptr %h2)
  ret i64 %x
}
