"""Contract tests: compiled with the system cc, independent of LLVM."""
import pathlib
import subprocess
import tempfile
import unittest

import run

ROOT = pathlib.Path(__file__).resolve().parents[1]


class RuntimeTests(unittest.TestCase):
    def build_run(self, body, inputs=(3, 4), canonical=False):
        with tempfile.TemporaryDirectory() as directory:
            d = pathlib.Path(directory)
            (d / 'case.c').write_text('#include "markers.h"\n' + body)
            cmd = ['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-I', str(ROOT),
                   '-no-pie', '-rdynamic', str(ROOT / 'runtime/trace_rt.c'),
                   str(ROOT / 'runtime/driver.c'), str(d / 'case.c'), '-ldl', '-o', str(d / 'a')]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            result = subprocess.run([str(d / 'a'), *map(str, inputs)], capture_output=True, text=True)
            if canonical:
                nm = run.tools_for([18])[18]['llvm-nm']
                result.raw = result.stdout
                result.stdout = run.canonicalize_trace(result.stdout, run.executable_symbols(d / 'a', nm, d, 'symbols'))
            return result

    def test_canonical_reset_regions_and_bits(self):
        result = self.build_run('''
static void region(void *env) { __bennett_gate(7, *(bq *)env, 2); }
int64_t case_entry(int64_t x) {
 bq h = __bennett_qalloc(1, 3);
 __bennett_rot(9, h, 0, -0.0);
 __bennett_ctrl(h, 1, region, 12, &h);
 __bennett_adj(region, &h);
 __bennett_compute(region, region, &h);
 __bennett_reversible(region, 3, &h);
 __bennett_inplace(region, region, &h);
 __bennett_ctrl_v(h, 1, (void *)region, 5, 99);
 bool a = __bennett_measure(h, 0);
 __bennett_qfree(h);
 return x + a;
}
''', (3, 3), canonical=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.raw, r'CTRL H0 1 F@0x[0-9a-f]+ 12\n')
        first, second = result.stdout.split('IN 3\n')[1:]
        self.assertEqual(first, second)
        self.assertIn('QALLOC H0 1 3\n', first)
        self.assertIn('ROT 9 H0 0 0x8000000000000000\n', first)
        self.assertIn('CTRL H0 1 F:region 12\n', first)
        self.assertEqual(first.count('GATE 7 H0 2\n'), 7)
        self.assertNotIn('F?', first)
        self.assertNotIn('BADHANDLE', first)

    def test_guard_fault(self):
        result = self.build_run('int64_t case_entry(int64_t x) { (void)x; bq h = __bennett_qalloc(0,1); return *(volatile char *)h; }', (0,))
        self.assertEqual(result.returncode, 86)
        self.assertIn('IN 0\nQALLOC H0 0 1\nFAULT handle-deref\n', result.stdout)

    def test_bad_and_freed_handles(self):
        result = self.build_run('int64_t case_entry(int64_t x) { (void)x; bq h=__bennett_qborrow(0,1); __bennett_qfree(h); __bennett_gate(1,h,0); __bennett_qfree((bq)(uintptr_t)123); return 0; }', (0,))
        self.assertEqual(result.returncode, 0)
        self.assertIn('GATE 1 BADHANDLE 0', result.stdout)
        self.assertIn('QFREE BADHANDLE', result.stdout)

    def test_driver_rejects_missing_or_invalid_input(self):
        body = 'int64_t case_entry(int64_t x) { return x; }'
        self.assertNotEqual(self.build_run(body, ()).returncode, 0)
        self.assertNotEqual(self.build_run(body, ('oops',)).returncode, 0)


if __name__ == '__main__':
    unittest.main()
