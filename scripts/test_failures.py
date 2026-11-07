"""Malformed checker inputs and programming errors must keep diagnostic identity."""
import unittest
import dialect_check as d
import dialect_check_v02 as v


class Diagnostics(unittest.TestCase):
    def test_bad_constant_is_not_an_unknown_value_set(self):
        module = d.Module('@g = internal constant [1 x i8] [i8 invalid]\n'
                          'define i8 @f() {\n %v = load i8, ptr @g\n ret i8 %v\n}\n')
        with self.assertRaisesRegex(d.Fail, 'value-set analysis.*%v'):
            v.value_set(module, module.funcs['f'], '%v')

    def test_checker_defect_is_distinguished_from_contract_failure(self):
        runner = object.__new__(v.Runner)
        runner.selected, runner.rows = set(), []
        def missing_field():
            return {}['missing']
        runner.check('state', 'broken', 'fixture', missing_field)
        self.assertEqual(runner.rows[0]['status'], 'failed')
        self.assertIn('checker defect KeyError', runner.rows[0]['detail'])
        self.assertIn('missing', runner.rows[0]['detail'])
