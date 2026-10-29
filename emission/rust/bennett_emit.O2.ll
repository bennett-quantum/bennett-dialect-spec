; ModuleID = 'bennett_emit.O2.bc'
source_filename = "bennett_emit.7dee62cccf2c2c09-cgu.0"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@alloc_1962bf4fe486936f0f5554c0adc669f6 = private unnamed_addr constant [16 x i8] c"bennett_emit.rs\00", align 1, !guid !0
@alloc_37f62a15fae368a2423b3a16c75adcc9 = private unnamed_addr constant [1 x i8] c"x", align 1, !guid !1
@alloc_f4d302337a3abcf1f4238b174f3f0242 = private unnamed_addr constant <{ ptr, [16 x i8] }> <{ ptr @alloc_1962bf4fe486936f0f5554c0adc669f6, [16 x i8] c"\0F\00\00\00\00\00\00\005\00\00\008\00\00\00" }>, align 8, !guid !2

; Function Attrs: nounwind nonlazybind uwtable
define internal void @_RINvCsaOknTnIz6g7_12bennett_emit5trampNCNvB2_10case_entry0EB2_(ptr nofree noundef readonly captures(none) %p) unnamed_addr #0 personality ptr @rust_eh_personality !guid !7 {
bb2:
  tail call void @llvm.experimental.noalias.scope.decl(metadata !8)
  %_3.i = load ptr, ptr %p, align 8, !alias.scope !8, !noundef !11
  %0 = getelementptr inbounds nuw i8, ptr %p, i64 8
  %_4.i = load i64, ptr %0, align 8, !alias.scope !8, !noundef !11
  tail call void @__bennett_gate(i32 noundef 5, ptr noundef %_3.i, i64 noundef %_4.i) #6, !noalias !8
  ret void
}

; Function Attrs: nounwind nonlazybind uwtable
define internal void @_RNvCsaOknTnIz6g7_12bennett_emit4body(ptr nofree noundef readonly captures(none) %p) unnamed_addr #0 !guid !12 {
start:
  %_4 = load ptr, ptr %p, align 8, !noundef !11
  %0 = getelementptr inbounds nuw i8, ptr %p, i64 8
  %_5 = load i64, ptr %0, align 8, !noundef !11
  %1 = getelementptr inbounds nuw i8, ptr %p, i64 16
  %_6 = load double, ptr %1, align 8, !noundef !11
  tail call void @__bennett_rot(i32 noundef 1, ptr noundef %_4, i64 noundef %_5, double noundef %_6) #6
  %_8 = load ptr, ptr %p, align 8, !noundef !11
  %_9 = load i64, ptr %0, align 8, !noundef !11
  tail call void @__bennett_gate(i32 noundef 2, ptr noundef %_8, i64 noundef %_9) #6
  ret void
}

; Function Attrs: nounwind nonlazybind uwtable
define void @_RNvXCsaOknTnIz6g7_12bennett_emitNtB2_5GuardNtNtNtCskADBYZwJmSU_4core3ops4drop4Drop4drop(ptr noalias nofree noundef readonly align 8 captures(none) dereferenceable(8) %self) unnamed_addr #0 !guid !13 {
start:
  %_2 = load ptr, ptr %self, align 8, !noundef !11
  tail call void @__bennett_qfree(ptr noundef %_2) #6
  ret void
}

; Function Attrs: nounwind nonlazybind uwtable
define noundef range(i64 0, 2) i64 @case_entry(i64 noundef %x) unnamed_addr #0 personality ptr @rust_eh_personality !guid !14 {
start:
  %tab = alloca [32 x i8], align 8
  %e = alloca [24 x i8], align 8
  %h = tail call noundef ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 4) #6
  tail call void @__bennett_gate(i32 noundef 1, ptr noundef %h, i64 noundef 0) #6
  %_5 = uitofp i64 %x to double
  %theta = fmul nnan double %_5, 1.250000e-01
  tail call void @__bennett_rot(i32 noundef 3, ptr noundef %h, i64 noundef 1, double noundef %theta) #6
  tail call void @__bennett_gate2(i32 noundef 4, ptr noundef %h, i64 noundef 0, ptr noundef %h, i64 noundef 1) #6
  %_8 = tail call noundef zeroext i1 @__bennett_measure(ptr noundef %h, i64 noundef 0) #6
  br i1 %_8, label %bb6, label %bb10

