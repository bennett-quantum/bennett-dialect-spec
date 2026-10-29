; ModuleID = 'bennett_emit.7dee62cccf2c2c09-cgu.0'
source_filename = "bennett_emit.7dee62cccf2c2c09-cgu.0"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@alloc_1962bf4fe486936f0f5554c0adc669f6 = private unnamed_addr constant [16 x i8] c"bennett_emit.rs\00", align 1, !guid !0
@alloc_ee3d2d55696e882886ba94a45b030c8d = private unnamed_addr constant <{ ptr, [16 x i8] }> <{ ptr @alloc_1962bf4fe486936f0f5554c0adc669f6, [16 x i8] c"\0F\00\00\00\00\00\00\00,\00\00\00?\00\00\00" }>, align 8, !guid !1
@alloc_854c627aaaf40140194e84d02bdef514 = private unnamed_addr constant <{ ptr, [16 x i8] }> <{ ptr @alloc_1962bf4fe486936f0f5554c0adc669f6, [16 x i8] c"\0F\00\00\00\00\00\00\00-\00\00\00\10\00\00\00" }>, align 8, !guid !2
@alloc_9371aad6bfd5c67695b0f5086162e7ae = private unnamed_addr constant [48 x i8] c"assertion failed: core::mem::size_of::<F>() == 0", align 1, !guid !3
@alloc_25f136abd1c665ef5cb8d3b424de74fa = private unnamed_addr constant <{ ptr, [16 x i8] }> <{ ptr @alloc_1962bf4fe486936f0f5554c0adc669f6, [16 x i8] c"\0F\00\00\00\00\00\00\00/\00\00\003\00\00\00" }>, align 8, !guid !4
@alloc_5bc228325e92f3f8cb80cbc8d753578f = private unnamed_addr constant <{ ptr, [16 x i8] }> <{ ptr @alloc_1962bf4fe486936f0f5554c0adc669f6, [16 x i8] c"\0F\00\00\00\00\00\00\00$\00\00\00\11\00\00\00" }>, align 8, !guid !5
@alloc_3e1ebac14318b612ab4efabc52799932 = private unnamed_addr constant [186 x i8] c"unsafe precondition(s) violated: usize::unchecked_add cannot overflow\0A\0AThis indicates a bug in the program. This Undefined Behavior check is optional, and cannot be relied on for safety.", align 1, !guid !6
@alloc_80c4ceccfccafaac944cb8ec78d6e597 = private unnamed_addr constant [79 x i8] c"/rustc/58cf8f9c35b355199727627d07ae34a4e2846d67/library/core/src/iter/range.rs\00", align 1, !guid !7
@alloc_31443e3fbc661f3a4fbbb2b484d80546 = private unnamed_addr constant <{ ptr, [16 x i8] }> <{ ptr @alloc_80c4ceccfccafaac944cb8ec78d6e597, [16 x i8] c"N\00\00\00\00\00\00\00$\02\00\00\01\00\00\00" }>, align 8, !guid !8
@alloc_39c77b5ece2e5ccc5db66753b62198b9 = private unnamed_addr constant <{ ptr, [16 x i8] }> <{ ptr @alloc_1962bf4fe486936f0f5554c0adc669f6, [16 x i8] c"\0F\00\00\00\00\00\00\00G\00\00\00\17\00\00\00" }>, align 8, !guid !9
@alloc_6e92a08db75e204a7d080a03e53a04f3 = private unnamed_addr constant <{ ptr, [16 x i8] }> <{ ptr @alloc_1962bf4fe486936f0f5554c0adc669f6, [16 x i8] c"\0F\00\00\00\00\00\00\00U\00\00\00%\00\00\00" }>, align 8, !guid !10
@alloc_a2267ae30f948452c2675cb964812821 = private unnamed_addr constant <{ ptr, [16 x i8] }> <{ ptr @alloc_1962bf4fe486936f0f5554c0adc669f6, [16 x i8] c"\0F\00\00\00\00\00\00\00F\00\00\00\15\00\00\00" }>, align 8, !guid !11
@alloc_37f62a15fae368a2423b3a16c75adcc9 = private unnamed_addr constant [1 x i8] c"x", align 1, !guid !12
@alloc_f4d302337a3abcf1f4238b174f3f0242 = private unnamed_addr constant <{ ptr, [16 x i8] }> <{ ptr @alloc_1962bf4fe486936f0f5554c0adc669f6, [16 x i8] c"\0F\00\00\00\00\00\00\005\00\00\008\00\00\00" }>, align 8, !guid !13

