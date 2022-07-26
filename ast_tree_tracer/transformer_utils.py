import ast

from slicing.slicing_exceptions import SlicingException


def recurse_visit(node_list, visit):
    values = []
    for value in node_list:
        values.append(visit(value))
    return values


def create_call(name, args):
    ast_name = ast.Name(name, ast.Load())
    kwargs = []
    return ast.Call(ast_name, args, kwargs)


def create_code_block(first_node, second_node):
    return ast.If(test=ast.NameConstant(value=True), body=[first_node, second_node], orelse=[])


def get_names_for_data_dep(node):
    if isinstance(node, ast.BoolOp):
        data_dep = ast.List(elts=[ast.Str(unparse_bool_op(node))], ctx=ast.Load())
    else:
        data_dep = ast.List(elts=get_name(node), ctx=ast.Load())
    return data_dep


def get_names_for_boolop_dyn_slice(node):
    if isinstance(node, ast.BoolOp):
        return ast.Str(unparse_bool_op(node))
    elif isinstance(node, ast.Call):
        return ast.Str(unparse_augmented_func(node).s)
    else:
        return ast.Str(unparse_for_arg(node).s)


def unparse_for_arg(node):
    return ast.Str(ast.unparse(node).rstrip())


def unparse_bool_op(node):
    return unparser_removing_additional_call_wrappers(node).rstrip()
    # op = " " + type(node.op).__name__.lower() + " "
    # unparse = []
    # for value in node.values:
    #     unparse.append(unparser_removing_additional_call_wrappers(value))
    #     # if isinstance(value, ast.Call):
    #     #     unparse.append(unparse_augmented_func(value).s)
    #     # else:
    #     #     unparse.append(unparse_for_arg(value).s)
    # return op.join(unparse)


def unparser_removing_additional_call_wrappers(node):
    new_node = ast.parse(ast.unparse(node)).body[0].value

    class RemoveCallWrappers(ast.NodeTransformer):
        def visit_Call(self, node):
            if node.func.id == 'p_call_after':
                new_node = node.args[6]
                # new_node = self.visit(new_node.args)
                return new_node
            return node

    new_node = RemoveCallWrappers().visit(new_node)
    # new_node = ast.fix_missing_locations(new_node)
    return ast.unparse(new_node).rstrip()


def unparse_augmented_func(node):
    # this is hacky and relies on the unparsed function name staying the 4th parameter of these augmented calls
    func_info = unparse_for_arg(node)
    if 'id' in dir(node.func) and (node.func.id == 'p_call_after' or node.func.id == 'p_call_before'):
        func_info = node.args[3].elts[0]
    return func_info


def get_sub_scripted_names(syntax_trees):
    ids = []
    if isinstance(syntax_trees, list):
        for syntax_tree in syntax_trees:
            ids.extend(get_sub_scripted_name(syntax_tree))
    return ids


def get_sub_scripted_name(syntax_tree):
    ids = []
    class SubscriptVisitor(ast.NodeVisitor):
        def visit_Subscript(self, node):
            ids.extend(get_name(node))
    SubscriptVisitor().visit(syntax_tree)
    return ids


def get_name(syntax_trees):
    ids = []

    class NameVisitor(ast.NodeVisitor):
        def visit_Attribute(self, node):
            ids.append(unparse_for_arg(node))

        def visit_Name(self, node):
            ids.append(ast.Str(node.id))

        def visit_Call(self, node):
            ids.append(unparse_augmented_func(node))

        def visit_BoolOp(self, node):
            ids.append(ast.Str(unparse_bool_op(node)))

    if isinstance(syntax_trees, list):
        for syntax_tree in syntax_trees:
            NameVisitor().visit(syntax_tree)
    else:
        NameVisitor().visit(syntax_trees)
    return ids


def get_name_from_list_of_trees(syntax_trees):
    ids = []
    if isinstance(syntax_trees, list):
        for syntax_tree in syntax_trees:
            ids.append(ast.List(elts=get_name(syntax_tree), ctx=ast.Load()))
    return ids


def get_assignmnet_targets_from_list_of_trees(syntax_trees): # excluding subscripts
    ids = []
    if isinstance(syntax_trees, list):
        for syntax_tree in syntax_trees:
            ids.append(ast.List(elts=get_name_excluding_sub_scripted_for_assignment_target(syntax_tree), ctx=ast.Load()))
    return ids


def get_name_excluding_sub_scripted_for_assignment_target(syntax_trees): # excluding subscripted, used for assignment target
    ids = []

    class NameVisitor(ast.NodeVisitor):
        def visit_Subscript(self, node):
            self.visit(node.value)

        def visit_Attribute(self, node):
            ids.append(unparse_for_arg(node))

        def visit_Name(self, node):
            ids.append(ast.Str(node.id))

    if isinstance(syntax_trees, list):
        for syntax_tree in syntax_trees:
            NameVisitor().visit(syntax_tree)
    else:
        NameVisitor().visit(syntax_trees)
    return ids


def get_lineno_range(syntax_tree):
    class LinenoVisitor(ast.NodeVisitor):
        def __init__(self):
            self.begin = syntax_tree.lineno
            self.end = self.begin

        def generic_visit(self, node):
            if 'lineno' in dir(node) and node.lineno > self.end:
                self.end = node.lineno
            ast.NodeVisitor.generic_visit(self, node)

    visitor = LinenoVisitor()
    visitor.visit(syntax_tree)
    return ast.List(elts=[ast.Num(visitor.begin), ast.Num(visitor.end)], ctx=ast.Load())


def check_for_unsupported_constructs(syntax_tree):
    class UnsupVisitor(ast.NodeVisitor):
        def generic_visit(self, node):
            if isinstance(node, ast.Lambda):
                raise (SlicingException("Lambda not supported"))
            if isinstance(node, ast.FunctionDef) and len(node.decorator_list):
                raise (SlicingException("Decorators not supported"))
            if isinstance(node, ast.Delete):
                raise (SlicingException("Delete not supported"))
            if isinstance(node, ast.AnnAssign):
                raise (SlicingException("AnnAssign not supported"))
            if isinstance(node, ast.Try):
                raise (SlicingException("Try not supported"))
            if isinstance(node, ast.AsyncFor) or isinstance(node, ast.AsyncWith) or isinstance(node, ast.AsyncFunctionDef):
                raise (SlicingException("Async not supported"))
            if isinstance(node, ast.Await):
                raise (SlicingException("Await not supported"))
            if isinstance(node, ast.Assert):
                raise (SlicingException("Assert not supported"))
            if isinstance(node, ast.Global):
                raise (SlicingException("Global not supported"))
            if isinstance(node, ast.Raise):
                raise (SlicingException("Raise not supported"))
            if isinstance(node, ast.With):
                raise (SlicingException("With not supported"))
            if isinstance(node, ast.Yield):
                raise (SlicingException("Yield not supported"))
            if isinstance(node, ast.Call) and not 'id' in dir(node.func) and not 'attr' in dir(node.func):
                raise (SlicingException("Call construct not having any id or attr not supported"))
            ast.NodeVisitor.generic_visit(self, node)
    visitor = UnsupVisitor()
    visitor.visit(syntax_tree)
