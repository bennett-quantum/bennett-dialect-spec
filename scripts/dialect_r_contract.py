"""Finite R-profile contract vectors; execution comes from the pinned ISA reader.

Clause checks establish retention only. Native printf is an independent byte
oracle; the hand-written ISA fixtures do not claim plugin/musl integration.
"""
import json
import re
import subprocess

import dialect_check as d
import dialect_check_v02 as v2
import dialect_cc as cc
from dialect_profile import ISA08, using_profile

CASES = d.ROOT / 'corpus' / 'legality' / 'r-contract'


def clauses(runner, case):
    for section, sentence in case['requires']:
        heading = re.search(r'^###? ' + re.escape(section) + r'\.? ', runner.spec, re.M)
        if heading is None:
            raise d.Fail('missing R-contract section ' + section)
        end = re.search(r'^###? ', runner.spec[heading.end():], re.M)
        text = runner.spec[heading.end():heading.end() + end.start()] if end else runner.spec[heading.end():]
        v2.equal(case['id'], 'clause in §' + section, True, sentence in text)


def object_file(runner, case, suffix='', functions=None):
    path = runner.tmp / (case['id'] + suffix + '.bisa')
    cc.emit(runner, path, functions if functions is not None else case['functions'],
            case['signatures'], {k: bytes.fromhex(v) for k, v in case.get('data', {}).items()},
            case.get('devices'))
    return path


def observations(case, got, expected):
    for key, value in expected.items():
        v2.equal(case['id'], key, value, got[key])


def faults(runner, case):
    path = object_file(runner, case)
    for code in case['codes']:
        path = object_file(runner, case, '-' + str(code),
                           [body.replace('fault 2', 'fault ' + str(code)) for body in case['functions']])
        got = runner.isa.call('run-cc', path, 'main')
        observations(case, got, dict(case['expected'], fault=code if code else 4))
        v2.equal(case['id'], 'one terminal record', 1, len(got['faults']))
        reset = runner.isa.call('reverse', path, 'main')
        observations(case, reset, case['reset'])
    # A generic trap is a distinguishable, incorrect lowering of fault 2.
    path = object_file(runner, case, '-trap', [body.replace('fault 2', 'trap') for body in case['functions']])
    got = runner.isa.call('run-cc', path, 'main')
    v2.equal(case['id'], 'trap has only code 4', 4, got['fault'])
    v2.equal(case['id'], 'trap cannot implement fault 2', False, got['fault'] == 2)


def identity(runner, case):
    current = object_file(runner, case)
    new_hash = runner.isa.call('hash', current)['symbols']['main']['interface_hash']
    with using_profile(ISA08):
        legacy_case = dict(case, signatures={'main': cc.signature([], [])})
        legacy = object_file(runner, legacy_case, '-legacy')
    old_hash = runner.isa.call('hash', legacy)['symbols']['main']['interface_hash']
    v2.equal(case['id'], 'ISA version changes semantic envelope hash', False, old_hash == new_hash)
    # Put the old claimed hash on real 0.9 bytes. A version-label rewrite is insufficient.
    stale = runner.tmp / 'stale-identity.bisa'
    stale.write_text(current.read_text().replace(new_hash, old_hash))
    reject(runner, stale, 'check', [], 'interface hash')
    # A mismatched ABI is also rejected, independently of the claimed hash.
    stale.write_text(current.read_text().replace('"abi":"0.9"', '"abi":"0.8"'))
    reject(runner, stale, 'check', [], 'abi')


def reject(runner, path, verb, options, diagnostic):
    runner.isa.build()
    result = subprocess.run([runner.isa.exe, verb, path, *options], capture_output=True,
                            text=True, env=v2.headless_env(), timeout=30)
    v2.equal(path.name, 'diagnostic exit', 1, result.returncode)
    v2.equal(path.name, 'no success JSON', '', result.stdout)
    if diagnostic.lower() not in result.stderr.lower():
        raise d.Fail(path.name + ': expected diagnostic ' + diagnostic + '; actual ' + result.stderr)


def console(runner, case):
    source = CASES / case['native']
    for major in ('18', '23'):
        exe = runner.tmp / ('console-native-' + major)
        v2.command([runner.frontends[major] / 'clang', '-O2', '-fno-builtin', source, '-o', exe])
        result = subprocess.run([exe], capture_output=True, env=v2.headless_env(), timeout=10)
        v2.equal(case['id'], 'native status LLVM ' + major, 0, result.returncode)
        v2.equal(case['id'], 'native formatted bytes LLVM ' + major, case['expected']['console_hex'], result.stdout.hex())
        v2.equal(case['id'], 'native stderr LLVM ' + major, b'', result.stderr)
    path = object_file(runner, case)
    observations(case, runner.isa.call('run-cc', path, 'main'), case['expected'])
    observations(case, runner.isa.call('reverse', path, 'main'), case['reset'])
    bad = object_file(runner, case, '-bad-range', [body.replace('const.i64 4096', 'const.i64 0') for body in case['functions']])
    observations(case, runner.isa.call('run-cc', bad, 'main'), case['invalid_range'])


def tape(runner, case):
    path = object_file(runner, case)
    saved = runner.tmp / (case['id'] + '.json')
    forward = runner.isa.call('run-cc', path, 'main', '--tape-out', saved)
    observations(case, forward, case['expected'])
    journal = json.loads(saved.read_text())
    v2.equal(case['id'], 'saved journal schema and hand-derived bytes', case['journal'], journal)
    for verb in ('run-cc', 'reverse'):
        plain = runner.isa.call(verb, path, 'main')
        replay = runner.isa.call(verb, path, 'main', '--replay-tape', saved)
        v2.equal(case['id'], verb + ' replay exact report', plain, replay)
    for mutation in case['corruptions']:
        entries = json.loads(saved.read_text())
        if mutation == 'missing':
            entries.pop()
        elif mutation == 'trailing':
            entries.append(entries[0])
        else:
            entries[0][mutation] = case['corruptions'][mutation]
        corrupt = runner.tmp / ('corrupt-' + mutation + '.json')
        corrupt.write_text(json.dumps(entries))
        out = runner.tmp / ('rejected-' + mutation + '.json')
        reject(runner, path, 'run-cc', ['main', '--replay-tape', str(corrupt), '--tape-out', str(out)], 'replay mismatch')
        v2.equal(case['id'], 'corrupt replay writes no tape', False, out.exists())
    malformed = runner.tmp / 'malformed-tape.json'
    malformed.write_text('[{"dev":"console","dev":"console","op":"write","args":[4096,1],"bytes":"78"}]')
    reject(runner, path, 'run-cc', ['main', '--replay-tape', str(malformed)], 'duplicate')


CHECKS = {'faults': faults, 'identity': identity, 'console': console, 'tape': tape}


def check_case(runner, case):
    clauses(runner, case)
    CHECKS[case['kind']](runner, case)
    return {'claim': 'clause retention and finite independent native/ISA boundary vectors; not whole-program producer conformance',
            'case': case['id']}


def check_all(runner):
    if runner.selected and 'r-contract' not in runner.selected:
        return
    paths = sorted(CASES.glob('*.json'))
    v2.equal('r-contract', 'four registered case groups', 4, len(paths))
    for path in paths:
        case = json.loads(path.read_text())
        runner.check('r-contract', case['id'], case['rule'], lambda case=case: check_case(runner, case))
