#!/usr/bin/env python3
import unittest
from pathlib import Path
from bin import ap_test


class TestAPTest(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Path(__file__).absolute().parent.parent

        class Dummy(object):
            pass

        self.args = Dummy()
        self.args.sjds = [59011]
        self.args.exps = [[34490027, 34490042, 34490051, 34490056, 34490069]]
        self.args.plot = False
        self.args.verbose = True

    def test_known_date(self):
        self.atest = ap_test.ApogeeFlat(
            '/data/apogee/quickred/58021/ap1D-a-24590019.fits.fz', self.args)
        self.atest.run_inputs()

    def test_directory(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        self.assertTrue(Path('/data/apogee/utr_cdr/').exists())

    def test_plotting(self):
        """Tests the plotting routine"""
        self.args.plot = True
        self.atest = ap_test.ApogeeFlat(
            '/data/apogee/quickred/58021/ap1D-a-24590019.fits.fz', self.args)
        self.atest.run_inputs()


if __name__ == '__main__':
    unittest.main()
