; ModuleID = 'rI_table'
source_filename = "rI_table"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@jl_nothing = external local_unnamed_addr constant ptr
@jlplt___bennett_qalloc_1031_got = external local_unnamed_addr global ptr #0
@jlplt___bennett_gate_1033_got = external local_unnamed_addr global ptr #1

@"+Core.GenericMemory#1028.jit" = private alias ptr, inttoptr (i64 127079420148128 to ptr)
@"+Core.Array#1029.jit" = private alias ptr, inttoptr (i64 127079420430544 to ptr)

; Function Signature: rI_table(UInt64)
define swiftcc void @julia_rI_table_1026(ptr nonnull swiftself "gcstack" %pgcstack_arg, i64 zeroext %"x::UInt64") local_unnamed_addr #2 !dbg !4 {
L20:
  %gcframe1 = alloca [4 x ptr], align 16
  call void @llvm.memset.p0.i64(ptr align 16 %gcframe1, i8 0, i64 32, i1 true)
  store i64 8, ptr %gcframe1, align 8, !tbaa !15
  %frame.prev = getelementptr inbounds nuw i8, ptr %gcframe1, i64 8
  %task.gcstack = load ptr, ptr %pgcstack_arg, align 8
  store ptr %task.gcstack, ptr %frame.prev, align 8, !tbaa !15
  store ptr %gcframe1, ptr %pgcstack_arg, align 8
  %"new::Tuple24" = alloca [1 x i64], align 8
  %ptls_field = getelementptr inbounds nuw i8, ptr %pgcstack_arg, i64 16
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !15
  %0 = getelementptr inbounds nuw i8, ptr %ptls_load, i64 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !19, !invariant.load !9
  fence syncscope("singlethread") seq_cst
  %1 = load volatile i64, ptr %safepoint, align 8
  fence syncscope("singlethread") seq_cst
    #dbg_value(i64 %"x::UInt64", !14, !DIExpression(), !21)
  %ptls_load38 = load ptr, ptr %ptls_field, align 8, !dbg !22, !tbaa !15
  %"Memory{Ptr}[]" = call noalias nonnull align 8 dereferenceable(64) ptr @ijl_gc_small_alloc(ptr %ptls_load38, i32 504, i32 64, i64 127079420148128) #9, !dbg !22
  %"Memory{Ptr}[].tag_addr" = getelementptr inbounds i8, ptr %"Memory{Ptr}[]", i64 -8, !dbg !22
  store atomic i64 127079420148128, ptr %"Memory{Ptr}[].tag_addr" unordered, align 8, !dbg !22, !tbaa !29
  %memory_ptr = getelementptr inbounds nuw i8, ptr %"Memory{Ptr}[]", i64 8, !dbg !22
  %memory_data = getelementptr inbounds nuw i8, ptr %"Memory{Ptr}[]", i64 16, !dbg !22
  store ptr %memory_data, ptr %memory_ptr, align 8, !dbg !22, !tbaa !32, !alias.scope !35, !noalias !38
  store i64 4, ptr %"Memory{Ptr}[]", align 8, !dbg !22, !tbaa !43, !alias.scope !35, !noalias !38
  %gc_slot_addr_0 = getelementptr inbounds nuw i8, ptr %gcframe1, i64 16
  store ptr %"Memory{Ptr}[]", ptr %gc_slot_addr_0, align 8
  %"new::Array" = call noalias nonnull align 8 dereferenceable(32) ptr @ijl_gc_small_alloc(ptr %ptls_load38, i32 408, i32 32, i64 127079420430544) #9, !dbg !45
  %"new::Array.tag_addr" = getelementptr inbounds i8, ptr %"new::Array", i64 -8, !dbg !45
  store atomic i64 127079420430544, ptr %"new::Array.tag_addr" unordered, align 8, !dbg !45, !tbaa !29
  %2 = getelementptr inbounds nuw i8, ptr %"new::Array", i64 8, !dbg !45
  store ptr %memory_data, ptr %"new::Array", align 8, !dbg !45, !tbaa !46, !alias.scope !35, !noalias !38
  store ptr %"Memory{Ptr}[]", ptr %2, align 8, !dbg !45, !tbaa !46, !alias.scope !35, !noalias !38
  %"new::Array.size_ptr" = getelementptr inbounds nuw i8, ptr %"new::Array", i64 16, !dbg !45
  store i64 4, ptr %"new::Array.size_ptr", align 8, !dbg !45, !tbaa !48, !alias.scope !35, !noalias !38
  %__bennett_qalloc = load atomic ptr, ptr @jlplt___bennett_qalloc_1031_got unordered, align 8, !dbg !50
  %gc_slot_addr_1 = getelementptr inbounds nuw i8, ptr %gcframe1, i64 24
  store ptr %"new::Array", ptr %gc_slot_addr_1, align 8
  %3 = call ptr %__bennett_qalloc(i64 0, i64 1), !dbg !50
  store ptr %3, ptr %memory_data, align 8, !dbg !53, !tbaa !58, !alias.scope !60, !noalias !61
  %__bennett_qalloc.1 = load atomic ptr, ptr @jlplt___bennett_qalloc_1031_got unordered, align 8, !dbg !50
  store ptr null, ptr %gc_slot_addr_0, align 8
  %4 = call ptr %__bennett_qalloc.1(i64 0, i64 1), !dbg !50
  %"new::Array.size_ptr5.copyload.1" = load i64, ptr %"new::Array.size_ptr", align 8, !dbg !62, !tbaa !48, !alias.scope !35, !noalias !38
  %.not.1 = icmp ugt i64 %"new::Array.size_ptr5.copyload.1", 1, !dbg !67
  br i1 %.not.1, label %L20.1, label %L17, !dbg !69

