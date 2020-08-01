# -*- coding: utf-8 -*-

"""Command line interface."""

import json
import logging
from collections import defaultdict
from typing import Optional

import click
from bio2bel.constants import get_global_connection
from diffupath.utils import reduce_dict_dimension, reduce_dict_two_dimensional, subvert_twodim_dict
from diffupy.constants import EMOJI, RAW, CSV, JSON
from diffupy.diffuse import diffuse as run_diffusion
from diffupy.kernels import regularised_laplacian_kernel
from diffupy.process_input import process_map_and_format_input_data_for_diff
from diffupy.process_network import get_kernel_from_network_path, process_kernel_from_file, process_graph_from_file
from diffupy.utils import from_json, to_json
from pybel import get_subgraph_by_annotation_value
from tqdm import tqdm

from .constants import *
from .cross_validation import cross_validation_by_method, cross_validation_by_subgraph

logger = logging.getLogger(__name__)

GRAPH_PATH = os.path.join(DEFAULT_DIFFUPATH_DIR, 'pickles', 'universe',
                          'pathme_universe_non_flatten_collapsed_names_no_isolates_16_03_2020.pickle')
KERNEL_PATH = os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels', 'kernel_regularized_pathme_universe.pickle')


@click.group(help='DiffuPath')
def main():
    """Run DiffuPath."""
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


@main.group()
def diffusion():
    """Commands for running diffusion experiments."""


@diffusion.command()
@click.option(
    '-i', '--input',
    help='Path to a (miscellaneous format) data input to be processed/formatted.',
    required=True,
    type=click.Path(exists=True, dir_okay=True)
)
@click.option(
    '-n', '--network',
    help='Path to the network as a graph or as a kernel. By default "KERNEL_PATH", pointing to PathMeUniverse kernel',
    default=KERNEL_PATH,
    type=click.Path(exists=True, dir_okay=True)
)
@click.option(
    '-o', '--output',
    type=click.File('w'),
    help='Path (with file name) for the generated scores output file. By default "$OUTPUT/diffusion_scores.csv"',
    default=os.path.join(OUTPUT_DIR, 'diffusion_scores_on_pathme.csv'),
)
@click.option(
    '-m', '--method',
    help='Method to elect among ["raw", "ml", "gm", "ber_s", "ber_p", "mc", "z"]. By default "raw"',
    type=click.Choice(METHODS),
    default=RAW,
    show_default=True,
)
@click.option(
    '-b', '--binarize',
    help='If logFC provided in dataset, convert logFC to binary (e.g., up-regulated entities to 1, down-regulated to '
         '-1). For scoring methods that accept quantitative values (i.e., raw & z), node labels can also be codified '
         'with LogFC (in this case, set binarize==False).',
    type=bool,
    default=False,
    show_default=True,
)
@click.option(
    '-t', '--threshold',
    help='Codify node labels by applying a threshold to logFC in input. By default None',
    default=None,
    type=float,
)
@click.option(
    '-a', '--absolute_value',
    help='Codify node labels by applying threshold to | logFC | in input. By default False',
    type=bool,
    default=False,
    show_default=True,
)
@click.option(
    '-p', '--p_value',
    help='Statistical significance (p-value).',
    type=float,
    default=0.05,
    show_default=True,
)
@click.option(
    '-f', '--format_output',
    help='Choose CSV or JSON output scores file format.',
    type=str,
    default=CSV,
    show_default=True,
)
def run(
        input: str,
        network: Optional[str] = KERNEL_PATH,
        output: Optional[str] = os.path.join(OUTPUT_DIR, 'diffusion_scores_on_pathme.csv'),
        method: Optional[str] = RAW,
        binarize: Optional[bool] = False,
        threshold: Optional[float] = None,
        absolute_value: Optional[bool] = False,
        p_value: Optional[float] = 0.05,
        format_output: Optional[str] = CSV
):
    """Run a diffusion method for the provided input_scores over (by default) PathMeUniverse integrated network.

    :param input: Path to a (miscellaneous format) data input to be processed/formatted.
    :param network: Path to the network as a graph or as a kernel. By default 'KERNEL_PATH', pointing to PathMeUniverse kernel
    :param output: Path (with file name) for the generated scores output file. By default '$OUTPUT/diffusion_scores.csv'
    :param method:  Elected method ["raw", "ml", "gm", "ber_s", "ber_p", "mc", "z"]. By default 'raw'
    :param binarize: If logFC provided in dataset, convert logFC to binary. By default False
    :param threshold: Codify node labels by applying a threshold to logFC in input. By default None
    :param absolute_value: Codify node labels by applying threshold to | logFC | in input. By default False
    :param p_value: Statistical significance. By default 0.05
    :param format_output: Elected output format ["CSV", "JSON"]. By default "CSV"'

    """
    click.secho(f'{EMOJI} Loading graph from {network} {EMOJI}')

    kernel = get_kernel_from_network_path(network)

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

    results = run_diffusion(
        input_scores_dict,
        method,
        k=kernel
    )

    if format_output == CSV:
        results.to_csv(output)

    elif format_output == JSON:
        json.dump(results, output, indent=2)

    click.secho(f'{EMOJI} Diffusion performed with success. Output located at {output} {EMOJI}\n')


