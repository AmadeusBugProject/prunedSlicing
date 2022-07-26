import argparse
import ast
import codecs
import glob
import pandas


def main(path, csv_file):
    boolop_stats = []
    if path[-1] != '/':
        path = path + '/'
    for py_file in glob.glob(path + '**/*.py', recursive=True):
        with codecs.open(py_file, 'r', encoding='utf-8', errors='ignore') as fd:
            py_code = fd.read()
        stats = file_boolops_stats(py_code)
        stats.update({'file': py_file})
        boolop_stats.append(stats)
    pandas.DataFrame(boolop_stats).to_csv(csv_file)


def file_boolops_stats(py_code):
    lines_boolops = {}

    class NameVisitor(ast.NodeVisitor):
        def visit_BoolOp(self, node):
            increment_in_dict(lines_boolops, node.lineno)
            ast.NodeVisitor.generic_visit(self, node)

    try:
        syntax_tree = ast.parse(py_code, mode='exec')
        file_loc = len(ast.unparse(syntax_tree).splitlines())
    except Exception as e:
        return {'file_loc': None, 'num_boolops': None, 'num_lines_with_boolops': None}

    NameVisitor().visit(syntax_tree)
    return {'file_loc': file_loc, 'num_boolops': sum(lines_boolops.values()), 'num_lines_with_boolops': len(lines_boolops)}


def increment_in_dict(dictt, key):
    if key in dictt.keys():
        dictt[key] += 1
    else:
        dictt[key] = 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="directory with python files")
    parser.add_argument("csv", help="csv filename")
    args = parser.parse_args()
    main(args.path, args.csv)
