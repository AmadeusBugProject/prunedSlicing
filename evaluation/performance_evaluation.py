import pandas as pd
import glob
import matplotlib.pyplot as plt
from matplotlib import ticker
from itertools import cycle, islice

from constants import root_dir
from evaluation.eval_utils import read_data, remove_exceptions_and_wrong_results, save_and_show
from helpers.Logger import Logger
import scipy.stats as stats
import scipy
from statistics import mean, stdev
from math import sqrt

log = Logger()


def main():
    df = read_data()
    df = remove_exceptions_and_wrong_results(df, 'both')
    df = df[df['benchmark'].isin(['tcas', 'refactory', 'quixbugs'])]
    # all_anova_tests(df)
    # all_wilcoxon(df)
    all_cohensd(df)

    # print(df.columns)
    #
    all_performance_measures(df)
    # # slicing_performance_measures(df[(df['benchmark']=='tcas')|(df['benchmark']=='refactory')|(df['benchmark']=='quixbugs')])
    analyze_performance_with_scatter_plot(df)


def all_wilcoxon(df):

    print("\n**************** QuixBugs *********************")
    QuixBugs = apply_wilcoxon_signed_rank(df[df['benchmark'] == 'quixbugs'])

    print("\n**************** Refactory *********************")
    Refactory = apply_wilcoxon_signed_rank(df[df['benchmark'] == 'refactory'])

    print("\n**************** TCAS *********************")
    TCAS = apply_wilcoxon_signed_rank(df[df['benchmark'] == 'tcas'])

    df = pd.DataFrame([TCAS, Refactory, QuixBugs])
    df = df.T.rename(columns={0: 'TCAS', 1: 'Refactory', 2: 'QuixBugs'})
    print(df.to_latex())


def all_cohensd(df):

    print("\n**************** QuixBugs *********************")
    QuixBugs = apply_cohensd(df[df['benchmark'] == 'quixbugs'])

    print("\n**************** Refactory *********************")
    Refactory = apply_cohensd(df[df['benchmark'] == 'refactory'])

    print("\n**************** TCAS *********************")
    TCAS = apply_cohensd(df[df['benchmark'] == 'tcas'])

    df = pd.DataFrame([TCAS, Refactory, QuixBugs])
    df = df.T.rename(columns={0: 'TCAS', 1: 'Refactory', 2: 'QuixBugs'})
    df.to_latex(root_dir() + 'evaluation/latex_tables/effect_size_cohens_d.tex')



def apply_cohensd(df):
    d_value_1 = sigle_cohensd_test(df, 'runtime_dyn_slice', 'runtime_relevant_slice')
    d_value_2 = sigle_cohensd_test(df, 'runtime_dyn_slice', 'runtime_pruned_slice')
    d_value_3 = sigle_cohensd_test(df, 'runtime_relevant_slice', 'runtime_pruned_relevant_slice')

    d_values = {"Dynamic - relevant": d_value_1, "Dynamic - pruned dynamic": d_value_2, "Relevant - pruned relevant": d_value_3}
    return d_values

def sigle_cohensd_test(df, group1, group2):
    cohens_d = (df[group1].mean() - df[group2].mean()) / (sqrt((df[group1].std() ** 2 + df[group2].std() ** 2) / 2))
    print('cohensd:')
    print(cohens_d)
    return cohens_d


def apply_wilcoxon_signed_rank(df):
    p_value_1 = sigle_wilcoxon_signed_rank_test(df, 'runtime_dyn_slice', 'runtime_relevant_slice')
    p_value_2 = sigle_wilcoxon_signed_rank_test(df, 'runtime_dyn_slice', 'runtime_pruned_slice')
    p_value_3 = sigle_wilcoxon_signed_rank_test(df, 'runtime_relevant_slice', 'runtime_pruned_relevant_slice')

    p_values = {"Dynamic - relevant": p_value_1, "Dynamic - pruned dynamic": p_value_2, "Relevant - pruned relevant": p_value_3}
    return p_values

