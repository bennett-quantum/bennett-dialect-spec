"""0.2.14 contract and finite witnesses (brt-vbi §§12.8/19.1/19.9; R23 §11.2).

The vectors are wire-format and expected-value evidence for the runtime integer
instance-delivery protocol, not a runtimes generator or helper implementation.
Python canonicalises the request and computes expected limbs (P-3); coreutils
sha256sum and LLVM 18/23 native `_BitInt(257)` builds are the independent executors.
"""
import hashlib
import itertools
import json
from pathlib import Path
import re

import dialect_check as d
from dialect_check_v02 import command, equal

STATES = {'runtime-instance-request', 'runtime-instance-i257'}
HERE = Path(__file__).resolve().parent
SOURCE = HERE / '0214_runtime_instances.c'
CONSOLE_SENTENCE = ('Editorial clarification (advisor R23 2026-11-03, b-dialect-spec-9rd), resolving an ambiguity toward native'
                    ' semantics: closing a virtual stdout/stderr descriptor has native descriptor semantics, so a later `write`,'
                    ' `writev` or `lseek` on that descriptor returns -1 with EBADF; "the virtual byte sink" names the console'
                    ' device, which stays available to other descriptors bound to it, and "releases no host resource" means no'
                    ' host-side close.')
# §12.8 op set of the delivery protocol, with its minimum request width (exclusive).
WIDE = ('mul', 'udiv', 'sdiv', 'urem', 'srem', 'shl', 'lshr', 'ashr')
ROWS = ('bswap', 'bitreverse', 'ctpop', 'ctlz', 'cttz', 'fshl', 'fshr', 'sshl_sat', 'ushl_sat',
        'smul_fix', 'umul_fix', 'smul_fix_sat', 'umul_fix_sat', 'sdiv_fix', 'udiv_fix',
        'sdiv_fix_sat', 'udiv_fix_sat', 'pdep', 'pext', 'clmul')
OVERFLOW = ('smul_with_overflow', 'umul_with_overflow')
REQUEST_KEYS = {'schema', 'llvm_major', 'target_triple', 'data_layout', 'entries'}


def section_text(text, number):
    heading = re.search(r'^#{2,3} ' + re.escape(number) + r'\.? .*$', text, re.M)
    if not heading:
        raise d.Fail('0214: missing section ' + number)
    end = re.search(r'^#{2,3} ', text[heading.end():], re.M)
    return text[heading.end():heading.end() + end.start()] if end else text[heading.end():]


def check_contract(text):
    version = re.search(r'^# Bennett LLVM Dialect — Specification, (?:draft )?([0-9.]+)$', text, re.M)
    if not version:
        raise d.Fail('0214: missing full dialect version')
    version = version[1]
    equal('0214', 'supported publication track', True, version in ('0.2.14', '0.3'))
    equal('0214', 'compatibility unit', True, f'**full version string** (`{version}`)' in text)
    items = json.loads((HERE / 'dialect_0214_items.json').read_text())
    for item in items:
        equal(item['id'], 'accepted wording in §' + item['section'], True,
              item['sentence'] in section_text(text, item['section']))
    ops = section_text(text, '12.8')
    for op in WIDE + ROWS + OVERFLOW:
        equal('0214', 'published op ' + op, True, '`' + op + '`' in ops)
    equal('0214', 'separate map identity', True,
          ('map 0.2.9' if version.startswith('0.2.') else 'map 0.3') in text)
    return {'full_version': version, 'items': len(items),
            'claim': 'publication and accepted wording integrity'}


def no_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise d.Fail('0214 request: duplicate JSON member')
    return dict(pairs)


def integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def validate(request):
    """The §12.8 REQUEST shape; violations fail loud."""
    equal('0214 request', 'exact members', REQUEST_KEYS, set(request))
    equal('0214 request', 'schema', 'bennett-runtimes-instantiations-1', request['schema'])
    equal('0214 request', 'integer llvm_major', True, integer(request['llvm_major']))
    for key in ('target_triple', 'data_layout'):
        equal('0214 request', key + ' string', True, isinstance(request[key], str))
    for entry in request['entries']:
        equal('0214 request', 'entry members', {'op', 'width'}, set(entry))
        equal('0214 request', 'integer width', True, integer(entry['width']))
        op, width = entry['op'], entry['width']
        equal('0214 request', 'known op', True, op in WIDE + ROWS + OVERFLOW)
        minimum = 128 if op in WIDE else 64 if op in OVERFLOW else 0
        equal('0214 request', op + ' width bound', True, width > minimum)


