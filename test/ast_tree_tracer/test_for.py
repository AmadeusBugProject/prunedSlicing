import unittest

from ast_tree_tracer import trace_container
from ast_tree_tracer.trace import trace_python
from ast_tree_tracer.trace_container import get_trace, clear_trace
from helpers.Logger import Logger

log = Logger()


class TestFor(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_simple_for(self):
        code_block = """
c = 0
stop = 2
for i in range(0, stop):
    c +=1
i = 8
"""
        trace_python(code_block)
        log.print_trace(get_trace())

        # for i in range(0, stop):
        for_begin = get_trace()[4]
        self.assertEqual('p_for_begin', for_begin['type'])
        self.assertIn('p_for_begin', for_begin['info'])
        self.assertEqual('module', for_begin['control_dep'])
        self.assertEqual(['range(0, stop)'], for_begin['data_dep'])
        self.assertEqual(['i'], for_begin['data_target'])

        control_dep_4 = "4: p_for_begin target: i iter:p_call_after(4, 'range', ['0', 'stop'], ['range(0, stop)'], [[], ['stop']], p_call_before(4, 'range', ['0', 'stop'], ['range(0, stop)'], [[], ['stop']]), range(0, stop))"
        # a += 1
        assignment = get_trace()[5]
        self.assertEqual('p_aug_assignment', assignment['type'])
        self.assertEqual(control_dep_4, assignment['control_dep'])

        # for i in range(0, stop):
        for_end = get_trace()[6]
        self.assertEqual('p_for_end', for_end['type'])
        self.assertIn('p_for_end', for_end['info'])
        self.assertEqual(control_dep_4, for_end['control_dep'])
        self.assertEqual(['range(0, stop)'], for_end['data_dep'])
        self.assertEqual(['i'], for_end['data_target'])

        # for i in range(0, stop):
        for_begin = get_trace()[7]
        self.assertEqual('p_for_begin', for_begin['type'])
        self.assertIn('p_for_begin', for_begin['info'])
        self.assertEqual('module', for_begin['control_dep'])
        self.assertEqual(['range(0, stop)'], for_begin['data_dep'])
        self.assertEqual(['i'], for_begin['data_target'])

        # a += 1
        assignment = get_trace()[8]
        self.assertEqual('p_aug_assignment', assignment['type'])
        self.assertEqual(control_dep_4, assignment['control_dep'])

        # for i in range(0, stop):
        for_end = get_trace()[9]
        self.assertEqual('p_for_end', for_end['type'])
        self.assertIn('p_for_end', for_end['info'])
        self.assertEqual(control_dep_4, for_end['control_dep'])
        self.assertEqual(['range(0, stop)'], for_end['data_dep'])
        self.assertEqual(['i'], for_end['data_target'])

        # i = 8
        assignment = get_trace()[10]
        self.assertEqual('p_assignment', assignment['type'])
        self.assertEqual('module', assignment['control_dep'])

    def test_nested_for(self):
        code_block = """
c = 0
a = 0
stop = 2
staaap = 2
for i in range(0, stop):
    a += 1
    for j in range(0, staaap):
        c += 1
i = 8
        """
        trace_python(code_block)
        log.print_trace(get_trace())

        # for i in range(0, stop):
        for_begin = get_trace()[6]
        self.assertEqual('p_for_begin', for_begin['type'])
        self.assertIn('p_for_begin', for_begin['info'])
        self.assertEqual('module', for_begin['control_dep'])
        self.assertEqual(['range(0, stop)'], for_begin['data_dep'])
        self.assertEqual(['i'], for_begin['data_target'])

        control_dep_6 = "6: p_for_begin target: i iter:p_call_after(6, 'range', ['0', 'stop'], ['range(0, stop)'], [[], ['stop']], p_call_before(6, 'range', ['0', 'stop'], ['range(0, stop)'], [[], ['stop']]), range(0, stop))"
        # a += 1
        assignment = get_trace()[7]
        self.assertEqual('p_aug_assignment', assignment['type'])
        self.assertEqual(control_dep_6, assignment['control_dep'])

        # for j in range(0, staaap):
        for_begin = get_trace()[10]
        self.assertEqual('p_for_begin', for_begin['type'])
        self.assertIn('p_for_begin', for_begin['info'])
        self.assertEqual(control_dep_6, for_begin['control_dep'])
        self.assertEqual(['range(0, staaap)'], for_begin['data_dep'])
        self.assertEqual(['j'], for_begin['data_target'])

        control_dep_8 = "8: p_for_begin target: j iter:p_call_after(8, 'range', ['0', 'staaap'], ['range(0, staaap)'], [[], ['staaap']], p_call_before(8, 'range', ['0', 'staaap'], ['range(0, staaap)'], [[], ['staaap']]), range(0, staaap))"
        # c += 1
        assignment = get_trace()[11]
        self.assertEqual('p_aug_assignment', assignment['type'])
        self.assertEqual(control_dep_8, assignment['control_dep'])

        # for j in range(0, staaap):
        for_end = get_trace()[12]
        self.assertEqual('p_for_end', for_end['type'])
        self.assertIn('p_for_end', for_end['info'])
        self.assertEqual(control_dep_8, for_end['control_dep'])
        self.assertEqual(['range(0, staaap)'], for_end['data_dep'])
        self.assertEqual(['j'], for_end['data_target'])

        # for j in range(0, staaap):
        for_begin = get_trace()[13]
        self.assertEqual('p_for_begin', for_begin['type'])
        self.assertIn('p_for_begin', for_begin['info'])
        self.assertEqual(control_dep_6, for_begin['control_dep'])
        self.assertEqual(['range(0, staaap)'], for_begin['data_dep'])
        self.assertEqual(['j'], for_begin['data_target'])

        # c += 1
        assignment = get_trace()[14]
        self.assertEqual('p_aug_assignment', assignment['type'])
        self.assertEqual(control_dep_8, assignment['control_dep'])

        # for j in range(0, staaap):
        for_end = get_trace()[15]
        self.assertEqual('p_for_end', for_end['type'])
        self.assertIn('p_for_end', for_end['info'])
        self.assertEqual(control_dep_8, for_end['control_dep'])
        self.assertEqual(['range(0, staaap)'], for_end['data_dep'])
        self.assertEqual(['j'], for_end['data_target'])

        # for i in range(0, stop):
        for_end = get_trace()[16]
        self.assertEqual('p_for_end', for_end['type'])
        self.assertIn('p_for_end', for_end['info'])
        self.assertEqual(control_dep_6, for_end['control_dep'])
        self.assertEqual(['range(0, stop)'], for_end['data_dep'])
        self.assertEqual(['i'], for_end['data_target'])

        # for i in range(0, stop):
        for_begin = get_trace()[17]
        self.assertEqual('p_for_begin', for_begin['type'])
        self.assertIn('p_for_begin', for_begin['info'])
        self.assertEqual('module', for_begin['control_dep'])
        self.assertEqual(['range(0, stop)'], for_begin['data_dep'])
        self.assertEqual(['i'], for_begin['data_target'])

        # c += 1
        assignment = get_trace()[28]
        self.assertEqual('p_assignment', assignment['type'])
        self.assertEqual('module', assignment['control_dep'])

    def test_iterator_is_list(self):
        code_block = """
a = [1,2,3]
c = 0
for i in a:
    c += 1
i = 8
                """
        trace_python(code_block)
        log.print_trace(get_trace())

        # for i in range(0, stop):
        for_begin = get_trace()[2]
        self.assertEqual('p_for_begin', for_begin['type'])
        self.assertIn('p_for_begin', for_begin['info'])
        self.assertEqual('module', for_begin['control_dep'])
        self.assertEqual(['a'], for_begin['data_dep'])
        self.assertEqual(['i'], for_begin['data_target'])

        # c += 1
        assignment = get_trace()[3]
        self.assertEqual('p_aug_assignment', assignment['type'])
        self.assertEqual('4: p_for_begin target: i iter:a', assignment['control_dep'])

        # for i in range(0, stop):
        for_end = get_trace()[4]
        self.assertEqual('p_for_end', for_end['type'])
        self.assertIn('p_for_end', for_end['info'])
        self.assertEqual('4: p_for_begin target: i iter:a', for_end['control_dep'])
        self.assertEqual(['a'], for_end['data_dep'])
        self.assertEqual(['i'], for_end['data_target'])

        # for i in range(0, stop):
        for_begin = get_trace()[5]
        self.assertEqual('p_for_begin', for_begin['type'])
        self.assertIn('p_for_begin', for_begin['info'])
        self.assertEqual('module', for_begin['control_dep'])
        self.assertEqual(['a'], for_begin['data_dep'])
        self.assertEqual(['i'], for_begin['data_target'])

        # c += 1
        assignment = get_trace()[11]
        self.assertEqual('p_assignment', assignment['type'])
        self.assertEqual('module', assignment['control_dep'])

    def test_multi_assign_for(self):
        code_block = """
a = [1,2,3]
c = 0
for i, j in enumerate(a):
    c += 1
i = 8
                        """
        trace_python(code_block)
        log.print_trace(get_trace())

        # for i in range(0, stop):
        for_begin = get_trace()[4]
        self.assertEqual('p_for_begin', for_begin['type'])
        self.assertIn('p_for_begin', for_begin['info'])
        self.assertEqual('module', for_begin['control_dep'])
        self.assertEqual(['enumerate(a)'], for_begin['data_dep'])
        self.assertEqual(['i', 'j'], for_begin['data_target'])