#!/usr/bin/env python3
import unittest
from pathlib import Path
from bin import ap_test
import numpy as np
from sdssobstools import sdss_paths


class TestAPTest(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Path(__file__).absolute().parent.parent

        class Dummy(object):
            pass

        self.args = Dummy()
        self.args.sjds = [59593]
        self.args.exps = [[40310015, 40310016, 40310017, 40310018, 40310019]]
        self.args.plot = False
        self.args.verbose = True

    def test_known_date(self):

        self.atest = ap_test.ApogeeFlat(self.args)
        self.atest.run_inputs()

    def test_directory(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        self.assertTrue(sdss_paths.ap_utr.exists())

    def test_plotting(self):
        """Tests the plotting routine"""
        self.args.plot = True
        self.atest = ap_test.ApogeeFlat(self.args)
        self.atest.run_inputs()


if __name__ == '__main__':
    unittest.main()
