/* Independent host oracle, not a production bennett-arith implementation. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <fenv.h>
#include <float.h>
#pragma STDC FENV_ACCESS ON
static unsigned flags(void) {
 return (fetestexcept(FE_INVALID)?1:0) | (fetestexcept(FE_DIVBYZERO)?2:0) |
 (fetestexcept(FE_OVERFLOW)?4:0) | (fetestexcept(FE_UNDERFLOW)?8:0) |
 (fetestexcept(FE_INEXACT)?16:0);
}
int main(void) {
#if LDBL_MANT_DIG != 64 || LDBL_MAX_EXP != 16384
#error This independent f80 boundary oracle requires an x87 long double host
#endif
 volatile double hi=1.0, lo=0x1p-60;
 feclearexcept(FE_ALL_EXCEPT);
 volatile long double sum=(long double)hi+(long double)lo;
 unsigned char raw[sizeof sum];memcpy(raw,(const void*)&sum,sizeof sum);
 printf("[\"%02x%02x",raw[9],raw[8]);
 for(int k=7;k>=0;k--)printf("%02x",raw[k]);
 uint64_t hib,lob;memcpy(&hib,(const void*)&hi,8);memcpy(&lob,(const void*)&lo,8);
 printf("\",%u,%d]\n",flags(),hib==UINT64_C(0x3ff0000000000000) && lob==UINT64_C(0x3c30000000000000));
 const uint64_t one=UINT64_C(0x3ff0000000000000);
 for(int kind=0;kind<2;kind++)for(int pos=0;pos<2;pos++)for(int sticky=0;sticky<2;sticky++)
 for(int p=0;p<2;p++)for(int signaling=0;signaling<2;signaling++)for(int ignore=0;ignore<2;ignore++){
  uint64_t q=kind?UINT64_C(0x7ff0000000000042):UINT64_C(0x7ff8000000000042);
  uint64_t a=pos?one:q,b=pos?q:one,aa,bb;
  volatile double x,y;memcpy((void*)&x,&a,8);memcpy((void*)&y,&b,8);
  feclearexcept(FE_ALL_EXCEPT);if(sticky)feraiseexcept(FE_INEXACT);
  /* Evaluate unordered comparison before constant false/true predicates. */
  volatile int comparison;
  if(ignore)comparison=0; /* Constant predicates need no FP work in ignore mode. */
  else if(!signaling)comparison=isless(x,y);
  else comparison=(x<y);
  (void)comparison;
  memcpy(&aa,(const void*)&x,8);memcpy(&bb,(const void*)&y,8);
  printf("[%d,%u,%d]\n",p,flags(),aa==a && bb==b);
 }
 int modes[]={FE_TONEAREST,FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO,FE_TONEAREST};
 /* Exact +0 has no tie: nearest-away and nearest-even necessarily agree. */
 for(int r=0;r<5;r++){
  fesetround(modes[r]);feclearexcept(FE_ALL_EXCEPT);
  volatile long double zero=0.0L;volatile long double result=sinl(zero);
  printf("[%d,%d,%u]\n",r,result==0 && !signbit(result),flags());
 }
 return 0;
}
