; ModuleID = 'rI_table'
source_filename = "rI_table"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128-ni:10:11:12:13"
target triple = "x86_64-unknown-linux-gnu"

@jl_nothing = external constant ptr
@"+Core.GenericMemory#1019" = private unnamed_addr constant ptr @"+Core.GenericMemory#1019.jit", !julia.constgv !0
@"+Core.Array#1020" = private unnamed_addr constant ptr @"+Core.Array#1020.jit", !julia.constgv !0
@"_j_const#1" = private unnamed_addr constant [1 x i64] [i64 4], align 8
@jlplt___bennett_qalloc_1022_got = external global ptr #0
@jlplt___bennett_gate_1024_got = external global ptr #1

@"+Core.GenericMemory#1019.jit" = private alias ptr, inttoptr (i64 127079420148128 to ptr)
@"+Core.Array#1020.jit" = private alias ptr, inttoptr (i64 127079420430544 to ptr)

; Function Signature: rI_table(UInt64)
define swiftcc void @julia_rI_table_1017(ptr nonnull swiftself "gcstack" %pgcstack_arg, i64 zeroext %"x::UInt64") #2 !dbg !5 {
top:
  %"new::Array.size" = alloca i64, align 8
  %"new::Array.size12" = alloca i64, align 8
  %"new::Tuple" = alloca [1 x i64], align 8
  %"new::Tuple24" = alloca [1 x i64], align 8
  %current_task = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152
  %ptls_field = getelementptr inbounds i8, ptr %current_task, i32 168
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !15
  %0 = getelementptr inbounds i8, ptr %ptls_load, i32 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !19, !invariant.load !0
  fence syncscope("singlethread") seq_cst
  call void @julia.safepoint(ptr %safepoint)
  fence syncscope("singlethread") seq_cst
    #dbg_value(i64 %"x::UInt64", !14, !DIExpression(), !21)
  %"+Core.GenericMemory#1019" = load ptr, ptr @"+Core.GenericMemory#1019", align 8, !dbg !22, !tbaa !19, !invariant.load !0, !alias.scope !29, !noalias !32, !nonnull !0, !dereferenceable !37, !align !38
  %current_task1 = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152, !dbg !22
  %1 = addrspacecast ptr %"+Core.GenericMemory#1019" to ptr addrspace(10), !dbg !22
  %"Memory{Ptr}[]" = call noalias nonnull align 16 dereferenceable(48) ptr addrspace(10) @julia.gc_alloc_obj(ptr %current_task1, i64 48, ptr addrspace(10) %1) #5, !dbg !22
  %2 = addrspacecast ptr addrspace(10) %"Memory{Ptr}[]" to ptr addrspace(11), !dbg !22
  %memory_ptr = getelementptr inbounds nuw { i64, ptr }, ptr addrspace(11) %2, i32 0, i32 1, !dbg !22
  %3 = addrspacecast ptr addrspace(10) %"Memory{Ptr}[]" to ptr addrspace(11), !dbg !22
  %4 = call nonnull ptr @julia.pointer_from_objref(ptr addrspace(11) %3) #6, !dbg !22
  %memory_data = getelementptr inbounds i8, ptr %4, i32 16, !dbg !22
  store ptr %memory_data, ptr addrspace(11) %memory_ptr, align 8, !dbg !22, !tbaa !39, !alias.scope !42, !noalias !43
  %5 = addrspacecast ptr addrspace(10) %"Memory{Ptr}[]" to ptr addrspace(11), !dbg !22
  %6 = getelementptr inbounds nuw { i64, ptr }, ptr addrspace(11) %5, i32 0, i32 0, !dbg !22
  store i64 4, ptr addrspace(11) %6, align 8, !dbg !22, !tbaa !44, !alias.scope !42, !noalias !43
  %7 = addrspacecast ptr addrspace(10) %"Memory{Ptr}[]" to ptr addrspace(11), !dbg !46
  %memory_data_ptr = getelementptr inbounds nuw { i64, ptr }, ptr addrspace(11) %7, i32 0, i32 1, !dbg !46
  %memory_data2 = load ptr, ptr addrspace(11) %memory_data_ptr, align 8, !dbg !46, !tbaa !39, !alias.scope !42, !noalias !43, !nonnull !0
  %8 = insertvalue { ptr, ptr addrspace(10) } zeroinitializer, ptr %memory_data2, 0, !dbg !46
  %memory_ref = insertvalue { ptr, ptr addrspace(10) } %8, ptr addrspace(10) %"Memory{Ptr}[]", 1, !dbg !46
  %"+Core.Array#1020" = load ptr, ptr @"+Core.Array#1020", align 8, !dbg !48, !tbaa !19, !invariant.load !0, !alias.scope !29, !noalias !32, !nonnull !0, !dereferenceable !37, !align !38
  %Array = ptrtoint ptr %"+Core.Array#1020" to i64, !dbg !48
  %9 = inttoptr i64 %Array to ptr, !dbg !48
  %current_task3 = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152, !dbg !48
  %10 = addrspacecast ptr %9 to ptr addrspace(10), !dbg !48
  %"new::Array" = call noalias nonnull align 8 dereferenceable(24) ptr addrspace(10) @julia.gc_alloc_obj(ptr %current_task3, i64 24, ptr addrspace(10) %10) #9, !dbg !48
  %11 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !48
  %12 = getelementptr inbounds i8, ptr addrspace(11) %11, i32 8, !dbg !48
  store ptr addrspace(10) null, ptr addrspace(11) %12, align 8, !dbg !48, !tbaa !49, !alias.scope !42, !noalias !43
  %13 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !48
  store { ptr, ptr addrspace(10) } %memory_ref, ptr addrspace(11) %13, align 8, !dbg !48, !tbaa !50, !alias.scope !42, !noalias !43
  %14 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !48
  %"new::Array.size_ptr" = getelementptr inbounds i8, ptr addrspace(11) %14, i32 16, !dbg !48
  %"_j_const#1.copyload" = load i64, ptr @"_j_const#1", align 8, !dbg !48, !tbaa !52, !alias.scope !56, !noalias !57
  store i64 %"_j_const#1.copyload", ptr addrspace(11) %"new::Array.size_ptr", align 8, !dbg !48, !tbaa !58, !alias.scope !42, !noalias !43
  br label %L4, !dbg !48

