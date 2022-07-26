import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.slice import get_dynamic_slice
from slicing.slicing_criteria_exception import SlicingCriteriaException


class TestSlicingCriteria(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_variable_not_contained(self):
        code_block = """
a = 0
b = 1
c = 2
"""
        variable = 'z'
        line_number = 4
        trace.trace_python(code_block)
        exec_trace = get_trace()
        self.assertRaises(SlicingCriteriaException, get_dynamic_slice, exec_trace, variable, line_number)

    def test_wrong_line_number(self):
        code_block = """
a = 0
b = 1
c = 2
"""
        variable = 'c'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        self.assertRaises(SlicingCriteriaException, get_dynamic_slice, exec_trace, variable, line_number)

    def test_wrong_line_number2(self):
        code_block = """
a = 0
b = 1
c = 2
"""
        variable = 'c'
        line_number = 3
        trace.trace_python(code_block)
        exec_trace = get_trace()
        self.assertRaises(SlicingCriteriaException, get_dynamic_slice, exec_trace, variable, line_number)

    def test_correct_criteria(self):
        code_block = """
a = 0
b = 1
c = 2
"""
        variable = 'c'
        line_number = 4
        trace.trace_python(code_block)
        exec_trace = get_trace()
        get_dynamic_slice(exec_trace, variable, line_number)

    def test_correct_criteria2(self):
        code_block = """
a = 0
b = 1
c = 2
"""
        variable = 'b'
        line_number = 4
        trace.trace_python(code_block)
        exec_trace = get_trace()
        get_dynamic_slice(exec_trace, variable, line_number)





