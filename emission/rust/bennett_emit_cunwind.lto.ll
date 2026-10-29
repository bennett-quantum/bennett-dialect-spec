; ModuleID = 'bennett_emit_cunwind.lto.bc'
source_filename = "bennett_emit_cunwind.8b1da32fb3f6aaf6-cgu.0"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@alloc_69f962397eeb0ba4e8a8d674a4b40f1a = private unnamed_addr constant [24 x i8] c"bennett_emit_cunwind.rs\00", align 1, !guid !0
@alloc_37f62a15fae368a2423b3a16c75adcc9 = private unnamed_addr constant [1 x i8] c"x", align 1, !guid !1
@alloc_362f4c346d0359ed82cee8d63dffe8a9 = private unnamed_addr constant <{ ptr, [16 x i8] }> <{ ptr @alloc_69f962397eeb0ba4e8a8d674a4b40f1a, [16 x i8] c"\17\00\00\00\00\00\00\00/\00\00\008\00\00\00" }>, align 8, !guid !2

; Function Attrs: nounwind nonlazybind uwtable
define internal void @_RINvCsbWvCnYHbl8o_20bennett_emit_cunwind5trampNCNvB2_10case_entry0EB2_(ptr nofree noundef readonly captures(none) %p) unnamed_addr #0 personality ptr @rust_eh_personality !guid !7 {
start:
  %_3.i = load ptr, ptr %p, align 8, !alias.scope !8, !noundef !11
  %0 = getelementptr inbounds nuw i8, ptr %p, i64 8
  %_4.i = load i64, ptr %0, align 8, !alias.scope !8, !noundef !11
  invoke void @__bennett_gate(i32 noundef 5, ptr noundef %_3.i, i64 noundef %_4.i)
          to label %bb2 unwind label %cleanup

cleanup:                                          ; preds = %start
  %1 = landingpad { ptr, i32 }
          cleanup
  tail call void @_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind() #7
  unreachable

bb2:                                              ; preds = %start
  ret void
}

; Function Attrs: nonlazybind uwtable
define internal fastcc void @_RINvNtCskADBYZwJmSU_4core3ptr9drop_glueNtCsbWvCnYHbl8o_20bennett_emit_cunwind5GuardEBD_(ptr noalias nofree noundef nonnull readonly align 8 captures(none) dereferenceable(8) %_1) unnamed_addr #1 !guid !12 {
start:
  tail call void @llvm.experimental.noalias.scope.decl(metadata !13)
  %_2.i = load ptr, ptr %_1, align 8, !alias.scope !13, !noundef !11
  tail call void @__bennett_qfree(ptr noundef %_2.i), !noalias !13
  ret void
}

; Function Attrs: nounwind nonlazybind uwtable
define internal void @_RNvCsbWvCnYHbl8o_20bennett_emit_cunwind4body(ptr nofree noundef readonly captures(none) %p) unnamed_addr #0 personality ptr @rust_eh_personality !guid !16 {
start:
  %_4 = load ptr, ptr %p, align 8, !noundef !11
  %0 = getelementptr inbounds nuw i8, ptr %p, i64 8
  %_5 = load i64, ptr %0, align 8, !noundef !11
  %1 = getelementptr inbounds nuw i8, ptr %p, i64 16
  %_6 = load double, ptr %1, align 8, !noundef !11
  invoke void @__bennett_rot(i32 noundef 1, ptr noundef %_4, i64 noundef %_5, double noundef %_6)
          to label %bb1 unwind label %terminate

terminate:                                        ; preds = %bb1, %start
  %2 = landingpad { ptr, i32 }
          filter [0 x ptr] zeroinitializer
  tail call void @_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind() #8
  unreachable

bb1:                                              ; preds = %start
  %_8 = load ptr, ptr %p, align 8, !noundef !11
  %_9 = load i64, ptr %0, align 8, !noundef !11
  invoke void @__bennett_gate(i32 noundef 2, ptr noundef %_8, i64 noundef %_9)
          to label %bb2 unwind label %terminate

bb2:                                              ; preds = %bb1
  ret void
}