; bennett_emit::tramp::<bennett_emit::case_entry::{closure#0}>
; Function Attrs: nounwind nonlazybind uwtable
define internal void @_RINvCsaOknTnIz6g7_12bennett_emit5trampNCNvB2_10case_entry0EB2_(ptr %p) unnamed_addr #0 personality ptr @rust_eh_personality !guid !18 {
start:
  %0 = alloca [16 x i8], align 8
  %f = alloca [0 x i8], align 1
  br label %bb1

terminate:                                        ; No predecessors!
  %1 = landingpad { ptr, i32 }
          filter [0 x ptr] zeroinitializer
; call core::panicking::panic_cannot_unwind
  call void @_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind() #9
  unreachable

bb1:                                              ; preds = %start
  br label %bb2

bb2:                                              ; preds = %bb1
  %_10 = ptrtoint ptr %p to i64
  %_12 = and i64 %_10, 7
  %_13 = icmp eq i64 %_12, 0
  br i1 %_13, label %bb7, label %panic

bb7:                                              ; preds = %bb2
  %_15 = ptrtoint ptr %p to i64
  %_16 = icmp eq i64 %_15, 0
  %_17 = and i1 %_16, true
  %_18 = xor i1 %_17, true
  br i1 %_18, label %bb8, label %panic1

panic:                                            ; preds = %bb2
; call core::panicking::panic_misaligned_pointer_dereference
  call void @_RNvNtCskADBYZwJmSU_4core9panicking36panic_misaligned_pointer_dereference(i64 8, i64 %_10, ptr align 8 @alloc_854c627aaaf40140194e84d02bdef514) #10
  unreachable

bb8:                                              ; preds = %bb7
; invoke bennett_emit::case_entry::{closure#0}
  invoke void @_RNCNvCsaOknTnIz6g7_12bennett_emit10case_entry0B3_(ptr %f, ptr align 8 %p)
          to label %bb3 unwind label %cleanup

panic1:                                           ; preds = %bb7
; call core::panicking::panic_null_reference_constructed
  call void @_RNvNtCskADBYZwJmSU_4core9panicking32panic_null_reference_constructed(ptr align 8 @alloc_854c627aaaf40140194e84d02bdef514) #10
  unreachable

bb5:                                              ; preds = %cleanup
  br label %bb6

cleanup:                                          ; preds = %bb8
  %2 = landingpad { ptr, i32 }
          cleanup
  %3 = extractvalue { ptr, i32 } %2, 0
  %4 = extractvalue { ptr, i32 } %2, 1
  store ptr %3, ptr %0, align 8
  %5 = getelementptr inbounds i8, ptr %0, i64 8
  store i32 %4, ptr %5, align 8
  br label %bb5

bb3:                                              ; preds = %bb8
  br label %bb4

bb4:                                              ; preds = %bb3
  ret void

bb6:                                              ; preds = %bb5
; call core::panicking::panic_cannot_unwind
  call void @_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind() #11
  unreachable
}

; bennett_emit::region_of::<bennett_emit::case_entry::{closure#0}>
; Function Attrs: nonlazybind uwtable
define internal ptr @_RINvCsaOknTnIz6g7_12bennett_emit9region_ofNCNvB2_10case_entry0EB2_() unnamed_addr #1 personality ptr @rust_eh_personality !guid !19 {
start:
  br label %bb1

bb1:                                              ; preds = %start
  %_2 = icmp eq i64 0, 0
  br i1 %_2, label %bb2, label %bb3

bb3:                                              ; preds = %bb1
; call core::panicking::panic
  call void @_RNvNtCskADBYZwJmSU_4core9panicking5panic(ptr @alloc_9371aad6bfd5c67695b0f5086162e7ae, i64 48, ptr align 8 @alloc_25f136abd1c665ef5cb8d3b424de74fa) #12
  unreachable

bb2:                                              ; preds = %bb1
  ret ptr @_RINvCsaOknTnIz6g7_12bennett_emit5trampNCNvB2_10case_entry0EB2_

bb5:                                              ; No predecessors!
  unreachable

bb6:                                              ; No predecessors!
  unreachable
}

; core::ptr::drop_glue::<bennett_emit::Guard>
; Function Attrs: nonlazybind uwtable
define void @_RINvNtCskADBYZwJmSU_4core3ptr9drop_glueNtCsaOknTnIz6g7_12bennett_emit5GuardEBD_(ptr align 8 %_1) unnamed_addr #1 !guid !20 {
start:
; call <bennett_emit::Guard as core::ops::drop::Drop>::drop
  call void @_RNvXCsaOknTnIz6g7_12bennett_emitNtB2_5GuardNtNtNtCskADBYZwJmSU_4core3ops4drop4Drop4drop(ptr align 8 %_1)
  ret void
}

; bennett_emit::case_entry::{closure#0}
; Function Attrs: inlinehint nonlazybind uwtable
define internal void @_RNCNvCsaOknTnIz6g7_12bennett_emit10case_entry0B3_(ptr %_1, ptr align 8 %e) unnamed_addr #2 !guid !21 {
start:
  %_3 = load ptr, ptr %e, align 8
  %0 = getelementptr inbounds i8, ptr %e, i64 8
  %_4 = load i64, ptr %0, align 8
  call void @__bennett_gate(i32 5, ptr %_3, i64 %_4) #13
  ret void
}

; bennett_emit::body
; Function Attrs: nounwind nonlazybind uwtable
define internal void @_RNvCsaOknTnIz6g7_12bennett_emit4body(ptr %p) unnamed_addr #0 !guid !22 {
start:
  %_12 = ptrtoint ptr %p to i64
  %_14 = and i64 %_12, 7
  %_15 = icmp eq i64 %_14, 0
  br i1 %_15, label %bb3, label %panic

