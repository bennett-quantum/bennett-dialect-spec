# Each route is a small function; emission.jl dumps IR for each.
const LIB = joinpath(@__DIR__, "libbennett_stub.so")
const H = Ptr{Cvoid}

# Route A: ccall((:sym, "lib"), ...) with library (literal path via const tuple)
rA_alloc(n::UInt64) = ccall((:__bennett_qalloc, LIB), H, (UInt64, UInt64), UInt64(0), n)
rA_gate(h::H, i::UInt64) = ccall((:__bennett_gate, LIB), Cvoid, (UInt32, H, UInt64), UInt32(1), h, i)
rA_measure(h::H) = ccall((:__bennett_measure, LIB), Bool, (H, UInt64), h, UInt64(0))
rA_rot(h::H, th::Float64) = ccall((:__bennett_rot, LIB), Cvoid, (UInt32, H, UInt64, Float64), UInt32(3), h, UInt64(1), th)

# Route B: ccall(:sym, ...) no library
rB_alloc(n::UInt64) = ccall(:__bennett_qalloc, H, (UInt64, UInt64), UInt64(0), n)
rB_gate(h::H, i::UInt64) = ccall(:__bennett_gate, Cvoid, (UInt32, H, UInt64), UInt32(1), h, i)
rB_measure(h::H) = ccall(:__bennett_measure, Bool, (H, UInt64), h, UInt64(0))
rB_rot(h::H, th::Float64) = ccall(:__bennett_rot, Cvoid, (UInt32, H, UInt64, Float64), UInt32(3), h, UInt64(1), th)

# Route C: @ccall macro (no library, and with library)
rC_alloc(n::UInt64) = @ccall __bennett_qalloc(0::UInt64, n::UInt64)::H
rC_gate(h::H, i::UInt64) = @ccall __bennett_gate(1::UInt32, h::H, i::UInt64)::Cvoid
rC_measure(h::H) = @ccall __bennett_measure(h::H, 0::UInt64)::Bool
rC_alloc_lib(n::UInt64) = @ccall LIB.__bennett_qalloc(0::UInt64, n::UInt64)::H

# Route D: Base.llvmcall((module_ir, "entry"), ...) with a declare in the module
function _m(decl, params, body, ret="void")
    return ("""$decl
define $ret @entry($params) {
$body
}""", "entry")
end
rD_alloc(n::UInt64) = Base.llvmcall(("""declare ptr @__bennett_qalloc(i64, i64)
define ptr @entry(i64 %0) {
  %r = call ptr @__bennett_qalloc(i64 0, i64 %0)
  ret ptr %r
}""", "entry"), H, Tuple{UInt64}, n)
rD_gate(h::H, i::UInt64) = Base.llvmcall(("""declare void @__bennett_gate(i32, ptr, i64)
define void @entry(ptr %0, i64 %1) {
  call void @__bennett_gate(i32 1, ptr %0, i64 %1)
  ret void
}""", "entry"), Cvoid, Tuple{H,UInt64}, h, i)
rD_measure(h::H) = Base.llvmcall(("""declare zeroext i1 @__bennett_measure(ptr, i64)
define zeroext i1 @entry(ptr %0) {
  %r = call zeroext i1 @__bennett_measure(ptr %0, i64 0)
  ret i1 %r
}""", "entry"), Bool, Tuple{H}, h)
rD_rot(h::H, th::Float64) = Base.llvmcall(("""declare void @__bennett_rot(i32, ptr, i64, double)
define void @entry(ptr %0, double %1) {
  call void @__bennett_rot(i32 3, ptr %0, i64 1, double %1)
  ret void
}""", "entry"), Cvoid, Tuple{H,Float64}, h, th)
# legacy two-string (declarations, body) form: expected to fail on 1.13 (2nd string taken as entry name)
RD0_SRC = """rD0_alloc(n::UInt64) = Base.llvmcall(("declare ptr @__bennett_qalloc(i64, i64)",
    "%r = call ptr @__bennett_qalloc(i64 0, i64 %0)\nret ptr %r"), Ptr{Cvoid}, Tuple{UInt64}, n)"""
# D1: single-string function-body form with declare inside is not possible; try the body-only form calling an undeclared fn
RD1_SRC = """rD1_alloc(n::UInt64) = Base.llvmcall("%r = call ptr @__bennett_qalloc(i64 0, i64 %0)\nret ptr %r", Ptr{Cvoid}, Tuple{UInt64}, n)"""
# D2: llvmcall with a full function body string (define @entry, declare inside)
rD2_gate(h::H, i::UInt64) = Base.llvmcall(("""
    declare void @__bennett_gate(i32, ptr, i64)
    define void @entry(ptr %0, i64 %1) {
      call void @__bennett_gate(i32 1, ptr %0, i64 %1)
      ret void
    }""", "entry"), Cvoid, Tuple{H,UInt64}, h, i)
# D3: llvmcall with explicit attributes on declaration (what a user could add)
rD3_gate(h::H, i::UInt64) = Base.llvmcall(("""
    declare void @__bennett_gate(i32, ptr, i64) #0
    attributes #0 = { nounwind }
    define void @entry(ptr %0, i64 %1) {
      call void @__bennett_gate(i32 1, ptr %0, i64 %1)
      ret void
    }""", "entry"), Cvoid, Tuple{H,UInt64}, h, i)

