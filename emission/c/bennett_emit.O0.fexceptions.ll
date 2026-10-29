; ModuleID = 'bennett_emit.c'
source_filename = "bennett_emit.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct.env = type { ptr, i64, double }

; Function Attrs: noinline uwtable
define dso_local i64 @case_entry(i64 noundef %0) #0 {
  %2 = alloca i64, align 8
  %3 = alloca ptr, align 8
  %4 = alloca double, align 8
  %5 = alloca i64, align 8
  %6 = alloca %struct.env, align 8
  %7 = alloca [4 x ptr], align 16
  %8 = alloca i32, align 4
  %9 = alloca ptr, align 8
  %10 = alloca i32, align 4
  store i64 %0, ptr %2, align 8
  %11 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 4)
  store ptr %11, ptr %3, align 8
  %12 = load ptr, ptr %3, align 8
  call void @__bennett_gate(i32 noundef 1, ptr noundef %12, i64 noundef 0)
  %13 = load i64, ptr %2, align 8
  %14 = uitofp i64 %13 to double
  %15 = fmul double %14, 1.250000e-01
  store double %15, ptr %4, align 8
  %16 = load ptr, ptr %3, align 8
  %17 = load double, ptr %4, align 8
  call void @__bennett_rot(i32 noundef 3, ptr noundef %16, i64 noundef 1, double noundef %17)
  %18 = load ptr, ptr %3, align 8
  %19 = load ptr, ptr %3, align 8
  call void @__bennett_gate2(i32 noundef 4, ptr noundef %18, i64 noundef 0, ptr noundef %19, i64 noundef 1)
  store i64 0, ptr %5, align 8
  %20 = load ptr, ptr %3, align 8
  %21 = call zeroext i1 @__bennett_measure(ptr noundef %20, i64 noundef 0)
  br i1 %21, label %22, label %24

22:                                               ; preds = %1
  %23 = load ptr, ptr %3, align 8
  call void @__bennett_gate(i32 noundef 2, ptr noundef %23, i64 noundef 2)
  store i64 1, ptr %5, align 8
  br label %24

24:                                               ; preds = %22, %1
  %25 = getelementptr inbounds %struct.env, ptr %6, i32 0, i32 0
  %26 = load ptr, ptr %3, align 8
  store ptr %26, ptr %25, align 8
  %27 = getelementptr inbounds %struct.env, ptr %6, i32 0, i32 1
  store i64 3, ptr %27, align 8
  %28 = getelementptr inbounds %struct.env, ptr %6, i32 0, i32 2
  %29 = load double, ptr %4, align 8
  store double %29, ptr %28, align 8
  %30 = load ptr, ptr %3, align 8
  call void @__bennett_ctrl(ptr noundef %30, i64 noundef 0, ptr noundef @body, i64 noundef 8, ptr noundef %6)
  store i32 0, ptr %8, align 4
  br label %31

31:                                               ; preds = %39, %24
  %32 = load i32, ptr %8, align 4
  %33 = icmp slt i32 %32, 4
  br i1 %33, label %34, label %42

34:                                               ; preds = %31
  %35 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1)
  %36 = load i32, ptr %8, align 4
  %37 = sext i32 %36 to i64
  %38 = getelementptr inbounds [4 x ptr], ptr %7, i64 0, i64 %37
  store ptr %35, ptr %38, align 8
  br label %39

39:                                               ; preds = %34
  %40 = load i32, ptr %8, align 4
  %41 = add nsw i32 %40, 1
  store i32 %41, ptr %8, align 4
  br label %31, !llvm.loop !6

42:                                               ; preds = %31
  %43 = load i64, ptr %2, align 8
  %44 = and i64 %43, 3
  %45 = getelementptr inbounds [4 x ptr], ptr %7, i64 0, i64 %44
  %46 = load ptr, ptr %45, align 8
  call void @__bennett_gate(i32 noundef 1, ptr noundef %46, i64 noundef 0)
  %47 = load ptr, ptr %3, align 8
  %48 = load ptr, ptr %3, align 8
  call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr noundef %47, i64 noundef 0, ptr noundef @body, i64 noundef 8, i32 noundef 1, double noundef 2.500000e+00, ptr noundef %48)
  call void @__bennett_adj(ptr noundef @body, ptr noundef %6)
  call void @__bennett_compute(ptr noundef @body, ptr noundef @body, ptr noundef %6)
  call void @__bennett_reversible(ptr noundef @body, i64 noundef 3, ptr noundef %6)
  call void @__bennett_inplace(ptr noundef @body, ptr noundef @body, ptr noundef %6)
  %49 = call ptr @__bennett_qborrow(i64 noundef 0, i64 noundef 1)
  store ptr %49, ptr %9, align 8
  %50 = load ptr, ptr %9, align 8
  %51 = load ptr, ptr %3, align 8
  %52 = getelementptr inbounds [4 x ptr], ptr %7, i64 0, i64 0
  %53 = load ptr, ptr %52, align 16
  call void @__bennett_qload(ptr noundef %50, ptr noundef %51, ptr noundef %53)
  %54 = load ptr, ptr %3, align 8
  %55 = getelementptr inbounds [4 x ptr], ptr %7, i64 0, i64 1
  %56 = load ptr, ptr %55, align 8
  %57 = load ptr, ptr %9, align 8
  call void @__bennett_qstore(ptr noundef %54, ptr noundef %56, ptr noundef %57)
  %58 = load ptr, ptr %9, align 8
  call void @__bennett_qfree(ptr noundef %58)
  store i32 0, ptr %10, align 4
  br label %59

