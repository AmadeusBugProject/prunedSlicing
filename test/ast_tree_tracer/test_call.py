import ast
import unittest

from ast_tree_tracer import trace_container
from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from helpers.Logger import Logger

log = Logger()

class TestCall(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_simple_call(self):
        code_block = """
print('a')
z = 1
        """
        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # before
        before = get_trace()[0]
        self.assertEqual('p_call_before', before['type'])
        self.assertEqual('module', before['control_dep'])
        self.assertEqual([[]], before['data_dep'])
        self.assertEqual(["print('a')"], before['data_target'])

        # after
        after = get_trace()[1]
        self.assertEqual('p_call_after', after['type'])
        self.assertEqual("2: p_call_before print [\"'a'\"]", after['control_dep'])
        self.assertEqual([[]], after['data_dep'])
        self.assertEqual(["print('a')"], after['data_target'])

        # z = 1
        assign = get_trace()[2]
        self.assertEqual('p_assignment', assign['type'])
        self.assertEqual('module', assign['control_dep'])
        self.assertEqual([], assign['data_dep'])
        self.assertEqual(['z'], assign['data_target'])

    def test_parameter_call(self):
        code_block = """
x = 'a'
y = 'b'
print(x + y)
z = 1
"""
        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # before
        before = get_trace()[2]
        self.assertEqual('p_call_before', before['type'])
        self.assertEqual('module', before['control_dep'])
        self.assertEqual([['x', 'y']], before['data_dep'])
        self.assertEqual(['print(x + y)'], before['data_target'])

        # after
        after = get_trace()[3]
        self.assertEqual('p_call_after', after['type'])
        self.assertEqual('4: p_call_before print [\'x + y\']', after['control_dep'])
        self.assertEqual([['x', 'y']], after['data_dep'])
        self.assertEqual(['print(x + y)'], after['data_target'])

        # z = 1
        assign = get_trace()[4]
        self.assertEqual('p_assignment', assign['type'])
        self.assertEqual('module', assign['control_dep'])
        self.assertEqual([], assign['data_dep'])
        self.assertEqual(['z'], assign['data_target'])

    def test_multi_parameter_call(self):
        code_block = """
def dummy(x, y):
    return x + y
a = 1
b = 2
dummy(a, b)
z = 1
        """
        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # before
        before = get_trace()[2]
        self.assertEqual('p_call_before', before['type'])
        self.assertEqual('module', before['control_dep'])
        self.assertEqual([['a'], ['b']], before['data_dep'])
        self.assertEqual(['dummy(a, b)'], before['data_target'])

        # def dummy(x, y):
        p_func_def = get_trace()[3]
        self.assertEqual('p_func_def', p_func_def['type'])
        self.assertEqual("6: p_call_before dummy ['a', 'b']", p_func_def['control_dep'])
        self.assertEqual([], p_func_def['data_dep'])
        self.assertEqual(['x', 'y'], p_func_def['data_target'])

        # after
        after = get_trace()[5]
        self.assertEqual('p_call_after', after['type'])
        self.assertEqual("6: p_call_before dummy ['a', 'b']", after['control_dep'])
        self.assertEqual([['a'], ['b']], after['data_dep'])
        self.assertEqual(['dummy(a, b)'], after['data_target'])

        # z = 1
        assign = get_trace()[6]
        self.assertEqual('p_assignment', assign['type'])
        self.assertEqual('module', assign['control_dep'])
        self.assertEqual([], assign['data_dep'])
        self.assertEqual(['z'], assign['data_target'])

    def test_inlined_call(self):
        code_block = """
def dummy(x, y):
    return x + y
a = 1
b = 2
c = 3
x = dummy(a, dummy(b, c))
c = 1
        """
        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # before dummy(x, dummy(y, z))
        before = get_trace()[3]
        self.assertEqual('p_call_before', before['type'])
        self.assertEqual('module', before['control_dep'])
        self.assertEqual([['a'], ['dummy(b, c)']], before['data_dep'])
        self.assertEqual(['dummy(a, dummy(b, c))'], before['data_target'])

        # before dummy(y, z)
        before = get_trace()[4]
        self.assertEqual('p_call_before', before['type'])
        self.assertEqual("7: p_call_before dummy ['a', 'dummy(b, c)']", before['control_dep'])
        self.assertEqual([['b'], ['c']], before['data_dep'])
        self.assertEqual(['dummy(b, c)'], before['data_target'])

        # def dummy(x, y)
        p_func_def = get_trace()[5]
        self.assertEqual('p_func_def', p_func_def['type'])
        self.assertEqual("7: p_call_before dummy ['b', 'c']", p_func_def['control_dep'])
        self.assertEqual([], p_func_def['data_dep'])
        self.assertEqual(['x', 'y'], p_func_def['data_target'])

        # return dummy(y, z)
        p_return = get_trace()[6]
        self.assertEqual('p_return', p_return['type'])
        self.assertEqual("7: p_call_before dummy ['b', 'c']", p_return['control_dep'])
        self.assertEqual(['x', 'y'], p_return['data_dep'])
        self.assertEqual([], p_return['data_target'])

        # after dummy(y, z)
        after = get_trace()[7]
        self.assertEqual('p_call_after', after['type'])
        self.assertEqual("7: p_call_before dummy ['b', 'c']", after['control_dep'])
        self.assertEqual([['b'], ['c']], after['data_dep'])
        self.assertEqual(['dummy(b, c)'], after['data_target'])

        # def dummy(x, y)
        p_func_def = get_trace()[8]
        self.assertEqual('p_func_def', p_func_def['type'])
        self.assertEqual("7: p_call_before dummy ['a', 'dummy(b, c)']", p_func_def['control_dep'])
        self.assertEqual([], p_func_def['data_dep'])
        self.assertEqual(['x', 'y'], p_func_def['data_target'])

        # return dummy(x, dummy(y, z))
        p_return = get_trace()[9]
        self.assertEqual('p_return', p_return['type'])
        self.assertEqual("7: p_call_before dummy ['a', 'dummy(b, c)']", p_return['control_dep'])
        self.assertEqual(['x', 'y'], p_return['data_dep'])
        self.assertEqual([], p_return['data_target'])

        # after dummy(x, dummy(y, z))
        after = get_trace()[10]
        self.assertEqual('p_call_after', after['type'])
        self.assertEqual("7: p_call_before dummy ['a', 'dummy(b, c)']", p_return['control_dep'])
        self.assertEqual([['a'], ['dummy(b, c)']], after['data_dep'])
        self.assertEqual(['dummy(a, dummy(b, c))'], after['data_target'])

        # x = dummy(x, dummy(y, z))
        assign = get_trace()[11]
        self.assertEqual('p_assignment', assign['type'])
        self.assertEqual('module', assign['control_dep'])
        self.assertEqual(['dummy(a, dummy(b, c))'], assign['data_dep'])
        self.assertEqual(['x'], assign['data_target'])

        # c = 1
        assign = get_trace()[12]
        self.assertEqual('p_assignment', assign['type'])
        self.assertEqual('module', assign['control_dep'])
        self.assertEqual([], assign['data_dep'])
        self.assertEqual(['c'], assign['data_target'])


    def test_inline_boolop_call(self):
        code_block = """
a = True
b = True
print(a and b)
        """
        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # before
        before = get_trace()[2]
        self.assertEqual('p_call_before', before['type'])
        self.assertEqual('module', before['control_dep'])
        self.assertEqual([['a and b']], before['data_dep'])
        self.assertEqual(["print(a and b)"], before['data_target'])

        # after
        after = get_trace()[5]
        self.assertEqual('p_call_after', after['type'])
        self.assertEqual("4: p_call_before print ['a and b']", after['control_dep'])
        self.assertEqual([['a and b']], after['data_dep'])
        self.assertEqual(["print(a and b)"], after['data_target'])


    def test_inline_operation_call(self):
        code_block = """
a = 5
b = 6
c = 10
print(a + b > c)
"""
        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # before
        before = get_trace()[3]
        self.assertEqual('p_call_before', before['type'])
        self.assertEqual('module', before['control_dep'])
        self.assertEqual([['a', 'b', 'c']], before['data_dep'])
        self.assertEqual(['print(a + b > c)'], before['data_target'])

        # after
        after = get_trace()[4]
        self.assertEqual('p_call_after', after['type'])
        self.assertEqual("5: p_call_before print ['a + b > c']", after['control_dep'])
        self.assertEqual([['a', 'b', 'c']], after['data_dep'])
        self.assertEqual(['print(a + b > c)'], after['data_target'])


    def test_parameter_association(self):
        code_block = """
def dummy(x, y, z):
    return x + y + z
a = 1
b = 2
dummy(a, 23, b)
z = 1
        """
        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # before
        before = get_trace()[2]
        self.assertEqual('p_call_before', before['type'])
        self.assertEqual('module', before['control_dep'])
        self.assertEqual([['a'], [], ['b']], before['data_dep'])
        self.assertEqual(['dummy(a, 23, b)'], before['data_target'])

        # def dummy(x, y):
        p_func_def = get_trace()[3]
        self.assertEqual('p_func_def', p_func_def['type'])
        self.assertEqual("6: p_call_before dummy ['a', '23', 'b']", p_func_def['control_dep'])
        self.assertEqual([], p_func_def['data_dep'])
        self.assertEqual(['x', 'y', 'z'], p_func_def['data_target'])


    def test_multi_method(self):
        code_block = """
def foo(a, b):
    return a + b
    
def bar(c, d):
    return foo(c,d)

print(dir())

x = 1
y = 2
q = bar(x, y)
"""
        trace.trace_python(code_block)
        log.print_trace(get_trace())

        # before bar
        p_call_before_bar = get_trace()[6]
        self.assertEqual('p_call_before', p_call_before_bar['type'])
        self.assertEqual('module', p_call_before_bar['control_dep'])
        self.assertEqual([['x'], ['y']], p_call_before_bar['data_dep'])
        self.assertEqual(['bar(x, y)'], p_call_before_bar['data_target'])

        # before foo
        p_call_before_foo = get_trace()[8]
        self.assertEqual('p_call_before', p_call_before_foo['type'])
        self.assertEqual("12: p_call_before bar ['x', 'y']", p_call_before_foo['control_dep'])
        self.assertEqual([['c'], ['d']], p_call_before_foo['data_dep'])
        self.assertEqual(['foo(c, d)'], p_call_before_foo['data_target'])