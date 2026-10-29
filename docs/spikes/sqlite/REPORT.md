# Rung-4 feasibility spike: Grover over unmodified SQLite

**Date:** 2026-10-29. **Phase 2** of `bennett/docs/plan/2026-10-29-path-to-north-star.md`.
**Standing rule applied:** no narrowing of north-star scope; every finding is "work needed",
never "out of scope". Written by an Opus subagent; saved and committed by the orchestrator after
checking `results/verify.txt` (0 mismatches everywhere) and the committed result files.

**Read:** north star (NS) §0, §3, §4.2, §5.1, §8; ISA 0.8 §3.3, §3.6, §3.7, §4.2, §5.1–5.4,
§7.1–7.3, §10, §14.3, §16.3; legality findings; phase-0 audit (rows G-12, ISA-11, B-16, O-07).
Dialect draft 0.1 was not treated as a limit.

## 0. Summary

- **Feasible with no ISA change.** Every construct in the oracle's closure maps to ISA 0.8 rows,
  sometimes after work in the dialect, normaliser, runtimes or arith (§5).
- **The database goes in as a VFS file image in an `in` interface region.** Inside the oracle,
  SQLite's own memdb VFS reads pages from it (§5.2(i)). No snapshot entry (G-12) and no
  host-data-by-reference (ISA-11) is needed.
- **Step budget.** B ≈ 2.8–2.9e5 ISA rows per oracle call, almost flat in N: 278k at N = 16,
  282k at 2^10, 290k at 2^20. Heap 182 KB cumulative, depth 21, about 71 KB touched per call.
- **Structure.** At least 92 % of the oracle's execution is identical for every rowid. Only 1.5 %
  of value instances depend on the rowid.
- **Costs (§7).** (a) Exhaustive verification at 2^10: about 1 min to 2 h on 32 cores, depending
  on interpreter speed. (b) Grover at 2^8: seconds to minutes. (c) At 2^20: 1.3e19 Toffoli per
  oracle call under the naive reference step machine, versus about 4e7 with structure recovery.
- **Ranked work items:** §8.

## 1. What was built

| Item | Value |
|---|---|
| SQLite | 3.54.1 amalgamation `sqlite-amalgamation-3540100.zip`, 2,990,966 B, SHA3-256 `92281c86e2957f9b9305890f9ac04204caa7b677cc868dc326d942689df28e30` (published value, verified by `scripts/fetch.sh`), source id `2026-10-16 14:45:20 555e07ef…`. Unpacked to `~/.local/share/bennett-sqlite/3.54.1/src/`; only compiled, never executed. |
| Toolchain | clang/LLVM 18.1.3. Per translation unit `clang -O2 -flto`, then `llvm-link`, then `opt -passes='internalize,lto<O3>'` with only `main` exported: the whole-program link of NS §3.3. |
| SQLite source edits | none |
| `src/` | `rung4.c`/`rung4.h`: host code plus three oracle shapes. `os_shim.c`: OS layer for `SQLITE_OS_OTHER`. `libc_shim.c`: the libc of the closure (profile build). `verify_main.c`. |
| Artefacts | `~/.cache/bennett-sqlite-spike/` (bitcode, .ll, binaries, raw profiles). Summaries in `results/`. |

### 1.1 Program

**Database.** `people(id INTEGER PRIMARY KEY, name TEXT, city TEXT, age INTEGER, score INTEGER)`,
N rows generated deterministically and inserted with a prepared INSERT, then serialised to the
database file image: 4096-byte pages, 40 KiB at 2^10, 33,492,992 B at 2^20. The image is position
independent.

**Predicate (a real SQL query).** The oracle bit is 1 when a row is returned:

```sql
SELECT 1 FROM people WHERE rowid = ?1 AND name LIKE '%an%'
  AND upper(substr(city, 1, 1)) IN ('B', 'L', 'M')
  AND age BETWEEN 25 AND 60 AND (score * 7 + age) % 11 = 3
```

Why it is representative:

- `rowid = ?1` is a B-tree seek keyed by the superposed value: the quantum-addressed memory part
  of rung 4.
- `LIKE` runs the pattern matcher: UTF-8 decoding, case folding, and a backtracking loop whose
  length depends on the row.
- `upper(substr())` calls built-in scalar functions through SQLite's function-pointer table and
  allocates their results.
- `IN` compares text under a collation.
- `BETWEEN` and the modular expression exercise VDBE integer arithmetic with overflow checks, plus
  record decoding (varints, serial types).
