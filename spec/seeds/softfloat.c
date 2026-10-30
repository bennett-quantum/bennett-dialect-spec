/* Integer-only binary64 fixtures, dialect §13.1. Round nearest, ties even. */
#include <stdint.h>
#include <limits.h>
typedef __uint128_t u128;
static const uint64_t QNAN=UINT64_C(0x7ff8000000000000), INF=UINT64_C(0x7ff0000000000000);
static uint64_t jam(uint64_t v,unsigned n) { return n==0?v:n<64?(v>>n)|((v<<(64-n))!=0):(v!=0); }
static uint64_t jam128(u128 v,unsigned n) { return n==0?(uint64_t)v:n<128?(uint64_t)(v>>n)|((v<<((128-n)))!=0):(v!=0); }
static uint64_t pack(unsigned sign,int e,uint64_t m) {
    if (!m) return (uint64_t)sign<<63;
    while (m>=(UINT64_C(1)<<56)) { m=jam(m,1);e++; }
    while (m<(UINT64_C(1)<<55) && e>1) {m<<=1;e--;}
    if (e<=0) {m=jam(m,(unsigned)(1-e));e=1;}
    unsigned low=m&7;uint64_t q=m>>3;
    if (low>4 || (low==4 && (q&1))) q++;
    if (q>=(UINT64_C(1)<<53)) {q>>=1;e++;}
    if (e>=2047)return ((uint64_t)sign<<63)|INF;
    if (q<(UINT64_C(1)<<52))e=0;
    return ((uint64_t)sign<<63)|((uint64_t)e<<52)|(q&UINT64_C(0xfffffffffffff));
}
uint64_t __bennett_sf_add_f64(uint64_t a,uint64_t b) {
    unsigned sa=a>>63,sb=b>>63;int ea=(a>>52)&2047,eb=(b>>52)&2047;
    uint64_t ma=a&UINT64_C(0xfffffffffffff),mb=b&UINT64_C(0xfffffffffffff);
    if ((ea==2047 && ma)||(eb==2047 && mb))return QNAN;
    if (ea==2047 || eb==2047) {if(ea==eb && sa!=sb)return QNAN;return ea==2047?a:b;}
    if(ea)ma|=UINT64_C(1)<<52;else ea=1;
    if(eb)mb|=UINT64_C(1)<<52;else eb=1;
    if(ea<eb || (ea==eb && ma<mb)){uint64_t t=ma;ma=mb;mb=t;int e=ea;ea=eb;eb=e;unsigned s=sa;sa=sb;sb=s;}
    ma<<=3;mb=jam(mb<<3,(unsigned)(ea-eb));
    if(sa==sb)return pack(sa,ea,ma+mb);
    if(ma==mb)return 0;
    return pack(sa,ea,ma-mb);
}
uint64_t __bennett_sf_mul_f64(uint64_t a,uint64_t b) {
    unsigned s=(a^b)>>63;int ea=(a>>52)&2047,eb=(b>>52)&2047;
    uint64_t ma=a&UINT64_C(0xfffffffffffff),mb=b&UINT64_C(0xfffffffffffff);
    if ((ea==2047 && ma)||(eb==2047 && mb))return QNAN;
    if (ea==2047 || eb==2047) {if((ea!=2047 && !(ea|ma))||(eb!=2047 && !(eb|mb)))return QNAN;return ((uint64_t)s<<63)|INF;}
    if (!(ea|ma)||!(eb|mb))return (uint64_t)s<<63;
    if(ea)ma|=UINT64_C(1)<<52;else ea=1;
    if(eb)mb|=UINT64_C(1)<<52;else eb=1;
    while(ma<(UINT64_C(1)<<52)){ma<<=1;ea--;}
    while(mb<(UINT64_C(1)<<52)){mb<<=1;eb--;}
    u128 prod=(u128)ma*mb;int e=ea+eb-1023;
    return pack(s,e,jam128(prod,49));
}
uint8_t __bennett_sf_cmp_f64(uint64_t a,uint64_t b,uint32_t p) {
    int nan=((a&INF)==INF && (a&UINT64_C(0xfffffffffffff)))||((b&INF)==INF && (b&UINT64_C(0xfffffffffffff)));
    int eq=a==b || ((a<<1)==0 && (b<<1)==0);
    int lt=!eq && ((a>>63)!=(b>>63)?(a>>63):(a>>63)?a>b:a<b);
    int ord=!nan;int gt=!lt&&!eq;
    switch(p){case 0:return 0;case 1:return ord&&eq;case 2:return ord&&gt;case 3:return ord&&(gt||eq);case 4:return ord&&lt;case 5:return ord&&(lt||eq);case 6:return ord&&!eq;case 7:return ord;case 8:return nan;case 9:return nan||eq;case 10:return nan||gt;case 11:return nan||gt||eq;case 12:return nan||lt;case 13:return nan||lt||eq;case 14:return nan||!eq;case 15:return 1;default:return 0;}
}
uint64_t __bennett_sf_fpext_f32_f64(uint32_t a) {
    unsigned s=a>>31;int e=(a>>23)&255;uint64_t m=a&0x7fffff;
    if(e==255)return m?QNAN:((uint64_t)s<<63)|INF;
    if(!e){if(!m)return (uint64_t)s<<63;e=1;while(m<(UINT64_C(1)<<23)){m<<=1;e--;}m&=0x7fffff;}
    return ((uint64_t)s<<63)|((uint64_t)(e+896)<<52)|(m<<29);
}
__uint128_t __bennett_sf_fptoui_f64(uint64_t a,uint32_t width) {
    int ef=(a>>52)&2047,e=ef-1023;uint64_t frac=a&UINT64_C(0xfffffffffffff);
    u128 max=width==128?~(u128)0:((u128)1<<width)-1;
    if ((ef==2047 && frac)||(a>>63)||e<0)return 0;
    if (ef==2047 || e>=(int)width)return max;
    u128 m=(u128)(frac|(UINT64_C(1)<<52));return e>=52?m<<(e-52):m>>(52-e);
}
__int128_t __bennett_sf_fptosi_f64(uint64_t a,uint32_t width) {
    int ef=(a>>52)&2047,e=ef-1023;uint64_t frac=a&UINT64_C(0xfffffffffffff);unsigned sign=a>>63;
    u128 boundary=(u128)1<<(width-1);
    if ((ef==2047 && frac)||e<0)return 0;
    if (ef==2047 || e>=(int)width-1)return sign?-(__int128_t)(boundary-1)-1:(__int128_t)(boundary-1);
    u128 m=(u128)(frac|(UINT64_C(1)<<52));m=e>=52?m<<(e-52):m>>(52-e);
    return sign?-(__int128_t)m:(__int128_t)m;
}
static uint64_t from_u128(u128 a,unsigned sign) {
    if (!a)return 0;
    int top=0;for(u128 n=a;n>>=1;)top++;
    uint64_t m=top>55?jam128(a,(unsigned)(top-55)):(uint64_t)a<<(55-top);
    return pack(sign,top+1023,m);
}
uint64_t __bennett_sf_uitofp_f64(u128 a) { return from_u128(a,0); }
uint64_t __bennett_sf_sitofp_f64(__int128_t a) { unsigned s=a<0;u128 u=s?(u128)(-(a+1))+1:(u128)a;return from_u128(u,s); }

