/* bennett_markers.h -- Bennett dialect 0.1 marker ABI (spec/Bennett-Dialect-Spec.md section 3).
 *
 * The prototype lines between the BEGIN/END PROTOTYPES comments are checked by
 * scripts/dialect_check.py: they must equal the C header view of section 3.3
 * byte for byte, and clang must lower them to exactly the IR signatures of
 * section 3.2. Do not add attributes to these declarations (section 3.6).
 */
#ifndef BENNETT_MARKERS_H
#define BENNETT_MARKERS_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
#define BENNETT_NOEXCEPT noexcept
extern "C" {
#else
#define BENNETT_NOEXCEPT
#endif

typedef struct bennett_q_opaque *bennett_q;   /* handle: never dereferenced (section 5) */
typedef void (*bennett_region)(void *env);    /* action or reversible region (section 6.1) */

#define BENNETT_DIALECT_VERSION "0.1"
#define BENNETT_CLASS_ANY      UINT64_C(0)
#define BENNETT_BUDGET_DEFAULT UINT64_MAX     /* section 6.5 */

/* operation codes (section 3.4) */
#define BENNETT_GATE_X    1u
#define BENNETT_GATE_H    2u
#define BENNETT_GATE_S    3u
#define BENNETT_GATE_SDG  4u
#define BENNETT_GATE_T    5u
#define BENNETT_GATE_TDG  6u
#define BENNETT_GATE_Z    7u
#define BENNETT_GATE_Y    8u
#define BENNETT_GATE2_CX   1u
#define BENNETT_GATE2_CZ   2u
#define BENNETT_GATE2_SWAP 3u
#define BENNETT_GATE3_CCX  1u
#define BENNETT_ROT_RX 1u
#define BENNETT_ROT_RY 2u
#define BENNETT_ROT_RZ 3u

/* BEGIN PROTOTYPES */
bennett_q __bennett_qalloc(uint64_t cls, uint64_t n) BENNETT_NOEXCEPT;
bennett_q __bennett_qborrow(uint64_t cls, uint64_t n) BENNETT_NOEXCEPT;
void __bennett_qfree(bennett_q h) BENNETT_NOEXCEPT;
void __bennett_gate(uint32_t op, bennett_q h, uint64_t i) BENNETT_NOEXCEPT;
void __bennett_gate2(uint32_t op, bennett_q a, uint64_t i, bennett_q b, uint64_t j) BENNETT_NOEXCEPT;
void __bennett_gate3(uint32_t op, bennett_q a, uint64_t i, bennett_q b, uint64_t j, bennett_q c, uint64_t k) BENNETT_NOEXCEPT;
void __bennett_rot(uint32_t op, bennett_q h, uint64_t i, double theta) BENNETT_NOEXCEPT;
bool __bennett_measure(bennett_q h, uint64_t i) BENNETT_NOEXCEPT;
void __bennett_qload(bennett_q dst, bennett_q mem, bennett_q addr) BENNETT_NOEXCEPT;
void __bennett_qstore(bennett_q mem, bennett_q addr, bennett_q val) BENNETT_NOEXCEPT;
void __bennett_ctrl(bennett_q q, uint64_t qi, bennett_region f, uint64_t budget, void *env) BENNETT_NOEXCEPT;
void __bennett_adj(bennett_region f, void *env) BENNETT_NOEXCEPT;
void __bennett_compute(bennett_region f, bennett_region use, void *env) BENNETT_NOEXCEPT;
void __bennett_reversible(bennett_region f, uint64_t budget, void *env) BENNETT_NOEXCEPT;
void __bennett_inplace(void *g, void *ginv, uint64_t budget, bennett_q x) BENNETT_NOEXCEPT;
void __bennett_oracle(void *f, uint64_t budget, bennett_q x, bennett_q tgt, bennett_q fault) BENNETT_NOEXCEPT;
/* END PROTOTYPES */

#ifdef __cplusplus
}
#endif
#endif /* BENNETT_MARKERS_H */
