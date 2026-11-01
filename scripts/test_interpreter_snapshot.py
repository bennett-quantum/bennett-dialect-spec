"""Offline integration regression for immutable two-crate interpreter snapshots."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import dialect_check_v02 as v


class InterpreterSnapshot(unittest.TestCase):
    def test_dependency_fingerprint_reuse_and_symlink(self):
        v.SCRATCH.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=v.SCRATCH) as tmp:
            root = Path(tmp)
            isa = root / 'isa'
            ref = isa / 'reference-interpreter'
            dep = isa / 'conformance'
            for crate in (ref, dep):
                (crate / 'src').mkdir(parents=True)
            (ref / 'Cargo.toml').write_text('''[package]
name = "bennett-isa-ref"
version = "0.0.0"
edition = "2021"
[dev-dependencies]
bennett-isa-conformance = { path = "../conformance" }
''')
            (dep / 'Cargo.toml').write_text('''[package]
name = "bennett-isa-conformance"
version = "0.0.0"
edition = "2021"
''')
            (ref / 'README.md').write_text('`run-program `\n')
            (ref / 'src/main.rs').write_text('fn main() { println!("{{}}"); }\n')
            (dep / 'src/lib.rs').write_text('pub fn witness() {}\n')
            cache = root / 'cache'
            cache.mkdir()
            link = root / 'linked-cache'
            link.symlink_to(cache, target_is_directory=True)
            with patch.object(v, 'ISA_SOURCE', ref), patch.object(v, 'ISA_DIR', link), \
                 patch.object(v, 'read_commit', return_value='fixture-head'), \
                 patch.dict(os.environ, {'CARGO_TARGET_DIR': str(root / 'external-target')}):
                interpreter = v.Interpreter()
                self.assertEqual(interpreter.call('run-program'), {})
                first = interpreter.exe
                self.assertTrue(first.is_file())
                stamp = (cache / 'BUILD.json').read_text()
                self.assertIn('conformance/src/lib.rs', json.loads(stamp)['files'])
                with patch.object(v, 'command', side_effect=AssertionError('unnecessary rebuild')):
                    v.Interpreter().build()
                for path in (dep / 'src/lib.rs', ref / 'src/main.rs'):
                    previous = interpreter.exe
                    path.write_text(path.read_text() + '// changed\n')
                    interpreter.build()
                    self.assertNotEqual(interpreter.exe, previous)
                    self.assertTrue(previous.exists())
                # A clean worktree resolves the same physical cache and reuses it.
                with patch.object(v, 'ISA_DIR', cache), \
                     patch.object(v, 'command', side_effect=AssertionError('unnecessary rebuild')):
                    reused = v.Interpreter()
                    reused.build()
                    self.assertEqual(reused.exe.resolve(), interpreter.exe.resolve())
                self.assertTrue(first.exists())


if __name__ == '__main__':
    unittest.main()
