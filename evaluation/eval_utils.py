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
    for zipped_csv in glob.glob('data/*_slicing_*.csv.zip'):
        zip_df = pandas.read_csv(zipped_csv, compression='zip')
        log.s(zipped_csv + ' ' + str(zip_df.shape))
        df = pandas.concat([df, zip_df], ignore_index=True)
        # df = df.append(zip_df, ignore_index=True)

    df['benchmark'] = df['test_name'].apply(lambda x: x.split('/')[1])

    # df = df.drop(columns=['Unnamed: 0.1', 'Unnamed: 0'])
    df = df.drop(columns=['Unnamed: 0'])
    return df


def remove_exceptions_and_wrong_results(df, slice_type=None):
    df = df[df['exception'].isnull()] # exceptions during augmentation, tracing,
    df = df[df['dumb_dyn_slice_exception'].isnull()]

    if slice_type in ['dyn', 'both']:
        df = df[df['dyn_slice_exception'].isnull()]
        df = df[df['pruned_slice_exception'].isnull()]
        df = df[df['pruned_sliced_result_equal_to_bare']]

    if slice_type in ['rel', 'both']:
        df = df[df['relevant_slice_exception'].isnull()]
        df = df[df['relevant_sliced_result_equal_to_bare']]
        df = df[df['pruned_relevant_slice_exception'].isnull()]
        df = df[df['pruned_relevant_sliced_result_equal_to_bare']]
    return df


def get_failing_tests(df):
    df = df[df['test_result'] == False]
    return df


def save_and_show(file_name, title, info_text, dpi=None):
    if add_titles:
        plt.gcf().suptitle(title)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(plots_dir + file_name, dpi=dpi)
    with open(plots_dir + file_name + '.txt', 'w', encoding="utf-8") as file:
        file.write(info_text)
    if show:
        plt.show()
    plt.close()
