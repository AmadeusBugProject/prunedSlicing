import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.slice import get_dynamic_slice
from helpers.Logger import Logger

log = Logger()


class TestFor(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_simple_for(self):
        code_block = """
c = 0
stop = 2
for i in range(0, stop):
    c +=1
i = 8
"""
        variable = 'c'
        line_number = 6
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5}
        self.assertEqual(expected_slice, computed_slice)

    def test_simple_for2(self):
        code_block = """
c = 0
stop = 4
for i in range(0, stop):
    c +=1
c = i
"""
        variable = 'c'
        line_number = 6
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {3, 4, 6}
        self.assertEqual(expected_slice, computed_slice)

    def test_nested_for(self):
        code_block = """
c = 0
a = 0
stop = 2
staaap = 2
for i in range(0, stop):
    a += 1
    for j in range(0, staaap):
        c += 1
i = 8
"""
        variable = 'c'
        line_number = 10
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 4, 5, 6, 8, 9}
        self.assertEqual(expected_slice, computed_slice)

    def test_nested_for2(self):
        code_block = """
c = 0
a = 0
stop = 2
staaap = 2
for i in range(0, stop):
    a += 1
    for j in range(0, staaap):
        c += 1
i = 8
"""
        variable = 'i'
        line_number = 10
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {10}
        self.assertEqual(expected_slice, computed_slice)

    def test_nested_for3(self):
        code_block = """
c = 0
a = 0
stop = 2
staaap = 2
for i in range(0, stop):
    a += 1
    for j in range(0, staaap):
        c += 1
i = 8
"""
        variable = 'i'
        line_number = 9
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {4, 6}
        self.assertEqual(expected_slice, computed_slice)

    def test_break(self):
        code_block = """
a = 0
stop = 2
for i in range(0, stop):
    if a > 0:
        break
    a += 1
i = a
"""
        variable = 'i'
        line_number = 8
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        print(computed_slice)
        expected_slice = {2, 3, 4, 5, 6, 7, 8}
        self.assertEqual(expected_slice, computed_slice)

    def test_break2(self):
        code_block = """
a = 0
stop = 2
for i in range(0, stop):
    if a > 0:
        break
    a += 1
i = 4
"""
        variable = 'i'
        line_number = 8
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        print(computed_slice)
        expected_slice = {8}
        self.assertEqual(expected_slice, computed_slice)

    def test_break_tricky(self):
        code_block = """
a = 0
stop = 10
for i in range(0, stop):
    if a > 3:
      break
    a += 1
a = i
"""
        variable = 'a'
        line_number = 8
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5, 6, 7, 8}
        self.assertEqual(expected_slice, computed_slice)

    def test_continue(self):
        code_block = """
a = 0
stop = 2
for i in range(0, stop):
    if a > 0:
        continue
    a += 1
i = a
"""
        variable = 'i'
        line_number = 8
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        print(computed_slice)
        expected_slice = {2, 3, 4, 5, 6, 7, 8}
        self.assertEqual(expected_slice, computed_slice)

    def test_continue2(self):
        code_block = """
a = 0
stop = 2
b = 0
for i in range(0, stop):
    if i > 0:
        continue
    b += 1
i = a
"""
        variable = 'i'
        line_number = 9
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        print(computed_slice)
        expected_slice = {2, 9}
        self.assertEqual(expected_slice, computed_slice)

    def test_break_continue(self):
        code_block = """
a = 0
stop = 10
b = 0
for i in range(0, stop):
    if i % 2 == 1:
        continue
    if b > 1:
        break
    b += 1
i = b
"""
        variable = 'i'
        line_number = 11
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        print(computed_slice)
        expected_slice = {3, 4, 5, 6, 7, 8, 9, 10, 11}
        self.assertEqual(expected_slice, computed_slice)

    def test_break_continue_tricky(self):
        code_block = """
a = 0
stop = 10
b = 0
for i in range(0, stop):
    if i % 2 == 1:
        continue
    if b > 1:
        break
    b += 1
b = i
"""
        variable = 'b'
        line_number = 11
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        print(computed_slice)
        expected_slice = {3, 4, 5, 6, 7, 8, 9, 10, 11}
        self.assertEqual(expected_slice, computed_slice)

    def test_quix_return_issue(self):
        code_block = """
def next_permutation(perm):
    for i in range(len(perm) - 2, -1, -1):
        if perm[i] < perm[i + 1]:
            for j in range(len(perm) - 1, i, -1):
                if perm[j] < perm[i]:
                    next_perm = list(perm)
                    next_perm[i], next_perm[j] = perm[j], perm[i]
                    next_perm[i + 1:] = reversed(next_perm[i + 1:])
                    return next_perm
quix_result = next_permutation([3, 4])
"""
        variable = 'quix_result'
        line_number = 11
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)

    def test_for_else(self):
        code_block = """
def loop_with_else(n):
    j = 0
    for i in n:
        j += 1
    else:
        j -= 1
    return j
result = loop_with_else([3, 4])
"""
        variable = 'result'
        line_number = 9
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5, 7, 8, 9}
        self.assertEqual(expected_slice, computed_slice)
