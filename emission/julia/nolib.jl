# ccall with a library string that does not exist at codegen time
using InteractiveUtils
f(h::Ptr{Cvoid}) = ccall((:__bennett_gate, "libbennett_does_not_exist"), Cvoid, (UInt32, Ptr{Cvoid}, UInt64), UInt32(1), h, UInt64(0))
code_llvm(stdout, f, Tuple{Ptr{Cvoid}}; raw=true, dump_module=true, optimize=false, debuginfo=:none)
