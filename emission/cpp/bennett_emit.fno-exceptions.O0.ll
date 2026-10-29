; ModuleID = 'bennett_emit.cpp'
source_filename = "bennett_emit.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct.env = type { ptr, i64, double }
%class.anon = type { i8 }
%struct.Scope = type { ptr }

$_ZN5ScopeC2EP11__bennett_q = comdat any

$_ZN5ScopeD2Ev = comdat any

; Function Attrs: mustprogress noinline nounwind uwtable
define dso_local i64 @case_entry(i64 noundef %0) #0 {
  %2 = alloca i64, align 8
  %3 = alloca ptr, align 8
  %4 = alloca double, align 8
  %5 = alloca i64, align 8
  %6 = alloca %struct.env, align 8
  %7 = alloca %class.anon, align 1
  %8 = alloca [4 x ptr], align 16
  %9 = alloca i32, align 4
  %10 = alloca %struct.Scope, align 8
  %11 = alloca i32, align 4
  store i64 %0, ptr %2, align 8
  %12 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 4)
  store ptr %12, ptr %3, align 8
  %13 = load ptr, ptr %3, align 8
  call void @__bennett_gate(i32 noundef 1, ptr noundef %13, i64 noundef 0)
  %14 = load i64, ptr %2, align 8
  %15 = uitofp i64 %14 to double
  %16 = fmul double %15, 1.250000e-01
  store double %16, ptr %4, align 8
  %17 = load ptr, ptr %3, align 8
  %18 = load double, ptr %4, align 8
  call void @__bennett_rot(i32 noundef 3, ptr noundef %17, i64 noundef 1, double noundef %18)
  %19 = load ptr, ptr %3, align 8
  %20 = load ptr, ptr %3, align 8
  call void @__bennett_gate2(i32 noundef 4, ptr noundef %19, i64 noundef 0, ptr noundef %20, i64 noundef 1)
  store i64 0, ptr %5, align 8
  %21 = load ptr, ptr %3, align 8
  %22 = call zeroext i1 @__bennett_measure(ptr noundef %21, i64 noundef 0)
  br i1 %22, label %23, label %25

23:                                               ; preds = %1
  %24 = load ptr, ptr %3, align 8
  call void @__bennett_gate(i32 noundef 2, ptr noundef %24, i64 noundef 2)
  store i64 1, ptr %5, align 8
  br label %25

25:                                               ; preds = %23, %1
  %26 = getelementptr inbounds %struct.env, ptr %6, i32 0, i32 0
  %27 = load ptr, ptr %3, align 8
  store ptr %27, ptr %26, align 8
  %28 = getelementptr inbounds %struct.env, ptr %6, i32 0, i32 1
  store i64 3, ptr %28, align 8
  %29 = getelementptr inbounds %struct.env, ptr %6, i32 0, i32 2
  %30 = load double, ptr %4, align 8
  store double %30, ptr %29, align 8
  %31 = load ptr, ptr %3, align 8
  call void @__bennett_ctrl(ptr noundef %31, i64 noundef 0, ptr noundef @_ZL4bodyPv, i64 noundef 8, ptr noundef %6)
  %32 = load ptr, ptr %3, align 8
  %33 = call noundef ptr @"_ZZ10case_entryENK3$_0cvPFvPvEEv"(ptr noundef nonnull align 1 dereferenceable(1) %7) #2
  call void @__bennett_ctrl(ptr noundef %32, i64 noundef 1, ptr noundef %33, i64 noundef 8, ptr noundef %6)
  store i32 0, ptr %9, align 4
  br label %34

34:                                               ; preds = %42, %25
  %35 = load i32, ptr %9, align 4
  %36 = icmp slt i32 %35, 4
  br i1 %36, label %37, label %45

37:                                               ; preds = %34
  %38 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1)
  %39 = load i32, ptr %9, align 4
  %40 = sext i32 %39 to i64
  %41 = getelementptr inbounds [4 x ptr], ptr %8, i64 0, i64 %40
  store ptr %38, ptr %41, align 8
  br label %42

42:                                               ; preds = %37
  %43 = load i32, ptr %9, align 4
  %44 = add nsw i32 %43, 1
  store i32 %44, ptr %9, align 4
  br label %34, !llvm.loop !6

45:                                               ; preds = %34
  %46 = load i64, ptr %2, align 8
  %47 = and i64 %46, 3
  %48 = getelementptr inbounds [4 x ptr], ptr %8, i64 0, i64 %47
  %49 = load ptr, ptr %48, align 8
  call void @__bennett_gate(i32 noundef 1, ptr noundef %49, i64 noundef 0)
  %50 = load ptr, ptr %3, align 8
  %51 = load ptr, ptr %3, align 8
  call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr noundef %50, i64 noundef 0, ptr noundef @_ZL4bodyPv, i64 noundef 8, i32 noundef 1, double noundef 2.500000e+00, ptr noundef %51)
  call void @__bennett_adj(ptr noundef @_ZL4bodyPv, ptr noundef %6)
  %52 = call ptr @__bennett_qborrow(i64 noundef 0, i64 noundef 1)
  call void @_ZN5ScopeC2EP11__bennett_q(ptr noundef nonnull align 8 dereferenceable(8) %10, ptr noundef %52)
  %53 = getelementptr inbounds %struct.Scope, ptr %10, i32 0, i32 0
  %54 = load ptr, ptr %53, align 8
  call void @__bennett_gate(i32 noundef 6, ptr noundef %54, i64 noundef 0)
  %55 = load i64, ptr %2, align 8
  call void @_Z9may_throwm(i64 noundef %55)
  %56 = getelementptr inbounds %struct.Scope, ptr %10, i32 0, i32 0
  %57 = load ptr, ptr %56, align 8
  call void @__bennett_gate(i32 noundef 7, ptr noundef %57, i64 noundef 0)
  %58 = load ptr, ptr %3, align 8
  call void @__bennett_ctrl(ptr noundef %58, i64 noundef 0, ptr noundef @_ZL4bodyPv, i64 noundef 8, ptr noundef %6)
  call void @_ZN5ScopeD2Ev(ptr noundef nonnull align 8 dereferenceable(8) %10) #2
  store i32 0, ptr %11, align 4
  br label %59

