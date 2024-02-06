import unittest

from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from ast_tree_tracer.trace_container import clear_trace
from slicing.code_from_slice import get_boolop_replacements, code_from_slice_ast
from slicing.slice import get_dynamic_slice, get_relevant_slice
from helpers.Logger import Logger

log = Logger()


class TestArray(unittest.TestCase):
    def tearDown(self):
        clear_trace()

    def test_relevant1(self):
        code_block = """
z = 0
x = 1
while x < 2:
    z = 5
    x += 1
z
"""
        variable = 'z'
        line_number = 6
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())
        # trace 3 | lineno: 5	 type: p_assignment	 data_target: ['c', 'b']	 data_dep: ['c', 'a', 'c', 'b']
        # but should be: data_target: ['c']

        # check content of pot_dep sets:
        for item in exec_trace:
            if item['type'] in {'p_condition', 'p_while_begin', 'p_while_end'}:
                assert(set(item['pot_dep']) == {'x', 'z'})
            else:
                assert(len(item['pot_dep']) == 0)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line_number)
        print('\n'.join([str(x) for x in rel_bool_ops]))
        print(computed_slice)
        print(get_boolop_replacements(line_number, rel_bool_ops, exec_trace))

        log.pretty_print_code(code_block)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)

    def test_relevant2(self):
        code_block = """
z = 0
y = 3
x = 2
a = 0
while x < y:
    z = 5
    a += 1
    x = a
z
"""
        variable = 'z'
        line_number = 7
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        # check content of pot_dep sets:
        for item in exec_trace:
            if item['type'] in {'p_condition', 'p_while_begin', 'p_while_end'}:
                assert(set(item['pot_dep']) == {'a', 'x', 'z'})
            else:
                assert(len(item['pot_dep']) == 0)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line_number)
        print('\n'.join([str(x) for x in rel_bool_ops]))
        print(computed_slice)
        print(get_boolop_replacements(line_number, rel_bool_ops, exec_trace))

        log.pretty_print_code(code_block)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)

    def test_relevant3(self):
        code_block = """
z = 0
y = 3
x = 2
a = 0
while x < y:
    z = 5
    if z > 10:
        a += 1
    else:
        a += 2
        b = 5
    x = a
z
"""
        variable = 'z'
        line_number = 7
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        # check content of pot_dep sets:
        for item in exec_trace:
            if item['type'] in {'p_while_begin', 'p_while_end'} \
                    or (item['type'] in {'p_condition'} and item['lineno'] == 6):
                assert(set(item['pot_dep']) == {'a', 'b', 'x', 'z'})
            elif item['type'] in {'p_else_begin', 'p_else_end'} \
                    or (item['type'] in {'p_condition'} and item['lineno'] == 8):
                assert (set(item['pot_dep']) == {'a', 'b'})
            else:
                assert(len(item['pot_dep']) == 0)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line_number)
        print('\n'.join([str(x) for x in rel_bool_ops]))
        print(computed_slice)
        print(get_boolop_replacements(line_number, rel_bool_ops, exec_trace))

        log.pretty_print_code(code_block)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)

    def test_relevant4(self):
        code_block = """
z = 0
y = 3
x = 2
a = 0
while x < y:
    z = 5
    if z < 10:
        a += 1
    else:
        b = 5
    x = a
z
"""
        variable = 'z'
        line_number = 12
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        # check content of pot_dep sets:
        for item in exec_trace:
            if item['type'] in {'p_while_begin', 'p_while_end'} \
                    or (item['type'] in {'p_condition'} and item['lineno'] == 6):
                assert(set(item['pot_dep']) == {'a', 'b', 'x', 'z'})
            elif item['type'] in {'p_if_begin', 'p_if_end'} \
                    or (item['type'] in {'p_condition'} and item['lineno'] == 8):
                assert(set(item['pot_dep']) == {'a', 'b'})
            else:
                assert(len(item['pot_dep']) == 0)

        computed_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line_number)
        print('\n'.join([str(x) for x in rel_bool_ops]))
        print(computed_slice)
        print(get_boolop_replacements(line_number, rel_bool_ops, exec_trace))

        log.pretty_print_code(code_block)

        sliced_code = code_from_slice_ast(code_block, computed_slice, rel_bool_ops, exec_trace, func_param_removal)
        log.pretty_print_code(sliced_code)

    def test_relevant5(self):
        code_block = """
z = 1
y = 2
x = 2
a = 0
while x > y:
    z = 5
    if z < 10:
        a += 1
    else:
        b = 5
    x = a
z = z + 1     
z
"""
        variable = 'z'
        line_number = 13
        trace.trace_python(code_block)
        exec_trace = get_trace()
        log.print_trace(get_trace())

        # check content of pot_dep sets:
        for item in exec_trace:
            if item['type'] in {'p_while_begin', 'p_while_end'} \
                    or (item['type'] in {'p_condition'} and item['lineno'] == 6):
                assert(set(item['pot_dep']) == {'a', 'b', 'x', 'z'})
            else:
                assert(len(item['pot_dep']) == 0)

        computed_relevant_slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line_number)
        print('\n'.join([str(x) for x in rel_bool_ops]))
        print(computed_relevant_slice)
        print(get_boolop_replacements(line_number, rel_bool_ops, exec_trace))

        assert computed_relevant_slice == {2, 3, 4, 6, 13}
        sliced_code = code_from_slice_ast(code_block, computed_relevant_slice, rel_bool_ops, exec_trace,
                                          func_param_removal)
        log.pretty_print_code(sliced_code)


        computed_dynamic_slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable,
                                                                                       line_number)
        assert computed_dynamic_slice == {2, 13}

        log.pretty_print_code(code_block)

