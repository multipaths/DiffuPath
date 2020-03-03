# -*- coding: utf-8 -*-

"""Command line interface."""

import logging

import click

logger = logging.getLogger(__name__)


@click.group(help='DiffuPy')
def main():
    """Run DiffuPy."""
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


# TODO Consider which commands could be implemented, since for now all the package functionalities are
#  offered as functions imports.

if __name__ == '__main__':
    main()
