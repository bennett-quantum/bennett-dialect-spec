#include <errno.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
extern int64_t case_entry(int64_t x);
extern void bennett_trace_reset(int64_t x);
int main(int argc, char **argv) {
    if (argc < 2) { fputs("driver: expected one or more signed i64 inputs\n", stderr); return 64; }
    if (setvbuf(stdout, NULL, _IONBF, 0)) { perror("setvbuf"); return 65; }
    for (int i = 1; i < argc; ++i) {
        char *end; errno = 0;
        intmax_t x = strtoimax(argv[i], &end, 10);
        if (errno || !argv[i][0] || *end || x < INT64_MIN || x > INT64_MAX) {
            fprintf(stderr, "driver: invalid signed i64 input: %s\n", argv[i]); return 64;
        }
        bennett_trace_reset((int64_t)x);
        printf("IN %" PRId64 "\n", (int64_t)x);
        int64_t result = case_entry((int64_t)x);
        printf("RET %" PRId64 "\n", result);
    }
    return 0;
}