def canonical(request):
    validate(request)
    unique = sorted({(e['op'], e['width']) for e in request['entries']},
                    key=lambda e: (e[0].encode(), e[1]))
    body = dict(request, entries=[{'op': op, 'width': width} for op, width in unique])
    # JCS: these members are ASCII strings and integers, so sorted compact JSON is exact.
    return json.dumps(body, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def request_vector(runner, block):
    body = block['body']
    equal('runtime-instance-request', 'one line, no trailing LF in the bytes', True,
          body.endswith('\n') and '\n' not in body[:-1] and not body[:-1].endswith((' ', '\t')))
    raw = body[:-1].encode()
    request = json.loads(raw, object_pairs_hook=no_duplicate_keys)
    equal('runtime-instance-request', 'canonical bytes', raw, canonical(request))
    entries = request['entries']
    variants = 0
    for extra in ([], entries[:1], entries[1:], entries + entries):
        for order in itertools.permutations(entries + extra):
            equal('runtime-instance-request', 'duplicate/reordered entries canonicalise identically',
                  raw, canonical(dict(request, entries=list(order))))
            variants += 1
    digest = hashlib.sha256(raw).hexdigest()
    path = runner.tmp / '0214-request.json'
    path.write_bytes(raw)
    native = command(['sha256sum', path]).split()[0]
    equal('runtime-instance-request', 'independent SHA-256', digest, native)
    result = json.loads(runner.block('state', 'runtime-instance-i257')['body'])
    equal('runtime-instance-request', 'published request_sha256', result['request_sha256'], native)
    return {'claim': 'canonical request wire-format example; not a helper implementation or generator result',
            'request_sha256': native, 'variants': variants}


def limbs(value, width=257):
    return [(value >> (64 * k)) & ((1 << min(64, width - 64 * k)) - 1) for k in range((width + 63) // 64)]


def i257_vector(runner, block):
    data = json.loads(block['body'], object_pairs_hook=no_duplicate_keys)
    equal('runtime-instance-i257', 'tagged source identity', data['source_sha256'],
          hashlib.sha256(SOURCE.read_bytes()).hexdigest())
    a, b, mask = 2**256 + 3, 2, 2**257 - 1
    product = (a * b) & mask
    expected = {'a': limbs(a), 'b': limbs(b), 'product': limbs(product),
                'ctpop_product': limbs(product.bit_count()), 'ctpop_a': limbs(a.bit_count())}
    equal('runtime-instance-i257', 'limb widths', [64, 64, 64, 64, 1], [min(64, 257 - 64 * k) for k in range(5)])
    for key, value in expected.items():
        equal('runtime-instance-i257', 'published ' + key, value, data[key])
    lines = [[key] + expected[key] for key in ('a', 'product', 'ctpop_product', 'ctpop_a')]
    for major in ('18', '23'):
        exe = runner.tmp / ('0214_runtime_instances-' + major)
        command([runner.frontends[major] / 'clang', '-std=c2x', '-Wall', '-Wextra', '-Werror', '-O2',
                 SOURCE, '-o', exe])
        equal('runtime-instance-i257/' + major, 'independent native fixture', lines,
              [json.loads(line) for line in command([exe]).splitlines()])
    return {'claim': 'i257 expected-value fixture; not a helper implementation or delivery evidence',
            'source_sha256': data['source_sha256']}


def check_state(runner, block):
    if block['attrs']['state'] == 'runtime-instance-request':
        return request_vector(runner, block)
    if block['attrs']['state'] == 'runtime-instance-i257':
        return i257_vector(runner, block)
    raise d.Fail('unknown 0.2.14 state witness: ' + block['attrs']['state'])


def check_all(runner):
    runner.check('coverage', '0214/publication', '§§11.2/12.8/19.1/19.9/23',
                 lambda: check_contract(runner.spec))
