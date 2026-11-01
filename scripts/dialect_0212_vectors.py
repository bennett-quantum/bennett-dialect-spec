"""Independent boundary oracles; samples do not certify consumer implementations."""
import json
from pathlib import Path
from dialect_check_v02 import command, equal


def numerical(runner):
    source=Path(__file__).with_name('0212_numerical.c')
    expected=[['3fff8000000000000008',0,1]]
    for kind in range(2):
        for pos in range(2):
            for sticky in range(2):
                for predicate in range(2):
                    for signaling in range(2):
                        for ignore in range(2):
                            expected.append([predicate,16*sticky | int((kind or signaling) and not ignore),1])
    expected += [[r,1,0] for r in range(5)]
    for major in ('18','23'):
        exe=runner.tmp/('0212-numerical-'+major)
        command([runner.frontends[major]/'clang','-O0','-frounding-math',source,'-lm','-o',exe])
        got=[json.loads(line) for line in command([exe]).splitlines()]
        equal('0212/DF/'+major,'independent host boundary oracle',expected,got)
    return {'claim':'independent host boundary evidence, not production carrier conformance','vectors_per_build':len(expected)}

