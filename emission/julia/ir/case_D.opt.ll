; ModuleID = 'case_D'
source_filename = "case_D"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@jlplt___bennett_ctrl_585_got = external local_unnamed_addr global ptr #0

@"+Core.GenericMemory#586.jit" = private alias ptr, inttoptr (i64 127079420148128 to ptr)
@"+Core.Array#587.jit" = private alias ptr, inttoptr (i64 127079420430544 to ptr)

; Function Signature: case_D(UInt64)
define swiftcc range(i64 0, 2) i64 @julia_case_D_571(ptr nonnull swiftself "gcstack" %pgcstack_arg, i64 zeroext %"x::UInt64") local_unnamed_addr #1 !dbg !6 {
top:
  %gcframe1 = alloca [3 x ptr], align 16
  call void @llvm.memset.p0.i64(ptr align 16 %gcframe1, i8 0, i64 24, i1 true)
  store i64 4, ptr %gcframe1, align 8, !tbaa !16
  %frame.prev = getelementptr inbounds nuw i8, ptr %gcframe1, i64 8
  %task.gcstack = load ptr, ptr %pgcstack_arg, align 8
  store ptr %task.gcstack, ptr %frame.prev, align 8, !tbaa !16
  store ptr %gcframe1, ptr %pgcstack_arg, align 8
  %"new::RefValue" = alloca [3 x i64], align 16, !dbg !20
  %"new::Tuple" = alloca [1 x i64], align 8
  %"new::Tuple36" = alloca [1 x i64], align 8
  %ptls_field = getelementptr inbounds nuw i8, ptr %pgcstack_arg, i64 16
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !16
  %0 = getelementptr inbounds nuw i8, ptr %ptls_load, i64 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !31, !invariant.load !12
  fence syncscope("singlethread") seq_cst
  %1 = load volatile i64, ptr %safepoint, align 8
  fence syncscope("singlethread") seq_cst
    #dbg_value(i64 %"x::UInt64", !15, !DIExpression(), !33)
  %2 = call fastcc ptr @julia_case_D_571u575(i64 4), !dbg !34
  call fastcc void @julia_case_D_571u577(ptr %2, i64 0), !dbg !37
  %3 = uitofp i64 %"x::UInt64" to double, !dbg !40
  %4 = fmul double %3, 1.250000e-01, !dbg !44
  call fastcc void @julia_case_D_571u579(ptr %2, double %4), !dbg !46
  %5 = call i8 @julia_case_D_571u581(ptr %2), !dbg !49
  %6 = trunc i8 %5 to i1, !dbg !51
  br i1 %6, label %L12, label %L20, !dbg !51

L12:                                              ; preds = %top
  call fastcc void @julia_case_D_571u582(ptr %2, i64 2), !dbg !52
  br label %L20, !dbg !52

