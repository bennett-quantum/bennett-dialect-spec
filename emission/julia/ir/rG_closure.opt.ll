; ModuleID = 'rG_closure'
source_filename = "rG_closure"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@jl_nothing = external local_unnamed_addr constant ptr
@jl_small_typeof = external constant i8
@"+Core.Tuple#959" = private unnamed_addr constant ptr @"+Core.Tuple#959.jit", !julia.constgv !0
@0 = private global [8 x ptr] [ptr @"j_#rG_closure##0_965", ptr null, ptr @"jl_global#968", ptr null, ptr @j_966_gfthunk, ptr getelementptr inbounds (i8, ptr @jl_small_typeof, i32 208), ptr @"+Core.Tuple#959", ptr inttoptr (i64 1 to ptr)]
@jl_world_counter = external local_unnamed_addr global i64
@1 = private global [34 x i64] zeroinitializer
@jl_emptysvec = external local_unnamed_addr constant ptr
@jlplt___bennett_ctrl_963_got = external local_unnamed_addr global ptr #0
@"_j_str_cfunction#3" = private unnamed_addr constant [10 x i8] c"cfunction\00", align 1
@"jl_global#968" = private unnamed_addr constant ptr @"jl_global#968.jit", !julia.constgv !0

@"+Main.#rG_closure##0#rG_closure##1#960.jit" = private alias ptr, inttoptr (i64 127079298881488 to ptr)
@"+Core.Tuple#959.jit" = private alias ptr, inttoptr (i64 127079298881616 to ptr)
@"jl_global#968.jit" = private alias ptr, inttoptr (i64 127079299147200 to ptr)
@"+Core.Ptr#967.jit" = private alias ptr, inttoptr (i64 127079415345856 to ptr)
@"+Main.Base.RefValue#957.jit" = private alias ptr, inttoptr (i64 127079416559152 to ptr)
@"+Main.Base.CFunction#961.jit" = private alias ptr, inttoptr (i64 127079475360288 to ptr)

