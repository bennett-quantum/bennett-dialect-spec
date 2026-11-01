"""Draft 0.2.12 static arith request v1 validation/canonical bytes, not a generator."""
import json

BASES={'f16','bf16','f32','f64','f80','f128','ppcf128'}
FORMATS={name:8 for name in ('Float8E5M2','Float8E5M2FNUZ','Float8E4M3','Float8E4M3FN','Float8E4M3FNUZ','Float8E4M3B11FNUZ','Float8E3M4','Float8E8M0FNU')}
FORMATS.update(Float6E3M2FN=6,Float6E2M3FN=6,Float4E2M1FN=4)

def canonical_request(request):
    def require(ok, detail):
        if not ok:raise ValueError('arith request v1: '+detail)
    require(type(request) is dict and set(request)=={'schema','llvm_major','target_triple','data_layout','entries'},'top-level keys')
    require(request['schema']=='bennett-arith-instantiations-1','schema')
    major=request['llvm_major']
    require(type(major) is int and major > 0,'positive LLVM major')
    for key in ('target_triple','data_layout'):
        require(type(request[key]) is str and bool(request[key]), key)
    require(type(request['entries']) is list,'entries array')
    entries={}
    for entry in request['entries']:
        require(type(entry) is dict,'entry object')
        op=entry.get('op');base=entry.get('base')
        require(type(base) is str and base in BASES,'base suffix')
        if op=='powi':
            require(set(entry)=={'op','base','exponent_bits'},'powi keys')
            k=entry['exponent_bits']
            require(type(k) is int and 1<=k<=8388608,'exponent width')
        else:
            require(op in ('convert_to','convert_from') and set(entry)=={'op','base','format'},'conversion keys')
            require(major==23 and type(entry['format']) is str and entry['format'] in FORMATS,'major interpretation MDString')
        key=(op,base,entry.get('format',''),entry.get('exponent_bits',0))
        entries[key]=entry
    canonical={**request,'entries':[entries[key] for key in sorted(entries)]}
    # All numbers are small exact integers; keys are ASCII. This subset has
    # the same ordering/encoding as JCS, with Unicode string values intact.
    return json.dumps(canonical,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
