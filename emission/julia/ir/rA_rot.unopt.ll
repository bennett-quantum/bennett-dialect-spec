; ModuleID = 'rA_rot'
source_filename = "rA_rot"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128-ni:10:11:12:13"
target triple = "x86_64-unknown-linux-gnu"

@jl_nothing = external constant ptr
@jlplt___bennett_rot_653_got = external global ptr #0

; Function Signature: rA_rot(Ptr{Nothing}, Float64)
define swiftcc void @julia_rA_rot_649(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"h::Ptr", double %"th::Float64") #1 !dbg !4 {
top:
  %current_task = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152
  %ptls_field = getelementptr inbounds i8, ptr %current_task, i32 168
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !17
  %0 = getelementptr inbounds i8, ptr %ptls_load, i32 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !21, !invariant.load !9
  fence syncscope("singlethread") seq_cst
  call void @julia.safepoint(ptr %safepoint)
  fence syncscope("singlethread") seq_cst
    #dbg_value(ptr %"h::Ptr", !15, !DIExpression(), !23)
    #dbg_value(double %"th::Float64", !16, !DIExpression(), !23)
  %__bennett_rot = load atomic ptr, ptr @jlplt___bennett_rot_653_got unordered, align 8, !dbg !23
  call void %__bennett_rot(i32 3, ptr %"h::Ptr", i64 1, double %"th::Float64"), !dbg !23
  ret void, !dbg !23
}

; Function Attrs: noinline optnone
define nonnull ptr addrspace(10) @jfptr_rA_rot_650(ptr addrspace(10) %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") #2 {
top:
  %pgcstack = call ptr @julia.get_pgcstack()
  %0 = load ptr addrspace(10), ptr %"args::Any[]", align 8, !tbaa !21, !invariant.load !9, !alias.scope !24, !noalias !27, !nonnull !9, !dereferenceable !32, !align !32
  %1 = getelementptr inbounds i8, ptr %"args::Any[]", i32 8
  %2 = load ptr addrspace(10), ptr %1, align 8, !tbaa !21, !invariant.load !9, !alias.scope !24, !noalias !27, !nonnull !9, !dereferenceable !32, !align !32
  %.unbox = load ptr, ptr addrspace(10) %0, align 8, !tbaa !33, !alias.scope !37, !noalias !38
  %.unbox1 = load double, ptr addrspace(10) %2, align 8, !tbaa !33, !alias.scope !37, !noalias !38
  call swiftcc void @julia_rA_rot_649(ptr nonnull swiftself "gcstack" %pgcstack, ptr %.unbox, double %.unbox1)
  %jl_nothing = load ptr, ptr @jl_nothing, align 8, !tbaa !21, !invariant.load !9, !alias.scope !24, !noalias !27, !nonnull !9
  %3 = addrspacecast ptr %jl_nothing to ptr addrspace(10)
  ret ptr addrspace(10) %3
}

declare ptr @julia.get_pgcstack()

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) #3

attributes #0 = { "julia.fname"="__bennett_rot" "julia.libname"="/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/libbennett_stub.so" }
attributes #1 = { "frame-pointer"="all" "julia.fsig"="rA_rot(Ptr{Nothing}, Float64)" "probe-stack"="inline-asm" }
attributes #2 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #3 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }

!llvm.module.flags = !{!0, !1}
!llvm.dbg.cu = !{!2}

!0 = !{i32 2, !"Dwarf Version", i32 4}
!1 = !{i32 2, !"Debug Info Version", i32 3}
!2 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !3, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!3 = !DIFile(filename: "julia", directory: ".")
!4 = distinct !DISubprogram(name: "rA_rot", linkageName: "julia_rA_rot_649", scope: null, file: !5, line: 9, type: !6, scopeLine: 9, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !13)
!5 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!6 = !DISubroutineType(types: !7)
!7 = !{!8, !10, !11, !12}
!8 = !DICompositeType(tag: DW_TAG_structure_type, name: "Nothing", align: 8, elements: !9, runtimeLang: DW_LANG_Julia, identifier: "127079415932560")
!9 = !{}
!10 = !DICompositeType(tag: DW_TAG_structure_type, name: "#rA_rot", align: 8, elements: !9, runtimeLang: DW_LANG_Julia, identifier: "127079338401360")
!11 = !DIBasicType(name: "Ptr", size: 64, encoding: DW_ATE_unsigned)
!12 = !DIBasicType(name: "Float64", size: 64, encoding: DW_ATE_unsigned)
!13 = !{!14, !15, !16}
!14 = !DILocalVariable(name: "#self#", arg: 1, scope: !4, file: !5, line: 9, type: !10)
!15 = !DILocalVariable(name: "h", arg: 2, scope: !4, file: !5, line: 9, type: !11)
!16 = !DILocalVariable(name: "th", arg: 3, scope: !4, file: !5, line: 9, type: !12)
!17 = !{!18, !18, i64 0}
!18 = !{!"jtbaa_gcframe", !19, i64 0}
!19 = !{!"jtbaa", !20, i64 0}
!20 = !{!"jtbaa"}
!21 = !{!22, !22, i64 0, i64 1}
!22 = !{!"jtbaa_const", !19, i64 0}
!23 = !DILocation(line: 9, scope: !4)
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