; Function Signature: rG_closure(Ptr{Nothing})
define swiftcc void @julia_rG_closure_955(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"h::Ptr") local_unnamed_addr #1 !dbg !5 {
top:
  %gcframe1 = alloca [3 x ptr], align 16
  call void @llvm.memset.p0.i64(ptr align 16 %gcframe1, i8 0, i64 24, i1 true)
  store i64 4, ptr %gcframe1, align 8, !tbaa !15
  %frame.prev = getelementptr inbounds nuw i8, ptr %gcframe1, i64 8
  %task.gcstack = load ptr, ptr %pgcstack_arg, align 8
  store ptr %task.gcstack, ptr %frame.prev, align 8, !tbaa !15
  store ptr %gcframe1, ptr %pgcstack_arg, align 8
  %ptls_field = getelementptr inbounds nuw i8, ptr %pgcstack_arg, i64 16
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !15
  %0 = getelementptr inbounds nuw i8, ptr %ptls_load, i64 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !19, !invariant.load !0
  fence syncscope("singlethread") seq_cst
  %1 = load volatile i64, ptr %safepoint, align 8
  fence syncscope("singlethread") seq_cst
    #dbg_value(ptr %"h::Ptr", !14, !DIExpression(), !21)
  %ptls_load9 = load ptr, ptr %ptls_field, align 8, !dbg !22, !tbaa !15
  %"new::RefValue" = call noalias nonnull align 8 dereferenceable(16) ptr @ijl_gc_small_alloc(ptr %ptls_load9, i32 360, i32 16, i64 127079416559152) #13, !dbg !22
  %"new::RefValue.tag_addr" = getelementptr inbounds i8, ptr %"new::RefValue", i64 -8, !dbg !22
  store atomic i64 127079416559152, ptr %"new::RefValue.tag_addr" unordered, align 8, !dbg !22, !tbaa !31
  store i64 0, ptr %"new::RefValue", align 8, !dbg !22, !tbaa !34, !alias.scope !37, !noalias !40
  %gc_slot_addr_0 = getelementptr inbounds nuw i8, ptr %gcframe1, i64 16
  store ptr %"new::RefValue", ptr %gc_slot_addr_0, align 8
  %"box::#rG_closure##0#rG_closure##1" = call noalias nonnull align 8 dereferenceable(16) ptr @ijl_gc_small_alloc(ptr %ptls_load9, i32 360, i32 16, i64 127079298881488) #13, !dbg !45
  %"box::#rG_closure##0#rG_closure##1.tag_addr" = getelementptr inbounds i8, ptr %"box::#rG_closure##0#rG_closure##1", i64 -8, !dbg !45
  store atomic i64 127079298881488, ptr %"box::#rG_closure##0#rG_closure##1.tag_addr" unordered, align 8, !dbg !45, !tbaa !31
  store atomic ptr %"new::RefValue", ptr %"box::#rG_closure##0#rG_closure##1" unordered, align 8, !dbg !45, !tbaa !46, !alias.scope !37, !noalias !40
  %jl_emptysvec = load ptr, ptr @jl_emptysvec, align 8, !dbg !45, !tbaa !19, !invariant.load !0, !alias.scope !48, !noalias !49, !nonnull !0
  store ptr %"box::#rG_closure##0#rG_closure##1", ptr %gc_slot_addr_0, align 8
  %2 = call ptr @jl_get_cfunction_trampoline(ptr nonnull %"box::#rG_closure##0#rG_closure##1", ptr nonnull @"+Main.Base.CFunction#961.jit", ptr nonnull @1, ptr nonnull %jl_emptysvec, ptr nonnull @"jlcapi_#rG_closure##0_958make", ptr null, ptr null), !dbg !45
  %.ptr = load ptr, ptr %2, align 8, !dbg !50, !tbaa !34, !alias.scope !37, !noalias !40
  %__bennett_ctrl = load atomic ptr, ptr @jlplt___bennett_ctrl_963_got unordered, align 8, !dbg !56
  store ptr %2, ptr %gc_slot_addr_0, align 8
  call void %__bennett_ctrl(ptr %"h::Ptr", i64 0, ptr %.ptr, i64 8, ptr null), !dbg !56
  %frame.prev17 = load ptr, ptr %frame.prev, align 8, !tbaa !15
  store ptr %frame.prev17, ptr %pgcstack_arg, align 8, !tbaa !15
  ret void, !dbg !56
}

; Function Attrs: noinline optnone
define nonnull ptr @jfptr_rG_closure_956(ptr %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") local_unnamed_addr #2 {
top:
  %thread_ptr = call ptr asm "movq %fs:0, $0", "=r"()
  %tls_ppgcstack = getelementptr inbounds i8, ptr %thread_ptr, i64 -8
  %tls_pgcstack = load ptr, ptr %tls_ppgcstack, align 8
  %0 = load ptr, ptr %"args::Any[]", align 8, !tbaa !19, !invariant.load !0, !alias.scope !48, !noalias !49, !nonnull !0, !dereferenceable !57, !align !57
  %.unbox = load ptr, ptr %0, align 8, !tbaa !46, !alias.scope !37, !noalias !40
  call swiftcc void @julia_rG_closure_955(ptr nonnull swiftself "gcstack" %tls_pgcstack, ptr %.unbox)
  %jl_nothing = load ptr, ptr @jl_nothing, align 8, !tbaa !19, !invariant.load !0, !alias.scope !48, !noalias !49, !nonnull !0
  ret ptr %jl_nothing
}

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) local_unnamed_addr #3

; Function Attrs: mustprogress nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @julia.gc_alloc_obj(ptr, i64, ptr) local_unnamed_addr #4

define void @"jlcapi_#rG_closure##0_958"(ptr nest %0, ptr %1) #5 {
top:
  %gcframe1 = alloca [3 x ptr], align 16
  call void @llvm.memset.p0.i64(ptr align 16 %gcframe1, i8 0, i64 24, i1 true)
  %thread_ptr = call ptr asm "movq %fs:0, $0", "=r"() #16
  %tls_ppgcstack = getelementptr inbounds i8, ptr %thread_ptr, i64 -8
  %tls_pgcstack = load ptr, ptr %tls_ppgcstack, align 8
  %.not2 = icmp eq ptr %tls_pgcstack, null
  br i1 %.not2, label %3, label %2, !prof !58

