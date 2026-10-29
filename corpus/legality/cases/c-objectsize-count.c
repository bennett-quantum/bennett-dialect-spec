// CASE: c-objectsize-count
// HAZARD: __builtin_object_size / __builtin_dynamic_object_size (llvm.objectsize) used as a classical marker argument (the qalloc width and a gate index derived from the remaining size of a buffer of qubit indices, a fortified-memcpy shape): at -O0 llc lowers objectsize to the "unknown" answer (-1), after O3 (instcombine / lower-constant-intrinsics) it folds to the real remaining size, so marker arguments differ between builds
// INPUTS: 0..15
// EXPECT: probe
/* spike marker ABI v0 (docs/spikes/2026-10-28-legality-spike.md section 1), declared inline */
#include <stdint.h>
#include <stdbool.h>
typedef struct __bennett_q *bq;
typedef void (*bregion)(void *env);
bq   __bennett_qalloc(uint64_t cls, uint64_t n);
bq   __bennett_qborrow(uint64_t cls, uint64_t n);
void __bennett_qfree(bq h);
void __bennett_gate(uint32_t op, bq h, uint64_t i);
void __bennett_gate2(uint32_t op, bq a, uint64_t i, bq b, uint64_t j);
void __bennett_rot(uint32_t op, bq h, uint64_t i, double theta);
bool __bennett_measure(bq h, uint64_t i);
void __bennett_qload(bq dst, bq mem, bq addr);
void __bennett_qstore(bq mem, bq addr, bq val);
void __bennett_ctrl(bq q, uint64_t qi, bregion f, uint64_t budget, void *env);
void __bennett_adj(bregion f, void *env);
void __bennett_compute(bregion f, bregion use, void *env);
void __bennett_reversible(bregion f, uint64_t budget, void *env);
void __bennett_inplace(bregion g, bregion ginv, void *env);
void __bennett_ctrl_v(bq q, uint64_t qi, void *f, uint64_t budget, ...);

int64_t case_entry(int64_t x) {
  char idx[5] = {0, 1, 2, 3, 4};
  char *p = idx + (x & 1);
  /* not foldable by the front end (depends on x); llc -O0 answers "unknown",
     O3 (instcombine / lower-constant-intrinsics) answers 5 - (x & 1) */
  uint64_t sz = __builtin_dynamic_object_size(p, 0);
  uint64_t w = sz == (uint64_t)-1 ? 2 : sz;
  uint64_t s0 = __builtin_object_size(p, 0);
  uint64_t budget = s0 == (uint64_t)-1 ? 100 : s0;
  bq h = __bennett_qalloc(0, w);
  __bennett_gate(1, h, (uint64_t)p[0]);
  __bennett_gate(2, h, budget & 1);
  __bennett_qfree(h);
  return (int64_t)(w * 1000 + budget);
}
