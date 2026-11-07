# Dialect tooling quality review, round 2

Reviewed head **`419d061e622257815b4285bda61167a9f7a5afaf`** on `job/quality-dialect`.
Batch range: `main..job/quality-dialect`, with main at
`de5f939bc070357f224bb3e6f1d61e8ea7784acd`; this round reviews only the fixes
`4f6be75..419d061`: `8d41d71`, `51fd510`, and evidence `a588093`/`419d061`,
against [round 1](2026-11-06-quality-dialect-r1.md). The unchanged 0.2.14 draft
(`22f9ed6`) and contract backlog remain outside this review.

**Verdict: CLEAR. No P0/P1 findings.**

- **P1-1 / b-dialect-spec-du2: fixed.** At `tools/dialect03_witnesses.py:28`,
  unexpected emission failures are re-raised before the unavailable second reader.
  Repeated the original invalid-signature/corrupt-binary reproduction with assertions:
  the identical `Fail` survives, the reader is never called, and `Runner.check`
  records `failed`, its original diagnostic, and an empty `blocked_on`.
  The new tests also cover hash/command failures, a recognized unsupported row,
  and successful path return. Static comparison with main and the round-1 head
  confirms that the regression was the unconditional unavailable-reader call.
- **P1-2 / b-dialect-spec-dd9: fixed.** `scripts/dialect_check_v02.py:467` and
  `:664` use an instance dispatcher; `tools/dialect_check_v03.py:21` supplies
  the draft dispatcher. No import-time assignment to `v2.state_check` remains.
  Repeated the original real `r-budget-prefix` scenario in a fresh process:
  after scoped draft import, ISA08, dispatcher identity, and the complete
  non-execution receipt are preserved. Draft budget/fault witnesses and inherited
  `inplace-bound` dispatch pass; changing the expected budget fault to 2 raises
  `Mismatch`. The main/round-1 global mutation would violate this isolation.

Verification used a headless environment, the review-local TMPDIR/CARGO_TARGET_DIR,
and gate-pinned sibling inputs. Commands actually run:

```sh
PYTHONPATH=scripts:tools timeout 120s python3 -m unittest -v test_dialect_v03 test_profile test_failures test_reporting test_quality test_test_runner
PYTHONPATH=scripts:tools timeout 30s python3 -  # asserted original round-1 scenarios described above
timeout 90s python3 scripts/dialect_check_v02.py --family blocker --json .tmp/rev-quality-dialect-r2/tmp/v02-blockers.json
timeout 60s python3 tools/dialect_check_v03.py --family lowering --json .tmp/rev-quality-dialect-r2/tmp/v03-lowering.json
timeout 30s python3 scripts/quality.py
git diff --check 4f6be75..419d061
```

Results: **20 tests passed in 4.254 s; 19/19 published blocker rows; 19/19 draft
lowering rows; ratchet and fix-only whitespace checks passed.** Discovery-only
assertions confirmed 156 default + 33 slow tests, with 189 distinct ids.
The broader `timeout 150s python3 tools/dialect_check_v03.py --family recognise,lowering,hash --json .tmp/rev-quality-dialect-r2/tmp/v03-focused.json`
timed out (exit 124, no report); it is not a passing check. No full gate, sibling
gate, or full v02 run was performed by this reviewer.

Evidence checks: `cmp`, SHA-256 and JSON assertions on the saved
`v02-before-r2.json`/`v02-after-r2.json` confirm identical bytes, 2943 passing rows
each, and digest `2744368bae4ec8b6ab3de33b8e07bce82592af5403affbfd789bb9c0ba5ea7e0`.
The saved coverage totals support the documented **47.71%**. These are inspected
implementer artifacts, separate from the reviewer executions above.

P2+ nits: **b-dialect-spec-0eb** carries forward the remaining **b-dialect-spec-jpi** items: five EOF blank lines in `dialect_analysis.py`, `dialect_check.py`, `dialect_execution.py`, `dialect_ir.py`, `dialect_rewrite.py`, and duplicated opening prose in `dialect_interprocedural.py`, `dialect_memory_witnesses.py`, `dialect_scalar_witnesses.py`; no new fix-diff nits. The stale second-reader docstring is fixed.

Coverage: read closely the entire fix executable/test diff, adjacent emission,
error classification and runner dispatch, and evidence/baseline changes; skimmed
the unchanged numeric baseline. Checked every COMMON anti-slop rule against the
fix diff: no new semantic violation, test weakening, narrowing or owned-path
violation found. The prior round's broader batch review stands.

Provenance: implementer **gpt-6.1-sol**; reviewer **gpt-6.1-sol**, fresh session, D9.
