import pandas
import glob

from evaluation.eval_utils import read_data, remove_exceptions_and_wrong_results, save_and_show
from helpers.Logger import Logger
from matplotlib import pyplot as plt
from itertools import cycle, islice

log = Logger()


def main():
    df = pandas.DataFrame()

    for csv_file in glob.glob('boolop_counter/**/*.csv', recursive=True):
        name = csv_file.split('/')[-1].replace('.csv', '')
        csv_df = pandas.read_csv(csv_file)
        csv_df['name'] = name
        df = pandas.concat([df, csv_df], ignore_index=True)

    boolops_count(df)


def boolops_count(df):
    my_colors = list(islice(cycle(['darkgray']), None, len(df)))
    cols = ['name', 'file_loc', 'num_boolops', 'num_lines_with_boolops']
    desired = ['tcas', 'quixbugs', 'refactory']

    df['name'] = df['name'].str.replace('boolop_counter\\\\', '')
    df['name']=df['name'].str.replace('benchmark_stats\\\\','')
    df['name'] = df['name'].str.replace('_stats', '')
    df = df[df['name']!='middle']
    df = df[df['name']!='triangle']

    sum_projects_df = df[cols].groupby('name').sum()

    sum_projects_df['boolops_per_loc'] = sum_projects_df['num_boolops']/sum_projects_df['file_loc']
    sum_projects_df['lines_with_boolops_per_loc'] = sum_projects_df['num_lines_with_boolops']*100/sum_projects_df['file_loc']
    sum_projects_df.sort_values(['boolops_per_loc'],inplace=True)

    f = plt.figure()
    f.set_figwidth(10)
    f.set_figheight(10)
    ax = sum_projects_df['boolops_per_loc'].plot(kind='barh', color=my_colors)
    ax.set_ylabel('')
    ax.set_xlabel('Boolean operations in relation of total LOC')
    for ticks in ax.yaxis.get_major_ticks():
        if ticks.label1.get_text() in desired:
            ax.patches[sum_projects_df.index.get_indexer([ticks.label1.get_text()])[0]].set_facecolor('b')
            # ax.patches[sum_projects_df.index.get_indexer([ticks.label1.get_text()])[0]].set_edgecolor('black')

    save_and_show('boolops_per_loc.pdf', 'boolops_per_loc', sum_projects_df['boolops_per_loc'].to_string())

    f = plt.figure()
    f.set_figwidth(10)
    f.set_figheight(10)
    sum_projects_df.sort_values(['lines_with_boolops_per_loc'], inplace=True)
    ax = sum_projects_df['lines_with_boolops_per_loc'].plot(kind='barh', figsize=[6.4, 8], color=my_colors)
    ax.set_ylabel('')
    ax.set_xlabel('% lines with Boolean operations of total LOC')
    for ticks in ax.yaxis.get_major_ticks():
        if ticks.label1.get_text() in desired:
            ax.patches[sum_projects_df.index.get_indexer([ticks.label1.get_text()])[0]].set_facecolor('b')
            # ax.patches[sum_projects_df.index.get_indexer([ticks.label1.get_text()])[0]].set_edgecolor('black')
    for index, value in enumerate(sum_projects_df['lines_with_boolops_per_loc']):
        if value > 10:
            plt.text(value - 1, index-0.21, "{:.2f}".format(value)+" %", color='white', fontsize=6)
        else:
            plt.text(value + 0.1, index-0.21, "{:.2f}".format(value)+" %", fontsize=7)
    save_and_show('lines_with_boolops_per_loc.pdf', 'lines_with_boolops_per_loc', sum_projects_df['lines_with_boolops_per_loc'].to_string())

    f = plt.figure()
    f.set_figwidth(15)
    f.set_figheight(8)
    sum_projects_df = sum_projects_df.rename(index={'cffi-branch-default': 'cffi-branch-df.',
                                               'Real-Time-Voice-Cloning': 'Real-Time-Vc.-Cl.',
                                               'face_recognition':' face_recog'})
    sum_projects_df.sort_values(['lines_with_boolops_per_loc'], inplace=True)
    ax = sum_projects_df['lines_with_boolops_per_loc'].plot(kind='bar', figsize=[10,5], color=my_colors)
    # plt.xticks(rotation=45)
    ax.set_xlabel('')
    ax.set_ylabel('% lines with Boolean operations of total LOC')
    for ticks in ax.xaxis.get_major_ticks():
        if ticks.label1.get_text() in desired:
            ax.patches[sum_projects_df.index.get_indexer([ticks.label1.get_text()])[0]].set_facecolor('b')
            # ax.patches[sum_projects_df.index.get_indexer([ticks.label1.get_text()])[0]].set_edgecolor('black')
    for index, value in enumerate(sum_projects_df['lines_with_boolops_per_loc']):
        if value > 10:
            plt.text(index - 0.2, value + 0.3, "{:.1f}".format(value), color='black', fontsize=8, rotation='vertical')
        else:
            plt.text(index - 0.2, value + 0.3, "{:.1f}".format(value), fontsize=8, rotation='vertical')
    ax.set_ylim(0, 12)
    plt.tight_layout()
    save_and_show('lines_with_boolops_per_loc_flipped.pdf', 'lines_with_boolops_per_loc',
                  sum_projects_df['lines_with_boolops_per_loc'].to_string())



if __name__ == '__main__':
    main()
