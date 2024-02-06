import pandas
import glob
import matplotlib.pyplot as plt
from itertools import cycle, islice
# from scipy.stats import normaltest, ttest_ind
from evaluation.eval_utils import read_data, remove_exceptions_and_wrong_results, save_and_show
from helpers.Logger import Logger

log = Logger()


def main():
    for slice_type in ['dyn', 'rel']:
        df = read_data()
        df = remove_exceptions_and_wrong_results(df, slice_type)
        df = df[df['benchmark'].isin(['tcas', 'refactory', 'quixbugs'])]
        print(df.columns)
        latex_table(df, slice_type)
        # slice_len(df, 'mean_slice_size_df', 'MeanAll', slice_type)
        # slice_len(df[df['num_boolops'] > 0], 'mean_slice_size_df_w_boolop_only', 'MeanWithBoolops')
        # slice_reduction_boolops(df, slice_type)
        # slice_length_passing_vs_failing(df[(df['benchmark']=='tcas')|(df['benchmark']=='refactory')|(df['benchmark']=='quixbugs')], 'mean_slice_size_test_result_df', slice_type)
        # slice_reduction_statistically_relevant(df[(df['benchmark']=='tcas')|(df['benchmark']=='refactory')|(df['benchmark']=='quixbugs')])

    slice_len(df, 'mean_slice_size_df_combined', 'MeanAll', 'subfigures')
    slice_reduction_boolops(df, 'subfigures')
    compare_dynamic_and_relevant_slice()


def compare_dynamic_and_relevant_slice():
    df = read_data()
    df_dyn = remove_exceptions_and_wrong_results(df, 'dyn')
    df_rel = remove_exceptions_and_wrong_results(df, 'rel')
    df = remove_exceptions_and_wrong_results(df, 'dyn')
    df = remove_exceptions_and_wrong_results(df, 'rel')
    df = df[df['benchmark'].isin(['tcas', 'refactory', 'quixbugs'])]
    print(df.columns)
    slice_len(df, 'mean_slice_size_df', 'MeanAll', 'both')
    scatter_plot_compare_slice(df, 'dyn_slice_len', 'relevant_slice_len',
                               "Dynamic slice length", "Relevant slice length",
                               'scatter_dyn_relevant_slice_length')
    scatter_plot_compare_slice(df_dyn, 'dyn_slice_len', 'pruned_slice_len',
                               "Dynamic slice length", "Pruned slice length",
                               'scatter_dyn_pruned_slice_length')
    scatter_plot_compare_slice(df_rel, 'relevant_slice_len', 'pruned_relevant_slice_len',
                               " Relevant slice length", "Pruned  relevant slice length",
                               'scatter_rel_pruned_slice_length')
    # scatter_plot_compare_slice(df)
    table_slice_size_comparison_greater_equal_smaller(df, 'relevant_slice_len', 'dyn_slice_len',
                                                     'size_comparison_dynamic_and_relevant_slice')
    table_slice_size_comparison_greater_equal_smaller(df_dyn, 'pruned_slice_len', 'dyn_slice_len',
                                                      'size_comparison_dynamic_and_pruned_slice')
    table_slice_size_comparison_greater_equal_smaller(df_rel, 'pruned_relevant_slice_len', 'relevant_slice_len',
                                                     'size_comparison_relevant_and_pruned_relevant_slice')



def scatter_plot_compare_slice(df, df_column1, df_column2, text_xlabel, text_ylabel, file_name):
    quix = df[df['benchmark'] == 'quixbugs']
    tcas = df[df['benchmark'] == 'tcas']
    refactory = df[df['benchmark'] == 'refactory']

    fig, ax = plt.subplots(1, figsize=(6, 6))
    ax.scatter(refactory[df_column1], refactory[df_column2], alpha=0.3, marker='s', c="b", s=10, label="Refactory")
    ax.scatter(quix[df_column1], quix[df_column2], alpha=0.3, marker='o', c="r", s=10, label="QuixBugs")
    ax.scatter(tcas[df_column1], tcas[df_column2], alpha=0.3, marker='v', c="black", s=10, label="Tcas")
    ax.set_xlabel(text_xlabel)
    ax.set_ylabel(text_ylabel)

    plt.legend(loc='lower right')
    save_and_show(file_name+'.pdf', file_name, '', dpi=300)


