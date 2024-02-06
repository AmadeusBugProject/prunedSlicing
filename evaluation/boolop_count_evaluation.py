import pandas
import glob
from itertools import cycle, islice
import matplotlib.pyplot as plt

from evaluation.eval_utils import read_data, remove_exceptions_and_wrong_results, save_and_show
from helpers.Logger import Logger

log = Logger()


def main():
    slice_type = 'rel'
    # slice_type = 'dyn'
    df = read_data()
    # df = remove_exceptions_and_wrong_results(df, slice_type)
    df = df[df['benchmark'].isin(['tcas', 'refactory', 'quixbugs'])]
    # boolops_count(df, slice_type)
    boolops_count_op_subfigures(df)


def boolops_count_op_subfigures(df):
    my_colors = list(islice(cycle(['black', 'grey', 'white']), None, len(df)))
    df_dyn = remove_exceptions_and_wrong_results(df, 'dyn')
    df_rel = remove_exceptions_and_wrong_results(df, 'rel')

    boolops_cols_dyn = ['benchmark', 'num_boolops_dyn_sliced', 'num_boolops_pruned_sliced']
    boolops_cols_rel = ['benchmark', 'num_boolops_relevant_sliced', 'num_boolops_pruned_relevant_sliced']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.8), sharex=True, sharey=True)

    num_boolops_df_dyn = mean_number_of_boolean_operators(boolops_cols_dyn, df_dyn, my_colors, ax=ax1, title='Dynamic Slicing')
    num_boolops_df_rel = mean_number_of_boolean_operators(boolops_cols_rel, df_rel, my_colors, ax=ax2, title='Relevant Slicing')

    save_and_show('mean_num_boolops_subfigures.pdf', 'mean_num_boolops_subfigures',
                  'Dynamic:\n' + num_boolops_df_dyn.to_string() + '\n\nRelevant:\n' + num_boolops_df_rel.to_string())

    ######

    boolops_line_cols_dyn = ['benchmark', 'num_lines_with_boolops_dyn_sliced', 'num_lines_with_boolops_pruned_sliced']
    boolops_line_cols_rel = ['benchmark', 'num_lines_with_boolops_relevant_sliced',
                             'num_boolops_pruned_relevant_sliced']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.8), sharex=True, sharey=True)

    num_lines_w_boolops_df_dyn = mean_lines_w_boolops_sub(boolops_line_cols_dyn, df_dyn, my_colors, ax=ax1, title='Dynamic Slicing')
    num_lines_w_boolops_df_rel = mean_lines_w_boolops_sub(boolops_line_cols_rel, df_rel, my_colors, ax=ax2, title='Relevant Slicing')

    save_and_show('mean_lines_w_boolops_subfigures.pdf', 'mean_lines_w_boolops_subfigures',
                  'Dynamic:\n' + num_lines_w_boolops_df_dyn.to_string()  + '\n\nRelevant:\n' + num_lines_w_boolops_df_rel.to_string() )


def mean_lines_w_boolops_sub(boolops_line_cols, df, my_colors, ax, title):
    num_lines_w_boolops_df = df[boolops_line_cols].groupby('benchmark').describe()
    log.s('\n' + str(num_lines_w_boolops_df.to_string()))
    column_names = {'num_lines_with_boolops': 'Source code',
                    'num_lines_with_boolops_dyn_sliced': 'Dynamic Slice (short circuit)',
                    'num_lines_with_boolops_pruned_sliced': 'Pruned Dynamic Slice',
                    'num_lines_with_boolops_relevant_sliced': 'Relevant Slice',
                    'num_boolops_pruned_relevant_sliced': 'Pruned Relevant Slice'
                    }
    mean_lines_w_boolops = df[boolops_line_cols].groupby('benchmark').mean()
    mean_lines_w_boolops = mean_lines_w_boolops.rename(columns=column_names)
    ax = mean_lines_w_boolops.plot(kind='barh', color=my_colors, edgecolor='black', ax=ax)
    keys = [column_names[x] for x in boolops_line_cols[1:]]
    for index, value in enumerate(mean_lines_w_boolops[keys[1]]):
        ax.text(value + 0.05, index + 0.08, "{:.2f}".format(value))
    for index, value in enumerate(mean_lines_w_boolops[keys[0]]):
        if value > 2:
            ax.text(value - 0.2, index - 0.2, "{:.2f}".format(value), color='white')
        else:
            ax.text(value + 0.05, index - 0.2, "{:.2f}".format(value))
    ax.set_title(title)
    ax.set_xlabel('Mean number of Lines with Boolean operators')
    ax.set_ylabel('')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='lower right')
    return num_lines_w_boolops_df


