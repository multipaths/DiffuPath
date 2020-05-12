# -*- coding: utf-8 -*-

"""Command line interface."""

import json
import logging
import sys
from collections import defaultdict

import click
import networkx as nx
from bio2bel.constants import get_global_connection
from diffupath.utils import reduce_dict_dimension
from diffupy.constants import EMOJI, RAW, CSV, JSON
from diffupy.diffuse import diffuse as run_diffusion
from diffupy.process_input import process_map_and_format_input_data_for_diff
from diffupy.process_network import get_kernel_from_network_path, process_kernel_from_file, process_graph_from_file
from diffupy.utils import from_json, to_json

from .constants import *
from .cross_validation import cross_validation_by_method

logger = logging.getLogger(__name__)

GRAPH_PATH = os.path.join(DEFAULT_DIFFUPATH_DIR, 'pickles', 'universe',
                          'pathme_universe_non_flatten_collapsed_names_no_isolates_16_03_2020.pickle')
KERNEL_PATH = os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels', 'kernel_regularized_pathme_universe.pickle')


@click.group(help='DiffuPy')
def main():
    """Run DiffuPy."""
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


@main.group()
def diffusion():
    """Commands for running diffusion experiments."""


@diffusion.command()
@click.option(
    '-i', '--input',
    help='Input data',
    required=True,
    type=click.Path(exists=True, dir_okay=True)
)
@click.option(
    '-n', '--network',
    help='Path to the network graph or kernel',
    default=KERNEL_PATH,
    type=click.Path(exists=True, dir_okay=True)
)
@click.option(
    '-o', '--output',
    type=click.File('w'),
    help="Output file",
    default=sys.stdout,
)
@click.option(
    '-m', '--method',
    help='Diffusion method',
    type=click.Choice(METHODS),
    default=RAW,
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
    help='Codify node labels by applying a threshold to logFC in input.',
    default=None,
    type=float,
)
@click.option(
    '-a', '--absolute_value',
    help='Codify node labels by applying threshold to | logFC | in input. If absolute_value is set to False,'
         'node labels will be signed.',
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
    '-f', '--output_format',
    help='Statistical significance (p-value).',
    type=float,
    default=CSV,
    show_default=True,
)
def run(
    input: str,
    network: str = KERNEL_PATH,
    output: str = OUTPUT_DIR,
    method: str = RAW,
    binarize: bool = False,
    threshold: float = None,
    absolute_value: bool = False,
    p_value: float = 0.05,
    output_format: str = CSV
):
    """Run a diffusion method over a network or pre-generated kernel."""
    click.secho(f'{EMOJI} Loading graph from {network} {EMOJI}')

    kernel = get_kernel_from_network_path(network)

    click.secho(f'Processing data input from {input}.')

    input_scores_dict = process_map_and_format_input_data_for_diff(input,
                                                                   kernel,
                                                                   method,
                                                                   binarize,
                                                                   absolute_value,
                                                                   p_value,
                                                                   threshold,
                                                                   )

    click.secho(f'Computing the diffusion algorithm.')

    results = run_diffusion(
        input_scores_dict,
        method,
        k=kernel
    )

    if output_format is CSV:
        results.to_csv(output)

    elif output_format is JSON:
        json.dump(results, output, indent=2)

    click.secho(f'{EMOJI} Diffusion performed with success. Output located at {output} {EMOJI}')