def table_slice_size_comparison_greater_equal_smaller(df, column1, column2, filename):
    df_equal = df[df[column1] == df[column2]]
    df_smaller = df[df[column1] < df[column2]]
    df_greater = df[df[column1] > df[column2]]

    greater = df_greater.groupby(df['benchmark']).count()
    equal = df_equal.groupby(df['benchmark']).count()
    smaller = df_smaller.groupby(df['benchmark']).count()

    df_slice_size_comparison = pandas.concat([greater['benchmark'], equal['benchmark'], smaller['benchmark']], axis=1)
    df_slice_size_comparison.columns = ['Greater', 'Equal', 'Smaller']
    df_slice_size_comparison = df_slice_size_comparison.transpose()
    df_slice_size_comparison = df_slice_size_comparison[['tcas', 'refactory', 'quixbugs']]
    df_slice_size_comparison.columns = ['\\textbf{TCAS}', '\\textbf{Refactory}', '\\textbf{QuixBugs}']

    with open('latex_tables/'+filename+'.tex', 'w', encoding="utf-8") as file:
        file.write(df_slice_size_comparison.to_latex().replace('NaN', '-').replace('.000000', '').replace('benchmark',
                                                                                                          '\\textbf{Benchmark}'))


def slice_len(df, name, name_latex_command, slice_type):
    my_colors = list(islice(cycle(['white', 'black', 'grey']), None, len(df)))

    if slice_type == 'dyn':
        cols = ['benchmark', 'dumb_dyn_slice_len', 'dyn_slice_len', 'pruned_slice_len']
    elif slice_type == 'rel':
        cols = ['benchmark', 'dumb_dyn_slice_len', 'relevant_slice_len', 'pruned_relevant_slice_len']
    elif slice_type == 'both':
        cols = ['benchmark', 'dumb_dyn_slice_len', 'dyn_slice_len', 'relevant_slice_len']
    elif slice_type == 'subfigures':
        cols = ['benchmark', 'dumb_dyn_slice_len', 'dyn_slice_len', 'pruned_slice_len', 'relevant_slice_len',
                'pruned_relevant_slice_len']
        cols_dyn = ['benchmark', 'dumb_dyn_slice_len', 'dyn_slice_len', 'pruned_slice_len']
        cols_rel = ['benchmark', 'dumb_dyn_slice_len', 'relevant_slice_len', 'pruned_relevant_slice_len']

    log.s('\n' + str(df[cols].describe()))

    slice_size_df = df[cols].groupby('benchmark').describe()
    log.s('\n' + str(slice_size_df.to_string()))

    mean_slice_size_df = df[cols].groupby('benchmark').mean()
    column_names = {'dumb_dyn_slice_len': 'Executed statements',
                    'dyn_slice_len': 'Dynamic Slice (short circ. eval.)',
                    'pruned_slice_len': 'Pruned Dynamic Slice',
                    'relevant_slice_len': 'Relevant Slice',
                    'pruned_relevant_slice_len': 'Pruned Relevant Slice'
                    }

    if slice_type == 'subfigures':
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.8), sharex=True, sharey=True)

        mean_slice_size_df = df[cols_dyn].groupby('benchmark').mean()
        mean_slice_size_df = mean_slice_size_df.rename(columns=column_names)
        ax = mean_slice_size_df.plot(kind='barh', color=my_colors, edgecolor='black', width=0.8, ax=ax1)
        ax.set_title('Dynamic Slicing')
        ax.set_xlabel('Mean number of statements')
        ax.set_ylabel('')

        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1])

        keys = add_values_to_bars(ax1, cols_dyn, column_names, mean_slice_size_df)

        mean_slice_size_df = df[cols_rel].groupby('benchmark').mean()
        mean_slice_size_df = mean_slice_size_df.rename(columns=column_names)
        ax = mean_slice_size_df.plot(kind='barh', color=my_colors, edgecolor='black', figsize=[8, 3.8], width=0.8,
                                     ax=ax2)
        ax.set_title('Relevant Slicing')
        ax.set_xlabel('Mean number of statements')
        ax.set_ylabel('')

        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1])

        keys = add_values_to_bars(ax2, cols_rel, column_names, mean_slice_size_df)

    else:
        mean_slice_size_df = mean_slice_size_df.rename(
            columns=column_names)
        ax = mean_slice_size_df.plot(kind='barh', color=my_colors, edgecolor='black', figsize=[4.4, 3.8], width=0.8)
        ax.set_xlabel('Mean number of statements')
        ax.set_ylabel('')

        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1])

        keys = add_values_to_bars(ax, cols, column_names, mean_slice_size_df)

    save_and_show(name + '_' + slice_type + '.pdf', name + '_' + slice_type, slice_size_df.to_string())

    number_names = {'Executed statements': 'Covered',
                    'Dynamic Slice (short circ. eval.)': 'Dynamic',
                    'Pruned Dynamic Slice': 'DynamicPruned',
                    'Relevant Slice': 'Relevant',
                    'Pruned Relevant Slice': 'RelevantPruned'
                    }

    with open('numbers/' + name + '_' + slice_type + '.tex', 'w') as writer:
        for index, row in mean_slice_size_df.iterrows():
            for key in keys:
                writer.write(
                    '\\newcommand{\\' + index + name_latex_command + number_names[key] + '}{' + "{:.2f}".format(
                        row[key]) + '\\xspace}\n')


