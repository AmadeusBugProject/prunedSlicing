from ast_tree_tracer import control_dependency
from constants import MAX_TRACE_LENGTH
from slicing.slicing_exceptions import SlicingException

execution_trace = []


def trace(lineno, type, info, data_target=None, data_dep=None, pot_dep=None, control_dep='', class_range=None, func_name='', bool_op=None):
    if not data_target:
        data_target = []
    if not data_dep:
        data_dep = []
    if not pot_dep:
        pot_dep = []
    if not class_range:
        class_range = []
    if not bool_op:
        bool_op = {}
    if not control_dep:
        control_dep = control_dependency.current_scope()
    execution_trace.append({'lineno': lineno,
                            'type': type,
                            'info': info,
                            'control_dep': control_dep,
                            'data_target': data_target,
                            'data_dep': data_dep,
                            'class_range': class_range,
                            'func_name': func_name,
                            'bool_op': bool_op,
                            'pot_dep': pot_dep})
    if len(execution_trace) > MAX_TRACE_LENGTH:
        raise SlicingException('Trace length too big, quitting')


def get_trace():
    return execution_trace


def clear_trace():
    execution_trace.clear()
    control_dependency.clear_control_dependencies()
