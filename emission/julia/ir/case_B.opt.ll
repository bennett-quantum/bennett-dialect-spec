; ModuleID = 'case_B'
source_filename = "case_B"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@jlplt___bennett_qalloc_526_got = external local_unnamed_addr global ptr #0
@jlplt___bennett_gate_528_got = external local_unnamed_addr global ptr #1
@jlplt___bennett_rot_530_got = external local_unnamed_addr global ptr #2
@jlplt___bennett_measure_532_got = external local_unnamed_addr global ptr #3
@jlplt___bennett_ctrl_535_got = external local_unnamed_addr global ptr #4
@jlplt___bennett_ctrl_v_539_got = external local_unnamed_addr global ptr #5
@jlplt___bennett_qfree_541_got = external local_unnamed_addr global ptr #6

@"+Core.GenericMemory#536.jit" = private alias ptr, inttoptr (i64 127079420148128 to ptr)
@"+Core.Array#537.jit" = private alias ptr, inttoptr (i64 127079420430544 to ptr)

; Function Signature: case_B(UInt64)
define swiftcc range(i64 0, 2) i64 @julia_case_B_523(ptr nonnull swiftself "gcstack" %pgcstack_arg, i64 zeroext %"x::UInt64") local_unnamed_addr #7 !dbg !4 {
top:
  %gcframe1 = alloca [4 x ptr], align 16
  call void @llvm.memset.p0.i64(ptr align 16 %gcframe1, i8 0, i64 32, i1 true)
  store i64 8, ptr %gcframe1, align 8, !tbaa !14
  %frame.prev = getelementptr inbounds nuw i8, ptr %gcframe1, i64 8
  %task.gcstack = load ptr, ptr %pgcstack_arg, align 8
  store ptr %task.gcstack, ptr %frame.prev, align 8, !tbaa !14
  store ptr %gcframe1, ptr %pgcstack_arg, align 8
  %"new::RefValue" = alloca [3 x i64], align 16, !dbg !18
  %"new::Tuple29" = alloca [1 x i64], align 8
  %ptls_field = getelementptr inbounds nuw i8, ptr %pgcstack_arg, i64 16
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !14
  %0 = getelementptr inbounds nuw i8, ptr %ptls_load, i64 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !29, !invariant.load !10
  fence syncscope("singlethread") seq_cst
  %1 = load volatile i64, ptr %safepoint, align 8
  fence syncscope("singlethread") seq_cst
    #dbg_value(i64 %"x::UInt64", !13, !DIExpression(), !31)
  %__bennett_qalloc = load atomic ptr, ptr @jlplt___bennett_qalloc_526_got unordered, align 8, !dbg !32
  %2 = call ptr %__bennett_qalloc(i64 0, i64 4), !dbg !32
  %__bennett_gate = load atomic ptr, ptr @jlplt___bennett_gate_528_got unordered, align 8, !dbg !35
  call void %__bennett_gate(i32 1, ptr %2, i64 0), !dbg !35
  %3 = uitofp i64 %"x::UInt64" to double, !dbg !38
  %4 = fmul double %3, 1.250000e-01, !dbg !42
  %__bennett_rot = load atomic ptr, ptr @jlplt___bennett_rot_530_got unordered, align 8, !dbg !44
  call void %__bennett_rot(i32 3, ptr %2, i64 1, double %4), !dbg !44
  %__bennett_measure = load atomic ptr, ptr @jlplt___bennett_measure_532_got unordered, align 8, !dbg !47
  %5 = call i8 %__bennett_measure(ptr %2, i64 0), !dbg !47
  %6 = trunc i8 %5 to i1, !dbg !49
  br i1 %6, label %L8, label %L42, !dbg !49

L8:                                               ; preds = %top
  %__bennett_gate1 = load atomic ptr, ptr @jlplt___bennett_gate_528_got unordered, align 8, !dbg !50
  call void %__bennett_gate1(i32 1, ptr %2, i64 2), !dbg !50
  br label %L42, !dbg !50

