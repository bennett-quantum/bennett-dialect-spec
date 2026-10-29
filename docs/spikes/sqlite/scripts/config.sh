# Shared configuration for the spike scripts (sourced, not executed).
VERSION=3.54.1
HOME_DIR=${BENNETT_SQLITE_HOME:-$HOME/.local/share/bennett-sqlite}
SQLITE_SRC=$HOME_DIR/$VERSION/src
WORK=${BENNETT_SQLITE_WORK:-$HOME/.cache/bennett-sqlite-spike}
LLVM=/usr/lib/llvm-18/bin
CLANG=$LLVM/clang

[ -f "$SQLITE_SRC/sqlite3.c" ] || { echo "run scripts/fetch.sh first ($SQLITE_SRC)" >&2; exit 1; }

COMMON_CFLAGS=(-O2 -flto -g0 -fno-stack-protector -fno-exceptions)

# Every flag is a documented SQLite compile-time option
# (https://sqlite.org/compile.html); no source edits.  Rationale in REPORT.md §2.
SQLITE_FLAGS=(
  -DSQLITE_THREADSAFE=0            # no mutexes, no pthreads (effect removal)
  -DSQLITE_OMIT_LOAD_EXTENSION     # no dlopen/dlsym (effect removal)
  -DSQLITE_OS_OTHER=1              # no built-in unix VFS; app supplies os_init + VFS (src/os_shim.c)
  -DSQLITE_TEMP_STORE=3            # temp tables/indices always in memory, never temp files
  -DSQLITE_DEFAULT_MEMSTATUS=0     # no global memory-statistics bookkeeping (recommended option)
  -DSQLITE_OMIT_SHARED_CACHE       # no shared-cache machinery (recommended option)
  -DSQLITE_OMIT_DEPRECATED         # drop deprecated interfaces (recommended option)
  -DSQLITE_DQS=0                   # no double-quoted string literals (recommended option)
)