- There is no floating point, which is typical of selection predicates. Floating point is still in
  the closure and is handled in §5.

About 1.1 % of rows match: 6 of 256, 13 of 1024, 11,698 of 2^20.

**Oracle shapes:**

| Shape | Entry | Fixed before entry | Inside the oracle |
|---|---|---|---|
| **V1 image (the rung-4 oracle)** | `uint8_t oracle_on_image(img, len, rowid)`; `oracle(rowid)` is the same on the host image | file image bytes and length | open `:memory:`, `sqlite3_deserialize(READONLY)` through memdb, prepare, bind, step, finalize, close |
| V2 prepared | `oracle_prepared(rowid)` | the host's connection and prepared statement (pointer-rich host heap) | bind, step, reset |
| V0 rebuild | `oracle_rebuild(rowid)` | row data in a global | open, CREATE, N INSERTs, then the query |

Return value: 1 match, 0 no match, 2 SQLite error (never observed).

### 1.2 Verification

An independent C re-implementation of the predicate (`ref_match`) agrees with every shape on every
rowid in [0, N+1] for N = 16, 256 and 1024. V2 also agrees on all 1,048,578 rowids at 2^20, and V1
on 257 sampled rowids at 2^20 (`results/verify.txt`). The instrumented profile build re-checks
every profiled call: 0 mismatches across about 12,000 calls. Native cost per call: V1 20–55 µs;
V2 1–3 µs; V0 225 µs at 2^10, growing linearly with N.

## 2. Build flags

All are documented options (sqlite.org/compile.html); `scripts/config.sh`.

| Flag | Why | Kind |
|---|---|---|
| `SQLITE_THREADSAFE=0` | no mutexes or pthreads | effect removal |
| `SQLITE_OMIT_LOAD_EXTENSION` | no dlopen/dlsym | effect removal |
| `SQLITE_OS_OTHER=1` | drops the unix VFS; the app supplies `sqlite3_os_init` and a VFS (`os_shim.c`: no files, deterministic randomness and clock) | effect removal + runtime shim |
| `SQLITE_TEMP_STORE=3` | temp data always in memory | effect removal |
| `SQLITE_DEFAULT_MEMSTATUS=0`, `SQLITE_OMIT_SHARED_CACHE`, `SQLITE_OMIT_DEPRECATED`, `SQLITE_DQS=0` | overhead only (recommended options) | optional |

No run-time `sqlite3_config` is used. Available but unused: `SQLITE_ENABLE_MEMSYS5` with
`SQLITE_CONFIG_HEAP` (allocation inside a static arena), `SQLITE_OMIT_LOCALTIME`, and
`SQLITE_OMIT_JSON` (shrinks indirect-call candidate sets).

## 3. Static inventory

Produced by the `bennett-inventory` pass (`scripts/plugin/BennettSpike.cpp`) and
`scripts/inventory.py` → `results/inventory.json`.

**Closure method (a sound over-approximation):** direct call edges, plus, for each indirect call
site of LLVM function type T, every address-taken function of exactly type T. Sound for defined C:
calling through an incompatible function type is undefined behaviour (C17 6.5.2.2p9), and
compatible C types lower to the same LLVM type under opaque pointers; LLVM never changes the
signature of an address-taken function. Recursion is found with Tarjan SCCs over this graph.

| Root | Reachable functions (defined) | Direct-only closure | Blocks | IR instructions |
|---|---|---|---|---|
| V1 `oracle_on_image` | 1,232 (1,218) | 822 | 49,161 | 262,100 |
| V2 `oracle_prepared` | 1,225 (1,211) | 813 | 48,853 | 260,511 |
| V0 `oracle_rebuild` | 1,233 (1,219) | 823 | 49,172 | 262,156 |

The sound closure is essentially all of SQLite, whatever the query. Dynamically, V1 executes only
288 functions (V2 91, V0 322).

Largest functions:

| Function | Instructions | Blocks | Largest `switch` |
|---|---|---|---|
| `sqlite3VdbeExec` | 12,981 | 2,155 | 182 cases |
| `yy_reduce` | 2,981 | – | 345 cases |
| `sqlite3Pragma` | 5,250 | – | – |
| `sqlite3Select` | 3,741 | – | – |