bb6:                                              ; preds = %start
  tail call void @__bennett_gate(i32 noundef 2, ptr noundef %h, i64 noundef 2) #6
  br label %bb10

bb10:                                             ; preds = %bb6, %start
  %r.sroa.0.0 = phi i64 [ 1, %bb6 ], [ 0, %start ]
  call void @llvm.lifetime.start.p0(ptr nonnull %e)
  store ptr %h, ptr %e, align 8
  %0 = getelementptr inbounds nuw i8, ptr %e, i64 8
  store i64 3, ptr %0, align 8
  %1 = getelementptr inbounds nuw i8, ptr %e, i64 16
  store double %theta, ptr %1, align 8
  call void @__bennett_ctrl(ptr noundef %h, i64 noundef 0, ptr noundef nonnull @_RNvCsaOknTnIz6g7_12bennett_emit4body, i64 noundef 8, ptr noundef nonnull %e) #6
  call void @__bennett_ctrl(ptr noundef %h, i64 noundef 1, ptr noundef nonnull @_RINvCsaOknTnIz6g7_12bennett_emit5trampNCNvB2_10case_entry0EB2_, i64 noundef 8, ptr noundef nonnull %e) #6
  call void @llvm.lifetime.start.p0(ptr nonnull %tab)
  %_22 = call noundef ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1) #6
  store ptr %_22, ptr %tab, align 8
  %_22.1 = call noundef ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1) #6
  %2 = getelementptr inbounds nuw i8, ptr %tab, i64 8
  store ptr %_22.1, ptr %2, align 8
  %_22.2 = call noundef ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1) #6
  %3 = getelementptr inbounds nuw i8, ptr %tab, i64 16
  store ptr %_22.2, ptr %3, align 8
  %_22.3 = call noundef ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1) #6
  %4 = getelementptr inbounds nuw i8, ptr %tab, i64 24
  store ptr %_22.3, ptr %4, align 8
  %_27 = and i64 %x, 3
  %5 = getelementptr inbounds nuw [8 x i8], ptr %tab, i64 %_27
  %_25 = load ptr, ptr %5, align 8, !noundef !11
  call void @__bennett_gate(i32 noundef 1, ptr noundef %_25, i64 noundef 0) #6
  call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr noundef %h, i64 noundef 0, ptr noundef nonnull @_RNvCsaOknTnIz6g7_12bennett_emit4body, i64 noundef 8, i32 noundef 1, double noundef 2.500000e+00, ptr noundef %h) #6
  call void @__bennett_adj(ptr noundef nonnull @_RNvCsaOknTnIz6g7_12bennett_emit4body, ptr noundef nonnull %e) #6
  call void @__bennett_compute(ptr noundef nonnull @_RNvCsaOknTnIz6g7_12bennett_emit4body, ptr noundef nonnull @_RNvCsaOknTnIz6g7_12bennett_emit4body, ptr noundef nonnull %e) #6
  call void @__bennett_reversible(ptr noundef nonnull @_RNvCsaOknTnIz6g7_12bennett_emit4body, i64 noundef 3, ptr noundef nonnull %e) #6
  call void @__bennett_inplace(ptr noundef nonnull @_RNvCsaOknTnIz6g7_12bennett_emit4body, ptr noundef nonnull @_RNvCsaOknTnIz6g7_12bennett_emit4body, ptr noundef nonnull %e) #6
  %_51 = call noundef ptr @__bennett_qborrow(i64 noundef 0, i64 noundef 1) #6
  call void @__bennett_qload(ptr noundef %_51, ptr noundef %h, ptr noundef %_22) #6
  call void @__bennett_qstore(ptr noundef %h, ptr noundef %_22.1, ptr noundef %_51) #6
  call void @rt_may_unwind(i64 noundef %x) #7
  call void @__bennett_gate(i32 noundef 6, ptr noundef %_51, i64 noundef 0)
  call void @__bennett_qfree(ptr noundef %_51) #6, !noalias !15
  call void @__bennett_qfree(ptr noundef %h)
  call void @__bennett_qfree(ptr noundef %_22) #6
  call void @__bennett_qfree(ptr noundef %_22.1) #6
  call void @__bennett_qfree(ptr noundef %_22.2) #6
  call void @__bennett_qfree(ptr noundef %_22.3) #6
  call void @__bennett_qfree(ptr noundef %h) #6
  call void @llvm.lifetime.end.p0(ptr nonnull %tab)
  call void @llvm.lifetime.end.p0(ptr nonnull %e)
  ret i64 %r.sroa.0.0
}

