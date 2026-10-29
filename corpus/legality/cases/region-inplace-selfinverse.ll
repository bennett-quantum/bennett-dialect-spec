; CASE: region-inplace-selfinverse
; HAZARD: mergefunc on __bennett_inplace(g, ginv, env) where g is self-inverse (xor with a constant), so a front end emits g and ginv with identical bodies; ginv is never called by anyone (only referenced through the marker); also __bennett_compute(f, use, env) with f referenced twice
; INPUTS: 0..63
; EXPECT: probe

target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef)
declare void @__bennett_qfree(ptr noundef)
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef)
declare void @__bennett_gate2(i32 noundef, ptr noundef, i64 noundef, ptr noundef, i64 noundef)
declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef)
declare void @__bennett_inplace(ptr noundef, ptr noundef, ptr noundef)
declare void @__bennett_compute(ptr noundef, ptr noundef, ptr noundef)

%env = type { ptr, i64 }

; x <- x xor k, applied as X gates on the set bits of k (k is classical, from env)
define internal void @xor_k(ptr %e) {
entry:
  %hp = getelementptr inbounds %env, ptr %e, i32 0, i32 0
  %h = load ptr, ptr %hp
  %kp = getelementptr inbounds %env, ptr %e, i32 0, i32 1
  %k = load i64, ptr %kp
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %next ]
  %bit = lshr i64 %k, %i
  %b = and i64 %bit, 1
  %set = icmp ne i64 %b, 0
  br i1 %set, label %flip, label %next
flip:
  call void @__bennett_gate(i32 2, ptr %h, i64 %i)
  br label %next
next:
  %i.next = add i64 %i, 1
  %d = icmp eq i64 %i.next, 4
  br i1 %d, label %out, label %loop
out:
  ret void
}

define internal void @xor_k_inv(ptr %e) {
entry:
  %hp = getelementptr inbounds %env, ptr %e, i32 0, i32 0
  %h = load ptr, ptr %hp
  %kp = getelementptr inbounds %env, ptr %e, i32 0, i32 1
  %k = load i64, ptr %kp
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %next ]
  %bit = lshr i64 %k, %i
  %b = and i64 %bit, 1
  %set = icmp ne i64 %b, 0
  br i1 %set, label %flip, label %next
flip:
  call void @__bennett_gate(i32 2, ptr %h, i64 %i)
  br label %next
next:
  %i.next = add i64 %i, 1
  %d = icmp eq i64 %i.next, 4
  br i1 %d, label %out, label %loop
out:
  ret void
}

define internal void @use_parity(ptr %e) {
  %hp = getelementptr inbounds %env, ptr %e, i32 0, i32 0
  %h = load ptr, ptr %hp
  call void @__bennett_gate2(i32 3, ptr %h, i64 0, ptr %h, i64 3)
  ret void
}

define i64 @case_entry(i64 %x) {
entry:
  %e = alloca %env
  %h = call ptr @__bennett_qalloc(i64 0, i64 4)
  %hp = getelementptr inbounds %env, ptr %e, i32 0, i32 0
  store ptr %h, ptr %hp
  %k = and i64 %x, 15
  %kp = getelementptr inbounds %env, ptr %e, i32 0, i32 1
  store i64 %k, ptr %kp
  call void @__bennett_inplace(ptr @xor_k, ptr @xor_k_inv, ptr %e)
  %k2 = lshr i64 %x, 2
  store i64 %k2, ptr %kp
  call void @__bennett_compute(ptr @xor_k, ptr @use_parity, ptr %e)
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 3)
  call void @__bennett_qfree(ptr %h)
  %z = zext i1 %m to i64
  ret i64 %z
}
