"""Viewer passes (view-cfg, view-dom, ...) must never reach the desktop or write to /tmp.

Regression for 2026-10-28: P1 ran every advertised pass, including LLVM's view-* family, with
DBUS_SESSION_BUS_ADDRESS set and TMPDIR unset; ~80,000 .dot files were written to /tmp and handed
to xdg-open, which opened them in the maintainer's editor.
"""
import os
import pathlib
import sys
import tempfile
import tomllib
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import run  # noqa: E402

MODULE = """define i32 @f(i32 %x) {
entry:
  %c = icmp eq i32 %x, 0
  br i1 %c, label %a, label %b
a:
  ret i32 1
b:
  ret i32 2
}
"""


class Headless(unittest.TestCase):
    def test_graph_output_stays_local_and_viewers_are_stubs(self):
        config = tomllib.loads((run.ROOT / 'toolchains.toml').read_text())
        opt = pathlib.Path(config['llvm18']['bin']) / 'opt'
        with tempfile.TemporaryDirectory() as cell:
            cell = pathlib.Path(cell)
            (cell / 'm.ll').write_text(MODULE)
            before = run.VIEWER_LOG.read_text() if run.VIEWER_LOG.exists() else ''
            env = run.headless_env(tmpdir=cell)
            self.assertNotIn('DBUS_SESSION_BUS_ADDRESS', env)
            self.assertNotIn('DISPLAY', env)
            self.assertNotIn('WAYLAND_DISPLAY', env)
            self.assertNotIn('BROWSER', env)
            scratch = pathlib.Path(env['TMPDIR'])
            self.assertTrue(scratch.is_relative_to(run.ROOT.parents[1]))
            result = run.command([opt, '-passes=dot-cfg', '-disable-output', cell / 'm.ll'], cell, 'graph')
            self.assertEqual(result['returncode'], 0, pathlib.Path(result['stderr']).read_text())
            self.assertTrue(list(cell.rglob('*.dot')), 'dot-cfg must write a graph')
            log = run.VIEWER_LOG.read_text() if run.VIEWER_LOG.exists() else ''
            self.assertEqual(log, before, 'graph generation must not launch a viewer')
            for name in run.VIEWERS:
                stub = run.HEADLESS_BIN / name
                self.assertTrue(os.access(stub, os.X_OK))
                self.assertIn('exit 1', stub.read_text())



if __name__ == '__main__':
    unittest.main()
