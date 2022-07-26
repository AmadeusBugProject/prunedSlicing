import pandas


from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace
from benchmark.benchmark_root import benchmark_dir
from evaluation.slice_benchmarks import refactory_compare_slices, quix_compare_slices
from helpers.Logger import Logger
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import dumb_dynamic_slice, get_dynamic_slice, get_pruned_slice
# usage inside refactory tests:
from collections import OrderedDict
import heapq

log = Logger()


def get_py_code(py_file, function_call_list):
    with open(py_file, 'r') as fd:
        py_code = fd.read()
    return py_code + '\n' + '\n'.join(function_call_list)


def param_from_csv(test_name, csv_file):
    py_file = test_name.split('#')[0].replace('benchmark', benchmark_dir())
    test_number = '#' + test_name.split('#')[1]
    test_inputs_df = pandas.read_csv(csv_file)
    return py_file, test_inputs_df[test_inputs_df['Number'] == test_number].to_dict(orient='records')[0]


def get_middle_test(test_name):
    file_name, test_param = param_from_csv(test_name, benchmark_dir() + '/middle/testData.csv')
    function_call = ['test_data = ' + str(test_param),
                     'middle_result = middle(test_data[\'x\'],test_data[\'y\'],test_data[\'z\'])']
    comp_code = get_py_code(file_name, function_call)
    slice_variable = 'middle_result'
    slice_line = len(comp_code.splitlines())
    return comp_code, test_param['Expected_output'], slice_variable, slice_line, {}


def get_triangle_test(test_name):
    file_name, test_param = param_from_csv(test_name, benchmark_dir() + '/triangle/testData.csv')
    function_call = ['test_data = ' + str(test_param),
                     'instance = Triangle(test_data)',
                     'triangle_result = instance.get_triangle_type()']
    comp_code = get_py_code(file_name, function_call)
    slice_variable = 'triangle_result'
    slice_line = len(comp_code.splitlines())
    return comp_code, test_param['Expected_output'], slice_variable, slice_line, {}


def get_tcas_test(test_name):
    file_name, test_param = param_from_csv(test_name, benchmark_dir() + '/tcas/testData.csv')
    function_call = ['test_data = ' + str(test_param),
                     'tcas_instance = Tcas(test_data)',
                     'alt_sep_actual = tcas_instance.alt_sep_test()']
    comp_code = get_py_code(file_name, function_call)
    slice_variable = 'alt_sep_actual'
    slice_line = len(comp_code.splitlines())
    return comp_code, test_param['Expected_output'], slice_variable, slice_line, {}


def get_refactory_test(test_name):
    py_file = test_name.split('#')[0].replace('benchmark', benchmark_dir())
    test_number = '#' + test_name.split('#')[1]
    question_path = py_file.split('/code/')[0] + '/'
    question = list(filter(lambda x: x['question_path'] == question_path, refactory_compare_slices.questions))[0]
    all_test_params = refactory_compare_slices.get_test_parameters_for_question(question['question_path'], question['num_inputs'], question['output_type'], question['slice_variable'], question['input_dummy'], question['add_globals'])
    _, io_py_code, expected, slice_variable, slice_line, add_globals, _ = list(filter(lambda x: x[0].replace(benchmark_dir(), 'benchmark') == test_name, all_test_params))[0]
    return io_py_code, expected, slice_variable, slice_line, add_globals


def get_quix_test(test_name):
    py_file = test_name.split('#')[0]
    py_file = py_file.replace('benchmark', benchmark_dir())
    test_number = '#' + test_name.split('#')[1]
    all_test_params = quix_compare_slices.get_test_parameters(py_file)
    _, io_py_code, expected, slice_variable, slice_line, _ = list(filter(lambda x: x[0].replace(benchmark_dir(), 'benchmark') == test_name, all_test_params))[0]
    return io_py_code, expected, slice_variable, slice_line, {}


def run_slicing_test(py_code, expected, slice_variable, slice_line, add_globals):
    log.pretty_print_code(py_code)
    bare_outcome = run_some_code(py_code, slice_variable, add_globals)
    io_augmented_code = trace.augment_python(py_code)
    trace.run_trace(io_augmented_code, add_globals)
    exec_trace = get_trace()
    dumb_dyn_slice = dumb_dynamic_slice(exec_trace)
    dyn_slice, dyn_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, slice_variable, slice_line)
    pruned_slice, cond_bool_ops, func_param_removal = get_pruned_slice(exec_trace, slice_variable, slice_line)
    log.s(str(pruned_slice))
    sliced_code = code_from_slice_ast(py_code, pruned_slice, cond_bool_ops, exec_trace, func_param_removal)
    log.pretty_print_code(sliced_code)
    sliced_outcome = run_some_code(sliced_code, slice_variable, add_globals)
    log.s('original outcome = ' + str(bare_outcome))
    log.s('sliced outcome = ' + str(sliced_outcome))
    sliced_equal_to_bare = sliced_outcome == bare_outcome
    return sliced_equal_to_bare


def run_some_code(some_code, variable_name, add_globals):
    globals_space = globals().copy()
    globals_space.update(add_globals)
    exec(compile(some_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]


def main():
    # test = 'benchmark/refactory/data/question_5/code/correct/correct_5_266.py#4:'
    test = 'benchmark/tcas/faulty_versions/Tcas_Fault9.py#1562:'
    # test = 'benchmark/quixbugs/correct_python_programs/max_sublist_sum.py#4:'
    # test = 'benchmark/refactory/data/question_2/code/fail/wrong_2_107.py#0:'

    if 'benchmark/triangle/' in test:
        py_code, expected, slice_variable, slice_line, add_globals = get_triangle_test(test)
    elif 'benchmark/middle/' in test:
        py_code, expected, slice_variable, slice_line, add_globals = get_middle_test(test)
    elif 'benchmark/tcas/' in test:
        py_code, expected, slice_variable, slice_line, add_globals = get_tcas_test(test)
    elif 'benchmark/refactory/' in test:
        py_code, expected, slice_variable, slice_line, add_globals = get_refactory_test(test)
    elif 'benchmark/quixbugs/' in test:
        py_code, expected, slice_variable, slice_line, add_globals = get_quix_test(test)
    else:
        print('cant find that test')
        return

    print(run_slicing_test(py_code, expected, slice_variable, slice_line, add_globals))


if __name__ == "__main__":
    main()
