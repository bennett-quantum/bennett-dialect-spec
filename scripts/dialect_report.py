"""Count executable semantic checks separately from structural bookkeeping."""
BOOKKEEPING = frozenset({'xrefs', 'parse', 'coverage', 'inventory'})


def counts(rows):
    result = {kind: {'total': 0, 'passed': 0} for kind in ('semantic', 'bookkeeping')}
    for row in rows:
        kind = 'bookkeeping' if row['family'] in BOOKKEEPING else 'semantic'
        result[kind]['total'] += 1
        result[kind]['passed'] += row['status'] == 'passed'
    return result


def summary(rows):
    return '; '.join(f'{value["passed"]}/{value["total"]} {kind}'
                     for kind, value in counts(rows).items())