# Route E: ccall through a Ptr (function pointer value, e.g. from dlsym at run time)
rE_gate(p::Ptr{Cvoid}, h::H, i::UInt64) = ccall(p, Cvoid, (UInt32, H, UInt64), UInt32(1), h, i)

# Regions: @cfunction with env pointer
struct Env; h::H; i::UInt64; theta::Float64; end
function body(p::Ptr{Cvoid})::Cvoid
    e = unsafe_load(Ptr{Env}(p))
    rD_gate(e.h, e.i)
    return nothing
end
const BODY = @cfunction(body, Cvoid, (Ptr{Cvoid},))
# ctrl via ccall with cfunction pointer; env via Ref
function rF_ctrl(h::H, theta::Float64)
    e = Ref(Env(h, 3, theta))
    GC.@preserve e begin
        ccall(:__bennett_ctrl, Cvoid, (H, UInt64, Ptr{Cvoid}, UInt64, Ptr{Cvoid}),
              h, UInt64(0), BODY, UInt64(8), Base.unsafe_convert(Ptr{Cvoid}, Base.cconvert(Ptr{Cvoid}, e)))
    end
end
# @cfunction inline (literal) inside the function
function rF2_ctrl(h::H, theta::Float64)
    e = Ref(Env(h, 3, theta))
    GC.@preserve e begin
        ccall(:__bennett_ctrl, Cvoid, (H, UInt64, Ptr{Cvoid}, UInt64, Ptr{Cvoid}),
              h, UInt64(0), @cfunction(body, Cvoid, (Ptr{Cvoid},)), UInt64(8), pointer_from_objref(e))
    end
end
# Closure: @cfunction($f, ...) with a closure
function rG_closure(h::H)
    cnt = Ref(0)
    f = (p::Ptr{Cvoid}) -> (cnt[] += 1; nothing)
    cf = @cfunction($f, Cvoid, (Ptr{Cvoid},))
    ccall(:__bennett_ctrl, Cvoid, (H, UInt64, Ptr{Cvoid}, UInt64, Ptr{Cvoid}), h, UInt64(0), cf, UInt64(8), C_NULL)
end

# Variadic
rH_ctrl_v(h::H) = @ccall __bennett_ctrl_v(h::H, 0::UInt64, C_NULL::Ptr{Cvoid}, 8::UInt64; 1::Cint, 2.5::Cdouble, h::H)::Cvoid
rH2_ctrl_v(h::H) = ccall(:__bennett_ctrl_v, Cvoid, (H, UInt64, Ptr{Cvoid}, UInt64, Cint, Cdouble, H), h, UInt64(0), C_NULL, UInt64(8), Cint(1), 2.5, h)
RH3_SRC = "rH3_ctrl_v(h::H) = ccall(:__bennett_ctrl_v, Cvoid, (H, UInt64, Ptr{Cvoid}, UInt64, Cint...), h, UInt64(0), C_NULL, UInt64(8), Cint(1))"
# the proper varargs ccall syntax: (fixed...; var...)
RH4_SRC = "rH4_ctrl_v(h::H) = ccall(:__bennett_ctrl_v, Cvoid, (H, UInt64, Ptr{Cvoid}, UInt64; Cint, Cdouble, H), h, UInt64(0), C_NULL, UInt64(8), Cint(1), 2.5, h)"
# llvmcall variadic
rH5_ctrl_v(h::H) = Base.llvmcall(("""
    declare void @__bennett_ctrl_v(ptr, i64, ptr, i64, ...)
    define void @entry(ptr %0) {
      call void (ptr, i64, ptr, i64, ...) @__bennett_ctrl_v(ptr %0, i64 0, ptr null, i64 8, i32 1, double 2.5, ptr %0)
      ret void
    }""", "entry"), Cvoid, Tuple{H}, h)

# Handle table: Vector of handles indexed by classical value
function rI_table(x::UInt64)
    tab = Vector{H}(undef, 4)
    for k in 1:4; tab[k] = rB_alloc(UInt64(1)); end
    rB_gate(tab[(x & 3) + 1], UInt64(0))
    return nothing
end

# Full case_entry using route B (ccall(:sym)) and route D alternately
function case_B(x::UInt64)
    h = rB_alloc(UInt64(4))
    rB_gate(h, UInt64(0))
    theta = Float64(x) * 0.125
    rB_rot(h, theta)
    r = UInt64(0)
    if rB_measure(h)
        rB_gate(h, UInt64(2)); r = UInt64(1)
    end
    rF_ctrl(h, theta)
    tab = Vector{H}(undef, 4)
    for k in 1:4; tab[k] = rB_alloc(UInt64(1)); end
    rB_gate(tab[(x & 3) + 1], UInt64(0))
    rH2_ctrl_v(h)
    ccall(:__bennett_qfree, Cvoid, (H,), h)
    return r
end
function case_D(x::UInt64)
    h = rD_alloc(UInt64(4))
    rD_gate(h, UInt64(0))
    theta = Float64(x) * 0.125
    rD_rot(h, theta)
    r = UInt64(0)
    if rD_measure(h)
        rD_gate(h, UInt64(2)); r = UInt64(1)
    end
    rF_ctrl(h, theta)
    tab = Vector{H}(undef, 4)
    for k in 1:4; tab[k] = rD_alloc(UInt64(1)); end
    rD_gate(tab[(x & 3) + 1], UInt64(0))
    rH5_ctrl_v(h)
    return r
end
