from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from helpers.Logger import Logger
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import get_pruned_slice

log = Logger()


def main():
    python_code = """a = True
b = True
c = 3
d = 2
z = a and b and (c == 3 or d > 5)"""
    log.pretty_print_code(python_code)

    trace.trace_python(python_code)
    exec_trace = get_trace()


    variable = 'z'
    line = 5
    log.pretty_print_slice_criteria(line, variable)

    pruned_slice, pruned_rel_bool_ops, pruned_func_param_removal = get_pruned_slice(exec_trace, variable, line)

    sliced_code = code_from_slice_ast(python_code, pruned_slice, pruned_rel_bool_ops, exec_trace, pruned_func_param_removal)
    log.pretty_print_code(sliced_code)


if __name__ == '__main__':
    main()
