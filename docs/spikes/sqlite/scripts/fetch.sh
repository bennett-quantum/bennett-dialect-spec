#!/usr/bin/env bash
# Fetch the SQLite amalgamation, verify size and SHA3-256 against the values
# published on https://sqlite.org/download.html, and unpack it into its own
# new directory outside the repo.  The archive is untrusted data: nothing in
# it is ever executed; it is only compiled (scripts/build.sh).
#
# Usage: scripts/fetch.sh            (pinned version below)
# Env:   BENNETT_SQLITE_HOME (default ~/.local/share/bennett-sqlite)
set -euo pipefail

VERSION=3.54.1
VERCODE=3540100
YEAR=2026
# Published on https://sqlite.org/download.html (checked 2026-10-29):
SIZE=2990966
SHA3=92281c86e2957f9b9305890f9ac04204caa7b677cc868dc326d942689df28e30

HOME_DIR=${BENNETT_SQLITE_HOME:-$HOME/.local/share/bennett-sqlite}
DEST=$HOME_DIR/$VERSION
ZIP=$DEST/sqlite-amalgamation-$VERCODE.zip
URL=https://sqlite.org/$YEAR/sqlite-amalgamation-$VERCODE.zip

mkdir -p "$DEST"

verify() {
  local f=$1
  [ -f "$f" ] || return 1
  local sz; sz=$(stat -c %s "$f")
  [ "$sz" = "$SIZE" ] || { echo "size mismatch: $sz != $SIZE" >&2; return 1; }
  local h; h=$(python3 -I -c 'import hashlib,sys;print(hashlib.sha3_256(open(sys.argv[1],"rb").read()).hexdigest())' "$f")
  [ "$h" = "$SHA3" ] || { echo "sha3 mismatch: $h != $SHA3" >&2; return 1; }
  return 0
}

if ! verify "$ZIP"; then
  rm -f "$ZIP.part"
  ok=0
  for attempt in 1 2 3 4 5 6 7 8; do
    if curl -fsS --max-time 120 -C - -o "$ZIP.part" "$URL"; then
      mv "$ZIP.part" "$ZIP"
      if verify "$ZIP"; then ok=1; break; fi
      echo "downloaded file failed verification; retrying" >&2
      rm -f "$ZIP"
    fi
    sleep $(( attempt * attempt * 2 ))
    echo "retry $attempt" >&2
  done
  [ $ok = 1 ] || { echo "FAILED to fetch $URL" >&2; exit 1; }
fi
echo "verified $ZIP size=$SIZE sha3-256=$SHA3"

SRC=$DEST/src
if [ ! -f "$SRC/sqlite3.c" ]; then
  rm -rf "$SRC"; mkdir -p "$SRC"
  # -j: flatten; only the four amalgamation files are expected.
  unzip -q -j "$ZIP" -d "$SRC"
fi
ls -l "$SRC"
grep -m1 '^#define SQLITE_VERSION ' "$SRC/sqlite3.h"
grep -m1 '^#define SQLITE_SOURCE_ID' "$SRC/sqlite3.h"
