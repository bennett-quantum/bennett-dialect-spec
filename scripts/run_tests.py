#!/usr/bin/env python3
"""Default tooling tests; --slow runs the execution checks retained in the gate."""
import argparse
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parent.parent
SUITES = ('scripts', 'tools', 'corpus/legality/harness')


def slow(reason):
    def mark(fn):
        fn.slow_reason = reason
        return fn
    return mark


def partition(suite):
    fast, deferred = [], []
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            a, b = partition(test)
            fast.extend(a)
            deferred.extend(b)
        else:
            method = getattr(test, test._testMethodName)
            (deferred if getattr(method, 'slow_reason', None) else fast).append(test)
    return fast, deferred


def discover():
    suite = unittest.TestSuite()
    for directory in SUITES:
        path = str(ROOT / directory)
        sys.path.insert(0, path)
        suite.addTests(unittest.TestLoader().discover(path))
    return suite


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slow', action='store_true', help='run only expensive execution tests')
    parser.add_argument('--all', action='store_true', help='run fast and slow tests')
    args = parser.parse_args(argv)
    fast, deferred = partition(discover())
    chosen = fast + deferred if args.all else deferred if args.slow else fast
    print(f'Tooling suite: {len(fast)} default + {len(deferred)} slow; running {len(chosen)}', flush=True)
    started = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(chosen))
    print(f'Wall time: {time.monotonic() - started:.2f} s', flush=True)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
