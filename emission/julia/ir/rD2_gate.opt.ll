; ModuleID = 'rD2_gate'
source_filename = "rD2_gate"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@jl_nothing = external local_unnamed_addr constant ptr

; Function Signature: rD2_gate(Ptr{Nothing}, UInt64)
define swiftcc void @julia_rD2_gate_790(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"h::Ptr", i64 zeroext %"i::UInt64") local_unnamed_addr #0 !dbg !6 {
top:
  %ptls_field = getelementptr inbounds nuw i8, ptr %pgcstack_arg, i64 16
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !19
  %0 = getelementptr inbounds nuw i8, ptr %ptls_load, i64 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !23, !invariant.load !11
  fence syncscope("singlethread") seq_cst
  %1 = load volatile i64, ptr %safepoint, align 8
  fence syncscope("singlethread") seq_cst
    #dbg_value(ptr %"h::Ptr", !17, !DIExpression(), !25)
    #dbg_value(i64 %"i::UInt64", !18, !DIExpression(), !25)
  call fastcc void @julia_rD2_gate_790u794(ptr %"h::Ptr", i64 %"i::UInt64"), !dbg !25
  ret void, !dbg !25
}

; Function Attrs: noinline optnone
define nonnull ptr @jfptr_rD2_gate_791(ptr %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") local_unnamed_addr #1 {
top:
  %thread_ptr = call ptr asm "movq %fs:0, $0", "=r"()
  %tls_ppgcstack = getelementptr inbounds i8, ptr %thread_ptr, i64 -8
  %tls_pgcstack = load ptr, ptr %tls_ppgcstack, align 8
  %0 = load ptr, ptr %"args::Any[]", align 8, !tbaa !23, !invariant.load !11, !alias.scope !26, !noalias !29, !nonnull !11, !dereferenceable !34, !align !34
  %1 = getelementptr inbounds i8, ptr %"args::Any[]", i32 8
  %2 = load ptr, ptr %1, align 8, !tbaa !23, !invariant.load !11, !alias.scope !26, !noalias !29, !nonnull !11, !dereferenceable !34, !align !34
  %.unbox = load ptr, ptr %0, align 8, !tbaa !35, !alias.scope !39, !noalias !40
  %.unbox1 = load i64, ptr %2, align 8, !tbaa !35, !alias.scope !39, !noalias !40
  call swiftcc void @julia_rD2_gate_790(ptr nonnull swiftself "gcstack" %tls_pgcstack, ptr %.unbox, i64 zeroext %.unbox1)
  %jl_nothing = load ptr, ptr @jl_nothing, align 8, !tbaa !23, !invariant.load !11, !alias.scope !26, !noalias !29, !nonnull !11
  ret ptr %jl_nothing
}

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) local_unnamed_addr #2

define internal fastcc void @julia_rD2_gate_790u794(ptr %0, i64 %1) unnamed_addr {
  call void @__bennett_gate(i32 1, ptr %0, i64 %1)
  ret void
}

declare void @__bennett_gate(i32, ptr, i64) local_unnamed_addr

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_small_alloc(ptr, i32, i32, i64) #3

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @ijl_gc_queue_root(ptr) #2

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_big_alloc(ptr, i64, i64) #4

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_alloc_typed(ptr, i64, i64) #4

attributes #0 = { "frame-pointer"="all" "julia.fsig"="rD2_gate(Ptr{Nothing}, UInt64)" "probe-stack"="inline-asm" }
attributes #1 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #2 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #3 = { nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #4 = { nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }

!llvm.module.flags = !{!0, !1, !2, !3}
!llvm.dbg.cu = !{!4}

!0 = !{i32 2, !"Dwarf Version", i32 4}
!1 = !{i32 2, !"Debug Info Version", i32 3}
!2 = !{i32 1, !"stack-protector-guard", !""}
!3 = !{i32 1, !"override-stack-alignment", i32 0}
!4 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !5, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!5 = !DIFile(filename: "julia", directory: ".")
!6 = distinct !DISubprogram(name: "rD2_gate", linkageName: "julia_rD2_gate_790", scope: null, file: !7, line: 56, type: !8, scopeLine: 56, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4, retainedNodes: !15)
!7 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!8 = !DISubroutineType(types: !9)
!9 = !{!10, !12, !13, !14}
!10 = !DICompositeType(tag: DW_TAG_structure_type, name: "Nothing", align: 8, elements: !11, runtimeLang: DW_LANG_Julia, identifier: "127079415932560")
!11 = !{}
!12 = !DICompositeType(tag: DW_TAG_structure_type, name: "#rD2_gate", align: 8, elements: !11, runtimeLang: DW_LANG_Julia, identifier: "127079338217552")
!13 = !DIBasicType(name: "Ptr", size: 64, encoding: DW_ATE_unsigned)
!14 = !DIBasicType(name: "UInt64", size: 64, encoding: DW_ATE_unsigned)
!15 = !{!16, !17, !18}
!16 = !DILocalVariable(name: "#self#", arg: 1, scope: !6, file: !7, line: 56, type: !12)
!17 = !DILocalVariable(name: "h", arg: 2, scope: !6, file: !7, line: 56, type: !13)
!18 = !DILocalVariable(name: "i", arg: 3, scope: !6, file: !7, line: 56, type: !14)
!19 = !{!20, !20, i64 0}
!20 = !{!"jtbaa_gcframe", !21, i64 0}
!21 = !{!"jtbaa", !22, i64 0}
!22 = !{!"jtbaa"}
!23 = !{!24, !24, i64 0}
!24 = !{!"jtbaa_const", !21, i64 0}
!25 = !DILocation(line: 56, scope: !6)
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
