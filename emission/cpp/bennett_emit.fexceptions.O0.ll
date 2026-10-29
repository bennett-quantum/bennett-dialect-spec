; ModuleID = 'bennett_emit.cpp'
source_filename = "bennett_emit.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct.env = type { ptr, i64, double }
%class.anon = type { i8 }
%struct.Scope = type { ptr }

$_ZN5ScopeC2EP11__bennett_q = comdat any

$_ZN5ScopeD2Ev = comdat any

$__clang_call_terminate = comdat any

; Function Attrs: mustprogress noinline uwtable
define dso_local i64 @case_entry(i64 noundef %0) #0 personality ptr @__gxx_personality_v0 {
  %2 = alloca i64, align 8
  %3 = alloca ptr, align 8
  %4 = alloca double, align 8
  %5 = alloca i64, align 8
  %6 = alloca %struct.env, align 8
  %7 = alloca %class.anon, align 1
  %8 = alloca [4 x ptr], align 16
  %9 = alloca i32, align 4
  %10 = alloca %struct.Scope, align 8
  %11 = alloca ptr, align 8
  %12 = alloca i32, align 4
  %13 = alloca i32, align 4
  store i64 %0, ptr %2, align 8
  %14 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 4)
  store ptr %14, ptr %3, align 8
  %15 = load ptr, ptr %3, align 8
  call void @__bennett_gate(i32 noundef 1, ptr noundef %15, i64 noundef 0)
  %16 = load i64, ptr %2, align 8
  %17 = uitofp i64 %16 to double
  %18 = fmul double %17, 1.250000e-01
  store double %18, ptr %4, align 8
  %19 = load ptr, ptr %3, align 8
  %20 = load double, ptr %4, align 8
  call void @__bennett_rot(i32 noundef 3, ptr noundef %19, i64 noundef 1, double noundef %20)
  %21 = load ptr, ptr %3, align 8
  %22 = load ptr, ptr %3, align 8
  call void @__bennett_gate2(i32 noundef 4, ptr noundef %21, i64 noundef 0, ptr noundef %22, i64 noundef 1)
  store i64 0, ptr %5, align 8
  %23 = load ptr, ptr %3, align 8
  %24 = call zeroext i1 @__bennett_measure(ptr noundef %23, i64 noundef 0)
  br i1 %24, label %25, label %27

25:                                               ; preds = %1
  %26 = load ptr, ptr %3, align 8
  call void @__bennett_gate(i32 noundef 2, ptr noundef %26, i64 noundef 2)
  store i64 1, ptr %5, align 8
  br label %27

27:                                               ; preds = %25, %1
  %28 = getelementptr inbounds %struct.env, ptr %6, i32 0, i32 0
  %29 = load ptr, ptr %3, align 8
  store ptr %29, ptr %28, align 8
  %30 = getelementptr inbounds %struct.env, ptr %6, i32 0, i32 1
  store i64 3, ptr %30, align 8
  %31 = getelementptr inbounds %struct.env, ptr %6, i32 0, i32 2
  %32 = load double, ptr %4, align 8
  store double %32, ptr %31, align 8
  %33 = load ptr, ptr %3, align 8
  call void @__bennett_ctrl(ptr noundef %33, i64 noundef 0, ptr noundef @_ZL4bodyPv, i64 noundef 8, ptr noundef %6)
  %34 = load ptr, ptr %3, align 8
  %35 = call noundef ptr @"_ZZ10case_entryENK3$_0cvPFvPvEEv"(ptr noundef nonnull align 1 dereferenceable(1) %7) #4
  call void @__bennett_ctrl(ptr noundef %34, i64 noundef 1, ptr noundef %35, i64 noundef 8, ptr noundef %6)
  store i32 0, ptr %9, align 4
  br label %36

36:                                               ; preds = %44, %27
  %37 = load i32, ptr %9, align 4
  %38 = icmp slt i32 %37, 4
  br i1 %38, label %39, label %47

