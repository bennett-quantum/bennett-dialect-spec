#!/usr/bin/env python3
"""Bennett legality spike. Python 3.11+ standard library only.

All tool invocations and immutable snapshots live below results/raw. No shell
is used for executing commands. Failed transformations never become noops.
"""
import argparse
import collections
import concurrent.futures
import contextlib
import difflib
import fcntl
import fnmatch
import functools
import hashlib
import json
import os
import pathlib
import random
import re
import resource
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
RAW = RESULTS / 'raw'
VERSION = 'legality-harness-v3'
FORBIDDEN = {'readnone', 'readonly', 'writeonly', 'argmemonly',
             'inaccessiblememonly', 'willreturn', 'speculatable'}
NAME = r'@("(?:[^"\\]|\\.)+"|[-a-zA-Z$._0-9]+)'
MARKER = r'@(__bennett_[-a-zA-Z$._0-9]+)\s*\('
ATTR_WORDS = set('''alwaysinline allocsize allocalign allocptr align alignstack builtin byval byref cold convergent dereferenceable dereferenceable_or_null elementtype fn_ret_thunk_extern hot immarg inalloca inreg inlinehint jumptable minsize mustprogress naked nest noalias nocallback nocapture nocf_check noduplicate nofree noimplicitfloat noinline nomerge nonlazybind nonnull noprofile noredzone norecurse noreturn nosanitize_bounds nosanitize_coverage nosync nounwind noundef null_pointer_is_valid optforfuzzing optnone optsize preallocated presplitcoroutine readnone readonly returned returns_twice safestack sanitize_address sanitize_hwaddress sanitize_memory sanitize_thread sanitize_realtime shadowcallstack signext speculatable speculatable stackalign sret ssp sspreq sspstrong strictfp swiftasync swifterror swiftself uwtable willreturn writeonly argmemonly inaccessiblememonly inaccessiblemem_or_argmemonly memory captures initializes dead_on_unwind range nofpclass nocreateundef noext zeroext vscale_range denormal-fp-math writable dead_on_return alloc-family allockind nooutline nosanitize_address nosanitize_memory nosanitize_thread no-jump-tables skipprofile sanitize_memtag coroutine_only_destroy_when_complete coro_only_destroy_when_complete'''.split())


def digest(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


def atomic_json(path, value):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f'.{os.getpid()}.tmp')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    tmp.replace(path)


def canonical_ir(text):
    return re.sub(r'^; ModuleID = .*\n', '', text, flags=re.M)


def read_header(text, stem):
    fields = {}
    for key in ('CASE', 'HAZARD', 'INPUTS', 'EXPECT'):
        values = re.findall(r'^\s*(?:;|//)\s*' + key + r':\s*(.*?)\s*$', text, re.M)
        if len(values) != 1 or not values[0]:
            raise ValueError(f'{stem}: expected exactly one nonempty {key} header')
        fields[key] = values[0]
    if fields['CASE'] != stem or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', stem):
        raise ValueError(f'{stem}: CASE must equal kebab-case file stem')
    if fields['EXPECT'] not in ('legal', 'probe'):
        raise ValueError(f'{stem}: EXPECT must be legal or probe')
    s = fields['INPUTS']
    if re.fullmatch(r'-?\d+\.\.-?\d+', s):
        lo, hi = map(int, s.split('..'))
        if lo > hi or hi - lo > 100000:
            raise ValueError(f'{stem}: invalid or excessive input range')
        inputs = list(range(lo, hi + 1))
    elif re.fullmatch(r'-?\d+(?:\s+-?\d+)*', s):
        inputs = list(map(int, s.split()))
    else:
        raise ValueError(f'{stem}: invalid INPUTS {s!r}')
    if any(x < -(1 << 63) or x >= (1 << 63) for x in inputs):
        raise ValueError(f'{stem}: INPUTS outside signed i64')
    return {'id': stem, 'hazard': fields['HAZARD'], 'expect': fields['EXPECT'], 'inputs': inputs}


def parse_passes(listing):
    passes, seen = [], set()
    level = None
    params = False
    for line in listing.splitlines():
        if line and not line[0].isspace():
            match = re.fullmatch(r'(Module|CGSCC|Function|Loop|LoopNest|Loop-MSSA|Loop MSSA) passes( with params)?:', line)
            level = match[1] if match else None
            params = bool(match and match[2])
            continue
        if not level or not line.strip():
            continue
        printed = line.strip()
        name = printed
        if params:
            # Strip the last top-level parameter group, retaining print<analysis>.
            depth, starts = 0, []
            for i, ch in enumerate(name):
                if ch == '<':
                    if depth == 0:
                        starts.append(i)
                    depth += 1
                elif ch == '>':
                    depth -= 1
            if depth != 0:
                raise ValueError(f'unbalanced print-passes entry: {printed}')
            if starts:
                name = name[:starts[-1]]
        actual_level = level
        if level == 'Module':
            pipeline = name
        elif level == 'CGSCC':
            pipeline = f'cgscc({name})'
        elif level == 'Function':
            pipeline = f'function({name})'
        else:
            mssa = level in ('Loop-MSSA', 'Loop MSSA') or name in ('licm', 'lnicm')
            actual_level = 'Loop-MSSA' if mssa else level
            pipeline = f'function({"loop-mssa" if mssa else "loop"}({name}))'
        if pipeline not in seen:
            seen.add(pipeline)
            passes.append({'printed': printed, 'name': name, 'level': actual_level, 'pipeline': pipeline})
    if not passes:
        raise ValueError('opt --print-passes contained no recognized IR passes')
    return passes


@functools.lru_cache(maxsize=256)
def functions(ir):
    result = {}
    current = None
    for line in ir.splitlines():
        if line.startswith('define '):
            m = re.search(NAME + r'\s*\(', line)
            if not m:
                raise ValueError(f'cannot parse function header {line}')
            current = m[1].strip('"')
            result[current] = []
        elif current is not None:
            if line.strip() == '}':
                current = None
            else:
                result[current].append(line)
    return result


def _balanced_end(text, start):
    depth = 0
    quoted, escaped = False, False
    for i in range(start, len(text)):
        c = text[i]
        if quoted:
            if escaped:
                escaped = False
            elif c == '\\':
                escaped = True
            elif c == '"':
                quoted = False
            continue
        if c == '"':
            quoted = True
        elif c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return i
    raise ValueError(f'unbalanced marker declaration/call: {text}')


def _attr_tokens(text, all_words=False):
    # Keep argument-bearing attributes intact (notably memory(argmem: read)).
    # Only `align N` takes a bare integer; otherwise `noundef 0` would swallow
    # the following call argument as part of the attribute.
    tokens = re.findall(r'"[^"\n]*"(?:="[^"\n]*")?|(?<![%@\w.-])align(?:stack)?\s+\d+|(?<![%@\w.-])[a-zA-Z_][\w.-]*(?:\([^()]*\))?', text)
    out = set()
    for token in tokens:
        base = re.split(r'[ (]', token)[0]
        if all_words or base in ATTR_WORDS or token.startswith('"'):
            if base not in ('to', 'unwind', 'label', 'metadata'):
                out.add(re.sub(r'\s+', ' ', token.strip()))
    return out


@functools.lru_cache(maxsize=256)
def marker_attributes(ir):
    groups = {int(n): body for n, body in re.findall(r'^attributes #(\d+) = \{(.*?)\}\s*$', ir, re.M)}
    records = []
    function = '<module>'
    for line in ir.splitlines():
        if line.startswith('define '):
            m = re.search(NAME, line)
            function = m[1].strip('"') if m else '<unknown>'
        if line.strip() == '}':
            function = '<module>'
        m = re.search(MARKER, line)
        if not m or not (line.startswith('declare ') or re.search(r'\b(call|invoke|callbr)\b', line[:m.start()])):
            continue
        start = line.index('(', m.start())
        end = _balanced_end(line, start)
        suffix = line[end + 1:]
        # Metadata and operand bundles are not function attributes.
        suffix = re.split(r',\s*!|\s+to label|\s+\[', suffix)[0]
        expanded = suffix
        for n in re.findall(r'#(\d+)', suffix):
            if int(n) not in groups:
                raise ValueError(f'unresolved marker attribute group #{n}')
            expanded = re.sub(r'#' + n + r'\b', groups[int(n)], expanded)
        prefix = line[:m.start()]
        attrs = _attr_tokens(prefix) | _attr_tokens(line[start + 1:end]) | _attr_tokens(expanded, True)
        records.append({'marker': m[1], 'kind': 'declaration' if line.startswith('declare ') else 'call',
                        'function': '<module>' if line.startswith('declare ') else function,
                        'signature': line[start + 1:end], 'attributes': attrs})
    return records


def forbidden(attr):
    return attr in FORBIDDEN or attr.startswith('memory(')


def check_l2(pre, post):
    before, after = marker_attributes(pre), marker_attributes(post)
    added, observations, existing = [], [], []
    for site in before:
        for attr in sorted(site['attributes']):
            if forbidden(attr):
                existing.append({k: site[k] for k in ('marker', 'kind', 'function')} | {'attribute': attr})
    counters = collections.Counter()
    signature_counters = collections.Counter()
    for site in after:
        candidates = [s for s in before if s['marker'] == site['marker'] and s['kind'] == site['kind'] and s['function'] == site['function']]
        if not candidates and site['kind'] == 'call':
            candidates = [s for s in before if s['marker'] == site['marker'] and s['kind'] == 'call']
        exact = [s for s in candidates if s['signature'] == site['signature']]
        key = (site['marker'], site['kind'], site['function'])
        index = counters[key]
        counters[key] += 1
        signature_key = (*key, site['signature'])
        exact_index = signature_counters[signature_key]
        signature_counters[signature_key] += 1
        prior = (exact[min(exact_index, len(exact) - 1)] if exact else candidates[min(index, len(candidates) - 1)]) if candidates else None
        old = prior['attributes'] if prior else set()
        for attr in sorted(site['attributes'] - old):
            detail = {k: site[k] for k in ('marker', 'kind', 'function')} | {'attribute': attr}
            (added if forbidden(attr) else observations).append(detail)
    return {'forbidden_added': added, 'observations': observations, 'preexisting_forbidden': existing}


def check_l3_static(pre, post):
    a, b = functions(pre), functions(post)
    graph = collections.defaultdict(set)
    globals_ = set(re.findall(r'^' + NAME + r'\s*=', pre + '\n' + post, re.M))
    global_users = collections.defaultdict(set)
    touched = set()
    for name, body in list(a.items()) + list(b.items()):
        text = '\n'.join(body)
        if '__bennett_' in text:
            touched.add(name)
        for callee in re.findall(NAME, text):
            if callee in a or callee in b:
                graph[name].add(callee)
                graph[callee].add(name)
            if callee in globals_:
                global_users[callee].add(name)
    for users in global_users.values():
        for name in users:
            graph[name].update(users - {name})
    pending = list(touched)
    while pending:
        name = pending.pop()
        for other in graph[name] - touched:
            touched.add(other)
            pending.append(other)
    flags = []
    for name in sorted(touched & b.keys()):
        for opcode in ('ptrtoint', 'inttoptr'):
            old = sum(len(re.findall(r'\b' + opcode + r'\b', line)) for line in a.get(name, []))
            new = [line.strip() for line in b[name] if re.search(r'\b' + opcode + r'\b', line)]
            if len(new) > old:
                flags.append({'function': name, 'opcode': opcode, 'before': old, 'after': len(new), 'lines': new})
    return flags


@functools.lru_cache(maxsize=128)
def region_symbols(trace):
    return re.findall(r'\bF:([^\s]+)', trace)


def check_l4(baseline_trace, trace, ir):
    """Region identity. Trace symbols are `name` or `name=alias...` (every symbol
    starting at that address in the executable), or `F?` (no symbol start)."""
    expected, actual = region_symbols(baseline_trace), region_symbols(trace)
    issues = []
    if expected != actual:
        issues.append({'reason': 'region symbol sequence changed', 'before': expected, 'after': actual})
    defs = functions(ir)
    for symbol in sorted(set(expected + actual)):
        if symbol == 'F?':
            issues.append({'reason': 'region address resolves to no symbol start', 'symbol': symbol})
            continue
        defined = [n for n in symbol.split('=') if n in defs]
        if not defined:
            issues.append({'reason': 'region is not a definition (missing, declaration, or alias)', 'symbol': symbol})
        for name in defined:
            body = [s.strip() for s in defs[name] if s.strip() and not s.lstrip().startswith(';') and not s.rstrip().endswith(':')]
            calls = re.findall(r'\b(?:call|invoke)\b[^\n]*?' + NAME + r'\s*\(', '\n'.join(body))
            if len(calls) == 1 and calls[0] in defs and calls[0] != name and all(re.search(r'\b(call|ret|bitcast)\b', s) for s in body):
                issues.append({'reason': 'region is a forwarding thunk', 'symbol': name, 'target': calls[0]})
    return issues

# ---------------------------------------------------------------------------
# Environment-incompatible native builds (outcome env-error). Decided only from
# the evidence of the failing tool, never from the pass name. Narrow by design:
# any undefined __bennett_* symbol, any symbol outside these runtime families,
# or any failure that is not an undefined reference keeps the cell FAIL.
ENV_RUNTIME_SYMBOL = re.compile(r'^(?:'
    r'__asan_|__msan_|__tsan_|__hwasan_|__dfsan_|__memprof_|__nsan_|__rtsan_|__tysan_|'
    r'__ubsan_|__sanitizer_|__sancov_|__cfi_|__safestack_|__xray_|'
    r'__llvm_profile_|__llvm_ctx_profile_|__llvm_gcov_|llvm_gcda_|llvm_gcov_|'
    r'__poison_checker_|__instrumentor_|_Unwind_SjLj_)')
