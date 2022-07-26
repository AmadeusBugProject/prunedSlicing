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

    def test_parameterless_call(self):
        code_block = """
def dummy():
  return 1
a = dummy()
b = 1
c = b
"""
        variable = 'c'
        line_number = 6
        trace.trace_python(code_block)
        exec_trace = get_trace()
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {5, 6}
        self.assertEqual(expected_slice, computed_slice)

    def test_parameterless_call2(self):
        code_block = """
def dummy():
  return 1
a = dummy()
b = a
c = b
"""
        variable = 'c'
        line_number = 6
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5, 6}
        self.assertEqual(expected_slice, computed_slice)

    def test_parameterless_call3(self):
        code_block = """
def dummy():
  return 1
a = dummy()
b = a
c = dummy()
"""
        variable = 'c'
        line_number = 6
        trace.trace_python(code_block)
        exec_trace = get_trace()
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 6}
        self.assertEqual(expected_slice, computed_slice)

    def test_parameterless_call4(self):
        code_block = """
def dummy():
  a = 5
  b = a + 5
  return b
a = dummy()
b = a
c = dummy()
"""
        variable = 'c'
        line_number = 8
        trace.trace_python(code_block)
        exec_trace = get_trace()
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5, 8}
        self.assertEqual(expected_slice, computed_slice)

    def test_parameterless_call5(self):
        code_block = """
def dummy():
  a = 5
  b = a + 5
  return b
def dummy2():
  a = 4
  return a
a = dummy2()
b = a
c = dummy()
"""
        variable = 'c'
        line_number = 11
        trace.trace_python(code_block)
        exec_trace = get_trace()
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5, 11}
        self.assertEqual(expected_slice, computed_slice)

    def test_parameterized_call(self):
        code_block = """
def dummy(d):
  b = d + 5
  return b
a = 1
b = a
c = dummy(a)
"""
        variable = 'c'
        line_number = 7
        trace.trace_python(code_block)
        exec_trace = get_trace()
        # log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5, 7}
        self.assertEqual(expected_slice, computed_slice)

    def test_parameterized_call2(self):
        code_block = """
def dummy(d, a):
  b = d + a
  return b
a = 1
b = a
c = dummy(a, b)
"""
        variable = 'c'
        line_number = 7
        trace.trace_python(code_block)
        exec_trace = get_trace()
        # log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5, 6, 7}
        self.assertEqual(expected_slice, computed_slice)

    def test_parameterized_call3(self):
        code_block = """
def dummy(d, a):
  b = d + a
  return b
a = 1
b = a
c = dummy(1, 1)
"""
        variable = 'c'
        line_number = 7
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 7}
        self.assertEqual(expected_slice, computed_slice)

    def test_parameterized_call4(self):
        code_block = """
def dummy(d, e):
    b = d
    return b
a = 1
b = 2
c = dummy(a, b)
"""
        variable = 'c'
        line_number = 7
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5, 7}
        self.assertEqual(expected_slice, computed_slice)

    def test_scope(self):
        code_block = """
def dummy(a, b):
    b = a
    return b
a = 1
b = 2
c = dummy(a, b)
"""
        variable = 'c'
        line_number = 7
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5, 7}
        self.assertEqual(expected_slice, computed_slice)

    def test_scope2(self):
        code_block = """
def dummy(a, b):
    b = a + b
    return b
a = 1
b = 2
c = dummy(a, b)
"""
        variable = 'c'
        line_number = 7
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5, 6, 7}
        self.assertEqual(expected_slice, computed_slice)

    def test_scope3(self):
        code_block = """
def dummy(a, b):
    b = a + b
    return b
a = 1
b = 2
c = dummy(a, b)
d = a + b
"""
        variable = 'd'
        line_number = 8
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {5, 6, 8}
        self.assertEqual(expected_slice, computed_slice)

    def test_scope4(self):
        code_block = """
def dummy(a, b):
    b = a + b
    return b
a = 1
b = 2
c = dummy(a, b)
d = a + b + c
"""
        variable = 'd'
        line_number = 8
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5, 6, 7, 8}
        self.assertEqual(expected_slice, computed_slice)

    def test_buildin_function_call(self):
        code_block = """
a = 1
b = 2
print(a, b)
d = a + b
"""
        variable = 'd'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 5}
        self.assertEqual(expected_slice, computed_slice)

    def test_buildin_function_call2(self):
        code_block = """
a = 1
b = 2
c = str(a)
d = c
"""
        variable = 'd'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 4, 5}
        self.assertEqual(expected_slice, computed_slice)

    def test_buildin_function_call3(self):
        code_block = """
a = 1
b = 2
c = str(a+b)
d = c
"""
        variable = 'd'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5}
        self.assertEqual(expected_slice, computed_slice)

    def test_buildin_function_call4(self):
        code_block = """
a = 1
b = 2
c = str(a+3)
d = c
"""
        variable = 'd'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 4, 5}
        self.assertEqual(expected_slice, computed_slice)

    def test_not(self):
        code_block = """
def dummy(d):
  return d
a = 1
b = a
c = not(dummy(a))
"""
        variable = 'c'
        line_number = 6
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 6}
        self.assertEqual(expected_slice, computed_slice)

    def test_slice_criteria_in_function(self):
        code_block = """
def dummy(d):   # 2
  a = 0
  b = d         # 4
  return d
a = 4           # 6
dummy(a)        # 7
"""
        variable = 'b'
        line_number = 4
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 4, 6, 7}
        self.assertEqual(expected_slice, computed_slice)
