# tools/

`dialect_check_v03.py` is the pre-flight for draft 0.3 (`spec/Bennett-Dialect-Spec-0.3-draft.md`,
grading target ISA 0.9). It composes the shared checker modules with the scoped publication
profile in `scripts/dialect_profile.py` and the independent witnesses in `dialect03_witnesses.py`.
There are no import hooks or source substitutions. Sibling inputs resolve only through `gate.toml`.


Run headless from the repo root:

    env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER \
      TMPDIR=$PWD/.tmp/dialect03/tmp python3 tools/dialect_check_v03.py --json .tmp/dialect03/gate.json

`dialect03_rehash.py` refreshes tagged object hashes using the pinned reference interpreter.
It validates the independently derived envelopes in `corpus/hash-anchors.json` first and refuses
to change any anchor. Missing anchors, input drift or executor drift fail before the spec write.
The file records the hand derivation and the published ISA source pin; rehash cannot update it.
