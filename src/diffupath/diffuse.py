# -*- coding: utf-8 -*-

"""Command line interface."""

import json
import logging
from typing import Optional, Union, Callable, List

import click
import networkx as nx
from diffupy.constants import EMOJI, RAW, CSV, JSON, GRAPH_FORMATS
from diffupy.diffuse import diffuse
from diffupy.kernels import regularised_laplacian_kernel
from diffupy.matrix import Matrix
from diffupy.process_input import process_map_and_format_input_data_for_diff
from diffupy.process_network import get_kernel_from_network_path
from pathme.cli import generate_universe

from .constants import *

logger = logging.getLogger(__name__)

GRAPHS_PATH = os.path.join(DEFAULT_DIFFUPATH_DIR, 'graphs', 'universe')
GRAPH_PATH = os.path.join(DEFAULT_DIFFUPATH_DIR, 'graphs', 'universe',
                          'Homo_sapiens_regularized_pathme_universe.pickle')

KERNELS_PATH = os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels')
KERNEL_PATH = os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels', 'Homo_sapiens_kernel_regularized_pathme_universe.pickle')


def run_diffusion(
        input: str,
        network: Optional[str] = None,
        output: Optional[str] = None,
        method: Union[str, Callable] = RAW,
        binarize: Optional[bool] = False,
        threshold: Optional[float] = None,
        absolute_value: Optional[bool] = False,
        p_value: Optional[float] = 0.05,
        format_output: Optional[str] = None,
        kernel_method: Optional[Callable] = regularised_laplacian_kernel,
        database: Optional[Union[List[str], str]] = None,
        filter_network_omic: Optional[List[str]] = None,
        specie: Optional[str] = HSA
):
    """Run a diffusion method for the provided input_scores over (by default) PathMeUniverse integrated network.

    :param input: Path or miscellaneous format data input to be processed/formatted.
    :param network: Path to the network or the network Object, as a (NetworkX) graph or as a (diffuPy.Matrix) kernel. By default 'KERNEL_PATH', pointing to PathMeUniverse kernel
    :param output: Path (with file name) for the generated scores output file. By default '$OUTPUT/diffusion_scores.csv'
    :param method:  Elected method ["raw", "ml", "gm", "ber_s", "ber_p", "mc", "z"]. By default 'raw'
    :param binarize: If logFC provided in dataset, convert logFC to binary. By default False
    :param threshold: Codify node labels by applying a threshold to logFC in input. By default None
    :param absolute_value: Codify node labels by applying threshold to | logFC | in input. By default False
    :param p_value: Statistical significance. By default 0.05
    :param kernel_method: Callable method for kernel computation.
    :param database: List (or a single database str) of selected network databases to construct/filter the network.
    :param filter_network_omic: List of omic network databases to filter the network.
    :param specie: Specie id name to retrieve network and perform diffusion on.
    """

    if not network:
        if specie != HSA:
            click.secho(f'{EMOJI} Loading and processing specie {specie} network for KEGG, Reactome and WP. {EMOJI}')
            for _, _, files in os.walk(os.path.abspath(KERNELS_PATH)):
                kernel_file = '_'.join([specie, 'kernel_regularized_pathme_universe.pickle'])
                if kernel_file in files:
                    network = os.path.join(KERNELS_PATH, kernel_file)
                else:
                    for _, _, files in os.walk(os.path.abspath(GRAPHS_PATH)):
                        graph_file = '_'.join([specie, 'pathme_universe.pickle'])
                        if graph_file not in files:
                            generate_universe(specie=specie)
                        network = os.path.join(GRAPHS_PATH, graph_file)
                        break
                break
        else:
            if filter_network_database or filter_network_omic:
                network = GRAPH_PATH
            else:
                network = KERNEL_PATH

    click.secho(f'{EMOJI} Loading network ')

    if isinstance(network, str):
        click.secho(f'from {network} {EMOJI}')

        kernel = get_kernel_from_network_path(network, False,
                                              filter_network_database,
                                              filter_network_omic,
                                              kernel_method)
    elif isinstance(network, Matrix):
        kernel = network
    else:
        raise IOError(
            f'{EMOJI} The selected network format is not valid neither as a graph or as a kernel. Please ensure you use one of the following formats: '
            f'{GRAPH_FORMATS}'
        )

    if isinstance(network, Matrix):
        kernel = network
    if isinstance(network, nx.Graph):
        kernel = get_kernel_from_graph(filter_graph(network, database, filter_network_omic), kernel_method)

    click.secho(f'{EMOJI} Processing data input from {input}. {EMOJI}')

    input_scores_dict = process_map_and_format_input_data_for_diff(input,
                                                                   kernel,
                                                                   method,
                                                                   binarize,
                                                                   absolute_value,
                                                                   p_value,
                                                                   threshold,
                                                                   )

    click.secho(f'{EMOJI} Computing the diffusion algorithm. {EMOJI}')

    results = diffuse(
        input_scores_dict,
        method,
        k=kernel
    )

    click.secho(f'{EMOJI} Diffusion performed with success.{EMOJI}\n')

    if not format_output and not output:
        return results

    elif format_output == CSV or output:
        results.as_csv(output)

    elif format_output == JSON:
        json.dump(results, output, indent=2)

    click.secho(f'{EMOJI} Diffusion performed with success. Output located at {output} {EMOJI}\n')
