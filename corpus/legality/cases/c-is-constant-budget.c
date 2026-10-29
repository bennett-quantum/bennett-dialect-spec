// CASE: c-is-constant-budget
// HAZARD: __builtin_constant_p (llvm.is.constant) choosing a region budget and a qalloc size: at -O0 codegen lowers is.constant to false, after O3 (ipsccp propagating the constant argument into the static helper, instcombine folding is.constant) it is true, so the budget/size arguments of the marker calls differ between baseline and optimised builds. LLVM-legal by definition of is.constant; the north star normalises is.constant only inside outlined regions, and this is host code computing a marker argument
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

static void body(void *env) { __bennett_gate(1, *(bq *)env, 0); }

static int64_t run(bq h, uint64_t n) {
  uint64_t budget = __builtin_constant_p(n) ? n * 4 : 1000;
  bq t = __bennett_qalloc(0, __builtin_constant_p(n) ? n : 8);
  __bennett_reversible(body, budget, &h);
  __bennett_gate2(3, h, 0, t, 0);
  __bennett_qfree(t);
  return (int64_t)budget;
}

int64_t case_entry(int64_t x) {
  bq h = __bennett_qalloc(0, 1);
  int64_t r = run(h, 3) + (x & 1);
  __bennett_qfree(h);
  return r;
}
