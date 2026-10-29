/* Profiler runtime for the bennett-prof instrumentation (native, never
 * instrumented).  Each oracle call runs in a forked child, so every call
 * starts from the identical memory image (the ISA's "same entry image on
 * every basis input"), and addresses are comparable across rowids.
 *
 * Per call (child-private): block counts, block trace, per-memory-site
 * address and value hashes, bytes touched (read / written), call depth,
 * live locations, stack bytes, memcpy-family bytes.
 * Across calls (shared with the parent): per-block min/max/sum counts, the
 * reference trace (first call) and divergence against it, per-memory-site
 * "address differs" / "value differs" / "count differs" flags, union and
 * intersection of the bytes touched, one summary record per call.
 */
#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>

extern const uint32_t __prof_nblocks, __prof_nmem, __prof_nfuncs, __prof_nvals;
extern const uint32_t __prof_bb_ninst[], __prof_fn_mprime[], __prof_fn_alloca[];
extern uint64_t shim_alloc_count, shim_free_count, shim_alloc_bytes, shim_live_bytes, shim_peak_live;

static int active;

/* ---------------------------------------------------------- byte sets */
#define PT_SLOTS (1u << 16)
typedef struct { uint64_t key; uint64_t r[64]; uint64_t w[64]; } page_t;  /* 4096 bits each */
static page_t *alloc_pt(int shared) {
  page_t *t = mmap(0, sizeof(page_t) * PT_SLOTS, PROT_READ | PROT_WRITE,
                   (shared ? MAP_SHARED : MAP_PRIVATE) | MAP_ANONYMOUS | MAP_NORESERVE, -1, 0);
  if (t == MAP_FAILED) { perror("mmap"); exit(3); }
  return t;
}
static page_t *pt_get(page_t *t, uint64_t pg, int create) {
  uint64_t key = pg + 1;
  uint32_t h = (uint32_t)((key * 0x9E3779B97F4A7C15ULL) >> 48) & (PT_SLOTS - 1);
  for (uint32_t i = 0; i < PT_SLOTS; i++) {
    page_t *p = &t[(h + i) & (PT_SLOTS - 1)];
    if (p->key == key) return p;
    if (p->key == 0) {
      if (!create) return 0;
      p->key = key;
      return p;
    }
  }
  fprintf(stderr, "prof_rt: page table full\n");
  exit(3);
}

/* ------------------------------------------------------- child state */
static uint32_t *bbcnt;
static uint64_t *m_ah, *m_vh;
static uint32_t *m_cnt;
static uint64_t *memx_max;
static uint64_t *v_h;
static uint32_t *v_cnt;
/* per-instance alignment against the reference run (k-th execution of a site) */
#define REF_CAP (1ull << 25)
static int is_ref;
static uint64_t *ref_stream;            /* private, reference run only: (id, value) pairs */
static uint64_t ref_stream_len;
static uint32_t *v_dcnt, *m_dcnt;       /* private: instances differing from the reference */
static uint32_t *s_vref_cnt, *s_mref_cnt, *s_vdi_max, *s_mdi_max;
static uint64_t *s_vref_off, *s_mref_off, *s_vref_vals, *s_mref_vals;
static uint32_t *trace;
#define TRACE_CAP (1ull << 27)
static uint64_t trace_len, trace_hash;
static page_t *touched, *last_page;
static uint64_t last_pg = ~0ull;
static int64_t depth, maxdepth, locs, maxlocs, sbytes, maxsbytes;
static uintptr_t sp_min, sp_entry;
static uint64_t n_ld, n_st, b_ld, b_st, n_memx, b_memx, memx_rows, dyn_alloca_bytes;
static int32_t fstack[1 << 16];

