import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.slice import get_dynamic_slice


class TestParameter(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_parameter1(self):
        code_block = """
def hanoi(height, start=1, end=3):                            # 2
    steps = []                                                # 3
    if height > 0:                                            # 4
        helper = ({1, 2, 3} - {start} - {end}).pop()          # 5
        steps.extend(hanoi(height - 1, start, helper))        # 6
        steps.append((start, end))                            # 7
    return steps                                              # 8
quix_result = hanoi(1, 1, 3)                                  # 9
"""

        variable = 'quix_result'
        line_number = 9
        trace.trace_python(code_block)
        exec_trace = get_trace()
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 6, 7, 8, 9}
        self.assertEqual(expected_slice, computed_slice)

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number, parameters_in_slice=True)
        expected_slice = {2, 3, 4, 5, 6, 7, 8, 9}
        self.assertEqual(expected_slice, computed_slice)

    def test_parameter2(self):
        code_block = """
def hanoi(height, start=1, end=3):                            # 2
    steps = []                                                # 3
    if height > 0:                                            # 4
        helper = ({1, 2, 3} - {start} - {end}).pop()          # 5
        hanoi(height - 1, start, helper)                      
        steps.append((start, end))                            # 7
    return steps
quix_result = hanoi(1, 1, 3)
"""

        variable = 'quix_result'
        line_number = 9
        trace.trace_python(code_block)
        exec_trace = get_trace()
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 7, 8, 9}
        self.assertEqual(expected_slice, computed_slice)

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number, parameters_in_slice=True)
        expected_slice = {2, 3, 4, 7, 8, 9}
        self.assertEqual(expected_slice, computed_slice)