59:                                               ; preds = %67, %45
  %60 = load i32, ptr %11, align 4
  %61 = icmp slt i32 %60, 4
  br i1 %61, label %62, label %70

62:                                               ; preds = %59
  %63 = load i32, ptr %11, align 4
  %64 = sext i32 %63 to i64
  %65 = getelementptr inbounds [4 x ptr], ptr %8, i64 0, i64 %64
  %66 = load ptr, ptr %65, align 8
  call void @__bennett_qfree(ptr noundef %66)
  br label %67

67:                                               ; preds = %62
  %68 = load i32, ptr %11, align 4
  %69 = add nsw i32 %68, 1
  store i32 %69, ptr %11, align 4
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

; Function Attrs: mustprogress noinline nounwind uwtable
define internal void @_ZL4bodyPv(ptr noundef %0) #0 {
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

; Function Attrs: mustprogress noinline nounwind uwtable
define internal noundef ptr @"_ZZ10case_entryENK3$_0cvPFvPvEEv"(ptr noundef nonnull align 1 dereferenceable(1) %0) #0 align 2 {
  %2 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  %3 = load ptr, ptr %2, align 8
  ret ptr @"_ZZ10case_entryEN3$_08__invokeEPv"
}

declare void @__bennett_ctrl_v(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ...) #1

declare void @__bennett_adj(ptr noundef, ptr noundef) #1

declare ptr @__bennett_qborrow(i64 noundef, i64 noundef) #1

; Function Attrs: mustprogress noinline nounwind uwtable
define linkonce_odr dso_local void @_ZN5ScopeC2EP11__bennett_q(ptr noundef nonnull align 8 dereferenceable(8) %0, ptr noundef %1) unnamed_addr #0 comdat align 2 {
  %3 = alloca ptr, align 8
  %4 = alloca ptr, align 8
  store ptr %0, ptr %3, align 8
  store ptr %1, ptr %4, align 8
  %5 = load ptr, ptr %3, align 8
  %6 = getelementptr inbounds %struct.Scope, ptr %5, i32 0, i32 0
  %7 = load ptr, ptr %4, align 8
  store ptr %7, ptr %6, align 8
  ret void
}

declare void @_Z9may_throwm(i64 noundef) #1

; Function Attrs: mustprogress noinline nounwind uwtable
define linkonce_odr dso_local void @_ZN5ScopeD2Ev(ptr noundef nonnull align 8 dereferenceable(8) %0) unnamed_addr #0 comdat align 2 {
  %2 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds %struct.Scope, ptr %3, i32 0, i32 0
  %5 = load ptr, ptr %4, align 8
  call void @__bennett_qfree(ptr noundef %5)
  ret void
}

declare void @__bennett_qfree(ptr noundef) #1

; Function Attrs: mustprogress noinline nounwind uwtable
define internal void @"_ZZ10case_entryEN3$_08__invokeEPv"(ptr noundef %0) #0 align 2 {
  %2 = alloca ptr, align 8
  %3 = alloca %class.anon, align 1
  store ptr %0, ptr %2, align 8
  %4 = load ptr, ptr %2, align 8
  call void @"_ZZ10case_entryENK3$_0clEPv"(ptr noundef nonnull align 1 dereferenceable(1) %3, ptr noundef %4)
  ret void
}

; Function Attrs: mustprogress noinline nounwind uwtable
define internal void @"_ZZ10case_entryENK3$_0clEPv"(ptr noundef nonnull align 1 dereferenceable(1) %0, ptr noundef %1) #0 align 2 {
  %3 = alloca ptr, align 8
  %4 = alloca ptr, align 8
  %5 = alloca ptr, align 8
  store ptr %0, ptr %3, align 8
  store ptr %1, ptr %4, align 8
  %6 = load ptr, ptr %3, align 8
  %7 = load ptr, ptr %4, align 8
  store ptr %7, ptr %5, align 8
  %8 = load ptr, ptr %5, align 8
  %9 = getelementptr inbounds %struct.env, ptr %8, i32 0, i32 0
  %10 = load ptr, ptr %9, align 8
  %11 = load ptr, ptr %5, align 8
  %12 = getelementptr inbounds %struct.env, ptr %11, i32 0, i32 1
  %13 = load i64, ptr %12, align 8
  call void @__bennett_gate(i32 noundef 5, ptr noundef %10, i64 noundef %13)
  ret void
}

attributes #0 = { mustprogress noinline nounwind uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #2 = { nounwind }

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