39:                                               ; preds = %36
  %40 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1)
  %41 = load i32, ptr %9, align 4
  %42 = sext i32 %41 to i64
  %43 = getelementptr inbounds [4 x ptr], ptr %8, i64 0, i64 %42
  store ptr %40, ptr %43, align 8
  br label %44

44:                                               ; preds = %39
  %45 = load i32, ptr %9, align 4
  %46 = add nsw i32 %45, 1
  store i32 %46, ptr %9, align 4
  br label %36, !llvm.loop !6

47:                                               ; preds = %36
  %48 = load i64, ptr %2, align 8
  %49 = and i64 %48, 3
  %50 = getelementptr inbounds [4 x ptr], ptr %8, i64 0, i64 %49
  %51 = load ptr, ptr %50, align 8
  call void @__bennett_gate(i32 noundef 1, ptr noundef %51, i64 noundef 0)
  %52 = load ptr, ptr %3, align 8
  %53 = load ptr, ptr %3, align 8
  call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr noundef %52, i64 noundef 0, ptr noundef @_ZL4bodyPv, i64 noundef 8, i32 noundef 1, double noundef 2.500000e+00, ptr noundef %53)
  call void @__bennett_adj(ptr noundef @_ZL4bodyPv, ptr noundef %6)
  %54 = call ptr @__bennett_qborrow(i64 noundef 0, i64 noundef 1)
  call void @_ZN5ScopeC2EP11__bennett_q(ptr noundef nonnull align 8 dereferenceable(8) %10, ptr noundef %54)
  %55 = getelementptr inbounds %struct.Scope, ptr %10, i32 0, i32 0
  %56 = load ptr, ptr %55, align 8
  invoke void @__bennett_gate(i32 noundef 6, ptr noundef %56, i64 noundef 0)
          to label %57 unwind label %76

57:                                               ; preds = %47
  %58 = load i64, ptr %2, align 8
  invoke void @_Z9may_throwm(i64 noundef %58)
          to label %59 unwind label %76

59:                                               ; preds = %57
  %60 = getelementptr inbounds %struct.Scope, ptr %10, i32 0, i32 0
  %61 = load ptr, ptr %60, align 8
  invoke void @__bennett_gate(i32 noundef 7, ptr noundef %61, i64 noundef 0)
          to label %62 unwind label %76

62:                                               ; preds = %59
  %63 = load ptr, ptr %3, align 8
  invoke void @__bennett_ctrl(ptr noundef %63, i64 noundef 0, ptr noundef @_ZL4bodyPv, i64 noundef 8, ptr noundef %6)
          to label %64 unwind label %76

64:                                               ; preds = %62
  call void @_ZN5ScopeD2Ev(ptr noundef nonnull align 8 dereferenceable(8) %10) #4
  store i32 0, ptr %13, align 4
  br label %65

65:                                               ; preds = %73, %64
  %66 = load i32, ptr %13, align 4
  %67 = icmp slt i32 %66, 4
  br i1 %67, label %68, label %80

68:                                               ; preds = %65
  %69 = load i32, ptr %13, align 4
  %70 = sext i32 %69 to i64
  %71 = getelementptr inbounds [4 x ptr], ptr %8, i64 0, i64 %70
  %72 = load ptr, ptr %71, align 8
  call void @__bennett_qfree(ptr noundef %72)
  br label %73

73:                                               ; preds = %68
  %74 = load i32, ptr %13, align 4
  %75 = add nsw i32 %74, 1
  store i32 %75, ptr %13, align 4
  br label %65, !llvm.loop !8

76:                                               ; preds = %62, %59, %57, %47
  %77 = landingpad { ptr, i32 }
          cleanup
  %78 = extractvalue { ptr, i32 } %77, 0
  store ptr %78, ptr %11, align 8
  %79 = extractvalue { ptr, i32 } %77, 1
  store i32 %79, ptr %12, align 4
  call void @_ZN5ScopeD2Ev(ptr noundef nonnull align 8 dereferenceable(8) %10) #4
  br label %83