L4:                                               ; preds = %L35, %top
  %value_phi = phi i64 [ 1, %top ], [ %value_phi8, %L35 ]
  %value_phi4 = phi i64 [ 1, %top ], [ %value_phi9, %L35 ]
  %__bennett_qalloc = load atomic ptr, ptr @jlplt___bennett_qalloc_1022_got unordered, align 8, !dbg !60
  %15 = call ptr %__bennett_qalloc(i64 0, i64 1), !dbg !60
  br i1 false, label %L20, label %L9, !dbg !63

L9:                                               ; preds = %L4
  %16 = sub i64 %value_phi, 1, !dbg !68
  %17 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !71
  %"new::Array.size_ptr5" = getelementptr inbounds i8, ptr addrspace(11) %17, i32 16, !dbg !71
  %"new::Array.size_ptr5.copyload" = load i64, ptr addrspace(11) %"new::Array.size_ptr5", align 8, !dbg !71, !tbaa !58, !alias.scope !42, !noalias !43
  store i64 %"new::Array.size_ptr5.copyload", ptr %"new::Array.size", align 8, !dbg !71, !tbaa !75, !alias.scope !77, !noalias !78
  %bitcast = load i64, ptr %"new::Array.size", align 8, !dbg !68, !tbaa !75, !alias.scope !77, !noalias !78
  %18 = icmp ult i64 %16, %bitcast, !dbg !68
  %19 = xor i1 %18, true, !dbg !63
  br i1 %19, label %L17, label %L16, !dbg !63

L16:                                              ; preds = %L9
  br label %L20, !dbg !63

L17:                                              ; preds = %L9
  %20 = getelementptr inbounds i8, ptr %"new::Tuple24", i32 0, !dbg !63
  store i64 %value_phi, ptr %20, align 8, !dbg !63, !tbaa !75, !alias.scope !77, !noalias !78
  %21 = addrspacecast ptr %"new::Tuple24" to ptr addrspace(11), !dbg !63
  call swiftcc void @j_throw_boundserror_1025(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr addrspace(10) %"new::Array", ptr addrspace(11) nocapture readonly %21) #10, !dbg !63
  call void @llvm.trap(), !dbg !63
  unreachable, !dbg !63