L39:                                              ; preds = %L42.2, %L42.1, %L42
  %value_phi6.lcssa = phi i64 [ 2, %L42 ], [ 3, %L42.1 ], [ 4, %L42.2 ]
  store i64 %value_phi6.lcssa, ptr %"new::Tuple29", align 8, !dbg !52, !tbaa !58, !alias.scope !60, !noalias !63
  call swiftcc void @j_throw_boundserror_542(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr nonnull %"new::Array", ptr nocapture nonnull readonly %"new::Tuple29") #18, !dbg !52
  unreachable, !dbg !52

L42:                                              ; preds = %L8, %top
  %value_phi = phi i64 [ 1, %L8 ], [ 0, %top ]
  call void @llvm.lifetime.start.p0(i64 24, ptr nonnull %"new::RefValue")
  store ptr %2, ptr %"new::RefValue", align 8, !dbg !18, !tbaa !68, !alias.scope !69, !noalias !70
  %"new::Env.sroa.2.0..sroa_idx" = getelementptr inbounds nuw i8, ptr %"new::RefValue", i64 8, !dbg !18
  store i64 3, ptr %"new::Env.sroa.2.0..sroa_idx", align 8, !dbg !18, !tbaa !68, !alias.scope !69, !noalias !70
  %"new::Env.sroa.3.0..sroa_idx" = getelementptr inbounds nuw i8, ptr %"new::RefValue", i64 16, !dbg !18
  store double %4, ptr %"new::Env.sroa.3.0..sroa_idx", align 8, !dbg !18, !tbaa !68, !alias.scope !69, !noalias !70
  %__bennett_ctrl = load atomic ptr, ptr @jlplt___bennett_ctrl_535_got unordered, align 8, !dbg !71
  call void %__bennett_ctrl(ptr %2, i64 0, ptr nonnull inttoptr (i64 127079231243584 to ptr), i64 8, ptr nonnull %"new::RefValue"), !dbg !71
  call void @llvm.lifetime.end.p0(i64 24, ptr nonnull %"new::RefValue")
  %ptls_load45 = load ptr, ptr %ptls_field, align 8, !dbg !72, !tbaa !14
  %"Memory{Ptr}[]" = call noalias nonnull align 8 dereferenceable(64) ptr @ijl_gc_small_alloc(ptr %ptls_load45, i32 504, i32 64, i64 127079420148128) #15, !dbg !72
  %"Memory{Ptr}[].tag_addr" = getelementptr inbounds i8, ptr %"Memory{Ptr}[]", i64 -8, !dbg !72
  store atomic i64 127079420148128, ptr %"Memory{Ptr}[].tag_addr" unordered, align 8, !dbg !72, !tbaa !78
  %memory_ptr = getelementptr inbounds nuw i8, ptr %"Memory{Ptr}[]", i64 8, !dbg !72
  %memory_data = getelementptr inbounds nuw i8, ptr %"Memory{Ptr}[]", i64 16, !dbg !72
  store ptr %memory_data, ptr %memory_ptr, align 8, !dbg !72, !tbaa !81, !alias.scope !84, !noalias !85
  store i64 4, ptr %"Memory{Ptr}[]", align 8, !dbg !72, !tbaa !86, !alias.scope !84, !noalias !85
  %gc_slot_addr_0 = getelementptr inbounds nuw i8, ptr %gcframe1, i64 16
  store ptr %"Memory{Ptr}[]", ptr %gc_slot_addr_0, align 8
  %"new::Array" = call noalias nonnull align 8 dereferenceable(32) ptr @ijl_gc_small_alloc(ptr %ptls_load45, i32 408, i32 32, i64 127079420430544) #15, !dbg !88
  %"new::Array.tag_addr" = getelementptr inbounds i8, ptr %"new::Array", i64 -8, !dbg !88
  store atomic i64 127079420430544, ptr %"new::Array.tag_addr" unordered, align 8, !dbg !88, !tbaa !78
  %7 = getelementptr inbounds nuw i8, ptr %"new::Array", i64 8, !dbg !88
  store ptr %memory_data, ptr %"new::Array", align 8, !dbg !88, !tbaa !89, !alias.scope !84, !noalias !85
  store ptr %"Memory{Ptr}[]", ptr %7, align 8, !dbg !88, !tbaa !89, !alias.scope !84, !noalias !85
  %"new::Array.size_ptr" = getelementptr inbounds nuw i8, ptr %"new::Array", i64 16, !dbg !88
  store i64 4, ptr %"new::Array.size_ptr", align 8, !dbg !88, !tbaa !91, !alias.scope !84, !noalias !85
  %__bennett_qalloc8 = load atomic ptr, ptr @jlplt___bennett_qalloc_526_got unordered, align 8, !dbg !93
  %gc_slot_addr_1 = getelementptr inbounds nuw i8, ptr %gcframe1, i64 24
  store ptr %"new::Array", ptr %gc_slot_addr_1, align 8
  %8 = call ptr %__bennett_qalloc8(i64 0, i64 1), !dbg !93
  store ptr %8, ptr %memory_data, align 8, !dbg !94, !tbaa !95, !alias.scope !97, !noalias !98
  %__bennett_qalloc8.1 = load atomic ptr, ptr @jlplt___bennett_qalloc_526_got unordered, align 8, !dbg !93
  store ptr null, ptr %gc_slot_addr_0, align 8
  %9 = call ptr %__bennett_qalloc8.1(i64 0, i64 1), !dbg !93
  %"new::Array.size_ptr9.copyload.1" = load i64, ptr %"new::Array.size_ptr", align 8, !dbg !99, !tbaa !91, !alias.scope !84, !noalias !85
  %.not.1 = icmp ugt i64 %"new::Array.size_ptr9.copyload.1", 1, !dbg !104
  br i1 %.not.1, label %L42.1, label %L39, !dbg !52