; Function Attrs: noinline nounwind nonlazybind uwtable
define void @rt_may_unwind(i64 noundef %x) unnamed_addr #1 personality ptr @rust_eh_personality !guid !20 {
start:
  %0 = icmp eq i64 %x, 77
  br i1 %0, label %bb1, label %bb2, !prof !21

bb1:                                              ; preds = %start
  invoke void @_RNvNtCskADBYZwJmSU_4core9panicking9panic_fmt(ptr noundef nonnull @alloc_37f62a15fae368a2423b3a16c75adcc9, ptr noundef nonnull inttoptr (i64 3 to ptr), ptr noalias nofree noundef readonly align 8 captures(address, read_provenance) dereferenceable(24) @alloc_f4d302337a3abcf1f4238b174f3f0242) #8
          to label %unreachable unwind label %terminate

bb2:                                              ; preds = %start
  ret void

terminate:                                        ; preds = %bb1
  %1 = landingpad { ptr, i32 }
          filter [0 x ptr] zeroinitializer
  tail call void @_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind() #9
  unreachable

unreachable:                                      ; preds = %bb1
  unreachable
}

; Function Attrs: nounwind nonlazybind uwtable
declare noundef range(i32 0, 10) i32 @rust_eh_personality(i32 noundef, i32 noundef, i64 noundef, ptr noundef, ptr noundef) unnamed_addr #0

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(ptr captures(none)) #2

; Function Attrs: cold minsize noinline noreturn nounwind nonlazybind optsize uwtable
declare void @_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind() unnamed_addr #3

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_rot(i32 noundef, ptr noundef, i64 noundef, double noundef) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_qfree(ptr noundef) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare noundef ptr @__bennett_qalloc(i64 noundef, i64 noundef) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_gate2(i32 noundef, ptr noundef, i64 noundef, ptr noundef, i64 noundef) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare noundef zeroext i1 @__bennett_measure(ptr noundef, i64 noundef) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef nonnull, i64 noundef, ptr noundef) unnamed_addr #0

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(ptr captures(none)) #2

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_ctrl_v(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ...) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_adj(ptr noundef nonnull, ptr noundef) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_compute(ptr noundef nonnull, ptr noundef nonnull, ptr noundef) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_reversible(ptr noundef nonnull, i64 noundef, ptr noundef) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_inplace(ptr noundef nonnull, ptr noundef nonnull, ptr noundef) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare noundef ptr @__bennett_qborrow(i64 noundef, i64 noundef) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_qload(ptr noundef, ptr noundef, ptr noundef) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_qstore(ptr noundef, ptr noundef, ptr noundef) unnamed_addr #0

; Function Attrs: cold noinline noreturn nonlazybind uwtable
declare void @_RNvNtCskADBYZwJmSU_4core9panicking9panic_fmt(ptr noundef nonnull, ptr noundef nonnull, ptr noalias nofree noundef readonly align 8 captures(address, read_provenance) dereferenceable(24)) unnamed_addr #4

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: readwrite)
declare void @llvm.experimental.noalias.scope.decl(metadata) #5

attributes #0 = { nounwind nonlazybind uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #1 = { noinline nounwind nonlazybind uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #2 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #3 = { cold minsize noinline noreturn nounwind nonlazybind optsize uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #4 = { cold noinline noreturn nonlazybind uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #5 = { nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: readwrite) }
attributes #6 = { nounwind }
attributes #7 = { noinline nounwind }
attributes #8 = { noreturn }
attributes #9 = { cold noreturn nounwind }

!llvm.module.flags = !{!3, !4, !5}
!llvm.ident = !{!6}