ENTRY = 'case_entry'


def external_entry_defined(ir):
    return bool(re.search(r'^define\s+(?!(?:internal|private)\b)(?:[\w()"=,.]+\s+)*?i64\s+@case_entry\(', ir, re.M))


def env_evidence_link(stderr_text, ir):
    undefined = link_undefined(stderr_text)
    if not undefined:
        return None
    hidden = bool(re.search(LD_UNDEFINED[2], stderr_text))
    hwasan = bool(re.search(r'@__hwasan_', ir))
    def accounted(line):
        return (not line.strip() or any(re.search(p, line) for p in LD_UNDEFINED)
                or re.search(r': in function [`\'][^\']*\':$', line) or 'ld returned 1 exit status' in line
                # follows a hidden undefined instrumentation symbol
                or (hidden and line.rstrip().endswith('final link failed: bad value'))
                # HWASan tags global addresses in the top byte; x86-64 PC32
                # relocations to tagged globals overflow without its runtime aliases.
                or (hwasan and 'relocation truncated to fit' in line))
    if not all(accounted(l) for l in stderr_text.splitlines()):
        return None
    if any(u.startswith('__bennett_') for u in undefined):
        return None
    runtime = [u for u in undefined if ENV_RUNTIME_SYMBOL.match(u)]
    rest = [u for u in undefined if u not in runtime]
    if rest == [ENTRY] and not external_entry_defined(ir):
        return {'rule': 'entry-not-external', 'undefined': undefined,
                'note': 'transformed module deleted or internalised @case_entry; the driver cannot link'}
    if rest:
        return None
    return {'rule': 'missing-instrumentation-runtime', 'undefined': undefined}


def env_evidence_llc(stderr_text, ir):
    """llc cannot select instrumentation intrinsics that an IR lowering pass
    (instrprof) must replace first; that pass is not part of llc."""
    if not re.search(r'\bcall\b[^\n]*@llvm\.instrprof\.', ir):
        return None
    if re.search(r'Cannot select: intrinsic %llvm\.instrprof\.', stderr_text) or \
            re.search(r"Running pass '[^']*Instruction Selection'", stderr_text):
        return {'rule': 'unlowered-instrprof-intrinsic',
                'intrinsics': sorted(set(re.findall(r'@(llvm\.instrprof\.[\w.]+)\(', ir))),
                'diagnostic': next((l for l in stderr_text.splitlines() if 'Cannot select' in l or 'Instruction Selection' in l), '')}
    return None


# ---------------------------------------------------------------------------
# Passes that by design do not preserve a standalone host program. Applied only
# to single-pass cells of exactly these passes, and only when the documented
# behaviour is confirmed in the transformed module. Rationale: harness/NOTES.md.
def _markers_renamed(pre, post):
    before = set(re.findall(r'@(__bennett_\w+)\s*\(', pre))
    after = set(re.findall(r'@(__bennett_\w+)\s*\(', post))
    return sorted(before - after)


NON_PRESERVING = {
    'metarenamer': ('renames every non-intrinsic, non-libcall function, including marker declarations and @case_entry',
                    lambda pre, post: bool(_markers_renamed(pre, post)) and not external_entry_defined(post)),
    'dfsan': ('DataFlowSanitizer without an ABI list renames functions with a .dfsan suffix, including markers',
              lambda pre, post: bool(re.search(r'@(?:__bennett_\w+|case_entry)\.dfsan\b', post))),
    'hipstdpar-select-accelerator-code': ('keeps only accelerator kernels; deletes host code including @case_entry',
              lambda pre, post: not re.search(r'^define\b.*@case_entry\(', post, re.M)),
}


def single_pass_name(pipeline):
    m = re.fullmatch(r'(?:function\((?:loop(?:-mssa)?\()?|cgscc\()?([\w.<>;=-]+?)\)*', pipeline)
    return m[1] if m else None


# ---------------------------------------------------------------------------
# Documented preconditions. A precondition outcome requires (a) evidence that
# the input violates the precondition: running the prerequisite passes alone
# changes the input module; and (b) that rerunning with the prerequisites
# passes every check. Otherwise the cell stays FAIL. Both runs are recorded.
PRECONDITIONS = {
    'structurizecfg': {
        'doc': 'StructurizeCFG expects no switch terminators, a reducible CFG and single-exit loops; '
               'its in-tree user (AMDGPU) runs lowerswitch, fix-irreducible and unify-loop-exits first',
        'prerequisites': ['{lowerswitch}', 'fix-irreducible', 'unify-loop-exits'],
    },
}
LOWERSWITCH = {18: 'lowerswitch'}  # LLVM 20 and 23 spell it lower-switch


def precondition_for(pipeline, major):
    name = single_pass_name(pipeline)
    spec = PRECONDITIONS.get(name)
    if not spec:
        return None
    prereqs = [p.format(lowerswitch=LOWERSWITCH.get(major, 'lower-switch')) for p in spec['prerequisites']]
    return {'pass': name, 'doc': spec['doc'], 'prerequisite_pipeline': f'function({",".join(prereqs)})',
            'pipeline': f'function({",".join(prereqs)},{name})'}


def prerequisites_change_input(case, tc, pre, input_module):
    directory = RAW / 'precondition-probes' / digest(json.dumps([VERSION, tc['identity'], input_module['hash'], pre['prerequisite_pipeline']]))
    with locked(directory / 'lock'):
        if (directory / 'probe.json').exists():
            return json.loads((directory / 'probe.json').read_text())['changed']
        r = required_command([tc['opt'], '-passes=' + pre['prerequisite_pipeline'], input_module['bc'], '-o', directory / 'out.bc'], directory, 'opt')
        out = publish_module(directory / 'out.bc', tc)
        changed = out['hash'] != input_module['hash']
        atomic_json(directory / 'probe.json', {'changed': changed, 'command': r['command'], 'output': out})
        return changed


# ---------------------------------------------------------------------------
# L6: static shape of every region-marker function operand (observation).
REGION_OPERANDS = {'__bennett_ctrl': (2,), '__bennett_adj': (0,), '__bennett_compute': (0, 1),
                   '__bennett_reversible': (0,), '__bennett_inplace': (0, 1), '__bennett_ctrl_v': (2,)}
L6_SHAPES = ('const', 'select-of-consts', 'phi-of-consts', 'load-from-const-table',
             'select-of-mixed', 'phi-of-mixed', 'other')
# *-of-mixed: every incoming value is itself statically resolvable (const, a
# constant-table load, or a nested select/phi of those) but not all are consts.


def _split_top(text):
    parts, depth, cur, quoted = [], 0, '', False
    for c in text:
        if c == '"':
            quoted = not quoted
        if not quoted:
            if c in '([{<':
                depth += 1
            elif c in ')]}>':
                depth -= 1
            elif c == ',' and depth == 0:
                parts.append(cur.strip())
                cur = ''
                continue
        cur += c
    if cur.strip():
        parts.append(cur.strip())
    return parts


def _operand_value(arg):
    """`ptr nonnull @f` -> `@f`; constant expressions are returned whole."""
    arg = arg.strip()
    m = re.search(r'\b(bitcast|addrspacecast)\s*\(\s*ptr\s+(@[-\w$.]+|@"[^"]+")\s+to\s+ptr\s*\)\s*$', arg)
    if m:
        return m[2]
    m = re.search(r'([%@]"[^"]*"|[%@][-\w$.]+)$', arg)
    if m and not arg.endswith(')'):
        return m[1]
    return arg


def _function_values(body):
    values = {}
    for line in body:
        m = re.match(r'\s*(%[-\w$.]+|%"[^"]+")\s*=\s*(.*)$', line)
        if m:
            values[m[1]] = m[2]
    return values


def _constant_globals(ir):
    tables = {}
    for m in re.finditer(r'^(@[-\w$.]+|@"[^"]+")\s*=\s*([^\n]*)$', ir, re.M):
        rhs = m[2]
        if re.search(r'\bconstant\b', rhs.split('[')[0] + ' ' + rhs.split('{')[0]) and not re.search(r'\b(alias|ifunc)\b', rhs.split('[')[0]):
            tables[m[1]] = rhs
    return tables


def _is_fn_const(value, defs_and_decls):
    return bool(re.fullmatch(r'@[-\w$.]+|@"[^"]+"', value)) and value[1:].strip('"') in defs_and_decls


def _combine(kind, parts):
    if parts and all(p == 'const' for p in parts):
        return kind + '-of-consts'
    if parts and all(p != 'other' for p in parts):
        return kind + '-of-mixed'
    return 'other'


def _shape(value, values, tables, names, depth=0):
    if _is_fn_const(value, names):
        return 'const', value
    if depth > 6 or not value.startswith('%') or value not in values:
        return 'other', value
    rhs = values[value]
    m = re.match(r'select\b(?:\s+\w+)*\s+i1\s+\S+,\s*ptr\s+(\S+),\s*ptr\s+(\S+)', rhs)
    if m:
        arms = [_operand_value('ptr ' + a.rstrip(',')) for a in (m[1], m[2])]
        return _combine('select', [_shape(a, values, tables, names, depth + 1)[0] for a in arms]), rhs
    m = re.match(r'phi\b(?:\s+\w+)*\s+ptr\s+(.*)$', rhs)
    if m:
        incoming = [v.strip() for v in re.findall(r'\[\s*([^,\]]+),\s*%[^\]]+\]', m[1])]
        return _combine('phi', [_shape(v, values, tables, names, depth + 1)[0] for v in incoming]), rhs
    m = re.match(r'load\b(?:\s+\w+)*\s+ptr,\s*ptr\s+(.*?)(?:,\s*align\b.*|,\s*!.*)?$', rhs)
    if m:
        address = m[1].strip()
        base = None
        inline = re.match(r'getelementptr\b.*?\(\s*[^,]+,\s*ptr\s+(@[-\w$.]+|@"[^"]+")', address)
        if inline:
            base = inline[1]
        elif address.startswith('@'):
            base = address
        elif address in values:
            gep = re.match(r'getelementptr\b(?:\s+\w+)*\s+[^,]+,\s*ptr\s+(@[-\w$.]+|@"[^"]+")', values[address])
            if gep:
                base = gep[1]
        if base and base in tables:
            refs = re.findall(r'\bptr\s+(@[-\w$.]+|@"[^"]+"|null)', tables[base])
            if refs and all(_is_fn_const(r, names) for r in refs):
                return 'load-from-const-table', rhs + ' ; ' + base
        return 'other', rhs
    return 'other', rhs


@functools.lru_cache(maxsize=256)
def region_operand_shapes(ir):
    defs = functions(ir)
    names = set(defs) | {m.strip('"') for m in re.findall(r'^declare\b[^@]*' + NAME, ir, re.M)}
    tables = _constant_globals(ir)
    sites = []
    for function, body in defs.items():
        values = _function_values(body)
        for line in body:
            m = re.search(r'\b(?:call|invoke)\b[^@]*@(__bennett_(?:ctrl_v|ctrl|adj|compute|reversible|inplace))\s*\(', line)
            if not m:
                continue
            start = line.index('(', m.end() - 1)
            args = _split_top(line[start + 1:_balanced_end(line, start)])
            for index in REGION_OPERANDS[m[1]]:
                if index >= len(args):
                    sites.append({'function': function, 'marker': m[1], 'operand': index, 'shape': 'other', 'value': '<missing operand>'})
                    continue
                value = _operand_value(args[index])
                shape, detail = _shape(value, values, tables, names)
                sites.append({'function': function, 'marker': m[1], 'operand': index, 'shape': shape, 'value': value, 'detail': detail})
    return sites


def check_l6(pre, post):
    before = collections.Counter((s['marker'], s['operand'], s['shape']) for s in region_operand_shapes(pre))
    after_sites = region_operand_shapes(post)
    after = collections.Counter((s['marker'], s['operand'], s['shape']) for s in after_sites)
    introduced = [{'marker': m, 'operand': o, 'shape': sh} for (m, o, sh), n in sorted(after.items()) if n > before.get((m, o, sh), 0) and sh != 'const']
    return {'sites': [{k: v for k, v in s.items() if k != 'detail'} for s in after_sites],
            'shapes': sorted({s['shape'] for s in after_sites}), 'introduced': introduced,
            'other': [s for s in after_sites if s['shape'] == 'other']}


@contextlib.contextmanager
def locked(path):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        yield


@functools.lru_cache(maxsize=256)
def immutable_text(path):
    return pathlib.Path(path).read_text()


STATIC_SCHEMA = 'static-v5'


def static_analysis(before, after):
    # Bump STATIC_SCHEMA whenever a static checker changes: cached analyses are
    # keyed only by the module pair.
    key = digest(json.dumps([STATIC_SCHEMA, before['hash'], after['hash']]))
    directory = RAW / 'static' / key
    with locked(directory / 'lock'):
        if (directory / 'analysis.json').exists():
            return json.loads((directory / 'analysis.json').read_text())
        a, b = immutable_text(before['ll']), immutable_text(after['ll'])
        result = {'l2': check_l2(a, b), 'l3': check_l3_static(a, b), 'l6': check_l6(a, b)}
        atomic_json(directory / 'analysis.json', result)
        return result


HEADLESS_BIN = RAW / 'headless-bin'
VIEWER_LOG = RAW / 'viewer-attempts.log'
VIEWERS = ('xdg-open', 'gio', 'gnome-open', 'kde-open', 'kde-open5', 'sensible-browser',
           'x-www-browser', 'xdot', 'dotty', 'gv', 'evince', 'okular', 'zathura', 'eog',
           'display', 'open')