L20:                                              ; preds = %L16, %L4
  %22 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !79
  %23 = getelementptr inbounds nuw { ptr, ptr addrspace(10) }, ptr addrspace(11) %22, i32 0, i32 0, !dbg !79
  %memoryref_data = load ptr, ptr addrspace(11) %23, align 8, !dbg !79, !tbaa !50, !alias.scope !42, !noalias !43
  %24 = getelementptr inbounds nuw { ptr, ptr addrspace(10) }, ptr addrspace(11) %22, i32 0, i32 1, !dbg !79
  %memoryref_mem = load ptr addrspace(10), ptr addrspace(11) %24, align 8, !dbg !79, !tbaa !50, !alias.scope !42, !noalias !43, !dereferenceable_or_null !38, !align !83
  %25 = insertvalue { ptr, ptr addrspace(10) } zeroinitializer, ptr %memoryref_data, 0, !dbg !79
  %"new::Array.ref" = insertvalue { ptr, ptr addrspace(10) } %25, ptr addrspace(10) %memoryref_mem, 1, !dbg !79
  %memoryref_offset = sub i64 %value_phi, 1, !dbg !82
  %memoryref_byteoffset = mul i64 %memoryref_offset, 8, !dbg !82
  %memoryref_data_byteoffset = getelementptr i8, ptr %memoryref_data, i64 %memoryref_byteoffset, !dbg !82
  %26 = insertvalue { ptr, ptr addrspace(10) } zeroinitializer, ptr %memoryref_data_byteoffset, 0, !dbg !82
  %memory_ref6 = insertvalue { ptr, ptr addrspace(10) } %26, ptr addrspace(10) %memoryref_mem, 1, !dbg !82
  %27 = addrspacecast ptr addrspace(10) %memoryref_mem to ptr addrspace(11), !dbg !82
  %28 = getelementptr inbounds nuw { i64, ptr }, ptr addrspace(11) %27, i32 0, i32 0, !dbg !82
  %memory_len = load i64, ptr addrspace(11) %28, align 8, !dbg !82, !tbaa !44, !range !84, !alias.scope !42, !noalias !43
  %29 = call ptr addrspace(13) @julia.gc_loaded(ptr addrspace(10) %memoryref_mem, ptr %memoryref_data), !dbg !82
  %memoryref_data7 = getelementptr inbounds i8, ptr addrspace(13) %29, i64 %memoryref_byteoffset, !dbg !82
  store ptr %15, ptr addrspace(13) %memoryref_data7, align 8, !dbg !82, !tbaa !85, !alias.scope !56, !noalias !57
  br label %L24, !dbg !87

L24:                                              ; preds = %L20
  br label %L25, !dbg !66

L25:                                              ; preds = %L24
  %30 = icmp eq i64 %value_phi4, 4, !dbg !88
  %31 = xor i1 %30, true, !dbg !91
  br i1 %31, label %L28, label %L27, !dbg !91

L27:                                              ; preds = %L25
  br label %L30, !dbg !91

L28:                                              ; preds = %L25
  %32 = add i64 %value_phi4, 1, !dbg !94
  br label %L30, !dbg !91

L30:                                              ; preds = %L28, %L27
  %value_phi8 = phi i64 [ %32, %L28 ], [ undef, %L27 ]
  %value_phi9 = phi i64 [ %32, %L28 ], [ undef, %L27 ]
  %value_phi10 = phi i8 [ 1, %L27 ], [ 0, %L28 ]
  %33 = trunc i8 %value_phi10 to i1, !dbg !62
  %34 = xor i1 %33, true, !dbg !62
  %35 = xor i1 %34, true, !dbg !62
  br i1 %35, label %L36, label %L35, !dbg !62

L35:                                              ; preds = %L30
  br label %L4, !dbg !62

