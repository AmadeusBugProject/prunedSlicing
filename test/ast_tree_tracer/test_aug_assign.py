import unittest

from ast_tree_tracer import trace_container
from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace


class TestAugAssign(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_simple_aug_assign(self):
        code_block = """
i = 0
i += 1
        """
        trace.trace_python(code_block)

        # i += 1
        aug_assignment = get_trace()[1]
        self.assertEqual('p_aug_assignment', aug_assignment['type'])
        self.assertEqual('module', aug_assignment['control_dep'])
        self.assertEqual(['i'], aug_assignment['data_dep'])
        self.assertEqual(['i'], aug_assignment['data_target'])

    def test_multi_assignment(self):
        code_block = """
i = 0
x = 5
i += x
        """

        trace.trace_python(code_block)

        # i += x
        aug_assignment = get_trace()[2]
        self.assertEqual('p_aug_assignment', aug_assignment['type'])
        self.assertEqual('module', aug_assignment['control_dep'])
        self.assertEqual(['x', 'i'], aug_assignment['data_dep'])
        self.assertEqual(['i'], aug_assignment['data_target'])
