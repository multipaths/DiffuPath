# -*- coding: utf-8 -*-

"""Miscellaneous utils of the package."""

import itertools
import logging
import pickle
import random
from statistics import mean

import numpy as np

log = logging.getLogger(__name__)


def from_pickle(input_path):
    """Read network from pickle."""
    with open(input_path, 'rb') as f:
        unpickler = pickle.Unpickler(f)
        background_mat = unpickler.load()

    return background_mat


def to_pickle(to_pickle, output):
    """Write pickle."""
    with open(output, 'wb') as file:
        pickle.dump(to_pickle, file)


def print_dict_dimensions(entities_db, title='', message='Total number of '):
    """Print dimension of the dictionary"""
    total = set()
    m = f'{title}\n'

    for k1, v1 in entities_db.items():
        m = ''
        if isinstance(v1, dict):
            for k2, v2 in v1.items():
                m += f'{k2}({len(v2)}), '
                total.update(v2)
        else:
            m += f'{len(v1)} '
            total.update(v1)

        print(f'{message} {k1}: {m} ')

    print(f'Total: {len(total)} ')


def print_dict(dict_to_print, message=''):
    """Print dimension of the dictionary"""

    for k1, v1 in dict_to_print.items():
        print(f'{message} {k1}: {v1} ')


def get_labels_set_from_dict(entities):
    if isinstance(list(entities.values())[0], dict):
        # TODO: Check
        return set(itertools.chain.from_iterable(itertools.chain.from_iterable(entities.values())))
    else:
        return set(itertools.chain.from_iterable(entities.values()))


def reduce_dict_dimension(dict):
    """Reduce dictionary dimension."""
    reduced_dict = {}

    for k1, entities1 in dict.items():
        for k2, entities2 in entities1.items():
            if k1 in reduced_dict.keys():
                reduced_dict[k1].update(entities2)
            else:
                reduced_dict[k1] = entities2

    return reduced_dict


def split_random_two_subsets(to_split):
    """Split random two subsets."""
    if isinstance(to_split, dict):
        to_split_labels = list(to_split.keys())
    else:
        to_split_labels = to_split

    half_1 = random.sample(population=list(to_split_labels), k=int(len(to_split_labels) / 2))
    half_2 = list(set(to_split_labels) - set(half_1))

    if isinstance(to_split, dict):
        return {entity_label: to_split[entity_label] for entity_label in half_1}, \
               {entity_label: to_split[entity_label] for entity_label in half_2}
    else:
        return half_1, half_2


def hide_true_positives(to_split, k=0.5):
    """Hide relative number of labels."""
    if isinstance(to_split, set):
        to_split = list(to_split)

    new_labels = to_split[:]

    # Check for -1
    if -1 in new_labels:
        new_labels = [0 if label == -1 else label for label in new_labels]

    indices = [index for index, label in enumerate(new_labels) if label != 0]

    for index in random.choices(indices, k=int(k * len(indices))):
        new_labels[index] = 0

    return new_labels


def split_random_three_subsets(to_split):
    half_1 = random.sample(population=list(to_split), k=int(len(to_split) / 3))
    half_2, half_3 = split_random_two_subsets(list(set(to_split) - set(half_1)))

    return half_1, half_2, half_3


def get_three_venn_intersections(set1, set2, set3):
    set1, set2, set3 = set(set1), set(set2), set(set3)
    set1_set2 = set1.intersection(set2)
    set1_set3 = set1.intersection(set3)
    core = set1_set3.intersection(set1_set2)

    set1_set2 = set1_set2 - core
    set1_set3 = set1_set3 - core
    set2_set3 = set2.intersection(set3) - core

    return {'unique_set1': set1 - set1_set2 - set1_set3 - core,
            'unique_set2': set2 - set1_set2 - set2_set3 - core,
            'set1_set2': set1_set2,
            'unique_set3': set3 - set1_set3 - set2_set3 - core,
            'set1_set3': set1_set3,
            'set2_set3': set2_set3,
            'core': core,
            }


def random_disjoint_intersection_two_subsets(unique_set1, unique_set2, intersection):
    set1, set2 = split_random_two_subsets(intersection)

    return unique_set1 | set(set1), unique_set2 | set(set2)


def random_disjoint_intersection_three_subsets(sets_dict):
    set_labels = list(sets_dict.keys())
    set_values = list(sets_dict.values())

    set1, set2, set3 = set_values[0][0], set_values[1][0], set_values[2][0]

    intersections = get_three_venn_intersections(set1, set2, set3)

    set1, set2 = random_disjoint_intersection_two_subsets(
        intersections['unique_set1'],
        intersections['unique_set2'],
        intersections['set1_set2']
    )

    set1, set3 = random_disjoint_intersection_two_subsets(set1,
                                                          intersections['unique_set3'],
                                                          intersections['set1_set3']
                                                          )

    set2, set3 = random_disjoint_intersection_two_subsets(set2,
                                                          set3,
                                                          intersections['set2_set3']
                                                          )

    set1_core, set2_core, set3_core = split_random_three_subsets(intersections['core'])

    return {set_labels[0]: set1 | set(set1_core),
            set_labels[1]: set2 | set(set2_core),
            set_labels[2]: set3 | set(set3_core)
            }


def get_count_and_labels_from_two_dim_dict(mapping_by_database_and_entity):
    db_labels = []
    types_labels = []

    all_count = []
    all_percentage = []

    # entity_type_map = {'metabolite_nodes': 'metabolite', 'mirna_nodes': 'micrornas', 'gene_nodes': 'genes', 'bp_nodes': 'bps'}

    for type_label, entities in mapping_by_database_and_entity.items():
        db_count = []
        db_percentage = []

        db_labels.append(type_label)

        if types_labels == []:
            types_labels = list(entities.keys())

        for entity_type, entities_tupple in entities.items():
            db_count.append(entities_tupple[1])
            db_percentage.append(entities_tupple[0])

        all_count.append(db_count)
        all_percentage.append(db_percentage)

    return np.array(all_count), np.array(all_percentage), db_labels, types_labels


def get_mean_from_two_dim_dict(d):
    for k1, v1 in d.items():
        for k2, v2 in v1.items():
            if v2:
                d[k1][k2] = [mean(v2)]

    return d
