; ModuleID = 'case_D'
source_filename = "case_D"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128-ni:10:11:12:13"
target triple = "x86_64-unknown-linux-gnu"

@"jl_global#551" = private unnamed_addr constant ptr @"jl_global#551.jit", !julia.constgv !0
@"jl_global#552" = private unnamed_addr constant ptr @"jl_global#552.jit", !julia.constgv !0
@"jl_global#554" = private unnamed_addr constant ptr @"jl_global#554.jit", !julia.constgv !0
@"jl_global#556" = private unnamed_addr constant ptr @"jl_global#556.jit", !julia.constgv !0
@"jl_global#558" = private unnamed_addr constant ptr @"jl_global#558.jit", !julia.constgv !0
@"_j_const#1" = private unnamed_addr constant i64 3, align 8
@"+Main.Base.RefValue#561" = private unnamed_addr constant ptr @"+Main.Base.RefValue#561.jit", !julia.constgv !0
@jlplt___bennett_ctrl_563_got = external global ptr #0
@"+Core.GenericMemory#564" = private unnamed_addr constant ptr @"+Core.GenericMemory#564.jit", !julia.constgv !0
@"+Core.Array#565" = private unnamed_addr constant ptr @"+Core.Array#565.jit", !julia.constgv !0
@"_j_const#3" = private unnamed_addr constant [1 x i64] [i64 4], align 8
@"jl_global#568" = private unnamed_addr constant ptr @"jl_global#568.jit", !julia.constgv !0

@"+Main.Base.RefValue#561.jit" = private alias ptr, inttoptr (i64 127079307385232 to ptr)
@"jl_global#552.jit" = private alias ptr, inttoptr (i64 127079338396112 to ptr)
@"jl_global#568.jit" = private alias ptr, inttoptr (i64 127079338459152 to ptr)
@"jl_global#554.jit" = private alias ptr, inttoptr (i64 127079338476416 to ptr)
@"jl_global#556.jit" = private alias ptr, inttoptr (i64 127079338544192 to ptr)
@"jl_global#558.jit" = private alias ptr, inttoptr (i64 127079338641680 to ptr)
@"jl_global#551.jit" = private alias ptr, inttoptr (i64 127079338975376 to ptr)
@"+Core.GenericMemory#564.jit" = private alias ptr, inttoptr (i64 127079420148128 to ptr)
@"+Core.Array#565.jit" = private alias ptr, inttoptr (i64 127079420430544 to ptr)

; Function Signature: case_D(UInt64)
define swiftcc i64 @julia_case_D_549(ptr nonnull swiftself "gcstack" %pgcstack_arg, i64 zeroext %"x::UInt64") #1 !dbg !7 {
top:
  %"new::Env" = alloca { ptr, i64, double }, align 8
  %"new::Array.size" = alloca i64, align 8
  %"new::Array.size21" = alloca i64, align 8
  %"new::Tuple" = alloca [1 x i64], align 8
  %"new::Tuple36" = alloca [1 x i64], align 8
  %current_task = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152
  %ptls_field = getelementptr inbounds i8, ptr %current_task, i32 168
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !16
  %0 = getelementptr inbounds i8, ptr %ptls_load, i32 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !20, !invariant.load !0
  fence syncscope("singlethread") seq_cst
  call void @julia.safepoint(ptr %safepoint)
  fence syncscope("singlethread") seq_cst
    #dbg_value(i64 %"x::UInt64", !15, !DIExpression(), !22)
  %"jl_global#551" = load ptr, ptr @"jl_global#551", align 8, !dbg !23, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0
  %1 = addrspacecast ptr %"jl_global#551" to ptr addrspace(10), !dbg !23
  %"jl_global#552" = load ptr, ptr @"jl_global#552", align 8, !dbg !23, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0
  %2 = addrspacecast ptr %"jl_global#552" to ptr addrspace(10), !dbg !23
  %3 = call ptr @julia_case_D_549u553(i64 4), !dbg !23
  %"jl_global#554" = load ptr, ptr @"jl_global#554", align 8, !dbg !35, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0
  %4 = addrspacecast ptr %"jl_global#554" to ptr addrspace(10), !dbg !35
  %"jl_global#5521" = load ptr, ptr @"jl_global#552", align 8, !dbg !35, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0
  %5 = addrspacecast ptr %"jl_global#5521" to ptr addrspace(10), !dbg !35
  call void @julia_case_D_549u555(ptr %3, i64 0), !dbg !35
  %6 = uitofp i64 %"x::UInt64" to double, !dbg !38
  %7 = fmul double %6, 1.250000e-01, !dbg !42
  %"jl_global#556" = load ptr, ptr @"jl_global#556", align 8, !dbg !44, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0
  %8 = addrspacecast ptr %"jl_global#556" to ptr addrspace(10), !dbg !44
  %"jl_global#5522" = load ptr, ptr @"jl_global#552", align 8, !dbg !44, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0
  %9 = addrspacecast ptr %"jl_global#5522" to ptr addrspace(10), !dbg !44
  call void @julia_case_D_549u557(ptr %3, double %7), !dbg !44
  %"jl_global#558" = load ptr, ptr @"jl_global#558", align 8, !dbg !47, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0
  %10 = addrspacecast ptr %"jl_global#558" to ptr addrspace(10), !dbg !47
  %"jl_global#5523" = load ptr, ptr @"jl_global#552", align 8, !dbg !47, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0
  %11 = addrspacecast ptr %"jl_global#5523" to ptr addrspace(10), !dbg !47
  %12 = call i8 @julia_case_D_549u559(ptr %3), !dbg !47
  %13 = trunc i8 %12 to i1, !dbg !49
  %14 = xor i1 %13, true, !dbg !49
  br i1 %14, label %top.L14_crit_edge, label %L12, !dbg !49

