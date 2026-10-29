; CASE: loop-fuse-distribute
; HAZARD: loop-fusion of two adjacent loops with equal trip counts (first applies gates to qubit i, second to qubit i of another register) and loop-distribute (llvm.loop.distribute.enable) of a loop mixing a classical array store with a marker call: fusing or distributing would reorder marker calls across iterations, which is only legal if the passes treat the markers as dependences; classical stores are present so the pure-store twin does fuse/distribute
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
define i64 @case_entry(i64 %x) {
entry:
  %arr = alloca [8 x i64]
  %brr = alloca [8 x i64]
  %crr = alloca [9 x i64]
  store i64 0, ptr %crr
  %a = call ptr @__bennett_qalloc(i64 0, i64 8)
  %b = call ptr @__bennett_qalloc(i64 0, i64 8)
  %n0 = and i64 %x, 7
  %n = add i64 %n0, 1
  br label %l1
l1:
  %i = phi i64 [ 0, %entry ], [ %i.next, %l1 ]
  %pa = getelementptr inbounds [8 x i64], ptr %arr, i64 0, i64 %i
  store i64 %i, ptr %pa
  call void @__bennett_gate(i32 1, ptr %a, i64 %i)
  %i.next = add nuw nsw i64 %i, 1
  %d1 = icmp eq i64 %i.next, %n
  br i1 %d1, label %mid, label %l1
mid:
  br label %l2
l2:
  %j = phi i64 [ 0, %mid ], [ %j.next, %l2 ]
  %pb = getelementptr inbounds [8 x i64], ptr %brr, i64 0, i64 %j
  %jj = mul i64 %j, 3
  store i64 %jj, ptr %pb
  call void @__bennett_gate(i32 2, ptr %b, i64 %j)
  %j.next = add nuw nsw i64 %j, 1
  %d2 = icmp eq i64 %j.next, %n
  br i1 %d2, label %pre3, label %l2
pre3:
  br label %l3
l3:
  ; distribute candidate: a loop-carried recurrence through crr, an independent update of brr, and a marker
  %k = phi i64 [ 0, %pre3 ], [ %k.next, %l3 ]
  %pk = getelementptr inbounds [9 x i64], ptr %crr, i64 0, i64 %k
  %v = load i64, ptr %pk
  %v1 = add i64 %v, %k
  %k1 = add nuw nsw i64 %k, 1
  %pk1 = getelementptr inbounds [9 x i64], ptr %crr, i64 0, i64 %k1
  store i64 %v1, ptr %pk1
  %pbk = getelementptr inbounds [8 x i64], ptr %brr, i64 0, i64 %k
  %w = load i64, ptr %pbk
  %w5 = mul i64 %w, 5
  store i64 %w5, ptr %pbk
  call void @__bennett_gate2(i32 3, ptr %a, i64 %k, ptr %b, i64 %k)
  %k.next = add nuw nsw i64 %k, 1
  %d3 = icmp eq i64 %k.next, %n
  br i1 %d3, label %out, label %l3, !llvm.loop !0
out:
  %pl = getelementptr inbounds [9 x i64], ptr %crr, i64 0, i64 %n
  %r0 = load i64, ptr %pl
  %last = sub i64 %n, 1
  %pbl = getelementptr inbounds [8 x i64], ptr %brr, i64 0, i64 %last
  %r1 = load i64, ptr %pbl
  %r = add i64 %r0, %r1
  call void @__bennett_qfree(ptr %b)
  call void @__bennett_qfree(ptr %a)
  ret i64 %r
}

!0 = distinct !{!0, !1}
!1 = !{!"llvm.loop.distribute.enable", i1 true}
