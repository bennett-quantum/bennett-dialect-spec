/* Independent native byte oracle. A normal main return flushes the last
 * buffered bytes, which deliberately have no newline. Descriptor 2 is closed
 * without closing the stdout console sink. These expectations follow POSIX
 * close/write/writev/lseek and the stated C format, not an executor trace. */
#include <errno.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/uio.h>

int main(void) {
    struct iovec v = { .iov_base = "x", .iov_len = 1 };
    if (close(2) != 0) return 1;
    errno = 0;
    if (write(2, "x", 1) != -1 || errno != EBADF) return 2;
    errno = 0;
    if (writev(2, &v, 1) != -1 || errno != EBADF) return 3;
    errno = 0;
    if (lseek(2, 0, SEEK_SET) != -1 || errno != EBADF) return 4;
    if (printf("%s %d %u %x %c %05d %.3s", "xy", -7, 9u, 42u,
               'Z', 12, "abcdef") != 22) return 5;
    return 0;
}