2:                                                ; preds = %top
  %ptls_field = getelementptr inbounds nuw i8, ptr %tls_pgcstack, i64 16
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !15
  %gc_state = getelementptr inbounds nuw i8, ptr %ptls_load, i64 25
  %old_state = load atomic i8, ptr %gc_state monotonic, align 1
  store atomic i8 0, ptr %gc_state release, align 8
  %is_new_state.not = icmp eq i8 %old_state, 0
  br i1 %is_new_state.not, label %after_safepoint, label %safepoint

3:                                                ; preds = %top
  %4 = call ptr @ijl_autoinit_and_adopt_thread()
  br label %after_safepoint

after_safepoint:                                  ; preds = %2, %safepoint, %3
  %5 = phi i8 [ 2, %3 ], [ %old_state, %safepoint ], [ 0, %2 ]
  %pgcstack12 = phi ptr [ %4, %3 ], [ %tls_pgcstack, %safepoint ], [ %tls_pgcstack, %2 ]
  store i64 4, ptr %gcframe1, align 8, !tbaa !15
  %frame.prev = getelementptr inbounds nuw i8, ptr %gcframe1, i64 8
  %task.gcstack = load ptr, ptr %pgcstack12, align 8
  store ptr %task.gcstack, ptr %frame.prev, align 8, !tbaa !15
  store ptr %gcframe1, ptr %pgcstack12, align 8
  %world_age = getelementptr inbounds nuw i8, ptr %pgcstack12, i64 8
  %6 = load i64, ptr %world_age, align 8, !tbaa !15, !alias.scope !59, !noalias !60
  %7 = load ptr, ptr %0, align 8
  %8 = load atomic i64, ptr getelementptr inbounds nuw (i8, ptr @0, i64 8) acquire, align 8
  %9 = load atomic ptr, ptr @0 monotonic, align 8
  %10 = load atomic i64, ptr @jl_world_counter acquire, align 8
  store i64 %10, ptr %world_age, align 8, !tbaa !15, !alias.scope !59, !noalias !60
  %.not = icmp eq i64 %8, %10
  br i1 %.not, label %guard_exit, label %guard_pass

guard_pass:                                       ; preds = %after_safepoint
  %current_task = getelementptr inbounds i8, ptr %pgcstack12, i64 -152
  %gc_slot_addr_0 = getelementptr inbounds nuw i8, ptr %gcframe1, i64 16
  store ptr %7, ptr %gc_slot_addr_0, align 8
  %11 = call ptr @jl_get_abi_converter(ptr nonnull %current_task, ptr nonnull @0)
  br label %guard_exit

guard_exit:                                       ; preds = %guard_pass, %after_safepoint
  %guard_res = phi ptr [ %9, %after_safepoint ], [ %11, %guard_pass ]
  %gc_slot_addr_06 = getelementptr inbounds nuw i8, ptr %gcframe1, i64 16
  store ptr %7, ptr %gc_slot_addr_06, align 8
  call swiftcc void %guard_res(ptr nonnull swiftself "gcstack" %pgcstack12, ptr nocapture readonly %7, ptr %1)
  store i64 %6, ptr %world_age, align 8, !tbaa !15, !alias.scope !59, !noalias !60
  %frame.prev11 = load ptr, ptr %frame.prev, align 8, !tbaa !15
  store ptr %frame.prev11, ptr %pgcstack12, align 8, !tbaa !15
  %ptls_field16 = getelementptr inbounds nuw i8, ptr %pgcstack12, i64 16
  %ptls_load17 = load ptr, ptr %ptls_field16, align 8, !tbaa !15
  %gc_state18 = getelementptr inbounds nuw i8, ptr %ptls_load17, i64 25
  store atomic i8 %5, ptr %gc_state18 release, align 8
  %12 = getelementptr inbounds nuw i8, ptr %ptls_load17, i64 16
  %safepoint19 = load atomic ptr, ptr %12 monotonic, align 8, !tbaa !15
  fence syncscope("singlethread") seq_cst
  %13 = load volatile i64, ptr %safepoint19, align 8
  fence syncscope("singlethread") seq_cst
  ret void

