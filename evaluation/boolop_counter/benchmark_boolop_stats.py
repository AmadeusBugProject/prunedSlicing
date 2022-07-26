# todo: count boolops in a python file

# check quixbugs  -  https://github.com/jkoppel/QuixBugs
# check refactorydataset  -  https://github.com/githubhuyang/refactory
import ast
import glob

import pandas

from benchmark.benchmark_root import benchmark_dir
from evaluation.boolop_counter import count_boolops


def main():
    benchmarks = [
                       'middle',
                       'quixbugs',
                       'refactory',
                       'tcas',
                       'triangle'
                      ]

    for bench in benchmarks:
        count_boolops.main(benchmark_dir() + '/' + bench, bench + '.csv')


if __name__ == '__main__':
    main()
