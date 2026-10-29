// CASE: c-program-mixed
// HAZARD: whole-program C shape through default<O3>, lto-pre-link/lto and the P4 clang -O3 -flto route: a handle table (array of handles) filled in a loop and indexed by classical values, a ctrl region with an environment struct holding a handle and a classical key, an adj region, a compute/use pair, rot angles from a loop, measurement feeding branches and the classical result, static helpers (inlined when the noinline from -O0 is absent), and a struct copy of the environment
// INPUTS: 0..63
// EXPECT: legal
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

enum { NQ = 4 };
struct env { bq reg[NQ]; uint64_t key; bq anc; };

static void oracle(void *p) {
  struct env *e = p;
  for (unsigned i = 0; i < NQ; i++)
    if ((e->key >> i) & 1)
      __bennett_gate2(3, e->reg[i], 0, e->anc, 0);
}

static void diffuse(void *p) {
  struct env *e = p;
  for (unsigned i = 0; i < NQ; i++) __bennett_gate(1, e->reg[i], 0);
  __bennett_gate(2, e->reg[e->key % NQ], 0);
}

static void phase(void *p) {
  struct env *e = p;
  __bennett_gate(5, e->anc, 0);
}

static void layer(struct env *e, int round) {
  for (unsigned i = 0; i < NQ; i++)
    __bennett_rot(6, e->reg[i], 0, 0.5 * (double)(round + 1) + 0.125 * (double)i);
}

int64_t case_entry(int64_t x) {
  struct env e;
  for (unsigned i = 0; i < NQ; i++) e.reg[i] = __bennett_qalloc(0, 1);
  e.anc = __bennett_qborrow(1, 1);
  e.key = (uint64_t)x & 15;
  bq ctl = __bennett_qalloc(0, 1);
  __bennett_gate(1, ctl, 0);
  int rounds = 1 + (int)((x >> 4) & 3);
  for (int r = 0; r < rounds; r++) {
    __bennett_ctrl(ctl, 0, oracle, 64, &e);
    __bennett_adj(diffuse, &e);
    layer(&e, r);
  }
  struct env snap = e;          /* struct copy of handles */
  __bennett_compute(oracle, phase, &snap);
  int64_t out = 0;
  for (unsigned i = 0; i < NQ; i++) {
    bool m = __bennett_measure(e.reg[i], 0);
    if (m) {
      out |= (int64_t)1 << i;
      __bennett_gate(2, e.reg[(i + 1) % NQ], 0);
    }
  }
  if (__bennett_measure(ctl, 0)) out += 100;
  __bennett_qfree(ctl);
  __bennett_qfree(e.anc);
  for (unsigned i = 0; i < NQ; i++) __bennett_qfree(snap.reg[i]);
  return out;
}
