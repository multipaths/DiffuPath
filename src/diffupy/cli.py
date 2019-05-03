# -*- coding: utf-8 -*-

"""Command line interface."""

import logging
import os
import pickle
import time

import click
import networkx as nx
import pybel

from diffupy.constants import DATA_DIR
from diffupy.kernels import regularised_laplacian_kernel

logger = logging.getLogger(__name__)


@click.group(help='DiffuPy')
def main():
    """Run DiffuPy."""
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


"""Diffupy"""


@main.command()
@click.option(
    '-g', '--graph',
    help='Path to the BEL graph',
    default=os.path.join(DATA_DIR, 'pickles', 'pathme_universe_bel_graph_no_flatten.bel.pickle'),
    show_default=True
)
@click.option(
    '-o', '--output',
    help='Output kernel pickle',
    default=os.path.join(DATA_DIR, 'kernels'),
    show_default=True
)
@click.option('--isolates', is_flag=False, help='Include isolates')
@click.option('-l', '--log', is_flag=True, help='Activate debug mode')
def kernel(graph, output, isolates, log):
    """Generates kernel for a given BEL graph."""

    # Configure logging level
    if log:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        logger.setLevel(logging.INFO)

    click.echo(f'Loading graph from {graph}')
    bel_graph = pybel.from_pickle(graph)

    if isolates:
        click.echo(f'Removing {nx.number_of_isolates(graph)} isolated nodes')

        bel_graph.remove_nodes_from({
            node
            for node in nx.isolates(bel_graph)
        })

    click.echo(
        f'Statistics\n'
        f'##########\n'
        f'{bel_graph.summary_str()}'
    )

    then = time.time()
    background_mat = regularised_laplacian_kernel(bel_graph)
    now = time.time()
    click.echo(f"It took: ", {now} - {then}, " seconds")

    output = os.path.join(output, 'regularized_kernel_pathme_universe.pickle')

    with open(output, 'wb') as file:
        pickle.dump(background_mat, file)

    click.echo(f'Kernel exported to: {output}')


if __name__ == '__main__':
    main()