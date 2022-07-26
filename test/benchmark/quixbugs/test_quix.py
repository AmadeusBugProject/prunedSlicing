import glob
import json
import os
import pathlib
import unittest
import timeout_decorator
import types

from parameterized import parameterized

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import clear_trace, get_trace
from constants import QUIX_TIMEOUT
from helpers.Logger import Logger
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import get_dynamic_slice
from test.run_in_test import relative_to_project_root
from slicing.dummy import Dummy

log = Logger()

quix_path = relative_to_project_root('benchmark/quixbugs/')
programs = [quix_path + 'correct_python_programs/',
            quix_path + 'python_programs']
test_input_path = quix_path + 'json_testcases/'

slice_variable = 'quix_result'

def get_test_parameters():
    test_params = []

    for program_file in glob.glob(quix_path + 'correct_python_programs/' + '*.py'): # only correct for now
        program_name = program_file.split('/')[-1].split('.')[0]
        test_input_file = test_input_path + program_name + '.json'

        if pathlib.Path(test_input_file).exists():
            with open(test_input_file, 'r') as fd:
                test_cases = fd.read().splitlines()
                test_cases = list(filter(lambda x: x.strip(), test_cases)) # remove empty lines
                test_cases = [json.loads(x) for x in test_cases]

            with open(program_file, 'r') as fd:
                py_code = fd.read()

            for i, test_case in enumerate(test_cases):
                test_name = program_name + '_' + str(i)

                if type(test_case[0]) is list:
                    func_params = str(test_case[0])[1:len(str(test_case[0]))-1]
                else:
                    func_params = str(test_case[0])

                function_call = program_name + '(' + func_params + ')'
                if 'yield ' in py_code:
                    function_call = 'list(' + function_call + ')'

                test_py_code = '\n'.join(py_code.splitlines() + [slice_variable + ' = ' + function_call])
                expected = test_case[1]
                slice_line = len(test_py_code.splitlines())
                test_params.append([test_name, test_py_code, expected, slice_variable, slice_line])
    return test_params

class TestQuix(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    @parameterized.expand(get_test_parameters())
    @timeout_decorator.timeout(QUIX_TIMEOUT)
    def test_quix(self, test_name, io_py_code, expected, slice_variable, slice_line):
        log.pretty_print_code(io_py_code)
        actual = run_code(io_py_code, slice_variable)
        self.assertEqual(expected, normalize_output(actual))


def normalize_output(output):
    # if isinstance(output, types.GeneratorType):
    #     output = list(output)
    return json.loads(json.dumps(output))


def run_code(sliced_code, variable_name):
    globals_space = globals().copy()
    exec(compile(sliced_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]
