#!/usr/bin/env python3
import unittest
from pathlib import Path
import ds9_live


class TestADS9(unittest.TestCase):
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
