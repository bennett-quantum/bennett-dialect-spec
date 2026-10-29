; ModuleID = 'f'
source_filename = "f"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128-ni:10:11:12:13"
target triple = "x86_64-unknown-linux-gnu"

@jl_nothing = external constant ptr
@jlplt___bennett_gate_133_got = external global ptr #0

; Function Signature: f(Ptr{Nothing})
define swiftcc void @julia_f_129(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"h::Ptr") #1 !dbg !4 {
top:
  %current_task = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152
  %ptls_field = getelementptr inbounds i8, ptr %current_task, i32 168
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !15
  %0 = getelementptr inbounds i8, ptr %ptls_load, i32 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !19, !invariant.load !9
  fence syncscope("singlethread") seq_cst
  call void @julia.safepoint(ptr %safepoint)
  fence syncscope("singlethread") seq_cst
    #dbg_value(ptr %"h::Ptr", !14, !DIExpression(), !21)
  %__bennett_gate = load atomic ptr, ptr @jlplt___bennett_gate_133_got unordered, align 8, !dbg !21
  call void %__bennett_gate(i32 1, ptr %"h::Ptr", i64 0), !dbg !21
  ret void, !dbg !21
}

; Function Attrs: noinline optnone
define nonnull ptr addrspace(10) @jfptr_f_130(ptr addrspace(10) %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") #2 {
top:
  %pgcstack = call ptr @julia.get_pgcstack()
  %0 = load ptr addrspace(10), ptr %"args::Any[]", align 8, !tbaa !19, !invariant.load !9, !alias.scope !22, !noalias !25, !nonnull !9, !dereferenceable !30, !align !30
  %.unbox = load ptr, ptr addrspace(10) %0, align 8, !tbaa !31, !alias.scope !35, !noalias !36
  call swiftcc void @julia_f_129(ptr nonnull swiftself "gcstack" %pgcstack, ptr %.unbox)
  %jl_nothing = load ptr, ptr @jl_nothing, align 8, !tbaa !19, !invariant.load !9, !alias.scope !22, !noalias !25, !nonnull !9
  %1 = addrspacecast ptr %jl_nothing to ptr addrspace(10)
  ret ptr addrspace(10) %1
}

declare ptr @julia.get_pgcstack()

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) #3

attributes #0 = { "julia.fname"="__bennett_gate" "julia.libname"="libbennett_does_not_exist" }
attributes #1 = { "frame-pointer"="all" "julia.fsig"="f(Ptr{Nothing})" "probe-stack"="inline-asm" }
attributes #2 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #3 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }

!llvm.module.flags = !{!0, !1}
!llvm.dbg.cu = !{!2}

!0 = !{i32 2, !"Dwarf Version", i32 4}
!1 = !{i32 2, !"Debug Info Version", i32 3}
!2 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !3, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!3 = !DIFile(filename: "julia", directory: ".")
!4 = distinct !DISubprogram(name: "f", linkageName: "julia_f_129", scope: null, file: !5, line: 3, type: !6, scopeLine: 3, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !12)
!5 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/nolib.jl", directory: ".")
!6 = !DISubroutineType(types: !7)
!7 = !{!8, !10, !11}
!8 = !DICompositeType(tag: DW_TAG_structure_type, name: "Nothing", align: 8, elements: !9, runtimeLang: DW_LANG_Julia, identifier: "131697386579600")
!9 = !{}
!10 = !DICompositeType(tag: DW_TAG_structure_type, name: "#f", align: 8, elements: !9, runtimeLang: DW_LANG_Julia, identifier: "131697305710096")
!11 = !DIBasicType(name: "Ptr", size: 64, encoding: DW_ATE_unsigned)
!12 = !{!13, !14}
!13 = !DILocalVariable(name: "#self#", arg: 1, scope: !4, file: !5, line: 3, type: !10)
!14 = !DILocalVariable(name: "h", arg: 2, scope: !4, file: !5, line: 3, type: !11)
!15 = !{!16, !16, i64 0}
!16 = !{!"jtbaa_gcframe", !17, i64 0}
!17 = !{!"jtbaa", !18, i64 0}
!18 = !{!"jtbaa"}
!19 = !{!20, !20, i64 0, i64 1}
!20 = !{!"jtbaa_const", !17, i64 0}
!21 = !DILocation(line: 3, scope: !4)
!22 = !{!23}
!23 = !{!"jnoalias_const", !24}
!24 = !{!"jnoalias"}
!25 = !{!26, !27, !28, !29}
!26 = !{!"jnoalias_gcframe", !24}
!27 = !{!"jnoalias_stack", !24}
!28 = !{!"jnoalias_data", !24}
!29 = !{!"jnoalias_typemd", !24}
!30 = !{i64 8}
!31 = !{!32, !32, i64 0}
!32 = !{!"jtbaa_immut", !33, i64 0}
!33 = !{!"jtbaa_value", !34, i64 0}
!34 = !{!"jtbaa_data", !17, i64 0}
!35 = !{!28}
!36 = !{!26, !27, !29, !23}
