; ModuleID = 'rA_rot'
source_filename = "rA_rot"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@jl_nothing = external local_unnamed_addr constant ptr
@jlplt___bennett_rot_658_got = external local_unnamed_addr global ptr #0

; Function Signature: rA_rot(Ptr{Nothing}, Float64)
define swiftcc void @julia_rA_rot_654(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"h::Ptr", double %"th::Float64") local_unnamed_addr #1 !dbg !4 {
top:
  %ptls_field = getelementptr inbounds nuw i8, ptr %pgcstack_arg, i64 16
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !17
  %0 = getelementptr inbounds nuw i8, ptr %ptls_load, i64 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !21, !invariant.load !9
  fence syncscope("singlethread") seq_cst
  %1 = load volatile i64, ptr %safepoint, align 8
  fence syncscope("singlethread") seq_cst
    #dbg_value(ptr %"h::Ptr", !15, !DIExpression(), !23)
    #dbg_value(double %"th::Float64", !16, !DIExpression(), !23)
  %__bennett_rot = load atomic ptr, ptr @jlplt___bennett_rot_658_got unordered, align 8, !dbg !23
  call void %__bennett_rot(i32 3, ptr %"h::Ptr", i64 1, double %"th::Float64"), !dbg !23
  ret void, !dbg !23
}

; Function Attrs: noinline optnone
define nonnull ptr @jfptr_rA_rot_655(ptr %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") local_unnamed_addr #2 {
top:
  %thread_ptr = call ptr asm "movq %fs:0, $0", "=r"()
  %tls_ppgcstack = getelementptr inbounds i8, ptr %thread_ptr, i64 -8
  %tls_pgcstack = load ptr, ptr %tls_ppgcstack, align 8
  %0 = load ptr, ptr %"args::Any[]", align 8, !tbaa !21, !invariant.load !9, !alias.scope !24, !noalias !27, !nonnull !9, !dereferenceable !32, !align !32
  %1 = getelementptr inbounds i8, ptr %"args::Any[]", i32 8
  %2 = load ptr, ptr %1, align 8, !tbaa !21, !invariant.load !9, !alias.scope !24, !noalias !27, !nonnull !9, !dereferenceable !32, !align !32
  %.unbox = load ptr, ptr %0, align 8, !tbaa !33, !alias.scope !37, !noalias !38
  %.unbox1 = load double, ptr %2, align 8, !tbaa !33, !alias.scope !37, !noalias !38
  call swiftcc void @julia_rA_rot_654(ptr nonnull swiftself "gcstack" %tls_pgcstack, ptr %.unbox, double %.unbox1)
  %jl_nothing = load ptr, ptr @jl_nothing, align 8, !tbaa !21, !invariant.load !9, !alias.scope !24, !noalias !27, !nonnull !9
  ret ptr %jl_nothing
}

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) local_unnamed_addr #3

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_small_alloc(ptr, i32, i32, i64) #4

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @ijl_gc_queue_root(ptr) #3

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_big_alloc(ptr, i64, i64) #5

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_alloc_typed(ptr, i64, i64) #5

attributes #0 = { "julia.fname"="__bennett_rot" "julia.libname"="/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/libbennett_stub.so" }
attributes #1 = { "frame-pointer"="all" "julia.fsig"="rA_rot(Ptr{Nothing}, Float64)" "probe-stack"="inline-asm" }
attributes #2 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #3 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #4 = { nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #5 = { nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }

!llvm.module.flags = !{!0, !1}
!llvm.dbg.cu = !{!2}

!0 = !{i32 2, !"Dwarf Version", i32 4}
!1 = !{i32 2, !"Debug Info Version", i32 3}
!2 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !3, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!3 = !DIFile(filename: "julia", directory: ".")
!4 = distinct !DISubprogram(name: "rA_rot", linkageName: "julia_rA_rot_654", scope: null, file: !5, line: 9, type: !6, scopeLine: 9, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !13)
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
!21 = !{!22, !22, i64 0}
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
