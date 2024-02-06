import pandas
import glob
import matplotlib.pyplot as plt
from itertools import cycle, islice
#from scipy.stats import normaltest, ttest_ind
from evaluation.eval_utils import read_data, remove_exceptions_and_wrong_results, save_and_show
from helpers.Logger import Logger

log = Logger()


def main():
    df = read_data()
    df = remove_exceptions_and_wrong_results(df)
    df = df[df['benchmark'].isin(['tcas', 'refactory', 'quixbugs'])]
    print(df.columns)
    latex_table(df)
    slice_len(df, 'mean_slice_size_df', 'MeanAll')
    #slice_len(df[df['num_boolops'] > 0], 'mean_slice_size_df_w_boolop_only', 'MeanWithBoolops')
    slice_reduction_boolops(df)
    slice_length_passing_vs_failing(df[(df['benchmark']=='tcas')|(df['benchmark']=='refactory')|(df['benchmark']=='quixbugs')], 'mean_slice_size_test_result_df',)
    # slice_reduction_statistically_relevant(df[(df['benchmark']=='tcas')|(df['benchmark']=='refactory')|(df['benchmark']=='quixbugs')])


def slice_len(df, name, name_latex_command):
    my_colors = list(islice(cycle(['white', 'black', 'gray', 'darkgray', 'lightgray']), None, len(df)))

    # cols = ['benchmark', 'code_len', 'dumb_dyn_slice_len', 'dyn_slice_len', 'pruned_slice_len']
    cols = ['benchmark', 'dumb_dyn_slice_len', 'dyn_slice_len', 'pruned_slice_len', 'relevant_slice_len', 'pruned_relevant_slice_len']

    log.s('\n' + str(df[cols].describe()))

    slice_size_df = df[cols].groupby('benchmark').describe()
    log.s('\n' + str(slice_size_df.to_string()))

    mean_slice_size_df = df[cols].groupby('benchmark').mean()
    mean_slice_size_df = mean_slice_size_df.rename(
        columns={'dumb_dyn_slice_len': 'Executed statements',
                 'dyn_slice_len': 'Dynamic Slice (short circ. eval.)',
                 'pruned_slice_len': 'Pruned Dynamic Slice',
                 'relevant_slice_len': 'Relevant Slice',
                 'pruned_relevant_slice_len': 'Pruned Relevant Slice'
                 })
    ax = mean_slice_size_df.plot(kind='barh', color=my_colors, edgecolor='black', figsize=[4.4, 6], width=0.8)
    ax.set_xlabel('Mean number of statements')
    ax.set_ylabel('')

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1])

    idx = 0
    x_offset = -5
    y_offset = 0.35
    y_multiplier = 0.16
    for key in ['Executed statements', 'Dynamic Slice (short circ. eval.)', 'Pruned Dynamic Slice', 'Relevant Slice', 'Pruned Relevant Slice']:
        for index, value in enumerate(mean_slice_size_df[key]):
            if value > 8 and idx == 1:
                plt.text(value + x_offset, index - y_offset + idx * y_multiplier, "{:.1f}".format(value), color='white', fontsize=9)
            elif value > 8:
                plt.text(value + x_offset, index - y_offset + idx * y_multiplier, "{:.1f}".format(value), color='black', fontsize=9)
            else:
                plt.text(value + 1, index - y_offset + idx * y_multiplier, "{:.1f}".format(value), fontsize=9)
        idx += 1

    save_and_show(name+'.pdf', name, slice_size_df.to_string())

    # data = df[cols]
    # data = data.rename(
    #     columns={'dumb_dyn_slice_len': 'Covered statements', 'dyn_slice_len': 'Dynamic Slice',
    #              'pruned_slice_len': 'Pruned Dynamic Slice'})
    # fig, axs = plt.subplots(5)
    # benchmarks = ['middle', 'quixbugs', 'refactory', 'tcas', 'triangle']
    # for i in range(0,len(benchmarks)):
    #     print(benchmarks[i])
    #     subset_data = data[data['benchmark']==benchmarks[i]]
    #     axs[i] = subset_data.boxplot(ax=axs[i])
    #     axs[i].set_ylabel(benchmarks[i])
    #
    # #boxplot = data.boxplot(by='benchmark')
    # save_and_show('slice_size_boxplot.png', 'slice_size_boxplot', slice_size_df.to_string())

    with open('numbers/'+name+'.tex', 'w') as writer:
        for index, row in mean_slice_size_df.iterrows():
            writer.write('\\newcommand{\\'+index+ name_latex_command + 'Covered}{'+"{:.2f}".format(
                row['Executed statements'])+'\\xspace}\n')
            writer.write('\\newcommand{\\' + index + name_latex_command + 'Dynamic}{' + "{:.2f}".format(
                row['Dynamic Slice (short circ. eval.)']) + '\\xspace}\n')
            writer.write('\\newcommand{\\' + index + name_latex_command + 'Pruned}{' + "{:.2f}".format(
                row['Pruned Dynamic Slice']) + '\\xspace}\n')
            writer.write('\\newcommand{\\' + index + name_latex_command + 'Relevant}{' + "{:.2f}".format(
                row['Relevant Slice']) + '\\xspace}\n')
            writer.write('\\newcommand{\\' + index + name_latex_command + 'PrunedRelevant}{' + "{:.2f}".format(
                row['Pruned Relevant Slice']) + '\\xspace}\n')

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


