"""Round-4 source-derived execution adapters; expectations are spec inputs."""
import json
import dialect_check as d
from dialect_check_v02 import equal
from dialect_map import Mapper

STATES={'n-gep-index'}

def check_state(runner,block):
    name=block['attrs']['state'];v=json.loads(block['body'])
    if name=='n-gep-index':
        source=runner.block('normalise-out',name)['body']
        for fn,cases in v.items():
            n=len(d.Module(source).funcs[fn].params)
            mapper=Mapper(source,'@'+fn,','.join(['ARG(64)']*n)+';tgt=64',
                          'null_size=4096 heap_base=4096 heap_limit_max=0 stack max 32')
            path=runner.tmp/(name+'-'+fn+'.bisa');path.write_text(mapper.run(runner.isa,path))
            runner.isa.call('check',path)
            for case in cases:
                argv=[]
                for x in case[:-2]:argv+=['--arg',str(x%(1<<64))]
                got=runner.isa.call('run-oracle',path,'ref','--input','',*argv,'--budget','1000,0,32,8')
                equal(name,fn+' mapped payload/code',case[-2:],[int(got['payload']),int(got['code'])])
    else:raise d.Fail('unknown round-4 state '+name)