59:                                               ; preds = %67, %42
  %60 = load i32, ptr %10, align 4
  %61 = icmp slt i32 %60, 4
  br i1 %61, label %62, label %70

62:                                               ; preds = %59
  %63 = load i32, ptr %10, align 4
  %64 = sext i32 %63 to i64
  %65 = getelementptr inbounds [4 x ptr], ptr %7, i64 0, i64 %64
  %66 = load ptr, ptr %65, align 8
  call void @__bennett_qfree(ptr noundef %66)
  br label %67

67:                                               ; preds = %62
  %68 = load i32, ptr %10, align 4
  %69 = add nsw i32 %68, 1
  store i32 %69, ptr %10, align 4
  br label %59, !llvm.loop !8

70:                                               ; preds = %59
  %71 = load ptr, ptr %3, align 8
  call void @__bennett_qfree(ptr noundef %71)
  %72 = load i64, ptr %5, align 8
  ret i64 %72
}

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef) #1

declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef) #1

declare void @__bennett_rot(i32 noundef, ptr noundef, i64 noundef, double noundef) #1

declare void @__bennett_gate2(i32 noundef, ptr noundef, i64 noundef, ptr noundef, i64 noundef) #1

declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef) #1

declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ptr noundef) #1

; Function Attrs: noinline uwtable
define internal void @body(ptr noundef %0) #0 {
  %2 = alloca ptr, align 8
  %3 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  %4 = load ptr, ptr %2, align 8
  store ptr %4, ptr %3, align 8
  %5 = load ptr, ptr %3, align 8
  %6 = getelementptr inbounds %struct.env, ptr %5, i32 0, i32 0
  %7 = load ptr, ptr %6, align 8
  %8 = load ptr, ptr %3, align 8
  %9 = getelementptr inbounds %struct.env, ptr %8, i32 0, i32 1
  %10 = load i64, ptr %9, align 8
  %11 = load ptr, ptr %3, align 8
  %12 = getelementptr inbounds %struct.env, ptr %11, i32 0, i32 2
  %13 = load double, ptr %12, align 8
  call void @__bennett_rot(i32 noundef 1, ptr noundef %7, i64 noundef %10, double noundef %13)
  %14 = load ptr, ptr %3, align 8
  %15 = getelementptr inbounds %struct.env, ptr %14, i32 0, i32 0
  %16 = load ptr, ptr %15, align 8
  %17 = load ptr, ptr %3, align 8
  %18 = getelementptr inbounds %struct.env, ptr %17, i32 0, i32 1
  %19 = load i64, ptr %18, align 8
  call void @__bennett_gate(i32 noundef 2, ptr noundef %16, i64 noundef %19)
  ret void
}

declare void @__bennett_ctrl_v(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ...) #1

declare void @__bennett_adj(ptr noundef, ptr noundef) #1

declare void @__bennett_compute(ptr noundef, ptr noundef, ptr noundef) #1

declare void @__bennett_reversible(ptr noundef, i64 noundef, ptr noundef) #1

declare void @__bennett_inplace(ptr noundef, ptr noundef, ptr noundef) #1

declare ptr @__bennett_qborrow(i64 noundef, i64 noundef) #1

declare void @__bennett_qload(ptr noundef, ptr noundef, ptr noundef) #1

declare void @__bennett_qstore(ptr noundef, ptr noundef, ptr noundef) #1

declare void @__bennett_qfree(ptr noundef) #1

attributes #0 = { noinline uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 2}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"Ubuntu clang version 18.1.3 (1ubuntu1)"}
!6 = distinct !{!6, !7}
!7 = !{!"llvm.loop.mustprogress"}
!8 = distinct !{!8, !7}
