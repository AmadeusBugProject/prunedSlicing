import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.slice import get_dynamic_slice, get_pruned_slice
from helpers.Logger import Logger

log = Logger()


class TestTcasALIM(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_ALIM(self):
        code_block = """
POSITIVE_RA_ALT_THRESH_0 = 400                    # 2
POSITIVE_RA_ALT_THRESH_1 = 500                    # 3
POSITIVE_RA_ALT_THRESH_2 = 640                    # 4
POSITIVE_RA_ALT_THRESH_3 = 740                    # 5
        
class Tcas:                                       # 7
    def __init__(self, alt_layer_value):          # 8
        self.Alt_Layer_Value = alt_layer_value    # 9
        
    def ALIM(self):                               # 11
        if self.Alt_Layer_Value == 0:             # 12
            return POSITIVE_RA_ALT_THRESH_0
        elif self.Alt_Layer_Value == 1:           # 14
            return POSITIVE_RA_ALT_THRESH_1
        elif self.Alt_Layer_Value == 2:           # 16
            return POSITIVE_RA_ALT_THRESH_2
        else:
            return POSITIVE_RA_ALT_THRESH_3       # 19

tcas = Tcas(0)                                    # 21
result = tcas.ALIM()                              # 22
"""
        variable = 'result'
        line_number = 22
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice_dyn, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice_dyn = {2, 7, 8, 9, 11, 12, 13, 21, 22}
        self.assertEqual(expected_slice_dyn, computed_slice_dyn)

        computed_slice_cond, rel_bool_ops, _ = get_pruned_slice(exec_trace, variable, line_number)
        expected_slice_cond = {2, 7, 8, 9, 11, 12, 13, 21, 22}
        self.assertEqual(expected_slice_cond, computed_slice_cond)

    def test_ALIM2(self):
        code_block = """
POSITIVE_RA_ALT_THRESH_0 = 400                    # 2
POSITIVE_RA_ALT_THRESH_1 = 500                    # 3
POSITIVE_RA_ALT_THRESH_2 = 640                    # 4
POSITIVE_RA_ALT_THRESH_3 = 740                    # 5
        
class Tcas:                                       # 7
    def __init__(self, alt_layer_value):          # 8
        self.Alt_Layer_Value = alt_layer_value    # 9
        
    def ALIM(self):                               # 11
        if self.Alt_Layer_Value == 0:             # 12
            return POSITIVE_RA_ALT_THRESH_0
        elif self.Alt_Layer_Value == 1:           # 14
            return POSITIVE_RA_ALT_THRESH_1
        elif self.Alt_Layer_Value == 2:           # 16
            return POSITIVE_RA_ALT_THRESH_2
        else:
            return POSITIVE_RA_ALT_THRESH_3       # 19

tcas = Tcas(3)                                    # 21
result = tcas.ALIM()                              # 22
"""

        variable = 'result'
        line_number = 22
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice_dyn, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice_dyn = {5, 7, 8, 9, 11, 12, 14, 16, 19, 21, 22}
        self.assertEqual(expected_slice_dyn, computed_slice_dyn)

        computed_slice_cond, rel_bool_ops, _ = get_pruned_slice(exec_trace, variable, line_number)
        expected_slice_cond = {5, 7, 8, 9, 11, 12, 14, 16, 19, 21, 22}
        self.assertEqual(expected_slice_cond, computed_slice_cond)