| Category | V1 closure (static) | Examples / notes |
|---|---|---|
| Loads / stores | 45,713 / 22,852. Loads by width: 1 B 8,301; 2 B 3,345; 3 B 169; 4 B 11,106; 8 B 22,774; 16 B 18. Stores: 4,383 / 2,370 / 38 / 8,213 / 7,813 / 35. | 3-byte and 16-byte widths come from LLVM load combining and SLP vectorisation |
| alloca | 949 static allocas, 31,975 B; 0 dynamic | address-taken locals, `Parse`, `StrAccum` |
| Heap | `sqlite3DbMallocRawNN` 326 call sites, `sqlite3Malloc` 32, `sqlite3Realloc` 15, `sqlite3DbFree` 18 → `xMalloc` (indirect, 1 candidate) → libc malloc/realloc/free (1 site each) | pcache1, lookaside |
| Direct calls | 8,749 sites | |
| Indirect calls | 2,229 sites over 39 types. 593 sites have 1 candidate, 271 have 2–7, 1,247 have 8–40, 45 have more than 40 (maximum 99: SQL scalar functions `void(ptr,i32,ptr)`). 73 sites have 0 candidates (slots never assigned). | table below |
| Floating-point arithmetic | fadd 50, fsub 16, fmul 14, fdiv 29, fcmp 218, fmuladd 10, fptosi/fptoui 111, sitofp/uitofp 93, fpext f32→f64 1. All binary64. 75 functions. | `sqlite3AtoF`, VDBE real arithmetic, date functions, `sum`/`avg`, `%f` printing |
| Floating point, bit-exact moves | fneg 8, fabs 14, loads 212, stores 94, phi 53, bitcast 46; 295 volatile double accesses (Kahan–Babuška–Neumaier `sum()`) | |
| Vectors | about 1,000 instructions (insertelement 454, phi 132, add 106, …) plus 32 `vector.reduce`, in 58 functions; widest is `<4 x ptr>` (256 bit) | vectoriser output in `sqlite3VdbeExec`, `resolveExprStep`, … |
| Varargs | 18 variadic definitions (`llvm.va_start`; `va_arg` is lowered inline by clang, 0 instructions), 952 variadic call sites | `sqlite3MPrintf`, `sqlite3ErrorMsg`, `sqlite3NestedParse` |
| setjmp/longjmp, inline asm, invoke, indirectbr | none | |
| Atomics | 453 relaxed atomic loads/stores (`AtomicLoad`/`AtomicStore` macros, even with THREADSAFE=0) in 186 functions; no rmw/cmpxchg/fence | |
| Intrinsics | memcpy 424, memset 727, memmove 27; lifetime 2,285; assume 6; smax/smin/umax/umin about 200; abs 5; bswap 9; fshl 33; ctpop 6; ctlz 2; fabs 14; fmuladd 10; va_start/va_end 18 each; vector.reduce 32 | |
| switch | 566 (maximum 345 cases) | |
| Other | freeze 62, unreachable 0 | |
| Recursion | Direct-call graph: 57 cyclic SCCs, the largest of 69 (execSql/NestedParse/ALTER/trigger), 46 (expression codegen) and 19 (printf/malloc/error). Including indirect edges: one SCC of 998 functions. | |
| Globals referenced | 954, 58,099 B (46,185 B constant, 11,914 B mutable) | `aBuiltinFunc` 5,184 B holds function pointers; parser tables |
| Register file | 185,860 values, 7.74 Mbit (all locations of the closure) | maximum call arity 13 (608 bits); maximum 17 phis (576 bits) per block |

**External calls of the closure** (call sites): strlen 160, bcmp 33, strcmp 16, memcmp 7,
strncmp 6, strspn 4, strchr 3, memchr 2, strcspn 1, strrchr 1, malloc 1, realloc 1, free 1,
localtime 1. Nothing else remains after the flags: no time, getenv, errno, file, mutex or dl* calls.

**Indirect calls by type:**

| Type | Sites | Candidates | Examples |
|---|---|---|---|
| `i32(ptr)` | 732 | 16 | memdbClose, jsonEach* |
| `void(ptr)` | 510 | 38 | finalizers, destructors |
| `ptr(i32)` | 308 | 1 | sqlite3MemMalloc |
| `i32(i32)` | 177 | 1 | sqlite3MemRoundup |
| `i32(ptr,i64,ptr)` | 78 | 1 | memdbUnfetch |
| `i32(ptr,ptr,i32,i64)` | 66 | 4 | memdbRead/Write, memjrnlRead/Write |
| `i32(ptr,i32,i32,i32)` | 57 | 0 | none (slot never assigned) |
| `i32(ptr,ptr)` | 41 | 63 | Walker callbacks |
| `void(ptr,i32,ptr)` | 4 | 99 | SQL scalar functions |