80:                                               ; preds = %65
  %81 = load ptr, ptr %3, align 8
  call void @__bennett_qfree(ptr noundef %81)
  %82 = load i64, ptr %5, align 8
  ret i64 %82

83:                                               ; preds = %76
  %84 = load ptr, ptr %11, align 8
  %85 = load i32, ptr %12, align 4
  %86 = insertvalue { ptr, i32 } poison, ptr %84, 0
  %87 = insertvalue { ptr, i32 } %86, i32 %85, 1
  resume { ptr, i32 } %87
}

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef) #1

declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef) #1

declare void @__bennett_rot(i32 noundef, ptr noundef, i64 noundef, double noundef) #1

declare void @__bennett_gate2(i32 noundef, ptr noundef, i64 noundef, ptr noundef, i64 noundef) #1

declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef) #1

declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ptr noundef) #1

; Function Attrs: mustprogress noinline uwtable
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
define internal noundef ptr @"_ZZ10case_entryENK3$_0cvPFvPvEEv"(ptr noundef nonnull align 1 dereferenceable(1) %0) #2 align 2 {
  %2 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  %3 = load ptr, ptr %2, align 8
  ret ptr @"_ZZ10case_entryEN3$_08__invokeEPv"
}

declare void @__bennett_ctrl_v(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ...) #1

declare void @__bennett_adj(ptr noundef, ptr noundef) #1

declare ptr @__bennett_qborrow(i64 noundef, i64 noundef) #1

; Function Attrs: mustprogress noinline nounwind uwtable
define linkonce_odr dso_local void @_ZN5ScopeC2EP11__bennett_q(ptr noundef nonnull align 8 dereferenceable(8) %0, ptr noundef %1) unnamed_addr #2 comdat align 2 {
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

declare i32 @__gxx_personality_v0(...)

declare void @_Z9may_throwm(i64 noundef) #1

; Function Attrs: mustprogress noinline nounwind uwtable
define linkonce_odr dso_local void @_ZN5ScopeD2Ev(ptr noundef nonnull align 8 dereferenceable(8) %0) unnamed_addr #2 comdat align 2 personality ptr @__gxx_personality_v0 {
  %2 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds %struct.Scope, ptr %3, i32 0, i32 0
  %5 = load ptr, ptr %4, align 8
  invoke void @__bennett_qfree(ptr noundef %5)
          to label %6 unwind label %7

6:                                                ; preds = %1
  ret void

7:                                                ; preds = %1
  %8 = landingpad { ptr, i32 }
          catch ptr null
  %9 = extractvalue { ptr, i32 } %8, 0
  call void @__clang_call_terminate(ptr %9) #5
  unreachable
}

declare void @__bennett_qfree(ptr noundef) #1

; Function Attrs: mustprogress noinline uwtable
define internal void @"_ZZ10case_entryEN3$_08__invokeEPv"(ptr noundef %0) #0 align 2 {
  %2 = alloca ptr, align 8
  %3 = alloca %class.anon, align 1
  store ptr %0, ptr %2, align 8
  %4 = load ptr, ptr %2, align 8
  call void @"_ZZ10case_entryENK3$_0clEPv"(ptr noundef nonnull align 1 dereferenceable(1) %3, ptr noundef %4)
  ret void
}

; Function Attrs: mustprogress noinline uwtable
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

; Function Attrs: noinline noreturn nounwind uwtable
define linkonce_odr hidden void @__clang_call_terminate(ptr noundef %0) #3 comdat {
  %2 = call ptr @__cxa_begin_catch(ptr %0) #4
  call void @_ZSt9terminatev() #5
  unreachable
}

declare ptr @__cxa_begin_catch(ptr)

declare void @_ZSt9terminatev()

attributes #0 = { mustprogress noinline uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #2 = { mustprogress noinline nounwind uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { noinline noreturn nounwind uwtable "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nounwind }
attributes #5 = { noreturn nounwind }

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
