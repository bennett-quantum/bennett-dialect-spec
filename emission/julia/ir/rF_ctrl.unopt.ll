; ModuleID = 'rF_ctrl'
source_filename = "rF_ctrl"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128-ni:10:11:12:13"
target triple = "x86_64-unknown-linux-gnu"

@jl_nothing = external constant ptr
@"_j_const#1" = private unnamed_addr constant i64 3, align 8
@"+Main.Base.RefValue#927" = private unnamed_addr constant ptr @"+Main.Base.RefValue#927.jit", !julia.constgv !0
@jlplt___bennett_ctrl_929_got = external global ptr #0

@"+Main.Base.RefValue#927.jit" = private alias ptr, inttoptr (i64 127079307385232 to ptr)

; Function Signature: rF_ctrl(Ptr{Nothing}, Float64)
define swiftcc void @julia_rF_ctrl_925(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"h::Ptr", double %"theta::Float64") #1 !dbg !5 {
top:
  %"new::Env" = alloca { ptr, i64, double }, align 8
  %current_task = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152
  %ptls_field = getelementptr inbounds i8, ptr %current_task, i32 168
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !17
  %0 = getelementptr inbounds i8, ptr %ptls_load, i32 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !21, !invariant.load !0
  fence syncscope("singlethread") seq_cst
  call void @julia.safepoint(ptr %safepoint)
  fence syncscope("singlethread") seq_cst
    #dbg_value(ptr %"h::Ptr", !15, !DIExpression(), !23)
    #dbg_value(double %"theta::Float64", !16, !DIExpression(), !23)
  br label %L2, !dbg !24

L2:                                               ; preds = %top
  br label %L3, !dbg !24

L3:                                               ; preds = %L2
  br label %L4, !dbg !24

L4:                                               ; preds = %L3
  br label %L5, !dbg !24

L5:                                               ; preds = %L4
  br label %L6, !dbg !24

L6:                                               ; preds = %L5
  %1 = getelementptr inbounds i8, ptr %"new::Env", i32 0, !dbg !35
  store ptr %"h::Ptr", ptr %1, align 8, !dbg !35, !tbaa !38, !alias.scope !40, !noalias !43
  %2 = getelementptr inbounds i8, ptr %"new::Env", i32 8, !dbg !35
  %"_j_const#1.copyload" = load i64, ptr @"_j_const#1", align 8, !dbg !35, !tbaa !48, !alias.scope !52, !noalias !53
  store i64 %"_j_const#1.copyload", ptr %2, align 8, !dbg !35, !tbaa !38, !alias.scope !40, !noalias !43
  %3 = getelementptr inbounds i8, ptr %"new::Env", i32 16, !dbg !35
  store double %"theta::Float64", ptr %3, align 8, !dbg !35, !tbaa !38, !alias.scope !40, !noalias !43
  br label %L8, !dbg !35

L8:                                               ; preds = %L6
  %"+Main.Base.RefValue#927" = load ptr, ptr @"+Main.Base.RefValue#927", align 8, !dbg !54, !tbaa !21, !invariant.load !0, !alias.scope !61, !noalias !62, !nonnull !0, !dereferenceable !63, !align !64
  %RefValue = ptrtoint ptr %"+Main.Base.RefValue#927" to i64, !dbg !54
  %4 = inttoptr i64 %RefValue to ptr, !dbg !54
  %current_task1 = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152, !dbg !54
  %5 = addrspacecast ptr %4 to ptr addrspace(10), !dbg !54
  %"new::RefValue" = call noalias nonnull align 8 dereferenceable(24) ptr addrspace(10) @julia.gc_alloc_obj(ptr %current_task1, i64 24, ptr addrspace(10) %5) #7, !dbg !54
  %6 = addrspacecast ptr addrspace(10) %"new::RefValue" to ptr addrspace(11), !dbg !54
  %7 = addrspacecast ptr addrspace(10) %"new::RefValue" to ptr addrspace(11), !dbg !54
  call void @llvm.memcpy.p11.p0.i64(ptr addrspace(11) align 8 %7, ptr align 8 %"new::Env", i64 24, i1 false), !dbg !54, !tbaa !65, !alias.scope !66, !noalias !67
  %8 = call token (...) @llvm.julia.gc_preserve_begin(ptr addrspace(10) %"new::RefValue"), !dbg !68
  %9 = addrspacecast ptr addrspace(10) %"new::RefValue" to ptr addrspace(11), !dbg !69
  %10 = call nonnull ptr @julia.pointer_from_objref(ptr addrspace(11) %9) #6, !dbg !69
  %__bennett_ctrl = load atomic ptr, ptr @jlplt___bennett_ctrl_929_got unordered, align 8, !dbg !74
  call void %__bennett_ctrl(ptr %"h::Ptr", i64 0, ptr inttoptr (i64 127079231243584 to ptr), i64 8, ptr %10), !dbg !74
  call void @llvm.julia.gc_preserve_end(token %8), !dbg !74
  ret void, !dbg !74
}