; Function Attrs: nonlazybind uwtable
define void @_RNvXCsbWvCnYHbl8o_20bennett_emit_cunwindNtB2_5GuardNtNtNtCskADBYZwJmSU_4core3ops4drop4Drop4drop(ptr noalias nofree noundef readonly align 8 captures(none) dereferenceable(8) %self) unnamed_addr #1 !guid !17 {
start:
  %_2 = load ptr, ptr %self, align 8, !noundef !11
  tail call void @__bennett_qfree(ptr noundef %_2)
  ret void
}

; Function Attrs: nounwind nonlazybind uwtable
define noundef range(i64 0, 2) i64 @case_entry(i64 noundef %x) unnamed_addr #0 personality ptr @rust_eh_personality !guid !18 {
start:
  %g = alloca [8 x i8], align 8
  %tab = alloca [32 x i8], align 8
  %e = alloca [24 x i8], align 8
  %h = invoke noundef ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 4)
          to label %bb1 unwind label %terminate.loopexit.split-lp.loopexit.split-lp

terminate.loopexit.split-lp.loopexit.split-lp:    ; preds = %bb14.3, %bb37, %bb38, %bb27, %bb21, %bb20, %bb19, %bb18, %bb17, %bb16, %bb10, %bb6, %bb8, %bb4, %bb3, %bb2, %bb1, %start
  %lpad.loopexit.split-lp11 = landingpad { ptr, i32 }
          filter [0 x ptr] zeroinitializer
  call void @_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind() #8
  unreachable

bb1:                                              ; preds = %start
  invoke void @__bennett_gate(i32 noundef 1, ptr noundef %h, i64 noundef 0)
          to label %bb2 unwind label %terminate.loopexit.split-lp.loopexit.split-lp

bb2:                                              ; preds = %bb1
  %_5 = uitofp i64 %x to double
  %theta = fmul nnan double %_5, 1.250000e-01
  invoke void @__bennett_rot(i32 noundef 3, ptr noundef %h, i64 noundef 1, double noundef %theta)
          to label %bb3 unwind label %terminate.loopexit.split-lp.loopexit.split-lp

bb3:                                              ; preds = %bb2
  invoke void @__bennett_gate2(i32 noundef 4, ptr noundef %h, i64 noundef 0, ptr noundef %h, i64 noundef 1)
          to label %bb4 unwind label %terminate.loopexit.split-lp.loopexit.split-lp

bb4:                                              ; preds = %bb3
  %_8 = invoke noundef zeroext i1 @__bennett_measure(ptr noundef %h, i64 noundef 0)
          to label %bb5 unwind label %terminate.loopexit.split-lp.loopexit.split-lp

bb5:                                              ; preds = %bb4
  br i1 %_8, label %bb6, label %bb8

bb8:                                              ; preds = %bb6, %bb5
  %r.sroa.0.0 = phi i64 [ 0, %bb5 ], [ 1, %bb6 ]
  call void @llvm.lifetime.start.p0(ptr nonnull %e)
  store ptr %h, ptr %e, align 8
  %0 = getelementptr inbounds nuw i8, ptr %e, i64 8
  store i64 3, ptr %0, align 8
  %1 = getelementptr inbounds nuw i8, ptr %e, i64 16
  store double %theta, ptr %1, align 8
  invoke void @__bennett_ctrl(ptr noundef %h, i64 noundef 0, ptr noundef nonnull @_RNvCsbWvCnYHbl8o_20bennett_emit_cunwind4body, i64 noundef 8, ptr noundef nonnull %e)
          to label %bb10 unwind label %terminate.loopexit.split-lp.loopexit.split-lp

bb6:                                              ; preds = %bb5
  invoke void @__bennett_gate(i32 noundef 2, ptr noundef %h, i64 noundef 2)
          to label %bb8 unwind label %terminate.loopexit.split-lp.loopexit.split-lp

bb10:                                             ; preds = %bb8
  invoke void @__bennett_ctrl(ptr noundef %h, i64 noundef 1, ptr noundef nonnull @_RINvCsbWvCnYHbl8o_20bennett_emit_cunwind5trampNCNvB2_10case_entry0EB2_, i64 noundef 8, ptr noundef nonnull %e)
          to label %bb11 unwind label %terminate.loopexit.split-lp.loopexit.split-lp

bb11:                                             ; preds = %bb10
  call void @llvm.lifetime.start.p0(ptr nonnull %tab)
  %_22 = invoke noundef ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1)
          to label %bb14 unwind label %terminate6

