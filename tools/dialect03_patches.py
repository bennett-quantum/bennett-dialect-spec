"""Exact source patches that retarget the frozen 0.2 checker modules at ISA 0.9.

`scripts/` stays byte-identical so the 0.2.14 gate is unaffected. Each edit is
(old, new, required hit count): a module that has drifted fails loud at import.
"""
ISA_TOKENS='isa=0.8 object=0.8 launch=0.8 sched=0.8 cert=0.8 coverage=0.8 target=0.8'
ISA_TOKENS_09=ISA_TOKENS.replace('0.8','0.9')

LOWERING={'BD-B-ISA4':'K1','BD-B-ISA1':'K3','BD-B-ISA12':'K2','BD-B-ISA7':'K5'}


def _abi(n):return ("'abi':'0.8'","'abi':'0.9'",n)
def _dev(n):return ("'version':'0.8'","'version':'0.9'",n)
def _hdr(n):return (ISA_TOKENS,ISA_TOKENS_09,n)


MODULES={
    'dialect_0212_vectors':[_abi(1)],
    'dialect_cc':[_abi(2),_dev(2),_hdr(1)],
    'dialect_check':[('"abi": "0.8"','"abi": "0.9"',1),
                     ('sibling("bennett-isa-spec") / "spec" / "Bennett-ISA-Spec.md"','sibling("bennett-isa-spec") / "spec" / "Bennett-ISA-Spec-0.9.md"',1),
                     ('ROOT / "spec" / "Bennett-Dialect-Spec.md"','ROOT / "spec" / "Bennett-Dialect-Spec-0.3-draft.md"',1)],
    'dialect_check_v02':[_abi(3),_hdr(2),
                         ('if version != "0.2.12":','if version != "0.3":',1),
                         ('"§19.9 expected 0.2.12; actual "','"§19.9 expected 0.3; actual "',1),
                         ("signatures.append({'abi':'0.9','kind':'lproc','tier':'q','params':[width],'result':width})","signatures.append({'abi':'0.9','args':[],'kind':'lproc','mem':[],'tier':'q','params':[width],'result':width,'tokens':[]})",1),
                         ("SCRATCH = ROOT / 'scripts' / '.tmp'","SCRATCH = ROOT / '.tmp' / 'dialect03' / 'scratch'",1),
                         ("ISA_DIR = ROOT / 'scripts' / '.isa-ref'","ISA_DIR = ROOT / '.tmp' / 'dialect03' / 'isa-ref'",1)],
    'dialect_driver':[_dev(1)],
    # The 0.2.10 byte baseline is replaced by the exact 0.2.14-to-0.3 delta of dialect03_witnesses.delta_checks.
    'dialect_0211_contract':[("runner.check('coverage','0211/baseline','S0 retained checked examples',baseline)","pass",1)],
    'dialect_map':[_abi(3),_hdr(1),
                   ("sig={'abi':'0.9','kind':'lproc','params':pws,'result':R,'tier':'q'}","sig={'abi':'0.9','args':[],'kind':'lproc','mem':[],'params':pws,'result':R,'tier':'q','tokens':[]}",1)],
    'dialect_round2':[_abi(2)],
    'dialect_round3':[_abi(2),
                      ("'validate':{'abi':'0.9','kind':'lproc','params':[64]*8,'result':1,'tier':'q'}","'validate':{'abi':'0.9','args':[],'kind':'lproc','mem':[],'params':[64]*8,'result':1,'tier':'q','tokens':[]}",1)],
    'dialect_round5':[("'blocked:BD-B-ISA4',verdict","'accept',verdict",1)],
    'dialect_tdl':[_abi(5),_hdr(1)],
}


def apply(text,edits,module):
    for old,new,count in edits:
        hits=text.count(old)
        if hits!=count:
            raise RuntimeError(f'{module}: expected {count} of {old!r}; actual {hits}; update dialect03_patches.py after review')
        text=text.replace(old,new)
    return text