bb3:                                              ; preds = %start
  %_17 = ptrtoint ptr %p to i64
  %_18 = icmp eq i64 %_17, 0
  %_19 = and i1 %_18, true
  %_20 = xor i1 %_19, true
  br i1 %_20, label %bb4, label %panic1

panic:                                            ; preds = %start
; call core::panicking::panic_misaligned_pointer_dereference
  call void @_RNvNtCskADBYZwJmSU_4core9panicking36panic_misaligned_pointer_dereference(i64 8, i64 %_12, ptr align 8 @alloc_5bc228325e92f3f8cb80cbc8d753578f) #10
  unreachable

bb4:                                              ; preds = %bb3
  %_5 = load ptr, ptr %p, align 8
  %0 = getelementptr inbounds i8, ptr %p, i64 8
  %_6 = load i64, ptr %0, align 8
  %1 = getelementptr inbounds i8, ptr %p, i64 16
  %_7 = load double, ptr %1, align 8
  call void @__bennett_rot(i32 1, ptr %_5, i64 %_6, double %_7) #13
  %_9 = load ptr, ptr %p, align 8
  %2 = getelementptr inbounds i8, ptr %p, i64 8
  %_10 = load i64, ptr %2, align 8
  call void @__bennett_gate(i32 2, ptr %_9, i64 %_10) #13
  ret void

panic1:                                           ; preds = %bb3
; call core::panicking::panic_null_reference_constructed
  call void @_RNvNtCskADBYZwJmSU_4core9panicking32panic_null_reference_constructed(ptr align 8 @alloc_5bc228325e92f3f8cb80cbc8d753578f) #10
  unreachable
}

; <core::fmt::Arguments>::from_str
; Function Attrs: inlinehint nonlazybind uwtable
define internal { ptr, ptr } @_RNvMs4_NtCskADBYZwJmSU_4core3fmtNtB5_9Arguments8from_strCsaOknTnIz6g7_12bennett_emit(ptr %s.0, i64 %s.1) unnamed_addr #2 !guid !23 {
start:
  %_6 = shl i64 %s.1, 1
  %_5 = or i64 %_6, 1
  %_4 = inttoptr i64 %_5 to ptr
  %0 = insertvalue { ptr, ptr } poison, ptr %s.0, 0
  %1 = insertvalue { ptr, ptr } %0, ptr %_4, 1
  ret { ptr, ptr } %1
}

; <usize>::unchecked_add::precondition_check
; Function Attrs: inlinehint nounwind nonlazybind uwtable
define internal void @_RNvNvMs9_NtCskADBYZwJmSU_4core3numj13unchecked_add18precondition_checkCsaOknTnIz6g7_12bennett_emit(i64 %lhs, i64 %rhs, ptr align 8 %0) unnamed_addr #3 !guid !24 {
start:
  %_7.0 = add i64 %lhs, %rhs
  %_7.1 = icmp ult i64 %_7.0, %lhs
  br i1 %_7.1, label %bb1, label %bb2

bb2:                                              ; preds = %start
  ret void

bb1:                                              ; preds = %start
; call core::panicking::panic_nounwind_fmt
  call void @_RNvNtCskADBYZwJmSU_4core9panicking18panic_nounwind_fmt(ptr @alloc_3e1ebac14318b612ab4efabc52799932, ptr inttoptr (i64 373 to ptr), i1 zeroext false, ptr align 8 %0) #10
  unreachable
}

; <bennett_emit::Guard as core::ops::drop::Drop>::drop
; Function Attrs: nonlazybind uwtable
define void @_RNvXCsaOknTnIz6g7_12bennett_emitNtB2_5GuardNtNtNtCskADBYZwJmSU_4core3ops4drop4Drop4drop(ptr align 8 %self) unnamed_addr #1 !guid !25 {
start:
  %_2 = load ptr, ptr %self, align 8
  call void @__bennett_qfree(ptr %_2) #13
  ret void
}

; <core::ops::range::Range<usize> as core::iter::traits::collect::IntoIterator>::into_iter
; Function Attrs: inlinehint nonlazybind uwtable
define { i64, i64 } @_RNvXNtNtNtCskADBYZwJmSU_4core4iter6traits7collectINtNtNtB8_3ops5range5RangejENtB2_12IntoIterator9into_iterCsaOknTnIz6g7_12bennett_emit(i64 %self.0, i64 %self.1) unnamed_addr #2 !guid !26 {
start:
  %0 = insertvalue { i64, i64 } poison, i64 %self.0, 0
  %1 = insertvalue { i64, i64 } %0, i64 %self.1, 1
  ret { i64, i64 } %1
}

; <core::ops::range::Range<usize> as core::iter::range::RangeIteratorImpl>::spec_next
; Function Attrs: inlinehint nonlazybind uwtable
define { i64, i64 } @_RNvXs3_NtNtCskADBYZwJmSU_4core4iter5rangeINtNtNtB9_3ops5range5RangejENtB5_17RangeIteratorImpl9spec_nextCsaOknTnIz6g7_12bennett_emit(ptr align 8 %self) unnamed_addr #2 !guid !27 {
start:
  %_0 = alloca [16 x i8], align 8
  %_4 = getelementptr inbounds i8, ptr %self, i64 8
  %_3.i = load i64, ptr %self, align 8
  %_4.i = load i64, ptr %_4, align 8
  %_0.i = icmp ult i64 %_3.i, %_4.i
  br i1 %_0.i, label %bb2, label %bb4