bb16:                                             ; preds = %bb14.3
  invoke void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr noundef %h, i64 noundef 0, ptr noundef nonnull @_RNvCsbWvCnYHbl8o_20bennett_emit_cunwind4body, i64 noundef 8, i32 noundef 1, double noundef 2.500000e+00, ptr noundef %h)
          to label %bb17 unwind label %terminate.loopexit.split-lp.loopexit.split-lp

bb17:                                             ; preds = %bb16
  invoke void @__bennett_adj(ptr noundef nonnull @_RNvCsbWvCnYHbl8o_20bennett_emit_cunwind4body, ptr noundef nonnull %e)
          to label %bb18 unwind label %terminate.loopexit.split-lp.loopexit.split-lp

bb18:                                             ; preds = %bb17
  invoke void @__bennett_compute(ptr noundef nonnull @_RNvCsbWvCnYHbl8o_20bennett_emit_cunwind4body, ptr noundef nonnull @_RNvCsbWvCnYHbl8o_20bennett_emit_cunwind4body, ptr noundef nonnull %e)
          to label %bb19 unwind label %terminate.loopexit.split-lp.loopexit.split-lp

bb19:                                             ; preds = %bb18
  invoke void @__bennett_reversible(ptr noundef nonnull @_RNvCsbWvCnYHbl8o_20bennett_emit_cunwind4body, i64 noundef 3, ptr noundef nonnull %e)
          to label %bb20 unwind label %terminate.loopexit.split-lp.loopexit.split-lp

bb20:                                             ; preds = %bb19
  invoke void @__bennett_inplace(ptr noundef nonnull @_RNvCsbWvCnYHbl8o_20bennett_emit_cunwind4body, ptr noundef nonnull @_RNvCsbWvCnYHbl8o_20bennett_emit_cunwind4body, ptr noundef nonnull %e)
          to label %bb21 unwind label %terminate.loopexit.split-lp.loopexit.split-lp

bb21:                                             ; preds = %bb20
  call void @llvm.lifetime.start.p0(ptr nonnull %g)
  %_51 = invoke noundef ptr @__bennett_qborrow(i64 noundef 0, i64 noundef 1)
          to label %bb22 unwind label %terminate.loopexit.split-lp.loopexit.split-lp

bb22:                                             ; preds = %bb21
  store ptr %_51, ptr %g, align 8
  invoke void @__bennett_qload(ptr noundef %_51, ptr noundef %h, ptr noundef %_22)
          to label %bb23 unwind label %cleanup

cleanup:                                          ; preds = %bb24, %bb23, %bb22
  %2 = landingpad { ptr, i32 }
          cleanup
  invoke fastcc void @_RINvNtCskADBYZwJmSU_4core3ptr9drop_glueNtCsbWvCnYHbl8o_20bennett_emit_cunwind5GuardEBD_(ptr noalias nofree noundef align 8 dereferenceable(8) %g) #9
          to label %bb34 unwind label %terminate4

bb23:                                             ; preds = %bb22
  invoke void @__bennett_qstore(ptr noundef %h, ptr noundef %_22.1, ptr noundef %_51)
          to label %bb24 unwind label %cleanup

bb24:                                             ; preds = %bb23
  call void @rt_may_unwind(i64 noundef %x) #10
  invoke void @__bennett_gate(i32 noundef 6, ptr noundef %_51, i64 noundef 0)
          to label %bb26 unwind label %cleanup

bb26:                                             ; preds = %bb24
  invoke void @__bennett_qfree(ptr noundef %_51)
          to label %bb27 unwind label %cleanup2

bb34:                                             ; preds = %cleanup2, %cleanup
  call void @_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind() #7
  unreachable

cleanup2:                                         ; preds = %bb26
  %3 = landingpad { ptr, i32 }
          cleanup
  br label %bb34

bb27:                                             ; preds = %bb26
  call void @llvm.lifetime.end.p0(ptr nonnull %g)
  invoke void @__bennett_qfree(ptr noundef %h)
          to label %bb29 unwind label %terminate.loopexit.split-lp.loopexit.split-lp

bb29:                                             ; preds = %bb37, %bb27
  %iter1.sroa.0.0 = phi i64 [ %4, %bb37 ], [ 0, %bb27 ]
  %exitcond.not = icmp eq i64 %iter1.sroa.0.0, 4
  br i1 %exitcond.not, label %bb38, label %bb37

