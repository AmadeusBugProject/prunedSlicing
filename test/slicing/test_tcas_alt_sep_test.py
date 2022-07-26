import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.slice import get_dynamic_slice, get_pruned_slice
from helpers.Logger import Logger

log = Logger()


class TestTcasAltSepTest(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_alt_sep_test(self):
        code_block = """
OLEV = 600                                                                          # 2
MAXALTDIFF = 600                                                                    # 3
NO_INTENT = 0                                                                       # 4
TCAS_TA = 1                                                                         # 5
UNRESOLVED = 0                                                                      # 6

class Tcas:                                                                         # 8
    def __init__(self, parameters):                                                 # 9
        self.Cur_Vertical_Sep = parameters['Cur_Vertical_Sep']                      # 10
        self.High_Confidence = parameters['High_Confidence']                        # 11
        self.Two_of_Three_Reports_Valid = parameters['Two_of_Three_Reports_Valid']  # 12
        self.Own_Tracked_Alt_Rate = parameters['Own_Tracked_Alt_Rate']              # 13
        self.Other_RAC = parameters['Other_RAC']                                    # 14
        self.Other_Capability = parameters['Other_Capability']                      # 15
        
    def alt_sep_test(self):                                                         # 17
        enabled = self.High_Confidence and (self.Own_Tracked_Alt_Rate <= OLEV) and (self.Cur_Vertical_Sep > MAXALTDIFF)
        tcas_equipped = self.Other_Capability == TCAS_TA                            # 19
        intent_not_known = self.Two_of_Three_Reports_Valid and self.Other_RAC == NO_INTENT # 20
    
        alt_sep = UNRESOLVED                                                        # 22
    
        if enabled and ((tcas_equipped and intent_not_known) or not tcas_equipped): # 24
            alt_sep = UNRESOLVED                                                    # 25
        return alt_sep                                                              # 26
        
test_data = {'Number': '#0000:', 'Cur_Vertical_Sep': 958, 'High_Confidence': 1, 'Two_of_Three_Reports_Valid': 1, 'Own_Tracked_Alt': 2597, 'Own_Tracked_Alt_Rate': 574, 'Other_Tracked_Alt': 4253, 'Alt_Layer_Value': 0, 'Up_Separation': 399, 'Down_Separation': 400, 'Other_RAC': 0, 'Other_Capability': 0, 'Climb_Inhibit': 1, 'Expected_output': 0}
tcas_instance = Tcas(test_data)
alt_sep_actual = tcas_instance.alt_sep_test()                                      # 30
"""
        variable = 'alt_sep_actual'
        line_number = 30
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice_dyn, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice_dyn = {2, 3, 5, 6, 8, 9, 10, 11, 13, 15, 17, 18, 19, 24, 25, 26, 28, 29, 30}
        self.assertEqual(expected_slice_dyn, computed_slice_dyn)

        computed_slice_cond, rel_bool_ops, _ = get_pruned_slice(exec_trace, variable, line_number)
        expected_slice_cond = {2, 3, 5, 6, 8, 9, 10, 11, 13, 15, 17, 18, 19, 24, 25, 26, 28, 29, 30}
        self.assertEqual(expected_slice_cond, computed_slice_cond)

    def test_alt_sep_test2(self):
        code_block = """
OLEV = 600                                                                          # 2
MAXALTDIFF = 600                                                                    # 3
NO_INTENT = 0                                                                       # 4
TCAS_TA = 1                                                                         # 5
UNRESOLVED = 0                                                                      # 6

class Tcas:                                                                         # 8
    def __init__(self, parameters):                                                 # 9
        self.Cur_Vertical_Sep = parameters['Cur_Vertical_Sep']                      # 10
        self.High_Confidence = parameters['High_Confidence']                        # 11
        self.Two_of_Three_Reports_Valid = parameters['Two_of_Three_Reports_Valid']  # 12
        self.Own_Tracked_Alt_Rate = parameters['Own_Tracked_Alt_Rate']              # 13
        self.Other_RAC = parameters['Other_RAC']                                    # 14
        self.Other_Capability = parameters['Other_Capability']                      # 15

    def alt_sep_test(self):                                                         # 17
        enabled = self.High_Confidence and (self.Own_Tracked_Alt_Rate <= OLEV) and (self.Cur_Vertical_Sep > MAXALTDIFF)
        tcas_equipped = self.Other_Capability == TCAS_TA                            # 19
        intent_not_known = self.Two_of_Three_Reports_Valid and self.Other_RAC == NO_INTENT # 20

        if enabled and ((tcas_equipped and intent_not_known) or not tcas_equipped): # 22
            alt_sep = UNRESOLVED                                                    # 23
        else: 
            alt_sep = UNRESOLVED                                                    # 25
        return alt_sep                                                              # 26

test_data = {'Number': '#0000:', 'Cur_Vertical_Sep': 958, 'High_Confidence': 0, 'Two_of_Three_Reports_Valid': 1, 'Own_Tracked_Alt': 2597, 'Own_Tracked_Alt_Rate': 574, 'Other_Tracked_Alt': 4253, 'Alt_Layer_Value': 0, 'Up_Separation': 399, 'Down_Separation': 400, 'Other_RAC': 0, 'Other_Capability': 0, 'Climb_Inhibit': 1, 'Expected_output': 0}
tcas_instance = Tcas(test_data)
alt_sep_actual = tcas_instance.alt_sep_test()                                      # 30
"""
        variable = 'alt_sep_actual'
        line_number = 30
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice_dyn, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice_dyn = {6, 8, 9, 11, 17, 18, 22, 25, 26, 28, 29, 30}
        self.assertEqual(expected_slice_dyn, computed_slice_dyn)

        computed_slice_cond, rel_bool_ops, _ = get_pruned_slice(exec_trace, variable, line_number)
        expected_slice_cond = {6, 8, 9, 11, 17, 18, 22, 25, 26, 28, 29, 30}
        self.assertEqual(expected_slice_cond, computed_slice_cond)

    def test_alt_sep_test3(self):
        code_block = """
OLEV = 600                                                                          # 2
MAXALTDIFF = 600                                                                    # 3
NO_INTENT = 0                                                                       # 4
TCAS_TA = 1                                                                         # 5
UNRESOLVED = 0                                                                      # 6

class Tcas:                                                                         # 8
    def __init__(self, parameters):                                                 # 9
        self.Cur_Vertical_Sep = parameters['Cur_Vertical_Sep']                      # 10
        self.High_Confidence = parameters['High_Confidence']                        # 11
        self.Two_of_Three_Reports_Valid = parameters['Two_of_Three_Reports_Valid']  # 12
        self.Own_Tracked_Alt_Rate = parameters['Own_Tracked_Alt_Rate']              # 13
        self.Other_RAC = parameters['Other_RAC']                                    # 14
        self.Other_Capability = parameters['Other_Capability']                      # 15

    def alt_sep_test(self):                                                         # 17
        enabled = self.High_Confidence and (self.Own_Tracked_Alt_Rate <= OLEV) and (self.Cur_Vertical_Sep > MAXALTDIFF)
        tcas_equipped = self.Other_Capability == TCAS_TA                            # 19
        intent_not_known = self.Two_of_Three_Reports_Valid and self.Other_RAC == NO_INTENT # 20

        if enabled and ((tcas_equipped and intent_not_known) or not tcas_equipped): # 22
            alt_sep = UNRESOLVED                                                    # 23
        else: 
            alt_sep = UNRESOLVED                                                    # 25
        return alt_sep                                                              # 26

test_data = {'Number': '#0000:', 'Cur_Vertical_Sep': 958, 'High_Confidence': 1, 'Two_of_Three_Reports_Valid': 1, 'Own_Tracked_Alt': 2597, 'Own_Tracked_Alt_Rate': 674, 'Other_Tracked_Alt': 4253, 'Alt_Layer_Value': 0, 'Up_Separation': 399, 'Down_Separation': 400, 'Other_RAC': 0, 'Other_Capability': 0, 'Climb_Inhibit': 1, 'Expected_output': 0}
tcas_instance = Tcas(test_data)
alt_sep_actual = tcas_instance.alt_sep_test()                                      # 30
"""
        variable = 'alt_sep_actual'
        line_number = 30
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice_dyn, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice_dyn = {2, 6, 8, 9, 11, 13, 17, 18, 22, 25, 26, 28, 29, 30}
        self.assertEqual(expected_slice_dyn, computed_slice_dyn)

        computed_slice_cond, rel_bool_ops, _ = get_pruned_slice(exec_trace, variable, line_number)
        expected_slice_cond = {2, 6, 8, 9, 13, 17, 18, 22, 25, 26, 28, 29, 30}
        self.assertEqual(expected_slice_cond, computed_slice_cond)
