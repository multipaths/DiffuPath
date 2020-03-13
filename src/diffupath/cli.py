# -*- coding: utf-8 -*-

"""Command line interface."""

import logging

import click
import pybel
from bio2bel.constants import get_global_connection
from networkx import read_graphml, read_gml, node_link_graph

from diffupy.constants import (
    CSV, TSV, FORMATS, GRAPHML, GML, BEL, BEL_PICKLE, NODE_LINK_JSON,
)
from diffupy.utils import process_network, load_json_file
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
    click.secho(f'{EMOJI} Running diffusion {EMOJI}')

    if network.endswith(CSV):
        graph = process_network(network, CSV)

    elif network.endswith(TSV):
        graph = process_network(network, TSV)

    elif network.endswith(GRAPHML):
        graph = read_graphml(network)

    elif network.endswith(GML):
        graph = read_gml(network)

    elif network.endswith(BEL):
        graph = pybel.from_path(network)

    elif network.endswith(BEL_PICKLE):
        graph = pybel.from_pickle(network)

    elif network.endswith(NODE_LINK_JSON):
        data = load_json_file(network)
        graph = node_link_graph(data)

    else:
        raise IOError(
            f'The selected format {format} is not valid. Please ensure you use one of the following formats: '
            f'{FORMATS}'
        )

    # TODO: Process arguments and call diffuse
    # TODO: @Josep


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
