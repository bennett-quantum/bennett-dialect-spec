/* bennett_markers.h -- Bennett dialect 0.2 marker ABI (spec/Bennett-Dialect-Spec.md section 3).
 *
 * The prototype lines between the BEGIN/END PROTOTYPES comments are checked by
 * scripts/dialect_check.py: they must equal the C header view of section 3.3
 * byte for byte, and clang must lower them to exactly the IR signatures of
 * section 3.2. Do not add attributes to these declarations (section 3.6).
 * The record layouts below are the C view of sections 8.1 and 9.1; their
 * binary layout is the LLVM struct layout under the module's datalayout.
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

typedef struct bennett_q_opaque *bennett_q;   /* handle: never dereferenced (section 6) */
typedef void (*bennett_region)(void *env);    /* action or reversible region (section 7.1) */

#define BENNETT_DIALECT_VERSION "0.2"
#define BENNETT_CLASS_ANY      UINT64_C(0)

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

/* budget record (section 9.1); LLVM type { i64, i64, i64, i64, ptr } */
#define BENNETT_BUDGET_TABLE UINT64_MAX       /* field value: take it from the budget table */
typedef struct bennett_budget {
  uint64_t steps;     /* reference-interpreter rows (section 9.4) */
  uint64_t heap;      /* heap bytes */
  uint64_t stack;     /* lifted stack cells */
  uint64_t depth;     /* call depth */
  bennett_q fault;    /* action regions: the caller's fault register (4 wires) or NULL */
} bennett_budget;

/* oracle interface descriptor (section 8.1) */
#define BENNETT_DESC_VERSION 2u
#define BENNETT_BIND_IN     1u    /* input register, zero- or sign-extended */
#define BENNETT_BIND_ARG    2u    /* classical value */
#define BENNETT_BIND_MEM_IN 3u    /* ptr parameter: lift.addr of an in region on q */
#define BENNETT_BIND_OUT    4u    /* ptr parameter: fresh zeroed buffer, XORed into q at exit */
#define BENNETT_BIND_INOUT  5u    /* in-place register (inplace only) */
#define BENNETT_MODE_ZEXT   0u
#define BENNETT_MODE_SEXT   1u
#define BENNETT_DEV_ENTROPY 1u    /* in region on q: the entropy tape */
#define BENNETT_DEV_BLOCK   2u    /* in region on q: the disk image */
#define BENNETT_DEV_CLOCK   3u    /* initial clock value in value */
#define BENNETT_DEV_CONSOLE 4u    /* output register q for console bytes, or NULL */

/* LLVM type { i32, i32, i32, i32, ptr, ptr } */
typedef struct bennett_oracle_desc {
  uint32_t version;   /* BENNETT_DESC_VERSION */
  uint32_t nparam;    /* number of IR parameters of the region function */
  uint32_t ndev;      /* number of device bindings */
  uint32_t flags;     /* 0 */
  bennett_q tgt;      /* result target, or NULL for none */
  bennett_q fault;    /* fault register (4 wires) */
} bennett_oracle_desc;

/* LLVM type { i32, i32, ptr, i64, i64 } */
typedef struct bennett_bind {
  uint32_t kind;      /* BENNETT_BIND_* */
  uint32_t mode;      /* BENNETT_MODE_* for IN, else 0 */
  bennett_q q;        /* register for IN, MEM_IN, OUT, INOUT; NULL for ARG */
  uint64_t value;     /* ARG: the parameter's bits */
  uint64_t size;      /* MEM_IN, OUT: bytes */
} bennett_bind;

/* LLVM type { i32, i32, ptr, i64 } */
typedef struct bennett_devbind {
  uint32_t model;     /* BENNETT_DEV_* */
  uint32_t mode;      /* 0 */
  bennett_q q;
  uint64_t value;     /* CLOCK: initial value */
} bennett_devbind;

/* Descriptors with NP >= 1 parameter and ND >= 1 device bindings, parameters only, devices only.
   A function with neither uses a bare bennett_oracle_desc. */
#define BENNETT_ORACLE_DESC(NP, ND) struct { bennett_oracle_desc h; bennett_bind param[NP]; bennett_devbind dev[ND]; }
#define BENNETT_ORACLE_DESC_P(NP)   struct { bennett_oracle_desc h; bennett_bind param[NP]; }
#define BENNETT_ORACLE_DESC_D(ND)   struct { bennett_oracle_desc h; bennett_devbind dev[ND]; }

/* Header fields by plain stores; d points to a bennett_oracle_desc. */
#define bennett_oracle_desc_init(d, np, nd, t, f) \
  ((d)->version = BENNETT_DESC_VERSION, (d)->nparam = (np), (d)->ndev = (nd), \
   (d)->flags = 0u, (d)->tgt = (t), (d)->fault = (f))
#define bennett_bind_set(b, k, m, qq, v, s) \
  ((b)->kind = (k), (b)->mode = (m), (b)->q = (qq), (b)->value = (v), (b)->size = (s))

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
void __bennett_qprep(bennett_q h, const void *src, uint64_t nbytes) BENNETT_NOEXCEPT;
void __bennett_observe(void *p, uint64_t len) BENNETT_NOEXCEPT;
void __bennett_ctrl(bennett_q q, uint64_t qi, bennett_region f, const bennett_budget *budget, void *env) BENNETT_NOEXCEPT;
void __bennett_adj(bennett_region f, const bennett_budget *budget, void *env) BENNETT_NOEXCEPT;
void __bennett_compute(bennett_region f, bennett_region use, const bennett_budget *budget, void *env) BENNETT_NOEXCEPT;
void __bennett_reversible(bennett_region f, const bennett_budget *budget, void *env) BENNETT_NOEXCEPT;
void __bennett_oracle(const void *f, const bennett_budget *budget, const bennett_oracle_desc *desc) BENNETT_NOEXCEPT;
void __bennett_inplace(const void *g, const void *ginv, const bennett_budget *budget, const bennett_oracle_desc *desc) BENNETT_NOEXCEPT;
void __bennett_effect_console_write(const void *p, uint64_t len) BENNETT_NOEXCEPT;
void __bennett_effect_clock_read(void *p) BENNETT_NOEXCEPT;
void __bennett_effect_entropy_read(void *p, uint64_t len) BENNETT_NOEXCEPT;
void __bennett_effect_block_read(uint64_t sector, void *p) BENNETT_NOEXCEPT;
void __bennett_effect_block_write(uint64_t sector, const void *p) BENNETT_NOEXCEPT;
/* END PROTOTYPES */

#ifdef __cplusplus
}
#endif
#endif /* BENNETT_MARKERS_H */
