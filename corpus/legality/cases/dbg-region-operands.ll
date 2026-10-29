; CASE: dbg-region-operands
; HAZARD: debug-info variant (clang-18 -g -O0 -Xclang -disable-O0-optnone, noinline removed, llvm.dbg.declare intrinsics: auto-upgraded to debug records by 20/23) of a program whose region operands are shaped by O3 into a select of two functions (if/else around __bennett_adj), a 6-entry @switch.table of function pointers feeding __bennett_ctrl (static helper with a switch, inlined), and rot angles from a fully unrolled loop; checks the verifier accepts it on 18/20/23 after every pass (Enzyme issue 2195 class of failure: a rewritten call losing !dbg) and that -g does not change the transformed code. Question: what operand shapes must the plugin resolve: constant / select-of-constants / phi-of-constants / load-from-constant-table / other
; INPUTS: 0..63
; EXPECT: probe
;
; Generated from this C source (ABI of docs/spikes/2026-10-28-legality-spike.md section 1):
;   /* spike marker ABI v0 (docs/spikes/2026-10-28-legality-spike.md section 1), declared inline */
;   #include <stdint.h>
;   #include <stdbool.h>
;   typedef struct __bennett_q *bq;
;   typedef void (*bregion)(void *env);
;   bq   __bennett_qalloc(uint64_t cls, uint64_t n);
;   bq   __bennett_qborrow(uint64_t cls, uint64_t n);
;   void __bennett_qfree(bq h);
;   void __bennett_gate(uint32_t op, bq h, uint64_t i);
;   void __bennett_gate2(uint32_t op, bq a, uint64_t i, bq b, uint64_t j);
;   void __bennett_rot(uint32_t op, bq h, uint64_t i, double theta);
;   bool __bennett_measure(bq h, uint64_t i);
;   void __bennett_qload(bq dst, bq mem, bq addr);
;   void __bennett_qstore(bq mem, bq addr, bq val);
;   void __bennett_ctrl(bq q, uint64_t qi, bregion f, uint64_t budget, void *env);
;   void __bennett_adj(bregion f, void *env);
;   void __bennett_compute(bregion f, bregion use, void *env);
;   void __bennett_reversible(bregion f, uint64_t budget, void *env);
;   void __bennett_inplace(bregion g, bregion ginv, void *env);
;   void __bennett_ctrl_v(bq q, uint64_t qi, void *f, uint64_t budget, ...);
;   
;   struct env { bq h; uint64_t k; };
;   
;   void reg_f(void *p) { struct env *e = p; __bennett_gate(40, e->h, 0); }
;   void reg_g(void *p) { struct env *e = p; __bennett_gate(41, e->h, 1); }
;   void ora0(void *p) { struct env *e = p; __bennett_gate(50, e->h, e->k & 1); }
;   void ora1(void *p) { struct env *e = p; __bennett_gate(51, e->h, 1); }
;   void ora2(void *p) { struct env *e = p; __bennett_gate(52, e->h, 0); __bennett_gate(52, e->h, 1); }
;   void ora3(void *p) { struct env *e = p; __bennett_gate(53, e->h, 1); }
;   
;   static void apply(bq q, int64_t sel, struct env *e) {
;     switch (sel & 7) {
;     case 0: __bennett_ctrl(q, 0, ora0, 8, e); break;
;     case 1: __bennett_ctrl(q, 0, ora1, 8, e); break;
;     case 2: __bennett_ctrl(q, 0, ora2, 8, e); break;
;     case 3: __bennett_ctrl(q, 0, ora3, 8, e); break;
;     case 4: __bennett_ctrl(q, 0, ora2, 8, e); break;
;     case 5: __bennett_ctrl(q, 0, ora1, 8, e); break;
;     default: __bennett_ctrl(q, 0, ora3, 8, e); break;
;     }
;   }
;   
;   int64_t case_entry(int64_t x) {
;     struct env e;
;     e.h = __bennett_qalloc(0, 2);
;     e.k = (uint64_t)x >> 3;
;     bq q = __bennett_qalloc(0, 1);
;     if (x & 1)
;       __bennett_adj(reg_g, &e);
;     else
;       __bennett_adj(reg_f, &e);
;     for (int i = 0; i < 3; i++) {
;       double th = 0.125 * (double)(i + 1);
;       __bennett_rot(6, e.h, (uint64_t)i & 1, th);
;     }
;     apply(q, x, &e);
;     bool m = __bennett_measure(e.h, 0);
;     __bennett_qfree(q);
;     __bennett_qfree(e.h);
;     return (int64_t)m + (x & 3);
;   }
; ModuleID = 'dbg-src.c'
source_filename = "dbg-src.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct.env = type { ptr, i64 }

