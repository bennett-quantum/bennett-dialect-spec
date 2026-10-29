; ModuleID = 'body'
source_filename = "body"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@jl_nothing = external local_unnamed_addr constant ptr

; Function Signature: body(Ptr{Nothing})
define swiftcc void @julia_body_492(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"p::Ptr") local_unnamed_addr #0 !dbg !6 {
top:
  %ptls_field = getelementptr inbounds nuw i8, ptr %pgcstack_arg, i64 16
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !17
  %0 = getelementptr inbounds nuw i8, ptr %ptls_load, i64 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !21, !invariant.load !11
  fence syncscope("singlethread") seq_cst
  %1 = load volatile i64, ptr %safepoint, align 8
  fence syncscope("singlethread") seq_cst
    #dbg_value(ptr %"p::Ptr", !16, !DIExpression(), !23)
  %pointerref.sroa.0.0.copyload = load ptr, ptr %"p::Ptr", align 1, !dbg !24, !tbaa !30, !alias.scope !31, !noalias !35
  %pointerref.sroa.2.0..sroa_idx = getelementptr inbounds nuw i8, ptr %"p::Ptr", i64 8, !dbg !24
  %pointerref.sroa.2.0.copyload = load i64, ptr %pointerref.sroa.2.0..sroa_idx, align 1, !dbg !24, !tbaa !30, !alias.scope !31, !noalias !35
  call fastcc void @julia_body_492u496(ptr %pointerref.sroa.0.0.copyload, i64 %pointerref.sroa.2.0.copyload), !dbg !39
  ret void, !dbg !42
}

; Function Attrs: noinline optnone
define nonnull ptr @jfptr_body_493(ptr %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") local_unnamed_addr #1 {
top:
  %thread_ptr = call ptr asm "movq %fs:0, $0", "=r"()
  %tls_ppgcstack = getelementptr inbounds i8, ptr %thread_ptr, i64 -8
  %tls_pgcstack = load ptr, ptr %tls_ppgcstack, align 8
  %0 = load ptr, ptr %"args::Any[]", align 8, !tbaa !21, !invariant.load !11, !alias.scope !43, !noalias !44, !nonnull !11, !dereferenceable !45, !align !45
  %.unbox = load ptr, ptr %0, align 8, !tbaa !46, !alias.scope !50, !noalias !51
  call swiftcc void @julia_body_492(ptr nonnull swiftself "gcstack" %tls_pgcstack, ptr %.unbox)
  %jl_nothing = load ptr, ptr @jl_nothing, align 8, !tbaa !21, !invariant.load !11, !alias.scope !43, !noalias !44, !nonnull !11
  ret ptr %jl_nothing
}

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) local_unnamed_addr #2

define internal fastcc void @julia_body_492u496(ptr %0, i64 %1) unnamed_addr {
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

attributes #0 = { "frame-pointer"="all" "julia.fsig"="body(Ptr{Nothing})" "probe-stack"="inline-asm" }
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
!6 = distinct !DISubprogram(name: "body", linkageName: "julia_body_492", scope: null, file: !7, line: 76, type: !8, scopeLine: 76, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4, retainedNodes: !14)
!7 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!8 = !DISubroutineType(types: !9)
!9 = !{!10, !12, !13}
!10 = !DICompositeType(tag: DW_TAG_structure_type, name: "Nothing", align: 8, elements: !11, runtimeLang: DW_LANG_Julia, identifier: "127079415932560")
!11 = !{}
!12 = !DICompositeType(tag: DW_TAG_structure_type, name: "#body", align: 8, elements: !11, runtimeLang: DW_LANG_Julia, identifier: "127079338221712")
!13 = !DIBasicType(name: "Ptr", size: 64, encoding: DW_ATE_unsigned)
!14 = !{!15, !16}
!15 = !DILocalVariable(name: "#self#", arg: 1, scope: !6, file: !7, line: 76, type: !12)
!16 = !DILocalVariable(name: "p", arg: 2, scope: !6, file: !7, line: 76, type: !13)
!17 = !{!18, !18, i64 0}
!18 = !{!"jtbaa_gcframe", !19, i64 0}
!19 = !{!"jtbaa", !20, i64 0}
!20 = !{!"jtbaa"}
!21 = !{!22, !22, i64 0}
!22 = !{!"jtbaa_const", !19, i64 0}
!23 = !DILocation(line: 76, scope: !6)
!24 = !DILocation(line: 151, scope: !25, inlinedAt: !28)
!25 = distinct !DISubprogram(name: "unsafe_load;", linkageName: "unsafe_load", scope: !26, file: !26, type: !27, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!26 = !DIFile(filename: "pointer.jl", directory: ".")
!27 = !DISubroutineType(types: !11)
!28 = !DILocation(line: 151, scope: !25, inlinedAt: !29)
!29 = !DILocation(line: 77, scope: !6)
!30 = !{!19, !19, i64 0}
!31 = !{!32, !34}
!32 = !{!"jnoalias_data", !33}
!33 = !{!"jnoalias"}
!34 = !{!"jnoalias_stack", !33}
!35 = !{!36, !37, !38}
!36 = !{!"jnoalias_gcframe", !33}
!37 = !{!"jnoalias_typemd", !33}
!38 = !{!"jnoalias_const", !33}
!39 = !DILocation(line: 35, scope: !40, inlinedAt: !41)
!40 = distinct !DISubprogram(name: "rD_gate;", linkageName: "rD_gate", scope: !7, file: !7, type: !27, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!41 = !DILocation(line: 78, scope: !6)
!42 = !DILocation(line: 79, scope: !6)
!43 = !{!38}
!44 = !{!36, !34, !32, !37}
!45 = !{i64 8}
!46 = !{!47, !47, i64 0}
!47 = !{!"jtbaa_immut", !48, i64 0}
!48 = !{!"jtbaa_value", !49, i64 0}
!49 = !{!"jtbaa_data", !19, i64 0}
!50 = !{!32}
!51 = !{!36, !34, !37, !38}
