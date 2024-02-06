import unittest
import timeout_decorator

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.code_from_slice import get_boolop_replacements, code_from_slice_ast
from slicing.slice import get_dynamic_slice, get_relevant_slice
from helpers.Logger import Logger
from constants import REFACTORY_TIMEOUT

log = Logger()


class TestRefactoryTimeouts(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_refactory_slice_len_1468_correct_1_348_py5(self):
        io_py_code = """
def search(x, seq):
    n = 0
    a = 0
    while n < len(seq):
        if seq[n] < x:
            n = n + 1
            a = n
        else:
            break
    return a
search_result = search(-5, (1, 5, 10))
"""
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()
        log.print_trace(exec_trace)

        variable = 'search_result'
        line = 12
        expected = 0

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        dynamic_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable, expected)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable, expected)


    def test_refactory_slice_len_0918_correct_1_071_py5(self):
        io_py_code = """
def search(x, seq):
    i=0
    while i<len(seq):
        if x<=seq[i]:
            break
        i=i+1 
    return i
search_result = search(-5, (1, 5, 10))
"""
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()

        log.print_trace(exec_trace)

        variable = 'search_result'
        line = 9
        expected = 0

        # computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        # dynamic_slice_len = len(computed_slice)
        # self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable, expected)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable, expected)

    def test_refactory_slice_len_dunno(self):
        io_py_code = """
def remove_extras(lst):
    a = ()
    c = ()
    n = len(lst)
    for i in range(n):
        for j in range(i,n):
            if lst[i] == lst[j] and i != j:
                a += (j,) #j is the jth index of the list
            else:
                continue
    d = tuple(set(a)) #[repeated_index1, repeated_index2]
    for i in d:
        c += (lst[i],)
    b = lst[::-1]
    for j in range(len(c)):
        b.remove(c[j])
    e = b[::-1]
    return e
extras_result = remove_extras([])
"""
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()

        log.print_trace(exec_trace)

        variable = 'extras_result'
        line = 20
        expected = []
        #
        # computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        # dynamic_slice_len = len(computed_slice)
        # self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable, expected)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable, expected)

    def test_refactory_slice_len_4107_correct_3_061_py2(self):
        io_py_code = """
def remove_extras(lst):
    new_lst = []
    for element in lst:
        if element not in new_lst:
            new_lst.append(element)
    return new_lst
    
extras_result = remove_extras([])
"""
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()

        log.print_trace(exec_trace)

        variable = 'extras_result'
        line = 9
        expected = []

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        dynamic_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable, expected)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable, expected)

    def test_refactory_slice_len_0918_correct_3_071_py5(self):
        io_py_code = """
def search(x, seq):
    i=0
    while i<len(seq):
        if x<=seq[i]:
            break
        i=i+1 
    return i
search_result = search(-5, (1, 5, 10))
"""
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()

        log.print_trace(exec_trace)

        variable = 'search_result'
        line = 9
        expected = 0

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        dynamic_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable, expected)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable, expected)

    def assert_slice_result(self, io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable, expected):
        sliced_code = code_from_slice_ast(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)
        actual = run_sliced(sliced_code, variable)
        self.assertEqual(expected, actual)

    def test_refactory_slice_len_3910_correct_3_018_py1(self):
        io_py_code = """
def remove_extras(lst):
    lst.reverse()
    for i in lst:
        if lst.count(i) >1:
            j = 0
            while j < lst.count(i):
                lst.remove(i)
                j += 1
    lst.reverse()
    return lst
extras_result = remove_extras([1, 5, 1, 1, 3, 2])
"""
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()

        log.print_trace(exec_trace)

        variable = 'extras_result'
        line = 12
        expected = [1, 5, 3, 2]

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        dynamic_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

    def test_refactory_slice_len_5373_correct_4_081_py0(self):
        io_py_code = """
def sort_age(lst):
    n = len(lst)
    result = []
    while n != 0:
        test = []
        for counter in range(n):
            test.append(lst[counter][1])
        first = max(test)
        for counter in range(n):
            if counter == len(lst):
                break
            elif lst[counter][1] == first:
                result.append(lst.pop(counter))
        n = len(lst)
    return result
        
sort_age_result = sort_age([("F", 19)])
"""
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()

        log.print_trace(exec_trace)

        variable = 'sort_age_result'
        line = 18
        expected = [("F", 19)]

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        dynamic_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

    def test_refactory_slice_len_5580_correct_4_142_py3(self):  # ValueError: list.remove(x): x not in list beim dyn slice
        io_py_code = """
def sort_age(lst):
    # Fill in your code here
    sorted_list = []
    while lst:
        tpl = lst[0]
        gender = lst[0][0]
        oldest = lst[0][1]
        for i in lst:
            if i[1] > oldest:
                oldest = i[1]
                tpl = i
                gender = i[0]
        lst.remove(tpl)
        sorted_list.append((gender, oldest))
    return sorted_list
        
sort_age_result = sort_age([("F", 18), ("M", 23), ("F", 19), ("M", 30)])
"""
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()

        log.print_trace(exec_trace)

        variable = 'sort_age_result'
        line = 18
        expected = [('M', 30), ('M', 23), ('F', 19), ('F', 18)]

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        dynamic_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

    def test_refactory_slice_len_5580_correct_4_142_py3_short(
            self):  # ValueError: list.remove(x): x not in list beim dyn slice
        io_py_code = """
def sort_age(lst):
    # Fill in your code here
    sorted_list = []
    while lst:
        tpl = lst[0]
        gender = lst[0][0]
        oldest = lst[0][1]
        for i in lst:
            if i[1] > oldest:
                oldest = i[1]
                tpl = i
                gender = i[0]
        lst.remove(tpl)
        sorted_list.append((gender, oldest))
    return sorted_list

sort_age_result = sort_age([("F", 18), ("M", 23)])
"""
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()

        log.print_trace(exec_trace)

        variable = 'sort_age_result'
        line = 18
        expected = [('M', 23), ('F', 18)]

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        dynamic_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

    def test_relevant_no_timeout_dynamic_timeout_3873_correct_3_375_py0(self):
        io_py_code = """
def remove_extras(lst):
    n = 0
    a = lst
    while n < len(a):
        if a[n] in a[n + 1:]:
            b = a[n + 1:]
            b.remove(a[n])
            a = a[:n + 1] + b
        else:
            n = n + 1
    return a
extras_result = remove_extras([1, 1, 2])
"""
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()

        log.print_trace(exec_trace)

        variable = 'extras_result'
        line = 13
        expected = [[1, 2]]

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        sliced_code = code_from_slice_ast(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        sliced_code = code_from_slice_ast(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)


@timeout_decorator.timeout(REFACTORY_TIMEOUT)
def run_sliced(sliced_code, variable_name):
    globals_space = globals().copy()
    exec(compile(sliced_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]