bb4:                                              ; preds = %start
  store i64 0, ptr %_0, align 8
  br label %bb5

bb2:                                              ; preds = %start
  %old = load i64, ptr %self, align 8
; call <usize as core::iter::range::Step>::forward_unchecked
  %_6 = call i64 @_RNvXsL_NtNtCskADBYZwJmSU_4core4iter5rangejNtB5_4Step17forward_uncheckedCsaOknTnIz6g7_12bennett_emit(i64 %old, i64 1) #14
  store i64 %_6, ptr %self, align 8
  %0 = getelementptr inbounds i8, ptr %_0, i64 8
  store i64 %old, ptr %0, align 8
  store i64 1, ptr %_0, align 8
  br label %bb5

bb5:                                              ; preds = %bb2, %bb4
  %1 = load i64, ptr %_0, align 8
  %2 = getelementptr inbounds i8, ptr %_0, i64 8
  %3 = load i64, ptr %2, align 8
  %4 = insertvalue { i64, i64 } poison, i64 %1, 0
  %5 = insertvalue { i64, i64 } %4, i64 %3, 1
  ret { i64, i64 } %5
}

; <core::ops::range::Range<usize> as core::iter::traits::iterator::Iterator>::next
; Function Attrs: inlinehint nonlazybind uwtable
define { i64, i64 } @_RNvXs4_NtNtCskADBYZwJmSU_4core4iter5rangeINtNtNtB9_3ops5range5RangejENtNtNtB7_6traits8iterator8Iterator4nextCsaOknTnIz6g7_12bennett_emit(ptr align 8 %self) unnamed_addr #2 !guid !28 {
start:
; call <core::ops::range::Range<usize> as core::iter::range::RangeIteratorImpl>::spec_next
  %0 = call { i64, i64 } @_RNvXs3_NtNtCskADBYZwJmSU_4core4iter5rangeINtNtNtB9_3ops5range5RangejENtB5_17RangeIteratorImpl9spec_nextCsaOknTnIz6g7_12bennett_emit(ptr align 8 %self) #14
  %_0.0 = extractvalue { i64, i64 } %0, 0
  %_0.1 = extractvalue { i64, i64 } %0, 1
  %1 = insertvalue { i64, i64 } poison, i64 %_0.0, 0
  %2 = insertvalue { i64, i64 } %1, i64 %_0.1, 1
  ret { i64, i64 } %2
}

; <usize as core::iter::range::Step>::forward_unchecked
; Function Attrs: inlinehint nonlazybind uwtable
define internal i64 @_RNvXsL_NtNtCskADBYZwJmSU_4core4iter5rangejNtB5_4Step17forward_uncheckedCsaOknTnIz6g7_12bennett_emit(i64 %start1, i64 %n) unnamed_addr #2 !guid !29 {
start:
  br label %bb1

bb1:                                              ; preds = %start
; call <usize>::unchecked_add::precondition_check
  call void @_RNvNvMs9_NtCskADBYZwJmSU_4core3numj13unchecked_add18precondition_checkCsaOknTnIz6g7_12bennett_emit(i64 %start1, i64 %n, ptr align 8 @alloc_31443e3fbc661f3a4fbbb2b484d80546) #15
  br label %bb2

bb2:                                              ; preds = %bb1
  %_0 = add nuw i64 %start1, %n
  ret i64 %_0
}

; Function Attrs: nounwind nonlazybind uwtable
define i64 @case_entry(i64 %x) unnamed_addr #0 personality ptr @rust_eh_personality !guid !30 {
start:
  %0 = alloca [16 x i8], align 8
  %_82 = alloca [16 x i8], align 8
  %iter1 = alloca [16 x i8], align 8
  %g = alloca [8 x i8], align 8
  %_27 = alloca [16 x i8], align 8
  %iter = alloca [16 x i8], align 8
  %tab = alloca [32 x i8], align 8
  %e = alloca [24 x i8], align 8
  %r = alloca [8 x i8], align 8
  %h = call ptr @__bennett_qalloc(i64 0, i64 4) #13
  call void @__bennett_gate(i32 1, ptr %h, i64 0) #13
  %_5 = uitofp i64 %x to double
  %theta = fmul double %_5, 1.250000e-01
  call void @__bennett_rot(i32 3, ptr %h, i64 1, double %theta) #13
  call void @__bennett_gate2(i32 4, ptr %h, i64 0, ptr %h, i64 1) #13
  store i64 0, ptr %r, align 8
  %_9 = call zeroext i1 @__bennett_measure(ptr %h, i64 0) #13
  br i1 %_9, label %bb6, label %bb8

bb8:                                              ; preds = %bb6, %start
  store ptr %h, ptr %e, align 8
  %1 = getelementptr inbounds i8, ptr %e, i64 8
  store i64 3, ptr %1, align 8
  %2 = getelementptr inbounds i8, ptr %e, i64 16
  store double %theta, ptr %2, align 8
  call void @__bennett_ctrl(ptr %h, i64 0, ptr @_RNvCsaOknTnIz6g7_12bennett_emit4body, i64 8, ptr %e) #13
