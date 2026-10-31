"""LLVM N9 operand parsing shared by expected normalisation and S2 transfers."""
import re
import dialect_check as d


def parts(ins):
    body=ins.text.split(' = ',1)[-1]
    kind,rest=body.split(None,1)
    rest=re.sub(r'^(?:(?:weak|volatile)\s+)*','',rest)
    if kind=='atomicrmw':op,rest=rest.split(None,1)
    elif kind=='cmpxchg':op='cmpxchg'
    else:raise d.Fail('N9 expected atomic update: '+body)
    fields=d.split_top(rest)
    expected=3 if kind=='cmpxchg' else 2
    if len(fields)<expected:raise d.Fail('N9 missing atomic operand: '+body)
    pty,_=d.parse_type(fields[0])
    if pty[0]!='ptr':raise d.Fail('N9 non-pointer atomic address: '+body)
    typed=fields[expected-1]
    ty,pos=d.parse_type(typed)
    value=typed[pos:].strip()
    order=re.search(r'\s+(?:syncscope\("[^"\n]*"\)\s+)?(?:unordered|monotonic|acquire|release|acq_rel|seq_cst)\b',value)
    if order is None:raise d.Fail('N9 missing atomic ordering: '+body)
    value=value[:order.start()]
    compare=d.typed_val(fields[1]) if kind=='cmpxchg' else None
    alignment=next((', '+x for x in fields[expected:] if x.startswith('align ')),'')
    return op,fields[0],d.typed_val(fields[0]),ty,d.tstr(ty),compare,value,alignment