def slice_reduction_boolops(df):
    df['reduction'] = df['dyn_slice_len'] - df['pruned_slice_len']
    cols = ['benchmark', 'reduction', 'num_boolops']
    # df_grouped = df[cols].groupby('num_boolops').mean()
    # plt.plot(df['num_boolops'], df['reduction'], 'o', color='black')

    # ax = df_grouped.plot(kind='barh')

    #handles, labels = ax.get_legend_handles_labels()
    #ax.legend(handles[::-1], labels[::-1])

    #save_and_show('slice_size_reduction.png', 'slice_size_reduction', df.to_string())

    ax = df[cols].boxplot(by='num_boolops', grid=False, figsize=[4.4, 3.8])
    ax.set_xlabel('Boolean operators')
    ax.set_ylabel('Slice length reduction')
    # plt.gcf().suptitle('')
    # ax.set_title('')
    save_and_show('slice_size_reduction_boxplot.pdf', 'slice_size_reduction', df[cols].describe().to_string())

    cols = ['benchmark', 'reduction', 'num_lines_with_boolops']
    ax = df[cols].boxplot(by='num_lines_with_boolops', grid=False)
    ax.set_xlabel('Lines with Boolean operators')
    ax.set_ylabel('Slice length reduction')
    # plt.gcf().suptitle('')
    # ax.set_title('')
    save_and_show('slice_size_reduction_boxplot_line.pdf', 'slice_size_reduction', df[cols].describe().to_string())


def latex_table(df):
    cols = ['benchmark', 'code_len', 'dumb_dyn_slice_len', 'dyn_slice_len', 'pruned_slice_len', 'relevant_slice_len', 'pruned_relevant_slice_len', 'num_boolops']
    df_grouped = df[cols].groupby('benchmark').mean()
    df_grouped = df_grouped.sort_index(ascending=False)
    df_grouped = df_grouped.rename(
        columns={'dumb_dyn_slice_len': 'Executed statements',
                 'dyn_slice_len': 'Dynamic Slice',
                 'pruned_slice_len': 'Pruned Dynamic Slice',
                 'relevant_slice_len': 'Relevant Slice',
                 'pruned_relevant_slice_len': 'Pruned Relevant Slice',
                 'code_len': 'LOC',
                 'num_boolops': 'Boolean operands' })
    latex_code = df_grouped.T.to_latex(float_format="%.2f", na_rep='-', column_format='lrrr', bold_rows=False)
    latex_code = latex_code.replace('benchmark', '\\textbf{Benchmark}')
    latex_code = latex_code.replace('tcas', '\\textbf{TCAS}')
    # latex_code = latex_code.replace('middle', '\\textbf{Mid}')
    latex_code = latex_code.replace('refactory', '\\textbf{Refactory}')
    latex_code = latex_code.replace('quixbugs', '\\textbf{QuixBugs}')
    # latex_code = latex_code.replace('triangle', '\\textbf{Triangle}')
    with open('latex_tables/mean_loc_exec_slice_size_boolop.tex', 'w') as writer:
        writer.write(latex_code)

def slice_length_passing_vs_failing(df, name):
    my_colors = list(islice(cycle(['white', 'black', 'grey']), None, len(df)))

    df.groupby(['benchmark', 'test_result'])

    cols = ['benchmark', 'test_result', 'dumb_dyn_slice_len', 'dyn_slice_len', 'pruned_slice_len']

    log.s('\n' + str(df[cols].describe()))

    #slice_size_df = df[cols].groupby('benchmark', 'test_result').describe()
    #log.s('\n' + str(slice_size_df.to_string()))

    mean_slice_size_df = df[cols].groupby(['benchmark', 'test_result']).mean()
    mean_slice_size_df = mean_slice_size_df.rename(
        columns={'dumb_dyn_slice_len': 'Executed statements', 'dyn_slice_len': 'Dynamic Slice',
                 'pruned_slice_len': 'Pruned Dynamic Slice'})
    ax = mean_slice_size_df.plot(kind='barh', color=my_colors, edgecolor='black', figsize=[6.4, 3.8], width=0.6)

    idx = 0
    for key in [ 'Executed statements', 'Dynamic Slice', 'Pruned Dynamic Slice']:
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

    save_and_show(name + '.pdf', name, mean_slice_size_df.to_string())


if __name__ == '__main__':
    main()
