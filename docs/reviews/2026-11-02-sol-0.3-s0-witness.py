#!/usr/bin/env python3
"""Reproduce qtab layout/image contradictions, checked by the ISA CLI.

This constructs a layout counterexample, not compiler output or a full dialect test.
All temporary files stay under docs/reviews and are removed on completion.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


REPO = Path(__file__).resolve().parents[2]
DEFAULT_REF = REPO / ".tmp/dialect03/isa-ref/4900508957bfd4aa/reference-interpreter/target/release/bennett-isa-ref"


def object_text(qtab_base, empty_image=False):
    signatures = [
        ("ref", "oracle", {"abi": "0.9", "args": [], "fault": 4,
                            "in": [], "kind": "oracle",
                            "mem": [{"A": 0, "W": 8, "role": "in"}],
                            "tgt": 8, "tier": "q"}),
        ("qtab", "data", {"abi": "0.9", "kind": "data",
                           "size": 4096, "tier": "-"}),
    ]
    symbols = {str(i): {"name": name, "kind": kind, "signature": sig,
                        "interface_hash": "0" * 64}
               for i, (name, kind, sig) in enumerate(signatures)}
    layout = {"A_tab": 1, "H": 14, "S_cells": 0,
              "globals": {"qtab": {"base": qtab_base, "image": "qtab", "size": 4096}},
              "heap_base": 8192, "heap_limit_max": 0,
              "interface_regions": {"ref": {"m0": {"base": 8192}}},
              "null_size": 4096, "ptr_width": 64}
    jcs = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"))
    return (
        "bennett-object isa=0.9 object=0.9 launch=0.9 sched=0.9 cert=0.9 coverage=0.9 target=0.9 ptr_width=64\n\n"
        "section symbols\n" + jcs(symbols) + "\n\n"
        "section functions\n"
        "oracle @ref () (tgt:wire[8]) (fault:wire[4]) (m0:region[0,8] in) ()\n"
        "regs { p:reg[64], v:reg[8] }\n"
        "^entry():\n"
        "p = lift.addr @m0\n"
        "lift.boundscheck p 1\n"
        "v = lift.load.i8 p\n"
        "lift.retval v\n\n"
        "section data\nqtab " + ("" if empty_image else "00" * 4096) + "\n\n"
        "section layout\n" + jcs(layout) + "\n"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", type=Path, default=DEFAULT_REF)
    args = parser.parse_args()
    ref = args.ref.resolve(strict=True)
    env = os.environ.copy()
    for key in ("DISPLAY", "WAYLAND_DISPLAY", "DBUS_SESSION_BUS_ADDRESS", "BROWSER"):
        env.pop(key, None)
    with tempfile.TemporaryDirectory(prefix=".sol-s0-", dir=Path(__file__).parent) as tmp:
        env["TMPDIR"] = tmp
        results = {}
        for name, base, empty_image in (("empty_image", 12288, True),
                                       ("overlap", 8192, False),
                                       ("disjoint", 12288, False)):
            path = Path(tmp) / (name + ".isa")
            path.write_text(object_text(base, empty_image))
            # The negative objects fail structural validation before hashing.
            # Obtain real hashes independently for the admitted control.
            if name == "disjoint":
                hashes = subprocess.run([str(ref), "hash", str(path)],
                                        text=True, capture_output=True, env=env, timeout=30)
                assert hashes.returncode == 0, hashes.stderr
                computed = json.loads(hashes.stdout)["symbols"]
                before, after = path.read_text().split("section symbols\n", 1)
                symbol_line, after = after.split("\n", 1)
                symbols = json.loads(symbol_line)
                for symbol in symbols.values():
                    symbol["interface_hash"] = computed[symbol["name"]]["interface_hash"]
                path.write_text(before + "section symbols\n" +
                                json.dumps(symbols, sort_keys=True, separators=(",", ":")) +
                                "\n" + after)
            result = subprocess.run([str(ref), "check", str(path)],
                                    text=True, capture_output=True, env=env, timeout=30)
            results[name] = {"exit": result.returncode,
                             "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
        print(json.dumps({"executor": str(ref),
                          "executor_sha256": hashlib.sha256(ref.read_bytes()).hexdigest(),
                          "qtab": [8192, 12288], "m0": [8192, 8193],
                          "checks": results}, indent=2))
        assert results["disjoint"]["exit"] == 0, "control object must be admitted"
        assert results["empty_image"]["exit"] != 0, "empty positive-size image must fail"
        assert "data size differs from signature" in results["empty_image"]["stderr"], \
            "failure must identify the data image size"
        assert results["overlap"]["exit"] != 0, "overlap must be rejected"
        assert "overlap" in (results["overlap"]["stdout"] + results["overlap"]["stderr"]).lower(), \
            "failure must identify overlapping ranges"


if __name__ == "__main__":
    main()