@diffusion.command()
@click.option(
    '-c', '--comparison',
    help='Comparison method',
    default=BY_METHOD,
    show_default=True,
    type=click.Choice(EVALUATION_COMPARISONS),
)
@click.option(
    '-i', '--input_path',
    default=os.path.join(ROOT_RESULTS_DIR, 'data', 'input_mappings'),
    show_default=True,
    type=click.Path(exists=True, dir_okay=True),
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
    default=OUTPUT_DIR,
    show_default=True,
    type=click.Path(exists=True, file_okay=False),
)
@click.option(
    '-i', '--iterations',
    help='Number of distinct cross validations',
    default=25,
    show_default=True,
    type=int,
)
def evaluate(
    comparison: str = BY_METHOD,
    input_path: str = os.path.join(ROOT_RESULTS_DIR, 'data', 'input_mappings'),
    graph: str = GRAPH_PATH,
    kernel: str = KERNEL_PATH,
    output: str = OUTPUT_DIR,
    iterations: int = 100,
):
    """Evaluate a kernel/network on one of the three presented datasets."""
    click.secho(f'{EMOJI} Loading network for random cross-validation... {EMOJI}')
    graph = process_graph_from_file(graph)
    kernel = process_kernel_from_file(kernel)

    nx.number_of_isolates(graph)
    graph.remove_nodes_from({
        node
        for node in nx.isolates(graph)
    })

    graph.summarize()

    click.secho(f'{EMOJI} Loading data for cross-validation... {EMOJI}')
    MAPPING_PATH_DATASET_1 = os.path.join(input_path, 'dataset_1_mapping.json')
    dataset1_mapping_by_database_and_entity = from_json(MAPPING_PATH_DATASET_1)
    dataset1_mapping_by_database = reduce_dict_dimension(dataset1_mapping_by_database_and_entity)
    dataset1_mapping_all_labels = {entity: entity_value
                                   for entity_type, entity_set in dataset1_mapping_by_database.items()
                                   for entity, entity_value in entity_set.items()
                                   }

    MAPPING_PATH_DATASET_2 = os.path.join(input_path, 'dataset_2_mapping.json')
    dataset2_mapping_by_database_and_entity = from_json(MAPPING_PATH_DATASET_2)
    dataset2_mapping_by_database = reduce_dict_dimension(dataset2_mapping_by_database_and_entity)
    dataset2_mapping_all_labels = {entity: entity_value
                                   for entity_type, entity_set in dataset2_mapping_by_database.items()
                                   for entity, entity_value in entity_set.items()
                                   }

    MAPPING_PATH_DATASET_3 = os.path.join(input_path, 'dataset_3_mapping.json')
    dataset3_mapping_by_database_and_entity = from_json(MAPPING_PATH_DATASET_3)
    dataset3_mapping_by_database = reduce_dict_dimension(dataset3_mapping_by_database_and_entity)
    dataset3_mapping_all_labels = {entity: entity_value
                                   for entity_type, entity_set in dataset3_mapping_by_database.items()
                                   for entity, entity_value in entity_set.items()
                                   }

    if comparison == BY_METHOD:
        click.secho(f'{EMOJI} Evaluating by method... {EMOJI}')

        metrics_by_method = defaultdict(lambda: defaultdict(lambda: list))

        click.secho(f'{EMOJI} Running cross_validation_by_method for Dataset 1... {EMOJI}')
        metrics_by_method['auroc']['Dataset 1'], metrics_by_method['auprc']['Dataset 1'] = cross_validation_by_method(
            dataset1_mapping_all_labels,
            graph,
            kernel,
            k=iterations)

        click.secho(f'{EMOJI} Running cross_validation_by_method for Dataset 2... {EMOJI}')
        metrics_by_method['auroc']['Dataset 2'], metrics_by_method['auprc']['Dataset 2'] = cross_validation_by_method(
            dataset2_mapping_all_labels,
            graph,
            kernel,
            k=iterations)

        click.secho(f'{EMOJI} Running cross_validation_by_method for Dataset 3... {EMOJI}')
        metrics_by_method['auroc']['Dataset 3'], metrics_by_method['auprc']['Dataset 3'] = cross_validation_by_method(
            dataset3_mapping_all_labels,
            graph,
            kernel,
            k=iterations)
    else:
        raise ValueError("The comparison method provided not match any provided method.")

    to_json(metrics_by_method, os.path.join(output, 'results.json'))

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
