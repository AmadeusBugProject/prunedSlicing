import glob
import os
import unittest

from parameterized import parameterized

from helpers.Logger import Logger
from test.run_in_test import relative_to_project_root

log = Logger()


def get_directory():
    return relative_to_project_root('benchmark/tcas/faulty_versions/')


def get_test_parameters():
    faulty_tcas = glob.glob(get_directory() + 'Tcas_Fault*.py')
    test_params = [[x] for x in faulty_tcas]
    test_params.sort()
    return test_params


class TestFaultyTcas(unittest.TestCase):
    def tearDown(self):
        pass

    @parameterized.expand(get_test_parameters())
    def test_tcas(self, faulty_tcas):
        test_data = {'Number': '#0001:', 'Cur_Vertical_Sep': 627, 'High_Confidence': 0, 'Two_of_Three_Reports_Valid': 0,
                     'Own_Tracked_Alt': 621, 'Own_Tracked_Alt_Rate': 216, 'Other_Tracked_Alt': 382,
                     'Alt_Layer_Value': 1, 'Up_Separation': 400, 'Down_Separation': 641, 'Other_RAC': 1,
                     'Other_Capability': 1, 'Climb_Inhibit': 0, 'Expected_output': 0}

        print(faulty_tcas)
        with open(faulty_tcas, 'r') as fd:
            faulty_tcas_code = fd.read()

        function_call = ['test_data = ' + str(test_data),
                         'tcas_instance = Tcas(test_data)',
                         'alt_sep_actual = tcas_instance.alt_sep_test()']

        faulty_tcas_code = faulty_tcas_code + '\n' + '\n'.join(function_call)
        run_faulty_code(faulty_tcas_code)


def run_faulty_code(faulty_tcas_code):
    globals_space = globals().copy()
    exec(compile(faulty_tcas_code, filename="", mode="exec"), globals_space)
