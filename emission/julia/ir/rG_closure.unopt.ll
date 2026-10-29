; ModuleID = 'rG_closure'
source_filename = "rG_closure"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128-ni:10:11:12:13"
target triple = "x86_64-unknown-linux-gnu"

@jl_nothing = external constant ptr
@"+Main.Base.RefValue#943" = private unnamed_addr constant ptr @"+Main.Base.RefValue#943.jit", !julia.constgv !0
@"_j_const#1" = private unnamed_addr constant i64 0, align 8
@jl_small_typeof = external constant i8
@"+Core.Tuple#945" = private unnamed_addr constant ptr @"+Core.Tuple#945.jit", !julia.constgv !0
@0 = private global [8 x ptr] [ptr @"j_#rG_closure##0_951", ptr null, ptr @"jl_global#954", ptr null, ptr @j_952_gfthunk, ptr getelementptr inbounds (i8, ptr @jl_small_typeof, i32 208), ptr @"+Core.Tuple#945", ptr inttoptr (i64 1 to ptr)]
@jl_world_counter = external global i64
@"+Main.#rG_closure##0#rG_closure##1#946" = private unnamed_addr constant ptr @"+Main.#rG_closure##0#rG_closure##1#946.jit", !julia.constgv !0
@1 = private global [34 x i64] zeroinitializer
@"+Main.Base.CFunction#947" = private unnamed_addr constant ptr @"+Main.Base.CFunction#947.jit", !julia.constgv !0
@jl_emptysvec = external constant ptr
@jlplt___bennett_ctrl_949_got = external global ptr #0
@"+Core.Ptr#953" = private unnamed_addr constant ptr @"+Core.Ptr#953.jit", !julia.constgv !0
@"_j_str_cfunction#3" = private unnamed_addr constant [10 x i8] c"cfunction\00", align 1
@"jl_global#954" = private unnamed_addr constant ptr @"jl_global#954.jit", !julia.constgv !0

@"+Main.#rG_closure##0#rG_closure##1#946.jit" = private alias ptr, inttoptr (i64 127079298881488 to ptr)
@"+Core.Tuple#945.jit" = private alias ptr, inttoptr (i64 127079298881616 to ptr)
@"jl_global#954.jit" = private alias ptr, inttoptr (i64 127079299147200 to ptr)
@"+Core.Ptr#953.jit" = private alias ptr, inttoptr (i64 127079415345856 to ptr)
@"+Main.Base.RefValue#943.jit" = private alias ptr, inttoptr (i64 127079416559152 to ptr)
@"+Main.Base.CFunction#947.jit" = private alias ptr, inttoptr (i64 127079475360288 to ptr)

