import glob
import json
import time
import pandas
import timeit
import timeout_decorator
import distutils.util
from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace, clear_trace
from benchmark.benchmark_root import benchmark_dir
from constants import NUM_RUNS_TIMEIT, REFACTORY_TIMEOUT
from evaluation.boolop_counter.count_boolops import file_boolops_stats
from evaluation.slice_benchmarks.utils import remove_comments_and_top_level_const_expression_strings
from helpers.Logger import Logger
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import get_dynamic_slice, get_pruned_slice, dumb_dynamic_slice, get_pruned_relevant_slice, \
    get_relevant_slice
from slicing.dummy import Dummy

# usage inside tests
from collections import OrderedDict
import heapq

log = Logger()

refactory_path = benchmark_dir() + '/refactory/data/'

questions = [
    {'question_path': refactory_path + 'question_1/',
     'num_inputs': 11,
     'output_type': int,
     'slice_variable': 'search_result',
     'input_dummy': 'search(0, (0, 0, 0, 0, 0, 0))',
     'add_globals': {}},
    {'question_path': refactory_path + 'question_2/',
     'num_inputs': 17,
     'output_type': distutils.util.strtobool,
     'slice_variable': 'day_results',
     'input_dummy': 'unique_day("-1", tuple_of_possible_birthdays)',
     'add_globals': {'tuple_of_possible_birthdays': (('May', '15'),
                                                     ('May', '16'),
                                                     ('May', '19'),
                                                     ('June', '17'),
                                                     ('June', '18'),
                                                     ('July', '14'),
                                                     ('July', '16'),
                                                     ('August', '14'),
                                                     ('August', '15'),
                                                     ('August', '17'))}},
    {'question_path': refactory_path + 'question_3/',
     'num_inputs': 4,
     'output_type': json.loads,
     'slice_variable': 'extras_result',
     'input_dummy': 'remove_extras([0])',
     'add_globals': {'OrderedDict': OrderedDict}},
    {'question_path': refactory_path + 'question_4/',
     'num_inputs': 6,
     'output_type': eval,
     'slice_variable': 'sort_age_result',
     'input_dummy': 'sort_age([("X", -1)])',
     'add_globals': {}},
    {'question_path': refactory_path + 'question_5/',
     'num_inputs': 5,
     'output_type': json.loads,
     'slice_variable': 'top_k_result',
     'input_dummy': 'top_k([], -1)',
     'add_globals': {'heapq': heapq}},
]


def get_test_parameters_for_question(question_path, num_inputs, output_type, slice_variable, input_dummy, add_globals):

    io_params = []
    for io_number in range(1, num_inputs + 1):
        with open(question_path + 'ans/input_' + "{:03d}".format(io_number) + '.txt', 'r') as fd:
            func_call = slice_variable + ' = ' + fd.read()
        with open(question_path + 'ans/output_' + "{:03d}".format(io_number) + '.txt', 'r') as fd:
            expected = output_type(fd.read().rstrip())  # to be
        io_params.append([func_call, expected])
    log.s(question_path)
    log.s('with ' + str(len(io_params)) + ' parameters')

    code_paths = ['code/correct/', 'code/fail/', 'code/reference/', 'code/wrong/']
    py_files = []

    for py_path in code_paths:
        py_glob = glob.glob(question_path + py_path + '*.py')
        py_glob.sort()
        log.s(py_path)
        log.s('with ' + str(len(py_glob)) + ' python files')
        unique_code_snippets = {}
        for pyfile in py_glob:
            with open(pyfile, 'r') as fd:
                unique_code_snippets.update({fd.read().strip(): pyfile})
        log.s('with ' + str(len(unique_code_snippets.values())) + ' unique python code snippets')
        py_files.extend(unique_code_snippets.values())

    test_params = []
    for pyfile in py_files:
        with open(pyfile, 'r') as fd:
            py_code = '\n'.join(fd.read().splitlines() + [slice_variable + ' = ' + input_dummy])
        py_code = remove_comments_and_top_level_const_expression_strings(py_code)
        boolops_stats = file_boolops_stats(py_code)

        slice_line = len(py_code.splitlines())
        for number, io in enumerate(io_params):
            io_py_code = py_code.replace(slice_variable + ' = ' + input_dummy, io[0])
            test_name = pyfile + '#' + str(number) + ':'
            test_params.append([test_name, io_py_code, io[1], slice_variable, slice_line, add_globals, boolops_stats])
    return test_params


def main():
    log.s('Starting')
    comp_df = pandas.DataFrame()

    for question in questions:
        log.s('at question: ' + question['question_path'])
        test_params = get_test_parameters_for_question(question['question_path'],
                                                       question['num_inputs'],
                                                       question['output_type'],
                                                       question['slice_variable'],
                                                       question['input_dummy'],
                                                       question['add_globals'])
        log.s('with ' + str(len(test_params)) + ' test params')

        df = run_question_tests_quix(test_params)
        # comp_df = comp_df.append(df, ignore_index=True)
        comp_df = pandas.concat([comp_df, df], ignore_index=True)

    comp_df.to_csv('../data/refactory_slicing_comparison.csv.zip', compression='zip')
    log.s('done')