L20:                                              ; preds = %L12, %top
  %value_phi = phi i64 [ 1, %L12 ], [ 0, %top ]
  call void @llvm.lifetime.start.p0(i64 24, ptr nonnull %"new::RefValue")
  store ptr %2, ptr %"new::RefValue", align 8, !dbg !20, !tbaa !54, !alias.scope !55, !noalias !59
  %"new::Env.sroa.2.0..sroa_idx" = getelementptr inbounds nuw i8, ptr %"new::RefValue", i64 8, !dbg !20
  store i64 3, ptr %"new::Env.sroa.2.0..sroa_idx", align 8, !dbg !20, !tbaa !54, !alias.scope !55, !noalias !59
  %"new::Env.sroa.3.0..sroa_idx" = getelementptr inbounds nuw i8, ptr %"new::RefValue", i64 16, !dbg !20
  store double %4, ptr %"new::Env.sroa.3.0..sroa_idx", align 8, !dbg !20, !tbaa !54, !alias.scope !55, !noalias !59
  %__bennett_ctrl = load atomic ptr, ptr @jlplt___bennett_ctrl_585_got unordered, align 8, !dbg !63
  call void %__bennett_ctrl(ptr %2, i64 0, ptr nonnull inttoptr (i64 127079231243584 to ptr), i64 8, ptr nonnull %"new::RefValue"), !dbg !63
  call void @llvm.lifetime.end.p0(i64 24, ptr nonnull %"new::RefValue")
  %ptls_load58 = load ptr, ptr %ptls_field, align 8, !dbg !64, !tbaa !16
  %"Memory{Ptr}[]" = call noalias nonnull align 8 dereferenceable(64) ptr @ijl_gc_small_alloc(ptr %ptls_load58, i32 504, i32 64, i64 127079420148128) #9, !dbg !64
  %"Memory{Ptr}[].tag_addr" = getelementptr inbounds i8, ptr %"Memory{Ptr}[]", i64 -8, !dbg !64
  store atomic i64 127079420148128, ptr %"Memory{Ptr}[].tag_addr" unordered, align 8, !dbg !64, !tbaa !70
  %memory_ptr = getelementptr inbounds nuw i8, ptr %"Memory{Ptr}[]", i64 8, !dbg !64
  %memory_data = getelementptr inbounds nuw i8, ptr %"Memory{Ptr}[]", i64 16, !dbg !64
  store ptr %memory_data, ptr %memory_ptr, align 8, !dbg !64, !tbaa !73, !alias.scope !76, !noalias !77
  store i64 4, ptr %"Memory{Ptr}[]", align 8, !dbg !64, !tbaa !78, !alias.scope !76, !noalias !77
  %gc_slot_addr_0 = getelementptr inbounds nuw i8, ptr %gcframe1, i64 16
  store ptr %"Memory{Ptr}[]", ptr %gc_slot_addr_0, align 8
  %"new::Array" = call noalias nonnull align 8 dereferenceable(32) ptr @ijl_gc_small_alloc(ptr %ptls_load58, i32 408, i32 32, i64 127079420430544) #9, !dbg !80
  %"new::Array.tag_addr" = getelementptr inbounds i8, ptr %"new::Array", i64 -8, !dbg !80
  store atomic i64 127079420430544, ptr %"new::Array.tag_addr" unordered, align 8, !dbg !80, !tbaa !70
  %7 = getelementptr inbounds nuw i8, ptr %"new::Array", i64 8, !dbg !80
  store ptr %memory_data, ptr %"new::Array", align 8, !dbg !80, !tbaa !81, !alias.scope !76, !noalias !77
  store ptr %"Memory{Ptr}[]", ptr %7, align 8, !dbg !80, !tbaa !81, !alias.scope !76, !noalias !77
  %"new::Array.size_ptr" = getelementptr inbounds nuw i8, ptr %"new::Array", i64 16, !dbg !80
  store i64 4, ptr %"new::Array.size_ptr", align 8, !dbg !80, !tbaa !83, !alias.scope !76, !noalias !77
  br label %L31, !dbg !80

L31:                                              ; preds = %L48, %L20
  %value_phi10 = phi i64 [ 1, %L20 ], [ %10, %L48 ]
  store ptr %"new::Array", ptr %gc_slot_addr_0, align 8
  %8 = call fastcc ptr @julia_case_D_571u588(i64 1), !dbg !85
  %9 = add nsw i64 %value_phi10, -1, !dbg !87
  %"new::Array.size_ptr14.copyload" = load i64, ptr %"new::Array.size_ptr", align 8, !dbg !95, !tbaa !83, !alias.scope !76, !noalias !77
  %.not = icmp ult i64 %9, %"new::Array.size_ptr14.copyload", !dbg !87
  br i1 %.not, label %L48, label %L45, !dbg !90

L45:                                              ; preds = %L31
  store i64 %value_phi10, ptr %"new::Tuple36", align 8, !dbg !90, !tbaa !99, !alias.scope !101, !noalias !102
  call swiftcc void @j_throw_boundserror_592(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr nonnull %"new::Array", ptr nocapture nonnull readonly %"new::Tuple36") #12, !dbg !90
  unreachable, !dbg !90

L48:                                              ; preds = %L31
  %memoryref_data = load ptr, ptr %"new::Array", align 8, !dbg !103, !tbaa !81, !alias.scope !76, !noalias !77
  %memoryref_byteoffset = shl i64 %9, 3, !dbg !106
  %memoryref_data16 = getelementptr inbounds i8, ptr %memoryref_data, i64 %memoryref_byteoffset, !dbg !106
  store ptr %8, ptr %memoryref_data16, align 8, !dbg !106, !tbaa !107, !alias.scope !109, !noalias !110
  %.not42 = icmp eq i64 %value_phi10, 4, !dbg !111
  %10 = add nuw nsw i64 %value_phi10, 1, !dbg !114
  br i1 %.not42, label %L64, label %L31, !dbg !86

