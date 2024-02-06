import unittest

from ast_tree_tracer import trace_container
from ast_tree_tracer.trace import trace_python
from ast_tree_tracer.trace_container import get_trace, clear_trace
from helpers.Logger import Logger

log = Logger()


class TestWhile(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_simple_while(self):
        code_block = """
c = 0
while(c < 2):
    c +=1
i = 8
"""
        trace_python(code_block)
        log.print_trace(get_trace())

        # condition c < 2:
        while_begin = get_trace()[1]
        self.assertEqual('p_condition', while_begin['type'])
        self.assertIn('c < 2 => True', while_begin['info'])
        self.assertEqual('module', while_begin['control_dep'])
        self.assertEqual(['c'], while_begin['data_dep'])
        self.assertEqual([], while_begin['data_target'])

        # while(c < 2):
        while_begin = get_trace()[2]
        self.assertEqual('p_while_begin', while_begin['type'])
        self.assertIn('p_while_begin', while_begin['info'])
        self.assertEqual('module', while_begin['control_dep'])
        self.assertEqual(['c'], while_begin['data_dep'])
        self.assertEqual([], while_begin['data_target'])

        # c += 1
        assignment = get_trace()[3]
        self.assertEqual('p_aug_assignment', assignment['type'])
        self.assertEqual("3: p_while_begin test: p_condition(3, 'c < 2', ['c'], c < 2, ['c'])", assignment['control_dep'])

        # while(c < 2):
        while_end = get_trace()[4]
        self.assertEqual('p_while_end', while_end['type'])
        self.assertIn('p_while_end', while_end['info'])
        self.assertEqual("3: p_while_begin test: p_condition(3, 'c < 2', ['c'], c < 2, ['c'])", while_end['control_dep'])
        self.assertEqual(['c'], while_end['data_dep'])
        self.assertEqual([], while_end['data_target'])

        # while(c < 2):
        while_begin = get_trace()[6]
        self.assertEqual('p_while_begin', while_begin['type'])
        self.assertIn('p_while_begin', while_begin['info'])
        self.assertEqual('module', while_begin['control_dep'])
        self.assertEqual(['c'], while_begin['data_dep'])
        self.assertEqual([], while_begin['data_target'])

        # while(c < 2):
        while_end = get_trace()[8]
        self.assertEqual('p_while_end', while_end['type'])
        self.assertIn('p_while_end', while_end['info'])
        self.assertEqual("3: p_while_begin test: p_condition(3, 'c < 2', ['c'], c < 2, ['c'])", while_end['control_dep'])
        self.assertEqual(['c'], while_end['data_dep'])
        self.assertEqual([], while_end['data_target'])

        # condition c < 2:
        while_begin = get_trace()[9]
        self.assertEqual('p_condition', while_begin['type'])
        self.assertIn('c < 2 => False', while_begin['info'])
        self.assertEqual('module', while_begin['control_dep'])
        self.assertEqual(['c'], while_begin['data_dep'])
        self.assertEqual([], while_begin['data_target'])

        # i = 8
        assignment = get_trace()[13]
        self.assertEqual('p_assignment', assignment['type'])
        self.assertEqual('module', assignment['control_dep'])

    def test_nested_while(self):
        code_block = """
c = 0
a = 0
while(c < 2):
    c +=1
    while(a < 2):
        a +=1
i = 8
        """
        trace_python(code_block)
        log.print_trace(get_trace())

        # while(c < 2):
        while_begin = get_trace()[3]
        self.assertEqual('p_while_begin', while_begin['type'])
        self.assertIn('p_while_begin', while_begin['info'])
        self.assertEqual('module', while_begin['control_dep'])
        self.assertEqual(['c'], while_begin['data_dep'])
        self.assertEqual([], while_begin['data_target'])

        # c += 1
        assignment = get_trace()[4]
        self.assertEqual('p_aug_assignment', assignment['type'])
        self.assertEqual("4: p_while_begin test: p_condition(4, 'c < 2', ['c'], c < 2, ['c', 'a'])", assignment['control_dep'])

        # while(a < 2):
        while_begin = get_trace()[6]
        self.assertEqual('p_while_begin', while_begin['type'])
        self.assertIn('p_while_begin', while_begin['info'])
        self.assertEqual("4: p_while_begin test: p_condition(4, 'c < 2', ['c'], c < 2, ['c', 'a'])", while_begin['control_dep'])
        self.assertEqual(['a'], while_begin['data_dep'])
        self.assertEqual([], while_begin['data_target'])

        # a += 1
        assignment = get_trace()[7]
        self.assertEqual('p_aug_assignment', assignment['type'])
        self.assertEqual("6: p_while_begin test: p_condition(6, 'a < 2', ['a'], a < 2, ['a'])", assignment['control_dep'])

        # while(a < 2):
        while_end = get_trace()[8]
        self.assertEqual('p_while_end', while_end['type'])
        self.assertIn('p_while_end', while_end['info'])
        self.assertEqual("6: p_while_begin test: p_condition(6, 'a < 2', ['a'], a < 2, ['a'])", while_end['control_dep'])
        self.assertEqual(['a'], while_end['data_dep'])
        self.assertEqual([], while_end['data_target'])

        # while(a < 2):
        while_begin = get_trace()[10]
        self.assertEqual('p_while_begin', while_begin['type'])
        self.assertIn('p_while_begin', while_begin['info'])
        self.assertEqual("4: p_while_begin test: p_condition(4, 'c < 2', ['c'], c < 2, ['c', 'a'])", while_begin['control_dep'])
        self.assertEqual(['a'], while_begin['data_dep'])
        self.assertEqual([], while_begin['data_target'])

        # while(c < 2):
        while_end = get_trace()[14]
        self.assertEqual('p_while_end', while_end['type'])
        self.assertIn('p_while_end', while_end['info'])
        self.assertEqual("4: p_while_begin test: p_condition(4, 'c < 2', ['c'], c < 2, ['c', 'a'])", while_end['control_dep'])
        self.assertEqual(['c'], while_end['data_dep'])
        self.assertEqual([], while_end['data_target'])

        # i = 8
        assignment = get_trace()[24]
        self.assertEqual('p_assignment', assignment['type'])
        self.assertEqual('module', assignment['control_dep'])

    def test_while_condition(self):
        code_block = """
c = 4
while(c < 2):
    c +=1
i = 8
"""

        trace_python(code_block)
        log.print_trace(get_trace())

        # i > 3:
        p_else_begin = get_trace()[1]
        self.assertEqual('p_condition', p_else_begin['type'])
        self.assertEqual('module', p_else_begin['control_dep'])
        self.assertEqual(['c'], p_else_begin['data_dep'])
