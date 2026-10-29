; ModuleID = 'rF2_ctrl'
source_filename = "rF2_ctrl"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@jl_nothing = external local_unnamed_addr constant ptr
@jl_small_typeof = external constant i8
@"+Core.Tuple#910" = private unnamed_addr constant ptr @"+Core.Tuple#910.jit", !julia.constgv !0
@0 = private global [8 x ptr] [ptr @j_body_914, ptr null, ptr @"jl_global#918", ptr null, ptr @j_915_gfthunk, ptr getelementptr inbounds (i8, ptr @jl_small_typeof, i32 208), ptr @"+Core.Tuple#910", ptr inttoptr (i64 1 to ptr)]
@jl_world_counter = external local_unnamed_addr global i64
@jlplt___bennett_ctrl_912_got = external local_unnamed_addr global ptr #0
@"_j_str_cfunction#3" = private unnamed_addr constant [10 x i8] c"cfunction\00", align 1
@"jl_global#918" = private unnamed_addr constant ptr @"jl_global#918.jit", !julia.constgv !0

@"jl_global#918.jit" = private alias ptr, inttoptr (i64 127079300351264 to ptr)
@"+Core.Tuple#910.jit" = private alias ptr, inttoptr (i64 127079338221840 to ptr)
@"jl_global#916.jit" = private alias ptr, inttoptr (i64 127079341093304 to ptr)
@"+Core.Ptr#917.jit" = private alias ptr, inttoptr (i64 127079415345856 to ptr)

; Function Signature: rF2_ctrl(Ptr{Nothing}, Float64)
define swiftcc void @julia_rF2_ctrl_906(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"h::Ptr", double %"theta::Float64") local_unnamed_addr #1 !dbg !5 {
top:
  %"new::RefValue" = alloca [3 x i64], align 16, !dbg !17
  %ptls_field = getelementptr inbounds nuw i8, ptr %pgcstack_arg, i64 16
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !26
  %0 = getelementptr inbounds nuw i8, ptr %ptls_load, i64 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !30, !invariant.load !0
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
  %__bennett_ctrl = load atomic ptr, ptr @jlplt___bennett_ctrl_912_got unordered, align 8, !dbg !42
  call void %__bennett_ctrl(ptr %"h::Ptr", i64 0, ptr nonnull @jlcapi_body_909, i64 8, ptr nonnull %"new::RefValue"), !dbg !42
  ret void, !dbg !42
}

; Function Attrs: noinline optnone
define nonnull ptr @jfptr_rF2_ctrl_907(ptr %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") local_unnamed_addr #2 {
top:
  %thread_ptr = call ptr asm "movq %fs:0, $0", "=r"()
  %tls_ppgcstack = getelementptr inbounds i8, ptr %thread_ptr, i64 -8
  %tls_pgcstack = load ptr, ptr %tls_ppgcstack, align 8
  %0 = load ptr, ptr %"args::Any[]", align 8, !tbaa !30, !invariant.load !0, !alias.scope !43, !noalias !44, !nonnull !0, !dereferenceable !45, !align !45
  %1 = getelementptr inbounds i8, ptr %"args::Any[]", i32 8
  %2 = load ptr, ptr %1, align 8, !tbaa !30, !invariant.load !0, !alias.scope !43, !noalias !44, !nonnull !0, !dereferenceable !45, !align !45
  %.unbox = load ptr, ptr %0, align 8, !tbaa !46, !alias.scope !50, !noalias !51
  %.unbox1 = load double, ptr %2, align 8, !tbaa !46, !alias.scope !50, !noalias !51
  call swiftcc void @julia_rF2_ctrl_906(ptr nonnull swiftself "gcstack" %tls_pgcstack, ptr %.unbox, double %.unbox1)
  %jl_nothing = load ptr, ptr @jl_nothing, align 8, !tbaa !30, !invariant.load !0, !alias.scope !43, !noalias !44, !nonnull !0
  ret ptr %jl_nothing
}

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) local_unnamed_addr #3

; Function Attrs: mustprogress nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @julia.gc_alloc_obj(ptr, i64, ptr) local_unnamed_addr #4

define void @jlcapi_body_909(ptr %0) #5 {
top:
  %thread_ptr = call ptr asm "movq %fs:0, $0", "=r"() #14
  %tls_ppgcstack = getelementptr inbounds i8, ptr %thread_ptr, i64 -8
  %tls_pgcstack = load ptr, ptr %tls_ppgcstack, align 8
  %.not1 = icmp eq ptr %tls_pgcstack, null
  br i1 %.not1, label %2, label %1, !prof !52

