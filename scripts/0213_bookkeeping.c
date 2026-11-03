/* Independent ordinary-metadata fixture, not a consumer runtime implementation.
 * The finite arena below bounds this test, not the permitted allocator domain. */
#include <assert.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

struct record { uint64_t base, requested, live; };
struct heap { unsigned char bytes[96]; uint64_t bump,count,limit; struct record records[16]; };
static unsigned alloc(struct heap *h,uint64_t n,uint64_t *p) {
    uint64_t extent=n?n:1;
    if(extent>h->limit || h->bump>h->limit-extent || h->count==16)return 2;
    *p=4096+h->bump;
    h->records[h->count++]=(struct record){*p,n,1};
    memset(h->bytes+h->bump,0,extent); h->bump+=extent; return 0;
}
static void store64(struct heap *h,uint64_t p,uint64_t value) {
    for(unsigned k=0;k<8;k++)h->bytes[p-4096+k]=(unsigned char)(value>>(8*k));
}
static uint64_t load64(struct heap *h,uint64_t p) {
    uint64_t value=0;for(unsigned k=0;k<8;k++)value|=(uint64_t)h->bytes[p-4096+k]<<(8*k);
    return value;
}
static unsigned body(struct heap *h,uint64_t *result) {
    uint64_t raw,probe,padding,payload,metadata;
    unsigned code=alloc(h,3,&raw); if(code)return code;
    code=alloc(h,0,&probe); if(code)return code;
    uint64_t pad=(-(probe+1))&15;
    if(pad){code=alloc(h,pad,&padding);if(code)return code;}
    code=alloc(h,16,&payload);if(code)return code;
    code=alloc(h,32,&metadata);if(code)return code;
    store64(h,metadata,payload); store64(h,metadata+8,1); /* original C byte count */
    store64(h,metadata+16,1); store64(h,metadata+24,0); /* liveness and next */
    *result=payload;return 0;
}
static void vector(uint64_t limit) {
    struct heap h={0};h.limit=limit;struct heap initial=h;
    /* The native fixture checks the forward prefix and identical replay;
     * the independent Rust executor checks actual ISA reversal. */
    uint64_t result=0;unsigned code=body(&h,&result);struct heap saved=h;
    printf("[%" PRIu64 ",%u,%" PRIu64 ",%" PRIu64 ",%" PRIu64 "]\n",limit,code,result,4096+h.bump,h.count);
    for(uint64_t k=0;k<h.count;k++)printf("[%" PRIu64 ",%" PRIu64 "]\n",h.records[k].base,h.records[k].requested);
    if(!code) {
        assert(load64(&h,4128)==4112 && load64(&h,4136)==1);
        assert(load64(&h,4144)==1 && load64(&h,4152)==0);
        /* A realloc(48) copy must preserve the original one byte, not 16. */
        unsigned char dest[48];memset(dest,0xcc,sizeof dest);h.bytes[16]=0x5a;
        uint64_t n=load64(&h,4136);memcpy(dest,h.bytes+16,n<48?n:48);
        assert(dest[0]==0x5a && dest[1]==0xcc);h=saved;
        puts("[4112,1,1,0]");
    }
    h=initial;uint64_t replay=0;unsigned replay_code=body(&h,&replay);
    assert(replay_code==code && replay==result && !memcmp(&h,&saved,sizeof h));
}
int main(void) {
    /* Every allocation failure boundary, plus enough heap for the full body. */
    const uint64_t limits[]={2,3,4,31,32,63,64};
    for(unsigned k=0;k<sizeof limits/sizeof *limits;k++)vector(limits[k]);
    return 0;
}
