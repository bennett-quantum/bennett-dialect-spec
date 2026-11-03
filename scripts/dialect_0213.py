"""0.2.13 contract and finite witnesses; no production allocator/arith claim.

Python establishes exact expected values. Native integer fixtures and the Rust
ISA executor independently execute the selector and ordinary-memory witnesses.
"""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

import dialect_check as d
from dialect_check_v02 import command, equal

STATES = {'ppc-zero-low-parity', 'allocator-bookkeeping'}
HERE = Path(__file__).resolve().parent


def check_contract(text):
    version = re.search(r'^# Bennett LLVM Dialect — Specification, (?:draft )?([0-9.]+)$', text, re.M)
    if not version:
        raise d.Fail('0213: missing full dialect version')
    version = version[1]
    equal('0213', 'supported publication track', True, version in ('0.2.13', '0.2.14', '0.3'))
    equal('0213', 'compatibility unit', True,
          f'**full version string** (`{version}`)' in text)
    items = json.loads((HERE / 'dialect_0213_items.json').read_text())
    for item in items:
        start = text.index('### '+item['section']+' ')
        start = text.index('\n', start)+1
        end = re.search(r'^#{2,3} ', text[start:], re.M)
        section = text[start:start+end.start()] if end else text[start:]
        equal(item['id'], 'accepted wording in §'+item['section'], True,
              item['sentence'] in section)
    equal('0213', 'separate map identity', True,
          ('map 0.2.9' if version.startswith('0.2.') else 'map 0.3') in text)
    return {'full_version': version, 'items': len(items),
            'claim': 'publication and accepted wording integrity'}


def binary64(bits):
    sign = -1 if bits >> 63 else 1
    exponent = (bits >> 52) & 2047
    significand = bits & ((1 << 52)-1)
    if exponent == 2047:
        raise d.Fail('finite binary64 witness required')
    if exponent:
        significand |= 1 << 52
    return sign * significand * Fraction(2) ** (exponent-1075 if exponent else -1074)


def fixture(runner, block, filename, expected):
    data = json.loads(block['body'])
    source = HERE / filename
    equal(filename, 'tagged source identity', data['source_sha256'],
          hashlib.sha256(source.read_bytes()).hexdigest())
    for major in ('18', '23'):
        exe = runner.tmp / (filename+'-'+major)
        command([runner.frontends[major]/'clang', '-std=c11', '-Wall', '-Wextra',
                 '-Werror', '-O2', source, '-o', exe])
        equal(filename+'/'+major, 'independent native fixture', expected,
              [json.loads(line) for line in command([exe]).splitlines()])
    return data


def numerical(runner, block):
    u = Fraction(2) ** -1074
    h, H = (binary64(bits) for bits in (0x3ff0000000000001, 0x0030000000000001))
    # Integer significands decoded independently of the selector fixture.
    equal('PPC FMA', 'exact midpoint', h+u/2, (h+u)/2+h/2)
    bits = 0x3c030000000000001200000000000000
    v = ((1 << 112)+(bits & ((1 << 112)-1))) * Fraction(2) ** (((bits >> 112)&32767)-16383-112)
    equal('PPC conversion', 'binary128 exact midpoint', H+u/2, v)
    expected = []
    for high in (0x3ff0000000000001, 0x0030000000000001,
                 0x3ff0000000000000, 0x0030000000000000):
        value = binary64(high)
        # Both neighbours are canonical: u is strictly below half a high ulp.
        equal('PPC', 'canonical high unchanged', True,
              u < (binary64(high+1)-value)/2)
        # Every finite binary64 sum is a multiple of u; these differ by u,
        # so no finite canonical sum can lie between them.
        equal('PPC', 'adjacent sums on the minimum binary64 grid', 1,
              (value+u-value)/u)
        for neg in (0, 1):
            for mode in range(5):
                far = mode == 4 or (mode == 1 and neg) or (mode == 2 and not neg)
                for sticky in (0, 32):
                    for observed in (0, 1):
                        expected.append([f'{high | (neg << 63):016x}',
                                         f'{((neg << 63) | 1) if far else 0:016x}',
                                         sticky | (16 if observed else 0)])
    expected += [['0000000000000000', '0000000000000000', 24],
                 ['0000000000000002', '0000000000000000', 24],
                 ['3ff0000000000001', '0000000000000001', 0],
                 ['3ff0000000000001', '0000000000000002', 0],
                 ['bff0000000000001', '8000000000000002', 0]]
    data = fixture(runner, block, '0213_ppc_policy.c', expected)
    equal('PPC', 'published nearest-even witnesses',
          [['3ff0000000000001', '0000000000000000', 16],
           ['0030000000000001', '0000000000000000', 16]], data['nearest_even'])
    equal('PPC', 'two-zero-low neighbours', [0, 2], data['two_zero_low_high_bits'])
    return {'claim': 'exact midpoint/adjacency and finite selector-policy evidence; not production arithmetic conformance',
            'source_sha256': data['source_sha256'], 'vectors_per_build': len(expected)}