bb38:                                             ; preds = %bb29
  invoke void @__bennett_qfree(ptr noundef %h)
          to label %bb32 unwind label %terminate.loopexit.split-lp.loopexit.split-lp

bb37:                                             ; preds = %bb29
  %4 = add nuw nsw i64 %iter1.sroa.0.0, 1
  %5 = getelementptr inbounds nuw [8 x i8], ptr %tab, i64 %iter1.sroa.0.0
  %_65 = load ptr, ptr %5, align 8, !noundef !11
  invoke void @__bennett_qfree(ptr noundef %_65)
          to label %bb29 unwind label %terminate.loopexit.split-lp.loopexit.split-lp

bb32:                                             ; preds = %bb38
  call void @llvm.lifetime.end.p0(ptr nonnull %tab)
  call void @llvm.lifetime.end.p0(ptr nonnull %e)
  ret i64 %r.sroa.0.0

terminate4:                                       ; preds = %cleanup
  %6 = landingpad { ptr, i32 }
          filter [0 x ptr] zeroinitializer
  call void @_RNvNtCskADBYZwJmSU_4core9panicking16panic_in_cleanup() #8
  unreachable

terminate6:                                       ; preds = %bb14.2, %bb14.1, %bb14, %bb11
  %7 = landingpad { ptr, i32 }
          filter [0 x ptr] zeroinitializer
  call void @_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind() #8
  unreachable

bb14:                                             ; preds = %bb11
  store ptr %_22, ptr %tab, align 8
  %_22.1 = invoke noundef ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1)
          to label %bb14.1 unwind label %terminate6

bb14.1:                                           ; preds = %bb14
  %8 = getelementptr inbounds nuw i8, ptr %tab, i64 8
  store ptr %_22.1, ptr %8, align 8
  %_22.2 = invoke noundef ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1)
          to label %bb14.2 unwind label %terminate6

bb14.2:                                           ; preds = %bb14.1
  %9 = getelementptr inbounds nuw i8, ptr %tab, i64 16
  store ptr %_22.2, ptr %9, align 8
  %_22.3 = invoke noundef ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1)
          to label %bb14.3 unwind label %terminate6

bb14.3:                                           ; preds = %bb14.2
  %10 = getelementptr inbounds nuw i8, ptr %tab, i64 24
  store ptr %_22.3, ptr %10, align 8
  %_27 = and i64 %x, 3
  %11 = getelementptr inbounds nuw [8 x i8], ptr %tab, i64 %_27
  %_25 = load ptr, ptr %11, align 8, !noundef !11
  invoke void @__bennett_gate(i32 noundef 1, ptr noundef %_25, i64 noundef 0)
          to label %bb16 unwind label %terminate.loopexit.split-lp.loopexit.split-lp
}

; Function Attrs: noinline nounwind nonlazybind uwtable
define void @rt_may_unwind(i64 noundef %x) unnamed_addr #2 personality ptr @rust_eh_personality !guid !19 {
start:
  %0 = icmp eq i64 %x, 77
  br i1 %0, label %bb1, label %bb2, !prof !20

bb1:                                              ; preds = %start
  invoke void @_RNvNtCskADBYZwJmSU_4core9panicking9panic_fmt(ptr noundef nonnull @alloc_37f62a15fae368a2423b3a16c75adcc9, ptr noundef nonnull inttoptr (i64 3 to ptr), ptr noalias nofree noundef readonly align 8 captures(address, read_provenance) dereferenceable(24) @alloc_362f4c346d0359ed82cee8d63dffe8a9) #11
          to label %unreachable unwind label %terminate

bb2:                                              ; preds = %start
  ret void

terminate:                                        ; preds = %bb1
  %1 = landingpad { ptr, i32 }
          filter [0 x ptr] zeroinitializer
  tail call void @_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind() #8
  unreachable

unreachable:                                      ; preds = %bb1
  unreachable
}

; Function Attrs: nounwind nonlazybind uwtable
declare noundef range(i32 0, 10) i32 @rust_eh_personality(i32 noundef, i32 noundef, i64 noundef, ptr noundef, ptr noundef) unnamed_addr #0

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(ptr captures(none)) #3

; Function Attrs: cold minsize noinline noreturn nounwind nonlazybind optsize uwtable
declare void @_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind() unnamed_addr #4

