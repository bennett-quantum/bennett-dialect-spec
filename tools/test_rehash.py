"""Immutable anchors must survive both corrupted inputs and executor drift."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import dialect03_rehash as rehash


class Anchors(unittest.TestCase):
    def test_independent_transcripts_match_pinned_spec_hashes(self):
        import hashlib
        for anchor in rehash.load_anchors():
            self.assertEqual(hashlib.sha256(anchor['envelope'].encode()).hexdigest(), anchor['sha256'])
            text = (rehash.ROOT / 'spec' / anchor['spec']).read_text()
            rehash.verify_anchors(text, [anchor])

    def test_executor_drift_is_refused_without_writing_spec(self):
        anchor = rehash.load_anchors()[0]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / anchor['spec']
            original = (rehash.ROOT / 'spec' / anchor['spec']).read_text()
            path.write_text(original)
            with patch.object(rehash, 'run', return_value={'symbols': {'L1': {'interface_hash': '0' * 64}}}):
                with self.assertRaisesRegex(ValueError, 'anchor'):
                    rehash.rewrite(path, 'executor', tmp, [anchor])
            self.assertEqual(path.read_text(), original)

    def test_missing_or_edited_anchor_is_refused(self):
        anchor = rehash.load_anchors()[0]
        text = (rehash.ROOT / 'spec' / anchor['spec']).read_text()
        with self.assertRaisesRegex(ValueError, 'anchor'):
            rehash.verify_anchors('', [anchor])
        with self.assertRaisesRegex(ValueError, 'anchor'):
            rehash.verify_anchors(text.replace(anchor['sha256'], '0' * 64), [anchor])
