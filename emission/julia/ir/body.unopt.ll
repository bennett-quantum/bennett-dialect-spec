; ModuleID = 'body'
source_filename = "body"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128-ni:10:11:12:13"
target triple = "x86_64-unknown-linux-gnu"

@jl_nothing = external constant ptr
@"jl_global#485" = private unnamed_addr constant ptr @"jl_global#485.jit", !julia.constgv !0
@"jl_global#486" = private unnamed_addr constant ptr @"jl_global#486.jit", !julia.constgv !0

@"jl_global#486.jit" = private alias ptr, inttoptr (i64 127079338396112 to ptr)
@"jl_global#485.jit" = private alias ptr, inttoptr (i64 127079338476416 to ptr)

; Function Signature: body(Ptr{Nothing})
define swiftcc void @julia_body_483(ptr nonnull swiftself "gcstack" %pgcstack_arg, ptr %"p::Ptr") #0 !dbg !7 {
top:
  %pointerref = alloca [3 x i64], align 8
  %current_task = getelementptr inbounds i8, ptr %pgcstack_arg, i32 -152
  %ptls_field = getelementptr inbounds i8, ptr %current_task, i32 168
  %ptls_load = load ptr, ptr %ptls_field, align 8, !tbaa !17
  %0 = getelementptr inbounds i8, ptr %ptls_load, i32 16
  %safepoint = load atomic ptr, ptr %0 monotonic, align 8, !tbaa !21, !invariant.load !0
  fence syncscope("singlethread") seq_cst
  call void @julia.safepoint(ptr %safepoint)
  fence syncscope("singlethread") seq_cst
    #dbg_value(ptr %"p::Ptr", !16, !DIExpression(), !23)
  %1 = getelementptr inbounds { ptr, i64, double }, ptr %"p::Ptr", i64 0, !dbg !24
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %pointerref, ptr align 1 %1, i64 24, i1 false), !dbg !24, !tbaa !30, !alias.scope !31, !noalias !35
  %pointerref.i_ptr = getelementptr inbounds i8, ptr %pointerref, i32 8, !dbg !39
  %"jl_global#485" = load ptr, ptr @"jl_global#485", align 8, !dbg !43, !tbaa !21, !invariant.load !0, !alias.scope !45, !noalias !46, !nonnull !0
  %2 = addrspacecast ptr %"jl_global#485" to ptr addrspace(10), !dbg !43
  %"jl_global#486" = load ptr, ptr @"jl_global#486", align 8, !dbg !43, !tbaa !21, !invariant.load !0, !alias.scope !45, !noalias !46, !nonnull !0
  %3 = addrspacecast ptr %"jl_global#486" to ptr addrspace(10), !dbg !43
  %pointerref.unbox = load ptr, ptr %pointerref, align 8, !dbg !43, !tbaa !47, !alias.scope !49, !noalias !50
  %pointerref.i_ptr.unbox = load i64, ptr %pointerref.i_ptr, align 8, !dbg !43, !tbaa !47, !alias.scope !49, !noalias !50
  call void @julia_body_483u487(ptr %pointerref.unbox, i64 %pointerref.i_ptr.unbox), !dbg !43
  ret void, !dbg !51
}

; Function Attrs: noinline optnone
define nonnull ptr addrspace(10) @jfptr_body_484(ptr addrspace(10) %"function::Core.Function", ptr noalias nocapture noundef readonly %"args::Any[]", i32 %"nargs::UInt32") #1 {
top:
  %pgcstack = call ptr @julia.get_pgcstack()
  %0 = load ptr addrspace(10), ptr %"args::Any[]", align 8, !tbaa !21, !invariant.load !0, !alias.scope !45, !noalias !46, !nonnull !0, !dereferenceable !52, !align !52
  %.unbox = load ptr, ptr addrspace(10) %0, align 8, !tbaa !53, !alias.scope !57, !noalias !58
  call swiftcc void @julia_body_483(ptr nonnull swiftself "gcstack" %pgcstack, ptr %.unbox)
  %jl_nothing = load ptr, ptr @jl_nothing, align 8, !tbaa !21, !invariant.load !0, !alias.scope !45, !noalias !46, !nonnull !0
  %1 = addrspacecast ptr %jl_nothing to ptr addrspace(10)
  ret ptr addrspace(10) %1
}

declare ptr @julia.get_pgcstack()

; Function Attrs: memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @julia.safepoint(ptr) #2

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #3

define internal void @julia_body_483u487(ptr %0, i64 %1) {
  call void @__bennett_gate(i32 1, ptr %0, i64 %1)
  ret void
}

