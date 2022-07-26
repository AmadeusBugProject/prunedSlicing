import unittest

from timeout_decorator import timeout_decorator

from ast_tree_tracer import trace
from ast_tree_tracer.augment import p_func_def, p_condition, p_if_label, p_return, p_call_after, p_call_before, p_or
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import get_dynamic_slice
from helpers.Logger import Logger
from slicing.dummy import Dummy
from constants import QUIX_TIMEOUT

log = Logger()


class TestFuncFailure(unittest.TestCase):
    def tearDown(self):
        clear_trace()


    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_scope2(self):
        code_block = """
def subsequences(a, b, k):
    if k == 0:
        return [[]]

    ret = []
    for i in range(a, b + 1 - k):
        ret.extend(
            [i] + rest for rest in subsequences(i + 1, b, k - 1)
        )

    return ret

quix_result = subsequences(1, 5, 3)
"""
        variable = 'quix_result'
        line_number = 14
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)
        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)
        # print('\n'.join([str(x) for x in rel_bool_ops]))
        print(computed_slice)
        # print(get_boolop_replacements(line_number, rel_bool_ops, exec_trace))

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)

        log.pretty_print_code(sliced_code)
        self.assertEqual(run_code(code_block, 'quix_result'), run_code(sliced_code, 'quix_result'))

    # @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_scope3(self):
        code_block = """
def hanoi(height, start=1, end=3):
    steps = []
    if height > 0:
        helper = ({1, 2, 3} - {start} - {end}).pop()
        steps.extend(hanoi(height - 1, start, helper))
        steps.append((start, end))
        steps.extend(hanoi(height - 1, helper, end))

    return steps
a = 2
b = 1
c = 3
quix_result = hanoi(a, b, c)
"""
        variable = 'quix_result'
        line_number = 14
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)
        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)
        # print('\n'.join([str(x) for x in rel_bool_ops]))
        print(computed_slice)
        # print(get_boolop_replacements(line_number, rel_bool_ops, exec_trace))

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)

        log.pretty_print_code(sliced_code)
        self.assertEqual(run_code(code_block, 'quix_result'), run_code(sliced_code, 'quix_result'))

    # @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_scope4(self):
        code_block = """
def search(x, seq):
    if len(seq)==0:
        return 0
    for i in range(len(seq)):
        if x<=seq[i]:break
        if i==len(seq)-1: i+=1
    return i
search_result = search(-100, (-5, -1, 3, 5, 7, 10))
"""
        variable = 'search_result'
        line_number = 9
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)
        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)
        # print('\n'.join([str(x) for x in rel_bool_ops]))
        print(computed_slice)
        # print(get_boolop_replacements(line_number, rel_bool_ops, exec_trace))

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)

        log.pretty_print_code(sliced_code)
        self.assertEqual(run_code(code_block, 'search_result'), run_code(sliced_code, 'search_result'))

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_scope5(self):
        code_block = """
def longest_common_subsequence(a, b):
    if not a or not b:
        return ''

    elif a[0] == b[0]:
        return a[0] + longest_common_subsequence(a[1:], b[1:])

    else:
        return max(longest_common_subsequence(a, b[1:]), longest_common_subsequence(a[1:], b), key=len)

quix_result = longest_common_subsequence('ABCD', 'XBCYDQ')
"""
        variable = 'quix_result'
        line_number = 12
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(exec_trace)
        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)
        # print('\n'.join([str(x) for x in rel_bool_ops]))
        print(computed_slice)
        # print(get_boolop_replacements(line_number, rel_bool_ops, exec_trace))

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)

        log.pretty_print_code(sliced_code)
        self.assertEqual(run_code(code_block, 'quix_result'), run_code(sliced_code, 'quix_result'))


def run_code(py_code, variable_name):
    globals_space = globals().copy()
    exec(compile(py_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]