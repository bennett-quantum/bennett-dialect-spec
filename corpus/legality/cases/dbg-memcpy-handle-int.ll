; CASE: dbg-memcpy-handle-int
; HAZARD: debug-info variant of c-memcpy-handle-int (clang-18 -g, noinline removed): the 8-byte memcpy of a handle becomes ptrtoint + store i64 under instcombine; additionally checks that the dbg.declare/dbg.value (debug records on 20/23) describing the handle variables survive verification, and whether salvaging produces DIExpressions over the ptrtoint'd handle. Generated from cases/c-memcpy-handle-int.c
; INPUTS: 0..63
; EXPECT: probe
; ModuleID = '/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/cases/c-memcpy-handle-int.c'
source_filename = "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/cases/c-memcpy-handle-int.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct.env1 = type { ptr, i64 }
%struct.pair = type { ptr, ptr }

@gslot = dso_local global [4 x ptr] zeroinitializer, align 16, !dbg !0

; Function Attrs: nounwind uwtable
define dso_local i64 @case_entry(i64 noundef %0) #0 !dbg !19 {
  %2 = alloca i64, align 8
  %3 = alloca %struct.env1, align 8
  %4 = alloca %struct.pair, align 8
  %5 = alloca %struct.pair, align 8
  %6 = alloca ptr, align 8
  store i64 %0, ptr %2, align 8
  call void @llvm.dbg.declare(metadata ptr %2, metadata !28, metadata !DIExpression()), !dbg !29
  call void @llvm.dbg.declare(metadata ptr %3, metadata !30, metadata !DIExpression()), !dbg !39
  %7 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1), !dbg !40
  %8 = load i64, ptr %2, align 8, !dbg !41
  %9 = and i64 %8, 3, !dbg !42
  %10 = getelementptr inbounds [4 x ptr], ptr @gslot, i64 0, i64 %9, !dbg !43
  store ptr %7, ptr %10, align 8, !dbg !44
  %11 = getelementptr inbounds %struct.env1, ptr %3, i32 0, i32 0, !dbg !45
  %12 = load i64, ptr %2, align 8, !dbg !46
  %13 = and i64 %12, 3, !dbg !47
  %14 = getelementptr inbounds [4 x ptr], ptr @gslot, i64 0, i64 %13, !dbg !48
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %11, ptr align 8 %14, i64 8, i1 false), !dbg !49
  %15 = getelementptr inbounds %struct.env1, ptr %3, i32 0, i32 1, !dbg !50
  store i64 0, ptr %15, align 8, !dbg !51
  %16 = getelementptr inbounds %struct.env1, ptr %3, i32 0, i32 0, !dbg !52
  %17 = load ptr, ptr %16, align 8, !dbg !52
  call void @__bennett_gate(i32 noundef 2, ptr noundef %17, i64 noundef 0), !dbg !53
  %18 = getelementptr inbounds %struct.env1, ptr %3, i32 0, i32 0, !dbg !54
  %19 = load ptr, ptr %18, align 8, !dbg !54
  call void @__bennett_ctrl(ptr noundef %19, i64 noundef 0, ptr noundef @rg, i64 noundef 4, ptr noundef %3), !dbg !55
  call void @llvm.dbg.declare(metadata ptr %4, metadata !56, metadata !DIExpression()), !dbg !61
  call void @llvm.dbg.declare(metadata ptr %5, metadata !62, metadata !DIExpression()), !dbg !63
  %20 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1), !dbg !64
  %21 = getelementptr inbounds %struct.pair, ptr %4, i32 0, i32 0, !dbg !65
  store ptr %20, ptr %21, align 8, !dbg !66
  %22 = load i64, ptr %2, align 8, !dbg !67
  %23 = and i64 %22, 3, !dbg !68
  %24 = getelementptr inbounds [4 x ptr], ptr @gslot, i64 0, i64 %23, !dbg !69
  %25 = load ptr, ptr %24, align 8, !dbg !69
  %26 = getelementptr inbounds %struct.pair, ptr %4, i32 0, i32 1, !dbg !70
  store ptr %25, ptr %26, align 8, !dbg !71
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %5, ptr align 8 %4, i64 16, i1 false), !dbg !72
  call void @__bennett_adj(ptr noundef @rpair, ptr noundef %5), !dbg !73
  call void @llvm.dbg.declare(metadata ptr %6, metadata !74, metadata !DIExpression()), !dbg !75
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %6, ptr align 8 %3, i64 8, i1 false), !dbg !76
  %27 = getelementptr inbounds %struct.pair, ptr %5, i32 0, i32 0, !dbg !77
  %28 = load ptr, ptr %27, align 8, !dbg !77
  call void @__bennett_qfree(ptr noundef %28), !dbg !78
  %29 = load ptr, ptr %6, align 8, !dbg !79
  call void @__bennett_qfree(ptr noundef %29), !dbg !80
  %30 = load i64, ptr %2, align 8, !dbg !81
  ret i64 %30, !dbg !82
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef) #2

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #3

declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef) #2

declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ptr noundef) #2

; Function Attrs: nounwind uwtable
define internal void @rg(ptr noundef %0) #0 !dbg !83 {
  %2 = alloca ptr, align 8
  %3 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  call void @llvm.dbg.declare(metadata ptr %2, metadata !87, metadata !DIExpression()), !dbg !88
  call void @llvm.dbg.declare(metadata ptr %3, metadata !89, metadata !DIExpression()), !dbg !91
  %4 = load ptr, ptr %2, align 8, !dbg !92
  store ptr %4, ptr %3, align 8, !dbg !91
  %5 = load ptr, ptr %3, align 8, !dbg !93
  %6 = getelementptr inbounds %struct.env1, ptr %5, i32 0, i32 0, !dbg !94
  %7 = load ptr, ptr %6, align 8, !dbg !94
  %8 = load ptr, ptr %3, align 8, !dbg !95
  %9 = getelementptr inbounds %struct.env1, ptr %8, i32 0, i32 1, !dbg !96
  %10 = load i64, ptr %9, align 8, !dbg !96
  call void @__bennett_gate(i32 noundef 1, ptr noundef %7, i64 noundef %10), !dbg !97
  ret void, !dbg !98
}

declare void @__bennett_adj(ptr noundef, ptr noundef) #2

; Function Attrs: nounwind uwtable
define internal void @rpair(ptr noundef %0) #0 !dbg !99 {
  %2 = alloca ptr, align 8
  %3 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  call void @llvm.dbg.declare(metadata ptr %2, metadata !100, metadata !DIExpression()), !dbg !101
  call void @llvm.dbg.declare(metadata ptr %3, metadata !102, metadata !DIExpression()), !dbg !104
  %4 = load ptr, ptr %2, align 8, !dbg !105
  store ptr %4, ptr %3, align 8, !dbg !104
  %5 = load ptr, ptr %3, align 8, !dbg !106
  %6 = getelementptr inbounds %struct.pair, ptr %5, i32 0, i32 0, !dbg !107
  %7 = load ptr, ptr %6, align 8, !dbg !107
  %8 = load ptr, ptr %3, align 8, !dbg !108
  %9 = getelementptr inbounds %struct.pair, ptr %8, i32 0, i32 1, !dbg !109
  %10 = load ptr, ptr %9, align 8, !dbg !109
  call void @__bennett_gate2(i32 noundef 3, ptr noundef %7, i64 noundef 0, ptr noundef %10, i64 noundef 0), !dbg !110
  ret void, !dbg !111
}

declare void @__bennett_qfree(ptr noundef) #2

declare void @__bennett_gate2(i32 noundef, ptr noundef, i64 noundef, ptr noundef, i64 noundef) #2

attributes #0 = { nounwind uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #2 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }

