; ModuleID = 'rF_ctrl'
source_filename = "rF_ctrl"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@jl_nothing = external local_unnamed_addr constant ptr
@jlplt___bennett_ctrl_934_got = external local_unnamed_addr global ptr #0

; Function Signature: rF_ctrl(Ptr{Nothing}, Float64)
define swiftcc void @julia_rF_ctrl_930(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"h::Ptr", double %"theta::Float64") local_unnamed_addr #1 !dbg !4 {
top:
  %"new::RefValue" = alloca [3 x i64], align 16, !dbg !17
  %ptls_field = getelementptr inbounds nuw i8, ptr %pgcstack_arg, i64 16
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !26
  %0 = getelementptr inbounds nuw i8, ptr %ptls_load, i64 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !30, !invariant.load !9
  fence syncscope("singlethread") seq_cst
  %1 = load volatile i64, ptr %safepoint, align 8
  fence syncscope("singlethread") seq_cst
    #dbg_value(ptr %"h::Ptr", !15, !DIExpression(), !32)
    #dbg_value(double %"theta::Float64", !16, !DIExpression(), !32)
  call void @llvm.lifetime.start.p0(i64 24, ptr nonnull %"new::RefValue")
  store ptr %"h::Ptr", ptr %"new::RefValue", align 8, !dbg !17, !tbaa !33, !alias.scope !34, !noalias !38
  %"new::Env.sroa.2.0..sroa_idx" = getelementptr inbounds nuw i8, ptr %"new::RefValue", i64 8, !dbg !17
  store i64 3, ptr %"new::Env.sroa.2.0..sroa_idx", align 8, !dbg !17, !tbaa !33, !alias.scope !34, !noalias !38
  %"new::Env.sroa.3.0..sroa_idx" = getelementptr inbounds nuw i8, ptr %"new::RefValue", i64 16, !dbg !17
  store double %"theta::Float64", ptr %"new::Env.sroa.3.0..sroa_idx", align 8, !dbg !17, !tbaa !33, !alias.scope !34, !noalias !38
  %__bennett_ctrl = load atomic ptr, ptr @jlplt___bennett_ctrl_934_got unordered, align 8, !dbg !42
  call void %__bennett_ctrl(ptr %"h::Ptr", i64 0, ptr nonnull inttoptr (i64 127079231243584 to ptr), i64 8, ptr nonnull %"new::RefValue"), !dbg !42
  ret void, !dbg !42
}

; Function Attrs: noinline optnone
define nonnull ptr @jfptr_rF_ctrl_931(ptr %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") local_unnamed_addr #2 {
top:
  %thread_ptr = call ptr asm "movq %fs:0, $0", "=r"()
  %tls_ppgcstack = getelementptr inbounds i8, ptr %thread_ptr, i64 -8
  %tls_pgcstack = load ptr, ptr %tls_ppgcstack, align 8
  %0 = load ptr, ptr %"args::Any[]", align 8, !tbaa !30, !invariant.load !9, !alias.scope !43, !noalias !44, !nonnull !9, !dereferenceable !45, !align !45
  %1 = getelementptr inbounds i8, ptr %"args::Any[]", i32 8
  %2 = load ptr, ptr %1, align 8, !tbaa !30, !invariant.load !9, !alias.scope !43, !noalias !44, !nonnull !9, !dereferenceable !45, !align !45
  %.unbox = load ptr, ptr %0, align 8, !tbaa !46, !alias.scope !50, !noalias !51
  %.unbox1 = load double, ptr %2, align 8, !tbaa !46, !alias.scope !50, !noalias !51
  call swiftcc void @julia_rF_ctrl_930(ptr nonnull swiftself "gcstack" %tls_pgcstack, ptr %.unbox, double %.unbox1)
  %jl_nothing = load ptr, ptr @jl_nothing, align 8, !tbaa !30, !invariant.load !9, !alias.scope !43, !noalias !44, !nonnull !9
  ret ptr %jl_nothing
}

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) local_unnamed_addr #3

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #4

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_small_alloc(ptr, i32, i32, i64) #5

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @ijl_gc_queue_root(ptr) #3

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_big_alloc(ptr, i64, i64) #6

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_alloc_typed(ptr, i64, i64) #6

