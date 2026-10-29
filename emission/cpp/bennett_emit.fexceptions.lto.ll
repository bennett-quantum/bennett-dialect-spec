; ModuleID = 'bennett_emit.fexceptions.lto.o'
source_filename = "bennett_emit.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct.env = type { ptr, i64, double }

$__clang_call_terminate = comdat any

; Function Attrs: mustprogress uwtable
define dso_local noundef i64 @case_entry(i64 noundef %0) local_unnamed_addr #0 personality ptr @__gxx_personality_v0 {
  %2 = alloca %struct.env, align 8
  %3 = alloca [4 x ptr], align 16
  %4 = tail call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 4)
  tail call void @__bennett_gate(i32 noundef 1, ptr noundef %4, i64 noundef 0)
  %5 = uitofp i64 %0 to double
  %6 = fmul double %5, 1.250000e-01
  tail call void @__bennett_rot(i32 noundef 3, ptr noundef %4, i64 noundef 1, double noundef %6)
  tail call void @__bennett_gate2(i32 noundef 4, ptr noundef %4, i64 noundef 0, ptr noundef %4, i64 noundef 1)
  %7 = tail call zeroext i1 @__bennett_measure(ptr noundef %4, i64 noundef 0)
  br i1 %7, label %8, label %9

8:                                                ; preds = %1
  tail call void @__bennett_gate(i32 noundef 2, ptr noundef %4, i64 noundef 2)
  br label %9

9:                                                ; preds = %8, %1
  %10 = phi i64 [ 1, %8 ], [ 0, %1 ]
  call void @llvm.lifetime.start.p0(i64 24, ptr nonnull %2) #5
  store ptr %4, ptr %2, align 8, !tbaa !7
  %11 = getelementptr inbounds %struct.env, ptr %2, i64 0, i32 1
  store i64 3, ptr %11, align 8, !tbaa !14
  %12 = getelementptr inbounds %struct.env, ptr %2, i64 0, i32 2
  store double %6, ptr %12, align 8, !tbaa !15
  call void @__bennett_ctrl(ptr noundef %4, i64 noundef 0, ptr noundef nonnull @_ZL4bodyPv, i64 noundef 8, ptr noundef nonnull %2)
  call void @__bennett_ctrl(ptr noundef %4, i64 noundef 1, ptr noundef nonnull @"_ZZ10case_entryEN3$_08__invokeEPv", i64 noundef 8, ptr noundef nonnull %2)
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %3) #5
  %13 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1)
  store ptr %13, ptr %3, align 16, !tbaa !16
  %14 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1)
  %15 = getelementptr inbounds [4 x ptr], ptr %3, i64 0, i64 1
  store ptr %14, ptr %15, align 8, !tbaa !16
  %16 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1)
  %17 = getelementptr inbounds [4 x ptr], ptr %3, i64 0, i64 2
  store ptr %16, ptr %17, align 16, !tbaa !16
  %18 = call ptr @__bennett_qalloc(i64 noundef 0, i64 noundef 1)
  %19 = getelementptr inbounds [4 x ptr], ptr %3, i64 0, i64 3
  store ptr %18, ptr %19, align 8, !tbaa !16
  %20 = and i64 %0, 3
  %21 = getelementptr inbounds [4 x ptr], ptr %3, i64 0, i64 %20
  %22 = load ptr, ptr %21, align 8, !tbaa !16
  call void @__bennett_gate(i32 noundef 1, ptr noundef %22, i64 noundef 0)
  call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr noundef %4, i64 noundef 0, ptr noundef nonnull @_ZL4bodyPv, i64 noundef 8, i32 noundef 1, double noundef 2.500000e+00, ptr noundef %4)
  call void @__bennett_adj(ptr noundef nonnull @_ZL4bodyPv, ptr noundef nonnull %2)
  %23 = call ptr @__bennett_qborrow(i64 noundef 0, i64 noundef 1)
  invoke void @__bennett_gate(i32 noundef 6, ptr noundef %23, i64 noundef 0)
          to label %24 unwind label %32

24:                                               ; preds = %9
  invoke void @_Z9may_throwm(i64 noundef %0)
          to label %25 unwind label %32

25:                                               ; preds = %24
  invoke void @__bennett_gate(i32 noundef 7, ptr noundef %23, i64 noundef 0)
          to label %26 unwind label %32

26:                                               ; preds = %25
  invoke void @__bennett_ctrl(ptr noundef %4, i64 noundef 0, ptr noundef nonnull @_ZL4bodyPv, i64 noundef 8, ptr noundef nonnull %2)
          to label %27 unwind label %32

