import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.slice import get_dynamic_slice
from helpers.Logger import Logger

log = Logger()

class TestArray(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_array(self):
        code_block = """
a = 0
b = 1
c = [0,1]
c[b] = c[a]
"""
        variable = 'c'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())
        # trace 3 | lineno: 5	 type: p_assignment	 data_target: ['c', 'b']	 data_dep: ['c', 'a', 'c', 'b']
        # but should be: data_target: ['c']

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5}
        self.assertEqual(computed_slice, expected_slice)

        variable = 'b'
        line_number = 5
        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {3}
        self.assertEqual(computed_slice, expected_slice)

    def test_array1(self):
        code_block = """
a = 0
b = 1
c = [0,1]
c[b] += a
"""

        trace.trace_python(code_block)
        log.print_trace(get_trace())

        assignment_trace = get_trace()[3]
        self.assertEqual('p_aug_assignment', assignment_trace['type'])
        self.assertEqual('module', assignment_trace['control_dep'])
        self.assertEqual(['a', 'c', 'b'], assignment_trace['data_dep'])
        self.assertEqual(['c'], assignment_trace['data_target'])

    def test_array2(self):
        code_block = """
a = 0
b = 1
c = [0,1]
c[b] = a
"""

        trace.trace_python(code_block)
        log.print_trace(get_trace())

        assignment_trace = get_trace()[3]
        self.assertEqual('p_assignment', assignment_trace['type'])
        self.assertEqual('module', assignment_trace['control_dep'])
        self.assertEqual(['a', 'c', 'b'], assignment_trace['data_dep'])
        self.assertEqual(['c'], assignment_trace['data_target'])

    def test_array3(self):
        code_block = """
a = 0
b = 1
x = 5
y = 6
c = [0,1]
c[a], c[b] = [x, y]
"""

        trace.trace_python(code_block)
        log.print_trace(get_trace())

        assignment_trace = get_trace()[5]
        self.assertEqual('p_assignment', assignment_trace['type'])
        self.assertEqual('module', assignment_trace['control_dep'])
        self.assertEqual(['x', 'y', 'c', 'a', 'c', 'b'], assignment_trace['data_dep'])
        self.assertEqual(['c', 'c'], assignment_trace['data_target'])
