/* Independent numerical fixture for N33 carrier probes, not a production
 * soft-float library. libquadmath supplies binary128 sin; double-double values
 * are assembled numerically, then split high/residual (APFloat carrier order).
 * Only the tagged witness vectors are asserted by this fixture. */
#include <stdint.h>
#include <string.h>
extern __float128 sinq(__float128);
typedef unsigned __int128 U;
U __bennett_sf_sin_f128(U bits) {
    __float128 x,r;
    memcpy(&x,&bits,16);r=sinq(x);memcpy(&bits,&r,16);return bits;
}
U __bennett_sf_sin_ppcf128(U bits) {
    uint64_t h=(uint64_t)bits,l=bits>>64;double hi,lo;
    memcpy(&hi,&h,8);memcpy(&lo,&l,8);
    __float128 r=sinq((__float128)hi+(__float128)lo);
    hi=(double)r;lo=(double)(r-(__float128)hi);
    memcpy(&h,&hi,8);memcpy(&l,&lo,8);
    return (U)l<<64|h;
}