L17:                                              ; preds = %L20.2, %L20.1, %L20
  %value_phi.lcssa = phi i64 [ 2, %L20 ], [ 3, %L20.1 ], [ 4, %L20.2 ]
  store i64 %value_phi.lcssa, ptr %"new::Tuple24", align 8, !dbg !69, !tbaa !70, !alias.scope !72, !noalias !73
  call swiftcc void @j_throw_boundserror_1034(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr nonnull %"new::Array", ptr nocapture nonnull readonly %"new::Tuple24") #12, !dbg !69
  unreachable, !dbg !69

L20.1:                                            ; preds = %L20
  %memoryref_data.1 = load ptr, ptr %"new::Array", align 8, !dbg !74, !tbaa !46, !alias.scope !35, !noalias !38
  %memoryref_data7.1 = getelementptr inbounds nuw i8, ptr %memoryref_data.1, i64 8, !dbg !53
  store ptr %4, ptr %memoryref_data7.1, align 8, !dbg !53, !tbaa !58, !alias.scope !60, !noalias !61
  %__bennett_qalloc.2 = load atomic ptr, ptr @jlplt___bennett_qalloc_1031_got unordered, align 8, !dbg !50
  %5 = call ptr %__bennett_qalloc.2(i64 0, i64 1), !dbg !50
  %"new::Array.size_ptr5.copyload.2" = load i64, ptr %"new::Array.size_ptr", align 8, !dbg !62, !tbaa !48, !alias.scope !35, !noalias !38
  %.not.2 = icmp ugt i64 %"new::Array.size_ptr5.copyload.2", 2, !dbg !67
  br i1 %.not.2, label %L20.2, label %L17, !dbg !69

L20.2:                                            ; preds = %L20.1
  %memoryref_data.2 = load ptr, ptr %"new::Array", align 8, !dbg !74, !tbaa !46, !alias.scope !35, !noalias !38
  %memoryref_data7.2 = getelementptr inbounds nuw i8, ptr %memoryref_data.2, i64 16, !dbg !53
  store ptr %5, ptr %memoryref_data7.2, align 8, !dbg !53, !tbaa !58, !alias.scope !60, !noalias !61
  %__bennett_qalloc.3 = load atomic ptr, ptr @jlplt___bennett_qalloc_1031_got unordered, align 8, !dbg !50
  %6 = call ptr %__bennett_qalloc.3(i64 0, i64 1), !dbg !50
  %"new::Array.size_ptr5.copyload.3" = load i64, ptr %"new::Array.size_ptr", align 8, !dbg !62, !tbaa !48, !alias.scope !35, !noalias !38
  %.not.3 = icmp ugt i64 %"new::Array.size_ptr5.copyload.3", 3, !dbg !67
  br i1 %.not.3, label %L53, label %L17, !dbg !69

