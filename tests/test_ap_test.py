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
        self.args.sjds = [59392]
        self.args.exps = [[38300015, 38300028, 38300041, 38300052]]
        self.args.plot = False
        self.args.legacy = False
        self.args.verbose = True
        master_path = self.project / 'dat/master_dome_flat_1.npy'
        self.master_data = np.load(master_path)

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

    def test_legacy(self):
        """Test the legacy version of ap_test"""
        self.args.legacy = True
        self.master_data = np.load(self.project / 'dat/utr_master_flat_21180043.npy')
        self.atest = ap_test.ApogeeFlat(self.args)
        self.atest.run_inputs()


if __name__ == '__main__':
    unittest.main()
