import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from helpers.Logger import Logger
from slicing.slice import get_dynamic_slice
from slicing.slice import get_pruned_slice

log = Logger()


class TestBoolop(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_and(self):
        code_block = """
a = True
b = True
c = False
z = a and b and c
"""
        variable = 'z'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)

        computed_slice_dyn, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice_dyn = {2, 3, 4, 5}
        self.assertEqual(expected_slice_dyn, computed_slice_dyn)

        computed_slice_cond, rel_bool_ops, _ = get_pruned_slice(exec_trace, variable, line_number)
        expected_slice_cond = {4, 5}
        self.assertEqual(expected_slice_cond, computed_slice_cond)

    def test_and2(self):
        code_block = """
a = False
b = True
c = False
z = a and b and c
"""
        variable = 'z'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)

        computed_slice_dyn, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice_dyn = {2, 5}
        self.assertEqual(expected_slice_dyn, computed_slice_dyn)

        computed_slice_cond, rel_bool_ops, _ = get_pruned_slice(exec_trace, variable, line_number)
        expected_slice_cond = {2, 5}
        self.assertEqual(expected_slice_cond, computed_slice_cond)

    def test_and3(self):
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

        computed_slice_dyn, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice_dyn = {2, 3, 4, 5}
        self.assertEqual(expected_slice_dyn, computed_slice_dyn)

        computed_slice_cond, rel_bool_ops, _ = get_pruned_slice(exec_trace, variable, line_number)
        expected_slice_cond = {2, 3, 4, 5}
        self.assertEqual(expected_slice_cond, computed_slice_cond)

    def test_and4(self):
        code_block = """
a = True
b = False
c = True
z = a and b and c
"""
        variable = 'z'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)

        computed_slice_dyn, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice_dyn = {2, 3, 5}
        self.assertEqual(expected_slice_dyn, computed_slice_dyn)

        computed_slice_cond, rel_bool_ops, _ = get_pruned_slice(exec_trace, variable, line_number)
        expected_slice_cond = {3, 5}
        self.assertEqual(expected_slice_cond, computed_slice_cond)

    def test_or(self):
        code_block = """
a = True
b = True
c = True
z = a or b or c
"""
        variable = 'z'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)

        computed_slice_dyn, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice_dyn = {2, 5}
        self.assertEqual(expected_slice_dyn, computed_slice_dyn)

        computed_slice_cond, rel_bool_ops, _ = get_pruned_slice(exec_trace, variable, line_number)
        expected_slice_cond = {2, 5}
        self.assertEqual(expected_slice_cond, computed_slice_cond)

    def test_or2(self):
        code_block = """
a = False
b = True
c = True
z = a or b or c
"""
        variable = 'z'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)

        computed_slice_dyn, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice_dyn = {2, 3, 5}
        self.assertEqual(expected_slice_dyn, computed_slice_dyn)

        computed_slice_cond, rel_bool_ops, _ = get_pruned_slice(exec_trace, variable, line_number)
        expected_slice_cond = {3, 5}
        self.assertEqual(expected_slice_cond, computed_slice_cond)

    def test_or3(self):
        code_block = """
a = False
b = False
c = True
z = a or b or c
"""
        variable = 'z'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)

        computed_slice_dyn, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice_dyn = {2, 3, 4, 5}
        self.assertEqual(expected_slice_dyn, computed_slice_dyn)

        computed_slice_cond, rel_bool_ops, _ = get_pruned_slice(exec_trace, variable, line_number)
        expected_slice_cond = {4, 5}
        self.assertEqual(expected_slice_cond, computed_slice_cond)

    def test_or4(self):
        code_block = """
a = False
b = False
c = False
z = a or b or c
"""
        variable = 'z'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)

        computed_slice_dyn, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice_dyn = {2, 3, 4, 5}
        self.assertEqual(expected_slice_dyn, computed_slice_dyn)

        computed_slice_cond, rel_bool_ops, _ = get_pruned_slice(exec_trace, variable, line_number)
        expected_slice_cond = {2, 3, 4, 5}
        self.assertEqual(expected_slice_cond, computed_slice_cond)

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

        computed_slice_dyn, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice_dyn = {2, 3, 5, 6, 7}
        self.assertEqual(expected_slice_dyn, computed_slice_dyn)

        computed_slice_cond, rel_bool_ops, _ = get_pruned_slice(exec_trace, variable, line_number)
        expected_slice_cond = {2, 3, 6, 7}
        self.assertEqual(expected_slice_cond, computed_slice_cond)

    def test_nested_boolop2(self):
        code_block = """
a = True
b = True
c = False
d = False
e = True
z = a and b and d or c or e
"""
        variable = 'z'
        line_number = 7
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)

        computed_slice_dyn, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice_dyn = {2, 3, 4, 5, 6, 7}
        self.assertEqual(expected_slice_dyn, computed_slice_dyn)

        computed_slice_cond, rel_bool_ops, _ = get_pruned_slice(exec_trace, variable, line_number)
        expected_slice_cond = {6, 7}
        self.assertEqual(expected_slice_cond, computed_slice_cond)
