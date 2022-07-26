import unittest

from ast_tree_tracer import trace_container
from ast_tree_tracer.trace import trace_python
from ast_tree_tracer.trace_container import get_trace, clear_trace
from helpers.Logger import Logger

log = Logger()


class TestPass(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_pass(self):
        code_block = """
c = 0
pass
c = 1
"""
        trace_python(code_block)
        log.print_trace(get_trace())

        # pass
        p_pass = get_trace()[1]
        self.assertEqual('p_pass', p_pass['type'])
        self.assertIn('', p_pass['info'])
        self.assertEqual('module', p_pass['control_dep'])
        self.assertEqual([], p_pass['data_dep'])
        self.assertEqual([], p_pass['data_target'])