; Function Signature: rG_closure(Ptr{Nothing})
define swiftcc void @julia_rG_closure_941(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"h::Ptr") #1 !dbg !5 {
top:
  %current_task = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152
  %ptls_field = getelementptr inbounds i8, ptr %current_task, i32 168
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !15
  %0 = getelementptr inbounds i8, ptr %ptls_load, i32 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !19, !invariant.load !0
  fence syncscope("singlethread") seq_cst
  call void @julia.safepoint(ptr %safepoint)
  fence syncscope("singlethread") seq_cst
    #dbg_value(ptr %"h::Ptr", !14, !DIExpression(), !21)
  %"+Main.Base.RefValue#943" = load ptr, ptr @"+Main.Base.RefValue#943", align 8, !dbg !22, !tbaa !19, !invariant.load !0, !alias.scope !31, !noalias !34, !nonnull !0, !dereferenceable !39, !align !40
  %RefValue = ptrtoint ptr %"+Main.Base.RefValue#943" to i64, !dbg !22
  %1 = inttoptr i64 %RefValue to ptr, !dbg !22
  %current_task1 = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152, !dbg !22
  %2 = addrspacecast ptr %1 to ptr addrspace(10), !dbg !22
  %"new::RefValue" = call noalias nonnull align 8 dereferenceable(8) ptr addrspace(10) @julia.gc_alloc_obj(ptr %current_task1, i64 8, ptr addrspace(10) %2) #13, !dbg !22
  %3 = addrspacecast ptr addrspace(10) %"new::RefValue" to ptr addrspace(11), !dbg !22
  %4 = addrspacecast ptr addrspace(10) %"new::RefValue" to ptr addrspace(11), !dbg !22
  %"_j_const#1.copyload" = load i64, ptr @"_j_const#1", align 8, !dbg !22, !tbaa !41, !alias.scope !45, !noalias !46
  store i64 %"_j_const#1.copyload", ptr addrspace(11) %4, align 8, !dbg !22, !tbaa !47, !alias.scope !45, !noalias !46
  %"+Main.#rG_closure##0#rG_closure##1#946" = load ptr, ptr @"+Main.#rG_closure##0#rG_closure##1#946", align 8, !dbg !49, !tbaa !19, !invariant.load !0, !alias.scope !31, !noalias !34, !nonnull !0, !dereferenceable !39, !align !40
  %"#rG_closure##0#rG_closure##1" = ptrtoint ptr %"+Main.#rG_closure##0#rG_closure##1#946" to i64, !dbg !49
  %5 = inttoptr i64 %"#rG_closure##0#rG_closure##1" to ptr, !dbg !49
  %current_task2 = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152, !dbg !49
  %6 = addrspacecast ptr %5 to ptr addrspace(10), !dbg !49
  %"box::#rG_closure##0#rG_closure##1" = call noalias nonnull align 8 dereferenceable(8) ptr addrspace(10) @julia.gc_alloc_obj(ptr %current_task2, i64 8, ptr addrspace(10) %6) #13, !dbg !49
  %7 = addrspacecast ptr addrspace(10) %"box::#rG_closure##0#rG_closure##1" to ptr addrspace(11), !dbg !49
  store atomic ptr addrspace(10) %"new::RefValue", ptr addrspace(11) %7 unordered, align 8, !dbg !49, !tbaa !41, !alias.scope !45, !noalias !46
  %"+Main.Base.CFunction#947" = load ptr, ptr @"+Main.Base.CFunction#947", align 8, !dbg !49, !tbaa !19, !invariant.load !0, !alias.scope !31, !noalias !34, !nonnull !0, !dereferenceable !39, !align !40
  %jl_emptysvec = load ptr, ptr @jl_emptysvec, align 8, !dbg !49, !tbaa !19, !invariant.load !0, !alias.scope !31, !noalias !34, !nonnull !0
  %8 = call ptr addrspace(10) @jl_get_cfunction_trampoline(ptr addrspace(10) %"box::#rG_closure##0#rG_closure##1", ptr %"+Main.Base.CFunction#947", ptr @1, ptr %jl_emptysvec, ptr @"jlcapi_#rG_closure##0_944make", ptr null, ptr addrspace(11) null), !dbg !49
  %9 = addrspacecast ptr addrspace(10) %8 to ptr addrspace(11), !dbg !50
  %.ptr = load ptr, ptr addrspace(11) %9, align 8, !dbg !50, !tbaa !47, !alias.scope !45, !noalias !46
  %__bennett_ctrl = load atomic ptr, ptr @jlplt___bennett_ctrl_949_got unordered, align 8, !dbg !56
  call void %__bennett_ctrl(ptr %"h::Ptr", i64 0, ptr %.ptr, i64 8, ptr null) [ "jl_roots"(ptr addrspace(10) %8) ], !dbg !56
  ret void, !dbg !56
}

; Function Attrs: noinline optnone
define nonnull ptr addrspace(10) @jfptr_rG_closure_942(ptr addrspace(10) %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") #2 {
top:
  %pgcstack = call ptr @julia.get_pgcstack()
  %0 = load ptr addrspace(10), ptr %"args::Any[]", align 8, !tbaa !19, !invariant.load !0, !alias.scope !31, !noalias !34, !nonnull !0, !dereferenceable !57, !align !57
  %.unbox = load ptr, ptr addrspace(10) %0, align 8, !tbaa !41, !alias.scope !45, !noalias !46
  call swiftcc void @julia_rG_closure_941(ptr nonnull swiftself "gcstack" %pgcstack, ptr %.unbox)
  %jl_nothing = load ptr, ptr @jl_nothing, align 8, !tbaa !19, !invariant.load !0, !alias.scope !31, !noalias !34, !nonnull !0
  %1 = addrspacecast ptr %jl_nothing to ptr addrspace(10)
  ret ptr addrspace(10) %1
}

