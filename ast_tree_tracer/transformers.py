import ast

from ast_tree_tracer.transformer_utils import get_name, get_names_for_data_dep, create_call, \
    recurse_visit, get_name_from_list_of_trees, unparse_for_arg, create_code_block, get_lineno_range, \
    get_names_for_boolop_dyn_slice, unparser_removing_additional_call_wrappers, get_sub_scripted_names, \
    check_for_unsupported_constructs, get_assignmnet_targets_from_list_of_trees, \
    get_name_excluding_sub_scripted_for_assignment_target, get_names_for_potential_dep, remove_duplicates


def transform_tree(syntax_tree):
    check_for_unsupported_constructs(syntax_tree)
    syntax_tree = overload_calls(syntax_tree) # adds calls around calls, has to be called first to not wrap our own calls
    syntax_tree = overload_create_orelse_branches_in_for_and_while(syntax_tree) # adds orelse branches to all fors and whiles
    syntax_tree = overload_flow_control_and_assigns_and_operators(syntax_tree) # adds calls
    syntax_tree = overload_pass_continue_break(syntax_tree) # adds if statements, has to be called after overload_if
    return syntax_tree


# https://stackoverflow.com/questions/51917400/python-how-to-overload-operator-with-ast
def overload_flow_control_and_assigns_and_operators(syntax_tree):
    class Transformer(ast.NodeTransformer):
        def visit_BoolOp(self, node):
            data_dep_static = ast.List(elts=(get_name(node.values)), ctx=ast.Load())
            # node.values = recurse_visit(node.values, self.visit)
            if isinstance(node.op, ast.And) or isinstance(node.op, ast.Or):
                args = [ast.Num(node.lineno), data_dep_static, get_names_for_data_dep(node)]
                arg_nodes = []
                for value in node.values:
                    keys = [ast.Str('data_dep_dyn'), ast.Str('tb_evaluated'), ast.Str('data_dep_stat'), ast.Str('unparsed')]
                    values = [get_names_for_data_dep(value), ast.Str(ast.unparse(self.visit(value))), ast.List(elts=get_name(value), ctx=ast.Load()), ast.Str(unparser_removing_additional_call_wrappers(value))]
                    values_dict = ast.Dict(keys=keys, values=values)
                    arg_nodes.append(values_dict)
                args.append(ast.List(elts=arg_nodes, ctx=ast.Load()))
                args.append(ast.Call(ast.Name('locals', ast.Load()), [], []))
                args.append(ast.Call(ast.Name('globals', ast.Load()), [], []))
                op = 'p_' + type(node.op).__name__.lower() # and, or
                return create_call(op, args)
            node.values = recurse_visit(node.values, self.visit)
            return node

        def visit_Assign(self, node):
            data_dep = get_names_for_data_dep(node.value)
            subscripted_target = get_sub_scripted_names(node.targets)
            data_dep.elts.extend(subscripted_target)
            data_target = ast.List(elts=get_assignmnet_targets_from_list_of_trees(node.targets)[0].elts, ctx=ast.Load())
            args = [ast.Num(node.lineno), unparse_for_arg(node.targets), self.visit(node.value), data_dep, data_target]
            node.value = create_call('p_assign', args)
            return node

        def visit_AugAssign(self, node):
            op = ast.Str(type(node.op).__name__)
            data_dep = ast.List(elts=(get_name(node.value) + get_name(node.target)), ctx=ast.Load())
            data_target = ast.List(elts=get_name_excluding_sub_scripted_for_assignment_target(node.target), ctx=ast.Load())
            args = [ast.Num(node.lineno), unparse_for_arg(node.target), op, self.visit(node.value), data_dep, data_target]
            node.value = create_call('p_aug_assign', args)
            return node

        def visit_If(self, node):
            data_dep = get_names_for_data_dep(node.test)
            pot_dep_if = get_names_for_potential_dep(node.body)
            pot_dep_orelse = get_names_for_potential_dep(node.orelse)

            pot_dep = ast.List(elts=pot_dep_if.elts + pot_dep_orelse.elts, ctx=ast.Load())
            pot_dep = remove_duplicates(pot_dep)

            target_args = [ast.Num(node.lineno), unparse_for_arg(node.test), data_dep, self.visit(node.test)]
            node.test = create_call('p_condition', target_args + [pot_dep])

            args = [ast.Num(node.lineno), unparse_for_arg(node.test), data_dep]
            if_begin = ast.Expr(create_call('p_if_label', args + [pot_dep, ast.Str('p_if_begin')]))
            if_end = ast.Expr(create_call('p_if_label', args + [pot_dep, ast.Str('p_if_end')]))
            else_begin = ast.Expr(create_call('p_if_label', args + [pot_dep, ast.Str('p_else_begin')]))
            else_end = ast.Expr(create_call('p_if_label', args + [pot_dep, ast.Str('p_else_end')]))

            node.body = recurse_visit(node.body, self.visit)
            node.orelse = recurse_visit(node.orelse, self.visit)
            node.body.insert(0, if_begin)
            node.body.append(if_end)
            node.orelse.insert(0, else_begin)
            node.orelse.append(else_end)
            return node

        def visit_Return(self, node):
            if node.value:
                data_dep = get_names_for_data_dep(node.value)
                new_value = self.visit(node.value)
            else:
                data_dep = ast.List(elts=[], ctx=ast.Load())
                new_value = ast.Constant(value=None)
            args = [ast.Num(node.lineno), new_value, data_dep]
            node.value = create_call('p_return', args)
            return node

        def visit_Yield(self, node):
            if node.value:
                data_dep = get_names_for_data_dep(node.value)
                new_value = self.visit(node.value)
            else:
                data_dep = ast.List(elts=[], ctx=ast.Load())
                new_value = ast.Constant(value=None)
            args = [ast.Num(node.lineno), new_value, data_dep]
            node.value = create_call('p_yield', args)
            return node

        def visit_For(self, node):
            data_dep = ast.List(elts=get_name(node.iter), ctx=ast.Load())

            pot_dep_for = get_names_for_potential_dep(node.body)
            pot_dep = pot_dep_for
            if node.orelse:
                pot_dep_else = get_names_for_potential_dep(node.orelse)
                pot_dep = ast.List(elts=pot_dep_for.elts + pot_dep_else.elts, ctx=ast.Load())
            pot_dep = remove_duplicates(pot_dep)

            data_target = ast.List(elts=get_name(node.target), ctx=ast.Load())
            args = [ast.Num(node.lineno), unparse_for_arg(node.target), unparse_for_arg(node.iter), data_dep, data_target]
            for_begin = ast.Expr(create_call('p_for_label', args + [pot_dep] + [ast.Str('p_for_begin')]))
            for_end = ast.Expr(create_call('p_for_label', args + [pot_dep] + [ast.Str('p_for_end')]))

            if node.orelse:
                else_begin = ast.Expr(create_call('p_for_label', args + [pot_dep] + [ast.Str('p_for_else_begin')]))
                else_end = ast.Expr(create_call('p_for_label', args + [pot_dep] + [ast.Str('p_for_else_end')]))
                node.orelse = recurse_visit(node.orelse, self.visit)
                node.orelse.insert(0, else_begin)
                node.orelse.append(else_end)

            node.body = recurse_visit(node.body, self.visit)
            node.iter = self.visit(node.iter)
            node.target = self.visit(node.target)
            node.body.insert(0, for_begin)
            node.body.append(for_end)

            target_args = [ast.Num(node.lineno), ast.Str('ForIter'), data_dep, ast.Str('ForIter')]
            return create_code_block(ast.Expr(create_call('p_condition', target_args + [pot_dep])), node)

        def visit_While(self, node):
            data_dep = get_names_for_data_dep(node.test)

            pot_dep_for = get_names_for_potential_dep(node.body)
            pot_dep = pot_dep_for
            if node.orelse:
                pot_dep_else = get_names_for_potential_dep(node.orelse)
                pot_dep = ast.List(elts=pot_dep_for.elts + pot_dep_else.elts, ctx=ast.Load())
            pot_dep = remove_duplicates(pot_dep)

            target_args = [ast.Num(node.lineno), unparse_for_arg(node.test), data_dep, self.visit(node.test)]
            node.test = create_call('p_condition', target_args + [pot_dep])
            args = [ast.Num(node.lineno), unparse_for_arg(node.test), data_dep, pot_dep]
            while_begin = ast.Expr(create_call('p_while_label', args + [ast.Str('p_while_begin')]))
            while_end = ast.Expr(create_call('p_while_label', args + [ast.Str('p_while_end')]))

            if node.orelse:
                else_begin = ast.Expr(create_call('p_while_label', args + [ast.Str('p_while_else_begin')]))
                else_end = ast.Expr(create_call('p_while_label', args + [ast.Str('p_while_else_end')]))
                node.orelse = recurse_visit(node.orelse, self.visit)
                node.orelse.insert(0, else_begin)
                node.orelse.append(else_end)

            node.body = recurse_visit(node.body, self.visit)
            node.body.insert(0, while_begin)
            node.body.append(while_end)
            return node

        def visit_FunctionDef(self, node):
            func_args_arr = [ast.Str(ast.unparse(x).rstrip()) for x in node.args.args]
            arguments = ast.List(elts=func_args_arr, ctx=ast.Load())
            args = [ast.Num(node.lineno), ast.Str(node.name), arguments]
            func_def = ast.Expr(create_call('p_func_def', args))
            node.body = recurse_visit(node.body, self.visit)
            node.body.insert(0, func_def)
            return node

        def visit_ClassDef(self, node):
            args = [ast.Num(node.lineno), ast.Str(node.name), get_lineno_range(node)]
            class_def = ast.Expr(create_call('p_class_def', args))
            node.body = recurse_visit(node.body, self.visit)
            node.body.insert(0, class_def)
            return node

    syntax_tree = Transformer().visit(syntax_tree)
    syntax_tree = ast.fix_missing_locations(syntax_tree)

    return syntax_tree


