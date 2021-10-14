#!/usr/bin/env python3
import unittest
import pyds9
from pathlib import Path
from sdssobstools import sdss_paths
from bin import ds9_live


class TestDS9(unittest.TestCase):
    """ These tests don't work very well because they interfere with each other,
    I'm not sure why or how to fix it
    """
    def setUp(self):
        class Args:
            def __init__(self):
                pass
        self.args = Args()
        self.args.name = "Scanner"
        self.args.fits_dir = ds9_live.default_dir
        self.args.regex = "apRaw*"
        self.args.scale = "histequ"
        self.args.zoom = "1.0"
        self.args.verbose = False
        self.args.info = False
        self.args.vertical = False
    def test_pyds9(self):
        # print('pyds9.test is disabled because it is quite slow')
        pyds9.test()

    def test_no_args(self):
        args = self.args
        window = ds9_live.DS9Window(args.name, args.fits_dir, args.regex,
                                    args.scale, args.zoom, args.verbose, False,
                                    True)
        window.close()

    def test_boss(self):
        window = ds9_live.DS9Window('BOSS', sdss_paths.boss, 'sdR-r1*',
                                        'histequ', '1.0', False, False, True)
        window.close()

    def test_guider(self):
        window = ds9_live.DS9Window('Guider', sdss_paths.gcam, 'gimg-*',
                                        'histequ', '1.0', False, False, True)
        window.close()

    def test_apogee_summary_dir(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        args = self.args
        self.assertTrue(Path(args.fits_dir).exists())


if __name__ == '__main__':
    unittest.main()
