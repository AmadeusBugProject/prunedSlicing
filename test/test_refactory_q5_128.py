import json
import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from constants import root_dir
from helpers.Logger import Logger
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import get_dynamic_slice, get_pruned_slice, get_relevant_slice

log = Logger()

with open('scam_tcas.py', 'r') as fd:
    TCAS = fd.read()


class TestRefacQ5(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_refacq5(self):
        with open(root_dir() + 'benchmark/refactory/data/question_5/code/correct/correct_5_128.py', 'r') as fd:
            code_block = fd.read()

        with open(root_dir() + 'benchmark/refactory/data/question_5/' + 'ans/input_004.txt', 'r') as fd:
            func_call = 'refacq5' + ' = ' + fd.read()
        with open(root_dir() + 'benchmark/refactory/data/question_5/' + 'ans/output_004.txt', 'r') as fd:
            expected = json.load(fd)

        code_block = '\n'.join(code_block.splitlines() + [func_call])

        variable = 'refacq5'

        line_number = len(code_block.splitlines())
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.pretty_print_code(code_block)

        log.print_trace(exec_trace)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line_number)
        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)
        log.s(str(computed_slice))

        with open('refacq5128orig.py', 'w') as fd:
            fd.write(code_block)
        with open('refacq5128relslice.py', 'w') as fd:
            fd.write(sliced_code)


        log.s('original: ' + str(run_sliced(code_block, variable)))
        log.s('sliced: ' + str(run_sliced(sliced_code, variable)))
        log.s('expected: ' + str(expected))


def run_sliced(sliced_code, variable_name):
    globals_space = globals().copy()
    exec(compile(sliced_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]