def mean_number_of_boolean_operators(boolops_cols, df, my_colors, ax, title):
    num_boolops_df = df[boolops_cols].groupby('benchmark').describe()
    log.s('\n' + str(num_boolops_df.to_string()))
    column_names = {'num_boolops': 'Source code',
                    'num_boolops_dyn_sliced': 'Dynamic Slice (short circ. eval.)',
                    'num_boolops_pruned_sliced': 'Pruned Dynamic Slice',
                    'num_boolops_relevant_sliced': 'Relevant Slice',
                    'num_boolops_pruned_relevant_sliced': 'Pruned Relevant Slice'
                    }
    mean_boolops = df[boolops_cols].groupby('benchmark').mean()
    mean_boolops = mean_boolops.rename(columns=column_names)
    ax = mean_boolops.plot(kind='barh', color=my_colors, edgecolor='black', ax=ax, width=0.7)
    keys = [column_names[x] for x in boolops_cols[1:]]
    x_offset = 0.08
    y_offset = 0.25
    y_multiplier = 0.38
    idx = 0
    for key in keys:
        for index, value in enumerate(mean_boolops[key]):
            if value > 4:
                ax.text(value - 0.4, index - y_offset + idx * y_multiplier, "{:.1f}".format(value), fontsize=9,
                         color='white')
            else:
                ax.text(value + x_offset, index - y_offset + idx * y_multiplier, "{:.1f}".format(value), fontsize=9)
        idx += 1

    ax.set_title(title)
    ax.set_xlabel('Mean number of Boolean operators')
    ax.set_ylabel('')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1])
    return num_boolops_df


