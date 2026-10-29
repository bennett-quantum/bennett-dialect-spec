# Route G: GPUCompiler.jl (native target) — closest thing to "Julia -> LTO-able module".
using GPUCompiler, LLVM
module TestRuntime
    signal_exception() = return
    malloc(sz) = C_NULL
    report_oom(sz) = return
    report_exception(ex) = return
    report_exception_name(ex) = return
    report_exception_frame(idx, func, file, line) = return
end
struct P <: GPUCompiler.AbstractCompilerParams end
GPUCompiler.runtime_module(::GPUCompiler.CompilerJob{<:Any,P}) = TestRuntime
const H = Ptr{Cvoid}
const LIB = joinpath(@__DIR__, "libbennett_stub.so")
kB(h::H) = ccall(:__bennett_gate, Cvoid, (UInt32, H, UInt64), UInt32(1), h, UInt64(0))
kA(h::H) = ccall((:__bennett_gate, LIB), Cvoid, (UInt32, H, UInt64), UInt32(1), h, UInt64(0))
kM(h::H) = ccall(:__bennett_measure, Bool, (H, UInt64), h, UInt64(0))
kV(h::H) = @ccall __bennett_ctrl_v(h::H, 0::UInt64, C_NULL::Ptr{Cvoid}, 8::UInt64; 1::Cint, 2.5::Cdouble)::Cvoid
kL(h::H) = Base.llvmcall(("""declare void @__bennett_gate(i32, ptr, i64)
define void @entry(ptr %0) {
  call void @__bennett_gate(i32 1, ptr %0, i64 0)
  ret void
}""", "entry"), Cvoid, Tuple{H}, h)
outdir = joinpath(@__DIR__, "ir_gpucompiler"); mkpath(outdir)
for (nm, f) in (("kB",kB),("kA",kA),("kM",kM),("kV",kV),("kL",kL))
  for (opt,tag) in ((false,"unopt"),(true,"opt"))
    try
      src = GPUCompiler.methodinstance(typeof(f), Tuple{H})
      cfg = GPUCompiler.CompilerConfig(GPUCompiler.NativeCompilerTarget(), P(); kernel=false, always_inline=false)
      job = GPUCompiler.CompilerJob(src, cfg)
      io = IOBuffer()
      GPUCompiler.code_llvm(io, job; optimize=opt, strip=false, dump_module=true)
      write(joinpath(outdir, "$nm.$tag.ll"), take!(io))
    catch err
      write(joinpath(outdir, "$nm.$tag.ERROR.txt"), sprint(showerror, err, catch_backtrace()))
      println("FAIL $nm $tag: ", first(split(sprint(showerror, err), '\n')))
    end
  end
end
