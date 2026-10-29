/* Minimal public math declarations for the vendored exp/log seed. This avoids
 * glibc private __sin/__cos names conflicting with musl's internal kernels. */
#ifndef BENNETT_SEED_MATH_H
#define BENNETT_SEED_MATH_H
typedef float float_t;
typedef double double_t;
#define INFINITY (__builtin_inff())
#define NAN (__builtin_nanf(""))
double exp(double);
double log(double);
#endif
