# -*- coding: utf-8 -*-

"""This module has methods to acquire the networks for each database available in DiffuPath."""
import importlib
import logging
import os
import sys
from contextlib import redirect_stdout
from typing import Optional

import click
from bio2bel import AbstractManager
from biokeen.convert import to_pykeen_df, to_pykeen_path, to_pykeen_summary_path
from pybel import from_json_path, to_json_path

from .constants import EMOJI, OUTPUT_DIR

_PATHME_MODULES = {
    'kegg': 'pathme',
    'reactome': 'pathme',
    'wikipathways': 'pathme',
}

logger = logging.getLogger(__name__)


def install_and_populate_database(name: str, connection: Optional[str] = None) -> Optional[str]:
    """Install biological database.
    :param name: The name of the databae
    :param connection: The optional database connection
    """
    export_file = os.path.join(OUTPUT_DIR, f'{name}.csv')
    summary_file = os.path.join(OUTPUT_DIR, f'{name}_summary.csv')
    json_file = os.path.join(OUTPUT_DIR, f'{name}.bel.json')

    if os.path.exists(export_file):
        logger.info(f'{EMOJI} {name} has already been retrieved. See: {export_file}')
        return export_file

    if os.path.exists(json_file):
        logger.info(f'{EMOJI} loaded {name} JSON: {json_file}')
        graph = from_json_path(json_file)
        df = to_pykeen_df(graph)
        to_pykeen_path(df, export_file)
        to_pykeen_summary_path(df, summary_file)
        return export_file

    if name in _PATHME_MODULES:
        click.secho(
            f'{EMOJI} You are trying to install {name} which is part of PathMe. '
            'Due to the complexity of the installation, we refer to the tutorial at'
            ' https://github.com/PathwayMerger/PathMe to install it. Alternatively, you can download the dumps of '
            f'{name} directly from the URLs at the DiffuPath README file.'
        )
        sys.exit(0)

    module_name = f'bio2bel_{name}'

    bio2bel_module = ensure_bio2bel_installation(module_name)
    logger.debug(f'{EMOJI} imported {name}')

    manager_cls = bio2bel_module.Manager

    manager = manager_cls(connection=connection)

    if issubclass(manager_cls, AbstractManager):
        if not manager.is_populated():
            logger.info(f'{EMOJI} populating {module_name}')
            manager.populate()
        else:
            logger.debug(f'{EMOJI} {module_name} has already been populated')

    logger.debug(f'{EMOJI} generating BEL for {module_name}')
    graph = manager.to_bel()

    logger.debug(f'Summary: {graph.number_of_nodes()} nodes / {graph.number_of_edges()} edges')
    to_json_path(graph, json_file, indent=2)

    logger.debug(f'{EMOJI} generating PyKEEN TSV for {module_name}')
    df = to_pykeen_df(graph)
    to_pykeen_summary_path(df, summary_file)
    success = to_pykeen_path(df, export_file)

    if success:
        logger.debug(f'{EMOJI} wrote PyKEEN TSV to {export_file}')
        return export_file

    logger.warning(f'{EMOJI} no statements generated')


def ensure_bio2bel_installation(package: str):
    """Import a package, or install it."""
    try:
        b_module = importlib.import_module(package)

    except ImportError:
        logger.info(f'{EMOJI} pip install {package}')

        with redirect_stdout(sys.stderr):
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

        try:
            return importlib.import_module(package)
        except ImportError:
            logger.exception(
                f'{EMOJI} failed to import {package}'
                f'{EMOJI} could not find {package} on PyPI. Try installing from GitHub with:'
                f'\n   pip install git+https://github.com/bio2bel/{package.split("_")[-1]}.git\n'
            )
            sys.exit(1)

    return b_module
