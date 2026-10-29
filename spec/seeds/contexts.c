/* Dialect §14.5/§14.6 materialised transition records. The normalised caller
 * performs the explicit propagation and resume dispatch; these functions do
 * not perform a native machine-stack jump. Input C uses the platform's
 * setjmp/ucontext as an independent reference. */
#include <stdint.h>
struct eh_state { int32_t active,selector;void *object; };
extern struct eh_state __bennett_rt_eh;
struct jump_record { void *frame;uint32_t site; };
void __bennett_rt_setjmp(struct jump_record *b,void *frame,uint32_t site) { b->frame=frame;b->site=site; }
void __bennett_rt_longjmp(struct jump_record *b,int32_t value) { __bennett_rt_eh=(struct eh_state){2,value?value:1,b}; }
struct fiber_record { void *frames;void *stack;uint64_t size;uint32_t resume; };
void __bennett_rt_fiber_switch(struct fiber_record *from,struct fiber_record *to) {
    (void)from;__bennett_rt_eh=(struct eh_state){3,0,to};
}