safepoint:                                        ; preds = %2
  %14 = getelementptr inbounds nuw i8, ptr %ptls_load, i64 16
  %safepoint14 = load atomic ptr, ptr %14 monotonic, align 8, !tbaa !61, !invariant.load !0
  fence syncscope("singlethread") seq_cst
  %15 = load volatile i64, ptr %safepoint14, align 8
  fence syncscope("singlethread") seq_cst
  br label %after_safepoint
}

declare ptr @jl_get_abi_converter(ptr, ptr) local_unnamed_addr

define ptr @"jlcapi_#rG_closure##0_958make"(ptr %wrapper, ptr %newval) #5 {
top:
  call void @llvm.init.trampoline(ptr %wrapper, ptr nonnull @"jlcapi_#rG_closure##0_958", ptr %newval)
  %0 = call ptr @llvm.adjust.trampoline(ptr %wrapper)
  ret ptr %0
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.init.trampoline(ptr nocapture writeonly, ptr readnone, ptr readnone) #6

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: read)
declare ptr @llvm.adjust.trampoline(ptr) #7

declare nonnull ptr @jl_get_cfunction_trampoline(ptr, ptr, ptr, ptr, ptr, ptr, ptr) local_unnamed_addr

declare nonnull ptr @ijl_apply_generic(ptr, ptr noalias nocapture noundef readonly, i32)

; Function Signature: (::Main.var"#rG_closure##0#rG_closure##1"{Base.RefValue{Int64}})(Ptr{Nothing})
define swiftcc void @j_966_gfthunk(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr nocapture readonly %0, ptr %1) #8 {
top:
  %jlcallframe = alloca ptr, align 8
  %gcframe1 = alloca [4 x ptr], align 16
  call void @llvm.memset.p0.i64(ptr align 16 %gcframe1, i8 0, i64 32, i1 true)
  store i64 8, ptr %gcframe1, align 8, !tbaa !15
  %frame.prev = getelementptr inbounds nuw i8, ptr %gcframe1, i64 8
  %task.gcstack = load ptr, ptr %pgcstack_arg, align 8
  store ptr %task.gcstack, ptr %frame.prev, align 8, !tbaa !15
  store ptr %gcframe1, ptr %pgcstack_arg, align 8
  %ptls_field = getelementptr inbounds nuw i8, ptr %pgcstack_arg, i64 16
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !15
  %"box::#rG_closure##0#rG_closure##1" = call noalias nonnull align 8 dereferenceable(16) ptr @ijl_gc_small_alloc(ptr %ptls_load, i32 360, i32 16, i64 127079298881488) #13
  %"box::#rG_closure##0#rG_closure##1.tag_addr" = getelementptr inbounds i8, ptr %"box::#rG_closure##0#rG_closure##1", i64 -8
  store atomic i64 127079298881488, ptr %"box::#rG_closure##0#rG_closure##1.tag_addr" unordered, align 8, !tbaa !31
  %2 = load i64, ptr %0, align 8, !tbaa !62, !alias.scope !63, !noalias !64
  store i64 %2, ptr %"box::#rG_closure##0#rG_closure##1", align 8, !tbaa !62, !alias.scope !63, !noalias !64
  %gc_slot_addr_1 = getelementptr inbounds nuw i8, ptr %gcframe1, i64 24
  store ptr %"box::#rG_closure##0#rG_closure##1", ptr %gc_slot_addr_1, align 8
  %"box::Ptr" = call noalias nonnull align 8 dereferenceable(16) ptr @ijl_gc_small_alloc(ptr %ptls_load, i32 360, i32 16, i64 127079415345856) #13
  %"box::Ptr.tag_addr" = getelementptr inbounds i8, ptr %"box::Ptr", i64 -8
  store atomic i64 127079415345856, ptr %"box::Ptr.tag_addr" unordered, align 8, !tbaa !31
  store ptr %1, ptr %"box::Ptr", align 8, !tbaa !46, !alias.scope !37, !noalias !40
  %gc_slot_addr_0 = getelementptr inbounds nuw i8, ptr %gcframe1, i64 16
  store ptr %"box::Ptr", ptr %gc_slot_addr_0, align 8
  store ptr %"box::Ptr", ptr %jlcallframe, align 8
  %3 = call nonnull ptr @ijl_apply_generic(ptr nonnull %"box::#rG_closure##0#rG_closure##1", ptr nonnull %jlcallframe, i32 1)
  %.tag_addr = getelementptr inbounds i8, ptr %3, i64 -8
  %.tag = load atomic volatile i64, ptr %.tag_addr unordered, align 8, !tbaa !31, !range !65
  %4 = and i64 %.tag, -16
  %exactly_isa = icmp eq i64 %4, 208
  br i1 %exactly_isa, label %pass, label %fail

