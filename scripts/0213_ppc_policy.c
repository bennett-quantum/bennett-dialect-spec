/* Finite integer selector-policy fixture, not production PPC arithmetic.
 * Exact adjacency/midpoints are independently established with rational values
 * by dialect_0213.py; no host floating-point rounding supplies these results. */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

struct pair { uint64_t hi, lo; };
static unsigned parity(uint64_t bits) { return (unsigned)(bits & 1); }
/* Candidates here have equal high components or both have zero low components.
 * Their unsigned magnitude encodings therefore order their absolute sums. */
static unsigned smaller(struct pair a, struct pair b) {
    uint64_t ah=a.hi&INT64_MAX, bh=b.hi&INT64_MAX;
    return ah!=bh ? ah<bh : (a.lo&INT64_MAX)<(b.lo&INT64_MAX);
}
static struct pair nearest(struct pair a, struct pair b) {
    unsigned lows=(a.lo&INT64_MAX)||(b.lo&INT64_MAX);
    unsigned pa=parity(lows?a.lo:a.hi), pb=parity(lows?b.lo:b.hi);
    if(pa!=pb) return pa?b:a;
    return smaller(a,b)?a:b;
}
static void emit(struct pair p,unsigned flags) {
    printf("[\"%016" PRIx64 "\",\"%016" PRIx64 "\",%u]\n",p.hi,p.lo,flags);
}
int main(void) {
    const uint64_t highs[]={UINT64_C(0x3ff0000000000001),UINT64_C(0x0030000000000001),
                            UINT64_C(0x3ff0000000000000),UINT64_C(0x0030000000000000)};
    for(unsigned k=0;k<4;k++)for(unsigned neg=0;neg<2;neg++)for(unsigned r=0;r<5;r++)
    for(unsigned sticky=0;sticky<2;sticky++)for(unsigned observed=0;observed<2;observed++) {
        uint64_t sign=(uint64_t)neg<<63;
        struct pair near={highs[k]|sign,0}, far={highs[k]|sign,sign|1}, result;
        if(r==0) result=nearest(near,far);
        else if(r==1) result=neg?far:near;
        else if(r==2) result=neg?near:far;
        else if(r==3) result=near;
        else result=far;
        /* All these midpoints round to a normal total: inexact, no underflow. */
        emit(result,32*sticky+(observed?16:0));
    }
    /* Two-zero-low subnormal neighbours: use high parity, final tiny total. */
    emit(nearest((struct pair){0,0},(struct pair){1,0}),24);
    emit(nearest((struct pair){1,0},(struct pair){2,0}),24);
    /* Exact representable values do not raise inexact. */
    emit((struct pair){highs[0],1},0);
    /* Exercise equal parity in both orders/signs. These are selector branch
     * tests only: no assertion that these synthetic candidates are adjacent. */
    emit(nearest((struct pair){highs[0],2},(struct pair){highs[0],4}),0);
    emit(nearest((struct pair){highs[0]|(UINT64_C(1)<<63),(UINT64_C(1)<<63)|4},
                 (struct pair){highs[0]|(UINT64_C(1)<<63),(UINT64_C(1)<<63)|2}),0);
    return 0;
}
