# Classical R-contract accepted profile

The full compatibility identity is **`0.3-r1`**, targeting ISA **`0.9`**.
This is a named profile of the 0.3 draft under §23, not a publication of the
whole draft or a patch to published 0.2.14. The mapping version remains `0.3`:
the change fixes the dialect's consumer contract, not the §16 map. Marker ABI
`0.2`, normaliser `0.2.8` and descriptor version 2 are retained. The profile was
unanimously council-accepted on 2026-11-07 (accept / core accept, no blocking
findings) in `bennett/docs/council/dialect-r3contract-2026-11-07/round-1/report.md`.
The graded candidate is `0822cbc72b2dd5299e4b44befed8b81bfcdf4527`; its immutable
ISA reference executable has SHA-256
`7b5299262334d1771303b01f9ba8083879ee954dbe1248a3d9fe7e704bbb924b`.

The normative grading boundary is §1.7, with the profile-specific identities
in §19.9 and §23. Only classical R applicability and its CC launch boundary
are accepted as `0.3-r1`. All other clauses remain ungraded and retain their full
obligations. Quantum R, coherent execution, platform work and mixed native
pointer/container launch contracts are not silently removed or declared inert.

The producer/consumer compatibility tuple is explicit: plugin
`dialect-0.3-r1;isa-0.9`, dialect option/module flag `0.3-r1`, ISA header and ABI
`0.9`, mapping `0.3`, build-record dialect/ISA/replay identities, and checked
ISA 0.9 hashes/certificate bindings. `producer.version` binds the build-record
JCS digest through the existing metadata channel. Published 0.2.14 continues
to identify ISA 0.8 objects. Relabelling an old envelope or retaining its hash
does not migrate it; a selected track requires fresh materialisation and all
dependent identities. No new ISA field is invented.

`SPEC_VERSIONS.toml` remains the exact published-full-dialect pin pair
`dialect = "0.2.14"` / `isa = "0.8"`; this publication does not replace either
pin or introduce a profile-registry schema. The accepted `0.3-r1` / ISA `0.9`
profile is indexed separately in `spec/README.md`. The council's muse-6
two-track registry suggestion remains follow-up work.

Typed R faults follow ISA §§4.9/10, not a generic trap: exact effective code,
one terminal record, no values or caller successor, unchanged failing-step
state and the entire reversible prefix preserved. Source-step counters remain
pre-instruction instrumentation, including return boundaries. Tool fuel is
separate. Fault-zero means effective code 4; nonzero program-defined codes
retain all 64 bits. Failed forward execution does not flush or reverse itself.

Console binding preserves §11.2's published close clarification: descriptor
liveness is ordinary reversible runtime memory, while the ISA byte sink stays
available to other descriptors. Normal C main return executes musl exit/stdio
cleanup exactly once, including a final buffer without a newline. No executor
invented flush/close effect is permitted. Tape entries correspond to successful
nonempty write vectors, not printf calls.

The replay identity is **`saved-tape-v1`**, adopting the gate-pinned reference
publication's tool interface (`bennett-isa-spec` at
`c1d13200acb08af4922535f5a15a1ab872b78b41`,
`reference-interpreter/README.md`, “Saved-tape profile v1”). ISA §7.3 explicitly
leaves persisted journal interchange to a versioned replay profile. The saved
journal includes successful effects subsequently cancelled by uncall; the
active ISA tape does not. Replay validates each candidate before commit,
rejects missing/mismatching/trailing input, and never substitutes a source
fault for a replay-validation error. Object, input, entropy, host replies and
budget identities remain separate, mandatory inputs.

The four new corpus groups use the existing 0.3 checker via a small family
registration in the shared runner. They provide clause-retention checks and
finite independent execution evidence: typed fault codes/failed-prefix reset,
version-dependent hashes/stale identity rejection, native formatted bytes and
descriptor-close errors, ISA console atomicity/reset, and valid/corrupt saved
journals. Native C uses the host implementation as an independent byte oracle;
the ISA fixtures are explicitly hand-written boundary programs. Neither is
evidence that the plugin has compiled musl vfprintf, that a production runtime
implements the close wrapper, or that either executor has completed the whole
rung. Those acceptance rows remain with the producer/executor/conformance
owners. Passing `--family r-contract` cannot grade the whole draft.

The council accepted the named compatibility identity and clause boundary,
confirmed the build-record metadata binding without a new ISA schema, and
adopted saved-tape-v1 as the profile's replay contract. Contract acceptance
does not establish completion of rung 3 on either executor. Bare `0.3` remains
draft, not graded; all evidence limits above still apply.
No ISA expressibility blocker was found for classical R. If one is identified,
§25.1 must name its exact required change and use `blocked:`, never `reject:`.