L64:                                              ; preds = %L48
  %11 = and i64 %"x::UInt64", 3, !dbg !117
  %.not43 = icmp ult i64 %11, %"new::Array.size_ptr14.copyload", !dbg !122
  br i1 %.not43, label %L81, label %L77, !dbg !123

L77:                                              ; preds = %L64
  %12 = add nuw nsw i64 %11, 1, !dbg !129
  store i64 %12, ptr %"new::Tuple", align 8, !dbg !123, !tbaa !99, !alias.scope !101, !noalias !102
  call swiftcc void @j_throw_boundserror_592(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr nonnull %"new::Array", ptr nocapture nonnull readonly %"new::Tuple") #12, !dbg !123
  unreachable, !dbg !123

L81:                                              ; preds = %L64
  %memoryref_byteoffset27 = shl nuw nsw i64 %11, 3, !dbg !132
  %memoryref_data32 = getelementptr inbounds nuw i8, ptr %memoryref_data, i64 %memoryref_byteoffset27, !dbg !132
  %13 = load ptr, ptr %memoryref_data32, align 8, !dbg !132, !tbaa !107, !alias.scope !109, !noalias !110
  store ptr null, ptr %gc_slot_addr_0, align 8
  call fastcc void @julia_case_D_571u589(ptr %13, i64 0), !dbg !133
  call fastcc void @julia_case_D_571u591(ptr %2), !dbg !134
  %frame.prev64 = load ptr, ptr %frame.prev, align 8, !tbaa !16
  store ptr %frame.prev64, ptr %pgcstack_arg, align 8, !tbaa !16
  ret i64 %value_phi, !dbg !137
}

; Function Attrs: noinline optnone
define nonnull ptr @jfptr_case_D_572(ptr %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") local_unnamed_addr #2 {
top:
  %thread_ptr = call ptr asm "movq %fs:0, $0", "=r"()
  %tls_ppgcstack = getelementptr inbounds i8, ptr %thread_ptr, i64 -8
  %tls_pgcstack = load ptr, ptr %tls_ppgcstack, align 8
  %0 = load ptr, ptr %"args::Any[]", align 8, !tbaa !31, !invariant.load !12, !alias.scope !138, !noalias !139, !nonnull !12, !dereferenceable !140, !align !140
  %.unbox = load i64, ptr %0, align 8, !tbaa !141, !alias.scope !109, !noalias !110
  %1 = call swiftcc i64 @julia_case_D_571(ptr nonnull swiftself "gcstack" %tls_pgcstack, i64 zeroext %.unbox)
  %box_UInt64 = call nonnull align 8 dereferenceable(8) ptr @ijl_box_uint64(i64 zeroext %1) #13
  ret ptr %box_UInt64
}

; Function Attrs: mustprogress nounwind willreturn memory(read, inaccessiblemem: readwrite)
declare nonnull align 8 dereferenceable(8) ptr @ijl_box_uint64(i64 zeroext) local_unnamed_addr #3

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
declare swiftcc void @j_throw_boundserror_592(ptr nonnull swiftself "gcstack", ptr, ptr nocapture readonly) local_unnamed_addr #7

define internal fastcc ptr @julia_case_D_571u575(i64 %0) unnamed_addr {
  %r = call ptr @__bennett_qalloc(i64 0, i64 %0)
  ret ptr %r
}

declare ptr @__bennett_qalloc(i64, i64) local_unnamed_addr

define internal fastcc void @julia_case_D_571u577(ptr %0, i64 %1) unnamed_addr {
  call void @__bennett_gate(i32 1, ptr %0, i64 %1)
  ret void
}

declare void @__bennett_gate(i32, ptr, i64) local_unnamed_addr

define internal fastcc void @julia_case_D_571u579(ptr %0, double %1) unnamed_addr {
  call void @__bennett_rot(i32 3, ptr %0, i64 1, double %1)
  ret void
}

declare void @__bennett_rot(i32, ptr, i64, double) local_unnamed_addr

define internal zeroext i1 @julia_case_D_571u581(ptr %0) unnamed_addr {
  %r = call zeroext i1 @__bennett_measure(ptr %0, i64 0)
  ret i1 %r
}