!llvm.dbg.cu = !{!2}
!llvm.module.flags = !{!12, !13, !14, !15, !16, !17, !18}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "gslot", scope: !2, file: !5, line: 29, type: !6, isLocal: false, isDefinition: true)
!2 = distinct !DICompileUnit(language: DW_LANG_C11, file: !3, isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, globals: !4, splitDebugInlining: false, nameTableKind: None)
!3 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/cases/c-memcpy-handle-int.c", directory: "/tmp/bennett-corpus", checksumkind: CSK_MD5, checksum: "dbe411dbcfdb2e76cc71e3fe864700d1")
!4 = !{!0}
!5 = !DIFile(filename: "/home/tobias/Projects/bennett-workspace/bennett-dialect-spec/corpus/legality/cases/c-memcpy-handle-int.c", directory: "", checksumkind: CSK_MD5, checksum: "dbe411dbcfdb2e76cc71e3fe864700d1")
!6 = !DICompositeType(tag: DW_TAG_array_type, baseType: !7, size: 256, elements: !10)
!7 = !DIDerivedType(tag: DW_TAG_typedef, name: "bq", file: !5, line: 9, baseType: !8)
!8 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !9, size: 64)
!9 = !DICompositeType(tag: DW_TAG_structure_type, name: "__bennett_q", file: !5, line: 9, flags: DIFlagFwdDecl)
!10 = !{!11}
!11 = !DISubrange(count: 4)
!12 = !{i32 7, !"Dwarf Version", i32 5}
!13 = !{i32 2, !"Debug Info Version", i32 3}
!14 = !{i32 1, !"wchar_size", i32 4}
!15 = !{i32 8, !"PIC Level", i32 2}
!16 = !{i32 7, !"PIE Level", i32 2}
!17 = !{i32 7, !"uwtable", i32 2}
!18 = !{i32 7, !"frame-pointer", i32 2}
!19 = distinct !DISubprogram(name: "case_entry", scope: !5, file: !5, line: 41, type: !20, scopeLine: 41, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !2, retainedNodes: !27)
!20 = !DISubroutineType(types: !21)
!21 = !{!22, !22}
!22 = !DIDerivedType(tag: DW_TAG_typedef, name: "int64_t", file: !23, line: 27, baseType: !24)
!23 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/stdint-intn.h", directory: "", checksumkind: CSK_MD5, checksum: "649b383a60bfa3eb90e85840b2b0be20")
!24 = !DIDerivedType(tag: DW_TAG_typedef, name: "__int64_t", file: !25, line: 44, baseType: !26)
!25 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/types.h", directory: "", checksumkind: CSK_MD5, checksum: "e1865d9fe29fe1b5ced550b7ba458f9e")
!26 = !DIBasicType(name: "long", size: 64, encoding: DW_ATE_signed)
!27 = !{}
!28 = !DILocalVariable(name: "x", arg: 1, scope: !19, file: !5, line: 41, type: !22)
!29 = !DILocation(line: 41, column: 28, scope: !19)
!30 = !DILocalVariable(name: "e", scope: !19, file: !5, line: 42, type: !31)
!31 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "env1", file: !5, line: 27, size: 128, elements: !32)
!32 = !{!33, !34}
!33 = !DIDerivedType(tag: DW_TAG_member, name: "h", scope: !31, file: !5, line: 27, baseType: !7, size: 64)
!34 = !DIDerivedType(tag: DW_TAG_member, name: "i", scope: !31, file: !5, line: 27, baseType: !35, size: 64, offset: 64)
!35 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint64_t", file: !36, line: 27, baseType: !37)
!36 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/stdint-uintn.h", directory: "", checksumkind: CSK_MD5, checksum: "256fcabbefa27ca8cf5e6d37525e6e16")
!37 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uint64_t", file: !25, line: 45, baseType: !38)
!38 = !DIBasicType(name: "unsigned long", size: 64, encoding: DW_ATE_unsigned)
!39 = !DILocation(line: 42, column: 15, scope: !19)
!40 = !DILocation(line: 43, column: 18, scope: !19)
!41 = !DILocation(line: 43, column: 9, scope: !19)
!42 = !DILocation(line: 43, column: 11, scope: !19)
!43 = !DILocation(line: 43, column: 3, scope: !19)
!44 = !DILocation(line: 43, column: 16, scope: !19)
!45 = !DILocation(line: 44, column: 13, scope: !19)
!46 = !DILocation(line: 44, column: 23, scope: !19)
!47 = !DILocation(line: 44, column: 25, scope: !19)
!48 = !DILocation(line: 44, column: 17, scope: !19)
!49 = !DILocation(line: 44, column: 3, scope: !19)
!50 = !DILocation(line: 45, column: 5, scope: !19)
!51 = !DILocation(line: 45, column: 7, scope: !19)
!52 = !DILocation(line: 46, column: 23, scope: !19)
!53 = !DILocation(line: 46, column: 3, scope: !19)
!54 = !DILocation(line: 47, column: 20, scope: !19)
!55 = !DILocation(line: 47, column: 3, scope: !19)
!56 = !DILocalVariable(name: "p", scope: !19, file: !5, line: 49, type: !57)
!57 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "pair", file: !5, line: 28, size: 128, elements: !58)
!58 = !{!59, !60}
!59 = !DIDerivedType(tag: DW_TAG_member, name: "a", scope: !57, file: !5, line: 28, baseType: !7, size: 64)
!60 = !DIDerivedType(tag: DW_TAG_member, name: "b", scope: !57, file: !5, line: 28, baseType: !7, size: 64, offset: 64)
!61 = !DILocation(line: 49, column: 15, scope: !19)
!62 = !DILocalVariable(name: "q", scope: !19, file: !5, line: 49, type: !57)
!63 = !DILocation(line: 49, column: 18, scope: !19)
!64 = !DILocation(line: 50, column: 9, scope: !19)
!65 = !DILocation(line: 50, column: 5, scope: !19)
!66 = !DILocation(line: 50, column: 7, scope: !19)
!67 = !DILocation(line: 51, column: 15, scope: !19)
!68 = !DILocation(line: 51, column: 17, scope: !19)
!69 = !DILocation(line: 51, column: 9, scope: !19)
!70 = !DILocation(line: 51, column: 5, scope: !19)
!71 = !DILocation(line: 51, column: 7, scope: !19)
!72 = !DILocation(line: 52, column: 7, scope: !19)
!73 = !DILocation(line: 53, column: 3, scope: !19)
!74 = !DILocalVariable(name: "t", scope: !19, file: !5, line: 55, type: !7)
!75 = !DILocation(line: 55, column: 6, scope: !19)
!76 = !DILocation(line: 56, column: 3, scope: !19)
!77 = !DILocation(line: 57, column: 21, scope: !19)
!78 = !DILocation(line: 57, column: 3, scope: !19)
!79 = !DILocation(line: 58, column: 19, scope: !19)
!80 = !DILocation(line: 58, column: 3, scope: !19)
!81 = !DILocation(line: 59, column: 10, scope: !19)
!82 = !DILocation(line: 59, column: 3, scope: !19)
!83 = distinct !DISubprogram(name: "rg", scope: !5, file: !5, line: 31, type: !84, scopeLine: 31, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition, unit: !2, retainedNodes: !27)
!84 = !DISubroutineType(types: !85)
!85 = !{null, !86}
!86 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 64)
!87 = !DILocalVariable(name: "e", arg: 1, scope: !83, file: !5, line: 31, type: !86)
!88 = !DILocation(line: 31, column: 22, scope: !83)
!89 = !DILocalVariable(name: "p", scope: !83, file: !5, line: 32, type: !90)
!90 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !31, size: 64)
!91 = !DILocation(line: 32, column: 16, scope: !83)
!92 = !DILocation(line: 32, column: 20, scope: !83)
!93 = !DILocation(line: 33, column: 21, scope: !83)
!94 = !DILocation(line: 33, column: 24, scope: !83)
!95 = !DILocation(line: 33, column: 27, scope: !83)
!96 = !DILocation(line: 33, column: 30, scope: !83)
!97 = !DILocation(line: 33, column: 3, scope: !83)
!98 = !DILocation(line: 34, column: 1, scope: !83)
!99 = distinct !DISubprogram(name: "rpair", scope: !5, file: !5, line: 36, type: !84, scopeLine: 36, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition, unit: !2, retainedNodes: !27)
!100 = !DILocalVariable(name: "e", arg: 1, scope: !99, file: !5, line: 36, type: !86)
!101 = !DILocation(line: 36, column: 25, scope: !99)
!102 = !DILocalVariable(name: "p", scope: !99, file: !5, line: 37, type: !103)
!103 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !57, size: 64)
!104 = !DILocation(line: 37, column: 16, scope: !99)
!105 = !DILocation(line: 37, column: 20, scope: !99)
!106 = !DILocation(line: 38, column: 22, scope: !99)
!107 = !DILocation(line: 38, column: 25, scope: !99)
!108 = !DILocation(line: 38, column: 31, scope: !99)
!109 = !DILocation(line: 38, column: 34, scope: !99)
!110 = !DILocation(line: 38, column: 3, scope: !99)
!111 = !DILocation(line: 39, column: 1, scope: !99)