; Function Attrs: noinline optnone
define nonnull ptr addrspace(10) @jfptr_rF_ctrl_926(ptr addrspace(10) %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") #2 {
top:
  %pgcstack = call ptr @julia.get_pgcstack()
  %0 = load ptr addrspace(10), ptr %"args::Any[]", align 8, !tbaa !21, !invariant.load !0, !alias.scope !61, !noalias !62, !nonnull !0, !dereferenceable !75, !align !75
  %1 = getelementptr inbounds i8, ptr %"args::Any[]", i32 8
  %2 = load ptr addrspace(10), ptr %1, align 8, !tbaa !21, !invariant.load !0, !alias.scope !61, !noalias !62, !nonnull !0, !dereferenceable !75, !align !75
  %.unbox = load ptr, ptr addrspace(10) %0, align 8, !tbaa !48, !alias.scope !52, !noalias !53
  %.unbox1 = load double, ptr addrspace(10) %2, align 8, !tbaa !48, !alias.scope !52, !noalias !53
  call swiftcc void @julia_rF_ctrl_925(ptr nonnull swiftself "gcstack" %pgcstack, ptr %.unbox, double %.unbox1)
  %jl_nothing = load ptr, ptr @jl_nothing, align 8, !tbaa !21, !invariant.load !0, !alias.scope !61, !noalias !62, !nonnull !0
  %3 = addrspacecast ptr %jl_nothing to ptr addrspace(10)
  ret ptr addrspace(10) %3
}

