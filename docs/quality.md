# Tooling quality baseline

Recorded 2026-11-06. This covers Python tooling, not a new contract or a consumer conformance claim.

The default command is `python3 scripts/run_tests.py`. The fresh instrumented default run passed
150 tests in 64.276 s (runner timing). The final uninstrumented run passed **151 tests in 38.26 s wall**
(37.848 s runner timing), measured with `/usr/bin/time -f %e timeout 180 python3 scripts/run_tests.py`.
The gate also runs `python3 scripts/run_tests.py --slow`; none of the 33 slow tests was deleted.
The combined suite passed 179 tests in 703.888 s before the final additional unit cases; those added
cases were checked separately. Slow checks include native LLVM matrices, ISA execution and O3 traces.
Snapshot unit fixtures record builds without compiling unrelated Rust crates.

The v02 spec checker passed 2943/2943 before and after the concept split. The JSON reports were
byte-identical, SHA-256 `2d35a530735b4bcd931ed9359f4c9c0ed36bfc6264f7b364c8351e311568d62a`:

```sh
timeout 900 python3 scripts/dialect_check_v02.py --json .tmp/quality-dialect/before.json
timeout 1200 python3 scripts/dialect_check_v02.py --json .tmp/quality-dialect/after-split.json
```

These are **472 semantic rows + 2471 bookkeeping rows**. The latter are the xrefs, parse,
coverage-ledger and inventory families. Semantic rows include spec-labelled verdicts; they are not
472 independent semantic oracles. Some ledger rows retain nested execution evidence without
counting it a second time. The final identifier cleanup intentionally changes evidence item codes;
its 78 publication-ledger rows were re-executed using the completed unchanged-spec semantic receipt,
and all passed. The draft 0.3 lowering family also passed 19/19 via
`python3 tools/dialect_check_v03.py --family lowering`.

All sibling reads resolve from `gate.toml` through the gate layout or its cached pinned checkouts.
The resolver rejects a missing pin, wrong HEAD or modified tracked files. In particular, the ISA
source pin is `c1d13200acb08af4922535f5a15a1ab872b78b41`; tests do not use a moving sibling checkout.
The full push gate is reserved for merge-time orchestration.

## Coverage

**46.43%** statement-and-branch coverage in the fresh default suite, using coverage.py 7.17.2.
This is the measured fast-suite scope, not an assertion about the full spec/matrix gate.
The report counted 4790/9696 statements and 2081/5104 branch exits covered. Test modules and the
snapshot build recorder are excluded from the denominator. Exact commands (headless environment,
project-local TMPDIR, and pinned sibling cache):

```sh
COVERAGE_FILE="$PWD/.tmp/quality-dialect/coverage-final" timeout 180   .tmp/quality-dialect/venv/bin/python -m coverage run --branch   --source=scripts,tools,corpus/legality/harness   --omit='*/test_*,*/interpreter_test_support.py' scripts/run_tests.py
COVERAGE_FILE="$PWD/.tmp/quality-dialect/coverage-final"   .tmp/quality-dialect/venv/bin/python -m coverage json   -o .tmp/quality-dialect/default-coverage.json
```

The five lowest modules in that report tie at 0%. Their execution is retained outside the default:

| Module | Reason and retained evidence |
|---|---|
| `scripts/dialect_0212_contract.py` | Whole-run inherited ledger; both complete v02 runs and final 78-row ledger check passed. |
| `scripts/dialect_0212_vectors.py` | Native numerical/allocation fixtures plus ISA boundary calls, executed by the spec gate and final ledger check. |
| `scripts/dialect_atomic_witnesses.py` | LLVM/native/ISA matrix; `test_round6_execution` is in the passing slow suite. |
| `scripts/dialect_boundaries.py` | Native/ISA lifecycle and boundary execution; retained slow cases passed, and renamed stack helper was rechecked. |
| `scripts/dialect_driver.py` | Native/reversible platform scenarios; `test_driver_platform_scenarios` passed in the slow suite. |

## Structure and hygiene

`python3 scripts/quality.py --snapshot` measures every tracked Python file in scripts/, tools/ and
corpus/legality/harness/, including tests. The JSON below records each file's function lengths,
cognitive-complexity mass and trivial-wrapper count. Length includes the complete function body;
`over_N` is a cumulative count. Cognitive mass is a documented local estimator: one plus current
nesting for if/conditional expressions, loops, handlers, matches and comprehensions, plus one for
each extra boolean operand; function entry resets nesting. It is not a vendor complexity score.
A trivial wrapper is a single return forwarding exactly the function's positional arguments to a call.
The gate compares total and per-file metrics, including wrappers, against this repository's own
baseline. New files are measured too. Baseline refreshes are explicit reviewable changes; no threshold
or automatic baseline rewrite is used.

