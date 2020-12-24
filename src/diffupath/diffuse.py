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
from diffupy.process_network import get_kernel_from_network_path, process_graph_from_file, get_kernel_from_graph, \
    filter_graph
from google_drive_downloader import GoogleDriveDownloader
from pathme.cli import generate_universe, universe
from pybel.struct import get_subgraph_by_annotation_value

from .constants import *
from .utils import get_or_create_dir, to_pickle, get_files_list

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
    click.secho(f'{EMOJI} Loading network {EMOJI}')

    if not network:
        if specie != HSA:
            if database and isinstance(database, str):
                database = [database]

            if not database or len(set(database).intersection(PATHME_DB)) == len(database):
                network = _process_network_specie(specie)
            else:
                raise ValueError('Species only covered within PathMe Database.')

        elif database:
            if isinstance(database, str):
                network = _pipeline_network_single_database(database, kernel_method, filter_network_omic)
            elif isinstance(database, list):
                network = _pipeline_network_multiple_database(database, kernel_method, filter_network_omic)
            else:
                raise ValueError('Database selection only as a list or string within available Databases.')
        else:
            network = KERNEL_PATH

    if isinstance(network, str):
        click.secho(f'{EMOJI}Loading from {network} {EMOJI}')

        kernel = get_kernel_from_network_path(network, False,
                                              filter_network_database=database,
                                              filter_network_omic=filter_network_omic,
                                              kernel_method=kernel_method)

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

    click.secho(f'{EMOJI} utput located at {output} {EMOJI}\n')


"""Pipeline for process/generate network either by given specie, database or enntity-type/omic."""


def _process_network_specie(specie: str) -> str:
    """Process network by specie."""
    click.secho(
        f'{EMOJI} Loading and processing specie {specie} network for KEGG, Reactome and WP. {EMOJI}')
    files = get_files_list(path=os.path.join(KERNELS_PATH, universe))

    kernel_file = f'{specie}_kernel_regularized_pathme_universe.pickle'

    if kernel_file in files:
        network = os.path.join(KERNELS_PATH, kernel_file)
    else:
        files = get_files_list(path=GRAPHS_PATH)
        graph_file = f'{specie}_pathme_universe.pickle'

        if graph_file not in files:
            generate_universe(specie=specie)

        network = os.path.join(GRAPHS_PATH, graph_file)

    return network


def _pipeline_network_single_database(database: str, kernel_method: Callable,
                                      filter_network_omic: Union[List, str]) -> Union[Matrix, str]:
    """Process network for a single database."""
    network = None

    db_norm = database.lower().replace(' ', '_')

    if db_norm in list(DATABASE_LINKS.keys()):
        if db_norm in list(PATHME_MAPPING.values()):
            folder = 'pathme'
        else:
            folder = 'by_db'

        kernels_db_path = os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels', folder)
        kernels_files_list = get_or_create_dir(kernels_db_path)

        for kernel in kernels_files_list:
            if db_norm in kernel or db_norm == kernel:
                network = os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels', folder, f'{db_norm}.pickle')
                break

        if not network:
            network = os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels', folder, f'{db_norm}.pickle')
            GoogleDriveDownloader.download_file_from_google_drive(file_id=DATABASE_LINKS[db_norm],
                                                                  dest_path=network,
                                                                  unzip=True)

    elif db_norm in PATHME_DB:
        graph_db_path = os.path.join(DEFAULT_DIFFUPATH_DIR, 'graphs', 'by_db')
        graphs_files_list = get_or_create_dir(graph_db_path)

        if graphs_files_list:
            for graph in graphs_files_list:
                if db_norm in graph or db_norm == graph:
                    network = os.path.join(DEFAULT_DIFFUPATH_DIR, 'graphs', 'by_db', f'{db_norm}.pickle')

        if not network:
            graph = process_graph_from_file(GRAPH_PATH)
            network = get_subgraph_by_annotation_value(graph,
                                                       'database',
                                                       db_norm
                                                       )
            to_pickle(network, os.path.join(DEFAULT_DIFFUPATH_DIR, 'graphs', 'by_db', f'{db_norm}.pickle'))

            if not filter_network_omic:
                click.secho(f'{EMOJI}Generating kernel from {GRAPH_PATH} {EMOJI}')
                network = get_kernel_from_graph(network, kernel_method)
                click.secho(f'{EMOJI}Kernel generated {EMOJI}')

                to_pickle(network,
                          os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels', 'by_db', f'{db_norm}.pickle'))

    else:
        raise ValueError(
            f'Specified Database not found. Please check among the available databases: {list(DATABASE_LINKS.keys())}')

    return network


def _pipeline_network_multiple_database(database: List[str], kernel_method: Callable,
                                        filter_network_omic: Union[List, str]) -> Union[Matrix, str]:
    """Process network for a multiple database."""
    network = None

    db_norm = frozenset([db.lower().replace(' ', '_') for db in database])

    if db_norm in list(PATHME_MAPPING.keys()):
        db_norm = PATHME_MAPPING[db_norm]

        kernels_db_path = os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels', 'pathme')
        kernels_files_list = get_or_create_dir(kernels_db_path)

        for kernel in kernels_files_list:
            if db_norm in kernel or db_norm == kernel:
                network = os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels', 'by_db', f'{db_norm}.pickle')
                break

        if not network:
            network = os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels', 'by_db', f'{db_norm}.pickle')
            GoogleDriveDownloader.download_file_from_google_drive(file_id=DATABASE_LINKS[db_norm],
                                                                  dest_path=network,
                                                                  unzip=True)
    else:
        intersecc_db = db_norm.intersection(PATHME_DB)
        intersecc_db_str = ''

        for db_name in intersecc_db:
            intersecc_db_str += f'_{db_name}'

        if intersecc_db:

            kernels_db_path = os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels', 'by_db')
            kernels_files_list = get_or_create_dir(kernels_db_path)

            for kernel_file in kernels_files_list:
                if intersecc_db_str == kernel_file:
                    network = os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels', 'by_db',
                                           f'{intersecc_db_str}.pickle')
                    break

            if not network:
                graph_db_path = os.path.join(DEFAULT_DIFFUPATH_DIR, 'graphs', 'by_db')
                graphs_files_list = get_or_create_dir(graph_db_path)

                if graphs_files_list:
                    for graph_file in graphs_files_list:
                        if f'{intersecc_db_str}.pickle' == graph_file:
                            network = os.path.join(DEFAULT_DIFFUPATH_DIR, 'graphs', 'by_db',
                                                   f'{intersecc_db_str}.pickle')
                            break

                if not network:
                    graph = process_graph_from_file(GRAPH_PATH)
                    network = get_subgraph_by_annotation_value(graph,
                                                               'database',
                                                               intersecc_db
                                                               )
                    to_pickle(network, os.path.join(DEFAULT_DIFFUPATH_DIR, 'graphs', 'by_db',
                                                    f'{intersecc_db_str}.pickle'))

                    if not filter_network_omic:
                        click.secho(f'{EMOJI}Generating kernel from {GRAPH_PATH} {EMOJI}')
                        network = get_kernel_from_graph(network, kernel_method)
                        click.secho(f'{EMOJI}Kernel generated {EMOJI}')

                        to_pickle(network, os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels', 'by_db',
                                                        f'{db_norm}.pickle'))

        else:
            raise ValueError(
                'Subgraph filtering by database only supported for PathMe network (KEGG, Reactome and Wikipathways).')

    return network
