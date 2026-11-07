# Dialect tooling quality review, round 1

Reviewed: all 14 commits in `main..job/quality-dialect`, first `d3517ff`, with main at
`de5f939bc070357f224bb3e6f1d61e8ea7784acd` and head **`972dadc4defdaf04b26ca919f5480e5da077a3f9`**.
Contract beads and the unchanged 0.2.14 draft text are outside this review.

**Verdict: BLOCK.** No P0; two P1 findings.

- **P1-1 — b-dialect-spec-du2:** `tools/dialect03_witnesses.py:41`, reached from `:28`.
  Every `d.Fail` during `cc.emit()` now reaches an unconditional `Unavailable` before
  `absent()` can classify its diagnostic. Invalid signatures, unrelated hash failures or
  broken interpreter commands become `blocked / SECOND-READER-PIN`, losing the original
  defect. Previously, the second-reader probe returned and `absent()` rethrew unexpected
  errors. This is separate from the existing second-reader pin backlog. Preserve unexpected
  failures and add a negative control. The focused reproduction below produced a blocked row
  for `invalid signature or corrupt reference binary`; calling `absent()` with that error
  preserved the original `Fail`.
- **P1-2 — b-dialect-spec-dd9:** `tools/dialect03_witnesses.py:368`, imported by
  `tools/dialect_check_v03.py:17`. The requested explicit composition retains the global
  assignment `v2.state_check=state_check`. Importing the draft checker inside the new ISA09
  profile scope permanently replaces the v02 dispatcher. After scope exit, the same real
  v02 `r-budget-prefix` state check changes from its valid non-execution receipt to
  `TypeError: 'NoneType' object is not subscriptable`, although the active profile is 0.8.
  Move draft state dispatch into explicit Runner03 composition and test state isolation.
  This is retained monkeypatch behavior the refactor was required to remove.

Both scenarios were run with the command below (headless environment and job-local TMPDIR).
The output showed a valid receipt before draft import, profile 0.8 plus TypeError afterward,
and then the incorrectly blocked unexpected-error row:

```sh
PYTHONPATH=scripts:tools timeout 30s python3 - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import dialect_check as d
import dialect_check_v02 as v
from dialect_profile import ISA09, profile, using_profile
text = d.SPEC.read_text(); blocks = d.extract_blocks(text); v.initialise(blocks)
block = next(b for b in blocks if b['attrs'].get('state') == 'r-budget-prefix')
with TemporaryDirectory() as tmp:
    runner = v.Runner(blocks, text, Path(tmp), {'state'})
    print(v.state_check(runner, block)['executed'])
    with using_profile(ISA09):
        import dialect_check_v03
    print(profile().isa, v.state_check.__module__)
    try: v.state_check(runner, block)
    except TypeError as error: print(type(error).__name__, str(error))
    import dialect03_witnesses as w
    problem = d.Fail('fixture: invalid signature or corrupt reference binary')
    try: w.absent(problem, 'fixture')
    except d.Fail as error: print(type(error).__name__, str(error))
    runner.selected = set()
    with patch.object(w.cc, 'emit', side_effect=problem):
        runner.check('isa09', 'malformed-fixture', 'fixture',
                     lambda: w.build(runner, 'malformed', [], {}))
    print(runner.rows[-1])
PY
```

Verification: `PYTHONPATH=scripts:tools timeout 120s python3 -m unittest -v test_rehash test_quality test_test_runner test_profile test_reporting test_failures test_pins test_dialect_v03` passed **22 tests**. `PYTHONPATH=scripts:tools:corpus/legality/harness timeout 150s python3 -` loading `test_dialect_check`, `test_interpreter_snapshot`, `test_headless`, `test_dialect_0213`, `test_dialect_0214` and selecting `partition(suite)[0]` passed **69 tests in 14.747 s**; 32 slow tests from those suites remain gate-selected. `timeout 150s python3 tools/dialect_check_v03.py --family recognise,lowering,hash --json .tmp/rev-quality-dialect-r1/tmp/v03-focused.json` passed **184/184 semantic rows**. `timeout 30s python3 scripts/quality.py` passed, reporting zero litter and the documented spec-bound identifier exception. No full gate or sibling gate was run.

Main-side comparison: extracted function/class ASTs match main except the intended `ref_hash` ABI profile and deleted `legacy_main`; top-level bindings differ only at pinned sibling paths. Static global-name inspection found no missing extracted imports. New anchor/fail-loud tests were checked against main-side code: the old rehasher lacked anchor refusal, and malformed value-set analysis returned TOP. The validator deletion is explicitly authorized by D7; slow-test selection remains in gate.toml. Plan items 9–11 were checked: ratchet wired and exercised, local HANDOFF deleted with README redirect, all COMMON anti-slop patterns checked; the evidenced failure-path and composition defects above block clearance.

P2+ nits: **b-dialect-spec-jpi** — five extra EOF blank lines reported by `git diff --check`; duplicated opening docstring prose in three renamed witness modules; stale second-reader docstring at `tools/dialect03_witnesses.py:38`.

Coverage: read closely the entire executable/test/config diff, anchor data and changed ledgers; AST-compared the moved checker bodies and reviewed their imports/globals; skimmed the numerical baseline table and deleted historical receipts/progress, reading the new quality methodology closely. No spec/emission semantics changed.

Provenance: implementer **gpt-6.1-sol**; reviewer **gpt-6.1-sol**, fresh session, D9.