L36:                                              ; preds = %L30
  %36 = and i64 %"x::UInt64", 3, !dbg !98
  %37 = add i64 %36, 1, !dbg !102
  br i1 false, label %L53, label %L41, !dbg !104

L41:                                              ; preds = %L36
  %38 = sub i64 %37, 1, !dbg !109
  %39 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !111
  %"new::Array.size_ptr11" = getelementptr inbounds i8, ptr addrspace(11) %39, i32 16, !dbg !111
  %"new::Array.size_ptr11.copyload" = load i64, ptr addrspace(11) %"new::Array.size_ptr11", align 8, !dbg !111, !tbaa !58, !alias.scope !42, !noalias !43
  store i64 %"new::Array.size_ptr11.copyload", ptr %"new::Array.size12", align 8, !dbg !111, !tbaa !75, !alias.scope !77, !noalias !78
  %bitcast13 = load i64, ptr %"new::Array.size12", align 8, !dbg !109, !tbaa !75, !alias.scope !77, !noalias !78
  %40 = icmp ult i64 %38, %bitcast13, !dbg !109
  %41 = xor i1 %40, true, !dbg !110
  br i1 %41, label %L49, label %L48, !dbg !110

L48:                                              ; preds = %L41
  br label %L52, !dbg !110

L49:                                              ; preds = %L41
  %42 = getelementptr inbounds i8, ptr %"new::Tuple", i32 0, !dbg !110
  store i64 %37, ptr %42, align 8, !dbg !110, !tbaa !75, !alias.scope !77, !noalias !78
  %43 = addrspacecast ptr %"new::Tuple" to ptr addrspace(11), !dbg !110
  call swiftcc void @j_throw_boundserror_1025(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr addrspace(10) %"new::Array", ptr addrspace(11) nocapture readonly %43) #10, !dbg !110
  call void @llvm.trap(), !dbg !110
  unreachable, !dbg !110

L52:                                              ; preds = %L48
  br label %L53, !dbg !110

L53:                                              ; preds = %L52, %L36
  %44 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !113
  %45 = getelementptr inbounds nuw { ptr, ptr addrspace(10) }, ptr addrspace(11) %44, i32 0, i32 0, !dbg !113
  %memoryref_data15 = load ptr, ptr addrspace(11) %45, align 8, !dbg !113, !tbaa !50, !alias.scope !42, !noalias !43
  %46 = getelementptr inbounds nuw { ptr, ptr addrspace(10) }, ptr addrspace(11) %44, i32 0, i32 1, !dbg !113
  %memoryref_mem21 = load ptr addrspace(10), ptr addrspace(11) %46, align 8, !dbg !113, !tbaa !50, !alias.scope !42, !noalias !43, !dereferenceable_or_null !38, !align !83
  %47 = insertvalue { ptr, ptr addrspace(10) } zeroinitializer, ptr %memoryref_data15, 0, !dbg !113
  %"new::Array.ref14" = insertvalue { ptr, ptr addrspace(10) } %47, ptr addrspace(10) %memoryref_mem21, 1, !dbg !113
  %memoryref_offset17 = sub i64 %37, 1, !dbg !113
  %memoryref_byteoffset18 = mul i64 %memoryref_offset17, 8, !dbg !113
  %memoryref_data_byteoffset19 = getelementptr i8, ptr %memoryref_data15, i64 %memoryref_byteoffset18, !dbg !113
  %48 = insertvalue { ptr, ptr addrspace(10) } zeroinitializer, ptr %memoryref_data_byteoffset19, 0, !dbg !113
  %memory_ref20 = insertvalue { ptr, ptr addrspace(10) } %48, ptr addrspace(10) %memoryref_mem21, 1, !dbg !113
  %49 = addrspacecast ptr addrspace(10) %memoryref_mem21 to ptr addrspace(11), !dbg !113
  %50 = getelementptr inbounds nuw { i64, ptr }, ptr addrspace(11) %49, i32 0, i32 0, !dbg !113
  %memory_len22 = load i64, ptr addrspace(11) %50, align 8, !dbg !113, !tbaa !44, !range !84, !alias.scope !42, !noalias !43
  %51 = call ptr addrspace(13) @julia.gc_loaded(ptr addrspace(10) %memoryref_mem21, ptr %memoryref_data15), !dbg !113
  %memoryref_data23 = getelementptr inbounds i8, ptr addrspace(13) %51, i64 %memoryref_byteoffset18, !dbg !113
  %52 = load ptr, ptr addrspace(13) %memoryref_data23, align 8, !dbg !113, !tbaa !85, !alias.scope !56, !noalias !57
  br label %L57, !dbg !113