top.L14_crit_edge:                                ; preds = %top
  br label %L14, !dbg !49

L12:                                              ; preds = %top
  %"jl_global#5544" = load ptr, ptr @"jl_global#554", align 8, !dbg !50, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0
  %15 = addrspacecast ptr %"jl_global#5544" to ptr addrspace(10), !dbg !50
  %"jl_global#5525" = load ptr, ptr @"jl_global#552", align 8, !dbg !50, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0
  %16 = addrspacecast ptr %"jl_global#5525" to ptr addrspace(10), !dbg !50
  call void @julia_case_D_549u560(ptr %3, i64 2), !dbg !50
  br label %L14, !dbg !50

L14:                                              ; preds = %top.L14_crit_edge, %L12
  %value_phi = phi i64 [ 1, %L12 ], [ 0, %top.L14_crit_edge ]
  br label %L16, !dbg !52

L16:                                              ; preds = %L14
  br label %L17, !dbg !52

L17:                                              ; preds = %L16
  br label %L18, !dbg !52

L18:                                              ; preds = %L17
  br label %L19, !dbg !52

L19:                                              ; preds = %L18
  br label %L20, !dbg !52

L20:                                              ; preds = %L19
  %17 = getelementptr inbounds i8, ptr %"new::Env", i32 0, !dbg !62
  store ptr %3, ptr %17, align 8, !dbg !62, !tbaa !67, !alias.scope !69, !noalias !70
  %18 = getelementptr inbounds i8, ptr %"new::Env", i32 8, !dbg !62
  %"_j_const#1.copyload" = load i64, ptr @"_j_const#1", align 8, !dbg !62, !tbaa !71, !alias.scope !75, !noalias !76
  store i64 %"_j_const#1.copyload", ptr %18, align 8, !dbg !62, !tbaa !67, !alias.scope !69, !noalias !70
  %19 = getelementptr inbounds i8, ptr %"new::Env", i32 16, !dbg !62
  store double %7, ptr %19, align 8, !dbg !62, !tbaa !67, !alias.scope !69, !noalias !70
  br label %L22, !dbg !62

L22:                                              ; preds = %L20
  %"+Main.Base.RefValue#561" = load ptr, ptr @"+Main.Base.RefValue#561", align 8, !dbg !77, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0, !dereferenceable !84, !align !85
  %RefValue = ptrtoint ptr %"+Main.Base.RefValue#561" to i64, !dbg !77
  %20 = inttoptr i64 %RefValue to ptr, !dbg !77
  %current_task6 = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152, !dbg !77
  %21 = addrspacecast ptr %20 to ptr addrspace(10), !dbg !77
  %"new::RefValue" = call noalias nonnull align 8 dereferenceable(24) ptr addrspace(10) @julia.gc_alloc_obj(ptr %current_task6, i64 24, ptr addrspace(10) %21) #10, !dbg !77
  %22 = addrspacecast ptr addrspace(10) %"new::RefValue" to ptr addrspace(11), !dbg !77
  %23 = addrspacecast ptr addrspace(10) %"new::RefValue" to ptr addrspace(11), !dbg !77
  call void @llvm.memcpy.p11.p0.i64(ptr addrspace(11) align 8 %23, ptr align 8 %"new::Env", i64 24, i1 false), !dbg !77, !tbaa !86, !alias.scope !87, !noalias !88
  %24 = call token (...) @llvm.julia.gc_preserve_begin(ptr addrspace(10) %"new::RefValue"), !dbg !89
  %25 = addrspacecast ptr addrspace(10) %"new::RefValue" to ptr addrspace(11), !dbg !90
  %26 = call nonnull ptr @julia.pointer_from_objref(ptr addrspace(11) %25) #7, !dbg !90
  %__bennett_ctrl = load atomic ptr, ptr @jlplt___bennett_ctrl_563_got unordered, align 8, !dbg !95
  call void %__bennett_ctrl(ptr %3, i64 0, ptr inttoptr (i64 127079231243584 to ptr), i64 8, ptr %26), !dbg !95
  call void @llvm.julia.gc_preserve_end(token %24), !dbg !95
  br label %L28, !dbg !95

