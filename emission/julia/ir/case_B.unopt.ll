; ModuleID = 'case_B'
source_filename = "case_B"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128-ni:10:11:12:13"
target triple = "x86_64-unknown-linux-gnu"

@jlplt___bennett_qalloc_506_got = external global ptr #0
@jlplt___bennett_gate_508_got = external global ptr #1
@jlplt___bennett_rot_510_got = external global ptr #2
@jlplt___bennett_measure_512_got = external global ptr #3
@"_j_const#5" = private unnamed_addr constant i64 3, align 8
@"+Main.Base.RefValue#513" = private unnamed_addr constant ptr @"+Main.Base.RefValue#513.jit", !julia.constgv !0
@jlplt___bennett_ctrl_515_got = external global ptr #4
@"+Core.GenericMemory#516" = private unnamed_addr constant ptr @"+Core.GenericMemory#516.jit", !julia.constgv !0
@"+Core.Array#517" = private unnamed_addr constant ptr @"+Core.Array#517.jit", !julia.constgv !0
@"_j_const#7" = private unnamed_addr constant [1 x i64] [i64 4], align 8
@jlplt___bennett_ctrl_v_519_got = external global ptr #5
@jlplt___bennett_qfree_521_got = external global ptr #6

@"+Main.Base.RefValue#513.jit" = private alias ptr, inttoptr (i64 127079307385232 to ptr)
@"+Core.GenericMemory#516.jit" = private alias ptr, inttoptr (i64 127079420148128 to ptr)
@"+Core.Array#517.jit" = private alias ptr, inttoptr (i64 127079420430544 to ptr)

; Function Signature: case_B(UInt64)
define swiftcc i64 @julia_case_B_503(ptr nonnull swiftself "gcstack" %pgcstack_arg, i64 zeroext %"x::UInt64") #7 !dbg !5 {
top:
  %"new::Env" = alloca { ptr, i64, double }, align 8
  %"new::Array.size" = alloca i64, align 8
  %"new::Array.size16" = alloca i64, align 8
  %"new::Tuple" = alloca [1 x i64], align 8
  %"new::Tuple29" = alloca [1 x i64], align 8
  %current_task = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152
  %ptls_field = getelementptr inbounds i8, ptr %current_task, i32 168
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !14
  %0 = getelementptr inbounds i8, ptr %ptls_load, i32 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !18, !invariant.load !0
  fence syncscope("singlethread") seq_cst
  call void @julia.safepoint(ptr %safepoint)
  fence syncscope("singlethread") seq_cst
    #dbg_value(i64 %"x::UInt64", !13, !DIExpression(), !20)
  %__bennett_qalloc = load atomic ptr, ptr @jlplt___bennett_qalloc_506_got unordered, align 8, !dbg !21
  %1 = call ptr %__bennett_qalloc(i64 0, i64 4), !dbg !21
  %__bennett_gate = load atomic ptr, ptr @jlplt___bennett_gate_508_got unordered, align 8, !dbg !25
  call void %__bennett_gate(i32 1, ptr %1, i64 0), !dbg !25
  %2 = uitofp i64 %"x::UInt64" to double, !dbg !28
  %3 = fmul double %2, 1.250000e-01, !dbg !32
  %__bennett_rot = load atomic ptr, ptr @jlplt___bennett_rot_510_got unordered, align 8, !dbg !34
  call void %__bennett_rot(i32 3, ptr %1, i64 1, double %3), !dbg !34
  %__bennett_measure = load atomic ptr, ptr @jlplt___bennett_measure_512_got unordered, align 8, !dbg !37
  %4 = call i8 %__bennett_measure(ptr %1, i64 0), !dbg !37
  %5 = trunc i8 %4 to i1, !dbg !39
  %6 = xor i1 %5, true, !dbg !39
  br i1 %6, label %top.L9_crit_edge, label %L8, !dbg !39

top.L9_crit_edge:                                 ; preds = %top
  br label %L9, !dbg !39

L8:                                               ; preds = %top
  %__bennett_gate1 = load atomic ptr, ptr @jlplt___bennett_gate_508_got unordered, align 8, !dbg !40
  call void %__bennett_gate1(i32 1, ptr %1, i64 2), !dbg !40
  br label %L9, !dbg !40

L9:                                               ; preds = %top.L9_crit_edge, %L8
  %value_phi = phi i64 [ 1, %L8 ], [ 0, %top.L9_crit_edge ]
  br label %L11, !dbg !42

L11:                                              ; preds = %L9
  br label %L12, !dbg !42

L12:                                              ; preds = %L11
  br label %L13, !dbg !42

L13:                                              ; preds = %L12
  br label %L14, !dbg !42

L14:                                              ; preds = %L13
  br label %L15, !dbg !42

