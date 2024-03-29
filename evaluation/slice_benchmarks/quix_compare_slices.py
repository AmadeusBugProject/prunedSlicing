import glob
import json
import pathlib
import time
import types

import pandas
import timeit
import timeout_decorator
import distutils.util
from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace, clear_trace
from benchmark.benchmark_root import benchmark_dir
from constants import NUM_RUNS_TIMEIT, QUIX_TIMEOUT
from evaluation.boolop_counter.count_boolops import file_boolops_stats
from evaluation.slice_benchmarks.utils import remove_comments_and_top_level_const_expression_strings
from helpers.Logger import Logger
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import get_dynamic_slice, get_pruned_slice, dumb_dynamic_slice, get_relevant_slice, \
    get_pruned_relevant_slice
from slicing.dummy import Dummy

# usage inside tests
from collections import OrderedDict
import heapq

from test.run_in_test import relative_to_project_root

log = Logger()

quix_path = benchmark_dir() + '/quixbugs/'
program_paths = [quix_path + 'correct_python_programs/',
                 quix_path + 'python_programs/']
test_input_path = quix_path + 'json_testcases/'


def get_test_parameters(program_file):
    test_params = []

    program_name = program_file.split('/')[-1].split('.')[0]
    test_input_file = test_input_path + program_name + '.json'

    if pathlib.Path(test_input_file).exists():
        with open(test_input_file, 'r') as fd:
            test_cases = fd.read().splitlines()
            test_cases = list(filter(lambda x: x.strip(), test_cases)) # remove empty lines
            test_cases = [json.loads(x) for x in test_cases]

        with open(program_file, 'r') as fd:
            py_code = fd.read()
        py_code = remove_comments_and_top_level_const_expression_strings(py_code)
        boolops_stats = file_boolops_stats(py_code)

        for i, test_case in enumerate(test_cases):
            test_name = program_file + '#' + str(i) + ':'

            if type(test_case[0]) is list:
                func_params = str(test_case[0])[1:len(str(test_case[0]))-1]
            else:
                func_params = str(test_case[0])

            function_call = program_name + '(' + func_params + ')'
            if 'yield ' in py_code:
                function_call = 'list(' + function_call + ')'

            slice_variable = 'quix_result'

            test_py_code = '\n'.join(py_code.splitlines() + [slice_variable + ' = ' + function_call])
            expected = test_case[1]
            slice_line = len(test_py_code.splitlines())
            test_params.append([test_name, test_py_code, expected, slice_variable, slice_line, boolops_stats])
    return test_params


def main():
    log.s('Starting')
    comp_df = pandas.DataFrame()
    program_files = []
    for ppath in program_paths:
        program_files.extend(glob.glob(ppath + '*.py'))
    for program_file in program_files:
        log.s('at program_file: ' + program_file)
        test_params = get_test_parameters(program_file)
        log.s('with ' + str(len(test_params)) + ' test params')
        df = run_tests(test_params)
        # comp_df = comp_df.append(df, ignore_index=True)
        comp_df = pandas.concat([comp_df, df], ignore_index=True)

    comp_df.to_csv('../data/quix_slicing_comparison.csv.zip', compression='zip')
    log.s('done')


def run_tests(test_params):
    comparison = []
    for test_param in test_params:
        test_results = slice_test_quix(test_param[0].replace(benchmark_dir(), 'benchmark'), test_param[1], test_param[2], test_param[3], test_param[4])
        test_results.update(test_param[5])
        comparison.append(test_results)
    return pandas.DataFrame(comparison)