/* ------------------------------------------------------ shared state */
typedef struct {
  uint64_t rowid, result, ref, insts, blocks, n_ld, n_st, b_ld, b_st, n_memx, b_memx, memx_rows;
  uint64_t heap_allocs, heap_frees, heap_bytes, heap_peak_live, heap_live_at_exit;
  int64_t maxdepth, maxlocs, maxsbytes;
  uint64_t native_stack, dyn_alloca_bytes;
  uint64_t touched_r, touched_w, touched_any, touched_heap, touched_stack, touched_image, touched_other;
  uint64_t trace_len, trace_hash, prefix, suffix;
} run_t;
typedef struct {
  uint64_t nruns, ref_len;
  uintptr_t image_lo, image_hi, stack_lo, stack_hi, heap_lo, heap_hi;
} hdr_t;
static hdr_t *H;
static run_t *R;
static uint32_t *s_bmin, *s_bmax;
static uint64_t *s_bsum;
static uint64_t *s_ah, *s_vh;
static uint32_t *s_mcnt_max;
static uint8_t *s_adiff, *s_vdiff, *s_cdiff;
static uint32_t *s_ref_trace;
static uint64_t *s_vh;
static uint32_t *s_vcnt_max;
static uint8_t *s_vdiff_v, *s_vdiff_c;
static page_t *s_union, *s_inter;
/* distinct (memory site, address) pairs over all rowids */
#define AS_SLOTS (1ull << 25)
typedef struct { uint64_t addr; uint32_t mid1; uint32_t pad; } as_t;
static as_t *s_aset;
static uint64_t *s_aset_n;
static inline void aset_add(uint32_t mid, uint64_t addr) {
  uint64_t k = addr * 0x9E3779B97F4A7C15ULL ^ ((uint64_t)mid * 0xC2B2AE3D27D4EB4FULL);
  uint64_t h = (k >> 20) & (AS_SLOTS - 1);
  for (;;) {
    as_t *e = &s_aset[h];
    if (e->mid1 == mid + 1 && e->addr == addr) return;
    if (e->mid1 == 0) {
      e->mid1 = mid + 1; e->addr = addr;
      if (++*s_aset_n > AS_SLOTS / 2) { fprintf(stderr, "address set too full\n"); _exit(3); }
      return;
    }
    h = (h + 1) & (AS_SLOTS - 1);
  }
}   /* r = any-touch bits, w = write bits */
static int s_inter_init;

static void *shm(size_t n) {
  void *p = mmap(0, n ? n : 1, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS | MAP_NORESERVE, -1, 0);
  if (p == MAP_FAILED) { perror("mmap"); exit(3); }
  return p;
}
static void *priv(size_t n) {
  void *p = mmap(0, n ? n : 1, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE, -1, 0);
  if (p == MAP_FAILED) { perror("mmap"); exit(3); }
  return p;
}

#define MAXRUNS 4096
void prof_init(uintptr_t image_lo, uintptr_t image_len, uintptr_t heap_lo) {
  uint32_t nb = __prof_nblocks, nm = __prof_nmem;
  H = shm(sizeof(hdr_t));
  R = shm(sizeof(run_t) * MAXRUNS);
  s_bmin = shm(4ull * nb); s_bmax = shm(4ull * nb); s_bsum = shm(8ull * nb);
  for (uint32_t i = 0; i < nb; i++) s_bmin[i] = UINT32_MAX;
  s_ah = shm(8ull * nm); s_vh = shm(8ull * nm); s_mcnt_max = shm(4ull * nm);
  s_adiff = shm(nm); s_vdiff = shm(nm); s_cdiff = shm(nm);
  s_ref_trace = shm(4ull * TRACE_CAP);
  uint32_t nv = __prof_nvals;
  s_vh = shm(8ull * nv); s_vcnt_max = shm(4ull * nv); s_vdiff_v = shm(nv); s_vdiff_c = shm(nv);
  v_h = priv(8ull * nv); v_cnt = priv(4ull * nv);
  ref_stream = priv(16ull * REF_CAP);
  v_dcnt = priv(4ull * nv); m_dcnt = priv(4ull * nm);
  s_vref_cnt = shm(4ull * nv); s_vref_off = shm(8ull * nv); s_vdi_max = shm(4ull * nv);
  s_mref_cnt = shm(4ull * nm); s_mref_off = shm(8ull * nm); s_mdi_max = shm(4ull * nm);
  s_vref_vals = shm(8ull * REF_CAP); s_mref_vals = shm(8ull * REF_CAP);
  memx_max = shm(8ull * nm);
  s_union = alloc_pt(1); s_inter = alloc_pt(1);
  s_aset = shm(sizeof(as_t) * AS_SLOTS); s_aset_n = shm(8);
  bbcnt = priv(4ull * nb); m_ah = priv(8ull * nm); m_vh = priv(8ull * nm); m_cnt = priv(4ull * nm);
  trace = priv(4ull * TRACE_CAP);
  touched = alloc_pt(0);
  H->image_lo = image_lo; H->image_hi = image_lo + image_len;
  H->heap_lo = heap_lo; H->heap_hi = heap_lo + (1ull << 34);
}