declare ptr @julia.get_pgcstack()

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) #3

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr addrspace(10) @julia.gc_alloc_obj(ptr, i64, ptr addrspace(10)) #4

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p11.p0.i64(ptr addrspace(11) noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #5

declare token @llvm.julia.gc_preserve_begin(...)

; Function Attrs: norecurse nosync nounwind speculatable willreturn memory(none)
declare nonnull ptr @julia.pointer_from_objref(ptr addrspace(11)) #6

declare void @llvm.julia.gc_preserve_end(token)

attributes #0 = { "julia.fname"="__bennett_ctrl" "julia.libidx"="0" }
attributes #1 = { "frame-pointer"="all" "julia.fsig"="rF_ctrl(Ptr{Nothing}, Float64)" "probe-stack"="inline-asm" }
attributes #2 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #3 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #4 = { nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #5 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { norecurse nosync nounwind speculatable willreturn memory(none) }
attributes #7 = { nounwind willreturn allockind("alloc,uninitialized") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }

!llvm.module.flags = !{!1, !2}
!llvm.dbg.cu = !{!3}

!0 = !{}
!1 = !{i32 2, !"Dwarf Version", i32 4}
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !4, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!4 = !DIFile(filename: "julia", directory: ".")
!5 = distinct !DISubprogram(name: "rF_ctrl", linkageName: "julia_rF_ctrl_925", scope: null, file: !6, line: 83, type: !7, scopeLine: 83, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3, retainedNodes: !13)
!6 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!7 = !DISubroutineType(types: !8)
!8 = !{!9, !10, !11, !12}
!9 = !DICompositeType(tag: DW_TAG_structure_type, name: "Nothing", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079415932560")
!10 = !DICompositeType(tag: DW_TAG_structure_type, name: "#rF_ctrl", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079338224016")
!11 = !DIBasicType(name: "Ptr", size: 64, encoding: DW_ATE_unsigned)
!12 = !DIBasicType(name: "Float64", size: 64, encoding: DW_ATE_unsigned)
!13 = !{!14, !15, !16}
!14 = !DILocalVariable(name: "#self#", arg: 1, scope: !5, file: !6, line: 83, type: !10)
!15 = !DILocalVariable(name: "h", arg: 2, scope: !5, file: !6, line: 83, type: !11)
!16 = !DILocalVariable(name: "theta", arg: 3, scope: !5, file: !6, line: 83, type: !12)
!17 = !{!18, !18, i64 0}
!18 = !{!"jtbaa_gcframe", !19, i64 0}
!19 = !{!"jtbaa", !20, i64 0}
!20 = !{!"jtbaa"}
!21 = !{!22, !22, i64 0, i64 1}
!22 = !{!"jtbaa_const", !19, i64 0}
!23 = !DILocation(line: 83, scope: !5)
!24 = !DILocation(line: 874, scope: !25, inlinedAt: !28)
!25 = distinct !DISubprogram(name: "check_sign_bit;", linkageName: "check_sign_bit", scope: !26, file: !26, type: !27, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!26 = !DIFile(filename: "boot.jl", directory: ".")
!27 = !DISubroutineType(types: !0)
!28 = !DILocation(line: 985, scope: !29, inlinedAt: !30)
!29 = distinct !DISubprogram(name: "toUInt64;", linkageName: "toUInt64", scope: !26, file: !26, type: !27, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!30 = !DILocation(line: 1015, scope: !31, inlinedAt: !32)
!31 = distinct !DISubprogram(name: "UInt64;", linkageName: "UInt64", scope: !26, file: !26, type: !27, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!32 = !DILocation(line: 7, scope: !33, inlinedAt: !35)
!33 = distinct !DISubprogram(name: "convert;", linkageName: "convert", scope: !34, file: !34, type: !27, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!34 = !DIFile(filename: "number.jl", directory: ".")
!35 = !DILocation(line: 75, scope: !36, inlinedAt: !37)
!36 = distinct !DISubprogram(name: "Env;", linkageName: "Env", scope: !6, file: !6, type: !27, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!37 = !DILocation(line: 84, scope: !5)
!38 = !{!39, !39, i64 0}
!39 = !{!"jtbaa_stack", !19, i64 0}
!40 = !{!41}
!41 = !{!"jnoalias_stack", !42}
!42 = !{!"jnoalias"}
!43 = !{!44, !45, !46, !47}
!44 = !{!"jnoalias_gcframe", !42}
!45 = !{!"jnoalias_data", !42}
!46 = !{!"jnoalias_typemd", !42}
!47 = !{!"jnoalias_const", !42}
!48 = !{!49, !49, i64 0}
!49 = !{!"jtbaa_immut", !50, i64 0}
!50 = !{!"jtbaa_value", !51, i64 0}
!51 = !{!"jtbaa_data", !19, i64 0}
!52 = !{!45}
!53 = !{!44, !41, !46, !47}
!54 = !DILocation(line: 8, scope: !55, inlinedAt: !57)
!55 = distinct !DISubprogram(name: "RefValue;", linkageName: "RefValue", scope: !56, file: !56, type: !27, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!56 = !DIFile(filename: "refvalue.jl", directory: ".")
!57 = !DILocation(line: 10, scope: !55, inlinedAt: !58)
!58 = !DILocation(line: 145, scope: !59, inlinedAt: !37)
!59 = distinct !DISubprogram(name: "Ref;", linkageName: "Ref", scope: !60, file: !60, type: !27, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!60 = !DIFile(filename: "refpointer.jl", directory: ".")
!61 = !{!47}
!62 = !{!44, !41, !45, !46}
!63 = !{i64 56}
!64 = !{i64 16}
!65 = !{!19, !19, i64 0}
!66 = !{!41, !45}
!67 = !{!44, !46, !47}
!68 = !DILocation(line: 85, scope: !5)
!69 = !DILocation(line: 302, scope: !70, inlinedAt: !72)
!70 = distinct !DISubprogram(name: "pointer_from_objref;", linkageName: "pointer_from_objref", scope: !71, file: !71, type: !27, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!71 = !DIFile(filename: "pointer.jl", directory: ".")
!72 = !DILocation(line: 40, scope: !73, inlinedAt: !74)
!73 = distinct !DISubprogram(name: "unsafe_convert;", linkageName: "unsafe_convert", scope: !56, file: !56, type: !27, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!74 = !DILocation(line: 86, scope: !5)
!75 = !{i64 8}
