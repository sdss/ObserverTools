#!/usr/bin/env python3
import unittest
from pathlib import Path
from bin import bds9


class TestADS9(unittest.TestCase):
    def test_no_args(self):
        args = bds9.parseargs()
        b_ds9 = bds9.BossDS9(args)
        b_ds9.close()

    def test_directory(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        args = bds9.parseargs()
        self.assertTrue(Path(args.fits_dir).exists())


if __name__ == '__main__':
    unittest.main()
