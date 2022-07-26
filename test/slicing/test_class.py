import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.slice import get_dynamic_slice
from helpers.Logger import Logger

log = Logger()


class TestClasses(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_method_call(self):
        code_block = """
class Tcas:
    a = 1
    def __init__(self, x):             # 4
        self.A = x                     # 5

    def get_sum(self):
        return self.A                  # 8

a = 2                                  # 10
tcas = Tcas(a)                         # 11
z = tcas.get_sum()                     # 12
"""
        variable = 'z'
        line_number = 12
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())
        log.pretty_print_code(code_block)

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 4, 5, 7, 8, 10, 11, 12}
        self.assertEqual(expected_slice, computed_slice)

    def test_method_call2(self):
        code_block = """ 
class Tcas:
    a = 1
    def __init__(self, x):        # 4
        self.A = x                # 5
        
    def set_A(self, a):           # 7
        self.A = a                # 8

    def get_sum(self):            
        return self.A             # 11

a = 2
b = 3                             # 14
tcas = Tcas(a)                    # 15
tcas.set_A(b)                     # 16
z = tcas.get_sum()                # 17
"""
        variable = 'z'
        line_number = 17
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 4, 7, 8, 10, 11, 14, 15, 16, 17}
        self.assertEqual(expected_slice, computed_slice)

    def test_method_call3(self):
        code_block = """ 
class Tcas:
    def __init__(self, x, y):      # 3
        self.A = x
        self.B = y                 # 5

    def set_A(self, a):            # 7
        self.A = a                 # 8
        
    def set_B(self, b):
        self.B = b

    def get_sum(self):             # 13
        return self.A+self.B       # 14

a = 2
b = 3       
tcas = Tcas(a,b)
tcas.set_A(b)
z = tcas.get_sum()
"""
        variable = 'z'
        line_number = 20
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 5, 7, 8, 13, 14, 17, 18, 19, 20}
        self.assertEqual(expected_slice, computed_slice)

    def test_method_call4(self):
        code_block = """ 
class Tcas:
    def __init__(self, x, y):   # 3
        self.A = x
        self.B = y

    def set_A(self, a):         # 7
        self.A = a              # 8

    def set_B(self, b):         # 10
        self.B = b              # 11

    def get_sum(self):          # 13
        return self.A+self.B    # 14

a = 2
b = 3                           # 17
tcas = Tcas(a,b)                # 18
tcas.set_A(b)                   # 19
tcas.set_B(b)                   # 20
z = tcas.get_sum()              # 21
"""
        variable = 'z'
        line_number = 21
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 7, 8, 10, 11, 13, 14, 17, 18, 19, 20, 21}
        self.assertEqual(expected_slice, computed_slice)

    def test_init(self):
        code_block = """
class Tcas:
    def __init__(self, x):   # 3
        self.A = x           # 4

tcas = Tcas(0)               # 6
"""
        variable = 'tcas'
        line_number = 6
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 6}
        self.assertEqual(expected_slice, computed_slice)

    def test_init2(self):
        code_block = """
class Tcas:
    def __init__(self, x):   # 3
        self.A = x           # 4

tcas = Tcas(0)               # 6
z = tcas.A                   # 7
"""
        variable = 'z'
        line_number = 7
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 4, 6, 7}
        self.assertEqual(expected_slice, computed_slice)

    def test_init3(self):
        code_block = """
class Tcas:
    def __init__(self):     # 3
        pass                # 4

tcas = Tcas()               # 6
"""
        variable = 'tcas'
        line_number = 6
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 6}
        self.assertEqual(expected_slice, computed_slice)

    def test_init4(self):
        code_block = """
class Tcas:
    def __init__(self, x):   # 3
        self.A = x           # 4

tcas = Tcas(0)               # 6
z = 0                        # 7
"""
        variable = 'tcas'
        line_number = 7
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        computed_slice, _, _ = get_dynamic_slice(exec_trace, variable, line_number)
        expected_slice = {2, 3, 6}
        self.assertEqual(expected_slice, computed_slice)