; Function Attrs: nounwind uwtable
define dso_local void @reg_f(ptr noundef %0) #0 !dbg !20 {
  %2 = alloca ptr, align 8
  %3 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  call void @llvm.dbg.declare(metadata ptr %2, metadata !25, metadata !DIExpression()), !dbg !26
  call void @llvm.dbg.declare(metadata ptr %3, metadata !27, metadata !DIExpression()), !dbg !36
  %4 = load ptr, ptr %2, align 8, !dbg !37
  store ptr %4, ptr %3, align 8, !dbg !36
  %5 = load ptr, ptr %3, align 8, !dbg !38
  %6 = getelementptr inbounds %struct.env, ptr %5, i32 0, i32 0, !dbg !39
  %7 = load ptr, ptr %6, align 8, !dbg !39
  call void @__bennett_gate(i32 noundef 40, ptr noundef %7, i64 noundef 0), !dbg !40
  ret void, !dbg !41
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef) #2

; Function Attrs: nounwind uwtable
define dso_local void @reg_g(ptr noundef %0) #0 !dbg !42 {
  %2 = alloca ptr, align 8
  %3 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  call void @llvm.dbg.declare(metadata ptr %2, metadata !43, metadata !DIExpression()), !dbg !44
  call void @llvm.dbg.declare(metadata ptr %3, metadata !45, metadata !DIExpression()), !dbg !46
  %4 = load ptr, ptr %2, align 8, !dbg !47
  store ptr %4, ptr %3, align 8, !dbg !46
  %5 = load ptr, ptr %3, align 8, !dbg !48
  %6 = getelementptr inbounds %struct.env, ptr %5, i32 0, i32 0, !dbg !49
  %7 = load ptr, ptr %6, align 8, !dbg !49
  call void @__bennett_gate(i32 noundef 41, ptr noundef %7, i64 noundef 1), !dbg !50
  ret void, !dbg !51
}

; Function Attrs: nounwind uwtable
define dso_local void @ora0(ptr noundef %0) #0 !dbg !52 {
  %2 = alloca ptr, align 8
  %3 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  call void @llvm.dbg.declare(metadata ptr %2, metadata !53, metadata !DIExpression()), !dbg !54
  call void @llvm.dbg.declare(metadata ptr %3, metadata !55, metadata !DIExpression()), !dbg !56
  %4 = load ptr, ptr %2, align 8, !dbg !57
  store ptr %4, ptr %3, align 8, !dbg !56
  %5 = load ptr, ptr %3, align 8, !dbg !58
  %6 = getelementptr inbounds %struct.env, ptr %5, i32 0, i32 0, !dbg !59
  %7 = load ptr, ptr %6, align 8, !dbg !59
  %8 = load ptr, ptr %3, align 8, !dbg !60
  %9 = getelementptr inbounds %struct.env, ptr %8, i32 0, i32 1, !dbg !61
  %10 = load i64, ptr %9, align 8, !dbg !61
  %11 = and i64 %10, 1, !dbg !62
  call void @__bennett_gate(i32 noundef 50, ptr noundef %7, i64 noundef %11), !dbg !63
  ret void, !dbg !64
}

; Function Attrs: nounwind uwtable
define dso_local void @ora1(ptr noundef %0) #0 !dbg !65 {
  %2 = alloca ptr, align 8
  %3 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  call void @llvm.dbg.declare(metadata ptr %2, metadata !66, metadata !DIExpression()), !dbg !67
  call void @llvm.dbg.declare(metadata ptr %3, metadata !68, metadata !DIExpression()), !dbg !69
  %4 = load ptr, ptr %2, align 8, !dbg !70
  store ptr %4, ptr %3, align 8, !dbg !69
  %5 = load ptr, ptr %3, align 8, !dbg !71
  %6 = getelementptr inbounds %struct.env, ptr %5, i32 0, i32 0, !dbg !72
  %7 = load ptr, ptr %6, align 8, !dbg !72
  call void @__bennett_gate(i32 noundef 51, ptr noundef %7, i64 noundef 1), !dbg !73
  ret void, !dbg !74
}

