import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.slice import get_dynamic_slice
from helpers.Logger import Logger

log = Logger()


class TestTcasInhibitBiasedClimb(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_inhibit_biased_climb(self):
        code_block = """
NOZCROSS = 100                                         # 2        
class Tcas:                                            # 3
    def __init__(self, up_sep, climb):                 # 4
        self.Up_Separation = up_sep                    # 5
        self.Climb_Inhibit = climb                     # 6
    
    def Inhibit_Biased_Climb(self):                    # 8
        if self.Climb_Inhibit > 0:                     # 9
            return self.Up_Separation + NOZCROSS       # 10
        else:
            return self.Up_Separation                  # 12

tcas = Tcas(0, 0)                                      # 14
result = tcas.Inhibit_Biased_Climb()                   # 15
"""
        variable = 'result'
        line_number = 15
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {3, 4, 5, 6, 8, 9, 12, 14, 15}
        self.assertEqual(expected_slice, computed_slice)

    def test_inhibit_biased_climb2(self):
        code_block = """
NOZCROSS = 100                                         # 2        
class Tcas:                                            # 3
    def __init__(self, up_sep, climb):                 # 4
        self.Up_Separation = up_sep                    # 5
        self.Climb_Inhibit = climb                     # 6

    def Inhibit_Biased_Climb(self):                    # 8
        if self.Climb_Inhibit > 0:                     # 9
            return self.Up_Separation + NOZCROSS       # 10
        else:
            return self.Up_Separation                  # 12

tcas = Tcas(0, 1)                                      # 14
result = tcas.Inhibit_Biased_Climb()                   # 15
"""
        variable = 'result'
        line_number = 15
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, rel_bool_ops, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 5, 6, 8, 9, 10, 14, 15}
        self.assertEqual(expected_slice, computed_slice)