def headless_env(tmpdir=None):
    """Environment for every tool the harness runs: no route to the desktop, temp files local.

    Viewer passes (view-cfg, view-dom, view-callgraph, ...) are still enumerated and run. On
    2026-10-28 they wrote ~80,000 .dot files to /tmp and reached the maintainer's editor through
    xdg-open over D-Bus: dropping DISPLAY/WAYLAND_DISPLAY alone was not enough. Now D-Bus is
    dropped too, TMPDIR is the cell directory, and every known viewer resolves first to a stub
    that logs the attempt to VIEWER_LOG and fails.
    """
    HEADLESS_BIN.mkdir(parents=True, exist_ok=True)
    for name in VIEWERS:
        stub = HEADLESS_BIN / name
        if not stub.exists():
            stub.write_text(f'#!/bin/sh\necho "{name} $*" >> "{VIEWER_LOG}"\nexit 1\n')
            stub.chmod(0o755)
    env = dict(os.environ, LLVM_DISABLE_CRASH_REPORT='1')
    for key in ('DISPLAY', 'WAYLAND_DISPLAY', 'DBUS_SESSION_BUS_ADDRESS', 'BROWSER'):
        env.pop(key, None)
    env['PATH'] = f'{HEADLESS_BIN}{os.pathsep}{env.get("PATH", "")}'
    if tmpdir is not None:
        env['TMPDIR'] = str(tmpdir)
    return env


def command(argv, directory, label, timeout=30, env_override=None):
    directory = pathlib.Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    out, err = directory / (label + '.stdout'), directory / (label + '.stderr')
    start = time.monotonic()
    timed_out = False
    env = headless_env(tmpdir=directory)
    env.update(env_override or {})
    new_session = os.environ.get('BENNETT_REDUCER_CHILD') != '1'
    with out.open('wb') as stdout, err.open('wb') as stderr:
        process = subprocess.Popen(list(map(str, argv)), cwd=directory, stdout=stdout,
                                   stderr=stderr, env=env, start_new_session=new_session)
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            if new_session:
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.wait()
    result = {'argv': list(map(str, argv)), 'command': shlex.join(list(map(str, argv))),
              'cwd': str(directory), 'returncode': process.returncode, 'timeout': timed_out,
              'stdout': str(out), 'stderr': str(err), 'seconds': round(time.monotonic() - start, 4)}
    atomic_json(directory / (label + '.command.json'), result)
    return result


def successful(result):
    return result['returncode'] == 0 and not result['timeout']


def required_command(argv, directory, label, timeout=30):
    r = command(argv, directory, label, timeout)
    if not successful(r):
        raise RuntimeError(f'{r["command"]}: exit {r["returncode"]}; {pathlib.Path(r["stderr"]).read_text(errors="replace")[-4000:]}')
    return r


def tools_for(majors):
    config = tomllib.loads((ROOT / 'toolchains.toml').read_text())
    result = {}
    for major in majors:
        key = f'llvm{major}'
        if key not in config:
            raise ValueError(f'major {major} not configured')
        bindir = pathlib.Path(config[key]['bin'])
        entry = {'major': major}
        for name in ('opt', 'llc', 'llvm-dis', 'llvm-as', 'llvm-link', 'llvm-nm'):
            path = bindir / name
            if not path.is_file() or not os.access(path, os.X_OK):
                raise ValueError(f'{key}: missing executable {path}')
            entry[name] = str(path)
        stat = pathlib.Path(entry['opt']).stat()
        entry['identity'] = digest(f'{bindir}:{stat.st_size}:{stat.st_mtime_ns}')
        result[major] = entry
    if not shutil.which('cc'):
        raise ValueError('system cc is required')
    return result


def runtime_objects():
    files = [ROOT / 'markers.h', ROOT / 'runtime/trace_rt.c', ROOT / 'runtime/driver.c']
    key = digest(b''.join(p.read_bytes() for p in files) + VERSION.encode())
    directory = RAW / 'runtime' / key
    with locked(directory / 'lock'):
        if not (directory / 'ready.json').exists():
            for stem in ('trace_rt', 'driver'):
                required_command(['cc', '-std=c11', '-O0', '-fPIC', '-Wall', '-Wextra', '-Werror', '-c',
                                  ROOT / f'runtime/{stem}.c', '-o', directory / f'{stem}.o'], directory, stem)
            atomic_json(directory / 'ready.json', {'key': key})
    return {'key': key, 'objects': [str(directory / 'trace_rt.o'), str(directory / 'driver.o')]}


def publish_module(bc, tc):
    bitcode_hash = digest(pathlib.Path(bc).read_bytes())
    index = RAW / 'bitcode-index' / str(tc['major']) / bitcode_hash
    with locked(index / 'lock'):
        if (index / 'module.json').exists():
            return json.loads((index / 'module.json').read_text())
        required_command([tc['llvm-dis'], bc, '-o', index / 'disassembled.ll'], index, 'disassemble')
        text = canonical_ir((index / 'disassembled.ll').read_text())
        # Bitcode can differ solely in writer/use-list ordering while llvm-dis
        # produces identical IR. Hash that IR, excluding its path-only ModuleID.
        key = digest(text)
        directory = RAW / 'modules' / str(tc['major']) / key
        with locked(directory / 'lock'):
            if not (directory / 'module.ll').exists():
                shutil.copyfile(bc, directory / 'module.bc')
                (directory / 'module.ll').write_text(text)
        result = {'hash': key, 'bc': str(directory / 'module.bc'), 'll': str(directory / 'module.ll')}
        atomic_json(index / 'module.json', result)
        return result


def execute_inputs(exe, inputs, directory, label, timeout=10):
    """Batch the common success path; resume remaining inputs after a fault.

    A malformed driver protocol is an explicit failure, even with exit status 0.
    """
    pending = list(inputs)
    traces, errors, commands = [], [], []
    exit_code, timed_out, executed = 0, False, 0
    while pending:
        r = command([exe, *map(str, pending)], directory, label + f'-batch-{len(commands)}', timeout=timeout)
        commands.append(r)
        trace = pathlib.Path(r['stdout']).read_text(errors='replace')
        traces.append(trace)
        errors.append(pathlib.Path(r['stderr']).read_text(errors='replace'))
        started = re.findall(r'^IN (-?\d+)$', trace, re.M)
        returned = re.findall(r'^RET (-?\d+)$', trace, re.M)
        valid = [int(x) for x in started] == pending[:len(started)] and len(started) <= len(pending)
        if r['returncode'] or r['timeout']:
            exit_code = exit_code or r['returncode'] or 88
            timed_out |= r['timeout']
        if not valid or (r['returncode'] == 0 and (len(started) != len(pending) or len(returned) != len(started))):
            exit_code = exit_code or 89
            errors.append('harness: incomplete or invalid IN/RET protocol\n')
        consumed = min(len(pending), max(1, len(started)))
        executed += len(started) if valid else 0
        pending = pending[consumed:]
        if r['timeout']:
            errors.append(f'harness: timeout; remaining inputs explicitly unexecuted: {pending}\n')
            break
    trace_path = pathlib.Path(directory) / (label + '.trace')
    error_path = pathlib.Path(directory) / (label + '.stderr')
    trace_path.write_text(''.join(traces))
    error_path.write_text(''.join(errors))
    return {'exit': exit_code, 'timeout': timed_out, 'trace': str(trace_path),
            'stderr': str(error_path), 'inputs_executed': executed,
            'inputs_unexecuted': pending, 'commands': commands}


RAW_REGION = re.compile(r'\bF@0x([0-9a-f]+)\b')


def canonicalize_trace(raw, symbols):
    """Replace runtime `F@0x<addr>` with `F:<name>[=<alias>...]` or `F:F?`.

    `symbols` maps a symbol start address to every defined symbol name there.
    An address that is not exactly a symbol start is unresolved (a finding).
    """
    if re.search(r'\bF:', raw):
        raise ValueError('raw trace already contains canonical F: symbols; runtime/harness mismatch')
    def name(m):
        names = symbols.get(int(m[1], 16))
        return 'F:' + ('='.join(sorted(set(names))) if names else 'F?')
    return RAW_REGION.sub(name, raw)


def executable_symbols(exe, nm, directory, label):
    """Full static symbol table (locals included) of a non-PIE executable."""
    with open(exe, 'rb') as f:
        header = f.read(18)
    if header[:4] != b'\x7fELF' or int.from_bytes(header[16:18], 'little') != 2:
        raise RuntimeError(f'{exe}: expected a non-PIE ELF executable (ET_EXEC) for fixed region addresses')
    r = required_command([nm, '-n', '--defined-only', exe], directory, label)
    symbols = collections.defaultdict(list)
    for line in pathlib.Path(r['stdout']).read_text().splitlines():
        parts = line.split()
        if len(parts) != 3:
            continue  # llvm-nm prints a filename header only for multiple inputs
        address, kind, name = parts
        if kind.lower() in ('t', 'w', 'i') or kind in ('T', 'W'):
            symbols[int(address, 16)].append(name)
    return symbols


def undefined_markers_in(obj, tc, directory, label):
    # GNU nm loads the bfd LLVM plugin and treats an object with a .llvm.lto
    # section (embed-bitcode / fat LTO) as IR, printing "no symbols". llvm-nm of
    # the same major reads the ELF symbol table.
    r = command([tc['llvm-nm'], '-u', obj], directory, label)
    if not successful(r):
        raise RuntimeError(f'llvm-nm failed: {r["command"]}')
    text = pathlib.Path(r['stdout']).read_text()
    return r, sorted(set(re.findall(r'\bU\s+(__bennett_[\w.]+)', text)))


LD_UNDEFINED = (r"undefined reference to [`']([^'`]+)'",
                r"more undefined references to [`']([^'`]+)' follow",
                r"hidden symbol [`']([^'`]+)' isn't defined")


def link_undefined(stderr_text):
    return sorted({s for pattern in LD_UNDEFINED for s in re.findall(pattern, stderr_text)})


NATIVE_SCHEMA = 'native-v3.1'


def native_key(tc, runtime, module, inputs, execution_timeout=10):
    # NATIVE_SCHEMA changes whenever the native.json record layout changes, so
    # cached records always carry every field the checks read.
    identity = [VERSION, NATIVE_SCHEMA, tc['identity'], runtime['key'], module['hash'], inputs]
    if execution_timeout != 10:
        identity.append(execution_timeout)
    return digest(json.dumps(identity))


def native(module, tc, runtime, inputs, levels=(0, 3), execution_timeout=10):
    # Lock around compile+run: concurrent identical outputs are evaluated once.
    key = native_key(tc, runtime, module, inputs, execution_timeout)
    directory = RAW / 'native' / key
    with locked(directory / 'lock'):
        data = json.loads((directory / 'native.json').read_text()) if (directory / 'native.json').exists() else {}
        for level in levels:
            tag = f'O{level}'
            if tag in data:
                continue
            obj, exe = directory / (tag + '.o'), directory / (tag + '.exe')
            commands = []
            r = command([tc['llc'], f'-O{level}', '-relocation-model=pic', '-filetype=obj', module['bc'], '-o', obj], directory, tag + '-llc')
            commands.append(r)
            record = {'commands': commands, 'stage': 'llc', 'ok': False}
            if not successful(r):
                record['diagnostic'] = pathlib.Path(r['stderr']).read_text(errors='replace')[:4000]
                record['diagnostic_path'] = r['stderr']
            else:
                nm, record['undefined_markers'] = undefined_markers_in(obj, tc, directory, tag + '-nm')
                commands.append(nm)
                r = command(['cc', '-no-pie', '-rdynamic', obj, *runtime['objects'], '-ldl', '-o', exe], directory, tag + '-link')
                commands.append(r)
                record['stage'] = 'link'
                if not successful(r):
                    record['diagnostic'] = pathlib.Path(r['stderr']).read_text(errors='replace')[:4000]
                    record['diagnostic_path'] = r['stderr']
                    record['link_undefined'] = link_undefined(pathlib.Path(r['stderr']).read_text(errors='replace'))
                else:
                    symbols = executable_symbols(exe, tc['llvm-nm'], directory, tag + '-symbols')
                    execution = execute_inputs(exe, inputs, directory, tag + '-execute', timeout=execution_timeout)
                    commands.extend(execution.pop('commands'))
                    raw_path = pathlib.Path(execution['trace'])
                    canonical = directory / (tag + '-execute.canonical.trace')
                    canonical.write_text(canonicalize_trace(raw_path.read_text(), symbols))
                    record.update(stage='execute', ok=True, **execution)
                    record.update(trace=str(canonical), raw_trace=str(raw_path))
            data[tag] = record
            atomic_json(directory / 'native.json', data)
    return data


TRACE_MARKERS = {name.upper(): '__bennett_' + name for name in (
    'qalloc', 'qborrow', 'qfree', 'gate', 'gate2', 'rot', 'measure', 'qload', 'qstore',
    'ctrl', 'adj', 'compute', 'reversible', 'inplace', 'ctrl_v')}


@functools.lru_cache(maxsize=128)
def called_markers(trace):
    return sorted({TRACE_MARKERS[line.split()[0]] for line in trace.splitlines() if line.split() and line.split()[0] in TRACE_MARKERS})


def dynamic_l3(trace):
    return [s for s in ('FAULT handle-deref', 'BADHANDLE') if s in trace]


