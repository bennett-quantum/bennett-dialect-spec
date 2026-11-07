"""Soundness of the R-contract clause/fixture registration, without an executor."""
import json
import contextlib
import io
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import dialect_check as d
import dialect_r_contract as contract
import dialect_check_v02 as v2


class ContractClauses(unittest.TestCase):
    def test_each_case_detects_removal_of_its_binding_clause(self):
        text = (d.ROOT / 'spec' / 'Bennett-Dialect-Spec-0.3-draft.md').read_text()
        for path in sorted(contract.CASES.glob('*.json')):
            case = json.loads(path.read_text())
            with self.subTest(case=case['id']):
                contract.clauses(SimpleNamespace(spec=text), case)
                sentence = case['requires'][0][1]
                self.assertIn(sentence, text)
                with self.assertRaises(d.Fail):
                    contract.clauses(SimpleNamespace(spec=text.replace(sentence, '', 1)), case)

    def test_a_clause_in_the_wrong_section_does_not_count(self):
        text = '### 11.2 Console\nTyped fault required.\n### 17.6 R tier\nNo rule here.\n'
        case = {'id': 'misplaced', 'requires': [['17.6', 'Typed fault required.']]}
        with self.assertRaises(d.Fail):
            contract.clauses(SimpleNamespace(spec=text), case)

    def test_a_missing_case_group_fails_instead_of_empty_green(self):
        with patch.object(contract, 'CASES') as cases:
            cases.glob.return_value = []
            with self.assertRaises(d.Fail):
                contract.check_all(SimpleNamespace(selected={'r-contract'}))

    def test_legacy_checker_cannot_report_empty_green_for_this_family(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as caught:
                v2.main(['--family', 'r-contract'])
        self.assertEqual(caught.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
