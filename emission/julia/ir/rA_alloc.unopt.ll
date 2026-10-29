; ModuleID = 'rA_alloc'
source_filename = "rA_alloc"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128-ni:10:11:12:13"
target triple = "x86_64-unknown-linux-gnu"

@"+Core.Ptr#601" = private unnamed_addr constant ptr @"+Core.Ptr#601.jit", !julia.constgv !0
@jlplt___bennett_qalloc_604_got = private unnamed_addr constant ptr @jlplt___bennett_qalloc_604_got.jit #0

@"+Core.Ptr#601.jit" = private alias ptr, inttoptr (i64 127079415345856 to ptr)
@jlplt___bennett_qalloc_604_got.jit = private alias ptr, inttoptr (i64 127079701373200 to ptr)

; Function Signature: rA_alloc(UInt64)
define swiftcc ptr @julia_rA_alloc_599(ptr nonnull swiftself "gcstack" %pgcstack_arg, i64 zeroext %"n::UInt64") #1 !dbg !5 {
top:
  %current_task = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152
  %ptls_field = getelementptr inbounds i8, ptr %current_task, i32 168
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !15
  %0 = getelementptr inbounds i8, ptr %ptls_load, i32 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !19, !invariant.load !0
  fence syncscope("singlethread") seq_cst
  call void @julia.safepoint(ptr %safepoint)
  fence syncscope("singlethread") seq_cst
    #dbg_value(i64 %"n::UInt64", !14, !DIExpression(), !21)
  %__bennett_qalloc = load atomic ptr, ptr @jlplt___bennett_qalloc_604_got unordered, align 8, !dbg !21
  %1 = call ptr %__bennett_qalloc(i64 0, i64 %"n::UInt64"), !dbg !21
  ret ptr %1, !dbg !21
}

; Function Attrs: noinline optnone
define nonnull ptr addrspace(10) @jfptr_rA_alloc_600(ptr addrspace(10) %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") #2 {
top:
  %pgcstack = call ptr @julia.get_pgcstack()
  %0 = load ptr addrspace(10), ptr %"args::Any[]", align 8, !tbaa !19, !invariant.load !0, !alias.scope !22, !noalias !25, !nonnull !0, !dereferenceable !30, !align !30
  %.unbox = load i64, ptr addrspace(10) %0, align 8, !tbaa !31, !alias.scope !35, !noalias !36
  %1 = call swiftcc ptr @julia_rA_alloc_599(ptr nonnull swiftself "gcstack" %pgcstack, i64 zeroext %.unbox)
  %"+Core.Ptr#601" = load ptr, ptr @"+Core.Ptr#601", align 8, !tbaa !19, !invariant.load !0, !alias.scope !22, !noalias !25, !nonnull !0, !dereferenceable !37, !align !38
  %Ptr = ptrtoint ptr %"+Core.Ptr#601" to i64
  %2 = inttoptr i64 %Ptr to ptr
  %current_task = getelementptr inbounds i8, ptr %pgcstack, i32 -152
  %3 = addrspacecast ptr %2 to ptr addrspace(10)
  %"box::Ptr" = call noalias nonnull align 8 dereferenceable(8) ptr addrspace(10) @julia.gc_alloc_obj(ptr %current_task, i64 8, ptr addrspace(10) %3) #5
  %4 = addrspacecast ptr addrspace(10) %"box::Ptr" to ptr addrspace(11)
  store ptr %1, ptr addrspace(11) %4, align 8, !tbaa !31, !alias.scope !35, !noalias !36
  ret ptr addrspace(10) %"box::Ptr"
}

declare ptr @julia.get_pgcstack()

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr addrspace(10) @julia.gc_alloc_obj(ptr, i64, ptr addrspace(10)) #3

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) #4

attributes #0 = { "julia.fname"="__bennett_qalloc" "julia.libname"="/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/libbennett_stub.so" }
attributes #1 = { "frame-pointer"="all" "julia.fsig"="rA_alloc(UInt64)" "probe-stack"="inline-asm" }
attributes #2 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #3 = { nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #4 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #5 = { nounwind willreturn allockind("alloc,uninitialized") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }

!llvm.module.flags = !{!1, !2}
!llvm.dbg.cu = !{!3}

!0 = !{}
!1 = !{i32 2, !"Dwarf Version", i32 4}
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !4, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!4 = !DIFile(filename: "julia", directory: ".")
!5 = distinct !DISubprogram(name: "rA_alloc", linkageName: "julia_rA_alloc_599", scope: null, file: !6, line: 6, type: !7, scopeLine: 6, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3, retainedNodes: !12)
!6 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!7 = !DISubroutineType(types: !8)
!8 = !{!9, !10, !11}
!9 = !DIBasicType(name: "Ptr", size: 64, encoding: DW_ATE_unsigned)
!10 = !DICompositeType(tag: DW_TAG_structure_type, name: "#rA_alloc", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079338399248")
!11 = !DIBasicType(name: "UInt64", size: 64, encoding: DW_ATE_unsigned)
!12 = !{!13, !14}
!13 = !DILocalVariable(name: "#self#", arg: 1, scope: !5, file: !6, line: 6, type: !10)
!14 = !DILocalVariable(name: "n", arg: 2, scope: !5, file: !6, line: 6, type: !11)
!15 = !{!16, !16, i64 0}
!16 = !{!"jtbaa_gcframe", !17, i64 0}
!17 = !{!"jtbaa", !18, i64 0}
!18 = !{!"jtbaa"}
!19 = !{!20, !20, i64 0, i64 1}
!20 = !{!"jtbaa_const", !17, i64 0}
!21 = !DILocation(line: 6, scope: !5)
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
!37 = !{i64 56}
!38 = !{i64 16}
