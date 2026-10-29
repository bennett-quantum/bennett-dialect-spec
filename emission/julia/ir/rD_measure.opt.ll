; ModuleID = 'rD_measure'
source_filename = "rD_measure"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@jl_false = external local_unnamed_addr constant ptr
@jl_true = external local_unnamed_addr constant ptr

; Function Signature: rD_measure(Ptr{Nothing})
define swiftcc i8 @julia_rD_measure_856(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"h::Ptr") local_unnamed_addr #0 !dbg !6 {
top:
  %ptls_field = getelementptr inbounds nuw i8, ptr %pgcstack_arg, i64 16
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !17
  %0 = getelementptr inbounds nuw i8, ptr %ptls_load, i64 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !21, !invariant.load !12
  fence syncscope("singlethread") seq_cst
  %1 = load volatile i64, ptr %safepoint, align 8
  fence syncscope("singlethread") seq_cst
    #dbg_value(ptr %"h::Ptr", !16, !DIExpression(), !23)
  %2 = call i8 @julia_rD_measure_856u860(ptr %"h::Ptr"), !dbg !23
  ret i8 %2, !dbg !23
}

; Function Attrs: noinline optnone
define nonnull ptr @jfptr_rD_measure_857(ptr %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") local_unnamed_addr #1 {
top:
  %thread_ptr = call ptr asm "movq %fs:0, $0", "=r"()
  %tls_ppgcstack = getelementptr inbounds i8, ptr %thread_ptr, i64 -8
  %tls_pgcstack = load ptr, ptr %tls_ppgcstack, align 8
  %0 = load ptr, ptr %"args::Any[]", align 8, !tbaa !21, !invariant.load !12, !alias.scope !24, !noalias !27, !nonnull !12, !dereferenceable !32, !align !32
  %.unbox = load ptr, ptr %0, align 8, !tbaa !33, !alias.scope !37, !noalias !38
  %1 = call swiftcc i8 @julia_rD_measure_856(ptr nonnull swiftself "gcstack" %tls_pgcstack, ptr %.unbox)
  %2 = trunc i8 %1 to i1
  %jl_false = load ptr, ptr @jl_false, align 8, !tbaa !21, !invariant.load !12, !alias.scope !24, !noalias !27, !nonnull !12, !dereferenceable !39, !align !39
  %jl_true = load ptr, ptr @jl_true, align 8, !tbaa !21, !invariant.load !12, !alias.scope !24, !noalias !27, !nonnull !12, !dereferenceable !39, !align !39
  %bool = select i1 %2, ptr %jl_true, ptr %jl_false
  ret ptr %bool
}

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) local_unnamed_addr #2

define internal zeroext i1 @julia_rD_measure_856u860(ptr %0) unnamed_addr {
  %r = call zeroext i1 @__bennett_measure(ptr %0, i64 0)
  ret i1 %r
}

declare zeroext i1 @__bennett_measure(ptr, i64) local_unnamed_addr

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_small_alloc(ptr, i32, i32, i64) #3

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @ijl_gc_queue_root(ptr) #2

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_big_alloc(ptr, i64, i64) #4

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_alloc_typed(ptr, i64, i64) #4

attributes #0 = { "frame-pointer"="all" "julia.fsig"="rD_measure(Ptr{Nothing})" "probe-stack"="inline-asm" }
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
!6 = distinct !DISubprogram(name: "rD_measure", linkageName: "julia_rD_measure_856", scope: null, file: !7, line: 40, type: !8, scopeLine: 40, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4, retainedNodes: !14)
!7 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!8 = !DISubroutineType(types: !9)
!9 = !{!10, !11, !13}
!10 = !DIBasicType(name: "Bool", size: 8, encoding: DW_ATE_unsigned)
!11 = !DICompositeType(tag: DW_TAG_structure_type, name: "#rD_measure", align: 8, elements: !12, runtimeLang: DW_LANG_Julia, identifier: "127079338215504")
!12 = !{}
!13 = !DIBasicType(name: "Ptr", size: 64, encoding: DW_ATE_unsigned)
!14 = !{!15, !16}
!15 = !DILocalVariable(name: "#self#", arg: 1, scope: !6, file: !7, line: 40, type: !11)
!16 = !DILocalVariable(name: "h", arg: 2, scope: !6, file: !7, line: 40, type: !13)
!17 = !{!18, !18, i64 0}
!18 = !{!"jtbaa_gcframe", !19, i64 0}
!19 = !{!"jtbaa", !20, i64 0}
!20 = !{!"jtbaa"}
!21 = !{!22, !22, i64 0}
!22 = !{!"jtbaa_const", !19, i64 0}
!23 = !DILocation(line: 40, scope: !6)
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
!39 = !{i64 1}