Totals: 762 functions; maximum 295 lines; 132 over 25, 47 over 50, 14 over 100, 3 over 200, 0 over 300.
Cognitive mass 12332; trivial wrappers 3. No function exceeds 300 lines.

The litter scan checks the git index for bytecode, caches, logs, lock files, backups and
LAST-RUN/PROGRESS files: **0 tracked**. The identifier grep checks non-test Python/C/JSON tooling,
excluding generated corpus reports: **1 spec-bound exception**. That is `brt-vbi` in a comment of
`scripts/0214_runtime_instances.c`, whose bytes are bound by SHA-256
`6f3383869a903ac96e45f20dabf61b90708d91a5da84a86b0ac55ead8ab1199b` in both spec tracks.
Changing those bytes needs a reviewed spec digest update; tracked as **b-dialect-spec-75q**.
All mutable tooling identifiers now use capability/item codes. Historical round modules and C helpers
have concept names. The obsolete `legacy_main` and import-hook patch module are deleted.

Independent hash anchors are in `corpus/hash-anchors.json`: hand-transcribed acyclic L1 increment
envelopes for ISA 0.8 and 0.9, derived from §9.2 and checked with both hashlib and sha256sum.
Rehash refuses input drift, executor drift, or a missing anchor/fence before writing any spec bytes.
The rehasher cannot update the anchor file.

Open tooling work: **b-dialect-spec-cxf**, pin and test the optional second admission reader for
unsupported draft 0.3 rows (now explicit blocked evidence); **b-dialect-spec-2qq**, independent
recognizer/normalizer labels in round 2. Contract P0/P1 beads, spec text and emission bytes were
outside this change and remain untouched. Critical verdict/gate changes require the programme's
fresh review/council; this implementer does not claim review clearance.

