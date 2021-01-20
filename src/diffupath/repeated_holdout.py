# -*- coding: utf-8 -*-

"""Cross-validation utilities."""
from collections import defaultdict
from typing import Union, Tuple, List, Dict, Optional

import networkx as nx
import numpy as np
from diffupy.diffuse_raw import diffuse_raw
from diffupy.matrix import Matrix
from diffupy.process_input import format_input_for_diffusion, process_input_data, \
    _type_dict_label_scores_dict_data_struct_check, _type_dict_label_list_data_struct_check, map_labels_input
from sklearn import metrics
from tqdm import tqdm

from .topological_analyses import generate_pagerank_baseline
from .utils import split_random_two_subsets

"""Random cross validation datasets functions"""


def validation_by_method(mapping_input: Union[List, Dict[str, List]],
                         graph: nx.Graph,
                         kernel: Matrix,
                         k: Optional[int] = 100
                         ) -> Tuple[Dict[str, list], Dict[str, list]]:
    """Repeated holdout validation by diffustion method.

    :param mapping_input: List or value dictionary of labels {'label':value}.
    :param graph: Network as a graph object.
    :param kernel: Network as a kernel.
    :param k: Iterations for the repeated_holdout validation.
    """
    auroc_metrics = defaultdict(list)
    auprc_metrics = defaultdict(list)

    for _ in tqdm(range(k)):
        input_diff, validation_diff = _get_random_cv_split_input_and_validation(
            mapping_input, kernel
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
            try:
                auroc, auprc = _get_metrics(*validation_set)
            except ValueError:
                auroc, auprc = (0, 0)
                print(f'ROC AUC unable to calculate for {validation_set}')

            auroc_metrics[method].append(auroc)
            auprc_metrics[method].append(auprc)

    return auroc_metrics, auprc_metrics


def validation_by_subgraph(mapping_input,
                           kernels: Dict[str, List[Matrix]],
                           universe_kernel: Optional[Matrix] = None,
                           z_normalization: Optional[bool] = True,
                           k: Optional[int] = 100
                           ) -> Tuple[Dict[str, Dict[str, List]], Dict[str, Dict[str, List]]]:
    """Repeated holdout validation by subgraph.

    :param mapping_input: List or value dictionary of labels {'label':value}.
    :param kernels: Network stratified as a dictionary  {'kernel-tile':kernel}.
    :param universe_kernel: Network as an integrated kernel.
    :param z_normalization: Flag for the statistical normalization option.
    :param k: Iterations for the repeated_holdout validation.
    """
    auroc_metrics = defaultdict(lambda: defaultdict(lambda: list()))
    auprc_metrics = defaultdict(lambda: defaultdict(lambda: list()))

    tmp_mapping = {}

    for _ in tqdm(range(k), 'Computate validation scores'):
        subgraph_validation_scores = defaultdict(lambda: defaultdict(lambda: tuple()))

        for type, kernel in tqdm(kernels.items()):

            if universe_kernel is None:
                universe_kernel = kernel

            if type in tmp_mapping.keys():
                data_input_i = tmp_mapping[type]

            elif (_type_dict_label_list_data_struct_check(
                    mapping_input) or _type_dict_label_scores_dict_data_struct_check(mapping_input)) and type in mapping_input:
                data_input_i = mapping_input[type]

            else:
                print(f'\n Mapping to {type}')
                data_input_i = map_labels_input(input_labels=mapping_input,
                                                background_labels=kernel.rows_labels,
                                                show_descriptive_stat=True
                                                )
                tmp_mapping[type] = data_input_i

            if len(data_input_i) > 1:
                input_diff, validation_diff = _get_random_cv_split_input_and_validation(data_input_i,
                                                                                        kernel)
                input_diff_universe, validation_diff_universe = _get_random_cv_split_input_and_validation(data_input_i,
                                                                                                          universe_kernel)

                scores_on_subgraph = diffuse_raw(graph=None,
                                                 scores=input_diff,
                                                 k=kernel,
                                                 z=z_normalization)
                scores_on_universe = diffuse_raw(graph=None,
                                                 scores=input_diff_universe,
                                                 k=universe_kernel,
                                                 z=z_normalization)

                subgraph_validation_scores[type]['subgraph'] = (validation_diff, scores_on_subgraph)
                subgraph_validation_scores[type]['PathMeUniverse'] = (validation_diff_universe, scores_on_universe)

            else:
                subgraph_validation_scores[type]['subgraph'] = (0, 0)
                subgraph_validation_scores[type]['PathMeUniverse'] = (0, 0)

        for type, validation_set in subgraph_validation_scores.items():
            if validation_set['PathMeUniverse'] == (0, 0):
                auroc_sg, auprc_sg = (0, 0)
                auroc_pu, auprc_pu = (0, 0)
            else:
                try:
                    auroc_sg, auprc_sg = _get_metrics(*validation_set['subgraph'])
                    auroc_pu, auprc_pu = _get_metrics(*validation_set['PathMeUniverse'])
                except ValueError:
                    auroc_sg, auprc_sg = (0, 0)
                    auroc_pu, auprc_pu = (0, 0)
                    print(f'ROC AUC unable to calculate for {validation_set}')

            auroc_metrics['PathMeUniverse'][type].append(auroc_pu)
            auprc_metrics['PathMeUniverse'][type].append(auprc_pu)

            auroc_metrics['subgraph'][type].append(auroc_sg)
            auprc_metrics['subgraph'][type].append(auprc_sg)

    return auroc_metrics, auprc_metrics


"""Helper functions for random cross-validation"""


def _generate_random_score_ranking(background_mat: Matrix) -> Matrix:
    """Generate random scores.

    :param mapping_input: List or value dictionary of labels {'label':value}.
    :param kernels: Network stratified as a dictionary  {'kernel-tile':kernel}.
    :param universe_kernel: Network as an integrated kernel.
    :param z_normalization: Flag for the statistical normalization option.
    :param k: Iterations for the repeated_holdout validation.
    """
    return Matrix(
        mat=np.array([np.random.rand(len(background_mat.rows_labels))]).T,
        rows_labels=background_mat.rows_labels,
        cols_labels=['Radom_Baseline'],
    )


def _get_random_cv_split_input_and_validation(input: Union[list, set],
                                              background_mat: Matrix
                                              ) -> Tuple[Matrix, Matrix]:
    """Get random CV split.

    :param input: Label set to split.
    :param background_mat: Network as a kernel.
    """
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


def _get_metrics(validation_labels: Union[Matrix, np.ndarray],
                 scores: Union[Matrix, np.ndarray]
                 ):
    """Return metrics.

    :param validation_labels: Validation scores set.
    :param scores: Train-diffued scores set.
    """
    if isinstance(validation_labels, Matrix):
        validation_labels = validation_labels.mat
    if isinstance(scores, Matrix):
        scores = scores.mat

    return metrics.roc_auc_score(validation_labels, scores), metrics.average_precision_score(validation_labels, scores)