L15:                                              ; preds = %L14
  %7 = getelementptr inbounds i8, ptr %"new::Env", i32 0, !dbg !52
  store ptr %1, ptr %7, align 8, !dbg !52, !tbaa !57, !alias.scope !59, !noalias !62
  %8 = getelementptr inbounds i8, ptr %"new::Env", i32 8, !dbg !52
  %"_j_const#5.copyload" = load i64, ptr @"_j_const#5", align 8, !dbg !52, !tbaa !67, !alias.scope !71, !noalias !72
  store i64 %"_j_const#5.copyload", ptr %8, align 8, !dbg !52, !tbaa !57, !alias.scope !59, !noalias !62
  %9 = getelementptr inbounds i8, ptr %"new::Env", i32 16, !dbg !52
  store double %3, ptr %9, align 8, !dbg !52, !tbaa !57, !alias.scope !59, !noalias !62
  br label %L17, !dbg !52

L17:                                              ; preds = %L15
  %"+Main.Base.RefValue#513" = load ptr, ptr @"+Main.Base.RefValue#513", align 8, !dbg !73, !tbaa !18, !invariant.load !0, !alias.scope !80, !noalias !81, !nonnull !0, !dereferenceable !82, !align !83
  %RefValue = ptrtoint ptr %"+Main.Base.RefValue#513" to i64, !dbg !73
  %10 = inttoptr i64 %RefValue to ptr, !dbg !73
  %current_task2 = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152, !dbg !73
  %11 = addrspacecast ptr %10 to ptr addrspace(10), !dbg !73
  %"new::RefValue" = call noalias nonnull align 8 dereferenceable(24) ptr addrspace(10) @julia.gc_alloc_obj(ptr %current_task2, i64 24, ptr addrspace(10) %11) #16, !dbg !73
  %12 = addrspacecast ptr addrspace(10) %"new::RefValue" to ptr addrspace(11), !dbg !73
  %13 = addrspacecast ptr addrspace(10) %"new::RefValue" to ptr addrspace(11), !dbg !73
  call void @llvm.memcpy.p11.p0.i64(ptr addrspace(11) align 8 %13, ptr align 8 %"new::Env", i64 24, i1 false), !dbg !73, !tbaa !84, !alias.scope !85, !noalias !86
  %14 = call token (...) @llvm.julia.gc_preserve_begin(ptr addrspace(10) %"new::RefValue"), !dbg !87
  %15 = addrspacecast ptr addrspace(10) %"new::RefValue" to ptr addrspace(11), !dbg !88
  %16 = call nonnull ptr @julia.pointer_from_objref(ptr addrspace(11) %15) #13, !dbg !88
  %__bennett_ctrl = load atomic ptr, ptr @jlplt___bennett_ctrl_515_got unordered, align 8, !dbg !93
  call void %__bennett_ctrl(ptr %1, i64 0, ptr inttoptr (i64 127079231243584 to ptr), i64 8, ptr %16), !dbg !93
  call void @llvm.julia.gc_preserve_end(token %14), !dbg !93
  br label %L23, !dbg !93

L23:                                              ; preds = %L17
  %"+Core.GenericMemory#516" = load ptr, ptr @"+Core.GenericMemory#516", align 8, !dbg !94, !tbaa !18, !invariant.load !0, !alias.scope !80, !noalias !81, !nonnull !0, !dereferenceable !82, !align !83
  %current_task3 = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152, !dbg !94
  %17 = addrspacecast ptr %"+Core.GenericMemory#516" to ptr addrspace(10), !dbg !94
  %"Memory{Ptr}[]" = call noalias nonnull align 16 dereferenceable(48) ptr addrspace(10) @julia.gc_alloc_obj(ptr %current_task3, i64 48, ptr addrspace(10) %17) #11, !dbg !94
  %18 = addrspacecast ptr addrspace(10) %"Memory{Ptr}[]" to ptr addrspace(11), !dbg !94
  %memory_ptr = getelementptr inbounds nuw { i64, ptr }, ptr addrspace(11) %18, i32 0, i32 1, !dbg !94
  %19 = addrspacecast ptr addrspace(10) %"Memory{Ptr}[]" to ptr addrspace(11), !dbg !94
  %20 = call nonnull ptr @julia.pointer_from_objref(ptr addrspace(11) %19) #13, !dbg !94
  %memory_data = getelementptr inbounds i8, ptr %20, i32 16, !dbg !94
  store ptr %memory_data, ptr addrspace(11) %memory_ptr, align 8, !dbg !94, !tbaa !99, !alias.scope !102, !noalias !103
  %21 = addrspacecast ptr addrspace(10) %"Memory{Ptr}[]" to ptr addrspace(11), !dbg !94
  %22 = getelementptr inbounds nuw { i64, ptr }, ptr addrspace(11) %21, i32 0, i32 0, !dbg !94
  store i64 4, ptr addrspace(11) %22, align 8, !dbg !94, !tbaa !104, !alias.scope !102, !noalias !103
  %23 = addrspacecast ptr addrspace(10) %"Memory{Ptr}[]" to ptr addrspace(11), !dbg !106
  %memory_data_ptr = getelementptr inbounds nuw { i64, ptr }, ptr addrspace(11) %23, i32 0, i32 1, !dbg !106
  %memory_data4 = load ptr, ptr addrspace(11) %memory_data_ptr, align 8, !dbg !106, !tbaa !99, !alias.scope !102, !noalias !103, !nonnull !0
  %24 = insertvalue { ptr, ptr addrspace(10) } zeroinitializer, ptr %memory_data4, 0, !dbg !106
  %memory_ref = insertvalue { ptr, ptr addrspace(10) } %24, ptr addrspace(10) %"Memory{Ptr}[]", 1, !dbg !106
  %"+Core.Array#517" = load ptr, ptr @"+Core.Array#517", align 8, !dbg !108, !tbaa !18, !invariant.load !0, !alias.scope !80, !noalias !81, !nonnull !0, !dereferenceable !82, !align !83
  %Array = ptrtoint ptr %"+Core.Array#517" to i64, !dbg !108
  %25 = inttoptr i64 %Array to ptr, !dbg !108
  %current_task5 = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152, !dbg !108
  %26 = addrspacecast ptr %25 to ptr addrspace(10), !dbg !108
  %"new::Array" = call noalias nonnull align 8 dereferenceable(24) ptr addrspace(10) @julia.gc_alloc_obj(ptr %current_task5, i64 24, ptr addrspace(10) %26) #16, !dbg !108
  %27 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !108
  %28 = getelementptr inbounds i8, ptr addrspace(11) %27, i32 8, !dbg !108
  store ptr addrspace(10) null, ptr addrspace(11) %28, align 8, !dbg !108, !tbaa !109, !alias.scope !102, !noalias !103
  %29 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !108
  store { ptr, ptr addrspace(10) } %memory_ref, ptr addrspace(11) %29, align 8, !dbg !108, !tbaa !110, !alias.scope !102, !noalias !103
  %30 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !108
  %"new::Array.size_ptr" = getelementptr inbounds i8, ptr addrspace(11) %30, i32 16, !dbg !108
  %"_j_const#7.copyload" = load i64, ptr @"_j_const#7", align 8, !dbg !108, !tbaa !67, !alias.scope !71, !noalias !72
  store i64 %"_j_const#7.copyload", ptr addrspace(11) %"new::Array.size_ptr", align 8, !dbg !108, !tbaa !112, !alias.scope !102, !noalias !103
  br label %L26, !dbg !108

