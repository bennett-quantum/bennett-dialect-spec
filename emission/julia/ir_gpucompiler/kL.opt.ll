; ModuleID = 'start'
source_filename = "start"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-linux-gnu"

;  @ /home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/gpucompiler.jl:19 within `kL`
define void @julia_kL_1712(ptr %"h::Ptr") local_unnamed_addr #0 {
top:
  call fastcc void @julia_kL_1712u1716(ptr %"h::Ptr")
  ret void
}

define internal fastcc void @julia_kL_1712u1716(ptr %0) unnamed_addr {
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