; Function Attrs: nounwind uwtable
define dso_local void @ora2(ptr noundef %0) #0 !dbg !75 {
  %2 = alloca ptr, align 8
  %3 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  call void @llvm.dbg.declare(metadata ptr %2, metadata !76, metadata !DIExpression()), !dbg !77
  call void @llvm.dbg.declare(metadata ptr %3, metadata !78, metadata !DIExpression()), !dbg !79
  %4 = load ptr, ptr %2, align 8, !dbg !80
  store ptr %4, ptr %3, align 8, !dbg !79
  %5 = load ptr, ptr %3, align 8, !dbg !81
  %6 = getelementptr inbounds %struct.env, ptr %5, i32 0, i32 0, !dbg !82
  %7 = load ptr, ptr %6, align 8, !dbg !82
  call void @__bennett_gate(i32 noundef 52, ptr noundef %7, i64 noundef 0), !dbg !83
  %8 = load ptr, ptr %3, align 8, !dbg !84
  %9 = getelementptr inbounds %struct.env, ptr %8, i32 0, i32 0, !dbg !85
  %10 = load ptr, ptr %9, align 8, !dbg !85
  call void @__bennett_gate(i32 noundef 52, ptr noundef %10, i64 noundef 1), !dbg !86
  ret void, !dbg !87
}

; Function Attrs: nounwind uwtable
define dso_local void @ora3(ptr noundef %0) #0 !dbg !88 {
  %2 = alloca ptr, align 8
  %3 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  call void @llvm.dbg.declare(metadata ptr %2, metadata !89, metadata !DIExpression()), !dbg !90
  call void @llvm.dbg.declare(metadata ptr %3, metadata !91, metadata !DIExpression()), !dbg !92
  %4 = load ptr, ptr %2, align 8, !dbg !93
  store ptr %4, ptr %3, align 8, !dbg !92
  %5 = load ptr, ptr %3, align 8, !dbg !94
  %6 = getelementptr inbounds %struct.env, ptr %5, i32 0, i32 0, !dbg !95
  %7 = load ptr, ptr %6, align 8, !dbg !95
  call void @__bennett_gate(i32 noundef 53, ptr noundef %7, i64 noundef 1), !dbg !96
  ret void, !dbg !97
}

; Function Attrs: nounwind uwtable
define dso_local i64 @case_entry(i64 noundef %0) #0 !dbg !98 {
  %2 = alloca i64, align 8
  %3 = alloca %struct.env, align 8
  %4 = alloca ptr, align 8
  %5 = alloca i32, align 4
  %6 = alloca double, align 8
  %7 = alloca i8, align 1
  store i64 %0, ptr %2, align 8
  call void @llvm.dbg.declare(metadata ptr %2, metadata !101, metadata !DIExpression()), !dbg !102
  call void @llvm.dbg.declare(metadata ptr %3, metadata !103, metadata !DIExpression()), !dbg !104
  %8 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 2), !dbg !105
  %9 = getelementptr inbounds %struct.env, ptr %3, i32 0, i32 0, !dbg !106
  store ptr %8, ptr %9, align 8, !dbg !107
  %10 = load i64, ptr %2, align 8, !dbg !108
  %11 = lshr i64 %10, 3, !dbg !109
  %12 = getelementptr inbounds %struct.env, ptr %3, i32 0, i32 1, !dbg !110
  store i64 %11, ptr %12, align 8, !dbg !111
  call void @llvm.dbg.declare(metadata ptr %4, metadata !112, metadata !DIExpression()), !dbg !113
  %13 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1), !dbg !114
  store ptr %13, ptr %4, align 8, !dbg !113
  %14 = load i64, ptr %2, align 8, !dbg !115
  %15 = and i64 %14, 1, !dbg !117
  %16 = icmp ne i64 %15, 0, !dbg !117
  br i1 %16, label %17, label %18, !dbg !118

17:                                               ; preds = %1
  call void @__bennett_adj(ptr noundef @reg_g, ptr noundef %3), !dbg !119
  br label %19, !dbg !119

18:                                               ; preds = %1
  call void @__bennett_adj(ptr noundef @reg_f, ptr noundef %3), !dbg !120
  br label %19

19:                                               ; preds = %18, %17
  call void @llvm.dbg.declare(metadata ptr %5, metadata !121, metadata !DIExpression()), !dbg !124
  store i32 0, ptr %5, align 4, !dbg !124
  br label %20, !dbg !125

20:                                               ; preds = %34, %19
  %21 = load i32, ptr %5, align 4, !dbg !126
  %22 = icmp slt i32 %21, 3, !dbg !128
  br i1 %22, label %23, label %37, !dbg !129

