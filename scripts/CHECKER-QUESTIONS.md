# Checker readings and questions

Each entry records the question, the contract section and the executable reading.
These are findings for the editor; the checker does not modify the spec.

## Q1 — which region operand does `candidates=` identify?

Sections: §1.5, §4.1, example `region-reversible-in-action`.
Question: does “first region operand” mean module text order, or the first call
in a device entry? `@body` calls `reversible(@classical)` before `@top` calls
`adj(@body)`, but the example states `candidates=body`.
Reading taken: first operand in module text order, consistent with §4.1.
Actual set `{classical}`; stated set `{body}`. Filed with label `spec-0.2-finding`
(the issue id is recorded in the progress file). This is a failing check.

## Q2 — section lists versus semicolon-separated clauses

Sections: §1.5; references at lines 1695, 4654, 5953, 5955, 6013.
Reading: comma/dash/and continues a list and inherits its document; a semicolon
starts a new prose clause and an unqualified reference resets to the dialect.
North Star §9.11 resolves to numbered item 11 of its §9 (that document uses a
numbered list rather than subsection headings). The comma-separated `NS §3.2,
§17.1` at line 4654 remains unresolved and is filed as a spec finding.

## Q3 — asm table patterns where exact constraints are unspecified

Sections: §15.2, §20.2, §20.7, D32.
The syscall table supplies exact constraints for k=0…6, so those rows have exact
keys. Other prose rows give mnemonic/pattern defaults and the platform explicitly
postpones its exact inventory to the platform spike. Data files retain these as
`match=mnemonic`, `pattern`, `intrinsic` or `platform-pattern`, with the literal
constraint description. No exact constraint string is invented. The normaliser
uses exact syscall constraints; the section prevails over generated data.

## Q4 — Round-1 normalisation fixes (editor)

Dialect revision 0.2.1: PT2/PT6, packed vector memory, partial limbs, fcmp enum,
returning transfer attributes and GC provenance changed. n-varargs now pushes 32,
not 24. Add n-fcmp differential vectors and state=normalisation-boundaries/fcmp-abi
execution. Existing normaliser expectations must follow the corrected rules; never
remove these examples to restore green. Full baseline already has incomplete families.

## Q5 — Round-1 TDL semantics (editor)

Implement retained compute views, instruction MC, forked branch views, all-code-zero
consumer predicates, clean workspace, deferred channel records, bounded G, inherited
virtual devices and per-K application. New §18.8 TDL/state witnesses and updated tdl-effect
are normative; baseline run-action is unavailable. Full baseline: 1922/1982 passed,
60 failed/blocked. Direct dialect_check_v02.py exits 0 without main; frontend runs it.

## Q6 — Round-1 interface and native adapters (editor)

New checked objects arena-o1, fp-aggregate and entry-stack require carrier, hidden arena
base and snapshot support; entry-stack is explicitly a runtime contract microvector,
not a byte-map of the general replay loop. All three were check/hash/run-oracle verified
with the offline-built Rust interpreter. Add native adapters for fp-aggregate, entry-stack
and n-fcmp. Update seed softfloat.c predicate enum (currently case 8 means ueq, 14 uno;
correct is uno=8, ueq=9, une=14), plus varargs rounded frame size and 0.2.1 version fields.
Implement common all-projection wide delivery, chunked snapshot release, stack backing
replay/adoption, sampled universal budget obligation, and parameterised in-place CC
expansion (inplace-param-quantum now accepts; BLK-3 retired). Candidate-pair witness
accepts with two trap bodies. Never alter spec vectors to fit old checker behavior.

## Q7 — Round-1 R budget/fault and platform (editor)

N34/§17.6 charge before each counted instruction. New BLK-5=ISA-7 requires
blocked:BD-B-ISA7 at typed R fault sites, including r-fault-code. Do not substitute
generic trap code. §20.6 translates kernel and user Sv39 accesses; add the alias
and reverse-state vector. r-budget-prefix, r-fault-code and sv39-kernel-alias
state witnesses require executor adapters; no source effects after first fault.

## Q8 — Final validation boundaries (editor)

All new ISA objects pass check/hash/run-oracle; all LLVM cells parse. Full checker
on the first revised snapshot: 1936/2028 pass, 92 fail/blocked (baseline 60).
The additional vectors intentionally remain obligations, not skips. Most new state/TDL
rows need run-action. Normalisation has stale frame size and no n-fcmp transform;
native adapters have no n-fcmp/fp-aggregate/entry-stack case. fp-aggregate now has
its linkmap companion, but aggregate carrier lifting still needs implementation.
r-fault-code is explicitly runtime/materialised IR: the recogniser must distinguish
normaliser primitives from producer-reserved-name errors, then classify ISA-7.
Final read also fixed Q1's candidates=classical and Q2's semicolon-inherited NS xref,
and added the missing all-guest privilege scope in the old §20.6 paragraph.
Independent clang18/23 runs verify packed i1 lane 7, i129 add/sext, n-fcmp input/output
and ueq/uno ABI values, aggregate packing and replay-adopting allocator contracts.
The dedicated fcmp ABI seed was used because the owned-path boundary forbids changing
the checker-owned old predicate seed; no claim is made that the old seed passes.

Final repeat: full gate 1939/2029 (90 failed/blocked); selected
parse/header/check/hash/run-oracle/xrefs gate 1702/1702. Detailed family counts and
independent validation are in round-1/response.md. Follow-up b-dialect-spec-ofu.

## Q9 — freeze coverage: normalisation witnesses (editor)

New pairs n-lower-widenable, n-defined-zero, n-dynamic-lane, n-byval-copy,
n-rstep-return (R entry f), n-platform-mmio (riscv64-bennett-virt). N12 passes.
N0/N15/N25/N34/N35 expose absent transforms; rmode/platform context must be
consumed for the last two. Keep expected outputs and P-1 intact. Whole gate
2043/2078 passes, 34 failures and one ISA-7 blocked state. Tracked on 1jb.
