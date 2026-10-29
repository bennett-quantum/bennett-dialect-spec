"""Dialect 0.2 checks. Grammar/toolchain utilities are shared with dialect_check.

No execution result is supplied by the Python interpreter retained from 0.1.
Each result includes its example, contract rule, expected value and observation.
"""
import argparse
import collections
import difflib
import fnmatch
import fcntl
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

sys.modules.setdefault("dialect_check_v02", sys.modules[__name__])
import dialect_check as d

ROOT = d.ROOT
SCRATCH = ROOT / 'scripts' / '.tmp'
ISA_DIR = ROOT / 'scripts' / '.isa-ref'
ISA_SOURCE = ROOT.parent / 'bennett-isa-spec' / 'reference-interpreter'
CLI_BEAD = 'b-isa-spec-xam'
TAGS = ('markers-ir', 'markers-c', 'example', 'normalise-in', 'normalise-out',
        'native', 'lift', 'linkmap', 'object', 'reference-body', 'hash', 'run',
        'fb', 'step-check', 'inplace', 'semantics', 'events', 'state', 'tdl',
        'cc-run', 'blocker', 'budget-table', 'run-program')
TAG_FAMILY = dict(zip(TAGS, (
    'header', 'header', 'recognise', 'normalise', 'normalise', 'native', 'map',
    'map', 'check', 'map', 'hash', 'run-oracle', 'run-oracle', 'step-check',
    'inplace', 'trace', 'events', 'state', 'tdl', 'cc-run', 'blocker', 'driver',
    'run-program')))


class Mismatch(d.Fail):
    pass


class Unavailable(d.Fail):
    def __init__(self, capability, command, bead):
        self.command, self.bead = command, bead
        super().__init__(f'P-2 checker-unimplemented: {capability}; expected executable check; '
                         f'actual unavailable; needs {command}; blocked-on {bead}')


def equal(example, rule, expected, actual):
    if expected != actual:
        raise Mismatch(f'{example} [{rule}] expected={expected!r}; actual={actual!r}')


def initialise(blocks):
    d.MARKERS.clear()
    d.MARKERS.update(d.marker_list(blocks))
    d.MARKERS_SHORT.clear()
    d.MARKERS_SHORT.update(n[10:] for n in d.MARKERS)
    d.DECLS_TEXT.clear()
    for name, fn in d.MARKERS.items():
        d.DECLS_TEXT[name] = 'declare ' + d.tstr(fn.ret) + ' @' + name + '(' + ', '.join(d.tstr(p[0]) for p in fn.params) + ')'
    d.DECLS_TEXT.update({
        '__bennett_nz_fault': 'declare void @__bennett_nz_fault(i64)',
        '__bennett_nz_alloc': 'declare ptr @__bennett_nz_alloc(i64)',
        '__bennett_nz_free': 'declare void @__bennett_nz_free(ptr)',
    })
    d.PERMITTED_FN.update('strictfp cold hot nomerge noinline convergent builtin nobuiltin optsize minsize optnone'.split())
    d.HANDLE_OPS.update({n: [] for n in d.MARKERS_SHORT if n.startswith('effect_')})
    d.HANDLE_OPS.update(qprep=[0], observe=[], oracle=[], inplace=[])
    d.ENV_OP.update(adj=2, compute=3)
    d.INT_CAND_OPS.update(inplace={}, oracle={})


def families(block):
    out = {TAG_FAMILY[k] for k in block['attrs'] if k in TAG_FAMILY}
    if block['lang'] == 'llvm':
        out.add('parse')
    if block['lang'] in ('c', 'rust', 'julia') and 'example' in block['attrs']:
        out.add('frontend')
    return sorted(out)


def headless_env():
    env = dict(os.environ)
    for key in ('DISPLAY', 'WAYLAND_DISPLAY', 'DBUS_SESSION_BUS_ADDRESS', 'BROWSER'):
        env.pop(key, None)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    env['TMPDIR'] = str(SCRATCH)
    return env


def command(argv, timeout=120, cwd=None):
    argv = list(map(str, argv))
    if any(re.search(r'(^-|[,(=])(?:-?view-)', a) for a in argv[1:] if a.startswith('-')):
        raise d.Fail('rule 11: forbidden LLVM view pass: ' + shlex.join(argv))
    try:
        p = subprocess.run(argv, capture_output=True, text=True, env=headless_env(),
                           timeout=timeout, cwd=cwd)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise d.Fail(f'command={shlex.join(argv)}; expected exit=0; actual={e}') from e
    if p.returncode:
        raise d.Fail(f'command={shlex.join(argv)}; expected exit=0; actual exit={p.returncode}\n'
                     + p.stderr.strip() + '\n' + p.stdout.strip())
    return p.stdout


def frontend_bins():
    import tomllib
    config = tomllib.loads(d.TOOLCHAINS.read_text())
    return {k: Path(config['llvm' + k].get('frontend_bin', config['llvm' + k]['bin']))
            for k in d.MAJORS}


def read_commit(repo):
    """Read the checkout identity without changing the checkout."""
    gd = repo / '.git'
    if gd.is_file():
        gd = (repo / gd.read_text().strip().split(': ', 1)[1]).resolve()
    head = (gd / 'HEAD').read_text().strip()
    if not head.startswith('ref: '):
        return head
    ref = head[5:]
    if (gd / ref).exists():
        return (gd / ref).read_text().strip()
    for ln in (gd / 'packed-refs').read_text().splitlines():
        if ln.endswith(' ' + ref):
            return ln.split()[0]
    raise d.Fail('cannot resolve interpreter checkout HEAD ' + ref)