declare ptr @julia.get_pgcstack()

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) #3

; Function Attrs: nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite)
declare noalias nonnull ptr addrspace(10) @julia.gc_alloc_obj(ptr, i64, ptr addrspace(10)) #4

define void @"jlcapi_#rG_closure##0_944"(ptr nest %0, ptr %1) #5 {
top:
  %pgcstack = call ptr @julia.get_pgcstack_or_new()
  %current_task = getelementptr inbounds i8, ptr %pgcstack, i32 -152
  %world_age = getelementptr inbounds i8, ptr %current_task, i32 160
  %2 = load i64, ptr %world_age, align 8, !tbaa !15, !alias.scope !58, !noalias !59
  %3 = load ptr addrspace(10), ptr %0, align 8
  %4 = load atomic i64, ptr getelementptr inbounds (i64, ptr @0, i32 1) acquire, align 8
  %5 = load atomic ptr, ptr @0 monotonic, align 8
  %6 = load atomic i64, ptr @jl_world_counter acquire, align 8
  %current_task1 = getelementptr inbounds i8, ptr %pgcstack, i32 -152
  %world_age2 = getelementptr inbounds i8, ptr %current_task1, i32 160
  store i64 %6, ptr %world_age2, align 8, !tbaa !15, !alias.scope !58, !noalias !59
  %7 = icmp ne i64 %4, %6
  br i1 %7, label %guard_pass, label %guard_exit

guard_pass:                                       ; preds = %top
  %current_task3 = getelementptr inbounds i8, ptr %pgcstack, i32 -152
  %8 = call ptr @jl_get_abi_converter(ptr %current_task3, ptr @0)
  br label %guard_exit

guard_exit:                                       ; preds = %guard_pass, %top
  %guard_res = phi ptr [ %5, %top ], [ %8, %guard_pass ]
  %9 = addrspacecast ptr addrspace(10) %3 to ptr addrspace(11)
  call swiftcc void %guard_res(ptr nonnull swiftself "gcstack" %pgcstack, ptr addrspace(11) nocapture readonly %9, ptr %1)
  %current_task4 = getelementptr inbounds i8, ptr %pgcstack, i32 -152
  %world_age5 = getelementptr inbounds i8, ptr %current_task4, i32 160
  store i64 %2, ptr %world_age5, align 8, !tbaa !15, !alias.scope !58, !noalias !59
  ret void
}

declare ptr @julia.get_pgcstack_or_new()

declare ptr @jl_get_abi_converter(ptr, ptr)

define ptr @"jlcapi_#rG_closure##0_944make"(ptr %wrapper, ptr %newval) #5 {
top:
  call void @llvm.init.trampoline(ptr %wrapper, ptr @"jlcapi_#rG_closure##0_944", ptr %newval)
  %0 = call ptr @llvm.adjust.trampoline(ptr %wrapper)
  ret ptr %0
}

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.init.trampoline(ptr nocapture writeonly, ptr readnone, ptr readnone) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: read)
declare ptr @llvm.adjust.trampoline(ptr) #7

declare nonnull ptr addrspace(10) @jl_get_cfunction_trampoline(ptr addrspace(10), ptr, ptr, ptr, ptr, ptr, ptr addrspace(11))

declare nonnull ptr addrspace(10) @ijl_apply_generic(ptr addrspace(10), ptr noalias nocapture noundef readonly, i32)