def add_values_to_bars(ax, cols, column_names, mean_slice_size_df):
    keys = [column_names[x] for x in cols[1:]]
    idx = 0
    for key in keys:
        for index, value in enumerate(mean_slice_size_df[key]):
            if value > 8 and idx == 1:
                ax.text(value - 4.9, index - 0.33 + idx * 0.25, "{:.1f}".format(value), color='white', fontsize=9)
            elif value > 8:
                ax.text(value - 4.9, index - 0.33 + idx * 0.25, "{:.1f}".format(value), color='black', fontsize=9)
            else:
                ax.text(value + 1, index - 0.33 + idx * 0.25, "{:.1f}".format(value), fontsize=9)
        idx += 1
    return keys


# def slice_reduction_statistically_relevant(df):
#     # Assuptions for Students's T-test:
#     # 1) Check for Gaussian distribution
#     # 2) Observations in each sample have the same variance.
#     # 3) Observations in each sample are independent and identically distributed (iid).
#     benchmarks=['tcas', 'refactory', 'quixbugs']
#     slice_types = ['dyn_slice_len', 'pruned_slice_len']
#     for benchmark in benchmarks:
#         df_sub = df[df['benchmark'] == benchmark]
#         for type in slice_types:
#             stat, p = normaltest(df_sub[type])
#             print(benchmark+' '+type+':'+'stat=%.3f, p=%.3f' % (stat, p))
#             if p > 0.05:
#                 print('Probably Gaussian')
#             else:
#                 print('Probably not Gaussian')
#
#         stat, p = ttest_ind(df_sub['dyn_slice_len'], df_sub['pruned_slice_len'])
#         print(benchmark+': '+'stat=%.3f, p=%.3f' % (stat, p))
#         if p > 0.05:
#             print('Probably the same distribution')
#         else:
#             print('Probably different distributions')


