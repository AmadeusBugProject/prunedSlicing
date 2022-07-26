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
from constants import REFACTORY_TIMEOUT, QUIX_TIMEOUT

log = Logger()


class TestSlicingRecursionError(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_recursion_error_1(self):
        code_block = """
def search(x, seq):
    index = 0
    def helper(index):
        if not seq:
            return 0
        elif x <= seq[index]:
            return index
        else:
            if index + 1 >= len(seq):
                return index + 1
            else:
                return helper(index+1)
    return helper(index)
search_result = search(42, (-5, 1, 3, 5, 7, 10))"""
        variable = 'search_result'
        line_number = len(code_block.splitlines())
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))


    @timeout_decorator.timeout(REFACTORY_TIMEOUT)
    def test_recursion_error_2(self):
        code_block = """
def search(x, seq):
    if seq:
        for i in range(len(seq)):
            if x <= seq[i]:
                return i
        return len(seq)
    else:
        return 0
   


search_result = search(7, [1, 5, 10])"""
        variable = 'search_result'
        line_number = len(code_block.splitlines())
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    @timeout_decorator.timeout(REFACTORY_TIMEOUT)
    def test_recursion_error_3(self):
        code_block = """
def search(x, seq):
    for i in range(len(seq)):
        if x <= seq[i]:
            return i
    else:
        return len(seq)
search_result = search(42, [1, 5, 10])
"""
        variable = 'search_result'
        line_number = len(code_block.splitlines())
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_recursion_error_4(self):
        code_block = """
def longest_common_subsequence(a, b):
    if not a or not b:
        return ''

    elif a[0] == b[0]:
        return a[0] + longest_common_subsequence(a[1:], b[1:])

    else:
        return max(longest_common_subsequence(a, b[1:]), longest_common_subsequence(a[1:], b), key=len)

quix_result = longest_common_subsequence('acbdegcedbg', 'begcfeubk')
"""
        variable = 'quix_result'
        line_number = len(code_block.splitlines())
        trace.trace_python(code_block)
        exec_trace = get_trace()
        # log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_recursion_error_5(self):
        code_block = """
def knapsack(capacity, items):
    from collections import defaultdict
    memo = defaultdict(int)

    for i in range(1, len(items) + 1):
        weight, value = items[i - 1]

        for j in range(1, capacity + 1):
            memo[i, j] = memo[i - 1, j]

            if weight <= j:
                memo[i, j] = max(memo[i, j], value + memo[i - 1, j - weight])

    return memo[len(items), capacity]

quix_result = knapsack(750, [[70, 135], [73, 139], [77, 149], [80, 150], [82, 156], [87, 163], [90, 173], [94, 184], [98, 192], [106, 201], [110, 210], [113, 214], [115, 221], [118, 229], [120, 240]])
"""
        variable = 'quix_result'
        line_number = len(code_block.splitlines())
        trace.trace_python(code_block)
        exec_trace = get_trace()
        # log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_recursion_error_6(self):
        code_block = """
def search(x, seq):
    count=0
    for i in range (len(seq)):
        if x<=seq[i]:
            break
        count +=1
    return count
search_result = search(-100, ())
"""
        variable = 'search_result'
        line_number = len(code_block.splitlines())
        trace.trace_python(code_block)
        exec_trace = get_trace()
        # log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    @timeout_decorator.timeout(REFACTORY_TIMEOUT)
    def test_recursion_error_7(self):
        code_block = """
def search(x, seq):
    i = 0
    for i, ele in enumerate(seq, 0):
        if x > ele:
            i += 1
        else:
            break
    return i
search_result = search(-100, (-5, -1, 3, 5, 7, 10))
"""
        variable = 'search_result'
        line_number = len(code_block.splitlines())
        trace.trace_python(code_block)
        exec_trace = get_trace()
        # log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_recursion_error_8(self):
        code_block = """
def search(x, seq):
    if seq == () or seq == []:
        return 0
    elif x < seq[0]:
        return 0
    elif x > seq[-1]:
        return len(seq)
    for i, elem in enumerate(seq):
            if x <= elem:
                return i 
search_result = search(-5, (1, 5, 10))
"""
        variable = 'search_result'
        line_number = len(code_block.splitlines())
        trace.trace_python(code_block)
        exec_trace = get_trace()
        # log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_recursion_error_9(self):
        code_block = """
def possible_change(coins, total):
    if total == 0:
        return 1
    if total < 0 or not coins:
        return 0

    first, *rest = coins
    return possible_change(coins, total - first) + possible_change(rest, total)
quix_result = possible_change([1, 3, 7, 42, 78], 140)
"""
        variable = 'quix_result'
        line_number = len(code_block.splitlines())
        trace.trace_python(code_block)
        exec_trace = get_trace()
        # log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))\

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_recursion_error_10(self):
        code_block = """
def possible_change(coins, total):
    if total == 0:
        return 1
    if total < 0 or not coins:
        return 0

    first, *rest = coins
    return possible_change(coins, total - first) + possible_change(rest, total)
quix_result = possible_change([1, 5, 10, 25], 140)
"""
        variable = 'quix_result'
        line_number = len(code_block.splitlines())
        trace.trace_python(code_block)
        exec_trace = get_trace()
        # log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))



def run_code(py_code, variable_name):
    globals_space = globals().copy()
    exec(compile(py_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]