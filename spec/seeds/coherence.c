/* Independent native contract fixtures, dialect 0.2.1 §10 and §20.6. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdlib.h>

struct bennett_seed_object {
    unsigned char shadow[32], arena[32], covered[32];
    size_t size;
    unsigned k; /* Cl=0, M=1, Co=2 */
};
unsigned bennett_seed_cc_store(struct bennett_seed_object *o,size_t off,unsigned char value) {
    if(off>=o->size)return 7;
    if(o->k==2) {
        if(!o->covered[off])return 4;
        o->arena[off]=value;o->shadow[off]=value;
        return 0; /* the covering write is this known classical store */
    }
    if(o->k==1) {
        for(size_t i=0;i<o->size;i++)o->arena[i]^=o->shadow[i];
        o->k=0;
    }
    o->shadow[off]=value;o->covered[off]=1;return 0;
}
void bennett_seed_materialise(struct bennett_seed_object *o) {
    if (o->k==0) {
        for(size_t i=0;i<o->size;i++)o->arena[i]^=o->shadow[i];
        o->k=1;
    }
}
void bennett_seed_mask(struct bennett_seed_object *o,size_t off,unsigned char m,int controlled) {
    if(off>=o->size)abort();
    if(controlled || o->k==2) {
        bennett_seed_materialise(o);o->arena[off]^=m;o->covered[off]=0;o->k=2;
    } else {
        if(o->k==1) {
            for(size_t i=0;i<o->size;i++)o->arena[i]^=o->shadow[i];
            o->k=0;
        }
        o->shadow[off]^=m;
    }
}
size_t bennett_seed_observe(struct bennett_seed_object *o,size_t off,size_t n,unsigned char *out,unsigned *widths) {
    if(off>o->size || n>o->size-off)abort();
    if(!n)return 0;
    size_t chunks=0;
    for(size_t pos=0;pos<n;) {
        size_t count=n-pos<16?n-pos:16;widths[chunks++]=(unsigned)(count*8);
        for(size_t j=0;j<count;j++) {
            size_t i=off+pos+j;out[pos+j]=o->k==0?o->shadow[i]:o->arena[i];
            o->shadow[i]=out[pos+j];o->covered[i]=1;
        }
        pos+=count;
    }
    int all=1;for(size_t i=0;i<o->size;i++)all&=o->covered[i];
    if(o->k==1 || all) {
        for(size_t i=0;i<o->size;i++)o->arena[i]^=o->shadow[i];
        o->k=0;
    }
    return chunks;
}

/* A real three-level Sv39 walk with canonical-address, permission and leaf
 * checks. Physical pages are supplied by a comparison-layout backing array. */
uint64_t bennett_seed_sv39(uint64_t va,uint64_t satp,const uint64_t tables[3][512],int write) {
    if(satp>>60!=8)return va;
    uint64_t upper=va>>39,sign=(va>>38)&1;
    if(upper!=(sign?((UINT64_C(1)<<25)-1):0))abort();
    uint64_t ppn=satp&((UINT64_C(1)<<44)-1);
    for(int level=2;level>=0;level--) {
        if(ppn<1 || ppn>3)abort();
        uint64_t pte=tables[ppn-1][(va>>(12+9*level))&511];
        if(!(pte&1) || (!(pte&2) && (pte&4)))abort();
        ppn=pte>>10;
        if(pte&10) {
            if(!(pte&64) || (write && (!(pte&4) || !(pte&128))))abort();
            unsigned low=9*(unsigned)level;
            if(ppn&((UINT64_C(1)<<low)-1))abort();
            return (ppn<<12)|(va&((UINT64_C(1)<<(12+low))-1));
        }
    }
    abort();
}