L53:                                              ; preds = %L20.2
  %memoryref_data.3 = load ptr, ptr %"new::Array", align 8, !dbg !74, !tbaa !46, !alias.scope !35, !noalias !38
  %memoryref_data7.3 = getelementptr inbounds nuw i8, ptr %memoryref_data.3, i64 24, !dbg !53
  store ptr %6, ptr %memoryref_data7.3, align 8, !dbg !53, !tbaa !58, !alias.scope !60, !noalias !61
  %7 = shl i64 %"x::UInt64", 3, !dbg !77
  %memoryref_byteoffset18 = and i64 %7, 24, !dbg !77
  %memoryref_data23 = getelementptr inbounds nuw i8, ptr %memoryref_data.3, i64 %memoryref_byteoffset18, !dbg !77
  %8 = load ptr, ptr %memoryref_data23, align 8, !dbg !77, !tbaa !58, !alias.scope !60, !noalias !61
  %__bennett_gate = load atomic ptr, ptr @jlplt___bennett_gate_1033_got unordered, align 8, !dbg !83
  store ptr null, ptr %gc_slot_addr_1, align 8
  call void %__bennett_gate(i32 1, ptr %8, i64 0), !dbg !83
  %frame.prev45 = load ptr, ptr %frame.prev, align 8, !tbaa !15
  store ptr %frame.prev45, ptr %pgcstack_arg, align 8, !tbaa !15
  ret void, !dbg !85
}

; Function Attrs: noinline optnone
define nonnull ptr @jfptr_rI_table_1027(ptr %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") local_unnamed_addr #3 {
top:
  %thread_ptr = call ptr asm "movq %fs:0, $0", "=r"()
  %tls_ppgcstack = getelementptr inbounds i8, ptr %thread_ptr, i64 -8
  %tls_pgcstack = load ptr, ptr %tls_ppgcstack, align 8
  %0 = load ptr, ptr %"args::Any[]", align 8, !tbaa !19, !invariant.load !9, !alias.scope !86, !noalias !87, !nonnull !9, !dereferenceable !88, !align !88
  %.unbox = load i64, ptr %0, align 8, !tbaa !89, !alias.scope !60, !noalias !61
  call swiftcc void @julia_rI_table_1026(ptr nonnull swiftself "gcstack" %tls_pgcstack, i64 zeroext %.unbox)
  %jl_nothing = load ptr, ptr @jl_nothing, align 8, !tbaa !19, !invariant.load !9, !alias.scope !86, !noalias !87, !nonnull !9
  ret ptr %jl_nothing
}

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) local_unnamed_addr #4

; Function Attrs: mustprogress nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @julia.gc_alloc_obj(ptr, i64, ptr) local_unnamed_addr #5

; Function Attrs: mustprogress nofree norecurse nosync nounwind speculatable willreturn memory(none)
declare nonnull ptr @julia.pointer_from_objref(ptr) local_unnamed_addr #6

; Function Attrs: mustprogress nofree norecurse nosync nounwind speculatable willreturn memory(none)
declare noundef nonnull ptr @julia.gc_loaded(ptr nocapture noundef nonnull readnone, ptr noundef nonnull readnone) local_unnamed_addr #6

; Function Signature: throw_boundserror(Array{Ptr{Nothing}, 1}, Tuple{Int64})
; Function Attrs: noreturn
declare swiftcc void @j_throw_boundserror_1034(ptr nonnull swiftself "gcstack", ptr, ptr nocapture readonly) local_unnamed_addr #7

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #8

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #8

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_small_alloc(ptr, i32, i32, i64) #9

