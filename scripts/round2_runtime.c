/* Independent executable reference micro-runtime for round-2 lifecycle vectors. */
#include <stdint.h>
#include <stddef.h>
struct generation { unsigned steps, used, local, events, failed; };
unsigned round2_generate(struct generation *g, const unsigned *ops, size_t n) {
  for(size_t i=0;i<n;i++) {
    if(g->used==g->steps){g->failed=1;break;}
    ++g->used;
    switch(ops[i]) {
      case 0: ++g->local; ++g->events; break;
      case 1: ++g->events; break;
      case 2: if(!g->local)return 4;--g->local;++g->events;break;
      case 3: break;
      default: return 4;
    }
  }
  if(g->failed){g->events=0;g->local=0;return 1;}
  return g->local?4:0;
}
struct view { struct view *parent; unsigned shadow, written, value; };
unsigned round2_read(struct view *v) {
  if(v->written)return v->value;
  return v->parent?round2_read(v->parent):v->shadow;
}
struct object { unsigned k, shadow, arena, covered; };
unsigned round2_store(struct object *o,unsigned value) {
  if(o->k==2 && !o->covered)return 4;
  o->shadow=value;if(o->k==2)o->arena=value;return 0;
}
unsigned round2_release(struct object *o) {
  if(o->k==2)return 4;
  o->arena=0;return 0;
}
void round2_observe(struct object *o,unsigned measured) {
  o->shadow=measured;o->arena=0;o->k=0;o->covered=1;
}