L42.1:                                            ; preds = %L42
  %memoryref_data.1 = load ptr, ptr %"new::Array", align 8, !dbg !106, !tbaa !89, !alias.scope !84, !noalias !85
  %memoryref_data11.1 = getelementptr inbounds nuw i8, ptr %memoryref_data.1, i64 8, !dbg !94
  store ptr %9, ptr %memoryref_data11.1, align 8, !dbg !94, !tbaa !95, !alias.scope !97, !noalias !98
  %__bennett_qalloc8.2 = load atomic ptr, ptr @jlplt___bennett_qalloc_526_got unordered, align 8, !dbg !93
  %10 = call ptr %__bennett_qalloc8.2(i64 0, i64 1), !dbg !93
  %"new::Array.size_ptr9.copyload.2" = load i64, ptr %"new::Array.size_ptr", align 8, !dbg !99, !tbaa !91, !alias.scope !84, !noalias !85
  %.not.2 = icmp ugt i64 %"new::Array.size_ptr9.copyload.2", 2, !dbg !104
  br i1 %.not.2, label %L42.2, label %L39, !dbg !52

L42.2:                                            ; preds = %L42.1
  %memoryref_data.2 = load ptr, ptr %"new::Array", align 8, !dbg !106, !tbaa !89, !alias.scope !84, !noalias !85
  %memoryref_data11.2 = getelementptr inbounds nuw i8, ptr %memoryref_data.2, i64 16, !dbg !94
  store ptr %10, ptr %memoryref_data11.2, align 8, !dbg !94, !tbaa !95, !alias.scope !97, !noalias !98
  %__bennett_qalloc8.3 = load atomic ptr, ptr @jlplt___bennett_qalloc_526_got unordered, align 8, !dbg !93
  %11 = call ptr %__bennett_qalloc8.3(i64 0, i64 1), !dbg !93
  %"new::Array.size_ptr9.copyload.3" = load i64, ptr %"new::Array.size_ptr", align 8, !dbg !99, !tbaa !91, !alias.scope !84, !noalias !85
  %.not.3 = icmp ugt i64 %"new::Array.size_ptr9.copyload.3", 3, !dbg !104
  br i1 %.not.3, label %L75, label %L39, !dbg !52