def slice_test_quix(test_name, py_code, expected, slice_variable, slice_line):
    stage = 'started'
    stats_result = {'test_name': test_name,
                    'code_len': None,
                    'dumb_dyn_slice': None,
                    'dyn_slice': None,
                    'pruned_slice': None,
                    'relevant_slice': None,
                    'pruned_relevant_slice': None,
                    'dumb_dyn_slice_len': None,
                    'pruned_slice_len': None,
                    'dyn_slice_len': None,
                    'relevant_slice_len': None,
                    'pruned_relevant_slice_len': None,
                    'runtime_bare_test': None,
                    'runtime_tracing_augmented_test': None,
                    'runtime_dyn_slice': None,
                    'runtime_pruned_slice': None,
                    'runtime_relevant_slice': None,
                    'runtime_pruned_relevant_slice': None,
                    'perf_runtime_bare_test': None,
                    'perf_runtime_tracing_augmented_test': None,
                    'perf_runtime_dyn_slice': None,
                    'perf_runtime_pruned_slice': None,
                    'perf_runtime_relevant_slice': None,
                    'perf_runtime_pruned_relevant_slice': None,
                    'len_exec_trace': None,
                    'test_result': None,
                    'pruned_sliced_result_equal_to_bare': None,
                    'relevant_sliced_result_equal_to_bare': None,
                    'pruned_relevant_sliced_result_equal_to_bare': None,
                    'exception': None,
                    'stage': stage,
                    'num_boolops_pruned_sliced': None,
                    'num_lines_with_boolops_pruned_sliced': None,
                    'num_boolops_dyn_sliced': None,
                    'num_lines_with_boolops_dyn_sliced': None,
                    'num_boolops_relevant_sliced': None,
                    'num_lines_with_boolops_relevant_sliced': None,
                    'num_boolops_pruned_relevant_sliced': None,
                    'num_lines_with_boolops_pruned_relevant_sliced': None,
                    }
    try:
        # run test as is and record result
        # bare execution:
        stage = 'bare execution'

        perf_start = time.perf_counter()
        bare_outcome = run_code(py_code, slice_variable)
        stats_result['perf_runtime_bare_test'] = time.perf_counter() - perf_start
        stats_result['test_result'] = bare_outcome == expected

        stats_result['code_len'] = len(py_code.splitlines())

        stats_result['runtime_bare_test'] = -1
        if NUM_RUNS_TIMEIT:
            stats_result['runtime_bare_test'] = timeit.timeit(stmt=py_code, number=NUM_RUNS_TIMEIT) / NUM_RUNS_TIMEIT

        # trace
        stage = 'trace'

        io_augmented_code = trace.augment_python(py_code)

        perf_start = time.perf_counter()
        trace.run_trace(io_augmented_code)
        stats_result['perf_runtime_tracing_augmented_test'] = time.perf_counter() - perf_start
        exec_trace = get_trace().copy()
        stats_result['len_exec_trace'] = len(exec_trace)
        clear_trace()

        stats_result['runtime_tracing_augmented_test'] = -1
        if NUM_RUNS_TIMEIT:
            tracing_call = """
trace.run_trace(io_augmented_code)
clear_trace()"""
            globals_copy = globals().copy()
            globals_copy.update({'io_augmented_code': io_augmented_code})
            stats_result['runtime_tracing_augmented_test'] = timeit.timeit(stmt=tracing_call, number=NUM_RUNS_TIMEIT,
                                                           globals=globals_copy) / NUM_RUNS_TIMEIT

        # dumb slicing
        try:
            stage = 'dumb slicing'
            dumb_dyn_slice = dumb_dynamic_slice(exec_trace)
            stats_result['dumb_dyn_slice'] = dumb_dyn_slice,
            stats_result['dumb_dyn_slice_len'] = len(dumb_dyn_slice)

        except Exception as e:
            stats_result['dumb_dyn_slice_exception'] = str(type(e)) + str(e.args)
            stats_result['stage'] = stage

        # dyn slice
        try:
            stage = 'dyn slice'

            perf_start = time.perf_counter()
            dyn_slice, dyn_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, slice_variable, slice_line)
            stats_result['perf_runtime_dyn_slice'] = time.perf_counter() - perf_start
            stats_result['dyn_slice'] = dyn_slice
            stats_result['dyn_slice_len'] = len(dyn_slice)

            stats_result['runtime_dyn_slice'] = -1
            if NUM_RUNS_TIMEIT:
                globals_copy = globals().copy()
                globals_copy.update({'exec_trace': exec_trace, 'slice_variable': slice_variable, 'slice_line': slice_line})
                stats_result['runtime_dyn_slice'] = timeit.timeit(stmt='get_dynamic_slice(exec_trace, slice_variable, slice_line)',
                                                  number=NUM_RUNS_TIMEIT, globals=globals_copy) / NUM_RUNS_TIMEIT

            # dyn code from slice
            stage = 'dyn code from slice'
            dyn_sliced_code = code_from_slice_ast(py_code, dyn_slice, dyn_bool_ops, exec_trace, func_param_removal)
            dyn_sliced_boolops_stats = file_boolops_stats(dyn_sliced_code)
            stats_result['num_boolops_dyn_sliced'] = dyn_sliced_boolops_stats['num_boolops']
            stats_result['num_lines_with_boolops_dyn_sliced'] = dyn_sliced_boolops_stats['num_lines_with_boolops']
        except Exception as e:
            stats_result['dyn_slice_exception'] = str(type(e)) + str(e.args)
            stats_result['stage'] = stage
        # pruned slice
        try:
            stage = 'pruned slice'

            perf_start = time.perf_counter()
            pruned_slice, cond_bool_ops, func_param_removal = get_pruned_slice(exec_trace, slice_variable, slice_line)
            stats_result['perf_runtime_pruned_slice'] = time.perf_counter() - perf_start
            stats_result['pruned_slice'] = pruned_slice
            stats_result['pruned_slice_len'] = len(pruned_slice)

            stats_result['runtime_pruned_slice'] = -1
            if NUM_RUNS_TIMEIT:
                globals_copy = globals().copy()
                globals_copy.update({'exec_trace': exec_trace, 'slice_variable': slice_variable, 'slice_line': slice_line})
                stats_result['runtime_pruned_slice'] = timeit.timeit(stmt='get_pruned_slice(exec_trace, slice_variable, slice_line)',
                                                   number=NUM_RUNS_TIMEIT, globals=globals_copy) / NUM_RUNS_TIMEIT

            # code from slice
            stage = 'code from slice'
            sliced_code = code_from_slice_ast(py_code, pruned_slice, cond_bool_ops, exec_trace, func_param_removal)
            pruned_sliced_boolops_stats = file_boolops_stats(sliced_code)
            stats_result['num_boolops_pruned_sliced'] = pruned_sliced_boolops_stats['num_boolops']
            stats_result['num_lines_with_boolops_pruned_sliced'] = pruned_sliced_boolops_stats['num_lines_with_boolops']

            # run sliced
            stage = 'run pruned sliced'
            sliced_outcome = run_code(sliced_code, slice_variable)
            stats_result['pruned_sliced_result_equal_to_bare'] = bare_outcome == sliced_outcome
        except Exception as e:
            stats_result['pruned_slice_exception'] = str(type(e)) + str(e.args)
            stats_result['stage'] = stage

        # relevant slice
        try:
            stage = 'relevant slice'

            perf_start = time.perf_counter()
            relevant_slice, cond_bool_ops, func_param_removal = get_relevant_slice(exec_trace, slice_variable, slice_line)
            stats_result['perf_runtime_relevant_slice'] = time.perf_counter() - perf_start
            stats_result['relevant_slice'] = relevant_slice
            stats_result['relevant_slice_len'] = len(relevant_slice)

            stats_result['runtime_relevant_slice'] = -1
            if NUM_RUNS_TIMEIT:
                globals_copy = globals().copy()
                globals_copy.update({'exec_trace': exec_trace, 'slice_variable': slice_variable, 'slice_line': slice_line})
                stats_result['runtime_relevant_slice'] = timeit.timeit(stmt='get_relevant_slice(exec_trace, slice_variable, slice_line)',
                                                   number=NUM_RUNS_TIMEIT, globals=globals_copy) / NUM_RUNS_TIMEIT

            # code from slice
            stage = 'code from relevant slice'
            sliced_code = code_from_slice_ast(py_code, relevant_slice, cond_bool_ops, exec_trace, func_param_removal)
            relevant_sliced_boolops_stats = file_boolops_stats(sliced_code)
            stats_result['num_boolops_relevant_sliced'] = relevant_sliced_boolops_stats['num_boolops']
            stats_result['num_lines_with_boolops_relevant_sliced'] = relevant_sliced_boolops_stats['num_lines_with_boolops']

            # run sliced
            stage = 'run relevant sliced'
            sliced_outcome = run_code(sliced_code, slice_variable)
            stats_result['relevant_sliced_result_equal_to_bare']  = sliced_outcome == bare_outcome
        except Exception as e:
            stats_result['relevant_slice_exception'] = str(type(e)) + str(e.args)
            stats_result['stage'] = stage


        # pruned relevant slice
        try:
            stage = 'pruned relevant slice'

            perf_start = time.perf_counter()
            pruned_relevant_slice, cond_bool_ops, func_param_removal = get_pruned_relevant_slice(exec_trace, slice_variable, slice_line)
            stats_result['perf_runtime_pruned_relevant_slice'] = time.perf_counter() - perf_start
            stats_result['pruned_relevant_slice'] = pruned_relevant_slice
            stats_result['pruned_relevant_slice_len'] = len(pruned_relevant_slice)

            stats_result['runtime_pruned_relevant_slice'] = -1
            if NUM_RUNS_TIMEIT:
                globals_copy = globals().copy()
                globals_copy.update({'exec_trace': exec_trace, 'slice_variable': slice_variable, 'slice_line': slice_line})
                stats_result['runtime_pruned_relevant_slice'] = timeit.timeit(stmt='get_pruned_relevant_slice(exec_trace, slice_variable, slice_line)',
                                                   number=NUM_RUNS_TIMEIT, globals=globals_copy) / NUM_RUNS_TIMEIT

            # code from slice
            stage = 'code from pruned relevant slice'
            sliced_code = code_from_slice_ast(py_code, pruned_relevant_slice, cond_bool_ops, exec_trace, func_param_removal)
            pruned_relevant_sliced_boolops_stats = file_boolops_stats(sliced_code)
            stats_result['num_boolops_pruned_relevant_sliced'] = pruned_relevant_sliced_boolops_stats['num_boolops']
            stats_result['num_lines_with_boolops_pruned_relevant_sliced'] = pruned_relevant_sliced_boolops_stats[
                'num_lines_with_boolops']

            # run sliced
            stage = 'run pruned relevant sliced'
            sliced_outcome = run_code(sliced_code, slice_variable)
            stats_result['pruned_relevant_sliced_result_equal_to_bare'] = sliced_outcome == bare_outcome
        except Exception as e:
            stats_result['pruned_relevant_slice_exception'] = str(type(e)) + str(e.args)
            stats_result['stage'] = stage

        stats_result['stage'] = 'finished'
    except Exception as e:
        stats_result['exception'] = str(type(e)) + str(e.args)
        stats_result['stage'] = stage
    finally:
        clear_trace()
        return stats_result


def normalize_output(output):
    if isinstance(output, types.GeneratorType):
        output = list(output)
    return json.loads(json.dumps(output))


@timeout_decorator.timeout(QUIX_TIMEOUT)
def run_code(sliced_code, variable_name):
    globals_space = globals().copy()
    exec(compile(sliced_code, filename="", mode="exec"), globals_space)
    return normalize_output(globals_space[variable_name])


if __name__ == "__main__":
    main()