; Function Attrs: nonlazybind uwtable
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef) unnamed_addr #1

; Function Attrs: nonlazybind uwtable
declare void @__bennett_rot(i32 noundef, ptr noundef, i64 noundef, double noundef) unnamed_addr #1

; Function Attrs: nonlazybind uwtable
declare void @__bennett_qfree(ptr noundef) unnamed_addr #1

; Function Attrs: nonlazybind uwtable
declare noundef ptr @__bennett_qalloc(i64 noundef, i64 noundef) unnamed_addr #1

; Function Attrs: nonlazybind uwtable
declare void @__bennett_gate2(i32 noundef, ptr noundef, i64 noundef, ptr noundef, i64 noundef) unnamed_addr #1

; Function Attrs: nonlazybind uwtable
declare noundef zeroext i1 @__bennett_measure(ptr noundef, i64 noundef) unnamed_addr #1

; Function Attrs: nonlazybind uwtable
declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef nonnull, i64 noundef, ptr noundef) unnamed_addr #1

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(ptr captures(none)) #3

; Function Attrs: nonlazybind uwtable
declare void @__bennett_ctrl_v(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ...) unnamed_addr #1

; Function Attrs: nonlazybind uwtable
declare void @__bennett_adj(ptr noundef nonnull, ptr noundef) unnamed_addr #1

; Function Attrs: nonlazybind uwtable
declare void @__bennett_compute(ptr noundef nonnull, ptr noundef nonnull, ptr noundef) unnamed_addr #1

; Function Attrs: nonlazybind uwtable
declare void @__bennett_reversible(ptr noundef nonnull, i64 noundef, ptr noundef) unnamed_addr #1

; Function Attrs: nonlazybind uwtable
declare void @__bennett_inplace(ptr noundef nonnull, ptr noundef nonnull, ptr noundef) unnamed_addr #1

; Function Attrs: nonlazybind uwtable
declare noundef ptr @__bennett_qborrow(i64 noundef, i64 noundef) unnamed_addr #1

; Function Attrs: nonlazybind uwtable
declare void @__bennett_qload(ptr noundef, ptr noundef, ptr noundef) unnamed_addr #1

; Function Attrs: nonlazybind uwtable
declare void @__bennett_qstore(ptr noundef, ptr noundef, ptr noundef) unnamed_addr #1

; Function Attrs: cold minsize noinline noreturn nounwind nonlazybind optsize uwtable
declare void @_RNvNtCskADBYZwJmSU_4core9panicking16panic_in_cleanup() unnamed_addr #4

; Function Attrs: cold noinline noreturn nonlazybind uwtable
declare void @_RNvNtCskADBYZwJmSU_4core9panicking9panic_fmt(ptr noundef nonnull, ptr noundef nonnull, ptr noalias nofree noundef readonly align 8 captures(address, read_provenance) dereferenceable(24)) unnamed_addr #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: readwrite)
declare void @llvm.experimental.noalias.scope.decl(metadata) #6

attributes #0 = { nounwind nonlazybind uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #1 = { nonlazybind uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #2 = { noinline nounwind nonlazybind uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #3 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #4 = { cold minsize noinline noreturn nounwind nonlazybind optsize uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #5 = { cold noinline noreturn nonlazybind uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: readwrite) }
attributes #7 = { cold noinline noreturn nounwind }
attributes #8 = { cold noreturn nounwind }
attributes #9 = { cold }
attributes #10 = { noinline nounwind }
attributes #11 = { noreturn }

!llvm.module.flags = !{!3, !4, !5}
!llvm.ident = !{!6}

