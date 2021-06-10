#!/usr/bin/env python3
import unittest
from pathlib import Path
from bin import ap_test
import numpy as np


class TestAPTest(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Path(__file__).absolute().parent.parent

        class Dummy(object):
            pass

        self.args = Dummy()
        self.args.sjds = [59011]
        self.args.exps = [[34490027, 34490042, 34490051, 34490056, 34490069]]
        self.args.plot = False
        self.args.legacy = False
        self.args.verbose = True
        master_path = self.project / 'dat/master_dome_flat_1.npy'
        self.master_data = np.load(master_path)

    def test_known_date(self):

        self.atest = ap_test.ApogeeFlat(self.master_data, self.args)
        self.atest.run_inputs()

    def test_directory(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        self.assertTrue(Path('/data/apogee/utr_cdr/').exists()
                        or (Path.home() / 'data/apogee/utr_cdr').exists())

    def test_plotting(self):
        """Tests the plotting routine"""
        self.args.plot = True
        self.atest = ap_test.ApogeeFlat(self.master_data, self.args)
        self.atest.run_inputs()

    def test_legacy(self):
        """Test the legacy version of ap_test"""
        self.args.legacy = True
        self.master_data = np.load(self.project / 'dat/utr_master_flat_21180043.npy')
        self.atest = ap_test.ApogeeFlat(self.master_data, self.args)
        self.atest.run_inputs()


if __name__ == '__main__':
    unittest.main()
