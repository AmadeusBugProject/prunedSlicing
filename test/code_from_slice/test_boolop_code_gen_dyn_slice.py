import os
import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace, clear_trace
from helpers.Logger import Logger
from slicing.code_from_slice import code_from_slice_ast, get_boolop_replacements
from slicing.slice import get_dynamic_slice
from slicing.dummy import Dummy


log = Logger()

class TestBoolopCodeGen(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_simple_boolop_codegen(self):
        code_block = """
a = True
b = True
c = 3
d = 2
z = a and b and (c == 3 or d > 5)
"""
        variable = 'z'
        lineno = 6
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)
        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, lineno)
        print('\n'.join([str(x) for x in rel_bool_ops]))
        print(computed_slice)
        print(get_boolop_replacements(lineno, rel_bool_ops, exec_trace))

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)

        log.pretty_print_code(sliced_code)
        self.assertEqual('z = a and b and (c == 3)', sliced_code.splitlines()[-1])


    def test_call_in_boolop_codegen(self):
        code_block = """
def dummy(x):
    return not x
    
a = True
b = True
c = 3
d = 2
z = a and not dummy(b) and (c == 3 or d > 5)
"""
        variable = 'z'
        lineno = 9
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)
        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, lineno)
        print('\n'.join([str(x) for x in rel_bool_ops]))
        print(computed_slice)
        print(get_boolop_replacements(lineno, rel_bool_ops, exec_trace))

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)

        log.pretty_print_code(sliced_code)
        self.assertEqual('z = a and (not dummy(b)) and (c == 3)', sliced_code.splitlines()[-1])

def run_sliced(sliced_code, variable_name):
    globals_space = globals().copy()
    exec(compile(sliced_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]