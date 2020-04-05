# -*- coding: utf-8 -*-

"""Validate label_input utilities."""

import logging

log = logging.getLogger(__name__)


def validation_input_from_dict(mapping_by_subsets, diffuse_input_type, validation_type, input_diffuse):
    """Validate cross validation from dict."""
    input_labels = mapping_by_subsets[diffuse_input_type]
    validation_labels = mapping_by_subsets[validation_type]
    out_labels = set(input_diffuse.rows_labels) - input_labels - validation_labels

    return [input_labels, validation_labels, out_labels]


def validate_cross_validation_input_1(input_diffuse, input_validate, sets):
    """Validate cross validation input 1."""
    labeled, unlabeled, no_labeled = set(), set(), set()

    for score, i, j, row_label, col_label in input_diffuse.__iter__(get_indices=True, get_labels=True):
        if score == 1:
            labeled.add(row_label)

        if score == 0:
            unlabeled.add(row_label)

        if score == -1:
            no_labeled.add(row_label)

    assert labeled == sets[0]
    assert unlabeled == sets[1]
    assert no_labeled == sets[2]

    labeled, unlabeled, no_labeled = set(), set(), set()

    for score, i, j, row_label, col_label in input_validate.__iter__(get_indices=True, get_labels=True):
        if score == 1:
            labeled.add(row_label)

        if score == 0:
            unlabeled.add(row_label)

        if score == -1:
            no_labeled.add(row_label)

    assert labeled == sets[1]
    assert len(unlabeled) == 0
    assert no_labeled == sets[0].union(sets[2])

    logging.info('Test cross_validation_input_1 passed.')
