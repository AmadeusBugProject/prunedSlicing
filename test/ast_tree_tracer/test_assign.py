import unittest

from ast_tree_tracer import trace_container
from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from helpers.Logger import Logger

log = Logger()

class TestAssign(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_num_assign(self):
        code_block = """
i = 4
        """

        trace.trace_python(code_block)

        # i = 4
        assignment_trace = get_trace()[0]
        self.assertEqual('p_assignment', assignment_trace['type'])
        self.assertEqual('module', assignment_trace['control_dep'])
        self.assertEqual([], assignment_trace['data_dep'])
        self.assertEqual(['i'], assignment_trace['data_target'])

    def test_multi_assignment(self):
        code_block = """
i, j = (4, 5)
        """

        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # i = 4
        assignment_trace = get_trace()[0]
        self.assertEqual('p_assignment', assignment_trace['type'])
        self.assertEqual('module', assignment_trace['control_dep'])
        self.assertEqual([], assignment_trace['data_dep'])
        self.assertEqual(['i', 'j'], assignment_trace['data_target'])

    def test_var_assign(self):
        code_block = """
a = 1
i = a
        """

        trace.trace_python(code_block)
        log.print_trace(get_trace())
        # i = a
        assignment_trace = get_trace()[1]
        self.assertEqual('p_assignment', assignment_trace['type'])
        self.assertEqual('module', assignment_trace['control_dep'])
        self.assertEqual(['a'], assignment_trace['data_dep'])
        self.assertEqual(['i'], assignment_trace['data_target'])
