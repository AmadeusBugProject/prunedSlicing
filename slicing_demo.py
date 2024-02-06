from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from helpers.Logger import Logger
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import get_pruned_slice, get_pruned_relevant_slice, get_relevant_slice, get_dynamic_slice

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

    # Dynamic slice:
    slice, rel_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, variable, line)
    sliced_code = code_from_slice_ast(python_code, slice, rel_bool_ops, exec_trace, func_param_removal)
    log.pretty_print_code(sliced_code)

    # Pruned dynamic slice:
    slice, rel_bool_ops, func_param_removal = get_pruned_slice(exec_trace, variable, line)
    sliced_code = code_from_slice_ast(python_code, slice, rel_bool_ops, exec_trace, func_param_removal)
    log.pretty_print_code(sliced_code)

    # Relevant slice:
    slice, rel_bool_ops, func_param_removal = get_relevant_slice(exec_trace, variable, line)
    sliced_code = code_from_slice_ast(python_code, slice, rel_bool_ops, exec_trace, func_param_removal)
    log.pretty_print_code(sliced_code)

    # Pruned relevant slice:
    slice, rel_bool_ops, func_param_removal = get_pruned_relevant_slice(exec_trace, variable, line)
    sliced_code = code_from_slice_ast(python_code, slice, rel_bool_ops, exec_trace, func_param_removal)
    log.pretty_print_code(sliced_code)


if __name__ == '__main__':
    main()
