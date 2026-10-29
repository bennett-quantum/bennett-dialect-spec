; ModuleID = 'rE_gate'
source_filename = "rE_gate"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128-ni:10:11:12:13"
target triple = "x86_64-unknown-linux-gnu"

@jl_nothing = external constant ptr
@jl_undefref_exception = external constant ptr

; Function Signature: rE_gate(Ptr{Nothing}, Ptr{Nothing}, UInt64)
define swiftcc void @julia_rE_gate_883(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"p::Ptr", ptr %"h::Ptr", i64 zeroext %"i::UInt64") #0 !dbg !4 {
top:
  %current_task = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152
  %ptls_field = getelementptr inbounds i8, ptr %current_task, i32 168
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !18
  %0 = getelementptr inbounds i8, ptr %ptls_load, i32 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !22, !invariant.load !9
  fence syncscope("singlethread") seq_cst
  call void @julia.safepoint(ptr %safepoint)
  fence syncscope("singlethread") seq_cst
    #dbg_value(ptr %"p::Ptr", !15, !DIExpression(), !24)
    #dbg_value(ptr %"h::Ptr", !16, !DIExpression(), !24)
    #dbg_value(i64 %"i::UInt64", !17, !DIExpression(), !24)
  %jl_undefref_exception = load ptr, ptr @jl_undefref_exception, align 8, !dbg !24, !tbaa !22, !invariant.load !9, !alias.scope !25, !noalias !28, !nonnull !9
  %1 = icmp ne ptr %"p::Ptr", null, !dbg !24
  br i1 %1, label %pass, label %fail, !dbg !24

fail:                                             ; preds = %top
  %2 = addrspacecast ptr %jl_undefref_exception to ptr addrspace(12), !dbg !24
  call void @ijl_throw(ptr addrspace(12) %2), !dbg !24
  unreachable, !dbg !24

pass:                                             ; preds = %top
  call void %"p::Ptr"(i32 1, ptr %"h::Ptr", i64 %"i::UInt64"), !dbg !24
  ret void, !dbg !24
}

; Function Attrs: noinline optnone
define nonnull ptr addrspace(10) @jfptr_rE_gate_884(ptr addrspace(10) %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") #1 {
top:
  %pgcstack = call ptr @julia.get_pgcstack()
  %0 = load ptr addrspace(10), ptr %"args::Any[]", align 8, !tbaa !22, !invariant.load !9, !alias.scope !25, !noalias !28, !nonnull !9, !dereferenceable !33, !align !33
  %1 = getelementptr inbounds i8, ptr %"args::Any[]", i32 8
  %2 = load ptr addrspace(10), ptr %1, align 8, !tbaa !22, !invariant.load !9, !alias.scope !25, !noalias !28, !nonnull !9, !dereferenceable !33, !align !33
  %3 = getelementptr inbounds i8, ptr %"args::Any[]", i32 16
  %4 = load ptr addrspace(10), ptr %3, align 8, !tbaa !22, !invariant.load !9, !alias.scope !25, !noalias !28, !nonnull !9, !dereferenceable !33, !align !33
  %.unbox = load ptr, ptr addrspace(10) %0, align 8, !tbaa !34, !alias.scope !38, !noalias !39
  %.unbox1 = load ptr, ptr addrspace(10) %2, align 8, !tbaa !34, !alias.scope !38, !noalias !39
  %.unbox2 = load i64, ptr addrspace(10) %4, align 8, !tbaa !34, !alias.scope !38, !noalias !39
  call swiftcc void @julia_rE_gate_883(ptr nonnull swiftself "gcstack" %pgcstack, ptr %.unbox, ptr %.unbox1, i64 zeroext %.unbox2)
  %jl_nothing = load ptr, ptr @jl_nothing, align 8, !tbaa !22, !invariant.load !9, !alias.scope !25, !noalias !28, !nonnull !9
  %5 = addrspacecast ptr %jl_nothing to ptr addrspace(10)
  ret ptr addrspace(10) %5
}

declare ptr @julia.get_pgcstack()

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) #2

; Function Attrs: noreturn
declare void @ijl_throw(ptr addrspace(12)) #3

attributes #0 = { "frame-pointer"="all" "julia.fsig"="rE_gate(Ptr{Nothing}, Ptr{Nothing}, UInt64)" "probe-stack"="inline-asm" }
attributes #1 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #2 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #3 = { noreturn }

!llvm.module.flags = !{!0, !1}
!llvm.dbg.cu = !{!2}

!0 = !{i32 2, !"Dwarf Version", i32 4}
!1 = !{i32 2, !"Debug Info Version", i32 3}
!2 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !3, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!3 = !DIFile(filename: "julia", directory: ".")
!4 = distinct !DISubprogram(name: "rE_gate", linkageName: "julia_rE_gate_883", scope: null, file: !5, line: 72, type: !6, scopeLine: 72, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !13)
!5 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!6 = !DISubroutineType(types: !7)
!7 = !{!8, !10, !11, !11, !12}
!8 = !DICompositeType(tag: DW_TAG_structure_type, name: "Nothing", align: 8, elements: !9, runtimeLang: DW_LANG_Julia, identifier: "127079415932560")
!9 = !{}
!10 = !DICompositeType(tag: DW_TAG_structure_type, name: "#rE_gate", align: 8, elements: !9, runtimeLang: DW_LANG_Julia, identifier: "127079338219280")
!11 = !DIBasicType(name: "Ptr", size: 64, encoding: DW_ATE_unsigned)
!12 = !DIBasicType(name: "UInt64", size: 64, encoding: DW_ATE_unsigned)
!13 = !{!14, !15, !16, !17}
!14 = !DILocalVariable(name: "#self#", arg: 1, scope: !4, file: !5, line: 72, type: !10)
!15 = !DILocalVariable(name: "p", arg: 2, scope: !4, file: !5, line: 72, type: !11)
!16 = !DILocalVariable(name: "h", arg: 3, scope: !4, file: !5, line: 72, type: !11)
!17 = !DILocalVariable(name: "i", arg: 4, scope: !4, file: !5, line: 72, type: !12)
!18 = !{!19, !19, i64 0}
!19 = !{!"jtbaa_gcframe", !20, i64 0}
!20 = !{!"jtbaa", !21, i64 0}
!21 = !{!"jtbaa"}
!22 = !{!23, !23, i64 0, i64 1}
!23 = !{!"jtbaa_const", !20, i64 0}
!24 = !DILocation(line: 72, scope: !4)
!25 = !{!26}
!26 = !{!"jnoalias_const", !27}
!27 = !{!"jnoalias"}
!28 = !{!29, !30, !31, !32}
!29 = !{!"jnoalias_gcframe", !27}
!30 = !{!"jnoalias_stack", !27}
!31 = !{!"jnoalias_data", !27}
!32 = !{!"jnoalias_typemd", !27}
!33 = !{i64 8}
!34 = !{!35, !35, i64 0}
!35 = !{!"jtbaa_immut", !36, i64 0}
!36 = !{!"jtbaa_value", !37, i64 0}
!37 = !{!"jtbaa_data", !20, i64 0}
!38 = !{!31}
!39 = !{!29, !30, !32, !26}
