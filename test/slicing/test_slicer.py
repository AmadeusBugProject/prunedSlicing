import glob
import json
import os
import unittest

from parameterized import parameterized

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace, clear_trace
from helpers.Logger import Logger
from slicing.slice import get_dynamic_slice, get_pruned_slice
from test.run_in_test import relative_to_project_root

log = Logger()


def get_directory():
    return relative_to_project_root('test/slicing/')


def add_function_call(python_code, function, input):
    function_call = function + '(' + ', '.join([str(i) for i in input]) + ')'
    lines = python_code.splitlines()
    lines.append(function_call)
    return '\n'.join(lines), len(lines)


def get_test_parameters():
    tests = []
    print(os.getcwd())
    for test in glob.glob(get_directory() + 'res/*.json'):
        with open(test, 'r') as fd:
            tests.extend(param_from_json(json.load(fd)))
    return tests


def param_from_json(test_json):
    tests = []

    file_name = test_json["testFile"]
    with open(get_directory() + 'res/' + file_name, 'r') as fd:
        python_code = fd.read()
    function = test_json["functionName"]
    for i, test_data in enumerate(test_json["testData"]):
        input = test_data["input"]
        code, added_line_no = add_function_call(python_code, function, input)

        tests.append([file_name + '_' + str(i),
                      file_name,
                      function,
                      code,
                      input,
                      test_data["sliceVariable"],
                      test_data["sliceLine"],
                      test_data["dynamicSlice"] + [added_line_no],
                      test_data["relevantSlice"] + [added_line_no],
                      test_data["prunedSlice"] + [added_line_no]
                      ])
    return tests


class TestDynamicSlices(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    @parameterized.expand(get_test_parameters())
    def test_dynamic_slicing(self, test_id, file_name, function, python_code, input, variable, line, dyn_slice, rel_slice, pruned_slice):
        trace.trace_python(python_code)
        exec_trace = get_trace()
        log.pretty_print_slice_criteria(line, variable)
        log.pretty_print_code(python_code)
        log.print_trace(exec_trace)
        computed_slice, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line)

        print(dyn_slice)
        print(computed_slice)
        self.assertEqual(set(dyn_slice), computed_slice)


class TestRelevantSlices(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    @parameterized.expand(get_test_parameters())
    def test_relevant_slicing(self, test_id, file_name, function, python_code, input, variable, line, dyn_slice, rel_slice, pruned_slice):
        trace.trace_python(python_code)
        exec_trace = get_trace()
        log.pretty_print_slice_criteria(line, variable)
        log.pretty_print_code(python_code)
        log.print_trace(exec_trace)
        computed_slice, rel_bool_ops, _ = get_pruned_slice(exec_trace, variable, line)

        print(pruned_slice)
        print(computed_slice)
        self.assertEqual(set(computed_slice), computed_slice)