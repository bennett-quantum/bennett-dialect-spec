#!/usr/bin/env bash
# Build the rung-4 program from the stock SQLite amalgamation to whole-program
# LLVM bitcode with clang 18, emulating the LTO link the driver performs
# (north star §3.3): per-TU `clang -O2 -flto` (pre-link pipeline), llvm-link,
# then `opt internalize,lto<O3>` with only the program's entry exported.
#
# Outputs (in $WORK, outside the repo):
#   bc/*.bc              per-TU bitcode
#   rung4.lto.bc/.ll     LTO-linked optimised module (inventory input)
#   verify               native binary from rung4.lto.bc (system libc)
#
# Usage: scripts/build.sh     (after scripts/fetch.sh)
# Env:   BENNETT_SQLITE_HOME, BENNETT_SQLITE_WORK (default ~/.cache/bennett-sqlite-spike)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
SPIKE=$(cd "$HERE/.." && pwd)
source "$HERE/config.sh"

mkdir -p "$WORK/bc"
cd "$WORK"   # never cd into the unpacked archive

echo "SQLite flags: ${SQLITE_FLAGS[*]}"
"$CLANG" "${COMMON_CFLAGS[@]}" "${SQLITE_FLAGS[@]}" -w -c "$SQLITE_SRC/sqlite3.c" -o bc/sqlite3.bc
for f in rung4 os_shim verify_main; do
  "$CLANG" "${COMMON_CFLAGS[@]}" "${SQLITE_FLAGS[@]}" -Wall -Wextra -Werror -I"$SQLITE_SRC" \
    -c "$SPIKE/src/$f.c" -o "bc/$f.bc"
done

"$LLVM/llvm-link" bc/sqlite3.bc bc/rung4.bc bc/os_shim.bc bc/verify_main.bc -o rung4.linked.bc
"$LLVM/opt" -passes='internalize,lto<O3>' -internalize-public-api-list=main \
  rung4.linked.bc -o rung4.lto.bc
"$LLVM/llvm-dis" rung4.lto.bc -o rung4.lto.ll
"$CLANG" -O2 rung4.lto.bc -o verify
ls -l rung4.lto.bc rung4.lto.ll verify
