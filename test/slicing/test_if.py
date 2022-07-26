import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.slice import get_dynamic_slice
from helpers.Logger import Logger

log = Logger()


class TestIf(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_simple_if(self):
        code_block = """
a = 2
b = 1
if a > b:
    b = 0
c = b
"""
        variable = 'c'
        line_number = 6
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5, 6}
        self.assertEqual(expected_slice, computed_slice)

    def test_another_simple_if(self):
        code_block = """
def simple_if(a, b):
    c = 0
    if a > b:
        c = 1
    return c

simple_if(1, 0)
    """
        variable = 'c'
        line_number = 8
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 4, 5, 8}
        self.assertEqual(expected_slice, computed_slice)



    def test_simple_else(self):
        code_block = """
a = 2
b = 1
if a > b:
    b = 0
else:
    b = 1
c = b
"""
        variable = 'c'
        line_number = 8
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5, 8}
        self.assertEqual(expected_slice, computed_slice)

    def test_simple_else2(self):
        code_block = """
a = 2
b = 3
if a > b:
    b = 0
else:
    b = 1
c = b
"""
        variable = 'c'
        line_number = 8
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())
        log.pretty_print_code(code_block)
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 7, 8}
        self.assertEqual(expected_slice, computed_slice)

    def test_nested_if(self):
        code_block = """
a = 4
b = 3
c = 1
if a > b:
    if c > 0:
        b = 0
c = b
"""
        variable = 'c'
        line_number = 8
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5, 6, 7, 8}
        self.assertEqual(expected_slice, computed_slice)

    def test_nested_if2(self):
        code_block = """
a = 4
b = 3
c = 1
if a > b:
    a = 3
    if c > 0:
        b = 0
c = a
"""
        variable = 'c'
        line_number = 9
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 5, 6, 9}
        self.assertEqual(expected_slice, computed_slice)

    def test_if_in_function(self):
        code_block = """
def dummy(a):
    if(a > 3):       # 3
        return 3     # 4
    else:
        return 0

b = 4                 # 8
c = dummy(b)          # 9
        """
        variable = 'c'
        line_number = 9
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 8, 9}
        self.assertEqual(expected_slice, computed_slice)


    def test_return(self):
        code_block = """
def simple_if(a, b):
    c = 0
    if a > b:
        c = 1
    return c
simple_if(1, 1)
"""
        variable = 'c'
        line_number = 6
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())
        log.pretty_print_code(code_block)

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 7}
        self.assertEqual(expected_slice, computed_slice)