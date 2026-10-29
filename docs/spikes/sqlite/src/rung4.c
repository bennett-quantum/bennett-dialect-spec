/* Rung-4 program for the SQLite feasibility spike (north star §8 rung 4).
 *
 * Host part (classical, runs before oracle entry):
 *   - generate N rows deterministically (splitmix64), insert them into an
 *     in-memory database with ordinary INSERT statements,
 *   - serialise the database to its file image (sqlite3_serialize); the
 *     image is position independent and is the "database fixed classically
 *     before entry".
 *
 * Oracle part (the coherent region of rung 4):
 *   uint8_t oracle(uint64_t rowid)
 *     opens a fresh in-memory connection, attaches the image read-only
 *     through SQLite's own memdb VFS (sqlite3_deserialize, no copy), prepares
 *     the predicate query, binds ?1 = rowid, steps once, finalises, closes.
 *     Returns 1 if the row matches, 0 if not, ORACLE_ERR on any SQLite error.
 *
 * Two further oracle shapes are measured for the database-image question:
 *   oracle_prepared(rowid)  bind/step/reset on a statement prepared by the
 *                           host (needs the host heap as the entry image);
 *   oracle_rebuild(rowid)   creates the table and inserts all N rows inside
 *                           the oracle, then queries (needs only the row data
 *                           as a global image).
 *
 * The predicate is checked against an independent C implementation
 * (ref_match) over every rowid.
 *
 * Nothing here edits SQLite: it is the stock amalgamation plus build flags
 * (scripts/build.sh) and the OS shim in os_shim.c.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "sqlite3.h"
#include "rung4.h"

/* ------------------------------------------------------------------ data */

static const char *const FIRST[16] = {
  "Ada", "Brian", "Carmen", "Dmitri", "Elena", "Frank", "Grace", "Hans",
  "Ingrid", "Juan", "Kenji", "Lena", "Morgan", "Nadia", "Oscar", "Priya"};
static const char *const LAST[8] = {
  "Anders", "Baker", "Chandra", "Diaz", "Evans", "Fujita", "Gallo", "Hansen"};
static const char *const CITY[16] = {
  "Berlin", "Lagos", "Madrid", "Boston", "Lima", "Mumbai", "Oslo", "Paris",
  "Quito", "Rome", "Seoul", "Tokyo", "Utrecht", "Vienna", "Warsaw", "Zagreb"};

static uint64_t splitmix64(uint64_t x) {
  x += 0x9e3779b97f4a7c15ULL;
  x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
  x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
  return x ^ (x >> 31);
}

void gen_row(uint64_t rowid, row_t *r) {
  uint64_t h = splitmix64(rowid * 0x2545F4914F6CDD1DULL + 7);
  snprintf(r->name, sizeof r->name, "%s %s", FIRST[h & 15], LAST[(h >> 4) & 7]);
  snprintf(r->city, sizeof r->city, "%s", CITY[(h >> 7) & 15]);
  r->age = 18 + (int64_t)((h >> 11) % 73);   /* 18..90 */
  r->score = (int64_t)((h >> 20) % 1000);    /* 0..999 */
}

/* The SQL predicate. Representative mix:
 *   rowid = ?1                     B-tree seek on the superposed key
 *   name LIKE '%an%'               pattern matcher, UTF-8 decoding, case folding
 *   upper(substr(city,1,1)) IN (…) built-in scalar functions (called through
 *                                  SQLite's function-pointer table), result
 *                                  allocation, text comparison with collation
 *   age BETWEEN 25 AND 60          integer comparison
 *   (score*7 + age) % 11 = 3       integer arithmetic with overflow checks
 */
const char *const QUERY =
  "SELECT 1 FROM people WHERE rowid = ?1"
  " AND name LIKE '%an%'"
  " AND upper(substr(city, 1, 1)) IN ('B', 'L', 'M')"
  " AND age BETWEEN 25 AND 60"
  " AND (score * 7 + age) % 11 = 3";

static const char *const SCHEMA =
  "CREATE TABLE people(id INTEGER PRIMARY KEY, name TEXT NOT NULL,"
  " city TEXT NOT NULL, age INTEGER NOT NULL, score INTEGER NOT NULL)";

/* Independent reference for the predicate (ASCII data, so LIKE's ASCII
 * case folding equals tolower on these strings). */
static int ci_contains_an(const char *s) {
  for (; s[0] && s[1]; s++) {
    char a = s[0] | 0x20, b = s[1] | 0x20;
    if (a == 'a' && b == 'n') return 1;
  }
  return 0;
}
int ref_match(uint64_t n, uint64_t rowid) {
  if (rowid < 1 || rowid > n) return 0;
  row_t r; gen_row(rowid, &r);
  char c = r.city[0];
  if (c >= 'a' && c <= 'z') c -= 32;
  return ci_contains_an(r.name) && (c == 'B' || c == 'L' || c == 'M') &&
         r.age >= 25 && r.age <= 60 && (r.score * 7 + r.age) % 11 == 3;
}

/* ------------------------------------------------------------------ host */

static void die(sqlite3 *db, const char *what, int rc) {
  fprintf(stderr, "FATAL %s: rc=%d %s\n", what, rc, db ? sqlite3_errmsg(db) : "");
  exit(2);
}