static inline uint64_t mix(uint64_t h, uint64_t v) {
  h ^= v + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2);
  return h * 0xff51afd7ed558ccdULL;
}

/* id < 2^31: value site; id | 2^31: memory site */
static inline void inst(uint32_t id, uint32_t k, uint64_t v) {
  if (is_ref) {
    if (ref_stream_len >= REF_CAP) { fprintf(stderr, "ref stream overflow\n"); _exit(3); }
    ref_stream[2 * ref_stream_len] = id;
    ref_stream[2 * ref_stream_len + 1] = v;
    ref_stream_len++;
    return;
  }
  if (id >> 31) {
    uint32_t m = id & 0x7fffffff;
    if (k >= s_mref_cnt[m] || s_mref_vals[s_mref_off[m] + k] != v) m_dcnt[m]++;
  } else {
    if (k >= s_vref_cnt[id] || s_vref_vals[s_vref_off[id] + k] != v) v_dcnt[id]++;
  }
}

static inline void mark(uintptr_t a, uint64_t n, int write) {
  for (uint64_t i = 0; i < n; i++) {
    uintptr_t x = a + i;
    uint64_t pg = x >> 12;
    if (pg != last_pg) { last_page = pt_get(touched, pg, 1); last_pg = pg; }
    uint32_t bit = x & 4095;
    if (write) last_page->w[bit >> 6] |= 1ull << (bit & 63);
    else last_page->r[bit >> 6] |= 1ull << (bit & 63);
  }
}