fail:                                             ; preds = %top
  %5 = load ptr, ptr getelementptr inbounds nuw (i8, ptr @jl_small_typeof, i64 208), align 8, !tbaa !19, !invariant.load !0, !alias.scope !48, !noalias !49, !nonnull !0, !dereferenceable !66, !align !67
  store ptr null, ptr %gc_slot_addr_1, align 8
  store ptr null, ptr %gc_slot_addr_0, align 8
  call void @ijl_type_error(ptr nonnull @"_j_str_cfunction#3", ptr nonnull %5, ptr nonnull %3)
  unreachable

pass:                                             ; preds = %top
  %frame.prev11 = load ptr, ptr %frame.prev, align 8, !tbaa !15
  store ptr %frame.prev11, ptr %pgcstack_arg, align 8, !tbaa !15
  ret void
}

declare nonnull ptr @julia.call(ptr, ptr, ...) local_unnamed_addr

; Function Attrs: nofree norecurse nosync nounwind memory(none)
declare nonnull ptr @julia.typeof(ptr) local_unnamed_addr #9

; Function Attrs: mustprogress nofree norecurse nosync nounwind speculatable willreturn memory(none)
declare nonnull ptr @julia.pointer_from_objref(ptr) local_unnamed_addr #10

; Function Attrs: noreturn
declare void @ijl_type_error(ptr, ptr, ptr) local_unnamed_addr #11

; Function Signature: (::Main.var"#rG_closure##0#rG_closure##1"{Base.RefValue{Int64}})(Ptr{Nothing})
declare swiftcc void @"j_#rG_closure##0_965"(ptr nonnull swiftself "gcstack", ptr nocapture readonly, ptr) #8

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #12

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #12

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_small_alloc(ptr, i32, i32, i64) #13

declare noalias nonnull ptr @julia.new_gc_frame(i32)

declare void @julia.push_gc_frame(ptr, i32)

declare ptr @julia.get_gc_frame_slot(ptr, i32)

declare void @julia.pop_gc_frame(ptr)

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @julia.gc_alloc_bytes(ptr, i64, i64) #14

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @ijl_gc_queue_root(ptr) #3

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_big_alloc(ptr, i64, i64) #14

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_alloc_typed(ptr, i64, i64) #14

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i64(ptr nocapture writeonly, i8, i64, i1 immarg) #15

declare ptr @ijl_autoinit_and_adopt_thread() local_unnamed_addr

attributes #0 = { "julia.fname"="__bennett_ctrl" "julia.libidx"="0" }
attributes #1 = { "frame-pointer"="all" "julia.fsig"="rG_closure(Ptr{Nothing})" "probe-stack"="inline-asm" }
attributes #2 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #3 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #4 = { mustprogress nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #5 = { "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #6 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: read) }
attributes #8 = { "frame-pointer"="all" "julia.fsig"="(::Main.var\22#rG_closure##0#rG_closure##1\22{Base.RefValue{Int64}})(Ptr{Nothing})" "probe-stack"="inline-asm" }
attributes #9 = { nofree norecurse nosync nounwind memory(none) }
attributes #10 = { mustprogress nofree norecurse nosync nounwind speculatable willreturn memory(none) }
attributes #11 = { noreturn }
attributes #12 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #13 = { nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #14 = { nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #15 = { nocallback nofree nounwind willreturn memory(argmem: write) }
attributes #16 = { nounwind }

!llvm.module.flags = !{!1, !2}
!llvm.dbg.cu = !{!3}

