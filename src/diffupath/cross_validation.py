# -*- coding: utf-8 -*-

"""Cross-validation utilities."""

from collections import defaultdict

import numpy as np
from diffupy.diffuse_raw import diffuse_raw
from diffupy.matrix import Matrix
from diffupy.process_input import generate_categoric_input_from_labels
from sklearn import metrics
from tqdm import tqdm

from typing import Union, Tuple

from .topological_analyses import generate_pagerank_baseline
from .utils import random_disjoint_intersection_three_subsets, hide_true_positives, split_random_two_subsets

"""Random cross validation_datasets"""


def get_random_cv_split_input_and_validation(input: Union[list, set],
                                             background_mat: Matrix
                                             ) -> Tuple[Matrix, Matrix]:
    """Get random CV split."""
    input_labels, validation_labels = split_random_two_subsets(input)

    return (
        generate_categoric_input_from_labels(
            input_labels,
            'label_input with hidden true positives',
            background_mat
        ),
        generate_categoric_input_from_labels(
            validation_labels,
            'original label_input labels',
            background_mat
        )
    )


def get_random_cv_inputs_from_subsets_same_diff_input(input_subsets: Union[list, set],
                                                      background_mat
                                                      ):
    """Get random CV label_input from subsets with different label_input."""
    input_labels = set()
    input_unlabeled = set()

    validation_mats_by_entity_type = defaultdict()

    for entity_type, input in input_subsets.items():
        hidden_input = hide_true_positives(input[0])
        validation_mats_by_entity_type[entity_type] = generate_categoric_input_from_labels(
            input[0],
            'Dataset 1 ' + str(
                entity_type),
            background_mat
        )
        input_unlabeled.update(set(input[0]))
        input_labels.update(set(hidden_input))

    input_mat = generate_categoric_input_from_labels(input_labels, 'Dataset1', background_mat, input_unlabeled)

    return input_mat, validation_mats_by_entity_type


# Partial cross validation_datasets

def get_one_x_in_cv_inputs_from_subsets(
        input_subsets,
        background_mat,
        one_in='Reactome',
        rows_unlabeled=False,
        missing_value=-1
):
    """Get one cross label_input from subsets."""
    input_dict = {}
    input_labels = input_subsets.pop(one_in)
    rows_unlabel = None

    for labels_type, validation_labels in input_subsets.items():
        if rows_unlabeled:
            rows_unlabel = validation_labels
            missing_value = -1

        input_dict[labels_type] = (
            generate_categoric_input_from_labels(
                input_labels,
                'two out label_input',
                background_mat,
                missing_value,
                rows_unlabeled=rows_unlabel
            ),
            generate_categoric_input_from_labels(
                validation_labels,
                'two out label_input',
                background_mat,
                missing_value,
            )
        )
    return input_dict


def get_metrics(validation_labels,
                scores
                ):
    """Return metrics."""
    validation_labels_vec = validation_labels.__copy__()

    return metrics.roc_auc_score(validation_labels.mat, scores.mat), metrics.average_precision_score(
        validation_labels.mat, scores.mat)


def cross_validation_by_subset_same_diff_input(mapping_by_subsets,
                                               kernel,
                                               k=3,
                                               z=True):
    """Cross validation helper."""
    auroc_metrics = defaultdict(list)
    auprc_metrics = defaultdict(list)

    for i in tqdm(range(k)):
        input_mat, validation_inputs_by_subsets = get_random_cv_inputs_from_subsets_same_diff_input(
            mapping_by_subsets,
            kernel,
        )

        scores = diffuse_raw(graph=None, scores=input_mat, k=kernel, z=z)

        for entity, validation_labels in validation_inputs_by_subsets.items():
            auroc, auprc = get_metrics(validation_labels, scores)
            auroc_metrics[entity].append(auroc)
            auprc_metrics[entity].append(auprc)

    return auroc_metrics, auprc_metrics


def cross_validation_one_x_in(mapping_by_subsets,
                              kernel,
                              k=1,
                              missing_value=-1,
                              disjoint=False,
                              rows_unlabeled=False,
                              z=False
                              ):
    """Cross validation one."""
    auroc_metrics = defaultdict(lambda: defaultdict(list))
    auprc_metrics = defaultdict(lambda: defaultdict(list))

    scores_dict = defaultdict(lambda: defaultdict(list))
    validation_dict = defaultdict(lambda: defaultdict(list))
    input_dict = defaultdict(lambda: defaultdict(list))

    if disjoint:
        mapping_by_subsets = random_disjoint_intersection_three_subsets(mapping_by_subsets)

    for i in tqdm(range(k)):

        for diffuse_input_type in tqdm(mapping_by_subsets):
            inputs = get_one_x_in_cv_inputs_from_subsets(
                dict(mapping_by_subsets),
                kernel,
                one_in=diffuse_input_type,
                rows_unlabeled=rows_unlabeled,
                missing_value=missing_value,
            )

            for validation_type, validation_labels in inputs.items():
                input_diffuse, input_validation = validation_labels[0], validation_labels[1]

                # Input test
                # validate_cross_validation_input_1(input_diffuse, input_validation, validation_input_from_dict(mapping_by_subsets, diffuse_input_type, validation_type, input_diffuse))

                # Run diffusion
                scores = diffuse_raw(graph=None, scores=input_diffuse, k=kernel, z=z)

                scores.cols_labels = ['scores']
                input_validation.cols_labels = ['input_validation']
                input_diffuse.cols_labels = ['input_diffuse']

                auroc, auprc = get_metrics(input_validation, scores)

                auroc_metrics[diffuse_input_type][validation_type].append(auroc)
                auprc_metrics[diffuse_input_type][validation_type].append(auprc)

                scores.col_bind(matrix=input_validation)
                scores.col_bind(matrix=input_diffuse)

                scores_dict[diffuse_input_type][validation_type].append(scores)

    return dict(auroc_metrics), dict(auprc_metrics), dict(scores_dict)


# Method cross validation_datasets


def generate_random_score_ranking(background_mat):
    """Generate random scores."""
    return Matrix(
        mat=np.random.rand(len(background_mat.rows_labels)),
        rows_labels=background_mat.rows_labels,
        cols_labels=['Radom_Baseline'],
    )


def cross_validation_by_method(all_labels_mapping,
                               graph,
                               kernel,
                               k=100
                               ):
    """Cross validation by method."""
    auroc_metrics = defaultdict(list)
    auprc_metrics = defaultdict(list)

    for _ in tqdm(range(k)):
        input_diff, validation_diff = get_random_cv_split_input_and_validation(
            all_labels_mapping, kernel
        )

        scores_z = diffuse_raw(graph=None, scores=input_diff, k=kernel, z=True)
        scores_raw = diffuse_raw(graph=None, scores=input_diff, k=kernel, z=False)
        scores_page_rank = generate_pagerank_baseline(graph, kernel)

        method_validation_inputs = {
            'raw': (validation_diff,
                    scores_raw
                    ),
            'z': (validation_diff,
                  scores_z
                  ),
            'random_baseline': (
                validation_diff,
                generate_random_score_ranking(kernel)
            ),
            'page_rank_baseline': (
                validation_diff,
                scores_page_rank
            ),

        }

        for method, validation_set in method_validation_inputs.items():
            auroc, auprc = get_metrics(*validation_set)
            auroc_metrics[method].append(auroc)
            auprc_metrics[method].append(auprc)

    return auroc_metrics, auprc_metrics
