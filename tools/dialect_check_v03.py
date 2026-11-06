#!/usr/bin/env python3
"""Pre-flight for dialect draft 0.3 (grading target ISA 0.9); see tools/README.md."""
import argparse,collections,fcntl,hashlib,importlib.abc,importlib.machinery,importlib.util,json,os,re,subprocess,sys,time
from pathlib import Path

TOOLS=Path(__file__).resolve().parent
ROOT=TOOLS.parent
SCRIPTS=ROOT/'scripts'
sys.path.insert(0,str(TOOLS))
import dialect03_patches as P


class Patched(importlib.machinery.SourceFileLoader):
    def get_data(self,path):
        data=super().get_data(path)
        name=Path(path).stem
        if path.endswith('.py') and name in P.MODULES:
            return P.apply(data.decode(),P.MODULES[name],name).encode()
        return data
    def path_stats(self,path):raise OSError('patched modules bypass the bytecode cache')
    def set_data(self,*_a,**_k):pass


class Finder(importlib.abc.MetaPathFinder):
    def find_spec(self,name,path=None,target=None):
        file=SCRIPTS/(name+'.py')
        if not file.exists():return None
        return importlib.util.spec_from_file_location(name,str(file),loader=Patched(name,str(file)))


sys.meta_path.insert(0,Finder())
sys.dont_write_bytecode=True
(ROOT/'.tmp'/'dialect03'/'scratch').mkdir(parents=True,exist_ok=True)
import dialect_check as d
import dialect_check_v02 as v2
import dialect03_witnesses as W

ISA_REPO=ROOT.parent/'bennett-isa-spec'


class PinnedInterpreter(v2.Interpreter):
    """The reference interpreter at the ISA repo's committed HEAD, never its dirty tree."""
    def build(self):
        commit=subprocess.run(['git','-C',str(ISA_REPO),'rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip()
        if self.ready and self.commit==commit:return
        source=v2.ISA_DIR.resolve()/commit[:16]
        manifest=source/'reference-interpreter'/'Cargo.toml'
        self.exe=manifest.parent/'target'/'release'/'bennett-isa-ref'
        v2.ISA_DIR.mkdir(parents=True,exist_ok=True)
        with (v2.ISA_DIR/'build.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            if not self.exe.exists():
                source.mkdir(parents=True,exist_ok=True)
                archive=subprocess.run(['git','-C',str(ISA_REPO),'archive',commit,'reference-interpreter','conformance','spec/ref-0.9.json'],capture_output=True,check=True).stdout
                subprocess.run(['tar','-x','-C',str(source)],input=archive,check=True)
                v2.command(['cargo','build','--release','--offline','-j4','--manifest-path',manifest,'--target-dir',manifest.parent/'target'],timeout=600)
        self.commit=commit;self.ready=True


v2.Interpreter=PinnedInterpreter
ORIGINAL_RECOGNISE=v2.recognise


def recognise03(text,**options):
    """Every 0.8 blocker class has an ISA 0.9 lowering: the verdict is accept and the row is recorded."""
    verdict,info=ORIGINAL_RECOGNISE(text,**options)
    if verdict.startswith('reject:'):return verdict,info
    rows=[(P.LOWERING[code],reason) for code,reason in info.blockers]
    if info.reversible:
        for f in info.funcs():
            if f.name in info.reversible and any(mk in ('qalloc','qborrow','qfree') for _,_,mk in info.marker_calls(f)):
                rows.append(('K2','§7.5(b) ledger frames in R: @'+f.name))
    info.lowerings=rows;info.blockers=[]
    return 'accept',info


v2.recognise=recognise03


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
    parser=argparse.ArgumentParser(description='Dialect 0.3 pre-flight against ISA 0.9.')
    parser.add_argument('spec',nargs='?',type=Path,default=d.SPEC)
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