def overload_calls(syntax_tree):
    class Transformer(ast.NodeTransformer):
        def visit_Call(self, node):
            lineno = ast.Num(node.lineno)
            func_name = unparse_for_arg(node.func)
            data_target = ast.List(elts=[unparse_for_arg(node)], ctx=ast.Load())

            func_args_arr = [unparse_for_arg(x) for x in node.args]
            func_args = ast.List(elts=func_args_arr, ctx=ast.Load())

            # for method calls, eg. asdf.get(x) this adds 'asdf' to the data dependecies below
            attr_dep = []
            if isinstance(node.func, ast.Attribute):
                attr_dep = [ast.List(elts=get_name(node.func.value), ctx=ast.Load())]

            data_dep = ast.List(elts=attr_dep + get_name_from_list_of_trees(node.args), ctx=ast.Load())
            node.args = recurse_visit(node.args, self.visit)

            args_before = [lineno, func_name, func_args, data_target, data_dep]
            call_before = create_call('p_call_before', args_before)
            args_after = [lineno, func_name, func_args, data_target, data_dep, call_before, node]
            call_after = create_call('p_call_after', args_after)
            return call_after # after(info, before(info), call(func_args))

    syntax_tree = Transformer().visit(syntax_tree)
    syntax_tree = ast.fix_missing_locations(syntax_tree)

    return syntax_tree


def overload_pass_continue_break(syntax_tree):
    class Transformer(ast.NodeTransformer):
        def visit_Pass(self, node):
            lineno = ast.Num(node.lineno)
            return create_code_block(ast.Expr(create_call('p_pass', [lineno])), node)

        def visit_Continue(self, node):
            lineno = ast.Num(node.lineno)
            return create_code_block(ast.Expr(create_call('p_continue', [lineno])), node)

        def visit_Break(self, node):
            lineno = ast.Num(node.lineno)
            return create_code_block(ast.Expr(create_call('p_break', [lineno])), node)

    syntax_tree = Transformer().visit(syntax_tree)
    syntax_tree = ast.fix_missing_locations(syntax_tree)

    return syntax_tree


def overload_create_orelse_branches_in_for_and_while(syntax_tree):
    class Transformer(ast.NodeTransformer):
        def visit_While(self, node):
            if not node.orelse:
                node.orelse = [ast.Pass()]
            return node

        def visit_For(self, node):
            if not node.orelse:
                node.orelse = [ast.Pass()]
            return node

    syntax_tree = Transformer().visit(syntax_tree)
    syntax_tree = ast.fix_missing_locations(syntax_tree)

    return syntax_tree
