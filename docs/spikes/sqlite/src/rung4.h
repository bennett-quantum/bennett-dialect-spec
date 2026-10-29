#ifndef RUNG4_H
#define RUNG4_H
#include <stdint.h>

#define ORACLE_ERR 2

typedef struct { char name[24]; char city[12]; int64_t age; int64_t score; } row_t;
typedef uint8_t (*oracle_fn)(uint64_t rowid);

extern const char *const QUERY;
void gen_row(uint64_t rowid, row_t *r);
int ref_match(uint64_t n, uint64_t rowid);
void host_setup(uint64_t n);           /* rows + database image */
void host_setup_prepared(void);        /* V2 host connection + statement */
uint8_t oracle(uint64_t rowid);        /* V1: the rung-4 oracle */
uint8_t oracle_prepared(uint64_t rowid);
uint8_t oracle_rebuild(uint64_t rowid);
oracle_fn oracle_by_name(const char *v);

extern long long g_db_image_len;
extern uint64_t g_nrows;
#endif
