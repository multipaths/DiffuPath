# -*- coding: utf-8 -*-

"""Tests checking kernel functions py implementation based on R package computations."""

import logging
import unittest

import networkx as nx
import numpy as np

from diffupy.kernels import commute_time_kernel, p_step_kernel, inverse_cosine_kernel, diffusion_kernel, \
    regularised_laplacian_kernel
from diffupy.matrix import Matrix
from .constants import *

log = logging.getLogger(__name__)

"""Helper functions for testing."""


def _run_kernel_test(kernel_func, G, validate_matrix_path):
    M = kernel_func(G)
    V = Matrix.from_csv(validate_matrix_path)

    logging.info(' %s  \n %s\n', 'Computed matrix', M)
    logging.info(' %s  \n %s\n', 'Test matrix', V)
    # Assert rounded similarity (floating comma)
    assert np.allclose(M, V)
    logging.info(' Test ' + kernel_func.__name__ + ' passed')


"""Tests"""


class KernelsTest(unittest.TestCase):
    G = nx.read_gml(GML_FILE_EXAMPLE, label='id')

    _run_kernel_test(commute_time_kernel, G, COMMUTE_TIME_KERNEL)
    _run_kernel_test(diffusion_kernel, G, DIFFUSION_KERNEL)
    _run_kernel_test(p_step_kernel, G, P_STEP_KERNEL)
    _run_kernel_test(inverse_cosine_kernel, G, INVERSE_COSINE_KERNEL)
    _run_kernel_test(regularised_laplacian_kernel, G, REGULARISED_LAPLACIAN_KERNEL)
