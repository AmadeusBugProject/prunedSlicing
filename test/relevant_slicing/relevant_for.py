import ast
import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from ast_tree_tracer.transformers import transform_tree
from slicing.code_from_slice import get_boolop_replacements, code_from_slice_ast
from slicing.slice import get_dynamic_slice, get_relevant_slice
from helpers.Logger import Logger

log = Logger()


class TestRelevantForLoops(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_relevant_for_loop(self):
        code_block = """
z = 0
x = 1
for i in range(1,5):
    z = 5
    x += 1
z
"""
        variable = 'z'
        line_number = 6

        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)
        print('\n'.join([str(x) for x in rel_bool_ops]))
        print(computed_slice)
        print(get_boolop_replacements(line_number, rel_bool_ops, exec_trace))

        log.pretty_print_code(code_block)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)


    def test_relevant_for_loop_2(self):
        code_block = """
z = 0
x = 1
for i in []:
    z = 5
    x += 1
print(z)
"""
        variable = 'z'
        line_number = 7

        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)
        print('\n'.join([str(x) for x in rel_bool_ops]))
        print(computed_slice)
        print(get_boolop_replacements(line_number, rel_bool_ops, exec_trace))

        log.pretty_print_code(code_block)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)

    def test_relevant_while_loop(self):
        code_block = """
z = 0
x = 1
while x < 1:
    z = 5
    x += 1
print(z)
"""
        variable = 'z'
        line_number = 7

        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)
        print('\n'.join([str(x) for x in rel_bool_ops]))
        print(computed_slice)
        print(get_boolop_replacements(line_number, rel_bool_ops, exec_trace))

        log.pretty_print_code(code_block)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)