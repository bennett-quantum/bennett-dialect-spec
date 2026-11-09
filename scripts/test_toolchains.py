"""Toolchain readers must use the invoking user's home and fail before execution."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from dialect_toolchains import load_toolchains, require_tool

ROOT = Path(__file__).resolve().parents[1]
READERS = {
    'harness': 'import run; print(run.tools_for([{major}])[{major}]["opt"])',
    'checker': ('import dialect_execution as d; d.MAJORS = ("{major}",); '
                'print(d.toolchains()["{major}"] / "opt")'),
}
HOME_BINS = {
    23: '.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin',
    20: '.julia/artifacts/21334d62ab8fb1788be32b83ab0373b77916a794/tools',
}


class HomeToolchainsTests(unittest.TestCase):
    def read(self, reader, major, home):
        env = dict(os.environ, HOME=str(home), PYTHONPATH=os.pathsep.join(
            (str(ROOT / 'scripts'), str(ROOT / 'corpus/legality/harness'))))
        return subprocess.run([sys.executable, '-c', READERS[reader].format(major=major)],
                              env=env, capture_output=True, text=True)

    def test_missing_home_toolchain_names_resolved_path_and_provider(self):
        with tempfile.TemporaryDirectory(prefix='home with spaces-') as home:
            for reader in READERS:
                for major, relative in HOME_BINS.items():
                    with self.subTest(reader=reader, major=major):
                        result = self.read(reader, major, home)
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                        self.assertIn(str(Path(home) / relative / 'opt'), result.stderr)
                        provider = 'rustup component add llvm-tools' if major == 23 else 'LLVM_full_jll'
                        self.assertIn(provider, result.stderr)

    def test_populated_home_selects_its_tools(self):
        with tempfile.TemporaryDirectory() as home:
            for major, relative in HOME_BINS.items():
                directory = Path(home) / relative
                directory.mkdir(parents=True)
                for name in ('opt', 'llc', 'llvm-dis', 'llvm-as', 'llvm-link', 'llvm-nm'):
                    path = directory / name
                    path.write_text('#!/bin/sh\nexit 0\n')
                    path.chmod(0o755)
                for reader in READERS:
                    with self.subTest(reader=reader, major=major):
                        result = self.read(reader, major, home)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(result.stdout.strip(), str(directory / 'opt'))

    def test_missing_secondary_tool_is_fatal(self):
        with tempfile.TemporaryDirectory() as home:
            directory = Path(home) / HOME_BINS[23]
            directory.mkdir(parents=True)
            opt = directory / 'opt'
            opt.write_text('#!/bin/sh\nexit 0\n')
            opt.chmod(0o755)
            for reader in READERS:
                with self.subTest(reader=reader):
                    result = self.read(reader, 23, home)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn(str(directory / 'llc'), result.stderr)
                    self.assertIn('rustup component add llvm-tools', result.stderr)


class ConfigToolchainsTests(unittest.TestCase):
    def test_bin_and_frontend_expand_home_but_absolute_paths_stay_literal(self):
        with tempfile.TemporaryDirectory() as home, patch.dict(os.environ, HOME=home):
            config = Path(home) / 'toolchains.toml'
            config.write_text('[llvm23]\nbin = "$HOME/tools"\nfrontend_bin = "$HOME/frontend"\n'
                              '[llvm18]\nbin = "/usr/lib/llvm-18/bin"\n')
            result = load_toolchains(config)
            self.assertEqual(result['llvm23']['bin'], Path(home) / 'tools')
            self.assertEqual(result['llvm23']['frontend_bin'], Path(home) / 'frontend')
            self.assertEqual(result['llvm18']['bin'], Path('/usr/lib/llvm-18/bin'))

    def test_frontend_reader_uses_resolved_inventory(self):
        import dialect_check_v02 as checker
        with tempfile.TemporaryDirectory() as home, patch.dict(os.environ, HOME=home):
            config = Path(home) / 'toolchains.toml'
            config.write_text('[llvm23]\nbin = "$HOME/tools"\nfrontend_bin = "$HOME/frontend"\n')
            with patch.object(checker.d, 'TOOLCHAINS', config), patch.object(checker.d, 'MAJORS', ('23',)):
                self.assertEqual(checker.frontend_bins(), {'23': Path(home) / 'frontend'})

    def test_invalid_paths_do_not_fall_back_to_host_tools(self):
        invalid = ('', 'relative/tools', '$UNKNOWN/tools', '/tools/$UNKNOWN')
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / 'toolchains.toml'
            for value in invalid:
                with self.subTest(value=value):
                    config.write_text(f'[llvm23]\nbin = "{value}"\n')
                    with self.assertRaisesRegex(ValueError, 'llvm23.bin'):
                        load_toolchains(config)

    def test_unset_home_requires_explicit_configuration(self):
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / 'toolchains.toml'
            config.write_text('[llvm23]\nbin = "$HOME/tools"\n')
            with patch.dict(os.environ, clear=True):
                with self.assertRaisesRegex(ValueError, 'HOME is unset.*set HOME'):
                    load_toolchains(config)

    def test_nonexecutable_tool_names_path_and_system_provider(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'opt'
            path.write_text('#!/bin/sh\nexit 0\n')
            with self.assertRaises(ValueError) as error:
                require_tool(path.parent, path.name, 18)
            self.assertIn(str(path), str(error.exception))
            self.assertIn('apt-get install -y clang-18 llvm-18-dev lld-18', str(error.exception))


if __name__ == '__main__':
    unittest.main()