L75:                                              ; preds = %L42.2
  %memoryref_data.3 = load ptr, ptr %"new::Array", align 8, !dbg !106, !tbaa !89, !alias.scope !84, !noalias !85
  %memoryref_data11.3 = getelementptr inbounds nuw i8, ptr %memoryref_data.3, i64 24, !dbg !94
  store ptr %11, ptr %memoryref_data11.3, align 8, !dbg !94, !tbaa !95, !alias.scope !97, !noalias !98
  %12 = shl i64 %"x::UInt64", 3, !dbg !109
  %memoryref_byteoffset22 = and i64 %12, 24, !dbg !109
  %memoryref_data27 = getelementptr inbounds nuw i8, ptr %memoryref_data.3, i64 %memoryref_byteoffset22, !dbg !109
  %13 = load ptr, ptr %memoryref_data27, align 8, !dbg !109, !tbaa !95, !alias.scope !97, !noalias !98
  %__bennett_gate28 = load atomic ptr, ptr @jlplt___bennett_gate_528_got unordered, align 8, !dbg !115
  store ptr null, ptr %gc_slot_addr_1, align 8
  call void %__bennett_gate28(i32 1, ptr %13, i64 0), !dbg !115
  %__bennett_ctrl_v = load atomic ptr, ptr @jlplt___bennett_ctrl_v_539_got unordered, align 8, !dbg !116
  call void %__bennett_ctrl_v(ptr %2, i64 0, ptr null, i64 8, i32 1, double 2.500000e+00, ptr %2), !dbg !116
  %__bennett_qfree = load atomic ptr, ptr @jlplt___bennett_qfree_541_got unordered, align 8, !dbg !119
  call void %__bennett_qfree(ptr %2), !dbg !119
  %frame.prev52 = load ptr, ptr %frame.prev, align 8, !tbaa !14
  store ptr %frame.prev52, ptr %pgcstack_arg, align 8, !tbaa !14
  ret i64 %value_phi, !dbg !120
}

; Function Attrs: noinline optnone
define nonnull ptr @jfptr_case_B_524(ptr %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") local_unnamed_addr #8 {
top:
  %thread_ptr = call ptr asm "movq %fs:0, $0", "=r"()
  %tls_ppgcstack = getelementptr inbounds i8, ptr %thread_ptr, i64 -8
  %tls_pgcstack = load ptr, ptr %tls_ppgcstack, align 8
  %0 = load ptr, ptr %"args::Any[]", align 8, !tbaa !29, !invariant.load !10, !alias.scope !121, !noalias !122, !nonnull !10, !dereferenceable !123, !align !123
  %.unbox = load i64, ptr %0, align 8, !tbaa !124, !alias.scope !97, !noalias !98
  %1 = call swiftcc i64 @julia_case_B_523(ptr nonnull swiftself "gcstack" %tls_pgcstack, i64 zeroext %.unbox)
  %box_UInt64 = call nonnull align 8 dereferenceable(8) ptr @ijl_box_uint64(i64 zeroext %1) #19
  ret ptr %box_UInt64
}

; Function Attrs: mustprogress nounwind willreturn memory(read, inaccessiblemem: readwrite)
declare nonnull align 8 dereferenceable(8) ptr @ijl_box_uint64(i64 zeroext) local_unnamed_addr #9

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) local_unnamed_addr #10

; Function Attrs: mustprogress nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @julia.gc_alloc_obj(ptr, i64, ptr) local_unnamed_addr #11

; Function Attrs: mustprogress nofree norecurse nosync nounwind speculatable willreturn memory(none)
declare nonnull ptr @julia.pointer_from_objref(ptr) local_unnamed_addr #12

; Function Attrs: mustprogress nofree norecurse nosync nounwind speculatable willreturn memory(none)
declare noundef nonnull ptr @julia.gc_loaded(ptr nocapture noundef nonnull readnone, ptr noundef nonnull readnone) local_unnamed_addr #12