L26:                                              ; preds = %L57, %L23
  %value_phi6 = phi i64 [ 1, %L23 ], [ %value_phi12, %L57 ]
  %value_phi7 = phi i64 [ 1, %L23 ], [ %value_phi13, %L57 ]
  %__bennett_qalloc8 = load atomic ptr, ptr @jlplt___bennett_qalloc_506_got unordered, align 8, !dbg !114
  %31 = call ptr %__bennett_qalloc8(i64 0, i64 1), !dbg !114
  br i1 false, label %L42, label %L31, !dbg !116

L31:                                              ; preds = %L26
  %32 = sub i64 %value_phi6, 1, !dbg !121
  %33 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !124
  %"new::Array.size_ptr9" = getelementptr inbounds i8, ptr addrspace(11) %33, i32 16, !dbg !124
  %"new::Array.size_ptr9.copyload" = load i64, ptr addrspace(11) %"new::Array.size_ptr9", align 8, !dbg !124, !tbaa !112, !alias.scope !102, !noalias !103
  store i64 %"new::Array.size_ptr9.copyload", ptr %"new::Array.size", align 8, !dbg !124, !tbaa !57, !alias.scope !59, !noalias !62
  %bitcast = load i64, ptr %"new::Array.size", align 8, !dbg !121, !tbaa !57, !alias.scope !59, !noalias !62
  %34 = icmp ult i64 %32, %bitcast, !dbg !121
  %35 = xor i1 %34, true, !dbg !116
  br i1 %35, label %L39, label %L38, !dbg !116

L38:                                              ; preds = %L31
  br label %L42, !dbg !116

L39:                                              ; preds = %L31
  %36 = getelementptr inbounds i8, ptr %"new::Tuple29", i32 0, !dbg !116
  store i64 %value_phi6, ptr %36, align 8, !dbg !116, !tbaa !57, !alias.scope !59, !noalias !62
  %37 = addrspacecast ptr %"new::Tuple29" to ptr addrspace(11), !dbg !116
  call swiftcc void @j_throw_boundserror_522(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr addrspace(10) %"new::Array", ptr addrspace(11) nocapture readonly %37) #17, !dbg !116
  call void @llvm.trap(), !dbg !116
  unreachable, !dbg !116