declare void @__bennett_gate(i32, ptr, i64)

attributes #0 = { "frame-pointer"="all" "julia.fsig"="body(Ptr{Nothing})" "probe-stack"="inline-asm" }
attributes #1 = { noinline optnone "frame-pointer"="all" "probe-stack"="inline-asm" }
attributes #2 = { memory(argmem: readwrite, inaccessiblemem: readwrite) }
attributes #3 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }

!llvm.module.flags = !{!1, !2, !3, !4}
!llvm.dbg.cu = !{!5}

!0 = !{}
!1 = !{i32 2, !"Dwarf Version", i32 4}
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = !{i32 1, !"stack-protector-guard", !""}
!4 = !{i32 1, !"override-stack-alignment", i32 0}
!5 = distinct !DICompileUnit(language: DW_LANG_Julia, file: !6, producer: "julia", isOptimized: true, runtimeVersion: 0, emissionKind: NoDebug, nameTableKind: GNU)
!6 = !DIFile(filename: "julia", directory: ".")
!7 = distinct !DISubprogram(name: "body", linkageName: "julia_body_483", scope: null, file: !8, line: 76, type: !9, scopeLine: 76, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5, retainedNodes: !14)
!8 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/emission/julia/routes.jl", directory: ".")
!9 = !DISubroutineType(types: !10)
!10 = !{!11, !12, !13}
!11 = !DICompositeType(tag: DW_TAG_structure_type, name: "Nothing", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079415932560")
!12 = !DICompositeType(tag: DW_TAG_structure_type, name: "#body", align: 8, elements: !0, runtimeLang: DW_LANG_Julia, identifier: "127079338221712")
!13 = !DIBasicType(name: "Ptr", size: 64, encoding: DW_ATE_unsigned)
!14 = !{!15, !16}
!15 = !DILocalVariable(name: "#self#", arg: 1, scope: !7, file: !8, line: 76, type: !12)
!16 = !DILocalVariable(name: "p", arg: 2, scope: !7, file: !8, line: 76, type: !13)
!17 = !{!18, !18, i64 0}
!18 = !{!"jtbaa_gcframe", !19, i64 0}
!19 = !{!"jtbaa", !20, i64 0}
!20 = !{!"jtbaa"}
!21 = !{!22, !22, i64 0, i64 1}
!22 = !{!"jtbaa_const", !19, i64 0}
!23 = !DILocation(line: 76, scope: !7)
!24 = !DILocation(line: 151, scope: !25, inlinedAt: !28)
!25 = distinct !DISubprogram(name: "unsafe_load;", linkageName: "unsafe_load", scope: !26, file: !26, type: !27, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!26 = !DIFile(filename: "pointer.jl", directory: ".")
!27 = !DISubroutineType(types: !0)
!28 = !DILocation(line: 151, scope: !25, inlinedAt: !29)
!29 = !DILocation(line: 77, scope: !7)
!30 = !{!19, !19, i64 0}
!31 = !{!32, !34}
!32 = !{!"jnoalias_data", !33}
!33 = !{!"jnoalias"}
!34 = !{!"jnoalias_stack", !33}
!35 = !{!36, !37, !38}
!36 = !{!"jnoalias_gcframe", !33}
!37 = !{!"jnoalias_typemd", !33}
!38 = !{!"jnoalias_const", !33}
!39 = !DILocation(line: 57, scope: !40, inlinedAt: !42)
!40 = distinct !DISubprogram(name: "getproperty;", linkageName: "getproperty", scope: !41, file: !41, type: !27, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!41 = !DIFile(filename: "Base_compiler.jl", directory: ".")
!42 = !DILocation(line: 78, scope: !7)
!43 = !DILocation(line: 35, scope: !44, inlinedAt: !42)
!44 = distinct !DISubprogram(name: "rD_gate;", linkageName: "rD_gate", scope: !8, file: !8, type: !27, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !5)
!45 = !{!38}
!46 = !{!36, !34, !32, !37}
!47 = !{!48, !48, i64 0}
!48 = !{!"jtbaa_stack", !19, i64 0}
!49 = !{!34}
!50 = !{!36, !32, !37, !38}
!51 = !DILocation(line: 79, scope: !7)
!52 = !{i64 8}
!53 = !{!54, !54, i64 0}
!54 = !{!"jtbaa_immut", !55, i64 0}
!55 = !{!"jtbaa_value", !56, i64 0}
!56 = !{!"jtbaa_data", !19, i64 0}
!57 = !{!32}
!58 = !{!36, !34, !37, !38}
