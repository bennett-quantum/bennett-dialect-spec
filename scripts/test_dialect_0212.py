"""Executable consumer-gap regressions, independent LLVM N0 lowering."""
import unittest
import dialect_check as d
from dialect_check_v02 import Analysis02, headless_env

class N0Resolution(unittest.TestCase):
    def test_widenable_definition_and_original_addresses(self):
        headless_env()
        text='''declare i1 @llvm.experimental.widenable.condition()
@alias = alias i1 (), ptr @f
define i1 @f() {
 %r = call i1 @llvm.experimental.widenable.condition()
 ret i1 %r
}
'''
        for major in d.MAJORS:
            a=Analysis02(d.Module(text));a.major=major
            self.assertEqual(a.resolve('f'),'f')
            self.assertEqual(a.resolve('alias'),'f')
            # Resolution's virtual bodies must not mutate the address-bearing source.
            self.assertIn('llvm.experimental.widenable.condition',a.m.funcs['f'].instrs().__next__().text)

if __name__=='__main__':unittest.main()
