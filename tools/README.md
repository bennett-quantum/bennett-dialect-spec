# tools/

`dialect_check_v03.py` is the pre-flight for draft 0.3 (`spec/Bennett-Dialect-Spec-0.3-draft.md`,
grading target ISA 0.9). It loads the frozen 0.2 checker modules from `scripts/` through an import
hook that applies the exact version-token patches listed in `dialect03_patches.py` (each with a
required hit count, so a drifted module fails loud), and adds the ISA 0.9 witnesses of
`dialect03_witnesses.py`. `scripts/` and its 0.2.12 gate are unchanged.

Run headless from the repo root:

    env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u BROWSER \
      TMPDIR=$PWD/.tmp/dialect03/tmp python3 tools/dialect_check_v03.py --json .tmp/dialect03/gate.json

`dialect03_rehash.py` recomputes the stored interface hashes of the draft's tagged ISA objects with
the reference interpreter (P-3: Python places bytes, the executor computes them).
The reference interpreter is built from a `git archive` of the ISA repo's committed HEAD, never its
possibly dirty working tree.
