/* Independent primitive/wrapper trace fixture, not a production allocator. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include <limits.h>
struct record { uint64_t base, requested, old_bump; };
struct heap { unsigned char bytes[32]; uint64_t bump,count,limit; struct record records[32]; };
static unsigned alloc(struct heap *h,uint64_t n,uint64_t *p){
 uint64_t extent=n?n:1;
 if(extent>h->limit || h->bump>h->limit-extent || h->count==32)return 2;
 *p=4096+h->bump;
 h->records[h->count++]=(struct record){*p,n,h->bump};
 memset(h->bytes+h->bump,0,extent);h->bump+=extent;return 0;
}
static unsigned cmalloc(struct heap *h,uint64_t n,uint64_t *p){
 uint64_t size=n?n:1,unused;
 if(size>UINT64_MAX-15)return 2;
 uint64_t extent=(size+15)&~UINT64_C(15),pad=(-(4096+h->bump))&15;
 if(pad){unsigned code=alloc(h,pad,&unused);if(code)return code;}
 return alloc(h,extent,p);
}
/* Reverse the ordinary primitive allocation, restoring its pre-state bytes. */
static void reverse(struct heap *h){
 struct record r=h->records[--h->count];
 memset(h->bytes+r.old_bump,0xaa,h->bump-r.old_bump);h->bump=r.old_bump;
 memset(h->records+h->count,0,sizeof r);
}
int main(void){
 struct heap h={0};memset(h.bytes,0xaa,sizeof h.bytes);h.limit=32;
 struct heap initial=h;uint64_t p,q;unsigned a=alloc(&h,3,&p),b=cmalloc(&h,1,&q);
 printf("[%u,%u,%llu,%llu,%llu,%llu]\n",a,b,(unsigned long long)p,(unsigned long long)q,(unsigned long long)(4096+h.bump),(unsigned long long)h.count);
 for(unsigned k=0;k<h.count;k++)printf("[%llu,%llu]\n",(unsigned long long)h.records[k].base,(unsigned long long)h.records[k].requested);
 unsigned nonzero=0;for(unsigned k=0;k<32;k++)nonzero|=h.bytes[k];printf("%u\n",nonzero);
 struct heap saved=h;unsigned code=alloc(&h,1,&q);printf("[%u,%d]\n",code,!memcmp(&saved,&h,sizeof h));
 code=cmalloc(&h,UINT64_MAX,&q);printf("[%u,%d]\n",code,!memcmp(&saved,&h,sizeof h));
 while(h.count)reverse(&h);printf("%d\n",!memcmp(&initial,&h,sizeof h));
 h=initial;alloc(&h,3,&p);saved=h;code=cmalloc(&h,UINT64_MAX,&q);
 printf("[%u,%d]\n",code,!memcmp(&saved,&h,sizeof h));
 /* Padding fails without mutation; extent failure preserves successful padding. */
 for(unsigned limit=3;limit<=31;limit+=28){
  h=initial;h.limit=limit;alloc(&h,3,&p);saved=h;
  code=cmalloc(&h,1,&q);
  printf("[%u,%llu,%llu,%d]\n",code,(unsigned long long)h.bump,(unsigned long long)h.count,limit==3?!memcmp(&saved,&h,sizeof h):h.records[1].requested==13);
 }
 h=initial;alloc(&h,0,&p);printf("[%llu,%llu,%llu,%u]\n",(unsigned long long)p,(unsigned long long)h.bump,(unsigned long long)h.records[0].requested,h.bytes[0]);
}
