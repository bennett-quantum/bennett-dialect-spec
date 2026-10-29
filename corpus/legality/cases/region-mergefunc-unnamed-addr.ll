; CASE: region-mergefunc-unnamed-addr
; HAZARD: mergefunc on two externally visible unnamed_addr region functions with identical bodies (rustc marks every function unnamed_addr and runs MergeFunctions with -mergefunc-use-aliases): mergefunc RAUWs the second region with the first, so __bennett_ctrl receives @oracle_key1 on both paths, and @oracle_key2 survives only as a thunk (or, with -mergefunc-use-aliases, an alias)
; INPUTS: 0..31
; EXPECT: probe

target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare ptr @__bennett_qalloc(i64 noundef, i64 noundef)
declare void @__bennett_qfree(ptr noundef)
declare void @__bennett_gate(i32 noundef, ptr noundef, i64 noundef)
declare void @__bennett_gate2(i32 noundef, ptr noundef, i64 noundef, ptr noundef, i64 noundef)
declare zeroext i1 @__bennett_measure(ptr noundef, i64 noundef)
declare void @__bennett_ctrl(ptr noundef, i64 noundef, ptr noundef, i64 noundef, ptr noundef)

; two semantically different regions (oracle for key 1 / key 2) that happen to compile to the same body
define void @oracle_key1(ptr %e) unnamed_addr {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  call void @__bennett_gate2(i32 3, ptr %h, i64 0, ptr %h, i64 1)
  call void @__bennett_gate(i32 7, ptr %h, i64 1)
  call void @__bennett_gate2(i32 3, ptr %h, i64 0, ptr %h, i64 1)
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  ret void
}

define void @oracle_key2(ptr %e) unnamed_addr {
  %h = load ptr, ptr %e
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  call void @__bennett_gate2(i32 3, ptr %h, i64 0, ptr %h, i64 1)
  call void @__bennett_gate(i32 7, ptr %h, i64 1)
  call void @__bennett_gate2(i32 3, ptr %h, i64 0, ptr %h, i64 1)
  call void @__bennett_gate(i32 1, ptr %h, i64 0)
  ret void
}

define i64 @case_entry(i64 %x) {
entry:
  %e = alloca ptr
  %q = call ptr @__bennett_qalloc(i64 0, i64 1)
  %h = call ptr @__bennett_qalloc(i64 0, i64 2)
  store ptr %h, ptr %e
  %b = and i64 %x, 1
  %c = icmp eq i64 %b, 0
  br i1 %c, label %k1, label %k2
k1:
  call void @__bennett_ctrl(ptr %q, i64 0, ptr @oracle_key1, i64 32, ptr %e)
  br label %join
k2:
  call void @__bennett_ctrl(ptr %q, i64 0, ptr @oracle_key2, i64 32, ptr %e)
  br label %join
join:
  %d = and i64 %x, 2
  %cd = icmp ne i64 %d, 0
  br i1 %cd, label %direct, label %done
direct:
  call void @oracle_key2(ptr %e)
  br label %done
done:
  %m = call zeroext i1 @__bennett_measure(ptr %h, i64 0)
  call void @__bennett_qfree(ptr %h)
  call void @__bennett_qfree(ptr %q)
  %z = zext i1 %m to i64
  ret i64 %z
}