23:                                               ; preds = %20
  call void @llvm.dbg.declare(metadata ptr %6, metadata !130, metadata !DIExpression()), !dbg !132
  %24 = load i32, ptr %5, align 4, !dbg !133
  %25 = add nsw i32 %24, 1, !dbg !134
  %26 = sitofp i32 %25 to double, !dbg !135
  %27 = fmul double 1.250000e-01, %26, !dbg !136
  store double %27, ptr %6, align 8, !dbg !132
  %28 = getelementptr inbounds %struct.env, ptr %3, i32 0, i32 0, !dbg !137
  %29 = load ptr, ptr %28, align 8, !dbg !137
  %30 = load i32, ptr %5, align 4, !dbg !138
  %31 = sext i32 %30 to i64, !dbg !139
  %32 = and i64 %31, 1, !dbg !140
  %33 = load double, ptr %6, align 8, !dbg !141
  call void @__bennett_rot(i32 noundef 6, ptr noundef %29, i64 noundef %32, double noundef %33), !dbg !142
  br label %34, !dbg !143

34:                                               ; preds = %23
  %35 = load i32, ptr %5, align 4, !dbg !144
  %36 = add nsw i32 %35, 1, !dbg !144
  store i32 %36, ptr %5, align 4, !dbg !144
  br label %20, !dbg !145, !llvm.loop !146

37:                                               ; preds = %20
  %38 = load ptr, ptr %4, align 8, !dbg !149
  %39 = load i64, ptr %2, align 8, !dbg !150
  call void @apply(ptr noundef %38, i64 noundef %39, ptr noundef %3), !dbg !151
  call void @llvm.dbg.declare(metadata ptr %7, metadata !152, metadata !DIExpression()), !dbg !154
  %40 = getelementptr inbounds %struct.env, ptr %3, i32 0, i32 0, !dbg !155
  %41 = load ptr, ptr %40, align 8, !dbg !155
  %42 = call zeroext i1 @__bennett_measure(ptr noundef %41, i64 noundef 0), !dbg !156
  %43 = zext i1 %42 to i8, !dbg !154
  store i8 %43, ptr %7, align 1, !dbg !154
  %44 = load ptr, ptr %4, align 8, !dbg !157
  call void @__bennett_qfree(ptr noundef %44), !dbg !158
  %45 = getelementptr inbounds %struct.env, ptr %3, i32 0, i32 0, !dbg !159
  %46 = load ptr, ptr %45, align 8, !dbg !159
  call void @__bennett_qfree(ptr noundef %46), !dbg !160
  %47 = load i8, ptr %7, align 1, !dbg !161
  %48 = trunc i8 %47 to i1, !dbg !161
  %49 = zext i1 %48 to i64, !dbg !162
  %50 = load i64, ptr %2, align 8, !dbg !163
  %51 = and i64 %50, 3, !dbg !164
  %52 = add nsw i64 %49, %51, !dbg !165
  ret i64 %52, !dbg !166
}

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef) #2

declare void @__bennett_adj(ptr noundef, ptr noundef) #2

declare void @__bennett_rot(i32 noundef, ptr noundef, i64 noundef, double noundef) #2

; Function Attrs: nounwind uwtable
define internal void @apply(ptr noundef %0, i64 noundef %1, ptr noundef %2) #0 !dbg !167 {
  %4 = alloca ptr, align 8
  %5 = alloca i64, align 8
  %6 = alloca ptr, align 8
  store ptr %0, ptr %4, align 8
  call void @llvm.dbg.declare(metadata ptr %4, metadata !170, metadata !DIExpression()), !dbg !171
  store i64 %1, ptr %5, align 8
  call void @llvm.dbg.declare(metadata ptr %5, metadata !172, metadata !DIExpression()), !dbg !173
  store ptr %2, ptr %6, align 8
  call void @llvm.dbg.declare(metadata ptr %6, metadata !174, metadata !DIExpression()), !dbg !175
  %7 = load i64, ptr %5, align 8, !dbg !176
  %8 = and i64 %7, 7, !dbg !177
  switch i64 %8, label %27 [
    i64 0, label %9
    i64 1, label %12
    i64 2, label %15
    i64 3, label %18
    i64 4, label %21
    i64 5, label %24
  ], !dbg !178

9:                                                ; preds = %3
  %10 = load ptr, ptr %4, align 8, !dbg !179
  %11 = load ptr, ptr %6, align 8, !dbg !181
  call void @__bennett_ctrl(ptr noundef %10, i64 noundef 0, ptr noundef @ora0, i64 noundef 8, ptr noundef %11), !dbg !182
  br label %30, !dbg !183

12:                                               ; preds = %3
  %13 = load ptr, ptr %4, align 8, !dbg !184
  %14 = load ptr, ptr %6, align 8, !dbg !185
  call void @__bennett_ctrl(ptr noundef %13, i64 noundef 0, ptr noundef @ora1, i64 noundef 8, ptr noundef %14), !dbg !186
  br label %30, !dbg !187