## 4. Dynamic profile

**Method** (`scripts/plugin` `bennett-prof` pass, `scripts/prof/prof_rt.c`):

- Each oracle call runs in its own `fork()`, so every call starts from the identical memory image.
- In **cold** mode the profiling process never runs SQLite: the image is built in a separate
  builder process, so globals start at their static images (ISA §3.7) and the oracle pays for
  `sqlite3_initialize`.
- The image sits on its own read-only pages, so a write into it would fault.
- The allocator follows ISA §7.1: fixed base, bump allocation, never reclaimed.
- ISA rows are estimated per IR category (`ROW_WEIGHT` in `analyze.py`):

| IR category | ISA rows |
|---|---|
| arithmetic, compare, cast, select, GEP, branch, phi, call, ret | 1 |
| load / store | 2 (boundscheck + access) |
| switch | 3 |
| indirect call | 9 |
| other intrinsics | 2 |
| floating-point operation | 150 |
| memcpy family | 3 + 3 per 8 B |
| lifetime / assume | 0 |

The resulting ratio is 1.24 rows per IR instruction.

| Shape, N | IR instructions (mean) | B = maximum rows | Cumulative heap / peak live | Allocations | Depth | Calls (indirect) | Monotonic location stack (cells) |
|---|---|---|---|---|---|---|---|
| V1 cold, 2^4 | 204,889 | 278,438 | 182 KB / 167 KB | ≤101 | 21 | – | – |
| V1 cold, 2^8 | 206,480 | 282,064 | same | | | | |
| **V1 cold, 2^10** | 206,927 (max 210,621) | **282,349** | 182 KB / 167 KB | 91–101 | 21 | 3,176 (532) | 1,214,248 |
| V1 cold, 2^14 (270 sampled) | 207,873 | 284,293 | | | | | |
| **V1 cold, 2^20 (257 sampled)** | 211,150 | **289,590** | 182 KB | | 21 | | |
| V1 warm, 2^10 (host already initialised SQLite) | 181,204 | 251,108 | | | | 3,021 | |
| V2 prepared, 2^10 / 2^20 | 11,002 / 11,682 | 26,522 / 29,424 | 20 KB | 10 | 12 | 169 (52) | 37,929 |
| V0 rebuild, 2^4 / 2^8 / 2^10 / 2^12 | 0.33M / 1.25M / 4.37M / 17.1M | 0.43M / 1.59M / 5.49M / 21.4M | 151 KB at 2^10, 252 KB at 2^12 | 188 | 25 | 41,666 (4,611) | 16.5M |

Further V1 facts at 2^10:

- Live locations on the stack (Σ R_f): 15,400 cells. Shadow-stack bytes (allocas): 5,496. Native
  stack: 9.2 KB.
- memcpy family: about 470 operations and 49 KB per call.
- Floating-point operations executed: 0 in every shape and rowid.
- Bytes touched per call: 63–76 KB. Union over all 1026 rowids: globals 7.8 KB, heap 50.4 KB,
  image 41 KB (every page), stack 5.1 KB. Intersection over all rowids: globals 7.8 KB, heap
  38.3 KB, image 8 KB, stack 5.0 KB.
- Bytes written into the image: zero.

**Divergence (V1, 2^10):**

- The shortest common block-trace prefix is 35,768 blocks, against traces of 37,198–38,924
  blocks: at least 92 % is identical. Open, deserialize, schema parse and prepare do not depend on
  the rowid.
- Every rowid has a distinct trace (1026 traces).
- 907 of the 4,688 executed blocks have rowid-dependent execution counts, worth about 14.4k rows.
- Per-instance differential taint (the k-th execution of each site compared against a
  middle-rowid reference): 2,375 of 158,332 value instances (1.5 %) and 563 address instances
  differ. At 2^20 the figures are 4,253 and 925.
- Where the divergence lives: `patternCompare`, `btreeParseCellPtr`/`getCellInfo`, the B-tree
  binary search in `sqlite3BtreeTableMoveto`, the record copy in OP_Column, and page-cache teardown
  (`pcache1Truncate` hashing superposed page numbers).
- Padding every allocation to 512 B changes none of this: the divergence is positional (cell
  offsets inside page buffers) and control-dependent (allocation counts), not caused by allocation
  sizes.

