# -*- coding: utf-8 -*-

"""Cross-validation utilities."""
import itertools
import math
from collections import defaultdict
from typing import Union, Tuple

import numpy as np
from diffupy.diffuse_raw import diffuse_raw
from diffupy.kernels import regularised_laplacian_kernel
from diffupy.matrix import Matrix
from diffupy.process_input import format_input_for_diffusion, process_input_data
from pybel import get_subgraph_by_annotation_value
from scipy import stats
from sklearn import metrics
from statsmodels.stats.multitest import fdrcorrection
from tqdm import tqdm

from .topological_analyses import generate_pagerank_baseline
from .utils import split_random_two_subsets

"""Random cross validation datasets functions"""


def cross_validation_by_method(data_input,
                               graph,
                               kernel,
                               k=100
                               ):
    """Cross validation by method."""
    auroc_metrics = defaultdict(list)
    auprc_metrics = defaultdict(list)

    for _ in tqdm(range(k)):
        input_diff, validation_diff = _get_random_cv_split_input_and_validation(
            data_input, kernel
        )

        scores_z = diffuse_raw(graph=None, scores=input_diff, k=kernel, z=True)
        scores_raw = diffuse_raw(graph=None, scores=input_diff, k=kernel, z=False)
        scores_page_rank = generate_pagerank_baseline(graph, kernel)

        method_validation_scores = {
            'raw': (validation_diff,
                    scores_raw
                    ),
            'z': (validation_diff,
                  scores_z
                  ),
            'random': (
                validation_diff,
                _generate_random_score_ranking(kernel)
            ),
            'page_rank': (
                validation_diff,
                scores_page_rank
            ),

        }

        for method, validation_set in method_validation_scores.items():
            auroc, auprc = _get_metrics(*validation_set)
            auroc_metrics[method].append(auroc)
            auprc_metrics[method].append(auprc)

    return auroc_metrics, auprc_metrics


def cross_validation_by_subgraph(data_input,
                                 graph,
                                 graph_parameter,
                                 type_list,
                                 universe_kernel=None,
                                 z_normalization=False,
                                 k=100
                                 ):
    """Cross validation by subgraph."""
    auroc_metrics = defaultdict(list)
    auprc_metrics = defaultdict(list)

    # Pre-process kernel for subgraphs
    kernels = {parameter: regularised_laplacian_kernel(get_subgraph_by_annotation_value(graph,
                                                                                        graph_parameter,
                                                                                        parameter)
                                                       )
               for parameter in tqdm(type_list, 'Generate kernels from subgraphs')
               }

    for _ in tqdm(range(k), 'Computate validation scores'):
        subgraph_validation_scores = {}

        for type, kernel in kernels.items():

            if universe_kernel is None:
                universe_kernel = kernel

            input_diff, validation_diff = _get_random_cv_split_input_and_validation(data_input[type],
                                                                                    kernel)
            input_diff_universe, validation_diff_universe = _get_random_cv_split_input_and_validation(data_input[type],
                                                                                                      universe_kernel)

            scores_on_subgraph = diffuse_raw(graph=None,
                                             scores=input_diff,
                                             k=kernel,
                                             z=z_normalization)
            scores_on_universe = diffuse_raw(graph=None,
                                             scores=input_diff_universe,
                                             k=universe_kernel,
                                             z=z_normalization)

            subgraph_validation_scores[type + 'on ' + type] = (validation_diff, scores_on_subgraph)
            subgraph_validation_scores[type + 'on PathMeUniverse'] = (validation_diff_universe, scores_on_universe)

        for method, validation_set in subgraph_validation_scores.items():
            auroc, auprc = _get_metrics(*validation_set)
            auroc_metrics[method].append(auroc)
            auprc_metrics[method].append(auprc)

    return auroc_metrics, auprc_metrics


"""Helper functions for random cross-validation"""


def _generate_random_score_ranking(background_mat):
    """Generate random scores."""
    return Matrix(
        mat=np.random.rand(len(background_mat.rows_labels)),
        rows_labels=background_mat.rows_labels,
        cols_labels=['Radom_Baseline'],
    )


def _get_random_cv_split_input_and_validation(input: Union[list, set],
                                              background_mat: Matrix
                                              ) -> Tuple[Matrix, Matrix]:
    """Get random CV split."""
    input_labels, validation_labels = split_random_two_subsets(input)

    if isinstance(validation_labels, dict):
        validation_labels = process_input_data(validation_labels, binning=True, threshold=0.5)

    return (
        format_input_for_diffusion(
            input_labels,
            background_mat,
            title='label_input with hidden true positives'
        ),
        format_input_for_diffusion(
            validation_labels,
            background_mat,
            title='original label_input labels'
        )
    )


def _get_metrics(validation_labels,
                 scores
                 ):
    """Return metrics."""
    return metrics.roc_auc_score(validation_labels.mat, scores.mat), metrics.average_precision_score(
        validation_labels.mat, scores.mat)


"""Statistical test"""


def get_p_values(metrics):
    p_values = {}

    result_list = map(dict, itertools.combinations(metrics.items(), 2))

    for ch in result_list:
        values = list(ch.values())
        ttest = stats.ttest_rel(a=values[0], b=values[1])
        p_values[str(tuple(ch.keys()))] = ttest.pvalue

    return p_values


def get_p_values_multiple(metrics):
    p_values = {}

    for k, v in metrics[0].items():
        ttest = stats.ttest_rel(a=v, b=metrics[1][k])
        p_values[str(k)] = ttest.pvalue

    return p_values


def get_normalized_p_values(p_values):
    normalized_p_values = {}

    fdr = fdrcorrection(list(p_values.values()),
                        alpha=0.05,
                        method='indep',
                        is_sorted=False)

    for k1, k2 in enumerate(p_values.keys()):
        normalized_p_values[k2] = -math.log10(fdr[1][k1])

    return normalized_p_values
