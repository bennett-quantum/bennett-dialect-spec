import unittest
from run import ROOT, evaluate, prepare_case, runtime_objects, task_for, tools_for


class SeedTests(unittest.TestCase):
    def test_all_seeds_keep_trace_through_o3_on_all_majors(self):
        tcs = tools_for([18, 20, 23])
        runtime = runtime_objects()
        for path in sorted((ROOT / 'harness/seed_cases').glob('*.ll')):
            case = prepare_case(path, tcs, runtime)
            self.assertTrue(case['cross_major_agreement'], case)
            for major, tc in tcs.items():
                with self.subTest(case=case['id'], major=major):
                    self.assertEqual(case['majors'][str(major)]['issues'], {})
                    result = evaluate(task_for(case, tc, runtime, 'seed-test', 'default<O3>'))
                    self.assertEqual(result['checks'], [], result)
                    self.assertIn(result['outcome'], ('pass', 'noop'))


if __name__ == '__main__':
    unittest.main()