void __prof_bb(uint32_t id) {
  if (!active) return;
  bbcnt[id]++;
  if (trace_len < TRACE_CAP) trace[trace_len] = id;
  trace_len++;
  trace_hash = mix(trace_hash, id);
}
void __prof_enter(uint32_t fid) {
  if (!active) return;
  uintptr_t sp = (uintptr_t)__builtin_frame_address(0);
  if (sp < sp_min) sp_min = sp;
  if (depth < (int64_t)(sizeof fstack / sizeof fstack[0])) fstack[depth] = (int32_t)fid;
  depth++;
  locs += 3 + __prof_fn_mprime[fid];   /* R_f = 3 + m' (ISA §3.7) */
  sbytes += __prof_fn_alloca[fid];
  if (depth > maxdepth) maxdepth = depth;
  if (locs > maxlocs) maxlocs = locs;
  if (sbytes > maxsbytes) maxsbytes = sbytes;
}
void __prof_exit(uint32_t fid) {
  if (!active) return;
  depth--;
  locs -= 3 + __prof_fn_mprime[fid];
  sbytes -= __prof_fn_alloca[fid];
}
void __prof_ld(void *p, uint32_t sz, uint32_t mid) {
  if (!active) return;
  inst(mid | 0x80000000u, m_cnt[mid], (uintptr_t)p);
  n_ld++; b_ld += sz; m_cnt[mid]++;
  m_ah[mid] = mix(m_ah[mid], (uintptr_t)p);
  aset_add(mid, (uintptr_t)p);
  mark((uintptr_t)p, sz, 0);
}
void __prof_st(void *p, uint32_t sz, uint32_t mid, uint64_t v) {
  if (!active) return;
  inst(mid | 0x80000000u, m_cnt[mid], (uintptr_t)p);
  n_st++; b_st += sz; m_cnt[mid]++;
  m_ah[mid] = mix(m_ah[mid], (uintptr_t)p);
  m_vh[mid] = mix(m_vh[mid], mix((uintptr_t)p, v));
  aset_add(mid, (uintptr_t)p);
  mark((uintptr_t)p, sz, 1);
}
void __prof_memx(void *d, void *s, uint64_t n, uint32_t kind, uint32_t mid) {
  if (!active) return;
  inst(mid | 0x80000000u, m_cnt[mid], mix((uintptr_t)d, mix((uintptr_t)s, n)));
  n_memx++; b_memx += n; m_cnt[mid]++;
  memx_rows += 3 + 3 * ((n + 7) / 8);   /* lifted word loop: load, store, step per 8 bytes */
  m_ah[mid] = mix(mix(m_ah[mid], (uintptr_t)d), mix((uintptr_t)s, n));
  m_vh[mid] = mix(m_vh[mid], n);
  aset_add(mid, (uintptr_t)d);
  if (s) aset_add(mid, (uintptr_t)s | (1ull << 62));   /* source addresses tagged */
  if (n > memx_max[mid]) memx_max[mid] = n;
  if (s) mark((uintptr_t)s, n, 0);
  mark((uintptr_t)d, n, 1);
  (void)kind;
}
void __prof_val(uint32_t vid, uint64_t bits) {
  if (!active) return;
  inst(vid, v_cnt[vid], bits);
  v_cnt[vid]++;
  v_h[vid] = mix(v_h[vid], bits);
}
void __prof_alloca(uint64_t n) { if (active) dyn_alloca_bytes += n; }

/* ------------------------------------------------------ child protocol */
static uint64_t c_rowid, c_ref;
void prof_child_begin(uint64_t rowid, uint64_t ref) {
  c_rowid = rowid; c_ref = ref;
  shim_alloc_count = shim_free_count = shim_alloc_bytes = shim_live_bytes = shim_peak_live = 0;
  is_ref = H->nruns == 0;
  sp_entry = sp_min = (uintptr_t)__builtin_frame_address(0);
  H->stack_hi = sp_entry + 4096;
  H->stack_lo = sp_entry - (64u << 20);
  active = 1;
}

static int region_of(uintptr_t a) {
  if (a >= H->image_lo && a < H->image_hi) return 2;
  if (a >= H->heap_lo && a < H->heap_hi) return 1;
  if (a >= H->stack_lo && a < H->stack_hi) return 3;
  return 0;
}

