"""Draft clarification and inherited witness ledger checks (not execution claims).

The existing gate executes the listed witnesses independently. Ledger rows check
that each ruled sentence and its dependency IDs survive and that a full gate has
actually passed the linked rows. They do not claim new end-to-end coverage.
"""
import json
import hashlib
import collections
import re
from pathlib import Path
import dialect_check as d
from dialect_check_v02 import equal

ITEMS=json.loads((Path(__file__).with_name('dialect_0211_items.json')).read_text())


def dependency_ids():
    directory=d.ROOT.parent/'bennett-conformance'/'clauses'
    valid=set()
    for name in ('DLT-0.2.10','ISA-0.8','ISA-0.9-draft'):
        graph=json.loads((directory/(name+'.json')).read_text())
        valid.update(n['id'] for n in graph['nodes'])
    return valid


def check_sentence(text,item):
    # PT12 is in a table; normalise only whitespace, never wording/dependencies.
    equal(item['item'],'ruled clarification present',True,item['sentence'] in text)
    headings=list(re.finditer(r'^#{2,3} (\d+(?:\.\d+)?)\.? (.+)$',text,re.M))
    start=next((h.end() for h in headings if h[1]==item['section']),None)
    if start is None:raise d.Fail('missing section '+item['section'])
    end=next((h.start() for h in headings if h.start()>start),len(text))
    equal(item['item'],'clarification in section '+item['section'],True,item['sentence'] in text[start:end])
    valid=dependency_ids()
    deps=re.search(r'\[deps: ([^]]+)\]$',item['sentence'])
    if not deps:raise d.Fail('missing terminal dependency declaration')
    for dep in deps[1].split(', '):
        equal(item['item'],'declared dependency '+dep,True,dep in valid)


def check_item(runner,item):
    check_sentence(runner.spec,item)
    evidence=[]
    for ref in item['witnesses']:
        family,name=ref.split('/',1)
        matches=[r for r in runner.rows if r['family']==family and r['example']==name]
        if not matches:raise d.Fail(item['item']+' missing executed witness '+ref)
        for row in matches:equal(item['item'],ref+' executed','passed',row['status'])
        evidence.append(ref)
    return {'bead':item['bead'],'section':item['section'],
            'retained_executed_rows':evidence,'claim':'clarification and retained evidence only'}


def check_all(runner):
    # A selected-family development run is not a complete inherited-evidence gate.
    if runner.selected:return
    def baseline():
        snapshot=json.loads(Path(__file__).with_name('dialect_0211_baseline.json').read_text())
        current=collections.Counter(hashlib.sha256(json.dumps({'lang':b['lang'],'attrs':b['attrs'],'body':b['body']},sort_keys=True).encode()).hexdigest() for b in runner.blocks if b['attrs'])
        missing=collections.Counter(snapshot['checked_block_hashes'])-current
        equal('0211/baseline','accepted checked blocks retained',{},dict(missing))
        return {'accepted_spec_sha256':snapshot['spec_sha256'],'checked_blocks':len(snapshot['checked_block_hashes'])}
    runner.check('coverage','0211/baseline','S0 retained checked examples',baseline)
    for item in ITEMS:
        runner.check('coverage','0211/'+item['item'],'ruled clarification / inherited evidence',
                     lambda item=item:check_item(runner,item))
