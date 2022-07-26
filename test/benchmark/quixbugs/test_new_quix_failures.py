import unittest

from timeout_decorator import timeout_decorator

from ast_tree_tracer import trace
from ast_tree_tracer.augment import p_func_def, p_condition, p_if_label, p_return, p_call_after, p_call_before, p_or
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from constants import QUIX_TIMEOUT
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import get_dynamic_slice
from helpers.Logger import Logger
from slicing.dummy import Dummy

log = Logger()


def run_code(py_code, variable_name):
    globals_space = globals().copy()
    exec(compile(py_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]


class TestQuixFailure(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_quix1(self):
        code_block = """	
def bitcount(n):
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count
quix_result = bitcount(128)"""

        variable = 'quix_result'
        line_number = len(code_block.splitlines())
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

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_quix2(self):
        code_block = """
def levenshtein(source, target):
    if source == '' or target == '':
        return len(source) or len(target)

    elif source[0] == target[0]:
        return levenshtein(source[1:], target[1:])

    else:
        return 1 + min(
            levenshtein(source,     target[1:]),
            levenshtein(source[1:], target[1:]),
            levenshtein(source[1:], target)
        )

quix_result = levenshtein('kitten', 'sitting')"""

        variable = 'quix_result'
        line_number = len(code_block.splitlines())
        run_code(code_block, variable)
        log.pretty_print_code(code_block)

        augmented = trace.augment_python(code_block)

        log.pretty_print_code(augmented)
        trace.run_trace(augmented)
        exec_trace = get_trace()
        # log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_quix3(self):
        code_block = """
def levenshtein(source, target):
    if source == '' or target == '':
        return len(source) or len(target)
    elif source[0] == target[0]:
        return levenshtein(source[1:], target[1:])
    else:
        return 1 + min(levenshtein(source, target[1:]), levenshtein(source[1:], target[1:]), levenshtein(source[1:], target))
quix_result = levenshtein('hello', 'olleh')"""

        variable = 'quix_result'
        line_number = len(code_block.splitlines())
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
quix_result = mergesort([5, 4, 3, 1, 2])"""

        variable = 'quix_result'
        line_number = len(code_block.splitlines())
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

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_quix6(self):
        code_block = """
def find_first_in_sorted(arr, x):
    lo = 0
    hi = len(arr)

    while lo < hi:
        mid = (lo + hi) // 2

        if x == arr[mid] and (mid == 0 or x != arr[mid - 1]):
            return mid

        elif x <= arr[mid]:
            hi = mid

        else:
            lo = mid + 1

    return -1
quix_result = find_first_in_sorted([3, 4, 5, 5, 5, 5, 6], 5)
"""

        variable = 'quix_result'
        line_number = len(code_block.splitlines())
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

    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_quix7(self):
        code_block = """
def levenshtein(source, target):
    if source == '' or target == '':
        return len(source) or len(target)
    elif source[0] == target[0]:
        return levenshtein(source[1:], target[1:])
    else:
        return 1 + min(levenshtein(source, target[1:]), levenshtein(source[1:], target[1:]), levenshtein(source[1:], target))
quix_result = levenshtein('a', 'b')"""

        variable = 'quix_result'
        line_number = len(code_block.splitlines())
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

    # @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_quix8(self):
        code_block = """
def lis(arr):
    ends = {}
    longest = 0

    for i, val in enumerate(arr):

        prefix_lengths = [j for j in range(1, longest + 1) if arr[ends[j]] < val]

        length = max(prefix_lengths) if prefix_lengths else 0

        if length == longest or val < arr[ends[length + 1]]:
            ends[length + 1] = i
            longest = max(longest, length + 1)

    return longest
quix_result = lis([5, 1, 3, 4, 7])"""

        variable = 'quix_result'
        line_number = len(code_block.splitlines())
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





