import sys

# collect_ignore = [] # to list whole files to be ignored


# QuixBugs test cases from the "correct" folder that are broken out of the box
QUIX_FAILING_OUT_OF_THE_BOX = [
    "benchmark/quixbugs/test_quix.py::TestQuix::test_quix_167_knapsack_9", # timeout, unperformant implementation with big input
    "benchmark/quixbugs/test_quix.py::TestQuix::test_quix_077_levenshtein_3", # timeout, unperformant implementation with big input
    "benchmark/quixbugs/test_quix.py::TestQuix::test_quix_105_sqrt_4", # float comparison
    "benchmark/quixbugs/test_quix.py::TestQuix::test_quix_106_sqrt_5", # float comparison
]

# issues that could be fixed by implementing relevant slicing.
RELEVANT_SLICING_ISSUES = [
    "benchmark/quixbugs/test_quix_failures.py::TestQuixFailure::test_quix8",
    "benchmark/refactory/test_new_refactory_failures.py::TestNewRefactoryFailures::test_timeout_1",
    "benchmark/refactory/test_new_refactory_failures.py::TestNewRefactoryFailures::test_timeout_2",
    "benchmark/refactory/test_new_refactory_failures.py::TestNewRefactoryFailures::test_timeout_3",
    "benchmark/refactory/test_new_refactory_failures.py::TestNewRefactoryFailures::test_timeout_5",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_067_hanoi_1",
]

# our slicer is built on the assumption that functions are called by value, therefore functions that build on
# call by reference produce broken slices.
CALL_BY_REFERENCE_ISSUES = [
    "slicing/test_evaluation_different_results.py::TestEvaluationDifferentResult::test_dependecy_issue_importance_to_drop_some_items",
    "slicing/test_evaluation_different_results.py::TestEvaluationDifferentResult::test_parameter_by_reference_modified_inside_function",
    "slicing/test_evaluation_different_results.py::TestEvaluationDifferentResult::test_parameter_by_reference_modified_inside_function_1",
    "slicing/test_evaluation_different_results.py::TestEvaluationDifferentResult::test_parameter_by_reference_modified_inside_function_2",
    "slicing/test_evaluation_different_results.py::TestEvaluationDifferentResult::test_parameter_by_reference_modified_inside_function_minimized",
]

# performance heavy tests that need readjusting of the timeouts to succeed
RECURSION_PERFORMANCE_ISSUES = [
    "slicing/test_slicing_recursion_error.py::TestSlicingRecursionError::test_recursion_error_10",
    "slicing/test_slicing_recursion_error.py::TestSlicingRecursionError::test_recursion_error_4",
    "slicing/test_slicing_recursion_error.py::TestSlicingRecursionError::test_recursion_error_5",
    "slicing/test_slicing_recursion_error.py::TestSlicingRecursionError::test_recursion_error_9",
]

# tests failing due to "unsupported" slicing exception
# see ast_tree_tracer/transformer_utils.py::check_for_unsupported_constructs for a complete list
# of unsupported constructs and keywords
NOT_SUPPORTED_CONSTRUCTS = [
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_006_rpn_eval_0",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_007_rpn_eval_1",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_008_rpn_eval_2",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_009_rpn_eval_3",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_010_rpn_eval_4",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_011_rpn_eval_5",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_042_flatten_0",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_043_flatten_1",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_044_flatten_2",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_045_flatten_3",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_046_flatten_4",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_047_flatten_5",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_048_flatten_6",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_203_kheapsort_0",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_204_kheapsort_1",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_205_kheapsort_2",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_206_kheapsort_3",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_2013_correct_1_694_py0",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_2014_correct_1_694_py1",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_2015_correct_1_694_py2",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_2016_correct_1_694_py3",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_2017_correct_1_694_py4",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_2018_correct_1_694_py5",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_2019_correct_1_694_py6",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_2020_correct_1_694_py7",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_2021_correct_1_694_py8",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_2022_correct_1_694_py9",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_2023_correct_1_694_py10",


]

# Tests that fail either due to excessive runtime or above described slicing issue that could be resolved with relevant slicing
TIMEOUTS_QUIX_REFACTORY = [
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_022_longest_common_subsequence_0",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_023_longest_common_subsequence_1",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_025_longest_common_subsequence_3",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_031_longest_common_subsequence_9",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_034_knapsack_2",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_041_knapsack_9",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_059_levenshtein_0",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_061_levenshtein_2",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_062_levenshtein_3",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_063_levenshtein_4",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_068_possible_change_2",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_071_possible_change_5",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_072_possible_change_6",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_073_possible_change_7",
    "benchmark/quixbugs/test_quix_dyn_slicing.py::TestDynSliceQuix::test_dyn_quix_074_possible_change_8",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_0475_correct_1_458_py2",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_0476_correct_1_458_py3",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_0477_correct_1_458_py4",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_0479_correct_1_458_py6",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_0481_correct_1_458_py8",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_2818_correct_1_526_py2",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_2819_correct_1_526_py3",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_2820_correct_1_526_py4",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_2822_correct_1_526_py6",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_2824_correct_1_526_py8",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_3617_correct_1_219_py9",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_3618_correct_1_219_py10",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_5608_correct_1_088_py9",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_5609_correct_1_088_py10",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_6257_correct_1_085_py9",
    "benchmark/refactory/test_refactory.py::TestRefactory::test_dyn_refactory_6258_correct_1_085_py10",
]

def pytest_configure(config):
    config.option.deselect = QUIX_FAILING_OUT_OF_THE_BOX +\
                             RELEVANT_SLICING_ISSUES +\
                             CALL_BY_REFERENCE_ISSUES +\
                             RECURSION_PERFORMANCE_ISSUES + \
                             NOT_SUPPORTED_CONSTRUCTS +\
                             TIMEOUTS_QUIX_REFACTORY