def discover(patterns=None):
    paths = []
    for folder in ('harness/seed_cases', 'controls', 'cases'):
        directory = ROOT / folder
        if directory.exists():
            paths.extend(p for p in sorted(directory.iterdir()) if p.suffix in ('.ll', '.c'))
    if patterns:
        paths = [p for p in paths if any(fnmatch.fnmatch(p.name, g) or fnmatch.fnmatch(p.stem, g) or fnmatch.fnmatch(str(p.relative_to(ROOT)), g) for g in patterns)]
    if not paths:
        raise ValueError('case selection matched no .ll or .c files')
    if len({p.stem for p in paths}) != len(paths):
        raise ValueError('duplicate case ids across selected directories')
    return paths


C_FLAGS = ['-O1', '-Xclang', '-disable-llvm-passes']


def prepare_case(path, tcs, runtime):
    text = path.read_text()
    source_hash = digest(text + (json.dumps(C_FLAGS) if path.suffix == '.c' else ''))
    source_dir = RAW / 'sources' / source_hash
    source_dir.mkdir(parents=True, exist_ok=True)
    snapshot = source_dir / path.name
    if not snapshot.exists():
        snapshot.write_text(text)
    case = {'id': path.stem, 'path': str(path.relative_to(ROOT)), 'source': str(snapshot), 'source_hash': source_hash, 'majors': {}}
    try:
        case.update(read_header(text, path.stem))
    except ValueError as error:
        case['error'] = str(error)
        return case
    ll = snapshot
    if path.suffix == '.c':
        clang = pathlib.Path(tomllib.loads((ROOT / 'toolchains.toml').read_text())['llvm18']['bin']) / 'clang'
        ll = source_dir / (path.stem + '.ll')
        # -O1 with LLVM passes disabled: unoptimised IR without the noinline that
        # -O0 puts on every function (which would hide every inlining hazard).
        r = command([clang, *C_FLAGS, '-emit-llvm', '-S', '-I', ROOT, '-I', path.parent, snapshot, '-o', ll], source_dir, 'clang18')
        if not successful(r):
            case['error'] = 'C front-end failed: ' + r['command']
            return case
    if not re.search(r'^define\s+(?:\w+\s+)*i64\s+@case_entry\(i64(?:\s+[^,()]*)?\)', ll.read_text(), re.M):
        case['error'] = 'missing or wrong definition: expected define i64 @case_entry(i64 %x)'
        return case
    for major, tc in tcs.items():
        d = source_dir / str(major)
        r = command([tc['llvm-as'], ll, '-o', d / 'assembled.bc'], d, 'assemble')
        if not successful(r):
            case['majors'][str(major)] = {'error': 'malformed case: ' + r['command'], 'command': r}
            continue
        # Establish a canonical writer image for byte-for-byte noop detection.
        r = command([tc['opt'], '-passes=no-op-module', d / 'assembled.bc', '-o', d / 'raw.bc'], d, 'canonicalize')
        if not successful(r):
            case['majors'][str(major)] = {'error': 'canonicalization failed', 'command': r}
            continue
        module = publish_module(d / 'raw.bc', tc)
        both = native(module, tc, runtime, case['inputs'], (0, 3))
        n = both['O0']
        pre = pathlib.Path(module['ll']).read_text()
        if n['ok']:
            trace = pathlib.Path(n['trace']).read_text()
            issues = {}
            if n['exit'] != 0 or n['timeout']:
                issues['L1'] = f'baseline exit={n["exit"]}, timeout={n["timeout"]}'
            if dynamic_l3(trace):
                issues['L3'] = dynamic_l3(trace)
            l4 = check_l4(trace, trace, pre)
            if l4:
                issues['L4'] = l4
            missing = sorted(set(called_markers(trace)) - set(n['undefined_markers']))
            if missing:
                issues['L5'] = {'missing_marker_externals': missing}
        else:
            issues = {'L5': 'baseline native build failed at ' + n['stage']}
        o3 = both['O3']
        # Observation, not a baseline-gate issue: the untouched module under
        # llc -O3 already behaves differently (a codegen-level L5 finding).
        llc_o3 = {'ok': o3['ok'], 'stage': o3['stage']}
        if o3['ok'] and n['ok']:
            llc_o3['trace_equal'] = pathlib.Path(o3['trace']).read_text() == pathlib.Path(n['trace']).read_text() and o3['exit'] == n['exit']
        case['majors'][str(major)] = {'module': module, 'native': n, 'issues': issues, 'llc_O3': llc_o3,
                                      'attributes': _serial_attrs(marker_attributes(pre))}
    traces = {major: (pathlib.Path(b['native']['trace']).read_text(), b['native']['exit'])
              for major, b in case['majors'].items() if 'native' in b and b['native']['ok']}
    case['cross_major_agreement'] = len(set(traces.values())) <= 1 and len(traces) == len(tcs)
    return case


def _serial_attrs(records):
    return [{**r, 'attributes': sorted(r['attributes'])} for r in records]


def baseline_problems(cases):
    """Case errors, cross-major disagreement, and any baseline issue (F?,
    missing markers, faults) outside the intentional handle-deref control."""
    out = []
    for c in cases:
        if c.get('error'):
            out.append(f'{c["id"]}: {c["error"]}')
            continue
        if not c.get('cross_major_agreement'):
            out.append(f'{c["id"]}: baselines disagree across majors')
        for major, b in c.get('majors', {}).items():
            issues = b.get('issues', {'error': b.get('error')})
            if c['id'] == 'control-handle-deref':
                issues = {k: v for k, v in issues.items() if k not in ('L1', 'L3')}
            if issues:
                out.append(f'{c["id"]} LLVM {major}: {json.dumps(issues, sort_keys=True)}')
    return out


def make_baselines(paths, tcs, runtime):
    cases = []
    for i, path in enumerate(paths):
        c = prepare_case(path, tcs, runtime)
        cases.append(c)
        verdict = 'case-error' if c.get('error') else ('agree' if c['cross_major_agreement'] else 'DISAGREE')
        print(f'baseline {i+1}/{len(paths)} {c["id"]}: {verdict}', flush=True)
    return cases


def behaviour(native_data, baseline_trace, ir):
    """Everything the dynamic checks observe about one module, per level."""
    out = []
    for level in ('O0', 'O3'):
        v = native_data[level]
        if not v['ok']:
            out.append((level, False, v['stage'], tuple(v.get('undefined_markers', ()))))
            continue
        trace = immutable_text(v['trace'])
        out.append((level, True, digest(trace), v['exit'], v['timeout'], tuple(v['undefined_markers']),
                    json.dumps(check_l4(baseline_trace, trace, ir), sort_keys=True)))
    return out


def cell_identity(task):
    case, tc, runtime = task['case'], task['tc'], task['runtime']
    identity = [VERSION, case['source_hash'], case['id'], tc['major'], task['suite'], task['mode'], task['pipeline'], runtime['key']]
    if task.get('opt_args'):
        identity.append(task['opt_args'])
    return digest(json.dumps(identity))[:20]


def pipeline_label(r):
    return r['pipeline'] + (' [' + ' '.join(r['opt_args']) + ']' if r.get('opt_args') else '')


def evaluate(task):
    """One complete recorded outcome, including optimizer refusal and crashes.

    Outcomes: pass | noop | FAIL:<checks> | opt-error | env-error |
    non-preserving | precondition. Only FAIL is a legality counterexample; the
    three non-FAIL failure outcomes each require recorded evidence.
    """
    if task['suite'] == 'P4':
        return evaluate_frontend(task)
    case, tc, runtime = task['case'], task['tc'], task['runtime']
    major = tc['major']
    failure_id = cell_identity(task)
    result = {'version': VERSION, 'id': failure_id, 'case': case['id'], 'expect': case.get('expect', 'malformed'),
              'path': case['path'], 'major': major, 'suite': task['suite'], 'mode': task['mode'],
              'pipeline': task['pipeline'], 'opt_args': task.get('opt_args', []), 'seed': task.get('seed'), 'sequence': task.get('sequence'),
              'outcome': None, 'checks': [], 'details': {}, 'observations': [], 'l3_static': []}
    error = case.get('error') or case.get('majors', {}).get(str(major), {}).get('error')
    if error:
        result.update(outcome='opt-error', details={'case-error': error})
        return result
    base = case['majors'][str(major)]
    baseline_module = base['module']
    directory = RAW / 'cells' / failure_id
    directory.mkdir(parents=True, exist_ok=True)
    input_module = task.get('input_module', baseline_module)
    result['input_module'] = input_module
    result['baseline_module'] = baseline_module
    r = command([tc['opt'], *task.get('opt_args', []), '-passes=' + task['pipeline'], input_module['bc'], '-o', directory / 'output.bc'], directory, 'opt')
    result['opt_command'] = r
    if not successful(r):
        result.update(outcome='opt-error', details={'opt': {'exit': r['returncode'], 'timeout': r['timeout'], 'stderr': r['stderr'],
                                                            'excerpt': pathlib.Path(r['stderr']).read_text(errors='replace')[:600]}})
        # Keep exact input and task even when opt failed: useful for optimizer bugs.
        atomic_json(directory / 'task.json', task)
        atomic_json(directory / 'result.json', result)
        return result
    transformed = publish_module(directory / 'output.bc', tc)
    (directory / 'output.bc').unlink()
    result['transformed'] = transformed
    post = immutable_text(transformed['ll'])
    pre_input = immutable_text(input_module['ll'])
    explained = []  # (check, item) pairs that an env rule accounts for

    def add(check, item, env=False):
        result['details'].setdefault(check, []).append(item)
        if env:
            explained.append((check, item))

    # Compare to raw baseline too: otherwise O3-introduced attributes escape the
    # post-O3 half of P1. Preserve immediate pre/post attribution separately.
    analysis = static_analysis(baseline_module, transformed)
    attrs = analysis['l2']
    immediate = static_analysis(input_module, transformed)
    result['observations'] = attrs['observations']
    result['preexisting_forbidden'] = attrs['preexisting_forbidden']
    if attrs['forbidden_added']:
        result['details']['L2'] = attrs['forbidden_added']
        result['details']['L2-immediate'] = immediate['l2']['forbidden_added']
    result['l3_static'] = analysis['l3']
    result['l6'] = immediate['l6']
    n = native(transformed, tc, runtime, case['inputs'], execution_timeout=task.get('execution_timeout', 10))
    result['native'] = {k: {'ok': v['ok'], 'stage': v['stage'], 'trace': v.get('trace'),
                          'commands': [c['command'] for c in v['commands']]} for k, v in n.items()}
    bn = base['native']
    baseline_trace = immutable_text(bn['trace']) if bn['ok'] else ''
    wanted_markers = set(called_markers(baseline_trace))
    diffs = []
    env = []
    for level in ('O0', 'O3'):
        current = n[level]
        missing = sorted(wanted_markers - set(current.get('undefined_markers', []))) if 'undefined_markers' in current else None
        if missing:
            add('L5', {'level': level, 'missing_marker_externals': missing})
        if not current['ok']:
            # Classify from the complete tool stderr, never from an excerpt.
            diagnostic = pathlib.Path(current['diagnostic_path']).read_text(errors='replace')
            evidence = env_evidence_llc(diagnostic, post) if current['stage'] == 'llc' else env_evidence_link(diagnostic, post)
            if evidence and not missing:
                env.append({'level': level, 'stage': current['stage'], **evidence})
            add('L5', f'{level}: native build failed at {current["stage"]}', env=bool(evidence and not missing))
            continue
        trace = immutable_text(current['trace'])
        if not bn['ok'] or trace != baseline_trace or current['exit'] != 0 or current['timeout']:
            add('L1' if level == 'O0' else 'L5', f'{level}: trace/result differs or execution failed (exit={current["exit"]}, timeout={current["timeout"]})')
            diffs.extend(difflib.unified_diff(baseline_trace.splitlines(True), trace.splitlines(True), fromfile='baseline-O0', tofile='transformed-' + level))
        l3 = dynamic_l3(trace)
        if l3:
            add('L3', {'level': level, 'finding': l3})
        for issue in check_l4(baseline_trace, trace, post):
            add('L4', issue)
    if not case['cross_major_agreement']:
        add('L1', 'baseline cross-major disagreement or unavailable baseline')
    result['checks'] = [k for k in ('L1', 'L2', 'L3', 'L4', 'L5') if k in result['details']]
    if result['checks'] and not immediate['l2']['forbidden_added']:
        source = native(input_module, tc, runtime, case['inputs'], execution_timeout=task.get('execution_timeout', 10))
        if behaviour(n, baseline_trace, post) == behaviour(source, baseline_trace, pre_input):
            # The pass changed nothing observable relative to its own input; the
            # failure belongs to the input (default<O3> output, or the untouched
            # module under llc -O3). Still FAIL; the report groups these.
            result['inherited'] = {'from': 'default<O3> output' if task['mode'] == 'post-O3' else 'untransformed input',
                                   'input_hash': input_module['hash']}
    all_items = [(k, item) for k in result['checks'] for item in result['details'][k]]
    single = single_pass_name(task['pipeline']) if task['suite'] in ('P1', 'reduction') and not task.get('opt_args') else None
    if not result['checks']:
        # Noop is a classification only after every check, including native O3.
        result['outcome'] = 'noop' if transformed['hash'] == input_module['hash'] else 'pass'
    elif env and len(explained) == len(all_items):
        result.update(outcome='env-error', env_evidence=env)
    elif single in NON_PRESERVING and NON_PRESERVING[single][1](pre_input, post):
        result.update(outcome='non-preserving', non_preserving={'pass': single, 'rationale': NON_PRESERVING[single][0],
                                                                 'markers_renamed': _markers_renamed(pre_input, post)})
    elif task['suite'] == 'P1' and not task.get('opt_args') and (pre := precondition_for(task['pipeline'], major)):
        pre.update(raw_checks=result['checks'], violated=prerequisites_change_input(case, tc, pre, input_module),
                   has_switch=bool(re.search(r'^\s+switch\s', pre_input, re.M)))
        if pre['violated']:
            rerun = evaluate(dict(task, suite='precondition-rerun', pipeline=pre['pipeline']))
            pre['rerun'] = {'id': rerun['id'], 'pipeline': rerun['pipeline'], 'outcome': rerun['outcome'], 'checks': rerun['checks']}
        result['precondition'] = pre
        result['outcome'] = 'precondition' if pre.get('rerun', {}).get('outcome') in ('pass', 'noop') else 'FAIL:' + ','.join(result['checks'])
    else:
        result['outcome'] = 'FAIL:' + ','.join(result['checks'])
    if result['checks']:
        if result['outcome'].startswith('FAIL') or result['outcome'] == 'precondition':
            shutil.copyfile(transformed['ll'], directory / 'transformed.ll')
            (directory / 'trace.diff').write_text(''.join(diffs) or 'No trace difference; see result.json for static/native diagnostics.\n')
        atomic_json(directory / 'task.json', task)
        atomic_json(directory / 'result.json', result)
        result['artifacts'] = str(directory)
    else:
        # Logs for successful tools are redundant; immutable module/native caches
        # contain the commands needed to inspect any accepted result.
        shutil.rmtree(directory)
    return result


