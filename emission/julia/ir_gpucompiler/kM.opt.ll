; ModuleID = 'start'
source_filename = "start"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-linux-gnu"

@jl_RTLD_DEFAULT_handle = external constant ptr
@ccall___bennett_measure_1687 = local_unnamed_addr global ptr null
@jlplt___bennett_measure_1688_got = local_unnamed_addr global ptr @jlplt___bennett_measure_1688 #0
@_j_str___bennett_measure_1 = private unnamed_addr constant [18 x i8] c"__bennett_measure\00", align 1

;  @ /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/gpucompiler.jl:17 within `kM`
define i8 @julia_kM_1685(ptr %"h::Ptr") local_unnamed_addr #1 {
top:
  %__bennett_measure = load atomic ptr, ptr @jlplt___bennett_measure_1688_got unordered, align 8
  %0 = call i8 %__bennett_measure(ptr %"h::Ptr", i64 0)
  ret i8 %0
}

define private i8 @jlplt___bennett_measure_1688(ptr %0, i64 %1) {
top:
  %2 = load atomic ptr, ptr @ccall___bennett_measure_1687 unordered, align 8
  %is_cached.not = icmp eq ptr %2, null
  br i1 %is_cached.not, label %dlsym, label %ccall

dlsym:                                            ; preds = %top
  %__bennett_measure.found = call ptr @ijl_load_and_lookup(ptr null, ptr nonnull @_j_str___bennett_measure_1, ptr nonnull @jl_RTLD_DEFAULT_handle)
  store atomic ptr %__bennett_measure.found, ptr @ccall___bennett_measure_1687 release, align 8
  br label %ccall

ccall:                                            ; preds = %dlsym, %top
  %3 = phi ptr [ %2, %top ], [ %__bennett_measure.found, %dlsym ]
  store atomic ptr %3, ptr @jlplt___bennett_measure_1688_got release, align 8
  %4 = musttail call i8 %3(ptr %0, i64 %1)
  ret i8 %4
}

declare ptr @ijl_load_and_lookup(ptr, ptr, ptr) local_unnamed_addr

attributes #0 = { "julia.fname"="__bennett_measure" "julia.libidx"="0" }
attributes #1 = { "frame-pointer"="all" }

!llvm.module.flags = !{!0, !1, !2, !3}

!0 = !{i32 2, !"Dwarf Version", i32 4}
!1 = !{i32 2, !"Debug Info Version", i32 3}
!2 = !{i32 1, !"stack-protector-guard", !""}
!3 = !{i32 1, !"override-stack-alignment", i32 0}
