/* libc shim for the oracle closure (prototype of bennett-runtimes libc-shims
 * and allocator).  Linked into the profile build as bitcode, so its code is
 * part of the measured closure exactly as the north star's comparison binary
 * is ("linked against the same bennett-runtimes ... never against the host
 * libc", §3.2).
 *
 * Covers every libc function the SQLite oracle closure references (see
 * results/inventory.json): malloc family, bcmp/memcmp/memchr, str*.
 * memcpy/memmove/memset are reached only as LLVM intrinsics; the profiler
 * accounts for them at the intrinsic (scripts/plugin), so they are left to
 * the host libc here to avoid double counting.
 * localtime is reachable only through the date functions' 'localtime'
 * modifier; it fails loud.
 *
 * Allocator: the ISA §7.1 model.  A monotonic bump allocator at a fixed base
 * (no ASLR), storage never reclaimed, free marks dead.  So the heap budget of
 * an oracle (heap_limit) is the cumulative bytes allocated, not the peak.
 * Compile with -fno-builtin so the loops are not turned back into libcalls.
 */
#include <stddef.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdlib.h>
#include <unistd.h>

#define ARENA_BASE ((uintptr_t)0x100000000000ULL)
#define ARENA_SIZE ((size_t)1 << 34)   /* 16 GiB virtual, lazily backed */
#define HDR 16

static unsigned char *arena;
static size_t bump;
/* SHIM_PAD=k (environment, read once before any oracle runs): round every
 * allocation up to a multiple of k bytes.  Emulates the north star's
 * "allocation whose size depends on a qubit is padded to its bound" (§4.2),
 * so that bump addresses stop depending on data-dependent sizes. */
static size_t pad = 16;
/* statistics (read by the profiler runtime) */
uint64_t shim_alloc_count, shim_free_count, shim_alloc_bytes, shim_live_bytes, shim_peak_live;

static void fail(const char *m) {
  size_t n = 0; while (m[n]) n++;
  (void)!write(2, m, n);
  _exit(99);
}

static void arena_init(void) {
  void *p = mmap((void *)ARENA_BASE, ARENA_SIZE, PROT_READ | PROT_WRITE,
                 MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE | MAP_FIXED_NOREPLACE, -1, 0);
  if (p != (void *)ARENA_BASE) fail("libc_shim: cannot map arena at fixed base\n");
  arena = p;
  const char *e = getenv("SHIM_PAD");
  if (e) {
    size_t k = 0;
    for (; *e >= '0' && *e <= '9'; e++) k = k * 10 + (size_t)(*e - '0');
    if (k < 16 || (k & 15)) fail("libc_shim: SHIM_PAD must be a multiple of 16\n");
    pad = k;
  }
}

uintptr_t shim_arena_base(void) { return ARENA_BASE; }
size_t shim_arena_used(void) { return bump; }

void *malloc(size_t n) {
  if (!arena) arena_init();
  size_t sz = (n + pad - 1) / pad * pad;
  if (sz == 0) sz = pad;
  if (bump + HDR + sz > ARENA_SIZE) fail("libc_shim: arena exhausted\n");
  unsigned char *p = arena + bump + HDR;
  ((size_t *)(p - HDR))[0] = n;
  bump += HDR + sz;
  shim_alloc_count++;
  shim_alloc_bytes += n;
  shim_live_bytes += n;
  if (shim_live_bytes > shim_peak_live) shim_peak_live = shim_live_bytes;
  return p;
}

static int in_arena(const void *p) {
  return arena && (uintptr_t)p >= (uintptr_t)arena && (uintptr_t)p < (uintptr_t)arena + ARENA_SIZE;
}

void free(void *p) {
  if (!p || !in_arena(p)) return;   /* pointers from ld.so's early allocator */
  shim_free_count++;
  shim_live_bytes -= ((size_t *)((unsigned char *)p - HDR))[0];
}

size_t malloc_usable_size(void *p) {
  return p && in_arena(p) ? ((size_t *)((unsigned char *)p - HDR))[0] : 0;
}

void *calloc(size_t a, size_t b) {
  size_t n = a * b;
  if (b && n / b != a) return 0;
  unsigned char *p = malloc(n);
  for (size_t i = 0; i < n; i++) p[i] = 0;   /* bump memory is fresh, but be explicit */
  return p;
}

void *realloc(void *p, size_t n) {
  if (!p) return malloc(n);
  size_t old = malloc_usable_size(p);
  unsigned char *q = malloc(n);
  size_t m = old < n ? old : n;
  for (size_t i = 0; i < m; i++) q[i] = ((unsigned char *)p)[i];
  free(p);
  return q;
}

void *aligned_alloc(size_t al, size_t n) {
  if (al <= 16) return malloc(n);
  unsigned char *p = malloc(n + al);
  uintptr_t a = ((uintptr_t)p + al - 1) & ~(uintptr_t)(al - 1);
  if (a != (uintptr_t)p) {   /* keep a valid header in front of the aligned block */
    if (a - (uintptr_t)p < HDR) a += al;
    ((size_t *)(a - HDR))[0] = n;
  }
  return (void *)a;
}
void *memalign(size_t al, size_t n) { return aligned_alloc(al, n); }
int posix_memalign(void **out, size_t al, size_t n) { *out = aligned_alloc(al, n); return 0; }

int memcmp(const void *a, const void *b, size_t n) {
  const unsigned char *x = a, *y = b;
  for (size_t i = 0; i < n; i++)
    if (x[i] != y[i]) return x[i] < y[i] ? -1 : 1;
  return 0;
}
int bcmp(const void *a, const void *b, size_t n) { return memcmp(a, b, n); }

void *memchr(const void *s, int c, size_t n) {
  const unsigned char *p = s;
  for (size_t i = 0; i < n; i++)
    if (p[i] == (unsigned char)c) return (void *)(p + i);
  return 0;
}

size_t strlen(const char *s) { size_t n = 0; while (s[n]) n++; return n; }

int strcmp(const char *a, const char *b) {
  while (*a && *a == *b) { a++; b++; }
  return (unsigned char)*a - (unsigned char)*b;
}
int strncmp(const char *a, const char *b, size_t n) {
  for (; n; n--, a++, b++) {
    if (*a != *b) return (unsigned char)*a - (unsigned char)*b;
    if (!*a) return 0;
  }
  return 0;
}
char *strchr(const char *s, int c) {
  for (;; s++) {
    if (*s == (char)c) return (char *)s;
    if (!*s) return 0;
  }
}
char *strrchr(const char *s, int c) {
  const char *r = 0;
  for (;; s++) {
    if (*s == (char)c) r = s;
    if (!*s) return (char *)r;
  }
}
size_t strspn(const char *s, const char *acc) {
  size_t n = 0;
  for (; s[n]; n++) {
    const char *a = acc;
    while (*a && *a != s[n]) a++;
    if (!*a) break;
  }
  return n;
}
size_t strcspn(const char *s, const char *rej) {
  size_t n = 0;
  for (; s[n]; n++) {
    const char *r = rej;
    while (*r && *r != s[n]) r++;
    if (*r) break;
  }
  return n;
}

struct tm;
struct tm *localtime(const void *t) {
  (void)t;
  fail("libc_shim: localtime reached (no time-zone device model)\n");
  return 0;
}
