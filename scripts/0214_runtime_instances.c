/* Independent native fixture for the dialect 0.2.14 runtime-instance vector
 * (brt-vbi, §12.8): i257 arithmetic of a = 2^256+3, b = 2 in LLVM's
 * arbitrary-width integer type, printed as the five §12.7 limbs
 * [64,64,64,64,1] of the destination slot. ctpop writes a full W-bit result.
 * This is expected-value evidence, not a runtimes helper implementation. */
#include <stdint.h>
#include <stdio.h>

typedef unsigned _BitInt(257) u257;

static void limbs(const char *name, u257 v) {
  printf("[\"%s\"", name);
  for (int k = 0; k < 5; ++k) {
    unsigned width = k < 4 ? 64 : 1;
    unsigned long long limb = (unsigned long long)(v >> (64 * k));
    if (width < 64) limb &= (1ULL << width) - 1;
    printf(",%llu", limb);
  }
  printf("]\n");
}

static u257 ctpop(u257 v) {
  u257 n = 0;
  for (int i = 0; i < 257; ++i) n += (v >> i) & 1;
  return n;
}

int main(void) {
  volatile unsigned long long three = 3, two = 2;
  u257 a = ((u257)1 << 256) + (u257)three;
  u257 b = (u257)two;
  u257 product = a * b;
  limbs("a", a);
  limbs("product", product);
  limbs("ctpop_product", ctpop(product));
  limbs("ctpop_a", ctpop(a));
  return 0;
}