def evaluate_frontend(task):
    """Clang-18 LTO through lld, with system cc compiling runtime and linking."""
    case, tc, runtime = task['case'], task['tc'], task['runtime']
    fid = digest(json.dumps([VERSION, case['source_hash'], 'P4', runtime['key']]))[:20]
    directory = RAW / 'cells' / fid
    directory.mkdir(parents=True, exist_ok=True)
    result = {'version': VERSION, 'id': fid, 'case': case['id'], 'expect': case.get('expect'),
              'path': case['path'], 'major': 18, 'suite': 'P4', 'mode': 'clang-O3-LTO',
              'pipeline': 'clang-18 -O3 -flto; system cc + lld --lto-O3',
              'outcome': 'opt-error', 'checks': [], 'details': {}, 'observations': [], 'l3_static': []}
    error = case.get('error') or case.get('majors', {}).get('18', {}).get('error')
    if error:
        result['details']['case-error'] = error
        return result
    bindir = pathlib.Path(tc['opt']).parent
    clang = bindir / 'clang'
    config = tomllib.loads((ROOT / 'toolchains.toml').read_text())
    llds = [bindir / 'ld.lld', pathlib.Path(config['llvm20']['bin']) / 'ld.lld']
    lld = next((p for p in llds if p.is_file()), None)
    if not clang.is_file() or lld is None:
        result['details']['tool-error'] = 'P4 requires clang-18 and ld.lld (18 or 20)'
        return result
    r = command([clang, '-O3', '-flto', '-c', '-I', ROOT, '-I', (ROOT / case['path']).parent,
                 case['source'], '-o', directory / 'frontend.o'], directory, 'clang-lto')
    result['opt_command'] = r
    if not successful(r):
        result['details']['frontend'] = r
        return result
    emitted = publish_module(directory / 'frontend.o', tc)
    base = case['majors']['18']
    pre, post = pathlib.Path(base['module']['ll']).read_text(), pathlib.Path(emitted['ll']).read_text()
    attrs = check_l2(pre, post)
    result['observations'] = attrs['observations']
    result['l3_static'] = check_l3_static(pre, post)
    if attrs['forbidden_added']:
        result['details']['L2'] = attrs['forbidden_added']
    # lld consumes LLVM bitcode directly; -B selects it while cc performs the
    # system startup/library link. Save post-LTO IR for L2/L3/L4 inspection.
    r = command(['cc', '-B' + str(lld.parent), '-fuse-ld=lld', '-no-pie', '-rdynamic',
                 directory / 'frontend.o', *runtime['objects'], '-ldl',
                 '-Wl,--lto-O3,--save-temps', '-o', directory / 'frontend.exe'], directory, 'lto-link', timeout=60)
    result['link_command'] = r
    if not successful(r):
        result['details']['L5'] = ['LTO native link failed']
    else:
        symbols = executable_symbols(directory / 'frontend.exe', tc['llvm-nm'], directory, 'lto-symbols')
        execution = execute_inputs(directory / 'frontend.exe', case['inputs'], directory, 'lto-execute')
        baseline_trace = pathlib.Path(base['native']['trace']).read_text()
        trace = canonicalize_trace(pathlib.Path(execution['trace']).read_text(), symbols)
        (directory / 'lto-execute.canonical.trace').write_text(trace)
        if trace != baseline_trace or execution['exit'] or execution['timeout']:
            result['details']['L1'] = ['front-end/LTO trace mismatch or execution failure']
            result['details']['L5'] = ['front-end/LTO trace mismatch or execution failure']
        if dynamic_l3(trace):
            result['details']['L3'] = dynamic_l3(trace)
        optimized = list(directory.glob('*.0.4.opt.bc'))
        if optimized:
            final_tc = tc if lld.parent == bindir else tools_for([20])[20]
            final_module = publish_module(optimized[0], final_tc)
            post = pathlib.Path(final_module['ll']).read_text()
            final_attrs = check_l2(pre, post)
            result['observations'] += final_attrs['observations']
            result['l3_static'] += check_l3_static(pre, post)
            if final_attrs['forbidden_added']:
                result['details']['L2'] = final_attrs['forbidden_added']
            result['transformed'] = final_module
        l4 = check_l4(baseline_trace, trace, post)
        if l4:
            result['details']['L4'] = l4
        obj = directory / 'frontend.exe.lto.o'
        if obj.exists():
            _, undefined = undefined_markers_in(obj, tc, directory, 'lto-nm')
            if set(called_markers(baseline_trace)) - set(undefined):
                result['details']['L5'] = ['LTO object missing baseline marker externals']
        else:
            result['details']['L5'] = ['lld did not retain the native LTO object for nm']
        (directory / 'trace.diff').write_text(''.join(difflib.unified_diff(baseline_trace.splitlines(True), trace.splitlines(True))))
    result['checks'] = [x for x in ('L1', 'L2', 'L3', 'L4', 'L5') if x in result['details']]
    result['outcome'] = 'FAIL:' + ','.join(result['checks']) if result['checks'] else 'pass'
    result['artifacts'] = str(directory)
    (directory / 'transformed.ll').write_text(post)
    atomic_json(directory / 'task.json', task)
    atomic_json(directory / 'result.json', result)
    return result


P2 = [f'default<{x}>' for x in ('O0', 'O1', 'O2', 'O3', 'Os', 'Oz')] + [
    'lto-pre-link<O3>', 'lto<O3>', 'thinlto-pre-link<O3>', 'thinlto<O3>',
    'default<O3>,default<O3>,default<O3>']


def pass_catalog(tc):
    directory = RAW / 'toolchains' / str(tc['major'])
    r = required_command([tc['opt'], '--print-passes'], directory, 'print-passes')
    required_command([tc['opt'], '--version'], directory, 'version')
    passes = parse_passes(pathlib.Path(r['stdout']).read_text())
    atomic_json(directory / 'passes.json', passes)
    return passes


def run_tasks(tasks, pool, stream, results):
    start = time.monotonic()
    total = len(tasks)
    counts = collections.Counter()
    # Bounded outstanding work prevents 100k futures from retaining all snapshots.
    iterator = iter(tasks)
    pending = {}
    def submit():
        try:
            task = next(iterator)
        except StopIteration:
            return False
        pending[pool.submit(evaluate, task)] = task
        return True
    for _ in range(min(total, 48)):
        submit()
    finished = 0
    last = start
    while pending:
        done, _ = concurrent.futures.wait(pending, timeout=5, return_when=concurrent.futures.FIRST_COMPLETED)
        for future in done:
            task = pending.pop(future)
            # An internal harness exception is loud and stops the run; never
            # downgrade an unknown exception into a legality pass or opt-error.
            result = future.result()
            stream.write(json.dumps(result, sort_keys=True) + '\n')
            stream.flush()
            results.append(result)
            counts[result['outcome'].split(':')[0]] += 1
            finished += 1
            submit()
        now = time.monotonic()
        if now - last >= 20 or finished == total:
            print(f'  {finished}/{total} cells in {now-start:.1f}s {dict(counts)}', flush=True)
            last = now
    return counts


P3_EXCLUDED_OUTCOMES = ('opt-error', 'env-error', 'non-preserving', 'precondition')


def p1_variants(passes):
    """Extra documented P1 cells. The bare cells are always kept as well."""
    names = {p['name']: p for p in passes}
    out = []
    if 'internalize' in names:
        # Bare internalize internalises @case_entry; the API list is how every
        # real user (LTO linkers) runs it.
        out.append(dict(names['internalize'], opt_args=['-internalize-public-api-list=case_entry'], variant='api-list'))
    if 'instcombine' in names:
        # instcombine's fixpoint verification aborts opt on some inputs; the
        # transformation itself is still worth checking.
        out.append(dict(names['instcombine'], pipeline='function(instcombine<no-verify-fixpoint>)', variant='no-verify-fixpoint'))
    return out


def task_for(case, tc, runtime, suite, pipeline, mode='raw', **extra):
    return dict(case=case, tc=tc, runtime=runtime, suite=suite, pipeline=pipeline, mode=mode, **extra)


def matrix(args, tcs, runtime, cases):
    run_id = time.strftime('%Y%m%dT%H%M%S') + f'-{os.getpid()}'
    run_dir = RAW / 'runs' / run_id
    run_dir.mkdir(parents=True)
    atomic_json(run_dir / 'manifest.json', {'version': VERSION, 'args': vars(args), 'cases': cases, 'toolchains': tcs, 'runtime': runtime})
    all_results = []
    with (run_dir / 'outcomes.jsonl').open('w') as stream, concurrent.futures.ProcessPoolExecutor(max_workers=args.jobs) as pool:
        for major, tc in tcs.items():
            passes = pass_catalog(tc)
            if args.p1_passes:
                passes = [p for p in passes if any(fnmatch.fnmatch(p['name'], g) or fnmatch.fnmatch(p['pipeline'], g) for g in args.p1_passes)]
                if not passes:
                    raise ValueError(f'--p1-passes matched no LLVM {major} pass')
            if 'P1' in args.suites:
                tasks = []
                for case in cases:
                    base = case.get('majors', {}).get(str(major), {})
                    optimized = None
                    if 'module' in base:
                        setup = evaluate(task_for(case, tc, runtime, 'setup', 'default<O3>'))
                        optimized = setup.get('transformed')
                        if optimized is None:
                            raise RuntimeError(f'default<O3> setup failed: {setup}')
                    for p in passes + p1_variants(passes):
                        extra = {'opt_args': p['opt_args']} if p.get('opt_args') else {}
                        tasks.append(task_for(case, tc, runtime, 'P1', p['pipeline'], **extra))
                        tasks.append(task_for(case, tc, runtime, 'P1', p['pipeline'], 'post-O3', **extra, **({'input_module': optimized} if optimized else {})))
                print(f'LLVM {major} P1: {len(passes)} passes, {len(tasks)} cells', flush=True)
                run_tasks(tasks, pool, stream, all_results)
            if 'P4' in args.suites and major == 18:
                selected = [c for c in cases if c['path'].endswith('.c')]
                if not selected:
                    raise ValueError('P4 requested, but no C cases were selected')
                tasks = [task_for(c, tc, runtime, 'P4', 'clang-O3-LTO') for c in selected]
                print(f'LLVM 18 P4: {len(tasks)} C front-end cells', flush=True)
                run_tasks(tasks, pool, stream, all_results)
            if 'P2' in args.suites:
                tasks = [task_for(c, tc, runtime, 'P2', p) for c in cases for p in P2]
                print(f'LLVM {major} P2: {len(tasks)} cells', flush=True)
                run_tasks(tasks, pool, stream, all_results)
            if 'P3' in args.suites:
                prior = [r for r in all_results if r['major'] == major and r['suite'] == 'P1']
                if not prior:
                    prior = [r for r in read_outcomes() if r['major'] == major and r['suite'] == 'P1' and r['case'] in {c['id'] for c in cases}]
                prior = [r for r in prior if not r.get('opt_args')]
                accepted = {r['pipeline'] for r in prior if r['outcome'] != 'opt-error'}
                # Exclude passes that, on any selected P1 input, were refused by opt
                # or were environment-incompatible, non-preserving by design or
                # precondition-violating: in a random sequence they would only
                # repeat that known outcome and hide what the other passes do.
                # Genuine FAIL passes stay eligible.
                rejected = {r['pipeline'] for r in prior if r['outcome'] in P3_EXCLUDED_OUTCOMES and 'case-error' not in r['details']}
                population = sorted(accepted - rejected)
                atomic_json(run_dir / f'p3-excluded-{major}.json', {p: sorted({r['outcome'] for r in prior if r['pipeline'] == p and r['outcome'] in P3_EXCLUDED_OUTCOMES}) for p in sorted(rejected)})
                if not population:
                    raise ValueError('P3 needs recorded successful P1 optimizer invocations; run P1 first')
                rng = random.Random(args.seed + major)
                sequences = [rng.choices(population, k=rng.randint(5, 40)) for _ in range(args.p3_seqs)]
                atomic_json(run_dir / f'p3-{major}.json', {'seed': args.seed, 'effective_seed': args.seed + major, 'population': population, 'sequences': sequences})
                tasks = [task_for(c, tc, runtime, 'P3', ','.join(seq), mode=f'seq-{i:04d}', seed=args.seed, sequence=seq) for c in cases for i, seq in enumerate(sequences)]
                print(f'LLVM {major} P3: {len(population)} eligible passes, {len(tasks)} cells', flush=True)
                run_tasks(tasks, pool, stream, all_results)
    atomic_json(run_dir / 'complete.json', {'cells': len(all_results), 'counts': dict(collections.Counter(r['outcome'].split(':')[0] for r in all_results))})
    print(f'Recorded {len(all_results)} cells: {run_dir}', flush=True)
    return all_results


