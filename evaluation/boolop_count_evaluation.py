import pandas
import glob
from itertools import cycle, islice
import matplotlib.pyplot as plt

from evaluation.eval_utils import read_data, remove_exceptions_and_wrong_results, save_and_show
from helpers.Logger import Logger

log = Logger()



def main():
    df = read_data()
    df = remove_exceptions_and_wrong_results(df)
    df = df[df['benchmark'].isin(['tcas', 'refactory', 'quixbugs'])]
    boolops_count(df)


def boolops_count(df):
    my_colors = list(islice(cycle(['black', 'grey', 'white']), None, len(df)))

    boolops_cols = ['benchmark', 'num_boolops_dyn_sliced', 'num_boolops_pruned_sliced']
    num_boolops_df = df[boolops_cols].groupby('benchmark').describe()
    log.s('\n' + str(num_boolops_df.to_string()))

    mean_boolops = df[boolops_cols].groupby('benchmark').mean()
    mean_boolops = mean_boolops.rename(
        columns={'num_boolops': 'Source code', 'num_boolops_dyn_sliced': 'Dynamic Slice (short circ. eval.)',
                 'num_boolops_pruned_sliced': 'Pruned Dynamic Slice'})
    ax = mean_boolops.plot(kind='barh', color=my_colors, edgecolor='black', figsize=[4.4, 3.8], width=0.7)

    for index, value in enumerate(mean_boolops['Pruned Dynamic Slice']):
        plt.text(value+0.05, index+0.08, "{:.2f}".format(value))
    for index, value in enumerate(mean_boolops['Dynamic Slice (short circ. eval.)']):
        if(value > 4):
            plt.text(value-0.5, index - 0.25, "{:.2f}".format(value), color='white')
        else:
            plt.text(value+0.05, index - 0.25, "{:.2f}".format(value))

    ax.set_xlabel('Mean number of Boolean operators')
    ax.set_ylabel('')

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1])

    save_and_show('mean_num_boolops.png', 'mean_num_boolops', num_boolops_df.to_string())

    boolops_cols = ['benchmark', 'num_boolops', 'num_boolops_dyn_sliced', 'num_boolops_pruned_sliced']
    num_boolops_df = df[boolops_cols].groupby('benchmark').describe()
    mean_boolops = df[boolops_cols].groupby('benchmark').mean()
    mean_boolops = mean_boolops.rename(
        columns={'num_boolops': 'Covered', 'num_boolops_dyn_sliced': 'Dynamic Slice (short circuit eval.)',
                 'num_boolops_pruned_sliced': 'Pruned Dynamic Slice'})
    with open('numbers/boolop_reduction.tex', 'w') as writer:
        for index, row in mean_boolops.iterrows():
            writer.write('\\newcommand{\\'+index+ 'MeanBoolopsCovered}{'+"{:.2f}".format(
                row['Covered'])+'\\xspace}\n')
            writer.write('\\newcommand{\\' + index + 'MeanBoolopsDynamic}{' + "{:.2f}".format(
                row['Dynamic Slice (short circuit eval.)']) + '\\xspace}\n')
            writer.write('\\newcommand{\\' + index + 'MeanBoolopsPruned}{' + "{:.2f}".format(
                row['Pruned Dynamic Slice']) + '\\xspace}\n')



    # boolops_line_cols = ['benchmark', 'num_lines_with_boolops', 'num_lines_with_boolops_dyn_sliced', 'num_lines_with_boolops_pruned_sliced']
    boolops_line_cols = ['benchmark', 'num_lines_with_boolops_dyn_sliced',
                         'num_lines_with_boolops_pruned_sliced']

    num_lines_w_boolops_df = df[boolops_line_cols].groupby('benchmark').describe()
    log.s('\n' + str(num_lines_w_boolops_df.to_string()))

    mean_lines_w_boolops = df[boolops_line_cols].groupby('benchmark').mean()
    mean_lines_w_boolops = mean_lines_w_boolops.rename(
        columns={'num_lines_with_boolops': 'Source code', 'num_lines_with_boolops_dyn_sliced': 'Dynamic Slice (short circuit eval.)',
                 'num_lines_with_boolops_pruned_sliced': 'Pruned Dynamic Slice'})
    ax = mean_lines_w_boolops.plot(kind='barh', color=my_colors, edgecolor='black')

    for index, value in enumerate(mean_lines_w_boolops['Pruned Dynamic Slice']):
        plt.text(value+0.05, index+0.08, "{:.2f}".format(value))
    for index, value in enumerate(mean_lines_w_boolops['Dynamic Slice (short circuit eval.)']):
        if(value > 2):
            plt.text(value-0.2, index - 0.2, "{:.2f}".format(value), color='white')
        else:
            plt.text(value+0.05, index - 0.2, "{:.2f}".format(value))

    ax.set_xlabel('Mean number of Lines with Boolean operators')
    ax.set_ylabel('')

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='lower right')

    save_and_show('mean_lines_w_boolops.png', 'mean_lines_w_boolops', num_lines_w_boolops_df.to_string())


if __name__ == '__main__':
    main()
