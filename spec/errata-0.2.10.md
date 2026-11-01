# Binding interpretations of accepted dialect 0.2.10

Published with draft 0.2.12, 2026-11-01. Accepted text at `023f5a771a814270634db3be9cfde88ded69f975`, spec SHA-256 `d4f3c1a88391cc147f8c8fa4f80f82852e3ebe6f880610fc16cd5151f33d7206`, is unchanged; consumer pins remain valid. These interpretations resolve ambiguity in that text; new 0.2.12 ABIs/accuracy requirements are identified separately and are not retroactive ABI changes.

## mkb — §§5.2, 7.2, 12.2 N0

**N0 and resolution order.** Before testing the forwarding-thunk predicate or freezing candidates, the plugin MUST apply the N0 passes of §12.2 to the virtual device bodies used by S2; §7.2 resolution then uses those bodies, and §7.3 hashes their materialised closures.

The plugin MUST retain A(S) for every original source function or alias whose address reaches the region operand, dispatching that address to its post-N0 resolved candidate even when N0 removes the forwarding call; a declaration remaining after N0 is still F(8), but an intrinsic call removed by N0 MUST NOT turn its containing defined body into an external candidate.

## jjr — §§16.9, 17.1

The thin malloc body in §16.9 is a specialised witness whose calls all request 16 bytes. ISA allocation itself is exactly byte-bumping, not aligned; C malloc still owes its target ABI alignment. The general wrapper rounds its requested extent and inserts explicit charged padding allocations when an intervening runtime primitive leaves the next address unaligned, identically in both builds. This resolves the example-versus-C-ABI ambiguity without altering ISA §7.1.

## lbq — §§11.2–11.3, 14.7, 19.2

**Console syscall framing.** For virtual stdout/stderr, runtimes MUST implement `writev` by validating the vector count and total length before the first effect, then emitting one `console.write` per nonempty vector in source order (zero-length writes emit no record), returning the total byte count; the descriptor ABI limits are 0..1024 vectors and total at most target SSIZE_MAX, with invalid counts/overflow returning EINVAL and a null nonempty vector table returning EFAULT.

The console shim MUST return ENOTTY for `ioctl(TIOCGWINSZ)`, ESPIPE for seeking, and success for closing a virtual stdout/stderr descriptor, with no extra device effect or terminal metadata; this close releases no host resource and does not disable the virtual byte sink.

**Model history.** R console writes MUST use only the ISA effect tape, while L model state is ordinary reversible memory initialised from descriptor bindings, private and discarding only under the oracle rules of §11.3; action console capacity exhaustion MUST fault before mutation under TDL-12, and a standalone native-model test undo log MUST NOT substitute for either tier's history. No second production model-history ABI is required.

**Process context.** Before entering `<sym>`, the driver/runtimes preparation MUST establish a static single-thread musl process context with the supplied argc/argv/envp bytes, a null-terminated argv and envp, `environ`, program name, initial fenv and the libc/stdio state needed by the linked program; comparison-only Linux `_start` is permitted, but Linux ELF crt/TLS/auxv entry is not required in device tiers.

For a C `main` entry, the runtimes entry wrapper MUST treat normal return as `exit(status)`, running registered exit handlers and flushing stdio exactly once under §14.7 before the launch stub catches the exit pseudo-exception; explicit `exit` follows that same path, and `_Exit` bypasses handlers/flush as §14.7 specifies.

## 0na — §§3.1, 17.7, 19.5

The “nobody: primitives” ownership row applies to production bitcode before ISA lowering, not native comparison support implementing those primitives after materialisation. Such support must preserve device layout and history. Draft 0.2.12 §19.5 publishes the new v1 layout transport ABI; that spelling is not imposed retroactively on 0.2.10. The existing memory/fault outcomes and North Star definedness classifiers are not waived by UBSan-only support.

## dfd — §§13.1, 13.5

The explicit exact-conversion and correct-rounding guarantees take priority over APFloat implementation fallbacks. PPCDoubleDouble denotes high+low, not the legacy consecutive-106-bit approximation. A low component may not be discarded when the exact sum is representable in the destination. Sparse-tail loss and intermediate unsigned-low saturation are not permitted by the named-format reference. Draft 0.2.12 §13.1 makes canonical-pair rounding and flags explicit; no claim that the current arith publication already meets these guarantees is made.

## 1av — §§13.4–13.5

“No correct-rounding claim” does not authorise an arbitrary deterministic non-numerical substitute for the named operation or waive the specified IEEE flags. The accepted text does not quantify its numerical error. The one-local-ulp carrier bound and precise constrained accuracy/flag policy in draft 0.2.12 are NEW requirements, not retroactive assertions that 0.2.10 contained a numeric bound or that measured sweeps prove a full-domain bound.

## z7u — §13.1 arbitrary-format row

“Format named by metadata” means the LLVM major’s named interpretation MDString and its format/carrier semantics, not an unbounded user-created APFloat precision/exponent schema. LLVM 23 Intrinsics.td and LangRef define to(value, format, rounding, saturation) and from(bits, format). Draft 0.2.12 publishes NEW concrete carrier operand spellings and a static request/manifest protocol; those new ABI details are not claimed to have existed in 0.2.10.