; Function Signature: throw_boundserror(Array{Ptr{Nothing}, 1}, Tuple{Int64})
; Function Attrs: noreturn
declare swiftcc void @j_throw_boundserror_542(ptr nonnull swiftself "gcstack", ptr, ptr nocapture readonly) local_unnamed_addr #13

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #14

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #14

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_small_alloc(ptr, i32, i32, i64) #15

declare noalias nonnull ptr @julia.new_gc_frame(i32)

declare void @julia.push_gc_frame(ptr, i32)

declare ptr @julia.get_gc_frame_slot(ptr, i32)

declare void @julia.pop_gc_frame(ptr)

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @julia.gc_alloc_bytes(ptr, i64, i64) #16

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @ijl_gc_queue_root(ptr) #10

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_big_alloc(ptr, i64, i64) #16

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_alloc_typed(ptr, i64, i64) #16

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i64(ptr nocapture writeonly, i8, i64, i1 immarg) #17

attributes #0 = { "julia.fname"="__bennett_qalloc" "julia.libidx"="0" }
attributes #1 = { "julia.fname"="__bennett_gate" "julia.libidx"="0" }
attributes #2 = { "julia.fname"="__bennett_rot" "julia.libidx"="0" }
attributes #3 = { "julia.fname"="__bennett_measure" "julia.libidx"="0" }
attributes #4 = { "julia.fname"="__bennett_ctrl" "julia.libidx"="0" }
attributes #5 = { "julia.fname"="__bennett_ctrl_v" "julia.libidx"="0" }
attributes #6 = { "julia.fname"="__bennett_qfree" "julia.libidx"="0" }
attributes #7 = { "frame-pointer"="all" "julia.fsig"="case_B(UInt64)" "probe-stack"="inline-asm" }
attributes #8 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #9 = { mustprogress nounwind willreturn memory(read, inaccessiblemem: readwrite) }
attributes #10 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #11 = { mustprogress nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #12 = { mustprogress nofree norecurse nosync nounwind speculatable willreturn memory(none) }
attributes #13 = { noreturn "frame-pointer"="all" "julia.fsig"="throw_boundserror(Array{Ptr{Nothing}, 1}, Tuple{Int64})" "probe-stack"="inline-asm" }
attributes #14 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #15 = { nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #16 = { nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #17 = { nocallback nofree nounwind willreturn memory(argmem: write) }
attributes #18 = { noreturn }
attributes #19 = { nounwind willreturn memory(read, inaccessiblemem: readwrite) }

!llvm.module.flags = !{!0, !1}
!llvm.dbg.cu = !{!2}