def read_outcomes():
    # A rerun replaces the same logical cell; retain every raw historical record.
    latest = {}
    for path in sorted((RAW / 'runs').glob('*/outcomes.jsonl')):
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r.get('version') != VERSION:
                continue
            key = (r['case'], r['major'], r['suite'], r['mode'], r['pipeline'] if r['suite'] != 'P3' else '<recorded-sequence>', tuple(r.get('opt_args') or ()))
            latest[key] = r
    return list(latest.values())


def controls(args, tcs, runtime):
    cases = make_baselines(discover(['control-*']), tcs, runtime)
    for major, tc in tcs.items():
        records = []
        for c in cases:
            pipeline = {'control-memory-none': 'default<O3>',
                        'control-readonly': 'function(loop-simplify,lcssa,loop-mssa(licm))',
                        'control-handle-deref': 'no-op-module',
                        'control-region-twin': 'mergefunc'}[c['id']]
            r = evaluate(task_for(c, tc, runtime, 'control', pipeline))
            if c['id'] == 'control-region-twin':
                pre = pathlib.Path(c['majors'][str(major)]['module']['ll']).read_text()
                post = pathlib.Path(r['transformed']['ll']).read_text() if 'transformed' in r else ''
                r['mergefunc_did_not_merge'] = canonical_ir(pre) == canonical_ir(post)
                if 'L4' not in r['checks'] and not r['mergefunc_did_not_merge']:
                    raise AssertionError(f'mergefunc changed IR but L4 did not fire: {r}')
            else:
                expected = 'L3' if c['id'] == 'control-handle-deref' else 'L1'
                if expected not in r['checks'] or not r['outcome'].startswith('FAIL'):
                    raise AssertionError(f'CONTROL UNEXPECTEDLY PASSED {c["id"]}, wanted FAIL with {expected}: {r}')
            records.append(r)
            print(f'control LLVM {major} {c["id"]}: {r["outcome"]}', flush=True)
        atomic_json(RAW / f'controls-{major}.json', records)
    return cases


def replay(failure_id):
    directory = RAW / 'cells' / failure_id
    if not (directory / 'task.json').exists():
        raise ValueError(f'no recorded failure {failure_id}')
    task = json.loads((directory / 'task.json').read_text())
    # Clear native cache entries for this module so replay executes codegen and
    # execution again, rather than accepting a cached observation.
    old = json.loads((directory / 'result.json').read_text())
    module = old.get('transformed')
    if module:
        key = native_key(task['tc'], task['runtime'], module, task['case']['inputs'], task.get('execution_timeout', 10))
        with locked(RAW / 'native' / key / 'lock'):
            (RAW / 'native' / key / 'native.json').unlink(missing_ok=True)
    result = evaluate(task)
    print(json.dumps(result, indent=2))
    return result


def audit():
    """Recheck retained static evidence after checker fixes, without a full rerun."""
    contexts = {}
    for manifest_path in sorted((RAW / 'runs').glob('*/manifest.json')):
        manifest = json.loads(manifest_path.read_text())
        if 'cases' not in manifest or 'toolchains' not in manifest:
            continue
        for case in manifest['cases']:
            for major, base in case.get('majors', {}).items():
                if base.get('module'):
                    contexts[(case['id'], int(major), base['module']['hash'])] = (case, manifest['toolchains'][major], manifest['runtime'])
    run_dir = RAW / 'runs' / (time.strftime('%Y%m%dT%H%M%S') + f'-audit-{os.getpid()}')
    run_dir.mkdir(parents=True)
    cache, changed, failures_changed = {}, 0, 0
    with (run_dir / 'outcomes.jsonl').open('w') as out:
        for r in read_outcomes():
            if not r.get('baseline_module') or not r.get('transformed'):
                continue
            key = (r['baseline_module']['ll'], r['transformed']['ll'])
            if key not in cache:
                a, b = pathlib.Path(key[0]).read_text(), pathlib.Path(key[1]).read_text()
                cache[key] = (check_l2(a, b), check_l3_static(a, b))
            attrs, l3 = cache[key]
            if attrs['forbidden_added'] != r['details'].get('L2', []):
                c, tc, rt = contexts[(r['case'], r['major'], r['baseline_module']['hash'])]
                task = task_for(c, tc, rt, r['suite'], r['pipeline'], r['mode'], input_module=r['input_module'], seed=r.get('seed'), sequence=r.get('sequence'))
                updated = evaluate(task)
                failures_changed += updated['outcome'] != r['outcome']
                r = updated
                changed += 1
            elif attrs['observations'] != r['observations'] or l3 != r['l3_static']:
                r.update(observations=attrs['observations'], l3_static=l3)
                changed += 1
            else:
                continue
            out.write(json.dumps(r, sort_keys=True) + '\n')
    meta = {'unique_ir_pairs_checked': len(cache), 'records_updated': changed, 'outcomes_changed': failures_changed}
    atomic_json(run_dir / 'complete.json', meta)
    print(json.dumps(meta, indent=2), flush=True)


def interesting(task_path, candidate):
    """llvm-reduce predicate: reduce pre-pass IR and rerun the actual pass."""
    task = json.loads(pathlib.Path(task_path).read_text())
    original = task.pop('reduction_original')
    tc, runtime = task['tc'], task['runtime']
    text = pathlib.Path(candidate).read_text()
    if not re.search(r'^define\s+.*?i64\s+@case_entry\(i64(?:\s+[^,()]*)?\)', text, re.M):
        return False
    directory = RAW / 'reduction-candidates' / digest(text + str(tc['major']))
    r = command([tc['llvm-as'], pathlib.Path(candidate).resolve(), '-o', directory / 'candidate.bc'], directory, 'assemble')
    if not successful(r):
        return False
    module = publish_module(directory / 'candidate.bc', tc)
    baseline = native(module, tc, runtime, task['case']['inputs'], (0,), execution_timeout=0.4)['O0']
    if not baseline['ok']:
        return False
    trace = pathlib.Path(baseline['trace']).read_text()
    target_checks = set(original['checks'])
    if 'L3' in target_checks and task['case']['id'] == 'control-handle-deref':
        return 'FAULT handle-deref' in trace
    baseline_l4 = check_l4(trace, trace, text)
    original_unresolved = any(x.get('reason') == 'region address resolves to no symbol start' for x in original['details'].get('L4', []))
    if baseline['exit'] or baseline['timeout'] or dynamic_l3(trace) or (baseline_l4 and not original_unresolved):
        return False
    case = dict(task['case'])
    case.update(source_hash=digest(text), cross_major_agreement=True)
    case['majors'] = {str(tc['major']): {'module': module, 'native': baseline, 'issues': {}}}
    task['case'] = case
    task.pop('input_module', None)
    if task['mode'] == 'post-O3':
        task['pipeline'] = 'default<O3>,' + task['pipeline']
    task.update(mode='reduce', suite='reduction', execution_timeout=0.4)
    result = evaluate(task)
    if set(result['checks']) != target_checks:
        return False
    if 'L2' in target_checks:
        wanted = {(s['marker'], s['attribute']) for s in original['details']['L2']}
        actual = {(s['marker'], s['attribute']) for s in result['details']['L2']}
        if not wanted <= actual:
            return False
    return True


def minimize(failure_id, seconds):
    directory = RAW / 'cells' / failure_id
    task_file, result_file = directory / 'task.json', directory / 'result.json'
    if not task_file.exists() or not result_file.exists():
        raise ValueError(f'failure not found: {failure_id}')
    task, original = json.loads(task_file.read_text()), json.loads(result_file.read_text())
    if not original['checks']:
        raise ValueError('minimize requires a failed check, not an optimizer refusal')
    task['reduction_original'] = original
    reduction_task = directory / 'reduction-task.json'
    atomic_json(reduction_task, task)
    reducer = pathlib.Path(task['tc']['opt']).parent / 'llvm-reduce'
    if not reducer.is_file():
        reducer = pathlib.Path(tools_for([18])[18]['opt']).parent / 'llvm-reduce'
    source = pathlib.Path(task['case']['source'])
    if source.suffix == '.c':
        source = source.with_suffix('.ll')
    candidate = directory / 'reduction-input.ll'
    shutil.copyfile(source, candidate)
    if not interesting(reduction_task, candidate):
        meta = {'status': 'not-interesting', 'reason': 'original input does not reproduce under reduction predicate', 'source': str(source)}
        atomic_json(directory / 'reduction.json', meta)
        return meta
    r = command([reducer, '--test=' + sys.executable, '--test-arg=' + str(pathlib.Path(__file__).resolve()),
                 '--test-arg=interesting', '--test-arg=' + str(reduction_task),
                 '--max-pass-iterations=1', '--delta-passes=functions,basic-blocks,instructions,attributes',
                 candidate, '-o', directory / 'reduced.ll'], directory, 'llvm-reduce', timeout=seconds,
                env_override={'BENNETT_REDUCER_CHILD': '1'})
    reduced = directory / 'reduced.ll'
    valid = reduced.exists() and interesting(reduction_task, reduced)
    meta = {'status': 'reproduced' if valid else 'incomplete', 'command': r,
            'input_bytes': candidate.stat().st_size, 'output_bytes': reduced.stat().st_size if reduced.exists() else None,
            'verified_same_checks': valid, 'output': str(reduced), 'bounded_seconds': seconds}
    atomic_json(directory / 'reduction.json', meta)
    print(json.dumps({'id': failure_id, **meta}, indent=2), flush=True)
    return meta


OUTCOMES = ('pass', 'FAIL', 'noop', 'opt-error', 'env-error', 'non-preserving', 'precondition')
CONTROL_INTENT = {'control-memory-none': ('L1', 'default<O3>'), 'control-readonly': ('L1', 'function(loop-simplify,lcssa,loop-mssa(licm))'),
                  'control-handle-deref': ('L3', 'no-op-module'), 'control-region-twin': ('L4', 'mergefunc')}


def group_of(r):
    return 'corpus' if r['path'].startswith('cases/') else 'control' if r['path'].startswith('controls/') else 'seed'


def outcome_kind(r):
    return r['outcome'].split(':')[0]


def _slim(r):
    # Keep the report's working set small: drop per-level command vectors.
    r = dict(r)
    r.pop('native', None)
    if r.get('opt_command'):
        r['opt_command'] = {'command': r['opt_command']['command'], 'stderr': r['opt_command']['stderr']}
    return r


def _cell_dir(r):
    return RAW / 'cells' / r['id']


def _diff_head(r, lines=14):
    path = _cell_dir(r) / 'trace.diff'
    if not path.exists():
        return ''
    out = path.read_text(errors='replace').splitlines()
    return '\n'.join(out[:lines]) + ('\n...' if len(out) > lines else '')


def _diagnose(r):
    d = r['details']
    bits = []
    for issue in d.get('L4', []):
        if isinstance(issue, dict):
            if issue['reason'] == 'region is a forwarding thunk':
                bits.append(f'region {issue["symbol"]} became a forwarding thunk to {issue["target"]}')
            elif issue['reason'] == 'region symbol sequence changed':
                before, after = issue['before'], issue['after']
                changed = [(a, b) for a, b in zip(before, after) if a != b]
                bits.append('region symbols changed ' + (', '.join(f'{a}->{b}' for a, b in sorted(set(changed))[:3]) if changed else f'(count {len(before)}->{len(after)})'))
            else:
                bits.append(f'{issue["reason"]}: {issue.get("symbol")}')
    for issue in d.get('L2', []):
        bits.append(f'added forbidden {issue["attribute"]} on {issue["marker"]} {issue["kind"]}')
    for issue in d.get('L3', []):
        bits.append(f'dynamic L3 {issue["finding"]} at {issue["level"]}')
    for issue in d.get('L5', []):
        if isinstance(issue, dict) and 'missing_marker_externals' in issue:
            bits.append(f'{issue["level"]} object lacks marker externals {",".join(issue["missing_marker_externals"])}')
        elif isinstance(issue, str) and 'native build failed' in issue:
            bits.append(issue)
    if 'L1' in d or any(isinstance(x, str) and 'trace/result differs' in x for x in d.get('L5', [])):
        diff = [l for l in _diff_head(r, 400).splitlines() if l[:1] in '+-' and not l.startswith(('+++', '---'))]
        if diff:
            bits.append('first trace difference: ' + ' / '.join(diff[:2]))
        else:
            bits.extend(x for x in d['L1'] if isinstance(x, str))
    seen, out = set(), []
    for b in bits:
        if b not in seen:
            seen.add(b)
            out.append(b)
    return '; '.join(out[:4])


def _majors(rows):
    return ','.join(str(m) for m in sorted({r['major'] for r in rows}))


def _md(text):
    return str(text).replace('|', '&#124;').replace('\n', ' ')


