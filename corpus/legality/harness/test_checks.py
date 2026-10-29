import unittest
from run import check_l2, check_l3_static, check_l4, parse_passes, read_header


class AttributeTests(unittest.TestCase):
    pre = '''declare void @__bennett_gate(i32, ptr, i64)
define i64 @case_entry(i64 %x) {
 call void @__bennett_gate(i32 1, ptr null, i64 %x)
 ret i64 %x
}
'''

    def test_declaration_group_forbidden(self):
        post = self.pre.replace('(i32, ptr, i64)', '(i32, ptr, i64) #7') + '\nattributes #7 = { nounwind memory(argmem: read) willreturn }\n'
        r = check_l2(self.pre, post)
        self.assertEqual({x['attribute'] for x in r['forbidden_added']}, {'memory(argmem: read)', 'willreturn'})
        self.assertIn('nounwind', {x['attribute'] for x in r['observations']})

    def test_callsite_and_renumbering(self):
        pre = self.pre.replace('i64 %x)\n ret', 'i64 %x) #1\n ret') + '\nattributes #1 = { nounwind }\n'
        post = pre.replace('#1', '#99').replace('{ nounwind }', '{ nounwind nosync memory(none) }')
        r = check_l2(pre, post)
        self.assertEqual([x['attribute'] for x in r['forbidden_added']], ['memory(none)'])
        self.assertEqual(r['forbidden_added'][0]['kind'], 'call')
        self.assertEqual([x['attribute'] for x in r['observations']], ['nosync'])
        self.assertFalse(check_l2(pre, pre.replace('#1', '#4'))['forbidden_added'])

    def test_decl_must_not_mask_callsite_addition(self):
        pre = self.pre.replace('(i32, ptr, i64)', '(i32, ptr, i64) readonly')
        post = pre.replace('i64 %x)\n ret', 'i64 %x) readonly\n ret')
        self.assertEqual(len(check_l2(pre, post)['forbidden_added']), 1)
        self.assertTrue(check_l2(pre, post)['preexisting_forbidden'])

    def test_every_callsite_not_just_union(self):
        pre = self.pre.replace(' ret i64', ' call void @__bennett_gate(i32 2, ptr null, i64 %x) nounwind\n ret i64')
        post = pre.replace('i32 1, ptr null, i64 %x)', 'i32 1, ptr null, i64 %x) nounwind')
        self.assertEqual([x['attribute'] for x in check_l2(pre, post)['observations']], ['nounwind'])

    def test_identical_argument_sites_do_not_mask_additions(self):
        call = ' call void @__bennett_gate(i32 1, ptr null, i64 %x)'
        pre = self.pre.replace(call, call + ' readonly\n' + call)
        post = pre.replace(call + '\n', call + ' readonly\n')
        self.assertEqual(len(check_l2(pre, post)['forbidden_added']), 1)

    def test_parameter_and_return_observations(self):
        pre = 'declare ptr @__bennett_qalloc(i64, i64)\n'
        post = 'declare noundef nonnull ptr @__bennett_qalloc(i64 noundef, i64)\n'
        self.assertEqual({x['attribute'] for x in check_l2(pre, post)['observations']}, {'noundef', 'nonnull'})

    def test_memory_and_legacy_spellings(self):
        for attr in ['readnone', 'readonly', 'writeonly', 'argmemonly', 'inaccessiblememonly', 'speculatable']:
            self.assertTrue(check_l2(self.pre, self.pre.replace('(i32, ptr, i64)', '(i32, ptr, i64) ' + attr))['forbidden_added'])

    def test_missing_group_loud(self):
        with self.assertRaises(ValueError):
            check_l2(self.pre, self.pre + '\ndeclare void @__bennett_other() #404\n')


