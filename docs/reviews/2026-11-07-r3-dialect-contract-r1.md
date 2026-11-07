# R-contract review, round 1

Reviewed `main...job/r3-dialect-contract`, base `b6a6e46`, four commits
`155842b` through **`0822cbc72b2dd5299e4b44befed8b81bfcdf4527`**.

**Verdict: CLEAR. P0/P1: none.**

The candidate distinguishes `0.3-r1` from full draft `0.3` and published
`0.2.14`/ISA 0.8 without relabelling old objects. Fault/prefix/reversal rules
agree with ISA 0.9 §§4.9, 5.4, 7.4 and 10; console binding preserves the
published descriptor-close semantics and emitted musl cleanup obligation.
The saved-journal contract agrees with ISA §7.3's tool-profile boundary and
the gate-pinned reference README's saved-tape v1. No narrowing found;
published 0.2.14 is untouched and other draft obligations remain binding and
ungraded. These finite vectors do not establish plugin/musl or whole-rung
acceptance, as the candidate explicitly states.

P2+ nits, one P3 review bead **`b-dialect-spec-iiv`**: execution family absent
from the push gate (`gate.toml:26`); parsed JSON comparisons omit canonical
writer/raw-stdout byte checks (`scripts/dialect_r_contract.py:111–116`);
clarify the code-9 parenthetical and add an explicit-9 vector
(`spec/Bennett-Dialect-Spec-0.3-draft.md:10415`); test-only mutation string
dispatch (`scripts/dialect_r_contract.py:138–145`). Explicit `fault 9` was
independently executed and correctly reports terminal code 9; the existing
all-code preservation requirement resolves the wording's intended behavior.

Verification (all focused tests under `timeout 30s`, headless, reviewer-local
TMPDIR/CARGO_TARGET_DIR, `RUST_TEST_THREADS=4`; no interpreter rebuild):

- `PYTHONPATH=scripts timeout 30s python3 -B -m unittest -v scripts/test_dialect_r_contract.py`:
  **4/4 passed**, including removal, wrong-section, missing-group and legacy-selection negatives.
- `tools/dialect_check_v03.py` via the wrapper below: **4/4 passed**, zero
  failed/blocked. This executes LLVM 18/23 native bytes, exact faults and
  0/1/2 source budgets, reset, identity negatives, saved/cancelled journals
  and seven replay mutations plus duplicate-key rejection. Sampled stderr
  independently confirms ABI mismatch, replay mismatch and duplicate-key
  reasons; each exits 1 without stdout JSON.
- The four `clauses()` groups against
  `git show main:spec/Bennett-Dialect-Spec-0.3-draft.md` each fail on their
  missing new clause; the new runner/corpus are absent at main. No branch
  switch or worktree creation.
- `timeout 30s python3 -B scripts/quality.py`: **passed**; tracked litter 0,
  existing identifier exception 1. `git diff --check main...job/r3-dialect-contract`:
  clean. Full gate not rerun, per brief.

Execution used `BENNETT_ISA_REF` pointing to this worktree's existing
`scripts/.isa-ref/source-f6512ca17682d9f66a56/reference-interpreter/target/release/bennett-isa-ref`,
SHA-256 `0a1b83bc2a5855f39c6f329d4c9d7e7b1cc1a983a2c0af2a04154feca6c4e1d3`
(`BENNETT_ISA_REF_SHA256`), built from gate pin
`c1d13200acb08af4922535f5a15a1ab872b78b41`. The scoped, 30-second Python
wrapper redirected only scratch artifacts into the reviewer's owned directory:

```python
import os, sys
from pathlib import Path
sys.path[:0] = ['scripts', 'tools']
import dialect_check_v02 as v2
import dialect_check_v03 as v3
v2.SCRATCH = Path(os.environ['TMPDIR'])
raise SystemExit(v3.main(['--family', 'r-contract', '--json',
    '.tmp/rev-r3-dialect-contract-r1/r-contract.json']))
```

Anti-slop: checked each COMMON rule; no semantics-bearing violation found.
The mutation dispatch is the style nit above. Plan items 9–11: the ratchet
remains registered, existing per-file limits are retained, HANDOFF.md is
retired and README points to the workspace handoff.

Coverage: read closely all 11 changed files, adjacent normative clauses,
ISA fault/device/history/identity/launch/certificate rules and the pinned
saved-tape publication; skimmed broader ungraded draft context, checker
composition and gate/test discovery. No implementation files changed.

Provenance: implementer gpt-6.1-sol; reviewer gpt-6.1-sol, fresh session (D9).
