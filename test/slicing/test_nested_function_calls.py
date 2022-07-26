import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.slice import get_dynamic_slice
from helpers.Logger import Logger

log = Logger()


class TestFunctionCalls(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_nested_call(self):
        code_block = """
def dummy(d):
  return d
a = 1
b = a
c = dummy(dummy(a))
"""
        variable = 'c'
        line_number = 6
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 6}
        self.assertEqual(expected_slice, computed_slice)

    def test_nested_call2(self):
        code_block = """
def dummy(d):
  return d
def dummy2(d):
  return d
a = 1
b = a
c = dummy(dummy2(a))
"""
        variable = 'c'
        line_number = 8
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5, 6, 8}
        self.assertEqual(expected_slice, computed_slice)

    def test_nested_call3(self):
        code_block = """
def another_dummy(d):
  return d
  
def dummy(d):
  return 5
  
a = 1
b = a
c = dummy(a)
"""
        variable = 'c'
        line_number = 10
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {5, 6, 10}
        self.assertEqual(expected_slice, computed_slice)

    def test_nested_call4(self):
        code_block = """
def another_dummy(d):
  return d

def dummy(d):
  e  = another_dummy(d)
  return e

a = 1
b = a
c = dummy(a)
"""
        variable = 'c'
        line_number = 11
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 5, 6, 7, 9, 11}
        self.assertEqual(expected_slice, computed_slice)

    def test_nested_call5(self):
        code_block = """
def another_dummy(d):
  return d

def dummy(d):
  e  = d
  return another_dummy(e)

a = 1
b = a
c = dummy(a)
"""
        variable = 'c'
        line_number = 11
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 5, 6, 7, 9, 11}
        self.assertEqual(expected_slice, computed_slice)

    def test_nested_builtins(self):
        code_block = """
def dummy(d):
    return d
  
a = 4          
x = len(range(0,a))  
"""
        variable = 'x'
        line_number = 6
        trace.trace_python(code_block)
        exec_trace = get_trace()
        # log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {5, 6}
        self.assertEqual(expected_slice, computed_slice)

    def test_nested_builtins2(self):
        code_block = """
def dummy(d):
    return d

a = 4
b = 3          
x = len(range(0,a+b))  
"""
        variable = 'x'
        line_number = 7
        trace.trace_python(code_block)
        exec_trace = get_trace()
        # log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {5, 6, 7}
        self.assertEqual(expected_slice, computed_slice)

    def test_nested_builtins3(self):
        code_block = """
def dummy(d):
    return d

a = 4          
x = len(range(0,dummy(a)))  
"""
        variable = 'x'
        line_number = 6
        trace.trace_python(code_block)
        exec_trace = get_trace()
        # log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 5, 6}
        self.assertEqual(expected_slice, computed_slice)