class Interpreter:
    def __init__(self):
        self.exe = ISA_DIR / 'source' / 'target' / 'debug' / 'bennett-isa-ref'
        self.ready = False
        self.commit = None

    def build(self):
        commit=read_commit(ISA_SOURCE.parent)
        if self.ready and self.commit==commit:
            return
        self.ready=False
        # Content fingerprints catch concurrent uncommitted command additions too.
        paths = sorted(p for p in ISA_SOURCE.rglob('*') if p.is_file() and
                       not any(x in ('target','.tmp','.git','.beads') for x in p.relative_to(ISA_SOURCE).parts) and
                       (p.suffix == '.rs' or p.name in ('Cargo.toml', 'Cargo.lock', 'README.md')))
        before = {str(p.relative_to(ISA_SOURCE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        fingerprint = hashlib.sha256(json.dumps({'commit':commit,'files':before}, sort_keys=True).encode()).hexdigest()
        ISA_DIR.mkdir(parents=True,exist_ok=True)
        # Content-addressed immutable snapshots keep a later build from deleting
        # the executable another checker process is still using.
        source = ISA_DIR / ('source-'+fingerprint[:20])
        self.exe = source / 'target' / 'debug' / 'bennett-isa-ref'
        stamp = ISA_DIR / ('BUILD-'+fingerprint[:20]+'.json')
        with (ISA_DIR/'build.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            if not stamp.exists() or not self.exe.exists():
                if not source.exists():
                    shutil.copytree(ISA_SOURCE, source, ignore=shutil.ignore_patterns('target', '.git', '.tmp', '.beads'))
                copied = {k: hashlib.sha256((source / k).read_bytes()).hexdigest() for k in before}
                after = {str(p.relative_to(ISA_SOURCE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
                if before != after or before != copied or read_commit(ISA_SOURCE.parent)!=commit:
                    raise d.Fail('interpreter sources changed during snapshot; rerun to take a consistent copy')
                command(['cargo', 'build', '--offline', '--manifest-path', source / 'Cargo.toml'], timeout=120)
                stamp.write_text(json.dumps({'commit': commit,
                    'source_sha256': fingerprint, 'files': before}, indent=2) + '\n')
            (ISA_DIR/'BUILD.json').write_text(stamp.read_text())
        if read_commit(ISA_SOURCE.parent)!=commit:
            raise d.Fail("interpreter HEAD moved during build; rerun for a consistent snapshot")
        self.commit=commit
        self.ready = True

    def call(self, verb, *args):
        self.build()
        readme = (self.exe.parents[2] / 'README.md').read_text()
        if verb in ('run-cc', 'reverse', 'run-action', 'run-program') and not re.search(r'(?:`|bennett-isa-ref )' + verb + r'\s', readme+'\n'+command([self.exe,'--help'])):
            raise Unavailable(verb, shlex.join(['bennett-isa-ref', verb, *map(str, args)]), CLI_BEAD)
        output = command([self.exe, verb, *args], timeout=180)
        try:
            return json.loads(output)
        except ValueError as e:
            raise d.Fail(f'{verb}: expected one JSON result; actual={output!r}') from e


def expanded_types(text):
    types = dict(re.findall(r'^(%[-\w.$]+) = type (.+)$', text, re.M))
    for _ in range(len(types) + 1):
        changed = False
        for name, val in list(types.items()):
            new = re.sub(r'%[-\w.$]+', lambda m: types.get(m[0], m[0]), val)
            changed |= val != new
            types[name] = new
        if not changed:
            break
    lines = [ln for ln in text.splitlines() if not re.match(r'^%[-\w.$]+ = type ', ln)]
    return '\n'.join(re.sub(r'%[-\w.$]+', lambda m: types.get(m[0], m[0]), ln) for ln in lines) + '\n'


def value_set(mod, f, val, seen=None):
    """PT3/PT5/PT6 finite integer values, capped at normative K=4096."""
    seen = set() if seen is None else set(seen)
    if re.fullmatch(r'-?\d+', val):
        return {int(val) % (1 << 64)}
    if val in ('true', 'false'):
        return {int(val == 'true')}
    if val in seen:
        return 'TOP'
    seen.add(val)
    ins = next((x for x in f.instrs() if x.res == val), None)
    if ins is None:
        for ty, attrs, name in f.params:
            if name == val:
                for attr in attrs:
                    m = re.match(r'range\(i\d+ (-?\d+), (-?\d+)\)', attr)
                    if m and 0 <= int(m[2]) - int(m[1]) <= 4096:
                        return set(range(int(m[1]), int(m[2])))
        return 'TOP'
    body = ins.text.split(' = ', 1)[1]
    if ins.op in ('phi', 'select'):
        vals = d.Analysis(mod).value_operands(ins)
        sets = [value_set(mod, f, x, seen) for x in vals]
        return 'TOP' if 'TOP' in sets else set.union(set(), *sets)
    if ins.op in d.BINOPS:
        rest = d.strip_flags(body.split(None, 1)[1])
        ty, n = d.parse_type(rest)
        a, b = d.split_top(rest[n:])
        sa, sb = value_set(mod, f, a, seen), value_set(mod, f, b, seen)
        w = ty[1]
        if sa == 'TOP' and isinstance(sb, set) and len(sb) == 1:
            m, = sb
            if ins.op == 'and' and m.bit_count() <= 12:
                bits = [1 << i for i in range(w) if m & (1 << i)]
                return {sum(x) for n in range(len(bits)+1) for x in itertools.combinations(bits, n)}
            if ins.op == 'urem' and 0 < m <= 4096:
                return set(range(m))
        if sa == 'TOP' or sb == 'TOP' or len(sa) * len(sb) > 4096:
            return 'TOP'
        ops = {'add': lambda a,b:a+b, 'sub':lambda a,b:a-b, 'mul':lambda a,b:a*b,
               'and':lambda a,b:a&b, 'or':lambda a,b:a|b, 'xor':lambda a,b:a^b,
               'shl':lambda a,b:a<<b if b<w else 0, 'lshr':lambda a,b:a>>b if b<w else 0,
               'urem':lambda a,b:a%b if b else 0, 'udiv':lambda a,b:a//b if b else 0}
        if ins.op not in ops:
            return 'TOP'
        return {ops[ins.op](a,b) % (1<<w) for a in sa for b in sb}
    try:
        return d.int_candidates(mod, f, val)
    except (IndexError, ValueError):
        return 'TOP'


# The recogniser shares S1's signature/attribute and invoke handling with 0.1.
# S2–S8 are defined below in terms of the 0.2 points-to and containment rules.
from dialect_flow import Flow


class Analysis02(Flow, d.Analysis):
    def first_candidates(self):
        # §1.5: first region operand (both operands of an inplace pair).
        for f in self.funcs():
            for ins, c, mk in self.marker_calls(f):
                if mk in d.REGION_OPS:
                    keys = list(d.REGION_OPS[mk]) if mk == 'inplace' else [next(iter(d.REGION_OPS[mk]))]
                    return set().union(*(self.cands[(id(ins), k)] for k in keys))
        return set()


def recognise(text, **options):
    a = Analysis02(d.Module(expanded_types(text)), materialised=options.get("materialised", False))
    a.major=options.get('major')
    try:
        a.s1()
        for version in re.findall(r'!"bennett.dialect", !"([^"\n]+)"', text):
            if version != "0.2.2":
                raise d.Reject("BD-E-VERSION", "§19.9 expected 0.2.2; actual " + version)
        a.analyse()
        a.region_rules()
        a.handle_rules()
        a.operand_rules()
        a.descriptor_rules()
        a.tdl_rules()
        a.instance_rules()
        verify_inplace02(a)
        return ('blocked:' + a.blockers[0][0] if a.blockers else 'accept'), a
    except d.Reject as e:
        return 'reject:' + e.code, e


# Explicit link facts for the standalone normalisation microvectors. These are
# published runtime/arith entry points (and the n-eh seed), not a name-prefix
# exemption for arbitrary unresolved functions. Full L/R validation defaults to
# an empty link environment.
NORMALISATION_LINK={
    '__bennett_rt_ss_push','__bennett_rt_ss_pop','__bennett_rt_memmove',
    '__bennett_rt_memset','__bennett_rt_ctpop_i32','__bennett_rt_eh_match',
    '__bennett_rt_syscall','__bennett_rt_poll','may_throw','exp','sinf',
    '__bennett_sf_cmp_f64','__bennett_sf_add_f64','__bennett_sf_mul_f64',
    '__bennett_sf_add_f80','__bennett_sf_fpext_f64_f80','__bennett_sf_fpext_f32_f64',
} | {'__bennett_rt_mmio_'+op+'_i'+str(w) for op in ('load','store') for w in (8,16,32,64,128)}


def validate(text,*,linked=()):
    m = d.Module(expanded_types(text))
    def bad(rule, where):
        raise d.Reject('BD-E-RESIDUAL', rule + ': ' + where)
    for f in m.funcs.values():
        if not f.is_def:
            continue
        for ins in f.instrs():
            body = ins.text.split(' = ', 1)[-1]
            toks = set(body.replace(',', ' ').split())
            if toks & (d.INT_FLAGS | d.FMF): bad('V1', ins.text)
            if re.search(r',\s*!(?!dbg\b|bennett\.rstep\b)[\w.]+\s+!', body): bad('V2', ins.text)
            if re.search(r'\b(undef|poison)\b', body): bad('V5', ins.text)
            if ins.op in ('freeze','fence','atomicrmw','cmpxchg') or re.search(r'\b(atomic|volatile)\b', body): bad('V6', ins.text)
            if ins.op == 'alloca': bad('V11', ins.text)
            if re.search(r'<(?:vscale x )?\d+ x ', body): bad('V13', ins.text)
            if any(int(w)>128 for w in re.findall(r'\bi(\d+)\b', body)): bad('V14', ins.text)
            if ins.op in ('va_arg','invoke','landingpad','resume','cleanuppad','catchpad','catchswitch','cleanupret','catchret'): bad('V15', ins.text)
            if ' asm ' in ' ' + body: bad('V16', ins.text)
            if ins.op in d.FBINOPS | {'fcmp','fptosi','fptoui','sitofp','uitofp','fpext','fptrunc'}: bad('V9', ins.text)
        for attrs in [f.ret_attrs, f.fn_attrs, *[p[1] for p in f.params]]:
            for attr in m.fn_attr_names(attrs):
                if d.attr_name(attr) in d.N4_PARAM | d.N4_FN: bad('V3', f.name + ': ' + attr)
        allins=list(f.instrs());defs={i.res:i for i in allins if i.res}
        for ins in allins:
            if ins.op in ('call','invoke'):
                c=d.parse_call(ins)
                for attr in c['ret_attrs'] + c['fn_attrs'] + [x for a in c['args'] for x in a[1]]:
                    if d.attr_name(attr) in d.N4_PARAM | d.N4_FN: bad('V3',ins.text)
                cal=c['callee']
                if re.match(r'@llvm\.(abs|ctlz|cttz)\.',cal) and c['args'][-1][2] in ('true','1'):bad('V4',ins.text)
                if cal.startswith('@') and not cal.startswith('@llvm.'):
                    target=m.resolve_alias(cal[1:])
                    if not m.defined(target) and target not in {'__bennett_nz_fault','__bennett_nz_alloc','__bennett_nz_free'} and target not in linked:
                        bad('V12',ins.text)
                if re.match(r'@llvm\.(assume|lifetime|invariant|is\.constant|objectsize|trap|debugtrap|ubsantrap|memcpy|memmove|memset|fmuladd|vector\.|ctpop|[su](?:min|max)|[su]add\.with\.overflow|va_|exp\.|sin\.)',cal):bad('V4',ins.text)
                if re.match(r'@llvm\.(?:x86|aarch64|riscv|arm|amdgcn|nvvm)\.',cal):bad('V16',ins.text)
            if ins.op in ('shl','lshr','ashr'):
                body=ins.text.split(' = ',1)[1].split(None,1)[1];ty,j=d.parse_type(body);_,amount=d.split_top(body[j:]);w=ty[1]
                if amount.isdigit() and int(amount)<w:continue
                uses=[i for i in allins if i is not ins and re.search(re.escape(ins.res)+r'(?![-\w.$])',i.text)]
                ok=len(uses)==1 and uses[0].op=='select'
                if ok:
                    ps=d.split_top(uses[0].text.split(' = ',1)[1][6:].strip());cond=d.typed_val(ps[0]);ci=defs.get(cond)
                    ok=d.typed_val(ps[1])=='0' and d.typed_val(ps[2])==ins.res and ci and ci.text.split(' = ',1)[1]==f'icmp uge i{w} {amount}, {w}'
                if not ok:bad('V7',ins.text)
    return 'accept' 

class Runner:
    def __init__(self, blocks, spec, tmp, selected):
        self.blocks, self.spec, self.tmp, self.selected = blocks, spec, Path(tmp), selected
        self.rows = []
        self.trace_cache = {}
        self.scenario_evidence = set()
        self.tc = d.toolchains()
        self.frontends = frontend_bins()
        self.isa = Interpreter()
        self.by_tag = collections.defaultdict(dict)
        for b in blocks:
            for tag in TAGS:
                if tag in b['attrs']:
                    self.by_tag[tag][b['attrs'][tag]] = b

    def check(self, family, ident, rule, fn):
        if self.selected and family not in self.selected:
            return
        row = {'family': family, 'example': str(ident), 'rule': rule, 'status': 'passed', 'blocked_on': ''}
        try:
            observation=fn()
            if isinstance(observation,dict):row['evidence']=observation
        except Unavailable as e:
            row.update(status='blocked', detail=str(e), blocked_on=e.command + ' / ' + e.bead)
        except (d.Fail, d.Reject, OSError, ValueError, KeyError, IndexError, TypeError, AttributeError) as e:
            # A bug remains a failure and cannot suppress subsequent examples.
            row.update(status='failed', detail=f'expected contract satisfied; actual {type(e).__name__}: {e}')
        self.rows.append(row)
        if row['status'] != 'passed':
            print(f"FAIL {ident} [{rule}] {row.get('detail', '')}", flush=True)

    def block(self, tag, ident):
        if ident not in self.by_tag[tag]:
            raise d.Fail(f'expected {tag}={ident}; actual missing companion block')
        return self.by_tag[tag][ident]

    def object_file(self, ident):
        body = self.block('object', ident)['body']
        path = self.tmp / (str(ident) + '.bisa')
        path.write_text(body)
        return path

    def verify(self, b, major):
        path = self.tmp / f"parse-{b['line']}.ll"
        path.write_text(d.with_decls(b['body']))
        command([self.tc[major] / 'opt', '-passes=verify', '-disable-output', path])

    def materialised(self,block):
        if block['attrs'].get('mode') in ('materialised','validate'):return True
        # BLK-5 witnesses describe normaliser-emitted typed faults, rather than
        # producer inputs. Use their role/report, never a hard-coded example id.
        report=self.by_tag['blocker'].get(block['attrs'].get('example'))
        return bool(report and 'BLK-5' in report['body'] and re.search(r'call void @__bennett_nz_fault\(i64 \d+\)',block['body']))

    def recognition(self, b):
        a = b['attrs']; text = d.with_decls(b['body'])
        if a.get('mode') == 'validate':
            try:
                got, info = validate(text), None
            except d.Reject as e:
                got, info = 'reject:' + e.code, e
        else:
            got, info = recognise(text, rmode=a.get('rmode'), materialised=self.materialised(b))
        equal(a['example'], '§1.6 verdict', a['verdict'], got)
        if 'candidates' in a:
            equal(a['example'], '§7.2 candidates', set(a['candidates'].split(',')), info.first_candidates())
        if 'callees' in a:
            equal(a['example'], '§14.2 callees', set(a['callees'].split(',')), info.first_callees())
        if 'shapes' in a:
            equal(a['example'], '§8.4 shapes', int(a['shapes']), info.shapes)

    def header(self):
        errors = []
        equal('markers-ir', '§3.2', 23, len(d.MARKERS))
        for major in d.MAJORS:
            tc=dict(self.tc);tc['18']=self.frontends[major]
            d.check_markers(self.blocks,tc,self.tmp,errors)
        if errors:
            raise d.Fail('\n'.join(errors))

    def oracle_run(self, b, step=False):
        ident = b['attrs']['step-check' if step else 'run']
        obj = self.object_file(ident)
        for line in b['body'].strip().splitlines():
            fields, expected = line.split(' -> ', 1)
            options = dict(re.findall(r'(\w[\w-]*)=([^ ]*)', fields))
            argv = [obj, 'ref']
            if step: argv += ['--exhaustive']
            else: argv += ['--input', options.pop('input')]
            for k, val in options.items():
                if k == 'mem': val = val.replace(':', '=', 1)
                argv += ['--' + k, val]
            got = self.isa.call('step-check' if step else 'run-oracle', *argv)
            for key, val in re.findall(r'(\w+)=([^ ]+)', expected):
                actual=got.get(key)
                if key=='fixed_regions':
                    equal(ident + ': ' + fields,'ISA §14.2 fixed_regions',val.split(','),actual)
                else:
                    equal(ident + ': ' + fields, 'ISA §14.1/§14.2 ' + key, val, str(actual))

    def hashes(self, b):
        ident = b['attrs']['hash']
        got = self.isa.call('hash', self.object_file(ident))
        for line in b['body'].strip().splitlines():
            name, want = line.split()
            equal(ident + '/' + name, 'ISA §9.2 interface_hash', want, got['symbols'][name]['interface_hash'])

    def blocker(self,b):
        ident=b['attrs']['blocker'];source=self.block('example',ident)
        got,info=recognise(d.with_decls(source['body']), materialised=self.materialised(source))
        equal(ident,'§25.1 verdict',source['attrs']['verdict'],got)
        expected_code=b['body'].split()[0]
        equal(ident,'§25.1 report code',expected_code,got.split(':',1)[1])
        if not info.blockers:raise d.Fail('expected blocker point report; actual none')
        blk=re.search(r'BLK-\d+',b['body'])
        if not blk or not any(blk[0] in reason for _,reason in info.blockers):raise d.Fail('expected blocker reason '+str(blk)+'; actual '+repr(info.blockers))

    def normalisation(self, b):
        ident=b['attrs']['normalise-in']
        want=self.block('normalise-out',ident)['body']
        for major in d.MAJORS:
            got=normalise(b['body'],rmode=b['attrs'].get('rmode'),platform=b['attrs'].get('platform'),major=major)
            if d.collapse(want)!=d.collapse(got):
                diff='\n'.join(difflib.unified_diff(d.collapse(want),d.collapse(got),'expected','actual',lineterm=''))
                raise Mismatch(f'{ident}/llvm{major} [§12] expected normalise-out; actual diff:\n{diff}')
            equal(ident,'§12.4 validator','accept',validate(got,linked=NORMALISATION_LINK))
            generated={'body':got,'line':'generated-'+ident}
            self.verify(generated,major)

    def unsupported(self, capability, command_text, bead=CLI_BEAD):
        raise Unavailable(capability, command_text, bead)

    def run(self):
        self.check('header', 'markers-c/markers-ir', '§3', self.header)
        self.check('seeds','native-seed-vectors','§21.4',lambda:seed_check(self))
        from dialect_meta import xrefs,coverage,check_asm
        self.check('asm','asm-0.2','§15',lambda:check_asm(self))
        for line,doc,ref,ok in xrefs(self.spec):
            self.check('xrefs',f'line-{line}/{doc}-§{ref}','§1.5',lambda ok=ok:equal('xref','§1.5',True,ok))
        from dialect_driver import SCENARIOS, check_scenario
        for name in SCENARIOS.values():
            # Coverage executes its witnesses even in a coverage-only gate.
            if not self.selected or self.selected & {"state","coverage"}:
                self.check("state" if not self.selected or "state" in self.selected else "coverage",
                           name,"§19/§20",lambda n=name:check_scenario(self,self.block("state",n)))
        covered,evidence=coverage(self)
        for rule,ok in covered.items():
            self.check('coverage',rule,'P-1',lambda r=rule,ok=ok:equal(r,'P-1 example coverage (b-dialect-spec-gvr)',True,ok))

        for b in self.blocks:
            a = b['attrs']
            ident = next((a[t] for t in TAGS if t in a), f"line-{b['line']}")
            if b['lang'] in ('llvm','isa') and not a:
                self.check('inventory', ident, '§1.5', lambda:self.unsupported('untagged normative block', 'add a tag in spec', 'b-dialect-spec-gvr'))
            if b['lang'] == 'llvm':
                for major in d.MAJORS:
                    self.check('parse', f'{ident}/llvm{major}', '§1.5', lambda b=b,k=major:self.verify(b,k))
            if b['lang'] == 'llvm' and 'example' in a:
                self.check('recognise', ident, '§3–§10', lambda b=b:self.recognition(b))
            if 'normalise-in' in a:
                self.check('normalise',ident,'§12',lambda b=b:self.normalisation(b))
            if 'budget-table' in a:
                from dialect_meta import budget_table
                self.check('driver',ident,'§9.2',lambda b=b:budget_table(self,b))
            if 'blocker' in a:
                self.check('blocker',ident,'§25.1',lambda b=b:self.blocker(b))
            if 'native' in a:
                from dialect_native import check as check_native
                self.check('native',ident,'§1.5 native',lambda b=b:check_native(self,b))
            if b['lang'] in ('c','rust','julia') and 'example' in a:
                from dialect_native import frontend
                for major in d.MAJORS:
                    self.check('frontend',str(ident)+'/llvm'+major,'§1.5 frontend',lambda b=b,k=major:frontend(self,b,k))
            if 'lift' in a:
                from dialect_map import map_object
                self.check('map',ident,'§16',lambda b=b:map_object(self,b))
            if a.get('object')=='arena-o1':
                from dialect_map import map_arena
                self.check('map',ident,'§16.4',lambda:map_arena(self))
            if 'object' in a:
                self.check('check', ident, 'ISA §9.2', lambda i=ident:self.isa.call('check',self.object_file(i)))
            if 'hash' in a: self.check('hash',ident,'ISA §9.2',lambda b=b:self.hashes(b))
            if 'run' in a: self.check('run-oracle',ident,'ISA §14.1',lambda b=b:self.oracle_run(b))
            if 'step-check' in a: self.check('step-check',ident,'ISA §14.2',lambda b=b:self.oracle_run(b,True))
            if 'cc-run' in a:
                for verb in ('run-cc','reverse') if 'reverse:' in b['body'] else ('run-cc',):
                    from dialect_cc import check as check_cc
                    self.check('cc-run',f'{ident}/{verb}','§18.6',lambda v=verb,b=b:check_cc(self,b,v))
                from dialect_cc import check as check_cc
                self.check('run-program',ident,'§10 launch',lambda b=b:check_cc(self,b,'run-program'))
            if 'semantics' in a:
                self.check('trace',ident,'§18.4 ABI 0.2',lambda b=b:trace_check(self,b))
            if 'events' in a:
                self.check('events',ident,'§18.4',lambda b=b:events_check(self,b))
            if 'state' in a and a['state'] not in SCENARIOS.values():
                family='blocker' if a.get('verdict','').startswith('blocked:') else 'state'
                self.check(family,ident,'§18.4',lambda b=b:state_check(self,b))
            if 'tdl' in a:
                from dialect_tdl import check_tdl
                self.check('tdl', ident, '§10/§18', lambda b=b:check_tdl(self,b))
        # Each family is registered before implementation; no tag can disappear silently.
        supported = {'markers-ir','markers-c','example','object','hash','run','step-check','cc-run','tdl','state','normalise-in','normalise-out','native','lift','linkmap','semantics','events','budget-table','blocker'}
        for b in self.blocks:
            for tag in TAGS:
                if tag in b['attrs'] and tag not in supported:
                    ident = b['attrs'][tag]
                    self.check(TAG_FAMILY[tag], ident, 'P-2', lambda t=tag:self.unsupported(t,'python3 scripts/dialect_check.py --family '+TAG_FAMILY[t], 'b-dialect-spec-qxd'))
        return self.rows


def main(argv=None):
    parser = argparse.ArgumentParser(description='Dialect 0.2 pre-flight (all failures are fatal).')
    parser.add_argument('spec', nargs='?', type=Path, default=d.SPEC)
    parser.add_argument('--family', action='append', help='family to execute; repeat or comma-separate')
    parser.add_argument('--list', action='store_true', help='list all examples and their checked status')
    parser.add_argument('--json', type=Path, help='write structured results')
    args = parser.parse_args(argv)
    selected = {x for f in args.family or [] for x in f.split(',')}
    known = set(TAG_FAMILY.values()) | {'parse','frontend','coverage','xrefs','asm','inventory','seeds'}
    if selected - known:
        parser.error('unknown family: ' + ', '.join(sorted(selected-known)))
    headless_env()
    text = args.spec.read_text(); blocks = d.extract_blocks(text)
    initialise(blocks)
    d.SPEC_PATH = args.spec
    tmp = SCRATCH / (time.strftime('run-%Y%m%dT%H%M%S-') + str(os.getpid()))
    tmp.mkdir()
    r = Runner(blocks, text, tmp, selected)
    rows = r.run()
    if args.list:
        for row in rows:
            print(f"{row['example']}\t{row['family']}\t{row['status']}\t{row.get('detail','')}")
    print('\nfamily          examples passed failed blocked-on')
    for family in sorted({r['family'] for r in rows}):
        rs = [r for r in rows if r['family']==family]
        passed = sum(r['status']=='passed' for r in rs)
        blockers = sorted({r['blocked_on'] for r in rs if r['blocked_on']})
        print(f'{family:16} {len(rs):8} {passed:6} {len(rs)-passed:6} ' + '; '.join(blockers))
    if args.json:
        args.json.write_text(json.dumps(rows, indent=2)+'\n')
    failures = sum(r['status']!='passed' for r in rows)
    print(f'\n{"FAIL" if failures else "OK"}: {len(rows)-failures}/{len(rows)} checks passed; {failures} failed or blocked')
    return 1 if failures else 0


def verify_inplace02(a):
    """§8.7 exhaustive inverse verification by the Rust executor, never run_ref."""
    if not a.inplace_pairs:return
    isa=Interpreter()
    for f,ins,c,fields in a.inplace_pairs:
        for g,gi in itertools.product(a.cands[id(ins),0],a.cands[id(ins),1]):
            fn=a.m.funcs[g];width=fn.params[0][0][1]
            if width>24:raise Unavailable('§8.7 sampled inverse evidence', 'bennett-isa-ref run-oracle <inplace-pair> ref --input <samples>', 'b-dialect-spec-qxd')
            args=fields[1:]
            for values in itertools.product(*args):
                bodies=[];signatures=[]
                for idx,name in enumerate((g,gi),1):
                    gf=a.m.funcs[name]
                    src=d.extract_function(a.m,name)
                    for (_,_,param),value in zip(gf.params[1:],values):
                        src=re.sub(re.escape(param)+r'(?![-\w.$])',str(value),src)
                    # Remove the specialised formal parameters after replacing uses.
                    first=src.splitlines()[0]
                    src=src.replace(first,re.sub(r'\(.*\)', '('+d.tstr(gf.params[0][0])+' '+gf.params[0][2]+')',first),1)
                    body,_,_=d.lift(src)
                    body=re.sub(r'^oracle @ref .*$',f'lproc @L{idx} (p0:reg[{width}]) (r:reg[{width}]) () () ()',body,flags=re.M)
                    body=body.replace('lift.retval ','lift.ret ')
                    bodies.append(body)
                    signatures.append({'abi':'0.8','kind':'lproc','tier':'q','params':[width],'result':width})
                sig={'abi':'0.8','kind':'oracle','tier':'q','in':[width],'tgt':width,'fault':4,'args':[],'mem':[]}
                symbols={'0':{'name':'ref','kind':'oracle','signature':sig,'interface_hash':'0'*64}}
                for idx,s in enumerate(signatures,1):symbols[str(idx)]={'name':'L'+str(idx),'kind':'lproc','signature':s,'interface_hash':'0'*64}
                body=f'oracle @ref (x:wire[{width}] in) (tgt:wire[{width}]) (fault:wire[4]) () ()\nregs {{ y:reg[{width}], z:reg[{width}] }}\n^entry():\ny = lift.call @L1 (x)\nz = lift.call @L2 (y)\nlift.retval z\n'+'\n'.join(bodies)
                obj='bennett-object isa=0.8 object=0.8 launch=0.8 sched=0.8 cert=0.8 coverage=0.8 target=0.8 ptr_width=64\n\nsection symbols\n'+json.dumps(symbols,sort_keys=True,separators=(',',':'))+'\n\nsection functions\n'+body+'\n\nsection layout\n'+json.dumps({'A_tab':0,'H':12,'S_cells':16,'globals':{},'heap_base':4096,'heap_limit_max':0,'interface_regions':{'ref':{}},'null_size':4096,'ptr_width':64},sort_keys=True,separators=(',',':'))+'\n'
                with tempfile.TemporaryDirectory(dir=SCRATCH,prefix='inplace-') as tmp:
                    path=Path(tmp)/'pair.bisa';path.write_text(obj)
                    hashes=isa.call('hash',path)
                    for s in symbols.values():s['interface_hash']=hashes['symbols'][s['name']]['interface_hash']
                    obj=obj.replace(obj.split('section symbols\n',1)[1].split('\n',1)[0],json.dumps(symbols,sort_keys=True,separators=(',',':')))
                    path.write_text(obj)
                    for x in range(1<<width):
                        got=isa.call('run-oracle',path,'ref','--input',str(x),'--budget','1000000,0,65536,256')
                        if got['code'] or int(got['payload'])!=x:
                            raise d.Reject('BD-E-INPLACE-NOT-INVERSE',f'§8.7 {g}/{gi} ARG={values} x={x}: expected payload={x}, code=0; actual={got}')

from dialect_normalise import normalise


def build_trace(body, ident, major, tc, tmp):
    directory=Path(tmp)/('trace-'+ident+'-'+major);directory.mkdir(exist_ok=True)
    ll=directory/'case.ll';ll.write_text(d.with_decls(body));obj=directory/'case.o';exe=directory/'case'
    command([tc[major]/'llc','-O0','-relocation-model=pic','-filetype=obj',ll,'-o',obj])
    command(['cc','-std=c11','-O0','-DBENNETT_MARKERS_ABI=2','-no-pie','-rdynamic',
             obj,d.LEG/'runtime'/'trace_rt.c',d.LEG/'runtime'/'driver.c','-ldl','-o',exe])
    traces={}
    inputs=re.search(r'^; INPUTS: (\d+)\.\.(\d+)',body,re.M)
    if not inputs:raise d.Fail('§18 trace: missing input domain')
    for x in range(int(inputs[1]),int(inputs[2])+1):
        output=command([exe,x]);(directory/f'{x}.trace').write_text(output)
        if 'BADHANDLE' in output or 'FAULT ' in output:raise d.Fail('§18 invalid trace: '+output)
        traces[x]=output.strip().splitlines()
    return traces


def trace_check(runner,block):
    a=block['attrs'];ident=a['semantics'];corpus=d.LEG/'cases'/(a['corpus']+'.ll')
    equal(ident,'§1.5 corpus bytes',corpus.read_text(),block['body'])
    verdict,_=recognise(block['body']);equal(ident,'§1.6','accept',verdict)
    results={}
    for major in d.MAJORS:
        results[major]=build_trace(block['body'],ident,major,runner.tc,runner.tmp)
    return results


def events_check(runner,block):
    a=block['attrs'];ident=a['events'];inp=int(a['input']);sem=runner.block('semantics',ident)
    traces=runner.trace_cache.get(ident)
    if traces is None:traces=trace_check(runner,sem);runner.trace_cache[ident]=traces
    for major,inputs in traces.items():
        events=[d.event_str(e) for e in d.trace_to_events(inputs[inp])]
        equal(ident+'/llvm'+major,'§18.4 events',d.collapse(block['body']),events)


def action_object(isa,path,name,widths,rows):
    sig={'abi':'0.8','args':[],'bounds':[],'in':[],'kind':'action','mem':[],'mut':widths,'tier':'q'}
    symbols={'0':{'interface_hash':'0'*64,'kind':'action','name':name,'signature':sig}}
    header='action @'+name+' ('+', '.join(f'q{k}:wire[{w}] mut' for k,w in enumerate(widths))+') () () () ()'
    prefix='bennett-object isa=0.8 object=0.8 launch=0.8 sched=0.8 cert=0.8 coverage=0.8 target=0.8 ptr_width=64\n\nsection symbols\n'
    tail='\n\nsection functions\n'+header+'\n^entry():\n'+'\n'.join(rows)+'\n'
    path.write_text(prefix+json.dumps(symbols,sort_keys=True,separators=(',',':'))+tail)
    hs=isa.call('hash',path);symbols['0']['interface_hash']=hs['symbols'][name]['interface_hash']
    path.write_text(prefix+json.dumps(symbols,sort_keys=True,separators=(',',':'))+tail)
    isa.call('check',path)


def state_check(runner,block):
    a=block['attrs'];ident=a['state'];at=int(a['at'])
    from dialect_driver import SCENARIOS, check_scenario
    if ident in SCENARIOS.values():return check_scenario(runner,block)
    from dialect_state import NATIVE_STATES, check_native_state
    if ident in NATIVE_STATES:return check_native_state(runner,block)
    from dialect_tdl import ORIGINAL, compare_original
    if ident in ORIGINAL:return compare_original(runner,block)
    from dialect_tdl import BOUNDARIES, check_boundary
    if ident in BOUNDARIES:return check_boundary(runner,block)
    from dialect_tdl import WRAPPERS, check_wrapper
    if ident in WRAPPERS:return check_wrapper(runner,block)
    if ident=='r-budget-prefix':
        from dialect_cc import r_budget_prefix
        return r_budget_prefix(runner,block)
    if 'input' not in a:
        raise Unavailable('TDL state execution',f'bennett-isa-ref run-action {runner.tmp / (ident+".bisa")} {ident} --mut <TDL-registers> --mem <coherent-arena>',CLI_BEAD)
    eb=runner.block('events',ident);lines=d.collapse(eb['body'])[:at];widths=[];rows=[]
    wire=lambda w:'q'+w[1:].replace('.', '[')+']'
    for line in lines:
        fields=line.split()
        if fields[0]=='qalloc':widths.append(int(fields[2]));continue
        if fields[0]=='qfree':raise d.Fail('state checkpoint after release needs live-register projection')
        operands,_,ctrl=line.partition(' ctrl ')
        tokens=operands.split();row=tokens[0]+' '+' '.join(wire(w) for w in tokens[1:])
        if ctrl and tokens[0]=='x' and ',' not in ctrl:
            row='cx '+wire(ctrl)+' '+wire(tokens[1])
        else:
            for w in reversed(ctrl.split(',')) if ctrl else []:row='ctl '+wire(w)+' '+row
        rows.append(row)
    path=runner.tmp/(ident+'-at'+str(at)+'.bisa');action_object(runner.isa,path,'checkpoint',widths,rows)
    got=runner.isa.call('run-action',path,'checkpoint','--mut',','.join('0' for _ in widths))
    want={}
    for line in block['body'].strip().splitlines():
        m=re.fullmatch(r'\|([01]+)> (\S+)',line);want[m[1]]=d.parse_amp(m[2])
    if 'state' not in got:raise d.Fail('run-action: expected JSON state vector; actual='+repr(got))
    observed={k:complex(*v) if isinstance(v,list) else complex(v) for k,v in got['state'].items()}
    for key in set(want)|set(observed):
        if abs(want.get(key,0)-observed.get(key,0))>1e-7:raise Mismatch(f'{ident} [§18.4 state] expected={want}; actual={observed}')


def seed_check(runner):
    seed=d.ROOT/'spec'/'seeds'
    for major in ('18','23'):
        exe=runner.tmp/('seed-test-'+major)
        sources=sorted((seed/'musl'/'src'/'math').glob('*.c'))
        command([runner.frontends[major]/'clang','-O2','-ffp-contract=off','-fno-builtin','-Dhidden=',
                 '-I',seed/'musl-compat','-I',seed/'musl'/'src'/'internal','-I',seed/'musl'/'arch'/'generic',
                 ROOT/'scripts'/'test_seeds.c',seed/'softfloat.c',*sources,'-o',exe])
        equal('seeds/clang'+major,'§13 seed vectors',
              '100000 binary64 add/mul vectors and musl exp/log anchors passed',command([exe]).strip())
        for name in ('runtime','contexts','devices','coherence'):
            command([runner.frontends[major]/'clang','-std=c11','-Wall','-Wextra','-Werror','-c',seed/(name+'.c'),'-o',runner.tmp/(name+'-'+major+'.o')])


if __name__ == "__main__":
    sys.exit(main())
