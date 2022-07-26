from ast_tree_tracer import control_dependency
from ast_tree_tracer import trace_container


def p_and(lineno, data_dep_static, unparsed_node, nodes, dlocals, dglobals):
    trace_container.trace(lineno, 'p_and_stat', unparsed_node, data_target=unparsed_node, data_dep=data_dep_static)

    evaled = []
    data_dyn = []
    result = True
    executed_nodes = []
    for pos, node in enumerate(nodes):
        resulting_value = eval(node['tb_evaluated'], dlocals, dglobals)
        evaled.append(str(node['data_dep_dyn']) + '=' + str(resulting_value))
        data_dyn.extend(node['data_dep_dyn'])
        executed_nodes.append({'unparsed': node['unparsed'], 'position': pos,  'data_dyn': node['data_dep_dyn'], 'result': resulting_value})
        result = result and resulting_value
        if not result:
            break
    operation = {'lineno': lineno, 'op': 'and', 'result': result, 'target': unparsed_node, 'executed_nodes': executed_nodes, 'num_nodes': len(nodes)}
    trace_container.trace(lineno, 'p_and_dyn', ' and '.join(evaled) + ' => ' + str(result), data_target=unparsed_node, data_dep=data_dyn, bool_op=operation)
    return result


def p_or(lineno, data_dep_static, unparsed_node, nodes, dlocals, dglobals):
    trace_container.trace(lineno, 'p_or_stat', unparsed_node, data_target=unparsed_node, data_dep=data_dep_static)

    evaled = []
    data_dyn = []
    result = False
    executed_nodes = []
    for pos, node in enumerate(nodes):
        resulting_value = eval(node['tb_evaluated'], dlocals, dglobals)
        evaled.append(str(node['data_dep_dyn']) + '=' + str(resulting_value))
        data_dyn.extend(node['data_dep_dyn'])
        executed_nodes.append({'unparsed': node['unparsed'], 'position': pos, 'data_dyn': node['data_dep_dyn'], 'result': resulting_value})
        result = result or resulting_value
        if result:
            break
    operation = {'lineno': lineno, 'op': 'or', 'result': result, 'target': unparsed_node, 'executed_nodes': executed_nodes, 'num_nodes': len(nodes)}
    trace_container.trace(lineno, 'p_or_dyn', ' or '.join(evaled) + ' => ' + str(result), data_target=unparsed_node, data_dep=data_dyn, bool_op=operation)
    return result


def p_assign(lineno, target, value, data_dep, data_target):
    tag = str(lineno) + ': ' + 'p_assignment ' + target + ' = ' + str(value)
    trace_container.trace(lineno, 'p_assignment', target + ' = ' + str(value), data_target=data_target, data_dep=data_dep)
    control_dependency.ctrl_add_expression(tag)
    return value


def p_aug_assign(lineno, target, op, value, data_dep, data_target):
    tag = str(lineno) + ': ' + 'p_aug_assignment ' + target + ' ' + op + ' = ' + str(value)
    trace_container.trace(lineno, 'p_aug_assignment', target + ' ' + op + ' = ' + str(value), data_target=data_target, data_dep=data_dep)
    control_dependency.ctrl_add_expression(tag)
    return value


def p_if_label(lineno, test, data_dep, label):
    tag = str(lineno) + ': ' + label + ' ' + test
    trace_container.trace(lineno, label, label + ' ' + test, data_dep=data_dep)
    control_dependency.ctrl_add_flow_control(tag)


def p_call_before(lineno, func_name, func_args, data_target, data_dep):
    tag = str(lineno) + ': ' + 'p_call_before ' + func_name + ' ' + str(func_args)
    trace_container.trace(lineno, 'p_call_before', func_name, data_target=data_target, data_dep=data_dep)
    control_dependency.ctrl_add_function_start(tag)


def p_call_after(lineno, func_name, func_args, data_target, data_dep, before_func, call_return):
    trace_container.trace(lineno, 'p_call_after', func_name + ' returns ' + str(call_return), data_target=data_target, data_dep=data_dep)
    control_dependency.ctrl_add_function_end()
    return call_return


def p_func_def(lineno, name, arguments):
    tag = str(lineno) + ': ' + 'p_func_def ' + name + str(arguments)
    trace_container.trace(lineno, 'p_func_def', name, data_target=arguments, func_name=name)
    control_dependency.ctrl_add_expression(tag)


def p_return(lineno, value, data_dep):
    tag = str(lineno) + ': ' + 'p_return ' + str(value)
    trace_container.trace(lineno, 'p_return', 'return ' + str(value), data_target=[], data_dep=data_dep)
    control_dependency.ctrl_add_return(tag)
    return value


def p_condition(lineno, test, data_dep, value):
    tag = str(lineno) + ': ' + 'p_condition ' + str(value)
    trace_container.trace(lineno, 'p_condition', test + ' => ' + str(value), data_target=[], data_dep=data_dep)
    control_dependency.ctrl_add_expression(tag)
    return value


def p_pass(lineno):
    tag = str(lineno) + ': ' + 'p_pass'
    trace_container.trace(lineno, 'p_pass', '')
    control_dependency.ctrl_add_expression(tag)


def p_break(lineno):
    tag = str(lineno) + ': ' + 'p_break'
    trace_container.trace(lineno, 'p_break', '')
    control_dependency.ctrl_add_break_or_continue(tag)


def p_continue(lineno):
    tag = str(lineno) + ': ' + 'p_continue'
    trace_container.trace(lineno, 'p_continue', '')
    control_dependency.ctrl_add_break_or_continue(tag)


def p_for_label(lineno, target, iter, data_dep, data_target, label):
    tag = str(lineno) + ': ' + label + ' target: ' + target + ' iter:' + iter
    trace_container.trace(lineno, label, label + ' target: ' + target + ' iter:' + iter, data_dep=data_dep, data_target=data_target)
    control_dependency.ctrl_add_flow_control(tag)


def p_while_label(lineno, test, data_dep, label):
    tag = str(lineno) + ': ' + label + ' test: ' + test
    trace_container.trace(lineno, label, label + ' test: ' + test, data_dep=data_dep)
    control_dependency.ctrl_add_flow_control(tag)


def p_class_def(lineno, name, lineno_range):
    tag = str(lineno) + ': p_class_def ' + name
    trace_container.trace(lineno, 'p_class_def', 'p_class_def ' + name, class_range=lineno_range)
    control_dependency.ctrl_add_expression(tag)

def p_yield(lineno, value, data_dep):
    tag = str(lineno) + ': ' + 'p_yield ' + str(value)
    trace_container.trace(lineno, 'p_yield', 'yield ' + str(value), data_target=[], data_dep=data_dep)
    control_dependency.ctrl_add_yield(tag)
    return value