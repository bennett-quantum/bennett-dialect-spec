#!/usr/bin/env python3
"""Dialect 0.3 pre-flight composed with the ISA 0.9 publication profile."""
import argparse
import collections
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import dialect_check as d
import dialect_check_v02 as v2
from dialect_profile import ISA09, using_profile
import dialect03_witnesses as W


class Runner03(v2.Runner):
    def materialised(self,block):
        return block['attrs'].get('mode') in ('materialised','validate')

    def recognition(self,b):
        super().recognition(b)
        a=b['attrs']
        if a.get('mode')=='validate':return
        _,info=v2.recognise(d.with_decls(b['body']),rmode=a.get('rmode'),materialised=self.materialised(b))
        want=set(filter(None,a.get('lowering','').split(',')))
        v2.equal(a['example'],'§25.1 ISA 0.9 lowering rows',want,{k for k,_ in getattr(info,'lowerings',[])})

    def lowering(self,b):
        ident=b['attrs']['lowering-report'];source=self.block('example',ident)
        verdict,info=v2.recognise(d.with_decls(source['body']),materialised=self.materialised(source),rmode=source['attrs'].get('rmode'))
        v2.equal(ident,'§25.1 verdict','accept',verdict)
        got={k for k,_ in info.lowerings}
        for line in b['body'].strip().splitlines():
            row=line.split()[0]
            if row not in got:raise d.Fail(f'{ident}: report row {row} not derived; derived {sorted(got)}')
        v2.equal(ident,'§25.1 every derived row reported',got,{ln.split()[0] for ln in b['body'].strip().splitlines()})

    def run(self):
        rows=super().run()
        for b in self.blocks:
            if 'lowering-report' in b['attrs']:
                self.check('lowering',b['attrs']['lowering-report'],'§25.1',lambda b=b:self.lowering(b))
            if 'witness09' in b['attrs']:
                self.check('isa09',b['attrs']['witness09'],'ISA 0.9 '+b['attrs'].get('row','?'),lambda b=b:W.check(self,b))
        W.delta_checks(self)
        return rows


def main(argv=None):
    with using_profile(ISA09):
        parser=argparse.ArgumentParser(description='Dialect 0.3 pre-flight against ISA 0.9.')
        parser.add_argument('spec',nargs='?',type=Path,default=ROOT / "spec" / ISA09.spec_name)
        parser.add_argument('--family',action='append')
        parser.add_argument('--json',type=Path)
        args=parser.parse_args(argv)
        selected={x for f in args.family or [] for x in f.split(',')}
        v2.headless_env()
        text=args.spec.read_text();blocks=d.extract_blocks(text)
        v2.initialise(blocks);d.SPEC_PATH=args.spec
        tmp=v2.SCRATCH/(time.strftime('run-%Y%m%dT%H%M%S-')+str(os.getpid()));tmp.mkdir()
        rows=Runner03(blocks,text,tmp,selected).run()
        print('\nfamily          examples passed failed blocked blocked-on')
        for family in sorted({r['family'] for r in rows}):
            rs=[r for r in rows if r['family']==family]
            n=collections.Counter(r['status'] for r in rs)
            print(f"{family:16}{len(rs):8}{n['passed']:7}{n['failed']:7}{n['blocked']:8} "+'; '.join(sorted({r['blocked_on'] for r in rs if r['blocked_on']})))
        if args.json:args.json.write_text(json.dumps(rows,indent=2)+'\n')
        print(v2.summary(rows))
        n=collections.Counter(r['status'] for r in rows)
        print(f"\n{'OK' if n['passed']==len(rows) else 'FAIL'}: {n['passed']}/{len(rows)} passed; {n['failed']} failed; {n['blocked']} blocked")
        return 0 if n['passed']==len(rows) else 1


if __name__=='__main__':sys.exit(main())
