import unittest

from ast_tree_tracer import trace_container
from ast_tree_tracer.trace import trace_python
from ast_tree_tracer.trace_container import get_trace, clear_trace
from helpers.Logger import Logger

log = Logger()


class TestReturn(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_boolop_return(self):
        code_block = """
a = False
b = True

def foo(x, y):
    return x and y

z = foo(a, b)
"""
        trace_python(code_block)
        log.print_trace(get_trace())

        p_and_dyn = get_trace()[5]
        self.assertEqual('p_and_dyn', p_and_dyn['type'])
        self.assertEqual("8: p_call_before foo ['a', 'b']", p_and_dyn['control_dep'])
        self.assertEqual(['x'], p_and_dyn['data_dep'])
        self.assertEqual(['x and y'], p_and_dyn['data_target'])

        p_return = get_trace()[6]
        self.assertEqual('p_return', p_return['type'])
        self.assertEqual("8: p_call_before foo ['a', 'b']", p_return['control_dep'])
        self.assertEqual(['x and y'], p_return['data_dep'])
        self.assertEqual([], p_return['data_target'])

    def test_simple_return(self):
        code_block = """
a = False
b = True

def foo(x, y):
    return x

z = foo(a, b)
"""
        trace_python(code_block)
        log.print_trace(get_trace())

        # for i in range(0, stop):
        p_return = get_trace()[4]
        self.assertEqual('p_return', p_return['type'])
        self.assertEqual("8: p_call_before foo ['a', 'b']", p_return['control_dep'])
        self.assertEqual(['x'], p_return['data_dep'])
        self.assertEqual([], p_return['data_target'])