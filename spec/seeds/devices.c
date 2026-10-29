/* Bounded deterministic buffers, dialect §11.3. */
#include <stdint.h>
#include <string.h>
#include <stddef.h>
extern _Noreturn void __bennett_nz_fault(uint64_t);
unsigned char *__bennett_dev_entropy_base;
uint64_t __bennett_dev_entropy_size,__bennett_dev_entropy_pos;
uint64_t __bennett_dev_clock_value;
unsigned char __bennett_dev_console_buffer[65536];
uint64_t __bennett_dev_console_size,__bennett_dev_console_pos;
void __bennett_dev_entropy_read(void *p,uint64_t n) {
    if(n>__bennett_dev_entropy_size-__bennett_dev_entropy_pos)__bennett_nz_fault(10);
    memcpy(p,__bennett_dev_entropy_base+__bennett_dev_entropy_pos,(size_t)n);__bennett_dev_entropy_pos+=n;
}
void __bennett_dev_clock_read(void *p) {
    uint64_t v=__bennett_dev_clock_value++;unsigned char *q=p;for(unsigned i=0;i<8;i++)q[i]=(unsigned char)(v>>(8*i));
}
void __bennett_dev_console_write(const void *p,uint64_t n) {
    uint64_t left=__bennett_dev_console_size-__bennett_dev_console_pos;if(n>left)n=left;
    if(__bennett_dev_console_pos+n>sizeof __bennett_dev_console_buffer)__bennett_nz_fault(7);
    memcpy(__bennett_dev_console_buffer+__bennett_dev_console_pos,p,(size_t)n);__bennett_dev_console_pos+=n;
}
