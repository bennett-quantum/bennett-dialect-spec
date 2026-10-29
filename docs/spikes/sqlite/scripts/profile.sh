#!/usr/bin/env bash
# Build the instrumented profile binary and run the dynamic profiles.
#   scripts/profile.sh build
#   scripts/profile.sh run <variant> <N> [stride]     -> $WORK/prof/<variant>-N<N>/
# The profile module is the same program as scripts/build.sh plus the libc
# shim (src/libc_shim.c, bitcode) and the driver, LTO-optimised with the
# same pipeline, then instrumented by the bennett-prof pass.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
SPIKE=$(cd "$HERE/.." && pwd)
source "$HERE/config.sh"
mkdir -p "$WORK/bc" "$WORK/prof"
cd "$WORK"

SHIM_EXPORTS=malloc,free,calloc,realloc,aligned_alloc,memalign,posix_memalign,malloc_usable_size,memcmp,bcmp,memchr,strlen,strcmp,strncmp,strchr,strrchr,strspn,strcspn,localtime,shim_alloc_count,shim_free_count,shim_alloc_bytes,shim_live_bytes,shim_peak_live

build() {
  "$LLVM/clang++" -shared -fPIC -O2 $("$LLVM/llvm-config" --cxxflags) \
    "$HERE/plugin/BennettSpike.cpp" -o BennettSpike.so
  [ -f bc/sqlite3.bc ] || { echo "run scripts/build.sh first" >&2; exit 1; }
  "$CLANG" "${COMMON_CFLAGS[@]}" -fno-builtin -Wall -Werror -c "$SPIKE/src/libc_shim.c" -o bc/libc_shim.bc
  "$CLANG" "${COMMON_CFLAGS[@]}" -Wall -Werror -I"$SQLITE_SRC" -I"$SPIKE/src" \
    -c "$HERE/prof/prof_main.c" -o bc/prof_main.bc
  "$LLVM/llvm-link" bc/sqlite3.bc bc/rung4.bc bc/os_shim.bc bc/libc_shim.bc bc/prof_main.bc -o prof.linked.bc
  "$LLVM/opt" -passes='internalize,lto<O3>' -internalize-public-api-list=main,$SHIM_EXPORTS \
    prof.linked.bc -o prof.lto.bc
  "$LLVM/opt" -load-pass-plugin=./BennettSpike.so -passes=bennett-inventory \
    -bennett-out=prof.inventory.jsonl -disable-output prof.lto.bc
  "$LLVM/opt" -load-pass-plugin=./BennettSpike.so -passes=bennett-prof \
    -bennett-out=prof.table.tsv prof.lto.bc -o prof.instr.bc
  "$CLANG" -O2 -c "$HERE/prof/prof_rt.c" -o prof_rt.o
  "$CLANG" -O2 prof.instr.bc prof_rt.o -o profile
  ls -l profile prof.table.tsv
}

run() {
  local v=$1 n=$2 stride=${3:-1}
  local out=prof/$v-N$n
  [ "$stride" = 1 ] || out=$out-s$stride
  [ -z "${SHIM_PAD:-}" ] || out=$out-pad$SHIM_PAD
  mkdir -p "$out"
  cp prof.table.tsv "$out/table.tsv"   # block/memory-site ids are per build
  ./profile "$v" "$n" "$out" "$stride" | tee "$out/summary.txt"
}

all() {
  rm -rf prof; mkdir -p prof
  for v in deser deser-warm prepared rebuild; do
    for n in 16 256 1024; do run $v $n; done
  done
  SHIM_PAD=512 run deser 1024
  SHIM_PAD=512 run prepared 1024
  run deser 16384 61
  run prepared 16384 61
  run deser 1048576 4099
  run prepared 1048576 4099
  SHIM_PAD=512 run deser 1048576 4099
  run rebuild 4096 255
}

case "${1:-}" in
  build) build ;;
  run) shift; run "$@" ;;
  all) all ;;
  *) echo "usage: $0 build | run <variant> <N> [stride] | all" >&2; exit 2 ;;
esac
