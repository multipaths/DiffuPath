# -*- coding: utf-8 -*-

"""Tests validator module."""

import unittest

from diffupath.validate_input import validate_cross_validation_input_1

from diffupy.matrix import Matrix
from diffupy.process_input import generate_categoric_input_from_labels


class ValidateCVInputTest(unittest.TestCase):
    """Test cross validation."""

    def test_validate_cross_validation_input_1(self):
        """Test label_input of CV."""
        set_1 = {'adenine', 'adp', 'tyramine', 'nadph', 'glycine', 'glutathione', 'choline', 'inosine'}
        set_2 = {'g6pc3', 'oscar', 'lin37', 'pip4k2c', 'asap3', 'smg7', 'fosl1', 'atg3', 'plod3', 'apoe', 'calcoco2',
                 'hbegf', 'ccne1', 'magi3', 'gpc1', 'dusp5', 'idi1', 'ids', 'il12a', 'fancd2', 'zmpste24', 'znf383',
                 'gstm3', 'pgm2l1', 'dpm2', 'galk1', 'tfg', 'smox', 'znf473', 'thtpa', 'cyp2u1', 'rpa3', 'ggct', 'c5',
                 'foxa2', 'ndufb1', 'fn1', 'tyms', 'hsd17b2', 'birc5', 'tuba4a', 'ucn', 'dnm1l', 'dock4', 'actr3b',
                 'pigw', 'map2k1', 'tusc3', 'znf248', 'amdhd1', 'znf561', 'dck', 'lifr', 'gldc', 'rgl1', 'il1r1',
                 'actg1', 'agmat', 'ggt5', 'palb2', 'chac2', 'slc33a1', 'xylt2', 'il11', 'mir31', 'atm', 'serpind1',
                 'skp1', 'odc1', 'taldo1', 'mir331', 'gys1', 'cyp3a7', 'ctsk', 'man1a1', 'col2a1', 'arf6', 'acp2',
                 'mocos', 'cyp51a1', 'cbl', 'synj2'}
        set_3 = {'mir31', 'mir106b', 'mir193b', 'mir17', 'mir21', 'mir30e', 'mir30d'}

        all_labels = set_1 | set_2 | set_3

        background_matrix = Matrix(
            cols_labels=all_labels,
            rows_labels=all_labels,
            init_value=0,
            name='Test Matrix 1'
        )

        input_diffuse = generate_categoric_input_from_labels(
            set_1,
            'two out label_input',
            background_matrix,
            rows_unlabeled=set_2)

        input_validate = generate_categoric_input_from_labels(
            set_2,
            'two out label_input',
            background_matrix
        )

        validate_cross_validation_input_1(input_diffuse, input_validate, [set_1, set_2, set_3])
