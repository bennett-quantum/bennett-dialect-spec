"""Refresh draft hashes while refusing to rewrite independently pinned anchors."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
ANCHORS = ROOT / 'corpus/hash-anchors.json'
FENCES = re.compile(r'^```([^\n]*)\n(.*?)^```[ \t]*$', re.S | re.M)


def load_anchors():
    anchors = json.loads(ANCHORS.read_text())['anchors']
    if not anchors:
        raise ValueError('hash anchor set must not be empty')
    for anchor in anchors:
        digest = hashlib.sha256(anchor['envelope'].encode()).hexdigest()
        if digest != anchor['sha256']:
            raise ValueError(f'anchor transcript digest mismatch: {anchor["object"]}/{anchor["symbol"]}')
    return anchors


def object_blocks(text):
    blocks = {}
    for match in FENCES.finditer(text):
        tag = re.search(r'\bobject=(\S+)', match[1])
        if tag:
            if tag[1] in blocks:
                raise ValueError('duplicate object=' + tag[1])
            blocks[tag[1]] = match[2]
    return blocks


def verify_anchors(text, anchors):
    blocks = object_blocks(text)
    for anchor in anchors:
        ident, name, expected = anchor['object'], anchor['symbol'], anchor['sha256']
        if ident not in blocks:
            raise ValueError(f'missing anchor object={ident}')
        table = json.loads(blocks[ident].split('section symbols\n', 1)[1].splitlines()[0])
        symbols = [s for s in table.values() if s['name'] == name]
        if len(symbols) != 1 or symbols[0]['interface_hash'] != expected:
            raise ValueError(f'input changed anchor {ident}/{name}; expected {expected}')
        for match in FENCES.finditer(text):
            if re.search(r'\bhash=' + re.escape(ident) + r'(?:\s|$)', match[1]):
                pairs = dict(line.split() for line in match[2].strip().splitlines())
                if pairs.get(name) != expected:
                    raise ValueError(f'expected-hash fence changed anchor {ident}/{name}')


def run(exe, verb, path):
    result = subprocess.run([exe, verb, path], capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise ValueError(f'{verb} {path}: {result.stderr.strip()}')
    return json.loads(result.stdout)


def rewrite(spec, exe, scratch, anchors):
    spec, scratch = Path(spec), Path(scratch)
    original = spec.read_text()
    verify_anchors(original, anchors)
    scratch.mkdir(parents=True, exist_ok=True)
    blocks = object_blocks(original)
    hashes = {}

    def observed(ident):
        if ident not in hashes:
            path = scratch / (ident + '.bisa')
            path.write_text(blocks[ident])
            hashes[ident] = run(exe, 'hash', path)['symbols']
        return hashes[ident]

    # Validate every anchor before constructing any replacement. The only spec
    # write happens after every executor result has been checked successfully.
    for anchor in anchors:
        actual = observed(anchor['object'])[anchor['symbol']]['interface_hash']
        if actual != anchor['sha256']:
            raise ValueError(f'refusing to change anchor {anchor["object"]}/{anchor["symbol"]}: '
                             f'expected {anchor["sha256"]}; executor returned {actual}')
    changed = 0
    def replace(match):
        nonlocal changed
        tag = re.search(r'\b(object|hash)=(\S+)', match[1])
        if not tag:
            return match[0]
        kind, ident = tag.groups()
        symbols = observed(ident)
        if kind == 'object':
            lines = match[2].split('\n')
            index = lines.index('section symbols') + 1
            table = json.loads(lines[index])
            for symbol in table.values():
                symbol['interface_hash'] = symbols[symbol['name']]['interface_hash']
            new = json.dumps(table, sort_keys=True, separators=(',', ':'))
            changed += new != lines[index]
            lines[index] = new
            body = '\n'.join(lines)
        else:
            body = '\n'.join(name + ' ' + symbols[name]['interface_hash']
                             for name, _ in (line.split() for line in match[2].strip().splitlines())) + '\n'
        return '```' + match[1] + '\n' + body + '```'

    updated = FENCES.sub(replace, original)
    verify_anchors(updated, anchors)
    spec.write_text(updated)
    return changed


def main(spec, exe, scratch):
    anchors = [a for a in load_anchors() if a['spec'] == Path(spec).name]
    if not anchors:
        raise ValueError('no independently pinned anchors for ' + str(spec))
    print('objects rehashed:', rewrite(spec, exe, scratch, anchors))


if __name__ == '__main__':
    main(*sys.argv[1:])