def boolops_count(df, slice_type):
    my_colors = list(islice(cycle(['black', 'grey', 'white']), None, len(df)))

    if slice_type == 'dyn':
        boolops_cols = ['benchmark', 'num_boolops_dyn_sliced', 'num_boolops_pruned_sliced']
    elif slice_type == 'rel':
        boolops_cols = ['benchmark', 'num_boolops_relevant_sliced', 'num_boolops_pruned_relevant_sliced']

    num_boolops_df = df[boolops_cols].groupby('benchmark').describe()
    log.s('\n' + str(num_boolops_df.to_string()))

    column_names = {'num_boolops': 'Source code',
                 'num_boolops_dyn_sliced': 'Dynamic Slice (short circ. eval.)',
                 'num_boolops_pruned_sliced': 'Pruned Dynamic Slice',
                 'num_boolops_relevant_sliced': 'Relevant Slice',
                 'num_boolops_pruned_relevant_sliced': 'Pruned Relevant Slice'
                 }
    mean_boolops = df[boolops_cols].groupby('benchmark').mean()
    mean_boolops = mean_boolops.rename(columns=column_names)
    ax = mean_boolops.plot(kind='barh', color=my_colors, edgecolor='black', figsize=[4.4, 3.8], width=0.7)

    keys = [column_names[x] for x in boolops_cols[1:]]

    # for index, value in enumerate(mean_boolops[keys[0]]):
    #     if index == 2:
    #         plt.text(value * 0.49 + 0.05, index + 0.08, "{:.2f}".format(value))
    #     else:
    #         plt.text(value + 0.05, index + 0.08, "{:.2f}".format(value))
    # for index, value in enumerate(mean_boolops[keys[1]]):
    #     if(value > 4):
    #         plt.text(value-0.05, index - 0.25, "{:.2f}".format(value), color='white')
    #     else:
    #         plt.text(value+0.05, index - 0.25, "{:.2f}".format(value))

    x_offset = 0.08
    y_offset = 0.25
    y_multiplier = 0.38
    idx = 0
    for key in keys:
        for index, value in enumerate(mean_boolops[key]):
            if value > 4:
                plt.text(value - 0.4, index - y_offset + idx * y_multiplier, "{:.1f}".format(value), fontsize=9, color='white')
            else:
                plt.text(value + x_offset, index - y_offset + idx * y_multiplier, "{:.1f}".format(value), fontsize=9)
        idx += 1

    ax.set_xlabel('Mean number of Boolean operators')
    ax.set_ylabel('')

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1])

    save_and_show('mean_num_boolops_' + slice_type + '.pdf', 'mean_num_boolops_' + slice_type, num_boolops_df.to_string())

    if slice_type == 'dyn':
        boolops_cols = ['benchmark', 'num_boolops', 'num_boolops_dyn_sliced', 'num_boolops_pruned_sliced']
    elif slice_type == 'rel':
        boolops_cols = ['benchmark', 'num_boolops', 'num_boolops_relevant_sliced', 'num_boolops_pruned_relevant_sliced']

    column_names = {'num_boolops': 'Covered',
     'num_boolops_dyn_sliced': 'Dynamic Slice (short circuit eval.)',
     'num_boolops_pruned_sliced': 'Pruned Dynamic Slice',
     'num_boolops_relevant_sliced': 'Relevant Slice',
     'num_boolops_pruned_relevant_sliced': 'Pruned Relevant Slice'
     }
    num_boolops_df = df[boolops_cols].groupby('benchmark').describe()
    mean_boolops = df[boolops_cols].groupby('benchmark').mean()
    mean_boolops = mean_boolops.rename(columns=column_names)
    keys = [column_names[x] for x in boolops_cols[1:]]

    number_keys = {'Covered': 'Covered',
     'Dynamic Slice (short circuit eval.)': 'Dynamic',
     'Pruned Dynamic Slice': 'DynamicPruned',
     'Relevant Slice': 'Relevant',
     'Pruned Relevant Slice': 'RelevantPruned'
     }

    with open('numbers/boolop_reduction_' + slice_type + '.tex', 'w') as writer:
        for index, row in mean_boolops.iterrows():
            for key in keys:
                writer.write('\\newcommand{\\'+index+ 'MeanBoolops' + number_keys[key] + '}{'+"{:.2f}".format(
                    row[key])+'\\xspace}\n')

    if slice_type == 'dyn':
        boolops_line_cols = ['benchmark', 'num_lines_with_boolops_dyn_sliced', 'num_lines_with_boolops_pruned_sliced']
    elif slice_type == 'rel':
        boolops_line_cols = ['benchmark', 'num_lines_with_boolops_relevant_sliced', 'num_boolops_pruned_relevant_sliced']

    num_lines_w_boolops_df = df[boolops_line_cols].groupby('benchmark').describe()
    log.s('\n' + str(num_lines_w_boolops_df.to_string()))

    column_names = {'num_lines_with_boolops': 'Source code',
                 'num_lines_with_boolops_dyn_sliced': 'Dynamic Slice (short circuit eval.)',
                 'num_lines_with_boolops_pruned_sliced': 'Pruned Dynamic Slice',
                 'num_lines_with_boolops_relevant_sliced': 'Relevant Slice',
                 'num_boolops_pruned_relevant_sliced': 'Pruned Relevant Slice'
                 }
    mean_lines_w_boolops = df[boolops_line_cols].groupby('benchmark').mean()
    mean_lines_w_boolops = mean_lines_w_boolops.rename(columns=column_names)
    ax = mean_lines_w_boolops.plot(kind='barh', color=my_colors, edgecolor='black')

    keys = [column_names[x] for x in boolops_line_cols[1:]]

    for index, value in enumerate(mean_lines_w_boolops[keys[1]]):
        plt.text(value+0.05, index+0.08, "{:.2f}".format(value))
    for index, value in enumerate(mean_lines_w_boolops[keys[0]]):
        if(value > 2):
            plt.text(value-0.2, index - 0.2, "{:.2f}".format(value), color='white')
        else:
            plt.text(value+0.05, index - 0.2, "{:.2f}".format(value))

    ax.set_xlabel('Mean number of Lines with Boolean operators')
    ax.set_ylabel('')

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='lower right')

    save_and_show('mean_lines_w_boolops_' + slice_type + '.pdf', 'mean_lines_w_boolops_' + slice_type, num_lines_w_boolops_df.to_string())


if __name__ == '__main__':
    main()
