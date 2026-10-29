/* OS interface shim for SQLite built with -DSQLITE_OS_OTHER=1
 * (https://sqlite.org/compile.html#os_other, https://sqlite.org/vfs.html).
 *
 * With SQLITE_OS_OTHER the stock unix VFS is not compiled; the application
 * supplies sqlite3_os_init()/sqlite3_os_end() and registers a default VFS.
 * This is the prototype of the bennett-runtimes "device-free VFS" shim:
 *   - no files: xOpen refuses every real file (SQLITE_CANTOPEN). The main
 *     database is reached through SQLite's own memdb VFS
 *     (sqlite3_deserialize), which wraps this VFS and serves the pages from
 *     the image in memory; temp storage is in memory (SQLITE_TEMP_STORE=3).
 *   - randomness, time and sleep are deterministic constants, so the oracle
 *     is a function of its classical inputs and rowid only.
 * Every method that should be unreachable for the rung-4 oracle fails loud
 * (returns an error that the oracle turns into ORACLE_ERR).
 */
#include <string.h>
#include "sqlite3.h"

static int shimOpen(sqlite3_vfs *v, sqlite3_filename name, sqlite3_file *f, int flags, int *out) {
  (void)v; (void)name; (void)flags; (void)out;
  f->pMethods = 0;
  return SQLITE_CANTOPEN;
}
static int shimDelete(sqlite3_vfs *v, const char *name, int sync) {
  (void)v; (void)name; (void)sync;
  return SQLITE_IOERR_DELETE;
}
static int shimAccess(sqlite3_vfs *v, const char *name, int flags, int *res) {
  (void)v; (void)name; (void)flags;
  *res = 0;
  return SQLITE_OK;
}
static int shimFullPathname(sqlite3_vfs *v, const char *name, int n, char *out) {
  (void)v;
  int len = (int)strlen(name);
  if (len >= n) return SQLITE_CANTOPEN;
  memcpy(out, name, (size_t)len + 1);
  return SQLITE_OK;
}
/* Deterministic "entropy": a fixed byte pattern. SQLite seeds its PRNG from
 * this once per process (sqlite3_randomness). */
static int shimRandomness(sqlite3_vfs *v, int n, char *out) {
  (void)v;
  for (int i = 0; i < n; i++) out[i] = (char)(0xA5 ^ (i * 29));
  return n;
}
static int shimSleep(sqlite3_vfs *v, int us) { (void)v; return us; }
/* Fixed clock: 2026-10-29 00:00:00 UTC as a Julian day number. */
static int shimCurrentTime(sqlite3_vfs *v, double *t) { (void)v; *t = 2461342.5; return SQLITE_OK; }
static int shimCurrentTimeInt64(sqlite3_vfs *v, sqlite3_int64 *t) {
  (void)v; *t = (sqlite3_int64)212659992000000LL; /* Julian day * 86400000 */ return SQLITE_OK;
}
static int shimGetLastError(sqlite3_vfs *v, int n, char *buf) {
  (void)v; if (n > 0) buf[0] = 0; return 0;
}

static sqlite3_vfs shim_vfs = {
  2,                       /* iVersion */
  (int)sizeof(sqlite3_file),
  512,                     /* mxPathname */
  0,                       /* pNext */
  "bennett-nofs",          /* zName */
  0,                       /* pAppData */
  shimOpen, shimDelete, shimAccess, shimFullPathname,
  0, 0, 0, 0,              /* xDlOpen/xDlError/xDlSym/xDlClose: SQLITE_OMIT_LOAD_EXTENSION */
  shimRandomness, shimSleep, shimCurrentTime, shimGetLastError,
  shimCurrentTimeInt64,
  0, 0, 0                  /* v3 syscall methods: unused */
};

int sqlite3_os_init(void) { return sqlite3_vfs_register(&shim_vfs, 1); }
int sqlite3_os_end(void) { return SQLITE_OK; }
