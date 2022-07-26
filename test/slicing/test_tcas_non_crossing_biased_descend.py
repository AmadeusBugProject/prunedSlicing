import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.slice import get_dynamic_slice
from helpers.Logger import Logger

log = Logger()


class TestTcasALIM(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_non_crossing_biased_climb(self):
        code_block = """
POSITIVE_RA_ALT_THRESH_0 = 400                                          # 2
POSITIVE_RA_ALT_THRESH_1 = 500                                          # 3
POSITIVE_RA_ALT_THRESH_2 = 640                                          # 4
POSITIVE_RA_ALT_THRESH_3 = 740                                          # 5
NOZCROSS = 100                                                          # 6
MINSEP = 300                                                            # 7
        
class Tcas:                                                             # 9
    def __init__(self, Cur_Vertical_Sep, Own_Tracked_Alt, Other_Tracked_Alt, Alt_Layer_Value, Up_Separation, Down_Separation, Climb_Inhibit): # 10
        self.Cur_Vertical_Sep = Cur_Vertical_Sep                        # 11
        self.Own_Tracked_Alt = Own_Tracked_Alt                          # 12
        self.Other_Tracked_Alt = Other_Tracked_Alt                      # 13
        self.Alt_Layer_Value = Alt_Layer_Value                          # 14
        self.Up_Separation = Up_Separation                              # 15
        self.Down_Separation = Down_Separation                          # 16
        self.Climb_Inhibit = Climb_Inhibit                              # 17

    def Inhibit_Biased_Climb(self):                                     # 19
        if self.Climb_Inhibit > 0:                                      # 20
            return self.Up_Separation + NOZCROSS                        # 21
        else:
            return self.Up_Separation                                   # 23

    def ALIM(self):                                                     # 25
        if self.Alt_Layer_Value == 0:                                   # 26
            return POSITIVE_RA_ALT_THRESH_0                             # 27
        elif self.Alt_Layer_Value == 1:                                 # 28
            return POSITIVE_RA_ALT_THRESH_1                             # 29
        elif self.Alt_Layer_Value == 2:                                 # 30
            return POSITIVE_RA_ALT_THRESH_2                             # 31
        else:
            return POSITIVE_RA_ALT_THRESH_3                             # 33

    def Own_Below_Threat(self):                                         # 35
        return self.Own_Tracked_Alt < self.Other_Tracked_Alt            # 36
 
    def Own_Above_Threat(self):                                         # 38
        return self.Other_Tracked_Alt < self.Own_Tracked_Alt            # 39
        
    def Non_Crossing_Biased_Descend(self):                              # 41
        if self.Inhibit_Biased_Climb() > self.Down_Separation:          # 42
            upward_preferred = 1                                        # 43
        else:
            upward_preferred = 0                                        # 45
        if upward_preferred != 0:                                       # 46
            result = self.Own_Below_Threat() and (self.Cur_Vertical_Sep >= MINSEP) and (self.Down_Separation >= self.ALIM())  # 47
        else:
            result = not(self.Own_Above_Threat()) or ((self.Own_Above_Threat()) and (self.Up_Separation >= self.ALIM()))  # 49
        return result                                                   # 50

tcas = Tcas(1, 2, 3, 4, 5, 6, 7)                                        # 52
result = tcas.Non_Crossing_Biased_Descend()                             # 53
"""
        variable = 'result'
        line_number = 53
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {6, 7, 9, 10, 11, 12, 13, 15, 16, 17, 19, 20, 21, 35, 36, 41, 42, 43, 46, 47, 50, 52, 53}
        self.assertEqual(expected_slice, computed_slice)

    def test_non_crossing_biased_climb_part(self):
        code_block = """
POSITIVE_RA_ALT_THRESH_0 = 400                                          # 2
POSITIVE_RA_ALT_THRESH_1 = 500                                          # 3
POSITIVE_RA_ALT_THRESH_2 = 640                                          # 4
POSITIVE_RA_ALT_THRESH_3 = 740                                          # 5
MINSEP = 300                                                            # 6

class Tcas:                                                             # 8
    def __init__(self, Cur_Vertical_Sep, Alt_Layer_Value, Down_Separation): # 9 
        self.Cur_Vertical_Sep = Cur_Vertical_Sep                        # 10
        self.Alt_Layer_Value = Alt_Layer_Value                          # 11
        self.Down_Separation = Down_Separation                          # 12

    def ALIM(self):                                                     # 14
        if self.Alt_Layer_Value == 0:                                   # 15
            return POSITIVE_RA_ALT_THRESH_0                             # 16
        elif self.Alt_Layer_Value == 1:                                 # 17
            return POSITIVE_RA_ALT_THRESH_1                             # 18
        elif self.Alt_Layer_Value == 2:                                 # 19
            return POSITIVE_RA_ALT_THRESH_2                             # 20
        else:
            return POSITIVE_RA_ALT_THRESH_3                             # 22

    def Non_Crossing_Biased_Descend(self):                              # 24
        result = (self.Cur_Vertical_Sep >= MINSEP) and (self.Down_Separation >= self.ALIM())  # 25
        return result                                                   # 26

tcas = Tcas(1, 0, 3)                                                    # 28
result = tcas.Non_Crossing_Biased_Descend()                             # 29
"""
        variable = 'result'
        line_number = 29
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {6, 8, 9, 10, 24, 25, 26, 28, 29}
        self.assertEqual(expected_slice, computed_slice)

    def test_non_crossing_biased_climb_part2(self):
        code_block = """
POSITIVE_RA_ALT_THRESH_0 = 400                                          # 2
POSITIVE_RA_ALT_THRESH_1 = 500                                          # 3
POSITIVE_RA_ALT_THRESH_2 = 640                                          # 4
POSITIVE_RA_ALT_THRESH_3 = 740                                          # 5
MINSEP = 300                                                            # 6

class Tcas:                                                             # 8
    def __init__(self, Cur_Vertical_Sep, Alt_Layer_Value, Down_Separation): # 9 
        self.Cur_Vertical_Sep = Cur_Vertical_Sep                        # 10
        self.Alt_Layer_Value = Alt_Layer_Value                          # 11
        self.Down_Separation = Down_Separation                          # 12

    def ALIM(self):                                                     # 14
        if self.Alt_Layer_Value == 0:                                   # 15
            return POSITIVE_RA_ALT_THRESH_0                             # 16
        elif self.Alt_Layer_Value == 1:                                 # 17
            return POSITIVE_RA_ALT_THRESH_1                             # 18
        elif self.Alt_Layer_Value == 2:                                 # 19
            return POSITIVE_RA_ALT_THRESH_2                             # 20
        else:
            return POSITIVE_RA_ALT_THRESH_3                             # 22

    def Non_Crossing_Biased_Descend(self):                              # 24
        result = (self.Cur_Vertical_Sep >= MINSEP) and (self.Down_Separation >= self.ALIM())  # 25
        return result                                                   # 26

tcas = Tcas(3000, 0, 3)                                                 # 28
result = tcas.Non_Crossing_Biased_Descend()                             # 29
"""
        variable = 'result'
        line_number = 29
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 6, 8, 9, 10, 11, 12, 14, 15, 16, 24, 25, 26, 28, 29}
        self.assertEqual(expected_slice, computed_slice)