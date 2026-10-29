; CASE: loop-idiom-handle-table
; HAZARD: loop-idiom turning a handle-table init loop (null fill) into memset and a handle-table copy loop into memcpy; then instcombine/sroa/memcpyopt/gvn on the memcpy'd handle table (instcombine lowers small memcpys to integer load/store, which can make a handle travel as i64 and come back through inttoptr); the table is indexed by classical values from the input; loop-vectorize may vectorise the copy with a runtime alias check (ptrtoint of table addresses, not of handles)
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
define i64 @case_entry(i64 %x) {
entry:
  %tab = alloca [8 x ptr]
  %cpy = alloca [8 x ptr]
  br label %zero
zero:
  %i = phi i64 [ 0, %entry ], [ %i.next, %zero ]
  %pz = getelementptr inbounds [8 x ptr], ptr %tab, i64 0, i64 %i
  store ptr null, ptr %pz
  %i.next = add nuw nsw i64 %i, 1
  %zd = icmp eq i64 %i.next, 8
  br i1 %zd, label %fillpre, label %zero
fillpre:
  %nf0 = and i64 %x, 7
  %nf = add i64 %nf0, 1
  br label %fill
fill:
  %j = phi i64 [ 0, %fillpre ], [ %j.next, %fill ]
  %hj = call ptr @__bennett_qalloc(i64 0, i64 1)
  %pj = getelementptr inbounds [8 x ptr], ptr %tab, i64 0, i64 %j
  store ptr %hj, ptr %pj
  %j.next = add nuw nsw i64 %j, 1
  %fd = icmp eq i64 %j.next, %nf
  br i1 %fd, label %copy, label %fill
copy:
  %k = phi i64 [ 0, %fill ], [ %k.next, %copy ]
  %sk = getelementptr inbounds [8 x ptr], ptr %tab, i64 0, i64 %k
  %hk = load ptr, ptr %sk
  %dk = getelementptr inbounds [8 x ptr], ptr %cpy, i64 0, i64 %k
  store ptr %hk, ptr %dk
  %k.next = add nuw nsw i64 %k, 1
  %cd = icmp eq i64 %k.next, 8
  br i1 %cd, label %use, label %copy
use:
  %sel = lshr i64 %x, 3
  %idx = urem i64 %sel, %nf
  %pu = getelementptr inbounds [8 x ptr], ptr %cpy, i64 0, i64 %idx
  %hu = load ptr, ptr %pu
  call void @__bennett_gate(i32 1, ptr %hu, i64 0)
  %p0 = getelementptr inbounds [8 x ptr], ptr %cpy, i64 0, i64 0
  %h0 = load ptr, ptr %p0
  %m = call zeroext i1 @__bennett_measure(ptr %h0, i64 0)
  br label %free
free:
  %f = phi i64 [ 0, %use ], [ %f.next, %free ]
  %pf = getelementptr inbounds [8 x ptr], ptr %cpy, i64 0, i64 %f
  %hf = load ptr, ptr %pf
  call void @__bennett_qfree(ptr %hf)
  %f.next = add nuw nsw i64 %f, 1
  %ffd = icmp eq i64 %f.next, %nf
  br i1 %ffd, label %done, label %free
done:
  %mz = zext i1 %m to i64
  %r = add i64 %mz, %idx
  ret i64 %r
}
