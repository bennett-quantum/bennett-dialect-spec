#!/usr/bin/env python3
"""Ratchet tracked Python structure and repository hygiene against docs/quality.md."""
import argparse
import ast
import fnmatch
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
LENGTH_BINS = (25, 50, 100, 200, 300)
LITTER = ('*.pyc', '*.log', '*.darc', 'LAST-RUN*', '*LAST-RUN*', '*PROGRESS*', 'LOCK', '*.lock')
PROCESS_ID = re.compile(r'\b(?:b-(?:dialect-spec|isa-spec)-[a-z0-9]+(?:\.[0-9]+)*|brt-[a-z0-9]{3}(?:\.[0-9]+)*|bennett-[a-z0-9]{3}(?!-))\b')
BEGIN = '<!-- quality-baseline -->'
END = '<!-- /quality-baseline -->'


class CognitiveMass(ast.NodeVisitor):
    """One per branch/loop/handler plus nesting; one per extra boolean operand."""
    def __init__(self):
        self.depth = 0
        self.mass = 0

    def visit_FunctionDef(self, node):
        previous = self.depth
        self.depth = 0
        for statement in node.body:
            self.visit(statement)
        self.depth = previous

    visit_AsyncFunctionDef = visit_FunctionDef

    def branch(self, node):
        self.mass += 1 + self.depth
        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1

    visit_If = branch
    visit_IfExp = branch
    visit_For = branch
    visit_AsyncFor = branch
    visit_While = branch
    visit_ExceptHandler = branch
    visit_comprehension = branch
    visit_Match = branch

    def visit_BoolOp(self, node):
        self.mass += len(node.values) - 1
        self.generic_visit(node)


def is_wrapper(node):
    body = node.body
    if len(body) != 1 or not isinstance(body[0], ast.Return) or not isinstance(body[0].value, ast.Call):
        return False
    call = body[0].value
    params = node.args.posonlyargs + node.args.args
    return (not call.keywords and not node.args.vararg and not node.args.kwarg
            and [arg.id if isinstance(arg, ast.Name) else None for arg in call.args]
            == [arg.arg for arg in params])


def source_metrics(source):
    tree = ast.parse(source)
    functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    lengths = [node.end_lineno - node.lineno + 1 for node in functions]
    cognitive = CognitiveMass()
    cognitive.visit(tree)
    return {'functions': len(functions), 'max_lines': max(lengths, default=0),
            **{f'over_{bound}': sum(length > bound for length in lengths) for bound in LENGTH_BINS},
            'complexity': cognitive.mass, 'wrappers': sum(is_wrapper(node) for node in functions)}


def measure(root=ROOT):
    result = subprocess.run(['git', '-C', str(root), 'ls-files', '-z'],
                            capture_output=True, text=True, check=True)
    files, litter, identifiers = {}, [], []
    for name in sorted(result.stdout.split('\0')):
        if not name or not (root / name).is_file():
            continue
        path = Path(name)
        if '__pycache__' in path.parts or any(fnmatch.fnmatch(path.name, pattern) for pattern in LITTER):
            litter.append(name)
        if path.suffix not in ('.py', '.json', '.c') or path.parts[0] not in ('scripts', 'tools', 'corpus'):
            continue
        if path.parts[0] == 'corpus' and not path.is_relative_to('corpus/legality/harness'):
            continue
        text = (root / name).read_text()
        if path.suffix == '.py':
            files[name] = source_metrics(text)
        if not path.name.startswith('test_'):
            identifiers.extend(f'{name}:{number}:{match[0]}'
                               for number, line in enumerate(text.splitlines(), 1)
                               for match in PROCESS_ID.finditer(line))
    return {'files': files, 'litter': litter, 'identifiers': identifiers}


def totals(files):
    result = {}
    for metrics in files.values():
        for key, value in metrics.items():
            result[key] = max(result.get(key, 0), value) if key == 'max_lines' else result.get(key, 0) + value
    return result


def regressions(baseline, current):
    failures = []
    for key in ('litter', 'identifiers'):
        if len(current[key]) > len(baseline[key]):
            failures.append(f'{key}: {len(baseline[key])} -> {len(current[key])}')
    for name, metrics in {'TOTAL': totals(current['files']), **current['files']}.items():
        previous = totals(baseline['files']) if name == 'TOTAL' else baseline['files'].get(name, {})
        for key, value in metrics.items():
            if value > previous.get(key, 0):
                failures.append(f'{name} {key}: {previous.get(key, 0)} -> {value}')
    return failures


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', action='store_true', help='print a reviewable baseline; never update it implicitly')
    args = parser.parse_args(argv)
    current = measure()
    if args.snapshot:
        print(json.dumps(current, indent=2, sort_keys=True))
        return 0
    document = (ROOT / 'docs/quality.md').read_text()
    encoded = document.split(BEGIN, 1)[1].split(END, 1)[0].strip()
    baseline = json.loads(encoded.removeprefix('```json').removesuffix('```').strip())
    failures = regressions(baseline, current)
    if failures:
        print('Quality regression:\n' + '\n'.join(failures), file=sys.stderr)
        return 1
    print('Quality baseline satisfied; tracked litter and process identifiers: '
          f'{len(current["litter"])}, {len(current["identifiers"])}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
