# Route S: StaticCompiler.jl generate_obj / static_llvm. Records what it does with ccall.
using StaticCompiler
const H = Ptr{Cvoid}
function kS(x::UInt64)
    h = ccall(:__bennett_qalloc, H, (UInt64, UInt64), UInt64(0), x)
    ccall(:__bennett_gate, Cvoid, (UInt32, H, UInt64), UInt32(1), h, UInt64(0))
    r = ccall(:__bennett_measure, Bool, (H, UInt64), h, UInt64(0))
    ccall(:__bennett_qfree, Cvoid, (H,), h)
    return r ? UInt64(1) : UInt64(0)
end
outdir = joinpath(@__DIR__, "ir_staticcompiler"); mkpath(outdir)
try
  StaticCompiler.generate_obj(kS, Tuple{UInt64}, joinpath(outdir), "kS"; strip_llvm=false) |> println
catch err
  write(joinpath(outdir,"generate_obj.ERROR.txt"), sprint(showerror, err, catch_backtrace())); println("generate_obj FAIL: ", first(split(sprint(showerror,err),'\n')))
end
try
  io = IOBuffer()
  r = StaticCompiler.static_llvm(kS, Tuple{UInt64}) 
  write(joinpath(outdir,"kS.static_llvm.ll"), string(r))
catch err
  write(joinpath(outdir,"static_llvm.ERROR.txt"), sprint(showerror, err, catch_backtrace())); println("static_llvm FAIL: ", first(split(sprint(showerror,err),'\n')))
end
