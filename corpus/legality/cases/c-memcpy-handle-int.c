// CASE: c-memcpy-handle-int
// HAZARD: instcombine lowering of small memcpy (8 bytes) to integer load/store, then store-to-load forwarding: a handle copied with memcpy (the shape of C struct assignment, Rust moves, memmove of a handle table entry) is turned into `ptrtoint ptr %h to i64` + `store i64` by O3, a handle-to-integer conversion the source never wrote; 16-byte struct copy of two handles and a handle-table entry copied out by memcpy as well
// INPUTS: 0..63
// EXPECT: probe
#include <string.h>
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

struct env1 { bq h; uint64_t i; };
struct pair { bq a; bq b; };
bq gslot[4];

static void rg(void *e) {
  struct env1 *p = e;
  __bennett_gate(1, p->h, p->i);
}

static void rpair(void *e) {
  struct pair *p = e;
  __bennett_gate2(3, p->a, 0, p->b, 0);
}

int64_t case_entry(int64_t x) {
  struct env1 e;
  gslot[x & 3] = __bennett_qalloc(0, 1);
  memcpy(&e.h, &gslot[x & 3], sizeof(bq));   /* 8-byte memcpy of a handle */
  e.i = 0;
  __bennett_gate(2, e.h, 0);
  __bennett_ctrl(e.h, 0, rg, 4, &e);

  struct pair p, q;
  p.a = __bennett_qalloc(0, 1);
  p.b = gslot[x & 3];
  q = p;                                       /* struct copy: 16-byte memcpy */
  __bennett_adj(rpair, &q);

  bq t;
  memcpy(&t, &e, sizeof t);                    /* handle out of the env by memcpy */
  __bennett_qfree(q.a);
  __bennett_qfree(t);
  return x;
}