def sigle_wilcoxon_signed_rank_test(df, group1, group2):
    statistic, p_value = stats.wilcoxon(df[group1], df[group2], alternative='two-sided')
    print(f"Wicloxon signed rank: p-value = {p_value:.15f}")
    if p_value < 0.05:
        print("Reject the null hypothesis: Significant difference between groups ("+group1+", "+group2+").")
    else:
        print("Fail to reject the null hypothesis: No significant difference between groups ("+group1+", "+group2+").")

    cohens_d = (df[group1].mean() - df[group2].mean()) / (sqrt((df[group1].std() ** 2 + df[group2].std() ** 2) / 2))
    print('cohensd:')
    print(cohens_d)
    return p_value


def all_anova_tests(df):
    quix = df[df['benchmark'] == 'quixbugs']
    tcas = df[df['benchmark'] == 'tcas']
    refactory = df[df['benchmark'] == 'refactory']

    print("\n**************** QuixBugs *********************")
    anova_test(df[df['benchmark'] == 'quixbugs'])

    print("\n**************** Refactory *********************")
    anova_test(df[df['benchmark'] == 'refactory'])

    print("\n**************** TCAS *********************")
    anova_test(df[df['benchmark'] == 'tcas'])


def anova_test(df):
    df = df[['runtime_dyn_slice', 'runtime_pruned_slice', 'runtime_relevant_slice', 'runtime_pruned_relevant_slice']]
    # Check assumptions
    # 1. Normality (Shapiro-Wilk test)
    print("SAMPLE size: "+str(len(df)))

    for group in df.columns:
        _, p_value = stats.shapiro(df[group])
        print(f"Shapiro-Wilk test for {group}: p-value = {p_value:.9f}")
        if p_value > 0.05:
            print(f"{group} is approximately normally distributed.")
        else:
            print(f"{group} is not normally distributed.")

    # 2. Homogeneity of variances (Levene test)
    _, p_value = stats.levene(df['runtime_dyn_slice'], df['runtime_pruned_slice'], df['runtime_relevant_slice'], df['runtime_pruned_relevant_slice'])
    print(f"Levene test for homogeneity of variances: p-value = {p_value:.4f}")
    if p_value > 0.05:
        print("Homogeneity of variances is met.")
    else:
        print("Homogeneity of variances is not met.")

    # Perform ANOVA
    _, p_value = stats.f_oneway(df['runtime_dyn_slice'], df['runtime_pruned_slice'], df['runtime_relevant_slice'], df['runtime_pruned_relevant_slice'])
    print(f"ANOVA: p-value = {p_value:.4f}")

    if p_value < 0.05:
        print("Significant differences found between groups.")
    else:
        print("No significant differences between groups.")


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
    axs[1].set_ylabel("Refactory\nsmillieconds")
    axs[2].scatter(quix['len_exec_trace'], quix['runtime_dyn_slice'], alpha=0.5, marker='.')
    axs[2].set_ylabel("Quixbugs\nmilliseconds")
    axs[2].set_xlabel("Execution trace length")
    save_and_show('scatter_performance_exec_len.png', 'scatter_performance_exec_len', '', dpi=300)

    fig, ax = plt.subplots(1, figsize=(6, 6))
    ax.scatter(refactory['len_exec_trace'], refactory['runtime_dyn_slice'], alpha=0.3, marker='s', c="b", s=10, label="Refactory")
    ax.scatter(quix['len_exec_trace'], quix['runtime_dyn_slice'], alpha=0.3, marker='o',  c="r", s=10, label="Quixbugs")
    ax.scatter(tcas['len_exec_trace'], tcas['runtime_dyn_slice'], alpha=0.3, marker='v', c="black", s=10, label="Tcas")
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_ylabel("Slice computation time in milliseconds")
    ax.set_xlabel("Execution trace length")
    plt.legend(loc='lower right')
    save_and_show('scatter_performance_exec_len_combined.png', 'scatter_performance_exec_len', '', dpi=300)

    print("*Person coefficients len_exec_trace - runtime_dyn_slice*")
    print("TCAS: "+str(scipy.stats.pearsonr(tcas['len_exec_trace'], tcas['runtime_dyn_slice'])))
    print("refactory: " + str(scipy.stats.pearsonr(refactory['len_exec_trace'], refactory['runtime_dyn_slice'])))
    print("quix: " + str(scipy.stats.pearsonr(quix['len_exec_trace'], quix['runtime_dyn_slice'])))

