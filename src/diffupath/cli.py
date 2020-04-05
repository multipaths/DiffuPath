# -*- coding: utf-8 -*-

"""Command line interface."""

import json
import logging
import sys

import click
from bio2bel.constants import get_global_connection
from diffupy.diffuse import diffuse as run_diffusion
from diffupy.process_input import process_input
from diffupy.utils import process_network_from_cli

from .constants import *
from .cross_validation import cross_validation_by_method
from .input_mapping import process_input_from_cli
from .validation_datasets_parsers import parse_set1, parse_set2, parse_set3

logger = logging.getLogger(__name__)

#: Parsing methods for each dataset
PARSING_METHODS = {
    '1': parse_set1,
    '2': parse_set2,
    '3': parse_set3,
}


@click.group(help='DiffuPy')
def main():
    """Run DiffuPy."""
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


@main.group()
def diffusion():
    """Commands for running diffusion experiments."""


@diffusion.command()
@click.option(
    '-n', '--network',
    help='Path to the network graph or kernel',
    required=True,
    type=click.Path(exists=True, dir_okay=False)
)
@click.option(
    '-i', '--data',
    help='Input data',
    required=True,
    type=click.Path(exists=True, dir_okay=False)
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
    required=True,
)
@click.option(
    '-b', '--binarize',
    help='If logFC provided in dataset, convert logFC to binary (e.g., up-regulated entities to 1, down-regulated to '
         '-1). For scoring methods that accept quantitative values (i.e., raw & z), node labels can also be codified '
         'with LogFC (in this case, set binarize==False).',
    type=bool,
    default=True,
    show_default=True,
)
@click.option(
    '-t', '--threshold',
    help='Codify node labels by applying a threshold to logFC in input.',
    type=float,
)
@click.option(
    '-a', '--absolute_value',
    help='Codify node labels by applying threshold to |logFC| in input. If absolute_value is set to False, node labels '
         'will be signed.',
    type=bool,
    default=True,
    show_default=True,
)
@click.option(
    '-p', '--p_value',
    help='Statistical significance (p-value).',
    type=float,
    default=0.05,
    show_default=True,
)
def diffuse(
    network: str,
    data: str,
    output: str,
    method: str,
    binarize: bool,
    absolute_value: bool,
    threshold: float,
    p_value: float,
):
    """Run a diffusion method over a network or pre-generated kernel."""
    click.secho(f'{EMOJI} Loading graph from {network} {EMOJI}')
    graph = process_network_from_cli(network)

    click.secho(
        f'{EMOJI} Graph loaded with: \n'
        f'{graph.number_of_nodes()} nodes\n'
        f'{graph.number_of_edges()} edges\n'
        f'{EMOJI}'
    )

    click.secho(f'Codifying data from {data}.')

    input_scores_dict = process_input(data, method, binarize, absolute_value, p_value, threshold)

    click.secho(f'Running the diffusion algorithm.')

    results = run_diffusion(
        input_scores_dict,
        method,
        graph,
    )

    json.dump(results, output, indent=2)

    click.secho(f'Finished!')


@diffusion.command()
@click.option(
    '-d', '--data',
    help='Input data',
    required=True,
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    '-n', '--network',
    help='Path to the network graph or kernel',
    required=True,
    type=click.Path(exists=True, dir_okay=False)
)
@click.option(
    '-g', '--graph_path',
    help='Path to the network as a graph',
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    '-q', '--quantitative',  # TODO Automatize if possible, check type of label_input.
    help='Generate categorical label_input from labels',
    is_flag=False,
)
@click.option(
    '-n', '--network_as_graph',
    help='If given expects graph else expects as a kernel',
    is_flag=False,
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
@click.option(
    '-c', '--comparison',
    help='Comparison method',
    default='by_method',
    show_default=True,
    type=click.Choice(EVALUATION_METHODS),
)
@click.option(
    '-k', '--dataset',
    help='Key for the datasets presented in the paper',
    show_default=True,
    default=1,
    type=click.Choice(DATASETS),
)
def evaluate(
    data: str,
    network: str,
    graph_path: str,
    quantitative: bool,  # TODO Automatize if possible, check type of label_input.
    network_as_graph: bool,  # TODO Automatize if possible, check type of graph.
    output: str,
    iterations: int,
    comparison: str,
    dataset: int,
):
    """Evaluate a kernel/network on one of the three presented datasets."""
    click.secho(f'{EMOJI} Loading label_input for cross-validation... {EMOJI}')

    if not network_as_graph and not graph_path:
        raise ValueError("Network not provided in graph format, which is required for evaluation.")

    _, kernel, labels_mapping, graph = process_input_from_cli(
        PARSING_METHODS[dataset],
        network,
        data,
        network_as_graph,
        quantitative,
    )

    if not network_as_graph:
        graph = process_network_from_cli(graph_path)

    if comparison == 'by_method':
        click.secho(f'{EMOJI} Evaluating by method... {EMOJI}')

        auroc_metrics, auprc_metrics = cross_validation_by_method(
            labels_mapping,
            graph,
            kernel,
            k=iterations,
        )
    elif comparison == 'by_db':
        click.secho(f'{EMOJI} Evaluating by database... {EMOJI}')

        # TODO to adapt from 'get_one_x_in_cv_inputs_from_subsets', and label_input treatment subset division.
        auroc_metrics, auprc_metrics = cross_validation_by_method(
            labels_mapping,
            graph,
            kernel,
            k=iterations,
        )
    else:
        raise ValueError("The comparison method provided not match any provided method.")

    with open(os.path.join(output, 'metrics.json'), 'w') as outfile:
        json.dump(
            {'auroc_metrics': auroc_metrics,
             'auprc_metrics': auprc_metrics
             },
            outfile,
            indent=2,
        )

    click.secho(f'{EMOJI} Random cross-validation performed with success. Output located at {output}... {EMOJI}')


@main.group()
def databases():
    """Commands related to available databases."""


@databases.command()
def ls():
    """Print the list of the available databases."""
    click.secho(f'{EMOJI} Available databases {DATABASES}')


@databases.command()
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
