import pandas
import glob
import re
from matplotlib import pyplot as plt
from evaluation.eval_utils import read_data, save_and_show
from helpers.Logger import Logger

log = Logger()


def main():
    # df = read_data()
    # df = df.apply(make_status, axis=1)
    # df.to_csv('data/test_status_overview.csv.zip', compression='zip')

    df = pandas.read_csv('data/test_status_overview.csv.zip', compression='zip')
    df.drop(['Unnamed: 0'], axis=1, inplace=True)

    status_plot(df[(df['benchmark']=='tcas')|(df['benchmark']=='refactory')|(df['benchmark']=='quixbugs')])
    exception_overview_csv(df[(df['benchmark']=='tcas')|(df['benchmark']=='refactory')|(df['benchmark']=='quixbugs')])


test_status = 'test_status'
def make_status(df):
    if df['stage'] == 'finished':
        if df['sliced_result_equal_to_bare']:
            df[test_status] = 'Successful'
        else:
            df[test_status] = 'Sliced code result differs from original'
    elif df['stage'] == 'bare execution':
        df[test_status] = 'Not executable'
    elif "<class 'timeout_decorator.timeout_decorator.TimeoutError'>()" in df['exception'] and \
            df['stage'] == 'run sliced':
        df[test_status] = 'Timeout during sliced code execution'
    elif "<class 'timeout_decorator.timeout_decorator.TimeoutError'>()" in df['exception']:
        df[test_status] = 'General Timeout'
    elif "<class 'slicing.slicing_exceptions.SlicingException'>" in df['exception'] and \
            "not supported" in df['exception']:
        df[test_status] = 'Not supported'
    elif df['exception']:
        df[test_status] = 'Other Exception'
    return df


def status_plot(df):
    ax = df[test_status].value_counts().plot(kind='pie')
    plt.legend()
    save_and_show('test_case_status.png', 'test_case_status', df[test_status].value_counts().to_string())

    status_counts_df = df[['benchmark', test_status]].groupby('benchmark')[test_status].value_counts().unstack(1)
    generate_latex_code(status_counts_df)
    status_counts_df = status_counts_df.div(status_counts_df.sum(axis=1), axis=0).fillna(0)
    ax = status_counts_df.plot(kind='barh', stacked=True)
    save_and_show('test_case_status_normalized_per_benchmark.png', 'test_case_status', df[test_status].value_counts().to_string())

def generate_latex_code(df):
    df_latex = df.T.sort_values(by='refactory', ascending=False)
    total = df_latex.sum(axis=1)
    df_latex['Total'] = total
    df_latex.loc['midrule  Total'] = df_latex.sum()
    latex_code = df_latex.to_latex(float_format="%.0f", na_rep='-', column_format='lrrrr', bold_rows=False)
    latex_code = latex_code.replace('Sliced code result differs from original', 'Different result')
    latex_code = latex_code.replace('Timeout during sliced code execution', 'Timeout sliced code')
    latex_code = latex_code.replace('midrule  Total', '\midrule\nTotal')
    m = re.search(r"test\\_status( *&*)*\\\\", latex_code)
    latex_code = latex_code.replace(m.group(0), '')
    latex_code = latex_code.replace('benchmark', '\\textbf{Benchmark}')
    latex_code = latex_code.replace('tcas', '\\textbf{TCAS}')
    # latex_code = latex_code.replace('middle', '\\textbf{Mid}')
    latex_code = latex_code.replace('refactory', '\\textbf{Refactory}')
    latex_code = latex_code.replace('quixbugs', '\\textbf{Quix}')
    # latex_code = latex_code.replace('triangle', '\\textbf{Triangle}')
    latex_code = latex_code.replace('Total', '\\textbf{Total}')
    with open('latex_tables/exceptions.tex', 'w') as writer:
        writer.write(latex_code)

    numbers = dict()
    sum = total.sum()
    numbers['percentSuccessfulSlicing'] = total['Successful']/sum*100.0
    numbers['percentGeneralTimeout'] = total['General Timeout']/sum*100.0
    numbers['percentDifferentResult'] = total['Sliced code result differs from original']/sum*100.0
    numbers['percentTimeoutSlicing'] = total['Timeout during sliced code execution'] / sum * 100.0
    numbers['percentNotExecutable'] = total['Not executable'] / sum * 100.0
    numbers['percentNotSupported'] = total['Not supported'] / sum * 100.0
    numbers['percentOtherException'] = total['Other Exception'] / sum * 100.0
    with open('numbers/exceptions.tex', 'w') as writer:
        for key in numbers:
            writer.write('\\newcommand{\\'+key+'}{'+"{:.2f}".format(numbers[key])+'\\,\\%\\xspace}\n')


def exception_overview_csv(df):
    log.s('number of tests = ' + str(df.shape))

    exceptions_df = df[~df['exception'].isnull()]
    log.s('number of exceptions = ' + str(exceptions_df.shape))
    exception_series = df['exception'].value_counts()
    exception_series.to_csv('data/exception_count.csv')
    exceptions_df.to_csv('data/all_exceptions.csv')

    filtered_exceptions_df = exceptions_df[~(exceptions_df['exception'].str.contains("<class 'timeout_decorator.timeout_decorator.TimeoutError'>()", regex=False) |
                                            exceptions_df['exception'].str.contains("<class 'slicing.slicing_exceptions.SlicingException'>") &
                                            exceptions_df['exception'].str.contains("not supported"))]
    filtered_exceptions_df.to_csv('data/filtered_exceptions.csv')

    no_exceptions_df = df[df['exception'].isnull()]
    log.s('tests with no exceptions = ' + str(no_exceptions_df.shape))

    slice_result_other_than_bare_result_df = no_exceptions_df[no_exceptions_df['sliced_result_equal_to_bare']==False]
    log.s('number of slices producing different result than original = ' + str(slice_result_other_than_bare_result_df.shape))
    slice_result_other_than_bare_result_df.to_csv('data/slice_other_result_than_original.csv')

    same_result_df = no_exceptions_df[no_exceptions_df['sliced_result_equal_to_bare']]
    log.s('number of slices producing same result = ' + str(same_result_df.shape))

    failing_tests_df = same_result_df[same_result_df['test_result']==False]
    log.s('number of failing test cases = ' + str(failing_tests_df.shape))

    filtered_exceptions_df = exceptions_df[~(
                exceptions_df['exception'].str.contains("<class 'timeout_decorator.timeout_decorator.TimeoutError'>()", regex=False) |
                exceptions_df['stage'].str.contains("bare execution", regex=False) |
                (exceptions_df['exception'].str.contains("<class 'slicing.slicing_exceptions.SlicingException'>", regex=False) &
                    (exceptions_df['exception'].str.contains("not supported") |
                     exceptions_df['exception'].str.contains("Trace length too big, quitting")))
    )]
    filtered_exceptions_df.to_csv('data/reduced_filtered_exceptions.csv')


if __name__ == '__main__':
    main()