15:                                               ; preds = %3
  %16 = load ptr, ptr %4, align 8, !dbg !188
  %17 = load ptr, ptr %6, align 8, !dbg !189
  call void @__bennett_ctrl(ptr noundef %16, i64 noundef 0, ptr noundef @ora2, i64 noundef 8, ptr noundef %17), !dbg !190
  br label %30, !dbg !191

18:                                               ; preds = %3
  %19 = load ptr, ptr %4, align 8, !dbg !192
  %20 = load ptr, ptr %6, align 8, !dbg !193
  call void @__bennett_ctrl(ptr noundef %19, i64 noundef 0, ptr noundef @ora3, i64 noundef 8, ptr noundef %20), !dbg !194
  br label %30, !dbg !195

21:                                               ; preds = %3
  %22 = load ptr, ptr %4, align 8, !dbg !196
  %23 = load ptr, ptr %6, align 8, !dbg !197
  call void @__bennett_ctrl(ptr noundef %22, i64 noundef 0, ptr noundef @ora2, i64 noundef 8, ptr noundef %23), !dbg !198
  br label %30, !dbg !199

24:                                               ; preds = %3
  %25 = load ptr, ptr %4, align 8, !dbg !200
  %26 = load ptr, ptr %6, align 8, !dbg !201
  call void @__bennett_ctrl(ptr noundef %25, i64 noundef 0, ptr noundef @ora1, i64 noundef 8, ptr noundef %26), !dbg !202
  br label %30, !dbg !203

27:                                               ; preds = %3
  %28 = load ptr, ptr %4, align 8, !dbg !204
  %29 = load ptr, ptr %6, align 8, !dbg !205
  call void @__bennett_ctrl(ptr noundef %28, i64 noundef 0, ptr noundef @ora3, i64 noundef 8, ptr noundef %29), !dbg !206
  br label %30, !dbg !207

30:                                               ; preds = %27, %24, %21, %18, %15, %12, %9
  ret void, !dbg !208
}

declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef) #2

declare void @__bennett_qfree(ptr noundef) #2

declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ptr noundef) #2

attributes #0 = { nounwind uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #2 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!13, !14, !15, !16, !17, !18, !19}

