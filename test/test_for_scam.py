import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from helpers.Logger import Logger
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import get_dynamic_slice, get_pruned_slice

log = Logger()

with open('scam_tcas.py', 'r') as fd:
    TCAS = fd.read()


class TestBoolop(unittest.TestCase):
    def tearDown(self):
        clear_trace()


    """pruned slice because:
    enabled = True
    tcas_equipped = True
    not tcas_equipped = False
    intent_not_known = False"""

    def test_tcas_scam(self):
        variable = 'alt_sep'
        line_number = 27
        trace.trace_python(TCAS)
        exec_trace = get_trace()
        log.pretty_print_code(TCAS)

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)
        sliced_code = code_from_slice_ast(TCAS, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)
        log.s(str(computed_slice))

        computed_slice, rel_bool_ops, func_param_removal = get_pruned_slice(exec_trace, variable, line_number)
        sliced_code = code_from_slice_ast(TCAS, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)
        log.s(str(computed_slice))

        # expected_slice = {2, 3, 4, 5}
        # self.assertEqual(expected_slice, computed_slice)


    def test_relevant_slicing_scam(self):
        code_block = """l = [0,1,2,3,4]
x = 2
i = 0
found = False
while i < len(l) and not found:
    if l[i] == x:
        found = True
    else:
        i += 1
result = i
"""
        variable = 'result'
        line_number = 10
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.pretty_print_code(code_block)

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)
        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)
        log.s(str(computed_slice))

        computed_slice, rel_bool_ops, func_param_removal = get_pruned_slice(exec_trace, variable, line_number)
        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)
        log.s(str(computed_slice))
