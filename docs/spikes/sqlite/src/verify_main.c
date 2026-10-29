/* Native verification of the rung-4 oracle shapes.
 *   verify <deser|prepared|rebuild> <N>
 * Builds the database of N rows, then for every rowid in [0, N+1] checks
 * oracle(rowid) against the independent C predicate ref_match.  Exit status
 * is non-zero on any mismatch or ORACLE_ERR (fail loud). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "rung4.h"

static double now(void) {
  struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
  return ts.tv_sec + ts.tv_nsec * 1e-9;
}

int main(int argc, char **argv) {
  if (argc != 3 && argc != 4) {
    fprintf(stderr, "usage: %s <deser|prepared|rebuild> <N> [stride]\n", argv[0]);
    return 2;
  }
  const char *variant = argv[1];
  uint64_t n = strtoull(argv[2], 0, 0);
  uint64_t stride = argc == 4 ? strtoull(argv[3], 0, 0) : 1;
  oracle_fn f = oracle_by_name(variant);
  double t0 = now();
  host_setup(n);
  if (!strcmp(variant, "prepared")) host_setup_prepared();
  double t1 = now();
  uint64_t matches = 0, checked = 0, bad = 0;
  for (uint64_t r = 0; r <= n + 1; r += (r == 0 || r >= n) ? 1 : stride) {
    uint8_t got = f(r);
    int want = ref_match(n, r);
    checked++;
    if (got == 1) matches++;
    if (got != (uint8_t)want) {
      bad++;
      if (bad < 10) fprintf(stderr, "MISMATCH rowid=%llu got=%u want=%d\n",
                            (unsigned long long)r, got, want);
    }
  }
  double t2 = now();
  printf("variant=%s N=%llu image_bytes=%lld checked=%llu matches=%llu mismatches=%llu "
         "setup_s=%.3f per_call_us=%.2f\n",
         variant, (unsigned long long)n, g_db_image_len, (unsigned long long)checked,
         (unsigned long long)matches, (unsigned long long)bad, t1 - t0,
         (t2 - t1) / (double)checked * 1e6);
  if (bad) { printf("FAIL\n"); return 1; }
  printf("PASS\n");
  return 0;
}
