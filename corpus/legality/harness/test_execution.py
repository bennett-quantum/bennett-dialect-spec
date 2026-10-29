import pathlib
import tempfile
import unittest
from run import execute_inputs


class ExhaustiveExecutionTests(unittest.TestCase):
    def test_fault_does_not_skip_later_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            exe = p / 'driver'
            exe.write_text('#!/usr/bin/env python3\nimport sys\nfor x in sys.argv[1:]:\n print("IN " + x, flush=True)\n if x == "1":\n  print("FAULT handle-deref", flush=True)\n  sys.exit(86)\n print("RET " + x, flush=True)\n')
            exe.chmod(0o755)
            r = execute_inputs(exe, [0, 1, 2], p, 'test')
            self.assertEqual(r['exit'], 86)
            self.assertEqual(pathlib.Path(r['trace']).read_text(), 'IN 0\nRET 0\nIN 1\nFAULT handle-deref\nIN 2\nRET 2\n')
            self.assertEqual(r['inputs_executed'], 3)

    def test_successful_exit_without_all_inputs_is_failure(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            exe = p / 'driver'
            exe.write_text('#!/bin/sh\necho "IN $1"\nexit 0\n')
            exe.chmod(0o755)
            r = execute_inputs(exe, [0, 1], p, 'test')
            self.assertNotEqual(r['exit'], 0)
            self.assertEqual(r['inputs_executed'], 2)


if __name__ == '__main__':
    unittest.main()