declare zeroext i1 @__bennett_measure(ptr, i64) local_unnamed_addr

define internal fastcc void @julia_case_D_571u582(ptr %0, i64 %1) unnamed_addr {
  call void @__bennett_gate(i32 1, ptr %0, i64 %1)
  ret void
}

define internal fastcc ptr @julia_case_D_571u588(i64 %0) unnamed_addr {
  %r = call ptr @__bennett_qalloc(i64 0, i64 %0)
  ret ptr %r
}

define internal fastcc void @julia_case_D_571u589(ptr %0, i64 %1) unnamed_addr {
  call void @__bennett_gate(i32 1, ptr %0, i64 %1)
  ret void
}

define internal fastcc void @julia_case_D_571u591(ptr %0) unnamed_addr {
  call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr %0, i64 0, ptr null, i64 8, i32 1, double 2.500000e+00, ptr %0)
  ret void
}

declare void @__bennett_ctrl_v(ptr, i64, ptr, i64, ...) local_unnamed_addr

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

attributes #0 = { "julia.fname"="__bennett_ctrl" "julia.libidx"="0" }
attributes #1 = { "frame-pointer"="all" "julia.fsig"="case_D(UInt64)" "probe-stack"="inline-asm" }
attributes #2 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #3 = { mustprogress nounwind willreturn memory(read, inaccessiblemem: readwrite) }
attributes #4 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #5 = { mustprogress nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #6 = { mustprogress nofree norecurse nosync nounwind speculatable willreturn memory(none) }
attributes #7 = { noreturn "frame-pointer"="all" "julia.fsig"="throw_boundserror(Array{Ptr{Nothing}, 1}, Tuple{Int64})" "probe-stack"="inline-asm" }
attributes #8 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #9 = { nounwind willreturn allockind("alloc") allocsize(2) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #10 = { nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #11 = { nocallback nofree nounwind willreturn memory(argmem: write) }
attributes #12 = { noreturn }
attributes #13 = { nounwind willreturn memory(read, inaccessiblemem: readwrite) }

!llvm.module.flags = !{!0, !1, !2, !3}
!llvm.dbg.cu = !{!4}

