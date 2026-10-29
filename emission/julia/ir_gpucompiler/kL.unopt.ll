; ModuleID = 'start'
source_filename = "start"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128-ni:10:11:12:13"
target triple = "x86_64-linux-gnu"

@_Z2kLPv_jl_global_460909126572bdec = private unnamed_addr constant ptr inttoptr (i64 135053106823184 to ptr)
@_Z2kLPv_jl_global_ef7679269d67cf27 = private unnamed_addr constant ptr inttoptr (i64 135052649108336 to ptr)

;  @ /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/gpucompiler.jl:19 within `kL`
define void @julia_kL_1707(ptr %"h::Ptr") local_unnamed_addr #0 {
top:
  %pgcstack = call ptr @julia.get_pgcstack()
  %"jl_global#1709" = load ptr, ptr @_Z2kLPv_jl_global_460909126572bdec, align 8
  %"jl_global#1710" = load ptr, ptr @_Z2kLPv_jl_global_ef7679269d67cf27, align 8
  call fastcc void @julia_kL_1707u1711(ptr %"h::Ptr")
  ret void
}

declare ptr @julia.get_pgcstack() local_unnamed_addr

define internal fastcc void @julia_kL_1707u1711(ptr %0) unnamed_addr {
  call void @__bennett_gate(i32 1, ptr %0, i64 0)
  ret void
}

declare void @__bennett_gate(i32, ptr, i64) local_unnamed_addr

attributes #0 = { "frame-pointer"="all" }

!llvm.module.flags = !{!0, !1, !2, !3}

!0 = !{i32 2, !"Dwarf Version", i32 4}
!1 = !{i32 2, !"Debug Info Version", i32 3}
!2 = !{i32 1, !"stack-protector-guard", !""}
!3 = !{i32 1, !"override-stack-alignment", i32 0}