## 5. Mapping to ISA 0.8

### 5.1 By category

| Category | ISA expression | Work needed |
|---|---|---|
| Integer arithmetic, compare, select, cast | `lift.binop/icmp/select/cast`, `lift.div` with DIV0/SDIV faults (§4.2) | normaliser: strip poison flags (NS §3.2) |
| Integer intrinsics (min/max/abs/bswap/fshl/ctpop/ctlz), freeze, lifetime, assume | rows after expansion | normaliser rules [dialect] |
| Vectors (about 1,000 instructions, up to 256 bit) | ISA types are `iN` with N ≤ 128 (§3.3) | normaliser scalarisation [dialect] |
| Loads and stores, including 3-byte and 16-byte widths | `lift.load/store.iN`, N a multiple of 8 up to 128, with an inherent inrange check giving `FAULT_UB_MEMFAULT` (§4.2, §7.2); the interface region is dispatched by address range (§7.2) | none beyond lifting |
| Atomics (relaxed), volatile | plain `lift.load/store` | normaliser sequentialisation (NS §3.2) [dialect] |
| memcpy/memset/memmove intrinsics | no block-copy row | lower to a runtime lproc reached by `lift.call` [dialect, runtimes]; optional ISA row E4 |
| Heap | malloc/realloc/free → shim → `lift.alloc`/`lift.free` (§4.2, §7.2). `heap_limit` must be at least the cumulative 182 KB, since storage is never reclaimed; about 101 allocations; pre-entries are pinned globals (§3.7) | allocator shim [runtimes]; or memsys5 over a global arena (no alloctab use) |
| alloca (static only) | addressable allocas need memory: either `lift.alloc` per frame (cumulative) or a shim-managed shadow stack (NS §3.2), 5.5 KB | normaliser + runtimes |
| Direct calls and recursion (SCCs up to 69 functions, depth 21) | `lift.call`/`lift.ret` with depth fault (§3.7). The stack is monotonic: `stack_limit` ≥ Σ R_f over all dynamic calls = 1.21M cells (V1) | none; cost item E1 |
| Indirect calls | `lift.call` is static and `qjumpr` stays inside one function (§4.2) → compare-and-branch dispatch to static `lift.call`s | function-address encoding and dispatch [plugin, dialect], §5.2(ii) |
| Varargs | `lift.call` needs exact parameter widths (§3.3) | normaliser: caller spills the variadic arguments into a block; `va_start` builds an x86-64 va_list with gp_offset 48 / fp_offset 176, so clang's inline `va_arg` always reads `overflow_arg_area` [dialect]. Executed here: `sqlite3MPrintf`, `sqlite3_mprintf`, `sqlite3_snprintf`, `sqlite3_config` |
| Floating point | soft-float lprocs (NS §3.2) | [arith] (§5.2(iii)) |
| switch (566, up to 345 cases) | compare trees, or a label table plus `qjumpr` (labels are canonical indices, §3.6) | plugin lowering |
| Zero-candidate indirect call sites | `fault FAULT_UB_TRAP` | plugin |
| Globals (58 KB; function pointers inside) | `layout.globals` images (§7.2, §9.1) | function-address encoding in data images [plugin] |
| SQLite error path | the region wrapper calls `__builtin_trap()` on error → `FAULT_UB_TRAP`; target is 1 bit | rung-4 wrapper (user code) [driver/dialect] |

### 5.2 Explicit answers

**(i) How the database reaches the oracle.**

*Route A, the V1 image route (recommended, no ISA change).*

- Oracle signature: `oracle (x: wire[20] in) (tgt t: wire[1]) (fault f: wire[4]) (mem db: region[25,8] in) (args len: i64)`.
- The host builds the database anywhere (natively, by any means), serialises it to the file image,
  pads it with zeros from 33,492,992 B to 2^25 B, and loads it with `bennett_qreg_prepare` into a
  `qreg[2^28]`, which binds to `region[25,8]` under §3.3.
- The C pointer parameter `img` is `lift.addr @db`, passed to lprocs as a parameter, exactly as in
  §16.3 Example 2.
- memdb reads 2–5 pages per call with memcpy from the region and never writes it (role `in`;
  measured).
- Cost: B ≈ 2.9e5 rows, almost independent of N.
- B-16 requirements: polyvariant cloning (a native host copy and the lifted device closure);
  device globals start from static images, so the oracle performs its own `sqlite3_initialize`
  (+11 % B); no host address crosses into the oracle, so no address mapping is needed; function
  pointers in global images use the plugin's encoding.
