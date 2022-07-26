import unittest

from ast_tree_tracer.trace import trace_python
from ast_tree_tracer.trace_container import clear_trace, get_trace
from helpers.Logger import Logger
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import get_dynamic_slice
from ast_tree_tracer.augment import *

log = Logger()


class TestRefactoryNewFailures(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_for_else_end_token_minimized(self):
        # benchmark/refactory/data/question_3/code/wrong/wrong_3_212.py#1:

        code_block = """
def remove_extras(lst):

    def position(i):
        n = len(lst)
        for j in range(n):
            if lst[j] == i:
                return j

    def helper(start, i):
        for k in lst[start:]:
            if k == i:
                lst.remove(k)
        else:
            j = 1
    for i in lst:
        index = position(i)
        helper(index + 1, i)
    return lst
extras_result = remove_extras([1])
"""
        variable = 'extras_result'
        line_number = len(code_block.splitlines())
        trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

def run_code(py_code, variable_name):
    globals_space = globals().copy()
    exec(compile(py_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]
