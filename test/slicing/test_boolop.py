import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from helpers.Logger import Logger
from slicing.slice import get_dynamic_slice

log = Logger()


class TestBoolop(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_and(self):
        code_block = """
a = True
b = False
c = True
z = a and b
"""
        variable = 'z'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 5}
        self.assertEqual(expected_slice, computed_slice)

    def test_or(self):
        code_block = """
a = False
b = True
c = True
z = a or b
"""
        variable = 'z'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 5}
        self.assertEqual(expected_slice, computed_slice)

    def test_or_shortcircuit(self):
        code_block = """
a = True
b = True
c = True
z = a or b
"""
        variable = 'z'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 5}
        self.assertEqual(expected_slice, computed_slice)

    def test_and_shortcircuit(self):
        code_block = """
a = False
b = True
c = True
z = a and b
"""
        variable = 'z'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 5}
        self.assertEqual(expected_slice, computed_slice)

    def test_multi_boolop(self):
        code_block = """
a = True
b = True
c = True
z = a and b and c
"""
        variable = 'z'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5}
        self.assertEqual(expected_slice, computed_slice)

    def test_nested_boolop(self):
        code_block = """
a = True
b = True
c = True
d = False
e = True
z = a and b and (d or e or c)
"""
        variable = 'z'
        line_number = 7
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 5, 6, 7}
        self.assertEqual(expected_slice, computed_slice)