L28:                                              ; preds = %L22
  %"+Core.GenericMemory#564" = load ptr, ptr @"+Core.GenericMemory#564", align 8, !dbg !96, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0, !dereferenceable !84, !align !85
  %current_task7 = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152, !dbg !96
  %27 = addrspacecast ptr %"+Core.GenericMemory#564" to ptr addrspace(10), !dbg !96
  %"Memory{Ptr}[]" = call noalias nonnull align 16 dereferenceable(48) ptr addrspace(10) @julia.gc_alloc_obj(ptr %current_task7, i64 48, ptr addrspace(10) %27) #5, !dbg !96
  %28 = addrspacecast ptr addrspace(10) %"Memory{Ptr}[]" to ptr addrspace(11), !dbg !96
  %memory_ptr = getelementptr inbounds nuw { i64, ptr }, ptr addrspace(11) %28, i32 0, i32 1, !dbg !96
  %29 = addrspacecast ptr addrspace(10) %"Memory{Ptr}[]" to ptr addrspace(11), !dbg !96
  %30 = call nonnull ptr @julia.pointer_from_objref(ptr addrspace(11) %29) #7, !dbg !96
  %memory_data = getelementptr inbounds i8, ptr %30, i32 16, !dbg !96
  store ptr %memory_data, ptr addrspace(11) %memory_ptr, align 8, !dbg !96, !tbaa !101, !alias.scope !104, !noalias !105
  %31 = addrspacecast ptr addrspace(10) %"Memory{Ptr}[]" to ptr addrspace(11), !dbg !96
  %32 = getelementptr inbounds nuw { i64, ptr }, ptr addrspace(11) %31, i32 0, i32 0, !dbg !96
  store i64 4, ptr addrspace(11) %32, align 8, !dbg !96, !tbaa !106, !alias.scope !104, !noalias !105
  %33 = addrspacecast ptr addrspace(10) %"Memory{Ptr}[]" to ptr addrspace(11), !dbg !108
  %memory_data_ptr = getelementptr inbounds nuw { i64, ptr }, ptr addrspace(11) %33, i32 0, i32 1, !dbg !108
  %memory_data8 = load ptr, ptr addrspace(11) %memory_data_ptr, align 8, !dbg !108, !tbaa !101, !alias.scope !104, !noalias !105, !nonnull !0
  %34 = insertvalue { ptr, ptr addrspace(10) } zeroinitializer, ptr %memory_data8, 0, !dbg !108
  %memory_ref = insertvalue { ptr, ptr addrspace(10) } %34, ptr addrspace(10) %"Memory{Ptr}[]", 1, !dbg !108
  %"+Core.Array#565" = load ptr, ptr @"+Core.Array#565", align 8, !dbg !110, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0, !dereferenceable !84, !align !85
  %Array = ptrtoint ptr %"+Core.Array#565" to i64, !dbg !110
  %35 = inttoptr i64 %Array to ptr, !dbg !110
  %current_task9 = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152, !dbg !110
  %36 = addrspacecast ptr %35 to ptr addrspace(10), !dbg !110
  %"new::Array" = call noalias nonnull align 8 dereferenceable(24) ptr addrspace(10) @julia.gc_alloc_obj(ptr %current_task9, i64 24, ptr addrspace(10) %36) #10, !dbg !110
  %37 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !110
  %38 = getelementptr inbounds i8, ptr addrspace(11) %37, i32 8, !dbg !110
  store ptr addrspace(10) null, ptr addrspace(11) %38, align 8, !dbg !110, !tbaa !111, !alias.scope !104, !noalias !105
  %39 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !110
  store { ptr, ptr addrspace(10) } %memory_ref, ptr addrspace(11) %39, align 8, !dbg !110, !tbaa !112, !alias.scope !104, !noalias !105
  %40 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !110
  %"new::Array.size_ptr" = getelementptr inbounds i8, ptr addrspace(11) %40, i32 16, !dbg !110
  %"_j_const#3.copyload" = load i64, ptr @"_j_const#3", align 8, !dbg !110, !tbaa !71, !alias.scope !75, !noalias !76
  store i64 %"_j_const#3.copyload", ptr addrspace(11) %"new::Array.size_ptr", align 8, !dbg !110, !tbaa !114, !alias.scope !104, !noalias !105
  br label %L31, !dbg !110

L31:                                              ; preds = %L63, %L28
  %value_phi10 = phi i64 [ 1, %L28 ], [ %value_phi17, %L63 ]
  %value_phi11 = phi i64 [ 1, %L28 ], [ %value_phi18, %L63 ]
  %"jl_global#55112" = load ptr, ptr @"jl_global#551", align 8, !dbg !116, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0
  %41 = addrspacecast ptr %"jl_global#55112" to ptr addrspace(10), !dbg !116
  %"jl_global#55213" = load ptr, ptr @"jl_global#552", align 8, !dbg !116, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0
  %42 = addrspacecast ptr %"jl_global#55213" to ptr addrspace(10), !dbg !116
  %43 = call ptr @julia_case_D_549u566(i64 1), !dbg !116
  br i1 false, label %L48, label %L37, !dbg !118

L37:                                              ; preds = %L31
  %44 = sub i64 %value_phi10, 1, !dbg !123
  %45 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !126
  %"new::Array.size_ptr14" = getelementptr inbounds i8, ptr addrspace(11) %45, i32 16, !dbg !126
  %"new::Array.size_ptr14.copyload" = load i64, ptr addrspace(11) %"new::Array.size_ptr14", align 8, !dbg !126, !tbaa !114, !alias.scope !104, !noalias !105
  store i64 %"new::Array.size_ptr14.copyload", ptr %"new::Array.size", align 8, !dbg !126, !tbaa !67, !alias.scope !69, !noalias !70
  %bitcast = load i64, ptr %"new::Array.size", align 8, !dbg !123, !tbaa !67, !alias.scope !69, !noalias !70
  %46 = icmp ult i64 %44, %bitcast, !dbg !123
  %47 = xor i1 %46, true, !dbg !118
  br i1 %47, label %L45, label %L44, !dbg !118

L44:                                              ; preds = %L37
  br label %L48, !dbg !118

L45:                                              ; preds = %L37
  %48 = getelementptr inbounds i8, ptr %"new::Tuple36", i32 0, !dbg !118
  store i64 %value_phi10, ptr %48, align 8, !dbg !118, !tbaa !67, !alias.scope !69, !noalias !70
  %49 = addrspacecast ptr %"new::Tuple36" to ptr addrspace(11), !dbg !118
  call swiftcc void @j_throw_boundserror_570(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr addrspace(10) %"new::Array", ptr addrspace(11) nocapture readonly %49) #11, !dbg !118
  call void @llvm.trap(), !dbg !118
  unreachable, !dbg !118