void prof_child_end(uint8_t result) {
  active = 0;
  uint64_t n = H->nruns;
  if (n >= MAXRUNS) { fprintf(stderr, "too many runs\n"); _exit(3); }
  run_t *r = &R[n];
  memset(r, 0, sizeof *r);
  r->rowid = c_rowid; r->result = result; r->ref = c_ref;
  uint32_t nb = __prof_nblocks, nm = __prof_nmem;
  uint64_t insts = 0, blocks = 0;
  for (uint32_t i = 0; i < nb; i++) {
    uint32_t c = bbcnt[i];
    insts += (uint64_t)c * __prof_bb_ninst[i];
    blocks += c;
    if (c < s_bmin[i]) s_bmin[i] = c;
    if (c > s_bmax[i]) s_bmax[i] = c;
    s_bsum[i] += c;
  }
  r->insts = insts; r->blocks = blocks;
  r->n_ld = n_ld; r->n_st = n_st; r->b_ld = b_ld; r->b_st = b_st;
  r->n_memx = n_memx; r->b_memx = b_memx; r->memx_rows = memx_rows;
  r->heap_allocs = shim_alloc_count; r->heap_frees = shim_free_count;
  r->heap_bytes = shim_alloc_bytes; r->heap_peak_live = shim_peak_live;
  r->heap_live_at_exit = shim_live_bytes;
  r->maxdepth = maxdepth; r->maxlocs = maxlocs; r->maxsbytes = maxsbytes;
  r->native_stack = sp_entry - sp_min; r->dyn_alloca_bytes = dyn_alloca_bytes;
  r->trace_len = trace_len; r->trace_hash = trace_hash;
  if (trace_len > TRACE_CAP) { fprintf(stderr, "trace overflow\n"); _exit(3); }
  for (uint32_t i = 0; i < nm; i++) {
    if (n == 0) { s_ah[i] = m_ah[i]; s_vh[i] = m_vh[i]; }
    else {
      if (s_ah[i] != m_ah[i]) s_adiff[i] = 1;
      if (s_vh[i] != m_vh[i]) s_vdiff[i] = 1;
    }
    if (n > 0 && m_cnt[i] != s_mcnt_max[i] && (m_cnt[i] || s_mcnt_max[i])) s_cdiff[i] = 1;
    if (m_cnt[i] > s_mcnt_max[i]) s_mcnt_max[i] = m_cnt[i];
  }
  if (is_ref) {
    uint64_t off = 0;
    for (uint32_t i = 0; i < __prof_nvals; i++) { s_vref_cnt[i] = v_cnt[i]; s_vref_off[i] = off; off += v_cnt[i]; }
    uint64_t moff = 0;
    for (uint32_t i = 0; i < nm; i++) { s_mref_cnt[i] = m_cnt[i]; s_mref_off[i] = moff; moff += m_cnt[i]; }
    if (off > REF_CAP || moff > REF_CAP) { fprintf(stderr, "ref values overflow\n"); _exit(3); }
    /* scatter in execution order: the k-th instance of a site lands at off + k */
    uint32_t *cur_v = (uint32_t *)priv(4ull * __prof_nvals), *cur_m = (uint32_t *)priv(4ull * nm);
    for (uint64_t j = 0; j < ref_stream_len; j++) {
      uint32_t id = (uint32_t)ref_stream[2 * j];
      uint64_t v = ref_stream[2 * j + 1];
      if (id >> 31) { uint32_t m = id & 0x7fffffff; s_mref_vals[s_mref_off[m] + cur_m[m]++] = v; }
      else s_vref_vals[s_vref_off[id] + cur_v[id]++] = v;
    }
  } else {
    for (uint32_t i = 0; i < __prof_nvals; i++) if (v_dcnt[i] > s_vdi_max[i]) s_vdi_max[i] = v_dcnt[i];
    for (uint32_t i = 0; i < nm; i++) if (m_dcnt[i] > s_mdi_max[i]) s_mdi_max[i] = m_dcnt[i];
  }
  for (uint32_t i = 0; i < __prof_nvals; i++) {
    if (n == 0) s_vh[i] = v_h[i];
    else if (s_vh[i] != v_h[i]) s_vdiff_v[i] = 1;
    if (n > 0 && v_cnt[i] != s_vcnt_max[i] && (v_cnt[i] || s_vcnt_max[i])) s_vdiff_c[i] = 1;
    if (v_cnt[i] > s_vcnt_max[i]) s_vcnt_max[i] = v_cnt[i];
  }
  if (n == 0) {
    memcpy(s_ref_trace, trace, 4 * trace_len);
    H->ref_len = trace_len;
    r->prefix = r->suffix = trace_len;
  } else {
    uint64_t L = H->ref_len, m = trace_len < L ? trace_len : L, p = 0, s = 0;
    while (p < m && trace[p] == s_ref_trace[p]) p++;
    while (s < m && trace[trace_len - 1 - s] == s_ref_trace[L - 1 - s]) s++;
    r->prefix = p; r->suffix = s;
  }
  /* bytes touched, union and intersection */
  uint64_t tr = 0, tw = 0, ta = 0, treg[4] = {0};
  for (uint32_t i = 0; i < PT_SLOTS; i++) {
    page_t *p = &touched[i];
    if (!p->key) continue;
    uintptr_t base = (p->key - 1) << 12;
    page_t *u = pt_get(s_union, p->key - 1, 1);
    for (int j = 0; j < 64; j++) {
      uint64_t a = p->r[j] | p->w[j];
      tr += __builtin_popcountll(p->r[j]);
      tw += __builtin_popcountll(p->w[j]);
      ta += __builtin_popcountll(a);
      u->r[j] |= a; u->w[j] |= p->w[j];
    }
    uint64_t cnt = 0;
    for (int j = 0; j < 64; j++) cnt += __builtin_popcountll(p->r[j] | p->w[j]);
    treg[region_of(base)] += cnt;
    if (n == 0) {
      page_t *q = pt_get(s_inter, p->key - 1, 1);
      for (int j = 0; j < 64; j++) q->r[j] = p->r[j] | p->w[j];
    }
  }
  if (n > 0) {
    for (uint32_t i = 0; i < PT_SLOTS; i++) {
      page_t *q = &s_inter[i];
      if (!q->key) continue;
      page_t *p = pt_get(touched, q->key - 1, 0);
      for (int j = 0; j < 64; j++) q->r[j] &= p ? (p->r[j] | p->w[j]) : 0;
    }
  }
  r->touched_r = tr; r->touched_w = tw; r->touched_any = ta;
  r->touched_other = treg[0]; r->touched_heap = treg[1]; r->touched_image = treg[2];
  r->touched_stack = treg[3];
  H->nruns = n + 1;
}