- The executor may treat the region as classical data (QROM). This is extensional (T6); hint E5.
- Variant A′: the same image as a link-time global image. Same cost, but the database is fixed at
  build time.

*Route B, rebuild inside the oracle from a global row image (V0).* B ≈ 5.2k rows per row: 5.5e6 at
2^10, about 5.5e9 at 2^20. The heap grows with the page cache (≥ 33.5 MB at 2^20, so H ≥ 26). No
ISA change, but about 20,000× B at 2^20. Not recommended.

*Route C, snapshot of a host-prepared statement (V2).*

- B ≈ 2.7–2.9e4 rows (10× smaller than A).
- The entry state is the host heap plus the mutable globals (12 KB) at host addresses. Under ISA
  0.8 this works through the O-07 replay/copy prologue, but needs G-12 to be efficient.
- Route C′ needs no ISA change: the host allocator shim places SQLite's arena at the device layout
  base (NS §3.2 deterministic layout; the prototype shim already maps at a fixed base); the arena
  (about 0.2 MB after open + deserialize + prepare) is passed as an `in` region at that base
  (SQLite may write it; it is restored by the construction); the oracle copies 12 KB of mutable
  globals from a second region at entry (about 4.5k rows).
- C′ requirements: an arena allocator rather than `lift.alloc` (so `free` never hits pinned
  entries); function-address encoding equal to comparison-link addresses (B-16: device dispatch
  maps an address to the clone); identical layouts in native and device builds.
- Under structure recovery, routes A and C cost about the same number of gates, because A's extra
  work is rowid-invariant (§7). So C′ is an optimisation of B and of verification time, not a
  requirement.

**Verdict:** G-12 and ISA-11 are not needed for rung 4.

**(ii) Indirect calls in lifted code.** Every address-taken function gets an encoding equal to its
address in the driver's comparison link (NS §3.2), used in `lift.const` for code constants, in
global data images (`aBuiltinFunc`, VFS/io/pcache method tables), and for function-pointer
comparisons and `ptrtoint`. A call site loads the pointer and runs a `lift.icmp.eq` + `qbranch`
tree over its candidate set (type-based and sound: ≤ 99 candidates, typically 1–38), with a static
`lift.call @f_i` per leaf; 0 candidates → trap. Cost about 2⌈log₂k⌉+1 rows per call; 532 dynamic
indirect calls per V1 call. Candidates enlarge the index space n (≈ 324k rows), which only matters
for the unstructured step machine. No ISA change (confirms R2). Optional E3: `lift.callr a [@f…]`.

**(iii) Floating point.** Static floating point in 75 functions; executed: 0 for this query, all
shapes, every rowid. The normaliser rewrites to bennett-arith binary64 lprocs: fadd, fsub, fmul,
fdiv, fcmp (all predicates), fptosi/fptoui to i32/i64, sitofp/uitofp from i8/i32/i64, fpext
f32→f64; `fmuladd` is split. fneg/fabs/loads/stores/phi/bitcast stay bit-exact; volatile is
meaningless under soft-float and is dropped. Formats: binary64 plus one binary32 load, all covered.
This adds to the static index space only. [arith]

**(iv) libc / external → runtime shim.**

| External | Shim | Executed in V1? |
|---|---|---|
| malloc/realloc/free | bennett-runtimes allocator | yes |
| strlen, strcmp, strncmp, strchr, strrchr, strspn, strcspn, memcmp, bcmp, memchr | libc-shims: plain C, lifted like user code; prototype in `src/libc_shim.c` | strlen, strcmp, strchr, strrchr, strcspn, memcmp |
| memcpy/memmove/memset (intrinsics) | runtime lproc | yes |
| localtime | libc-shims: UTC-only deterministic; unreached here, otherwise `FAULT_EFFECT_UNMODELLED` until the shim exists | no |
| OS layer | `os_shim.c` VFS `bennett-nofs` as a runtimes component | – |

The host-only externals (snprintf, printf, …) are outside the oracle closure.

**(v) Effects during the query and how each is handled.**

