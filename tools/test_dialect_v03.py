"""Exercise publication composition through real recognizer verdicts."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import dialect_check as d
import dialect_check_v02 as v2
from dialect_profile import ISA09, using_profile


class Publications(unittest.TestCase):
    def test_r_entry_blocker_is_isa09_lowering_and_does_not_leak(self):
        source = 'define void @entry() {\n ret void\n}\n'
        self.assertEqual(v2.recognise(source, rmode='@entry')[0], 'blocked:BD-B-ISA7')
        with using_profile(ISA09):
            verdict, info = v2.recognise(source, rmode='@entry')
            self.assertEqual(verdict, 'accept')
            self.assertEqual([code for code, _ in info.lowerings], ['K5'])
            self.assertEqual(info.blockers, [])
        self.assertEqual(v2.recognise(source, rmode='@entry')[0], 'blocked:BD-B-ISA7')

    def test_rejections_survive_lowering_profile(self):
        source = 'define void @__bennett_bad() {\n ret void\n}\n'
        with using_profile(ISA09):
            self.assertEqual(v2.recognise(source)[0], 'reject:BD-E-MARKER-UNKNOWN')

    def test_selected_document_controls_full_version(self):
        source = ('define void @entry() {\n ret void\n}\n!llvm.module.flags = !{!0}\n'
                  '!0 = !{i32 1, !"bennett.dialect", !"VERSION"}\n')
        with using_profile(ISA09), patch.object(d, 'SPEC_PATH', d.ROOT / 'spec' / ISA09.spec_name):
            self.assertEqual(v2.recognise(source.replace('VERSION', '0.3'))[0], 'accept')
            self.assertEqual(v2.recognise(source.replace('VERSION', '0.2.14'))[0], 'reject:BD-E-VERSION')

    def test_runner_derives_lowering_report_and_rejects_wrong_label(self):
        from dialect_check_v03 import Runner03
        source = 'define void @entry() {\n ret void\n}\n'
        block = {'body': source, 'attrs': {'example': 'entry', 'rmode': '@entry',
                                         'verdict': 'accept', 'lowering': 'K5'}}
        runner = object.__new__(Runner03)
        runner.by_tag = {'example': {'entry': block}}
        report = {'body': 'K5 reversible entry\n', 'attrs': {'lowering-report': 'entry'}}
        with using_profile(ISA09), patch.object(d, 'SPEC_PATH', d.ROOT / 'spec' / ISA09.spec_name):
            self.assertIsNone(runner.recognition(block))
            self.assertIsNone(runner.lowering(report))
            with self.assertRaises(v2.Mismatch):
                runner.recognition(dict(block, attrs=dict(block['attrs'], lowering='K2')))
            with self.assertRaises(d.Fail):
                runner.lowering(dict(report, body='K2 wrong ledger row\n'))

    def test_unknown_family_is_an_argument_error(self):
        import contextlib
        import io
        from dialect_check_v03 import main
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            main(['--family', 'not-a-check-family'])
        self.assertEqual(caught.exception.code, 2)


class FixtureFailures(unittest.TestCase):
    def test_unexpected_emission_errors_remain_failed_rows(self):
        import dialect03_witnesses as witnesses
        runner = object.__new__(v2.Runner)
        runner.rows, runner.selected = [], set()
        with tempfile.TemporaryDirectory() as tmp:
            runner.tmp = Path(tmp)
            for diagnostic in ('invalid signature', 'interface hash mismatch', 'interpreter command exited 127'):
                with self.subTest(diagnostic=diagnostic):
                    error = d.Fail('fixture: ' + diagnostic)
                    with patch.object(witnesses.cc, 'emit', side_effect=error):
                        with self.assertRaises(d.Fail) as caught:
                            witnesses.build(runner, 'malformed', [], {})
                        self.assertIs(caught.exception, error)
                        runner.check('isa09', 'malformed', 'fixture',
                                     lambda: witnesses.build(runner, 'malformed', [], {}))
                    self.assertEqual(runner.rows[-1]['status'], 'failed')
                    self.assertIn(str(error), runner.rows[-1]['detail'])
                    self.assertEqual(runner.rows[-1]['blocked_on'], '')

    def test_unsupported_emission_requires_second_reader_pin(self):
        import dialect03_witnesses as witnesses
        runner = object.__new__(v2.Runner)
        runner.rows, runner.selected = [], set()
        with tempfile.TemporaryDirectory() as tmp:
            runner.tmp = Path(tmp)
            with patch.object(witnesses.cc, 'emit', side_effect=d.Fail('qreg instructions are CC only')):
                runner.check('isa09', 'unsupported', 'fixture',
                             lambda: witnesses.build(runner, 'unsupported', [], {}))
        self.assertEqual(runner.rows[0]['status'], 'blocked')
        self.assertIn('SECOND-READER-PIN', runner.rows[0]['blocked_on'])

    def test_successful_emission_returns_object_path(self):
        import dialect03_witnesses as witnesses
        runner = object.__new__(v2.Runner)
        with tempfile.TemporaryDirectory() as tmp:
            runner.tmp = Path(tmp)
            with patch.object(witnesses.cc, 'emit') as emit:
                result = witnesses.build(runner, 'valid', [], {})
            self.assertEqual(result, Path(tmp) / 'valid.bisa')
            emit.assert_called_once_with(runner, result, [], {}, None, None)
