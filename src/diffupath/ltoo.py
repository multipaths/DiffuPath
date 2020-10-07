# -*- coding: utf-8 -*-

"""Leave two omics out validation utilities."""
from collections import defaultdict
from typing import Union, Tuple, Dict

import numpy as np
from diffupy.diffuse_raw import diffuse_raw
from diffupy.matrix import Matrix
from diffupy.process_input import format_input_for_diffusion
from sklearn import metrics
from tqdm import tqdm

from .topological_analyses import generate_pagerank_baseline

"""Leave two omics out  validation datasets functions"""


def ltoo_by_method(
        mapping_input,
        graph,
        kernel,
        k=100
):
    """Cross validation by method."""
    auroc_metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    auprc_metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for _ in tqdm(range(k)):
        for entity in mapping_input:

            input_diff, merged_validation_diff, stratified_validation_diff = _get_split_by_type_input_and_validation(
                mapping_input, kernel, entity
            )

            scores_z = diffuse_raw(graph=None, scores=input_diff, k=kernel, z=True)
            scores_raw = diffuse_raw(graph=None, scores=input_diff, k=kernel, z=False)
            scores_page_rank = generate_pagerank_baseline(graph, kernel)

            method_validation_scores_by_type = {
                'merged': get_by_method_metrics_input_dict(merged_validation_diff,
                                                           scores_raw,
                                                           scores_z,
                                                           scores_page_rank,
                                                           kernel
                                                           )
            }

            for entity_label, validation_diff in stratified_validation_diff.items():
                method_validation_scores_by_type[entity_label] = get_by_method_metrics_input_dict(validation_diff,
                                                                                                  scores_raw,
                                                                                                  scores_z,
                                                                                                  scores_page_rank,
                                                                                                  kernel
                                                                                                  )
            for entity_label, method_validation_scores in method_validation_scores_by_type.items():
                for method, validation_set in method_validation_scores.items():
                    try:
                        auroc, auprc = _get_metrics(*validation_set)
                    except ValueError:
                        auroc, auprc = (0, 0)
                        print(f'ROC AUC unable to calculate for {validation_set}')

                    auroc_metrics[entity][entity_label][method].append(auroc)
                    auprc_metrics[entity][entity_label][method].append(auprc)

    return auroc_metrics, auprc_metrics


"""Helper functions for LTOO validation"""


def get_by_method_metrics_input_dict(
        validation_diff: Matrix,
        scores_raw: Matrix,
        scores_z: Matrix,
        scores_page_rank: Matrix,
        kernel: Matrix) -> Dict[str, Tuple[Matrix, Matrix]]:
    """Get dict metric input by method."""
    return {
        'raw': (
            validation_diff,
            scores_raw
        ),
        'z': (
            validation_diff,
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


def _generate_random_score_ranking(background_mat):
    """Generate random scores."""
    return Matrix(
        mat=np.random.rand(len(background_mat.rows_labels)),
        rows_labels=background_mat.rows_labels,
        cols_labels=['Radom_Baseline'],
    )


def _get_split_by_type_input_and_validation(
        input: Dict[str, Union[list, set]],
        background_mat: Matrix,
        type_label: str) -> Tuple[Matrix, Matrix, Dict[str, Matrix]]:
    """Get LTOO split (One-out as diffuse input and Leave-One-Out as validation)."""
    input_labels = list(set(input[type_label]))

    all_validation_labels = list(set().union(*[v for label, v in input.items() if label != type_label]))

    stratified_validation_labels = {
        label: format_input_for_diffusion(
            enitites,
            background_mat,
            title='label_input for validation with hidden true positives'
        )
        for label, enitites in input.items()
        if label != type_label
    }

    return (
        format_input_for_diffusion(
            input_labels,
            background_mat,
            title='label_input for diffusion with hidden true positives'
        ),
        format_input_for_diffusion(
            all_validation_labels,
            background_mat,
            title='label_input for validation with hidden true positives'
        ),
        stratified_validation_labels
    )


def _get_metrics(
        validation_labels,
        scores
):
    """Return metrics."""
    return metrics.roc_auc_score(validation_labels.mat, scores.mat), metrics.average_precision_score(
        validation_labels.mat, scores.mat)
