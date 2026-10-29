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
