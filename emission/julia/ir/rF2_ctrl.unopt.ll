; ModuleID = 'rF2_ctrl'
source_filename = "rF2_ctrl"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128-ni:10:11:12:13"
target triple = "x86_64-unknown-linux-gnu"

@jl_nothing = external constant ptr
@"_j_const#1" = private unnamed_addr constant i64 3, align 8
@"+Main.Base.RefValue#895" = private unnamed_addr constant ptr @"+Main.Base.RefValue#895.jit", !julia.constgv !0
@jl_small_typeof = external constant i8
@"+Core.Tuple#897" = private unnamed_addr constant ptr @"+Core.Tuple#897.jit", !julia.constgv !0
@0 = private global [8 x ptr] [ptr @j_body_901, ptr null, ptr @"jl_global#905", ptr null, ptr @j_902_gfthunk, ptr getelementptr inbounds (i8, ptr @jl_small_typeof, i32 208), ptr @"+Core.Tuple#897", ptr inttoptr (i64 1 to ptr)]
@jl_world_counter = external global i64
@jlplt___bennett_ctrl_899_got = external global ptr #0
@"jl_global#903" = private unnamed_addr constant ptr @"jl_global#903.jit", !julia.constgv !0
@"+Core.Ptr#904" = private unnamed_addr constant ptr @"+Core.Ptr#904.jit", !julia.constgv !0
@"_j_str_cfunction#3" = private unnamed_addr constant [10 x i8] c"cfunction\00", align 1
@"jl_global#905" = private unnamed_addr constant ptr @"jl_global#905.jit", !julia.constgv !0

@"jl_global#905.jit" = private alias ptr, inttoptr (i64 127079300351264 to ptr)
@"+Main.Base.RefValue#895.jit" = private alias ptr, inttoptr (i64 127079307385232 to ptr)
@"+Core.Tuple#897.jit" = private alias ptr, inttoptr (i64 127079338221840 to ptr)
@"jl_global#903.jit" = private alias ptr, inttoptr (i64 127079341093304 to ptr)
@"+Core.Ptr#904.jit" = private alias ptr, inttoptr (i64 127079415345856 to ptr)

; Function Signature: rF2_ctrl(Ptr{Nothing}, Float64)
define swiftcc void @julia_rF2_ctrl_893(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"h::Ptr", double %"theta::Float64") #1 !dbg !5 {
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
  %"+Main.Base.RefValue#895" = load ptr, ptr @"+Main.Base.RefValue#895", align 8, !dbg !54, !tbaa !21, !invariant.load !0, !alias.scope !61, !noalias !62, !nonnull !0, !dereferenceable !63, !align !64
  %RefValue = ptrtoint ptr %"+Main.Base.RefValue#895" to i64, !dbg !54
  %4 = inttoptr i64 %RefValue to ptr, !dbg !54
  %current_task1 = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152, !dbg !54
  %5 = addrspacecast ptr %4 to ptr addrspace(10), !dbg !54
  %"new::RefValue" = call noalias nonnull align 8 dereferenceable(24) ptr addrspace(10) @julia.gc_alloc_obj(ptr %current_task1, i64 24, ptr addrspace(10) %5) #11, !dbg !54
  %6 = addrspacecast ptr addrspace(10) %"new::RefValue" to ptr addrspace(11), !dbg !54
  %7 = addrspacecast ptr addrspace(10) %"new::RefValue" to ptr addrspace(11), !dbg !54
  call void @llvm.memcpy.p11.p0.i64(ptr addrspace(11) align 8 %7, ptr align 8 %"new::Env", i64 24, i1 false), !dbg !54, !tbaa !65, !alias.scope !66, !noalias !67
  %8 = call token (...) @llvm.julia.gc_preserve_begin(ptr addrspace(10) %"new::RefValue"), !dbg !68
  %9 = addrspacecast ptr addrspace(10) %"new::RefValue" to ptr addrspace(11), !dbg !69
  %10 = call nonnull ptr @julia.pointer_from_objref(ptr addrspace(11) %9) #7, !dbg !69
  %__bennett_ctrl = load atomic ptr, ptr @jlplt___bennett_ctrl_899_got unordered, align 8, !dbg !72
  call void %__bennett_ctrl(ptr %"h::Ptr", i64 0, ptr @jlcapi_body_896, i64 8, ptr %10), !dbg !72
  call void @llvm.julia.gc_preserve_end(token %8), !dbg !72
  ret void, !dbg !72
}

