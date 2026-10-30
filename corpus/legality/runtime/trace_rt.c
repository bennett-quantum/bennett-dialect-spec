#define _GNU_SOURCE
#ifndef BENNETT_MARKERS_ABI
#define BENNETT_MARKERS_ABI 2
#endif
#include "../markers.h"
#include <inttypes.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#if defined(BENNETT_MARKERS_ABI) && BENNETT_MARKERS_ABI == 2
#define BUDGET_T const bennett_budget *
#else
#define BUDGET_T uint64_t
#endif

/* Keep this translation unit outside every optimizer/LTO invocation. */
enum { HANDLE_COUNT = 65536, HANDLE_STRIDE = 4096 };
static unsigned char *guard;
static unsigned char live[HANDLE_COUNT];
static uint64_t next_handle, measure_ordinal, input_bits;

static void die(const char *message) {
    fprintf(stderr, "trace runtime: %s\n", message);
    exit(90);
}
static void segv(int sig, siginfo_t *info, void *context) {
    (void)sig; (void)context;
    uintptr_t a = (uintptr_t)info->si_addr, start = (uintptr_t)guard;
    if (guard && a >= start && a - start < (size_t)HANDLE_COUNT * HANDLE_STRIDE) {
        static const char msg[] = "FAULT handle-deref\n";
        (void)write(STDOUT_FILENO, msg, sizeof(msg) - 1);
        _exit(86);
    }
    static const char msg[] = "FAULT host-segv\n";
    (void)write(STDOUT_FILENO, msg, sizeof(msg) - 1);
    _exit(87);
}
void bennett_trace_reset(int64_t input) {
    if (!guard) {
        void *p = mmap(NULL, (size_t)HANDLE_COUNT * HANDLE_STRIDE, PROT_NONE,
                       MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (p == MAP_FAILED) die("mmap failed");
        guard = p;
        struct sigaction action;
        memset(&action, 0, sizeof(action));
        action.sa_sigaction = segv;
        action.sa_flags = SA_SIGINFO;
        if (sigemptyset(&action.sa_mask) || sigaction(SIGSEGV, &action, NULL))
            die("sigaction failed");
    }
    memset(live, 0, sizeof(live));
    next_handle = measure_ordinal = 0;
    input_bits = (uint64_t)input;
}
static const char *handle(bq h, char *buf) {
    uintptr_t a = (uintptr_t)h, start = (uintptr_t)guard;
    if (!guard || a < start || a - start >= (size_t)HANDLE_COUNT * HANDLE_STRIDE ||
        (a - start) % HANDLE_STRIDE) return "BADHANDLE";
    size_t k = (a - start) / HANDLE_STRIDE;
    if (k >= next_handle || !live[k]) return "BADHANDLE";
    snprintf(buf, 32, "H%zu", k);
    return buf;
}
/* Region pointers print as raw addresses, "F@0x<hex>". The harness links
 * non-PIE executables and resolves each address against the executable's full
 * symbol table (local symbols included; dladdr cannot see those). */
static const char *symbol(void *f, char *buf) {
    snprintf(buf, 32, "F@0x%" PRIxPTR, (uintptr_t)f);
    return buf;
}
static bq alloc(const char *op, uint64_t cls, uint64_t n) {
    if (next_handle == HANDLE_COUNT) die("handle capacity exceeded");
    size_t k = next_handle++;
    live[k] = 1;
    printf("%s H%zu %" PRIu64 " %" PRIu64 "\n", op, k, cls, n);
    return (bq)(guard + k * HANDLE_STRIDE);
}
bq __bennett_qalloc(uint64_t cls, uint64_t n) { return alloc("QALLOC", cls, n); }
bq __bennett_qborrow(uint64_t cls, uint64_t n) { return alloc("QBORROW", cls, n); }
void __bennett_qfree(bq h) {
    char b[32]; const char *s = handle(h, b);
    printf("QFREE %s\n", s);
    if (s == b) live[((uintptr_t)h - (uintptr_t)guard) / HANDLE_STRIDE] = 0;
}
void __bennett_gate(uint32_t op, bq h, uint64_t i) {
    char b[32]; printf("GATE %" PRIu32 " %s %" PRIu64 "\n", op, handle(h,b), i);
}
void __bennett_gate2(uint32_t op, bq a, uint64_t i, bq b, uint64_t j) {
    char x[32], y[32];
    printf("GATE2 %" PRIu32 " %s %" PRIu64 " %s %" PRIu64 "\n", op, handle(a,x), i, handle(b,y), j);
}
void __bennett_rot(uint32_t op, bq h, uint64_t i, double theta) {
    char b[32]; uint64_t bits;
    _Static_assert(sizeof(bits) == sizeof(theta), "requires 64-bit double");
    memcpy(&bits, &theta, sizeof(bits));
    printf("ROT %" PRIu32 " %s %" PRIu64 " 0x%016" PRIx64 "\n", op, handle(h,b), i, bits);
}
bool __bennett_measure(bq h, uint64_t i) {
    char b[32];
    uint64_t k = measure_ordinal++;
    uint64_t z = input_bits + (k + 1) * UINT64_C(0x9e3779b97f4a7c15);
    z = (z ^ (z >> 30)) * UINT64_C(0xbf58476d1ce4e5b9);
    z = (z ^ (z >> 27)) * UINT64_C(0x94d049bb133111eb);
    bool bit = (z ^ (z >> 31)) & 1;
    printf("MEASURE %s %" PRIu64 " %" PRIu64 " %u\n", handle(h,b), i, k, (unsigned)bit);
    return bit;
}
void __bennett_qload(bq dst, bq mem, bq addr) {
    char a[32], b[32], c[32]; printf("QLOAD %s %s %s\n", handle(dst,a), handle(mem,b), handle(addr,c));
}
void __bennett_qstore(bq mem, bq addr, bq val) {
    char a[32], b[32], c[32]; printf("QSTORE %s %s %s\n", handle(mem,a), handle(addr,b), handle(val,c));
}
#if BENNETT_MARKERS_ABI == 2
static void print_budget(const bennett_budget *budget) {
    if (!budget) { printf("0"); return; }
    char h[32];
    printf("steps=%" PRIu64 " heap=%" PRIu64 " stack=%" PRIu64 " depth=%" PRIu64 " fault=%s",
           budget->steps, budget->heap, budget->stack, budget->depth,
           budget->fault ? handle(budget->fault, h) : "null");
}
#else
static void print_budget(uint64_t budget) { printf("%" PRIu64, budget); }
#endif
void __bennett_ctrl(bq q, uint64_t qi, bregion f, BUDGET_T budget, void *env) {
    char b[32], s[32]; printf("CTRL %s %" PRIu64 " %s ", handle(q,b), qi, symbol((void *)f, s));
    print_budget(budget); putchar('\n');
    f(env); puts("END CTRL");
}
#if defined(BENNETT_MARKERS_ABI) && BENNETT_MARKERS_ABI == 2
void __bennett_adj(bregion f, const bennett_budget *budget, void *env) {
    (void)budget;
#else
void __bennett_adj(bregion f, void *env) {
#endif
    char s[32]; printf("ADJ %s\n", symbol((void *)f, s)); f(env); puts("END ADJ");
}
#if defined(BENNETT_MARKERS_ABI) && BENNETT_MARKERS_ABI == 2
void __bennett_compute(bregion f, bregion use, const bennett_budget *budget, void *env) {
    (void)budget;
#else
void __bennett_compute(bregion f, bregion use, void *env) {
#endif
    char s[32], t[32]; printf("COMPUTE %s %s\n", symbol((void *)f, s), symbol((void *)use, t));
    f(env); use(env); f(env); puts("END COMPUTE");
}
void __bennett_reversible(bregion f, BUDGET_T budget, void *env) {
    char s[32]; printf("REVERSIBLE %s ", symbol((void *)f, s));
    print_budget(budget); putchar('\n'); f(env); puts("END REVERSIBLE");
}
#if defined(BENNETT_MARKERS_ABI) && BENNETT_MARKERS_ABI == 2
void __bennett_inplace(const void *g, const void *ginv, const bennett_budget *budget, const bennett_oracle_desc *desc) {
    (void)g; (void)ginv; (void)budget; (void)desc;
    die("ABI 0.2 inplace requires the ISA executor");
}
void __bennett_oracle(const void *f, const bennett_budget *budget, const bennett_oracle_desc *desc) {
    (void)f; (void)budget; (void)desc;
    die("ABI 0.2 oracle requires the ISA executor");
}
#else
void __bennett_inplace(bregion g, bregion ginv, void *env) {
    char s[32], t[32]; printf("INPLACE %s %s\n", symbol((void *)g, s), symbol((void *)ginv, t)); g(env); puts("END INPLACE");
}
#endif
void __bennett_ctrl_v(bq q, uint64_t qi, void *f, uint64_t budget, ...) {
    char b[32], s[32]; printf("CTRL_V %s %" PRIu64 " %s %" PRIu64 "\n", handle(q,b), qi, symbol(f, s), budget);
}