; invoke bennett_emit::region_of::<bennett_emit::case_entry::{closure#0}>
  %f = invoke ptr @_RINvCsaOknTnIz6g7_12bennett_emit9region_ofNCNvB2_10case_entry0EB2_()
          to label %bb10 unwind label %terminate

bb6:                                              ; preds = %start
  call void @__bennett_gate(i32 2, ptr %h, i64 2) #13
  store i64 1, ptr %r, align 8
  br label %bb8

terminate:                                        ; preds = %panic3, %bb38, %bb36, %bb35, %panic, %bb14, %repeat_loop_next, %bb8
  %3 = landingpad { ptr, i32 }
          filter [0 x ptr] zeroinitializer
; call core::panicking::panic_cannot_unwind
  call void @_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind() #9
  unreachable

bb10:                                             ; preds = %bb8
  call void @__bennett_ctrl(ptr %h, i64 1, ptr %f, i64 8, ptr %e) #13
  br label %bb12

bb12:                                             ; preds = %bb10
  %4 = getelementptr inbounds nuw ptr, ptr %tab, i64 0
  %5 = getelementptr inbounds nuw ptr, ptr %tab, i64 4
  br label %repeat_loop_header

repeat_loop_header:                               ; preds = %repeat_loop_body, %bb12
  %6 = phi ptr [ %4, %bb12 ], [ %8, %repeat_loop_body ]
  %7 = icmp ne ptr %6, %5
  br i1 %7, label %repeat_loop_body, label %repeat_loop_next

repeat_loop_body:                                 ; preds = %repeat_loop_header
  store ptr null, ptr %6, align 8
  %8 = getelementptr inbounds ptr, ptr %6, i64 1
  br label %repeat_loop_header

repeat_loop_next:                                 ; preds = %repeat_loop_header
; invoke <core::ops::range::Range<usize> as core::iter::traits::collect::IntoIterator>::into_iter
  %9 = invoke { i64, i64 } @_RNvXNtNtNtCskADBYZwJmSU_4core4iter6traits7collectINtNtNtB8_3ops5range5RangejENtB2_12IntoIterator9into_iterCsaOknTnIz6g7_12bennett_emit(i64 0, i64 4)
          to label %bb13 unwind label %terminate

bb13:                                             ; preds = %repeat_loop_next
  %_24.0 = extractvalue { i64, i64 } %9, 0
  %_24.1 = extractvalue { i64, i64 } %9, 1
  store i64 %_24.0, ptr %iter, align 8
  %10 = getelementptr inbounds i8, ptr %iter, i64 8
  store i64 %_24.1, ptr %10, align 8
  br label %bb14

bb14:                                             ; preds = %bb20, %bb13
; invoke <core::ops::range::Range<usize> as core::iter::traits::iterator::Iterator>::next
  %11 = invoke { i64, i64 } @_RNvXs4_NtNtCskADBYZwJmSU_4core4iter5rangeINtNtNtB9_3ops5range5RangejENtNtNtB7_6traits8iterator8Iterator4nextCsaOknTnIz6g7_12bennett_emit(ptr align 8 %iter)
          to label %bb15 unwind label %terminate

bb15:                                             ; preds = %bb14
  %12 = extractvalue { i64, i64 } %11, 0
  %13 = extractvalue { i64, i64 } %11, 1
  store i64 %12, ptr %_27, align 8
  %14 = getelementptr inbounds i8, ptr %_27, i64 8
  store i64 %13, ptr %14, align 8
  %_29 = load i64, ptr %_27, align 8
  %15 = getelementptr inbounds i8, ptr %_27, i64 8
  %16 = load i64, ptr %15, align 8
  %17 = trunc nuw i64 %_29 to i1
  br i1 %17, label %bb17, label %bb18

bb17:                                             ; preds = %bb15
  %18 = getelementptr inbounds i8, ptr %_27, i64 8
  %k5 = load i64, ptr %18, align 8
  %_31 = call ptr @__bennett_qalloc(i64 0, i64 1) #13
  %_32 = icmp ult i64 %k5, 4
  br i1 %_32, label %bb20, label %panic6

bb18:                                             ; preds = %bb15
  %_36 = and i64 %x, 3
  %_37 = icmp ult i64 %_36, 4
  br i1 %_37, label %bb21, label %panic

bb21:                                             ; preds = %bb18
  %19 = getelementptr inbounds nuw ptr, ptr %tab, i64 %_36
  %_34 = load ptr, ptr %19, align 8
  call void @__bennett_gate(i32 1, ptr %_34, i64 0) #13
  call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr %h, i64 0, ptr @_RNvCsaOknTnIz6g7_12bennett_emit4body, i64 8, i32 1, double 2.500000e+00, ptr %h) #13
  call void @__bennett_adj(ptr @_RNvCsaOknTnIz6g7_12bennett_emit4body, ptr %e) #13
  call void @__bennett_compute(ptr @_RNvCsaOknTnIz6g7_12bennett_emit4body, ptr @_RNvCsaOknTnIz6g7_12bennett_emit4body, ptr %e) #13
  call void @__bennett_reversible(ptr @_RNvCsaOknTnIz6g7_12bennett_emit4body, i64 3, ptr %e) #13
  call void @__bennett_inplace(ptr @_RNvCsaOknTnIz6g7_12bennett_emit4body, ptr @_RNvCsaOknTnIz6g7_12bennett_emit4body, ptr %e) #13
  %_64 = call ptr @__bennett_qborrow(i64 0, i64 1) #13
  store ptr %_64, ptr %g, align 8
  %_66 = load ptr, ptr %g, align 8
  br label %bb29