L48:                                              ; preds = %L44, %L31
  %50 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !130
  %51 = getelementptr inbounds nuw { ptr, ptr addrspace(10) }, ptr addrspace(11) %50, i32 0, i32 0, !dbg !130
  %memoryref_data = load ptr, ptr addrspace(11) %51, align 8, !dbg !130, !tbaa !112, !alias.scope !104, !noalias !105
  %52 = getelementptr inbounds nuw { ptr, ptr addrspace(10) }, ptr addrspace(11) %50, i32 0, i32 1, !dbg !130
  %memoryref_mem = load ptr addrspace(10), ptr addrspace(11) %52, align 8, !dbg !130, !tbaa !112, !alias.scope !104, !noalias !105, !dereferenceable_or_null !85, !align !134
  %53 = insertvalue { ptr, ptr addrspace(10) } zeroinitializer, ptr %memoryref_data, 0, !dbg !130
  %"new::Array.ref" = insertvalue { ptr, ptr addrspace(10) } %53, ptr addrspace(10) %memoryref_mem, 1, !dbg !130
  %memoryref_offset = sub i64 %value_phi10, 1, !dbg !133
  %memoryref_byteoffset = mul i64 %memoryref_offset, 8, !dbg !133
  %memoryref_data_byteoffset = getelementptr i8, ptr %memoryref_data, i64 %memoryref_byteoffset, !dbg !133
  %54 = insertvalue { ptr, ptr addrspace(10) } zeroinitializer, ptr %memoryref_data_byteoffset, 0, !dbg !133
  %memory_ref15 = insertvalue { ptr, ptr addrspace(10) } %54, ptr addrspace(10) %memoryref_mem, 1, !dbg !133
  %55 = addrspacecast ptr addrspace(10) %memoryref_mem to ptr addrspace(11), !dbg !133
  %56 = getelementptr inbounds nuw { i64, ptr }, ptr addrspace(11) %55, i32 0, i32 0, !dbg !133
  %memory_len = load i64, ptr addrspace(11) %56, align 8, !dbg !133, !tbaa !106, !range !135, !alias.scope !104, !noalias !105
  %57 = call ptr addrspace(13) @julia.gc_loaded(ptr addrspace(10) %memoryref_mem, ptr %memoryref_data), !dbg !133
  %memoryref_data16 = getelementptr inbounds i8, ptr addrspace(13) %57, i64 %memoryref_byteoffset, !dbg !133
  store ptr %43, ptr addrspace(13) %memoryref_data16, align 8, !dbg !133, !tbaa !136, !alias.scope !75, !noalias !76
  br label %L52, !dbg !138

L52:                                              ; preds = %L48
  br label %L53, !dbg !121

L53:                                              ; preds = %L52
  %58 = icmp eq i64 %value_phi11, 4, !dbg !139
  %59 = xor i1 %58, true, !dbg !142
  br i1 %59, label %L56, label %L55, !dbg !142

L55:                                              ; preds = %L53
  br label %L58, !dbg !142

L56:                                              ; preds = %L53
  %60 = add i64 %value_phi11, 1, !dbg !145
  br label %L58, !dbg !142

L58:                                              ; preds = %L56, %L55
  %value_phi17 = phi i64 [ %60, %L56 ], [ undef, %L55 ]
  %value_phi18 = phi i64 [ %60, %L56 ], [ undef, %L55 ]
  %value_phi19 = phi i8 [ 1, %L55 ], [ 0, %L56 ]
  %61 = trunc i8 %value_phi19 to i1, !dbg !117
  %62 = xor i1 %61, true, !dbg !117
  %63 = xor i1 %62, true, !dbg !117
  br i1 %63, label %L64, label %L63, !dbg !117

L63:                                              ; preds = %L58
  br label %L31, !dbg !117

L64:                                              ; preds = %L58
  %64 = and i64 %"x::UInt64", 3, !dbg !149
  %65 = add i64 %64, 1, !dbg !153
  br i1 false, label %L81, label %L69, !dbg !155

L69:                                              ; preds = %L64
  %66 = sub i64 %65, 1, !dbg !160
  %67 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !162
  %"new::Array.size_ptr20" = getelementptr inbounds i8, ptr addrspace(11) %67, i32 16, !dbg !162
  %"new::Array.size_ptr20.copyload" = load i64, ptr addrspace(11) %"new::Array.size_ptr20", align 8, !dbg !162, !tbaa !114, !alias.scope !104, !noalias !105
  store i64 %"new::Array.size_ptr20.copyload", ptr %"new::Array.size21", align 8, !dbg !162, !tbaa !67, !alias.scope !69, !noalias !70
  %bitcast22 = load i64, ptr %"new::Array.size21", align 8, !dbg !160, !tbaa !67, !alias.scope !69, !noalias !70
  %68 = icmp ult i64 %66, %bitcast22, !dbg !160
  %69 = xor i1 %68, true, !dbg !161
  br i1 %69, label %L77, label %L76, !dbg !161

L76:                                              ; preds = %L69
  br label %L80, !dbg !161

L77:                                              ; preds = %L69
  %70 = getelementptr inbounds i8, ptr %"new::Tuple", i32 0, !dbg !161
  store i64 %65, ptr %70, align 8, !dbg !161, !tbaa !67, !alias.scope !69, !noalias !70
  %71 = addrspacecast ptr %"new::Tuple" to ptr addrspace(11), !dbg !161
  call swiftcc void @j_throw_boundserror_570(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr addrspace(10) %"new::Array", ptr addrspace(11) nocapture readonly %71) #11, !dbg !161
  call void @llvm.trap(), !dbg !161
  unreachable, !dbg !161

