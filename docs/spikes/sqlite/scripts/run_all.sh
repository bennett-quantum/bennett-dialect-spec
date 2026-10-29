#!/usr/bin/env bash
# Reproduce the whole spike end to end (about 30-60 minutes on 4 cores):
#   fetch (SHA3-verified) -> build (LTO bitcode) -> native verification ->
#   static inventory -> instrumented profile build -> profiles -> analysis -> cost.
# Large artefacts stay in $BENNETT_SQLITE_WORK (default ~/.cache/bennett-sqlite-spike);
# the small summaries land in results/ in the repo.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
SPIKE=$(cd "$HERE/.." && pwd)
"$HERE/fetch.sh"
"$HERE/build.sh"
source "$HERE/config.sh"
mkdir -p "$SPIKE/results"
{
  for v in deser prepared rebuild; do for n in 16 256 1024; do "$WORK/verify" $v $n; done; done
  "$WORK/verify" prepared 1048576
  "$WORK/verify" deser 1048576 4099
} | tee "$SPIKE/results/verify.txt"
if grep -q FAIL "$SPIKE/results/verify.txt"; then echo "native verification FAILED" >&2; exit 1; fi
"$HERE/inventory.sh"
"$HERE/profile.sh" build
"$HERE/profile.sh" all
python3 -I "$HERE/analyze.py" "$WORK/prof" "$SPIKE/results" | tee "$SPIKE/results/profiles.txt"
python3 -I "$HERE/cost.py" "$SPIKE/results" > /dev/null
echo "results in $SPIKE/results"