panic:                                            ; preds = %bb18
; invoke core::panicking::panic_bounds_check
  invoke void @_RNvNtCskADBYZwJmSU_4core9panicking18panic_bounds_check(i64 %_36, i64 4, ptr align 8 @alloc_39c77b5ece2e5ccc5db66753b62198b9) #16
          to label %unreachable unwind label %terminate

unreachable:                                      ; preds = %panic6, %panic3, %panic
  unreachable

bb29:                                             ; preds = %bb21
  %20 = getelementptr inbounds nuw ptr, ptr %tab, i64 0
  %_67 = load ptr, ptr %20, align 8
  call void @__bennett_qload(ptr %_66, ptr %h, ptr %_67) #13
  br label %bb31

bb31:                                             ; preds = %bb29
  %21 = getelementptr inbounds nuw ptr, ptr %tab, i64 1
  %_71 = load ptr, ptr %21, align 8
  %_74 = load ptr, ptr %g, align 8
  call void @__bennett_qstore(ptr %h, ptr %_71, ptr %_74) #13
  call void @rt_may_unwind(i64 %x) #17
  %_77 = load ptr, ptr %g, align 8
  invoke void @__bennett_gate(i32 6, ptr %_77, i64 0)
          to label %bb34 unwind label %cleanup

bb44:                                             ; preds = %cleanup
; invoke core::ptr::drop_glue::<bennett_emit::Guard>
  invoke void @_RINvNtCskADBYZwJmSU_4core3ptr9drop_glueNtCsaOknTnIz6g7_12bennett_emit5GuardEBD_(ptr align 8 %g) #18
          to label %bb45 unwind label %terminate4

cleanup:                                          ; preds = %bb31
  %22 = landingpad { ptr, i32 }
          cleanup
  %23 = extractvalue { ptr, i32 } %22, 0
  %24 = extractvalue { ptr, i32 } %22, 1
  store ptr %23, ptr %0, align 8
  %25 = getelementptr inbounds i8, ptr %0, i64 8
  store i32 %24, ptr %25, align 8
  br label %bb44

bb34:                                             ; preds = %bb31
; invoke core::ptr::drop_glue::<bennett_emit::Guard>
  invoke void @_RINvNtCskADBYZwJmSU_4core3ptr9drop_glueNtCsaOknTnIz6g7_12bennett_emit5GuardEBD_(ptr align 8 %g)
          to label %bb35 unwind label %cleanup2

bb45:                                             ; preds = %bb44, %cleanup2
; call core::panicking::panic_cannot_unwind
  call void @_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind() #11
  unreachable

cleanup2:                                         ; preds = %bb34
  %26 = landingpad { ptr, i32 }
          cleanup
  %27 = extractvalue { ptr, i32 } %26, 0
  %28 = extractvalue { ptr, i32 } %26, 1
  store ptr %27, ptr %0, align 8
  %29 = getelementptr inbounds i8, ptr %0, i64 8
  store i32 %28, ptr %29, align 8
  br label %bb45

bb35:                                             ; preds = %bb34
  invoke void @__bennett_qfree(ptr %h)
          to label %bb36 unwind label %terminate

bb36:                                             ; preds = %bb35
; invoke <core::ops::range::Range<usize> as core::iter::traits::collect::IntoIterator>::into_iter
  %30 = invoke { i64, i64 } @_RNvXNtNtNtCskADBYZwJmSU_4core4iter6traits7collectINtNtNtB8_3ops5range5RangejENtB2_12IntoIterator9into_iterCsaOknTnIz6g7_12bennett_emit(i64 0, i64 4)
          to label %bb37 unwind label %terminate

bb37:                                             ; preds = %bb36
  %_79.0 = extractvalue { i64, i64 } %30, 0
  %_79.1 = extractvalue { i64, i64 } %30, 1
  store i64 %_79.0, ptr %iter1, align 8
  %31 = getelementptr inbounds i8, ptr %iter1, i64 8
  store i64 %_79.1, ptr %31, align 8
  br label %bb38

bb38:                                             ; preds = %bb42, %bb37
; invoke <core::ops::range::Range<usize> as core::iter::traits::iterator::Iterator>::next
  %32 = invoke { i64, i64 } @_RNvXs4_NtNtCskADBYZwJmSU_4core4iter5rangeINtNtNtB9_3ops5range5RangejENtNtNtB7_6traits8iterator8Iterator4nextCsaOknTnIz6g7_12bennett_emit(ptr align 8 %iter1)
          to label %bb39 unwind label %terminate

