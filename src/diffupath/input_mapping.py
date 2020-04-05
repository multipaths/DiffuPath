# -*- coding: utf-8 -*-

"""Input mapping."""

import logging
from typing import Set, Tuple

import networkx as nx
from diffupy.kernels import regularised_laplacian_kernel
from diffupy.matrix import Matrix
from diffupy.process_input import generate_categoric_input_from_labels
from diffupy.utils import process_kernel_from_cli, process_network_from_cli, print_dict_dimensions

from .constants import EMOJI
from .utils import get_labels_set_from_dict, check_substrings

logger = logging.getLogger(__name__)


def get_mapping(
    to_map: Set,
    background_map: Set,
    mirnas=None,
    mirnas_mapping=None,
    submapping=None,
    title='',
    print_percentage=False,
):
    intersection = to_map.intersection(background_map)

    if mirnas and title in ['micrornas', 'Micrornas', 'mirna_nodes']:
        mirnas_substring = [e for e in check_substrings(mirnas, background_map) if 'mir' in e]
        intersection = intersection.union(mirnas_substring)

    if mirnas_mapping:
        intersection = intersection.union(mirnas_mapping.intersection(to_map))

    if submapping:
        intersection = intersection.intersection(submapping)

    if len(intersection) != 0 and print_percentage:
        print(f'{title} ({str(len(intersection))}) {(len(intersection) / len(to_map)) * 100}%')

    return intersection


def get_mapping_subsets(
    subsets_dict,
    map_labels,
    title,
    percentage_reference_labels=False,
    submapping=None,
    mirnas=None,
    mirnas_mapping=None,
    relative_statistics=None,
):
    entity_type_map = {'metabolite_nodes': 'metabolite', 'mirna_nodes': 'micrornas', 'gene_nodes': 'genes',
                       'bp_nodes': 'bps'}
    mapping_dict = {}
    total_entites = set()

    print('Mapping by ' + title + ':')

    if not isinstance(map_labels, set) and not isinstance(map_labels, list):
        raise Exception('map_labels must be a set or a list.')

    for type_name, entites in subsets_dict.items():

        # TODO: Mapping substring not other than mirnas

        mapping = get_mapping(entites,
                              map_labels,
                              mirnas=mirnas,
                              mirnas_mapping=mirnas_mapping,
                              title=type_name,
                              submapping=submapping)

        percentage = 0

        if percentage_reference_labels:
            percentage = len(mapping) / len(map_labels)
        elif relative_statistics:
            subset_len = len(relative_statistics[entity_type_map[type_name]])
            if subset_len != 0:
                percentage = len(mapping) / subset_len
        else:
            if len(entites) != 0:
                percentage = len(mapping) / len(entites)

        print(f'{type_name} ({str(len(mapping))}) {percentage * 100}%')

        mapping_dict[type_name] = (mapping, percentage)

        total_entites.update(mapping)

    total_dimention = len(total_entites)

    if percentage_reference_labels:
        percentage = total_dimention / len(map_labels)

    else:
        percentage = total_dimention / len(get_labels_set_from_dict(subsets_dict))

    print(f'Total ({total_dimention}) {percentage * 100}% \n')

    return mapping_dict, percentage, total_entites


def get_mapping_two_dim_subsets(
    two_dimentional_dict,
    map_labels,
    background_labels=None,
    percentage_reference_background_labels=False,
    mirnas=None,
    relative_statistics=None,
    mirnas_mapping=None,
):
    mapping_dict = {}
    total_entites = set()

    for subset_title, subsets_dict in two_dimentional_dict.items():
        mapping, percentage, entites = get_mapping_subsets(
            subsets_dict,
            map_labels,
            relative_statistics=relative_statistics,
            submapping=background_labels,
            mirnas=mirnas,
            mirnas_mapping=mirnas_mapping,
            title=subset_title.capitalize(),
        )

        mapping_dict[subset_title] = (mapping, percentage)
        total_entites.update(entites)

    total_dimention = len(total_entites)

    if percentage_reference_background_labels:
        total_percentage = total_dimention / len(background_labels)
    else:
        total_percentage = total_dimention / len(map_labels)

    print(f'Total ({total_dimention}) {total_percentage * 100}% \n')

    return mapping_dict, total_percentage, total_dimention


def process_input_from_cli(
    parse_set_funct,
    network_path,
    input_path,
    graph: bool = False,
    quantitative: bool = False,
) -> Tuple[Matrix, Matrix, set, nx.Graph]:
    """Process input from cli."""
    logger.info(f'{EMOJI} Loading networs (as graph or kernel) from {network_path} {EMOJI}')

    # Load label_input from dataset
    # TODO: Consider universal label_input processing, now parse set specific function by parameter, use from diffuPy process_input
    # input_scores = _process_input(input_path)
    dataset_labels_by_omics = parse_set_funct(input_path)
    dataset_all_labels = get_labels_set_from_dict(dataset_labels_by_omics)

    print_dict_dimensions(dataset_labels_by_omics, 'Dataset imported labels:')

    mirnas_dataset = dataset_labels_by_omics['micrornas']

    # Load background network from the label_input graph (if indicated as flag) or kernel
    if graph:
        graph = process_network_from_cli(network_path)

        logger.info(
            f'{EMOJI} Graph loaded with: \n'
            f'{graph.number_of_nodes()} nodes\n'
            f'{graph.number_of_edges()} edges\n'
            f'{EMOJI}'
        )

        # Generate the kernel from the label_input graph
        kernel = regularised_laplacian_kernel(graph)

    else:
        kernel = process_kernel_from_cli(network_path)

        logger.info(
            f'{EMOJI} Kernel loaded with: \n'
            f'{len(kernel.rows_labels)} nodes\n'
            f'{EMOJI}'
        )

    background_labels = kernel.rows_labels

    # Dataset label mapping to the network
    mapping_scores = get_mapping(
        dataset_all_labels,
        background_labels,
        title='Global mapping: ',
        mirnas=mirnas_dataset,
        print_percentage=True,
    )

    # Format label_input as Matrix for run_diffusion
    if quantitative:
        # TODO: Import from label_input column continuous scores as in diffuPy process_input
        # Generate label_input as a categoric label_input from labels
        input_scores = generate_categoric_input_from_labels(
            mapping_scores,
            'label_input with hidden true positives',
            kernel,
        )
    else:
        input_scores = generate_categoric_input_from_labels(
            mapping_scores,
            'label_input with hidden true positives',
            kernel,
        )

    return input_scores, kernel, mapping_scores, graph
