// CASE: c-pure-attr-wrapper
// HAZARD: a user helper that calls markers but is declared __attribute__((pure)) / __attribute__((const)) (a source-level lie, or a front end deriving memory(read)/memory(none) from a language-level effect annotation such as Julia @assume_effects): clang emits memory(read)/memory(none) on the helper, so early-cse/gvn/dce/licm may common, delete or hoist calls to it and the markers inside vanish from the trace. Not a stock-LLVM bug; tests whether the dialect must reject marker calls reachable from memory(none)/memory(read)/willreturn functions
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

__attribute__((pure)) static int peek_twice(bq h) {
  return __bennett_measure(h, 0) + __bennett_measure(h, 0);
}

__attribute__((const)) static int hadamard_ret(bq h) {
  __bennett_gate(1, h, 0);
  return 1;
}

int64_t case_entry(int64_t x) {
  bq h = __bennett_qalloc(0, 1);
  int a = peek_twice(h);
  int b = peek_twice(h);
  int unused = hadamard_ret(h);
  (void)unused;
  for (int i = 0; i < (int)(x & 3); i++)
    a += hadamard_ret(h);
  __bennett_qfree(h);
  return a + b;
}
