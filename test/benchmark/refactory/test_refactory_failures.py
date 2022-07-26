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


class TestRefactory(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_index_out_of_range197(self):
        code_block = """
def search():
    y = 0
    for x in range(0,2):
        y += 1
    return y
search_result = search()
"""
        variable = 'search_result'
        line_number = 7
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

    def test_index_out_of_range199(self):
        code_block = """
def search():
    for i in range(0,2):
        return i
search_result = search()
"""
        variable = 'search_result'
        line_number = 5
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

    def test_for_else_construct1(self):
        # TODO: I recommend ignoring this, for else constructs

        # slicing.slicing_exceptions.InconsistentExecutionTraceException: Lineno: {'lineno': 6, 'type': 'p_call_after', 'info': 'len returns 6', 'control_dep': "6: p_call_before len ['seq']", 'data_target': ['len(seq)'], 'data_dep': [['seq']], 'class_range': [], 'func_name': '', 'bool_op': {}} Expecting type 'p_return, but got p_call_after

        code_block = """
def search():
    for i in range(0, 2):
        pass
    else:
        return 5
search_result = search()
"""
        variable = 'search_result'
        line_number = 7
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)
        # expected_slice = {2, 3, 4, 5}
        # self.assertEqual(expected_slice, computed_slice)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

    def test_nested_function_recursive(self):
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
search_result = search(100, [])
"""
        variable = 'search_result'
        line_number = 15
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    def test_nested_function1(self):
        code_block = """
def search(x, seq):
    index = 0
    def helper(index):
        return index
    return helper(index)
search_result = search(100, [])
"""
        variable = 'search_result'
        line_number = 7
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    @timeout_decorator.timeout(REFACTORY_TIMEOUT)
    def test_break_not_included_in_slice(self):
        code_block = """
def search(x,seq):
    counter=0
    y=len(seq)
    while counter<y:
        if x>seq[counter]:
            counter+=1
            continue
        break
    return counter
search_result = search(0, (-5, -1, 3, 5, 7, 10))
"""
        variable = 'search_result'
        line_number = 11
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    def test_break_not_included_in_slice2(self):
        code_block = """
def search(x, seq):
    position = 0
    while position < len(seq):
        if seq[position] == x:
             break
        elif seq[position] > x:
            break
        position = position + 1
    return position
search_result = search(3, (1, 5, 10))
"""
        variable = 'search_result'
        line_number = 11
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    def test_wrong_result1_break_missed(self):
        code_block = """
def search(x, seq):
    i=0
    while i<len(seq):
        if x<=seq[i]:
            break
        i=i+1 
    return i
search_result = search(0, (-5, -1, 3, 5, 7, 10))
    """
        variable = 'search_result'
        line_number = 9
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    def test_list_operations(self):
        # instance method calls should be included in slice if the object is out of our augmentation and we cannot assure that it doesnt change anything we slice for.

        code_block = """
def search():
    temp_list = []
    temp_list.append(1)
    return temp_list
search_result = search()
    """

        variable = 'search_result'
        line_number = 6
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    def test_wrong_result3(self):
        code_block = """
def search(x, seq):
    if seq==[]:
        return 0
    elif seq==():
        return 0
    else:
        for i,v in enumerate(seq):
            if x>v and i!=len(seq)-1:
                continue
            elif x>v and i==len(seq)-1:
                return i+1
            else:
                break
        
        return i
search_result = search(-100, (-5, -1, 3, 5, 7, 10))
    """

        variable = 'search_result'
        line_number = 17
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    def test_wrong_result4(self):
        code_block = """
def search(x,seq):
    if len(seq) == 0:
        return 0
    else:
        for i in range(len(seq)):
            if x > max(seq):
                return len(seq)
            elif x > seq[i]:
                continue
            elif x <= seq[i]:
                break
        return i
search_result = search(3, (1, 5, 10))
    """

        variable = 'search_result'
        line_number = 14
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    def test_code_gen_broken2(self):
        # top_level_boolop = list(filter(lambda x: x['target'][0] == target, boolops))[0]
        # IndexError: list index out of range

        code_block = """
def search(x, seq):
    for i,v in enumerate(seq):
        if x>v and i!=len(seq)-1:
            continue
        elif x>v and i==len(seq)-1:
            return i+1
        else:
            break
    
    return i
search_result = search(10, (-5, -1, 3, 5, 7, 10))
    """

        variable = 'search_result'
        line_number = 12
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    def test_tracer_broken1(self):
        #     if node.func.id == 'p_call_after' or node.func.id == 'p_call_before':
        # AttributeError: 'Attribute' object has no attribute 'id'

        code_block = """
seq = [10]
seq.insert(seq.index(10),5)
"""

        trace.trace_python(code_block)
        log.print_trace(get_trace())

    def test_tracer_broken2(self):
        #     IndexError: list index out of range

        code_block = """
def search(key, seq):
    lst = list(seq)
    n = len(lst)
    for i in range(n+1): #0,1,2,3 
        if i <= n-1 and key <= lst[i]:
            return i
    return n 
search_result = search(42, (-5, 1, 3, 5, 7, 10))
        """

        variable = 'search_result'
        line_number = 9
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))

    def test_tracer_broken3(self):
        #     IndexError: list index out of range

        code_block = """
def search(x, seq):
    if len(seq)==0 or x < seq[0]:
        return 0
    # for i in range(len(seq)-1):
    #     if seq[i] <= x <= seq[i+1]:
    #         return i+1
    # return len(seq)
search_result = search(100, [])
"""

        variable = 'search_result'
        line_number = 9
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

    def test_loop_missing1(self):
        #     ValueError: 42 is not in list -> seq.insert(seq.index(max_value) + 1,x) not in slice

        code_block = """
def search(x, seq):
    if len(seq) ==0 :
        return 0
    else:
        seq = list(seq)
        max_value = max(seq)
        for i,elem in enumerate(seq):
            if x > max_value:
                seq.insert(seq.index(max_value) + 1,x)
                break
            elif x<elem:
                y = max(0,i)
                seq.insert(y,x)
                break
    return seq.index(x)
search_result = search(42, [1, 5, 10])
"""

        variable = 'search_result'
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

    def test_empty_return(self):
        # AttributeError: 'NoneType' object has no attribute '_fields'

        code_block = """
def search():
    return
search_result = search()
"""

        variable = 'search_result'
        line_number = 4
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)
        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))


    def test_parameter_removal(self):
        code_block = """
def search(x, seq):
    counter = 0
    result = 0
    while counter < len(seq):
        if x < min(seq):
            result = 0
            break
        elif x > max(seq):
            result = len(seq)
            break
        elif x <= seq[counter]:
            result = counter
            break
        counter += 1
    return result
search_result = search(42, (-5, 1, 3, 5, 7, 10))
"""

        variable = 'search_result'
        line_number = 17
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)
        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)


    def test_for_else_test(self):
        code_block = """
def search(x, seq):
    index = []
    for i, elem in enumerate(seq):
        index += [[i, elem],]
    for i in index:
        if x <= i[1]:
            return i[0]
    else:
        return len(seq)
search_result = search(100, [])
"""

        variable = 'search_result'
        line_number = 11
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)
        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)

        self.assertEqual(run_code(code_block, variable), run_code(sliced_code, variable))


def run_code(py_code, variable_name):
    globals_space = globals().copy()
    exec(compile(py_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]