!0 = !{i64 4981177886773023490}
!1 = !{i64 6215965559920105160}
!2 = !{i64 5619148338520634717}
!3 = !{i32 8, !"PIC Level", i32 2}
!4 = !{i32 2, !"RtLibUseGOT", i32 1}
!5 = !{i32 7, !"uwtable", i32 2}
!6 = !{!"rustc version 1.99.1 (58cf8f9c3 2026-10-13)"}
!7 = !{i64 999348089483641093}
!8 = !{!9}
!9 = distinct !{!9, !10, !"_RNCNvCsbWvCnYHbl8o_20bennett_emit_cunwind10case_entry0B3_: %e"}
!10 = distinct !{!10, !"_RNCNvCsbWvCnYHbl8o_20bennett_emit_cunwind10case_entry0B3_"}
!11 = !{}
!12 = !{i64 7766224934977739169}
!13 = !{!14}
!14 = distinct !{!14, !15, !"_RNvXCsbWvCnYHbl8o_20bennett_emit_cunwindNtB2_5GuardNtNtNtCskADBYZwJmSU_4core3ops4drop4Drop4drop: %self"}
!15 = distinct !{!15, !"_RNvXCsbWvCnYHbl8o_20bennett_emit_cunwindNtB2_5GuardNtNtNtCskADBYZwJmSU_4core3ops4drop4Drop4drop"}
!16 = !{i64 -4072427864844824995}
!17 = !{i64 -5130074176868323965}
!18 = !{i64 829468968551850661}
!19 = !{i64 7779443428098473721}
!20 = !{!"branch_weights", !"expected", i32 1, i32 2000}

