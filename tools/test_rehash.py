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

    def test_missing_expected_hash_fence_is_refused(self):
        import re
        anchor = rehash.load_anchors()[0]
        text = (rehash.ROOT / 'spec' / anchor['spec']).read_text()
        stripped = re.sub(r'```text hash=inc8\n.*?```', '', text, flags=re.S)
        self.assertNotEqual(stripped, text)
        with self.assertRaisesRegex(ValueError, 'anchor.*fence'):
            rehash.verify_anchors(stripped, [anchor])

    def test_nonanchor_refresh_preserves_fixed_hashes(self):
        anchor = rehash.load_anchors()[0]
        table = {'0': {'name': 'L1', 'interface_hash': anchor['sha256']},
                 '1': {'name': 'aux', 'interface_hash': '0' * 64}}
        source = ('```isa object=inc8\nsection symbols\n' + json.dumps(table) +
                  '\n```\n```text hash=inc8\nL1 ' + anchor['sha256'] + '\naux ' + '0' * 64 + '\n```')
        response = {'symbols': {'L1': {'interface_hash': anchor['sha256']},
                                'aux': {'interface_hash': '1' * 64}}}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / anchor['spec']
            path.write_text(source)
            with patch.object(rehash, 'run', return_value=response):
                self.assertEqual(rehash.rewrite(path, 'executor', tmp, [anchor]), 1)
            updated = path.read_text()
            self.assertIn('L1 ' + anchor['sha256'], updated)
            self.assertIn('aux ' + '1' * 64, updated)
            self.assertNotIn('aux ' + '0' * 64, updated)
            rehash.verify_anchors(updated, [anchor])
