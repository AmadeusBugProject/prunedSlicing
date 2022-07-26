import ast

import astpretty
from timeout_decorator import timeout_decorator

from constants import CODE_GEN_TIMEOUT
from slicing.slicing_exceptions import SlicingException


def get_boolop_usages_from_data_deps(lineno, exec_trace): # finds the outmost boolop used in the line
    top_level_dependencies = []
    for trace in list(filter(lambda x: x['lineno'] == lineno, exec_trace)):
        if trace['type'] not in ['p_and_dyn', 'p_and_stat', 'p_or_dyn', 'p_or_stat']:
            for data_dep in trace['data_dep']:
                if ' or ' in data_dep or ' and ' in data_dep:
                    top_level_dependencies.append(data_dep)
                if isinstance(data_dep, list):
                    for data_item in data_dep:
                        if ' or ' in data_item or ' and ' in data_item:
                            top_level_dependencies.append(data_item)
    return top_level_dependencies


def get_boolop_replacements(lineno, rel_boolop, exec_trace):
    top_level_boolop = set(get_boolop_usages_from_data_deps(lineno, exec_trace))
    boolops_in_line = list(filter(lambda x: x['lineno'] == lineno, rel_boolop))
    if not boolops_in_line:
        return None
    replacement_boolops = []
    for target in top_level_boolop:
        replacement = make_executable_boolop(target, boolops_in_line)
        replacement_boolops.append({'orig': target, 'replacement': replacement})
    return replacement_boolops


def make_executable_boolop(target, boolops):
    top_level_boolop = list(filter(lambda x: x['target'][0] == target, boolops))
    executed_nodes = {}
    for boolop in top_level_boolop:
        for node in boolop['executed_nodes']:
            executed_nodes.update({node['position']: node['unparsed']})

    all_unparsed_nodes = []
    for node_pos in range(top_level_boolop[0]['num_nodes']):
        if node_pos in executed_nodes.keys():
            if ' or ' in executed_nodes[node_pos] or ' and ' in executed_nodes[node_pos]:
                all_unparsed_nodes.append('(' + make_executable_boolop(executed_nodes[node_pos], boolops) + ')')
            else:
                all_unparsed_nodes.append(executed_nodes[node_pos])
    return (' ' + top_level_boolop[0]['op'] + ' ').join(all_unparsed_nodes)

    #
    # for node in executed_nodes:
    #     if ' or ' in node or ' and ' in node:
    #         # all_unparsed_nodes.append('(' + make_executable_boolop(node, boolops) + ')')
    #         target.replace(node, make_executable_boolop(node, boolops))
    #     # else:
    #     #     all_unparsed_nodes.append(node)
    #
    # # return (' ' + top_level_boolop[0]['op'] + ' ').join(all_unparsed_nodes)
    # return target


def get_func_param_removal_set(func_param_removal, slice):
    # remove all candidate function calls that arent in the slice in the first place
    remove_params = list(filter(lambda x: x['lineno'] in slice, func_param_removal))

    # intersect all removal sets of the same functions and keep the parameter indices that are to be removed in every usage
    parameters_tb_removed = {}
    for parameter_item in remove_params:
        func_name = parameter_item['func_name']
        remove_param_idx = set(parameter_item['remove_param_idx'])
        if func_name in parameters_tb_removed.keys():
            parameters_tb_removed[func_name] = parameters_tb_removed[func_name].intersection(remove_param_idx)
        else:
            parameters_tb_removed.update({func_name: remove_param_idx})
    return parameters_tb_removed