1:                                                ; preds = %top
  %ptls_field = getelementptr inbounds nuw i8, ptr %tls_pgcstack, i64 16
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !26
  %gc_state = getelementptr inbounds nuw i8, ptr %ptls_load, i64 25
  %old_state = load atomic i8, ptr %gc_state monotonic, align 1
  store atomic i8 0, ptr %gc_state release, align 8
  %is_new_state.not = icmp eq i8 %old_state, 0
  br i1 %is_new_state.not, label %after_safepoint, label %safepoint

2:                                                ; preds = %top
  %3 = call ptr @ijl_autoinit_and_adopt_thread()
  br label %after_safepoint

after_safepoint:                                  ; preds = %1, %safepoint, %2
  %4 = phi i8 [ 2, %2 ], [ %old_state, %safepoint ], [ 0, %1 ]
  %pgcstack7 = phi ptr [ %3, %2 ], [ %tls_pgcstack, %safepoint ], [ %tls_pgcstack, %1 ]
  %world_age = getelementptr inbounds nuw i8, ptr %pgcstack7, i64 8
  %5 = load i64, ptr %world_age, align 8, !tbaa !26, !alias.scope !53, !noalias !54
  %6 = load atomic i64, ptr getelementptr inbounds nuw (i8, ptr @0, i64 8) acquire, align 8
  %7 = load atomic ptr, ptr @0 monotonic, align 8
  %8 = load atomic i64, ptr @jl_world_counter acquire, align 8
  store i64 %8, ptr %world_age, align 8, !tbaa !26, !alias.scope !53, !noalias !54
  %.not = icmp eq i64 %6, %8
  br i1 %.not, label %guard_exit, label %guard_pass

guard_pass:                                       ; preds = %after_safepoint
  %current_task = getelementptr inbounds i8, ptr %pgcstack7, i64 -152
  %9 = call ptr @jl_get_abi_converter(ptr nonnull %current_task, ptr nonnull @0)
  br label %guard_exit

guard_exit:                                       ; preds = %guard_pass, %after_safepoint
  %guard_res = phi ptr [ %7, %after_safepoint ], [ %9, %guard_pass ]
  call swiftcc void %guard_res(ptr nonnull swiftself "gcstack" %pgcstack7, ptr %0)
  store i64 %5, ptr %world_age, align 8, !tbaa !26, !alias.scope !53, !noalias !54
  %ptls_field11 = getelementptr inbounds nuw i8, ptr %pgcstack7, i64 16
  %ptls_load12 = load ptr, ptr %ptls_field11, align 8, !tbaa !26
  %gc_state13 = getelementptr inbounds nuw i8, ptr %ptls_load12, i64 25
  store atomic i8 %4, ptr %gc_state13 release, align 8
  %10 = getelementptr inbounds nuw i8, ptr %ptls_load12, i64 16
  %safepoint14 = load atomic ptr, ptr %10 monotonic, align 8, !tbaa !26
  fence syncscope("singlethread") seq_cst
  %11 = load volatile i64, ptr %safepoint14, align 8
  fence syncscope("singlethread") seq_cst
  ret void

safepoint:                                        ; preds = %1
  %12 = getelementptr inbounds nuw i8, ptr %ptls_load, i64 16
  %safepoint9 = load atomic ptr, ptr %12 monotonic, align 8, !tbaa !55, !invariant.load !0
  fence syncscope("singlethread") seq_cst
  %13 = load volatile i64, ptr %safepoint9, align 8
  fence syncscope("singlethread") seq_cst
  br label %after_safepoint
}

declare ptr @jl_get_abi_converter(ptr, ptr) local_unnamed_addr

; Function Attrs: mustprogress nofree norecurse nosync nounwind speculatable willreturn memory(none)
declare nonnull ptr @julia.pointer_from_objref(ptr) local_unnamed_addr #6

declare nonnull ptr @ijl_apply_generic(ptr, ptr noalias nocapture noundef readonly, i32)