!0 = !{i64 9118137893752966836}
!1 = !{i64 -7355899746778665416}
!2 = !{i64 -5683099207853529922}
!3 = !{i32 8, !"PIC Level", i32 2}
!4 = !{i32 2, !"RtLibUseGOT", i32 1}
!5 = !{i32 7, !"uwtable", i32 2}
!6 = !{!"rustc version 1.99.1 (58cf8f9c3 2026-10-13)"}
!7 = !{i64 -8428455889319306347}
!8 = !{!9}
!9 = distinct !{!9, !10, !"_RNCNvCsaOknTnIz6g7_12bennett_emit10case_entry0B3_: %e"}
!10 = distinct !{!10, !"_RNCNvCsaOknTnIz6g7_12bennett_emit10case_entry0B3_"}
!11 = !{}
!12 = !{i64 -2031306674162102066}
!13 = !{i64 7409136921373146039}
!14 = !{i64 829468968551850661}
!15 = !{!16, !18}
!16 = distinct !{!16, !17, !"_RNvXCsaOknTnIz6g7_12bennett_emitNtB2_5GuardNtNtNtCskADBYZwJmSU_4core3ops4drop4Drop4drop: %self"}
!17 = distinct !{!17, !"_RNvXCsaOknTnIz6g7_12bennett_emitNtB2_5GuardNtNtNtCskADBYZwJmSU_4core3ops4drop4Drop4drop"}
!18 = distinct !{!18, !19, !"_RINvNtCskADBYZwJmSU_4core3ptr9drop_glueNtCsaOknTnIz6g7_12bennett_emit5GuardEBD_: %_1"}
!19 = distinct !{!19, !"_RINvNtCskADBYZwJmSU_4core3ptr9drop_glueNtCsaOknTnIz6g7_12bennett_emit5GuardEBD_"}
!20 = !{i64 7779443428098473721}
!21 = !{!"branch_weights", !"expected", i32 1, i32 2000}