L80:                                              ; preds = %L76
  br label %L81, !dbg !161

L81:                                              ; preds = %L80, %L64
  %72 = addrspacecast ptr addrspace(10) %"new::Array" to ptr addrspace(11), !dbg !164
  %73 = getelementptr inbounds nuw { ptr, ptr addrspace(10) }, ptr addrspace(11) %72, i32 0, i32 0, !dbg !164
  %memoryref_data24 = load ptr, ptr addrspace(11) %73, align 8, !dbg !164, !tbaa !112, !alias.scope !104, !noalias !105
  %74 = getelementptr inbounds nuw { ptr, ptr addrspace(10) }, ptr addrspace(11) %72, i32 0, i32 1, !dbg !164
  %memoryref_mem30 = load ptr addrspace(10), ptr addrspace(11) %74, align 8, !dbg !164, !tbaa !112, !alias.scope !104, !noalias !105, !dereferenceable_or_null !85, !align !134
  %75 = insertvalue { ptr, ptr addrspace(10) } zeroinitializer, ptr %memoryref_data24, 0, !dbg !164
  %"new::Array.ref23" = insertvalue { ptr, ptr addrspace(10) } %75, ptr addrspace(10) %memoryref_mem30, 1, !dbg !164
  %memoryref_offset26 = sub i64 %65, 1, !dbg !164
  %memoryref_byteoffset27 = mul i64 %memoryref_offset26, 8, !dbg !164
  %memoryref_data_byteoffset28 = getelementptr i8, ptr %memoryref_data24, i64 %memoryref_byteoffset27, !dbg !164
  %76 = insertvalue { ptr, ptr addrspace(10) } zeroinitializer, ptr %memoryref_data_byteoffset28, 0, !dbg !164
  %memory_ref29 = insertvalue { ptr, ptr addrspace(10) } %76, ptr addrspace(10) %memoryref_mem30, 1, !dbg !164
  %77 = addrspacecast ptr addrspace(10) %memoryref_mem30 to ptr addrspace(11), !dbg !164
  %78 = getelementptr inbounds nuw { i64, ptr }, ptr addrspace(11) %77, i32 0, i32 0, !dbg !164
  %memory_len31 = load i64, ptr addrspace(11) %78, align 8, !dbg !164, !tbaa !106, !range !135, !alias.scope !104, !noalias !105
  %79 = call ptr addrspace(13) @julia.gc_loaded(ptr addrspace(10) %memoryref_mem30, ptr %memoryref_data24), !dbg !164
  %memoryref_data32 = getelementptr inbounds i8, ptr addrspace(13) %79, i64 %memoryref_byteoffset27, !dbg !164
  %80 = load ptr, ptr addrspace(13) %memoryref_data32, align 8, !dbg !164, !tbaa !136, !alias.scope !75, !noalias !76
  br label %L85, !dbg !164

L85:                                              ; preds = %L81
  br label %L86, !dbg !164

L86:                                              ; preds = %L85
  %"jl_global#55433" = load ptr, ptr @"jl_global#554", align 8, !dbg !165, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0
  %81 = addrspacecast ptr %"jl_global#55433" to ptr addrspace(10), !dbg !165
  %"jl_global#55234" = load ptr, ptr @"jl_global#552", align 8, !dbg !165, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0
  %82 = addrspacecast ptr %"jl_global#55234" to ptr addrspace(10), !dbg !165
  call void @julia_case_D_549u567(ptr %80, i64 0), !dbg !165
  %"jl_global#568" = load ptr, ptr @"jl_global#568", align 8, !dbg !166, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0
  %83 = addrspacecast ptr %"jl_global#568" to ptr addrspace(10), !dbg !166
  %"jl_global#55235" = load ptr, ptr @"jl_global#552", align 8, !dbg !166, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0
  %84 = addrspacecast ptr %"jl_global#55235" to ptr addrspace(10), !dbg !166
  call void @julia_case_D_549u569(ptr %3), !dbg !166
  ret i64 %value_phi, !dbg !169

after_noret:                                      ; No predecessors!
  call void @llvm.trap(), !dbg !161
  unreachable, !dbg !161

after_noret37:                                    ; No predecessors!
  call void @llvm.trap(), !dbg !118
  unreachable, !dbg !118
}

; Function Attrs: noinline optnone
define nonnull ptr addrspace(10) @jfptr_case_D_550(ptr addrspace(10) %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") #2 {
top:
  %pgcstack = call ptr @julia.get_pgcstack()
  %0 = load ptr addrspace(10), ptr %"args::Any[]", align 8, !tbaa !20, !invariant.load !0, !alias.scope !27, !noalias !30, !nonnull !0, !dereferenceable !134, !align !134
  %.unbox = load i64, ptr addrspace(10) %0, align 8, !tbaa !71, !alias.scope !75, !noalias !76
  %1 = call swiftcc i64 @julia_case_D_549(ptr nonnull swiftself "gcstack" %pgcstack, i64 zeroext %.unbox)
  %box_UInt64 = call nonnull align 8 dereferenceable(8) ptr addrspace(10) @ijl_box_uint64(i64 zeroext %1) #3
  ret ptr addrspace(10) %box_UInt64
}

declare ptr @julia.get_pgcstack()

