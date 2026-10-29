; ModuleID = 'start'
source_filename = "start"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-linux-gnu"

@_j_str___bennett_ctrl_v_1 = private unnamed_addr constant [17 x i8] c"__bennett_ctrl_v\00", align 1
@jl_RTLD_DEFAULT_handle = external constant ptr
@ccall___bennett_ctrl_v_1700 = local_unnamed_addr global ptr null

;  @ /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/gpucompiler.jl:18 within `kV`
define void @julia_kV_1698(ptr %"h::Ptr") local_unnamed_addr #0 {
top:
  %0 = load atomic ptr, ptr @ccall___bennett_ctrl_v_1700 unordered, align 8
  %is_cached.not = icmp eq ptr %0, null
  br i1 %is_cached.not, label %dlsym, label %ccall

dlsym:                                            ; preds = %top
  %__bennett_ctrl_v.found = call ptr @ijl_load_and_lookup(ptr null, ptr nonnull @_j_str___bennett_ctrl_v_1, ptr nonnull @jl_RTLD_DEFAULT_handle)
  store atomic ptr %__bennett_ctrl_v.found, ptr @ccall___bennett_ctrl_v_1700 release, align 8
  br label %ccall

ccall:                                            ; preds = %dlsym, %top
  %1 = phi ptr [ %0, %top ], [ %__bennett_ctrl_v.found, %dlsym ]
  call void (ptr, i64, ptr, i64, ...) %1(ptr %"h::Ptr", i64 0, ptr null, i64 8, i32 1, double 2.500000e+00)
  ret void
}

declare ptr @ijl_load_and_lookup(ptr, ptr, ptr) local_unnamed_addr

attributes #0 = { "frame-pointer"="all" }

!llvm.module.flags = !{!0, !1, !2, !3}

!0 = !{i32 2, !"Dwarf Version", i32 4}
!1 = !{i32 2, !"Debug Info Version", i32 3}
!2 = !{i32 1, !"stack-protector-guard", !""}
!3 = !{i32 1, !"override-stack-alignment", i32 0}
