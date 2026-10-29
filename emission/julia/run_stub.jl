using Libdl
dlopen(joinpath(@__DIR__,"libbennett_stub.so"), RTLD_GLOBAL|RTLD_NOW)
include("routes.jl")
h = rA_alloc(UInt64(4)); println("A alloc -> ", h)
println("B alloc -> ", rB_alloc(UInt64(2)))
println("D alloc (llvmcall) -> ", rD_alloc(UInt64(3)))
println("measure A,B,D = ", rA_measure(h), " ", rB_measure(h), " ", rD_measure(h))
rF_ctrl(h, 0.5)   # cfunction const + body -> llvmcall gate
rF2_ctrl(h, 0.5)
