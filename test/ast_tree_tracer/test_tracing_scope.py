import ast
import unittest

from ast_tree_tracer import trace_container
from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from helpers.Logger import Logger

log = Logger()

class TestTracingScope(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_multi_method(self):
        code_block = """
def foo(a, b):
    return a + b
    
def bar(c, d):
    return foo(c,d)

x = 1
y = 2
q = bar(x, y)
"""
        trace.trace_python(code_block)
        clear_trace()

        code_block = """
q = bar(x, y)
        """
        with self.assertRaises(NameError) as context:
            trace.trace_python(code_block)
        self.assertEqual(str(context.exception), 'name \'bar\' is not defined')




