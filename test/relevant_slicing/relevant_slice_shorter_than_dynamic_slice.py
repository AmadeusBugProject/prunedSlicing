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


class TestRelevantSliceShorterThanDynamicSlice(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def assert_slice_result(self, io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable, expected):
        sliced_code = code_from_slice_ast(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)
        actual = run_sliced(sliced_code, variable)
        self.assertEqual(expected, actual)

# test_refactory_slice_len_5271_correct_4_063_py0
# test_refactory_slice_len_5367_correct_4_080_py0
# test_refactory_slice_len_5427_correct_4_093_py0
# test_refactory_slice_len_5454_correct_4_101_py3
# test_refactory_slice_len_5454_correct_4_101_py4
# test_refactory_slice_len_5961_correct_4_258_py0
# test_refactory_slice_len_6123_correct_4_315_py0

    def test_refactory_slice_len_5454_correct_4_101_py3(self):
        io_py_code = """
def sort_age(lst):
    # Fill in your code here
    i = 1
    while i < len(lst):
        j = i
        while j>0 and lst[j-1][1] > lst[j][1]:
            lst[j], lst[j-1] = lst[j-1], lst[j]
            j-=1
        i+=1
    return lst[::-1]
sort_age_result = sort_age([("F", 18), ("M", 23), ("F", 19), ("M", 30)])
"""
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()

        log.print_trace(exec_trace)

        variable = 'sort_age_result'
        line = 12
        expected = [('M', 30), ('M', 23), ('F', 19), ('F', 18)]

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        dynamic_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        # ToDo: Describe in paper that this might happen
        self.assertGreater(dynamic_slice_len, relevant_slice_len)

    def test_refactory_slice_len_5454_correct_4_101_py4(self):
        io_py_code = """
def sort_age(lst):
    # Fill in your code here
    i = 1
    while i < len(lst):
        j = i
        while j>0 and lst[j-1][1] > lst[j][1]:
            lst[j], lst[j-1] = lst[j-1], lst[j]
            j-=1
        i+=1
    return lst[::-1]
sort_age_result = sort_age([("M", 23), ("F", 19), ("M", 30)])
"""
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()

        log.print_trace(exec_trace)

        variable = 'sort_age_result'
        line = 12
        expected = [("M", 30), ("M", 23), ("F", 19)]

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        dynamic_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        # ToDo: Describe in paper that this might happen
        self.assertGreater(dynamic_slice_len, relevant_slice_len)

    def test_refactory_slice_len_5367_correct_4_080_py0(self):
        io_py_code = """
def sort_age(lst):
    new_lst = []
    age = []
    for i in lst:
        age = age + [i[1],]
    while len(lst) != 0:
        for j in lst:
            if j[1] == max(age):
                lst.remove(j)
                age.remove(max(age))
                new_lst = new_lst + [j,]

    return new_lst

sort_age_result = sort_age([("F", 19)])
"""
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()

        log.print_trace(exec_trace)

        variable = 'sort_age_result'
        line = 16
        expected = [('F', 19)]

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        dynamic_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        # ToDo: Describe in paper that this might happen
        self.assertGreater(dynamic_slice_len, relevant_slice_len)

    def test_refactory_slice_len_5961_correct_4_258_py0(self):
        io_py_code = """
def sort_age(lst):
    newlst=[]
    lstages=[i[1] for i in lst]
    while lst:
        for i in lst:
            if i[1] == max(lstages):
                newlst+=[i]
                lst.remove(i)
                lstages.remove(i[1])
    return newlst
sort_age_result = sort_age([("F", 19)])
"""
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()

        log.print_trace(exec_trace)

        variable = 'sort_age_result'
        line = 12
        expected = [('F', 19)]

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        dynamic_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        # ToDo: Describe in paper that this might happen
        self.assertGreater(dynamic_slice_len, relevant_slice_len)

    def test_refactory_slice_len_5271_correct_4_063_py0(self):
        io_py_code = """
def sort_age(lst):
    all_age = []
    for person in lst:
        all_age += [person[1],]
    result = []
    while len(result) < len(lst):
        for person in lst:
            if person[1] == max(all_age):
                result += (person,)
        all_age.remove(max(all_age))
    return result
sort_age_result = sort_age([("F", 19)])
"""
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()

        log.print_trace(exec_trace)

        variable = 'sort_age_result'
        line = 13
        expected = [('F', 19)]

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        dynamic_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        # ToDo: Describe in paper that this might happen
        self.assertGreater(dynamic_slice_len, relevant_slice_len)

    def test_refactory_slice_len_5427_correct_4_093_py0(self):
        io_py_code = """
def sort_age(lst):
    res = []
    a=age_list(lst)
    while lst:
        for i in lst:
            if max(a) == i[1]:
                highest=i
                res= res + [i]
        lst.remove(highest)
        a.remove(highest[1])
    return res


def age_list(lst):
    age_list= []
    for i in range(len(lst)):
        age_list = age_list+ [lst[i][1]]
    return age_list
sort_age_result = sort_age([("F", 19)])
"""
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()

        log.print_trace(exec_trace)

        variable = 'sort_age_result'
        line = 20
        expected = [('F', 19)]

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        dynamic_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        # ToDo: Describe in paper that this might happen
        self.assertGreater(dynamic_slice_len, relevant_slice_len)

    def test_refactory_slice_len_6123_correct_4_315_py0(self):
        io_py_code = """
def sort_age(lst):
    res = []
    a=age_list(lst)
    while lst:
        for i in lst:
            if max(a) == i[1]:
                highest=i
                res= res + [i]
        lst.remove(highest)
        a.remove(highest[1])
    return res




def age_list(lst):
    age_list= []
    for i in range(len(lst)):
        age_list = age_list+ [lst[i][1]]
    return age_list
sort_age_result = sort_age([("F", 19)])
"""
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()

        log.print_trace(exec_trace)

        variable = 'sort_age_result'
        line = 22
        expected = [('F', 19)]

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        dynamic_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable,
                                 expected)

        # ToDo: Describe in paper that this might happen
        self.assertGreater(dynamic_slice_len, relevant_slice_len)

@timeout_decorator.timeout(REFACTORY_TIMEOUT)
def run_sliced(sliced_code, variable_name):
    globals_space = globals().copy()
    exec(compile(sliced_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]