declare noalias nonnull ptr @julia.new_gc_frame(i32)

declare void @julia.push_gc_frame(ptr, i32)

declare ptr @julia.get_gc_frame_slot(ptr, i32)

declare void @julia.pop_gc_frame(ptr)

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @julia.gc_alloc_bytes(ptr, i64, i64) #10

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @ijl_gc_queue_root(ptr) #4

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_big_alloc(ptr, i64, i64) #10

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr @ijl_gc_alloc_typed(ptr, i64, i64) #10

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i64(ptr nocapture writeonly, i8, i64, i1 immarg) #11

attributes #0 = { "julia.fname"="__bennett_qalloc" "julia.libidx"="0" }
attributes #1 = { "julia.fname"="__bennett_gate" "julia.libidx"="0" }
attributes #2 = { "frame-pointer"="all" "julia.fsig"="rI_table(UInt64)" "probe-stack"="inline-asm" }
attributes #3 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #4 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #5 = { mustprogress nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #6 = { mustprogress nofree norecurse nosync nounwind speculatable willreturn memory(none) }
attributes #7 = { noreturn "frame-pointer"="all" "julia.fsig"="throw_boundserror(Array{Ptr{Nothing}, 1}, Tuple{Int64})" "probe-stack"="inline-asm" }
attributes #8 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #9 = { nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #10 = { nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #11 = { nocallback nofree nounwind willreturn memory(argmem: write) }
attributes #12 = { noreturn }

!llvm.module.flags = !{!0, !1}
!llvm.dbg.cu = !{!2}

