; ModuleID = 'bennett_emit.c'
source_filename = "bennett_emit.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct.env = type { ptr, i64, double }

; Function Attrs: nounwind uwtable
define dso_local noundef i64 @case_entry(i64 noundef %0) local_unnamed_addr #0 {
  %2 = alloca %struct.env, align 8
  %3 = alloca [4 x ptr], align 16
  %4 = tail call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 4) #3
  tail call void @__bennett_gate(i32 noundef 1, ptr noundef %4, i64 noundef 0) #3
  %5 = uitofp i64 %0 to double
  %6 = fmul double %5, 1.250000e-01
  tail call void @__bennett_rot(i32 noundef 3, ptr noundef %4, i64 noundef 1, double noundef %6) #3
  tail call void @__bennett_gate2(i32 noundef 4, ptr noundef %4, i64 noundef 0, ptr noundef %4, i64 noundef 1) #3
  %7 = tail call zeroext i1 @__bennett_measure(ptr noundef %4, i64 noundef 0) #3
  br i1 %7, label %8, label %9

8:                                                ; preds = %1
  tail call void @__bennett_gate(i32 noundef 2, ptr noundef %4, i64 noundef 2) #3
  br label %9

9:                                                ; preds = %8, %1
  %10 = phi i64 [ 1, %8 ], [ 0, %1 ]
  call void @llvm.lifetime.start.p0(i64 24, ptr nonnull %2) #3
  store ptr %4, ptr %2, align 8, !tbaa !5
  %11 = getelementptr inbounds %struct.env, ptr %2, i64 0, i32 1
  store i64 3, ptr %11, align 8, !tbaa !12
  %12 = getelementptr inbounds %struct.env, ptr %2, i64 0, i32 2
  store double %6, ptr %12, align 8, !tbaa !13
  call void @__bennett_ctrl(ptr noundef %4, i64 noundef 0, ptr noundef nonnull @body, i64 noundef 8, ptr noundef nonnull %2) #3
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %3) #3
  %13 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1) #3
  store ptr %13, ptr %3, align 16, !tbaa !14
  %14 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1) #3
  %15 = getelementptr inbounds [4 x ptr], ptr %3, i64 0, i64 1
  store ptr %14, ptr %15, align 8, !tbaa !14
  %16 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1) #3
  %17 = getelementptr inbounds [4 x ptr], ptr %3, i64 0, i64 2
  store ptr %16, ptr %17, align 16, !tbaa !14
  %18 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1) #3
  %19 = getelementptr inbounds [4 x ptr], ptr %3, i64 0, i64 3
  store ptr %18, ptr %19, align 8, !tbaa !14
  %20 = and i64 %0, 3
  %21 = getelementptr inbounds [4 x ptr], ptr %3, i64 0, i64 %20
  %22 = load ptr, ptr %21, align 8, !tbaa !14
  call void @__bennett_gate(i32 noundef 1, ptr noundef %22, i64 noundef 0) #3
  call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr noundef %4, i64 noundef 0, ptr noundef nonnull @body, i64 noundef 8, i32 noundef 1, double noundef 2.500000e+00, ptr noundef %4) #3
  call void @__bennett_adj(ptr noundef nonnull @body, ptr noundef nonnull %2) #3
  call void @__bennett_compute(ptr noundef nonnull @body, ptr noundef nonnull @body, ptr noundef nonnull %2) #3
  call void @__bennett_reversible(ptr noundef nonnull @body, i64 noundef 3, ptr noundef nonnull %2) #3
  call void @__bennett_inplace(ptr noundef nonnull @body, ptr noundef nonnull @body, ptr noundef nonnull %2) #3
  %23 = call ptr @__bennett_qborrow(i64 noundef 0, i64 noundef 1) #3
  call void @__bennett_qload(ptr noundef %23, ptr noundef %4, ptr noundef %13) #3
  call void @__bennett_qstore(ptr noundef %4, ptr noundef %14, ptr noundef %23) #3
  call void @__bennett_qfree(ptr noundef %23) #3
  call void @__bennett_qfree(ptr noundef %13) #3
  call void @__bennett_qfree(ptr noundef %14) #3
  call void @__bennett_qfree(ptr noundef %16) #3
  call void @__bennett_qfree(ptr noundef %18) #3
  call void @__bennett_qfree(ptr noundef %4) #3
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %3) #3
  call void @llvm.lifetime.end.p0(i64 24, ptr nonnull %2) #3
  ret i64 %10
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #1

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef) local_unnamed_addr #2

declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef) local_unnamed_addr #2

declare void @__bennett_rot(i32 noundef, ptr noundef, i64 noundef, double noundef) local_unnamed_addr #2

declare void @__bennett_gate2(i32 noundef, ptr noundef, i64 noundef, ptr noundef, i64 noundef) local_unnamed_addr #2

declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef) local_unnamed_addr #2

declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ptr noundef) local_unnamed_addr #2

; Function Attrs: nounwind uwtable
define internal void @body(ptr nocapture noundef readonly %0) #0 {
  %2 = load ptr, ptr %0, align 8, !tbaa !5
  %3 = getelementptr inbounds %struct.env, ptr %0, i64 0, i32 1
  %4 = load i64, ptr %3, align 8, !tbaa !12
  %5 = getelementptr inbounds %struct.env, ptr %0, i64 0, i32 2
  %6 = load double, ptr %5, align 8, !tbaa !13
  tail call void @__bennett_rot(i32 noundef 1, ptr noundef %2, i64 noundef %4, double noundef %6) #3
  %7 = load ptr, ptr %0, align 8, !tbaa !5
  %8 = load i64, ptr %3, align 8, !tbaa !12
  tail call void @__bennett_gate(i32 noundef 2, ptr noundef %7, i64 noundef %8) #3
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #1

declare void @__bennett_ctrl_v(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ...) local_unnamed_addr #2

declare void @__bennett_adj(ptr noundef, ptr noundef) local_unnamed_addr #2

declare void @__bennett_compute(ptr noundef, ptr noundef, ptr noundef) local_unnamed_addr #2

declare void @__bennett_reversible(ptr noundef, i64 noundef, ptr noundef) local_unnamed_addr #2

declare void @__bennett_inplace(ptr noundef, ptr noundef, ptr noundef) local_unnamed_addr #2

declare ptr @__bennett_qborrow(i64 noundef, i64 noundef) local_unnamed_addr #2

declare void @__bennett_qload(ptr noundef, ptr noundef, ptr noundef) local_unnamed_addr #2

declare void @__bennett_qstore(ptr noundef, ptr noundef, ptr noundef) local_unnamed_addr #2

declare void @__bennett_qfree(ptr noundef) local_unnamed_addr #2

attributes #0 = { nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { nounwind }

!llvm.module.flags = !{!0, !1, !2, !3}
!llvm.ident = !{!4}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 2}
!4 = !{!"Ubuntu clang version 18.1.3 (1ubuntu1)"}
!5 = !{!6, !7, i64 0}
!6 = !{!"env", !7, i64 0, !10, i64 8, !11, i64 16}
!7 = !{!"any pointer", !8, i64 0}
!8 = !{!"omnipotent char", !9, i64 0}
!9 = !{!"Simple C/C++ TBAA"}
!10 = !{!"long", !8, i64 0}
!11 = !{!"double", !8, i64 0}
!12 = !{!6, !10, i64 8}
!13 = !{!6, !11, i64 16}
!14 = !{!7, !7, i64 0}
