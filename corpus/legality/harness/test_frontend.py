import pathlib
import tempfile
import unittest
from run import ROOT, evaluate_frontend, prepare_case, runtime_objects, task_for, tools_for


class FrontendTests(unittest.TestCase):
    def test_real_clang18_lto_with_system_cc_link(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'harness') as d:
            source = pathlib.Path(d) / 'frontend-test.c'
            source.write_text('''// CASE: frontend-test
// HAZARD: harness front-end integration fixture
// INPUTS: 0..3
// EXPECT: legal
#include "markers.h"
int64_t case_entry(int64_t x) {
 bq h=__bennett_qalloc(0,1);
 __bennett_gate(1,h,0);
 __bennett_qfree(h);
 return x;
}
''')
            tc = tools_for([18])
            rt = runtime_objects()
            case = prepare_case(source, tc, rt)
            self.assertNotIn('error', case)
            r = evaluate_frontend(task_for(case, tc[18], rt, 'P4', 'clang-O3-LTO'))
            self.assertEqual(r['outcome'], 'pass', r)


if __name__ == '__main__':
    unittest.main()
