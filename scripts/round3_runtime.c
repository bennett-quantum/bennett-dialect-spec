/* Contract micro-runtime: logical frames are distinct from backing storage. */
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
struct frame { uint64_t base, end; unsigned live; };
struct stack { unsigned char bytes[16]; struct frame frames[8]; unsigned count; uint64_t top; };
static uint64_t ss_push(struct stack *s,uint64_t size) {
    if(s->count==8 || size>16-s->top)abort();
    uint64_t base=s->top;s->top+=size;
    s->frames[s->count++]=(struct frame){base,s->top,1};
    memset(s->bytes+base,0,size);return base;
}
static void ss_pop(struct stack *s,uint64_t base) {
    unsigned k=s->count;while(k && s->frames[k-1].base!=base)k--;
    if(!k)abort();
    s->top=base;for(unsigned j=k-1;j<s->count;j++)s->frames[j].live=0;
    s->count=k-1;
}
static void ss_restore(struct stack *s,uint64_t top) {
    if(top>s->top)abort();
    for(unsigned j=0;j<s->count;j++) {
        struct frame *f=&s->frames[j];
        if(f->base>=top)f->live=0;
        else if(f->end>top)f->end=top;
    }
    s->top=top;
}
static unsigned ss_check(const struct stack *s,uint64_t p,uint64_t n) {
    if(p+n<p)return 7;
    for(unsigned j=0;j<s->count;j++) {
        const struct frame *f=&s->frames[j];
        if(f->live && p>=f->base && p+n<=f->end)return 0;
    }
    return 7;
}
static unsigned ss_store(struct stack *s,uint64_t p,unsigned char v) {
    unsigned code=ss_check(s,p,1);if(!code)s->bytes[p]=v;return code;
}
static unsigned ss_load(const struct stack *s,uint64_t p,unsigned *code) {
    *code=ss_check(s,p,1);return *code?0:s->bytes[p];
}
