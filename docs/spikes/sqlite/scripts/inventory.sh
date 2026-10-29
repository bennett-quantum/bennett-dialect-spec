#!/usr/bin/env bash
# Static inventory of the oracle closures from the LTO-linked module of
# scripts/build.sh: run the bennett-inventory pass, then inventory.py.
# Writes results/inventory.json in the repo (small) and prints a summary.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
SPIKE=$(cd "$HERE/.." && pwd)
source "$HERE/config.sh"
cd "$WORK"
"$LLVM/clang++" -shared -fPIC -O2 $("$LLVM/llvm-config" --cxxflags) \
  "$HERE/plugin/BennettSpike.cpp" -o BennettSpike.so
"$LLVM/opt" -load-pass-plugin=./BennettSpike.so -passes=bennett-inventory \
  -bennett-out=inventory.jsonl -disable-output rung4.lto.bc
python3 -I "$HERE/inventory.py" inventory.jsonl oracle_on_image oracle_prepared oracle_rebuild \
  --out "$SPIKE/results"
