# -*- coding: utf-8 -*-

"""Cross-validation utilities."""
import itertools
import math
from collections import defaultdict

import pandas as pd
from scipy import stats
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import fdrcorrection

"""Statistical tests"""


def get_p_values(metrics):
    """Get p_values."""
    p_values = {}

    result_list = map(dict, itertools.combinations(metrics.items(), 2))

    for ch in result_list:
        values = list(ch.values())
        ttest = stats.ttest_rel(a=values[0], b=values[1])
        p_values[str(tuple(ch.keys()))] = ttest.pvalue

    return p_values


def get_p_values_multiple(metrics):
    """Get p_values_multiple."""
    p_values = {}

    for k, v in metrics[0].items():
        ttest = stats.ttest_rel(a=v, b=metrics[1][k])
        p_values[str(k)] = ttest.pvalue

    return p_values


def get_normalized_p_values(p_values):
    """Get normalized_p_values."""
    normalized_p_values = {}

    fdr = fdrcorrection(list(p_values.values()),
                        alpha=0.05,
                        method='indep',
                        is_sorted=False)

    for k1, k2 in enumerate(p_values.keys()):
        normalized_p_values[k2] = -math.log10(fdr[1][k1])

    return normalized_p_values


"""Wilcoxon test"""


def get_wilcoxon_test(metrics, dataframe=False, title=""):
    """Get Wilcoxon test p_values."""
    p_values = defaultdict(lambda: defaultdict(lambda: float))

    for metrics_i in metrics:
        result_list = map(dict, itertools.combinations(metrics[metrics_i].items(), 2))
        for ch in result_list:
            values = list(ch.values())

            _, p_value = wilcoxon(values[0], values[1])

            p_values[metrics_i][str(tuple(ch.keys()))] = p_value

    if dataframe:
        df = pd.DataFrame.from_dict({(i, j): [i, j, p_values[i][j], p_values[i][j] < 0.017]
                                     for i in p_values.keys()
                                     for j in p_values[i].keys()},
                                    orient='index')
        df.columns = ['Dataset', f'Comparison {title}', 'p_value', 'Significant difference']

        return df

    return p_values
