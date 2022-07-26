import os
import pandas

from test.run_in_test import relative_to_project_root
from slicing.dummy import Dummy


def get_directory():
    return relative_to_project_root('benchmark/tcas/')


with open(get_directory() + 'Tcas.py', 'r') as fd:
    tcas_code = fd.read().splitlines()


def add_function_call(test_data):
    lines = tcas_code.copy()
    lines.append('test_data = ' + str(test_data))
    lines.append('tcas_instance = Tcas(test_data)')
    lines.append('alt_sep_actual = tcas_instance.alt_sep_test()')
    return '\n'.join(lines), len(lines), 'alt_sep_actual'


def get_test_parameters():
    test_file = get_directory() + 'testData.csv'
    df = pandas.read_csv(test_file)
    return [[x['Number'], x, x['Expected_output']] for x in df.to_dict(orient='records')]


def run_sliced(sliced_code, variable_name):
    globals_space = globals().copy()
    exec(compile(sliced_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]
