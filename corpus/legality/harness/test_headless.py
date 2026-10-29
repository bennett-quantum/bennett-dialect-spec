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
    def test_view_pass_stays_in_cell_and_never_opens_a_viewer(self):
        config = tomllib.loads((run.ROOT / 'toolchains.toml').read_text())
        opt = pathlib.Path(config['llvm18']['bin']) / 'opt'
        with tempfile.TemporaryDirectory() as cell:
            cell = pathlib.Path(cell)
            (cell / 'm.ll').write_text(MODULE)
            before = set(os.listdir('/tmp'))
            env = run.headless_env()
            self.assertNotIn('DBUS_SESSION_BUS_ADDRESS', env)
            self.assertNotIn('DISPLAY', env)
            self.assertNotIn('WAYLAND_DISPLAY', env)
            run.command([opt, '-passes=view-cfg', '-disable-output', cell / 'm.ll'], cell, 'view')
            after = set(os.listdir('/tmp'))
            leaked = [n for n in after - before if n.endswith('.dot')]
            self.assertEqual(leaked, [], f'view pass wrote to /tmp: {leaked}')
            dots = list(cell.rglob('*.dot'))
            self.assertTrue(dots, 'view-cfg should have written its .dot inside the cell directory')
            log = run.VIEWER_LOG.read_text() if run.VIEWER_LOG.exists() else ''
            self.assertTrue(all(str(cell) in line or 'cfg.f' in line for line in log.splitlines()[-1:]),
                            'a viewer, if invoked, must be the logging stub')


if __name__ == '__main__':
    unittest.main()
