// Test-only stub to give Julia something to dlopen; NOT part of the ABI deliverable.
#include <stdint.h>
#include <stdio.h>
void *__bennett_qalloc(uint64_t c, uint64_t n){ printf("qalloc %lu %lu\n",c,n); return (void*)0x1000; }
void __bennett_gate(uint32_t op, void*h, uint64_t i){ printf("gate %u %lu\n",op,i); }
void __bennett_ctrl(void*q,uint64_t qi,void(*f)(void*),uint64_t b,void*env){ printf("ctrl\n"); f(env); }
_Bool __bennett_measure(void*h,uint64_t i){ return 1; }
