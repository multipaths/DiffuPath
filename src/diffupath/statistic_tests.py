# -*- coding: utf-8 -*-

"""Cross-validation utilities."""
import itertools
import math
from collections import defaultdict
from typing import Union, Tuple

import numpy as np
import pandas as pd
from diffupy.diffuse_raw import diffuse_raw
from diffupy.matrix import Matrix
from diffupy.process_input import format_input_for_diffusion, process_input_data, \
    _type_dict_label_scores_dict_data_struct_check, _type_dict_label_list_data_struct_check, map_labels_input
from scipy import stats
from scipy.stats import wilcoxon
from sklearn import metrics
from statsmodels.stats.multitest import fdrcorrection
from tqdm import tqdm

from .topological_analyses import generate_pagerank_baseline
from .utils import split_random_two_subsets


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
