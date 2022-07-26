import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.slice import get_dynamic_slice


class TestAssignment(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_assignment1(self):
        code_block = """
a = 0
b = 1
c = 2
"""
        variable = 'c'
        line_number = 4
        trace.trace_python(code_block)
        exec_trace = get_trace()
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {4}
        self.assertEqual(computed_slice, expected_slice)

    def test_assignment2(self):
        code_block = """
a = 0
b = 1
c = a + b
"""
        variable = 'c'
        line_number = 4
        trace.trace_python(code_block)
        exec_trace = get_trace()
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4}
        self.assertEqual(computed_slice, expected_slice)

    def test_assignment3(self):
        code_block = """
a = 0
b = a
c = b + 3
"""
        variable = 'c'
        line_number = 4
        trace.trace_python(code_block)
        exec_trace = get_trace()
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4}
        self.assertEqual(computed_slice, expected_slice)

    def test_assignment4(self):
        code_block = """
a = 0
b = a
c = b + 3
d = b
e = a
f = d + c
"""
        variable = 'f'
        line_number = 7
        trace.trace_python(code_block)
        exec_trace = get_trace()
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5, 7}
        self.assertEqual(computed_slice, expected_slice)