!0 = !{i32 2, !"Dwarf Version", i32 4}
!1 = !{i32 2, !"Debug Info Version", i32 3}
!2 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !3, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!3 = !DIFile(filename: "julia", directory: ".")
!4 = distinct !DISubprogram(name: "case_B", linkageName: "julia_case_B_523", scope: null, file: !5, line: 129, type: !6, scopeLine: 129, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !11)
!5 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!6 = !DISubroutineType(types: !7)
!7 = !{!8, !9, !8}
!8 = !DIBasicType(name: "UInt64", size: 64, encoding: DW_ATE_unsigned)
!9 = !DICompositeType(tag: DW_TAG_structure_type, name: "#case_B", align: 8, elements: !10, runtimeLang: DW_LANG_Julia, identifier: "127079337970000")
!10 = !{}
!11 = !{!12, !13}
!12 = !DILocalVariable(name: "#self#", arg: 1, scope: !4, file: !5, line: 129, type: !9)
!13 = !DILocalVariable(name: "x", arg: 2, scope: !4, file: !5, line: 129, type: !8)
!14 = !{!15, !15, i64 0}
!15 = !{!"jtbaa_gcframe", !16, i64 0}
!16 = !{!"jtbaa", !17, i64 0}
!17 = !{!"jtbaa"}
!18 = !DILocation(line: 8, scope: !19, inlinedAt: !22)
!19 = distinct !DISubprogram(name: "RefValue;", linkageName: "RefValue", scope: !20, file: !20, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!20 = !DIFile(filename: "refvalue.jl", directory: ".")
!21 = !DISubroutineType(types: !10)
!22 = !DILocation(line: 10, scope: !19, inlinedAt: !23)
!23 = !DILocation(line: 145, scope: !24, inlinedAt: !26)
!24 = distinct !DISubprogram(name: "Ref;", linkageName: "Ref", scope: !25, file: !25, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!25 = !DIFile(filename: "refpointer.jl", directory: ".")
!26 = !DILocation(line: 84, scope: !27, inlinedAt: !28)
!27 = distinct !DISubprogram(name: "rF_ctrl;", linkageName: "rF_ctrl", scope: !5, file: !5, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!28 = !DILocation(line: 138, scope: !4)
!29 = !{!30, !30, i64 0}
!30 = !{!"jtbaa_const", !16, i64 0}
!31 = !DILocation(line: 129, scope: !4)
!32 = !DILocation(line: 12, scope: !33, inlinedAt: !34)
!33 = distinct !DISubprogram(name: "rB_alloc;", linkageName: "rB_alloc", scope: !5, file: !5, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!34 = !DILocation(line: 130, scope: !4)
!35 = !DILocation(line: 13, scope: !36, inlinedAt: !37)
!36 = distinct !DISubprogram(name: "rB_gate;", linkageName: "rB_gate", scope: !5, file: !5, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!37 = !DILocation(line: 131, scope: !4)
!38 = !DILocation(line: 251, scope: !39, inlinedAt: !41)
!39 = distinct !DISubprogram(name: "Float64;", linkageName: "Float64", scope: !40, file: !40, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!40 = !DIFile(filename: "float.jl", directory: ".")
!41 = !DILocation(line: 132, scope: !4)
!42 = !DILocation(line: 494, scope: !43, inlinedAt: !41)
!43 = distinct !DISubprogram(name: "*;", linkageName: "*", scope: !40, file: !40, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!44 = !DILocation(line: 15, scope: !45, inlinedAt: !46)
!45 = distinct !DISubprogram(name: "rB_rot;", linkageName: "rB_rot", scope: !5, file: !5, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!46 = !DILocation(line: 133, scope: !4)
!47 = !DILocation(line: 14, scope: !48, inlinedAt: !49)
!48 = distinct !DISubprogram(name: "rB_measure;", linkageName: "rB_measure", scope: !5, file: !5, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!49 = !DILocation(line: 135, scope: !4)
!50 = !DILocation(line: 13, scope: !36, inlinedAt: !51)
!51 = !DILocation(line: 136, scope: !4)
!52 = !DILocation(line: 1024, scope: !53, inlinedAt: !55)
!53 = distinct !DISubprogram(name: "_setindex!;", linkageName: "_setindex!", scope: !54, file: !54, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!54 = !DIFile(filename: "array.jl", directory: ".")
!55 = !DILocation(line: 1020, scope: !56, inlinedAt: !57)
!56 = distinct !DISubprogram(name: "setindex!;", linkageName: "setindex!", scope: !54, file: !54, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!57 = !DILocation(line: 140, scope: !4)
!58 = !{!59, !59, i64 0}
!59 = !{!"jtbaa_stack", !16, i64 0}
!60 = !{!61}
!61 = !{!"jnoalias_stack", !62}
!62 = !{!"jnoalias"}
!63 = !{!64, !65, !66, !67}
!64 = !{!"jnoalias_gcframe", !62}
!65 = !{!"jnoalias_data", !62}
!66 = !{!"jnoalias_typemd", !62}
!67 = !{!"jnoalias_const", !62}
!68 = !{!16, !16, i64 0}
!69 = !{!61, !65}
!70 = !{!64, !66, !67}
!71 = !DILocation(line: 86, scope: !27, inlinedAt: !28)
!72 = !DILocation(line: 588, scope: !73, inlinedAt: !75)
!73 = distinct !DISubprogram(name: "GenericMemory;", linkageName: "GenericMemory", scope: !74, file: !74, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!74 = !DIFile(filename: "boot.jl", directory: ".")
!75 = !DILocation(line: 648, scope: !76, inlinedAt: !77)
!76 = distinct !DISubprogram(name: "Array;", linkageName: "Array", scope: !74, file: !74, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!77 = !DILocation(line: 139, scope: !4)
!78 = !{!79, !79, i64 0}
!79 = !{!"jtbaa_tag", !80, i64 0}
!80 = !{!"jtbaa_data", !16, i64 0}
!81 = !{!82, !82, i64 0}
!82 = !{!"jtbaa_memoryptr", !83, i64 0}
!83 = !{!"jtbaa_array", !16, i64 0}
!84 = !{!66}
!85 = !{!64, !61, !65, !67}
!86 = !{!87, !87, i64 0}
!87 = !{!"jtbaa_memorylen", !83, i64 0}
!88 = !DILocation(line: 649, scope: !76, inlinedAt: !77)
!89 = !{!90, !90, i64 0}
!90 = !{!"jtbaa_arrayptr", !83, i64 0}
!91 = !{!92, !92, i64 0}
!92 = !{!"jtbaa_arraysize", !83, i64 0}
!93 = !DILocation(line: 12, scope: !33, inlinedAt: !57)
!94 = !DILocation(line: 1025, scope: !53, inlinedAt: !55)
!95 = !{!96, !96, i64 0}
!96 = !{!"jtbaa_arraybuf", !80, i64 0}
!97 = !{!65}
!98 = !{!64, !61, !66, !67}
!99 = !DILocation(line: 10, scope: !100, inlinedAt: !102)
!100 = distinct !DISubprogram(name: "size;", linkageName: "size", scope: !101, file: !101, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!101 = !DIFile(filename: "essentials.jl", directory: ".")
!102 = !DILocation(line: 11, scope: !103, inlinedAt: !104)
!103 = distinct !DISubprogram(name: "length;", linkageName: "length", scope: !101, file: !101, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!104 = !DILocation(line: 385, scope: !105, inlinedAt: !52)
!105 = distinct !DISubprogram(name: "checkbounds;", linkageName: "checkbounds", scope: !101, file: !101, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!106 = !DILocation(line: 57, scope: !107, inlinedAt: !94)
!107 = distinct !DISubprogram(name: "getproperty;", linkageName: "getproperty", scope: !108, file: !108, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!108 = !DIFile(filename: "Base_compiler.jl", directory: ".")
!109 = !DILocation(line: 975, scope: !110, inlinedAt: !111)
!110 = distinct !DISubprogram(name: "getindex;", linkageName: "getindex", scope: !101, file: !101, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!111 = !DILocation(line: 1366, scope: !112, inlinedAt: !114)
!112 = distinct !DISubprogram(name: "getindex;", linkageName: "getindex", scope: !113, file: !113, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!113 = !DIFile(filename: "abstractarray.jl", directory: ".")
!114 = !DILocation(line: 141, scope: !4)
!115 = !DILocation(line: 13, scope: !36, inlinedAt: !114)
!116 = !DILocation(line: 108, scope: !117, inlinedAt: !118)
!117 = distinct !DISubprogram(name: "rH2_ctrl_v;", linkageName: "rH2_ctrl_v", scope: !5, file: !5, type: !21, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!118 = !DILocation(line: 142, scope: !4)
!119 = !DILocation(line: 143, scope: !4)
!120 = !DILocation(line: 144, scope: !4)
!121 = !{!67}
!122 = !{!64, !61, !65, !66}
!123 = !{i64 8}
!124 = !{!125, !125, i64 0}
!125 = !{!"jtbaa_immut", !126, i64 0}
!126 = !{!"jtbaa_value", !80, i64 0}