/* §13.1 limb ABI: no integer-side truncation to i128. */
static unsigned limb_bit(const uint64_t *p,unsigned k){return (p[k/64]>>(k%64))&1;}
static uint64_t wide_to_f64(const uint64_t *p,unsigned width,unsigned is_signed){
    unsigned n=(width+63)/64,sign=is_signed&&limb_bit(p,width-1);uint64_t a[n],carry=sign;
    for(unsigned k=0;k<n;k++){uint64_t t=sign?~p[k]:p[k];a[k]=t+carry;carry=carry&&a[k]==0;}
    if(width%64)a[n-1]&=(UINT64_C(1)<<(width%64))-1;
    int top=(int)width-1;while(top>=0&&!limb_bit(a,top))top--;
    if(top<0)return 0;
    uint64_t m=0;for(unsigned j=0;j<56;j++)m=(m<<1)|((int)j<=top?limb_bit(a,top-j):0);
    for(int j=top-56;j>=0;j--)if(limb_bit(a,j)){m|=1;break;}
    return pack(sign,top+1023,m);
}
uint64_t __bennett_sf_sitofp_f64_wide(const uint64_t *p,uint32_t width){return wide_to_f64(p,width,1);}
uint64_t __bennett_sf_uitofp_f64_wide(const uint64_t *p,uint32_t width){return wide_to_f64(p,width,0);}
static void f64_to_wide(uint64_t *p,uint64_t a,unsigned width,unsigned is_signed){
    unsigned n=(width+63)/64,sign=a>>63,ef=(a>>52)&2047;int e=(int)ef-1023;
    uint64_t fraction=a&UINT64_C(0xfffffffffffff);for(unsigned k=0;k<n;k++)p[k]=0;
    if((ef==2047&&fraction)||e<0||(!is_signed&&sign))return;
    unsigned limit=width-is_signed;
    if(ef==2047||e>=(int)limit){
        if(is_signed&&sign){p[(width-1)/64]=UINT64_C(1)<<((width-1)%64);return;}
        for(unsigned k=0;k<limit;k++)p[k/64]|=UINT64_C(1)<<(k%64);return;
    }
    uint64_t m=fraction|(UINT64_C(1)<<52);
    for(int j=0;j<=52;j++){int dst=e-52+j;if(dst>=0&&(unsigned)dst<width&&((m>>j)&1))p[dst/64]|=UINT64_C(1)<<(dst%64);}
    if(sign){uint64_t carry=1;for(unsigned k=0;k<n;k++){uint64_t t=~p[k];p[k]=t+carry;carry=carry&&p[k]==0;}}
    if(width%64)p[n-1]&=(UINT64_C(1)<<(width%64))-1;
}
void __bennett_sf_fptosi_f64_wide(uint64_t *p,uint64_t a,uint32_t width){f64_to_wide(p,a,width,1);}
void __bennett_sf_fptoui_f64_wide(uint64_t *p,uint64_t a,uint32_t width){f64_to_wide(p,a,width,0);}
