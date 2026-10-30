# Brief: dialect 0.2.8 → 0.2.9, two findings relayed from the plugin implementer (before council round 8)

Repository `/home/tobias/Projects/bennett-workspace/bennett-dialect-spec` (HEAD 369e237, draft 0.2.8, freeze gate
2731/2731). You are the **sole editor** of the spec **and** the checker **and** the legality corpus runtime for this
pass. The round-5 brief (`docs/briefs/2026-10-30-dialect-round-5-fixes.md`: read-first list, method, exact freeze-gate
command, owned paths, process) still binds. Two findings came from `bennett-plugin` milestone 1 (its gate reproduces
eleven published objects byte-for-byte on LLVM 18 and 23); both are recorded as beads here (`bd list` from the repo
root with `BEADS_HOOK_TIMEOUT=20`; read each bead's full text):

1. **Canonical global numbering** (new bug bead "Dialect §16.3 canonical global numbering: G1 in text vs G0 in the
   atomic-nand example (§12.2)"). §16.3 Layout numbers globals G1, G2, … in link order and the naming table says the
   n-th global is G<n>; the atomic-nand example uses G0 for its only global while binding-clock-read uses G1. These
   names enter ISA interface hashes, so two conformant implementations differ (S0). Decide one starting index
   (keep G1 unless the text elsewhere relies on G0), fix the inconsistent example, and regenerate every affected
   `isa object=` example and hash vector with the reference binary; the checker must execute the regenerated objects.
2. **Corpus trace runtime at ABI v0** (bead b-dialect-spec-566, see the relayed note). `corpus/legality/cases/
   spec-sem2-adj.ll` and `spec-sem2-compute.ll` exit 87 (FAULT host-segv right after ADJ/COMPUTE) on LLVM 18 and 23
   without any plugin because the trace runtime and harness still implement ABI v0 while the cases are ABI 0.2 (the
   new budget argument). §21.1 already lists "the trace runtime and harness at ABI 0.2" as a corpus work item.
   Upgrade `corpus/legality/runtime/` and `harness/run.py` to ABI 0.2 per `spec/bennett_markers.h`; do not change the
   corpus programs; both cases must then exit 0 and their L1–L6 results must be recorded in the corpus results. Keep
   every other case's result unchanged (re-run the whole harness on both majors and compare with the stored results).

Deliverables: spec edit and regenerated examples with checker coverage; the runtime/harness upgrade with the two
cases green on both majors; freeze gate ≥ 2731 with receipts in both PROGRESS files; version 0.2.9; a short
`docs/council/dialect-2026-10-29/round-7/response-addendum.md` in `bennett` listing both items (so the round-8
members see them in the diff with an explanation). Owned paths: `spec/`, `scripts/`, `corpus/`, `SPEC_VERSIONS.toml`,
`.beads/` via `bd`, and the addendum file. Commit by explicit path list with `BEADS_HOOK_TIMEOUT=20` and absolute paths;
never push; headless (never LLVM `-view-*`; TMPDIR under `scripts/.tmp`); no `cd` in compound commands; rule 10.
Final message: commit hashes, the numbering decision and the regenerated hashes, the harness results for both cases
per major, freeze total before → after.