| Effect | Treatment |
|---|---|
| File I/O | none. memdb (`memdbOpen/Read/Lock/Unlock/FileSize/FileControl/Access/FullPathname/Close` executed) is plain memory code over the region: the "in-memory VFS over quantum-addressed memory" of rung 4 |
| Temp files | removed by `TEMP_STORE=3` |
| Mutex | removed by `THREADSAFE=0` |
| dlopen | removed by `OMIT_LOAD_EXTENSION` |
| unix VFS (open/fcntl/mmap/getpid/time) | removed by `OS_OTHER` |
| Randomness and clock | reachable but not executed; the shim returns deterministic constants (in the coherent tier, classical values fixed before entry) |
| Atomics | sequentialised |
| Heap | virtualised as oracle memory |
| `sqlite3_log` | no callback installed, so nothing happens |
| errno, getenv | absent |

No device model is needed in the coherent tier.

**(vi) ISA changes.** None required. Efficiency candidates for 0.9, on evidence only:

- **E1:** a uniform cell width `W_cell` = 128 (because of i128 locations) makes the monotonic
  location stack 1.21M × 128 bits ≈ 155 Mbit per call; per-function cell widths would cut this by
  3–4×.
- **E2:** the uniform per-step frame (about 740 bits × B ≈ 235 Mbit).
- **E3:** an indirect call row.
- **E4:** a block-copy row.
- **E5:** a classical-content hint for `in` regions (non-semantic, enables QROM).
- **G-12** remains useful for general snapshots (rung 7), not for rung 4.

## 6. Audit cross-check

- **G-12:** not needed; route A, confirmed by measurement.
- **ISA-11:** not needed; no host memory by reference.
- **B-16:** polyvariant cloning plus function-address encoding in data images. For route C′ the
  encoding must equal the comparison-link addresses.
- **O-07:** the replay prologue is unnecessary with route A.

## 7. Cost (assumptions in `scripts/cost.py`; output `results/cost.json`)

**Assumptions:** B margin 1.10; fault register F = 4; interpreter speed 1e5–1e7 rows/s per core,
32 cores; each basis input costs 2B rows (forward plus prefix reversal); Toffoli costs: 64-bit add
or compare, compute + uncompute = 128; predicated move = 64; i64 multiply = 20,000 (Bennett.jl v1
BENCHMARKS: i32 multiply 5,024); QROM over D classical items ≈ 2D Toffoli; a select or write over D
quantum words of b bytes ≈ 2D(1+8b). Target: `example-surface-code-d17` (illustrative, made-up
numbers), ccx = 170 time units, cx = 17.

**(a) Exhaustive oracle check at N = 2^10.** The domain covers every x (2^10), t (2) and e (2^4):
32,768 inputs × 6.2e5 rows = 2.0e10 rows; on 32 cores 64 s at 1e7 rows/s, 10.6 min at 1e6, 1.8 h at
1e5. F_B(x) does not depend on t or e, so one run per x with checked XOR structure is 32× cheaper:
2 s / 20 s / 3.3 min. At 2^8: 16 s / 2.6 min / 26 min.

**(b) End-to-end Grover at N = 2^8.** M = 6, θ = 0.154, k = 5 iterations. Branch enumeration:
256 runs per oracle application (the |−⟩ target is shared), 1,280 runs, 7.9e8 rows; on 32 cores
2.5 s / 25 s / 4.1 min. The diffusion operator on 256 amplitudes is negligible; the state stays
clean because of prefix reversal.

**(c) N = 2^20.** Iterations: 7 for the real M = 11,698; 804 for M = 1.

*Reference construction* (ISA §3.6/§5.2 literal, no structure recovery): n = 324k-row index space
(P = 19), B = 3.19e5, H = 18 (256 KiB mem), image region A = 25, A_tab = 11. Qubits ≈ 6.9e8:

| Component | Qubits |
|---|---|
| image region | 2.7e8 |
| B step frames | 2.4e8 |
| monotonic location stack | 1.7e8 |
| register file | 7.7e6 |
| mem | 2.1e6 |

Toffoli per step ≈ 2.1e13, dominated by one-hot address dispatch over 2^18 + 2^25 cells for each of
68.6k static memory rows. Per oracle call 1.3e19; Grover total 9.3e19 (M = 11,698) or 1.1e22
(M = 1), i.e. 1.8e24 time units. This is the reference semantics, not a compilation target.

*Structure-recovered* (per-instance differential taint; the invariant prefix is precomputed
classically; only divergent instances are coherent; superposed accesses use their observed
address-set sizes, and page reads use QROM over 8,177 pages):

