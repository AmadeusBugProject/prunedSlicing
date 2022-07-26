import os
import unittest

import pandas as pandas
from parameterized import parameterized

from helpers.Logger import Logger
from test.run_in_test import relative_to_project_root

log = Logger()


def get_directory():
    return relative_to_project_root('benchmark/tcas/')


def get_test_parameters():
    test_file= get_directory() + 'testData.csv'
    df = pandas.read_csv(test_file)
    return [[x['Number'], x, x['Expected_output']] for x in df.to_dict(orient='records')]


class TestBasicTcas(unittest.TestCase):
    def tearDown(self):
        pass

    @parameterized.expand(get_test_parameters())
    def test_tcas(self, test_number, test_data, expected):
        from benchmark.tcas.Tcas import Tcas
        tcas = Tcas(test_data)
        self.assertEqual(tcas.alt_sep_test(), expected)
