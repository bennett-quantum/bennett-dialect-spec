// CASE: c-pie-reltable-region
// HAZARD: simplifycfg switch-to-lookup on a switch that only selects the region of __bennett_ctrl, compiled by clang as a PIE module ("PIC Level"/"PIE Level" module flags): O3 builds a private [6 x ptr] @switch.table of functions + GEP + load + phi feeding the region operand; probes whether rel-lookup-table-converter (runs at the end of O3 for PIC targets) turns it into 32-bit relative offsets read through llvm.load.relative (seen: no, on 18 and 23 with -relocation-model=pic). Question: what operand shapes must the plugin resolve: constant / select-of-constants / phi-of-constants / load-from-constant-table / other
// INPUTS: 0..63
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

struct env { bq h; };
void o0(void *p) { __bennett_gate(60, ((struct env *)p)->h, 0); }
void o1(void *p) { __bennett_gate(61, ((struct env *)p)->h, 1); }
void o2(void *p) { __bennett_gate(62, ((struct env *)p)->h, 0); }
void o3(void *p) { __bennett_gate(63, ((struct env *)p)->h, 1); }
void o4(void *p) { __bennett_gate(64, ((struct env *)p)->h, 0); }

int64_t case_entry(int64_t x) {
  struct env e;
  e.h = __bennett_qalloc(0, 2);
  bq q = __bennett_qalloc(0, 1);
  bregion f;
  switch (x & 7) {
  case 0: f = o0; break;
  case 1: f = o1; break;
  case 2: f = o2; break;
  case 3: f = o3; break;
  case 4: f = o4; break;
  case 5: f = o2; break;
  default: f = o1; break;
  }
  __bennett_ctrl(q, 0, f, 8, &e);
  __bennett_qfree(q);
  __bennett_qfree(e.h);
  return x & 7;
}