; Function Signature: (::Main.var"#rG_closure##0#rG_closure##1"{Base.RefValue{Int64}})(Ptr{Nothing})
define swiftcc void @j_952_gfthunk(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr addrspace(11) nocapture readonly %0, ptr %1) #8 {
top:
  %"+Main.#rG_closure##0#rG_closure##1#946" = load ptr, ptr @"+Main.#rG_closure##0#rG_closure##1#946", align 8, !tbaa !19, !invariant.load !0, !alias.scope !31, !noalias !34, !nonnull !0, !dereferenceable !39, !align !40
  %"#rG_closure##0#rG_closure##1" = ptrtoint ptr %"+Main.#rG_closure##0#rG_closure##1#946" to i64
  %2 = inttoptr i64 %"#rG_closure##0#rG_closure##1" to ptr
  %current_task = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152
  %3 = addrspacecast ptr %2 to ptr addrspace(10)
  %"box::#rG_closure##0#rG_closure##1" = call noalias nonnull align 8 dereferenceable(8) ptr addrspace(10) @julia.gc_alloc_obj(ptr %current_task, i64 8, ptr addrspace(10) %3) #13
  %4 = addrspacecast ptr addrspace(10) %"box::#rG_closure##0#rG_closure##1" to ptr addrspace(11)
  call void @llvm.memcpy.p11.p11.i64(ptr addrspace(11) align 8 %4, ptr addrspace(11) align 8 %0, i64 8, i1 false), !tbaa !60, !alias.scope !61, !noalias !62
  %"+Core.Ptr#953" = load ptr, ptr @"+Core.Ptr#953", align 8, !tbaa !19, !invariant.load !0, !alias.scope !31, !noalias !34, !nonnull !0, !dereferenceable !39, !align !40
  %Ptr = ptrtoint ptr %"+Core.Ptr#953" to i64
  %5 = inttoptr i64 %Ptr to ptr
  %current_task1 = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152
  %6 = addrspacecast ptr %5 to ptr addrspace(10)
  %"box::Ptr" = call noalias nonnull align 8 dereferenceable(8) ptr addrspace(10) @julia.gc_alloc_obj(ptr %current_task1, i64 8, ptr addrspace(10) %6) #13
  %7 = addrspacecast ptr addrspace(10) %"box::Ptr" to ptr addrspace(11)
  store ptr %1, ptr addrspace(11) %7, align 8, !tbaa !41, !alias.scope !45, !noalias !46
  %8 = call nonnull ptr addrspace(10) (ptr, ptr addrspace(10), ...) @julia.call(ptr @ijl_apply_generic, ptr addrspace(10) %"box::#rG_closure##0#rG_closure##1", ptr addrspace(10) %"box::Ptr")
  %9 = call ptr addrspace(10) @julia.typeof(ptr addrspace(10) %8)
  %10 = addrspacecast ptr addrspace(10) %9 to ptr addrspace(11)
  %11 = call nonnull ptr @julia.pointer_from_objref(ptr addrspace(11) %10) #11
  %typeof = ptrtoint ptr %11 to i64
  %exactly_isa = icmp eq i64 %typeof, 208
  br i1 %exactly_isa, label %pass, label %fail

fail:                                             ; preds = %top
  %12 = load ptr, ptr getelementptr inbounds (i8, ptr @jl_small_typeof, i32 208), align 8, !tbaa !19, !invariant.load !0, !alias.scope !31, !noalias !34, !nonnull !0, !dereferenceable !39, !align !40
  %13 = addrspacecast ptr %12 to ptr addrspace(10)
  %14 = addrspacecast ptr addrspace(10) %8 to ptr addrspace(12)
  call void @ijl_type_error(ptr @"_j_str_cfunction#3", ptr addrspace(10) %13, ptr addrspace(12) %14)
  unreachable

pass:                                             ; preds = %top
  ret void
}

declare nonnull ptr addrspace(10) @julia.call(ptr, ptr addrspace(10), ...)

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p11.p11.i64(ptr addrspace(11) noalias nocapture writeonly, ptr addrspace(11) noalias nocapture readonly, i64, i1 immarg) #9

