include(joinpath(@__DIR__, "routes.jl"))
using InteractiveUtils
outdir = joinpath(@__DIR__, "ir"); mkpath(outdir)
const T = Dict{String,Any}(
 "rA_alloc"=>(rA_alloc,(UInt64,)), "rA_gate"=>(rA_gate,(H,UInt64)), "rA_measure"=>(rA_measure,(H,)), "rA_rot"=>(rA_rot,(H,Float64)),
 "rB_alloc"=>(rB_alloc,(UInt64,)), "rB_gate"=>(rB_gate,(H,UInt64)), "rB_measure"=>(rB_measure,(H,)), "rB_rot"=>(rB_rot,(H,Float64)),
 "rC_alloc"=>(rC_alloc,(UInt64,)), "rC_gate"=>(rC_gate,(H,UInt64)), "rC_measure"=>(rC_measure,(H,)), "rC_alloc_lib"=>(rC_alloc_lib,(UInt64,)),
 "rD_alloc"=>(rD_alloc,(UInt64,)), "rD_gate"=>(rD_gate,(H,UInt64)), "rD_measure"=>(rD_measure,(H,)), "rD_rot"=>(rD_rot,(H,Float64)),
 "rD2_gate"=>(rD2_gate,(H,UInt64)), "rD3_gate"=>(rD3_gate,(H,UInt64)),
 "rE_gate"=>(rE_gate,(Ptr{Cvoid},H,UInt64)),
 "rF_ctrl"=>(rF_ctrl,(H,Float64)), "rF2_ctrl"=>(rF2_ctrl,(H,Float64)), "rG_closure"=>(rG_closure,(H,)),
 "rH_ctrl_v"=>(rH_ctrl_v,(H,)), "rH2_ctrl_v"=>(rH2_ctrl_v,(H,)), "rH5_ctrl_v"=>(rH5_ctrl_v,(H,)),
 "rI_table"=>(rI_table,(UInt64,)), "case_B"=>(case_B,(UInt64,)), "case_D"=>(case_D,(UInt64,)), "body"=>(body,(Ptr{Cvoid},)))
for (name,(f,tt)) in sort(collect(T); by=first)
    for (opt,tag) in ((false,"unopt"),(true,"opt"))
        try
            io = IOBuffer()
            code_llvm(io, f, Tuple{tt...}; raw=true, dump_module=true, optimize=opt, debuginfo=:none)
            write(joinpath(outdir, "$(name).$(tag).ll"), take!(io))
        catch err
            write(joinpath(outdir, "$(name).$(tag).ERROR.txt"), sprint(showerror, err, catch_backtrace()))
            println("FAIL $name $tag: ", first(split(sprint(showerror, err), '\n')))
        end
    end
end
for (nm,src) in (("rH3_ctrl_v",RH3_SRC),("rH4_ctrl_v",RH4_SRC),("rD0_alloc",RD0_SRC),("rD1_alloc",RD1_SRC))
  try
    eval(Meta.parseall(src))
    f = getfield(Main, Symbol(nm)); 
    for (opt,tag) in ((false,"unopt"),(true,"opt"))
      try
        io = IOBuffer(); code_llvm(io, f, Tuple{nm=="rH3_ctrl_v" ? H : UInt64}; raw=true, dump_module=true, optimize=opt, debuginfo=:none)
        write(joinpath(outdir,"$nm.$tag.ll"), take!(io))
      catch err2; write(joinpath(outdir,"$nm.$tag.ERROR.txt"), sprint(showerror,err2)); println(nm," ",tag," codegen err: ", first(split(sprint(showerror,err2),'\n'))) end
    end
  catch err; write(joinpath(outdir,nm*".ERROR.txt"), sprint(showerror,err)); println(nm," err: ", sprint(showerror,err)) end
end
