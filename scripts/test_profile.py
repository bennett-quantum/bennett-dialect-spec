"""Publication profiles compose version differences without replacing module source."""
import unittest
from dialect_profile import ISA08, ISA09, profile, using_profile


class Profiles(unittest.TestCase):
    def test_scoped_versions_and_lproc_groups(self):
        self.assertEqual(profile(), ISA08)
        with using_profile(ISA09):
            self.assertEqual(profile().isa, '0.9')
            self.assertEqual(profile().signature({'kind': 'lproc', 'params': [8]}),
                             {'kind': 'lproc', 'params': [8], 'args': [], 'mem': [], 'tokens': []})
            self.assertEqual(profile().verdict('blocked:BD-B-ISA4'), 'accept')
            self.assertEqual(profile().verdict('reject:BD-E-OPERAND'), 'reject:BD-E-OPERAND')
        self.assertEqual(profile(), ISA08)
        self.assertEqual(profile().signature({'kind': 'lproc'}), {'kind': 'lproc'})

    def test_exception_restores_profile(self):
        with self.assertRaisesRegex(ValueError, 'fixture'):
            with using_profile(ISA09):
                raise ValueError('fixture')
        self.assertEqual(profile(), ISA08)
