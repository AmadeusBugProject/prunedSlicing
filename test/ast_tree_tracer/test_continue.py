import unittest

from ast_tree_tracer import trace_container
from ast_tree_tracer.trace import trace_python
from ast_tree_tracer.trace_container import get_trace, clear_trace
from helpers.Logger import Logger

log = Logger()


class TestContinue(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_simple_continue(self):
        code_block = """
c = 0
for i in [1,2,3,4]:
    if i%2:
        continue
    c += 1
i = 8
"""
        trace_python(code_block)
        log.print_trace(get_trace())

        # for i in range(0, stop):
        for_begin = get_trace()[2]
        self.assertEqual('p_for_begin', for_begin['type'])
        self.assertIn('p_for_begin', for_begin['info'])
        self.assertEqual('module', for_begin['control_dep'])
        self.assertEqual([], for_begin['data_dep'])
        self.assertEqual(['i'], for_begin['data_target'])

        # continue
        cont = get_trace()[5]
        self.assertEqual('p_continue', cont['type'])
        self.assertEqual("4: p_if_begin p_condition(4, 'i % 2', ['i'], i % 2, [])", cont['control_dep'])

        # for i in range(0, stop):
        for_end = get_trace()[11]
        self.assertEqual('p_for_end', for_end['type'])
        self.assertIn('p_for_end', for_end['info'])
        self.assertEqual('3: p_for_begin target: i iter:[1, 2, 3, 4]', for_end['control_dep'])
        self.assertEqual([], for_end['data_dep'])
        self.assertEqual(['i'], for_end['data_target'])

        # i = 8
        assignment = get_trace()[25]
        self.assertEqual('p_assignment', assignment['type'])
        self.assertEqual('module', assignment['control_dep'])