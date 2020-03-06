# -*- coding: utf-8 -*-

"""Command line interface."""

import logging

import click

logger = logging.getLogger(__name__)


@click.group(help='DiffuPy')
def main():
    """Run DiffuPy."""
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")



@main.command()
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
    '-o', '--output',
    help='Output path for the results',
    default=OUTPUT,
    show_default=True,
    type=click.Path(exists=True, file_okay=False)
)
@click.option(
    '-m', '--method',
    help='Difussion method',
    type=click.Choice(METHODS),
)
def diffuse(
        network: str,
        input: str,
        output: str,
        method: str,
):
    """Run a diffusion method over a network or pregenerated kernel."""
    raise NotImplementedError
    #TODO : Process arguments and call diffuse

    
@main.command()
@click.option(
    '-d', '--database',
    help='Database to be downloaded',
    required=True,
)
def download_database(
        database: str,
):
    """Downloads a biological database and prepare the network for diffusion."""
    raise NotImplementedError
    #TODO : Process arguments and call diffuse


if __name__ == '__main__':
    main()
