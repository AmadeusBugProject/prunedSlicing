import glob
import time
import pandas
import timeit
from ast_tree_tracer import trace
from ast_tree_tracer.trace_container import get_trace, clear_trace
from benchmark.benchmark_root import benchmark_dir
from constants import NUM_RUNS_TIMEIT
from evaluation.boolop_counter.count_boolops import file_boolops_stats
from evaluation.slice_benchmarks.utils import remove_comments_and_top_level_const_expression_strings
from helpers.Logger import Logger
from slicing.code_from_slice import code_from_slice_ast
from slicing.slice import get_dynamic_slice, get_pruned_slice, dumb_dynamic_slice, get_relevant_slice, \
    get_pruned_relevant_slice
from slicing.dummy import Dummy

log = Logger()

slice_variable = 'alt_sep_actual'

dummy_test_data = {'Number': '', 'Cur_Vertical_Sep': 0, 'High_Confidence': 0, 'Two_of_Three_Reports_Valid': 0,
                   'Own_Tracked_Alt': 0, 'Own_Tracked_Alt_Rate': 0, 'Other_Tracked_Alt': 0,
                   'Alt_Layer_Value': 0,
                   'Up_Separation': 0, 'Down_Separation': 0, 'Other_RAC': 0, 'Other_Capability': 0,
                   'Climb_Inhibit': 1,
                   'Expected_output': 0}


def get_tcas_versions():
    tcas_versions = [benchmark_dir() + '/tcas/Tcas.py']
    tcas_versions.extend(glob.glob(benchmark_dir() + '/tcas/faulty_versions/Tcas_Fault*.py'))
    tcas_versions.sort()
    return tcas_versions


def add_function_call(tcas_code, test_data):
    lines = tcas_code.splitlines()
    lines.append('test_data = ' + str(test_data))
    lines.append('tcas_instance = Tcas(test_data)')
    lines.append(slice_variable + ' = tcas_instance.alt_sep_test()')
    return '\n'.join(lines), len(lines)


def main():
    log.s('Starting')
    test_inputs_df = pandas.read_csv(benchmark_dir() + '/tcas/testData.csv')
    test_inputs = [x for x in test_inputs_df.to_dict(orient='records')]
    test_inputs[:1]
    comp_df = pandas.DataFrame()
    for tcas_file in get_tcas_versions():
        log.s('at Tcas version: ' + tcas_file)
        df = slice_file(tcas_file, test_inputs)
        # comp_df = comp_df.append(df, ignore_index=True)
        comp_df = pandas.concat([comp_df, df], ignore_index=True)

    comp_df.to_csv('../data/tcas_slicing_comparison.csv.zip', compression='zip')
    log.s('done')


