; ModuleID = 'rD_alloc'
source_filename = "rD_alloc"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@"+Core.Ptr#825" = private unnamed_addr constant ptr @"+Core.Ptr#825.jit", !julia.constgv !0

@"+Core.Ptr#825.jit" = private alias ptr, inttoptr (i64 127079415345856 to ptr)

; Function Signature: rD_alloc(UInt64)
define swiftcc ptr @julia_rD_alloc_823(ptr nonnull swiftself "gcstack" %pgcstack_arg, i64 zeroext %"n::UInt64") local_unnamed_addr #0 !dbg !7 {
top:
  %ptls_field = getelementptr inbounds nuw i8, ptr %pgcstack_arg, i64 16
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !17
  %0 = getelementptr inbounds nuw i8, ptr %ptls_load, i64 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !21, !invariant.load !0
  fence syncscope("singlethread") seq_cst
  %1 = load volatile i64, ptr %safepoint, align 8
  fence syncscope("singlethread") seq_cst
    #dbg_value(i64 %"n::UInt64", !16, !DIExpression(), !23)
  %2 = call fastcc ptr @julia_rD_alloc_823u828(i64 %"n::UInt64"), !dbg !23
  ret ptr %2, !dbg !23
}

; Function Attrs: noinline optnone
define nonnull ptr @jfptr_rD_alloc_824(ptr %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") local_unnamed_addr #1 {
top:
  %thread_ptr = call ptr asm "movq %fs:0, $0", "=r"()
  %tls_ppgcstack = getelementptr inbounds i8, ptr %thread_ptr, i64 -8
  %tls_pgcstack = load ptr, ptr %tls_ppgcstack, align 8
  %0 = load ptr, ptr %"args::Any[]", align 8, !tbaa !21, !invariant.load !0, !alias.scope !24, !noalias !27, !nonnull !0, !dereferenceable !32, !align !32
  %.unbox = load i64, ptr %0, align 8, !tbaa !33, !alias.scope !37, !noalias !38
  %1 = call swiftcc ptr @julia_rD_alloc_823(ptr nonnull swiftself "gcstack" %tls_pgcstack, i64 zeroext %.unbox)
  %"+Core.Ptr#825" = load ptr, ptr @"+Core.Ptr#825", align 8, !tbaa !21, !invariant.load !0, !alias.scope !24, !noalias !27, !nonnull !0, !dereferenceable !39, !align !40
  %Ptr = ptrtoint ptr %"+Core.Ptr#825" to i64
  %2 = inttoptr i64 %Ptr to ptr
  %current_task = getelementptr inbounds i8, ptr %tls_pgcstack, i32 -152
  call void @llvm.assume(i1 true) [ "align"(ptr %2, i64 16) ]
  %ptls_field = getelementptr inbounds i8, ptr %current_task, i32 168
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !17
  %3 = ptrtoint ptr %2 to i64
  %"box::Ptr" = call noalias nonnull align 8 dereferenceable(8) ptr @ijl_gc_small_alloc(ptr %ptls_load, i32 360, i32 16, i64 %3) #5
  %"box::Ptr.tag_addr" = getelementptr inbounds ptr, ptr %"box::Ptr", i64 -1
  store atomic ptr %2, ptr %"box::Ptr.tag_addr" unordered, align 8, !tbaa !41
  store ptr %1, ptr %"box::Ptr", align 8, !tbaa !33, !alias.scope !37, !noalias !38
  ret ptr %"box::Ptr"
}

; Function Attrs: mustprogress nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @julia.gc_alloc_obj(ptr, i64, ptr) local_unnamed_addr #2

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) local_unnamed_addr #3

define internal fastcc ptr @julia_rD_alloc_823u828(i64 %0) unnamed_addr {
  %r = call ptr @__bennett_qalloc(i64 0, i64 %0)
  ret ptr %r
}

declare ptr @__bennett_qalloc(i64, i64) local_unnamed_addr

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #4

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #4

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_small_alloc(ptr, i32, i32, i64) #5

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @ijl_gc_queue_root(ptr) #3

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_big_alloc(ptr, i64, i64) #6

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_alloc_typed(ptr, i64, i64) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: write)
declare void @llvm.assume(i1 noundef) #7

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @julia.gc_alloc_bytes(ptr, i64, i64) #6

attributes #0 = { "frame-pointer"="all" "julia.fsig"="rD_alloc(UInt64)" "probe-stack"="inline-asm" }
attributes #1 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #2 = { mustprogress nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #3 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #4 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #6 = { nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: write) }

!llvm.module.flags = !{!1, !2, !3, !4}
!llvm.dbg.cu = !{!5}

!0 = !{}
!1 = !{i32 2, !"Dwarf Version", i32 4}
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = !{i32 1, !"stack-protector-guard", !""}
!4 = !{i32 1, !"override-stack-alignment", i32 0}
!5 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !6, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!6 = !DIFile(filename: "julia", directory: ".")
!7 = distinct !DISubprogram(name: "rD_alloc", linkageName: "julia_rD_alloc_823", scope: null, file: !8, line: 30, type: !9, scopeLine: 30, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5, retainedNodes: !14)
!8 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!9 = !DISubroutineType(types: !10)
!10 = !{!11, !12, !13}
!11 = !DIBasicType(name: "Ptr", size: 64, encoding: DW_ATE_unsigned)
!12 = !DICompositeType(tag: DW_TAG_structure_type, name: "#rD_alloc", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079338213968")
!13 = !DIBasicType(name: "UInt64", size: 64, encoding: DW_ATE_unsigned)
!14 = !{!15, !16}
!15 = !DILocalVariable(name: "#self#", arg: 1, scope: !7, file: !8, line: 30, type: !12)
!16 = !DILocalVariable(name: "n", arg: 2, scope: !7, file: !8, line: 30, type: !13)
!17 = !{!18, !18, i64 0}
!18 = !{!"jtbaa_gcframe", !19, i64 0}
!19 = !{!"jtbaa", !20, i64 0}
!20 = !{!"jtbaa"}
!21 = !{!22, !22, i64 0}
!22 = !{!"jtbaa_const", !19, i64 0}
!23 = !DILocation(line: 30, scope: !7)
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
!39 = !{i64 56}
!40 = !{i64 16}
!41 = !{!42, !42, i64 0}
!42 = !{!"jtbaa_tag", !36, i64 0}