27:                                               ; preds = %26
  invoke void @__bennett_qfree(ptr noundef %23)
          to label %28 unwind label %29

28:                                               ; preds = %27
  call void @__bennett_qfree(ptr noundef %13)
  call void @__bennett_qfree(ptr noundef %14)
  call void @__bennett_qfree(ptr noundef %16)
  call void @__bennett_qfree(ptr noundef %18)
  call void @__bennett_qfree(ptr noundef %4)
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %3) #5
  call void @llvm.lifetime.end.p0(i64 24, ptr nonnull %2) #5
  ret i64 %10

29:                                               ; preds = %27
  %30 = landingpad { ptr, i32 }
          catch ptr null
  %31 = extractvalue { ptr, i32 } %30, 0
  call void @__clang_call_terminate(ptr %31) #6
  unreachable

32:                                               ; preds = %26, %25, %24, %9
  %33 = landingpad { ptr, i32 }
          cleanup
  invoke void @__bennett_qfree(ptr noundef %23)
          to label %37 unwind label %34

34:                                               ; preds = %32
  %35 = landingpad { ptr, i32 }
          catch ptr null
  %36 = extractvalue { ptr, i32 } %35, 0
  call void @__clang_call_terminate(ptr %36) #6
  unreachable

37:                                               ; preds = %32
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %3) #5
  call void @llvm.lifetime.end.p0(i64 24, ptr nonnull %2) #5
  resume { ptr, i32 } %33
}

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #1

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef) local_unnamed_addr #2

declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef) local_unnamed_addr #2

declare void @__bennett_rot(i32 noundef, ptr noundef, i64 noundef, double noundef) local_unnamed_addr #2

declare void @__bennett_gate2(i32 noundef, ptr noundef, i64 noundef, ptr noundef, i64 noundef) local_unnamed_addr #2

declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef) local_unnamed_addr #2

declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ptr noundef) local_unnamed_addr #2

; Function Attrs: mustprogress uwtable
define internal void @_ZL4bodyPv(ptr nocapture noundef readonly %0) #0 {
  %2 = load ptr, ptr %0, align 8, !tbaa !7
  %3 = getelementptr inbounds %struct.env, ptr %0, i64 0, i32 1
  %4 = load i64, ptr %3, align 8, !tbaa !14
  %5 = getelementptr inbounds %struct.env, ptr %0, i64 0, i32 2
  %6 = load double, ptr %5, align 8, !tbaa !15
  tail call void @__bennett_rot(i32 noundef 1, ptr noundef %2, i64 noundef %4, double noundef %6)
  %7 = load ptr, ptr %0, align 8, !tbaa !7
  %8 = load i64, ptr %3, align 8, !tbaa !14
  tail call void @__bennett_gate(i32 noundef 2, ptr noundef %7, i64 noundef %8)
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #1

declare void @__bennett_ctrl_v(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ...) local_unnamed_addr #2

declare void @__bennett_adj(ptr noundef, ptr noundef) local_unnamed_addr #2

declare ptr @__bennett_qborrow(i64 noundef, i64 noundef) local_unnamed_addr #2

declare i32 @__gxx_personality_v0(...)

declare void @_Z9may_throwm(i64 noundef) local_unnamed_addr #2

declare void @__bennett_qfree(ptr noundef) local_unnamed_addr #2

; Function Attrs: inlinehint mustprogress uwtable
define internal void @"_ZZ10case_entryEN3$_08__invokeEPv"(ptr nocapture noundef readonly %0) #3 align 2 {
  %2 = load ptr, ptr %0, align 8, !tbaa !7
  %3 = getelementptr inbounds %struct.env, ptr %0, i64 0, i32 1
  %4 = load i64, ptr %3, align 8, !tbaa !14
  tail call void @__bennett_gate(i32 noundef 5, ptr noundef %2, i64 noundef %4)
  ret void
}

; Function Attrs: noinline noreturn nounwind uwtable
define linkonce_odr hidden void @__clang_call_terminate(ptr noundef %0) local_unnamed_addr #4 comdat {
  %2 = tail call ptr @__cxa_begin_catch(ptr %0) #5
  tail call void @_ZSt9terminatev() #6
  unreachable
}

declare ptr @__cxa_begin_catch(ptr) local_unnamed_addr

declare void @_ZSt9terminatev() local_unnamed_addr

attributes #0 = { mustprogress uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { inlinehint mustprogress uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { noinline noreturn nounwind uwtable "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { nounwind }
attributes #6 = { noreturn nounwind }

