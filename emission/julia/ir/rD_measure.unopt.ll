; ModuleID = 'rD_measure'
source_filename = "rD_measure"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128-ni:10:11:12:13"
target triple = "x86_64-unknown-linux-gnu"

@jl_false = external constant ptr
@jl_true = external constant ptr
@"jl_global#853" = private unnamed_addr constant ptr @"jl_global#853.jit", !julia.constgv !0
@"jl_global#854" = private unnamed_addr constant ptr @"jl_global#854.jit", !julia.constgv !0

@"jl_global#854.jit" = private alias ptr, inttoptr (i64 127079338396112 to ptr)
@"jl_global#853.jit" = private alias ptr, inttoptr (i64 127079338641680 to ptr)

; Function Signature: rD_measure(Ptr{Nothing})
define swiftcc i8 @julia_rD_measure_851(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"h::Ptr") #0 !dbg !7 {
top:
  %current_task = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152
  %ptls_field = getelementptr inbounds i8, ptr %current_task, i32 168
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !17
  %0 = getelementptr inbounds i8, ptr %ptls_load, i32 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !21, !invariant.load !0
  fence syncscope("singlethread") seq_cst
  call void @julia.safepoint(ptr %safepoint)
  fence syncscope("singlethread") seq_cst
    #dbg_value(ptr %"h::Ptr", !16, !DIExpression(), !23)
  %"jl_global#853" = load ptr, ptr @"jl_global#853", align 8, !dbg !23, !tbaa !21, !invariant.load !0, !alias.scope !24, !noalias !27, !nonnull !0
  %1 = addrspacecast ptr %"jl_global#853" to ptr addrspace(10), !dbg !23
  %"jl_global#854" = load ptr, ptr @"jl_global#854", align 8, !dbg !23, !tbaa !21, !invariant.load !0, !alias.scope !24, !noalias !27, !nonnull !0
  %2 = addrspacecast ptr %"jl_global#854" to ptr addrspace(10), !dbg !23
  %3 = call i8 @julia_rD_measure_851u855(ptr %"h::Ptr"), !dbg !23
  ret i8 %3, !dbg !23
}

; Function Attrs: noinline optnone
define nonnull ptr addrspace(10) @jfptr_rD_measure_852(ptr addrspace(10) %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") #1 {
top:
  %pgcstack = call ptr @julia.get_pgcstack()
  %0 = load ptr addrspace(10), ptr %"args::Any[]", align 8, !tbaa !21, !invariant.load !0, !alias.scope !24, !noalias !27, !nonnull !0, !dereferenceable !32, !align !32
  %.unbox = load ptr, ptr addrspace(10) %0, align 8, !tbaa !33, !alias.scope !37, !noalias !38
  %1 = call swiftcc i8 @julia_rD_measure_851(ptr nonnull swiftself "gcstack" %pgcstack, ptr %.unbox)
  %2 = trunc i8 %1 to i1
  %jl_false = load ptr, ptr @jl_false, align 8, !tbaa !21, !invariant.load !0, !alias.scope !24, !noalias !27, !nonnull !0, !dereferenceable !39, !align !39
  %jl_true = load ptr, ptr @jl_true, align 8, !tbaa !21, !invariant.load !0, !alias.scope !24, !noalias !27, !nonnull !0, !dereferenceable !39, !align !39
  %bool = select i1 %2, ptr %jl_true, ptr %jl_false
  %3 = addrspacecast ptr %bool to ptr addrspace(10)
  ret ptr addrspace(10) %3
}

declare ptr @julia.get_pgcstack()

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) #2

define internal zeroext i1 @julia_rD_measure_851u855(ptr %0) {
  %r = call zeroext i1 @__bennett_measure(ptr %0, i64 0)
  ret i1 %r
}

declare zeroext i1 @__bennett_measure(ptr, i64)

attributes #0 = { "frame-pointer"="all" "julia.fsig"="rD_measure(Ptr{Nothing})" "probe-stack"="inline-asm" }
attributes #1 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #2 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }

!llvm.module.flags = !{!1, !2, !3, !4}
!llvm.dbg.cu = !{!5}

!0 = !{}
!1 = !{i32 2, !"Dwarf Version", i32 4}
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = !{i32 1, !"stack-protector-guard", !""}
!4 = !{i32 1, !"override-stack-alignment", i32 0}
!5 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !6, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!6 = !DIFile(filename: "julia", directory: ".")
!7 = distinct !DISubprogram(name: "rD_measure", linkageName: "julia_rD_measure_851", scope: null, file: !8, line: 40, type: !9, scopeLine: 40, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5, retainedNodes: !14)
!8 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!9 = !DISubroutineType(types: !10)
!10 = !{!11, !12, !13}
!11 = !DIBasicType(name: "Bool", size: 8, encoding: DW_ATE_unsigned)
!12 = !DICompositeType(tag: DW_TAG_structure_type, name: "#rD_measure", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079338215504")
!13 = !DIBasicType(name: "Ptr", size: 64, encoding: DW_ATE_unsigned)
!14 = !{!15, !16}
!15 = !DILocalVariable(name: "#self#", arg: 1, scope: !7, file: !8, line: 40, type: !12)
!16 = !DILocalVariable(name: "h", arg: 2, scope: !7, file: !8, line: 40, type: !13)
!17 = !{!18, !18, i64 0}
!18 = !{!"jtbaa_gcframe", !19, i64 0}
!19 = !{!"jtbaa", !20, i64 0}
!20 = !{!"jtbaa"}
!21 = !{!22, !22, i64 0, i64 1}
!22 = !{!"jtbaa_const", !19, i64 0}
!23 = !DILocation(line: 40, scope: !7)
!24 = !{!25}
!25 = !{!"jnoalias_const", !26}
!26 = !{!"jnoalias"}
!27 = !{!28, !29, !30, !31}
!28 = !{!"jnoalias_gcframe", !26}
!29 = !{!"jnoalias_stack", !26}
!30 = !{!"jnoalias_data", !26}
!31 = !{!"jnoalias_typemd", !26}
!32 = !{i64 8}
!33 = !{!34, !34, i64 0}
!34 = !{!"jtbaa_immut", !35, i64 0}
!35 = !{!"jtbaa_value", !36, i64 0}
!36 = !{!"jtbaa_data", !19, i64 0}
!37 = !{!30}
!38 = !{!28, !29, !31, !25}
!39 = !{i64 1}