def report():
    rows = [_slim(r) for r in read_outcomes()]
    if not rows:
        raise ValueError('no v3 outcomes recorded; run the matrix first')
    # L6 is an observation; recompute it from retained IR with the current
    # classifier so a checker fix never leaves stale cached shapes in the report.
    l6_cache = {}
    for r in rows:
        if r.get('transformed') and r.get('input_module'):
            key = (r['input_module']['ll'], r['transformed']['ll'])
            if key not in l6_cache:
                l6_cache[key] = check_l6(immutable_text(key[0]), immutable_text(key[1]))
            r['l6'] = l6_cache[key]
    majors = sorted({r['major'] for r in rows})
    suites = [x for x in ('P1', 'P2', 'P3', 'P4') if any(r['suite'] == x for r in rows)]
    groups = {g: [r for r in rows if group_of(r) == g] for g in ('corpus', 'seed', 'control')}
    def table(selected):
        t = {}
        for m in majors:
            for su in suites:
                cell = collections.Counter(outcome_kind(r) for r in selected if r['major'] == m and r['suite'] == su)
                if cell:
                    t[f'{m}/{su}'] = {k: cell.get(k, 0) for k in OUTCOMES}
        return t
    corpus_table, seed_table = table(groups['corpus']), table(groups['seed'])
    corpus_cases = sorted({r['case'] for r in groups['corpus']})

    # Controls: detected yes/no per check, from the designated pipeline record.
    control_records = {}
    for path in sorted(RAW.glob('controls-*.json')):
        for r in json.loads(path.read_text()):
            if r.get('version') == VERSION:
                control_records[(r['case'], r['major'])] = r
    controls_view = []
    for case, (check, pipeline) in sorted(CONTROL_INTENT.items()):
        entry = {'case': case, 'intended_check': check, 'pipeline': pipeline, 'detected': {}}
        for m in majors:
            r = control_records.get((case, m))
            entry['detected'][str(m)] = None if r is None else {c: c in r['checks'] for c in ('L1', 'L2', 'L3', 'L4', 'L5')} | {'outcome': r['outcome']}
        matrix_cells = [r for r in groups['control'] if r['case'] == case]
        entry['matrix_cells'] = len(matrix_cells)
        entry['matrix_cells_detecting_intended'] = sum(check in r['checks'] for r in matrix_cells)
        controls_view.append(entry)

    # P2 per pipeline per case (all groups, corpus first).
    p2 = collections.defaultdict(dict)
    for r in rows:
        if r['suite'] == 'P2':
            p2[(group_of(r), r['case'])].setdefault(r['pipeline'], {})[str(r['major'])] = r['outcome']

    # Distinct FAILs: case + pass (+opt args) + check signature; majors/modes merged.
    p1_fail_passes = collections.defaultdict(set)
    for r in rows:
        if r['suite'] == 'P1' and outcome_kind(r) == 'FAIL' and not r.get('inherited') and not r.get('opt_args'):
            p1_fail_passes[(r['case'], r['major'])].add(r['pipeline'])
    def explaining(r):
        return tuple(sorted({p for p in r['sequence'] if p in p1_fail_passes[(r['case'], r['major'])]}))
    def fail_key(r):
        if r.get('inherited'):
            return (r['case'], 'inherited', r['inherited']['from'], tuple(r['checks']))
        if r['suite'] == 'P3':
            # Sequences containing passes that FAIL alone on this case are grouped
            # under those passes; the rest are individual interaction findings.
            return (r['case'], 'P3', 'explained' if explaining(r) else r['mode'], tuple(r['checks']))
        return (r['case'], r['suite'], pipeline_label(r), tuple(r['checks']))
    distinct = collections.OrderedDict()
    for r in sorted((r for r in rows if outcome_kind(r) == 'FAIL'), key=lambda r: (group_of(r) != 'corpus', r['case'], r['suite'], pipeline_label(r), r['major'], r['mode'])):
        distinct.setdefault((group_of(r),) + fail_key(r), []).append(r)
    fail_entries = []
    for key, members in distinct.items():
        first = members[0]
        if first.get('inherited'):
            label = f'(any pass; behaviour identical to its input = {first["inherited"]["from"]}; {len({(r["suite"], pipeline_label(r), r["mode"]) for r in members})} pass/mode cells)'
        elif first['suite'] == 'P3' and explaining(first):
            counts = collections.Counter(p for r in members for p in explaining(r))
            label = f'{len(members)} random sequences, each containing a pass that FAILs alone on this case (' + ', '.join(f'{p} {n}' for p, n in counts.most_common()) + ')'
        else:
            label = pipeline_label(first) if first['suite'] != 'P3' else f'{first["mode"]} ({len(first["sequence"])} passes)'
        entry = {'group': key[0], 'case': first['case'], 'expect': first['expect'], 'suite': first['suite'] if not first.get('inherited') else 'inherited',
                 'inherited': bool(first.get('inherited')), 'suites': sorted({r['suite'] for r in members}),
                 'pass': label,
                 'checks': list(first['checks']), 'majors': sorted({r['major'] for r in members}),
                 'modes': sorted({r['mode'] for r in members}), 'cells': [r['id'] for r in members],
                 'diagnosis': _diagnose(first), 'reproduce': {'opt': first.get('opt_command', {}).get('command'),
                                                              'replay': f'python3 corpus/legality/harness/run.py replay {first["id"]}'},
                 'trace_diff_head': _diff_head(first)}
        if first['suite'] == 'P3':
            entry['sequence'] = first['sequence']
            entry['contains_p1_failing_passes'] = sorted({p for r in members for p in explaining(r)})
            entry['interaction'] = not explaining(first)
        fail_entries.append(entry)

    # L2 observations (non-forbidden additions), by attribute and pass.
    l2_obs = collections.defaultdict(lambda: collections.defaultdict(set))
    for r in rows:
        for o in r['observations']:
            l2_obs[o['attribute']][pipeline_label(r) if r['suite'] != 'P3' else 'P3 sequences'].add(r['major'])
    # L3 static review flags, separated by outcome family.
    l3 = {'legality-relevant': collections.defaultdict(set), 'env-error/non-preserving': collections.defaultdict(set)}
    for r in rows:
        if r['l3_static']:
            bucket = 'env-error/non-preserving' if outcome_kind(r) in ('env-error', 'non-preserving') else 'legality-relevant'
            for f in r['l3_static']:
                l3[bucket][(group_of(r), r['case'], pipeline_label(r) if r['suite'] != 'P3' else r['mode'], f['function'], f['opcode'])].add(r['major'])
    # L6 shapes: shape x introducing pass; every `other` site is a finding.
    l6_intro = collections.defaultdict(lambda: collections.defaultdict(set))
    l6_other = collections.defaultdict(set)
    l6_present = collections.Counter()
    for r in rows:
        l6 = r.get('l6') or {}
        for sh in l6.get('shapes', []):
            l6_present[sh] += 1
        label = pipeline_label(r) if r['suite'] != 'P3' else 'P3 sequences'
        for i in l6.get('introduced', []):
            l6_intro[i['shape']][label].add(r['major'])
        new_other = {(i['marker'], i['operand']) for i in l6.get('introduced', []) if i['shape'] == 'other'}
        for o in l6.get('other', []):
            if (o['marker'], o['operand']) in new_other:
                l6_other[(group_of(r), r['case'], o['marker'], o['operand'], o.get('value', ''), r['suite'], label if r['suite'] != 'P3' else 'P3')].add(r['major'])
    baseline_cases = json.loads((RAW / 'baseline.json').read_text()) if (RAW / 'baseline.json').exists() else []
    baseline_shapes = collections.defaultdict(set)
    baseline_other = collections.defaultdict(set)
    for c in baseline_cases:
        for m, b in c.get('majors', {}).items():
            if 'module' in b:
                for site in region_operand_shapes(pathlib.Path(b['module']['ll']).read_text()):
                    baseline_shapes[site['shape']].add(c['id'])
                    if site['shape'] == 'other':
                        baseline_other[(c['id'], site['function'], site['marker'], site['operand'], site['detail'])].add(m)
    # Non-FAIL failure outcomes with evidence.
    env_groups = collections.defaultdict(list)
    for r in rows:
        if r['outcome'] == 'env-error':
            for e in r['env_evidence']:
                env_groups[(e['rule'], r['major'], pipeline_label(r) if r['suite'] != 'P3' else 'P3', e['stage'],
                            ','.join(sorted({re.sub(r'\d+$', 'N', u) for u in e.get('undefined', e.get('intrinsics', []))}))[:300])].append(r['id'])
    env_counts = {g: collections.Counter(e['rule'] for r in groups[g] if r['outcome'] == 'env-error' for e in r['env_evidence'][:1]) for g in groups}
    nonpres = collections.defaultdict(list)
    for r in rows:
        if r['outcome'] == 'non-preserving':
            nonpres[(r['non_preserving']['pass'], r['major'])].append(r['id'])
    precond = [r for r in rows if r['outcome'] == 'precondition']
    prefail = [r for r in rows if r.get('precondition') and outcome_kind(r) == 'FAIL' and not r.get('inherited')]
    for r in prefail:
        r['precondition'].setdefault('rerun', {'pipeline': '(not rerun: prerequisites leave the input unchanged)', 'outcome': 'n/a'})
    opt_errors = collections.defaultdict(list)
    for r in rows:
        if r['outcome'] == 'opt-error':
            opt_errors[(r['major'], pipeline_label(r) if r['suite'] != 'P3' else 'P3 ' + r['mode'])].append(r)
    baseline_view = [{'case': c['id'], 'error': c.get('error'), 'cross_major_agreement': c.get('cross_major_agreement'),
                      'issues': {m: b.get('issues', b.get('error')) for m, b in c.get('majors', {}).items()},
                      'llc_O3_differs': sorted(m for m, b in c.get('majors', {}).items() if b.get('llc_O3', {}).get('trace_equal') is False or b.get('llc_O3', {}).get('ok') is False)}
                     for c in baseline_cases]

    summary = {'version': VERSION, 'generated': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'total_cells': len(rows),
               'corpus_cases': corpus_cases, 'corpus_matrix': corpus_table, 'seed_matrix': seed_table, 'controls': controls_view,
               'p2': {f'{g}:{c}': v for (g, c), v in sorted(p2.items())},
               'distinct_failures': fail_entries,
               'l2_observations': {a: {p: sorted(m) for p, m in v.items()} for a, v in sorted(l2_obs.items())},
               'l3_static_review': {k: [{'group': g, 'case': c, 'pass': p, 'function': f, 'opcode': o, 'majors': sorted(m)} for (g, c, p, f, o), m in sorted(v.items())] for k, v in l3.items()},
               'l6': {'shapes_present_cells': dict(l6_present), 'baseline_shapes': {k: sorted(v) for k, v in baseline_shapes.items()},
                      'introduced': {sh: {p: sorted(m) for p, m in v.items()} for sh, v in sorted(l6_intro.items())},
                      'baseline_other': [{'case': c, 'function': f, 'marker': mk, 'operand': o, 'definition': d, 'majors': sorted(m)} for (c, f, mk, o, d), m in sorted(baseline_other.items())],
                      'other_findings': [{'group': g, 'case': c, 'marker': mk, 'operand': o, 'value': v, 'suite': su, 'pass': p, 'majors': sorted(m)}
                                         for (g, c, mk, o, v, su, p), m in sorted(l6_other.items())]},
               'env_error': {'counts_by_group_and_rule': {g: dict(v) for g, v in env_counts.items()},
                             'groups': [{'rule': k[0], 'major': k[1], 'pass': k[2], 'stage': k[3], 'symbols': k[4], 'cells': len(set(v)), 'example': v[0]}
                                        for k, v in sorted(env_groups.items())]},
               'non_preserving': [{'pass': k[0], 'major': k[1], 'cells': len(v), 'rationale': NON_PRESERVING[k[0]][0], 'example': v[0]} for k, v in sorted(nonpres.items())],
               'precondition': [{'case': r['case'], 'major': r['major'], 'mode': r['mode'], 'pipeline': r['pipeline'], 'raw_checks': r['precondition']['raw_checks'],
                                 'rerun': r['precondition']['rerun'], 'id': r['id']} for r in precond],
               'precondition_rerun_failed': [{'case': r['case'], 'major': r['major'], 'mode': r['mode'], 'pipeline': r['pipeline'], 'rerun': r['precondition']['rerun'], 'id': r['id']} for r in prefail],
               'opt_errors': [{'major': k[0], 'pass': k[1], 'cells': len(v), 'cases': sorted({r['case'] for r in v})[:8],
                               'command': v[0].get('opt_command', {}).get('command', v[0]['details'].get('case-error')),
                               'excerpt': (v[0]['details'].get('opt') or {}).get('excerpt', '')[:300]} for k, v in sorted(opt_errors.items())],
               'baseline': baseline_view}
    atomic_json(RESULTS / 'summary.json', summary)

    L = ['# Bennett legality spike results', '',
         f'Generated {summary["generated"]} by `{VERSION}`; {len(rows)} recorded matrix cells over {len(corpus_cases)} corpus cases '
         f'(plus {len({r["case"] for r in groups["seed"]})} harness seeds and {len({r["case"] for r in groups["control"]})} negative controls, reported separately).', '',
         'Outcomes: **FAIL** is the only legality counterexample. `env-error` (native build impossible in this standalone host environment, by the evidence rule in Harness notes), '
         '`non-preserving` (documented single passes that by design do not preserve a standalone program, confirmed per cell), and `precondition` '
         '(pass run without its documented prerequisite; rerun with the prerequisite passes) are recorded with evidence and never hide a trace difference, '
         'a guard fault, BADHANDLE, a forbidden attribute or a missing marker external. `noop` means identical IR after all checks pass.', '',
         '## 1. Corpus matrix (cases/ only)', '', '| LLVM / suite | ' + ' | '.join(OUTCOMES) + ' |', '|---|' + '---:|' * len(OUTCOMES)]
    for key, c in corpus_table.items():
        L.append(f'| {key} | ' + ' | '.join(str(c[k]) for k in OUTCOMES) + ' |')
    L += ['', 'Harness seeds (must be all pass/noop apart from env-error/non-preserving/precondition cells of instrumentation passes):', '',
          '| LLVM / suite | ' + ' | '.join(OUTCOMES) + ' |', '|---|' + '---:|' * len(OUTCOMES)]
    for key, c in seed_table.items():
        L.append(f'| {key} | ' + ' | '.join(str(c[k]) for k in OUTCOMES) + ' |')
    L += ['', '## 2. Negative controls (must be detected)', '', '| Control | intended | pipeline | ' + ' | '.join(f'LLVM {m}' for m in majors) + ' | matrix cells detecting intended check |',
          '|---|---|---|' + '---|' * len(majors) + '---|']
    for e in controls_view:
        cols = []
        for m in majors:
            d = e['detected'][str(m)]
            cols.append('not run' if d is None else ('detected: **yes**' if d[e['intended_check']] else 'detected: **NO**') + ' (' + ', '.join(f'{c}:{"yes" if d[c] else "no"}' for c in ('L1', 'L2', 'L3', 'L4', 'L5')) + ')')
        L.append(f'| `{e["case"]}` | {e["intended_check"]} | `{e["pipeline"]}` | ' + ' | '.join(cols) + f' | {e["matrix_cells_detecting_intended"]}/{e["matrix_cells"]} |')
    L += ['', '## 3. P2 standard pipelines, per case', '', 'Cell: `ok` = pass/noop on every major run; otherwise outcome per major.', '',
          '| Case | ' + ' | '.join(f'`{p}`' for p in P2) + ' |', '|---|' + '---|' * len(P2)]
    for (g, case), per in sorted(p2.items(), key=lambda kv: ({'corpus': 0, 'seed': 1, 'control': 2}[kv[0][0]], kv[0][1])):
        cols = []
        for pl in P2:
            o = per.get(pl, {})
            if not o:
                cols.append('-')
            elif all(v in ('pass', 'noop') for v in o.values()):
                cols.append('ok')
            else:
                cols.append('<br>'.join(f'{m}:{v}' for m, v in sorted(o.items()) if v not in ('pass', 'noop')))
        L.append(f'| {"" if g == "corpus" else g + " "}`{case}` | ' + ' | '.join(cols) + ' |')
    L += ['', f'## 4. Distinct FAILs ({len(fail_entries)})', '',
          'Deduplicated by case + pass + failed-check signature (P3: by case + sequence). Corpus first, then seeds, then controls (controls are expected to FAIL).', '']
    current = None
    for e in fail_entries:
        if e['group'] != current:
            current = e['group']
            L += [f'### {current}', '']
        L.append(f'- **`{e["case"]}`** ({e["expect"]}) — {e["suite"]} `{_md(e["pass"])}` — **{",".join(e["checks"])}** — LLVM {",".join(map(str, e["majors"]))}; modes {",".join(e["modes"])}; {len(e["cells"])} cells')
        if e.get('interaction'):
            L.append('  - **interaction**: no pass of this sequence FAILs alone on this case in P1')
        L.append(f'  - diagnosis: {_md(e["diagnosis"])}')

        L.append(f'  - reproduce: `{e["reproduce"]["replay"]}`; opt: `{_md(e["reproduce"]["opt"])}`')
        if e['trace_diff_head'].strip() and not e['trace_diff_head'].startswith('No trace difference'):
            L += ['  <details><summary>trace diff head</summary>', '', '  ```diff'] + ['  ' + x for x in e['trace_diff_head'].splitlines()] + ['  ```', '  </details>']
    L += ['', '## 5. L2 observations (added marker attributes that are not forbidden)', '']
    if not l2_obs:
        L.append('None.')
    for attr, per in sorted(l2_obs.items()):
        L.append(f'- `{attr}`: ' + ', '.join(f'`{_md(p)}` ({",".join(map(str, sorted(m)))})' for p, m in sorted(per.items())[:25]) + (f' … {len(per) - 25} more' if len(per) > 25 else ''))
    L += ['', '## 6. L3-static review flags (new ptrtoint/inttoptr in handle-touching functions; never automatic failures)', '']
    for bucket, flags in l3.items():
        L.append(f'### {bucket}: {len(flags)} distinct (case, pass, function, opcode)')
        L.append('')
        if bucket == 'env-error/non-preserving':
            per_pass = collections.Counter(k[2] for k in flags)
            L.append('By pass: ' + ', '.join(f'`{_md(p)}` {n}' for p, n in per_pass.most_common()) or 'none')
        else:
            for (g, c, p, f, o), m in sorted(flags.items()):
                L.append(f'- {g} `{c}` `{_md(p)}`: `{f}` gains `{o}` (LLVM {",".join(map(str, sorted(m)))})')
        L.append('')
    L += ['## 7. L6 region-operand shapes', '', 'Shapes present in baselines: ' + '; '.join(f'`{k}`: {len(v)} cases' for k, v in sorted(baseline_shapes.items())), '',
          '| Shape | passes that introduced it (majors) |', '|---|---|']
    for sh in L6_SHAPES:
        if sh in l6_intro:
            per = l6_intro[sh]
            L.append(f'| `{sh}` | ' + ', '.join(f'`{_md(p)}` ({",".join(map(str, sorted(m)))})' for p, m in sorted(per.items())) + ' |')
    L += ['', '### L6 `other` operands already present in the untransformed cases', '']
    for (c, f, mk, o, d), m in sorted(baseline_other.items()):
        L.append(f'- `{c}` in `{f}`: `{mk}` operand {o} = `{_md(d)}` (LLVM {",".join(sorted(m))})')
    L += ['', f'### L6 `other` introduced by a pass (findings: the plugin cannot resolve these statically): {len(l6_other)} distinct', '']
    for (g, c, mk, o, v, su, p), m in sorted(l6_other.items()):
        L.append(f'- {g} `{c}` {su} `{_md(p)}`: `{mk}` operand {o} = `{_md(v)}` (LLVM {",".join(map(str, sorted(m)))})')
    L += ['', '## 8. Harness notes', '', '### env-error rule and counts', '',
          'A native build failure is `env-error` only when (link) every line of the full ld stderr is an undefined/hidden reference to a symbol of an '
          'instrumentation runtime we do not link (prefixes `' + ENV_RUNTIME_SYMBOL.pattern[4:-1].replace('|', ' ') + '`), or the only non-runtime undefined symbol is '
          '`case_entry` and the transformed module has no externally visible `@case_entry` definition; or (llc) the module still calls '
          '`llvm.instrprof.*` intrinsics (they need the `instrprof` IR lowering pass, which llc does not run) and llc fails in instruction selection. '
          'In addition the object must still import every marker the baseline calls, every other check must pass, and no undefined `__bennett_*` symbol may appear.', '',
          'Counts (cells): ' + '; '.join(f'{g}: ' + ', '.join(f'{k} {v}' for k, v in sorted(c.items())) for g, c in env_counts.items() if c), '',
          '| rule | LLVM | pass | stage | symbols / intrinsics | cells |', '|---|---:|---|---|---|---:|']
    for g in summary['env_error']['groups']:
        L.append(f'| {g["rule"]} | {g["major"]} | `{_md(g["pass"])}` | {g["stage"]} | `{_md(g["symbols"][:120])}` | {g["cells"]} |')
    L += ['', '### non-preserving (documented list; rationale in harness/NOTES.md)', '']
    for e in summary['non_preserving']:
        L.append(f'- `{e["pass"]}` LLVM {e["major"]}: {e["cells"]} cells — {e["rationale"]}')
    L += ['', '### precondition', '']
    for e in summary['precondition']:
        L.append(f'- `{e["case"]}` LLVM {e["major"]} {e["mode"]} `{e["pipeline"]}`: raw run {",".join(e["raw_checks"])}; rerun `{e["rerun"]["pipeline"]}` → {e["rerun"]["outcome"]}')
    for e in summary['precondition_rerun_failed']:
        if e['rerun']['outcome'] == 'n/a':
            L.append(f'- FAIL, no precondition violation (prerequisite passes leave the input unchanged): `{e["case"]}` LLVM {e["major"]} {e["mode"]} `{e["pipeline"]}`')
        else:
            L.append(f'- FAIL even with prerequisites: `{e["case"]}` LLVM {e["major"]} {e["mode"]} `{e["pipeline"]}`; rerun `{e["rerun"]["pipeline"]}` → {e["rerun"]["outcome"]}')
    L += ['', '### opt-error (optimizer refused or crashed; not legality results)', '']
    for e in summary['opt_errors']:
        L.append(f'- LLVM {e["major"]} `{_md(e["pass"])}`: {e["cells"]} cells ({", ".join(e["cases"])}{"…" if e["cells"] > len(e["cases"]) else ""}); `{_md(e["excerpt"][:220])}`')
    L += ['', '### Baselines', '']
    bad = baseline_problems(baseline_cases)
    L.append(f'{len(baseline_cases)} baselines; cross-major agreement for all: {all(c.get("cross_major_agreement") for c in baseline_cases)}; problems: ' + ('; '.join(bad) if bad else 'none') + '.')
    differs = [f'`{c["case"]}` ({",".join(c["llc_O3_differs"])})' for c in baseline_view if c['llc_O3_differs']]
    L.append('')
    L.append('Untransformed module under `llc -O3` behaves differently from `llc -O0` (codegen-level finding; every cell of the case inherits it as L5): ' + (', '.join(differs) if differs else 'none') + '.')
    L += ['', '### Method', '',
          'Region pointers are printed by the runtime as raw addresses and resolved against the linked non-PIE executable\'s full symbol table '
          '(llvm-nm, local symbols included); `F:F?` now means the address is not the start of any symbol. Marker imports are checked with the matching '
          'major\'s llvm-nm (GNU nm misreads objects carrying a `.llvm.lto` section). `.c` cases are compiled with `clang-18 ' + ' '.join(C_FLAGS) + '`. '
          'P1 adds `internalize [-internalize-public-api-list=case_entry]` and `instcombine<no-verify-fixpoint>` cells beside the bare ones. '
          'P3 draws from P1 passes that were never opt-error/env-error/non-preserving/precondition on any selected case. '
          'Every cell has an exact record in raw/runs/*/outcomes.jsonl and, for every non-pass outcome, raw/cells/ID/result.json.']
    (RESULTS / 'REPORT.md').write_text('\n'.join(L) + '\n')
    print(json.dumps({'corpus_matrix': corpus_table, 'cells': len(rows), 'distinct_failures': len(fail_entries), 'report': str(RESULTS / 'REPORT.md')}, indent=1))