^0 = module: (path: "bennett_emit_cunwind.lto.bc", hash: (2149591034, 1549936847, 229676523, 1713137088, 2653166464))
^1 = gv: (name: "case_entry", summaries: (function: (module: ^0, flags: (linkage: external, visibility: default, notEligibleToImport: 0, live: 0, dsoLocal: 0, canAutoHide: 0, importType: definition, noRenameOnPromotion: 0), insts: 78, funcFlags: (readNone: 0, readOnly: 0, noRecurse: 0, returnDoesNotAlias: 0, noInline: 0, alwaysInline: 0, noUnwind: 1, mayThrow: 0, hasUnknownCall: 0, mustBeUnreachable: 0), calls: ((callee: ^8), (callee: ^2), (callee: ^4), (callee: ^14), (callee: ^22), (callee: ^6), (callee: ^29), (callee: ^5), (callee: ^30), (callee: ^23), (callee: ^31), (callee: ^13), (callee: ^21), (callee: ^11), (callee: ^17), (callee: ^16), (callee: ^18), (callee: ^28), (callee: ^20)), refs: (^27, ^26, ^3)))) ; guid = 829468968551850661
^2 = gv: (name: "_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind") ; guid = 931455048851401831
^3 = gv: (name: "_RINvCsbWvCnYHbl8o_20bennett_emit_cunwind5trampNCNvB2_10case_entry0EB2_", summaries: (function: (module: ^0, flags: (linkage: internal, visibility: default, notEligibleToImport: 0, live: 0, dsoLocal: 1, canAutoHide: 0, importType: definition, noRenameOnPromotion: 0), insts: 8, funcFlags: (readNone: 0, readOnly: 0, noRecurse: 0, returnDoesNotAlias: 0, noInline: 0, alwaysInline: 0, noUnwind: 1, mayThrow: 0, hasUnknownCall: 0, mustBeUnreachable: 0), calls: ((callee: ^4), (callee: ^2, tail: 1)), refs: (^27)))) ; guid = 999348089483641093
^4 = gv: (name: "__bennett_gate") ; guid = 2982123004906011917
^5 = gv: (name: "__bennett_ctrl_v") ; guid = 3388239159881652307
^6 = gv: (name: "__bennett_measure") ; guid = 3968391300744443354
^7 = gv: (name: "_RNvNtCskADBYZwJmSU_4core9panicking9panic_fmt") ; guid = 4033766315225999373
^8 = gv: (name: "__bennett_qalloc") ; guid = 4673891782026730886
^9 = gv: (name: "llvm.lifetime.start.p0") ; guid = 4736283418132453162
^10 = gv: (name: "alloc_69f962397eeb0ba4e8a8d674a4b40f1a", summaries: (variable: (module: ^0, flags: (linkage: private, visibility: default, notEligibleToImport: 0, live: 0, dsoLocal: 1, canAutoHide: 0, importType: definition, noRenameOnPromotion: 0), varFlags: (readonly: 1, writeonly: 0, constant: 1)))) ; guid = 4981177886773023490
^11 = gv: (name: "__bennett_qload") ; guid = 5523751926362201190
^12 = gv: (name: "alloc_362f4c346d0359ed82cee8d63dffe8a9", summaries: (variable: (module: ^0, flags: (linkage: private, visibility: default, notEligibleToImport: 0, live: 0, dsoLocal: 1, canAutoHide: 0, importType: definition, noRenameOnPromotion: 0), varFlags: (readonly: 1, writeonly: 0, constant: 1), refs: (^10)))) ; guid = 5619148338520634717
^13 = gv: (name: "__bennett_inplace") ; guid = 5689239253225716227
^14 = gv: (name: "__bennett_rot") ; guid = 6169953353981470639
^15 = gv: (name: "alloc_37f62a15fae368a2423b3a16c75adcc9", summaries: (variable: (module: ^0, flags: (linkage: private, visibility: default, notEligibleToImport: 0, live: 0, dsoLocal: 1, canAutoHide: 0, importType: definition, noRenameOnPromotion: 0), varFlags: (readonly: 1, writeonly: 0, constant: 1)))) ; guid = 6215965559920105160
^16 = gv: (name: "__bennett_qstore") ; guid = 7240128825523100880
^17 = gv: (name: "_RINvNtCskADBYZwJmSU_4core3ptr9drop_glueNtCsbWvCnYHbl8o_20bennett_emit_cunwind5GuardEBD_", summaries: (function: (module: ^0, flags: (linkage: internal, visibility: default, notEligibleToImport: 0, live: 0, dsoLocal: 1, canAutoHide: 0, importType: definition, noRenameOnPromotion: 0), insts: 4, calls: ((callee: ^28, tail: 1))))) ; guid = 7766224934977739169
^18 = gv: (name: "rt_may_unwind", summaries: (function: (module: ^0, flags: (linkage: external, visibility: default, notEligibleToImport: 0, live: 0, dsoLocal: 0, canAutoHide: 0, importType: definition, noRenameOnPromotion: 0), insts: 8, funcFlags: (readNone: 0, readOnly: 0, noRecurse: 0, returnDoesNotAlias: 0, noInline: 1, alwaysInline: 0, noUnwind: 1, mayThrow: 0, hasUnknownCall: 0, mustBeUnreachable: 0), calls: ((callee: ^7), (callee: ^2, tail: 1)), refs: (^27, ^15, ^12)))) ; guid = 7779443428098473721
^19 = gv: (name: "llvm.experimental.noalias.scope.decl") ; guid = 8095543252637616711
^20 = gv: (name: "_RNvNtCskADBYZwJmSU_4core9panicking16panic_in_cleanup") ; guid = 9245626366280320556
^21 = gv: (name: "__bennett_qborrow") ; guid = 9491372177710512436
^22 = gv: (name: "__bennett_gate2") ; guid = 11316789583050174531
^23 = gv: (name: "__bennett_compute") ; guid = 11359642307109096958
^24 = gv: (name: "llvm.lifetime.end.p0") ; guid = 13244677477227836793
^25 = gv: (name: "_RNvXCsbWvCnYHbl8o_20bennett_emit_cunwindNtB2_5GuardNtNtNtCskADBYZwJmSU_4core3ops4drop4Drop4drop", summaries: (function: (module: ^0, flags: (linkage: external, visibility: default, notEligibleToImport: 0, live: 0, dsoLocal: 0, canAutoHide: 0, importType: definition, noRenameOnPromotion: 0), insts: 3, calls: ((callee: ^28, tail: 1))))) ; guid = 13316669896841227651
^26 = gv: (name: "_RNvCsbWvCnYHbl8o_20bennett_emit_cunwind4body", summaries: (function: (module: ^0, flags: (linkage: internal, visibility: default, notEligibleToImport: 0, live: 0, dsoLocal: 1, canAutoHide: 0, importType: definition, noRenameOnPromotion: 0), insts: 13, funcFlags: (readNone: 0, readOnly: 0, noRecurse: 0, returnDoesNotAlias: 0, noInline: 0, alwaysInline: 0, noUnwind: 1, mayThrow: 0, hasUnknownCall: 0, mustBeUnreachable: 0), calls: ((callee: ^14), (callee: ^2, tail: 1), (callee: ^4)), refs: (^27)))) ; guid = 14374316208864726621
^27 = gv: (name: "rust_eh_personality") ; guid = 14807195490537628141
^28 = gv: (name: "__bennett_qfree") ; guid = 16633130219932291175
^29 = gv: (name: "__bennett_ctrl") ; guid = 16800917137780716501
^30 = gv: (name: "__bennett_adj") ; guid = 17297851703929373874
^31 = gv: (name: "__bennett_reversible") ; guid = 17933274057403866412
^32 = blockcount: 0
