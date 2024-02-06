import distutils.util
import glob
import heapq
import json
import os
import unittest
from collections import OrderedDict

import timeout_decorator

from parameterized import parameterized

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import clear_trace, get_trace
from helpers.Logger import Logger
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import get_dynamic_slice, get_pruned_slice, get_relevant_slice, get_pruned_relevant_slice
from constants import REFACTORY_TIMEOUT
from slicing.slicing_exceptions import SlicingException
from test.run_in_test import relative_to_project_root
from slicing.dummy import Dummy

log = Logger()

refactory_path = relative_to_project_root('benchmark/refactory/data/')

# questions = [{'question_path': refactory_path + 'question_1/',
#               'num_inputs': 11,
#               'output_type': int,
#               'slice_variable': 'search_result',
#               'input_dummy': 'search(0, (0, 0, 0, 0, 0, 0))'}]

questions = [
    {'question_path': refactory_path + 'question_1/',
     'num_inputs': 11,
     'output_type': int,
     'slice_variable': 'search_result',
     'input_dummy': 'search(0, (0, 0, 0, 0, 0, 0))',
     'add_globals': {}},
    # {'question_path': refactory_path + 'question_2/',
    #  'num_inputs': 17,
    #  'output_type': distutils.util.strtobool,
    #  'slice_variable': 'day_results',
    #  'input_dummy': 'unique_day("-1", tuple_of_possible_birthdays)',
    #  'add_globals': {'tuple_of_possible_birthdays': (('May', '15'),
    #                                                  ('May', '16'),
    #                                                  ('May', '19'),
    #                                                  ('June', '17'),
    #                                                  ('June', '18'),
    #                                                  ('July', '14'),
    #                                                  ('July', '16'),
    #                                                  ('August', '14'),
    #                                                  ('August', '15'),
    #                                                  ('August', '17'))}},
    {'question_path': refactory_path + 'question_3/',
     'num_inputs': 4,
     'output_type': json.loads,
     'slice_variable': 'extras_result',
     'input_dummy': 'remove_extras([0])',
     'add_globals': {'OrderedDict': OrderedDict}},
    {'question_path': refactory_path + 'question_4/',
     'num_inputs': 6,
     'output_type': eval,
     'slice_variable': 'sort_age_result',
     'input_dummy': 'sort_age([("X", -1)])',
     'add_globals': {}},
    {'question_path': refactory_path + 'question_5/',
     'num_inputs': 5,
     'output_type': json.loads,
     'slice_variable': 'top_k_result',
     'input_dummy': 'top_k([], -1)',
     'add_globals': {'heapq': heapq}},
]

def get_test_parameters():
    test_params = []
    for question in questions:
        test_params.extend(get_test_parameters_for_question(question['question_path'],
                                                            question['num_inputs'],
                                                            question['output_type'],
                                                            question['slice_variable'],
                                                            question['input_dummy']))
    return test_params


def get_test_parameters_for_question(question_path, num_inputs, output_type, slice_variable, input_dummy):
    code_path = question_path + 'code/correct/'

    io_params = []
    for io_number in range(1, num_inputs + 1):
        with open(question_path + 'ans/input_' + "{:03d}".format(io_number) + '.txt', 'r') as fd:
            func_call = slice_variable + ' = ' + fd.read()
        with open(question_path + 'ans/output_' + "{:03d}".format(io_number) + '.txt', 'r') as fd:
            expected = output_type(fd.read())  # to be
        io_params.append([func_call, expected])

    test_params = []
    for pyfile in glob.glob(code_path + '*.py'):
        with open(pyfile, 'r') as fd:
            py_code = '\n'.join(fd.read().splitlines() + [slice_variable + ' = ' + input_dummy])
        slice_line = len(py_code.splitlines())
        for number, io in enumerate(io_params):
            io_py_code = py_code.replace(slice_variable + ' = ' + input_dummy, io[0])
            test_name = pyfile.split('/')[-1] + str(number)
            test_params.append([test_name, io_py_code, io[1], slice_variable, slice_line])
    return test_params


class TestRefactorySliceLen(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    @parameterized.expand(get_test_parameters())
    def test_refactory_slice_len(self, test_name, io_py_code, expected, variable, line):
        try:
            log.pretty_print_code(io_py_code)
            io_augmented_code = trace.augment_python(io_py_code)
            trace.run_trace(io_augmented_code)
            exec_trace = get_trace()

            computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
            dynamic_slice_len = len(computed_slice)
            self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable, expected)

            computed_slice, rel_bool_ops, func_param_removal = get_pruned_slice(exec_trace, variable, line)
            pruned_dynamic_slice_len = len(computed_slice)
            self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable, expected)
        except AssertionError:
            self.skipTest('skipped due to dynamic slicing timeout')
        except SlicingException:
            self.skipTest('skipped due to dynamic slicing exception')

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
        relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable, expected)

        computed_slice, rel_bool_ops, func_param_removal = get_pruned_relevant_slice(exec_trace, variable, line)
        pruned_relevant_slice_len = len(computed_slice)
        self.assert_slice_result(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable, expected)

        log.s('dynamic slice length: ' + str(dynamic_slice_len))
        log.s('pruned dynamic slice length: ' + str(pruned_dynamic_slice_len))
        log.s('relevant slice length: ' + str(relevant_slice_len))
        log.s('pruned relevant slice length: ' + str(pruned_relevant_slice_len))

        self.assertLessEqual(dynamic_slice_len, relevant_slice_len)
        self.assertLessEqual(pruned_dynamic_slice_len, dynamic_slice_len)
        self.assertLessEqual(pruned_relevant_slice_len, relevant_slice_len)

    def assert_slice_result(self, io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal, variable, expected):
        sliced_code = code_from_slice_ast(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)
        actual = run_sliced(sliced_code, variable)
        self.assertEqual(expected, actual)

@timeout_decorator.timeout(REFACTORY_TIMEOUT)
def run_sliced(sliced_code, variable_name):
    globals_space = globals().copy()
    exec(compile(sliced_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]