- Per oracle call (compute + uncompute) ≈ 4.0e7 Toffoli: memory 1.84e7 (pcache teardown hashing
  8.6e6, OP_Column record copy 5.8e6, B-tree cell search about 2e6, page QROM 0.7e6); values
  0.55e6; predication 0.93e6. Plus about 2.7e8 CNOT of QROM data loading per call.
- Qubits ≈ 7.4e5: 4.7e5 superposed-memory upper bound plus 2.7e5 garbage without pebbling.
- Grover total: 2.8e8 Toffoli (M = 11,698) or 3.2e10 Toffoli (M = 1), i.e. 5.4e12 units
  sequential. At 1 µs per Toffoli that is about 9 h for M = 1 and about 5 min for M = 11,698,
  before parallelism.
- This estimate is optimistic. Dynamic invariance over the domain is a lower bound on coherent
  work; a sound static taint analysis will mark more. How much of the gap between 1e19 and 4e7 the
  plugin and specialiser actually close is the open question for structure recovery (ISA I2).

## 8. Work items for rung 4 (ranked)

1. **[plugin + dialect]** Lift the full closure (1,218 functions, 262k instructions):
   `lift.load/store/alloc/free/call/ret`, recursion, budgets. Removes D4/D2/B-42.
2. **[dialect + driver]** Oracle region entry with an `in` interface region bound to a C pointer
   parameter, a classical length argument, a superposed rowid input (zext + 1) and a 1-bit target;
   the error path traps. Removes D21/D3/B-32.
3. **[plugin + dialect]** Function-address encoding (code constants and data images), sound
   candidate sets (type-based, later points-to), compare-and-branch dispatch, zero-candidate sites
   to trap. Closes O-01/R2.
4. **[dialect normaliser]** Varargs lowering (952 sites; x86-64 va_list emulation). Closes O-03.
5. **[dialect normaliser]** memcpy-family → runtime lprocs; integer-intrinsic expansion; vector
   scalarisation (D16); atomic/volatile sequentialisation; freeze/lifetime/assume; switch lowering;
   allocas → shadow stack.
6. **[runtimes]** Allocator (`lift.alloc/free`, realloc), 10 libc string/memory shims, a UTC
   `localtime`, the `bennett-nofs` OS-shim VFS with deterministic randomness and clock. Closes D11
   for rung 4.
7. **[arith]** Soft-float coverage for the static floating-point set in §5.2(iii).
8. **[driver]** Record the 8 build flags in the certificate; LTO link; polyvariant cloning (B-16);
   image → qreg preparation with zero padding; layout with H = 18, A = 25, A_tab = 11,
   `heap_limit` ≥ 182 KB, `stack_limit` ≥ 1.34M cells, depth ≥ 21, B ≈ 3.2e5.
9. **[vm/circuits]** Structure recovery: classical partial evaluation of the invariant prefix
   (≥ 92 %), predicated tail only, QROM for the classical `in` region, select networks for
   superposed heap accesses. This is the difference between 1e19 and 4e7 Toffoli per call.
10. **[vm]** Branch-enumeration executor and reference interpreter at ≥ 1e6 rows/s, so (a) runs in
    minutes.
11. **[estimate]** Resource estimate from certificates for (c).
12. **[runtimes + driver, optional]** Route C′ snapshot: fixed-base arena plus a globals copy, for
    10× smaller B; still no ISA change.
13. **[ISA 0.9, optional, on evidence]** E1–E5.

## 9. Method, soundness, limits

- Instruction counts are IR instructions in the LTO-optimised module. Rows come from the stated
  weight model; the dialect's real mapping does not exist yet.
- Differential taint uses an exhaustive domain at N ≤ 2^10; runs at 2^14 and 2^20 are sampled (270
  and 257 rowids). Instances are aligned by k-th execution against a middle rowid, which is
  conservative after a divergence.
- Not measured: the speed of a real reversible interpreter (phase 1), gate counts of the `ref`
  expansion, and the static taint the plugin will achieve.

## 10. Reproduction

`scripts/run_all.sh` runs fetch → build → verify → inventory → profile → analyze → cost, in about
30–60 minutes. Work directory: `$BENNETT_SQLITE_WORK`, default `~/.cache/bennett-sqlite-spike`.

| Script | Does |
|---|---|
| `fetch.sh` | download with retry/backoff; size and SHA3 check |
| `build.sh` | bitcode, LTO module, native verify |
| `inventory.sh` | static inventory |
| `profile.sh build\|run\|all` | instrumented build and profiles |
| `analyze.py`, `cost.py` | summaries and estimates |