!0 = !{i32 2, !"Dwarf Version", i32 4}
!1 = !{i32 2, !"Debug Info Version", i32 3}
!2 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !3, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!3 = !DIFile(filename: "julia", directory: ".")
!4 = distinct !DISubprogram(name: "rI_table", linkageName: "julia_rI_table_1026", scope: null, file: !5, line: 121, type: !6, scopeLine: 121, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !12)
!5 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!6 = !DISubroutineType(types: !7)
!7 = !{!8, !10, !11}
!8 = !DICompositeType(tag: DW_TAG_structure_type, name: "Nothing", align: 8, elements: !9, runtimeLang: DW_LANG_Julia, identifier: "127079415932560")
!9 = !{}
!10 = !DICompositeType(tag: DW_TAG_structure_type, name: "#rI_table", align: 8, elements: !9, runtimeLang: DW_LANG_Julia, identifier: "127079337969232")
!11 = !DIBasicType(name: "UInt64", size: 64, encoding: DW_ATE_unsigned)
!12 = !{!13, !14}
!13 = !DILocalVariable(name: "#self#", arg: 1, scope: !4, file: !5, line: 121, type: !10)
!14 = !DILocalVariable(name: "x", arg: 2, scope: !4, file: !5, line: 121, type: !11)
!15 = !{!16, !16, i64 0}
!16 = !{!"jtbaa_gcframe", !17, i64 0}
!17 = !{!"jtbaa", !18, i64 0}
!18 = !{!"jtbaa"}
!19 = !{!20, !20, i64 0}
!20 = !{!"jtbaa_const", !17, i64 0}
!21 = !DILocation(line: 121, scope: !4)
!22 = !DILocation(line: 588, scope: !23, inlinedAt: !26)
!23 = distinct !DISubprogram(name: "GenericMemory;", linkageName: "GenericMemory", scope: !24, file: !24, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!24 = !DIFile(filename: "boot.jl", directory: ".")
!25 = !DISubroutineType(types: !9)
!26 = !DILocation(line: 648, scope: !27, inlinedAt: !28)
!27 = distinct !DISubprogram(name: "Array;", linkageName: "Array", scope: !24, file: !24, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!28 = !DILocation(line: 122, scope: !4)
!29 = !{!30, !30, i64 0}
!30 = !{!"jtbaa_tag", !31, i64 0}
!31 = !{!"jtbaa_data", !17, i64 0}
!32 = !{!33, !33, i64 0}
!33 = !{!"jtbaa_memoryptr", !34, i64 0}
!34 = !{!"jtbaa_array", !17, i64 0}
!35 = !{!36}
!36 = !{!"jnoalias_typemd", !37}
!37 = !{!"jnoalias"}
!38 = !{!39, !40, !41, !42}
!39 = !{!"jnoalias_gcframe", !37}
!40 = !{!"jnoalias_stack", !37}
!41 = !{!"jnoalias_data", !37}
!42 = !{!"jnoalias_const", !37}
!43 = !{!44, !44, i64 0}
!44 = !{!"jtbaa_memorylen", !34, i64 0}
!45 = !DILocation(line: 649, scope: !27, inlinedAt: !28)
!46 = !{!47, !47, i64 0}
!47 = !{!"jtbaa_arrayptr", !34, i64 0}
!48 = !{!49, !49, i64 0}
!49 = !{!"jtbaa_arraysize", !34, i64 0}
!50 = !DILocation(line: 12, scope: !51, inlinedAt: !52)
!51 = distinct !DISubprogram(name: "rB_alloc;", linkageName: "rB_alloc", scope: !5, file: !5, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!52 = !DILocation(line: 123, scope: !4)
!53 = !DILocation(line: 1025, scope: !54, inlinedAt: !56)
!54 = distinct !DISubprogram(name: "_setindex!;", linkageName: "_setindex!", scope: !55, file: !55, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!55 = !DIFile(filename: "array.jl", directory: ".")
!56 = !DILocation(line: 1020, scope: !57, inlinedAt: !52)
!57 = distinct !DISubprogram(name: "setindex!;", linkageName: "setindex!", scope: !55, file: !55, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!58 = !{!59, !59, i64 0}
!59 = !{!"jtbaa_arraybuf", !31, i64 0}
!60 = !{!41}
!61 = !{!39, !40, !36, !42}
!62 = !DILocation(line: 10, scope: !63, inlinedAt: !65)
!63 = distinct !DISubprogram(name: "size;", linkageName: "size", scope: !64, file: !64, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!64 = !DIFile(filename: "essentials.jl", directory: ".")
!65 = !DILocation(line: 11, scope: !66, inlinedAt: !67)
!66 = distinct !DISubprogram(name: "length;", linkageName: "length", scope: !64, file: !64, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!67 = !DILocation(line: 385, scope: !68, inlinedAt: !69)
!68 = distinct !DISubprogram(name: "checkbounds;", linkageName: "checkbounds", scope: !64, file: !64, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!69 = !DILocation(line: 1024, scope: !54, inlinedAt: !56)
!70 = !{!71, !71, i64 0}
!71 = !{!"jtbaa_stack", !17, i64 0}
!72 = !{!40}
!73 = !{!39, !41, !36, !42}
!74 = !DILocation(line: 57, scope: !75, inlinedAt: !53)
!75 = distinct !DISubprogram(name: "getproperty;", linkageName: "getproperty", scope: !76, file: !76, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!76 = !DIFile(filename: "Base_compiler.jl", directory: ".")
!77 = !DILocation(line: 975, scope: !78, inlinedAt: !79)
!78 = distinct !DISubprogram(name: "getindex;", linkageName: "getindex", scope: !64, file: !64, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!79 = !DILocation(line: 1366, scope: !80, inlinedAt: !82)
!80 = distinct !DISubprogram(name: "getindex;", linkageName: "getindex", scope: !81, file: !81, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!81 = !DIFile(filename: "abstractarray.jl", directory: ".")
!82 = !DILocation(line: 124, scope: !4)
!83 = !DILocation(line: 13, scope: !84, inlinedAt: !82)
!84 = distinct !DISubprogram(name: "rB_gate;", linkageName: "rB_gate", scope: !5, file: !5, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!85 = !DILocation(line: 125, scope: !4)
!86 = !{!42}
!87 = !{!39, !40, !41, !36}
!88 = !{i64 8}
!89 = !{!90, !90, i64 0}
!90 = !{!"jtbaa_immut", !91, i64 0}
!91 = !{!"jtbaa_value", !31, i64 0}
