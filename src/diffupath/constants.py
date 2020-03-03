"""Constants of diffupath."""

import os

dir_path = os.path.dirname(os.path.realpath(__file__))
SOURCE_DIR = os.path.join(os.path.abspath(os.path.join(dir_path, os.pardir)))
DATA_DIR = os.path.join(os.path.abspath(os.path.join(SOURCE_DIR, os.pardir)), 'data')
KERNEL_DIR = os.path.join(DATA_DIR, 'kernels')


def ensure_output_dirs():
    """Ensure that the output directories exists."""
    os.makedirs(KERNEL_DIR, exist_ok=True)


# TODO: establish (or move from local) package constants