L42:                                              ; preds = %L38, %L26
  %38 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !128
  %39 = getelementptr inbounds nuw { ptr, ptr addrspace(10) }, ptr addrspace(11) %38, i32 0, i32 0, !dbg !128
  %memoryref_data = load ptr, ptr addrspace(11) %39, align 8, !dbg !128, !tbaa !110, !alias.scope !102, !noalias !103
  %40 = getelementptr inbounds nuw { ptr, ptr addrspace(10) }, ptr addrspace(11) %38, i32 0, i32 1, !dbg !128
  %memoryref_mem = load ptr addrspace(10), ptr addrspace(11) %40, align 8, !dbg !128, !tbaa !110, !alias.scope !102, !noalias !103, !dereferenceable_or_null !83, !align !132
  %41 = insertvalue { ptr, ptr addrspace(10) } zeroinitializer, ptr %memoryref_data, 0, !dbg !128
  %"new::Array.ref" = insertvalue { ptr, ptr addrspace(10) } %41, ptr addrspace(10) %memoryref_mem, 1, !dbg !128
  %memoryref_offset = sub i64 %value_phi6, 1, !dbg !131
  %memoryref_byteoffset = mul i64 %memoryref_offset, 8, !dbg !131
  %memoryref_data_byteoffset = getelementptr i8, ptr %memoryref_data, i64 %memoryref_byteoffset, !dbg !131
  %42 = insertvalue { ptr, ptr addrspace(10) } zeroinitializer, ptr %memoryref_data_byteoffset, 0, !dbg !131
  %memory_ref10 = insertvalue { ptr, ptr addrspace(10) } %42, ptr addrspace(10) %memoryref_mem, 1, !dbg !131
  %43 = addrspacecast ptr addrspace(10) %memoryref_mem to ptr addrspace(11), !dbg !131
  %44 = getelementptr inbounds nuw { i64, ptr }, ptr addrspace(11) %43, i32 0, i32 0, !dbg !131
  %memory_len = load i64, ptr addrspace(11) %44, align 8, !dbg !131, !tbaa !104, !range !133, !alias.scope !102, !noalias !103
  %45 = call ptr addrspace(13) @julia.gc_loaded(ptr addrspace(10) %memoryref_mem, ptr %memoryref_data), !dbg !131
  %memoryref_data11 = getelementptr inbounds i8, ptr addrspace(13) %45, i64 %memoryref_byteoffset, !dbg !131
  store ptr %31, ptr addrspace(13) %memoryref_data11, align 8, !dbg !131, !tbaa !134, !alias.scope !71, !noalias !72
  br label %L46, !dbg !136

L46:                                              ; preds = %L42
  br label %L47, !dbg !119

L47:                                              ; preds = %L46
  %46 = icmp eq i64 %value_phi7, 4, !dbg !137
  %47 = xor i1 %46, true, !dbg !140
  br i1 %47, label %L50, label %L49, !dbg !140

L49:                                              ; preds = %L47
  br label %L52, !dbg !140

L50:                                              ; preds = %L47
  %48 = add i64 %value_phi7, 1, !dbg !143
  br label %L52, !dbg !140

L52:                                              ; preds = %L50, %L49
  %value_phi12 = phi i64 [ %48, %L50 ], [ undef, %L49 ]
  %value_phi13 = phi i64 [ %48, %L50 ], [ undef, %L49 ]
  %value_phi14 = phi i8 [ 1, %L49 ], [ 0, %L50 ]
  %49 = trunc i8 %value_phi14 to i1, !dbg !115
  %50 = xor i1 %49, true, !dbg !115
  %51 = xor i1 %50, true, !dbg !115
  br i1 %51, label %L58, label %L57, !dbg !115

L57:                                              ; preds = %L52
  br label %L26, !dbg !115

L58:                                              ; preds = %L52
  %52 = and i64 %"x::UInt64", 3, !dbg !147
  %53 = add i64 %52, 1, !dbg !151
  br i1 false, label %L75, label %L63, !dbg !153

L63:                                              ; preds = %L58
  %54 = sub i64 %53, 1, !dbg !158
  %55 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !160
  %"new::Array.size_ptr15" = getelementptr inbounds i8, ptr addrspace(11) %55, i32 16, !dbg !160
  %"new::Array.size_ptr15.copyload" = load i64, ptr addrspace(11) %"new::Array.size_ptr15", align 8, !dbg !160, !tbaa !112, !alias.scope !102, !noalias !103
  store i64 %"new::Array.size_ptr15.copyload", ptr %"new::Array.size16", align 8, !dbg !160, !tbaa !57, !alias.scope !59, !noalias !62
  %bitcast17 = load i64, ptr %"new::Array.size16", align 8, !dbg !158, !tbaa !57, !alias.scope !59, !noalias !62
  %56 = icmp ult i64 %54, %bitcast17, !dbg !158
  %57 = xor i1 %56, true, !dbg !159
  br i1 %57, label %L71, label %L70, !dbg !159

L70:                                              ; preds = %L63
  br label %L74, !dbg !159

L71:                                              ; preds = %L63
  %58 = getelementptr inbounds i8, ptr %"new::Tuple", i32 0, !dbg !159
  store i64 %53, ptr %58, align 8, !dbg !159, !tbaa !57, !alias.scope !59, !noalias !62
  %59 = addrspacecast ptr %"new::Tuple" to ptr addrspace(11), !dbg !159
  call swiftcc void @j_throw_boundserror_522(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr addrspace(10) %"new::Array", ptr addrspace(11) nocapture readonly %59) #17, !dbg !159
  call void @llvm.trap(), !dbg !159
  unreachable, !dbg !159

L74:                                              ; preds = %L70
  br label %L75, !dbg !159

