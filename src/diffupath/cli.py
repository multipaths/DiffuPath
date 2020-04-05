# -*- coding: utf-8 -*-

"""Command line interface."""

import json
import logging

import click
from bio2bel.constants import get_global_connection
from diffupy.utils import process_network_from_cli

from .cross_validation import cross_validation_by_method

from diffupy.diffuse import diffuse as run_diffusion

from .input_mapping import process_input_from_cli

from .validation_datasets_parsers import parse_set1

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
    '-q', '--quantitative', # TODO Automatize if possible, check type of input.
    help='Generate categorical input from labels',
    show_default=False,
    is_flag=False
)
@click.option(
    '-n', '--network',
    help='Path to the network graph or kernel',
    default=os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels', 'kernel_regularized_pathme_universe.pickle'),
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
        quantitative: bool = False,
        network: str = os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels', 'kernel_regularized_pathme_universe.pickle'),
        graph: bool = False,
        method: str = 'raw',
        output: str = OUTPUT_DIR,
):
    """Run a diffusion method given an input over a network or a pre-generated kernel."""
    click.secho(f'{EMOJI} Running diffusion... {EMOJI}')

    input_scores, kernel, _, _ = process_input_from_cli(click, parse_set1, network, input, graph, quantitative)

    # Perform/run diffusion
    results = run_diffusion(
        input_scores,
        method,
        k=kernel,
    )

    # Export diffusion scores as a csv data file
    results.to_csv(output)

    click.secho(f'{EMOJI} Diffusion performed with success. Output located at {output}... {EMOJI}')


@diffusion.command()
@click.option(
    '-i', '--input',
    help='Input data',
    required=True,
    type=click.Path(exists=True, dir_okay=False)
)
@click.option(
    '-q', '--quantitative', # TODO Automatize if possible, check type of input.
    help='Generate categorical input from labels',
    show_default=False,
    is_flag=False
)
@click.option(
    '-n', '--network',
    help='Path to the network graph or kernel',
    default=os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels', 'kernel_regularized_pathme_universe.pickle'),
    show_default=True,
    type=click.Path(exists=True, dir_okay=False)
)
@click.option(
    '-n', '--network_as_graph',
    help='network_as_graph',
    show_default=True,
    is_flag=False
)
@click.option(
    '-g', '--graph_path',
    help='Path to the network as a graph',
    default=os.path.join(DEFAULT_DIFFUPATH_DIR, 'pickles', 'universe', 'pathme_universe_bel_graph.bel.pickle'),
    show_default=True,
    type=click.Path(exists=True, dir_okay=False)
)
@click.option(
    '-o', '--output',
    help='Output path for the results',
    default=OUTPUT_DIR,
    show_default=True,
    type=click.Path(exists=True, file_okay=False)
)
@click.option(
    '-k', '--k_iterations',
    help='Number of iterations for the cross validation',
    default=20,
    show_default=True,
    type=int
)
@click.option(
    '-c', '--comparaison_method',
    help='Comparaison method',
    default='by_method',
    show_default=True,
    type=click.Choice(CV_METHODS),
)
def random_cross_validation(
        input: str,
        quantitative: bool = False, # TODO Automatize if possible, check type of input.
        network: str = os.path.join(DEFAULT_DIFFUPATH_DIR, 'kernels', 'kernel_regularized_pathme_universe.pickle'),
        network_as_graph: bool = False,  # TODO Automatize if possible, check type of graph.
        graph_path: str = os.path.join(DEFAULT_DIFFUPATH_DIR, 'pickles', 'universe', 'pathme_universe_bel_graph.pickle'),
        output: str = OUTPUT_DIR,
        k_iterations: int = 20,
        comparaison_method: str = 'by_method',
):
    """Run a diffusion method given an input over a network or a pre-generated kernel."""
    click.secho(f'{EMOJI} Loading input for cross-validation... {EMOJI}')

    if not network_as_graph and not graph_path:
        raise Warning("Network not provided in graph format, which required for the random baseline generation.")

    _, kernel, labels_mapping, graph = process_input_from_cli(click, parse_set1, network, input, network_as_graph, quantitative)

    if not network_as_graph:
        graph = process_network_from_cli(graph_path)

    if comparaison_method == 'by_method':
        click.secho(f'{EMOJI} Running random cross-validation by method... {EMOJI}')

        auroc_metrics, auprc_metrics = cross_validation_by_method(
            labels_mapping,
            graph,
            kernel,
            k=k_iterations,
        )
    elif comparaison_method == 'by_db':
        # TODO to adapt from 'get_one_x_in_cv_inputs_from_subsets', and input treatment subset division.
        auroc_metrics, auprc_metrics = cross_validation_by_method(
            labels_mapping,
            graph,
            kernel,
            k=k_iterations,
        )
    else:
        raise Warning("Comparaison method provided not match any provided method.")


    with open(os.path.join(output, 'metrics_set1_universe.json'), 'w') as outfile:
        json.dump(
            {'auroc_metrics': auroc_metrics,
             'auprc_metrics_by_method': auprc_metrics
            },
            outfile
        )

    click.secho(f'{EMOJI} Random cross-validation performed with success. Output located at {output}... {EMOJI}')


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