; Function Attrs: noinline optnone
define nonnull ptr addrspace(10) @jfptr_rF2_ctrl_894(ptr addrspace(10) %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") #2 {
top:
  %pgcstack = call ptr @julia.get_pgcstack()
  %0 = load ptr addrspace(10), ptr %"args::Any[]", align 8, !tbaa !21, !invariant.load !0, !alias.scope !61, !noalias !62, !nonnull !0, !dereferenceable !73, !align !73
  %1 = getelementptr inbounds i8, ptr %"args::Any[]", i32 8
  %2 = load ptr addrspace(10), ptr %1, align 8, !tbaa !21, !invariant.load !0, !alias.scope !61, !noalias !62, !nonnull !0, !dereferenceable !73, !align !73
  %.unbox = load ptr, ptr addrspace(10) %0, align 8, !tbaa !48, !alias.scope !52, !noalias !53
  %.unbox1 = load double, ptr addrspace(10) %2, align 8, !tbaa !48, !alias.scope !52, !noalias !53
  call swiftcc void @julia_rF2_ctrl_893(ptr nonnull swiftself "gcstack" %pgcstack, ptr %.unbox, double %.unbox1)
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

define void @jlcapi_body_896(ptr %0) #6 {
top:
  %pgcstack = call ptr @julia.get_pgcstack_or_new()
  %current_task = getelementptr inbounds i8, ptr %pgcstack, i32 -152
  %world_age = getelementptr inbounds i8, ptr %current_task, i32 160
  %1 = load i64, ptr %world_age, align 8, !tbaa !17, !alias.scope !74, !noalias !75
  %2 = load atomic i64, ptr getelementptr inbounds (i64, ptr @0, i32 1) acquire, align 8
  %3 = load atomic ptr, ptr @0 monotonic, align 8
  %4 = load atomic i64, ptr @jl_world_counter acquire, align 8
  %current_task1 = getelementptr inbounds i8, ptr %pgcstack, i32 -152
  %world_age2 = getelementptr inbounds i8, ptr %current_task1, i32 160
  store i64 %4, ptr %world_age2, align 8, !tbaa !17, !alias.scope !74, !noalias !75
  %5 = icmp ne i64 %2, %4
  br i1 %5, label %guard_pass, label %guard_exit

guard_pass:                                       ; preds = %top
  %current_task3 = getelementptr inbounds i8, ptr %pgcstack, i32 -152
  %6 = call ptr @jl_get_abi_converter(ptr %current_task3, ptr @0)
  br label %guard_exit

guard_exit:                                       ; preds = %guard_pass, %top
  %guard_res = phi ptr [ %3, %top ], [ %6, %guard_pass ]
  call swiftcc void %guard_res(ptr nonnull swiftself "gcstack" %pgcstack, ptr %0)
  %current_task4 = getelementptr inbounds i8, ptr %pgcstack, i32 -152
  %world_age5 = getelementptr inbounds i8, ptr %current_task4, i32 160
  store i64 %1, ptr %world_age5, align 8, !tbaa !17, !alias.scope !74, !noalias !75
  ret void
}

declare ptr @julia.get_pgcstack_or_new()

declare ptr @jl_get_abi_converter(ptr, ptr)

; Function Attrs: norecurse nosync nounwind speculatable willreturn memory(none)
declare nonnull ptr @julia.pointer_from_objref(ptr addrspace(11)) #7

declare void @llvm.julia.gc_preserve_end(token)

declare nonnull ptr addrspace(10) @ijl_apply_generic(ptr addrspace(10), ptr noalias nocapture noundef readonly, i32)