L57:                                              ; preds = %L53
  br label %L58, !dbg !113

L58:                                              ; preds = %L57
  %__bennett_gate = load atomic ptr, ptr @jlplt___bennett_gate_1024_got unordered, align 8, !dbg !114
  call void %__bennett_gate(i32 1, ptr %52, i64 0), !dbg !114
  ret void, !dbg !116

after_noret:                                      ; No predecessors!
  call void @llvm.trap(), !dbg !110
  unreachable, !dbg !110

after_noret25:                                    ; No predecessors!
  call void @llvm.trap(), !dbg !63
  unreachable, !dbg !63
}

; Function Attrs: noinline optnone
define nonnull ptr addrspace(10) @jfptr_rI_table_1018(ptr addrspace(10) %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") #3 {
top:
  %pgcstack = call ptr @julia.get_pgcstack()
  %0 = load ptr addrspace(10), ptr %"args::Any[]", align 8, !tbaa !19, !invariant.load !0, !alias.scope !29, !noalias !32, !nonnull !0, !dereferenceable !83, !align !83
  %.unbox = load i64, ptr addrspace(10) %0, align 8, !tbaa !52, !alias.scope !56, !noalias !57
  call swiftcc void @julia_rI_table_1017(ptr nonnull swiftself "gcstack" %pgcstack, i64 zeroext %.unbox)
  %jl_nothing = load ptr, ptr @jl_nothing, align 8, !tbaa !19, !invariant.load !0, !alias.scope !29, !noalias !32, !nonnull !0
  %1 = addrspacecast ptr %jl_nothing to ptr addrspace(10)
  ret ptr addrspace(10) %1
}

declare ptr @julia.get_pgcstack()

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) #4

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr addrspace(10) @julia.gc_alloc_obj(ptr, i64, ptr addrspace(10)) #5

; Function Attrs: norecurse nosync nounwind speculatable willreturn memory(none)
declare nonnull ptr @julia.pointer_from_objref(ptr addrspace(11)) #6

; Function Attrs: norecurse nosync nounwind speculatable willreturn memory(none)
declare noundef nonnull ptr addrspace(13) @julia.gc_loaded(ptr addrspace(10) nocapture noundef nonnull readnone, ptr noundef nonnull readnone) #6

; Function Signature: throw_boundserror(Array{Ptr{Nothing}, 1}, Tuple{Int64})
; Function Attrs: noreturn
declare swiftcc void @j_throw_boundserror_1025(ptr nonnull swiftself "gcstack", ptr addrspace(10), ptr addrspace(11) nocapture readonly) #7

; Function Attrs: cold noreturn nounwind memory(inaccessiblemem: write)
declare void @llvm.trap() #8

attributes #0 = { "julia.fname"="__bennett_qalloc" "julia.libidx"="0" }
attributes #1 = { "julia.fname"="__bennett_gate" "julia.libidx"="0" }
attributes #2 = { "frame-pointer"="all" "julia.fsig"="rI_table(UInt64)" "probe-stack"="inline-asm" }
attributes #3 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #4 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #5 = { nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #6 = { norecurse nosync nounwind speculatable willreturn memory(none) }
attributes #7 = { noreturn "frame-pointer"="all" "julia.fsig"="throw_boundserror(Array{Ptr{Nothing}, 1}, Tuple{Int64})" "probe-stack"="inline-asm" }
attributes #8 = { cold noreturn nounwind memory(inaccessiblemem: write) }
attributes #9 = { nounwind willreturn allockind("alloc,uninitialized") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #10 = { noreturn }

!llvm.module.flags = !{!1, !2}
!llvm.dbg.cu = !{!3}

