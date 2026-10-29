#include <stdint.h>
extern "C" {
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
}
void may_throw(uint64_t);   // external, may throw
struct env { bq h; uint64_t i; double theta; };
extern "C++" { }
static void body(void *p) {
  env *e = static_cast<env *>(p);
  __bennett_rot(1, e->h, e->i, e->theta);
  __bennett_gate(2, e->h, e->i);
}
// RAII scope guard: marker calls inside its scope, may_throw can unwind -> invoke
struct Scope { bq h; Scope(bq h_) : h(h_) {} ~Scope() { __bennett_qfree(h); } };
extern "C" uint64_t case_entry(uint64_t x) {
  bq h = __bennett_qalloc(0, 4);
  __bennett_gate(1, h, 0);
  double theta = (double)x * 0.125;
  __bennett_rot(3, h, 1, theta);
  __bennett_gate2(4, h, 0, h, 1);
  uint64_t r = 0;
  if (__bennett_measure(h, 0)) { __bennett_gate(2, h, 2); r = 1; }
  env e = { h, 3, theta };
  __bennett_ctrl(h, 0, body, 8, &e);
  // lambda -> fn pointer (captureless) and region
  auto lam = [](void *p) { auto *e = static_cast<env *>(p); __bennett_gate(5, e->h, e->i); };
  __bennett_ctrl(h, 1, lam, 8, &e);
  bq tab[4];
  for (int k = 0; k < 4; k++) tab[k] = __bennett_qalloc(0, 1);
  __bennett_gate(1, tab[x & 3], 0);
  __bennett_ctrl_v(h, 0, (void *)body, 8, 1, 2.5, h);
  __bennett_adj(body, &e);
  {
    Scope s(__bennett_qborrow(0, 1));
    __bennett_gate(6, s.h, 0);
    may_throw(x);                  // invoke here under -fexceptions
    __bennett_gate(7, s.h, 0);
    __bennett_ctrl(h, 0, body, 8, &e);
  }
  for (int k = 0; k < 4; k++) __bennett_qfree(tab[k]);
  __bennett_qfree(h);
  return r;
}