def all_performance_measures(df):
    my_colors = list(islice(cycle(['blue', 'white', 'black', 'gray', 'darkgray', 'lightgray']), None, len(df)))

    # cols = ['benchmark', 'runtime_bare_test', 'perf_runtime_bare_test',
    #         'runtime_tracing_augmented_test', 'perf_runtime_tracing_augmented_test',
    #         'runtime_dyn_slice', 'perf_runtime_dyn_slice',
    #         'runtime_pruned_slice', 'perf_runtime_pruned_slice']
    cols = ['benchmark', 'runtime_bare_test',  'runtime_tracing_augmented_test',
            'runtime_dyn_slice', 'runtime_pruned_slice', 'runtime_relevant_slice', 'runtime_pruned_relevant_slice']
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
    mean_performance_df['runtime_relevant_slice'] = mean_performance_df['runtime_relevant_slice'] * 1000
    mean_performance_df['runtime_pruned_relevant_slice'] = mean_performance_df['runtime_pruned_relevant_slice'] * 1000
    mean_performance_df = mean_performance_df.rename(
        columns={'runtime_bare_test': 'Bare test',
                 'runtime_tracing_augmented_test': 'Tracing',
                 'runtime_dyn_slice': 'Dynamic Slicing',
                 'runtime_pruned_slice': 'Pruned Dynamic Slicing',
                 'runtime_relevant_slice': 'Relevant Slicing',
                 'runtime_pruned_relevant_slice': 'Pruned Relevant Slicing'
                 })
    ax = mean_performance_df.plot(kind='barh', color=my_colors, edgecolor='black', figsize=[6.4, 6], width=0.8)

    ax.set_xlabel('milliseconds')
    ax.set_ylabel('')
    ax.set_xlim([0, 16])

    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))

    x_offset = 0.2
    y_offset = 0.39
    y_multiplier = 0.14
    idx = 0
    for key in ['Bare test', 'Tracing', 'Dynamic Slicing', 'Pruned Dynamic Slicing', 'Relevant Slicing', 'Pruned Relevant Slicing']:
        for index, value in enumerate(mean_performance_df[key]):
            if key == 'Bare test':
                plt.text(value + x_offset, index - y_offset + idx * y_multiplier, "{:.3f}".format(value), color='blue',
                         fontsize=9)
            else:
                plt.text(value + x_offset, index - y_offset + idx * y_multiplier, "{:.3f}".format(value), fontsize=9)

        idx += 1

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1])

    save_and_show('mean_performance_df.pdf', 'mean_performance_df', performance_df.to_string())


def slicing_performance_measures(df):
    cols = ['benchmark', 'runtime_dyn_slice', 'runtime_pruned_slice']
    log.s('\n' + str(df[cols].describe()))

    slicing_performance_df = df[cols].groupby('benchmark').describe()
    log.s('\n' + str(slicing_performance_df.to_string()))

    mean_slicing_performance_df = df[cols].groupby('benchmark').mean()
    ax = mean_slicing_performance_df.plot(kind='barh')
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.5fs'))
    save_and_show('mean_slicing_performance_df.pdf', 'mean_slicing_performance_df', slicing_performance_df.to_string())

if __name__ == '__main__':
    main()