bb39:                                             ; preds = %bb38
  %33 = extractvalue { i64, i64 } %32, 0
  %34 = extractvalue { i64, i64 } %32, 1
  store i64 %33, ptr %_82, align 8
  %35 = getelementptr inbounds i8, ptr %_82, i64 8
  store i64 %34, ptr %35, align 8
  %_84 = load i64, ptr %_82, align 8
  %36 = getelementptr inbounds i8, ptr %_82, i64 8
  %37 = load i64, ptr %36, align 8
  %38 = trunc nuw i64 %_84 to i1
  br i1 %38, label %bb40, label %bb41

bb40:                                             ; preds = %bb39
  %39 = getelementptr inbounds i8, ptr %_82, i64 8
  %k = load i64, ptr %39, align 8
  %_88 = icmp ult i64 %k, 4
  br i1 %_88, label %bb42, label %panic3

bb41:                                             ; preds = %bb39
  call void @__bennett_qfree(ptr %h) #13
  %_0 = load i64, ptr %r, align 8
  ret i64 %_0

bb42:                                             ; preds = %bb40
  %40 = getelementptr inbounds nuw ptr, ptr %tab, i64 %k
  %_87 = load ptr, ptr %40, align 8
  call void @__bennett_qfree(ptr %_87) #13
  br label %bb38

panic3:                                           ; preds = %bb40
; invoke core::panicking::panic_bounds_check
  invoke void @_RNvNtCskADBYZwJmSU_4core9panicking18panic_bounds_check(i64 %k, i64 4, ptr align 8 @alloc_6e92a08db75e204a7d080a03e53a04f3) #16
          to label %unreachable unwind label %terminate

terminate4:                                       ; preds = %bb44
  %41 = landingpad { ptr, i32 }
          filter [0 x ptr] zeroinitializer
; call core::panicking::panic_in_cleanup
  call void @_RNvNtCskADBYZwJmSU_4core9panicking16panic_in_cleanup() #9
  unreachable

bb20:                                             ; preds = %bb17
  %42 = getelementptr inbounds nuw ptr, ptr %tab, i64 %k5
  store ptr %_31, ptr %42, align 8
  br label %bb14

panic6:                                           ; preds = %bb17
; invoke core::panicking::panic_bounds_check
  invoke void @_RNvNtCskADBYZwJmSU_4core9panicking18panic_bounds_check(i64 %k5, i64 4, ptr align 8 @alloc_a2267ae30f948452c2675cb964812821) #16
          to label %unreachable unwind label %terminate7

terminate7:                                       ; preds = %panic6
  %43 = landingpad { ptr, i32 }
          filter [0 x ptr] zeroinitializer
; call core::panicking::panic_cannot_unwind
  call void @_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind() #9
  unreachable

bb16:                                             ; No predecessors!
  unreachable
}

; Function Attrs: noinline nounwind nonlazybind uwtable
define void @rt_may_unwind(i64 %x) unnamed_addr #4 personality ptr @rust_eh_personality !guid !31 {
start:
  %_2 = icmp eq i64 %x, 77
  br i1 %_2, label %bb1, label %bb3

bb3:                                              ; preds = %start
  ret void

bb1:                                              ; preds = %start
; invoke <core::fmt::Arguments>::from_str
  %0 = invoke { ptr, ptr } @_RNvMs4_NtCskADBYZwJmSU_4core3fmtNtB5_9Arguments8from_strCsaOknTnIz6g7_12bennett_emit(ptr @alloc_37f62a15fae368a2423b3a16c75adcc9, i64 1)
          to label %bb2 unwind label %terminate

terminate:                                        ; preds = %bb2, %bb1
  %1 = landingpad { ptr, i32 }
          filter [0 x ptr] zeroinitializer
; call core::panicking::panic_cannot_unwind
  call void @_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind() #9
  unreachable

bb2:                                              ; preds = %bb1
  %_4.0 = extractvalue { ptr, ptr } %0, 0
  %_4.1 = extractvalue { ptr, ptr } %0, 1
; invoke core::panicking::panic_fmt
  invoke void @_RNvNtCskADBYZwJmSU_4core9panicking9panic_fmt(ptr %_4.0, ptr %_4.1, ptr align 8 @alloc_f4d302337a3abcf1f4238b174f3f0242) #16
          to label %unreachable unwind label %terminate

unreachable:                                      ; preds = %bb2
  unreachable
}

; Function Attrs: nounwind nonlazybind uwtable
declare i32 @rust_eh_personality(i32, i32, i64, ptr, ptr) unnamed_addr #0

; core::panicking::panic_cannot_unwind
; Function Attrs: cold minsize noinline noreturn nounwind nonlazybind optsize uwtable
declare void @_RNvNtCskADBYZwJmSU_4core9panicking19panic_cannot_unwind() unnamed_addr #5

; core::panicking::panic_misaligned_pointer_dereference
; Function Attrs: cold minsize noinline noreturn nounwind nonlazybind optsize uwtable
declare void @_RNvNtCskADBYZwJmSU_4core9panicking36panic_misaligned_pointer_dereference(i64, i64, ptr align 8) unnamed_addr #5

