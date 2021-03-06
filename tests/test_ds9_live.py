#!/usr/bin/env python3
import unittest
from pathlib import Path
from bin import ds9_live
import pyds9


class TestDS9(unittest.TestCase):
    """ These tests don't work very well because they interfere with each other,
    I'm not sure why or how to fix it
    """
    def test_pyds9(self):
        print('pyds9.test is disabled because it is quite slow')
        # pyds9.test()

    def test_no_args(self):
        args = ds9_live.parseargs()
        window = ds9_live.DS9Window(args.name, args.fits_dir, args.regex,
                                    args.scale, args.zoom, args.verbose)
        window.close()

    def test_boss(self):
        window = ds9_live.DS9Window('BOSS', '/data/spectro/', 'sdR-r1*',
                                    'histequ', '1.0', False)
        window.close()

    def test_guider(self):
        window = ds9_live.DS9Window('Guider', '/data/gcam/', 'gimg-*',
                                    'histequ', '1.0', False)
        window.close()

    def test_apogee_summary_dir(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        args = ds9_live.parseargs()
        self.assertTrue(Path(args.fits_dir).exists())


if __name__ == '__main__':
    unittest.main()
