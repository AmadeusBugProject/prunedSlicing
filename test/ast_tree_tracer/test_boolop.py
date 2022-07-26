import unittest

from ast_tree_tracer import trace_container
from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from helpers.Logger import Logger

log = Logger()

class TestBoolOp(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_simple_and(self):
        code_block = """
a = True
b = False
c = True
z = a and b and c
"""

        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # z = a and b and c
        stat_trace = get_trace()[3]
        self.assertEqual('p_and_stat', stat_trace['type'])
        self.assertEqual('module', stat_trace['control_dep'])
        self.assertEqual(['a', 'b', 'c'], stat_trace['data_dep'])
        self.assertEqual(['a and b and c'], stat_trace['data_target'])

        dyn_trace = get_trace()[4]
        self.assertEqual('p_and_dyn', dyn_trace['type'])
        self.assertEqual('module', dyn_trace['control_dep'])
        self.assertEqual(['a', 'b'], dyn_trace['data_dep'])
        self.assertEqual(['a and b and c'], dyn_trace['data_target'])

    def test_nested(self):
        code_block = """
a = True
b = False
c = True
z = a and ( b or c )
"""

        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # ( b or c )
        stat_trace = get_trace()[4]
        self.assertEqual('p_or_stat', stat_trace['type'])
        self.assertEqual('module', stat_trace['control_dep'])
        self.assertEqual(['b', 'c'], stat_trace['data_dep'])
        self.assertEqual(['b or c'], stat_trace['data_target'])

        dyn_trace = get_trace()[5]
        self.assertEqual('p_or_dyn', dyn_trace['type'])
        self.assertEqual('module', dyn_trace['control_dep'])
        self.assertEqual(['b', 'c'], dyn_trace['data_dep'])
        self.assertEqual(['b or c'], dyn_trace['data_target'])

        # a and ( b or c )
        stat_trace = get_trace()[3]
        self.assertEqual('p_and_stat', stat_trace['type'])
        self.assertEqual('module', stat_trace['control_dep'])
        self.assertEqual(['a', 'b or c'], stat_trace['data_dep'])
        self.assertEqual(['a and (b or c)'], stat_trace['data_target'])

        dyn_trace = get_trace()[6]
        self.assertEqual('p_and_dyn', dyn_trace['type'])
        self.assertEqual('module', dyn_trace['control_dep'])
        self.assertEqual(['a', 'b or c'], dyn_trace['data_dep'])
        self.assertEqual(['a and (b or c)'], dyn_trace['data_target'])

    def test_simple_or(self):
        code_block = """
a = False
b = True
c = False
z = a or b or c
"""

        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # z = a or b or c
        stat_trace = get_trace()[3]
        self.assertEqual('p_or_stat', stat_trace['type'])
        self.assertEqual('module', stat_trace['control_dep'])
        self.assertEqual(['a', 'b', 'c'], stat_trace['data_dep'])
        self.assertEqual(['a or b or c'], stat_trace['data_target'])

        dyn_trace = get_trace()[4]
        self.assertEqual('p_or_dyn', dyn_trace['type'])
        self.assertEqual('module', dyn_trace['control_dep'])
        self.assertEqual(['a', 'b'], dyn_trace['data_dep'])
        self.assertEqual(['a or b or c'], dyn_trace['data_target'])

    def test_simple_if_test(self):
        code_block = """
a = False
b = True
if a and b:
    pass
"""

        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # if a and b:
        stat_trace = get_trace()[2]
        self.assertEqual('p_and_stat', stat_trace['type'])
        self.assertEqual('module', stat_trace['control_dep'])
        self.assertEqual(['a', 'b'], stat_trace['data_dep'])
        self.assertEqual(['a and b'], stat_trace['data_target'])

        dyn_trace = get_trace()[3]
        self.assertEqual('p_and_dyn', dyn_trace['type'])
        self.assertEqual('module', dyn_trace['control_dep'])
        self.assertEqual(['a'], dyn_trace['data_dep'])
        self.assertEqual(['a and b'], dyn_trace['data_target'])

    def test_simple_while_test(self):
        code_block = """
a = True
b = True
while a and b:
    a = False
"""

        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # a and b:
        stat_trace = get_trace()[2]
        self.assertEqual('p_and_stat', stat_trace['type'])
        self.assertEqual('module', stat_trace['control_dep'])
        self.assertEqual(['a', 'b'], stat_trace['data_dep'])
        self.assertEqual(['a and b'], stat_trace['data_target'])

        dyn_trace = get_trace()[3]
        self.assertEqual('p_and_dyn', dyn_trace['type'])
        self.assertEqual('module', dyn_trace['control_dep'])
        self.assertEqual(['a', 'b'], dyn_trace['data_dep'])
        self.assertEqual(['a and b'], dyn_trace['data_target'])

        # while a and b:
        while_trace = get_trace()[5]
        self.assertEqual('p_while_begin', while_trace['type'])
        self.assertEqual('module', while_trace['control_dep'])
        self.assertEqual(['a and b'], while_trace['data_dep'])
        self.assertEqual([], while_trace['data_target'])

        # a and b:
        stat_trace = get_trace()[8]
        self.assertEqual('p_and_stat', stat_trace['type'])
        self.assertEqual('module', stat_trace['control_dep'])
        self.assertEqual(['a', 'b'], stat_trace['data_dep'])
        self.assertEqual(['a and b'], stat_trace['data_target'])

        dyn_trace = get_trace()[9]
        self.assertEqual('p_and_dyn', dyn_trace['type'])
        self.assertEqual('module', dyn_trace['control_dep'])
        self.assertEqual(['a'], dyn_trace['data_dep'])
        self.assertEqual(['a and b'], dyn_trace['data_target'])

    def test_complex_statments(self):
        code_block = """
def gt(a, b):
    return a > b
a = 3
b = 2
c = True
z = gt(a, 1) and b > 5 and c
"""

        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # gt(a, 1) and b > 5 and c
        p_and_stat = get_trace()[3]
        self.assertEqual('p_and_stat', p_and_stat['type'])
        self.assertEqual('module', p_and_stat['control_dep'])
        self.assertEqual(['gt(a, 1)', 'b', 'c'], p_and_stat['data_dep'])
        self.assertEqual(['gt(a, 1) and b > 5 and c'], p_and_stat['data_target'])

        # gt(a, 1) and b > 5 and c
        p_and_dyn = get_trace()[8]
        self.assertEqual('p_and_dyn', p_and_dyn['type'])
        self.assertEqual('module', p_and_dyn['control_dep'])
        self.assertEqual(['gt(a, 1)', 'b'], p_and_dyn['data_dep'])
        self.assertEqual(['gt(a, 1) and b > 5 and c'], p_and_dyn['data_target'])


        # z = gt(a, 1) and b > 5 and c
        assignment = get_trace()[9]
        self.assertEqual('p_assignment', assignment['type'])
        self.assertEqual('module', assignment['control_dep'])
        self.assertEqual(['gt(a, 1) and b > 5 and c'], assignment['data_dep'])
        self.assertEqual(['z'], assignment['data_target'])



