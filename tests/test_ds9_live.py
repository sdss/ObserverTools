#!/usr/bin/env python3
import pytest
import pyds9
from pathlib import Path
from sdssobstools import sdss_paths
from bin import ds9_live


class Args:
    def __init__(self):
        pass
args = Args()
args.name = "Scanner"
args.fits_dir = ds9_live.default_dir
args.regex = "apRaw*"
args.scale = "histequ"
args.zoom = "1.0"
args.verbose = False
args.info = False
args.vertical = False

class TestDS9():
    """ These tests don't work very well because they interfere with each other,
    I'm not sure why or how to fix it
    """
    def test_pyds9(self):
        # print('pyds9.test is disabled because it is quite slow')
        pyds9.test()

    def test_no_args(self):
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
        assert Path(args.fits_dir).exists()


if __name__ == '__main__':
    pytest.main()