!0 = distinct !DICompileUnit(language: DW_LANG_C11, file: !1, isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, retainedTypes: !2, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "dbg-src.c", directory: "/tmp/bennett-corpus", checksumkind: CSK_MD5, checksum: "3ce9e751e383e8efeff7f7d44ec900f9")
!2 = !{!3, !8, !9}
!3 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint64_t", file: !4, line: 27, baseType: !5)
!4 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/stdint-uintn.h", directory: "", checksumkind: CSK_MD5, checksum: "256fcabbefa27ca8cf5e6d37525e6e16")
!5 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uint64_t", file: !6, line: 45, baseType: !7)
!6 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/types.h", directory: "", checksumkind: CSK_MD5, checksum: "e1865d9fe29fe1b5ced550b7ba458f9e")
!7 = !DIBasicType(name: "unsigned long", size: 64, encoding: DW_ATE_unsigned)
!8 = !DIBasicType(name: "double", size: 64, encoding: DW_ATE_float)
!9 = !DIDerivedType(tag: DW_TAG_typedef, name: "int64_t", file: !10, line: 27, baseType: !11)
!10 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/stdint-intn.h", directory: "", checksumkind: CSK_MD5, checksum: "649b383a60bfa3eb90e85840b2b0be20")
!11 = !DIDerivedType(tag: DW_TAG_typedef, name: "__int64_t", file: !6, line: 44, baseType: !12)
!12 = !DIBasicType(name: "long", size: 64, encoding: DW_ATE_signed)
!13 = !{i32 7, !"Dwarf Version", i32 5}
!14 = !{i32 2, !"Debug Info Version", i32 3}
!15 = !{i32 1, !"wchar_size", i32 4}
!16 = !{i32 8, !"PIC Level", i32 2}
!17 = !{i32 7, !"PIE Level", i32 2}
!18 = !{i32 7, !"uwtable", i32 2}
!19 = !{i32 7, !"frame-pointer", i32 2}
!20 = distinct !DISubprogram(name: "reg_f", scope: !1, file: !1, line: 24, type: !21, scopeLine: 24, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !24)
!21 = !DISubroutineType(types: !22)
!22 = !{null, !23}
!23 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 64)
!24 = !{}
!25 = !DILocalVariable(name: "p", arg: 1, scope: !20, file: !1, line: 24, type: !23)
!26 = !DILocation(line: 24, column: 18, scope: !20)
!27 = !DILocalVariable(name: "e", scope: !20, file: !1, line: 24, type: !28)
!28 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !29, size: 64)
!29 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "env", file: !1, line: 22, size: 128, elements: !30)
!30 = !{!31, !35}
!31 = !DIDerivedType(tag: DW_TAG_member, name: "h", scope: !29, file: !1, line: 22, baseType: !32, size: 64)
!32 = !DIDerivedType(tag: DW_TAG_typedef, name: "bq", file: !1, line: 4, baseType: !33)
!33 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !34, size: 64)
!34 = !DICompositeType(tag: DW_TAG_structure_type, name: "__bennett_q", file: !1, line: 4, flags: DIFlagFwdDecl)
!35 = !DIDerivedType(tag: DW_TAG_member, name: "k", scope: !29, file: !1, line: 22, baseType: !3, size: 64, offset: 64)
!36 = !DILocation(line: 24, column: 35, scope: !20)
!37 = !DILocation(line: 24, column: 39, scope: !20)
!38 = !DILocation(line: 24, column: 61, scope: !20)
!39 = !DILocation(line: 24, column: 64, scope: !20)
!40 = !DILocation(line: 24, column: 42, scope: !20)
!41 = !DILocation(line: 24, column: 71, scope: !20)
!42 = distinct !DISubprogram(name: "reg_g", scope: !1, file: !1, line: 25, type: !21, scopeLine: 25, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !24)
!43 = !DILocalVariable(name: "p", arg: 1, scope: !42, file: !1, line: 25, type: !23)
!44 = !DILocation(line: 25, column: 18, scope: !42)
!45 = !DILocalVariable(name: "e", scope: !42, file: !1, line: 25, type: !28)
!46 = !DILocation(line: 25, column: 35, scope: !42)
!47 = !DILocation(line: 25, column: 39, scope: !42)
!48 = !DILocation(line: 25, column: 61, scope: !42)
!49 = !DILocation(line: 25, column: 64, scope: !42)
!50 = !DILocation(line: 25, column: 42, scope: !42)
!51 = !DILocation(line: 25, column: 71, scope: !42)
!52 = distinct !DISubprogram(name: "ora0", scope: !1, file: !1, line: 26, type: !21, scopeLine: 26, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !24)
!53 = !DILocalVariable(name: "p", arg: 1, scope: !52, file: !1, line: 26, type: !23)
!54 = !DILocation(line: 26, column: 17, scope: !52)
!55 = !DILocalVariable(name: "e", scope: !52, file: !1, line: 26, type: !28)
!56 = !DILocation(line: 26, column: 34, scope: !52)
!57 = !DILocation(line: 26, column: 38, scope: !52)
!58 = !DILocation(line: 26, column: 60, scope: !52)
!59 = !DILocation(line: 26, column: 63, scope: !52)
!60 = !DILocation(line: 26, column: 66, scope: !52)
!61 = !DILocation(line: 26, column: 69, scope: !52)
!62 = !DILocation(line: 26, column: 71, scope: !52)
!63 = !DILocation(line: 26, column: 41, scope: !52)
!64 = !DILocation(line: 26, column: 77, scope: !52)
!65 = distinct !DISubprogram(name: "ora1", scope: !1, file: !1, line: 27, type: !21, scopeLine: 27, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !24)
!66 = !DILocalVariable(name: "p", arg: 1, scope: !65, file: !1, line: 27, type: !23)
!67 = !DILocation(line: 27, column: 17, scope: !65)
!68 = !DILocalVariable(name: "e", scope: !65, file: !1, line: 27, type: !28)
!69 = !DILocation(line: 27, column: 34, scope: !65)
!70 = !DILocation(line: 27, column: 38, scope: !65)
!71 = !DILocation(line: 27, column: 60, scope: !65)
!72 = !DILocation(line: 27, column: 63, scope: !65)
!73 = !DILocation(line: 27, column: 41, scope: !65)
!74 = !DILocation(line: 27, column: 70, scope: !65)
!75 = distinct !DISubprogram(name: "ora2", scope: !1, file: !1, line: 28, type: !21, scopeLine: 28, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !24)
!76 = !DILocalVariable(name: "p", arg: 1, scope: !75, file: !1, line: 28, type: !23)
!77 = !DILocation(line: 28, column: 17, scope: !75)
!78 = !DILocalVariable(name: "e", scope: !75, file: !1, line: 28, type: !28)
!79 = !DILocation(line: 28, column: 34, scope: !75)
!80 = !DILocation(line: 28, column: 38, scope: !75)
!81 = !DILocation(line: 28, column: 60, scope: !75)
!82 = !DILocation(line: 28, column: 63, scope: !75)
!83 = !DILocation(line: 28, column: 41, scope: !75)
!84 = !DILocation(line: 28, column: 89, scope: !75)
!85 = !DILocation(line: 28, column: 92, scope: !75)
!86 = !DILocation(line: 28, column: 70, scope: !75)
!87 = !DILocation(line: 28, column: 99, scope: !75)
!88 = distinct !DISubprogram(name: "ora3", scope: !1, file: !1, line: 29, type: !21, scopeLine: 29, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !24)
!89 = !DILocalVariable(name: "p", arg: 1, scope: !88, file: !1, line: 29, type: !23)
!90 = !DILocation(line: 29, column: 17, scope: !88)
!91 = !DILocalVariable(name: "e", scope: !88, file: !1, line: 29, type: !28)
!92 = !DILocation(line: 29, column: 34, scope: !88)
!93 = !DILocation(line: 29, column: 38, scope: !88)
!94 = !DILocation(line: 29, column: 60, scope: !88)
!95 = !DILocation(line: 29, column: 63, scope: !88)
!96 = !DILocation(line: 29, column: 41, scope: !88)
!97 = !DILocation(line: 29, column: 70, scope: !88)
!98 = distinct !DISubprogram(name: "case_entry", scope: !1, file: !1, line: 43, type: !99, scopeLine: 43, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !24)
!99 = !DISubroutineType(types: !100)
!100 = !{!9, !9}
!101 = !DILocalVariable(name: "x", arg: 1, scope: !98, file: !1, line: 43, type: !9)
!102 = !DILocation(line: 43, column: 28, scope: !98)
!103 = !DILocalVariable(name: "e", scope: !98, file: !1, line: 44, type: !29)
!104 = !DILocation(line: 44, column: 14, scope: !98)
!105 = !DILocation(line: 45, column: 9, scope: !98)
!106 = !DILocation(line: 45, column: 5, scope: !98)
!107 = !DILocation(line: 45, column: 7, scope: !98)
!108 = !DILocation(line: 46, column: 19, scope: !98)
!109 = !DILocation(line: 46, column: 21, scope: !98)
!110 = !DILocation(line: 46, column: 5, scope: !98)
!111 = !DILocation(line: 46, column: 7, scope: !98)
!112 = !DILocalVariable(name: "q", scope: !98, file: !1, line: 47, type: !32)
!113 = !DILocation(line: 47, column: 6, scope: !98)
!114 = !DILocation(line: 47, column: 10, scope: !98)
!115 = !DILocation(line: 48, column: 7, scope: !116)
!116 = distinct !DILexicalBlock(scope: !98, file: !1, line: 48, column: 7)
!117 = !DILocation(line: 48, column: 9, scope: !116)
!118 = !DILocation(line: 48, column: 7, scope: !98)
!119 = !DILocation(line: 49, column: 5, scope: !116)
!120 = !DILocation(line: 51, column: 5, scope: !116)
!121 = !DILocalVariable(name: "i", scope: !122, file: !1, line: 52, type: !123)
!122 = distinct !DILexicalBlock(scope: !98, file: !1, line: 52, column: 3)
!123 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!124 = !DILocation(line: 52, column: 12, scope: !122)
!125 = !DILocation(line: 52, column: 8, scope: !122)
!126 = !DILocation(line: 52, column: 19, scope: !127)
!127 = distinct !DILexicalBlock(scope: !122, file: !1, line: 52, column: 3)
!128 = !DILocation(line: 52, column: 21, scope: !127)
!129 = !DILocation(line: 52, column: 3, scope: !122)
!130 = !DILocalVariable(name: "th", scope: !131, file: !1, line: 53, type: !8)
!131 = distinct !DILexicalBlock(scope: !127, file: !1, line: 52, column: 31)
!132 = !DILocation(line: 53, column: 12, scope: !131)
!133 = !DILocation(line: 53, column: 34, scope: !131)
!134 = !DILocation(line: 53, column: 36, scope: !131)
!135 = !DILocation(line: 53, column: 25, scope: !131)
!136 = !DILocation(line: 53, column: 23, scope: !131)
!137 = !DILocation(line: 54, column: 24, scope: !131)
!138 = !DILocation(line: 54, column: 37, scope: !131)
!139 = !DILocation(line: 54, column: 27, scope: !131)
!140 = !DILocation(line: 54, column: 39, scope: !131)
!141 = !DILocation(line: 54, column: 44, scope: !131)
!142 = !DILocation(line: 54, column: 5, scope: !131)
!143 = !DILocation(line: 55, column: 3, scope: !131)
!144 = !DILocation(line: 52, column: 27, scope: !127)
!145 = !DILocation(line: 52, column: 3, scope: !127)
!146 = distinct !{!146, !129, !147, !148}
!147 = !DILocation(line: 55, column: 3, scope: !122)
!148 = !{!"llvm.loop.mustprogress"}
!149 = !DILocation(line: 56, column: 9, scope: !98)
!150 = !DILocation(line: 56, column: 12, scope: !98)
!151 = !DILocation(line: 56, column: 3, scope: !98)
!152 = !DILocalVariable(name: "m", scope: !98, file: !1, line: 57, type: !153)
!153 = !DIBasicType(name: "_Bool", size: 8, encoding: DW_ATE_boolean)
!154 = !DILocation(line: 57, column: 8, scope: !98)
!155 = !DILocation(line: 57, column: 32, scope: !98)
!156 = !DILocation(line: 57, column: 12, scope: !98)
!157 = !DILocation(line: 58, column: 19, scope: !98)
!158 = !DILocation(line: 58, column: 3, scope: !98)
!159 = !DILocation(line: 59, column: 21, scope: !98)
!160 = !DILocation(line: 59, column: 3, scope: !98)
!161 = !DILocation(line: 60, column: 19, scope: !98)
!162 = !DILocation(line: 60, column: 10, scope: !98)
!163 = !DILocation(line: 60, column: 24, scope: !98)
!164 = !DILocation(line: 60, column: 26, scope: !98)
!165 = !DILocation(line: 60, column: 21, scope: !98)
!166 = !DILocation(line: 60, column: 3, scope: !98)
!167 = distinct !DISubprogram(name: "apply", scope: !1, file: !1, line: 31, type: !168, scopeLine: 31, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition, unit: !0, retainedNodes: !24)
!168 = !DISubroutineType(types: !169)
!169 = !{null, !32, !9, !28}
!170 = !DILocalVariable(name: "q", arg: 1, scope: !167, file: !1, line: 31, type: !32)
!171 = !DILocation(line: 31, column: 22, scope: !167)
!172 = !DILocalVariable(name: "sel", arg: 2, scope: !167, file: !1, line: 31, type: !9)
!173 = !DILocation(line: 31, column: 33, scope: !167)
!174 = !DILocalVariable(name: "e", arg: 3, scope: !167, file: !1, line: 31, type: !28)
!175 = !DILocation(line: 31, column: 50, scope: !167)
!176 = !DILocation(line: 32, column: 11, scope: !167)
!177 = !DILocation(line: 32, column: 15, scope: !167)
!178 = !DILocation(line: 32, column: 3, scope: !167)
!179 = !DILocation(line: 33, column: 26, scope: !180)
!180 = distinct !DILexicalBlock(scope: !167, file: !1, line: 32, column: 20)
!181 = !DILocation(line: 33, column: 41, scope: !180)
!182 = !DILocation(line: 33, column: 11, scope: !180)
!183 = !DILocation(line: 33, column: 45, scope: !180)
!184 = !DILocation(line: 34, column: 26, scope: !180)
!185 = !DILocation(line: 34, column: 41, scope: !180)
!186 = !DILocation(line: 34, column: 11, scope: !180)
!187 = !DILocation(line: 34, column: 45, scope: !180)
!188 = !DILocation(line: 35, column: 26, scope: !180)
!189 = !DILocation(line: 35, column: 41, scope: !180)
!190 = !DILocation(line: 35, column: 11, scope: !180)
!191 = !DILocation(line: 35, column: 45, scope: !180)
!192 = !DILocation(line: 36, column: 26, scope: !180)
!193 = !DILocation(line: 36, column: 41, scope: !180)
!194 = !DILocation(line: 36, column: 11, scope: !180)
!195 = !DILocation(line: 36, column: 45, scope: !180)
!196 = !DILocation(line: 37, column: 26, scope: !180)
!197 = !DILocation(line: 37, column: 41, scope: !180)
!198 = !DILocation(line: 37, column: 11, scope: !180)
!199 = !DILocation(line: 37, column: 45, scope: !180)
!200 = !DILocation(line: 38, column: 26, scope: !180)
!201 = !DILocation(line: 38, column: 41, scope: !180)
!202 = !DILocation(line: 38, column: 11, scope: !180)
!203 = !DILocation(line: 38, column: 45, scope: !180)
!204 = !DILocation(line: 39, column: 27, scope: !180)
!205 = !DILocation(line: 39, column: 42, scope: !180)
!206 = !DILocation(line: 39, column: 12, scope: !180)
!207 = !DILocation(line: 39, column: 46, scope: !180)
!208 = !DILocation(line: 41, column: 1, scope: !167)
