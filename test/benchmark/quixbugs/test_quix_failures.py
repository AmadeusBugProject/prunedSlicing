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


class TestQuixFailure(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_quix1(self):
        code_block = """
def sqrt(x, epsilon):
    return x
quix_result = sqrt(2, 0.5)
"""

        variable = 'quix_result'
        line_number = 4
        run_code(code_block, variable)
        log.pretty_print_code(code_block)

        augmented = trace.augment_python(code_block)

        log.pretty_print_code(augmented)
        trace.run_trace(augmented)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    def test_array_index_augassign(self):
        code_block = """
counts = [0]
counts[0] += 1
"""

        variable = 'counts'
        line_number = 3
        run_code(code_block, variable)
        augmented = trace.augment_python(code_block)

        log.pretty_print_code(augmented)
        trace.run_trace(augmented)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    def test_array_index_assign(self):
        code_block = """
counts = [0]
counts[0] = 1
"""

        variable = 'counts'
        line_number = 3
        run_code(code_block, variable)
        augmented = trace.augment_python(code_block)

        log.pretty_print_code(augmented)
        trace.run_trace(augmented)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    def test_array_index_multiassign(self):
        code_block = """
x = [0,0]
y = [0,0]
x[0], y[1] = (1,2)
"""

        variable = 'x'
        line_number = 4
        run_code(code_block, variable)
        augmented = trace.augment_python(code_block)

        log.pretty_print_code(augmented)
        trace.run_trace(augmented)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_quix4(self):
        code_block = """
def mergesort(arr):
    def merge(left, right):
        result = []
        i = 0
        j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:] or right[j:])
        return result

    if len(arr) <= 1:
        return arr
    else:
        middle = len(arr) // 2
        left = mergesort(arr[:middle])
        right = mergesort(arr[middle:])
        return merge(left, right)
quix_result = mergesort([1, 2, 6, 72, 7, 33, 4])
"""

        variable = 'quix_result'
        line_number = 24
        run_code(code_block, variable)
        augmented = trace.augment_python(code_block)

        log.pretty_print_code(augmented)
        trace.run_trace(augmented)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_quix5(self):
        code_block = """
def next_palindrome(digit_list):
    high_mid = len(digit_list) // 2
    low_mid = (len(digit_list) - 1) // 2
    while high_mid < len(digit_list) and low_mid >= 0:
        if digit_list[high_mid] == 9:
            digit_list[high_mid] = 0
            digit_list[low_mid] = 0
            high_mid += 1
            low_mid -= 1
        else:
            digit_list[high_mid] += 1
            if low_mid != high_mid:
                digit_list[low_mid] += 1
            return digit_list
    return [1] + (len(digit_list) - 1) * [0] + [1]
quix_result = next_palindrome([9, 9, 9])
"""

        variable = 'quix_result'
        line_number = 17
        run_code(code_block, variable)
        augmented = trace.augment_python(code_block)

        log.pretty_print_code(augmented)
        trace.run_trace(augmented)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_quix6(self):
        code_block = """
def subsequences(a, b, k):
    if k == 0:
        return [[]]

    ret = []
    for i in range(a, b + 1 - k):
        ret.extend([i] + rest for rest in subsequences(i + 1, b, k - 1))

    return ret

quix_result = subsequences(1, 5, 3)
"""

        variable = 'quix_result'
        line_number = 12
        run_code(code_block, variable)
        augmented = trace.augment_python(code_block)

        log.pretty_print_code(augmented)
        trace.run_trace(augmented)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_quix7(self):
        code_block = """
def longest_common_subsequence(a, b):
    if not a or not b:
        return ''

    elif a[0] == b[0]:
        return a[0] + longest_common_subsequence(a[1:], b[1:])

    else:
        return max(longest_common_subsequence(a, b[1:]), longest_common_subsequence(a[1:], b), key=len)

quix_result = longest_common_subsequence('1234', '1224533324')
"""

        variable = 'quix_result'
        line_number = 12
        run_code(code_block, variable)
        augmented = trace.augment_python(code_block)

        log.pretty_print_code(augmented)
        trace.run_trace(augmented)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_quix8(self):
        code_block = """
def hanoi(height, start=1, end=3):
    steps = []
    if height > 0:
        helper = ({1, 2, 3} - {start} - {end}).pop()
        steps.extend(hanoi(height - 1, start, helper))
        steps.append((start, end))
        steps.extend(hanoi(height - 1, helper, end))
    
    return steps
quix_result = hanoi(1, 1, 3)
"""

        variable = 'quix_result'
        line_number = 11
        run_code(code_block, variable)
        augmented = trace.augment_python(code_block)

        log.pretty_print_code(code_block)
        trace.run_trace(augmented)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_incorrect_slice_dropping_most_of_function(self):
        code_block = """
def get_factors(n):
    if n == 1:
        return []

    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return [i] + get_factors(n // i)

    return [n]
quix_result = get_factors(83)
"""

        variable = 'quix_result'
        line_number = 11
        run_code(code_block, variable)
        augmented = trace.augment_python(code_block)

        log.pretty_print_code(augmented)
        trace.run_trace(augmented)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_wrong_result(self):
        code_block = """
def bitcount(n):
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count
quix_result = bitcount(5)
"""

        variable = 'quix_result'
        line_number = 8
        run_code(code_block, variable)
        augmented = trace.augment_python(code_block)

        log.pretty_print_code(augmented)
        trace.run_trace(augmented)
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