L75:                                              ; preds = %L74, %L58
  %60 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !162
  %61 = getelementptr inbounds nuw { ptr, ptr addrspace(10) }, ptr addrspace(11) %60, i32 0, i32 0, !dbg !162
  %memoryref_data19 = load ptr, ptr addrspace(11) %61, align 8, !dbg !162, !tbaa !110, !alias.scope !102, !noalias !103
  %62 = getelementptr inbounds nuw { ptr, ptr addrspace(10) }, ptr addrspace(11) %60, i32 0, i32 1, !dbg !162
  %memoryref_mem25 = load ptr addrspace(10), ptr addrspace(11) %62, align 8, !dbg !162, !tbaa !110, !alias.scope !102, !noalias !103, !dereferenceable_or_null !83, !align !132
  %63 = insertvalue { ptr, ptr addrspace(10) } zeroinitializer, ptr %memoryref_data19, 0, !dbg !162
  %"new::Array.ref18" = insertvalue { ptr, ptr addrspace(10) } %63, ptr addrspace(10) %memoryref_mem25, 1, !dbg !162
  %memoryref_offset21 = sub i64 %53, 1, !dbg !162
  %memoryref_byteoffset22 = mul i64 %memoryref_offset21, 8, !dbg !162
  %memoryref_data_byteoffset23 = getelementptr i8, ptr %memoryref_data19, i64 %memoryref_byteoffset22, !dbg !162
  %64 = insertvalue { ptr, ptr addrspace(10) } zeroinitializer, ptr %memoryref_data_byteoffset23, 0, !dbg !162
  %memory_ref24 = insertvalue { ptr, ptr addrspace(10) } %64, ptr addrspace(10) %memoryref_mem25, 1, !dbg !162
  %65 = addrspacecast ptr addrspace(10) %memoryref_mem25 to ptr addrspace(11), !dbg !162
  %66 = getelementptr inbounds nuw { i64, ptr }, ptr addrspace(11) %65, i32 0, i32 0, !dbg !162
  %memory_len26 = load i64, ptr addrspace(11) %66, align 8, !dbg !162, !tbaa !104, !range !133, !alias.scope !102, !noalias !103
  %67 = call ptr addrspace(13) @julia.gc_loaded(ptr addrspace(10) %memoryref_mem25, ptr %memoryref_data19), !dbg !162
  %memoryref_data27 = getelementptr inbounds i8, ptr addrspace(13) %67, i64 %memoryref_byteoffset22, !dbg !162
  %68 = load ptr, ptr addrspace(13) %memoryref_data27, align 8, !dbg !162, !tbaa !134, !alias.scope !71, !noalias !72
  br label %L79, !dbg !162

L79:                                              ; preds = %L75
  br label %L80, !dbg !162

L80:                                              ; preds = %L79
  %__bennett_gate28 = load atomic ptr, ptr @jlplt___bennett_gate_508_got unordered, align 8, !dbg !163
  call void %__bennett_gate28(i32 1, ptr %68, i64 0), !dbg !163
  %__bennett_ctrl_v = load atomic ptr, ptr @jlplt___bennett_ctrl_v_519_got unordered, align 8, !dbg !164
  call void %__bennett_ctrl_v(ptr %1, i64 0, ptr null, i64 8, i32 1, double 2.500000e+00, ptr %1), !dbg !164
  %__bennett_qfree = load atomic ptr, ptr @jlplt___bennett_qfree_521_got unordered, align 8, !dbg !167
  call void %__bennett_qfree(ptr %1), !dbg !167
  ret i64 %value_phi, !dbg !168

after_noret:                                      ; No predecessors!
  call void @llvm.trap(), !dbg !159
  unreachable, !dbg !159

after_noret30:                                    ; No predecessors!
  call void @llvm.trap(), !dbg !116
  unreachable, !dbg !116
}

; Function Attrs: noinline optnone
define nonnull ptr addrspace(10) @jfptr_case_B_504(ptr addrspace(10) %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") #8 {
top:
  %pgcstack = call ptr @julia.get_pgcstack()
  %0 = load ptr addrspace(10), ptr %"args::Any[]", align 8, !tbaa !18, !invariant.load !0, !alias.scope !80, !noalias !81, !nonnull !0, !dereferenceable !132, !align !132
  %.unbox = load i64, ptr addrspace(10) %0, align 8, !tbaa !67, !alias.scope !71, !noalias !72
  %1 = call swiftcc i64 @julia_case_B_503(ptr nonnull swiftself "gcstack" %pgcstack, i64 zeroext %.unbox)
  %box_UInt64 = call nonnull align 8 dereferenceable(8) ptr addrspace(10) @ijl_box_uint64(i64 zeroext %1) #9
  ret ptr addrspace(10) %box_UInt64
}

declare ptr @julia.get_pgcstack()