; core::panicking::panic_null_reference_constructed
; Function Attrs: cold minsize noinline noreturn nounwind nonlazybind optsize uwtable
declare void @_RNvNtCskADBYZwJmSU_4core9panicking32panic_null_reference_constructed(ptr align 8) unnamed_addr #5

; core::panicking::panic
; Function Attrs: cold noinline noreturn nonlazybind uwtable
declare void @_RNvNtCskADBYZwJmSU_4core9panicking5panic(ptr, i64, ptr align 8) unnamed_addr #6

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_gate(i32, ptr, i64) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_rot(i32, ptr, i64, double) unnamed_addr #0

; core::panicking::panic_nounwind_fmt
; Function Attrs: cold noinline noreturn nounwind nonlazybind uwtable
declare void @_RNvNtCskADBYZwJmSU_4core9panicking18panic_nounwind_fmt(ptr, ptr, i1 zeroext, ptr align 8) unnamed_addr #7

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_qfree(ptr) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare ptr @__bennett_qalloc(i64, i64) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_gate2(i32, ptr, i64, ptr, i64) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare zeroext i1 @__bennett_measure(ptr, i64) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_ctrl(ptr, i64, ptr, i64, ptr) unnamed_addr #0

; core::panicking::panic_bounds_check
; Function Attrs: cold minsize noinline noreturn nonlazybind optsize uwtable
declare void @_RNvNtCskADBYZwJmSU_4core9panicking18panic_bounds_check(i64, i64, ptr align 8) unnamed_addr #8

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_ctrl_v(ptr, i64, ptr, i64, ...) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_adj(ptr, ptr) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_compute(ptr, ptr, ptr) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_reversible(ptr, i64, ptr) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_inplace(ptr, ptr, ptr) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare ptr @__bennett_qborrow(i64, i64) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_qload(ptr, ptr, ptr) unnamed_addr #0

; Function Attrs: nounwind nonlazybind uwtable
declare void @__bennett_qstore(ptr, ptr, ptr) unnamed_addr #0

; core::panicking::panic_in_cleanup
; Function Attrs: cold minsize noinline noreturn nounwind nonlazybind optsize uwtable
declare void @_RNvNtCskADBYZwJmSU_4core9panicking16panic_in_cleanup() unnamed_addr #5

; core::panicking::panic_fmt
; Function Attrs: cold noinline noreturn nonlazybind uwtable
declare void @_RNvNtCskADBYZwJmSU_4core9panicking9panic_fmt(ptr, ptr, ptr align 8) unnamed_addr #6

attributes #0 = { nounwind nonlazybind uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #1 = { nonlazybind uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #2 = { inlinehint nonlazybind uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #3 = { inlinehint nounwind nonlazybind uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #4 = { noinline nounwind nonlazybind uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #5 = { cold minsize noinline noreturn nounwind nonlazybind optsize uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #6 = { cold noinline noreturn nonlazybind uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #7 = { cold noinline noreturn nounwind nonlazybind uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #8 = { cold minsize noinline noreturn nonlazybind optsize uwtable "probe-stack"="inline-asm" "target-cpu"="x86-64" }
attributes #9 = { cold noreturn nounwind }
attributes #10 = { noinline noreturn nounwind }
attributes #11 = { cold noinline noreturn nounwind }
attributes #12 = { noinline noreturn }
attributes #13 = { nounwind }
attributes #14 = { inlinehint }
attributes #15 = { inlinehint nounwind }
attributes #16 = { noreturn }
attributes #17 = { noinline nounwind }
attributes #18 = { cold }

!llvm.module.flags = !{!14, !15, !16}
!llvm.ident = !{!17}

!0 = !{i64 9118137893752966836}
!1 = !{i64 -1233952984979479474}
!2 = !{i64 4118119865467988422}
!3 = !{i64 5695742013429636198}
!4 = !{i64 7826096018722294096}
!5 = !{i64 -998643382319848445}
!6 = !{i64 5744142236472620586}
!7 = !{i64 -7200156211192534197}
!8 = !{i64 8697529570792962422}
!9 = !{i64 -8842547236111524653}
!10 = !{i64 2755655526841799998}
!11 = !{i64 8623644876362121646}
!12 = !{i64 -7355899746778665416}
!13 = !{i64 -5683099207853529922}
!14 = !{i32 8, !"PIC Level", i32 2}
!15 = !{i32 2, !"RtLibUseGOT", i32 1}
!16 = !{i32 7, !"uwtable", i32 2}
!17 = !{!"rustc version 1.99.1 (58cf8f9c3 2026-10-13)"}
!18 = !{i64 -8428455889319306347}
!19 = !{i64 -4714469101530818364}
!20 = !{i64 5556554986355720341}
!21 = !{i64 -5032768763040225657}
!22 = !{i64 -2031306674162102066}
!23 = !{i64 -7340061420639097117}
!24 = !{i64 -7423679159646315635}
!25 = !{i64 7409136921373146039}
!26 = !{i64 4565380390040987484}
!27 = !{i64 -4420598359052134998}
!28 = !{i64 -249004477653349940}
!29 = !{i64 8891430672583798209}
!30 = !{i64 829468968551850661}
!31 = !{i64 7779443428098473721}