; Function Attrs: norecurse nounwind memory(none)
declare nonnull ptr addrspace(10) @julia.typeof(ptr addrspace(10)) #10

; Function Attrs: norecurse nosync nounwind speculatable willreturn memory(none)
declare nonnull ptr @julia.pointer_from_objref(ptr addrspace(11)) #11

; Function Attrs: noreturn
declare void @ijl_type_error(ptr, ptr addrspace(10), ptr addrspace(12)) #12

; Function Signature: (::Main.var"#rG_closure##0#rG_closure##1"{Base.RefValue{Int64}})(Ptr{Nothing})
declare swiftcc void @"j_#rG_closure##0_951"(ptr nonnull swiftself "gcstack", ptr addrspace(11) nocapture readonly, ptr) #8

attributes #0 = { "julia.fname"="__bennett_ctrl" "julia.libidx"="0" }
attributes #1 = { "frame-pointer"="all" "julia.fsig"="rG_closure(Ptr{Nothing})" "probe-stack"="inline-asm" }
attributes #2 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #3 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #4 = { nounwind willreturn allockind("alloc") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }
attributes #5 = { "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(argmem: read) }
attributes #8 = { "frame-pointer"="all" "julia.fsig"="(::Main.var\22#rG_closure##0#rG_closure##1\22{Base.RefValue{Int64}})(Ptr{Nothing})" "probe-stack"="inline-asm" }
attributes #9 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #10 = { norecurse nounwind memory(none) }
attributes #11 = { norecurse nosync nounwind speculatable willreturn memory(none) }
attributes #12 = { noreturn }
attributes #13 = { nounwind willreturn allockind("alloc,uninitialized") allocsize(1) memory(argmem: read, inaccessiblemem: readwrite) }

!llvm.module.flags = !{!1, !2}
!llvm.dbg.cu = !{!3}

!0 = !{}
!1 = !{i32 2, !"Dwarf Version", i32 4}
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !4, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!4 = !DIFile(filename: "julia", directory: ".")
!5 = distinct !DISubprogram(name: "rG_closure", linkageName: "julia_rG_closure_941", scope: null, file: !6, line: 99, type: !7, scopeLine: 99, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3, retainedNodes: !12)
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
!19 = !{!20, !20, i64 0, i64 1}
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
!31 = !{!32}
!32 = !{!"jnoalias_const", !33}
!33 = !{!"jnoalias"}
!34 = !{!35, !36, !37, !38}
!35 = !{!"jnoalias_gcframe", !33}
!36 = !{!"jnoalias_stack", !33}
!37 = !{!"jnoalias_data", !33}
!38 = !{!"jnoalias_typemd", !33}
!39 = !{i64 56}
!40 = !{i64 16}
!41 = !{!42, !42, i64 0}
!42 = !{!"jtbaa_immut", !43, i64 0}
!43 = !{!"jtbaa_value", !44, i64 0}
!44 = !{!"jtbaa_data", !17, i64 0}
!45 = !{!37}
!46 = !{!35, !36, !38, !32}
!47 = !{!48, !48, i64 0}
!48 = !{!"jtbaa_mutab", !43, i64 0}
!49 = !DILocation(line: 102, scope: !5)
!50 = !DILocation(line: 57, scope: !51, inlinedAt: !53)
!51 = distinct !DISubprogram(name: "getproperty;", linkageName: "getproperty", scope: !52, file: !52, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!52 = !DIFile(filename: "Base_compiler.jl", directory: ".")
!53 = !DILocation(line: 36, scope: !54, inlinedAt: !56)
!54 = distinct !DISubprogram(name: "unsafe_convert;", linkageName: "unsafe_convert", scope: !55, file: !55, type: !25, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !3)
!55 = !DIFile(filename: "c.jl", directory: ".")
!56 = !DILocation(line: 103, scope: !5)
!57 = !{i64 8}
!58 = !{!35}
!59 = !{!36, !37, !38, !32}
!60 = !{!17, !17, i64 0}
!61 = !{!32, !37}
!62 = !{!35, !36, !38}
