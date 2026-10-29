/* Profile driver: profile <variant> <N> <outdir> [stride]
 *   deser       V1, cold: SQLite globals at their static images on entry, as
 *               ISA §3.7 prescribes for oracle memory.  The database image is
 *               built in a separate builder process, so this process never
 *               runs SQLite before the oracle.
 *   deser-warm  V1 after the host has already initialised SQLite in this
 *               process (sqlite3_initialize skipped inside the oracle).
 *   prepared    V2, statement prepared by the host (the snapshot model).
 *   rebuild     V0, cold: rows from a global image, database built inside.
 * One forked child per rowid in {0, 1, 1+stride, ..., N, N+1} runs the oracle
 * with instrumentation active. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>
#include "rung4.h"

extern unsigned char *g_db_image;
void prof_init(uintptr_t image_lo, uintptr_t image_len, uintptr_t heap_lo);
int prof_run_all(oracle_fn f, const uint64_t *rowids, uint64_t n, int (*ref)(uint64_t));
void prof_report(const char *dir);
uintptr_t shim_arena_base(void);
size_t shim_arena_used(void);

static uint64_t N;
static int ref(uint64_t r) { return ref_match(N, r); }

int main(int argc, char **argv) {
  if (argc != 4 && argc != 5) {
    fprintf(stderr, "usage: %s <deser|prepared|rebuild> <N> <outdir> [stride]\n", argv[0]);
    return 2;
  }
  const char *v = argv[1];
  int warm = !strcmp(v, "deser-warm") || !strcmp(v, "prepared");
  oracle_fn f = oracle_by_name(!strcmp(v, "deser-warm") ? "deser" : v);
  N = strtoull(argv[2], 0, 0);
  uint64_t stride = argc == 5 ? strtoull(argv[4], 0, 0) : 1;
  if (warm) {
    host_setup(N);
  } else {
    /* builder process: makes the image; this process stays SQLite-cold */
    size_t cap = 64 + (N + 64) * 256;
    unsigned char *sh = mmap(0, cap, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    pid_t pid = fork();
    if (pid == 0) {
      host_setup(N);
      if ((size_t)g_db_image_len + 8 > cap) _exit(4);
      memcpy(sh, &g_db_image_len, 8);
      memcpy(sh + 8, g_db_image, (size_t)g_db_image_len);
      _exit(0);
    }
    int st;
    waitpid(pid, &st, 0);
    if (!WIFEXITED(st) || WEXITSTATUS(st)) { fprintf(stderr, "builder failed\n"); return 3; }
    memcpy(&g_db_image_len, sh, 8);
    g_db_image = sh + 8;
    host_rows(N);
  }
  {  /* The image on its own read-only pages: footprint regions are exact and any
      * write into the database image faults the child (fails loud). */
    size_t len = (size_t)g_db_image_len;
    unsigned char *p = mmap(0, len, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    memcpy(p, g_db_image, len);
    mprotect(p, len, PROT_READ);
    g_db_image = p;
  }
  if (!strcmp(argv[1], "prepared")) host_setup_prepared();
  uint64_t cap = N / stride + 8, n = 0;
  uint64_t *rows = calloc(cap, sizeof *rows);
  for (uint64_t r = 0; r <= N + 1; r += (r == 0 || r >= N) ? 1 : stride) rows[n++] = r;
  {  /* reference run (the first child) = a middle rowid, not the absent row 0 */
    uint64_t t = rows[0]; rows[0] = rows[n / 2]; rows[n / 2] = t;
  }
  size_t used_before = shim_arena_used();
  prof_init((uintptr_t)g_db_image, (uintptr_t)g_db_image_len, shim_arena_base());
  int bad = prof_run_all(f, rows, n, ref);
  prof_report(argv[3]);
  printf("variant=%s cold=%d N=%llu runs=%llu host_heap_bytes=%zu image_bytes=%lld bad=%d\n", v, !warm,
         (unsigned long long)N, (unsigned long long)n, used_before, g_db_image_len, bad);
  return bad != 0;
}
