"""Suite selection keeps expensive execution tests in an explicit gate run."""
import unittest
from run_tests import partition, slow


class Selection(unittest.TestCase):
    def test_partition_retains_each_test_once(self):
        class Examples(unittest.TestCase):
            def test_fast(self):
                self.assertEqual(2 + 3, 5)

            @slow('compiler matrix')
            def test_slow(self):
                self.assertEqual(3 * 4, 12)

        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Examples)
        fast, deferred = partition(suite)
        self.assertEqual([t._testMethodName for t in fast], ['test_fast'])
        self.assertEqual([t._testMethodName for t in deferred], ['test_slow'])
        self.assertEqual(len(fast) + len(deferred), suite.countTestCases())
