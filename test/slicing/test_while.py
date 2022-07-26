import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.slice import get_dynamic_slice
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
        variable = 'c'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4}
        self.assertEqual(expected_slice, computed_slice)

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
        variable = 'c'
        line_number = 8
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 4, 5}
        self.assertEqual(expected_slice, computed_slice)

    def test_nested_while2(self):
        code_block = """
c = 0
a = 3
while(c < 5):
    c +=1
    while(a < c):
        a +=1
i = 8
"""
        variable = 'a'
        line_number = 8
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2 ,3, 4, 5, 6, 7}
        self.assertEqual(expected_slice, computed_slice)

    def test_while_with_else(self):
        code_block = """
c = 0
a = 3
while(c < 5):
    c +=1
else:
    c -= 1
i = 8
"""
        variable = 'c'
        line_number = 8
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2 ,4, 5, 7}
        self.assertEqual(expected_slice, computed_slice)