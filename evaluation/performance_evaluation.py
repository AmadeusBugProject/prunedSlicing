import pandas
import glob
import matplotlib.pyplot as plt
from matplotlib import ticker
from itertools import cycle, islice
from evaluation.eval_utils import read_data, remove_exceptions_and_wrong_results, save_and_show
from helpers.Logger import Logger

log = Logger()


def main():
    df = read_data()
    df = remove_exceptions_and_wrong_results(df)
    df = df[df['benchmark'].isin(['tcas', 'refactory', 'quixbugs'])]

    print(df.columns)
    analyze_performance_with_scatter_plot(df)
    all_performance_measures(df)
    # slicing_performance_measures(df[(df['benchmark']=='tcas')|(df['benchmark']=='refactory')|(df['benchmark']=='quixbugs')])


def analyze_performance_with_scatter_plot(df):
    cols = ['benchmark', 'len_exec_trace', 'runtime_dyn_slice']
    df['runtime_dyn_slice']=df['runtime_dyn_slice']*1000
    quix = df[df['benchmark']=='quixbugs']
    tcas = df[df['benchmark']=='tcas']
    refactory = df[df['benchmark']=='refactory']

    # df_large = df[df['runtime_dyn_slice']>0.1]
    # print(df_large.to_string())

    fig, axs = plt.subplots(3, figsize=(6, 6))

    axs[0].scatter(tcas['len_exec_trace'], tcas['runtime_dyn_slice'], alpha=0.5, marker='.')
    axs[0].set_ylabel("Tcas\nmilliseconds")
    axs[1].scatter(refactory['len_exec_trace'], refactory['runtime_dyn_slice'], alpha=0.5, marker='.')
    axs[1].set_ylabel("Refactory\nmilliseconds")
    axs[2].scatter(quix['len_exec_trace'], quix['runtime_dyn_slice'], alpha=0.5, marker='.')
    axs[2].set_ylabel("Quixbugs\nmilliseconds")
    axs[2].set_xlabel("Execution trace length")
    save_and_show('scatter_performance_exec_len.png', 'scatter_performance_exec_len', '')

    fig, ax = plt.subplots(1, figsize=(6, 6))
    ax.scatter(refactory['len_exec_trace'], refactory['runtime_dyn_slice'], alpha=0.3, marker='s', c="g", s=10, label="Refactory")
    ax.scatter(quix['len_exec_trace'], quix['runtime_dyn_slice'], alpha=0.3, marker='v',  c="black", s=10, label="Quixbugs")
    ax.scatter(tcas['len_exec_trace'], tcas['runtime_dyn_slice'], alpha=0.3, marker='o', c="r", s=10, label="Tcas")
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_ylabel("Slice computation time in milliseconds")
    ax.set_xlabel("Execution trace length")
    plt.legend(loc='lower right')
    save_and_show('scatter_performance_exec_len_combined.png', 'scatter_performance_exec_len', '')


def all_performance_measures(df):
    my_colors = list(islice(cycle(['blue', 'white', 'black', 'grey']), None, len(df)))

    # cols = ['benchmark', 'runtime_bare_test', 'perf_runtime_bare_test',
    #         'runtime_tracing_augmented_test', 'perf_runtime_tracing_augmented_test',
    #         'runtime_dyn_slice', 'perf_runtime_dyn_slice',
    #         'runtime_pruned_slice', 'perf_runtime_pruned_slice']
    cols = ['benchmark', 'runtime_bare_test',  'runtime_tracing_augmented_test',
            'runtime_dyn_slice', 'runtime_pruned_slice']
    # cols = ['benchmark', 'perf_runtime_bare_test', 'perf_runtime_tracing_augmented_test',
    #         'perf_runtime_dyn_slice', 'perf_runtime_pruned_slice']
    log.s('\n' + str(df[cols].describe()))

    performance_df = df[cols].groupby('benchmark').describe()
    log.s('\n' + str(performance_df.to_string()))

    mean_performance_df = df[cols].groupby('benchmark').mean()
    mean_performance_df['runtime_bare_test'] = mean_performance_df['runtime_bare_test'] * 1000
    mean_performance_df['runtime_tracing_augmented_test'] = mean_performance_df['runtime_tracing_augmented_test'] * 1000
    mean_performance_df['runtime_dyn_slice'] = mean_performance_df['runtime_dyn_slice'] * 1000
    mean_performance_df['runtime_pruned_slice'] = mean_performance_df['runtime_pruned_slice'] * 1000
    mean_performance_df = mean_performance_df.rename(
        columns={'runtime_bare_test': 'Bare test', 'runtime_tracing_augmented_test': 'Tracing',
                 'runtime_dyn_slice': 'Dynamic Slice', 'runtime_pruned_slice': 'Pruned Dynamic Slice'})
    ax = mean_performance_df.plot(kind='barh', color=my_colors, edgecolor='black', figsize=[6.4, 3.8], width=0.8)

    ax.set_xlabel('milliseconds')
    ax.set_ylabel('')

    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))

    idx = 0
    for key in ['Bare test', 'Tracing', 'Dynamic Slice', 'Pruned Dynamic Slice']:
        for index, value in enumerate(mean_performance_df[key]):
            if value > 17:
                plt.text(value - 1.5, index - 0.35 + idx*0.2, "{:.3f}".format(value), color='white', fontsize=8)
            elif key == 'Bare test':
                plt.text(value + 0.3, index - 0.35 + idx * 0.2, "{:.3f}".format(value), color='blue', fontsize=8)
            else:
                plt.text(value + 0.3, index - 0.35 + idx*0.2, "{:.3f}".format(value), fontsize=8)
        idx += 1

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1])

    save_and_show('mean_performance_df.png', 'mean_performance_df', performance_df.to_string())


def slicing_performance_measures(df):
    cols = ['benchmark', 'runtime_dyn_slice', 'runtime_pruned_slice']
    log.s('\n' + str(df[cols].describe()))

    slicing_performance_df = df[cols].groupby('benchmark').describe()
    log.s('\n' + str(slicing_performance_df.to_string()))

    mean_slicing_performance_df = df[cols].groupby('benchmark').mean()
    ax = mean_slicing_performance_df.plot(kind='barh')
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.5fs'))
    save_and_show('mean_slicing_performance_df.png', 'mean_slicing_performance_df', slicing_performance_df.to_string())

if __name__ == '__main__':
    main()
