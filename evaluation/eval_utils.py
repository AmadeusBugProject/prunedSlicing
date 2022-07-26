import glob

import pandas

from helpers.Logger import Logger
from matplotlib import pyplot as plt

log = Logger()

show = True
plots_dir = 'plots/'
add_titles = True

def read_data():
    df = pandas.DataFrame()
    for zipped_csv in glob.glob('data/*.csv.zip'):
        zip_df = pandas.read_csv(zipped_csv, compression='zip')
        log.s(zipped_csv + ' ' + str(zip_df.shape))
        df = df.append(zip_df, ignore_index=True)

    df.drop(['Unnamed: 0'], axis=1, inplace=True)
    df['benchmark'] = df['test_name'].apply(lambda x: x.split('/')[1])
    return df


def remove_exceptions_and_wrong_results(df):
    df = df[df['exception'].isnull()]
    df = df[df['sliced_result_equal_to_bare']]
    return df


def get_failing_tests(df):
    df = df[df['test_result'] == False]
    return df


def save_and_show(file_name, title, info_text):
    if add_titles:
        plt.gcf().suptitle(title)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(plots_dir + file_name)
    with open(plots_dir + file_name + '.txt', 'w', encoding="utf-8") as file:
        file.write(info_text)
    if show:
        plt.show()
    plt.close()