def main():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='subcommand', required=True)
    for name in ('baseline', 'matrix', 'controls'):
        p = subs.add_parser(name)
        p.add_argument('--majors', default='18,20,23')
        p.add_argument('--cases', action='append', help='glob of id, filename or legality-relative path; repeatable')
        p.add_argument('--jobs', type=int, default=12)
        if name == 'matrix':
            p.add_argument('--suites', default='P1,P2,P3')
            p.add_argument('--p3-seqs', type=int, default=200)
            p.add_argument('--seed', type=int, default=20261028)
            p.add_argument('--p1-passes', action='append', help='restrict P1 to passes matching this glob (re-evaluation); not with P3')
    subs.add_parser('report')
    subs.add_parser('audit')
    p = subs.add_parser('replay')
    p.add_argument('failure_id')
    p = subs.add_parser('minimize')
    p.add_argument('failure_id')
    p.add_argument('--seconds', type=int, default=30)
    p = subs.add_parser('interesting', help=argparse.SUPPRESS)
    p.add_argument('task_path')
    p.add_argument('candidate')
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    if args.subcommand == 'report':
        report()
        return
    if args.subcommand == 'audit':
        audit()
        report()
        return
    if args.subcommand == 'replay':
        replay(args.failure_id)
        return
    if args.subcommand == 'minimize':
        minimize(args.failure_id, args.seconds)
        return
    if args.subcommand == 'interesting':
        raise SystemExit(0 if interesting(args.task_path, args.candidate) else 1)
    majors = [int(x) for x in args.majors.split(',')]
    if len(set(majors)) != len(majors) or args.jobs < 1:
        parser.error('majors must be unique and jobs must be positive')
    tcs, runtime = tools_for(majors), runtime_objects()
    if args.subcommand == 'controls':
        controls(args, tcs, runtime)
        return
    cases = make_baselines(discover(args.cases), tcs, runtime)
    atomic_json(RAW / 'baseline.json', cases)
    bad = baseline_problems(cases)
    for problem in bad:
        print('BASELINE PROBLEM:', problem, flush=True)
    if args.subcommand == 'baseline':
        if bad:
            raise SystemExit(1)
        return
    args.suites = args.suites.split(',')
    if set(args.suites) - {'P1', 'P2', 'P3', 'P4'} or len(set(args.suites)) != len(args.suites) or args.p3_seqs < 1:
        parser.error('invalid suites or P3 sequence count')
    if args.p1_passes and set(args.suites) != {'P1'}:
        parser.error('--p1-passes re-evaluates P1 cells only; use --suites P1')
    if 'P4' in args.suites and 18 not in majors:
        parser.error('P4 requires major 18 in --majors')
    matrix(args, tcs, runtime, cases)
    report()


if __name__ == '__main__':
    main()
