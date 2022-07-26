import os
import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import get_dynamic_slice
from helpers.Logger import Logger
from slicing.dummy import Dummy

log = Logger()


def get_directory():
    if os.getcwd().endswith('code_gen'):
        return '../../benchmark/tcas/'
    if os.getcwd().endswith('test'):
        return '../benchmark/tcas/'
    return 'benchmark/tcas/'


with open(get_directory() + 'Tcas.py', 'r') as fd:
    tcas_code = fd.read().splitlines()


def add_function_call(test_data):
    lines = tcas_code.copy()
    lines.append('test_data = ' + str(test_data))
    lines.append('tcas_instance = Tcas(test_data)')
    lines.append('alt_sep_actual = tcas_instance.alt_sep_test()')
    return '\n'.join(lines), len(lines), 'alt_sep_actual'


class TestTcas0001FuncException(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_base_tcas_with_param(self):
        test_data = {'Number': '#0000:', 'Cur_Vertical_Sep': 958, 'High_Confidence': 1, 'Two_of_Three_Reports_Valid': 1,
                     'Own_Tracked_Alt': 2597, 'Own_Tracked_Alt_Rate': 574, 'Other_Tracked_Alt': 4253, 'Alt_Layer_Value': 0,
                     'Up_Separation': 399, 'Down_Separation': 400, 'Other_RAC': 0, 'Other_Capability': 0, 'Climb_Inhibit': 1,
                     'Expected_output': 0}


        tcas_test_code, line, variable = add_function_call(test_data)
        # with open('uninitialized_tcas.py', 'w') as fd:
        #     fd.write(tcas_test_code)

        trace.trace_python(tcas_test_code)
        exec_trace = get_trace()
        log.print_trace(exec_trace)
        computed_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
        print(computed_slice)
        sliced_code = code_from_slice_ast(tcas_test_code, computed_slice, rel_bool_ops, exec_trace, func_param_removal)

        # with open('uninitialized_sliced_tcas.py', 'w') as fd:
        #     fd.write(sliced_code)

        # print(sliced_code)
        actual = run_sliced(sliced_code, variable)
        self.assertEqual(actual, test_data['Expected_output'])


def run_sliced(sliced_code, variable_name):
    globals_space = globals().copy()
    exec(compile(sliced_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]