!0 = !{}
!1 = !{i32 2, !"Dwarf Version", i32 4}
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !4, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!4 = !DIFile(filename: "julia", directory: ".")
!5 = distinct !DISubprogram(name: "rI_table", linkageName: "julia_rI_table_1017", scope: null, file: !6, line: 121, type: !7, scopeLine: 121, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3, retainedNodes: !12)
!6 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!7 = !DISubroutineType(types: !8)
!8 = !{!9, !10, !11}
!9 = !DICompositeType(tag: DW_TAG_structure_type, name: "Nothing", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079415932560")
!10 = !DICompositeType(tag: DW_TAG_structure_type, name: "#rI_table", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079337969232")
!11 = !DIBasicType(name: "UInt64", size: 64, encoding: DW_ATE_unsigned)
!12 = !{!13, !14}
!13 = !DILocalVariable(name: "#self#", arg: 1, scope: !5, file: !6, line: 121, type: !10)
!14 = !DILocalVariable(name: "x", arg: 2, scope: !5, file: !6, line: 121, type: !11)
!15 = !{!16, !16, i64 0}
!16 = !{!"jtbaa_gcframe", !17, i64 0}
!17 = !{!"jtbaa", !18, i64 0}
!18 = !{!"jtbaa"}
!19 = !{!20, !20, i64 0, i64 1}
!20 = !{!"jtbaa_const", !17, i64 0}
!21 = !DILocation(line: 121, scope: !5)
!22 = !DILocation(line: 588, scope: !23, inlinedAt: !26)
!23 = distinct !DISubprogram(name: "GenericMemory;", linkageName: "GenericMemory", scope: !24, file: !24, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!24 = !DIFile(filename: "boot.jl", directory: ".")
!25 = !DISubroutineType(types: !0)
!26 = !DILocation(line: 648, scope: !27, inlinedAt: !28)
!27 = distinct !DISubprogram(name: "Array;", linkageName: "Array", scope: !24, file: !24, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!28 = !DILocation(line: 122, scope: !5)
!29 = !{!30}
!30 = !{!"jnoalias_const", !31}
!31 = !{!"jnoalias"}
!32 = !{!33, !34, !35, !36}
!33 = !{!"jnoalias_gcframe", !31}
!34 = !{!"jnoalias_stack", !31}
!35 = !{!"jnoalias_data", !31}
!36 = !{!"jnoalias_typemd", !31}
!37 = !{i64 56}
!38 = !{i64 16}
!39 = !{!40, !40, i64 0}
!40 = !{!"jtbaa_memoryptr", !41, i64 0}
!41 = !{!"jtbaa_array", !17, i64 0}
!42 = !{!36}
!43 = !{!33, !34, !35, !30}
!44 = !{!45, !45, i64 0}
!45 = !{!"jtbaa_memorylen", !41, i64 0}
!46 = !DILocation(line: 594, scope: !47, inlinedAt: !48)
!47 = distinct !DISubprogram(name: "memoryref;", linkageName: "memoryref", scope: !24, file: !24, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!48 = !DILocation(line: 649, scope: !27, inlinedAt: !28)
!49 = !{!41, !41, i64 0}
!50 = !{!51, !51, i64 0}
!51 = !{!"jtbaa_arrayptr", !41, i64 0}
!52 = !{!53, !53, i64 0}
!53 = !{!"jtbaa_immut", !54, i64 0}
!54 = !{!"jtbaa_value", !55, i64 0}
!55 = !{!"jtbaa_data", !17, i64 0}
!56 = !{!35}
!57 = !{!33, !34, !36, !30}
!58 = !{!59, !59, i64 0}
!59 = !{!"jtbaa_arraysize", !41, i64 0}
!60 = !DILocation(line: 12, scope: !61, inlinedAt: !62)
!61 = distinct !DISubprogram(name: "rB_alloc;", linkageName: "rB_alloc", scope: !6, file: !6, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!62 = !DILocation(line: 123, scope: !5)
!63 = !DILocation(line: 1024, scope: !64, inlinedAt: !66)
!64 = distinct !DISubprogram(name: "_setindex!;", linkageName: "_setindex!", scope: !65, file: !65, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!65 = !DIFile(filename: "array.jl", directory: ".")
!66 = !DILocation(line: 1020, scope: !67, inlinedAt: !62)
!67 = distinct !DISubprogram(name: "setindex!;", linkageName: "setindex!", scope: !65, file: !65, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!68 = !DILocation(line: 385, scope: !69, inlinedAt: !63)
!69 = distinct !DISubprogram(name: "checkbounds;", linkageName: "checkbounds", scope: !70, file: !70, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!70 = !DIFile(filename: "essentials.jl", directory: ".")
!71 = !DILocation(line: 10, scope: !72, inlinedAt: !73)
!72 = distinct !DISubprogram(name: "size;", linkageName: "size", scope: !70, file: !70, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!73 = !DILocation(line: 11, scope: !74, inlinedAt: !68)
!74 = distinct !DISubprogram(name: "length;", linkageName: "length", scope: !70, file: !70, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!75 = !{!76, !76, i64 0}
!76 = !{!"jtbaa_stack", !17, i64 0}
!77 = !{!34}
!78 = !{!33, !35, !36, !30}
!79 = !DILocation(line: 57, scope: !80, inlinedAt: !82)
!80 = distinct !DISubprogram(name: "getproperty;", linkageName: "getproperty", scope: !81, file: !81, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!81 = !DIFile(filename: "Base_compiler.jl", directory: ".")
!82 = !DILocation(line: 1025, scope: !64, inlinedAt: !66)
!83 = !{i64 8}
!84 = !{i64 0, i64 1152921504606846975}
!85 = !{!86, !86, i64 0}
!86 = !{!"jtbaa_arraybuf", !55, i64 0}
!87 = !DILocation(line: 1026, scope: !64, inlinedAt: !66)
!88 = !DILocation(line: 641, scope: !89, inlinedAt: !91)
!89 = distinct !DISubprogram(name: "==;", linkageName: "==", scope: !90, file: !90, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!90 = !DIFile(filename: "promotion.jl", directory: ".")
!91 = !DILocation(line: 928, scope: !92, inlinedAt: !62)
!92 = distinct !DISubprogram(name: "iterate;", linkageName: "iterate", scope: !93, file: !93, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!93 = !DIFile(filename: "range.jl", directory: ".")
!94 = !DILocation(line: 87, scope: !95, inlinedAt: !97)
!95 = distinct !DISubprogram(name: "+;", linkageName: "+", scope: !96, file: !96, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!96 = !DIFile(filename: "int.jl", directory: ".")
!97 = !DILocation(line: 929, scope: !92, inlinedAt: !62)
!98 = !DILocation(line: 393, scope: !99, inlinedAt: !100)
!99 = distinct !DISubprogram(name: "&;", linkageName: "&", scope: !96, file: !96, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!100 = !DILocation(line: 1058, scope: !99, inlinedAt: !101)
!101 = !DILocation(line: 124, scope: !5)
!102 = !DILocation(line: 87, scope: !95, inlinedAt: !103)
!103 = !DILocation(line: 1058, scope: !95, inlinedAt: !101)
!104 = !DILocation(line: 974, scope: !105, inlinedAt: !106)
!105 = distinct !DISubprogram(name: "getindex;", linkageName: "getindex", scope: !70, file: !70, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!106 = !DILocation(line: 1366, scope: !107, inlinedAt: !101)
!107 = distinct !DISubprogram(name: "getindex;", linkageName: "getindex", scope: !108, file: !108, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!108 = !DIFile(filename: "abstractarray.jl", directory: ".")
!109 = !DILocation(line: 385, scope: !69, inlinedAt: !110)
!110 = !DILocation(line: 389, scope: !69, inlinedAt: !104)
!111 = !DILocation(line: 10, scope: !72, inlinedAt: !112)
!112 = !DILocation(line: 11, scope: !74, inlinedAt: !109)
!113 = !DILocation(line: 975, scope: !105, inlinedAt: !106)
!114 = !DILocation(line: 13, scope: !115, inlinedAt: !101)
!115 = distinct !DISubprogram(name: "rB_gate;", linkageName: "rB_gate", scope: !6, file: !6, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!116 = !DILocation(line: 125, scope: !5)