<!-- quality-baseline -->
```json
{
  "files": {
    "corpus/legality/harness/run.py": {
      "complexity": 1305,
      "functions": 89,
      "max_lines": 295,
      "over_100": 2,
      "over_200": 1,
      "over_25": 20,
      "over_300": 0,
      "over_50": 6,
      "wrappers": 0
    },
    "corpus/legality/harness/test_checks.py": {
      "complexity": 13,
      "functions": 16,
      "max_lines": 20,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "corpus/legality/harness/test_controls.py": {
      "complexity": 4,
      "functions": 1,
      "max_lines": 12,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "corpus/legality/harness/test_execution.py": {
      "complexity": 1,
      "functions": 2,
      "max_lines": 10,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "corpus/legality/harness/test_fixes_v3.py": {
      "complexity": 6,
      "functions": 27,
      "max_lines": 22,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "corpus/legality/harness/test_frontend.py": {
      "complexity": 1,
      "functions": 1,
      "max_lines": 21,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "corpus/legality/harness/test_headless.py": {
      "complexity": 4,
      "functions": 1,
      "max_lines": 23,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "corpus/legality/harness/test_runtime.py": {
      "complexity": 5,
      "functions": 8,
      "max_lines": 27,
      "over_100": 0,
      "over_200": 0,
      "over_25": 1,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "corpus/legality/harness/test_seeds.py": {
      "complexity": 4,
      "functions": 1,
      "max_lines": 12,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/dialect_0211.py": {
      "complexity": 18,
      "functions": 2,
      "max_lines": 31,
      "over_100": 0,
      "over_200": 0,
      "over_25": 2,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/dialect_0211_contract.py": {
      "complexity": 20,
      "functions": 5,
      "max_lines": 14,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/dialect_0212_contract.py": {
      "complexity": 8,
      "functions": 2,
      "max_lines": 27,
      "over_100": 0,
      "over_200": 0,
      "over_25": 1,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/dialect_0212_vectors.py": {
      "complexity": 45,
      "functions": 2,
      "max_lines": 60,
      "over_100": 0,
      "over_200": 0,
      "over_25": 1,
      "over_300": 0,
      "over_50": 1,
      "wrappers": 0
    },
    "scripts/dialect_0213.py": {
      "complexity": 63,
      "functions": 7,
      "max_lines": 59,
      "over_100": 0,
      "over_200": 0,
      "over_25": 2,
      "over_300": 0,
      "over_50": 1,
      "wrappers": 0
    },
    "scripts/dialect_0214.py": {
      "complexity": 32,
      "functions": 11,
      "max_lines": 23,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/dialect_analysis.py": {
      "complexity": 1279,
      "functions": 48,
      "max_lines": 168,
      "over_100": 1,
      "over_200": 0,
      "over_25": 13,
      "over_300": 0,
      "over_50": 3,
      "wrappers": 0
    },
    "scripts/dialect_arith_request.py": {
      "complexity": 15,
      "functions": 2,
      "max_lines": 28,
      "over_100": 0,
      "over_200": 0,
      "over_25": 1,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/dialect_atomic.py": {
      "complexity": 9,
      "functions": 1,
      "max_lines": 21,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/dialect_atomic_witnesses.py": {
      "complexity": 23,
      "functions": 4,
      "max_lines": 45,
      "over_100": 0,
      "over_200": 0,
      "over_25": 2,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/dialect_boundaries.py": {
      "complexity": 233,
      "functions": 4,
      "max_lines": 159,
      "over_100": 1,
      "over_200": 0,
      "over_25": 1,
      "over_300": 0,
      "over_50": 1,
      "wrappers": 0
    },
    "scripts/dialect_bounds.py": {
      "complexity": 462,
      "functions": 7,
      "max_lines": 83,
      "over_100": 0,
      "over_200": 0,
      "over_25": 5,
      "over_300": 0,
      "over_50": 2,
      "wrappers": 0
    },
    "scripts/dialect_cc.py": {
      "complexity": 74,
      "functions": 6,
      "max_lines": 128,
      "over_100": 1,
      "over_200": 0,
      "over_25": 3,
      "over_300": 0,
      "over_50": 1,
      "wrappers": 0
    },
    "scripts/dialect_check.py": {
      "complexity": 3,
      "functions": 1,
      "max_lines": 5,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/dialect_check_v02.py": {
      "complexity": 554,
      "functions": 46,
      "max_lines": 86,
      "over_100": 0,
      "over_200": 0,
      "over_25": 8,
      "over_300": 0,
      "over_50": 3,
      "wrappers": 0
    },
    "scripts/dialect_driver.py": {
      "complexity": 152,
      "functions": 8,
      "max_lines": 55,
      "over_100": 0,
      "over_200": 0,
      "over_25": 2,
      "over_300": 0,
      "over_50": 1,
      "wrappers": 0
    },
    "scripts/dialect_execution.py": {
      "complexity": 790,
      "functions": 31,
      "max_lines": 230,
      "over_100": 1,
      "over_200": 1,
      "over_25": 9,
      "over_300": 0,
      "over_50": 2,
      "wrappers": 0
    },
    "scripts/dialect_flow.py": {
      "complexity": 2486,
      "functions": 50,
      "max_lines": 122,
      "over_100": 1,
      "over_200": 0,
      "over_25": 10,
      "over_300": 0,
      "over_50": 5,
      "wrappers": 0
    },
    "scripts/dialect_initialisation.py": {
      "complexity": 24,
      "functions": 2,
      "max_lines": 36,
      "over_100": 0,
      "over_200": 0,
      "over_25": 1,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/dialect_interprocedural.py": {
      "complexity": 15,
      "functions": 1,
      "max_lines": 37,
      "over_100": 0,
      "over_200": 0,
      "over_25": 1,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/dialect_ir.py": {
      "complexity": 219,
      "functions": 29,
      "max_lines": 79,
      "over_100": 0,
      "over_200": 0,
      "over_25": 6,
      "over_300": 0,
      "over_50": 1,
      "wrappers": 1
    },
    "scripts/dialect_lifetimes.py": {
      "complexity": 334,
      "functions": 1,
      "max_lines": 156,
      "over_100": 1,
      "over_200": 0,
      "over_25": 1,
      "over_300": 0,
      "over_50": 1,
      "wrappers": 0
    },
    "scripts/dialect_map.py": {
      "complexity": 872,
      "functions": 31,
      "max_lines": 219,
      "over_100": 1,
      "over_200": 1,
      "over_25": 5,
      "over_300": 0,
      "over_50": 2,
      "wrappers": 0
    },
    "scripts/dialect_memory_witnesses.py": {
      "complexity": 7,
      "functions": 1,
      "max_lines": 20,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/dialect_meta.py": {
      "complexity": 167,
      "functions": 10,
      "max_lines": 45,
      "over_100": 0,
      "over_200": 0,
      "over_25": 2,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/dialect_native.py": {
      "complexity": 722,
      "functions": 6,
      "max_lines": 134,
      "over_100": 1,
      "over_200": 0,
      "over_25": 2,
      "over_300": 0,
      "over_50": 2,
      "wrappers": 0
    },
    "scripts/dialect_normalise.py": {
      "complexity": 726,
      "functions": 46,
      "max_lines": 129,
      "over_100": 2,
      "over_200": 0,
      "over_25": 12,
      "over_300": 0,
      "over_50": 6,
      "wrappers": 0
    },
    "scripts/dialect_pins.py": {
      "complexity": 5,
      "functions": 1,
      "max_lines": 19,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/dialect_profile.py": {
      "complexity": 23,
      "functions": 6,
      "max_lines": 12,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 1
    },
    "scripts/dialect_report.py": {
      "complexity": 5,
      "functions": 2,
      "max_lines": 7,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/dialect_rewrite.py": {
      "complexity": 382,
      "functions": 11,
      "max_lines": 156,
      "over_100": 1,
      "over_200": 0,
      "over_25": 3,
      "over_300": 0,
      "over_50": 2,
      "wrappers": 0
    },
    "scripts/dialect_scalar_witnesses.py": {
      "complexity": 38,
      "functions": 3,
      "max_lines": 37,
      "over_100": 0,
      "over_200": 0,
      "over_25": 1,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/dialect_state.py": {
      "complexity": 110,
      "functions": 3,
      "max_lines": 105,
      "over_100": 1,
      "over_200": 0,
      "over_25": 1,
      "over_300": 0,
      "over_50": 1,
      "wrappers": 0
    },
    "scripts/dialect_tdl.py": {
      "complexity": 490,
      "functions": 21,
      "max_lines": 78,
      "over_100": 0,
      "over_200": 0,
      "over_25": 5,
      "over_300": 0,
      "over_50": 3,
      "wrappers": 0
    },
    "scripts/dialect_wide.py": {
      "complexity": 82,
      "functions": 4,
      "max_lines": 81,
      "over_100": 0,
      "over_200": 0,
      "over_25": 1,
      "over_300": 0,
      "over_50": 1,
      "wrappers": 0
    },
    "scripts/interpreter_test_support.py": {
      "complexity": 1,
      "functions": 1,
      "max_lines": 9,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/quality.py": {
      "complexity": 61,
      "functions": 10,
      "max_lines": 22,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/run_tests.py": {
      "complexity": 12,
      "functions": 5,
      "max_lines": 12,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/test_dialect_0211.py": {
      "complexity": 10,
      "functions": 9,
      "max_lines": 15,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/test_dialect_0212.py": {
      "complexity": 35,
      "functions": 5,
      "max_lines": 22,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/test_dialect_0213.py": {
      "complexity": 7,
      "functions": 9,
      "max_lines": 17,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/test_dialect_0214.py": {
      "complexity": 11,
      "functions": 8,
      "max_lines": 22,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/test_dialect_check.py": {
      "complexity": 157,
      "functions": 88,
      "max_lines": 42,
      "over_100": 0,
      "over_200": 0,
      "over_25": 3,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/test_failures.py": {
      "complexity": 0,
      "functions": 3,
      "max_lines": 9,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/test_interpreter_snapshot.py": {
      "complexity": 3,
      "functions": 1,
      "max_lines": 59,
      "over_100": 0,
      "over_200": 0,
      "over_25": 1,
      "over_300": 0,
      "over_50": 1,
      "wrappers": 0
    },
    "scripts/test_pins.py": {
      "complexity": 0,
      "functions": 3,
      "max_lines": 25,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/test_profile.py": {
      "complexity": 0,
      "functions": 2,
      "max_lines": 10,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/test_quality.py": {
      "complexity": 1,
      "functions": 4,
      "max_lines": 12,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/test_reporting.py": {
      "complexity": 1,
      "functions": 1,
      "max_lines": 6,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "scripts/test_test_runner.py": {
      "complexity": 2,
      "functions": 3,
      "max_lines": 14,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "tools/dialect03_rehash.py": {
      "complexity": 50,
      "functions": 8,
      "max_lines": 49,
      "over_100": 0,
      "over_200": 0,
      "over_25": 1,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "tools/dialect03_witnesses.py": {
      "complexity": 119,
      "functions": 26,
      "max_lines": 52,
      "over_100": 0,
      "over_200": 0,
      "over_25": 4,
      "over_300": 0,
      "over_50": 1,
      "wrappers": 1
    },
    "tools/dialect_check_v03.py": {
      "complexity": 30,
      "functions": 5,
      "max_lines": 26,
      "over_100": 0,
      "over_200": 0,
      "over_25": 1,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "tools/test_dialect_v03.py": {
      "complexity": 1,
      "functions": 5,
      "max_lines": 15,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    },
    "tools/test_rehash.py": {
      "complexity": 1,
      "functions": 5,
      "max_lines": 18,
      "over_100": 0,
      "over_200": 0,
      "over_25": 0,
      "over_300": 0,
      "over_50": 0,
      "wrappers": 0
    }
  },
  "identifiers": [
    "scripts/0214_runtime_instances.c:2:brt-vbi"
  ],
  "litter": []
}
```
<!-- /quality-baseline -->
