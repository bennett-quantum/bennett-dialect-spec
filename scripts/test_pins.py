"""Pin resolution must never substitute a moving sibling checkout."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import subprocess
import os

from dialect_pins import sibling


class Pins(unittest.TestCase):
    def test_cache_pin_and_missing_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sha = 'a' * 40
            (root / 'gate.toml').write_text('[siblings.oracle]\nsha = "' + sha + '"\n')
            with self.assertRaisesRegex(RuntimeError, sha):
                sibling('oracle', root)
            cache = root / '.tmp/gate/cache' / ('oracle@' + sha[:12]) / 'oracle'
            cache.mkdir(parents=True)
            # A directory without the pinned git identity is never trusted.
            with self.assertRaisesRegex(RuntimeError, 'oracle'):
                sibling('oracle', root)

    def test_exact_pin_accepted_and_dirty_or_wrong_pin_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache = root / 'layout/oracle'
            cache.mkdir(parents=True)
            def git(*args):
                return subprocess.run(['git', '-C', str(cache), *args], check=True,
                                      capture_output=True, text=True).stdout.strip()
            git('init', '--quiet')
            (cache / 'input').write_text('published')
            git('add', 'input')
            git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                'commit', '-qm', 'pin')
            sha = git('rev-parse', 'HEAD')
            config = root / 'gate.toml'
            config.write_text('[siblings.oracle]\nsha = "' + sha + '"\n')
            with patch.dict(os.environ, {'BENNETT_GATE_LAYOUT': str(cache.parent)}):
                self.assertEqual(sibling('oracle', root), cache)
                sibling.cache_clear()
                (cache / 'input').write_text('dirty')
                with self.assertRaisesRegex(RuntimeError, 'modified tracked'):
                    sibling('oracle', root)
                config.write_text('[siblings.oracle]\nsha = "' + 'b' * 40 + '"\n')
                with self.assertRaisesRegex(RuntimeError, 'actual ' + sha):
                    sibling('oracle', root)