@timeout_decorator.timeout(CODE_GEN_TIMEOUT)
def code_from_slice_ast(code, slice, rel_boolop, exec_trace,  func_param_removal):
    # func_param_removal = False
    syntax_tree = ast.parse(code, mode='exec')

    class SliceLinenoTransformer(ast.NodeTransformer):
        def generic_visit(self, node):
            if 'lineno' in dir(node) and node.lineno not in slice:
                if type(node) == ast.Import or type(node) == ast.ImportFrom: # just always take imports, even if not in slice
                    return node
                return ast.Pass()
            else:
                return ast.NodeTransformer.generic_visit(self, node)

    SliceLinenoTransformer().visit(syntax_tree)

    class BoolOpTransformer(ast.NodeTransformer):
        def visit_BoolOp(self, node):
            if 'lineno' in dir(node) and node.lineno in slice:
                replacements = get_boolop_replacements(node.lineno, rel_boolop, exec_trace)
                if not replacements:
                    return ast.Constant(value=False)
                unparsed = ast.unparse(node).strip()
                for replacement in replacements:
                    if replacement['orig'] == unparsed:
                        new_node = ast.parse(replacement['replacement']).body[0].value
                        # new_node.col_offset = node.col_offset
                        # new_node.lineno = node.lineno
                        return new_node
                return ast.Str('NO_REPLACEMENT_SOMETHINGS_WRONG')

    if rel_boolop and exec_trace:
        BoolOpTransformer().visit(syntax_tree)

    class NameVisitor(ast.NodeVisitor):
        def __init__(self):
            self.contains_named_instance = 0

        def generic_visit(self, node):
            if type(node) == ast.Name or type(node) == ast.NameConstant or ast.Name == ast.NamedExpr:
                self.contains_named_instance += 1
            ast.NodeVisitor.generic_visit(self, node)

    #     class GetNamesInNodesVisitor(ast.NodeVisitor):
    #         def __init__(self):
    #             self.names = []
    #
    #         def generic_visit(self, node):
    #             if type(node) == ast.Name or type(node) == ast.NameConstant or type(node) == ast.NamedExpr:
    #                 self.names.append(node.id)
    #             ast.NodeVisitor.generic_visit(self, node)
    #
    #     class CountNameUsages(ast.NodeVisitor):
    #         def __init__(self, name):
    #             self.usages = 0
    #             self.name = name
    #
    #         def generic_visit(self, node):
    #             if type(node) == ast.Name or type(node) == ast.NameConstant or type(node) == ast.NamedExpr:
    #                 if node.id == self.name:
    #                     self.usages += 1
    #             ast.NodeVisitor.generic_visit(self, node)

    class FuncParamRemoval(ast.NodeTransformer):
        def __init__(self, remove_params):
            self.remove_params = remove_params

        def visit_Call(self, node):
            if 'lineno' in dir(node) and node.lineno in slice:
                unparsed = ast.unparse(node).strip()
                func_name = None
                if 'id' in dir(node.func):
                    func_name = node.func.id
                if 'attr' in dir(node.func):
                    func_name = node.func.attr
                if not func_name:
                    raise SlicingException('No func_name, somethings wrong:\n' + str(astpretty.pformat(node)))

                if func_name in self.remove_params:
                    for remove_arg_index in self.remove_params[func_name]:
                        nv = NameVisitor()
                        nv.visit(node.args[remove_arg_index])
                        if nv.contains_named_instance:  # because without this, numeric parameters may be replaced with 'Dummy'
                            node.args[remove_arg_index] = ast.Constant(value=None)
                        #                         nv = GetNamesInNodesVisitor()
                        #                         nv.visit(node.args[remove_arg_index])
                        #                         usage_counter = 0
                        #                         for name in nv.names:
                        #                             count_usages = CountNameUsages(name)
                        #                             count_usages.visit(syntax_tree)
                        #                             usage_counter += count_usages.usages
                        #                         if not usage_counter - len(nv.names) and len(nv.names): # and len(nv.names) because without this, numeric parameters may be replaced with 'Dummy'
            for arg in node.args:
                arg = self.visit(arg)
            return node

    if func_param_removal:
        params_for_removal = get_func_param_removal_set(func_param_removal, slice)
        FuncParamRemoval(params_for_removal).visit(syntax_tree)

    syntax_tree = ast.fix_missing_locations(syntax_tree)
    return ast.unparse(syntax_tree)
