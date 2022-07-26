import unittest

from ast_tree_tracer.trace import trace_python
from ast_tree_tracer.trace_container import clear_trace, get_trace
from helpers.Logger import Logger
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import get_dynamic_slice
from ast_tree_tracer.augment import *

log = Logger()


class TestEvaluationDifferentResult(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_parameter_by_reference_modified_inside_function(self):
        # benchmark/refactory/data/question_5/code/correct/correct_5_192.py#3:
        # bubble_sort(lst) explicitely returns None, but modifies the lst object that is passed as reference

        code_block = """
def bubble_sort(seq):
    changed = True
    while changed:
        changed = False
        for i in range(len(seq) - 1):
            if seq[i] < seq[i+1]:
                seq[i], seq[i+1] = seq[i+1], seq[i]
                changed = True
    return None
def top_k(lst, k):
    bubble_sort(lst)
    return lst[:k]
top_k_result = top_k([9, 9, 4, 9, 7, 9, 3, 1, 6], 5)"""
        variable = 'top_k_result'
        line_number = len(code_block.splitlines())
        trace_python(code_block)
        exec_trace = get_trace()
        # log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    def test_parameter_by_reference_modified_inside_function_minimized(self):
        # benchmark/refactory/data/question_5/code/correct/correct_5_192.py#3:
        # bubble_sort(lst) explicitely returns None, but modifies the lst object that is passed as reference

        code_block = """
def bubble_sort(seq):
    changed = True
    while changed:
        changed = False
        for i in range(len(seq) - 1):
            if seq[i] < seq[i+1]:
                seq[i], seq[i+1] = seq[i+1], seq[i]
                changed = True
    return None
def top_k(lst, k):
    bubble_sort(lst)
    return lst[:k]
top_k_result = top_k([4, 9], 1)"""
        variable = 'top_k_result'
        line_number = len(code_block.splitlines())
        trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    def test_parameter_by_reference_modified_inside_function_1(self):
        # benchmark/refactory/data/question_5/code/correct/correct_5_416.py#3:
        # newlist = sort(lst) although newlist is never used, lst is modified inside sort by reference, therefore not ending up in slice

        code_block = """
def sort(lst):
    a = 0
    for i in range(len(lst)-1):
        if lst[i]<lst[i+1]:
            lst.insert(i,lst[i+1])
            lst.pop(i+2)
            a += 1
    if a == 0:
        return lst
    else:
        return sort(lst)
        
def top_k(lst, k):
    newlist = sort(lst)
    finish = []
    for i in range(k):
        finish.append(lst[i])
    return finish
top_k_result = top_k([4, 5, 2, 3, 1, 6], 3)"""
        variable = 'top_k_result'
        line_number = len(code_block.splitlines())
        trace_python(code_block)
        exec_trace = get_trace()
        # log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    def test_parameter_by_reference_modified_inside_function_2(self):
        # benchmark/refactory/data/question_5/code/correct/correct_5_053.py#3:
        # insertion_sort(lst) modifies lst by reference and is not in slice

        code_block = """
def top_k(lst, num):
    def insertion_sort(lst):
        for i in range(len(lst)):
            if i == 0: continue
            else:
                while i > 0:
                    if lst[i] < lst[i-1]:
                        lst[i], lst[i-1] = lst[i-1], lst[i]
                        i -= 1
                    else: i = 0

    insertion_sort(lst)
    lst.reverse()
    
    score, result = -1, []
    for i in lst:
        if i == score:
            result += (i,)
        elif len(result) >= num: break
        else:
            result += (i,)
            score = i
    return result
top_k_result = top_k([4, 5, 2, 3, 1, 6], 3)"""
        variable = 'top_k_result'
        line_number = len(code_block.splitlines())
        trace_python(code_block)
        exec_trace = get_trace()
        # log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    def test_control_dependency_missing(self):
        # benchmark/refactory/data/question_4/code/correct/correct_4_296.py#4:
        # insertion_sort(lst) modifies lst by reference and is not in slice

        code_block = """
def sort_age(lst):
    def age(i):
        return i[1]
        
    def position(seq, ele):
        n = len(seq)
        for i in range(n):
            if seq[i] == ele:
                return i
                
    def largest_age(seq):
        largest = age(seq[0])
        largest_pos = 0
        for i in seq:
            if age(i) > largest:
                largest = age(i)
                largest_pos = position(seq,i)
        return seq[largest_pos]
    n = len(lst)
    final = []
    if n ==0:
        return []
    elif n ==1:
        return lst
    else:
        final = [largest_age(lst)]
        lst.remove(largest_age(lst))
        final = final + sort_age(lst)
        return final

sort_age_result = sort_age([("M", 23), ("F", 19), ("M", 30)])"""
        variable = 'sort_age_result'
        line_number = len(code_block.splitlines())
        trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)
        log.s(str(computed_slice))
        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))


    def test_dependecy_issue_importance_to_drop_some_items(self):
        # benchmark/refactory/data/question_3/code/correct/correct_3_056.py#5:
        # for the runs where checker=False is reached, the assignment in line 10 (l+=[i]) is not happening, therefore this statement is not in the slice.
        # the case here, in which the actual omission of something is in fact also changing the relevant variable is not considered in dynamic slicing i guess.

        code_block = """
def remove_extras(lst):
    l=[]
    for i in lst:
        checker=True
        for k in l:
            if k==i:
                checker=False
        if checker:
            l+=[i]
    return l
extras_result = remove_extras([3, 4, 5, 1, 3])"""
        variable = 'extras_result'
        line_number = len(code_block.splitlines())
        trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)
        log.s(str(computed_slice))
        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))




def run_code(py_code, variable_name):
    globals_space = globals().copy()
    exec(compile(py_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]