; Function Signature: body(Ptr{Nothing})
define swiftcc void @j_915_gfthunk(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %0) #7 {
top:
  %jlcallframe = alloca ptr, align 8
  %gcframe1 = alloca [3 x ptr], align 16
  call void @llvm.memset.p0.i64(ptr align 16 %gcframe1, i8 0, i64 24, i1 true)
  store i64 4, ptr %gcframe1, align 8, !tbaa !26
  %frame.prev = getelementptr inbounds nuw i8, ptr %gcframe1, i64 8
  %task.gcstack = load ptr, ptr %pgcstack_arg, align 8
  store ptr %task.gcstack, ptr %frame.prev, align 8, !tbaa !26
  store ptr %gcframe1, ptr %pgcstack_arg, align 8
  %ptls_field = getelementptr inbounds nuw i8, ptr %pgcstack_arg, i64 16
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !26
  %"box::Ptr" = call noalias nonnull align 8 dereferenceable(16) ptr @ijl_gc_small_alloc(ptr %ptls_load, i32 360, i32 16, i64 127079415345856) #11
  %"box::Ptr.tag_addr" = getelementptr inbounds i8, ptr %"box::Ptr", i64 -8
  store atomic i64 127079415345856, ptr %"box::Ptr.tag_addr" unordered, align 8, !tbaa !56
  store ptr %0, ptr %"box::Ptr", align 8, !tbaa !46, !alias.scope !50, !noalias !51
  %gc_slot_addr_0 = getelementptr inbounds nuw i8, ptr %gcframe1, i64 16
  store ptr %"box::Ptr", ptr %gc_slot_addr_0, align 8
  store ptr %"box::Ptr", ptr %jlcallframe, align 8
  %1 = call nonnull ptr @ijl_apply_generic(ptr nonnull @"jl_global#916.jit", ptr nonnull %jlcallframe, i32 1)
  %.tag_addr = getelementptr inbounds i8, ptr %1, i64 -8
  %.tag = load atomic volatile i64, ptr %.tag_addr unordered, align 8, !tbaa !56, !range !58
  %2 = and i64 %.tag, -16
  %exactly_isa = icmp eq i64 %2, 208
  br i1 %exactly_isa, label %pass, label %fail

fail:                                             ; preds = %top
  %3 = load ptr, ptr getelementptr inbounds nuw (i8, ptr @jl_small_typeof, i64 208), align 8, !tbaa !30, !invariant.load !0, !alias.scope !43, !noalias !44, !nonnull !0, !dereferenceable !59, !align !60
  store ptr null, ptr %gc_slot_addr_0, align 8
  call void @ijl_type_error(ptr nonnull @"_j_str_cfunction#3", ptr nonnull %3, ptr nonnull %1)
  unreachable

pass:                                             ; preds = %top
  %frame.prev5 = load ptr, ptr %frame.prev, align 8, !tbaa !26
  store ptr %frame.prev5, ptr %pgcstack_arg, align 8, !tbaa !26
  ret void
}

declare nonnull ptr @julia.call(ptr, ptr, ...) local_unnamed_addr

; Function Attrs: nofree norecurse nosync nounwind memory(none)
declare nonnull ptr @julia.typeof(ptr) local_unnamed_addr #8

; Function Attrs: noreturn
declare void @ijl_type_error(ptr, ptr, ptr) local_unnamed_addr #9

; Function Signature: body(Ptr{Nothing})
declare swiftcc void @j_body_914(ptr nonnull swiftself "gcstack", ptr) #7

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #10

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #10

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_small_alloc(ptr, i32, i32, i64) #11

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @ijl_gc_queue_root(ptr) #3

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_big_alloc(ptr, i64, i64) #12

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_alloc_typed(ptr, i64, i64) #12

declare noalias nonnull ptr @julia.new_gc_frame(i32)

declare void @julia.push_gc_frame(ptr, i32)

declare ptr @julia.get_gc_frame_slot(ptr, i32)

declare void @julia.pop_gc_frame(ptr)

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @julia.gc_alloc_bytes(ptr, i64, i64) #12

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i64(ptr nocapture writeonly, i8, i64, i1 immarg) #13

declare ptr @ijl_autoinit_and_adopt_thread() local_unnamed_addr

