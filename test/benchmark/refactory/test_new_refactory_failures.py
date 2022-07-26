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
from constants import REFACTORY_TIMEOUT

log = Logger()


class TestNewRefactoryFailures(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    # @timeout_decorator.timeout(REFACTORY_TIMEOUT)
    def test_timeout_1(self):
        code_block = """
def search(x, seq):
    position = 0
    found = False

    while position < len(seq) and not found:
        if x <= seq[position]:
            found = True
        else:
            position += 1

    return position
search_result = search(5, (1, 5, 10))"""
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

    # @timeout_decorator.timeout(REFACTORY_TIMEOUT)
    def test_timeout_2(self):
        code_block = """
def search(x, seq):
    new_seq=list(seq)
    new_seq.append(x)
    sort=[]
    while new_seq:
        smallest=new_seq[0]
        for element in new_seq:
            if element<smallest:
                smallest=element
        new_seq.remove(smallest)
        sort.append(smallest)
    for i,elem in enumerate(sort):
        if elem==x:
            return i
search_result = search(-100, ())"""
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

    # @timeout_decorator.timeout(REFACTORY_TIMEOUT)
    def test_timeout_3(self):
        code_block = """
def search(x, seq):
    lst = list(seq)
    lst.append(x)
    sort = []
    while lst:
        smallest = lst[0]
        for ele in lst:
            if ele < smallest:
                smallest = ele
        lst.remove(smallest)
        sort.append(smallest)
    for i in range(len(sort)):
        if sort[i] ==x:
            return i
search_result = search(-100, ())"""
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

    # @timeout_decorator.timeout(REFACTORY_TIMEOUT)
    def test_timeout_5(self):
        code_block = """
def search(x, seq):
    position = 0
    found = False
    
    while position < len(seq) and not found:
        if x <= seq[position]:
            found = True
        else:
            position += 1
    
    return position
search_result = search(3, (1, 5, 10))"""
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
def run_code(py_code, variable_name):
    globals_space = globals().copy()
    exec(compile(py_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]