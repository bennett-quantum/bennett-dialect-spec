#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
extern uint64_t __bennett_sf_add_f64(uint64_t,uint64_t),__bennett_sf_mul_f64(uint64_t,uint64_t);
extern uint64_t __bennett_sf_fpext_f32_f64(uint32_t);
static uint64_t rng=0xd531a35816c48e19ULL;
static uint64_t random64(void){rng^=rng<<13;rng^=rng>>7;rng^=rng<<17;return rng;}
static uint64_t canonical(uint64_t x){return (x&0x7ff0000000000000ULL)==0x7ff0000000000000ULL && (x&0xfffffffffffffULL)?0x7ff8000000000000ULL:x;}
int main(void) {
 if(__bennett_sf_add_f64(0x3ff0000000000000ULL,0x3ff0000000000000ULL)!=0x4000000000000000ULL)return 1;
 for(unsigned i=0;i<100000;i++){
  uint64_t a=random64(),b=random64(),ea,em;double x,y,z;memcpy(&x,&a,8);memcpy(&y,&b,8);
  z=x+y;memcpy(&ea,&z,8);z=x*y;memcpy(&em,&z,8);
  uint64_t aa=__bennett_sf_add_f64(a,b),mm=__bennett_sf_mul_f64(a,b);
  if(aa!=canonical(ea)||mm!=canonical(em)){fprintf(stderr,"seed mismatch a=%llx b=%llx add=%llx expected=%llx mul=%llx expected=%llx\n",(unsigned long long)a,(unsigned long long)b,(unsigned long long)aa,(unsigned long long)ea,(unsigned long long)mm,(unsigned long long)em);return 2;}
 }
 if(exp(0.0)!=1.0 || log(1.0)!=0.0)return 3;
 puts("100000 binary64 add/mul vectors and musl exp/log anchors passed");return 0;
}
