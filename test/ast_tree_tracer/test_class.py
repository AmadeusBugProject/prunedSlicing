import ast
import unittest

import astpretty

from ast_tree_tracer import trace_container
from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from helpers.Logger import Logger
from slicing.slicing_exceptions import SlicingException

log = Logger()

class TestClass(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_class(self):
        code_block = """
a = 1
class Tcas:
    def __init__(self, x):
        self.A = x
        self.B = 0
    
    def get_sum(self, x):
        return self.B + self.A + x

x = 5
tcas = Tcas(x)
zz = tcas.get_sum(x)
"""

        trace.trace_python(code_block)
        log.print_trace(get_trace())

        p_class_def = get_trace()[1]
        self.assertEqual('p_class_def', p_class_def['type'])
        self.assertEqual('module', p_class_def['control_dep'])
        self.assertEqual([], p_class_def['data_dep'])
        self.assertEqual([], p_class_def['data_target'])

        p_call_before_init = get_trace()[3]
        self.assertEqual('p_call_before', p_call_before_init['type'])
        self.assertEqual('module', p_call_before_init['control_dep'])
        self.assertEqual([['x']], p_call_before_init['data_dep'])
        self.assertEqual(['Tcas(x)'], p_call_before_init['data_target'])

        p_call_before_get_sum = get_trace()[9]
        self.assertEqual('p_call_before', p_call_before_get_sum['type'])
        self.assertEqual('module', p_call_before_get_sum['control_dep'])
        self.assertEqual([['tcas'], ['x']], p_call_before_get_sum['data_dep'])
        self.assertEqual(['tcas.get_sum(x)'], p_call_before_get_sum['data_target'])

        # lineno: 3	 type: p_assignment	 data_target: ['a'] should have control dependency on class TCAS
        # methods also on top of control dependency TCAS

    def test_builtin_class(self):
        code_block = """
from collections import Counter
a = {'blue': 3, 'red': 2, 'green': 1}
x = Counter(a)
z = x
"""

        trace.trace_python(code_block)
        log.print_trace(get_trace())

        p_call_before_init = get_trace()[1]
        self.assertEqual('p_call_before', p_call_before_init['type'])
        self.assertEqual('module', p_call_before_init['control_dep'])
        self.assertEqual([['a']], p_call_before_init['data_dep'])
        self.assertEqual(['Counter(a)'], p_call_before_init['data_target'])

        p_call_after = get_trace()[2]
        self.assertEqual('p_call_after', p_call_after['type'])
        self.assertEqual("4: p_call_before Counter ['a']", p_call_after['control_dep'])
        self.assertEqual([['a']], p_call_after['data_dep'])
        self.assertEqual(['Counter(a)'], p_call_after['data_target'])