; Function Signature: body(Ptr{Nothing})
define swiftcc void @j_902_gfthunk(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %0) #8 {
top:
  %"jl_global#903" = load ptr, ptr @"jl_global#903", align 8, !tbaa !21, !invariant.load !0, !alias.scope !61, !noalias !62, !nonnull !0
  %1 = addrspacecast ptr %"jl_global#903" to ptr addrspace(10)
  %"+Core.Ptr#904" = load ptr, ptr @"+Core.Ptr#904", align 8, !tbaa !21, !invariant.load !0, !alias.scope !61, !noalias !62, !nonnull !0, !dereferenceable !63, !align !64
  %Ptr = ptrtoint ptr %"+Core.Ptr#904" to i64
  %2 = inttoptr i64 %Ptr to ptr
  %current_task = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152
  %3 = addrspacecast ptr %2 to ptr addrspace(10)
  %"box::Ptr" = call noalias nonnull align 8 dereferenceable(8) ptr addrspace(10) @julia.gc_alloc_obj(ptr %current_task, i64 8, ptr addrspace(10) %3) #11
  %4 = addrspacecast ptr addrspace(10) %"box::Ptr" to ptr addrspace(11)
  store ptr %0, ptr addrspace(11) %4, align 8, !tbaa !48, !alias.scope !52, !noalias !53
  %5 = call nonnull ptr addrspace(10) (ptr, ptr addrspace(10), ...) @julia.call(ptr @ijl_apply_generic, ptr addrspace(10) %1, ptr addrspace(10) %"box::Ptr")
  %6 = call ptr addrspace(10) @julia.typeof(ptr addrspace(10) %5)
  %7 = addrspacecast ptr addrspace(10) %6 to ptr addrspace(11)
  %8 = call nonnull ptr @julia.pointer_from_objref(ptr addrspace(11) %7) #7
  %typeof = ptrtoint ptr %8 to i64
  %exactly_isa = icmp eq i64 %typeof, 208
  br i1 %exactly_isa, label %pass, label %fail

fail:                                             ; preds = %top
  %9 = load ptr, ptr getelementptr inbounds (i8, ptr @jl_small_typeof, i32 208), align 8, !tbaa !21, !invariant.load !0, !alias.scope !61, !noalias !62, !nonnull !0, !dereferenceable !63, !align !64
  %10 = addrspacecast ptr %9 to ptr addrspace(10)
  %11 = addrspacecast ptr addrspace(10) %5 to ptr addrspace(12)
  call void @ijl_type_error(ptr @"_j_str_cfunction#3", ptr addrspace(10) %10, ptr addrspace(12) %11)
  unreachable

pass:                                             ; preds = %top
  ret void
}

declare nonnull ptr addrspace(10) @julia.call(ptr, ptr addrspace(10), ...)

; Function Attrs: norecurse nounwind memory(none)
declare nonnull ptr addrspace(10) @julia.typeof(ptr addrspace(10)) #9

; Function Attrs: noreturn
declare void @ijl_type_error(ptr, ptr addrspace(10), ptr addrspace(12)) #10

; Function Signature: body(Ptr{Nothing})
declare swiftcc void @j_body_901(ptr nonnull swiftself "gcstack", ptr) #8

attributes #0 = { "julia.fname"="__bennett_ctrl" "julia.libidx"="0" }
attributes #1 = { "frame-pointer"="all" "julia.fsig"="rF2_ctrl(Ptr{Nothing}, Float64)" "probe-stack"="inline-asm" }
attributes #2 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #3 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #4 = { nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #5 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #7 = { norecurse nosync nounwind speculatable willreturn memory(none) }
attributes #8 = { "frame-pointer"="all" "julia.fsig"="body(Ptr{Nothing})" "probe-stack"="inline-asm" }
attributes #9 = { norecurse nounwind memory(none) }
attributes #10 = { noreturn }
attributes #11 = { nounwind willreturn allockind("alloc,uninitialized") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }

!llvm.module.flags = !{!1, !2}
!llvm.dbg.cu = !{!3}

!0 = !{}
!1 = !{i32 2, !"Dwarf Version", i32 4}
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !4, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!4 = !DIFile(filename: "julia", directory: ".")
!5 = distinct !DISubprogram(name: "rF2_ctrl", linkageName: "julia_rF2_ctrl_893", scope: null, file: !6, line: 91, type: !7, scopeLine: 91, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3, retainedNodes: !13)
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
!17 = !{!18, !18, i64 0}
!18 = !{!"jtbaa_gcframe", !19, i64 0}
!19 = !{!"jtbaa", !20, i64 0}
!20 = !{!"jtbaa"}
!21 = !{!22, !22, i64 0, i64 1}
!22 = !{!"jtbaa_const", !19, i64 0}
!23 = !DILocation(line: 91, scope: !5)
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
!37 = !DILocation(line: 92, scope: !5)
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
!68 = !DILocation(line: 93, scope: !5)
!69 = !DILocation(line: 302, scope: !70, inlinedAt: !72)
!70 = distinct !DISubprogram(name: "pointer_from_objref;", linkageName: "pointer_from_objref", scope: !71, file: !71, type: !27, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!71 = !DIFile(filename: "pointer.jl", directory: ".")
!72 = !DILocation(line: 94, scope: !5)
!73 = !{i64 8}
!74 = !{!44}
!75 = !{!41, !45, !46, !47}
