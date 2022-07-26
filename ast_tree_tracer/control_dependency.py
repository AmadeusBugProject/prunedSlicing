control_stack = ['module']
dependency_graph = {}


def clear_control_dependencies():
    dependency_graph.clear()
    control_stack.clear()
    control_stack.append('module')


def tag_type(tag):
    return tag.split(' ')[1]


def current_scope():
    return control_stack[-1]


def pop_till_loop():
    while not(tag_type(current_scope()) in ['p_while_begin', 'p_for_begin']):
        control_stack.pop()


def pop_till_method():
    while not tag_type(current_scope()) == 'p_call_before':
        control_stack.pop()


def ctrl_add_expression(tag):
    dependency_graph.update({tag: current_scope()})


def ctrl_add_flow_control(tag):
    if tag_type(tag) in ['p_if_begin', 'p_for_begin', 'p_for_else_begin', 'p_while_begin', 'p_while_else_begin', 'p_else_begin']:
        ctrl_add_expression(tag)
        control_stack.append(tag)
    else:
        control_stack.pop()


def ctrl_add_break_or_continue(tag):
    ctrl_add_expression(tag)
    pop_till_loop()
    control_stack.pop()


def ctrl_add_function_start(tag):
    control_stack.append(tag)


def ctrl_add_return(tag):
    ctrl_add_expression(tag)
    pop_till_method()


def ctrl_add_function_end():
    control_stack.pop()


def ctrl_add_yield(tag):
    ctrl_add_expression(tag)
    pop_till_method()