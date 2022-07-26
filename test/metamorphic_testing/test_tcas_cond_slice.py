import unittest

from parameterized import parameterized

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace, clear_trace
from helpers.Logger import Logger
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import get_dynamic_slice, get_pruned_slice
from test.metamorphic_testing.utils import get_test_parameters, add_function_call, run_sliced

log = Logger()

dummy_test_data = {'Number': '', 'Cur_Vertical_Sep': 0, 'High_Confidence': 0, 'Two_of_Three_Reports_Valid': 0,
         'Own_Tracked_Alt': 0, 'Own_Tracked_Alt_Rate': 0, 'Other_Tracked_Alt': 0, 'Alt_Layer_Value': 0,
         'Up_Separation': 0, 'Down_Separation': 0, 'Other_RAC': 0, 'Other_Capability': 0, 'Climb_Inhibit': 1,
         'Expected_output': 0}

tcas_test_code, line, variable = add_function_call(dummy_test_data)
tcas_augmented = trace.augment_python(tcas_test_code)


class TestTcasDynamicSlices(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    @parameterized.expand(get_test_parameters())
    def test_slice_tcas(self, test_number, test_data, expected):
        print(test_data)
        tcas_augmented_test = tcas_augmented.replace(str(dummy_test_data), str(test_data))
        tcas_test_code_test = tcas_test_code.replace(str(dummy_test_data), str(test_data))
        # tcas_test_code, line, variable = add_function_call(test_data)
        # trace.trace_python(tcas_test_code)
        # x = trace.augment_python(tcas_test_code)
        trace.run_trace(tcas_augmented_test)
        exec_trace = get_trace()
        # log.print_trace(exec_trace)
        computed_slice, rel_bool_ops, func_param_removal = get_pruned_slice(exec_trace, variable, line)
        print(computed_slice)
        sliced_code = code_from_slice_ast(tcas_test_code_test, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        # with open(get_directory() + '../test/tcas_dyn_slice_tests/output/' + test_number.lstrip('#').rstrip(':') + '.py', 'w') as fd:
        #     fd.write(sliced_code)

        # print(sliced_code)
        actual = run_sliced(sliced_code, variable)
        self.assertEqual(actual, expected)

