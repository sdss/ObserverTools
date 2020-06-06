#!/usr/bin/env python3
import unittest
from pathlib import Path
from bin import ap_test


class TestAPTest(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Path(__file__).parent.parent
        class dummy(object):
            pass
        self.args = dummy()
        self.args.mjds = [58900]
        self.args.exps = [[33380025, 33380042, 33380071, 33380080]]

    def test_known_date(self):
        self.atest = ap_test.ApogeeFlat(
            self.project / 'dat/ap_master_flat_col_array.dat', self.args)
        self.atest.run_inputs()

    def test_directory(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        self.assertTrue(Path('/data/apogee/utr_cdr/').exists())

    def test_plotting(self):
        """Tests the plotting routine"""
        self.args.plot = True
        self.atest = ap_test.ApogeeFlat(
            self.project / 'dat/ap_master_flat_col_array.dat', self.args)
        self.atest.run_inputs()


if __name__ == '__main__':
    unittest.main()
