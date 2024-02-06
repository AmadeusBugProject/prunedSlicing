import ast

# import astpretty
from timeout_decorator import timeout_decorator

from ast_tree_tracer.transformers import transform_tree
from ast_tree_tracer.augment import *
from constants import TRACING_TIMEOUT, TRACING_AUGMENTATION_TIMEOUT


def trace_python(code_block, add_globals=None):
    if not add_globals:
        add_globals = {}
    syntax_tree = ast.parse(code_block, mode='exec')
    # astpretty.pprint(syntax_tree)
    syntax_tree = transform_tree(syntax_tree)
    globals_copy = globals().copy()
    globals_copy.update(add_globals)
    exec(compile(syntax_tree, filename="", mode="exec"), globals_copy)


@timeout_decorator.timeout(TRACING_AUGMENTATION_TIMEOUT)
def augment_python(code_block):
    syntax_tree = ast.parse(code_block, mode='exec')
    syntax_tree = transform_tree(syntax_tree)
    return ast.unparse(syntax_tree)


@timeout_decorator.timeout(TRACING_TIMEOUT)
def run_trace(code_block, add_globals=None):
    if not add_globals:
        add_globals = {}
    globals_copy = globals().copy()
    globals_copy.update(add_globals)
    exec(compile(code_block, filename="", mode="exec"), globals_copy)