; Function Attrs: nounwind willreturn memory(read, inaccessiblemem: readwrite)
declare nonnull align 8 dereferenceable(8) ptr addrspace(10) @ijl_box_uint64(i64 zeroext) #3

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) #4

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr addrspace(10) @julia.gc_alloc_obj(ptr, i64, ptr addrspace(10)) #5

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p11.p0.i64(ptr addrspace(11) noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #6

declare token @llvm.julia.gc_preserve_begin(...)

; Function Attrs: norecurse nosync nounwind speculatable willreturn memory(none)
declare nonnull ptr @julia.pointer_from_objref(ptr addrspace(11)) #7

declare void @llvm.julia.gc_preserve_end(token)

; Function Attrs: norecurse nosync nounwind speculatable willreturn memory(none)
declare noundef nonnull ptr addrspace(13) @julia.gc_loaded(ptr addrspace(10) nocapture noundef nonnull readnone, ptr noundef nonnull readnone) #7

; Function Signature: throw_boundserror(Array{Ptr{Nothing}, 1}, Tuple{Int64})
; Function Attrs: noreturn
declare swiftcc void @j_throw_boundserror_570(ptr nonnull swiftself "gcstack", ptr addrspace(10), ptr addrspace(11) nocapture readonly) #8

; Function Attrs: cold noreturn nounwind memory(inaccessiblemem: write)
declare void @llvm.trap() #9

define internal ptr @julia_case_D_549u553(i64 %0) {
  %r = call ptr @__bennett_qalloc(i64 0, i64 %0)
  ret ptr %r
}

declare ptr @__bennett_qalloc(i64, i64)

define internal void @julia_case_D_549u555(ptr %0, i64 %1) {
  call void @__bennett_gate(i32 1, ptr %0, i64 %1)
  ret void
}

declare void @__bennett_gate(i32, ptr, i64)

define internal void @julia_case_D_549u557(ptr %0, double %1) {
  call void @__bennett_rot(i32 3, ptr %0, i64 1, double %1)
  ret void
}

declare void @__bennett_rot(i32, ptr, i64, double)

define internal zeroext i1 @julia_case_D_549u559(ptr %0) {
  %r = call zeroext i1 @__bennett_measure(ptr %0, i64 0)
  ret i1 %r
}

declare zeroext i1 @__bennett_measure(ptr, i64)

define internal void @julia_case_D_549u560(ptr %0, i64 %1) {
  call void @__bennett_gate(i32 1, ptr %0, i64 %1)
  ret void
}

define internal ptr @julia_case_D_549u566(i64 %0) {
  %r = call ptr @__bennett_qalloc(i64 0, i64 %0)
  ret ptr %r
}

define internal void @julia_case_D_549u567(ptr %0, i64 %1) {
  call void @__bennett_gate(i32 1, ptr %0, i64 %1)
  ret void
}

define internal void @julia_case_D_549u569(ptr %0) {
  call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr %0, i64 0, ptr null, i64 8, i32 1, double 2.500000e+00, ptr %0)
  ret void
}

declare void @__bennett_ctrl_v(ptr, i64, ptr, i64, ...)

attributes #0 = { "julia.fname"="__bennett_ctrl" "julia.libidx"="0" }
attributes #1 = { "frame-pointer"="all" "julia.fsig"="case_D(UInt64)" "probe-stack"="inline-asm" }
attributes #2 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #3 = { nounwind willreturn memory(read, inaccessiblemem: readwrite) }
attributes #4 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #5 = { nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #6 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { norecurse nosync nounwind speculatable willreturn memory(none) }
attributes #8 = { noreturn "frame-pointer"="all" "julia.fsig"="throw_boundserror(Array{Ptr{Nothing}, 1}, Tuple{Int64})" "probe-stack"="inline-asm" }
attributes #9 = { cold noreturn nounwind memory(inaccessiblemem: write) }
attributes #10 = { nounwind willreturn allockind("alloc,uninitialized") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #11 = { noreturn }

!llvm.module.flags = !{!1, !2, !3, !4}
!llvm.dbg.cu = !{!5}