/* ------------------------------------------------------------ report */
static void count_pt(page_t *t, uint64_t out[4][2]) {
  for (uint32_t i = 0; i < PT_SLOTS; i++) {
    page_t *p = &t[i];
    if (!p->key) continue;
    int reg = region_of((p->key - 1) << 12);
    for (int j = 0; j < 64; j++) {
      out[reg][0] += __builtin_popcountll(p->r[j]);
      out[reg][1] += __builtin_popcountll(p->w[j]);
    }
  }
}

void prof_report(const char *dir) {
  char path[4096];
  FILE *f;
  snprintf(path, sizeof path, "%s/runs.tsv", dir);
  f = fopen(path, "w");
  fprintf(f, "rowid\tresult\tref\tinsts\tblocks\tn_ld\tn_st\tb_ld\tb_st\tn_memx\tb_memx\tmemx_rows\t"
             "heap_allocs\theap_frees\theap_bytes\theap_peak_live\theap_live_at_exit\tmaxdepth\t"
             "maxlocs\tmaxsbytes\tnative_stack\tdyn_alloca_bytes\ttouched_r\ttouched_w\ttouched_any\t"
             "touched_heap\ttouched_stack\ttouched_image\ttouched_other\ttrace_len\ttrace_hash\t"
             "prefix\tsuffix\n");
  for (uint64_t i = 0; i < H->nruns; i++) {
    run_t *r = &R[i];
    fprintf(f, "%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t"
               "%ld\t%ld\t%ld\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t%016lx\t%lu\t%lu\n",
            r->rowid, r->result, r->ref, r->insts, r->blocks, r->n_ld, r->n_st, r->b_ld, r->b_st,
            r->n_memx, r->b_memx, r->memx_rows, r->heap_allocs, r->heap_frees, r->heap_bytes,
            r->heap_peak_live, r->heap_live_at_exit, r->maxdepth, r->maxlocs, r->maxsbytes,
            r->native_stack, r->dyn_alloca_bytes, r->touched_r, r->touched_w, r->touched_any,
            r->touched_heap, r->touched_stack, r->touched_image, r->touched_other, r->trace_len,
            r->trace_hash, r->prefix, r->suffix);
  }
  fclose(f);
  snprintf(path, sizeof path, "%s/blocks.tsv", dir);
  f = fopen(path, "w");
  fprintf(f, "bid\tmin\tmax\tsum\n");
  for (uint32_t i = 0; i < __prof_nblocks; i++)
    if (s_bmax[i]) fprintf(f, "%u\t%u\t%u\t%lu\n", i, s_bmin[i], s_bmax[i], s_bsum[i]);
  fclose(f);
  snprintf(path, sizeof path, "%s/mem.tsv", dir);
  f = fopen(path, "w");
  fprintf(f, "mid\tmaxcnt\taddr_differs\tval_differs\tcnt_differs\taddr_diff_inst_max\n");
  for (uint32_t i = 0; i < __prof_nmem; i++)
    if (s_mcnt_max[i]) fprintf(f, "%u\t%u\t%u\t%u\t%u\t%u\n", i, s_mcnt_max[i], s_adiff[i], s_vdiff[i], s_cdiff[i], s_mdi_max[i]);
  fclose(f);
  snprintf(path, sizeof path, "%s/val.tsv", dir);
  f = fopen(path, "w");
  fprintf(f, "vid\tmaxcnt\tval_differs\tcnt_differs\tdiff_inst_max\n");
  for (uint32_t i = 0; i < __prof_nvals; i++)
    if (s_vcnt_max[i]) fprintf(f, "%u\t%u\t%u\t%u\t%u\n", i, s_vcnt_max[i], s_vdiff_v[i], s_vdiff_c[i], s_vdi_max[i]);
  fclose(f);
  {  /* distinct addresses per memory site (dst and src counted separately) */
    uint32_t nm = __prof_nmem;
    uint64_t *dd = calloc(nm, 8), *ds = calloc(nm, 8);
    for (uint64_t i = 0; i < AS_SLOTS; i++) {
      as_t *e = &s_aset[i];
      if (!e->mid1) continue;
      if (e->addr >> 62) ds[e->mid1 - 1]++; else dd[e->mid1 - 1]++;
    }
    snprintf(path, sizeof path, "%s/addrsets.tsv", dir);
    f = fopen(path, "w");
    fprintf(f, "mid\tdistinct_addr\tdistinct_src\tmemx_max_bytes\n");
    for (uint32_t i = 0; i < nm; i++)
      if (dd[i]) fprintf(f, "%u\t%lu\t%lu\t%lu\n", i, dd[i], ds[i], memx_max[i]);
    fclose(f);
  }
  uint64_t U[4][2] = {{0}}, I[4][2] = {{0}};
  count_pt(s_union, U);
  count_pt(s_inter, I);
  snprintf(path, sizeof path, "%s/footprint.json", dir);
  f = fopen(path, "w");
  fprintf(f, "{\"regions\": [\"other(globals)\", \"heap\", \"image\", \"stack\"],\n"
             " \"union_touched\": [%lu, %lu, %lu, %lu],\n \"union_written\": [%lu, %lu, %lu, %lu],\n"
             " \"intersection_touched\": [%lu, %lu, %lu, %lu],\n \"image_bytes\": %lu}\n",
          U[0][0], U[1][0], U[2][0], U[3][0], U[0][1], U[1][1], U[2][1], U[3][1],
          I[0][0], I[1][0], I[2][0], I[3][0], (uint64_t)(H->image_hi - H->image_lo));
  fclose(f);
}

/* fork one child per rowid */
typedef uint8_t (*oracle_fn)(uint64_t);
int prof_run_all(oracle_fn f, const uint64_t *rowids, uint64_t n, int (*ref)(uint64_t)) {
  int bad = 0;
  for (uint64_t i = 0; i < n; i++) {
    fflush(0);
    pid_t pid = fork();
    if (pid < 0) { perror("fork"); exit(3); }
    if (pid == 0) {
      int want = ref(rowids[i]);
      prof_child_begin(rowids[i], (uint64_t)want);
      uint8_t got = f(rowids[i]);
      prof_child_end(got);
      _exit(got == (uint8_t)want ? 0 : 1);
    }
    int st;
    waitpid(pid, &st, 0);
    if (!WIFEXITED(st) || WEXITSTATUS(st) != 0) {
      fprintf(stderr, "rowid %lu: child status %d (mismatch or crash)\n", rowids[i], st);
      bad++;
    }
  }
  return bad;
}