@diffusion.command()
@click.option(
    '-c', '--comparison',
    help='Comparison method',
    default=BY_METHOD,
    show_default=True,
    type=click.Choice(EVALUATION_COMPARISONS),
)
@click.option(
    '-d', '--data_path',
    default=os.path.join(ROOT_RESULTS_DIR, 'data', 'input_mappings'),
    show_default=True,
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
)
@click.option(
    '-k', '--kernel',
    help='Path to the kernel',
    default=GRAPH_PATH,
    type=click.Path(exists=True, dir_okay=False)
)
@click.option(
    '-g', '--graph',
    help='Path to the network as a graph',
    default=KERNEL_PATH,
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    '-o', '--output',
    help='Output path for the results',
    default=os.path.join(OUTPUT_DIR, 'evaluation_metrics.json'),
    show_default=True,
    type=click.Path(dir_okay=True, file_okay=False),
)
@click.option(
    '-i', '--iterations',
    help='Number of distinct cross validations',
    default=25,
    show_default=True,
    type=int,
)
def evaluate(
        comparison: Optional[str] = BY_METHOD,
        data_path: Optional[str] = os.path.join(ROOT_RESULTS_DIR, 'data', 'input_mappings'),
        graph: Optional[str] = GRAPH_PATH,
        kernel: Optional[str] = KERNEL_PATH,
        output: Optional[str] = OUTPUT_DIR,
        iterations: Optional[int] = 100,
):
    """Evaluate a kernel/network on one of the three presented datasets.

    :param comparison: Elected comparison ["by_method", "by_database", "by_entity_type"]. By default 'by_method'
    :param data_path: Path to a DIRECTORY with a set of preprocessed and mapped data inputs in .json.
    :param graph: Path to the network as a (NetworkX) graph.
    :param kernel: Path to the network kernel (diffuPy.Matrix type).
    :param output: Path (with file name) for the generated scores output file. By default '$OUTPUT/diffusion_scores.csv'
    :param iterations: Number of iterations of the Cross-Validation.

    """
    click.secho(f'{EMOJI} Loading network for random cross-validation... {EMOJI}')

    graph = process_graph_from_file(graph)
    kernel = process_kernel_from_file(kernel)

    click.secho(f'{EMOJI} Loading data for cross-validation... {EMOJI}')

    MAPPING_PATH_DATASET_1 = os.path.join(data_path, 'dataset_1_mapping_absolute_value.json')
    dataset1_mapping_by_database_and_entity = from_json(MAPPING_PATH_DATASET_1)

    MAPPING_PATH_DATASET_2 = os.path.join(data_path, 'dataset_2_mapping.json')
    dataset2_mapping_by_database_and_entity = from_json(MAPPING_PATH_DATASET_2)

    MAPPING_PATH_DATASET_3 = os.path.join(data_path, 'dataset_3_mapping.json')
    dataset3_mapping_by_database_and_entity = from_json(MAPPING_PATH_DATASET_3)

    if comparison == BY_METHOD:
        dataset1_mapping_all_labels = reduce_dict_two_dimensional(dataset1_mapping_by_database_and_entity)
        dataset2_mapping_all_labels = reduce_dict_two_dimensional(dataset2_mapping_by_database_and_entity)
        dataset3_mapping_all_labels = reduce_dict_two_dimensional(dataset3_mapping_by_database_and_entity)

        click.secho(f'{EMOJI} Evaluating by method... {EMOJI}')

        metrics = defaultdict(lambda: defaultdict(lambda: list))

        click.secho(f'{EMOJI} Running cross_validation_by_method for Dataset 1... {EMOJI}')
        metrics['auroc']['Dataset 1'], metrics['auprc']['Dataset 1'] = cross_validation_by_method(
            dataset1_mapping_all_labels,
            graph,
            kernel,
            k=iterations)

        click.secho(f'{EMOJI} Running cross_validation_by_method for Dataset 2... {EMOJI}')
        metrics['auroc']['Dataset 2'], metrics['auprc']['Dataset 2'] = cross_validation_by_method(
            dataset2_mapping_all_labels,
            graph,
            kernel,
            k=iterations)

        click.secho(f'{EMOJI} Running cross_validation_by_method for Dataset 3... {EMOJI}')
        metrics['auroc']['Dataset 3'], metrics['auprc']['Dataset 3'] = cross_validation_by_method(
            dataset3_mapping_all_labels,
            graph,
            kernel,
            k=iterations)

    elif comparison == BY_DB:
        dataset1_mapping_all_labels = reduce_dict_two_dimensional(dataset1_mapping_by_database_and_entity)
        dataset2_mapping_all_labels = reduce_dict_two_dimensional(dataset2_mapping_by_database_and_entity)
        dataset3_mapping_all_labels = reduce_dict_two_dimensional(dataset3_mapping_by_database_and_entity)

        click.secho(f'{EMOJI} Evaluating by data_base... {EMOJI}')

        # Pre-process kernel for subgraphs
        kernels = {parameter: regularised_laplacian_kernel(get_subgraph_by_annotation_value(graph,
                                                                                            'database',
                                                                                            parameter)
                                                           )
                   for parameter in tqdm(['kegg', 'reactome', 'wikipathways'], 'Generate kernels from subgraphs')
                   }

        metrics = defaultdict(lambda: defaultdict(lambda: list))

        click.secho(f'{EMOJI} Running cross_validation_by_database for Dataset 1... {EMOJI}')
        metrics['auroc']['Dataset 1'], metrics['auprc']['Dataset 1'] = cross_validation_by_subgraph(
            dataset1_mapping_all_labels,
            kernels,
            universe_kernel=kernel,
            k=iterations)

        click.secho(f'{EMOJI} Running cross_validation_by_database for Dataset 2... {EMOJI}')
        metrics['auroc']['Dataset 2'], metrics['auprc']['Dataset 2'] = cross_validation_by_subgraph(
            dataset2_mapping_all_labels,
            kernels,
            universe_kernel=kernel,
            k=iterations)

        click.secho(f'{EMOJI} Running cross_validation_by_database for Dataset 3... {EMOJI}')
        metrics['auroc']['Dataset 3'], metrics['auprc']['Dataset 3'] = cross_validation_by_subgraph(
            dataset3_mapping_all_labels,
            kernels,
            universe_kernel=kernel,
            k=iterations)

    elif comparison == BY_ENTITY_METHOD:
        dataset1_mapping_by_entity = reduce_dict_dimension(subvert_twodim_dict(dataset1_mapping_by_database_and_entity))
        dataset2_mapping_by_entity = reduce_dict_dimension(subvert_twodim_dict(dataset2_mapping_by_database_and_entity))
        dataset3_mapping_by_entity = reduce_dict_dimension(subvert_twodim_dict(dataset3_mapping_by_database_and_entity))

        metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: list)))

        click.secho(f'{EMOJI} Running cross_validation_by_method stratified by omic for Dataset 1... {EMOJI}')

        for entity_type, entity_set in dataset1_mapping_by_entity.items():
            if len(entity_set) > 2:
                click.secho(f'{EMOJI} Running cross_validation_by_method for {entity_type}... {EMOJI}')
                metrics['auroc']['Dataset 1'][entity_type], metrics['auprc']['Dataset 1'][
                    entity_type] = cross_validation_by_method(
                    entity_set,
                    graph,
                    kernel,
                    k=iterations
                )

        click.secho(f'{EMOJI} Running cross_validation_by_method stratified by omic for Dataset 2... {EMOJI}')

        for entity_type, entity_set in dataset2_mapping_by_entity.items():
            if len(entity_set) > 2:
                click.secho(f'{EMOJI} Running cross_validation_by_method for {entity_type}... {EMOJI}')
                metrics['auroc']['Dataset 2'][entity_type], metrics['auprc']['Dataset 2'][
                    entity_type] = cross_validation_by_method(
                    entity_set,
                    graph,
                    kernel,
                    k=iterations
                )

        click.secho(f'{EMOJI} Running cross_validation_by_method stratified by omic for Dataset 3... {EMOJI}')

        for entity_type, entity_set in dataset3_mapping_by_entity.items():
            if len(entity_set) > 2:
                click.secho(f'{EMOJI} Running cross_validation_by_method for {entity_type}... {EMOJI}')
                metrics['auroc']['Dataset 3'][entity_type], metrics['auprc']['Dataset 3'][
                    entity_type] = cross_validation_by_method(
                    entity_set,
                    graph,
                    kernel,
                    k=iterations
                )


    elif comparison == BY_ENTITY_DB:
        dataset1_mapping_by_entity = reduce_dict_dimension(subvert_twodim_dict(dataset1_mapping_by_database_and_entity))
        dataset2_mapping_by_entity = reduce_dict_dimension(subvert_twodim_dict(dataset2_mapping_by_database_and_entity))
        dataset3_mapping_by_entity = reduce_dict_dimension(subvert_twodim_dict(dataset3_mapping_by_database_and_entity))

        # Pre-process kernel for subgraphs
        kernels = {parameter: regularised_laplacian_kernel(get_subgraph_by_annotation_value(graph,
                                                                                            'database',
                                                                                            parameter)
                                                           )
                   for parameter in tqdm(['kegg', 'reactome', 'wikipathways'],
                                         'Generate kernels from subgraphs')
                   }

        metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: list)))

        click.secho(f'{EMOJI} Running cross_validation_by_database stratified by omic for Dataset 1... {EMOJI}')

        for entity_type, entity_set in dataset1_mapping_by_entity.items():
            if len(entity_set) > 2:
                click.secho(f'{EMOJI} Running cross_validation_by_database for {entity_type}... {EMOJI}')
                metrics[entity_type]['auroc']['Dataset 1'], metrics[entity_type]['auprc'][
                    'Dataset 1'] = cross_validation_by_subgraph(
                    entity_set,
                    kernels,
                    universe_kernel=kernel,
                    k=iterations)

        click.secho(f'{EMOJI} Running cross_validation_by_database stratified by omic for Dataset 2... {EMOJI}')

        for entity_type, entity_set in dataset2_mapping_by_entity.items():
            if len(entity_set) > 2:
                click.secho(f'{EMOJI} Running cross_validation_by_database for {entity_type}... {EMOJI}')
                metrics[entity_type]['auroc']['Dataset 2'], metrics[entity_type]['auprc'][
                    'Dataset 2'] = cross_validation_by_subgraph(
                    entity_set,
                    kernels,
                    universe_kernel=kernel,
                    k=iterations)

        click.secho(f'{EMOJI} Running cross_validation_by_database stratified by omic for Dataset 3... {EMOJI}')

        for entity_type, entity_set in dataset3_mapping_by_entity.items():
            if len(entity_set) > 2:
                click.secho(f'{EMOJI} Running cross_validation_by_database for {entity_type}... {EMOJI}')
                metrics[entity_type]['auroc']['Dataset 3'], metrics[entity_type]['auprc'][
                    'Dataset 3'] = cross_validation_by_subgraph(
                    entity_set,
                    kernels,
                    universe_kernel=kernel,
                    k=iterations)


    else:
        raise ValueError("The indicated comparison method do not match any provided method.")

    to_json(metrics, output)

    click.secho(f'{EMOJI} Random cross-validation performed with success. Output located at {output}... {EMOJI}')


@main.group()
def database():
    """Commands related to available databases."""


@database.command()
def ls():
    """Print the list of the available databases."""
    click.secho(f'{EMOJI} Available databases {DATABASES}')


@database.command()
@click.option(
    '-d', '--database',
    help='Database',
    type=click.Choice(DATABASES),
    required=True,
)
@click.option(
    '-c',
    '--connection',
    default=get_global_connection(),
    show_default=True,
    help='Bio2BEL database connection string',
)
@click.option('-v', '--verbose', count=True)
def get_database(database: str, connection: str, verbose: bool):
    """Generate a network for a given database."""
    if verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif verbose == 2:
        logging.basicConfig(level=logging.DEBUG)

    from .database import install_and_populate_database

    click.secho(f'{EMOJI} Exporting {database}')
    install_and_populate_database(database, connection)


if __name__ == '__main__':
    main()
