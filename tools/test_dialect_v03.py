"""Red-green unit tests of the 0.3 pre-flight's own mechanics (no spec gate)."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import dialect03_patches as P

class Patches(unittest.TestCase):
    def test_exact_hit_count_is_enforced(self):
        self.assertEqual(P.apply('abc abc',[('abc','x',2)],'m'),'x x')
        with self.assertRaises(RuntimeError):P.apply('abc abc',[('abc','x',1)],'m')
        with self.assertRaises(RuntimeError):P.apply('abc',[('zzz','x',1)],'m')

    def test_every_listed_module_exists_and_patches_apply(self):
        scripts=Path(__file__).parent.parent/'scripts'
        for name,edits in P.MODULES.items():
            text=(scripts/(name+'.py')).read_text()
            out=P.apply(text,edits,name)
            self.assertNotEqual(text,out,name)

    def test_blocker_verdicts_map_to_isa09_rows(self):
        self.assertEqual(P.LOWERING,{'BD-B-ISA4':'K1','BD-B-ISA1':'K3','BD-B-ISA12':'K2','BD-B-ISA7':'K5'})

if __name__=='__main__':unittest.main()
