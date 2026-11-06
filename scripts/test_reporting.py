"""Structural verification must not inflate the reported semantic count."""
import unittest
from dialect_report import counts


class Counts(unittest.TestCase):
    def test_mixed_status_and_family_counts(self):
        rows = [{'family': family, 'status': status} for family, status in
                [('xrefs', 'passed'), ('parse', 'failed'), ('coverage', 'blocked'),
                 ('inventory', 'passed'), ('recognise', 'passed'), ('state', 'blocked')]]
        self.assertEqual(counts(rows), {'semantic': {'total': 2, 'passed': 1},
                                      'bookkeeping': {'total': 4, 'passed': 2}})
