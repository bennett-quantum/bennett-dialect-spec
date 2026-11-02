# Binding interpretations of dialect 0.2.12

Published 2026-11-02. Text of draft 0.2.12 at `c775e6d458006fde143f2bf8ec62f07b034fb431`, spec SHA-256 `cfcce70e84ead8a05924c0921f13fc9cb477fdd71f5448c7f6f357ea91349e83`, is unchanged; the full version string, map 0.2.9 and consumer pins remain valid. These interpretations clarify that text without changing any reference result. Draft 0.3 carries the same text in §§5.1, 5.2 and 24.

## 5u3 — §§5.1, 5.2, 24 (council run `contract-5u3-2026-11-02`, round 1 sol and codex accept; `accept-4ht-recheck-2026-11-02` round 1 PASS; muse accept in `accept-muse-batch-2026-11-02`; bead `b-dialect-spec-5u3`)

**§5.1, after K.** The reference bounds INT atoms as above; it imposes no additional
cardinality bound on pointer-offset sets or memory intervals. Implementers
MAY use exact symbolic sets, shared interval relations and SCC
acceleration instead of enumerating represented offsets or slots.
All reference sets and byte/representation-width distinctions must be
preserved for verdicts, candidate sets and dispatch domains. A coarser
summary is not the reference result merely because it is sound for
aliasing. An unfinished analysis reports an unfinished build with the
rule and exhausted implementation resource, not a source rejection,
completed verdict or run-time fault for a valid input.

**§5.2, after the least-fixpoint paragraph.** In a pure modular-translation inclusion SCC, if every cycle transfer is
an unfiltered fixed displacement at one bit width W and preserves one
base/provenance coordinate, close the generated displacements as a
subgroup of Z/(2^W). For a single self-cycle of stride s, each seed a
denotes the coset a modulo gcd(s,2^W). Union distinct seed cosets. For
multiple vertices, retain vertex-specific path displacements; do not
merge their seed coordinates. For edges u→v labelled d_uv,
choose root-to-vertex path displacements p_v and let
g=gcd(2^W,{p_u+d_uv−p_v}). A seed a at u contributes
{a−p_u+p_v+kg mod 2^W} at v. Union contributions from all seeds.
Apply the same rule to a memory relation
only when every transfer preserves the complete storage interval and
representation width and all PT6–PT8 read/overlap results are identical
to the represented individual slots. Retain every ROOT and FN alternative
explicitly. Otherwise use the original rules or another exact method.
PT2's pointer-index width and preserved high pointer bits still apply;
this rule does not replace them by unrestricted full-pointer addition.

**§24.** Analysis representation/acceleration is implementation policy; the
default result is the exact §5 least fixpoint, including existing K=4096
INT abstraction. Time or memory caps do not alter that result. A report
of unfinished analysis keeps the remaining implementation obligation open.
