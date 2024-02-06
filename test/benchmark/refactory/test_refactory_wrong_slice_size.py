import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import get_dynamic_slice, get_relevant_slice
from helpers.Logger import Logger

log = Logger()

#  Relevant Slices shorter than dynamic slices:
#  'benchmark/refactory/data/question_4/code/correct/correct_4_080.py#0:'
#  'benchmark/refactory/data/question_4/code/correct/correct_4_080.py#1:'
#  'benchmark/refactory/data/question_4/code/correct/correct_4_080.py#2:'
#  'benchmark/refactory/data/question_4/code/correct/correct_4_080.py#3:'
#  'benchmark/refactory/data/question_4/code/correct/correct_4_080.py#4:'
#  'benchmark/refactory/data/question_4/code/correct/correct_4_080.py#5:'
#  'benchmark/refactory/data/question_4/code/correct/correct_4_258.py#0:'
#  'benchmark/refactory/data/question_4/code/correct/correct_4_258.py#1:'
#  'benchmark/refactory/data/question_4/code/correct/correct_4_258.py#2:'
#  'benchmark/refactory/data/question_4/code/correct/correct_4_258.py#3:'
#  'benchmark/refactory/data/question_4/code/correct/correct_4_258.py#4:'
#  'benchmark/refactory/data/question_4/code/correct/correct_4_258.py#5:


class TestRefactoryWrongSliceSize(unittest.TestCase):
    def tearDown(self):
        clear_trace()

# Problem: age.remove(max(age)) is part of the dyn slice, but not of the relevant slice
# (1) Please check the metamorphic testing rules. This is a clear violation of dyn_slic \subset rel_slice and
#     should have been detected.
# (2) Reason: wrong set in data_target for line 11 and 7
# data_target should be 'age', not 'max('age') (line 11)
# data_target should be empty for line 7
# We have to tread len(x), x.remove(), max(x) properly in the traces process
# Note: the problem is hidden in dynamic slicing because, of the symmetric dependency which traverses the loop
# one more time and having then max(age) in the relevant  variables and analyzing
# lineno: 11	 type: p_call_before	data_target: ['max(age)']	 data_dep: [['age']]	again
#  and therefore adding the line.
    def test_correct_4_080_input0(self):
        code_block = """
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
    
result = sort_age([("F", 19)])
"""

        variable = 'result'
        line_number = 15
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_dyn_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)
        sliced_dyn_code = code_from_slice_ast(code_block, computed_dyn_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_dyn_code)

        computed_rel_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line_number)
        sliced_rel_code = code_from_slice_ast(code_block, computed_rel_slice, rel_bool_ops, exec_trace,
                                              func_param_removal)
        log.pretty_print_code(sliced_rel_code)


    def test_correct_4_080_modified(self):
        code_block = """
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

result = sort_age([("F", 19), ("F", 25)])
    """

        variable = 'result'
        line_number = 15
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_dyn_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line_number)
        sliced_dyn_code = code_from_slice_ast(code_block, computed_dyn_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(code_block)
        log.pretty_print_code(sliced_dyn_code)

        computed_rel_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line_number)
        sliced_rel_code = code_from_slice_ast(code_block, computed_rel_slice, rel_bool_ops, exec_trace,
                                              func_param_removal)
        log.pretty_print_code(sliced_rel_code)
