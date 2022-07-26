import ast

from timeout_decorator import timeout_decorator

from constants import CODE_CLEANUP_TIMEOUT


@timeout_decorator.timeout(CODE_CLEANUP_TIMEOUT)
def remove_comments_and_top_level_const_expression_strings(py_code):
    syntax_tree = ast.parse(py_code)
    new_body = []
    for node in syntax_tree.body:
        if not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)):
            new_body.append(node)
    syntax_tree.body = new_body
    syntax_tree = ast.fix_missing_locations(syntax_tree)

    return ast.unparse(syntax_tree)