^0 = module: (path: "bennett_emit.O2.bc", hash: (2383113678, 1119568479, 233772443, 1752707424, 4188247665))
^1 = gv: (name: "case_entry", summaries: (function: (module: ^0, flags: (linkage: external, visibility: default, notEligibleToImport: 0, live: 0, dsoLocal: 0, canAutoHide: 0, importType: definition, noRenameOnPromotion: 0), insts: 57, funcFlags: (readNone: 0, readOnly: 0, noRecurse: 0, returnDoesNotAlias: 0, noInline: 0, alwaysInline: 0, noUnwind: 1, mayThrow: 0, hasUnknownCall: 0, mustBeUnreachable: 0), calls: ((callee: ^7, tail: 1), (callee: ^3, tail: 1), (callee: ^11, tail: 1), (callee: ^20, tail: 1), (callee: ^5, tail: 1), (callee: ^27), (callee: ^4), (callee: ^28), (callee: ^21), (callee: ^29), (callee: ^10), (callee: ^17), (callee: ^9), (callee: ^12), (callee: ^14), (callee: ^26)), refs: (^24, ^25, ^18)))) ; guid = 829468968551850661
^2 = gv: (name: "_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind") ; guid = 931455048851401831
^3 = gv: (name: "__bennett_gate") ; guid = 2982123004906011917
^4 = gv: (name: "__bennett_ctrl_v") ; guid = 3388239159881652307
^5 = gv: (name: "__bennett_measure") ; guid = 3968391300744443354
^6 = gv: (name: "_RNvNtCskADBYZwJmSU_4core9panicking9panic_fmt") ; guid = 4033766315225999373
^7 = gv: (name: "__bennett_qalloc") ; guid = 4673891782026730886
^8 = gv: (name: "llvm.lifetime.start.p0") ; guid = 4736283418132453162
^9 = gv: (name: "__bennett_qload") ; guid = 5523751926362201190
^10 = gv: (name: "__bennett_inplace") ; guid = 5689239253225716227
^11 = gv: (name: "__bennett_rot") ; guid = 6169953353981470639
^12 = gv: (name: "__bennett_qstore") ; guid = 7240128825523100880
^13 = gv: (name: "_RNvXCsaOknTnIz6g7_12bennett_emitNtB2_5GuardNtNtNtCskADBYZwJmSU_4core3ops4drop4Drop4drop", summaries: (function: (module: ^0, flags: (linkage: external, visibility: default, notEligibleToImport: 0, live: 0, dsoLocal: 0, canAutoHide: 0, importType: definition, noRenameOnPromotion: 0), insts: 3, funcFlags: (readNone: 0, readOnly: 0, noRecurse: 0, returnDoesNotAlias: 0, noInline: 0, alwaysInline: 0, noUnwind: 1, mayThrow: 0, hasUnknownCall: 0, mustBeUnreachable: 0), calls: ((callee: ^26, tail: 1))))) ; guid = 7409136921373146039
^14 = gv: (name: "rt_may_unwind", summaries: (function: (module: ^0, flags: (linkage: external, visibility: default, notEligibleToImport: 0, live: 0, dsoLocal: 0, canAutoHide: 0, importType: definition, noRenameOnPromotion: 0), insts: 8, funcFlags: (readNone: 0, readOnly: 0, noRecurse: 0, returnDoesNotAlias: 0, noInline: 1, alwaysInline: 0, noUnwind: 1, mayThrow: 0, hasUnknownCall: 0, mustBeUnreachable: 0), calls: ((callee: ^6), (callee: ^2, tail: 1)), refs: (^24, ^19, ^22)))) ; guid = 7779443428098473721
^15 = gv: (name: "llvm.experimental.noalias.scope.decl") ; guid = 8095543252637616711
^16 = gv: (name: "alloc_1962bf4fe486936f0f5554c0adc669f6", summaries: (variable: (module: ^0, flags: (linkage: private, visibility: default, notEligibleToImport: 0, live: 0, dsoLocal: 1, canAutoHide: 0, importType: definition, noRenameOnPromotion: 0), varFlags: (readonly: 1, writeonly: 0, constant: 1)))) ; guid = 9118137893752966836
^17 = gv: (name: "__bennett_qborrow") ; guid = 9491372177710512436
^18 = gv: (name: "_RINvCsaOknTnIz6g7_12bennett_emit5trampNCNvB2_10case_entry0EB2_", summaries: (function: (module: ^0, flags: (linkage: internal, visibility: default, notEligibleToImport: 0, live: 0, dsoLocal: 1, canAutoHide: 0, importType: definition, noRenameOnPromotion: 0), insts: 6, funcFlags: (readNone: 0, readOnly: 0, noRecurse: 0, returnDoesNotAlias: 0, noInline: 0, alwaysInline: 0, noUnwind: 1, mayThrow: 0, hasUnknownCall: 0, mustBeUnreachable: 0), calls: ((callee: ^3, tail: 1)), refs: (^24)))) ; guid = 10018288184390245269
^19 = gv: (name: "alloc_37f62a15fae368a2423b3a16c75adcc9", summaries: (variable: (module: ^0, flags: (linkage: private, visibility: default, notEligibleToImport: 0, live: 0, dsoLocal: 1, canAutoHide: 0, importType: definition, noRenameOnPromotion: 0), varFlags: (readonly: 1, writeonly: 0, constant: 1)))) ; guid = 11090844326930886200
^20 = gv: (name: "__bennett_gate2") ; guid = 11316789583050174531
^21 = gv: (name: "__bennett_compute") ; guid = 11359642307109096958
^22 = gv: (name: "alloc_f4d302337a3abcf1f4238b174f3f0242", summaries: (variable: (module: ^0, flags: (linkage: private, visibility: default, notEligibleToImport: 0, live: 0, dsoLocal: 1, canAutoHide: 0, importType: definition, noRenameOnPromotion: 0), varFlags: (readonly: 1, writeonly: 0, constant: 1), refs: (^16)))) ; guid = 12763644865856021694
^23 = gv: (name: "llvm.lifetime.end.p0") ; guid = 13244677477227836793
^24 = gv: (name: "rust_eh_personality") ; guid = 14807195490537628141
^25 = gv: (name: "_RNvCsaOknTnIz6g7_12bennett_emit4body", summaries: (function: (module: ^0, flags: (linkage: internal, visibility: default, notEligibleToImport: 0, live: 0, dsoLocal: 1, canAutoHide: 0, importType: definition, noRenameOnPromotion: 0), insts: 10, funcFlags: (readNone: 0, readOnly: 0, noRecurse: 0, returnDoesNotAlias: 0, noInline: 0, alwaysInline: 0, noUnwind: 1, mayThrow: 0, hasUnknownCall: 0, mustBeUnreachable: 0), calls: ((callee: ^11, tail: 1), (callee: ^3, tail: 1))))) ; guid = 16415437399547449550
^26 = gv: (name: "__bennett_qfree") ; guid = 16633130219932291175
^27 = gv: (name: "__bennett_ctrl") ; guid = 16800917137780716501
^28 = gv: (name: "__bennett_adj") ; guid = 17297851703929373874
^29 = gv: (name: "__bennett_reversible") ; guid = 17933274057403866412
^30 = blockcount: 0