!0 = !{}
!1 = !{i32 2, !"Dwarf Version", i32 4}
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = !{i32 1, !"stack-protector-guard", !""}
!4 = !{i32 1, !"override-stack-alignment", i32 0}
!5 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !6, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!6 = !DIFile(filename: "julia", directory: ".")
!7 = distinct !DISubprogram(name: "case_D", linkageName: "julia_case_D_549", scope: null, file: !8, line: 146, type: !9, scopeLine: 146, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5, retainedNodes: !13)
!8 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!9 = !DISubroutineType(types: !10)
!10 = !{!11, !12, !11}
!11 = !DIBasicType(name: "UInt64", size: 64, encoding: DW_ATE_unsigned)
!12 = !DICompositeType(tag: DW_TAG_structure_type, name: "#case_D", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079337970704")
!13 = !{!14, !15}
!14 = !DILocalVariable(name: "#self#", arg: 1, scope: !7, file: !8, line: 146, type: !12)
!15 = !DILocalVariable(name: "x", arg: 2, scope: !7, file: !8, line: 146, type: !11)
!16 = !{!17, !17, i64 0}
!17 = !{!"jtbaa_gcframe", !18, i64 0}
!18 = !{!"jtbaa", !19, i64 0}
!19 = !{!"jtbaa"}
!20 = !{!21, !21, i64 0, i64 1}
!21 = !{!"jtbaa_const", !18, i64 0}
!22 = !DILocation(line: 146, scope: !7)
!23 = !DILocation(line: 30, scope: !24, inlinedAt: !26)
!24 = distinct !DISubprogram(name: "rD_alloc;", linkageName: "rD_alloc", scope: !8, file: !8, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!25 = !DISubroutineType(types: !0)
!26 = !DILocation(line: 147, scope: !7)
!27 = !{!28}
!28 = !{!"jnoalias_const", !29}
!29 = !{!"jnoalias"}
!30 = !{!31, !32, !33, !34}
!31 = !{!"jnoalias_gcframe", !29}
!32 = !{!"jnoalias_stack", !29}
!33 = !{!"jnoalias_data", !29}
!34 = !{!"jnoalias_typemd", !29}
!35 = !DILocation(line: 35, scope: !36, inlinedAt: !37)
!36 = distinct !DISubprogram(name: "rD_gate;", linkageName: "rD_gate", scope: !8, file: !8, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!37 = !DILocation(line: 148, scope: !7)
!38 = !DILocation(line: 251, scope: !39, inlinedAt: !41)
!39 = distinct !DISubprogram(name: "Float64;", linkageName: "Float64", scope: !40, file: !40, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!40 = !DIFile(filename: "float.jl", directory: ".")
!41 = !DILocation(line: 149, scope: !7)
!42 = !DILocation(line: 494, scope: !43, inlinedAt: !41)
!43 = distinct !DISubprogram(name: "*;", linkageName: "*", scope: !40, file: !40, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!44 = !DILocation(line: 45, scope: !45, inlinedAt: !46)
!45 = distinct !DISubprogram(name: "rD_rot;", linkageName: "rD_rot", scope: !8, file: !8, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!46 = !DILocation(line: 150, scope: !7)
!47 = !DILocation(line: 40, scope: !48, inlinedAt: !49)
!48 = distinct !DISubprogram(name: "rD_measure;", linkageName: "rD_measure", scope: !8, file: !8, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!49 = !DILocation(line: 152, scope: !7)
!50 = !DILocation(line: 35, scope: !36, inlinedAt: !51)
!51 = !DILocation(line: 153, scope: !7)
!52 = !DILocation(line: 874, scope: !53, inlinedAt: !55)
!53 = distinct !DISubprogram(name: "check_sign_bit;", linkageName: "check_sign_bit", scope: !54, file: !54, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!54 = !DIFile(filename: "boot.jl", directory: ".")
!55 = !DILocation(line: 985, scope: !56, inlinedAt: !57)
!56 = distinct !DISubprogram(name: "toUInt64;", linkageName: "toUInt64", scope: !54, file: !54, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!57 = !DILocation(line: 1015, scope: !58, inlinedAt: !59)
!58 = distinct !DISubprogram(name: "UInt64;", linkageName: "UInt64", scope: !54, file: !54, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!59 = !DILocation(line: 7, scope: !60, inlinedAt: !62)
!60 = distinct !DISubprogram(name: "convert;", linkageName: "convert", scope: !61, file: !61, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!61 = !DIFile(filename: "number.jl", directory: ".")
!62 = !DILocation(line: 75, scope: !63, inlinedAt: !64)
!63 = distinct !DISubprogram(name: "Env;", linkageName: "Env", scope: !8, file: !8, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!64 = !DILocation(line: 84, scope: !65, inlinedAt: !66)
!65 = distinct !DISubprogram(name: "rF_ctrl;", linkageName: "rF_ctrl", scope: !8, file: !8, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!66 = !DILocation(line: 155, scope: !7)
!67 = !{!68, !68, i64 0}
!68 = !{!"jtbaa_stack", !18, i64 0}
!69 = !{!32}
!70 = !{!31, !33, !34, !28}
!71 = !{!72, !72, i64 0}
!72 = !{!"jtbaa_immut", !73, i64 0}
!73 = !{!"jtbaa_value", !74, i64 0}
!74 = !{!"jtbaa_data", !18, i64 0}
!75 = !{!33}
!76 = !{!31, !32, !34, !28}
!77 = !DILocation(line: 8, scope: !78, inlinedAt: !80)
!78 = distinct !DISubprogram(name: "RefValue;", linkageName: "RefValue", scope: !79, file: !79, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!79 = !DIFile(filename: "refvalue.jl", directory: ".")
!80 = !DILocation(line: 10, scope: !78, inlinedAt: !81)
!81 = !DILocation(line: 145, scope: !82, inlinedAt: !64)
!82 = distinct !DISubprogram(name: "Ref;", linkageName: "Ref", scope: !83, file: !83, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!83 = !DIFile(filename: "refpointer.jl", directory: ".")
!84 = !{i64 56}
!85 = !{i64 16}
!86 = !{!18, !18, i64 0}
!87 = !{!32, !33}
!88 = !{!31, !34, !28}
!89 = !DILocation(line: 85, scope: !65, inlinedAt: !66)
!90 = !DILocation(line: 302, scope: !91, inlinedAt: !93)
!91 = distinct !DISubprogram(name: "pointer_from_objref;", linkageName: "pointer_from_objref", scope: !92, file: !92, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!92 = !DIFile(filename: "pointer.jl", directory: ".")
!93 = !DILocation(line: 40, scope: !94, inlinedAt: !95)
!94 = distinct !DISubprogram(name: "unsafe_convert;", linkageName: "unsafe_convert", scope: !79, file: !79, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!95 = !DILocation(line: 86, scope: !65, inlinedAt: !66)
!96 = !DILocation(line: 588, scope: !97, inlinedAt: !98)
!97 = distinct !DISubprogram(name: "GenericMemory;", linkageName: "GenericMemory", scope: !54, file: !54, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!98 = !DILocation(line: 648, scope: !99, inlinedAt: !100)
!99 = distinct !DISubprogram(name: "Array;", linkageName: "Array", scope: !54, file: !54, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!100 = !DILocation(line: 156, scope: !7)
!101 = !{!102, !102, i64 0}
!102 = !{!"jtbaa_memoryptr", !103, i64 0}
!103 = !{!"jtbaa_array", !18, i64 0}
!104 = !{!34}
!105 = !{!31, !32, !33, !28}
!106 = !{!107, !107, i64 0}
!107 = !{!"jtbaa_memorylen", !103, i64 0}
!108 = !DILocation(line: 594, scope: !109, inlinedAt: !110)
!109 = distinct !DISubprogram(name: "memoryref;", linkageName: "memoryref", scope: !54, file: !54, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!110 = !DILocation(line: 649, scope: !99, inlinedAt: !100)
!111 = !{!103, !103, i64 0}
!112 = !{!113, !113, i64 0}
!113 = !{!"jtbaa_arrayptr", !103, i64 0}
!114 = !{!115, !115, i64 0}
!115 = !{!"jtbaa_arraysize", !103, i64 0}
!116 = !DILocation(line: 30, scope: !24, inlinedAt: !117)
!117 = !DILocation(line: 157, scope: !7)
!118 = !DILocation(line: 1024, scope: !119, inlinedAt: !121)
!119 = distinct !DISubprogram(name: "_setindex!;", linkageName: "_setindex!", scope: !120, file: !120, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!120 = !DIFile(filename: "array.jl", directory: ".")
!121 = !DILocation(line: 1020, scope: !122, inlinedAt: !117)
!122 = distinct !DISubprogram(name: "setindex!;", linkageName: "setindex!", scope: !120, file: !120, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!123 = !DILocation(line: 385, scope: !124, inlinedAt: !118)
!124 = distinct !DISubprogram(name: "checkbounds;", linkageName: "checkbounds", scope: !125, file: !125, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!125 = !DIFile(filename: "essentials.jl", directory: ".")
!126 = !DILocation(line: 10, scope: !127, inlinedAt: !128)
!127 = distinct !DISubprogram(name: "size;", linkageName: "size", scope: !125, file: !125, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!128 = !DILocation(line: 11, scope: !129, inlinedAt: !123)
!129 = distinct !DISubprogram(name: "length;", linkageName: "length", scope: !125, file: !125, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!130 = !DILocation(line: 57, scope: !131, inlinedAt: !133)
!131 = distinct !DISubprogram(name: "getproperty;", linkageName: "getproperty", scope: !132, file: !132, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!132 = !DIFile(filename: "Base_compiler.jl", directory: ".")
!133 = !DILocation(line: 1025, scope: !119, inlinedAt: !121)
!134 = !{i64 8}
!135 = !{i64 0, i64 1152921504606846975}
!136 = !{!137, !137, i64 0}
!137 = !{!"jtbaa_arraybuf", !74, i64 0}
!138 = !DILocation(line: 1026, scope: !119, inlinedAt: !121)
!139 = !DILocation(line: 641, scope: !140, inlinedAt: !142)
!140 = distinct !DISubprogram(name: "==;", linkageName: "==", scope: !141, file: !141, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!141 = !DIFile(filename: "promotion.jl", directory: ".")
!142 = !DILocation(line: 928, scope: !143, inlinedAt: !117)
!143 = distinct !DISubprogram(name: "iterate;", linkageName: "iterate", scope: !144, file: !144, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!144 = !DIFile(filename: "range.jl", directory: ".")
!145 = !DILocation(line: 87, scope: !146, inlinedAt: !148)
!146 = distinct !DISubprogram(name: "+;", linkageName: "+", scope: !147, file: !147, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!147 = !DIFile(filename: "int.jl", directory: ".")
!148 = !DILocation(line: 929, scope: !143, inlinedAt: !117)
!149 = !DILocation(line: 393, scope: !150, inlinedAt: !151)
!150 = distinct !DISubprogram(name: "&;", linkageName: "&", scope: !147, file: !147, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!151 = !DILocation(line: 1058, scope: !150, inlinedAt: !152)
!152 = !DILocation(line: 158, scope: !7)
!153 = !DILocation(line: 87, scope: !146, inlinedAt: !154)
!154 = !DILocation(line: 1058, scope: !146, inlinedAt: !152)
!155 = !DILocation(line: 974, scope: !156, inlinedAt: !157)
!156 = distinct !DISubprogram(name: "getindex;", linkageName: "getindex", scope: !125, file: !125, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!157 = !DILocation(line: 1366, scope: !158, inlinedAt: !152)
!158 = distinct !DISubprogram(name: "getindex;", linkageName: "getindex", scope: !159, file: !159, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!159 = !DIFile(filename: "abstractarray.jl", directory: ".")
!160 = !DILocation(line: 385, scope: !124, inlinedAt: !161)
!161 = !DILocation(line: 389, scope: !124, inlinedAt: !155)
!162 = !DILocation(line: 10, scope: !127, inlinedAt: !163)
!163 = !DILocation(line: 11, scope: !129, inlinedAt: !160)
!164 = !DILocation(line: 975, scope: !156, inlinedAt: !157)
!165 = !DILocation(line: 35, scope: !36, inlinedAt: !152)
!166 = !DILocation(line: 113, scope: !167, inlinedAt: !168)
!167 = distinct !DISubprogram(name: "rH5_ctrl_v;", linkageName: "rH5_ctrl_v", scope: !8, file: !8, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!168 = !DILocation(line: 159, scope: !7)
!169 = !DILocation(line: 160, scope: !7)
