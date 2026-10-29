# Independent pre-flight seeds (dialect 0.2.1)

These fixtures are checker inputs, independent of bennett-runtimes and bennett-arith
(CLAUDE.md rule 5). They implement the exercised contract rows, rather than importing
implementation code across that boundary. `python3 scripts/dialect_check.py --family
seeds,native` builds and tests them headlessly with clang 18 and 23.

| Seed | Contract | Example(s) needing it |
|---|---|---|
| runtime.c: allocation table and fault | §17.1/§17.5, lift.alloc/free | listsum; rung4-mini fault |
| runtime.c: ss_push/ss_pop | §17.3 zero-filled aligned frames | n-shadow-stack, n-varargs |
| runtime.c: memmove/memset/memcmp | N26 | n-memintrinsics; varargs copies |
| runtime.c: ctpop_i32 | N27 | n-intrinsics |
| runtime.c: EH state, catch-all personality subset, may_throw | N28/§14.4 | n-eh (input uses an independently compiled C++ throw) |
| contexts.c: setjmp record, longjmp pseudo-exception | N29/§14.5 | sjlj-two-frames (native input uses system setjmp) |
| contexts.c: fiber switch record | N30/§14.6 | fiber-pingpong (native input uses system ucontext) |
| softfloat.c: binary64 add/mul/cmp, integer conversions, f32 extension | §13.1 | n-fcmp, fcmp-abi, n-fmuladd; FP normalisation fixtures |
| musl/src/math/exp.c, log.c and tables/helpers | §13.4 | n-libm; rung-8 libm seed obligation of §21.4 |
| devices.c: console/entropy/clock buffers | §11.3 | effect-console-*, rung8-mini, TDL effect |
| runtime.c: replayed stack adoption and allocator offset | §8.5/§17.3 | entry-stack, entry-backing |
| coherence.c: Cl/M/Co shadow and chunk observation | TDL-2/TDL-11 | partial-observe, classical-event-application |
| coherence.c: three-level Sv39 walk | §20.6 | sv39-kernel-alias |
| runtime.c: seven-argument syscall row | §15.5 | n-asm, asm-musl-syscall |

The context seeds expose the memory transitions of materialised code; resume and
unwind dispatch belong to the N29/N30 caller transform. They do not replace native
setjmp/ucontext with inert stubs. The native C inputs use their platform operations.
The EH fixture implements the demonstrated catch-all subset; it is not a general
C++ personality or the production ABI implementation.

`softfloat.c` uses integer arithmetic only. The seed self-test uses native floating
point as an independent comparison for 100,000 bit-pattern pairs; it is outside the
materialised seed. The musl files retain their upstream C form for N32 to rewrite
in a materialised build; their native anchor tests explicitly disable contraction.

Source provenance: musl 1.2.5, downloaded from
https://musl.libc.org/releases/musl-1.2.5.tar.gz . Archive SHA-256:
`a9a118bbe84d8764da0ea0d28b3ab3fae8477fc7e4085d90102b8596fc7c75e4`.
The selected source files are unchanged. `musl/COPYRIGHT` is retained.
`musl-compat/math.h` is a small build header to avoid glibc private-name collisions;
it does not supply a host libm implementation.