def slice_reduction_boolops(df, slice_type):
    if slice_type == 'dyn':
        df['reduction'] = df['dyn_slice_len'] - df['pruned_slice_len']
    if slice_type == 'rel':
        df['reduction'] = df['relevant_slice_len'] - df['pruned_relevant_slice_len']
    elif slice_type == 'subfigures':
        df['reduction_dyn'] = df['dyn_slice_len'] - df['pruned_slice_len']
        df['reduction_rel'] = df['relevant_slice_len'] - df['pruned_relevant_slice_len']

    if slice_type == 'subfigures':
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.8), sharex=True, sharey=True)
        cols_dyn = ['benchmark', 'reduction_dyn', 'num_boolops']
        cols_rel = ['benchmark', 'reduction_rel', 'num_boolops']
        ax = df[cols_dyn].boxplot(by='num_boolops', grid=False, ax=ax1)
        ax.set_title('Pruned Dynamic Slicing')
        ax.set_xlabel('Boolean operators')
        ax.set_ylabel('Slice length reduction')
        ax = df[cols_rel].boxplot(by='num_boolops', grid=False, ax=ax2)
        ax.set_title('Pruned Relevant Slicing')
        ax.set_xlabel('Boolean operators')
        save_and_show('slice_size_reduction_boxplot_' + slice_type + '.pdf', 'slice_size_reduction_' + slice_type,
                      'Dynamic: \n' + df[cols_dyn].describe().to_string() + '\n\n Relevant: \n' + df[
                          cols_rel].describe().to_string())

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.8), sharex=True, sharey=True)
        cols_dyn = ['benchmark', 'reduction_dyn', 'num_lines_with_boolops']
        cols_rel = ['benchmark', 'reduction_rel', 'num_lines_with_boolops']
        ax = df[cols_dyn].boxplot(by='num_lines_with_boolops', grid=False, ax=ax1)
        ax.set_title('Pruned Dynamic Slicing')
        ax.set_xlabel('Lines with Boolean operators')
        ax.set_ylabel('Slice length reduction')
        ax = df[cols_rel].boxplot(by='num_lines_with_boolops', grid=False, ax=ax2)
        ax.set_title('Pruned Relevant Slicing')
        ax.set_xlabel('Lines with Boolean operators')

        save_and_show('slice_size_reduction_boxplot_line_' + slice_type + '.pdf', 'slice_size_reduction_' + slice_type,
                      'Dynamic: \n' + df[cols_dyn].describe().to_string() + '\n\n Relevant: \n' + df[
                          cols_rel].describe().to_string())

    else:
        cols = ['benchmark', 'reduction', 'num_boolops']
        # df_grouped = df[cols].groupby('num_boolops').mean()
        # plt.plot(df['num_boolops'], df['reduction'], 'o', color='black')

        # ax = df_grouped.plot(kind='barh')

        # handles, labels = ax.get_legend_handles_labels()
        # ax.legend(handles[::-1], labels[::-1])

        # save_and_show('slice_size_reduction.png', 'slice_size_reduction', df.to_string())

        ax = df[cols].boxplot(by='num_boolops', grid=False, figsize=[4.4, 3.8])
        ax.set_xlabel('Boolean operators')
        ax.set_ylabel('Slice length reduction')
        # plt.gcf().suptitle('')
        # ax.set_title('')
        save_and_show('slice_size_reduction_boxplot_' + slice_type + '.pdf', 'slice_size_reduction_' + slice_type,
                      df[cols].describe().to_string())

        cols = ['benchmark', 'reduction', 'num_lines_with_boolops']
        ax = df[cols].boxplot(by='num_lines_with_boolops', grid=False)
        ax.set_xlabel('Lines with Boolean operators')
        ax.set_ylabel('Slice length reduction')
        # plt.gcf().suptitle('')
        # ax.set_title('')
        save_and_show('slice_size_reduction_boxplot_line_' + slice_type + '.pdf', 'slice_size_reduction_' + slice_type,
                      df[cols].describe().to_string())


