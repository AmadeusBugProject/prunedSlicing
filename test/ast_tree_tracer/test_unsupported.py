import unittest

from ast_tree_tracer import trace_container
from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from helpers.Logger import Logger
from slicing.slicing_exceptions import SlicingException

log = Logger()

class TestUnsupported(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_lambda(self):
        code_block = """
f = lambda x: x**2
i = f(5)
        """
        with self.assertRaises(SlicingException) as e:
            trace.trace_python(code_block)
            self.assertEquals('Lambda not supported', str(e.attr))
        # TODO write a slicer test for this

    def test_delete(self):
        code_block = """
i = 5
del i
            """
        with self.assertRaises(SlicingException) as e:
            trace.trace_python(code_block)
            self.assertEquals('Delete not supported', str(e.attr))

    def test_decorated_method(self):
        code_block = """
class Tcas:
    def __init__(self, x):
        self.A = x
        self.B = 0

    @staticmethod
    def get_sum(tcas):
        return tcas.B + tcas.A + x


x = 5
tcas = Tcas(x)
zz = tcas.get_sum(tcas)
    """

        with self.assertRaises(SlicingException) as e:
            trace.trace_python(code_block)
            self.assertEquals('Decorators not supported', str(e.attr))

    def test_annassign(self):
        code_block = """
i : int = 42
        """
        with self.assertRaises(SlicingException) as e:
            trace.trace_python(code_block)
            self.assertEquals('AnnAssign not supported', str(e.attr))

    def test_try(self):
        code_block = """
try:
    i = 42
except:
    pass
        """
        with self.assertRaises(SlicingException) as e:
            trace.trace_python(code_block)
            self.assertEquals('Try not supported', str(e.attr))

    def test_raise(self):
        code_block = """
i = 42
raise Exception("Some Exception") 
"""
        with self.assertRaises(SlicingException) as e:
            trace.trace_python(code_block)
            self.assertEquals('Raise not supported', str(e.attr))

    def test_assert(self):
        code_block = """
i = 42
assert(i)
"""
        with self.assertRaises(SlicingException) as e:
            trace.trace_python(code_block)
            self.assertEquals('Assert not supported', str(e.attr))

    def test_async_for(self):
        code_block = """
async for i in [1,2,3]:
    print(i)
        """
        with self.assertRaises(SlicingException) as e:
            trace.trace_python(code_block)
            self.assertEquals('Async not supported', str(e.attr))

    def test_async_func(self):
        code_block = """
async def foo(i):
    print(i)
i(7)
        """
        with self.assertRaises(SlicingException) as e:
            trace.trace_python(code_block)
            self.assertEquals('Async not supported', str(e.attr))

    def test_async_with(self):
        code_block = """
async with open('testfile', 'r') as fd:
    i = fd.read()
"""
        with self.assertRaises(SlicingException) as e:
            trace.trace_python(code_block)
            self.assertEquals('Async not supported', str(e.attr))

    def test_with(self):
        code_block = """
with open('testfile', 'r') as fd:
    i = fd.read()
"""
        with self.assertRaises(SlicingException) as e:
            trace.trace_python(code_block)
            self.assertEquals('With not supported', str(e.attr))

    def test_await(self):
        code_block = """
i = await foo()
"""
        with self.assertRaises(SlicingException) as e:
            trace.trace_python(code_block)
            self.assertEquals('Await not supported', str(e.attr))

    def test_global(self):
        code_block = """
global i
i = 3
"""
        with self.assertRaises(SlicingException) as e:
            trace.trace_python(code_block)
            self.assertEquals('Global not supported', str(e.attr))

    def test_yield(self):
        code_block = """
def foo(x):
    for i in range(x):
        yield i
a = 5
z = list(foo(5))
"""
        with self.assertRaises(SlicingException) as e:
            trace.trace_python(code_block)
            self.assertEquals('Yield not supported', str(e.attr))
