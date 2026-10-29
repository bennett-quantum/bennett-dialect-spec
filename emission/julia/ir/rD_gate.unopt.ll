; ModuleID = 'rD_gate'
source_filename = "rD_gate"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128-ni:10:11:12:13"
target triple = "x86_64-unknown-linux-gnu"

@jl_nothing = external constant ptr
@"jl_global#837" = private unnamed_addr constant ptr @"jl_global#837.jit", !julia.constgv !0
@"jl_global#838" = private unnamed_addr constant ptr @"jl_global#838.jit", !julia.constgv !0

@"jl_global#838.jit" = private alias ptr, inttoptr (i64 127079338396112 to ptr)
@"jl_global#837.jit" = private alias ptr, inttoptr (i64 127079338476416 to ptr)

; Function Signature: rD_gate(Ptr{Nothing}, UInt64)
define swiftcc void @julia_rD_gate_835(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"h::Ptr", i64 zeroext %"i::UInt64") #0 !dbg !7 {
top:
  %current_task = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152
  %ptls_field = getelementptr inbounds i8, ptr %current_task, i32 168
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !19
  %0 = getelementptr inbounds i8, ptr %ptls_load, i32 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !23, !invariant.load !0
  fence syncscope("singlethread") seq_cst
  call void @julia.safepoint(ptr %safepoint)
  fence syncscope("singlethread") seq_cst
    #dbg_value(ptr %"h::Ptr", !17, !DIExpression(), !25)
    #dbg_value(i64 %"i::UInt64", !18, !DIExpression(), !25)
  %"jl_global#837" = load ptr, ptr @"jl_global#837", align 8, !dbg !25, !tbaa !23, !invariant.load !0, !alias.scope !26, !noalias !29, !nonnull !0
  %1 = addrspacecast ptr %"jl_global#837" to ptr addrspace(10), !dbg !25
  %"jl_global#838" = load ptr, ptr @"jl_global#838", align 8, !dbg !25, !tbaa !23, !invariant.load !0, !alias.scope !26, !noalias !29, !nonnull !0
  %2 = addrspacecast ptr %"jl_global#838" to ptr addrspace(10), !dbg !25
  call void @julia_rD_gate_835u839(ptr %"h::Ptr", i64 %"i::UInt64"), !dbg !25
  ret void, !dbg !25
}

; Function Attrs: noinline optnone
define nonnull ptr addrspace(10) @jfptr_rD_gate_836(ptr addrspace(10) %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") #1 {
top:
  %pgcstack = call ptr @julia.get_pgcstack()
  %0 = load ptr addrspace(10), ptr %"args::Any[]", align 8, !tbaa !23, !invariant.load !0, !alias.scope !26, !noalias !29, !nonnull !0, !dereferenceable !34, !align !34
  %1 = getelementptr inbounds i8, ptr %"args::Any[]", i32 8
  %2 = load ptr addrspace(10), ptr %1, align 8, !tbaa !23, !invariant.load !0, !alias.scope !26, !noalias !29, !nonnull !0, !dereferenceable !34, !align !34
  %.unbox = load ptr, ptr addrspace(10) %0, align 8, !tbaa !35, !alias.scope !39, !noalias !40
  %.unbox1 = load i64, ptr addrspace(10) %2, align 8, !tbaa !35, !alias.scope !39, !noalias !40
  call swiftcc void @julia_rD_gate_835(ptr nonnull swiftself "gcstack" %pgcstack, ptr %.unbox, i64 zeroext %.unbox1)
  %jl_nothing = load ptr, ptr @jl_nothing, align 8, !tbaa !23, !invariant.load !0, !alias.scope !26, !noalias !29, !nonnull !0
  %3 = addrspacecast ptr %jl_nothing to ptr addrspace(10)
  ret ptr addrspace(10) %3
}

declare ptr @julia.get_pgcstack()

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) #2

define internal void @julia_rD_gate_835u839(ptr %0, i64 %1) {
  call void @__bennett_gate(i32 1, ptr %0, i64 %1)
  ret void
}

declare void @__bennett_gate(i32, ptr, i64)

attributes #0 = { "frame-pointer"="all" "julia.fsig"="rD_gate(Ptr{Nothing}, UInt64)" "probe-stack"="inline-asm" }
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
!7 = distinct !DISubprogram(name: "rD_gate", linkageName: "julia_rD_gate_835", scope: null, file: !8, line: 35, type: !9, scopeLine: 35, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5, retainedNodes: !15)
!8 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!9 = !DISubroutineType(types: !10)
!10 = !{!11, !12, !13, !14}
!11 = !DICompositeType(tag: DW_TAG_structure_type, name: "Nothing", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079415932560")
!12 = !DICompositeType(tag: DW_TAG_structure_type, name: "#rD_gate", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079338214736")
!13 = !DIBasicType(name: "Ptr", size: 64, encoding: DW_ATE_unsigned)
!14 = !DIBasicType(name: "UInt64", size: 64, encoding: DW_ATE_unsigned)
!15 = !{!16, !17, !18}
!16 = !DILocalVariable(name: "#self#", arg: 1, scope: !7, file: !8, line: 35, type: !12)
!17 = !DILocalVariable(name: "h", arg: 2, scope: !7, file: !8, line: 35, type: !13)
!18 = !DILocalVariable(name: "i", arg: 3, scope: !7, file: !8, line: 35, type: !14)
!19 = !{!20, !20, i64 0}
!20 = !{!"jtbaa_gcframe", !21, i64 0}
!21 = !{!"jtbaa", !22, i64 0}
!22 = !{!"jtbaa"}
!23 = !{!24, !24, i64 0, i64 1}
!24 = !{!"jtbaa_const", !21, i64 0}
!25 = !DILocation(line: 35, scope: !7)
!26 = !{!27}
!27 = !{!"jnoalias_const", !28}
!28 = !{!"jnoalias"}
!29 = !{!30, !31, !32, !33}
!30 = !{!"jnoalias_gcframe", !28}
!31 = !{!"jnoalias_stack", !28}
!32 = !{!"jnoalias_data", !28}
!33 = !{!"jnoalias_typemd", !28}
!34 = !{i64 8}
!35 = !{!36, !36, i64 0}
!36 = !{!"jtbaa_immut", !37, i64 0}
!37 = !{!"jtbaa_value", !38, i64 0}
!38 = !{!"jtbaa_data", !21, i64 0}
!39 = !{!32}
!40 = !{!30, !31, !33, !27}
