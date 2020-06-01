#!/usr/bin/env python3
import unittest
from pathlib import Path
from bin import ads9


class TestSloanLog(unittest.TestCase):
    def test_no_args(self):
        args = ads9.parseargs()
        ap_ds9 = ads9.ADS9(args)
        ap_ds9.close()

    def test_directory(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        args = ads9.parseargs()
        self.assertTrue(Path(args.fits_dir).exists())


if __name__ == '__main__':
    unittest.main()
