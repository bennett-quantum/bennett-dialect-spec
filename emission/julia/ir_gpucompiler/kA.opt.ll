; ModuleID = 'start'
source_filename = "start"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-linux-gnu"

@ccalllib_libbennett_stub_so1672 = global ptr null
@ccall___bennett_gate_1673 = local_unnamed_addr global ptr null
@jlplt___bennett_gate_1674_got = local_unnamed_addr global ptr @jlplt___bennett_gate_1674 #0
@_j_str__home_tobias_Projects_ben____1 = private unnamed_addr constant [95 x i8] c"/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/libbennett_stub.so\00", align 1
@_j_str___bennett_gate_2 = private unnamed_addr constant [15 x i8] c"__bennett_gate\00", align 1

;  @ /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/gpucompiler.jl:16 within `kA`
define void @julia_kA_1670(ptr %"h::Ptr") local_unnamed_addr #1 {
top:
  %__bennett_gate = load atomic ptr, ptr @jlplt___bennett_gate_1674_got unordered, align 8
  call void %__bennett_gate(i32 1, ptr %"h::Ptr", i64 0)
  ret void
}

define private void @jlplt___bennett_gate_1674(i32 %0, ptr %1, i64 %2) {
top:
  %3 = load atomic ptr, ptr @ccall___bennett_gate_1673 unordered, align 8
  %is_cached.not = icmp eq ptr %3, null
  br i1 %is_cached.not, label %dlsym, label %ccall

dlsym:                                            ; preds = %top
  %__bennett_gate.found = call ptr @ijl_load_and_lookup(ptr nonnull @_j_str__home_tobias_Projects_ben____1, ptr nonnull @_j_str___bennett_gate_2, ptr nonnull @ccalllib_libbennett_stub_so1672)
  store atomic ptr %__bennett_gate.found, ptr @ccall___bennett_gate_1673 release, align 8
  br label %ccall

ccall:                                            ; preds = %dlsym, %top
  %4 = phi ptr [ %3, %top ], [ %__bennett_gate.found, %dlsym ]
  store atomic ptr %4, ptr @jlplt___bennett_gate_1674_got release, align 8
  musttail call void %4(i32 %0, ptr %1, i64 %2)
  ret void
}

declare ptr @ijl_load_and_lookup(ptr, ptr, ptr) local_unnamed_addr

attributes #0 = { "julia.fname"="__bennett_gate" "julia.libname"="/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/libbennett_stub.so" }
attributes #1 = { "frame-pointer"="all" }

!llvm.module.flags = !{!0, !1, !2, !3}

!0 = !{i32 2, !"Dwarf Version", i32 4}
!1 = !{i32 2, !"Debug Info Version", i32 3}
!2 = !{i32 1, !"stack-protector-guard", !""}
!3 = !{i32 1, !"override-stack-alignment", i32 0}