def allocation(runner, block):
    requests = (3, 0, 12, 16, 32)
    expected = []
    limits = (2, 3, 4, 31, 32, 63, 64)
    for limit in limits:
        bump = 0
        records = []
        for n in requests:
            if bump+max(n, 1) > limit:
                break
            records.append([4096+bump, n])
            bump += max(n, 1)
        ok = len(records) == len(requests)
        expected += [[limit, 0 if ok else 2, 4112 if ok else 0, 4096+bump, len(records)], *records]
        if ok:
            expected += [[4112, 1, 1, 0]]
    data = fixture(runner, block, '0213_bookkeeping.c', expected)
    equal('bookkeeping', 'published successful trace',
          [[4096,3], [4099,0], [4100,12], [4112,16], [4128,32]], data['records'])
    equal('bookkeeping', 'published successful state', [4112,4160,5,0], data['heap64'])
    equal('bookkeeping', 'published failure prefix', [0,4128,4,2], data['heap32'])
    from dialect_tdl import object_text
    regs, rows = [], []
    for k, n in enumerate(requests):
        regs += [f'n{k}:reg[64]', f'p{k}:reg[64]']
        rows += [f'n{k} = lift.const.i64 {n}', f'p{k} = lift.alloc n{k}']
    regs += ['ptr:reg[64]', 'off:reg[64]', 'value:reg[64]', 'got:reg[64]',
             'wrong:reg[1]', 'bad:reg[1]', 'result:reg[64]']
    rows += ['bad = lift.const.i1 0']
    # Actual ordinary metadata stores/loads are reversed by the independent ISA
    # step-check, together with the five primitive allocation records.
    for k, value in enumerate((4112, 1, 1, 0)):
        rows += [f'off = lift.const.i64 {k*8}', 'ptr = lift.add p4 off',
                 'lift.boundscheck ptr 8', f'value = lift.const.i64 {value}',
                 'lift.store.i64 ptr value', 'got = lift.load.i64 ptr',
                 'wrong = lift.icmp.ne got value', 'bad = lift.or bad wrong']
    rows += ['result = lift.zext.i64 bad', 'off = lift.const.i64 48',
             'result = lift.shl result off', 'result = lift.or result p3', 'lift.retval result']
    body = ('oracle @ref () (tgt:wire[64]) (fault:wire[4]) () ()\nregs { '+
            ', '.join(regs)+' }\n^entry():\n'+'\n'.join(rows))
    # Use the runner's ISA version so the same fixture runs on both tracks.
    abi = re.search(r'targets ISA (0\.[89])', runner.spec)[1]
    sig = {'abi': abi, 'args': [], 'fault': 4, 'in': [], 'kind': 'oracle',
           'mem': [], 'tgt': 64, 'tier': 'q'}
    layout = {'A_tab': 16, 'H': 13, 'S_cells': 8, 'globals': {},
              'heap_base': 4096, 'heap_limit_max': 64, 'interface_regions': {'ref': {}},
              'null_size': 4096, 'ptr_width': 64}
    obj = object_text(runner.isa, runner.tmp/'0213-bookkeeping.bisa', [body], {'ref': sig}, layout)
    for limit in limits:
        budget = f'1000,{limit},8,8'
        got = runner.isa.call('run-oracle', obj, 'ref', '--input', '', '--budget', budget)
        equal('bookkeeping', 'ordinary metadata result/failure',
              [0,4112] if limit == 64 else [2,0], [int(got['code']),int(got['payload'])])
        reverse = runner.isa.call('step-check', obj, 'ref', '--exhaustive', '--budget', budget)
        equal('bookkeeping', 'metadata and primitive-history reversal', 'ok', reverse['status'])
        replay = runner.isa.call('run-oracle', obj, 'ref', '--input', '', '--budget', budget)
        equal('bookkeeping', 'identical replay', got, replay)
    return {'claim': 'identity-bound finite native/ISA bookkeeping fixture, failure prefixes, metadata reversal and replay; not production runtime conformance',
            'source_sha256': data['source_sha256'], 'isa_identity': runner.isa.call('hash', obj)}


def check_state(runner, block):
    if block['attrs']['state'] == 'ppc-zero-low-parity':
        return numerical(runner, block)
    if block['attrs']['state'] == 'allocator-bookkeeping':
        return allocation(runner, block)
    raise d.Fail('unknown 0.2.13 state witness: '+block['attrs']['state'])


def check_all(runner):
    runner.check('coverage', '0213/publication', '§§13.1/17.1/23',
                 lambda: check_contract(runner.spec))