!0 = !{i32 2, !"Dwarf Version", i32 4}
!1 = !{i32 2, !"Debug Info Version", i32 3}
!2 = !{i32 1, !"stack-protector-guard", !""}
!3 = !{i32 1, !"override-stack-alignment", i32 0}
!4 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !5, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!5 = !DIFile(filename: "julia", directory: ".")
!6 = distinct !DISubprogram(name: "case_D", linkageName: "julia_case_D_571", scope: null, file: !7, line: 146, type: !8, scopeLine: 146, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4, retainedNodes: !13)
!7 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!8 = !DISubroutineType(types: !9)
!9 = !{!10, !11, !10}
!10 = !DIBasicType(name: "UInt64", size: 64, encoding: DW_ATE_unsigned)
!11 = !DICompositeType(tag: DW_TAG_structure_type, name: "#case_D", align: 8, elements: !12, runtimeLang: DW_LANG_Julia, identifier: "127079337970704")
!12 = !{}
!13 = !{!14, !15}
!14 = !DILocalVariable(name: "#self#", arg: 1, scope: !6, file: !7, line: 146, type: !11)
!15 = !DILocalVariable(name: "x", arg: 2, scope: !6, file: !7, line: 146, type: !10)
!16 = !{!17, !17, i64 0}
!17 = !{!"jtbaa_gcframe", !18, i64 0}
!18 = !{!"jtbaa", !19, i64 0}
!19 = !{!"jtbaa"}
!20 = !DILocation(line: 8, scope: !21, inlinedAt: !24)
!21 = distinct !DISubprogram(name: "RefValue;", linkageName: "RefValue", scope: !22, file: !22, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!22 = !DIFile(filename: "refvalue.jl", directory: ".")
!23 = !DISubroutineType(types: !12)
!24 = !DILocation(line: 10, scope: !21, inlinedAt: !25)
!25 = !DILocation(line: 145, scope: !26, inlinedAt: !28)
!26 = distinct !DISubprogram(name: "Ref;", linkageName: "Ref", scope: !27, file: !27, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!27 = !DIFile(filename: "refpointer.jl", directory: ".")
!28 = !DILocation(line: 84, scope: !29, inlinedAt: !30)
!29 = distinct !DISubprogram(name: "rF_ctrl;", linkageName: "rF_ctrl", scope: !7, file: !7, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!30 = !DILocation(line: 155, scope: !6)
!31 = !{!32, !32, i64 0}
!32 = !{!"jtbaa_const", !18, i64 0}
!33 = !DILocation(line: 146, scope: !6)
!34 = !DILocation(line: 30, scope: !35, inlinedAt: !36)
!35 = distinct !DISubprogram(name: "rD_alloc;", linkageName: "rD_alloc", scope: !7, file: !7, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!36 = !DILocation(line: 147, scope: !6)
!37 = !DILocation(line: 35, scope: !38, inlinedAt: !39)
!38 = distinct !DISubprogram(name: "rD_gate;", linkageName: "rD_gate", scope: !7, file: !7, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!39 = !DILocation(line: 148, scope: !6)
!40 = !DILocation(line: 251, scope: !41, inlinedAt: !43)
!41 = distinct !DISubprogram(name: "Float64;", linkageName: "Float64", scope: !42, file: !42, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!42 = !DIFile(filename: "float.jl", directory: ".")
!43 = !DILocation(line: 149, scope: !6)
!44 = !DILocation(line: 494, scope: !45, inlinedAt: !43)
!45 = distinct !DISubprogram(name: "*;", linkageName: "*", scope: !42, file: !42, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!46 = !DILocation(line: 45, scope: !47, inlinedAt: !48)
!47 = distinct !DISubprogram(name: "rD_rot;", linkageName: "rD_rot", scope: !7, file: !7, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!48 = !DILocation(line: 150, scope: !6)
!49 = !DILocation(line: 40, scope: !50, inlinedAt: !51)
!50 = distinct !DISubprogram(name: "rD_measure;", linkageName: "rD_measure", scope: !7, file: !7, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!51 = !DILocation(line: 152, scope: !6)
!52 = !DILocation(line: 35, scope: !38, inlinedAt: !53)
!53 = !DILocation(line: 153, scope: !6)
!54 = !{!18, !18, i64 0}
!55 = !{!56, !58}
!56 = !{!"jnoalias_stack", !57}
!57 = !{!"jnoalias"}
!58 = !{!"jnoalias_data", !57}
!59 = !{!60, !61, !62}
!60 = !{!"jnoalias_gcframe", !57}
!61 = !{!"jnoalias_typemd", !57}
!62 = !{!"jnoalias_const", !57}
!63 = !DILocation(line: 86, scope: !29, inlinedAt: !30)
!64 = !DILocation(line: 588, scope: !65, inlinedAt: !67)
!65 = distinct !DISubprogram(name: "GenericMemory;", linkageName: "GenericMemory", scope: !66, file: !66, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!66 = !DIFile(filename: "boot.jl", directory: ".")
!67 = !DILocation(line: 648, scope: !68, inlinedAt: !69)
!68 = distinct !DISubprogram(name: "Array;", linkageName: "Array", scope: !66, file: !66, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!69 = !DILocation(line: 156, scope: !6)
!70 = !{!71, !71, i64 0}
!71 = !{!"jtbaa_tag", !72, i64 0}
!72 = !{!"jtbaa_data", !18, i64 0}
!73 = !{!74, !74, i64 0}
!74 = !{!"jtbaa_memoryptr", !75, i64 0}
!75 = !{!"jtbaa_array", !18, i64 0}
!76 = !{!61}
!77 = !{!60, !56, !58, !62}
!78 = !{!79, !79, i64 0}
!79 = !{!"jtbaa_memorylen", !75, i64 0}
!80 = !DILocation(line: 649, scope: !68, inlinedAt: !69)
!81 = !{!82, !82, i64 0}
!82 = !{!"jtbaa_arrayptr", !75, i64 0}
!83 = !{!84, !84, i64 0}
!84 = !{!"jtbaa_arraysize", !75, i64 0}
!85 = !DILocation(line: 30, scope: !35, inlinedAt: !86)
!86 = !DILocation(line: 157, scope: !6)
!87 = !DILocation(line: 385, scope: !88, inlinedAt: !90)
!88 = distinct !DISubprogram(name: "checkbounds;", linkageName: "checkbounds", scope: !89, file: !89, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!89 = !DIFile(filename: "essentials.jl", directory: ".")
!90 = !DILocation(line: 1024, scope: !91, inlinedAt: !93)
!91 = distinct !DISubprogram(name: "_setindex!;", linkageName: "_setindex!", scope: !92, file: !92, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!92 = !DIFile(filename: "array.jl", directory: ".")
!93 = !DILocation(line: 1020, scope: !94, inlinedAt: !86)
!94 = distinct !DISubprogram(name: "setindex!;", linkageName: "setindex!", scope: !92, file: !92, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!95 = !DILocation(line: 10, scope: !96, inlinedAt: !97)
!96 = distinct !DISubprogram(name: "size;", linkageName: "size", scope: !89, file: !89, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!97 = !DILocation(line: 11, scope: !98, inlinedAt: !87)
!98 = distinct !DISubprogram(name: "length;", linkageName: "length", scope: !89, file: !89, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!99 = !{!100, !100, i64 0}
!100 = !{!"jtbaa_stack", !18, i64 0}
!101 = !{!56}
!102 = !{!60, !58, !61, !62}
!103 = !DILocation(line: 57, scope: !104, inlinedAt: !106)
!104 = distinct !DISubprogram(name: "getproperty;", linkageName: "getproperty", scope: !105, file: !105, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!105 = !DIFile(filename: "Base_compiler.jl", directory: ".")
!106 = !DILocation(line: 1025, scope: !91, inlinedAt: !93)
!107 = !{!108, !108, i64 0}
!108 = !{!"jtbaa_arraybuf", !72, i64 0}
!109 = !{!58}
!110 = !{!60, !56, !61, !62}
!111 = !DILocation(line: 641, scope: !112, inlinedAt: !114)
!112 = distinct !DISubprogram(name: "==;", linkageName: "==", scope: !113, file: !113, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!113 = !DIFile(filename: "promotion.jl", directory: ".")
!114 = !DILocation(line: 928, scope: !115, inlinedAt: !86)
!115 = distinct !DISubprogram(name: "iterate;", linkageName: "iterate", scope: !116, file: !116, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!116 = !DIFile(filename: "range.jl", directory: ".")
!117 = !DILocation(line: 393, scope: !118, inlinedAt: !120)
!118 = distinct !DISubprogram(name: "&;", linkageName: "&", scope: !119, file: !119, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!119 = !DIFile(filename: "int.jl", directory: ".")
!120 = !DILocation(line: 1058, scope: !118, inlinedAt: !121)
!121 = !DILocation(line: 158, scope: !6)
!122 = !DILocation(line: 385, scope: !88, inlinedAt: !123)
!123 = !DILocation(line: 389, scope: !88, inlinedAt: !124)
!124 = !DILocation(line: 974, scope: !125, inlinedAt: !126)
!125 = distinct !DISubprogram(name: "getindex;", linkageName: "getindex", scope: !89, file: !89, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!126 = !DILocation(line: 1366, scope: !127, inlinedAt: !121)
!127 = distinct !DISubprogram(name: "getindex;", linkageName: "getindex", scope: !128, file: !128, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!128 = !DIFile(filename: "abstractarray.jl", directory: ".")
!129 = !DILocation(line: 87, scope: !130, inlinedAt: !131)
!130 = distinct !DISubprogram(name: "+;", linkageName: "+", scope: !119, file: !119, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!131 = !DILocation(line: 1058, scope: !130, inlinedAt: !121)
!132 = !DILocation(line: 975, scope: !125, inlinedAt: !126)
!133 = !DILocation(line: 35, scope: !38, inlinedAt: !121)
!134 = !DILocation(line: 113, scope: !135, inlinedAt: !136)
!135 = distinct !DISubprogram(name: "rH5_ctrl_v;", linkageName: "rH5_ctrl_v", scope: !7, file: !7, type: !23, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !4)
!136 = !DILocation(line: 159, scope: !6)
!137 = !DILocation(line: 160, scope: !6)
!138 = !{!62}
!139 = !{!60, !56, !58, !61}
!140 = !{i64 8}
!141 = !{!142, !142, i64 0}
!142 = !{!"jtbaa_immut", !143, i64 0}
!143 = !{!"jtbaa_value", !72, i64 0}
