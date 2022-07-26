import glob
import os
import unittest
import timeout_decorator

from parameterized import parameterized

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import clear_trace, get_trace
from helpers.Logger import Logger
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import get_dynamic_slice
from constants import REFACTORY_TIMEOUT
from test.run_in_test import relative_to_project_root
from slicing.dummy import Dummy

log = Logger()

refactory_path = relative_to_project_root('benchmark/refactory/data/')

questions = [{'question_path': refactory_path + 'question_1/',
              'num_inputs': 11,
              'output_type': int,
              'slice_variable': 'search_result',
              'input_dummy': 'search(0, (0, 0, 0, 0, 0, 0))'}]


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


class TestRefactory(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    @parameterized.expand(get_test_parameters())
    def test_dyn_refactory(self, test_name, io_py_code, expected, slice_variable, slice_line):
        log.pretty_print_code(io_py_code)
        io_augmented_code = trace.augment_python(io_py_code)
        trace.run_trace(io_augmented_code)
        exec_trace = get_trace()
        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, slice_variable, slice_line)
        print(computed_slice)
        sliced_code = code_from_slice_ast(io_py_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)
        actual = run_sliced(sliced_code, slice_variable)
        self.assertEqual(expected, actual)

@timeout_decorator.timeout(REFACTORY_TIMEOUT)
def run_sliced(sliced_code, variable_name):
    globals_space = globals().copy()
    exec(compile(sliced_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]