static int insert_rows(sqlite3 *db, const row_t *rows, uint64_t n) {
  sqlite3_stmt *ins;
  int rc = sqlite3_exec(db, SCHEMA, 0, 0, 0);
  if (rc) return rc;
  rc = sqlite3_exec(db, "BEGIN", 0, 0, 0);
  if (rc) return rc;
  rc = sqlite3_prepare_v2(db, "INSERT INTO people VALUES(?1,?2,?3,?4,?5)", -1, &ins, 0);
  if (rc) return rc;
  for (uint64_t i = 0; i < n; i++) {
    sqlite3_bind_int64(ins, 1, (sqlite3_int64)(i + 1));
    sqlite3_bind_text(ins, 2, rows[i].name, -1, SQLITE_STATIC);
    sqlite3_bind_text(ins, 3, rows[i].city, -1, SQLITE_STATIC);
    sqlite3_bind_int64(ins, 4, rows[i].age);
    sqlite3_bind_int64(ins, 5, rows[i].score);
    rc = sqlite3_step(ins);
    if (rc != SQLITE_DONE) { sqlite3_finalize(ins); return rc; }
    sqlite3_reset(ins);
  }
  sqlite3_finalize(ins);
  return sqlite3_exec(db, "COMMIT", 0, 0, 0);
}

/* Classical inputs of the oracle, fixed before entry. */
unsigned char *g_db_image;      /* database file image (V1) */
sqlite3_int64 g_db_image_len;
row_t *g_rows;                  /* row data (V0) */
uint64_t g_nrows;
static sqlite3 *g_host_db;      /* host connection (V2) */
static sqlite3_stmt *g_host_stmt;

void host_setup(uint64_t n) {
  int rc;
  g_nrows = n;
  g_rows = calloc(n ? n : 1, sizeof(row_t));
  for (uint64_t i = 0; i < n; i++) gen_row(i + 1, &g_rows[i]);

  sqlite3 *db;
  rc = sqlite3_open(":memory:", &db);
  if (rc) die(db, "open", rc);
  rc = insert_rows(db, g_rows, n);
  if (rc) die(db, "insert", rc);
  g_db_image = sqlite3_serialize(db, "main", &g_db_image_len, 0);
  if (!g_db_image) die(db, "serialize", 0);
  sqlite3_close(db);
}

/* V2 set-up: a host connection over the image and a prepared statement. */
void host_setup_prepared(void) {
  int rc = sqlite3_open(":memory:", &g_host_db);
  if (rc) die(g_host_db, "open", rc);
  rc = sqlite3_deserialize(g_host_db, "main", g_db_image, g_db_image_len, g_db_image_len,
                           SQLITE_DESERIALIZE_READONLY);
  if (rc) die(g_host_db, "deserialize", rc);
  rc = sqlite3_prepare_v2(g_host_db, QUERY, -1, &g_host_stmt, 0);
  if (rc) die(g_host_db, "prepare", rc);
}

/* ---------------------------------------------------------------- oracles */

static uint8_t run_query(sqlite3 *db, uint64_t rowid) {
  sqlite3_stmt *st;
  if (sqlite3_prepare_v2(db, QUERY, -1, &st, 0) != SQLITE_OK) return ORACLE_ERR;
  uint8_t out = ORACLE_ERR;
  if (sqlite3_bind_int64(st, 1, (sqlite3_int64)rowid) == SQLITE_OK) {
    int rc = sqlite3_step(st);
    if (rc == SQLITE_ROW) out = 1;
    else if (rc == SQLITE_DONE) out = 0;
  }
  if (sqlite3_finalize(st) != SQLITE_OK) out = ORACLE_ERR;
  return out;
}

/* V1: the rung-4 oracle. Self-contained: everything SQLite allocates is
 * allocated and freed inside the call; the only classical inputs are the
 * read-only database image and its length. */
__attribute__((noinline)) uint8_t oracle(uint64_t rowid) {
  sqlite3 *db;
  if (sqlite3_open(":memory:", &db) != SQLITE_OK) { sqlite3_close(db); return ORACLE_ERR; }
  uint8_t out = ORACLE_ERR;
  if (sqlite3_deserialize(db, "main", g_db_image, g_db_image_len, g_db_image_len,
                          SQLITE_DESERIALIZE_READONLY) == SQLITE_OK)
    out = run_query(db, rowid);
  if (sqlite3_close(db) != SQLITE_OK) out = ORACLE_ERR;
  return out;
}

/* V2: statement prepared before entry; the oracle binds, steps and resets. */
__attribute__((noinline)) uint8_t oracle_prepared(uint64_t rowid) {
  uint8_t out = ORACLE_ERR;
  if (sqlite3_bind_int64(g_host_stmt, 1, (sqlite3_int64)rowid) == SQLITE_OK) {
    int rc = sqlite3_step(g_host_stmt);
    if (rc == SQLITE_ROW) out = 1;
    else if (rc == SQLITE_DONE) out = 0;
  }
  if (sqlite3_reset(g_host_stmt) != SQLITE_OK) out = ORACLE_ERR;
  return out;
}

/* V0: rebuild the database from the row data inside the oracle. */
__attribute__((noinline)) uint8_t oracle_rebuild(uint64_t rowid) {
  sqlite3 *db;
  if (sqlite3_open(":memory:", &db) != SQLITE_OK) { sqlite3_close(db); return ORACLE_ERR; }
  uint8_t out = ORACLE_ERR;
  if (insert_rows(db, g_rows, g_nrows) == SQLITE_OK) out = run_query(db, rowid);
  if (sqlite3_close(db) != SQLITE_OK) out = ORACLE_ERR;
  return out;
}

oracle_fn oracle_by_name(const char *v) {
  if (!strcmp(v, "deser")) return oracle;
  if (!strcmp(v, "prepared")) return oracle_prepared;
  if (!strcmp(v, "rebuild")) return oracle_rebuild;
  fprintf(stderr, "unknown variant %s (deser|prepared|rebuild)\n", v);
  exit(2);
}
