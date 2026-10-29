/* Independent checker fixtures for dialect §11/§14/§17. Not production runtimes. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

_Noreturn void __bennett_nz_fault(uint64_t code) {
    fprintf(stderr, "__bennett_nz_fault(%llu)\n", (unsigned long long)code);
    exit(128 + (int)code);
}
static unsigned char heap[1 << 20], shadow[1 << 20];
static size_t hp, sp;
static struct { void *p; size_t n; int live; } allocations[1<<20];
static size_t allocation_count;
void *__bennett_nz_alloc(uint64_t n) {
    if (!n) n=1;
    if (n>sizeof heap-hp) __bennett_nz_fault(2);
    void *p=heap+hp; hp+=(size_t)n; memset(p,0,(size_t)n);
    allocations[allocation_count].p=p;allocations[allocation_count].n=(size_t)n;allocations[allocation_count++].live=1;return p;
}
void __bennett_nz_free(void *p) {
    if (!p)return;
    for(size_t k=0;k<allocation_count;k++)if(allocations[k].p==p && allocations[k].live){allocations[k].live=0;return;}
    __bennett_nz_fault(7);
}
void *__bennett_rt_ss_push(uint64_t n,uint64_t a) {
    if (!a || (a&(a-1))) __bennett_nz_fault(4);
    size_t p=(sp+sizeof(size_t)+a-1)&~(size_t)(a-1);
    if (n>sizeof shadow || p>sizeof shadow-n) __bennett_nz_fault(2);
    memcpy(shadow+p-sizeof(size_t),&sp,sizeof sp); sp=p+(size_t)n;
    memset(shadow+p,0,(size_t)n);return shadow+p;
}
void __bennett_rt_ss_pop(void *p) {
    size_t off=(unsigned char *)p-shadow;
    if (off<sizeof(size_t) || off>sp) __bennett_nz_fault(7);
    memcpy(&sp,shadow+off-sizeof(size_t),sizeof sp);
}
void __bennett_rt_memmove(void *d,const void *s,uint64_t n) { memmove(d,s,(size_t)n); }
void __bennett_rt_memset(void *d,uint8_t v,uint64_t n) { memset(d,v,(size_t)n); }
int32_t __bennett_rt_memcmp(const void *a,const void *b,uint64_t n) { return memcmp(a,b,(size_t)n); }
uint32_t __bennett_rt_ctpop_i32(uint32_t x) { uint32_t n=0;for (;x;x>>=1)n+=x&1;return n; }
struct eh_state { int32_t active, selector; void *object; } __bennett_rt_eh;
struct eh_pair { void *object; int32_t selector; };
void may_throw(int32_t x) { if (x&1) __bennett_rt_eh=(struct eh_state){1,1,(void *)(uintptr_t)1}; }
struct eh_pair __bennett_rt_eh_match(void *personality,const void *clauses) {
    (void)personality;
    const uint64_t *c=clauses;
    if (__bennett_rt_eh.active==1 && c[1]) {
        struct eh_pair p={__bennett_rt_eh.object,__bennett_rt_eh.selector};
        __bennett_rt_eh.active=0;return p;
    }
    return (struct eh_pair){__bennett_rt_eh.object,-1};
}
uint64_t __bennett_rt_syscall(uint64_t nr,uint64_t a1,uint64_t a2,uint64_t a3,uint64_t a4,uint64_t a5,uint64_t a6) {
    (void)a4;(void)a5;(void)a6;
    if (nr==1 && (a1==1 || a1==2)) return fwrite((const void *)(uintptr_t)a2,1,(size_t)a3,a1==1?stdout:stderr);
    __bennett_nz_fault(8);
}
/* Only the address is passed to the catch-all fixture; matching is above. */
int __gxx_personality_v0(void) { return 0; }