def run_slicing(tcas_file, tcas_test_code, tcas_augmented, test_inputs, slice_line):
    comparison = []
    for test_input in test_inputs:
        test_number = test_input['Number']
        stage = 'started'

        stats_result = {'test_name': tcas_file.replace(benchmark_dir(), 'benchmark') + test_number,
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
                        'dumb_dyn_slice_exception': None,
                        'dyn_slice_exception': None,
                        'pruned_slice_exception': None,
                        'relevant_slice_exception': None,
                        'pruned_relevant_slice_exception': None
                        }

        try:
            tcas_test_code_w_input = tcas_test_code.replace(str(dummy_test_data), str(test_input))
            tcas_augmented_w_input = tcas_augmented.replace(str(dummy_test_data), str(test_input))

            stats_result['test_name'] = tcas_file.replace(benchmark_dir(), 'benchmark') + test_number
            stats_result['code_len'] = len(tcas_test_code_w_input.splitlines())

            # bare execution:
            stage = 'bare execution'

            stats_result['runtime_bare_test'] = -1
            if NUM_RUNS_TIMEIT:
                stats_result['runtime_bare_test'] = timeit.timeit(stmt=tcas_test_code_w_input, number=NUM_RUNS_TIMEIT)/NUM_RUNS_TIMEIT

            perf_start = time.perf_counter()
            bare_result = run_py_code(tcas_test_code_w_input, slice_variable)
            stats_result['perf_runtime_bare_test']  = time.perf_counter() - perf_start
            stats_result['test_result'] = bare_result == test_input['Expected_output']


            # tracing execution
            stage = 'trace'

            stats_result['runtime_tracing_augmented_test'] = -1
            if NUM_RUNS_TIMEIT:
                tracing_call = """
trace.run_trace(tcas_augmented_w_input)
clear_trace()"""
                globals_copy = globals().copy()
                globals_copy.update({'tcas_augmented_w_input': tcas_augmented_w_input})
                stats_result['runtime_tracing_augmented_test'] = timeit.timeit(stmt=tracing_call, number=NUM_RUNS_TIMEIT, globals=globals_copy)/NUM_RUNS_TIMEIT

            perf_start = time.perf_counter()
            trace.run_trace(tcas_augmented_w_input)
            stats_result['perf_runtime_tracing_augmented_test'] = time.perf_counter() - perf_start
            exec_trace = get_trace()
            stats_result['len_exec_trace'] = len(exec_trace)

            # dumb slicing
            try:
                stage = 'dumb slicing'
                dumb_dyn_slice = dumb_dynamic_slice(exec_trace)
                stats_result['dumb_dyn_slice'] = dumb_dyn_slice,
                stats_result['dumb_dyn_slice_len'] = len(dumb_dyn_slice)

            except Exception as e:
                stats_result['dumb_dyn_slice_exception'] = str(type(e)) + str(e.args)
                stats_result['stage'] = stage

            ############################################
            # dynamic slicing
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

                dyn_sliced_code = code_from_slice_ast(tcas_test_code_w_input, dyn_slice, dyn_bool_ops, exec_trace, func_param_removal)
                dyn_sliced_boolops_stats = file_boolops_stats(dyn_sliced_code)

                stats_result['num_boolops_dyn_sliced'] = dyn_sliced_boolops_stats['num_boolops']
                stats_result['num_lines_with_boolops_dyn_sliced'] = dyn_sliced_boolops_stats['num_lines_with_boolops']
            except Exception as e:
                stats_result['dyn_slice_exception'] = str(type(e)) + str(e.args)
                stats_result['stage'] = stage

            #####################################
            # pruned slicing
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

                # pruned code from slice
                stage = 'code from slice'

                sliced_code = code_from_slice_ast(tcas_test_code_w_input, pruned_slice, cond_bool_ops, exec_trace, func_param_removal)
                pruned_sliced_boolops_stats = file_boolops_stats(sliced_code)
                stats_result['num_boolops_pruned_sliced'] = pruned_sliced_boolops_stats['num_boolops']
                stats_result['num_lines_with_boolops_pruned_sliced'] = pruned_sliced_boolops_stats['num_lines_with_boolops']

                # run sliced
                stage = 'run pruned sliced'
                sliced_result = run_py_code(sliced_code, slice_variable)
                stats_result['pruned_sliced_result_equal_to_bare'] = bare_result == sliced_result
            except Exception as e:
                stats_result['pruned_slice_exception'] = str(type(e)) + str(e.args)
                stats_result['stage'] = stage

            #####################################
            # relevant slicing
            try:
                stage = 'relevant slice'

                stats_result['runtime_relevant_slice'] = -1
                if NUM_RUNS_TIMEIT:
                    globals_copy = globals().copy()
                    globals_copy.update(
                        {'exec_trace': exec_trace, 'slice_variable': slice_variable, 'slice_line': slice_line})
                    stats_result['runtime_relevant_slice'] = timeit.timeit(stmt='get_relevant_slice(exec_trace, slice_variable, slice_line)',
                                                         number=NUM_RUNS_TIMEIT, globals=globals_copy) / NUM_RUNS_TIMEIT

                perf_start = time.perf_counter()
                relevant_slice, cond_bool_ops, func_param_removal = get_relevant_slice(exec_trace, slice_variable, slice_line)
                stats_result['perf_runtime_relevant_slice'] = time.perf_counter() - perf_start
                stats_result['relevant_slice'] = relevant_slice
                stats_result['relevant_slice_len'] = len(relevant_slice)

                # code from relevant slice
                stage = 'code from relevant slice'

                sliced_code = code_from_slice_ast(tcas_test_code_w_input, relevant_slice, cond_bool_ops, exec_trace,
                                                  func_param_removal)
                relevant_sliced_boolops_stats = file_boolops_stats(sliced_code)
                stats_result['num_boolops_relevant_sliced'] = relevant_sliced_boolops_stats['num_boolops']
                stats_result['num_lines_with_boolops_relevant_sliced'] = relevant_sliced_boolops_stats['num_lines_with_boolops']

                # run sliced
                stage = 'run relevant sliced'
                sliced_result = run_py_code(sliced_code, slice_variable)
                stats_result['relevant_sliced_result_equal_to_bare'] = bare_result == sliced_result
            except Exception as e:
                stats_result['relevant_slice_exception'] = str(type(e)) + str(e.args)
                stats_result['stage'] = stage

            #####################################
            # pruned relevant slicing
            try:
                stage = 'pruned relevant slice'

                stats_result['runtime_pruned_relevant_slice'] = -1
                if NUM_RUNS_TIMEIT:
                    globals_copy = globals().copy()
                    globals_copy.update(
                        {'exec_trace': exec_trace, 'slice_variable': slice_variable, 'slice_line': slice_line})
                    stats_result['runtime_pruned_relevant_slice'] = timeit.timeit(stmt='get_pruned_relevant_slice(exec_trace, slice_variable, slice_line)',
                                                         number=NUM_RUNS_TIMEIT, globals=globals_copy) / NUM_RUNS_TIMEIT

                perf_start = time.perf_counter()
                pruned_relevant_slice, cond_bool_ops, func_param_removal = get_pruned_relevant_slice(exec_trace, slice_variable, slice_line)
                stats_result['perf_runtime_pruned_relevant_slice'] = time.perf_counter() - perf_start
                stats_result['pruned_relevant_slice'] = pruned_relevant_slice
                stats_result['pruned_relevant_slice_len'] = len(pruned_relevant_slice)

                # pruned code from slice
                stage = 'code from pruned relevant slice'

                sliced_code = code_from_slice_ast(tcas_test_code_w_input, pruned_relevant_slice, cond_bool_ops, exec_trace,
                                                  func_param_removal)
                pruned_relevant_sliced_boolops_stats = file_boolops_stats(sliced_code)

                stats_result['num_boolops_pruned_relevant_sliced'] = pruned_relevant_sliced_boolops_stats['num_boolops']
                stats_result['num_lines_with_boolops_pruned_relevant_sliced'] = pruned_relevant_sliced_boolops_stats['num_lines_with_boolops']

                # run sliced
                stage = 'run pruned relevant sliced'
                sliced_result = run_py_code(sliced_code, slice_variable)
                stats_result['pruned_relevant_sliced_result_equal_to_bare'] = bare_result == sliced_result
            except Exception as e:
                stats_result['pruned_relevant_slice_exception'] = str(type(e)) + str(e.args)
                stats_result['stage'] = stage

            stats_result['stage'] = 'finished'

        except Exception as e:
            stats_result['overall_exception'] = str(type(e)) + str(e.args)
            stats_result['stage'] = stage
        finally:
            comparison.append(stats_result)
            clear_trace()
    return pandas.DataFrame(comparison)


def slice_file(tcas_file, test_inputs):
    with open(tcas_file, 'r') as fd:
        tcas_code = fd.read()

    tcas_code = remove_comments_and_top_level_const_expression_strings(tcas_code)
    boolops_stats = file_boolops_stats(tcas_code)

    tcas_test_code, line = add_function_call(tcas_code, dummy_test_data)
    tcas_augmented = trace.augment_python(tcas_test_code)

    test_results = run_slicing(tcas_file, tcas_test_code, tcas_augmented, test_inputs, line)
    test_results['num_boolops'] = boolops_stats['num_boolops']
    test_results['num_lines_with_boolops'] = boolops_stats['num_lines_with_boolops']
    return test_results


def run_py_code(py_code, variable_name):
    globals_space = globals().copy()
    exec(compile(py_code, filename="", mode="exec"), globals_space)
    return globals_space[variable_name]


if __name__ == "__main__":
    main()
