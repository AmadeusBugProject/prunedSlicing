import unittest

from ast_tree_tracer import trace_container
from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from helpers.Logger import Logger

log = Logger()

class TestIf(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_nested_if(self):
        code_block = """
i = 4
if i > 3:
    if i == 4:
        i = 7
    i = 8
i = 9
"""
        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # if i > 3:
        if_begin = get_trace()[2]
        self.assertEqual('p_if_begin', if_begin['type'])
        self.assertIn('p_if_begin', if_begin['info'])
        self.assertEqual('module', if_begin['control_dep'])
        self.assertEqual(['i'], if_begin['data_dep'])

        # if i == 4:
        if_begin = get_trace()[4]
        self.assertEqual('p_if_begin', if_begin['type'])
        self.assertIn('p_if_begin', if_begin['info'])
        self.assertEqual("3: p_if_begin p_condition(3, 'i > 3', ['i'], i > 3)", if_begin['control_dep'])
        self.assertEqual(['i'], if_begin['data_dep'])

        # i = 7
        assignment_trace = get_trace()[5]
        self.assertEqual('p_assignment', assignment_trace['type'])
        self.assertEqual("4: p_if_begin p_condition(4, 'i == 4', ['i'], i == 4)", assignment_trace['control_dep'])

        # end if i == 4:
        if_end = get_trace()[6]
        self.assertEqual('p_if_end', if_end['type'])
        self.assertIn('p_if_end', if_end['info'])
        self.assertEqual("4: p_if_begin p_condition(4, 'i == 4', ['i'], i == 4)", if_end['control_dep'])
        self.assertEqual(['i'], if_end['data_dep'])

        # i = 8
        assignment_trace = get_trace()[7]
        self.assertEqual('p_assignment', assignment_trace['type'])
        self.assertEqual("3: p_if_begin p_condition(3, 'i > 3', ['i'], i > 3)", assignment_trace['control_dep'])

        # end if i > 3:
        if_end = get_trace()[8]
        self.assertEqual('p_if_end', if_end['type'])
        self.assertIn('p_if_end', if_end['info'])
        self.assertEqual("3: p_if_begin p_condition(3, 'i > 3', ['i'], i > 3)", if_end['control_dep'])
        self.assertEqual(['i'], if_end['data_dep'])

        # i = 9
        assignment_trace = get_trace()[9]
        self.assertEqual('p_assignment', assignment_trace['type'])
        self.assertEqual('module', assignment_trace['control_dep'])

    def test_simple_if(self):
        code_block = """
i = 4
if i > 3:
    i = 7
i = 8
"""
        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # if i > 3:
        if_begin = get_trace()[2]
        self.assertEqual('p_if_begin', if_begin['type'])
        self.assertIn('p_if_begin', if_begin['info'])
        self.assertEqual('module', if_begin['control_dep'])
        self.assertEqual(['i'], if_begin['data_dep'])

        # i = 7
        assignment_trace = get_trace()[3]
        self.assertEqual('p_assignment', assignment_trace['type'])
        self.assertEqual("3: p_if_begin p_condition(3, 'i > 3', ['i'], i > 3)", assignment_trace['control_dep'])

        # if i > 3:
        if_end = get_trace()[4]
        self.assertEqual('p_if_end', if_end['type'])
        self.assertIn('p_if_end', if_end['info'])
        self.assertEqual("3: p_if_begin p_condition(3, 'i > 3', ['i'], i > 3)", if_end['control_dep'])
        self.assertEqual(['i'], if_end['data_dep'])

        # i = 8
        assignment_trace = get_trace()[5]
        self.assertEqual('p_assignment', assignment_trace['type'])
        self.assertEqual('module', assignment_trace['control_dep'])

    def test_multiple_data_dep_test_if(self):
        code_block = """
i = 4
a = 0
b = 3
if i > 3 and a != b:
    i = 7
"""
        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # if i > 3 and a != b:
        if_begin = get_trace()[6]
        self.assertEqual('p_if_begin', if_begin['type'])
        self.assertIn('p_if_begin', if_begin['info'])
        self.assertEqual('module', if_begin['control_dep'])
        self.assertEqual(['i > 3 and a != b'], if_begin['data_dep'])

        # todo data_target: ['((i > 3) and (a != b))']	 data_dep: ['(i > 3)', '(a != b)'] dependencies should be i, a, b

    def test_call_data_dep_test_if(self):
        code_block = """
a = 'foo'
b = 3
if len(a) == b:
    i = 7
"""
        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # if i > 3 and a != b:
        if_begin = get_trace()[5]
        self.assertEqual('p_if_begin', if_begin['type'])
        self.assertIn('p_if_begin', if_begin['info'])
        self.assertEqual('module', if_begin['control_dep'])
        self.assertEqual(['len(a)', 'b'], if_begin['data_dep'])

    def test_simple_else(self):
        code_block = """
i = 2
if i > 3:
    pass
else:
    i = 7
i = 8
"""
        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # if i > 3:
        p_else_begin = get_trace()[2]
        self.assertEqual('p_else_begin', p_else_begin['type'])
        self.assertIn('p_else_begin', p_else_begin['info'])
        self.assertEqual('module', p_else_begin['control_dep'])
        self.assertEqual(['i'], p_else_begin['data_dep'])

        # i = 7
        assignment_trace = get_trace()[3]
        self.assertEqual('p_assignment', assignment_trace['type'])
        self.assertEqual("3: p_else_begin p_condition(3, 'i > 3', ['i'], i > 3)", assignment_trace['control_dep'])

        # if i > 3:
        p_else_end = get_trace()[4]
        self.assertEqual('p_else_end', p_else_end['type'])
        self.assertIn('p_else_end', p_else_end['info'])
        self.assertEqual("3: p_else_begin p_condition(3, 'i > 3', ['i'], i > 3)", p_else_end['control_dep'])
        self.assertEqual(['i'], p_else_end['data_dep'])

        # i = 8
        assignment_trace = get_trace()[5]
        self.assertEqual('p_assignment', assignment_trace['type'])
        self.assertEqual('module', assignment_trace['control_dep'])


    def test_simple_elif(self):
        code_block = """
i = 2
j = 1
if i > 3:
    pass
elif j < 3:
    i = 7
i = 8
"""
        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # if i > 3:
        p_else_begin = get_trace()[3]
        self.assertEqual('p_else_begin', p_else_begin['type'])
        self.assertIn('p_else_begin', p_else_begin['info'])
        self.assertEqual('module', p_else_begin['control_dep'])
        self.assertEqual(['i'], p_else_begin['data_dep'])

        # elif i < 3:
        if_begin = get_trace()[5]
        self.assertEqual('p_if_begin', if_begin['type'])
        self.assertIn('p_if_begin', if_begin['info'])
        self.assertEqual("4: p_else_begin p_condition(4, 'i > 3', ['i'], i > 3)", if_begin['control_dep'])
        self.assertEqual(['j'], if_begin['data_dep'])

        # i = 7
        assignment_trace = get_trace()[6]
        self.assertEqual('p_assignment', assignment_trace['type'])
        self.assertEqual("6: p_if_begin p_condition(6, 'j < 3', ['j'], j < 3)", assignment_trace['control_dep'])

        # elif i < 3:
        if_end = get_trace()[7]
        self.assertEqual('p_if_end', if_end['type'])
        self.assertIn('p_if_end', if_end['info'])
        self.assertEqual("6: p_if_begin p_condition(6, 'j < 3', ['j'], j < 3)", if_end['control_dep'])
        self.assertEqual(['j'], if_end['data_dep'])

        # if i > 3:
        p_else_end = get_trace()[8]
        self.assertEqual('p_else_end', p_else_end['type'])
        self.assertIn('p_else_end', p_else_end['info'])
        self.assertEqual("4: p_else_begin p_condition(4, 'i > 3', ['i'], i > 3)", p_else_end['control_dep'])
        self.assertEqual(['i'], p_else_end['data_dep'])

        # i = 8
        assignment_trace = get_trace()[9]
        self.assertEqual('p_assignment', assignment_trace['type'])
        self.assertEqual('module', assignment_trace['control_dep'])

    def test_if_condition(self):
        code_block = """
i = 4
if i > 43:
    i = 7
i = 8
"""

        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # i > 3:
        p_else_begin = get_trace()[1]
        self.assertEqual('p_condition', p_else_begin['type'])
        self.assertEqual('module', p_else_begin['control_dep'])
        self.assertEqual(['i'], p_else_begin['data_dep'])