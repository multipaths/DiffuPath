# -*- coding: utf-8 -*-

"""Command line interface."""

import json
import logging

import click
from bio2bel.constants import get_global_connection

from diffupy.diffuse import diffuse as run_diffusion
from diffupy.utils import process_network_from_cli, _process_input
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
    '-n', '--network',
    help='Path to the network graph or kernel',
    required=True,
    type=click.Path(exists=True, dir_okay=False)
)
@click.option(
    '-i', '--input',
    help='Input data',
    required=True,
    type=click.Path(exists=True, dir_okay=False)
)
@click.option(
    '-m', '--method',
    help='Difussion method',
    type=click.Choice(DIFFUPY_METHODS),
    required=True,
)
@click.option(
    '-o', '--output',
    help='Output path for the results',
    default=OUTPUT_DIR,
    show_default=True,
    type=click.Path(exists=True, file_okay=False)
)
def run(
        network: str,
        input: str,
        method: str,
        output: str,
):
    """Run a diffusion method over a network or pregenerated kernel."""
    click.secho(f'{EMOJI} Running diffusion... {EMOJI}')

    click.secho(f'{EMOJI} Loading graph from {network} {EMOJI}')
    graph = process_network_from_cli(network)

    click.secho(
        f'{EMOJI} Graph loaded with: \n'
        f'{graph.number_of_nodes()} nodes\n'
        f'{graph.number_of_edges()} edges\n'
        f'{EMOJI}'
    )

    input_scores = _process_input(input)

    results = run_diffusion(
        input_scores,
        method,
        graph,
    )

    json.dump(results, output, indent=2)


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