!0 = !{}
!1 = !{i32 2, !"Dwarf Version", i32 4}
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !4, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!4 = !DIFile(filename: "julia", directory: ".")
!5 = distinct !DISubprogram(name: "rG_closure", linkageName: "julia_rG_closure_955", scope: null, file: !6, line: 99, type: !7, scopeLine: 99, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3, retainedNodes: !12)
!6 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!7 = !DISubroutineType(types: !8)
!8 = !{!9, !10, !11}
!9 = !DICompositeType(tag: DW_TAG_structure_type, name: "Nothing", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079415932560")
!10 = !DICompositeType(tag: DW_TAG_structure_type, name: "#rG_closure", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079338227536")
!11 = !DIBasicType(name: "Ptr", size: 64, encoding: DW_ATE_unsigned)
!12 = !{!13, !14}
!13 = !DILocalVariable(name: "#self#", arg: 1, scope: !5, file: !6, line: 99, type: !10)
!14 = !DILocalVariable(name: "h", arg: 2, scope: !5, file: !6, line: 99, type: !11)
!15 = !{!16, !16, i64 0}
!16 = !{!"jtbaa_gcframe", !17, i64 0}
!17 = !{!"jtbaa", !18, i64 0}
!18 = !{!"jtbaa"}
!19 = !{!20, !20, i64 0}
!20 = !{!"jtbaa_const", !17, i64 0}
!21 = !DILocation(line: 99, scope: !5)
!22 = !DILocation(line: 8, scope: !23, inlinedAt: !26)
!23 = distinct !DISubprogram(name: "RefValue;", linkageName: "RefValue", scope: !24, file: !24, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!24 = !DIFile(filename: "refvalue.jl", directory: ".")
!25 = !DISubroutineType(types: !0)
!26 = !DILocation(line: 10, scope: !23, inlinedAt: !27)
!27 = !DILocation(line: 145, scope: !28, inlinedAt: !30)
!28 = distinct !DISubprogram(name: "Ref;", linkageName: "Ref", scope: !29, file: !29, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!29 = !DIFile(filename: "refpointer.jl", directory: ".")
!30 = !DILocation(line: 100, scope: !5)
!31 = !{!32, !32, i64 0}
!32 = !{!"jtbaa_tag", !33, i64 0}
!33 = !{!"jtbaa_data", !17, i64 0}
!34 = !{!35, !35, i64 0}
!35 = !{!"jtbaa_mutab", !36, i64 0}
!36 = !{!"jtbaa_value", !33, i64 0}
!37 = !{!38}
!38 = !{!"jnoalias_data", !39}
!39 = !{!"jnoalias"}
!40 = !{!41, !42, !43, !44}
!41 = !{!"jnoalias_gcframe", !39}
!42 = !{!"jnoalias_stack", !39}
!43 = !{!"jnoalias_typemd", !39}
!44 = !{!"jnoalias_const", !39}
!45 = !DILocation(line: 102, scope: !5)
!46 = !{!47, !47, i64 0}
!47 = !{!"jtbaa_immut", !36, i64 0}
!48 = !{!44}
!49 = !{!41, !42, !38, !43}
!50 = !DILocation(line: 57, scope: !51, inlinedAt: !53)
!51 = distinct !DISubprogram(name: "getproperty;", linkageName: "getproperty", scope: !52, file: !52, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!52 = !DIFile(filename: "Base_compiler.jl", directory: ".")
!53 = !DILocation(line: 36, scope: !54, inlinedAt: !56)
!54 = distinct !DISubprogram(name: "unsafe_convert;", linkageName: "unsafe_convert", scope: !55, file: !55, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!55 = !DIFile(filename: "c.jl", directory: ".")
!56 = !DILocation(line: 103, scope: !5)
!57 = !{i64 8}
!58 = !{!"branch_weights", i32 1, i32 9}
!59 = !{!41}
!60 = !{!42, !38, !43, !44}
!61 = !{!20, !20, i64 0, i64 1}
!62 = !{!17, !17, i64 0}
!63 = !{!44, !38}
!64 = !{!41, !42, !43}
!65 = !{i64 16, i64 0}
!66 = !{i64 56}
!67 = !{i64 16}
