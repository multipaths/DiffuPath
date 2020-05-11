# -*- coding: utf-8 -*-

"""Topological analyses."""

import warnings
from collections import defaultdict

import networkx as nx
import numpy as np
from diffupy.matrix import LaplacianMatrix, Matrix
from diffupy.process_network import get_simple_graph_from_multigraph


def generate_pagerank_baseline(graph: nx.Graph, background_mat: Matrix) -> Matrix:
    """Generate baseline results using page rank algorithm."""
    graph = get_simple_graph_from_multigraph(graph)

    pagerank_scores = nx.pagerank(graph)

    if len(pagerank_scores.values()) != len(background_mat.mat):
        warnings.warn(
            'The provided graph do not match the kernel nodes amount. The nodes will be matched (deleting and filling missing) according to the reference Matrix.')

    return Matrix(mat=np.array(
        list(pagerank_scores.values())).reshape(
        (len(list(pagerank_scores.values())), 1)
    ),
        rows_labels=list(pagerank_scores.keys()),
        cols_labels=['PageRank']
    ).match_delete_rows(background_mat.rows_labels).match_missing_rows(background_mat.rows_labels).match_rows(
        background_mat)


def resistance_distance(G=None, M=None, normalized=False):
    """Calculate the resistance."""
    if G:
        ER = LaplacianMatrix(G, normalized)
        add_edges_inv = 1 / G.number_of_edges()

    elif M:
        ER = M
        add_edges_inv = 1 / len(ER.rows_labels)

    else:
        raise Warning('A graph or a matrix must be given.')

    LT = np.linalg.inv([x + add_edges_inv
                        for x in ER.mat
                        ]
                       )
    dLT = np.diag(LT)

    sER = [x * -2
           for x in LT
           ] + dLT[:, np.newaxis]
    ssER = sER + dLT[np.newaxis, :]

    ER.mat = ssER

    return ER


def filter_quadratic_mat_by_mapping(M, mapping):
    d = defaultdict(lambda: defaultdict(lambda: list()))

    for k1, v1 in mapping.items():
        for k2, v2 in mapping.items():
            for e1 in v1[0]:
                for e2 in v2[0]:
                    d[k1][k2].append(M.get_cell_from_labels(e1, e2))

    return d