def latex_table(df, slice_type):
    if slice_type == 'dyn':
        cols = ['benchmark', 'code_len', 'dumb_dyn_slice_len', 'dyn_slice_len', 'pruned_slice_len', 'num_boolops']
    elif slice_type == 'rel':
        cols = ['benchmark', 'code_len', 'dumb_dyn_slice_len', 'relevant_slice_len', 'pruned_relevant_slice_len',
                'num_boolops']

    column_names = {'dumb_dyn_slice_len': 'Executed statements',
                    'dyn_slice_len': 'Dynamic Slice',
                    'pruned_slice_len': 'Pruned Dynamic Slice',
                    'relevant_slice_len': 'Relevant Slice',
                    'pruned_relevant_slice_len': 'Pruned Relevant Slice',
                    'code_len': 'LOC',
                    'num_boolops': 'Boolean operands'
                    }
    df_grouped = df[cols].groupby('benchmark').mean()
    df_grouped = df_grouped.sort_index(ascending=False)
    df_grouped = df_grouped.rename(columns=column_names)
    latex_code = df_grouped.T.to_latex(float_format="%.2f", na_rep='-', column_format='lrrr', bold_rows=False)
    latex_code = latex_code.replace('benchmark', '\\textbf{Benchmark}')
    latex_code = latex_code.replace('tcas', '\\textbf{TCAS}')
    # latex_code = latex_code.replace('middle', '\\textbf{Mid}')
    latex_code = latex_code.replace('refactory', '\\textbf{Refactory}')
    latex_code = latex_code.replace('quixbugs', '\\textbf{QuixBugs}')
    # latex_code = latex_code.replace('triangle', '\\textbf{Triangle}')
    with open('latex_tables/mean_loc_exec_slice_size_boolop_' + slice_type + '.tex', 'w') as writer:
        writer.write(latex_code)


def slice_length_passing_vs_failing(df, name, slice_type):
    my_colors = list(islice(cycle(['white', 'black', 'grey']), None, len(df)))

    df.groupby(['benchmark', 'test_result'])

    if slice_type == 'dyn':
        cols = ['benchmark', 'test_result', 'dumb_dyn_slice_len', 'dyn_slice_len', 'pruned_slice_len']
    elif slice_type == 'dyn':
        cols = ['benchmark', 'test_result', 'dumb_dyn_slice_len', 'relevant_slice_len', 'pruned_relevant_slice_len']

    log.s('\n' + str(df[cols].describe()))

    # slice_size_df = df[cols].groupby('benchmark', 'test_result').describe()
    # log.s('\n' + str(slice_size_df.to_string()))

    column_names = {'dumb_dyn_slice_len': 'Executed statements',
                    'dyn_slice_len': 'Dynamic Slice',
                    'pruned_slice_len': 'Pruned Dynamic Slice',
                    'relevant_slice_len': 'Relevant Slice',
                    'pruned_relevant_slice_len': 'Pruned Relevant Slice',
                    }

    mean_slice_size_df = df[cols].groupby(['benchmark', 'test_result']).mean()
    mean_slice_size_df = mean_slice_size_df.rename(columns=column_names)
    ax = mean_slice_size_df.plot(kind='barh', color=my_colors, edgecolor='black', figsize=[6.4, 3.8], width=0.6)

    keys = [column_names[x] for x in cols[1:]]

    idx = 0
    for key in keys:
        for index, value in enumerate(mean_slice_size_df[key]):
            if (value > 60):
                plt.text(value - 3, index - 0.28 + idx * 0.2, "{:.1f}".format(value), color='black', fontsize=6)
            else:
                plt.text(value + 2, index - 0.28 + idx * 0.2, "{:.1f}".format(value), fontsize=6)
        idx += 1

    ax.set_xlabel('Mean number of statements')
    ax.set_ylabel('')

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1])

    save_and_show(name + '_' + slice_type + '.pdf', name + '_' + slice_type, mean_slice_size_df.to_string())


if __name__ == '__main__':
    main()