def run_question_tests_quix(test_params):
    comparison = []
    for test_param in test_params:
        test_results = slice_test_refactory(test_param[0].replace(benchmark_dir(), 'benchmark'), test_param[1], test_param[2], test_param[3], test_param[4], test_param[5])
        test_results.update(test_param[6])
        comparison.append(test_results)
    return pandas.DataFrame(comparison)


def slice_test_refactory(test_name, io_py_code, expected, slice_variable, slice_line, add_globals):
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
        stage = 'bare execution'

        perf_start = time.perf_counter()
        bare_outcome = run_come_code(io_py_code, slice_variable, add_globals)
        stats_result['perf_runtime_bare_test'] = time.perf_counter() - perf_start
        stats_result['test_result'] = bare_outcome == expected

        stats_result['code_len'] = len(io_py_code.splitlines())

        stats_result['runtime_bare_test'] = -1
        if NUM_RUNS_TIMEIT:
            globals_copy = globals().copy()
            globals_copy.update(add_globals)
            stats_result['runtime_bare_test'] = timeit.timeit(stmt=io_py_code, number=NUM_RUNS_TIMEIT, globals=globals_copy)/NUM_RUNS_TIMEIT

        # trace
        stage = 'trace'

        io_augmented_code = trace.augment_python(io_py_code)

        perf_start = time.perf_counter()
        trace.run_trace(io_augmented_code, add_globals)
        stats_result['perf_runtime_tracing_augmented_test'] = time.perf_counter() - perf_start
        exec_trace = get_trace().copy()
        stats_result['len_exec_trace'] = len(exec_trace)
        clear_trace()

        stats_result['runtime_tracing_augmented_test'] = -1
        if NUM_RUNS_TIMEIT:
            tracing_call = """
trace.run_trace(io_augmented_code, add_globals)
clear_trace()"""
            globals_copy = globals().copy()
            globals_copy.update({'io_augmented_code': io_augmented_code})
            globals_copy.update({'add_globals': add_globals})
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

            stats_result['runtime_dyn_slice'] = -1
            if NUM_RUNS_TIMEIT:
                globals_copy = globals().copy()
                globals_copy.update({'exec_trace': exec_trace, 'slice_variable': slice_variable, 'slice_line': slice_line})
                stats_result['runtime_dyn_slice'] = timeit.timeit(stmt='get_dynamic_slice(exec_trace, slice_variable, slice_line)', number=NUM_RUNS_TIMEIT, globals=globals_copy)/NUM_RUNS_TIMEIT

            perf_start = time.perf_counter()
            dyn_slice, dyn_bool_ops, func_param_removal = get_dynamic_slice(exec_trace, slice_variable, slice_line)
            stats_result['perf_runtime_dyn_slice'] = time.perf_counter() - perf_start
            stats_result['dyn_slice'] = dyn_slice
            stats_result['dyn_slice_len'] = len(dyn_slice)

            # dyn code from slice
            stage = 'dyn code from slice'

            dyn_sliced_code = code_from_slice_ast(io_py_code, dyn_slice, dyn_bool_ops, exec_trace, func_param_removal)
            dyn_sliced_boolops_stats = file_boolops_stats(dyn_sliced_code)
            stats_result['num_boolops_dyn_sliced'] = dyn_sliced_boolops_stats['num_boolops']
            stats_result['num_lines_with_boolops_dyn_sliced'] = dyn_sliced_boolops_stats['num_lines_with_boolops']
        except Exception as e:
            stats_result['dyn_slice_exception'] = str(type(e)) + str(e.args)
            stats_result['stage'] = stage

        # pruned slice
        try:
            stage = 'pruned slice'

            stats_result['runtime_pruned_slice'] = -1
            if NUM_RUNS_TIMEIT:
                globals_copy = globals().copy()
                globals_copy.update({'exec_trace': exec_trace, 'slice_variable': slice_variable, 'slice_line': slice_line})
                stats_result['runtime_pruned_slice'] = timeit.timeit(stmt='get_pruned_slice(exec_trace, slice_variable, slice_line)', number=NUM_RUNS_TIMEIT, globals=globals_copy)/NUM_RUNS_TIMEIT

            perf_start = time.perf_counter()
            pruned_slice, cond_bool_ops, func_param_removal = get_pruned_slice(exec_trace, slice_variable, slice_line)
            stats_result['perf_runtime_pruned_slice'] = time.perf_counter() - perf_start
            stats_result['pruned_slice'] = pruned_slice
            stats_result['pruned_slice_len'] = len(pruned_slice)

            # code from slice
            stage = 'code from slice'

            sliced_code = code_from_slice_ast(io_py_code, pruned_slice, cond_bool_ops, exec_trace, func_param_removal)
            pruned_sliced_boolops_stats = file_boolops_stats(sliced_code)
            stats_result['num_boolops_pruned_sliced'] = pruned_sliced_boolops_stats['num_boolops']
            stats_result['num_lines_with_boolops_pruned_sliced'] = pruned_sliced_boolops_stats['num_lines_with_boolops']

            # run sliced
            stage = 'run pruned sliced'
            sliced_outcome = run_come_code(sliced_code, slice_variable, add_globals)
            stats_result['pruned_sliced_result_equal_to_bare'] = bare_outcome == sliced_outcome
        except Exception as e:
            stats_result['pruned_slice_exception'] = str(type(e)) + str(e.args)
            stats_result['stage'] = stage

        # relevant slice
        try:
            stage = 'relevant slice'

            stats_result['runtime_relevant_slice'] = -1
            if NUM_RUNS_TIMEIT:
                globals_copy = globals().copy()
                globals_copy.update({'exec_trace': exec_trace, 'slice_variable': slice_variable, 'slice_line': slice_line})
                stats_result['runtime_relevant_slice'] = timeit.timeit(stmt='get_relevant_slice(exec_trace, slice_variable, slice_line)', number=NUM_RUNS_TIMEIT, globals=globals_copy)/NUM_RUNS_TIMEIT

            perf_start = time.perf_counter()
            relevant_slice, cond_bool_ops, func_param_removal = get_relevant_slice(exec_trace, slice_variable, slice_line)
            stats_result['perf_runtime_relevant_slice'] = time.perf_counter() - perf_start
            stats_result['relevant_slice'] = relevant_slice
            stats_result['relevant_slice_len'] = len(relevant_slice)

            # code from slice
            stage = 'code from relevant slice'

            sliced_code = code_from_slice_ast(io_py_code, relevant_slice, cond_bool_ops, exec_trace, func_param_removal)
            relevant_sliced_boolops_stats = file_boolops_stats(sliced_code)
            stats_result['num_boolops_relevant_sliced'] = relevant_sliced_boolops_stats['num_boolops']
            stats_result['num_lines_with_boolops_relevant_sliced'] = relevant_sliced_boolops_stats['num_lines_with_boolops']

            # run sliced
            stage = 'run relevant sliced'

            sliced_outcome = run_come_code(sliced_code, slice_variable, add_globals)
            stats_result['relevant_sliced_result_equal_to_bare'] = sliced_outcome == bare_outcome
        except Exception as e:
            stats_result['relevant_slice_exception'] = str(type(e)) + str(e.args)
            stats_result['stage'] = stage

        # pruned relevant slice
        try:
            stage = 'pruned relevant slice'

            stats_result['runtime_pruned_relevant_slice'] = -1
            if NUM_RUNS_TIMEIT:
                globals_copy = globals().copy()
                globals_copy.update({'exec_trace': exec_trace, 'slice_variable': slice_variable, 'slice_line': slice_line})
                stats_result['runtime_pruned_relevant_slice'] = timeit.timeit(stmt='get_pruned_relevant_slice(exec_trace, slice_variable, slice_line)',
                                                       number=NUM_RUNS_TIMEIT, globals=globals_copy) / NUM_RUNS_TIMEIT

            perf_start = time.perf_counter()
            pruned_relevant_slice, cond_bool_ops, func_param_removal = get_pruned_relevant_slice(exec_trace, slice_variable, slice_line)
            stats_result['perf_runtime_pruned_relevant_slice'] = time.perf_counter() - perf_start
            stats_result['pruned_relevant_slice'] = pruned_relevant_slice
            stats_result['pruned_relevant_slice_len'] = len(pruned_relevant_slice)

            # code from slice
            stage = 'code from pruned relevant slice'

            sliced_code = code_from_slice_ast(io_py_code, pruned_relevant_slice, cond_bool_ops, exec_trace, func_param_removal)
            pruned_relevant_sliced_boolops_stats = file_boolops_stats(sliced_code)

            stats_result['num_boolops_pruned_relevant_sliced'] = pruned_relevant_sliced_boolops_stats['num_boolops']
            stats_result['num_lines_with_boolops_pruned_relevant_sliced'] = pruned_relevant_sliced_boolops_stats[
                'num_lines_with_boolops']

            # run sliced
            stage = 'run pruned relevant sliced'

            sliced_outcome = run_come_code(sliced_code, slice_variable, add_globals)
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


@timeout_decorator.timeout(REFACTORY_TIMEOUT)
def run_come_code(some_code, variable_name, add_globals):
    globals_space = globals().copy()
    globals_space.update(add_globals)
    exec(compile(some_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]


if __name__ == "__main__":
    main()