class HandleStaticTests(unittest.TestCase):
    pre = '''declare ptr @__bennett_qalloc(i64, i64)
define i64 @case_entry(i64 %x) {
 %h = call ptr @__bennett_qalloc(i64 0, i64 1)
 ret i64 %x
}
'''
    def test_new_cast_flagged_but_not_failure(self):
        post = self.pre.replace(' ret i64', ' %i = ptrtoint ptr %h to i64\n ret i64')
        self.assertEqual(check_l3_static(self.pre, post)[0]['opcode'], 'ptrtoint')
        self.assertEqual(check_l3_static(post, post), [])

    def test_unrelated_function_ignored(self):
        post = self.pre + 'define i64 @unrelated(ptr %p) {\n %i = ptrtoint ptr %p to i64\n ret i64 %i\n}\n'
        self.assertEqual(check_l3_static(self.pre, post), [])

    def test_handle_helper_and_existing_count(self):
        pre = self.pre + 'define i64 @helper(ptr %h) {\n ret i64 0\n}\n'
        pre = pre.replace(' ret i64 %x', ' %r = call i64 @helper(ptr %h)\n ret i64 %x')
        post = pre.replace(' ret i64 0', ' %i = ptrtoint ptr %h to i64\n ret i64 0')
        self.assertIn('helper', [x['function'] for x in check_l3_static(pre, post)])

    def test_region_pointer_and_global_handle_flow(self):
        pre = self.pre.replace(' ret i64 %x', ' call void @__bennett_adj(ptr @body, ptr %h)\n ret i64 %x')
        pre += 'define void @body(ptr %h) {\n ret void\n}\n'
        post = pre.replace(' ret void', ' %i = ptrtoint ptr %h to i64\n ret void')
        self.assertIn('body', [x['function'] for x in check_l3_static(pre, post)])
        pre = self.pre.replace(' ret i64 %x', ' store ptr %h, ptr @saved\n ret i64 %x')
        pre += '@saved = global ptr null\ndefine i64 @reader() {\n %h = load ptr, ptr @saved\n ret i64 0\n}\n'
        post = pre.replace(' ret i64 0', ' %i = ptrtoint ptr %h to i64\n ret i64 0')
        self.assertIn('reader', [x['function'] for x in check_l3_static(pre, post)])


class RegionTests(unittest.TestCase):
    ir = 'define void @region(ptr %env) {\n ret void\n}\n'
    trace = 'IN 0\nCTRL H0 0 F:region 2\nEND CTRL\nRET 0\n'
    def test_defined_region_pass(self):
        self.assertEqual(check_l4(self.trace, self.trace, self.ir), [])

    def test_changed_symbol_alias_declaration_and_thunk(self):
        self.assertTrue(check_l4(self.trace, self.trace.replace('F:region', 'F:other'), self.ir))
        for ir in ['@region = alias void (ptr), ptr @other', 'declare void @region(ptr)',
                   'define void @region(ptr %p) {\n tail call void @other(ptr %p)\n ret void\n}\ndefine void @other(ptr %p) {\n ret void\n}\n']:
            self.assertTrue(check_l4(self.trace, self.trace, ir))


class EnumerationTests(unittest.TestCase):
    def test_sections_params_and_mssa(self):
        listing = '''Module passes:
  invalidate<all>
Module passes with params:
  print<structural-hash><detailed>
Module analyses:
  wrong
CGSCC passes:
  inline
Function passes with params:
  gvn<pre;no-pre>
LoopNest passes:
  loop-flatten
Loop passes with params:
  licm<allowspeculation>
Machine function passes (WIP):
  wrong-machine
'''
        pipelines = [x['pipeline'] for x in parse_passes(listing)]
        self.assertEqual(pipelines, ['invalidate<all>', 'print<structural-hash>', 'cgscc(inline)', 'function(gvn)', 'function(loop(loop-flatten))', 'function(loop-mssa(licm))'])

    def test_bad_header_rejected(self):
        with self.assertRaises(ValueError):
            read_header('; CASE: wrong\n; INPUTS: 0\n; EXPECT: legal\n', 'right')


if __name__ == '__main__':
    unittest.main()