!llvm.module.flags = !{!0, !1, !2, !3, !4, !5}
!llvm.ident = !{!6}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 2}
!4 = !{i32 1, !"ThinLTO", i32 0}
!5 = !{i32 1, !"EnableSplitLTOUnit", i32 1}
!6 = !{!"Ubuntu clang version 18.1.3 (1ubuntu1)"}
!7 = !{!8, !9, i64 0}
!8 = !{!"_ZTS3env", !9, i64 0, !12, i64 8, !13, i64 16}
!9 = !{!"any pointer", !10, i64 0}
!10 = !{!"omnipotent char", !11, i64 0}
!11 = !{!"Simple C++ TBAA"}
!12 = !{!"long", !10, i64 0}
!13 = !{!"double", !10, i64 0}
!14 = !{!8, !12, i64 8}
!15 = !{!8, !13, i64 16}
!16 = !{!9, !9, i64 0}

^0 = module: (path: "bennett_emit.fexceptions.lto.o", hash: (0, 0, 0, 0, 0))
^1 = gv: (name: "case_entry", summaries: (function: (module: ^0, flags: (linkage: external, visibility: default, notEligibleToImport: 1, live: 0, dsoLocal: 1, canAutoHide: 0), insts: 66, funcFlags: (readNone: 0, readOnly: 0, noRecurse: 0, returnDoesNotAlias: 0, noInline: 0, alwaysInline: 0, noUnwind: 0, mayThrow: 1, hasUnknownCall: 0, mustBeUnreachable: 0), calls: ((callee: ^10, tail: 1), (callee: ^6, tail: 1), (callee: ^12, tail: 1), (callee: ^15, tail: 1), (callee: ^9, tail: 1), (callee: ^19), (callee: ^7), (callee: ^20), (callee: ^13), (callee: ^8), (callee: ^18), (callee: ^3)), refs: (^4, ^2, ^14)))) ; guid = 829468968551850661
^2 = gv: (name: "_ZL4bodyPv", summaries: (function: (module: ^0, flags: (linkage: internal, visibility: default, notEligibleToImport: 1, live: 0, dsoLocal: 1, canAutoHide: 0), insts: 10, calls: ((callee: ^12, tail: 1), (callee: ^6, tail: 1))))) ; guid = 1001469975461361572
^3 = gv: (name: "__clang_call_terminate", summaries: (function: (module: ^0, flags: (linkage: linkonce_odr, visibility: hidden, notEligibleToImport: 1, live: 0, dsoLocal: 1, canAutoHide: 1), insts: 3, funcFlags: (readNone: 0, readOnly: 0, noRecurse: 0, returnDoesNotAlias: 0, noInline: 1, alwaysInline: 0, noUnwind: 1, mayThrow: 0, hasUnknownCall: 0, mustBeUnreachable: 1), calls: ((callee: ^5, tail: 1), (callee: ^17, tail: 1))))) ; guid = 1080103601501470593
^4 = gv: (name: "__gxx_personality_v0") ; guid = 1233668236132380018
^5 = gv: (name: "__cxa_begin_catch") ; guid = 2822380080272388849
^6 = gv: (name: "__bennett_gate") ; guid = 2982123004906011917
^7 = gv: (name: "__bennett_ctrl_v") ; guid = 3388239159881652307
^8 = gv: (name: "_Z9may_throwm") ; guid = 3559730199985047526
^9 = gv: (name: "__bennett_measure") ; guid = 3968391300744443354
^10 = gv: (name: "__bennett_qalloc") ; guid = 4673891782026730886
^11 = gv: (name: "llvm.lifetime.start.p0") ; guid = 4736283418132453162
^12 = gv: (name: "__bennett_rot") ; guid = 6169953353981470639
^13 = gv: (name: "__bennett_qborrow") ; guid = 9491372177710512436
^14 = gv: (name: "_ZZ10case_entryEN3$_08__invokeEPv", summaries: (function: (module: ^0, flags: (linkage: internal, visibility: default, notEligibleToImport: 1, live: 0, dsoLocal: 1, canAutoHide: 0), insts: 5, calls: ((callee: ^6, tail: 1))))) ; guid = 11059119917319874433
^15 = gv: (name: "__bennett_gate2") ; guid = 11316789583050174531
^16 = gv: (name: "llvm.lifetime.end.p0") ; guid = 13244677477227836793
^17 = gv: (name: "_ZSt9terminatev") ; guid = 13807749166652787960
^18 = gv: (name: "__bennett_qfree") ; guid = 16633130219932291175
^19 = gv: (name: "__bennett_ctrl") ; guid = 16800917137780716501
^20 = gv: (name: "__bennett_adj") ; guid = 17297851703929373874
^21 = flags: 8
^22 = blockcount: 0
