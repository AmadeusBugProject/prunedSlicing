import pandas
import glob

from evaluation.eval_utils import read_data, remove_exceptions_and_wrong_results, save_and_show
from helpers.Logger import Logger

log = Logger()



def main():
    df = read_data()
    # df = remove_exceptions_and_wrong_results(df)
    print(df.columns)
    df['test_file'] = df['test_name'].apply(lambda x: x.split('#')[0])
    df = df.drop_duplicates(subset=['test_file'], keep='last')

    log.s('locs for each benchmark:')
    log.s('\n' + str(df.groupby('benchmark')['code_len'].describe()))

    log.s('num boolops for each benchmark:')
    log.s('\n' + str(df.groupby('benchmark')['num_boolops'].describe()))

    log.s('number of test files in benchmark:')
    log.s(str(df['benchmark'].value_counts()))

    refac_df = df[df['benchmark'] == 'refactory'].copy()
    refac_df['question'] = refac_df['test_file'].apply(lambda x: x.split('/')[3])
    log.s('refactory program versions per question:')
    log.s(str(refac_df['question'].value_counts()))


if __name__ == '__main__':
    main()
