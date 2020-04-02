# -*- coding: utf-8 -*-

"""Command line interface."""

import json
import logging

import click
from bio2bel.constants import get_global_connection
from diffupath.input_mapping import get_mapping
from diffupath.utils import get_labels_set_from_dict
from diffupath.validation_datasets_parsers import parse_set1

from diffupy.diffuse import diffuse as run_diffusion
from diffupy.kernels import regularised_laplacian_kernel
from diffupy.process_input import generate_categoric_input_from_labels
from diffupy.utils import process_network_from_cli, process_kernel_from_cli, print_dict_dimensions, \
    get_label_list_graph
from .constants import *

logger = logging.getLogger(__name__)


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
    type=click.Path(exists=True, dir_okay=False)
)
@click.option(
    '-c', '--categoric',
    help='Generate categorical input from labels',
    show_default=False,
    is_flag=False
)
@click.option(
    '-n', '--network',
    help='Path to the network graph or kernel',
    default=os.path.join(DEFAULT_DIFFUPY_DIR, 'kernels', 'kernel_regularized_pathme_universe.pickle'),
    show_default=True,
    type=click.Path(exists=True, dir_okay=False)
)
@click.option(
    '-g', '--graph',
    help='Network provided as a graph',
    show_default=False,
    is_flag=False
)
@click.option(
    '-m', '--method',
    help='Difussion method',
    default='raw',
    show_default=True,
    type=click.Choice(DIFFUPY_METHODS),
)
@click.option(
    '-o', '--output',
    help='Output path for the results',
    default=OUTPUT_DIR,
    show_default=True,
    type=click.Path(exists=True, file_okay=False)
)
def run(
        input: str,
        categoric: bool = False,
        network: str = os.path.join(DEFAULT_DIFFUPY_DIR, 'kernels', 'kernel_regularized_pathme_universe.pickle'),
        graph: bool = False,
        method: str = 'raw',
        output: str = OUTPUT_DIR,
):
    """Run a diffusion method given an input over a network or a pre-generated kernel."""
    click.secho(f'{EMOJI} Running diffusion... {EMOJI}')

    click.secho(f'{EMOJI} Loading graph from {network} {EMOJI}')

    # Load input from dataset
    # TODO: Universal input processing, now parse set 1 specific, use from diffuPy process_input
    # input_scores = _process_input(input)
    dataset_labels_by_omics = parse_set1(input)
    dataset1_all_labels = get_labels_set_from_dict(dataset_labels_by_omics)

    print_dict_dimensions(dataset_labels_by_omics, 'Dataset1 imported labels:')

    mirnas_dataset = dataset_labels_by_omics['micrornas']

    # Load background network from the input graph (if indicated as flag) or kernel
    if graph:
        graph = process_network_from_cli(network)

        click.secho(
            f'{EMOJI} Graph loaded with: \n'
            f'{graph.number_of_nodes()} nodes\n'
            f'{graph.number_of_edges()} edges\n'
            f'{EMOJI}'
        )

        # Generate the kernel from the input graph
        k = regularised_laplacian_kernel(graph)

    else:
        k = process_kernel_from_cli(network)

        click.secho(
            f'{EMOJI} Kernel loaded with: \n'
            f'{len(k.rows_labels)} nodes\n'
            f'{EMOJI}'
        )

    background_labels = k.rows_labels

    # Dataset label mapping to the network
    mapping_scores = get_mapping(dataset1_all_labels,
                                 background_labels,
                                 title='Global mapping: ',
                                 mirnas=mirnas_dataset,
                                 print_percentage=True
                                 )

    # Format input
    if categoric:
        # Generate input as a categoric input from labels
        input_scores = generate_categoric_input_from_labels(mapping_scores,
                                                            'input with hidden true positives',
                                                            k
                                                            )
    else:
        #TODO: Import from input column continuous scores as in diffuPy process_input
        input_scores = generate_categoric_input_from_labels(mapping_scores,
                                                            'input with hidden true positives',
                                                            k
                                                            )

    # Perform/run diffusion
    results = run_diffusion(
        input_scores,
        method,
        k=k,
    )

    # Export diffusion scores as a csv data file
    results.to_csv(output)


@main.group()
def database():
    """Commands for generating networks from biological databases."""


@database.command()
def ls():
    """Get network for database."""
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
def network(database: str, connection: str, verbose: bool):
    """Get network for database."""
    if verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif verbose == 2:
        logging.basicConfig(level=logging.DEBUG)

    from .database import install_and_populate_database

    click.secho(f'{EMOJI} Exporting {database}')
    install_and_populate_database(database, connection)


if __name__ == '__main__':
    main()
