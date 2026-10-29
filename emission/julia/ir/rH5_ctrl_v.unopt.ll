; ModuleID = 'rH5_ctrl_v'
source_filename = "rH5_ctrl_v"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128-ni:10:11:12:13"
target triple = "x86_64-unknown-linux-gnu"

@jl_nothing = external constant ptr
@"jl_global#991" = private unnamed_addr constant ptr @"jl_global#991.jit", !julia.constgv !0
@"jl_global#992" = private unnamed_addr constant ptr @"jl_global#992.jit", !julia.constgv !0

@"jl_global#992.jit" = private alias ptr, inttoptr (i64 127079338396112 to ptr)
@"jl_global#991.jit" = private alias ptr, inttoptr (i64 127079338459152 to ptr)

; Function Signature: rH5_ctrl_v(Ptr{Nothing})
define swiftcc void @julia_rH5_ctrl_v_989(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"h::Ptr") #0 !dbg !7 {
top:
  %current_task = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152
  %ptls_field = getelementptr inbounds i8, ptr %current_task, i32 168
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !17
  %0 = getelementptr inbounds i8, ptr %ptls_load, i32 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !21, !invariant.load !0
  fence syncscope("singlethread") seq_cst
  call void @julia.safepoint(ptr %safepoint)
  fence syncscope("singlethread") seq_cst
    #dbg_value(ptr %"h::Ptr", !16, !DIExpression(), !23)
  %"jl_global#991" = load ptr, ptr @"jl_global#991", align 8, !dbg !23, !tbaa !21, !invariant.load !0, !alias.scope !24, !noalias !27, !nonnull !0
  %1 = addrspacecast ptr %"jl_global#991" to ptr addrspace(10), !dbg !23
  %"jl_global#992" = load ptr, ptr @"jl_global#992", align 8, !dbg !23, !tbaa !21, !invariant.load !0, !alias.scope !24, !noalias !27, !nonnull !0
  %2 = addrspacecast ptr %"jl_global#992" to ptr addrspace(10), !dbg !23
  call void @julia_rH5_ctrl_v_989u993(ptr %"h::Ptr"), !dbg !23
  ret void, !dbg !23
}

; Function Attrs: noinline optnone
define nonnull ptr addrspace(10) @jfptr_rH5_ctrl_v_990(ptr addrspace(10) %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") #1 {
top:
  %pgcstack = call ptr @julia.get_pgcstack()
  %0 = load ptr addrspace(10), ptr %"args::Any[]", align 8, !tbaa !21, !invariant.load !0, !alias.scope !24, !noalias !27, !nonnull !0, !dereferenceable !32, !align !32
  %.unbox = load ptr, ptr addrspace(10) %0, align 8, !tbaa !33, !alias.scope !37, !noalias !38
  call swiftcc void @julia_rH5_ctrl_v_989(ptr nonnull swiftself "gcstack" %pgcstack, ptr %.unbox)
  %jl_nothing = load ptr, ptr @jl_nothing, align 8, !tbaa !21, !invariant.load !0, !alias.scope !24, !noalias !27, !nonnull !0
  %1 = addrspacecast ptr %jl_nothing to ptr addrspace(10)
  ret ptr addrspace(10) %1
}

declare ptr @julia.get_pgcstack()

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) #2

define internal void @julia_rH5_ctrl_v_989u993(ptr %0) {
  call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr %0, i64 0, ptr null, i64 8, i32 1, double 2.500000e+00, ptr %0)
  ret void
}

declare void @__bennett_ctrl_v(ptr, i64, ptr, i64, ...)

attributes #0 = { "frame-pointer"="all" "julia.fsig"="rH5_ctrl_v(Ptr{Nothing})" "probe-stack"="inline-asm" }
attributes #1 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #2 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }

!llvm.module.flags = !{!1, !2, !3, !4}
!llvm.dbg.cu = !{!5}

!0 = !{}
!1 = !{i32 2, !"Dwarf Version", i32 4}
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = !{i32 1, !"stack-protector-guard", !""}
!4 = !{i32 1, !"override-stack-alignment", i32 0}
!5 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !6, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!6 = !DIFile(filename: "julia", directory: ".")
!7 = distinct !DISubprogram(name: "rH5_ctrl_v", linkageName: "julia_rH5_ctrl_v_989", scope: null, file: !8, line: 113, type: !9, scopeLine: 113, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5, retainedNodes: !14)
!8 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!9 = !DISubroutineType(types: !10)
!10 = !{!11, !12, !13}
!11 = !DICompositeType(tag: DW_TAG_structure_type, name: "Nothing", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079415932560")
!12 = !DICompositeType(tag: DW_TAG_structure_type, name: "#rH5_ctrl_v", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079337968464")
!13 = !DIBasicType(name: "Ptr", size: 64, encoding: DW_ATE_unsigned)
!14 = !{!15, !16}
!15 = !DILocalVariable(name: "#self#", arg: 1, scope: !7, file: !8, line: 113, type: !12)
!16 = !DILocalVariable(name: "h", arg: 2, scope: !7, file: !8, line: 113, type: !13)
!17 = !{!18, !18, i64 0}
!18 = !{!"jtbaa_gcframe", !19, i64 0}
!19 = !{!"jtbaa", !20, i64 0}
!20 = !{!"jtbaa"}
!21 = !{!22, !22, i64 0, i64 1}
!22 = !{!"jtbaa_const", !19, i64 0}
!23 = !DILocation(line: 113, scope: !7)
!24 = !{!25}
!25 = !{!"jnoalias_const", !26}
!26 = !{!"jnoalias"}
!27 = !{!28, !29, !30, !31}
!28 = !{!"jnoalias_gcframe", !26}
!29 = !{!"jnoalias_stack", !26}
!30 = !{!"jnoalias_data", !26}
!31 = !{!"jnoalias_typemd", !26}
!32 = !{i64 8}
!33 = !{!34, !34, i64 0}
!34 = !{!"jtbaa_immut", !35, i64 0}
!35 = !{!"jtbaa_value", !36, i64 0}
!36 = !{!"jtbaa_data", !19, i64 0}
!37 = !{!30}
!38 = !{!28, !29, !31, !25}