attributes #0 = { "julia.fname"="__bennett_ctrl" "julia.libidx"="0" }
attributes #1 = { "frame-pointer"="all" "julia.fsig"="rF2_ctrl(Ptr{Nothing}, Float64)" "probe-stack"="inline-asm" }
attributes #2 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #3 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #4 = { mustprogress nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #5 = { "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #6 = { mustprogress nofree norecurse nosync nounwind speculatable willreturn memory(none) }
attributes #7 = { "frame-pointer"="all" "julia.fsig"="body(Ptr{Nothing})" "probe-stack"="inline-asm" }
attributes #8 = { nofree norecurse nosync nounwind memory(none) }
attributes #9 = { noreturn }
attributes #10 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #11 = { nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #12 = { nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #13 = { nocallback nofree nounwind willreturn memory(argmem: write) }
attributes #14 = { nounwind }

!llvm.module.flags = !{!1, !2}
!llvm.dbg.cu = !{!3}

!0 = !{}
!1 = !{i32 2, !"Dwarf Version", i32 4}
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !4, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!4 = !DIFile(filename: "julia", directory: ".")
!5 = distinct !DISubprogram(name: "rF2_ctrl", linkageName: "julia_rF2_ctrl_906", scope: null, file: !6, line: 91, type: !7, scopeLine: 91, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3, retainedNodes: !13)
!6 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!7 = !DISubroutineType(types: !8)
!8 = !{!9, !10, !11, !12}
!9 = !DICompositeType(tag: DW_TAG_structure_type, name: "Nothing", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079415932560")
!10 = !DICompositeType(tag: DW_TAG_structure_type, name: "#rF2_ctrl", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079338225744")
!11 = !DIBasicType(name: "Ptr", size: 64, encoding: DW_ATE_unsigned)
!12 = !DIBasicType(name: "Float64", size: 64, encoding: DW_ATE_unsigned)
!13 = !{!14, !15, !16}
!14 = !DILocalVariable(name: "#self#", arg: 1, scope: !5, file: !6, line: 91, type: !10)
!15 = !DILocalVariable(name: "h", arg: 2, scope: !5, file: !6, line: 91, type: !11)
!16 = !DILocalVariable(name: "theta", arg: 3, scope: !5, file: !6, line: 91, type: !12)
!17 = !DILocation(line: 8, scope: !18, inlinedAt: !21)
!18 = distinct !DISubprogram(name: "RefValue;", linkageName: "RefValue", scope: !19, file: !19, type: !20, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!19 = !DIFile(filename: "refvalue.jl", directory: ".")
!20 = !DISubroutineType(types: !0)
!21 = !DILocation(line: 10, scope: !18, inlinedAt: !22)
!22 = !DILocation(line: 145, scope: !23, inlinedAt: !25)
!23 = distinct !DISubprogram(name: "Ref;", linkageName: "Ref", scope: !24, file: !24, type: !20, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!24 = !DIFile(filename: "refpointer.jl", directory: ".")
!25 = !DILocation(line: 92, scope: !5)
!26 = !{!27, !27, i64 0}
!27 = !{!"jtbaa_gcframe", !28, i64 0}
!28 = !{!"jtbaa", !29, i64 0}
!29 = !{!"jtbaa"}
!30 = !{!31, !31, i64 0}
!31 = !{!"jtbaa_const", !28, i64 0}
!32 = !DILocation(line: 91, scope: !5)
!33 = !{!28, !28, i64 0}
!34 = !{!35, !37}
!35 = !{!"jnoalias_stack", !36}
!36 = !{!"jnoalias"}
!37 = !{!"jnoalias_data", !36}
!38 = !{!39, !40, !41}
!39 = !{!"jnoalias_gcframe", !36}
!40 = !{!"jnoalias_typemd", !36}
!41 = !{!"jnoalias_const", !36}
!42 = !DILocation(line: 94, scope: !5)
!43 = !{!41}
!44 = !{!39, !35, !37, !40}
!45 = !{i64 8}
!46 = !{!47, !47, i64 0}
!47 = !{!"jtbaa_immut", !48, i64 0}
!48 = !{!"jtbaa_value", !49, i64 0}
!49 = !{!"jtbaa_data", !28, i64 0}
!50 = !{!37}
!51 = !{!39, !35, !40, !41}
!52 = !{!"branch_weights", i32 1, i32 9}
!53 = !{!39}
!54 = !{!35, !37, !40, !41}
!55 = !{!31, !31, i64 0, i64 1}
!56 = !{!57, !57, i64 0}
!57 = !{!"jtbaa_tag", !49, i64 0}
!58 = !{i64 16, i64 0}
!59 = !{i64 56}
!60 = !{i64 16}
