// CASE: c-unprototyped-decl
// HAZARD: markers declared K&R-style without prototypes (C17 and earlier accept `void __bennett_gate();`): clang emits `declare void @__bennett_gate(...)` and calls with a per-site function type; instcombine (transformConstExprCastCall) and deadargelim may rewrite the call to the declared type, and the plugin's "recognise by name and signature" sees a variadic declaration. Arguments are passed with their exact ABI types so the runtime call is well defined
// INPUTS: 0..15
// EXPECT: probe
#include <stdint.h>
#include <stdbool.h>
typedef struct __bennett_q *bq;
bq   __bennett_qalloc();
void __bennett_qfree();
void __bennett_gate();
bool __bennett_measure();
void __bennett_rot();

int64_t case_entry(int64_t x) {
  bq h = __bennett_qalloc((uint64_t)0, (uint64_t)2);
  __bennett_gate((uint32_t)1, h, (uint64_t)(x & 1));
  __bennett_rot((uint32_t)2, h, (uint64_t)0, 0.25 * (double)x);
  bool m = __bennett_measure(h, (uint64_t)0);
  __bennett_qfree(h);
  return m;
}
