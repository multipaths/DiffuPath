# -*- coding: utf-8 -*-

"""Miscellaneous utils of the package."""

import itertools
import json
import logging
import pickle
import random
from statistics import mean
from .constants import *

from networkx import DiGraph

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)


def from_pickle(input_path):
    with open(input_path, 'rb') as f:
        unpickler = pickle.Unpickler(f)
        background_mat = unpickler.load()

    return background_mat


def to_pickle(to_pickle, output):
    with open(output, 'wb') as file:
        pickle.dump(to_pickle, file)


def print_dict_dimensions(entities_db, title):
    """Print dimension of the dictionary"""
    total = 0

    for k1, v1 in entities_db.items():
        m = ''
        if isinstance(v1, dict):
            for k2, v2 in v1.items():
                m += f'{k2}({len(v2)}), '
                total += len(v2)
        else:
            m += f'{len(v1)} '
            total += len(v1)

        print(f'Total number of {k1}: {m} ')

    print(f'Total: {total} ')


def get_labels_set_from_dict(entities):
    if isinstance(list(entities.values())[0], dict):
        # TODO: Check
        return set(itertools.chain.from_iterable(itertools.chain.from_iterable(entities.values())))
    else:
        return set(itertools.chain.from_iterable(entities.values()))


def reduce_dict_dimension(dict):
    """Reduce dictionary dimension."""
    return {
        k: set(itertools.chain.from_iterable(entities.values()))
        for k, entities in dict.items()
    }


def check_substrings(dataset_nodes, db_nodes):
    mapping_substrings = set()

    for entity in dataset_nodes:
        if isinstance(entity, tuple):
            for subentity in entity:
                for entity_db in db_nodes:
                    if isinstance(entity_db, tuple):
                        for subentity_db in entity_db:
                            if subentity_db in subentity or subentity in subentity_db:
                                mapping_substrings.add(entity_db)
                                break
                        break
                    else:
                        if entity_db in subentity or subentity in entity_db:
                            mapping_substrings.add(entity_db)
                            break
        else:
            for entity_db in db_nodes:
                if isinstance(entity_db, tuple):
                    for subentity_db in entity_db:
                        if subentity_db in entity or entity in subentity_db:
                            mapping_substrings.add(entity_db)
                            break
                    break
                else:
                    if entity_db in entity or entity in entity_db:
                        mapping_substrings.add(entity_db)
                        break

    return mapping_substrings


def split_random_two_subsets(to_split):
    half_1 = random.sample(population=list(to_split), k=int(len(to_split) / 2))
    half_2 = list(set(to_split) - set(half_1))

    return half_1, half_2


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

    set1, set2 = random_disjoint_intersection_two_subsets(intersections['unique_set1'],
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

    for db_name, entities_by_type in mapping_by_database_and_entity.items():
        db_count = []
        db_percentage = []

        db_labels.append(db_name)

        if not types_labels:
            types_labels = entities_by_type[0].keys()

        for entity_type, entities_tupple in entities_by_type[0].items():
            db_count.append(len(entities_tupple[0]))
            db_percentage.append(entities_tupple[1])

        all_count.append(db_count)
        all_percentage.append(db_percentage)

    return np.array(all_count), np.array(all_percentage), db_labels, types_labels


def get_mean_from_two_dim_dict(d):
    for k1, v1 in d.items():
        for k2, v2 in v1.items():
            if v2:
                d[k1][k2] = [mean(v2)]

    return d


"""Check formats of networks """


def _format_checker(format: str) -> None:
    """Check column format."""
    if format not in FORMATS:
        raise ValueError(
            f'The selected format {format} is not valid. Please ensure you use one of the following formats: '
            f'{FORMATS}'
        )


def _read_network_file(path: str, format: str) -> pd.DataFrame:
    """Read network file."""
    _format_checker(format)

    df = pd.read_csv(
        path,
        header=0,
        sep=FORMAT_SEPARATOR_MAPPING[CSV] if format == CSV else FORMAT_SEPARATOR_MAPPING[TSV]
    )

    if SOURCE and TARGET not in df.columns:

        raise ValueError(
            f'Ensure that your file contains columns for {SOURCE} and {TARGET}. The column for {RELATION} is optional'
            f'and can be omitted.'
        )

    return df

def process_network(path: str, format: str) -> DiGraph:
    """Parse dataFrame and """
    _format_checker(format)

    df = _read_network_file(path, format)

    graph = DiGraph()

    for index, row in df.iterrows():

        # Get node names from data frame
        sub_name = row[SOURCE]
        obj_name = row[TARGET]

        if RELATION in df.columns:

            relation = row[RELATION]

            # Store edge in the graph
            graph.add_edge(
                sub_name, obj_name,
                relation=relation
            )

        else:
            graph.add_edge(
                sub_name, obj_name,
            )

    return graph


def load_json_file(path: str) -> DiGraph:
    """Read json file."""
    with open(path) as f:
        return json.load(f)