attributes #0 = { "julia.fname"="__bennett_ctrl" "julia.libidx"="0" }
attributes #1 = { "frame-pointer"="all" "julia.fsig"="rF_ctrl(Ptr{Nothing}, Float64)" "probe-stack"="inline-asm" }
attributes #2 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #3 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #4 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #6 = { nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }

!llvm.module.flags = !{!0, !1}
!llvm.dbg.cu = !{!2}

!0 = !{i32 2, !"Dwarf Version", i32 4}
!1 = !{i32 2, !"Debug Info Version", i32 3}
!2 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !3, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!3 = !DIFile(filename: "julia", directory: ".")
!4 = distinct !DISubprogram(name: "rF_ctrl", linkageName: "julia_rF_ctrl_930", scope: null, file: !5, line: 83, type: !6, scopeLine: 83, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !13)
!5 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!6 = !DISubroutineType(types: !7)
!7 = !{!8, !10, !11, !12}
!8 = !DICompositeType(tag: DW_TAG_structure_type, name: "Nothing", align: 8, elements: !9, runtimeLang: DW_LANG_Julia, identifier: "127079415932560")
!9 = !{}
!10 = !DICompositeType(tag: DW_TAG_structure_type, name: "#rF_ctrl", align: 8, elements: !9, runtimeLang: DW_LANG_Julia, identifier: "127079338224016")
!11 = !DIBasicType(name: "Ptr", size: 64, encoding: DW_ATE_unsigned)
!12 = !DIBasicType(name: "Float64", size: 64, encoding: DW_ATE_unsigned)
!13 = !{!14, !15, !16}
!14 = !DILocalVariable(name: "#self#", arg: 1, scope: !4, file: !5, line: 83, type: !10)
!15 = !DILocalVariable(name: "h", arg: 2, scope: !4, file: !5, line: 83, type: !11)
!16 = !DILocalVariable(name: "theta", arg: 3, scope: !4, file: !5, line: 83, type: !12)
!17 = !DILocation(line: 8, scope: !18, inlinedAt: !21)
!18 = distinct !DISubprogram(name: "RefValue;", linkageName: "RefValue", scope: !19, file: !19, type: !20, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!19 = !DIFile(filename: "refvalue.jl", directory: ".")
!20 = !DISubroutineType(types: !9)
!21 = !DILocation(line: 10, scope: !18, inlinedAt: !22)
!22 = !DILocation(line: 145, scope: !23, inlinedAt: !25)
!23 = distinct !DISubprogram(name: "Ref;", linkageName: "Ref", scope: !24, file: !24, type: !20, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!24 = !DIFile(filename: "refpointer.jl", directory: ".")
!25 = !DILocation(line: 84, scope: !4)
!26 = !{!27, !27, i64 0}
!27 = !{!"jtbaa_gcframe", !28, i64 0}
!28 = !{!"jtbaa", !29, i64 0}
!29 = !{!"jtbaa"}
!30 = !{!31, !31, i64 0}
!31 = !{!"jtbaa_const", !28, i64 0}
!32 = !DILocation(line: 83, scope: !4)
!33 = !{!28, !28, i64 0}
!34 = !{!35, !37}
!35 = !{!"jnoalias_stack", !36}
!36 = !{!"jnoalias"}
!37 = !{!"jnoalias_data", !36}
!38 = !{!39, !40, !41}
!39 = !{!"jnoalias_gcframe", !36}
!40 = !{!"jnoalias_typemd", !36}
!41 = !{!"jnoalias_const", !36}
!42 = !DILocation(line: 86, scope: !4)
!43 = !{!41}
!44 = !{!39, !35, !37, !40}
!45 = !{i64 8}
!46 = !{!47, !47, i64 0}
!47 = !{!"jtbaa_immut", !48, i64 0}
!48 = !{!"jtbaa_value", !49, i64 0}
!49 = !{!"jtbaa_data", !28, i64 0}
!50 = !{!37}
!51 = !{!39, !35, !40, !41}