; Function Attrs: nounwind willreturn memory(read, inaccessiblemem: readwrite)
declare nonnull align 8 dereferenceable(8) ptr addrspace(10) @ijl_box_uint64(i64 zeroext) #9

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) #10

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr addrspace(10) @julia.gc_alloc_obj(ptr, i64, ptr addrspace(10)) #11

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p11.p0.i64(ptr addrspace(11) noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #12

declare token @llvm.julia.gc_preserve_begin(...)

; Function Attrs: norecurse nosync nounwind speculatable willreturn memory(none)
declare nonnull ptr @julia.pointer_from_objref(ptr addrspace(11)) #13

declare void @llvm.julia.gc_preserve_end(token)

; Function Attrs: norecurse nosync nounwind speculatable willreturn memory(none)
declare noundef nonnull ptr addrspace(13) @julia.gc_loaded(ptr addrspace(10) nocapture noundef nonnull readnone, ptr noundef nonnull readnone) #13

; Function Signature: throw_boundserror(Array{Ptr{Nothing}, 1}, Tuple{Int64})
; Function Attrs: noreturn
declare swiftcc void @j_throw_boundserror_522(ptr nonnull swiftself "gcstack", ptr addrspace(10), ptr addrspace(11) nocapture readonly) #14

; Function Attrs: cold noreturn nounwind memory(inaccessiblemem: write)
declare void @llvm.trap() #15

attributes #0 = { "julia.fname"="__bennett_qalloc" "julia.libidx"="0" }
attributes #1 = { "julia.fname"="__bennett_gate" "julia.libidx"="0" }
attributes #2 = { "julia.fname"="__bennett_rot" "julia.libidx"="0" }
attributes #3 = { "julia.fname"="__bennett_measure" "julia.libidx"="0" }
attributes #4 = { "julia.fname"="__bennett_ctrl" "julia.libidx"="0" }
attributes #5 = { "julia.fname"="__bennett_ctrl_v" "julia.libidx"="0" }
attributes #6 = { "julia.fname"="__bennett_qfree" "julia.libidx"="0" }
attributes #7 = { "frame-pointer"="all" "julia.fsig"="case_B(UInt64)" "probe-stack"="inline-asm" }
attributes #8 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #9 = { nounwind willreturn memory(read, inaccessiblemem: readwrite) }
attributes #10 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #11 = { nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #12 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #13 = { norecurse nosync nounwind speculatable willreturn memory(none) }
attributes #14 = { noreturn "frame-pointer"="all" "julia.fsig"="throw_boundserror(Array{Ptr{Nothing}, 1}, Tuple{Int64})" "probe-stack"="inline-asm" }
attributes #15 = { cold noreturn nounwind memory(inaccessiblemem: write) }
attributes #16 = { nounwind willreturn allockind("alloc,uninitialized") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #17 = { noreturn }

!llvm.module.flags = !{!1, !2}
!llvm.dbg.cu = !{!3}

!0 = !{}
!1 = !{i32 2, !"Dwarf Version", i32 4}
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !4, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!4 = !DIFile(filename: "julia", directory: ".")
!5 = distinct !DISubprogram(name: "case_B", linkageName: "julia_case_B_503", scope: null, file: !6, line: 129, type: !7, scopeLine: 129, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3, retainedNodes: !11)
!6 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!7 = !DISubroutineType(types: !8)
!8 = !{!9, !10, !9}
!9 = !DIBasicType(name: "UInt64", size: 64, encoding: DW_ATE_unsigned)
!10 = !DICompositeType(tag: DW_TAG_structure_type, name: "#case_B", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079337970000")
!11 = !{!12, !13}
!12 = !DILocalVariable(name: "#self#", arg: 1, scope: !5, file: !6, line: 129, type: !10)
!13 = !DILocalVariable(name: "x", arg: 2, scope: !5, file: !6, line: 129, type: !9)
!14 = !{!15, !15, i64 0}
!15 = !{!"jtbaa_gcframe", !16, i64 0}
!16 = !{!"jtbaa", !17, i64 0}
!17 = !{!"jtbaa"}
!18 = !{!19, !19, i64 0, i64 1}
!19 = !{!"jtbaa_const", !16, i64 0}
!20 = !DILocation(line: 129, scope: !5)
!21 = !DILocation(line: 12, scope: !22, inlinedAt: !24)
!22 = distinct !DISubprogram(name: "rB_alloc;", linkageName: "rB_alloc", scope: !6, file: !6, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!23 = !DISubroutineType(types: !0)
!24 = !DILocation(line: 130, scope: !5)
!25 = !DILocation(line: 13, scope: !26, inlinedAt: !27)
!26 = distinct !DISubprogram(name: "rB_gate;", linkageName: "rB_gate", scope: !6, file: !6, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!27 = !DILocation(line: 131, scope: !5)
!28 = !DILocation(line: 251, scope: !29, inlinedAt: !31)
!29 = distinct !DISubprogram(name: "Float64;", linkageName: "Float64", scope: !30, file: !30, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!30 = !DIFile(filename: "float.jl", directory: ".")
!31 = !DILocation(line: 132, scope: !5)
!32 = !DILocation(line: 494, scope: !33, inlinedAt: !31)
!33 = distinct !DISubprogram(name: "*;", linkageName: "*", scope: !30, file: !30, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!34 = !DILocation(line: 15, scope: !35, inlinedAt: !36)
!35 = distinct !DISubprogram(name: "rB_rot;", linkageName: "rB_rot", scope: !6, file: !6, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!36 = !DILocation(line: 133, scope: !5)
!37 = !DILocation(line: 14, scope: !38, inlinedAt: !39)
!38 = distinct !DISubprogram(name: "rB_measure;", linkageName: "rB_measure", scope: !6, file: !6, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!39 = !DILocation(line: 135, scope: !5)
!40 = !DILocation(line: 13, scope: !26, inlinedAt: !41)
!41 = !DILocation(line: 136, scope: !5)
!42 = !DILocation(line: 874, scope: !43, inlinedAt: !45)
!43 = distinct !DISubprogram(name: "check_sign_bit;", linkageName: "check_sign_bit", scope: !44, file: !44, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!44 = !DIFile(filename: "boot.jl", directory: ".")
!45 = !DILocation(line: 985, scope: !46, inlinedAt: !47)
!46 = distinct !DISubprogram(name: "toUInt64;", linkageName: "toUInt64", scope: !44, file: !44, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!47 = !DILocation(line: 1015, scope: !48, inlinedAt: !49)
!48 = distinct !DISubprogram(name: "UInt64;", linkageName: "UInt64", scope: !44, file: !44, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!49 = !DILocation(line: 7, scope: !50, inlinedAt: !52)
!50 = distinct !DISubprogram(name: "convert;", linkageName: "convert", scope: !51, file: !51, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!51 = !DIFile(filename: "number.jl", directory: ".")
!52 = !DILocation(line: 75, scope: !53, inlinedAt: !54)
!53 = distinct !DISubprogram(name: "Env;", linkageName: "Env", scope: !6, file: !6, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!54 = !DILocation(line: 84, scope: !55, inlinedAt: !56)
!55 = distinct !DISubprogram(name: "rF_ctrl;", linkageName: "rF_ctrl", scope: !6, file: !6, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!56 = !DILocation(line: 138, scope: !5)
!57 = !{!58, !58, i64 0}
!58 = !{!"jtbaa_stack", !16, i64 0}
!59 = !{!60}
!60 = !{!"jnoalias_stack", !61}
!61 = !{!"jnoalias"}
!62 = !{!63, !64, !65, !66}
!63 = !{!"jnoalias_gcframe", !61}
!64 = !{!"jnoalias_data", !61}
!65 = !{!"jnoalias_typemd", !61}
!66 = !{!"jnoalias_const", !61}
!67 = !{!68, !68, i64 0}
!68 = !{!"jtbaa_immut", !69, i64 0}
!69 = !{!"jtbaa_value", !70, i64 0}
!70 = !{!"jtbaa_data", !16, i64 0}
!71 = !{!64}
!72 = !{!63, !60, !65, !66}
!73 = !DILocation(line: 8, scope: !74, inlinedAt: !76)
!74 = distinct !DISubprogram(name: "RefValue;", linkageName: "RefValue", scope: !75, file: !75, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!75 = !DIFile(filename: "refvalue.jl", directory: ".")
!76 = !DILocation(line: 10, scope: !74, inlinedAt: !77)
!77 = !DILocation(line: 145, scope: !78, inlinedAt: !54)
!78 = distinct !DISubprogram(name: "Ref;", linkageName: "Ref", scope: !79, file: !79, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!79 = !DIFile(filename: "refpointer.jl", directory: ".")
!80 = !{!66}
!81 = !{!63, !60, !64, !65}
!82 = !{i64 56}
!83 = !{i64 16}
!84 = !{!16, !16, i64 0}
!85 = !{!60, !64}
!86 = !{!63, !65, !66}
!87 = !DILocation(line: 85, scope: !55, inlinedAt: !56)
!88 = !DILocation(line: 302, scope: !89, inlinedAt: !91)
!89 = distinct !DISubprogram(name: "pointer_from_objref;", linkageName: "pointer_from_objref", scope: !90, file: !90, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!90 = !DIFile(filename: "pointer.jl", directory: ".")
!91 = !DILocation(line: 40, scope: !92, inlinedAt: !93)
!92 = distinct !DISubprogram(name: "unsafe_convert;", linkageName: "unsafe_convert", scope: !75, file: !75, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!93 = !DILocation(line: 86, scope: !55, inlinedAt: !56)
!94 = !DILocation(line: 588, scope: !95, inlinedAt: !96)
!95 = distinct !DISubprogram(name: "GenericMemory;", linkageName: "GenericMemory", scope: !44, file: !44, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!96 = !DILocation(line: 648, scope: !97, inlinedAt: !98)
!97 = distinct !DISubprogram(name: "Array;", linkageName: "Array", scope: !44, file: !44, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!98 = !DILocation(line: 139, scope: !5)
!99 = !{!100, !100, i64 0}
!100 = !{!"jtbaa_memoryptr", !101, i64 0}
!101 = !{!"jtbaa_array", !16, i64 0}
!102 = !{!65}
!103 = !{!63, !60, !64, !66}
!104 = !{!105, !105, i64 0}
!105 = !{!"jtbaa_memorylen", !101, i64 0}
!106 = !DILocation(line: 594, scope: !107, inlinedAt: !108)
!107 = distinct !DISubprogram(name: "memoryref;", linkageName: "memoryref", scope: !44, file: !44, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!108 = !DILocation(line: 649, scope: !97, inlinedAt: !98)
!109 = !{!101, !101, i64 0}
!110 = !{!111, !111, i64 0}
!111 = !{!"jtbaa_arrayptr", !101, i64 0}
!112 = !{!113, !113, i64 0}
!113 = !{!"jtbaa_arraysize", !101, i64 0}
!114 = !DILocation(line: 12, scope: !22, inlinedAt: !115)
!115 = !DILocation(line: 140, scope: !5)
!116 = !DILocation(line: 1024, scope: !117, inlinedAt: !119)
!117 = distinct !DISubprogram(name: "_setindex!;", linkageName: "_setindex!", scope: !118, file: !118, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!118 = !DIFile(filename: "array.jl", directory: ".")
!119 = !DILocation(line: 1020, scope: !120, inlinedAt: !115)
!120 = distinct !DISubprogram(name: "setindex!;", linkageName: "setindex!", scope: !118, file: !118, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!121 = !DILocation(line: 385, scope: !122, inlinedAt: !116)
!122 = distinct !DISubprogram(name: "checkbounds;", linkageName: "checkbounds", scope: !123, file: !123, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!123 = !DIFile(filename: "essentials.jl", directory: ".")
!124 = !DILocation(line: 10, scope: !125, inlinedAt: !126)
!125 = distinct !DISubprogram(name: "size;", linkageName: "size", scope: !123, file: !123, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!126 = !DILocation(line: 11, scope: !127, inlinedAt: !121)
!127 = distinct !DISubprogram(name: "length;", linkageName: "length", scope: !123, file: !123, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!128 = !DILocation(line: 57, scope: !129, inlinedAt: !131)
!129 = distinct !DISubprogram(name: "getproperty;", linkageName: "getproperty", scope: !130, file: !130, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!130 = !DIFile(filename: "Base_compiler.jl", directory: ".")
!131 = !DILocation(line: 1025, scope: !117, inlinedAt: !119)
!132 = !{i64 8}
!133 = !{i64 0, i64 1152921504606846975}
!134 = !{!135, !135, i64 0}
!135 = !{!"jtbaa_arraybuf", !70, i64 0}
!136 = !DILocation(line: 1026, scope: !117, inlinedAt: !119)
!137 = !DILocation(line: 641, scope: !138, inlinedAt: !140)
!138 = distinct !DISubprogram(name: "==;", linkageName: "==", scope: !139, file: !139, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!139 = !DIFile(filename: "promotion.jl", directory: ".")
!140 = !DILocation(line: 928, scope: !141, inlinedAt: !115)
!141 = distinct !DISubprogram(name: "iterate;", linkageName: "iterate", scope: !142, file: !142, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!142 = !DIFile(filename: "range.jl", directory: ".")
!143 = !DILocation(line: 87, scope: !144, inlinedAt: !146)
!144 = distinct !DISubprogram(name: "+;", linkageName: "+", scope: !145, file: !145, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!145 = !DIFile(filename: "int.jl", directory: ".")
!146 = !DILocation(line: 929, scope: !141, inlinedAt: !115)
!147 = !DILocation(line: 393, scope: !148, inlinedAt: !149)
!148 = distinct !DISubprogram(name: "&;", linkageName: "&", scope: !145, file: !145, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!149 = !DILocation(line: 1058, scope: !148, inlinedAt: !150)
!150 = !DILocation(line: 141, scope: !5)
!151 = !DILocation(line: 87, scope: !144, inlinedAt: !152)
!152 = !DILocation(line: 1058, scope: !144, inlinedAt: !150)
!153 = !DILocation(line: 974, scope: !154, inlinedAt: !155)
!154 = distinct !DISubprogram(name: "getindex;", linkageName: "getindex", scope: !123, file: !123, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!155 = !DILocation(line: 1366, scope: !156, inlinedAt: !150)
!156 = distinct !DISubprogram(name: "getindex;", linkageName: "getindex", scope: !157, file: !157, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!157 = !DIFile(filename: "abstractarray.jl", directory: ".")
!158 = !DILocation(line: 385, scope: !122, inlinedAt: !159)
!159 = !DILocation(line: 389, scope: !122, inlinedAt: !153)
!160 = !DILocation(line: 10, scope: !125, inlinedAt: !161)
!161 = !DILocation(line: 11, scope: !127, inlinedAt: !158)
!162 = !DILocation(line: 975, scope: !154, inlinedAt: !155)
!163 = !DILocation(line: 13, scope: !26, inlinedAt: !150)
!164 = !DILocation(line: 108, scope: !165, inlinedAt: !166)
!165 = distinct !DISubprogram(name: "rH2_ctrl_v;", linkageName: "rH2_ctrl_v", scope: !6, file: !6, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!166 = !DILocation(line: 142, scope: !5)
!167 = !DILocation(line: 143, scope: !5)
!168 = !DILocation(line: 144, scope: !5)
