"""Consumer-gap sentence integrity and inherited execution witnesses.

These checks do not claim completion of consumer implementation blockers.
"""
import json
from pathlib import Path
from dialect_check_v02 import equal

def check_all(runner):
    if runner.selected:
        return
    from test_dialect_0212 import N0Resolution
    runner.check('coverage', '0212/mkb/n0-resolution-source', '§7.2 N0 order',
                 N0Resolution('test_widenable_definition_and_original_addresses').test_widenable_definition_and_original_addresses)
    from test_dialect_0212 import CarrierABI, InstantiationRequest
    runner.check('coverage', '0212/z7u/carriers', '§13.1 metadata carrier ABI',
                 CarrierABI('test_arbitrary_names_and_operands').test_arbitrary_names_and_operands)
    runner.check('coverage', '0212/z7u/request', '§13.1 request schema',
                 InstantiationRequest('test_schema_canonicalisation_and_no_width_subset').test_schema_canonicalisation_and_no_width_subset)
    runner.check('coverage', '0212/21a/comparison-abi', '§13.5 signaling/quiet ABI',
                 CarrierABI('test_constrained_comparison_operands').test_constrained_comparison_operands)
    from dialect_0212_vectors import numerical, allocation
    runner.check('coverage', '0212/round11/DF-boundaries', '§§13.1/13.4/13.5 suite DF',
                 lambda: numerical(runner))
    runner.check('coverage', '0212/round11/DR-DD-boundaries', '§§17.1/19.5 suites DR/DD',
                 lambda: allocation(runner))
    for item in json.loads(Path(__file__).with_name('dialect_0212_items.json').read_text()):
        def check(item=item):
            equal(item['id'], 'normative wording retained', True, item['sentence'] in runner.spec)
            for ref in item['witnesses']:
                family, name = ref.split('/', 1)
                rows = [r for r in runner.rows if r['family'] == family and r['example'] == name]
                equal(item['id'], 'executed witness '+ref, ['passed'], [r['status'] for r in rows])
            return {'claim': 'wording integrity and listed inherited witnesses only', 'section': item['section']}
        runner.check('coverage', '0212/'+item['id'], 'consumer gap', check)
